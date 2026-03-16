#!/usr/bin/env python3
"""
FSR workaround: split multi-day solution by day, build pinned per-day input,
POST each day as new route plan, aggregate results and report efficiency.

Usage:
  python run_per_day_workaround.py
  python run_per_day_workaround.py --dry-run   # build inputs only, do not POST
  python run_per_day_workaround.py --days 3   # run first 3 days only (for testing)

Reads: fixed/from-patch-reduced/export-field-service-routing-5ff46c3d-*-output.json (solution)
       fixed/from-patch-reduced/input-only-used-shifts.json (full input)
       hourly/export-field-service-routing-v1-eb827631-*-input.json (reference config)

Writes: fixed/per-day-workaround/input-{date}.json, output-{date}.json
"""

import argparse
import copy
import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
if ROOT.name == "scripts":
    ROOT = ROOT.parent
SOLUTION_PATH = ROOT / "fixed/from-patch-reduced/export-field-service-routing-5ff46c3d-f7c3-40bd-9428-5ee24fc5bcd9-output.json"
INPUT_PATH = ROOT / "fixed/from-patch-reduced/input-only-used-shifts.json"
REFERENCE_CONFIG = ROOT / "hourly/export-field-service-routing-v1-eb827631-6657-4c4f-948f-0c8aeceacd62-input.json"
OUT_DIR = ROOT / "fixed/per-day-workaround"

TIMEFOLD_BASE = "https://app.timefold.ai/api/models/field-service-routing/v1/route-plans"
API_KEY = os.environ.get("TIMEFOLD_API_KEY")
HEADERS = {"Content-Type": "application/json", "X-API-KEY": API_KEY or ""}

# Reuse efficiency aggregation and duration parsing from compare script
sys.path.insert(0, str(DIR))
from compare_full_vs_from_patch import aggregate as aggregate_metrics, parse_duration_seconds  # noqa: E402
from datetime import datetime, timedelta


def visit_pinning_from_solution(solution: dict) -> dict[str, str]:
    """Return visit_id -> minStartTravelTime (ISO) from solution itinerary."""
    out = solution.get("modelOutput") or solution.get("model_output") or {}
    result: dict[str, str] = {}
    for v in out.get("vehicles") or []:
        for s in v.get("shifts") or []:
            for item in s.get("itinerary") or []:
                if isinstance(item, dict) and item.get("kind") == "VISIT":
                    vid = item.get("id")
                    mst = item.get("minStartTravelTime")
                    if vid and mst:
                        result[vid] = mst
    return result


def visit_start_times_from_solution(solution: dict) -> dict[str, tuple[str, str]]:
    """Return visit_id -> (startServiceTime, effectiveServiceDuration) from solution."""
    out = solution.get("modelOutput") or solution.get("model_output") or {}
    result: dict[str, tuple[str, str]] = {}
    for v in out.get("vehicles") or []:
        for s in v.get("shifts") or []:
            for item in s.get("itinerary") or []:
                if isinstance(item, dict) and item.get("kind") == "VISIT":
                    vid = item.get("id")
                    st = item.get("startServiceTime")
                    dur = item.get("effectiveServiceDuration") or "PT0S"
                    if vid and st:
                        result[vid] = (st, dur)
    return result


def per_day_data_from_solution(solution: dict) -> tuple[list[str], dict[str, set[str]], dict[str, set[tuple[str, str]]]]:
    """
    Returns (sorted_dates, visit_ids_by_date, shift_ids_by_date).
    shift_ids_by_date[date] = set of (vehicle_id, shift_id).
    """
    out = solution.get("modelOutput") or solution.get("model_output") or {}
    visit_by_date: dict[str, set[str]] = {}
    shift_by_date: dict[str, set[tuple[str, str]]] = {}

    for v in out.get("vehicles") or []:
        vid = v.get("id")
        if not vid:
            continue
        for s in v.get("shifts") or []:
            sid = s.get("id")
            start = s.get("startTime") or ""
            if not sid or not start:
                continue
            d = start[:10]
            shift_by_date.setdefault(d, set()).add((vid, sid))
            for item in s.get("itinerary") or []:
                if isinstance(item, dict) and item.get("kind") == "VISIT":
                    visit_id = item.get("id")
                    st = (item.get("startServiceTime") or "")[:10]
                    if visit_id and st:
                        visit_by_date.setdefault(st, set()).add(visit_id)

    dates = sorted(set(visit_by_date.keys()) | set(shift_by_date.keys()))
    return dates, visit_by_date, shift_by_date


