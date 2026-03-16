# PRD / Plan Review: Bryntum Timeplan & Reference

**Date:** 2026-03-07  
**Documents reviewed:** `bryntum_consultant_specs/bryntum_timeplan.md`, `bryntum_consultant_specs/bryntum-reference.md`  
**Method:** Code-reviewer (docs vs PRDs, code, Jira 2.0) + framework-docs-researcher (Bryntum feasibility) + explore (path verification).

---

## Verdict: Not fully up to date

Both docs are **partially out of date** with current decisions and implementations. References to missing files, missing PRD/Jira 2.0 alignment, and stray content need fixes. Feasibility of the described Bryntum implementation is **confirmed** (SchedulerPro 7.x, 7.1.2+ for nested/visit groups).

---

## 1. Broken or missing references

### bryntum_timeplan.md

| Reference                                            | Issue                                                                                                                        |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **Data Model v2.0** `../../03-data/data-model-v2.md` | File does not exist. Use `../../03-data/data-model.md`.                                                                      |
| **Umbrella PRD** `../prd-umbrella.md`                | File does not exist. Replace with CAIRE_PLANNING_PRD.md, CAIRE_SCHEDULING_PRD.md, JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES.md. |
| **BRYNTUM_MAIN_PRD.md** (multiple categories)        | File does not exist. Use BRYNTUM_FROM_SCRATCH_PRD.md (same folder).                                                          |
| **SOLUTION_UI_SPECIFICATION.md**                     | Already fixed (correct file and path).                                                                                       |

### bryntum-reference.md

| Reference                                  | Issue                                                                            |
| ------------------------------------------ | -------------------------------------------------------------------------------- |
| **Lines 2–4**                              | Stray content: "testing" and Siesta URL. Remove.                                 |
| **Feature PRD – Bryntum Calendar View.md** | File does not exist. Point to CAIRE_SCHEDULING_PRD.md and CAIRE_PLANNING_PRD.md. |
| **"umbrella PRD"** (line 311)              | Same missing doc; use current PRD names.                                         |

---

## 2. Missing alignment with PRDs and Jira 2.0

- **Neither doc** references: CAIRE_PLANNING_PRD.md, CAIRE_SCHEDULING_PRD.md, JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES.md.
- **Architecture** from the PRDs is not stated: apps/dashboard (UI), apps/dashboard-server (API), direct GraphQL hooks only, route-plans from-patch, visitDependencies, visit groups (Dubbel), Preferred scenario.
- **Jira:** timeplan uses "Jira: TBD" everywhere. Map to: **262, 303–306** (Resources UI / constraints), **C0-366** (schema/constraints/dependencies), **CO-43, 201, 203** (resources backend).
- **User stories:** No mapping from timeplan categories to US-1–US-11 (Scheduling) or US-1–US-6 (Planning).

---

## 3. Feasibility (Bryntum SchedulerPro 7.x)

| Area                         | Finding                                                                                                                                            |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Day view, 100+ events        | Supported; 100–500 events in day view is within normal use; timeplan target is feasible.                                                           |
| Pin / drag                   | No built-in `pinned`; use EventModel `locked` and `beforeEventDrag`/`beforeEventResize`; send pinningRequested + minStartTravelTime in from-patch. |
| From-patch                   | Backend (Timefold); Bryntum only displays state. Integration category and save handlers cover this.                                                |
| Visit groups / nested events | Supported; use **7.1.2+** for nested/multi-assign (7.1.0/7.1.1 had fixes).                                                                         |
| Version                      | Lock to **7.1.2+** in doc; no need to inflate 14–19 day estimate.                                                                                  |

---

## 4. Recommended edits (concrete)

### bryntum_timeplan.md

