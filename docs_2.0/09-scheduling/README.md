# Caire Scheduling Documentation

**Version:** 2.0  
**Last Updated:** 2026-03-18  
**Status:** ✅ Core Documentation Complete

**Single source of truth (product & UI):** **[SOLUTION_UI_SPECIFICATION.md](./SOLUTION_UI_SPECIFICATION.md)** — use this as the one place for what we build and why. For metrics definitions → [METRICS_SPECIFICATION.md](./METRICS_SPECIFICATION.md). For schedule/solution/scenario architecture → [SCHEDULE_SOLUTION_ARCHITECTURE.md](./SCHEDULE_SOLUTION_ARCHITECTURE.md). (Superseded product narrative: [../../archive/SOLUTION_UI_PRD.md](../../archive/SOLUTION_UI_PRD.md).)

---

## Overview

This section contains comprehensive scheduling documentation for Caire, updated for:

- **GraphQL API** (replacing REST)
- **Bryntum SchedulerPro UI** (replacing custom UI)
- **WebSocket subscriptions** (real-time optimization)
- **Prisma ORM** (if applicable)

## Documentation Organization

Documents are organized by descriptive names (no numbering scheme):

- **Core Documentation**: Overview, architecture, integration guides
- **Advanced Features**: Planning windows, movable visits, pinned visits
- **Pilots**: Pilot-specific documentation in [`pilots/`](./pilots/) folder

---

## Quick Navigation

### 🎯 Start Here

1. **[OVERVIEW.md](./OVERVIEW.md)** - Complete scheduling system overview
2. **[BACKEND_ARCHITECTURE.md](./BACKEND_ARCHITECTURE.md)** - Complete backend architecture

### 🏗️ Architecture & Backend

3. **[BACKEND_ARCHITECTURE.md](./BACKEND_ARCHITECTURE.md)** - Complete backend architecture
4. **[TIMEFOLD_INTEGRATION.md](./TIMEFOLD_INTEGRATION.md)** - Timefold optimization engine integration

### 🔧 Advanced Features

5. **[PINNED_VISITS_GUIDE.md](./PINNED_VISITS_GUIDE.md)** - Timefold pinning guide (movable visits, fine-tuning)
6. **[MOVABLE_VISITS.md](./MOVABLE_VISITS.md)** - Movable visits guide
7. **[PLANNING_WINDOW_STRATEGY.md](./PLANNING_WINDOW_STRATEGY.md)** - Planning window strategy (longer horizons for better optimization)
8. **[BACKEND_PLANNING_WINDOW_SUPPORT.md](./BACKEND_PLANNING_WINDOW_SUPPORT.md)** - Backend support for longer planning windows
9. **[PLANNING_WINDOW_ANALYSIS.md](./PLANNING_WINDOW_ANALYSIS.md)** - Analysis: Does backend support longer windows?

### 🎨 Frontend

10. **[FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md)** - Bryntum UI integration
11. **[PREPLANNING_FRONTEND_IMPLEMENTATION.md](./PREPLANNING_FRONTEND_IMPLEMENTATION.md)** - Pre-planning frontend implementation guide
12. **Client View** - Client-centric scheduler (`ClientScheduler`, `ClientFilterPanel`); resources = clients, events = assignments; filters: inset names, inset groups, frequencies, employees, only-with-dependencies
13. **Scheduler Appearance** - Org-level overrides via `Organization.settings.schedulerAppearance`; `SchedulerAppearanceSection` in Operational Settings; category/frequency colors, client view appearance; env fallbacks: `VITE_SCHEDULER_CATEGORY_COLORS`, `VITE_SCHEDULER_FREQUENCY_COLORS`

### 🔍 Pre-Planning Analysis

12. **[PREPLANNING_BACKEND_ANALYSIS.md](./PREPLANNING_BACKEND_ANALYSIS.md)** - Backend architecture analysis for pre-planning

### ESS + FSR integration

13. **[ess-fsr/](./ess-fsr/)** - ESS + FSR dual-model integration
    - **[USING_ESS.md](./ess-fsr/USING_ESS.md)** - When and how to use ESS (staging, flow, continuity)
    - **[CONTINUITY_AND_PRIORITIES.md](./ess-fsr/CONTINUITY_AND_PRIORITIES.md)** - Priority order (0 unassigned → 0 empty → metrics → continuity) and continuity goal
    - **[ESS_FSR_DUAL_MODEL_ARCHITECTURE.md](./ess-fsr/ESS_FSR_DUAL_MODEL_ARCHITECTURE.md)** - Dual-model architecture
    - **[ESS_FSR_PROJECT_PLAN.md](./ess-fsr/ESS_FSR_PROJECT_PLAN.md)** - Project plan and sprint breakdown

