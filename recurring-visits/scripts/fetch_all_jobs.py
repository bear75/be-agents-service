#!/usr/bin/env python3
"""
Fetch all jobs (route plans) from Timefold FSR API for both test and prod environments.
Analyzes and compares results across environments.

Usage:
  python3 fetch_all_jobs.py
  python3 fetch_all_jobs.py --test-key tf_p_xxx --prod-key tf_p_yyy
  python3 fetch_all_jobs.py --output analysis.json
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

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
    """Load env: CAIRE_ENV_FILE override, else ~/.config/caire/env, else scripts/.env."""
    override = os.environ.get("CAIRE_ENV_FILE", "").strip()
    if override:
        _load_env_file(Path(override).expanduser())
        return
    _load_env_file(_DEFAULT_ENV_FILE)
    if not os.environ.get("TIMEFOLD_API_KEY", "").strip():
        script_env = Path(__file__).resolve().parent / ".env"
        _load_env_file(script_env)


def fetch_all_route_plans(api_key: str, page_size: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch all route plans from Timefold API.
    Uses pagination to get complete list.
    """
    all_plans = []
    page = 0

    while True:
        url = f"{TIMEFOLD_BASE}?page={page}&size={page_size}"
        headers = {"Accept": "application/json", "X-API-KEY": api_key}

        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code != 200:
                print(f"Warning: HTTP {r.status_code} on page {page}: {r.text[:200]}", file=sys.stderr)
                break

            data = r.json()

            # Handle different response formats
            if isinstance(data, list):
                plans = data
            elif isinstance(data, dict):
                plans = data.get("content", data.get("items", []))
            else:
                break

            if not plans:
                break

            all_plans.extend(plans)

            # Check if there are more pages
            if isinstance(data, dict):
                total_pages = data.get("totalPages", 1)
                if page >= total_pages - 1:
                    break

            if len(plans) < page_size:
                break

            page += 1

        except requests.RequestException as e:
            print(f"Error fetching page {page}: {e}", file=sys.stderr)
            break

    return all_plans


