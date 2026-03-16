# Timefold Integration Guide

**Version:** 2.0  
**Last Updated:** 2025-12-11

---

## Overview

Caire uses **Timefold Field Service Routing API** as the optimization engine. This document covers the complete integration, including API endpoints, data formats, optimization workflows, and best practices.

**Key Concepts:**

- **INPUT**: Problem definition (visits, employees, constraints)
- **OUTPUT**: Solution (assignments, metrics)
- **Planning Windows**: Flexible date ranges for optimization
- **Pinning**: Preserve existing assignments
- **from-patch**: Incremental optimization

---

## Timefold API Endpoints

### 1. Full Solve Endpoint

**Endpoint**: `POST /api/models/field-service-routing/v1/route-plans`

**Use When**:

- Creating new schedule from scratch
- Full optimization (all visits movable)
- Pre-planning with movable visits

**Request**:

```json
{
  "config": {
    "run": {
      "name": "Daily Schedule Optimization"
    }
  },
  "modelInput": {
    "planningWindow": {
      "startDate": "2026-01-15T00:00:00+01:00",
      "endDate": "2026-01-22T00:00:00+01:00"  // 7-day window for daily optimization
    },
    "visits": [...],
    "vehicles": [...]
  }
}
```

**Response**:

```json
{
  "metadata": {
    "id": "job_123",
    "status": "SOLVING",
    ...
  }
}
```

### 2. From-Patch Endpoint

**Endpoint**: `POST /api/models/field-service-routing/v1/route-plans/<datasetId>/from-patch`

**Use When**:

- Fine-tuning existing schedule
- Adding new visits to existing schedule
- Real-time disruptions (re-optimize remaining day)

**Request**:

```json
{
  "patch": [
    {
      "op": "add",
      "path": "/visits",
      "value": {
        "id": "new-visit-123",
        "location": [59.254417, 18.081677],
        "serviceDuration": "PT30M",
        "timeWindows": [...],
        "pinningRequested": false
      }
    }
  ],
  "modelInput": {
    "visits": [/* only new visits */],
    "vehicles": [/* existing vehicles with itinerary */]
  }
}
```

**Benefits**:

- Faster optimization (incremental)
- Preserves existing assignments (pinned)
- Less data transfer

---

## Planning Window Strategy

### Using Longer Windows for Daily Optimizations

**Recommended**: Use 7-day planning window for daily optimizations.

```typescript
// Calculate planning window
const planningWindow = {
  startDate: targetDate, // Target day
  endDate: addDays(targetDate, 7).toISOString(), // 7 days later
};

// Include all visits in window
const visits = await getVisitsForDateRange(
  organizationId,
  planningWindow.startDate,
  planningWindow.endDate,
);

// Send to Timefold
const timefoldInput = {
  modelInput: {
    planningWindow,
    visits,
    vehicles: employees,
  },
};
```

**Benefits**:

- Movable visits can be optimally placed across week
- Cross-area optimization possible
- Better unused hours recapture
- More context for solver

**After Optimization**: Filter results to show only target date.

See [Planning Window Strategy](./PLANNING_WINDOW_STRATEGY.md) for details.

---

## Visit Classification

### Mandatory vs Optional

Determined by `planningWindow`:

- **Mandatory**: `maxEndTime` ≤ `planningWindow.endDate` → Must be assigned
- **Optional**: `maxEndTime` > `planningWindow.endDate` → Can be skipped

### Movable vs Non-Movable

Determined by time window span:

- **Non-movable**: Time window on **single day** → Cannot move to another day
- **Movable**: Time window **spans multiple days** → Can be scheduled on different days

### Pinned vs Unpinned

- **Pinned**: `pinningRequested: true` + visit in vehicle `itinerary` + `minStartTravelTime` → Keep existing assignment
- **Unpinned**: `pinningRequested: false` → Solver can assign/move

See [Pinned Visits Guide](./PINNED_VISITS_GUIDE.md) for complete details.

---

## Optimization Workflows

### Workflow 1: Daily Schedule Optimization

**Input**:

- Existing schedule with pinned visits
- Some unpinned visits (manual edits or new)
- 7-day planning window

**Process**:

1. Reconstruct INPUT from database
2. Include all visits in planning window
3. Send to Timefold (full solve or from-patch)
4. Receive solution
5. Process OUTPUT to solution tables
6. Filter results to show target date

**Timefold Request**:

```json
{
  "modelInput": {
    "planningWindow": {
      "startDate": "2026-01-15T00:00:00+01:00",
      "endDate": "2026-01-22T00:00:00+01:00"
    },
    "visits": [
      {
        "id": "visit-pinned-123",
        "pinningRequested": true,
        "minStartTravelTime": "2026-01-15T09:45:00+01:00",
        "timeWindows": [
          {
            "minStartTime": "2026-01-15T10:00:00+01:00",
            "maxEndTime": "2026-01-15T11:00:00+01:00"
          }
        ]
      },
      {
        "id": "visit-movable-456",
        "pinningRequested": false,
        "timeWindows": [
          {
            "minStartTime": "2026-01-15T08:00:00+01:00",
            "maxEndTime": "2026-01-22T17:00:00+01:00" // Spans full week
          }
        ]
      }
    ],
    "vehicles": [
      {
        "id": "employee-123",
        "shifts": [
          {
            "id": "shift-2026-01-15",
            "itinerary": [{ "id": "visit-pinned-123", "kind": "VISIT" }]
          }
        ]
      }
    ]
  }
}
```

