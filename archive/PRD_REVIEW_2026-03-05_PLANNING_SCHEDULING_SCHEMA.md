# PRD / Plan Review: Planning, Scheduling & Schema Resources

**Date:** 2026-03-05  
**Documents reviewed:** CAIRE_PLANNING_PRD.md, CAIRE_SCHEDULING_PRD.md, JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES.md, be-agent-service `.cursor/agents/timefold-specialist.md`  
**Method:** Parallel expert review (framework-docs-researcher, architecture-strategist, explore).

---

## 1. Feasibility (external: Timefold & Bryntum)

### Timefold FSR / ESS

| Area                             | Finding                                                                                                                                                                                                                                                        |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **visitDependencies**            | Low risk. API supports `precedingVisit` + `minDelay` (e.g. PT3H); same-day ordering and spread-over-week map cleanly. No documented limit on count; very large DAGs may affect solve time.                                                                     |
| **Visit groups (e.g. Dubbel)**   | Low risk. FSR `visitGroups[]` with “No semi-assigned visit groups”; schema/UI must keep group membership consistent when building FSR input.                                                                                                                   |
| **preferredVehicles**            | Low risk. “Preferred (pool 15, weight 2)” is supported; **weight is solver/config**, not FSR JSON — clarify in PRD that dashboard applies Preferred scenario config.                                                                                           |
| **from-patch**                   | Use **route-plans from-patch** (`POST /v1/route-plans/{id}/from-patch`) for pin + re-solve. Confirm API key/plan includes from-patch; validate payload size with many pins. **Platform dataset-centric from-patch is preview** — not in scope for current PRD. |
| **Recommendations (US-7, US-8)** | `visit-recommend-time-windows` exists; “fill gaps” / “propose additional visits” is implemented in-app (candidates → recommendations → add to plan → solve/from-patch). Note latency if many recommendations per day.                                          |
| **ESS+FSR**                      | Combined metrics and convergence depend on Platform/tenant config; not fully verifiable from FSR docs alone.                                                                                                                                                   |

### Bryntum Scheduler Pro

| Area            | Finding                                                                                                                                                                         |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Version**     | 7.0.x / 7.1.x; 7.1 is a safe target.                                                                                                                                            |
| **Day view**    | Use day-oriented preset (e.g. `hourAndDay`).                                                                                                                                    |
| **100+ visits** | Feasible; virtualization supports 100–500 events in day view. Avoid full-horizon load for day-focused UI; tune `eventReleaseThreshold` if needed.                               |
| **Pin / drag**  | No built-in “pinned”; use event-level `readOnly` or custom `pinned` and disable drag/resize for pinned events; build from-patch (pinningRequested, minStartTravelTime) on save. |

---

## 2. Codebase fit

