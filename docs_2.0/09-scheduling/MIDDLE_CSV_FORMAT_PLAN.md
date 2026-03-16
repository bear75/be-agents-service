# Middle CSV Format - Implementation Plan

**Date**: 2026-03-16
**Purpose**: Create canonical middle CSV format with offline Python preprocessing to simplify upload zone and enable ~2,000 dependency creation

---

## Executive Summary

### Problem

Current Attendo CSV import has complex logic distributed across:

1. **Upload zone** (`attendoToCaire.ts`) - recurrence expansion, dependency creation
2. **Timefold projection** (`buildTimefoldModelInput.ts`) - spread dependency creation at solve-time
3. **Result**: 3,329 dependencies created (87.8% ratio) incorrectly, or 0 dependencies with recent fix

**Root Cause**: "Antal tim mellan besöken" semantics:

- **< 12 hours**: Same-day spread (morning visit → lunch visit on same day)
- **≥ 18 hours**: Cross-day spread (Monday visit → Tuesday visit)

This distinction requires parsing the entire visit pattern (recurrence, weekdays, dates) to determine which visits are on the same day vs consecutive days.

### Solution Architecture

```
Attendo CSV → [Python Preprocessor] → Middle CSV → [Upload Zone] → Caire → DB → Timefold
```

**Benefits**:

1. **Correctness**: ~2,000 dependencies created with proper same-day vs cross-day logic
2. **Debuggability**: Middle CSV is versionable, inspectable, hand-editable
3. **Performance**: Heavy parsing done offline, not during upload
4. **Flexibility**: Middle format can be generated from other sources (not just Attendo)
5. **Simplicity**: Upload zone becomes trivial 1:1 mapping (no recurrence logic)

---

## Phase 1: Middle CSV Format Design

### 1.1 Format Overview

Middle CSV represents **fully expanded visits** with **explicit dependencies**. No recurrence patterns, no complex parsing needed.

**Four CSV files**:

1. `visits.csv` - All visit occurrences (3,793 rows for 14-day window)
2. `dependencies.csv` - All visit dependencies (~2,000 rows)
3. `employees.csv` - Employee shifts (42 rows)
4. `clients.csv` - Client addresses (115 rows)

### 1.2 visits.csv Schema

**Columns** (based on Timefold FSR + Caire format):

| Column                | Type     | Example                        | Description                                |
| --------------------- | -------- | ------------------------------ | ------------------------------------------ |
| `recurring_visit_id`  | string   | `RV-H015-morgon-0`             | Parent recurring visit ID (for grouping)   |
| `visit_id`            | string   | `V-H015-2026-03-16-morgon-0`   | Unique visit ID                            |
| `client_id`           | string   | `H015`                         | Client external ID (Kundnr)                |
| `date`                | ISO date | `2026-03-16`                   | Visit date (YYYY-MM-DD)                    |
| `start_time`          | time     | `08:00`                        | Start time (HH:MM) or empty for flexible   |
| `duration_minutes`    | int      | `30`                           | Service duration                           |
| `time_slot`           | string   | `morgon`                       | Canonical slot (morgon/lunch/kväll/heldag) |
| `flex_before_minutes` | int      | `0`                            | Flexibility before start                   |
| `flex_after_minutes`  | int      | `120`                          | Flexibility after start                    |
| `insets`              | string   | `supervision;personal_hygiene` | Semicolon-separated canonical inset IDs    |
| `is_critical`         | boolean  | `true`                         | Critical task flag                         |
| `priority`            | int      | `8`                            | Priority 1-10                              |
| `group_id`            | string   | `G-H015-2026-03-16-dubbel`     | Visit group ID (double-staffing) or empty  |
| `assigned_employee`   | string   | `Dag_01_Central_1`             | Preferred employee (Slinga) or empty       |
| `shift_type`          | string   | `dag`                          | Shift constraint (dag/helg/kväll)          |

