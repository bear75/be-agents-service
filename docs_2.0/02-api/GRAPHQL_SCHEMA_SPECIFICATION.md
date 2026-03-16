# GraphQL Schema Specification

**Version:** 2.0
**Date:** 2025-12-17 (Updated: 2026-01-27)
**Purpose:** Single source of truth for GraphQL API specification
**Status:** ✅ **PARTIALLY IMPLEMENTED** - Employee & Client models updated (2026-01-27)
**Architecture:** Based on **NEW architecture** documented in `docs_2.0/` (NOT the old/existing schema)

---

## 🆕 Recent Updates (2026-01-27)

**Migration:** `20260127063104_add_data_model_2_0_fields`

The GraphQL schema has been updated to match the Data Model 2.0 specification:

### Employee Type Updates

- ✅ Renamed `homeServiceAreaId` → `serviceAreaId`
- ✅ Added fields: `gender`, `status`, `role`, `startDate`, `endDate`, `phoniroEmployeeId`, `recentClientVisits`
- ✅ Added relationships: `skills`, `tags`, `costs`, `preferences`
- ✅ Field resolvers implemented for all relationships

### Client Type Updates

- ✅ Added fields: `gender`, `birthYear`, `contactPerson`, `address`, `latitude`, `longitude`, `municipality`, `careLevel`, `diagnoses`, `allergies`, `languagePreference`
- ✅ Added relationships: `addresses`, `primaryAddress`, `contacts`, `preferences`, `allocations`
- ✅ Field resolvers implemented for all relationships

### New Relationship Types

- ✅ `Address`, `ClientContact`, `ClientPreference`, `MonthlyAllocation`
- ✅ `EmployeeSkill`, `EmployeeTag`, `EmployeeCost`, `EmployeePreference`

**Implementation Details:** See `docs/docs_2.0/03-data/data-model-implementation-notes.md`

---

## Executive Summary

This document defines where GraphQL schema files should be located and how they relate to mappers and the data model.

**Key Principle:** GraphQL schema files (`.graphql`) are the **single source of truth** for GraphQL API specification. Mapper specifications reference these schema files.

**⚠️ IMPORTANT:** GraphQL schema must be based on the **NEW architecture** documented in `docs_2.0/`, NOT the old/existing database schema. The new architecture uses:

- **Prisma ORM** (not Drizzle)
- **Normalized database structure** (see `docs_2.0/03-data/data-model.md`)
- **GraphQL + Express** (not Next.js API routes)
- **New data model** (target schema, not current schema)

---

## Single Source of Truth

### GraphQL Schema Files (Primary Source)

**Location:** `packages/server/src/graphql/schema/` (to be created)

**Structure:**

```
packages/server/src/graphql/schema/
├── index.graphql              # Main schema file (imports all)
├── types/
│   ├── common.graphql         # Common types (ID, DateTime, etc.)
│   ├── organization.graphql   # Organization types
│   ├── employee.graphql       # Employee types
│   ├── client.graphql         # Client types
│   ├── schedule.graphql       # Schedule types
│   ├── visit.graphql          # Visit types
│   ├── solution.graphql       # Solution/optimization types
│   ├── metrics.graphql        # Metrics types
│   └── input.graphql          # Input types for mutations
├── queries/
│   ├── schedule.queries.graphql
│   ├── employee.queries.graphql
│   ├── client.queries.graphql
│   └── ...
├── mutations/
│   ├── schedule.mutations.graphql
│   ├── employee.mutations.graphql
│   └── ...
└── subscriptions/
    ├── optimization.subscriptions.graphql
    └── ...
```

**Schema File Format:**

Each GraphQL schema file should include:

1. **Type definitions** with field descriptions
2. **Mapper annotations** (via comments) linking to mapper functions
3. **Data model references** (via comments) linking to database schema

**Example:**

