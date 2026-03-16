# Priority 1: Demand Curve Generator (Service Hours)

**Project:** ESS+FSR Integration | **Sprint 1 Night 5** | **Branch:** feature/ess-fsr-sprint1-night5

**Description:** Create demand curve generator that aggregates CAIRE visits into ESS hourly demand format (minimumMaximumShiftsPerHourlyDemand). For each hour slot, count concurrent visits and calculate employees needed. This is SERVICE HOURS ONLY -- travel overhead will be added in Sprint 2.

**Expected outcome:**

- New file: apps/dashboard-server/src/services/bridge/scheduling/demand-curve.service.ts
- Function: generateDemandCurve(visits: Visit[], overheadMultiplier: number): ESSDemandDetails[]
- Aggregates visits per hour slot (07:00-08:00, 08:00-09:00, etc.)
- Calculates concurrent employees needed per slot
- Applies overhead multiplier to inflate for travel
- Returns ESS minimumMaximumShiftsPerHourlyDemand format
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/scheduling/demand-curve.service.ts (new)
- apps/dashboard-server/src/services/timefold/ess.types.ts (demand types)

**Dependencies:** Night 1

**Complexity:** Medium

**Reference:** docs/docs_2.0/09-scheduling/ESS_FSR_PROJECT_PLAN.md
