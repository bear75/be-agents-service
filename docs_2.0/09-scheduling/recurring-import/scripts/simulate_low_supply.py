#!/usr/bin/env python3
"""
Build a sick-day from-patch payload for Timefold FSR supply-demand simulation.

Simulates N employees calling in sick on target day. Builds a patch that:
1. Sets planning window (target_date to target_date + N days, or single day)
2. Removes target-day shifts for the N sick employees (busiest or quietest by visit count)
3. Does NOT patch visit time windows (frequency from expand pipeline is authoritative)

Output: payload_*.json (from-patch request) and deferred_*.json (sick visit IDs for extract_recommendations).

Usage:
  python simulate_low_supply.py \\
    --output solve/tf-16feb-0800/from-patch-output.json \\
    --input  solve/tf-16feb-0800/export-field-service-routing-v1-073f6280-...-input.json \\
    --day 2026-02-16 --sick 2 --select busiest \\
    --days 3 \\
    --out-dir solve/supply-demand-sim/

  python simulate_low_supply.py --output ... --input ... --day 2026-02-16 --sick 1 --single-day-window --out-dir ...
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def parse_date(s: str) -> datetime:
    """Parse YYYY-MM-DD to datetime at midnight UTC+1."""
    return datetime.strptime(s, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)


def date_to_iso(d: datetime, end_of_day: bool = False) -> str:
    """Convert datetime to ISO string with +01:00 offset."""
    if end_of_day:
        d = d.replace(hour=23, minute=59, second=59, microsecond=999999)
    return d.strftime("%Y-%m-%dT%H:%M:%S") + "+01:00"


def shift_overlaps_day(shift: dict, target_date: datetime) -> bool:
    """True if shift overlaps target_date (any part of the day)."""
    start_str = shift.get("minStartTime") or shift.get("startTime") or shift.get("start") or ""
    end_str = shift.get("maxEndTime") or shift.get("endTime") or shift.get("end") or ""
    if not start_str or not end_str:
        return False
    try:
        start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        day_start = target_date.replace(tzinfo=start.tzinfo) if start.tzinfo else target_date
        day_end = day_start + timedelta(days=1)
        return start < day_end and end > day_start
    except (ValueError, TypeError):
        return False


def visit_ids_on_shift(shift: dict) -> list[str]:
    """Return visit IDs in shift itinerary (kind=VISIT)."""
    result: list[str] = []
    for item in shift.get("itinerary", []):
        if isinstance(item, dict) and item.get("kind") == "VISIT":
            vid = item.get("id")
            if vid:
                result.append(vid)
    return result


def vehicle_visit_count_on_day(output_data: dict, target_date: datetime) -> dict[str, int]:
    """Return vehicle_id -> visit count on target_date."""
    out = output_data.get("modelOutput") or output_data.get("model_output") or {}
    counts: dict[str, int] = {}
    for v in out.get("vehicles", []):
        vid = v.get("id")
        if not vid:
            continue
        n = 0
        for s in v.get("shifts", []):
            if shift_overlaps_day(s, target_date):
                n += len(visit_ids_on_shift(s))
        if n > 0:
            counts[vid] = n
    return counts


def shifts_on_target_day(output_data: dict, target_date: datetime) -> list[tuple[str, str, list[str]]]:
    """Return (vehicle_id, shift_id, visit_ids) for shifts overlapping target_date."""
    out = output_data.get("modelOutput") or output_data.get("model_output") or {}
    result: list[tuple[str, str, list[str]]] = []
    for v in out.get("vehicles", []):
        vid = v.get("id")
        if not vid:
            continue
        for s in v.get("shifts", []):
            sid = s.get("id")
            if not sid or not shift_overlaps_day(s, target_date):
                continue
            visit_ids = visit_ids_on_shift(s)
            result.append((vid, sid, visit_ids))
    return result


def select_sick_vehicles(
    output_data: dict,
    target_date: datetime,
    n: int,
    select: str,
) -> set[str]:
    """Select N vehicle IDs (busiest or quietest by visit count on target day)."""
    counts = vehicle_visit_count_on_day(output_data, target_date)
    if not counts:
        return set()
    sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=(select == "busiest"))
    return {vid for vid, _ in sorted_items[:n]}


def build_patch(
    output_data: dict,
    input_data: dict,
    target_date: datetime,
    n_days: int,
    sick_vehicle_ids: set[str],
    single_day: bool,
) -> tuple[list[dict], list[str]]:
    """
    Build patch ops and return (patch, deferred_visit_ids).
    deferred_visit_ids = visits on removed shifts (sick visits for extract_recommendations).
    """
    patch: list[dict] = []
    deferred_visit_ids: list[str] = []

    # Planning window
    if single_day:
        start_iso = date_to_iso(target_date, end_of_day=False)
        end_iso = date_to_iso(target_date + timedelta(days=1), end_of_day=False)
    else:
        start_iso = date_to_iso(target_date, end_of_day=False)
        end_dt = target_date + timedelta(days=n_days)
        end_iso = date_to_iso(end_dt, end_of_day=True)

    pw = {"startDate": start_iso, "endDate": end_iso}
    mi = input_data.get("modelInput") or input_data
    if mi.get("planningWindow"):
        patch.append({"op": "replace", "path": "/planningWindow", "value": pw})
    else:
        patch.append({"op": "add", "path": "/planningWindow", "value": pw})

    # Remove shifts on target day for sick employees
    shifts_to_remove = shifts_on_target_day(output_data, target_date)
    for vid, sid, visit_ids in shifts_to_remove:
        if vid in sick_vehicle_ids:
            patch.append({"op": "remove", "path": f"/vehicles/[id={vid}]/shifts/[id={sid}]"})
            deferred_visit_ids.extend(visit_ids)

    return patch, list(dict.fromkeys(deferred_visit_ids))  # preserve order, dedupe


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Build sick-day from-patch payload (planning window + remove sick shifts).",
    )
    ap.add_argument("--output", type=Path, required=True, help="Timefold output JSON (baseline solution).")
    ap.add_argument("--input", type=Path, required=True, help="Original input JSON.")
    ap.add_argument("--day", type=str, required=True, help="Target date YYYY-MM-DD (sick day).")
    ap.add_argument("--sick", type=int, default=1, help="Number of employees to simulate as sick.")
    ap.add_argument(
        "--select",
        choices=["busiest", "quietest"],
        default="busiest",
        help="Select busiest (most visits) or quietest (fewest visits) employees.",
    )
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--days", type=int, choices=[3, 5, 7], help="Planning window length (target + N days).")
    group.add_argument("--single-day-window", action="store_true", help="Single-day planning window.")
    ap.add_argument("--out-dir", type=Path, required=True, help="Directory for payload and deferred JSON.")
    args = ap.parse_args()

    if not args.output.exists():
        print(f"Error: output not found: {args.output}", file=sys.stderr)
        return 1
    if not args.input.exists():
        print(f"Error: input not found: {args.input}", file=sys.stderr)
        return 1

    target_date = parse_date(args.day)
    with open(args.output) as f:
        output_data = json.load(f)
    with open(args.input) as f:
        input_data = json.load(f)

    n_days = 1 if args.single_day_window else args.days
    sick_vehicle_ids = select_sick_vehicles(output_data, target_date, args.sick, args.select)
    if len(sick_vehicle_ids) < args.sick:
        print(
            f"Warning: only {len(sick_vehicle_ids)} vehicles have visits on {args.day}, "
            f"requested {args.sick}",
            file=sys.stderr,
        )

    patch, deferred = build_patch(
        output_data,
        input_data,
        target_date,
        n_days,
        sick_vehicle_ids,
        single_day=args.single_day_window,
    )

    # Generate short hash for filenames (from first 8 chars of day + sick count)
    tag = f"{args.day.replace('-', '')}_{args.sick}sick"
    payload_path = args.out_dir / f"payload_{tag}.json"
    deferred_path = args.out_dir / f"deferred_{tag}.json"

    payload = {
        "config": {"run": {"name": f"sick-day-sim-{args.day}-{args.sick}"}},
        "patch": patch,
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    with open(payload_path, "w") as f:
        json.dump(payload, f, indent=2)
    with open(deferred_path, "w") as f:
        json.dump({"deferred_visit_ids": deferred, "target_day": args.day}, f, indent=2)

    print(f"Patch: {len(patch)} ops (planning window {n_days}d, remove {len([p for p in patch if p['op']=='remove'])} shifts)")
    print(f"Sick vehicles: {sorted(sick_vehicle_ids)}")
    print(f"Deferred (sick) visits: {len(deferred)}")
    print(f"Wrote {payload_path}")
    print(f"Wrote {deferred_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
