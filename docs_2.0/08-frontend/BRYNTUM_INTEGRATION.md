# Bryntum Integration Guide

**Purpose:** Guide for integrating Bryntum SchedulerPro into the CAIRE frontend  
**Related:** `FRONTEND_REFACTORING.md`, `../05-prd/bryntum-reference.md`, `../05-prd/bryntum_consultant_specs/BRYNTUM_FROM_SCRATCH_PRD.md`  
**Timeline:** 14-19 days (112-152 hours) - See `bryntum_timeplan.md` for detailed breakdown

---

## Overview

Bryntum SchedulerPro is the calendar/scheduling UI component used for visualizing and editing schedules.

**Approach:** Building from scratch following `BRYNTUM_FROM_SCRATCH_PRD.md` specifications.

**Key Implementation Steps:**

1. Set up Bryntum SchedulerPro component structure
2. Implement mapper functions (GraphQL ↔ Bryntum format)
3. Create GraphQL hooks for data fetching and mutations
4. Build UI components following the PRD specifications
5. Connect save/optimize handlers to GraphQL mutations

**Reference Documents:**

- **Implementation Guide:** `../05-prd/bryntum_consultant_specs/BRYNTUM_FROM_SCRATCH_PRD.md`
- **Timeplan:** `../05-prd/bryntum_consultant_specs/bryntum_timeplan.md`
- **Backend Spec:** `../05-prd/bryntum_consultant_specs/BRYNTUM_BACKEND_SPEC.md`
- **Bryntum Examples:** `../05-prd/bryntum_consultant_specs/bryntum-reference.md`

---

## Component Structure

**Location:** `packages/client/src/features/scheduling/components/bryntum-calendar/`

**Components to Build:**

```
bryntum-calendar/
├── SchedulerView.tsx          # Main calendar component
├── LegendAndFiltering.tsx     # Legend and filter controls
├── ResourceHistogram.tsx       # Resource utilization chart (P2)
├── ComparisonView.tsx          # Baseline vs optimized comparison
├── OptimizationScenarioModal.tsx # Scenario selection
├── MetricsPanel.tsx           # Metrics display
├── RouteSummary.tsx           # Route summary
└── types.ts                   # Bryntum-specific types
```

**Implementation Priority:**

- **P0 (Must Have):** Core schedule viewing, visit assignment, CRUD operations, optimization, pre-planning
- **P1 (High):** Filtering, comparison, basic analytics
- **P2 (Nice to Have):** Advanced analytics, WebSocket updates, cross-service area, export

---

### Step 1: Create Mapper Functions (8-12 hours)

**Purpose:** Transform between GraphQL types and Bryntum format

**Location:** `src/features/scheduling/lib/mappers.ts`

> **Key:** The data model is normalized (Caire 2.0 architecture), so mapping is straightforward! All data comes from normalized database tables via GraphQL, not from stored JSON.

**Required Mappers (per MAPPER_SPECIFICATIONS.md):**

1. **`mapScheduleToBryntum(schedule)`** - Main schedule mapper
2. **`mapEmployeeToResource(employee)`** - Employee → Resource mapping
3. **`mapVisitToEvent(visit)`** - Visit → Event mapping (includes time windows, preferences, continuity)
4. **`mapEmployeeToCalendar(employee)`** - Shifts/breaks → Bryntum calendars
5. **`mapBryntumChangesToUpdate(changes, scheduleId)`** - User edits → GraphQL mutation input
6. **`mapSolutionToBryntum(solution)`** - Optimization solution → Bryntum format
7. **`mapRawSolverDataToBryntum(rawSolverData)`** - Real-time optimization updates (IDs only, no DB lookups)
8. **`prePlanningDataToBryntum(prePlanningData)`** - Multi-week/month pre-planning data
9. **`mapMetricsToDisplay(metrics, userRole)`** - Metrics with RBAC filtering

