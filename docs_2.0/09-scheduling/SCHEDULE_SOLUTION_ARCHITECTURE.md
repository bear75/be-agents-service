# Schedule vs Solution Architecture

> **Referred from:** [SOLUTION_UI_SPECIFICATION.md](SOLUTION_UI_SPECIFICATION.md) (product & UI); archived narrative [../../archive/SOLUTION_UI_PRD.md](../../archive/SOLUTION_UI_PRD.md). This file is architecture detail only.  
> **Status:** Design Specification  
> **Last Updated:** 2026-01-19  
> **Related:** `data-model.md`, `TIMEFOLD_INTEGRATION.md`, `PINNED_VISITS_GUIDE.md`

---

## Executive Summary

This document defines the architectural relationship between **Schedules** and **Solutions**, and how the system handles real-time changes to both **supply** (employees/capacity) and **demand** (visits/requirements). The design supports:

- Multiple solution revisions per schedule
- What-if scenario comparison
- Fine-tuning with supply and demand adjustments
- Planner decision workflow

---

## Core Concepts

### Schedule

A **Schedule** represents a **planning problem instance** for a specific date/period. It contains:

- **Visits** (demand) - what needs to be done
- **Schedule Employees** (supply) - who can do the work
- **Constraints** - rules and preferences

```
Schedule
├── id, name, scheduleDate
├── status: draft | optimizing | published | archived
├── scheduleType: original | what_if | revision
│
├── Visits[] (demand)
│   ├── clientId, visitDate, durationMinutes
│   ├── priority, isMandatory, isMovable
│   ├── allowedTimeWindow, preferredTimeWindow
│   └── skills[], preferences[]
│
├── ScheduleEmployees[] (supply)
│   ├── employeeId, isAvailable
│   ├── unavailabilityReason
│   └── shifts[] (startTime, endTime, breaks[])
│
└── Solutions[] (optimization results)
```

### Solution

A **Solution** represents an **optimization result** for a schedule. Multiple solutions can exist for the same schedule, enabling comparison.

```
Solution
├── id, scheduleId
├── datasetId (Timefold job ID)
├── parentDatasetId (for fine-tune chains)
├── status: solving_scheduled | solving_active | solving_completed | failed
│
├── SolutionAssignments[] (visit → employee mapping)
│   ├── visitId, scheduleEmployeeId
│   ├── assignedStartTime, travelTimeMinutes
│   └── sequence (order in employee's day)
│
├── SolutionMetrics (KPIs)
│   ├── totalVisits, assignedVisits, unassignedVisits
│   ├── totalTravelMinutes, avgTravelPerVisit
│   ├── utilizationPercent, continuityScore
│   └── constraintViolations[]
│
└── metadata (JSON)
    ├── scenarioId
    ├── supplySnapshot: { employeeIds, availabilityState }
    ├── demandSnapshot: { visitCount, movableCount, optionalCount }
    └── patchOperations: [{ type, description }]
```

---

## Architectural Principles

### 1. Schedule = Immutable Problem Definition (mostly)

The schedule defines **what needs to be solved**. During active optimization:

- Visits and employees define the problem space
- Changes to the schedule require re-optimization

### 2. Solutions = Exploration Space

Multiple solutions per schedule enable:

- What-if analysis
- Fine-tuning iterations
- Scenario comparison

### 3. Fine-Tuning = Incremental Optimization

Using Timefold's `from-patch` endpoint:

- Start from previous solution
- Unpin specific visits for re-optimization
- Keep most assignments stable
- Much faster than full solve

### 4. Snapshots for Comparison

Each solution stores a snapshot of the supply/demand state it was optimized against:

- Enables accurate comparison even after schedule changes
- Supports "time travel" to see what state produced what result

---

## Planning Window Strategy (Consolidated)

This section consolidates the planning window strategy and backend support previously in `PLANNING_WINDOW_STRATEGY.md`, `PLANNING_WINDOW_ANALYSIS.md`, and `BACKEND_PLANNING_WINDOW_SUPPORT.md`. Use this as the single source of truth.

### Why Longer Planning Windows

Caire uses **longer time horizons** (weekly/monthly) for daily optimizations to improve quality:

