#!/usr/bin/env python3
"""
Nova recurring visits pipeline: CSV -> Expanded CSV -> Timefold FSR JSON.

Same pipeline as Huddinge, with step 1 (expand) adapted to Nova column names.
Uses huddinge-package scripts for expansion logic and JSON generation.

Usage:
  python process_nova.py --weeks 2
  python process_nova.py --weeks 4 --output-dir .
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent
_NOVA_SCRIPTS = _PKG_DIR / "scripts"
_HUDDINGE_SCRIPTS = _PKG_DIR.parent / "huddinge-package" / "scripts"

for d in [_NOVA_SCRIPTS, _HUDDINGE_SCRIPTS]:
    if str(d) not in sys.path:
        sys.path.insert(0, str(d))

from expand_nova_recurring_visits import expand_nova_visits
from csv_to_timefold_fsr import generate_timefold_json


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Process Nova recurring CSV to Timefold FSR JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python process_nova.py --weeks 2
  python process_nova.py --weeks 4 --output-dir /tmp/nova
        """,
    )
    parser.add_argument(
        "--weeks",
        type=int,
        default=2,
        choices=[2, 4],
        help="Planning window in weeks (default: 2)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=_PKG_DIR,
        help="Base output directory (default: package root)",
    )
    parser.add_argument(
        "--start-date",
        default="2026-02-16",
        help="Planning start Monday (default: 2026-02-16)",
    )
    args = parser.parse_args()

    source_dir = args.output_dir / "source"
    expanded_dir = args.output_dir / "expanded"
    solve_dir = args.output_dir / "solve"

    expanded_dir.mkdir(parents=True, exist_ok=True)
    solve_dir.mkdir(parents=True, exist_ok=True)

    input_csv = source_dir / "Nova_Final_Verified_geocoded.csv"
    if not input_csv.exists():
        input_csv = source_dir / "Nova_recurring.csv"
    if not input_csv.exists():
        input_csv = args.output_dir / "Nova_Final_Verified_geocoded.csv"
    if not input_csv.exists():
        input_csv = args.output_dir / "Nova_recurring.csv"
    if not input_csv.exists():
        print("Error: Source CSV not found (tried source/, output-dir/)", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    expanded_csv = expanded_dir / f"nova_{args.weeks}wk_expanded_{ts}.csv"
    output_json = solve_dir / f"input_{ts}.json"

    print("=" * 60)
    print("Nova Recurring Visits Pipeline")
    print("=" * 60)
    print(f"Input:        {input_csv}")
    print(f"Planning:     {args.weeks} weeks from {args.start_date}")
    print()

    # Step 1: Expand (Nova format -> Huddinge expanded format)
    print("[1/2] Expanding recurring visits (Nova format)...")
    try:
        n_expanded = expand_nova_visits(
            input_csv,
            expanded_csv,
            planning_weeks=args.weeks,
            planning_start_date=args.start_date,
            delimiter=";",
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1

    print()

    # Step 2: Generate JSON (uses Nova source for vehicles)
    print("[2/2] Generating Timefold FSR JSON...")
    try:
        payload = generate_timefold_json(
            expanded_csv,
            output_json,
            planning_weeks=args.weeks,
            planning_start_date=args.start_date,
            run_name=f"Nova {args.weeks}-Week Schedule",
            delimiter=",",
            source_csv_path=input_csv,
            source_format="nova",
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1

    # Summary
    mi = payload["modelInput"]
    n_visits = len(mi["visits"])
    n_groups = len(mi.get("visitGroups", []))
    n_group_visits = sum(len(g["visits"]) for g in mi.get("visitGroups", []))
    n_vehicles = len(mi["vehicles"])
    n_shifts = sum(len(v["shifts"]) for v in mi["vehicles"])

    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Expanded CSV: {expanded_csv}")
    print(f"  Rows:       {n_expanded}")
    print()
    print(f"Timefold JSON: {output_json}")
    print(f"  Standalone visits: {n_visits}")
    print(f"  Visit groups:      {n_groups} ({n_group_visits} visits)")
    print(f"  Total visits:      {n_visits + n_group_visits}")
    print(f"  Vehicles:          {n_vehicles}")
    print(f"  Shifts:            {n_shifts}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
