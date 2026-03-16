# Pre-Planning Backend Architecture Analysis

**Version:** 2.0  
**Date:** 2025-12-11  
**Purpose:** Analyze backend architecture support for pre-planning and locate mapper specifications for **Caire 2.0** (normalized data model)

---

## ⚠️ Important: Caire 2.0 Architecture Change

**Caire 1.0 (Legacy):**

- External Systems → Timefold JSON → Database (stores Timefold JSON)
- Mappers: External → Timefold JSON format

**Caire 2.0 (New Architecture):**

- External Systems → **Normalized Database** → GraphQL → Bryntum
- **No Timefold JSON storage** - only normalized relational tables
- Mappers: External → Normalized Database → Bryntum

**This document focuses on Caire 2.0 requirements.**

---

## Executive Summary

### Pre-Planning Support Status

| Component          | Status           | Notes                                                                    |
| ------------------ | ---------------- | ------------------------------------------------------------------------ |
| **Data Model**     | ✅ **Supported** | `visit_templates`, `templates` (slingor), `schedule_groups` tables exist |
| **API Design**     | ⚠️ **Partial**   | Missing specific pre-planning GraphQL operations                         |
| **Architecture**   | ⚠️ **Mentioned** | Brief mention, no detailed implementation                                |
| **Mappers (v2.0)** | ❌ **Missing**   | No mapper specifications for v2.0 normalized data model                  |

### Mapper Specifications Location

| Mapper Type                         | Location                                             | Status                | Version           |
| ----------------------------------- | ---------------------------------------------------- | --------------------- | ----------------- |
| **Carefox → Timefold**              | `src/features/scheduling/services/mappers/README.md` | ✅ Documented         | **v1.0 (Legacy)** |
| **eCare CSV → Timefold**            | `docs/SLINGOR/SCHEDULING/00_OVERVIEW.md`             | ✅ Mentioned          | **v1.0 (Legacy)** |
| **Bryntum ↔ Database**              | `docs/BRYNTUM_CAIRE/COMPONENTS_AND_MAPPERS.md`       | ✅ Documented         | **v1.0 (Legacy)** |
| **Timefold → Database**             | `src/features/scheduling/services/mappers/README.md` | ✅ Documented         | **v1.0 (Legacy)** |
| **External → Normalized DB (v2.0)** | ❌ **Missing**                                       | Need for v2.0         |
| **Normalized DB → Bryntum (v2.0)**  | ❌ **Missing**                                       | Need for v2.0         |
| **Pre-Planning Mappers (v2.0)**     | ❌ **Missing**                                       | Need to be documented |

---

## 1. Data Model Support for Pre-Planning

### ✅ Supported Tables

**From `data-model-v2.md`:**

#### 1.1 `visit_templates` (Movable Visits)

- **Purpose:** Movable visit templates from municipalities (recurring work orders)
- **Key Fields:**
  - `frequency` (daily, weekly, bi-weekly, monthly)
  - `preferredWindowStart/End` (preferred time windows)
  - `allowedWindowStart/End` (allowed time windows)
  - `status` (draft, suggested, preferred, final, converted)
  - `lifecycleStatus` (identified, user_accepted, planned_1st, etc.)
- **Relationships:**
  - N→1 to `clients`, `organizations`, `service_areas`
  - 1→N to `visits` (via `visits.movableVisitId`)
  - 1→N to `movable_visit_assignments` (if exists)

#### 1.2 `templates` (Slinga)

- **Purpose:** Reusable daily or weekly schedule patterns
- **Key Fields:**
  - `recurrenceRule` (e.g., "Mon-Fri")
  - `patternJson` (sparse representation of visits/shifts)
  - `status` (draft, suggested, published, archived)
- **Relationships:**
  - N→1 to `organizations`
  - 1→N to `template_visits`, `template_employees`, `template_constraints`

#### 1.3 `schedule_groups`

- **Purpose:** Planning sessions that group multiple schedules (horizon planning)
- **Key Fields:**
  - `startDate`, `endDate` (planning horizon)
  - `name`, `description`
  - References to `templateId`, `scenarioId`, `configId`
- **Relationships:**
  - N→1 to `organizations`, `templates`, `scenarios`, `solver_configs`
  - 1→N to `schedules`

#### 1.4 `visits` (with pinned flag)

- **Key Fields:**
  - `pinned` (boolean) - Is visit pinned/locked?
  - `isMovable` (boolean) - Can be moved during optimization
  - `movableVisitId` (FK to `visit_templates`)
- **Support:** Pinned/unpinned visit distinction for pre-planning

### ⚠️ Missing Tables/Fields

1. **`movable_visit_assignments`** - Referenced in data model but not fully defined
   - Should store optimized assignments for movable visits
   - Links `visit_templates` to `schedules` and `employees`

2. **`template_visits`** - Referenced but not fully defined
   - Should store visits within a slinga template
   - Fields: `slinga_id`, `client_id`, `planned_start_time`, `sequence_index`, `pinned`

3. **`template_employees`** - Referenced but not fully defined
   - Should store employees assigned to slinga
   - Fields: `slinga_id`, `employee_id`, `weekday`, `shift_start`, `shift_end`

---

## 2. API Design Support for Pre-Planning

### Current GraphQL Operations (from `API_DESIGN_V2.md`)

**Existing Operations:**

