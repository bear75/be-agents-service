#!/usr/bin/env python3
"""
Run full workflow: fetch solution → metrics → analyze → trim (build from-patch) →
submit from-patch → store new route plan ID → fetch patch solution → un-metrics (solve_report --exclude-inactive) → analyze.

Trimming uses build_from_patch with trim-to-visit-span: shifts with visits (and break)
get minStartTime/maxEndTime = first visit start → last visit end (idle and breaks removed).

Usage:
  cd docs_2.0/recurring-visits/scripts

  TIMEFOLD_API_KEY=tf_p_... python3 run_fetch_trim_patch_fetch_unmetrics.py \\
    --route-plan-id 5ff7929f-738b-4cfa-9add-845c03089b0d \\
    --input ../huddinge-package/solve/25feb-stagetf-corect/export-field-service-routing-v1-c87d58dd-5200-41a9-a334-e075c54a7d94-input.json \\
    --output-dir ../huddinge-package/solve/25feb_prod \\
    --metrics-dir ../huddinge-package/metrics

  # Optional: write new route plan ID to a file and append to timefold_route_plan_ids.md
  ... --save-id-to ../huddinge-package/solve/25feb_prod/from_patch_route_plan_id.txt \\
    --append-id-to timefold_route_plan_ids.md

  # Prod config (for from-patch step)
  ... --configuration-id a43d4eec-9f53-40b3-82ad-f135adc8c7e3

If Step 4 fails with HTTP 403 "Unauthorized access to feature MODEL_API_DATASET_PATCH",
the API key or plan does not include from-patch. Use a key/plan that has the feature,
or run from-patch in Timefold staging if enabled there.

Workaround when from-patch is unavailable: build a full trimmed input and submit as
a new solve instead. See build_trimmed_input.py and .cursor/commands/fetchtimefoldsolution.md
("Workaround when from-patch is not available"). Steps: build_trimmed_input.py → submit
solve (not from-patch) → fetch/save solution → run metrics with --exclude-inactive.
"""

import argparse
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PKG = _SCRIPT_DIR.parent  # huddinge-package parent (recurring-visits)


def _run(cmd: list[str], cwd: Path | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
    cwd = cwd or _SCRIPT_DIR
    return subprocess.run(cmd, cwd=str(cwd), env=env or None)


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch → metrics → analyze → trim/patch → store ID → fetch patch → un-metrics → analyze.")
    ap.add_argument("--route-plan-id", required=True, help="Current route plan ID (e.g. first solve).")
    ap.add_argument("--input", type=Path, required=True, help="Timefold input JSON used for the solve.")
    ap.add_argument("--output-dir", type=Path, default=Path("../huddinge-package/solve/25feb_prod"), help="Directory for output and patch payload.")
    ap.add_argument("--metrics-dir", type=Path, default=Path("../huddinge-package/metrics"), help="Metrics output directory.")
    ap.add_argument("--save-id-to", type=Path, default=None, help="Write new route plan ID to this file after from-patch.")
    ap.add_argument("--append-id-to", type=Path, default=None, help="Append new ID line to this markdown file (e.g. timefold_route_plan_ids.md).")
    ap.add_argument("--configuration-id", default=None, help="Timefold configuration ID for from-patch (default: from env or script default).")
    args = ap.parse_args()

    # Resolve relative paths from the scripts directory (where the user runs)
    def _resolve(p: Path) -> Path:
        return p.resolve() if p.is_absolute() else (_SCRIPT_DIR / p).resolve()

    out_dir = _resolve(args.output_dir)
    metrics_dir = _resolve(args.metrics_dir)
    in_path = _resolve(args.input)

    out_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)

    saved_output = out_dir / "output.json"
    patch_payload = out_dir / "from_patch_payload.json"
    patch_output = out_dir / "from_patch_output.json"
    # Always save new route plan ID so we can fetch in step 6
    id_file = _resolve(args.save_id_to) if args.save_id_to is not None else (out_dir / "from_patch_route_plan_id.txt")

    env = None  # use current env (TIMEFOLD_API_KEY)

    # 1. Fetch solution, run metrics (and solve_report if we run it explicitly next)
    print("Step 1: Fetch solution and run metrics...")
    r = _run([
        sys.executable,
        str(_SCRIPT_DIR / "fetch_timefold_solution.py"),
        args.route_plan_id,
        "--save", str(saved_output),
        "--input", str(in_path),
        "--metrics-dir", str(metrics_dir),
    ], env=env)
    if r.returncode != 0:
        return r.returncode

    # 2. Analyze (solve_report: metrics already saved; this prints unassigned + empty-shifts)
    print("\nStep 2: Analyze (unassigned + empty-shifts)...")
    r = _run([
        sys.executable,
        str(_SCRIPT_DIR / "solve_report.py"),
        str(saved_output),
        "--input", str(in_path),
        "--save", str(metrics_dir),
    ], cwd=_PKG)
    if r.returncode != 0:
        return r.returncode

    # 3. Build from-patch payload (trim to visit span: removes idle + breaks)
    print("\nStep 3: Build from-patch payload (trim shifts to visit span)...")
    r = _run([
        sys.executable,
        str(_SCRIPT_DIR / "build_from_patch.py"),
        "--output", str(saved_output),
        "--input", str(in_path),
        "--out", str(patch_payload),
        "--no-timestamp",
    ], cwd=_PKG)
    if r.returncode != 0:
        return r.returncode

    # 4. Submit from-patch, wait, save output and new ID
    print("\nStep 4: Submit from-patch and wait...")
    patch_cmd = [
        sys.executable,
        str(_SCRIPT_DIR / "submit_to_timefold.py"),
        "from-patch",
        str(patch_payload),
        "--route-plan-id", args.route_plan_id,
        "--wait",
        "--save", str(patch_output),
        "--no-timestamp",
    ]
    if args.configuration_id:
        patch_cmd.extend(["--configuration-id", args.configuration_id])
    patch_cmd.extend(["--save-id", str(id_file)])
    r = _run(patch_cmd)
    if r.returncode != 0:
        return r.returncode

    # Read new route plan ID (submit writes it via --save-id)
    new_id = None
    if id_file.exists():
        new_id = id_file.read_text().strip()
    if not new_id:
        print("Warning: could not read new route plan ID; run fetch manually with the ID printed above.", file=sys.stderr)
        return 1

    # 5. Store new ID (append to markdown if requested)
    if args.append_id_to:
        append_path = args.append_id_to if args.append_id_to.is_absolute() else _SCRIPT_DIR / args.append_id_to
        line = f"| `{new_id}` | (from-patch) | {args.route_plan_id} |\n"
        with open(append_path, "a") as f:
            f.write(line)
        print(f"\nAppended new ID to {append_path}")

    # 6. Fetch patch solution (save only; metrics next with exclude-inactive)
    print("\nStep 6: Fetch patch solution...")
    r = _run([
        sys.executable,
        str(_SCRIPT_DIR / "fetch_timefold_solution.py"),
        new_id,
        "--save", str(patch_output),
    ], env=env)
    if r.returncode != 0:
        return r.returncode

    # 7. Un-metrics + analyze: solve_report with --exclude-inactive (shift = visit+travel+wait+break, no idle)
    print("\nStep 7: Solve report with exclude-inactive (un-metrics, analyze)...")
    r = _run([
        sys.executable,
        str(_SCRIPT_DIR / "solve_report.py"),
        str(patch_output),
        "--input", str(in_path),
        "--save", str(metrics_dir),
        "--exclude-inactive",
    ], cwd=_PKG)
    if r.returncode != 0:
        return r.returncode

    print("\nDone. New route plan ID:", new_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
