# PRD: TimeFold Integration — Employee Scheduling & Field Service Routing

**Priority:** 3 (after mobile app)
**Status:** Documentation only — not yet approved for implementation
**Created:** 2026-02-08

---

## 1. Problem Statement

AppCaire currently handles scheduling **manually** — coordinators drag visits onto employee timelines using the Bryntum SchedulerPro dashboard. This works for small organizations but breaks down at scale:

- **Manual assignment** — Coordinators spend 2-4 hours daily assigning 50+ visits to 15+ caregivers
- **Suboptimal routes** — No travel time optimization; caregivers zigzag across the city
- **Constraint blindness** — Hard to mentally track certifications, client preferences, employee availability, and travel time simultaneously
- **No re-optimization** — When a caregiver calls in sick, the coordinator manually reassigns all their visits
- **Employee dissatisfaction** — Unfair workload distribution; some get harder routes than others

### What TimeFold Solves

[TimeFold](https://timefold.ai) is an AI-powered constraint solving engine that optimizes:

1. **Employee Shift Scheduling** — Assign employees to shifts considering skills, availability, preferences, fairness, and labor regulations
2. **Field Service Routing** — Assign visits to caregivers and optimize travel routes considering time windows, skills, vehicle capacity, and real-time conditions

By integrating TimeFold, we automate the coordinator's manual work: **input visits + employees → output optimized schedules with routes**.

## 2. Current Architecture

```
┌────────────────────────────┐
│  dashboard-server          │
│  (Apollo + Prisma + PG)    │
│                            │
│  Employees ──┐             │
│  Visits ─────┤             │
│  Schedules ──┤             │
│  Shifts ─────┘             │
│                            │
│  Manual assignment via     │
│  Bryntum SchedulerPro UI   │
└────────────────────────────┘
```

### Existing Data Model (Relevant)

```prisma
model Employee {
  id              BigInt
  name            String
  organizationId  BigInt
  certifications  Certification[]
  availability    Availability[]
  // ... location, contact, etc.
}

model Visit {
  id              BigInt
  clientId        BigInt
  scheduledStart  DateTime
  scheduledEnd    DateTime
  duration        Int          // minutes
  requiredSkills  String[]     // e.g., ["medication", "wound-care"]
  address         String
  latitude        Float?
  longitude       Float?
  assignedTo      Employee?
  status          VisitStatus  // PLANNED, IN_PROGRESS, COMPLETED
  // ...
}

model Shift {
  id              BigInt
  employeeId      BigInt
  startTime       DateTime
  endTime         DateTime
  // ...
}
```

## 3. Proposed Architecture

### 3.1 Integration Pattern: Backend Microservice

TimeFold runs as a **separate optimization microservice** that the dashboard-server calls via REST API. This keeps the monorepo clean and allows independent scaling.

```
┌────────────────────────────┐
│  dashboard (React + Vite)  │
│  "Optimize" button in UI   │
│         │                  │
│         ▼                  │
│  dashboard-server          │      ┌──────────────────────┐
│  (Apollo + Prisma)         │─────▶│  TimeFold Platform   │
│                            │ REST │  (Cloud API)         │
│  New: optimization-service │◀─────│                      │
│  module in server          │      │  OR                  │
│                            │      │                      │
│                            │      │  TimeFold Solver      │
│                            │      │  (Self-hosted Java)  │
└────────────────────────────┘      └──────────────────────┘
```

### 3.2 Two Integration Options

**Option A: TimeFold Cloud Platform (Recommended to start)**

- Use TimeFold's hosted REST API
- No Java infrastructure needed
- Pay-per-solve pricing
- API key authentication
- Endpoints: `POST /v1/route-plans`, `GET /v1/route-plans/{id}`
- Faster time to value

**Option B: Self-Hosted TimeFold Solver (Future)**

- Run TimeFold Solver (Java/Quarkus) on our infrastructure
- Full control, no per-solve costs
- Requires Java runtime + Docker
- More customizable constraints
- Better for high-volume (100+ solves/day)

**Recommendation:** Start with Option A (Cloud API). Migrate to Option B when solve volume justifies self-hosting.

## 4. Integration Design

### 4.1 Data Flow

```
1. Coordinator clicks "Optimize Schedule" for a date range
                    │
                    ▼
2. dashboard-server collects:
   - Unassigned visits (with locations, time windows, skills needed)
   - Available employees (with shifts, skills, home locations)
   - Constraints (max hours, travel preferences, client preferences)
                    │
                    ▼
3. Transform to TimeFold input format:
   {
     "vehicles": [...],   // employees with shifts
     "visits": [...]      // visits with locations + time windows
   }
                    │
                    ▼
4. POST to TimeFold API → returns job ID
                    │
                    ▼
5. Poll for solution (typically 1-5 minutes)
                    │
                    ▼
6. Parse solution:
   - Visit → Employee assignments
   - Optimized visit order per employee
   - Travel time estimates
   - Unassigned visits (if infeasible)
                    │
                    ▼
7. Present to coordinator:
   - "Accept all" → apply assignments
   - "Review" → show changes, let coordinator adjust
   - "Reject" → discard, keep manual assignments
                    │
                    ▼
8. Write accepted assignments to database
   - Update Visit.assignedTo
   - Update Visit.scheduledStart/End (optimized times)
   - Store route order as metadata
```

### 4.2 TimeFold Data Mapping

**Vehicles = Employees**

```typescript
// Our Employee → TimeFold Vehicle
{
  id: employee.id,
  shifts: [{
    id: shift.id,
    start: shift.startTime,   // "2026-02-10T08:00:00"
    end: shift.endTime,       // "2026-02-10T16:00:00"
    startLocation: {
      latitude: employee.homeLatitude,
      longitude: employee.homeLongitude,
    },
    endLocation: {
      latitude: employee.homeLatitude,  // returns home
      longitude: employee.homeLongitude,
    },
  }],
  skillSet: employee.certifications.map(c => c.type),
}
```

**Visits = Visits**

```typescript
// Our Visit → TimeFold Visit
{
  id: visit.id,
  name: `Visit ${visit.id} - ${client.name}`,
  location: {
    latitude: visit.latitude,
    longitude: visit.longitude,
  },
  serviceDuration: `PT${visit.duration}M`,  // ISO 8601 duration
  minStartTime: visit.earliestStart,        // time window
  maxEndTime: visit.latestEnd,              // time window
  requiredSkills: visit.requiredSkills,
  priority: visit.priority || "MEDIUM",     // HIGH visits must be assigned
}
```

### 4.3 Constraint Configuration

| Constraint | Type | Description |
|-----------|------|-------------|
| Time windows | Hard | Visit must happen within client's preferred time |
| Employee skills | Hard | Employee must have required certifications |
| Shift boundaries | Hard | All visits within employee's shift hours |
| Max travel time | Hard | No single leg > 45 minutes |
| Travel time | Soft (minimize) | Minimize total travel across all employees |
| Fairness | Soft | Balance workload across employees |
| Client preference | Soft | Prefer the same caregiver for regular clients |
| Consecutive visits | Soft | Minimize gaps between visits for an employee |
| Employee preference | Soft | Respect employee location/area preferences |

### 4.4 New GraphQL API

```graphql
type Mutation {
  """
  Submit an optimization request for a date range.
  Returns an optimization job ID to poll for results.
  """
  requestScheduleOptimization(input: OptimizationInput!): OptimizationJob!

  """
  Accept an optimization result and apply it to the schedule.
  """
  acceptOptimizationResult(jobId: ID!): AcceptResult!

  """
  Reject an optimization result.
  """
  rejectOptimizationResult(jobId: ID!): Boolean!
}

type Query {
  """
  Get the status and result of an optimization job.
  """
  optimizationJob(id: ID!): OptimizationJob!

  """
  List recent optimization jobs for the organization.
  """
  optimizationHistory(limit: Int): [OptimizationJob!]!
}

input OptimizationInput {
  startDate: DateTime!
  endDate: DateTime!
  includeEmployeeIds: [ID!]        # Optional: only optimize for specific employees
  includeVisitIds: [ID!]           # Optional: only optimize specific visits
  constraints: ConstraintConfig    # Optional: override default constraints
}

type OptimizationJob {
  id: ID!
  status: OptimizationStatus!      # SUBMITTED, SOLVING, SOLVED, FAILED
  submittedAt: DateTime!
  solvedAt: DateTime
  score: String                    # TimeFold score (hard/soft violations)
  result: OptimizationResult
  inputSummary: OptimizationInputSummary!
}

type OptimizationResult {
  assignments: [VisitAssignment!]!
  unassignedVisits: [UnassignedVisit!]!
  totalTravelTime: Int!            # minutes
  employeeSummaries: [EmployeeRouteSummary!]!
}

type VisitAssignment {
  visitId: ID!
  employeeId: ID!
  optimizedStart: DateTime!
  optimizedEnd: DateTime!
  travelTimeFromPrevious: Int!     # minutes
  previousVisitId: ID             # for route ordering
}

type UnassignedVisit {
  visitId: ID!
  reason: String!                  # "No qualified employee available"
}

type EmployeeRouteSummary {
  employeeId: ID!
  employeeName: String!
  visitCount: Int!
  totalTravelTime: Int!            # minutes
  utilization: Float!              # percentage of shift spent on visits
  route: [ID!]!                    # ordered visit IDs
}
```

## 5. Work Breakdown

### Phase 1: Foundation (Week 1)

| # | Task | Effort | Details |
|---|------|--------|---------|
| 1.1 | Set up TimeFold Cloud API account + API key | S | Sign up at app.timefold.ai |
| 1.2 | Create `optimization-service` module in dashboard-server | M | `apps/dashboard-server/src/services/optimization/` |
| 1.3 | Build TimeFold API client (REST, with retry + polling) | M | `optimization/timefold-client.ts` |
| 1.4 | Create data transformation layer (our models → TimeFold format) | L | `optimization/transformers.ts` |
| 1.5 | Store API key securely in env config | S | `.env` + dotenvx |

### Phase 2: Backend Integration (Week 2)

| # | Task | Effort | Details |
|---|------|--------|---------|
| 2.1 | Add `OptimizationJob` Prisma model (track job status) | M | New table for audit trail |
| 2.2 | Create GraphQL schema for optimization (see §4.4) | M | Types, queries, mutations |
| 2.3 | Implement `requestScheduleOptimization` resolver | L | Collect data, transform, submit to TimeFold |
| 2.4 | Implement polling + webhook for job completion | M | Background job or polling resolver |
| 2.5 | Implement `acceptOptimizationResult` resolver | M | Parse result, update Visit assignments |
| 2.6 | Add organizationId filtering to all optimization queries | S | Security: org-scoped |

### Phase 3: Dashboard UI (Week 3)

| # | Task | Effort | Details |
|---|------|--------|---------|
| 3.1 | Add "Optimize" button to schedule view | S | Opens optimization dialog |
| 3.2 | Build optimization dialog (date range, employee filter) | M | Form with constraints |
| 3.3 | Build optimization progress view (polling, spinner) | M | Real-time status updates |
| 3.4 | Build result comparison view (before/after) | L | Side-by-side schedule diff |
| 3.5 | Build route visualization on map | L | Show employee routes with travel times |
| 3.6 | Add "Accept" / "Reject" / "Adjust" actions | M | Apply or discard results |

### Phase 4: Mobile App Integration (Week 4)

| # | Task | Effort | Details |
|---|------|--------|---------|
| 4.1 | Show optimized route order in caregiver app | M | Ordered visit list with travel times |
| 4.2 | Show "next visit" with ETA and navigation | M | Auto-calculated from TimeFold route |
| 4.3 | Push notification when route is re-optimized | S | Alert caregiver of schedule change |

### Phase 5: Advanced Features (Week 5+)

| # | Task | Effort | Details |
|---|------|--------|---------|
| 5.1 | Real-time re-optimization (caregiver sick → auto-reassign) | L | Triggered by status change |
| 5.2 | Client preference learning (prefer same caregiver) | M | Track history, feed as soft constraint |
| 5.3 | Multi-day optimization (weekly schedule planning) | L | Batch optimization for the week |
| 5.4 | Self-hosted TimeFold Solver (cost optimization) | XL | Java/Quarkus microservice |
| 5.5 | Route optimization feedback loop | M | Track actual vs predicted travel times |

## 6. Technical Considerations

### 6.1 TimeFold API Limits

| Limit | Cloud Platform | Self-Hosted |
|-------|---------------|-------------|
| Solve time | ~2-5 min for 50 visits | Configurable |
| Concurrent solves | Depends on plan | Unlimited |
| API calls/hour | Depends on plan | Unlimited |
| Data retention | 30 days | Unlimited |

### 6.2 Geocoding

Visits need latitude/longitude for route optimization. Options:
- Store on Visit model (preferred — already have `latitude`/`longitude` fields)
- Geocode addresses on-the-fly (slower, API costs)
- Batch geocode when visits are created

### 6.3 Travel Time Estimation

TimeFold supports:
- **Straight-line distance** (fastest, least accurate)
- **Road network distance** (requires road distance matrix)
- **Real-time traffic** (requires external API like Google Maps)

**Recommendation:** Start with straight-line. Upgrade to road network when accuracy matters.

### 6.4 Error Handling

- **Infeasible solutions** — Some visits can't be assigned (missing skills, no time). Surface as "unassigned visits" with reasons.
- **API timeouts** — TimeFold solve can take minutes. Use async polling, not blocking requests.
- **Partial acceptance** — Let coordinators accept some assignments and manually handle others.

## 7. Cost Analysis

### TimeFold Cloud Pricing (Estimated)

| Usage | Volume | Estimated Cost |
|-------|--------|---------------|
| Starter | ~50 solves/month | Free tier |
| Growth | ~200 solves/month | ~$200/month |
| Scale | ~1000 solves/month | ~$500/month |

### ROI Estimate

| Current (Manual) | With TimeFold |
|-------------------|---------------|
| 2-4 hours/day coordinator time | 15 min review + accept |
| Suboptimal routes (~30% excess travel) | Optimized routes (-20-30% travel) |
| Unfair workload distribution | Balanced distribution |
| 30+ min to handle sick call reassignment | 5 min re-optimization |

**Break-even:** ~10 hours/month coordinator time saved = 1 coordinator-day/month. At Swedish labor costs, this far exceeds the API cost.

## 8. Non-Goals (V1)

- ❌ Real-time GPS tracking of caregivers
- ❌ Fuel cost optimization
- ❌ Multi-vehicle types (all caregivers use same transport mode)
- ❌ Dynamic pricing for visits
- ❌ Integration with external ERP/payroll systems
- ❌ Self-hosted TimeFold (Phase 5 future work)

## 9. Dependencies

| Dependency | Status | Required For |
|-----------|--------|-------------|
| Visit geocoding (lat/lng) | Partially exists | Route optimization |
| Employee home address (lat/lng) | Needs adding | Start/end location |
| Certification model | Exists | Skill matching |
| Shift model | Exists | Time constraints |
| Mobile app (Priority 2) | In progress | Phase 4 route display |

## 10. Success Metrics

| Metric | Target | How |
|--------|--------|-----|
| Coordinator scheduling time | -60% | Time tracking before/after |
| Total caregiver travel time | -25% | Compare route distances |
| Visit on-time rate | 95%+ | Check-in time vs scheduled time |
| Workload fairness | Gini coefficient < 0.15 | Visit count distribution |
| Coordinator satisfaction | NPS > 50 | Survey |
| Optimization acceptance rate | 80%+ | Accepted / total optimizations |

---

## References

- [TimeFold Platform Docs](https://docs.timefold.ai/)
- [Field Service Routing API](https://docs.timefold.ai/field-service-routing/latest/understanding-the-api)
- [Employee Shift Scheduling API](https://docs.timefold.ai/employee-shift-scheduling/latest/understanding-the-api)
- [TimeFold Model SDK (Java)](https://docs.timefold.ai/sdk/latest/introduction)
- [TimeFold GitHub](https://github.com/timefoldai)

---

*This document is for planning and documentation only. Implementation has not been approved. See priorities.md for current execution order.*
