#!/usr/bin/env python3
"""
Generate an Attendo-style pilot report (HTML) comparing baseline vs optimized FSR metrics.

Reads:
  - Baseline metrics JSON (e.g. run with idle / "manual" slinga)
  - Optimized metrics JSON (e.g. from-patch trimmed, no idle)
  - Optional: FSR output JSON for optimized run (for sample day Gantt + visit-detail table)

Output:
  - Single HTML file styled like Attendo_Schedule_Pilot_Report.pdf, suitable for printing to PDF.

Usage:
  python generate_pilot_report.py \\
    --baseline-metrics path/to/metrics_*_c87d58dd.json \\
    --optimized-metrics path/to/metrics_*_fa713a0d.json \\
    --output path/to/report.html \\
    [--optimized-output path/to/export-*-fa713a0d-*-output.json] \\
    [--title "Huddinge Hemtjänst — Recurring Visits"] \\
    [--window "2-Week Window"]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


# Exact metrics from Attendo_Schedule_Pilot_Report.pdf (Huddinge 2-week pilot)
ATTENDO_PDF_VALUES = {
    "eff_incl_manual": 60.6,
    "eff_incl_caire": 85.4,
    "eff_incl_delta": "+24.8pp",
    "eff_excl_manual": 67.8,
    "eff_excl_caire": 85.7,
    "eff_excl_delta": "+17.9pp",
    "travel_manual": 24.0,
    "travel_caire": 9.8,
    "travel_delta": "-14.2pp",
    "idle_manual": 12.9,
    "idle_caire": 0.0,
    "idle_delta": "-12.9pp",
    "margin_manual": 31.0,
    "margin_caire": 51.0,
    "margin_delta": "+20.0pp",
    "shift_hours_saved_int": 726,
    "margin_uplift_kr": 166_617,
    "cost_saved_kr": 167_011,
    "visits_manual": 3622,
    "visits_caire": 3620,
    "shifts_manual": 340,
    "shifts_caire": 271,
    "shift_time_manual_h": 2502,
    "shift_time_caire_h": 1776,
    "visit_time_manual_h": 1517,
    "visit_time_caire_h": 1516,
    "travel_time_manual_h": 600,
    "travel_time_caire_h": 174,
    "break_time_manual_h": 121,
    "break_time_caire_h": 80,
    "idle_time_manual_h": 322,
    "idle_time_caire_h": 0,
    "wait_time_caire_h": 6,
    "visit_revenue_manual_kr": 834_350,
    "visit_revenue_caire_kr": 833_956,
    "shift_cost_manual_kr": 575_460,
    "shift_cost_caire_kr": 408_449,
    "margin_manual_kr": 258_890,
    "margin_caire_kr": 425_507,
    "footer_visits": 3622,
    "footer_slingas": 39,
    "footer_clients": 81,
    "footer_text": "2-Week Window · 3,622 Visits · 39 Slingas · 81 Clients · All metrics on 2-week basis · Feb 2026",
}


def load_metrics(path: Path) -> dict:
    """Load metrics from a JSON file produced by fsr_metrics.py (or compatible)."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    # Normalize keys used by both fsr_metrics output and our report
    shift_h = data.get("shift_time_h") or 0
    visit_h = data.get("visit_time_h") or 0
    travel_h = data.get("travel_time_h") or 0
    wait_h = data.get("wait_time_h") or 0
    break_h = data.get("break_time_h") or 0
    idle_h = data.get("inactive_time_h") or 0
    paid_h = shift_h - break_h  # shift − break for efficiency denominator
    assignable_h = visit_h + travel_h + wait_h + break_h
    eff_incl = (visit_h / shift_h * 100) if shift_h else 0
    eff_excl = (visit_h / (visit_h + travel_h + wait_h + break_h) * 100) if (visit_h + travel_h + wait_h + break_h) else 0
    travel_pct = (travel_h / shift_h * 100) if shift_h else 0
    idle_pct = (idle_h / shift_h * 100) if shift_h else 0
    cost_kr = data.get("shift_cost_kr") or 0
    revenue_kr = data.get("visit_revenue_kr") or 0
    margin_kr = data.get("margin_kr") or (revenue_kr - cost_kr)
    margin_pct = (margin_kr / revenue_kr * 100) if revenue_kr else 0
    return {
        "route_plan_id": data.get("route_plan_id") or "unknown",
        "shift_time_h": shift_h,
        "visit_time_h": visit_h,
        "travel_time_h": travel_h,
        "wait_time_h": wait_h,
        "break_time_h": break_h,
        "inactive_time_h": idle_h,
        "paid_time_h": paid_h,
        "efficiency_incl_idle_pct": round(eff_incl, 1),
        "efficiency_excl_idle_pct": round(eff_excl, 1),
        "travel_pct": round(travel_pct, 1),
        "idle_pct": round(idle_pct, 1),
        "wait_pct": round((wait_h / shift_h * 100) if shift_h else 0, 1),
        "break_pct": round((break_h / shift_h * 100) if shift_h else 0, 1),
        "shift_cost_kr": cost_kr,
        "visit_revenue_kr": revenue_kr,
        "margin_kr": margin_kr,
        "margin_pct": round(margin_pct, 1),
        "cost_per_hour_kr": data.get("cost_per_hour_kr") or 230,
        "revenue_per_visit_hour_kr": data.get("revenue_per_visit_hour_kr") or 550,
        "total_shifts": data.get("total_shifts") or 0,
        "total_vehicles": data.get("total_vehicles") or 0,
        "total_visits_assigned": data.get("total_visits_assigned") or 0,
        "unassigned_visits": data.get("unassigned_visits") or 0,
        "input_summary": data.get("input_summary") or {},
        "score": data.get("score") or "",
    }


def h_min(h: float) -> str:
    """Format hours as 'Xh Ymin'."""
    hi = int(h)
    mi = int((h - hi) * 60 + 0.5)
    return f"{hi}h {mi}min"


