# Frontend Refactoring Strategy

**Project:** CAIRE Platform Refactoring  
**Current:** Next.js app with 319 API routes  
**Target:** React + Vite + GraphQL client (Apollo)  
**Timeline:** 1-2 weeks (40-80 hours) ⚡ **Dramatically reduced**  
**Related:** `architecture.md`, `API_DESIGN_V2.md`, `bryntum-reference.md`, `../05-prd/bryntum_consultant_specs/BRYNTUM_FROM_SCRATCH_PRD.md`

---

## Quick Answer

**Frontend refactoring approach:**

✅ **React 18** + **Vite** (replacing Next.js for client-side app)  
✅ **Apollo Client** (GraphQL queries, mutations, subscriptions)  
✅ **Bryntum SchedulerPro** (calendar/scheduling UI component) - **Already built!** ✅  
✅ **React Router** (client-side routing)  
✅ **TypeScript** (full type safety)  
✅ **Tailwind CSS** (styling)

**Key Insight:** Building Bryntum integration from scratch following the PRD specifications.

**Scope:**

- ✅ **Scheduling UI:** Build from scratch following `BRYNTUM_FROM_SCRATCH_PRD.md` (see `bryntum_timeplan.md` for timeline)
- ✅ **GraphQL Integration:** Connect to new API with mapper functions
- ✅ **Pre-Planning Features:** Multi-week/month planning with movable visits (Phase 9 from BRYNTUM_FROM_SCRATCH_PRD.md)
- ✅ **Simple CRUD Pages:** Resources, analytics, admin (no complex business logic)
- ✅ **Real-time Updates:** GraphQL subscriptions for optimization progress (P2 - WebSocket optional)

---

## Current State Analysis

### Problems with Current Frontend

- ❌ Tightly coupled to Next.js API routes
- ❌ Uses 319 different REST endpoints
- ❌ No type safety between frontend and backend
- ❌ Mixed server/client rendering (unnecessary complexity)
- ❌ Hard to test (server/client boundaries unclear)
- ❌ Difficult to maintain (scattered API calls)

### What to Build

- ✅ **Bryntum SchedulerPro integration** (building from scratch per BRYNTUM_FROM_SCRATCH_PRD.md)
  - Timeline calendar, drag-and-drop, filters, legend
  - Swedish localization
  - Visual system (colors, icons, status indicators)
  - Resource histogram, comparison view, scenario modal
  - All UX patterns and workflows
- ✅ **Component structure** (all components ready)
- ✅ **Styling and visual system** (complete)
- ✅ **User workflows** (proven and tested)

### What to Replace

- ❌ Next.js API route calls → GraphQL queries/mutations
- ❌ Server-side rendering → Client-side React app
- ❌ Scattered API calls → Centralized Apollo Client
- ❌ Manual state management → GraphQL cache + React hooks

---

## Target Architecture

### Tech Stack

```
packages/client/
├── src/
│   ├── features/           # Feature modules
│   │   ├── scheduling/     # Calendar, optimization, schedules
│   │   ├── analytics/       # Metrics, dashboards, reports
│   │   ├── resources/       # Employees, clients, service areas
│   │   ├── templates/       # Schedule templates, movable visits
│   │   └── admin/          # Settings, users, integrations
│   ├── components/         # Shared UI components
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utilities, mappers, helpers
│   ├── graphql/            # GraphQL queries, mutations, types
│   └── App.tsx             # Root component
├── vite.config.ts
└── package.json
```

### Key Technologies

**1. React 18 + Vite**

- Fast development server
- Hot module replacement
- Optimized production builds
- No SSR complexity (pure client app)

**2. Apollo Client**

- GraphQL queries, mutations, subscriptions
- Automatic caching and cache updates
- Optimistic UI updates
- TypeScript code generation from schema

**3. Bryntum SchedulerPro**

- Calendar/scheduling UI component
- Drag-and-drop scheduling
- Resource management
- Timeline visualization

**4. React Router**

- Client-side navigation
- Protected routes (RBAC)
- Route-based code splitting

**5. State Management**

- Apollo Client cache (server state)
- React Context (global UI state)
- Zustand (optional, for complex local state)

---

## Refactoring Strategy

> **Key Approach:** Building Bryntum integration from scratch following `BRYNTUM_FROM_SCRATCH_PRD.md` specifications.

