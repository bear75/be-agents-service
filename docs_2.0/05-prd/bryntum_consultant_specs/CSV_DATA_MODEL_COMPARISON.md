# CSV Template vs Data Model Comparison

**Date:** 2025-12-15  
**Purpose:** Identify gaps and mismatches between the CSV data requirements template and the actual database schema

---

## Summary

### ✅ Matches Well

- Core visit fields (id, clientId, duration, time windows)
- Employee basic fields (id, name, transport mode)
- Shift and break structure
- Cost and revenue fields
- **Time window approach**: CSV uses `originalStartTime` + `flexibilityMinutes` (user-friendly) → maps to DB `minStartTime`/`maxStartTime`/`maxEndTime` ✅

### ✅ Business Logic (Not in CSV - Applied During Import)

1. **`pinned` flag**: All imported planned schedules are automatically pinned (business logic, not in CSV)
2. **`mandatory` in Timefold**: Visits with longer time window (weekly) than schedule planning window (daily) are mandatory (business logic)
3. **`scheduleId`**: Internal DB field - created during import process (not in CSV)

### ⚠️ Resolved Gaps

1. **Added to CSV:**
   - ✅ `visitStatus` enum (planned, cancelled, completed, missed) - **ADDED**
   - ✅ `requiredStaff` (for double staffing) - **ADDED**

2. **Mapping Clarifications:**
   - `originalStartTime` + `flexibilityMinutes` → `minStartTime`/`maxStartTime`/`maxEndTime` (user-friendly approach)
   - `originalStartTime` + `preferredFlexibilityMinutes` → `preferredTimeWindows` jsonb array (Timefold soft constraints)
   - `contactPerson`: Unique employee per client (different from preferred caregivers)
   - `unusedHours`: Tracked in `monthly_allocations` table (not per-visit in CSV)
   - `visitCategory`/`recurrenceType`: Part of pre-planning - use separate `movable-visits-data-template.csv`

3. **Format Issues:**
   - Format conversions (ISO 8601 → minutes, priority 1-10 → enum) will be handled during import
   - Focus on data completeness, not format precision

4. **Type/Format Mismatches:**
   - CSV: `serviceDuration` (ISO 8601 duration) vs DB: `duration` (integer minutes)
   - CSV: `priority` (String 1-10) vs DB: `priority` (text: low, normal, high, urgent)
   - CSV: `movableFrequency` (string) vs DB: `visit_templates.frequency` (enum)
   - CSV: `continuity` (string: high/medium/low) vs DB: calculated metric in `client_solution_metrics`
   - CSV: Break JSON format vs DB: normalized `employee_breaks` table
   - CSV: Cost JSON format vs DB: `employees.monthlySalary`/`hourlySalary` + `employee_costs` table

---

## Detailed Field Comparison

### Visit Fields