```typescript
import { Schedule, Employee, Visit } from "@/graphql/generated";
import { SchedulerPro } from "@bryntum/schedulerpro";

/**
 * Maps GraphQL Schedule to Bryntum SchedulerPro data format
 *
 * Key: Maps from normalized database structure (not stored JSON)
 * Includes: Employees, visits, assignments, shifts, breaks, metrics
 */
export function mapScheduleToBryntum(schedule: Schedule) {
  return {
    // Resources (employees with service area, preferences, contact person relationships)
    resources: schedule.employees.map(mapEmployeeToResource),

    // Events (visits with time windows, preferences, continuity, allocated hours)
    events: schedule.visits.map(mapVisitToEvent),

    // Assignments (employee-visit relationships from solution_assignments)
    assignments:
      schedule.solution?.assignments?.map((a) => ({
        id: `${a.visitId}-${a.employeeId}`,
        eventId: a.visitId,
        resourceId: a.employeeId,
        startTime: a.startTime,
        endTime: a.endTime,
        travelTime: a.travelTimeSeconds,
        waitingTime: a.waitingTimeSeconds,
      })) || [],

    // Calendars (employee shifts and breaks)
    calendars: schedule.employees.flatMap((emp) => mapEmployeeToCalendar(emp)),
  };
}

function mapEmployeeToResource(employee: Employee) {
  return {
    id: employee.id,
    name: employee.name,
    type: "employee",
    role: employee.role,
    contractType: employee.contractType,
    transportMode: employee.transportMode,
    serviceArea: employee.serviceArea,
    preferredClients: employee.preferredClients?.map((c) => c.id) || [],
    nonPreferredClients: employee.nonPreferredClients?.map((c) => c.id) || [],
    contactPersonClients: employee.contactPersonClients?.map((c) => c.id) || [],
    skills: employee.skills?.map((s) => s.skillName) || [],
  };
}

function mapVisitToEvent(visit: Visit) {
  return {
    id: visit.id,
    name: visit.name || visit.clientName,
    startDate: visit.plannedStartTime || visit.assignment?.startTime,
    endDate: visit.plannedEndTime || visit.assignment?.endTime,
    duration: visit.duration, // minutes
    clientName: visit.client?.name,
    clientPhone: visit.client?.phone,
    requiredSkills: visit.requiredSkills?.map((s) => s.skillName) || [],
    // Time windows (hard constraints)
    minStartTime: visit.minStartTime,
    maxStartTime: visit.maxStartTime,
    maxEndTime: visit.maxEndTime,
    // Preferred time windows (soft constraints for Timefold waiting time reduction)
    preferredTimeWindows: visit.preferredTimeWindows || [], // jsonb array
    // Allowed window (for constraint visualization)
    allowedWindowStart: visit.allowedWindowStart,
    allowedWindowEnd: visit.allowedWindowEnd,
    // Visit status and type
    pinned: visit.pinned, // Shows 🔒 icon if true
    isMovable: visit.isMovable, // Shows dashed border if true
    visitStatus: visit.visitStatus, // mandatory/optional, movable, cancelled/absent/extra/regular
    priority: visit.priority,
    // Preferences
    preferredStaff: visit.preferredStaff?.map((e) => e.id) || [],
    nonPreferredStaff: visit.nonPreferredStaff?.map((e) => e.id) || [],
    // Continuity and allocation
    continuity: visit.continuity,
    allocatedHours: visit.allocatedHours,
    unusedHours: visit.unusedHours, // Client's unused allocation (monthly allocation - actual service hours)
    // SLA
    sla: visit.sla,
  };
}

/**
 * Maps employee shifts and breaks to Bryntum calendars
 */
function mapEmployeeToCalendar(employee: Employee) {
  const calendars = [];

  // Working hours (shifts)
  employee.shifts?.forEach((shift) => {
    calendars.push({
      id: `shift-${shift.id}`,
      resourceId: employee.id,
      startDate: shift.minStartTime,
      endDate: shift.maxEndTime,
      name: "Working Hours",
      cls: "shift-time-range",
    });
  });

  // Breaks
  employee.shifts?.forEach((shift) => {
    shift.breaks?.forEach((breakPeriod) => {
      calendars.push({
        id: `break-${breakPeriod.id}`,
        resourceId: employee.id,
        startDate: breakPeriod.minStartTime,
        endDate: breakPeriod.maxEndTime,
        name: `Break (${breakPeriod.breakType})`,
        cls: "break-event",
      });
    });
  });

  return calendars;
}

/**
 * Maps Bryntum changes back to GraphQL mutation input
 */
export function mapBryntumChangesToUpdate(
  changes: any,
  scheduleId: string,
): UpdateScheduleInput {
  return {
    id: scheduleId,
    visits: changes.events.map((event: any) => ({
      id: event.id,
      plannedStartTime: event.startDate,
      plannedEndTime: event.endDate,
      assignedEmployeeId: event.resourceId,
      pinned: event.pinned,
    })),
  };
}

/**
 * Maps raw Timefold solver data to Bryntum format (real-time optimization updates)
 *
 * Key: No database lookups - uses IDs only for performance
 * Used during optimization for real-time calendar preview (polling every 2 seconds)
 */
export function mapRawSolverDataToBryntum(rawSolverData: any) {
  return {
    resources: rawSolverData.vehicles.map((v: any) => ({
      id: v.id,
      name: `Employee ${v.id.substring(0, 6)}`, // Placeholder, no DB lookup
    })),
    events: rawSolverData.assignments.map((a: any) => ({
      id: a.visitId,
      resourceId: a.employeeId,
      startDate: a.startTime,
      endDate: a.endTime,
      eventType: "visit",
      // Minimal data - no client names, no details
    })),
  };
}

/**
 * Maps pre-planning data (multiple schedules across time horizon) to Bryntum format
 */
export function prePlanningDataToBryntum(prePlanningData: any) {
  return {
    resources: prePlanningData.employees.map(mapEmployeeToResource),
    events: [
      ...prePlanningData.pinnedVisits.map((v: Visit) => ({
        ...mapVisitToEvent(v),
        pinned: true,
        cls: "pinned-visit", // Solid blue background
      })),
      ...prePlanningData.unpinnedVisits.map((v: Visit) => ({
        ...mapVisitToEvent(v),
        pinned: false,
        cls: "unpinned-visit", // Dashed border
      })),
    ],
    unassignedVisits: prePlanningData.unassignedVisits.map((v: Visit) => ({
      id: v.id,
      name: v.name,
      clientName: v.client?.name,
      duration: v.duration,
      timeWindow: {
        minStart: v.minStartTime,
        maxStart: v.maxStartTime,
        maxEnd: v.maxEndTime,
      },
      preferredTimeWindows: v.preferredTimeWindows || [],
      priority: v.priority,
      requiredSkills: v.requiredSkills?.map((s) => s.skillName) || [],
    })),
  };
}
```

