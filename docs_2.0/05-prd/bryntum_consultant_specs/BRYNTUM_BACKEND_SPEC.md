# Bryntum Backend API Specification

> **Archive notice:** This document is superseded for canonical API and architecture by [SCHEDULE_SOLUTION_ARCHITECTURE.md](../../09-scheduling/SCHEDULE_SOLUTION_ARCHITECTURE.md) and the GraphQL schema (code is the source of truth for API). Use this doc for historical reference only.

**Version:** 2.0  
**Date:** 2025-12-09  
**Purpose:** Complete backend API specifications for Bryntum frontend integration  
**Target Audience:** Backend developers and Bryntum consultants (for reference)

---

## Executive Summary

This document provides complete backend API specifications, data flow patterns, mapper requirements, and metrics calculations for the Bryntum frontend implementation. The backend uses a **normalized database architecture (Caire 2.0)** with no Timefold JSON storage - all data is stored in relational tables.

**Key Architecture Principles:**

- **Normalized Database:** All data stored in relational tables (Prisma + PostgreSQL)
- **GraphQL API:** Primary interface for frontend (queries, mutations, subscriptions)
- **REST Endpoints:** Used for webhooks, file operations, health checks
- **No JSON Storage:** Timefold JSON is temporary (only for API communication, not stored)
- **Metrics Calculation:** Backend calculates and stores all metrics (frontend only displays)

---

## Data Model

The backend uses a normalized data model. Key entities:

- **Schedules:** Main schedule instances
- **Visits:** Individual care visits
- **Employees:** Caregivers/staff
- **Clients:** Care recipients
- **Solutions:** Optimization results
- **Assignments:** Visit-to-employee assignments
- **Visit Templates:** Movable visits (for pre-planning)
- **Templates (Slinga):** Reusable schedule patterns
- **Schedule Groups:** Planning sessions (for pre-planning)

**Note:** Detailed schema documentation is available in `data-model-v2.md`.

---

## API Operations & Data Flow

### GraphQL Operations Overview

The backend provides approximately **71 GraphQL operations** organized into:

**Queries (~30 operations):**

- Schedule queries (get schedule, list schedules, get schedule details)
- Employee queries (get employees, get employee details, list by service area)
- Client queries (get clients, get client details, list by service area)
- Visit queries (get visits, get visit details)
- Visit template queries (movable visits)
- Template queries (Slinga templates)
- Schedule group queries (planning sessions)
- Optimization queries (get job status, get optimization history)
- Solution queries (get solution details, get solution metrics)
- Scenario queries (get scenarios, get scenario details)
- Metrics queries (schedule metrics, solution metrics, employee metrics, client metrics, service area metrics, organization metrics)
- Pre-planning queries (pre-planning data, supply/demand balance, demand curve, unused hours, optimal placement recommendations)

**Mutations (~38 operations):**

- Schedule mutations (create, update, delete, publish, duplicate)
- Visit mutations (create, update, delete, pin/unpin, assign)
- Employee mutations (CRUD operations, add skills)
- Client mutations (CRUD operations, update preferences)
- Visit template mutations (CRUD, lifecycle management, convert to visit)
- Template mutations (CRUD, instantiate template)
- Schedule group mutations (CRUD)
- Optimization mutations (run optimization, fine-tune, terminate)
- Solution mutations (accept solution)
- Scenario mutations (CRUD)
- Pre-planning mutations (create movable visit, update movable visit, run pre-planning optimization, accept pre-planning solution)

**Subscriptions (3+ operations):**

- `optimizationProgress(jobId)` - Real-time optimization progress updates
- `solutionUpdated(scheduleId)` - Notify when new solution is available
- `scheduleUpdated(scheduleId)` - Notify when schedule changes
- `prePlanningProgress(jobId)` - Real-time pre-planning optimization progress

### REST Endpoints (~15 endpoints)

REST endpoints are used for operations where GraphQL is less suitable:

**Webhooks (5 endpoints):**

- `POST /api/webhooks/timefold` - Receive Timefold optimization completion callbacks
- `POST /api/webhooks/clerk` - Sync Clerk organization and user changes
- `POST /api/webhooks/carefox` - Receive Carefox import webhooks
- `POST /api/webhooks/phoniro` - Receive Phoniro import webhooks
- `POST /api/webhooks/ecare` - Receive eCare import webhooks

