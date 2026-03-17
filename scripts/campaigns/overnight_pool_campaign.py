#!/usr/bin/env python3
"""
Overnight campaign runner: submit 12-15 Timefold FSR campaigns with varying
pool sizes, preferred-vehicle weights, and travel/wait balancing.

Strategy: all campaigns use preferredVehicles (soft constraint, not required/hard)
with larger employee pools so the solver can optimise travel, wait, and caregiver
continuity together.

Campaigns matrix:
  Pool sizes: 8, 10, 12, 15
  Weight profiles:
    - balanced:      preferred=10, travelWeight=default, waitWeight=default
    - continuity:    preferred=20, travelWeight=default, waitWeight=default
    - low-travel:    preferred=5,  minimizeTravelTimeWeight=5
    - low-wait:      preferred=10, minimizeWaitingTimeWeight=5
    - combo:         preferred=10, minimizeWaitingTimeWeight=3, minimizeTravelTimeWeight=3
  Baseline: no pools (unconstrained)

Total: 4 pool sizes × 3 weight profiles + baseline = 13 campaigns

Usage:
  # Dry run (build inputs only, no submission)
  python3 overnight_pool_campaign.py --dry-run

  # Submit all campaigns
  python3 overnight_pool_campaign.py

  # Custom output dir
  python3 overnight_pool_campaign.py --out-dir /path/to/campaign
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = SCRIPTS_ROOT.parent
CONTINUITY_SCRIPTS = SCRIPTS_ROOT / "continuity"
TIMEFOLD_SCRIPTS = SCRIPTS_ROOT / "timefold"

BASE_INPUT = REPO_ROOT / "recurring-visits" / "data" / "huddinge-v3" / "input" / "input_huddinge-v3_FIXED.json"
FIRST_RUN_OUTPUT = REPO_ROOT / "recurring-visits" / "data" / "huddinge-v3" / "research_output" / "exp_1773675529_iter1" / "output_20260316_164057.json"

POOL_SIZES = [8, 10, 12, 15]

WEIGHT_PROFILES: list[dict] = [
    {
        "name": "balanced",
        "desc": "Balanced preferred weight; default travel/wait",
        "overrides": {"preferVisitVehicleMatchPreferredVehiclesWeight": 10},
    },
    {
        "name": "continuity-heavy",
        "desc": "High preferred weight to maximize caregiver continuity",
        "overrides": {"preferVisitVehicleMatchPreferredVehiclesWeight": 20},
    },
    {
        "name": "low-wait",
        "desc": "Balanced preferred + minimize wait time",
        "overrides": {
            "preferVisitVehicleMatchPreferredVehiclesWeight": 10,
            "minimizeWaitingTimeWeight": 5,
        },
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
    local_env = TIMEFOLD_SCRIPTS / ".env"
    if local_env.exists():
        pattern = re.compile(r"^(?:export\s+)?TIMEFOLD_API_KEY=(.*)$")
        for line in local_env.read_text().splitlines():
            m = pattern.match(line.strip())
            if m:
                val = m.group(1).strip().strip("'\"")
                if val:
                    return val
    return None


def build_pools(
    base_input: Path,
    first_run_output: Path,
    out_dir: Path,
    pool_size: int,
) -> Path | None:
    """Build continuity pools using first-run strategy and patch FSR input."""
    pool_dir = out_dir / f"pool_{pool_size}"
    pool_dir.mkdir(parents=True, exist_ok=True)
    pools_json = pool_dir / "pools.json"
    patched_input = pool_dir / f"input_pool{pool_size}_preferred.json"

    cmd = [
        sys.executable,
        str(CONTINUITY_SCRIPTS / "build_pools.py"),
        "--source", "first-run",
        "--input", str(base_input),
        "--output", str(first_run_output),
        "--out", str(pools_json),
        "--max-per-client", str(pool_size),
        "--patch-fsr-input", str(base_input),
        "--patched-input", str(patched_input),
        "--use-preferred",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR building pools for size {pool_size}: {result.stderr[:300]}", file=sys.stderr)
        return None
    print(f"  Built pool {pool_size}: {pools_json}")
    return patched_input


def apply_weight_profile(
    source_input: Path,
    out_path: Path,
    profile: dict,
) -> bool:
    """Apply weight overrides to an FSR input JSON."""
    with open(source_input, encoding="utf-8") as f:
        payload = json.load(f)

    config = payload.get("config")
    if config is None:
        config = {}
        payload["config"] = config
    model = config.get("model") or {}
    overrides = model.get("overrides") or {}
    for k, v in profile["overrides"].items():
        overrides[k] = v
    model["overrides"] = overrides
    config["model"] = model

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return True


def make_baseline(base_input: Path, out_dir: Path) -> Path:
    """Create a baseline campaign input with no pools, no weight overrides."""
    baseline_dir = out_dir / "baseline"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    out_path = baseline_dir / "input_baseline.json"
    with open(base_input, encoding="utf-8") as f:
        payload = json.load(f)
    model = payload.get("modelInput") or payload
    for v in model.get("visits") or []:
        v.pop("requiredVehicles", None)
        v.pop("preferredVehicles", None)
    for g in model.get("visitGroups") or []:
        for v in g.get("visits") or []:
            v.pop("requiredVehicles", None)
            v.pop("preferredVehicles", None)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return out_path


def submit_campaign(
    input_path: Path,
    api_key: str,
    strategy_name: str,
    dataset: str = "huddinge-v3",
    batch: str = "",
    darwin_api: str = "",
    configuration_id: str = "",
    max_retries: int = 30,
    retry_interval: int = 120,
) -> str | None:
    """Submit a single campaign to Timefold. Retries on 429 (queue full). Returns route_plan_id or None."""
    if not batch:
        batch = datetime.now().strftime("%d-%b").lower()

    cmd = [
        sys.executable,
        str(TIMEFOLD_SCRIPTS / "submit.py"),
        "solve",
        str(input_path),
        "--skip-validate",
        "--api-key", api_key,
        "--dataset", dataset,
        "--batch", batch,
        "--strategy", strategy_name,
        "--algorithm", strategy_name,
        "--hypothesis", f"Overnight campaign: {strategy_name}",
    ]
    if configuration_id:
        cmd.extend(["--configuration-id", configuration_id])
    if darwin_api:
        cmd.extend(["--darwin-api", darwin_api])
    else:
        cmd.append("--no-register-darwin")

    for attempt in range(1, max_retries + 1):
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
        out = result.stdout + "\n" + result.stderr
        match = re.search(r"Route plan ID:\s*([a-f0-9-]+)", out)
        if match:
            return match.group(1)

        if "429" in out and "Too many concurrent" in out:
            queued_match = re.search(r"currently queued:\s*(\d+)", out)
            queued = queued_match.group(1) if queued_match else "?"
            print(f"  Queue full ({queued}/50). Waiting {retry_interval}s before retry {attempt}/{max_retries}...")
            time.sleep(retry_interval)
            continue

        print(f"  SUBMIT FAILED for {strategy_name}: {out[:300]}", file=sys.stderr)
        return None

    print(f"  SUBMIT FAILED for {strategy_name}: max retries ({max_retries}) exhausted", file=sys.stderr)
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Overnight pool campaign runner")
    ap.add_argument("--out-dir", type=Path, default=REPO_ROOT / "recurring-visits" / "data" / "huddinge-v3" / "campaigns" / datetime.now().strftime("overnight_%Y%m%d"))
    ap.add_argument("--base-input", type=Path, default=BASE_INPUT)
    ap.add_argument("--first-run-output", type=Path, default=FIRST_RUN_OUTPUT)
    ap.add_argument("--api-key", type=str, default=None)
    ap.add_argument("--darwin-api", type=str, default="http://localhost:3010")
    ap.add_argument("--configuration-id", type=str, default="", help="Timefold configuration profile ID")
    ap.add_argument("--dry-run", action="store_true", help="Build inputs only, do not submit")
    ap.add_argument("--delay", type=int, default=5, help="Seconds between submissions (default 5)")
    ap.add_argument("--retry-interval", type=int, default=120, help="Seconds to wait on queue-full 429 before retry (default 120)")
    args = ap.parse_args()

    api_key = args.api_key or load_env()
    if not api_key and not args.dry_run:
        print("Error: TIMEFOLD_API_KEY required. Set env var, pass --api-key, or create ~/.config/caire/env", file=sys.stderr)
        return 1

    if not args.base_input.exists():
        print(f"Error: base input not found: {args.base_input}", file=sys.stderr)
        return 1
    if not args.first_run_output.exists():
        print(f"Error: first-run output not found: {args.first_run_output}", file=sys.stderr)
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)
    batch_label = datetime.now().strftime("%d-%b-overnight").lower()

    print("=" * 60)
    print("  OVERNIGHT POOL CAMPAIGN")
    print(f"  Output: {args.out_dir}")
    print(f"  Pool sizes: {POOL_SIZES}")
    print(f"  Weight profiles: {[p['name'] for p in WEIGHT_PROFILES]}")
    print(f"  Mode: {'DRY RUN (build only)' if args.dry_run else 'SUBMIT'}")
    print("=" * 60)

    # Step 1: Build pools for each size
    print("\n--- Building pools ---")
    pool_inputs: dict[int, Path] = {}
    for size in POOL_SIZES:
        patched = build_pools(args.base_input, args.first_run_output, args.out_dir, size)
        if patched and patched.exists():
            pool_inputs[size] = patched
        else:
            print(f"  WARN: Pool {size} failed, skipping", file=sys.stderr)

    # Step 2: Generate weight-profile variants for each pool
    print("\n--- Generating weight-profile variants ---")
    campaigns: list[tuple[str, Path]] = []

    for size, base_patched in sorted(pool_inputs.items()):
        pool_dir = args.out_dir / f"pool_{size}"
        for profile in WEIGHT_PROFILES:
            variant_name = f"pool{size}_{profile['name']}"
            variant_path = pool_dir / f"input_{variant_name}.json"
            if apply_weight_profile(base_patched, variant_path, profile):
                campaigns.append((variant_name, variant_path))
                print(f"  {variant_name}: {profile['desc']}")

    # Step 3: Baseline (no pools)
    print("\n--- Baseline (no pools) ---")
    baseline_path = make_baseline(args.base_input, args.out_dir)
    campaigns.append(("baseline_no_pools", baseline_path))
    print(f"  baseline_no_pools: unconstrained (no preferred/required)")

    print(f"\nTotal campaigns: {len(campaigns)}")

    # Step 4: Submit
    if args.dry_run:
        print("\n--- DRY RUN: would submit ---")
        for name, path in campaigns:
            print(f"  {name}: {path}")
        manifest_path = args.out_dir / "campaign_manifest.json"
        manifest = [{"strategy": name, "input": str(path), "status": "dry-run"} for name, path in campaigns]
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"\nManifest (dry-run): {manifest_path}")
        return 0

    print("\n--- Submitting campaigns ---")
    manifest: list[dict] = []
    for i, (name, path) in enumerate(campaigns):
        print(f"\n[{i+1}/{len(campaigns)}] Submitting {name}...")
        plan_id = submit_campaign(
            path, api_key, name,
            dataset="huddinge-v3",
            batch=batch_label,
            darwin_api=args.darwin_api,
            configuration_id=args.configuration_id,
            retry_interval=args.retry_interval,
        )
        entry = {
            "strategy": name,
            "route_plan_id": plan_id,
            "input": str(path),
            "submitted_at": datetime.now().isoformat(),
            "status": "submitted" if plan_id else "failed",
        }
        manifest.append(entry)
        if plan_id:
            print(f"  -> Route plan ID: {plan_id}")
        else:
            print(f"  -> FAILED")

        if i < len(campaigns) - 1:
            time.sleep(args.delay)

    # Write manifest
    manifest_path = args.out_dir / "campaign_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    # Summary markdown
    md_lines = [
        f"# Overnight Campaign — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "All campaigns use **preferredVehicles** (soft constraint). Pools built from first-run output.",
        "",
        "| # | Strategy | Pool | Weights | Route Plan ID | Status |",
        "|---|----------|------|---------|---------------|--------|",
    ]
    for i, m in enumerate(manifest):
        pool = m["strategy"].split("_")[0] if "pool" in m["strategy"] else "none"
        weights = m["strategy"].split("_", 1)[1] if "_" in m["strategy"] else m["strategy"]
        rid = m.get("route_plan_id") or "—"
        md_lines.append(f"| {i+1} | {m['strategy']} | {pool} | {weights} | `{rid}` | {m['status']} |")
    md_lines.append("")
    md_lines.append("## Weight profiles")
    md_lines.append("")
    md_lines.append("- **balanced**: preferredVehiclesWeight=10 (default travel/wait)")
    md_lines.append("- **continuity-heavy**: preferredVehiclesWeight=20 (maximize caregiver continuity)")
    md_lines.append("- **low-wait**: preferredVehiclesWeight=10, minimizeWaitingTimeWeight=5")
    md_lines.append("- **baseline_no_pools**: no pools, no overrides (unconstrained)")
    md_lines.append("")

    md_path = args.out_dir / "CAMPAIGN_SUMMARY.md"
    with open(md_path, "w") as f:
        f.write("\n".join(md_lines))

    print(f"\n{'=' * 60}")
    print(f"  CAMPAIGN COMPLETE")
    print(f"  Submitted: {sum(1 for m in manifest if m['status'] == 'submitted')}/{len(manifest)}")
    print(f"  Failed:    {sum(1 for m in manifest if m['status'] == 'failed')}/{len(manifest)}")
    print(f"  Manifest:  {manifest_path}")
    print(f"  Summary:   {md_path}")
    print(f"{'=' * 60}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