**Row count**: ~3,793 visits for 14-day window (115 clients)

### 1.3 dependencies.csv Schema

| Column                | Type   | Example                      | Description                                       |
| --------------------- | ------ | ---------------------------- | ------------------------------------------------- |
| `dependency_id`       | string | `DEP-H015-sd-0001`           | Unique dependency ID                              |
| `preceding_visit_id`  | string | `V-H015-2026-03-16-morgon-0` | Preceding visit ID                                |
| `succeeding_visit_id` | string | `V-H015-2026-03-16-lunch-0`  | Succeeding visit ID                               |
| `min_delay_hours`     | float  | `3.5`                        | Minimum delay (hours)                             |
| `max_delay_hours`     | float  | ``                           | Maximum delay (hours) or empty                    |
| `dependency_type`     | string | `same_day_spread`            | Type: same_day_spread, cross_day_spread, explicit |

**Dependency Types**:

- `same_day_spread`: Same-day visits with spread delay (< 12 hours)
- `cross_day_spread`: Cross-day visits with spread delay (≥ 18 hours)
- `explicit`: Explicit dependency from CSV or user input

**Row count**: ~2,000 dependencies

- ~1,200 same-day spread (< 12h)
- ~800 cross-day spread (≥ 18h)

### 1.4 employees.csv Schema

| Column                   | Type   | Example            | Description                         |
| ------------------------ | ------ | ------------------ | ----------------------------------- |
| `employee_id`            | string | `Dag_01_Central_1` | Unique employee ID (Slinga)         |
| `first_name`             | string | `Dag`              | First name                          |
| `last_name`              | string | `Central 1`        | Last name                           |
| `shift_type`             | string | `dag`              | Primary shift type (dag/helg/kväll) |
| `shift_start`            | time   | `07:00`            | Shift start time                    |
| `shift_end`              | time   | `15:00`            | Shift end time                      |
| `weekdays`               | string | `0,1,2,3,4`        | Allowed weekdays (0=Mon, 6=Sun)     |
| `break_duration_minutes` | int    | `30`               | Required break duration             |
| `break_window_start`     | time   | `10:00`            | Break window start                  |
| `break_window_end`       | time   | `14:00`            | Break window end                    |

**Shift types** (from existing scripts):

- **Dag**: Mon-Fri 07:00-15:00, break 10:00-14:00 (30min)
- **Helg**: Sat-Sun 07:00-14:30, break 10:00-14:00 (30min)
- **Kväll**: All days 16:00-22:00, no break

### 1.5 clients.csv Schema

| Column            | Type   | Example            | Description                    |
| ----------------- | ------ | ------------------ | ------------------------------ |
| `client_id`       | string | `H015`             | Unique client ID (Kundnr)      |
| `name`            | string | `Peter Andersson`  | Client name (or ID if privacy) |
| `street`          | string | `Ängsnäsvägen 6`   | Street address                 |
| `postal_code`     | string | `14146`            | Postal code (no spaces)        |
| `city`            | string | `HUDDINGE`         | City                           |
| `latitude`        | float  | `59.2334527`       | Geocoded latitude              |
| `longitude`       | float  | `17.9911485`       | Geocoded longitude             |
| `service_area_id` | string | `huddinge_central` | Service area (optional)        |
| `notes`           | string | `Har kateter...`   | Client notes (optional)        |

---

## Phase 2: Python Preprocessor Design

### 2.1 Architecture

```
attendo_to_middle.py
├── parse_attendo_csv()        # Read Attendo CSV
├── expand_recurrence()         # Varje vecka → actual dates
├── calculate_time_windows()    # När på dagen + Skift + Före/Efter → flex minutes
├── create_dependencies()       # Antal tim mellan → same-day vs cross-day deps
├── geocode_addresses()         # Address → lat/lon (with cache)
└── write_middle_csvs()         # Output 4 CSV files
```

