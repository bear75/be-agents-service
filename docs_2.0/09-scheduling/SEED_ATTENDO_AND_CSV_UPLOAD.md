# Attendo seed (catalog only) and schedule CSV upload

## What the Attendo seed does

**Seed = catalog only (strict).** The script `seed-attendo.ts` creates:

1. **Organization** – Attendo Hemtjänst Huddinge (and links to Clerk org via `CLERK_ORG_ID`).
2. **Catalog** – via `seedDefaultsForOrganization(org.id, tx)`:
   - **DaySlots** – e.g. Morgon, Lunch, Kväll (used for “När på dagen” and time windows).
   - **Insets** – care types (Tillsyn, Bad/Dusch, Städ, …) and their names in the org catalog.
   - **InsetGroups** – grouping of insets.
   - **Skills** – skill catalog for the org.
   - **Default inset delays** – ServiceAreaDependencyRule per (service area, inset): meals PT3H30M, tillsyn PT6H, hygien/dusch PT48H, etc. Schedule CSV can override per client via ClientDependencyRule ("Antal tim mellan besöken"); client rules take precedence.
3. **Org member** – one admin user for the org.
4. **OperationalSettings** – default contract, salary, shifts (Dag, Kväll, Helg), working days, travel, etc.
5. **ServiceArea** – e.g. Huddinge (with coordinates, revenue/cost per hour).

It does **not** create:

- Employees
- Clients
- Schedule
- Visits, visit templates, visit groups
- Client dependency rules

**First schedule for that org always comes from CSV upload in the UI.** The Attendo Huddinge CSV changes frequently; if the seed contained schedule data, production/pilot would need daily reseeds. Catalog is stable; schedule data is dynamic and is only imported via upload.

**Local dev flow:** Run `yarn db:seed:attendo` once (or use bootstrap for that org) → then upload the Attendo CSV once in the dashboard. No need to reseed when the CSV changes; just upload a new file.

---

## How schedule CSV upload integrates

Upload is done in the dashboard via the multi-step wizard. For Attendo format, the backend calls `importAttendoSchedule()` in `services/schedule/importAttendoSchedule.ts`. That flow:

- **Upserts** clients (by Kundnr) and employees (by normalized Slinga).
- **Creates** a new schedule and, under it, visits, visit templates, visit groups, shifts, and client dependency rules.

The CSV is **not** self-contained: it references the **org catalog** for:

- **Insets** – CSV column “Insatser” (e.g. “Tillsyn”, “Bad/Dusch”) is mapped to catalog inset **by name** via `INSET_NAME_MAP`; the visit gets `insetId` from the org’s Insets.
- **Day slots / “När på dagen”** – CSV “När på dagen” (e.g. Morgon, Lunch, Kväll) is used to compute **time windows** (slot bounds). Catalog DaySlots can be used for preferred time slot on templates; the import also derives windows from the same labels (Morgon 07:00–10:30, Lunch 11:00–13:30, Kväll 16:00–19:00, unknown → 07:00–22:00).
- **Ordering / dependencies** – “Antal tim mellan besöken” in the CSV becomes **ClientDependencyRule** (min delay between visits). These are **client-level** rules (same org), not schedule-level; import creates them when processing the CSV and skips if the same client+delay already exists.
- **Shifts** – Shift type (Dag/Kväll/Helg) is inferred from the **Slinga** prefix. Shift definitions (start/end, breaks) come from **OperationalSettings** (org-level); the import creates ScheduleEmployeeShift rows for the new schedule based on that and the Slinga type.

So: **catalog = lookups and defaults**; **CSV = concrete data** (who, when, where, which inset, which delay). No catalog → CSV values for Insatser/När på dagen cannot be resolved to inset IDs or slot bounds; upload still runs but visits may have `insetId: null` or broad windows.

---

## Org-level (seed) vs schedule-level (CSV)

