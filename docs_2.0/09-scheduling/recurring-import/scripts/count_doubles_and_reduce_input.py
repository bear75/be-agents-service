#!/usr/bin/env python3
"""
1) Count double visits in the input: distinct double_id values (from CSV) for
   visit_ids that appear in the FSR input. One double_id = one "double" (e.g. 1 and 1 = one double).
2) Build reduced input from from-patch output: only vehicles and shifts that have visits.
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if ROOT.name == "scripts":
    ROOT = ROOT.parent
DIR = ROOT
CSV_PATH = DIR / "data/anonymized/movable_visits_anonymized_v2.csv"
# Input that matches the from-patch visits (same visit ids)
INPUT_PATH = DIR / "data/anonymized/movable_visits_unplanned_input.json"
FROM_PATCH_OUTPUT = DIR / "fixed/from-patch-reduced/export-field-service-routing-5ff46c3d-f7c3-40bd-9428-5ee24fc5bcd9-output.json"
OUTPUT_REDUCED = DIR / "fixed/from-patch-reduced/input-only-used-shifts.json"

sys.path.insert(0, str(ROOT / "scripts"))
from build_reduced_input import used_vehicles_and_shifts_from_solution  # noqa: E402


def get_input_visit_ids(input_path: Path) -> set[str]:
    """Return set of visit ids (as str) from FSR modelInput."""
    with open(input_path) as f:
        data = json.load(f)
    mi = data.get("modelInput") or data
    return {str(v.get("id")) for v in mi.get("visits", []) if v.get("id") is not None}


def get_visit_id_to_double_id(csv_path: Path) -> dict[str, str]:
    """From CSV (header on row 2), return map visit_id -> double_id (empty string if missing)."""
    out: dict[str, str] = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)  # row 0
        next(reader)  # row 1
        headers = next(reader)  # row 2
        try:
            vid_idx = headers.index("visit_id")
            did_idx = headers.index("double_id")
        except ValueError:
            return out
        for row in reader:
            if len(row) > max(vid_idx, did_idx):
                vid = (row[vid_idx] or "").strip()
                did = (row[did_idx] or "").strip()
                if vid:
                    out[vid] = did
    return out


def count_doubles_in_input(input_path: Path, csv_path: Path) -> tuple[int, int]:
    """
    Return (num_doubles, num_visits_in_doubles).
    One double = one distinct double_id that appears in the input (e.g. double_id 1 and 1 = 1 double).
    """
    input_ids = get_input_visit_ids(input_path)
    visit_to_double = get_visit_id_to_double_id(csv_path)
    double_ids_seen: set[str] = set()
    visits_in_doubles = 0
    for vid in input_ids:
        did = visit_to_double.get(vid, "")
        if did:
            double_ids_seen.add(did)
            visits_in_doubles += 1
    return len(double_ids_seen), visits_in_doubles


def main() -> int:
    # 1) Double count
    if CSV_PATH.exists() and INPUT_PATH.exists():
        num_doubles, num_visits_in_doubles = count_doubles_in_input(INPUT_PATH, CSV_PATH)
        print(f"Input visit ids (from {INPUT_PATH.name}): {len(get_input_visit_ids(INPUT_PATH))}")
        print(f"Double visits: {num_doubles} distinct double_id values (= {num_doubles} doubles)")
        print(f"Visits that have a double_id: {num_visits_in_doubles}")
    else:
        print("CSV or input not found, skipping double count.")

    # 2) Build reduced input (only used vehicles and used shifts from from-patch output)
    if not FROM_PATCH_OUTPUT.exists():
        print(f"From-patch output not found: {FROM_PATCH_OUTPUT}", file=sys.stderr)
        return 1
    if not INPUT_PATH.exists():
        print(f"Input not found: {INPUT_PATH}", file=sys.stderr)
        return 1

    with open(FROM_PATCH_OUTPUT) as f:
        solution = json.load(f)
    with open(INPUT_PATH) as f:
        full_input = json.load(f)

    used_v, used_s = used_vehicles_and_shifts_from_solution(solution)
    mi = full_input.get("modelInput") or full_input
    visits = mi.get("visits", [])
    vehicles_in = mi.get("vehicles", [])
    vehicles_out = []
    for v in vehicles_in:
        if v.get("id") not in used_v:
            continue
        shifts = [s for s in v.get("shifts", []) if s.get("id") in used_s]
        if not shifts:
            continue
        vehicles_out.append({**v, "shifts": shifts})

    # Fixed cost
    FIXED = 1375
    for v in vehicles_out:
        for s in v.get("shifts", []):
            s["cost"] = {"fixedCost": FIXED, "rates": []}

    reduced = {
        "modelInput": {
            "visits": visits,
            "vehicles": vehicles_out,
        }
    }

    OUTPUT_REDUCED.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_REDUCED, "w") as f:
        json.dump(reduced, f, indent=2, ensure_ascii=False)

    n_shifts = sum(len(v.get("shifts", [])) for v in vehicles_out)
    print(f"\nReduced input (only used vehicles and shifts): {OUTPUT_REDUCED}")
    print(f"  Vehicles: {len(vehicles_out)}, Shifts: {n_shifts}, Visits: {len(visits)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
