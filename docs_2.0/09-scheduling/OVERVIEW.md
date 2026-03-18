# Caire Scheduling System Overview

> **Canonical sources:** Keep this doc as an intro/index. Do not duplicate metrics definitions, score display, or architecture details here — those live in [METRICS_SPECIFICATION.md](METRICS_SPECIFICATION.md), [SOLUTION_UI_SPECIFICATION.md](SOLUTION_UI_SPECIFICATION.md) (and [../../archive/SOLUTION_UI_PRD.md](../../archive/SOLUTION_UI_PRD.md) § Score and Metrics Display), and [SCHEDULE_SOLUTION_ARCHITECTURE.md](SCHEDULE_SOLUTION_ARCHITECTURE.md).

**Version:** 2.0  
**Last Updated:** 2026-03-18  
**Status:** Core Documentation

---

## Executive Summary

Caire is a **hybrid scheduling system** that balances human intuition with AI optimization. The system uses recurring weekly patterns (slingor) as stable baselines, with AI optimization handling movable visits, disruptions, and fine-tuning.

**Key Principles:**

- **Manual vs AI Balance** - Varies by scenario:
  - **70% manual** when fine-tuning a slinga (stable patterns with minor adjustments)
  - **0% manual** when running from scratch/unplanned (fully AI-optimized)
  - **Low manual %** when running pre-planning for movable visits (mostly AI with minimal human input)
- **Longer Planning Windows** - Use weekly/monthly windows for daily optimizations (more information = better optimization)
- **Multi-Dimensional Optimization** - Time, location, and scope dimensions

---

## Core Architecture

### Normalized Database Architecture

Caire uses a **normalized database architecture** - all data is stored in relational tables. **No Timefold JSON storage**.

```
EXTERNAL JSON/CSV  →  MAPPERS  →  NORMALIZED DATABASE  →  GraphQL API  →  Bryntum UI
     (Various)         (Per source)   (Relational tables)   (Express + Apollo)
```

**Key Principle**: External data is mapped directly to normalized database tables. Timefold JSON is generated on-the-fly when needed for optimization.

### External Data Sources

| External Source  | Format   | Mapper / Adapter        | Database Tables                     | Purpose                                              |
| ---------------- | -------- | ----------------------- | ----------------------------------- | ---------------------------------------------------- |
| **Attendo CSV**  | CSV      | AttendoAdapter + attendoToCaire | `schedules`, `visits`, `clients`, `employees`, `VisitDependency` | 3-step upload wizard; Caire format; traffic-light validation |
| **Nova Expanded**| CSV      | NovaExpandedAdapter + parseExpandedCsv | Same as above                | Expanded recurring-visits format                     |
| **Timefold API** | JSON     | TimefoldResponseMapper  | `solutions`, `solution_assignments` | AI optimization results                              |
| **Carefox API**  | JSON     | CarefoxMapper           | `schedules`, `visits`, `employees`  | Planned visits from Swedish ERP (legacy)             |
| **eCare CSV**    | CSV      | eCareMapper             | `schedules`, `visits`, `employees`  | ERP import (legacy)                                  |

### Complete Data Flow

#### Import Flow

```
1. IMPORT (External Data: CSV, JSON, API)
   ↓
2. MAPPERS (Transform to Normalized Database)
   ↓
3. DATABASE (Relational Tables: schedules, visits, employees, etc.)
   ↓
4. GraphQL API (Query/Mutation)
   ↓
5. Bryntum UI (Display/Edit)
```

#### Optimization Flow

```
1. DATABASE (Normalized Data: schedules, visits, employees)
   ↓
2. TF INPUT GENERATION (On-the-fly from database)
   ↓
3. TIMEFOLD API (Optimization)
   ↓
4. WEBHOOK (Completion callback)
   ↓
5. TF OUTPUT PROCESSING (Parse solution JSON)
   ↓
6. DATABASE (Store in normalized tables: solutions, solution_assignments)
   ↓
7. GraphQL Subscription (Real-time update)
   ↓
8. Bryntum UI (Display results)
```

**For Manual Schedules** (Baseline, Actuals): Optimization steps (2-4) are skipped, data stored directly in normalized tables.

---

## Schedule Types

| Type                | INPUT Source                                      | OUTPUT Source              | Purpose                                                                    |
| ------------------- | ------------------------------------------------- | -------------------------- | -------------------------------------------------------------------------- |
| **Original**        | Carefox/eCare API → Mapper                        | Timefold AI                | Base schedule for optimization                                             |
| **AI Optimized**    | From Original (same data)                         | Timefold AI                | AI-optimized visit assignments                                             |
| **Manual Baseline** | Derived from Original (fixed time windows)        | Manual generation          | "What was planned" for comparison                                          |
| **Phoniro Actuals** | Phoniro CSV → Mapper (Carefox only)               | Manual generation from CSV | "What actually happened" (Carefox)                                         |
| **eCare Actuals**   | eCare CSV (actuals columns) → Mapper              | Manual generation from CSV | "What actually happened" (eCare)                                           |
| **Fine-tune**       | Existing planned/optimized schedule + adjustments | Timefold AI                | User-adjusted optimization revision (preserves pinned, optimizes unpinned) |
| **Slinga-based**    | Expand slingor patterns                           | Timefold AI or manual      | Daily schedules from recurring patterns                                    |

