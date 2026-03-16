# Priority 1: ESS API Client

**Project:** ESS+FSR Integration | **Sprint 1 Night 2** | **Branch:** feature/ess-fsr-sprint1-night2

**Description:** Create ESS HTTP client following same pattern as existing TimefoldClient.ts. Support fullSolve, getStatus, getSolution, and recommendations endpoints for the Employee Shift Scheduling model at /api/models/employee-scheduling/v1/.

**Expected outcome:**

- New file: apps/dashboard-server/src/services/timefold/ESSClient.ts
- Methods: solve(), getStatus(), getSolution(), getRecommendations()
- Uses same API key and error handling as existing TimefoldClient
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/timefold/TimefoldClient.ts (existing, use as pattern)
- apps/dashboard-server/src/services/timefold/ESSClient.ts (new)
- apps/dashboard-server/src/services/timefold/ess.types.ts (from night 1)

**Dependencies:** Night 1 (ess.types.ts)

**Complexity:** Medium

**Reference:** docs/docs_2.0/09-scheduling/ESS_FSR_PROJECT_PLAN.md
