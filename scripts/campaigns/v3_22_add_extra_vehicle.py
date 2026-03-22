#!/usr/bin/env python3
"""
Add exploratory evening capacity for Huddinge v3/22 campaign.

Baseline analyze_unassigned showed 0 pure supply gaps (all unassigned classified as
config/tuning). This script still adds a synthetic evening vehicle with shifts on
high-unassigned days to test whether extra parallel capacity helps the solver assign
stubborn visits (evening overlap / continuity pools).

Copies shift shape from Kväll_01_Central (15:00–21:00 UTC, Huddinge central coords).

Usage:
  python3 v3_22_add_extra_vehicle.py --input pool8.json --output pool8_extra.json
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
import uuid
from pathlib import Path

# Days with high unassigned slot counts (from analyze_unassigned summary)
_EXTRA_DAYS_UTC = (
    "2026-03-17T15:00:00.000Z",
    "2026-03-24T15:00:00.000Z",
    "2026-03-26T15:00:00.000Z",
)


def _new_id() -> str:
    return str(uuid.uuid4())


def _evening_shift_for_day(min_start: str) -> dict:
    """Build one evening shift (6h window) matching v3/22 Kväll pattern."""
    day = min_start[:10]
    end = f"{day}T21:00:00.000Z"
    return {
        "id": _new_id(),
        "startLocation": [59.2368721, 17.9942601],
        "minStartTime": min_start,
        "maxEndTime": end,
        "skills": [],
        "tags": [],
        "temporarySkillSets": [],
        "temporaryTagSets": [],
        "itinerary": [],
        "cost": {"fixedCost": 1840, "rates": []},
    }


def add_extra_evening_vehicle(payload: dict) -> dict:
    """Return a deep copy of payload with one extra vehicle appended."""
    data = copy.deepcopy(payload)
    mi = data.get("modelInput") or data
    vehicles = mi.setdefault("vehicles", [])
    shifts = [_evening_shift_for_day(d) for d in _EXTRA_DAYS_UTC]
    extra = {
        "id": "v3_22_extra_evening_1",
        "vehicleType": "VAN",
        "shifts": shifts,
    }
    vehicles.append(extra)
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description="Add synthetic evening vehicle for v3/22 campaign")
    ap.add_argument("--input", type=Path, required=True, help="FSR input JSON (e.g. pool8 preferred)")
    ap.add_argument("--output", type=Path, required=True, help="Output JSON path")
    args = ap.parse_args()
    if not args.input.exists():
        print(f"Error: not found {args.input}", file=sys.stderr)
        return 1
    with open(args.input, encoding="utf-8") as f:
        payload = json.load(f)
    out = add_extra_evening_vehicle(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    mi = out.get("modelInput") or out
    n = sum(len(v.get("shifts", [])) for v in mi.get("vehicles", []))
    print(f"Wrote {args.output} ({len(mi.get('vehicles', []))} vehicles, {n} shifts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
