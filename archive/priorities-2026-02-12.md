# Priority 1: Swedish Labor Law Contract Config

**Project:** ESS+FSR Integration | **Sprint 1 Night 3** | **Branch:** feature/ess-fsr-sprint1-night3

**Description:** Create Swedish labor law configuration as ESS contract definitions. Implement kollektivavtal rules: max 40h/week (preferred), max 48h/week (hard), 11h daily rest, max 5 consecutive days, break requirements. Support full-time and part-time (75%) contract templates. Store as organization-level configuration.

**Expected outcome:**

- New file: apps/dashboard-server/src/services/bridge/scheduling/swedish-labor-contracts.ts
- Function: getSwedishLaborContracts(contractType: 'fullTime' | 'partTime75')
- Returns ESS-formatted contract with periodRules, minutesBetweenShiftsRules, consecutiveDaysWorkedRules, rollingWindowRules
- Unit test with expected contract output
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/scheduling/swedish-labor-contracts.ts (new)
- apps/dashboard-server/src/services/timefold/ess.types.ts (contract types)

**Dependencies:** Night 1

**Complexity:** Medium

**Reference:** docs/docs_2.0/09-scheduling/ESS_FSR_PROJECT_PLAN.md
