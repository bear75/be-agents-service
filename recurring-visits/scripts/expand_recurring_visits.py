#!/usr/bin/env python3
"""
Expand recurring visit patterns to explicit visit occurrences within planning window.

Uses frequency column and recurringVisit_id to determine expansion. Time window rules:

- Daily: One time window per day (day-specific). Weekday from recurring_external / occurence.
- Biweekly: Only *1 is biweekly; use full 2-week window; solver picks day.
- Monthly: Only *1 is relevant; use full 4-week planning window.
- Weekly x1: Full week window; solver picks the day.
- Weekly x2–x6: Weekday is in the data (recurring_external e.g. "Varje vecka, tor" → Thursday).
  One expanded row per occurrence. We use that weekday to set a day-specific time window:
  get_visit_date_from_weekday_index(planning_start, weekday_index, week) then
  calculate_time_windows_daily(row, visit_date) so minStartTime, maxStartTime, maxEndTime
  are all on that single day. No inventing weekdays—enforces different days per recurring id.

Usage:
  python expand_recurring_visits.py input.csv -o expanded.csv --weeks 2
"""

import argparse
import csv
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# Allow importing from scripts directory when run from parent
_scripts_dir = Path(__file__).resolve().parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from calculate_time_windows import (
    PLANNING_START_DATE,
    TIMEZONE_SUFFIX,
    calculate_time_windows_daily,
    calculate_time_windows_period,
    get_visit_date_from_weekday_index,
)


def _parse_int(val: Any, default: int = 0) -> int:
    """Safely parse integer."""
    if val is None or val == "":
        return default
    try:
        return int(float(str(val).replace(",", ".")))
    except (ValueError, TypeError):
        return default


def _parse_float(val: Any, default: float = 0.0) -> float:
    """Safely parse float (handles comma decimal)."""
    if val is None or val == "":
        return default
    try:
        return float(str(val).replace(",", "."))
    except (ValueError, TypeError):
        return default


def _address_string(row: Dict[str, Any]) -> str:
    """Build a geocode-able address from street, postal code, city. Empty if no usable parts."""
    street = str(row.get("client_addressStreet", "") or "").strip()
    postal = str(row.get("client_addressPostalCdode", "") or "").strip()
    postal = re.sub(r"\s+", "", postal)
    city = str(row.get("client_addressCity", "") or "").strip()
    if not street and not postal and not city:
        return ""
    if street:
        return f"{street}, {postal} {city}, Sweden".strip(" ,")
    return f"{postal} {city}, Sweden".strip(" ,")


def _geocode_nominatim(
    address: str, cache: Dict[str, Tuple[Optional[float], Optional[float]]]
) -> Tuple[Optional[float], Optional[float]]:
    """Geocode one address via Nominatim (OSM). Uses cache; respects 1 req/sec. Returns (lat, lon) or (None, None)."""
    if not address or not address.strip():
        return (None, None)
    key = address.strip()
    if key in cache:
        return cache[key]
    try:
        url = "https://nominatim.openstreetmap.org/search?" + urlencode({"q": key, "format": "json", "limit": 1})
        req = Request(url, headers={"User-Agent": "AppCaireRecurringVisits/1.0"})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        if data:
            lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
            cache[key] = (lat, lon)
            return (lat, lon)
    except Exception:
        pass
    cache[key] = (None, None)
    return (None, None)


def _fill_missing_coordinates(
    rows: List[Dict[str, Any]],
    geocode_rate_sec: float = 1.0,
) -> None:
    """
    For rows that have an address but missing client_lat/client_lon, geocode and fill.
    Mutates rows in place so addresses get coordinates (week/day time windows already applied later).
    """

    def has_coords(r: Dict[str, Any]) -> bool:
        lat = _parse_float(r.get("client_lat"), 0)
        lon = _parse_float(r.get("client_lon"), 0)
        return not (lat == 0 and lon == 0)

    address_to_indices: Dict[str, List[int]] = defaultdict(list)
    for i, row in enumerate(rows):
        if has_coords(row):
            continue
        addr = _address_string(row)
        if addr:
            address_to_indices[addr].append(i)

    if not address_to_indices:
        return

    n_unique = len(address_to_indices)
    n_rows = sum(len(indices) for indices in address_to_indices.values())
    print(f"Geocoding {n_unique} unique address(es) for {n_rows} row(s) with missing coordinates...", file=sys.stderr)

    cache: Dict[str, Tuple[Optional[float], Optional[float]]] = {}
    for addr, indices in address_to_indices.items():
        lat, lon = _geocode_nominatim(addr, cache)
        if lat is not None and lon is not None:
            for i in indices:
                rows[i]["client_lat"] = lat
                rows[i]["client_lon"] = lon
        time.sleep(geocode_rate_sec)


