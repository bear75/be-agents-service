# Attendo Pilot Revised Timeplan (v2)

## Overview

This revised timeplan integrates the new requirements (data gathering, generation of new slingor from scratch, and supply/demand balancing) and consolidates budgets to keep the pilot within Attendo's budget constraints (50 k SEK for preparation, 100 k SEK for each of the two execution phases). It supersedes the previous timeplan and should replace any earlier phase/budget sections in the pilot documentation. The rationale for data gathering and movable visits is based on CAIRE's hybrid scheduling approach[^1] and the principle that each slinga visit must be linked to a movable visit template[^2].

## Bryntum UI Development

| Milestone                  | Date         |
| -------------------------- | ------------ |
| Plan Review med Ballistix  | Dec 22, 2025 |
| Bryntum-utveckling startar | Jan 1, 2026  |
| Bryntum fas 1 klart        | Jan 23, 2026 |
| Bryntum fas 2 startar      | Jan 26, 2026 |

**Tillgänglig tid:** ~3 veckor (1 jan - 23 jan)

**Detaljerad Bryntum timeplan:** Se [BRYNTUM_BALLISTIX_TIMEPLAN.md](../../bryntum_consultant_specs/BRYNTUM_BALLISTIX_TIMEPLAN.md)

**Bryntum fas 1 scope:**

- Core Viewing (timeline, navigation)
- Visit Assignment (drag-drop)
- Visit CRUD (editering, pin/unpin, validering)
- Employee CRUD (lägga till/ta bort)
- Comparison (planerat vs optimerat)
- Metrics (KPI + finansiella)
- Optimization (polling-baserad, scenario lab)
- Pre-Planning (movable visits, slingor, pinned/unpinned)
- Integration (GraphQL mappers)
- Kartvy (redan implementerad i CAIRE)

**Bryntum fas 2 scope (från Jan 26, 2026):**

- WebSocket realtidsuppdateringar
- Cross-service area integration
- Advanced analytics (histogram, utilization)
- Export (PDF, Excel, iCal)
- Advanced pre-planning (AI recommendations, demand curve)

## Phase 0 – Data Gathering & Preparation

- **Dates:** Jan 12 – Jan 23, 2026
- **Budget:** ~50 k SEK

### Goal

Ensure CAIRE has the same information as manual planners. Gather one month of historical schedule data and define movable visit templates for each client and visit type. Prepare revision datasets to simulate real‑time changes.

### Tasks

- Collect historic schedules: Export one month of unplanned, planned and actual schedules from eCare. Each row should represent a single visit on a specific date. Approximately 3,000 rows for 30 days at 100 visits/day.
- Create movable visit templates: Define recurring visit templates for each client and visit type (frequency, duration, time windows, skills, priority, mandatory/optional) and assign a unique `movableVisitTemplateId` for linking to daily schedules.
- Generate revision schedules: Produce a set of daily schedule CSVs with real‑time changes (sickness, cancellations, extra visits, extended visits) to use as revision datasets for optimisation tests.

### Deliverables

- Validated daily schedule CSV (baseline) and revision CSVs.
- Movable visit template CSV with unique identifiers.

## Phase 1 – Daily & Monthly Optimisation & New Slingor

- **Dates:** Jan 30 – Feb 20, 2026
- **Budget:** ~50 k SEK

### Goal

Optimise daily and monthly schedules, incorporate slingor and movable visits, generate new slingor from scratch and compare them with existing patterns, and simulate real‑time disruptions. Provide planners with a UI that supports pinning/unpinning and drag‑and‑drop editing.

### Tasks

- Import & map data: Load the Phase 0 CSV files into CAIRE. Link each daily visit to its `movableVisitTemplateId` and mark visits as pinned or unpinned depending on whether they are part of a slinga.
- Generate new slingor from scratch: Use the movable visit templates to create new weekly patterns that optimise continuity and travel time. Compare these new slingor with the existing slingor imported from eCare and evaluate improvements.
- Optimise daily schedules: Optimise a selected day's unplanned visits and fine‑tune planned schedules by unpinning selected visits. Compare unplanned, planned, actual and optimised schedules using KPIs.
- Optimise monthly schedules: Optimise a 30‑day horizon by combining slingor and movable visits, measuring efficiency, continuity and travel time.
- Simulate real‑time changes: Apply the revision schedule to simulate disruptions. Re‑optimise and compare results against original plans and manual adjustments.
- Enhance Bryntum UI: Update the scheduler UI to support pinning/unpinning, editing planned schedules and dragging unassigned visits. Clearly distinguish between fixed and movable visits.

### Deliverables

