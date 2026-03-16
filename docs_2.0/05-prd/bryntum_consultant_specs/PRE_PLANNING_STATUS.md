# Pre-Planning & Movable Visits Implementation Status

**Date:** 2026-01-22  
**Branch:** `feat/serices-impl`  
**Reference Plans:**

- `accelerated_2.0_pilot_afb51e15.plan.md` - Bridge architecture plan
- `scheduling_system_architecture_2.0_d94bae6a.plan.md` - Full migration plan

---

## Executive Summary

**Status:** ⚠️ **PARTIALLY IMPLEMENTED** - Database ready, GraphQL & Frontend missing

Pre-planning infrastructure is **partially ready**. The database schema is fully prepared with `VisitTemplate`, `Template` (slingor), and `MovableVisitAssignment` models. CSV schema exists for parsing visit templates. However, the GraphQL layer and frontend UI are **missing**.

---

## Current State

### ✅ What Exists (Ready for Implementation)

1. **Database Schema** - ✅ **FULLY PREPARED**
   - `VisitTemplate` model in `apps/dashboard-server/schema.prisma` (lines 812-839)
     - Fields: `frequency`, `durationMinutes`, `preferredDays`, `preferredTimeSlot`, `requiredSkills`, `lifecycleStatus`, `source`, etc.
     - Relationships: `Organization`, `Visit[]`, `MovableVisitAssignment[]`
   - `Template` model (slingor) - lines 773-792
   - `TemplateVisit` model - lines 794-810
   - `MovableVisitAssignment` model - lines 841-856
   - All enums: `MovableVisitLifecycleStatus`, `MovableVisitSource`, `VisitFrequency`, `SlingaStatus`

2. **CSV Schema** - ✅ **EXISTS**
   - `apps/dashboard-server/src/services/bridge/mappers/schema/schemas/visit-template.schema.ts`
   - Defines complete CSV format for visit templates (26 fields)
   - Fields: `movableVisitTemplateId`, `clientId`, `frequencyPeriod`, `durationMinutes`, `preferredWindowStart/End`, `allowedWindowStart/End`, `skills`, etc.

3. **Bridge Service Stubs** - ⚠️ **PLACEHOLDERS**
   - `apps/dashboard-server/src/services/bridge/pre-planning/movable-visit.service.ts` - TODOs
   - `apps/dashboard-server/src/services/bridge/pre-planning/pre-planning-orchestrator.service.ts` - TODOs

4. **Documentation** - ✅ **COMPREHENSIVE**
   - `docs/docs_2.0/09-scheduling/MOVABLE_VISITS.md` - Full guide
   - `docs/docs_2.0/09-scheduling/PREPLANNING_BACKEND_ANALYSIS.md` - Backend architecture
   - `docs/docs_2.0/09-scheduling/PREPLANNING_FRONTEND_IMPLEMENTATION.md` - Frontend guide

### ❌ What's Missing

1. **GraphQL Schema** - No types/queries/mutations for pre-planning
   - No `VisitTemplate` type in `packages/graphql/schema/dashboard/types.graphql`
   - No `Template` type (slingor)
   - No queries: `visitTemplates`, `templates`, `prePlanningSession`
   - No mutations: `createVisitTemplate`, `uploadVisitTemplatesCsv`, `startPrePlanning`, `optimizeMovableVisits`

2. **GraphQL Operations** - No `.graphql` operation files
   - Missing: `packages/graphql/operations/mutations/preplanning/*.graphql`
   - Missing: `packages/graphql/operations/queries/preplanning/*.graphql`

3. **GraphQL Resolvers** - No resolver implementations
   - Missing: `apps/dashboard-server/src/graphql/resolvers/preplanning/` or `visit-template/`
   - Missing: Resolvers for `Template` (slingor)

4. **CSV Upload** - No CSV upload for visit templates
   - Existing: `UploadCsvModal.tsx` only handles schedules and solutions
   - Missing: CSV upload mutation for visit templates
   - Missing: CSV parser integration (schema exists but not used)

5. **Frontend UI** - No pre-planning pages/components
   - Missing: `apps/dashboard/src/pages/PrePlanningPage.tsx`
   - Missing: `apps/dashboard/src/components/preplanning/` directory
   - Missing: Visit templates list/editor
   - Missing: Pre-planning workflow UI

6. **Backend Implementation** - Services are stubs
   - All functions return "Not yet implemented" errors
   - Need to bridge from 1.0 services
   - CSV parser exists but not integrated

---

## What Needs to Be Done (Based on Plans)

### Phase 1: Backend Services (Bridge from 1.0)