---

## Key Concepts

### Slinga (Recurring Patterns)

A **slinga** is a weekly pattern of visits assigned to a caregiver on a specific weekday and shift (e.g., "Lisa – Monday day shift").

- **Pinned visits** - Part of fixed recurring pattern, solver cannot move unless explicitly unpinned
- **Unpinned visits** - Movable, solver can assign to any caregiver/day/time within window
- **Daily schedules** - Generated from slingor by expanding weekly patterns into concrete visits

### Planning Windows

**Strategy**: Use **longer planning windows** (weekly/monthly) for daily optimizations.

- **Daily optimization**: Use 7-day planning window
- **Weekly optimization**: Use 2-week planning window
- **Monthly optimization**: Use full month planning window

**Benefits**:

- More context for movable visits
- Cross-area optimization
- Better unused hours recapture
- Multi-dimensional optimization (time, location, scope)

See [Planning Window Strategy](./PLANNING_WINDOW_STRATEGY.md) for details.

### Pinned vs Unpinned Visits

| Type                | `pinningRequested` | Time Window           | Assigned? | Behavior                                                                                      |
| ------------------- | ------------------ | --------------------- | --------- | --------------------------------------------------------------------------------------------- |
| **Pinned assigned** | `true`             | Fixed (min=max)       | **Yes**   | Keep existing assignment (requires `itinerary` + `minStartTravelTime` from previous solution) |
| **Frozen movable**  | `false`            | Single day (narrowed) | No        | Must be assigned on date, solver chooses employee/time                                        |
| **New movable**     | `false`            | Multi-day             | No        | Solver can assign anywhere in window                                                          |

See [Pinned Visits Guide](./PINNED_VISITS_GUIDE.md) for complete details.

### Movable Visits

Visits that can be scheduled on different days within their time window:

- **New movable**: Full time window (weekly/monthly), maximum flexibility
- **Frozen movable**: Narrowed to specific date, still unassigned
- **Pinned movable**: Already assigned, keep assignment

See [Movable Visits Guide](./MOVABLE_VISITS.md) for details.

---

## System Architecture

### Backend

- **GraphQL API** (Express + Apollo Server) - Primary interface
- **Prisma ORM** (type-safe database access, replacing Drizzle)
- **WebSocket subscriptions** (real-time optimization progress)
- **Normalized database** (PostgreSQL, all relational tables, **no JSON storage**)
- **REST endpoints** (secondary, for webhooks, file operations)

### Frontend

- **Bryntum SchedulerPro v7** (professional calendar UI)
- **React 18 + TypeScript**
- **Apollo Client** (GraphQL queries/mutations/subscriptions)
- **Real-time updates** (WebSocket subscriptions for optimization progress)

### Optimization

- **Timefold Field Service Routing API** (external optimization service)
- **Planning windows** (flexible, calculated dynamically, can span any date range)
- **Multi-dimensional optimization** (time, location, scope)
- **Timefold JSON** (generated on-the-fly from normalized database, not stored)

---

## Operational Scenarios

### Scenario A: Regular Daily Planning (Stable Days)

**Goal**: Use slinga as baseline, minimize travel while respecting continuity

**Process**:

1. Import existing slingor
2. Generate daily schedule from slingor (all visits pinned)
3. Manual edits if needed (unpin some visits)
4. Optimize if needed (from-patch endpoint)
5. Review and accept/reject changes

**Value**: Predictable, efficient, continuity-preserved schedules

### Scenario B: Pre-Planning with New Clients (Growth)

**Goal**: Insert new recurring visits into existing Slingor without disruption

**Process**:

1. Create visit templates for new clients (movable visits)
2. Generate movable visits for upcoming period
3. Run pre-planning optimization (longer time horizon)
4. Review recommendations
5. Accept and pin optimal placements

**Value**: Seamless integration of new clients without breaking existing patterns

### Scenario C: Real-Time Disruptions (Chaos Days)

**Goal**: Quickly adapt when cancellations or absences occur

**Process**:

1. Detect disruption (cancellation, sick leave, urgent visit)
2. Unpin affected visits
3. Run patch optimization (from-patch endpoint)
4. Review proposed changes
5. Apply solution

**Value**: One-click replanning with minimal disruption to stable patterns

---

## Multi-Dimensional Optimization

Caire optimizes across three dimensions:

### 1. Time Dimension

- **Daily optimization**: Optimize for specific date with real-time changes
- **Weekly/Monthly domain**: Optimize movable visits across their full time window
- **Template vs Instance**: Distinguish temporary changes vs stable template updates

### 2. Location Dimension

- **Route optimization**: Minimize travel time within service areas
- **Cross-area optimization**: Optimize multiple service areas together
- **Area boundary recommendations**: Suggest moving clients between areas

### 3. Temporary vs Template Scope

