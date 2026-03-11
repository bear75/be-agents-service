#!/usr/bin/env python3
"""
Build continuity pool variants for pool sizes 5, 8, 10 and generate preferred/wait-min/combo payloads.

Given base FSR input and first-run FSR output:
  1. For each --max-per-client in (5, 8, 10): run build_continuity_pools (first-run), patch base input.
  2. Run prepare_continuity_test_variants on each patched input to produce preferred (weights 2, 10, 20), wait-min, combo.

Output layout:
  <out-dir>/pool_5/  input_pool5.json, pools.json, input_preferred_vehicles_weight*.json, input_wait_min_*.json, input_combo_*.json
  <out-dir>/pool_8/  ...
  <out-dir>/pool_10/ ...

Usage:
  python run_pool_campaign.py --base-input path/to/fsr-input.json --first-run-output path/to/fsr-output.json --out-dir continuity/variants
  python run_pool_campaign.py --base-input in.json --first-run-output out.json --out-dir . --preferred-weights 2 10 20
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _script_dir() -> Path:
    return Path(__file__).resolve().parent


POOL_SIZES = (5, 8, 10)


def run_build_pools(
    base_input: Path,
    first_run_output: Path,
    pool_dir: Path,
    max_per_client: int,
) -> bool:
    """Run build_continuity_pools (first-run) and patch FSR input into pool_dir. Returns True on success."""
    pools_json = pool_dir / "pools.json"
    patched_input = pool_dir / f"input_pool{max_per_client}.json"
    cmd = [
        sys.executable,
        str(_script_dir() / "build_continuity_pools.py"),
        "--source",
        "first-run",
        "--input",
        str(base_input),
        "--output",
        str(first_run_output),
        "--out",
        str(pools_json),
        "--max-per-client",
        str(max_per_client),
        "--patch-fsr-input",
        str(base_input),
        "--patched-input",
        str(patched_input),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=_script_dir())
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return False
    return True


def run_prepare_variants(
    patched_input: Path,
    out_dir: Path,
    preferred_weights: list[int],
) -> bool:
    """Run prepare_continuity_test_variants. Returns True on success."""
    cmd = [
        sys.executable,
        str(_script_dir() / "prepare_continuity_test_variants.py"),
        "--input",
        str(patched_input),
        "--out-dir",
        str(out_dir),
    ]
    if preferred_weights:
        cmd.append("--preferred-weights")
        cmd.extend(str(w) for w in preferred_weights)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=_script_dir())
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate pool 5/8/10 continuity variants and preferred/wait-min/combo payloads.",
    )
    parser.add_argument(
        "--base-input",
        type=Path,
        required=True,
        help="Base FSR input JSON (unpatched).",
    )
    parser.add_argument(
        "--first-run-output",
        type=Path,
        required=True,
        help="First-run FSR output JSON (used to build continuity pools).",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("continuity/variants"),
        help="Output directory; creates pool_5/, pool_8/, pool_10/ under it (default: continuity/variants).",
    )
    parser.add_argument(
        "--preferred-weights",
        type=int,
        nargs="*",
        default=[2, 10, 20],
        metavar="W",
        help="Preferred-vehicles weights for variant generation (default: 2 10 20).",
    )
    parser.add_argument(
        "--pool-sizes",
        type=int,
        nargs="*",
        default=list(POOL_SIZES),
        metavar="N",
        help=f"Pool sizes to generate (default: {list(POOL_SIZES)}).",
    )
    args = parser.parse_args()

    if not args.base_input.exists():
        print(f"Error: base input not found: {args.base_input}", file=sys.stderr)
        return 1
    if not args.first_run_output.exists():
        print(f"Error: first-run output not found: {args.first_run_output}", file=sys.stderr)
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)

    for n in args.pool_sizes:
        pool_dir = args.out_dir / f"pool_{n}"
        pool_dir.mkdir(parents=True, exist_ok=True)
        print(f"--- Pool size {n} ---")
        if not run_build_pools(
            args.base_input,
            args.first_run_output,
            pool_dir,
            n,
        ):
            print(f"Error: build_continuity_pools failed for max_per_client={n}", file=sys.stderr)
            return 1
        patched = pool_dir / f"input_pool{n}.json"
        if not patched.exists():
            print(f"Error: patched input not created: {patched}", file=sys.stderr)
            return 1
        if not run_prepare_variants(patched, pool_dir, args.preferred_weights):
            print(f"Error: prepare_continuity_test_variants failed for pool_{n}", file=sys.stderr)
            return 1

    print(f"\nDone. Variants written under {args.out_dir}/ (pool_5/, pool_8/, pool_10/).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
