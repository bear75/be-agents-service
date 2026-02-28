#!/usr/bin/env python3
"""
Generate employee/vehicle placeholders from SOURCE CSV using external_slinga_shiftName.

Creates ONE vehicle per unique shift name (employee), including those with no visits.
Each vehicle gets shifts for their working weekdays × 2 weeks. Uses shift_type,
shift_start, shift_end, shift_break_* and parses weekday from occurence (Varje vecka, mån etc).

Shift hours: weekday day 7.5h (07:00-15:00 −30m break), weekend day 7h (07:00-14:30 −30m),
evening 6h (16:00-22:00). Total ~78 shifts × ~35h ≈ 2730h. Visit hours ~1523h.

Usage:
  Called by csv_to_timefold_fsr.py with source_csv_path.
"""

import csv
import re
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Default office/depot location (Huddinge)
DEFAULT_OFFICE = [59.2368721, 17.9942601]
PLANNING_START_DATE = "2026-02-16"
TIMEZONE_SUFFIX = "+01:00"

# Shift names to exclude (inactive)
EXCLUDED_SHIFT_NAMES = {"", "städ", "vilande kunder/besök", "external_slinga_shiftname"}

# Swedish weekday in occurence -> Python weekday (Mon=0, Sun=6)
OCCURRENCE_WEEKDAY = {
    "mån": 0, "månag": 0, "måndag": 0,
    "tis": 1, "tisdag": 1,
    "ons": 2, "onsdag": 2,
    "tor": 3, "torsdag": 3,
    "fre": 4, "fredag": 4,
    "lör": 5, "lördag": 5,
    "sön": 6, "söndag": 6,
}


def _parse_weekday_from_occurence(occ: str) -> int | None:
    """Parse weekday from occurence e.g. 'Varje vecka, mån' -> 0 (Monday)."""
    if not occ:
        return None
    s = str(occ).strip().lower()
    for key, wd in OCCURRENCE_WEEKDAY.items():
        if key in s:
            return wd
    return None


def _slug(s: str) -> str:
    """Create Timefold-safe ID from shift name."""
    slug = re.sub(r"[^\w\s-]", "", s.strip())
    slug = re.sub(r"[\s_]+", "_", slug).strip("_")
    return slug or "employee"


def _parse_float(val: Any, default: float = 0.0) -> float:
    if val is None or val == "":
        return default
    try:
        return float(str(val).replace(",", "."))
    except (ValueError, TypeError):
        return default


def _parse_int(val: Any, default: int = 0) -> int:
    if val is None or val == "":
        return default
    try:
        return int(float(str(val).replace(",", ".")))
    except (ValueError, TypeError):
        return default


def _looks_like_time(s: str) -> bool:
    """True if s looks like HH:MM or HH:MM:SS (for break_max_start / break_max_end)."""
    if not s or not isinstance(s, str):
        return False
    s = s.strip()
    if not s:
        return False
    parts = s.split(":")
    if len(parts) < 2:
        return False
    try:
        h, m = int(parts[0]), int(parts[1])
        return 0 <= h <= 23 and 0 <= m <= 59
    except (ValueError, TypeError):
        return False


def _to_iso_datetime(date: datetime, time_str: str) -> str:
    parts = str(time_str).strip().split(":")
    h = int(parts[0]) if parts else 0
    m = int(parts[1]) if len(parts) > 1 else 0
    dt = date.replace(hour=h, minute=m, second=0, microsecond=0)
    return dt.isoformat() + TIMEZONE_SUFFIX


def _minutes_to_iso_duration(minutes: int) -> str:
    if minutes < 60:
        return f"PT{minutes}M"
    h, m = minutes // 60, minutes % 60
    return f"PT{h}H{m}M" if m else f"PT{h}H"


