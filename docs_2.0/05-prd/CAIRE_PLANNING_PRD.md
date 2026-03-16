# Visit Planning — Product Requirements

Status: DRAFT | Owner: TBD | Last updated: 2026-03-03

## Problem

Monthly planning of recurring client visits is done manually in external systems (eCare, Carefox). Supply (staff hours) and demand (client visit allocations from biståndsbeslut) are never explicitly balanced. Movable visits have no structured placement — they land wherever someone puts them. No stable repeating pattern exists in Caire; every week starts from scratch.

## Outcome

An operations planner imports recurring visit templates, sees supply vs demand across a planning horizon, approves an AI-generated repeating pattern with all hours assigned, and publishes it as the stable baseline. At the point of approval the schedule is complete and balanced — no gaps, no unassigned demand. The schedule "just runs" from that point — no weekly re-planning unless the underlying care plan changes.

## Success Metrics

| Metric                                                 | Baseline    | Target                 |
| ------------------------------------------------------ | ----------- | ---------------------- |
| First-proposal approval rate for AI-generated patterns | TBD per org | 80%+                   |
| Client-allocated hours assigned at approval            | N/A         | 100% (no unmet demand) |
| Planning horizon in one session                        | TBD         | 14–30 days             |
| Time to produce approved repeating schedule            | TBD         | Under 2 hours          |

## Users & Jobs to be Done

| Role                   | Job                                                                 | Current pain                                                                      |
| ---------------------- | ------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Operations planner     | Produce a stable repeating schedule that balances supply and demand | Manual placement in external systems; no single view of supply vs demand in Caire |
| Scheduler (downstream) | Use the approved pattern as baseline for daily scheduling           | No stable baseline; every week starts from scratch                                |

## Scope

**In scope:** Import of movable visit templates (external system or CSV); supply vs demand view; AI-generated repeating pattern (slingor) with all hours assigned; planner review, pin, adjust; approve and publish as scheduling baseline; reset/revise plan when care plan changes significantly.

**Out of scope:** Real-time disruption handling; recapture of unused hours from cancellations; recommendation visits to fill gaps; daily re-optimization. These belong to Daily Scheduling (PRD 2).

## Architecture & implementation boundaries

- **Backend:** All planning backend (import, validation, FSR/ESS input generation, solver invocation, scenario/solver config) lives in **`apps/dashboard-server`**. Resolvers follow the monorepo pattern: `src/graphql/resolvers/{domain}/{topic}/queries/` and `mutations/` with one file per operation and named exports.
- **Frontend:** Planning UI lives in **`apps/dashboard`**. Data is loaded via **direct GraphQL hooks from `@appcaire/graphql`** (no wrapper hooks).
- **Schema & types:** GraphQL schema and generated types live in **`packages/graphql`**. After adding or changing operations, run `yarn workspace @appcaire/graphql codegen`.
- **Config:** Scenario/solver presets (e.g. Preferred, weight 2) are **data** (stored via dashboard-server DB) or **app-level environment** (e.g. `apps/dashboard-server/.env` for Timefold). They are not implemented by changing protected monorepo config (codegen, eslint, root package.json); those require architect approval.

## Schema & constraints