### Phase 1: Setup & Foundation (2-3 days)

**Goal:** Create new frontend structure and set up Bryntum SchedulerPro foundation

**Tasks:**

1. **Create Vite + React project structure**

   ```bash
   npm create vite@latest client -- --template react-ts
   cd client
   npm install @apollo/client graphql
   npm install @bryntum/schedulerpro
   npm install react-router-dom
   npm install @clerk/clerk-react
   ```

2. **Setup Apollo Client** (standard setup, ~2 hours)

   ```typescript
   // src/lib/apollo-client.ts
   import { ApolloClient, InMemoryCache, createHttpLink } from "@apollo/client";
   import { setContext } from "@apollo/client/link/context";
   import { Clerk } from "@clerk/clerk-react";

   const httpLink = createHttpLink({
     uri: import.meta.env.VITE_GRAPHQL_URL || "http://localhost:4000/graphql",
   });

   const authLink = setContext((_, { headers }) => {
     const token = Clerk.session?.getToken();
     return {
       headers: {
         ...headers,
         authorization: token ? `Bearer ${token}` : "",
       },
     };
   });

   export const apolloClient = new ApolloClient({
     link: authLink.concat(httpLink),
     cache: new InMemoryCache(),
   });
   ```

3. **Set Up Bryntum Component Structure** (~4 hours)
   - Create `src/features/scheduling/components/bryntum-calendar/` structure
   - Set up base SchedulerPro component
   - Configure Bryntum with base settings
   - Follow BRYNTUM_FROM_SCRATCH_PRD.md Phase 1 specifications

4. **Setup Folder Structure** (~2 hours)
   ```
   src/
   ├── features/
   │   ├── scheduling/          # Bryntum SchedulerPro (building from scratch)
   │   ├── resources/           # Simple CRUD pages
   │   ├── analytics/           # Simple CRUD pages
   │   └── admin/              # Simple CRUD pages
   ├── components/             # Shared components
   ├── hooks/                  # Shared hooks
   ├── lib/                    # Utilities, mappers
   └── graphql/                # GraphQL operations
   ```

**Deliverable:** Working Vite app with Bryntum calendar (still using mock data, but structure ready)

**Time:** 8-12 hours (1-1.5 days)

---

### Phase 2: GraphQL Integration (3-4 days)

**Goal:** Replace mock data with GraphQL queries (this is the main work!)

**Tasks:**

1. **Generate TypeScript Types** (~1 hour)

   ```bash
   npm install -D @graphql-codegen/cli @graphql-codegen/typescript @graphql-codegen/typescript-operations
   # Setup codegen.yml and generate types
   ```

2. **Create GraphQL Queries/Mutations** (~4 hours)
   - Create queries for schedules, employees, clients
   - Create mutations for save, optimize
   - Create subscriptions for optimization progress
   - All follow standard GraphQL patterns

3. **Build Mapper Functions** (~12 hours) - **This is the key work!**

   **Reference:** See `MAPPER_SPECIFICATIONS.md` for complete mapper specifications

   **Required Mappers (10+ functions):**
   - `mapScheduleToBryntum(schedule)` - Main schedule mapper
   - `mapEmployeeToResource(employee)` - Employee → Resource (includes service area, preferences)
   - `mapVisitToEvent(visit)` - Visit → Event (includes time windows, preferences, continuity, allocated hours)
   - `mapEmployeeToCalendar(employee)` - Shifts/breaks → Bryntum calendars
   - `mapBryntumChangesToUpdate(changes, scheduleId)` - User edits → GraphQL mutation input
   - `mapSolutionToBryntum(solution)` - Optimization solution → Bryntum format
   - `mapRawSolverDataToBryntum(rawSolverData)` - Real-time optimization updates (IDs only, no DB lookups)
   - `prePlanningDataToBryntum(prePlanningData)` - Multi-week/month pre-planning data
   - `mapMetricsToDisplay(metrics, userRole)` - Metrics with RBAC filtering

   ```typescript
   // src/features/scheduling/lib/mappers.ts
   // Map GraphQL Schedule → Bryntum format (normalized database structure)
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
       calendars: schedule.employees.flatMap((emp) =>
         mapEmployeeToCalendar(emp),
       ),
     };
   }

   // Map Bryntum changes → GraphQL mutation input
   export function mapBryntumToScheduleUpdate(
     changes: any,
     scheduleId: string,
   ) {
     // Simple mapping - data model is normalized!
     // Backend recalculates metrics after save
   }
   ```

