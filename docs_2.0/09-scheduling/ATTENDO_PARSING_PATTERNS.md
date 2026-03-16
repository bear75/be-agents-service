# Attendo CSV Parsing Patterns

**Source**: Extracted from `/Users/bjornevers_MacPro/HomeCare/be-agent-service/scripts/conversion/csv_to_fsr.py`
**Purpose**: Reference for implementing middle CSV preprocessor

---

## 1. Recurrence Patterns ("Återkommande")

### Pattern Types

| Pattern      | Example                            | Type       | Expansion Logic             |
| ------------ | ---------------------------------- | ---------- | --------------------------- |
| **Daily**    | "Varje dag"                        | `daily`    | All days in planning window |
| **Weekly**   | "Varje vecka, mån tis ons tor fre" | `weekly`   | Mon-Fri each week           |
| **Weekend**  | "Varje vecka, lör sön"             | `weekly`   | Sat-Sun each week           |
| **Biweekly** | "Varannan vecka, ons"              | `biweekly` | Every other Wed             |
| **3-weekly** | "Var 3:e vecka, tor"               | `3weekly`  | Every 3rd Thu               |
| **4-weekly** | "Var 4:e vecka, fre"               | `4weekly`  | Every 4th Fri               |

### Weekday Mapping (Swedish → Python)

```python
OCCURRENCE_WEEKDAY = {
    "mån": 0, "månag": 0, "måndag": 0,    # Monday
    "tis": 1, "tisdag": 1,                # Tuesday
    "ons": 2, "onsdag": 2,                # Wednesday
    "tor": 3, "torsdag": 3,               # Thursday
    "fre": 4, "fredag": 4,                # Friday
    "lör": 5, "lördag": 5,                # Saturday
    "sön": 6, "söndag": 6,                # Sunday
}
```

### Complete Weekday Sets (Pinned vs Flexible)

**Pinned** (create visit on exact weekday):

- Mon-Fri: `{0, 1, 2, 3, 4}`
- Sat-Sun: `{5, 6}`
- All 7 days: `{0, 1, 2, 3, 4, 5, 6}`

**Flexible** (solver picks day within period):

- Partial sets: "mån tis tor", "ons", "tis fre", etc.
- Use period-based time windows

---

## 2. Time Slot Mapping ("När på dagen" + "Skift")

### Canonical Slots

| Slot            | Time Range  | Description                     |
| --------------- | ----------- | ------------------------------- |
| **morgon**      | 07:00-10:00 | Morning (includes förmiddag)    |
| **lunch**       | 11:00-13:30 | Lunch/midday                    |
| **eftermiddag** | 13:30-15:00 | Afternoon (rare)                |
| **middag**      | 16:00-19:00 | Dinner/evening meal             |
| **kväll**       | 19:00-22:00 | Evening                         |
| **heldag**      | 07:00-22:00 | Full day (empty "När på dagen") |

### Shift Types ("Skift")

| Shift        | Days     | Hours       | Break               |
| ------------ | -------- | ----------- | ------------------- |
| **Dag**      | Mon-Fri  | 07:00-15:00 | 10:00-14:00 (30min) |
| **Helg dag** | Sat-Sun  | 07:00-14:30 | 10:00-14:00 (30min) |
| **Kväll**    | All days | 16:00-22:00 | None                |

### Slot + Shift Interaction

When "När på dagen" is empty or "Exakt dag/tid":

- **Helg dag** shift → infer `morgon` slot (07:00-14:30 fits morning)
- **Kväll** shift → infer `kväll` slot
- **Dag** shift + empty → `heldag` (full flexibility)

---

## 3. Time Window Calculation ("Starttid", "Före", "Efter", "Kritisk insats")

### Four Cases (from SUMMARY.md)

| Case                    | CSV Signal                      | Result                             | Flex                 |
| ----------------------- | ------------------------------- | ---------------------------------- | -------------------- |
| **1. Exakt dag/tid**    | "När på dagen" contains "exakt" | Exact Starttid                     | ±1 min               |
| **2. Empty Före/Efter** | Both cells blank                | Full slot OR minimal (if critical) | Slot range OR ±1 min |
| **3. Explicit 0,0**     | Före=0, Efter=0 (explicit)      | Exact time                         | ±1 min               |
| **4. Non-zero**         | Any other values                | Starttid ± före/efter              | Custom               |

### Implementation

