# CAIRE 2.0: Architecture Handover Specification

This document contains the complete technical specification for the CAIRE 2.0 data model and GraphQL API. It incorporates feedback from the Bryntum integration team and follows a fully normalized, "total accounting" philosophy.

---

## CHANGELOG

### 2026-01-27: Data Model 2.0 Gap Analysis Implementation

**Migration:** `20260127063104_add_data_model_2_0_fields`
**Status:** Backend Complete, Frontend Pending

#### Employee Model Updates

- ✅ Renamed `homeServiceAreaId` → `serviceAreaId` (nullable for multi-area employees)
- ✅ Added `gender`, `status`, `role`, `startDate`, `endDate`, `phoniroEmployeeId`, `recentClientVisits`
- ✅ Kept home address fields as optional (homeAddress, homeLatitude, homeLongitude)
- ✅ Added EmployeePreference model for bidirectional employee-client preferences

#### Client Model Updates

- ✅ Added **CRITICAL** `contactPerson` field for caregiver continuity tracking
- ✅ Added `gender`, `birthYear` (instead of full DOB for privacy)
- ✅ Added denormalized address fields: `address`, `latitude`, `longitude`, `municipality`
- ✅ Added care fields: `careLevel`, `diagnoses`, `allergies`, `languagePreference`

#### GraphQL Schema Updates

- ✅ Added 8 relationship types (Address, ClientContact, ClientPreference, MonthlyAllocation, EmployeeSkill, EmployeeTag, EmployeeCost, EmployeePreference)
- ✅ Updated all Employee/Client types, inputs, queries, mutations
- ✅ Implemented field resolvers for all relationships
- ✅ Regenerated TypeScript types and React hooks

#### Design Decisions

- **serviceAreaId nullable** - Supports multi-area employees and org-level staff
- **birthYear instead of dateOfBirth** - GDPR compliance (less sensitive)
- **contactPerson as text** - Flexibility for CSV imports
- **diagnoses optional** - Sensitive GDPR data, use skill matching instead
- **Home address kept optional** - User-requested flexibility

**Documentation:**

- See `data-model-implementation-notes.md` for detailed implementation vs documentation differences
- See `/DATA_MODEL_IMPLEMENTATION_STATUS.md` (repo root) for frontend implementation guide

---

## 1. Core Principles

- **Normalization**: `SolutionAssignment` and `SolutionEvent` are linked to `ScheduleEmployee` (the specific shift context) rather than a generic `Employee`.
- **Total Time Accounting**: Every second of a shift must be accounted for. Gaps between visits are materially stored as `TRAVEL` or `WAITING` events.
- **Single Source of Truth**: The GraphQL schema defines the interface for the Bryntum frontend, regardless of the underlying database complexity.
- **Solver Transparency**: `unassignedVisits` and solver `warnings` are stored directly in the `Solution` entity for immediate UI feedback.

---

## 2. Database Layer (Prisma)

Copy the following into `prisma/schema.prisma` in the new repository.

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// --- Core Entities ---

model Organization {
  id          String   @id
  name        String
  description String?
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  employees  Employee[]
  clients    Client[]
  schedules  Schedule[]
  solutions  Solution[]
  metrics    SolutionMetric[]

  @@map("organizations")
}

model Employee {
  id             String   @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  organizationId String
  firstName      String
  lastName       String
  email          String?
  contractType   String?  // full_time, part_time, hourly
  transportMode  String?  // car, bike, walk
  isActive       Boolean  @default(true)
  createdAt      DateTime @default(now())
  updatedAt      DateTime @updatedAt

  organization Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)
  shifts       ScheduleEmployeeShift[]
  skills       EmployeeSkill[]
  scheduleAssignments ScheduleEmployee[]

  @@index([organizationId])
  @@map("employees")
}

model Client {
  id             String   @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  organizationId String
  firstName      String
  lastName       String
  address        String?
  latitude       Float?
  longitude      Float?
  isActive       Boolean  @default(true)

  organization Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)
  visits       Visit[]
  events       SolutionEvent[]

  @@map("clients")
}

model Schedule {
  id             String   @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  organizationId String
  name           String
  dateFrom       DateTime
  dateTo         DateTime
  status         String   @default("draft")

  organization Organization      @relation(fields: [organizationId], references: [id], onDelete: Cascade)
  employees    ScheduleEmployee[]
  visits       Visit[]
  solutions    Solution[]
  shifts       ScheduleEmployeeShift[]

  @@map("schedules")
}

// --- Normalization Join ---

model ScheduleEmployee {
  id         String   @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  scheduleId String   @db.Uuid
  employeeId String   @db.Uuid
  role       String   @default("caregiver")

  schedule    Schedule   @relation(fields: [scheduleId], references: [id], onDelete: Cascade)
  employee    Employee   @relation(fields: [employeeId], references: [id], onDelete: Cascade)

  shifts      ScheduleEmployeeShift[]
  assignments SolutionAssignment[]
  events      SolutionEvent[]

  @@unique([scheduleId, employeeId])
  @@map("schedule_employees")
}

