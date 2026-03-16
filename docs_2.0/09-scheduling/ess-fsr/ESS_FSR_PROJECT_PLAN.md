# ESS + FSR Integration: Project Plan & Task Breakdown

> **Status:** PO Backlog for Engineering Scrum Team  
> **Created:** 2026-02-08  
> **Architecture:** See `ESS_FSR_DUAL_MODEL_ARCHITECTURE.md`  
> **Feature roadmap:** See `CAIRE_FEATURE_ROADMAP.md` (how each CAIRE feature is achieved with ESS/FSR)  
> **Advanced planning (Timefold guides):** See `SCHEDULING_ADVANCED_PLANNING_PRD.md` (US-1–US-5; Sprints 7 fill Night 31–35, Sprint 13 = Night 61–65, Sprint 14 = Night 66–70)  
> **Agent Workflow:** be-agent-service nightly engineering (one priority/night)  
> **Pilot:** Attendo (Huddinge) -- early pilot, not yet live

---

## Project Overview

Transform CAIRE from FSR-only to ESS+FSR dual-model scheduling. The planner says "schedule all visits" and CAIRE determines staffing, shifts, routes, costs, and compliance automatically.

**Timeline:** ~12 weeks (60 engineering nights)  
**Priority order:** Foundation first, then layer features. Each sprint delivers demoable value.

**US-6 (AI chat):** Cross-cutting UX. Build chat shell + action registry early (dedicated sprint or parallel track); then add **"Connect chat to [feature]"** tasks as US-1–US-5 ship, so every new feature is both button- and chat-accessible. See [implementation plan](../../plans/2026-02-25-ai-chat-schedule-integration.md) and PRD US-6.

---

## Sprint Structure

Each sprint = 7 engineering nights (Mon-Sun, includes weekends).  
Each night = 1 priority file → 1 PR.  
PO creates priority files in advance, reviews PRs each morning.

**Priority files:** `reports/ess-fsr/priorities-YYYY-MM-DD.md`  
**Base branch:** `feature/ess-fsr-integration` (PRs merge here, not main)  
**Workflow:** See `be-agent-service/docs/guides/ess-fsr-workflow.md`

---

## US-6 AI Chat (parallel track)

Optional sprint or parallel track for the AI chat shell. Full task breakdown: [implementation plan](../../plans/2026-02-25-ai-chat-schedule-integration.md). Summary:

| Night  | Task                                                                                                             |
| ------ | ---------------------------------------------------------------------------------------------------------------- |
| **X1** | Schedule chat context (type + provider), route-based context (scheduleId, solutionId, compare params).           |
| **X2** | Action registry (intent/handler map), wire to Bryntum refs/GraphQL where applicable.                             |
| **X3** | Bryntum AI chat panel (or placeholder) in SchedulerContainer; expose context to chat.                            |
| **X4** | Mount chat on all four schedule surfaces (ScheduleView, ScheduleDetailPage, SchedulesPage, ScheduleComparePage). |
| **X5** | Document "connect chat to [feature]" pattern; add placeholder tasks for Connect chat to US-1, US-3, etc.         |

### Connect chat to [feature] (when each ships)

| When this ships      | Task                                                                                                                                             |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| US-1 (Suggest times) | Connect chat to `visitTimeWindowRecommendations`: register action "suggest times for this visit"; chat passes visitId from context or selection. |
| US-3 (Disruption)    | Connect chat to `handleDisruption`, `optimizeStrategy`, `compareSolutions`: register "Anna is sick", "run add backup", "compare solutions".      |
| US-4 (Freeze)        | Connect chat to from-patch with `freezeBeforeTime`: register "freeze next hour", "replan but freeze next 60 minutes".                            |
| US-5 (What-if)       | Connect chat to what-if flow: register "what if we add 3 employees", open what-if modal or create branches and route to compare.                 |
| US-2 (Multi-area)    | Connect chat to schedule creation and compare: "create schedule for area X and Y", "compare single vs multi-area".                               |

---

## Sprint 1: ESS API Foundation (Week 1)

**Goal:** Connect to Timefold ESS API. Prove we can send employees and shifts and get assignments back.

### Night 1: ESS Type Definitions

```markdown
# Priority 1

**Description:** Create TypeScript type definitions for Timefold Employee Shift Scheduling API.
Define all ESS input/output types: employees, shifts, contracts, globalRules, skills, availability,
costGroups, demandDetails, and ESS response format (shift assignments, KPIs, metrics).

**Expected outcome:**

- New file: apps/dashboard-server/src/services/timefold/ess.types.ts
- All ESS API types defined matching Timefold OpenAPI spec
- Types exported for use by mapper and client
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/timefold/types.ts (existing FSR types for reference)
- apps/dashboard-server/src/services/timefold/ess.types.ts (new)

**Dependencies:** None

**Complexity:** Medium
```

### Night 2: ESS API Client

```markdown
# Priority 1

**Description:** Create ESS HTTP client following same pattern as existing TimefoldClient.ts.
Support fullSolve, getStatus, getSolution, and recommendations endpoints for the Employee
Shift Scheduling model at /api/models/employee-scheduling/v1/.

**Expected outcome:**

- New file: apps/dashboard-server/src/services/timefold/ESSClient.ts
- Methods: solve(), getStatus(), getSolution(), getRecommendations()
- Uses same API key and error handling as existing TimefoldClient
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/timefold/TimefoldClient.ts (existing, use as pattern)
- apps/dashboard-server/src/services/timefold/ESSClient.ts (new)
- apps/dashboard-server/src/services/timefold/ess.types.ts (from night 1)

**Dependencies:** Night 1 (ess.types.ts)

**Complexity:** Medium
```

### Night 3: Swedish Labor Law Contract Config

```markdown
# Priority 1

**Description:** Create Swedish labor law configuration as ESS contract definitions.
Implement kollektivavtal rules: max 40h/week (preferred), max 48h/week (hard),
11h daily rest, max 5 consecutive days, break requirements. Support full-time and
part-time (75%) contract templates. Store as organization-level configuration.

**Expected outcome:**

- New file: apps/dashboard-server/src/services/bridge/scheduling/swedish-labor-contracts.ts
- Function: getSwedishLaborContracts(contractType: 'fullTime' | 'partTime75')
- Returns ESS-formatted contract with periodRules, minutesBetweenShiftsRules,
  consecutiveDaysWorkedRules, rollingWindowRules
- Unit test with expected contract output
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/scheduling/swedish-labor-contracts.ts (new)
- apps/dashboard-server/src/services/timefold/ess.types.ts (contract types)

**Dependencies:** Night 1

**Complexity:** Medium
```