- **Full context for movable visits** — Solver can place them optimally across the period.
- **Cross-area optimization** — Multiple service areas in one run; solver can suggest moving clients between areas.
- **Unused hours recapture** — Identify and utilize unused capacity across the period.
- **Priority and demand management** — Balance priorities and demand/supply with full context.
- **Multi-dimensional optimization** — Time (movable across days), location (areas), scope (temporary vs template changes).

### Recommended Windows

| Optimization type | Planning window         | Use case                                                                                                         |
| ----------------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **Daily**         | 7 days (target day + 6) | Optimize one day with weekly context; daily visits mandatory, movable visits can be placed anywhere in the week. |
| **Weekly**        | 2 weeks                 | Optimize a week with bi-weekly context; better continuity across weeks.                                          |
| **Monthly**       | Full month              | Monthly movable visits; long-term planning.                                                                      |

Planning windows are **not stored** in the database; they are calculated at runtime and passed to Timefold in `modelInput.planningWindow`.

### Backend Support

- **Schedule model:** `startDate` and `endDate` are timestamps and can span multiple days; `scheduleTimespan` supports daily/weekly/monthly/consolidated.
- **Pre-planning orchestrator:** Accepts any date range for planning window.
- **Carefox mapper / pattern calculator:** Handle multi-day schedules and weekly/monthly aligned windows.
- **Timefold:** Accepts planning windows of any length in the API.
- **Enhancement:** Daily schedule creation can be extended to accept an optional `planningWindowDays` (e.g. 7 for weekly context) so a single-day UI still gets a 7-day optimization window.

### Visit Classification Within a Window

- **Mandatory:** Visit must be assigned (e.g. `maxEndTime` within planning window).
- **Optional:** Can be skipped (e.g. ends after window).
- **Movable:** Time window spans multiple days; solver can place on any day in the window.
- **Non-movable:** Single-day time window.

### Filtering Results for Display

After optimization, filter assignments to the **target period** for UI display (e.g. show only the target day when using a 7-day window).

### References

