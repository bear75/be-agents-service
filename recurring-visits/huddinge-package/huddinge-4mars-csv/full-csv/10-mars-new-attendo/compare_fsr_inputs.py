#!/usr/bin/env python3
"""
Compare dashboard (seed + buildTimefoldModelInput) FSR vs script (attendo_4mars_to_fsr.py) FSR
when both use the same source CSV and same planning window.

Usage:
  python compare_fsr_inputs.py
  python compare_fsr_inputs.py --dashboard dashboard_fsr.json --script script_fsr_no_extra_vehicles.json

Reads dashboard_fsr.json and script_fsr_*.json from this folder (or paths given),
extracts modelInput from each, and prints a side-by-side comparison.
Also checks that dashboard visits have time window length >= service duration (no Timefold warnings).
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def _iso_duration_to_minutes(d: str) -> int:
    """Parse ISO 8601 duration (PTxHyM or PTxH or PTyM) to minutes."""
    if not d:
        return 0
    h = 0
    m = 0
    # PT1H30M -> hours=1, minutes=30
    hm = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", d.strip().upper())
    if hm:
        h = int(hm.group(1) or 0)
        m = int(hm.group(2) or 0)
    return h * 60 + m


def _window_span_minutes(tw: dict) -> int:
    """Return (maxEndTime - minStartTime) in minutes from ISO strings."""
    min_s = tw.get("minStartTime") or ""
    max_e = tw.get("maxEndTime") or ""
    if not min_s or not max_e:
        return 0
    try:
        start = datetime.fromisoformat(min_s.replace("Z", "+00:00"))
        end = datetime.fromisoformat(max_e.replace("Z", "+00:00"))
        return int((end - start).total_seconds() / 60)
    except (ValueError, TypeError):
        return 0


def get_model_input(path: Path) -> dict:
    """Load JSON and return the modelInput object (top-level or under key)."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("modelInput", data)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare dashboard vs script FSR inputs")
    parser.add_argument(
        "--dashboard",
        type=Path,
        default=Path(__file__).parent / "dashboard_fsr.json",
        help="Dashboard FSR JSON (from E2E_DUMP_JSON)",
    )
    parser.add_argument(
        "--script",
        type=Path,
        default=Path(__file__).parent / "script_fsr_no_extra_vehicles.json",
        help="Script FSR JSON (attendo_4mars_to_fsr.py with --no-supplementary-vehicles)",
    )
    args = parser.parse_args()

    if not args.dashboard.exists():
        print(f"Dashboard file not found: {args.dashboard}", file=sys.stderr)
        return 1
    if not args.script.exists():
        print(f"Script file not found: {args.script}", file=sys.stderr)
        return 1

    dash = get_model_input(args.dashboard)
    script = get_model_input(args.script)

    def visit_count(mi: dict) -> int:
        stand = len(mi.get("visits") or [])
        groups = mi.get("visitGroups") or []
        in_groups = sum(len(g.get("visits") or []) for g in groups)
        return stand + in_groups

    def vehicle_shift_count(mi: dict) -> tuple[int, int]:
        vehicles = mi.get("vehicles") or []
        shifts = sum(len(v.get("shifts") or []) for v in vehicles)
        return len(vehicles), shifts

    # Counts
    dash_visits = visit_count(dash)
    script_visits = visit_count(script)
    dash_vehicles, dash_shifts = vehicle_shift_count(dash)
    script_vehicles, script_shifts = vehicle_shift_count(script)
    dash_groups = len(dash.get("visitGroups") or [])
    script_groups = len(script.get("visitGroups") or [])

    print("=" * 60)
    print("FSR comparison (same CSV, same planning window)")
    print("=" * 60)
    print(f"{'Metric':<35} {'Dashboard':>12} {'Script':>12}")
    print("-" * 60)
    print(f"{'Total visits':<35} {dash_visits:>12} {script_visits:>12}")
    print(f"{'Visit groups':<35} {dash_groups:>12} {script_groups:>12}")
    print(f"{'Vehicles':<35} {dash_vehicles:>12} {script_vehicles:>12}")
    print(f"{'Shifts':<35} {dash_shifts:>12} {script_shifts:>12}")
    print("=" * 60)

    # Check dashboard: every visit has time window >= service duration (seed fix)
    visits = list(dash.get("visits") or [])
    for g in dash.get("visitGroups") or []:
        visits.extend(g.get("visits") or [])
    narrow = []
    for v in visits:
        dur_iso = v.get("serviceDuration") or "PT0M"
        dur_min = _iso_duration_to_minutes(dur_iso)
        for tw in v.get("timeWindows") or []:
            span = _window_span_minutes(tw)
            if 0 < dur_min and span < dur_min:
                narrow.append((v.get("id"), dur_iso, span, dur_min))
    if narrow:
        print("\n⚠️  Dashboard visits with time window smaller than duration (Timefold would warn):")
        for vid, dur_iso, span, dur_min in narrow[:10]:
            print(f"   {vid}  duration={dur_iso} ({dur_min}min)  window_span={span}min")
        if len(narrow) > 10:
            print(f"   ... and {len(narrow) - 10} more")
    else:
        print("\n✅ All dashboard visits have time window >= service duration (no narrow-window warnings).")

    # Planning window
    pw_d = dash.get("planningWindow") or {}
    pw_s = script.get("planningWindow") or {}
    print(f"\nPlanning window:")
    print(f"  Dashboard: {pw_d.get('startDate')} .. {pw_d.get('endDate')}")
    print(f"  Script:    {pw_s.get('startDate')} .. {pw_s.get('endDate')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
