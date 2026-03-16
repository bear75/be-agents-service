#!/usr/bin/env python3
"""
Extract planner recommendations from a sick-day solve output.

Compares new solve output to baseline: identifies reassigned visits (moved to another day)
and unassigned visits (split into sick vs other using --deferred).

Usage:
  python extract_recommendations.py \\
    --output solve/supply-demand-sim/output.json \\
    --baseline solve/tf-16feb-0800/from-patch-output.json \\
    --target-day 2026-02-16 \\
    --deferred solve/supply-demand-sim/deferred_20260216_2sick.json \\
    --out solve/supply-demand-sim/recommendations.json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def parse_date(s: str) -> datetime:
    """Parse YYYY-MM-DD to datetime at midnight."""
    return datetime.strptime(s, "%Y-%m-%d")


def extract_date_from_iso(iso_str: str) -> str | None:
    """Extract YYYY-MM-DD from ISO string."""
    if not iso_str:
        return None
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def visit_assignments(output_data: dict) -> dict[str, dict]:
    """
    From solution output, return visit_id -> {day, vehicle_id, shift_id, start, end, ...}.
    """
    out = output_data.get("modelOutput") or output_data.get("model_output") or {}
    result: dict[str, dict] = {}
    for v in out.get("vehicles", []):
        vid = v.get("id")
        if not vid:
            continue
        for s in v.get("shifts", []):
            sid = s.get("id", "")
            for item in s.get("itinerary", []):
                if not isinstance(item, dict) or item.get("kind") != "VISIT":
                    continue
                visit_id = item.get("id")
                if not visit_id:
                    continue
                start = item.get("startTime") or item.get("minStartTravelTime") or ""
                end = item.get("endTime") or ""
                day = extract_date_from_iso(start) or extract_date_from_iso(end)
                result[visit_id] = {
                    "visit_id": visit_id,
                    "day": day,
                    "vehicle_id": vid,
                    "shift_id": sid,
                    "recommended_start": start,
                    "recommended_end": end,
                }
    return result


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Extract reassigned and unassigned visits from sick-day solve output.",
    )
    ap.add_argument("--output", type=Path, required=True, help="New solve output JSON.")
    ap.add_argument("--baseline", type=Path, required=True, help="Baseline solution (before sick-day solve).")
    ap.add_argument("--target-day", type=str, required=True, help="Target date YYYY-MM-DD.")
    ap.add_argument(
        "--deferred",
        type=Path,
        default=None,
        help="JSON with deferred_visit_ids (sick visits from simulate_low_supply).",
    )
    ap.add_argument("--out", type=Path, required=True, help="Output JSON path.")
    args = ap.parse_args()

    if not args.output.exists():
        print(f"Error: output not found: {args.output}", file=sys.stderr)
        return 1
    if not args.baseline.exists():
        print(f"Error: baseline not found: {args.baseline}", file=sys.stderr)
        return 1

    with open(args.output) as f:
        output_data = json.load(f)
    with open(args.baseline) as f:
        baseline_data = json.load(f)

    deferred_ids: set[str] = set()
    if args.deferred and args.deferred.exists():
        with open(args.deferred) as f:
            d = json.load(f)
        deferred_ids = set(d.get("deferred_visit_ids", []))

    baseline_assignments = visit_assignments(baseline_data)
    new_assignments = visit_assignments(output_data)

    reassigned: list[dict] = []
    unassigned_sick: list[str] = []
    unassigned_other: list[str] = []

    for visit_id, bl in baseline_assignments.items():
        bl_day = bl.get("day")
        if bl_day != args.target_day:
            continue
        if visit_id in new_assignments:
            new_day = new_assignments[visit_id].get("day")
            if new_day and new_day != args.target_day:
                entry = {
                    "visit_id": visit_id,
                    "original_day": args.target_day,
                    "new_day": new_day,
                    "recommended_start": new_assignments[visit_id].get("recommended_start", ""),
                    "recommended_end": new_assignments[visit_id].get("recommended_end", ""),
                    "vehicle_id": new_assignments[visit_id].get("vehicle_id", ""),
                }
                reassigned.append(entry)
        else:
            if visit_id in deferred_ids:
                unassigned_sick.append(visit_id)
            else:
                unassigned_other.append(visit_id)

    summary = {
        "reassigned_count": len(reassigned),
        "unassigned_sick_count": len(unassigned_sick),
        "unassigned_other_count": len(unassigned_other),
        "unassigned_count": len(unassigned_sick) + len(unassigned_other),
    }

    output = {
        "reassigned": reassigned,
        "unassigned_sick": unassigned_sick,
        "unassigned_other": unassigned_other,
        "unassigned": unassigned_sick + unassigned_other,
        "summary": summary,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Reassigned: {summary['reassigned_count']}")
    print(f"Unassigned (sick): {summary['unassigned_sick_count']}")
    print(f"Unassigned (other): {summary['unassigned_other_count']}")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
