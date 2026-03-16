#!/usr/bin/env python3
"""
Unified CSV to Timefold FSR JSON converter.

Reads all 3 CSV formats (anonymized, Huddinge, Nova) and produces Timefold FSR modelInput JSON.
Uses configurable column mappings for each format.

Usage:
  python csv_to_timefold_json.py movable_visits_anonymized_v2.csv -o anonymized_input.json
  python csv_to_timefold_json.py Huddinge_Final_Verified_geocoded.csv --format huddinge -o huddinge_input.json
  python csv_to_timefold_json.py Nova_Final_Verified_geocoded.csv --format nova -o nova_input.json

Output format: { "modelInput": { "visits": [...], "vehicles": [...] } }
"""

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Constants
BASE_DATE_DEFAULT = "2026-02-10"  # Monday
WEEKDAY_MAP = {
    "mån": 0, "tis": 1, "ons": 2, "tor": 3, "fre": 4, "lör": 5, "sön": 6,
    "mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6,
}
DEFAULT_OFFICE = [59.2368721, 17.9942601]
PLACEHOLDER_EVENING_SLOTS = 5
PLACEHOLDER_WEEKEND_DAY_SLOTS = 3

# Column mapping configs (internal key -> CSV column name per format)
COLUMN_MAPS = {
    "anonymized": {
        "visit_id": "visit_id",
        "weekday": "slinga_weekday",
        "start_time": "original_start_time",
        "planned_start": "slinga_start_time",
        "duration": "duration",
        "min_before": "Min_before",
        "min_after": "Min_after",
        "slinga": "Slinga",
        "description": "description",
        "priority": "Prio (1-10)",
        "skills": "visit_skills",
        "double_id": "double_id",
        "dormant": "inactive_visit besök",
        "notes": "Note",
        "employee_name": None,  # Not present in anonymized
        "header_row": 2,
        "require_assignment": False,
    },
    "huddinge": {
        "visit_id": "visit_id_str",
        "weekday": "weekday",
        "start_time": "originalstarttime",
        "planned_start": "Starttid",
        "duration": "Längd",
        "min_before": "Min före",
        "min_after": "Min efter",
        "slinga": "Slinga",
        "description": "Beskrivning",
        "priority": "Prio (1-3)",
        "skills": "Insatser",
        "double_id": "Dubbelid",
        "dormant": "Vilande besök",
        "notes": "Notering",
        "employee_name": "FastOMS",
        "header_row": 0,
        "require_assignment": True,
    },
    "nova": {
        "visit_id": "visit_id_str",
        "weekday": "weekday",
        "start_time": "originalstarttime",
        "planned_start": "Starttid",
        "duration": "Längd",
        "min_before": "Min före",
        "min_after": "Min efter",
        "slinga": "Slinga",
        "description": "Beskrivning",
        "priority": "Prio (1-3)",
        "skills": "Insatser",
        "double_id": "Dubbelid",
        "dormant": "Vilande besök",
        "notes": "Notering",
        "employee_name": "FastOMS",
        "header_row": 0,
        "require_assignment": False,  # Nova data often has unassigned visits (pre-planning)
    },
}

skipped_visits: List[Dict[str, Any]] = []


def detect_format(csv_path: Path) -> str:
    """Auto-detect CSV format from headers."""
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        rows = list(reader)
    if not rows:
        return "anonymized"
    # Try row 0 first
    headers_row0 = set(h.strip() for h in rows[0] if h)
    if "visit_id_str" in headers_row0 or "movablevisitid" in headers_row0:
        return "nova" if "NFC" in headers_row0 or "Förnamn" in headers_row0 else "huddinge"
    # Try row 2 (anonymized has annotations in rows 0-1)
    if len(rows) >= 3:
        headers_row2 = set(h.strip() for h in rows[2] if h)
        if "visit_id" in headers_row2 and "slinga_weekday" in headers_row2:
            return "anonymized"
    return "huddinge"


