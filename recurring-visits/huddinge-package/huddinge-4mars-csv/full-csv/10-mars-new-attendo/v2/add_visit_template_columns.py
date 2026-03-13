#!/usr/bin/env python3
"""
Add visit-template columns to Huddinge CSV for schedule CSV import support.

Adds columns required by the schedule CSV import (per summary 2026-03-12):
- recurringVisit_id (generated from Kundnr + row index)
- recurringVisit_clientName (derived from Kundnr)
- frequency_type (parsed from Återkommande: daily|weekly|biweekly|3weekly|4weekly)
- minStartTime, maxStartTime, maxEndTime (computed from Starttid, Före, Efter, Längd)
- original_visit_id (empty; set when expanding)
- date (empty; set when expanding)
- serviceArea_lat, serviceArea_lon (from Lat/Lon or empty)

Usage:
  python add_visit_template_columns.py [input.csv] [output.csv]
  Default: huddinge-81-clients-v2-with-coords.csv -> same file (in-place update).
"""

import csv
import re
import sys
from pathlib import Path


def _recurrence_type(atterkommande: str) -> str:
    """Return 'daily' | 'weekly' | 'biweekly' | '3weekly' | '4weekly'."""
    if not atterkommande:
        return "weekly"
    s = str(atterkommande).strip().lower()
    if "varje dag" in s:
        return "daily"
    if "varannan" in s:
        return "biweekly"
    if "4:e vecka" in s or "var 4:e" in s:
        return "4weekly"
    if "3:e vecka" in s or "var 3:e" in s:
        return "3weekly"
    return "weekly"


def _parse_int(val, default: int = 0) -> int:
    if val is None or val == "":
        return default
    s = str(val).strip().replace(",", ".")
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return default


def _time_to_minutes(t: str) -> int:
    """Parse HH:MM or HH:MM:SS to minutes since midnight."""
    if not t or not isinstance(t, str):
        return 0
    parts = t.strip().split(":")
    try:
        h = int(parts[0])
        m = int(parts[1]) if len(parts) > 1 else 0
        return h * 60 + m
    except (ValueError, IndexError):
        return 0


def _minutes_to_hhmm(minutes: int) -> str:
    """Format minutes since midnight as HH:MM (clamped to 00:00–23:59)."""
    minutes = max(0, min(24 * 60 - 1, minutes))
    h, m = minutes // 60, minutes % 60
    return f"{h:02d}:{m:02d}"


def _slug(s: str) -> str:
    """Safe ID segment: alphanumeric and underscore only."""
    s = re.sub(r"[^\w\s-]", "", str(s).strip())
    s = re.sub(r"[\s_]+", "_", s).strip("_")
    return s or "unknown"


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    default_input = script_dir / "huddinge-81-clients-v2-with-coords.csv"

    if len(sys.argv) >= 2:
        input_path = Path(sys.argv[1])
    else:
        input_path = default_input

    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        output_path = input_path  # in-place

    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return 1

    new_columns = [
        "recurringVisit_id",
        "recurringVisit_clientName",
        "frequency_type",
        "minStartTime",
        "maxStartTime",
        "maxEndTime",
        "original_visit_id",
        "date",
        "serviceArea_lat",
        "serviceArea_lon",
    ]

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames_orig = reader.fieldnames or []
        rows = list(reader)

    fieldnames = list(fieldnames_orig) + new_columns

    for i, row in enumerate(rows):
        kundnr = (row.get("Kundnr") or "").strip()
        starttid = (row.get("Starttid") or "08:00").strip()
        fore = _parse_int(row.get("Före"), 0)
        efter = _parse_int(row.get("Efter"), 0)
        langd = _parse_int(row.get("Längd"), 0)
        atterkommande = (row.get("Återkommande") or "").strip()
        lat = (row.get("Lat") or "").strip()
        lon = (row.get("Lon") or "").strip()

        # recurringVisit_id: stable per row, e.g. H015_r1, H015_r2
        client_prefix = _slug(kundnr) or "unknown"
        recurring_visit_id = f"{client_prefix}_r{i + 1}"

        # recurringVisit_clientName: derive from Kundnr (parser can replace with real name)
        recurring_client_name = kundnr or ""

        # frequency_type from Återkommande
        frequency_type = _recurrence_type(atterkommande)

        # Time windows from Starttid, Före, Efter, Längd (all in minutes)
        start_m = _time_to_minutes(starttid)
        min_start_m = start_m - fore
        max_start_m = start_m + efter
        max_end_m = start_m + efter + langd
        minStartTime = _minutes_to_hhmm(min_start_m)
        maxStartTime = _minutes_to_hhmm(max_start_m)
        maxEndTime = _minutes_to_hhmm(max_end_m)

        # Empty until expansion
        original_visit_id = ""
        date = ""

        # Optional service area coords (use client Lat/Lon)
        service_area_lat = lat if lat and lat.replace(".", "").replace("-", "").isdigit() else ""
        service_area_lon = lon if lon and lon.replace(".", "").replace("-", "").isdigit() else ""

        row["recurringVisit_id"] = recurring_visit_id
        row["recurringVisit_clientName"] = recurring_client_name
        row["frequency_type"] = frequency_type
        row["minStartTime"] = minStartTime
        row["maxStartTime"] = maxStartTime
        row["maxEndTime"] = maxEndTime
        row["original_visit_id"] = original_visit_id
        row["date"] = date
        row["serviceArea_lat"] = service_area_lat
        row["serviceArea_lon"] = service_area_lon

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows with {len(new_columns)} new columns to {output_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