**Source Files in 1.0:**

- `src/features/scheduling/services/movable-visits/movable-visit-sync.service.ts`
- `src/features/scheduling/services/movable-visits/movable-visit-expansion.service.ts`
- `src/features/scheduling/services/preplanning/pre-planning-orchestrator.ts`
- `src/app/api/pre-planning/movable-visits/route.ts` (REST API endpoints)

**Target Files in 2.0:**

- `apps/dashboard-server/src/services/bridge/pre-planning/movable-visit.service.ts` ✅ (exists, needs implementation)
- `apps/dashboard-server/src/services/bridge/pre-planning/pre-planning-orchestrator.service.ts` ✅ (exists, needs implementation)

**Tasks:**

1. Copy logic from 1.0 movable-visit services
2. Convert Drizzle queries → Prisma queries
3. Implement CSV parsing for movable visits
4. Implement optimization integration with Timefold
5. Add validation and error handling

### Phase 2: Database Schema

**✅ ALREADY EXISTS in `apps/dashboard-server/schema.prisma`:**

- ✅ `VisitTemplate` model (lines 812-839) - Movable visit templates
- ✅ `Template` model (lines 773-792) - Slingor/loops
- ✅ `TemplateVisit` model (lines 794-810) - Visits within templates
- ✅ `MovableVisitAssignment` model (lines 841-856) - Template assignments
- ✅ All enums: `MovableVisitLifecycleStatus`, `MovableVisitSource`, `VisitFrequency`, `SlingaStatus`

**No database changes needed!**

### Phase 3: GraphQL Schema

**Add to `packages/graphql/schema/dashboard/types.graphql`:**

```graphql
type VisitTemplate {
  id: ID!
  organizationId: ID!
  clientId: ID!
  frequency: VisitFrequency!
  durationMinutes: Int!
  preferredDays: [String!]!
  preferredTimeSlot: String
  requiredSkills: [String!]!
  lifecycleStatus: MovableVisitLifecycleStatus!
  source: MovableVisitSource!
  patternConfidence: Float
  lastOccurrence: DateTime
  nextSuggested: DateTime
  notes: String
  metadata: JSON
  createdAt: DateTime!
  updatedAt: DateTime!

  organization: Organization!
  client: Client!
  visits: [Visit!]!
  assignments: [MovableVisitAssignment!]!
}

type Template {
  id: ID!
  organizationId: ID!
  name: String!
  description: String
  status: SlingaStatus!
  templateType: String!
  recurrence: JSON
  metadata: JSON
  createdAt: DateTime!
  updatedAt: DateTime!

  organization: Organization!
  visits: [TemplateVisit!]!
  scheduleGroups: [ScheduleGroup!]!
}

type TemplateVisit {
  id: ID!
  templateId: ID!
  clientId: ID
  dayOffset: Int!
  startTime: String!
  durationMinutes: Int!
  requiredSkills: [String!]!
  notes: String
  metadata: JSON
  createdAt: DateTime!

  template: Template!
}

type MovableVisitAssignment {
  id: ID!
  visitTemplateId: ID!
  scheduleId: ID!
  assignedDate: DateTime!
  assignedTime: DateTime
  status: String!
  notes: String
  createdAt: DateTime!

  visitTemplate: VisitTemplate!
}
```

**Note:** Enums already exist in schema: `MovableVisitLifecycleStatus`, `MovableVisitSource`, `VisitFrequency`, `SlingaStatus`

**Add to `packages/graphql/schema/dashboard/queries.graphql`:**

```graphql
extend type Query {
  visitTemplates(
    organizationId: ID!
    limit: Int
    offset: Int
    lifecycleStatus: MovableVisitLifecycleStatus
    clientId: ID
  ): PaginatedVisitTemplates!

  visitTemplate(id: ID!): VisitTemplate

  templates(
    organizationId: ID!
    limit: Int
    offset: Int
    status: SlingaStatus
  ): PaginatedTemplates!

  template(id: ID!): Template
}

type PaginatedVisitTemplates {
  records: [VisitTemplate!]!
  total: Int!
}

type PaginatedTemplates {
  records: [Template!]!
  total: Int!
}
```

**Add to `packages/graphql/schema/dashboard/mutations.graphql`:**

