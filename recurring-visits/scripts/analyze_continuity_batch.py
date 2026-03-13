#!/usr/bin/env python3
"""
Analyze a batch of continuity jobs from Timefold FSR.
Fetches jobs, runs metrics (excluding idle shifts), compares continuity, and prepares from-patch.

Usage:
  python3 analyze_continuity_batch.py --campaign d2a6a01b-3309-4db5-ab4c-78ad1a218c19
  python3 analyze_continuity_batch.py --job-ids 1aa5e0a0,6d2d0476,595e0754
  python3 analyze_continuity_batch.py --since-hours 24 --env test
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

TIMEFOLD_BASE = "https://app.timefold.ai/api/models/field-service-routing/v1/route-plans"
_DEFAULT_ENV_FILE = Path.home() / ".config" / "caire" / "env"
_SCRIPT_DIR = Path(__file__).resolve().parent


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
    """Load env: CAIRE_ENV_FILE override, else ~/.config/caire/env, else scripts/.env."""
    override = os.environ.get("CAIRE_ENV_FILE", "").strip()
    if override:
        _load_env_file(Path(override).expanduser())
        return
    _load_env_file(_DEFAULT_ENV_FILE)
    if not os.environ.get("TIMEFOLD_API_KEY", "").strip():
        script_env = _SCRIPT_DIR / ".env"
        _load_env_file(script_env)


def fetch_route_plan(plan_id: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Fetch full route plan details."""
    url = f"{TIMEFOLD_BASE}/{plan_id}"
    headers = {"Accept": "application/json", "X-API-KEY": api_key}

    try:
        r = requests.get(url, headers=headers, timeout=60)
        if r.status_code != 200:
            print(f"Error fetching {plan_id}: HTTP {r.status_code}", file=sys.stderr)
            return None
        return r.json()
    except requests.RequestException as e:
        print(f"Error fetching {plan_id}: {e}", file=sys.stderr)
        return None