```python
def calculate_time_windows(row):
    när_på_dagen = row["När på dagen"].strip().lower()
    starttid = row["Starttid"]  # HH:MM
    före_raw = row["Före"].strip()
    efter_raw = row["Efter"].strip()
    kritisk = row["Kritisk insats Ja/nej"].strip().lower() in ["ja", "true", "1"]

    # Case 1: Exakt dag/tid
    if "exakt" in när_på_dagen:
        return (starttid, 1, 1)

    # Case 2: Empty Före/Efter
    if före_raw == "" and efter_raw == "":
        if kritisk:
            # Critical task with empty före/efter → minimal flex (like Exakt)
            return (starttid, 1, 1)
        else:
            # Non-critical with empty före/efter → full slot
            slot = map_slot(när_på_dagen, row["Skift"])
            slot_start, slot_end = get_slot_range(slot)
            # Calculate flex from starttid to slot boundaries
            flex_before = minutes_between(slot_start, starttid)
            flex_after = minutes_between(starttid, slot_end) - duration_minutes
            return (starttid, flex_before, flex_after)

    # Case 3: Explicit 0,0
    if före_raw == "0" and efter_raw == "0":
        return (starttid, 1, 1)

    # Case 4: Non-zero
    före = parse_int(före_raw)
    efter = parse_int(efter_raw)
    return (starttid, före, efter)
```

### Slot Ranges (for Case 2)

```python
SLOT_RANGES = {
    "morgon":      ("07:00", "10:00"),
    "formiddag":   ("10:00", "11:00"),
    "lunch":       ("11:00", "13:30"),
    "eftermiddag": ("13:30", "15:00"),
    "middag":      ("16:00", "19:00"),
    "kväll":       ("19:00", "22:00"),
    "heldag":      ("07:00", "22:00"),
}
```

---

## 4. Dependency Creation ("Antal tim mellan besöken")

### Spread Hours Semantics

| Hours     | Meaning          | Dependency Type    | Logic                       |
| --------- | ---------------- | ------------------ | --------------------------- |
| **< 12h** | Same-day spread  | `same_day_spread`  | Morning → lunch on SAME day |
| **≥ 18h** | Cross-day spread | `cross_day_spread` | Monday → Tuesday            |
| **Empty** | No spread        | None               | No dependency               |

### Implementation

```python
def create_dependencies(visits):
    """
    Create dependencies based on spread hours.

    Returns list of dependencies with types:
    - same_day_spread: < 12 hours (morning → lunch on same day)
    - cross_day_spread: ≥ 18 hours (Monday → Tuesday)
    """
    dependencies = []

    # Group visits by client
    visits_by_client = defaultdict(list)
    for visit in visits:
        visits_by_client[visit["client_id"]].append(visit)

    for client_id, client_visits in visits_by_client.items():
        # Sort by date, then start time
        client_visits.sort(key=lambda v: (v["date"], v["start_time"] or "00:00"))

        for i, visit in enumerate(client_visits):
            spread_hours = parse_spread_hours(visit["aantal_tim_mellan"])
            if not spread_hours:
                continue

            if spread_hours < 12:
                # Same-day spread: find visits on same day AFTER this one
                same_day_visits = [
                    v for v in client_visits
                    if v["date"] == visit["date"] and v != visit
                ]
                for other in same_day_visits:
                    # Only create dependency if other is later (avoid duplicates)
                    if (other["start_time"] or "00:00") > (visit["start_time"] or "00:00"):
                        dependencies.append({
                            "dependency_id": f"DEP-{client_id}-sd-{len(dependencies)}",
                            "preceding_visit_id": visit["visit_id"],
                            "succeeding_visit_id": other["visit_id"],
                            "min_delay_hours": spread_hours,
                            "max_delay_hours": None,
                            "dependency_type": "same_day_spread",
                        })

            elif spread_hours >= 18:
                # Cross-day spread: chain to next occurrence (any day)
                if i < len(client_visits) - 1:
                    next_visit = client_visits[i + 1]
                    dependencies.append({
                        "dependency_id": f"DEP-{client_id}-cd-{len(dependencies)}",
                        "preceding_visit_id": visit["visit_id"],
                        "succeeding_visit_id": next_visit["visit_id"],
                        "min_delay_hours": spread_hours,
                        "max_delay_hours": None,
                        "dependency_type": "cross_day_spread",
                    })

    return dependencies
```

### Parse Spread Hours

```python
def parse_spread_hours(antal_tim_mellan):
    """
    Parse "Antal tim mellan besöken" to hours (float).

    Formats:
    - "3,5timmar" → 3.5
    - "48" → 48.0
    - "" → None
    """
    if not antal_tim_mellan or antal_tim_mellan.strip() == "":
        return None

    s = antal_tim_mellan.strip().lower()
    # Remove "timmar", "tim", "h" suffix
    s = re.sub(r"(timmar|tim|h)$", "", s).strip()
    # Replace comma with dot (Swedish decimal)
    s = s.replace(",", ".")

    try:
        return float(s)
    except ValueError:
        return None
```