```graphql
extend type Mutation {
  createVisitTemplate(input: CreateVisitTemplateInput!): VisitTemplate!

  updateVisitTemplate(id: ID!, input: UpdateVisitTemplateInput!): VisitTemplate!

  uploadVisitTemplatesCsv(
    organizationId: ID!
    fileBase64: String!
    fileName: String!
  ): UploadVisitTemplatesResult!

  startPrePlanning(input: StartPrePlanningInput!): PrePlanningSession!

  optimizeMovableVisits(
    visitTemplateIds: [ID!]!
    timeHorizon: TimeHorizonInput!
  ): OptimizeMovableVisitsResult!

  finalizePrePlanning(sessionId: ID!): FinalizePrePlanningResult!
}

input CreateVisitTemplateInput {
  organizationId: ID!
  clientId: ID!
  frequency: VisitFrequency!
  durationMinutes: Int!
  preferredDays: [String!]
  preferredTimeSlot: String
  requiredSkills: [String!]
  lifecycleStatus: MovableVisitLifecycleStatus
  source: MovableVisitSource
  notes: String
  metadata: JSON
}

input UpdateVisitTemplateInput {
  frequency: VisitFrequency
  durationMinutes: Int
  preferredDays: [String!]
  preferredTimeSlot: String
  requiredSkills: [String!]
  lifecycleStatus: MovableVisitLifecycleStatus
  notes: String
  metadata: JSON
}

input StartPrePlanningInput {
  organizationId: ID!
  startDate: DateTime!
  endDate: DateTime!
  serviceAreaIds: [ID!]
}

input TimeHorizonInput {
  startDate: DateTime!
  endDate: DateTime!
}

type UploadVisitTemplatesResult {
  success: Boolean!
  count: Int!
  errors: [String!]
}

type OptimizeMovableVisitsResult {
  success: Boolean!
  optimizedCount: Int!
  sessionId: ID!
}

type FinalizePrePlanningResult {
  success: Boolean!
  scheduleIds: [ID!]!
}
```

### Phase 4: GraphQL Operations

**Create `packages/graphql/operations/mutations/preplanning/createVisitTemplate.graphql`:**

```graphql
mutation CreateVisitTemplate($input: CreateVisitTemplateInput!) {
  createVisitTemplate(input: $input) {
    id
    clientId
    frequency
    durationMinutes
    preferredDays
    preferredTimeSlot
    requiredSkills
    lifecycleStatus
    source
    createdAt
    client {
      id
      firstName
      lastName
    }
  }
}
```

**Create `packages/graphql/operations/mutations/preplanning/uploadVisitTemplatesCsv.graphql`:**

```graphql
mutation UploadVisitTemplatesCsv(
  $organizationId: ID!
  $fileBase64: String!
  $fileName: String!
) {
  uploadVisitTemplatesCsv(
    organizationId: $organizationId
    fileBase64: $fileBase64
    fileName: $fileName
  ) {
    success
    count
    errors
  }
}
```

**Create `packages/graphql/operations/queries/preplanning/visitTemplates.graphql`:**

```graphql
query VisitTemplates(
  $organizationId: ID!
  $limit: Int
  $offset: Int
  $lifecycleStatus: MovableVisitLifecycleStatus
  $clientId: ID
) {
  visitTemplates(
    organizationId: $organizationId
    limit: $limit
    offset: $offset
    lifecycleStatus: $lifecycleStatus
    clientId: $clientId
  ) {
    records {
      id
      clientId
      frequency
      durationMinutes
      preferredDays
      preferredTimeSlot
      requiredSkills
      lifecycleStatus
      source
      patternConfidence
      lastOccurrence
      nextSuggested
      client {
        id
        firstName
        lastName
      }
    }
    total
  }
}
```

### Phase 5: GraphQL Resolvers

**Create `apps/dashboard-server/src/graphql/resolvers/preplanning/`:**

```
preplanning/
├── index.ts
├── mutations/
│   ├── createMovableVisit.ts
│   ├── uploadMovableVisitsCsv.ts
│   ├── startPrePlanning.ts
│   ├── optimizeMovableVisits.ts
│   ├── finalizePrePlanning.ts
│   └── index.ts
├── queries/
│   ├── movableVisits.ts
│   ├── prePlanningSession.ts
│   ├── prePlanningSessions.ts
│   └── index.ts
└── resolvers/
    ├── client.ts
    ├── organization.ts
    └── index.ts
```

### Phase 6: CSV Upload Frontend

**Create `apps/dashboard/src/components/modals/UploadVisitTemplatesCsvModal.tsx`:**

Similar to `UploadCsvModal.tsx` but:

- Validates visit templates CSV format using `visitTemplateSchema`
- Calls `uploadVisitTemplatesCsv` mutation
- Shows preview of visit templates
- Handles errors

**CSV Format (from `visit-template.schema.ts`):**

