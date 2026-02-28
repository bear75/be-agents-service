#!/usr/bin/env python3
"""
Build a 2-week expanded CSV that keeps ALL visits and optionally adds extra
placeholder shifts for dates with unassigned demand.

Does NOT remove any visit rows. Use this CSV with the pipeline as usual; to get
trimmed employees/shifts (39 vehicles, 897 shifts), pass --trimmed-output to
csv_to_timefold_fsr.py so only allowed (vehicle, date) shifts are generated.

Usage:
  python build_expanded_2w_trimmed.py \\
    --expanded expanded/huddinge_2wk_expanded_20260224_043456.csv \\
    --unassigned-input solve/24feb/...-input.json \\
    --unassigned-output solve/24feb/...-output.json \\
    --out expanded/huddinge_2wk_expanded_2w_with_placeholders.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Reuse unassigned analysis
if __name__ == "__main__" and __package__ is None:
    _SCRIPTS = Path(__file__).resolve().parent
    if str(_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(_SCRIPTS))

from analyze_unassigned import run_analysis as run_unassigned_analysis  # noqa: E402

DEPOT_LAT = "59.2368721"
DEPOT_LON = "17.9942601"
OCCURRENCE_BY_WEEKDAY = {
    0: "Varje vecka, mån",
    1: "Varje vecka, tis",
    2: "Varje vecka, ons",
    3: "Varje vecka, tor",
    4: "Varje vecka, fre",
    5: "Varje vecka, lör",
    6: "Varje vecka, sön",
}


def _dates_with_unassigned(
    input_data: dict, output_data: dict, supply_only: bool = False
) -> list[str]:
    """Return sorted list of dates that have unassigned (supply, or any if not supply_only)."""
    mi = input_data.get("modelInput") or input_data
    mo = output_data.get("modelOutput") or output_data
    _report, rows = run_unassigned_analysis(mi, mo)
    by_date: set[str] = set()
    for row in rows:
        if row.get("issue") == "supply" or not supply_only:
            by_date.add(row["date"])
    return sorted(by_date)


def _make_placeholder_row(
    shift_name: str,
    date_iso: str,
    shift_type: str,
    fieldnames: list[str],
) -> dict[str, str]:
    """One placeholder CSV row so generate_employees creates a shift for that date."""
    dt = datetime.strptime(date_iso, "%Y-%m-%d")
    weekday = dt.weekday()
    occ = OCCURRENCE_BY_WEEKDAY.get(weekday, "Varje vecka, mån")
    is_weekend = weekday >= 5
    if shift_type == "day":
        shift_start, shift_end = "07:00", "14:30" if is_weekend else "15:00"
        break_dur, break_min, break_max = "30", "10:00", "14:00"
    else:
        shift_start, shift_end = "16:00", "22:00"
        break_dur, break_min, break_max = "", "", ""
    row: dict[str, str] = {k: "" for k in fieldnames}
    row["external_slinga_shiftName"] = shift_name
    row["date"] = date_iso
    row["shift_type"] = shift_type
    row["shift_start"] = shift_start
    row["shift_end"] = shift_end
    row["recurring_external"] = occ
    row["serviceArea_lat"] = DEPOT_LAT
    row["serviceArea_lon"] = DEPOT_LON
    row["shift_break_duration"] = break_dur
    row["shift_break_minStart"] = break_min
    row["shift_break_maxEnd"] = break_max
    row["recurringVisit_id"] = "placeholder"
    row["frequency"] = "daily"
    row["frequency_type"] = "daily"
    row["week"] = "0"
    return row


def build_expanded_csv_with_placeholders(
    expanded_path: Path,
    unassigned_input_path: Path | None,
    unassigned_output_path: Path | None,
    out_path: Path,
    delimiter: str = ",",
    add_placeholder_for_unassigned: bool = True,
    supply_only: bool = False,
) -> int:
    """
    Copy expanded CSV (all visit rows unchanged), then append placeholder rows
    for dates with unassigned demand. Visit count is preserved (e.g. 3,622).
    """
    with open(expanded_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    # Keep all rows (all visits)
    result: list[dict[str, str]] = [dict(r) for r in rows]

    dates_to_add: list[str] = []
    if add_placeholder_for_unassigned and unassigned_input_path and unassigned_output_path:
        if unassigned_input_path.exists() and unassigned_output_path.exists():
            with open(unassigned_input_path, encoding="utf-8") as f:
                inp = json.load(f)
            with open(unassigned_output_path, encoding="utf-8") as f:
                out = json.load(f)
            dates_to_add = _dates_with_unassigned(inp, out, supply_only=supply_only)

    for date_iso in dates_to_add:
        for shift_name, shift_type in [
            ("Placeholder_Supply_Day", "day"),
            ("Placeholder_Supply_Evening", "evening"),
        ]:
            result.append(
                _make_placeholder_row(shift_name, date_iso, shift_type, fieldnames)
            )

    # Re-number original_visit_id
    for i, row in enumerate(result):
        row["original_visit_id"] = str(i + 1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        w.writeheader()
        w.writerows(result)

    return len(result)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Expanded CSV with all visits preserved + optional placeholder rows for unassigned dates.",
    )
    ap.add_argument("--expanded", type=Path, required=True, help="Current 2w expanded CSV (all visits).")
    ap.add_argument(
        "--unassigned-input",
        type=Path,
        default=None,
        help="Pre-trim solve input JSON (for unassigned analysis).",
    )
    ap.add_argument(
        "--unassigned-output",
        type=Path,
        default=None,
        help="Pre-trim solve output JSON (for unassigned analysis).",
    )
    ap.add_argument("--out", type=Path, required=True, help="Output expanded CSV path.")
    ap.add_argument(
        "--delimiter",
        default=",",
        help="Delimiter for expanded CSV (default: ,).",
    )
    ap.add_argument(
        "--no-extra-shifts",
        action="store_true",
        help="Do not add placeholder shifts for unassigned dates.",
    )
    ap.add_argument(
        "--supply-only",
        action="store_true",
        help="Add placeholder shifts only for dates with supply issues (default: any unassigned date).",
    )
    args = ap.parse_args()

    if not args.expanded.exists():
        print(f"Error: expanded CSV not found: {args.expanded}", file=sys.stderr)
        return 1

    n = build_expanded_csv_with_placeholders(
        args.expanded,
        args.unassigned_input,
        args.unassigned_output,
        args.out,
        delimiter=args.delimiter,
        add_placeholder_for_unassigned=not args.no_extra_shifts,
        supply_only=args.supply_only,
    )
    print(f"Wrote {args.out} ({n} rows, all visits preserved)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
