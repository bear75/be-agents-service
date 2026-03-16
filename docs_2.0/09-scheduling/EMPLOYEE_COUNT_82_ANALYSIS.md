# Analysis: 82 Employees vs 41 (Input) / 35 (CSV)

## Summary

The `Employee` table shows **82** rows for the organization while:

- **FSR input JSON** (`export-field-service-routing-v1-...-input.json`) has **41 vehicles** (workers).
- **Attendo CSV** (`Huddinge-v3 - Data_final.csv`) has **35 unique** "Slinga" values (caregiver/route names in column 1).

**Conclusion:** 82 ≈ **41 + 41**. The same ~41 logical workers were likely created **twice** under two different **externalId** formats, so upsert did not match and duplicate rows were created.

---

## 1. Counts from the files

| Source                               | Count | Identifier                                                  |
| ------------------------------------ | ----- | ----------------------------------------------------------- |
| FSR input JSON `modelInput.vehicles` | 41    | Vehicle `id` (e.g. `Dag_00_Central_1`, `Dag_01_Central_1`)  |
| CSV unique "Slinga" (column 1)       | 35    | Raw string (e.g. `Dag 01 Central 1`, `Dag 02 ⭐ Central 2`) |

So:

- **41** = workers in the Timefold/script export (underscore IDs).
- **35** = distinct caregiver names in the CSV (spaces, optional ⭐).

---

## 2. Why 82 and not 41 or 35?

The dashboard creates/updates employees via **upsert by `(organizationId, externalId)`** in `scheduleUploadHelpers.upsertEmployees`. The same person is only merged if **externalId** is identical.

So 82 arises if the same logical person appears under **two different externalIds**:

1. **Format A** (e.g. from “Create schedule from Timefold JSON” or script):  
   `Dag_00_Central_1`, `Dag_01_Central_1`, … (underscores, 41 IDs).

2. **Format B** (e.g. from CSV upload / Attendo):  
   `Dag 00 Central 1`, `Dag 01 Central 1`, `Dag 02 ⭐ Central 2`, … (spaces, ⭐; 35 or 41 depending on how names are normalized).

If both flows ran for the same organization:

- First flow creates 41 employees with Format A.
- Second flow uses Format B; lookup by `externalId` finds no match → 41 new rows.
- **Total: 41 + 41 = 82.**

So the 82 rows are consistent with **two imports of the same ~41 people with different externalId conventions** (and possibly one flow using 35 CSV Slinga values and another 41 vehicle IDs, with overlap in count if some CSV names map to the same vehicle set).

---

## 3. CSV naming quirks

The CSV has small variants that can split one person into two “employees”:

- `Kväll 04 ⭐ Flemingsberg` (14 rows) vs `Kväll 04 ⭐Flemingsberg` (2 rows) — space before ⭐.
- `Dag 03⭐ Fullersta` (no space before ⭐) vs possible `Dag 03 ⭐ Fullersta`.

So even with a single CSV import, inconsistent spacing/unicode can increase the number of unique Slinga values and thus the number of employee rows. That can push the total toward 82 if the other import (e.g. JSON) adds 41 with underscore IDs.

---

## 4. Recommendations

1. **Normalize `externalId` when upserting** ✅ _Implemented_  
   Shared `normalizeEmployeeExternalId()` in `utils/normalizeEmployeeExternalId.ts`; used in scheduleUploadHelpers, importAttendoSchedule, seed-attendo, createScheduleFromModelInput. Original guidance:
   - Replace spaces with underscores.
   - Normalize optional symbols (e.g. ⭐) or strip them.
   - Use a single canonical form so “Dag 01 Central 1” and “Dag_01_Central_1” map to the same employee.

2. **Single source of truth for “worker” list**  
   Prefer one flow (e.g. CSV upload **or** Timefold JSON import) to create employees for a given org/schedule, and have the other path only attach to existing employees by the same normalized externalId.

3. **Data cleanup for current 82 rows**
   - Identify pairs that are the same logical person (e.g. same `firstName`/`lastName` or normalized name).
   - Merge or delete duplicates and point `ScheduleEmployee` / related data to the chosen employee.
   - Optionally backfill a canonical `externalId` and use it for future upserts.

4. **CSV parsing**  
   When deriving “Slinga” from CSV, normalize early (trim, normalize space/star) so the same caregiver always yields the same key.

---

## 5. Could the seed be the source?

**Yes.** The Attendo seed can add the first batch of employees; a second batch can then come from Timefold JSON (or CSV upload) with a different `externalId` format.

| Script                    | Creates employees?                                       | externalId                                                            |
| ------------------------- | -------------------------------------------------------- | --------------------------------------------------------------------- |
| **seed-org-bootstrap.ts** | No                                                       | —                                                                     |
| **seed-org-defaults.ts**  | No (only catalog: DaySlots, Insets, Skills, ServiceArea) | —                                                                     |
| **seed-attendo.ts**       | **Yes**                                                  | Raw Slinga from CSV (e.g. `Dag 01 Central 1`, `Helg 03 ⭐ Central 1`) |

- **seed-attendo** builds one employee per unique **Slinga** in the CSV and sets `externalId: slingaName` (no normalization). Default CSV: `seed-scripts/seed-data/Huddinge-v3 - Data-substitute-locations.csv`, which has **43 unique** Slinga values.
- **createScheduleFromTimefoldJson** → `createScheduleFromModelInput` **always creates** new employees (no upsert) with `externalId: vehicle.id` (e.g. `Dag_00_Central_1`).

So:

- **Seed (43) + Create from Timefold JSON (41)** → 43 + 41 = **84** (close to 82; small differences possible if the seed CSV in use had 41 unique Slinga or a couple of employees were removed).
- **Seed (41 from a different CSV) + Timefold JSON (41)** → **82** exactly.

To see if seed was used for this org, check for employees with `metadata.seed === true` or `metadata.slingaName` (seed-attendo sets that). If present, the 82 is explained by **seed + Timefold JSON** (or seed + CSV upload with different Slinga formatting), not only by two uploads.

---

## 6. References

- **Upsert:** `apps/dashboard-server/src/services/schedule/scheduleUploadHelpers.ts` — `upsertEmployees(organizationId, employees)` keys by `emp.shiftName` → `Employee.externalId`.
- **Attendo CSV:** `apps/dashboard-server/src/services/schedule/adapters/AttendoAdapter.ts` — unique employees by `row.Slinga` as-is.
- **FSR input:** `modelInput.vehicles[].id` (e.g. `Dag_00_Central_1`) — used when building Timefold input; `createScheduleFromModelInput` creates employees with this as `externalId`.
- **Seed:** `apps/dashboard-server/src/seed-attendo.ts` — one employee per unique Slinga, `externalId: slingaName`; default CSV has 43 unique Slinga.
