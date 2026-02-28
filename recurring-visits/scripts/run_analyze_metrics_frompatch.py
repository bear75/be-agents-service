#!/usr/bin/env python3
"""
Convenience wrapper: run solve_report (metrics + analysis) then build_from_patch.

Use solve_report.py for metrics + unassigned + empty-shifts in one go.
Use this script when you also want to build the from-patch payload in one command.

Usage:
  python run_analyze_metrics_frompatch.py --output solve/tf/output.json --input solve/input.json
  python run_analyze_metrics_frompatch.py --output solve/tf/output.json --input solve/input.json --metrics-dir metrics/ --from-patch-out from-patch/payload.json
"""

import argparse
import subprocess
import sys
from pathlib import Path

_PKG = Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True, help="Timefold output JSON")
    ap.add_argument("--input", type=Path, required=True, help="Timefold input JSON")
    ap.add_argument("--metrics-dir", type=Path, default=Path("metrics"))
    ap.add_argument("--from-patch-out", type=Path, default=None)
    ap.add_argument("--exclude-inactive", action="store_true", help="Pass through to solve_report (e.g. for from-patch output).")
    args = ap.parse_args()

    out_path = args.output if args.output.is_absolute() else _PKG / args.output
    in_path = args.input if args.input.is_absolute() else _PKG / args.input
    metrics_dir = args.metrics_dir if args.metrics_dir.is_absolute() else _PKG / args.metrics_dir

    if not out_path.exists() or not in_path.exists():
        print("Error: missing output or input file", file=sys.stderr)
        return 1

    rel_out = out_path.relative_to(_PKG) if out_path.is_relative_to(_PKG) else out_path
    rel_in = in_path.relative_to(_PKG) if in_path.is_relative_to(_PKG) else in_path
    scripts = _PKG / "scripts"

    # 1. solve_report (metrics + unassigned + empty-shifts)
    cmd = [sys.executable, str(scripts / "solve_report.py"), str(rel_out), "--input", str(rel_in), "--save", str(metrics_dir)]
    if args.exclude_inactive:
        cmd.append("--exclude-inactive")
    r1 = subprocess.run(cmd, cwd=str(_PKG))
    if r1.returncode != 0:
        return r1.returncode

    # 2. build_from_patch
    import json
    with open(out_path) as f:
        meta = json.load(f).get("metadata") or {}
    rid = (meta.get("id") or "unknown").replace("-", "")[:8]
    fp_out = args.from_patch_out or (_PKG / "from-patch" / f"payload_{rid}.json")
    if not fp_out.is_absolute():
        fp_out = _PKG / fp_out
    fp_out.parent.mkdir(parents=True, exist_ok=True)
    rel_fp = fp_out.relative_to(_PKG) if fp_out.is_relative_to(_PKG) else fp_out
    r2 = subprocess.run([
        sys.executable, str(scripts / "build_from_patch.py"),
        "--output", str(rel_out), "--input", str(rel_in),
        "--out", str(rel_fp), "--no-timestamp",
    ], cwd=str(_PKG))
    if r2.returncode != 0:
        return r2.returncode
    print(f"\nFrom-patch payload: {fp_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