---

### Step 2: Create GraphQL Hooks (4-6 hours)

**Location:** `src/features/scheduling/hooks/`

> **Key:** Standard Apollo Client patterns following GraphQL best practices.

```typescript
// useSchedule.ts
import { useQuery } from "@apollo/client";
import { GET_SCHEDULE } from "../graphql/queries/getSchedule.graphql";
import { mapScheduleToBryntum } from "../lib/mappers";

export function useSchedule(scheduleId: string) {
  const { data, loading, error } = useQuery(GET_SCHEDULE, {
    variables: { id: scheduleId },
    skip: !scheduleId,
  });

  const bryntumData = data?.schedule
    ? mapScheduleToBryntum(data.schedule)
    : null;

  return {
    schedule: data?.schedule,
    bryntumData,
    loading,
    error,
  };
}
```

```typescript
// useUpdateSchedule.ts
import { useMutation } from "@apollo/client";
import { UPDATE_SCHEDULE } from "../graphql/mutations/updateSchedule.graphql";
import { mapBryntumChangesToUpdate } from "../lib/mappers";

export function useUpdateSchedule() {
  const [updateSchedule, { loading, error }] = useMutation(UPDATE_SCHEDULE, {
    // Optimistic update
    optimisticResponse: (vars) => ({
      updateSchedule: {
        __typename: "Schedule",
        id: vars.id,
        // ... optimistic data
      },
    }),
  });

  const handleSave = (bryntumChanges: any, scheduleId: string) => {
    const input = mapBryntumChangesToUpdate(bryntumChanges, scheduleId);
    return updateSchedule({ variables: { input } });
  };

  return {
    saveSchedule: handleSave,
    loading,
    error,
  };
}
```

