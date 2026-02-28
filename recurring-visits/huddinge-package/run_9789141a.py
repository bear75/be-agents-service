#!/usr/bin/env python3
"""
One-off: run metrics, analyze_unassigned, and build from-patch for run 9789141a.
Run from huddinge-package: python run_9789141a.py
"""
import json
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parent
SCRIPTS = PKG / "scripts"
sys.path.insert(0, str(SCRIPTS))

OUTPUT_JSON = PKG / "solve/tf/export-field-service-routing-9789141a-f9b9-4dcb-aca6-9eb5c2dbe0eb-output.json"
INPUT_JSON = PKG / "solve/input_20260214_171612.json"
METRICS_DIR = PKG / "metrics"
FROM_PATCH_DIR = PKG / "from-patch"

def main():
    if not OUTPUT_JSON.exists():
        print(f"Missing: {OUTPUT_JSON}", file=sys.stderr)
        return 1
    if not INPUT_JSON.exists():
        print(f"Missing: {INPUT_JSON}", file=sys.stderr)
        return 1
    with open(OUTPUT_JSON) as f:
        output_data = json.load(f)
    with open(INPUT_JSON) as f:
        input_data = json.load(f)

    # 1. Metrics
    from metrics import aggregate, analyze_input, save_metrics, print_report
    input_info = analyze_input(INPUT_JSON)
    agg = aggregate(output_data, input_data)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    filepath, report_path = save_metrics(agg, input_info, METRICS_DIR, exclude_inactive=False)
    print(f"Metrics saved: {filepath}")
    print(f"Report saved: {report_path}")

    # 2. Analyze unassigned
    from analyze_unassigned import (
        parse_iso_dt, parse_duration_seconds, overlap, _visit_window_type,
    )
    mi = input_data.get("modelInput") or input_data
    mo = output_data.get("modelOutput") or output_data
    unassigned_ids = set(str(u) for u in (mo.get("unassignedVisits") or []))
    output_shift_visit_count = {}
    for v in mo.get("vehicles", []):
        for s in v.get("shifts", []):
            sid = s.get("id", "")
            it = s.get("itinerary") or []
            output_shift_visit_count[sid] = sum(1 for x in it if isinstance(x, dict) and x.get("kind") == "VISIT")
    shifts = []
    for v in mi.get("vehicles", []):
        vid = v.get("id", "?")
        for s in v.get("shifts", []):
            sid = s.get("id", "")
            st, et = parse_iso_dt(s.get("minStartTime")), parse_iso_dt(s.get("maxEndTime"))
            if st and et:
                shifts.append((sid, vid, st, et, output_shift_visit_count.get(sid, 0) == 0))
    def get_tws(visit):
        out = []
        for tw in visit.get("timeWindows", []):
            mn, mx = parse_iso_dt(tw.get("minStartTime")), parse_iso_dt(tw.get("maxEndTime"))
            if mn and mx:
                out.append((mn, mx))
        return out
    unassigned_windows = []
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
    from collections import defaultdict
    supply_count = config_count = 0
    by_date = defaultdict(lambda: {"supply": 0, "config": 0, "day": 0, "evening": 0, "both": 0})
    for uid, tw_s, tw_e in unassigned_windows:
        overlapping = [(sid, vid, st, et, is_empty) for sid, vid, st, et, is_empty in shifts if overlap(st, et, tw_s, tw_e)]
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
    total_visit_sec = total_travel_sec = 0.0
    for v in mo.get("vehicles", []):
        for s in v.get("shifts", []):
            it, metrics = s.get("itinerary") or [], s.get("metrics") or {}
            visit_sec = sum(parse_duration_seconds(item.get("effectiveServiceDuration") or "") for item in it if isinstance(item, dict) and item.get("kind") == "VISIT")
            total_visit_sec += visit_sec
            total_travel_sec += parse_duration_seconds(metrics.get("totalTravelTime") or "PT0S")
    field_sec = total_visit_sec + total_travel_sec
    visit_travel_ratio = (total_visit_sec / total_travel_sec) if total_travel_sec > 0 else 0.0
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
        "=" * 60,
    ])
    analyze_path = METRICS_DIR / "analyze_unassigned_9789141a.txt"
    analyze_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Analysis report: {analyze_path}")

    # 3. From-patch
    from build_from_patch import build_patch
    patch = build_patch(output_data, input_data, remove_empty_shifts=True, end_shifts_at_depot=True)
    payload = {"config": {"run": {"name": "from-patch-trim-empty"}}, "patch": patch}
    FROM_PATCH_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FROM_PATCH_DIR / "payload_9789141a.json"
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"From-patch payload: {out_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
