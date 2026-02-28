#!/usr/bin/env python3
"""
Validate visit groups: ensure all visits in each group have overlapping time windows.

Timefold multi-vehicle visits require visits in a group to be schedulable at the same time.
If time windows don't overlap, scheduling is impossible.

Usage:
  python validate_visit_groups.py ../solve/input_20260213_195240.json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def parse_iso_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def overlap(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    """True if [a_start, a_end] overlaps [b_start, b_end]."""
    return a_start < b_end and b_start < a_end


def check_visit_group(group: dict) -> tuple[bool, str]:
    """
    Check if all visits in a group have pairwise overlapping time windows.
    Returns (ok, message).
    """
    visits = group.get("visits", [])
    if len(visits) < 2:
        return True, "single visit (no overlap needed)"

    windows: list[tuple[datetime, datetime]] = []
    for v in visits:
        tws = v.get("timeWindows", [])
        if not tws:
            return False, f"visit {v.get('id')} has no time window"
        tw = tws[0]
        mn = parse_iso_dt(tw.get("minStartTime"))
        mx = parse_iso_dt(tw.get("maxEndTime"))
        if not mn or not mx:
            return False, f"visit {v.get('id')} has invalid time window"
        windows.append((mn, mx))

    for i in range(len(windows)):
        for j in range(i + 1, len(windows)):
            a_s, a_e = windows[i]
            b_s, b_e = windows[j]
            if not overlap(a_s, a_e, b_s, b_e):
                return False, (
                    f"visits {visits[i].get('id')} and {visits[j].get('id')} "
                    f"have non-overlapping windows: "
                    f"[{a_s.isoformat()}, {a_e.isoformat()}] vs [{b_s.isoformat()}, {b_e.isoformat()}]"
                )
    return True, "all overlap"


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate visit group time window overlap.")
    ap.add_argument("input", type=Path, help="Timefold input JSON.")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"Error: not found {args.input}", file=sys.stderr)
        return 1

    with open(args.input) as f:
        data = json.load(f)

    mi = data.get("modelInput") or data
    groups = mi.get("visitGroups", [])

    if not groups:
        print("No visit groups in input.")
        return 0

    ok_count = 0
    fail_count = 0
    for g in groups:
        gid = g.get("id", "?")
        ok, msg = check_visit_group(g)
        if ok:
            ok_count += 1
            print(f"OK  {gid}: {msg}")
        else:
            fail_count += 1
            print(f"FAIL {gid}: {msg}")

    print(f"\nSummary: {ok_count} OK, {fail_count} FAIL (total {len(groups)} groups)")
    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
