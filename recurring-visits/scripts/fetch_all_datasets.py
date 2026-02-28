#!/usr/bin/env python3
"""
Fetch multiple Timefold FSR datasets (input + output), run metrics and continuity for each.
Stores results in a structured folder: <base_dir>/<id_short>/output.json, input.json,
continuity.csv, metrics/.

Usage:
  TIMEFOLD_API_KEY=... python3 fetch_all_datasets.py --base ../huddinge-package/solve/28-feb
  TIMEFOLD_API_KEY=... python3 fetch_all_datasets.py --base ../huddinge-package/solve/28-feb --ids id1 id2 ...
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent

# Dataset IDs from TF prod (28-feb run)
DEFAULT_IDS = [
    "48b04930-53ef-4b69-b34b-7235e97879cd",
    "b69e582b-9321-4cfe-be40-92bc27287b5e",
    "82a338b9-f14f-41a7-a9aa-9140e688000c",
    "7c002442-e72d-4274-baee-eb1edecbaafd",
    "b8e58647-1717-421a-8e81-fc05a6929ea6",
    "203cf1d6-03e9-42a7-82ca-46b011dd7ed3",
    "8a2318b9-9331-4dec-902d-507e93e74a11",
    "a9664f39-48a1-4b69-b0c4-570d009f862f",
    "41ce610c-bd67-47b8-9e62-7820f87ffcdd",
    "2b36ebdb-b8e6-4993-85e1-3226eb252c08",
    "5ff7929f-738b-4cfa-9add-845c03089b0d",
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch multiple TF FSR datasets and run metrics + continuity")
    ap.add_argument("--base", type=Path, required=True, help="Base dir, e.g. ../huddinge-package/solve/28-feb")
    ap.add_argument("--ids", nargs="*", default=None, help="Dataset IDs (default: built-in list)")
    ap.add_argument("--api-key", default=None, help="Timefold API key (default: TIMEFOLD_API_KEY env)")
    args = ap.parse_args()

    import os
    api_key = args.api_key or os.environ.get("TIMEFOLD_API_KEY", "")
    if not api_key:
        print("Error: Set TIMEFOLD_API_KEY or pass --api-key", file=sys.stderr)
        return 1

    ids = args.ids or DEFAULT_IDS
    base = args.base if args.base.is_absolute() else (Path.cwd() / args.base)
    base.mkdir(parents=True, exist_ok=True)

    fetch_script = _SCRIPT_DIR / "fetch_timefold_solution.py"
    env = {**os.environ, "TIMEFOLD_API_KEY": api_key}

    # Paths relative to scripts dir (fetch script cwd)
    base_str = str(args.base) if not args.base.is_absolute() else str(base)
    if not base_str.startswith("..") and not Path(base_str).is_absolute():
        base_str = ".." + ("/" + base_str if base_str else "")

    ok = 0
    fail = 0
    for i, dataset_id in enumerate(ids, 1):
        short_id = dataset_id.split("-")[0] if "-" in dataset_id else dataset_id[:8]
        out_dir = base / short_id
        out_dir.mkdir(parents=True, exist_ok=True)
        save_path = Path(base_str) / short_id / "output.json"
        metrics_path = Path(base_str) / short_id / "metrics"

        print(f"\n[{i}/{len(ids)}] {short_id} ...")
        cmd = [
            sys.executable,
            str(fetch_script),
            dataset_id,
            "--save", str(save_path),
            "--metrics-dir", str(metrics_path),
        ]
        r = subprocess.run(cmd, cwd=str(_SCRIPT_DIR), env=env)
        if r.returncode == 0:
            ok += 1
        else:
            fail += 1
            print(f"  -> failed (exit {r.returncode})", file=sys.stderr)

    print(f"\nDone: {ok} ok, {fail} failed. Base: {base.resolve()}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
