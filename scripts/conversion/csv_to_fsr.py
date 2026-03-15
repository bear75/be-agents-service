#!/usr/bin/env python3
"""
Convert Attendo Huddinge 4mars CSV to Timefold FSR modelInput JSON.

Reads ATTENDO_DATABEHOV_PER_KUND_OCH_BESOK - data.csv, expands recurring rows
to visit occurrences (planning window 2 March–15 March 2026), geocodes addresses,
builds visits with time windows (Morgon/Lunch/Kväll), visitDependencies (same-day short delay e.g. frukost→lunch 3.5h; spread same insats e.g. 48h dusch),
visitGroups (Dubbel), and vehicles from Slinga with shifts and requiredBreaks.

UPDATED (2026-03-13): Fixed time window calculation logic (aligned with dashboard seed/import):
- "Exakt dag/tid" (När på dagen contains "exakt"): exact time, minimal 1-min flex
- Empty Före/Efter (cells blank): full slot from När på dagen + Skift
- Explicit 0,0 Före/Efter: exact time (same as Exakt), minimal 1-min flex
- Non-zero Före/Efter: Starttid ± före/efter
- Same-day visits now sequence correctly (PT0M dependencies)

Usage:
  python attendo_4mars_to_fsr.py input.csv -o input.json
  python attendo_4mars_to_fsr.py input.csv -o input.json --start-date 2026-03-02 --no-geocode
"""

import argparse
import csv
import json
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# Ensure scripts dir in path
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# Planning window defaults (used when --start-date / --end-date not given)
# Also exported for analyze_4mars_csv_to_json and map_visits_time_windows (must match input JSON window)
PLANNING_START_DATE = "2026-03-02"
PLANNING_END_DATE = "2026-03-15"
TIMEZONE_SUFFIX = "+01:00"

RECURRENCE_DAYS = {"daily": 7, "weekly": 14, "biweekly": 14, "3weekly": 21, "4weekly": 28}
DEFAULT_OFFICE = [59.2368721, 17.9942601]

# När på dagen (visit slot) -> (slot_start, slot_end) as "HH:MM"
# v2 Lathund: Morgon 07:00-10:00, Förmiddag 10:00-11:00, Lunch 11:00-13:30, Eftermiddag 13:30-15:00,
#             Middag 16:00-19:00, Kväll 19:00-22:00. Flex 09-10:30 / 13:30-14:30 = Förmiddag/Eftermiddag.
# Tomt/annat = heldag 07-22.
SLOT_MORGON = ("07:00", "10:00")
SLOT_FORMIDDAG = ("10:00", "11:00")
SLOT_LUNCH = ("11:00", "13:30")
SLOT_EFTERMIDDAG = ("13:30", "15:00")
SLOT_MIDDAG = ("16:00", "19:00")
SLOT_KVALL = ("19:00", "22:00")
SLOT_HELDAG = ("07:00", "22:00")  # Fritt tidsfönster (När på dagen tom eller annat)

# Skift (vehicle shift): Helg 07-14:30 Sat-Sun, Dag 07-15 Mon-Fri, Kväll 16-22 all 7 days
# Dag/Helg have requiredBreak 10:00-14:00, 30 min at office
SHIFT_DAG = ("07:00", "15:00")
SHIFT_HELG = ("07:00", "14:30")
SHIFT_KVALL = ("16:00", "22:00")

# Swedish weekday names -> Python weekday (Mon=0, Sun=6)
OCCURRENCE_WEEKDAY: Dict[str, int] = {
    "mån": 0, "månag": 0, "måndag": 0,
    "tis": 1, "tisdag": 1,
    "ons": 2, "onsdag": 2,
    "tor": 3, "torsdag": 3,
    "fre": 4, "fredag": 4,
    "lör": 5, "lördag": 5,
    "sön": 6, "söndag": 6,
}


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


def _slug(s: str) -> str:
    """Create Timefold-safe ID from Slinga or name."""
    slug = re.sub(r"[^\w\s-]", "", s.strip())
    slug = re.sub(r"[\s_]+", "_", slug).strip("_")
    return slug or "unknown"


def _to_iso_datetime(date: datetime, time_str: str) -> str:
    """Combine date and time (HH:MM) into ISO 8601 with timezone."""
    parts = str(time_str).strip().split(":")
    h = int(parts[0]) if parts else 0
    m = int(parts[1]) if len(parts) > 1 else 0
    dt = date.replace(hour=h, minute=m, second=0, microsecond=0)
    return dt.isoformat() + TIMEZONE_SUFFIX


def _parse_time_minutes(time_str: str) -> int:
    """Parse HH:MM or HH:MM:SS to minutes since midnight."""
    if not time_str or not isinstance(time_str, str):
        return 0
    try:
        parts = time_str.strip().split(":")
        h, m = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
        return h * 60 + m
    except (ValueError, IndexError):
        return 0


def _longest_recurrence_days(rows: List[Dict[str, Any]]) -> int:
    """Scan CSV rows and return the longest recurrence period in days."""
    longest = 14  # default 2 weeks
    for row in rows:
        rt = _recurrence_type(str(row.get("Återkommande", "") or ""))
        longest = max(longest, RECURRENCE_DAYS.get(rt, 14))
    return longest


def _auto_planning_window() -> Tuple[str, str]:
    """
    Auto-compute planning window: start = Monday of current week,
    end determined after CSV is read (longest recurrence).
    Returns (start_date_str, None placeholder).
    """
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    return monday.strftime("%Y-%m-%d")


# ---- Address and geocoding ----


# Same split-street normalization as full-csv/convert_original_to_new.py so address_key matches.
_STREET_NAME_FIXES: Dict[str, str] = {
    "DAL VÄGEN": "Dalvägen",
    "DAMMTORPS VÄGEN": "Dammtorpsvägen",
    "DIAGNOS VÄGEN": "Diagnosvägen",
    "FRIMANS VÄG": "Frimans väg",
    "KVARNBERGS PLAN": "Kvarnbergsplan",
    "LAGMANS VÄGEN": "Lagmansvägen",
    "SANDSTENS VÄGEN": "Sandstensvägen",
    "SJÖDALS VÄGEN": "Sjödalsvägen",
    "SMÅBRUKETS BACKE": "Småbruksbacken",
    "SÅGSTU VÄGEN": "Sågstuvägen",
    "Tekniker vägen": "Teknikervägen",
    "URBERGS VÄGEN": "Urbergsvägen",
    "VISÄTTRA VÄGEN": "Visättravägen",
    "ÄNGSNÄS VÄGEN": "Ängsnäsvägen",
    "UVVÄGEN": "Uvvägen",
}


def _normalize_gata(gata: str) -> str:
    """
    Normalize street field before geocoding: trim all whitespace, remove apartment/suite
    noise (LGH, VÅN, våning, etc.), collapse space before street suffixes (gatan, vägen),
    and apply split-street fixes. No fallback coordinates — if geocoding fails, fix CSV.
    """
    if not gata:
        return ""
    s = str(gata).strip()
    # Remove apartment/suite suffixes (order matters: longer patterns first)
    # LGH / Lgh: "LGH 1002", "LGH nr 1002", "LGH1002"
    s = re.sub(r",?\s*LGH\s*nr?\s*\d+.*$", "", s, flags=re.IGNORECASE).strip()
    s = re.sub(r",?\s*LGH\s*\d+.*$", "", s, flags=re.IGNORECASE).strip()
    s = re.sub(r",?\s*LGH\s+\S+.*$", "", s, flags=re.IGNORECASE).strip()
    # VÅN / våning: "VÅN 3", "våning 2", "Vån 1"
    s = re.sub(r",?\s*VÅN\s*\d+.*$", "", s, flags=re.IGNORECASE).strip()
    s = re.sub(r",?\s*våning\s*\d+.*$", "", s, flags=re.IGNORECASE).strip()
    s = re.sub(r",?\s*Vån\s*\d+.*$", "", s, flags=re.IGNORECASE).strip()
    # Lägenhet, trappor, tr (abbrev. for trappor)
    s = re.sub(r",?\s*Lägenhet\s*\d+.*$", "", s, flags=re.IGNORECASE).strip()
    s = re.sub(r",?\s*trappor\s*[A-Za-z0-9]*.*$", "", s, flags=re.IGNORECASE).strip()
    s = re.sub(r",?\s*tr\s*\d+.*$", "", s, flags=re.IGNORECASE).strip()
    # Generic "LGH <anything>" or "våning <anything>" remainder
    s = re.sub(r"\s+LGH\s+\S+.*$", "", s, flags=re.IGNORECASE).strip()
    s = re.sub(r"\s+(våning|Våning|VÅN|Vån)\s+\S+.*$", "", s, flags=re.IGNORECASE).strip()
    s = re.sub(r"\s+Lägenhet\s+\S+.*$", "", s, flags=re.IGNORECASE).strip()
    s = re.sub(r"\s+trappor\s+\S+.*$", "", s, flags=re.IGNORECASE).strip()
    s = re.sub(r"\s+tr\s+\S+.*$", "", s, flags=re.IGNORECASE).strip()
    # Trailing comma, collapse all whitespace to single space, trim
    s = re.sub(r",\s*$", "", s).strip()
    s = re.sub(r"\s+", " ", s).strip()
    # Normalize split street names first (e.g. SMÅBRUKETS BACKE -> Småbruksbacken) so suffix merge doesn't break them
    for wrong, correct in _STREET_NAME_FIXES.items():
        if s.upper().startswith(wrong.upper()):
            rest = s[len(wrong) :].strip()
            s = (correct + " " + rest).strip()
            break
    # Remove space before Swedish street-type suffixes (e.g. "bergs gatan" -> "bergsgatan", "X vägen" -> "Xvägen")
    for suffix in ("gatan", "vägen", "väg", "gränd", "stigen", "backen", "backe", "plan", "torget"):
        s = re.sub(r"\s+" + suffix + r"\b", suffix, s, flags=re.IGNORECASE)
    return s.strip()


