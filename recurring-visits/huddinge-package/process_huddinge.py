#!/usr/bin/env python3
"""
Huddinge recurring visits pipeline: CSV -> Expanded CSV -> Timefold FSR JSON.

Orchestrates the full pipeline using scripts in this package.
API key and config are selected by --env (prod | dev); --send submits to Timefold FSR.

Usage:
  # Generate only (no send), dev env
  python process_huddinge.py --weeks 2

  # Use existing expanded CSV and send to production
  python process_huddinge.py --expanded-csv expanded/huddinge_2wk_expanded_20260224_043456.csv --weeks 2 --env prod --send

  # Full pipeline (expand + JSON) and send to prod
  python process_huddinge.py --weeks 2 --env prod --send

  # With continuity: build manual pools, patch requiredVehicles (max 15 per client), write input_continuity_*.json and submit to prod
  python process_huddinge.py --expanded-csv expanded/huddinge_2wk_expanded_20260224_043456.csv --weeks 2 --env prod --continuity --send
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Timefold FSR API: prod vs stage/dev (set via --env before importing submit_to_timefold).
# Prod config: 8f3ffcc6 = default; a43d4eec = Huddinge 2-week long run (use --config-id a43d4eec-9f53-40b3-82ad-f135adc8c7e3).
TIMEFOLD_PROD_API_KEY = "tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8"
TIMEFOLD_PROD_CONFIG_ID = "8f3ffcc6-1cb4-4ef9-a4c4-770191a23834"
TIMEFOLD_DEV_API_KEY = "tf_p_411fa75d-ffeb-40ec-b491-9d925bd1d1f3"  # stage
TIMEFOLD_DEV_CONFIG_ID = "6a4e6b5f-8767-48f8-9365-7091f7e74a37"  # stage config

_PKG_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _PKG_DIR / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
# Parent scripts (e.g. build_continuity_pools) when --continuity
_REPO_SCRIPTS = _PKG_DIR.parent / "scripts"
if str(_REPO_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_REPO_SCRIPTS))

from expand_recurring_visits import expand_visits
from csv_to_timefold_fsr import generate_timefold_json


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Process Huddinge recurring CSV to Timefold FSR JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python process_huddinge.py --weeks 2
  python process_huddinge.py --expanded-csv expanded/huddinge_2wk_expanded_20260224_043456.csv --weeks 2 --env prod --send
  python process_huddinge.py --expanded-csv expanded/huddinge_2wk_expanded_20260224_043456.csv --weeks 2 --env prod --continuity --send
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
    parser.add_argument(
        "--source-file",
        type=Path,
        default=None,
        help="Source CSV filename under output-dir/source/ (e.g. source.csv for demo-data)",
    )
    parser.add_argument(
        "--expanded-csv",
        type=Path,
        default=None,
        help="Use this expanded CSV instead of running expand (skip step 1); output-dir is base for relative paths.",
    )
    parser.add_argument(
        "--env",
        choices=["dev", "prod"],
        default="dev",
        help="Timefold API environment: prod uses production API key and default config id (default: dev)",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="After generating JSON, submit solve to Timefold FSR API (uses --env for API key and config)",
    )
    parser.add_argument(
        "--continuity",
        action="store_true",
        help="Build manual continuity pools from expanded CSV, patch FSR input with requiredVehicles (max 15 per client), write tf_input_continuity JSON; if --send, submit that continuity input.",
    )
    parser.add_argument(
        "--config-id",
        default=None,
        help="Override Timefold configuration ID for --send (e.g. a43d4eec-9f53-40b3-82ad-f135adc8c7e3 for prod run with different profile)",
    )
    args = parser.parse_args()

    # Set Timefold API env from --env (prod or dev) so submit_to_timefold uses correct key when imported
    if args.send:
        if args.env == "prod":
            os.environ["TIMEFOLD_API_KEY"] = TIMEFOLD_PROD_API_KEY
            os.environ["TIMEFOLD_CONFIGURATION_ID"] = TIMEFOLD_PROD_CONFIG_ID
        else:
            os.environ["TIMEFOLD_API_KEY"] = TIMEFOLD_DEV_API_KEY
            os.environ.setdefault("TIMEFOLD_CONFIGURATION_ID", TIMEFOLD_DEV_CONFIG_ID)

    source_dir = args.output_dir / "source"
    expanded_dir = args.output_dir / "expanded"
    solve_dir = args.output_dir / "solve"

    expanded_dir.mkdir(parents=True, exist_ok=True)
    solve_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    use_expanded_csv = args.expanded_csv is not None

    if use_expanded_csv:
        expanded_csv = args.expanded_csv if args.expanded_csv.is_absolute() else args.output_dir / args.expanded_csv
        if not expanded_csv.exists():
            print(f"Error: Expanded CSV not found: {expanded_csv}", file=sys.stderr)
            return 1
        output_json = solve_dir / f"input_{ts}.json"
        run_name = f"Huddinge {args.weeks}-Week Schedule"
        input_csv = None  # optional for generate_timefold_json
        n_expanded = None  # unknown when using existing CSV
    else:
        if args.source_file is not None:
            input_csv = source_dir / args.source_file.name
        else:
            input_csv = source_dir / "Huddinge_recurring_v2.csv"
            if not input_csv.exists():
                input_csv = source_dir / "Huddinge_recurring.csv"
            if not input_csv.exists():
                input_csv = args.output_dir / "Huddinge_recurring_v2.csv"
            if not input_csv.exists():
                input_csv = args.output_dir / "Huddinge_recurring.csv"
        if not input_csv.exists():
            print("Error: Source CSV not found (tried source/, output-dir/)", file=sys.stderr)
            return 1
        use_demo_names = args.source_file is not None and args.source_file.name == "source.csv"
        expanded_basename = f"demo_{args.weeks}wk_expanded_{ts}.csv" if use_demo_names else f"huddinge_{args.weeks}wk_expanded_{ts}.csv"
        expanded_csv = expanded_dir / expanded_basename
        output_json = solve_dir / f"input_{ts}.json"
        run_name = f"Demo {args.weeks}-Week Schedule" if use_demo_names else f"Huddinge {args.weeks}-Week Schedule"

    print("=" * 60)
    print("Recurring Visits Pipeline")
    print("=" * 60)
    if use_expanded_csv:
        print(f"Expanded CSV: {expanded_csv}")
        print(f"Planning:     {args.weeks} weeks from {args.start_date}")
    else:
        print(f"Input:        {input_csv}")
        print(f"Planning:     {args.weeks} weeks from {args.start_date}")
    if args.send:
        print(f"Env:          {args.env} (will submit to Timefold after JSON)")
    print()

    if not use_expanded_csv:
        # Step 1: Expand
        print("[1/2] Expanding recurring visits...")
        try:
            n_expanded = expand_visits(
                input_csv,
                expanded_csv,
                planning_weeks=args.weeks,
                planning_start_date=args.start_date,
                delimiter=";",
                write_delimiter=",",
            )
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            import traceback

            traceback.print_exc()
            return 1
        print()
    else:
        n_expanded = None

    # Step 2: Generate JSON
    step_label = "[2/2]" if not use_expanded_csv else "[1/1]"
    print(f"{step_label} Generating Timefold FSR JSON...")
    try:
        payload = generate_timefold_json(
            expanded_csv,
            output_json,
            planning_weeks=args.weeks,
            planning_start_date=args.start_date,
            run_name=run_name,
            delimiter=",",
            source_csv_path=input_csv,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1

    # Optional: continuity-patched input (expanded -> tf_input_continuity)
    payload_to_send = payload
    continuity_json_path = None
    if args.continuity:
        print()
        print("[Continuity] Building manual pools and patching FSR input...")
        try:
            from build_continuity_pools import (
                pools_from_manual,
                visit_to_person_from_model,
                patch_payload_with_pools,
            )
        except ImportError as e:
            print(f"Error: {e}. Ensure scripts/build_continuity_pools.py is on path (e.g. from huddinge-package parent).", file=sys.stderr)
            return 1
        mi = payload["modelInput"]
        valid_vehicle_ids = {str(v.get("id") or "") for v in mi.get("vehicles") or [] if v.get("id")}
        pools = pools_from_manual(
            expanded_csv,
            max_per_client=15,
            valid_vehicle_ids=valid_vehicle_ids,
        )
        visit_to_person = visit_to_person_from_model(mi)
        patch_payload_with_pools(payload, pools, visit_to_person)
        continuity_json_path = solve_dir / f"input_continuity_{ts}.json"
        with open(continuity_json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        n_with_pool = sum(1 for p in pools.values() if p)
        print(f"  Client pools: {len(pools)} clients, {n_with_pool} with non-empty pool (requiredVehicles set)")
        print(f"  Wrote: {continuity_json_path}")
        payload_to_send = payload

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
    if n_expanded is not None:
        print(f"  Rows:       {n_expanded}")
    print()
    print(f"Timefold JSON: {output_json}")
    print(f"  Standalone visits: {n_visits}")
    print(f"  Visit groups:      {n_groups} ({n_group_visits} visits)")
    print(f"  Total visits:      {n_visits + n_group_visits}")
    print(f"  Vehicles:          {n_vehicles}")
    print(f"  Shifts:            {n_shifts}")
    if continuity_json_path:
        print(f"  Continuity input:  {continuity_json_path}")
    print("=" * 60)

    if args.send:
        config_id = (
            args.config_id
            if args.config_id
            else (TIMEFOLD_PROD_CONFIG_ID if args.env == "prod" else os.environ.get("TIMEFOLD_CONFIGURATION_ID", TIMEFOLD_DEV_CONFIG_ID))
        )
        print()
        print("Submitting solve to Timefold FSR API...")
        if args.config_id:
            print(f"  Configuration: {config_id}")
        if args.continuity:
            print("  Using continuity-patched input (requiredVehicles per client).")
        try:
            from submit_to_timefold import submit_solve
            resp = submit_solve(payload_to_send, configuration_id=config_id)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
        plan_id = resp.get("id") or resp.get("parentId") or resp.get("originId") or "?"
        print(f"Submitted. Route plan ID: {plan_id}")
        print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