model ScheduleEmployeeShift {
  id                 String   @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  scheduleEmployeeId String   @db.Uuid
  employeeId         String   @db.Uuid
  scheduleId         String   @db.Uuid
  minStartTime       DateTime
  maxEndTime         DateTime

  scheduleEmployee ScheduleEmployee @relation(fields: [scheduleEmployeeId], references: [id], onDelete: Cascade)
  employee         Employee         @relation(fields: [employeeId], references: [id], onDelete: Cascade)
  schedule         Schedule         @relation(fields: [scheduleId], references: [id], onDelete: Cascade)
  breaks           ScheduleEmployeeBreak[]

  @@map("schedule_employee_shifts")
}

model ScheduleEmployeeBreak {
  id              String   @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  employeeShiftId String   @db.Uuid
  startTime       DateTime
  endTime         DateTime
  duration        Int
  costImpact      String   @default("PAID")

  shift           ScheduleEmployeeShift @relation(fields: [employeeShiftId], references: [id], onDelete: Cascade)

  @@map("schedule_employee_breaks")
}

model Visit {
  id             String   @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  scheduleId     String   @db.Uuid
  clientId       String   @db.Uuid
  name           String
  duration       Int      // seconds
  minStartTime   DateTime
  maxStartTime   DateTime
  maxEndTime     DateTime
  pinned         Boolean  @default(false)

  schedule    Schedule   @relation(fields: [scheduleId], references: [id], onDelete: Cascade)
  client      Client     @relation(fields: [clientId], references: [id], onDelete: Cascade)
  assignments SolutionAssignment[]
  events      SolutionEvent[]

  @@map("visits")
}

// --- Solution (Timefold Output) ---

model Solution {
  id               String   @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  scheduleId       String   @db.Uuid
  organizationId   String
  status           String   @default("solving_completed")
  score            String?
  unassignedVisits String[] @db.Uuid
  warnings         String[]
  metadata         Json?

  schedule     Schedule             @relation(fields: [scheduleId], references: [id], onDelete: Cascade)
  organization Organization         @relation(fields: [organizationId], references: [id], onDelete: Cascade)
  assignments  SolutionAssignment[]
  events       SolutionEvent[]

  @@map("solutions")
}

model SolutionAssignment {
  id                 String   @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  solutionId         String   @db.Uuid
  visitId            String   @db.Uuid
  scheduleEmployeeId String?  @db.Uuid
  arrivalTime        DateTime?
  startTime          DateTime?
  endTime            DateTime?
  departureTime      DateTime?
  travelTimeSeconds  Int?
  waitingTimeSeconds Int?

  solution         Solution          @relation(fields: [solutionId], references: [id], onDelete: Cascade)
  visit            Visit             @relation(fields: [visitId], references: [id], onDelete: Cascade)
  scheduleEmployee ScheduleEmployee? @relation(fields: [scheduleEmployeeId], references: [id], onDelete: SetNull)

  @@map("solution_assignments")
}

model SolutionEvent {
  id                 String   @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  solutionId         String   @db.Uuid
  scheduleEmployeeId String   @db.Uuid
  visitId            String?  @db.Uuid
  eventType          String   // travel, waiting, break, visit
  startTime          DateTime
  endTime            DateTime
  duration           Int

  solution         Solution         @relation(fields: [solutionId], references: [id], onDelete: Cascade)
  scheduleEmployee ScheduleEmployee @relation(fields: [scheduleEmployeeId], references: [id], onDelete: Cascade)
  visit            Visit?           @relation(fields: [visitId], references: [id], onDelete: SetNull)

  @@map("solution_events")
}
```

---

## 3. API Layer (GraphQL)

Scaffold these into `src/graphql/schema/`.

### Solution Type

```graphql
type Solution {
  id: ID!
  schedule: Schedule!
  score: String
  assignments: [SolutionAssignment!]!
  assignedVisits: [Visit!]!
  unassignedVisits: [Visit!]!
  events: [SolutionEvent!]!
  warnings: [String!]!
}
```

### Event Type (Total Coverage)

```graphql
type SolutionEvent {
  id: ID!
  scheduleEmployee: ScheduleEmployee!
  eventType: EventType!
  startTime: DateTime!
  endTime: DateTime!
  duration: Int!
  visit: Visit
}

enum EventType {
  VISIT
  TRAVEL
  WAITING
  BREAK
  OFFICE
}
```

---

## 4. Mapper Logic (Timefold Output Processing)

When processing the Timefold output JSON, the backend must perform the following transformations:

### A. Materializing Gaps

Timefold provides visits and breaks. The mapper must iterate through each vehicle's `itinerary` and create `TRAVEL` and `WAITING` events for every gap between start location, visits, and end location.

### B. Unassigned Visit Logic

- Read `totalUnassignedVisits` from KPIs.
- Map the list of unassigned visit IDs into the `Solution.unassignedVisits` array.
- Extract `validationResult.warnings` to explain unassigned status to the user.

### C. Normalization Mapping

- Look up the `ScheduleEmployee` ID using the `vehicleId` (EmployeeID) and the current `ScheduleID`.
- Save all assignments/events against the `scheduleEmployeeId` to maintain the shift context.

---

## 5. Bryntum Requirements Checklist

- [x] **Filterable Queries**: `getSolution(id: UUID)` must allow filtering at the assignment level.
- [x] **Nested Expansion**: `Solution -> ScheduleEmployee -> Shift -> Break`.
- [x] **Update Mutation**: `updateSolutionAssignment(id, input)` to support drag-and-drop reshuffling.
- [x] **Naming**: Models renamed to `ScheduleEmployeeShift/Break` for clarity.
