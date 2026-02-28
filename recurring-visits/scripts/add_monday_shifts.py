#!/usr/bin/env python3
"""
Add extra Monday-only vehicles to an input JSON to increase Monday capacity.

Creates new vehicles (Extra_Monday_1, Extra_Monday_2, ...) with shifts only on
2026-02-16 and 2026-02-23 (the two Mondays in the planning window).

Usage:
  python add_monday_shifts.py ../solve/input_20260213_180452.json --out ../solve/input_shifts_update.json
  python add_monday_shifts.py ../solve/input_20260213_180452.json --count 5
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

DEPOT = [59.2368721, 17.9942601]
MONDAYS = ["2026-02-16", "2026-02-23"]


def make_shift(day: str, shift_idx: int) -> dict:
    """Create a shift for given Monday (YYYY-MM-DD)."""
    base = f"{day}T"
    sid = hashlib.md5(f"extra_mon_{day}_{shift_idx}".encode()).hexdigest()[:8]
    return {
        "id": sid,
        "startLocation": DEPOT,
        "minStartTime": f"{base}07:00:00+01:00",
        "maxEndTime": f"{base}15:00:00+01:00",
        "tags": [],
        "itinerary": [],
        "requiredBreaks": [
            {
                "id": f"{sid}_break",
                "minStartTime": f"{base}10:00:00+01:00",
                "maxEndTime": f"{base}14:00:00+01:00",
                "duration": "PT30M",
                "costImpact": "PAID",
                "type": "FLOATING",
                "location": DEPOT,
            }
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Add extra Monday vehicles to input JSON.")
    ap.add_argument("input", type=Path, help="Input JSON with modelInput.")
    ap.add_argument("--out", type=Path, default=None, help="Output path (default: input_shifts_update_<ts>.json).")
    ap.add_argument("--count", type=int, default=5, help="Number of extra Monday vehicles (default: 5).")
    ap.add_argument("--no-timestamp", action="store_true", help="Use exact --out path.")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"Error: not found {args.input}", file=sys.stderr)
        return 1

    with open(args.input) as f:
        data = json.load(f)

    mi = data.get("modelInput") or data
    vehicles = mi.get("vehicles", [])

    for i in range(1, args.count + 1):
        vid = f"Extra_Monday_{i}"
        shifts = [make_shift(day, i) for day in MONDAYS]
        vehicles.append({
            "id": vid,
            "vehicleType": "VAN",
            "shifts": shifts,
            "historicalTimeUtilized": "PT0S",
            "historicalTimeCapacity": "PT0S",
        })

    mi["vehicles"] = vehicles

    out_path = args.out
    if out_path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = args.input.parent / f"input_shifts_update_{ts}.json"
    elif not args.no_timestamp:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = out_path.parent / f"{out_path.stem}_{ts}{out_path.suffix}"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    n_vehicles = len(vehicles)
    n_shifts = sum(len(v.get("shifts", [])) for v in vehicles)
    print(f"Added {args.count} extra Monday vehicles ({args.count * len(MONDAYS)} shifts)")
    print(f"Total: {n_vehicles} vehicles, {n_shifts} shifts")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