- Visit Templates: 2 queries, 5 mutations (CRUD + lifecycle + convert)
- Templates (Slinga): 2 queries, 3 mutations (CRUD + instantiate)
- Schedule Groups: 2 queries, 3 mutations (CRUD)

### ❌ Missing Pre-Planning Operations

**Required GraphQL Operations:**

#### Queries:

1. `prePlanningData(timeHorizon)` - Get all schedules, visits, employees for planning horizon
2. `supplyDemandBalance(timeHorizon)` - Get supply/demand metrics
3. `demandCurve(timeHorizon)` - Get demand trend data
4. `unusedHours(timeHorizon)` - Get unused hours analysis
5. `getOptimalPlacementRecommendations(visitInput)` - Get AI recommendations
6. `scheduleHealthHistory(timeHorizon)` - Get historical health metrics

#### Mutations:

1. `createMovableVisit(input)` - Create new recurring visit ✅ (exists as `createVisitTemplate`)
2. `updateMovableVisit(id, input)` - Update existing movable visit ✅ (exists as `updateVisitTemplate`)
3. `runPrePlanningOptimization(input)` - Trigger pre-planning optimization ❌ **Missing**
4. `acceptPrePlanningSolution(input)` - Pin approved visits ❌ **Missing**
5. `freezeMovableVisit(id, pattern)` - Freeze optimized pattern ❌ **Missing**
6. `unfreezeMovableVisit(id)` - Unfreeze for re-optimization ❌ **Missing**

#### Subscriptions:

1. `prePlanningProgress(jobId)` - Real-time pre-planning progress ❌ **Missing**

**Note:** Some operations may exist under different names (e.g., `createVisitTemplate` vs `createMovableVisit`). Need to verify naming consistency.

---

## 3. Architecture Support for Pre-Planning

### Current Architecture (from `architecture.md`)

**Line 94 mentions:**

> "Movable visit pre‑planning: The scheduler creates or updates visit templates. Pre‑planning runs generate proposed day/time assignments based on capacity and scenario settings. Results are stored in `proposed_changes` and surfaced via the UI."

### ⚠️ Missing Architecture Details

1. **Pre-Planning Service Layer:**
   - No service class defined for pre-planning orchestration
   - No two-stage optimization process documented
   - No pattern replication logic documented

2. **Integration Layer:**
   - No adapter for pre-planning Timefold API calls
   - No `/from-patch` endpoint usage for pre-planning
   - No pattern discovery vs employee assignment distinction

3. **Background Jobs:**
   - No job queue configuration for pre-planning
   - No progress tracking for two-stage optimization

4. **Data Flow:**
   - No documented flow from `visit_templates` → optimization → `schedules`
   - No documented flow for pattern replication

---

## 4. Mapper Specifications

### ⚠️ Legacy Mappers (Caire 1.0)

**Note:** The following mappers are for **Caire 1.0** which uses Timefold JSON storage. These are **NOT** the mappers needed for Caire 2.0.

#### 4.1 Legacy: External System → Timefold Input (v1.0)

**Location:** `src/features/scheduling/services/mappers/README.md` (Legacy)

**Legacy Mappers (v1.0):**

- ❌ **Carefox → Timefold:** `carefox-to-timefold-input.mapper.ts` (v1.0 only)
- ❌ **eCare CSV → Timefold:** Mentioned in `docs/SLINGOR/SCHEDULING/00_OVERVIEW.md` (v1.0 only)
- ❌ **External CSV/JSON → Timefold:** `external-schedule-to-timefold-input.mapper.ts` (v1.0 only)

**Legacy Architecture (v1.0):**

```
External Sources → Orchestrator → Service Area Logic → Core Mappers → Timefold JSON → Database (JSON storage)
```

**These mappers are NOT used in Caire 2.0.**

---

### ✅ Required Mappers for Caire 2.0

**Caire 2.0 Architecture:**

```
External Sources → Normalized Database (Prisma) → GraphQL → Bryntum
```

#### 4.2 External Systems → Normalized Database (v2.0)

**Purpose:** Import external data directly into normalized database tables (no Timefold JSON intermediate)

**Required Mappers:**

1. **`carefoxToNormalizedDb.mapper.ts`**
   - **Input:** Carefox API JSON
   - **Output:** Direct database inserts/updates via Prisma
   - **Tables:** `employees`, `clients`, `visits`, `schedules`, `employee_shifts`, `employee_breaks`
   - **Location:** `packages/server/src/integrations/mappers/carefox-to-normalized-db.mapper.ts`

2. **`ecareCsvToNormalizedDb.mapper.ts`**
   - **Input:** eCare CSV file
   - **Output:** Direct database inserts/updates via Prisma
   - **Tables:** Same as Carefox mapper
   - **Location:** `packages/server/src/integrations/mappers/ecare-csv-to-normalized-db.mapper.ts`

3. **`phoniroCsvToNormalizedDb.mapper.ts`**
   - **Input:** Phoniro CSV file (actuals data)
   - **Output:** Direct database inserts/updates via Prisma
   - **Tables:** `solution_events`, `solution_assignments` (actual execution data)
   - **Location:** `packages/server/src/integrations/mappers/phoniro-csv-to-normalized-db.mapper.ts`

4. **`customJsonToNormalizedDb.mapper.ts`**
   - **Input:** Custom JSON format
   - **Output:** Direct database inserts/updates via Prisma
   - **Tables:** Generic mapping to normalized schema
   - **Location:** `packages/server/src/integrations/mappers/custom-json-to-normalized-db.mapper.ts`

