#!/usr/bin/env python3
"""
Build a from-patch payload (remove unused vehicles, pin all assigned visits) and
POST it to Timefold FSR from-patch endpoint.

Requires: TIMEFOLD_API_KEY env (or fallback in script).

Usage:
  # From full solution + full input: remove vehicles with 0 visits, pin all visits
  python run_from_patch.py --solution fixed/...-output.json --input hourly/...-input.json

  # From a previous from-patch output (no --input): remove vehicles that have 0 visits
  # in that solution (empty/break-only). Pins all visits from the solution.
  python run_from_patch.py --solution fixed/from-patch-reduced/...-output.json \\
    --route-plan-id 5ff46c3d-f7c3-40bd-9428-5ee24fc5bcd9

  python run_from_patch.py --dry-run   # only write patch JSON, do not POST

  # Experimental: also add remove ops for break-only shifts (may be rejected by API)
  python run_from_patch.py --solution ... --remove-empty-shifts --dry-run

Note: By default we only remove whole vehicles. Use --remove-empty-shifts to also
remove shifts with 0 visits (path /vehicles/[id=X]/shifts/[id=Y]); see
docs/WHY_TRIM_EMPLOYEES_DILEMMA.md. If the API accepts it, you get 0 unassigned and no empty shifts.

Full pipeline (CSV → input → solve → from-patch iterate): see PIPELINE.md.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests

# Reuse logic from build_reduced_input
from build_reduced_input import used_vehicles_and_shifts_from_solution


def empty_shifts_from_solution(solution: dict) -> list[tuple[str, str]]:
    """
    Return (vehicle_id, shift_id) for every shift that has zero VISITs in its itinerary.
    Used to build patch ops that remove break-only shifts (experimental; API may not support).
    """
    out = solution.get("modelOutput") or solution.get("model_output")
    if not out:
        return []
    result: list[tuple[str, str]] = []
    for v in out.get("vehicles", []):
        vid = v.get("id")
        if not vid:
            continue
        for s in v.get("shifts", []):
            sid = s.get("id")
            if not sid:
                continue
            itinerary = s.get("itinerary", [])
            has_visit = any(
                isinstance(item, dict) and item.get("kind") == "VISIT"
                for item in itinerary
            )
            if not has_visit:
                result.append((vid, sid))
    return sorted(result)

TIMEFOLD_BASE = "https://app.timefold.ai/api/models/field-service-routing/v1/route-plans"
API_KEY = os.environ.get("TIMEFOLD_API_KEY", "tf_p_411fa75d-ffeb-40ec-b491-9d925bd1d1f3")
HEADERS = {"Content-Type": "application/json", "X-API-KEY": API_KEY}

ROOT = Path(__file__).resolve().parent
if ROOT.name == "scripts":
    ROOT = ROOT.parent
SOLUTION_PATH = ROOT / "fixed/export-field-service-routing-eb827631-6657-4c4f-948f-0c8aeceacd62-output.json"
INPUT_PATH = ROOT / "hourly/export-field-service-routing-v1-eb827631-6657-4c4f-948f-0c8aeceacd62-input.json"


def visit_min_start_travel_times(solution: dict) -> dict[str, str]:
    """From solution output, return dict visit_id -> minStartTravelTime (ISO string)."""
    out = solution.get("modelOutput") or solution.get("model_output")
    result: dict[str, str] = {}
    if not out:
        return result
    for v in out.get("vehicles", []):
        for s in v.get("shifts", []):
            for item in s.get("itinerary", []):
                if isinstance(item, dict) and item.get("kind") == "VISIT":
                    vid = item.get("id")
                    mst = item.get("minStartTravelTime")
                    if vid and mst:
                        result[vid] = mst
    return result


def build_patch(
    solution: dict,
    full_input: dict | None = None,
    remove_empty_shifts: bool = False,
) -> list[dict]:
    """
    Build JSON Patch array: remove unused/empty vehicles, optionally remove break-only
    shifts, add pinningRequested and minStartTravelTime for every visit in the solution.
    Paths are relative to modelInput (Timefold from-patch convention).

    If full_input is None, "unused" = vehicles with 0 visits in the solution.
    If remove_empty_shifts is True, add remove ops for each shift that has 0 visits
    (path /vehicles/[id=X]/shifts/[id=Y]). Whether the API supports this is unknown;
    see docs/WHY_TRIM_EMPLOYEES_DILEMMA.md.
    """
    used_v, _ = used_vehicles_and_shifts_from_solution(solution)
    out = solution.get("modelOutput") or solution.get("model_output") or {}
    if full_input is not None:
        mi = full_input.get("modelInput") or full_input
        all_vehicle_ids = [v["id"] for v in mi.get("vehicles", []) if v.get("id")]
    else:
        all_vehicle_ids = [v["id"] for v in out.get("vehicles", []) if v.get("id")]
    unused_vehicle_ids = [vid for vid in all_vehicle_ids if vid not in used_v]
    visit_mst = visit_min_start_travel_times(solution)

    patch: list[dict] = []

    # Remove unused/empty vehicles (no pinned visits)
    for vid in sorted(unused_vehicle_ids):
        patch.append({"op": "remove", "path": f"/vehicles/[id={vid}]"})

    # Optionally remove shifts that have 0 visits (break-only). API support TBD.
    if remove_empty_shifts:
        for vid, sid in empty_shifts_from_solution(solution):
            patch.append({"op": "remove", "path": f"/vehicles/[id={vid}]/shifts/[id={sid}]"})

    # Pin all assigned visits: add pinningRequested and minStartTravelTime
    for visit_id, mst in sorted(visit_mst.items()):
        patch.append({"op": "add", "path": f"/visits/[id={visit_id}]/pinningRequested", "value": True})
        patch.append({"op": "add", "path": f"/visits/[id={visit_id}]/minStartTravelTime", "value": mst})

    return patch


def main() -> int:
    ap = argparse.ArgumentParser(description="Build from-patch payload and POST to Timefold FSR.")
    ap.add_argument("--dry-run", action="store_true", help="Only write patch JSON, do not POST.")
    ap.add_argument("--solution", type=Path, default=SOLUTION_PATH, help="Solution output JSON.")
    ap.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Full input JSON. If omitted, empty vehicles are those with 0 visits in --solution (for chained from-patch).",
    )
    ap.add_argument("--route-plan-id", type=str, default="eb827631-6657-4c4f-948f-0c8aeceacd62", help="Route plan ID to patch.")
    ap.add_argument(
        "--remove-empty-shifts",
        action="store_true",
        help="Add patch ops to remove shifts with 0 visits (path /vehicles/[id=X]/shifts/[id=Y]). Experimental; API may reject.",
    )
    args = ap.parse_args()

    if not args.solution.exists():
        print(f"Error: solution not found: {args.solution}", file=sys.stderr)
        return 1
    full_input = None
    if args.input is not None:
        if not args.input.exists():
            print(f"Error: input not found: {args.input}", file=sys.stderr)
            return 1
        with open(args.input) as f:
            full_input = json.load(f)

    with open(args.solution) as f:
        solution = json.load(f)

    patch = build_patch(solution, full_input, remove_empty_shifts=args.remove_empty_shifts)
    used_v, _ = used_vehicles_and_shifts_from_solution(solution)
    out = solution.get("modelOutput") or solution.get("model_output") or {}
    all_v = [v["id"] for v in out.get("vehicles", []) if v.get("id")]
    if full_input is not None:
        all_v = [v["id"] for v in (full_input.get("modelInput") or full_input).get("vehicles", []) if v.get("id")]
    unused_count = len(all_v) - len(used_v)
    empty_shift_count = len(empty_shifts_from_solution(solution)) if args.remove_empty_shifts else 0

    payload = {
        "config": {
            "run": {"name": "from-patch-reduce-unused-employees"},
        },
        "patch": patch,
    }

    out_path = DIR / "from_patch_payload.json"
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    msg = f"Patch: {len(patch)} ops (remove {unused_count} vehicles"
    if empty_shift_count:
        msg += f", remove {empty_shift_count} empty shifts"
    msg += f", pin {len(visit_min_start_travel_times(solution))} visits). Wrote {out_path}"
    print(msg)

    if args.dry_run:
        return 0

    url = f"{TIMEFOLD_BASE}/{args.route_plan_id}/from-patch"
    params = {"select": "SOLVED", "operation": "SOLVE"}
    try:
        r = requests.post(url, headers=HEADERS, params=params, json=payload, timeout=60)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    if r.status_code == 202:
        body = r.json()
        new_id = body.get("id") or body.get("parentId") or body.get("originId")
        print(f"Accepted. New route plan id: {new_id}")
        print(f"GET solution: {TIMEFOLD_BASE}/{new_id}")
        return 0
    print(f"Error: {r.status_code} {r.text[:800]}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