def filter_visit_for_day(
    visit: dict, date: str, fallback_start_end: tuple[str, str] | None = None
) -> dict | None:
    """
    Return a copy of visit with only time windows that match date.
    If no window matches and fallback_start_end is (minStartTime, maxEndTime), use that as single window.
    """
    tws = visit.get("timeWindows") or []
    matching = [tw for tw in tws if (tw.get("minStartTime") or "")[:10] == date]
    if not matching and fallback_start_end:
        min_start, max_end = fallback_start_end
        matching = [{"minStartTime": min_start, "maxEndTime": max_end}]
    if not matching:
        return None
    v = copy.deepcopy(visit)
    v["timeWindows"] = matching
    return v


def build_day_input(
    full_input: dict,
    solution: dict,
    date: str,
    visit_ids: set[str],
    shift_pairs: set[tuple[str, str]],
    pinning: dict[str, str],
    visit_start_times: dict[str, tuple[str, str]],
) -> dict:
    """Build modelInput for one day: only those visits (filtered timeWindows) and those shifts; add pinning."""
    mi = (full_input.get("modelInput") or full_input).copy()
    visits_full = {v["id"]: v for v in (mi.get("visits") or []) if v.get("id")}
    vehicles_full = list(mi.get("vehicles") or [])

    # Visits: only on this day, filter timeWindows (or synthetic from solution), add pinning
    day_visits = []
    for vid in visit_ids:
        v = visits_full.get(vid)
        if not v:
            continue
        fallback = None
        if vid in visit_start_times:
            st, dur = visit_start_times[vid]
            try:
                dt = datetime.fromisoformat(st.replace("Z", "+00:00"))
                dur_sec = parse_duration_seconds(dur or "PT0M") or 1800
                end_dt = dt + timedelta(seconds=dur_sec)
                fallback = (dt.isoformat(), end_dt.isoformat())
            except Exception:
                pass
        v_day = filter_visit_for_day(v, date, fallback)
        if not v_day:
            continue
        v_day["pinningRequested"] = True
        if vid in pinning:
            v_day["minStartTravelTime"] = pinning[vid]
        day_visits.append(v_day)

    # Vehicles: only those with at least one shift in shift_pairs; only those shifts
    day_vehicles = []
    for veh in vehicles_full:
        vid = veh.get("id")
        shifts = veh.get("shifts") or []
        keep_shifts = [s for s in shifts if (vid, s.get("id")) in shift_pairs]
        if not keep_shifts:
            continue
        day_vehicles.append({**veh, "shifts": keep_shifts})

    return {"visits": day_visits, "vehicles": day_vehicles}


