#!/usr/bin/env python3
"""
Compute Timefold FSR metrics from output JSON (+ optional input JSON).
Writes metrics JSON and metrics_report_<route_id>.txt.
Exclude-inactive mode: only shifts with at least one visit (from-patch style).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_duration(s: str) -> float:
    """Parse ISO8601 duration (PT1H30M, PT45M, PT2M18S) to seconds."""
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


def parse_iso(s: str) -> datetime:
    """Parse ISO datetime to naive UTC seconds since epoch for delta math."""
    dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if dt.tzinfo:
        dt = dt.astimezone(timezone.utc)
    return dt


def aggregate_from_output(
    output_path: Path,
    input_data: dict | None,
    exclude_inactive: bool,
) -> dict:
    """Compute aggregate metrics from FSR output (and optional input for summary)."""
    with open(output_path, encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("metadata") or data.get("run") or {}
    route_plan_id = meta.get("id") or "unknown"
    score = meta.get("score") or ""
    solver_status = (meta.get("solverStatus") or "").replace("_", " ")

    vehicles_out = (data.get("modelOutput") or {}).get("vehicles") or []
    input_metrics = data.get("inputMetrics") or {}

    total_visit_sec = 0.0
    total_travel_sec = 0.0
    total_wait_sec = 0.0
    total_break_sec = 0.0
    total_shift_sec = 0.0
    n_shifts = 0
    n_shifts_with_visits = 0
    vehicle_ids_with_visits = set()
    vehicle_ids_all = set()
    empty_vehicle_ids = []

    for v in vehicles_out:
        vid = v.get("id") or ""
        vehicle_ids_all.add(vid)
        shifts_list = v.get("shifts") or []
        for shift in shifts_list:
            start_s = shift.get("startTime")
            itinerary = shift.get("itinerary") or []
            metrics = shift.get("metrics") or {}
            end_s = metrics.get("endLocationArrivalTime")
            if not end_s and itinerary:
                last = itinerary[-1]
                if last.get("kind") == "VISIT":
                    end_s = last.get("departureTime")
                elif last.get("kind") == "BREAK":
                    end_s = last.get("endTime")
            if not start_s or not end_s:
                continue
            shift_sec = (parse_iso(end_s) - parse_iso(start_s)).total_seconds()
            visit_sec = 0.0
            travel_sec = 0.0
            wait_sec = 0.0
            break_sec = 0.0
            for item in itinerary:
                kind = (item.get("kind") or "").upper()
                if kind == "VISIT":
                    visit_sec += parse_duration(item.get("effectiveServiceDuration") or "PT0S")
                    travel_sec += parse_duration(item.get("travelTimeFromPreviousStandstill") or "PT0S")
                    arr = item.get("arrivalTime")
                    start_svc = item.get("startServiceTime")
                    if arr and start_svc:
                        wait_sec += (parse_iso(start_svc) - parse_iso(arr)).total_seconds()
                elif kind == "BREAK":
                    bs = item.get("startTime")
                    be = item.get("endTime")
                    if bs and be:
                        break_sec += (parse_iso(be) - parse_iso(bs)).total_seconds()
            idle_sec = max(0, shift_sec - visit_sec - travel_sec - wait_sec - break_sec)
            has_visits = visit_sec > 0
            if exclude_inactive and not has_visits:
                continue
            n_shifts += 1
            if has_visits:
                n_shifts_with_visits += 1
                vehicle_ids_with_visits.add(vid)
            total_shift_sec += shift_sec
            total_visit_sec += visit_sec
            total_travel_sec += travel_sec
            total_wait_sec += wait_sec
            total_break_sec += break_sec

    for vid in sorted(vehicle_ids_all):
        if vid not in vehicle_ids_with_visits:
            empty_vehicle_ids.append(vid)

    total_idle_sec = max(0, total_shift_sec - total_visit_sec - total_travel_sec - total_wait_sec - total_break_sec)

    COST_PER_HOUR = 170
    REVENUE_PER_VISIT_HOUR = 550
    shift_h = total_shift_sec / 3600
    visit_h = total_visit_sec / 3600
    travel_h = total_travel_sec / 3600
    wait_h = total_wait_sec / 3600
    break_h = total_break_sec / 3600
    idle_h = total_idle_sec / 3600

    shift_cost = round(shift_h * COST_PER_HOUR)
    visit_cost = round(visit_h * COST_PER_HOUR)
    travel_cost = round(travel_h * COST_PER_HOUR)
    wait_cost = round(wait_h * COST_PER_HOUR)
    break_cost = round(break_h * COST_PER_HOUR)
    inactive_cost = round(idle_h * COST_PER_HOUR)
    visit_revenue = round(visit_h * REVENUE_PER_VISIT_HOUR)
    margin_kr = visit_revenue - shift_cost
    margin_pct = (margin_kr / visit_revenue * 100) if visit_revenue else 0

    assignable_sec = total_visit_sec + total_travel_sec + total_wait_sec
    shift_minus_break_sec = total_shift_sec - total_break_sec
    efficiency_pct = (total_visit_sec / shift_minus_break_sec * 100) if shift_minus_break_sec else 0
    field_visit_travel = total_visit_sec + total_travel_sec
    field_efficiency_pct = (total_visit_sec / field_visit_travel * 100) if field_visit_travel else 0
    field_incl_wait_pct = (total_visit_sec / assignable_sec * 100) if assignable_sec else 0
    visit_plus_idle = total_visit_sec + total_travel_sec + total_idle_sec
    idle_efficiency_pct = (total_visit_sec / visit_plus_idle * 100) if visit_plus_idle else 0
    routing_efficiency_pct = (total_visit_sec / assignable_sec * 100) if assignable_sec else 0
    total_provisioned_sec = shift_h * 3600 * (len(vehicle_ids_all) * (input_metrics.get("vehicleShifts") or 0) // max(1, len(vehicle_ids_all))) if vehicle_ids_all else shift_sec
    # System efficiency: visit / all provisioned (including empty shifts). When exclude_inactive we already dropped empty shifts so shift_sec is only active; then system = efficiency.
    all_shifts_sec = shift_sec  # placeholder; for base solve we need total shift time including empty
    # Simplified: when exclude_inactive, system_efficiency_pct = efficiency_pct. When not, we'd need total shift time including empty - would require second pass. For from-patch output we only have non-empty shifts, so system = efficiency.
    system_efficiency_pct = efficiency_pct if exclude_inactive else (total_visit_sec / total_shift_sec * 100 if total_shift_sec else 0)
    efficiency_assignable_used_pct = routing_efficiency_pct

    total_vehicles = len(vehicle_ids_all) if not exclude_inactive else len(vehicle_ids_with_visits)
    total_shifts_input = input_metrics.get("vehicleShifts") or 0
    if exclude_inactive:
        total_shifts = n_shifts
        empty_vehicles = 0
        shifts_no_visits = 0
    else:
        total_shifts = total_shifts_input or n_shifts
        empty_vehicles = len(vehicle_ids_all) - len(vehicle_ids_with_visits)
        shifts_no_visits = (total_shifts - n_shifts_with_visits) if total_shifts else 0

    active_shift_h = shift_h - idle_h
    active_cost_kr = round(active_shift_h * COST_PER_HOUR)
    active_margin_kr = visit_revenue - active_cost_kr
    active_margin_pct = (active_margin_kr / visit_revenue * 100) if visit_revenue else 0

    visits_count = input_metrics.get("visits") or input_metrics.get("mandatoryVisits") or 0
    assigned = data.get("modelOutput", {}).get("unassignedVisits")
    total_assigned = (input_metrics.get("totalAssignedVisits") or visits_count) if input_metrics else visits_count
    unassigned = len(assigned) if isinstance(assigned, list) else (visits_count - total_assigned if visits_count else 0)
    if input_metrics and "totalAssignedVisits" in input_metrics:
        total_assigned = input_metrics["totalAssignedVisits"]
        unassigned = visits_count - total_assigned

    # Input summary from input_data or inputMetrics
    if input_data:
        mi = input_data.get("modelInput") or {}
        visits_in = mi.get("visits") or []
        vehicles_in = mi.get("vehicles") or []
        n_visits = len(visits_in) if isinstance(visits_in, list) else 0
        n_vehicles = len(vehicles_in)
        n_shifts_in = sum(len((v.get("shifts") or [])) for v in vehicles_in)
        input_summary = {
            "visits": n_visits,
            "visit_groups": input_metrics.get("visitGroups") or 0,
            "group_visits": (input_metrics.get("visitGroups") or 0) * 2,
            "total_visits": input_metrics.get("visits") or n_visits,
            "care_visits": input_metrics.get("visits") or n_visits,
            "time_window_slots": input_metrics.get("visits") or n_visits,
            "vehicles": input_metrics.get("vehicles") or n_vehicles,
            "shifts": input_metrics.get("vehicleShifts") or n_shifts_in,
            "shifts_fixed_cost": 0,
            "shifts_hourly": 0,
        }
    else:
        input_summary = {
            "visits": input_metrics.get("visits") or 0,
            "visit_groups": input_metrics.get("visitGroups") or 0,
            "group_visits": (input_metrics.get("visitGroups") or 0) * 2,
            "total_visits": input_metrics.get("visits") or 0,
            "care_visits": input_metrics.get("visits") or 0,
            "time_window_slots": input_metrics.get("visits") or 0,
            "vehicles": input_metrics.get("vehicles") or 0,
            "shifts": input_metrics.get("vehicleShifts") or 0,
            "shifts_fixed_cost": 0,
            "shifts_hourly": 0,
        }

    rid_short = (route_plan_id.split("-")[0] if route_plan_id != "unknown" else "unknown")

    agg = {
        "route_plan_id": route_plan_id,
        "score": score,
        "solver_status": solver_status,
        "total_visits_assigned": total_assigned,
        "unassigned_visits": unassigned,
        "total_vehicles": total_vehicles,
        "empty_vehicles": empty_vehicles if not exclude_inactive else 0,
        "empty_vehicle_ids": [] if exclude_inactive else empty_vehicle_ids,
        "total_shifts": total_shifts,
        "shifts_with_visits": n_shifts_with_visits,
        "shifts_no_visits": shifts_no_visits if not exclude_inactive else 0,
        "shift_time_h": round(shift_h, 6),
        "break_time_h": round(break_h, 6),
        "visit_time_h": round(visit_h, 6),
        "travel_time_h": round(travel_h, 6),
        "wait_time_h": round(wait_h, 6),
        "inactive_time_h": round(idle_h, 6),
        "shift_cost_kr": shift_cost,
        "visit_cost_kr": visit_cost,
        "travel_cost_kr": travel_cost,
        "wait_cost_kr": wait_cost,
        "break_cost_kr": break_cost,
        "inactive_cost_kr": inactive_cost,
        "visit_revenue_kr": visit_revenue,
        "margin_kr": margin_kr,
        "margin_pct": round(margin_pct, 2),
        "efficiency_pct": round(efficiency_pct, 2),
        "efficiency_assignable_used_pct": round(efficiency_assignable_used_pct, 2),
        "field_efficiency_pct": round(field_efficiency_pct, 2),
        "field_incl_wait_pct": round(field_incl_wait_pct, 2),
        "idle_efficiency_pct": round(idle_efficiency_pct, 2),
        "routing_efficiency_pct": round(routing_efficiency_pct, 2),
        "system_efficiency_pct": round(system_efficiency_pct, 2),
        "active_cost_kr": active_cost_kr,
        "active_margin_kr": active_margin_kr,
        "active_margin_pct": round(active_margin_pct, 2),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "cost_per_hour_kr": COST_PER_HOUR,
        "revenue_per_visit_hour_kr": REVENUE_PER_VISIT_HOUR,
        "input_summary": input_summary,
        "exclude_inactive": exclude_inactive,
        "shift_time_active_h": round(active_shift_h, 6),
        "cost_active_kr": active_cost_kr,
        "margin_active_kr": active_margin_kr,
        "margin_active_pct": round(active_margin_pct, 6),
    }
    # Sanity: visit+travel+wait+break+idle should equal shift (when excluding inactive we only have non-empty shifts so idle is the small remainder)
    sum_parts = visit_h + travel_h + wait_h + break_h + idle_h
    diff_pct = abs(sum_parts - shift_h) / shift_h * 100 if shift_h else 0
    agg["metrics_sanity_diff_pct"] = round(diff_pct, 2)

    kpis = data.get("kpis") or {}
    agg["total_visits_assigned"] = kpis.get("totalAssignedVisits") or input_metrics.get("totalAssignedVisits") or input_summary.get("total_visits") or 0
    visits_count = input_metrics.get("visits") or input_metrics.get("mandatoryVisits") or input_summary.get("total_visits") or 0
    agg["unassigned_visits"] = kpis.get("totalUnassignedVisits") if "totalUnassignedVisits" in (kpis or {}) else max(0, visits_count - agg["total_visits_assigned"])

    return agg


def report_lines(agg: dict, exclude_inactive: bool) -> list[str]:
    """Produce text report lines."""
    lines = [
        "=========================================================================",
        "TIMEFOLD FSR METRICS REPORT  (EXCLUDING INACTIVE)" if exclude_inactive else "TIMEFOLD FSR METRICS REPORT",
        "=========================================================================",
        "",
        "--- KPI: Efficiency % ---",
    ]
    sh = agg["shift_time_h"]
    vh = agg["visit_time_h"]
    bh = agg["break_time_h"]
    th = agg["travel_time_h"]
    wh = agg["wait_time_h"]
    ih = agg["inactive_time_h"]
    adj = sh - bh
    lines.append(f"  Efficiency (visit / (shift − break))     {agg['efficiency_pct']}%  [staffing]")
    lines.append(f"  Travel efficiency (visit / (visit+travel))  {agg['field_efficiency_pct']}%  [field, target >67.5%]")
    lines.append(f"  Wait efficiency (visit / (visit+travel+wait))  {agg['field_incl_wait_pct']}%")
    lines.append(f"  Idle efficiency (visit / (visit+travel+idle))  {agg['idle_efficiency_pct']}%  [≈ efficiency]")
    if not exclude_inactive and agg.get("shifts_no_visits"):
        lines.append(f"  System efficiency (visit / all provisioned)  {agg['system_efficiency_pct']}%  [incl. {agg['shifts_no_visits']} empty shifts]")
    lines.append("")
    lines.append("--- Times (h:min) ---")
    def h_min(h: float) -> str:
        hi = int(h)
        mi = int((h - hi) * 60 + 0.5)
        return f"{hi}h {mi}min"
    lines.append(f"  shift   = {h_min(sh)}")
    lines.append(f"  visit   = {h_min(vh)}")
    lines.append(f"  travel  = {h_min(th)}")
    lines.append(f"  wait    = {h_min(wh)}")
    lines.append(f"  break   = {h_min(bh)}")
    lines.append(f"  idle    = {h_min(ih)}  [inactive / empty shift time]")
    lines.append(f"  sum     = {h_min(vh+th+wh+bh+ih)}  (visit+travel+wait+break+idle)")
    lines.append("")
    lines.append("--- Counts ---")
    lines.append(f"  Employees (vehicles):  {agg['total_vehicles']}  (empty: {agg['empty_vehicles']})")
    lines.append(f"  Shifts:                {agg['total_shifts']}  (with visits: {agg['shifts_with_visits']}, empty: {agg['shifts_no_visits']})")
    lines.append(f"  Visits assigned:       {agg['total_visits_assigned']} / {agg['input_summary']['total_visits']}")
    lines.append(f"  Unassigned:            {agg['unassigned_visits']}")
    lines.append("")
    lines.append("--- Input ---")
    inv = agg["input_summary"]
    lines.append(f"  Care visits: {inv['care_visits']} ({inv['visits']} solo + {inv['visit_groups']} double-employee)")
    lines.append(f"  Timefold visits: {inv['total_visits']} ({inv['visits']} solo + {inv['group_visits']} in {inv['visit_groups']} groups)")
    lines.append(f"  Time window slots: {inv['time_window_slots']}")
    lines.append(f"  Vehicles: {inv['vehicles']}  Shifts: {inv['shifts']}")
    lines.append("")
    lines.append("--- Solver ---")
    lines.append(f"  Plan:  {agg['route_plan_id']}")
    lines.append(f"  Score: {agg['score']}")
    lines.append("")
    sum_h = vh + th + wh + bh + ih
    pct_shift = (vh / sh * 100) if sh else 0
    lines.append("--- Time equation: shift = visit + travel + wait + break + idle ---")
    lines.append(f"  shift  = {h_min(sh)}  (100.00%)")
    lines.append(f"  visit  = {h_min(vh)}  ({vh/sh*100:.2f}%)" if sh else "  visit  = 0h 0min")
    lines.append(f"  travel = {h_min(th)}  ({th/sh*100:.2f}%)" if sh else "  travel = 0h 0min")
    lines.append(f"  wait   = {h_min(wh)}  ({wh/sh*100:.2f}%)" if sh else "  wait   = 0h 0min")
    lines.append(f"  break  = {h_min(bh)}  ({bh/sh*100:.2f}%)" if sh else "  break  = 0h 0min")
    lines.append(f"  idle   = {h_min(ih)}  ({ih/sh*100:.2f}%)" if sh else "  idle   = 0h 0min")
    lines.append(f"  sum    = {h_min(sum_h)}")
    if sh:
        lines.append(f"  visit/shift = {pct_shift:.2f}%")
    lines.append("")
    lines.append(f"--- Time & Cost Breakdown (inactive removed: {h_min(ih)} / {agg['inactive_cost_kr']:,} kr) ---")
    active_h = sh - ih
    lines.append("  Category                     Time   % shift   Cost (kr)    Rev (kr)")
    lines.append("  ──────────────────── ──────────── ──────── ────────── ──────────")
    lines.append(f"  Active shift          {h_min(active_h):>12}   100.00%     {agg['active_cost_kr']:>6,}")
    if active_h:
        lines.append(f"    Visit time          {h_min(vh):>12}    {vh/active_h*100:>5.2f}%     {agg['visit_cost_kr']:>6,}     {agg['visit_revenue_kr']:>6,}")
        lines.append(f"    Travel time           {h_min(th):>12}    {th/active_h*100:>5.2f}%     {agg['travel_cost_kr']:>6,}")
        lines.append(f"    Wait time             {h_min(wh):>12}    {wh/active_h*100:>5.2f}%     {agg['wait_cost_kr']:>6,}")
        lines.append(f"    Break time            {h_min(bh):>12}    {bh/active_h*100:>5.2f}%     {agg['break_cost_kr']:>6,}")
    lines.append("")
    lines.append("--- Margin (excluding inactive) ---")
    lines.append(f"  Revenue:  {agg['visit_revenue_kr']:,} kr")
    lines.append(f"  Cost:     {agg['active_cost_kr']:,} kr")
    lines.append(f"  Margin:   {agg['active_margin_kr']:,} kr  ({agg['active_margin_pct']:.2f}%)")
    lines.append("")
    lines.append("--- Non-Visit Cost (waste, excl inactive) ---")
    lines.append(f"  Travel:   {agg['travel_cost_kr']:,} kr  ({h_min(th)})")
    lines.append(f"  Wait:     {agg['wait_cost_kr']:,} kr  ({h_min(wh)})")
    lines.append(f"  Break:    {agg['break_cost_kr']:,} kr  ({h_min(bh)})")
    pct_waste = (agg['travel_cost_kr'] + agg['wait_cost_kr'] + agg['break_cost_kr']) / agg['active_cost_kr'] * 100 if agg['active_cost_kr'] else 0
    lines.append(f"  Total:    {agg['travel_cost_kr'] + agg['wait_cost_kr'] + agg['break_cost_kr']:,} kr  ({pct_waste:.2f}% of active cost)")
    lines.append("=========================================================================")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute FSR metrics from output JSON")
    parser.add_argument("output", type=Path, help="Path to FSR output JSON")
    parser.add_argument("--input", type=Path, default=None, help="Path to FSR input JSON (for input summary)")
    parser.add_argument("--exclude-inactive", action="store_true", help="Exclude empty shifts (from-patch style)")
    parser.add_argument("--save", type=Path, default=None, help="Directory to save metrics JSON and report TXT")
    args = parser.parse_args()

    input_data = None
    if args.input and args.input.exists():
        with open(args.input, encoding="utf-8") as f:
            input_data = json.load(f)

    agg = aggregate_from_output(args.output, input_data, args.exclude_inactive)
    rid = agg.get("route_plan_id", "unknown")
    rid_short = rid.split("-")[0] if rid != "unknown" else "unknown"

    if args.save:
        args.save.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        json_path = args.save / f"metrics_{ts}_{rid_short}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(agg, f, indent=2)
        report_path = args.save / f"metrics_report_{rid_short}.txt"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines(agg, args.exclude_inactive)))
        print(f"Wrote {json_path}")
        print(f"Wrote {report_path}")
    else:
        print(json.dumps(agg, indent=2))
        print("\n".join(report_lines(agg, args.exclude_inactive)))

    return 0


if __name__ == "__main__":
    sys.exit(main())
