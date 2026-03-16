# Jira 2.0: User stories for schema, constraints, dependencies & resources

**Purpose:** Copy-paste ready user stories and acceptance criteria for Jira tickets C0-366, CO-43, 201, 203, 262, 303-306. These support the [Resources & schema-driven constraints](CAIRE_SCHEDULING_PRD.md#resources--schema-driven-constraints) section of the Daily Scheduling PRD.

**Note:** The Jira refs are **existing** implementation/epic tickets; this document provides PRD content and user stories to attach to them (no code changes implied by this doc).

**Implementation note:** Backend = **apps/dashboard-server** (resolver layout: `resolvers/{domain}/{topic}/queries|mutations/`, one file per operation). UI = **apps/dashboard**; use **direct GraphQL hooks** from `@appcaire/graphql` only (no wrapper hooks). Scenario/solver config = data or app env; constraint and FSR logic stays in dashboard-server, not in packages.

---

## Schema & constraints (generic)

### US-SC1: Schema as source of truth

**As a** product owner,  
**I want** all scheduling and planning constraints to be stored and managed in the **schema** (data model + API + UI)  
**so that** CSV, API, and UI edits all flow from one source and metrics and solver input (FSR and, when used, ESS) stay consistent.

**Acceptance criteria:**

- Visit, client, and employee constraint fields are defined in the schema
- FSR input is generated from schema (and scenarios)
- When ESS is used, ESS dataset (employees, contracts, demand curve from visits, labor/cost config) is also generated from schema/standing data, not from import-specific logic alone

**Map to Jira:** C0-366. Implementation: dashboard-server (schema/Prisma and resolvers); no constraint or FSR logic in packages.

---

### US-SC2: Configure constraints per category

**As an** admin/scheduler,  
**I want** to configure **visit** (time windows, duration, skills), **client** (address, continuity, unused hours, fixed contact), and **employee** (shifts, breaks, skills, employment type, wages) constraints in the resources/admin UI  
**so that** optimization respects them.

**Acceptance criteria:**

- UI and API support the constraint categories listed in the PRD (Visit, Customer, Employee, Dependencies, Scenarios)
- Changes are persisted and reflected in next optimization run

**Map to Jira:** C0-366

---

## Dependencies (visit dependencies & rules)

### US-DEP1: Per-customer visit dependencies

**As a** scheduler,  
**I want** to define **per-customer** visit dependencies (e.g. "Visit B must start at least 3.5 h after Visit A")  
**so that** same-day ordering and minimum gaps are enforced by the solver.

**Acceptance criteria:**

- Data model supports visit dependency (preceding visit, minDelay)
- UI to define/edit per client/visit pair or template
- FSR input includes `visitDependencies` from schema

**Map to Jira:** C0-366

---

### US-DEP2: Area/org rules for visit types

**As an** admin,  
**I want** to define **general rules** for an area or organisation (e.g. same-day slot order Morgon→Lunch→Kväll, default min delay between visits, or spread-over-week behaviour)  
**so that** dependency generation is consistent and not hardcoded per import format.

**Acceptance criteria:**

- Area/org-level rules (e.g. visit type → slot, default min delay, same-day vs spread) are stored in schema
- System generates or validates `visitDependencies` from these rules when building FSR input

**Map to Jira:** C0-366

---

## Resources (align with CO-43, 201, 203, 262, 303-306)

### US-RES1: Resources 2.0 – data model

**As a** developer,  
**I want** the **resources** data model (employees, clients, visits, service areas) to include all constraint and dependency fields needed for planning and scheduling  
**so that** FSR and UI use one source—and when ESS+FSR is used, **standing data** (contracts, availability, labor rules, cost groups, skills) supports both ESS and FSR dataset generation.

**Acceptance criteria:**

- Resources schema includes visit, client, employee, dependency, and scenario-related constraint fields
- When ESS is used, ESS dataset can be built from schema/standing data (employees, contracts, demand from visits, labor/cost config)

**Map to Jira:** CO-43, 201, 203. Implementation: dashboard-server (schema/Prisma and resolvers); no constraint or FSR logic in packages.

---

### US-RES2: Resources 2.0 – UI

**As a** scheduler,  
**I want** to manage employees, clients, visits, and **constraints/dependencies** in the Resources UI  
**so that** I don't depend on CSV or external tools for rule changes.

**Acceptance criteria:**

- Resources UI supports CRUD for employees, clients, visits, service areas
- UI supports configuring constraints and dependencies (per-customer and area/org rules) as in the PRD
- Changes are persisted and reflected in optimization

**Map to Jira:** 262, 303-306

---

### US-RES3: Scenarios and schema

**As a** scheduler,  
**I want** to select a **scenario** (preset) that applies a set of overrides/defaults to the current schema or run  
**so that** I can quickly run "all updates" for a given schema (e.g. planning default, or a specific scheduling preset).

**Acceptance criteria:**

- Scenarios can drive schema-level overrides, not only one-off solver payloads
- When ESS+FSR is used, scenarios can affect both ESS config (e.g. labor rules, cost weights) and FSR config (e.g. continuity weight, visit flexibility)

**Map to Jira:** Scenario tickets under C0-151/C0-153

---

## Employee break location (optional) and travel time

### US-BREAK1: Optional break location with travel to/from break

**As a** scheduler,  
**I want** to optionally assign a **location** to an employee break (e.g. lunch at a specific place)  
**so that** the solver plans **travel to the break**, the **break**, and **travel to the next visit** in the correct sequence: _visit A → travel to break → break → travel to visit B → visit B_.

**Acceptance criteria:**

- Schema supports **optional** break location: `ScheduleEmployeeBreak` (or equivalent) has an optional location field (e.g. lat/long or address reference). When absent, break is time-only (no extra travel).
- FSR input: when a break has a location, `requiredBreaks[].location` is populated (e.g. `[lat, lon]`). When omitted, break has no location in the payload and is treated as time-window-only.
- Solver/FSR models the route sequence correctly: **travel from previous visit to break location**, **break at location**, **travel from break location to next visit**. Travel time to and from the break is included in the route and in solution metrics.
- Time handling: break time windows (`minStartTime`, `maxEndTime`) and any dependency logic use explicit timezone when DST matters (per Timefold visit-dependency behaviour).
- UI: scheduler can optionally set or clear break location in the Resources/admin UI; day view shows break as a location stop with travel legs when location is set.

**Reference:** FSR input already supports `requiredBreaks` with optional `location` (see e.g. `e2e_pipeline_quicktest/input.json`). Database table `ScheduleEmployeeBreak` currently has no location column — add optional location (e.g. `locationLat`, `locationLon` or JSONB `location`) and map to FSR `requiredBreaks[].location`.

**Map to Jira:** C0-366 (schema/constraints), CO-43 / 201 / 203 (resources data model & FSR input generation), 262 / 303–306 (Resources UI for break location).

---

## Jira mapping summary

| Jira ref         | Suggested focus                                                                                            |
| ---------------- | ---------------------------------------------------------------------------------------------------------- |
| **C0-366**       | Schema-driven constraints & dependencies; US-SC1, US-SC2, US-DEP1, US-DEP2; US-BREAK1 (schema).            |
| **CO-43**        | Resources (data model / API); US-RES1; US-BREAK1 (break location).                                         |
| **201, 203**     | Resources backend/schema; US-RES1; US-BREAK1 (FSR input from schema).                                      |
| **262, 303-306** | Resources UI and constraint/dependency configuration; US-RES2, US-DEP1; US-BREAK1 (break location UI).     |
| **C0-368**       | Solution metrics (bug): fix total shift (shift boundaries, not event span); break/travel; units (h/min).   |
| **C0-369**       | Solution metrics: Active shift hours (shifts with visits, incl. idle and breaks). Blocks: C0-368.          |
| **C0-370**       | Solution metrics: Field time (no idle; shift end = arrival at office; breaks per variant). Blocks: C0-368. |

**Related PRD:** [CAIRE_SCHEDULING_PRD.md — Resources & schema-driven constraints](CAIRE_SCHEDULING_PRD.md#resources--schema-driven-constraints).

**ESS+FSR roadmap:** [CAIRE_FEATURE_ROADMAP.md](../09-scheduling/ess-fsr/CAIRE_FEATURE_ROADMAP.md), [ESS_FSR_PROJECT_PLAN.md](../09-scheduling/ess-fsr/ESS_FSR_PROJECT_PLAN.md).

---

## Solution metrics: bug + shift variants

**Context:** [BUG_SOLUTION_METRICS_TOTAL_SHIFT_AND_VARIANTS.md](../10-consistency/BUG_SOLUTION_METRICS_TOTAL_SHIFT_AND_VARIANTS.md). Metrics are always from the **solution**; input is reference only (e.g. unassigned visits). Use **hours and minutes** for human-facing durations.

### BUG-MET1: Total shift computed from event span instead of shift length (quick fix)

**As a** scheduler,  
**I want** solution **Total shift** (and thus Utilization) to reflect actual scheduled shift time  
**so that** KPIs are meaningful and comparable to the Python metrics reference.

**Problem:** Total shift is currently the sum over employees of (last event time − first event time). Over 4 weeks that becomes ~744k min (per-employee calendar span), not sum of shift lengths (~76k min). Utilization then shows ~8.7% instead of ~90%+.

**Acceptance criteria:**

- Total shift = sum over **all shifts** in the solution of (shift end − shift start). Shift end = **arrival at end location** (office/depot), not last visit end.
- Use **shift boundaries** from the solution (or schedule), not (first event, last event) per employee.
- Total break and travel sourced from solution events; fix break double-count and travel undercount if present.
- All duration metrics shown in **hours and minutes** (e.g. `1 082 h 15 min`) for consistency.

**Map to Jira:** [C0-368](https://caire.atlassian.net/browse/C0-368). Implementation: `apps/dashboard-server` solution metrics service + UI formatting.

---

### US-MET2: Active shift hours (shifts with visits, incl. idle) — feature request

**As a** scheduler,  
**I want** to see metrics for **active shifts only** (shifts with at least one visit), including tail idle and breaks in those shifts  
**so that** I can compare capacity used vs. full capacity until “remove empty shifts from patch” is implemented.

**Acceptance criteria:**

- **Active shift hours** = sum of (shift end − shift start) only for shifts that have **≥ 1 visit**. Shift end = arrival at end location. Includes tail idle.
- **Breaks (active):** only breaks in shifts that have at least one visit. Empty shifts contribute no shift time and no breaks.
- Visit count, visit time, travel, wait are unchanged (same for all variants). Only shift and break differ.
- Display in hours and minutes.

**Map to Jira:** [C0-369](https://caire.atlassian.net/browse/C0-369). Depends on C0-368 (correct shift boundaries).

---

### US-MET3: Field time (no idle: empty shifts and tail idle excluded) — feature request

**As a** scheduler,  
**I want** to see **field time** = assignable time with all idle removed (empty shifts + tail idle after last visit until arrival at office)  
**so that** I can measure “pure” visit+travel+wait+break and utilization on that basis.

**Acceptance criteria:**

- **Field time** excludes: (a) entire empty shifts, (b) tail idle from last visit end to **arrival at end location** (office). Shift does **not** end at last visit; it ends when the employee arrives at the office after the last visit.
- **Breaks (field):** only breaks that occur in the solution. Tail idle after last visit does **not** get break unless break already occurred before last visit.
- Visit count, visit time, travel, wait are unchanged. Only shift and break differ from “all shifts” and “active shifts.”
- Display in hours and minutes.

**Map to Jira:** [C0-370](https://caire.atlassian.net/browse/C0-370). Depends on C0-368. Complements future “scenario remove empty shifts from patch.”
