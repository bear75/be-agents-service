# Seed vs CSV Upload (Attendo Huddinge)

How the **seed script** (`seed-attendo.ts`) and the **dashboard CSV upload** (Upload Schedule Wizard) compare when loading the same Attendo CSV (e.g. `Huddinge-v3 - Data.csv`).

---

## 1. Service area dropdown: why it can be empty

The **Service Area** dropdown in the Upload Schedule Wizard is filled from `serviceAreas(organizationId)`. It is empty when the **current organization has no `ServiceArea` records**.

| How the org was created                      | Service areas                                                                                                        |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **seed-attendo**                             | One: "Huddinge" (with lat/lng, cost/revenue).                                                                        |
| **seed-org-bootstrap** (or Clerk webhook)    | One: "Huvudområde".                                                                                                  |
| **seed-org-defaults** (existing org)         | If the org had **none**, one "Huvudområde" is created when you run `ORGANIZATION_ID=<id> yarn db:seed:org-defaults`. |
| **Org created in Clerk only** (no bootstrap) | None → dropdown empty.                                                                                               |

**Ways to get at least one service area:**

1. **Run seed for that org**
   - Full demo: `yarn db:seed:attendo` (creates org + "Huddinge" + catalog + schedule from CSV).
   - Catalog + default service area only: `ORGANIZATION_ID=<uuid> yarn db:seed:org-defaults` (creates "Huvudområde" if the org has none).

2. **Create a service area in the UI**  
   Resources → Verksamhetsområden → create one (e.g. "Huddinge").

3. **Import without selecting a service area**  
   When there are no service areas, the wizard treats service area as optional (`noServiceAreasAvailable`), so you can leave it empty and still finalize import.

---

## 2. Seed vs CSV upload: what each does

| Aspect              | **seed-attendo.ts**                                                                                              | **Dashboard CSV upload** (finalizeScheduleUpload + importAttendoSchedule)                                                          |
| ------------------- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **Input**           | Same Attendo CSV (e.g. `Huddinge-v3 - Data.csv` in `seed-scripts/attendo/` or `ATTENDO_CSV_PATH`).               | File chosen in wizard; same CSV format (Kundnr, Slinga, Återkommande, Starttid, Längd, Före, Efter, När på dagen, Insatser, etc.). |
| **Organization**    | Creates one org (or uses `CLERK_ORG_ID`).                                                                        | Uses **current user’s organization** (no new org).                                                                                 |
| **Catalog**         | `seedDefaultsForOrganization` → DaySlots, Insets, InsetGroups, Skills.                                           | Not created by upload; org must already have catalog (e.g. from bootstrap or seed-org-defaults).                                   |
| **Service area**    | Creates one "Huddinge" with lat/lng (office).                                                                    | User picks from existing service areas (or skips if none). Financial defaults can be written to the chosen service area.           |
| **Employees**       | From CSV "Slinga"; created/updated by name; linked to service area.                                              | Same: Slinga → employees; created/linked per org.                                                                                  |
| **Clients**         | From CSV "Kundnr"; clients + addresses.                                                                          | Same: Kundnr → Client (externalId = Kundnr), addresses from Gata/Postnr/Ort.                                                       |
| **Schedule period** | Fixed: `SCHEDULE_DAYS = 14`, start from `getScheduleStart()` (env `ATTENDO_SCHEDULE_START_DATE` or next Monday). | User sets in wizard: start date + number of days (or quick 1–12 weeks).                                                            |
| **Visits**          | Recurrence expanded over 14 days; time windows from Starttid/Före/Efter, När på dagen; insets mapped by name.    | Same expansion and mapping; period = configured days.                                                                              |
| **Visit IDs**       | Seed uses its own `externalId` pattern.                                                                          | Upload uses `{kundnr}_r{row}_{occ}` (Attendo/Timefold script format).                                                              |
| **Dependencies**    | "Antal tim mellan besöken" → ClientDependencyRule.                                                               | Same.                                                                                                                              |
| **Shifts**          | From org OperationalSettings + Slinga type (Dag/Kväll/Helg).                                                     | From org OperationalSettings; employees get shifts for schedule days.                                                              |

So: **same CSV, same logical data** (clients, employees, visits, dependencies). Seed creates org + catalog + one service area + full schedule in one go; upload assumes an existing org (and optional catalog/service area) and creates schedule + visits + employees/clients from the file.

---

## 3. Files and commands