```graphql
# packages/server/src/graphql/schema/types/schedule.graphql

"""
Schedule represents a planning period (day/week/month) with visits and employees.

@mapper: mapScheduleToBryntum (see MAPPER_SPECIFICATIONS.md section 2.1)
@dataModel: schedules table (see docs_2.0/03-data/data-model.md - NEW architecture)
@prismaSchema: packages/prisma/schema.prisma (to be created for new architecture)
@architecture: Based on docs_2.0/01-architecture/architecture.md (target architecture)
"""
type Schedule {
  """
  Unique identifier for the schedule.
  @mapper: Direct mapping from schedules.id
  """
  id: ID!

  """
  Schedule name (e.g., "Week 1 - Stockholm")
  @mapper: Direct mapping from schedules.name
  """
  name: String!

  """
  Start date of the schedule period.
  @mapper: Direct mapping from schedules.dateFrom
  """
  dateFrom: DateTime!

  """
  End date of the schedule period.
  @mapper: Direct mapping from schedules.dateTo
  """
  dateTo: DateTime!

  """
  Schedule status (draft, published, archived).
  @mapper: Direct mapping from schedules.status (enum: scheduleStatus)
  """
  status: ScheduleStatus!

  """
  Employees assigned to this schedule.
  @mapper: mapScheduleEmployeesToResources (see MAPPER_SPECIFICATIONS.md section 2.2)
  @dataModel: schedule_employees table (many-to-many with employees)
  """
  employees: [Employee!]!

  """
  Visits in this schedule.
  @mapper: mapVisitsToEvents (see MAPPER_SPECIFICATIONS.md section 2.3)
  @dataModel: visits table (filtered by scheduleId)
  """
  visits: [Visit!]!

  """
  Current solution (optimization result) for this schedule.
  @mapper: mapSolutionToBryntum (see MAPPER_SPECIFICATIONS.md section 2.4)
  @dataModel: solutions table (linked via scheduleId)
  """
  solution: Solution

  """
  Metrics for this schedule.
  @mapper: mapMetricsToDisplay (see MAPPER_SPECIFICATIONS.md section 2.5)
  @dataModel: solution_metrics table
  """
  metrics: ScheduleMetrics
}

"""
Schedule status enumeration.
@dataModel: scheduleStatus enum (see docs_2.0/03-data/data-model.md)
@prismaSchema: packages/prisma/schema.prisma (to be created)
"""
enum ScheduleStatus {
  DRAFT
  PUBLISHED
  ARCHIVED
}
```

---

## Mapper Specifications

**Location:** `docs_2.0/02-api/MAPPER_SPECIFICATIONS.md`

**Purpose:** Detailed mapper function specifications that reference GraphQL schema files.

**Key Sections:**

1. External Systems → Normalized Database
2. Normalized Database → GraphQL (automatic via Prisma)
3. GraphQL → Bryntum (frontend mappers)
4. GraphQL → Timefold (optimization API mappers)

**Mapper Documentation Format:**

Each mapper in `MAPPER_SPECIFICATIONS.md` should reference:

- **GraphQL Type:** Which GraphQL type(s) it maps to/from
- **GraphQL Schema File:** Location of the schema definition
- **Data Model Doc:** Reference to `docs_2.0/03-data/data-model.md` (NEW architecture)
- **Prisma Schema:** Reference to `packages/prisma/schema.prisma` (to be created)

**Example:**

```markdown
### 2.1 Schedule → Bryntum Mapper

**Mapper Function:** `mapScheduleToBryntum(schedule: Schedule): BryntumScheduleData`

**GraphQL Type:** `Schedule` (see `packages/server/src/graphql/schema/types/schedule.graphql`)

**Input:** GraphQL `Schedule` type (from `getSchedule` query)

**Output:** Bryntum SchedulerPro data format

**Mapping Details:**

- `schedule.id` → `bryntumData.id`
- `schedule.employees` → `bryntumData.resources` (via `mapEmployeeToResource`)
- `schedule.visits` → `bryntumData.events` (via `mapVisitToEvent`)
- `schedule.solution.assignments` → `bryntumData.assignments`
```

---

## Data Model Reference

**Location:** `docs_2.0/03-data/data-model.md`

**Purpose:** Database schema documentation for the **NEW architecture** (target schema)

**⚠️ Important:** This references the **NEW architecture** documented in `docs_2.0/`, NOT the old/existing schema.

**Relationship:**

- **Data Model Doc** (`docs_2.0/03-data/data-model.md`) → **Prisma Schema** (`packages/prisma/schema.prisma`) → **GraphQL Schema** → **Mapper Specs**