def _address_string_4mars(row: Dict[str, Any]) -> str:
    """Build geocode-able address from Gata, Postnr, Ort."""
    gata = _normalize_gata(str(row.get("Gata", "") or ""))
    postnr = re.sub(r"\s+", "", str(row.get("Postnr", "") or "").strip())
    ort = str(row.get("Ort", "") or "").strip()
    if not gata and not postnr and not ort:
        return ""
    if gata:
        return f"{gata}, {postnr} {ort}, Sweden".strip(" ,")
    return f"{postnr} {ort}, Sweden".strip(" ,")


# No built-in fallback coordinates. If geocoding fails, fix Gata in CSV (remove LGH, VÅN, etc.)
# and re-run build_address_coordinates.py until all addresses resolve via Nominatim or
# --address-coordinates file.


def _normalize_address_for_fallback_lookup(addr: str) -> str:
    """Lowercase and collapse spaces for fallback table lookup."""
    if not addr:
        return ""
    return re.sub(r"\s+", " ", str(addr).strip().lower())


def _geocode_nominatim(
    address: str,
    cache: Dict[str, Tuple[Optional[float], Optional[float]]],
    external_coordinates: Optional[Dict[str, Tuple[float, float]]] = None,
) -> Tuple[Optional[float], Optional[float]]:
    """Geocode one address: cache, then Nominatim, then --address-coordinates file only.
    No built-in fallback. If resolution fails, fix Gata in CSV (remove LGH, VÅN, etc.) and re-run.
    """
    if not address or not address.strip():
        return (None, None)
    key = address.strip()
    if key in cache:
        return cache[key]
    lookup = _normalize_address_for_fallback_lookup(key)
    lookup_no_country = lookup.replace(", sweden", "").strip() if lookup else ""
    # External address→coordinates file (from build_address_coordinates.py) checked first
    if external_coordinates:
        if lookup in external_coordinates:
            coords = external_coordinates[lookup]
            cache[key] = coords
            return coords
        if lookup_no_country in external_coordinates:
            coords = external_coordinates[lookup_no_country]
            cache[key] = coords
            return coords
    try:
        url = "https://nominatim.openstreetmap.org/search?" + urlencode(
            {"q": key, "format": "json", "limit": 1}
        )
        req = Request(url, headers={"User-Agent": "AppCaireRecurringVisits/1.0"})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        if data:
            lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
            cache[key] = (lat, lon)
            return (lat, lon)
    except Exception as e:
        print(f"WARNING: geocode failed for '{key}': {e}", file=sys.stderr)
    cache[key] = (None, None)
    return (None, None)


def _fill_coordinates_4mars(
    occurrences: List[Dict[str, Any]],
    geocode_rate_sec: float = 1.0,
    external_coordinates: Optional[Dict[str, Tuple[float, float]]] = None,
) -> None:
    """Geocode occurrences that have address but no lat/lon. Mutates in place.
    Uses external_coordinates (--address-coordinates file) then Nominatim. No fallback; failures must be fixed in CSV.
    """
    address_to_indices: Dict[str, List[int]] = defaultdict(list)
    for i, occ in enumerate(occurrences):
        lat = _parse_float(occ.get("lat"), 0)
        lon = _parse_float(occ.get("lon"), 0)
        if lat != 0 or lon != 0:
            continue
        addr = occ.get("address_key", "")
        if addr:
            address_to_indices[addr].append(i)

    if not address_to_indices:
        return

    n_unique = len(address_to_indices)
    print(f"Geocoding {n_unique} unique address(es)...", file=sys.stderr)
    cache: Dict[str, Tuple[Optional[float], Optional[float]]] = {}
    for addr, indices in address_to_indices.items():
        lat, lon = _geocode_nominatim(addr, cache, external_coordinates=external_coordinates)
        if lat is not None and lon is not None:
            for i in indices:
                occurrences[i]["lat"] = lat
                occurrences[i]["lon"] = lon
        time.sleep(geocode_rate_sec)


# ---- Återkommande parsing and expansion ----


def _parse_weekdays_from_atterkommande(atterkommande: str) -> Optional[List[int]]:
    """
    Parse Återkommande to list of weekdays (0-6).
    E.g. "Varje vecka, mån tis ons tor fre" -> [0,1,2,3,4]; "Varje vecka, lör sön" -> [5,6].
    Returns None for "Varje dag", "Varannan vecka", "Var 4:e vecka" (handled separately).
    """
    if not atterkommande:
        return None
    s = str(atterkommande).strip().lower()
    if "varje dag" in s or "varannan" in s or "4:e vecka" in s or "3:e vecka" in s:
        return None
    found: List[int] = []
    for key, wd in OCCURRENCE_WEEKDAY.items():
        if key in s and wd not in found:
            found.append(wd)
    return sorted(found) if found else None


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


def _should_pin_weekdays(weekdays: Optional[List[int]], recurrence: str) -> bool:
    """
    True only when the CSV specifies a complete weekday set: we create exactly one
    visit per matching date (pinned). False for partial sets (e.g. "mån tis tor") so
    the solver picks N days within the period with spread delays (e.g. 18h/36h/48h).
    Pin: all weekdays (mån–fre), both weekend (lör sön), all 7 (daily), or daily recurrence.
    Solver picks: "Varje vecka, mån tis tor", "Varje vecka, ons", "tis fre", etc.
    """
    if recurrence == "daily":
        return True  # daily => all days
    if not weekdays or len(weekdays) == 0:
        return False  # no specific days => solver picks (e.g. "Varje vecka" only)
    ws = set(weekdays)
    # Pin only complete sets: all weekdays, both weekend, or all 7
    if ws == {0, 1, 2, 3, 4}:
        return True   # mån–fre
    if ws == {5, 6}:
        return True   # lör sön
    if ws == {0, 1, 2, 3, 4, 5, 6}:
        return True   # all 7 = daily
    return False  # partial set (mån tis tor, ons, tis fre, ...) => flexible_day, solver picks


def _dates_in_window(
    start_date: datetime, end_date: datetime
) -> List[datetime]:
    """All dates from start_date through end_date (inclusive)."""
    dates: List[datetime] = []
    d = start_date.date()
    end = end_date.date()
    while d <= end:
        dates.append(datetime.combine(d, datetime.min.time()))
        d += timedelta(days=1)
    return dates


def _flexible_period_restrict_to_shift(
    period_start: datetime, period_end: datetime, schift: str
) -> Tuple[datetime, datetime]:
    """
    Restrict flexible_day period by skift so solver only places visit on allowed days.
    - Helg: Sat–Sun only (shift 07–14:30).
    - Dag: Mon–Fri only (shift 07–15).
    - Kväll (or other): no restriction; full period (any day). Visit time is still 16–19 (när på dagen).
    """
    s = (schift or "").strip().lower()
    if "helg" in s:
        allowed = [d for d in _dates_in_window(period_start, period_end)
                   if d.weekday() in (5, 6)]
        if allowed:
            return (allowed[0], allowed[-1])
    elif "dag" in s:
        allowed = [d for d in _dates_in_window(period_start, period_end)
                   if d.weekday() <= 4]
        if allowed:
            return (allowed[0], allowed[-1])
    return (period_start, period_end)