Planning uses the same **schema-driven** constraints and dependencies as the rest of the system. Import (CSV or external system) is mapped into this schema; pattern generation (Preferred scenario, FSR — and when used, ESS+FSR) consumes schema data (time windows, skills, continuity, **visit dependencies**, labor rules, cost groups where applicable). Schema and **standing data** (employees, clients, visits, dependency rules) are the single source for both planning and daily scheduling. For the full list of visit/customer/employee/dependency/scenario attributes, see the [Resources & schema-driven constraints](CAIRE_SCHEDULING_PRD.md#resources--schema-driven-constraints) section in the Daily Scheduling PRD.

## Scenario: Continuity & efficiency (solver strategy)

For the dashboard planning flow, the AI-generated pattern shall use the **Preferred** solver strategy so that both continuity and efficiency goals are met.

| Goal                 | Target                                                                 | Rationale                                                      |
| -------------------- | ---------------------------------------------------------------------- | -------------------------------------------------------------- |
| **Continuity**       | Each client served by ≤15 distinct caregivers over the planning window | Stable care team; fewer handovers.                             |
| **Field efficiency** | Visit time / (visit + travel) > 67.5%                                  | Slingor benchmark; paid time used for care + travel, not wait. |

**Chosen strategy:** **Preferred** — soft continuity via `preferredVehicles` (pool of preferred caregivers per client). The **weight 2** is a **solver/scenario configuration parameter** (e.g. in Timefold configuration or scenario preset), not a field in the FSR JSON; the dashboard must invoke FSR with the Preferred scenario so continuity vs efficiency is reproducible. No hard `requiredVehicles`; no wait-minimization at the cost of unassigned visits.

**Verdict (from Huddinge test tenant, 2-week pool-15 runs):** Preferred is the only strategy that meets both goals (0 clients over 15 distinct caregivers, max 12; field efficiency 85.08%) with few unassigned (4). Combo (preferred + wait-min) improves feasibility but breaks continuity (10 clients over 15). Wait-min alone is infeasible (94 unassigned) and must not be used as baseline.

**Dashboard implication:** When invoking the FSR/solver for pattern generation, use the Preferred configuration (preferredVehicles, pool 15, weight 2). Expose or report continuity (e.g. distinct caregivers per client) and field efficiency so planners can confirm the pattern meets the scenario.

_Evidence and full comparison: in **be-agent-service** repo — `recurring-visits/huddinge-package/continuity -3march/pipeline_da2de902/test_tenant/ANALYSIS_VS_GOAL.md` and `recurring-visits/docs/brainstorms/2026-03-03-continuity-config-weights-brainstorm.md`._

## User Stories

### US-1: Import movable visit templates (external system / CSV)

As an operations planner, I want to import recurring visit templates from an external system or CSV so that Caire has the demand side for planning.

**Acceptance criteria:**

- Import from configured external system (eCare, Carefox) or CSV upload
- Visit templates include frequency (daily, weekly, monthly), duration, priority, and flexible time windows
- Data is validated and mapped into Caire's normalised schema (including dependency rules where applicable), not only into a one-off CSV-shaped payload
- Import errors are surfaced with clear messages

### US-2: View supply vs demand across planning horizon

As an operations planner, I want to see supply (staff hours) and demand (client visit allocations) across the planning horizon so that I can verify balance before approving a pattern.

**Acceptance criteria:**

- Supply and demand are shown for the selected horizon (14–30 days)
- Unmet demand or excess supply is clearly visible
- View supports the same horizon used for pattern generation

### US-3: AI generates repeating pattern proposal (slingor) with all hours assigned

As an operations planner, I want the system to propose a repeating pattern with every client-allocated hour assigned so that I have a complete baseline to review.

**Acceptance criteria:**

- Solver produces a repeating pattern (e.g. 2-week or 4-week cycle)
- All demand from imported templates is assigned; no unassigned visits at approval
- Pattern respects time windows, skills, and continuity where configured
- Pattern respects **schema-defined visit dependencies and area/org rules** (same day / same week behaviour)
- **Pattern generation uses the Preferred scenario by default** (or planner explicitly selects it from planning presets). See § Scenario: Continuity & efficiency.
- Proposal is available for review within a defined time limit (e.g. under 10 minutes for typical org size)

### US-4: Planner reviews, pins, adjusts visits in the pattern

As an operations planner, I want to review the AI proposal, pin visits I want to keep, and adjust others so that the final pattern matches operational constraints.

**Acceptance criteria:**

- Planner can view the proposed pattern in a planning UI
- Planner can pin visits (fix day/time) and re-run optimization on the rest
- Planner can manually move or adjust visits within rules
- After adjustments, pattern remains fully assigned (no gaps, no unmet demand)

### US-5: Approve and publish fully assigned pattern as scheduling baseline

As an operations planner, I want to approve the pattern and publish it as the scheduling baseline so that daily scheduling can use it without re-planning each week.

**Acceptance criteria:**

- Approval is explicit (e.g. "Approve and publish" action)
- Published pattern is stored as the repeating baseline for the organisation
- Daily Scheduling (PRD 2) consumes this baseline as the source for each day
- At publication, 100% of client-allocated hours in scope are assigned

### US-6: Reset or revise the plan when care plan changes significantly

As an operations planner, I want to reset or revise the plan when client allocations or care plans change significantly so that the baseline stays accurate.

**Acceptance criteria:**

- Planner can trigger a new planning session (reset) that supersedes the current baseline
- New import and pattern generation can run; result becomes the new published baseline when approved
- Existing baseline remains in effect until the new one is published

## Roadmap

- Multi-area planning (one schedule spanning 2+ service areas)
- Municipality data integration for demand forecasting

## Open Questions

| #   | Question                                                 | Owner        | Status |
| --- | -------------------------------------------------------- | ------------ | ------ |
| 1   | Preferred planning horizon default (14 vs 28 days)?      | Product      | Open   |
| 2   | Integration order for external systems (eCare, Carefox)? | Product / IT | Open   |

## Jira

| Epic                                   | User stories     |
| -------------------------------------- | ---------------- |
| Visit Planning — Import & balance      | US-1, US-2       |
| Visit Planning — AI pattern & approval | US-3, US-4, US-5 |
| Visit Planning — Reset & revise        | US-6             |

**Scenario (Preferred, Planning):** No new ticket. Add **Preferred** as the **planning** default preset in existing scenario tasks (SCEN-BE-03, SCEN-FE-03 under C0-151). Most existing scenario tickets describe real-time scheduling; Preferred is for **Visit Planning** (pattern generation). See [JIRA_SCENARIO_PREFERRED_AND_CLEANUP.md](../10-consistency/JIRA_SCENARIO_PREFERRED_AND_CLEANUP.md).

## Related specifications

- [MOVABLE_VISITS.md](../09-scheduling/MOVABLE_VISITS.md)
- [PLANNING_WINDOW_STRATEGY.md](../09-scheduling/PLANNING_WINDOW_STRATEGY.md)
- [PREPLANNING_BACKEND_ANALYSIS.md](../09-scheduling/PREPLANNING_BACKEND_ANALYSIS.md)
- **Schema data and constraints:** Full list of visit/customer/employee/dependency/scenario attributes and how they feed planning and scheduling: see [CAIRE_SCHEDULING_PRD.md — Resources & schema-driven constraints](CAIRE_SCHEDULING_PRD.md#resources--schema-driven-constraints).
- **Continuity & efficiency scenario:** Verdict and goals above (section "Scenario: Continuity & efficiency"). Evidence: in **be-agent-service** — `recurring-visits/huddinge-package/continuity -3march/pipeline_da2de902/test_tenant/ANALYSIS_VS_GOAL.md` and `recurring-visits/docs/brainstorms/2026-03-03-continuity-config-weights-brainstorm.md`.