def analyze_route_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key information from a route plan."""
    metadata = plan.get("metadata", plan.get("run", {}))
    output = plan.get("modelOutput", {})

    plan_id = plan.get("id", "unknown")
    name = metadata.get("name", plan.get("name", ""))
    status = (metadata.get("solverStatus", plan.get("solverStatus", ""))).upper()
    score = metadata.get("score")
    created = metadata.get("createdAt", plan.get("createdAt"))
    updated = metadata.get("updatedAt", plan.get("updatedAt"))
    parent_id = metadata.get("parentId")
    origin_id = metadata.get("originId")
    tags = metadata.get("tags", [])

    vehicles = output.get("vehicles", [])
    unassigned = output.get("unassignedVisits", [])

    n_vehicles = len(vehicles)
    n_unassigned = len(unassigned)
    n_assigned = sum(len(v.get("visits", [])) for v in vehicles)

    return {
        "id": plan_id,
        "name": name,
        "status": status,
        "score": score,
        "created_at": created,
        "updated_at": updated,
        "parent_id": parent_id,
        "origin_id": origin_id,
        "tags": tags,
        "vehicles": n_vehicles,
        "assigned_visits": n_assigned,
        "unassigned_visits": n_unassigned,
        "total_visits": n_assigned + n_unassigned,
        "is_from_patch": any("from-patch" in str(t).lower() for t in tags),
    }


def generate_summary(plans: List[Dict[str, Any]], env_name: str) -> Dict[str, Any]:
    """Generate summary statistics for a set of route plans."""
    total = len(plans)

    status_counts = {}
    for p in plans:
        status = p["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    completed = [p for p in plans if "COMPLETED" in p["status"]]
    failed = [p for p in plans if "FAILED" in p["status"]]
    running = [p for p in plans if "ACTIVE" in p["status"] or "SCHEDULED" in p["status"]]
    from_patch = [p for p in plans if p["is_from_patch"]]

    total_visits = sum(p["total_visits"] for p in plans)
    total_unassigned = sum(p["unassigned_visits"] for p in plans)

    return {
        "environment": env_name,
        "total_plans": total,
        "status_breakdown": status_counts,
        "completed_count": len(completed),
        "failed_count": len(failed),
        "running_count": len(running),
        "from_patch_count": len(from_patch),
        "total_visits_across_all": total_visits,
        "total_unassigned_across_all": total_unassigned,
        "avg_visits_per_plan": total_visits / total if total > 0 else 0,
        "recent_plans": sorted(plans, key=lambda x: x.get("created_at") or "", reverse=True)[:10],
    }


def print_summary(summary: Dict[str, Any]) -> None:
    """Print formatted summary to console."""
    print(f"\n{'=' * 80}")
    print(f"Environment: {summary['environment'].upper()}")
    print(f"{'=' * 80}")
    print(f"Total Route Plans: {summary['total_plans']}")
    print(f"\nStatus Breakdown:")
    for status, count in sorted(summary['status_breakdown'].items()):
        print(f"  {status:25s}: {count:4d}")

    print(f"\nSummary:")
    print(f"  Completed: {summary['completed_count']}")
    print(f"  Failed:    {summary['failed_count']}")
    print(f"  Running:   {summary['running_count']}")
    print(f"  From-Patch: {summary['from_patch_count']}")

    print(f"\nVisits:")
    print(f"  Total across all plans: {summary['total_visits_across_all']}")
    print(f"  Unassigned across all:  {summary['total_unassigned_across_all']}")
    print(f"  Avg per plan:           {summary['avg_visits_per_plan']:.1f}")

    if summary['recent_plans']:
        print(f"\nRecent Plans (last 10):")
        for i, plan in enumerate(summary['recent_plans'], 1):
            status_icon = "✓" if "COMPLETED" in plan['status'] else "✗" if "FAILED" in plan['status'] else "•"
            print(f"  {i:2d}. {status_icon} {plan['id'][:8]}... | {plan['name'][:40]:40s} | "
                  f"{plan['status']:20s} | Visits: {plan['total_visits']:3d} | "
                  f"Unassigned: {plan['unassigned_visits']:2d}")


def compare_environments(test_summary: Dict[str, Any], prod_summary: Dict[str, Any]) -> None:
    """Print comparison between test and prod environments."""
    print(f"\n{'=' * 80}")
    print("ENVIRONMENT COMPARISON")
    print(f"{'=' * 80}")

    print(f"\n{'Metric':<40s} {'Test':>15s} {'Prod':>15s}")
    print(f"{'-' * 70}")
    print(f"{'Total Plans':<40s} {test_summary['total_plans']:>15d} {prod_summary['total_plans']:>15d}")
    print(f"{'Completed':<40s} {test_summary['completed_count']:>15d} {prod_summary['completed_count']:>15d}")
    print(f"{'Failed':<40s} {test_summary['failed_count']:>15d} {prod_summary['failed_count']:>15d}")
    print(f"{'Running':<40s} {test_summary['running_count']:>15d} {prod_summary['running_count']:>15d}")
    print(f"{'From-Patch':<40s} {test_summary['from_patch_count']:>15d} {prod_summary['from_patch_count']:>15d}")
    print(f"{'Total Visits':<40s} {test_summary['total_visits_across_all']:>15d} {prod_summary['total_visits_across_all']:>15d}")
    print(f"{'Unassigned Visits':<40s} {test_summary['total_unassigned_across_all']:>15d} {prod_summary['total_unassigned_across_all']:>15d}")
    print(f"{'Avg Visits/Plan':<40s} {test_summary['avg_visits_per_plan']:>15.1f} {prod_summary['avg_visits_per_plan']:>15.1f}")


def fetch_detailed_plan(plan_id: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Fetch full details for a single route plan including modelOutput."""
    url = f"{TIMEFOLD_BASE}/{plan_id}"
    headers = {"Accept": "application/json", "X-API-KEY": api_key}

    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code != 200:
            return None
        return r.json()
    except requests.RequestException:
        return None