### 2.2 Key Functions

#### 2.2.1 expand_recurrence()

**Input**: Attendo row with "Återkommande" pattern
**Output**: List of visit dates

**Logic** (from existing `csv_to_fsr.py`):

```python
def expand_recurrence(row, planning_start, planning_end):
    """
    Expand recurrence pattern to actual dates.

    Patterns:
    - "Varje dag" → all days in window
    - "Varje vecka, mån tis ons tor fre" → Mon-Fri in window
    - "Varje vecka, lör sön" → Sat-Sun in window
    - "Varannan vecka, ons" → Every other Wed
    - "Var 3:e vecka, tor" → Every 3rd Thu
    - "Var 4:e vecka, fre" → Every 4th Fri
    """
    atterkommande = row["Återkommande"].strip()
    recurrence_type = parse_recurrence_type(atterkommande)
    weekdays = parse_weekdays(atterkommande)

    if recurrence_type == "daily":
        return all_dates_in_window(planning_start, planning_end)
    elif recurrence_type == "weekly":
        return weekly_dates(planning_start, planning_end, weekdays)
    elif recurrence_type == "biweekly":
        return biweekly_dates(planning_start, planning_end, weekdays)
    # ... etc
```

**Existing reference**: `_expand_row_to_occurrences()` in `csv_to_fsr.py:417-500`

#### 2.2.2 calculate_time_windows()

**Input**: Row with "När på dagen", "Skift", "Starttid", "Före", "Efter", "Kritisk insats"
**Output**: (start_time, flex_before_minutes, flex_after_minutes)

**Logic** (from existing scripts + SUMMARY.md):

```python
def calculate_time_windows(row):
    """
    Calculate time window flex from CSV signals.

    Cases (from SUMMARY.md):
    1. "Exakt dag/tid" in När på dagen → exact time, 1-min flex
    2. Empty Före/Efter → full slot from När på dagen + Skift
    3. Explicit 0,0 Före/Efter → exact time, 1-min flex
    4. Non-zero Före/Efter → Starttid ± före/efter
    """
    när_på_dagen = row["När på dagen"].strip().lower()
    starttid = row["Starttid"]
    före_raw = row["Före"].strip()
    efter_raw = row["Efter"].strip()
    kritisk = row["Kritisk insats Ja/nej"].strip().lower() == "ja"

    # Case 1: Exakt dag/tid
    if "exakt" in när_på_dagen:
        return (starttid, 1, 1)  # minimal flex

    # Case 2: Empty Före/Efter
    if före_raw == "" and efter_raw == "":
        if kritisk:
            return (starttid, 1, 1)  # critical → minimal flex
        else:
            # Full slot from när_på_dagen
            slot = map_slot(när_på_dagen, row["Skift"])
            return calculate_full_slot_flex(slot, starttid)

    # Case 3: Explicit 0,0
    if före_raw == "0" and efter_raw == "0":
        return (starttid, 1, 1)

    # Case 4: Non-zero
    före = parse_int(före_raw, 0)
    efter = parse_int(efter_raw, 0)
    return (starttid, före, efter)
```

**Existing reference**: `csv_to_fsr.py:10-28` (time window cases)

#### 2.2.3 create_dependencies()

**Input**: Expanded visits with "Antal tim mellan besöken"
**Output**: List of dependencies

**Logic** (NEW - this is where the bug was):