def create_shift(
    shift_id: str,
    visit_date: datetime,
    shift_start: str,
    shift_end: str,
    start_location: List[float],
    break_duration: int,
    break_min_start: str,
    break_max_end: str,
    break_location: List[float] | None = None,
    break_max_start: str | None = None,
) -> Dict[str, Any]:
    """Create a single shift object for Timefold FSR.

    When break_location is set, the break is sent with that location so the solver
    schedules travel to/from the break place (same behaviour as visits).
    Uses standard Break API: id, location (nullable), minStartTime, maxStartTime (nullable),
    maxEndTime (nullable), duration. LEGACY type/costImpact are not emitted.
    """
    min_start = _to_iso_datetime(visit_date, shift_start)
    max_end = _to_iso_datetime(visit_date, shift_end)

    shift: Dict[str, Any] = {
        "id": shift_id,
        "startLocation": start_location,
        "minStartTime": min_start,
        "maxEndTime": max_end,
        "tags": [],
        "itinerary": [],
    }

    if break_duration > 0 and break_min_start and break_max_end:
        br_min = _to_iso_datetime(visit_date, break_min_start)
        br_max = _to_iso_datetime(visit_date, break_max_end)
        break_obj: Dict[str, Any] = {
            "id": f"{shift_id}_break",
            "minStartTime": br_min,
            "maxEndTime": br_max,
            "duration": _minutes_to_iso_duration(break_duration),
        }
        # Emit maxStartTime when valid time in CSV, or use default 13:00 (start + duration = maxEndTime 13:30)
        effective_max_start = break_max_start if (break_max_start and _looks_like_time(break_max_start)) else "13:00"
        break_obj["maxStartTime"] = _to_iso_datetime(visit_date, effective_max_start)
        if break_location is not None:
            break_obj["location"] = break_location
        shift["requiredBreaks"] = [break_obj]

    return shift


def _get_row_value(row: Dict[str, Any], huddinge_col: str, nova_col: str | None, default: str = "") -> str:
    """Get value from row; use nova_col when source_format is nova."""
    if nova_col and nova_col in row and str(row[nova_col]).strip():
        return str(row[nova_col]).strip()
    return str(row.get(huddinge_col, default)).strip()