5. **`pdfToMovableVisits.mapper.ts`**
   - **Input:** PDF (Biståndsbeslut) → Parsed JSON
   - **Output:** Direct database inserts to `visit_templates` table
   - **Tables:** `visit_templates`, `clients` (if new)
   - **Location:** `packages/server/src/integrations/mappers/pdf-to-movable-visits.mapper.ts`

**Key Difference from v1.0:**

- **v1.0:** External → Timefold JSON → Store JSON in database
- **v2.0:** External → Normalized tables → No JSON storage

#### 4.3 Normalized Database → Timefold Input (v2.0)

**Purpose:** Convert normalized database data to Timefold API format **only when calling Timefold API** (not for storage)

**Required Mappers:**

1. **`normalizedDbToTimefoldInput.mapper.ts`**
   - **Input:** Normalized database data (from Prisma queries)
   - **Output:** Timefold API input JSON (temporary, for API call only)
   - **Source Tables:** `schedules`, `visits`, `employees`, `employee_shifts`, `employee_breaks`, `clients`
   - **Location:** `packages/server/src/integrations/timefold/normalized-db-to-timefold-input.mapper.ts`
   - **Usage:** Called only when submitting optimization job to Timefold API

2. **`timefoldSolutionToNormalizedDb.mapper.ts`**
   - **Input:** Timefold API response (solution JSON)
   - **Output:** Database inserts/updates via Prisma
   - **Target Tables:** `solutions`, `solution_assignments`, `solution_events`, `solution_metrics`
   - **Location:** `packages/server/src/integrations/timefold/timefold-solution-to-normalized-db.mapper.ts`
   - **Usage:** Called after Timefold optimization completes

**Key Principle:**

- Timefold JSON is **temporary** - only used for API communication
- All persistent data is in **normalized database tables**
- No `rawInput` or `rawOutput` JSON storage in v2.0

#### 4.4 Normalized Database → Bryntum (v2.0)

**Purpose:** Convert normalized database data to Bryntum calendar format for frontend display

**Required Mappers:**

1. **`normalizedDbToBryntum.mapper.ts`**
   - **Input:** Normalized database data (from GraphQL queries)
   - **Output:** Bryntum calendar data format
   - **Source Tables:** `schedules`, `visits`, `employees`, `employee_shifts`, `employee_breaks`, `solution_assignments`, `solution_events`
   - **Location:** `packages/server/src/services/mappers/normalized-db-to-bryntum.mapper.ts`
   - **Key Methods:**
     - `mapScheduleToBryntum()` - Main conversion
     - `mapEmployeesToResources()` - Employee rows
     - `mapVisitsToEvents()` - Visit events
     - `mapShiftsToTimeRanges()` - Working hours
     - `mapBreaksToEvents()` - Break periods
     - `mapAssignmentsToEvents()` - Solution assignments

2. **`prePlanningDataToBryntum.mapper.ts`**
   - **Input:** Consolidated schedules across time horizon (from GraphQL)
   - **Output:** Bryntum calendar data (multi-week/month view)
   - **Source Tables:** Multiple `schedules`, `visits`, `employees` across time horizon
   - **Location:** `packages/server/src/services/mappers/pre-planning/pre-planning-data-to-bryntum.mapper.ts`
   - **Key Methods:**
     - `mapConsolidatedSchedulesToBryntum()` - Multi-week view
     - `mapPinnedVisitsToEvents()` - Pinned visits (🔒 icon)
     - `mapUnpinnedVisitsToEvents()` - Unpinned visits (dashed border)
     - `mapUnassignedVisitsToPanel()` - Unassigned visits for sidebar

3. **`rawSolverDataToBryntum.mapper.ts`** (for real-time optimization)
   - **Input:** Raw Timefold solution data (IDs only, no names/details)
   - **Output:** Minimal Bryntum data (fast, no DB lookups)
   - **Purpose:** Fast real-time updates during optimization
   - **Location:** `packages/server/src/services/mappers/pre-planning/raw-solver-data-to-bryntum.mapper.ts`
   - **Key Methods:**
     - `mapRawSolutionToBryntum()` - Fast conversion with IDs only
     - `mapRawAssignmentsToEvents()` - Minimal event data

#### 4.5 Bryntum → Normalized Database (v2.0)

**Purpose:** Convert Bryntum calendar edits back to normalized database updates

**Required Mappers:**

1. **`bryntumToNormalizedDb.mapper.ts`**
   - **Input:** Bryntum event changes (drag, drop, edit, resize)
   - **Output:** Database updates via Prisma
   - **Target Tables:** `visits` (time changes), `solution_assignments` (employee changes)
   - **Location:** `packages/server/src/services/mappers/bryntum-to-normalized-db.mapper.ts`
   - **Key Methods:**
     - `mapEventChangeToVisitUpdate()` - Visit time/duration changes
     - `mapEventMoveToAssignmentUpdate()` - Employee reassignment
     - `mapEventCreateToVisitInsert()` - New visit creation
     - `mapEventDeleteToVisitSoftDelete()` - Visit deletion

**Key Principle:**

- All user edits in Bryntum → Direct database updates
- No intermediate JSON storage
- GraphQL mutations handle the updates

### ❌ Missing Pre-Planning Mappers (v2.0)

#### 4.6 Pre-Planning Specific Mappers (v2.0)