| Check                                    | Result                                                                                                                                                                                |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **docs/docs_2.0/09-scheduling/**         | All referenced specs exist: MOVABLE_VISITS, PLANNING_WINDOW_STRATEGY, PREPLANNING_BACKEND_ANALYSIS, SCHEDULE_SOLUTION_ARCHITECTURE, SOLUTION_UI_SPECIFICATION, METRICS_SPECIFICATION. |
| **docs/docs_2.0/09-scheduling/ess-fsr/** | ESS_FSR_DUAL_MODEL_ARCHITECTURE, CAIRE_FEATURE_ROADMAP, ESS_FSR_PROJECT_PLAN exist.                                                                                                   |
| **apps/dashboard**                       | Exists; Bryntum scheduling UI.                                                                                                                                                        |
| **packages/graphql**                     | Exists; Timefold-related operations (startOptimization, createSolutionFromPatch, etc.).                                                                                               |
| **apps/dashboard-server**                | Timefold/FSR integrated: `src/services/timefold/`, `src/services/bridge/optimization/`, `src/routes/webhooks/timefold.ts`, solution/schedule mutations.                               |
| **Broken reference**                     | `bryntum_consultant_specs/bryntum_timeplan.md` references non-existent `SOLUTION_UI_PRD.md`; should point to `SOLUTION_UI_SPECIFICATION.md`.                                          |

---

## 3. Architecture compliance

| Principle                | Status                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Docs in docs/**        | Compliant; PRDs and specs under `docs/`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **One DB per server**    | Compliant; single schema/DB for planning and scheduling.                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Packages pure**        | Compliant as long as FSR/import/solver logic stays in apps (dashboard-server).                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| **No direct violations** | None found.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **Risks**                | (1) PRDs do not state that backend = `apps/dashboard-server`, UI = `apps/dashboard`, so implementers might put logic in packages. (2) No explicit GraphQL rules: resolver layout (one file per query/mutation), **direct hooks only** (no wrappers). (3) “Schema”/“scenarios” could be read as protected config — clarify: scenario/solver config = **data or app env**, not codegen/eslint/root package.json. (4) Planning PRD evidence path `docs/brainstorms/...` refers to **be-agent-service**; clarify repo in PRD. |

---

## 4. Recommended plan / PRD changes

### 4.1 All three PRDs

- **Add “Architecture & implementation boundaries”** (or equivalent):
  - **Backend:** All scheduling/planning backend (import, FSR/ESS input, solver, scenarios) in **`apps/dashboard-server`**; resolvers under `resolvers/{domain}/{topic}/queries|mutations/`, one file per operation, named exports.
  - **Frontend:** **`apps/dashboard`**; use **direct GraphQL hooks** from `@appcaire/graphql` only; **no wrapper hooks**.
  - **Schema/types:** **`packages/graphql`**; after .graphql changes run `yarn workspace @appcaire/graphql codegen`.
  - **Config:** Scenario/solver presets = **data (DB) or app env** (e.g. dashboard-server `.env` for Timefold); **not** changes to protected monorepo config.

### 4.2 Timefold / Bryntum (from framework research)

1. **from-patch:** State explicitly that **route-plans from-patch** is the supported mechanism for “pin and re-optimize”; Platform dataset-centric from-patch is out of scope.
2. **Recommendations:** Specify that US-7/US-8 use `visit-recommend-time-windows` and that “fill gaps”/“propose visits” is implemented in-app; note latency for many recommendations.
3. **Visit groups:** In “Resources & schema-driven constraints,” map visit groups (e.g. Dubbel) to FSR `visitGroups` and “No semi-assigned visit groups”; schema/UI keeps group membership consistent.
4. **Bryntum:** In Scheduling US-1, add: day view primary; 100–500 events per day with virtualization; if count grows, load visible day or apply filters.
5. **Preferred weight:** Clarify that “weight 2” is a **solver/scenario configuration** (not FSR JSON); add AC or design note that dashboard invokes FSR with Preferred scenario so continuity vs efficiency is reproducible.

### 4.3 Cross-repo reference

- **CAIRE_PLANNING_PRD.md:** Clarify that `docs/brainstorms/2026-03-03-continuity-config-weights-brainstorm.md` is in **be-agent-service** (`recurring-visits/docs/brainstorms/`).

### 4.4 Fix broken link

- In `docs/docs_2.0/05-prd/bryntum_consultant_specs/bryntum_timeplan.md`: change `SOLUTION_UI_PRD.md` to `SOLUTION_UI_SPECIFICATION.md` (and verify anchor `#score-and-metrics-display`).

---

## 5. Summary

| Dimension                  | Result                                                                                                                                                                                                   |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Feasibility (external)** | Timefold FSR (visitDependencies, visit groups, preferredVehicles, from-patch, recommendations) and Bryntum (day view, 100+ visits, pin/drag) are feasible with the noted clarifications and API choices. |
| **Codebase fit**           | All PRD-referenced paths exist; dashboard-server has Timefold/FSR integration; one broken link in Bryntum consultant spec.                                                                               |
| **Architecture**           | Compliant if implementation stays in apps and uses direct hooks; add explicit boundaries and GraphQL/config rules to PRDs to avoid drift.                                                                |
| **Recommended edits**      | Add architecture boundaries to all three PRDs; clarify from-patch, recommendations, visit groups, Preferred weight, and evidence path; fix SOLUTION_UI_PRD → SOLUTION_UI_SPECIFICATION.                  |