def _employee_schedule_from_source(
    source_csv_path: Path,
    planning_start: datetime,
    planning_weeks: int,
    delimiter: str,
    source_format: str = "huddinge",
) -> Tuple[
    Dict[str, Set[int]],  # emp_id -> set of weekdays (0-6) they work
    Dict[Tuple[str, int], List[Tuple[str, str, int, str, str, float, float, float, float]]],  # (emp_id, wd) -> list of shift params
    Dict[str, Tuple[float, float]],  # emp_id -> (lat, lon)
]:
    """
    From SOURCE CSV, build employee pool and (employee, weekday) -> list of shift times.

    Allows multiple shifts per (emp, weekday) so day and evening shifts are both included
    (e.g. Nova: 07:15-16:00 and 15:45-21:30 for the same Slinga on the same weekday).

    Two locations: service area (start/depot) and break location. If break_lat/break_lon
    are missing or zero, break location falls back to service area (Huddinge/Nova placeholder).

    Returns:
        emp_weekdays: employee_id -> set of weekdays (0=Mon, 6=Sun)
        emp_wd_shift: (emp_id, weekday) -> list of (shift_start, shift_end, break_dur, break_min, break_max, break_max_start, lat, lon, break_lat, break_lon)
        emp_location: emp_id -> (lat, lon)
    """
    nova = source_format.lower() == "nova"

    with open(source_csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)

    emp_weekdays: Dict[str, Set[int]] = defaultdict(set)
    emp_wd_shift: Dict[Tuple[str, int], List[Tuple[str, str, int, str, str, str | None, float, float, float, float]]] = defaultdict(list)
    emp_location: Dict[str, Tuple[float, float]] = {}
    # Deduplicate: source CSV has one row per recurring visit (same shift name repeated per client).
    # We want one shift per (employee, weekday, shift type), not one per row.
    seen_shift_key: Set[Tuple[str, int, str, str, int, str, str, str | None]] = set()

    for row in rows:
        shift_name = _get_row_value(row, "external_slinga_shiftName", "Slinga" if nova else None)
        if not shift_name or shift_name.lower() in EXCLUDED_SHIFT_NAMES:
            continue

        st = str(row.get("shift_type", "day")).strip().lower()
        if st == "inactive":
            continue

        emp_id = _slug(shift_name)
        occ = (
            row.get("weekday", "") if nova else (row.get("recurring_external", "") or row.get("occurence", ""))
        )
        wd = _parse_weekday_from_occurence(str(occ))
        if wd is None:
            continue

        shift_start = _get_row_value(row, "shift_start", None, "07:00") or "07:00"
        shift_end = _get_row_value(row, "shift_end", None, "15:00") or "15:00"
        break_dur = _parse_int(row.get("shift_break_duration") or row.get("slinga_break_duration", 0))
        break_min = _get_row_value(row, "shift_break_minStart", "slinga_break_min_start", "10:00") or "10:00"
        # Default break window: maxStartTime 13:00, duration 30m, maxEndTime 13:30 (start + duration = end)
        break_max = _get_row_value(row, "shift_break_maxEnd", "slinga_break_max_end", "13:30") or "13:30"
        break_max_start = _get_row_value(row, "shift_break_maxStart", "slinga_break_max_start", "13:00") or "13:00"
        if not break_max_start.strip():
            break_max_start = "13:00"

        # Deduplicate: one shift per (emp, weekday, shift type identified by times)
        shift_key = (emp_id, wd, shift_start, shift_end, break_dur, break_min, break_max, break_max_start)
        if shift_key in seen_shift_key:
            continue
        seen_shift_key.add(shift_key)

        # Service area (depot / start location)
        lat = _parse_float(row.get("serviceArea_lat") or row.get("office_lat"), DEFAULT_OFFICE[0])
        lon = _parse_float(row.get("serviceArea_lon") or row.get("office_lon"), DEFAULT_OFFICE[1])
        if lat == 0 and lon == 0:
            lat, lon = DEFAULT_OFFICE[0], DEFAULT_OFFICE[1]

        # Break location: optional; if missing/zero use service area (office) so travel to/from break is computed
        break_lat = _parse_float(row.get("break_lat") or row.get("slinga_break_lat"), 0.0)
        break_lon = _parse_float(row.get("break_lon") or row.get("slinga_break_lon"), 0.0)

        emp_weekdays[emp_id].add(wd)
        key = (emp_id, wd)
        shift_params = (shift_start, shift_end, break_dur, break_min, break_max, break_max_start, lat, lon, break_lat, break_lon)
        # Append so we keep both day and evening shifts for same (emp, weekday)
        emp_wd_shift[key].append(shift_params)
        if emp_id not in emp_location:
            emp_location[emp_id] = (lat, lon)

    return dict(emp_weekdays), dict(emp_wd_shift), emp_location


