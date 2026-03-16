# CSV-to-Timefold Developer Handoff

Developer handoff document for the CSV-to-Timefold upload pipeline. Covers CSV formats, DB mapping, pipeline steps, scripts reference, testing guide, and the FSR+placeholder approach.

## Location

**Pipeline scripts and data** live in `local/test_data_import/` (or `apps/dashboard/test_data_import/` if migrated). Run commands from that directory.

## The 3 CSV Formats

All use semicolon delimiter. All share the same core data but with different column names.

### Column Mapping

| Concept             | Anonymized (v2)              | Huddinge            | Nova                |
| ------------------- | ---------------------------- | ------------------- | ------------------- |
| **Header row**      | Row 3 (rows 1–2 annotations) | Row 1               | Row 1               |
| **Visit ID**        | `visit_id`                   | `visit_id_str`      | `visit_id_str`      |
| **Template ID**     | `movable_visit_id`           | `movablevisitid`    | `movablevisitid`    |
| **Double ID**       | `double_id`                  | `Dubbelid`          | `Dubbelid`          |
| **Route name**      | `Slinga`                     | `Slinga`            | `Slinga`            |
| **Weekday**         | `slinga_weekday`             | `weekday`           | `weekday`           |
| **Start time**      | `original_start_time`        | `originalstarttime` | `originalstarttime` |
| **Planned start**   | `slinga_start_time`          | `Starttid`          | `Starttid`          |
| **Duration (min)**  | `duration`                   | `Längd`             | `Längd`             |
| **Min before**      | `Min_before`                 | `Min före`          | `Min före`          |
| **Min after**       | `Min_after`                  | `Min efter`         | `Min efter`         |
| **Is movable**      | `is_movable`                 | `is_movable`        | `is_movable`        |
| **Frequency**       | `frequency`                  | `frequency`         | `frequency`         |
| **Client ID**       | `client_id`                  | `Kundnr`            | `Kundnr`            |
| **Client lat/lon**  | `client_lat`/`client_lon`    | same                | same                |
| **Office lat/lon**  | `office_lat`/`office_lon`    | same                | same                |
| **Shift start/end** | `shift_start`/`shift_end`    | same                | same                |
| **Shift type**      | `shift_type`                 | `shift_type`        | `shift_type`        |
| **Break config**    | `slinga_break_*`             | same                | same                |
| **Description**     | `description`                | `Beskrivning`       | `Beskrivning`       |
| **Priority**        | `Prio (1-10)`                | `Prio (1-3)`        | `Prio (1-3)`        |
| **Skills**          | `visit_skills`               | `Insatser`          | `Insatser`          |
| **Dormant flag**    | `inactive_visit besök`       | `Vilande besök`     | `Vilande besök`     |
| **Notes**           | `Note`                       | `Notering`          | `Notering`          |
| **Street**          | `Street`                     | `Gata`              | `Gata`              |
| **Postal code**     | `Postal_code`                | `Postnr`            | `Postnr`            |
| **City**            | `City`                       | `Ort`               | `Ort`               |

### Nova-specific (not in Huddinge/Anonymized)

- `Förnamn`, `Efternamn` — client first/last name (DPIA sensitive)
- `NFC` — NFC tag ID
- `Nattkund` — night client flag
- `Flexible_weekly` — flexible weekly visits flag

### Anonymized-specific (not in Huddinge/Nova)

- `slinga_skills` — route-level skills
- `preferred_weekday`, `preferred_start_time`, etc. — preferred scheduling
- `slinga_break_paid` — paid break flag
- `break_address`, `break_lat`, `break_lon` — break location
- `visit_category`, `Inset_type`, `care_contact_person`, `decision_end`, `start_decision`

---

## Two-Stage Pipeline

```
Stage 1 (data prep, per-provider):
  Raw Excel (Attendo/Nova)
    → transform_visits_v2.py (row split, IDs, frequency)
    → geocode_addresses.py (add lat/lon)
    → *_Final_Verified_geocoded.csv

Stage 2 (Timefold, universal):
  *_geocoded.csv (or anonymized_v2.csv)
    → csv_to_timefold_json.py
    → modelInput JSON
    → submit_to_timefold.py (solve)
    → run_from_patch.py (iterate: pin + remove empty vehicles)
    → solution
```