### Night 4: Employee-to-ESS Mapper

```markdown
# Priority 1

**Description:** Create mapper that transforms CAIRE Employee database records into
Timefold ESS employee format. Map: employee.id, skills, contractType to ESS contracts,
home location (latitude/longitude), availability from ScheduleEmployee shifts,
costGroup (fixed-contract vs hourly-staff based on employee.contractType).

**Expected outcome:**

- New file: apps/dashboard-server/src/services/bridge/mappers/db-to-ess.mapper.ts
- Function: mapEmployeesToESS(employees: Employee[]): ESSEmployee[]
- Maps skills, location, contracts, availability, cost groups
- Handles both fixed-contract and hourly employees
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/mappers/db-to-timefold.mapper.ts (existing FSR mapper pattern)
- apps/dashboard-server/src/services/bridge/mappers/db-to-ess.mapper.ts (new)
- apps/dashboard-server/src/services/bridge/scheduling/swedish-labor-contracts.ts (from night 3)

**Dependencies:** Night 1, Night 3

**Complexity:** Medium
```

### Night 5: Demand Curve Generator (Service Hours)

```markdown
# Priority 1

**Description:** Create demand curve generator that aggregates CAIRE visits into ESS
hourly demand format (minimumMaximumShiftsPerHourlyDemand). For each hour slot, count
concurrent visits and calculate employees needed. This is SERVICE HOURS ONLY -- travel
overhead will be added in Sprint 2.

**Expected outcome:**

- New file: apps/dashboard-server/src/services/bridge/scheduling/demand-curve.service.ts
- Function: generateDemandCurve(visits: Visit[], overheadMultiplier: number): ESSDemandDetails[]
- Aggregates visits per hour slot (07:00-08:00, 08:00-09:00, etc.)
- Calculates concurrent employees needed per slot
- Applies overhead multiplier to inflate for travel
- Returns ESS minimumMaximumShiftsPerHourlyDemand format
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/scheduling/demand-curve.service.ts (new)
- apps/dashboard-server/src/services/timefold/ess.types.ts (demand types)

**Dependencies:** Night 1

**Complexity:** Medium
```

---

## Sprint 2: ESS-to-FSR Bridge (Week 2)

**Goal:** Connect ESS output to FSR input. Complete the basic loop: ESS assigns shifts, FSR routes visits.

### Night 6: ESS Output to FSR Vehicle Mapper

```markdown
# Priority 1

**Description:** Create bridge mapper that transforms ESS shift assignment output into FSR
vehicle input format. Each ESS shift assignment (employee + start/end time) becomes an FSR
vehicle with shift, enriched with employee home location (for startLocation/endLocation),
skills, and break configuration.

**Expected outcome:**

- New file: apps/dashboard-server/src/services/bridge/mappers/ess-to-fsr-bridge.ts
- Function: mapESSShiftsToFSRVehicles(essResult, employees): TimefoldVehicle[]
- Enriches ESS shifts with employee home location, skills, breaks
- Uses existing FSR vehicle format (compatible with TimefoldClient)
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/mappers/ess-to-fsr-bridge.ts (new)
- apps/dashboard-server/src/services/bridge/mappers/db-to-timefold.mapper.ts (FSR format reference)
- apps/dashboard-server/src/services/timefold/ess.types.ts (ESS output types)

**Dependencies:** Sprint 1

**Complexity:** Medium
```

### Night 7: Geographic Travel Bootstrap

```markdown
# Priority 1

**Description:** Create bootstrap service that estimates travel overhead from client GPS
coordinates when no historical data exists. Calculate average inter-client distance in
service area, apply urban speed model (25-35 km/h for Swedish municipalities), estimate
travel per visit, and return overhead multiplier. User never configures this -- it's
automatic.

**Expected outcome:**

- New file: apps/dashboard-server/src/services/bridge/scheduling/travel-bootstrap.service.ts
- Function: bootstrapTravelOverhead(visits: Visit[]): number (returns multiplier like 1.25)
- Calculates average inter-client distance using Haversine formula
- Applies speed model based on distance spread (dense urban vs suburban)
- Returns overhead multiplier (typically 1.2-1.4)
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/scheduling/travel-bootstrap.service.ts (new)

**Dependencies:** None

**Complexity:** Medium
```

### Night 8: Basic Two-Phase Orchestrator

```markdown
# Priority 1

**Description:** Create the core two-phase optimization orchestrator that runs ESS then FSR
sequentially. Phase 1: Generate demand curve, run ESS to get shift assignments. Phase 2:
Map ESS shifts to FSR vehicles, run FSR to get routes. No convergence loop yet -- just
the basic sequence. Return combined result.

**Expected outcome:**

- New file: apps/dashboard-server/src/services/bridge/optimization/two-phase-optimization.service.ts
- Function: runTwoPhaseOptimization(scheduleId, options): TwoPhaseResult
- Fetches schedule data (visits, employees)
- Phase 1: demand curve → ESS → shift assignments
- Phase 2: ESS shifts → FSR vehicles → FSR → routes
- Returns combined ESS+FSR result
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/optimization/two-phase-optimization.service.ts (new)
- apps/dashboard-server/src/services/bridge/optimization/timefold.service.ts (existing, for FSR)
- apps/dashboard-server/src/services/timefold/ESSClient.ts (from night 2)

**Dependencies:** Sprint 1 complete, Night 6, Night 7

**Complexity:** High
```

### Night 9: Convergence Check Service

```markdown
# Priority 1

**Description:** Create convergence check service that compares FSR actual travel with the
estimated overhead. If visits are unassigned or efficiency diverges too far, signal that
another iteration is needed. Max 3 iterations. Store the learned overhead multiplier per
service area for future use.

**Expected outcome:**

- New file: apps/dashboard-server/src/services/bridge/scheduling/convergence-check.service.ts
- Function: checkConvergence(fsrResult, estimatedOverhead): ConvergenceResult
- Calculates actual efficiency from FSR KPIs (service time / shift time)
- Checks unassigned visits count
- Returns { converged: boolean, adjustedOverhead: number, iteration: number }
- Uses damping factor (0.7 actual + 0.3 previous) to prevent oscillation
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/scheduling/convergence-check.service.ts (new)

**Dependencies:** Night 8

**Complexity:** Medium
```