### 📤 Upload & Import

14. **[UPLOAD_ZONE_ARCHITECTURE.md](./UPLOAD_ZONE_ARCHITECTURE.md)** - 3-step upload wizard, Caire format, traffic-light validation
15. **[SCHEDULE_IMPORT_UPLOAD_FLOW.md](./SCHEDULE_IMPORT_UPLOAD_FLOW.md)** - Current vs target import flow
16. **[DEPENDENCY_CREATION_VERIFICATION.md](./DEPENDENCY_CREATION_VERIFICATION.md)** - Visit dependency creation during Attendo CSV import

### 📋 Resources & Insets

17. **[SEED_DATA_SYSTEM_SETTINGS.md](./SEED_DATA_SYSTEM_SETTINGS.md)** - Org-scoped catalog (DaySlots, Insets, InsetGroups, Skills)
18. **[INSETS_AND_CLIENT_VIEW.md](./INSETS_AND_CLIENT_VIEW.md)** - Insets, InsetGroups, client view, scheduler appearance

### 📊 Pilots

19. **[pilots/](./pilots/)** - Pilot-specific documentation
    - **[Attendo Pilot](./pilots/attendo/)** - Attendo pilot plan and data requirements

---

## Documentation Status

| Document                                                      | Status      | Notes                            |
| ------------------------------------------------------------- | ----------- | -------------------------------- |
| OVERVIEW.md                                                   | ✅ Complete | Consolidated scheduling overview |
| PINNED_VISITS_GUIDE.md                                        | ✅ Complete | Timefold pinning guide           |
| BACKEND_ARCHITECTURE.md                                       | ✅ Complete | Complete backend architecture    |
| FRONTEND_INTEGRATION.md                                       | ✅ Complete | Bryntum UI integration           |
| TIMEFOLD_INTEGRATION.md                                       | ✅ Complete | Timefold integration guide       |
| MOVABLE_VISITS.md                                             | ✅ Complete | Movable visits guide             |
| PLANNING_WINDOW_STRATEGY.md                                   | ✅ Complete | Planning window strategy         |
| BACKEND_PLANNING_WINDOW_SUPPORT.md                            | ✅ Complete | Backend support verification     |
| PLANNING_WINDOW_ANALYSIS.md                                   | ✅ Complete | Backend analysis                 |
| PREPLANNING_BACKEND_ANALYSIS.md                               | ✅ Complete | Backend architecture analysis    |
| PREPLANNING_FRONTEND_IMPLEMENTATION.md                        | ✅ Complete | Frontend implementation guide    |
| ess-fsr/ESS_FSR_PROJECT_PLAN.md                               | ✅ Keep     | ESS+FSR project plan             |
| ess-fsr/ESS_FSR_DUAL_MODEL_ARCHITECTURE.md                    | ✅ Complete | Dual-model architecture          |
| ess-fsr/CONTINUITY_AND_PRIORITIES.md                          | ✅ Complete | Priority order and continuity    |
| ess-fsr/USING_ESS.md                                          | ✅ Complete | Using ESS (staging, flow)        |
| [docs/TIMEFOLD_ESS_FSR_ENV.md](../../TIMEFOLD_ESS_FSR_ENV.md) | ✅ Complete | FSR/ESS env and staging key      |
| pilots/attendo/PILOT_PLAN.md                                  | ✅ Keep     | Attendo pilot plan               |
| pilots/attendo/DATA_REQUIREMENTS.md                           | ✅ Keep     | Attendo data requirements        |

---

## Related Documentation

### Architecture

- [`01-architecture/`](../01-architecture/) - System architecture
- [`02-api/`](../02-api/) - API design and specifications

### Frontend

- [`08-frontend/BRYNTUM_INTEGRATION.md`](../08-frontend/BRYNTUM_INTEGRATION.md) - Bryntum integration details
- [`05-prd/bryntum_consultant_specs/BRYNTUM_FROM_SCRATCH_PRD.md`](../05-prd/bryntum_consultant_specs/BRYNTUM_FROM_SCRATCH_PRD.md) - Bryntum UI PRD (from scratch)

### Data Model

- [`03-data/data-model-v2.md`](../03-data/data-model-v2.md) - Complete data model

### Documentation Structure

- [`DOCUMENTATION_STRUCTURE.md`](../DOCUMENTATION_STRUCTURE.md) - Guide to PRD vs Technical docs

---

## Contributing

When updating scheduling documentation:

1. Update the status table above
2. Ensure GraphQL API patterns are used (not REST)
3. Reference Bryntum UI patterns where applicable
4. Include WebSocket subscription patterns for real-time features
5. Update data access patterns if Prisma is used
