#!/usr/bin/env python3
"""
Clean visit address fields in an Attendo-format CSV so geocoding lookups succeed.

- Gata: same normalization as attendo_4mars_to_fsr (_normalize_gata): strip LGH, VÅN,
  våning, lägenhet, trappor/tr, trailing comma, collapse spaces, street-name fixes.
  Every row must geocode; no fallback — fix CSV and re-run if any address fails.
- Postnr: remove spaces (e.g. "141 44" -> "14144").

Usage:
  python cleanup_addresses_in_csv.py "huddinge-81-clients - Data.csv"
  python cleanup_addresses_in_csv.py "v2/huddinge-81-clients-v2 - Data.csv" -o "v2/huddinge-81-clients-v2 - Data-cleaned.csv"
"""

import argparse
import csv
import re
import sys
from pathlib import Path

# Import FSR normalization so cleanup and geocoding use the same address string
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
from attendo_4mars_to_fsr import _normalize_gata  # noqa: E402


def clean_postnr(s: str) -> str:
    if not s:
        return ""
    return re.sub(r"\s+", "", str(s).strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean Gata and Postnr in Attendo CSV")
    parser.add_argument("csv_path", type=Path, help="Input CSV")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output path (default: overwrite input)")
    args = parser.parse_args()

    p = args.csv_path.resolve()
    if not p.exists():
        print(f"Error: {p} not found.", file=sys.stderr)
        return 1
    out = (args.output or p).resolve()

    with open(p, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    if "Gata" not in fieldnames:
        print("Error: CSV has no Gata column.", file=sys.stderr)
        return 1

    changes = 0
    for row in rows:
        g = row.get("Gata", "")
        pnr = row.get("Postnr", "")
        g2 = _normalize_gata(g)
        pnr2 = clean_postnr(pnr)
        if g != g2 or pnr != pnr2:
            changes += 1
        row["Gata"] = g2
        if "Postnr" in row:
            row["Postnr"] = pnr2

    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"Cleaned {changes} row(s). Wrote {out}.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
