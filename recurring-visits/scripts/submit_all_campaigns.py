#!/usr/bin/env python3
"""
Submit all continuity campaign variants to Timefold in parallel, splitting across two API keys
to reduce queue load (caire-test and caire-production tenants).

Reads variant paths from continuity/variants (pool_5, pool_8, pool_10) and optional roster inputs.
Writes manifest JSON and MD listing strategy_name, route_plan_id, tenant.

Usage:
  cd recurring-visits
  python3 scripts/submit_all_campaigns.py \
    --continuity-dir huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/continuity \
    --api-key-test tf_p_96b5507b-57be-4ab6-b0a6-08a9d3372938 \
    --api-key-prod tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def _script_dir() -> Path:
    return Path(__file__).resolve().parent


# Campaign matrix: (subpath under continuity dir, strategy label)
POOL_STRATEGIES = [
    ("variants/pool_5/input_preferred_vehicles_weight2.json", "preferred_2_pool5"),
    ("variants/pool_5/input_preferred_vehicles_weight10.json", "preferred_10_pool5"),
    ("variants/pool_5/input_preferred_vehicles_weight20.json", "preferred_20_pool5"),
    ("variants/pool_5/input_wait_min_weight3.json", "wait_min_pool5"),
    ("variants/pool_5/input_combo_preferred_and_wait_min.json", "combo_pool5"),
    ("variants/pool_5/input_pool5.json", "required_pool5"),
    ("variants/pool_8/input_preferred_vehicles_weight2.json", "preferred_2_pool8"),
    ("variants/pool_8/input_preferred_vehicles_weight10.json", "preferred_10_pool8"),
    ("variants/pool_8/input_preferred_vehicles_weight20.json", "preferred_20_pool8"),
    ("variants/pool_8/input_wait_min_weight3.json", "wait_min_pool8"),
    ("variants/pool_8/input_combo_preferred_and_wait_min.json", "combo_pool8"),
    ("variants/pool_8/input_pool8.json", "required_pool8"),
    ("variants/pool_10/input_preferred_vehicles_weight2.json", "preferred_2_pool10"),
    ("variants/pool_10/input_preferred_vehicles_weight10.json", "preferred_10_pool10"),
    ("variants/pool_10/input_preferred_vehicles_weight20.json", "preferred_20_pool10"),
    ("variants/pool_10/input_wait_min_weight3.json", "wait_min_pool10"),
    ("variants/pool_10/input_combo_preferred_and_wait_min.json", "combo_pool10"),
    ("variants/pool_10/input_pool10.json", "required_pool10"),
]
ROSTER_STRATEGIES = [
    ("input_roster_preferred.json", "roster_preferred"),
    ("input_roster_required.json", "roster_required"),
]


def submit_one(
    input_path: Path,
    api_key: str,
    strategy_name: str,
    tenant: str,
) -> tuple[str | None, str]:
    """Run submit_to_timefold.py solve; return (route_plan_id or None, stderr)."""
    cmd = [
        sys.executable,
        str(_script_dir() / "submit_to_timefold.py"),
        "solve",
        str(input_path.resolve()),
        "--skip-validate",
        "--api-key",
        api_key,
        "--no-register-darwin",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=_script_dir().parent)
    out = result.stdout + "\n" + result.stderr
    match = re.search(r"Route plan ID:\s*([a-f0-9-]+)", out)
    plan_id = match.group(1) if match else None
    if result.returncode != 0:
        return None, result.stderr or result.stdout or "unknown error"
    return plan_id, ""


def main() -> int:
    ap = argparse.ArgumentParser(description="Submit all campaign variants to Timefold (two tenants).")
    ap.add_argument(
        "--continuity-dir",
        type=Path,
        default=Path("huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/continuity"),
        help="Continuity directory containing variants/ and optional roster inputs.",
    )
    ap.add_argument("--api-key-test", type=str, required=True, help="Timefold API key (caire-test tenant).")
    ap.add_argument("--api-key-prod", type=str, required=True, help="Timefold API key (caire-production tenant).")
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Only list inputs that would be submitted.",
    )
    args = ap.parse_args()

    base = args.continuity_dir.resolve()
    if not base.exists():
        print(f"Error: continuity dir not found: {base}", file=sys.stderr)
        return 1

    # Build list of (absolute path, strategy_name)
    jobs: list[tuple[Path, str]] = []
    for subpath, label in POOL_STRATEGIES:
        p = base / subpath
        if p.exists():
            jobs.append((p, label))
        else:
            print(f"Skip (missing): {p}", file=sys.stderr)
    for subpath, label in ROSTER_STRATEGIES:
        p = base / subpath
        if p.exists():
            jobs.append((p, label))
        else:
            print(f"Skip (missing): {p}", file=sys.stderr)

    if not jobs:
        print("Error: no variant inputs found.", file=sys.stderr)
        return 1

    # Alternate keys: even index = test, odd = prod
    keys = [args.api_key_test, args.api_key_prod]
    tenants = ["caire-test", "caire-production"]

    if args.dry_run:
        for i, (path, name) in enumerate(jobs):
            tenant = tenants[i % 2]
            print(f"  {name}: {path} -> {tenant}")
        print(f"Total: {len(jobs)} submissions")
        return 0

    manifest: list[dict] = []
    for i, (input_path, strategy_name) in enumerate(jobs):
        api_key = keys[i % 2]
        tenant = tenants[i % 2]
        print(f"Submitting {strategy_name} ({tenant})...", flush=True)
        plan_id, err = submit_one(input_path, api_key, strategy_name, tenant)
        if plan_id:
            manifest.append({
                "strategy": strategy_name,
                "route_plan_id": plan_id,
                "tenant": tenant,
                "input": str(input_path),
            })
            print(f"  -> {plan_id}")
        else:
            print(f"  FAILED: {err[:200]}", file=sys.stderr)
            manifest.append({
                "strategy": strategy_name,
                "route_plan_id": None,
                "tenant": tenant,
                "error": err[:500],
            })

    # Write manifest
    manifest_path = base / "campaign_manifest_submitted.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest: {manifest_path}")

    md_path = base / "campaign_manifest_submitted.md"
    lines = [
        "# Campaign submissions (night run)",
        "",
        "| Strategy | Route plan ID | Tenant |",
        "|----------|----------------|--------|",
    ]
    for m in manifest:
        rid = m.get("route_plan_id") or m.get("error", "?")[:40]
        lines.append(f"| {m['strategy']} | {rid} | {m['tenant']} |")
    lines.append("")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Summary: {md_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
