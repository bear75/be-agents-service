#!/usr/bin/env python3
"""
Build a trimmed input JSON by removing empty shifts and unused vehicles
from the current solution (output). Use this to start a parallel fresh solve
with fewer shifts, based on analysis of an ongoing or completed run.

Usage:
  python build_trimmed_input.py --output ../e2e_pipeline_0cf9ea85/output.json \\
    --input ../e2e_pipeline_0cf9ea85/input.json --out ../e2e_pipeline_0cf9ea85/input_trimmed.json
"""

import argparse
import json
import sys
from pathlib import Path


def _empty_shifts_from_output(output_data: dict) -> list[tuple[str, str]]:
    """Return (vehicle_id, shift_id) for shifts with empty itinerary (no VISITs)."""
    out = output_data.get("modelOutput") or output_data.get("model_output") or {}
    result: list[tuple[str, str]] = []
    for v in out.get("vehicles", []):
        vid = v.get("id", "")
        for s in v.get("shifts", []):
            sid = s.get("id", "")
            has_visit = any(
                isinstance(item, dict) and item.get("kind") == "VISIT"
                for item in s.get("itinerary", [])
            )
            if not has_visit:
                result.append((vid, sid))
    return sorted(result)


def _used_vehicles_from_output(output_data: dict) -> set[str]:
    """Return vehicle IDs that have at least one VISIT in any shift."""
    used: set[str] = set()
    out = output_data.get("modelOutput") or output_data.get("model_output") or {}
    for v in out.get("vehicles", []):
        vid = v.get("id")
        if not vid:
            continue
        for s in v.get("shifts", []):
            has_visit = any(
                isinstance(item, dict) and item.get("kind") == "VISIT"
                for item in s.get("itinerary", [])
            )
            if has_visit:
                used.add(vid)
                break
    return used


def build_trimmed_input(input_data: dict, output_data: dict) -> dict:
    """
    Return a new input dict with empty shifts and unused vehicles removed,
    so a fresh solve can run with fewer shifts (parallel to the original run).
    """
    empty_set = set(_empty_shifts_from_output(output_data))
    used_v = _used_vehicles_from_output(output_data)
    mi = input_data.get("modelInput") or input_data
    all_vids = [v["id"] for v in mi.get("vehicles", []) if v.get("id")]
    unused_vids = set(all_vids) - used_v

    new_vehicles: list[dict] = []
    for v in mi.get("vehicles", []):
        vid = v.get("id", "")
        if vid in unused_vids:
            continue
        new_shifts = [
            s for s in v.get("shifts", [])
            if (vid, s.get("id", "")) not in empty_set
        ]
        if not new_shifts:
            continue
        new_v = {**v, "shifts": new_shifts}
        new_vehicles.append(new_v)

    out_mi = {k: v for k, v in mi.items() if k != "vehicles"}
    out_mi["vehicles"] = new_vehicles
    result = {k: v for k, v in input_data.items() if k != "modelInput"}
    result["modelInput"] = out_mi
    return result


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Build trimmed input (remove empty shifts/unused vehicles) for a parallel fresh solve.",
    )
    ap.add_argument("--output", type=Path, required=True, help="Current solution output JSON.")
    ap.add_argument("--input", type=Path, required=True, help="Original input JSON.")
    ap.add_argument("--out", type=Path, required=True, help="Path for trimmed input JSON.")
    args = ap.parse_args()

    if not args.output.exists():
        print(f"Error: output not found: {args.output}", file=sys.stderr)
        return 1
    if not args.input.exists():
        print(f"Error: input not found: {args.input}", file=sys.stderr)
        return 1

    with open(args.output) as f:
        output_data = json.load(f)
    with open(args.input) as f:
        input_data = json.load(f)

    trimmed = build_trimmed_input(input_data, output_data)
    mi = trimmed.get("modelInput") or trimmed
    n_vehicles = len(mi.get("vehicles", []))
    n_shifts = sum(len(v.get("shifts", [])) for v in mi.get("vehicles", []))
    empty_set = set(_empty_shifts_from_output(output_data))
    unused_v = set(v["id"] for v in (input_data.get("modelInput") or input_data).get("vehicles", [])) - _used_vehicles_from_output(output_data)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(trimmed, f, indent=2, ensure_ascii=False)

    print(f"Trimmed input: removed {len(unused_v)} unused vehicles, {len(empty_set)} empty shifts")
    print(f"New input: {n_vehicles} vehicles, {n_shifts} shifts")
    print(f"Wrote: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