- Data import/mapping report and verification.
- New slinga proposals and comparison metrics against existing slingor.
- KPI reports for daily and monthly optimisation.
- Real‑time optimisation demo with metrics.
- Updated UI with pinnable and drag‑and‑drop capabilities.

### Phase 1 Simplifications

**Transport mode:** Endast bil (DRIVING) – ingen differentiering. Timefold använder `transportMode: DRIVING` för alla employees.

**Data import:** Alla scheman (oplanerat, planerat, utfört) importeras via CSV från eCare. Phoniro/GPS är EJ aktuellt för Attendo.

**Kartvy:** Ingår i fas 1 för restidsvalidering – jämför manuella, optimerade och faktiska restider.

## Phase 2 – Supply/Demand Balancing & Advanced Scenarios

- **Dates:** Feb 24 – Mar 27, 2026
- **Budget:** ~100 k SEK

### Goal

Demonstrate CAIRE's ability to balance supply and demand, optimise across multiple service areas and run advanced scenarios (e.g. high demand, resource shortages). Provide management with insights via resource histograms and dashboards.

### Tasks

- Demand/supply balancing: Use unused hours, priority levels and mandatory/optional flags to balance supply and demand across service areas. Adapt shift allocations and schedules to minimise unused hours and maximise client continuity.
- Cross‑area optimisation: Optimise schedules that span multiple service areas, suggesting client moves to neighbouring areas when beneficial. Integrate multi‑day planning windows.
- Scenario simulation (use case 3): Model complex scenarios such as sudden increases in demand, service area rebalancing and resource shortages. Assess CAIRE's performance against manual adjustments.
- Resource histograms & dashboards: Develop analytics to visualise supply/demand balance, unused hours recapture and other KPIs. Provide planners and managers with insights for decision‑making.

### Fas 2 – Avancerade constraints och funktioner

**Tillägg utöver fas 1:**

| Kategori                   | Funktion                                                |
| -------------------------- | ------------------------------------------------------- |
| **Avancerade constraints** | Skills/kompetens-matching                               |
|                            | Preferenser (klient ↔ vårdgivare)                       |
|                            | Kontaktperson-logik                                     |
| **Kontinuitetsanalys**     | Full kontinuitetslogik (vem som gjort besöket tidigare) |
|                            | Kontinuitets-KPI (antal olika vårdgivare)               |
|                            | Kontaktperson-procent                                   |
| **Supply/demand över tid** | Outnyttjade timmar-pool (100 % flexibilitet)            |
|                            | Demand-analyser över tid (geografiskt, kompetens)       |
|                            | Kapacitetshistogram och dashboards                      |
| **Cross-area**             | Optimering över flera områden samtidigt                 |
|                            | Förslag om klientflytt till bättre passande område      |
| **Bryntum UI fas 2**       | Skills/kompetensfiltrering                              |
|                            | Preferensvisning                                        |
|                            | Kontaktperson-logik                                     |
|                            | Outnyttjade timmar-pool                                 |
|                            | Analyser över tid                                       |
|                            | Cross-area-vy                                           |
| **WebSocket (valfritt)**   | Realtidsuppdateringar under optimering                  |

### Deliverables

- Balanced schedules and supply/demand analysis.
- Cross‑area optimisation proposals.
- Scenario simulation reports.
- Resource histogram dashboards and analytics.

## Updating Existing Documentation

To incorporate this revised timeplan into existing documents (e.g. `PILOT_PLAN.md` or other planning materials), remove or replace the earlier "Pilot Structure & Phases" and budget tables with this new structure. Mark outdated sections as superseded or move them to an appendix to avoid confusion. The updated document should reflect the three phases (0, 1 and 2), their dates, tasks and condensed budgets. Doing so ensures the pilot plan remains aligned with Attendo's feedback and budgetary constraints.

## Related Documents

| Document                                                                                      | Description                                                     |
| --------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| [BRYNTUM_BALLISTIX_TIMEPLAN.md](../../bryntum_consultant_specs/BRYNTUM_BALLISTIX_TIMEPLAN.md) | Detailed Bryntum development timeplan for Ballistix consultants |
| [fas1-scope.md](./fas1-scope.md)                                                              | Attendo Pilot Phase 1 scope and requirements                    |
| [BRYNTUM_BACKEND_SPEC.md](../../bryntum_consultant_specs/BRYNTUM_BACKEND_SPEC.md)             | Backend API specifications for Bryntum integration              |
| [BRYNTUM_FROM_SCRATCH_PRD.md](../../bryntum_consultant_specs/BRYNTUM_FROM_SCRATCH_PRD.md)     | Full Bryntum PRD with all features                              |

## References

[^1]: [Hybrid Scheduling with Slingor | CAIRE](https://app.caire.se/platform/en/scheduling-with-slingor.html)

[^2]: Movable Visit Template documentation
