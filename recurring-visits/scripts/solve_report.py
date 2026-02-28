#!/usr/bin/env python3
"""
Combined solve report: metrics, unassigned analysis, and empty-shifts analysis in one run.

Loads input and output JSON once, then runs:
  1. Metrics (efficiency, cost, time equation, field efficiency %)
  2. Unassigned analysis (supply vs config, visit:travel, by date)
  3. Empty-shifts analysis (empty shifts list, overlap with unassigned)

Usage:
  python solve_report.py solve/output.json --input solve/input.json
  python solve_report.py solve/output.json --input solve/input.json --save metrics/
  python solve_report.py solve/output.json --input solve/input.json --save metrics/ --csv metrics/unassigned.csv
  python solve_report.py solve/output.json --input solve/input.json --exclude-inactive
"""

import argparse
import json
import sys
from pathlib import Path

# Same directory as this script
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from metrics import aggregate, analyze_input, print_report, save_metrics
from analyze_unassigned import run_analysis as run_unassigned_analysis
from analyze_empty_shifts import run_analysis as run_empty_shifts_analysis


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Combined report: metrics + unassigned analysis + empty-shifts analysis.",
    )
    ap.add_argument("output", type=Path, help="Timefold output JSON.")
    ap.add_argument("--input", type=Path, default=None, help="Timefold input JSON (for shift times and analysis).")
    ap.add_argument("--save", type=Path, default=None, help="Directory to save metrics JSON.")
    ap.add_argument("--csv", type=Path, default=None, help="Write unassigned rows to CSV.")
    ap.add_argument(
        "--exclude-inactive",
        action="store_true",
        help="Exclude inactive time from metrics (e.g. for from-patch output).",
    )
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
    elif args.input:
        print(f"Warning: input file not found {args.input}, metrics will use output only.", file=sys.stderr)

    mi = (input_data.get("modelInput") or input_data) if input_data else {}
    mo = output_data.get("modelOutput") or output_data

    # ─── 1. Metrics ─────────────────────────────────────────────────────────
    input_info = analyze_input(args.input) if args.input else None
    agg = aggregate(output_data, input_data, use_depot_end=args.exclude_inactive)
    print_report(agg, input_info, exclude_inactive=args.exclude_inactive)

    if args.save:
        filepath, report_path = save_metrics(agg, input_info, args.save, exclude_inactive=args.exclude_inactive)
        print(f"\nMetrics saved to {filepath}")
        print(f"Report saved to {report_path}")

    # ─── 2. Unassigned analysis ────────────────────────────────────────────
    if mi and mo:
        print()
        unassigned_report, rows_for_csv = run_unassigned_analysis(mi, mo)
        print(unassigned_report)
        if args.csv and rows_for_csv:
            args.csv.parent.mkdir(parents=True, exist_ok=True)
            import csv as csv_mod
            with open(args.csv, "w", newline="") as f:
                w = csv_mod.DictWriter(f, fieldnames=list(rows_for_csv[0].keys()))
                w.writeheader()
                w.writerows(rows_for_csv)
            print(f"Unassigned CSV: {args.csv}")

        # ─── 3. Empty-shifts analysis ───────────────────────────────────────
        print()
        empty_report = run_empty_shifts_analysis(mi, mo)
        print(empty_report)
    else:
        print("\n(Skip unassigned and empty-shifts analysis: no input JSON provided)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
