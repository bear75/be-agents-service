#!/usr/bin/env python3
"""
Merge variant1 and variant2 metrics into base metrics.json.
Output: one metrics file with all 3 efficiency values and shift hours.

1. All shifts and hours (base): system_efficiency_pct, shift_time_h, inactive_time_h
2. Min 1 visit (variant1): routing_efficiency_pct, shift_time_h, inactive_time_h
3. Visit-span only (variant2): routing_efficiency_pct, shift_time_h, inactive_time_h (0)

Usage:
  python merge-metrics-into-base.py <batch_dir>
  python merge-metrics-into-base.py ../huddinge-datasets/28-feb
"""
import json
import sys
from pathlib import Path


def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def find_first_json(dir_path: Path, prefix: str = "metrics_") -> Path | None:
    if not dir_path.exists():
        return None
    for f in sorted(dir_path.iterdir()):
        if f.suffix == ".json" and f.name.startswith(prefix):
            return f
    for f in sorted(dir_path.iterdir()):
        if f.suffix == ".json":
            return f
    return None


def merge_run(run_dir: Path) -> bool:
    metrics_dir = run_dir / "metrics"
    if not metrics_dir.exists():
        return False
    base_path = find_first_json(metrics_dir)
    if not base_path:
        return False
    v1_dir = metrics_dir / "variant1"
    v2_dir = metrics_dir / "variant2"
    v1_path = find_first_json(v1_dir) if v1_dir.exists() else None
    v2_path = find_first_json(v2_dir) if v2_dir.exists() else None
    base = read_json(base_path)
    if not base:
        return False
    v1 = read_json(v1_path) if v1_path else None
    v2 = read_json(v2_path) if v2_path else None

    # Build merged keys to add to all base metrics files
    extra = {}
    extra["efficiency_all_pct"] = base.get("system_efficiency_pct")
    extra["shift_hours_all"] = base.get("shift_time_h")
    extra["idle_hours_all"] = base.get("inactive_time_h")
    if v1:
        extra["efficiency_min_visit_pct"] = v1.get("routing_efficiency_pct")
        extra["shift_hours_min_visit"] = v1.get("shift_time_h")
        extra["idle_hours_min_visit"] = v1.get("inactive_time_h")
    else:
        extra["efficiency_min_visit_pct"] = None
        extra["shift_hours_min_visit"] = None
        extra["idle_hours_min_visit"] = None
    if v2:
        extra["efficiency_visit_span_pct"] = v2.get("routing_efficiency_pct")
        extra["shift_hours_visit_span"] = v2.get("shift_time_h")
        extra["idle_hours_visit_span"] = v2.get("inactive_time_h")
    else:
        extra["efficiency_visit_span_pct"] = None
        extra["shift_hours_visit_span"] = None
        extra["idle_hours_visit_span"] = None

    # Write merged keys to ALL metrics_*.json files so parser finds them
    for f in metrics_dir.glob("metrics_*.json"):
        data = read_json(f)
        if data:
            data.update(extra)
            with open(f, "w") as out:
                json.dump(data, out, indent=2)

    # Remove variant folders
    import shutil
    if v1_dir.exists():
        shutil.rmtree(v1_dir)
    if v2_dir.exists():
        shutil.rmtree(v2_dir)
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python merge-metrics-into-base.py <batch_dir>")
        sys.exit(1)
    batch_dir = Path(sys.argv[1]).resolve()
    if not batch_dir.exists():
        print(f"Error: {batch_dir} not found")
        sys.exit(1)
    merged = 0
    for run_dir in batch_dir.iterdir():
        if run_dir.is_dir() and not run_dir.name.startswith("."):
            if merge_run(run_dir):
                merged += 1
                print(f"Merged {run_dir.name}")
    print(f"Done. Merged {merged} runs.")


if __name__ == "__main__":
    main()