def main() -> int:
    _bootstrap_env()

    parser = argparse.ArgumentParser(
        description="Fetch and analyze all Timefold FSR jobs from test and prod environments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--test-key",
        default=None,
        help="Test environment API key (default: TIMEFOLD_API_KEY env)",
    )
    parser.add_argument(
        "--prod-key",
        default=None,
        help="Production environment API key (default: TIMEFOLD_PROD_API_KEY env)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Save full analysis to JSON file",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=100,
        help="Number of items per page (default: 100)",
    )
    parser.add_argument(
        "--detailed",
        type=int,
        default=5,
        help="Number of recent plans to fetch full details for (default: 5)",
    )

    args = parser.parse_args()

    # Get API keys
    test_key = args.test_key or os.environ.get("TIMEFOLD_API_KEY", "")
    prod_key = args.prod_key or os.environ.get("TIMEFOLD_PROD_API_KEY", "")

    if not test_key and not prod_key:
        print("Error: No API keys found. Set TIMEFOLD_API_KEY or TIMEFOLD_PROD_API_KEY, "
              "or pass --test-key/--prod-key", file=sys.stderr)
        return 1

    results = {}

    # Fetch from test environment
    if test_key:
        print("Fetching route plans from TEST environment...")
        test_plans_raw = fetch_all_route_plans(test_key, args.page_size)
        print(f"  Found {len(test_plans_raw)} route plans in TEST")

        test_plans = [analyze_route_plan(p) for p in test_plans_raw]

        # Fetch detailed info for recent plans
        if args.detailed > 0:
            print(f"  Fetching detailed data for {args.detailed} most recent plans...")
            recent_ids = [p["id"] for p in test_plans[:args.detailed]]
            for i, plan_id in enumerate(recent_ids, 1):
                detailed = fetch_detailed_plan(plan_id, test_key)
                if detailed:
                    # Update the plan with detailed info
                    analyzed = analyze_route_plan(detailed)
                    # Find and update in test_plans
                    for idx, p in enumerate(test_plans):
                        if p["id"] == plan_id:
                            test_plans[idx] = analyzed
                            break
                    print(f"    {i}/{len(recent_ids)}: {plan_id[:8]}... - {analyzed['total_visits']} visits")

        test_summary = generate_summary(test_plans, "test")
        print_summary(test_summary)

        results["test"] = {
            "summary": test_summary,
            "plans": test_plans,
        }

    # Fetch from prod environment
    if prod_key:
        print("\nFetching route plans from PROD environment...")
        prod_plans_raw = fetch_all_route_plans(prod_key, args.page_size)
        print(f"  Found {len(prod_plans_raw)} route plans in PROD")

        prod_plans = [analyze_route_plan(p) for p in prod_plans_raw]

        # Fetch detailed info for recent plans
        if args.detailed > 0:
            print(f"  Fetching detailed data for {args.detailed} most recent plans...")
            recent_ids = [p["id"] for p in prod_plans[:args.detailed]]
            for i, plan_id in enumerate(recent_ids, 1):
                detailed = fetch_detailed_plan(plan_id, prod_key)
                if detailed:
                    # Update the plan with detailed info
                    analyzed = analyze_route_plan(detailed)
                    # Find and update in prod_plans
                    for idx, p in enumerate(prod_plans):
                        if p["id"] == plan_id:
                            prod_plans[idx] = analyzed
                            break
                    print(f"    {i}/{len(recent_ids)}: {plan_id[:8]}... - {analyzed['total_visits']} visits")

        prod_summary = generate_summary(prod_plans, "prod")
        print_summary(prod_summary)

        results["prod"] = {
            "summary": prod_summary,
            "plans": prod_plans,
        }

    # Compare environments if both available
    if test_key and prod_key:
        compare_environments(test_summary, prod_summary)

    # Save to file if requested
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nFull analysis saved to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