4. **Build Core Schedule Viewing** (~4 hours)
   - Implement GraphQL queries for schedule data
   - Create mapper functions (GraphQL ↔ Bryntum format)
   - Build basic SchedulerView component
   - Connect to GraphQL API

**Deliverable:** Bryntum calendar loads real data from GraphQL API

**Time:** 16-20 hours (2-2.5 days)

---

### Phase 3: Pre-Planning Features (2-3 days)

**Goal:** Implement pre-planning workflow with movable visits (Phase 9 from BRYNTUM_FROM_SCRATCH_PRD.md)

**Tasks:**

1. **Pre-Planning Hub** (~8 hours)
   - Time horizon selector (1 week, 1 month, 3 months, custom)
   - Consolidated multi-week/month calendar view
   - Movable visits panel (unassigned visits sidebar)
   - Supply/demand balance dashboard
   - Unused hours tracker

2. **Pre-Planning Optimization** (~6 hours)
   - Pre-planning optimization trigger
   - Real-time progress subscription (two-stage: Pattern Discovery → Employee Assignment)
   - Diff view (ghost tracks for original, solid blocks for optimized)
   - Accept/reject workflow

3. **Pre-Planning Components** (~6 hours)
   - Demand curve visualization
   - Schedule health tracking
   - Optimal placement recommendations
   - Movable visits CRUD operations

**Deliverable:** Complete pre-planning workflow working with GraphQL

**Time:** 20-24 hours (2.5-3 days)

**Reference:** See `PREPLANNING_FRONTEND_IMPLEMENTATION.md` for detailed guide

---

### Phase 4: Simple CRUD Pages (2-3 days)

**Goal:** Build resources, analytics, and admin pages (simple CRUD, no complex logic)

**Tasks:**

1. **Resources Pages** (~8 hours)
   - Employee list/create/edit (standard CRUD)
   - Client list/create/edit (standard CRUD)
   - Service area list/create/edit (standard CRUD)
   - **No complex business logic - just forms and tables!**

2. **Analytics Pages** (~6 hours)
   - Metrics dashboard (GraphQL query + charts)
   - Schedule comparison (build per BRYNTUM_FROM_SCRATCH_PRD.md)
   - KPI visualization (standard charts)
   - **Data model is normalized - queries are straightforward!**
   - **Metrics are pre-calculated in backend - frontend only displays**

3. **Admin Pages** (~6 hours)
   - Settings (standard form)
   - User management (standard CRUD)
   - Integrations (standard CRUD)
   - **Simple forms - no complex workflows!**

**Deliverable:** All feature pages working with GraphQL

**Time:** 20-24 hours (2.5-3 days)

---

### Phase 5: Real-time & Polish (1-2 days)

**Goal:** Add real-time updates, polish, and testing

**Tasks:**

1. **Real-time Updates** (~4 hours)
   - GraphQL subscriptions for optimization progress
   - WebSocket connection (Apollo handles this)
   - Update Bryntum calendar with progress updates
   - **WebSocket updates are P2 (optional) - polling fallback is P0**

2. **Polish & Testing** (~8 hours)
   - Loading states (standard patterns)
   - Error handling (standard patterns)
   - Component tests (standard React Testing Library)
   - Integration tests (critical flows only)

**Deliverable:** Production-ready frontend

**Time:** 12-16 hours (1.5-2 days)

---

## Implementation Timeline

### ✅ Building from Scratch

- **Following BRYNTUM_FROM_SCRATCH_PRD.md** - Complete specifications
- **Phased approach per bryntum_timeplan.md** - 14-19 days (112-152 hours)
- **Visual system** - Colors, icons, status indicators
- **Swedish localization** - All labels translated
- **Filters and legend** - Complex filtering logic complete
- **Resource histogram** - Utilization charts working
- **Comparison view** - Baseline vs optimized comparison
- **Scenario modal** - Optimization scenario selection
- **All UX patterns** - Drag-and-drop, pinned visits, etc.

### ✅ What's Simple (Other Pages)

