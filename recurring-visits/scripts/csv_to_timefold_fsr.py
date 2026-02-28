#!/usr/bin/env python3
"""
Convert expanded Huddinge CSV to Timefold FSR JSON format.

Reads expanded CSV (from expand_recurring_visits.py), generates vehicles from
generate_employees.py, and produces full Timefold modelInput JSON.

Usage:
  python csv_to_timefold_fsr.py expanded.csv -o input.json --weeks 2
"""

import argparse
import csv
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from generate_employees import generate_vehicles

# Ensure scripts dir in path
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


def _vehicle_shift_dates_from_trimmed_output(
    trimmed_output_path: Path, exclude_placeholders: bool = True
) -> set[tuple[str, str, str]]:
    """Load trimmed from-patch output. Return set of (vehicle_id, date_iso, shift_kind) for shifts with visits.
    shift_kind is 'day' or 'evening' (inferred from shift end hour <= 15.5 -> day).
    """
    import json
    with open(trimmed_output_path, encoding="utf-8") as f:
        data = json.load(f)
    out = data.get("modelOutput") or data.get("model_output") or {}
    result: set[tuple[str, str, str]] = set()
    for v in out.get("vehicles", []):
        vid = v.get("id", "")
        if not vid:
            continue
        if exclude_placeholders and (
            vid.startswith("Placeholder_Supply_Day") or vid.startswith("Placeholder_Supply_Evening")
        ):
            continue
        for s in v.get("shifts", []):
            has_visit = any(
                isinstance(item, dict) and item.get("kind") == "VISIT"
                for item in s.get("itinerary", [])
            )
            if has_visit:
                st = s.get("startTime")
                if st:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(st.replace("Z", "+00:00"))
                        date_iso = dt.date().isoformat()
                        # Infer day vs evening from start time (evening typically 16:00+)
                        h = dt.hour + dt.minute / 60.0
                        kind = "evening" if h >= 15.5 else "day"
                        result.add((vid, date_iso, kind))
                    except Exception:
                        pass
    return result

DEFAULT_OFFICE = [59.2368721, 17.9942601]
TIMEZONE_SUFFIX = "+01:00"


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


def _minutes_to_iso_duration(minutes: int) -> str:
    if minutes < 60:
        return f"PT{minutes}M"
    h, m = minutes // 60, minutes % 60
    return f"PT{h}H{m}M" if m else f"PT{h}H"


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
    delimiter: str = ",",
    geocode_rate_sec: float = 1.0,
) -> None:
    """
    For rows that have an address but missing client_lat/client_lon, geocode and fill.
    Mutates rows in place so addresses get coordinates instead of being skipped.
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


def build_visit(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Build Timefold visit object from expanded CSV row.
    Rows with no coordinates and no geocode-able address are skipped. Call
    _fill_missing_coordinates() on the row list first so addresses get coordinates.
    """
    occ_id = str(row.get("original_visit_id", "")).strip()
    if not occ_id:
        return None

    lat = _parse_float(row.get("client_lat"), 0)
    lon = _parse_float(row.get("client_lon"), 0)
    if lat == 0 and lon == 0:
        return None

    duration = _parse_int(row.get("duration", 0))
    min_start = str(row.get("minStartTime", "")).strip()
    max_end = str(row.get("maxEndTime", "")).strip()
    if not min_start or not max_end:
        return None

    name = str(row.get("recurringVisit_clientName", occ_id)).strip()
    inset = str(row.get("inset_type", "")).strip()
    if inset:
        name = f"{name} - {inset[:50]}"

    # No priority: let Timefold use default (6). Priority 1 would outcompete groups.
    visit: Dict[str, Any] = {
        "id": occ_id,
        "name": name[:100],
        "location": [lat, lon],
        "timeWindows": [
            {
                "minStartTime": min_start,
                "maxEndTime": max_end,
            }
        ],
        "serviceDuration": _minutes_to_iso_duration(duration),
        "pinningRequested": False,
    }

    # Add maxStartTime if present (for daily visits)
    max_start = str(row.get("maxStartTime", "")).strip()
    if max_start:
        visit["timeWindows"][0]["maxStartTime"] = max_start

    return visit


