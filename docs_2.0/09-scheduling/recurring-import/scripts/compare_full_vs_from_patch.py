#!/usr/bin/env python3
"""
Compare full fixed-cost solution vs from-patch revision: shift time (excl breaks),
visit time, efficiency (visit/shift) %.
Output: summary table and optional per-shift CSV.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parent
if ROOT.name == "scripts":
    ROOT = ROOT.parent
FULL_FIXED = ROOT / "fixed/export-field-service-routing-eb827631-6657-4c4f-948f-0c8aeceacd62-output.json"
FROM_PATCH = ROOT / "fixed/from-patch-reduced/export-field-service-routing-5ff46c3d-f7c3-40bd-9428-5ee24fc5bcd9-output.json"


def parse_duration_seconds(iso: str) -> float:
    """Parse ISO 8601 duration (PT1H30M, PT10M, PT7M48S) to seconds."""
    if not iso or not iso.startswith("PT"):
        return 0.0
    total = 0.0
    for m in re.finditer(r"(\d+)([HMS])", iso):
        val = int(m.group(1))
        if m.group(2) == "H":
            total += val * 3600
        elif m.group(2) == "M":
            total += val * 60
        else:
            total += val
    return total




def shift_metrics(shift: dict) -> dict:
    """
    For one shift: shift_time_excl_breaks_min, visit_time_min, travel_time_min,
    visit_count, efficiency_pct.
    Shift time = from startTime to end of last activity (or endLocationArrivalTime), minus break time.
    """
    start_s = shift.get("startTime")
    metrics = shift.get("metrics") or {}
    end_s = metrics.get("endLocationArrivalTime")
    itinerary = shift.get("itinerary") or []

    break_seconds = 0.0
    visit_seconds = 0.0
    wait_seconds = 0.0  # arrive early: startServiceTime - arrivalTime per visit
    last_departure = None

    for item in itinerary:
        if not isinstance(item, dict):
            continue
        kind = item.get("kind")
        if kind == "BREAK":
            st = item.get("startTime")
            et = item.get("endTime")
            if st and et:
                try:
                    dt1 = datetime.fromisoformat(st.replace("Z", "+00:00").split("+")[0])
                    dt2 = datetime.fromisoformat(et.replace("Z", "+00:00").split("+")[0])
                    break_seconds += (dt2 - dt1).total_seconds()
                except Exception:
                    pass
        elif kind == "VISIT":
            dur = item.get("effectiveServiceDuration")
            if dur:
                visit_seconds += parse_duration_seconds(dur)
            arr = item.get("arrivalTime")
            start_svc = item.get("startServiceTime")
            if arr and start_svc:
                try:
                    t_arr = datetime.fromisoformat(arr.replace("Z", "+00:00"))
                    t_start = datetime.fromisoformat(start_svc.replace("Z", "+00:00"))
                    wait_seconds += max(0.0, (t_start - t_arr).total_seconds())
                except Exception:
                    pass
            dep = item.get("departureTime")
            if dep:
                last_departure = dep

    if not end_s and last_departure:
        # Include final leg to depot: end = last_departure + travelTimeFromLastVisitToEndLocation
        last_leg = parse_duration_seconds(metrics.get("travelTimeFromLastVisitToEndLocation") or "PT0S")
        if last_leg > 0:
            try:
                dt = datetime.fromisoformat(last_departure.replace("Z", "+00:00"))
                end_s = (dt + timedelta(seconds=last_leg)).isoformat()
            except Exception:
                end_s = last_departure
        else:
            end_s = last_departure
    if not end_s and itinerary:
        last = itinerary[-1]
        if isinstance(last, dict):
            end_s = last.get("endTime") or last.get("departureTime")

    shift_start_sec = 0.0
    shift_end_sec = 0.0
    if start_s:
        try:
            dt = datetime.fromisoformat(start_s.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            shift_start_sec = dt.timestamp()
        except Exception:
            pass
    if end_s:
        try:
            dt = datetime.fromisoformat(end_s.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            shift_end_sec = dt.timestamp()
        except Exception:
            pass

    # shift_seconds = clock span from start to end; denominator = shift_seconds - break_seconds
    shift_seconds = shift_end_sec - shift_start_sec if shift_end_sec > shift_start_sec else 0.0
    shift_seconds_excl_breaks = max(0.0, shift_seconds - break_seconds)
    visit_count = sum(1 for i in itinerary if isinstance(i, dict) and i.get("kind") == "VISIT")
    # Empty shift = 0 visits, break-only itinerary, metrics.totalTravelDistanceMeters=0
    # Efficiency = visit_seconds / (shift_seconds - break_seconds)
    efficiency_pct = (visit_seconds / shift_seconds_excl_breaks * 100) if shift_seconds_excl_breaks > 0 else 0.0

    travel_seconds = parse_duration_seconds(metrics.get("totalTravelTime") or "PT0S")

    return {
        "shift_seconds": shift_seconds,
        "break_seconds": break_seconds,
        "shift_seconds_excl_breaks": shift_seconds_excl_breaks,
        "visit_seconds": visit_seconds,
        "travel_seconds": travel_seconds,
        "wait_seconds": wait_seconds,
        "shift_time_excl_breaks_min": shift_seconds_excl_breaks / 60,
        "visit_time_min": visit_seconds / 60,
        "travel_time_min": travel_seconds / 60,
        "wait_time_min": wait_seconds / 60,
        "visit_count": visit_count,
        "efficiency_pct": efficiency_pct,
    }


def aggregate(output: dict) -> dict:
    """Aggregate over all shifts. Efficiency = total_visit_seconds / (total_shift_seconds - total_break_seconds)."""
    vehicles = (output.get("modelOutput") or output.get("model_output") or {}).get("vehicles") or []
    total_shift_seconds = 0.0
    total_break_seconds = 0.0
    total_visit_seconds = 0.0
    total_travel_seconds = 0.0
    total_wait_seconds = 0.0
    total_visits = 0
    shift_count = 0
    shift_count_with_visits = 0
    # Only shifts with ≥1 visit (exclude break-only / empty shifts)
    shift_sec_excl_breaks_with_visits = 0.0
    visit_sec_with_visits = 0.0
    travel_sec_with_visits = 0.0
    wait_sec_with_visits = 0.0

    for v in vehicles:
        for s in v.get("shifts") or []:
            m = shift_metrics(s)
            total_shift_seconds += m["shift_seconds"]
            total_break_seconds += m["break_seconds"]
            total_visit_seconds += m["visit_seconds"]
            total_travel_seconds += m["travel_seconds"]
            total_wait_seconds += m["wait_seconds"]
            total_visits += m["visit_count"]
            shift_count += 1
            if m["visit_count"] > 0:
                shift_count_with_visits += 1
                shift_sec_excl_breaks_with_visits += m["shift_seconds_excl_breaks"]
                visit_sec_with_visits += m["visit_seconds"]
                travel_sec_with_visits += m["travel_seconds"]
                wait_sec_with_visits += m["wait_seconds"]

    total_shift_seconds_excl_breaks = total_shift_seconds - total_break_seconds
    # Efficiency % = visit_seconds / (shift_seconds - break_seconds) * 100
    efficiency_pct = (total_visit_seconds / total_shift_seconds_excl_breaks * 100) if total_shift_seconds_excl_breaks > 0 else 0.0
    total_shift_min = total_shift_seconds_excl_breaks / 60
    total_visit_min = total_visit_seconds / 60
    total_travel_min = total_travel_seconds / 60
    total_wait_min = total_wait_seconds / 60
    total_other_min = total_shift_min - total_visit_min - total_travel_min - total_wait_min
    # Other = empty-shift capacity (shifts with no visits) + any rounding; for shifts with visits: other = 0 (visit+travel+wait = span)
    empty_shift_min = total_shift_min - (shift_sec_excl_breaks_with_visits / 60)
    efficiency_shifts_with_visits_only = (visit_sec_with_visits / shift_sec_excl_breaks_with_visits * 100) if shift_sec_excl_breaks_with_visits > 0 else 0.0
    other_on_used_shifts_min = (shift_sec_excl_breaks_with_visits / 60) - (visit_sec_with_visits / 60) - (travel_sec_with_visits / 60) - (wait_sec_with_visits / 60)

    return {
        "shift_seconds": total_shift_seconds,
        "break_seconds": total_break_seconds,
        "shift_seconds_excl_breaks": total_shift_seconds_excl_breaks,
        "visit_seconds": total_visit_seconds,
        "travel_seconds": total_travel_seconds,
        "wait_seconds": total_wait_seconds,
        "shift_time_excl_breaks_min": total_shift_min,
        "shift_time_excl_breaks_h": total_shift_min / 60,
        "visit_time_min": total_visit_min,
        "visit_time_h": total_visit_min / 60,
        "travel_time_min": total_travel_min,
        "travel_time_h": total_travel_min / 60,
        "wait_time_min": total_wait_min,
        "wait_time_h": total_wait_min / 60,
        "other_time_min": total_other_min,
        "other_time_h": total_other_min / 60,
        "empty_shift_capacity_min": empty_shift_min,
        "other_on_used_shifts_min": other_on_used_shifts_min,
        "visit_count": total_visits,
        "shift_count": shift_count,
        "shift_count_with_visits": shift_count_with_visits,
        "shift_count_no_visits": shift_count - shift_count_with_visits,
        "efficiency_pct": efficiency_pct,
        "efficiency_pct_shifts_with_visits_only": efficiency_shifts_with_visits_only,
    }


def main() -> int:
    full_path = Path(sys.argv[1]) if len(sys.argv) > 1 else FULL_FIXED
    patch_path = Path(sys.argv[2]) if len(sys.argv) > 2 else FROM_PATCH

    if not full_path.exists():
        print(f"Error: not found {full_path}", file=sys.stderr)
        return 1
    if not patch_path.exists():
        print(f"Error: not found {patch_path}", file=sys.stderr)
        return 1

    with open(full_path) as f:
        full = json.load(f)
    with open(patch_path) as f:
        patch = json.load(f)

    a = aggregate(full)
    b = aggregate(patch)

    name_full = (full.get("metadata") or full.get("run") or {}).get("name") or full_path.stem
    name_patch = (patch.get("metadata") or patch.get("run") or {}).get("name") or patch_path.stem

    print("Comparison: Full fixed vs From-patch revision")
    print("=" * 72)
    print(f"{'Metric':<42} {'Full fixed (eb827631)':<18} {'From-patch (5ff46c3d)':<18}")
    print("-" * 72)
    print(f"{'Shift seconds (clock span)':<42} {a['shift_seconds']:<18.0f} {b['shift_seconds']:<18.0f}")
    print(f"{'Break seconds':<42} {a['break_seconds']:<18.0f} {b['break_seconds']:<18.0f}")
    print(f"{'Shift seconds (excl. breaks)':<42} {a['shift_seconds_excl_breaks']:<18.0f} {b['shift_seconds_excl_breaks']:<18.0f}")
    print(f"{'Visit seconds':<42} {a['visit_seconds']:<18.0f} {b['visit_seconds']:<18.0f}")
    print(f"{'Travel seconds':<42} {a['travel_seconds']:<18.0f} {b['travel_seconds']:<18.0f}")
    print(f"{'Wait seconds (arrive early)':<42} {a['wait_seconds']:<18.0f} {b['wait_seconds']:<18.0f}")
    print()
    print(f"{'Shift time (excl. breaks) [h]':<42} {a['shift_time_excl_breaks_h']:<18.2f} {b['shift_time_excl_breaks_h']:<18.2f}")
    print(f"{'Visit time [h]':<42} {a['visit_time_h']:<18.2f} {b['visit_time_h']:<18.2f}")
    print(f"{'Travel time [h]':<42} {a['travel_time_h']:<18.2f} {b['travel_time_h']:<18.2f}")
    print(f"{'Wait time (arrive early) [h]':<42} {a['wait_time_h']:<18.2f} {b['wait_time_h']:<18.2f}")
    print(f"{'Other (unaccounted) [h]':<42} {a['other_time_h']:<18.2f} {b['other_time_h']:<18.2f}")
    print()
    print(f"{'  -> Empty-shift capacity [h] (shifts with 0 visits)':<42} {a['empty_shift_capacity_min']/60:<18.2f} {b['empty_shift_capacity_min']/60:<18.2f}")
    print(f"{'  -> Other on used shifts [h] (should be ~0)':<42} {a['other_on_used_shifts_min']/60:<18.2f} {b['other_on_used_shifts_min']/60:<18.2f}")
    print()
    print(f"{'Visit count':<42} {a['visit_count']:<18} {b['visit_count']:<18}")
    print(f"{'Shift count':<42} {a['shift_count']:<18} {b['shift_count']:<18}")
    print(f"{'Shifts with ≥1 visit':<42} {a['shift_count_with_visits']:<18} {b['shift_count_with_visits']:<18}")
    print(f"{'Empty shifts (0 visits, break-only, 0 travel)':<42} {a['shift_count_no_visits']:<18} {b['shift_count_no_visits']:<18}")
    print()
    print(f"{'Efficiency % = visit_s / (shift_s - break_s)':<42} {a['efficiency_pct']:<18.1f} {b['efficiency_pct']:<18.1f}")
    print(f"{'Efficiency % (shifts with ≥1 visit only)':<42} {a['efficiency_pct_shifts_with_visits_only']:<18.1f} {b['efficiency_pct_shifts_with_visits_only']:<18.1f}")
    print("=" * 72)
    print()
    print("Formula: efficiency_pct = visit_seconds / (shift_seconds - break_seconds) * 100")
    print("  shift_seconds = clock span from shift start to end (endLocationArrivalTime).")
    print("  break_seconds = sum of break durations in itinerary.")
    print("  visit_seconds = sum of effectiveServiceDuration over all visits.")
    print("  Wait = sum over visits of max(0, startServiceTime - arrivalTime) [arrive early for time window].")
    print("  Other = (shift_s - break_s) - visit_s - travel_s - wait_s.")
    print("  Empty shifts = itinerary has only BREAK, no VISITs; metrics.totalTravelDistanceMeters=0.")
    print("  Other = empty-shift capacity (those shifts) + other_on_used_shifts (should be ~0).")
    print("  (Negative other_on_used_shifts can be timing/rounding or shift-end definition.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
