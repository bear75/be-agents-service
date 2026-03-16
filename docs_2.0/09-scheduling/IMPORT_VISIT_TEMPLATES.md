# Import Visit Templates – Script Instructions

This guide explains how to use the **import-visit-templates** script to create or update visit templates from a CSV file and link existing visits to them by visit external ID.

---

## 1. Prerequisites

- **Database:** Dashboard PostgreSQL must be running and migrated.
- **Environment:** From the monorepo root or from `apps/dashboard-server`, ensure `DATABASE_URL` is set (e.g. via `apps/dashboard-server/.env`).
- **Data in DB:** The CSV references existing records:
  - **organizationId** – must match an existing `Organization.id` (UUID).
  - **clientId** – must match an existing `Client.id` (UUID) and that client must belong to the given organization.
  - **visitIds** (optional) – comma-separated **visit external IDs**. Only visits that already have `externalId` set and belong to a schedule in the same organization will be linked.

---

## 2. Running the Script

From the **monorepo root**:

```bash
yarn workspace dashboard-server import-visit-templates <path-to-your-file.csv>
```

Example:

```bash
yarn workspace dashboard-server import-visit-templates ./my-templates.csv
```

From **inside** `apps/dashboard-server`:

```bash
yarn import-visit-templates <path-to-your-file.csv>
```

Using **dotenvx** directly (e.g. if you use a custom env file):

```bash
cd apps/dashboard-server
dotenvx run -f .env -- tsx src/scripts/import-visit-templates.ts ./my-templates.csv
```

The script reads the CSV, validates each row, then for each row either creates a new `VisitTemplate` or updates an existing one (matched by `organizationId` + `externalId`). If the row has a `visitIds` column, it links those visits (by **visit external ID**) to the template by setting their `visitTemplateId`.

---

## 3. CSV Format

### 3.1 Required columns

Every row **must** have these columns (names are **case-insensitive**):

| Column              | Description                                                                                                                            |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **organizationId**  | UUID of the organization that owns the template and the client.                                                                        |
| **clientId**        | UUID of the client this template is for. Must belong to the organization.                                                              |
| **externalId**      | Unique template identifier (e.g. from an external system). Used to upsert: same org + externalId → update; otherwise create.           |
| **frequency**       | Recurrence: `daily`, `weekly`, `bi_weekly`, `monthly`, or `custom`.                                                                    |
| **durationMinutes** | Visit duration in minutes (positive integer).                                                                                          |
| **lifecycleStatus** | One of: `identified`, `user_accepted`, `planned_1st`, `client_preferences`, `planned_client_preferences`, `planned_final`, `exported`. |
| **source**          | One of: `user_manual`, `pattern_detection`, `bulk_import`, `api`.                                                                      |

### 3.2 Optional columns

| Column                | Description                                                                                                                                                                                                      |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **preferredDays**     | Comma-separated weekday names, e.g. `monday,wednesday,friday`. Use lowercase. If the cell contains commas, wrap the value in double quotes.                                                                      |
| **preferredTimeSlot** | Free text (e.g. `morning`, `afternoon`).                                                                                                                                                                         |
| **requiredSkills**    | Comma-separated skill names, e.g. `nursing,cleaning`. Quote if the value contains commas.                                                                                                                        |
| **notes**             | Free-text notes for the template.                                                                                                                                                                                |
| **visitIds**          | Comma-separated **visit external IDs** (not UUIDs). Visits with these `externalId` values in the same organization will have their `visitTemplateId` set to this template. Quote the cell if it contains commas. |

### 3.3 Allowed values (enums)

- **frequency:** `daily` \| `weekly` \| `bi_weekly` \| `monthly` \| `custom`
- **lifecycleStatus:** `identified` \| `user_accepted` \| `planned_1st` \| `client_preferences` \| `planned_client_preferences` \| `planned_final` \| `exported`
- **source:** `user_manual` \| `pattern_detection` \| `bulk_import` \| `api`

Values are matched case-insensitively.

---

## 4. Example CSV

Header row and two data rows:

```csv
organizationId,clientId,externalId,frequency,durationMinutes,lifecycleStatus,source,preferredDays,preferredTimeSlot,requiredSkills,notes,visitIds
550e8400-e29b-41d4-a716-446655440000,6ba7b810-9dad-11d1-80b4-00c04fd430c8,tpl-001,weekly,60,identified,bulk_import,"monday,wednesday,friday",morning,"nursing,cleaning",Weekly home care,"visit-ext-1,visit-ext-2"
550e8400-e29b-41d4-a716-446655440000,6ba7b810-9dad-11d1-80b4-00c04fd430c8,tpl-002,daily,30,user_accepted,user_manual,sunday,,,,Daily visit,
```

Notes:

- **visitIds** in the first row: two visit external IDs. Any visit in that organization with `externalId` equal to `visit-ext-1` or `visit-ext-2` will be linked to the template `tpl-001`.
- Second row has no **visitIds**; the template is created/updated but no visits are linked.
- Cells that contain commas (e.g. `preferredDays`, `requiredSkills`, `visitIds`) are wrapped in double quotes.

A copy of this example (with placeholders) lives at:

`apps/dashboard-server/src/seed-scripts/seed-data/visit-templates-example.csv`

---

## 5. Behaviour Summary

1. **Read CSV** – First row = headers. Column names are matched case-insensitively.
2. **Per row:**
   - Validate required columns and enum values.
   - Resolve organization and client; check client belongs to organization.
   - **Upsert template:** look up by `organizationId` + `externalId`. If found, update; otherwise create.
   - If **visitIds** is non-empty: parse as comma-separated visit external IDs and run `Visit.updateMany` for visits in that organization with `externalId` in the list, setting `visitTemplateId` to the template id.
3. **Output** – Prints counts: templates created, templates updated, visits linked. Validation errors are printed before the summary.

---

## 6. Troubleshooting

| Problem                                                            | What to check                                                                                                                                                                                                                                                |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `organizationId and clientId are required`                         | Ensure the row has non-empty `organizationId`, `clientId`, and **externalId**.                                                                                                                                                                               |
| `externalId is required`                                           | Add an **externalId** column and a value in every row.                                                                                                                                                                                                       |
| `organizationId "…" not found`                                     | Use a valid organization UUID from the dashboard database (e.g. from `Organization` table).                                                                                                                                                                  |
| `clientId "…" not found`                                           | Use a valid client UUID.                                                                                                                                                                                                                                     |
| `client … does not belong to organization …`                       | The client’s `organizationId` must match the CSV’s `organizationId`.                                                                                                                                                                                         |
| `invalid frequency` / `invalid lifecycleStatus` / `invalid source` | Use only the allowed enum values (see section 3.3).                                                                                                                                                                                                          |
| `durationMinutes must be a positive integer`                       | Use a number ≥ 1, no decimals.                                                                                                                                                                                                                               |
| No visits linked                                                   | Visits are matched by **external ID**, not by UUID. Ensure the visit rows in the DB have `externalId` set and that the CSV **visitIds** column contains those exact external IDs. Only visits in schedules that belong to the same organization are updated. |

---

## 7. Quick reference

- **Script:** `apps/dashboard-server/src/scripts/import-visit-templates.ts`
- **Example CSV:** `apps/dashboard-server/src/seed-scripts/seed-data/visit-templates-example.csv`
- **Run:** `yarn workspace dashboard-server import-visit-templates <path-to.csv>`
- **Requires:** `DATABASE_URL` in `apps/dashboard-server/.env` (or equivalent).
