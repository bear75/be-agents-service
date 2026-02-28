#!/usr/bin/env python3
"""
Anonymize recurring visits CSV for demo data.

Maps client IDs, client names, contact names, and shift names to anonymized values.
Output format: same structure (semicolon delimiter). Write to demo-data/source/source.csv.

Usage:
  python anonymize_huddinge_to_demo.py <source.csv> -o demo-data/source/source.csv
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Any, Dict, List

CLIENT_PREFIX = "Client"
DRIVER_PREFIX = "Driver"
ADDRESS_PREFIX = "Anonymized"


def _next_id(seen: set, prefix: str, width: int = 3) -> str:
    n = len(seen)
    return f"{prefix}-{str(n + 1).zfill(width)}"


def anonymize_row(
    row: Dict[str, Any],
    client_map: Dict[str, str],
    driver_map: Dict[str, str],
) -> Dict[str, Any]:
    """Anonymize a single row."""
    out = dict(row)

    client_id = str(row.get("client_externalId", "")).strip()
    if client_id and client_id not in client_map:
        client_map[client_id] = _next_id(set(client_map.values()), CLIENT_PREFIX)
    if client_id:
        cid = client_map[client_id]
        out["client_externalId"] = cid
        out["recurringVisit_clientName"] = f"{cid}_1"
        out["client_caireConact"] = cid
        out["client_caireContact"] = cid
        out["client_addressStreet"] = f"{ADDRESS_PREFIX} Street {cid}"
        # Keep postal code and city for geocoding lookup if needed
        # out["client_addressPostalCdode"] = "000 00"
        # out["client_addressCity"] = "Anonymized"

    shift_name = str(row.get("external_slinga_shiftName", "")).strip()
    if shift_name and shift_name.lower() not in {"", "städ", "vilande kunder/besök"}:
        if shift_name not in driver_map:
            driver_map[shift_name] = _next_id(set(driver_map.values()), DRIVER_PREFIX, 2)
        out["external_slinga_shiftName"] = driver_map[shift_name]

    return out


def anonymize_huddinge(
    input_path: Path,
    output_path: Path,
    delimiter: str = ";",
) -> int:
    """Anonymize Huddinge CSV. Returns number of rows written."""
    with open(input_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)
        fieldnames = reader.fieldnames or list(rows[0].keys()) if rows else []

    client_map: Dict[str, str] = {}
    driver_map: Dict[str, str] = {}

    out_rows: List[Dict[str, Any]] = []
    for row in rows:
        out_rows.append(anonymize_row(row, client_map, driver_map))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Anonymized {len(out_rows)} rows")
    print(f"  Clients: {len(client_map)} unique → {CLIENT_PREFIX}-*")
    print(f"  Drivers: {len(driver_map)} unique → {DRIVER_PREFIX}-*")
    print(f"Wrote: {output_path}")
    return len(out_rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Anonymize Huddinge CSV for demo data")
    parser.add_argument("input", type=Path, help="Huddinge source CSV")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output path (e.g. demo-data/source/huddinge_anonymized.csv)")
    parser.add_argument("--delimiter", default=";")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input not found: {args.input}", file=sys.stderr)
        return 1

    try:
        anonymize_huddinge(args.input, args.output, delimiter=args.delimiter)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
