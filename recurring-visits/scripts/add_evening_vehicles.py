#!/usr/bin/env python3
"""
Add extra evening vehicles to an input JSON to increase evening capacity.

Creates new vehicles (Kväll_Extra_1, Kväll_Extra_2, ...) with shifts 16:00-22:00
for each day in the 2-week planning window (2026-02-16 to 2026-03-01). No breaks.
Matches existing Kväll_* vehicle pattern.

Usage:
  python add_evening_vehicles.py solve/tf/input.json --out solve/input_evening.json
  python add_evening_vehicles.py solve/tf/input.json --count 3
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

DEPOT = [59.2368721, 17.9942601]
TZ = "+01:00"
# 2-week planning window: 2026-02-16 to 2026-03-01 (14 days)
EVENING_DAYS = [
    "2026-02-16", "2026-02-17", "2026-02-18", "2026-02-19", "2026-02-20",
    "2026-02-21", "2026-02-22", "2026-02-23", "2026-02-24", "2026-02-25",
    "2026-02-26", "2026-02-27", "2026-02-28", "2026-03-01",
]


def make_shift(day: str, vehicle_idx: int, shift_idx: int) -> dict:
    """Create one evening shift (16:00-22:00, no break) for the given day."""
    sid = hashlib.md5(f"kvall_extra_{vehicle_idx}_{day}_{shift_idx}".encode()).hexdigest()[:8]
    base = f"{day}T"
    return {
        "id": sid,
        "startLocation": DEPOT,
        "minStartTime": f"{base}16:00:00{TZ}",
        "maxEndTime": f"{base}22:00:00{TZ}",
        "tags": [],
        "itinerary": [],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Add extra evening vehicles to input JSON.")
    ap.add_argument("input", type=Path, help="Input JSON with modelInput.")
    ap.add_argument("--out", type=Path, default=None, help="Output path (default: input_evening_<ts>.json).")
    ap.add_argument("--count", type=int, default=3, help="Number of extra evening vehicles (default: 3).")
    ap.add_argument("--no-timestamp", action="store_true", help="Use exact --out path.")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"Error: not found {args.input}", file=sys.stderr)
        return 1

    with open(args.input) as f:
        data = json.load(f)

    mi = data.get("modelInput") or data
    vehicles = list(mi.get("vehicles", []))

    for i in range(1, args.count + 1):
        vid = f"Kväll_Extra_{i}"
        shifts = [
            make_shift(day, i, si)
            for si, day in enumerate(EVENING_DAYS)
        ]
        vehicles.append({
            "id": vid,
            "vehicleType": "VAN",
            "shifts": shifts,
        })

    mi["vehicles"] = vehicles

    out_path = args.out
    if out_path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = args.input.parent / f"input_evening_{ts}.json"
    elif not args.no_timestamp:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = out_path.parent / f"{out_path.stem}_{ts}{out_path.suffix}"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    n_vehicles = len(vehicles)
    n_shifts = sum(len(v.get("shifts", [])) for v in vehicles)
    print(f"Added {args.count} extra evening vehicles ({args.count * len(EVENING_DAYS)} shifts)")
    print(f"Total: {n_vehicles} vehicles, {n_shifts} shifts")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