### Night 10: Iterative Orchestrator (Complete Loop)

```markdown
# Priority 1

**Description:** Upgrade the two-phase orchestrator to support iterative convergence.
After FSR result, run convergence check. If not converged and iteration < 3, adjust
overhead and re-run ESS then FSR. Store final overhead as learned profile. This makes
the system self-improving over time.

**Expected outcome:**

- Updated: apps/dashboard-server/src/services/bridge/optimization/two-phase-optimization.service.ts
- Adds iteration loop with convergence check
- Stores learned travel profile after convergence
- Progress callback for UI (iteration N of 3, optimizing...)
- Max 3 iterations with proper logging
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/optimization/two-phase-optimization.service.ts (update)
- apps/dashboard-server/src/services/bridge/scheduling/convergence-check.service.ts (from night 9)

**Dependencies:** Night 8, Night 9

**Complexity:** High
```

---

## Sprint 3: Database & GraphQL (Week 3)

**Goal:** Database schema for travel profiles and combined metrics. GraphQL API for two-phase optimization.

### Night 11: Travel Profile Schema

```markdown
# Priority 1

**Description:** Add TravelProfile and OptimizationMetrics models to Prisma schema.
TravelProfile stores learned travel overhead per service area per hour slot.
OptimizationMetrics stores combined ESS+FSR metrics per solution.

**Expected outcome:**

- Updated: apps/dashboard-server/schema.prisma
- New model: TravelProfile (serviceAreaId, hourSlot, overheadMultiplier, sampleCount, updatedAt)
- New model: OptimizationMetrics (scheduleId, solutionId, essDatasetId, fsrDatasetId,
  activatedEmployees, fixedEmployees, hourlyEmployees, totalShiftCostSek, fairnessPercentage,
  totalTravelMinutes, assignedVisits, trueEfficiency, costPerVisit, continuityScore,
  iterations, converged, travelOverheadLearned)
- Migration created: add_ess_fsr_metrics
- Type-check passes

**Files:**

- apps/dashboard-server/schema.prisma

**Dependencies:** None

**Complexity:** Medium
```

### Night 12: GraphQL Schema for Two-Phase Optimization

```markdown
# Priority 1

**Description:** Add GraphQL types and mutations for two-phase ESS+FSR optimization.
Add TwoPhaseOptimizationResult type with ESS metrics, FSR metrics, combined metrics,
and convergence info. Add startTwoPhaseOptimization mutation.

**Expected outcome:**

- Updated: packages/graphql/schema/dashboard/types.graphql (add TwoPhaseResult types)
- Updated: packages/graphql/schema/dashboard/mutations.graphql (add mutation)
- Run codegen: yarn workspace @appcaire/graphql codegen
- Type-check passes

**Files:**

- packages/graphql/schema/dashboard/types.graphql
- packages/graphql/schema/dashboard/mutations.graphql

**Dependencies:** Night 11

**Complexity:** Medium
```

### Night 13: Two-Phase Optimization Resolver

```markdown
# Priority 1

**Description:** Create GraphQL resolver for startTwoPhaseOptimization mutation.
Calls the iterative orchestrator service, stores results in OptimizationMetrics table,
returns combined ESS+FSR result to frontend.

**Expected outcome:**

- New resolver: apps/dashboard-server/src/graphql/resolvers/schedule/mutations/startTwoPhaseOptimization.ts
- Calls two-phase-optimization.service.ts
- Stores OptimizationMetrics after completion
- Returns TwoPhaseOptimizationResult to client
- Handles errors gracefully
- Type-check passes

**Files:**

- apps/dashboard-server/src/graphql/resolvers/schedule/mutations/startTwoPhaseOptimization.ts (new)
- apps/dashboard-server/src/graphql/resolvers/schedule/index.ts (add to exports)

**Dependencies:** Night 12, Sprint 2

**Complexity:** Medium
```

### Night 14: Travel Profile CRUD Resolver

```markdown
# Priority 1

**Description:** Create GraphQL query for travel profiles per service area. The planner
doesn't configure these (they're automatic), but managers can view them to understand
how CAIRE learned travel patterns.

**Expected outcome:**

- New query: travelProfiles(serviceAreaId: ID!) returning TravelProfile[]
- New resolver in apps/dashboard-server/src/graphql/resolvers/analytics/
- Returns learned overhead multipliers per hour slot
- Type-check passes

**Files:**

- apps/dashboard-server/src/graphql/resolvers/analytics/queries/travelProfiles.ts (new)
- packages/graphql/schema/dashboard/queries.graphql (add query)

**Dependencies:** Night 11, Night 12

**Complexity:** Low
```

### Night 15: Optimization Metrics Query

```markdown
# Priority 1

**Description:** Create GraphQL query for combined optimization metrics. Return both
ESS and FSR metrics for a solution, plus combined KPIs (true efficiency, cost per visit,
continuity score). Used by dashboard metrics panels.

**Expected outcome:**

- New query: optimizationMetrics(solutionId: ID!) returning OptimizationMetrics
- Resolver in apps/dashboard-server/src/graphql/resolvers/analytics/
- Returns ESS metrics (staffing, cost, fairness) + FSR metrics (travel, utilization) + combined
- Type-check passes

**Files:**

- apps/dashboard-server/src/graphql/resolvers/analytics/queries/optimizationMetrics.ts (new)
- packages/graphql/schema/dashboard/queries.graphql (add query)

**Dependencies:** Night 11, Night 12

**Complexity:** Low
```

---

## Sprint 4: Cost Optimization & Employee Activation (Week 4)

**Goal:** Fixed vs hourly staffing model. Cost management integration.

### Night 16: Employee Cost Group Configuration

```markdown
# Priority 1

**Description:** Add cost group configuration to Organization settings. Store fixed-contract
vs hourly-staff cost groups with activation costs and ratio weights. Map to ESS
employeeCostGroups format.

**Expected outcome:**

- Updated schema: add costGroup field to Employee model (FIXED_CONTRACT, HOURLY_STAFF)
- New service function: getOrganizationCostGroups(organizationId)
- Returns ESS employeeCostGroups with activation costs and ratio weights
- Default: fixed activationCost=0, hourly activationCost=500, ratio 4:1
- Type-check passes

**Files:**

- apps/dashboard-server/schema.prisma (add costGroup to Employee)
- apps/dashboard-server/src/services/bridge/scheduling/cost-groups.service.ts (new)

**Dependencies:** Sprint 1

**Complexity:** Medium
```