def _expand_row_to_occurrences(
    row: Dict[str, Any],
    row_index: int,
    start_date: datetime,
    end_date: datetime,
) -> List[Dict[str, Any]]:
    """
    Expand one CSV row to list of occurrence dicts (one per date in window).
    Each occurrence has: date, date_iso, kundnr, address_key, slinga, starttid, längd,
    när_på_dagen, schift, före, efter, dubbel, antal_tim_mellan, kritisk_insats, row_index,
    recurrence_type, weekdays (for weekly), lat, lon (filled later).
    """
    atterkommande = str(row.get("Återkommande", "") or "").strip()
    recurrence = _recurrence_type(atterkommande)
    weekdays = _parse_weekdays_from_atterkommande(atterkommande)

    gata = _normalize_gata(str(row.get("Gata", "") or ""))
    postnr = re.sub(r"\s+", "", str(row.get("Postnr", "") or "").strip())
    ort = str(row.get("Ort", "") or "").strip()
    address_key = f"{gata}, {postnr} {ort}, Sweden".strip(" ,") if (gata or postnr or ort) else ""

    # Use CSV Lat/Lon if present so every row has coordinates (no geocode needed for those)
    csv_lat = _parse_float(row.get("Lat") or row.get("Latitud"), 0)
    csv_lon = _parse_float(row.get("Lon") or row.get("Longitud"), 0)
    base_lat = csv_lat if (csv_lat != 0 or csv_lon != 0) else 0.0
    base_lon = csv_lon if (csv_lat != 0 or csv_lon != 0) else 0.0

    # Empty vs explicit 0: empty Före/Efter → full slot; explicit 0,0 → exact time (same as Exakt dag/tid)
    _fore_raw = str(row.get("Före", "") or "").strip()
    _efter_raw = str(row.get("Efter", "") or "").strip()
    fore_efter_empty = _fore_raw == "" and _efter_raw == ""

    base: Dict[str, Any] = {
        "kundnr": str(row.get("Kundnr", "") or "").strip(),
        "address_key": address_key,
        "slinga": str(row.get("Slinga", "") or "").strip(),
        "starttid": str(row.get("Starttid", "") or "08:00").strip(),
        "längd": _parse_int(row.get("Längd"), 0),
        "när_på_dagen": str(row.get("När på dagen", "") or "").strip(),
        "schift": str(row.get("Skift", "") or row.get("Schift", "") or "").strip(),
        "insatser": str(row.get("Insatser", "") or "").strip(),
        "före": _parse_int(row.get("Före"), 0),
        "efter": _parse_int(row.get("Efter"), 0),
        "före_efter_empty": fore_efter_empty,
        "dubbel": str(row.get("Dubbel", "") or "").strip(),
        "antal_tim_mellan": str(row.get("Antal tim mellan besöken", "") or "").strip(),
        "kritisk_insats": str(row.get("Kritisk insats Ja/nej", "") or "").strip().lower() == "ja",
        "row_index": row_index,
        "recurrence_type": recurrence,
        "weekdays": weekdays,  # for pinning: list of 0-6 or None
        "lat": base_lat,
        "lon": base_lon,
    }

    dates_in_window = _dates_in_window(start_date, end_date)
    occurrences: List[Dict[str, Any]] = []

    if recurrence == "daily":
        for d in dates_in_window:
            occ = {**base, "date": d, "date_iso": d.date().isoformat()}
            occurrences.append(occ)

    elif recurrence == "weekly" and weekdays:
        if _should_pin_weekdays(weekdays, "weekly"):
            for d in dates_in_window:
                if d.weekday() in weekdays:
                    occ = {**base, "date": d, "date_iso": d.date().isoformat()}
                    occurrences.append(occ)
        else:
            # Solver picks best days in each week (same count as manual: len(weekdays) per week).
            # Period restricted to weekdays (Dag) or weekend (Helg) so när på dagen is followed.
            n_per_week = len(weekdays)
            d = start_date
            while d <= end_date:
                week_start = d
                week_end = min(d + timedelta(days=6), end_date)
                p_start, p_end = _flexible_period_restrict_to_shift(week_start, week_end, base["schift"])
                for i in range(n_per_week):
                    occ = {
                        **base,
                        "date": week_start,
                        "date_iso": week_start.date().isoformat(),
                        "flexible_day": True,
                        "period_start": p_start,
                        "period_end": p_end,
                        "period_start_iso": p_start.date().isoformat(),
                        "period_visit_index": i,
                    }
                    occurrences.append(occ)
                d = week_end + timedelta(days=1)

    elif recurrence == "biweekly":
        # One occurrence per 2-week block; solver picks day in period (weekdays/helg per shift)
        d = start_date
        while d <= end_date:
            period_end = min(d + timedelta(days=13), end_date)
            p_start, p_end = _flexible_period_restrict_to_shift(d, period_end, base["schift"])
            occ = {
                **base,
                "date": d,
                "date_iso": d.date().isoformat(),
                "flexible_day": True,
                "period_start": p_start,
                "period_end": p_end,
                "period_start_iso": p_start.date().isoformat(),
                "period_visit_index": 0,
            }
            occurrences.append(occ)
            d = period_end + timedelta(days=1)

    elif recurrence == "4weekly":
        d = start_date
        while d <= end_date:
            period_end = min(d + timedelta(days=27), end_date)
            p_start, p_end = _flexible_period_restrict_to_shift(d, period_end, base["schift"])
            occ = {
                **base,
                "date": d,
                "date_iso": d.date().isoformat(),
                "flexible_day": True,
                "period_start": p_start,
                "period_end": p_end,
                "period_start_iso": p_start.date().isoformat(),
                "period_visit_index": 0,
            }
            occurrences.append(occ)
            d = period_end + timedelta(days=1)

    elif recurrence == "3weekly":
        d = start_date
        while d <= end_date:
            period_end = min(d + timedelta(days=20), end_date)
            p_start, p_end = _flexible_period_restrict_to_shift(d, period_end, base["schift"])
            occ = {
                **base,
                "date": d,
                "date_iso": d.date().isoformat(),
                "flexible_day": True,
                "period_start": p_start,
                "period_end": p_end,
                "period_start_iso": p_start.date().isoformat(),
                "period_visit_index": 0,
            }
            occurrences.append(occ)
            d = period_end + timedelta(days=1)

    else:
        # weekly without specific weekdays: 1 visit per week, solver picks day (mån 07 – sön 22)
        d = start_date
        while d <= end_date:
            week_start = d
            week_end = min(d + timedelta(days=6), end_date)
            p_start, p_end = _flexible_period_restrict_to_shift(week_start, week_end, base["schift"])
            occ = {
                **base,
                "date": week_start,
                "date_iso": week_start.date().isoformat(),
                "flexible_day": True,
                "period_start": p_start,
                "period_end": p_end,
                "period_start_iso": p_start.date().isoformat(),
                "period_visit_index": 0,
            }
            occurrences.append(occ)
            d = week_end + timedelta(days=1)

    return occurrences


# ---- Time windows (Morgon / Lunch / Kväll + flex) ----


def _slot_for_nar_pa_dagen(nar: str, schift: str = "") -> Tuple[str, str]:
    """
    Return (slot_start, slot_end) for När på dagen.
    Morgon/Lunch/Kväll -> fixed slots. Tomt eller annat:
    - Om Skift = Dag -> 07:00–15:00 (skiftets fönster, månd–fred).
    - Om Skift = Helg -> 07:00–14:30.
    - Om Skift = Kväll -> 16:00–22:00.
    - Annars -> heldag 07:00–22:00.

    Special case: "Exakt dag/tid" returns ("EXACT", "EXACT") marker for zero-flex time windows.
    """
    n = (nar or "").strip().lower()
    # FIX: Recognize "Exakt dag/tid" entries that require exact time adherence
    if "exakt" in n:
        return ("EXACT", "EXACT")
    if "morgon" in n:
        return SLOT_MORGON
    if "lördag" in n:
        return SLOT_MORGON  # weekend morning slot (10-mars)
    if "förmiddag" in n:
        return SLOT_FORMIDDAG
    if "lunch" in n:
        return SLOT_LUNCH
    if "eftermiddag" in n:
        return SLOT_EFTERMIDDAG
    if "middag" in n:
        return SLOT_MIDDAG
    if "kväll" in n:
        return SLOT_KVALL
    s = (schift or "").strip().lower()
    if "dag" in s and "helg" not in s:
        return SHIFT_DAG
    if "helg" in s:
        return SHIFT_HELG
    if "kväll" in s:
        return SHIFT_KVALL
    return SLOT_HELDAG


def _compute_slot_bounds(occ: Dict[str, Any]) -> Tuple[int, int, bool]:
    """
    Return (min_start_minutes, max_start_minutes, is_heldag) for one occurrence.

    Three cases (aligned with attendo_4mars_to_fsr and dashboard):
    1. "Exakt dag/tid": exact Starttid, minimal 1-min flex
    2. Empty Före/Efter (cells blank): full slot from När på dagen + Skift
    3. Explicit 0,0 Före/Efter: exact time (same as case 1), minimal 1-min flex
    Non-zero Före/Efter: Starttid ± före/efter
    """
    slot_start, slot_end = _slot_for_nar_pa_dagen(occ["när_på_dagen"], occ.get("schift", ""))
    starttid = occ.get("starttid", "08:00")
    före = occ.get("före", 0)
    efter = occ.get("efter", 0)
    längd = occ.get("längd", 0)

    start_min = _parse_time_minutes(starttid)
    is_exact = (slot_start, slot_end) == ("EXACT", "EXACT")
    is_heldag = (slot_start, slot_end) == SLOT_HELDAG
    slot_start_min = _parse_time_minutes(slot_start) if slot_start != "EXACT" else start_min
    slot_end_min = _parse_time_minutes(slot_end) if slot_end != "EXACT" else start_min

    # FIX 1: "Exakt dag/tid" entries get MINIMAL flex (1 min) for Timefold compatibility
    if is_exact:
        return (start_min, start_min + 1, False)

    # When före==0 and efter==0: distinguish empty (full slot) vs explicit 0,0 (exact time)
    före_efter_empty = occ.get("före_efter_empty", True)  # default True for legacy rows
    if före == 0 and efter == 0:
        if före_efter_empty:
            # Empty Före/Efter → full slot from När på dagen
            kritisk = occ.get("kritisk_insats", False)
            if kritisk:
                return (max(slot_start_min, start_min - 1), start_min + 1, is_heldag)
            return (slot_start_min, max(slot_start_min, slot_end_min - längd), is_heldag)
        # Explicit 0,0 → exact time (same as Exakt dag/tid), minimal 1-min flex
        return (start_min, start_min + 1, False)

    # Före/Efter specified: use them
    min_start_min = max(0, start_min - före)
    max_start_min = start_min + efter

    # Säkerhetsnät: om någon kombination ger noll flex, använd sloten istället
    if min_start_min >= max_start_min:
        return (slot_start_min, max(slot_start_min, slot_end_min - längd), is_heldag)
    return (min_start_min, max_start_min, is_heldag)