```python
def create_dependencies(visits):
    """
    Create dependencies based on spread hours.

    Rules:
    - < 12 hours: Same-day spread (find other visits for client on same day)
    - ≥ 18 hours: Cross-day spread (create chain between consecutive days)
    - Empty: No dependency
    """
    dependencies = []

    # Group visits by client
    visits_by_client = defaultdict(list)
    for visit in visits:
        visits_by_client[visit["client_id"]].append(visit)

    for client_id, client_visits in visits_by_client.items():
        # Sort by date, then start time
        client_visits.sort(key=lambda v: (v["date"], v["start_time"]))

        for i, visit in enumerate(client_visits):
            spread_hours = visit["spread_hours"]  # from "Antal tim mellan"
            if not spread_hours:
                continue

            if spread_hours < 12:
                # Same-day spread: find other visits on same day
                same_day_visits = [v for v in client_visits if v["date"] == visit["date"]]
                for other in same_day_visits:
                    if other == visit:
                        continue
                    # Create same-day dependency
                    dependencies.append({
                        "preceding_visit_id": visit["visit_id"],
                        "succeeding_visit_id": other["visit_id"],
                        "min_delay_hours": spread_hours,
                        "dependency_type": "same_day_spread"
                    })

            elif spread_hours >= 18:
                # Cross-day spread: chain to next day occurrence
                if i < len(client_visits) - 1:
                    next_visit = client_visits[i + 1]
                    dependencies.append({
                        "preceding_visit_id": visit["visit_id"],
                        "succeeding_visit_id": next_visit["visit_id"],
                        "min_delay_hours": spread_hours,
                        "dependency_type": "cross_day_spread"
                    })

    return dependencies
```

**Expected output**: ~2,000 dependencies

- ~1,200 same-day spread (clients with 2-3 visits/day, 3.5h delay)
- ~800 cross-day spread (clients with daily visits, 18-48h delay)

#### 2.2.4 map_time_slot()

**Input**: "När på dagen" + "Skift"
**Output**: Canonical time slot

**Logic** (from existing `aliasMaps.ts` + scripts):

```python
SLOT_ALIASES = {
    "morgon": ["morgon", "MORGON", "Morgon", "förmiddag", "Förmiddag"],
    "lunch": ["lunch", "LUNCH", "Lunch", "middag", "Middag"],
    "kväll": ["kväll", "KVÄLL", "Kväll", "kvällen", "natt"],
    "heldag": ["heldag", "", None],  # Empty = heldag
}

def map_time_slot(när_på_dagen, skift):
    """Map Swedish slot + shift to canonical slot."""
    slot = när_på_dagen.strip().lower()

    # Direct mapping
    if slot in ["morgon", "förmiddag"]:
        return "morgon"
    elif slot in ["lunch", "middag"]:
        return "lunch"
    elif slot in ["kväll", "kvällen", "natt"]:
        return "kväll"
    elif slot == "" or "exakt" in slot:
        # Use shift to infer slot
        if "helg" in skift.lower():
            return "morgon"  # Helg shift is 07:00-14:30 (morning)
        elif "kväll" in skift.lower():
            return "kväll"
        else:
            return "heldag"  # Default
    else:
        return "heldag"
```

#### 2.2.5 map_insets()

**Input**: "Insatser" (semicolon-separated Swedish terms)
**Output**: Canonical inset IDs

**Logic** (from existing `aliasMaps.ts`):

```python
INSET_ALIASES = {
    "supervision": ["Tillsyn", "TILLSYN", "tillsyn"],
    "personal_hygiene": ["Personlig hygien", "personlig_hygien"],
    "bath_shower": ["Bad/Dusch", "bad_dusch", "Bad", "Dusch"],
    "meal": ["Måltid", "måltid", "Mat"],
    "medication": ["Medicinering", "medicinering", "Medicin"],
    "cleaning": ["Städ", "städ", "Städning"],
    "laundry": ["Tvätt", "tvätt"],
    "shopping": ["Inköp", "inköp", "Shopping"],
    "escort": ["Ledsagning", "ledsagning"],
    "other": ["Övrigt", "övrigt", "Annat"],
}

def map_insets(insatser_str):
    """Map Swedish insets to canonical IDs."""
    insets = []
    for swedish_term in insatser_str.split(";"):
        canonical = resolve_inset(swedish_term.strip(), INSET_ALIASES)
        insets.append(canonical)
    return ";".join(insets)
```

