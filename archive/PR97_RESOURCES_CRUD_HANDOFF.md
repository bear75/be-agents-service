# PR #97 — Resources CRUD: Handoff for Shridhar

> **PR:** https://github.com/CairePlatform/beta-appcaire/pull/97
> **Branch:** `feat/resources-crud-complete`
> **Date:** 2026-03-13

---

## 1. What This PR Does (Summary)

This PR adds the **Resources CRUD system** — 8 new database models, full backend CRUD resolvers, frontend pages, and a Timefold projection builder. It is the **prerequisite** for the upcoming CSV upload feature (Jira C0-398).

**Why it exists:** Currently, schedule data enters the system via seed scripts or pre-expanded JSON uploads. Every upload creates duplicate resources because there are no stable external IDs. This PR:

- Adds proper data models with `externalId` fields for upsert support
- Formalizes Swedish care concepts (insatser, tidsluckor, beroenden) as database entities
- Builds CRUD pages so orgs can manage their catalog and resources
- Adds a Timefold projection builder that constructs FSR input from the database

---

## 2. New Database Models (8 Added)

### 2.1 The Inset System

The "Inset" system formalizes Swedish care service types ("insatser") into reusable definitions.

| Model                | Purpose                    | Example                                                                         |
| -------------------- | -------------------------- | ------------------------------------------------------------------------------- |
| **Inset**            | Service type definition    | "Dusch" (defaultSpreadDelay: PT48H, defaultDuration: 25min, defaultPriority: 5) |
| **InsetGroup**       | Sequence of related insets | "Meals" = frukost → lunch → middag (PT3H spread between each)                   |
| **InsetGroupMember** | Join table with ordering   | frukost=seq 1, lunch=seq 2, middag=seq 3                                        |
| **DaySlot**          | Time-of-day window         | "Morgon" 07:00-10:00, "Lunch" 11:30-13:30, "Kvall" 19:00-22:00                  |

**How they relate:**

```
DaySlot ──defaultDaySlotId──> Inset ──insetId──> InsetGroupMember <── InsetGroup
                                │
              ┌─────────────────┼──────────────────┐
              ▼                 ▼                  ▼
        VisitTemplate         Visit         ClientDependencyRule
```

**Key points:**

- `Inset` has defaults (duration, priority, spread delay, required skills, day slot) — visits inherit but can override
- `insetId` is on **both** Visit and VisitTemplate — Visit can override its template's inset; enables direct queries
- All catalog data (Insets, DaySlots, InsetGroups, Skills) is **org-scoped** — no system-level shared data between organizations
- Each org gets its own catalog via `seedDefaultsForOrganization(orgId, tx)`

### 2.2 Dependencies and Groups

| Model                         | Purpose                                       | Example                                                  |
| ----------------------------- | --------------------------------------------- | -------------------------------------------------------- |
| **VisitDependency**           | Temporal ordering constraint between visits   | "Frukost must precede Lunch by at least PT3H30M"         |
| **VisitGroupMember**          | Join table for visit groups (double-staffing) | Two visits linked with sequence for same client/time     |
| **ClientDependencyRule**      | Per-client default dependency patterns        | "Client H015: dusch visits must have PT42H between them" |
| **ServiceAreaDependencyRule** | Per-area default dependency patterns          | "Huddinge: all visits min PT3H same-day gap"             |

**Dependency hierarchy (cascade):**

1. **VisitDependency** (concrete, highest priority) — explicit per-schedule
2. **ClientDependencyRule** (client-level defaults) — generates VisitDependencies when visits are materialized
3. **ServiceAreaDependencyRule** (area-level defaults) — fallback when no client rule exists

---

## 3. Operational Settings Cascade

Costs and revenues flow down through a cascade:

```
Organization (OperationalSettings, level="organization")
    ↓ fallback
ServiceArea (OperationalSettings, level="service_area" OR ServiceArea.costPerHour/revenuePerHour)
    ↓ fallback
Employee (OperationalSettings, level="employee" OR EmployeeCost.hourlySalary)
    ↓ fallback
Hardcoded (230 SEK cost, 534 SEK revenue)
```

**Where the cascade runs:**

- `getEffectiveDefaultHourlySalary()` — used by Timefold projection for vehicle costs
- `getEffectiveRevenuePerHour()` — used by solution metrics for revenue calculation
- `ensureEmployeeCostsFromDefaults()` — creates EmployeeCost records from cascade on CSV upload
- UI operational settings form — shows merged values from cascade

**File:** `apps/dashboard-server/src/services/operational-defaults.ts`

---

## 4. Seed Data System

All org catalog data is seeded per-organization — there is no system-level shared catalog.

