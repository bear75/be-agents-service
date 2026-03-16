# Solution Metrics Specification

> **Referred from:** [SOLUTION_UI_PRD.md](SOLUTION_UI_PRD.md) — that doc is the single source of truth for scheduling product and UI; this file is metrics definitions and formulas only.  
> **Purpose**: Comprehensive documentation of the metrics system for schedule optimization solutions. This document defines all KPIs, breakdown metrics, and derived metrics that support schedule analysis, comparison, and decision-making.

---

## Table of Contents

1. [Overview](#overview)
2. [Key Metrics (Home Care First: Time & %, Then Financials)](#key-metrics-home-care-first-time--then-financials)
3. [Solution-Level Metrics](#solution-level-metrics)
4. [Breakdown Metrics](#breakdown-metrics)
5. [Derived/Advanced Metrics](#derivedadvanced-metrics)
6. [Timefold Solver Score](#timefold-solver-score)
7. [Metrics Calculation](#metrics-calculation)
8. [Data Model Reference](#data-model-reference)

---

## Overview

**Home care metrics first.** We lead with home care KPIs (time, %, utilization, continuity, unassigned count); the Timefold solver score (hard/medium/soft) is route/optimization context and supports feasibility and constraint breakdown — it is not the primary lens for planners.

The metrics system provides comprehensive KPIs and analytics for schedule optimization solutions. Metrics are organized into three levels:

1. **Solution-level metrics** - Overall KPIs for an entire schedule or optimization run
2. **Breakdown metrics** - Per-entity metrics (employee, client, service area) for drill-down analysis
3. **Derived/Advanced metrics** - Calculated insights on top of solver output

All metrics support:

- **Comparison** between different schedule states (unplanned, planned, optimized, actual)
- **Drill-down** from organization → region → service area → employee/client level
- **Trend analysis** over time
- **ROI calculation** and optimization impact assessment

---

## Key Metrics (Home Care First: Time & %, Then Financials)

The metrics panel surfaces **home care metrics first** (time and %), then financials. Continuity is a first-class key metric. All are defined in detail in [Solution-Level Metrics](#solution-level-metrics) and [Breakdown Metrics](#breakdown-metrics); this section names them and gives the core definitions.

**Order in UI:** Time and % first; then nr and %; then nr (distance, continuity); then financials where shown.

**Metrics panel structure:**

| Type                      | Metrics                                                                        |
| ------------------------- | ------------------------------------------------------------------------------ |
| **Time**                  | Shift, Visit, Travel, Wait, Idle (durations)                                   |
| **%**                     | **Efficiency** = visit / (shift − break) — see [Efficiency](#efficiency) below |
| **Nr and %**              | Assigned & unassigned visits (count and %), visit groups (count and %)         |
| **Nr**                    | Distance (km), Continuity (caregivers per client per 14 days; target &lt; 15)  |
| **Financials** (if shown) | Cost, margin — see [Solution-Level Metrics](#solution-level-metrics)           |

### Efficiency

**Efficiency (%)** = productive (visit) time as a share of paid time excluding break:

**Formula:** `Efficiency = (totalServiceTime / (totalShiftTime − totalBreakTime)) × 100`

- **totalServiceTime** = sum of visit durations (seconds).
- **totalShiftTime** = sum of shift durations (seconds). Can be computed in different variants (see below).
- **totalBreakTime** = sum of break durations (seconds).

**Variants (shift definition):** The reported efficiency % depends on how shift time is defined. For example (see e.g. Huddinge `METRICS_VARIANTER.md` in be-agent-service):

- **All shifts:** Shift = scheduled length for every shift (includes empty shifts and time after last visit). Idle = shift − (visit + travel + wait + break). Lower efficiency (large denominator).
- **Exclude empty shifts only:** Shift = only shifts with ≥1 visit (scheduled length). Idle still includes end-of-shift gap. Mid efficiency.
- **Visit-span only:** Shift = first visit start to last visit end per shift; no empty parts. Idle = 0 for non-empty shifts. Higher efficiency.

Continuity is unchanged by these variants (it depends only on visit→employee→client).

| Key metric     | What it is                              | Main fields / formula                                                                                           | Why it matters                                        |
| -------------- | --------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| **Efficiency** | Visit time / (shift − break)            | `Efficiency = (totalServiceTime / (totalShiftTime − totalBreakTime)) × 100` (%). Target typically ≥75%.         | Primary KPI for how well shift time is used for care. |
| **Travel**     | Time between visits                     | `totalTravelTime` (seconds), `averageTravelTime`.                                                               | Core driver of route quality and cost.                |
| **Shift**      | Total paid/worked time                  | `totalShiftTime` = service + travel + wait + breaks (time). Per-employee: `totalWorkMinutes`, `totalShiftTime`. | Capacity and fairness.                                |
| **Visit**      | Demand coverage                         | `totalVisits`, `assignedVisits`, `unassignedVisits`, `assignedVisitsPercent` (%), visit groups (nr and %).      | Coverage gap and demand fulfilment.                   |
| **Continuity** | Nr of caregivers per client per 14 days | Count of distinct caregivers per client in rolling 14-day window. Lower is better.                              | **Target &lt; 15.** Care quality.                     |
| **Distance**   | Km driven                               | Total or average distance (km).                                                                                 | Route quality and cost.                               |

**UI requirement (one metrics panel):** One metrics panel (sidebar or header): time (shift, visit, travel, wait, idle), % (efficiency), nr and % (assigned/unassigned visits, visit groups), nr (distance km, continuity). Same panel on Schedule View and Compare; optional delta when comparing. Financials after if shown. See [SOLUTION_UI_PRD.md](SOLUTION_UI_PRD.md) § Metrics Display.

---

## Solution-Level Metrics

The `solution_metrics` table stores aggregated metrics for an entire schedule or optimization run.

### Financial Summary

| Field                | Type          | Description                                       |
| -------------------- | ------------- | ------------------------------------------------- |
| `totalRevenue`       | Decimal(10,2) | Total revenue generated (SEK)                     |
| `totalStaffCost`     | Decimal(10,2) | Total staff cost (SEK)                            |
| `totalMargin`        | Decimal(10,2) | Total margin = revenue - staff cost (SEK)         |
| `totalMarginPercent` | Decimal(5,2)  | Margin as percentage of revenue (%)               |
| `totalCost`          | Decimal(10,2) | Total cost (includes staff + travel + wait costs) |
| `profitMargin`       | Decimal(5,2)  | Profit margin percentage                          |

**Calculation:**

- `totalMargin = totalRevenue - totalStaffCost`
- `totalMarginPercent = (totalMargin / totalRevenue) * 100` (if revenue > 0)
- `totalCost = totalStaffCost + travelCost + waitTimeCost`

### Staff Distribution

| Field                 | Type         | Description                                               |
| --------------------- | ------------ | --------------------------------------------------------- |
| `totalEmployees`      | Integer      | Total number of employees in solution                     |
| `activeEmployees`     | Integer      | Number of employees with assigned visits                  |
| `unassignedEmployees` | Integer      | Number of employees with no assigned visits               |
| `staffUtilisation`    | Decimal(5,2) | Overall staff utilization percentage                      |
| `workingTimeFairness` | Decimal(5,2) | Fairness score for work distribution across employees (%) |

**Calculation:**

- `unassignedEmployees = totalEmployees - activeEmployees`
- `staffUtilisation = (totalServiceTime / totalShiftTime) * 100`
- `workingTimeFairness` = Standard deviation of employee shift times (lower = more fair)

### Visit Distribution

| Field                   | Type         | Description                                   |
| ----------------------- | ------------ | --------------------------------------------- |
| `totalVisits`           | Integer      | Total number of visits in schedule            |
| `assignedVisits`        | Integer      | Number of visits successfully assigned        |
| `assignedVisitsPercent` | Decimal(5,2) | Percentage of visits assigned (%)             |
| `unassignedVisits`      | Integer      | Number of visits that couldn't be assigned    |
| `clientsServed`         | Integer      | Number of unique clients with assigned visits |

**Calculation:**

- `unassignedVisits = totalVisits - assignedVisits`
- `assignedVisitsPercent = (assignedVisits / totalVisits) * 100`
- `clientsServed` = COUNT(DISTINCT clientId) WHERE assignedVisits > 0

**Critical Indicator:**

- `unassignedVisits > 0` indicates schedule feasibility issues
- High `unassignedVisits` suggests insufficient capacity or constraint conflicts

### Time & Distance Metrics

| Field               | Type    | Description                                         | Unit    |
| ------------------- | ------- | --------------------------------------------------- | ------- |
| `totalServiceTime`  | Integer | Total service time across all visits                | seconds |
| `totalTravelTime`   | Integer | Total travel time between visits                    | seconds |
| `totalWaitTime`     | Integer | Total waiting time (gaps between visits)            | seconds |
| `totalShiftTime`    | Integer | Total shift time (service + travel + wait + breaks) | seconds |
| `totalBreakMinutes` | Integer | Total break time                                    | minutes |

**Supporting Calculations:**

- **Travel Efficiency** = `totalTravelTime / totalServiceTime` (lower is better)
- **Service Time Ratio** = `totalServiceTime / totalShiftTime` (higher is better)
- **Wait Time Ratio** = `totalWaitTime / totalShiftTime` (lower is better)

### Cost Breakdown

| Field                 | Type          | Description                          |
| --------------------- | ------------- | ------------------------------------ |
| `totalTechnicianCost` | Decimal(10,2) | Total employee/staff cost (SEK)      |
| `travelCost`          | Decimal(10,2) | Cost component for travel time (SEK) |
| `waitTimeCost`        | Decimal(10,2) | Cost component for wait time (SEK)   |

**Calculation:**

- `totalTechnicianCost` = Sum of employee costs based on contract type and payment model
- `travelCost` = Travel time cost based on payment model (Model A/C include travel)
- `waitTimeCost` = Wait time cost based on payment model (Model A includes wait)

**Payment Model Impact:**

- **Model A**: Paid for all hours (service + travel + wait + breaks) → `travelCost` and `waitTimeCost` included
- **Model B**: Paid for service hours only → `travelCost = 0`, `waitTimeCost = 0`
- **Model C**: Paid for service + travel, not wait → `waitTimeCost = 0`
- **Model D**: Custom payment rules

### Constraint/Solver Scores

| Field                        | Type    | Description                                       |
| ---------------------------- | ------- | ------------------------------------------------- |
| `hardConstraintViolations`   | Integer | Number of hard constraint violations              |
| `mediumConstraintViolations` | Integer | Number of medium constraint violations            |
| `softConstraintViolations`   | Integer | Number of soft constraint violations              |
| `solverScore`                | String  | Timefold optimization score (from Solution.score) |
| `isFeasible`                 | Boolean | Whether solution satisfies all hard constraints   |

**Timefold Score:**

- The `solverScore` comes from Timefold's `SolutionMetrics.score` field
- Higher score = fewer soft constraint violations = better solution
- `isFeasible = true` means all hard constraints are satisfied
- Score format: `"0hard/-12345soft"` (hard score / soft score)

**Usage:**

- Compare scores between different optimization runs
- Understand why one solution differs from another
- Identify constraint trade-offs

---

## Breakdown Metrics

Metrics are provided for individual entities to enable drill-down analysis.

### Employee Metrics

Each row in `employee_solution_metrics` contains per-employee KPIs.

| Field              | Type          | Description                                    |
| ------------------ | ------------- | ---------------------------------------------- |
| `employeeId`       | UUID          | Reference to employee                          |
| `assignedVisits`   | Integer       | Number of visits assigned to employee          |
| `utilisation`      | Decimal(5,2)  | Utilization percentage (%)                     |
| `totalShiftTime`   | Integer       | Total shift time (seconds)                     |
| `totalServiceTime` | Integer       | Total service time (seconds)                   |
| `totalTravelTime`  | Integer       | Total travel time (seconds)                    |
| `totalWaitTime`    | Integer       | Total wait time (seconds)                      |
| `totalBreakTime`   | Integer       | Total break time (seconds)                     |
| `overTime`         | Integer       | Overtime beyond contracted hours (seconds)     |
| `underTime`        | Integer       | Undertime (unused contracted hours) (seconds)  |
| `staffCost`        | Decimal(10,2) | Total cost for this employee (SEK)             |
| `revenueGenerated` | Decimal(10,2) | Revenue generated from employee's visits (SEK) |
| `travelCost`       | Decimal(10,2) | Travel cost component (SEK)                    |
| `waitTimeCost`     | Decimal(10,2) | Wait time cost component (SEK)                 |

**Calculation:**

- `utilisation = (totalServiceTime / totalShiftTime) * 100`
- `overTime = MAX(0, totalShiftTime - contractedHours)`
- `underTime = MAX(0, contractedHours - totalShiftTime)`
- `revenueGenerated` = Sum of visit revenues for this employee
- `staffCost` = Based on contract type and payment model

**Use Cases:**

- Identify over- or under-utilized caregivers
- Analyze impact of breaks and waiting on productivity
- Compare employee performance
- Optimize work distribution

### Client Metrics

For each client, the system records visit and continuity metrics.

| Field                     | Type          | Description                                                                    |
| ------------------------- | ------------- | ------------------------------------------------------------------------------ |
| `clientId`                | UUID          | Reference to client                                                            |
| `totalVisits`             | Integer       | Total visits for this client                                                   |
| `assignedVisits`          | Integer       | Number of visits successfully assigned                                         |
| `unassignedVisits`        | Integer       | Number of visits that couldn't be assigned                                     |
| `totalServiceTime`        | Integer       | Total service time for client (seconds)                                        |
| `calculatedRevenue`       | Decimal(10,2) | Revenue from client's visits (SEK)                                             |
| `uniqueEmployeesIn14Days` | Integer       | **Continuity:** Nr of different caregivers assigned to client in 14-day window |
| `contactPersonCoverage`   | Decimal(5,2)  | Percentage of visits by contact person (%)                                     |

**Calculation:**

- `uniqueEmployeesIn14Days` = COUNT(DISTINCT employeeId) for assigned visits to this client in a rolling 14-day window. **This is the continuity metric.** Lower is better. **Target &lt; 15.**
- `contactPersonCoverage` = (visits by contact person / total visits) \* 100

**Use Cases:**

- Monitor continuity (fewer caregivers per 14 days per client = better; target &lt; 15)
- Track contact person coverage
- Identify clients with unassigned visits
- Calculate client-level revenue

**Continuity (definition):**

- **Metric:** Nr of caregivers per client per 14 days (= `uniqueEmployeesIn14Days` in rolling 14-day window).
- **Target:** &lt; 15.
- **Lower is better.**

### Service Area Metrics

Service areas aggregate metrics across geography.

| Field                 | Type          | Description                                    |
| --------------------- | ------------- | ---------------------------------------------- |
| `serviceAreaId`       | UUID          | Reference to service area                      |
| `totalVisits`         | Integer       | Total visits in service area                   |
| `assignedVisits`      | Integer       | Number of visits assigned                      |
| `unassignedVisits`    | Integer       | Number of visits unassigned                    |
| `totalServiceTime`    | Integer       | Total service time (seconds)                   |
| `totalTravelTime`     | Integer       | Total travel time (seconds)                    |
| `totalWaitTime`       | Integer       | Total wait time (seconds)                      |
| `totalEmployees`      | Integer       | Number of employees working in area            |
| `activeEmployees`     | Integer       | Number of employees with assignments           |
| `staffUtilisation`    | Decimal(5,2)  | Staff utilization percentage (%)               |
| `totalRevenue`        | Decimal(10,2) | Total revenue for area (SEK)                   |
| `totalCost`           | Decimal(10,2) | Total cost for area (SEK)                      |
| `coverageSuccessRate` | Decimal(5,2)  | Percentage of visits successfully assigned (%) |
| `supplyDemandBalance` | Decimal(10,2) | Supply hours - demand hours (hours)            |

**Calculation:**

- `coverageSuccessRate = (assignedVisits / totalVisits) * 100`
- `supplyDemandBalance = totalShiftTime - totalServiceTime` (positive = excess supply, negative = excess demand)
- `staffUtilisation = (totalServiceTime / totalShiftTime) * 100`

**Use Cases:**

- **Hierarchical analytics**: Drill down from organization → region → area → visit level
- **Cross-area comparisons**: Resource distribution, performance benchmarking, cost allocation
- **Supply/demand analysis**: Identify over- or under-supplied areas
- **Geographic performance**: Compare efficiency across service areas

---

## Derived/Advanced Metrics

The BI layer adds additional insights on top of solver output.

### Efficiency (Primary KPI)

**Formula:** `Efficiency = serviceHours / shiftHours`

- **Service hours**: Total time spent on actual client care
- **Shift hours**: Total paid time (service + travel + wait + breaks)

**Target:** ≥75% efficiency

**Interpretation:**

- Higher efficiency = more time spent on care vs. travel/waiting
- Primary metric for comparing schedule quality
- Used across all schedule states (unplanned, planned, optimized, actual)

### Continuity

**Metrics:**

1. **Number of different caregivers per client**
   - Count of unique employees assigned to each client
   - Lower is better (1 = best, ~10 = typical, 12+ = poor)

2. **Contact person percentage**
   - Percentage of visits by the designated contact person
   - Higher is better (target: maximize)

3. **Preferred caregivers assignment rate**
   - Percentage of visits assigned to preferred caregivers
   - Based on client preferences

**Calculation:**

- **Continuity** = nr of caregivers per client per 14 days (`uniqueEmployeesIn14Days` in rolling 14-day window). Lower is better; **target &lt; 15.**
- `contactPersonCoverage` = (visits by contact person / total visits) \* 100

### Unused Hours Recapture

**Purpose:** Measure how many unused client allocation hours are successfully rescheduled.

**Calculation:**

- `unusedHours = allocatedHours - assignedServiceHours`
- `recapturedHours = MIN(unusedHours, rescheduledHours)`
- `recaptureRate = (recapturedHours / unusedHours) * 100`

**Use Cases:**

- Identify lost revenue opportunities
- Optimize allocation utilization
- Balance supply and demand

### Skills Utilization

**Purpose:** Measure how well required skills are matched to available caregivers.

**Metrics:**

- **Skills match rate**: Percentage of visits where assigned employee has required skills
- **Skills coverage**: Percentage of required skills covered by assigned employees
- **Skills over-qualification**: Percentage of visits where employee has more skills than required

**Calculation:**

- `skillsMatchRate = (visits with skill match / total visits) * 100`
- `skillsCoverage = (required skills covered / total required skills) * 100`

### Travel Efficiency

**Formula:** `Travel Efficiency = travelTime / serviceHours`

- Lower is better (less travel time per service hour)
- Target: 15-30% reduction vs. manual planning

**Supporting Metrics:**

- Average travel time per visit
- Travel time distribution
- Geographic clustering score

### Client Continuity Score

**Derived metric** that evaluates consistency of care.

**Components:**

1. Number of unique caregivers (lower = better)
2. Contact person coverage (higher = better)
3. Preferred caregiver assignment rate (higher = better)

**Calculation:**

- Weighted combination of the three components
- Normalized to 0-100 scale

### Contact Person Coverage

**Percentage of visits by the designated contact person.**

**Calculation:**

- `contactPersonCoverage = (visits by contact person / total visits) * 100`

**Target:** Maximize contact person coverage for better continuity

### Recaptured Hours

**Measure of unused client hours successfully rescheduled.**

**Calculation:**

- `recapturedHours = MIN(unusedAllocatedHours, rescheduledHours)`
- `recaptureRate = (recapturedHours / unusedAllocatedHours) * 100`

### Geographic Performance Analysis

**Cross-area comparisons:**

- Resource distribution across service areas
- Performance benchmarking
- Cost allocation per area
- Supply/demand balance per area

### Supply-Demand Balance

**Formula:** `Balance = supplyHours - demandHours`

- **Positive balance**: Excess supply (underutilized resources)
- **Negative balance**: Excess demand (insufficient capacity)
- **Zero balance**: Optimal allocation

**Calculation:**

- `supplyHours = SUM(employeeShiftTime)` for area
- `demandHours = SUM(visitServiceTime)` for area
- `balance = supplyHours - demandHours`

---

## Timefold Solver Score

The Timefold solver attaches a score and feasibility flag to each solution. **This is route/optimization context:** the primary lens for the UI is home care metrics (time, %, utilization, continuity); solver score and constraint breakdown support feasibility and comparison.

### Score Structure

**Location:** `Solution.score` (String) and `Solution.isFeasible` (Boolean)

**Format:** `"0hard/-12345soft"`

- **Hard score**: Number of hard constraint violations (0 = all satisfied)
- **Soft score**: Penalty for soft constraint violations (higher absolute value = more violations)

**Example Scores:**

- `"0hard/-500soft"` = All hard constraints satisfied, some soft constraint violations
- `"-1hard/-1000soft"` = One hard constraint violation, many soft constraint violations
- `"0hard/0soft"` = Perfect solution (rare)

### Feasibility Flag

**Location:** `Solution.isFeasible` (Boolean)

- `true` = All hard constraints satisfied (feasible solution)
- `false` = One or more hard constraints violated (infeasible solution)

**Note:** Infeasible solutions may still be useful for analysis, but cannot be deployed.

### Usage in Metrics

**Expose solver score as supporting context (home care metrics first):**

- Display `score` (hard/medium/soft) and `isFeasible` in the one metrics panel
- Constraint breakdown explains penalties; optional delta when comparing solutions
- Compare scores between different optimization runs to understand trade-offs

**Integration:**

- `SolutionMetric.solverScore` = `Solution.score`
- `SolutionMetric.isFeasible` = `Solution.isFeasible`
- Same metrics panel (sidebar or header) on Schedule View and Compare; panel shows score, feasible, constraint breakdown, unassigned count, utilization, continuity (time & % first, then financials where shown)

**Why It Matters:**

- Higher score = fewer soft constraint violations = better solution
- Helps explain optimization quality
- Supports comparison between manual and AI-optimized schedules

---

## Metrics Calculation

### Calculation Timing

Metrics are calculated:

1. **After optimization completes** - When Timefold returns a solution
2. **After manual edits** - When planner modifies assignments
3. **On-demand** - When user requests metrics refresh

### Calculation Process

1. **Fetch solution assignments** from `SolutionAssignment` table
2. **Aggregate by entity** (employee, client, service area)
3. **Calculate time metrics** (service, travel, wait, shift, breaks)
4. **Calculate financial metrics** (cost, revenue, margin)
5. **Calculate derived metrics** (efficiency, continuity, utilization)
6. **Store in metrics tables** (`SolutionMetric`, `EmployeeSolutionMetric`, etc.)

### Payment Model Impact

**Different payment models affect cost calculation:**

| Model | Service | Travel      | Wait        | Breaks            |
| ----- | ------- | ----------- | ----------- | ----------------- |
| **A** | ✅ Paid | ✅ Paid     | ✅ Paid     | ✅ Paid (if PAID) |
| **B** | ✅ Paid | ❌ Not paid | ❌ Not paid | ❌ Not paid       |
| **C** | ✅ Paid | ✅ Paid     | ❌ Not paid | ❌ Not paid       |
| **D** | Custom  | Custom      | Custom      | Custom            |

**Break Payment Policy:**

- **PAID**: Breaks count toward cost
- **UNPAID**: Breaks don't count toward cost

**Configuration:**

- Payment models stored in `operational_settings` table
- Break payment policy in `operational_settings.breakPaymentPolicy`

### Revenue Calculation

**Revenue model varies by service area and municipality:**

- Each service area/municipality may have different revenue rates
- Revenue = Sum of visit revenues based on service area/municipality payment model
- Configuration via `service_area_payment_models` table

**Revenue per Visit:**

- Based on visit type, duration, and service area payment model
- May include travel time compensation (depending on model)

---

## Data Model Reference

### SolutionMetric Table

**Location:** `apps/dashboard-server/schema.prisma`

**Key Fields:**

- Financial: `totalRevenue`, `totalCost`, `profitMargin`
- Staff: `totalEmployees`, `activeEmployees`, `staffUtilisation`
- Visits: `totalVisits`, `assignedVisits`, `unassignedVisits`
- Time: `totalServiceTime`, `totalTravelTime`, `totalWaitTime`, `totalShiftTime`
- Constraints: `hardConstraintViolations`, `softConstraintViolations`
- Solver: `solverScore` (from `Solution.score`), `isFeasible` (from `Solution.isFeasible`)

### EmployeeSolutionMetric Table

**Key Fields:**

- `assignedVisits`, `utilisation`, `totalShiftTime`, `totalServiceTime`
- `totalTravelTime`, `totalWaitTime`, `totalBreakTime`
- `overTime`, `underTime`
- `staffCost`, `revenueGenerated`, `travelCost`, `waitTimeCost`

### ClientSolutionMetric Table

**Key Fields:**

- `totalVisits`, `assignedVisits`, `unassignedVisits`
- `totalServiceTime`, `calculatedRevenue`
- `uniqueEmployeesIn14Days` (continuity: nr of caregivers per client per 14 days; target &lt; 15), `contactPersonCoverage`

### ServiceAreaSolutionMetric Table

**Key Fields:**

- `totalVisits`, `assignedVisits`, `unassignedVisits`
- `totalServiceTime`, `totalTravelTime`, `totalWaitTime`
- `totalEmployees`, `activeEmployees`, `staffUtilisation`
- `totalRevenue`, `totalCost`
- `coverageSuccessRate`, `supplyDemandBalance`

---

## Summary

### Primary KPI

**Efficiency** = service hours ÷ shift hours (target: ≥75%)

### Core Metrics

- **Financial**: revenue, cost, margin (SEK and %)
- **Staff**: employee counts, utilization, distribution, fairness
- **Visits**: total, assigned, unassigned, clients served
- **Time**: service, travel, wait, shift, breaks (all in seconds)
- **Constraints**: hard/medium/soft violation counts
- **Solver**: Timefold score and feasibility flag

### Breakdown Metrics

- **Per organization** → **per service area** → **per employee** → **per client** → **per visit**
- Supports hierarchical drill-down and cross-area comparisons

### Advanced Metrics

- **Efficiency** (primary KPI)
- **Continuity** (caregivers per client, contact person coverage)
- **Unused hours recapture**
- **Skills utilization**
- **Travel efficiency**
- **Supply-demand balance**
- **Geographic performance analysis**

### Solver Score

- **Timefold optimization score** from `Solution.score` and `Solution.isFeasible`
- Exposed in `SolutionMetric` alongside KPIs
- Explains optimization quality and supports solution comparison

Together, these metrics provide stakeholders with a comprehensive view of:

- **Schedule efficiency** (service hours vs. paid hours)
- **Cost and revenue** (financial performance)
- **Resource utilization** (staff efficiency)
- **Care quality** (continuity, contact person coverage)
- **Optimization quality** (solver score, constraint satisfaction)

This enables informed decision-making when comparing human-planned and AI-optimized schedules.

---

_Last updated: January 2026_
