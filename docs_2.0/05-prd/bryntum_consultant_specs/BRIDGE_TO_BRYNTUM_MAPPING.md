# BRIDGE Services to Bryntum Plan Mapping

**Date:** 2026-01-22  
**Purpose:** Map BRIDGE backend services to Bryntum frontend requirements

---

## Overview

**BRIDGE Services** = Backend services that port 1.0 logic to 2.0 architecture (Prisma-based)  
**Bryntum Plan** = Frontend UI implementation plan for Phase 1

The BRIDGE services provide the **backend infrastructure** that the Bryntum frontend needs to function. This document maps which BRIDGE sprints support which Bryntum categories.

---

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│  BRYNTUM FRONTEND (apps/dashboard/)                        │
│  - SchedulerContainer, ScheduleView, ScheduleDetailPage    │
│  - Bryntum SchedulerPro components                         │
│  - UI for pre-planning, comparison, metrics                │
└─────────────────────────┬───────────────────────────────────┘
                          │ GraphQL (Apollo Client)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  GRAPHQL RESOLVERS (Sprint 4)                              │
│  apps/dashboard-server/src/graphql/resolvers/              │
│  - Thin resolvers that call bridge services                │
└─────────────────────────┬───────────────────────────────────┘
                          │ function calls
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  BRIDGE SERVICES (Sprints 1-3, 5-7)                        │
│  apps/dashboard-server/src/services/bridge/                │
│  - Ported 1.0 logic with Prisma                            │
│  - CSV mappers, metrics, optimization, pre-planning         │
└─────────────────────────┬───────────────────────────────────┘
                          │ Prisma Client
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  DATABASE 2.0                                              │
│  apps/dashboard-server/schema.prisma                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Mapping Table: BRIDGE Sprints → Bryntum Categories

| BRIDGE Sprint               | Bryntum Category                       | Status      | Relationship                                      |
| --------------------------- | -------------------------------------- | ----------- | ------------------------------------------------- |
| **Sprint 1: Foundation**    | Category 12: Integration               | ✅ Complete | Types, validation, conservation law               |
| **Sprint 2: Input Mappers** | Category 4: Three-State Import         | ⚠️ Partial  | CSV parsing for oplanerat/planerat/utfört         |
| **Sprint 3: Metrics**       | Category 7: Analytics & Metrics        | ⚠️ Partial  | Metrics calculation service                       |
| **Sprint 4: GraphQL**       | Category 12: Integration               | ✅ Complete | GraphQL resolvers connect frontend to bridge      |
| **Sprint 5: Loop**          | Category 9: Pre-Planning (Sling-minne) | ⚠️ Partial  | Loop/template services for slingor                |
| **Sprint 6: Pre-planning**  | Category 9: Pre-Planning Core          | ❌ Missing  | Movable visit services, pre-planning orchestrator |
| **Sprint 7: Integration**   | All Categories                         | ⚠️ Partial  | E2E testing, mapper integration                   |

---

## Detailed Mapping

### Sprint 1: Foundation → Category 12: Integration

**BRIDGE Services:**

- `apps/dashboard-server/src/services/bridge/types.ts` - Type definitions
- Conservation law validation

**Bryntum Needs:**

- ✅ Type safety for all data structures
- ✅ Validation ensures data integrity

**Status:** ✅ **Complete** - Foundation is ready

---

### Sprint 2: Input Mappers → Category 4: Three-State Schedule Import

**BRIDGE Services:**

- `apps/dashboard-server/src/services/bridge/mappers/csv-schedule.mapper.ts` - CSV parsing
- `apps/dashboard-server/src/services/bridge/mappers/schema/schemas/daily-schedule.schema.ts` - Schedule CSV schema
- `apps/dashboard-server/src/services/bridge/scheduling/schedule.service.ts` - Schedule CRUD

**Bryntum Needs:**

- ❌ Import oplanerat (unplanned) schedule
- ❌ Import planerat (planned/manual) schedule
- ❌ Import utfört (actual) schedule
- ❌ Three-state comparison capability

**Status:** ⚠️ **Partial** - CSV mapper exists, but:

- No GraphQL mutation for three-state import
- No frontend UI for schedule type selection
- No comparison logic

**What Exists:**

