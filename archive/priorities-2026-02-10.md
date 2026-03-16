# Priority 1: ESS Type Definitions

**Project:** ESS+FSR Integration | **Sprint 1 Night 1** | **Branch:** feature/ess-fsr-sprint1-night1

**Description:** Create TypeScript type definitions for Timefold Employee Shift Scheduling API. Define all ESS input/output types: employees, shifts, contracts, globalRules, skills, availability, costGroups, demandDetails, and ESS response format (shift assignments, KPIs, metrics).

**Expected outcome:**

- New file: apps/dashboard-server/src/services/timefold/ess.types.ts
- All ESS API types defined matching Timefold OpenAPI spec
- Types exported for use by mapper and client
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/timefold/types.ts (existing FSR types for reference)
- apps/dashboard-server/src/services/timefold/ess.types.ts (new)

**Dependencies:** None

**Complexity:** Medium

**Reference:** docs/docs_2.0/09-scheduling/ESS_FSR_PROJECT_PLAN.md
