# Reset and reseed (after employee dedup fix)

After applying the `normalizeEmployeeExternalId` fix, reset the dashboard DB and reseed so you can upload the CSV and confirm no duplicate employees.

**These commands destroy all data in the dashboard database.** Run only against a development DB.

## 1. Reset database

From repo root:

```bash
cd apps/dashboard-server
yarn db:reset
```

If Prisma prompts for confirmation, confirm. This drops all tables and re-applies migrations.

## 2. Reseed Attendo (org + catalog + employees + schedule from seed CSV)

```bash
yarn db:seed:attendo
```

Uses `CLERK_ORG_ID` from `.env` (or default attendo-development). Seeds one org with default catalog and employees from `seed-scripts/seed-data/Huddinge-v3 - Data-substitute-locations.csv`. Employees are created with **normalized** `externalId` (e.g. `Dag_01_Central_1`).

## 3. Upload your CSV in the dashboard

1. Open the dashboard, select the same organization.
2. Upload your Attendo CSV (e.g. `Huddinge-v3 - Data_final.csv`) via the schedule upload flow.
3. Finalize the upload.

Employees from the CSV are **upserted by normalized externalId**: "Dag 01 Central 1" and "Dag_01_Central_1" match the same row. You should see **one** employee per logical caregiver (no 82-style duplication).

## 4. Verify

- Resources → Employees: count should match unique Slinga in your CSV (or seed count if you didn’t upload, or the union without duplicates if you did).
- If you later “Create schedule from Timefold JSON”, those vehicles will also match by normalized ID; no extra employee rows.

## Fix reference

- **Shared normalizer:** `apps/dashboard-server/src/utils/normalizeEmployeeExternalId.ts`
- **Used in:** `scheduleUploadHelpers.upsertEmployees`, `importAttendoSchedule`, `seed-attendo.ts`, `createScheduleFromModelInput` (Timefold JSON).