| CSV Field                     | CSV Type    | DB Field                                        | DB Type           | Status            | Notes                                                                                                                   |
| ----------------------------- | ----------- | ----------------------------------------------- | ----------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `visitId`                     | String      | `visits.id`                                     | uuid              | ✅ Match          | External ID can be stored in `externalId`                                                                               |
| `clientId`                    | String      | `visits.clientId`                               | uuid FK           | ✅ Match          | External ID supported                                                                                                   |
| `clientName`                  | String      | `clients.name`                                  | text              | ✅ Match          | Via client relation                                                                                                     |
| `visitDate`                   | Date        | `schedules.date`                                | timestamp         | ⚠️ Indirect       | Visit belongs to schedule                                                                                               |
| `serviceDuration`             | ISO 8601    | `visits.duration`                               | integer (minutes) | ⚠️ Format         | CSV: "PT30M", DB: 30                                                                                                    |
| `originalStartTime`           | ISO 8601    | `visits.minStartTime` (calculated)              | timestamp         | ✅ User-friendly  | CSV user-friendly approach: originalStartTime + flexibilityMinutes → DB minStartTime/maxStartTime/maxEndTime            |
| `flexibilityMinutes`          | Integer     | `visits.minStartTime/maxStartTime` (calculated) | timestamp         | ✅ User-friendly  | Used with originalStartTime to calculate DB time windows                                                                |
| `preferredFlexibilityMinutes` | Integer     | `visits.preferredTimeWindows` (calculated)      | jsonb array       | ✅ User-friendly  | Used with originalStartTime to create preferredTimeWindows (Timefold soft constraint)                                   |
| `skills`                      | CSV string  | `visit_skills.skillName`                        | text[]            | ✅ Match          | Via join table                                                                                                          |
| `serviceAreas`                | CSV string  | `visits.serviceAreaId`                          | uuid FK           | ⚠️ Single         | CSV: multiple, DB: single FK                                                                                            |
| `serviceAreaOfficeLocation`   | lat,lng     | `service_areas.latitude/longitude`              | numeric           | ✅ Match          | Via service area                                                                                                        |
| `priority`                    | String 1-10 | `visits.priority`                               | text enum         | ⚠️ Format         | CSV: "5", DB: "normal"                                                                                                  |
| `mandatory`                   | Boolean     | -                                               | -                 | ✅ Business Logic | Business logic: Visits with longer time window (weekly) than schedule planning window (daily) are mandatory in Timefold |
| `movable`                     | Boolean     | `visits.isMovable`                              | boolean           | ✅ Match          |                                                                                                                         |
| `movableFrequency`            | String      | `visit_templates.frequency`                     | enum              | ⚠️ Location       | In visit_templates table                                                                                                |
| `continuity`                  | String      | `client_solution_metrics.continuityScore`       | numeric           | ⚠️ Location       | Calculated metric, not input                                                                                            |
| `contactPerson`               | String      | `clients.contactPerson`                         | text              | ✅ Match          | Unique employee per client (different from preferred caregivers)                                                        |
| `preferredEmployees`          | CSV string  | `visit_preferences.*`                           | join table        | ⚠️ Structure      | DB uses normalized table                                                                                                |
| `nonPreferredEmployees`       | CSV string  | `visit_preferences.*`                           | join table        | ⚠️ Structure      | DB uses normalized table                                                                                                |
| `unusedHours`                 | Decimal     | `monthly_allocations.unusedHours`               | numeric           | ✅ Match          | Tracked in monthly_allocations table (not per-visit)                                                                    |
| `visitAddress`                | String      | `addresses.street` + `addresses.city`           | text              | ⚠️ Structure      | DB normalized to addresses table                                                                                        |
| `visitLocationLat`            | Decimal     | `addresses.latitude`                            | numeric           | ✅ Match          | Via address relation                                                                                                    |
| `visitLocationLng`            | Decimal     | `addresses.longitude`                           | numeric           | ✅ Match          | Via address relation                                                                                                    |
| `plannedStart`                | ISO 8601    | `visits.plannedStartTime`                       | timestamp         | ✅ Match          |                                                                                                                         |
| `plannedDuration`             | ISO 8601    | `visits.duration`                               | integer           | ⚠️ Format         | Same as serviceDuration                                                                                                 |
| `plannedEmployee`             | String      | `solution_assignments.employeeId`               | uuid FK           | ⚠️ Location       | In solution_assignments table                                                                                           |
| `plannedStatus`               | String      | `visits.visitStatus`                            | text enum         | ⚠️ Format         | DB: planned, cancelled, completed, missed                                                                               |
| `plannedShiftStart`           | ISO 8601    | `employee_shifts.minStartTime`                  | timestamp         | ✅ Match          | Via employee shift                                                                                                      |
| `plannedShiftEnd`             | ISO 8601    | `employee_shifts.maxEndTime`                    | timestamp         | ✅ Match          | Via employee shift                                                                                                      |
| `plannedTravelTimeSeconds`    | Integer     | `solution_assignments.travelTimeSeconds`        | integer           | ✅ Match          | Via solution_assignments                                                                                                |
| `plannedTravelDistanceMeters` | Integer     | `solution_events.distance`                      | numeric           | ⚠️ Location       | In solution_events table                                                                                                |
| `actualStart`                 | ISO 8601    | `solution_events.startTime`                     | timestamp         | ⚠️ Location       | In solution_events table                                                                                                |
| `actualDuration`              | ISO 8601    | `solution_events.duration`                      | integer           | ⚠️ Location       | In solution_events table                                                                                                |
| `actualEmployee`              | String      | `solution_events.employeeId`                    | uuid FK           | ⚠️ Location       | In solution_events table                                                                                                |
| `actualStatus`                | String      | `visits.visitStatus`                            | text enum         | ✅ Match          |                                                                                                                         |
| `actualShiftStart`            | ISO 8601    | `employee_shifts.minStartTime`                  | timestamp         | ✅ Match          | Via employee shift                                                                                                      |
| `actualShiftEnd`              | ISO 8601    | `employee_shifts.maxEndTime`                    | timestamp         | ✅ Match          | Via employee shift                                                                                                      |
| `actualTravelTimeSeconds`     | Integer     | `solution_events.duration`                      | integer           | ⚠️ Location       | In solution_events table                                                                                                |
| `actualTravelDistanceMeters`  | Integer     | `solution_events.distance`                      | numeric           | ⚠️ Location       | In solution_events table                                                                                                |