def load_csv(csv_path: Path, fmt: str) -> Dict[str, List[Dict[str, str]]]:
    """Load CSV and group by (slinga, weekday). Returns dict of group_key -> list of rows."""
    cm = COLUMN_MAPS[fmt]
    header_row = cm["header_row"]
    groups: Dict[str, List[Dict[str, str]]] = defaultdict(list)

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        rows = list(reader)

    if len(rows) <= header_row:
        return {}

    headers = [h.strip() for h in rows[header_row]]
    for row_list in rows[header_row + 1 :]:
        if len(row_list) < len(headers):
            row_list.extend([""] * (len(headers) - len(row_list)))
        row = dict(zip(headers, (v.strip() if isinstance(v, str) else str(v) for v in row_list)))

        if _is_inactive(row, cm):
            continue
        if cm["require_assignment"] and not _is_assigned(row, cm):
            continue

        lat = row.get("client_lat", "").strip()
        lon = row.get("client_lon", "").strip()
        if not lat or not lon:
            continue

        slinga = _get(row, cm, "slinga")
        weekday = _get(row, cm, "weekday")
        if not slinga or not weekday or weekday.lower() == "unknown":
            continue

        enriched = {**row}
        enriched["office_lat"] = row.get("office_lat", "59.2368721").replace(",", ".")
        enriched["office_lon"] = row.get("office_lon", "17.9942601").replace(",", ".")
        enriched["shift_start"] = row.get("shift_start", "07:00")
        enriched["shift_end"] = row.get("shift_end", "15:00")
        enriched["shift_type"] = row.get("shift_type", "day")
        enriched["slinga_break_duration"] = row.get("slinga_break_duration", "30")
        enriched["slinga_break_min_start"] = row.get("slinga_break_min_start", "10:00")
        enriched["slinga_break_max_end"] = row.get("slinga_break_max_end", "14:00")
        enriched["_fmt"] = fmt
        enriched["_cm"] = cm

        groups[f"{slinga}_{weekday}"].append(enriched)

    return dict(groups)


def _get(row: Dict[str, str], cm: Dict[str, Any], key: str) -> str:
    col = cm.get(key)
    if col is None:
        return ""
    return row.get(col, "").strip()


def _is_inactive(row: Dict[str, str], cm: Dict[str, Any]) -> bool:
    slinga = row.get("Slinga", "")
    if "Vilande" in slinga:
        return True
    notes = _get(row, cm, "notes")
    if "INACTIVE" in notes or "Besök ej aktivt" in notes:
        return True
    dormant_col = cm.get("dormant")
    if dormant_col and row.get(dormant_col, "").strip():
        return True
    return False


def _is_assigned(row: Dict[str, str], cm: Dict[str, Any]) -> bool:
    emp_col = cm.get("employee_name")
    if not emp_col:
        return True
    slinga = _get(row, cm, "slinga")
    emp = row.get(emp_col, "").strip()
    return bool(emp) and bool(slinga)


def parse_time_to_minutes(time_str: str) -> int:
    if not time_str:
        return 0
    try:
        parts = time_str.split(":")
        return int(parts[0]) * 60 + (int(parts[1]) if len(parts) > 1 else 0)
    except (ValueError, IndexError):
        return 0


def minutes_to_iso_duration(minutes: int) -> str:
    if minutes < 60:
        return f"PT{minutes}M"
    h, m = minutes // 60, minutes % 60
    return f"PT{h}H{m}M" if m else f"PT{h}H"


def get_visit_datetime(base_date: str, weekday_str: str, time_str: str) -> str:
    base = datetime.fromisoformat(base_date)
    wd = weekday_str.lower()[:3] if weekday_str else "mån"
    days_offset = WEEKDAY_MAP.get(wd, 0)
    visit_date = base + timedelta(days=days_offset)
    if time_str and ":" in time_str:
        parts = time_str.split(":")
        visit_date = visit_date.replace(hour=int(parts[0]), minute=int(parts[1]) if len(parts) > 1 else 0)
    return visit_date.isoformat() + "+01:00"


def parse_iso_duration(duration_str: str) -> timedelta:
    pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
    m = re.match(pattern, duration_str)
    if not m:
        return timedelta(0)
    return timedelta(
        hours=int(m.group(1) or 0),
        minutes=int(m.group(2) or 0),
        seconds=int(m.group(3) or 0),
    )


