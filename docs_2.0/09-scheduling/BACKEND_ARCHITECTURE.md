# Caire Backend Architecture

**Version:** 2.0  
**Last Updated:** 2025-12-11

---

## Overview

Caire backend uses **GraphQL** (primary) + **REST** (secondary) with a **normalized database architecture**. All scheduling data is stored in relational tables - no JSON storage.

**Key Principles:**

- **GraphQL API** (Express + Apollo Server) - primary interface
- **Prisma ORM** - type-safe database access
- **WebSocket subscriptions** - real-time optimization progress
- **Normalized storage** - all data in relational tables
- **Planning windows** - calculated dynamically, not stored

---

## Technology Stack

### Backend Server

- **Express.js** - Standalone server (not Next.js API routes)
- **Apollo Server** - GraphQL server
- **Prisma** - Type-safe ORM (replacing Drizzle)
- **PostgreSQL** - Database
- **WebSocket** - Real-time subscriptions

### External Services

- **Timefold API** - Optimization engine
- **Clerk** - Authentication
- **S3/Storage** - File storage (CSV, PDF)

---

## API Architecture

### GraphQL (Primary) - ~50-60 Operations

**Queries (~30 operations):**

- Schedule queries (get, list, details)
- Employee queries (get, list by service area)
- Client queries (get, list by service area)
- Visit queries (get, list, by schedule)
- Slinga queries (get, list, by employee)
- Movable visit queries (get, list, by group)
- Optimization job queries (get, list, status)

**Mutations (~20 operations):**

- Schedule mutations (create, update, delete, clone)
- Visit mutations (create, update, pin/unpin, assign)
- Optimization mutations (start, stop, accept solution)
- Slinga mutations (create, update, expand)
- Movable visit mutations (create, update, freeze)

**Subscriptions (~5 operations):**

- Optimization progress (real-time updates)
- Schedule updates (real-time changes)
- Job status (real-time status)

### REST (Secondary) - ~10-15 Endpoints

- **Webhooks**: Timefold completion callbacks
- **File operations**: CSV/PDF uploads
- **Health checks**: System status

---

## Data Flow Architecture

### Complete Scheduling Flow

```
1. EXTERNAL DATA IMPORT (CSV, JSON, API)
   ↓
2. MAPPERS (External → Normalized Database)
   ↓
3. NORMALIZED DATABASE STORAGE (Prisma + PostgreSQL)
   ↓
4. TF INPUT GENERATION (On-the-fly from database)
   ↓
5. TIMEFOLD API (Optimization)
   ↓
6. WEBHOOK (Completion)
   ↓
7. SOLUTION PROCESSING (TF OUTPUT → Normalized Database)
   ↓
8. NORMALIZED DATABASE STORAGE (solutions, solution_assignments)
   ↓
9. GRAPHQL QUERY (Get Solution)
```

### Key Services

| Service                    | Purpose                            | Input                       | Output                             |
| -------------------------- | ---------------------------------- | --------------------------- | ---------------------------------- |
| **ImportService**          | External data import               | Carefox/eCare API, CSV, PDF | Normalized database records        |
| **External Mappers**       | Transform external → Normalized DB | External JSON/CSV           | Prisma inserts (normalized tables) |
| **TimefoldInputGenerator** | Generate TF INPUT from DB          | Database queries            | TF INPUT JSON (temporary)          |
| **TimefoldClient**         | Optimization API                   | TF INPUT JSON (temp)        | TF OUTPUT JSON (temp)              |
| **SolutionMapper**         | Process OUTPUT → Normalized DB     | TF OUTPUT JSON (temp)       | Prisma inserts (normalized tables) |
| **GraphQL Resolvers**      | API layer                          | GraphQL queries/mutations   | Database queries                   |

---

## Database Schema

### Core Tables

**Schedules**

- `id`, `organizationId`, `date`, `startDate`, `endDate`
- `scheduleTimespan` (daily/weekly/monthly/consolidated)
- `status`, `scheduleType`, `source`
- `efficiency` (calculated: service hours / shift hours)

**Visits**