**Missing in CSV (Business Logic / Internal):**

- `pinned` (boolean) - **Business Logic**: All imported planned schedules are automatically pinned
- `scheduleId` - **Internal DB**: Created during import process (visits belong to schedules)
- `addressId` - **Internal DB**: Normalized address reference (created from visitAddress)
- `movableVisitId` - **Internal DB**: Link to visit_templates (for movable visits)

**Missing in CSV (Use Separate Template):**

- `visitCategory` - daily, recurring → Use `movable-visits-data-template.csv`
- `recurrenceType` - weekly, bi-weekly, monthly → Use `movable-visits-data-template.csv`

**Added to CSV:**

- ✅ `visitStatus` enum - planned, cancelled, completed, missed
- ✅ `requiredStaff` - for double staffing
- `minStartTime`, `maxStartTime`, `maxEndTime` - hard time window constraints

### Employee Fields

| CSV Field                   | CSV Type    | DB Field                                     | DB Type          | Status       | Notes                                |
| --------------------------- | ----------- | -------------------------------------------- | ---------------- | ------------ | ------------------------------------ |
| `employeeId`                | String      | `employees.id`                               | uuid             | ✅ Match     | External ID in `externalId`          |
| `employeeName`              | String      | `employees.name`                             | text             | ✅ Match     |                                      |
| `employeeShiftId`           | String      | `employee_shifts.id`                         | uuid             | ✅ Match     | External ID in `shiftExternalId`     |
| `employeeShiftMinStartTime` | ISO 8601    | `employee_shifts.minStartTime`               | timestamp        | ✅ Match     |                                      |
| `employeeShiftMaxEndTime`   | ISO 8601    | `employee_shifts.maxEndTime`                 | timestamp        | ✅ Match     |                                      |
| `employeeShiftSkills`       | CSV string  | `employee_skills.skillName`                  | text[]           | ✅ Match     | Via join table                       |
| `employeeShiftTags`         | CSV string  | `employee_tags.tagName`                      | text[]           | ✅ Match     | Via join table                       |
| `employeeShiftBreaksJSON`   | JSON string | `employee_breaks.*`                          | normalized table | ⚠️ Structure | DB uses normalized table             |
| `employeeShiftCostJSON`     | JSON string | `employees.monthlySalary` + `employee_costs` | normalized       | ⚠️ Structure | DB uses normalized fields            |
| `transportType`             | String      | `employees.transportMode`                    | text enum        | ✅ Match     |                                      |
| `revenuePerServiceArea`     | JSON string | `service_areas.revenuePerHour`               | numeric          | ⚠️ Structure | DB: per-hour rate, not per-area JSON |
| `employeeCostMonthly`       | Decimal     | `employees.monthlySalary`                    | numeric(10,2)    | ✅ Match     |                                      |
| `employeeCostPerHour`       | Decimal     | `employees.hourlySalary`                     | numeric(10,2)    | ✅ Match     |                                      |

**Missing in CSV:**

- `status` - active, inactive, on_leave
- `role` - CAREGIVER, DRIVER, COORDINATOR
- `contractType` - full_time, part_time, hourly
- `organizationId` - **REQUIRED** FK
- `scheduleId` - **REQUIRED** for schedule_employees junction
- `scheduleEmployeeId` - **REQUIRED** FK for employee_shifts

