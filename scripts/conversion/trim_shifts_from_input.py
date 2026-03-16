#!/usr/bin/env python3
"""
Trim shifts from a Timefold FSR input to reduce problem size.

Two modes:
  1. From solution: keep only vehicles and shifts that have ≥1 visit in the solution
     (same idea as build_reduced_input.py; reduces oversupply for follow-up runs).
  2. Heuristic (no solution): cap shifts per vehicle (e.g. --max-shifts-per-vehicle 10)
     to shrink input for faster research/optimization runs.

Preserves full input structure: config, modelInput (planningWindow, visits, visitGroups,
vehicles, skills, tags, pinNextVisitDuringFreeze).

Usage:
  # Trim to used shifts only (from a previous solution)
  python trim_shifts_from_input.py --input script_fsr_no_extra_vehicles.json \\
    --solution output.json -o input_trimmed.json

  # Cap shifts per vehicle (no solution)
  python trim_shifts_from_input.py --input script_fsr_no_extra_vehicles.json \\
    --max-shifts-per-vehicle 10 -o input_trimmed.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _used_vehicles_and_shifts_from_solution(solution: dict) -> tuple[set[str], set[str]]:
    """From solution JSON, return (used_vehicle_ids, used_shift_ids)."""
    used_vehicle_ids: set[str] = set()
    used_shift_ids: set[str] = set()
    out = solution.get("modelOutput") or solution.get("model_output") or solution
    vehicles = out.get("vehicles", [])
    for v in vehicles:
        vid = v.get("id")
        if not vid:
            continue
        for s in v.get("shifts", []):
            sid = s.get("id")
            if not sid:
                continue
            itinerary = s.get("itinerary", [])
            has_visit = any(
                isinstance(item, dict) and item.get("kind") == "VISIT"
                for item in itinerary
            )
            if has_visit:
                used_vehicle_ids.add(vid)
                used_shift_ids.add(sid)
    return used_vehicle_ids, used_shift_ids


def trim_from_solution(
    data: dict,
    used_vehicle_ids: set[str],
    used_shift_ids: set[str],
) -> dict:
    """Keep only used vehicles and shifts; preserve all other modelInput and config."""
    result = dict(data)
    mi = result.get("modelInput", {})
    if not mi:
        return result
    vehicles_in = mi.get("vehicles", [])
    vehicles_out = []
    for v in vehicles_in:
        if v.get("id") not in used_vehicle_ids:
            continue
        shifts = [s for s in v.get("shifts", []) if s.get("id") in used_shift_ids]
        if not shifts:
            continue
        vehicles_out.append({**v, "shifts": shifts})
    result["modelInput"] = {**mi, "vehicles": vehicles_out}
    return result


def trim_max_shifts_per_vehicle(data: dict, max_shifts: int) -> dict:
    """Keep first max_shifts shifts per vehicle; preserve rest of input."""
    result = dict(data)
    mi = result.get("modelInput", {})
    if not mi or max_shifts < 1:
        return result
    vehicles_in = mi.get("vehicles", [])
    vehicles_out = []
    for v in vehicles_in:
        shifts = v.get("shifts", [])[:max_shifts]
        if not shifts:
            continue
        vehicles_out.append({**v, "shifts": shifts})
    result["modelInput"] = {**mi, "vehicles": vehicles_out}
    return result


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Trim shifts from FSR input (from solution or cap per vehicle)."
    )
    ap.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to full FSR input JSON (e.g. script_fsr_no_extra_vehicles.json).",
    )
    ap.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Path to write trimmed input JSON.",
    )
    ap.add_argument(
        "--solution",
        type=Path,
        default=None,
        help="Path to solution JSON; if set, keep only vehicles/shifts used in this solution.",
    )
    ap.add_argument(
        "--max-shifts-per-vehicle",
        type=int,
        default=None,
        metavar="N",
        help="If set (and no --solution), keep only first N shifts per vehicle.",
    )
    args = ap.parse_args()

    if not args.input.exists():
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        return 1
    if args.solution is not None and not args.solution.exists():
        print(f"Error: solution file not found: {args.solution}", file=sys.stderr)
        return 1
    if args.solution is None and args.max_shifts_per_vehicle is None:
        print(
            "Error: set either --solution or --max-shifts-per-vehicle",
            file=sys.stderr,
        )
        return 1
    if args.solution is not None and args.max_shifts_per_vehicle is not None:
        print(
            "Error: use either --solution or --max-shifts-per-vehicle, not both",
            file=sys.stderr,
        )
        return 1

    with open(args.input) as f:
        data = json.load(f)

    if args.solution is not None:
        with open(args.solution) as f:
            solution = json.load(f)
        used_v, used_s = _used_vehicles_and_shifts_from_solution(solution)
        trimmed = trim_from_solution(data, used_v, used_s)
    else:
        trimmed = trim_max_shifts_per_vehicle(data, args.max_shifts_per_vehicle)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(trimmed, f, indent=2, ensure_ascii=False)

    n_vehicles = len(trimmed.get("modelInput", {}).get("vehicles", []))
    n_shifts = sum(
        len(v.get("shifts", []))
        for v in trimmed.get("modelInput", {}).get("vehicles", [])
    )
    n_visits = len(trimmed.get("modelInput", {}).get("visits", []))
    print(
        f"Wrote trimmed input to {args.output}: "
        f"{n_visits} visits, {n_vehicles} vehicles, {n_shifts} shifts"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