---

## DB Mapping: CSV to CAIRE Prisma Schema

### Key Relationship: `movable_visit_id` → `VisitTemplate`

```
CSV movable_visit_id / movablevisitid  →  VisitTemplate.externalId (NEW)
CSV visit_id / visit_id_str            →  Visit.externalId
Visit.visitTemplateId                  →  VisitTemplate.id (FK)
```

### Full Mapping Table

| CSV Concept     | Anonymized Column         | Huddinge/Nova Column   | DB Model.Field                              | Notes                       |
| --------------- | ------------------------- | ---------------------- | ------------------------------------------- | --------------------------- |
| Template ID     | `movable_visit_id`        | `movablevisitid`       | **VisitTemplate.externalId** (NEW)          | Parent recurring pattern    |
| Visit ID        | `visit_id`                | `visit_id_str`         | **Visit.externalId**                        | Concrete instance           |
| Double ID       | `double_id`               | `Dubbelid`             | **Visit.metadata.doubleId**                 | Tandem visit pairing        |
| Client ID       | `client_id`               | `Kundnr`               | **Client.externalId**                       | Create/lookup               |
| Street          | `Street`                  | `Gata`                 | **Address.street**                          |                             |
| Postal code     | `Postal_code`             | `Postnr`               | **Address.postalCode**                      |                             |
| City            | `City`                    | `Ort`                  | **Address.city**                            |                             |
| Client lat/lon  | `client_lat`/`client_lon` | same                   | **Address.latitude/longitude**              | Decimal(10,7)               |
| Route           | `Slinga`                  | `Slinga`               | **ScheduleEmployeeShift** grouping          | Maps to TF vehicle          |
| Duration        | `duration`                | `Längd`                | **Visit.durationMinutes**                   | Minutes                     |
| Start time      | `original_start_time`     | `originalstarttime`    | **Visit.startTime**                         |                             |
| Time window     | `Min_before`/`Min_after`  | `Min före`/`Min efter` | **Visit.allowedTimeWindowStart/End**        | Calculated                  |
| Is movable      | `is_movable`              | same                   | **Visit.visitCategory**                     | TRUE=recurring, FALSE=daily |
| Frequency       | `frequency`               | same                   | **VisitTemplate.frequency**                 | Maps to VisitFrequency      |
| Weekday         | `slinga_weekday`          | `weekday`              | **Visit.visitDate** (derived)               | Expanded to 14-day          |
| Skills          | `visit_skills`            | `Insatser`             | **VisitSkill.skillName**                    | Comma-separated             |
| Office lat/lon  | `office_lat`/`office_lon` | same                   | **ServiceArea** coordinates                 | Depot location              |
| Shift start/end | `shift_start`/`shift_end` | same                   | **ScheduleEmployeeShift.startTime/endTime** |                             |
| Shift type      | `shift_type`              | same                   | **ScheduleEmployeeShift** metadata          | day/evening/night           |
| Break config    | `slinga_break_*`          | same                   | **ScheduleEmployeeShift** break fields      |                             |
| Priority        | `Prio (1-10)`             | `Prio (1-3)`           | **Visit.priority**                          | Different scales            |
| Notes           | `Note`                    | `Notering`             | **Visit.notes**                             |                             |
| Dormant         | `inactive_visit besök`    | `Vilande besök`        | _(filter on import)_                        | Skip these                  |

### Schema Gaps

1. **double_id / tandem visits** — no dedicated field (use `Visit.metadata`)
2. **Break location** (anonymized: `break_lat`/`break_lon`) — not in schema
3. **Care contact person** (anonymized: `care_contact_person`) — not in Client model

---

## Scripts Reference