def parse_frequency(freq_str: str) -> Tuple[str, int]:
    """
    Parse frequency column to (type, occurrences_per_period).

    Returns:
        ("daily", 1), ("weekly", 1), ("weekly", 2), ("weekly", 4),
        ("biweekly", 1), ("4weekly", 1), ("3weekly", 1), ("monthly", 1)
    """
    if not freq_str:
        return ("weekly", 1)
    s = str(freq_str).strip().lower()

    if "daily" in s or "dag" in s:
        return ("daily", 1)
    if "monthly" in s or "månad" in s:
        return ("monthly", 1)
    if "biweekly" in s or "varannan" in s:
        return ("biweekly", 1)
    # 4weekly / "Var 4:e vecka" (once every 4 weeks) - must be before "weekly"
    if "4weekly" in s or "4:e vecka" in s or "var 4:e" in s:
        return ("4weekly", 1)
    # 3weekly / "Var 3:e vecka" (once every 3 weeks) - must be before "weekly"
    if "3weekly" in s or "3:e vecka" in s or "var 3:e" in s:
        return ("3weekly", 1)

    # weekly x1, weekly x2, weekly x3, weekly x4
    m = re.search(r"weekly\s*x\s*(\d+)", s)
    if m:
        occ = _parse_int(m.group(1), 1)
        return ("weekly", max(1, min(occ, 7)))
    if "weekly" in s or "vecka" in s:
        return ("weekly", 1)

    return ("weekly", 1)


def is_inactive(row: Dict[str, Any]) -> bool:
    """Check if visit should be skipped (inactive)."""
    shift_type = str(row.get("shift_type", "")).strip().lower()
    if shift_type == "inactive":
        return True
    visit_note = str(row.get("visit_note", "") or "").strip().upper()
    if "INACTIVE" in visit_note:
        return True
    return False


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