- **Resources pages** - Standard CRUD (employees, clients, service areas)
- **Analytics pages** - GraphQL queries + charts (data model is normalized)
- **Admin pages** - Simple forms (settings, users, integrations)
- **No complex business logic** - Just data display and forms

### ✅ What We Actually Need to Build

1. **Mapper functions** - GraphQL ↔ Bryntum format (straightforward mapping)
2. **GraphQL hooks** - Standard Apollo Client patterns
3. **Simple CRUD pages** - Standard React forms and tables
4. **Real-time subscriptions** - Standard Apollo subscriptions

**Total:** ~40-80 hours (1-2 weeks) vs original 120-160 hours (3-4 weeks)

---

## Component Structure

### Feature Modules

Each feature is self-contained:

```
src/features/scheduling/
├── components/
│   ├── ScheduleList.tsx
│   ├── ScheduleDetail.tsx
│   └── bryntum-calendar/
│       ├── SchedulerView.tsx
│       ├── LegendAndFiltering.tsx
│       └── ResourceHistogram.tsx
├── hooks/
│   ├── useSchedule.ts
│   ├── useSchedules.ts
│   └── useOptimization.ts
├── graphql/
│   ├── queries/
│   ├── mutations/
│   └── subscriptions/
├── lib/
│   └── mappers.ts
└── pages/
    └── SchedulingPage.tsx
```

### Shared Components

```
src/components/
├── ui/              # Base UI components (buttons, inputs, etc.)
├── layout/          # Layout components (header, sidebar, etc.)
├── feedback/        # Loading, error, empty states
└── forms/           # Form components
```

---

## GraphQL Integration Patterns

### Query Pattern

```typescript
// src/features/scheduling/hooks/useSchedule.ts
import { useQuery } from "@apollo/client";
import { GET_SCHEDULE } from "../graphql/queries/schedules.graphql";

export function useSchedule(scheduleId: string) {
  const { data, loading, error } = useQuery(GET_SCHEDULE, {
    variables: { id: scheduleId },
  });

  return {
    schedule: data?.schedule,
    loading,
    error,
  };
}
```

### Mutation Pattern

```typescript
// src/features/scheduling/hooks/useUpdateSchedule.ts
import { useMutation } from "@apollo/client";
import { UPDATE_SCHEDULE } from "../graphql/mutations/schedules.graphql";

export function useUpdateSchedule() {
  const [updateSchedule, { loading, error }] = useMutation(UPDATE_SCHEDULE, {
    // Optimistic update
    optimisticResponse: {
      updateSchedule: {
        __typename: "Schedule",
        id: "...",
        // ... optimistic data
      },
    },
    // Update cache after mutation
    update: (cache, { data }) => {
      // Update cache
    },
  });

  return { updateSchedule, loading, error };
}
```

### Subscription Pattern

```typescript
// src/features/scheduling/hooks/useOptimizationProgress.ts
import { useSubscription } from "@apollo/client";
import { OPTIMIZATION_PROGRESS } from "../graphql/subscriptions/optimization.graphql";

export function useOptimizationProgress(jobId: string) {
  const { data, loading } = useSubscription(OPTIMIZATION_PROGRESS, {
    variables: { jobId },
  });

  return {
    progress: data?.optimizationProgress,
    loading,
  };
}
```

---

## Migration Checklist

### Pre-Migration

- [x] Bryntum PRD and specifications complete ✅
- [x] Visual system defined ✅
- [x] Swedish localization complete ✅
- [ ] GraphQL schema available
- [ ] TypeScript types generated
- [ ] Mapper functions designed

### Migration

- [ ] Vite + React project created
- [ ] Apollo Client configured
- [ ] Bryntum components built from scratch (per BRYNTUM_FROM_SCRATCH_PRD.md)
- [ ] GraphQL queries/mutations created
- [ ] Mapper functions implemented (GraphQL ↔ Bryntum)
- [ ] Bryntum connected to GraphQL
- [ ] Simple CRUD pages built (resources, analytics, admin)
- [ ] Real-time subscriptions working
- [ ] All features tested

### Post-Migration

- [ ] All tests passing
- [ ] Performance benchmarks met
- [ ] Documentation complete
- [ ] Old frontend code removed

---

## Timeline Summary

