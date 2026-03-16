# Frontend Component Structure Guide

**Purpose:** Best practices for organizing React components in the CAIRE frontend  
**Related:** `FRONTEND_REFACTORING.md`, `architecture.md`

---

## Folder Structure

```
packages/client/
├── src/
│   ├── features/              # Feature modules (self-contained)
│   │   ├── scheduling/
│   │   ├── analytics/
│   │   ├── resources/
│   │   ├── templates/
│   │   └── admin/
│   ├── components/            # Shared components
│   │   ├── ui/               # Base UI components
│   │   ├── layout/           # Layout components
│   │   ├── feedback/         # Loading, error, empty states
│   │   └── forms/            # Form components
│   ├── hooks/                # Shared custom hooks
│   ├── lib/                  # Utilities, helpers, mappers
│   ├── graphql/              # GraphQL operations
│   │   ├── queries/
│   │   ├── mutations/
│   │   ├── subscriptions/
│   │   └── generated.ts      # Auto-generated types
│   ├── styles/               # Global styles, Tailwind config
│   ├── App.tsx               # Root component
│   └── main.tsx              # Entry point
├── public/                   # Static assets
├── vite.config.ts
└── package.json
```

---

## Feature Module Structure

Each feature is self-contained with its own components, hooks, GraphQL operations, and utilities.

### Example: Scheduling Feature

```
src/features/scheduling/
├── components/
│   ├── ScheduleList.tsx              # List view
│   ├── ScheduleCard.tsx              # Schedule card item
│   ├── ScheduleDetail.tsx            # Detail view wrapper
│   ├── ScheduleHeader.tsx            # Header with actions
│   ├── bryntum-calendar/             # Bryntum-specific components
│   │   ├── SchedulerView.tsx          # Main calendar view
│   │   ├── LegendAndFiltering.tsx     # Legend and filters
│   │   ├── ResourceHistogram.tsx      # Resource utilization chart
│   │   ├── ComparisonView.tsx         # Baseline vs optimized
│   │   └── MetricsPanel.tsx           # Metrics display
│   └── pre-planning/                 # Pre-planning components
│       ├── PrePlanningHub.tsx         # Main pre-planning entry point
│       ├── MovableVisitsPanel.tsx     # Unassigned visits sidebar
│       ├── ConsolidatedCalendarView.tsx # Multi-week/month view
│       ├── SupplyDemandDashboard.tsx  # Supply/demand balance
│       ├── UnusedHoursTracker.tsx    # Unused hours display
│       ├── DemandCurveChart.tsx      # Demand trend visualization
│       └── PrePlanningDiffView.tsx    # Diff view (ghost tracks)
├── hooks/
│   ├── useSchedule.ts                # Single schedule query
│   ├── useSchedules.ts               # List of schedules
│   ├── useCreateSchedule.ts           # Create schedule mutation
│   ├── useUpdateSchedule.ts           # Update schedule mutation
│   ├── useOptimization.ts             # Run optimization
│   ├── useOptimizationProgress.ts     # Optimization progress subscription
│   ├── usePrePlanningData.ts         # Pre-planning data query
│   ├── usePrePlanningOptimization.ts  # Run pre-planning optimization
│   ├── usePrePlanningProgress.ts     # Pre-planning progress subscription
│   ├── useMovableVisits.ts           # Movable visits CRUD
│   ├── useSupplyDemandBalance.ts     # Supply/demand metrics
│   └── useMetrics.ts                 # Schedule metrics (with RBAC)
├── graphql/
│   ├── queries/
│   │   ├── getSchedule.graphql
│   │   ├── getSchedules.graphql
│   │   ├── getScheduleMetrics.graphql
│   │   ├── prePlanningData.graphql
│   │   ├── supplyDemandBalance.graphql
│   │   ├── demandCurve.graphql
│   │   └── unusedHours.graphql
│   ├── mutations/
│   │   ├── createSchedule.graphql
│   │   ├── updateSchedule.graphql
│   │   ├── runOptimization.graphql
│   │   ├── createMovableVisit.graphql
│   │   ├── updateMovableVisit.graphql
│   │   ├── runPrePlanningOptimization.graphql
│   │   └── acceptPrePlanningSolution.graphql
│   └── subscriptions/
│       ├── optimizationProgress.graphql
│       └── prePlanningProgress.graphql
├── lib/
│   ├── mappers.ts                    # DB ↔ Bryntum mappers (10+ functions)
│   │   ├── mapScheduleToBryntum
│   │   ├── mapEmployeeToResource
│   │   ├── mapVisitToEvent
│   │   ├── mapEmployeeToCalendar
│   │   ├── mapBryntumChangesToUpdate
│   │   ├── mapSolutionToBryntum
│   │   ├── mapRawSolverDataToBryntum
│   │   ├── prePlanningDataToBryntum
│   │   └── mapMetricsToDisplay
│   └── validators.ts                 # Schedule validation
└── pages/
    ├── SchedulingPage.tsx             # Main scheduling page
    └── PrePlanningPage.tsx            # Pre-planning hub page
```