def build_daily_groups(rows: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group rows by recurringVisit_id. Daily groups may have 7+ rows (e.g. 14 for 2 employees × 7 days).

    Returns dict: recurringVisit_id -> list of rows sorted by visit_id
    """
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        rvid = str(row.get("recurringVisit_id", "")).strip()
        if rvid:
            groups[rvid].append(row)

    # Sort each group by visit_id
    for rvid in groups:
        groups[rvid] = sorted(groups[rvid], key=lambda r: _parse_int(r.get("visit_id", 0)))
    return dict(groups)


def expand_row(
    row: Dict[str, Any],
    planning_start: datetime,
    planning_weeks: int,
    weekday_index: Optional[int],
    freq_type: str,
    occ_per_period: int,
) -> List[Dict[str, Any]]:
    """
    Expand a single row into occurrence rows.

    Args:
        row: CSV row
        planning_start: Monday of week 0
        planning_weeks: 2 or 4
        weekday_index: For daily and weekly x2–x6: 0–6 from recurring_external. For weekly x1, biweekly, monthly: None (full-period window).
        freq_type: "daily", "weekly", "biweekly", "3weekly", "4weekly", "monthly"
        occ_per_period: 1, 2, 3, 4 for weekly

    Returns:
        List of expanded rows with minStartTime, maxStartTime, maxEndTime
    """
    visit_id = str(row.get("visit_id", "")).strip()
    if not visit_id:
        return []

    expanded = []

    if freq_type == "daily" and weekday_index is not None:
        for week in range(planning_weeks):
            visit_date = get_visit_date_from_weekday_index(
                planning_start, weekday_index, week
            )
            min_st, max_st, max_end = calculate_time_windows_daily(row, visit_date)
            new_row = {**row}
            new_row["week"] = str(week)
            new_row["frequency_type"] = "daily"
            new_row["minStartTime"] = min_st
            new_row["maxStartTime"] = max_st
            new_row["maxEndTime"] = max_end
            new_row["date"] = visit_date.strftime("%Y-%m-%d")
            expanded.append(new_row)

    elif freq_type == "weekly":
        duration = _parse_int(row.get("duration", 0))
        if weekday_index is not None:
            # Weekly x2–x6: weekday from recurring_external (e.g. "Varje vecka, lör" -> Saturday).
            # One occurrence per week on that day; day-specific window so no same-day stacking.
            for week in range(planning_weeks):
                visit_date = get_visit_date_from_weekday_index(
                    planning_start, weekday_index, week
                )
                min_st, max_st, max_end = calculate_time_windows_daily(row, visit_date)
                new_row = {**row}
                new_row["week"] = str(week)
                new_row["frequency_type"] = "weekly"
                new_row["minStartTime"] = min_st
                new_row["maxStartTime"] = max_st
                new_row["maxEndTime"] = max_end
                new_row["date"] = visit_date.strftime("%Y-%m-%d")
                expanded.append(new_row)
        else:
            # Weekly x1: full-week window; solver picks best day.
            for week in range(planning_weeks):
                min_st, max_end = calculate_time_windows_period(
                    planning_start, week, 1
                )
                max_end_dt = datetime.fromisoformat(max_end.replace(TIMEZONE_SUFFIX, ""))
                max_st_dt = max_end_dt - timedelta(minutes=duration)
                max_st = max_st_dt.isoformat() + TIMEZONE_SUFFIX
                new_row = {**row}
                new_row["week"] = str(week)
                new_row["frequency_type"] = "weekly"
                new_row["minStartTime"] = min_st
                new_row["maxStartTime"] = max_st
                new_row["maxEndTime"] = max_end
                expanded.append(new_row)

    elif freq_type == "biweekly":
        duration = _parse_int(row.get("duration", 0))
        for week in range(0, planning_weeks, 2):
            min_st, max_end = calculate_time_windows_period(
                planning_start, week, 2
            )
            max_end_dt = datetime.fromisoformat(max_end.replace(TIMEZONE_SUFFIX, ""))

            max_st_dt = max_end_dt - timedelta(minutes=duration)
            max_st = max_st_dt.isoformat() + TIMEZONE_SUFFIX
            new_row = {**row}
            new_row["week"] = str(week)
            new_row["frequency_type"] = "biweekly"
            new_row["minStartTime"] = min_st
            new_row["maxStartTime"] = max_st
            new_row["maxEndTime"] = max_end
            expanded.append(new_row)

    elif freq_type == "3weekly":
        # One occurrence every 3 weeks (e.g. weeks 0 and 3 in a 4-week window)
        duration = _parse_int(row.get("duration", 0))
        for week in range(0, planning_weeks, 3):
            min_st, max_end = calculate_time_windows_period(
                planning_start, week, 3
            )
            max_end_dt = datetime.fromisoformat(max_end.replace(TIMEZONE_SUFFIX, ""))
            max_st_dt = max_end_dt - timedelta(minutes=duration)
            max_st = max_st_dt.isoformat() + TIMEZONE_SUFFIX
            new_row = {**row}
            new_row["week"] = str(week)
            new_row["frequency_type"] = "3weekly"
            new_row["minStartTime"] = min_st
            new_row["maxStartTime"] = max_st
            new_row["maxEndTime"] = max_end
            expanded.append(new_row)

    elif freq_type == "4weekly":
        # One occurrence per 4-week period (Var 4:e vecka); only when window >= 4 weeks
        if planning_weeks >= 4:
            duration = _parse_int(row.get("duration", 0))
            week = 0
            min_st, max_end = calculate_time_windows_period(
                planning_start, week, 4
            )
            max_end_dt = datetime.fromisoformat(max_end.replace(TIMEZONE_SUFFIX, ""))
            max_st_dt = max_end_dt - timedelta(minutes=duration)
            max_st = max_st_dt.isoformat() + TIMEZONE_SUFFIX
            new_row = {**row}
            new_row["week"] = "0"
            new_row["frequency_type"] = "4weekly"
            new_row["minStartTime"] = min_st
            new_row["maxStartTime"] = max_st
            new_row["maxEndTime"] = max_end
            expanded.append(new_row)

    elif freq_type == "monthly":
        if planning_weeks >= 4:
            duration = _parse_int(row.get("duration", 0))
            week = 0
            min_st, max_end = calculate_time_windows_period(
                planning_start, week, 4
            )
            max_end_dt = datetime.fromisoformat(max_end.replace(TIMEZONE_SUFFIX, ""))

            max_st_dt = max_end_dt - timedelta(minutes=duration)
            max_st = max_st_dt.isoformat() + TIMEZONE_SUFFIX
            new_row = {**row}
            new_row["week"] = "0"
            new_row["frequency_type"] = "monthly"
            new_row["minStartTime"] = min_st
            new_row["maxStartTime"] = max_st
            new_row["maxEndTime"] = max_end
            expanded.append(new_row)

    return expanded


def expand_visits(
    csv_path: Path,
    output_path: Path,
    planning_weeks: int = 2,
    planning_start_date: str = PLANNING_START_DATE,
    delimiter: str = ";",
    write_delimiter: str | None = None,
) -> int:
    """
    Expand recurring CSV to planning window CSV.

    delimiter: used when reading csv_path (sources are often ;).
    write_delimiter: used when writing output_path (default: delimiter). Use "," for dashboard upload.
    Returns number of expanded rows written.
    """
    out_delim = write_delimiter if write_delimiter is not None else delimiter
    planning_start = datetime.strptime(planning_start_date, "%Y-%m-%d")
    planning_start = planning_start.replace(hour=7, minute=0, second=0, microsecond=0)

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)

    if not rows:
        print("Error: Input CSV is empty", file=sys.stderr)
        return 0

    # Geocode rows with address but missing coordinates so they get coordinates (week/day windows applied below).
    _fill_missing_coordinates(rows)

    daily_groups = build_daily_groups(rows)
    expanded_rows: List[Dict[str, Any]] = []
    skipped = 0

    for row in rows:
        if is_inactive(row):
            skipped += 1
            continue

        visit_id = str(row.get("visit_id", "")).strip()
        rvid = str(row.get("recurringVisit_id", "")).strip()
        freq_str = str(row.get("frequency", "")).strip()
        freq_type, occ_per_period = parse_frequency(freq_str)

        # Daily: use occurence or recurring_external for weekday (e.g. "Varje vecka, tis" -> Tue).
        # Weekly x2–x6: weekday is defined in source (recurring_external e.g. "Varje vecka, lör" / "lsön");
        # use it so each row gets a single-day time window (no multiple occurrences on same day).
        # Weekly x1, biweekly, monthly, etc.: full period window; solver picks day.
        occ = str(row.get("occurence", "") or row.get("recurring_external", "")).strip()
        if freq_type == "daily":
            weekday_index = _parse_weekday_from_occurence(occ)
            if weekday_index is None:
                weekday_index = 0  # fallback to Monday
        elif freq_type == "weekly" and occ_per_period >= 2:
            weekday_index = _parse_weekday_from_occurence(occ)
            if weekday_index is None:
                weekday_index = 0  # fallback to Monday
        else:
            weekday_index = None

        for new_row in expand_row(
            row, planning_start, planning_weeks, weekday_index, freq_type, occ_per_period
        ):
            expanded_rows.append(new_row)

    if not expanded_rows:
        print("Error: No visits to write (all skipped or invalid)", file=sys.stderr)
        return 0

    exclude_cols = {"visit_id", "visit_id_occurrence", "occurence", "startDate", "endDate", "client_caireConact"}
    for i, row in enumerate(expanded_rows):
        row["original_visit_id"] = str(i + 1)
        for c in exclude_cols:
            row.pop(c, None)
    # Collect all unique keys across all rows (some rows have extra fields like 'date')
    seen = set()
    all_fields: list[str] = []
    for row in expanded_rows:
        for k in row.keys():
            if k not in seen:
                seen.add(k)
                all_fields.append(k)
    fieldnames = [f for f in all_fields if f not in exclude_cols]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=out_delim)
        writer.writeheader()
        writer.writerows(expanded_rows)

    print(f"Expanded: {len(rows)} rows -> {len(expanded_rows)} rows")
    if skipped > 0:
        print(f"Skipped: {skipped} inactive rows")
    print(f"Wrote: {output_path}")
    return len(expanded_rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Expand recurring visits to planning window")
    parser.add_argument("input", type=Path, help="Input CSV (Huddinge format)")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output CSV")
    parser.add_argument("--weeks", type=int, default=2, choices=[2, 4], help="Planning weeks")
    parser.add_argument(
        "--start-date",
        default=PLANNING_START_DATE,
        help=f"Planning start Monday (default: {PLANNING_START_DATE})",
    )
    parser.add_argument(
        "--delimiter",
        default=";",
        help="Delimiter for reading input CSV (default: ;)",
    )
    parser.add_argument(
        "--write-delimiter",
        default=",",
        help="Delimiter for writing expanded CSV (default: , for dashboard upload)",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input not found: {args.input}", file=sys.stderr)
        return 1

    try:
        expand_visits(
            args.input,
            args.output,
            planning_weeks=args.weeks,
            planning_start_date=args.start_date,
            delimiter=args.delimiter,
            write_delimiter=args.write_delimiter,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
