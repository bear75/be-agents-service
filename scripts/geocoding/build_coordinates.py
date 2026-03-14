#!/usr/bin/env python3
"""
Build a JSON file mapping every unique CSV address -> [lat, lon] for use with
attendo_4mars_to_fsr.py --address-coordinates. All addresses must resolve via Nominatim;
no fallback. If any address fails, clean Gata in CSV (remove LGH, VÅN, våning, etc.) and re-run.

Usage:
  python build_address_coordinates.py full-csv/ATTENDO_DATABEHOV_ALL_81_CLIENTS.csv -o full-csv/address_coordinates.json
"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

# Same address logic and geocoding as attendo_4mars_to_fsr
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from attendo_4mars_to_fsr import (
    _address_string_4mars,
    _geocode_nominatim,
    _normalize_address_for_fallback_lookup,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Geocode all unique CSV addresses and write address -> [lat, lon] JSON"
    )
    parser.add_argument("csv_path", type=Path, help="Input CSV (same columns as 4mars)")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output JSON path")
    parser.add_argument("--geocode-rate", type=float, default=1.0, help="Seconds between Nominatim requests")
    parser.add_argument(
        "--merge-existing",
        type=Path,
        default=None,
        help="Existing address_coordinates.json to reuse for addresses Nominatim misses (same normalized keys)",
    )
    args = parser.parse_args()

    if not args.csv_path.exists():
        print(f"Error: CSV not found: {args.csv_path}", file=sys.stderr)
        return 1

    with open(args.csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")
        rows = list(reader)

    unique_addresses: set[str] = set()
    for row in rows:
        addr = _address_string_4mars(row)
        if addr and addr.strip():
            unique_addresses.add(addr.strip())

    if not unique_addresses:
        print("No addresses found in CSV.", file=sys.stderr)
        return 1

    external_coordinates: Optional[dict[str, Tuple[float, float]]] = None
    if args.merge_existing and args.merge_existing.exists():
        with open(args.merge_existing, encoding="utf-8") as f:
            raw = json.load(f)
        external_coordinates = {k: (float(v[0]), float(v[1])) for k, v in raw.items() if isinstance(v, list) and len(v) >= 2}
        print(f"Loaded {len(external_coordinates)} existing coordinates from {args.merge_existing}", file=sys.stderr)

    print(f"Geocoding {len(unique_addresses)} unique address(es)...", file=sys.stderr)
    cache: dict[str, Tuple[Optional[float], Optional[float]]] = {}
    out: dict[str, list[float]] = {}
    failed: list[str] = []

    for i, addr in enumerate(sorted(unique_addresses)):
        lat, lon = _geocode_nominatim(addr, cache, external_coordinates=external_coordinates)
        if lat is not None and lon is not None:
            norm = _normalize_address_for_fallback_lookup(addr)
            if norm:
                out[norm] = [lat, lon]
        else:
            failed.append(addr)
        if i < len(unique_addresses) - 1:
            time.sleep(args.geocode_rate)

    if failed:
        print("ERROR: The following addresses have no coordinates (Nominatim failed). No fallback allowed.", file=sys.stderr)
        for a in sorted(failed):
            print(f"  - {a}", file=sys.stderr)
        print("Clean Gata in CSV (remove LGH, VÅN, våning, lägenhet, trappor, etc.) and re-run.", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(out)} address(es) to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