---

### Step 3: Build SchedulerView Component (2-3 hours)

**Implementation with GraphQL:**

```typescript
// src/features/scheduling/components/bryntum-calendar/SchedulerView.tsx
import { useSchedule } from '../../hooks/useSchedule';
import { useUpdateSchedule } from '../../hooks/useUpdateSchedule';

interface SchedulerViewProps {
  scheduleId: string;
}

export function SchedulerView({ scheduleId }: SchedulerViewProps) {
  const { bryntumData, loading, error } = useSchedule(scheduleId);
  const { saveSchedule, loading: saving } = useUpdateSchedule();

  if (loading) return <LoadingState />;
  if (error) return <ErrorState error={error} />;
  if (!bryntumData) return <EmptyState />;

  const handleSave = (changes: any) => {
    saveSchedule(changes, scheduleId);
  };

  return (
    <SchedulerPro
      {...bryntumData}
      onEventChange={handleSave}
      // ... other Bryntum config
    />
  );
}
```

---

### Step 4: Real-time Updates (P2 - Optional)

**GraphQL Subscription for Optimization Progress:**

> **Note:** WebSocket real-time updates are P2 (nice to have). Basic optimization uses polling (P0).

**Important:** During optimization, only raw solver data is available (IDs only, no names/details). Full data with metrics becomes available only after optimization completes.

```typescript
// src/features/scheduling/hooks/useOptimizationProgress.ts
import { useSubscription } from "@apollo/client";
import { OPTIMIZATION_PROGRESS } from "../graphql/subscriptions/optimizationProgress.graphql";
import {
  mapRawSolverDataToBryntum,
  mapScheduleToBryntum,
} from "../lib/mappers";

export function useOptimizationProgress(jobId: string) {
  const { data, loading } = useSubscription(OPTIMIZATION_PROGRESS, {
    variables: { jobId },
    skip: !jobId,
  });

  return {
    progress: data?.optimizationProgress,
    rawSolution: data?.optimizationProgress?.rawSolution, // Raw solver data (during optimization)
    completeSolution: data?.optimizationProgress?.completeSolution, // Full solution (after completion)
    loading,
  };
}
```

**Use in component:**

```typescript
const { progress, rawSolution, completeSolution } =
  useOptimizationProgress(optimizationJobId);

// Update Bryntum with progress updates
useEffect(() => {
  if (progress) {
    if (progress.status === "solving_active" && rawSolution) {
      // During optimization: Use raw solver data (IDs only, fast updates)
      const bryntumData = mapRawSolverDataToBryntum(rawSolution);
      scheduler.eventStore.data = bryntumData;
    } else if (progress.status === "solving_completed" && completeSolution) {
      // After completion: Use complete solution with full data and metrics
      const bryntumData = mapScheduleToBryntum(completeSolution);
      scheduler.eventStore.data = bryntumData;
      // Fetch and display metrics
      refetchMetrics();
    }
  }
}, [progress, rawSolution, completeSolution]);
```

**Pre-Planning Optimization Progress:**

```typescript
// src/features/scheduling/hooks/usePrePlanningProgress.ts
import { useSubscription } from "@apollo/client";
import { PRE_PLANNING_PROGRESS } from "../graphql/subscriptions/prePlanningProgress.graphql";

export function usePrePlanningProgress(jobId: string) {
  const { data, loading } = useSubscription(PRE_PLANNING_PROGRESS, {
    variables: { jobId },
    skip: !jobId,
  });

  return {
    progress: data?.prePlanningProgress,
    stage: data?.prePlanningProgress?.stage, // 'pattern_discovery' | 'employee_assignment'
    loading,
  };
}
```