**File Operations (3 endpoints):**

- `POST /api/files/upload` - Upload schedule files (CSV, JSON)
- `GET /api/files/download/:id` - Download exported files
- `GET /api/files/export/:scheduleId` - Export schedule to file

**Integration Endpoints (3 endpoints):**

- `POST /api/integrations/carefox/token` - Get Carefox API token
- `POST /api/integrations/phoniro/token` - Get Phoniro API token
- `GET /api/integrations/status` - Check integration status

**Authentication (2 endpoints):**

- `POST /api/auth/refresh` - Refresh authentication token
- `GET /api/auth/me` - Get current user information

**Health Checks (2 endpoints):**

- `GET /api/health` - Application health check
- `GET /api/health/db` - Database connection health check

---

## Data Flow Patterns

### 1. Fetch Schedule Data

**Flow:**

1. Frontend calls GraphQL query `getSchedule(id)` with schedule ID
2. Backend fetches from database (normalized tables: schedules, visits, employees, assignments, metrics, etc.)
3. Backend returns normalized GraphQL response (including pre-calculated metrics)
4. Frontend receives data and transforms via mapper functions
5. Mapper converts normalized data to Bryntum format (resources, events, assignments, calendars)
6. Frontend fetches metrics separately via `getScheduleMetrics(scheduleId)` query (metrics are pre-calculated and stored in database)
7. Bryntum SchedulerPro displays the schedule
8. Metrics panel displays fetched metrics (no calculation in frontend)

**Data Transformation:**

- **Backend → Frontend:** Normalized database structure → Bryntum data format
- **Mapper Function:** `mapScheduleToBryntum(schedule)` transforms:
  - Employees → Bryntum resources (including service area, preferred/non-preferred clients, contact person relationships)
  - Visits → Bryntum events (including visit type, preferred/allowed time windows, preferred/non-preferred staff, continuity, allocated hours, unused allocation hours (client-side), SLA)
  - Assignments → Bryntum assignments
  - Employee shifts/breaks → Bryntum calendars
  - Visit status → Bryntum event styling (mandatory/optional, movable, cancelled/absent/extra/regular)
  - Time windows → Bryntum constraints (preferred vs allowed windows)

**Key Fields Mapped:**

