# Movable Visits Guide

**Version:** 2.0  
**Last Updated:** 2025-12-11

---

## Overview

Movable visits are flexible visits that can be scheduled on different days within their time window. They are used for pre-planning, new client integration, and demand/supply management.

**Key Concepts:**

- **Movable**: Time window spans multiple days
- **Lifecycle**: New → Frozen → Pinned
- **Pre-planning**: Optimize placement across longer time horizons
- **Template updates**: Stable improvements become part of slingor

---

## Movable Visit Lifecycle

### 1. New Movable Visit

**Status**: Not yet optimized, full flexibility

**Characteristics**:

- Time window spans multiple days (weekly/monthly)
- Not assigned to employee
- Not pinned
- Can be placed anywhere in time window

**Example**:

```json
{
  "id": "movable-visit-123",
  "timeWindows": [
    {
      "minStartTime": "2026-01-15T08:00:00+01:00", // Monday
      "maxEndTime": "2026-01-22T17:00:00+01:00" // Sunday (full week)
    }
  ],
  "pinningRequested": false,
  "frequency": "weekly"
}
```

**Use Case**: New biståndsbeslut visit that can happen any day in the week.

### 2. Frozen Movable Visit

**Status**: Planner decided on specific date, but not yet assigned

**Characteristics**:

- Time window narrowed to single day
- Not assigned to employee
- Not pinned
- Must be scheduled on that date

**Example**:

```json
{
  "id": "movable-visit-456-frozen-2026-01-17",
  "timeWindows": [
    {
      "minStartTime": "2026-01-17T08:00:00+01:00", // Wednesday
      "maxEndTime": "2026-01-17T17:00:00+01:00" // Same day
    }
  ],
  "pinningRequested": false
}
```

**Use Case**: Planner decided this movable visit should happen on Wednesday, but hasn't assigned employee yet.

### 3. Pinned Movable Visit

**Status**: Already assigned and pinned

**Characteristics**:

- Fixed time window (minStartTime = maxStartTime)
- Assigned to employee
- Pinned (`pinningRequested: true`)
- Part of slingor (recurring pattern)

**Example**:

```json
{
  "id": "movable-visit-789",
  "timeWindows": [
    {
      "minStartTime": "2026-01-17T10:00:00+01:00", // Fixed time
      "maxEndTime": "2026-01-17T11:00:00+01:00"
    }
  ],
  "pinningRequested": true,
  "assignedEmployeeId": "employee-123",
  "minStartTravelTime": "2026-01-17T09:45:00+01:00",
  "slingaId": "slinga-456" // Now part of recurring pattern
}
```

**Use Case**: Movable visit was optimized, accepted, and pinned. Now part of weekly slinga.

---

## Pre-Planning Workflow

### Step 1: Create Movable Visit Template

**From biståndsbeslut PDF or manual entry:**

```typescript
// GraphQL mutation
mutation CreateMovableVisit($input: CreateMovableVisitInput!) {
  createMovableVisit(input: $input) {
    id
    clientId
    frequency
    timeWindows
  }
}
```

**Input**:

- Client ID
- Frequency (daily/weekly/bi-weekly/monthly)
- Preferred time band (morning/afternoon/evening)
- Required skills
- Continuity preference

### Step 2: Generate Concrete Visits

**For planning horizon:**

```typescript
// Backend generates visits for each occurrence
const visits = generateMovableVisits(
  movableVisitTemplate,
  planningWindow, // e.g., 1 month
);

// Result: Array of unassigned visits with time windows
visits.forEach((visit) => {
  visit.pinned = false;
  visit.assignedEmployeeId = null;
  visit.timeWindows = calculateTimeWindow(visit.frequency, planningWindow);
});
```

### Step 3: Pre-Planning Optimization

**With longer planning window:**

```typescript
// Use weekly/monthly planning window
const planningWindow = {
  startDate: "2026-01-15T00:00:00+01:00",
  endDate: "2026-02-15T00:00:00+01:00", // 1 month
};

// Include:
// - Existing slingor (pinned visits)
// - New movable visits (unpinned)
const timefoldInput = {
  modelInput: {
    planningWindow,
    visits: [...pinnedVisitsFromSlingor, ...newMovableVisits],
    vehicles: employees,
  },
};
```