### Night 17: Cost Definitions for Contracts

```markdown
# Priority 1

**Description:** Add hourly cost definitions to Swedish labor contracts. Fixed-contract:
220 SEK/h base, 330 SEK/h overtime (after 8h/day). Hourly-staff: 280 SEK/h flat.
Integrate with ESS contract costDefinition format.

**Expected outcome:**

- Updated: apps/dashboard-server/src/services/bridge/scheduling/swedish-labor-contracts.ts
- Add costDefinition to contract periodRules
- Support overtime tiers (base + overtime1 + overtime2)
- Configurable per organization (store in Organization settings)
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/scheduling/swedish-labor-contracts.ts (update)

**Dependencies:** Night 3, Night 16

**Complexity:** Medium
```

### Night 18: Integrate Cost Groups into ESS Mapper

```markdown
# Priority 1

**Description:** Update the Employee-to-ESS mapper to include cost group assignments
and the ESS global cost rules. Fixed employees get lower activation cost, hourly get
higher. ESS will naturally prefer fixed staff.

**Expected outcome:**

- Updated: apps/dashboard-server/src/services/bridge/mappers/db-to-ess.mapper.ts
- Includes employeeCostGroups in ESS input
- Maps employee.costGroup to ESS costGroup
- Adds minimize-activated-employees and maximize-saturation constraints
- Adds activation ratio weight (4:1 fixed:hourly)
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/mappers/db-to-ess.mapper.ts (update)
- apps/dashboard-server/src/services/bridge/scheduling/cost-groups.service.ts

**Dependencies:** Night 4, Night 16, Night 17

**Complexity:** Medium
```

### Night 19-20: Cost Dashboard UI (2 nights)

```markdown
# Priority 1

**Description:** Add cost analysis panel to ScheduleDetailPage showing ESS cost metrics:
fixed vs hourly employee breakdown, activation costs, overtime costs, total shift cost,
and cost per visit. Uses optimizationMetrics query.

**Expected outcome:**

- New component: apps/dashboard/src/components/Schedule/CostAnalysisPanel.tsx
- Shows: fixed/hourly employee count, activation cost, overtime hours, total cost/visit
- Bar chart (Recharts): cost breakdown by category
- Trend chart: cost per visit over time
- Uses useOptimizationMetricsQuery from @appcaire/graphql
- Type-check passes

**Files:**

- apps/dashboard/src/components/Schedule/CostAnalysisPanel.tsx (new)
- apps/dashboard/src/pages/ScheduleDetailPage.tsx (add panel)
- packages/graphql/operations/queries/dashboard/optimizationMetrics.graphql (new)

**Dependencies:** Night 15 (metrics query)

**Complexity:** Medium
```

---

## Sprint 5: Continuity & Skills Sync (Week 5)

### Night 21: Employee-Client Affinity Tracker

```markdown
# Priority 1

**Description:** Create service that tracks employee-client visit history and builds an
affinity matrix. After each FSR solution, record which employees visited which clients.
Use this to generate preferredVehicles for FSR and preferredEmployees for ESS in future runs.

**Expected outcome:**

- New model in schema: EmployeeClientAffinity (employeeId, clientId, visitCount, lastVisitDate)
- New service: apps/dashboard-server/src/services/bridge/scheduling/continuity-tracker.service.ts
- Function: recordAffinities(fsrSolution) -- stores visit patterns
- Function: getPreferredEmployees(clientId, maxCount) -- returns top N employees for client
- Migration created
- Type-check passes

**Files:**

- apps/dashboard-server/schema.prisma (add EmployeeClientAffinity)
- apps/dashboard-server/src/services/bridge/scheduling/continuity-tracker.service.ts (new)

**Dependencies:** None

**Complexity:** Medium
```

### Night 22: Continuity Integration into ESS-FSR Loop

```markdown
# Priority 1

**Description:** Integrate continuity tracker into the iterative optimization loop. Before
FSR runs, inject preferredVehicles from affinity data. After FSR runs, update affinity
records. Calculate continuity score (unique caregivers per client per 14 days).

**Expected outcome:**

- Updated: two-phase-optimization.service.ts
- Before FSR: adds preferredVehicles to visits from affinity data
- After FSR: calls continuityTracker.recordAffinities()
- Calculates continuityScore and stores in OptimizationMetrics
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/optimization/two-phase-optimization.service.ts (update)
- apps/dashboard-server/src/services/bridge/scheduling/continuity-tracker.service.ts

**Dependencies:** Night 21, Night 10

**Complexity:** Medium
```

### Night 23: Skill Aggregation for ESS Demand

```markdown
# Priority 1

**Description:** Enhance demand curve generator to aggregate visit skill requirements
per hour slot. When generating ESS shifts from demand, include requiredSkills and
preferredSkills based on the visits in that time slot. Ensures ESS assigns employees
with matching skills.

**Expected outcome:**

- Updated: demand-curve.service.ts
- Aggregates requiredSkills per hour slot (most common skills become shift requirements)
- Tags shifts with service area for ESS concurrent shift rules
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/scheduling/demand-curve.service.ts (update)

**Dependencies:** Night 5

**Complexity:** Medium
```

### Night 24: Pin State Synchronization

```markdown
# Priority 1

**Description:** Create pin synchronization service that keeps ESS shift pins and FSR
visit pins consistent. When an ESS shift is pinned to an employee, all FSR visits within
that shift's time window must be pinned to the same vehicle. When a visit is unpinned,
the containing shift should be unpinned.

**Expected outcome:**

- New service: apps/dashboard-server/src/services/bridge/scheduling/pin-sync.service.ts
- Function: syncPinState(essShifts, fsrVisits): PinSyncResult
- Ensures consistency between ESS and FSR pin states
- Handles partial unpinning (disruption scenario)
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/scheduling/pin-sync.service.ts (new)

**Dependencies:** Sprint 2

**Complexity:** Medium
```

### Night 25: Continuity Dashboard Panel