def create_visit(
    row: Dict[str, Any],
    week_offset: int,
    planned: bool,
    base_date: str,
) -> Optional[Dict[str, Any]]:
    cm = row.get("_cm", COLUMN_MAPS["huddinge"])
    visit_id = _get(row, cm, "visit_id")
    duration_minutes = int(_get(row, cm, "duration") or "0")

    lat_str = row.get("client_lat", "").strip()
    lon_str = row.get("client_lon", "").strip()
    if not lat_str or not lon_str:
        skipped_visits.append({"id": visit_id, "reason": "missing_coordinates"})
        return None
    try:
        client_lat = float(lat_str.replace(",", "."))
        client_lon = float(lon_str.replace(",", "."))
    except ValueError:
        skipped_visits.append({"id": visit_id, "reason": "invalid_coordinates"})
        return None
    if client_lat == 0.0 and client_lon == 0.0:
        skipped_visits.append({"id": visit_id, "reason": "zero_coordinates"})
        return None

    weekday = _get(row, cm, "weekday") or "mån"
    planned_start_col = cm.get("planned_start") or cm.get("start_time")
    start_col = cm.get("start_time") or cm.get("planned_start")

    if planned:
        start_time_str = row.get(planned_start_col, "07:00") if planned_start_col else "07:00"
        if not start_time_str:
            start_time_str = "07:00"
        base_dt_str = get_visit_datetime(base_date, weekday, start_time_str)
        base_dt = datetime.fromisoformat(base_dt_str.replace("+01:00", ""))
        if week_offset > 0:
            base_dt += timedelta(weeks=week_offset)
        start_str = base_dt.isoformat() + "+01:00"
        min_start_str = max_start_str = start_str
    else:
        original_start = row.get(start_col, "").strip() or row.get(planned_start_col, "07:00") or "07:00"
        min_before = int(_get(row, cm, "min_before") or "0")
        min_after = int(_get(row, cm, "min_after") or "0")
        base_dt_str = get_visit_datetime(base_date, weekday, original_start)
        base_dt = datetime.fromisoformat(base_dt_str.replace("+01:00", ""))
        if week_offset > 0:
            base_dt += timedelta(weeks=week_offset)
        min_start_dt = base_dt - timedelta(minutes=min_before)
        max_start_dt = base_dt + timedelta(minutes=min_after)
        min_start_str = min_start_dt.isoformat() + "+01:00"
        max_start_str = max_start_dt.isoformat() + "+01:00"

    prio_val = _get(row, cm, "priority") or "1"
    try:
        prio = int(prio_val.split()[0] if prio_val.split() else "1")
    except (ValueError, IndexError):
        prio = 1

    visit = {
        "id": f"{visit_id}_w{week_offset}" if week_offset > 0 else visit_id,
        "location": [client_lat, client_lon],
        "serviceDuration": minutes_to_iso_duration(duration_minutes),
        "timeWindows": [
            {
                "minStartTime": min_start_str,
                "maxStartTime": max_start_str,
                "maxEndTime": (
                    datetime.fromisoformat(max_start_str.replace("+01:00", ""))
                    + parse_iso_duration(minutes_to_iso_duration(duration_minutes))
                ).isoformat()
                + "+01:00",
            }
        ],
        "name": (_get(row, cm, "description") or "")[:100],
        "priority": str(prio),
    }
    # double_id: Timefold FSR schema does not support requiredStaff or metadata.
    # Tandem visits (2 staff) are treated as single-staff for solver; DB mapping
    # stores doubleId in Visit.metadata on import.
    return visit


