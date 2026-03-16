# Unplanned Schedule with Placeholders - What, Why, and Verification

## What

**Feature:** Import unplanned visits (no employee data) and run optimization using placeholder employees to determine staffing requirements.

**Input:** CSV with visits only - no `employeeId`, `plannedEmployeeId`, or `actualEmployeeId`. Example: [test-import-csv-files/removed_empty_req_rows/unplanned_visits_canonical.csv](../../test-import-csv-files/removed_empty_req_rows/unplanned_visits_canonical.csv)

**Flow:**

1. Import CSV → Schedule created with visits, `scheduleEmployees: []`
2. System adds placeholder employees from pool (or generates them)
3. Run optimization → Timefold assigns visits to placeholders
4. Output: Staffing analysis ("Need X employees, these skills, this coverage")
5. User adds real employees and swaps placeholders before publishing

---

## Why

**Business need:** Organizations plan future schedules (weeks/months ahead) before knowing which employees will work. They need to:

- Understand staffing requirements (how many FTEs, which skills)
- Run optimization to see visit coverage and route feasibility
- Add real employees later when shifts are planned

**Current gap:** Import works, but optimization fails with "Schedule has no available employees" because the mapper blocks the Timefold call when `employees.length === 0`.

**Solution:** Use placeholder employees so optimization runs. Placeholders = generic "Slot 1", "Slot 2" with all skills, full-day shifts. Timefold assigns visits; result shows staffing needs.

---

## Test Data

**File:** `test-import-csv-files/removed_empty_req_rows/unplanned_visits_canonical.csv`

**Characteristics:**

- ~564 visits for 2026-01-01
- Columns: visitId, clientName, visitDate, startTime, duration, skills, serviceArea, address, slingaName
- **No employee columns** - no employeeId, plannedEmployeeId, plannedEmployeeName
- slingaName (e.g. "3 HS 2- Hilde") references loop names, not employee IDs
- Matches SCHEDULE_UNPLANNED format: visitDate, startTime, duration, clientId/clientName, address

**Required for canonical parser:**

- visitDate (e.g. 2026-01-01)
- startTime (ISO: 2026-01-01T07:05:00+01:00)
- duration (minutes: 20, 15, 5)
- clientId OR clientName
- address

---

## Verification Steps

### 1. Import Creates Schedule with Visits, No Employees

```
Given: unplanned_visits_canonical.csv (SCHEDULE_UNPLANNED)
When: User uploads via Upload Schedule CSV modal
Then:
  - Schedule created with visits
  - scheduleEmployees = []
  - No error
```

**Verify:** Check schedule in DB or GraphQL - `schedule.employees` is empty, `schedule.visits` has records.

### 2. Add Placeholders Enables Optimization

```
Given: Schedule with visits, 0 employees
When: User clicks "Add placeholders" or "Generate placeholder employees"
Then:
  - N placeholder employees added to schedule (from pool or generated)
  - Each has shifts covering visit time windows
  - Each has all required skills from visits
```

**Verify:** `schedule.employees.length > 0`, each has `isPlaceholder: true` (or `employee.isPlaceholder`), shifts exist.

### 3. Optimization Runs Successfully

```
Given: Schedule with visits + placeholder employees
When: User clicks "Generate solution"
Then:
  - Timefold API called (no "NO_EMPLOYEES" validation error)
  - Solution created with assignments
  - All visits assigned to placeholder slots
```

**Verify:** Solution appears in Schedule Detail, assignments link visits to schedule employees (placeholders).

### 4. Solution Metrics (Abstracted from Employee Type)

**Principle:** Metrics are abstracted from employee type. Whether placeholder or real, show both aggregate and individual.

```
Given: Solution with assignments (placeholder or real employees)
When: User views solution metrics
Then:
  - Aggregate: "X slots used", "Y service hours", "Skills: A, B, C"
  - Individual: Per-slot metrics by display name ("Lisa Nilsson" or "Slot 101")
  - Same metric structure for placeholder and real - no special-case UI
```

### 5. Swap Placeholder with Real Employee

```
Given: Schedule with placeholder assignments
When: User selects slot, picks real employee, clicks "Fill slot"
Then:
  - ScheduleEmployee.employeeId updated from placeholder to real
  - Assignments unchanged (same visit → same slot)
  - Placeholder released back to pool
```

**Verify:** Assignments still exist, `scheduleEmployee.employee` now shows real employee name.

---

## Test Commands / Manual Verification

```bash
# 1. Start dashboard-server
yarn workspace dashboard-server dev

# 2. Start dashboard
yarn dev:dashboard

# 3. In browser:
#    - Log in
#    - Go to Schedules
#    - Upload unplanned_visits_canonical.csv as SCHEDULE_UNPLANNED
#    - Open schedule detail
#    - Add placeholders (or generate)
#    - Click "Generate solution"
#    - Verify solution appears, visits assigned
```

---

## CSV Format Notes

The test file `unplanned_visits_canonical.csv` may need column alignment with the canonical parser:

- Parser expects `address` as single column - test file has it
- `duration` as number - test file has 20, 15, 5 (numeric)
- `visitDate` as YYYY-MM-DD - parseDate() handles this via `new Date()` fallback
- `startTime` as ISO - test file has full ISO timestamps

If import fails, check that column names match: visitDate, startTime, duration, address, clientName (or clientId).
