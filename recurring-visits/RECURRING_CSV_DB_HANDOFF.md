# Recurring Visits: CSV–DB Mapping & From-Patch Flow

Developer handoff for the recurring visits pipeline in `docs_2.0/recurring-visits/`. Focus: CSV column mapping to CAIRE DB, movable visits handling, and from-patch workflow.

**Pipeline location:** `docs_2.0/recurring-visits/huddinge-package/` and `nova/` (Nova reuses Huddinge scripts with column mapping).

---

## 1. Pipeline Overview

```
Source CSV  →  Expanded CSV  →  Input JSON  →  Solve  →  Output JSON
     ↓              ↓                ↓                      ↓
  (no ts)     (timestamped)    (timestamped)          (timestamped)
                                                           ↓
                                                    Metrics  →  from-patch  →  Final metrics
```

| Step | Script | Input | Output |
|------|--------|-------|--------|
| 1. Expand | `expand_recurring_visits.py` (Huddinge) or `expand_nova_recurring_visits.py` (Nova) | Source CSV | Expanded CSV |
| 2. JSON | `csv_to_timefold_fsr.py` + `generate_employees.py` | Expanded CSV + Source CSV | Timefold input JSON |
| 3. Solve | `submit_to_timefold.py` | Input JSON | Output JSON |
| 4. Metrics | `metrics.py` / `solve_report.py` | Output + Input JSON | metrics/\*.json |
| 5. From-patch | `build_from_patch.py` | Output + Input JSON | from-patch payload |
| 6. Re-solve | `submit_to_timefold.py from-patch` | Payload + route-plan-id | from-patch output |

---

## 2. CSV Column Mapping: Huddinge vs Nova

### 2.1 Huddinge Source Format (`Huddinge_recurring_v2.csv`)

**Delimiter:** semicolon (`;`). **Header:** row 1.

| Huddinge Column | Purpose | Used By |
|-----------------|---------|---------|
| `visit_id` | Sequential row ID, weekday ordering for daily visits | expand |
| `recurringVisit_id` | Recurring pattern ID → **VisitTemplate.externalId** | expand, DB |
| `visitGroup_id` | Double-staffing group (Dubbelbemanning) | expand, visit groups |
| `recurringVisit_clientName` | Display name (e.g. H015_1) | Timefold visit name |
| `serviceArea_address` | Depot/office address | — |
| `serviceArea_lat` / `serviceArea_lon` | Depot coordinates | generate_employees |
| `frequency` | daily, weekly x1, biweekly, 4weekly, monthly | expand |
| `occurence` | Empty for most; sometimes used | expand |
| `startTime` | Preferred start (HH:MM) | Timefold time windows |
| `duration` | Visit duration (minutes) | Timefold serviceDuration |
| `flex_beforeStart` | Minutes before start | Timefold minStartTime |
| `flex_afterStart` | Minutes after start | Timefold maxStartTime |
| `recurring_external` | Weekday text (e.g. "Varje vecka, mån") | expand, generate_employees |
| `external_slinga_shiftName` | Route/shift name (e.g. Dag 01 Central 1) | generate_employees (vehicles) |
| `shift_type` | day, evening, helg, inactive | expand (filter), generate_employees |
| `shift_start` / `shift_end` | Shift bounds (HH:MM) | generate_employees |
| `shift_break_duration` | Break minutes | generate_employees |
| `shift_break_minStart` / `shift_break_maxEnd` | Break window | generate_employees |
| `visit_note` | Notes; "INACTIVE" → skip | expand (is_inactive) |
| `visit_type` | e.g. Hemtjänst | — |
| `inset_type` | Care type (e.g. Tillsyn) | Timefold visit name |
| `client_externalId` | Client ID (e.g. H015) → **Client.externalId** | DB |
| `client_addressStreet` | Street | Address |
| `client_addressPostalCdode` | Postal code | Address |
| `client_addressCity` | City | Address |
| `Prio (1-3)` | Priority 1–3 | Visit.priority |
| `client_lat` / `client_lon` | Client coordinates | Timefold visit location |

### 2.2 Nova Source Format (`Nova_Final_Verified_geocoded.csv`)

Nova uses different column names. `expand_nova_recurring_visits.py` maps to Huddinge format before calling `expand_recurring_visits`:

| Nova Column | Maps To Huddinge |
|-------------|------------------|
| `visitid` | `visit_id` |
| `movablevisitid` | `recurringVisit_id` |
| `Dubbelid` | `visitGroup_id` |
| `Slinga` | `external_slinga_shiftName` |
| `weekday` | `recurring_external` (e.g. "Varje vecka, mån") |
| `originalstarttime` | `startTime` |
| `Längd` | `duration` |
| `Min före` | `flex_beforeStart` |
| `Min efter` | `flex_afterStart` |
| `Kundnr` | `client_externalId` |
| `Gata` | `client_addressStreet` |
| `Postnr` | `client_addressPostalCdode` |
| `Ort` | `client_addressCity` |
| `movable_id_str` | `recurringVisit_clientName` |
| `Insatser` | `inset_type` |
| `Vilande besök` | `visit_note` (inactive if set) |
| `office_lat` / `office_lon` | `serviceArea_lat` / `serviceArea_lon` |
| `slinga_break_duration` | `shift_break_duration` |
| `slinga_break_min_start` | `shift_break_minStart` |
| `slinga_break_max_end` | `shift_break_maxEnd` |

Nova-specific columns (not mapped to Huddinge): `Förnamn`, `Efternamn`, `NFC`, `Nattkund`, `Flexible_weekly`.

### 2.3 Expanded CSV (Post-expand)

After expand, each row has:

- `original_visit_id` — sequential ID used as Timefold visit ID
- `week` — 0, 1, …
- `frequency_type` — daily, weekly, biweekly, 4weekly, monthly
- `date` — concrete date (YYYY-MM-DD) for daily
- `minStartTime`, `maxStartTime`, `maxEndTime` — ISO datetime strings

Source columns `visit_id`, `occurence`, `startDate`, `endDate` are removed. All other source columns are preserved.

---

## 3. CSV → CAIRE DB Mapping

### 3.1 Template vs VisitTemplate vs TemplateVisit (distinct concepts)

| Model | Purpose | Maps From CSV |
|-------|---------|---------------|
| **Template** | Slinga (route pattern), e.g. "Dag 01 Central 1" | `external_slinga_shiftName` (for route structure, not per-visit) |
| **TemplateVisit** | Slot in a Template: day offset, start time, duration | Used for planned slingor, not recurring import |
| **VisitTemplate** | Recurring visit pattern per client | `recurringVisit_id` (Huddinge) / `movablevisitid` (Nova) |

**Template + TemplateVisit** = organizational route patterns (Slingor).  
**VisitTemplate + Visit** = recurring visit patterns and their concrete occurrences.

### 3.2 DB Mapping Table

| CSV Concept | Huddinge Column | Nova Column | DB Model.Field |
|-------------|-----------------|-------------|----------------|
| Recurring pattern ID | `recurringVisit_id` | `movablevisitid` | **VisitTemplate.externalId** |
| Concrete visit ID | `original_visit_id` (expanded) | — | **Visit.externalId** |
| Double-staffing group | `visitGroup_id` | `Dubbelid` | **Visit.visitGroupId** |
| Client ID | `client_externalId` | `Kundnr` | **Client.externalId** |
| Street | `client_addressStreet` | `Gata` | **Address.street** |
| Postal code | `client_addressPostalCdode` | `Postnr` | **Address.postalCode** |
| City | `client_addressCity` | `Ort` | **Address.city** |
| Client lat/lon | `client_lat` / `client_lon` | same | **Address.latitude** / **longitude** |
| Route name | `external_slinga_shiftName` | `Slinga` | Template / ScheduleEmployeeShift grouping |
| Duration (min) | `duration` | `Längd` | **Visit.durationMinutes** |
| Start time | `startTime` | `originalstarttime` | **Visit.startTime** (derived) |
| Time window | `flex_beforeStart` / `flex_afterStart` | `Min före` / `Min efter` | **Visit.allowedTimeWindowStart** / **End** |
| Frequency | `frequency` | `frequency` | **VisitTemplate.frequency** (enum) |
| Weekday | `recurring_external` | `weekday` | Used for expand; **Visit.visitDate** derived |
| Priority | `Prio (1-3)` | `Prio (1-3)` | **Visit.priority** |
| Notes | `visit_note` | `Notering` | **Visit.notes** |
| Shift bounds | `shift_start` / `shift_end` | same | **ScheduleEmployeeShift** startTime/endTime |

### 3.3 Schema Gaps (what CSV has but DB does not yet support fully)

1. **VisitTemplate time window fields** — CSV has `startTime`, `flex_beforeStart`, `flex_afterStart`; VisitTemplate only has `preferredTimeSlot` (string).
2. **Break location** — Not in schema (anonymized CSV has break_lat/break_lon).

---

## 4. Movable Visits (Recurring)

### 4.1 Definition

