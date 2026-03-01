#!/usr/bin/env python3
"""
Fetch a Timefold FSR solution by route plan (dataset) ID.

Uses:
  GET .../v1/route-plans/<ID>         -> solution (modelOutput, metadata, etc.)
  GET .../v1/route-plans/<ID>/input   -> input dataset (modelInput)

When the solution is completed, can run metrics and continuity. If --save is set,
input is fetched from the API and saved next to the output (input.json in same dir)
so metrics and continuity can run without a separate --input file.

Usage:
  # Fetch and print status + summary
  python3 fetch_timefold_solution.py 391486da-ca6f-4928-a928-056a589842e1

  # Fetch output + input, save both, run metrics and continuity
  python3 fetch_timefold_solution.py <ID> --save solve/dataset/output.json --metrics-dir ../metrics/

  # Or pass input explicitly (e.g. local file instead of API)
  python3 fetch_timefold_solution.py <ID> --save solve/output.json --input solve/input.json --metrics-dir ../metrics/

Route plan IDs are listed in timefold_route_plan_ids.md in this folder.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import requests

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

TIMEFOLD_BASE = "https://app.timefold.ai/api/models/field-service-routing/v1/route-plans"
_DEFAULT_ENV_FILE = Path.home() / ".config" / "caire" / "env"


def _load_env_file(env_file: Path) -> None:
    """Load simple KEY=VALUE or export KEY=VALUE pairs into os.environ."""
    if not env_file.exists():
        return
    pattern = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = pattern.match(line)
        if not match:
            continue
        key, value = match.groups()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        os.environ.setdefault(key, value)


def _bootstrap_env() -> None:
    """Load ~/.config/caire/env (or CAIRE_ENV_FILE override) if present."""
    override = os.environ.get("CAIRE_ENV_FILE", "").strip()
    if override:
        _load_env_file(Path(override).expanduser())
        return
    _load_env_file(_DEFAULT_ENV_FILE)


def fetch_solution(route_plan_id: str, api_key: str) -> dict:
    """GET route plan by ID. Returns full response JSON (metadata, modelOutput, etc.)."""
    if not api_key:
        raise RuntimeError("TIMEFOLD_API_KEY environment variable is required")
    url = f"{TIMEFOLD_BASE}/{route_plan_id}"
    headers = {"Accept": "application/json", "X-API-KEY": api_key}
    r = requests.get(url, headers=headers, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:800]}")
    return r.json()


def fetch_input(route_plan_id: str, api_key: str) -> dict:
    """GET route plan input by ID. Returns input dataset (RoutePlanInput / modelInput)."""
    if not api_key:
        raise RuntimeError("TIMEFOLD_API_KEY environment variable is required")
    url = f"{TIMEFOLD_BASE}/{route_plan_id}/input"
    headers = {"Accept": "application/json", "X-API-KEY": api_key}
    r = requests.get(url, headers=headers, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:800]}")
    return r.json()


def main() -> int:
    _bootstrap_env()

    parser = argparse.ArgumentParser(
        description="Fetch Timefold FSR solution by route plan ID",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "route_plan_id",
        help="Route plan (dataset) ID returned when the solve was submitted",
    )
    parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Save full response JSON to this path",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional: path to input JSON. If not set and --save is set, input is fetched from API and saved next to output.",
    )
    parser.add_argument(
        "--metrics-dir",
        type=Path,
        default=None,
        help="Run metrics (and continuity) and save here. Uses --input if set, else input fetched from API when --save is set.",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key (default: TIMEFOLD_API_KEY env)",
    )
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("TIMEFOLD_API_KEY", "")
    if not api_key:
        print("Error: Set TIMEFOLD_API_KEY or pass --api-key", file=sys.stderr)
        return 1

    try:
        data = fetch_solution(args.route_plan_id.strip(), api_key)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    meta = data.get("metadata") or data.get("run") or {}
    status = (meta.get("solverStatus") or data.get("solverStatus") or "?").upper()
    score = meta.get("score", "?")
    name = meta.get("name") or data.get("name") or "—"

    out = data.get("modelOutput") or {}
    n_vehicles = len(out.get("vehicles", []))
    unassigned = out.get("unassignedVisits") or []
    n_unassigned = len(unassigned)

    print(f"Route plan ID: {args.route_plan_id}")
    print(f"Name:          {name}")
    print(f"Solver status: {status}")
    print(f"Score:         {score}")
    print(f"Vehicles:      {n_vehicles}")
    print(f"Unassigned:    {n_unassigned}")

    status_completed = status == "SOLVING_COMPLETED"

    if args.save:
        args.save.parent.mkdir(parents=True, exist_ok=True)
        with open(args.save, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved:         {args.save}")

        # Fetch and save input from API so metrics/continuity can run without --input
        if status_completed and args.metrics_dir and not (args.input and (args.input if args.input.is_absolute() else (Path.cwd() / args.input)).exists()):
            try:
                input_data_api = fetch_input(args.route_plan_id.strip(), api_key)
                if "modelInput" not in input_data_api and ("vehicles" in input_data_api or "visits" in input_data_api):
                    input_data_api = {"modelInput": input_data_api}
                input_save_path = args.save.parent / "input.json"
                with open(input_save_path, "w", encoding="utf-8") as f:
                    json.dump(input_data_api, f, indent=2, ensure_ascii=False)
                print(f"Saved input:   {input_save_path}")
            except RuntimeError as e:
                print(f"Warning: could not fetch input from API: {e}", file=sys.stderr)

    # Resolve input path: explicit --input, or input.json next to saved output
    input_path = None
    if args.input and args.input.exists():
        input_path = args.input.resolve() if args.input.is_absolute() else (Path.cwd() / args.input).resolve()
    elif args.save and args.save.exists():
        candidate = args.save.parent / "input.json"
        if candidate.exists():
            input_path = candidate.resolve()

    # Run metrics when solution is completed and we have input + metrics-dir
    if status_completed and input_path and args.metrics_dir:
        if not input_path.exists():
            print(f"Warning: input not found {input_path}, skipping metrics.", file=sys.stderr)
        else:
            from metrics import aggregate, analyze_input, print_report, save_metrics

            with open(input_path, encoding="utf-8") as f:
                input_data = json.load(f)
            if "modelInput" not in input_data and ("vehicles" in input_data or "visits" in input_data):
                input_data = {"modelInput": input_data}
            input_info = analyze_input(input_path)
            agg = aggregate(data, input_data, use_depot_end=False)
            print()
            print_report(agg, input_info, exclude_inactive=False)
            metrics_dir = args.metrics_dir if args.metrics_dir.is_absolute() else (Path.cwd() / args.metrics_dir)
            metrics_dir.mkdir(parents=True, exist_ok=True)
            _fp, _rp = save_metrics(agg, input_info, metrics_dir, exclude_inactive=False)
            print(f"\nMetrics saved to {metrics_dir}")

            # If empty shifts: run run_analyze_metrics_frompatch.py (solve_report + build_from_patch)
            if agg.get("shifts_no_visits", 0) > 0:
                out_path = args.save.resolve() if args.save else None
                if out_path and out_path.exists():
                    cmd = [
                        sys.executable,
                        str(_SCRIPT_DIR / "run_analyze_metrics_frompatch.py"),
                        "--output", str(out_path),
                        "--input", str(input_path.resolve()),
                        "--metrics-dir", str(metrics_dir.resolve()),
                    ]
                    print(f"\nEmpty shifts detected ({agg['shifts_no_visits']}). Running run_analyze_metrics_frompatch...")
                    r = subprocess.run(cmd, cwd=str(_REPO_ROOT))
                    if r.returncode != 0:
                        print(f"Warning: run_analyze_metrics_frompatch exited with {r.returncode}", file=sys.stderr)

            # Continuity report (per-client distinct caregivers)
            if args.save and args.save.exists():
                continuity_report_path = args.save.parent / "continuity.csv"
                cmd = [
                    sys.executable,
                    str(_SCRIPT_DIR / "continuity_report.py"),
                    "--input", str(input_path.resolve()),
                    "--output", str(args.save.resolve()),
                    "--report", str(continuity_report_path),
                ]
                print(f"\nRunning continuity report -> {continuity_report_path}")
                r = subprocess.run(cmd, cwd=str(_SCRIPT_DIR))
                if r.returncode != 0:
                    print(f"Warning: continuity_report.py exited with {r.returncode}", file=sys.stderr)
                # Append continuity summary to metrics report
                elif continuity_report_path.exists() and _rp and Path(_rp).exists():
                    import csv as csv_mod
                    with open(continuity_report_path, encoding="utf-8") as cf:
                        rows = list(csv_mod.DictReader(cf))
                    cont_values = []
                    for r in rows:
                        c = r.get("continuity", "").strip()
                        if c.isdigit():
                            cont_values.append(int(c))
                    if cont_values:
                        n_clients = len(cont_values)
                        avg_c = sum(cont_values) / n_clients
                        max_c = max(cont_values)
                        over_15 = sum(1 for c in cont_values if c > 15)
                        with open(_rp, "a", encoding="utf-8") as rf:
                            rf.write("\n")
                            rf.write("--- Continuity (distinct caregivers per client; target ≤15) ---\n")
                            rf.write(f"  Clients: {n_clients}  |  Avg continuity: {avg_c:.1f}  |  Max: {max_c}  |  Over 15: {over_15}\n")
                            rf.write(f"  Full CSV: {continuity_report_path.resolve()}\n")
                            rf.write("=" * 72 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
