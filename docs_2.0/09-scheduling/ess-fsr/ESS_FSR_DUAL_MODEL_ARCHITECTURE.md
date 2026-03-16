# ESS + FSR Dual-Model Architecture

> **Status:** Architecture Specification  
> **Last Updated:** 2026-02-08  
> **Related:** `SCHEDULE_SOLUTION_ARCHITECTURE.md`, `OVERVIEW.md`, `MOVABLE_VISITS.md`  
> **Timefold Models:** [Employee Shift Scheduling (ESS)](https://docs.timefold.ai/employee-shift-scheduling/latest/introduction) + [Field Service Routing (FSR)](https://docs.timefold.ai/field-service-routing/latest/introduction)  
> **Timefold roadmap relevance:** [TIMEFOLD_ROADMAP_RELEVANCE.md](./TIMEFOLD_ROADMAP_RELEVANCE.md) (demand-curve shift creation, what-if, hyper-tuning)  
> **CAIRE feature roadmap:** [CAIRE_FEATURE_ROADMAP.md](./CAIRE_FEATURE_ROADMAP.md) (how each CAIRE feature is achieved with ESS and FSR)

---

## Executive Summary

CAIRE's scheduling platform evolves from a single-model architecture (FSR only) to a **dual-model architecture** combining Timefold Employee Shift Scheduling (ESS) and Field Service Routing (FSR). This eliminates the placeholder employee pool workaround and enables true demand-driven scheduling where the planner simply says "schedule all visits" and CAIRE determines the optimal staffing, shifts, and routes.

**Key principle:** The user sets a 100% visit coverage goal. CAIRE handles everything under the hood -- staffing levels, shift assignments, route optimization, travel overhead, labor law compliance, cost optimization, and continuity tracking. Efficiency is discovered, not configured.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Integration Point Map](#2-integration-point-map)
3. [Shift Travel and Locations](#3-shift-travel-and-locations)
4. [Cost Optimization: Fixed vs Hourly Staff](#4-cost-optimization-fixed-vs-hourly-staff)
5. [Mandatory and Optional Shifts](#5-mandatory-and-optional-shifts)
6. [Preferred Employees and Continuity](#6-preferred-employees-and-continuity)
7. [Skill Matching](#7-skill-matching)
8. [Pinning Synchronization](#8-pinning-synchronization)
9. [Replacement Recommendations](#9-replacement-recommendations)
10. [Real-Time Planning](#10-real-time-planning)
11. [Swedish Labor Law Compliance](#11-swedish-labor-law-compliance)
12. [Solution Comparison](#12-solution-comparison)
13. [Incremental Changes (from-patch)](#13-incremental-changes-from-patch)
14. [Explainable AI for Mobile](#14-explainable-ai-for-mobile)
15. [Uncovering Inefficiencies](#15-uncovering-inefficiencies)
16. [Real-Time Disruption Recommendations](#16-real-time-disruption-recommendations)
17. [Maps and Navigation](#17-maps-and-navigation)
18. [Metrics Strategy](#18-metrics-strategy)
19. [Iterative Convergence Loop](#19-iterative-convergence-loop)
20. [Implementation Phases](#20-implementation-phases)

---

## 1. Architecture Overview

### Current State: FSR Only

```
Visits (demand) + Employees with shifts (supply) → FSR → Routes + Assignments
Problem: When shifts are unknown → placeholder pool workaround
```

### Target State: ESS + FSR

```
Visits (demand) → [Demand Curve Generator] → ESS → Optimal Shifts
                                                ↓
Visits (with locations) + ESS Shifts → FSR → Routes + Assignments
                                                ↓
                                    [Convergence Check] → iterate if needed
                                                ↓
                                    Planner sees: "45/45 visits, 8 employees"
```

### Who Benefits

| Role                 | ESS Benefits                                                      | FSR Benefits                                               | Combined Benefits                         |
| -------------------- | ----------------------------------------------------------------- | ---------------------------------------------------------- | ----------------------------------------- |
| **Planner**          | Staffing recommendations, labor law compliance, cost optimization | Route optimization, visit assignments, travel minimization | "Schedule all visits" → complete solution |
| **Manager**          | Shift fairness metrics, cost analysis, staffing efficiency        | Travel KPIs, utilization rates, continuity scores          | Efficiency X-ray, what-if scenarios       |
| **Caregiver**        | Fair shift distribution, preferences respected, work-life balance | Optimized routes, less travel, predictable schedules       | Transparent explanations, self-service    |
| **Client (Brukare)** | Consistent caregiver assignments                                  | Reliable visit times                                       | Care continuity, visit transparency       |

---

## 2. Integration Point Map

| #   | ESS Feature                       | FSR Feature                       | Sync Mechanism                                                        | CAIRE Use Case                                       |
| --- | --------------------------------- | --------------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------- |
| 1   | Shift travel & locations          | Route optimization                | ESS limits home→area distance; FSR optimizes inter-visit routes       | Employee assigned to nearby service areas            |
| 2   | Cost management + activation      | Vehicle costs                     | ESS prefers fixed staff; FSR optimizes routes for activated employees | 80/20 fixed/hourly staffing model                    |
| 3   | Mandatory/optional shifts         | Mandatory/optional visits         | ESS shift priorities mirror FSR visit priorities                      | Daily=mandatory shifts, movable=optional shifts      |
| 4   | Preferred employees on shifts     | Preferred vehicles on visits      | Employee-client affinity from FSR feeds ESS shift preferences         | Continuity: < 10-15 caregivers per client            |
| 5   | Required/preferred skills         | Required skills                   | Same skill IDs used in both models                                    | Medication, dementia, wound care matching            |
| 6   | Manual intervention (pinning)     | Pinned visits                     | Pin state synchronized between models                                 | Approved slingor stay locked                         |
| 7   | Recommendations API               | Recommendations API               | ESS recommends shift replacement; FSR recommends visit reassignment   | Employee sick → who covers the shift AND the visits? |
| 8   | Real-time planning                | Real-time planning                | ESS re-plans shifts; FSR re-routes with updated shifts                | Same-day disruption handling                         |
| 9   | Labor law contracts               | Shift hours/overtime              | ESS enforces kollektivavtal; FSR respects shift boundaries            | Swedish labor compliance                             |
| 10  | Timefold Platform comparison      | Timefold Platform comparison      | Compare ESS+FSR solutions side-by-side                                | Challenge existing slingor with CAIRE alternatives   |
| 11  | from-patch API                    | from-patch API                    | Incremental changes to both models                                    | Add/remove employee without full re-solve            |
| 12  | Score analysis + justifications   | Score analysis + justifications   | Expose ESS+FSR explanations in mobile app                             | "Why am I working this shift?" transparency          |
| 13  | Metrics + KPIs                    | Metrics + KPIs                    | Combined efficiency analysis                                          | Management dashboard, bottleneck detection           |
| 14  | Recommendations during disruption | Recommendations during disruption | ESS shift reco + FSR visit reco in one workflow                       | Planner gets complete recommendation                 |
| 15  | Employee locations (Haversine)    | Maps service (OSRM Sweden)        | FSR uses OSRM for routes; ESS uses Haversine for home→shift           | Mobile app navigation with real routes               |

---

## 3. Shift Travel and Locations

**ESS Feature:** [Shift travel and locations](https://docs.timefold.ai/employee-shift-scheduling/latest/employee-resource-constraints/shift-travel-and-locations)

**Q: Can we use this for inter-visit travel?**

**A: No.** ESS shift travel is for **employee home → shift location** travel (commuting), not inter-visit routing. But it IS highly relevant for home care:

### How CAIRE Uses ESS Travel

ESS shift travel constraints ensure employees are assigned to shifts (service areas) near their home, which has cascading benefits for FSR:

```
ESS: "Lisa lives in Huddinge → assign her shifts in Huddinge Vastra service area"
     Uses: maxEmployeeToShiftTravelDistanceInMeters = 25000 (25 km)
     Uses: Minimize travel distance (soft constraint)

FSR: "Lisa is working Huddinge Vastra today → optimize her route within that area"
     Uses: OSRM Sweden map for actual road routing
```

### ESS Travel Configuration for CAIRE

```json
{
  "contracts": [
    {
      "id": "fullTimeContract",
      "travelConfigurations": [
        {
          "id": "maxTravelToServiceArea",
          "maxEmployeeToShiftTravelDistanceInMeters": 25000,
          "minMinutesBetweenShiftsInDifferentLocations": 60
        }
      ]
    }
  ]
}
```

### Shift Locations = Service Area Depot

Each ESS shift gets a `location` corresponding to the service area depot (office):

```json
{
  "shifts": [
    {
      "id": "huddinge-vastra-day-2026-02-10",
      "start": "2026-02-10T07:00:00+01:00",
      "end": "2026-02-10T15:00:00+01:00",
      "location": [59.2369, 17.9396]
    }
  ]
}
```

### What This Enables

- Employees consistently assigned to service areas near their home
- `locationsWorkedMax: 2` per week → limits how many different areas an employee works in (reduces commute variability)
- `minimizeTraveDistance` → ESS prefers employees closest to the shift location
- The commuting aspect is NOT included in the FSR shift time -- it's separate, just like real organizations treat it

### Travel Split

| Travel Type                               | Handled By                    | Included in Shift Time? |
| ----------------------------------------- | ----------------------------- | ----------------------- |
| Home → first client                       | FSR (depot→first visit)       | Yes                     |
| Between visits                            | FSR (inter-visit routing)     | Yes                     |
| Last client → home                        | FSR (last visit→depot)        | Yes                     |
| Home → office (commute)                   | ESS (shift travel)            | No (separate)           |
| Between service areas (if different days) | ESS (minMinutesBetweenShifts) | N/A (rest constraint)   |

---

## 4. Cost Optimization: Fixed vs Hourly Staff

**ESS Features:** [Cost management](https://docs.timefold.ai/employee-shift-scheduling/latest/shift-service-constraints/cost-management) + [Employee activation](https://docs.timefold.ai/employee-shift-scheduling/latest/employee-resource-constraints/employee-activation)

**Q: Is this useful?**

**A: Extremely.** This directly models the 80/20 fixed/hourly staffing pattern that Swedish home care organizations use.

### The Real-World Pattern

- **80% of demand** → covered by fixed-contract employees (tillsvidareanställda)
- **20% buffer** → absorbs cancellations. As the date approaches, uncovered visits go to hourly staff (timanställda)
- Fixed staff are cheaper per hour but have contract obligations
- Hourly staff are more expensive but flexible

### ESS Configuration

```json
{
  "employeeCostGroups": [
    {
      "id": "fixed-contract",
      "employeeActivationCost": 0,
      "employeeActivationRatioWeight": 4
    },
    {
      "id": "hourly-staff",
      "employeeActivationCost": 500,
      "employeeActivationRatioWeight": 1
    }
  ]
}
```

**What this does:**

- `employeeActivationCost: 0` for fixed → no penalty for using them
- `employeeActivationCost: 500` for hourly → soft penalty discourages unnecessary activation
- `employeeActivationRatioWeight: 4:1` → try to maintain 80/20 ratio
- `Minimize activated employees` constraint → use fewer hourly staff
- `Maximize activated employee saturation` → if hourly staff IS activated, fill their shift fully

### Cost Definitions for Swedish Home Care

```json
{
  "contracts": [
    {
      "id": "fixedFullTime",
      "periodRules": [
        {
          "id": "dailyCost",
          "period": "DAY",
          "satisfiability": "PREFERRED",
          "costDefinition": {
            "baseMinutesLimit": 480,
            "baseHourlyCost": 220,
            "overtimeCostDetails": [
              {
                "overtimeMinutesLimit": 120,
                "overtimeHourlyCost": 330
              }
            ]
          }
        }
      ]
    },
    {
      "id": "hourlyCasual",
      "periodRules": [
        {
          "id": "dailyCost",
          "period": "DAY",
          "satisfiability": "PREFERRED",
          "costDefinition": {
            "baseMinutesLimit": 480,
            "baseHourlyCost": 280
          }
        }
      ]
    }
  ]
}
```

### How This Syncs with FSR

1. ESS determines which employees work (preferring fixed, adding hourly only when needed)
2. FSR receives the activated employees as vehicles
3. FSR optimizes routes for the activated set
4. Combined cost = ESS shift costs + FSR travel costs

### Manager Dashboard Metrics

- Fixed vs hourly ratio per day/week/month
- Activation cost trends
- Overtime cost analysis
- Cost per visit (shift cost + travel cost / visits assigned)

---

## 5. Mandatory and Optional Shifts

**ESS Feature:** [Mandatory and optional shifts](https://docs.timefold.ai/employee-shift-scheduling/latest/shift-service-constraints/mandatory-and-optional-shifts)

### Mapping to CAIRE Visit Types

| CAIRE Visit Type                      | ESS Shift Type              | Priority | FSR Visit Type                     |
| ------------------------------------- | --------------------------- | -------- | ---------------------------------- |
| Daily mandatory (medication, toilet)  | MANDATORY shift, priority 1 | Highest  | Mandatory visit, priority 1        |
| Recurring weekly (cleaning, shopping) | OPTIONAL shift, priority 5  | Lower    | Optional visit with movable window |
| Bi-weekly/monthly (deep cleaning)     | OPTIONAL shift, priority 8  | Lowest   | Optional visit with broad window   |

### ESS Configuration

```json
{
  "globalRules": {
    "unassignedShiftRule": {
      "id": "caireShiftPriorities",
      "priorityWeights": [
        { "priority": "1", "weight": 100, "assignment": "MANDATORY" },
        { "priority": "3", "weight": 50, "assignment": "MANDATORY" },
        { "priority": "5", "weight": 10, "assignment": "OPTIONAL" },
        { "priority": "8", "weight": 1, "assignment": "OPTIONAL" }
      ]
    }
  }
}
```

### How This Works in the Loop

1. ESS creates mandatory shifts for daily demand peaks (must be staffed)
2. ESS creates optional shifts for movable visit capacity (staffed if possible)
3. FSR receives both types: mandatory visits MUST be assigned, optional MAY be left unassigned
4. If ESS over-provisioned (too many optional shifts), FSR leaves some vehicles idle → convergence check adjusts

---

## 6. Preferred Employees and Continuity

**ESS Feature:** [Shift assignments - preferred employees](https://docs.timefold.ai/employee-shift-scheduling/latest/shift-service-constraints/shift-assignments)

### Continuity Goal: < 10-15 Different Caregivers per Client per 14 Days

This requires synchronization between ESS and FSR:

**ESS role:** Ensure the SAME employees are consistently scheduled on the SAME days

```json
{
  "shifts": [
    {
      "id": "huddinge-vastra-mon-day",
      "preferredEmployees": ["lisa", "erik", "anna"],
      "start": "2026-02-10T07:00:00+01:00",
      "end": "2026-02-10T15:00:00+01:00"
    }
  ]
}
```

**FSR role:** Assign visits to the SAME employees who visited each client before

```json
{
  "visits": [
    {
      "id": "visit-client-123-med",
      "preferredVehicles": ["lisa"],
      "location": [59.2412, 17.9456]
    }
  ]
}
```

### Cross-Model Continuity Sync

```
After FSR optimization run N:
  Extract: Lisa visited clients [123, 456, 789] on Mondays

Before ESS optimization run N+1:
  Feed: preferredEmployees on Monday shifts = ["lisa", ...]

Before FSR optimization run N+1:
  Feed: preferredVehicles on visits for clients [123, 456, 789] = ["lisa"]
```

### ESS Concurrent Shift Rules for Continuity

Limit how many different employees can work a service area per day:

```json
{
  "globalRules": {
    "concurrentShiftsRules": [
      {
        "id": "maxCaregivers-huddinge-vastra",
        "includeShiftTags": ["huddinge-vastra"],
        "concurrentShiftsMax": 8
      }
    ]
  }
}
```

This indirectly limits client-caregiver diversity because fewer unique employees in the area = fewer different faces for clients.

---

## 7. Skill Matching

**ESS Feature:** [Skills and risk factors](https://docs.timefold.ai/employee-shift-scheduling/latest/shift-service-constraints/skills-and-risk-factors)

### Unified Skill IDs Across ESS and FSR

```json
// ESS: Employee skills
{
  "employees": [{
    "id": "lisa",
    "skills": [
      { "id": "medication" },
      { "id": "dementia" },
      { "id": "wound-care" }
    ]
  }]
}

// ESS: Shift requires skills (aggregated from visit requirements)
{
  "shifts": [{
    "id": "huddinge-vastra-mon-day",
    "requiredSkills": ["medication"],
    "preferredSkills": ["dementia"]
  }]
}

// FSR: Visit requires skills
{
  "visits": [{
    "id": "visit-client-123-medication",
    "requiredSkills": [{ "name": "medication" }]
  }]
}
```

### Skill Aggregation: Visits → Shift Requirements

When generating ESS demand, aggregate visit skills per hour slot:

```
08:00-09:00: 3 visits need "medication", 1 needs "dementia"
→ ESS shift at 08:00 requires: medication (hard), dementia (preferred)
→ ESS will assign an employee with medication skill, preferring one with dementia too
```

### Skill Expressions for Complex Requirements

ESS supports skill expressions (AND/OR logic):

```json
{
  "requiredSkillsExpression": {
    "type": "NODE",
    "operator": "AND",
    "operands": [
      { "type": "LEAF", "skillId": "medication" },
      {
        "type": "NODE",
        "operator": "OR",
        "operands": [
          { "type": "LEAF", "skillId": "dementia" },
          { "type": "LEAF", "skillId": "palliative" }
        ]
      }
    ]
  }
}
```

---

## 8. Pinning Synchronization

**ESS Feature:** [Manual intervention](https://docs.timefold.ai/employee-shift-scheduling/latest/manual-intervention)

### Pin State Must Be Consistent

| Scenario                             | ESS Pin State                                                | FSR Pin State                   |
| ------------------------------------ | ------------------------------------------------------------ | ------------------------------- |
| Approved slinga pattern              | Shift pinned to employee                                     | Visits pinned to vehicles       |
| New/unplanned schedule               | Shifts unpinned                                              | Visits unpinned                 |
| Partial disruption (1 employee sick) | Healthy employee shifts pinned, sick employee shift unpinned | Sick employee's visits unpinned |
| Fine-tuning after optimization       | Selected shifts unpinned for re-optimization                 | Corresponding visits unpinned   |

### Sync Logic

```typescript
// When ESS shift is pinned → corresponding FSR visits must be pinned
function syncPinState(essResult: ESSResult, fsrInput: FSRInput) {
  for (const shift of essResult.shifts) {
    if (shift.pinned && shift.employee) {
      // Find all FSR visits in this shift's time window
      const visitsInShift = fsrInput.visits.filter(
        (v) => v.startTime >= shift.start && v.endTime <= shift.end,
      );
      // Pin those visits to the same employee
      visitsInShift.forEach((v) => {
        v.pinned = true;
        v.pinnedVehicleId = shift.employee;
      });
    }
  }
}
```

---

## 9. Replacement Recommendations

**ESS Feature:** [Recommendations](https://docs.timefold.ai/employee-shift-scheduling/latest/recommendations)

### Two-Level Recommendation Flow

When an employee calls in sick:

```
Step 1: ESS Recommendation
  "Who should cover Lisa's shift?"
  → Returns ranked list: [Erik (score: +1medium), Anna (score: +1medium/-960soft)]
  → Erik is better because Anna has unpreferred time on Mondays

Step 2: FSR Recommendation (after shift is reassigned)
  "How should Lisa's visits be redistributed?"
  → Visits reassigned to Erik and other available employees
  → Route re-optimized for affected employees
```

### ESS Recommendation API Call

```json
{
  "maxNumberOfRecommendations": 3,
  "fitShiftId": "huddinge-vastra-mon-day-2026-02-10",
  "modelInput": {
    "employees": [...],
    "shifts": [
      {
        "id": "huddinge-vastra-mon-day-2026-02-10",
        "start": "2026-02-10T07:00:00+01:00",
        "end": "2026-02-10T15:00:00+01:00",
        "requiredSkills": ["medication"]
        // No employee assigned - Lisa is sick
      }
    ]
  }
}
```

### Mobile App: "Why Me?" Button

The recommendation API with `includeJustifications=true` provides explanations that can be shown in the caregiver mobile app:

```json
{
  "constraintDiffs": [
    {
      "constraintName": "Unassigned mandatory shift",
      "justification": {
        "description": "Mandatory shift 'Huddinge Vastra Mon Day' needs coverage."
      }
    },
    {
      "constraintName": "Required skill matched",
      "justification": {
        "description": "You have the required 'medication' skill."
      }
    }
  ]
}
```

---

## 10. Real-Time Planning

**ESS Features:** [Real-time planning](https://docs.timefold.ai/employee-shift-scheduling/latest/real-time-planning) + [Real-time planning preview](https://docs.timefold.ai/employee-shift-scheduling/latest/real-time-planning-preview)

### Disruption Response Workflow

```
1. Disruption detected (employee sick, visit cancelled, urgent visit)
   ↓
2. CAIRE determines response path:

   Same-day, shifts known → FSR only (fast path, 1-3 min)
   Same-day, need backup  → ESS recommendation + FSR re-route (2-5 min)
   Future schedule impact  → Full ESS+FSR loop (5-10 min)

3. ESS uses disruption rules to minimize shift changes:
   {
     "globalRules": {
       "disruptionRules": [{
         "id": "minimizeDisruption",
         "start": "2026-02-10",
         "end": "2026-02-11",
         "multiplier": 5  // Strong preference for stability
       }]
     }
   }

4. FSR uses from-patch to incrementally adjust routes

5. Planner sees diff view in Bryntum

6. Caregivers notified via mobile push
```

### ESS Real-Time Preview (from-patch)

The preview `from-patch` API enables incremental ESS changes without rebuilding the full dataset:

```json
{
  "patch": [
    {
      "op": "add",
      "path": "/employees[id=lisa]/unavailableTimeSpans/-",
      "value": {
        "start": "2026-02-10T00:00:00+01:00",
        "end": "2026-02-11T00:00:00+01:00"
      }
    },
    {
      "op": "add",
      "path": "/shifts[id=huddinge-vastra-mon-day-2026-02-10]/pinned",
      "value": false
    }
  ]
}
```

---

## 11. Swedish Labor Law Compliance

**ESS Feature:** [Configuring labor law compliance](https://docs.timefold.ai/employee-shift-scheduling/latest/scenarios/configuring-labor-law-compliance)

### Swedish Kollektivavtal Configuration

```json
{
  "contracts": [
    {
      "id": "svenskKollektivavtal",
      "periodRules": [
        {
          "id": "max40hPerWeek",
          "period": "WEEK",
          "minutesWorkedLimit": { "minutesWorkedMax": 2400 },
          "satisfiability": "PREFERRED"
        },
        {
          "id": "max48hPerWeekHard",
          "period": "WEEK",
          "minutesWorkedLimit": { "minutesWorkedMax": 2880 },
          "satisfiability": "REQUIRED"
        },
        {
          "id": "max10hPerDay",
          "period": "DAY",
          "minutesWorkedLimit": { "minutesWorkedMax": 600 },
          "satisfiability": "REQUIRED"
        }
      ],
      "minutesBetweenShiftsRules": [
        {
          "id": "11hDailyRest",
          "minimumMinutesBetweenShifts": 660,
          "scope": { "type": "duration", "duration": "P1D" },
          "satisfiability": "REQUIRED"
        }
      ],
      "consecutiveDaysWorkedRules": [
        {
          "id": "max5ConsecutiveDays",
          "maximum": 5,
          "satisfiability": "REQUIRED"
        }
      ],
      "rollingWindowRules": [
        {
          "id": "1DayOffPer7",
          "rollingWindow": { "type": "DAILY", "size": 7 },
          "consecutiveDaysOffLimit": { "consecutiveDaysOffMin": 1 },
          "satisfiability": "REQUIRED"
        }
      ]
    }
  ]
}
```

### Part-Time Contracts

```json
{
  "contracts": [
    {
      "id": "partTime75",
      "periodRules": [
        {
          "id": "max30hPerWeek",
          "period": "WEEK",
          "minutesWorkedLimit": { "minutesWorkedMax": 1800 },
          "satisfiability": "PREFERRED"
        }
      ]
    }
  ]
}
```

---

## 12. Solution Comparison

**Platform Feature:** [Comparing datasets](https://docs.timefold.ai/timefold-platform/latest/how-tos/comparing-runs)

### CAIRE Comparison Scenarios

| Comparison                       | What We Compare                       | User Value                   |
| -------------------------------- | ------------------------------------- | ---------------------------- |
| Manual slinga vs CAIRE-generated | ESS+FSR solution vs imported baseline | Challenge existing patterns  |
| Before/after disruption          | Original solution vs re-optimized     | Understand disruption impact |
| Different staffing levels        | Same visits, different employee pools | Staffing analysis            |
| Fixed-only vs hybrid staffing    | All fixed-contract vs fixed+hourly    | Cost-benefit analysis        |
| Different constraint weights     | Continuity-focused vs travel-focused  | Goal alignment               |

### Metrics Shown in Comparison

```
| Metric              | Manual Slinga | CAIRE Generated | Delta    |
|---------------------|---------------|-----------------|----------|
| Travel time         | 185 min       | 142 min         | -23%     |
| Visits assigned     | 45/45         | 45/45           | =        |
| Employees needed    | 10            | 9               | -1       |
| Efficiency          | 69%           | 78%             | +9pp     |
| Continuity score    | 8.2/client    | 6.1/client      | -2.1     |
| Total cost (SEK)    | 24,500        | 21,200          | -13%     |
| Overtime hours      | 3.5h          | 0.5h            | -86%     |
```

---

## 13. Incremental Changes (from-patch)

**Platform Feature:** [Real-time planning with /from-patch](https://docs.timefold.ai/timefold-platform/latest/how-tos/from-patch-endpoint)

### CAIRE Uses for from-patch

Both ESS and FSR support the from-patch API, creating a **natural versioning system** for schedule evolution:

```
ESS Dataset v1 (initial staffing)
  ↓ from-patch: "Lisa sick"
ESS Dataset v2 (Erik covers Lisa's shift)
  ↓ feeds into
FSR Dataset v1 (initial routing)
  ↓ from-patch: "Lisa's visits redistributed"
FSR Dataset v2 (updated routes)
  ↓ from-patch: "urgent visit added"
FSR Dataset v3 (new visit inserted)
```

Each version is traceable via `parentId` and `originId`, enabling full audit trail in both models.

---

## 14. Explainable AI for Mobile

**Platform Feature:** [Validating an optimized plan with Explainable AI](https://docs.timefold.ai/timefold-platform/latest/guides/validating-an-optimized-plan-with-explainable-ai)

### Caregiver Mobile App: "Why This Schedule?"

ESS and FSR both provide score analysis and constraint justifications. CAIRE exposes these in the mobile app:

**For caregivers:**

- "Why am I working Monday?" → ESS: "Your contract requires 40h/week, Monday is your preferred day"
- "Why this client first?" → FSR: "Closest to your starting location, saves 12 min travel"
- "Why not me for Mrs. Andersson?" → FSR: "Erik has the required wound-care skill"

**For clients (brukare):**

- "Why is Erik coming instead of Lisa?" → ESS: "Lisa is on vacation, Erik has the same skills"
- "Why did my visit time change?" → FSR: "Optimized to reduce your waiting time by 15 min"

### Mobile Gamification Metrics from ESS

| Metric               | Source                   | Gamification Use                                              |
| -------------------- | ------------------------ | ------------------------------------------------------------- |
| On-time percentage   | FSR actual vs planned    | "You were on time for 95% of visits this week"                |
| Shift fairness score | ESS balance constraints  | "Your workload is balanced with your team"                    |
| Continuity score     | FSR preferred vehicles   | "You maintained care continuity for 12 clients"               |
| Skill utilization    | ESS/FSR skill matching   | "Your wound-care skill was used 8 times this month"           |
| Travel efficiency    | FSR KPIs                 | "Your average travel between visits: 6 min (team avg: 8 min)" |
| Days off respected   | ESS time off constraints | "All your requested days off were honored"                    |

---

## 15. Uncovering Inefficiencies

**Platform Feature:** [Uncovering inefficiencies in operational planning](https://docs.timefold.ai/timefold-platform/latest/guides/uncovering-inefficiencies-in-operational-planning)

### Management Dashboard: ESS+FSR Combined Analysis

**Staffing inefficiencies (ESS):**

- Understaffed hours (demand > supply)
- Overstaffed hours (supply > demand by >20%)
- Skill gaps (visits unassigned due to missing skills)
- Cost outliers (high overtime, excessive hourly staff usage)
- Fairness imbalances (some employees consistently overworked)

**Route inefficiencies (FSR):**

- High travel time per visit (> 15 min avg)
- Geographic imbalances (some areas consistently understaffed)
- Low utilization employees (< 60% service time)
- Unassigned visits (capacity issues)

**Combined insights:**

- "You need 1 more employee with medication skill on Tuesdays 07:00-09:00"
- "Moving Client 456 from Vastra to Ostra service area would save 45 min/day travel"
- "Lisa is consistently underutilized Wednesdays -- consider reassigning her shifts"

---

## 16. Real-Time Disruption Recommendations

**Platform Feature:** [Responding to disruptions with real-time planning](https://docs.timefold.ai/timefold-platform/latest/guides/responding-to-disruptions-with-real-time-replanning)

### Planner Workflow: Employee Calls in Sick

```
1. Planner marks Lisa as sick in CAIRE
   ↓
2. CAIRE calls ESS Recommendation API:
   "Who should cover Lisa's Huddinge Vastra Mon Day shift?"
   → Erik (best fit: has skills, lives nearby, fair workload)
   → Anna (second: has skills, would cause overtime)
   → Suggested: call hourly employee Karin
   ↓
3. Planner selects Erik → CAIRE calls ESS from-patch:
   - Remove Lisa's shift
   - Assign Erik to the shift
   ↓
4. CAIRE calls FSR from-patch:
   - Unpin Lisa's visits
   - Run re-optimization with Erik replacing Lisa
   - Pin all other employees' routes
   ↓
5. Planner sees diff view in Bryntum:
   - Lisa's visits redistributed to Erik + remaining employees
   - Travel impact: +12 min total
   - 0 unassigned visits
   ↓
6. Planner approves → push notification to Erik's mobile app
   "You've been assigned to cover Huddinge Vastra today.
    Your first visit is at 07:15. Tap for route."
```

---

## 17. Maps and Navigation

**Platform Features:** [Maps service](https://docs.timefold.ai/timefold-platform/latest/how-tos/maps-service) + [Traffic awareness](https://docs.timefold.ai/timefold-platform/latest/guides/designing-routing-plans-with-traffic-awareness)

### CAIRE Map Configuration

Timefold provides an **OSRM Sweden map** out of the box. CAIRE uses:

- **FSR routing:** OSRM Sweden map for accurate Swedish road routing
- **ESS travel:** Haversine (as-the-crow-flies) for home→shift distance (sufficient for shift assignment)
- **Mobile app:** FSR waypoints for turn-by-turn navigation display

### Traffic Considerations

Timefold recommends buffers rather than real-time traffic for planning:

```json
{
  "config": {
    "model": {
      "overrides": {
        "travelTimeMultiplier": 1.2
      }
    }
  }
}
```

This 20% buffer accounts for Swedish urban traffic conditions without the complexity of real-time traffic data.

### Mobile App Navigation

FSR provides `itinerary` with waypoints per shift. The mobile app can:

1. Display the day's route on a map
2. Launch native navigation (Google Maps/Apple Maps/Waze) for each visit
3. Show estimated arrival times based on FSR route sequence
4. Update ETAs based on actual GPS position

---

## 18. Metrics Strategy

### Current State: FSR Metrics Only

CAIRE currently stores metrics from FSR solutions only. With ESS+FSR, we need a unified metrics layer.

### ESS Metrics to Store

| Metric Category        | Specific Metrics                                  | User              | Source                   |
| ---------------------- | ------------------------------------------------- | ----------------- | ------------------------ |
| **Staffing**           | Activated employees, fixed vs hourly ratio        | Manager           | ESS KPIs                 |
| **Cost**               | Total shift cost, overtime cost, activation cost  | Manager           | ESS cost management      |
| **Fairness**           | Working time fairness %, balance across employees | Manager, Employee | ESS fairness constraints |
| **Labor compliance**   | Days worked per week, rest hours, overtime hours  | Manager, HR       | ESS work limits          |
| **Disruption**         | Disruption percentage, shifts changed             | Planner           | ESS disruption rules     |
| **Shift patterns**     | Consecutive days worked, shift rotation adherence | Employee, HR      | ESS patterns             |
| **Time off**           | Days off per period, consecutive rest             | Employee          | ESS time off rules       |
| **Skills utilization** | Skill match rate, overqualification %             | Manager           | ESS skills               |
| **Travel (commute)**   | Home-to-shift distance, locations worked          | Employee          | ESS travel               |

### FSR Metrics (Already Stored)

| Metric Category | Specific Metrics                                             | User              | Source         |
| --------------- | ------------------------------------------------------------ | ----------------- | -------------- |
| **Travel**      | Total travel time, per-visit travel, first/last visit travel | Manager, Employee | FSR KPIs       |
| **Assignment**  | Assigned/unassigned visits, mandatory/optional               | Planner           | FSR KPIs       |
| **Utilization** | Service hours / shift hours (efficiency)                     | Manager           | FSR calculated |
| **Continuity**  | Preferred vehicle match rate                                 | Manager           | FSR KPIs       |
| **Cost**        | Vehicle/route costs                                          | Manager           | FSR KPIs       |

### Combined Metrics (New)

| Metric                   | Formula                                              | User            | Purpose            |
| ------------------------ | ---------------------------------------------------- | --------------- | ------------------ |
| **True efficiency**      | FSR service hours / ESS shift hours                  | Manager         | Primary KPI        |
| **Total cost per visit** | (ESS shift cost + FSR travel cost) / assigned visits | Manager         | Cost analysis      |
| **Staffing accuracy**    | ESS planned employees / actually needed              | Manager         | Planning quality   |
| **Schedule stability**   | 1 - (ESS disruption % + FSR reassignment %)          | Manager         | Stability tracking |
| **Caregiver diversity**  | Unique caregivers per client per 14 days             | Manager, Client | Continuity goal    |

### Gamification Metrics for Caregiver Mobile App

| Metric                | Display                               | Gamification                       |
| --------------------- | ------------------------------------- | ---------------------------------- |
| On-time rate          | "95% on time this week"               | Badge: "Punctuality Star"          |
| Travel efficiency     | "6 min avg travel (team: 8 min)"      | Leaderboard position               |
| Continuity maintained | "12 clients with consistent care"     | Badge: "Continuity Champion"       |
| Skill utilization     | "Medication skill used 8x this month" | Progress bar toward specialization |
| Shift fairness        | "Your hours: 38h (team avg: 37.5h)"   | Fairness indicator                 |
| Days off honored      | "100% of requests granted"            | Work-life balance score            |
| Client satisfaction   | "4.8/5 average rating"                | Client feedback badge              |
| Documentation quality | "98% notes completed on time"         | Compliance badge                   |

### Database Schema for Combined Metrics

```prisma
model OptimizationMetrics {
  id                    String   @id @default(uuid())
  scheduleId            String
  solutionId            String

  // ESS metrics
  essDatasetId          String?
  activatedEmployees    Int
  fixedEmployees        Int
  hourlyEmployees       Int
  totalShiftCostSek     Decimal?
  overtimeCostSek       Decimal?
  fairnessPercentage    Float?
  disruptionPercentage  Float?
  laborComplianceScore  Float?   // 100% = fully compliant

  // FSR metrics
  fsrDatasetId          String?
  totalTravelMinutes    Int
  assignedVisits        Int
  unassignedVisits      Int
  avgTravelPerVisit     Float?

  // Combined metrics
  trueEfficiency        Float?   // service hours / shift hours
  costPerVisit          Decimal? // total cost / assigned visits
  continuityScore       Float?   // unique caregivers per client
  scheduleStability     Float?   // 1 - disruption rate

  // Convergence metadata
  iterations            Int      @default(1)
  converged             Boolean  @default(true)
  travelOverheadLearned Float?   // learned overhead multiplier

  createdAt             DateTime @default(now())

  schedule              Schedule @relation(fields: [scheduleId])
  solution              Solution @relation(fields: [solutionId])
}
```

---

## 19. Iterative Convergence Loop

### Algorithm (Detailed)

```typescript
async function optimizeSchedule(
  visits: Visit[],
  employees: Employee[],
  serviceArea: ServiceArea,
): Promise<OptimizationResult> {
  // Phase 0: Estimate travel overhead from geography or learned profiles
  let overhead =
    getLearnedOverhead(serviceArea.id) ??
    bootstrapFromGeography(serviceArea, visits);

  let iteration = 0;
  let converged = false;
  let essResult: ESSResult;
  let fsrResult: FSRResult;

  while (!converged && iteration < 3) {
    iteration++;

    // Phase 1: ESS - Determine staffing
    const demand = generateDemandCurve(visits, overhead);
    essResult = await essClient.solve({
      employees: mapToESSEmployees(employees),
      shifts: generateShiftsFromDemand(demand),
      contracts: getSwedishLaborContracts(),
      globalRules: {
        minimumMaximumShiftsPerHourlyDemand: [demand],
        costsRules: getCostRules(),
      },
    });

    // Phase 2: FSR - Optimize routes
    fsrResult = await fsrClient.solve({
      vehicles: mapESSShiftsToFSRVehicles(essResult, employees),
      visits: mapToFSRVisits(visits),
      planningWindow: getPlanningWindow(visits),
    });

    // Phase 3: Convergence check
    const actualEfficiency =
      fsrResult.kpis.totalServiceMinutes / fsrResult.kpis.totalShiftMinutes;
    const unassigned = fsrResult.kpis.totalUnassignedVisits;

    if (unassigned === 0 && Math.abs(actualEfficiency - 1 / overhead) < 0.05) {
      converged = true;
    } else {
      // Adjust overhead with damping
      const actualOverhead =
        fsrResult.kpis.totalShiftMinutes / fsrResult.kpis.totalServiceMinutes;
      overhead = 0.7 * actualOverhead + 0.3 * overhead;
    }
  }

  // Store learned overhead for next time
  await updateLearnedOverhead(serviceArea.id, overhead);

  // Store combined metrics
  await storeMetrics(essResult, fsrResult, iteration, converged);

  return { essResult, fsrResult, iterations: iteration, converged };
}
```

---

## 20. Implementation Phases

### Phase A: ESS Foundation (2-3 weeks)

- ESS API client (`ESSClient.ts`)
- ESS type definitions (`ess.types.ts`)
- Employee → ESS employee mapper (`db-to-ess.mapper.ts`)
- Swedish labor law contract configuration
- Demand curve generator with geographic bootstrap
- Basic ESS→FSR bridge (shifts → vehicles)

### Phase B: Iterative Loop (2-3 weeks)

- Iterative optimization orchestrator
- Convergence check service
- Learned overhead profiles (TravelProfile model)
- Combined metrics storage
- GraphQL mutations for dual-model optimization

### Phase C: Cost and Staffing (1-2 weeks)

- Fixed vs hourly employee cost groups
- Employee activation cost configuration
- Cost optimization integration
- Manager cost dashboard

### Phase D: Continuity and Skills Sync (1-2 weeks)

- Cross-model continuity tracking (employee-client affinity)
- Skill synchronization (ESS ↔ FSR)
- Preferred employee sync (ESS ↔ FSR)
- Continuity metrics in dashboard

### Phase E: Real-Time and Recommendations (2-3 weeks)

- ESS recommendation API integration
- Two-level recommendation workflow (ESS shift + FSR route)
- from-patch integration for both models
- Disruption handling with ESS+FSR
- Push notifications to mobile app

### Phase F: Explainability and Mobile (2-3 weeks)

- Score analysis + justification exposure via GraphQL
- Mobile app "Why this schedule?" feature
- Gamification metrics from ESS
- Client (brukare) schedule transparency

### Phase G: Management Analytics (1-2 weeks)

- Combined ESS+FSR efficiency dashboard
- Staffing analysis (over/under staffing by hour)
- Skill gap detection
- Cost trend analysis
- Comparison views (manual vs CAIRE, before/after)

---

## References

### Timefold Documentation

- [ESS Introduction](https://docs.timefold.ai/employee-shift-scheduling/latest/introduction)
- [FSR Introduction](https://docs.timefold.ai/field-service-routing/latest/introduction)
- [ESS + FSR Relationship](https://docs.timefold.ai/field-service-routing/latest/scenarios/configuring-labor-law-compliance)
- [Demand-based scheduling](https://docs.timefold.ai/employee-shift-scheduling/latest/shift-service-constraints/demand-based-scheduling)
- [API usage](https://docs.timefold.ai/timefold-platform/latest/api/api-usage)
- [Maps service](https://docs.timefold.ai/timefold-platform/latest/how-tos/maps-service)

### CAIRE Documentation

- [SCHEDULE_SOLUTION_ARCHITECTURE.md](./SCHEDULE_SOLUTION_ARCHITECTURE.md)
- [OVERVIEW.md](./OVERVIEW.md)
- [MOVABLE_VISITS.md](./MOVABLE_VISITS.md)
- [SCHEDULING_MASTER_PRD.md](../05-prd/SCHEDULING_MASTER_PRD.md)
- [Hybrid Scheduling with Slingor](../../../apps/dashboard/public/platform/en/scheduling-with-slingor.html)
- [CAIRE Scheduling Platform](../../../apps/dashboard/public/platform/en/scheduling.html)

---

_Document created: 2026-02-08_  
_Next review: After Timefold ESS API verification and pricing confirmation_
