#!/usr/bin/env python3
"""
Fetch completed solutions for a v3/22 campaign manifest and run metrics + continuity.

Reads campaign_manifest.json (from v3_22_optimization_campaign.py), then for each run
with a route_plan_id calls scripts/timefold/fetch.py to save output and metrics.

Usage:
  cd be-agent-service
  TIMEFOLD_API_KEY=... python3 scripts/campaigns/v3_22_fetch_campaign_results.py \\
    --manifest recurring-visits/.../campaign_20260322/campaign_manifest.json

Options:
  --skip-pending   Skip runs that are not SOLVING_COMPLETED (poll not implemented; re-run later)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = SCRIPTS_ROOT.parent
FETCH = SCRIPTS_ROOT / "timefold" / "fetch.py"


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch v3/22 campaign results from manifest")
    ap.add_argument("--manifest", type=Path, required=True, help="campaign_manifest.json")
    ap.add_argument(
        "--results-dir",
        type=Path,
        default=None,
        help="Base directory for outputs (default: <campaign_dir>/results)",
    )
    ap.add_argument(
        "--skip-pending",
        action="store_true",
        help="Skip entries where fetch fails (e.g. still solving)",
    )
    args = ap.parse_args()

    if not args.manifest.exists():
        print(f"Error: manifest not found: {args.manifest}", file=sys.stderr)
        return 1

    with open(args.manifest, encoding="utf-8") as f:
        manifest = json.load(f)

    campaign_dir = Path(manifest.get("campaign_dir", args.manifest.parent))
    results_base = args.results_dir or (campaign_dir / "results")
    results_base.mkdir(parents=True, exist_ok=True)

    runs = manifest.get("runs") or []
    failed = 0
    for run in runs:
        rid = run.get("route_plan_id")
        strategy = run.get("strategy") or f"{run.get('variant')}-{run.get('profile')}"
        if not rid:
            print(f"Skip (no id): {strategy}")
            continue
        out_dir = results_base / str(strategy)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_json = out_dir / "output.json"
        metrics_dir = out_dir / "metrics"

        cmd = [
            sys.executable,
            str(FETCH),
            str(rid),
            "--save",
            str(out_json),
            "--metrics-dir",
            str(metrics_dir),
        ]
        print(f"\n--- {strategy} ({rid}) ---")
        r = subprocess.run(cmd, cwd=str(REPO_ROOT))
        if r.returncode != 0:
            failed += 1
            if not args.skip_pending:
                print(f"Warning: fetch failed for {strategy}", file=sys.stderr)

    if failed:
        print(f"\nCompleted with {failed} fetch failure(s). Re-run when solves finish.", file=sys.stderr)
        return 1 if not args.skip_pending else 0
    print("\nAll fetches completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
