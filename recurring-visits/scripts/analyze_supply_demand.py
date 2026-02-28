#!/usr/bin/env python3
"""
Analyze Timefold FSR output: supply (shifts) vs demand (visits), empty shifts, unassigned.
Produces a markdown report with where supply is low/high and how to assign all visits
or remove/move shifts.

Usage:
  python analyze_supply_demand.py output.json [input.json]
  python analyze_supply_demand.py output.json input.json --report report.md
"""

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def parse_iso_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def date_str(dt: datetime | None) -> str:
    if not dt:
        return "?"
    return dt.strftime("%Y-%m-%d")


def run_analysis(output_path: Path, input_path: Path | None) -> str:
    with open(output_path) as f:
        out = json.load(f)

    mo = out.get("modelOutput") or out
    kpis = out.get("kpis") or {}
    input_metrics = out.get("inputMetrics") or {}

    unassigned = list(mo.get("unassignedVisits") or [])
    n_unassigned = kpis.get("totalUnassignedVisits", len(unassigned))
    n_assigned = kpis.get("totalAssignedVisits", 0)
    n_total_visits = input_metrics.get("visits") or (n_assigned + n_unassigned)
    n_shifts_input = input_metrics.get("vehicleShifts") or 0
    n_vehicles = input_metrics.get("vehicles") or 0

    # Per-shift visit counts and empty shifts
    shift_info: list[tuple[str, str, str, int, str]] = []  # vehicle_id, shift_id, date, n_visits, start_time
    empty_shifts: list[tuple[str, str, str]] = []  # vehicle_id, shift_id, date

    for v in mo.get("vehicles") or []:
        vehicle_id = v.get("id", "?")
        for s in v.get("shifts") or []:
            shift_id = s.get("id", "?")
            start_time = s.get("startTime", "")
            dt = parse_iso_dt(start_time)
            date = date_str(dt)
            itinerary = s.get("itinerary") or []
            visits = [x for x in itinerary if isinstance(x, dict) and x.get("kind") == "VISIT"]
            n_visits = len(visits)
            shift_info.append((vehicle_id, shift_id, date, n_visits, start_time))
            if n_visits == 0:
                empty_shifts.append((vehicle_id, shift_id, date))

    # By date: supply (shifts, empty count) and demand (assigned visits)
    by_date: dict[str, dict] = defaultdict(lambda: {"shifts": 0, "empty": 0, "visits": 0, "vehicle_names": set()})
    for vehicle_id, _sid, date, n_visits, _st in shift_info:
        by_date[date]["shifts"] += 1
        by_date[date]["visits"] += n_visits
        by_date[date]["vehicle_names"].add(vehicle_id)
        if n_visits == 0:
            by_date[date]["empty"] += 1

    # Sort by date
    dates_sorted = sorted(by_date.keys())

    # High/low supply: by visits per shift (utilization)
    shifts_with_visits = [(v, s, d, n) for v, s, d, n, _ in shift_info if n > 0]
    shifts_with_visits.sort(key=lambda x: -x[3])
    top_load = shifts_with_visits[:20]
    low_load = [x for x in shift_info if 0 < x[3] <= 3]  # 1-3 visits

    # Build report
    lines = [
        "# Supply vs demand analysis",
        "",
        f"**Output:** `{output_path.name}`",
        f"**Input:** `{input_path.name}`" if input_path else "",
        "",
        "## 1. Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total visits (input) | {n_total_visits} |",
        f"| Assigned visits | {n_assigned} |",
        f"| **Unassigned visits** | **{n_unassigned}** |",
        f"| Total shifts (input) | {n_shifts_input} |",
        f"| Vehicles | {n_vehicles} |",
        f"| Empty shifts (0 visits) | {len(empty_shifts)} |",
        "",
        "---",
        "",
        "## 2. Where supply is high vs low (by day)",
        "",
        "Supply = shifts on that day. Demand = assigned visits on that day. Empty = shifts with 0 visits.",
        "",
        "| Date | Shifts | Empty | Assigned visits | Visits/shift (avg) |",
        "|------|--------|-------|-----------------|---------------------|",
    ]

    for d in dates_sorted:
        row = by_date[d]
        n_sh = row["shifts"]
        n_emp = row["empty"]
        n_vis = row["visits"]
        avg = f"{n_vis / n_sh:.1f}" if n_sh else "—"
        lines.append(f"| {d} | {n_sh} | {n_emp} | {n_vis} | {avg} |")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Empty shifts (remove or move)",
        "",
        f"**{len(empty_shifts)} shifts** have no visits. These can be removed or moved to days with high demand.",
        "",
    ])

    # Group empty by date
    empty_by_date = defaultdict(list)
    for v, s, d in empty_shifts:
        empty_by_date[d].append((v, s))
    for d in dates_sorted:
        if d in empty_by_date:
            lines.append(f"### {d} ({len(empty_by_date[d])} empty)")
            lines.append("")
            for v, s in sorted(empty_by_date[d]):
                lines.append(f"- `{v}` shift `{s}`")
            lines.append("")

    lines.extend([
        "---",
        "",
        "## 4. Highest-load shifts (supply tight)",
        "",
        "Shifts with the most visits — may need relief or more capacity on those days.",
        "",
        "| Vehicle | Shift | Date | Visits |",
        "|---------|-------|------|--------|",
    ])
    for v, s, d, n in top_load:
        lines.append(f"| {v} | {s} | {d} | {n} |")
    lines.append("")

    lines.extend([
        "---",
        "",
        "## 5. Unassigned visit IDs",
        "",
        f"**{n_unassigned} visits** could not be assigned. To assign all:",
        "",
        "1. **Add shifts** on days where demand exceeds supply (days with many unassigned time windows).",
        "2. **Move shifts** from days with many empty shifts to days with high demand.",
        "3. **Widen time windows** (if care rules allow) so more visits can fit on existing shifts.",
        "4. **Run solver longer** so it can find feasible assignments for tight days.",
        "",
        "Unassigned IDs:",
        "",
        "```",
        ", ".join(unassigned),
        "```",
        "",
        "---",
        "",
        "## 6. Recommendations",
        "",
        "| Goal | Action |",
        "|------|--------|",
        "| Assign all visits | Add shifts on high-demand days, or move empty shifts from low-demand days; re-run solver. |",
        "| Remove waste | Delete or deactivate the empty shifts listed in §3 (or move them to other days). |",
        "| Balance load | Consider moving some shifts from days with many empty shifts to days with high visits/shift. |",
        "",
    ])

    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Analyze supply vs demand from Timefold FSR output")
    p.add_argument("output", type=Path, help="Output JSON path")
    p.add_argument("input", type=Path, nargs="?", default=None, help="Input JSON path (optional)")
    p.add_argument("--report", "-o", type=Path, help="Write report to this path (default: stdout)")
    args = p.parse_args()

    if not args.output.exists():
        print(f"Error: output file not found: {args.output}", flush=True)
        return 1

    report = run_analysis(args.output, args.input)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
        print(f"Report written to {args.report}", flush=True)
    else:
        print(report, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
