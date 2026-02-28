#!/usr/bin/env python3
"""
Trim a Timefold FSR output JSON: remove shifts with no visits and vehicles
with no shifts. Optionally set each shift end to depot arrival (removes idle).

Use when from-patch API is not available (e.g. plan still SOLVING_ACTIVE).
Output is a valid FSR output with only non-empty shifts; use with metrics.py.

Usage:
  python trim_output_empty_shifts.py output.json --out output_trimmed.json
  python trim_output_empty_shifts.py output.json --out output_trimmed.json --end-at-depot
"""

import argparse
import json
import sys
from pathlib import Path


def has_visit(shift: dict) -> bool:
    """True if shift itinerary contains at least one VISIT."""
    for item in shift.get("itinerary") or []:
        if isinstance(item, dict) and item.get("kind") == "VISIT":
            return True
    return False


def trim_output(
    output_data: dict,
    end_shifts_at_depot: bool = False,
) -> dict:
    """
    Return a copy of output_data with empty shifts and empty vehicles removed.
    If end_shifts_at_depot, set each shift's end to metrics.endLocationArrivalTime
    (removes idle time in the trimmed output for metrics).
    """
    out = output_data.get("modelOutput") or output_data.get("model_output") or {}
    vehicles_in = out.get("vehicles") or []
    vehicles_out = []

    for v in vehicles_in:
        shifts_kept = []
        for s in v.get("shifts") or []:
            if not has_visit(s):
                continue
            shift = dict(s)
            if end_shifts_at_depot:
                metrics = shift.get("metrics")
                if isinstance(metrics, dict):
                    arrival = metrics.get("endLocationArrivalTime")
                    if isinstance(arrival, str) and arrival:
                        shift["metrics"] = {**metrics, "endLocationArrivalTime": arrival}
            shifts_kept.append(shift)
        if shifts_kept:
            vehicles_out.append({
                **v,
                "shifts": shifts_kept,
            })

    model_output = {
        **out,
        "vehicles": vehicles_out,
    }
    return {
        **output_data,
        "modelOutput": model_output,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Trim FSR output: remove empty shifts and vehicles.")
    ap.add_argument("output", type=Path, help="Timefold output JSON.")
    ap.add_argument("--out", type=Path, required=True, help="Trimmed output path.")
    ap.add_argument(
        "--end-at-depot",
        action="store_true",
        help="Use depot arrival as shift end (for metrics).",
    )
    args = ap.parse_args()

    if not args.output.exists():
        print(f"Error: not found {args.output}", file=sys.stderr)
        return 1

    with open(args.output) as f:
        data = json.load(f)

    out = data.get("modelOutput") or data.get("model_output") or {}
    vehicles = out.get("vehicles") or []
    total_shifts = sum(len(v.get("shifts") or []) for v in vehicles)
    non_empty = sum(1 for v in vehicles for s in v.get("shifts") or [] if has_visit(s))
    empty = total_shifts - non_empty
    used_vehicles = sum(1 for v in vehicles if any(has_visit(s) for s in v.get("shifts") or []))

    trimmed = trim_output(data, end_shifts_at_depot=args.end_at_depot)
    out_after = trimmed.get("modelOutput") or {}
    vehicles_after = out_after.get("vehicles") or []
    shifts_after = sum(len(v.get("shifts") or []) for v in vehicles_after)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(trimmed, f, indent=2, ensure_ascii=False)

    print(f"Removed {empty} empty shifts and {len(vehicles) - len(vehicles_after)} empty vehicles.")
    print(f"Before: {len(vehicles)} vehicles, {total_shifts} shifts. After: {len(vehicles_after)} vehicles, {shifts_after} shifts.")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