def create_vehicle_shift(
    slinga_id: str,
    slinga_data: List[Dict[str, Any]],
    week_offset: int,
    base_date: str,
) -> Dict[str, Any]:
    first = slinga_data[0]
    cm = first.get("_cm", COLUMN_MAPS["huddinge"])
    try:
        office_lat = float(first.get("office_lat", "0").replace(",", "."))
        office_lon = float(first.get("office_lon", "0").replace(",", "."))
    except (ValueError, TypeError):
        office_lat, office_lon = DEFAULT_OFFICE[0], DEFAULT_OFFICE[1]

    weekday = _get(first, cm, "weekday") or "mån"
    shift_start = first.get("shift_start", "07:00")
    shift_end = first.get("shift_end", "15:00")
    shift_type = first.get("shift_type", "day")
    emp_col = cm.get("employee_name")
    employee_name = first.get(emp_col, slinga_id) if emp_col else slinga_id

    shift_start_dt = get_visit_datetime(base_date, weekday, shift_start)
    shift_end_dt = get_visit_datetime(base_date, weekday, shift_end)
    if week_offset > 0:
        shift_start_dt = (
            datetime.fromisoformat(shift_start_dt.replace("+01:00", "")) + timedelta(weeks=week_offset)
        ).isoformat() + "+01:00"
        shift_end_dt = (
            datetime.fromisoformat(shift_end_dt.replace("+01:00", "")) + timedelta(weeks=week_offset)
        ).isoformat() + "+01:00"

    break_dur = int(first.get("slinga_break_duration", "30") or "30")
    break_min = first.get("slinga_break_min_start", "10:00")
    break_max = first.get("slinga_break_max_end", "14:00")

    shift_id = f"{slinga_id}_{weekday}_w{week_offset}" if week_offset > 0 else f"{slinga_id}_{weekday}"
    shift: Dict[str, Any] = {
        "id": shift_id,
        "startLocation": [office_lat, office_lon],
        "endLocation": [office_lat, office_lon],
        "minStartTime": shift_start_dt,
        "maxEndTime": shift_end_dt,
        "cost": {"fixedCost": 1375, "rates": []},
    }
    if break_dur > 0:
        br_start = get_visit_datetime(base_date, weekday, break_min)
        br_end = get_visit_datetime(base_date, weekday, break_max)
        if week_offset > 0:
            br_start = (
                datetime.fromisoformat(br_start.replace("+01:00", "")) + timedelta(weeks=week_offset)
            ).isoformat() + "+01:00"
            br_end = (
                datetime.fromisoformat(br_end.replace("+01:00", "")) + timedelta(weeks=week_offset)
            ).isoformat() + "+01:00"
        shift["requiredBreaks"] = [
            {
                "type": "FLOATING",
                "id": f"{shift_id}_break_0",
                "duration": minutes_to_iso_duration(break_dur),
                "minStartTime": br_start,
                "maxEndTime": br_end,
            }
        ]
    return shift


def create_placeholder_shift(
    weekday: str,
    shift_type: str,
    slot_index: int,
    week_offset: int,
    base_date: str,
) -> Dict[str, Any]:
    if shift_type == "evening":
        start_t, end_t = "16:00", "22:00"
    else:
        start_t, end_t = "07:00", "15:00"

    start_dt = get_visit_datetime(base_date, weekday, start_t)
    end_dt = get_visit_datetime(base_date, weekday, end_t)
    if week_offset > 0:
        start_dt = (
            datetime.fromisoformat(start_dt.replace("+01:00", "")) + timedelta(weeks=week_offset)
        ).isoformat() + "+01:00"
        end_dt = (
            datetime.fromisoformat(end_dt.replace("+01:00", "")) + timedelta(weeks=week_offset)
        ).isoformat() + "+01:00"

    shift_id = (
        f"placeholder_{shift_type}_{slot_index}_{weekday}_w{week_offset}"
        if week_offset > 0
        else f"placeholder_{shift_type}_{slot_index}_{weekday}"
    )
    shift: Dict[str, Any] = {
        "id": shift_id,
        "startLocation": DEFAULT_OFFICE,
        "endLocation": DEFAULT_OFFICE,
        "minStartTime": start_dt,
        "maxEndTime": end_dt,
        "cost": {
            "fixedCost": 0,
            "rates": [
                {
                    "unit": "MINUTE",
                    "duration": "PT24H",
                    "costPerUnit": 2.92,
                    "activationCost": 0,
                }
            ],
        },
    }
    if shift_type == "day":
        br_start = get_visit_datetime(base_date, weekday, "10:00")
        br_end = get_visit_datetime(base_date, weekday, "14:00")
        if week_offset > 0:
            br_start = (
                datetime.fromisoformat(br_start.replace("+01:00", "")) + timedelta(weeks=week_offset)
            ).isoformat() + "+01:00"
            br_end = (
                datetime.fromisoformat(br_end.replace("+01:00", "")) + timedelta(weeks=week_offset)
            ).isoformat() + "+01:00"
        shift["requiredBreaks"] = [
            {
                "type": "FLOATING",
                "id": f"{shift_id}_break_0",
                "duration": "PT30M",
                "minStartTime": br_start,
                "maxEndTime": br_end,
            }
        ]
    return shift


