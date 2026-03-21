#!/usr/bin/env python3
"""
Add extra evening shifts to FSR JSON input.

This script adds N additional vehicles with evening shifts (16:00-22:00)
to handle bottlenecks where many visits compete for few evening shifts.

Usage:
  python3 add_evening_shifts_to_fsr.py input.json -o output.json --count 7
  python3 add_evening_shifts_to_fsr.py input.json -o output.json --count 7 --start-date 2026-03-02 --end-date 2026-03-15
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

# Match csv_to_fsr.py (office / default depot)
DEFAULT_OFFICE: List[float] = [59.2368721, 17.9942601]
TIMEZONE_SUFFIX = "+01:00"


def parse_date(s: str) -> datetime:
    """Parse YYYY-MM-DD date string."""
    return datetime.strptime(s, "%Y-%m-%d")


def to_shift_iso(visit_date: datetime, time_str: str) -> str:
    """Combine date and HH:MM into ISO 8601 with timezone (same as csv_to_fsr)."""
    parts = str(time_str).strip().split(":")
    h = int(parts[0]) if parts else 0
    m = int(parts[1]) if len(parts) > 1 else 0
    dt = visit_date.replace(hour=h, minute=m, second=0, microsecond=0)
    return dt.isoformat() + TIMEZONE_SUFFIX


def create_evening_shift(
    shift_id: str,
    visit_date: datetime,
    start_location: List[float],
) -> Dict[str, Any]:
    """Evening shift 16:00–22:00 without break (matches csv_to_fsr _create_shift_no_break)."""
    return {
        "id": shift_id,
        "startLocation": start_location,
        "minStartTime": to_shift_iso(visit_date, "16:00"),
        "maxEndTime": to_shift_iso(visit_date, "22:00"),
        "skills": [],
        "temporarySkillSets": [],
        "temporaryTagSets": [],
        "itinerary": [],
    }


def add_evening_shifts(
    input_path: Path,
    output_path: Path,
    count: int = 7,
    start_date: str | None = None,
    end_date: str | None = None,
) -> None:
    """Add N evening shift vehicles to FSR JSON input."""
    print(f"📖 Reading input: {input_path}")
    with open(input_path) as f:
        data = json.load(f)

    model_input = data.get("modelInput") or data
    vehicles = model_input.get("vehicles", [])

    # Determine planning window
    if start_date and end_date:
        start = parse_date(start_date)
        end = parse_date(end_date)
    else:
        # Infer from existing shifts
        all_dates = set()
        for v in vehicles:
            for s in v.get("shifts", []):
                st = s.get("minStartTime") or s.get("startTime") or ""
                if st:
                    try:
                        normalized = st.replace("Z", "+00:00")
                        dt = datetime.fromisoformat(normalized)
                        all_dates.add(dt.date())
                    except Exception:
                        pass

        if not all_dates:
            raise ValueError("Could not determine planning window. Provide --start-date and --end-date")

        start = datetime.combine(min(all_dates), datetime.min.time())
        end = datetime.combine(max(all_dates), datetime.min.time())

    print(f"📅 Planning window: {start.date()} to {end.date()}")

    # Count existing evening-capable vehicles (approx. from shift start hour)
    existing_evening = sum(
        1
        for v in vehicles
        if any(
            (s.get("minStartTime") or s.get("startTime") or "").split("T")[-1][:2] in ("16", "17", "18", "19")
            for s in v.get("shifts", [])
        )
    )
    print(f"🔍 Found {existing_evening} existing evening-capable vehicles (approx.)")

    # Create new vehicles with evening shifts
    new_vehicles: List[Dict[str, Any]] = []
    current_date = start

    while current_date <= end:
        for i in range(1, count + 1):
            vehicle_id = f"kvall_extra_{i}"
            shift_id = f"{vehicle_id}_shift_{current_date.strftime('%Y-%m-%d')}"

            # Find or create vehicle
            vehicle = next((v for v in new_vehicles if v.get("id") == vehicle_id), None)
            if not vehicle:
                vehicle = {
                    "id": vehicle_id,
                    "vehicleType": "VAN",
                    "shifts": [],
                }
                new_vehicles.append(vehicle)

            shift = create_evening_shift(shift_id, current_date, DEFAULT_OFFICE)
            vehicle["shifts"].append(shift)

        current_date += timedelta(days=1)

    print(f"✅ Created {len(new_vehicles)} new vehicles with {sum(len(v['shifts']) for v in new_vehicles)} shifts")

    # Add new vehicles to model input
    model_input["vehicles"] = vehicles + new_vehicles

    # Update vehicle count in metadata if present
    if "metadata" in model_input:
        model_input["metadata"]["originalVehicleCount"] = len(vehicles)
        model_input["metadata"]["addedEveningVehicles"] = count
        model_input["metadata"]["totalVehicleCount"] = len(model_input["vehicles"])

    # Write output
    print(f"💾 Writing output: {output_path}")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✨ Successfully added {count} evening shift vehicles")
    print(f"   - New vehicles: {len(new_vehicles)}")
    print(f"   - New shifts: {sum(len(v['shifts']) for v in new_vehicles)}")
    print(f"   - Total vehicles: {len(model_input['vehicles'])}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Add extra evening shifts to FSR JSON input")
    parser.add_argument("input", type=Path, help="Input FSR JSON file")
    parser.add_argument("-o", "--output", type=Path, help="Output JSON path (default: input with _with_shifts suffix)")
    parser.add_argument("--count", type=int, default=7, help="Number of extra evening vehicles to add (default: 7)")
    parser.add_argument("--start-date", type=str, help="Planning start date (YYYY-MM-DD). Auto-detected if not provided")
    parser.add_argument("--end-date", type=str, help="Planning end date (YYYY-MM-DD). Auto-detected if not provided")

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input not found: {args.input}", file=sys.stderr)
        return 1

    output = args.output or args.input.parent / f"{args.input.stem}_with_shifts.json"

    try:
        add_evening_shifts(
            args.input,
            output,
            count=args.count,
            start_date=args.start_date,
            end_date=args.end_date,
        )
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
