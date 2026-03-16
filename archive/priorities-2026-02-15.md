# Priority 1: Sprint 1 Integration Test

**Project:** ESS+FSR Integration | **Sprint 1 Night 6** | **Branch:** feature/ess-fsr-sprint1-night6

**Description:** Create integration test that verifies Sprint 1 ESS foundation components work together. Load sample employees and visits from dashboard-server, run mapEmployeesToESS, generateDemandCurve, and verify output shapes match ESS API expectations. Add a simple test script or Vitest integration test.

**Expected outcome:**

- New file: apps/dashboard-server/src/services/bridge/**tests**/ess-foundation.integration.test.ts (or similar)
- Test: Load 2-3 employees + 5-10 visits, run mappers, assert output structure
- Document any missing fields or API mismatches for Sprint 2
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/mappers/db-to-ess.mapper.ts
- apps/dashboard-server/src/services/bridge/scheduling/demand-curve.service.ts
- apps/dashboard-server/src/services/bridge/scheduling/swedish-labor-contracts.ts
- apps/dashboard-server/src/services/timefold/ess.types.ts

**Dependencies:** Nights 1-5

**Complexity:** Low

**Reference:** docs/docs_2.0/09-scheduling/ESS_FSR_PROJECT_PLAN.md