1. **Related Documents (top):** Replace Data Model v2.0 with `[Data Model](../../03-data/data-model.md)`. Replace Umbrella PRD with `[Visit Planning PRD](../CAIRE_PLANNING_PRD.md)`, `[Daily Scheduling PRD](../CAIRE_SCHEDULING_PRD.md)`, `[Jira 2.0 user stories](../JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES.md)`.
2. **All categories:** Replace every `data-model-v2.md` with `data-model.md` and path `../../03-data/data-model.md`. Replace every **BRYNTUM_MAIN_PRD.md** with **BRYNTUM_FROM_SCRATCH_PRD.md**.
3. **Jira:** Replace "Jira: TBD" with: UI categories → **262, 303–306** (and C0-366 where constraints/dependencies apply); Integration → **CO-43, 201, 203**. Add one sentence: "Scheduling/Resources UI: 262, 303–306; schema/resources backend: C0-366, CO-43, 201, 203 (see JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES.md)."
4. **Architecture (after Executive Summary):** Add short "Architecture & PRD alignment" block: frontend **apps/dashboard**, backend **apps/dashboard-server**, **direct GraphQL hooks** from `@appcaire/graphql`, re-optimization via **route-plans from-patch**, constraints/dependencies (**visitDependencies**, **visit groups**) and **Preferred scenario** per CAIRE_SCHEDULING_PRD and CAIRE_PLANNING_PRD.
5. **Pin implementation (Category 3 or Movable vs Pinned):** Add note: "Bryntum has no built-in pinned field; use EventModel `locked` and beforeEventDrag/beforeEventResize; store pinned in domain model and send pinningRequested + minStartTravelTime in from-patch payload."
6. **Version and scaling:** State SchedulerPro **7.1.2+** for nested events/visit groups. For 500+ events or long horizons, note infinite scroll and optional load of visible range; tune eventReleaseThreshold.

### bryntum-reference.md

1. **Top:** Remove lines 2–4 (stray "testing" and Siesta URL).
2. **PRD reference (block quote):** Replace "Feature PRD – Bryntum Calendar View.md" with CAIRE_SCHEDULING_PRD.md and CAIRE_PLANNING_PRD.md (and optionally JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES.md).
3. **Line 311 ("umbrella PRD"):** Replace with "requirements in CAIRE_SCHEDULING_PRD.md and CAIRE_PLANNING_PRD.md (and JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES.md for schema/constraints/dependencies)."
4. **Reality Check:** Set "Last Updated" to current date (e.g. 2026-03-07). Resolve inconsistent status for Embedded Chart and Tree Summary Heatmap (one status per feature; align with Remaining Features list).
5. **Optional:** Add one-line pointer to Jira 2.0 (262, 303–306, C0-366, CO-43, 201, 203) for implementation tracking.

### Terminology

- **from-patch:** Add in timeplan Category 8 (Real-time Optimization): "Re-optimization uses Timefold route-plans from-patch (see CAIRE_SCHEDULING_PRD)."
- **Visit groups / Dubbel:** In timeplan Category 3 (or double-staffing), add "visit groups (e.g. Dubbel)" to match CAIRE_SCHEDULING_PRD.
- **Preferred scenario:** In timeplan Category 8 (scenarios), add that **Preferred** (preferredVehicles, weight 2) is the planning default per CAIRE_PLANNING_PRD.

---

## 5. Summary

| Item                 | Action                                                                                                    |
| -------------------- | --------------------------------------------------------------------------------------------------------- |
| Broken links         | Fix data-model-v2 → data-model, prd-umbrella → current PRDs, BRYNTUM_MAIN_PRD → BRYNTUM_FROM_SCRATCH_PRD. |
| bryntum-reference.md | Remove stray "testing"/Siesta; fix PRD refs; update Reality Check date and status.                        |
| PRD / Jira 2.0       | Add PRD and Jira links to both docs; add architecture/PRD alignment to timeplan.                          |
| Bryntum version      | State 7.1.2+ for nested/visit groups; add pin implementation note and scaling note.                       |

Applying these edits will align both Bryntum docs with current decisions, implementations, and Jira 2.0 tickets.
