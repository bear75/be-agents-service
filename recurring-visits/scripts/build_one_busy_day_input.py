#!/usr/bin/env python3
"""
Build a single-day FSR input from a full-window (e.g. 2-week) da2de902-style input.

Keeps only visits whose timeWindows overlap the target date and only shifts on that date.
Visit groups are preserved but filtered (groups with no visits on the day are dropped).

Vehicle refs: requiredVehicles are always converted to preferredVehicles (intersected with
vehicles on the day), so the one-day solve uses soft continuity and the optimizer can
balance efficiency vs continuity. requiredVehicles would force travel/wait regardless of config.

Usage:
  python build_one_busy_day_input.py --input full-input.json --date 2026-02-16 --output one_day_input.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def date_from_iso(iso: str) -> str:
    """Return YYYY-MM-DD from ISO datetime string."""
    if not iso:
        return ""
    return iso[:10] if len(iso) >= 10 else iso.split("T")[0]


def visit_on_date(visit: dict, target_date: str) -> bool:
    """True if any timeWindow overlaps target_date (by date)."""
    for tw in visit.get("timeWindows") or []:
        start = tw.get("minStartTime") or tw.get("maxEndTime") or ""
        if date_from_iso(start) == target_date:
            return True
        end = tw.get("maxEndTime") or start
        if date_from_iso(end) == target_date:
            return True
    return False


def shift_on_date(shift: dict, target_date: str) -> bool:
    """True if shift is entirely on target_date."""
    start = shift.get("minStartTime") or ""
    end = shift.get("maxEndTime") or ""
    return date_from_iso(start) == target_date and date_from_iso(end) == target_date


def main() -> int:
    ap = argparse.ArgumentParser(description="Build one-busy-day FSR input from full-window input.")
    ap.add_argument("--input", type=Path, required=True, help="Full-window input JSON.")
    ap.add_argument("--date", required=True, help="Target date YYYY-MM-DD (e.g. 2026-02-16).")
    ap.add_argument("--output", type=Path, required=True, help="Output one-day input JSON.")
    args = ap.parse_args()

    target_date = args.date.strip()
    if len(target_date) != 10 or target_date[4] != "-" or target_date[7] != "-":
        print("Error: --date must be YYYY-MM-DD", file=sys.stderr)
        return 1

    if not args.input.exists():
        print(f"Error: not found {args.input}", file=sys.stderr)
        return 1

    with open(args.input, encoding="utf-8") as f:
        payload = json.load(f)

    model = payload.get("modelInput") or payload
    visits = model.get("visits") or []
    visit_groups = model.get("visitGroups") or []
    vehicles = model.get("vehicles") or []

    # Visit IDs on the target day
    day_visit_ids = {v["id"] for v in visits if visit_on_date(v, target_date)}
    for g in visit_groups:
        for v in g.get("visits") or []:
            if visit_on_date(v, target_date):
                day_visit_ids.add(v["id"])

    # Filter standalone visits
    new_visits = [v for v in visits if v["id"] in day_visit_ids]

    # Filter visit groups
    new_groups = []
    for g in visit_groups:
        group_visits = [v for v in (g.get("visits") or []) if v["id"] in day_visit_ids]
        if not group_visits:
            continue
        new_groups.append({**g, "visits": group_visits})

    # Filter vehicles: keep only shifts on target_date
    new_vehicles = []
    for v in vehicles:
        day_shifts = [s for s in (v.get("shifts") or []) if shift_on_date(s, target_date)]
        if not day_shifts:
            continue
        new_vehicles.append({**v, "shifts": day_shifts})

    valid_vehicle_ids = {v["id"] for v in new_vehicles}

    def to_preferred_only(visit: dict) -> dict:
        """Use preferredVehicles only (from required + preferred), so optimizer can balance efficiency vs continuity."""
        out = dict(visit)
        out.pop("requiredVehicles", None)
        preferred = list(out.get("preferredVehicles") or [])
        for vid in visit.get("requiredVehicles") or []:
            if vid not in preferred:
                preferred.append(vid)
        kept = [vid for vid in preferred if vid in valid_vehicle_ids]
        if kept:
            out["preferredVehicles"] = kept
        else:
            out.pop("preferredVehicles", None)
        return out

    new_visits = [to_preferred_only(v) for v in new_visits]
    new_groups = [
        {**g, "visits": [to_preferred_only(v) for v in (g.get("visits") or [])]}
        for g in new_groups
    ]

    new_model = {
        "vehicles": new_vehicles,
        "visits": new_visits,
        "visitGroups": new_groups,
    }
    out_payload = {**payload, "modelInput": new_model}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out_payload, f, indent=2, ensure_ascii=False)

    n_visits = len(new_visits) + sum(len(g.get("visits") or []) for g in new_groups)
    n_shifts = sum(len(v.get("shifts") or []) for v in new_vehicles)
    print(f"One busy day {target_date}: {n_visits} visits, {len(new_vehicles)} vehicles, {n_shifts} shifts")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
