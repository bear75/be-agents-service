#!/usr/bin/env python3
"""
Huddinge v3/22 multi-strategy optimization campaign: 4 input variants x 4 weight profiles = 16 solves.

Input variants (under campaign dir):
  - input_trimmed.json
  - input_pool8_preferred.json
  - input_pool12_preferred.json
  - input_pool8_extra_vehicle.json

Each run includes:
  - **Custom soft weights** in `config.model.overrides` (see WEIGHT_PROFILES: preferred vehicles,
    travel, wait, time windows, max soft shift travel). These **merge** with the chosen
    `--configuration-id` profile in Timefold.
  - **Termination:** PT5H spent limit, PT30M unimproved.
Default **maxThreadCount is 2** — balance between solver speed and queue slots (~2 slots/job).
Use `--max-thread-count 1` to maximize parallel accepted jobs; `4` uses ~4 slots/job (~10 concurrent).

Submits via scripts/timefold/submit.py without waiting.

Usage:
  cd be-agent-service
  python3 scripts/campaigns/v3_22_optimization_campaign.py --dry-run
  TIMEFOLD_API_KEY=... python3 scripts/campaigns/v3_22_optimization_campaign.py --configuration-id Caire_prod_pilot_20min
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = SCRIPTS_ROOT.parent
TIMEFOLD_SUBMIT = SCRIPTS_ROOT / "timefold" / "submit.py"

DEFAULT_CAMPAIGN_DIR = (
    REPO_ROOT
    / "recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/22/campaign_20260322"
)

INPUT_VARIANTS: list[tuple[str, str]] = [
    ("trimmed", "input_trimmed.json"),
    ("pool8", "input_pool8_preferred.json"),
    ("pool12", "input_pool12_preferred.json"),
    ("pool8_extra", "input_pool8_extra_vehicle.json"),
]

# Merged into payload as config.model.overrides (on top of configuration profile).
# Keys match Timefold modelConfiguration / overnight_pool_campaign pattern.
WEIGHT_PROFILES: list[dict[str, object]] = [
    {
        "name": "efficiency-first",
        "desc": "Low preferred weight, high travel, moderate wait",
        "overrides": {
            "preferVisitVehicleMatchPreferredVehiclesWeight": 1,
            "minimizeTravelTimeWeight": 6,
            "minimizeWaitingTimeWeight": 2,
            "preferredVisitTimeWindowWeight": 3,
            "maxSoftShiftTravelTimeWeight": 1,
        },
    },
    {
        "name": "balanced",
        "desc": "Campaign baseline: moderate preferred + travel",
        "overrides": {
            "preferVisitVehicleMatchPreferredVehiclesWeight": 10,
            "minimizeTravelTimeWeight": 4,
            "minimizeWaitingTimeWeight": 0,
            "preferredVisitTimeWindowWeight": 3,
            "maxSoftShiftTravelTimeWeight": 1,
        },
    },
    {
        "name": "continuity-heavy",
        "desc": "Strong preferred-vehicle (continuity) signal",
        "overrides": {
            "preferVisitVehicleMatchPreferredVehiclesWeight": 20,
            "minimizeTravelTimeWeight": 4,
            "minimizeWaitingTimeWeight": 0,
            "preferredVisitTimeWindowWeight": 3,
            "maxSoftShiftTravelTimeWeight": 1,
        },
    },
    {
        "name": "combo",
        "desc": "Travel + wait minimization with moderate preferred",
        "overrides": {
            "preferVisitVehicleMatchPreferredVehiclesWeight": 10,
            "minimizeTravelTimeWeight": 3,
            "minimizeWaitingTimeWeight": 3,
            "preferredVisitTimeWindowWeight": 3,
            "maxSoftShiftTravelTimeWeight": 1,
        },
    },
]


def apply_campaign_config(
    payload: dict,
    run_name: str,
    overrides: dict[str, int],
    max_thread_count: int = 2,
) -> dict:
    """Return deep copy with config.run + config.model.overrides (custom TF weights)."""
    data = copy.deepcopy(payload)
    config = data.setdefault("config", {})
    run = config.setdefault("run", {})
    run["name"] = run_name
    run["termination"] = {
        "spentLimit": "PT5H",
        "unimprovedSpentLimit": "PT30M",
    }
    # Timefold concurrent capacity: roughly one slot per thread (cap 4).
    run["maxThreadCount"] = max(1, min(4, max_thread_count))
    model = config.setdefault("model", {})
    model["overrides"] = dict(overrides)
    return data


def load_api_key(explicit: str | None) -> str | None:
    if explicit and explicit.strip():
        return explicit.strip()
    k = os.environ.get("TIMEFOLD_API_KEY", "").strip()
    if k:
        return k
    env_file = Path.home() / ".config" / "caire" / "env"
    if env_file.exists():
        pattern = re.compile(r"^(?:export\s+)?TIMEFOLD_API_KEY=(.*)$")
        for line in env_file.read_text(encoding="utf-8").splitlines():
            m = pattern.match(line.strip())
            if m:
                val = m.group(1).strip().strip("'\"")
                if val:
                    return val
    return None


def submit_one(
    input_path: Path,
    api_key: str,
    strategy_name: str,
    configuration_id: str,
    delay_after: int,
) -> str | None:
    """Submit one solve; return route plan id or None."""
    cmd = [
        sys.executable,
        str(TIMEFOLD_SUBMIT),
        "solve",
        str(input_path),
        "--api-key",
        api_key,
        "--no-register-darwin",
        "--skip-validate",
        "--strategy",
        strategy_name,
        "--algorithm",
        strategy_name,
        "--hypothesis",
        f"v3/22 campaign: {strategy_name}",
        "--dataset",
        "huddinge-v3-22",
        "--batch",
        datetime.now(timezone.utc).strftime("%d-%b-v322").lower(),
    ]
    if configuration_id:
        cmd.extend(["--configuration-id", configuration_id])

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    out = result.stdout + "\n" + result.stderr
    match = re.search(r"Route plan ID:\s*([a-f0-9-]+)", out, re.I)
    if match:
        if delay_after > 0:
            time.sleep(delay_after)
        return match.group(1)

    if "429" in out and "Too many concurrent" in out:
        print(f"  Queue full; stdout/stderr:\n{out[:1200]}", file=sys.stderr)
    else:
        print(f"  SUBMIT FAILED ({strategy_name}):\n{out[:800]}", file=sys.stderr)
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Huddinge v3/22 optimization campaign (16 solves)")
    ap.add_argument(
        "--campaign-dir",
        type=Path,
        default=DEFAULT_CAMPAIGN_DIR,
        help="Campaign directory containing input_*.json files",
    )
    ap.add_argument(
        "--configuration-id",
        type=str,
        default=os.environ.get("TIMEFOLD_CONFIGURATION_ID", "Caire_prod_pilot_20min"),
        help="Timefold configuration profile id",
    )
    ap.add_argument("--api-key", type=str, default=None)
    ap.add_argument("--dry-run", action="store_true", help="Build prepared inputs only, no API calls")
    ap.add_argument("--delay", type=int, default=30, help="Seconds between submissions (default 30)")
    ap.add_argument(
        "--max-retries",
        type=int,
        default=5,
        help="Retries per submission when HTTP 429 queue full",
    )
    ap.add_argument(
        "--max-thread-count",
        type=int,
        default=2,
        metavar="N",
        help="Solver threads per job (1–4). Default 2 (balance speed vs queue). "
        "1 ≈ 1 slot/job (max parallel runs); 4 ≈ 4 slots/job (~10 concurrent large jobs).",
    )
    args = ap.parse_args()

    campaign_dir: Path = args.campaign_dir
    prepared_dir = campaign_dir / "prepared"
    prepared_dir.mkdir(parents=True, exist_ok=True)

    api_key = load_api_key(args.api_key)

    manifest: dict = {
        "submitted_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign_dir": str(campaign_dir.resolve()),
        "configuration_id": args.configuration_id,
        "submission_mode": "dry_run" if args.dry_run else "live",
        "api_key_loaded": bool(api_key),
        "max_thread_count": args.max_thread_count,
        "runs": [],
    }

    print("=" * 72)
    print("  Huddinge v3/22 optimization campaign — 16 prepared solves")
    print(f"  Campaign dir: {campaign_dir}")
    print(f"  Prepared:     {prepared_dir}")
    print(f"  Mode:         {'DRY RUN' if args.dry_run else 'SUBMIT'}")
    print(f"  Threads/job:  {args.max_thread_count}  (default 2; use 1 for max parallel queue)")
    print("=" * 72)

    for variant_slug, fname in INPUT_VARIANTS:
        src = campaign_dir / fname
        if not src.exists():
            print(f"Error: missing input variant file: {src}", file=sys.stderr)
            return 1

    for variant_slug, fname in INPUT_VARIANTS:
        src = campaign_dir / fname
        with open(src, encoding="utf-8") as f:
            base_payload = json.load(f)

        for profile in WEIGHT_PROFILES:
            name = str(profile["name"])
            overrides = profile["overrides"]
            assert isinstance(overrides, dict)
            strategy = f"v322-{variant_slug}-{name}"
            run_name = f"v3/22 {variant_slug} — {name}"
            payload = apply_campaign_config(
                base_payload,
                run_name,
                overrides,  # type: ignore[arg-type]
                max_thread_count=args.max_thread_count,
            )

            out_name = f"{strategy}.json"
            out_path = prepared_dir / out_name
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            print(f"Wrote {out_path}")

            entry: dict = {
                "variant": variant_slug,
                "profile": name,
                "strategy": strategy,
                "prepared_input": str(out_path.resolve()),
                "route_plan_id": None,
            }

            if args.dry_run:
                manifest["runs"].append(entry)
                continue

            if not api_key:
                print("Error: TIMEFOLD_API_KEY required for submit (or --dry-run)", file=sys.stderr)
                return 1

            plan_id: str | None = None
            for attempt in range(1, args.max_retries + 1):
                plan_id = submit_one(
                    out_path,
                    api_key,
                    strategy,
                    args.configuration_id,
                    args.delay,
                )
                if plan_id:
                    break
                if attempt < args.max_retries:
                    wait = 120 * attempt
                    print(f"  Retry {attempt}/{args.max_retries} after {wait}s...")
                    time.sleep(wait)

            entry["route_plan_id"] = plan_id
            manifest["runs"].append(entry)
            if plan_id:
                print(f"  -> {strategy}  Route plan ID: {plan_id}")
            else:
                print(f"  -> FAILED: {strategy}", file=sys.stderr)

    manifest_path = campaign_dir / "campaign_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\nManifest written: {manifest_path}")

    if args.dry_run:
        print("\nDry run complete. No submissions performed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
