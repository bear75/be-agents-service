# Timefold Platform Guides — Alignment with CAIRE

> **Purpose:** Map Timefold's operational-planning and real-time replanning guides to CAIRE documentation and implementation. Use this when prioritizing work, onboarding, or discussing features with Timefold.
> **Last Updated:** 2026-02-25

---

## Timefold guides (source)

| Guide                                                 | URL                                                                                                                                                                                      | Summary                                                                                    |
| ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Uncovering inefficiencies in operational planning** | [docs.timefold.ai/.../uncovering-inefficiencies-in-operational-planning](https://docs.timefold.ai/timefold-platform/latest/guides/uncovering-inefficiencies-in-operational-planning)     | Broader segments, unassigned analysis, recommendations, what-if simulations, resource mix. |
| **Responding to disruptions with real-time planning** | [docs.timefold.ai/.../responding-to-disruptions-with-real-time-replanning](https://docs.timefold.ai/timefold-platform/latest/guides/responding-to-disruptions-with-real-time-replanning) | Impact analysis, recommendations, freeze, minimal disruption, survival mode.               |

---

## Mapping: Guide concept → CAIRE doc → Implementation

| Timefold guide concept                                                       | Where it's documented in CAIRE                                                                                                                                                                                                                                   | Which sprint/tasks implement it                                                                                                                                                    |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Optimize broader segments** (multiple areas in one solve, share employees) | [SCHEDULING_ADVANCED_PLANNING_PRD.md](../05-prd/SCHEDULING_ADVANCED_PLANNING_PRD.md) US-2; [CAIRE_FEATURE_ROADMAP.md](ess-fsr/CAIRE_FEATURE_ROADMAP.md) § Supply/demand optimization                                                                             | Sprint 14 (Night 66–70): multi-area schema, data aggregation, ESS demand curve, schedule creation UI, comparison                                                                   |
| **Unassigned jobs + recommendations** (time windows for unassigned visits)   | [SCHEDULING_ADVANCED_PLANNING_PRD.md](../05-prd/SCHEDULING_ADVANCED_PLANNING_PRD.md) US-1; [CONTINUITY_AND_PRIORITIES.md](ess-fsr/CONTINUITY_AND_PRIORITIES.md) (0 unassigned priority)                                                                          | Sprint 7 (Night 31–32, 35): FSR time-window recommendation client, GraphQL + bridge, unassigned-visit UI                                                                           |
| **What-if simulations** (add/remove employees, defer visits, compare)        | [SCHEDULING_ADVANCED_PLANNING_PRD.md](../05-prd/SCHEDULING_ADVANCED_PLANNING_PRD.md) US-3, US-5; [SCHEDULE_SOLUTION_ARCHITECTURE.md](SCHEDULE_SOLUTION_ARCHITECTURE.md); [CAIRE_FEATURE_ROADMAP.md](ess-fsr/CAIRE_FEATURE_ROADMAP.md) § Disruption, § Comparison | Sprint 13 (Night 61–65): optimizeStrategy, compareSolutions, Disruption Panel, Compare Panel, What-if entry point                                                                  |
| **Impact analysis** (what does this disruption mean?)                        | [SCHEDULING_ADVANCED_PLANNING_PRD.md](../05-prd/SCHEDULING_ADVANCED_PLANNING_PRD.md) US-3; [ESS_FSR_DUAL_MODEL_ARCHITECTURE.md](ess-fsr/ESS_FSR_DUAL_MODEL_ARCHITECTURE.md) § Real-Time Disruption                                                               | Sprint 7 (Night 34): disruption handler returns affectedVisits + strategy branches                                                                                                 |
| **Freeze** (pin in-motion parts of plan)                                     | [SCHEDULING_ADVANCED_PLANNING_PRD.md](../05-prd/SCHEDULING_ADVANCED_PLANNING_PRD.md) US-4; [ESS_FSR_DUAL_MODEL_ARCHITECTURE.md](ess-fsr/ESS_FSR_DUAL_MODEL_ARCHITECTURE.md) § Real-Time                                                                          | Sprint 7 (Night 33): createSolutionFromPatch accepts freezeBeforeTime, payload builder pins early assignments                                                                      |
| **Recommendations** (shift replacement, visit reassignment)                  | [ESS_FSR_DUAL_MODEL_ARCHITECTURE.md](ess-fsr/ESS_FSR_DUAL_MODEL_ARCHITECTURE.md) § Recommendations, § Real-Time Disruption; [CAIRE_FEATURE_ROADMAP.md](ess-fsr/CAIRE_FEATURE_ROADMAP.md) § Disruption                                                            | Sprint 6 (Night 26–28): ESS recommendations, two-level workflow, GraphQL; Sprint 7 (Night 31–32, 35): FSR time-window recommendations                                              |
| **Reoptimization with minimal disruption**                                   | [SCHEDULE_SOLUTION_ARCHITECTURE.md](SCHEDULE_SOLUTION_ARCHITECTURE.md) (fine-tune, pin/unpin); [ESS_FSR_DUAL_MODEL_ARCHITECTURE.md](ess-fsr/ESS_FSR_DUAL_MODEL_ARCHITECTURE.md) § from-patch                                                                     | createSolutionFromPatch (existing); freeze horizon (Night 33) reduces moved assignments                                                                                            |
| **AI chat for schedule** (Bryntum, not Timefold)                             | [SCHEDULING_ADVANCED_PLANNING_PRD.md](../05-prd/SCHEDULING_ADVANCED_PLANNING_PRD.md) US-6; [CAIRE_FEATURE_ROADMAP.md](ess-fsr/CAIRE_FEATURE_ROADMAP.md) § Supply/demand optimization                                                                             | [Implementation plan](../../plans/2026-02-25-ai-chat-schedule-integration.md): chat shell (Night X1–X5); connect to US-1–US-5 as they land. Bryntum AI integration (experimental). |

---

## Quick links

- **Product requirements (user stories, acceptance criteria):** [SCHEDULING_ADVANCED_PLANNING_PRD.md](../05-prd/SCHEDULING_ADVANCED_PLANNING_PRD.md)
- **Feature → ESS/FSR mapping:** [CAIRE_FEATURE_ROADMAP.md](ess-fsr/CAIRE_FEATURE_ROADMAP.md)
- **Sprint and task breakdown:** [ESS_FSR_PROJECT_PLAN.md](ess-fsr/ESS_FSR_PROJECT_PLAN.md) (Night 31–35, 61–70)
- **Schedule/solution and what-if design:** [SCHEDULE_SOLUTION_ARCHITECTURE.md](SCHEDULE_SOLUTION_ARCHITECTURE.md)
- **Priority order (0 unassigned, continuity):** [CONTINUITY_AND_PRIORITIES.md](ess-fsr/CONTINUITY_AND_PRIORITIES.md)
- **When ESS is used, multi-area:** [USING_ESS.md](ess-fsr/USING_ESS.md)

---

## Out of scope (Timefold roadmap, not in current CAIRE plan)

- **Efficiency X-ray** — Future Timefold feature; automatic bottleneck reports. See [Uncovering inefficiencies](https://docs.timefold.ai/timefold-platform/latest/guides/uncovering-inefficiencies-in-operational-planning) “What’s next”.
- **Reality check** — Timefold roadmap: compare planned vs executed. See [Responding to disruptions](https://docs.timefold.ai/timefold-platform/latest/guides/responding-to-disruptions-with-real-time-replanning) “What’s next”.
- **from-patch dataset-centric API** — Timefold preview; we use existing from-patch today.
