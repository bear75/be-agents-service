# Pre-Planning Frontend Implementation Guide

**Version:** 1.0  
**Date:** 2025-12-11  
**Purpose:** Explain how pre-planning with movable visits will be implemented in the Bryntum frontend

---

## Table of Contents

1. [Where Are Pre-Planning Requirements?](#where-are-pre-planning-requirements)
2. [Weekly/Monthly Planning with Movable Visits](#weeklymonthly-planning-with-movable-visits)
3. [Adding New Client's Movable Visit to Existing Schedules](#adding-new-clients-movable-visit-to-existing-schedules)
4. [Supply & Demand Balance Using Time Horizon](#supply--demand-balance-using-time-horizon)
5. [Schedule Health Tracking (Demand Curve)](#schedule-health-tracking-demand-curve)
6. [Unused Hours Display](#unused-hours-display)
7. [Unused Hours for Supply/Demand Balance](#unused-hours-for-supplydemand-balance)

---

## Pre-Planning Requirements & Concepts

### Core Concepts

**Pre-Planning:** Process of planning recurring visits across multiple weeks/months before they enter daily scheduling. Allows finding optimal patterns (day-of-week, time-of-day) for recurring visits through AI-powered optimization.

**Slinga (Slingor):** Weekly pattern of visits for a caregiver on a given weekday and shift (e.g., "Lisa – Monday day shift"). Slingor are the building blocks of stable schedules. Once approved, visits in a slinga become pinned (fixed).

**Pinned Visit:** Fixed time, duration, and caregiver (🔒 icon, solid background). Cannot move unless explicitly unlocked by planner. Represents stable recurring patterns that honor continuity promises to clients. Forms the baseline of daily schedules.

**Unpinned Visit:** Movable within allowed window (dashed border). Can be moved by optimizer or user. Used for new clients, flexible tasks, and visits that don't yet belong to a slinga.

**Movable Visit:** A recurring visit with flexible time window (e.g., "weekly, any day 8 AM-12 PM") that can be optimized to find best placement. Movable visits start as unpinned and become pinned after optimization and acceptance.

**Time Horizon:** Planning period (1 week, 1 month, 3 months, custom date range) for pre-planning optimization. Defines the scope of schedules to consider when optimizing.

**Unused Hours:** Client allocation hours that were not utilized (monthly allocation - actual service hours delivered). If a client has 100h total allowed visits per month and 5h are cancelled (by client or by org if optional visit during supply limitation), the unused hours = 5h. These unused hours can be recaptured when we have excess staff capacity.

**Supply/Demand Balance:** Comparison of available employee capacity (supply) vs required visit hours (demand) across time horizon. Used to identify capacity gaps, excess capacity, and optimal visit placement.

**Continuity:** Client preference to see the same caregiver at the same time each week. Modeled as hard or high-weight constraint in optimization. Critical for dementia clients and quality of care.

**Priority:** Visit priority levels (mandatory/optional) that influence which visits are preserved when capacity is tight. Obligatory visits (medication, meals) must be scheduled; optional visits (social activities) can be deferred.

### Three Planning Scenarios

**Scenario A: Regular Daily Planning (Stable Days)**

- Use slingor as baseline
- Minimize travel while respecting continuity and preferences
- Most visits are pinned (90%+)
- Small adjustments for daily variations
- Manual edits or minor re-optimization

**Scenario B: Pre-Planning with New Clients (Movable Visits)**

- Insert new recurring visits into existing slingor
- Existing visits remain pinned (stable)
- New visits start as unpinned (movable)
- Optimizer finds best insertion points
- After acceptance, new visits become pinned and join slingor

**Scenario C: Real-Time Disruptions (Chaos Days)**

- Handle cancellations, sick leave, urgent visits
- Temporarily unpin affected visits
- Run incremental optimization
- Fill gaps with nearby tasks or unused hours recapture
- Pinned visits remain fixed (already started or imminent)

### Two-Stage Optimization Process

**Stage 1: Pattern Discovery (5-15 minutes)**

- Optimize first occurrence of each movable visit group
- Find optimal day-of-week + time-of-day pattern
- Expand time windows (weekly → 7-day window, bi-weekly → 14-day window)
- Extract pattern from optimized first occurrence
- Replicate pattern to all future occurrences

**Stage 2: Employee Assignment (5-15 minutes, optional)**

- Assign employees to complete baseline schedule
- All visits have locked times (pinned=true)
- Optimize employee assignments considering:
  - Skills matching
  - Continuity preferences
  - Travel efficiency
  - Workload balance

### Movable Visit Status Lifecycle

```
draft → optimized → exported → synced
  ↑         ↓
  └── (unfreeze / re-optimize)
```

- **draft**: Visit group created, not yet optimized
- **optimized**: Pre-planning completed, pattern found, ready for review
- **exported**: Updates sent to external system (Carefox), waiting for sync confirmation
- **synced**: External system confirmed matching times, now in production

### Time Windows vs Flexibility

**Time Windows (Pre-Planning Phase):**

- Breda tillåtna perioder (e.g., "Morgon 07:00-10:00")
- Used to guide AI optimization
- Result: Optimal fixed times (e.g., "Varje måndag 08:00-08:40")

**Flexibility Minutes (Daily Optimization Phase):**

- Small buffers around fixed times (e.g., ±15 minutes)
- Set in external systems (Welfare/Epsilon/Carefox)
- Used for daily adjustments (traffic, delays)
- Not part of pre-planning phase

---

## Weekly/Monthly Planning with Movable Visits

### Frontend Implementation Overview

The Bryntum frontend will support **pre-planning mode** that allows planners to:

1. **View consolidated schedules** across multiple weeks/months
2. **Add new movable visits** to the planning horizon
3. **Run pre-planning optimization** to find optimal patterns
4. **Review and approve** optimized schedules
5. **Track schedule health** over longer time periods

### UI Components Required

#### 1. Pre-Planning Hub (Main Entry Point)

**Location:** `/dashboard/scheduling/pre-planning`

**Features:**

- **Time Horizon Selector**: Choose planning period (1 week, 1 month, 3 months, custom)
- **Movable Visits Panel**: List of all unassigned/unpinned visits
- **Consolidated Schedule View**: Multi-week/month calendar showing all schedules
- **Supply/Demand Dashboard**: Visual indicators of capacity vs demand
- **Unused Hours Tracker**: Display unused hours across the planning horizon

**Bryntum Integration:**

- Use **Timeline** example for multi-week view
- Use **Columns** example for employee metadata
- Use **Zoom** controls to navigate between day/week/month views

#### 2. Movable Visits Management

**Component:** `MovableVisitsDashboard` (already exists in codebase)

**Features:**

- **Create New Movable Visit**: Form to add client's recurring visit
- **Configure Time Windows**: Set allowed periods (e.g., "Morgon 07:00-10:00")
- **Set Frequency**: Daily, weekly, bi-weekly, monthly
- **Set Priority**: Mandatory vs optional
- **Set Skills Required**: Delegation, language, gender preferences

**Data Flow:**

```
User Input → GraphQL Mutation (createMovableVisit) → Backend stores as RecurringVisit →
System generates unassigned visits for planning horizon → Displayed in Movable Visits Panel
```

#### 3. Consolidated Schedule View

**Component:** `ConsolidatedCalendarView` (Bryntum-based)

**Features:**

- **Multi-Week/Month Display**: Show all schedules in planning horizon
- **Pinned vs Unpinned Indicators**:
  - Pinned visits: Solid background with 🔒 icon
  - Unpinned visits: Dashed border, can be moved
- **Time Horizon Navigation**: Scroll/zoom to navigate weeks/months
- **Supply/Demand Overlay**: Color-coded indicators showing capacity gaps

**Bryntum Configuration:**

```javascript
{
  viewPreset: 'weekAndMonth', // Multi-week view
  startDate: planningWindowStart,
  endDate: planningWindowEnd,
  resources: employees, // All employees in organization
  events: allVisits, // Pinned + unpinned visits
  features: {
    eventTooltip: true,
    eventEdit: true,
    drag: {
      constrainDragToResource: false, // Allow moving between weeks
    },
  },
}
```

#### 4. Pre-Planning Optimization Trigger

**Component:** Optimization Button in Pre-Planning Hub

**User Flow:**

1. User selects time horizon (e.g., "Next 30 days")
2. User adds new movable visits or adjusts existing ones
3. User clicks "Run Pre-Planning Optimization"
4. System calls GraphQL mutation: `runPrePlanningOptimization(input: { timeHorizon, movableVisitIds })`
5. Backend runs Timefold optimization (Stage 1: Pattern Discovery, Stage 2: Employee Assignment)
6. Frontend subscribes to optimization progress via WebSocket
7. When complete, frontend displays optimized schedule with diff view

**Bryntum Integration:**

- Use **WebSockets** example for real-time progress
- Use **Diff View** pattern to show before/after (ghost tracks for original, solid for optimized)

---

## Adding New Client's Movable Visit to Existing Schedules

### User Workflow

#### Step 1: Create Movable Visit

**UI Location:** Pre-Planning Hub → "Add New Movable Visit" button

**Form Fields:**

- Client selection (search/select from existing clients or create new)
- Visit title (e.g., "Frukosthjälp", "Medicinering")
- Duration (minutes)
- Frequency (daily, weekly, bi-weekly, monthly)
- Time window (e.g., "Morgon 07:00-10:00")
- Priority (mandatory/optional)
- Skills required (delegation, language, gender)
- Preferred staff (optional)
- Non-preferred staff (optional)

**GraphQL Mutation:**

```graphql
mutation CreateMovableVisit($input: CreateMovableVisitInput!) {
  createMovableVisit(input: $input) {
    id
    clientId
    frequency
    timeWindow {
      minStartTime
      maxStartTime
      maxEndTime
    }
    status # draft
  }
}
```

#### Step 2: System Generates Unassigned Visits

**Backend Process:**

1. Backend receives `CreateMovableVisit` mutation
2. Creates `RecurringVisit` record
3. Expands recurring visit into concrete `Visit` records for planning horizon
4. All generated visits are marked as:
   - `isMovable = true`
   - `pinned = false`
   - `assignedEmployeeId = null`
   - `scheduleId = null` (unassigned)

**Frontend Display:**

- New visits appear in "Unassigned Visits" panel
- Visits are grouped by client and frequency
- Each visit shows time window, priority, skills required

#### Step 3: Run Pre-Planning Optimization

**User Action:** Click "Run Pre-Planning Optimization" button

**Backend Process:**

1. Backend queries all visits in planning horizon:
   - Fixed visits (pinned = true)
   - Existing unpinned visits
   - **New unassigned movable visits** (pinned = false, scheduleId = null)
2. Backend calls Timefold API with:
   - All pinned visits (frozen)
   - All unpinned visits (movable, including new ones)
   - Employee shifts and availability
   - Constraints (skills, time windows, continuity)
3. Timefold optimizes placement of new visits around existing pinned patterns
4. Returns optimized assignments

**GraphQL Mutation:**

```graphql
mutation RunPrePlanningOptimization($input: PrePlanningOptimizationInput!) {
  runPrePlanningOptimization(input: $input) {
    jobId
    status
    estimatedDuration
  }
}
```

**WebSocket Subscription:**

```graphql
subscription PrePlanningProgress($jobId: ID!) {
  prePlanningProgress(jobId: $jobId) {
    status
    progress
    currentStage # "pattern_discovery" | "employee_assignment"
    metrics {
      travelTimeSaved
      continuityScore
      utilization
    }
  }
}
```

#### Step 4: Review Optimized Schedule

**Frontend Display:**

- Bryntum calendar shows optimized schedule
- **Diff View**:
  - Ghost tracks (faded) show where visits were before
  - Solid blocks show optimized positions
  - Connector lines explain moves
- **Metrics Panel**: Shows impact (travel time saved, continuity, utilization)

**User Actions:**

- Accept all changes
- Accept individual changes
- Reject and re-optimize with adjusted parameters

#### Step 5: Pin Accepted Visits

**User Action:** Click "Accept & Pin" for approved visits

**Backend Process:**

1. Updates visit records:
   - `pinned = true`
   - `assignedEmployeeId = <optimized employee>`
   - `assignedStartTime = <optimized time>`
   - `scheduleId = <target schedule>`
2. Creates/updates slingor for affected employees
3. Future schedules will include these visits as pinned

**GraphQL Mutation:**

```graphql
mutation AcceptPrePlanningSolution($input: AcceptPrePlanningSolutionInput!) {
  acceptPrePlanningSolution(input: $input) {
    success
    pinnedVisitIds
    updatedSlingorIds
  }
}
```

### Integration with Existing Schedules

**Key Principle:** New movable visits are inserted **around** existing pinned patterns, not replacing them.

**Visual Indicators in Bryntum:**

- **Pinned visits**: Solid blue background, 🔒 icon
- **New optimized visits**: Green background, dashed border initially
- **After pinning**: Green background becomes solid blue, 🔒 icon added

---

## Supply & Demand Balance Using Time Horizon

### Concept

**Supply** = Available employee capacity (shift hours - breaks)  
**Demand** = Required visit hours (service time + travel + wait)

**Goal:** Balance supply and demand across the planning horizon to:

- Minimize unused hours
- Maximize utilization
- Identify capacity gaps early
- Suggest when to add/remove visits

### Frontend Implementation

#### 1. Supply/Demand Dashboard Component

**Component:** `SupplyDemandDashboard` (already exists in codebase)

**Features:**

- **Time Horizon Selector**: Choose period (1 week, 1 month, 3 months)
- **Aggregated Metrics**:
  - Total supply hours (all employees)
  - Total demand hours (all visits)
  - Balance (supply - demand)
  - Utilization percentage
- **Per-Day Breakdown**: Show supply/demand for each day in horizon
- **Visual Indicators**:
  - Green: Balanced (utilization 75-85%)
  - Yellow: Underutilized (utilization < 75%)
  - Red: Overcapacity (demand > supply)

**Data Source:**

```graphql
query SupplyDemandBalance($input: SupplyDemandBalanceInput!) {
  supplyDemandBalance(input: $input) {
    timeHorizon {
      startDate
      endDate
    }
    dailyMetrics {
      date
      supplyHours
      demandHours
      balance
      utilization
      unusedHours
    }
    aggregatedMetrics {
      totalSupplyHours
      totalDemandHours
      totalBalance
      averageUtilization
      totalUnusedHours
    }
  }
}
```

#### 2. Movable Visits Impact Analysis

**Feature:** When adding a new movable visit, show impact on supply/demand

**UI Flow:**

1. User configures new movable visit (client, frequency, time window)
2. System calculates projected demand if visit is added
3. **Preview Panel** shows:
   - Current supply/demand balance
   - Projected balance after adding visit
   - Days with capacity gaps (red indicators)
   - Days with excess capacity (green indicators)
   - Recommended days/times for optimal balance

**Example Display:**

```
Current Balance (Next 30 Days):
  Supply: 2,400 hours
  Demand: 2,100 hours
  Balance: +300 hours (12.5% unused)

After Adding New Visit (Weekly, 1 hour):
  Projected Supply: 2,400 hours
  Projected Demand: 2,130 hours (+30 hours)
  Projected Balance: +270 hours (11.3% unused)

Recommended Placement:
  ✅ Monday 08:00-09:00 (fits existing gap)
  ✅ Wednesday 14:00-15:00 (fits existing gap)
  ⚠️ Friday 10:00-11:00 (would create overload)
```

#### 3. Time Horizon Visualization in Bryntum

**Bryntum Configuration:**

- Use **Timeline Histogram** example to show demand curve
- Overlay employee capacity bars
- Color-code by balance (green/yellow/red)

**Custom Overlay:**

```javascript
{
  features: {
    timeRanges: {
      // Show supply capacity as background ranges
      data: employeeShifts.map(shift => ({
        startDate: shift.startTime,
        endDate: shift.endTime,
        name: `${shift.employeeName} - Available`,
        cls: 'supply-capacity',
      })),
    },
    eventTooltip: {
      // Show demand (visits) as events
      template: (data) => {
        return `
          <div>Visit: ${data.eventRecord.name}</div>
          <div>Duration: ${data.eventRecord.duration} min</div>
          <div>Demand Impact: +${data.eventRecord.duration} min</div>
        `;
      },
    },
  },
}
```

#### 4. Recommendations Based on Supply/Demand

**Feature:** AI-powered recommendations for optimal visit placement

**Backend Process:**

1. System analyzes supply/demand balance across time horizon
2. Identifies:
   - Days with excess staff capacity (can recapture unused client allocation)
   - Days with capacity gaps (demand > supply)
   - Optimal time slots for new visits
3. Returns ranked recommendations

**GraphQL Query:**

```graphql
query GetOptimalPlacementRecommendations(
  $input: PlacementRecommendationsInput!
) {
  getOptimalPlacementRecommendations(input: $input) {
    recommendations {
      dayOfWeek
      timeWindow {
        startTime
        endTime
      }
      employeeId
      score # 0-100, higher is better
      reasoning # "Fits existing gap", "Minimizes travel", etc.
      impactMetrics {
        utilizationChange
        travelTimeChange
        continuityScore
      }
    }
  }
}
```

**Frontend Display:**

- Recommendations shown in tooltip when hovering over calendar cells
- "Best Fit" badge on recommended time slots
- Click recommendation to auto-fill visit configuration

---

## Schedule Health Tracking (Demand Curve)

### Concept

**Demand Curve** = Visualization of visit demand over time (weeks/months)

**Purpose:**

- Identify trends (increasing/decreasing demand)
- Spot capacity bottlenecks early
- Plan for seasonal variations
- Track schedule stability over time

### Frontend Implementation

#### 1. Demand Curve Visualization

**Component:** `DemandCurveChart` (new component, using Chart.js or Recharts)

**Features:**

- **Line Chart**: Show visit hours per day/week over time horizon
- **Capacity Line**: Overlay employee capacity (supply)
- **Trend Indicators**:
  - Upward trend (increasing demand)
  - Downward trend (decreasing demand)
  - Stable (consistent demand)
- **Anomaly Detection**: Highlight days with unusual demand spikes/drops

**Data Source:**

```graphql
query DemandCurve($input: DemandCurveInput!) {
  demandCurve(input: $input) {
    timeHorizon {
      startDate
      endDate
    }
    dataPoints {
      date
      visitHours
      visitCount
      capacityHours
      utilization
      trend # "increasing" | "decreasing" | "stable"
    }
    aggregatedTrends {
      overallTrend
      weeklyAverage
      monthlyAverage
      seasonalVariation
    }
  }
}
```

#### 2. Schedule Health Metrics Panel

**Component:** `ScheduleHealthDashboard` (new component)

**Metrics Displayed:**

- **Stability Score**: How consistent are visit patterns? (0-100)
- **Capacity Utilization**: Average utilization across time horizon
- **Unused Hours Trend**: Are unused hours increasing/decreasing?
- **Continuity Score**: How well are continuity promises maintained?
- **Travel Efficiency**: Average travel time per visit

**Visual Indicators:**

- 🟢 Green: Healthy (stability > 80%, utilization 75-85%)
- 🟡 Yellow: Warning (stability 60-80%, utilization < 75% or > 90%)
- 🔴 Red: Critical (stability < 60%, utilization < 60% or > 95%)

#### 3. Long-Term Health Tracking

**Feature:** Track schedule health over multiple planning cycles

**Data Storage:**

- Backend stores health metrics snapshots after each pre-planning cycle
- Frontend queries historical health data

**GraphQL Query:**

```graphql
query ScheduleHealthHistory($input: HealthHistoryInput!) {
  scheduleHealthHistory(input: $input) {
    snapshots {
      date
      stabilityScore
      utilization
      unusedHours
      continuityScore
      travelEfficiency
    }
    trends {
      stabilityTrend # "improving" | "declining" | "stable"
      utilizationTrend
      unusedHoursTrend
    }
    recommendations {
      message
      priority # "high" | "medium" | "low"
      action # "add_visits" | "remove_visits" | "adjust_capacity"
    }
  }
}
```

**Frontend Display:**

- **Timeline View**: Show health metrics over past 3/6/12 months
- **Trend Arrows**: Visual indicators for improving/declining metrics
- **Recommendations Panel**: Actionable suggestions based on trends

#### 4. Integration with Bryntum Calendar

**Overlay on Calendar:**

- **Health Heatmap**: Color-code days by health score
- **Trend Indicators**: Small arrows on days showing demand trend
- **Capacity Warnings**: Red borders on days with capacity issues

**Bryntum Configuration:**

```javascript
{
  features: {
    timeRanges: {
      // Overlay health indicators
      data: healthData.map(day => ({
        startDate: day.date,
        endDate: day.date,
        name: `Health: ${day.stabilityScore}`,
        cls: `health-${day.healthLevel}`, // health-good, health-warning, health-critical
      })),
    },
  },
}
```

---

## Unused Hours Display

### Concept

**Unused Hours** = Client allocation hours that were not utilized (monthly allocation - actual service hours delivered)

**Purpose:**

- Identify clients with unused allocation (cancelled visits, optional visits not scheduled during supply limitation)
- Opportunities for recapturing hours when we have excess staff capacity
- Track which clients have unused allocation that could be utilized

### Frontend Implementation

#### 1. Unused Hours Panel

**Component:** `UnusedHoursDashboard` (part of `MetricsBalanceDashboard`, already exists)

**Features:**

- **Total Unused Hours**: Aggregated across time horizon (sum of all clients' unused allocation)
- **Per-Client Breakdown**: Show unused allocation hours per client (which clients have unused allocation and how much)
- **Per-Day Breakdown**: Show unused allocation hours per day
- **Recapture Opportunities**: Identify when unused allocation can be utilized (when we have excess staff capacity)

**Data Source:**

```graphql
query UnusedHours($input: UnusedHoursInput!) {
  unusedHours(input: $input) {
    timeHorizon {
      startDate
      endDate
    }
    totalUnusedHours # Sum of all clients' unused allocation
    perClient {
      clientId
      clientName
      monthlyAllocation
      actualServiceHours
      unusedHours # monthlyAllocation - actualServiceHours
      recaptureOpportunities {
        visitId
        visitName
        canRecapture # true if excess staff capacity available
      }
    }
    perDay {
      date
      unusedHours # Sum of clients' unused allocation for this day
      topOpportunities {
        clientId
        clientName
        unusedHours
      }
    }
  }
}
```

#### 2. Visual Indicators in Bryntum Calendar

**Display Options:**

- **Client Badge**: Show unused allocation hours as badge on client visits
- **Time Range Overlay**: Highlight periods where unused allocation could be recaptured
- **Tooltip**: Show unused allocation hours when hovering over client visits

**Bryntum Configuration:**

```javascript
{
  columns: [
    {
      text: 'Employee',
      field: 'name',
      width: 150,
    },
    {
      text: 'Unused Allocation',
      field: 'unusedHours',
      width: 120,
      renderer: ({ record }) => {
        const hours = record.unusedHours || 0; // Client's unused allocation hours
        const color = hours > 5 ? 'red' : hours > 2 ? 'orange' : 'green';
        return `<span style="color: ${color}">${hours.toFixed(1)}h</span>`;
      },
    },
  ],
  features: {
    timeRanges: {
      // Show unused time as transparent ranges
      data: unusedTimeSlots.map(slot => ({
        resourceId: slot.employeeId,
        startDate: slot.startTime,
        endDate: slot.endTime,
        name: `Unused: ${slot.hours}h`,
        cls: 'unused-time-slot',
        style: 'opacity: 0.3; background: gray;',
      })),
    },
  },
}
```

#### 3. Unused Hours Metrics in Tooltips

**Employee Row Tooltip:**

```
Employee: Lisa K.
Shift: 07:00-16:00 (9 hours)
Service Time: 6.5 hours
Travel Time: 1.0 hour
Wait Time: 0.5 hours
Break: 0.5 hours
─────────────────
Unused Hours: 0.5 hours
Cost: 92.50 SEK
Recapture Opportunities: 2 visits could fit
```

**Visit Event Tooltip:**

```
Visit: Frukost - Anna S.
Duration: 40 min
Assigned: Lisa K. at 08:00
─────────────────
If moved to 14:00:
  Client unused allocation: 5h (can be recaptured when excess staff capacity available)
  Impact: Utilize unused allocation
```

#### 4. Unused Hours Toggle

**Feature:** Toggle to show/hide unused hours indicators

**UI Control:**

- Checkbox in toolbar: "Show Unused Hours"
- When enabled:
  - Unused time slots highlighted
  - Badges shown on employee rows
  - Tooltips include unused hours info
- When disabled:
  - Normal calendar view (unused hours still calculated, just not displayed)

---

## Unused Hours for Supply/Demand Balance

### Concept

**Unused Hours (Client Allocation)** are a key metric for supply/demand balance:

- **High Unused Hours** = Clients have unused allocation that could be utilized when we have excess staff capacity
  - **Action**: Recapture unused allocation by scheduling cancelled/optional visits when staff capacity allows
- **Low/Zero Unused Hours** = Clients' allocation is fully utilized (or minimal cancellations)
  - **Action**: Monitor for trends, maintain current utilization

### Frontend Implementation

#### 1. Supply/Demand Balance with Unused Hours

**Component:** `SupplyDemandBalanceChart` (enhanced version of `SupplyDemandDashboard`)

**Visualization:**

- **Stacked Bar Chart**:
  - Bottom: Service hours delivered (utilized)
  - Middle: Travel + wait hours (utilized)
  - Top: Unused allocation hours (client-side, can be recaptured when excess staff capacity)
- **Target Line**: Optimal utilization (75-85%)
- **Color Coding**:
  - Green: Unused allocation < 10% of total monthly allocation (well-utilized)
  - Yellow: Unused allocation 10-20% (moderate cancellations)
  - Red: Unused allocation > 20% (high cancellation rate, investigate reasons)

**Data Source:**

```graphql
query SupplyDemandBalanceWithUnusedHours($input: BalanceInput!) {
  supplyDemandBalanceWithUnusedHours(input: $input) {
    dailyMetrics {
      date
      supplyHours
      demandHours
      utilizedHours # service + travel + wait
      unusedHours
      utilizationPercentage
      unusedPercentage
    }
    recommendations {
      type # "add_visits" | "remove_capacity" | "adjust_schedule"
      priority
      message
      estimatedImpact {
        unusedHoursChange
        utilizationChange
        costChange
      }
    }
  }
}
```

#### 2. Recommendations Based on Unused Hours

**Feature:** AI-powered recommendations to balance supply/demand using unused hours

**Recommendation Types:**

**A. Recapture Unused Allocation (High Unused Hours + Excess Staff)**

```
Client Unused Allocation: 45 hours/week across multiple clients
Staff Capacity: Excess capacity available
Recommendation: Recapture unused allocation by scheduling cancelled/optional visits
Impact: Utilize 45h of unused client allocation
Suggested Actions:
  - Schedule optional visits for clients with unused allocation
  - Recapture cancelled visits when staff capacity allows
```

**B. Monitor Unused Allocation (Persistent High Unused Hours)**

```
Client Unused Allocation: 60 hours/week for 4+ weeks
Recommendation: Investigate why clients have persistent unused allocation
Impact: Identify if cancellations are client-driven or supply-driven
Suggested Actions:
  - Review cancellation reasons (client-initiated vs org-initiated during supply limitation)
  - Identify if optional visits are being skipped due to supply constraints
  - Plan to recapture when staff capacity becomes available
```

**C. Monitor Unused Allocation (Moderate Unused Hours)**

```
Client Unused Allocation: 15 hours/week (6% of monthly allocation)
Recommendation: Normal level of cancellations, monitor for trends
Impact: Minimal impact, within expected range
Suggested Actions:
  - Move 2 visits from Tuesday to Wednesday (better fit)
  - Adjust 1 visit time by 30 min (reduces travel)
```

**Frontend Display:**

- Recommendations shown in dedicated panel
- Click recommendation to see detailed impact analysis
- "Apply Recommendation" button to auto-adjust schedule

#### 3. Interactive Unused Hours Management

**Feature:** Recapture unused client allocation when excess staff capacity is available

**UI Flow:**

1. User enables "Show Unused Hours" toggle
2. Client visits with unused allocation highlighted in calendar
3. System identifies periods with excess staff capacity
4. User can schedule optional visits or recapture cancelled visits for clients with unused allocation
5. System validates:
   - Visit fits in time slot
   - Skills match
   - Time window allows
6. If valid, visit is assigned and unused hours recalculated

**Bryntum Integration:**

```javascript
{
  features: {
    drag: {
      // Highlight unused time slots as valid drop targets
      validTargets: (context) => {
        const { eventRecord, targetResource, targetDate } = context;
        const unusedSlots = getUnusedTimeSlots(targetResource, targetDate);
        return unusedSlots.some(slot =>
          eventRecord.duration <= slot.duration &&
          isWithinTimeWindow(eventRecord, slot) &&
          skillsMatch(eventRecord, targetResource)
        );
      },
    },
    timeRanges: {
      // Show unused slots as drop targets
      data: unusedTimeSlots.map(slot => ({
        resourceId: slot.employeeId,
        startDate: slot.startTime,
        endDate: slot.endTime,
        name: `Unused: Drop visit here`,
        cls: 'unused-drop-target',
        style: 'border: 2px dashed green; background: rgba(0,255,0,0.1);',
      })),
    },
  },
}
```

#### 4. Unused Hours Metrics in Metrics Panel

**Display in Main Metrics Panel:**

```
Schedule Metrics (Next 30 Days):
─────────────────────────────────
Total Supply: 2,400 hours
Total Demand: 2,100 hours
Utilized: 2,100 hours (87.5%)
─────────────────────────────────
Client Unused Allocation: 300 hours (12.5% of total monthly allocation)
Cost: 55,500 SEK
Recapture Potential: 8 clients with unused allocation (120 hours total) can be utilized when excess staff capacity available
```

**Per-Client Metrics:**

```
Client: Anna S.
─────────────────────────────────
Monthly Allocation: 100 hours
Actual Service Hours: 95 hours
Unused Allocation: 5 hours (5%)
Can Recapture: When excess staff capacity available
Top Opportunities: 2 optional visits could utilize 3h
```

---

## Summary

### Key Frontend Components Needed

1. **Pre-Planning Hub** - Main entry point with time horizon selector
2. **Movable Visits Dashboard** - Manage unassigned/unpinned visits
3. **Consolidated Calendar View** - Multi-week/month Bryntum calendar
4. **Supply/Demand Dashboard** - Balance visualization
5. **Demand Curve Chart** - Long-term health tracking
6. **Unused Hours Panel** - Display and manage unused client allocation
7. **Optimization Progress** - Real-time WebSocket updates
8. **Diff View** - Before/after comparison for optimized schedules

### Key GraphQL Operations

1. `createMovableVisit` - Add new client's recurring visit
2. `runPrePlanningOptimization` - Trigger optimization
3. `prePlanningProgress` (subscription) - Real-time progress
4. `acceptPrePlanningSolution` - Pin approved visits
5. `supplyDemandBalance` - Get balance metrics
6. `demandCurve` - Get demand trend data
7. `unusedHours` - Get unused hours analysis
8. `getOptimalPlacementRecommendations` - AI recommendations

### Integration Points

- **Bryntum Calendar**: Main scheduling view with pinned/unpinned indicators
- **WebSocket**: Real-time optimization progress
- **GraphQL**: All data operations
- **Metrics Panels**: Display supply/demand, unused hours, health scores
- **Tooltips**: Show detailed metrics on hover
- **Drag & Drop**: Recapture unused client allocation when excess staff capacity available

---

**Last Updated:** 2025-12-11  
**Version:** 1.0