| Script                  | Purpose                                          | What it creates                                                            |
| ----------------------- | ------------------------------------------------ | -------------------------------------------------------------------------- |
| `seed-org-defaults.ts`  | Exports `seedDefaultsForOrganization(orgId, tx)` | DaySlots (8), Insets (~30), InsetGroups (2), Skills (12) for one org       |
| `seed-org-bootstrap.ts` | CLI: bootstrap new org                           | Organization + OperationalSettings + ServiceArea + default catalog         |
| `seed-attendo.ts`       | Full Attendo Huddinge demo                       | Org + catalog + 81 clients + employees + 2-week schedule + visits from CSV |
| `seed.ts`               | **Deprecated**                                   | Legacy Stockholm Hemtjanst AB (no Insets/DaySlots/Skills)                  |

**Commands:**

```bash
yarn db:seed:attendo                    # Full Attendo demo
yarn db:seed:attendo --reset            # Truncate + seed
ORGANIZATION_ID=<uuid> yarn db:seed:org-defaults  # Seed catalog for existing org
CLERK_ORG_ID=org_xxx ORG_NAME="AB" ORG_SLUG=ab yarn db:seed:org  # Bootstrap new org
```

---

## 5. E2E Scheduling Flow

```
1. DATA IMPORT
   ├── Upload CSV → importAttendoSchedule → Schedule, Visits, Employees
   ├── Upload input JSON → createScheduleFromTimefoldJson
   └── Seed data → yarn db:seed:attendo

2. OPTIMIZATION
   ├── Via button → startOptimization → buildTimefoldModelInput → Timefold API
   ├── Upload output JSON → createSolutionFromTimefoldJson
   └── Upload patch → createSolutionFromPatch

3. WEBHOOK
   POST /webhooks/timefold → fetch output → map to Solution + Assignments + Metrics

4. DISPLAY
   Dashboard reads Solution + SolutionAssignments → Bryntum Scheduler
```

**The Timefold projection (`buildTimefoldModelInput`):**

- Builds FSR request from DB using all new models
- Time windows: `ensureTimeWindowMinDuration` ensures windows span at least visit duration
- Visit classification: pinned (isPinned=true), fixed-slot (priority 1-3), flexible
- Dependencies: generated from InsetGroup chains and client dependency rules
- Costs: resolved via operational settings cascade

---

## 6. Visit Semantics (FSR Alignment)

| Concept       | FSR API                                           | Our Backend                                              | Notes                                                          |
| ------------- | ------------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------------- |
| **Movable**   | No field; multi-day time windows                  | Expressed by wide time windows (multi-day)               | DB `isMovable` is deprecated; UI derives from time window span |
| **Pinned**    | `pinningRequested`                                | `Visit.isPinned`                                         | Correct                                                        |
| **Mandatory** | No field; derived from windows vs planning window | `Visit.isMandatory` is UI/business only, NOT sent to FSR | "Kritisk insats" = priority 1 + isMandatory for UI             |
| **Priority**  | `priority` (string "1"-"10")                      | `Visit.priority` default 6                               | 1=highest (Kritisk), 10=lowest                                 |

**VisitTemplate.preferredTimeSlot:** Free-text string (not FK to DaySlot). Values should match `DaySlot.name` (e.g., "morgon", "lunch", "kvall") for consistency. No FK needed today; convention only.

---

## 7. Known Bugs from CRUD Audit

### CRITICAL

1. **Client type resolvers not registered** — Root `resolvers/index.ts` missing `Client: clientResolvers.Client`. Client addresses, contacts, skills, preferences, monthly allocations will NOT resolve.

### HIGH

2. **createEmployee/updateEmployee missing Decimal conversion** — `homeLatitude`, `homeLongitude`, `contractedHoursPerWeek`, etc. passed as raw numbers instead of `Prisma.Decimal`
3. **createAddress/updateAddress missing Decimal conversion** — `latitude`, `longitude` not converted
4. **updateOperationalSettings Decimal conversion** — `defaultHourlySalary`, `overtimeMultiplier`, etc.
5. **updateVisit not using mapVisit()** — Check-in/check-out coordinate Decimals not converted

### MEDIUM

6. **~20+ missing translation keys** — Various `resources.skills.*`, `common.saved`, `resources.visits.form.*`
7. **InsetManagement/InsetFormDialog hardcoded Swedish** — Not using `t()` for strings

---

## 8. Type Safety Tech Debt

### Category 1: `as unknown as GraphQLType` (72 files)

Every CRUD resolver returns `result as unknown as Type` to bridge Prisma → GraphQL type mismatch.

```typescript
// Current pattern in 72+ resolvers:
return result as unknown as DaySlot;
```

**Fix:** Create a shared mapper or use `Prisma.XGetPayload<...>` return types.

### Category 2: `as any` in projection (1 file, 8 instances) — HIGHEST PRIORITY

`buildTimefoldModelInput.ts` uses `metadata as any` to read CSV-specific fields.

