#!/usr/bin/env python3
"""
Quick continuity campaign: Submit multiple 3h runs without waiting.
Focuses on continuity optimization with different pool sizes and weight profiles.
"""

import argparse
import json
import os
import re
import requests
import sys
from datetime import datetime
from pathlib import Path

TIMEFOLD_BASE_URL = "https://app.timefold.ai/api/models/field-service-routing/v1"

# Continuity campaign variants
VARIANTS = [
    {
        "name": "pool5_continuity_heavy",
        "description": "Pool size 5 with high continuity weight",
        "pool_size": 5,
        "overrides": {
            "preferVisitVehicleMatchPreferredVehiclesWeight": 20,
        },
    },
    {
        "name": "pool7_balanced",
        "description": "Pool size 7 with balanced weights",
        "pool_size": 7,
        "overrides": {
            "preferVisitVehicleMatchPreferredVehiclesWeight": 10,
        },
    },
    {
        "name": "pool8_preferred",
        "description": "Pool size 8 with preferred vehicles",
        "pool_size": 8,
        "overrides": {
            "preferVisitVehicleMatchPreferredVehiclesWeight": 15,
        },
    },
    {
        "name": "pool10_continuity_heavy",
        "description": "Pool size 10 with continuity-heavy profile",
        "pool_size": 10,
        "overrides": {
            "preferVisitVehicleMatchPreferredVehiclesWeight": 20,
        },
    },
    {
        "name": "baseline_no_pools",
        "description": "Baseline with no pools for comparison",
        "pool_size": None,
        "overrides": {},
    },
]


def load_env() -> str | None:
    """Load TIMEFOLD_API_KEY from env file or environment."""
    api_key = os.environ.get("TIMEFOLD_API_KEY", "").strip()
    if api_key:
        return api_key
    env_file = Path.home() / ".config" / "caire" / "env"
    if env_file.exists():
        pattern = re.compile(r"^(?:export\s+)?TIMEFOLD_API_KEY=(.*)$")
        for line in env_file.read_text().splitlines():
            m = pattern.match(line.strip())
            if m:
                val = m.group(1).strip().strip("'\"")
                if val:
                    return val
    return None


def prepare_variant(input_data: dict, variant: dict) -> dict:
    """Prepare input data for a specific variant."""
    payload = json.loads(json.dumps(input_data))  # Deep copy
    
    # Ensure config structure exists
    if "config" not in payload:
        payload["config"] = {}
    config = payload["config"]
    
    # Set 3h termination
    if "run" not in config:
        config["run"] = {}
    config["run"]["termination"] = {"spentLimit": "PT3H"}
    config["run"]["maxThreadCount"] = 1  # 1 thread per job for queue management
    
    # Apply weight overrides
    if "model" not in config:
        config["model"] = {}
    if "overrides" not in config["model"]:
        config["model"]["overrides"] = {}
    
    for key, value in variant["overrides"].items():
        config["model"]["overrides"][key] = value
    
    # Set run name
    config["run"]["name"] = f"Continuity Campaign - {variant['name']}"
    
    # Note: Pool building would require a first-run output, which we don't have here
    # For now, we'll submit with weight overrides only
    # The pools would need to be built separately using build_pools.py
    
    return payload


def submit_variant(
    payload: dict,
    variant: dict,
    api_key: str,
    configuration_id: str = "",
) -> str | None:
    """Submit a variant to Timefold and return route plan ID."""
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    
    # Add configuration ID if provided
    if configuration_id:
        payload["config"]["run"]["configurationId"] = configuration_id
    
    try:
        response = requests.post(
            f"{TIMEFOLD_BASE_URL}/route-plans",
            headers=headers,
            json=payload,
            timeout=60,
        )
        
        if response.status_code in [200, 201, 202]:
            result = response.json()
            route_plan_id = result.get("id", "unknown")
            status = result.get("solverStatus", "unknown")
            print(f"  ✅ {variant['name']}: {route_plan_id} (status: {status})")
            return route_plan_id
        else:
            error_text = response.text[:500]
            print(f"  ❌ {variant['name']}: HTTP {response.status_code}")
            print(f"     {error_text}")
            return None
            
    except requests.RequestException as e:
        print(f"  ❌ {variant['name']}: Network error - {e}")
        return None


def main():
    ap = argparse.ArgumentParser(
        description="Submit multiple continuity campaign runs (3h each, no wait)"
    )
    ap.add_argument(
        "input_file",
        type=Path,
        help="Input FSR JSON file",
    )
    ap.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Timefold API key (default: from env or ~/.config/caire/env)",
    )
    ap.add_argument(
        "--configuration-id",
        type=str,
        default="",
        help="Timefold configuration profile ID",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory for route plan IDs (default: same as input)",
    )
    ap.add_argument(
        "--delay",
        type=int,
        default=2,
        help="Seconds between submissions (default: 2)",
    )
    args = ap.parse_args()
    
    # Load API key
    api_key = args.api_key or load_env()
    if not api_key:
        print("Error: TIMEFOLD_API_KEY required", file=sys.stderr)
        print("Set env var, pass --api-key, or create ~/.config/caire/env", file=sys.stderr)
        return 1
    
    # Load input file
    if not args.input_file.exists():
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        return 1
    
    with open(args.input_file, encoding="utf-8") as f:
        input_data = json.load(f)
    
    # Determine output directory
    out_dir = args.out_dir or args.input_file.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Route plan IDs file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ids_file = out_dir / f"continuity_campaign_route_plan_ids_{timestamp}.txt"
    
    print("=" * 60)
    print("  CONTINUITY CAMPAIGN - QUICK SUBMIT")
    print(f"  Input: {args.input_file}")
    print(f"  Variants: {len(VARIANTS)}")
    print(f"  Output: {ids_file}")
    print("=" * 60)
    print()
    
    route_plan_ids = []
    
    # Submit each variant
    for i, variant in enumerate(VARIANTS, 1):
        print(f"[{i}/{len(VARIANTS)}] {variant['name']}: {variant['description']}")
        
        # Prepare payload
        payload = prepare_variant(input_data, variant)
        
        # Submit (no wait)
        route_plan_id = submit_variant(payload, variant, api_key, args.configuration_id)
        
        if route_plan_id:
            route_plan_ids.append({
                "variant": variant["name"],
                "description": variant["description"],
                "route_plan_id": route_plan_id,
                "submitted_at": datetime.now().isoformat(),
            })
        
        # Delay between submissions (except last)
        if i < len(VARIANTS) and args.delay > 0:
            import time
            time.sleep(args.delay)
    
    # Save route plan IDs
    if route_plan_ids:
        with open(ids_file, "w", encoding="utf-8") as f:
            f.write(f"# Continuity Campaign Route Plan IDs\n")
            f.write(f"# Submitted: {datetime.now().isoformat()}\n")
            f.write(f"# Input: {args.input_file}\n\n")
            for entry in route_plan_ids:
                f.write(f"{entry['route_plan_id']}  # {entry['variant']}: {entry['description']}\n")
        
        print()
        print("=" * 60)
        print(f"  ✅ Submitted {len(route_plan_ids)}/{len(VARIANTS)} runs")
        print(f"  📝 Route plan IDs saved to: {ids_file}")
        print("=" * 60)
        print()
        print("To fetch results later, use:")
        print(f"  python3 fetch_timefold_solution.py <route_plan_id> --save output.json")
        print()
        print("Route plan IDs:")
        for entry in route_plan_ids:
            print(f"  {entry['route_plan_id']}  ({entry['variant']})")
    else:
        print()
        print("❌ No runs submitted successfully", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