def build_visit_groups(
    visits: List[Dict[str, Any]],
    rows: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Group visits by (visitGroup_id, week, date) for double staffing.

    CRITICAL: Timefold multi-vehicle visits require overlapping time windows.
    Visits on different days (e.g. Mon vs Tue) cannot overlap and are impossible to schedule.
    Therefore we group by (visitGroup_id, week, date) so each group contains only visits
    on the SAME day with overlapping windows.

    Returns (standalone_visits, visit_groups).
    """
    visit_by_id = {v["id"]: v for v in visits}
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for row in rows:
        vgid = str(row.get("visitGroup_id", "")).strip()
        occ_id = str(row.get("original_visit_id", "")).strip()
        week = str(row.get("week", "0")).strip()
        date = str(row.get("date", "")).strip()  # e.g. 2026-02-16
        if not vgid or not occ_id:
            continue
        v = visit_by_id.get(occ_id)
        if not v:
            continue
        # Group by (visitGroup_id, week, date) so visits on same day have overlapping windows
        group_key = f"{vgid}_w{week}_{date}" if date else f"{vgid}_w{week}"
        if v not in groups[group_key]:
            groups[group_key].append(v)

    standalone: List[Dict[str, Any]] = []
    visit_groups: List[Dict[str, Any]] = []
    used_in_group: set[str] = set()

    for group_key, group_visits in groups.items():
        if len(group_visits) >= 2:
            visit_groups.append({
                "id": f"visitGroup_{group_key}",
                "visits": group_visits,
            })
            used_in_group.update(v["id"] for v in group_visits)
        else:
            standalone.extend(group_visits)
            used_in_group.update(v["id"] for v in group_visits)  # avoid duplicate in final loop

    for v in visits:
        if v["id"] not in used_in_group:
            standalone.append(v)

    return (standalone, visit_groups)


def generate_timefold_json(
    expanded_csv_path: Path,
    output_json_path: Path,
    planning_weeks: int = 2,
    planning_start_date: str = "2026-02-16",
    run_name: str = "Huddinge 2-Week Schedule",
    delimiter: str = ",",
    source_csv_path: Path | None = None,
    source_format: str = "huddinge",
    trimmed_output_path: Path | None = None,
) -> Dict[str, Any]:
    """
    Generate full Timefold FSR JSON from expanded CSV.

    Uses source_csv_path for employee/shift pool (39 employees, ~78 shifts). If not
    provided, infers from expanded path (../source/Huddinge_recurring_v2.csv).

    If trimmed_output_path is provided (from-patch trimmed output JSON), only
    vehicles and shifts that appear there are created (no empty employees/shifts).
    All visits from the expanded CSV are still included (e.g. 3,622).

    Returns { config: { run: { name } }, modelInput }. Other config set in TF dashboard.
    """
    with open(expanded_csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)

    # Geocode rows that have address but missing coordinates so they get coordinates instead of being skipped.
    _fill_missing_coordinates(rows, delimiter=delimiter)

    visits_raw: List[Dict[str, Any]] = []
    for row in rows:
        v = build_visit(row)
        if v:
            visits_raw.append(v)

    standalone, visit_groups = build_visit_groups(visits_raw, rows)

    if source_csv_path is None:
        source_csv_path = expanded_csv_path.parent.parent / "source" / "Huddinge_recurring_v2.csv"
    if not source_csv_path.exists():
        source_csv_path = expanded_csv_path.parent.parent / "source" / "Huddinge_recurring.csv"

    # Source CSV is typically semicolon-delimited (Huddinge export)
    source_delimiter = ";"

    trimmed_shift_dates: set[tuple[str, str]] | set[tuple[str, str, str]] | None = None
    if trimmed_output_path and trimmed_output_path.exists():
        trimmed_shift_dates = _vehicle_shift_dates_from_trimmed_output(trimmed_output_path)

    vehicles = generate_vehicles(
        source_csv_path,
        planning_start_date=planning_start_date,
        planning_weeks=planning_weeks,
        delimiter=source_delimiter,
        source_format=source_format,
        trimmed_shift_dates=trimmed_shift_dates,
    )

    model_input: Dict[str, Any] = {
        "vehicles": vehicles,
        "visits": standalone,
    }
    if visit_groups:
        model_input["visitGroups"] = visit_groups

    payload: Dict[str, Any] = {
        "config": {"run": {"name": run_name}},
        "modelInput": model_input,
    }
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert expanded CSV to Timefold FSR JSON")
    parser.add_argument("input", type=Path, help="Expanded CSV file")
    parser.add_argument("-o", "--output", type=Path, help="Output JSON (default: input_dir/input.json)")
    parser.add_argument("--weeks", type=int, default=2, choices=[2, 4])
    parser.add_argument("--start-date", default="2026-02-16")
    parser.add_argument("--name", default="Huddinge 2-Week Schedule")
    parser.add_argument("--delimiter", default=",", help="CSV delimiter (default: , for dashboard upload)")
    parser.add_argument("--source", type=Path, default=None, help="Source CSV for vehicles (default: inferred from expanded path)")
    parser.add_argument("--format", dest="source_format", choices=["huddinge", "nova"], default="huddinge", help="Source format (default: huddinge)")
    parser.add_argument("--trimmed-output", type=Path, default=None, help="From-patch trimmed output JSON: only create vehicles/shifts that appear here (keeps all visits)")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input not found: {args.input}", file=sys.stderr)
        return 1

    out = args.output
    if not out:
        out = args.input.parent / "input.json"

    try:
        payload = generate_timefold_json(
            args.input,
            out,
            planning_weeks=args.weeks,
            planning_start_date=args.start_date,
            run_name=args.name,
            delimiter=args.delimiter,
            source_csv_path=args.source,
            source_format=args.source_format,
            trimmed_output_path=args.trimmed_output,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

    mi = payload["modelInput"]
    n_visits = len(mi["visits"])
    n_groups = len(mi.get("visitGroups", []))
    n_group_visits = sum(len(g["visits"]) for g in mi.get("visitGroups", []))
    n_vehicles = len(mi["vehicles"])
    n_shifts = sum(len(v["shifts"]) for v in mi["vehicles"])

    print(f"Generated: {n_visits} standalone visits + {n_group_visits} in {n_groups} visit groups")
    print(f"           {n_vehicles} vehicles, {n_shifts} shifts")
    print(f"Wrote: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
