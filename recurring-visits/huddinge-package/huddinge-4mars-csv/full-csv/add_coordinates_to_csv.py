#!/usr/bin/env python3
"""
Add Lat and Lon columns to ATTENDO_DATABEHOV_ALL_81_CLIENTS.csv using
address_coordinates.json. Uses same address normalization as attendo_4mars_to_fsr.py.
Run from this directory or from recurring-visits with paths adjusted.
"""
import csv
import json
import re
import sys
from pathlib import Path

# Reuse address logic from attendo_4mars_to_fsr
SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from attendo_4mars_to_fsr import _address_string_4mars, _normalize_address_for_fallback_lookup

CSV_PATH = Path(__file__).resolve().parent / "ATTENDO_DATABEHOV_ALL_81_CLIENTS.csv"
JSON_PATH = Path(__file__).resolve().parent / "address_coordinates.json"


def main() -> int:
    if not JSON_PATH.exists():
        print(f"Error: {JSON_PATH} not found. Run build_address_coordinates.py first.", file=sys.stderr)
        return 1
    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found.", file=sys.stderr)
        return 1

    with open(JSON_PATH, encoding="utf-8") as f:
        coords_map = json.load(f)

    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    if "Lat" in fieldnames and "Lon" in fieldnames:
        print("CSV already has Lat and Lon columns.", file=sys.stderr)
        return 0

    # Insert Lat, Lon after Ort
    ort_idx = fieldnames.index("Ort") + 1 if "Ort" in fieldnames else len(fieldnames)
    new_fieldnames = fieldnames[:ort_idx] + ["Lat", "Lon"] + fieldnames[ort_idx:]
    missing = []

    for row in rows:
        addr = _address_string_4mars(row)
        norm = _normalize_address_for_fallback_lookup(addr)
        if not norm:
            row["Lat"] = ""
            row["Lon"] = ""
            continue
        coords = coords_map.get(norm) or coords_map.get(norm.replace(", sweden", "").strip())
        if coords and len(coords) >= 2:
            row["Lat"] = str(coords[0])
            row["Lon"] = str(coords[1])
        else:
            row["Lat"] = ""
            row["Lon"] = ""
            if norm not in missing:
                missing.append(norm)

    if missing:
        print(f"Warning: {len(missing)} address(es) not in address_coordinates.json:", file=sys.stderr)
        for m in sorted(missing)[:10]:
            print(f"  - {m}", file=sys.stderr)
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more", file=sys.stderr)

    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Added Lat, Lon to {CSV_PATH}. Rows: {len(rows)}.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