**Required Mappers:**

1. **`visitTemplatesToNormalizedDb.mapper.ts`**
   - **Input:** `visit_templates` (movable visits) from database
   - **Output:** `visits` records inserted into database (unpinned, unassigned)
   - **Purpose:** Generate concrete visits from movable visit templates for planning horizon
   - **Location:** `packages/server/src/services/pre-planning/visit-templates-to-normalized-db.mapper.ts`
   - **Process:**
     - Query `visit_templates` for planning horizon
     - Generate `visits` records based on frequency
     - Set `pinned = false`, `isMovable = true`
     - Insert into `visits` table via Prisma

2. **`normalizedDbToTimefoldInput.mapper.ts`** (Pre-Planning variant)
   - **Input:** Normalized database data (pinned + unpinned visits) from Prisma
   - **Output:** Timefold input JSON (temporary, for API call)
   - **Purpose:** Convert pre-planning data to Timefold format for optimization
   - **Location:** `packages/server/src/integrations/timefold/normalized-db-to-timefold-input.mapper.ts`
   - **Key:** Pinned visits marked as `pinned: true`, unpinned visits as `pinned: false`

3. **`timefoldSolutionToPattern.mapper.ts`**
   - **Input:** Timefold solution (first occurrence optimization) from API
   - **Output:** Pattern object `{ dayOfWeek, timeOfDay, duration }`
   - **Purpose:** Extract pattern from optimized first occurrence
   - **Location:** `packages/server/src/services/pre-planning/timefold-solution-to-pattern.mapper.ts`
   - **Process:**
     - Parse Timefold solution JSON
     - Extract optimized time for first occurrence
     - Calculate dayOfWeek (0=Monday, 6=Sunday)
     - Extract timeOfDay and duration
     - Return pattern object

4. **`patternToNormalizedDb.mapper.ts`**
   - **Input:** Pattern object + planning horizon + `visit_templates`
   - **Output:** Database inserts for `visits` with locked times (pinned=true)
   - **Purpose:** Replicate pattern to all future occurrences in database
   - **Location:** `packages/server/src/services/pre-planning/pattern-to-normalized-db.mapper.ts`
   - **Process:**
     - For each occurrence in planning horizon:
       - Calculate date based on pattern.dayOfWeek
       - Set `plannedStartTime` = pattern.timeOfDay
       - Set `plannedEndTime` = pattern.timeOfDay + duration
       - Set `pinned = true` (locked)
       - Insert into `visits` table via Prisma

5. **`prePlanningDataToBryntum.mapper.ts`** (see 4.4 above)
   - Already documented in section 4.4

6. **`supplyDemandCalculator.service.ts`**
   - **Input:** Employee shifts + visits across horizon (from Prisma queries)
   - **Output:** Supply/demand metrics (calculated, not mapped)
   - **Purpose:** Calculate supply/demand balance from normalized data
   - **Location:** `packages/server/src/services/metrics/supply-demand-calculator.service.ts`
   - **Process:**
     - Query `employee_shifts` for horizon → Calculate supply hours
     - Query `visits` for horizon → Calculate demand hours
     - Calculate balance, utilization, unused allocation hours (client-side)
     - Return metrics object (not database writes)

7. **`rawSolverDataToBryntum.mapper.ts`** (see 4.4 above)
   - Already documented in section 4.4

---

## 5. Required Additions

### 5.1 Data Model Additions

**Missing Tables:**

1. **`movable_visit_assignments`**

   ```sql
   CREATE TABLE movable_visit_assignments (
     id UUID PRIMARY KEY,
     movable_visit_id UUID REFERENCES visit_templates(id),
     schedule_id UUID REFERENCES schedules(id),
     employee_id UUID REFERENCES employees(id),
     assigned_start_time TIMESTAMP,
     assigned_end_time TIMESTAMP,
     pattern JSONB, -- Extracted pattern (dayOfWeek, timeOfDay)
     status TEXT, -- draft, optimized, accepted, pinned
     created_at TIMESTAMP,
     updated_at TIMESTAMP
   );
   ```

2. **`template_visits`** (if not exists)

   ```sql
   CREATE TABLE template_visits (
     id UUID PRIMARY KEY,
     template_id UUID REFERENCES templates(id),
     client_id UUID REFERENCES clients(id),
     planned_start_time TIME,
     planned_end_time TIME,
     sequence_index INTEGER,
     pinned BOOLEAN DEFAULT true,
     created_at TIMESTAMP
   );
   ```

3. **`template_employees`** (if not exists)
   ```sql
   CREATE TABLE template_employees (
     id UUID PRIMARY KEY,
     template_id UUID REFERENCES templates(id),
     employee_id UUID REFERENCES employees(id),
     weekday INTEGER, -- 0=Monday, 6=Sunday
     shift_start TIME,
     shift_end TIME,
     created_at TIMESTAMP
   );
   ```

### 5.2 API Additions

**GraphQL Schema Additions:**

