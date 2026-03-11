#!/usr/bin/env python3
"""
Prepare test variant payloads from a continuity (da2de902-style) FSR input for test-tenant runs.

Variants:
  1. preferred (weight W): requiredVehicles -> preferredVehicles, preferVisitVehicleMatchPreferredVehiclesWeight=W (default W=2; use --preferred-weights 2 10 20 for campaign)
  2. wait-min:  same input, minimizeWaitingTimeWeight=3
  3. combo:     preferred + weight 2 + minimizeWaitingTimeWeight=3

Writes JSON files to --out-dir for submission with submit_to_timefold.py (test tenant API key).

Usage:
  python prepare_continuity_test_variants.py --input path/to/da2de902-input.json --out-dir path/to/out
  python prepare_continuity_test_variants.py --input patched.json --out-dir out --preferred-weights 2 10 20
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def visit_name_to_person(name: str) -> str:
    """E.g. 'H026_24 - Bad/Dusch' -> 'H026'."""
    if not name or " - " not in name:
        return ""
    client = name.split(" - ")[0].strip()
    return client.rsplit("_", 1)[0] if "_" in client else client


def convert_required_to_preferred(model: dict) -> None:
    """Replace requiredVehicles with preferredVehicles on all visits (mutates in place)."""
    def on_visit(v: dict) -> None:
        if "requiredVehicles" in v and v["requiredVehicles"]:
            v["preferredVehicles"] = v.pop("requiredVehicles")

    for v in model.get("visits") or []:
        on_visit(v)
    for g in model.get("visitGroups") or []:
        for v in g.get("visits") or []:
            on_visit(v)


def set_overrides(payload: dict, **kwargs: int | float) -> None:
    """Set config.model.overrides keys in payload (mutates in place)."""
    config = payload.get("config")
    if config is None:
        config = {}
        payload["config"] = config
    model = config.get("model") or {}
    overrides = model.get("overrides") or {}
    for k, val in kwargs.items():
        overrides[k] = val
    model["overrides"] = overrides
    config["model"] = model


def main() -> int:
    ap = argparse.ArgumentParser(description="Prepare continuity test variant payloads.")
    ap.add_argument("--input", type=Path, required=True, help="Path to da2de902-style input JSON.")
    ap.add_argument("--out-dir", type=Path, required=True, help="Directory to write variant JSONs.")
    ap.add_argument(
        "--preferred-weights",
        type=int,
        nargs="*",
        default=[2],
        metavar="W",
        help="Preferred-vehicles weight(s) to emit (default: 2). E.g. 2 10 20 for campaign matrix.",
    )
    args = ap.parse_args()

    if not args.input.exists():
        print(f"Error: not found {args.input}", file=sys.stderr)
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.input, encoding="utf-8") as f:
        payload = json.load(f)

    config = payload.get("config") or {}
    model_input = payload.get("modelInput") or payload

    # 1) preferred: required -> preferred, one file per weight
    for weight in args.preferred_weights:
        p_preferred = json.loads(json.dumps(payload))
        mi_pref = p_preferred.get("modelInput") or p_preferred
        convert_required_to_preferred(mi_pref)
        set_overrides(p_preferred, preferVisitVehicleMatchPreferredVehiclesWeight=weight)
        out_preferred = args.out_dir / f"input_preferred_vehicles_weight{weight}.json"
        with open(out_preferred, "w", encoding="utf-8") as f:
            json.dump(p_preferred, f, indent=2, ensure_ascii=False)
        print(f"Wrote {out_preferred}")

    # 2) wait-min: same input, wait weight 3
    p_wait = json.loads(json.dumps(payload))
    set_overrides(p_wait, minimizeWaitingTimeWeight=3)
    out_wait = args.out_dir / "input_wait_min_weight3.json"
    with open(out_wait, "w", encoding="utf-8") as f:
        json.dump(p_wait, f, indent=2, ensure_ascii=False)
    print(f"Wrote {out_wait}")

    # 3) combo: preferred + both weights
    p_combo = json.loads(json.dumps(payload))
    mi_combo = p_combo.get("modelInput") or p_combo
    convert_required_to_preferred(mi_combo)
    set_overrides(
        p_combo,
        preferVisitVehicleMatchPreferredVehiclesWeight=2,
        minimizeWaitingTimeWeight=3,
    )
    out_combo = args.out_dir / "input_combo_preferred_and_wait_min.json"
    with open(out_combo, "w", encoding="utf-8") as f:
        json.dump(p_combo, f, indent=2, ensure_ascii=False)
    print(f"Wrote {out_combo}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