---

## Component Types

### 1. Page Components

**Location:** `features/{feature}/pages/`  
**Purpose:** Top-level route components

```typescript
// src/features/scheduling/pages/SchedulingPage.tsx
import { ScheduleList } from '../components/ScheduleList';
import { ScheduleDetail } from '../components/ScheduleDetail';

export function SchedulingPage() {
  return (
    <div className="flex h-screen">
      <aside className="w-80">
        <ScheduleList />
      </aside>
      <main className="flex-1">
        <ScheduleDetail />
      </main>
    </div>
  );
}
```

**Guidelines:**

- ✅ One page component per route
- ✅ Composes feature components
- ✅ Handles routing logic
- ✅ Minimal business logic

---

### 2. Feature Components

**Location:** `features/{feature}/components/`  
**Purpose:** Feature-specific UI components

```typescript
// src/features/scheduling/components/ScheduleList.tsx
import { useSchedules } from '../hooks/useSchedules';
import { ScheduleCard } from './ScheduleCard';

export function ScheduleList() {
  const { schedules, loading, error } = useSchedules();

  if (loading) return <LoadingState />;
  if (error) return <ErrorState error={error} />;
  if (!schedules.length) return <EmptyState />;

  return (
    <div className="space-y-2">
      {schedules.map(schedule => (
        <ScheduleCard key={schedule.id} schedule={schedule} />
      ))}
    </div>
  );
}
```

**Guidelines:**

- ✅ Feature-specific logic
- ✅ Uses feature hooks
- ✅ Can use shared components
- ✅ Self-contained

---

### 3. Shared Components

**Location:** `components/`  
**Purpose:** Reusable UI components used across features

#### UI Components (`components/ui/`)

Base UI building blocks:

```
components/ui/
├── Button.tsx
├── Input.tsx
├── Select.tsx
├── Modal.tsx
├── Card.tsx
└── Badge.tsx
```

```typescript
// src/components/ui/Button.tsx
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
}

export function Button({ variant = 'primary', size = 'md', children, onClick }: ButtonProps) {
  return (
    <button
      className={cn(
        'rounded-md font-medium',
        variants[variant],
        sizes[size]
      )}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

#### Layout Components (`components/layout/`)

```
components/layout/
├── Header.tsx
├── Sidebar.tsx
├── MainLayout.tsx
└── PageContainer.tsx
```

#### Feedback Components (`components/feedback/`)

```
components/feedback/
├── LoadingState.tsx
├── ErrorState.tsx
├── EmptyState.tsx
└── SkeletonLoader.tsx
```

**Guidelines:**

- ✅ Generic and reusable
- ✅ No feature-specific logic
- ✅ Well-documented props
- ✅ Accessible (ARIA labels, keyboard navigation)

---

## Custom Hooks

### Feature Hooks

**Location:** `features/{feature}/hooks/`  
**Purpose:** Feature-specific data fetching and state management

```typescript
// src/features/scheduling/hooks/useSchedule.ts
import { useQuery } from "@apollo/client";
import { GET_SCHEDULE } from "../graphql/queries/getSchedule.graphql";