- **Temporary**: Real-time changes (sick employee, cancellation) → only today's schedule
- **Template**: Stable improvements → update slinga/movable visit defaults

See [Planning Window Strategy](./PLANNING_WINDOW_STRATEGY.md) for details.

---

## Key Metrics

### Primary Metric: Efficiency

**Efficiency** = Service Hours / Shift Hours (target: ≥75%)

This is the **top priority metric** for all optimizations.

### Additional Metrics

- **Travel Time**: Total travel time reduction (target: 15-30% vs manual)
- **Continuity**: Same caregiver for recurring visits (target: ≥90%)
- **Unused Hours Recapture**: Identify and utilize cancelled hours (target: ≥80%)
- **Optimization Performance**: Completion time (target: <5 minutes for daily)

---

## Data Model

### Core Entities (Normalized Database)

All data stored in **relational tables** (Prisma + PostgreSQL):

- **Schedules**: Main schedule instances with `startDate`/`endDate` (can span multiple days)
- **Visits**: Individual care visits with time windows, skills, priority, `pinned` flag; linked to Inset (visit type)
- **Employees**: Caregivers with shifts, skills, availability, transport mode
- **Clients**: Care recipients with preferences, continuity requirements
- **Insets**: Visit types (morning_care, shower, etc.); org-scoped; `InsetGroup` + `InsetGroupMember` for dependency ordering (e.g. meals: breakfast → lunch → dinner)
- **VisitDependency**: Schedule-level visit-to-visit dependencies (preceding, succeeding, minDelay, dependencyType: spread | same_day | temporal)
- **ClientDependencyRule / ServiceAreaDependencyRule**: Client/area-level rules that generate VisitDependency
- **Slinga (Templates)**: Recurring weekly patterns stored in `templates` table
- **Visit Templates (Movable Visits)**: Flexible visits with time windows, stored in `visit_templates` table
- **Solutions**: Optimization results stored in `solutions` table
- **Solution Assignments**: Visit-to-employee assignments stored in `solution_assignments` table

### Key Architecture Principles

1. **No JSON Storage**: All data in normalized relational tables
2. **Timefold JSON Generation**: Generated on-the-fly from database when needed for optimization
3. **Planning Windows**: Calculated dynamically, not stored
   - Calculated from date ranges or visit data
   - Passed to Timefold in `modelInput.planningWindow`
   - Flexible - can be any length (daily, weekly, monthly)

See [Backend Architecture](./BACKEND_ARCHITECTURE.md) for complete data model details.

---

## API Architecture

### GraphQL (Primary) - ~50-60 Operations

- **Queries** (~30): Get schedules, visits, employees, clients, slinga, solutions
- **Mutations** (~25): Create schedules, optimize, pin/unpin visits, manage slinga
- **Subscriptions** (~5): Real-time optimization progress, schedule updates

### REST (Secondary)

- **Webhooks**: Timefold completion callbacks
- **File operations**: CSV/PDF uploads
- **Health checks**: System status

See [Backend Architecture](./BACKEND_ARCHITECTURE.md) for complete API details.

---

## Frontend Architecture

### Bryntum SchedulerPro Integration

- **Employee view**: Employees as resources, visits as events; drag-and-drop assignments
- **Client view**: Clients as resources, assignments as events; `ClientScheduler` + `ClientFilterPanel`; filters: inset names, inset groups, frequencies, employees, only-with-dependencies
- **Real-time updates**: WebSocket subscriptions for optimization progress
- **Diff view**: Compare baseline vs optimized
- **Bench panel**: Unassigned visits for drag-and-drop

### Scheduler Appearance

- **Org-level overrides**: `Organization.settings.schedulerAppearance` (category colors, frequency border colors) via `SchedulerAppearanceSection` in Operational Settings
- **Env fallbacks**: `VITE_SCHEDULER_CATEGORY_COLORS`, `VITE_SCHEDULER_FREQUENCY_COLORS` (JSON)
- **Client view appearance**: Time window background/border via `schedulerAppearanceConfig`

See [Frontend Integration](./FRONTEND_INTEGRATION.md) for details.

---

---

## Next Steps

1. Read [Backend Architecture](./BACKEND_ARCHITECTURE.md) for implementation details
2. Read [Frontend Integration](./FRONTEND_INTEGRATION.md) for UI patterns
3. Read [Timefold Integration](./TIMEFOLD_INTEGRATION.md) for optimization details
4. Read [Planning Window Strategy](./PLANNING_WINDOW_STRATEGY.md) for optimization strategy

---

## References

- [Backend Architecture](./BACKEND_ARCHITECTURE.md) - Complete backend implementation
- [Frontend Integration](./FRONTEND_INTEGRATION.md) - Bryntum UI integration
- [Timefold Integration](./TIMEFOLD_INTEGRATION.md) - Optimization engine integration
- [Planning Window Strategy](./PLANNING_WINDOW_STRATEGY.md) - Longer planning windows strategy
- [Pinned Visits Guide](./PINNED_VISITS_GUIDE.md) - Timefold pinning behavior
- [Movable Visits](./MOVABLE_VISITS.md) - Movable visits guide
