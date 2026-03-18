# Daily Scheduling — Product Requirements

Status: DRAFT | Owner: TBD | Last updated: 2026-03-18

## Problem

With an approved repeating schedule in place, home care organizations still face daily disruptions: sick employees, late arrivals, client cancellations, last-minute additions. These create gaps — hours that were allocated in the plan but are no longer filled. Today disruptions are handled manually (CSV re-upload, phone calls). Gaps from cancelled or deferred visits are not recaptured. There is no single view comparing "planned" vs "AI-optimized" vs "what happened."

## Outcome

A scheduler opens the day view, sees disruptions and resulting gaps flagged automatically, runs AI re-optimization, reviews changes side-by-side with the baseline, makes adjustments, recaptures unused hours from gaps, and publishes — in under 30 minutes. Staff see their updated schedule on mobile.

## Success Metrics

| Metric                                                                     | Baseline            | Target              |
| -------------------------------------------------------------------------- | ------------------- | ------------------- |
| Staff efficiency (care time / shift time)                                  | TBD per org         | 75–80%+             |
| Scheduling time vs manual                                                  | Current manual time | 50%+ reduction      |
| Travel time                                                                | TBD                 | Up to 20% reduction |
| First-proposal acceptance after disruption                                 | TBD                 | 80%+                |
| Time from disruption flagged to re-published schedule                      | TBD                 | Under 30 min        |
| Unused hours recaptured (hours freed by cancellations reassigned same day) | TBD                 | 30%+                |

## Users & Jobs to be Done

| Role                    | Job                                                                       | Current pain                                                                 |
| ----------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Scheduler / dispatcher  | Publish an updated daily schedule that handles disruptions and fills gaps | Manual CSV re-upload and phone calls; no single view of planned vs optimized |
| Caregiver / field staff | View and follow the current day's schedule                                | Delayed or inconsistent updates when plans change                            |

## Scope

**In scope:** Day view against approved baseline; **employee view** (employees as resources) and **client view** (clients as resources, assignments as events; filters: inset names, inset groups, frequencies, employees, only-with-dependencies); flagging disruptions (sick, late, cancellation) and surfacing gaps; AI re-optimization (Timefold FSR) on affected portion; side-by-side comparison; pin/unpin, drag, re-optimize; deferred movable visits (reschedule or pool); recapture unused hours from gaps; recommendation visits to fill remaining gaps; temp employee in resource pool and re-optimize; publish to staff (mobile); live metrics (efficiency, travel, continuity); **insets and InsetGroups** (visit types, dependency ordering); **visit dependencies** (VisitDependency, ClientDependencyRule, ServiceAreaDependencyRule; from CSV import and rules); **scheduler appearance** (org-level category/frequency colors via Operational Settings).

**Out of scope:** Creating or revising the repeating baseline (that is Visit Planning, PRD 1); ESS+FSR auto staffing discovery (roadmap); multi-area scheduling, AI chat, BI export (roadmap).

## Architecture & implementation boundaries

- **Backend:** All scheduling backend (import, FSR/ESS input, solver, from-patch, scenarios) lives in **`apps/dashboard-server`**. Resolvers under `resolvers/{domain}/{topic}/queries/` and `mutations/`, one file per operation, named exports.
- **Frontend:** Scheduling UI lives in **`apps/dashboard`**. Use **direct GraphQL hooks** from `@appcaire/graphql` only; **no wrapper hooks**.
- **Schema & types:** **`packages/graphql`**; after .graphql changes run `yarn workspace @appcaire/graphql codegen`.
- **Config:** Scenario/solver presets = **data (DB) or app env** (e.g. dashboard-server `.env` for Timefold); not changes to protected monorepo config.
- **Pin and re-optimize:** The supported mechanism is **Timefold route-plans from-patch** (`POST /v1/route-plans/{id}/from-patch`) with pinning + re-solve. Platform dataset-centric from-patch is preview and out of scope for this PRD.

## Resources & schema-driven constraints

