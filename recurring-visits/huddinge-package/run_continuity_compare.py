#!/usr/bin/env python3
"""
Submit all 4 continuity strategies to Timefold FSR in parallel for comparison.

Strategies:
  1. base       – no continuity (plain FSR input)
  2. manual     – requiredVehicles from manual CSV (distinct employees per client, cap 15)
  3. area       – requiredVehicles from area-based even distribution (cap 15)
  4. first-run  – requiredVehicles from top-15 vehicles per client from a previous FSR output (requires --first-run-output)

Builds the 4 payloads, then submits them concurrently. Prints each route plan ID when done so you can compare in Timefold.

Usage (from huddinge-package):
  python run_continuity_compare.py --expanded-csv expanded/huddinge_2wk_expanded_20260224_043456.csv --weeks 2 --env prod
  python run_continuity_compare.py --expanded-csv expanded/huddinge_2wk_expanded_20260224_043456.csv --weeks 2 --env prod --first-run-output solve/24feb/trimmed/export-field-service-routing-fa713a0d-f4e7-4c56-a019-65f41042e336-output.json
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# Same API keys as process_huddinge
TIMEFOLD_PROD_API_KEY = "tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8"
TIMEFOLD_PROD_CONFIG_ID = "8f3ffcc6-1cb4-4ef9-a4c4-770191a23834"
TIMEFOLD_DEV_API_KEY = "tf_p_411fa75d-ffeb-40ec-b491-9d925bd1d1f3"
TIMEFOLD_DEV_CONFIG_ID = "6a4e6b5f-8767-48f8-9365-7091f7e74a37"

_PKG_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _PKG_DIR / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
_REPO_SCRIPTS = _PKG_DIR.parent / "scripts"
if str(_REPO_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_REPO_SCRIPTS))

from csv_to_timefold_fsr import generate_timefold_json


def _submit_one(
    strategy: str,
    payload: dict,
    config_id: str,
) -> tuple[str, str | None, str | None]:
    """Submit one payload; return (strategy, plan_id or None, error or None)."""
    try:
        from submit_to_timefold import submit_solve
        resp = submit_solve(payload, configuration_id=config_id)
        plan_id = resp.get("id") or resp.get("parentId") or resp.get("originId") or "?"
        return (strategy, str(plan_id), None)
    except Exception as e:
        return (strategy, None, str(e))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Submit base + manual + area + first-run continuity strategies to Timefold FSR in parallel",
    )
    parser.add_argument("--expanded-csv", type=Path, required=True, help="Expanded CSV path (e.g. expanded/huddinge_2wk_expanded_*.csv)")
    parser.add_argument("--weeks", type=int, default=2, choices=[2, 4])
    parser.add_argument("--start-date", default="2026-02-16")
    parser.add_argument("--env", choices=["dev", "prod"], default="prod", help="API env (default: prod)")
    parser.add_argument(
        "--first-run-output",
        type=Path,
        default=None,
        help="Existing FSR output JSON for first-run strategy (optional; if omitted, only 3 strategies are submitted)",
    )
    parser.add_argument("--output-dir", type=Path, default=_PKG_DIR, help="Base dir for paths and solve output")
    args = parser.parse_args()

    expanded_csv = args.expanded_csv if args.expanded_csv.is_absolute() else args.output_dir / args.expanded_csv
    if not expanded_csv.exists():
        print(f"Error: Expanded CSV not found: {expanded_csv}", file=sys.stderr)
        return 1

    # Set API key before any import of submit_to_timefold
    if args.env == "prod":
        os.environ["TIMEFOLD_API_KEY"] = TIMEFOLD_PROD_API_KEY
        os.environ["TIMEFOLD_CONFIGURATION_ID"] = TIMEFOLD_PROD_CONFIG_ID
    else:
        os.environ["TIMEFOLD_API_KEY"] = TIMEFOLD_DEV_API_KEY
        os.environ.setdefault("TIMEFOLD_CONFIGURATION_ID", TIMEFOLD_DEV_CONFIG_ID)
    config_id = TIMEFOLD_PROD_CONFIG_ID if args.env == "prod" else os.environ.get("TIMEFOLD_CONFIGURATION_ID", TIMEFOLD_DEV_CONFIG_ID)

    solve_dir = args.output_dir / "solve"
    solve_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_json = solve_dir / f"compare_base_{ts}.json"

    run_name = f"Huddinge {args.weeks}-Week Compare {ts}"
    print("Generating base FSR payload...")
    try:
        payload_base = generate_timefold_json(
            expanded_csv,
            base_json,
            planning_weeks=args.weeks,
            planning_start_date=args.start_date,
            run_name=run_name,
            delimiter=",",
            source_csv_path=None,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

    mi = payload_base["modelInput"]
    visit_to_person = None
    try:
        from build_continuity_pools import (
            pools_from_manual,
            pools_from_first_run,
            visit_to_person_from_model,
            patch_payload_with_pools,
        )
        visit_to_person = visit_to_person_from_model(mi)
    except ImportError as e:
        print(f"Error: {e}. Need build_continuity_pools on path.", file=sys.stderr)
        return 1

    valid_vehicle_ids = {str(v.get("id") or "") for v in mi.get("vehicles") or [] if v.get("id")}

    # Build strategy payloads (deep copy so we don't mutate base)
    tasks: list[tuple[str, dict]] = [("base", payload_base)]

    # Manual
    payload_manual = copy.deepcopy(payload_base)
    pools_manual = pools_from_manual(expanded_csv, max_per_client=15, valid_vehicle_ids=valid_vehicle_ids)
    patch_payload_with_pools(payload_manual, pools_manual, visit_to_person)
    tasks.append(("manual", payload_manual))

    # Area: pools_from_area needs fsr input path; use temp file
    payload_area = copy.deepcopy(payload_base)
    try:
        from build_continuity_pools import pools_from_area
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(payload_base, f, indent=2, ensure_ascii=False)
            tmp_path = Path(f.name)
        try:
            pools_area = pools_from_area(expanded_csv, tmp_path, max_per_client=15)
            patch_payload_with_pools(payload_area, pools_area, visit_to_person)
            tasks.append(("area", payload_area))
        finally:
            tmp_path.unlink(missing_ok=True)
    except Exception as e:
        print(f"Warning: area strategy skipped: {e}", file=sys.stderr)

    # First-run (optional)
    if args.first_run_output:
        fr_output = args.first_run_output if args.first_run_output.is_absolute() else args.output_dir / args.first_run_output
        if fr_output.exists():
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump(payload_base, f, indent=2, ensure_ascii=False)
                tmp_input = Path(f.name)
            try:
                pools_fr = pools_from_first_run(tmp_input, fr_output, max_per_client=15)
                # Restrict to vehicle IDs that exist in current payload (first-run output may be from different input)
                pools_fr_filtered = {
                    person: [vid for vid in vids if vid in valid_vehicle_ids][:15]
                    for person, vids in pools_fr.items()
                }
                payload_firstrun = copy.deepcopy(payload_base)
                patch_payload_with_pools(payload_firstrun, pools_fr_filtered, visit_to_person)
                tasks.append(("first-run", payload_firstrun))
            finally:
                tmp_input.unlink(missing_ok=True)
        else:
            print(f"Warning: --first-run-output not found: {fr_output}", file=sys.stderr)

    # Save each strategy JSON for reference
    for name, pl in tasks:
        path = solve_dir / f"compare_{name}_{ts}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(pl, f, indent=2, ensure_ascii=False)
        print(f"  Wrote {path}")

    # Submit all in parallel
    print()
    print(f"Submitting {len(tasks)} strategies to Timefold FSR ({args.env}) in parallel...")
    results: list[tuple[str, str | None, str | None]] = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(_submit_one, name, pl, config_id): name for name, pl in tasks}
        for fut in as_completed(futures):
            results.append(fut.result())

    # Sort by strategy name for stable output
    results.sort(key=lambda x: x[0])
    print()
    print("=" * 60)
    print("Results (compare in Timefold when solves finish)")
    print("=" * 60)
    for strategy, plan_id, err in results:
        if err:
            print(f"  {strategy:12} ERROR: {err}")
        else:
            print(f"  {strategy:12} Route plan ID: {plan_id}")
    print("=" * 60)
    return 0 if all(r[1] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