| Script                                      | Purpose                                                   |
| ------------------------------------------- | --------------------------------------------------------- |
| `scripts/csv_to_timefold_json.py`           | Convert CSV to Timefold FSR modelInput JSON               |
| `scripts/submit_to_timefold.py`             | POST modelInput to Timefold FSR API                       |
| `scripts/run_from_patch.py`                 | Iterative from-patch (pin visits + remove empty vehicles) |
| `scripts/build_reduced_input.py`            | Build reduced input from solution (used vehicles/shifts)  |
| `scripts/compare_full_vs_from_patch.py`     | Compare two solution outputs                              |
| `scripts/count_doubles_and_reduce_input.py` | Count double_id, optionally reduce input                  |
| `scripts/run_per_day_workaround.py`         | Per-day efficiency check                                  |
| `scripts/upstream/transform_visits_v2.py`   | Raw Excel → CAIRE movable CSV (Stage 1)                   |
| `scripts/upstream/geocode_addresses.py`     | Add lat/lon via Nominatim (Stage 1)                       |
| `scripts/upstream/anonymize-visits-csv.mjs` | Anonymize names in CSV (Stage 1)                          |

---

## Testing Guide (How to Run Outside Repo)

1. **Prerequisites**
   - Python 3.10+
   - `requests` for submit_to_timefold.py
   - `TIMEFOLD_API_KEY` environment variable (or hardcoded fallback in script)
   - Node.js for `anonymize-visits-csv.mjs` (upstream only)

2. **Quick test (anonymized CSV)**

   ```bash
   cd local/test_data_import
   python scripts/csv_to_timefold_json.py data/anonymized/movable_visits_anonymized_v2.csv -o data/anonymized/movable_visits_unplanned_input.json
   python scripts/submit_to_timefold.py data/anonymized/movable_visits_unplanned_input.json --dry-run
   ```

3. **Full pipeline**
   - See `local/test_data_import/docs/PIPELINE.md` for full command sequence.

4. **Format detection**
   - `csv_to_timefold_json.py` auto-detects format from CSV headers.
   - Use `--format anonymized|huddinge|nova` to force a format.

---

## Current Approach: FSR + Placeholder Iteration

**Scope**: Unplanned movable visits only (no planned slingor — out of scope for now).

1. Upload CSV with movable visits
2. Convert to Timefold JSON via `csv_to_timefold_json.py`
3. Create placeholder employees in CAIRE ("Slot 1"…"Slot N", `Employee.isPlaceholder = true`)
4. Submit to FSR with all placeholder shifts + all visits
5. Iterate: solve → from-patch (pin visits + remove empty vehicles) → repeat until no empty vehicles
6. Result: staffing need determined, visits assigned to surviving shifts
7. Swap: manager replaces placeholders with real employees via UI

**The FSR-only dilemma**: Always gives either "shifts with no visits" or "unassigned visits". The from-patch iteration removes empty _vehicles_ but not individual empty _shifts_. Per-day workaround achieves ~83% efficiency with 0 empty shifts (tested).

---

## Long-Term: ESS + FSR Dual Model

1. **ESS**: demand-driven, creates exactly the shifts needed
2. **FSR**: routes visits to ESS-generated shifts
3. **Convergence**: if efficiency below target, iterate (max 2–3 rounds)
4. **Eliminates**: placeholder pool, manual shift guessing, iterative removal

See `docs/docs_2.0/09-scheduling/ess-fsr/ESS_FSR_DUAL_MODEL_ARCHITECTURE.md` for details.

---

## Directory Structure

```
local/test_data_import/
├── scripts/
│   ├── csv_to_timefold_json.py
│   ├── submit_to_timefold.py
│   ├── run_from_patch.py
│   ├── run_per_day_workaround.py
│   ├── build_reduced_input.py
│   ├── compare_full_vs_from_patch.py
│   ├── count_doubles_and_reduce_input.py
│   └── upstream/
│       ├── transform_visits_v2.py
│       ├── geocode_addresses.py
│       └── anonymize-visits-csv.mjs
├── data/
│   ├── anonymized/          # Committed, DPIA-clean
│   ├── attendo/             # GITIGNORED (DPIA)
│   └── nova/                # GITIGNORED (DPIA)
├── docs/
│   ├── PIPELINE.md
│   ├── WHY_TRIM_EMPLOYEES_DILEMMA.md
│   ├── APPROACH_FROM_SOLUTION_PATCH.md
│   ├── PER_DAY_WORKAROUND_EFFICIENCY.md
│   └── README_REDUCED_INPUT.md
└── testing/
    └── schedule_visits_test_data/
```
