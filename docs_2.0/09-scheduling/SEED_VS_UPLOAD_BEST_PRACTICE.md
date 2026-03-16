# Seed vs CSV upload: best practice and flow

## Recommendation

**Seed = operational + catalog only.**  
**Schedule data (employees, clients, visits) = from CSV upload (or “Create from Timefold JSON”).**

- **Seed** should provide: org shape, OperationalSettings, ServiceArea, DaySlots, Insets, InsetGroups, Skills (and any org-level costs/defaults). No employees, clients, or visits.
- **Transactional data** should come from the **upload flow** (or equivalent API): the CSV (or JSON) is the source of truth for a given schedule; upload is how production and staging get data.

That gives:

- One canonical path for schedule data (upload).
- No duplicate logic (no seed-attendo vs importAttendoSchedule for the same data).
- Stage/prod never depend on seed CSVs; they get data only via upload or manual entry.
- Clear split: seed = “org + catalog”, upload = “schedule data”.

---

## Current flow

| Script / flow                             | What it creates                                                                                                                             | When to use                                                         |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| **seed-org-bootstrap** (or Clerk webhook) | Org + OperationalSettings + ServiceArea + **catalog only** (DaySlots, Insets, InsetGroups, Skills). No employees, clients, visits.          | New org onboarding; stage/prod; “empty” org ready for first upload. |
| **seed-attendo**                          | Same as bootstrap **plus** employees, clients, schedule, visits from a **CSV file** (real or substitute).                                   | Local/pilot “one-command” full demo. Convenience only.              |
| **CSV upload (dashboard)**                | Schedule + employees (upsert) + clients (upsert) + visits. Requires org to already have **catalog** (inset names in CSV map to org insets). | Normal way to load schedule data in all environments.               |

So today:

- **Bootstrap** already matches the recommended “seed = catalog only” model.
- **seed-attendo** is an extra “full demo” path that duplicates the upload path (same `importAttendoSchedule` logic, but triggered from a script + file path instead of UI).

---

## Best-practice flow (target)

1. **New org**
   - Create org in Clerk (or run `seed-org-bootstrap` for a specific org).
   - Webhook / bootstrap runs → org + OperationalSettings + ServiceArea + catalog. **No** employees, clients, visits.

2. **First schedule**
   - User uploads Attendo (or other) CSV in the dashboard → parse + validate → finalize.
   - Backend uses same logic as today (e.g. `importAttendoSchedule` or Nova path); employees/clients/visits are created/updated from the CSV only.

3. **Local dev**
   - **Option A (recommended):** Bootstrap org + catalog (e.g. `seed-org-bootstrap` with CLERK_ORG_ID), then **upload** the same CSV once via the UI (or a small script that calls the same import). No seed CSVs for transactional data.
   - **Option B (convenience):** Keep `seed-attendo` as a **demo-only** script that runs bootstrap + import from a file so “one command” gives a full demo; document that it is not the path for stage/prod and that upload is canonical.

---

## Summary

| Question                                           | Answer                                                                                                                         |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Should seed add employees, clients, visits?        | **No** for best practice. Seed = operational + catalog only.                                                                   |
| Where should employees, clients, visits come from? | **CSV upload** (or Timefold JSON import). Single source of truth.                                                              |
| What is seed for?                                  | Org + OperationalSettings + ServiceArea + DaySlots, Insets, InsetGroups, Skills (and any org-level defaults).                  |
| What about seed-attendo?                           | Treat as **optional demo convenience** for local/pilot (bootstrap + import from file). Stage/prod use bootstrap + upload only. |

If you want to align fully with best practice, the next step is to either (1) **remove** employees/clients/visits/schedule from seed-attendo (so it only runs bootstrap + catalog for the Attendo org, and the first schedule is always from upload), or (2) **keep** seed-attendo as a documented “demo seed” that explicitly says “for local one-command demo only; production data comes from upload.”
