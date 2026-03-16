# Caire Frontend Integration (Bryntum SchedulerPro)

> **Archive notice:** This document is superseded by the codebase and [bryntum_timeplan.md](../05-prd/bryntum_consultant_specs/bryntum_timeplan.md). For what and why (product scope), use [SOLUTION_UI_PRD.md](SOLUTION_UI_PRD.md). For implementation categories and Bryntum examples, use the timeplan.

**Version:** 2.0

---

## Overview

Caire frontend uses **Bryntum SchedulerPro v7** for the scheduling calendar UI, integrated with **GraphQL API** for data fetching and **WebSocket subscriptions** for real-time updates.

**Key Features:**

- Professional calendar UI with drag-and-drop
- Real-time optimization progress
- Diff view (baseline vs optimized)
- Bench panel (unassigned visits)
- Multi-dimensional optimization visualization

---

## Technology Stack

### Frontend

- **React 18** + **TypeScript**
- **Bryntum SchedulerPro v7** - Calendar UI
- **Apollo Client** - GraphQL queries/mutations/subscriptions
- **Vite** - Build tool
- **Tailwind CSS** - Styling

### Backend Integration

- **GraphQL API** - Primary data interface
- **WebSocket** - Real-time subscriptions
- **REST** - File operations, webhooks

---

## Data Flow

### 1. Load Schedule Data

```
GraphQL Query → Backend (Prisma) → Database → GraphQL Response → Mapper → Bryntum Format → Display
```

**Example Query:**

```graphql
query GetScheduleForCalendar($id: ID!) {
  schedule(id: $id) {
    id
    name
    date
    employees {
      id
      name
      shifts { ... }
    }
    visits {
      id
      name
      timeWindows
      pinned
      assignedEmployee { ... }
    }
    metrics {
      efficiency
      travelTime
      serviceHours
    }
  }
}
```

**Mapper Function:**

```typescript
function mapScheduleToBryntum(schedule: Schedule): BryntumData {
  return {
    resources: schedule.employees.map(mapEmployeeToResource),
    events: schedule.visits.map(mapVisitToEvent),
    assignments: schedule.assignments.map(mapAssignment),
    calendars: schedule.employees.map(mapShiftsToCalendar),
  };
}
```

### 2. Save Changes

```
Bryntum Changes → Mapper → GraphQL Mutation → Backend → Database → Metrics Recalculation → GraphQL Response → Update UI
```

**Example Mutation:**

```graphql
mutation UpdateSchedule($input: UpdateScheduleInput!) {
  updateSchedule(input: $input) {
    id
    status
    metrics {
      efficiency
      travelTime
    }
  }
}
```

### 3. Real-Time Optimization

```
Start Optimization → GraphQL Mutation → Backend → Timefold API → WebSocket Subscription → Real-Time Updates → UI Progress
```

**Example Subscription:**

```graphql
subscription OptimizationProgress($jobId: ID!) {
  optimizationProgress(jobId: $jobId) {
    status
    progress
    currentScore
    metrics {
      efficiency
      travelTime
    }
  }
}
```

---

## Bryntum Component Structure

### Main Calendar View

**Component**: `SchedulerView.tsx`

**Features**:

- Timeline with employees as resources
- Visits as events (drag-and-drop)
- Time axis navigation (day/week/month)
- Zoom controls
- Visit editing (time, duration)

**Configuration**:

```typescript
const schedulerConfig = {
  resources: employees, // From GraphQL
  events: visits, // From GraphQL
  assignments: assignments, // From GraphQL
  viewPreset: "weekAndMonth",
  startDate: schedule.startDate,
  endDate: schedule.endDate,
  // ... other config
};
```

### Legend and Filtering

**Component**: `LegendAndFiltering.tsx`

**Features**:

- Color-coded visit types
- Pinned/unpinned indicators
- Priority indicators
- Filter by service area, employee, visit type

### Resource Histogram

**Component**: `ResourceHistogram.tsx`

**Features**:

- Employee utilization chart
- Service hours vs shift hours
- Workload balance visualization

### Comparison View

**Component**: `ComparisonView.tsx`

**Features**:

- Side-by-side baseline vs optimized
- Diff highlighting
- Metrics comparison
- Accept/reject changes

### Bench Panel

**Component**: `BenchPanel.tsx`

**Features**:

- Unassigned visits list
- Movable visits list
- Drag-and-drop to employee rows
- Filter and search

---

## Data Transformation

### GraphQL → Bryntum

**Employees → Resources:**

```typescript
function mapEmployeeToResource(employee: Employee): BryntumResource {
  return {
    id: employee.id,
    name: employee.name,
    role: employee.role,
    contractType: employee.contractType,
    transportMode: employee.transportMode,
    skills: employee.skills,
    // Metadata columns
    serviceArea: employee.serviceArea?.name,
    preferredClients: employee.preferredClients?.map((c) => c.name),
  };
}
```

**Visits → Events:**

```typescript
function mapVisitToEvent(visit: Visit): BryntumEvent {
  return {
    id: visit.id,
    name: visit.name,
    startDate: visit.assignedStartTime || visit.minStartTime,
    endDate: visit.assignedEndTime || visit.maxEndTime,
    duration: visit.serviceDuration,
    // Styling
    eventColor: visit.pinned ? "blue" : "orange",
    eventStyle: visit.pinned ? "solid" : "dashed",
    iconCls: visit.pinned ? "fa-solid fa-lock" : undefined,
    // Constraints
    timeWindows: visit.timeWindows,
    preferredTimeWindows: visit.preferredTimeWindows,
  };
}
```

