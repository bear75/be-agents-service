# Timefold Pinned Visits Guide

## Overview

This guide explains how to use Timefold's `pinned` flag for two key scenarios:

1. **Pre-planning with movable visits** (monthly/weekly optimization)
2. **Fine-tuning existing solutions** (with some assigned visits pinned)

## Key Concepts

### Timefold Visit Classification

According to [Timefold's official documentation](https://docs.timefold.ai/field-service-routing/latest/visit-service-constraints/movable-visits-and-multi-day-schedules):

#### Movable vs Non-Movable Visits

- **Non-movable**: Time window(s) on a **single day** → visit cannot be scheduled on another day
- **Movable**: Time window(s) that **span multiple days** → visit can be scheduled on different days

#### Mandatory vs Optional Visits

According to [Timefold's priority and optional visits docs](https://docs.timefold.ai/field-service-routing/latest/visit-service-constraints/priority-visits-and-optional-visits):

- **Mandatory**: Time window **ends within** the planning window → must be assigned
- **Optional**: Time window **ends outside** the planning window → can be left unassigned

**Note**: This is determined by the `planningWindow` in the input, not an explicit `optional` flag (though the API does support an `optional` field for explicit control).

### Timefold Visit States

| State                | `pinningRequested` | Time Window           | Planning Window | Assigned? | Behavior                                                                        |
| -------------------- | ------------------ | --------------------- | --------------- | --------- | ------------------------------------------------------------------------------- |
| **Non-movable**      | `false`            | Single day            | Within          | No        | Must be assigned on that day                                                    |
| **Movable (new)**    | `false`            | Multiple days         | Overlaps        | No        | Solver can assign anywhere in window                                            |
| **Movable (frozen)** | `false`            | Single day (narrowed) | Within          | No        | Must be assigned on that day, solver chooses employee/time                      |
| **Pinned assigned**  | `true`             | Fixed (min=max)       | N/A             | **Yes**   | Keep existing assignment (requires `minStartTravelTime` from previous solution) |
| **Optional**         | `false`            | Any                   | Ends outside    | No        | Can be skipped if not efficient                                                 |

### Important Distinctions

1. **`pinningRequested` vs `optional`**:
   - `pinningRequested: true` = **Keep existing assignment** (employee + time fixed) - **only works for already assigned visits**
   - `optional: true` OR time window ends outside planning window = **Can be left unassigned**
   - These are **independent** - a visit can be pinned AND optional

2. **Movable visits are determined by time window span**:
   - Single day time window = **non-movable** (cannot move to another day)
   - Multi-day time window = **movable** (can be scheduled on different days)
   - Use soft constraint "Prefer visits scheduled to the earliest day" to schedule movable visits early

3. **Mandatory vs Optional is based on planning window**:
   - If time window `maxEndTime` is **within** `planningWindow.endDate` → **mandatory**
   - If time window `maxEndTime` is **after** `planningWindow.endDate` → **optional**
   - The `Require scheduling mandatory visits` constraint penalizes unassigned mandatory visits

4. **Freezing a movable visit**:
   - Limits time window to a **single day** (makes it non-movable)
   - Does NOT make it pinned (still unassigned)
   - Does NOT make it optional (still mandatory if within planning window)
   - Solver must assign it on that date, but can choose employee/time

5. **Pinning requires previous solution**:
   - `pinningRequested: true` **only works** if visit was already assigned in a previous solution
   - Must include `minStartTravelTime` from the previous solution's output
   - Must include the visit in the vehicle shift's `itinerary` from previous solution

---

## Planning Window and Mandatory/Optional Behavior

According to [Timefold's documentation](https://docs.timefold.ai/field-service-routing/latest/visit-service-constraints/priority-visits-and-optional-visits), the `planningWindow` determines which visits are mandatory vs optional:

```json
{
  "modelInput": {
    "planningWindow": {
      "startDate": "2026-01-15T00:00:00+01:00",
      "endDate": "2026-01-16T00:00:00+01:00" // Single day planning window
    },
    "visits": [
      {
        "id": "Visit A",
        "timeWindows": [
          {
            "minStartTime": "2026-01-15T09:00:00+01:00",
            "maxEndTime": "2026-01-15T17:00:00Z" // Ends WITHIN planning window
          }
        ]
        // → MANDATORY (must be assigned)
      },
      {
        "id": "Visit B",
        "timeWindows": [
          {
            "minStartTime": "2026-01-15T09:00:00+01:00",
            "maxEndTime": "2026-01-20T17:00:00Z" // Ends OUTSIDE planning window
          }
        ]
        // → OPTIONAL (can be skipped)
      }
    ]
  }
}
```

**Rules**:

- **Mandatory**: `maxEndTime` ≤ `planningWindow.endDate` → must be assigned
- **Optional**: `maxEndTime` > `planningWindow.endDate` → can be left unassigned
- The `Require scheduling mandatory visits` constraint penalizes unassigned mandatory visits
- The `Prefer scheduling optional visits` soft constraint encourages assigning optional visits if capacity allows

---

## Scenario 1: Pre-Planning Monthly/Weekly with Movable Visits

### Goal

Plan January 1-30, 2026 with movable visits that have different lifecycle statuses.

### Movable Visit Lifecycle States

#### 1. New Movable Visit (No Limits)

**Behavior**: Multi-day time window, solver has maximum flexibility

```json
{
  "id": "movable-visit-123",
  "timeWindows": [
    {
      "minStartTime": "2026-01-01T06:00:00+01:00", // Start of month
      "maxEndTime": "2026-01-30T23:00:00+01:00" // End of month (spans multiple days = movable)
    }
  ],
  "pinningRequested": false
}
```

**Key Points**:

- Time window spans **multiple days** → Timefold treats it as **movable**
- If `planningWindow.endDate` is `2026-01-30T23:59:59+01:00` or later → **mandatory** (must be assigned)
- If `planningWindow.endDate` is before `2026-01-30T23:00:00+01:00` → **optional** (can be skipped)
- Use soft constraint "Prefer visits scheduled to the earliest day" to schedule early

**Use Case**: New biståndsbeslut visit that can happen any day in January.

---

#### 2. Existing Movable Visit (Frozen to Single Day)

**Behavior**: Time window narrowed to single day → becomes **non-movable**, but still unassigned

```json
{
  "id": "movable-visit-456-frozen-2026-01-15",
  "timeWindows": [
    {
      "minStartTime": "2026-01-15T08:00:00+01:00", // Single day
      "maxEndTime": "2026-01-15T17:00:00+01:00" // Same day (single day = non-movable)
    }
  ],
  "pinningRequested": false // NOT pinned - still unassigned!
}
```

**Key Points**:

- Time window is **single day** → Timefold treats it as **non-movable** (cannot move to another day)
- `pinningRequested: false` because the visit is **not yet assigned**
- If `planningWindow` includes Jan 15 → **mandatory** (must be assigned)
- Solver must assign it on Jan 15, but can choose employee/time

**Use Case**: Planner decided this movable visit should happen on Jan 15, but hasn't assigned employee yet.

---

#### 3. Recurring Movable Visit (Daily Schedule Optimization)

**Behavior**: Optimize daily schedule with movable visits added for specific time window per date

**Step 1: Initial Optimization (Unassigned, Single Day Window)**

```json
{
  "id": "movable-visit-789",
  "timeWindows": [
    {
      "minStartTime": "2026-01-20T10:00:00+01:00", // Single day
      "maxEndTime": "2026-01-20T11:00:00+01:00" // Same day (non-movable)
    }
  ],
  "pinningRequested": false // Not pinned - not yet assigned
}
```

**Step 2: After First Optimization - Pin the Assignment**
Once the solver assigns the visit, you can pin it for the next optimization:

```json
{
  "id": "movable-visit-789",
  "timeWindows": [
    {
      "minStartTime": "2026-01-20T10:00:00+01:00", // Fixed time from solution
      "maxEndTime": "2026-01-20T11:00:00+01:00"
    }
  ],
  "pinningRequested": true, // Pin the assignment
  "minStartTravelTime": "2026-01-20T09:45:00+01:00" // From previous solution
}
```

**Step 3: If Efficiency/Supply-Demand Not Satisfying - Unpin and Re-optimize**

```json
{
  "id": "movable-visit-789",
  "timeWindows": [
    {
      "minStartTime": "2026-01-20T08:00:00+01:00", // Wider window
      "maxEndTime": "2026-01-20T17:00:00+01:00"
    }
  ],
  "pinningRequested": false // Unpinned - allow solver to move
}
```

**Use Case**: Daily schedule optimization where movable visits are initially unassigned, then pinned after first optimization, but can be unpinned for revision if efficiency is low.

---

## Scenario 2: Fine-Tuning Existing Solutions

### Goal

Fine-tune a schedule where certain assigned visits are pinned (cannot be changed).

### Pinned Assigned Visit

**Behavior**: Keep existing assignment (employee + time) fixed

According to [Timefold's pinning documentation](https://docs.timefold.ai/field-service-routing/latest/real-time-planning/real-time-planning-pinning-visits), pinning requires:

1. The visit must be **already assigned** in a previous solution
2. Include the visit in the vehicle shift's `itinerary` from previous solution
3. Set `pinningRequested: true`
4. Include `minStartTravelTime` from previous solution output

```json
{
  "modelInput": {
    "vehicles": [
      {
        "id": "employee-123",
        "shifts": [
          {
            "id": "shift-2026-01-15",
            "itinerary": [
              {
                "id": "visit-abc",
                "kind": "VISIT"
              }
            ]
          }
        ]
      }
    ],
    "visits": [
      {
        "id": "visit-abc",
        "timeWindows": [
          {
            "minStartTime": "2026-01-15T10:00:00+01:00", // Fixed time from previous solution
            "maxEndTime": "2026-01-15T11:00:00+01:00"
          }
        ],
        "pinningRequested": true, // Pin the assignment
        "minStartTravelTime": "2026-01-15T09:45:00+01:00" // From previous solution output
      }
    ]
  }
}
```

**Key Points**:

- `pinningRequested: true` tells Timefold to **preserve** the assignment from the previous solution
- Must include visit in vehicle shift's `itinerary` from previous solution
- `minStartTravelTime` must be from the previous solution's output
- Time window should match the assigned time from previous solution

**Use Case**: Fine-tuning a schedule while keeping certain critical visits fixed, or real-time planning where some visits cannot be rescheduled.

---

## Real-time planning (preview): from-patch endpoint

Timefold offers a **from-patch** API (preview) for real-time planning. Instead of sending a full new `modelInput`, you send a **patch** (JSON Patch operations) applied to the latest revision’s input. That keeps the current solution as the base and only applies changes (e.g. add visit, pin visits, remove unused employees).

### Endpoint and body

- **Endpoint:** `POST /v1/route-plans/{id}/from-patch`
- **Body:** `{ "config": { "run": { "name": "..." } }, "patch": [ { "op": "add"|"remove"|..., "path": "...", "value": ... } ] }`
- **Paths:** Relative to `modelInput` (e.g. `/freezeTime`, `/visits/[id=Visit E]/pinningRequested`, `/visits/-`, `/vehicles/[id=Route A2]`).

### Why use from-patch for “remove unused employees”

If you **reduce** the input (e.g. only 31 vehicles and 143 shifts that had visits) and **re-solve** by posting a new route plan, the solver can produce a **different** allocation and leave visits **unassigned** (we observed 29 unassigned visits). To **keep the same assignment** and only drop unused employees/shifts, use **from-patch**:

1. Solve once with full fixed-cost input → get solution (e.g. 31 vehicles used, 143 shifts with visits).
2. Build a **patch** that:
   - **Pins** all assigned visits (`pinningRequested: true` and `minStartTravelTime` from the solution for each).
   - **Removes** unused vehicles (and optionally unused shifts) via `remove` ops on `/vehicles/[id=...]` (and shifts as needed).
3. **POST** to `POST /v1/route-plans/{id}/from-patch`. The new revision keeps the same assignment and no longer includes the removed employees/shifts.

### Documentation and access

- [Real-time planning (preview)](https://docs.timefold.ai/field-service-routing/latest/real-time-planning/preview/real-time-planning) – overview and process.
- [Real-time planning: pinning visits (preview)](https://docs.timefold.ai/field-service-routing/latest/real-time-planning/preview/real-time-planning-pinning-visits) – pinning with from-patch and example `patch` payloads (add visit, add `freezeTime`, add `pinningRequested`).

The Patch feature is **preview only**. For early access, [contact Timefold](https://timefold.ai/contact).

See also `apps/dashboard/test_data_import/APPROACH_FROM_SOLUTION_PATCH.md` for the “reduce employees without re-solving” flow and the 29 unassigned-visits outcome when re-solving on reduced input.

---

## Common Misconceptions

### ❌ Incorrect: "Freezing a movable visit makes it pinned"

**Wrong**:

```json
{
  "id": "movable-visit-frozen",
  "timeWindows": [
    /* narrow window */
  ],
  "pinningRequested": true, // ❌ WRONG - visit is not assigned yet!
  "assignedVehicleId": null // No assignment to pin
}
```

**Correct**:

```json
{
  "id": "movable-visit-frozen",
  "timeWindows": [
    /* narrow window for specific date */
  ],
  "pinningRequested": false, // ✅ Correct - still unassigned
  "optional": false // Mandatory for this date
}
```

### ❌ Incorrect: "Movable visit with wide time window won't be assigned for a one-day optimization"

**Reality**: According to Timefold's behavior:

- If the time window **overlaps** with the planning window → Timefold will try to assign it
- If `maxEndTime` is **within** `planningWindow.endDate` → **mandatory** (must be assigned)
- If `maxEndTime` is **after** `planningWindow.endDate` → **optional** (can be skipped)

**Example**: Optimizing Jan 15 only (`planningWindow.endDate = 2026-01-16T00:00:00+01:00`), but movable visit has window Jan 1-30:

- If `maxEndTime = 2026-01-30T23:00:00+01:00` → **optional** (ends after planning window)
- Timefold may still try to assign it if capacity allows (soft constraint)
- If it doesn't fit (e.g., no available employees), it will be left unassigned (no hard constraint violation)

**Solution**: If you want to exclude a movable visit from a specific date optimization:

1. Set time window `maxEndTime` to be **after** `planningWindow.endDate` → makes it optional
2. Or filter it out of the input entirely
3. Or set time window that doesn't overlap with planning window

### ❌ Incorrect: "Pinning works for unassigned visits"

**Reality**: According to [Timefold's pinning documentation](https://docs.timefold.ai/field-service-routing/latest/real-time-planning/real-time-planning-pinning-visits):

- `pinningRequested: true` **only works** if the visit was already assigned in a previous solution
- Must include the visit in the vehicle shift's `itinerary` from previous solution
- Must include `minStartTravelTime` from previous solution output
- For unassigned visits, use time window constraints instead

**Correct Approach**:

- **Unassigned visit**: Use narrow time window to force specific date/time
- **Assigned visit**: Use `pinningRequested: true` + `itinerary` + `minStartTravelTime` to preserve assignment

---

## Implementation Patterns

### Pattern 1: Pre-Planning with Movable Visits

```typescript
function buildPrePlanningInput(
  planningWindow: { start: string; end: string },
  movableVisits: MovableVisit[],
): TimefoldInput {
  const visits: TimefoldVisit[] = [];

  for (const movable of movableVisits) {
    if (movable.lifecycleStatus === "new") {
      // New movable: full time window
      visits.push({
        id: movable.id,
        timeWindows: [
          {
            minStartTime: planningWindow.start,
            maxStartTime: planningWindow.end,
            maxEndTime: addDuration(planningWindow.end, movable.duration),
          },
        ],
        pinningRequested: false,
        optional: false,
      });
    } else if (movable.lifecycleStatus === "frozen") {
      // Frozen movable: narrow time window for specific date
      visits.push({
        id: `${movable.id}-frozen-${movable.frozenDate}`,
        timeWindows: [
          {
            minStartTime: `${movable.frozenDate}T08:00:00+01:00`,
            maxStartTime: `${movable.frozenDate}T16:00:00+01:00`,
            maxEndTime: `${movable.frozenDate}T17:00:00+01:00`,
          },
        ],
        pinningRequested: false, // Still unassigned!
        optional: false,
      });
    } else if (movable.lifecycleStatus === "pinned") {
      // Pinned movable: already assigned, keep assignment
      visits.push({
        id: movable.id,
        timeWindows: [
          {
            minStartTime: movable.assignedStartTime,
            maxStartTime: movable.assignedStartTime, // Fixed
            maxEndTime: movable.assignedEndTime,
          },
        ],
        pinningRequested: true, // Pin the assignment
        minStartTravelTime: subtractDuration(
          movable.assignedStartTime,
          "PT15M",
        ),
      });
    }
  }

  return { visits /* ... */ };
}
```

### Pattern 2: Fine-Tuning with Pinned Visits

```typescript
function buildFineTuningInput(
  existingSolution: TimefoldSolution,
  visitsToPin: string[],
  visitsToUnpin: string[],
): TimefoldInput {
  const visits: TimefoldVisit[] = [];

  for (const assignment of existingSolution.visitAssignments) {
    const visit = {
      id: assignment.visitId,
      timeWindows: [
        {
          minStartTime: assignment.startTime,
          maxStartTime: assignment.startTime, // Fixed
          maxEndTime: assignment.endTime,
        },
      ],
      pinningRequested: visitsToPin.includes(assignment.visitId),
      minStartTravelTime: subtractDuration(assignment.startTime, "PT15M"),
    };

    visits.push(visit);
  }

  return { visits /* ... */ };
}
```

### Pattern 3: Daily Schedule with Movable Visits (Revision Flow)

```typescript
async function optimizeDailySchedule(
  date: string,
  pinnedMovableVisits: MovableVisit[],
  unpinnedMovableVisits: MovableVisit[],
): Promise<TimefoldSolution> {
  // Step 1: Build input with pinned movable visits
  const input = {
    visits: [
      ...pinnedMovableVisits.map((mv) => ({
        id: mv.id,
        timeWindows: [
          /* fixed time window */
        ],
        pinningRequested: true, // Pin the assignment
      })),
      ...unpinnedMovableVisits.map((mv) => ({
        id: mv.id,
        timeWindows: [
          /* flexible time window */
        ],
        pinningRequested: false,
      })),
    ],
  };

  // Step 2: Optimize
  const solution = await timefold.optimize(input);

  // Step 3: Check efficiency
  const efficiency = calculateEfficiency(solution);

  if (efficiency < 0.75) {
    // Step 4: Unpin and re-optimize
    return await optimizeDailySchedule(
      date,
      [], // No pinned visits
      [...pinnedMovableVisits, ...unpinnedMovableVisits], // All unpinned
    );
  }

  return solution;
}
```

---

## Summary Table

| Scenario        | `pinningRequested` | Time Window | Planning Window                         | Assigned? | Movable? | Mandatory?                                 | Behavior                                                               |
| --------------- | ------------------ | ----------- | --------------------------------------- | --------- | -------- | ------------------------------------------ | ---------------------------------------------------------------------- |
| New movable     | `false`            | Multi-day   | Overlaps                                | No        | Yes      | If `maxEndTime` ≤ `planningWindow.endDate` | Solver assigns anywhere in window                                      |
| Frozen movable  | `false`            | Single day  | Within                                  | No        | No       | If `maxEndTime` ≤ `planningWindow.endDate` | Solver must assign on date, chooses employee/time                      |
| Pinned assigned | `true`             | Fixed       | N/A                                     | **Yes**   | N/A      | N/A                                        | Keep existing assignment (requires `itinerary` + `minStartTravelTime`) |
| Optional visit  | `false`            | Any         | `maxEndTime` > `planningWindow.endDate` | No        | Depends  | No                                         | Can be skipped if not efficient                                        |

---

## Key Takeaways

1. **Movable vs Non-Movable**: Determined by whether time window spans **multiple days** (movable) or **single day** (non-movable)

2. **Mandatory vs Optional**: Determined by `planningWindow`:
   - **Mandatory**: `maxEndTime` ≤ `planningWindow.endDate`
   - **Optional**: `maxEndTime` > `planningWindow.endDate`

3. **`pinningRequested: true`** only works for **already assigned visits**:
   - Requires visit in vehicle shift's `itinerary` from previous solution
   - Requires `minStartTravelTime` from previous solution output
   - Preserves employee + time assignment

4. **Freezing a movable visit** = narrow time window to **single day** (makes it non-movable) + `pinningRequested: false` (still unassigned)

5. **For daily optimization with wide movable windows**:
   - Set `maxEndTime` **after** `planningWindow.endDate` to make it optional
   - Or filter it out of the input entirely

6. **Use `freezeTime`** for real-time planning to automatically pin visits before a certain time

7. **Use `movableOccupationRatioThreshold`** to control percentage of shift for movable visits

---

---

## Advanced Features

### FreezeTime (Real-Time Planning)

According to [Timefold's pinning documentation](https://docs.timefold.ai/field-service-routing/latest/real-time-planning/real-time-planning-pinning-visits), `freezeTime` automatically pins visits:

```json
{
  "modelInput": {
    "freezeTime": "2026-01-15T12:00:00+01:00",
    "pinNextVisitDuringFreeze": "ALWAYS" // or "NEVER"
  }
}
```

**Behavior**:

- **`ALWAYS` (default)**: Pins all visits that are:
  - Already completed
  - Already started
  - Technicians are already traveling to (before `freezeTime`)
- **`NEVER`**: Only pins visits that are completed or started (not those being traveled to)

**Use Case**: Real-time planning where you want to preserve visits that have already started or are in progress.

### Movable Occupation Ratio

Control the percentage of a vehicle shift that can be assigned movable visits:

```json
{
  "vehicles": [
    {
      "shifts": [
        {
          "id": "shift-2026-01-15",
          "movableOccupationRatioThreshold": 0.5 // 50% of shift for movable visits
        }
      ]
    }
  ]
}
```

**Values**:

- `0.0` = 0% of shift for movable visits
- `0.5` = 50% of shift for movable visits
- `1.0` = 100% of shift for movable visits

**Use Case**: Balance movable and non-movable visits to retain flexibility for new non-movable visits and real-time planning.

---

---

## Planning Window Strategy

**Important**: Caire uses **longer planning windows** (weekly/monthly) for daily optimizations to maximize optimization quality. See [Planning Window Strategy](./PLANNING_WINDOW_STRATEGY.md) for details.

**Key Points**:

- Use 7-day planning window for daily optimizations
- Include multiple service areas for cross-area optimization
- More information = better optimization decisions
- Filter results to show target date after optimization

---

## References

- [Planning Window Strategy](./PLANNING_WINDOW_STRATEGY.md) - Caire's planning window approach
- [Timefold Movable Visits Documentation](https://docs.timefold.ai/field-service-routing/latest/visit-service-constraints/movable-visits-and-multi-day-schedules)
- [Timefold Priority and Optional Visits](https://docs.timefold.ai/field-service-routing/latest/visit-service-constraints/priority-visits-and-optional-visits)
- [Timefold Pinning Visits (Real-Time Planning)](https://docs.timefold.ai/field-service-routing/latest/real-time-planning/real-time-planning-pinning-visits)
- [Caire Pre-Planning Orchestrator](../../src/features/scheduling/services/preplanning/pre-planning-orchestrator.ts)
- [Visit Pinning Service](../../src/features/scheduling/services/slinga/visit-pinning.service.ts)