### Step 4: Review Recommendations

**Timefold returns**:

- Recommended employee for each visit
- Recommended day/time
- Impact metrics (travel time, continuity, workload)

**UI displays**:

- Diff view (baseline vs optimized)
- Recommendations panel
- Impact metrics

### Step 5: Accept and Pin

**User accepts recommendations:**

```typescript
// GraphQL mutation
mutation AcceptPrePlanningSolution($input: AcceptSolutionInput!) {
  acceptPrePlanningSolution(input: $input) {
    scheduleId
    pinnedVisits {
      id
      assignedEmployeeId
      assignedStartTime
    }
  }
}
```

**Backend**:

1. Pin accepted visits (`pinned = true`)
2. Update slingor (add visits to recurring patterns)
3. Update movable visit defaults (if template change)

---

## Time Window Calculation

### Weekly Movable Visits

**Time Window**: Monday 07:00 → Sunday 23:00

```typescript
function calculateWeeklyTimeWindow(
  planningWindowStart: Date,
  planningWindowEnd: Date,
): TimeWindow {
  const monday = startOfWeek(planningWindowStart, { weekStartsOn: 1 });
  const sunday = addDays(monday, 6);

  return {
    minStartTime: setHours(monday, 7).toISOString(),
    maxEndTime: setHours(sunday, 23).toISOString(),
  };
}
```

### Monthly Movable Visits

**Time Window**: 1st 07:00 → Last day 23:00

```typescript
function calculateMonthlyTimeWindow(
  planningWindowStart: Date,
  planningWindowEnd: Date,
): TimeWindow {
  const firstDay = startOfMonth(planningWindowStart);
  const lastDay = endOfMonth(planningWindowEnd);

  return {
    minStartTime: setHours(firstDay, 7).toISOString(),
    maxEndTime: setHours(lastDay, 23).toISOString(),
  };
}
```

---

## Integration with Slingor

### From Movable to Slinga

**Process**:

1. Movable visit optimized and accepted
2. Visit pinned and assigned to employee
3. System detects pattern (same day/time each week)
4. Creates or updates slinga
5. Future schedules generated from slinga

**Example**:

```typescript
// After optimization, movable visit becomes:
{
  "id": "visit-123",
  "assignedEmployeeId": "employee-456",
  "assignedStartTime": "2026-01-17T10:00:00+01:00",  // Wednesday 10:00
  "pinned": true,
  "slingaId": "slinga-789"  // Added to slinga
}

// Future weeks: Visit automatically generated from slinga
```

---

## Demand & Supply Management

### Using Movable Visits

**Demand Adaptation**:

- Create movable visits for optional services
- Use priority to control assignment
- Use unused hours to fill gaps

**Supply Management**:

- Identify capacity gaps
- Suggest movable visit placements
- Balance workload across employees

**Example**:

```typescript
// Identify unused hours
const unusedHours = await getUnusedHours(organizationId, planningWindow);

// Create movable visits to fill gaps
const movableVisits = unusedHours.map((hour) => ({
  clientId: hour.clientId,
  frequency: "weekly",
  preferredTimeBand: hour.timeBand,
  priority: "10", // Lower priority (optional)
  unusedHours: true, // Flag for recapture
}));
```

---

## Best Practices

1. **Use longer planning windows** for pre-planning (weekly/monthly)
2. **Start with new movable visits** (full flexibility)
3. **Freeze to specific date** when planner decides
4. **Pin after optimization** to make part of slingor
5. **Update templates** when stable improvements found
6. **Use priority** to control assignment order
7. **Leverage unused hours** for demand/supply balance

---

## References

- [Planning Window Strategy](./PLANNING_WINDOW_STRATEGY.md)
- [Pinned Visits Guide](./PINNED_VISITS_GUIDE.md)
- [Timefold Integration](./TIMEFOLD_INTEGRATION.md)
