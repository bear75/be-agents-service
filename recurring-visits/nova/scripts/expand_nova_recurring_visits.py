#!/usr/bin/env python3
"""
Expand Nova recurring visit patterns to Huddinge-compatible expanded CSV.

Maps Nova columns to Huddinge format, then reuses the Huddinge expand logic.
Output is compatible with csv_to_timefold_fsr.py and generate_vehicles (Nova format).

Nova expanded output uses comma delimiter by default (dashboard upload compatible). Column mapping:
  Nova                    -> Huddinge (internal)
  visitid                 -> visit_id (for ordering)
  movablevisitid          -> recurringVisit_id
  Dubbelid                -> visitGroup_id
  Slinga                  -> external_slinga_shiftName
  weekday                 -> recurring_external (e.g. "Varje vecka, mån")
  originalstarttime       -> startTime
  Längd                   -> duration
  Min före                -> flex_beforeStart
  Min efter               -> flex_afterStart
  Kundnr                  -> client_externalId
  Gata                    -> client_addressStreet
  Postnr                  -> client_addressPostalCdode
  Ort                     -> client_addressCity
  movable_id_str          -> recurringVisit_clientName
  Insatser                -> inset_type
  Vilande besök           -> visit_note (inactive if set)
  shift_type, shift_start, shift_end, slinga_break_* -> same
  office_lat/lon          -> serviceArea_lat/lon

Usage:
  python expand_nova_recurring_visits.py input.csv -o expanded.csv --weeks 2
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Any, Dict, List

_SCRIPTS_DIR = Path(__file__).resolve().parent
_HUDDINGE_SCRIPTS = _SCRIPTS_DIR.parent.parent / "huddinge-package" / "scripts"
if str(_HUDDINGE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_HUDDINGE_SCRIPTS))

from expand_recurring_visits import expand_visits


# Nova -> Huddinge column mapping
NOVA_TO_HUDDINGE: Dict[str, str] = {
    "visitid": "visit_id",
    "movablevisitid": "recurringVisit_id",
    "Dubbelid": "visitGroup_id",
    "Slinga": "external_slinga_shiftName",
    "weekday": "recurring_external",  # mån, tis, etc - expand expects "Varje vecka, X"
    "originalstarttime": "startTime",
    "Längd": "duration",
    "Min före": "flex_beforeStart",
    "Min efter": "flex_afterStart",
    "Kundnr": "client_externalId",
    "Gata": "client_addressStreet",
    "Postnr": "client_addressPostalCdode",
    "Ort": "client_addressCity",
    "movable_id_str": "recurringVisit_clientName",
    "Insatser": "inset_type",
    "Vilande besök": "visit_note",
    "office_lat": "serviceArea_lat",
    "office_lon": "serviceArea_lon",
}

# Columns that exist in both (same name)
SHARED_COLS = {"shift_type", "shift_start", "shift_end", "frequency", "client_lat", "client_lon"}

# Nova break columns
NOVA_BREAK_MAP = {
    "slinga_break_duration": "shift_break_duration",
    "slinga_break_min_start": "shift_break_minStart",
    "slinga_break_max_end": "shift_break_maxEnd",
}


def _format_weekday_as_recurring(weekday: str) -> str:
    """Nova weekday 'mån' -> 'Varje vecka, mån' for expand parser."""
    wd = str(weekday).strip().lower()
    if not wd or wd == "unknown":
        return ""
    return f"Varje vecka, {wd}"


def _map_nova_row_to_huddinge(row: Dict[str, Any]) -> Dict[str, Any]:
    """Map Nova CSV row to Huddinge-format row."""
    out: Dict[str, Any] = {}
    for nova_col, huddinge_col in NOVA_TO_HUDDINGE.items():
        val = row.get(nova_col, "")
        if nova_col == "weekday" and val:
            val = _format_weekday_as_recurring(val)
        out[huddinge_col] = val
    for col in SHARED_COLS:
        if col in row:
            out[col] = row[col]
    for nova_col, huddinge_col in NOVA_BREAK_MAP.items():
        if nova_col in row:
            out[huddinge_col] = row[nova_col]
    return out


def _is_inactive_nova(row: Dict[str, Any]) -> bool:
    """Nova: Vilande besök or shift_type inactive."""
    vilande = str(row.get("Vilande besök", "") or "").strip()
    if vilande:
        return True
    st = str(row.get("shift_type", "")).strip().lower()
    return st == "inactive"


def normalize_nova_to_huddinge(
    nova_path: Path,
    normalized_path: Path,
    delimiter: str = ",",
) -> int:
    """
    Convert Nova CSV to Huddinge-format source CSV.
    Returns number of rows written (excluding inactive).
    """
    with open(nova_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        nova_rows = list(reader)

    huddinge_rows: List[Dict[str, Any]] = []
    for row in nova_rows:
        if _is_inactive_nova(row):
            continue
        h = _map_nova_row_to_huddinge(row)
        # Ensure visit_id for ordering
        if not h.get("visit_id"):
            h["visit_id"] = row.get("visitid", len(huddinge_rows) + 1)
        huddinge_rows.append(h)

    if not huddinge_rows:
        return 0

    fieldnames = list(huddinge_rows[0].keys())
    with open(normalized_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(huddinge_rows)

    return len(huddinge_rows)


def expand_nova_visits(
    nova_csv_path: Path,
    output_path: Path,
    planning_weeks: int = 2,
    planning_start_date: str = "2026-02-16",
    delimiter: str = ",",
) -> int:
    """
    Expand Nova recurring CSV to planning window CSV (Huddinge expanded format).

    Normalizes Nova -> Huddinge source, then runs Huddinge expand.
    Returns number of expanded rows.
    """
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as tf:
        norm_path = Path(tf.name)
    try:
        n_norm = normalize_nova_to_huddinge(nova_csv_path, norm_path, delimiter)
        if n_norm == 0:
            print("Error: No active visits after normalization", file=sys.stderr)
            return 0
        return expand_visits(
            norm_path,
            output_path,
            planning_weeks=planning_weeks,
            planning_start_date=planning_start_date,
            delimiter=delimiter,
            write_delimiter=",",
        )
    finally:
        norm_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Expand Nova recurring visits to planning window")
    parser.add_argument("input", type=Path, help="Nova source CSV")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output expanded CSV")
    parser.add_argument("--weeks", type=int, default=2, choices=[2, 4])
    parser.add_argument("--start-date", default="2026-02-16")
    parser.add_argument("--delimiter", default=",", help="CSV delimiter (default: , for dashboard upload)")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input not found: {args.input}", file=sys.stderr)
        return 1

    try:
        expand_nova_visits(
            args.input,
            args.output,
            planning_weeks=args.weeks,
            planning_start_date=args.start_date,
            delimiter=args.delimiter,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