---

## Business Logic & Mapping Clarifications

### 1. **`pinned` Flag** ✅ Business Logic

- **Purpose:** Lock visit to specific employee/time (optimizer cannot move)
- **DB Field:** `visits.pinned` (boolean, NOT NULL, default false)
- **Business Logic:** All imported planned schedules are automatically pinned
- **CSV:** Not needed - applied during import

### 2. **`scheduleId`** ✅ Internal DB Field

- **Purpose:** Visits must belong to a schedule instance
- **DB Field:** `visits.scheduleId` (uuid FK, NOT NULL)
- **CSV:** Not needed - schedule created during import, then visits linked

### 3. **Time Window Mapping** ✅ User-Friendly Approach

- **CSV Approach:** `originalStartTime` + `flexibilityMinutes` + `duration` (user-friendly)
- **DB Fields:** `visits.minStartTime`, `visits.maxStartTime`, `visits.maxEndTime` (calculated)
- **Mapping:**
  ```
  minStartTime = originalStartTime - (flexibilityMinutes / 2)
  maxStartTime = originalStartTime + (flexibilityMinutes / 2)
  maxEndTime = maxStartTime + duration
  ```
- **Status:** ✅ Correct approach - CSV is user-friendly, DB stores calculated values

### 4. **`preferredTimeWindows`** ✅ User-Friendly Approach

- **Purpose:** Soft constraints for Timefold (waiting time reduction)
- **DB Field:** `visits.preferredTimeWindows` (jsonb array)
- **CSV Approach:** `originalStartTime` + `preferredFlexibilityMinutes` (user-friendly)
- **Mapping:**
  ```
  preferredTimeWindows = [{
    startTime: originalStartTime - (preferredFlexibilityMinutes / 2),
    endTime: originalStartTime + (preferredFlexibilityMinutes / 2)
  }]
  ```
- **Status:** ✅ Correct approach - CSV is user-friendly, DB stores Timefold format

### 5. **`visitStatus`** ✅ ADDED TO CSV

- **Purpose:** Visit lifecycle status (affects UI color coding)
- **DB Field:** `visits.visitStatus` (text enum: planned, cancelled, completed, missed)
- **CSV:** ✅ Now included as `visitStatus` column
- **Mapping:** Use `visitStatus` directly, or derive from `plannedStatus`/`actualStatus` if needed

### 6. **`mandatory` Flag** ✅ Business Logic

- **Purpose:** Indicates if visit must be scheduled in Timefold
- **Business Logic:** Visits with longer time window (weekly) than schedule planning window (daily) are mandatory
- **CSV:** Included for reference, but business logic determines Timefold mandatory flag

---

## Recommendations

### ✅ Completed Updates

1. ✅ **Added `visitStatus` column** (String enum: planned, cancelled, completed, missed)
2. ✅ **Added `requiredStaff` column** (Integer, default: 1, use 2 for double staffing)
3. ✅ **Clarified `contactPerson`** - Unique employee per client (different from preferred caregivers)
4. ✅ **Clarified time window mapping** - User-friendly `originalStartTime` + `flexibilityMinutes` approach
5. ✅ **Clarified `preferredTimeWindows` mapping** - Uses `originalStartTime` + `preferredFlexibilityMinutes`
6. ✅ **Created `movable-visits-data-template.csv`** - Separate template for pre-planning/movable visits

### For Documentation (Clarify These Mappings)

1. **Time Window Calculation:** ✅ Documented
2. **Preferred Time Windows:** ✅ Documented
3. **Visit Status Mapping:** ✅ Added to CSV
4. **Priority Mapping:** Document conversion (1-10 → enum)
5. **Mandatory Mapping:** ✅ Business logic documented
6. **Service Area Mapping:** Document single FK approach
7. **Break JSON Mapping:** Document normalized table structure
8. **Cost JSON Mapping:** Document normalized fields structure

### For Documentation (Clarify These Mappings)

