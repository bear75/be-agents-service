#!/usr/bin/env python3
"""
Submit a Timefold FSR request: either a fresh solve (modelInput) or a from-patch.

Modes:
  1. Fresh solve: POST modelInput to create a new route plan
  2. From-patch:  POST patch payload to an existing route plan

With --wait, polls until solve completes and saves the output JSON.

Usage:
  # Fresh solve
  python3 submit_to_timefold.py solve ../tf/step2-input-trimmed.json --wait --save ../tf/step2-output.json

  # From-patch
  python3 submit_to_timefold.py from-patch ../tf/step2-from-patch-payload.json \
    --route-plan-id eb1af587-f316-42b2-94e0-a099b2f8e833 \
    --wait --save ../tf/step2-output.json
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import functools

import requests

# Ensure all prints flush immediately (important for background execution)
print = functools.partial(print, flush=True)

TIMEFOLD_BASE = "https://app.timefold.ai/api/models/field-service-routing/v1/route-plans"
API_KEY = os.environ.get("TIMEFOLD_API_KEY", "tf_p_411fa75d-ffeb-40ec-b491-9d925bd1d1f3")
HEADERS = {"Content-Type": "application/json", "X-API-KEY": API_KEY}
SOLVER_TERMINAL = {"SOLVING_COMPLETED", "SOLVING_FAILED", "SOLVING_INCOMPLETE"}
POLL_INTERVAL_SEC = 10
POLL_TIMEOUT_SEC = 7200  # 2 hours


def validate_shifts(model_input: dict) -> list[tuple[str, str]]:
    """Return (vehicle_id, shift_id) for shifts with zero or negative work time."""
    bad = []
    for vehicle in model_input.get("vehicles", []):
        vid = vehicle.get("id", "?")
        for shift in vehicle.get("shifts", []):
            sid = shift.get("id", "?")
            start = shift.get("minStartTime", "")
            end = shift.get("maxEndTime", "")
            if not start or not end or start >= end:
                bad.append((vid, sid))
    return bad


def submit_solve(payload: dict, configuration_id: str | None = None) -> dict:
    """POST a fresh solve request. Returns response JSON."""
    params = {}
    if configuration_id:
        params["configurationId"] = configuration_id
    r = requests.post(
        TIMEFOLD_BASE, headers=HEADERS, json=payload, params=params or None, timeout=300
    )
    if r.status_code not in (200, 201, 202):
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:800]}")
    return r.json()


def submit_from_patch(
    payload: dict, route_plan_id: str, configuration_id: str | None = None
) -> dict:
    """POST a from-patch request. Returns response JSON."""
    url = f"{TIMEFOLD_BASE}/{route_plan_id}/from-patch"
    params = {"select": "SOLVED", "operation": "SOLVE"}
    if configuration_id:
        params["configurationId"] = configuration_id
    r = requests.post(url, headers=HEADERS, params=params, json=payload, timeout=60)
    if r.status_code not in (200, 201, 202):
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:800]}")
    return r.json()


def poll_until_done(plan_id: str) -> dict:
    """Poll route plan until terminal status. Returns final response."""
    url = f"{TIMEFOLD_BASE}/{plan_id}"
    deadline = time.monotonic() + POLL_TIMEOUT_SEC
    last_status = ""
    while time.monotonic() < deadline:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            raise RuntimeError(f"Poll error: HTTP {r.status_code}: {r.text[:500]}")
        data = r.json()
        meta = data.get("metadata") or data.get("run") or {}
        status = meta.get("solverStatus", "").upper() or data.get("solverStatus", "").upper()
        if status != last_status:
            score = meta.get("score", "")
            print(f"  [{time.strftime('%H:%M:%S')}] Status: {status}  Score: {score}")
            last_status = status
        if status in SOLVER_TERMINAL:
            return data
        time.sleep(POLL_INTERVAL_SEC)
    raise RuntimeError("Timeout waiting for solve to complete.")


def main() -> int:
    ap = argparse.ArgumentParser(description="Submit to Timefold FSR API.")
    sub = ap.add_subparsers(dest="mode", required=True)

    # Solve mode
    solve_p = sub.add_parser("solve", help="Submit fresh solve (modelInput).")
    solve_p.add_argument("input", type=Path, help="Input JSON with modelInput.")
    solve_p.add_argument(
        "--configuration-id",
        default=os.environ.get("TIMEFOLD_CONFIGURATION_ID", "6a4e6b5f-8767-48f8-9365-7091f7e74a37"),
        help="Timefold configuration profile ID (or set TIMEFOLD_CONFIGURATION_ID). Default: 6a4e6b5f-8767-48f8-9365-7091f7e74a37",
    )
    solve_p.add_argument("--skip-validate", action="store_true")

    # From-patch mode
    patch_p = sub.add_parser("from-patch", help="Submit from-patch to existing route plan.")
    patch_p.add_argument("payload", type=Path, help="From-patch payload JSON.")
    patch_p.add_argument("--route-plan-id", required=True, help="Route plan ID to patch.")
    patch_p.add_argument(
        "--configuration-id",
        default=os.environ.get("TIMEFOLD_CONFIGURATION_ID", "6a4e6b5f-8767-48f8-9365-7091f7e74a37"),
        help="Timefold configuration profile ID (or set TIMEFOLD_CONFIGURATION_ID).",
    )

    # Common args
    for p in [solve_p, patch_p]:
        p.add_argument("--wait", action="store_true", help="Poll until solve completes.")
        p.add_argument("--save", type=Path, default=None, help="Save output JSON to file (timestamp inserted: output_YYYYMMDD_HHMMSS.json).")
        p.add_argument("--no-timestamp", action="store_true", help="Use exact --save path (no timestamp).")
    patch_p.add_argument("--save-id", type=Path, default=None, help="Write new route plan ID to this file (from-patch only).")

    args = ap.parse_args()

    if args.mode == "solve":
        if not args.input.exists():
            print(f"Error: not found {args.input}", file=sys.stderr)
            return 1
        with open(args.input) as f:
            payload = json.load(f)
        mi = payload.get("modelInput") or payload
        n_visits = len(mi.get("visits", []))
        n_vehicles = len(mi.get("vehicles", []))
        n_shifts = sum(len(v.get("shifts", [])) for v in mi.get("vehicles", []))
        print(f"Solve: {n_visits} visits, {n_vehicles} vehicles, {n_shifts} shifts")

        if not args.skip_validate:
            bad = validate_shifts(mi)
            if bad:
                print(f"Error: {len(bad)} shifts with zero/negative work time.", file=sys.stderr)
                for vid, sid in bad[:10]:
                    print(f"  vehicle={vid} shift={sid}", file=sys.stderr)
                return 1

        if getattr(args, "configuration_id", None):
            print(f"Using configuration profile: {args.configuration_id}")
        try:
            resp = submit_solve(payload, getattr(args, "configuration_id", None))
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        plan_id = resp.get("id") or resp.get("parentId") or resp.get("originId") or "?"
        print(f"Submitted. Route plan ID: {plan_id}")

    elif args.mode == "from-patch":
        if not args.payload.exists():
            print(f"Error: not found {args.payload}", file=sys.stderr)
            return 1
        with open(args.payload) as f:
            payload = json.load(f)
        n_ops = len(payload.get("patch", []))
        print(f"From-patch: {n_ops} operations -> route plan {args.route_plan_id}")

        if getattr(args, "configuration_id", None):
            print(f"Using configuration profile: {args.configuration_id}")
        try:
            resp = submit_from_patch(
                payload, args.route_plan_id, getattr(args, "configuration_id", None)
            )
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        plan_id = resp.get("id") or resp.get("parentId") or resp.get("originId") or "?"
        print(f"Submitted. New route plan ID: {plan_id}")
        if getattr(args, "save_id", None):
            args.save_id.parent.mkdir(parents=True, exist_ok=True)
            args.save_id.write_text(plan_id.strip() + "\n")
            print(f"Saved route plan ID to {args.save_id}")

    else:
        ap.print_help()
        return 1

    if args.wait:
        print(f"\nPolling for completion (route plan: {plan_id})...")
        try:
            result = poll_until_done(plan_id)
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        meta = result.get("metadata") or result.get("run") or {}
        status = meta.get("solverStatus", "?")
        score = meta.get("score", "?")
        print(f"\nDone. Status: {status}, Score: {score}")

        if args.save:
            args.save.parent.mkdir(parents=True, exist_ok=True)
            if getattr(args, "no_timestamp", False):
                save_path = args.save
            else:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = args.save.parent / f"{args.save.stem}_{ts}{args.save.suffix}"
            with open(save_path, "w") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Output saved to {save_path}")

        if "COMPLETED" not in status.upper():
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