```markdown
# Priority 1

**Description:** Add continuity analysis panel showing unique caregivers per client,
preferred caregiver match rate, and continuity trends. Target: < 10-15 different
caregivers per client per 14 days.

**Expected outcome:**

- New component: apps/dashboard/src/components/Schedule/ContinuityPanel.tsx
- Shows: avg unique caregivers/client, worst-case clients, preferred match rate
- Table: clients sorted by caregiver diversity (highest first = worst continuity)
- Uses data from optimizationMetrics + employeeClientAffinity
- Type-check passes

**Files:**

- apps/dashboard/src/components/Schedule/ContinuityPanel.tsx (new)
- apps/dashboard/src/pages/ScheduleDetailPage.tsx (add panel)
- packages/graphql/operations/queries/dashboard/ (new query if needed)

**Dependencies:** Night 22

**Complexity:** Medium
```

---

## Sprint 6-7: Recommendations & Real-Time (Week 6-7)

### Night 26: ESS Recommendation Integration

```markdown
# Priority 1

**Description:** Create service that calls ESS Recommendations API when an employee
calls in sick. Returns ranked list of replacement employees with justifications.
Integrates with existing disruption handling workflow.

**Expected outcome:**

- New service: apps/dashboard-server/src/services/bridge/scheduling/ess-recommendations.service.ts
- Function: getShiftRecommendations(shiftId, employees): ESSRecommendation[]
- Calls ESS /recommendations/recommend-employees endpoint
- Returns ranked employees with score diffs and constraint justifications
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/scheduling/ess-recommendations.service.ts (new)
- apps/dashboard-server/src/services/timefold/ESSClient.ts (add recommendations method)

**Dependencies:** Night 2

**Complexity:** Medium
```

### Night 27: Two-Level Recommendation Workflow

```markdown
# Priority 1

**Description:** Create combined recommendation workflow: ESS recommends shift replacement,
then FSR recommends visit redistribution. Planner sees both in one view. Implements the
disruption response flow from SCHEDULE_SOLUTION_ARCHITECTURE.md.

**Expected outcome:**

- New service: apps/dashboard-server/src/services/bridge/scheduling/disruption-handler.service.ts
- Function: handleEmployeeSick(employeeId, scheduleId): DisruptionResponse
- Step 1: ESS recommendation for shift coverage
- Step 2: FSR re-optimization with selected replacement
- Returns combined recommendation with before/after metrics
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/scheduling/disruption-handler.service.ts (new)

**Dependencies:** Night 26, Night 10

**Complexity:** High
```

### Night 28: GraphQL Mutations for Disruption Handling

```markdown
# Priority 1

**Description:** Add GraphQL mutations for the disruption handling workflow.
getShiftRecommendations query returns ranked replacements.
applyDisruptionResponse mutation applies selected recommendation.

**Expected outcome:**

- New query: getShiftRecommendations(scheduleId, employeeId) in GraphQL schema
- New mutation: applyDisruptionResponse(scheduleId, recommendationId)
- GraphQL operation files created
- Codegen run
- Type-check passes

**Files:**

- packages/graphql/schema/dashboard/queries.graphql (add query)
- packages/graphql/schema/dashboard/mutations.graphql (add mutation)
- packages/graphql/schema/dashboard/types.graphql (add types)
- apps/dashboard-server/src/graphql/resolvers/schedule/queries/getShiftRecommendations.ts (new)
- apps/dashboard-server/src/graphql/resolvers/schedule/mutations/applyDisruptionResponse.ts (new)

**Dependencies:** Night 27

**Complexity:** Medium
```

### Night 29-30: Disruption UI Panel (2 nights)

Reserve for Bryntum disruption alert panel and recommendation selector UI.

### Night 31: FSR Time-Window Recommendation Client

```markdown
# Priority 1

**Description:** Add FSR visit time-window recommendations to TimefoldClient. When visits
are unassigned (pre-plan or post-disruption), planners need feasible time windows to
offer clients. Implement getVisitTimeWindowRecommendations(datasetId, fitVisitId,
timeWindows) calling Timefold FSR recommendations endpoint. Add request/response types
in types.ts. Unit test with mocked fetch; request shape must match Timefold docs.

**Expected outcome:**

- Updated: apps/dashboard-server/src/services/timefold/TimefoldClient.ts (add method)
- Updated: apps/dashboard-server/src/services/timefold/types.ts (recommendation types)
- Unit test: request/response shape and error handling
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/timefold/TimefoldClient.ts
- apps/dashboard-server/src/services/timefold/types.ts

**Dependencies:** FSR client (Sprint 1-2)

**Reference:** SCHEDULING_ADVANCED_PLANNING_PRD.md US-1

**Complexity:** Medium
```

### Night 32: Time-Window Recommendation GraphQL + Bridge

```markdown
# Priority 1

**Description:** Expose visit time-window recommendations via GraphQL. New query
visitTimeWindowRecommendations(scheduleId, solutionId, visitId, timeWindows). Resolver
builds minimal FSR modelInput from schedule (and optional solution), calls
TimefoldClient.getVisitTimeWindowRecommendations, maps response to GraphQL types.
Support both unsolved and solved dataset contexts.

**Expected outcome:**

- New query in packages/graphql/schema/dashboard/queries.graphql
- New resolver: apps/dashboard-server/src/graphql/resolvers/schedule/queries/visitTimeWindowRecommendations.ts
- Resolver enforces organization access (Clerk + organizationId) per dashboard rules
- Bridge/service builds modelInput from prepareScheduleData or equivalent (from schedule/FSR input pipeline, e.g. Night 8)
- Integration test with mock Timefold response
- Add operation file packages/graphql/operations/queries/dashboard/visitTimeWindowRecommendations.graphql; run codegen
- Type-check passes

**Files:**

- packages/graphql/schema/dashboard/queries.graphql
- packages/graphql/schema/dashboard/types.graphql (response type)
- apps/dashboard-server/src/graphql/resolvers/schedule/queries/visitTimeWindowRecommendations.ts

**Dependencies:** Night 31; FSR modelInput builder (e.g. prepareScheduleData / schedule data pipeline from Night 8 or equivalent)

**Reference:** SCHEDULING_ADVANCED_PLANNING_PRD.md US-1

**Complexity:** Medium
```

### Night 33: Freeze Horizon in From-Patch

