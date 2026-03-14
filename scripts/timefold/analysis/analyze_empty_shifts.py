#!/usr/bin/env python3
"""
Analyze empty shifts: list them and check if they overlap with unassigned visit time windows.

Empty shifts = shifts with no visits. If unassigned visits have time windows that overlap
with empty shift hours, there may be a scheduling opportunity we're missing.

Usage:
  python analyze_empty_shifts.py solve/input.json solve/output.json
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
    return a_start < b_end and b_start < a_end


def run_analysis(mi: dict, mo: dict) -> str:
    """
    Run empty-shifts analysis on already-loaded input/output model data.
    Returns report text.
    """
    unassigned = mo.get("unassignedVisits") or []

    # Build shift_id -> (start, end) from input
    shift_windows: dict[str, tuple[datetime, datetime]] = {}
    for v in mi.get("vehicles", []):
        for s in v.get("shifts", []):
            sid = s.get("id", "")
            st = parse_iso_dt(s.get("minStartTime"))
            et = parse_iso_dt(s.get("maxEndTime"))
            if st and et:
                shift_windows[sid] = (st, et)

    # Shifts with no visits (from output)
    empty_shift_ids: list[str] = []
    for v in mo.get("vehicles", []):
        for s in v.get("shifts", []):
            itinerary = s.get("itinerary") or []
            visits = [x for x in itinerary if isinstance(x, dict) and x.get("kind") == "VISIT"]
            if not visits:
                empty_shift_ids.append(s.get("id", "?"))

    vid_by_shift: dict[str, str] = {}
    for v in mi.get("vehicles", []):
        vid = v.get("id", "?")
        for s in v.get("shifts", []):
            vid_by_shift[s.get("id", "")] = vid

    def get_tws(v: dict) -> list[tuple[datetime, datetime]]:
        result = []
        for tw in v.get("timeWindows", []):
            mn = parse_iso_dt(tw.get("minStartTime"))
            mx = parse_iso_dt(tw.get("maxEndTime"))
            if mn and mx:
                result.append((mn, mx))
        return result

    unassigned_ids = {str(u) for u in unassigned} if unassigned else set()
    unassigned_tws: list[tuple[str, datetime, datetime]] = []
    for v in mi.get("visits", []):
        uid = str(v.get("id", "?"))
        if uid in unassigned_ids:
            for mn, mx in get_tws(v):
                unassigned_tws.append((uid, mn, mx))
    for g in mi.get("visitGroups", []):
        for v in g.get("visits", []):
            uid = str(v.get("id", "?"))
            if uid in unassigned_ids:
                for mn, mx in get_tws(v):
                    unassigned_tws.append((uid, mn, mx))

    overlap_count = 0
    overlap_lines: list[str] = []
    for sid in empty_shift_ids:
        sw = shift_windows.get(sid)
        if not sw:
            continue
        for uid, uw_s, uw_e in unassigned_tws:
            if overlap(sw[0], sw[1], uw_s, uw_e):
                overlap_count += 1
                overlap_lines.append(f"  {sid} overlaps visit {uid} [{uw_s.isoformat()} - {uw_e.isoformat()}]")
                break

    lines = [
        f"Empty shifts: {len(empty_shift_ids)} / {len(shift_windows)}",
        f"Unassigned visits: {len(unassigned)}",
        "",
        "--- Empty shifts (shift_id, vehicle, start, end) ---",
    ]
    for sid in sorted(empty_shift_ids):
        w = shift_windows.get(sid)
        vid = vid_by_shift.get(sid, "?")
        if w:
            lines.append(f"  {sid}  {vid}  {w[0].isoformat()} -- {w[1].isoformat()}")
        else:
            lines.append(f"  {sid}  {vid}  (no window)")
    lines.extend([
        "",
        "--- Empty shifts overlapping unassigned visit windows ---",
    ])
    if not overlap_lines and unassigned_tws:
        lines.append("  (none)")
    lines.extend(overlap_lines)
    lines.extend([
        "",
        f"Summary: {overlap_count} empty shifts overlap with unassigned visit time windows",
    ])
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Analyze empty shifts vs unassigned visits.")
    ap.add_argument("input", type=Path, help="Timefold input JSON.")
    ap.add_argument("output", type=Path, help="Timefold output JSON.")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"Error: not found {args.input}", file=sys.stderr)
        return 1
    if not args.output.exists():
        print(f"Error: not found {args.output}", file=sys.stderr)
        return 1

    with open(args.input) as f:
        inp = json.load(f)
    with open(args.output) as f:
        out = json.load(f)
    mi = inp.get("modelInput") or inp
    mo = out.get("modelOutput") or out

    print(run_analysis(mi, mo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
