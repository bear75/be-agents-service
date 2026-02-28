#!/usr/bin/env python3
"""
Validate visitGroup_id pairs in SOURCE CSV: do all visits in each group overlap?

For multi-vehicle visits, both employees must be at the client at the SAME time.
In the source, each row has occurence (e.g. "Varje vecka, mån" = Monday).
Two visits overlap only if they occur on the SAME weekday.

If visitGroup_id 16 has:
  - visit A: "Varje vecka, mån" (Monday)
  - visit B: "Varje vecka, tis" (Tuesday)
Then they NEVER overlap — source is incorrect for multi-vehicle grouping.

Usage:
  python validate_source_visit_groups.py ../source/Huddinge_recurring_v2.csv
"""

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

# Swedish weekday in occurence -> normalized key
OCCURRENCE_WEEKDAY = {
    "mån": 0, "månag": 0, "måndag": 0,
    "tis": 1, "tisdag": 1,
    "ons": 2, "onsdag": 2,
    "tor": 3, "torsdag": 3,
    "fre": 4, "fredag": 4,
    "lör": 5, "lördag": 5,
    "sön": 6, "söndag": 6,
}


def parse_weekday(occ: str) -> int | None:
    """Parse weekday from occurence e.g. 'Varje vecka, mån' -> 0."""
    if not occ:
        return None
    s = str(occ).strip().lower()
    for key, wd in OCCURRENCE_WEEKDAY.items():
        if key in s:
            return wd
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate visitGroup_id overlap in source CSV.")
    ap.add_argument("source", type=Path, help="Source CSV (Huddinge_recurring_v2.csv).")
    ap.add_argument("--delimiter", default=";", help="CSV delimiter.")
    args = ap.parse_args()

    if not args.source.exists():
        print(f"Error: not found {args.source}", file=sys.stderr)
        return 1

    groups: dict[str, list[dict]] = defaultdict(list)
    with open(args.source, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=args.delimiter)
        for row in reader:
            vgid = str(row.get("visitGroup_id", "")).strip()
            if not vgid:
                continue
            visit_id = row.get("visit_id", "?")
            # Weekday text: occurence (typo) or recurring_external (e.g. "Varje vecka, tis")
            occ = row.get("occurence", "") or row.get("recurring_external", "")
            start_time = row.get("startTime", "")
            recurring = row.get("recurringVisit_clientName", "")
            weekday = parse_weekday(occ)
            groups[vgid].append({
                "visit_id": visit_id,
                "occurence": occ,
                "weekday": weekday,
                "startTime": start_time,
                "recurring": recurring[:40],
            })

    ok_count = 0
    fail_count = 0
    for vgid in sorted(groups.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        rows = groups[vgid]
        if len(rows) < 2:
            continue

        weekdays = [r["weekday"] for r in rows if r["weekday"] is not None]
        unique_wd = set(weekdays)

        # Overlap = all visits share at least one weekday
        # If we have 2 visits with different weekdays (e.g. Mon and Tue), they never overlap
        if len(unique_wd) > 1 and len(rows) >= 2:
            # Different weekdays -> no overlap
            fail_count += 1
            print(f"FAIL visitGroup_id={vgid}: visits on DIFFERENT weekdays (never overlap)")
            for r in rows:
                wd_str = "Mon" if r["weekday"] == 0 else "Tue" if r["weekday"] == 1 else "Wed" if r["weekday"] == 2 else "Thu" if r["weekday"] == 3 else "Fri" if r["weekday"] == 4 else "Sat" if r["weekday"] == 5 else "Sun" if r["weekday"] == 6 else "?"
                print(f"    visit_id={r['visit_id']}  occurence={r['occurence']} ({wd_str})  startTime={r['startTime']}  {r['recurring']}")
        else:
            ok_count += 1
            print(f"OK   visitGroup_id={vgid}: {len(rows)} visits, same weekday(s)")

    total = ok_count + fail_count
    print(f"\nSummary: {ok_count} OK, {fail_count} FAIL (total {total} groups with 2+ visits)")
    if fail_count > 0:
        print("\nSource is INCORRECT for multi-vehicle: visits in same group must occur on SAME weekday.")
    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
