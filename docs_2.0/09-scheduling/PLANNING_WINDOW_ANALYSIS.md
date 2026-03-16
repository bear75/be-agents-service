# Planning Window Analysis: Backend Support

> **Archive notice:** Backend support for planning windows is summarized in [SCHEDULE_SOLUTION_ARCHITECTURE.md](SCHEDULE_SOLUTION_ARCHITECTURE.md) § Planning Window Strategy (Consolidated). Use that section as the single source of truth.

**Date:** 2025-12-11  
**Question:** Does our data model and backend support longer planning windows (weekly/monthly) for daily optimizations?

**Answer:** ✅ **YES - Fully Supported**

---

## Executive Summary

The Caire backend architecture **fully supports** using longer planning windows (weekly/monthly) for daily optimizations. The data model uses flexible timestamp fields, services calculate planning windows dynamically, and Timefold accepts planning windows of any length.

**No schema changes needed** - the system is already capable of this strategy.

---

## Data Model Analysis

### Schedules Table

```typescript
export const schedules = pgTable("schedules", {
  date: timestamp("date", { mode: "string" }).notNull(), // Primary date
  startDate: timestamp("start_date", { mode: "string" }).notNull(), // ✅ Can span multiple days
  endDate: timestamp("end_date", { mode: "string" }).notNull(), // ✅ Can span multiple days
  scheduleTimespan: scheduleTimespan("schedule_timespan")
    .notNull()
    .default("daily"), // ✅ Supports "daily" | "weekly" | "monthly" | "consolidated"
});
```

**Key Findings**:

- ✅ `startDate` and `endDate` are **timestamps** (not dates) → can span multiple days
- ✅ `scheduleTimespan` enum already supports weekly/monthly
- ✅ No single-day constraint in schema

### Planning Window Storage

**Finding**: Planning windows are **NOT stored in the database** - they are:

1. Calculated dynamically from date ranges
2. Passed to Timefold in `modelInput.planningWindow`
3. Flexible - can be any length

**Implication**: ✅ No schema changes needed - planning windows are runtime calculations

---

## Backend Service Analysis

### 1. Pre-Planning Orchestrator ✅

**File**: `pre-planning-orchestrator.ts`

**Current Code**:

```typescript
const planningWindow: PlanningWindow = {
  start: parseISO(request.dateRangeStart + "T06:00:00.000Z"),
  end: parseISO(request.dateRangeEnd + "T23:00:00.000Z"), // ✅ Any date range!
};
```

**Support**: ✅ Already accepts any date range (daily, weekly, monthly)

### 2. Carefox Mapper ✅

**File**: `carefox-mapper-shared.ts`

**Current Code**:

```typescript
static calculatePlanningWindow(...) {
  // ✅ Detects single-day vs multi-day
  const isSingleDay = /* checks if visits span multiple days */;

  if (isSingleDay) {
    // Single-day logic
  } else {
    // ✅ MULTI-DAY logic already implemented
    earliestDate = new Date(earliestTime - totalBufferMs);
    latestDate = new Date(latestTime + totalBufferMs);
  }
}
```

**Support**: ✅ Already handles multi-day schedules correctly

### 3. Pattern Time Calculator ✅

**File**: `pattern-time-calculator.ts`

**Current Code**:

```typescript
export function calculatePatternTimeWindows(
  frequency: "weekly" | "bi-weekly" | "monthly",
  dateFrom: string, // ✅ Planning window start
  dateTo: string, // ✅ Planning window end
) {
  // ✅ Calculates weekly/monthly aligned windows
  // Weekly: Monday 06:00 -> Sunday 23:00
  // Monthly: 1st 06:00 -> Last day 23:00
}
```

**Support**: ✅ Already supports weekly/monthly planning windows

---

## Timefold Integration Analysis

### Planning Window Format

```typescript
interface TimefoldPlanningWindow {
  startDate: string; // ISO 8601 "YYYY-MM-DD"
  endDate: string; // ISO 8601 "YYYY-MM-DD"
}
```

**Finding**: ✅ Timefold accepts planning windows of **any length** - no restrictions

**Documentation**: According to [Timefold docs](https://docs.timefold.ai/field-service-routing/latest/user-guide/planning-window), planning windows can span any date range.

---

## Current Limitations & Recommendations

### Limitation: Daily Schedule Creation

**Current Behavior**:

- Daily schedule creation uses `calculatePlanningWindow()` with a single date
- This calculates a single-day window from visit data

**Recommendation**:

1. **Option A**: Update daily schedule creation to accept optional `planningWindowDays` parameter
2. **Option B**: Use pre-planning service for daily optimizations with weekly context

### Enhancement Needed

**File**: Daily schedule creation services

**Suggested Change**:

```typescript
interface CreateDailyScheduleRequest {
  targetDate: string;
  planningWindowDays?: number; // NEW: default 1, can be 7 for weekly
}

// In service:
const planningWindow = {
  startDate: targetDate,
  endDate: addDays(targetDate, planningWindowDays || 1).toISOString(),
};
```

---

## Verification Results

| Component                     | Status         | Notes                                |
| ----------------------------- | -------------- | ------------------------------------ |
| **Schedules table schema**    | ✅ Supported   | `startDate`/`endDate` are timestamps |
| **Pre-planning orchestrator** | ✅ Supported   | Accepts any date range               |
| **Carefox mapper**            | ✅ Supported   | Handles multi-day schedules          |
| **Pattern calculator**        | ✅ Supported   | Weekly/monthly windows               |
| **Timefold integration**      | ✅ Supported   | No length restrictions               |
| **Daily schedule creation**   | ⚠️ Enhancement | Should add optional longer window    |

---

## Conclusion

**The backend fully supports longer planning windows.** The architecture is designed for flexibility:

1. ✅ **Data model** supports multi-day schedules
2. ✅ **Services** calculate planning windows dynamically
3. ✅ **Timefold** accepts planning windows of any length
4. ⚠️ **Enhancement**: Update daily schedule creation to optionally use longer windows

**No breaking changes needed** - this is an enhancement to leverage existing capabilities.

---

## Next Steps

1. ✅ Document the strategy (done - `PLANNING_WINDOW_STRATEGY.md`)
2. ✅ Verify backend support (done - this document)
3. ⏳ Update daily schedule creation to support optional longer windows
4. ⏳ Update UI to allow planners to specify planning window length
5. ⏳ Test with weekly planning windows for daily optimizations

---

## References

- [Planning Window Strategy](./PLANNING_WINDOW_STRATEGY.md)
- [Backend Planning Window Support](./BACKEND_PLANNING_WINDOW_SUPPORT.md)
- [Pre-Planning Orchestrator](../../src/features/scheduling/services/preplanning/pre-planning-orchestrator.ts)
- [Carefox Mapper](../../src/features/scheduling/services/mappers/carefox-mapper-shared.ts)