```graphql
# Pre-Planning Queries
type Query {
  prePlanningData(timeHorizon: TimeHorizonInput!): PrePlanningData!
  supplyDemandBalance(timeHorizon: TimeHorizonInput!): SupplyDemandBalance!
  demandCurve(timeHorizon: TimeHorizonInput!): DemandCurve!
  unusedHours(timeHorizon: TimeHorizonInput!): UnusedHoursAnalysis!
  getOptimalPlacementRecommendations(
    input: PlacementRecommendationsInput!
  ): [PlacementRecommendation!]!
  scheduleHealthHistory(timeHorizon: TimeHorizonInput!): ScheduleHealthHistory!
}

# Pre-Planning Mutations
type Mutation {
  runPrePlanningOptimization(
    input: PrePlanningOptimizationInput!
  ): OptimizationJob!
  acceptPrePlanningSolution(
    input: AcceptPrePlanningSolutionInput!
  ): AcceptPrePlanningSolutionResult!
  freezeMovableVisit(id: ID!, pattern: PatternInput!): MovableVisit!
  unfreezeMovableVisit(id: ID!): MovableVisit!
}

# Pre-Planning Subscriptions
type Subscription {
  prePlanningProgress(jobId: ID!): PrePlanningProgress!
}

# Input Types
input TimeHorizonInput {
  startDate: DateTime!
  endDate: DateTime!
  organizationId: ID!
}

input PrePlanningOptimizationInput {
  timeHorizon: TimeHorizonInput!
  movableVisitIds: [ID!]
  scenarioId: ID
  configId: ID
}

input AcceptPrePlanningSolutionInput {
  jobId: ID!
  acceptedVisitIds: [ID!]!
  applyToAllFuture: Boolean! # true = update slinga, false = this date only
}

input PatternInput {
  dayOfWeek: Int! # 0=Monday, 6=Sunday
  timeOfDay: Time!
  duration: Int! # minutes
}

input PlacementRecommendationsInput {
  visitTemplateId: ID!
  timeHorizon: TimeHorizonInput!
}

# Output Types
type PrePlanningData {
  timeHorizon: TimeHorizon!
  schedules: [Schedule!]!
  visits: [Visit!]! # Pinned + unpinned
  employees: [Employee!]!
  movableVisits: [MovableVisit!]!
}

type SupplyDemandBalance {
  timeHorizon: TimeHorizon!
  dailyMetrics: [DailySupplyDemand!]!
  aggregatedMetrics: AggregatedSupplyDemand!
  recommendations: [SupplyDemandRecommendation!]!
}

type DemandCurve {
  timeHorizon: TimeHorizon!
  dataPoints: [DemandDataPoint!]!
  aggregatedTrends: DemandTrends!
}

type UnusedHoursAnalysis {
  timeHorizon: TimeHorizon!
  totalUnusedHours: Float! # Sum of all clients' unused allocation
  perClient: [ClientUnusedHours!]! # Per-client unused allocation breakdown
  perDay: [DailyUnusedHours!]!
}

type ClientUnusedHours {
  clientId: ID!
  clientName: String!
  monthlyAllocation: Float! # Total allocated hours per month
  actualServiceHours: Float! # Actual service hours delivered
  unusedHours: Float! # monthlyAllocation - actualServiceHours
  cancellationReasons: [CancellationReason!]! # Why visits were cancelled
}

type PlacementRecommendation {
  dayOfWeek: Int!
  timeWindow: TimeWindow!
  employeeId: ID
  score: Float!
  reasoning: String!
  impactMetrics: ImpactMetrics!
}

type PrePlanningProgress {
  jobId: ID!
  status: OptimizationStatus!
  progress: Float!
  currentStage: PrePlanningStage! # "pattern_discovery" | "employee_assignment"
  metrics: PrePlanningMetrics!
}

enum PrePlanningStage {
  PATTERN_DISCOVERY
  EMPLOYEE_ASSIGNMENT
}
```

### 5.3 Service Layer Additions

**Required Services:**

1. **`PrePlanningOrchestratorService`**
   - Location: `src/features/scheduling/services/pre-planning/pre-planning-orchestrator.service.ts`
   - Responsibilities:
     - Orchestrate two-stage optimization
     - Manage pattern discovery
     - Handle pattern replication
     - Coordinate employee assignment

2. **`PatternReplicationService`**
   - Location: `src/features/scheduling/services/pre-planning/pattern-replication.service.ts`
   - Responsibilities:
     - Extract pattern from optimized first occurrence
     - Replicate pattern to all future occurrences
     - Generate visits with locked times

3. **`SupplyDemandService`**
   - Location: `src/features/scheduling/services/metrics/supply-demand.service.ts`
   - Responsibilities:
     - Calculate supply (employee capacity)
     - Calculate demand (visit hours)
     - Compute balance and unused allocation hours (client-side)
     - Generate recommendations

4. **`ScheduleHealthService`**
   - Location: `src/features/scheduling/services/metrics/schedule-health.service.ts`
   - Responsibilities:
     - Calculate stability score
     - Track utilization trends
     - Generate health metrics
     - Store historical snapshots

### 5.4 Mapper Additions (v2.0 - Normalized Data Model)

**Required Mappers for Caire 2.0:**

#### External Systems → Normalized Database

1. **`carefoxToNormalizedDb.mapper.ts`**
   - Location: `packages/server/src/integrations/mappers/carefox-to-normalized-db.mapper.ts`
   - Purpose: Import Carefox data directly to normalized tables
   - Input: Carefox API JSON
   - Output: Prisma inserts to `employees`, `clients`, `visits`, `schedules`, `employee_shifts`, `employee_breaks`
   - **No Timefold JSON intermediate**