export function useSchedule(scheduleId: string) {
  const { data, loading, error, refetch } = useQuery(GET_SCHEDULE, {
    variables: { id: scheduleId },
    skip: !scheduleId,
  });

  return {
    schedule: data?.schedule,
    loading,
    error,
    refetch,
  };
}
```

### Shared Hooks

**Location:** `hooks/`  
**Purpose:** Reusable hooks across features

```
hooks/
├── useAuth.ts              # Clerk authentication
├── useOrganization.ts      # Current organization
├── usePermissions.ts       # RBAC permissions
└── useDebounce.ts          # Debounce utility
```

**Guidelines:**

- ✅ Start with `use` prefix
- ✅ Return object (not array) for named destructuring
- ✅ Handle loading/error states
- ✅ Document with JSDoc

---

## GraphQL Organization

### File Structure

```
graphql/
├── queries/
│   ├── schedules/
│   │   ├── getSchedule.graphql
│   │   └── getSchedules.graphql
│   └── employees/
│       └── getEmployees.graphql
├── mutations/
│   ├── schedules/
│   │   ├── createSchedule.graphql
│   │   └── updateSchedule.graphql
│   └── optimization/
│       └── runOptimization.graphql
├── subscriptions/
│   └── optimizationProgress.graphql
└── generated.ts            # Auto-generated by GraphQL Codegen
```

### Query Example

```graphql
# src/features/scheduling/graphql/queries/getSchedule.graphql
query GetSchedule($id: ID!) {
  schedule(id: $id) {
    id
    name
    date
    status
    employees {
      id
      name
      email
    }
    visits {
      id
      clientName
      plannedStartTime
      plannedEndTime
    }
  }
}
```

**Guidelines:**

- ✅ One operation per file
- ✅ Group by feature/domain
- ✅ Use descriptive names
- ✅ Only fetch needed fields

---

## Mapper Functions

**Location:** `features/{feature}/lib/mappers.ts`  
**Purpose:** Transform data between GraphQL types and UI component formats

**Reference:** See `MAPPER_SPECIFICATIONS.md` for complete mapper specifications

**Required Mappers (per MAPPER_SPECIFICATIONS.md):**

1. **`mapScheduleToBryntum(schedule)`** - Main schedule mapper (employees, visits, assignments, calendars)
2. **`mapEmployeeToResource(employee)`** - Employee → Resource (includes service area, preferences, contact person relationships)
3. **`mapVisitToEvent(visit)`** - Visit → Event (includes time windows, preferences, continuity, allocated hours, unused hours)
4. **`mapEmployeeToCalendar(employee)`** - Shifts/breaks → Bryntum calendars
5. **`mapBryntumChangesToUpdate(changes, scheduleId)`** - User edits → GraphQL mutation input
6. **`mapSolutionToBryntum(solution)`** - Optimization solution → Bryntum format
7. **`mapRawSolverDataToBryntum(rawSolverData)`** - Real-time optimization updates (IDs only, no DB lookups)
8. **`prePlanningDataToBryntum(prePlanningData)`** - Multi-week/month pre-planning data
9. **`mapMetricsToDisplay(metrics, userRole)`** - Metrics with RBAC filtering (financial metrics only for authorized roles)

**Example Implementation:**

```typescript
// src/features/scheduling/lib/mappers.ts
import { Schedule, Employee, Visit } from "@/graphql/generated";
import { SchedulerPro } from "@bryntum/schedulerpro";

/**
 * Maps GraphQL Schedule to Bryntum SchedulerPro format
 *
 * Key: Maps from normalized database structure (Caire 2.0 architecture)
 * Includes: Employees, visits, assignments, shifts, breaks, metrics
 */
export function mapScheduleToBryntum(schedule: Schedule) {
  return {
    resources: schedule.employees.map(mapEmployeeToResource),
    events: schedule.visits.map(mapVisitToEvent),
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
    calendars: schedule.employees.flatMap((emp) => mapEmployeeToCalendar(emp)),
  };
}