def fmt_pct(pct: float) -> str:
    return f"{pct:.1f}%"


def delta_pp(manual: float, caire: float) -> str:
    d = caire - manual
    return f"{d:+.1f}pp" if d >= 0 else f"{d:.1f}pp"


def build_comparison(baseline: dict, optimized: dict) -> dict:
    """Compute comparison deltas and derived text."""
    def d_pp(m: float, c: float) -> str:
        return f"{c - m:+.1f}pp" if c >= m else f"{c - m:.1f}pp"

    shift_saved = baseline["shift_time_h"] - optimized["shift_time_h"]
    cost_saved = baseline["shift_cost_kr"] - optimized["shift_cost_kr"]
    margin_abs = optimized["margin_kr"] - baseline["margin_kr"]

    return {
        "eff_excl_manual": baseline["efficiency_excl_idle_pct"],
        "eff_excl_caire": optimized["efficiency_excl_idle_pct"],
        "eff_excl_delta": d_pp(baseline["efficiency_excl_idle_pct"], optimized["efficiency_excl_idle_pct"]),
        "eff_incl_manual": baseline["efficiency_incl_idle_pct"],
        "eff_incl_caire": optimized["efficiency_incl_idle_pct"],
        "eff_incl_delta": d_pp(baseline["efficiency_incl_idle_pct"], optimized["efficiency_incl_idle_pct"]),
        "travel_manual": baseline["travel_pct"],
        "travel_caire": optimized["travel_pct"],
        "travel_delta": d_pp(baseline["travel_pct"], optimized["travel_pct"]),
        "idle_manual": baseline["idle_pct"],
        "idle_caire": optimized["idle_pct"],
        "idle_delta": d_pp(baseline["idle_pct"], optimized["idle_pct"]),
        "margin_manual": baseline["margin_pct"],
        "margin_caire": optimized["margin_pct"],
        "margin_delta": d_pp(baseline["margin_pct"], optimized["margin_pct"]),
        "shift_hours_saved": round(shift_saved, 1),
        "shift_hours_saved_int": int(round(shift_saved, 0)),
        "cost_saved_kr": cost_saved,
        "margin_uplift_kr": margin_abs,
        "visits_manual": baseline["total_visits_assigned"],
        "visits_caire": optimized["total_visits_assigned"],
        "shifts_manual": baseline["total_shifts"],
        "shifts_caire": optimized["total_shifts"],
    }


def parse_duration(s: str) -> float:
    """Parse ISO8601 duration to seconds."""
    if not s or s == "PT0S":
        return 0.0
    total = 0.0
    if m := re.search(r"(\d+)H", s):
        total += int(m.group(1)) * 3600
    if m := re.search(r"(\d+)M", s):
        total += int(m.group(1)) * 60
    if m := re.search(r"(\d+)S", s):
        total += int(m.group(1))
    return total


def extract_sample_day_and_shift(output_path: Path):
    """
    From FSR output JSON, extract:
    - day_summary: first date that has shifts, with list of shifts and visit counts + time summary
    - sample_shift: first shift of that day with full itinerary for visit-detail table
    """
    with open(output_path, encoding="utf-8") as f:
        data = json.load(f)
    vehicles = (data.get("modelOutput") or {}).get("vehicles") or []
    # Collect all shifts with date
    shifts_by_date = {}
    for v in vehicles:
        vid = v.get("id") or ""
        for shift in v.get("shifts") or []:
            start = shift.get("startTime")
            if not start:
                continue
            # "2026-02-24T07:00:00+01:00" -> date key 2026-02-24
            date_key = start[:10]
            if date_key not in shifts_by_date:
                shifts_by_date[date_key] = []
            itinerary = shift.get("itinerary") or []
            visit_count = sum(1 for it in itinerary if (it.get("kind") or "").upper() == "VISIT")
            metrics = shift.get("metrics") or {}
            total_svc = parse_duration(metrics.get("totalServiceDuration") or "PT0S")
            total_travel = parse_duration(metrics.get("totalTravelTime") or "PT0S")
            total_wait = parse_duration(metrics.get("totalWaitingTime") or "PT0S")
            total_break = parse_duration(metrics.get("totalBreakDuration") or "PT0S")
            shifts_by_date[date_key].append({
                "vehicle_id": vid,
                "shift_id": shift.get("id") or "",
                "start_time": start,
                "visit_count": visit_count,
                "visit_h": total_svc / 3600,
                "travel_h": total_travel / 3600,
                "wait_h": total_wait / 3600,
                "break_h": total_break / 3600,
                "itinerary": itinerary,
            })
    if not shifts_by_date:
        return None, None
    first_date = sorted(shifts_by_date.keys())[0]
    day_shifts = shifts_by_date[first_date]
    # Day summary
    total_visits = sum(s["visit_count"] for s in day_shifts)
    total_visit_h = sum(s["visit_h"] for s in day_shifts)
    total_travel_h = sum(s["travel_h"] for s in day_shifts)
    total_wait_h = sum(s["wait_h"] for s in day_shifts)
    total_break_h = sum(s["break_h"] for s in day_shifts)
    total_shift_h = total_visit_h + total_travel_h + total_wait_h + total_break_h
    # Format date for display
    try:
        dt = datetime.strptime(first_date, "%Y-%m-%d")
        date_display = dt.strftime("%A %d %B %Y")
    except Exception:
        date_display = first_date
    day_summary = {
        "date": first_date,
        "date_display": date_display,
        "shifts": day_shifts,
        "n_shifts": len(day_shifts),
        "n_visits": total_visits,
        "visit_h": total_visit_h,
        "travel_h": total_travel_h,
        "wait_h": total_wait_h,
        "shift_h": total_shift_h,
    }
    # Sample shift: first shift with multiple visits
    sample_shift = None
    for s in day_shifts:
        if s["visit_count"] >= 3:
            sample_shift = s
            break
    if not sample_shift and day_shifts:
        sample_shift = day_shifts[0]
    return day_summary, sample_shift


