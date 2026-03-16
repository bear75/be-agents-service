# Backend Support for Longer Planning Windows

> **Archive notice:** This content is consolidated into [SCHEDULE_SOLUTION_ARCHITECTURE.md](SCHEDULE_SOLUTION_ARCHITECTURE.md) § Planning Window Strategy (Consolidated). Use that section as the single source of truth.

**Version:** 2.0  
**Last Updated:** 2025-12-11

---

## Summary

✅ **YES - The backend fully supports longer planning windows (weekly/monthly) for daily optimizations.**

The data model and services are designed to handle planning windows of any length. Planning windows are calculated dynamically and passed to Timefold, not stored as fixed constraints in the database.

---

## Data Model Support

### Schedules Table

The `schedules` table has flexible date fields that support multi-day planning windows:

```typescript
export const schedules = pgTable("schedules", {
  id: uuid().defaultRandom().primaryKey().notNull(),
  date: timestamp("date", { mode: "string" }).notNull(), // Primary date
  startDate: timestamp("start_date", { mode: "string" }).notNull(), // Can span multiple days
  endDate: timestamp("end_date", { mode: "string" }).notNull(), // Can span multiple days
  scheduleTimespan: scheduleTimespan("schedule_timespan")
    .notNull()
    .default("daily"), // "daily" | "weekly" | "monthly" | "consolidated"
  // ... other fields
});
```

**Key Points**:

- `startDate` and `endDate` are **timestamps** (not just dates) → can span multiple days
- `scheduleTimespan` enum supports "daily", "weekly", "monthly", "consolidated"
- No hard-coded single-day limitation

### Planning Window Storage

**Planning windows are NOT stored in the database** - they are:

1. **Calculated dynamically** from date ranges or visit data
2. **Passed to Timefold** in the `modelInput.planningWindow` field
3. **Flexible** - can be any length (daily, weekly, monthly)

---

## Backend Service Support

### 1. Pre-Planning Orchestrator

**File**: `src/features/scheduling/services/preplanning/pre-planning-orchestrator.ts`

**Current Implementation**:

```typescript
// Planning window calculated from date range
const planningWindow: PlanningWindow = {
  start: parseISO(request.dateRangeStart + "T06:00:00.000Z"),
  end: parseISO(request.dateRangeEnd + "T23:00:00.000Z"), // Can be any date range!
};
```

**Supports**:

- ✅ Any date range (daily, weekly, monthly)
- ✅ Calculates planning window from `dateRangeStart` and `dateRangeEnd`
- ✅ No restrictions on window length

### 2. Carefox Mapper

**File**: `src/features/scheduling/services/mappers/carefox-mapper-shared.ts`

**Current Implementation**:

```typescript
static calculatePlanningWindow(
  visits: any[],
  employees: any[],
  date?: string,
  logPrefix?: string,
): { startDate: string; endDate: string } {
  // Detects single-day vs multi-day schedules
  const isSingleDay = /* checks if visits span multiple days */;

  if (isSingleDay) {
    // Single-day: Use target date with buffered hours
  } else {
    // MULTI-DAY: Use actual dates with buffered times
    earliestDate = new Date(earliestTime - totalBufferMs);
    latestDate = new Date(latestTime + totalBufferMs);
  }
}
```

**Supports**:

- ✅ Detects single-day vs multi-day schedules
- ✅ Calculates planning window from visit/employee data
- ✅ Handles multi-day schedules correctly

### 3. Pattern Time Calculator

**File**: `src/features/scheduling/services/pattern-detection/pattern-time-calculator.ts`

**Current Implementation**:

```typescript
export function calculatePatternTimeWindows(
  frequency: "weekly" | "bi-weekly" | "monthly",
  referenceDate: Date,
  duration: number,
  dateFrom: string, // Planning window start
  dateTo: string, // Planning window end
): TimeWindow {
  // Calculates aligned planning windows:
  // - Weekly: Monday 06:00 -> Sunday 23:00
  // - Monthly: 1st 06:00 -> Last day 23:00
}
```

**Supports**:

- ✅ Weekly planning windows (Monday-Sunday)
- ✅ Monthly planning windows (1st - last day)
- ✅ Calendar-aligned boundaries

---

## Timefold Integration

### Planning Window in Timefold Input

Planning windows are passed to Timefold in the standard format:

```typescript
interface TimefoldPlanningWindow {
  startDate: string; // ISO 8601 Date format "YYYY-MM-DD"
  endDate: string; // ISO 8601 Date format "YYYY-MM-DD"
}

interface TimefoldInput {
  modelInput: {
    planningWindow?: TimefoldPlanningWindow;
    visits: TimefoldVisit[];
    vehicles: TimefoldVehicle[];
  };
}
```

**No restrictions** - Timefold accepts planning windows of any length.

---

## Current Usage Patterns

### Pattern 1: Pre-Planning (Already Supports Longer Windows)

```typescript
// Pre-planning orchestrator
const planningWindow = {
  start: parseISO(request.dateRangeStart + "T06:00:00.000Z"),
  end: parseISO(request.dateRangeEnd + "T23:00:00.000Z"), // Can be 7 days, 30 days, etc.
};
```

**Status**: ✅ Already supports weekly/monthly windows

### Pattern 2: Daily Schedule Creation (Needs Update)

```typescript
// Carefox mapper for daily schedules
const planningWindow = CarefoxMapperShared.calculatePlanningWindow(
  visits,
  employees,
  date, // Single date
);
```

**Current Behavior**: Calculates single-day window from visit data

**To Support Longer Windows**: Pass date range instead of single date, or explicitly set longer window

---

## Implementation Recommendations

### For Daily Optimizations with Weekly Windows

**Option 1: Update Daily Schedule Creation**

Modify the daily schedule creation to accept an optional planning window:

```typescript
interface CreateDailyScheduleRequest {
  targetDate: string; // Primary date to optimize
  planningWindowDays?: number; // Optional: default 1, can be 7 for weekly
}

// In service:
const planningWindow = {
  startDate: targetDate,
  endDate: addDays(targetDate, planningWindowDays || 1).toISOString(),
};
```

**Option 2: Use Pre-Planning Service**

For daily optimizations with weekly context, use the pre-planning service:

```typescript
// Instead of daily schedule creation
await runPrePlanningInBackground({
  dateRangeStart: targetDate,
  dateRangeEnd: addDays(targetDate, 7).toISOString(), // 7-day window
  // ... other params
});
```

### For Cross-Area Optimization

**Current Support**: ✅ Already supported

The backend can include multiple service areas in a single optimization:

```typescript
// Service area filtering is optional
const visits = await getVisitsForServiceAreas(
  organizationId,
  [serviceAreaId1, serviceAreaId2], // Multiple areas
  planningWindow,
);
```

---

## Verification Checklist

- [x] **Schedules table** supports multi-day `startDate`/`endDate`
- [x] **Pre-planning orchestrator** accepts any date range
- [x] **Carefox mapper** detects and handles multi-day schedules
- [x] **Pattern calculator** supports weekly/monthly windows
- [x] **Timefold integration** accepts planning windows of any length
- [ ] **Daily schedule creation** should be updated to support optional longer windows (recommended enhancement)

---

## Conclusion

**The backend architecture fully supports longer planning windows.** The main enhancement needed is:

1. **Update daily schedule creation** to optionally use longer planning windows (7 days for daily, 2 weeks for weekly)
2. **Document the pattern** for using longer windows in daily optimizations
3. **Update UI** to allow planners to specify planning window length

The data model, services, and Timefold integration are already capable of handling this strategy.

---

## References

- [Planning Window Strategy](./PLANNING_WINDOW_STRATEGY.md) - Strategy document
- [Pre-Planning Orchestrator](../../src/features/scheduling/services/preplanning/pre-planning-orchestrator.ts)
- [Carefox Mapper](../../src/features/scheduling/services/mappers/carefox-mapper-shared.ts)
- [Pattern Time Calculator](../../src/features/scheduling/services/pattern-detection/pattern-time-calculator.ts)
