#!/usr/bin/env python3
"""
Submit a modelInput JSON to Timefold FSR API (create new route plan and solve).
Wraps modelInput with config (run, model, maps) from a reference input if needed.
Validates that no vehicle shift has zero work time (minStartTime < maxEndTime).
With --wait, polls until solve completes and exits non-zero if solving failed.

Usage:
  python submit_to_timefold.py fixed/from-patch-reduced/input-only-used-shifts.json
  python submit_to_timefold.py input.json --dry-run
  python submit_to_timefold.py input.json --wait
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

TIMEFOLD_BASE = "https://app.timefold.ai/api/models/field-service-routing/v1/route-plans"
API_KEY = os.environ.get("TIMEFOLD_API_KEY", "tf_p_411fa75d-ffeb-40ec-b491-9d925bd1d1f3")
HEADERS = {"Content-Type": "application/json", "X-API-KEY": API_KEY}
# Terminal solver statuses (no more progress)
SOLVER_TERMINAL = {"SOLVING_COMPLETED", "SOLVING_FAILED", "SOLVING_INCOMPLETE"}
POLL_INTERVAL_SEC = 5
POLL_TIMEOUT_SEC = 3600

ROOT = Path(__file__).resolve().parent
if ROOT.name == "scripts":
    ROOT = ROOT.parent
# Reference: full request shape (config + modelInput) - may not exist if running fresh
REFERENCE_INPUT = ROOT / "hourly/export-field-service-routing-v1-eb827631-6657-4c4f-948f-0c8aeceacd62-input.json"


def validate_shifts(model_input: dict) -> list[tuple[str, str]]:
    """
    Return list of (vehicle_id, shift_id) for shifts with zero or negative work time.
    Timefold requires each shift to have positive work time (minStartTime < maxEndTime).
    """
    bad = []
    for vehicle in model_input.get("vehicles", []):
        vid = vehicle.get("id", "?")
        for shift in vehicle.get("shifts", []):
            sid = shift.get("id", "?")
            start = shift.get("minStartTime") or shift.get("startTime") or shift.get("start")
            end = shift.get("maxEndTime") or shift.get("endTime") or shift.get("end")
            if not start or not end:
                bad.append((vid, sid))
                continue
            if start >= end:
                bad.append((vid, sid))
    return bad


def build_request(model_input_path: Path, reference_path: Path | None) -> dict:
    """Build full request: config from reference + modelInput from model_input_path."""
    with open(model_input_path) as f:
        data = json.load(f)
    model_input = data.get("modelInput") or data

    if reference_path and reference_path.exists():
        with open(reference_path) as f:
            ref = json.load(f)
        config = ref.get("config", {})
        # Override run name so we can identify this submission
        if "run" not in config:
            config["run"] = {}
        config["run"]["name"] = f"only-used-shifts-{model_input_path.stem}"
        if "tags" not in config.get("run", {}):
            config["run"]["tags"] = ["system.profile:caire", "system.type:from-request"]
        return {"config": config, "modelInput": model_input}
    return {"modelInput": model_input}


def main() -> int:
    ap = argparse.ArgumentParser(description="Submit modelInput to Timefold FSR (create route plan).")
    ap.add_argument("input", type=Path, help="JSON file with modelInput (visits + vehicles).")
    ap.add_argument("--reference", type=Path, default=REFERENCE_INPUT, help="Reference request for config (default: hourly input).")
    ap.add_argument("--dry-run", action="store_true", help="Only print request summary, do not POST.")
    ap.add_argument("--wait", action="store_true", help="Poll until solve completes; exit 1 if solving failed.")
    ap.add_argument("--skip-validate", action="store_true", help="Skip pre-submit validation (zero-work shifts).")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"Error: not found {args.input}", file=sys.stderr)
        return 1

    payload = build_request(args.input, args.reference)
    mi = payload["modelInput"]
    n_visits = len(mi.get("visits", []))
    n_vehicles = len(mi.get("vehicles", []))
    n_shifts = sum(len(v.get("shifts", [])) for v in mi.get("vehicles", []))

    if not args.skip_validate:
        bad_shifts = validate_shifts(mi)
        if bad_shifts:
            print("Error: Timefold requires every shift to have positive work time (minStartTime < maxEndTime).", file=sys.stderr)
            print("Shifts with zero or missing work time:", file=sys.stderr)
            for vid, sid in bad_shifts[:50]:
                print(f"  vehicle={vid} shift={sid}", file=sys.stderr)
            if len(bad_shifts) > 50:
                print(f"  ... and {len(bad_shifts) - 50} more.", file=sys.stderr)
            print("Fix or remove these shifts in the input, or run with --skip-validate to submit anyway.", file=sys.stderr)
            return 1

    print(f"Request: {n_visits} visits, {n_vehicles} vehicles, {n_shifts} shifts")

    if args.dry_run:
        print("Dry-run: not sending to Timefold.")
        return 0

    try:
        r = requests.post(TIMEFOLD_BASE, headers=HEADERS, json=payload, timeout=30)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if r.status_code not in (200, 201, 202):
        print(f"Error: {r.status_code} {r.text[:800]}", file=sys.stderr)
        return 1

    body = r.json()
    plan_id = body.get("id") or body.get("parentId") or body.get("originId") or "?"
    print(f"Submitted. Route plan id: {plan_id}")
    print(f"GET solution: {TIMEFOLD_BASE}/{plan_id}")

    if not args.wait:
        return 0

    # Poll until terminal status; exit 0 only if SOLVING_COMPLETED
    url = f"{TIMEFOLD_BASE}/{plan_id}"
    deadline = time.monotonic() + POLL_TIMEOUT_SEC
    while time.monotonic() < deadline:
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
        except Exception as e:
            print(f"Error polling: {e}", file=sys.stderr)
            return 1
        if r.status_code != 200:
            print(f"Error: GET {r.status_code} {r.text[:500]}", file=sys.stderr)
            return 1
        data = r.json()
        status = (data.get("solverStatus") or data.get("status") or "").upper()
        if status in SOLVER_TERMINAL:
            if status == "SOLVING_COMPLETED":
                print("Solve completed successfully.")
                return 0
            print(f"Solve ended with status: {status}", file=sys.stderr)
            if data.get("message"):
                print(f"Message: {data.get('message')}", file=sys.stderr)
            return 1
        print(f"  Status: {status or 'unknown'} ... waiting")
        time.sleep(POLL_INTERVAL_SEC)

    print("Timeout waiting for solve to complete.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