```markdown
# Priority 1

**Description:** Extend createSolutionFromPatch (or the service that builds the
from-patch payload) to accept optional freezeBeforeTime: DateTime. For each
assignment in the current solution, if assignedStartTime < freezeBeforeTime, add that
visit to the pinned set so the solver does not move it. Enables real-time replanning
without rerouting technicians already en route.

**Expected outcome:**

- Updated: createSolutionFromPatch input type (optional freezeBeforeTime)
- From-patch payload builder includes pinned set derived from freeze horizon
- Test: from-patch with freezeBeforeTime → pinned set contains only early assignments
- Type-check passes

**Files:**

- apps/dashboard-server/src/graphql/resolvers/solution/mutations/createSolutionFromPatch.ts
- apps/dashboard-server/src/services/bridge/optimization/ (payload builder)

**Dependencies:** createSolutionFromPatch and from-patch payload builder (pre-existing; verify before Sprint 7). If not yet implemented, add a prior night for the mutation and payload builder.

**Reference:** SCHEDULING_ADVANCED_PLANNING_PRD.md US-4

**Complexity:** Medium
```

### Night 34: Impact Analysis in Disruption Handler

```markdown
# Priority 1

**Description:** Extend disruption-handler.service.ts (from Night 27) to return
affectedVisits when an employee is marked unavailable: visitId, clientId,
currentAssignment, optional slaRisk. Also return strategy branches as designed in
SCHEDULE_SOLUTION_ARCHITECTURE (Add backup, Defer visits, Reduce duration, Hybrid).
Enables UI to show "What does this mean?" before the planner chooses a strategy.

**Expected outcome:**

- Updated: apps/dashboard-server/src/services/bridge/scheduling/disruption-handler.service.ts
- handleEmployeeSick (or equivalent) returns { affectedVisits, strategies }
- Strategy branches have id, name, description, optional estimatedImpact
- Unit or integration test: sick employee → non-empty affectedVisits and strategies
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/scheduling/disruption-handler.service.ts

**Dependencies:** Night 27

**Reference:** SCHEDULING_ADVANCED_PLANNING_PRD.md US-3

**Complexity:** Medium
```

### Night 35: Unassigned Visit Recommendations UI

```markdown
# Priority 1

**Description:** Bryntum/dashboard: from the unassigned visit list, add "Suggest times"
(or equivalent) action. On click, call visitTimeWindowRecommendations query with
schedule/solution context and the selected visit; display returned time windows.
Planner can pick one; optionally update visit time window and trigger re-solve or
from-patch. Implements US-1 UI.

**Expected outcome:**

- New or updated component: unassigned visit list with "Suggest times" button
- Calls useVisitTimeWindowRecommendationsQuery (or equivalent) from @appcaire/graphql
- Displays slots; selection updates visit or triggers optimization
- Manual test: unassigned visit → Suggest times → see slots → select one
- Type-check passes

**Files:**

- apps/dashboard/src/components/Schedule/ (unassigned visit panel or list)
- packages/graphql/operations/queries/dashboard/visitTimeWindowRecommendations.graphql (create and run codegen)

**Dependencies:** Night 32

**Reference:** SCHEDULING_ADVANCED_PLANNING_PRD.md US-1

**Complexity:** Medium
```

---

## Sprint 8-9: Explainability & Mobile (Week 8-9)

### Night 36-40: Score Analysis & Justifications

- Night 36: GraphQL query for ESS+FSR score analysis per solution
- Night 37: "Why this schedule?" data service (combine ESS+FSR justifications)
- Night 38: Mobile API endpoint for caregiver schedule explanations
- Night 39: Gamification metrics service (on-time rate, continuity, skill use)
- Night 40: GraphQL subscription for schedule change notifications

### Night 41-45: Mobile Caregiver Enhancements

- Night 41: ESS-aware shift view in mobile app (shows shift fairness, hours worked)
- Night 42: "Why me?" button with ESS constraint justifications
- Night 43: Gamification badges from ESS metrics (punctuality, continuity, skills)
- Night 44: Navigation integration with FSR waypoints
- Night 45: Schedule change push notifications with explanation text

---

## Sprint 10-12: Management Analytics & Polish (Week 10-12)

### Night 46-50: Management Dashboard

- Night 46: Combined ESS+FSR efficiency dashboard (true efficiency metric)
- Night 47: Staffing analysis (over/under staffed hours, skill gaps)
- Night 48: Cost trend analysis (fixed vs hourly, overtime trends)
- Night 49: Comparison view (manual slinga vs CAIRE-generated with ESS+FSR metrics)
- Night 50: Export combined metrics to BI (analytics warehouse integration)

### Night 51-55: Integration & Testing

- Night 51: End-to-end test with Attendo Huddinge data (45 visits, 10 employees)
- Night 52: Performance benchmarking (convergence time, iteration count)
- Night 53: Learned profile accuracy validation (compare predicted vs actual overhead)
- Night 54: Swedish labor law compliance verification
- Night 55: Cost optimization validation (fixed/hourly ratio, activation costs)

### Night 56-60: Documentation & Polish

- Night 56: Update CLAUDE.md with ESS+FSR learnings
- Night 57: Update scheduling platform docs (scheduling.html, scheduling-with-slingor.html)
- Night 58: API documentation for two-phase optimization
- Night 59: Onboarding guide for ESS+FSR configuration per organization
- Night 60: Architecture review and technical debt cleanup

---

## Sprint 13: Strategy Comparison (Night 61-65)

**Goal:** Implement handleDisruption → strategy branches → optimizeStrategy → compareSolutions → Select / Fine-tune / Publish flow. Supports US-3 (disruption strategy comparison) and US-5 (what-if without disruption).

**Reference:** [SCHEDULING_ADVANCED_PLANNING_PRD.md](../../05-prd/SCHEDULING_ADVANCED_PLANNING_PRD.md) US-3, US-5; [SCHEDULE_SOLUTION_ARCHITECTURE.md](../SCHEDULE_SOLUTION_ARCHITECTURE.md)

### Night 61: optimizeStrategy Mutation