def generate_vehicles(
    source_csv_path: Path,
    planning_start_date: str = PLANNING_START_DATE,
    planning_weeks: int = 2,
    delimiter: str = ";",
    source_format: str = "huddinge",
    trimmed_shift_dates: set[tuple[str, str]] | set[tuple[str, str, str]] | None = None,
) -> List[Dict[str, Any]]:
    """
    Generate vehicles (employees) from SOURCE CSV using external_slinga_shiftName.

    One vehicle per unique shift name (39 employees with Vilande removed). Each vehicle
    gets shifts for their working weekdays × 2 weeks. Total ~78 shifts, ~2730 shift hours.

    If trimmed_shift_dates is provided, only create shifts for (vehicle_id, date_iso)
    or (vehicle_id, date_iso, shift_kind) in that set. Use 3-tuples when set contains
    (vid, date, "day"|"evening") so we match exactly one shift per (vehicle, date, kind).
    Shift kind is inferred from shift_end: end hour <= 15.5 -> "day", else "evening".

    Returns:
        List of vehicle objects for Timefold modelInput.vehicles.
    """
    planning_start = datetime.strptime(planning_start_date, "%Y-%m-%d")

    emp_weekdays, emp_wd_shift, emp_location = _employee_schedule_from_source(
        source_csv_path, planning_start, planning_weeks, delimiter, source_format
    )

    if not emp_weekdays:
        return []

    use_triples = False
    if trimmed_shift_dates:
        first = next(iter(trimmed_shift_dates), ())
        use_triples = len(first) == 3

    # Build list of all dates in planning window
    dates: List[datetime] = []
    for week in range(planning_weeks):
        for day in range(7):
            dates.append(planning_start + timedelta(weeks=week, days=day))

    used_ids: Set[str] = set()
    vehicles: List[Dict[str, Any]] = []
    added_triples: Set[Tuple[str, str, str]] = set()  # when trimming: at most one shift per (base_id, date_iso, kind)

    for emp_id in sorted(emp_weekdays.keys()):
        base_id = emp_id
        idx = 0
        while emp_id in used_ids:
            idx += 1
            emp_id = f"{base_id}_{idx}"
        used_ids.add(emp_id)

        weekdays = emp_weekdays[base_id]
        lat, lon = emp_location.get(base_id, DEFAULT_OFFICE)
        start_location = [lat, lon]

        shifts: List[Dict[str, Any]] = []
        for d in dates:
            wd = d.weekday()
            if wd not in weekdays:
                continue
            key = (base_id, wd)
            if key not in emp_wd_shift:
                continue
            date_iso = d.date().isoformat()
            # One shift per (emp, wd) entry: day and evening shifts both included
            for ss, se, bd, bmin, bmax, bmax_start, _lat, _lon, break_lat, break_lon in emp_wd_shift[key]:
                if trimmed_shift_dates is not None:
                    shift_kind = "evening" if (_parse_time_hour(se) or 0) >= 15.5 else "day"
                    if use_triples:
                        if (base_id, date_iso, shift_kind) not in trimmed_shift_dates:
                            continue
                        if (base_id, date_iso, shift_kind) in added_triples:
                            continue
                        added_triples.add((base_id, date_iso, shift_kind))
                    else:
                        if (base_id, date_iso) not in trimmed_shift_dates:
                            continue
                shift_id = str(uuid.uuid4())[:8]
                # Use break_lat/break_lon when both set; else service area (office) so travel to/from break is computed
                if break_lat != 0 or break_lon != 0:
                    break_location = [break_lat, break_lon]
                else:
                    break_location = start_location
                shift_dict = create_shift(
                    shift_id=shift_id,
                    visit_date=d,
                    shift_start=ss,
                    shift_end=se,
                    start_location=start_location,
                    break_duration=bd,
                    break_min_start=bmin,
                    break_max_end=bmax,
                    break_location=break_location,
                    break_max_start=bmax_start,
                )
                shifts.append(shift_dict)

        if shifts:
            vehicles.append({
                "id": emp_id,
                "vehicleType": "VAN",
                "shifts": shifts,
                "historicalTimeUtilized": "PT0S",
                "historicalTimeCapacity": "PT0S",
            })

    return vehicles


def _parse_time_hour(time_str: str) -> float | None:
    """Parse 'HH:MM' or 'HH:MM:SS' to hour as float. Returns None if invalid."""
    if not time_str or not isinstance(time_str, str):
        return None
    parts = time_str.strip().split(":")
    if not parts:
        return None
    try:
        h = int(parts[0])
        m = int(parts[1]) if len(parts) > 1 else 0
        return h + m / 60.0
    except (ValueError, TypeError):
        return None