| Phase       | Task                             | Time       | Status |
| ----------- | -------------------------------- | ---------- | ------ |
| **Phase 1** | Setup & Foundation               | 1-1.5 days | ⏸️     |
| **Phase 2** | GraphQL Integration (mappers)    | 2-2.5 days | ⏸️     |
| **Phase 3** | Pre-Planning Features            | 2.5-3 days | ⏸️     |
| **Phase 4** | Simple CRUD Pages                | 2.5-3 days | ⏸️     |
| **Phase 5** | Real-time & Polish               | 1.5-2 days | ⏸️     |
| **Total**   | **1.5-2.5 weeks (60-100 hours)** |            |        |

**With 2 developers:** Can be done in **1.5 weeks** (parallel work on CRUD pages and pre-planning)

---

## Best Practices

### 1. Type Safety

- ✅ Generate TypeScript types from GraphQL schema
- ✅ Use typed hooks (useQuery, useMutation)
- ✅ Type mapper functions
- ✅ No `any` types

### 2. Component Organization

- ✅ Feature-based folder structure
- ✅ Shared components in `components/`
- ✅ Custom hooks in `hooks/`
- ✅ One component per file

### 3. State Management

- ✅ Apollo Client cache for server state
- ✅ React Context for global UI state
- ✅ Local state for component-specific state
- ✅ Avoid prop drilling

### 4. Performance

- ✅ Code splitting per route
- ✅ Lazy load heavy components (Bryntum)
- ✅ Optimize GraphQL queries (only fetch needed fields)
- ✅ Use Apollo cache effectively

### 5. Error Handling

- ✅ Error boundaries for component errors
- ✅ GraphQL error handling in hooks
- ✅ User-friendly error messages
- ✅ Retry logic for failed requests

---

## Implementation Approach

**Building from Scratch:**

- Following `BRYNTUM_FROM_SCRATCH_PRD.md` specifications
- Phased implementation per `bryntum_timeplan.md` (14-19 days, 112-152 hours)
- Priority-based development (P0 → P1 → P2)
- Complete control over implementation
- Reference Bryntum examples from `bryntum-reference.md`

---

## Related Documents

- **Architecture:** `../01-architecture/architecture.md`
- **API Design:** `../02-api/API_DESIGN.md`
- **Mapper Specifications:** `../02-api/MAPPER_SPECIFICATIONS.md`
- **Bryntum PRD:** `../05-prd/bryntum_consultant_specs/BRYNTUM_FROM_SCRATCH_PRD.md`
- **Backend Spec:** `../05-prd/bryntum_consultant_specs/BRYNTUM_BACKEND_SPEC.md`
- **Pre-Planning Frontend:** `../09-scheduling/PREPLANNING_FRONTEND_IMPLEMENTATION.md`
- **Visual System:** `../05-prd/schedule-VISUAL_SYSTEM.md`

---

**Status:** ✅ Ready for implementation  
**Timeline:** 14-19 days (112-152 hours) for Bryntum integration per `bryntum_timeplan.md`  
**Next Steps:** Follow `BRYNTUM_FROM_SCRATCH_PRD.md` Phase 1 and `bryntum_timeplan.md` for phased implementation

---

## Summary: Implementation Timeline

### ✅ Building from Scratch

Following `BRYNTUM_FROM_SCRATCH_PRD.md` and `bryntum_timeplan.md`:

- **Phase 1 - Foundation:** 2-3 days (16-24 hours) - Core schedule viewing, integration setup
- **Phase 2 - Core Supply/Demand:** 4-5 days (32-40 hours) - Visit assignment, CRUD, optimization
- **Phase 3 - Enhanced Tools:** 3-4 days (24-32 hours) - Filtering, comparison, analytics
- **Phase 4 - Advanced Planning:** 3-4 days (24-32 hours) - Pre-planning, movable visits
- **Phase 5 - Polish:** 2-3 days (16-24 hours) - Export, testing, documentation

**Total: 14-19 days (112-152 hours) for complete Bryntum integration**

### ✅ Simple CRUD Pages

- **Resources pages:** Standard CRUD (employees, clients, service areas) - 8 hours
- **Analytics pages:** GraphQL queries + charts - 6 hours
- **Admin pages:** Simple forms - 6 hours

**Total: 20 hours (2.5 days) for all other pages**

### ✅ Total Frontend Refactoring: 14-19 days (112-152 hours) for Bryntum + 2.5 days (20 hours) for other pages