---

## Bryntum Configuration

### Base Configuration

```typescript
// src/features/scheduling/components/bryntum-calendar/schedulerConfig.ts
import { SchedulerProConfig } from "@bryntum/schedulerpro";

export const baseSchedulerConfig: Partial<SchedulerProConfig> = {
  // View configuration
  viewPreset: "hourAndDay",
  startDate: new Date(),
  endDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days

  // Resource configuration
  resourceColumns: [{ text: "Namn", field: "name", width: 200 }],

  // Event configuration
  eventStyle: "colored",
  eventColor: "blue",

  // Features
  features: {
    eventEdit: true,
    eventDrag: true,
    eventResize: true,
    eventTooltip: true,
    resourceHistogram: true,
  },

  // Localization
  locale: "SvSE",
};
```

### Visual System Integration

**Status Colors:**

```typescript
// Map CAIRE status colors to Bryntum event styles
const statusColors = {
  draft: "#9ca3af", // Grey
  published: "#3b82f6", // Blue
  optimized: "#10b981", // Green
  baseline: "#f59e0b", // Orange
};
```

**Icons:**

```typescript
// Map CAIRE icons to Bryntum event icons
const eventIcons = {
  recurrence: "fa-repeat",
  priority: "fa-exclamation",
  mandatory: "fa-lock",
};
```

---

## Testing

### Component Tests

```typescript
// SchedulerView.test.tsx
import { render, screen } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import { SchedulerView } from './SchedulerView';

const mocks = [
  {
    request: {
      query: GET_SCHEDULE,
      variables: { id: 'schedule-1' },
    },
    result: {
      data: {
        schedule: {
          id: 'schedule-1',
          // ... mock schedule data
        },
      },
    },
  },
];

test('renders scheduler with schedule data', async () => {
  render(
    <MockedProvider mocks={mocks}>
      <SchedulerView scheduleId="schedule-1" />
    </MockedProvider>
  );

  expect(await screen.findByText('Schedule Name')).toBeInTheDocument();
});
```

### Integration Tests

```typescript
// Test drag-and-drop functionality
test("can drag visit to different employee", async () => {
  // Setup
  const { scheduler } = renderScheduler();

  // Action
  await dragEvent("visit-1", "employee-2");

  // Assert
  expect(saveSchedule).toHaveBeenCalledWith({
    visits: [
      {
        id: "visit-1",
        assignedEmployeeId: "employee-2",
      },
    ],
  });
});
```

---

## Performance Optimization

### 1. Lazy Load Bryntum

```typescript
// Lazy load heavy Bryntum component
const SchedulerView = lazy(() => import('./bryntum-calendar/SchedulerView'));

function SchedulingPage() {
  return (
    <Suspense fallback={<LoadingState />}>
      <SchedulerView scheduleId={scheduleId} />
    </Suspense>
  );
}
```

### 2. Memoize Mapper Functions

```typescript
const bryntumData = useMemo(
  () => (schedule ? mapScheduleToBryntum(schedule) : null),
  [schedule],
);
```

### 3. Optimize GraphQL Queries

Only fetch fields needed for Bryntum:

```graphql
query GetScheduleForCalendar($id: ID!) {
  schedule(id: $id) {
    id
    name
    date
    employees {
      id
      name
      # Only fields needed for Bryntum resources
    }
    visits {
      id
      clientName
      plannedStartTime
      plannedEndTime
      assignedEmployeeId
      # Only fields needed for Bryntum events
    }
  }
}
```

---

## Troubleshooting

### Issue: Bryntum not rendering

**Solution:**

- Check that Bryntum CSS is imported
- Verify container has width/height
- Check browser console for errors

### Issue: Data not updating

**Solution:**

- Verify GraphQL query is executing
- Check mapper function output
- Ensure Apollo cache is updating

