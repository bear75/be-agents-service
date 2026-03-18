#!/usr/bin/env python3
"""
Generate 15 overnight campaign variant JSONs: preferred pools only, balanced weights (P, W, T).
P = preferVisitVehicleMatchPreferredVehiclesWeight, W = minimizeWaitingTimeWeight, T = minimizeTravelTimeWeight.
All get config.run.termination = PT3H / PT15M. Run from be-agent-service or v3/continuity; --out-dir defaults to variants/overnight.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


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


def set_overrides_and_termination(
    payload: dict,
    *,
    preferred: int,
    wait: int,
    travel: int,
    spent_limit: str = "PT3H",
    unimproved: str = "PT15M",
) -> None:
    """Set config.model.overrides and config.run.termination (mutates in place)."""
    config = payload.setdefault("config", {})
    run = config.setdefault("run", {})
    run["termination"] = {"spentLimit": spent_limit, "unimprovedSpentLimit": unimproved}
    model = config.setdefault("model", {})
    overrides = model.setdefault("overrides", {})
    overrides["preferVisitVehicleMatchPreferredVehiclesWeight"] = preferred
    overrides["minimizeWaitingTimeWeight"] = wait
    overrides["minimizeTravelTimeWeight"] = travel
    model["overrides"] = overrides
    config["model"] = model


# 15 variants: (strategy_name, base_key, P, W, T). base_key "pool10" | "pool8"
VARIANTS = [
    ("pool10_p5_w3_t3", "pool10", 5, 3, 3),
    ("pool10_p10_w3_t3", "pool10", 10, 3, 3),
    ("pool10_p5_w5_t3", "pool10", 5, 5, 3),
    ("pool10_p5_w3_t5", "pool10", 5, 3, 5),
    ("pool10_p10_w5_t5", "pool10", 10, 5, 5),
    ("pool8_p5_w3_t3", "pool8", 5, 3, 3),
    ("pool8_p10_w3_t3", "pool8", 10, 3, 3),
    ("pool8_p5_w5_t5", "pool8", 5, 5, 5),
    ("pool10_p8_w4_t4", "pool10", 8, 4, 4),
    ("pool10_p15_w2_t5", "pool10", 15, 2, 5),
    ("pool8_p8_w4_t4", "pool8", 8, 4, 4),
    ("pool10_p3_w5_t5", "pool10", 3, 5, 5),
    ("pool10_p20_w2_t2", "pool10", 20, 2, 2),
    ("pool8_p15_w2_t5", "pool8", 15, 2, 5),
    ("pool8_p10_w5_t5", "pool8", 10, 5, 5),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate overnight campaign variant JSONs.")
    ap.add_argument("--pool10-input", type=Path, required=True, help="Path to pool10 input (required vehicles).")
    ap.add_argument("--pool8-input", type=Path, required=True, help="Path to pool8 preferred input.")
    ap.add_argument("--out-dir", type=Path, required=True, help="Output directory for variant JSONs.")
    ap.add_argument("--spent-limit", default="PT3H", help="termination.spentLimit (default PT3H).")
    ap.add_argument("--unimproved", default="PT15M", help="termination.unimprovedSpentLimit (default PT15M).")
    args = ap.parse_args()

    if not args.pool10_input.exists():
        print(f"Error: not found {args.pool10_input}", file=__import__("sys").stderr)
        return 1
    if not args.pool8_input.exists():
        print(f"Error: not found {args.pool8_input}", file=__import__("sys").stderr)
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.pool10_input, encoding="utf-8") as f:
        pool10_payload = json.load(f)
    mi10 = pool10_payload.get("modelInput") or pool10_payload
    convert_required_to_preferred(mi10)

    with open(args.pool8_input, encoding="utf-8") as f:
        pool8_payload = json.load(f)

    for name, base, p, w, t in VARIANTS:
        if base == "pool10":
            payload = json.loads(json.dumps(pool10_payload))
        else:
            payload = json.loads(json.dumps(pool8_payload))
        set_overrides_and_termination(
            payload,
            preferred=p,
            wait=w,
            travel=t,
            spent_limit=args.spent_limit,
            unimproved=args.unimproved,
        )
        out_path = args.out_dir / f"{name}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"Wrote {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
