# Planning Window Strategy for Caire Optimizations

> **Archive notice:** This content is consolidated into [SCHEDULE_SOLUTION_ARCHITECTURE.md](SCHEDULE_SOLUTION_ARCHITECTURE.md) § Planning Window Strategy (Consolidated). Use that section as the single source of truth.

**Version:** 2.0  
**Last Updated:** 2025-12-11

---

## Overview

Caire uses **longer time horizons** (weekly/monthly planning windows) for daily optimizations to maximize optimization quality. This strategy leverages Timefold's ability to optimize across multiple dimensions (time, location, scope) with full context.

---

## Key Principle: More Information = Better Optimization

### Why Longer Planning Windows?

Using weekly/monthly planning windows for daily optimizations provides:

1. **Full Context for Movable Visits**
   - Movable visits with weekly/monthly time windows can be optimally placed
   - Solver can see the full time horizon and make better decisions
   - Can balance visits across the entire period, not just one day

2. **Cross-Area Optimization**
   - Multiple service areas included in single optimization
   - Solver can suggest moving clients between areas for better route efficiency
   - Better geographic optimization with full location context

3. **Unused Hours Recapture**
   - Can identify and utilize unused hours across the entire period
   - Better capacity planning with full time horizon visibility
   - More opportunities to fill gaps

4. **Priority and Demand Management**
   - Can balance priorities across the entire period
   - Better demand/supply matching with full context
   - Can suggest template changes (not just temporary fixes)

5. **Multi-Dimensional Optimization**
   - **Time dimension**: Optimize movable visits across weekly/monthly domains
   - **Location dimension**: Optimize across multiple service areas
   - **Scope dimension**: Distinguish temporary vs template changes

---

## Planning Window Strategy

### For Daily Optimizations

**Recommended Approach**: Use **weekly planning window** (7 days) even when optimizing a single day.

```json
{
  "modelInput": {
    "planningWindow": {
      "startDate": "2026-01-15T00:00:00+01:00", // Target day
      "endDate": "2026-01-22T00:00:00+01:00" // 7 days later
    },
    "visits": [
      {
        "id": "visit-daily-2026-01-15",
        "timeWindows": [
          {
            "minStartTime": "2026-01-15T08:00:00+01:00",
            "maxEndTime": "2026-01-15T17:00:00+01:00"
          }
        ]
        // → MANDATORY (ends within planning window)
      },
      {
        "id": "movable-visit-weekly",
        "timeWindows": [
          {
            "minStartTime": "2026-01-15T08:00:00+01:00",
            "maxEndTime": "2026-01-22T17:00:00+01:00" // Spans full week
          }
        ]
        // → MOVABLE (can be scheduled any day in week)
        // → OPTIONAL (ends after planning window if planning window is shorter)
      }
    ]
  }
}
```

**Benefits**:

- Daily visits are **mandatory** (must be assigned on target day)
- Movable visits can be optimally placed anywhere in the week
- Solver has full context for better decisions
- Can suggest moving visits to adjacent days if more efficient

### For Weekly Optimizations

**Recommended Approach**: Use **2-week planning window** for weekly optimizations.

```json
{
  "modelInput": {
    "planningWindow": {
      "startDate": "2026-01-15T00:00:00+01:00", // Week start
      "endDate": "2026-01-29T00:00:00+01:00" // 2 weeks later
    }
  }
}
```

**Benefits**:

- Can optimize movable visits across bi-weekly patterns
- Better continuity planning across weeks
- Can balance workload across multiple weeks

### For Monthly Optimizations

**Recommended Approach**: Use **full month planning window** for monthly optimizations.

```json
{
  "modelInput": {
    "planningWindow": {
      "startDate": "2026-01-01T00:00:00+01:00", // Month start
      "endDate": "2026-02-01T00:00:00+01:00" // Next month start
    }
  }
}
```

**Benefits**:

- Full context for monthly movable visits
- Can optimize across entire month
- Better long-term planning

---

## Multi-Dimensional Optimization with Longer Windows

### Time Dimension

With longer planning windows, Timefold can:

- **Optimize movable visits** across their full time window (weekly/monthly)
- **Balance workload** across multiple days
- **Suggest template changes** (e.g., "this movable visit works better on Tuesday instead of Thursday")

**Example**:

```json
{
  "id": "movable-cleaning-weekly",
  "timeWindows": [
    {
      "minStartTime": "2026-01-15T08:00:00+01:00", // Monday
      "maxEndTime": "2026-01-22T17:00:00+01:00" // Sunday (full week)
    }
  ],
  "priority": "10"
}
```

With a 7-day planning window, Timefold can place this visit on the most efficient day (e.g., Wednesday when employee has more capacity).

### Location Dimension

With longer planning windows, include **multiple service areas**:

```json
{
  "modelInput": {
    "planningWindow": {
      "startDate": "2026-01-15T00:00:00+01:00",
      "endDate": "2026-01-22T00:00:00+01:00"
    },
    "visits": [
      {
        "id": "visit-area-a",
        "location": [59.254417, 18.081677],
        "requiredTags": ["AreaA"]
      },
      {
        "id": "visit-area-b",
        "location": [59.264417, 18.091677],
        "requiredTags": ["AreaB"]
      }
    ]
  }
}
```