2. **`ecareCsvToNormalizedDb.mapper.ts`**
   - Location: `packages/server/src/integrations/mappers/ecare-csv-to-normalized-db.mapper.ts`
   - Purpose: Import eCare CSV directly to normalized tables
   - Input: eCare CSV file
   - Output: Prisma inserts to normalized tables

3. **`phoniroCsvToNormalizedDb.mapper.ts`**
   - Location: `packages/server/src/integrations/mappers/phoniro-csv-to-normalized-db.mapper.ts`
   - Purpose: Import Phoniro actuals to normalized tables
   - Input: Phoniro CSV file
   - Output: Prisma inserts to `solution_events`, `solution_assignments`

4. **`customJsonToNormalizedDb.mapper.ts`**
   - Location: `packages/server/src/integrations/mappers/custom-json-to-normalized-db.mapper.ts`
   - Purpose: Generic JSON import to normalized tables
   - Input: Custom JSON format
   - Output: Prisma inserts to normalized tables

5. **`pdfToMovableVisits.mapper.ts`**
   - Location: `packages/server/src/integrations/mappers/pdf-to-movable-visits.mapper.ts`
   - Purpose: Import PDF (Biståndsbeslut) to `visit_templates` table
   - Input: PDF → Parsed JSON
   - Output: Prisma inserts to `visit_templates`, `clients`

#### Normalized Database → Timefold API (Temporary)

6. **`normalizedDbToTimefoldInput.mapper.ts`**
   - Location: `packages/server/src/integrations/timefold/normalized-db-to-timefold-input.mapper.ts`
   - Purpose: Convert normalized DB data to Timefold API format (temporary, for API call only)
   - Input: Prisma query results (`schedules`, `visits`, `employees`, etc.)
   - Output: Timefold API input JSON (temporary, not stored)
   - **Usage:** Called only when submitting optimization job

7. **`timefoldSolutionToNormalizedDb.mapper.ts`**
   - Location: `packages/server/src/integrations/timefold/timefold-solution-to-normalized-db.mapper.ts`
   - Purpose: Convert Timefold API response to normalized database
   - Input: Timefold solution JSON (from API)
   - Output: Prisma inserts to `solutions`, `solution_assignments`, `solution_events`, `solution_metrics`
   - **No JSON storage** - all data normalized

#### Normalized Database → Bryntum

8. **`normalizedDbToBryntum.mapper.ts`**
   - Location: `packages/server/src/services/mappers/normalized-db-to-bryntum.mapper.ts`
   - Purpose: Convert normalized DB data to Bryntum calendar format
   - Input: Prisma query results (from GraphQL)
   - Output: Bryntum calendar data format
   - Key Methods: `mapScheduleToBryntum()`, `mapEmployeesToResources()`, `mapVisitsToEvents()`

9. **`prePlanningDataToBryntum.mapper.ts`**
   - Location: `packages/server/src/services/mappers/pre-planning/pre-planning-data-to-bryntum.mapper.ts`
   - Purpose: Map consolidated schedules (multi-week/month) to Bryntum format
   - Input: Multiple schedules across time horizon (from GraphQL)
   - Output: Bryntum calendar data (multi-week/month view)
   - Key Methods: `mapConsolidatedSchedulesToBryntum()`, `mapPinnedVisitsToEvents()`, `mapUnpinnedVisitsToEvents()`

10. **`rawSolverDataToBryntum.mapper.ts`**
    - Location: `packages/server/src/services/mappers/pre-planning/raw-solver-data-to-bryntum.mapper.ts`
    - Purpose: Fast mapping during real-time optimization (no DB lookups)
    - Input: Raw Timefold solution data (IDs only, no names/details)
    - Output: Minimal Bryntum data (fast, for real-time updates)

#### Bryntum → Normalized Database

11. **`bryntumToNormalizedDb.mapper.ts`**
    - Location: `packages/server/src/services/mappers/bryntum-to-normalized-db.mapper.ts`
    - Purpose: Convert Bryntum edits to database updates
    - Input: Bryntum event changes (drag, drop, edit)
    - Output: Prisma updates to `visits`, `solution_assignments`

#### Pre-Planning Specific

12. **`visitTemplatesToNormalizedDb.mapper.ts`**
    - Location: `packages/server/src/services/pre-planning/visit-templates-to-normalized-db.mapper.ts`
    - Purpose: Generate concrete visits from movable visit templates
    - Input: `visit_templates` from database
    - Output: Prisma inserts to `visits` table (unpinned, unassigned)

13. **`timefoldSolutionToPattern.mapper.ts`**
    - Location: `packages/server/src/services/pre-planning/timefold-solution-to-pattern.mapper.ts`
    - Purpose: Extract pattern from optimized first occurrence
    - Input: Timefold solution JSON (from API)
    - Output: Pattern object `{ dayOfWeek, timeOfDay, duration }`

14. **`patternToNormalizedDb.mapper.ts`**
    - Location: `packages/server/src/services/pre-planning/pattern-to-normalized-db.mapper.ts`
    - Purpose: Replicate pattern to all future occurrences in database
    - Input: Pattern object + planning horizon
    - Output: Prisma inserts to `visits` table (pinned=true, locked times)

---

## 6. Mapper Specifications by System (Caire 2.0)

### 6.1 External Systems → Normalized Database (v2.0)

