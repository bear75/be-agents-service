#!/usr/bin/env python3
"""
Verify Timefold FSR solution output: count unassigned visits (goal: 0).

Reads modelOutput.unassignedVisits from a solution JSON (GET response or saved output).

Usage:
  python3 verify_unassigned.py path/to/output.json
  python3 verify_unassigned.py path/to/output.json --max 0    # fail if count > 0 (default)
  python3 verify_unassigned.py path/to/output.json --warn-only # always exit 0

Exit: 0 if within --max (default 0), else 1.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _count_unassigned(data: dict) -> tuple[int, list[str]]:
    mo = data.get("modelOutput") or data.get("model_output") or {}
    if not isinstance(mo, dict):
        return 0, []
    raw = mo.get("unassignedVisits") or mo.get("unassigned_visits")
    if raw is None:
        # Some exports only have KPI total
        total = mo.get("totalUnassignedVisits")
        if total is not None:
            return int(total), []
        return 0, []
    if isinstance(raw, list):
        return len(raw), [str(x) for x in raw]
    return 0, []


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify unassigned visit count in Timefold output JSON")
    ap.add_argument("output_json", type=Path, help="Solution JSON (modelOutput with unassignedVisits)")
    ap.add_argument(
        "--max",
        type=int,
        default=0,
        help="Maximum allowed unassigned visits (default: 0)",
    )
    ap.add_argument(
        "--warn-only",
        action="store_true",
        help="Print count but always exit 0",
    )
    args = ap.parse_args()

    path = args.output_json.expanduser().resolve()
    if not path.exists():
        print(
            f"Error: file not found: {path}\n"
            f"  (cwd: {Path.cwd()})\n"
            f"  Pass full path to Timefold solution JSON, e.g.:\n"
            f"    python3 scripts/verification/verify_unassigned.py recurring-visits/.../output.json",
            file=sys.stderr,
        )
        return 1

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    n, ids = _count_unassigned(data)
    print(f"Unassigned visits: {n} (max allowed: {args.max})")
    if ids and n <= 20:
        for i in ids:
            print(f"  {i}")
    elif ids and n > 20:
        for i in ids[:10]:
            print(f"  {i}")
        print(f"  ... and {n - 10} more")

    if args.warn_only:
        return 0
    return 0 if n <= args.max else 1


if __name__ == "__main__":
    raise SystemExit(main())