### Workflow 2: Pre-Planning Optimization

**Input**:

- Existing slingor (pinned visits)
- New movable visits (unpinned)
- Longer planning window (weekly/monthly)

**Process**:

1. Load consolidated schedule
2. Include all pinned visits (from slingor)
3. Include new movable visits (unpinned)
4. Send to Timefold with longer planning window
5. Receive recommendations
6. User accepts → Pin approved visits

### Workflow 3: Real-Time Disruption

**Input**:

- Current schedule
- Cancellations or new urgent visits
- Freeze time (visits before this time are pinned)

**Process**:

1. Pin visits before `freezeTime`
2. Unpin remaining visits
3. Add cancellations/urgent visits
4. Send to Timefold (from-patch)
5. Receive re-optimized solution
6. Auto-approve or review

---

## Constraint Handling

### Hard Constraints

- **Time windows**: Visits must be scheduled within `minStartTime` - `maxEndTime`
- **Skills**: Employee must have required skills
- **Pinned visits**: Cannot be moved if `pinningRequested: true`
- **Shift hours**: Cannot exceed employee shift boundaries

### Soft Constraints

- **Travel time**: Minimize total travel
- **Efficiency**: Maximize service hours / shift hours
- **Continuity**: Prefer same caregiver for recurring visits
- **Priority**: Higher priority visits scheduled first
- **Unused hours**: Recapture cancelled hours

### Constraint Weights

Configured in Timefold configuration:

```json
{
  "config": {
    "constraintWeights": {
      "minimizeTravelTime": 3,
      "balanceTimeUtilization": 3,
      "minimizeShiftCosts": 1,
      "preferSchedulingOptionalVisits": 1
    }
  }
}
```

---

## Solution Processing

### OUTPUT Structure

```json
{
  "modelOutput": {
    "vehicles": [
      {
        "id": "employee-123",
        "shifts": [
          {
            "id": "shift-2026-01-15",
            "itinerary": [
              {
                "id": "visit-123",
                "kind": "VISIT",
                "arrivalTime": "2026-01-15T10:00:00+01:00",
                "startServiceTime": "2026-01-15T10:00:00+01:00",
                "departureTime": "2026-01-15T10:30:00+01:00",
                "travelTimeFromPreviousStandstill": "PT15M",
                "travelDistanceMetersFromPreviousStandstill": 5000
              }
            ],
            "metrics": {
              "totalTravelTime": "PT1H30M",
              "totalTravelDistanceMeters": 25000
            }
          }
        ]
      }
    ]
  },
  "kpis": {
    "totalTravelTime": "PT5H",
    "totalAssignedVisits": 50,
    "totalUnassignedVisits": 2,
    "assignedMandatoryVisits": 48,
    "assignedOptionalVisits": 2
  }
}
```

### Processing Steps

1. **Extract assignments**: Visit → Employee mappings
2. **Calculate metrics**: Travel time, efficiency, continuity
3. **Store to database**: Solution tables
4. **Update schedule**: Link solution to schedule

---

## Error Handling

### Common Errors

**Invalid Input**:

- Missing required fields
- Invalid time windows
- Planning window issues

**Timefold Errors**:

- Timeout (optimization too complex)
- Invalid configuration
- API rate limits

**Handling**:

- Validate input before sending
- Retry with longer timeout
- Fallback to simpler optimization
- Log errors for debugging

---

## Performance Optimization

### Optimization Time

- **Daily schedule**: <5 minutes (target)
- **Weekly pre-planning**: 10-15 minutes
- **Monthly pre-planning**: 30-60 minutes

**Factors**:

- Number of visits
- Number of employees
- Planning window length
- Constraint complexity

### Optimization Strategies

1. **Use from-patch** for incremental changes
2. **Pin more visits** to reduce search space
3. **Shorter planning windows** for faster optimization (trade-off with quality)
4. **Parallel optimization** for multiple schedules

---

## Best Practices

1. **Always use longer planning windows** for daily optimizations (7 days minimum)
2. **Include multiple service areas** for cross-area optimization
3. **Use from-patch** for fine-tuning (faster than full solve)
4. **Pin stable visits** to preserve continuity
5. **Filter results** to show target period after optimization
6. **Monitor performance** and adjust window size if needed

---

## References

- [Timefold Documentation](https://docs.timefold.ai/field-service-routing/latest)
- [Pinned Visits Guide](./PINNED_VISITS_GUIDE.md)
- [Planning Window Strategy](./PLANNING_WINDOW_STRATEGY.md)
- [Backend Architecture](./BACKEND_ARCHITECTURE.md)