1. **Time Window Calculation:**

   ```
   CSV: originalStartTime + flexibilityMinutes (±30 min)
   → DB: minStartTime = originalStartTime - flexibilityMinutes/2
        maxStartTime = originalStartTime + flexibilityMinutes/2
        maxEndTime = maxStartTime + duration
   ```

2. **Preferred Time Windows:**

   ```
   CSV: preferredFlexibilityMinutes (single value)
   → DB: preferredTimeWindows = [{startTime: originalStartTime - preferredFlexibilityMinutes/2,
                                   endTime: originalStartTime + preferredFlexibilityMinutes/2}]
   ```

3. **Visit Status Mapping:**

   ```
   CSV: plannedStatus + actualStatus
   → DB: visitStatus =
        - If actualStatus exists: actualStatus (COMPLETED, CANCELLED, NO_SHOW, EXTRA)
        - Else if plannedStatus exists: plannedStatus (PLANNED, CONFIRMED)
        - Else: "planned" (default)
   ```

4. **Priority Mapping:**

   ```
   CSV: priority (String 1-10)
   → DB: priority =
        - 1-3: "urgent"
        - 4-6: "high"
        - 7-8: "normal"
        - 9-10: "low"
   ```

5. **Mandatory Mapping:**

   ```
   CSV: mandatory (Boolean)
   → DB: Derived from priority ("urgent" = mandatory) OR visitStatus
   ```

6. **Service Area Mapping:**

   ```
   CSV: serviceAreas (comma-separated: "Farsta,Tallkrogen")
   → DB: visits.serviceAreaId = first service area (single FK)
        Additional areas via visit_tags table
   ```

7. **Break JSON Mapping:**

   ```
   CSV: employeeShiftBreaksJSON (JSON string)
   → DB: Normalized to employee_breaks table
        - id → employee_breaks.id
        - type → employee_breaks.breakType
        - minStartTime → employee_breaks.minStartTime
        - maxEndTime → employee_breaks.maxEndTime
        - duration → employee_breaks.duration (ISO 8601)
        - costImpact → employee_breaks.costImpact
   ```

8. **Cost JSON Mapping:**
   ```
   CSV: employeeShiftCostJSON (JSON string)
   → DB:
        - fixedCost → employees.monthlySalary
        - rates[].costPerUnit → employees.hourlySalary
        Additional cost structure in employee_costs table
   ```

---

## Action Items

### ✅ Completed

1. ✅ **Added `visitStatus` column** - Required for UI color coding
2. ✅ **Added `requiredStaff` column** - For double staffing feature
3. ✅ **Documented time window calculation** - User-friendly CSV approach → DB format
4. ✅ **Documented preferredTimeWindows mapping** - User-friendly CSV approach → DB format
5. ✅ **Clarified business logic** - Pinned, mandatory, scheduleId are internal/business logic
6. ✅ **Created movable visits CSV template** - Separate template for pre-planning data

### Remaining (Documentation Only)

7. ⚠️ **Document priority mapping** - CSV uses 1-10, DB uses enum (format conversion during import)
8. ⚠️ **Document service area mapping** - CSV allows multiple, DB uses single FK (first area used)
9. ⚠️ **Document break JSON → normalized table mapping** - For reference
10. ⚠️ **Document cost JSON → normalized fields mapping** - For reference

---

## Conclusion

The CSV template is **well aligned** with the database schema after updates:

### ✅ Resolved

1. ✅ **Added `visitStatus`** - Now in CSV template
2. ✅ **Added `requiredStaff`** - Now in CSV template
3. ✅ **Time window approach** - User-friendly CSV (`originalStartTime` + `flexibilityMinutes`) correctly maps to DB (`minStartTime`/`maxStartTime`/`maxEndTime`)
4. ✅ **Preferred time windows** - User-friendly CSV (`originalStartTime` + `preferredFlexibilityMinutes`) correctly maps to DB (`preferredTimeWindows` jsonb array)
5. ✅ **Business logic clarified** - `pinned`, `mandatory`, `scheduleId` are internal/business logic (not in CSV)
6. ✅ **Movable visits** - Separate CSV template created for pre-planning data

### 📋 CSV Templates Available

1. **`data-requirements-template.csv`** - For regular scheduled visits (planned/actual)
2. **`movable-visits-data-template.csv`** - For pre-planning/movable visits (from PDF extraction)