```markdown
# Priority 1

**Description:** Implement optimizeStrategy mutation. Given scheduleId and strategy config
(supply/demand adjustments from SCHEDULE_SOLUTION_ARCHITECTURE), apply adjustments
(add employee, defer visits, reduce duration, or hybrid) and call fullSolve or
fromPatch. Persist solution with metadata: supplySnapshot, demandSnapshot,
patchOperations. Enables per-branch optimization for strategy comparison.

**Expected outcome:**

- New mutation: optimizeStrategy(scheduleId!, strategyId!, options) in GraphQL schema
- Resolver applies strategy adjustments, calls orchestration layer (e.g. two-phase-optimization.service or from-patch flow from Night 10), stores solution with metadata
- Resolver enforces organization access (Clerk + organizationId) per dashboard rules
- Solution metadata (supplySnapshot, demandSnapshot, patchOperations) stored; schema supports it (see SCHEDULE_SOLUTION_ARCHITECTURE; add migration if needed)
- Add GraphQL operation file in packages/graphql/operations; run yarn workspace @appcaire/graphql codegen
- Integration test: handleDisruption → optimizeStrategy for one branch → solution exists
- Type-check passes

**Files:**

- packages/graphql/schema/dashboard/mutations.graphql
- apps/dashboard-server/src/graphql/resolvers/schedule/mutations/optimizeStrategy.ts (new)

**Dependencies:** Night 10 (orchestrator / from-patch), Night 27, Night 34

**Reference:** SCHEDULING_ADVANCED_PLANNING_PRD.md US-3

**Complexity:** High
```

### Night 62: compareSolutions Query

```markdown
# Priority 1

**Description:** Implement compareSolutions query. Input: solutionIds + baselineId. Load
solutions, normalize metrics (per-visit travel, assignment rate, utilization, cost,
deferred count). Return baseline + variants + deltas + simple scoring recommendation
(e.g. by weighted score). Used by Compare Panel UI.

**Expected outcome:**

- New query: compareSolutions(solutionIds!, baselineId!) in GraphQL schema
- Resolver enforces organization access per dashboard rules
- Resolver loads solutions, computes normalized metrics and deltas, returns recommendation
- Add GraphQL operation file; run codegen
- Test: 2-3 solutions → deltas and recommendation consistent
- Type-check passes

**Files:**

- packages/graphql/schema/dashboard/queries.graphql
- apps/dashboard-server/src/graphql/resolvers/solution/queries/compareSolutions.ts (new)

**Dependencies:** Solutions with metrics exist

**Reference:** SCHEDULING_ADVANCED_PLANNING_PRD.md US-3

**Complexity:** Medium
```

### Night 63: Disruption Panel UI

```markdown
# Priority 1

**Description:** Bryntum component: when disruption is detected (e.g. employee marked
sick), show disruption panel with affected visits list and strategy cards (Add backup,
Defer visits, Reduce duration, Hybrid). Each card has "Optimize" button; or "Optimize
All". Uses handleDisruption (for affected visits + strategies) and optimizeStrategy
(per card). Implements US-3 UI part 1.

**Expected outcome:**

- New component: DisruptionPanel or equivalent in apps/dashboard
- Displays affected visits (from handleDisruption), strategy cards, Optimize actions
- Calls getShiftRecommendations / handleDisruption and optimizeStrategy
- Manual test: mark employee sick → panel shows affected visits and strategies → Optimize
- Type-check passes

**Files:**

- apps/dashboard/src/components/Schedule/DisruptionPanel.tsx (or similar)

**Dependencies:** Night 28, Night 34 (affected visits + strategy branches from handleDisruption), Night 61

**Reference:** SCHEDULING_ADVANCED_PLANNING_PRD.md US-3

**Complexity:** Medium
```

### Night 64: Compare Panel UI

```markdown
# Priority 1

**Description:** Bryntum component: after one or more strategies are optimized, show
Compare Panel with metric matrix (travel, assigned, utilization, cost, quality per
strategy), recommendation highlight, and actions: Select, Fine-tune, Publish. Uses
compareSolutions query and existing createSolutionFromPatch for fine-tune. Implements
US-3 UI part 2.

**Expected outcome:**

- New component: CompareSolutionsPanel or equivalent
- Metric table: baseline vs variants, deltas, recommendation
- Select → sets selected solution; Fine-tune → opens from-patch flow; Publish → publish flow
- Manual test: after Optimize All → Compare Panel → Select → Fine-tune or Publish
- Type-check passes

**Files:**

- apps/dashboard/src/components/Schedule/CompareSolutionsPanel.tsx (or similar)

**Dependencies:** Night 62

**Reference:** SCHEDULING_ADVANCED_PLANNING_PRD.md US-3

**Complexity:** Medium
```

### Night 65: What-If Entry Point

```markdown
# Priority 1

**Description:** Add "What-if" entry point from schedule view (button or menu). Opens
modal where manager configures supply/demand changes (e.g. +N employees, defer N
visits). Creates strategy branches and runs same optimizeStrategy + compareSolutions
flow; result shown in same Compare Panel. Implements US-5 (what-if without disruption).

**Expected outcome:**

- "What-if" button on schedule detail view
- Modal: configure supply/demand changes (add employees, defer visits, etc.)
- Creates strategy branches, calls optimizeStrategy for each, then compareSolutions
- Reuses Compare Panel from Night 64
- Manual test: What-if → configure → compare → select
- Type-check passes

**Files:**

- apps/dashboard/src/pages/ScheduleDetailPage.tsx (or equivalent)
- apps/dashboard/src/components/Schedule/WhatIfModal.tsx (or similar)

**Dependencies:** Night 61, Night 62, Night 64

**Reference:** SCHEDULING_ADVANCED_PLANNING_PRD.md US-5

**Complexity:** Medium
```

---

## Sprint 14: Multi-Area Scheduling (Night 66-70)

**Goal:** Allow schedules to span multiple service areas so the solver can share employees and improve routing across nearby areas. Implements US-2.

**Reference:** [SCHEDULING_ADVANCED_PLANNING_PRD.md](../../05-prd/SCHEDULING_ADVANCED_PLANNING_PRD.md) US-2; [CAIRE_FEATURE_ROADMAP.md](./CAIRE_FEATURE_ROADMAP.md)

### Night 66: Schedule Multi-Area Schema

```markdown
# Priority 1

**Description:** Add optional serviceAreaIds: [ID!] to Schedule (GraphQL + Prisma).
Backward compatibility: if only serviceAreaId is set, treat as serviceAreaIds = [serviceAreaId].
Migration for new column/relation. Enables multi-area schedule creation.

**Expected outcome:**

- Updated: packages/graphql/schema/dashboard/types.graphql (Schedule type)
- Updated: apps/dashboard-server/schema.prisma (Schedule model)
- Migration created and applied
- Existing schedules unchanged (single serviceAreaId → serviceAreaIds derived)
- Type-check passes

**Files:**

- packages/graphql/schema/dashboard/types.graphql
- apps/dashboard-server/schema.prisma

**Dependencies:** None

**Reference:** SCHEDULING_ADVANCED_PLANNING_PRD.md US-2

**Complexity:** Medium
```

