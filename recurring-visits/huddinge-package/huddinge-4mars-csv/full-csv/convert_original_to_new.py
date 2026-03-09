#!/usr/bin/env python3
"""
Convert ALL 81 clients to the new CSV format:
- 15 clients already enriched in ATTENDO_DATABEHOV → keep as-is
- 66 remaining clients from the original 1-Huddinge → convert & enrich
"""

import csv
import re
from collections import defaultdict
from typing import Dict, List, Set, Tuple

ORIGINAL_CSV = "/sessions/relaxed-trusting-hawking/mnt/uploads/1-Huddinge - Blad1.csv"
NEW_CSV = "/sessions/relaxed-trusting-hawking/mnt/uploads/ATTENDO_DATABEHOV_PER_KUND_OCH_BESOK - data.csv"
OUTPUT_CSV = "/sessions/relaxed-trusting-hawking/mnt/full-csv/ATTENDO_DATABEHOV_ALL_81_CLIENTS.csv"


# Normalize split/misspelled street names to their correct geocodable form
STREET_NAME_FIXES = {
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


def clean_address(gata: str) -> str:
    """
    Strip apartment/floor/staircase details that break geocoding,
    and normalize split street names (e.g. 'DIAGNOS VÄGEN' → 'Diagnosvägen').
    Examples:
      'DIAGNOSVÄGEN 1 F LGH 1502'       → 'Diagnosvägen 1 F'
      'LAGMANS VÄGEN 11, LGH 1501 våning 5' → 'Lagmansvägen 11'
      'SJÖDALSBACKEN 9 LGH 1304 3 trappor'  → 'Sjödalsbacken 9'
      'BOTKYRKAVÄGEN 9 LGH 1606 MOSHE L EISHO' → 'Botkyrkavägen 9'
      'SOLFAGRAVÄGEN 93,'                → 'Solfagravägen 93'
      'STAMBANEVÄGEN 28 Våning 2'        → 'Stambanevägen 28'
    """
    s = gata.strip()
    if not s:
        return s

    # Cut at LGH, Lgh, våning, Våning, trappor (case-insensitive)
    s = re.split(r'[,;]\s*$|[,;]?\s*(?:LGH|lgh|Lgh|våning|Våning|VÅNING|trappor|TRAPPOR)\b', s)[0].strip()

    # Remove trailing comma
    s = s.rstrip(',').strip()

    # Normalize split street names
    for wrong, correct in STREET_NAME_FIXES.items():
        if s.upper().startswith(wrong.upper()):
            rest = s[len(wrong):]  # keep the number + letter suffix
            s = correct + rest
            break

    # Title-case: capitalize first letter of street, keep rest of street as-is
    # but numbers and letter suffixes stay uppercase
    # Simple approach: if still ALL CAPS, convert to title case
    if s == s.upper():
        # Split into street name part and number part
        m = re.match(r'^([A-ZÅÄÖ\s]+?)(\s+\d.*)$', s)
        if m:
            street_part = m.group(1).strip().title()
            number_part = m.group(2)
            s = street_part + number_part
        else:
            s = s.title()

    return s

NEW_COLS = [
    "Column-0", "Slinga", "Starttid", "Längd", "Återkommande", "Dubbel",
    "När på dagen", "Schift", "Besökstyp", "Insatser", "Beskrivning",
    "Kundnr", "Gata", "Postnr", "Ort", "FastOMS", "Slutar", "Före",
    "Efter", "Antal tim mellan besöken", "Kritisk insats Ja/nej"
]


def time_to_minutes(t: str) -> int:
    """Parse HH:MM to minutes since midnight."""
    if not t:
        return 0
    try:
        parts = t.strip().split(":")
        return int(parts[0]) * 60 + (int(parts[1]) if len(parts) > 1 else 0)
    except (ValueError, IndexError):
        return 0


def derive_nar_pa_dagen(starttid: str, besokstyp: str) -> str:
    """Derive 'När på dagen' from start time."""
    if besokstyp.strip() == "Service Insats":
        return ""  # Service visits don't use time-of-day slots
    mins = time_to_minutes(starttid)
    if mins < 660:     # before 11:00
        return "Morgon"
    elif mins < 960:   # 11:00 - 15:59
        return "Lunch"
    else:              # 16:00+
        return "Kväll"


def derive_schift(slinga: str, starttid: str) -> str:
    """
    Derive Schift from Slinga name and time.
    Helg = weekend shifts, Dag = day shifts, Kväll = evening shifts.
    """
    sl = slinga.strip().lower()
    mins = time_to_minutes(starttid)

    if "kväll" in sl:
        return "Kväll"
    elif "helg" in sl:
        if mins < 960:  # before 16:00 → Helg (dag)
            return "Helg"
        return "Kväll"
    elif "vilande" in sl:
        return "Dag"  # default for inactive
    elif mins >= 960:   # 16:00+
        return "Kväll"
    else:
        return "Dag"


WEEKDAY_ORDER = ["mån", "tis", "ons", "tor", "fre", "lör", "sön"]
PINNED_SETS = [
    {"mån", "tis", "ons", "tor", "fre"},
    {"lör", "sön"},
    {"mån", "tis", "ons", "tor", "fre", "lör", "sön"},
]


def _parse_weekdays(aterkammande: str) -> Tuple[List[str], bool]:
    """
    Parse Återkommande to (list_of_weekdays, is_pinned).
    Pinned = complete set (mån-fre, lör-sön, all 7) or "Varje dag".
    """
    s = aterkammande.strip().lower()
    if "varje dag" in s:
        return WEEKDAY_ORDER[:], True

    found = []
    for d in WEEKDAY_ORDER:
        if d in s:
            found.append(d)

    is_pinned = set(found) in PINNED_SETS
    return found, is_pinned


def _is_flexible_day(aterkammande: str) -> bool:
    """True if this visit has solver-picked days (not pinned)."""
    days, pinned = _parse_weekdays(aterkammande)
    return len(days) >= 1 and not pinned


def _visits_per_period(aterkammande: str) -> int:
    """How many visits per period (week/2w/4w) from Återkommande."""
    days, _ = _parse_weekdays(aterkammande)
    return max(len(days), 1)


def derive_antal_tim(client_visits: List[Dict], current_row: Dict) -> str:
    """
    Derive 'Antal tim mellan besöken' following the FSR script logic:

    TWO types of dependencies:
    1. SAME-DAY CHAIN (short, ≤12h): When same client has visits at different
       times of day (Morgon + Lunch, or Lunch + Kväll). Value: "3,5timmar".
       Applied to both the Morgon and Lunch rows.
    2. SPREAD (long, >12h): When the SAME visit row (same insats) recurs N≥2
       times per week with flexible (non-pinned) days. The spread ensures visits
       fall on different days:
       - N=2 visits/period → "48 timmar"
       - N=3 visits/period → "36 timmar"
       - N=4 visits/period → "24 timmar"
       - N=5+ visits/period → "18 timmar" (minimum)
       - N=1 → no spread needed (empty)

    The script checks:
    - If value ≤12h → same-day chain (breakfast→lunch)
    - If value >12h → spread only (same insats, different days)
    """
    besokstyp = current_row.get("Besökstyp", "").strip()
    if besokstyp == "Service Insats":
        return ""

    aterkammande = current_row.get("Återkommande", "").strip()
    starttid = current_row.get("Starttid", "")
    nar = derive_nar_pa_dagen(starttid, besokstyp)

    # ---- SPREAD DEPENDENCY (multi-day, same insats) ----
    # Check if THIS row is a flexible_day visit with N>=2
    # Delays are slightly LESS than the ideal spacing to avoid time-window drift,
    # but long enough to enforce the intended pattern:
    #   N=2 (e.g. 2x/week → ~3.5 days apart): 42h — blocks next-day, no drift risk
    #   N=3 (e.g. 3x/week → ~2.3 days apart): 24h — next-day OK, same-day blocked
    #   N=4 (e.g. 4x/week → ~1.75 days apart): 24h — next-day OK
    #   N=5+ (nearly daily): 18h — just prevent same-day
    if _is_flexible_day(aterkammande):
        n = _visits_per_period(aterkammande)
        if n >= 2:
            if n == 2:
                return "42 timmar"
            elif n <= 4:
                return "24 timmar"
            else:
                return "18 timmar"

    # ---- SAME-DAY CHAIN (short delay, different insats) ----
    # Check if client has visits at multiple times of day (Morgon + Lunch etc.)
    if nar in ("Morgon", "Lunch"):
        has_morning = False
        has_lunch = False
        has_evening = False
        for v in client_visits:
            if v.get("Vilande besök", "").strip():
                continue
            vt = v.get("Starttid", "")
            vn = derive_nar_pa_dagen(vt, v.get("Besökstyp", ""))
            if vn == "Morgon":
                has_morning = True
            elif vn == "Lunch":
                has_lunch = True
            elif vn == "Kväll":
                has_evening = True

        times_count = sum([has_morning, has_lunch, has_evening])
        if times_count >= 2:
            return "3,5timmar"

    return ""


def read_new_csv(path: str) -> Tuple[List[Dict], Set[str]]:
    """Read the enriched 15-client new CSV."""
    rows = []
    clients = set()
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            clients.add(row.get("Kundnr", "").strip())
    return rows, clients


def read_original_csv(path: str) -> List[Dict]:
    """Read the original source CSV."""
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def convert_original_row(row: Dict, client_visits: List[Dict]) -> Dict:
    """Convert one original-format row to new format."""
    starttid = row.get("Starttid", "").strip()
    besokstyp = row.get("Besökstyp", "").strip()
    slinga = row.get("Slinga", "").strip()
    dubbelid = row.get("Dubbelid", "").strip()
    insatser = row.get("Insatser", "").strip()

    nar_pa_dagen = derive_nar_pa_dagen(starttid, besokstyp)
    schift = derive_schift(slinga, starttid)

    # For Dubbelbemanning visits, add "Dubbel" suffix to När på dagen
    if besokstyp == "Dubbelbemanning" and nar_pa_dagen:
        if nar_pa_dagen == "Kväll":
            nar_pa_dagen = "kvällen Dubbel"
        else:
            nar_pa_dagen = f"{nar_pa_dagen} Dubbel"

    antal_tim = derive_antal_tim(client_visits, row)

    return {
        "Column-0": "unchecked",
        "Slinga": slinga,
        "Starttid": starttid,
        "Längd": row.get("Längd", "").strip(),
        "Återkommande": row.get("Återkommande", "").strip(),
        "Dubbel": dubbelid,
        "När på dagen": nar_pa_dagen,
        "Schift": schift,
        "Besökstyp": besokstyp,
        "Insatser": insatser,
        "Beskrivning": row.get("Beskrivning", "").strip(),
        "Kundnr": row.get("Kundnr", "").strip(),
        "Gata": clean_address(row.get("Gata", "")),
        "Postnr": row.get("Postnr", "").strip(),
        "Ort": row.get("Ort", "").strip(),
        "FastOMS": row.get("FastOMS", "").strip(),
        "Slutar": row.get("Slutar", "").strip(),
        "Före": row.get("Min före", "").strip(),
        "Efter": row.get("Min efter", "").strip(),
        "Antal tim mellan besöken": antal_tim,
        "Kritisk insats Ja/nej": "",
    }


def main():
    # Read the enriched 15-client new CSV
    print("Reading enriched new CSV (15 clients)...")
    new_rows, new_clients = read_new_csv(NEW_CSV)
    print(f"  {len(new_rows)} rows, {len(new_clients)} clients")

    # Read the original full source CSV
    print("Reading original source CSV (81 clients)...")
    original_rows = read_original_csv(ORIGINAL_CSV)
    print(f"  {len(original_rows)} rows")

    # Group original rows by client
    client_visits = defaultdict(list)
    for r in original_rows:
        cid = r.get("Kundnr", "").strip()
        client_visits[cid].append(r)

    # Convert the 66 remaining clients
    print("\nConverting 66 remaining clients...")
    converted_rows = []
    converted_clients = set()

    for r in original_rows:
        cid = r.get("Kundnr", "").strip()

        # Skip clients already in the enriched new CSV
        if cid in new_clients:
            continue

        # Skip vilande (inactive) visits
        if r.get("Vilande besök", "").strip():
            continue

        new_row = convert_original_row(r, client_visits[cid])
        converted_rows.append(new_row)
        converted_clients.add(cid)

    print(f"  {len(converted_rows)} rows for {len(converted_clients)} clients")

    # Clean addresses in enriched rows too
    for row in new_rows:
        gata = row.get("Gata", "")
        cleaned = clean_address(gata)
        if cleaned != gata:
            row["Gata"] = cleaned

    # Fix enriched rows: recalculate spread values using same logic as converted rows
    # (prevents drift while keeping same-day chain 3,5timmar untouched)
    spread_fixed = 0
    for row in new_rows:
        atm = row.get("Antal tim mellan besöken", "").strip()
        if atm in ("48 timmar", "36 timmar"):
            ak = row.get("Återkommande", "").strip()
            if _is_flexible_day(ak):
                n = _visits_per_period(ak)
                if n == 2:
                    new_val = "42 timmar"
                elif n <= 4:
                    new_val = "24 timmar"
                else:
                    new_val = "18 timmar"
                if atm != new_val:
                    row["Antal tim mellan besöken"] = new_val
                    spread_fixed += 1
    if spread_fixed:
        print(f"  Fixed {spread_fixed} enriched rows spread values")

    # Combine: enriched 15 clients + converted 66 clients
    all_rows = list(new_rows) + converted_rows
    all_clients = new_clients | converted_clients
    print(f"\nTotal: {len(all_rows)} rows, {len(all_clients)} clients")

    # Write output
    print(f"Writing to {OUTPUT_CSV}...")
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=NEW_COLS, extrasaction='ignore')
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)

    print(f"\nDone! {len(all_rows)} rows written for {len(all_clients)} clients.")

    # Summary per client
    from collections import Counter
    counts = Counter(r.get("Kundnr", "") for r in all_rows)
    for cid, cnt in sorted(counts.items()):
        src = "new" if cid in new_clients else "orig"
        print(f"  {cid}: {cnt} visits ({src})")


if __name__ == "__main__":
    main()