### 2.3 Script Structure

**File**: `apps/dashboard-server/scripts/attendo_to_middle.py`

```python
#!/usr/bin/env python3
"""
Convert Attendo CSV to Middle CSV format.

Usage:
  python attendo_to_middle.py input.csv -o output_dir/ --start-date 2026-03-16 --weeks 2
"""

import argparse
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", help="Attendo CSV file")
    parser.add_argument("-o", "--output-dir", required=True, help="Output directory")
    parser.add_argument("--start-date", default="2026-03-16", help="Planning start date (YYYY-MM-DD)")
    parser.add_argument("--weeks", type=int, default=2, help="Planning window weeks")
    parser.add_argument("--no-geocode", action="store_true", help="Skip geocoding")
    args = parser.parse_args()

    # Parse inputs
    attendo_rows = parse_attendo_csv(args.input_csv)
    planning_start = datetime.fromisoformat(args.start_date)
    planning_end = planning_start + timedelta(weeks=args.weeks)

    # Expand recurrence
    visits = []
    for row in attendo_rows:
        dates = expand_recurrence(row, planning_start, planning_end)
        for date in dates:
            visit = create_visit_row(row, date)
            visits.append(visit)

    # Create dependencies
    dependencies = create_dependencies(visits)

    # Extract employees
    employees = extract_employees(attendo_rows)

    # Extract clients
    clients = extract_clients(attendo_rows, geocode=not args.no_geocode)

    # Write outputs
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    write_csv(output_dir / "visits.csv", visits, VISITS_COLUMNS)
    write_csv(output_dir / "dependencies.csv", dependencies, DEPENDENCIES_COLUMNS)
    write_csv(output_dir / "employees.csv", employees, EMPLOYEES_COLUMNS)
    write_csv(output_dir / "clients.csv", clients, CLIENTS_COLUMNS)

    # Summary
    print(f"✅ Created middle CSV format:")
    print(f"   Visits: {len(visits)}")
    print(f"   Dependencies: {len(dependencies)}")
    print(f"   Employees: {len(employees)}")
    print(f"   Clients: {len(clients)}")
    print(f"   Output: {output_dir}")

if __name__ == "__main__":
    main()
```

---

## Phase 3: Upload Zone Simplification

### 3.1 New Middle CSV Adapter

**File**: `apps/dashboard-server/src/services/schedule/adapters/MiddleAdapter.ts`

```typescript
export class MiddleAdapter extends BaseAdapter {
  async parse(buffer: Buffer): Promise<ParsedScheduleData> {
    // Parse 4 CSV files (visits, dependencies, employees, clients)
    const visits = await this.parseVisits(buffer);
    const dependencies = await this.parseDependencies(buffer);
    const employees = await this.parseEmployees(buffer);
    const clients = await this.parseClients(buffer);

    return {
      sourceType: "MIDDLE",
      summary: {
        clientCount: clients.length,
        employeeCount: employees.length,
        visitCount: visits.length,
        dateRange: this.calculateDateRange(visits),
      },
      rawData: { visits, dependencies, employees, clients },
      validationErrors: [],
      missingFields: [],
      metadata: {},
    };
  }
}
```

### 3.2 Simplified middleToCaire()

**File**: `apps/dashboard-server/src/services/schedule/import/middleToCaire.ts`