def extract_locations_from_fsr_input(input_path: Path) -> list[tuple[float, float]]:
    """
    Extract unique visit and depot locations from FSR input JSON for map display.
    Returns list of (lat, lon). Deduplicates by rounding to 5 decimals (same address).
    """
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)
    model = data.get("modelInput") or data
    seen: set[tuple[float, float]] = set()
    out: list[tuple[float, float]] = []

    def add(lat: float, lon: float) -> None:
        key = (round(lat, 5), round(lon, 5))
        if key not in seen:
            seen.add(key)
            out.append((lat, lon))

    for v in model.get("visits") or []:
        loc = v.get("location")
        if isinstance(loc, (list, tuple)) and len(loc) >= 2:
            try:
                add(float(loc[0]), float(loc[1]))
            except (TypeError, ValueError):
                pass
    for veh in model.get("vehicles") or []:
        for shift in veh.get("shifts") or []:
            loc = shift.get("startLocation")
            if isinstance(loc, (list, tuple)) and len(loc) >= 2:
                try:
                    add(float(loc[0]), float(loc[1]))
                except (TypeError, ValueError):
                    pass
    return out


def extract_full_schedule(output_path: Path) -> list[dict]:
    """
    Extract all shifts from FSR output with start/end times and assigned visits.
    Returns a list of dicts: date, date_display, vehicle_id, start, end, visit_count, visits (list of {id, start, end}).
    """
    with open(output_path, encoding="utf-8") as f:
        data = json.load(f)
    vehicles = (data.get("modelOutput") or {}).get("vehicles") or []
    rows = []
    for v in vehicles:
        vid = v.get("id") or ""
        for shift in v.get("shifts") or []:
            start = shift.get("startTime")
            if not start:
                continue
            date_key = start[:10]
            try:
                dt = datetime.strptime(date_key, "%Y-%m-%d")
                date_display = dt.strftime("%a %d %b")
            except Exception:
                date_display = date_key
            itinerary = shift.get("itinerary") or []
            metrics = shift.get("metrics") or {}
            end_s = metrics.get("endLocationArrivalTime")
            if not end_s and itinerary:
                last = itinerary[-1]
                if (last.get("kind") or "").upper() == "VISIT":
                    end_s = last.get("departureTime")
                elif (last.get("kind") or "").upper() == "BREAK":
                    end_s = last.get("endTime")
            visits = []
            for it in itinerary:
                kind = (it.get("kind") or "").upper()
                if kind == "VISIT":
                    dep = it.get("departureTime") or ""
                    start_svc = it.get("startServiceTime") or it.get("arrivalTime") or ""
                    vid_visit = it.get("id") or ""
                    visits.append({
                        "id": vid_visit,
                        "start": format_time_iso(start_svc),
                        "end": format_time_iso(dep),
                    })
            rows.append({
                "date": date_key,
                "date_display": date_display,
                "vehicle_id": vid,
                "shift_id": shift.get("id") or "",
                "start": start,
                "end": end_s or "",
                "start_display": format_time_iso(start),
                "end_display": format_time_iso(end_s) if end_s else "—",
                "visit_count": len(visits),
                "visits": visits,
            })
    return sorted(rows, key=lambda r: (r["date"], r["start"], r["vehicle_id"]))


def iso_time_to_minutes(iso_str: str) -> int:
    """Convert ISO datetime string to minutes since midnight (0-1439)."""
    if not iso_str or "T" not in iso_str:
        return 0
    time_part = iso_str.split("T")[1]
    h = 0
    m = 0
    if len(time_part) >= 2:
        h = int(time_part[:2])
    if len(time_part) >= 5:
        m = int(time_part[3:5])
    return h * 60 + m


def extract_timeline_by_day(output_path: Path) -> list[dict]:
    """
    Extract per-day timeline: shifts with events (visit/break) as start_min, end_min since midnight.
    Returns list of { date, date_display, shifts: [ { vehicle_id, events: [ { start_min, end_min, label, kind } ] } ] }.
    """
    with open(output_path, encoding="utf-8") as f:
        data = json.load(f)
    vehicles = (data.get("modelOutput") or {}).get("vehicles") or []
    by_date: dict[str, list[dict]] = {}
    for v in vehicles:
        vid = v.get("id") or ""
        for shift in v.get("shifts") or []:
            start_iso = shift.get("startTime")
            if not start_iso:
                continue
            date_key = start_iso[:10]
            try:
                dt = datetime.strptime(date_key, "%Y-%m-%d")
                date_display = dt.strftime("%A %d %B %Y")
            except Exception:
                date_display = date_key
            itinerary = shift.get("itinerary") or []
            events = []
            for it in itinerary:
                kind = (it.get("kind") or "").upper()
                if kind == "VISIT":
                    start_svc = it.get("startServiceTime") or it.get("arrivalTime") or ""
                    dep = it.get("departureTime") or ""
                    vid_visit = it.get("id") or ""
                    start_min = iso_time_to_minutes(start_svc)
                    end_min = iso_time_to_minutes(dep)
                    if dep and start_svc:
                        events.append({
                            "start_min": start_min,
                            "end_min": end_min,
                            "label": str(vid_visit),
                            "kind": "visit",
                        })
                elif kind == "BREAK":
                    start_b = it.get("startTime") or ""
                    end_b = it.get("endTime") or ""
                    start_min = iso_time_to_minutes(start_b)
                    end_min = iso_time_to_minutes(end_b)
                    if end_b and start_b:
                        events.append({
                            "start_min": start_min,
                            "end_min": end_min,
                            "label": "Break",
                            "kind": "break",
                        })
            if date_key not in by_date:
                by_date[date_key] = []
            by_date[date_key].append({
                "vehicle_id": vid,
                "events": events,
            })
    out = []
    for date_key in sorted(by_date.keys()):
        try:
            dt = datetime.strptime(date_key, "%Y-%m-%d")
            date_display = dt.strftime("%A %d %B %Y")
        except Exception:
            date_display = date_key
        out.append({
            "date": date_key,
            "date_display": date_display,
            "shifts": by_date[date_key],
        })
    return out