Scheduling and optimization use **schema data** as the source of truth: data model (entities and constraint fields), metrics (derived from schema; with ESS+FSR, combined ESS and FSR metrics), and UI (edit/display of constraints and dependencies). **Standing data** (employees, clients, visits, constraints, dependency rules, labor rules, cost groups) feeds both FSR and—when used—ESS (demand curve from visits, supply from employees/contracts/availability). Resources data and FSR/ESS dataset generation are implemented in **apps/dashboard-server** (Prisma + GraphQL); the Resources UI is in **apps/dashboard**. **Combined ESS+FSR metrics** (e.g. true efficiency, cost per visit, continuity) are derived from schema and optimization runs and exposed in UI; see [ESS_FSR_DUAL_MODEL_ARCHITECTURE.md § Metrics Strategy](../09-scheduling/ess-fsr/ESS_FSR_DUAL_MODEL_ARCHITECTURE.md).

### Constraint categories

All of the following are first-class in the schema (data model, API, UI), not only in CSV or solver payloads. The table indicates which model(s) consume each category when ESS+FSR is used.

| Category              | Examples (flexible, configurable)                                                            | Consumed by           |
| --------------------- | -------------------------------------------------------------------------------------------- | --------------------- |
| **Visit**             | start, min/max times, duration, skills, visitType, priority                                  | FSR; ESS (demand)     |
| **Customer (client)** | address, name, id, location, fixed care contact, continuity, unused hours, preferences       | FSR; ESS (continuity) |
| **Employee**          | shifts, breaks, employment type, skills, wages/cost, service area, availability              | ESS; FSR (vehicles)   |
| **Dependencies**      | Per-customer (preceding, minDelay); area/org rules (same day/week); visit groups             | FSR                   |
| **Scenarios**         | Presets for overrides/defaults (planning default, scheduling preset); can affect ESS and FSR | ESS; FSR              |

### Dependencies

- **Per-customer:** Visit-to-visit dependencies (preceding visit, minDelay). Used for same-day ordering and minimum gap (e.g. "3.5 h between visits"). Data model: `VisitDependency` (schedule-level); `ClientDependencyRule` / `ServiceAreaDependencyRule` (client/area-level rules). UI allows defining/editing per client/visit pair or template. FSR input includes `visitDependencies` from schema.
- **Area/org rules:** General rules for visit types (e.g. same-day slot order Morgon→Lunch→Kväll, default min delay, spread-over-week behaviour). Stored in schema; the system generates or validates `visitDependencies` from these rules when building FSR input. These feed FSR `visitDependencies` and visit groups but are **defined and editable in the schema/UI**, not only in import files.
- **CSV import:** Attendo CSV "Antal tim mellan besöken" → `attendoToCaire` → `upsertVisitDependencies`; semantics: &lt;12h = same-day, ≥18h = cross-day spread. See [DEPENDENCY_CREATION_VERIFICATION.md](../09-scheduling/DEPENDENCY_CREATION_VERIFICATION.md).
- **InsetGroups:** `InsetGroup` + `InsetGroupMember` define ordering (e.g. meals: breakfast → lunch → dinner); `resolveInsetGroupDependencies` builds FSR edges from schema.
- **Visit groups (e.g. Dubbel / double-staffing):** FSR supports **visit groups** (`visitGroups[]`): all visits in a group must be assigned to different vehicles and run at the same time (no semi-assigned groups). Schema and UI must keep visit group membership consistent when building FSR input.

### Scenarios

Scenarios apply a bundle of overrides/defaults to the current schema or run so that "all updates for a schema" can be run in one go (e.g. planning default, or a specific scheduling preset). When ESS+FSR is used, a scenario may affect both ESS config (e.g. labor rules, cost weights) and FSR config (e.g. continuity weight, visit flexibility).

### Jira (schema & resources)

The following Jira refs are **existing** implementation/epic tickets. This PRD and the user stories in [JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES.md](JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES.md) provide content to attach to them. Where relevant, schema/constraints/resources work is traceable to the ESS+FSR dual-model implementation: [CAIRE_FEATURE_ROADMAP.md](../09-scheduling/ess-fsr/CAIRE_FEATURE_ROADMAP.md), [ESS_FSR_PROJECT_PLAN.md](../09-scheduling/ess-fsr/ESS_FSR_PROJECT_PLAN.md).

