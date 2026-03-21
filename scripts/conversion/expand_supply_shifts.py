#!/usr/bin/env python3
"""
Expand supply in a Timefold FSR *model input* by duplicating vehicles (more shifts)
and/or extending shift end times for research runs.

Why: analyze_unassigned.py often classifies unassigned visits as "config" (solver) but
underlying capacity can still be tight. Cloning the fleet adds parallel routes with the
same shift pattern; extending end times adds hours per day (e.g. evening coverage).

Input JSON may be:
  - { "modelInput": { ... }, "config": { ... } }  (dashboard export)
  - { "planningWindow", "visits", "vehicles", ... }  (bare modelInput)

Usage:
  python3 scripts/conversion/expand_supply_shifts.py \\
    -i recurring-visits/.../export-*-input.json \\
    -o recurring-visits/.../input_supply_plus1.json \\
    --fleet-duplicates 1

  # Combine: one full fleet clone + extend each shift end by 3h (evening buffer)
  python3 scripts/conversion/expand_supply_shifts.py -i in.json -o out.json \\
    --fleet-duplicates 1 --extend-end-hours 3
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _rewrite_uuids(obj: Any) -> Any:
    """Deep copy with new UUIDs for any 'id' field whose value matches UUID shape."""
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            if k == "id" and isinstance(v, str) and UUID_RE.match(v):
                out[k] = str(uuid.uuid4())
            else:
                out[k] = _rewrite_uuids(v)
        return out
    if isinstance(obj, list):
        return [_rewrite_uuids(x) for x in obj]
    return obj


def _parse_iso_utc(s: str) -> datetime:
    s2 = s.replace("Z", "+00:00")
    dt = datetime.fromisoformat(s2)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _format_iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _extend_shift_end_only(shift: dict[str, Any], hours: float) -> None:
    """Add hours to shift maxEndTime only (longer working block; start unchanged)."""
    delta = timedelta(hours=hours)
    if "maxEndTime" in shift and isinstance(shift["maxEndTime"], str):
        try:
            shift["maxEndTime"] = _format_iso_utc(
                _parse_iso_utc(shift["maxEndTime"]) + delta
            )
        except (ValueError, TypeError):
            pass


def _extend_all_shifts(vehicles: list[dict[str, Any]], hours: float) -> None:
    for v in vehicles:
        for sh in v.get("shifts") or []:
            if isinstance(sh, dict):
                _extend_shift_end_only(sh, hours)


def expand_model_input(
    model_input: dict[str, Any],
    *,
    fleet_duplicates: int,
    extend_end_hours: float,
) -> dict[str, Any]:
    """
    Return a new modelInput dict with expanded vehicles list.
    """
    out = copy.deepcopy(model_input)
    vehicles = out.get("vehicles")
    if not isinstance(vehicles, list):
        raise ValueError("modelInput has no vehicles list")

    extras: list[dict[str, Any]] = []
    for dup_idx in range(1, fleet_duplicates + 1):
        for v in vehicles:
            if not isinstance(v, dict):
                continue
            vid = v.get("id", "vehicle")
            clone = copy.deepcopy(v)
            clone["id"] = f"{vid}__supply_dup{dup_idx}"
            clone = _rewrite_uuids(clone)
            extras.append(clone)

    vehicles.extend(extras)

    if extend_end_hours and extend_end_hours > 0:
        _extend_all_shifts(vehicles, extend_end_hours)

    out["vehicles"] = vehicles
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Expand FSR model input supply (duplicate fleet / extend shifts)"
    )
    ap.add_argument("-i", "--input", type=Path, required=True, help="FSR input JSON")
    ap.add_argument("-o", "--output", type=Path, required=True, help="Output JSON path")
    ap.add_argument(
        "--fleet-duplicates",
        type=int,
        default=0,
        help="Append N full copies of the fleet (new vehicle ids + fresh shift UUIDs). Default 0.",
    )
    ap.add_argument(
        "--extend-end-hours",
        type=float,
        default=0.0,
        help="Add this many hours to every shift end (and shift break times). Default 0.",
    )
    ap.add_argument(
        "--bare-model-input",
        action="store_true",
        help="Write only modelInput object (no config wrapper)",
    )
    args = ap.parse_args()

    if args.fleet_duplicates < 0:
        ap.error("--fleet-duplicates must be >= 0")
    if args.fleet_duplicates == 0 and args.extend_end_hours <= 0:
        ap.error("Set --fleet-duplicates >= 1 and/or --extend-end-hours > 0")

    raw = json.loads(args.input.expanduser().resolve().read_text(encoding="utf-8"))
    config = raw.get("config")
    mi = raw.get("modelInput")
    if mi is None:
        mi = raw
        config = None

    if not isinstance(mi, dict):
        raise SystemExit("Input has no modelInput object")

    expanded = expand_model_input(
        mi,
        fleet_duplicates=args.fleet_duplicates,
        extend_end_hours=args.extend_end_hours,
    )

    if args.bare_model_input:
        out_doc: dict[str, Any] = expanded
    elif config is not None:
        out_doc = {"config": copy.deepcopy(config), "modelInput": expanded}
    else:
        out_doc = expanded

    out_path = args.output.expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(out_doc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    n_veh = len(expanded.get("vehicles") or [])
    print(f"Wrote: {out_path}")
    print(f"  vehicles: {n_veh}")
    if args.fleet_duplicates:
        print(f"  fleet_duplicates: {args.fleet_duplicates} (appended full fleet copies)")
    if args.extend_end_hours > 0:
        print(f"  extend_end_hours: {args.extend_end_hours}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
