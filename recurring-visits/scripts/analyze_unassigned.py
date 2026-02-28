#!/usr/bin/env python3
"""
Analyze unassigned visits: classify as supply issue (add shifts) vs config issue (tune solver).

Supply = no shift in input overlaps the visit time window → add more shifts for that day/period.
Config = at least one shift overlaps (e.g. empty shift) but solver did not assign → reduce travel
weight, distribute movable visits to day/evening, or tune solver.

Goal: Get visit:travel ratio as high as possible first (config), then add placeholder shifts
only for the required visit+travel demand.

Usage:
  python analyze_unassigned.py solve/input.json solve/output.json
  python analyze_unassigned.py solve/input.json solve/output.json --csv unassigned.csv
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Reuse pattern from metrics.py for travel/visit from output
import re

def parse_iso_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def parse_duration_seconds(iso: str) -> float:
    """Parse ISO 8601 duration (PT1H30M, PT10M) to seconds."""
    if not iso or not iso.startswith("PT"):
        return 0.0
    total = 0.0
    for m in re.finditer(r"(\d+(?:\.\d+)?)([HMS])", iso):
        val, unit = float(m.group(1)), m.group(2)
        total += val * (3600 if unit == "H" else 60 if unit == "M" else 1)
    return total


def overlap(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end


def _shift_type(start: datetime, end: datetime) -> str:
    """Classify as 'day' or 'evening' by shift end. Day typically ends by 15:30, evening from 16:00."""
    # Use end time: if shift ends by 15:30 treat as day; else evening
    end_h = end.hour + end.minute / 60.0
    if end_h <= 15.5:
        return "day"
    return "evening"


def _visit_window_type(tw_start: datetime, tw_end: datetime) -> str:
    """Classify visit window as day, evening, or both."""
    start_h = tw_start.hour + tw_start.minute / 60.0
    end_h = tw_end.hour + tw_end.minute / 60.0
    if end_h <= 15.5:
        return "day"
    if start_h >= 15.0:
        return "evening"
    return "both"


def run_analysis(mi: dict, mo: dict) -> tuple[str, list[dict]]:
    """
    Run unassigned analysis on already-loaded input/output model data.
    Returns (report_text, rows_for_csv).
    """
    unassigned_ids = set(str(u) for u in (mo.get("unassignedVisits") or []))

    # Build shift windows from input: (shift_id, vehicle_id, start, end)
    # From output: which shifts are empty (no visits)
    output_shift_visit_count: dict[str, int] = {}
    for v in mo.get("vehicles", []):
        for s in v.get("shifts", []):
            sid = s.get("id", "")
            it = s.get("itinerary") or []
            output_shift_visit_count[sid] = sum(
                1 for x in it if isinstance(x, dict) and x.get("kind") == "VISIT"
            )

    shifts: list[tuple[str, str, datetime, datetime, bool]] = []
    for v in mi.get("vehicles", []):
        vid = v.get("id", "?")
        for s in v.get("shifts", []):
            sid = s.get("id", "")
            st = parse_iso_dt(s.get("minStartTime"))
            et = parse_iso_dt(s.get("maxEndTime"))
            if st and et:
                is_empty = output_shift_visit_count.get(sid, 0) == 0
                shifts.append((sid, vid, st, et, is_empty))

    # Unassigned visit id -> list of (tw_start, tw_end)
    def get_tws(visit: dict) -> list[tuple[datetime, datetime]]:
        result = []
        for tw in visit.get("timeWindows", []):
            mn = parse_iso_dt(tw.get("minStartTime"))
            mx = parse_iso_dt(tw.get("maxEndTime"))
            if mn and mx:
                result.append((mn, mx))
        return result

    unassigned_windows: list[tuple[str, datetime, datetime]] = []
    for v in mi.get("visits", []):
        uid = str(v.get("id", "?"))
        if uid in unassigned_ids:
            for mn, mx in get_tws(v):
                unassigned_windows.append((uid, mn, mx))
    for g in mi.get("visitGroups", []):
        for v in g.get("visits", []):
            uid = str(v.get("id", "?"))
            if uid in unassigned_ids:
                for mn, mx in get_tws(v):
                    unassigned_windows.append((uid, mn, mx))

    # Classify each unassigned (per window): supply vs config
    # supply = no shift overlaps this window
    # config = at least one shift overlaps (empty or not)
    supply_count = 0
    config_count = 0
    by_date: dict[str, dict[str, int]] = defaultdict(lambda: {"supply": 0, "config": 0, "day": 0, "evening": 0, "both": 0})
    rows_for_csv: list[dict] = []

    for uid, tw_s, tw_e in unassigned_windows:
        overlapping = [
            (sid, vid, st, et, is_empty)
            for sid, vid, st, et, is_empty in shifts
            if overlap(st, et, tw_s, tw_e)
        ]
        if not overlapping:
            supply_count += 1
            kind = "supply"
        else:
            config_count += 1
            kind = "config"
        date_key = tw_s.date().isoformat()
        by_date[date_key]["supply" if kind == "supply" else "config"] += 1
        bucket = _visit_window_type(tw_s, tw_e)
        by_date[date_key][bucket] += 1
        rows_for_csv.append({
            "visit_id": uid,
            "tw_start": tw_s.isoformat(),
            "tw_end": tw_e.isoformat(),
            "date": date_key,
            "demand_bucket": bucket,
            "issue": kind,
            "overlapping_empty_shifts": sum(1 for _, _, _, _, empty in overlapping if empty),
            "overlapping_shifts": len(overlapping),
        })

    # Visit:travel ratio from output (assigned shifts only)
    total_visit_sec = 0.0
    total_travel_sec = 0.0
    for v in mo.get("vehicles", []):
        for s in v.get("shifts", []):
            it = s.get("itinerary") or []
            metrics = s.get("metrics") or {}
            visit_sec = 0.0
            for item in it:
                if isinstance(item, dict) and item.get("kind") == "VISIT":
                    dur = item.get("effectiveServiceDuration")
                    if dur:
                        visit_sec += parse_duration_seconds(dur)
            travel_sec = parse_duration_seconds(metrics.get("totalTravelTime") or "PT0S")
            total_visit_sec += visit_sec
            total_travel_sec += travel_sec
    field_sec = total_visit_sec + total_travel_sec
    visit_travel_ratio = (total_visit_sec / total_travel_sec) if total_travel_sec > 0 else (total_visit_sec or 0.0)
    field_eff_pct = (total_visit_sec / field_sec * 100) if field_sec > 0 else 0.0

    lines = [
        "=" * 60,
        "Unassigned visits analysis",
        "=" * 60,
        f"Unassigned visits (unique): {len(unassigned_ids)}",
        f"Unassigned time-window slots: {len(unassigned_windows)}",
        "",
        "--- Classification (per time-window slot) ---",
        f"  Supply (no overlapping shift):     {supply_count}  → add shifts for that day/period",
        f"  Config (≥1 overlapping shift):    {config_count}  → tune solver (travel, movable distribution)",
        "",
        "--- By date (demand bucket: day / evening / both) ---",
    ]
    for d in sorted(by_date.keys()):
        rec = by_date[d]
        lines.append(f"  {d}: supply={rec['supply']} config={rec['config']}  day={rec['day']} evening={rec['evening']} both={rec['both']}")
    lines.extend([
        "",
        "--- Visit:travel (assigned shifts only) ---",
        f"  Visit time:   {total_visit_sec / 3600:.2f} h",
        f"  Travel time:  {total_travel_sec / 3600:.2f} h",
        f"  Visit:travel ratio:  {visit_travel_ratio:.2f}",
        f"  Field efficiency:   {field_eff_pct:.1f}%  (target >67.5%)",
        "",
        "Next steps:",
    ])
    if supply_count > 0:
        lines.append("  - Add placeholder shifts for dates/periods with supply issues (day or evening).")
    if config_count > 0:
        lines.append("  - Tune Timefold config: reduce travel weight, prefer movable to day/evening for better routing.")
    lines.append("  - Aim for highest visit:travel ratio first, then add shifts only for required visit+travel.")
    lines.append("=" * 60)
    return "\n".join(lines), rows_for_csv


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Analyze unassigned visits: supply vs config, and visit:travel ratio.",
    )
    ap.add_argument("input", type=Path, help="Timefold input JSON.")
    ap.add_argument("output", type=Path, help="Timefold output JSON.")
    ap.add_argument("--csv", type=Path, default=None, help="Optional: write unassigned rows to CSV.")
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

    report, rows_for_csv = run_analysis(mi, mo)
    print(report)

    if args.csv and rows_for_csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with open(args.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows_for_csv[0].keys()))
            w.writeheader()
            w.writerows(rows_for_csv)
        print(f"Wrote {args.csv}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