- `id`, `scheduleId`, `clientId`, `organizationId`
- `minStartTime`, `maxStartTime`, `maxEndTime` (time windows)
- `pinned`, `pinningRequested`
- `assignedEmployeeId`, `assignedStartTime`, `assignedEndTime`
- `isMovable`, `movableGroupId`
- `slingaId` (nullable - links to recurring pattern)

**Employees**

- `id`, `organizationId`, `name`, `skills`
- Shifts, breaks, availability

**Slinga**

- `id`, `organizationId`, `employeeId`, `weekday`
- Recurring weekly patterns

**SlingaVisits**

- `id`, `slingaId`, `clientId`
- `sequenceIndex`, `pinned`
- Pattern definition

**MovableVisits**

- `id`, `organizationId`, `clientId`
- `movableStartTime`, `movableEndTime`
- `frequency` (daily/weekly/monthly)
- `lifecycleStatus` (new/frozen/pinned)

**OptimizationJobs**

- `id`, `scheduleId`, `status`
- `timefoldJobId`, `startedAt`, `completedAt`
- Metrics and results

**SolutionVisitAssignments**

- `id`, `jobId`, `visitId`, `employeeId`
- `startTime`, `endTime`, `travelTime`
- Solution data

---

## Planning Window Implementation

### Dynamic Calculation

Planning windows are **NOT stored** in the database - they are calculated dynamically:

```typescript
// Pre-planning orchestrator
const planningWindow: PlanningWindow = {
  start: parseISO(request.dateRangeStart + "T06:00:00.000Z"),
  end: parseISO(request.dateRangeEnd + "T23:00:00.000Z"), // Can be any range!
};

// Carefox mapper
const planningWindow = CarefoxMapperShared.calculatePlanningWindow(
  visits,
  employees,
  date, // Or date range
);
```

### Support for Longer Windows

✅ **Fully Supported**:

- `schedules.startDate` and `endDate` are timestamps (can span multiple days)
- Services calculate planning windows from date ranges
- Timefold accepts planning windows of any length

**Enhancement**: Update daily schedule creation to optionally use 7-day windows.

See [Backend Planning Window Support](./BACKEND_PLANNING_WINDOW_SUPPORT.md) for details.

---

## GraphQL Schema (Scheduling)

### Queries

```graphql
# Schedule queries
query GetSchedule($id: ID!) {
  schedule(id: $id) {
    id
    name
    date
    startDate
    endDate
    status
    efficiency
    visits { ... }
    employees { ... }
  }
}

query ListSchedules($organizationId: ID!, $filters: ScheduleFilters) {
  schedules(organizationId: $organizationId, filters: $filters) {
    id
    name
    date
    status
    efficiency
  }
}

# Visit queries
query GetVisits($scheduleId: ID!) {
  visits(scheduleId: $scheduleId) {
    id
    client { name }
    timeWindows
    pinned
    assignedEmployee { name }
  }
}

# Optimization queries
query GetOptimizationJob($id: ID!) {
  optimizationJob(id: $id) {
    id
    status
    progress
    metrics
  }
}
```

### Mutations

```graphql
# Schedule mutations
mutation CreateSchedule($input: CreateScheduleInput!) {
  createSchedule(input: $input) {
    id
    status
  }
}

mutation OptimizeSchedule($scheduleId: ID!, $options: OptimizationOptions) {
  optimizeSchedule(scheduleId: $scheduleId, options: $options) {
    jobId
    status
  }
}

# Visit mutations
mutation PinVisit($visitId: ID!) {
  pinVisit(visitId: $visitId) {
    id
    pinned
  }
}

mutation UnpinVisit($visitId: ID!) {
  unpinVisit(visitId: $visitId) {
    id
    pinned
  }
}
```

### Subscriptions

```graphql
# Real-time optimization progress
subscription OptimizationProgress($jobId: ID!) {
  optimizationProgress(jobId: $jobId) {
    status
    progress
    currentScore
    metrics
  }
}

# Schedule updates
subscription ScheduleUpdates($scheduleId: ID!) {
  scheduleUpdates(scheduleId: $scheduleId) {
    type  # CREATED, UPDATED, DELETED
    schedule { ... }
  }
}
```

---

## Service Layer Architecture

### Import Services

**CarefoxImportService**

- Fetches data from Carefox API
- Transforms via CarefoxMapper
- Creates Original schedule

**eCareImportService**