### Expected Counts (v3 CSV)

For Huddinge v3 (115 clients, 14-day window):

- **Total dependencies**: ~2,000
- **Same-day spread** (~1,200):
  - Clients with 2-3 visits/day (breakfast + lunch + dinner)
  - Typical delay: 3-4 hours
- **Cross-day spread** (~800):
  - Clients with daily recurring visits
  - Typical delay: 18-48 hours

---

## 5. Inset Mapping ("Insatser")

### Canonical Inset IDs

| Swedish Term     | Canonical ID       | Category     |
| ---------------- | ------------------ | ------------ |
| Tillsyn          | `supervision`      | Basic care   |
| Personlig hygien | `personal_hygiene` | Basic care   |
| Påklädning       | `dressing`         | Basic care   |
| Bad/Dusch        | `bath_shower`      | Basic care   |
| Måltid           | `meal`             | Meal support |
| Medicinering     | `medication`       | Medical      |
| Städ             | `cleaning`         | Household    |
| Tvätt            | `laundry`          | Household    |
| Inköp            | `shopping`         | Household    |
| Ledsagning       | `escort`           | Social       |
| Övrigt           | `other`            | Other        |

### Implementation

```python
INSET_ALIASES = {
    "supervision": ["Tillsyn", "TILLSYN", "tillsyn"],
    "personal_hygiene": ["Personlig hygien", "personlig_hygien", "Personlig Hygien"],
    "dressing": ["Påklädning", "påklädning"],
    "bath_shower": ["Bad/Dusch", "bad_dusch", "Bad", "Dusch"],
    "meal": ["Måltid", "måltid", "Mat"],
    "medication": ["Medicinering", "medicinering", "Medicin"],
    "cleaning": ["Städ", "städ", "Städning"],
    "laundry": ["Tvätt", "tvätt"],
    "shopping": ["Inköp", "inköp", "Shopping"],
    "escort": ["Ledsagning", "ledsagning"],
    "social_activities": ["Socialt", "socialt", "Aktiviteter"],
    "other": ["Övrigt", "övrigt", "Annat"],
}

def map_insets(insatser_str):
    """
    Map semicolon-separated Swedish insets to canonical IDs.

    Input: "Tillsyn;Personlig hygien;Bad/Dusch"
    Output: "supervision;personal_hygiene;bath_shower"
    """
    if not insatser_str or insatser_str.strip() == "":
        return ""

    insets = []
    for swedish_term in insatser_str.split(";"):
        canonical = resolve_inset(swedish_term.strip(), INSET_ALIASES)
        if canonical:
            insets.append(canonical)

    return ";".join(insets)

def resolve_inset(swedish_term, aliases):
    """Case-insensitive lookup in aliases."""
    normalized = swedish_term.strip()
    for canonical_id, alias_list in aliases.items():
        if normalized in alias_list:
            return canonical_id
    # Fallback: return original (will create yellow warning in validation)
    return normalized.lower().replace(" ", "_")
```

---

## 6. Visit Group ("Dubbel")

### Double-Staffing Logic

When "Dubbel" column is not empty, two employees are required for the visit.

**Group ID format**: `{client_id}_{date_iso}_{dubbel_value}`

Example:

- Client: H015
- Date: 2026-03-16
- Dubbel: "X"
- Group ID: `H015_2026-03-16_X`

All visits with same Group ID are scheduled together.

### Implementation

```python
def create_visit_group_id(client_id, date_iso, dubbel):
    """
    Create visit group ID for double-staffing.

    Returns None if not a group visit.
    """
    if not dubbel or dubbel.strip() == "":
        return None

    return f"{client_id}_{date_iso}_{dubbel.strip()}"
```

---

## 7. Address Normalization and Geocoding

### Street Name Fixes

```python
STREET_NAME_FIXES = {
    "DAL VÄGEN": "Dalvägen",
    "DAMMTORPS VÄGEN": "Dammtorpsvägen",
    "DIAGNOS VÄGEN": "Diagnosvägen",
    # ... (see csv_to_fsr.py:160-176)
}
```

### Normalization Steps

1. Trim whitespace
2. Remove apartment suffixes: "LGH 1002", "VÅN 3", "Lägenhet 4"
3. Collapse spaces before street suffixes: "Ängsnäs vägen" → "Ängsnäsvägen"
4. Apply split-street fixes
5. Remove postal code from end if present