| Purpose                                                          | File / command                                                                                                           |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Full Attendo demo (org + catalog + Huddinge + schedule from CSV) | `yarn db:seed:attendo`; optional `ATTENDO_CSV_PATH`, `ATTENDO_SCHEDULE_START_DATE`, `CLERK_ORG_ID`.                      |
| Default catalog + one service area for existing org              | `ORGANIZATION_ID=<uuid> yarn db:seed:org-defaults [--reset]`.                                                            |
| Bootstrap new org (catalog + "Huvudområde")                      | `CLERK_ORG_ID=... ORG_NAME=... ORG_SLUG=... yarn db:seed:org`.                                                           |
| CSV used by seed (default path)                                  | `apps/dashboard-server/src/seed-scripts/attendo/Huddinge-v3 - Data.csv` (or path in repo under `seed-scripts/attendo/`). |
| Upload wizard                                                    | Dashboard → Schedule → Upload; step 2 Configure (service area, period, depot, optional financials).                      |

---

## 4. No duplication when you seed then import the same CSV

If you **seed the DB** with the CSV and later **import the same CSV** via the dashboard (same organization), the import **does not duplicate** shared resources:

| Entity                                          | Behaviour on re-import                                                                                                                                                                  |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Clients**                                     | **Reused.** Lookup by `organizationId + externalId` (Kundnr). Existing client → address updated; missing → created. No duplicate clients.                                               |
| **Employees**                                   | **Reused.** Lookup by `organizationId + externalId` (normalized Slinga name). Existing → coords updated if null; missing → created. No duplicate employees.                             |
| **Insets (catalog)**                            | **Shared.** Import does not create insets; it uses the org’s existing insets (from seed or seed-org-defaults). Same `insetIdMap` (name → id) for seed and upload.                       |
| **ClientDependencyRules**                       | **No duplicate rules.** Before creating a rule we check `clientId + defaultMinDelay`; if it exists we skip. So "Antal tim mellan besöken" is not duplicated per client.                 |
| **Schedule**                                    | **New each time.** Each import creates a **new** schedule (new period). That is intended: you add another schedule, not replace.                                                        |
| **Visits, VisitTemplates, VisitGroups, Shifts** | **New per schedule.** They belong to the new schedule. So you get a new set of visits for the new period; clients and employees are the same records, linked again to the new schedule. |

So: **seed then import same CSV** → same clients, same employees, same catalog (Insets), no duplicate dependency rules; only new schedule + its visits/templates/groups/shifts.

---

## 5. How seed, CSV upload, and input JSON connect (dependencies, insets)

The important chain is: **catalog (Insets) → visits (insetId) → dependencies → Timefold input JSON**.

1. **Catalog (Insets, DaySlots, InsetGroups)**  
   Created once per org by **seed** (seedDefaultsForOrganization). CSV upload **never** creates insets; it loads `insetIdMap` from the org’s existing insets and maps CSV "Insatser" to `insetId`. So seed and upload use the **same** catalog.

2. **Visits**  
   Each visit has `insetId` (and optional `visitTemplateId`). So visit types and dependency logic are tied to the **same** insets the script/Timefold model expect.

3. **Dependencies**
   - **ClientDependencyRule**: "Antal tim mellan besöken" → min delay between visits for a client. Not duplicated on re-import (see table above).
   - **InsetGroup** (e.g. meals: breakfast → lunch → dinner): Used by the projection to build **visitDependencies** in the Timefold payload. So the **input JSON** (modelInput.visits[].visitDependencies) comes from the same insets and groups that seed and CSV import use.

4. **Timefold input JSON**  
   `buildTimefoldModelInput` reads the schedule’s visits (with insetId), employees, shifts, and org’s InsetGroups + ClientDependencyRules, and builds the same shape as the script’s export (visits, visitGroups, vehicles, planningWindow, dependencies). So **seed → same catalog**, **CSV import → same clients/employees + same catalog → same visit/dependency structure → same input JSON**.

---

## 6. Aligning seed and upload

- **Same CSV**: Use the same file (e.g. `Huddinge-v3 - Data.csv`) in both flows for comparable data.
- **Same period**: Set `ATTENDO_SCHEDULE_START_DATE=2026-03-02` for seed and the same start + 14 days in the wizard to match the 2-week seed window.
- **Service area**: Run `db:seed:org-defaults` for the org (or seed-attendo) so the wizard dropdown has at least one option; or create one in Resources.