```csv
movableVisitTemplateId,clientId,clientName,visitTitle,visitCategory,frequencyPeriod,daysInPeriod,occasionsDay,occasionsNight,durationMinutes,validFrom,validTo,skills,serviceAreaId,priority,preferredWindowStart,preferredWindowEnd,allowedWindowStart,allowedWindowEnd,notes
template-123,client-456,Anna S.,Frukosthjälp,recurring,weekly,7,1,0,30,2026-01-01,2026-12-31,"skill1,skill2",area-789,5,08:00,10:00,07:00,12:00,Weekly breakfast help
```

**Integration:**

- Use existing `visitTemplateSchema` from `apps/dashboard-server/src/services/bridge/mappers/schema/schemas/visit-template.schema.ts`
- Parser already exists in bridge services, just needs GraphQL mutation wrapper

### Phase 7: Frontend Pages

**Create `apps/dashboard/src/pages/PrePlanningPage.tsx`:**

- List movable visits
- Create new movable visit
- Upload CSV
- Start pre-planning session
- View optimization progress
- Finalize and create schedules

**Create `apps/dashboard/src/components/preplanning/`:**

- `MovableVisitList.tsx` - List with filters
- `MovableVisitForm.tsx` - Create/edit form
- `PrePlanningSessionCard.tsx` - Session status card
- `PrePlanningWorkflow.tsx` - Step-by-step workflow

---

## Implementation Priority

Based on `accelerated_2.0_pilot_afb51e15.plan.md`:

| Priority | Task                                      | Effort      | Status            |
| -------- | ----------------------------------------- | ----------- | ----------------- |
| **P1**   | Bridge movable-visit services from 1.0    | 2 days      | ❌ Not started    |
| **P1**   | Bridge pre-planning-orchestrator from 1.0 | 2 days      | ❌ Not started    |
| **P1**   | ~~Add Prisma schema~~                     | ✅ **DONE** | ✅ Database ready |
| **P1**   | Create GraphQL schema types               | 0.5 days    | ❌ Not started    |
| **P1**   | Create GraphQL resolvers                  | 1 day       | ❌ Not started    |
| **P1**   | Create GraphQL operations                 | 0.5 days    | ❌ Not started    |
| **P1**   | CSV upload mutation (use existing schema) | 0.5 days    | ❌ Not started    |
| **P1**   | Frontend PrePlanningPage                  | 2 days      | ❌ Not started    |
| **P1**   | CSV upload modal                          | 1 day       | ❌ Not started    |

**Total P1 Effort:** ~9.5 days (database already done)

---

## Key Files Reference

### Database (✅ Ready)

- `apps/dashboard-server/schema.prisma` - `VisitTemplate`, `Template`, `TemplateVisit`, `MovableVisitAssignment` models exist
- All enums defined: `MovableVisitLifecycleStatus`, `MovableVisitSource`, `VisitFrequency`, `SlingaStatus`

### CSV Schema (✅ Exists)

- `apps/dashboard-server/src/services/bridge/mappers/schema/schemas/visit-template.schema.ts`
- Complete field definitions (26 fields) for CSV parsing

### Backend Services (⚠️ Stubs - Need Implementation)

- `apps/dashboard-server/src/services/bridge/pre-planning/movable-visit.service.ts` - TODOs
- `apps/dashboard-server/src/services/bridge/pre-planning/pre-planning-orchestrator.service.ts` - TODOs
- `apps/dashboard-server/src/services/bridge/pre-planning/index.ts`

### Frontend (❌ Missing)

- No pre-planning pages or components exist
- CSV upload only handles schedules/solutions
- Need: `PrePlanningPage.tsx`, `UploadVisitTemplatesCsvModal.tsx`

### GraphQL (❌ Missing)

- No `VisitTemplate` or `Template` types in schema
- No pre-planning queries/mutations
- No pre-planning resolvers

---

## Next Steps

1. **Immediate:** Implement bridge services by copying from 1.0
2. **Add Prisma schema** for MovableVisit and PrePlanningSession
3. **Create GraphQL schema** types and operations
4. **Implement resolvers** that call bridge services
5. **Create CSV upload** functionality
6. **Build frontend UI** for pre-planning workflow

---

**Last Updated:** 2026-01-22  
**Status:** ⚠️ **PARTIALLY READY** - Database & CSV schema exist, GraphQL & Frontend missing

**Key Finding:** The database is fully prepared with `VisitTemplate`, `Template`, and related models. CSV schema exists. Only GraphQL layer and frontend UI need to be implemented. The plan says 16 hours (2 days) for Pre-Planning Core, which aligns with implementing the missing GraphQL + frontend components.
