#!/usr/bin/env python3
"""
Build a from-patch JSON payload for Timefold FSR.

Strategy: pin all assigned visits (lock the good shifts), trim each non-empty
shift to visit span (minStartTime/maxEndTime = first visit start -> last visit end,
removing all idle and breaks), then remove shifts with empty itinerary and remove
empty vehicles. Patch order: 1) pin visits, 2) set shift minStartTime/maxEndTime
(trim to visit span by default, or only maxEndTime = depot with --no-trim-shifts),
3) remove empty shifts, 4) remove empty vehicles. Submit to POST /v1/route-plans/{id}/from-patch.

Usage:
  # Build patch (default: pin, trim shifts to visit span, remove empty shifts/vehicles)
  python build_from_patch.py --output ../tf/step1-output.json --out ../tf/step2-payload.json

  # REQUIRED: pass --input so visitGroup visits get correct patch paths (e.g. /visitGroups/[id=double_13]/visits/[id=78]/...)
  python build_from_patch.py --output ../tf/step1-output.json --input ../tf/step1-input.json --out ../tf/step2-payload.json

  # End shifts at depot only (no trim to visit span)
  python build_from_patch.py --output ../tf/step1-output.json --no-trim-shifts --out ../tf/step2-payload.json

  # Skip shift end/trim or empty-shift removal
  python build_from_patch.py --output ../tf/step1-output.json --no-end-shifts-at-depot --no-remove-empty-shifts --out ../tf/step2-payload.json
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path


def _parse_duration_seconds(iso: str) -> float:
    """Parse ISO 8601 duration (PT1H30M, PT10M) to seconds."""
    if not iso or not iso.startswith("PT"):
        return 0.0
    total = 0.0
    for m in re.finditer(r"(\d+(?:\.\d+)?)([HMS])", iso):
        val, unit = float(m.group(1)), m.group(2)
        total += val * (3600 if unit == "H" else 60 if unit == "M" else 1)
    return total


def _parse_iso_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def used_vehicles_from_output(output_data: dict) -> set[str]:
    """Return vehicle IDs that have at least one VISIT in any shift."""
    used: set[str] = set()
    out = output_data.get("modelOutput") or output_data.get("model_output") or {}
    for v in out.get("vehicles", []):
        vid = v.get("id")
        if not vid:
            continue
        for s in v.get("shifts", []):
            has_visit = any(
                isinstance(item, dict) and item.get("kind") == "VISIT"
                for item in s.get("itinerary", [])
            )
            if has_visit:
                used.add(vid)
                break
    return used


def empty_shifts_from_output(output_data: dict) -> list[tuple[str, str]]:
    """Return (vehicle_id, shift_id) for shifts with empty itinerary (no VISITs)."""
    out = output_data.get("modelOutput") or output_data.get("model_output") or {}
    result: list[tuple[str, str]] = []
    for v in out.get("vehicles", []):
        vid = v.get("id", "")
        for s in v.get("shifts", []):
            sid = s.get("id", "")
            has_visit = any(
                isinstance(item, dict) and item.get("kind") == "VISIT"
                for item in s.get("itinerary", [])
            )
            if not has_visit:
                result.append((vid, sid))
    return sorted(result)


def shift_depot_end_times_from_output(output_data: dict) -> list[tuple[str, str, str]]:
    """
    Return (vehicle_id, shift_id, end_time_iso) for shifts that have at least one
    VISIT and provide metrics.endLocationArrivalTime (depot arrival).
    Used to patch shift maxEndTime so the shift ends when the vehicle arrives at depot.
    """
    out = output_data.get("modelOutput") or output_data.get("model_output") or {}
    result: list[tuple[str, str, str]] = []
    for v in out.get("vehicles", []):
        vid = v.get("id", "")
        for s in v.get("shifts", []):
            sid = s.get("id", "")
            has_visit = any(
                isinstance(item, dict) and item.get("kind") == "VISIT"
                for item in s.get("itinerary", [])
            )
            if not has_visit:
                continue
            metrics = s.get("metrics") if isinstance(s.get("metrics"), dict) else {}
            arrival = metrics.get("endLocationArrivalTime")
            if isinstance(arrival, str) and arrival:
                result.append((vid, sid, arrival))
    return sorted(result)


def shift_visit_span_from_output(output_data: dict) -> list[tuple[str, str, str, str]]:
    """
    Return (vehicle_id, shift_id, min_start_iso, max_end_iso) for shifts that have
    at least one VISIT. Window is the span of assigned visits only: first visit
    start -> last visit end. Trimming removes all idle time including breaks
    (e.g. shift 7-15, visits 7-10, break 12-12:30 -> trimmed 7-10).
    """
    out = output_data.get("modelOutput") or output_data.get("model_output") or {}
    result: list[tuple[str, str, str, str]] = []
    for v in out.get("vehicles", []):
        vid = v.get("id", "")
        for s in v.get("shifts", []):
            sid = s.get("id", "")
            itinerary = s.get("itinerary") or []
            visit_items = [
                it
                for it in itinerary
                if isinstance(it, dict) and it.get("kind") == "VISIT"
            ]
            if not visit_items:
                continue
            first = visit_items[0]
            last = visit_items[-1]
            min_start = first.get("minStartTravelTime") or first.get("arrivalTime") or first.get("startServiceTime")
            if not min_start:
                continue
            # Last visit end = startServiceTime + effectiveServiceDuration (or departureTime)
            end_svc = last.get("startServiceTime") or last.get("arrivalTime")
            dur_iso = last.get("effectiveServiceDuration")
            if end_svc and dur_iso:
                dt = _parse_iso_dt(end_svc)
                sec = _parse_duration_seconds(dur_iso)
                if dt and sec >= 0:
                    max_end = (dt + timedelta(seconds=sec)).isoformat()
                else:
                    max_end = last.get("departureTime") or end_svc
            else:
                max_end = last.get("departureTime") or end_svc
            if max_end:
                result.append((vid, sid, min_start, max_end))
    return sorted(result)


def visit_pinning_data(output_data: dict) -> dict[str, str]:
    """From output, return dict visit_id -> minStartTravelTime (ISO string)."""
    out = output_data.get("modelOutput") or output_data.get("model_output") or {}
    result: dict[str, str] = {}
    for v in out.get("vehicles", []):
        for s in v.get("shifts", []):
            for item in s.get("itinerary", []):
                if isinstance(item, dict) and item.get("kind") == "VISIT":
                    vid = item.get("id")
                    mst = item.get("minStartTravelTime")
                    if vid and mst:
                        result[vid] = mst
    return result


def visit_pinning_order(output_data: dict) -> list[tuple[str, str]]:
    """
    From output, return list of (visit_id, minStartTravelTime) in itinerary order.
    Patching must pin visits in this order so no visit is pinned before its predecessor.
    """
    out = output_data.get("modelOutput") or output_data.get("model_output") or {}
    result: list[tuple[str, str]] = []
    for v in out.get("vehicles", []):
        for s in v.get("shifts", []):
            for item in s.get("itinerary", []):
                if isinstance(item, dict) and item.get("kind") == "VISIT":
                    vid = item.get("id")
                    mst = item.get("minStartTravelTime")
                    if vid and mst:
                        result.append((vid, mst))
    return result


def visit_start_service_times(output_data: dict) -> dict[str, str]:
    """From output, return dict visit_id -> startServiceTime (ISO string). For itinerary pinning."""
    out = output_data.get("modelOutput") or output_data.get("model_output") or {}
    result: dict[str, str] = {}
    for v in out.get("vehicles", []):
        for s in v.get("shifts", []):
            for item in s.get("itinerary", []):
                if isinstance(item, dict) and item.get("kind") == "VISIT":
                    vid = item.get("id")
                    sst = item.get("startServiceTime")
                    if vid and sst:
                        result[vid] = sst
    return result


def shift_itinerary_visit_ids(output_data: dict) -> list[tuple[str, str, list[str]]]:
    """
    From output, return list of (vehicle_id, shift_id, [visit_id, ...]) in itinerary order.
    Used to build input itinerary (startServiceTime + pin) for trimmed solve.
    """
    out = output_data.get("modelOutput") or output_data.get("model_output") or {}
    result: list[tuple[str, str, list[str]]] = []
    for v in out.get("vehicles", []):
        vid = v.get("id", "")
        for s in v.get("shifts", []):
            sid = s.get("id", "")
            visit_ids = []
            for item in s.get("itinerary", []):
                if isinstance(item, dict) and item.get("kind") == "VISIT":
                    visit_ids.append(item.get("id", ""))
            if visit_ids:
                result.append((vid, sid, visit_ids))
    return result


def visit_group_membership(input_data: dict | None) -> dict[str, str]:
    """
    From input, return dict visit_id -> visitGroup_id for visits inside visitGroups.
    Solo visits (in top-level "visits") are NOT included.
    """
    if not input_data:
        return {}
    mi = input_data.get("modelInput") or input_data
    result: dict[str, str] = {}
    for g in mi.get("visitGroups", []):
        gid = g.get("id", "")
        for v in g.get("visits", []):
            vid = v.get("id")
            if vid:
                result[vid] = gid
    return result


def build_patch(
    output_data: dict,
    input_data: dict | None = None,
    remove_empty_shifts: bool = True,
    end_shifts_at_depot: bool = True,
    trim_to_visit_span: bool = True,
) -> list[dict]:
    """
    Build JSON Patch array (order matters):
    1. Pin all assigned visits (lock the good shifts) — pinningRequested + minStartTravelTime
    2. Trim shift window: if trim_to_visit_span, set minStartTime and maxEndTime to visit span
       (first visit start -> last visit end), removing all idle and breaks. Else if end_shifts_at_depot,
       set maxEndTime = endLocationArrivalTime (removes idle after last visit).
    3. Remove shifts with empty itinerary (no assigned visits)
    4. Remove unused vehicles (entirely empty)

    For visits inside visitGroups, uses:
      /visitGroups/[id=GROUP_ID]/visits/[id=VISIT_ID]/pinningRequested
    For solo visits:
      /visits/[id=VISIT_ID]/pinningRequested
    """
    used_v = used_vehicles_from_output(output_data)
    out = output_data.get("modelOutput") or output_data.get("model_output") or {}

    # Determine all vehicle IDs
    if input_data is not None:
        mi = input_data.get("modelInput") or input_data
        all_vehicle_ids = [v["id"] for v in mi.get("vehicles", []) if v.get("id")]
    else:
        all_vehicle_ids = [v["id"] for v in out.get("vehicles", []) if v.get("id")]

    unused_vehicle_ids = set(all_vehicle_ids) - used_v
    visit_pin_order = visit_pinning_order(output_data)  # itinerary order (required by API)
    group_membership = visit_group_membership(input_data)

    patch: list[dict] = []

    # 1. Pin all assigned visits first (lock the good shifts), in itinerary order
    for visit_id, mst in visit_pin_order:
        gid = group_membership.get(visit_id)
        if gid:
            base_path = f"/visitGroups/[id={gid}]/visits/[id={visit_id}]"
        else:
            base_path = f"/visits/[id={visit_id}]"
        patch.append({"op": "add", "path": f"{base_path}/pinningRequested", "value": True})
        patch.append({"op": "add", "path": f"{base_path}/minStartTravelTime", "value": mst})

    # 2. Trim shift window: visit span (removes idle + breaks) or end at depot only
    if trim_to_visit_span:
        for vid, sid, min_start, max_end in shift_visit_span_from_output(output_data):
            if vid not in unused_vehicle_ids:
                patch.append({
                    "op": "add",
                    "path": f"/vehicles/[id={vid}]/shifts/[id={sid}]/minStartTime",
                    "value": min_start,
                })
                patch.append({
                    "op": "add",
                    "path": f"/vehicles/[id={vid}]/shifts/[id={sid}]/maxEndTime",
                    "value": max_end,
                })
    elif end_shifts_at_depot:
        for vid, sid, end_time in shift_depot_end_times_from_output(output_data):
            if vid not in unused_vehicle_ids:
                patch.append({
                    "op": "add",
                    "path": f"/vehicles/[id={vid}]/shifts/[id={sid}]/maxEndTime",
                    "value": end_time,
                })

    # 3. Remove shifts with empty itinerary (no assigned visits)
    if remove_empty_shifts:
        for vid, sid in empty_shifts_from_output(output_data):
            if vid not in unused_vehicle_ids:
                patch.append({"op": "remove", "path": f"/vehicles/[id={vid}]/shifts/[id={sid}]"})

    # 4. Remove unused vehicles (entirely empty)
    for vid in sorted(unused_vehicle_ids):
        patch.append({"op": "remove", "path": f"/vehicles/[id={vid}]"})

    return patch


def main() -> int:
    ap = argparse.ArgumentParser(description="Build from-patch payload for Timefold FSR.")
    ap.add_argument("--output", type=Path, required=True, help="Timefold output JSON (solved).")
    ap.add_argument("--input", type=Path, default=None, help="Original input JSON (optional, for full vehicle list).")
    ap.add_argument("--out", type=Path, default=None, help="Path for from-patch payload JSON.")
    ap.add_argument(
        "--remove-empty-shifts",
        action="store_true",
        default=True,
        help="Remove shifts with empty itinerary (no assigned visits). Default: True.",
    )
    ap.add_argument(
        "--no-remove-empty-shifts",
        action="store_false",
        dest="remove_empty_shifts",
        help="Do not remove empty shifts.",
    )
    ap.add_argument(
        "--no-trim-shifts",
        action="store_false",
        dest="trim_to_visit_span",
        default=True,
        help="Do not trim to visit span (default: trim; removes idle and breaks so shift = first visit start -> last visit end). Use end-shifts-at-depot only.",
    )
    ap.add_argument(
        "--end-shifts-at-depot",
        action="store_true",
        default=True,
        help="When not trimming: set each shift maxEndTime to depot arrival (removes idle time). Default: True.",
    )
    ap.add_argument(
        "--no-end-shifts-at-depot",
        action="store_false",
        dest="end_shifts_at_depot",
        help="Do not patch shift end times (use only when --no-trim-shifts).",
    )
    ap.add_argument("--no-timestamp", action="store_true", help="Use exact --out path (no timestamp).")
    args = ap.parse_args()

    if not args.output.exists():
        print(f"Error: output not found: {args.output}", file=sys.stderr)
        return 1

    with open(args.output) as f:
        output_data = json.load(f)

    input_data = None
    if args.input and args.input.exists():
        with open(args.input) as f:
            input_data = json.load(f)

    patch = build_patch(
        output_data,
        input_data,
        remove_empty_shifts=args.remove_empty_shifts,
        end_shifts_at_depot=args.end_shifts_at_depot,
        trim_to_visit_span=args.trim_to_visit_span,
    )
    visit_pins = visit_pinning_data(output_data)
    used_v = used_vehicles_from_output(output_data)

    # Count operations
    add_ops = [p for p in patch if p["op"] == "add"]
    remove_ops = [p for p in patch if p["op"] == "remove"]
    shift_trim_ops = sum(1 for p in add_ops if "minStartTime" in p.get("path", ""))
    shift_end_ops = sum(1 for p in add_ops if "maxEndTime" in p.get("path", ""))
    remove_vehicle_ops = sum(1 for p in remove_ops if "/shifts/" not in p.get("path", ""))
    remove_shift_ops = sum(1 for p in remove_ops if "/shifts/" in p.get("path", ""))
    group_membership = visit_group_membership(input_data)
    solo_pins = sum(1 for vid in visit_pins if vid not in group_membership)
    group_pins = sum(1 for vid in visit_pins if vid in group_membership)

    print(f"Patch operations: {len(patch)} total")
    print(f"  Pin visits:           {solo_pins} solo + {group_pins} in visitGroups = {solo_pins + group_pins} total")
    if args.trim_to_visit_span and shift_trim_ops:
        print(f"  Trim shift to visit span: {shift_trim_ops} shifts (minStartTime + maxEndTime = visit span, idle and breaks removed)")
    elif shift_end_ops:
        print(f"  End shift at depot:   {shift_end_ops} shifts (maxEndTime = endLocationArrivalTime)")
    if args.remove_empty_shifts:
        print(f"  Remove empty shifts: {remove_shift_ops}")
    print(f"  Remove empty vehicles: {remove_vehicle_ops}")

    payload = {
        "config": {
            "run": {"name": "from-patch-trim-empty"},
        },
        "patch": patch,
    }

    base = args.out or Path("from-patch/payload.json")
    if args.no_timestamp:
        out_path = base
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = base.parent / f"{base.stem}_{ts}{base.suffix}"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\nWrote from-patch payload: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