- [Timefold Planning Window Documentation](https://docs.timefold.ai/field-service-routing/latest/user-guide/planning-window)
- [MOVABLE_VISITS.md](MOVABLE_VISITS.md), [TIMEFOLD_INTEGRATION.md](TIMEFOLD_INTEGRATION.md)

---

## Real-Time Change Scenarios

### Scenario: Employee Calls in Sick

**Problem:** Anna calls in sick at 7:00 AM. She has 8 visits assigned today.

**Available Response Strategies:**

| Strategy                    | Type      | Description                              | Trade-off           |
| --------------------------- | --------- | ---------------------------------------- | ------------------- |
| **A. Find replacement**     | Supply    | Add another employee or extend shifts    | Higher cost         |
| **B. Move optional visits** | Demand    | Defer movable visits to tomorrow         | Reduced service     |
| **C. Reduce durations**     | Demand    | Shorten visit durations where flexible   | Lower quality       |
| **D. Redistribute**         | Rebalance | Spread visits across remaining employees | Higher workload     |
| **E. Hybrid**               | Combined  | Combination of above                     | Optimized trade-off |

**System Flow:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PLANNER WORKFLOW: Anna Calls in Sick                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. Mark Anna unavailable                                               │
│     └── scheduleEmployee.isAvailable = false                            │
│                                                                         │
│  2. System creates What-If branches:                                    │
│                                                                         │
│     ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                 │
│     │ Strategy A  │   │ Strategy B  │   │ Strategy C  │                 │
│     │ Add Erik    │   │ Move visits │   │ Reduce time │                 │
│     │ (backup)    │   │ to tomorrow │   │ -10% each   │                 │
│     └──────┬──────┘   └──────┬──────┘   └──────┬──────┘                 │
│            │                 │                 │                         │
│            ▼                 ▼                 ▼                         │
│     ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                 │
│     │ Solution A  │   │ Solution B  │   │ Solution C  │                 │
│     │             │   │             │   │             │                 │
│     │ Cost: +2h   │   │ Deferred: 3 │   │ Quality: -  │                 │
│     │ Travel: +15m│   │ Travel: -5m │   │ Travel: =   │                 │
│     │ Quality: =  │   │ Quality: =  │   │ Quality: ↓  │                 │
│     └──────┬──────┘   └──────┬──────┘   └──────┬──────┘                 │
│            │                 │                 │                         │
│            └─────────────────┴─────────────────┘                         │
│                              │                                           │
│                              ▼                                           │
│                    ┌─────────────────┐                                   │
│                    │ Compare Panel   │                                   │
│                    │                 │                                   │
│                    │ Pick Strategy B │                                   │
│                    │ (best balance)  │                                   │
│                    └────────┬────────┘                                   │
│                             │                                            │
│                             ▼                                            │
│                    ┌─────────────────┐                                   │
│                    │ Further tune?   │                                   │
│                    │                 │                                   │
│                    │ Yes: Unpin 2    │                                   │
│                    │ visits, re-opt  │                                   │
│                    └────────┬────────┘                                   │
│                             │                                            │
│                             ▼                                            │
│                    ┌─────────────────┐                                   │
│                    │ Solution B-2    │                                   │
│                    │ (fine-tuned)    │                                   │
│                    │                 │                                   │
│                    │ Publish ✓       │                                   │
│                    └─────────────────┘                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Data Model for What-If Scenarios

### Option A: Solution-Level Snapshots (Recommended)

Store supply/demand state changes in **solution metadata**:

```typescript
interface SolutionMetadata {
  // Link to parent for fine-tune chains
  parentDatasetId?: string;

  // Scenario configuration used
  scenarioId?: string;

  // Supply snapshot at time of optimization
  supplySnapshot: {
    employeeIds: string[];
    unavailable: { employeeId: string; reason: string }[];
    addedShifts: { employeeId: string; shiftId: string }[];
  };

  // Demand snapshot at time of optimization
  demandSnapshot: {
    totalVisits: number;
    deferredVisits: { visitId: string; deferredTo: Date }[];
    reducedDurations: {
      visitId: string;
      originalMinutes: number;
      newMinutes: number;
    }[];
    excludedOptional: string[];
  };

  // Operations applied to create this solution
  patchOperations: PatchOperation[];
}

interface PatchOperation {
  type:
    | "supply_remove"
    | "supply_add"
    | "demand_defer"
    | "demand_reduce"
    | "demand_exclude";
  entityId: string;
  description: string;
  metadata?: Record<string, unknown>;
}
```

### Option B: Schedule Cloning (For Major What-If)

For scenarios with **significantly different inputs**, clone the schedule:

```typescript
// When to clone vs snapshot:
// - Clone: Different employee set, different visit set
// - Snapshot: Same schedule, different optimization parameters

interface ScheduleCloneOptions {
  baseScheduleId: string;
  name: string;
  scheduleType: "what_if" | "revision";

  // Supply modifications
  excludeEmployeeIds?: string[];
  includeEmployeeIds?: string[]; // Add backup employees

  // Demand modifications
  excludeVisitIds?: string[]; // Remove optional visits
  deferVisitIds?: { visitId: string; newDate: Date }[];
}
```

---

## Fine-Tuning Strategies

### Strategy A: Supply-Side Adjustment

**Add capacity to handle demand:**

```typescript
interface SupplyAdjustment {
  type: "add_employee" | "extend_shift" | "add_break_coverage";

  // Add employee
  addEmployee?: {
    employeeId: string;
    shiftStart: Date;
    shiftEnd: Date;
  };

  // Extend shift
  extendShift?: {
    scheduleEmployeeId: string;
    newEndTime: Date;
    overtimeApproved: boolean;
  };
}
```

**Example: Add backup employee**

```typescript
async function addBackupEmployee(
  context: BridgeContext,
  scheduleId: string,
  backupEmployeeId: string,
  shift: { start: Date; end: Date },
): Promise<ServiceResult<SolutionData>> {
  // 1. Add employee to schedule
  const scheduleEmployee = await context.prisma.scheduleEmployee.create({
    data: {
      scheduleId,
      employeeId: backupEmployeeId,
      isAvailable: true,
    },
  });

  // 2. Create shift
  await context.prisma.scheduleEmployeeShift.create({
    data: {
      scheduleEmployeeId: scheduleEmployee.id,
      startTime: shift.start,
      endTime: shift.end,
      breakMinutes: 30,
    },
  });

  // 3. Run optimization with unpinned visits from sick employee
  return fineTuneSolution(context, {
    scheduleId,
    unpinnedVisitIds: await getUnassignedVisits(scheduleId),
    metadata: {
      patchOperations: [
        {
          type: "supply_add",
          entityId: backupEmployeeId,
          description: "Added backup employee to cover sick leave",
        },
      ],
    },
  });
}
```

### Strategy B: Demand-Side Adjustment

**Reduce demand to match available capacity:**

```typescript
interface DemandAdjustment {
  type: "defer_visit" | "reduce_duration" | "exclude_optional";

  // Defer to another day
  deferVisit?: {
    visitId: string;
    newDate: Date;
    reason: string;
  };

  // Reduce duration
  reduceDuration?: {
    visitId: string;
    newDurationMinutes: number;
    originalDurationMinutes: number;
  };

  // Mark optional visit as excluded
  excludeOptional?: {
    visitId: string;
    reason: string;
  };
}
```

**Example: Defer movable visits**

```typescript
async function deferMovableVisits(
  context: BridgeContext,
  scheduleId: string,
  targetDate: Date,
  maxToDefer: number = 5,
): Promise<ServiceResult<DeferResult>> {
  // 1. Find movable, optional visits
  const movableVisits = await context.prisma.visit.findMany({
    where: {
      scheduleId,
      isMovable: true,
      isMandatory: false,
    },
    orderBy: { priority: "desc" }, // Lowest priority first
    take: maxToDefer,
  });

  // 2. Create or find tomorrow's schedule
  const tomorrowSchedule = await getOrCreateSchedule(context, {
    organizationId: schedule.organizationId,
    scheduleDate: targetDate,
  });

  // 3. Move visits
  const deferred: DeferredVisit[] = [];
  for (const visit of movableVisits) {
    // Clone visit to tomorrow
    await context.prisma.visit.create({
      data: {
        ...visit,
        id: undefined,
        scheduleId: tomorrowSchedule.id,
        visitDate: targetDate,
        metadata: {
          ...visit.metadata,
          deferredFrom: scheduleId,
          originalDate: visit.visitDate,
        },
      },
    });

    // Mark original as excluded
    await context.prisma.visit.update({
      where: { id: visit.id },
      data: {
        visitStatus: "deferred",
        metadata: {
          ...visit.metadata,
          deferredTo: tomorrowSchedule.id,
          deferredDate: targetDate,
        },
      },
    });

    deferred.push({ visitId: visit.id, deferredTo: targetDate });
  }

  return {
    success: true,
    data: {
      deferredCount: deferred.length,
      deferred,
      targetScheduleId: tomorrowSchedule.id,
    },
  };
}
```

### Strategy C: Hybrid Adjustment

**Combine supply and demand changes:**

```typescript
interface HybridAdjustment {
  supplyChanges: SupplyAdjustment[];
  demandChanges: DemandAdjustment[];

  // Optimization parameters
  prioritizeSupply?: boolean; // Try to maintain all visits
  prioritizeDemand?: boolean; // Minimize cost/overtime
}

async function applyHybridStrategy(
  context: BridgeContext,
  scheduleId: string,
  strategy: HybridAdjustment,
): Promise<ServiceResult<SolutionData>> {
  // 1. Apply demand changes first (immediate)
  for (const demand of strategy.demandChanges) {
    await applyDemandChange(context, scheduleId, demand);
  }

  // 2. Apply supply changes
  for (const supply of strategy.supplyChanges) {
    await applySupplyChange(context, scheduleId, supply);
  }

  // 3. Run optimization
  return fineTuneSolution(context, {
    scheduleId,
    unpinnedVisitIds: await getAffectedVisits(strategy),
    metadata: {
      patchOperations: [
        ...strategy.demandChanges.map(toPatchOp),
        ...strategy.supplyChanges.map(toPatchOp),
      ],
    },
  });
}
```

---

## Multi-Path Comparison Workflow

### Step 1: Create Strategy Branches

```typescript
interface StrategyBranch {
  id: string;
  name: string;
  description: string;
  adjustments: HybridAdjustment;
  solutionId?: string; // Filled after optimization
  metrics?: SolutionMetrics;
}

async function createStrategyBranches(
  context: BridgeContext,
  scheduleId: string,
  trigger: DisruptionTrigger, // e.g., { type: 'sick_employee', employeeId: '...' }
): Promise<StrategyBranch[]> {
  const branches: StrategyBranch[] = [];

  // Branch A: Add backup employee
  if (await hasAvailableBackup(context, scheduleId)) {
    branches.push({
      id: "strategy-a",
      name: "Add Backup Employee",
      description: "Call in backup to cover all visits",
      adjustments: {
        supplyChanges: [
          {
            type: "add_employee",
            addEmployee: await getRecommendedBackup(
              context,
              scheduleId,
              trigger,
            ),
          },
        ],
        demandChanges: [],
      },
    });
  }

  // Branch B: Defer optional visits
  const movableCount = await getMovableVisitCount(context, scheduleId);
  if (movableCount > 0) {
    branches.push({
      id: "strategy-b",
      name: "Defer Optional Visits",
      description: `Move up to ${movableCount} optional visits to tomorrow`,
      adjustments: {
        supplyChanges: [],
        demandChanges: [
          {
            type: "defer_visit",
            deferVisit: { maxCount: movableCount, targetDate: tomorrow() },
          },
        ],
      },
    });
  }

  // Branch C: Reduce durations
  branches.push({
    id: "strategy-c",
    name: "Reduce Visit Durations",
    description: "Reduce flexible visits by 10%",
    adjustments: {
      supplyChanges: [],
      demandChanges: [
        {
          type: "reduce_duration",
          reduceDuration: { percentReduction: 10, onlyFlexible: true },
        },
      ],
    },
  });

  // Branch D: Hybrid
  branches.push({
    id: "strategy-d",
    name: "Balanced Approach",
    description: "Defer 2 optional visits + reduce durations by 5%",
    adjustments: {
      supplyChanges: [],
      demandChanges: [
        {
          type: "defer_visit",
          deferVisit: { maxCount: 2, targetDate: tomorrow() },
        },
        {
          type: "reduce_duration",
          reduceDuration: { percentReduction: 5, onlyFlexible: true },
        },
      ],
    },
  });

  return branches;
}
```

### Step 2: Parallel Optimization

```typescript
async function optimizeBranches(
  context: BridgeContext,
  scheduleId: string,
  branches: StrategyBranch[],
): Promise<StrategyBranch[]> {
  // Run all optimizations in parallel
  const results = await Promise.all(
    branches.map(async (branch) => {
      // Apply adjustments and optimize
      const result = await applyHybridStrategy(
        context,
        scheduleId,
        branch.adjustments,
      );

      if (result.success && result.data) {
        return {
          ...branch,
          solutionId: result.data.solutionId,
          metrics: result.data.metrics,
        };
      }
      return branch;
    }),
  );

  return results;
}
```

### Step 3: Compare and Decide

```typescript
interface ComparisonResult {
  branches: StrategyBranch[];
  recommendation: {
    branchId: string;
    reason: string;
    tradeoffs: string[];
  };
  comparisonMatrix: {
    metric: string;
    branchValues: { branchId: string; value: number; delta: number }[];
  }[];
}

async function compareBranches(
  context: BridgeContext,
  branches: StrategyBranch[],
  baseline: SolutionMetrics,
): Promise<ComparisonResult> {
  const metrics = [
    "travelTime",
    "assignmentRate",
    "utilization",
    "cost",
    "deferredVisits",
  ];

  const matrix = metrics.map((metric) => ({
    metric,
    branchValues: branches.map((branch) => ({
      branchId: branch.id,
      value: branch.metrics?.[metric] ?? 0,
      delta: (branch.metrics?.[metric] ?? 0) - (baseline[metric] ?? 0),
    })),
  }));

  // Simple scoring: minimize travel + cost, maximize assignment
  const scores = branches.map((branch) => ({
    branchId: branch.id,
    score: calculateScore(branch.metrics, baseline),
  }));

  const best = scores.sort((a, b) => b.score - a.score)[0];

  return {
    branches,
    recommendation: {
      branchId: best.branchId,
      reason: generateRecommendationReason(best, branches),
      tradeoffs: generateTradeoffs(best.branchId, branches),
    },
    comparisonMatrix: matrix,
  };
}
```

### Step 4: Further Fine-Tune

After selecting a branch, the planner can further refine:

```typescript
async function furtherFineTune(
  context: BridgeContext,
  selectedSolutionId: string,
  adjustments: {
    unpinVisitIds?: string[]; // Allow these to be reassigned
    pinVisitIds?: string[]; // Lock these assignments
    constraintOverrides?: Record<string, unknown>;
  },
): Promise<ServiceResult<SolutionData>> {
  return fineTuneSolution(context, {
    parentSolutionId: selectedSolutionId,
    unpinnedVisitIds: adjustments.unpinVisitIds,
    pinnedVisitIds: adjustments.pinVisitIds,
    metadata: {
      refinementReason: "Manual fine-tuning after strategy selection",
    },
  });
}
```

---

## Solution Chain Visualization

```
Schedule (2026-01-20)
│
├── Solution v1 (baseline)
│   ├── Status: completed
│   ├── Employees: [Anna, Erik, Maria]
│   └── Metrics: { travel: 120min, assigned: 50/50 }
│
├── [DISRUPTION: Anna sick]
│
├── Solution v2-A (add backup)          ← parentDatasetId: v1
│   ├── Status: completed
│   ├── supplySnapshot: { +Johan }
│   └── Metrics: { travel: 135min, assigned: 50/50, cost: +2h }
│
├── Solution v2-B (defer visits)        ← parentDatasetId: v1
│   ├── Status: completed
│   ├── demandSnapshot: { deferred: 3 }
│   └── Metrics: { travel: 95min, assigned: 47/50 }
│
├── Solution v2-C (reduce duration)     ← parentDatasetId: v1
│   ├── Status: completed
│   ├── demandSnapshot: { reduced: 8 visits -10% }
│   └── Metrics: { travel: 110min, assigned: 50/50, quality: -10% }
│
├── [DECISION: Select v2-B]
│
└── Solution v3 (fine-tuned from v2-B)  ← parentDatasetId: v2-B
    ├── Status: completed
    ├── Adjustments: unpinned 2 visits for better routing
    └── Metrics: { travel: 90min, assigned: 47/50 }  ← PUBLISHED
```

---

## Metrics Normalization for Comparison

When comparing solutions with different supply/demand:

### Absolute vs Normalized Metrics

| Metric          | Absolute | Normalized     | Use When                  |
| --------------- | -------- | -------------- | ------------------------- |
| Total travel    | 120 min  | 2.4 min/visit  | Different visit counts    |
| Assigned visits | 47       | 94%            | Different demand          |
| Utilization     | N/A      | 78%            | Always normalized         |
| Cost            | 2,500 kr | 50 kr/visit    | Different scales          |
| Deferred count  | 3        | 6% of optional | Different optional counts |

### Comparison Display

```typescript
interface ComparisonDisplay {
  baseline: {
    solutionId: string;
    label: string;
    metrics: NormalizedMetrics;
  };
  variants: {
    solutionId: string;
    label: string;
    metrics: NormalizedMetrics;
    deltas: MetricDeltas; // vs baseline
  }[];
}

interface NormalizedMetrics {
  // Per-visit metrics
  travelPerVisit: number; // minutes
  durationPerVisit: number; // minutes

  // Percentage metrics
  assignmentRate: number; // 0-100%
  utilizationRate: number; // 0-100%
  continuityScore: number; // 0-100%

  // Cost metrics (normalized)
  costPerVisit: number; // kr
  overtimePercentage: number; // 0-100%

  // Quality metrics
  deferredPercentage: number; // of optional
  durationReductionPct: number; // average reduction
}
```

---

## API Design

### Disruption Handling Endpoint

```graphql
# Trigger disruption workflow
mutation HandleDisruption($input: DisruptionInput!) {
  handleDisruption(input: $input) {
    scheduleId
    strategies {
      id
      name
      description
      estimatedImpact {
        travelDelta
        assignmentDelta
        costDelta
        qualityDelta
      }
    }
  }
}

input DisruptionInput {
  scheduleId: ID!
  type: DisruptionType! # SICK_EMPLOYEE, CANCELLED_VISIT, NEW_VISIT, etc.
  entityId: ID! # employeeId or visitId
  reason: String
}
```

### Strategy Optimization Endpoint

```graphql
# Optimize a specific strategy
mutation OptimizeStrategy($input: OptimizeStrategyInput!) {
  optimizeStrategy(input: $input) {
    solutionId
    status
    metrics {
      totalTravelMinutes
      assignedVisits
      unassignedVisits
      utilizationPercent
    }
  }
}

input OptimizeStrategyInput {
  scheduleId: ID!
  strategyId: ID!
  options: OptimizationOptions
}
```

### Comparison Endpoint

```graphql
# Compare multiple solutions
query CompareSolutions($solutionIds: [ID!]!, $baselineId: ID!) {
  compareSolutions(solutionIds: $solutionIds, baselineId: $baselineId) {
    baseline {
      solutionId
      metrics { ... }
    }
    variants {
      solutionId
      metrics { ... }
      deltas {
        travelDelta
        assignmentDelta
        costDelta
      }
    }
    recommendation {
      solutionId
      reason
      confidence
    }
  }
}
```

### Fine-Tune Endpoint

```graphql
# Fine-tune selected solution
mutation FineTuneSolution($input: FineTuneInput!) {
  fineTuneSolution(input: $input) {
    solutionId
    parentSolutionId
    status
    metrics { ... }
  }
}

input FineTuneInput {
  parentSolutionId: ID!
  unpinnedVisitIds: [ID!]
  pinnedVisitIds: [ID!]
  constraintOverrides: JSON
}
```

---

## Bryntum UI Integration

### Disruption Alert Panel

When disruption detected:

```
┌─────────────────────────────────────────────────────────────┐
│ ⚠️ DISRUPTION: Anna Andersson called in sick                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 8 visits affected • 4.5 hours of work                       │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Strategy A: Call in backup                              │ │
│ │ ├── Add Johan Svensson (07:00-16:00)                    │ │
│ │ ├── Est. cost: +2h overtime                             │ │
│ │ └── [Optimize] [Details]                                │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Strategy B: Defer optional visits                       │ │
│ │ ├── Move 3 movable visits to tomorrow                   │ │
│ │ ├── Est. impact: -3 visits today                        │ │
│ │ └── [Optimize] [Details]                                │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Strategy C: Reduce durations                            │ │
│ │ ├── Shorten 8 flexible visits by 10%                    │ │
│ │ ├── Est. impact: -24 min total service                  │ │
│ │ └── [Optimize] [Details]                                │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Optimize All]  [Custom Strategy...]                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Compare Solutions Panel

After optimization:

```
┌─────────────────────────────────────────────────────────────┐
│ Compare Solutions                                [Close]    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Metric          │ Baseline │ Add Backup │ Defer │ Reduce   │
│ ─────────────────────────────────────────────────────────── │
│ Travel time     │ 120 min  │ 135 min ↑  │ 95 min ↓ │ 110 min │
│ Assigned        │ 50/50    │ 50/50      │ 47/50 ↓  │ 50/50   │
│ Utilization     │ 78%      │ 72% ↓      │ 82% ↑    │ 78%     │
│ Cost            │ 2,500 kr │ 2,850 kr ↑ │ 2,350 kr │ 2,500 kr│
│ Quality         │ 100%     │ 100%       │ 100%     │ 90% ↓   │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ 💡 Recommendation: "Defer" - Best balance of cost & service │
│                                                             │
│ [Select "Add Backup"]  [Select "Defer" ✓]  [Select "Reduce"]│
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ Selected: Defer Optional Visits                             │
│ [Fine-tune this solution]  [Publish now]                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

| Scenario             | Action               | Schedule        | Solution             |
| -------------------- | -------------------- | --------------- | -------------------- |
| Sick employee        | Update availability  | Modify existing | New revision         |
| What-if (same input) | Compare scenarios    | Same schedule   | Multiple solutions   |
| What-if (diff input) | Clone schedule       | New schedule    | New solutions        |
| Fine-tune            | Adjust selected      | Same schedule   | Child solution       |
| Supply change        | Add/remove employees | Modify existing | Snapshot in metadata |
| Demand change        | Defer/reduce visits  | Modify existing | Snapshot in metadata |

The key insight is that **Solutions capture the state they were optimized against**, enabling accurate comparison even as the underlying schedule evolves. This supports the iterative, exploratory workflow planners need for real-time decision making.