| System          | Format   | Mapper Location (v2.0)                                                            | Status         | Notes                                   |
| --------------- | -------- | --------------------------------------------------------------------------------- | -------------- | --------------------------------------- |
| **Carefox**     | JSON API | `packages/server/src/integrations/mappers/carefox-to-normalized-db.mapper.ts`     | ❌ **Missing** | Need v2.0 mapper (not Timefold JSON)    |
| **eCare**       | CSV      | `packages/server/src/integrations/mappers/ecare-csv-to-normalized-db.mapper.ts`   | ❌ **Missing** | Need v2.0 mapper                        |
| **Phoniro**     | CSV      | `packages/server/src/integrations/mappers/phoniro-csv-to-normalized-db.mapper.ts` | ❌ **Missing** | Need v2.0 mapper (actuals data)         |
| **Custom JSON** | JSON     | `packages/server/src/integrations/mappers/custom-json-to-normalized-db.mapper.ts` | ❌ **Missing** | Need v2.0 mapper                        |
| **CSV Upload**  | CSV      | Via custom-json mapper                                                            | ❌ **Missing** | Need v2.0 mapper                        |
| **PDF Upload**  | PDF→JSON | `packages/server/src/integrations/mappers/pdf-to-movable-visits.mapper.ts`        | ❌ **Missing** | Need v2.0 mapper (to `visit_templates`) |

**Key Difference from v1.0:**

- **v1.0:** External → Timefold JSON → Store JSON in database
- **v2.0:** External → **Normalized tables** → No JSON storage

### 6.2 Normalized Database → Timefold API (v2.0)

**Purpose:** Convert normalized DB data to Timefold format **only for API calls** (temporary, not stored)

| Source                              | Mapper Location (v2.0)                                                                | Status         | Notes                                            |
| ----------------------------------- | ------------------------------------------------------------------------------------- | -------------- | ------------------------------------------------ |
| **Normalized DB → Timefold Input**  | `packages/server/src/integrations/timefold/normalized-db-to-timefold-input.mapper.ts` | ❌ **Missing** | Convert Prisma data to Timefold JSON (temporary) |
| **Movable Visits → Timefold Input** | Same mapper (handles pinned/unpinned)                                                 | ❌ **Missing** | Part of normalized-db-to-timefold mapper         |
| **Pre-Planning → Timefold Input**   | Same mapper (handles time horizon)                                                    | ❌ **Missing** | Part of normalized-db-to-timefold mapper         |

**Key Principle:**

- Timefold JSON is **temporary** - only used for API communication
- Generated on-the-fly from normalized database
- **Not stored** in database

### 6.3 Timefold API → Normalized Database (v2.0)

| Source                                | Mapper Location (v2.0)                                                                   | Status         | Notes                                  |
| ------------------------------------- | ---------------------------------------------------------------------------------------- | -------------- | -------------------------------------- |
| **Timefold Solution → Normalized DB** | `packages/server/src/integrations/timefold/timefold-solution-to-normalized-db.mapper.ts` | ❌ **Missing** | Convert API response to Prisma inserts |
| **Timefold Solution → Pattern**       | `packages/server/src/services/pre-planning/timefold-solution-to-pattern.mapper.ts`       | ❌ **Missing** | Extract pattern for replication        |
| **Raw Solver Data → Normalized DB**   | Via timefold-solution mapper                                                             | ❌ **Missing** | Handle real-time updates               |

**Key Principle:**

- Timefold API response → Normalized database tables
- **No JSON storage** - all data normalized immediately
- Pattern extraction for pre-planning replication

### 6.4 Normalized Database → Bryntum (v2.0)

| Source                             | Mapper Location (v2.0)                                                                     | Status         | Notes                                   |
| ---------------------------------- | ------------------------------------------------------------------------------------------ | -------------- | --------------------------------------- |
| **Schedule Data → Bryntum**        | `packages/server/src/services/mappers/normalized-db-to-bryntum.mapper.ts`                  | ❌ **Missing** | Convert Prisma data to Bryntum format   |
| **Optimization Results → Bryntum** | Same mapper (handles solutions)                                                            | ❌ **Missing** | Part of normalized-db-to-bryntum mapper |
| **Pre-Planning Data → Bryntum**    | `packages/server/src/services/mappers/pre-planning/pre-planning-data-to-bryntum.mapper.ts` | ❌ **Missing** | Multi-week/month view                   |
| **Raw Solver Data → Bryntum**      | `packages/server/src/services/mappers/pre-planning/raw-solver-data-to-bryntum.mapper.ts`   | ❌ **Missing** | Fast real-time updates                  |

**Key Principle:**

- GraphQL queries Prisma → Mapper converts to Bryntum format
- **No Timefold JSON** in the flow
- Direct database → Bryntum conversion

### 6.5 Bryntum → Normalized Database (v2.0)

| Source                            | Mapper Location (v2.0)                                                    | Status         | Notes                                |
| --------------------------------- | ------------------------------------------------------------------------- | -------------- | ------------------------------------ |
| **Bryntum Edits → Normalized DB** | `packages/server/src/services/mappers/bryntum-to-normalized-db.mapper.ts` | ❌ **Missing** | Convert user edits to Prisma updates |

**Key Principle:**

- User edits in Bryntum → GraphQL mutations → Prisma updates
- **No intermediate JSON** storage

---

## 7. Recommendations

### 7.1 Immediate Actions

1. **Create v2.0 Mapper Specifications Document:**
   - Document all external system → normalized database mappers
   - Document normalized database → Timefold API mappers (temporary)
   - Document normalized database → Bryntum mappers
   - Document Bryntum → normalized database mappers
   - **Clarify:** No Timefold JSON storage in v2.0

