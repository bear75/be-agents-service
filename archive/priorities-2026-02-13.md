# Priority 1: Employee-to-ESS Mapper

**Project:** ESS+FSR Integration | **Sprint 1 Night 4** | **Branch:** feature/ess-fsr-sprint1-night4

**Description:** Create mapper that transforms CAIRE Employee database records into Timefold ESS employee format. Map: employee.id, skills, contractType to ESS contracts, home location (latitude/longitude), availability from ScheduleEmployee shifts, costGroup (fixed-contract vs hourly-staff based on employee.contractType).

**Expected outcome:**

- New file: apps/dashboard-server/src/services/bridge/mappers/db-to-ess.mapper.ts
- Function: mapEmployeesToESS(employees: Employee[]): ESSEmployee[]
- Maps skills, location, contracts, availability, cost groups
- Handles both fixed-contract and hourly employees
- Type-check passes

**Files:**

- apps/dashboard-server/src/services/bridge/mappers/db-to-timefold.mapper.ts (existing FSR mapper pattern)
- apps/dashboard-server/src/services/bridge/mappers/db-to-ess.mapper.ts (new)
- apps/dashboard-server/src/services/bridge/scheduling/swedish-labor-contracts.ts (from night 3)

**Dependencies:** Night 1, Night 3

**Complexity:** Medium

**Reference:** docs/docs_2.0/09-scheduling/ESS_FSR_PROJECT_PLAN.md