| Layer                           | Set by seed (org-level)                                                          | Set by CSV upload (schedule-level)                                                                                                                            |
| ------------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Organization**                | Name, slug, Clerk id, address, coordinates, timezone                             | —                                                                                                                                                             |
| **Catalog**                     | DaySlots, Insets, InsetGroups, Skills                                            | —                                                                                                                                                             |
| **OperationalSettings**         | Default salary, shifts (Dag, Kväll, Helg), working days, travel, continuity      | —                                                                                                                                                             |
| **ServiceArea**                 | Name, coordinates, revenue/cost per hour (defaults)                              | Optional: financial config can be updated per upload (revenue/cost on selected service area).                                                                 |
| **ServiceAreaDependencyRule**   | Default min delay per inset (meals, tillsyn, hygien, etc.) for the service area. | —                                                                                                                                                             |
| **Employees**                   | —                                                                                | Created/updated from CSV “Slinga” (one per unique Slinga, upsert by normalized externalId).                                                                   |
| **Clients**                     | —                                                                                | Created/updated from CSV “Kundnr” (upsert by externalId).                                                                                                     |
| **Schedule**                    | —                                                                                | One new schedule per upload (name, date range, source metadata).                                                                                              |
| **Schedule employees & shifts** | —                                                                                | From CSV: which employees are on the schedule; shift times from org OperationalSettings + Slinga type.                                                        |
| **Visit templates**             | —                                                                                | From CSV: recurrence (Återkommande), duration, preferred days, inset (lookup from catalog), priority (Kritisk).                                               |
| **Visits**                      | —                                                                                | From CSV: date, time window, duration, client, template, inset (lookup), priority, mandatory.                                                                 |
| **Visit groups**                | —                                                                                | From CSV “Dubbel” (double staffing).                                                                                                                          |
| **ClientDependencyRule**        | —                                                                                | From CSV “Antal tim mellan besöken” (min delay between visits for a client). Overrides seed default (ServiceAreaDependencyRule) for that client when present. |

So: **seed = standard data** (org + catalog + operational defaults). **CSV = schedule dynamics** (employees, clients, one schedule, its visits and dependency rules). Catalog is the shared lookup layer so that “Insatser” and “När på dagen” in the CSV map to the same insets and slot logic everywhere.

---

## Lookups vs CSV-only data

- **Lookups (CSV → org catalog)**
  - **Insatser** → catalog **Inset** by name (`INSET_NAME_MAP`). Unknown label → visit gets `insetId: null`.
  - **När på dagen** → time window (and optionally preferred time slot from DaySlots).
  - **Skift** → inferred from Slinga prefix; shift definition (start/end, breaks) from **OperationalSettings**.

- **CSV-only (no catalog)**
  - Kundnr, Slinga, Gata, Postnr, Ort, Lat, Lon, Starttid, Längd, Återkommande, Dubbel, Före, Efter, Kritisk insats, Antal tim mellan besöken.  
    These are the actual data (who, where, when, how long, recurrence, grouping, constraints). They are stored on Client, Employee, Visit, VisitTemplate, VisitGroup, ClientDependencyRule. The catalog does not store this; it only provides the reference (inset id, slot bounds, shift template).

---

## Unknown CSV values (Insatser, När på dagen, Skift, timmar mellan besök)

| CSV field                    | Behaviour                                                                          | Duplicates?                                                    |
| ---------------------------- | ---------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| **Insatser**                 | Mapped to catalog inset by `INSET_NAME_MAP`. Unknown → visit gets `insetId: null`. | No. Add new types in catalog + `INSET_NAME_MAP` to categorize. |
| **När på dagen**             | Used for time windows. Unknown → 07:00–22:00.                                      | No new records.                                                |
| **Skift**                    | From Slinga prefix (Dag/Kväll/Helg). Employees upserted by normalized Slinga.      | No. Same Slinga → same employee.                               |
| **Antal tim mellan besöken** | Stored as ClientDependencyRule. Same client + same delay → skip.                   | No.                                                            |

See `importAttendoSchedule.ts` (and `ATTENDO_CSV_MAPPING.md` if kept) for the exact mapping and upsert rules.