### Geocoding

- Use Nominatim (OpenStreetMap) API
- Cache results (address → lat/lon)
- Rate limit: 1 request/second
- Fallback: Use office coordinates (59.2368721, 17.9942601) if geocoding fails

```python
DEFAULT_OFFICE = [59.2368721, 17.9942601]

def geocode_address(street, postal_code, city):
    address = f"{street}, {postal_code} {city}, Sweden"
    # ... geocode via Nominatim
    # ... if fail, return DEFAULT_OFFICE
```

---

## 8. Employee Shifts ("Slinga")

### Extract Unique Employees

From "Slinga" column, extract unique employee IDs and infer shift type.

**Shift naming patterns**:

- "Dag 01 Central 1" → shift_type: `dag`
- "Helg 03 ⭐ Central 1" → shift_type: `helg`
- "Kväll 02 Nord" → shift_type: `kväll`

### Implementation

```python
def extract_employees(attendo_rows):
    employees = {}

    for row in attendo_rows:
        slinga = row["Slinga"].strip()
        if not slinga or slinga in employees:
            continue

        # Infer shift type from name
        slinga_lower = slinga.lower()
        if "helg" in slinga_lower:
            shift_type = "helg"
            shift_start = "07:00"
            shift_end = "14:30"
            weekdays = "5,6"  # Sat-Sun
        elif "kväll" in slinga_lower or "kvall" in slinga_lower:
            shift_type = "kväll"
            shift_start = "16:00"
            shift_end = "22:00"
            weekdays = "0,1,2,3,4,5,6"  # All days
        else:
            shift_type = "dag"
            shift_start = "07:00"
            shift_end = "15:00"
            weekdays = "0,1,2,3,4"  # Mon-Fri

        employees[slinga] = {
            "employee_id": slinga,
            "first_name": slinga.split()[0] if " " in slinga else slinga,
            "last_name": " ".join(slinga.split()[1:]) if " " in slinga else "",
            "shift_type": shift_type,
            "shift_start": shift_start,
            "shift_end": shift_end,
            "weekdays": weekdays,
            "break_duration_minutes": 30 if shift_type != "kväll" else 0,
            "break_window_start": "10:00" if shift_type != "kväll" else "",
            "break_window_end": "14:00" if shift_type != "kväll" else "",
        }

    return list(employees.values())
```

---

## 9. Planning Window

### Default Window

```python
PLANNING_START_DATE = "2026-03-02"
PLANNING_END_DATE = "2026-03-15"
```

### Adaptive Window

For recurrence patterns like "Var 4:e vecka", extend window to at least 4 weeks.

```python
def calculate_planning_window(attendo_rows, start_date, user_weeks):
    longest_recurrence = 14  # default 2 weeks

    for row in attendo_rows:
        recurrence_type = parse_recurrence_type(row["Återkommande"])
        if recurrence_type == "4weekly":
            longest_recurrence = max(longest_recurrence, 28)
        elif recurrence_type == "3weekly":
            longest_recurrence = max(longest_recurrence, 21)
        elif recurrence_type == "biweekly":
            longest_recurrence = max(longest_recurrence, 14)

    actual_weeks = max(user_weeks, longest_recurrence // 7)
    end_date = start_date + timedelta(weeks=actual_weeks)

    return (start_date, end_date)
```

---

## 10. Summary

### Key Patterns to Implement

1. **Recurrence expansion**: "Varje vecka, mån tis" → list of dates
2. **Time window calculation**: 4 cases (Exakt/Empty/0,0/Non-zero)
3. **Dependency creation**: Same-day (<12h) vs cross-day (≥18h)
4. **Slot mapping**: Swedish → canonical (morgon/lunch/kväll)
5. **Inset mapping**: Swedish → canonical (supervision/meal/cleaning)
6. **Shift inference**: "Dag 01" → dag shift (Mon-Fri 07-15)
7. **Address normalization**: Remove apartment suffixes, fix split streets
8. **Geocoding**: Nominatim with cache and fallback
9. **Visit groups**: "Dubbel" → group ID for double-staffing
10. **Planning window**: Adaptive based on longest recurrence

### Test Data

Use `/Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/Huddinge-v3 - Data_final.csv`:

- 115 clients
- 664 rows (recurring visit templates)
- Expected output: ~3,793 visits, ~2,000 dependencies

---

**Status**: Patterns extracted, ready for preprocessor implementation
**Next**: Implement `attendo_to_middle.py` with TDD approach