- Employee fields: id, name, role, contractType, transportMode, skills, shifts, breaks, serviceArea, preferredClients, nonPreferredClients, contactPersonClients
- Visit fields: id, name, clientName, plannedStartTime, plannedEndTime, duration, visitStatus, priority, pinned, recurrenceType, requiredStaff, skills, time windows (minStartTime, maxStartTime, maxEndTime, preferredTimeWindows [jsonb array for Timefold waiting time reduction], allowedWindowStart, allowedWindowEnd), visitType (mandatory/optional, movable, cancelled/absent/extra/regular), preferredStaff, nonPreferredStaff, continuity, allocatedHours, unusedHours (client's unused allocation), SLA
- Assignment fields: visitId, employeeId, startTime, endTime, travelTime, waitingTime
- Calendar fields: working hours intervals, break periods

### 2. Save Schedule Changes

**Flow:**

1. User makes changes in Bryntum (drag visit, edit time, assign/unassign)
2. Bryntum emits change events (eventStore changes, assignmentStore changes)
3. Frontend collects changes and transforms via mapper function
4. Mapper converts Bryntum changes to GraphQL mutation input format
5. Frontend calls GraphQL mutation `updateSchedule(input)`
6. Backend validates and saves changes to database
7. Backend creates new schedule revision (if needed)
8. **Backend recalculates and stores metrics** (schedule-level, employee-level, client-level, service area-level)
9. **Backend calculates financial metrics** (costs based on employee contract types, revenues based on service area/municipality payment models - revenue models can vary between service areas and municipalities)
10. Backend returns updated schedule with metrics
11. Frontend updates Bryntum with new data and refreshes metrics panel
12. Frontend updates metrics display in UI (respecting RBAC for financial data)

**Data Transformation:**

- **Frontend → Backend:** Bryntum changes → GraphQL mutation input
- **Mapper Function:** `mapBryntumChangesToUpdate(changes, scheduleId)` transforms:
  - Event changes → Visit updates (time, duration, pinned status)
  - Assignment changes → Assignment creates/updates/deletes
  - Resource changes → Employee updates (if any)

**Change Types Handled:**

- Visit time changes (plannedStartTime, plannedEndTime)
- Visit assignment changes (assign to employee, unassign)
- Visit pin/unpin status
- Visit duration changes
- Visit deletion

### 3. Run Optimization

**Flow:**

1. User selects optimization scenario and clicks "Optimize"
2. Frontend calls GraphQL mutation `runOptimization(scheduleId, scenarioId)`
3. Backend validates schedule and scenario
4. Backend prepares optimization problem (TimefoldSolverRequest format)
5. Backend submits problem to Timefold API (external service)
6. Backend stores optimization job record with status "running"
7. Backend returns job ID and initial status
8. Frontend subscribes to `optimizationProgress(jobId)` subscription
9. Backend polls Timefold API for progress (or receives webhook)
10. Backend publishes progress updates via WebSocket subscription
11. Frontend receives real-time progress updates
12. When complete, backend receives Timefold solution via webhook
13. **When optimization completes:** Backend receives final solution from Timefold via webhook
14. **Backend stores solution in database** (solution_assignments, solution_events, etc.) - **Only after completion, not during optimization**
15. **Backend calculates and stores comprehensive metrics** (schedule, employee, client, service area, organization levels) - **Only after completion**
16. **Backend calculates financial metrics** (costs, revenues, profit) based on contract types and payment models - **Only after completion**
17. Backend publishes final solution via subscription (including full data with names, details, and metrics)
18. Frontend receives complete solution and updates Bryntum calendar with full information
19. Frontend fetches and displays metrics from database (respecting RBAC for financial data)

**Timefold Integration:**

- **Submission:** Backend sends TimefoldSolverRequest JSON to Timefold `/runs` endpoint
- **Polling:** Backend polls Timefold `/runs/{runId}` endpoint for status (or uses webhook)
- **Webhook:** Timefold calls `POST /api/webhooks/timefold` when optimization completes
- **Solution:** Backend receives Timefold solution JSON and normalizes into database tables

**Optimization States:**

- `solving_scheduled` - Job queued
- `solving_active` - Optimization running
- `solving_completed` - Optimization finished successfully
- `solving_failed` - Optimization failed
- `solving_terminated` - Optimization cancelled

### 4. Real-time Updates

**WebSocket Subscriptions:**

- Frontend establishes WebSocket connection to GraphQL endpoint
- Frontend subscribes to `optimizationProgress(jobId)` with job ID
- Backend publishes updates when:
  - Optimization progress changes (percentage, status, ETA)
  - Raw solution data arrives from Timefold solver (during optimization)
  - Optimization completes or fails

**During Optimization (Real-time Updates):**

- **Data Available:** Raw solver data from Timefold (visit IDs, employee IDs, start/end times, assignments)
- **Data NOT Available:** Employee names, client names, full visit details, metrics (requires DB lookups - too expensive for frequent polling)
- **Frontend Action:** Map raw solver data directly to Bryntum format using IDs only
- **Display:** Show progress bar, update calendar with raw assignment data (IDs only, no names/details)
- **Performance:** No database lookups during optimization to avoid performance issues (jobs can run 20+ minutes, polling every 2 seconds)

**After Optimization Completes:**

- Backend stores solution in database (normalized tables)
- Backend calculates and stores all metrics
- Backend publishes final solution with full data (names, details, metrics)
- Frontend receives complete data and updates Bryntum with full information
- Frontend can now display employee names, client names, and all metrics

**Polling Fallback:**

- If WebSocket unavailable, frontend can poll `getOptimizationJob(jobId)` query
- Polling interval: 2-5 seconds during active optimization
- Stop polling when status is `completed`, `failed`, or `terminated`
- During polling, only raw solver data is returned (no DB lookups)

### 5. Fine-tune Optimization

**Flow:**

1. User makes manual edits to optimized schedule
2. Frontend saves changes via `updateSchedule` mutation
3. User clicks "Fine-tune" optimization
4. Frontend calls GraphQL mutation `fineTuneOptimization(scheduleId, scenarioId)`
5. Backend computes patch operations (delta between current and previous solution)
6. Backend sends patch to Timefold `/runs/{runId}/patch` endpoint
7. Backend stores new optimization job
8. Process continues as in "Run Optimization" flow

**Patch Operations:**

- Backend computes differences between current schedule and previous solution
- Creates patch JSON with: added visits, removed visits, modified visits, changed assignments
- Sends patch to Timefold (more efficient than full re-optimization)

### 6. Pre-Planning Data Flow

**Flow:**

1. Frontend calls GraphQL query `prePlanningData(timeHorizon)` with planning horizon (1 week, 1 month, 3 months, custom)
2. Backend fetches all schedules, visits, employees across time horizon from database
3. Backend returns consolidated data (multiple schedules, pinned + unpinned visits, all employees)
4. Frontend transforms data via `prePlanningDataToBryntum` mapper
5. Bryntum displays multi-week/month consolidated view
6. User creates new movable visit via `createMovableVisit` mutation
7. Backend creates `visit_templates` record and generates concrete `visits` (unpinned, unassigned)
8. Frontend displays new visits in "Unassigned Visits" panel
9. User runs pre-planning optimization via `runPrePlanningOptimization` mutation
10. Backend triggers two-stage optimization (Pattern Discovery, Employee Assignment)
11. Backend publishes progress via `prePlanningProgress` subscription
12. When complete, backend stores patterns and assignments in database
13. Frontend displays optimized schedule with diff view
14. User accepts solution via `acceptPrePlanningSolution` mutation
15. Backend pins approved visits (`pinned = true`) and updates slingor

**Pre-Planning GraphQL Operations:**

**Queries:**

- `prePlanningData(timeHorizon)` - Get all schedules, visits, employees for planning horizon
- `supplyDemandBalance(timeHorizon)` - Get supply/demand metrics
- `demandCurve(timeHorizon)` - Get demand trend data
- `unusedHours(timeHorizon)` - Get unused hours analysis
- `getOptimalPlacementRecommendations(visitInput)` - Get AI recommendations

**Mutations:**

- `createMovableVisit(input)` - Create new recurring visit
- `updateMovableVisit(id, input)` - Update existing movable visit
- `runPrePlanningOptimization(input)` - Trigger optimization
- `acceptPrePlanningSolution(input)` - Pin approved visits

**Subscriptions:**

- `prePlanningProgress(jobId)` - Real-time optimization progress

---

## Metrics Calculation & Display

**Requirement:** All schedule changes (manual edits or optimization) must trigger metrics recalculation and storage in the backend (normalized database tables), then frontend fetches and displays the updated metrics.

**Important:** Metrics are **calculated and stored in the backend**, not in the frontend. Frontend only fetches and displays pre-calculated metrics from the database.

### Metrics Calculation (Backend)

**When Metrics Are Calculated and Stored:**

- After manual schedule changes (save operation) - Backend calculates and stores immediately
- After optimization completes - Backend calculates and stores after solution is saved to database
- After fine-tune optimization - Backend calculates and stores after solution is saved
- On schedule load - Metrics are fetched from database (already calculated)

**During Optimization:**

- Metrics are **NOT calculated or stored** during optimization (only raw solver data is available)
- Metrics become available **only after optimization completes** and solution is stored in database
- This avoids expensive database lookups during long-running optimizations (20+ minutes, polling every 2 seconds)

### Metrics Levels (Resource Hierarchy)

1. **Schedule-Level Metrics:**
   - Total service hours
   - Total travel time
   - Total waiting time
   - Utilization percentage
   - Unassigned visits count
   - Total cost (sum of employee costs)
   - Total revenue (sum of visit revenues)
   - Profit (revenue - cost)
   - Profitability ratio (profit / revenue)

2. **Employee-Level Metrics:**
   - Service hours per employee
   - Travel time per employee
   - Waiting time per employee
   - Utilization percentage per employee
   - (Note: Unused hours are client-side, not employee-side)
   - Cost per employee (based on contract type)
   - Revenue per employee (based on assigned visits)
   - Profit per employee

3. **Client-Level Metrics:**
   - Service hours per client
   - Travel time per client
   - Waiting time per client
   - Utilization percentage per client
   - Revenue per client (based on service area/municipality payment model)
   - Cost per client (sum of employee costs for client visits)
   - Profit per client (revenue - cost)
   - Profitability ratio (profit / revenue)
   - Travel/wait ratio ((travel + wait) / service hours)

4. **Service Area-Level Metrics:**
   - Aggregated metrics across all employees and clients in service area
   - Total supply hours
   - Total demand hours
   - Balance (supply - demand)
   - Utilization percentage
   - Total cost
   - Total revenue
   - Profit
   - Profitability ratio

5. **Organization-Level Metrics:**
   - Aggregated metrics across all service areas
   - Total supply hours
   - Total demand hours
   - Balance
   - Utilization percentage
   - Total cost
   - Total revenue
   - Profit
   - Profitability ratio

### Financial Metrics Calculation

**Cost Calculation:**

- **Fixed Contract Employees:** Cost = fixed monthly salary / working days in month
- **Hourly Contract Employees:** Cost based on payment models (A, B, C, D) and break payment policies (PAID/UNPAID)
  - **Model A:** Paid for all hours (service + travel + wait + breaks)
  - **Model B:** Paid for service hours only
  - **Model C:** Paid for service + travel, not wait or breaks
  - **Model D:** Custom payment rules
  - **Break Payment:** PAID breaks count toward cost, UNPAID breaks don't
- Configuration via `operational_settings` table

**Revenue Calculation:**

- Revenue model can vary between service areas and municipalities (different payment models per service area/municipality)
- Each service area/municipality may have different revenue rates and models
- Revenue = sum of visit revenues based on service area/municipality payment model
- Configuration via `service_area_payment_models` table

**Profit Calculation:**

- Profit = Revenue - Cost
- Profitability ratio = Profit / Revenue (if revenue > 0)

### Client Profitability Analysis

**Client-Level Metrics:**

- Utilization: Service hours / allocated hours
- Revenue: Based on service area/municipality payment model
- Cost: Sum of employee costs for client visits
- Profit: Revenue - Cost
- Profitability ratio: Profit / Revenue (if revenue > 0)
- Travel/wait ratio: (Travel time + Wait time) / Service hours

**Visual Indicators:**

- **Unprofitable clients:** Cost > Revenue (red indicator)
- **High travel/wait ratio:** (Travel + Wait) significantly exceeds service duration (yellow/orange indicator)
- **Profitable clients:** Revenue > Cost and reasonable travel/wait ratio (green indicator)

**RBAC (Role-Based Access Control):**

- Financial metrics (cost, revenue, profit) only visible to authorized roles
- Frontend filters metrics based on user role before display
- Backend returns all metrics, frontend applies RBAC filtering

### Metrics Display (Frontend)

**Metrics Panel:**

- Schedule-level metrics displayed in main panel
- Toggle to show/hide financial metrics (based on RBAC)
- Color-coded indicators (green/yellow/red) for health metrics

**Tooltips:**

- Individual metrics displayed in tooltips on resources (employees) and events (visits)
- Employee tooltip: Service hours, travel time, waiting time, utilization, cost (if authorized)
- Client tooltip: Service hours, allocated hours, unused allocation hours (monthly allocation - actual service hours delivered), revenue, cost (if authorized), profit (if authorized), profitability ratio, travel/wait ratio

**Visual Indicators:**

- Toggleable indicators on resource rows and events
- Badges showing unused allocation hours (client-side), profitability warnings
- Color-coded indicators for health metrics

**Metrics Modal:**

- Full-screen modal displaying all clients and employees
- Complete metrics tables with all available metrics
- Filtering and sorting capabilities
- Export functionality

**Service Area Metrics:**

- Service area-level metrics displayed in service area panel
- Aggregated metrics across all employees and clients in service area

---

## Mapper Functions Required

**Purpose:** Transform data between backend format (normalized GraphQL) and Bryntum format

**Required Mappers:**

1. **`mapScheduleToBryntum(schedule)`**
   - Input: GraphQL Schedule object (with employees, visits, assignments, metrics)
   - Output: Bryntum data structure (resources, events, assignments, calendars)
   - Handles: Employee → Resource mapping, Visit → Event mapping, Assignment mapping, Calendar mapping

2. **`mapEmployeeToResource(employee)`**
   - Input: GraphQL Employee object
   - Output: Bryntum Resource object
   - Maps: Employee fields to Bryntum resource fields, skills, transport mode, contract type, service area, preferred clients list, non-preferred clients list, contact person-client relationships

3. **`mapVisitToEvent(visit)`**
   - Input: GraphQL Visit object
   - Output: Bryntum Event object
   - Maps: Visit fields to Bryntum event fields, status to styling, time windows to constraints (hard: minStartTime/maxStartTime/maxEndTime, soft: preferredTimeWindows [jsonb array for Timefold waiting time reduction], allowed: allowedWindowStart/allowedWindowEnd), visit type (mandatory/optional, movable, cancelled/absent/extra/regular), preferred staff list, non-preferred staff list, continuity requirements, allocated hours, unused allocation hours (client-side: monthly allocation - actual service hours delivered), SLA requirements

4. **`mapEmployeeToCalendar(employee)`**
   - Input: GraphQL Employee object (with shifts and breaks)
   - Output: Bryntum Calendar object
   - Maps: Shifts to working intervals, breaks to non-working periods

5. **`mapBryntumChangesToUpdate(changes, scheduleId)`**
   - Input: Bryntum change object (from eventStore/assignmentStore changes)
   - Output: GraphQL UpdateScheduleInput
   - Maps: Event changes to visit updates, assignment changes to assignment updates

6. **`mapSolutionToBryntum(solution)`**
   - Input: GraphQL Solution object (from optimization) - **Can be raw solver data (during optimization) or complete solution (after completion)**
   - Output: Bryntum data structure
   - Maps: Solution assignments to Bryntum assignments, updates event times
   - **During optimization:** Maps raw solver data (IDs only, no names/details) - minimal data for real-time preview
   - **After completion:** Maps complete solution with full data (names, details, metrics) from database

7. **`mapRawSolverDataToBryntum(rawSolverData)`**
   - Input: Raw Timefold solver data (visit IDs, employee IDs, start/end times, assignments) - **No database lookups**
   - Output: Bryntum data structure (IDs only, no names/details)
   - Maps: Raw solver assignments to Bryntum format for real-time preview during optimization
   - **Performance:** No database lookups, no name resolution, no metrics - just raw assignment data
   - Used during optimization for real-time calendar updates (20+ minute jobs, polling every 2 seconds)

8. **`mapMetricsToDisplay(metrics, userRole)`**
   - Input: GraphQL Metrics object (schedule/employee/client/service area), user role/permissions
   - Output: UI-ready metrics object
   - Maps: Metrics to display format, filters financial data based on RBAC (cost, revenue, profit only visible to authorized roles)
   - Handles: Multiple metric levels (schedule, employee, client, service area, organization)
   - **Client metrics:** Maps client-level metrics including utilization, revenue, cost, profit, profitability ratio, travel/wait ratio
   - **Profitability analysis:** Calculates and flags unprofitable clients (cost > revenue) and high travel/wait ratio clients (travel+wait time significantly exceeds service time)
   - **Visual indicators:** Generates profitability warnings and visual indicators for display in UI

9. **`prePlanningDataToBryntum(prePlanningData)`**
   - Input: GraphQL PrePlanningData object (multiple schedules across time horizon)
   - Output: Bryntum data structure (multi-week/month view)
   - Maps: Consolidated schedules to Bryntum format, pinned vs unpinned visits, unassigned visits to panel

10. **`mapRawSolverDataToBryntum(rawSolverData)`** (Pre-planning variant)
    - Input: Raw Timefold pre-planning solution data
    - Output: Bryntum data structure (minimal, for real-time updates)
    - Maps: Raw solver data to Bryntum format during pre-planning optimization

**Mapper Considerations:**

- Handle null/undefined values gracefully
- Transform time formats (ISO strings ↔ Date objects)
- Transform duration units (minutes ↔ hours)
- Map status enums to Bryntum format (mandatory/optional, movable, cancelled/absent/extra/regular)
- Handle unassigned visits (no assignment)
- Handle missing data (optional fields)
- Map employee preferences (preferred/non-preferred clients, contact person relationships)
- Map visit preferences (preferred/non-preferred staff, continuity requirements)
- Map time windows (hard constraints: minStartTime/maxStartTime/maxEndTime, soft constraints: preferredTimeWindows [jsonb array for Timefold waiting time reduction], allowed: allowedWindowStart/allowedWindowEnd for constraint visualization)
- Map service area relationships for filtering and grouping
- Map allocated hours and unused allocation hours (client-side) for metrics display
- Map SLA requirements for validation and display
- Map metrics at all levels (schedule, employee, client, service area, organization) - **Only available after schedule is saved to database**
- Apply RBAC filtering for financial metrics (cost, revenue, profit) based on user role
- Map financial calculations (costs based on contract types, revenues based on payment models) - **Backend calculates, frontend just displays**
- Map client profitability metrics (utilization, revenue, cost, profit, profitability ratio, travel/wait ratio) - **Backend calculates, frontend displays with visual indicators**
- Calculate and flag profitability warnings (unprofitable clients, high travel/wait ratio) - **Frontend calculates ratios and generates warnings from backend metrics**
- Handle raw solver data during optimization (IDs only, no names/details, no metrics) - **Performance optimization for long-running jobs**
- Distinguish between raw solver data (during optimization) and complete solution data (after completion with database lookups)

**Note:** Detailed mapper specifications for all external systems (Carefox, eCare, Phoniro, CSV, JSON, PDF) and internal data flows are documented in `MAPPER_SPECIFICATIONS_V2.md`.

---

## Error Handling

**GraphQL Errors:**

- Network errors: Retry with exponential backoff
- Validation errors: Display user-friendly messages
- Authentication errors: Redirect to login
- Authorization errors: Show permission denied message

**Optimization Errors:**

- Job failed: Display error message, allow retry
- Timeout: Show timeout message, allow retry with different scenario
- Invalid input: Show validation errors

**Data Transformation Errors:**

- Missing required fields: Log error, show fallback UI
- Invalid data format: Log error, show error message
- Type mismatches: Log error, handle gracefully

---

## Performance Considerations

**Query Optimization:**

- Request only fields needed for Bryntum (avoid over-fetching)
- Use GraphQL fragments for reusable field sets
- Implement pagination for large schedules
- Cache query results in Apollo Client

**Data Transformation:**

- Memoize mapper functions to avoid re-computation
- Batch multiple changes before sending to backend
- Debounce rapid changes (e.g., drag operations)

**Real-time Updates:**

- Throttle subscription updates to avoid UI flicker
- Batch multiple updates into single UI refresh
- Handle connection drops gracefully (reconnect, show status)

**Metrics Calculation:**

- Backend calculates metrics asynchronously after schedule changes
- Frontend polls for updated metrics if needed
- Cache metrics in frontend to avoid repeated queries

---

## Authentication & Authorization

**Authentication:**

- Clerk JWT tokens (details to be shared during project)
- Token refresh via REST endpoint
- Session management via Clerk

**Authorization (RBAC):**

- Financial metrics (cost, revenue, profit) only visible to authorized roles
- Backend returns all metrics, frontend applies RBAC filtering
- Role-based access to schedule operations (view, edit, optimize)

---

## Related Documentation

- **`MAPPER_SPECIFICATIONS_V2.md`** - Complete mapper specifications for Caire 2.0 (all external systems, internal data flows, pre-planning)
- **`API_DESIGN_V2.md`** - Detailed GraphQL schema and operation specifications
- **`data-model-v2.md`** - Complete database schema documentation
- **`PREPLANNING_BACKEND_ANALYSIS.md`** - Pre-planning backend architecture analysis

---

**Document Status:** Ready for Implementation  
**Last Updated:** 2025-12-09  
**Version:** 2.0
