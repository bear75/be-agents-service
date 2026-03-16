# Scheduling Advanced Planning PRD

> **Purpose:** Product requirements for advanced planning features enabled by Timefold's operational-planning and real-time replanning guides. This document is an **addendum** to [SCHEDULING_MASTER_PRD.md](./SCHEDULING_MASTER_PRD.md).
> **Audience:** Product, Engineering, QA
> **Last Updated:** 2026-02-25

---

## Table of Contents

1. [Scope and References](#1-scope-and-references)
2. [User Stories](#2-user-stories)
3. [Technical Requirements](#3-technical-requirements)
4. [Dependencies](#4-dependencies)
5. [Out of Scope](#5-out-of-scope)

---

## 1. Scope and References

### 1.1 Scope

This PRD covers six feature areas: five aligned with Timefold's platform guides and one cross-cutting UX (AI chat).

| Feature Area                                           | Description                                                                                                                      | Timefold Guide                                                                                                                                                                                                                                                                     |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Unassigned visit time-window recommendations**       | Get feasible time slots for unassigned visits so planners can offer alternatives to clients                                      | [Uncovering inefficiencies](https://docs.timefold.ai/timefold-platform/latest/guides/uncovering-inefficiencies-in-operational-planning), [Responding to disruptions](https://docs.timefold.ai/timefold-platform/latest/guides/responding-to-disruptions-with-real-time-replanning) |
| **Multi-area scheduling**                              | Run one schedule spanning 2+ nearby service areas so the solver can share employees and improve routing                          | Uncovering inefficiencies (optimize broader segments)                                                                                                                                                                                                                              |
| **Disruption impact analysis and strategy comparison** | Show affected visits, suggest strategies, optimize each branch, compare outcomes, fine-tune                                      | Responding to disruptions                                                                                                                                                                                                                                                          |
| **Freeze horizon for real-time replanning**            | Automatically pin visits already in progress or about to start so technicians aren't rerouted mid-visit                          | Responding to disruptions                                                                                                                                                                                                                                                          |
| **What-if without disruption**                         | Run capacity/demand experiments and compare schedules without a real disruption trigger                                          | Uncovering inefficiencies (what-if simulations)                                                                                                                                                                                                                                    |
| **AI chat for schedule (cross-cutting)**               | Natural language / voice as first-class entry point for all schedule actions (filter, sort, suggest, compare, optimize, what-if) | [Bryntum AI integration](https://bryntum.com/products/schedulerpro/docs/guide/Scheduler/advanced/ai-integration); build chat first, connect to US-1–US-5 as they land                                                                                                              |

### 1.2 Related Documents

| Document                                                                                          | Purpose                                                      |
| ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| [SCHEDULING_MASTER_PRD.md](./SCHEDULING_MASTER_PRD.md)                                            | Core scheduling workflows, data model, UI spec               |
| [SCHEDULE_SOLUTION_ARCHITECTURE.md](../09-scheduling/SCHEDULE_SOLUTION_ARCHITECTURE.md)           | Schedule vs Solution, what-if strategy branches, fine-tuning |
| [ESS_FSR_DUAL_MODEL_ARCHITECTURE.md](../09-scheduling/ess-fsr/ESS_FSR_DUAL_MODEL_ARCHITECTURE.md) | ESS+FSR integration, recommendations, real-time              |
| [CAIRE_FEATURE_ROADMAP.md](../09-scheduling/ess-fsr/CAIRE_FEATURE_ROADMAP.md)                     | Feature → ESS/FSR mapping                                    |
| [ESS_FSR_PROJECT_PLAN.md](../09-scheduling/ess-fsr/ESS_FSR_PROJECT_PLAN.md)                       | Sprint and task breakdown                                    |
| [TIMEFOLD_GUIDES_ALIGNMENT.md](../09-scheduling/TIMEFOLD_GUIDES_ALIGNMENT.md)                     | Mapping of Timefold guide concepts to this PRD and sprints   |

---

## 2. User Stories

### US-1: Unassigned visit time-window recommendations

**As a planner**, when pre-planning produces unassigned visits, I want to get feasible time-window alternatives (e.g. "tomorrow 14:00–16:00") so that I can offer the client a new slot instead of leaving the visit unassigned.

**As a planner**, when a sick leave leaves visits unassigned (after deferring and redistributing), I want to see recommended windows for the remaining unassigned visits so that I can reschedule them.

#### Acceptance criteria

- [ ] Backend calls Timefold FSR visit time-window recommendations endpoint with schedule/solution context.
- [ ] GraphQL exposes a query that returns suggested time windows for a given unassigned visit (e.g. `visitTimeWindowRecommendations(scheduleId, solutionId, visitId, timeWindows)`).
- [ ] UI shows a "Suggest times" (or equivalent) action for unassigned visits; planner can pick a returned window and optionally update the visit and re-run solve or from-patch.
- [ ] Works for both pre-planning (unsolved or solved plan) and post-disruption (solution after sick leave) contexts.

#### Touches

- FSR Recommendation API (`/recommendations/visit-time-windows`), TimefoldClient, GraphQL query, Bryntum unassigned-visit panel.

---

### US-2: Multi-area scheduling (shared employees)

**As a planner**, when two nearby service areas (e.g. Huddinge Vastra + Ostra) both have partial capacity, I want to run one schedule spanning both areas so that the solver can share employees and find better routes across the boundary.

**As a manager**, I want to compare single-area vs multi-area schedules to see if combining areas improves efficiency and reduces cost.

#### Acceptance criteria

- [ ] User can create a schedule for 2+ selected service areas (or one area plus "include linked areas" where configured).
- [ ] Optimization runs with visits and employees from all selected areas; solution assigns visits across areas.
- [ ] Metrics and continuity remain interpretable per area where needed (e.g. for reporting). API or metrics support filtering/breakdown by service area (e.g. compareSolutions or optimizationMetrics).
- [ ] Schedule creation/editing UI allows selecting multiple areas (multi-select or area group).

#### Touches

- Schedule schema (`serviceAreaIds` or equivalent), `prepareScheduleData`, ESS demand curve (combined areas), FSR input builder, schedule creation UI.

---

### US-3: Disruption impact analysis and strategy comparison

**As a planner**, when an employee calls in sick, I want to immediately see the impact (which visits are affected, which clients, SLA risk) before deciding what to do.

**As a planner**, I want the system to suggest multiple strategies (add backup, defer optional visits, reduce durations, hybrid) and let me optimize each one so that I can compare outcomes side-by-side and pick the best.

**As a planner**, after selecting a strategy, I want to fine-tune it (unpin/pin specific visits) without re-running the full optimization.

#### Acceptance criteria

- [ ] When marking an employee unavailable (e.g. sick), API returns affected visits: visitId, clientId, current assignment, optional SLA risk.
- [ ] `handleDisruption` returns strategy branches (Add backup, Defer visits, Reduce duration, Hybrid) with descriptions.
- [ ] `optimizeStrategy` runs optimization for one branch and persists solution with metadata (supplySnapshot, demandSnapshot, patchOperations).
- [ ] `compareSolutions` returns baseline + variants + deltas + a simple recommendation (e.g. by score).
- [ ] Planner can select a solution and run fine-tune (existing from-patch) or publish.
- [ ] UI: disruption panel → strategy cards → Optimize (per card or "Optimize All") → Compare panel → Select → Fine-tune / Publish.

#### Touches

- `handleDisruption` mutation (strategy branches + affected visits), `optimizeStrategy` mutation, `compareSolutions` query, existing `createSolutionFromPatch` (fine-tune), Bryntum disruption panel + compare panel.

---

### US-4: Freeze horizon for real-time replanning

**As a planner**, when replanning during the day, I want visits that are already in progress or about to start (e.g. within the next hour) to be automatically frozen so that technicians aren't rerouted mid-visit.

#### Acceptance criteria

- [ ] From-patch accepts an optional freeze horizon (e.g. "pin all assignments that start before now + 1 hour").
- [ ] When provided, every assignment with `assignedStartTime < freezeBeforeTime` is included in the pinned set and not moved by the solver.
- [ ] UI exposes a way to set or toggle freeze (e.g. "Freeze next 1h" when triggering real-time replan). When the user does not set freeze, default is documented (e.g. now + 1h or no freeze).

#### Touches

- `createSolutionFromPatch` (accept `freezeBeforeTime`), pin-sync service, from-patch payload builder, UI toggle.

---

### US-5: What-if without disruption

**As a manager**, I want to run what-if experiments ("what if we add 3 employees?", "what if demand grows 20%?") and compare the resulting schedules to understand capacity and cost trade-offs, without needing a real disruption trigger.

**What-if input (supply/demand):** Supply changes (e.g. +N employees, change availability), demand changes (e.g. defer N visits, +% demand) map to strategy branch config; same optimizeStrategy and compareSolutions backend as disruption flow.

#### Acceptance criteria

- [ ] "What-if" entry point from schedule view (e.g. button or menu) opens a flow where the user configures supply/demand changes (e.g. +N employees, defer N visits).
- [ ] Same `optimizeStrategy` and `compareSolutions` backend as disruption flow; strategy branches are created from user-configured what-if options.
- [ ] Result is displayed in the same Compare Panel as for disruption; user can select, fine-tune, or publish.

#### Touches

- Same backend as US-3; "What-if" button/modal in schedule view that creates strategy branches and routes to Compare Panel.

---

### US-6: AI chat as first-class entry point for schedule actions

**As a planner**, I want to use natural language or voice in a chat panel to perform any schedule action (filter, sort, suggest times, compare solutions, run optimization, what-if) so that I don't have to hunt for buttons and can work from one place.

The chat integrates with the **entire** schedule Bryntum UI: list (SchedulesPage), detail (ScheduleDetailPage), main scheduler (ScheduleView + SchedulerContainer), and compare (ScheduleComparePage). Same backend (GraphQL, Timefold); the chat is an alternative entry point. If we build the chat layer first, we connect each new feature (US-1–US-5) to it as we build it.

#### Acceptance criteria

- [ ] Bryntum AI chat panel (or equivalent) is available on all schedule surfaces: ScheduleView, ScheduleDetailPage, SchedulesPage, ScheduleComparePage.
- [ ] Chat receives **context** from the current page (e.g. scheduleId, solutionId, compare left/right) and can invoke **actions** that call existing GraphQL operations and Bryntum APIs (filter, sort, select, suggest times, optimize, compare, what-if).
- [ ] Each feature (US-1–US-5) that adds a button or modal also registers a chat-action so the same capability is available via natural language or voice.
- [ ] Chat is documented as experimental (Bryntum AI integration); no new backend beyond existing queries/mutations.

#### Touches

- Bryntum AI chat panel integration, shared **schedule chat context** (route + selected ids), **action registry** (intent → handler per feature), all schedule pages and SchedulerContainer (provide context, optional chat slot). Roadmap: CAIRE_FEATURE_ROADMAP, ESS_FSR_PROJECT_PLAN (sprint/task for chat shell + connect-to-feature tasks).

---

## 3. Technical Requirements

### 3.1 API Endpoints (GraphQL)

| Operation                                                                        | Type                | Purpose                                                                                                                                                                    |
| -------------------------------------------------------------------------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `visitTimeWindowRecommendations(scheduleId!, solutionId, visitId!, timeWindows)` | Query               | Return suggested time windows for an unassigned visit (US-1).                                                                                                              |
| `handleDisruption(scheduleId!, type!, entityId!)`                                | Mutation            | Return affected visits and strategy branches (US-3). Read-only: no persistence. `type`: e.g. `EMPLOYEE_UNAVAILABLE`; `entityId`: e.g. employeeId.                          |
| `optimizeStrategy(scheduleId!, strategyId!, options)`                            | Mutation            | Run optimization for one strategy branch; persist solution with metadata (US-3, US-5). `strategyId` references a strategy branch (id, name, description, estimatedImpact). |
| `compareSolutions(solutionIds!, baselineId!)`                                    | Query               | Return baseline + variants + deltas + recommendation (US-3, US-5).                                                                                                         |
| `createSolutionFromPatch(..., freezeBeforeTime)`                                 | Mutation (existing) | Extend to accept optional `freezeBeforeTime` for freeze horizon (US-4).                                                                                                    |

**Response types:** `handleDisruption` returns `AffectedVisit[]` (visitId, clientId, currentAssignment?, slaRisk?) and strategy branches (id, name, description?, estimatedImpact?). All new queries/mutations enforce organization access (Clerk + organizationId) per dashboard rules.

### 3.2 Timefold API Calls

| Feature | Timefold API                                                                   | Notes                                                                                                                                                           |
| ------- | ------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| US-1    | FSR `/recommendations/visit-time-windows` (or equivalent)                      | fitVisitId, timeWindows, modelInput; see [Timefold FSR recommendations](https://docs.timefold.ai/field-service-routing/latest/recommendations/recommendations). |
| US-3    | ESS recommendations (shift replacement), FSR from-patch (visit redistribution) | Already covered in ESS_FSR_PROJECT_PLAN Sprint 6.                                                                                                               |
| US-4    | FSR from-patch with pinned assignments                                         | Pin set built from assignments where startTime < freezeBeforeTime.                                                                                              |
| US-2    | FSR fullSolve / from-patch                                                     | No model change; input built from multiple service areas.                                                                                                       |

### 3.3 Data Model Changes

| Change                                                                    | Purpose                                                                                                                                                       |
| ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Schedule: optional `serviceAreaIds: [ID!]` (or equivalent)                | Multi-area schedule (US-2). Backward compatibility: if only `serviceAreaId` is set, treat as single-area.                                                     |
| Solution metadata: `supplySnapshot`, `demandSnapshot`, `patchOperations`  | Strategy comparison and audit (US-3). Already designed in SCHEDULE_SOLUTION_ARCHITECTURE. Schema must support storing this metadata on Solution (or related). |
| AffectedVisit (response): visitId, clientId, currentAssignment?, slaRisk? | handleDisruption response.                                                                                                                                    |
| Strategy branch (response): id, name, description?, estimatedImpact?      | handleDisruption and optimizeStrategy; strategyId references this.                                                                                            |

### 3.4 UI Components (Bryntum / Dashboard)

| Component                                      | Purpose                                                                            |
| ---------------------------------------------- | ---------------------------------------------------------------------------------- |
| Unassigned visit list + "Suggest times" action | US-1: call recommendation query, show slots, allow selection.                      |
| Disruption panel                               | US-3: show affected visits, strategy cards, Optimize buttons.                      |
| Compare panel                                  | US-3, US-5: metric matrix, recommendation, Select / Fine-tune / Publish.           |
| Freeze toggle (e.g. "Freeze next 1h")          | US-4: pass freezeBeforeTime when triggering real-time from-patch.                  |
| Schedule creation: multi-select service areas  | US-2.                                                                              |
| "What-if" button / modal                       | US-5: configure supply/demand changes, create branches, open Compare Panel.        |
| AI chat panel (all schedule surfaces)          | US-6: same actions as above via natural language/voice; context from current page. |

### 3.5 AI chat as alternative entry point (Bryntum Scheduler Pro) — US-6

[Bryntum Scheduler Pro’s AI integration](https://bryntum.com/products/schedulerpro/docs/guide/Scheduler/advanced/ai-integration) provides a chat panel so planners can type or speak to interact with the schedule (filter, sort, select, add/update/delete records). The same user stories can be fulfilled via **natural language or voice** in addition to buttons; the backend (GraphQL + Timefold) is unchanged.

| User story                              | Button / UI today                                      | AI chat equivalent (examples)                                                                                                                                                                             |
| --------------------------------------- | ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **US-1** (Suggest times for unassigned) | Unassigned list + "Suggest times"                      | "Suggest times for this visit" / "What slots can we offer for visit X?" → agent calls `visitTimeWindowRecommendations`, shows result.                                                                     |
| **US-2** (Multi-area)                   | Schedule creation: multi-select areas                  | "Create a schedule for Huddinge Vastra and Ostra" / "Compare single vs multi-area for tomorrow" → agent drives schedule creation or comparison.                                                           |
| **US-3** (Disruption + strategies)      | Disruption panel → strategy cards → Optimize → Compare | "Anna is sick — what's the impact?" → `handleDisruption`. "Run add backup" / "Compare add backup vs defer visits" → `optimizeStrategy`, `compareSolutions`.                                               |
| **US-4** (Freeze horizon)               | "Freeze next 1h" toggle                                | "Replan but freeze the next hour" / "Don't move anything starting in the next 60 minutes" → from-patch with `freezeBeforeTime`.                                                                           |
| **US-5** (What-if)                      | "What-if" button / modal                               | "What if we add 3 employees?" / "What if demand grows 20%?" → agent opens what-if flow or creates strategy branches and routes to Compare Panel.                                                          |
| **US-6** (Chat surface)                 | —                                                      | Chat panel on all schedule pages (list, detail, scheduler, compare); context (scheduleId, solutionId, compare state) + action registry so any of the above can be triggered by natural language or voice. |

**Implementation note:** Wire the Bryntum AI chat panel (experimental) to the same GraphQL operations and Timefold calls as the existing UI. No new backend. Build the chat shell and action registry first (US-6); then add "connect chat to [feature]" tasks as US-1–US-5 are implemented, so every new feature is both button- and chat-accessible.

---

## 4. Dependencies

| User Story                              | ESS+FSR Sprints Required                                                        | Notes                                                                                                                     |
| --------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| US-1 (Time-window recommendations)      | FSR client and schedule/solution loading                                        | Can be built on FSR-only; no ESS dependency.                                                                              |
| US-2 (Multi-area)                       | Sprint 3 (schema, prepareScheduleData)                                          | Schema + data aggregation; can proceed once Schedule and FSR input builder exist.                                         |
| US-3 (Disruption + strategy comparison) | Sprint 6 (disruption handler, ESS recommendations), Sprint 7 (impact, branches) | handleDisruption and optimizeStrategy build on Night 26–28.                                                               |
| US-4 (Freeze horizon)                   | createSolutionFromPatch exists                                                  | Extension to existing from-patch flow.                                                                                    |
| US-5 (What-if)                          | Same as US-3                                                                    | Same backend; different UI entry point.                                                                                   |
| US-6 (AI chat)                          | None (chat is UI layer)                                                         | Build chat shell + action registry first; add "connect chat to [feature]" tasks as US-1–US-5 land. Same GraphQL/Timefold. |

Implementation order in ESS_FSR_PROJECT_PLAN: Night 31–35 (Sprint 7) deliver US-1 backend/API/UI and US-4; Sprint 13 (Night 61–65) delivers US-3 and US-5; Sprint 14 (Night 66–70) delivers US-2. US-6: dedicate an early sprint (or parallel track) for chat shell + registry; then one connection task per feature as it ships.

---

## 5. Out of Scope

The following are **not** in scope for this PRD:

- **Efficiency X-ray** — Future Timefold feature; automatic reports on bottlenecks. Will be covered when Timefold releases it.
- **Reality check** — Timefold roadmap feature comparing planned vs executed plans. Deferred.
- **Mobile push notifications** for schedule changes — Communication to staff is called out in the real-time guide but is a separate product decision; solution metadata already supports generating a "what changed" summary for future use.
- **Native "max distinct vehicles per client" in FSR** — Continuity is achieved today via pool + preferredVehicles; see [CONTINUITY_AND_PRIORITIES.md](../09-scheduling/ess-fsr/CONTINUITY_AND_PRIORITIES.md).
