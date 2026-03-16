#!/usr/bin/env python3
"""
Build a REDUCED Timefold FSR input by removing oversupply.

We must NOT send oversupply to Timefold: if we send 39 vehicles and 342 shifts,
TF tends to activate many of them even when minimizing technician cost (hourly).
So we reduce the input to only the employees (vehicles) and shifts that were
actually USED in a reference solution (e.g. fixed-cost run).

Usage:
  # Reduced input WITH FIXED COSTS (recommended): use the fixed-cost input as source
  python build_reduced_input.py \\
    --solution fixed/export-field-service-routing-eb827631-6657-4c4f-948f-0c8aeceacd62-output.json \\
    --input hourly/export-field-service-routing-v1-eb827631-6657-4c4f-948f-0c8aeceacd62-input.json \\
    --output movable_visits_unplanned_input_reduced.json

  # Or use --cost fixed to force fixed cost (1375 per shift) regardless of source input
  python build_reduced_input.py --cost fixed --input movable_visits_unplanned_input.json ...

Then submit the reduced JSON to the FSR API (e.g. via submit_to_timefold.py).
Full pipeline (CSV → input → solve → from-patch iterate): see PIPELINE.md.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if ROOT.name == "scripts":
    ROOT = ROOT.parent


def used_vehicles_and_shifts_from_solution(solution: dict) -> tuple[set[str], set[str]]:
    """
    From a Timefold solution output, return (used_vehicle_ids, used_shift_ids).
    A vehicle/shift is "used" if it has at least one VISIT in its itinerary.
    """
    used_vehicle_ids: set[str] = set()
    used_shift_ids: set[str] = set()
    out = solution.get("modelOutput") or solution.get("model_output")
    if not out:
        return used_vehicle_ids, used_shift_ids
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
                item.get("kind") == "VISIT" for item in itinerary if isinstance(item, dict)
            )
            if has_visit:
                used_vehicle_ids.add(vid)
                used_shift_ids.add(sid)
    return used_vehicle_ids, used_shift_ids


FIXED_COST_PER_SHIFT = 1375


def apply_fixed_cost_to_shifts(vehicles: list[dict]) -> None:
    """Overwrite each shift's cost to fixedCost: 1375, rates: [] (in-place)."""
    for v in vehicles:
        for s in v.get("shifts", []):
            s["cost"] = {"fixedCost": FIXED_COST_PER_SHIFT, "rates": []}


def build_reduced_input(
    full_input: dict,
    used_vehicle_ids: set[str],
    used_shift_ids: set[str],
    force_fixed_cost: bool = False,
) -> dict:
    """
    From full modelInput, keep only used vehicles and only used shifts.
    Visits are unchanged.
    If force_fixed_cost is True, set every shift's cost to fixedCost 1375, rates [].
    """
    mi = full_input.get("modelInput") or full_input
    visits = mi.get("visits", [])
    vehicles_in = mi.get("vehicles", [])
    vehicles_out = []
    for v in vehicles_in:
        if v.get("id") not in used_vehicle_ids:
            continue
        shifts = [s for s in v.get("shifts", []) if s.get("id") in used_shift_ids]
        if not shifts:
            continue
        vehicles_out.append({**v, "shifts": shifts})
    if force_fixed_cost:
        apply_fixed_cost_to_shifts(vehicles_out)
    return {
        "modelInput": {
            "visits": visits,
            "vehicles": vehicles_out,
        }
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Build reduced FSR input (no oversupply) from a solution output."
    )
    ap.add_argument(
        "--solution",
        type=Path,
        default=ROOT / "fixed/export-field-service-routing-eb827631-6657-4c4f-948f-0c8aeceacd62-output.json",
        help="Path to solution output JSON (fixed-cost run recommended).",
    )
    ap.add_argument(
        "--input",
        type=Path,
        default=ROOT / "hourly/export-field-service-routing-v1-eb827631-6657-4c4f-948f-0c8aeceacd62-input.json",
        help="Path to full input JSON. Use fixed-cost input to get fixed costs in reduced file.",
    )
    ap.add_argument(
        "--cost",
        choices=["preserve", "fixed"],
        default="preserve",
        help="preserve: keep cost from --input. fixed: set every shift to fixedCost 1375, rates [].",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=ROOT / "movable_visits_unplanned_input_reduced.json",
        help="Path to write reduced input JSON.",
    )
    args = ap.parse_args()

    if not args.solution.exists():
        print(f"Error: solution file not found: {args.solution}", file=sys.stderr)
        return 1
    if not args.input.exists():
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        return 1

    with open(args.solution) as f:
        solution = json.load(f)
    with open(args.input) as f:
        full_data = json.load(f)

    used_v, used_s = used_vehicles_and_shifts_from_solution(solution)
    reduced = build_reduced_input(
        full_data, used_v, used_s, force_fixed_cost=(args.cost == "fixed")
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(reduced, f, indent=2, ensure_ascii=False)

    n_visits = len(reduced["modelInput"]["visits"])
    n_vehicles = len(reduced["modelInput"]["vehicles"])
    n_shifts = sum(
        len(v.get("shifts", [])) for v in reduced["modelInput"]["vehicles"]
    )
    print(
        f"Wrote reduced input to {args.output}: "
        f"{n_visits} visits, {n_vehicles} vehicles, {n_shifts} shifts "
        f"(no oversupply)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
