#!/usr/bin/env python3
"""
Count total, assigned, and unassigned visits from a Timefold FSR solution.

Use after fetching with fetch_timefold_solution.py. The GET response has
modelOutput (and optionally pass --input for modelInput).

Timefold represents unassigned in modelOutput.unassignedVisits (array of visit IDs).
Assigned = visits that appear in any shift's itinerary (kind=VISIT).

Usage:
  python3 count_timefold_visits.py solution.json
  python3 count_timefold_visits.py solution.json --input input.json
"""

import argparse
import json
import sys
from pathlib import Path


def count_input_visits(data: dict) -> int:
    """Count visits in modelInput: standalone visits + visits inside visitGroups."""
    mi = data.get("modelInput") or data
    n = len(mi.get("visits") or [])
    for g in mi.get("visitGroups") or []:
        n += len(g.get("visits") or [])
    return n


def count_assigned_from_output(mo: dict) -> int:
    """Count visit IDs that appear in any shift itinerary (kind=VISIT)."""
    n = 0
    for v in mo.get("vehicles") or []:
        for s in v.get("shifts") or []:
            for item in s.get("itinerary") or []:
                if isinstance(item, dict) and item.get("kind") == "VISIT":
                    n += 1
    return n


def count_unassigned_from_output(mo: dict) -> int:
    """Count unassigned from modelOutput.unassignedVisits."""
    return len(mo.get("unassignedVisits") or [])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Count total, assigned, unassigned from Timefold FSR solution JSON",
    )
    parser.add_argument(
        "solution",
        type=Path,
        help="Path to solution JSON (GET route-plans/{id} response or saved fetch output)",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Path to input JSON (GET route-plans/{id}/input). If omitted, total = assigned + unassigned.",
    )
    args = parser.parse_args()

    if not args.solution.exists():
        print(f"Error: {args.solution} not found", file=sys.stderr)
        return 1

    with open(args.solution, encoding="utf-8") as f:
        solution_data = json.load(f)

    # GET response: top-level modelOutput; or file may be the raw response
    mo = solution_data.get("modelOutput") or solution_data
    if "vehicles" not in mo and "unassignedVisits" not in mo:
        print("Error: no modelOutput (vehicles / unassignedVisits) in solution JSON", file=sys.stderr)
        return 1

    assigned = count_assigned_from_output(mo)
    unassigned = count_unassigned_from_output(mo)

    if args.input and args.input.exists():
        with open(args.input, encoding="utf-8") as f:
            input_data = json.load(f)
        if "modelInput" in input_data:
            input_data = input_data["modelInput"]
        total = count_input_visits(input_data)
    else:
        total = assigned + unassigned
        print("(No --input; total = assigned + unassigned)", file=sys.stderr)

    print(f"Total visits (input/dataset): {total}")
    print(f"Assigned (in itineraries):   {assigned}")
    print(f"Unassigned:                  {unassigned}")
    if total > 0 and total != assigned + unassigned:
        print(f"  (assigned + unassigned = {assigned + unassigned}; total from input = {total})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