/**
 * Maps employee with all required fields including:
 * - Service area
 * - Preferred/non-preferred clients
 * - Contact person-client relationships
 * - Skills, transport mode, contract type
 */
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

/**
 * Maps visit with all required fields including:
 * - Time windows (hard: minStartTime/maxStartTime/maxEndTime)
 * - Preferred time windows (soft: preferredTimeWindows jsonb array)
 * - Visit type (mandatory/optional, movable, cancelled/absent/extra/regular)
 * - Preferences (preferred/non-preferred staff, continuity)
 * - Allocation (allocated hours, unused hours - client-side)
 * - SLA requirements
 */
function mapVisitToEvent(visit: Visit) {
  return {
    id: visit.id,
    name: visit.name || visit.clientName,
    startDate: visit.plannedStartTime || visit.assignment?.startTime,
    endDate: visit.plannedEndTime || visit.assignment?.endTime,
    duration: visit.duration,
    pinned: visit.pinned, // Shows 🔒 icon if true
    isMovable: visit.isMovable, // Shows dashed border if true
    visitStatus: visit.visitStatus,
    priority: visit.priority,
    // Time windows
    minStartTime: visit.minStartTime,
    maxStartTime: visit.maxStartTime,
    maxEndTime: visit.maxEndTime,
    preferredTimeWindows: visit.preferredTimeWindows || [], // jsonb array
    allowedWindowStart: visit.allowedWindowStart,
    allowedWindowEnd: visit.allowedWindowEnd,
    // Preferences
    preferredStaff: visit.preferredStaff?.map((e) => e.id) || [],
    nonPreferredStaff: visit.nonPreferredStaff?.map((e) => e.id) || [],
    // Continuity and allocation
    continuity: visit.continuity,
    allocatedHours: visit.allocatedHours,
    unusedHours: visit.unusedHours, // Client's unused allocation
    // ... other fields
  };
}

/**
 * Maps Bryntum changes back to GraphQL mutation input
 */