---

## Movable Visits Template Fields (PDF Extraction)

The `movable-visits-data-template.csv` includes additional client and contact information extracted from municipality PDF orders ("Underlag för beräkning av hemtjänsttimmar"). These fields are specific to pre-planning/movable visits workflows.

### Client Information Fields (from PDF)

| CSV Field               | CSV Type             | DB Field                                   | DB Type          | Status            | Notes                                                   |
| ----------------------- | -------------------- | ------------------------------------------ | ---------------- | ----------------- | ------------------------------------------------------- |
| `clientPersonnummer`    | String (YYMMDD-XXXX) | `clients.ssn`                              | text (encrypted) | ✅ Match          | Social security number from PDF                         |
| `clientAddress`         | String               | `clients.address` or `addresses.street`    | text             | ✅ Match          | Full address from PDF                                   |
| `clientPortkod`         | String               | `addresses.metadata` or `clients.metadata` | jsonb            | ⚠️ Metadata       | Door code - may be stored in metadata or notes          |
| `clientPhone`           | String               | `clients.phone`                            | text             | ✅ Match          | Home phone from PDF                                     |
| `clientMobilnummer`     | String               | `clients.metadata` or separate field       | jsonb/text       | ⚠️ Metadata       | Mobile phone - may need metadata storage                |
| `clientCivilstand`      | String               | `clients.metadata`                         | jsonb            | ⚠️ Metadata       | Marital status (Änka, Gift, etc.) - stored in metadata  |
| `clientLanguage`        | String               | `clients.languagePreference`               | text             | ✅ Match          | Preferred language from PDF                             |
| `clientAktuelSituation` | String (multi-line)  | `clients.notes` or `clients.metadata`      | text/jsonb       | ⚠️ Notes/Metadata | Full situation assessment - may be in notes or metadata |

### Order/Municipality Information

| CSV Field            | CSV Type | DB Field                                         | DB Type    | Status      | Notes                                                               |
| -------------------- | -------- | ------------------------------------------------ | ---------- | ----------- | ------------------------------------------------------------------- |
| `orderNumber`        | String   | `visit_templates.metadata` or `clients.metadata` | jsonb      | ⚠️ Metadata | Beställningsnummer - stored in metadata                             |
| `orderDate`          | Date     | `visit_templates.metadata` or `clients.metadata` | jsonb      | ⚠️ Metadata | Order creation date - stored in metadata                            |
| `handlaggare`        | String   | `clients.metadata` or `clients.contactPerson`    | jsonb/text | ⚠️ Metadata | Municipality case worker name - may be in metadata or contactPerson |
| `handlaggareTelefon` | String   | `clients.metadata` or `clients.contactPhone`     | jsonb/text | ⚠️ Metadata | Case worker phone - may be in metadata or contactPhone              |

**Note:** `handlaggare` (municipality case worker) is different from `clients.contactPerson` (caregiver employee). The municipality case worker is the kommun person who manages the order, while `contactPerson` is the designated caregiver for the client.

### External Contacts (Närstående)

| CSV Field              | CSV Type | DB Field                                               | DB Type | Status       | Notes                                                     |
| ---------------------- | -------- | ------------------------------------------------------ | ------- | ------------ | --------------------------------------------------------- |
| `contactRelation`      | String   | `client_contacts.relation`                             | text    | ✅ Match     | Relation to client (Dotter, Son, Vän, etc.)               |
| `contactName`          | String   | `client_contacts.name`                                 | text    | ✅ Match     | External contact full name                                |
| `contactTelefonHem`    | String   | `client_contacts.phone` or `client_contacts.phoneHome` | text    | ⚠️ Structure | Home phone - structure depends on client_contacts table   |
| `contactTelefonArbete` | String   | `client_contacts.phoneWork`                            | text    | ⚠️ Structure | Work phone - structure depends on client_contacts table   |
| `contactMobilnummer`   | String   | `client_contacts.mobile`                               | text    | ⚠️ Structure | Mobile phone - structure depends on client_contacts table |
| `contactEmail`         | String   | `client_contacts.email`                                | text    | ✅ Match     | Contact email                                             |