2. **Add Pre-Planning API Operations:**
   - Add GraphQL operations to `API_DESIGN_V2.md`
   - Define input/output types
   - Document subscription requirements
   - Ensure all operations use normalized database (not JSON)

3. **Complete Data Model:**
   - Define `movable_visit_assignments` table (if needed)
   - Define `template_visits` table (if missing)
   - Define `template_employees` table (if missing)
   - Verify all pre-planning tables exist in `data-model-v2.md`

4. **Architecture Documentation:**
   - Add pre-planning service layer to `architecture.md`
   - Document two-stage optimization process
   - Document pattern replication flow
   - **Clarify:** Normalized database architecture (no JSON storage)

5. **Update Existing Documentation:**
   - Mark v1.0 mappers as "Legacy" in documentation
   - Create new v2.0 mapper specifications
   - Document the architectural change (normalized DB vs JSON storage)

### 7.2 Implementation Priority (v2.0)

**Phase 1: Core v2.0 Mappers (Week 1)**

- Create `carefoxToNormalizedDb.mapper.ts` (external → normalized DB)
- Create `normalizedDbToTimefoldInput.mapper.ts` (DB → API, temporary)
- Create `timefoldSolutionToNormalizedDb.mapper.ts` (API → DB)
- Create `normalizedDbToBryntum.mapper.ts` (DB → UI)
- Create `bryntumToNormalizedDb.mapper.ts` (UI → DB)

**Phase 2: Pre-Planning Core (Week 2)**

- Add missing GraphQL operations
- Create pre-planning orchestrator service
- Create `visitTemplatesToNormalizedDb.mapper.ts`
- Create `timefoldSolutionToPattern.mapper.ts`
- Create `patternToNormalizedDb.mapper.ts`

**Phase 3: Pre-Planning Bryntum (Week 3)**

- Create `prePlanningDataToBryntum.mapper.ts`
- Create `rawSolverDataToBryntum.mapper.ts`
- Add multi-week/month view support
- Integrate with existing Bryntum components

**Phase 4: Supply/Demand & Metrics (Week 4)**

- Create supply/demand calculator service
- Add unused allocation hours calculation (client-side: monthly allocation - actual service hours delivered)
- Create schedule health service
- Implement metrics calculations (all from normalized DB)

---

## 8. Summary

### Pre-Planning Support: ⚠️ **Partial**

- ✅ **Data Model:** Supported (visit_templates, templates, schedule_groups)
- ⚠️ **API Design:** Missing specific pre-planning operations
- ⚠️ **Architecture:** Mentioned but not detailed
- ❌ **Mappers (v2.0):** Missing all v2.0 mappers (normalized data model)

### Mapper Specifications: ❌ **Missing for v2.0**

**Legacy (v1.0) - Documented but NOT used in v2.0:**

- ✅ **Carefox → Timefold:** Documented (v1.0 only)
- ✅ **Database → Bryntum:** Documented (v1.0 only)
- ✅ **Timefold → Database:** Documented (v1.0 only)

**Required (v2.0) - All Missing:**

- ❌ **External Systems → Normalized DB:** Not documented
- ❌ **Normalized DB → Timefold API (temporary):** Not documented
- ❌ **Timefold API → Normalized DB:** Not documented
- ❌ **Normalized DB → Bryntum:** Not documented
- ❌ **Bryntum → Normalized DB:** Not documented
- ❌ **Pre-Planning Mappers (v2.0):** Not documented

### Key Architectural Change

**Caire 1.0 (Legacy):**

```
External → Timefold JSON → Store JSON in DB → Bryntum
```

**Caire 2.0 (New):**

```
External → Normalized DB (Prisma) → GraphQL → Bryntum
                ↓
         Timefold API (temporary, not stored)
```

### Next Steps

1. **✅ v2.0 Mapper Specifications Document Created:**
   - **Location:** `docs_refactor/02-api/MAPPER_SPECIFICATIONS_V2.md`
   - Documents all external → normalized DB mappers
   - Documents normalized DB → Timefold API mappers (temporary)
   - Documents normalized DB → Bryntum mappers
   - Documents Bryntum → normalized DB mappers
   - **Clarifies:** No JSON storage in v2.0

2. **Add Pre-Planning GraphQL Operations:**
   - Add to `API_DESIGN_V2.md`
   - Ensure all operations use normalized database

3. **Add Pre-Planning Service Layer:**
   - Document in `architecture.md`
   - Clarify normalized database architecture

4. **Complete Data Model:**
   - Verify all pre-planning tables exist
   - Add missing tables if needed

5. **Update Documentation:**
   - Mark v1.0 mappers as "Legacy"
   - Create comprehensive v2.0 mapper specifications

---

**Last Updated:** 2025-12-11  
**Version:** 2.0

---

## Related Documentation

- **Mapper Specifications (v2.0):** `docs_refactor/02-api/MAPPER_SPECIFICATIONS_V2.md` - Complete mapper specifications for Caire 2.0 normalized data model
- **API Design:** `docs_refactor/02-api/API_DESIGN_V2.md` - GraphQL operations and REST endpoints
- **Data Model:** `docs_refactor/03-data/data-model-v2.md` - Complete database schema
- **Architecture:** `docs_refactor/01-architecture/architecture.md` - System architecture overview