**Benefits**:

- Solver can suggest moving clients between areas for better route efficiency
- Can optimize routes across area boundaries
- Better geographic optimization

### Scope Dimension (Temporary vs Template)

With longer planning windows, distinguish:

- **Temporary changes**: Only affect the specific date (e.g., employee sick)
- **Template changes**: Should update slinga/movable visit defaults (e.g., client fits better in another area)

**Example**:

```json
{
  "id": "visit-template-change",
  "timeWindows": [
    {
      "minStartTime": "2026-01-15T10:00:00+01:00",
      "maxEndTime": "2026-01-15T11:00:00+01:00"
    }
  ],
  "pinningRequested": false, // Allow solver to suggest better time
  "tags": ["AreaA"]
}
```

If solver suggests moving to Area B or different time, this is a **template change** (update slinga/movable visit).

---

## Implementation Guidelines

### 1. Planning Window Calculation

```typescript
function calculatePlanningWindow(
  targetDate: string,
  optimizationType: "daily" | "weekly" | "monthly",
): { startDate: string; endDate: string } {
  const target = new Date(targetDate);

  switch (optimizationType) {
    case "daily":
      // Use 7-day window for daily optimization
      return {
        startDate: target.toISOString(),
        endDate: addDays(target, 7).toISOString(),
      };

    case "weekly":
      // Use 2-week window for weekly optimization
      return {
        startDate: startOfWeek(target).toISOString(),
        endDate: addWeeks(startOfWeek(target), 2).toISOString(),
      };

    case "monthly":
      // Use full month window
      return {
        startDate: startOfMonth(target).toISOString(),
        endDate: startOfNextMonth(target).toISOString(),
      };
  }
}
```

### 2. Visit Classification

With longer planning windows, visits are classified as:

- **Mandatory**: `maxEndTime` ≤ `planningWindow.endDate` → Must be assigned
- **Optional**: `maxEndTime` > `planningWindow.endDate` → Can be skipped
- **Movable**: Time window spans multiple days → Can be scheduled on different days
- **Non-movable**: Time window is single day → Cannot move to another day

### 3. Filtering Results

After optimization, filter results to show only the target period:

```typescript
function filterResultsForTargetDate(
  solution: TimefoldSolution,
  targetDate: string,
): TimefoldSolution {
  // Filter visit assignments to only include target date
  const filtered = {
    ...solution,
    vehicles: solution.vehicles.map((vehicle) => ({
      ...vehicle,
      shifts: vehicle.shifts.map((shift) => ({
        ...shift,
        itinerary: shift.itinerary.filter((visit) =>
          isSameDay(visit.startServiceTime, targetDate),
        ),
      })),
    })),
  };

  return filtered;
}
```

---

## Performance Considerations

### Optimization Time

- **Longer planning windows** = more visits to optimize = longer optimization time
- **Trade-off**: Better quality vs faster optimization
- **Recommendation**: Use 7-day window for daily, monitor performance

### Visit Count Limits

- Timefold can handle 1000+ visits efficiently
- With 7-day window, expect 7x daily visit count
- Monitor optimization time and adjust window size if needed

### Memory Usage

- Longer planning windows require more memory
- Monitor system resources
- Consider batching if memory is constrained

---

## Best Practices

1. **Always use longer planning windows** for daily optimizations (7 days minimum)
2. **Include multiple service areas** when optimizing for location dimension
3. **Filter results** to show only target period after optimization
4. **Monitor performance** and adjust window size if needed
5. **Use movable visits** with wide time windows to leverage longer horizons
6. **Distinguish temporary vs template** changes based on optimization results

---

## Examples

### Example 1: Daily Optimization with Weekly Window

**Goal**: Optimize Monday, Jan 15, 2026

**Planning Window**: Jan 15 - Jan 22 (7 days)

**Visits**:

- 50 daily visits for Jan 15 (mandatory, non-movable)
- 10 movable visits with weekly time window (movable, can be placed anywhere in week)
- 5 visits from adjacent days (optional if ends after planning window)

**Result**: Solver optimizes all visits, places movable visits optimally, suggests template changes if beneficial.

**Display**: Filter to show only Jan 15 visits in UI.

### Example 2: Cross-Area Optimization

**Goal**: Optimize Area A and Area B together

**Planning Window**: 7 days

**Visits**:

- 100 visits in Area A
- 80 visits in Area B
- 20 movable visits (can be in either area)

**Result**: Solver suggests moving 5 clients from Area A to Area B for better route efficiency (template change).

---

## References

- [Timefold Planning Window Documentation](https://docs.timefold.ai/field-service-routing/latest/user-guide/planning-window)
- [Movable Visits Guide](./MOVABLE_VISITS.md)
- [Pinned Visits Guide](./PINNED_VISITS_GUIDE.md)
- [Timefold Integration](./TIMEFOLD_INTEGRATION.md)