```typescript
const meta = visit.metadata as any;
function buildTimefoldVisitFromDbVisit(visit: any, ...) { ... }
```

**Fix:** Define typed interfaces:

```typescript
interface VisitCsvMetadata {
  skift?: string;
  starttid?: string;
  antalTimMellanBesoken?: string;
  dubbel?: string | number;
}
```

### Category 3: Test type assertions (low priority)

Tests use `data as { ... }` — acceptable but could use generated types.

### How to find all instances:

```bash
rg "as any|as unknown|: any" apps/dashboard-server/src/ -g "*.ts" -g "!**/generated/**" -g "!**/node_modules/**" -l
```

---

## 9. Visit field gaps in createVisit/updateVisit

**Fixed in this PR:** `createVisit` and `updateVisit` resolvers now persist `insetId`, `isMandatory`, `isMovable`, `latestSlaEndTime`. Mutation GraphQL documents also request these fields.

---

## 10. File Reference

| Area                | Key Files                                                                                     |
| ------------------- | --------------------------------------------------------------------------------------------- |
| Schema              | `apps/dashboard-server/schema.prisma`                                                         |
| Seed defaults       | `apps/dashboard-server/src/seed-org-defaults.ts`                                              |
| Seed Attendo        | `apps/dashboard-server/src/seed-attendo.ts`                                                   |
| Seed bootstrap      | `apps/dashboard-server/src/seed-org-bootstrap.ts`                                             |
| Operational cascade | `apps/dashboard-server/src/services/operational-defaults.ts`                                  |
| Timefold projection | `apps/dashboard-server/src/services/timefold/projection/buildTimefoldModelInput.ts`           |
| CRUD resolvers      | `apps/dashboard-server/src/graphql/resolvers/{inset,daySlot,visitDependency,visitGroup,...}/` |
| GraphQL schema      | `packages/graphql/schema/dashboard/{types,queries,mutations}.graphql`                         |
| Frontend resources  | `apps/dashboard/src/components/Resources/`                                                    |
| Frontend pages      | `apps/dashboard/src/pages/resources/`                                                         |

---

## 11. How to Test

```bash
# 1. Install and generate types
yarn install && yarn generate

# 2. Run all checks
yarn format && yarn lint && yarn type-check && yarn test

# 3. Seed demo data
yarn workspace dashboard-server db:seed:attendo --reset

# 4. Start servers
yarn workspace dashboard-server dev   # port 4000
yarn workspace dashboard dev          # port 3000

# 5. Open dashboard
open http://localhost:3000/resources

# 6. Test CRUD for each resource type:
#    - Organization (Skills, Tags, Insets, InsetGroups, DaySlots, Operational Settings tabs)
#    - Service Areas (list, create, edit with dependency rules)
#    - Employees (list, create, edit with skills, tags, cost periods)
#    - Clients (list, create, edit with addresses, contacts, preferences, allocations)
#    - Visits (create, edit with inset, dependencies, groups)

# 7. Test GraphQL directly
open http://localhost:4000/graphql
# Query: { insets(organizationId: "...") { id name defaultSpreadDelay } }
# Query: { daySlots(organizationId: "...") { id name startTime endTime } }
```

---

## 12. Jira Tasks (for tracking)

**Epic:** [C0-406](https://caire.atlassian.net/browse/C0-406) — PR #97 Resources CRUD: Type Safety and Bug Fixes

| Task                                                | Priority | Summary                                                                                |
| --------------------------------------------------- | -------- | -------------------------------------------------------------------------------------- |
| [C0-407](https://caire.atlassian.net/browse/C0-407) | HIGHEST  | Fix `as any` in buildTimefoldModelInput.ts (8 instances)                               |
| [C0-408](https://caire.atlassian.net/browse/C0-408) | HIGH     | Fix `as unknown` casts in CRUD resolvers (72 files)                                    |
| [C0-409](https://caire.atlassian.net/browse/C0-409) | CRITICAL | Register Client type resolvers in root resolvers/index.ts                              |
| [C0-410](https://caire.atlassian.net/browse/C0-410) | HIGH     | Add Decimal conversions in create/update Employee, Address, OperationalSettings, Visit |
| [C0-411](https://caire.atlassian.net/browse/C0-411) | MEDIUM   | Add missing translation keys for Resources CRUD pages (~20 keys)                       |
| [C0-412](https://caire.atlassian.net/browse/C0-412) | LOW      | Fix test type assertions using generated GraphQL types                                 |
| [C0-413](https://caire.atlassian.net/browse/C0-413) | MEDIUM   | E2E verification of all Resources CRUD pages                                           |

**Recommended fix order:** C0-409 (critical bug) → C0-407 (as any) → C0-410 (Decimals) → C0-408 (as unknown systematic) → C0-411 (translations) → C0-413 (E2E test) → C0-412 (test types)

---

_Document created: 2026-03-13_