- Parses eCare CSV
- Transforms via eCareMapper
- Creates schedule

**PhoniroImportService**

- Parses Phoniro CSV (Carefox actuals only)
- Matches names to UUIDs
- Creates actuals schedule from CSV data

### Mapper Services

**CarefoxMapper**

- Carefox JSON → Normalized Database (Prisma inserts)
- Calculates planning windows
- Handles multi-day schedules
- No Timefold JSON storage

**eCareMapper**

- eCare CSV → Normalized Database (Prisma inserts)
- Supports all schedule states (unplanned/planned/actual)
- No Timefold JSON storage

**PhoniroMapper**

- Phoniro CSV → Normalized Database (Prisma updates)
- Updates actual execution data
- No Timefold JSON storage

### Optimization Services

**TimefoldClient**

- Sends INPUT to Timefold API
- Polls for completion
- Receives OUTPUT

**OptimizationService**

- Orchestrates optimization
- Manages job lifecycle
- Handles errors

**PrePlanningOrchestrator**

- Pre-planning optimization
- Handles movable visits
- Supports longer planning windows

### Data Services

**TimefoldInputGenerator**

- Generates TF INPUT JSON on-the-fly from normalized database
- Used only when calling Timefold API (temporary, not stored)
- Caches when possible for performance

**SolutionMapper**

- Processes TF OUTPUT JSON → Normalized Database (Prisma inserts)
- Stores assignments and metrics in solution tables
- No JSON storage - all normalized immediately

---

## Planning Window Strategy Implementation

### For Daily Optimizations

**Recommended**: Use 7-day planning window

```typescript
// Calculate planning window
const planningWindow = {
  startDate: targetDate,
  endDate: addDays(targetDate, 7).toISOString(), // 7 days
};

// Include visits from entire week
const visits = await getVisitsForDateRange(
  organizationId,
  planningWindow.startDate,
  planningWindow.endDate,
);

// Filter results to show only target date
const filteredSolution = filterResultsForTargetDate(solution, targetDate);
```

### For Cross-Area Optimization

**Include multiple service areas**:

```typescript
const visits = await getVisitsForServiceAreas(
  organizationId,
  [serviceAreaId1, serviceAreaId2], // Multiple areas
  planningWindow,
);
```

---

## WebSocket Subscriptions

### Real-Time Optimization Progress

```typescript
// GraphQL subscription
subscription OptimizationProgress($jobId: ID!) {
  optimizationProgress(jobId: $jobId) {
    status
    progress
    currentScore
    metrics {
      travelTime
      efficiency
      assignedVisits
    }
  }
}
```

**Implementation**:

- Timefold webhook triggers update
- GraphQL subscription broadcasts to clients
- Frontend updates UI in real-time

---

## Error Handling

### Optimization Errors

- **Timeout**: Retry with longer timeout
- **Invalid Input**: Validate before sending
- **Timefold Error**: Log and notify user

### Data Validation

- **Planning window**: Validate date ranges
- **Time windows**: Ensure minStartTime ≤ maxStartTime
- **Pinned visits**: Require previous solution data

---

## Performance Considerations

### Database Queries

- **Indexes**: On `scheduleId`, `organizationId`, `date`, `pinned`
- **Pagination**: For large visit lists
- **Caching**: INPUT reconstruction when possible

### Optimization

- **Longer planning windows** = more visits = longer optimization time
- **Trade-off**: Better quality vs faster optimization
- **Recommendation**: Use 7-day window for daily, monitor performance

---

## Security

### Authentication

- **Clerk** - User authentication
- **Organization scoping** - All queries filtered by `organizationId`
- **Role-based access** - Planner vs admin permissions

### Data Access

- **Soft deletes** - `deletedAt` timestamp
- **Audit fields** - `createdBy`, `updatedBy`
- **Organization isolation** - All queries scoped to organization

---

## References

- [API Design V2](../../02-api/API_DESIGN_V2.md)
- [Data Model V2](../../03-data/data-model-v2.md)
- [Planning Window Strategy](./PLANNING_WINDOW_STRATEGY.md)
- [Backend Planning Window Support](./BACKEND_PLANNING_WINDOW_SUPPORT.md)
- [Timefold Integration](./TIMEFOLD_INTEGRATION.md)