### Bryntum → GraphQL

**Changes → Mutations:**

```typescript
function mapBryntumChangesToUpdate(
  changes: BryntumChanges,
  scheduleId: string,
): UpdateScheduleInput {
  return {
    scheduleId,
    visitUpdates: changes.events.map((event) => ({
      visitId: event.id,
      plannedStartTime: event.startDate,
      plannedEndTime: event.endDate,
      pinned: event.pinned,
    })),
    assignmentUpdates: changes.assignments.map((assignment) => ({
      visitId: assignment.eventId,
      employeeId: assignment.resourceId,
    })),
  };
}
```

---

## Real-Time Features

### Optimization Progress

**Subscription Setup:**

```typescript
const { data, loading } = useSubscription(OPTIMIZATION_PROGRESS, {
  variables: { jobId: optimizationJobId },
});

useEffect(() => {
  if (data?.optimizationProgress) {
    updateProgressBar(data.optimizationProgress.progress);
    updateMetrics(data.optimizationProgress.metrics);
  }
}, [data]);
```

**UI Updates:**

- Progress bar
- Current score
- Metrics (efficiency, travel time)
- Estimated time remaining

### Schedule Updates

**Subscription:**

```typescript
useSubscription(SCHEDULE_UPDATES, {
  variables: { scheduleId },
  onData: ({ data }) => {
    if (data?.scheduleUpdates.type === "UPDATED") {
      refetchSchedule(); // Or update specific parts
    }
  },
});
```

---

## Planning Window Integration

### Multi-Week/Month View

**For Pre-Planning:**

```typescript
// Query with longer planning window
const { data } = useQuery(GET_PRE_PLANNING_DATA, {
  variables: {
    timeHorizon: "1_month", // or '1_week', '3_months', 'custom'
    startDate: planningWindowStart,
    endDate: planningWindowEnd,
  },
});

// Bryntum displays multi-week/month view
const schedulerConfig = {
  viewPreset: "weekAndMonth", // Multi-week view
  startDate: planningWindowStart,
  endDate: planningWindowEnd,
};
```

**Filtering Results:**

```typescript
// After optimization, filter to show only target date
function filterResultsForTargetDate(
  bryntumData: BryntumData,
  targetDate: string,
): BryntumData {
  return {
    ...bryntumData,
    events: bryntumData.events.filter((event) =>
      isSameDay(event.startDate, targetDate),
    ),
  };
}
```

---

## User Workflows

### Daily Schedule Optimization

1. **Load Schedule**: GraphQL query → Display in Bryntum
2. **Manual Edits**: Drag-and-drop visits → GraphQL mutation
3. **Optimize**: Click "Optimize" → GraphQL mutation → WebSocket subscription
4. **Review**: Diff view shows changes
5. **Accept/Reject**: GraphQL mutation to accept solution

### Pre-Planning with Movable Visits

1. **Load Pre-Planning Data**: GraphQL query with longer time horizon
2. **Create Movable Visit**: Form → GraphQL mutation
3. **Run Optimization**: GraphQL mutation → WebSocket subscription
4. **Review Recommendations**: Diff view
5. **Accept and Pin**: GraphQL mutation → Visits become pinned

### Real-Time Disruptions

1. **Receive Update**: WebSocket subscription → Notification
2. **Auto-Optimize**: GraphQL mutation → WebSocket subscription
3. **Review Changes**: Diff view
4. **Auto-Approve** (optional): GraphQL mutation

---

## Visual System

### Visit Styling

| Visit Type        | Color  | Border        | Icon    |
| ----------------- | ------ | ------------- | ------- |
| **Pinned**        | Blue   | Solid         | 🔒 Lock |
| **Unpinned**      | Orange | Dashed        | -       |
| **Movable**       | Purple | Dotted        | -       |
| **Cancelled**     | Gray   | Strikethrough | ❌      |
| **High Priority** | Red    | Thick         | ⚠️      |

### Employee Rows

- **Metadata columns**: Name, role, contract type, transport mode
- **Utilization bar**: Service hours / shift hours
- **Status indicators**: Active, on break, overtime

---

## Performance Optimization

### Data Loading

- **Pagination**: Load visits in batches
- **Lazy loading**: Load employee details on expand
- **Caching**: Apollo Client cache for repeated queries

### Bryntum Performance

- **Virtual scrolling**: For 100+ employees
- **Event virtualization**: For 1000+ visits
- **Debounced updates**: Batch changes before saving

---

## Error Handling

### GraphQL Errors

```typescript
const { data, error, loading } = useQuery(GET_SCHEDULE, {
  variables: { id },
  onError: (error) => {
    if (error.graphQLErrors) {
      // Handle GraphQL errors
    }
    if (error.networkError) {
      // Handle network errors
    }
  },
});
```

### Optimization Errors

- **Timeout**: Show retry option
- **Invalid Input**: Display validation errors
- **Timefold Error**: Show error message, allow manual fix

---

## References

- [Bryntum Integration Guide](../../08-frontend/BRYNTUM_INTEGRATION.md)
- [Bryntum From Scratch PRD](../../05-prd/bryntum_consultant_specs/BRYNTUM_FROM_SCRATCH_PRD.md)
- [Backend Architecture](./BACKEND_ARCHITECTURE.md)
- [Planning Window Strategy](./PLANNING_WINDOW_STRATEGY.md)