**Note:** The Prisma schema will be created based on the new data model documentation, not from the old Drizzle schema.

---

## Architecture Flow (NEW Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│              DATA MODEL DOCUMENTATION (NEW)                  │
│         docs_2.0/03-data/data-model.md                        │
│         (Target schema for new architecture)                  │
│         (NOT the old/existing schema)                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              PRISMA SCHEMA (To Be Created)                   │
│         packages/prisma/schema.prisma                        │
│         (Based on new data model, not old schema)            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              GRAPHQL SCHEMA (Single Source of Truth)         │
│         packages/server/src/graphql/schema/*.graphql          │
│         (Defines GraphQL types, queries, mutations)           │
│         (Based on new architecture, not old schema)           │
│         (Includes mapper annotations in comments)            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              MAPPER SPECIFICATIONS                           │
│         docs_2.0/02-api/MAPPER_SPECIFICATIONS.md            │
│         (References GraphQL schema files)                    │
│         (Documents transformation logic)                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              IMPLEMENTATION                                   │
│         packages/server/src/graphql/resolvers/                │
│         packages/client/src/features/scheduling/lib/mappers/  │
└─────────────────────────────────────────────────────────────┘
```

**⚠️ Key Point:** GraphQL schema is based on the **NEW architecture** (`docs_2.0/`), NOT the old/existing database schema.

---

## Implementation Status

### ✅ Completed

- [x] **NEW architecture documentation** (`docs_2.0/01-architecture/architecture.md`)
- [x] **NEW data model documentation** (`docs_2.0/03-data/data-model.md`) - Target schema
- [x] Mapper specifications (`docs_2.0/02-api/MAPPER_SPECIFICATIONS.md`)
- [x] API design documentation (`docs_2.0/02-api/API_DESIGN.md`)

**Note:** The old database schema (`src/lib/db/schema/schema.ts`) is NOT used as a reference. GraphQL schema must be based on the NEW architecture.

### ⚠️ To Be Implemented

- [ ] GraphQL schema files (`.graphql`) - **SINGLE SOURCE OF TRUTH**
- [ ] Mapper annotations in GraphQL schema comments
- [ ] GraphQL code generation from schema files
- [ ] TypeScript types generated from GraphQL schema
- [ ] Update MAPPER_SPECIFICATIONS.md to reference GraphQL schema files

---

## Next Steps

1. **Create GraphQL Schema Files**
   - Set up `packages/server/src/graphql/schema/` directory structure
   - Define all types in `.graphql` files based on **NEW architecture** (`docs_2.0/`)
   - Reference `docs_2.0/03-data/data-model.md` (NOT old schema)
   - Add mapper annotations in comments
   - Add data model references in comments

2. **Update Mapper Specifications**
   - Add references to GraphQL schema file locations
   - Link each mapper to specific GraphQL types
   - Ensure consistency between schema and mapper docs

3. **Code Generation**
   - Set up GraphQL codegen to generate TypeScript types
   - Generate resolver types from schema
   - Generate client types for frontend

4. **Documentation Updates**
   - Update `API_DESIGN.md` to reference GraphQL schema files
   - Update `architecture.md` to show schema file location
   - Update `MIGRATION_STRATEGY.md` if needed

---

## Related Documents

- **API Design:** `API_DESIGN.md` - Overall API architecture
- **Mapper Specifications:** `MAPPER_SPECIFICATIONS.md` - Detailed mapper docs
- **Data Model:** `../03-data/data-model.md` - Database schema docs
- **Architecture:** `../01-architecture/architecture.md` - System architecture
- **Migration Strategy:** `../04-migration/MIGRATION_STRATEGY.md` - Migration plan

---

**Status:** This document defines the target state. GraphQL schema files need to be created as the single source of truth, based on the **NEW architecture** documented in `docs_2.0/`, NOT the old/existing database schema.

**Key References:**

- **New Architecture:** `docs_2.0/01-architecture/architecture.md`
- **New Data Model:** `docs_2.0/03-data/data-model.md`
- **API Design:** `docs_2.0/02-api/API_DESIGN.md`
- **Mapper Specs:** `docs_2.0/02-api/MAPPER_SPECIFICATIONS.md`