def format_time_iso(t: str) -> str:
    """Format ISO time as HH:MM for display."""
    if not t or "T" not in t:
        return t
    part = t.split("T")[1][:5]
    return part.replace(":", ":")


def render_visit_row(item: dict, idx: int) -> dict:
    """Build one visit row for the detail table."""
    kind = (item.get("kind") or "").upper()
    if kind == "BREAK":
        start = item.get("startTime") or ""
        end = item.get("endTime") or ""
        return {
            "num": idx,
            "type": "Break",
            "arrival": format_time_iso(start),
            "start": format_time_iso(start),
            "depart": format_time_iso(end),
            "duration": "30m" if start and end else "—",
            "travel": "—",
            "dist": "—",
            "wait": "—",
            "pinned": False,
        }
    arr = item.get("arrivalTime") or ""
    start_svc = item.get("startServiceTime") or arr
    dep = item.get("departureTime") or ""
    dur = item.get("effectiveServiceDuration") or "PT0S"
    travel = item.get("travelTimeFromPreviousStandstill") or "PT0S"
    dist_m = item.get("travelDistanceMetersFromPreviousStandstill") or 0
    # Parse duration for display
    dur_sec = parse_duration(dur)
    dur_str = f"{int(dur_sec // 60)}m" if dur_sec else "—"
    travel_sec = parse_duration(travel)
    travel_str = f"{int(travel_sec // 60)}m {int(travel_sec % 60)}s" if travel_sec else "—"
    dist_km = dist_m / 1000
    dist_str = f"{dist_km:.1f}km" if dist_m else "—"
    wait_sec = 0
    if arr and start_svc:
        from datetime import datetime, timezone
        try:
            dt_a = datetime.fromisoformat(arr.replace("Z", "+00:00"))
            dt_s = datetime.fromisoformat(start_svc.replace("Z", "+00:00"))
            if dt_s.tzinfo and dt_a.tzinfo:
                wait_sec = (dt_s - dt_a).total_seconds()
        except Exception:
            pass
    wait_str = f"{int(wait_sec)}m" if wait_sec > 0 else "—"
    return {
        "num": idx,
        "type": "Visit" + (" (pinned)" if item.get("pinned") else ""),
        "arrival": format_time_iso(arr),
        "start": format_time_iso(start_svc),
        "depart": format_time_iso(dep),
        "duration": dur_str,
        "travel": travel_str,
        "dist": dist_str,
        "wait": wait_str,
        "pinned": bool(item.get("pinned")),
    }