- **Movable** = recurring visit that can be scheduled flexibly within time windows.
- In Huddinge/Nova: all recurring rows are effectively movable (pre-planning assigns dates; solver assigns times and employees).
- `visitGroup_id` ≠ movable; it means double-staffing (2+ employees at same time).

### 4.2 Flow: Recurring Pattern → Concrete Visit

```
CSV recurringVisit_id  →  VisitTemplate (externalId)
     ↓
expand_recurring_visits  →  one row per occurrence (planning window)
     ↓
original_visit_id  →  Visit (externalId), Visit.visitTemplateId → VisitTemplate.id
     ↓
Timefold solve  →  SolutionAssignment (employee, time)
```

### 4.3 Frequency Expansion

| frequency | Expansion | Time Window |
|-----------|-----------|-------------|
| daily | 7 rows per recurringVisit_id (one per weekday), then × weeks | Narrow: date-specific, flex_before/flex_after |
| weekly x1 | 1 occurrence per week | Full week (Mon 07:00 – Sun 22:00) |
| weekly x2, x3, x4 | Multiple per week | Full week |
| biweekly | 1 per 2 weeks | Full 2-week window |
| 4weekly | 1 per 4 weeks | Full 4-week window |
| monthly | 1 per month (4-week window) | Full period |

`recurring_external` (e.g. "Varje vecka, mån") is used for employee/shift weekday assignment, **not** for pinning visit time windows. Weekly+ visits get full-period flex windows.

---

## 5. Visit Groups (Double-Staffing)

- **visitGroup_id** groups visits that need 2+ employees simultaneously.
- In Timefold: `visitGroups` array; each group has `id` and `visits`.
- Grouping in `csv_to_timefold_fsr.py`: by `(visitGroup_id, week, date)` so only same-day visits are grouped (time windows must overlap).
- Solo visits (no visitGroup_id) go to top-level `visits`.
- DB: **Visit.visitGroupId** links visits in the same double-staffing group; **Visit.requiredStaff** = 2 for group members.

---

## 6. From-Patch Flow

### 6.1 Purpose

After initial solve:

1. **Pin** assigned visits (lock good assignments)
2. **End shifts at depot** (remove idle time after last visit)
3. **Remove** empty shifts and empty vehicles
4. **Re-solve** with leaner fleet

### 6.2 Patch Order (build_from_patch.py)

1. Pin all assigned visits: `pinningRequested = true`, `minStartTravelTime` from output
   - Solo visits: `/visits/[id=VISIT_ID]/...`
   - Group visits: `/visitGroups/[id=GROUP_ID]/visits/[id=VISIT_ID]/...`
2. End non-empty shifts at depot: `maxEndTime = metrics.endLocationArrivalTime`
3. Remove shifts with empty itinerary
4. Remove unused vehicles (no visits in any shift)

### 6.3 Usage

```bash
python3 build_from_patch.py --output solve/output.json --input solve/input.json --out from-patch/payload.json
```

**Input is required** when visits are in `visitGroups` (for correct patch paths).

### 6.4 Submit From-Patch

```bash
pnpm timefold submit_to_timefold.py from-patch from-patch/payload.json --route-plan-id <id> --wait --save from-patch/output.json
```

### 6.5 Metrics After From-Patch

Run metrics with `--exclude-inactive` to measure efficiency without inactive/empty time in the denominator:

```bash
python3 metrics.py from-patch/output.json --input solve/input.json --save metrics/ --exclude-inactive
```

---

## 7. Script Locations

| Script | Location |
|--------|----------|
| expand_recurring_visits.py | huddinge-package/scripts/ |
| expand_nova_recurring_visits.py | nova/scripts/ |
| csv_to_timefold_fsr.py | huddinge-package/scripts/ |
| generate_employees.py | huddinge-package/scripts/ |
| calculate_time_windows.py | huddinge-package/scripts/ |
| build_from_patch.py | huddinge-package/scripts/ |
| submit_to_timefold.py | huddinge-package/scripts/ |
| metrics.py | huddinge-package/scripts/ |
| solve_report.py | huddinge-package/scripts/ |

Nova uses `process_nova.py` which calls Nova expand → Huddinge `csv_to_timefold_fsr` and `generate_employees` with `source_format=nova`.

---

## 8. Efficiency Targets

- **Field efficiency** = visit / (visit + travel). Target: **>67.5%** (manual Slingor benchmark).
- **Staffing efficiency** = visit / (shift − break). Includes inactive time unless `--exclude-inactive`.
- **Time equation:** shift = visit + travel + wait + break + idle.

---

*Based on docs_2.0/recurring-visits pipeline (Huddinge, Nova) and CAIRE Prisma schema as of Feb 2026.*