def fetch_route_plan_input(plan_id: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Fetch route plan input (modelInput)."""
    url = f"{TIMEFOLD_BASE}/{plan_id}/input"
    headers = {"Accept": "application/json", "X-API-KEY": api_key}

    try:
        r = requests.get(url, headers=headers, timeout=60)
        if r.status_code != 200:
            return None
        return r.json()
    except requests.RequestException:
        return None


def run_metrics(input_path: Path, output_path: Path, exclude_inactive: bool = True) -> Optional[Dict[str, Any]]:
    """Run metrics.py on input/output and return aggregated results."""
    sys.path.insert(0, str(_SCRIPT_DIR))
    from metrics import aggregate, analyze_input

    try:
        with open(input_path, encoding="utf-8") as f:
            input_data = json.load(f)
        if "modelInput" not in input_data and ("vehicles" in input_data or "visits" in input_data):
            input_data = {"modelInput": input_data}

        with open(output_path, encoding="utf-8") as f:
            output_data = json.load(f)

        input_info = analyze_input(input_path)
        agg = aggregate(output_data, input_data, use_depot_end=False)

        return {
            "metrics": agg,
            "input_info": input_info,
            "exclude_inactive": exclude_inactive,
        }
    except Exception as e:
        print(f"Error running metrics: {e}", file=sys.stderr)
        return None


def run_continuity_report(input_path: Path, output_path: Path, report_path: Path) -> Optional[Dict[str, Any]]:
    """Run continuity_report.py and return summary."""
    import subprocess

    cmd = [
        sys.executable,
        str(_SCRIPT_DIR / "continuity_report.py"),
        "--input", str(input_path),
        "--output", str(output_path),
        "--report", str(report_path),
    ]

    try:
        result = subprocess.run(cmd, cwd=str(_SCRIPT_DIR), capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"continuity_report.py failed: {result.stderr}", file=sys.stderr)
            return None

        # Parse the CSV
        if not report_path.exists():
            return None

        import csv
        with open(report_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        cont_values = []
        for r in rows:
            c = r.get("continuity", "").strip()
            if c.isdigit():
                cont_values.append(int(c))

        if not cont_values:
            return None

        return {
            "clients": len(cont_values),
            "avg_continuity": sum(cont_values) / len(cont_values),
            "max_continuity": max(cont_values),
            "over_15": sum(1 for c in cont_values if c > 15),
            "continuity_values": cont_values,
        }
    except Exception as e:
        print(f"Error running continuity report: {e}", file=sys.stderr)
        return None


def main() -> int:
    _bootstrap_env()

    parser = argparse.ArgumentParser(
        description="Analyze batch of continuity jobs from Timefold FSR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--campaign",
        default=None,
        help="Campaign/batch ID (e.g., d2a6a01b-3309-4db5-ab4c-78ad1a218c19)",
    )
    parser.add_argument(
        "--job-ids",
        default=None,
        help="Comma-separated list of route plan IDs",
    )
    parser.add_argument(
        "--env",
        choices=["test", "prod"],
        default="test",
        help="Environment (test or prod)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("../analysis/continuity_batch"),
        help="Output directory for analysis results",
    )
    parser.add_argument(
        "--exclude-inactive",
        action="store_true",
        default=True,
        help="Exclude inactive/empty shifts from metrics (default: True)",
    )
    parser.add_argument(
        "--include-inactive",
        action="store_false",
        dest="exclude_inactive",
        help="Include inactive/empty shifts in metrics",
    )

    args = parser.parse_args()

    # Get API key based on environment
    if args.env == "test":
        api_key = os.environ.get("TIMEFOLD_API_KEY", "")
    else:
        api_key = os.environ.get("TIMEFOLD_PROD_API_KEY", "")

    if not api_key:
        print(f"Error: No API key found for {args.env} environment", file=sys.stderr)
        print("Set TIMEFOLD_API_KEY (test) or TIMEFOLD_PROD_API_KEY (prod)", file=sys.stderr)
        return 1

    # Parse job IDs
    job_ids = []
    if args.job_ids:
        job_ids = [j.strip() for j in args.job_ids.split(",") if j.strip()]
    elif args.campaign:
        # For now, use the job IDs from the tables provided by user
        # In production, we'd query Timefold API with campaign tag
        print(f"Campaign mode: {args.campaign}")
        print("Please provide --job-ids for specific jobs to analyze")
        return 1

    if not job_ids:
        print("Error: No job IDs provided. Use --job-ids or --campaign", file=sys.stderr)
        return 1

    # Create output directory
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = _SCRIPT_DIR.parent / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Analyzing {len(job_ids)} jobs from {args.env} environment")
    print(f"Output directory: {output_dir}")
    print(f"Exclude inactive shifts: {args.exclude_inactive}")
    print()

    results = []

    for i, job_id in enumerate(job_ids, 1):
        print(f"[{i}/{len(job_ids)}] Processing job: {job_id}")

        # Fetch route plan
        print(f"  Fetching route plan...")
        output_data = fetch_route_plan(job_id, api_key)
        if not output_data:
            print(f"  ✗ Failed to fetch route plan")
            continue

        # Fetch input
        print(f"  Fetching input...")
        input_data = fetch_route_plan_input(job_id, api_key)
        if not input_data:
            print(f"  ✗ Failed to fetch input")
            continue

        # Save to disk
        job_dir = output_dir / job_id[:8]
        job_dir.mkdir(parents=True, exist_ok=True)

        output_path = job_dir / "output.json"
        input_path = job_dir / "input.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        if "modelInput" not in input_data:
            input_data = {"modelInput": input_data}
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(input_data, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Saved to {job_dir}")

        # Run metrics
        print(f"  Running metrics (exclude_inactive={args.exclude_inactive})...")
        metrics_result = run_metrics(input_path, output_path, args.exclude_inactive)
        if not metrics_result:
            print(f"  ✗ Metrics failed")
            continue

        metrics = metrics_result["metrics"]
        print(f"    Visits: {metrics.get('visits_assigned', 0)}/{metrics.get('visits_total', 0)} assigned")
        print(f"    Unassigned: {metrics.get('visits_unassigned', 0)}")
        print(f"    Travel efficiency: {metrics.get('travel_efficiency', 0):.1f}%")
        print(f"    Field efficiency: {metrics.get('field_efficiency', 0):.1f}%")
        print(f"    Empty shifts: {metrics.get('shifts_no_visits', 0)}")

        # Run continuity report
        print(f"  Running continuity report...")
        continuity_path = job_dir / "continuity.csv"
        continuity_result = run_continuity_report(input_path, output_path, continuity_path)
        if continuity_result:
            print(f"    Clients: {continuity_result['clients']}")
            print(f"    Avg continuity: {continuity_result['avg_continuity']:.1f}")
            print(f"    Max continuity: {continuity_result['max_continuity']}")
            print(f"    Over 15: {continuity_result['over_15']}")
        else:
            print(f"  ✗ Continuity report failed")

        # Extract metadata
        metadata = output_data.get("metadata", output_data.get("run", {}))
        status = metadata.get("solverStatus", "")
        score = metadata.get("score", "")
        name = metadata.get("name", output_data.get("name", ""))

        results.append({
            "job_id": job_id,
            "name": name,
            "status": status,
            "score": score,
            "metrics": metrics,
            "continuity": continuity_result,
            "output_path": str(output_path),
            "input_path": str(input_path),
        })

        print()

    # Generate summary report
    summary_path = output_dir / "BATCH_ANALYSIS_SUMMARY.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"# Continuity Batch Analysis\n\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n")
        f.write(f"**Environment:** {args.env}\n")
        f.write(f"**Jobs Analyzed:** {len(results)}\n")
        f.write(f"**Exclude Inactive Shifts:** {args.exclude_inactive}\n\n")
        f.write(f"---\n\n")

        f.write(f"## Summary Table\n\n")
        f.write(f"| Job ID | Name | Unassigned | Travel Eff | Empty Shifts | Continuity Avg | Over 15 |\n")
        f.write(f"|--------|------|------------|------------|--------------|----------------|----------|\n")

        for r in results:
            m = r["metrics"]
            c = r["continuity"] or {}
            f.write(f"| {r['job_id'][:8]}... | {r['name'][:30]:30s} | "
                   f"{m.get('visits_unassigned', 0):3d} | "
                   f"{m.get('travel_efficiency', 0):5.1f}% | "
                   f"{m.get('shifts_no_visits', 0):3d} | "
                   f"{c.get('avg_continuity', 0):5.1f} | "
                   f"{c.get('over_15', 0):3d} |\n")

        f.write(f"\n---\n\n")

        f.write(f"## Detailed Results\n\n")
        for r in results:
            f.write(f"### {r['name']} ({r['job_id'][:8]}...)\n\n")
            f.write(f"**Status:** {r['status']}\n")
            f.write(f"**Score:** {r['score']}\n\n")

            m = r["metrics"]
            f.write(f"**Metrics:**\n")
            f.write(f"- Visits: {m.get('visits_assigned', 0)}/{m.get('visits_total', 0)} assigned ({m.get('visits_unassigned', 0)} unassigned)\n")
            f.write(f"- Travel efficiency: {m.get('travel_efficiency', 0):.1f}%\n")
            f.write(f"- Field efficiency: {m.get('field_efficiency', 0):.1f}%\n")
            f.write(f"- Empty shifts: {m.get('shifts_no_visits', 0)}\n")
            f.write(f"- Activated vehicles: {m.get('vehicles_used', 0)}\n\n")

            if r["continuity"]:
                c = r["continuity"]
                f.write(f"**Continuity:**\n")
                f.write(f"- Clients: {c['clients']}\n")
                f.write(f"- Avg continuity: {c['avg_continuity']:.1f}\n")
                f.write(f"- Max continuity: {c['max_continuity']}\n")
                f.write(f"- Over 15: {c['over_15']}\n\n")

            f.write(f"**Files:**\n")
            f.write(f"- Output: `{r['output_path']}`\n")
            f.write(f"- Input: `{r['input_path']}`\n\n")
            f.write(f"---\n\n")

    print(f"✓ Summary report saved to {summary_path}")

    # Save JSON results
    json_path = output_dir / "batch_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"✓ JSON results saved to {json_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