**Note:** External contacts (närstående) are stored in the `client_contacts` table (1→N relationship from `clients`). Multiple contacts can exist per client. In CSV format, contacts can be:

1. **Separate rows** - One row per contact (with same client/visit data)
2. **JSON format** - Array of contacts in a single field (if CSV parser supports)
3. **Comma-separated** - Multiple contacts in comma-separated format

### Visit Template Fields (Movable Visits)

| CSV Field                   | CSV Type | DB Field                                     | DB Type       | Status      | Notes                                      |
| --------------------------- | -------- | -------------------------------------------- | ------------- | ----------- | ------------------------------------------ |
| `visitTitle`                | String   | `visit_templates.name`                       | text          | ✅ Match    | Visit type (Morgon, Lunchtid, Städ, etc.)  |
| `visitCategory`             | Enum     | `visit_templates.category`                   | enum          | ✅ Match    | daily or recurring                         |
| `frequencyPeriod`           | Enum     | `visit_templates.frequency`                  | enum          | ✅ Match    | week, month, year                          |
| `daysInPeriod`              | Integer  | `visit_templates.daysInPeriod`               | integer       | ✅ Match    | Days/occurrences in period                 |
| `occasionsDay`              | Integer  | `visit_templates.occasionsDay`               | integer       | ✅ Match    | Occasions per day (07:00-22:00)            |
| `occasionsNight`            | Integer  | `visit_templates.occasionsNight`             | integer       | ✅ Match    | Occasions per night (22:00-07:00)          |
| `durationMinutes`           | Integer  | `visit_templates.duration`                   | integer       | ✅ Match    | Duration in minutes                        |
| `isDubbelbemanning`         | Boolean  | `visit_templates.requiredStaff`              | integer       | ⚠️ Format   | TRUE = 2 staff, FALSE = 1 staff            |
| `validFrom`                 | Date     | `visit_templates.validFrom`                  | date          | ✅ Match    | Order validity period start                |
| `validTo`                   | Date     | `visit_templates.validTo`                    | date          | ✅ Match    | Order validity period end                  |
| `beraknadInsatstidPerManad` | Decimal  | `visit_templates.monthlyHours` or `metadata` | numeric/jsonb | ⚠️ Location | Total hours per month - may be in metadata |
| `dagKvallstimmar`           | Decimal  | `visit_templates.metadata`                   | jsonb         | ⚠️ Metadata | Day + evening hours per month              |
| `dubbelbemanningMinuter`    | Integer  | `visit_templates.metadata`                   | jsonb         | ⚠️ Metadata | Double staffing minutes per month          |
| `nattExklDubbelbemanning`   | Decimal  | `visit_templates.metadata`                   | jsonb         | ⚠️ Metadata | Night hours per month                      |
| `nattbesokAntalPerManad`    | Integer  | `visit_templates.metadata`                   | jsonb         | ⚠️ Metadata | Number of night visits per month           |

### Mapping Notes for Movable Visits Template

1. **Client Metadata Fields:**
   - Fields like `portkod`, `mobilnummer`, `civilstand`, `aktuelSituation` may be stored in `clients.metadata` jsonb field or `clients.notes` text field
   - `handlaggare` and `handlaggareTelefon` (municipality case worker) may be stored in `clients.metadata` or separate fields

2. **External Contacts:**
   - Multiple contacts per client are supported via `client_contacts` table
   - CSV format: Use separate rows for each contact, or JSON array format

3. **Order Information:**
   - `orderNumber` and `orderDate` may be stored in `visit_templates.metadata` or `clients.metadata`

4. **Summary Fields:**
   - PDF summary fields (`beraknadInsatstidPerManad`, `dagKvallstimmar`, etc.) may be stored in `visit_templates.metadata` for reference

### ✅ Status

**CSV templates are ready for consultants to create test data.** All critical fields are included, and business logic mappings are documented. Format conversions (ISO 8601, priority enum, etc.) will be handled during import.

**Movable Visits Template:** Includes all client, contact, and order information extracted from municipality PDFs. Some fields may be stored in `metadata` jsonb fields or `notes` text fields depending on schema implementation.
