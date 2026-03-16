# CAIRE Database Schema – Complete Data Model v2.0

> **📌 Status:** Target schema with current fields integrated  
> **Last Updated:** 2026-03-07  
> **Migration Plan:** See `REFACTORING_PLAN.md`  
> **Schema:** `apps/dashboard-server/schema.prisma` · **Client:** `apps/dashboard-server/src/prisma.ts` · **Migrations:** `apps/dashboard-server/migrations/`  
> **Related:** [Atlassian Wiki - TWC Space](https://caire.atlassian.net/wiki/spaces/TWC/overview)  
> **Constraints & dependencies:** For visit dependencies (preceding, minDelay), visit groups (e.g. Dubbel), and schema-driven constraint list see [CAIRE_SCHEDULING_PRD § Resources & schema-driven constraints](../05-prd/CAIRE_SCHEDULING_PRD.md#resources--schema-driven-constraints) and [JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES](../05-prd/JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES.md). Those PRD entities may be added to this schema in a future update.

---

## Document Purpose

This document defines the **complete target database schema** for the CAIRE scheduling platform, combining:

1. New structural requirements (from `data-model.md`)
2. Existing field definitions (from `src/lib/db/schema/schema.ts`)
3. Prototype requirements (from PRDs)

**Format:** Each table follows this structure:

- **Purpose**: What this table represents
- **Fields**: Complete field list with types, constraints, defaults
- **Indexes**: Performance optimization indexes
- **Relationships**: Foreign keys and references
- **Prototype Support**: Which features this supports

---

## Design Principles

1. **Domain-Driven Design**: Clear separation between domain concepts and solver-specific data
2. **Normalized Structure**: Minimal JSON blobs, proper foreign keys
3. **Template Support**: Full support for Slinga templates and movable visits
4. **Problem/Solution Pattern**: Separate problems (input) from solutions (output)
5. **Patch-Based Fine-Tuning**: Incremental optimization without cloning
6. **Comprehensive Metrics**: Complete metrics at all levels
7. **Multi-Tenant Isolation**: All data properly scoped to organizations
8. **Audit Trail**: Created/updated timestamps on all tables
9. **Soft Deletes**: Where appropriate, use `deletedAt` instead of hard deletes

---

## Entity Relationship Diagram

```
organizations ──┬─< templates (Slinga) ─┬─< template_visits
                │                       ├─< template_employees
                │                       ├─< template_constraints
                │                       └─< template_configurations
                │
                ├─< scenarios (constraint sets)
                │
                ├─< solver_configs (solver configurations)
                │
                ├─< service_areas (hierarchical) ─┬─< operational_settings
                │                                  └─< (self-reference for hierarchy)
                │
                ├─< schedule_groups (planning sessions)
                │      └─< schedules ─┬─< visits ──┬─< visit_skills
                │                     │           ├─< visit_tags
                │                     │           └─< visit_preferences
                │                     │
                │                     ├─< schedule_employees ──┬─< employee_shifts ─< employee_breaks
                │                     │                        └─< (shift/break data)
                │                     │
                │                     ├─< schedule_metrics
                │                     ├─< schedule_service_areas
                │                     └─< schedule_constraints
                │
                ├─< visit_templates (movable visits) ─< movable_visit_assignments
                │
                ├─< clients ─┬─< addresses
                │           ├─< client_contacts
                │           ├─< client_preferences
                │           └─< monthly_allocations
                │
                └─< employees ──┬─< employee_skills
                                ├─< employee_tags
                                ├─< employee_vehicles ─< vehicles
                                └─< employee_costs

problems ─┬─ (referenced by schedules)
          └─< problem_metrics

solutions ──┬─< solution_assignments
            ├─< solution_events
            ├─< solution_metrics ─┬─< employee_solution_metrics
            │                     ├─< client_solution_metrics
            │                     └─< service_area_solution_metrics
            └─< solution_comparisons
```

---

## Schema alignment: documentation vs actual database

The **actual** database is defined in `apps/dashboard-server/schema.prisma` and uses:

- **Table names:** PascalCase, singular (e.g. `Organization`, `Visit`, `ScheduleEmployee`). What you see in TablePlus/Postgres matches Prisma model names.
- **Column names:** camelCase (e.g. `organizationId`, `startTime`, `durationMinutes`).

This doc and the Bryntum timeplan often use **snake_case** or conceptual names (e.g. `organizations`, `schedule_employees`, `visit_skills`). Use the mapping below when reading the timeplan or implementing against the real DB.

### Doc / timeplan name → actual Prisma table

| Doc / timeplan (snake_case or conceptual) | Actual table (Prisma)     |
| ----------------------------------------- | ------------------------- |
| organizations                             | Organization              |
| organization_members                      | OrganizationMember        |
| service_areas                             | ServiceArea               |
| employees                                 | Employee                  |
| employee_skills                           | EmployeeSkill             |
| employee_shifts                           | ScheduleEmployeeShift     |
| employee_breaks                           | ScheduleEmployeeBreak     |
| clients                                   | Client                    |
| addresses                                 | Address                   |
| client_contacts                           | ClientContact             |
| client_preferences                        | ClientPreference          |
| monthly_allocations                       | MonthlyAllocation         |
| schedules                                 | Schedule                  |
| schedule_employees                        | ScheduleEmployee          |
| schedule_constraints                      | ScheduleConstraint        |
| schedule_metrics                          | ScheduleMetric            |
| schedule_service_areas                    | ScheduleServiceArea       |
| schedule_groups                           | ScheduleGroup             |
| visits                                    | Visit                     |
| visit_skills                              | VisitSkill                |
| visit_tags                                | VisitTag                  |
| visit_preferences                         | VisitPreference           |
| visit_templates                           | VisitTemplate             |
| movable_visit_assignments                 | MovableVisitAssignment    |
| templates (Slinga)                        | Template                  |
| template_visits                           | TemplateVisit             |
| problems                                  | Problem                   |
| problem_metrics                           | ProblemMetric             |
| solutions                                 | Solution                  |
| solution_assignments                      | SolutionAssignment        |
| solution_events                           | SolutionEvent             |
| solution_metrics                          | SolutionMetric            |
| employee_solution_metrics                 | EmployeeSolutionMetric    |
| client_solution_metrics                   | ClientSolutionMetric      |
| service_area_solution_metrics             | ServiceAreaSolutionMetric |
| scenarios                                 | Scenario                  |
| solver_configs                            | SolverConfig              |
| operational_settings                      | OperationalSettings       |
| vehicles                                  | Vehicle                   |
| employee_vehicles                         | EmployeeVehicle           |

### In doc/ERD but not in current Prisma schema

- **template_employees**, **template_constraints**, **template_configurations** — shown in the ERD as target Slinga template structure; not yet implemented. Template today has only Template + TemplateVisit.
- **visit_dependencies** (or VisitDependency) — **not in DB**. Required for Timefold FSR (preceding visit, minDelay or minDelayTo with minStartDateAdjuster, minStartTime, timezone). See [Timefold visit dependencies](https://docs.timefold.ai/field-service-routing/latest/visit-service-constraints/visit-dependencies) and [CAIRE_SCHEDULING_PRD § Dependencies](../05-prd/CAIRE_SCHEDULING_PRD.md#dependencies). To be added in a future migration.
- **Visit groups** (e.g. Dubbel) — no first-class table; currently inferred from Visit.metadata or similar. PRD expects schema/UI to keep visit group membership consistent when building FSR input.

When implementing from the Bryntum timeplan or this doc, use the Prisma client and the **actual** model names above; translate any snake_case table names from the timeplan using this section.

---

## Core Tables

### 1. organizations

**Purpose:** Multi-tenant root entity. Each organization represents a home care agency.

**Fields:**

| Field                  | Type      | Constraints      | Default       | Description                                            |
| ---------------------- | --------- | ---------------- | ------------- | ------------------------------------------------------ |
| `id`                   | text      | PK, NOT NULL     | -             | Unique organization identifier (Clerk org ID)          |
| `name`                 | text      | NOT NULL         | -             | Organization display name                              |
| `slug`                 | text      | NOT NULL, UNIQUE | -             | URL-safe identifier                                    |
| `address`              | text      | -                | -             | Physical address                                       |
| `phone`                | text      | -                | -             | Contact phone number                                   |
| `contactPerson`        | text      | -                | -             | Primary contact name                                   |
| `operationsManager`    | text      | -                | -             | Operations manager name                                |
| `email`                | text      | -                | -             | Contact email                                          |
| `languages`            | jsonb     | NOT NULL         | `["Swedish"]` | Supported languages array                              |
| `settings`             | jsonb     | NOT NULL         | {...}         | Platform configuration (see OrganizationSettings type) |
| `status`               | text      | NOT NULL         | `"trial"`     | Account status: trial, active, suspended, cancelled    |
| `trialEndsAt`          | timestamp | -                | -             | Trial expiration date                                  |
| `metadata`             | jsonb     | -                | `{}`          | Custom metadata                                        |
| `latitude`             | double    | -                | -             | Geocoded latitude from address                         |
| `longitude`            | double    | -                | -             | Geocoded longitude from address                        |
| `coordinatesUpdatedAt` | timestamp | -                | -             | Last geocoding update                                  |
| `createdAt`            | timestamp | NOT NULL         | NOW()         | Record creation timestamp                              |
| `updatedAt`            | timestamp | NOT NULL         | NOW()         | Last update timestamp                                  |

**Indexes:**

- `UNIQUE (slug)`
- `INDEX (latitude, longitude)` - for geospatial queries

**Relationships:**

- 1→N to all other tables (multi-tenant root)

**Prototype Support:**

- ✅ Multi-tenancy
- ✅ Organization settings
- ✅ Geocoding for map mode

---

### 2. organization_members

**Purpose:** Links users (from Clerk) to organizations with role-based access.

**Fields:**

| Field            | Type      | Constraints      | Default | Description                                  |
| ---------------- | --------- | ---------------- | ------- | -------------------------------------------- |
| `id`             | text      | PK, NOT NULL     | -       | Unique membership identifier                 |
| `organizationId` | text      | FK, NOT NULL     | -       | References organizations.id (CASCADE DELETE) |
| `userId`         | text      | NOT NULL, UNIQUE | -       | Clerk user ID                                |
| `role`           | text      | NOT NULL         | -       | User role: admin, scheduler, viewer, analyst |
| `permissions`    | jsonb     | -                | `[]`    | Fine-grained permissions array               |
| `metadata`       | jsonb     | -                | `{}`    | Additional user metadata                     |
| `createdAt`      | timestamp | NOT NULL         | NOW()   | Membership created                           |
| `updatedAt`      | timestamp | NOT NULL         | NOW()   | Last updated                                 |

**Indexes:**

- `INDEX (organizationId)`
- `INDEX (userId)`
- `UNIQUE (userId)` - one active membership per user

**Relationships:**

- N→1 to organizations
- Referenced by employees.userId

**Prototype Support:**

- ✅ Authentication
- ✅ Role-based access control

---

### 3. service_areas

**Purpose:** Hierarchical geographic/organizational areas with defaults for salary, continuity, priorities.

**Fields:**

| Field                          | Type          | Constraints  | Default           | Description                                       |
| ------------------------------ | ------------- | ------------ | ----------------- | ------------------------------------------------- |
| `id`                           | uuid          | PK           | gen_random_uuid() | Unique service area ID                            |
| `organizationId`               | text          | FK, NOT NULL | -                 | References organizations.id (CASCADE DELETE)      |
| `parentId`                     | uuid          | FK           | NULL              | Self-reference for hierarchy (SET NULL on delete) |
| `name`                         | text          | NOT NULL     | -                 | Service area name                                 |
| `fullPath`                     | text          | NOT NULL     | -                 | Hierarchical path: "Västra/Majorna"               |
| `shortName`                    | text          | NOT NULL     | -                 | Abbreviated name                                  |
| `level`                        | integer       | -            | 0                 | Hierarchy level (0=top, 1=child, etc.)            |
| `externalId`                   | text          | -            | -                 | External system identifier                        |
| `address`                      | text          | -            | -                 | Service area address                              |
| `latitude`                     | numeric(10,7) | -            | -                 | Area center latitude                              |
| `longitude`                    | numeric(10,7) | -            | -                 | Area center longitude                             |
| `continuityThresholdDefault`   | integer       | -            | -                 | Default continuity threshold                      |
| `continuityThresholdManual`    | integer       | -            | -                 | Manual override                                   |
| `unusedHoursRecapturePriority` | integer       | -            | -                 | Priority for reclaiming unused hours              |
| `revenuePerHour`               | numeric(10,2) | -            | -                 | Default revenue rate                              |
| `isAbstracted`                 | boolean       | NOT NULL     | false             | Is this a virtual/combined area?                  |
| `abstractedType`               | text          | -            | NULL              | Type: 'combined', 'disabled'                      |
| `representedServiceAreaIds`    | uuid[]        | -            | NULL              | Array of real area IDs                            |
| `metadata`                     | jsonb         | -            | -                 | Additional metadata                               |
| `createdAt`                    | timestamp     | NOT NULL     | NOW()             | Created timestamp                                 |
| `updatedAt`                    | timestamp     | NOT NULL     | NOW()             | Updated timestamp                                 |

**Indexes:**

- `INDEX (organizationId)`
- `INDEX (parentId)`
- `INDEX (externalId)`
- `UNIQUE (organizationId, fullPath)`

**Relationships:**

- N→1 to organizations
- Self-reference (parentId) for hierarchy
- Referenced by clients, employees, visits

**Prototype Support:**

- ✅ Service area filtering
- ✅ Hierarchical grouping
- ✅ Map mode (lat/lng)
- ✅ Analys mode (capacity by area)

---

### 4. employees

**Purpose:** Caregivers and staff who can be scheduled for visits.

> **📍 Route Optimization Note:** Employee home addresses are **not stored** in this table. Route optimization uses **office/depot locations** (from `organizations.address` or `service_areas.address`) as the start and end point for all employees. This data minimization approach reduces privacy risk while maintaining full optimization functionality.

**Fields:**

| Field                | Type          | Constraints  | Default           | Description                                          |
| -------------------- | ------------- | ------------ | ----------------- | ---------------------------------------------------- |
| `id`                 | uuid          | PK           | gen_random_uuid() | Unique employee ID                                   |
| `organizationId`     | text          | FK, NOT NULL | -                 | References organizations.id (CASCADE DELETE)         |
| `userId`             | text          | FK           | NULL              | References organization_members.userId (SET NULL)    |
| `externalId`         | text          | -            | -                 | External system ID (Carefox)                         |
| `phoniroEmployeeId`  | text          | -            | -                 | Phoniro system ID                                    |
| `name`               | text          | NOT NULL     | -                 | Full name                                            |
| `email`              | text          | NOT NULL     | -                 | Contact email                                        |
| `phone`              | text          | -            | -                 | Contact phone                                        |
| `status`             | text          | NOT NULL     | `"active"`        | Status: active, inactive, on_leave                   |
| `role`               | text          | NOT NULL     | `"CAREGIVER"`     | Role: CAREGIVER, DRIVER, COORDINATOR                 |
| `contractType`       | enum          | NOT NULL     | `"full_time"`     | Contract: full_time, part_time, hourly               |
| `startDate`          | timestamp     | -            | -                 | Employment start date                                |
| `endDate`            | timestamp     | -            | -                 | Employment end date                                  |
| `transportMode`      | text          | NOT NULL     | `"DRIVING"`       | Transport: DRIVING, CYCLING, WALKING, PUBLIC_TRANSIT |
| `monthlySalary`      | numeric(10,2) | -            | -                 | Fixed monthly salary                                 |
| `hourlySalary`       | numeric(10,2) | -            | -                 | Hourly rate                                          |
| `metadata`           | jsonb         | -            | `{}`              | Additional metadata                                  |
| `notes`              | text          | -            | -                 | Internal notes                                       |
| `recentClientVisits` | jsonb         | -            | `[]`              | Cache of recent client visits                        |
| `createdAt`          | timestamp     | -            | NOW()             | Created timestamp                                    |
| `updatedAt`          | timestamp     | -            | NOW()             | Updated timestamp                                    |

**Indexes:**

- `INDEX (organizationId)`
- `INDEX (phoniroEmployeeId)`
- `UNIQUE (organizationId, externalId)`

**Relationships:**

- N→1 to organizations
- N→1 to organization_members (optional)
- 1→N to employee_skills, employee_tags, employee_vehicles
- Referenced by schedule_employees, employee_costs

**Prototype Support:**

- ✅ Employee rows in calendar
- ✅ Skill matching
- ✅ Transport mode icons
- ✅ Contract type filtering

---

### 5. clients

**Purpose:** Care recipients who receive visits.

**Fields:**

| Field                | Type          | Constraints  | Default           | Description                                  |
| -------------------- | ------------- | ------------ | ----------------- | -------------------------------------------- |
| `id`                 | uuid          | PK           | gen_random_uuid() | Unique client ID                             |
| `organizationId`     | text          | FK, NOT NULL | -                 | References organizations.id (CASCADE DELETE) |
| `serviceAreaId`      | uuid          | FK           | -                 | References service_areas.id (SET NULL)       |
| `externalId`         | text          | -            | -                 | External system ID                           |
| `name`               | text          | NOT NULL     | -                 | Client full name                             |
| `ssn`                | text          | -            | -                 | Social security number (encrypted)           |
| `gender`             | text          | -            | -                 | Gender: male, female, other                  |
| `dateOfBirth`        | date          | -            | -                 | Date of birth                                |
| `email`              | text          | -            | -                 | Contact email                                |
| `phone`              | text          | -            | -                 | Contact phone                                |
| `address`            | text          | -            | -                 | Primary address (text)                       |
| `addressId`          | uuid          | FK           | -                 | References addresses.id                      |
| `latitude`           | numeric(10,7) | -            | -                 | Geocoded latitude                            |
| `longitude`          | numeric(10,7) | -            | -                 | Geocoded longitude                           |
| `municipality`       | text          | -            | -                 | Municipality name                            |
| `contactPerson`      | text          | -            | -                 | Primary contact name                         |
| `contactPhone`       | text          | -            | -                 | Contact phone                                |
| `contactEmail`       | text          | -            | -                 | Contact email                                |
| `careLevel`          | text          | -            | -                 | Care needs level                             |
| `diagnoses`          | text[]        | -            | -                 | Array of diagnoses                           |
| `allergies`          | text[]        | -            | -                 | Array of allergies                           |
| `languagePreference` | text          | -            | -                 | Preferred language                           |
| `notes`              | text          | -            | -                 | Care notes                                   |
| `monthlyAllocation`  | integer       | -            | -                 | Monthly hours allocated                      |
| `preferences`        | jsonb         | -            | -                 | Client preferences                           |
| `metadata`           | jsonb         | -            | `{}`              | Additional metadata                          |
| `createdAt`          | timestamp     | -            | NOW()             | Created timestamp                            |
| `updatedAt`          | timestamp     | -            | NOW()             | Updated timestamp                            |

**Indexes:**

- `INDEX (organizationId)`
- `INDEX (serviceAreaId)`
- `INDEX (latitude, longitude)`
- `UNIQUE (organizationId, externalId)`

**Relationships:**

- N→1 to organizations
- N→1 to service_areas
- N→1 to addresses (optional)
- 1→N to visits, visit_templates, client_contacts

**Prototype Support:**

- ✅ Client info in visit tooltips
- ✅ Map mode (geocoding)
- ✅ Client preferences matching

---

### 6. addresses

**Purpose:** Normalized address table for geocoding and location sharing.

**Fields:**

| Field            | Type          | Constraints  | Default           | Description                                  |
| ---------------- | ------------- | ------------ | ----------------- | -------------------------------------------- |
| `id`             | uuid          | PK           | gen_random_uuid() | Unique address ID                            |
| `organizationId` | text          | FK, NOT NULL | -                 | References organizations.id (CASCADE DELETE) |
| `street`         | text          | NOT NULL     | -                 | Street address                               |
| `city`           | text          | NOT NULL     | -                 | City name                                    |
| `postalCode`     | text          | NOT NULL     | -                 | Postal code                                  |
| `country`        | text          | NOT NULL     | `"Sweden"`        | Country                                      |
| `latitude`       | numeric(10,7) | -            | -                 | Geocoded latitude                            |
| `longitude`      | numeric(10,7) | -            | -                 | Geocoded longitude                           |
| `geojson`        | jsonb         | -            | -                 | GeoJSON representation                       |
| `geocodedAt`     | timestamp     | -            | -                 | Last geocoding timestamp                     |
| `createdAt`      | timestamp     | NOT NULL     | NOW()             | Created timestamp                            |
| `updatedAt`      | timestamp     | NOT NULL     | NOW()             | Updated timestamp                            |

**Indexes:**

- `INDEX (organizationId)`
- `INDEX (latitude, longitude)`
- `UNIQUE (organizationId, street, postalCode)` - prevent duplicates

**Relationships:**

- N→1 to organizations
- Referenced by clients, visits

**Prototype Support:**

- ✅ Map mode (marker placement)
- ✅ Route visualization
- ✅ Travel time calculation

---

### 7. templates (Slinga)

**Purpose:** Reusable daily or weekly schedule patterns.

**Fields:**

| Field            | Type      | Constraints  | Default           | Description                                   |
| ---------------- | --------- | ------------ | ----------------- | --------------------------------------------- |
| `id`             | uuid      | PK           | gen_random_uuid() | Unique template ID                            |
| `organizationId` | text      | FK, NOT NULL | -                 | References organizations.id (CASCADE DELETE)  |
| `name`           | text      | NOT NULL     | -                 | Template name: "Vecka 1 Dagskift"             |
| `description`    | text      | -            | -                 | Template description                          |
| `recurrenceRule` | text      | -            | -                 | Recurrence pattern (e.g., "Mon-Fri")          |
| `patternJson`    | jsonb     | -            | -                 | Sparse representation of visits/shifts        |
| `status`         | enum      | NOT NULL     | `"draft"`         | Status: draft, suggested, published, archived |
| `tags`           | text[]    | -            | -                 | Categorization tags                           |
| `validFrom`      | date      | -            | -                 | Template valid from date                      |
| `validTo`        | date      | -            | -                 | Template valid until date                     |
| `metadata`       | jsonb     | -            | `{}`              | Additional metadata                           |
| `createdAt`      | timestamp | NOT NULL     | NOW()             | Created timestamp                             |
| `updatedAt`      | timestamp | NOT NULL     | NOW()             | Updated timestamp                             |

**Indexes:**

- `INDEX (organizationId)`
- `INDEX (status)`

**Relationships:**

- N→1 to organizations
- 1→N to template_visits, template_employees, template_constraints

**Prototype Support:**

- ✅ Baseline templates
- ✅ Template instantiation
- ✅ Pre-planning with templates

---

### 8. schedule_groups

**Purpose:** Planning sessions that group multiple schedules (horizon planning).

**Fields:**

| Field            | Type      | Constraints  | Default           | Description                                  |
| ---------------- | --------- | ------------ | ----------------- | -------------------------------------------- |
| `id`             | uuid      | PK           | gen_random_uuid() | Unique schedule group ID                     |
| `organizationId` | text      | FK, NOT NULL | -                 | References organizations.id (CASCADE DELETE) |
| `templateId`     | uuid      | FK           | NULL              | References templates.id (SET NULL)           |
| `scenarioId`     | uuid      | FK, NOT NULL | -                 | References scenarios.id                      |
| `configId`       | uuid      | FK, NOT NULL | -                 | References solver_configs.id                 |
| `name`           | text      | NOT NULL     | -                 | Planning session name                        |
| `description`    | text      | -            | -                 | Session description                          |
| `startDate`      | date      | NOT NULL     | -                 | Planning horizon start                       |
| `endDate`        | date      | NOT NULL     | -                 | Planning horizon end                         |
| `metadata`       | jsonb     | -            | `{}`              | Additional metadata                          |
| `createdAt`      | timestamp | NOT NULL     | NOW()             | Created timestamp                            |
| `updatedAt`      | timestamp | NOT NULL     | NOW()             | Updated timestamp                            |

**Indexes:**

- `INDEX (organizationId)`
- `INDEX (templateId)`
- `INDEX (scenarioId)`
- `INDEX (startDate, endDate)`

**Relationships:**

- N→1 to organizations, templates (optional), scenarios, solver_configs
- 1→N to schedules

**Prototype Support:**

- ✅ Horizon planning
- ✅ Pre-planning sessions
- ✅ Analys mode (capacity planning)

---

### 9. schedules

**Purpose:** Individual schedule instances (daily or multi-day).

**Fields:**

| Field                 | Type          | Constraints  | Default           | Description                                            |
| --------------------- | ------------- | ------------ | ----------------- | ------------------------------------------------------ |
| `id`                  | uuid          | PK           | gen_random_uuid() | Unique schedule ID                                     |
| `organizationId`      | text          | FK, NOT NULL | -                 | References organizations.id (CASCADE DELETE)           |
| `scheduleGroupId`     | uuid          | FK           | NULL              | References schedule_groups.id (SET NULL)               |
| `templateId`          | uuid          | FK           | NULL              | References templates.id (SET NULL)                     |
| `scenarioId`          | uuid          | FK, NOT NULL | -                 | References scenarios.id                                |
| `configId`            | uuid          | FK, NOT NULL | -                 | References solver_configs.id                           |
| `problemId`           | uuid          | FK           | NULL              | References problems.id                                 |
| `solutionId`          | uuid          | FK           | NULL              | References solutions.id                                |
| `date`                | timestamp     | NOT NULL     | -                 | Schedule date (main identifier)                        |
| `startDate`           | timestamp     | NOT NULL     | -                 | Period start                                           |
| `endDate`             | timestamp     | NOT NULL     | -                 | Period end                                             |
| `name`                | text          | NOT NULL     | -                 | Schedule name                                          |
| `type`                | enum          | NOT NULL     | `"original"`      | Type: original, baseline, fine_tune, manual            |
| `status`              | enum          | NOT NULL     | `"draft"`         | Status: draft, unplanned, planned, published, archived |
| `scheduleType`        | enum          | NOT NULL     | `"production"`    | Environment: production, test, demo, training          |
| `scheduleTimespan`    | enum          | NOT NULL     | `"daily"`         | Timespan: daily, consolidated                          |
| `source`              | enum          | NOT NULL     | `"carefox"`       | Source: carefox, phoniro, ecare, manual, other         |
| `userId`              | text          | FK, NOT NULL | -                 | References organization_members.userId                 |
| `datasetId`           | text          | -            | -                 | Timefold dataset identifier                            |
| `rawInput`            | jsonb         | -            | -                 | Original input data (if needed)                        |
| `availableShiftHours` | numeric(10,2) | -            | -                 | Hours available for scheduling                         |
| `paidShiftHours`      | numeric(10,2) | -            | -                 | Hours paid to employees                                |
| `totalVisitHours`     | numeric(10,2) | -            | -                 | Total visit duration                                   |
| `estimatedStaffCost`  | numeric(10,2) | -            | -                 | Estimated staff cost                                   |
| `metadata`            | jsonb         | -            | `{}`              | Additional metadata                                    |
| `createdAt`           | timestamp     | NOT NULL     | NOW()             | Created timestamp                                      |
| `updatedAt`           | timestamp     | NOT NULL     | NOW()             | Updated timestamp                                      |
| `deletedAt`           | timestamp     | -            | NULL              | Soft delete timestamp                                  |

**Indexes:**

- `INDEX (organizationId)`
- `INDEX (scheduleGroupId)`
- `INDEX (problemId)`
- `INDEX (solutionId)`
- `INDEX (date, status)`
- `INDEX (userId)`

**Relationships:**

- N→1 to organizations, schedule_groups, templates, scenarios, solver_configs, problems, solutions, organization_members
- 1→N to visits, schedule_employees, schedule_metrics, schedule_service_areas

**Prototype Support:**

- ✅ Main calendar view
- ✅ Schedule type filtering
- ✅ Comparison mode (baseline vs optimized)
- ✅ Fine-tune workflows

---

### 10. visits

**Purpose:** Individual care visits to be scheduled.

**Fields:**

| Field                  | Type      | Constraints  | Default           | Description                                                                                                                    |
| ---------------------- | --------- | ------------ | ----------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `id`                   | uuid      | PK           | gen_random_uuid() | Unique visit ID                                                                                                                |
| `scheduleId`           | uuid      | FK, NOT NULL | -                 | References schedules.id (CASCADE DELETE)                                                                                       |
| `organizationId`       | text      | FK, NOT NULL | -                 | References organizations.id (CASCADE DELETE)                                                                                   |
| `clientId`             | uuid      | FK, NOT NULL | -                 | References clients.id (CASCADE DELETE)                                                                                         |
| `serviceAreaId`        | uuid      | FK           | -                 | References service_areas.id (SET NULL)                                                                                         |
| `addressId`            | uuid      | FK           | -                 | References addresses.id (SET NULL)                                                                                             |
| `movableVisitId`       | uuid      | FK           | NULL              | References visit_templates.id (SET NULL)                                                                                       |
| `externalId`           | text      | -            | -                 | External system ID                                                                                                             |
| `name`                 | text      | NOT NULL     | -                 | Visit name/type                                                                                                                |
| `description`          | text      | -            | -                 | Visit description                                                                                                              |
| `duration`             | integer   | NOT NULL     | -                 | Duration in minutes                                                                                                            |
| `plannedStartTime`     | timestamp | -            | -                 | Planned start time                                                                                                             |
| `plannedEndTime`       | timestamp | -            | -                 | Planned end time                                                                                                               |
| `minStartTime`         | timestamp | NOT NULL     | -                 | Earliest allowed start (hard constraint)                                                                                       |
| `maxStartTime`         | timestamp | NOT NULL     | -                 | Latest allowed start (hard constraint)                                                                                         |
| `maxEndTime`           | timestamp | NOT NULL     | -                 | Latest allowed end (hard constraint)                                                                                           |
| `preferredTimeWindows` | jsonb     | -            | `[]`              | Preferred time windows (soft constraint for waiting time reduction) - Timefold format: array of `{startTime, endTime}` objects |
| `allowedWindowStart`   | timestamp | -            | -                 | Allowed start (hard constraint)                                                                                                |
| `allowedWindowEnd`     | timestamp | -            | -                 | Allowed end (hard constraint)                                                                                                  |
| `requiredStaff`        | integer   | NOT NULL     | 1                 | Number of staff required (for double visits)                                                                                   |
| `priority`             | text      | -            | `"normal"`        | Priority: low, normal, high, urgent                                                                                            |
| `visitStatus`          | text      | NOT NULL     | `"planned"`       | Status: planned, cancelled, completed, missed                                                                                  |
| `visitCategory`        | enum      | -            | -                 | Category: daily, recurring                                                                                                     |
| `visitType`            | text      | -            | -                 | Type: morning, lunch, cleaning, etc.                                                                                           |
| `recurrenceType`       | text      | -            | -                 | Recurrence: weekly, bi-weekly, monthly                                                                                         |
| `pinned`               | boolean   | NOT NULL     | false             | Is visit pinned/locked?                                                                                                        |
| `isMovable`            | boolean   | NOT NULL     | false             | Can be moved during optimization                                                                                               |
| `notes`                | text      | -            | -                 | Visit notes                                                                                                                    |
| `metadata`             | jsonb     | -            | `{}`              | Additional metadata                                                                                                            |
| `createdAt`            | timestamp | NOT NULL     | NOW()             | Created timestamp                                                                                                              |
| `updatedAt`            | timestamp | NOT NULL     | NOW()             | Updated timestamp                                                                                                              |
| `deletedAt`            | timestamp | -            | NULL              | Soft delete timestamp                                                                                                          |

**Indexes:**

- `INDEX (scheduleId)`
- `INDEX (clientId)`
- `INDEX (serviceAreaId)`
- `INDEX (movableVisitId)`
- `INDEX (visitStatus, pinned)`
- `INDEX (plannedStartTime, plannedEndTime)`

**Relationships:**

- N→1 to schedules, organizations, clients, service_areas, addresses, visit_templates
- 1→N to visit_skills, visit_tags, visit_preferences
- Referenced by solution_assignments

**Prototype Support:**

- ✅ Calendar events
- ✅ Pinned visits (lock icon)
- ✅ Visit status colors
- ✅ Recurrence icons
- ✅ Time window constraints (hard: minStartTime/maxStartTime/maxEndTime, soft: preferredTimeWindows for waiting time reduction)
- ✅ Double staffing (👥 icon)

---

### 11. visit_templates (Movable Visits)

**Purpose:** Movable visit templates from municipalities (recurring work orders).

**Fields:**

| Field                  | Type      | Constraints  | Default           | Description                                              |
| ---------------------- | --------- | ------------ | ----------------- | -------------------------------------------------------- |
| `id`                   | uuid      | PK           | gen_random_uuid() | Unique template ID                                       |
| `organizationId`       | text      | FK, NOT NULL | -                 | References organizations.id (CASCADE DELETE)             |
| `clientId`             | uuid      | FK, NOT NULL | -                 | References clients.id (CASCADE DELETE)                   |
| `serviceAreaId`        | uuid      | FK           | -                 | References service_areas.id (SET NULL)                   |
| `externalId`           | text      | -            | -                 | External system ID                                       |
| `name`                 | text      | NOT NULL     | -                 | Template name                                            |
| `description`          | text      | -            | -                 | Template description                                     |
| `frequency`            | text      | NOT NULL     | -                 | Frequency: daily, weekly, bi-weekly, monthly             |
| `occurrences`          | integer   | -            | -                 | Number of occurrences                                    |
| `duration`             | integer   | NOT NULL     | -                 | Duration in minutes                                      |
| `requiredStaff`        | integer   | NOT NULL     | 1                 | Staff required                                           |
| `priority`             | text      | -            | `"normal"`        | Priority level                                           |
| `preferredWindowStart` | time      | -            | -                 | Preferred start time                                     |
| `preferredWindowEnd`   | time      | -            | -                 | Preferred end time                                       |
| `allowedWindowStart`   | time      | -            | -                 | Allowed start time                                       |
| `allowedWindowEnd`     | time      | -            | -                 | Allowed end time                                         |
| `status`               | enum      | NOT NULL     | `"draft"`         | Status: draft, suggested, preferred, final, converted    |
| `lifecycleStatus`      | enum      | -            | -                 | Lifecycle: identified, user_accepted, planned_1st, etc.  |
| `source`               | enum      | -            | `"user_manual"`   | Source: user_manual, pattern_detection, bulk_import, api |
| `notes`                | text      | -            | -                 | Template notes                                           |
| `metadata`             | jsonb     | -            | `{}`              | Additional metadata                                      |
| `createdAt`            | timestamp | NOT NULL     | NOW()             | Created timestamp                                        |
| `updatedAt`            | timestamp | NOT NULL     | NOW()             | Updated timestamp                                        |

**Indexes:**

- `INDEX (organizationId)`
- `INDEX (clientId)`
- `INDEX (status, lifecycleStatus)`

**Relationships:**

- N→1 to organizations, clients, service_areas
- Referenced by visits.movableVisitId
- 1→N to movable_visit_assignments

**Prototype Support:**

- ✅ Movable visits toggle
- ✅ Recurring patterns
- ✅ Pre-planning suggestions

---

### 12. schedule_employees

**Purpose:** Junction table linking employees to schedules with shift data.

**Fields:**

| Field        | Type      | Constraints  | Default           | Description                              |
| ------------ | --------- | ------------ | ----------------- | ---------------------------------------- |
| `id`         | uuid      | PK           | gen_random_uuid() | Unique assignment ID                     |
| `scheduleId` | uuid      | FK, NOT NULL | -                 | References schedules.id (CASCADE DELETE) |
| `employeeId` | uuid      | FK, NOT NULL | -                 | References employees.id (CASCADE DELETE) |
| `externalId` | text      | NOT NULL     | -                 | External system ID                       |
| `role`       | text      | -            | `"caregiver"`     | Role: caregiver, driver, coordinator     |
| `primary`    | boolean   | -            | false             | Is primary caregiver for continuity      |
| `shiftData`  | jsonb     | NOT NULL     | -                 | Shift and break definitions              |
| `notes`      | text      | -            | -                 | Assignment notes                         |
| `createdAt`  | timestamp | NOT NULL     | NOW()             | Created timestamp                        |
| `updatedAt`  | timestamp | NOT NULL     | NOW()             | Updated timestamp                        |

**Indexes:**

- `INDEX (scheduleId)`
- `INDEX (employeeId)`
- `UNIQUE (scheduleId, employeeId)`

**Relationships:**

- N→1 to schedules, employees
- 1→N to employee_shifts, employee_breaks

**Prototype Support:**

- ✅ Employee rows in calendar
- ✅ Shift definitions
- ✅ Break periods

---

### 13. employee_shifts

**Purpose:** Individual shifts within a schedule for an employee.

**Fields:**

| Field                  | Type           | Constraints  | Default           | Description                                       |
| ---------------------- | -------------- | ------------ | ----------------- | ------------------------------------------------- |
| `id`                   | uuid           | PK           | gen_random_uuid() | Unique shift ID                                   |
| `scheduleEmployeeId`   | uuid           | FK, NOT NULL | -                 | References schedule_employees.id (CASCADE DELETE) |
| `employeeId`           | uuid           | FK, NOT NULL | -                 | References employees.id (CASCADE DELETE)          |
| `scheduleId`           | uuid           | FK, NOT NULL | -                 | References schedules.id (CASCADE DELETE)          |
| `shiftExternalId`      | text           | NOT NULL     | -                 | External system ID                                |
| `minStartTime`         | timestamp      | NOT NULL     | -                 | Shift start time                                  |
| `maxEndTime`           | timestamp      | NOT NULL     | -                 | Shift end time                                    |
| `totalDurationSeconds` | integer        | -            | -                 | Total shift duration                              |
| `startLocationLat`     | numeric(18,14) | -            | -                 | Start location latitude                           |
| `startLocationLng`     | numeric(18,14) | -            | -                 | Start location longitude                          |
| `endLocationLat`       | numeric(18,14) | -            | -                 | End location latitude                             |
| `endLocationLng`       | numeric(18,14) | -            | -                 | End location longitude                            |
| `metadata`             | jsonb          | -            | `{}`              | Additional metadata                               |
| `createdAt`            | timestamp      | NOT NULL     | NOW()             | Created timestamp                                 |
| `updatedAt`            | timestamp      | NOT NULL     | NOW()             | Updated timestamp                                 |

**Indexes:**

- `INDEX (scheduleEmployeeId)`
- `INDEX (employeeId)`
- `INDEX (scheduleId)`
- `INDEX (scheduleId, employeeId, minStartTime)` - pre-planning optimization

**Relationships:**

- N→1 to schedule_employees, employees, schedules
- 1→N to employee_breaks

**Prototype Support:**

- ✅ Working hours display
- ✅ Non-working time shading

---

### 14. employee_breaks

**Purpose:** Break periods within employee shifts.

**Fields:**

| Field             | Type      | Constraints  | Default           | Description                                    |
| ----------------- | --------- | ------------ | ----------------- | ---------------------------------------------- |
| `id`              | uuid      | PK           | gen_random_uuid() | Unique break ID                                |
| `employeeShiftId` | uuid      | FK, NOT NULL | -                 | References employee_shifts.id (CASCADE DELETE) |
| `breakExternalId` | text      | NOT NULL     | -                 | External system ID                             |
| `minStartTime`    | timestamp | -            | -                 | Break start time                               |
| `maxStartTime`    | timestamp | -            | -                 | Break latest start                             |
| `maxEndTime`      | timestamp | -            | -                 | Break end time                                 |
| `duration`        | text      | NOT NULL     | -                 | Break duration (ISO 8601)                      |
| `breakType`       | text      | NOT NULL     | `"LUNCH"`         | Type: LUNCH, REST, OTHER                       |
| `costImpact`      | text      | NOT NULL     | `"UNPAID"`        | Impact: PAID, UNPAID                           |
| `metadata`        | jsonb     | -            | `{}`              | Additional metadata                            |
| `createdAt`       | timestamp | NOT NULL     | NOW()             | Created timestamp                              |
| `updatedAt`       | timestamp | NOT NULL     | NOW()             | Updated timestamp                              |

**Indexes:**

- `INDEX (employeeShiftId)`

**Relationships:**

- N→1 to employee_shifts

**Prototype Support:**

- ✅ Break periods (☕ toggle)
- ✅ Lunch break display
- ✅ Paid/unpaid break handling

---

### 15. scenarios

**Purpose:** Business-level constraint sets for optimization.

**Fields:**

| Field                     | Type      | Constraints | Default           | Description                                                    |
| ------------------------- | --------- | ----------- | ----------------- | -------------------------------------------------------------- |
| `id`                      | uuid      | PK          | gen_random_uuid() | Unique scenario ID                                             |
| `organizationId`          | text      | FK          | NULL              | References organizations.id (CASCADE DELETE) - NULL for global |
| `name`                    | text      | NOT NULL    | -                 | Scenario name: "Daglig Planering"                              |
| `description`             | text      | -           | -                 | Scenario description                                           |
| `configData`              | jsonb     | -           | -                 | Scenario configuration (weights, constraints)                  |
| `timefoldConfigurationId` | uuid      | FK          | NULL              | References timefold_configurations.id (SET NULL)               |
| `isDefault`               | boolean   | NOT NULL    | false             | Is default scenario                                            |
| `isActive`                | boolean   | NOT NULL    | true              | Is scenario active                                             |
| `createdAt`               | timestamp | NOT NULL    | NOW()             | Created timestamp                                              |
| `updatedAt`               | timestamp | NOT NULL    | NOW()             | Updated timestamp                                              |

**Indexes:**

- `INDEX (organizationId)`
- `INDEX (timefoldConfigurationId)`

**Relationships:**

- N→1 to organizations (nullable for global scenarios)
- N→1 to timefold_configurations
- Referenced by schedules, schedule_groups

**Prototype Support:**

- ✅ Optimization scenarios (5 presets)
- ✅ Editable weights
- ✅ Constraint toggles

---

### 16. solver_configs (Timefold Configurations)

**Purpose:** Low-level solver settings (engine-specific).

**Fields:**

| Field            | Type      | Constraints | Default           | Description                                                    |
| ---------------- | --------- | ----------- | ----------------- | -------------------------------------------------------------- |
| `id`             | uuid      | PK          | gen_random_uuid() | Unique config ID                                               |
| `organizationId` | text      | FK          | NULL              | References organizations.id (CASCADE DELETE) - NULL for global |
| `name`           | text      | NOT NULL    | -                 | Configuration name                                             |
| `description`    | text      | -           | -                 | Configuration description                                      |
| `engine`         | text      | NOT NULL    | `"Timefold"`      | Solver engine name                                             |
| `configJson`     | jsonb     | NOT NULL    | -                 | Solver-specific configuration                                  |
| `isDefault`      | boolean   | NOT NULL    | false             | Is default configuration                                       |
| `isActive`       | boolean   | NOT NULL    | true              | Is configuration active                                        |
| `createdAt`      | timestamp | NOT NULL    | NOW()             | Created timestamp                                              |
| `updatedAt`      | timestamp | NOT NULL    | NOW()             | Updated timestamp                                              |

**Indexes:**

- `INDEX (organizationId)`

**Relationships:**

- N→1 to organizations (nullable for global configs)
- Referenced by schedules, schedule_groups

**Prototype Support:**

- ✅ Solver configuration
- ✅ Termination settings

---

### 17. problems

**Purpose:** Normalized input for a schedule (domain-level problem definition).

**Fields:**

| Field              | Type      | Constraints  | Default           | Description                                                   |
| ------------------ | --------- | ------------ | ----------------- | ------------------------------------------------------------- |
| `id`               | uuid      | PK           | gen_random_uuid() | Unique problem ID                                             |
| `organizationId`   | text      | FK, NOT NULL | -                 | References organizations.id (CASCADE DELETE)                  |
| `description`      | text      | -            | -                 | Problem description                                           |
| `sourceTemplateId` | uuid      | FK           | NULL              | References templates.id (SET NULL) - if derived from template |
| `datasetId`        | text      | -            | -                 | Timefold dataset identifier                                   |
| `metadata`         | jsonb     | -            | `{}`              | Additional metadata                                           |
| `createdAt`        | timestamp | NOT NULL     | NOW()             | Created timestamp                                             |

**Indexes:**

- `INDEX (organizationId)`
- `INDEX (sourceTemplateId)`

**Relationships:**

- N→1 to organizations, templates (optional)
- Referenced by schedules
- 1→N to problem_metrics

**Prototype Support:**

- ✅ Problem/solution separation
- ✅ Reusable problems for fine-tune

---

### 18. solutions

**Purpose:** Solver result metadata (references Timefold dataset).

**Fields:**

| Field             | Type      | Constraints  | Default               | Description                                          |
| ----------------- | --------- | ------------ | --------------------- | ---------------------------------------------------- |
| `id`              | uuid      | PK           | gen_random_uuid()     | Unique solution ID                                   |
| `scheduleId`      | uuid      | FK, NOT NULL | -                     | References schedules.id (CASCADE DELETE)             |
| `datasetId`       | text      | NOT NULL     | -                     | Timefold dataset identifier                          |
| `parentDatasetId` | text      | -            | NULL                  | Parent solution (for fine-tune)                      |
| `originDatasetId` | text      | -            | NULL                  | Original solution (for patches)                      |
| `status`          | enum      | NOT NULL     | `"solving_scheduled"` | Status: solving_active, solving_completed, etc.      |
| `submittedAt`     | timestamp | -            | -                     | Job submission timestamp                             |
| `completedAt`     | timestamp | -            | -                     | Job completion timestamp                             |
| `summaryKpis`     | jsonb     | -            | -                     | High-level KPIs JSON                                 |
| `patchOperations` | jsonb     | -            | -                     | Patch operations for fine-tune                       |
| `score`           | text      | -            | -                     | Timefold score (e.g., "0hard/-1200medium/-5000soft") |
| `metadata`        | jsonb     | -            | `{}`                  | Additional metadata                                  |
| `createdAt`       | timestamp | NOT NULL     | NOW()                 | Created timestamp                                    |
| `updatedAt`       | timestamp | NOT NULL     | NOW()                 | Updated timestamp                                    |

**Indexes:**

- `INDEX (scheduleId)`
- `INDEX (datasetId)`
- `INDEX (status)`

**Relationships:**

- N→1 to schedules
- 1→N to solution_assignments, solution_events, solution_metrics

**Prototype Support:**

- ✅ Optimization progress tracking
- ✅ Fine-tune via patches
- ✅ Solution comparison

---

### 19. solution_assignments

**Purpose:** Assignment of visits to employees (solver output).

**Fields:**

| Field                | Type      | Constraints  | Default           | Description                                             |
| -------------------- | --------- | ------------ | ----------------- | ------------------------------------------------------- |
| `id`                 | uuid      | PK           | gen_random_uuid() | Unique assignment ID                                    |
| `solutionId`         | uuid      | FK, NOT NULL | -                 | References solutions.id (CASCADE DELETE)                |
| `visitId`            | uuid      | FK, NOT NULL | -                 | References visits.id (CASCADE DELETE)                   |
| `employeeId`         | uuid      | FK           | NULL              | References employees.id (SET NULL) - NULL if unassigned |
| `arrivalTime`        | timestamp | -            | -                 | Arrival at client location                              |
| `startTime`          | timestamp | -            | -                 | Visit start time                                        |
| `endTime`            | timestamp | -            | -                 | Visit end time                                          |
| `departureTime`      | timestamp | -            | -                 | Departure from client location                          |
| `travelTimeSeconds`  | integer   | -            | -                 | Travel time before visit                                |
| `waitingTimeSeconds` | integer   | -            | -                 | Waiting time before visit                               |
| `eventType`          | text      | -            | `"visit"`         | Type: visit, travel, waiting, break, office             |
| `metadata`           | jsonb     | -            | `{}`              | Additional metadata                                     |
| `createdAt`          | timestamp | NOT NULL     | NOW()             | Created timestamp                                       |

**Indexes:**

- `INDEX (solutionId)`
- `INDEX (visitId)`
- `INDEX (employeeId)`

**Relationships:**

- N→1 to solutions, visits, employees

**Prototype Support:**

- ✅ Visit assignments in calendar
- ✅ Travel time display
- ✅ Waiting time analysis

---

### 20. solution_events

**Purpose:** Per-second event log for a solution (travel, waiting, breaks, visits, office).

**Fields:**

| Field        | Type          | Constraints  | Default           | Description                                         |
| ------------ | ------------- | ------------ | ----------------- | --------------------------------------------------- |
| `id`         | uuid          | PK           | gen_random_uuid() | Unique event ID                                     |
| `solutionId` | uuid          | FK, NOT NULL | -                 | References solutions.id (CASCADE DELETE)            |
| `employeeId` | uuid          | FK, NOT NULL | -                 | References employees.id (CASCADE DELETE)            |
| `eventType`  | enum          | NOT NULL     | -                 | Type: travel, waiting, break, visit, office         |
| `startTime`  | timestamp     | NOT NULL     | -                 | Event start time                                    |
| `endTime`    | timestamp     | NOT NULL     | -                 | Event end time                                      |
| `duration`   | integer       | NOT NULL     | -                 | Duration in seconds                                 |
| `distance`   | numeric(10,2) | -            | -                 | Distance in km (for travel)                         |
| `cost`       | numeric(10,2) | -            | -                 | Cost for this event                                 |
| `revenue`    | numeric(10,2) | -            | -                 | Revenue for this event                              |
| `paid`       | boolean       | NOT NULL     | false             | Is this event paid time?                            |
| `clientId`   | uuid          | FK           | NULL              | References clients.id (SET NULL) - for visit events |
| `visitId`    | uuid          | FK           | NULL              | References visits.id (SET NULL) - for visit events  |
| `notes`      | text          | -            | -                 | Event notes                                         |
| `metadata`   | jsonb         | -            | `{}`              | Additional metadata                                 |
| `createdAt`  | timestamp     | NOT NULL     | NOW()             | Created timestamp                                   |

**Indexes:**

- `INDEX (solutionId)`
- `INDEX (employeeId)`
- `INDEX (eventType)`
- `INDEX (startTime, endTime)`

**Relationships:**

- N→1 to solutions, employees, clients (optional), visits (optional)

**Prototype Support:**

- ✅ Detailed event log
- ✅ Financial analysis
- ✅ Time tracking

---

## Metrics Tables

### 21. schedule_metrics

**Purpose:** Aggregated KPIs at schedule level (pre-optimization).

**Fields:**

| Field              | Type          | Constraints          | Default           | Description                              |
| ------------------ | ------------- | -------------------- | ----------------- | ---------------------------------------- |
| `id`               | uuid          | PK                   | gen_random_uuid() | Unique metric ID                         |
| `scheduleId`       | uuid          | FK, NOT NULL, UNIQUE | -                 | References schedules.id (CASCADE DELETE) |
| `shiftHoursFixed`  | numeric(10,2) | -                    | -                 | Fixed contract hours                     |
| `shiftHoursHourly` | numeric(10,2) | -                    | -                 | Hourly contract hours                    |
| `serviceHours`     | numeric(10,2) | -                    | -                 | Total service hours                      |
| `employeeCount`    | integer       | -                    | -                 | Number of employees                      |
| `visitCount`       | integer       | -                    | -                 | Number of visits                         |
| `clientCount`      | integer       | -                    | -                 | Number of clients                        |
| `travelTime`       | numeric(10,2) | -                    | -                 | Estimated travel time                    |
| `travelDistance`   | numeric(10,2) | -                    | -                 | Estimated travel distance                |
| `totalCost`        | numeric(10,2) | -                    | -                 | Total estimated cost                     |
| `totalRevenue`     | numeric(10,2) | -                    | -                 | Total estimated revenue                  |
| `continuityScore`  | numeric(5,2)  | -                    | -                 | Continuity score (0-100)                 |
| `overtimeHours`    | numeric(10,2) | -                    | -                 | Overtime hours                           |
| `notes`            | text          | -                    | -                 | Metric notes                             |
| `createdAt`        | timestamp     | NOT NULL             | NOW()             | Created timestamp                        |

**Indexes:**

- `INDEX (scheduleId)`

**Relationships:**

- 1→1 to schedules

**Prototype Support:**

- ✅ Metrics panel (📊 KPI)
- ✅ Pre-optimization stats

---

### 22. problem_metrics

**Purpose:** Statistics computed before optimization.

**Fields:**

| Field              | Type          | Constraints          | Default           | Description                             |
| ------------------ | ------------- | -------------------- | ----------------- | --------------------------------------- |
| `id`               | uuid          | PK                   | gen_random_uuid() | Unique metric ID                        |
| `problemId`        | uuid          | FK, NOT NULL, UNIQUE | -                 | References problems.id (CASCADE DELETE) |
| `employeeCount`    | integer       | -                    | -                 | Number of employees                     |
| `visitCount`       | integer       | -                    | -                 | Number of visits                        |
| `clientCount`      | integer       | -                    | -                 | Number of clients                       |
| `maxServiceHours`  | numeric(10,2) | -                    | -                 | Maximum service hours                   |
| `estimatedCost`    | numeric(10,2) | -                    | -                 | Estimated cost                          |
| `estimatedRevenue` | numeric(10,2) | -                    | -                 | Estimated revenue                       |
| `notes`            | text          | -                    | -                 | Metric notes                            |
| `createdAt`        | timestamp     | NOT NULL             | NOW()             | Created timestamp                       |

**Indexes:**

- `INDEX (problemId)`

**Relationships:**

- 1→1 to problems

**Prototype Support:**

- ✅ Problem statistics
- ✅ Capacity analysis

---

### 23. solution_metrics

**Purpose:** Aggregated results per solution (post-optimization KPIs).

**Fields:**

| Field                   | Type          | Constraints          | Default           | Description                                  |
| ----------------------- | ------------- | -------------------- | ----------------- | -------------------------------------------- |
| `id`                    | uuid          | PK                   | gen_random_uuid() | Unique metric ID                             |
| `solutionId`            | uuid          | FK, NOT NULL, UNIQUE | -                 | References solutions.id (CASCADE DELETE)     |
| `organizationId`        | text          | FK, NOT NULL         | -                 | References organizations.id (CASCADE DELETE) |
| `scheduleId`            | uuid          | FK, NOT NULL         | -                 | References schedules.id (CASCADE DELETE)     |
| `totalCost`             | numeric(10,2) | -                    | -                 | Total cost                                   |
| `totalRevenue`          | numeric(10,2) | -                    | -                 | Total revenue                                |
| `profit`                | numeric(10,2) | -                    | -                 | Profit (revenue - cost)                      |
| `utilizationPercentage` | numeric(5,2)  | -                    | -                 | Staff utilization %                          |
| `serviceHours`          | numeric(10,2) | -                    | -                 | Service hours delivered                      |
| `travelTimeSeconds`     | integer       | -                    | -                 | Total travel time                            |
| `waitingTimeSeconds`    | integer       | -                    | -                 | Total waiting time                           |
| `overtimeSeconds`       | integer       | -                    | -                 | Total overtime                               |
| `continuityScore`       | numeric(5,2)  | -                    | -                 | Continuity score                             |
| `unassignedVisits`      | integer       | -                    | -                 | Number of unassigned visits                  |
| `hardScore`             | integer       | -                    | -                 | Hard constraint score                        |
| `mediumScore`           | integer       | -                    | -                 | Medium constraint score                      |
| `softScore`             | integer       | -                    | -                 | Soft constraint score                        |
| `metadata`              | jsonb         | -                    | `{}`              | Additional KPIs                              |
| `createdAt`             | timestamp     | NOT NULL             | NOW()             | Created timestamp                            |
| `updatedAt`             | timestamp     | NOT NULL             | NOW()             | Updated timestamp                            |

**Indexes:**

- `INDEX (solutionId)`
- `INDEX (scheduleId)`
- `INDEX (organizationId)`

**Relationships:**

- 1→1 to solutions
- N→1 to schedules, organizations

**Prototype Support:**

- ✅ Metrics panel (📊 KPI)
- ✅ Comparison mode (delta metrics)
- ✅ Analys mode (KPI trends)

---

### 24. employee_solution_metrics

**Purpose:** Per-employee KPIs for a solution.

**Fields:**

| Field                   | Type          | Constraints  | Default           | Description                                     |
| ----------------------- | ------------- | ------------ | ----------------- | ----------------------------------------------- |
| `id`                    | uuid          | PK           | gen_random_uuid() | Unique metric ID                                |
| `solutionMetricId`      | uuid          | FK, NOT NULL | -                 | References solution_metrics.id (CASCADE DELETE) |
| `employeeId`            | uuid          | FK, NOT NULL | -                 | References employees.id (CASCADE DELETE)        |
| `visitCount`            | integer       | -            | -                 | Visits assigned                                 |
| `clientCount`           | integer       | -            | -                 | Unique clients served                           |
| `serviceHours`          | numeric(10,2) | -            | -                 | Service hours                                   |
| `travelTimeSeconds`     | integer       | -            | -                 | Travel time                                     |
| `waitingTimeSeconds`    | integer       | -            | -                 | Waiting time                                    |
| `overtimeSeconds`       | integer       | -            | -                 | Overtime                                        |
| `utilizationPercentage` | numeric(5,2)  | -            | -                 | Utilization %                                   |
| `cost`                  | numeric(10,2) | -            | -                 | Employee cost                                   |
| `revenue`               | numeric(10,2) | -            | -                 | Revenue generated                               |
| `continuityScore`       | numeric(5,2)  | -            | -                 | Continuity score                                |
| `metadata`              | jsonb         | -            | `{}`              | Additional metrics                              |
| `createdAt`             | timestamp     | NOT NULL     | NOW()             | Created timestamp                               |

**Indexes:**

- `INDEX (solutionMetricId)`
- `INDEX (employeeId)`

**Relationships:**

- N→1 to solution_metrics, employees

**Prototype Support:**

- ✅ Per-employee analysis
- ✅ Employee metrics columns

---

### 25. client_solution_metrics

**Purpose:** Per-client KPIs for a solution.

**Fields:**

| Field                     | Type          | Constraints  | Default           | Description                                     |
| ------------------------- | ------------- | ------------ | ----------------- | ----------------------------------------------- |
| `id`                      | uuid          | PK           | gen_random_uuid() | Unique metric ID                                |
| `solutionMetricId`        | uuid          | FK, NOT NULL | -                 | References solution_metrics.id (CASCADE DELETE) |
| `clientId`                | uuid          | FK, NOT NULL | -                 | References clients.id (CASCADE DELETE)          |
| `visitCount`              | integer       | -            | -                 | Visits assigned                                 |
| `serviceHours`            | numeric(10,2) | -            | -                 | Service hours                                   |
| `continuityScore`         | numeric(5,2)  | -            | -                 | Continuity score                                |
| `contactPersonPercentage` | numeric(5,2)  | -            | -                 | Contact person visit %                          |
| `uniqueCaregiversCount`   | integer       | -            | -                 | Number of caregivers                            |
| `metadata`                | jsonb         | -            | `{}`              | Additional metrics                              |
| `createdAt`               | timestamp     | NOT NULL     | NOW()             | Created timestamp                               |

**Indexes:**

- `INDEX (solutionMetricId)`
- `INDEX (clientId)`

**Relationships:**

- N→1 to solution_metrics, clients

**Prototype Support:**

- ✅ Per-client analysis
- ✅ Continuity tracking

---

### 26. service_area_solution_metrics

**Purpose:** Per-service-area KPIs for a solution.

**Fields:**

| Field                   | Type          | Constraints  | Default           | Description                                     |
| ----------------------- | ------------- | ------------ | ----------------- | ----------------------------------------------- |
| `id`                    | uuid          | PK           | gen_random_uuid() | Unique metric ID                                |
| `solutionMetricId`      | uuid          | FK, NOT NULL | -                 | References solution_metrics.id (CASCADE DELETE) |
| `serviceAreaId`         | uuid          | FK, NOT NULL | -                 | References service_areas.id (CASCADE DELETE)    |
| `visitCount`            | integer       | -            | -                 | Visits in area                                  |
| `employeeCount`         | integer       | -            | -                 | Employees in area                               |
| `clientCount`           | integer       | -            | -                 | Clients in area                                 |
| `serviceHours`          | numeric(10,2) | -            | -                 | Service hours                                   |
| `travelTimeSeconds`     | integer       | -            | -                 | Travel time                                     |
| `utilizationPercentage` | numeric(5,2)  | -            | -                 | Utilization %                                   |
| `cost`                  | numeric(10,2) | -            | -                 | Area cost                                       |
| `revenue`               | numeric(10,2) | -            | -                 | Area revenue                                    |
| `metadata`              | jsonb         | -            | `{}`              | Additional metrics                              |
| `createdAt`             | timestamp     | NOT NULL     | NOW()             | Created timestamp                               |

**Indexes:**

- `INDEX (solutionMetricId)`
- `INDEX (serviceAreaId)`

**Relationships:**

- N→1 to solution_metrics, service_areas

**Prototype Support:**

- ✅ Service area filtering
- ✅ Area capacity analysis

---

## Supporting Tables

### 27. employee_skills

**Purpose:** Skills and certifications for employees.

**Fields:**

| Field               | Type      | Constraints  | Default           | Description                              |
| ------------------- | --------- | ------------ | ----------------- | ---------------------------------------- |
| `id`                | uuid      | PK           | gen_random_uuid() | Unique skill assignment ID               |
| `employeeId`        | uuid      | FK, NOT NULL | -                 | References employees.id (CASCADE DELETE) |
| `skillName`         | text      | NOT NULL     | -                 | Skill name (e.g., "Dementia Care")       |
| `level`             | text      | -            | -                 | Skill level: basic, intermediate, expert |
| `certificationDate` | date      | -            | -                 | Certification date                       |
| `expiryDate`        | date      | -            | -                 | Expiry date                              |
| `metadata`          | jsonb     | -            | `{}`              | Additional metadata                      |
| `createdAt`         | timestamp | -            | NOW()             | Created timestamp                        |
| `updatedAt`         | timestamp | -            | NOW()             | Updated timestamp                        |

**Indexes:**

- `INDEX (employeeId)`
- `UNIQUE (employeeId, skillName)`

**Relationships:**

- N→1 to employees

**Prototype Support:**

- ✅ Skill matching
- ✅ Skill filtering (🎯 Kompetens)

---

### 28. employee_tags

**Purpose:** Tags for categorizing employees.

**Fields:**

| Field        | Type      | Constraints  | Default           | Description                              |
| ------------ | --------- | ------------ | ----------------- | ---------------------------------------- |
| `id`         | uuid      | PK           | gen_random_uuid() | Unique tag assignment ID                 |
| `employeeId` | uuid      | FK, NOT NULL | -                 | References employees.id (CASCADE DELETE) |
| `tagName`    | text      | NOT NULL     | -                 | Tag name                                 |
| `createdAt`  | timestamp | -            | NOW()             | Created timestamp                        |

**Indexes:**

- `INDEX (employeeId)`

**Relationships:**

- N→1 to employees

**Prototype Support:**

- ✅ Employee filtering

---

### 29. visit_skills

**Purpose:** Skills required for visits.

**Fields:**

| Field       | Type      | Constraints  | Default           | Description                           |
| ----------- | --------- | ------------ | ----------------- | ------------------------------------- |
| `id`        | uuid      | PK           | gen_random_uuid() | Unique skill requirement ID           |
| `visitId`   | uuid      | FK, NOT NULL | -                 | References visits.id (CASCADE DELETE) |
| `skillName` | text      | NOT NULL     | -                 | Required skill name                   |
| `required`  | boolean   | NOT NULL     | true              | Is skill mandatory?                   |
| `createdAt` | timestamp | -            | NOW()             | Created timestamp                     |

**Indexes:**

- `INDEX (visitId)`

**Relationships:**

- N→1 to visits

**Prototype Support:**

- ✅ Skill validation during drag

---

### 30. visit_tags

**Purpose:** Tags for categorizing visits.

**Fields:**

| Field       | Type      | Constraints  | Default           | Description                           |
| ----------- | --------- | ------------ | ----------------- | ------------------------------------- |
| `id`        | uuid      | PK           | gen_random_uuid() | Unique tag assignment ID              |
| `visitId`   | uuid      | FK, NOT NULL | -                 | References visits.id (CASCADE DELETE) |
| `tagName`   | text      | NOT NULL     | -                 | Tag name                              |
| `createdAt` | timestamp | -            | NOW()             | Created timestamp                     |

**Indexes:**

- `INDEX (visitId)`

**Relationships:**

- N→1 to visits

**Prototype Support:**

- ✅ Visit filtering

---

### 31. vehicles

**Purpose:** Vehicles available to the organization.

**Fields:**

| Field             | Type          | Constraints  | Default           | Description                                  |
| ----------------- | ------------- | ------------ | ----------------- | -------------------------------------------- |
| `id`              | uuid          | PK           | gen_random_uuid() | Unique vehicle ID                            |
| `organizationId`  | text          | FK, NOT NULL | -                 | References organizations.id (CASCADE DELETE) |
| `type`            | text          | NOT NULL     | -                 | Vehicle type: car, bike, scooter             |
| `capacity`        | integer       | -            | -                 | Passenger capacity                           |
| `range`           | integer       | -            | -                 | Range in km                                  |
| `costPerKm`       | numeric(10,2) | -            | -                 | Cost per kilometer                           |
| `emissionsRate`   | numeric(10,2) | -            | -                 | CO2 emissions g/km                           |
| `characteristics` | jsonb         | -            | `{}`              | Vehicle characteristics                      |
| `createdAt`       | timestamp     | NOT NULL     | NOW()             | Created timestamp                            |
| `updatedAt`       | timestamp     | NOT NULL     | NOW()             | Updated timestamp                            |

**Indexes:**

- `INDEX (organizationId)`

**Relationships:**

- N→1 to organizations
- Referenced by employee_vehicles

**Prototype Support:**

- ✅ Transport mode icons
- ✅ Route calculation

---

### 32. employee_vehicles

**Purpose:** Junction table linking employees to vehicles.

**Fields:**

| Field        | Type      | Constraints  | Default           | Description                              |
| ------------ | --------- | ------------ | ----------------- | ---------------------------------------- |
| `id`         | uuid      | PK           | gen_random_uuid() | Unique assignment ID                     |
| `employeeId` | uuid      | FK, NOT NULL | -                 | References employees.id (CASCADE DELETE) |
| `vehicleId`  | uuid      | FK, NOT NULL | -                 | References vehicles.id (CASCADE DELETE)  |
| `primary`    | boolean   | NOT NULL     | false             | Is primary vehicle                       |
| `notes`      | text      | -            | -                 | Assignment notes                         |
| `createdAt`  | timestamp | NOT NULL     | NOW()             | Created timestamp                        |

**Indexes:**

- `INDEX (employeeId)`
- `INDEX (vehicleId)`

**Relationships:**

- N→1 to employees, vehicles

**Prototype Support:**

- ✅ Transport mode selection

---

## Enums

### scheduleStatus

**Values:** `draft`, `unplanned`, `planned`, `published`, `archived`

**Usage:** schedules.status

### scheduleType

**Values:** `original`, `baseline`, `fine_tune`, `manual`, `test`, `production`, `demo`, `training`

**Usage:** schedules.type, schedules.scheduleType

### scheduleTimespan

**Values:** `daily`, `consolidated`

**Usage:** schedules.scheduleTimespan

### scheduleSource

**Values:** `carefox`, `phoniro`, `ecare`, `manual`, `other`

**Usage:** schedules.source

### optimizationStatus

**Values:** `solving_scheduled`, `solving_active`, `solving_completed`, `solving_incomplete`, `solving_failed`, `solving_terminated`, `solving_cancelled`

**Usage:** solutions.status

### constraintType

**Values:** `hard`, `medium`, `soft`

**Usage:** constraint definitions

### employeeContractType

**Values:** `full_time`, `part_time`, `hourly`

**Usage:** employees.contractType

### shiftType

**Values:** `day`, `evening`, `night`

**Usage:** shift definitions

### visitCategory

**Values:** `daily`, `recurring`

**Usage:** visits.visitCategory

**Note:** This field is derived from `recurrenceType`:

- `visitCategory: "daily"` = `recurrenceType` is `null`, `"daily"`, or `"other"` (shows as 📅1 in UI)
- `visitCategory: "recurring"` = `recurrenceType` is `"weekly"`, `"bi-weekly"`, or `"monthly"` (shows as 📅7/14/30 in UI)

The distinction helps identify which visits are part of a recurring pattern (can potentially be moved/adjusted during daily planning) vs one-off daily visits.

### visitFrequency

**Values:** `daily`, `weekly`, `bi-weekly`, `monthly`, `custom`

**Usage:** visit_templates.frequency

### movableVisitLifecycleStatus

**Values:** `identified`, `user_accepted`, `planned_1st`, `client_preferences`, `planned_client_preferences`, `planned_final`, `exported`

**Usage:** visit_templates.lifecycleStatus

### movableVisitSource

**Values:** `user_manual`, `pattern_detection`, `bulk_import`, `api`

**Usage:** visit_templates.source

### slingaStatus

**Values:** `draft`, `suggested`, `published`, `archived`

**Usage:** templates.status

### eventType

**Values:** `travel`, `waiting`, `break`, `visit`, `office`

**Usage:** solution_events.eventType, solution_assignments.eventType

---

## Prototype Requirements Coverage

| Feature                    | Tables/Fields Required            | Status |
| -------------------------- | --------------------------------- | ------ |
| **Schema Mode (Calendar)** |                                   |        |
| Timeline view              | schedules, visits, employees      | ✅     |
| Drag & drop                | visits, solution_assignments      | ✅     |
| Pinned visits              | visits.pinned                     | ✅     |
| Visit status colors        | visits.visitStatus                | ✅     |
| Recurrence icons           | visits.recurrenceType             | ✅     |
| Double staffing            | visits.requiredStaff              | ✅     |
| Transport icons            | employees.transportMode           | ✅     |
| Skill matching             | employee_skills, visit_skills     | ✅     |
| Time windows               | visits.preferred/allowed windows  | ✅     |
| Breaks                     | employee_breaks                   | ✅     |
| **Comparison Mode**        |                                   |        |
| Baseline vs optimized      | schedules.type, solutions         | ✅     |
| Side-by-side metrics       | solution_metrics                  | ✅     |
| Delta highlighting         | solution_metrics (computed)       | ✅     |
| **Map Mode**               |                                   |        |
| Visit markers              | addresses.latitude/longitude      | ✅     |
| Routes                     | solution_events (travel)          | ✅     |
| Service area overlay       | service_areas.latitude/longitude  | ✅     |
| **Analys Mode**            |                                   |        |
| Capacity planning          | schedule_metrics, problem_metrics | ✅     |
| Demand/supply curves       | schedule_metrics (computed)       | ✅     |
| Heatmaps                   | service_area_solution_metrics     | ✅     |
| **Templates**              |                                   |        |
| Slinga templates           | templates, template_visits        | ✅     |
| Movable visits             | visit_templates                   | ✅     |
| Pre-planning               | schedule_groups                   | ✅     |
| **Optimization**           |                                   |        |
| Scenarios                  | scenarios                         | ✅     |
| Solver configs             | solver_configs                    | ✅     |
| Fine-tune                  | solutions.patchOperations         | ✅     |
| Progress tracking          | solutions.status                  | ✅     |

---

## Migration Checklist

Based on `REFACTORING_PLAN.md`:

- [ ] **Phase 1:** Add missing fields (visits.pinned, employees.contractType, etc.)
- [ ] **Phase 2:** Create new tables (templates, schedule_groups, problems, solutions, addresses)
- [ ] **Phase 3:** Rename tables to snake_case (scheduleEmployees → schedule_employees)
- [ ] **Phase 4:** Migrate data (optimizationJobs → solutions, movableVisits → visit_templates)
- [ ] **Phase 5:** Remove deprecated tables

---

## Related Documentation

- **Migration Plan:** `REFACTORING_PLAN.md`
- **Schema (source of truth):** `apps/dashboard-server/schema.prisma`
- **Prisma client:** `apps/dashboard-server/src/prisma.ts`
- **Migrations:** `apps/dashboard-server/migrations/`
- **Prototype Roadmap:** `PROTOTYPE_ROADMAP.md`
- **Architecture:** `architecture.md`
- **PRDs:** [CAIRE_SCHEDULING_PRD](../05-prd/CAIRE_SCHEDULING_PRD.md), [CAIRE_PLANNING_PRD](../05-prd/CAIRE_PLANNING_PRD.md), [JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES](../05-prd/JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES.md)
- **Atlassian:** [TWC Space](https://caire.atlassian.net/wiki/spaces/TWC/overview)

---

**Last Updated:** 2026-03-07  
**Version:** 2.0  
**Status:** Target schema ready for implementation

**Recent Changes:**

- **2026-03-07:** Doc refresh. Updated Last Updated date; corrected Current Schema to `apps/dashboard-server/schema.prisma`; added pointer to CAIRE_SCHEDULING_PRD and JIRA_2.0 for visit dependencies, visit groups, and schema-driven constraints (to be added to schema in future). Fixed PRD links in footer (removed non-existent prd-umbrella and Feature PRD – Bryntum Calendar View).
- **2025-12-10:** Added `preferredTimeWindows` jsonb field to `visits` table (replaces separate `preferredWindowStart`/`preferredWindowEnd` timestamp fields). This field stores Timefold preferred time windows as a jsonb array of `{startTime, endTime}` objects for waiting time reduction (soft constraint). This is **not** client preferences - it's an internal optimization constraint stored per-visit.
