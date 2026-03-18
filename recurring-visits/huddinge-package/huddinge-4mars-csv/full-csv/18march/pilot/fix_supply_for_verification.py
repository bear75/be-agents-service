#!/usr/bin/env python3
"""
Fix supply-demand imbalance for VERIFICATION purposes.

Goal: 0 unassigned visits so Attendo can verify all visit time windows in the client tab.

Strategy (minimal changes):
1. Extend ALL existing shifts to full-day (05:30-22:00)
2. Add extra full-day vehicles for peak demand days (Mondays)
3. Widen very tight time windows (<=15min) slightly to help solver feasibility
"""

import json
import uuid
from collections import Counter
from datetime import datetime

INPUT_FILE = "export-field-service-routing-v1-89e20faa-574b-4d48-b4ad-65fad2ee2bde-input.json"
OUTPUT_FILE = "input_verification_full_supply.json"

OFFICE_LAT = 59.2368721
OFFICE_LON = 17.9942601

FULL_DAY_START = "05:30:00"
FULL_DAY_END = "22:30:00"


def get_day(ts: str) -> str:
    return ts[:10]


def parse_duration_minutes(dur: str) -> int:
    if not dur:
        return 0
    mins = 0
    rest = dur.replace("PT", "")
    if "H" in rest:
        h_part, rest = rest.split("H")
        mins += int(h_part) * 60
    if "M" in rest:
        m_str = rest.replace("M", "").split(".")[0]
        if m_str:
            mins += int(m_str)
    return mins


def extend_shifts_to_full_day(data: dict) -> int:
    """Extend every shift to cover 05:30-22:30."""
    extended = 0
    for vehicle in data["modelInput"]["vehicles"]:
        for shift in vehicle.get("shifts", []):
            day = get_day(shift["minStartTime"])
            new_start = f"{day}T{FULL_DAY_START}Z"
            new_end = f"{day}T{FULL_DAY_END}Z"

            if shift["minStartTime"] != new_start or shift["maxEndTime"] != new_end:
                shift["minStartTime"] = new_start
                shift["maxEndTime"] = new_end

                # Adjust break window to fit new shift
                for brk in shift.get("requiredBreaks", []):
                    brk["minStartTime"] = f"{day}T09:00:00Z"
                    brk["maxEndTime"] = f"{day}T20:00:00Z"

                extended += 1
    return extended


def count_visits_per_day(data: dict) -> Counter:
    """Count visits per day from timeWindows."""
    counts = Counter()
    for v in data["modelInput"].get("visits", []):
        tws = v.get("timeWindows", [])
        if tws:
            ms = tws[0].get("minStartTime", "")
            if ms:
                counts[get_day(ms)] += 1
    for vg in data["modelInput"].get("visitGroups", []):
        for v in vg.get("visits", []):
            tws = v.get("timeWindows", [])
            if tws:
                ms = tws[0].get("minStartTime", "")
                if ms:
                    counts[get_day(ms)] += 1
    return counts


def count_shifts_per_day(data: dict) -> Counter:
    counts = Counter()
    for vehicle in data["modelInput"]["vehicles"]:
        for shift in vehicle.get("shifts", []):
            counts[get_day(shift["minStartTime"])] += 1
    return counts


def create_full_day_vehicle(vehicle_id: str, days: list) -> dict:
    """Create a vehicle with full-day shifts on specified days."""
    shifts = []
    for day in days:
        shift_id = str(uuid.uuid4())
        break_id = str(uuid.uuid4())
        shifts.append({
            "id": shift_id,
            "startLocation": [OFFICE_LAT, OFFICE_LON],
            "minStartTime": f"{day}T{FULL_DAY_START}Z",
            "maxEndTime": f"{day}T{FULL_DAY_END}Z",
            "skills": [],
            "tags": [],
            "requiredBreaks": [
                {
                    "id": break_id,
                    "minStartTime": f"{day}T09:00:00Z",
                    "maxEndTime": f"{day}T20:00:00Z",
                    "duration": "PT30M",
                    "costImpact": "PAID",
                    "type": "FLOATING",
                    "location": [OFFICE_LAT, OFFICE_LON],
                }
            ],
            "temporarySkillSets": [],
            "temporaryTagSets": [],
            "cost": {"fixedCost": 1840},
            "itinerary": [],
        })
    return {
        "id": vehicle_id,
        "vehicleType": "VAN",
        "shifts": shifts,
    }


def widen_tight_time_windows(data: dict, min_width_minutes: int = 30) -> int:
    """Widen time windows narrower than min_width_minutes."""
    widened = 0

    def widen_visit(v: dict):
        nonlocal widened
        for tw in v.get("timeWindows", []):
            ms = tw.get("minStartTime", "")
            me = tw.get("maxStartTime", tw.get("maxEndTime", ""))
            if ms and me:
                start = datetime.fromisoformat(ms.replace("Z", "+00:00"))
                end = datetime.fromisoformat(me.replace("Z", "+00:00"))
                width = (end - start).total_seconds() / 60
                if width < min_width_minutes:
                    # Extend maxStartTime by (min_width - current_width) / 2 on each side
                    extend = int((min_width_minutes - width) / 2) + 1
                    from datetime import timedelta
                    new_start = start - timedelta(minutes=extend)
                    new_max_start = end + timedelta(minutes=extend)
                    tw["minStartTime"] = new_start.strftime("%Y-%m-%dT%H:%M:%SZ")
                    tw["maxStartTime"] = new_max_start.strftime("%Y-%m-%dT%H:%M:%SZ")
                    # Also adjust maxEndTime if it exists
                    if "maxEndTime" in tw:
                        svc_dur = parse_duration_minutes(v.get("serviceDuration", "PT0M"))
                        tw["maxEndTime"] = (new_max_start + timedelta(minutes=svc_dur)).strftime("%Y-%m-%dT%H:%M:%SZ")
                    widened += 1

    for v in data["modelInput"].get("visits", []):
        widen_visit(v)
    for vg in data["modelInput"].get("visitGroups", []):
        for v in vg.get("visits", []):
            widen_visit(v)

    return widened


