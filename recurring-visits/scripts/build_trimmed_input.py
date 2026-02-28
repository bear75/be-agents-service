#!/usr/bin/env python3
"""
Build a full trimmed RoutePlanInput for POST /v1/route-plans (new solve).

Workaround when from-patch is not available (e.g. 403 MODEL_API_DATASET_PATCH):
instead of PATCH + from-patch, build the same effective input as a full modelInput
and submit it as a new solve. Then fetch the solution and run metrics with
--exclude-inactive.

Trimmed input:
- Only vehicles that have at least one visit in the output.
- Only shifts that have visits; each such shift gets minStartTime/maxEndTime =
  visit span (first visit start → last visit end), requiredBreaks = [] (no break
  in trimmed window), and itinerary with pinned visits (startServiceTime + pin).
- All assigned visits get pinningRequested=true and minStartTravelTime from output.
- planningWindow, skills, tags, visits, visitGroups (structure) copied from input;
  unassigned visits remain so the solver can optionally reassign (metrics then
  exclude inactive).

Usage:
  python build_trimmed_input.py --output ../tf/output.json --input ../tf/input.json --out ../tf/trimmed-input.json

  # Then submit as new solve (not from-patch):
  python submit_to_timefold.py solve ../tf/trimmed-input.json --wait --save ../tf/trimmed_solve_output.json
"""

import argparse
import copy
import json
import sys
from pathlib import Path

# Reuse trim/pinning logic from build_from_patch
from build_from_patch import (
    empty_shifts_from_output,
    shift_itinerary_visit_ids,
    shift_visit_span_from_output,
    used_vehicles_from_output,
    visit_group_membership,
    visit_pinning_data,
    visit_start_service_times,
)


def _span_map(output_data: dict) -> dict[tuple[str, str], tuple[str, str]]:
    """(vehicle_id, shift_id) -> (min_start_iso, max_end_iso)."""
    return {
        (vid, sid): (min_start, max_end)
        for vid, sid, min_start, max_end in shift_visit_span_from_output(output_data)
    }


def _non_empty_shift_ids(output_data: dict) -> set[tuple[str, str]]:
    """Set of (vehicle_id, shift_id) that have at least one visit."""
    empty = set(empty_shifts_from_output(output_data))
    out = output_data.get("modelOutput") or output_data.get("model_output") or {}
    all_shifts: set[tuple[str, str]] = set()
    for v in out.get("vehicles", []):
        vid = v.get("id", "")
        for s in v.get("shifts", []):
            all_shifts.add((vid, s.get("id", "")))
    return all_shifts - empty


def build_trimmed_model_input(output_data: dict, input_data: dict) -> dict:
    """
    Build a full RoutePlanInput (trimmed): used vehicles only, non-empty shifts
    with visit-span window and pinned itinerary, visits/visitGroups with pinning.
    """
    mi = input_data.get("modelInput") or input_data
    used_v = used_vehicles_from_output(output_data)
    span_by_shift = _span_map(output_data)
    non_empty = _non_empty_shift_ids(output_data)
    pin_mst = visit_pinning_data(output_data)
    pin_sst = visit_start_service_times(output_data)
    itinerary_by_shift = {(vid, sid): visit_ids for vid, sid, visit_ids in shift_itinerary_visit_ids(output_data)}
    group_membership = visit_group_membership(input_data)

    # Deep copy so we don't mutate original
    trimmed = copy.deepcopy(mi)

    # Vehicles: only used; for each vehicle only non-empty shifts; trim shift and set itinerary
    new_vehicles: list[dict] = []
    for v in trimmed.get("vehicles", []):
        vid = v.get("id", "")
        if vid not in used_v:
            continue
        new_shifts: list[dict] = []
        for s in v.get("shifts", []):
            sid = s.get("id", "")
            if (vid, sid) not in non_empty:
                continue
            span = span_by_shift.get((vid, sid))
            shift_copy = copy.deepcopy(s)
            if span:
                shift_copy["minStartTime"] = span[0]
                shift_copy["maxEndTime"] = span[1]
            shift_copy["requiredBreaks"] = []  # trimmed window has no break
            visit_ids = itinerary_by_shift.get((vid, sid), [])
            shift_copy["itinerary"] = []
            for visit_id in visit_ids:
                sst = pin_sst.get(visit_id)
                if sst:
                    shift_copy["itinerary"].append({
                        "id": visit_id,
                        "kind": "VISIT",
                        "startServiceTime": sst,
                        "pin": True,
                    })
            new_shifts.append(shift_copy)
        if new_shifts:
            v_copy = copy.deepcopy(v)
            v_copy["shifts"] = new_shifts
            new_vehicles.append(v_copy)

    trimmed["vehicles"] = new_vehicles

    # Solo visits: set pinningRequested and minStartTravelTime
    for visit in trimmed.get("visits", []):
        vid = visit.get("id")
        if vid and vid in pin_mst:
            visit["pinningRequested"] = True
            visit["minStartTravelTime"] = pin_mst[vid]

    # VisitGroups: set pinning on each visit that is assigned
    for g in trimmed.get("visitGroups", []):
        for visit in g.get("visits", []):
            vid = visit.get("id")
            if vid and vid in pin_mst:
                visit["pinningRequested"] = True
                visit["minStartTravelTime"] = pin_mst[vid]

    return trimmed


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Build full trimmed modelInput for POST /v1/route-plans (workaround when from-patch is unavailable)."
    )
    ap.add_argument("--output", type=Path, required=True, help="Timefold solution output JSON.")
    ap.add_argument("--input", type=Path, required=True, help="Original input JSON (with modelInput).")
    ap.add_argument("--out", type=Path, required=True, help="Output path for trimmed request JSON.")
    args = ap.parse_args()

    if not args.output.exists():
        print(f"Error: not found {args.output}", file=sys.stderr)
        return 1
    if not args.input.exists():
        print(f"Error: not found {args.input}", file=sys.stderr)
        return 1

    with open(args.output) as f:
        output_data = json.load(f)
    with open(args.input) as f:
        input_data = json.load(f)

    trimmed = build_trimmed_model_input(output_data, input_data)
    payload = {"modelInput": trimmed}

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(payload, f, indent=2)

    used_v = used_vehicles_from_output(output_data)
    n_shifts = sum(
        1
        for v in trimmed.get("vehicles", [])
        for _ in v.get("shifts", [])
    )
    print(f"Trimmed input: {len(used_v)} vehicles, {n_shifts} shifts, {len(trimmed.get('visits', []))} solo visits, {len(trimmed.get('visitGroups', []))} visit groups")
    print(f"Wrote {args.out}")
    print("Submit with: python submit_to_timefold.py solve <trimmed.json> --wait [--configuration-id ...]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