### Night 67: Multi-Area Data Aggregation

```markdown
# Priority 1

**Description:** Update prepareScheduleData (or equivalent) to load visits and employees
from all schedule.serviceAreaIds. Build FSR input from combined set. Test: schedule
with 2 areas → input contains visits and vehicles from both areas.

**Expected outcome:**

- Updated: prepareScheduleData or schedule data service
- When serviceAreaIds.length > 1, aggregate visits and employees from all areas
- FSR input builder (prepareScheduleData or equivalent from existing pipeline) receives combined visits and vehicles
- Integration test: 2-area schedule → FSR input has visits from both
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/timefold/prepareScheduleData.ts (or equivalent)
- apps/dashboard-server/src/services/bridge/ (input builder)

**Dependencies:** Night 66; prepareScheduleData / FSR input builder (existing from schedule pipeline)

**Reference:** SCHEDULING_ADVANCED_PLANNING_PRD.md US-2

**Complexity:** Medium
```

### Night 68: Multi-Area ESS Demand Curve

```markdown
# Priority 1

**Description:** Update demand-curve.service.ts to aggregate demand across multiple
service areas when schedule has serviceAreaIds.length > 1. Tag shifts with area for
ESS concurrent-shift rules so ESS can assign employees across areas. Ensures ESS
output is consistent with multi-area FSR input.

**Expected outcome:**

- Updated: apps/dashboard-server/src/services/bridge/scheduling/demand-curve.service.ts
- Demand aggregated per hour across all schedule areas
- Shifts tagged with area for ESS (if required by ESS model)
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/scheduling/demand-curve.service.ts

**Dependencies:** Night 5, Night 66

**Reference:** SCHEDULING_ADVANCED_PLANNING_PRD.md US-2

**Complexity:** Medium
```

### Night 69: Multi-Area Schedule Creation UI

```markdown
# Priority 1

**Description:** Update schedule creation/editing form to allow selecting multiple
service areas (multi-select or "area group" if configured). Save schedule with
serviceAreaIds. Validation: at least one area selected.

**Expected outcome:**

- Schedule create/edit form: multi-select for service areas (or area group picker)
- On save, schedule.serviceAreaIds set from selection
- Existing single-area flow still works (one area selected)
- Manual test: create schedule with 2 areas → save → schedule has both
- Type-check passes

**Files:**

- apps/dashboard/src/ (schedule form / create schedule page)

**Dependencies:** Night 66

**Reference:** SCHEDULING_ADVANCED_PLANNING_PRD.md US-2

**Complexity:** Low
```

### Night 70: Multi-Area vs Single-Area Comparison

```markdown
# Priority 1

**Description:** Enable running single-area and multi-area schedules for the same date
and using compareSolutions to compare efficiency, cost, and utilization. Document or
UI hint for managers: "Compare single-area vs multi-area to see if combining areas
improves results." Closes US-2 comparison story.

**Expected outcome:**

- Same compareSolutions flow works for solutions from single-area and multi-area schedules
- Optional: preset or template "Single vs multi-area" comparison from schedule view
- Documentation or tooltip on when multi-area is beneficial
- Manual test: run single + multi-area → compare
- Type-check passes

**Files:**

- apps/dashboard (comparison entry point or docs)
- docs (optional short note in TIMEFOLD_GUIDES_ALIGNMENT or PRD)

**Dependencies:** Night 62, Night 67, Night 69

**Reference:** SCHEDULING_ADVANCED_PLANNING_PRD.md US-2

**Complexity:** Low
```

---

## Decision Gates

### After Sprint 2 (Week 2): ESS API Verification

**Gate:** Can we successfully call ESS API and get shift assignments?

- Verify Timefold ESS API is accessible with current API key
- Confirm pricing for ESS model (separate from FSR?)
- Validate that ESS demand-based scheduling works with our visit patterns
- **If blocked:** Fallback to ESS-lite (manual shift generation with labor law validation)

### After Sprint 3 (Week 3): Convergence Validation

**Gate:** Does the iterative loop converge for real Attendo data?

- Test with Huddinge_Final_Verified_geocoded.csv (1862 rows)
- Verify convergence in < 3 iterations
- Validate that learned profiles improve over time
- **If slow:** Increase geographic bootstrap accuracy, reduce max iterations to 2

### After Sprint 5 (Week 5): Pilot Readiness

**Gate:** Can we demo ESS+FSR to Attendo?

- All visits assigned with ESS-determined staffing
- Cost analysis shows fixed vs hourly breakdown
- Continuity score visible and trending toward target
- Side-by-side comparison: their manual slinga vs CAIRE ESS+FSR result

---

## PO Daily Workflow for This Project

```
Morning (5 min):
  1. Check dashboard for overnight PR
  2. Review PR diff (does it match expected outcome?)
  3. Run type-check if needed
  4. Merge if good

Afternoon (10 min):
  1. Verify merged work (quick functional check)
  2. Create tomorrow's priority file from this plan
  3. Adjust if dependencies changed

Example:
  reports/priorities-2026-02-10.md → Night 1 (ESS types)
  reports/priorities-2026-02-11.md → Night 2 (ESS client)
  reports/priorities-2026-02-12.md → Night 3 (Swedish contracts)
  reports/priorities-2026-02-13.md → Night 4 (Employee mapper)
  reports/priorities-2026-02-14.md → Night 5 (Demand curve)
```

---

## Risk Mitigation

| Risk                    | Probability | Impact | Mitigation                                                         |
| ----------------------- | ----------- | ------ | ------------------------------------------------------------------ |
| ESS API not accessible  | Low         | High   | Contact Timefold early, verify API key scope                       |
| ESS pricing too high    | Medium      | High   | ESS only used when shifts unknown (not daily), limits API calls    |
| Convergence too slow    | Low         | Medium | Geographic bootstrap is usually accurate enough for 1-2 iterations |
| Agent produces bad code | Medium      | Low    | Verification specialist catches type/build errors, PO reviews PR   |
| Night task too complex  | Medium      | Medium | Break into 2 nights, reduce scope of single priority               |

---

_Document created: 2026-02-08_  
_Review cadence: Weekly sprint review with management_  
_Contact Timefold for ESS API access: Before Sprint 1 starts_