```typescript
export function middleToCaire(middleData: MiddleParseResult): {
  payload: CaireImportPayload;
  warnings: ValidationWarning[];
} {
  const warnings: ValidationWarning[] = [];

  // Trivial 1:1 mapping - no parsing needed!
  const clients = middleData.clients.map((row) => ({
    externalId: row.client_id,
    name: row.name,
    address: {
      street: row.street,
      postalCode: row.postal_code,
      city: row.city,
      latitude: parseFloat(row.latitude),
      longitude: parseFloat(row.longitude),
    },
  }));

  const visits = middleData.visits.map((row) => ({
    externalId: row.visit_id,
    clientExternalId: row.client_id,
    date: row.date,
    durationMinutes: parseInt(row.duration_minutes),
    startTime: row.start_time,
    timeSlot: row.time_slot, // Already canonical!
    flexBeforeMinutes: parseInt(row.flex_before_minutes),
    flexAfterMinutes: parseInt(row.flex_after_minutes),
    insets: row.insets.split(";"), // Already canonical!
    groupId: row.group_id || undefined,
    priority: parseInt(row.priority),
    isCritical: row.is_critical === "true",
  }));

  const dependencies = middleData.dependencies.map((row) => ({
    precedingVisitExternalId: row.preceding_visit_id,
    succeedingVisitExternalId: row.succeeding_visit_id,
    minDelay: hoursToISO8601(parseFloat(row.min_delay_hours)),
    maxDelay: row.max_delay_hours
      ? hoursToISO8601(parseFloat(row.max_delay_hours))
      : undefined,
    dependencyType: row.dependency_type as
      | "same_day_spread"
      | "cross_day_spread"
      | "explicit",
  }));

  // No warnings - already validated by Python!
  return { payload: { clients, visits, dependencies }, warnings };
}
```

**Key benefit**: ~300 lines → ~50 lines (no recurrence logic, no parsing)

---

## Phase 4: Testing & Verification

### 4.1 Test with v3 CSV

**Input**: `Huddinge-v3 - Data_final.csv` (115 clients, 664 rows)
**Expected Output**:

- visits.csv: ~3,793 rows (14-day window)
- dependencies.csv: ~2,000 rows
  - ~1,200 same-day spread
  - ~800 cross-day spread
- employees.csv: ~42 rows
- clients.csv: 115 rows

**Verification Steps**:

1. **Run preprocessor**:

   ```bash
   python attendo_to_middle.py Huddinge-v3.csv -o middle_output/ --start-date 2026-03-16 --weeks 2
   ```

2. **Verify dependency count**:

   ```bash
   wc -l middle_output/dependencies.csv
   # Expected: ~2000 lines

   grep "same_day_spread" middle_output/dependencies.csv | wc -l
   # Expected: ~1200 lines

   grep "cross_day_spread" middle_output/dependencies.csv | wc -l
   # Expected: ~800 lines
   ```

3. **Upload via dashboard**:
   - Upload middle CSV (zip with 4 files)
   - Verify validation shows ~2,000 dependencies
   - Finalize import
   - Check DB has correct dependency count

4. **Solve with Timefold**:
   - Submit to Timefold FSR
   - Verify dependency constraints are respected
   - Check continuity (requiredVehicles pools)

### 4.2 Comparison Test

**Compare old vs new**:

| Metric                 | Old (Attendo direct)          | New (Middle CSV)        |
| ---------------------- | ----------------------------- | ----------------------- |
| Dependencies created   | 3,329 (wrong) → 0 (fixed bug) | ~2,000 (correct)        |
| Same-day spread        | 0                             | ~1,200                  |
| Cross-day spread       | 0                             | ~800                    |
| Upload zone complexity | ~500 lines parsing            | ~50 lines mapping       |
| Debuggability          | Opaque (in-memory)            | Transparent (CSV files) |
| Preprocessing time     | N/A                           | ~30 seconds             |

---

## Phase 5: Documentation

### 5.1 User Guide

**File**: `docs/docs_2.0/09-scheduling/MIDDLE_CSV_USER_GUIDE.md`

**Contents**:

1. What is middle CSV format?
2. Why use it vs Attendo CSV?
3. How to prepare middle CSV (Python script)
4. Upload via dashboard
5. Troubleshooting

### 5.2 Developer Guide

**File**: `docs/docs_2.0/09-scheduling/MIDDLE_CSV_DEVELOPER_GUIDE.md`

**Contents**:

