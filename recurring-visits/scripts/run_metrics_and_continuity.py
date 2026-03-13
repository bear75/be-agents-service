#!/usr/bin/env python3
"""
Run metrics.py and continuity_report.py on the same FSR input/output and write a combined run summary.

Produces:
  - Metrics (efficiency, unassigned) via metrics.py --save <out_dir>
  - Continuity report (unique count, CCI) via continuity_report.py --report <out_dir>/continuity.csv
  - run_summary_<id>.json and run_summary_<id>.md with: efficiency_pct, unassigned_visits,
    average_unique_count, average_cci (and route_plan_id).

Usage:
  python run_metrics_and_continuity.py --input path/to/input.json --output path/to/output.json --out-dir path/to/out
  python run_metrics_and_continuity.py --input in.json --output out.json --out-dir . --only-kundnr
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


def _script_dir() -> Path:
    """Directory containing this script (and metrics.py, continuity_report.py)."""
    return Path(__file__).resolve().parent


def run_metrics(input_path: Path, output_path: Path, save_dir: Path) -> dict | None:
    """Run metrics.py and return the latest saved metrics JSON dict, or None on failure."""
    cmd = [
        sys.executable,
        str(_script_dir() / "metrics.py"),
        str(output_path),
        "--input",
        str(input_path),
        "--save",
        str(save_dir),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=_script_dir())
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return None
    # Find latest metrics_*.json in save_dir
    jsons = list(save_dir.glob("metrics_*.json"))
    if not jsons:
        return None
    latest = max(jsons, key=lambda p: p.stat().st_mtime)
    with open(latest, encoding="utf-8") as f:
        return json.load(f)


def run_continuity_report(
    input_path: Path,
    output_path: Path,
    report_path: Path,
    only_kundnr: bool = False,
) -> bool:
    """Run continuity_report.py writing CSV to report_path. Returns True on success."""
    cmd = [
        sys.executable,
        str(_script_dir() / "continuity_report.py"),
        "--input",
        str(input_path),
        "--output",
        str(output_path),
        "--report",
        str(report_path),
    ]
    if only_kundnr:
        cmd.append("--only-kundnr")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=_script_dir())
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return False
    return True


def continuity_summary_from_csv(report_path: Path) -> tuple[float, float | None]:
    """
    Read continuity CSV and return (average_unique_count, average_cci or None if no cci column).
    """
    if not report_path.exists():
        return 0.0, None
    with open(report_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        return 0.0, None
    # continuity = unique count column
    continuity_vals = []
    cci_vals: list[float] = []
    for r in rows:
        c = r.get("continuity", "")
        if c != "":
            try:
                continuity_vals.append(int(c))
            except ValueError:
                pass
        cci = r.get("cci", "")
        if cci != "":
            try:
                cci_vals.append(float(cci))
            except ValueError:
                pass
    avg_unique = sum(continuity_vals) / len(continuity_vals) if continuity_vals else 0.0
    avg_cci = sum(cci_vals) / len(cci_vals) if cci_vals else None
    return avg_unique, avg_cci


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run metrics + continuity report and write combined run summary.",
    )
    parser.add_argument("--input", type=Path, required=True, help="FSR input JSON")
    parser.add_argument("--output", type=Path, required=True, help="FSR output JSON")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("."),
        help="Directory for metrics save, continuity CSV, and run_summary output (default: .)",
    )
    parser.add_argument(
        "--id",
        type=str,
        default=None,
        help="Override run summary filename suffix (default: from output JSON route_plan_id)",
    )
    parser.add_argument(
        "--only-kundnr",
        action="store_true",
        help="Pass --only-kundnr to continuity_report.py",
    )
    args = parser.parse_args()

    # Resolve to absolute so subprocess cwd=script_dir does not break relative paths
    args.input = args.input.resolve()
    args.output = args.output.resolve()
    args.out_dir = args.out_dir.resolve()

    if not args.input.exists():
        print(f"Error: input not found: {args.input}", file=sys.stderr)
        return 1
    if not args.output.exists():
        print(f"Error: output not found: {args.output}", file=sys.stderr)
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)
    continuity_csv = args.out_dir / "continuity.csv"

    # Run metrics (saves to out_dir)
    metrics_data = run_metrics(args.input, args.output, args.out_dir)
    if not metrics_data:
        print("Error: metrics.py failed or produced no JSON", file=sys.stderr)
        return 1

    # Run continuity report
    if not run_continuity_report(
        args.input,
        args.output,
        continuity_csv,
        only_kundnr=args.only_kundnr,
    ):
        print("Error: continuity_report.py failed", file=sys.stderr)
        return 1

    avg_unique, avg_cci = continuity_summary_from_csv(continuity_csv)
    route_id = args.id or metrics_data.get("route_plan_id", "unknown")
    rid_safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in str(route_id))[:32]

    summary = {
        "route_plan_id": route_id,
        "efficiency_pct": metrics_data.get("efficiency_pct"),
        "field_efficiency_pct": metrics_data.get("field_efficiency_pct"),
        "unassigned_visits": metrics_data.get("unassigned_visits"),
        "average_unique_count": round(avg_unique, 2),
        "average_cci": round(avg_cci, 4) if avg_cci is not None else None,
    }

    summary_json = args.out_dir / f"run_summary_{rid_safe}.json"
    with open(summary_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Wrote {summary_json}")

    summary_md = args.out_dir / f"run_summary_{rid_safe}.md"
    lines = [
        "# Run summary",
        "",
        f"- **Plan ID:** {route_id}",
        f"- **Efficiency (visit / assignable, excl. idle):** {summary['efficiency_pct']}%",
        f"- **Field efficiency (visit / (visit+travel), no wait):** {(str(summary['field_efficiency_pct']) + '%') if summary.get('field_efficiency_pct') is not None else '—'}",
        f"- **Unassigned visits:** {summary['unassigned_visits']}",
        f"- **Average unique caregivers per client:** {summary['average_unique_count']}",
    ]
    if summary["average_cci"] is not None:
        lines.append(f"- **Average CCI:** {summary['average_cci']}")
    lines.append("")
    with open(summary_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {summary_md}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
