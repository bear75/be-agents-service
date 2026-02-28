#!/usr/bin/env python3
"""
Minimal test: 1 visit, 1 shift, 1 break (with location).
Submits minimal_breakloc_test.json to Timefold and checks whether the BREAK
itinerary item includes travelTimeFromPreviousStandstill (travel TO break).

Result (verified 2026-02-19): Timefold FSR does NOT return travel on BreakPlan
for FLOATING breaks with location — only id, startTime, endTime, kind.
Their docs show FIXED breaks with location having travel on the break.
So break travel metrics (to/from break) are currently only available when
using FIXED breaks with location, or by inferring from the next visit's
travel (which is "from previous standstill" = from break when break has location).

Run from huddinge-package/scripts:
  python3 test_break_travel.py
"""
import json
import os
import subprocess
import sys
from pathlib import Path

# Resolve paths: script may be run from repo root or from scripts/
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent  # appcaire repo
SOLVE_DIR = SCRIPT_DIR.parent / "solve"
MINIMAL_BREAKLOC = SOLVE_DIR / "minimal_breakloc_test.json"
OUTPUT_PATH = SOLVE_DIR / "minimal_breakloc_output.json"


def main() -> int:
    if not MINIMAL_BREAKLOC.exists():
        print(f"Error: {MINIMAL_BREAKLOC} not found.", file=sys.stderr)
        return 1

    # Run submit_to_timefold.py solve ... --wait --save ...
    cmd = [
        sys.executable,
        str(SCRIPT_DIR / "submit_to_timefold.py"),
        "solve",
        str(MINIMAL_BREAKLOC),
        "--wait",
        "--save",
        str(OUTPUT_PATH),
        "--no-timestamp",
    ]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(SCRIPT_DIR))
    if result.returncode != 0:
        print("Submit/poll failed.", file=sys.stderr)
        return result.returncode

    if not OUTPUT_PATH.exists():
        print(f"Error: output not saved at {OUTPUT_PATH}", file=sys.stderr)
        return 1

    with open(OUTPUT_PATH) as f:
        data = json.load(f)

    # Navigate to itinerary: modelOutput.vehicles[0].shifts[0].itinerary
    model_output = data.get("modelOutput") or data
    vehicles = model_output.get("vehicles") or []
    if not vehicles:
        print("Error: no vehicles in output.", file=sys.stderr)
        return 1
    shifts = vehicles[0].get("shifts") or []
    if not shifts:
        print("Error: no shifts in output.", file=sys.stderr)
        return 1
    itinerary = shifts[0].get("itinerary") or []

    break_items = [i for i in itinerary if i.get("kind") == "BREAK"]
    if not break_items:
        print("Error: no BREAK item in itinerary.", file=sys.stderr)
        return 1

    break_plan = break_items[0]
    travel_time = break_plan.get("travelTimeFromPreviousStandstill")
    travel_dist = break_plan.get("travelDistanceMetersFromPreviousStandstill")

    if travel_time is None and travel_dist is None:
        print("RESULT: BREAK item has no travel fields (current Timefold API behaviour for FLOATING+location).")
        print("Break item keys:", list(break_plan.keys()))
        print("See script docstring: only FIXED breaks with location get travel on BreakPlan in the docs.")
        return 0  # Documented behaviour; test passes so we can re-run to verify API changes later

    print("OK: Break has travel fields (Timefold now returns break travel for this case):")
    print(f"  travelTimeFromPreviousStandstill: {travel_time}")
    print(f"  travelDistanceMetersFromPreviousStandstill: {travel_dist}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