def main():
    print(f"Reading {INPUT_FILE}...")
    with open(INPUT_FILE, "r") as f:
        data = json.load(f)

    total_visits_standalone = len(data["modelInput"].get("visits", []))
    total_vg_visits = sum(
        len(vg.get("visits", []))
        for vg in data["modelInput"].get("visitGroups", [])
    )
    original_vehicles = len(data["modelInput"]["vehicles"])
    original_shifts = sum(
        len(v.get("shifts", [])) for v in data["modelInput"]["vehicles"]
    )

    print(f"Original: {original_vehicles} vehicles, {original_shifts} shifts")
    print(f"Visits: {total_visits_standalone} standalone + {total_vg_visits} in groups = {total_visits_standalone + total_vg_visits}")

    visits_per_day = count_visits_per_day(data)
    shifts_per_day = count_shifts_per_day(data)

    print("\n=== BEFORE FIX: visits vs shifts per day ===")
    for day in sorted(visits_per_day.keys()):
        v = visits_per_day[day]
        s = shifts_per_day.get(day, 0)
        dow = datetime.fromisoformat(day).strftime("%a")
        ratio = v / s if s > 0 else float("inf")
        print(f"  {day} ({dow}): {v} visits, {s} shifts, ratio={ratio:.1f}")

    # Step 1: Extend all shifts to full day
    extended = extend_shifts_to_full_day(data)
    print(f"\nStep 1: Extended {extended} shifts to full-day ({FULL_DAY_START}-{FULL_DAY_END})")

    # Step 2: Add extra vehicles for days where visits/shifts ratio > 15
    # Each full-day vehicle can handle ~20-25 visits (avg 25min service + 10min travel)
    TARGET_RATIO = 15
    all_days = sorted(visits_per_day.keys())
    new_shifts_per_day = count_shifts_per_day(data)

    days_needing_extra = {}
    for day in all_days:
        v = visits_per_day[day]
        s = new_shifts_per_day.get(day, 0)
        needed = max(0, (v // TARGET_RATIO) - s + 5)  # +5 buffer
        if needed > 0:
            days_needing_extra[day] = needed

    max_extra = max(days_needing_extra.values()) if days_needing_extra else 0
    new_vehicles = 0
    for i in range(max_extra):
        vehicle_id = f"EXTRA_{i + 1:02d}"
        vehicle_days = [day for day in all_days if days_needing_extra.get(day, 0) > i]
        if vehicle_days:
            data["modelInput"]["vehicles"].append(
                create_full_day_vehicle(vehicle_id, vehicle_days)
            )
            new_vehicles += 1

    print(f"Step 2: Added {new_vehicles} extra full-day vehicles")

    # Step 3: Widen tight time windows
    widened = widen_tight_time_windows(data, min_width_minutes=30)
    print(f"Step 3: Widened {widened} time windows (< 30min -> 30min)")

    # Summary
    final_vehicles = len(data["modelInput"]["vehicles"])
    final_shifts = sum(
        len(v.get("shifts", [])) for v in data["modelInput"]["vehicles"]
    )
    final_shifts_per_day = count_shifts_per_day(data)

    print(f"\n=== AFTER FIX ===")
    print(f"Vehicles: {original_vehicles} -> {final_vehicles} (+{final_vehicles - original_vehicles})")
    print(f"Shifts: {original_shifts} -> {final_shifts} (+{final_shifts - original_shifts})")

    total_shift_hours = 0
    for vehicle in data["modelInput"]["vehicles"]:
        for shift in vehicle.get("shifts", []):
            start = datetime.fromisoformat(shift["minStartTime"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(shift["maxEndTime"].replace("Z", "+00:00"))
            total_shift_hours += (end - start).total_seconds() / 3600

    total_service_hours = 0
    for v in data["modelInput"].get("visits", []):
        total_service_hours += parse_duration_minutes(v.get("serviceDuration", "PT0M")) / 60
    for vg in data["modelInput"].get("visitGroups", []):
        for v in vg.get("visits", []):
            total_service_hours += parse_duration_minutes(v.get("serviceDuration", "PT0M")) / 60

    print(f"\nCapacity: {total_shift_hours:.0f}h shifts / {total_service_hours:.0f}h service = {total_shift_hours / total_service_hours:.2f}x ratio")

    print("\n=== AFTER FIX: visits vs shifts per day ===")
    for day in sorted(visits_per_day.keys()):
        v = visits_per_day[day]
        s = final_shifts_per_day.get(day, 0)
        dow = datetime.fromisoformat(day).strftime("%a")
        ratio = v / s if s > 0 else float("inf")
        print(f"  {day} ({dow}): {v} visits, {s} shifts, ratio={ratio:.1f}")

    # Write output
    print(f"\nWriting {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

    file_size_mb = len(json.dumps(data)) / 1024 / 1024
    print(f"Done! File size: {file_size_mb:.1f} MB")


if __name__ == "__main__":
    main()