def html_report(
    baseline: dict,
    optimized: dict,
    comparison: dict,
    title: str,
    window: str,
    day_summary=None,
    sample_shift=None,
    n_days: int | None = None,
    n_clients: int | None = None,
    full_schedule: list | None = None,
    timeline_by_day: list | None = None,
    use_attendo_values: bool = False,
    locations: list[tuple[float, float]] | None = None,
) -> str:
    """Generate full HTML report in Attendo style."""
    b, c, d = baseline, optimized, dict(comparison)
    cost_kr = c.get("cost_per_hour_kr") or 230
    rev_kr = c.get("revenue_per_visit_hour_kr") or 550
    n_employees = c.get("total_vehicles") or 0

    # Optional: use exact metrics from Attendo_Schedule_Pilot_Report.pdf
    if use_attendo_values:
        apv = ATTENDO_PDF_VALUES
        override_keys = [
            "eff_incl_manual", "eff_incl_caire", "eff_incl_delta",
            "eff_excl_manual", "eff_excl_caire", "eff_excl_delta",
            "travel_manual", "travel_caire", "travel_delta",
            "idle_manual", "idle_caire", "idle_delta",
            "margin_manual", "margin_caire", "margin_delta",
            "shift_hours_saved_int", "cost_saved_kr", "margin_uplift_kr",
            "visits_manual", "visits_caire", "shifts_manual", "shifts_caire",
        ]
        for k in override_keys:
            if k in apv:
                d[k] = apv[k]
        footer_line = apv["footer_text"]
        n_employees = apv["footer_slingas"]
        # Time breakdown from PDF (hours and %)
        def row(cat: str, m_h: float, m_pct: float, caire_h: float, caire_pct: float, delta: str = ""):
            delta_cell = f'<span class="td-delta-improvement">{delta}</span>' if delta and delta != "—" else (delta or "—")
            return f'<tr><td>{cat}</td><td>{h_min(m_h)}</td><td>{fmt_pct(m_pct)}</td><td>{h_min(caire_h)}</td><td>{fmt_pct(caire_pct)}</td><td>{delta_cell}</td></tr>'
        rows = [
            row("Total Shift", apv["shift_time_manual_h"], 100, apv["shift_time_caire_h"], 100, "—"),
            row("Visit Time", apv["visit_time_manual_h"], apv["eff_incl_manual"], apv["visit_time_caire_h"], apv["eff_incl_caire"], apv["eff_incl_delta"]),
            row("Travel Time", apv["travel_time_manual_h"], apv["travel_manual"], apv["travel_time_caire_h"], apv["travel_caire"], apv["travel_delta"]),
            row("Wait Time", 0, 0, apv.get("wait_time_caire_h", 0), 0.3, "—"),
            row("Break Time", apv["break_time_manual_h"], 4.8, apv["break_time_caire_h"], 4.5, "—"),
            row("Idle Time", apv["idle_time_manual_h"], apv["idle_manual"], apv["idle_time_caire_h"], apv["idle_caire"], apv["idle_delta"]),
        ]
        # Override b/c for revenue table and insights
        b = {**b, "shift_time_h": apv["shift_time_manual_h"], "visit_time_h": apv["visit_time_manual_h"], "inactive_time_h": apv["idle_time_manual_h"], "visit_revenue_kr": apv["visit_revenue_manual_kr"], "shift_cost_kr": apv["shift_cost_manual_kr"], "margin_kr": apv["margin_manual_kr"]}
        c = {**c, "shift_time_h": apv["shift_time_caire_h"], "visit_time_h": apv["visit_time_caire_h"], "inactive_time_h": apv["idle_time_caire_h"], "visit_revenue_kr": apv["visit_revenue_caire_kr"], "shift_cost_kr": apv["shift_cost_caire_kr"], "margin_kr": apv["margin_caire_kr"], "total_shifts": apv["shifts_caire"], "total_visits_assigned": apv["visits_caire"]}
        dataset_visits = apv["footer_visits"]
        dataset_shifts = apv["shifts_caire"]
        dataset_clients = apv["footer_clients"]
    else:
        footer_line = f"{window} · {c['total_visits_assigned']} Visits · {c['total_shifts']} Shifts · All metrics on same period · {datetime.now().strftime('%b %Y')}"
        dataset_visits = c["total_visits_assigned"]
        dataset_shifts = c["total_shifts"]
        dataset_clients = n_clients if n_clients is not None else "—"

    # Build time breakdown rows (only when not using Attendo values)
    if not use_attendo_values:
        def row(cat: str, m_h: float, m_pct: float, caire_h: float, caire_pct: float, delta: str = ""):
            delta_cell = f'<span class="td-delta-improvement">{delta}</span>' if delta and delta != "—" else (delta or "—")
            return f'<tr><td>{cat}</td><td>{h_min(m_h)}</td><td>{fmt_pct(m_pct)}</td><td>{h_min(caire_h)}</td><td>{fmt_pct(caire_pct)}</td><td>{delta_cell}</td></tr>'
        rows = [
            row("Total Shift", b["shift_time_h"], b["shift_time_h"] / b["shift_time_h"] * 100 if b["shift_time_h"] else 0, c["shift_time_h"], c["shift_time_h"] / c["shift_time_h"] * 100 if c["shift_time_h"] else 0, "—"),
            row("Visit Time", b["visit_time_h"], b["efficiency_excl_idle_pct"], c["visit_time_h"], c["efficiency_excl_idle_pct"], d["eff_excl_delta"]),
            row("Travel Time", b["travel_time_h"], b["travel_pct"], c["travel_time_h"], c["travel_pct"], d["travel_delta"]),
            row("Wait Time", 0, 0, c["wait_time_h"], c["wait_pct"], "—" if c["wait_time_h"] < 0.01 else "—"),
            row("Break Time", b["break_time_h"], b["break_pct"], c["break_time_h"], c["break_pct"], "—"),
            row("Idle Time", b["inactive_time_h"], b["idle_pct"], c["inactive_time_h"], c["idle_pct"], d["idle_delta"]),
        ]

    # Visit detail table from sample shift
    visit_detail_rows = ""
    if sample_shift and sample_shift.get("itinerary"):
        detail_rows = []
        for i, it in enumerate(sample_shift["itinerary"], 1):
            r = render_visit_row(it, i)
            detail_rows.append(
                f'<tr><td>{r["num"]}</td><td>{r["type"]}</td><td>{r["arrival"]}</td><td>{r["start"]}</td><td>{r["depart"]}</td><td>{r["duration"]}</td><td>{r["travel"]}</td><td>{r["dist"]}</td><td>{r["wait"]}</td></tr>'
            )
        visit_detail_rows = "\n".join(detail_rows)
        sample_vehicle = sample_shift.get("vehicle_id", "")
        sample_visits = sample_shift.get("visit_count", 0)
        visit_time_min = int(sample_shift.get("visit_h", 0) * 60)
        travel_min = int(sample_shift.get("travel_h", 0) * 60)
        wait_min = int(sample_shift.get("wait_h", 0) * 60)
    else:
        sample_vehicle = ""
        sample_visits = 0
        visit_time_min = 0
        travel_min = 0
        wait_min = 0

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Pilot Report</title>
<style>
:root {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14px; color: #1a1a1a; }}
body {{ max-width: 900px; margin: 0 auto; padding: 24px; background: #fff; }}
h1 {{ font-size: 1.75rem; font-weight: 700; margin: 0 0 0.25rem 0; }}
h2 {{ font-size: 1.25rem; font-weight: 600; margin: 1.5rem 0 0.75rem 0; border-bottom: 1px solid #e5e7eb; padding-bottom: 0.25rem; }}
h3 {{ font-size: 1.1rem; font-weight: 600; margin: 1rem 0 0.5rem 0; }}
p {{ margin: 0.5rem 0; line-height: 1.5; }}
.report-header {{ text-align: center; margin-bottom: 2rem; }}
.report-header .brand {{ font-size: 0.9rem; color: #6b7280; letter-spacing: 0.05em; }}
.report-header .subtitle {{ font-size: 0.85rem; color: #9ca3af; margin-top: 0.5rem; }}
.metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 1.5rem 0; }}
.metric-card {{ border: 1px solid #e5e7eb; border-radius: 8px; padding: 1rem; text-align: center; background: #fafafa; }}
.metric-card .label {{ font-size: 0.8rem; color: #6b7280; margin-bottom: 0.35rem; font-weight: 500; }}
.metric-card .manual {{ font-size: 1rem; color: #6b7280; }}
.metric-card .caire {{ font-size: 1.35rem; font-weight: 700; color: #1e40af; }}
.metric-card .delta {{ font-size: 0.95rem; font-weight: 600; margin-top: 0.35rem; }}
.metric-card .delta.delta-improvement {{ color: #047857; }}
.metric-card .delta.delta-worse {{ color: #b91c1c; }}
table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.9rem; }}
th, td {{ border: 1px solid #e5e7eb; padding: 0.5rem 0.75rem; text-align: left; }}
th {{ background: #f3f4f6; font-weight: 600; color: #374151; }}
tr:nth-child(even) {{ background: #fafafa; }}
.td-delta-improvement {{ color: #047857; font-weight: 600; }}
.td-delta-worse {{ color: #b91c1c; font-weight: 600; }}
.page-break {{ page-break-before: always; }}
.insight-list {{ margin: 1rem 0; padding-left: 1.25rem; }}
.insight-list li {{ margin: 0.5rem 0; }}
.footer-note {{ font-size: 0.8rem; color: #6b7280; margin-top: 2rem; }}
.schedule-visits {{ font-size: 0.8rem; line-height: 1.3; max-width: 320px; }}
.timeline-day {{ margin-bottom: 2rem; }}
.timeline-day h3 {{ margin-top: 1rem; }}
.timeline-axis {{ display: flex; align-items: stretch; margin-bottom: 2px; font-size: 0.7rem; color: #6b7280; }}
.timeline-axis-spacer {{ width: 98px; flex-shrink: 0; }}
.timeline-axis-hours {{ flex: 1; display: flex; justify-content: space-between; padding: 0 2px; min-width: 0; }}
.timeline-row {{ display: flex; align-items: stretch; margin-bottom: 4px; min-height: 28px; }}
.timeline-row-label {{ width: 98px; flex-shrink: 0; font-size: 0.75rem; padding: 2px 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.timeline-lane {{ flex: 1; position: relative; height: 24px; background: #f5f5f5; border-radius: 2px; min-width: 0; }}
.timeline-event {{ position: absolute; top: 1px; bottom: 1px; border-radius: 2px; font-size: 0.65rem; overflow: hidden; text-align: center; line-height: 22px; white-space: nowrap; }}
.timeline-event.visit {{ background: #059669; color: #fff; }}
.timeline-event.break {{ background: #64748b; color: #fff; }}
.report-map {{ width: 100%; height: 500px; margin: 1rem 0; border: 1px solid #e5e7eb; border-radius: 8px; }}
</style>
</head>
<body>
<div class="report-header">
  <div class="brand">caire × Attendo</div>
  <h1>Attendo Schedule Pilot</h1>
  <p class="subtitle">{title}</p>
  <p class="subtitle">Powered by caire and EirTech</p>
  <p class="subtitle">bjorn@caire.se · caire.se · eirtech.ai</p>
</div>

<h2>Manual vs Caire — Key Results</h2>
<div class="metrics-grid">
  <div class="metric-card">
    <div class="label">Eff. (incl idle)</div>
    <div class="manual">{d["eff_incl_manual"]}% Manual</div>
    <div class="caire">{d["eff_incl_caire"]}% Caire</div>
    <div class="delta delta-improvement">{d["eff_incl_delta"]}</div>
  </div>
  <div class="metric-card">
    <div class="label">Eff. (excl idle)</div>
    <div class="manual">{d["eff_excl_manual"]}% Manual</div>
    <div class="caire">{d["eff_excl_caire"]}% Caire</div>
    <div class="delta delta-improvement">{d["eff_excl_delta"]}</div>
  </div>
  <div class="metric-card">
    <div class="label">Travel</div>
    <div class="manual">{d["travel_manual"]}% Manual</div>
    <div class="caire">{d["travel_caire"]}% Caire</div>
    <div class="delta delta-improvement">{d["travel_delta"]}</div>
  </div>
  <div class="metric-card">
    <div class="label">Margin</div>
    <div class="manual">{d["margin_manual"]}% Manual</div>
    <div class="caire">{d["margin_caire"]}% Caire</div>
    <div class="delta delta-improvement">{d["margin_delta"]}</div>
  </div>
</div>
<p class="footer-note">{footer_line}</p>

<h3>Dataset summary</h3>
<table>
<thead><tr><th>Metric</th><th>Value</th></tr></thead>
<tbody>
<tr><td>Employees (vehicles / slingor)</td><td>{n_employees}</td></tr>
<tr><td>Shifts</td><td>{dataset_shifts}</td></tr>
<tr><td>Visits (assigned)</td><td>{dataset_visits}</td></tr>
<tr><td>Clients</td><td>{dataset_clients}</td></tr>
<tr><td>Planning window (days)</td><td>{n_days if n_days is not None else "—"}</td></tr>
</tbody>
</table>
"""
    html += f"""
<div class="page-break"></div>
<h2>Manual vs Caire — Dashboard</h2>
<p>Side-by-side comparison of baseline (manual-style) vs Caire-optimized scheduling.</p>
<table>
<thead><tr><th>Metric</th><th>Manual</th><th>Caire</th><th>∆</th></tr></thead>
<tbody>
<tr><td>Eff. (incl idle)</td><td>{d["eff_incl_manual"]}%</td><td>{d["eff_incl_caire"]}%</td><td class="td-delta-improvement">{d["eff_incl_delta"]}</td></tr>
<tr><td>Eff. (excl idle)</td><td>{d["eff_excl_manual"]}%</td><td>{d["eff_excl_caire"]}%</td><td class="td-delta-improvement">{d["eff_excl_delta"]}</td></tr>
<tr><td>Travel</td><td>{d["travel_manual"]}%</td><td>{d["travel_caire"]}%</td><td class="td-delta-improvement">{d["travel_delta"]}</td></tr>
<tr><td>Idle Time</td><td>{d["idle_manual"]}%</td><td>{d["idle_caire"]}%</td><td class="td-delta-improvement">{d["idle_delta"]}</td></tr>
<tr><td>Margin</td><td>{d["margin_manual"]}%</td><td>{d["margin_caire"]}%</td><td class="td-delta-improvement">{d["margin_delta"]}</td></tr>
</tbody>
</table>

<h3>Time Breakdown (hours)</h3>
<table>
<thead><tr><th>Category</th><th>Manual (h)</th><th>Manual %</th><th>Caire (h)</th><th>Caire %</th><th>∆</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody>
</table>

<h3>Revenue & Cost Analysis</h3>
<p>Assumptions: Employee cost {cost_kr} kr/h, visit revenue {rev_kr} kr/h. Pure field routing ROI.</p>
<table>
<thead><tr><th></th><th>Manual</th><th>Caire</th><th>Difference</th></tr></thead>
<tbody>
<tr><td>Visits</td><td>{d["visits_manual"]}</td><td>{d["visits_caire"]}</td><td>{d["visits_caire"] - d["visits_manual"]}</td></tr>
<tr><td>Shifts</td><td>{d["shifts_manual"]}</td><td>{d["shifts_caire"]}</td><td>{d["shifts_caire"] - d["shifts_manual"]}</td></tr>
<tr><td>Visit Hours</td><td>{h_min(b["visit_time_h"])}</td><td>{h_min(c["visit_time_h"])}</td><td>—</td></tr>
<tr><td>Shift Hours</td><td>{h_min(b["shift_time_h"])}</td><td>{h_min(c["shift_time_h"])}</td><td class="td-delta-improvement">-{d["shift_hours_saved_int"]} h</td></tr>
<tr><td>Revenue</td><td>{b["visit_revenue_kr"]:,} kr</td><td>{c["visit_revenue_kr"]:,} kr</td><td>{c["visit_revenue_kr"] - b["visit_revenue_kr"]:,} kr</td></tr>
<tr><td>Staffing Cost</td><td>-{b["shift_cost_kr"]:,} kr</td><td>-{c["shift_cost_kr"]:,} kr</td><td class="td-delta-improvement">+{d["cost_saved_kr"]:,} kr saved</td></tr>
<tr><td>Margin</td><td>{b["margin_kr"]:,} kr</td><td>{c["margin_kr"]:,} kr</td><td class="td-delta-improvement">+{d["margin_uplift_kr"]:,} kr</td></tr>
<tr><td>Margin %</td><td>{d["margin_manual"]}%</td><td>{d["margin_caire"]}%</td><td class="td-delta-improvement">{d["margin_delta"]}</td></tr>
</tbody>
</table>

<h2>Key Insights</h2>
<ol class="insight-list">
<li><strong>Idle:</strong> Manual {d["idle_manual"]}% idle ({h_min(b["inactive_time_h"])}) vs Caire {d["idle_caire"]}%. Solver compressed shift windows.</li>
<li><strong>Efficiency:</strong> Increased from {d["eff_excl_manual"]}% to {d["eff_excl_caire"]}%. More visit time per paid hour.</li>
<li><strong>Margin Uplift:</strong> +{d["margin_uplift_kr"]:,} kr — {d["shift_hours_saved_int"]} fewer shift hours at {cost_kr} kr/h.</li>
<li><strong>Travel:</strong> Baseline {d["travel_manual"]}% travel vs Caire {d["travel_caire"]}% — geographic clustering and route optimization.</li>
</ol>
"""
    if timeline_by_day:
        DAY_START_MIN = 6 * 60   # 06:00
        DAY_END_MIN = 22 * 60    # 22:00
        DAY_LEN_MIN = DAY_END_MIN - DAY_START_MIN
        hour_labels = list(range(6, 23))  # 6 to 22
        for day in timeline_by_day:
            html += f'''
<div class="page-break"></div>
<h2>Timeline — {day["date_display"]}</h2>
<div class="timeline-day">
  <div class="timeline-axis">
    <div class="timeline-axis-spacer"></div>
    <div class="timeline-axis-hours">
      {"".join(f'<span>{h}:00</span>' for h in hour_labels)}
    </div>
  </div>
'''
            for shift in day["shifts"]:
                events_html = []
                for ev in shift["events"]:
                    start_min = max(ev["start_min"], DAY_START_MIN)
                    end_min = min(ev["end_min"], DAY_END_MIN)
                    if start_min >= end_min:
                        continue
                    left_pct = (start_min - DAY_START_MIN) / DAY_LEN_MIN * 100
                    width_pct = (end_min - start_min) / DAY_LEN_MIN * 100
                    if width_pct < 2:
                        width_pct = 2
                    events_html.append(
                        f'<div class="timeline-event {ev["kind"]}" style="left:{left_pct:.2f}%;width:{width_pct:.2f}%" title="{ev["label"]}">{ev["label"]}</div>'
                    )
                lane_html = "\n    ".join(events_html) if events_html else ""
                html += f'  <div class="timeline-row"><div class="timeline-row-label" title="{shift["vehicle_id"]}">{shift["vehicle_id"]}</div><div class="timeline-lane">{lane_html}</div></div>\n'
            html += "</div>\n"

    # Map section: after calendar (timeline), before schedule table
    if locations:
        locations_json = json.dumps([[lat, lon] for lat, lon in locations])
        html += f"""
<div class="page-break"></div>
<h2>Map — All locations</h2>
<p>Visit and depot locations from the schedule (unique addresses).</p>
<div id="report-map" class="report-map"></div>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<script>
(function() {{
  var locations = {locations_json};
  if (locations.length === 0) return;
  var map = L.map('report-map').setView([locations[0][0], locations[0][1]], 12);
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{ attribution: '© OpenStreetMap' }}).addTo(map);
  var bounds = L.latLngBounds(locations.map(function(p) {{ return [p[0], p[1]]; }}));
  for (var i = 0; i < locations.length; i++) {{
    L.circleMarker([locations[i][0], locations[i][1]], {{ radius: 6, fillColor: '#1e40af', color: '#1e3a8a', weight: 1, opacity: 1, fillOpacity: 0.7 }}).addTo(map);
  }}
  map.fitBounds(bounds, {{ padding: [30, 30] }});
}})();
</script>
"""

    if full_schedule:
        schedule_rows_html = []
        for s in full_schedule:
            visits_cell = ""
            if s.get("visits"):
                parts = [f'{v["id"]} {v["start"]}–{v["end"]}' for v in s["visits"]]
                visits_cell = '<span class="schedule-visits">' + ", ".join(parts) + "</span>"
            else:
                visits_cell = "—"
            schedule_rows_html.append(
                f'<tr><td>{s["date_display"]}</td><td>{s["vehicle_id"]}</td><td>{s["start_display"]}</td><td>{s["end_display"]}</td><td>{s["visit_count"]}</td><td>{visits_cell}</td></tr>'
            )
        html += """
<div class="page-break"></div>
<h2>Schedule view — all shifts</h2>
<p>All shifts with start/end times and assigned visits (visit id and time window).</p>
<table>
<thead><tr><th>Date</th><th>Shift</th><th>Start</th><th>End</th><th>Visits</th><th>Assigned visits</th></tr></thead>
<tbody>
"""
        html += "\n".join(schedule_rows_html)
        html += "\n</tbody></table>\n"

    if day_summary and sample_shift:
        html += f"""
<div class="page-break"></div>
<h2>Caire Schedule — {day_summary["date_display"]}</h2>
<p>Summary of {day_summary["n_shifts"]} shifts, {day_summary["n_visits"]} visits. Total visit time {day_summary["visit_h"]:.1f}h, travel {day_summary["travel_h"]:.1f}h.</p>
<table>
<thead><tr><th>Shift</th><th>Visits</th><th>Visit h</th><th>Travel h</th><th>Wait h</th><th>Shift h</th></tr></thead>
<tbody>
"""
        for s in day_summary["shifts"][:25]:
            shift_h = s["visit_h"] + s["travel_h"] + s["wait_h"] + s["break_h"]
            html += f'<tr><td>{s["vehicle_id"]}</td><td>{s["visit_count"]}</td><td>{s["visit_h"]:.2f}</td><td>{s["travel_h"]:.2f}</td><td>{s["wait_h"]:.2f}</td><td>{shift_h:.2f}</td></tr>\n'
        html += "</tbody></table>\n"

    if visit_detail_rows:
        html += f"""
<div class="page-break"></div>
<h2>Visit Details — Sample Shift</h2>
<p>Detailed itinerary for <strong>{sample_vehicle}</strong> on {day_summary["date_display"] if day_summary else ""} — {sample_visits} visits, visit time {visit_time_min} min, travel {travel_min} min, wait {wait_min} min.</p>
<table>
<thead><tr><th>#</th><th>Type</th><th>Arrival</th><th>Start</th><th>Depart</th><th>Duration</th><th>Travel</th><th>Dist.</th><th>Wait</th></tr></thead>
<tbody>
{visit_detail_rows}
</tbody>
</table>
<p class="footer-note">Pinned visits are locked to this vehicle. Wait time appears when the solver respects earliest-start constraints.</p>
"""

    html += """
</body>
</html>
"""
    return html


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Attendo-style pilot report (HTML) from baseline vs optimized FSR metrics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--baseline-metrics", type=Path, required=True, help="Path to baseline (manual) metrics JSON")
    parser.add_argument("--optimized-metrics", type=Path, required=True, help="Path to optimized (Caire) metrics JSON")
    parser.add_argument("--output", "-o", type=Path, required=True, help="Output HTML report path")
    parser.add_argument("--optimized-output", type=Path, default=None, help="Optional: FSR output JSON for sample day + visit detail")
    parser.add_argument("--title", type=str, default="Huddinge Hemtjänst — Recurring Visits", help="Report subtitle/title")
    parser.add_argument("--window", type=str, default="2-Week Window", help="Window description for footer")
    parser.add_argument("--days", type=int, default=None, help="Planning window in days (e.g. 14 for 2 weeks)")
    parser.add_argument("--clients", type=int, default=None, help="Number of unique clients (if known)")
    parser.add_argument("--use-attendo-values", action="store_true", help="Use exact metrics and footer from Attendo_Schedule_Pilot_Report.pdf")
    parser.add_argument("--fsr-input", type=Path, default=None, help="Optional: FSR input JSON to show map of all visit/depot locations")
    args = parser.parse_args()

    if not args.baseline_metrics.exists():
        print(f"Error: baseline metrics not found: {args.baseline_metrics}", file=sys.stderr)
        return 1
    if not args.optimized_metrics.exists():
        print(f"Error: optimized metrics not found: {args.optimized_metrics}", file=sys.stderr)
        return 1

    baseline = load_metrics(args.baseline_metrics)
    optimized = load_metrics(args.optimized_metrics)
    comparison = build_comparison(baseline, optimized)

    day_summary = None
    sample_shift = None
    full_schedule = []
    timeline_by_day = []
    if args.optimized_output and args.optimized_output.exists():
        day_summary, sample_shift = extract_sample_day_and_shift(args.optimized_output)
        full_schedule = extract_full_schedule(args.optimized_output)
        timeline_by_day = extract_timeline_by_day(args.optimized_output)

    locations = None
    if args.fsr_input and args.fsr_input.exists():
        try:
            locations = extract_locations_from_fsr_input(args.fsr_input)
        except Exception as e:
            print(f"Warning: could not load locations from FSR input: {e}", file=sys.stderr)

    html = html_report(
        baseline=baseline,
        optimized=optimized,
        comparison=comparison,
        title=args.title,
        window=args.window,
        day_summary=day_summary,
        sample_shift=sample_shift,
        n_days=args.days,
        n_clients=args.clients,
        full_schedule=full_schedule,
        timeline_by_day=timeline_by_day,
        use_attendo_values=args.use_attendo_values,
        locations=locations,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
