#!/usr/bin/env python3
"""
Measure efficiency, cost, and revenue metrics for a Timefold FSR output JSON.

Key metrics:
  - Shift time excl. breaks = paid salary time (what we pay for).
  - Visit time = value (care delivery; revenue).
  - Travel and wait = costs to minimize (paid but non-productive).

Time equation (must hold): shift = visit + travel + wait + break + idle

Every second is exactly one of: visit, travel, wait, break, or idle (mutually exclusive, sum to shift).
  - Visit time:    employee is performing a visit (billable)
  - Travel time:   employee is driving between locations (from shift.metrics.totalTravelTime) — minimize
  - Wait time:     employee arrived early, waiting for time window — minimize.
                   API totalWaitingTime excludes overlap with break (so wait is the lower figure; no double-count with break).
  - Break time:    scheduled break
  - Inactive time: shift is scheduled but employee has no work
                   (tail gap after last visit return, or entire empty shift)
                   Computed as: shift - visit - travel - wait - break

Efficiency:
  - Staffing = visit / (shift - break)  [visit share of paid time]
  - Field = visit / (visit + travel)  [target >67.5% vs Slingor manual benchmark]
  - Field (incl. wait) = visit / (visit + travel + wait)

Cost = shift_hours × 230 kr/h (paid salary); Revenue = visit_hours × 550 kr/h

Sanity check: warns if (visit+travel+wait+break+idle) differs from shift by >2%.
See docs/PRIORITIES.md for metrics accuracy details.

Usage:
  python metrics.py ../tf/output.json --input ../tf/input.json
  python metrics.py ../tf/output.json --input ../tf/input.json --save ../tf/metrics/
  python metrics.py ../tf/output.json --input ../tf/input.json --exclude-inactive
  python metrics.py ../tf/output.json --input ../tf/input.json --exclude-empty-shifts-only   # variant 1: endast helt tomma skift borttagna
  python metrics.py ../tf/output.json --input ../tf/input.json --visit-span-only             # variant 2: + tomma delar i skift borttagna (visit-span)
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ─── Constants ────────────────────────────────────────────────────────────────
COST_PER_HOUR = 230.0   # kr/h — employee cost (175 kr/h + 30% social fees, incl breaks)
REVENUE_PER_VISIT_HOUR = 550.0  # kr/h — revenue per visiting hour


# ─── Parsing helpers ──────────────────────────────────────────────────────────

def parse_duration_seconds(iso: str) -> float:
    """Parse ISO 8601 duration (PT1H30M, PT10M, PT7M48S) to seconds."""
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


# ─── Input analysis ───────────────────────────────────────────────────────────

def build_scheduled_shift_map(input_data: dict) -> dict[str, float]:
    """From input JSON, build shift_id → scheduled_duration_seconds."""
    mi = input_data.get("modelInput") or input_data
    result: dict[str, float] = {}
    for v in mi.get("vehicles", []):
        for s in v.get("shifts", []):
            sid = s.get("id", "")
            st = parse_iso_dt(s.get("minStartTime"))
            et = parse_iso_dt(s.get("maxEndTime"))
            if st and et:
                result[sid] = max(0.0, (et - st).total_seconds())
    return result


def analyze_input(path: Path | None) -> dict | None:
    """Analyze input JSON for summary info."""
    if not path or not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    mi = data.get("modelInput") or data
    vehicles = mi.get("vehicles", [])
    visits = mi.get("visits", [])
    visit_groups = mi.get("visitGroups", [])
    shifts = sum(len(v.get("shifts", [])) for v in vehicles)
    fc = hr = 0
    for v in vehicles:
        for s in v.get("shifts", []):
            c = s.get("cost", {})
            if c.get("fixedCost", 0) > 0:
                fc += 1
            elif c.get("rates"):
                hr += 1
    group_visit_count = sum(len(g.get("visits", [])) for g in visit_groups)
    total_tf_visits = len(visits) + group_visit_count
    # Care visits = unique care moments (each visitGroup = 1 care visit, not 2)
    care_visits = len(visits) + len(visit_groups)
    # Time window slots = total week-occurrences across all visits
    tw_slots = sum(len(v.get("timeWindows", [])) for v in visits)
    tw_slots += sum(len(v.get("timeWindows", [])) for g in visit_groups for v in g.get("visits", []))
    return {
        "visits": len(visits),
        "visit_groups": len(visit_groups),
        "group_visits": group_visit_count,
        "total_visits": total_tf_visits,
        "care_visits": care_visits,
        "time_window_slots": tw_slots,
        "vehicles": len(vehicles),
        "shifts": shifts,
        "shifts_fixed_cost": fc,
        "shifts_hourly": hr,
    }


# ─── Per-shift metrics ───────────────────────────────────────────────────────

def _visit_span_seconds(shift: dict) -> tuple[float, float]:
    """
    For a shift with at least one VISIT, return (span_sec, break_inside_span_sec).
    Span = first visit start -> last visit end (e.g. 7–10 if last visit ends at 10).
    Break inside span = break time that overlaps that window (breaks in idle part are excluded).
    Returns (0, 0) if no visits.
    """
    itinerary = shift.get("itinerary") or []
    visit_items = [it for it in itinerary if isinstance(it, dict) and it.get("kind") == "VISIT"]
    if not visit_items:
        return 0.0, 0.0

    # Use actual first/last by time (minStartTravelTime can be global 00:00, not shift start)
    def _visit_start(it: dict):
        return parse_iso_dt(it.get("arrivalTime") or it.get("startServiceTime"))

    def _visit_end(it: dict):
        et = parse_iso_dt(it.get("startServiceTime") or it.get("arrivalTime"))
        dur = parse_duration_seconds(it.get("effectiveServiceDuration") or "PT0S")
        if et and dur >= 0:
            return et + timedelta(seconds=dur)
        return parse_iso_dt(it.get("departureTime") or it.get("startServiceTime"))

    first_start = _visit_start(visit_items[0])
    if not first_start:
        return 0.0, 0.0
    # Chronological first/last by actual times (itinerary may not be sorted)
    starts = [_visit_start(it) for it in visit_items]
    ends = [_visit_end(it) for it in visit_items]
    first_start = min((t for t in starts if t), default=first_start)
    last_end = max((t for t in ends if t), default=None)
    if not last_end:
        last_end = _visit_end(visit_items[-1])

    span_sec = max(0.0, (last_end - first_start).total_seconds())

    break_inside = 0.0
    for item in itinerary:
        if not isinstance(item, dict) or item.get("kind") != "BREAK":
            continue
        st = parse_iso_dt(item.get("startTime"))
        et = parse_iso_dt(item.get("endTime"))
        if st and et:
            overlap_start = max(st, first_start)
            overlap_end = min(et, last_end)
            if overlap_end > overlap_start:
                break_inside += (overlap_end - overlap_start).total_seconds()

    return span_sec, break_inside


def shift_metrics(
    shift: dict,
    scheduled_sec: float | None = None,
    visit_span_only: bool = False,
    exclude_empty_shifts_only: bool = False,
) -> dict:
    """Compute time and cost metrics for a single shift."""
    start_s = shift.get("startTime")
    metrics_block = shift.get("metrics") or {}
    itinerary = shift.get("itinerary") or []

    break_sec = 0.0
    visit_sec = 0.0
    wait_sec = 0.0
    visit_count = 0

    for item in itinerary:
        if not isinstance(item, dict):
            continue
        kind = item.get("kind")
        if kind == "BREAK":
            st = parse_iso_dt(item.get("startTime"))
            et = parse_iso_dt(item.get("endTime"))
            if st and et:
                break_sec += max(0.0, (et - st).total_seconds())
        elif kind == "VISIT":
            visit_count += 1
            dur = item.get("effectiveServiceDuration")
            if dur:
                visit_sec += parse_duration_seconds(dur)
            arr = parse_iso_dt(item.get("arrivalTime"))
            svc = parse_iso_dt(item.get("startServiceTime"))
            if arr and svc:
                wait_sec += max(0.0, (svc - arr).total_seconds())

    travel_sec = parse_duration_seconds(metrics_block.get("totalTravelTime") or "PT0S")

    # Prefer metrics block totals when present so shift = visit+travel+wait+break (no spurious idle).
    # Itinerary sums can diverge (e.g. effectiveServiceDuration vs totalServiceDuration rounding).
    if metrics_block.get("totalServiceDuration"):
        visit_sec = parse_duration_seconds(metrics_block["totalServiceDuration"])
    if metrics_block.get("totalWaitingTime"):
        wait_sec = parse_duration_seconds(metrics_block["totalWaitingTime"])
    if metrics_block.get("totalBreakDuration"):
        break_sec = parse_duration_seconds(metrics_block["totalBreakDuration"])

    # Shift duration
    if exclude_empty_shifts_only and visit_count == 0:
        # Variant 1: helt tomma skift bidrar inte med skifttimmar (räkna endast skift med besök).
        total_shift_sec = 0.0
        break_sec = 0.0
    elif visit_span_only:
        # Variant 2: tomma skift = 0; skift med besök = första besök start → sista besök slut (inga tomma delar).
        if visit_count == 0:
            total_shift_sec = 0.0
            break_sec = 0.0
        else:
            span_sec, break_inside_sec = _visit_span_seconds(shift)
            total_shift_sec = span_sec
            break_sec = break_inside_sec
    elif scheduled_sec is not None and scheduled_sec > 0:
        # Use SCHEDULED time from input (what we pay for)
        total_shift_sec = scheduled_sec
    elif (
        metrics_block.get("totalServiceDuration")
        and metrics_block.get("totalTravelTime")
    ):
        # From-patch / API output: shift ends at depot. Use metrics-block sum so shift = visit+travel+wait+break (no idle).
        total_shift_sec = (
            visit_sec + travel_sec + wait_sec + break_sec
        )
    else:
        # Fall back to output endLocationArrivalTime
        end_s = metrics_block.get("endLocationArrivalTime")
        if not end_s:
            last_dep = None
            for item in reversed(itinerary):
                if isinstance(item, dict) and item.get("departureTime"):
                    last_dep = item["departureTime"]
                    break
            if last_dep:
                last_leg = parse_duration_seconds(
                    metrics_block.get("travelTimeFromLastVisitToEndLocation") or "PT0S"
                )
                dt = parse_iso_dt(last_dep)
                if dt and last_leg > 0:
                    end_s = (dt + timedelta(seconds=last_leg)).isoformat()
                else:
                    end_s = last_dep
        dt_start = parse_iso_dt(start_s)
        dt_end = parse_iso_dt(end_s)
        total_shift_sec = max(0.0, (dt_end - dt_start).total_seconds()) if dt_start and dt_end else 0.0

    # Inactive = shift time not accounted for by visit + travel + wait + break
    # This is the tail gap (employee back at depot before shift ends) + any gaps
    inactive_sec = max(0.0, total_shift_sec - visit_sec - travel_sec - wait_sec - break_sec)

    productive_sec = max(0.0, total_shift_sec - break_sec - inactive_sec)
    eff = (visit_sec / (total_shift_sec - break_sec) * 100) if (total_shift_sec - break_sec) > 0 else 0.0

    # Costs
    shift_cost = total_shift_sec / 3600 * COST_PER_HOUR
    visit_revenue = visit_sec / 3600 * REVENUE_PER_VISIT_HOUR

    return {
        "shift_id": shift.get("id", "?"),
        "visit_count": visit_count,
        "shift_sec": total_shift_sec,
        "break_sec": break_sec,
        "visit_sec": visit_sec,
        "travel_sec": travel_sec,
        "wait_sec": wait_sec,
        "inactive_sec": inactive_sec,
        "efficiency_pct": eff,
        "shift_cost_kr": shift_cost,
        "visit_revenue_kr": visit_revenue,
    }


# ─── Aggregation ──────────────────────────────────────────────────────────────

def aggregate(
    output_data: dict,
    input_data: dict | None = None,
    use_depot_end: bool = False,
    visit_span_only: bool = False,
    exclude_empty_shifts_only: bool = False,
) -> dict:
    """Aggregate metrics across all shifts.

    exclude_empty_shifts_only (variant 1): Empty shifts and empty employees contribute 0 shift hours;
    non-empty shifts use scheduled length. Idle = only end-of-shift idle in shifts that have visits.
    visit_span_only (variant 2): Empty shifts = 0; non-empty shift time = first visit start -> last visit end;
    no end-of-shift idle, no breaks after last visit. Idle = 0.
    When use_depot_end is True (e.g. for trimmed or from-patch output), shift duration
    is taken from the output so that shift = visit + travel + wait + break (idle = 0).
    Otherwise, when input_data is provided, scheduled shift length from input is used.
    """
    mo = output_data.get("modelOutput") or output_data.get("model_output") or {}
    vehicles = mo.get("vehicles") or []
    unassigned = mo.get("unassignedVisits") or []

    scheduled_map: dict[str, float] = {}
    if input_data and not use_depot_end:
        scheduled_map = build_scheduled_shift_map(input_data)

    totals = {
        "shift_sec": 0.0, "break_sec": 0.0,
        "visit_sec": 0.0, "travel_sec": 0.0, "wait_sec": 0.0, "inactive_sec": 0.0,
        "shift_cost_kr": 0.0, "visit_revenue_kr": 0.0,
    }
    total_visits = 0
    shift_count = 0
    shifts_with_visits = 0
    shifts_no_visits = 0
    empty_vehicle_ids: list[str] = []
    per_shift: list[dict] = []

    for v in vehicles:
        v_has_visits = False
        for s in v.get("shifts") or []:
            sid = s.get("id", "")
            sched = scheduled_map.get(sid) if not visit_span_only else None
            m = shift_metrics(
                s,
                scheduled_sec=sched,
                visit_span_only=visit_span_only,
                exclude_empty_shifts_only=exclude_empty_shifts_only,
            )
            per_shift.append({**m, "vehicle_id": v.get("id", "?")})
            shift_count += 1
            for k in totals:
                totals[k] += m.get(k, 0.0)
            total_visits += m["visit_count"]
            if m["visit_count"] > 0:
                shifts_with_visits += 1
                v_has_visits = True
            else:
                shifts_no_visits += 1
        if not v_has_visits:
            empty_vehicle_ids.append(v.get("id", "?"))

    paid_sec = totals["shift_sec"] - totals["break_sec"]
    active_paid_sec = paid_sec - totals["inactive_sec"]

    # Staffing (with inactive): visit / (shift - break). Inactive is IN the denominator so that
    # removing inactive (e.g. ESS) improves the %.
    staffing_eff = (totals["visit_sec"] / paid_sec * 100) if paid_sec > 0 else 0.0
    # Staffing (assignable used): visit / (shift - break - inactive). Shown when --exclude-inactive.
    staffing_assignable_eff = (totals["visit_sec"] / active_paid_sec * 100) if active_paid_sec > 0 else 0.0
    # Field efficiency: visit / (visit + travel) — share of field time (excl. wait) that is at client (~67% target)
    field_time_sec = totals["visit_sec"] + totals["travel_sec"]
    field_eff = (totals["visit_sec"] / field_time_sec * 100) if field_time_sec > 0 else 0.0
    # Field (incl. wait): visit / (visit + travel + wait) — share of paid field time that is visit (wait is paid but not visit)
    field_incl_wait_sec = totals["visit_sec"] + totals["travel_sec"] + totals["wait_sec"]
    field_incl_wait_eff = (totals["visit_sec"] / field_incl_wait_sec * 100) if field_incl_wait_sec > 0 else 0.0
    # Idle efficiency: visit / (visit + travel + idle) — same denominator concept as staffing when wait=0
    visit_plus_travel_plus_idle_sec = totals["visit_sec"] + totals["travel_sec"] + totals["inactive_sec"]
    idle_eff = (
        totals["visit_sec"] / visit_plus_travel_plus_idle_sec * 100
        if visit_plus_travel_plus_idle_sec > 0 else 0.0
    )
    # System efficiency: visit / all provisioned assignable time (incl. empty shifts) — for context only
    system_eff = (totals["visit_sec"] / paid_sec * 100) if paid_sec > 0 else 0.0

    # Margin
    margin_kr = totals["visit_revenue_kr"] - totals["shift_cost_kr"]
    margin_pct = (margin_kr / totals["visit_revenue_kr"] * 100) if totals["visit_revenue_kr"] > 0 else 0.0

    # Active-only margin (excluding inactive cost)
    active_cost_kr = (totals["shift_sec"] - totals["inactive_sec"]) / 3600 * COST_PER_HOUR
    active_margin_kr = totals["visit_revenue_kr"] - active_cost_kr
    active_margin_pct = (active_margin_kr / totals["visit_revenue_kr"] * 100) if totals["visit_revenue_kr"] > 0 else 0.0

    # Sanity check: visit + travel + wait + break + inactive should ≈ shift (within 1%)
    # When visit_span_only, shift_sec is per-shift span so sum(shift_sec) can be less than sum(visit+travel+wait+break) from metrics block; skip strict check.
    accounted = (
        totals["visit_sec"]
        + totals["travel_sec"]
        + totals["wait_sec"]
        + totals["break_sec"]
        + totals["inactive_sec"]
    )
    diff_pct = abs(accounted - totals["shift_sec"]) / totals["shift_sec"] * 100 if totals["shift_sec"] > 0 else 0
    if diff_pct > 2.0 and not visit_span_only and not exclude_empty_shifts_only:
        import warnings

        warnings.warn(
            f"Metrics sanity check: visit+travel+wait+break+idle ({accounted:.0f}s) "
            f"differs from shift ({totals['shift_sec']:.0f}s) by {diff_pct:.1f}%",
            UserWarning,
        )

    # Score from metadata
    meta = output_data.get("metadata") or output_data.get("run") or {}
    score = meta.get("score", "N/A")
    solver_status = meta.get("solverStatus", "N/A")
    route_plan_id = meta.get("id") or (output_data.get("run") or {}).get("id") or "unknown"

    out = {
        "metrics_sanity_diff_pct": diff_pct,
        "route_plan_id": route_plan_id,
        "score": score,
        "solver_status": solver_status,
        "visit_span_only": visit_span_only,
        "exclude_empty_shifts_only": exclude_empty_shifts_only,
        "total_visits_assigned": total_visits,
        "unassigned_visits": len(unassigned),
        "total_vehicles": len(vehicles),
        "empty_vehicles": len(empty_vehicle_ids),
        "empty_vehicle_ids": empty_vehicle_ids,
        "total_shifts": shift_count,
        "shifts_with_visits": shifts_with_visits,
        "shifts_no_visits": shifts_no_visits,
        # Time (hours)
        "shift_time_h": totals["shift_sec"] / 3600,
        "break_time_h": totals["break_sec"] / 3600,
        "visit_time_h": totals["visit_sec"] / 3600,
        "travel_time_h": totals["travel_sec"] / 3600,
        "wait_time_h": totals["wait_sec"] / 3600,
        "inactive_time_h": totals["inactive_sec"] / 3600,
        # Cost (kr) — all shift time is paid at COST_PER_HOUR
        "shift_cost_kr": totals["shift_cost_kr"],
        "visit_cost_kr": totals["visit_sec"] / 3600 * COST_PER_HOUR,
        "travel_cost_kr": totals["travel_sec"] / 3600 * COST_PER_HOUR,
        "wait_cost_kr": totals["wait_sec"] / 3600 * COST_PER_HOUR,
        "break_cost_kr": totals["break_sec"] / 3600 * COST_PER_HOUR,
        "inactive_cost_kr": totals["inactive_sec"] / 3600 * COST_PER_HOUR,
        # Revenue
        "visit_revenue_kr": totals["visit_revenue_kr"],
        "margin_kr": margin_kr,
        "margin_pct": margin_pct,
        # Efficiency
        "efficiency_pct": staffing_eff,
        "efficiency_assignable_used_pct": staffing_assignable_eff,
        "field_efficiency_pct": field_eff,
        "field_incl_wait_pct": field_incl_wait_eff,
        "idle_efficiency_pct": idle_eff,
        "routing_efficiency_pct": staffing_assignable_eff,
        "system_efficiency_pct": system_eff,
        # Active-only margin
        "active_cost_kr": active_cost_kr,
        "active_margin_kr": active_margin_kr,
        "active_margin_pct": active_margin_pct,
        "per_shift": per_shift,
    }
    return out


# ─── Report printing ─────────────────────────────────────────────────────────

def fmt_kr(v: float) -> str:
    """Format kr with no decimals (integer)."""
    return f"{int(round(v)):>10,}"


def fmt_pct(pct: float) -> str:
    """Format percentage with 2 decimals."""
    return f"{pct:.2f}%"


def fmt_hm(hours: float) -> str:
    """Format time as h:min (e.g. 1h 30min)."""
    total_min = int(round(hours * 60))
    h, m = total_min // 60, total_min % 60
    return f"{h}h {m}min"


def report_lines(
    agg: dict,
    input_info: dict | None = None,
    exclude_inactive: bool = False,
) -> list[str]:
    """Build the full metrics report as a list of lines (for printing or saving to file)."""
    w = 72
    lines: list[str] = []
    title = "TIMEFOLD FSR METRICS REPORT"
    if agg.get("visit_span_only"):
        title += "  (Variant 2: visit-span; tomma delar borttagna)"
    elif agg.get("exclude_empty_shifts_only"):
        title += "  (Variant 1: endast helt tomma skift borttagna)"
    elif exclude_inactive:
        title += "  (EXCLUDING INACTIVE)"
    lines.append("=" * w)
    lines.append(title)
    lines.append("=" * w)

    # Förklaring: hur idle räknas (sv)
    if agg.get("exclude_empty_shifts_only") or agg.get("visit_span_only"):
        lines.append("")
        lines.append("--- Hur idle räknas ut ---")
        if agg.get("exclude_empty_shifts_only") and not agg.get("visit_span_only"):
            lines.append("  Variant 1: Helt tomma skift och tomma medarbetare räknas inte som skifttimmar.")
            lines.append("  Skifttimmar = endast skift som har minst ett besök (enl. schema längd).")
            lines.append("  Idle = skift − (besök + resa + väntan + rast); inkl. tom tid i slutet av skift (efter sista besök).")
        elif agg.get("visit_span_only"):
            lines.append("  Variant 2: Som variant 1, plus: varje skift med besök räknas endast från första besök start")
            lines.append("  till sista besök slut (ingen tom tid efter sista besök, rast efter sista besök räknas inte).")
            lines.append("  Idle = 0 (inga helt tomma skift, inga tomma delar i skift).")
        lines.append("")

    lines.append("")
    lines.append("--- Key metrics ---")
    paid_h = agg["shift_time_h"] - agg["break_time_h"]
    lines.append(f"  Paid time (shift − break)  = {fmt_hm(paid_h)}  [salary cost]")
    lines.append(f"  Visit time (value)         = {fmt_hm(agg['visit_time_h'])}  [care delivery / revenue]")
    lines.append(f"  Travel + wait (minimize)    = {fmt_hm(agg['travel_time_h'] + agg['wait_time_h'])}  [cost to minimize]")

    sh = agg["shift_time_h"]
    vh = agg["visit_time_h"]
    th = agg["travel_time_h"]
    wh = agg["wait_time_h"]
    bh = agg["break_time_h"]
    ih = agg["inactive_time_h"]
    sum_h = vh + th + wh + bh + ih
    inactive_h = agg["inactive_time_h"]

    # ─── 1. KPI: Efficiency % (README: Staffing, Field, Wait efficiency) ───────
    lines.append("")
    lines.append("--- KPI: Efficiency % ---")
    lines.append(f"  Efficiency (visit / (shift − break))     {fmt_pct(agg['efficiency_pct'])}  [staffing]")
    lines.append(f"  Travel efficiency (visit / (visit+travel))  {fmt_pct(agg.get('field_efficiency_pct', 0))}  [field, target >67.5%]")
    lines.append(f"  Wait efficiency (visit / (visit+travel+wait))  {fmt_pct(agg.get('field_incl_wait_pct', 0))}")
    lines.append(f"  Idle efficiency (visit / (visit+travel+idle))  {fmt_pct(agg.get('idle_efficiency_pct', 0))}  [≈ efficiency]")
    if agg.get("shifts_no_visits", 0) > 0:
        lines.append(f"  System efficiency (visit / all provisioned)  {fmt_pct(agg.get('system_efficiency_pct', 0))}  [incl. {agg['shifts_no_visits']} empty shifts]")

    # ─── 2. Times (h:min) ────────────────────────────────────────────────────
    lines.append("")
    lines.append("--- Times (h:min) ---")
    lines.append(f"  shift   = {fmt_hm(sh)}")
    lines.append(f"  visit   = {fmt_hm(vh)}")
    lines.append(f"  travel  = {fmt_hm(th)}")
    lines.append(f"  wait    = {fmt_hm(wh)}")
    lines.append(f"  break   = {fmt_hm(bh)}")
    lines.append(f"  idle    = {fmt_hm(ih)}  [inactive / empty shift time]")
    lines.append(f"  sum     = {fmt_hm(sum_h)}  (visit+travel+wait+break+idle)")

    # ─── 3. Counts ───────────────────────────────────────────────────────────
    total_visits = agg["total_visits_assigned"] + agg["unassigned_visits"]
    lines.append("")
    lines.append("--- Counts ---")
    lines.append(f"  Employees (vehicles):  {agg['total_vehicles']}  (empty: {agg['empty_vehicles']})")
    lines.append(f"  Shifts:                {agg['total_shifts']}  (with visits: {agg['shifts_with_visits']}, empty: {agg['shifts_no_visits']})")
    lines.append(f"  Visits assigned:       {agg['total_visits_assigned']} / {total_visits}")
    lines.append(f"  Unassigned:            {agg['unassigned_visits']}")

    if input_info:
        lines.append("")
        lines.append("--- Input ---")
        vg = input_info.get("visit_groups", 0)
        gv = input_info.get("group_visits", 0)
        cv = input_info.get("care_visits", input_info["visits"])
        tw = input_info.get("time_window_slots", 0)
        if vg:
            lines.append(f"  Care visits: {cv} ({input_info['visits']} solo + {vg} double-employee)")
            lines.append(f"  Timefold visits: {input_info['total_visits']} ({input_info['visits']} solo + {gv} in {vg} groups)")
        else:
            lines.append(f"  Care visits: {cv}")
        if tw:
            lines.append(f"  Time window slots: {tw} (movable across weeks)")
        lines.append(f"  Vehicles: {input_info['vehicles']}  Shifts: {input_info['shifts']}")

    lines.append("")
    lines.append("--- Solver ---")
    lines.append(f"  Plan:  {agg['route_plan_id']}")
    lines.append(f"  Score: {agg['score']}")

    # ─── Time equation: shift = visit + travel + wait + break + idle ──────────
    lines.append("")
    lines.append("--- Time equation: shift = visit + travel + wait + break + idle ---")
    pct_shift = (vh / sh * 100) if sh > 0 else 0.0
    lines.append(f"  shift  = {fmt_hm(sh)}  (100.00%)")
    lines.append(f"  visit  = {fmt_hm(vh)}  ({fmt_pct(vh/sh*100) if sh > 0 else '0.00%'})")
    lines.append(f"  travel = {fmt_hm(th)}  ({fmt_pct(th/sh*100) if sh > 0 else '0.00%'})")
    lines.append(f"  wait   = {fmt_hm(wh)}  ({fmt_pct(wh/sh*100) if sh > 0 else '0.00%'})")
    lines.append(f"  break  = {fmt_hm(bh)}  ({fmt_pct(bh/sh*100) if sh > 0 else '0.00%'})")
    lines.append(f"  idle   = {fmt_hm(ih)}  ({fmt_pct(ih/sh*100) if sh > 0 else '0.00%'})")
    lines.append(f"  sum    = {fmt_hm(sum_h)}")
    lines.append(f"  visit/shift = {fmt_pct(pct_shift)}")

    if exclude_inactive:
        adj_shift_h = sh - inactive_h
        adj_cost = adj_shift_h * COST_PER_HOUR
        lines.append("")
        lines.append(f"--- Time & Cost Breakdown (inactive removed: {fmt_hm(inactive_h)} / {fmt_kr(inactive_h * COST_PER_HOUR).strip()} kr) ---")
        lines.append(f"  {'Category':<20} {'Time':>12}  {'% shift':>8}  {'Cost (kr)':>10}  {'Rev (kr)':>10}")
        lines.append(f"  {'─'*20} {'─'*12}  {'─'*8}  {'─'*10}  {'─'*10}")
        for label, hours, pct, cost, rev in [
            ("Active shift", adj_shift_h, 100.0, adj_cost, None),
            ("  Visit time", agg["visit_time_h"], agg["visit_time_h"]/adj_shift_h*100, agg["visit_cost_kr"], agg["visit_revenue_kr"]),
            ("  Travel time", agg["travel_time_h"], agg["travel_time_h"]/adj_shift_h*100, agg["travel_cost_kr"], None),
            ("  Wait time", agg["wait_time_h"], agg["wait_time_h"]/adj_shift_h*100, agg["wait_cost_kr"], None),
            ("  Break time", agg["break_time_h"], agg["break_time_h"]/adj_shift_h*100, agg["break_cost_kr"], None),
        ]:
            rev_str = fmt_kr(rev).strip() if rev is not None else ""
            lines.append(f"  {label:<20} {fmt_hm(hours):>12}  {fmt_pct(pct):>8}  {fmt_kr(cost).strip():>10}  {rev_str:>10}")
        lines.append("")
        lines.append("--- Margin (excluding inactive) ---")
        lines.append(f"  Revenue:  {fmt_kr(agg['visit_revenue_kr']).strip()} kr")
        lines.append(f"  Cost:     {fmt_kr(agg['active_cost_kr']).strip()} kr")
        lines.append(f"  Margin:   {fmt_kr(agg['active_margin_kr']).strip()} kr  ({fmt_pct(agg['active_margin_pct'])})")
    else:
        lines.append("")
        lines.append("--- Time & Cost Breakdown ---")
        lines.append(f"  {'Category':<20} {'Time':>12}  {'% shift':>8}  {'Cost (kr)':>10}  {'Rev (kr)':>10}")
        lines.append(f"  {'─'*20} {'─'*12}  {'─'*8}  {'─'*10}  {'─'*10}")
        for label, hours, pct, cost, rev in [
            ("Shift time", sh, 100.0, agg["shift_cost_kr"], None),
            ("  Visit time", agg["visit_time_h"], agg["visit_time_h"]/sh*100, agg["visit_cost_kr"], agg["visit_revenue_kr"]),
            ("  Travel time", agg["travel_time_h"], agg["travel_time_h"]/sh*100, agg["travel_cost_kr"], None),
            ("  Wait time", agg["wait_time_h"], agg["wait_time_h"]/sh*100, agg["wait_cost_kr"], None),
            ("  Break time", agg["break_time_h"], agg["break_time_h"]/sh*100, agg["break_cost_kr"], None),
            ("  Inactive time", agg["inactive_time_h"], agg["inactive_time_h"]/sh*100, agg["inactive_cost_kr"], None),
        ]:
            rev_str = fmt_kr(rev).strip() if rev is not None else ""
            lines.append(f"  {label:<20} {fmt_hm(hours):>12}  {fmt_pct(pct):>8}  {fmt_kr(cost).strip():>10}  {rev_str:>10}")
        lines.append("")
        lines.append("--- Margin ---")
        lines.append(f"  Revenue:  {fmt_kr(agg['visit_revenue_kr']).strip()} kr")
        lines.append(f"  Cost:     {fmt_kr(agg['shift_cost_kr']).strip()} kr")
        lines.append(f"  Margin:   {fmt_kr(agg['margin_kr']).strip()} kr  ({fmt_pct(agg['margin_pct'])})")

    if not exclude_inactive:
        waste = agg["travel_cost_kr"] + agg["wait_cost_kr"] + agg["inactive_cost_kr"] + agg["break_cost_kr"]
        waste_pct = (waste / agg["shift_cost_kr"] * 100) if agg["shift_cost_kr"] > 0 else 0.0
        lines.append("")
        lines.append("--- Costs to minimize (travel, wait) + other non-visit ---")
        lines.append(f"  Travel:   {fmt_kr(agg['travel_cost_kr']).strip()} kr  ({fmt_hm(agg['travel_time_h'])})  [minimize]")
        lines.append(f"  Wait:     {fmt_kr(agg['wait_cost_kr']).strip()} kr  ({fmt_hm(agg['wait_time_h'])})  [minimize]")
        lines.append(f"  Inactive: {fmt_kr(agg['inactive_cost_kr']).strip()} kr  ({fmt_hm(agg['inactive_time_h'])})")
        lines.append(f"  Break:    {fmt_kr(agg['break_cost_kr']).strip()} kr  ({fmt_hm(agg['break_time_h'])})")
        lines.append(f"  Total:    {fmt_kr(waste).strip()} kr  ({fmt_pct(waste_pct)} of shift cost)")
    else:
        waste = agg["travel_cost_kr"] + agg["wait_cost_kr"] + agg["break_cost_kr"]
        waste_pct = (waste / agg["active_cost_kr"] * 100) if agg["active_cost_kr"] > 0 else 0.0
        lines.append("")
        lines.append("--- Costs to minimize (travel, wait) + break ---")
        lines.append(f"  Travel:   {fmt_kr(agg['travel_cost_kr']).strip()} kr  ({fmt_hm(agg['travel_time_h'])})  [minimize]")
        lines.append(f"  Wait:     {fmt_kr(agg['wait_cost_kr']).strip()} kr  ({fmt_hm(agg['wait_time_h'])})  [minimize]")
        lines.append(f"  Break:    {fmt_kr(agg['break_cost_kr']).strip()} kr  ({fmt_hm(agg['break_time_h'])})")
        lines.append(f"  Total:    {fmt_kr(waste).strip()} kr  ({fmt_pct(waste_pct)} of active cost)")

    lines.append("=" * w)
    return lines


def print_report(agg: dict, input_info: dict | None = None, exclude_inactive: bool = False) -> None:
    """Print the full metrics report to stdout."""
    for line in report_lines(agg, input_info, exclude_inactive):
        print(line)


# ─── File output ──────────────────────────────────────────────────────────────

def save_metrics(
    agg: dict,
    input_info: dict | None,
    save_dir: Path,
    exclude_inactive: bool = False,
) -> Path:
    """Save timestamped metrics JSON and metrics_report_<route_id>.txt (full report)."""
    save_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    rid = agg.get("route_plan_id", "unknown")
    rid_short = rid[:8] if len(rid) > 8 else rid
    filename = f"metrics_{ts}_{rid_short}.json"
    filepath = save_dir / filename

    out = {}
    for k, v in agg.items():
        if k == "per_shift":
            continue
        if isinstance(v, (int, float)) and (k.endswith("_kr") or "cost_kr" in k or "revenue_kr" in k or "margin_kr" in k):
            out[k] = int(round(v))
        elif isinstance(v, (int, float)) and (k.endswith("_pct") or "efficiency" in k):
            out[k] = round(v, 2)
        else:
            out[k] = v
    out["timestamp"] = datetime.now().isoformat()
    out["cost_per_hour_kr"] = int(COST_PER_HOUR)
    out["revenue_per_visit_hour_kr"] = int(REVENUE_PER_VISIT_HOUR)
    if input_info:
        out["input_summary"] = input_info
    if exclude_inactive:
        out["exclude_inactive"] = True
        out["shift_time_active_h"] = agg["shift_time_h"] - agg["inactive_time_h"]
        out["cost_active_kr"] = agg["active_cost_kr"]
        out["margin_active_kr"] = agg["visit_revenue_kr"] - agg["active_cost_kr"]
        out["margin_active_pct"] = agg["active_margin_pct"]

    with open(filepath, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    # Store full text report (README: metrics = JSON + report with efficiency definitions)
    report_path = save_dir / f"metrics_report_{rid_short}.txt"
    report_content = "\n".join(report_lines(agg, input_info, exclude_inactive))
    with open(report_path, "w") as f:
        f.write(report_content)

    return filepath, report_path


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description="Measure Timefold FSR output metrics with cost/revenue.")
    ap.add_argument("output", type=Path, help="Timefold output JSON file.")
    ap.add_argument("--input", type=Path, default=None,
                    help="Corresponding input JSON (for scheduled shift times).")
    ap.add_argument("--save", type=Path, default=None,
                    help="Directory to save timestamped metrics JSON.")
    ap.add_argument("--csv", type=Path, default=None,
                    help="Write per-shift metrics to CSV.")
    ap.add_argument("--exclude-inactive", action="store_true",
                    help="Exclude inactive time from shift/cost (ESS simulation: only travel, visit, break, wait). Use for from-patch outputs.")
    ap.add_argument("--exclude-empty-shifts-only", action="store_true",
                    help="Variant 1: Helt tomma skift/medarbetare bidrar 0 skifttimmar; idle = endast slutet av skift med besök.")
    ap.add_argument("--visit-span-only", action="store_true",
                    help="Variant 2: Som variant 1 + skifttid = första besök start -> sista besök slut (inga tomma delar).")
    args = ap.parse_args()

    if not args.output.exists():
        print(f"Error: not found {args.output}", file=sys.stderr)
        return 1

    with open(args.output) as f:
        output_data = json.load(f)

    input_data = None
    if args.input and args.input.exists():
        with open(args.input) as f:
            input_data = json.load(f)

    input_info = analyze_input(args.input) if args.input else None
    agg = aggregate(
        output_data,
        input_data,
        use_depot_end=args.exclude_inactive,
        visit_span_only=args.visit_span_only,
        exclude_empty_shifts_only=args.exclude_empty_shifts_only,
    )
    print_report(agg, input_info, exclude_inactive=args.exclude_inactive)

    if args.save:
        filepath, report_path = save_metrics(agg, input_info, args.save, exclude_inactive=args.exclude_inactive)
        print(f"\nMetrics saved to {filepath}")
        print(f"Report saved to {report_path}")

    if args.csv:
        import csv as csv_mod
        with open(args.csv, "w", newline="") as f:
            fieldnames = [
                "vehicle_id", "shift_id", "visit_count",
                "shift_sec", "break_sec", "visit_sec", "travel_sec",
                "wait_sec", "inactive_sec", "efficiency_pct",
                "shift_cost_kr", "visit_revenue_kr",
            ]
            writer = csv_mod.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in agg["per_shift"]:
                writer.writerow({k: row.get(k) for k in fieldnames})
        print(f"Per-shift CSV written to {args.csv}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