export function mapBryntumChangesToUpdate(
  bryntumChanges: any,
  scheduleId: string,
): UpdateScheduleInput {
  return {
    id: scheduleId,
    visits: bryntumChanges.events.map((event: any) => ({
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
        cls: "pinned-visit",
      })),
      ...prePlanningData.unpinnedVisits.map((v: Visit) => ({
        ...mapVisitToEvent(v),
        pinned: false,
        cls: "unpinned-visit",
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

/**
 * Maps metrics to display format with RBAC filtering
 *
 * Key: Financial metrics (cost, revenue, profit) only visible to authorized roles
 * Backend returns all metrics, frontend applies RBAC filtering
 */
export function mapMetricsToDisplay(metrics: any, userRole: string) {
  const hasFinancialAccess = ["admin", "finance"].includes(userRole);

  return {
    schedule: {
      ...metrics.schedule,
      cost: hasFinancialAccess ? metrics.schedule.cost : undefined,
      revenue: hasFinancialAccess ? metrics.schedule.revenue : undefined,
      profit: hasFinancialAccess ? metrics.schedule.profit : undefined,
    },
    employees: metrics.employees.map((emp: any) => ({
      ...emp,
      cost: hasFinancialAccess ? emp.cost : undefined,
      revenue: hasFinancialAccess ? emp.revenue : undefined,
      profit: hasFinancialAccess ? emp.profit : undefined,
    })),
    clients: metrics.clients.map((client: any) => ({
      ...client,
      revenue: hasFinancialAccess ? client.revenue : undefined,
      cost: hasFinancialAccess ? client.cost : undefined,
      profit: hasFinancialAccess ? client.profit : undefined,
      profitabilityRatio: hasFinancialAccess
        ? client.profitabilityRatio
        : undefined,
    })),
  };
}
```

**Guidelines:**

- ✅ Pure functions (no side effects)
- ✅ Type-safe (use generated types)
- ✅ Well-documented
- ✅ Handle edge cases (null, undefined)
- ✅ Follow MAPPER_SPECIFICATIONS.md for complete field mappings
- ✅ Support both regular scheduling and pre-planning use cases

---

## Naming Conventions

### Files

- **Components:** PascalCase (`ScheduleList.tsx`)
- **Hooks:** camelCase with `use` prefix (`useSchedule.ts`)
- **Utilities:** camelCase (`mappers.ts`, `validators.ts`)
- **GraphQL:** camelCase (`getSchedule.graphql`)

### Components

- **Page components:** `{Feature}Page.tsx` (e.g., `SchedulingPage.tsx`)
- **Feature components:** Descriptive name (e.g., `ScheduleList.tsx`)
- **UI components:** Generic name (e.g., `Button.tsx`, `Modal.tsx`)

### Hooks

- **Data fetching:** `use{Resource}` (e.g., `useSchedule`, `useSchedules`)
- **Mutations:** `use{Action}{Resource}` (e.g., `useCreateSchedule`, `useUpdateSchedule`)
- **Subscriptions:** `use{Event}` (e.g., `useOptimizationProgress`)

---

## Best Practices

### 1. Component Size

- ✅ Keep components under 200 lines
- ✅ Extract sub-components if too large
- ✅ Extract logic to custom hooks

### 2. Props

- ✅ Use TypeScript interfaces for props
- ✅ Destructure props in function signature
- ✅ Provide default values where appropriate
- ✅ Document complex props

### 3. State Management

- ✅ Use Apollo Client for server state
- ✅ Use React state for UI state
- ✅ Use Context for global UI state (theme, sidebar)
- ✅ Avoid prop drilling (use Context or composition)

### 4. Performance

- ✅ Memoize expensive computations (`useMemo`)
- ✅ Memoize callbacks (`useCallback`)
- ✅ Memoize components (`React.memo`) when needed
- ✅ Lazy load heavy components (Bryntum)

### 5. Testing

- ✅ Test components in isolation
- ✅ Test hooks separately
- ✅ Use React Testing Library
- ✅ Test user interactions, not implementation

---

## Pre-Planning Components

**Reference:** See `BRYNTUM_FROM_SCRATCH_PRD.md` Phase 9 and `PREPLANNING_FRONTEND_IMPLEMENTATION.md`

**Key Components:**

1. **PrePlanningHub** - Main entry point (`/dashboard/scheduling/pre-planning`)
2. **MovableVisitsPanel** - Unassigned visits sidebar with drag-and-drop
3. **ConsolidatedCalendarView** - Multi-week/month Bryntum calendar
4. **SupplyDemandDashboard** - Visual supply/demand balance indicators
5. **UnusedHoursTracker** - Unused hours display and recapture opportunities
6. **DemandCurveChart** - Demand trend visualization
7. **PrePlanningDiffView** - Diff view showing optimization changes (ghost tracks + solid blocks)

**GraphQL Operations:**

- **Queries:** `prePlanningData`, `supplyDemandBalance`, `demandCurve`, `unusedHours`
- **Mutations:** `createMovableVisit`, `updateMovableVisit`, `runPrePlanningOptimization`, `acceptPrePlanningSolution`
- **Subscriptions:** `prePlanningProgress(jobId)`

---

## Related Documents

- **Frontend Refactoring:** `FRONTEND_REFACTORING.md`
- **Bryntum Integration:** `BRYNTUM_INTEGRATION.md`
- **Architecture:** `../01-architecture/architecture.md`
- **API Design:** `../02-api/API_DESIGN.md`
- **Mapper Specifications:** `../02-api/MAPPER_SPECIFICATIONS.md`
- **Pre-Planning Frontend:** `../09-scheduling/PREPLANNING_FRONTEND_IMPLEMENTATION.md`
- **Bryntum PRD:** `../05-prd/bryntum_consultant_specs/BRYNTUM_FROM_SCRATCH_PRD.md`

---

**Status:** ✅ Ready for implementation
