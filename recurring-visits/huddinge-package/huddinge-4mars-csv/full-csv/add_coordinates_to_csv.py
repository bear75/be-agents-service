#!/usr/bin/env python3
"""
Add Lat and Lon columns to an Attendo-format CSV using an address_coordinates.json
file. Uses the same address normalization as attendo_4mars_to_fsr.py.

Use this as a pre-step so that the CSV has coordinates for:
- Dashboard seed (beta-appcaire: yarn db:seed:attendo with ATTENDO_CSV_PATH)
- Dashboard CSV upload (schedule import)

Run from full-csv/ or from recurring-visits with paths relative to full-csv/.

Usage:
  python full-csv/add_coordinates_to_csv.py full-csv/10-mars-new-attendo/huddinge-81-clients\\ -\\ Data.csv \\
    --coordinates full-csv/10-mars-new-attendo/address_coordinates.json \\
    -o full-csv/10-mars-new-attendo/huddinge-81-clients-with-coords.csv

  # Default -o: same dir as CSV, name "<basename>-with-coords.csv"
  python full-csv/add_coordinates_to_csv.py full-csv/10-mars-new-attendo/huddinge-81-clients\\ -\\ Data.csv \\
    --coordinates full-csv/10-mars-new-attendo/address_coordinates.json
"""
import argparse
import csv
import json
import sys
from pathlib import Path

# Reuse address logic from attendo_4mars_to_fsr
SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from attendo_4mars_to_fsr import (  # noqa: E402
    _address_string_4mars,
    _normalize_address_for_fallback_lookup,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add Lat/Lon columns to Attendo CSV using address_coordinates.json."
    )
    parser.add_argument(
        "csv_path",
        type=Path,
        help="Input Attendo CSV (Gata, Postnr, Ort columns).",
    )
    parser.add_argument(
        "--coordinates",
        "-c",
        type=Path,
        required=True,
        help="Path to address_coordinates.json (from build_address_coordinates.py).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output CSV path. Default: same dir as input, basename with '-with-coords' before .csv.",
    )
    args = parser.parse_args()

    csv_path = args.csv_path.resolve()
    json_path = args.coordinates.resolve()

    if not json_path.exists():
        print(
            f"Error: {json_path} not found. Run build_address_coordinates.py first.",
            file=sys.stderr,
        )
        return 1
    if not csv_path.exists():
        print(f"Error: {csv_path} not found.", file=sys.stderr)
        return 1

    if args.output is not None:
        out_path = args.output.resolve()
    else:
        stem = csv_path.stem
        out_path = csv_path.parent / f"{stem}-with-coords{csv_path.suffix}"

    with open(json_path, encoding="utf-8") as f:
        coords_map = json.load(f)

    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    if "Lat" in fieldnames and "Lon" in fieldnames:
        print(
            "CSV already has Lat and Lon columns. Copying to output unchanged.",
            file=sys.stderr,
        )
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {out_path}. Rows: {len(rows)}.", file=sys.stderr)
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
        coords = coords_map.get(norm) or coords_map.get(
            norm.replace(", sweden", "").strip()
        )
        if coords and len(coords) >= 2:
            row["Lat"] = str(coords[0])
            row["Lon"] = str(coords[1])
        else:
            row["Lat"] = ""
            row["Lon"] = ""
            if norm not in missing:
                missing.append(norm)

    if missing:
        print(
            f"Warning: {len(missing)} address(es) not in {json_path.name}:",
            file=sys.stderr,
        )
        for m in sorted(missing)[:10]:
            print(f"  - {m}", file=sys.stderr)
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more", file=sys.stderr)

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Added Lat, Lon to {out_path}. Rows: {len(rows)}.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