### Issue: Drag-and-drop not working

**Solution:**

- Verify `eventDrag` feature is enabled
- Check constraints/validation rules
- Ensure mutation is being called on drop

---

## Pre-Planning Features (Phase 9)

**Reference:** See `BRYNTUM_FROM_SCRATCH_PRD.md` Phase 9 for complete specifications

**Key Features:**

1. **Pre-Planning Hub** - Multi-week/month consolidated schedule view
2. **Movable Visits Management** - Create and configure recurring visits with flexible time windows
3. **Supply/Demand Balance Dashboard** - Visual indicators of capacity vs demand
4. **Unused Hours Tracking** - Display and recapture unused client allocation hours
5. **Pre-Planning Optimization** - Two-stage optimization (Pattern Discovery → Employee Assignment)
6. **Diff View** - Ghost tracks for original positions, solid blocks for optimized positions
7. **Schedule Health Tracking** - Long-term metrics and trend analysis

**GraphQL Operations:**

- **Queries:** `prePlanningData`, `supplyDemandBalance`, `demandCurve`, `unusedHours`, `getOptimalPlacementRecommendations`
- **Mutations:** `createMovableVisit`, `updateMovableVisit`, `runPrePlanningOptimization`, `acceptPrePlanningSolution`
- **Subscriptions:** `prePlanningProgress(jobId)`

**Mapper Functions:**

- `prePlanningDataToBryntum(prePlanningData)` - Multi-week/month consolidated view
- `mapRawSolverDataToBryntum(rawSolverData)` - Real-time pre-planning updates

**Implementation:** See `PREPLANNING_FRONTEND_IMPLEMENTATION.md` for detailed frontend guide

---

## Metrics Integration

**Key:** Metrics are calculated and stored in the backend, not in the frontend. Frontend only fetches and displays pre-calculated metrics.

**Metrics Levels:**

- Schedule-level metrics
- Employee-level metrics
- Client-level metrics (including profitability analysis)
- Service area-level metrics
- Organization-level metrics

**Financial Metrics (RBAC):**

- Cost, revenue, profit only visible to authorized roles
- Frontend applies RBAC filtering before display

**Mapper Function:**

- `mapMetricsToDisplay(metrics, userRole)` - Filters financial metrics based on user permissions

---

## Related Documents

- **Frontend Refactoring:** `FRONTEND_REFACTORING.md`
- **Component Structure:** `COMPONENT_STRUCTURE.md`
- **Bryntum PRD:** `../05-prd/bryntum_consultant_specs/BRYNTUM_FROM_SCRATCH_PRD.md`
- **Backend Spec:** `../05-prd/bryntum_consultant_specs/BRYNTUM_BACKEND_SPEC.md`
- **Mapper Specs:** `../02-api/MAPPER_SPECIFICATIONS.md`
- **Pre-Planning Frontend:** `../09-scheduling/PREPLANNING_FRONTEND_IMPLEMENTATION.md`
- **API Design:** `../02-api/API_DESIGN.md`

---

**Status:** ✅ Ready for implementation  
**Timeline:** 14-19 days (112-152 hours) - See `bryntum_timeplan.md` for detailed phase breakdown  
**Next Steps:** Follow `BRYNTUM_FROM_SCRATCH_PRD.md` and `bryntum_timeplan.md` for phased implementation

---

## Implementation Approach

### ✅ Building from Scratch

- Following `BRYNTUM_FROM_SCRATCH_PRD.md` specifications
- Phased implementation per `bryntum_timeplan.md`
- Priority-based development (P0 → P1 → P2)

### ✅ Clear Structure

- Mapper functions transform normalized GraphQL data to Bryntum format
- Standard Apollo Client patterns for data fetching
- Component structure follows feature-based organization

### ✅ Normalized Data Model

- All data comes from normalized database tables via GraphQL
- No stored JSON - straightforward mapping
- Resources pages: Simple CRUD
- Analytics pages: GraphQL queries + charts
- Admin pages: Simple forms
