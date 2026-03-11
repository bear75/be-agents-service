#!/usr/bin/env python3
"""
Submit all continuity campaign variants with delays to avoid Timefold rate limits.
Submits one variant every 60 seconds (or custom interval) to gradually queue overnight.

Usage:
  python3 submit_campaign_delayed.py \
    --continuity-dir path/to/continuity \
    --api-key YOUR_KEY \
    --delay 60
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime


def _script_dir() -> Path:
    return Path(__file__).resolve().parent


# Campaign matrix
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


def submit_one(input_path: Path, api_key: str, strategy_name: str) -> tuple[str | None, str]:
    """Run submit_to_timefold.py solve; return (route_plan_id or None, error_msg)."""
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
        # Extract error message
        err_match = re.search(r"Error: (.*)", out)
        err_msg = err_match.group(1) if err_match else (result.stderr or result.stdout or "unknown")
        return None, err_msg[:200]
    return plan_id, ""


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Submit campaign variants with delays to avoid rate limits."
    )
    ap.add_argument(
        "--continuity-dir",
        type=Path,
        required=True,
        help="Continuity directory containing variants/.",
    )
    ap.add_argument(
        "--api-key",
        type=str,
        required=True,
        help="Timefold API key.",
    )
    ap.add_argument(
        "--delay",
        type=int,
        default=60,
        help="Seconds to wait between submissions (default: 60).",
    )
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
            print(f"Skip (missing): {label}", file=sys.stderr)
    for subpath, label in ROSTER_STRATEGIES:
        p = base / subpath
        if p.exists():
            jobs.append((p, label))
        else:
            print(f"Skip (missing): {label}", file=sys.stderr)

    if not jobs:
        print("Error: no variant inputs found.", file=sys.stderr)
        return 1

    if args.dry_run:
        for i, (path, name) in enumerate(jobs):
            print(f"{i+1:2d}. {name}: {path.name}")
        print(f"\nTotal: {len(jobs)} submissions (with {args.delay}s delay between each)")
        total_time = len(jobs) * args.delay / 60
        print(f"Estimated time: {total_time:.1f} minutes")
        return 0

    manifest: list[dict] = []
    start_time = datetime.now()

    print(f"Starting campaign submission at {start_time.strftime('%H:%M:%S')}")
    print(f"Submitting {len(jobs)} variants with {args.delay}s delay between each\n")

    for i, (input_path, strategy_name) in enumerate(jobs, 1):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{i}/{len(jobs)}] {timestamp} - Submitting {strategy_name}...", flush=True)

        plan_id, err = submit_one(input_path, args.api_key, strategy_name)

        if plan_id:
            manifest.append({
                "strategy": strategy_name,
                "route_plan_id": plan_id,
                "submitted_at": timestamp,
                "input": str(input_path),
            })
            print(f"  ✓ {plan_id}", flush=True)
        else:
            print(f"  ✗ FAILED: {err}", file=sys.stderr, flush=True)
            manifest.append({
                "strategy": strategy_name,
                "route_plan_id": None,
                "submitted_at": timestamp,
                "error": err,
            })

        # Write intermediate manifest after each submission
        manifest_path = base / "campaign_manifest_delayed.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        # Delay before next submission (except for last one)
        if i < len(jobs):
            print(f"  Waiting {args.delay}s...\n", flush=True)
            time.sleep(args.delay)

    # Write final manifest
    print(f"\n{'='*60}")
    print(f"Completed at {datetime.now().strftime('%H:%M:%S')}")
    print(f"Manifest: {manifest_path}")

    md_path = base / "campaign_manifest_delayed.md"
    lines = [
        "# Campaign submissions (delayed)",
        "",
        f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Delay: {args.delay}s between submissions",
        "",
        "| # | Strategy | Route plan ID | Time |",
        "|---|----------|---------------|------|",
    ]
    for i, m in enumerate(manifest, 1):
        rid = m.get("route_plan_id") or f"FAILED: {m.get('error', '?')[:30]}"
        time_str = m.get("submitted_at", "?")
        lines.append(f"| {i} | {m['strategy']} | {rid} | {time_str} |")
    lines.append("")

    successful = sum(1 for m in manifest if m.get("route_plan_id"))
    failed = len(manifest) - successful
    lines.append(f"**Summary:** {successful} successful, {failed} failed")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Summary: {md_path}")
    print(f"\nSuccessful: {successful}/{len(manifest)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