| Jira ref         | Suggested focus                                                                                       |
| ---------------- | ----------------------------------------------------------------------------------------------------- |
| **C0-366**       | Epic or parent for "Schema-driven constraints & dependencies"; link US-SC1, US-SC2, US-DEP1, US-DEP2. |
| **CO-43**        | Resources (data model / API); US-RES1.                                                                |
| **201, 203**     | Resources backend/schema; US-RES1.                                                                    |
| **262, 303-306** | Resources UI and constraint/dependency configuration; US-RES2, US-DEP1 (UI part).                     |

## User Stories

### US-1: View today's schedule against approved baseline (Bryntum)

As a scheduler, I want to view today's schedule derived from the approved repeating baseline so that I can see what was planned and what needs adjustment.

**Acceptance criteria:**

- [ ] Day view shows visits and assignments from the approved baseline for the selected day
- [ ] UI supports the density and interactions needed for 100+ visits (Bryntum or equivalent). Day view is the primary view; event count is expected in the 100–500 range per day with virtualization enabled; if the count grows significantly, load only the visible day or apply resource/visit filters to keep the view responsive.
- [ ] Baseline source is clearly indicated (e.g. "From approved pattern")

### US-2: Flag disruptions automatically (sick, late, cancellation) and surface resulting gaps

As a scheduler, I want disruptions (sick employee, late arrival, client cancellation) to be flagged and resulting gaps to be visible so that I know what to re-optimize.

**Acceptance criteria:**

- [ ] Scheduler can mark employee as sick, visit as cancelled, or similar disruption
- [ ] System surfaces which visits are affected and which hours become gaps (unused)
- [ ] Gaps are visible in the day view or a dedicated view (e.g. unused hours pool)

### US-3: Run AI re-optimization (Timefold FSR) on affected portion

As a scheduler, I want to run AI re-optimization on the affected portion of the day so that assignments are updated without full manual reassignment.

**Acceptance criteria:**

- [ ] Re-optimization can be triggered from the day view (e.g. "Re-optimize" action)
- [ ] Solver receives current state (pins, disruptions, gaps) and returns updated assignments
- [ ] Result is presented for review before publication

### US-4: Compare original vs optimized side-by-side

As a scheduler, I want to compare the baseline (or current) version with the optimized version side-by-side so that I can validate changes before publishing.

**Acceptance criteria:**

- [ ] UI supports viewing two schedule versions (e.g. baseline vs optimized) for the same day
- [ ] Differences in assignment are clear (e.g. highlighted or diff view)
- [ ] Scheduler can accept, reject, or further adjust before publishing

### US-5: Fine-tune via patch (pin/unpin, drag, re-optimize)

As a scheduler, I want to pin visits I want to keep, unpin others, drag to adjust, and re-run optimization so that the result matches my constraints.

**Acceptance criteria:**

- [ ] Scheduler can pin visits (fix assignment) and re-optimize the rest
- [ ] Scheduler can unpin and drag visits within rules (skills, time windows)
- [ ] Patch-based re-optimization uses current pins and constraints. Implementation uses **Timefold route-plans from-patch** (`POST /v1/route-plans/{id}/from-patch`) with pinning and re-solve (Platform dataset-centric from-patch is out of scope).

### US-6: Handle deferred movable visits (reschedule within day or pool for later)

As a scheduler, I want to reschedule deferred movable visits within the day or pool them for later so that we don't lose track of unfulfilled demand.

**Acceptance criteria:**

- [ ] Visits deferred (e.g. client cancelled) can be moved to another time same day or marked for later
- [ ] Pool of deferred visits is visible and can be brought back into scope when capacity allows
- [ ] Re-optimization can consider deferred visits when filling gaps

### US-7: Recapture unused hours — AI suggests how to fill gaps from cancelled/deferred visits

As a scheduler, I want the system to suggest how to fill gaps (hours freed by cancellations or deferrals) so that we recapture unused hours the same day.

**Acceptance criteria:**

- [ ] Gaps from cancelled/deferred visits are identified
- [ ] AI suggests reassignments or moves that fill gaps (e.g. move another visit into the slot, assign from pool). Time-window suggestions use Timefold **visit-recommend-time-windows**; "fill gaps" is implemented in-app (select candidates → call recommendations → add to plan → solve/from-patch). Consider latency when requesting many recommendations per day.
- [ ] Scheduler can accept suggestions or adjust manually
- [ ] Target: 30%+ of hours freed by cancellations reassigned same day (metric)

