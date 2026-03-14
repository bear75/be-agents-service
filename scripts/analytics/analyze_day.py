#!/usr/bin/env python3
"""
Print one day from a Timefold FSR output: shifts on that day with itinerary
(visits, travel, break), client assignment (visit id → from input if available),
and per-shift totals so you can verify against metrics.

Usage:
  python3 analyze_day.py <output.json> [--input <input.json>] [--day 2026-02-16]
"""

import argparse
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

def parse_duration_seconds(iso: str) -> float:
    if not iso or not iso.startswith("PT"):
        return 0.0
    total = 0.0
    for m in re.finditer(r"(\d+(?:\.\d+)?)([HMS])", iso):
        val, unit = float(m.group(1)), m.group(2)
        total += val * (3600 if unit == "H" else 60 if unit == "M" else 1)
    return total

def parse_iso_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None

def fmt_hm(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    return f"{h}h{m:02d}"

def main():
    ap = argparse.ArgumentParser(description="Analyze one day: shifts, visits, travel, clients")
    ap.add_argument("output", type=Path, help="Timefold output JSON")
    ap.add_argument("--input", type=Path, default=None, help="Input JSON (for scheduled times + visit names)")
    ap.add_argument("--day", default="2026-02-16", help="Date (YYYY-MM-DD)")
    args = ap.parse_args()

    with open(args.output) as f:
        data = json.load(f)
    mo = data.get("modelOutput") or data.get("model_output") or {}
    vehicles = mo.get("vehicles") or []

    # Build visit id -> name and shift id -> scheduled seconds from input
    visit_to_name: dict[str, str] = {}
    shift_scheduled_sec: dict[str, float] = {}
    if args.input and args.input.exists():
        with open(args.input) as f:
            inp = json.load(f)
        mi = inp.get("modelInput") or inp
        for v in mi.get("visits", []):
            vid = str(v.get("id", ""))
            visit_to_name[vid] = v.get("name") or vid
        for g in mi.get("visitGroups", []):
            for v in g.get("visits", []):
                vid = str(v.get("id", ""))
                visit_to_name[vid] = v.get("name") or vid
        for veh in mi.get("vehicles", []):
            for s in veh.get("shifts", []):
                sid = s.get("id", "")
                st = parse_iso_dt(s.get("minStartTime"))
                et = parse_iso_dt(s.get("maxEndTime"))
                if st and et:
                    shift_scheduled_sec[sid] = (et - st).total_seconds()

    day_prefix = args.day  # e.g. 2026-02-16
    shift_count = 0
    day_visit_sec = 0.0
    day_travel_sec = 0.0
    day_wait_sec = 0.0
    day_break_sec = 0.0
    day_shift_sec = 0.0

    lines = []
    lines.append("=" * 80)
    lines.append(f"DAY: {day_prefix} — Shifts, visits, travel, break, idle (client = visit name from input)")
    lines.append("=" * 80)

    for v in vehicles:
        vid = v.get("id", "?")
        for s in v.get("shifts") or []:
            start_s = s.get("startTime") or ""
            if not start_s.startswith(day_prefix):
                continue
            shift_count += 1
            sid = s.get("id", "?")
            metrics_block = s.get("metrics") or {}
            itinerary = s.get("itinerary") or []

            visit_sec = parse_duration_seconds(metrics_block.get("totalServiceDuration") or "PT0S")
            travel_sec = parse_duration_seconds(metrics_block.get("totalTravelTime") or "PT0S")
            wait_sec = parse_duration_seconds(metrics_block.get("totalWaitingTime") or "PT0S")
            break_sec = parse_duration_seconds(metrics_block.get("totalBreakDuration") or "PT0S")
            scheduled_sec = shift_scheduled_sec.get(sid, 8 * 3600.0)
            idle_sec = max(0.0, scheduled_sec - visit_sec - travel_sec - wait_sec - break_sec)

            day_visit_sec += visit_sec
            day_travel_sec += travel_sec
            day_wait_sec += wait_sec
            day_break_sec += break_sec
            day_shift_sec += scheduled_sec

            lines.append("")
            lines.append(f"--- {vid} / shift {sid}   scheduled {fmt_hm(scheduled_sec)} ---")
            lines.append(f"  Visit: {fmt_hm(visit_sec)}  Travel: {fmt_hm(travel_sec)}  Wait: {fmt_hm(wait_sec)}  Break: {fmt_hm(break_sec)}  Idle: {fmt_hm(idle_sec)}  (sum check: {fmt_hm(visit_sec+travel_sec+wait_sec+break_sec+idle_sec)})")
            lines.append("  Itinerary:")

            for i, item in enumerate(itinerary):
                if not isinstance(item, dict):
                    continue
                kind = item.get("kind", "")
                if kind == "VISIT":
                    visit_id = str(item.get("id", ""))
                    name = visit_to_name.get(visit_id) or visit_id
                    arr = item.get("arrivalTime") or ""
                    svc = item.get("startServiceTime") or ""
                    dep = item.get("departureTime") or ""
                    dur_iso = item.get("effectiveServiceDuration") or "PT0S"
                    trav_iso = item.get("travelTimeFromPreviousStandstill") or "PT0S"
                    dur_sec = parse_duration_seconds(dur_iso)
                    trav_sec = parse_duration_seconds(trav_iso)
                    # Wait = svc - arr
                    dt_arr = parse_iso_dt(arr)
                    dt_svc = parse_iso_dt(svc)
                    wait_this = (dt_svc - dt_arr).total_seconds() if dt_arr and dt_svc else 0
                    lines.append(f"    VISIT {visit_id} (client: {name})  arr={arr[11:19] if len(arr)>=19 else arr}  start={svc[11:19] if len(svc)>=19 else svc}  dep={dep[11:19] if len(dep)>=19 else dep}  duration={fmt_hm(dur_sec)}  travel_prev={fmt_hm(trav_sec)}  wait={wait_this:.0f}s")
                elif kind == "BREAK":
                    st = item.get("startTime") or ""
                    et = item.get("endTime") or ""
                    lines.append(f"    BREAK  {st[11:19] if len(st)>=19 else st} – {et[11:19] if len(et)>=19 else et}")

    day_idle_sec = day_shift_sec - day_visit_sec - day_travel_sec - day_wait_sec - day_break_sec
    day_idle_sec = max(0.0, day_idle_sec)

    lines.append("")
    lines.append("--- Day totals ---")
    lines.append(f"  Shifts on {day_prefix}: {shift_count}")
    lines.append(f"  Shift time (scheduled 8h each): {fmt_hm(day_shift_sec)}")
    lines.append(f"  Visit: {fmt_hm(day_visit_sec)}  Travel: {fmt_hm(day_travel_sec)}  Wait: {fmt_hm(day_wait_sec)}  Break: {fmt_hm(day_break_sec)}  Idle: {fmt_hm(day_idle_sec)}")
    lines.append("=" * 80)

    text = "\n".join(lines)
    print(text)
    return 0

if __name__ == "__main__":
    exit(main())