1. Middle CSV schema reference
2. Preprocessor architecture
3. Adding new source formats
4. Extending dependency types
5. Custom validation rules

### 5.3 Migration Guide

**File**: `docs/docs_2.0/09-scheduling/ATTENDO_TO_MIDDLE_MIGRATION.md`

**Contents**:

1. Differences between Attendo and Middle formats
2. Migration steps
3. Testing checklist
4. Rollback procedure

---

## Implementation Checklist

### Phase 1: Design ✅

- [x] Define middle CSV schema (visits, dependencies, employees, clients)
- [x] Document time window cases
- [x] Document dependency creation rules
- [x] Create plan document

### Phase 2: Python Preprocessor

- [ ] Extract parsing logic from `csv_to_fsr.py`
- [ ] Implement `expand_recurrence()`
- [ ] Implement `calculate_time_windows()`
- [ ] Implement `create_dependencies()` with same-day vs cross-day logic
- [ ] Implement `map_time_slot()` and `map_insets()`
- [ ] Implement geocoding with cache
- [ ] Write unit tests for each function
- [ ] Integration test with v3 CSV

### Phase 3: Upload Zone Adapter

- [ ] Create `MiddleAdapter.ts`
- [ ] Create `middleToCaire.ts` (trivial mapping)
- [ ] Update `scheduleAdapterFactory.ts` to detect middle CSV
- [ ] Add middle CSV to GraphQL schema
- [ ] Update `parseAndValidateSchedule` mutation
- [ ] Update `previewScheduleImport` mutation
- [ ] Update `finalizeScheduleUpload` mutation

### Phase 4: Testing

- [ ] Test with v3 CSV (115 clients)
- [ ] Verify ~2,000 dependencies created
- [ ] Upload to dashboard and finalize
- [ ] Submit to Timefold and verify solve
- [ ] Compare old vs new dependency counts
- [ ] Performance benchmarks

### Phase 5: Documentation

- [ ] Write MIDDLE_CSV_USER_GUIDE.md
- [ ] Write MIDDLE_CSV_DEVELOPER_GUIDE.md
- [ ] Write ATTENDO_TO_MIDDLE_MIGRATION.md
- [ ] Update UPLOAD_ZONE_ARCHITECTURE.md
- [ ] Update CSV_IMPORT_AND_VALIDATION_BEST_PRACTICES.md

---

## Success Criteria

### Functional

- ✅ ~2,000 dependencies created (vs 0 or 3,329 before)
- ✅ Same-day spread dependencies (~1,200) correctly identify visits on same day
- ✅ Cross-day spread dependencies (~800) correctly chain consecutive days
- ✅ All time windows match Attendo CSV intent (exakt/empty/explicit 0,0)
- ✅ All insets and slots mapped to canonical IDs

### Non-Functional

- ✅ Preprocessing completes in < 1 minute for 115 clients
- ✅ Upload zone code reduced from ~500 → ~50 lines
- ✅ Middle CSV files inspectable and hand-editable
- ✅ No regressions in existing Attendo CSV upload

### Quality

- ✅ 100% unit test coverage for preprocessor functions
- ✅ Integration test passes with v3 CSV
- ✅ Documentation complete (user guide, developer guide, migration guide)
- ✅ Code review approval

---

## Next Steps

1. **Identify all parsing patterns** from existing scripts (csv_to_fsr.py, expand_recurring_visits.py)
2. **Extract dependency creation rules** from SUMMARY.md and CSV_TO_JSON_VERIFICATION.md
3. **Implement preprocessor** with TDD approach
4. **Test with v3 CSV** to verify ~2,000 dependencies
5. **Update upload zone** to support middle CSV format
6. **Document** for users and developers

---

**Status**: Plan created, ready for implementation
**Estimated Effort**: 3-5 days (preprocessor + adapter + testing + docs)
**Risk**: Low (existing logic is well-documented in Python scripts)
