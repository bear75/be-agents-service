#!/usr/bin/env python3
"""
Patch an FSR input JSON with requiredVehicles = [exact slinga vehicle] per visit,
using external_slinga_shiftName from the expanded CSV.

This replicates the manual schedule strategy: each visit is assigned to exactly
the slinga (vehicle) that the manual schedule uses. FSR then optimizes routing
within that constraint.

Usage:
  python patch_visits_slinga_direct.py \\
    --expanded-csv expanded/huddinge_2wk_expanded_20260224_043456.csv \\
    --fsr-input solve/input_20260224_202857.json \\
    --output solve/research/approach-0/input_slinga_direct.json
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path


def _slug(s: str) -> str:
    """Same as generate_employees.py: remove non-word chars, spaces -> underscores."""
    slug = re.sub(r"[^\w\s-]", "", s.strip())
    slug = re.sub(r"[\s_]+", "_", slug).strip("_")
    return slug or "employee"


def patch_visits(expanded_csv: Path, fsr_input: Path, output: Path) -> None:
    # Build lookup: original_visit_id -> list of vehicle_ids (preserving order, deduped)
    with open(expanded_csv, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    visit_to_pool: dict[str, list[str]] = {}
    for row in rows:
        vid = row.get("original_visit_id", "").strip()
        slinga = row.get("external_slinga_shiftName", "").strip()
        if not vid or not slinga:
            continue
        veh_id = _slug(slinga)
        if vid not in visit_to_pool:
            visit_to_pool[vid] = []
        if veh_id not in visit_to_pool[vid]:
            visit_to_pool[vid].append(veh_id)

    with open(fsr_input, encoding="utf-8") as f:
        payload = json.load(f)

    mi = payload["modelInput"]
    valid_vehicle_ids = {v.get("id") for v in mi.get("vehicles", []) if v.get("id")}
    patched = skipped = invalid = 0

    def patch_visit(visit: dict) -> None:
        nonlocal patched, skipped, invalid
        pool = visit_to_pool.get(visit["id"])
        if not pool:
            skipped += 1
            return
        # Only include vehicle IDs that exist in the FSR input (avoid DATASET_INVALID)
        valid_pool = [v for v in pool if v in valid_vehicle_ids]
        if not valid_pool:
            invalid += 1
            return
        visit["requiredVehicles"] = valid_pool
        patched += 1

    for visit in mi.get("visits", []):
        patch_visit(visit)
    for group in mi.get("visitGroups", []):
        for visit in group.get("visits", []):
            patch_visit(visit)

    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"Patched {patched} visits, skipped {skipped} (no slinga match), {invalid} (slinga not in FSR vehicles)")
    print(f"Wrote: {output}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Patch FSR input with exact slinga requiredVehicles"
    )
    parser.add_argument("--expanded-csv", type=Path, required=True)
    parser.add_argument("--fsr-input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if not args.expanded_csv.exists():
        print(f"Error: {args.expanded_csv} not found", file=sys.stderr)
        return 1
    if not args.fsr_input.exists():
        print(f"Error: {args.fsr_input} not found", file=sys.stderr)
        return 1

    patch_visits(args.expanded_csv, args.fsr_input, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
