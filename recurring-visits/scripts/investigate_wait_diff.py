#!/usr/bin/env python3
"""
Compare wait time: itinerary sum (startServiceTime - arrivalTime) vs API totalWaitingTime.

Finding: The API's totalWaitingTime = wait excluding overlap with BREAK.
When an employee arrives early and then has a break before the allowed service start,
the API counts only the wait after the break (pure wait), not the full arrival-to-start
interval. So: raw itinerary wait (147h) - break-overlap (95.5h) = API wait (52h).

Usage:
  python investigate_wait_diff.py path/to/output.json
"""

import json
import sys
from pathlib import Path

# Reuse metrics parsing
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from metrics import parse_duration_seconds, parse_iso_dt


def wait_from_itinerary(shift: dict) -> float:
    """Sum over VISIT items: max(0, startServiceTime - arrivalTime) in seconds."""
    total = 0.0
    for item in shift.get("itinerary") or []:
        if not isinstance(item, dict) or item.get("kind") != "VISIT":
            continue
        arr = parse_iso_dt(item.get("arrivalTime"))
        svc = parse_iso_dt(item.get("startServiceTime"))
        if arr and svc:
            total += max(0.0, (svc - arr).total_seconds())
    return total


def wait_from_api(shift: dict) -> float:
    """totalWaitingTime from shift.metrics in seconds."""
    metrics = shift.get("metrics") or {}
    raw = metrics.get("totalWaitingTime")
    return parse_duration_seconds(raw) if raw else 0.0


def wait_from_itinerary_excl_break(shift: dict) -> float:
    """
    Wait = sum over VISIT of (startServiceTime - arrivalTime), but subtract any overlap
    with BREAK intervals. So if employee arrives, then has a break, then service starts,
    only the wait after the break counts (matches API totalWaitingTime).
    """
    itinerary = shift.get("itinerary") or []
    breaks = []
    for item in itinerary:
        if not isinstance(item, dict) or item.get("kind") != "BREAK":
            continue
        st = parse_iso_dt(item.get("startTime"))
        et = parse_iso_dt(item.get("endTime"))
        if st and et:
            breaks.append((st, et))

    total = 0.0
    for item in itinerary:
        if not isinstance(item, dict) or item.get("kind") != "VISIT":
            continue
        arr = parse_iso_dt(item.get("arrivalTime"))
        svc = parse_iso_dt(item.get("startServiceTime"))
        if not arr or not svc:
            continue
        wait_sec = max(0.0, (svc - arr).total_seconds())
        # Subtract overlap with any break
        for b_start, b_end in breaks:
            overlap_start = max(arr, b_start)
            overlap_end = min(svc, b_end)
            if overlap_end > overlap_start:
                wait_sec -= (overlap_end - overlap_start).total_seconds()
        total += max(0.0, wait_sec)
    return total


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python investigate_wait_diff.py <output.json>", file=sys.stderr)
        return 1
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Not found: {path}", file=sys.stderr)
        return 1

    with open(path) as f:
        data = json.load(f)
    mo = data.get("modelOutput") or data.get("model_output") or {}
    vehicles = mo.get("vehicles") or []

    total_itinerary_sec = 0.0
    total_itinerary_excl_break_sec = 0.0
    total_api_sec = 0.0
    shifts_with_diff = []
    max_diff_sec = 0.0

    for v in vehicles:
        for s in v.get("shifts") or []:
            if not any(
                isinstance(i, dict) and i.get("kind") == "VISIT"
                for i in s.get("itinerary") or []
            ):
                continue
            w_it = wait_from_itinerary(s)
            w_it_excl = wait_from_itinerary_excl_break(s)
            w_api = wait_from_api(s)
            total_itinerary_sec += w_it
            total_itinerary_excl_break_sec += w_it_excl
            total_api_sec += w_api
            diff = w_it - w_api
            if abs(diff) > 1.0:  # more than 1 second
                shifts_with_diff.append({
                    "vehicle": v.get("id"),
                    "shift_id": s.get("id"),
                    "itinerary_sec": w_it,
                    "api_sec": w_api,
                    "diff_sec": diff,
                })
                max_diff_sec = max(max_diff_sec, abs(diff))

    total_itinerary_h = total_itinerary_sec / 3600
    total_itinerary_excl_break_h = total_itinerary_excl_break_sec / 3600
    total_api_h = total_api_sec / 3600
    diff_h = total_itinerary_h - total_api_h

    print("=" * 60)
    print("Wait time: itinerary vs API totalWaitingTime")
    print("=" * 60)
    print(f"  Wait from itinerary (raw startServiceTime - arrivalTime):    {total_itinerary_h:.2f} h  ({total_itinerary_sec:.0f} s)")
    print(f"  Wait from itinerary (excl. overlap with BREAK):              {total_itinerary_excl_break_h:.2f} h  ({total_itinerary_excl_break_sec:.0f} s)")
    print(f"  Wait from API (sum of metrics.totalWaitingTime):             {total_api_h:.2f} h  ({total_api_sec:.0f} s)")
    print(f"  Difference (raw itinerary - API):  {diff_h:.2f} h  ({total_itinerary_sec - total_api_sec:.0f} s)")
    diff_excl = total_itinerary_excl_break_sec - total_api_sec
    print(f"  Difference (itinerary excl break - API):  {diff_excl/3600:.2f} h  ({diff_excl:.0f} s)")
    print()
    print(f"  Shifts with difference > 1 s:  {len(shifts_with_diff)}")
    if shifts_with_diff:
        print(f"  Max per-shift |diff|:  {max_diff_sec / 60:.1f} min")
        print()
        # Show a few examples where itinerary > API (itinerary overcount?)
        over = [x for x in shifts_with_diff if x["diff_sec"] > 60]
        under = [x for x in shifts_with_diff if x["diff_sec"] < -60]
        if over:
            print("  Sample shifts where itinerary wait > API (first 5):")
            for x in sorted(over, key=lambda t: -t["diff_sec"])[:5]:
                print(f"    {x['vehicle']} / {x['shift_id']}: itinerary {x['itinerary_sec']/60:.1f} min, API {x['api_sec']/60:.1f} min, diff +{x['diff_sec']/60:.1f} min")
        if under:
            print("  Sample shifts where itinerary wait < API (first 5):")
            for x in sorted(under, key=lambda t: t["diff_sec"])[:5]:
                print(f"    {x['vehicle']} / {x['shift_id']}: itinerary {x['itinerary_sec']/60:.1f} min, API {x['api_sec']/60:.1f} min, diff {x['diff_sec']/60:.1f} min")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