def _make_time_window(date: datetime, min_start_min: int, max_start_min: int, längd: int) -> Dict[str, str]:
    """Build a single timeWindow dict for one date."""
    min_dt = date.replace(hour=min_start_min // 60, minute=min_start_min % 60, second=0, microsecond=0)
    max_st_dt = date.replace(hour=max_start_min // 60, minute=max_start_min % 60, second=0, microsecond=0)
    max_end_dt = max_st_dt + timedelta(minutes=längd)
    return {
        "minStartTime": min_dt.isoformat() + TIMEZONE_SUFFIX,
        "maxStartTime": max_st_dt.isoformat() + TIMEZONE_SUFFIX,
        "maxEndTime": max_end_dt.isoformat() + TIMEZONE_SUFFIX,
    }


def _build_time_windows(occ: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Build timeWindows list for a visit occurrence.
    For flexible_day with Morgon/Lunch/Kväll: one window per eligible day (enforces
    time-of-day on each day). For HELDAG or non-flexible: single window.
    """
    min_start_min, max_start_min, is_heldag = _compute_slot_bounds(occ)
    längd = occ.get("längd", 0)

    if occ.get("flexible_day") and occ.get("period_start") and occ.get("period_end"):
        p_start = occ["period_start"]
        p_end = occ["period_end"]
        if is_heldag:
            min_dt = p_start.replace(hour=min_start_min // 60, minute=min_start_min % 60, second=0, microsecond=0)
            max_st_dt = p_end.replace(hour=max_start_min // 60, minute=max_start_min % 60, second=0, microsecond=0)
            max_end_dt = max_st_dt + timedelta(minutes=längd)
            return [{
                "minStartTime": min_dt.isoformat() + TIMEZONE_SUFFIX,
                "maxStartTime": max_st_dt.isoformat() + TIMEZONE_SUFFIX,
                "maxEndTime": max_end_dt.isoformat() + TIMEZONE_SUFFIX,
            }]
        period_dates = _dates_in_window(p_start, p_end)
        # Restrict to row weekdays when set (e.g. "mån tis tor" => only Mon, Tue, Thu).
        # Otherwise flexible_day would get windows for all days in period (e.g. Fri) and
        # the solver could place multiple visits on the same day.
        weekdays = occ.get("weekdays")
        if weekdays is not None and len(weekdays) > 0:
            period_dates = [d for d in period_dates if d.weekday() in weekdays]
        windows = [_make_time_window(d, min_start_min, max_start_min, längd) for d in period_dates]
        return windows if windows else [_make_time_window(occ["date"], min_start_min, max_start_min, längd)]

    return [_make_time_window(occ["date"], min_start_min, max_start_min, längd)]


# ---- Visit dependencies: parse "Antal tim mellan besöken" ----


# When "Antal tim mellan besöken" is <= this (minutes), we use it for same-day chain (e.g. frukost→lunch 3.5h).
# When > this (e.g. 48h for dusch), we use it only for spread (same insats), so that insats can sit next to others.
SAME_DAY_DELAY_MAX_MINUTES = 12 * 60  # 12h
# Default delay between flexible_day visits (spread over days).
SPREAD_DELAY_DEFAULT_MIN = 18 * 60
SPREAD_DELAY_DEFAULT_ISO = "PT18H"


def _iso_duration_to_minutes(d: str) -> int:
    """Parse ISO 8601 duration (PTxHyM) to minutes."""
    if not d:
        return 0
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", d)
    if not m:
        return 0
    h = int(m.group(1) or 0)
    mi = int(m.group(2) or 0)
    return h * 60 + mi


def _slot_length_minutes(occ: Dict[str, Any]) -> int:
    """
    Return the length of the previous visit's time window (slot) in minutes.
    Used so that effective minDelay = interval - slot_length, giving each
    following visit the same preconditions as the first (start at window start).
    E.g. 48h interval with Morgon 07:00-10:30 → 48h - 3.5h = 44.5h effective.
    """
    slot_start, slot_end = _slot_for_nar_pa_dagen(
        occ.get("när_på_dagen", "") or "", occ.get("schift", "") or ""
    )
    return _parse_time_minutes(slot_end) - _parse_time_minutes(slot_start)


def _effective_delay_iso(
    interval_iso: str,
    prev_occ: Dict[str, Any],
    is_spread: bool,
) -> str:
    """
    Used only for spread dependencies (flexible_day, same insats). Effective minDelay
    = interval - prev_slot_length (floor 18h) so spacing does not drift across periods.
    Same-day chain uses the raw CSV delay (e.g. PT3H30M) without subtraction.
    """
    interval_min = _iso_duration_to_minutes(interval_iso)
    slot_min = _slot_length_minutes(prev_occ)
    effective_min = max(0, interval_min - slot_min)
    if is_spread:
        effective_min = max(SPREAD_DELAY_DEFAULT_MIN, effective_min)
    return _minutes_to_iso_duration(effective_min)


def _cap_infeasible_delay(
    prev_visit: Optional[Dict[str, Any]],
    dep_visit: Optional[Dict[str, Any]],
    delay_str: str,
) -> Optional[str]:
    """
    Check if a visitDependency delay is feasible per (prev_day, dep_day) window pair
    (same logic as scripts/analyze_dependency_feasibility.py). Requires at least one
    pair to satisfy prev_end + delay <= dep_latest_start with 15 min margin.
    If no pair is feasible, cap delay to the best possible with 15 min margin, or remove.
    Returns the (possibly capped) delay ISO string, or None if entirely infeasible.
    """
    if not prev_visit or not dep_visit:
        return delay_str
    prev_tws = prev_visit.get("timeWindows", [])
    dep_tws = dep_visit.get("timeWindows", [])
    if not prev_tws or not dep_tws:
        return delay_str

    delay_min = _iso_duration_to_minutes(delay_str)
    prev_dur_min = _iso_duration_to_minutes(prev_visit.get("serviceDuration", "PT0M"))
    dep_dur_min = _iso_duration_to_minutes(dep_visit.get("serviceDuration", "PT0M"))
    MARGIN_MIN = 15

    def _tw_date(tw: Dict[str, Any]) -> Optional[str]:
        s = (tw.get("minStartTime") or tw.get("maxEndTime") or "").replace("+01:00", "").split("T")[0]
        return s if len(s) == 10 else None

    def _tw_bounds(tw: Dict[str, Any]) -> Tuple[Optional[datetime], Optional[datetime]]:
        mn = (tw.get("minStartTime") or "").replace("+01:00", "+01:00")
        mx = (tw.get("maxEndTime") or "").replace("+01:00", "+01:00")
        try:
            return (datetime.fromisoformat(mn) if mn else None, datetime.fromisoformat(mx) if mx else None)
        except (ValueError, TypeError):
            return (None, None)

    prev_by_date: Dict[str, datetime] = {}
    for t in prev_tws:
        d = _tw_date(t)
        if not d:
            continue
        _, max_e = _tw_bounds(t)
        if max_e and (d not in prev_by_date or max_e > prev_by_date.get(d, max_e)):
            prev_by_date[d] = max_e

    dep_by_date: Dict[str, Tuple[datetime, datetime]] = {}
    for t in dep_tws:
        d = _tw_date(t)
        if not d:
            continue
        min_s, max_e = _tw_bounds(t)
        if not min_s or not max_e:
            continue
        latest_start = max_e - timedelta(minutes=dep_dur_min)
        if d not in dep_by_date:
            dep_by_date[d] = (min_s, latest_start)
        else:
            old_min, old_lt = dep_by_date[d]
            dep_by_date[d] = (min(min_s, old_min), max(latest_start, old_lt))

    best_cap_min: Optional[int] = None
    for dep_date, (_, dep_latest_start) in dep_by_date.items():
        # Same day
        if dep_date in prev_by_date:
            prev_max_end = prev_by_date[dep_date]
            max_delay = int((dep_latest_start - prev_max_end).total_seconds() / 60) - MARGIN_MIN
            if max_delay >= 0 and (best_cap_min is None or max_delay > best_cap_min):
                best_cap_min = max_delay
        # Prev previous day (for 18h+ delay; spread over days)
        if delay_min >= SPREAD_DELAY_DEFAULT_MIN:
            try:
                prev_dt = datetime.fromisoformat(dep_date + "T00:00:00+01:00") - timedelta(days=1)
                prev_date_str = prev_dt.strftime("%Y-%m-%d")
                if prev_date_str in prev_by_date:
                    prev_max_end = prev_by_date[prev_date_str]
                    max_delay = int((dep_latest_start - prev_max_end).total_seconds() / 60) - MARGIN_MIN
                    if max_delay >= 0 and (best_cap_min is None or max_delay > best_cap_min):
                        best_cap_min = max_delay
            except (ValueError, TypeError):
                pass

    # At least one pair feasible with 15 min margin?
    if best_cap_min is not None and delay_min <= best_cap_min:
        return delay_str

    if best_cap_min is None or best_cap_min < 0:
        print(
            f"WARNING: dependency {dep_visit.get('id')} ← {prev_visit.get('id')} infeasible (no window pair with 15 min margin), removing",
            file=sys.stderr,
        )
        return None

    capped_str = _minutes_to_iso_duration(best_cap_min)
    print(
        f"WARNING: dependency {dep_visit.get('id')} ← {prev_visit.get('id')}: "
        f"delay {delay_str} infeasible for all window pairs, capped to {capped_str} (15 min margin)",
        file=sys.stderr,
    )
    return capped_str


def _parse_min_delay_hours(s: str) -> Optional[str]:
    """Parse '3,5timmar', '48 timmar', '36 timmar' -> ISO 8601 duration e.g. PT3H30M."""
    if not s or not str(s).strip():
        return None
    s = str(s).strip().lower()
    s = re.sub(r"timmar?", "", s).strip()
    s = s.replace(",", ".")
    try:
        hours = float(s)
    except ValueError:
        return None
    h = int(hours)
    m = int(round((hours - h) * 60))
    if m:
        return f"PT{h}H{m}M"
    return f"PT{h}H"


# ---- Build visits and visit groups ----


def _day_slot_order(nar: str) -> int:
    """Morgon=0, Lunch=1, Kväll=2 for ordering visits same client/date."""
    n = (nar or "").strip().lower()
    if "morgon" in n:
        return 0
    if "lunch" in n:
        return 1
    return 2


def _assign_visit_ids_kundnr_lopnr(occurrences: List[Dict[str, Any]]) -> None:
    """
    Set visit_id as kundid_återkommande_expanded: kundnr + row (CSV row = recurrence) + expanded index.
    E.g. H015_r12_1, H015_r12_2 … for CSV row 12 expanded to multiple dates.
    """
    sorted_occs = sorted(
        occurrences,
        key=lambda o: (
            o.get("kundnr", ""),
            o.get("row_index", 0),
            o.get("date_iso", ""),
            _day_slot_order(o.get("när_på_dagen", "")),
            o.get("starttid", ""),
            o.get("period_start_iso", ""),
            o.get("period_visit_index", 0),
        ),
    )
    row_counter: Dict[tuple[str, int], int] = {}
    for occ in sorted_occs:
        k = (occ.get("kundnr") or "").strip()
        if not k:
            k = f"_row{occ.get('row_index', 0)}"
        ri = occ.get("row_index", 0)
        key = (k, ri)
        row_counter[key] = row_counter.get(key, 0) + 1
        occ["visit_id"] = f"{k}_r{ri}_{row_counter[key]}"


def _build_visits_and_groups(
    occurrences: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, str]]:
    """
    Build Timefold visits and visitGroups from occurrences.
    Expects visit_id already set on each occurrence (e.g. via _assign_visit_ids_kundnr_lopnr).
    Returns (standalone_visits, visit_groups, visit_id_to_preceding for dependencies).
    """

    visits_by_id: Dict[str, Dict[str, Any]] = {}
    for occ in occurrences:
        lat = _parse_float(occ.get("lat"), 0)
        lon = _parse_float(occ.get("lon"), 0)
        if lat == 0 and lon == 0:
            continue
        time_windows = _build_time_windows(occ)
        visit_id = occ["visit_id"]
        kundnr = occ.get("kundnr", "")
        nar = occ.get("när_på_dagen", "") or ""
        skift = occ.get("schift", "") or ""
        insatser = occ.get("insatser", "") or ""
        # Name: kundid + När på dagen + Skift + Insatser (e.g. "H015 Morgon Dag Tillsyn")
        name = f"{kundnr} {nar} {skift} {insatser}".strip()[:100]

        # Continuity tags: add customer ID so solver can prefer same employee for same customer
        customer_tag = f"customer_{kundnr}" if kundnr else ""

        visit: Dict[str, Any] = {
            "id": visit_id,
            "name": name,
            "location": [lat, lon],
            "timeWindows": time_windows,
            "serviceDuration": _minutes_to_iso_duration(occ.get("längd", 0)),
            "tags": [customer_tag] if customer_tag else [],
        }
        visits_by_id[visit_id] = visit
        occ["_visit"] = visit

    # Visit dependencies: two kinds.
    # 1) Same-day chain (måltider: frukost → lunch): different rows (insatser) same customer same day.
    #    Only when the LATER visit's row has "Antal tim mellan besöken" filled with a SHORT value
    #    (<= SAME_DAY_DELAY_MAX_MINUTES, e.g. 3.5h). Long values (48h etc.) are for spread only, so
    #    e.g. dusch (48h) gets no same-day dep and can be placed directly next to lunch.
    # 2) Spread: same insats (same row), flexible_day, multiple occurrences (week 2,3,4) with
    #    minDelay from CSV (e.g. 48h) or 18h default.
    # Include ALL occurrences (pinned + flexible_day) per (kundnr, date_iso) so we can add
    # "dusch after morgon" same-day dependency for Bad/Dusch with long delay (e.g. 42h).
    per_client_date: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for occ in occurrences:
        if occ.get("_visit") is None:
            continue
        key = (occ["kundnr"], occ["date_iso"])
        per_client_date[key].append(occ)

    preceding_map: Dict[str, Tuple[str, str]] = {}  # vid -> (prev_id, min_delay_iso)
    for _key, occs in per_client_date.items():
        occs.sort(key=lambda o: (_day_slot_order(o.get("når_på_dagen", "")), o.get("starttid", "")))
        for i, occ in enumerate(occs):
            if i == 0:
                continue
            prev_occ = occs[i - 1]
            delay_str = _parse_min_delay_hours(occ.get("antal_tim_mellan", ""))

            # FIX 3a: Handle same-day sequencing even without explicit delay
            # If current visit starts after previous (by time), add PT0M dependency to prevent overlap
            curr_start_min = _parse_time_minutes(occ.get("starttid", "08:00"))
            prev_start_min = _parse_time_minutes(prev_occ.get("starttid", "08:00"))

            if delay_str:
                delay_min = _iso_duration_to_minutes(delay_str)
                # FIX 3b: Don't skip long delays entirely - instead, check if they're meant
                # for same-day sequencing (e.g., shower 36h after morning on Mon/Wed/Fri)
                # If the delay is longer than 12h, only apply it if it's truly a spread constraint
                # (same insats/row) rather than a same-day sequence.
                if delay_min > SAME_DAY_DELAY_MAX_MINUTES:
                    # Check if same row (same insats) - if so, this is a spread constraint, skip
                    # If different rows (different insats), this might be bad data or a same-day constraint
                    if occ.get("row_index") == prev_occ.get("row_index"):
                        continue  # Spread constraint, handled separately below
                    # Different rows with long delay: likely same-day but with weird delay value
                    # Use PT0M to sequence them without the long delay
                    delay_str = "PT0M"
                # Use the specified delay
                preceding_map[occ["visit_id"]] = (prev_occ["visit_id"], delay_str)
            elif curr_start_min > prev_start_min:
                # No explicit delay, but current visit starts later: add PT0M to prevent overlap
                preceding_map[occ["visit_id"]] = (prev_occ["visit_id"], "PT0M")

    # Same-day "dusch dikt med morgon": only when the two visit insatser (rows) are a true pair:
    # - same client, same date, same återkommande dag (recurrence), same när på dagen och skift,
    # - and starttid/före/efter place both within the same time window (slot bounds overlap).
    # Effect of delay=0 is the same as combining to one long visit (less travel). If Timefold has
    # issues with delay=0, consider merging the two visits into one long visit instead.
    def _recurrence_key(occ: Dict[str, Any]) -> tuple:
        """Same recurrence = same weekdays so they fall on same dates."""
        wd = occ.get("weekdays")
        return (tuple(sorted(wd)) if wd else ())

    def _time_window_bounds_overlap(occ_a: Dict[str, Any], occ_b: Dict[str, Any]) -> bool:
        """True if the two occurrences' start-time windows (min_start, max_start) overlap."""
        min_a, max_a, _ = _compute_slot_bounds(occ_a)
        min_b, max_b, _ = _compute_slot_bounds(occ_b)
        return min_a < max_b and min_b < max_a

    # Group by (client, date, när_på_dagen, skift, recurrence) so we only pair same-slot same-recurrence visits.
    per_client_date_slot: Dict[Tuple[Any, ...], List[Dict[str, Any]]] = defaultdict(list)
    for occ in occurrences:
        if occ.get("_visit") is None:
            continue
        key = (
            occ["kundnr"],
            occ["date_iso"],
            (occ.get("när_på_dagen") or "").strip(),
            (occ.get("schift") or "").strip(),
            _recurrence_key(occ),
        )
        per_client_date_slot[key].append(occ)

    for _key, occs in per_client_date_slot.items():
        occs_sorted = sorted(occs, key=lambda o: (_day_slot_order(o["när_på_dagen"]), o.get("starttid", "")))
        morgon_occs = [o for o in occs_sorted if "morgon" in (o.get("när_på_dagen") or "").lower()]
        for occ in occs_sorted:
            if occ["visit_id"] in preceding_map:
                continue
            insats_lower = (occ.get("insatser") or "").lower()
            if "bad/dusch" not in insats_lower and "dusch" not in insats_lower:
                continue
            delay_str = _parse_min_delay_hours(occ.get("antal_tim_mellan", ""))
            if not delay_str:
                continue
            if _iso_duration_to_minutes(delay_str) <= SAME_DAY_DELAY_MAX_MINUTES:
                continue
            # Find a morgon in this group whose time window overlaps this dusch (same time window).
            for m_occ in morgon_occs:
                if _time_window_bounds_overlap(m_occ, occ):
                    preceding_map[occ["visit_id"]] = (m_occ["visit_id"], "PT0M")
                    break

    # Spread dependencies: N flexible_day visits in same (row, period). When N >= 2 we need a delay
    # between them. If "Antal tim mellan besöken" is filled we use it; if empty we use 18h default
    # so they fall on different days (18h < 24h avoids lunch→lunch next day being impossible).
    # For N == 1 (e.g. 1x laundry per week) we add no dependency.
    spread_deps: List[Tuple[str, str, str]] = []  # (vid, prev_id, min_delay_iso)
    per_row_period: Dict[Tuple[int, str], List[Dict[str, Any]]] = defaultdict(list)
    for occ in occurrences:
        if occ.get("_visit") is None or not occ.get("flexible_day"):
            continue
        ri = occ.get("row_index", 0)
        psi = occ.get("period_start_iso", "")
        if psi:
            per_row_period[(ri, psi)].append(occ)
    for (_ri, _psi), occs in per_row_period.items():
        if len(occs) < 2:
            continue
        occs.sort(key=lambda o: (o.get("period_visit_index", 0), o.get("starttid", "")))
        delay_str = _parse_min_delay_hours(occs[0].get("antal_tim_mellan", ""))
        if not delay_str:
            delay_str = SPREAD_DELAY_DEFAULT_ISO
        else:
            # Effective delay = interval - prev slot length (e.g. 48h - 2.5h) so no drift over time
            delay_str = _effective_delay_iso(delay_str, occs[0], is_spread=True)

        # Chain feasibility: check that N visits with (N-1) delays + service time
        # fit within the available window. If not, cap to max feasible delay.
        n = len(occs)
        delay_min = _iso_duration_to_minutes(delay_str)
        avg_dur = sum(o.get("längd", 0) for o in occs) / n
        first_v = visits_by_id.get(occs[0].get("visit_id", ""), {})
        last_v = visits_by_id.get(occs[-1].get("visit_id", ""), {})
        first_tws = first_v.get("timeWindows", [])
        last_tws = last_v.get("timeWindows", [])
        if first_tws and last_tws:
            try:
                chain_start = datetime.fromisoformat(first_tws[0]["minStartTime"])
                chain_end = datetime.fromisoformat(last_tws[-1]["maxEndTime"])
                window_min = (chain_end - chain_start).total_seconds() / 60
                needed_min = (n - 1) * (delay_min + avg_dur)
                if needed_min > window_min and window_min > 0:
                    max_delay = max(0, (window_min - n * avg_dur) / (n - 1))
                    capped = int(max_delay * 0.9)
                    capped = max(capped, SPREAD_DELAY_DEFAULT_MIN)
                    if capped < delay_min:
                        delay_str = _minutes_to_iso_duration(capped)
                        print(
                            f"WARNING: spread chain ({n} visits) delay {_minutes_to_iso_duration(delay_min)} "
                            f"infeasible for {window_min:.0f}min window, capped to {delay_str}",
                            file=sys.stderr,
                        )
            except (ValueError, TypeError, KeyError):
                pass

        for i in range(1, len(occs)):
            spread_deps.append((occs[i]["visit_id"], occs[i - 1]["visit_id"], delay_str))

    # Visit groups: same Dubbel + same date (build before dependencies so we can skip same-group deps)
    groups_by_key: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for occ in occurrences:
        v = occ.get("_visit")
        if not v or not occ.get("dubbel"):
            continue
        gk = f"{occ['dubbel']}_{occ['date_iso']}"
        if v not in groups_by_key[gk]:
            groups_by_key[gk].append(v)

    # visit_id -> group_key for groups with >= 2 visits (used to avoid dependency loops)
    visit_id_to_group: Dict[str, str] = {}
    for gk, group_visits in groups_by_key.items():
        if len(group_visits) >= 2:
            for v in group_visits:
                visit_id_to_group[v["id"]] = gk

    # visit_id -> (row_index, period_start_iso) for flexible_day (skip same-day dep when both in same spread)
    visit_id_to_spread_key: Dict[str, Tuple[int, str]] = {}
    for occ in occurrences:
        if occ.get("_visit") and occ.get("flexible_day") and occ.get("period_start_iso"):
            visit_id_to_spread_key[occ["visit_id"]] = (occ.get("row_index", 0), occ["period_start_iso"])

    # Collect dependencies: same-day (short delay) + spread (same row, flexible_day).
    deps_by_vid: Dict[str, List[Tuple[str, str]]] = defaultdict(list)  # vid -> [(prev_id, delay_str), ...]
    for vid, (prev_id, delay_str) in preceding_map.items():
        if vid not in visits_by_id or prev_id not in visits_by_id:
            continue
        if visit_id_to_group.get(vid) == visit_id_to_group.get(prev_id) and visit_id_to_group.get(vid):
            continue
        if vid in visit_id_to_spread_key and prev_id in visit_id_to_spread_key:
            if visit_id_to_spread_key[vid] == visit_id_to_spread_key[prev_id]:
                continue
        deps_by_vid[vid].append((prev_id, delay_str))
    for vid, prev_id, delay_str in spread_deps:
        if vid not in visits_by_id or prev_id not in visits_by_id:
            continue
        # Do not add dependency between visits in the same visit group (avoids loops in Timefold model)
        if visit_id_to_group.get(vid) == visit_id_to_group.get(prev_id) and visit_id_to_group.get(vid):
            continue
        deps_by_vid[vid].append((prev_id, delay_str))
    # Any dependency with original delay >= 18h is a "spread" (different days) constraint; never cap below 18h.
    MIN_SPREAD_DELAY_MIN = SPREAD_DELAY_DEFAULT_MIN
    for vid, deps in deps_by_vid.items():
        if vid not in visits_by_id:
            continue
        dep_list: List[Dict[str, Any]] = []
        for i, (prev_id, delay_str) in enumerate(deps):
            original_min = _iso_duration_to_minutes(delay_str)
            capped = _cap_infeasible_delay(visits_by_id.get(prev_id), visits_by_id.get(vid), delay_str)
            if capped:
                if original_min >= MIN_SPREAD_DELAY_MIN:
                    capped_min = _iso_duration_to_minutes(capped)
                    if capped_min < MIN_SPREAD_DELAY_MIN:
                        capped = _minutes_to_iso_duration(MIN_SPREAD_DELAY_MIN)
                dep_list.append({"id": f"dep_{vid}_{i}", "precedingVisit": prev_id, "minDelay": capped})
        if dep_list:
            visits_by_id[vid]["visitDependencies"] = dep_list

    standalone: List[Dict[str, Any]] = []
    visit_groups: List[Dict[str, Any]] = []
    used_in_group: set[str] = set()

    for gk, group_visits in groups_by_key.items():
        if len(group_visits) >= 2:
            visit_groups.append({"id": f"VG_{_slug(gk)}", "visits": group_visits})
            used_in_group.update(v["id"] for v in group_visits)
        else:
            for v in group_visits:
                if v["id"] not in used_in_group:
                    standalone.append(v)
                    used_in_group.add(v["id"])

    for v in visits_by_id.values():
        if v["id"] not in used_in_group:
            standalone.append(v)

    return (standalone, visit_groups, {})


# ---- Vehicles from Slinga ----


def _build_vehicles(
    occurrences: List[Dict[str, Any]],
    start_date: datetime,
    end_date: datetime,
    no_supplementary_vehicles: bool = False,
) -> List[Dict[str, Any]]:
    """
    Build one vehicle per unique Slinga. For each Slinga, collect (weekday, shift_type)
    from occurrences; add shifts for each date in window that matches.
    Day/Helg: break 10:00-14:00, 30 min at office.
    """
    # Slinga -> set of (weekday, shift_type) from occurrence's Schift
    slinga_schedule: Dict[str, Dict[Tuple[int, str], None]] = defaultdict(dict)
    for occ in occurrences:
        slinga_raw = occ.get("slinga", "")
        if not slinga_raw:
            continue
        slinga = _slug(slinga_raw)
        schift = occ.get("schift", "").strip().lower()
        if "kväll" in schift:
            st = "kväll"
        elif "helg" in schift:
            st = "helg"
        else:
            st = "dag"
        if occ.get("flexible_day") and occ.get("period_start") and occ.get("period_end"):
            for d in _dates_in_window(occ["period_start"], occ["period_end"]):
                slinga_schedule[slinga][(d.weekday(), st)] = None
        else:
            wd = occ["date"].weekday()
            slinga_schedule[slinga][(wd, st)] = None

    dates = _dates_in_window(start_date, end_date)
    vehicles: List[Dict[str, Any]] = []
    used_ids: set[str] = set()

    for slinga in sorted(slinga_schedule.keys()):
        vid = slinga
        idx = 0
        while vid in used_ids:
            idx += 1
            vid = f"{slinga}_{idx}"
        used_ids.add(vid)

        schedule = slinga_schedule[slinga]
        shifts: List[Dict[str, Any]] = []
        date_iso = ""
        for d in dates:
            wd = d.weekday()
            date_iso = d.date().isoformat()
            # Day shift: Mon-Fri
            if (wd, "dag") in schedule:
                shift_id = f"{vid}_{date_iso}_dag"
                shift = _create_shift_with_break(
                    shift_id, d, "07:00", "15:00", DEFAULT_OFFICE
                )
                shifts.append(shift)
            # Helg: Sat-Sun
            if (wd, "helg") in schedule:
                shift_id = f"{vid}_{date_iso}_helg"
                shift = _create_shift_with_break(
                    shift_id, d, "07:00", "14:30", DEFAULT_OFFICE
                )
                shifts.append(shift)
            # Kväll: every day
            if (wd, "kväll") in schedule:
                shift_id = f"{vid}_{date_iso}_kvall"
                shift = _create_shift_no_break(shift_id, d, "16:00", "22:00", DEFAULT_OFFICE)
                shifts.append(shift)

        if shifts:
            vehicles.append({
                "id": vid,
                "vehicleType": "VAN",
                "shifts": shifts,
            })

    if not no_supplementary_vehicles:
        vehicles = _add_supplementary_vehicles(vehicles, occurrences, start_date, end_date)
    return vehicles


def _add_supplementary_vehicles(
    vehicles: List[Dict[str, Any]],
    occurrences: List[Dict[str, Any]],
    start_date: datetime,
    end_date: datetime,
) -> List[Dict[str, Any]]:
    """
    Analyze demand vs supply per date/shift-type. Add supplementary vehicles
    when the number of visits on a date exceeds existing shift capacity.
    Ensures visit groups (Dubbel) have enough concurrent vehicles.
    """
    from collections import Counter as Ctr

    dates = _dates_in_window(start_date, end_date)

    kvall_demand: Dict[str, int] = Ctr()
    dag_demand: Dict[str, int] = Ctr()
    for occ in occurrences:
        if _parse_float(occ.get("lat"), 0) == 0 and _parse_float(occ.get("lon"), 0) == 0:
            continue
        tws_dates: List[str] = []
        if occ.get("flexible_day") and occ.get("period_start") and occ.get("period_end"):
            for d in _dates_in_window(occ["period_start"], occ["period_end"]):
                tws_dates.append(d.date().isoformat())
        else:
            tws_dates.append(occ["date"].date().isoformat())

        slot_start, _ = _slot_for_nar_pa_dagen(occ.get("när_på_dagen", ""))
        for dt in tws_dates:
            if _parse_time_minutes(slot_start) >= 16 * 60:
                kvall_demand[dt] += 1
            else:
                dag_demand[dt] += 1

    kvall_supply: Dict[str, int] = Ctr()
    dag_supply: Dict[str, int] = Ctr()
    for veh in vehicles:
        for s in veh.get("shifts", []):
            dt = s["minStartTime"].split("T")[0]
            h = int(s["minStartTime"].split("T")[1].split(":")[0])
            if h >= 16:
                kvall_supply[dt] += 1
            else:
                dag_supply[dt] += 1

    max_kvall_deficit = 0
    max_dag_deficit = 0
    for d in dates:
        ds = d.date().isoformat()
        kd = kvall_demand.get(ds, 0) - kvall_supply.get(ds, 0)
        dd = dag_demand.get(ds, 0) - dag_supply.get(ds, 0)
        if kd > max_kvall_deficit:
            max_kvall_deficit = kd
        if dd > max_dag_deficit:
            max_dag_deficit = dd

    extra_kvall = max(0, (max_kvall_deficit + 2) // 3)
    extra_dag = max(0, (max_dag_deficit + 3) // 4)

    used_ids = {v["id"] for v in vehicles}
    added = 0

    for i in range(extra_kvall):
        vid = f"Extra_Kvall_{i + 1}"
        while vid in used_ids:
            vid += "_x"
        used_ids.add(vid)
        shifts = []
        for d in dates:
            sid = f"{vid}_{d.date().isoformat()}_kvall"
            shifts.append(_create_shift_no_break(sid, d, "16:00", "22:00", DEFAULT_OFFICE))
        vehicles.append({"id": vid, "vehicleType": "VAN", "shifts": shifts})
        added += 1

    for i in range(extra_dag):
        vid = f"Extra_Dag_{i + 1}"
        while vid in used_ids:
            vid += "_x"
        used_ids.add(vid)
        shifts = []
        for d in dates:
            wd = d.weekday()
            if wd <= 4:
                sid = f"{vid}_{d.date().isoformat()}_dag"
                shifts.append(_create_shift_with_break(sid, d, "07:00", "15:00", DEFAULT_OFFICE))
            else:
                sid = f"{vid}_{d.date().isoformat()}_helg"
                shifts.append(_create_shift_with_break(sid, d, "07:00", "14:30", DEFAULT_OFFICE))
        vehicles.append({"id": vid, "vehicleType": "VAN", "shifts": shifts})
        added += 1

    if added:
        print(
            f"Added {extra_kvall} extra Kväll + {extra_dag} extra Dag vehicles "
            f"(peak deficit: kväll={max_kvall_deficit}, dag={max_dag_deficit})",
            file=sys.stderr,
        )

    return vehicles


def _create_shift_with_break(
    shift_id: str,
    visit_date: datetime,
    shift_start: str,
    shift_end: str,
    start_location: List[float],
) -> Dict[str, Any]:
    """Create shift with requiredBreak 10:00-14:00, 30 min, at office (plan reference)."""
    min_start = _to_iso_datetime(visit_date, shift_start)
    max_end = _to_iso_datetime(visit_date, shift_end)
    br_min = _to_iso_datetime(visit_date, "10:00")
    br_max = _to_iso_datetime(visit_date, "14:00")
    shift: Dict[str, Any] = {
        "id": shift_id,
        "startLocation": start_location,
        "minStartTime": min_start,
        "maxEndTime": max_end,
        "skills": [],
        "tags": [],
        "requiredBreaks": [
            {
                "id": f"{shift_id}_break",
                "minStartTime": br_min,
                "maxEndTime": br_max,
                "duration": "PT30M",
                "costImpact": "PAID",
                "type": "FLOATING",
                "location": start_location,
            }
        ],
        "temporarySkillSets": [],
        "temporaryTagSets": [],
        "itinerary": [],
    }
    return shift


def _create_shift_no_break(
    shift_id: str,
    visit_date: datetime,
    shift_start: str,
    shift_end: str,
    start_location: List[float],
) -> Dict[str, Any]:
    """Create evening shift without break."""
    min_start = _to_iso_datetime(visit_date, shift_start)
    max_end = _to_iso_datetime(visit_date, shift_end)
    return {
        "id": shift_id,
        "startLocation": start_location,
        "minStartTime": min_start,
        "maxEndTime": max_end,
        "skills": [],
        "tags": [],
        "temporarySkillSets": [],
        "temporaryTagSets": [],
        "itinerary": [],
    }


# ---- Flex verification: ALLA BESÖK HAR FLEX (tid eller dag) ----


def _verify_all_visits_have_flex(model_input: Dict[str, Any]) -> Tuple[bool, List[Tuple[str, str]]]:
    """
    Check that every visit has flex: either time flex (minStartTime != maxStartTime
    within a window) or day flex (multiple time windows or one window spanning >1 day).
    Returns (ok, list of (visit_id, reason) for violations).
    """
    violations: List[Tuple[str, str]] = []
    visits: List[Dict[str, Any]] = list(model_input.get("visits") or [])
    for g in model_input.get("visitGroups") or []:
        visits.extend(g.get("visits") or [])

    for v in visits:
        vid = v.get("id", "")
        tws = v.get("timeWindows") or []
        if not tws:
            violations.append((vid, "no time windows"))
            continue
        # Day flex: more than one window → solver picks day
        if len(tws) > 1:
            continue
        tw = tws[0]
        min_s = (tw.get("minStartTime") or "").strip()
        max_s = (tw.get("maxStartTime") or "").strip()
        if not min_s or not max_s:
            violations.append((vid, "missing min/max start"))
            continue
        # Same datetime → 0 flex
        if min_s == max_s:
            violations.append((vid, f"0 flex: minStartTime==maxStartTime ({min_s[:19]})"))
            continue
        # Single window spanning different dates → day flex
        min_date = min_s.split("T")[0]
        max_date = max_s.split("T")[0]
        if min_date != max_date:
            continue
        # Same day, different time → time flex
    return (len(violations) == 0, violations)


# ---- Main pipeline ----


def _load_address_coordinates(path: Path) -> Dict[str, Tuple[float, float]]:
    """Load JSON map normalized_address -> [lat, lon]. Keys normalized with _normalize_address_for_fallback_lookup."""
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    out: Dict[str, Tuple[float, float]] = {}
    for addr, coords in raw.items():
        if isinstance(coords, (list, tuple)) and len(coords) >= 2:
            lat, lon = float(coords[0]), float(coords[1])
            norm = _normalize_address_for_fallback_lookup(addr)
            if norm:
                out[norm] = (lat, lon)
    return out


def generate_fsr_json(
    csv_path: Path,
    output_path: Path,
    start_date_str: Optional[str] = None,
    end_date_str: Optional[str] = None,
    run_name: str = "Huddinge 4mars Schedule",
    geocode: bool = True,
    geocode_rate_sec: float = 1.0,
    no_supplementary_vehicles: bool = False,
    address_coordinates_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Read 4mars CSV, expand, geocode, build visits and vehicles, write FSR JSON.
    If start/end dates not given, auto-computes: Monday of current week + longest recurrence.
    """

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=",")
        rows = list(reader)

    if not rows:
        raise ValueError("CSV is empty")

    longest_days = _longest_recurrence_days(rows)

    if not start_date_str:
        start_date_str = _auto_planning_window()
        print(f"Auto start date: {start_date_str} (Monday of current week)", file=sys.stderr)
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

    if not end_date_str:
        end_date = start_date + timedelta(days=longest_days - 1)
        end_date_str = end_date.strftime("%Y-%m-%d")
        print(f"Auto end date: {end_date_str} ({longest_days} days, matching longest recurrence)", file=sys.stderr)
    else:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    window_days = (end_date - start_date).days + 1
    if window_days < longest_days:
        print(
            f"WARNING: planning window ({window_days}d) shorter than longest recurrence ({longest_days}d). "
            f"Recommend --end-date {(start_date + timedelta(days=longest_days - 1)).strftime('%Y-%m-%d')}",
            file=sys.stderr,
        )

    occurrences: List[Dict[str, Any]] = []
    for i, row in enumerate(rows):
        occs = _expand_row_to_occurrences(row, i, start_date, end_date)
        occurrences.extend(occs)

    _write_facit(csv_path, occurrences, start_date, end_date)

    external_coordinates: Optional[Dict[str, Tuple[float, float]]] = None
    if address_coordinates_path and address_coordinates_path.exists():
        external_coordinates = _load_address_coordinates(address_coordinates_path)
        print(f"Loaded {len(external_coordinates)} address(es) from {address_coordinates_path}", file=sys.stderr)

    if geocode:
        _fill_coordinates_4mars(
            occurrences,
            geocode_rate_sec=geocode_rate_sec,
            external_coordinates=external_coordinates,
        )

    n_no_coords = sum(1 for o in occurrences if _parse_float(o.get("lat"), 0) == 0 and _parse_float(o.get("lon"), 0) == 0)
    if n_no_coords:
        failed_addrs = {o.get("address_key", "(no address)") for o in occurrences
                        if _parse_float(o.get("lat"), 0) == 0 and _parse_float(o.get("lon"), 0) == 0
                        and (o.get("address_key") or "").strip()}
        if geocode and failed_addrs:
            raise ValueError(
                "ALLA CSV RADER MÅSTE HA ADDRESSER -> KOORDINATER. "
                "Följande adresser saknar koordinat (Nominatim):\n  " +
                "\n  ".join(sorted(failed_addrs)) +
                "\nRensa Gata i CSV från LGH, VÅN, våning etc. Kör sedan build_address_coordinates.py "
                "tills alla adresser löses; ingen fallback tillåten."
            )
        print(f"WARNING: {n_no_coords} occurrences have no coordinates — these visits will be DROPPED.", file=sys.stderr)
        for addr in sorted({o.get("address_key", "(no address)") for o in occurrences
                           if _parse_float(o.get("lat"), 0) == 0 and _parse_float(o.get("lon"), 0) == 0}):
            print(f"  - {addr}", file=sys.stderr)

    _assign_visit_ids_kundnr_lopnr(occurrences)
    standalone, visit_groups, _ = _build_visits_and_groups(occurrences)
    vehicles = _build_vehicles(
        occurrences, start_date, end_date,
        no_supplementary_vehicles=no_supplementary_vehicles,
    )

    planning_window = {
        "startDate": f"{start_date_str}T00:00:00{TIMEZONE_SUFFIX}",
        "endDate": f"{end_date_str}T23:59:59{TIMEZONE_SUFFIX}",
    }

    model_input: Dict[str, Any] = {
        "planningWindow": planning_window,
        "vehicles": vehicles,
        "visits": standalone,
    }
    if visit_groups:
        model_input["visitGroups"] = visit_groups

    ok, violations = _verify_all_visits_have_flex(model_input)
    if not ok:
        for vid, reason in violations:
            print(f"FLEX VIOLATION: {vid} — {reason}", file=sys.stderr)
        raise ValueError(
            f"ALLA BESÖK MÅSTE HA FLEX (tid eller dag). {len(violations)} besök har 0 flex. "
            "Korrigera _compute_slot_bounds / CSV så att varje besök får antingen tidsflex eller dagflex."
        )

    payload: Dict[str, Any] = {
        "config": {"run": {"name": run_name}},
        "modelInput": model_input,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    _log_csv_json_summary(rows, occurrences, model_input)
    return payload


def _write_facit(
    csv_path: Path,
    occurrences: List[Dict[str, Any]],
    start_date: datetime,
    end_date: datetime,
) -> None:
    """
    Write facit.json next to the CSV with expected counts from expansion.
    Same definitions as dashboard import: visits, groups (client+date+Dubbel ≥2), same-day ordering edges.
    """
    visits_by_client_date: Dict[Tuple[str, str], int] = defaultdict(int)
    group_key_count: Dict[Tuple[str, str, str], int] = defaultdict(int)
    for occ in occurrences:
        kundnr = str(occ.get("kundnr", "")).strip()
        date_iso = str(occ.get("date_iso", "")).strip()
        if not date_iso:
            continue
        visits_by_client_date[(kundnr, date_iso)] += 1
        dubbel = str(occ.get("dubbel", "")).strip()
        if dubbel:
            group_key_count[(kundnr, date_iso, dubbel)] += 1

    expected_visit_count = len(occurrences)
    expected_visit_groups = sum(1 for c in group_key_count.values() if c >= 2)
    expected_same_day_ordering = sum(max(0, c - 1) for c in visits_by_client_date.values())

    window_days = (end_date - start_date).days + 1
    period_weeks = window_days / 7.0

    facit = {
        "sourceCsv": csv_path.name,
        "periodDays": window_days,
        "periodWeeks": period_weeks,
        "expectedVisitCount": expected_visit_count,
        "expectedVisitGroupsCount": expected_visit_groups,
        "expectedSameDayOrderingCount": expected_same_day_ordering,
        "periodStart": start_date.date().isoformat(),
        "periodEnd": end_date.date().isoformat(),
        "appendix": "Facit from CSV expansion: visits = occurrence count; groups = (client, date, Dubbel) with ≥2; dependencies = same-day ordering edges (no skip logic).",
        "writtenAt": datetime.utcnow().isoformat() + "Z",
    }
    out = csv_path.parent / "facit.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(facit, f, indent=2, ensure_ascii=False)
    print(f"Wrote facit: {out}", file=sys.stderr)


def _log_csv_json_summary(
    rows: List[Dict[str, Any]],
    occurrences: List[Dict[str, Any]],
    model_input: Dict[str, Any],
) -> None:
    """
    Log how JSON output matches CSV: kunder, besök, dubbel, vehicles, shifts.
    """
    csv_rader = len(rows)
    csv_kunder = len({str(r.get("Kundnr", "") or "").strip() for r in rows})
    csv_besok_utokade = len(occurrences)
    csv_rader_med_dubbel = sum(1 for r in rows if (str(r.get("Dubbel", "") or "").strip()))
    csv_slingor = len({_slug(str(r.get("Slinga", "") or "")) for r in rows if (str(r.get("Slinga", "") or "").strip())})

    visits_standalone = len(model_input.get("visits") or [])
    visit_groups = model_input.get("visitGroups") or []
    visits_i_grupper = sum(len(g.get("visits") or []) for g in visit_groups)
    json_besok_totalt = visits_standalone + visits_i_grupper
    json_vehicles = len(model_input.get("vehicles") or [])
    json_shifts = sum(len(v.get("shifts") or []) for v in (model_input.get("vehicles") or []))

    lines = [
        "",
        "CSV vs JSON – sammanställning",
        "=============================",
        "CSV:",
        f"  Rader (besöksrader):     {csv_rader}",
        f"  Unika kunder (Kundnr):   {csv_kunder}",
        f"  Utökade besök (antal):   {csv_besok_utokade}  (recurrence × planeringsfönster)",
        f"  Rader med Dubbel:        {csv_rader_med_dubbel}  (samma Dubbel-id → visit group)",
        f"  Unika Slingor:           {csv_slingor}  (→ vehicles)",
        "JSON (modelInput):",
        f"  Besök standalone:        {visits_standalone}",
        f"  Visit groups:            {len(visit_groups)}  grupper, {visits_i_grupper} besök",
        f"  Besök totalt:            {json_besok_totalt}  (ska motsvara utökade med adress/koordinat)",
        f"  Vehicles:                {json_vehicles}  (en per Slinga)",
        f"  Shifts:                  {json_shifts}  (vehicle_id + date + dag/helg/kväll)",
        "",
    ]
    for line in lines:
        print(line, file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert Attendo 4mars Huddinge CSV to Timefold FSR JSON"
    )
    parser.add_argument("input", type=Path, help="Input CSV (ATTENDO_DATABEHOV_PER_KUND_OCH_BESOK)")
    parser.add_argument("-o", "--output", type=Path, help="Output JSON path")
    parser.add_argument("--start-date", default=None, help="Planning start (Monday). Omit = Monday of current week")
    parser.add_argument("--end-date", default=None, help="Planning end (Sunday). Omit = auto from longest recurrence")
    parser.add_argument("--name", default="Huddinge 4mars Schedule", help="Run name")
    parser.add_argument("--no-geocode", action="store_true", help="Skip geocoding (use if addresses pre-filled)")
    parser.add_argument("--geocode-rate", type=float, default=1.0, help="Seconds between geocode requests")
    parser.add_argument(
        "--address-coordinates",
        type=Path,
        default=None,
        help="JSON file mapping address -> [lat, lon] for addresses Nominatim misses (from build_address_coordinates.py)",
    )
    parser.add_argument(
        "--no-supplementary-vehicles",
        action="store_true",
        help="Do not add extra Kväll/Dag vehicles (match reference 26 vehicles for 2w)",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input not found: {args.input}", file=sys.stderr)
        return 1

    out = args.output or args.input.parent / "export-field-service-routing-v1-4mars-input.json"

    try:
        generate_fsr_json(
            args.input,
            out,
            start_date_str=args.start_date,
            end_date_str=args.end_date,
            run_name=args.name,
            geocode=not args.no_geocode,
            geocode_rate_sec=args.geocode_rate,
            no_supplementary_vehicles=args.no_supplementary_vehicles,
            address_coordinates_path=args.address_coordinates,
        )
        print(f"Wrote: {out}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