### US-8: Recommendation visits — AI proposes additional client visits to fill remaining unused hours

As a scheduler, I want the system to propose additional client visits that could be placed in remaining unused hours so that we use capacity and reduce lost revenue.

**Acceptance criteria:**

- [ ] When unused hours remain after re-optimization, system can propose additional visits (e.g. from client allocation or pool). Proposals use Timefold **visit-recommend-time-windows**; "propose additional visits" is implemented in-app (candidates → recommendations → add to plan → solve/from-patch). Note latency if many recommendations are requested per day.
- [ ] Proposals are feasible (time, skills, geography) and visible to scheduler
- [ ] Scheduler can accept or dismiss; accepted visits are added to the schedule

### US-9: Call in temp employee — update resource pool and re-optimize

As a scheduler, I want to add a temp employee to the resource pool and re-optimize so that we can cover shortfalls without overloading existing staff.

**Acceptance criteria:**

- [ ] Scheduler can add a temp (or extra) employee to the day's resource pool
- [ ] Re-optimization includes the new resource when run
- [ ] Assignments for the temp are visible and publishable like others

### US-10: Publish updated schedule to staff (mobile)

As a scheduler, I want to publish the updated schedule so that staff see the current plan on mobile (or web).

**Acceptance criteria:**

- [ ] "Publish" action makes the current day schedule the official one for staff
- [ ] Staff can view their assigned visits on mobile (or designated channel)
- [ ] Updates are pushed or available shortly after publish (e.g. within minutes)

### US-11: View metrics (efficiency, travel, continuity) live

As a scheduler, I want to see efficiency, travel, and continuity metrics for the current schedule so that I can judge quality before and after re-optimization.

**Acceptance criteria:**

- [ ] Metrics (e.g. care time / shift time, travel time, caregiver-per-client continuity) are visible in the scheduling UI
- [ ] Metrics update when the schedule or solution changes (e.g. after re-optimize)
- [ ] Definitions align with METRICS_SPECIFICATION.md

## Roadmap

- **ESS+FSR:** Auto staffing discovery — number of shifts needed per day determined by optimizer, not manually (see architecture docs).
- Multi-area scheduling (one schedule spanning 2+ areas).
- AI chat interface for schedule actions.
- BI / data warehouse export.

## Open Questions

| #   | Question                                                                   | Owner   | Status |
| --- | -------------------------------------------------------------------------- | ------- | ------ |
| 1   | Freeze horizon for real-time replanning (pin visits in progress)?          | Product | Open   |
| 2   | Priority order for filling gaps (deferred first vs recommendation visits)? | Product | Open   |

## Jira

| Epic                                     | User stories       |
| ---------------------------------------- | ------------------ |
| Daily Scheduling — View & disrupt        | US-1, US-2         |
| Daily Scheduling — Re-optimize & compare | US-3, US-4, US-5   |
| Daily Scheduling — Gaps & recapture      | US-6, US-7, US-8   |
| Daily Scheduling — Resources & publish   | US-9, US-10, US-11 |

## Related specifications

- [SCHEDULE_SOLUTION_ARCHITECTURE.md](../09-scheduling/SCHEDULE_SOLUTION_ARCHITECTURE.md)
- [SOLUTION_UI_SPECIFICATION.md](../09-scheduling/SOLUTION_UI_SPECIFICATION.md)
- [METRICS_SPECIFICATION.md](../09-scheduling/METRICS_SPECIFICATION.md)
- [JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES.md](JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES.md) — user stories (US-SC1, US-SC2, US-DEP1, US-DEP2, US-RES1, US-RES2, US-RES3) for Jira C0-366, CO-43, 201, 203, 262, 303-306.
- [ESS_FSR_DUAL_MODEL_ARCHITECTURE.md](../09-scheduling/ess-fsr/ESS_FSR_DUAL_MODEL_ARCHITECTURE.md) — combined metrics, standing data, ESS/FSR consumption of schema.