def post_and_wait(payload: dict, timeout_sec: int = 600, poll_interval: int = 15) -> str | None:
    """POST route plan, poll until SOLVING_COMPLETED or SOLVING_FAILED; return route plan id or None."""
    try:
        r = requests.post(TIMEFOLD_BASE, headers=HEADERS, json=payload, timeout=30)
    except Exception as e:
        print(f"  POST error: {e}", file=sys.stderr)
        return None
    if r.status_code not in (200, 201, 202):
        print(f"  POST {r.status_code}: {r.text[:500]}", file=sys.stderr)
        return None
    body = r.json()
    plan_id = body.get("id") or body.get("parentId") or body.get("originId")
    if not plan_id:
        print("  No id in response", file=sys.stderr)
        return None

    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            r2 = requests.get(f"{TIMEFOLD_BASE}/{plan_id}/metadata", headers=HEADERS, timeout=30)
        except Exception as e:
            print(f"  GET metadata error: {e}", file=sys.stderr)
            time.sleep(poll_interval)
            continue
        if r2.status_code != 200:
            time.sleep(poll_interval)
            continue
        meta = r2.json()
        status = meta.get("solverStatus") or ""
        if status == "SOLVING_COMPLETED":
            return plan_id
        if status in ("SOLVING_FAILED", "DATASET_INVALID"):
            print(f"  Solver status: {status}", file=sys.stderr)
            return None
        time.sleep(poll_interval)
    print("  Timeout waiting for completion", file=sys.stderr)
    return None


def get_solution(plan_id: str) -> dict | None:
    """GET full solution (modelOutput + kpis) for route plan."""
    try:
        r = requests.get(f"{TIMEFOLD_BASE}/{plan_id}", headers=HEADERS, timeout=60)
    except Exception as e:
        print(f"  GET error: {e}", file=sys.stderr)
        return None
    if r.status_code != 200:
        print(f"  GET {r.status_code}", file=sys.stderr)
        return None
    return r.json()


