#!/usr/bin/env python3
"""
Compute per-client continuity for the MANUAL schedule from the expanded CSV.

Uses:
  - client_externalId = client (e.g. H015, H026)
  - external_slinga_shiftName = employee (shift/caregiver)
  - continuity = number of distinct employees per client (lower is better)

Output: client, nr_visits, continuity — same format as continuity_report.py for comparison.

Usage:
  python continuity_manual_from_csv.py --csv path/to/huddinge_2wk_expanded_*.csv [--report path/to/continuity_manual.csv]
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Per-client continuity from manual schedule (expanded CSV)"
    )
    parser.add_argument(
        "--csv",
        type=Path,
        required=True,
        help="Expanded CSV (e.g. huddinge_2wk_expanded_*.csv)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Optional: write CSV to this path",
    )
    args = parser.parse_args()

    if not args.csv.exists():
        print(f"Error: CSV not found: {args.csv}", file=sys.stderr)
        return 1

    # client_externalId -> set of external_slinga_shiftName (employees)
    client_employees: dict[str, set[str]] = {}
    client_visit_count: dict[str, int] = {}

    with open(args.csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "client_externalId" not in reader.fieldnames or "external_slinga_shiftName" not in reader.fieldnames:
            print(
                "Error: CSV must have columns client_externalId and external_slinga_shiftName",
                file=sys.stderr,
            )
            return 1
        for row in reader:
            client = (row.get("client_externalId") or "").strip()
            employee = (row.get("external_slinga_shiftName") or "").strip()
            if not client:
                continue
            client_visit_count[client] = client_visit_count.get(client, 0) + 1
            if employee:
                client_employees.setdefault(client, set()).add(employee)

    # Build rows: client, nr_visits, continuity (distinct employees)
    rows: list[tuple[str, int, int]] = []
    for client in sorted(client_visit_count.keys()):
        nr_visits = client_visit_count[client]
        continuity = len(client_employees.get(client, set()))
        rows.append((client, nr_visits, continuity))

    print("client,nr_visits,continuity")
    print("(manual schedule; continuity = distinct employees; lower is better)")
    print("-" * 50)
    for client, nr_visits, continuity in rows:
        print(f"{client},{nr_visits},{continuity}")

    total_visits = sum(r[1] for r in rows)
    print("\n" + "=" * 50)
    print("Summary (manual schedule from expanded CSV)")
    print("=" * 50)
    print(f"  Total visits:  {total_visits}")
    print(f"  Clients:       {len(rows)}")
    if rows:
        avg_cont = sum(r[2] for r in rows) / len(rows)
        max_cont = max(r[2] for r in rows)
        min_cont = min(r[2] for r in rows)
        print(f"  Continuity:    min={min_cont}, max={max_cont}, avg={avg_cont:.1f}")

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with open(args.report, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["client", "nr_visits", "continuity"])
            w.writerows(rows)
        print(f"\nWrote {args.report}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
