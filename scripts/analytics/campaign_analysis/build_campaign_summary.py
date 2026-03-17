#!/usr/bin/env python3
"""
Build SUMMARY.md from campaign_analysis variant dirs (metrics_*.json + continuity).
Run from be-agent-service root or from this directory.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

VARIANTS = ["baseline_data_final", "pool3_required", "pool5_required", "pool8_required"]
GOAL_EFF = 70.0  # field efficiency % (CAMPAIGN_MATRIX: 73%+)
GOAL_CONTINUITY = 11.0  # avg distinct caregivers per client (≤11)
GOAL_UNASSIGNED_PCT = 5.0  # unassigned < 5%


def find_latest_metrics(dir_path: Path) -> dict | None:
    metrics_files = list(dir_path.glob("metrics_*.json"))
    if not metrics_files:
        return None
    latest = max(metrics_files, key=lambda p: p.stat().st_mtime)
    with open(latest, encoding="utf-8") as f:
        return json.load(f)


def continuity_avg_from_csv(csv_path: Path) -> float | None:
    if not csv_path.exists():
        return None
    values = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            c = (row.get("continuity") or "").strip()
            if c.isdigit():
                values.append(int(c))
    return sum(values) / len(values) if values else None


def continuity_avg_from_summary(txt_path: Path) -> float | None:
    if not txt_path.exists():
        return None
    text = txt_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if "Average unique count:" in line or "avg" in line.lower():
            parts = line.split(":")
            if len(parts) >= 2:
                try:
                    return float(parts[-1].strip())
                except ValueError:
                    pass
    return None


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    lines = [
        "# v3 campaign – fetch & analyze all jobs",
        "",
        "**Goals:** Field efficiency **≥70%** (stretch 73%+), continuity avg ≤11, unassigned <5%.",
        "",
        "| Variant | Plan ID | Assigned | Unassigned | Unassigned % | Field eff. | Continuity avg | ≤11 | Eff. ≥70% |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    total_visits = 7653  # from input
    rows = []
    for variant in VARIANTS:
        d = script_dir / variant
        if not d.is_dir():
            rows.append((variant, "—", "—", "—", "—", "—", "—", "—", "—"))
            continue
        metrics = find_latest_metrics(d)
        cont_avg = continuity_avg_from_csv(d / "continuity.csv") or continuity_avg_from_summary(d / "continuity_summary.txt")
        if not metrics:
            rows.append((variant, "—", "—", "—", "—", "—", f"{cont_avg:.2f}" if cont_avg else "—", "—", "—"))
            continue
        plan_id = (metrics.get("route_plan_id") or "—").split("-")[0]
        assigned = metrics.get("total_visits_assigned", 0)
        unassigned = metrics.get("unassigned_visits", 0)
        unass_pct = (100.0 * unassigned / total_visits) if total_visits else 0
        field_eff = metrics.get("field_efficiency_pct")
        eff_str = f"{field_eff:.2f}%" if field_eff is not None else "—"
        cont_str = f"{cont_avg:.2f}" if cont_avg is not None else "—"
        goal_cont = "Yes" if cont_avg is not None and cont_avg <= GOAL_CONTINUITY else "No"
        goal_eff = "Yes" if field_eff is not None and field_eff >= GOAL_EFF else "No"
        rows.append((variant, plan_id, f"{assigned:,}", f"{unassigned:,}", f"{unass_pct:.1f}%", eff_str, cont_str, goal_cont, goal_eff))

    for variant, plan_id, assigned, unassigned, unass_pct, eff_str, cont_str, goal_cont, goal_eff in rows:
        lines.append(f"| **{variant}** | {plan_id} | {assigned} | {unassigned} | {unass_pct} | {eff_str} | {cont_str} | {goal_cont} | {goal_eff} |")

    lines.extend([
        "",
        "**Notes:**",
        "- Per-job outputs: `baseline_data_final/`, `pool3_required/`, `pool5_required/`, `pool8_required/` (output.json, metrics_*.json, continuity.csv, empty_shifts.txt).",
        "- To re-fetch: `./scripts/analytics/campaign_analysis/fetch_all_campaign_runs.sh` (requires TIMEFOLD_API_KEY).",
        "",
    ])
    out = script_dir / "SUMMARY.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