def main() -> int:
    ap = argparse.ArgumentParser(description="Per-day FSR workaround: split, pin, POST each day, aggregate efficiency.")
    ap.add_argument("--dry-run", action="store_true", help="Only build per-day inputs, do not POST.")
    ap.add_argument("--days", type=int, default=0, help="Limit to first N days (0 = all).")
    ap.add_argument("--solution", type=Path, default=SOLUTION_PATH, help="Multi-day solution JSON.")
    ap.add_argument("--input", type=Path, default=INPUT_PATH, help="Full input JSON (modelInput).")
    ap.add_argument("--reference", type=Path, default=REFERENCE_CONFIG, help="Reference for config (run, model, maps).")
    args = ap.parse_args()

    if not API_KEY and not args.dry_run:
        print("Error: set TIMEFOLD_API_KEY when running without --dry-run", file=sys.stderr)
        return 1
    if not args.solution.exists():
        print(f"Error: solution not found {args.solution}", file=sys.stderr)
        return 1
    if not args.input.exists():
        print(f"Error: input not found {args.input}", file=sys.stderr)
        return 1

    with open(args.solution) as f:
        solution = json.load(f)
    with open(args.input) as f:
        full_input = json.load(f)
    with open(args.reference) as f:
        ref = json.load(f)
    config = ref.get("config", {}).copy()
    # Shorter termination per day
    if "run" not in config:
        config["run"] = {}
    config["run"]["termination"] = {"spentLimit": "PT5M"}
    config["run"]["maxThreadCount"] = 4

    dates, visit_by_date, shift_by_date = per_day_data_from_solution(solution)
    if args.days > 0:
        dates = dates[: args.days]
    pinning = visit_pinning_from_solution(solution)
    visit_start_times = visit_start_times_from_solution(solution)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    all_aggregates: list[dict] = []
    day_outputs: list[dict] = []

    for i, date in enumerate(dates):
        visit_ids = visit_by_date.get(date, set())
        shift_pairs = shift_by_date.get(date, set())
        if not visit_ids or not shift_pairs:
            print(f"  {date}: skip (no visits or no shifts)")
            continue

        model_input = build_day_input(
            full_input, solution, date, visit_ids, shift_pairs, pinning, visit_start_times
        )
        n_visits = len(model_input["visits"])
        n_shifts = sum(len(v.get("shifts") or []) for v in model_input["vehicles"])
        n_vehicles = len(model_input["vehicles"])

        in_path = OUT_DIR / f"input-{date}.json"
        with open(in_path, "w") as f:
            json.dump({"modelInput": model_input}, f, indent=2)
        print(f"  {date}: {n_visits} visits, {n_vehicles} vehicles, {n_shifts} shifts -> {in_path.name}")

        if args.dry_run:
            continue

        config["run"]["name"] = f"per-day-workaround-{date}"
        payload = {"config": config, "modelInput": model_input}

        plan_id = post_and_wait(payload, timeout_sec=420, poll_interval=10)
        if not plan_id:
            print(f"  {date}: POST/wait failed")
            continue

        sol = get_solution(plan_id)
        if not sol:
            print(f"  {date}: GET solution failed")
            continue

        out_path = OUT_DIR / f"output-{date}.json"
        with open(out_path, "w") as f:
            json.dump(sol, f, indent=2)
        print(f"  {date}: saved -> {out_path.name}")

        agg = aggregate_metrics(sol)
        all_aggregates.append(agg)
        day_outputs.append(sol)

    if args.dry_run:
        print("Dry-run done. Run without --dry-run to POST and collect results.")
        return 0

    if not all_aggregates:
        print("No day results to aggregate.")
        return 1

    # Aggregate across days: sum shift/visit/travel/wait seconds
    total_shift_sec = sum(a["shift_seconds"] for a in all_aggregates)
    total_break_sec = sum(a["break_seconds"] for a in all_aggregates)
    total_visit_sec = sum(a["visit_seconds"] for a in all_aggregates)
    total_travel_sec = sum(a["travel_seconds"] for a in all_aggregates)
    total_wait_sec = sum(a["wait_seconds"] for a in all_aggregates)
    total_visits = sum(a["visit_count"] for a in all_aggregates)
    total_shifts = sum(a["shift_count"] for a in all_aggregates)
    total_shifts_with_visits = sum(a["shift_count_with_visits"] for a in all_aggregates)
    shift_sec_excl_breaks = total_shift_sec - total_break_sec
    efficiency_pct = (total_visit_sec / shift_sec_excl_breaks * 100) if shift_sec_excl_breaks > 0 else 0.0

    # Shift-count with visits only (no empty shifts in workaround)
    shift_sec_used = sum(
        a["shift_seconds"] - a["break_seconds"]
        for a in all_aggregates
    )
    efficiency_used_only = (total_visit_sec / shift_sec_used * 100) if shift_sec_used > 0 else 0.0

    print()
    print("=" * 60)
    print("PER-DAY WORKAROUND – EFFICIENCY REPORT")
    print("=" * 60)
    print(f"  Days run:           {len(all_aggregates)}")
    print(f"  Total visits:       {total_visits}")
    print(f"  Total shifts:       {total_shifts} (all with visits – no empty shifts)")
    print(f"  Shift time (excl breaks): {shift_sec_excl_breaks / 3600:.2f} h")
    print(f"  Visit time:         {total_visit_sec / 3600:.2f} h")
    print(f"  Travel time:        {total_travel_sec / 3600:.2f} h")
    print(f"  Wait time:          {total_wait_sec / 3600:.2f} h")
    print(f"  Efficiency:         {efficiency_pct:.1f}%  (visit time / shift time excl. breaks)")
    print(f"  (Used shifts only) {efficiency_used_only:.1f}%")
    print("=" * 60)

    report_path = OUT_DIR / "efficiency_report.json"
    report = {
        "days_run": len(all_aggregates),
        "total_visits": total_visits,
        "total_shifts": total_shifts,
        "total_shift_seconds_excl_breaks": shift_sec_excl_breaks,
        "total_visit_seconds": total_visit_sec,
        "total_travel_seconds": total_travel_sec,
        "total_wait_seconds": total_wait_sec,
        "efficiency_pct": round(efficiency_pct, 2),
        "per_day_aggregates": [
            {
                "shift_count": a["shift_count"],
                "visit_count": a["visit_count"],
                "efficiency_pct": round(a["efficiency_pct"], 2),
            }
            for a in all_aggregates
        ],
    }
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Report saved -> {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
