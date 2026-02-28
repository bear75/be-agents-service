#!/usr/bin/env python3
"""
Produce a no-break-location variant from a Timefold FSR input that has break locations.

Reads the given input JSON, deep-copies it, and removes the "location" field from
every requiredBreaks entry in every vehicle shift. Saves to the given output path.
Use this to run the same dataset with and without break location using the same
configuration profile for comparison.

Usage:
  python strip_break_location.py input_with_breakloc.json -o input_nobreakloc.json
"""

import argparse
import copy
import json
import sys
from pathlib import Path


def strip_break_locations(payload: dict) -> dict:
    """Return a deep copy of payload with 'location' removed from every requiredBreaks entry."""
    out = copy.deepcopy(payload)
    model = out.get("modelInput") or out
    vehicles = model.get("vehicles", [])
    for vehicle in vehicles:
        for shift in vehicle.get("shifts", []):
            for br in shift.get("requiredBreaks", []):
                br.pop("location", None)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove break locations from FSR input for no-break-loc variant"
    )
    parser.add_argument("input", type=Path, help="Input JSON (with break locations)")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output JSON (no break locations)")
    parser.add_argument(
        "--name",
        default=None,
        help="Override config.run.name in output (default: keep existing)",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: not found {args.input}", file=sys.stderr)
        return 1

    with open(args.input, encoding="utf-8") as f:
        payload = json.load(f)

    out = strip_break_locations(payload)
    if args.name is not None:
        if "config" not in out:
            out["config"] = {}
        if "run" not in out["config"]:
            out["config"]["run"] = {}
        out["config"]["run"]["name"] = args.name

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    model = out.get("modelInput") or out
    n_stripped = sum(
        len(s.get("requiredBreaks", []))
        for v in model.get("vehicles", [])
        for s in v.get("shifts", [])
    )
    print(f"Stripped location from {n_stripped} breaks. Wrote: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