- ✅ `csv-schedule.mapper.ts` - Can parse schedule CSV
- ✅ `daily-schedule.schema.ts` - Defines CSV format
- ✅ `uploadScheduleForOrganization` mutation exists (but doesn't support three states)

**What's Missing:**

- ❌ Schedule type parameter in upload mutation (oplanerat/planerat/utfört)
- ❌ Frontend UI to select schedule type
- ❌ Comparison service to diff three states

---

### Sprint 3: Metrics → Category 7: Analytics & Metrics Display

**BRIDGE Services:**

- `apps/dashboard-server/src/services/bridge/metrics/metrics.service.ts` - Metrics calculation
- Solution metrics, employee metrics, client metrics, service area metrics

**Bryntum Needs:**

- ❌ KPI metrics panel (📊 KPI)
- ❌ Efficiency percentage display
- ❌ Supply hours total
- ❌ Demand hours total
- ❌ Balance indicator
- ❌ Unassigned visits count
- ❌ Continuity score
- ❌ Time breakdown (visits, traveling, waiting, breaks)
- ❌ Financial summary (revenue, staff cost, margin)

**Status:** ⚠️ **Partial** - Metrics service exists, but:

- No GraphQL queries for metrics
- No frontend UI to display metrics
- Metrics calculated but not exposed

**What Exists:**

- ✅ `metrics.service.ts` - Can calculate all metrics
- ✅ Metrics hierarchy: solution → org → service area → employee → client → visit

**What's Missing:**

- ❌ GraphQL queries: `scheduleMetrics`, `solutionMetrics`, `employeeMetrics`
- ❌ Frontend components: `MetricsPanel.tsx`, `KPIDashboard.tsx`
- ❌ Real-time metrics updates

---

### Sprint 4: GraphQL → Category 12: Integration

**BRIDGE Services:**

- GraphQL resolvers that call bridge services
- `apps/dashboard-server/src/graphql/resolvers/scheduling/`

**Bryntum Needs:**

- ✅ GraphQL client setup
- ✅ Schedule data fetching
- ✅ Mutation handlers
- ✅ Error handling

**Status:** ✅ **Complete** - GraphQL layer connects frontend to bridge services

**What Exists:**

- ✅ GraphQL resolvers for schedules, visits, employees
- ✅ Apollo Client setup in frontend
- ✅ Data mappers (Bryntum ↔ GraphQL)

---

### Sprint 5: Loop → Category 9: Pre-Planning (Sling-minne)

**BRIDGE Services:**

- `apps/dashboard-server/src/services/bridge/loop/loop.service.ts` - Loop CRUD
- `apps/dashboard-server/src/services/bridge/loop/loop-derivation.service.ts` - Generate loops from visits

**Bryntum Needs:**

- ❌ Sling-minne Level A: Daily continuity (same employee per slinga)
- ❌ Sling-minne Level B: Weekly continuity (same slingor repeat each week)
- ❌ Slingor visualization (grouped rows or tabs)
- ❌ Generate slingor from scratch (weekly patterns from movable visits)

**Status:** ⚠️ **Partial** - Loop services exist, but:

- No GraphQL operations for loops
- No frontend UI for slingor
- Database has `Template` model but not used

**What Exists:**

- ✅ `loop.service.ts` - Loop CRUD operations
- ✅ `loop-derivation.service.ts` - Can derive loops from visits
- ✅ `Template` model in Prisma schema (slingor)

**What's Missing:**

- ❌ GraphQL queries: `templates`, `template`
- ❌ GraphQL mutations: `createTemplate`, `updateTemplate`, `generateTemplateFromVisits`
- ❌ Frontend UI: `SlingorView.tsx`, `TemplateEditor.tsx`
- ❌ Sling-minne visualization in Bryntum

---

### Sprint 6: Pre-planning → Category 9: Pre-Planning Core

**BRIDGE Services:**

- `apps/dashboard-server/src/services/bridge/pre-planning/movable-visit.service.ts` - Movable visit CRUD
- `apps/dashboard-server/src/services/bridge/pre-planning/pre-planning-orchestrator.service.ts` - Pre-planning workflow

**Bryntum Needs:**

- ❌ Unified Pre-Planning UI
- ❌ Generate slingor from scratch (weekly patterns from movable visits)
- ❌ Compare AI slingor vs manual slingor
- ❌ Real-time changes (same UI with partial unpinning)
- ❌ Sling-minne support (Level A + B)
- ❌ Calendar view (Weekly/Bi-weekly/Monthly) with daily summary cells
- ❌ Pinned/Unpinned visual states (🔒 icon, solid vs dashed border)

**Status:** ❌ **Missing** - Services are stubs

**What Exists:**

- ✅ `VisitTemplate` model in Prisma schema (movable visits)
- ✅ `visit-template.schema.ts` - CSV schema for templates
- ⚠️ `movable-visit.service.ts` - **STUB** (returns "Not yet implemented")
- ⚠️ `pre-planning-orchestrator.service.ts` - **STUB** (returns "Not yet implemented")

**What's Missing:**

- ❌ GraphQL queries: `visitTemplates`, `prePlanningSession`
- ❌ GraphQL mutations: `createVisitTemplate`, `uploadVisitTemplatesCsv`, `startPrePlanning`, `optimizeMovableVisits`
- ❌ Frontend UI: `PrePlanningPage.tsx`, `MovableVisitsPanel.tsx`
- ❌ CSV upload modal for visit templates
- ❌ Pre-planning optimization integration

---

### Sprint 7: Integration → All Categories

**BRIDGE Services:**

- E2E testing
- Mapper integration
- `apps/dashboard-server/src/services/bridge/mappers/db-to-bryntum.mapper.ts` - Database → Bryntum format
- `apps/dashboard-server/src/services/bridge/mappers/db-to-timefold.mapper.ts` - Database → Timefold format

**Bryntum Needs:**

- ⚠️ Data mappers (Bryntum ↔ Database)
- ❌ E2E tests
- ❌ Integration validation

**Status:** ⚠️ **Partial** - Mappers exist, testing missing

**What Exists:**

- ✅ `db-to-bryntum.mapper.ts` - Converts Prisma data to Bryntum format
- ✅ `db-to-timefold.mapper.ts` - Converts Prisma data to Timefold API format

**What's Missing:**

- ❌ E2E tests for complete flows
- ❌ Integration tests for mappers
- ❌ Validation of conservation law in production

---

## Critical Path for Attendo Phase 1

Based on `BRYNTUM_IMPLEMENTATION_STATUS.md`, these are **critical** for Attendo Phase 1:

### High Priority (Required)

1. **Sprint 6: Pre-planning** → **Category 9: Pre-Planning Core**
   - Status: ❌ **Missing** (services are stubs)
   - Effort: 2 days (16 hours) per plan
   - Blocking: Grovplanering av slingor, Sling-minne

2. **Sprint 2: Input Mappers** → **Category 4: Three-State Import**
   - Status: ⚠️ **Partial** (CSV parser exists, but no three-state support)
   - Effort: ~1 day to add schedule type parameter
   - Blocking: Oplanerat/planerat/utfört comparison

3. **Sprint 3: Metrics** → **Category 7: Metrics Display**
   - Status: ⚠️ **Partial** (service exists, but no GraphQL/frontend)
   - Effort: ~1 day for GraphQL queries, ~1 day for frontend UI
   - Blocking: KPI metrics display

4. **Sprint 5: Loop** → **Category 9: Sling-minne**
   - Status: ⚠️ **Partial** (services exist, but no GraphQL/frontend)
   - Effort: ~1 day for GraphQL, ~1 day for frontend UI
   - Blocking: Sling-minne Level A + B

### Medium Priority

5. **Sprint 7: Integration** → **Category 6: Schedule Comparison**
   - Status: ❌ **Missing** (comparison logic not implemented)
   - Effort: ~1 day for comparison service
   - Blocking: AI vs manual comparison

---

## Implementation Priority

### Phase 1: Complete Backend Services (Week 1)

1. **Sprint 6: Pre-planning** (2 days)
   - Implement `movable-visit.service.ts` (port from 1.0)
   - Implement `pre-planning-orchestrator.service.ts` (port from 1.0)
   - Add GraphQL schema for `VisitTemplate`, `Template`
   - Add GraphQL resolvers for pre-planning

2. **Sprint 2: Three-State Import** (1 day)
   - Add `scheduleType` parameter to `uploadScheduleForOrganization`
   - Update CSV mapper to handle three states
   - Add comparison service

3. **Sprint 3: Metrics GraphQL** (1 day)
   - Add GraphQL queries for metrics
   - Expose metrics service via GraphQL

4. **Sprint 5: Loop GraphQL** (1 day)
   - Add GraphQL queries/mutations for templates
   - Expose loop services via GraphQL

### Phase 2: Frontend Integration (Week 2)

5. **Category 9: Pre-Planning UI** (2 days)
   - `PrePlanningPage.tsx`
   - `MovableVisitsPanel.tsx`
   - `UploadVisitTemplatesCsvModal.tsx`
   - Sling-minne visualization

6. **Category 4: Three-State Import UI** (1 day)
   - Schedule type selector
   - Comparison view

7. **Category 7: Metrics UI** (1 day)
   - `MetricsPanel.tsx`
   - `KPIDashboard.tsx`

8. **Category 6: Comparison UI** (1 day)
   - Side-by-side comparison
   - Delta metrics display

---

## Summary

| Component              | Backend Status | GraphQL Status | Frontend Status | Blocking Attendo? |
| ---------------------- | -------------- | -------------- | --------------- | ----------------- |
| **Pre-planning**       | ⚠️ Stubs       | ❌ Missing     | ❌ Missing      | ✅ **YES**        |
| **Three-State Import** | ✅ CSV parser  | ⚠️ Partial     | ❌ Missing      | ✅ **YES**        |
| **Metrics**            | ✅ Service     | ❌ Missing     | ❌ Missing      | ✅ **YES**        |
| **Loop/Sling-minne**   | ✅ Service     | ❌ Missing     | ❌ Missing      | ✅ **YES**        |
| **Comparison**         | ❌ Missing     | ❌ Missing     | ❌ Missing      | ✅ **YES**        |
| **Integration**        | ✅ Mappers     | ✅ Resolvers   | ✅ Apollo       | ❌ No             |

**Key Insight:** The BRIDGE services provide the **backend foundation**, but most are missing the **GraphQL layer** and **frontend UI** needed for Bryntum. The plan says 16 hours (2 days) for Pre-Planning Core, which aligns with implementing the missing GraphQL + frontend components.

---

**Last Updated:** 2026-01-22  
**Related Documents:**

- `BRIDGE/README.md` - BRIDGE sprint overview
- `BRYNTUM_BALLISTIX_TIMEPLAN-PHASE1.md` - Bryntum Phase 1 plan
- `BRYNTUM_IMPLEMENTATION_STATUS.md` - Current implementation status
- `PRE_PLANNING_STATUS.md` - Pre-planning detailed status