def build_vehicles_from_shifts(vehicle_shifts: List[Dict]) -> List[Dict]:
    """Convert flat shifts to vehicles[].shifts[] structure."""
    vehicles_map: Dict[str, List[Dict]] = defaultdict(list)
    for shift in vehicle_shifts:
        shift_id = shift["id"]
        base_id = shift_id
        if base_id.endswith("_w1"):
            base_id = base_id[:-3]
        if "_" in base_id:
            base_id = base_id.rsplit("_", 1)[0]
        vehicles_map[base_id].append(shift)
    return [{"id": vid, "shifts": shifts} for vid, shifts in vehicles_map.items()]


def generate(
    csv_path: Path,
    fmt: str,
    planned: bool,
    weeks: int,
    base_date: str,
) -> Dict[str, Any]:
    global skipped_visits
    skipped_visits = []

    groups = load_csv(csv_path, fmt)
    total_visits = sum(len(v) for v in groups.values())

    visits: List[Dict] = []
    vehicle_shifts: List[Dict] = []

    for week in range(weeks):
        for group_key, rows in groups.items():
            slinga_id = group_key.rsplit("_", 1)[0]
            shift = create_vehicle_shift(slinga_id, rows, week, base_date)
            vehicle_shifts.append(shift)

            for row in rows:
                visit = create_visit(row, week, planned, base_date)
                if visit:
                    visit["pinningRequested"] = planned
                    visits.append(visit)

    if not planned:
        weekdays = ["mån", "tis", "ons", "tor", "fre", "lör", "sön"]
        for week in range(weeks):
            for wd in weekdays:
                for slot in range(PLACEHOLDER_EVENING_SLOTS):
                    vehicle_shifts.append(create_placeholder_shift(wd, "evening", slot, week, base_date))
                if wd in ("lör", "sön"):
                    for slot in range(PLACEHOLDER_WEEKEND_DAY_SLOTS):
                        vehicle_shifts.append(create_placeholder_shift(wd, "day", slot, week, base_date))

    vehicles = build_vehicles_from_shifts(vehicle_shifts)
    return {
        "modelInput": {
            "visits": visits,
            "vehicles": vehicles,
        }
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Convert CSV to Timefold FSR modelInput JSON.")
    ap.add_argument("input", type=Path, help="Input CSV file")
    ap.add_argument("-o", "--output", type=Path, help="Output JSON file (default: <input_stem>_input.json)")
    ap.add_argument(
        "--format",
        choices=["anonymized", "huddinge", "nova"],
        default=None,
        help="CSV format (default: auto-detect from headers)",
    )
    ap.add_argument("--planned", action="store_true", help="Generate planned/pinned output (default: unplanned)")
    ap.add_argument("--weeks", type=int, default=2, help="Number of weeks to expand (default: 2)")
    ap.add_argument("--base-date", default=BASE_DATE_DEFAULT, help=f"Base Monday (default: {BASE_DATE_DEFAULT})")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        return 1

    fmt = args.format or detect_format(args.input)
    print(f"Format: {fmt} (auto-detected)" if not args.format else f"Format: {fmt}")

    out_path = args.output or args.input.with_name(args.input.stem + "_input.json")

    try:
        data = generate(
            args.input,
            fmt,
            planned=args.planned,
            weeks=args.weeks,
            base_date=args.base_date,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise

    n_visits = len(data["modelInput"]["visits"])
    n_vehicles = len(data["modelInput"]["vehicles"])
    n_shifts = sum(len(v["shifts"]) for v in data["modelInput"]["vehicles"])
    print(f"Generated: {n_visits} visits, {n_vehicles} vehicles, {n_shifts} shifts")

    if skipped_visits:
        print(f"Skipped {len(skipped_visits)} visits (invalid/missing coordinates)")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
