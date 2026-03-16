# Mapper Specifications for Caire 2.0

**Version:** 2.0  
**Date:** 2025-12-09  
**Purpose:** Complete mapper specifications for **ALL scheduling use cases** in Caire 2.0 normalized data model architecture

**Related Documents:**

- **GraphQL Schema Specification:** `GRAPHQL_SCHEMA_SPECIFICATION.md` - Single source of truth for GraphQL types
- **Data Model:** `../03-data/data-model.md` - Database schema documentation
- **API Design:** `API_DESIGN.md` - Overall API architecture

**Scope:** This document covers mappers for:

- ✅ **Regular scheduling** (daily/weekly optimization)
- ✅ **Pre-planning** (multi-week/month planning with movable visits)
- ✅ **External system imports** (Carefox, eCare, Phoniro, CSV, JSON, PDF)
- ✅ **Timefold integration** (optimization API)
- ✅ **Bryntum UI** (calendar display and user edits)

---

## ⚠️ Important: Caire 2.0 Architecture

**Caire 1.0 (Legacy - NOT used in v2.0):**

- External Systems → Timefold JSON → Store JSON in database
- Mappers: External → Timefold JSON format

**Caire 2.0 (Current Architecture):**

- External Systems → **Normalized Database (Prisma)** → GraphQL → Bryntum
- **No Timefold JSON storage** - only normalized relational tables
- Timefold JSON is **temporary** - only used for API communication

**This document specifies mappers for Caire 2.0 only.**

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL DATA SOURCES                        │
├─────────────────────────────────────────────────────────────────┤
│  Carefox API  │  eCare CSV  │  Phoniro CSV  │  Custom JSON/CSV  │
└───────────────┴──────────────┴───────────────┴──────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              EXTERNAL → NORMALIZED DATABASE MAPPERS            │
├─────────────────────────────────────────────────────────────────┤
│  carefoxToNormalizedDb  │  ecareCsvToNormalizedDb              │
│  phoniroCsvToNormalizedDb  │  customJsonToNormalizedDb         │
│  pdfToMovableVisits                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    NORMALIZED DATABASE                          │
│              (Prisma + PostgreSQL)                              │
├─────────────────────────────────────────────────────────────────┤
│  schedules, visits, employees, clients,                         │
│  visit_templates, templates, schedule_groups,                   │
│  solution_assignments, solution_events, solution_metrics         │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
        ┌───────────────────┐  ┌───────────────────┐
        │  GraphQL API       │  │  Timefold API     │
        │  (Queries/Mutations)│  │  (Temporary JSON) │
        └───────────────────┘  └───────────────────┘
                    │                   │
                    │                   ▼
                    │          ┌───────────────────┐
                    │          │  Timefold Solution │
                    │          │  → Normalized DB    │
                    │          └───────────────────┘
                    │
                    ▼
        ┌───────────────────┐
        │  NORMALIZED DB    │
        │  → BRYNTUM        │
        │  MAPPERS          │
        └───────────────────┘
                    │
                    ▼
        ┌───────────────────┐
        │  BRYNTUM CALENDAR │
        │  (Frontend UI)     │
        └───────────────────┘
```

---

## 1. External Systems → Normalized Database

### Purpose

Import external data directly into normalized database tables using Prisma. **No Timefold JSON intermediate storage.**

### 1.1 Carefox → Normalized Database

**Mapper:** `carefoxToNormalizedDb.mapper.ts`  
**Location:** `packages/server/src/integrations/mappers/carefox-to-normalized-db.mapper.ts`

**Input:** Carefox API JSON response

**Output:** Prisma inserts/updates to normalized tables

**Tables Updated:**

- `organizations` (if new)
- `employees` (with `externalId` from Carefox)
- `clients` (with `externalId` from Carefox)
- `visits` (with `externalId` from Carefox)
- `schedules` (with `source = 'carefox'`)
- `employee_shifts` (from Carefox shift data)
- `employee_breaks` (from Carefox break data)
- `addresses` (geocoded client addresses)

**Key Mapping Logic:**

```typescript
// Employee mapping
CarefoxEmployee → {
  id: generateUUID(),
  organizationId: orgId,
  externalId: carefoxEmployee.id, // Carefox ID
  name: carefoxEmployee.name,
  email: carefoxEmployee.email,
  phone: carefoxEmployee.phone,
  contractType: mapContractType(carefoxEmployee.contractType),
  transportMode: mapTransportMode(carefoxEmployee.transportMode),
  // ... other fields
}

// Client mapping
CarefoxPatient → {
  id: generateUUID(),
  organizationId: orgId,
  externalId: carefoxPatient.id, // Carefox ID
  name: carefoxPatient.name,
  address: carefoxPatient.address,
  latitude: geocode(carefoxPatient.address).lat,
  longitude: geocode(carefoxPatient.address).lng,
  // ... other fields
}

// Visit mapping
CarefoxVisit → {
  id: generateUUID(),
  scheduleId: scheduleId,
  organizationId: orgId,
  clientId: findClientByExternalId(carefoxVisit.patientId),
  externalId: carefoxVisit.id, // Carefox ID
  name: carefoxVisit.type,
  duration: carefoxVisit.duration, // minutes
  minStartTime: parseTimestamp(carefoxVisit.startTime),
  maxStartTime: parseTimestamp(carefoxVisit.endTime),
  maxEndTime: parseTimestamp(carefoxVisit.endTime) + duration,
  pinned: false, // Default unpinned, can be pinned later
  isMovable: false, // Default not movable
  // ... other fields
}

// Shift mapping
CarefoxShift → {
  id: generateUUID(),
  scheduleEmployeeId: scheduleEmployeeId,
  employeeId: employeeId,
  scheduleId: scheduleId,
  shiftExternalId: carefoxShift.id,
  minStartTime: parseTimestamp(carefoxShift.startTime),
  maxEndTime: parseTimestamp(carefoxShift.endTime),
  totalDurationSeconds: calculateDuration(carefoxShift),
  // ... other fields
}

// Break mapping
CarefoxBreak → {
  id: generateUUID(),
  employeeShiftId: employeeShiftId,
  breakExternalId: carefoxBreak.id,
  minStartTime: parseTimestamp(carefoxBreak.startTime),
  maxStartTime: parseTimestamp(carefoxBreak.startTime),
  maxEndTime: parseTimestamp(carefoxBreak.endTime),
  duration: carefoxBreak.duration, // ISO 8601
  breakType: mapBreakType(carefoxBreak.type),
  costImpact: carefoxBreak.paid ? 'PAID' : 'UNPAID',
  // ... other fields
}
```

**Skills & Tags Mapping:**

- `employee_skills`: Extract from `carefoxEmployee.delegations`, `educations`, `languages`, `attributes`
- `employee_tags`: Extract from `carefoxEmployee.units`
- `visit_skills`: Extract from `carefoxPatient.attributes`
- `visit_tags`: Extract from `carefoxPatient.units`

**Service Area Mapping:**

- Match Carefox organizational units to `service_areas` table
- Use hierarchical matching (dot notation: "Stockholm.Syd")

---

### 1.2 eCare CSV → Normalized Database

**Mapper:** `ecareCsvToNormalizedDb.mapper.ts`  
**Location:** `packages/server/src/integrations/mappers/ecare-csv-to-normalized-db.mapper.ts`

**Input:** eCare CSV file

**Output:** Prisma inserts/updates to normalized tables

**Tables Updated:** Same as Carefox mapper

**CSV Columns Mapping:**

- Employee columns → `employees` table
- Client columns → `clients` table
- Visit columns → `visits` table
- Shift columns → `employee_shifts` table

**Key Differences from Carefox:**

- CSV parsing instead of JSON
- Different column names (need mapping table)
- Batch processing for large files

---

### 1.3 Phoniro CSV → Normalized Database

**Mapper:** `phoniroCsvToNormalizedDb.mapper.ts`  
**Location:** `packages/server/src/integrations/mappers/phoniro-csv-to-normalized-db.mapper.ts`

**Input:** Phoniro CSV file (actual execution data)

**Output:** Prisma inserts/updates to `solution_events` and `solution_assignments` tables

**Purpose:** Import actual visit execution data (what actually happened vs what was planned)

**Tables Updated:**

- `solution_events` (actual travel, waiting, visit times)
- `solution_assignments` (actual assignments)
- `visits` (update `visitStatus` to 'completed' or 'missed')

**Key Mapping:**

- Actual start/end times → `solution_events.startTime`, `endTime`
- Actual travel time → `solution_events.duration` (eventType: 'travel')
- Actual waiting time → `solution_events.duration` (eventType: 'waiting')
- Actual visit time → `solution_events.duration` (eventType: 'visit')

---

### 1.4 Custom JSON/CSV → Normalized Database

**Mapper:** `customJsonToNormalizedDb.mapper.ts`  
**Location:** `packages/server/src/integrations/mappers/custom-json-to-normalized-db.mapper.ts`

**Input:** Custom JSON or CSV format (user-defined schema)

**Output:** Prisma inserts/updates to normalized tables

**Purpose:** Generic import for any external system format

**Configuration:**

- User provides field mapping configuration
- Supports JSON and CSV formats
- Validates against normalized schema

---

### 1.5 PDF (Kommunbeslut) → Movable Visits

**Mapper:** `pdfToMovableVisits.mapper.ts`  
**Location:** `packages/server/src/integrations/mappers/pdf-to-movable-visits.mapper.ts`

**Input:** PDF file → Parsed JSON (via OCR/PDF parser)

**Output:** Prisma inserts to `visit_templates` table

**Tables Updated:**

- `visit_templates` (movable visits)
- `clients` (if new clients found in PDF)

**Key Mapping:**

- Client info from PDF → `clients` table
- Visit frequency from PDF → `visit_templates.frequency`
- Visit duration from PDF → `visit_templates.duration`
- Time windows from PDF → `visit_templates.allowedWindowStart/End`
- Priority from PDF → `visit_templates.priority`

**Status:** All imported visits start as `status = 'draft'`, `lifecycleStatus = 'identified'`

---

## 2. Normalized Database → Timefold API (Temporary)

### Purpose

Convert normalized database data to Timefold API format **only when calling Timefold API**. This JSON is **temporary** and **not stored** in the database.

### 2.1 Normalized Database → Timefold Input

**Mapper:** `normalizedDbToTimefoldInput.mapper.ts`  
**Location:** `packages/server/src/integrations/timefold/normalized-db-to-timefold-input.mapper.ts`

**Input:** Prisma query results (normalized database data)

**Output:** Timefold API input JSON (temporary, for API call only)

**Source Tables:**

- `schedules` (planning window, date)
- `visits` (with `pinned` flag)
- `employees` (with shifts)
- `employee_shifts` (working hours)
- `employee_breaks` (break periods)
- `clients` (addresses for travel calculation)
- `visit_skills` (required skills)
- `employee_skills` (available skills)

**Key Mapping Logic:**

```typescript
// Schedule → Timefold Planning Window
{
  planningWindow: {
    startDate: schedule.startDate,
    endDate: schedule.endDate,
  }
}

// Employees → Timefold Vehicles
employees.map(employee => ({
  id: employee.id,
  name: employee.name,
  transportMode: employee.transportMode,
  shifts: employeeShifts.map(shift => ({
    startTime: shift.minStartTime,
    endTime: shift.maxEndTime,
    breaks: employeeBreaks.map(break => ({
      earliestStart: break.minStartTime,
      latestEnd: break.maxEndTime,
      minDuration: break.duration,
      costImpact: break.costImpact, // "PAID" or "UNPAID"
    })),
  })),
  skills: employeeSkills.map(skill => skill.skillName),
}))

// Visits → Timefold Visits
visits.map(visit => ({
  id: visit.id,
  name: visit.name,
  duration: visit.duration, // seconds
  minStartTime: visit.minStartTime,
  maxStartTime: visit.maxStartTime,
  maxEndTime: visit.maxEndTime,
  preferredTimeWindows: visit.preferredTimeWindows || [], // Timefold soft constraint for waiting time reduction - array of {startTime, endTime} objects
  pinned: visit.pinned, // Critical: tells Timefold if visit can move
  requiredSkills: visitSkills.map(skill => skill.skillName),
  priority: visit.priority,
  location: {
    latitude: client.latitude,
    longitude: client.longitude,
  },
}))
```

**Key Principles:**

- **Pinned visits:** `pinned: true` → Timefold cannot move these
- **Unpinned visits:** `pinned: false` → Timefold can optimize these
- **Time windows (hard constraints):** Map `minStartTime`, `maxStartTime`, `maxEndTime` from database
- **Preferred time windows (soft constraints):** Map `preferredTimeWindows` jsonb array from database - used by Timefold to minimize waiting time (not client preferences, but internal optimization constraint)
- **Skills:** Map from `visit_skills` and `employee_skills` tables
- **Breaks:** Map `costImpact` from `employee_breaks.costImpact`

**Usage:**

- Called only when submitting optimization job to Timefold API
- JSON is generated on-the-fly from database
- **Not stored** in database (no `rawInput` field)

---

## 3. Timefold API → Normalized Database

### Purpose

Convert Timefold API response to normalized database tables. **No JSON storage** - all data normalized immediately.

### 3.1 Timefold Solution → Normalized Database

**Mapper:** `timefoldSolutionToNormalizedDb.mapper.ts`  
**Location:** `packages/server/src/integrations/timefold/timefold-solution-to-normalized-db.mapper.ts`

**Input:** Timefold API response (solution JSON)

**Output:** Prisma inserts/updates to normalized tables

**Tables Updated:**

- `solutions` (solution metadata, `datasetId`, `status`, `score`)
- `solution_assignments` (visit → employee assignments)
- `solution_events` (detailed event log: travel, waiting, visits, breaks)
- `solution_metrics` (aggregated KPIs)
- `employee_solution_metrics` (per-employee metrics)
- `client_solution_metrics` (per-client metrics)
- `service_area_solution_metrics` (per-service-area metrics)

**Key Mapping Logic:**

```typescript
// Solution metadata
{
  id: generateUUID(),
  scheduleId: scheduleId,
  datasetId: timefoldResponse.datasetId,
  status: mapStatus(timefoldResponse.status), // 'solving_completed', etc.
  score: timefoldResponse.score, // "0hard/-1200medium/-5000soft"
  submittedAt: timefoldResponse.submittedAt,
  completedAt: timefoldResponse.completedAt,
  summaryKpis: timefoldResponse.summaryKpis, // JSONB
}

// Assignments
timefoldResponse.assignments.map(assignment => ({
  id: generateUUID(),
  solutionId: solutionId,
  visitId: assignment.visitId, // Reference to visits table
  employeeId: assignment.employeeId, // Reference to employees table
  arrivalTime: parseTimestamp(assignment.arrivalTime),
  startTime: parseTimestamp(assignment.startTime),
  endTime: parseTimestamp(assignment.endTime),
  departureTime: parseTimestamp(assignment.departureTime),
  travelTimeSeconds: assignment.travelTimeSeconds,
  waitingTimeSeconds: assignment.waitingTimeSeconds,
  eventType: 'visit',
}))

// Events (detailed per-second log)
timefoldResponse.events.map(event => ({
  id: generateUUID(),
  solutionId: solutionId,
  employeeId: event.employeeId,
  eventType: mapEventType(event.type), // 'travel', 'waiting', 'break', 'visit', 'office'
  startTime: parseTimestamp(event.startTime),
  endTime: parseTimestamp(event.endTime),
  duration: event.duration, // seconds
  distance: event.distance, // km (for travel events)
  clientId: event.clientId, // For visit events
  visitId: event.visitId, // For visit events
}))

// Metrics
{
  id: generateUUID(),
  solutionId: solutionId,
  organizationId: organizationId,
  scheduleId: scheduleId,
  totalCost: calculateCost(timefoldResponse),
  totalRevenue: calculateRevenue(timefoldResponse),
  profit: calculateProfit(timefoldResponse),
  utilizationPercentage: calculateUtilization(timefoldResponse),
  serviceHours: calculateServiceHours(timefoldResponse),
  travelTimeSeconds: calculateTravelTime(timefoldResponse),
  waitingTimeSeconds: calculateWaitingTime(timefoldResponse),
  continuityScore: calculateContinuity(timefoldResponse),
  unassignedVisits: countUnassigned(timefoldResponse),
  // ... other metrics
}
```

**Key Principles:**

- **No JSON storage:** All data normalized to relational tables
- **Immediate normalization:** Convert API response to database immediately
- **Metrics calculation:** Calculate all metrics during mapping (not stored as JSON)

---

### 3.2 Timefold Solution → Pattern (Pre-Planning)

**Mapper:** `timefoldSolutionToPattern.mapper.ts`  
**Location:** `packages/server/src/services/pre-planning/timefold-solution-to-pattern.mapper.ts`

**Input:** Timefold solution JSON (first occurrence optimization)

**Output:** Pattern object `{ dayOfWeek, timeOfDay, duration }`

**Purpose:** Extract pattern from optimized first occurrence for replication

**Key Mapping Logic:**

```typescript
// Find first occurrence assignment
const firstOccurrence = timefoldSolution.assignments.find(
  (assignment) => assignment.visitId === firstOccurrenceVisitId,
);

// Extract pattern
const pattern = {
  dayOfWeek: getDayOfWeek(firstOccurrence.startTime), // 0=Monday, 6=Sunday
  timeOfDay: extractTimeOfDay(firstOccurrence.startTime), // "13:00:00"
  duration: firstOccurrence.endTime - firstOccurrence.startTime, // seconds
  employeeId: firstOccurrence.employeeId, // Optional: preferred employee
};
```

**Usage:** Called during Stage 1 (Pattern Discovery) of pre-planning optimization

---

## 4. Normalized Database → Bryntum

### Purpose

Convert normalized database data (from GraphQL queries) to Bryntum calendar format for frontend display.

### 4.1 Schedule Data → Bryntum

**Mapper:** `normalizedDbToBryntum.mapper.ts`  
**Location:** `packages/server/src/services/mappers/normalized-db-to-bryntum.mapper.ts`

**Input:** Prisma query results (from GraphQL)

**Output:** Bryntum calendar data format

**Source Tables:**

- `schedules` (schedule metadata)
- `visits` (visit data)
- `employees` (employee data)
- `employee_shifts` (working hours)
- `employee_breaks` (break periods)
- `solution_assignments` (optimized assignments)
- `solution_events` (detailed events)
- `clients` (client info for tooltips)

**Key Mapping Methods:**

```typescript
// Main conversion
mapScheduleToBryntum(scheduleData: ScheduleData): BryntumScheduleData {
  return {
    resources: this.mapEmployeesToResources(scheduleData.employees),
    events: [
      ...this.mapShiftsToTimeRanges(scheduleData.employeeShifts),
      ...this.mapBreaksToEvents(scheduleData.employeeBreaks),
      ...this.mapVisitsToEvents(scheduleData.visits),
      ...this.mapAssignmentsToEvents(scheduleData.solutionAssignments),
      ...this.mapTravelAndWaitToEvents(scheduleData.solutionEvents),
    ],
  };
}

// Employees → Resources
mapEmployeesToResources(employees: Employee[]): BryntumResource[] {
  return employees.map(employee => ({
    id: employee.id,
    name: employee.name,
    role: employee.role,
    transportMode: employee.transportMode,
    contractType: employee.contractType,
    // Note: unusedHours is client-side (client allocation - actual service hours), not employee capacity
    // ... other fields
  }));
}

// Visits → Events
mapVisitsToEvents(visits: Visit[]): BryntumEvent[] {
  return visits.map(visit => ({
    // ... other fields
    preferredTimeWindows: visit.preferredTimeWindows || [], // Timefold soft constraint for waiting time reduction (jsonb array)
    id: visit.id,
    name: visit.name,
    resourceId: visit.assignment?.employeeId || null,
    startDate: visit.plannedStartTime || visit.assignment?.startTime,
    endDate: visit.plannedEndTime || visit.assignment?.endTime,
    duration: visit.duration, // minutes
    eventType: visit.assignment ? 'visit' : 'unplanned-visit',
    pinned: visit.pinned, // Shows 🔒 icon if true
    isMovable: visit.isMovable, // Shows dashed border if true
    visitStatus: visit.visitStatus,
    priority: visit.priority,
    clientName: visit.client.name,
    requiredSkills: visit.visitSkills.map(skill => skill.skillName),
    preferredTimeWindows: visit.preferredTimeWindows || [], // Timefold soft constraint for waiting time reduction (jsonb array)
    // ... other fields
  }));
}

// Shifts → Time Ranges
mapShiftsToTimeRanges(shifts: EmployeeShift[]): BryntumTimeRange[] {
  return shifts.map(shift => ({
    id: `shift-${shift.id}`,
    resourceId: shift.employeeId,
    startDate: shift.minStartTime,
    endDate: shift.maxEndTime,
    name: 'Working Hours',
    cls: 'shift-time-range',
  }));
}

// Breaks → Events
mapBreaksToEvents(breaks: EmployeeBreak[]): BryntumEvent[] {
  return breaks.map(break => ({
    id: `break-${break.id}`,
    resourceId: break.employeeShift.employeeId,
    startDate: break.minStartTime,
    endDate: break.maxEndTime,
    duration: parseDuration(break.duration),
    eventType: 'break',
    name: `Break (${break.breakType})`,
    cls: 'break-event',
  }));
}

// Assignments → Events (from solution)
mapAssignmentsToEvents(assignments: SolutionAssignment[]): BryntumEvent[] {
  return assignments
    .filter(a => a.eventType === 'visit')
    .map(assignment => ({
      id: `assignment-${assignment.id}`,
      resourceId: assignment.employeeId,
      startDate: assignment.startTime,
      endDate: assignment.endTime,
      eventType: 'visit',
      visitId: assignment.visitId,
      travelTime: assignment.travelTimeSeconds,
      waitingTime: assignment.waitingTimeSeconds,
      // ... other fields
    }));
}

// Travel & Wait → Events
mapTravelAndWaitToEvents(events: SolutionEvent[]): BryntumEvent[] {
  return events
    .filter(e => e.eventType === 'travel' || e.eventType === 'waiting')
    .map(event => ({
      id: `event-${event.id}`,
      resourceId: event.employeeId,
      startDate: event.startTime,
      endDate: event.endTime,
      eventType: event.eventType, // 'travel' or 'waiting'
      distance: event.distance, // For travel events
      // ... other fields
    }));
}
```

**Key Fields Mapped:**

- Employee service area
- Preferred/non-preferred clients
- Contact person-client
- Visit preferred start/end time
- Visit type (mandatory/optional, movable, cancelled/absent/extra/regular)
- Preferred/non-preferred staff
- Continuity requirements
- Allocated hours and unused allocation hours (client-side: monthly allocation - actual service hours delivered)
- SLA requirements

---

### 4.2 Pre-Planning Data → Bryntum

**Mapper:** `prePlanningDataToBryntum.mapper.ts`  
**Location:** `packages/server/src/services/mappers/pre-planning/pre-planning-data-to-bryntum.mapper.ts`

**Input:** Consolidated schedules across time horizon (from GraphQL)

**Output:** Bryntum calendar data (multi-week/month view)

**Source Tables:**

- Multiple `schedules` (across time horizon)
- All `visits` (pinned + unpinned)
- All `employees` (with shifts)
- `visit_templates` (movable visits)

**Key Mapping Methods:**

```typescript
// Consolidated schedules → Multi-week view
mapConsolidatedSchedulesToBryntum(
  schedules: Schedule[],
  timeHorizon: TimeHorizon
): BryntumScheduleData {
  return {
    resources: this.mapEmployeesToResources(allEmployees),
    events: [
      ...this.mapPinnedVisitsToEvents(pinnedVisits),
      ...this.mapUnpinnedVisitsToEvents(unpinnedVisits),
      ...this.mapUnassignedVisitsToPanel(unassignedVisits),
      ...this.mapShiftsToTimeRanges(allShifts),
    ],
    timeHorizon: {
      startDate: timeHorizon.startDate,
      endDate: timeHorizon.endDate,
    },
  };
}

// Pinned visits → Events (🔒 icon, solid background)
mapPinnedVisitsToEvents(visits: Visit[]): BryntumEvent[] {
  return visits
    .filter(v => v.pinned === true)
    .map(visit => ({
      id: visit.id,
      name: visit.name,
      resourceId: visit.assignment?.employeeId || null,
      startDate: visit.plannedStartTime,
      endDate: visit.plannedEndTime,
      eventType: 'visit',
      pinned: true, // Shows 🔒 icon
      cls: 'pinned-visit', // Solid blue background
      // ... other fields
    }));
}

// Unpinned visits → Events (dashed border)
mapUnpinnedVisitsToEvents(visits: Visit[]): BryntumEvent[] {
  return visits
    .filter(v => v.pinned === false)
    .map(visit => ({
      id: visit.id,
      name: visit.name,
      resourceId: visit.assignment?.employeeId || null,
      startDate: visit.plannedStartTime,
      endDate: visit.plannedEndTime,
      eventType: 'visit',
      pinned: false, // No lock icon
      cls: 'unpinned-visit', // Dashed border
      // ... other fields
    }));
}

// Unassigned visits → Panel data (not on calendar)
mapUnassignedVisitsToPanel(visits: Visit[]): UnassignedVisit[] {
  return visits
    .filter(v => v.assignment === null)
    .map(visit => ({
      id: visit.id,
      name: visit.name,
      clientName: visit.client.name,
      duration: visit.duration,
      timeWindow: {
        minStart: visit.minStartTime,
        maxStart: visit.maxStartTime,
        maxEnd: visit.maxEndTime,
      },
      preferredWindow: visit.preferredTimeWindows?.[0]
        ? {
            start: visit.preferredTimeWindows[0].startTime,
            end: visit.preferredTimeWindows[0].endTime,
          }
        : null, // Extract first preferred time window if available, otherwise null
      preferredTimeWindows: visit.preferredTimeWindows || [], // Full array of preferred time windows
      priority: visit.priority,
      requiredSkills: visit.visitSkills.map(skill => skill.skillName),
      // ... other fields
    }));
}
```

---

### 4.3 Raw Solver Data → Bryntum (Real-time)

**Mapper:** `rawSolverDataToBryntum.mapper.ts`  
**Location:** `packages/server/src/services/mappers/pre-planning/raw-solver-data-to-bryntum.mapper.ts`

**Input:** Raw Timefold solution data (IDs only, no names/details)

**Output:** Minimal Bryntum data (fast, no DB lookups)

**Purpose:** Fast real-time updates during optimization (polling every 2 seconds)

**Key Mapping Logic:**

```typescript
// Fast conversion with IDs only
mapRawSolutionToBryntum(
  rawSolution: TimefoldRawSolution
): BryntumScheduleData {
  return {
    resources: rawSolution.vehicles.map(v => ({
      id: v.id,
      name: `Employee ${v.id.substring(0, 6)}`, // Placeholder, no DB lookup
    })),
    events: rawSolution.assignments.map(a => ({
      id: a.visitId,
      resourceId: a.employeeId,
      startDate: a.startTime,
      endDate: a.endTime,
      eventType: 'visit',
      // Minimal data - no client names, no details
    })),
  };
}
```

**Key Principles:**

- **No database lookups:** Use IDs only
- **Fast conversion:** Minimal processing
- **Placeholder names:** "Employee {id}" instead of actual names
- **Full data after completion:** Once optimization completes, use full mapper with DB lookups

---

## 5. Bryntum → Normalized Database

### Purpose

Convert user edits in Bryntum calendar to database updates via GraphQL mutations.

### 5.1 Bryntum Edits → Normalized Database

**Mapper:** `bryntumToNormalizedDb.mapper.ts`  
**Location:** `packages/server/src/services/mappers/bryntum-to-normalized-db.mapper.ts`

**Input:** Bryntum event changes (from frontend)

**Output:** Prisma updates to normalized tables

**Target Tables:**

- `visits` (time changes, duration changes)
- `solution_assignments` (employee reassignment)
- `visits.pinned` (pin/unpin changes)

**Key Mapping Methods:**

```typescript
// Event time change → Visit update
mapEventChangeToVisitUpdate(
  eventChange: BryntumEventChange
): PrismaVisitUpdate {
  return {
    where: { id: eventChange.eventId },
    data: {
      plannedStartTime: eventChange.newStartDate,
      plannedEndTime: eventChange.newEndDate,
      duration: calculateDuration(eventChange.newStartDate, eventChange.newEndDate),
      updatedAt: new Date(),
    },
  };
}

// Event move → Assignment update
mapEventMoveToAssignmentUpdate(
  eventMove: BryntumEventMove
): PrismaAssignmentUpdate {
  return {
    where: {
      solutionId: eventMove.solutionId,
      visitId: eventMove.eventId,
    },
    data: {
      employeeId: eventMove.newResourceId,
      startTime: eventMove.newStartDate,
      endTime: eventMove.newEndDate,
      updatedAt: new Date(),
    },
  };
}

// Event create → Visit insert
mapEventCreateToVisitInsert(
  eventCreate: BryntumEventCreate
): PrismaVisitCreate {
  return {
    data: {
      id: generateUUID(),
      scheduleId: eventCreate.scheduleId,
      organizationId: eventCreate.organizationId,
      clientId: eventCreate.clientId,
      name: eventCreate.name,
      duration: eventCreate.duration,
      plannedStartTime: eventCreate.startDate,
      plannedEndTime: eventCreate.endDate,
      minStartTime: eventCreate.startDate,
      maxStartTime: eventCreate.endDate,
      maxEndTime: eventCreate.endDate,
      pinned: false,
      isMovable: true,
      visitStatus: 'planned',
      // ... other fields
    },
  };
}

// Event delete → Visit soft delete
mapEventDeleteToVisitSoftDelete(
  eventDelete: BryntumEventDelete
): PrismaVisitUpdate {
  return {
    where: { id: eventDelete.eventId },
    data: {
      deletedAt: new Date(),
      visitStatus: 'cancelled',
      updatedAt: new Date(),
    },
  };
}

// Pin/unpin change
mapPinChangeToVisitUpdate(
  pinChange: BryntumPinChange
): PrismaVisitUpdate {
  return {
    where: { id: pinChange.eventId },
    data: {
      pinned: pinChange.pinned,
      updatedAt: new Date(),
    },
  };
}
```

**Key Principles:**

- **Direct database updates:** No intermediate JSON
- **GraphQL mutations:** Mapper used in mutation resolvers
- **Transaction safety:** All updates in single transaction
- **Metrics recalculation:** After updates, backend recalculates metrics

---

## 6. Pre-Planning Specific Mappers

### 6.1 Movable Visits → Concrete Visits

**Mapper:** `visitTemplatesToNormalizedDb.mapper.ts`  
**Location:** `packages/server/src/services/pre-planning/visit-templates-to-normalized-db.mapper.ts`

**Input:** `visit_templates` from database + planning horizon

**Output:** Prisma inserts to `visits` table

**Purpose:** Generate concrete visits from movable visit templates for planning horizon

**Key Mapping Logic:**

```typescript
// Generate visits from template
generateVisitsFromTemplate(
  template: VisitTemplate,
  timeHorizon: TimeHorizon
): PrismaVisitCreate[] {
  const visits: PrismaVisitCreate[] = [];
  const occurrences = calculateOccurrences(template.frequency, timeHorizon);

  for (const occurrence of occurrences) {
    visits.push({
      data: {
        id: generateUUID(),
        scheduleId: null, // Unassigned initially
        organizationId: template.organizationId,
        clientId: template.clientId,
        movableVisitId: template.id, // Link to template
        name: template.name,
        duration: template.duration,
        minStartTime: occurrence.date + template.allowedWindowStart,
        maxStartTime: occurrence.date + template.allowedWindowEnd,
        maxEndTime: occurrence.date + template.allowedWindowEnd + template.duration,
        preferredWindowStart: occurrence.date + template.preferredWindowStart,
        preferredWindowEnd: occurrence.date + template.preferredWindowEnd,
        pinned: false, // Unpinned until optimized and accepted
        isMovable: true, // Can be moved during optimization
        visitStatus: 'planned',
        priority: template.priority,
        // ... other fields
      },
    });
  }

  return visits;
}
```

---

### 6.2 Pattern → Replicated Visits

**Mapper:** `patternToNormalizedDb.mapper.ts`  
**Location:** `packages/server/src/services/pre-planning/pattern-to-normalized-db.mapper.ts`

**Input:** Pattern object + planning horizon + `visit_templates`

**Output:** Prisma inserts to `visits` table (pinned=true, locked times)

**Purpose:** Replicate discovered pattern to all future occurrences in database

**Key Mapping Logic:**

```typescript
// Replicate pattern to all occurrences
replicatePatternToVisits(
  pattern: Pattern,
  template: VisitTemplate,
  timeHorizon: TimeHorizon
): PrismaVisitCreate[] {
  const visits: PrismaVisitCreate[] = [];
  const occurrences = calculateOccurrences(template.frequency, timeHorizon);

  for (const occurrence of occurrences) {
    // Calculate date based on pattern.dayOfWeek
    const date = findNextDateWithDayOfWeek(
      occurrence.date,
      pattern.dayOfWeek
    );

    // Calculate times based on pattern
    const startTime = combineDateAndTime(date, pattern.timeOfDay);
    const endTime = addMinutes(startTime, pattern.duration);

    visits.push({
      data: {
        id: generateUUID(),
        scheduleId: findScheduleForDate(date),
        organizationId: template.organizationId,
        clientId: template.clientId,
        movableVisitId: template.id,
        name: template.name,
        duration: pattern.duration,
        plannedStartTime: startTime,
        plannedEndTime: endTime,
        minStartTime: startTime, // Locked
        maxStartTime: startTime, // Locked
        maxEndTime: endTime, // Locked
        pinned: true, // Locked after pattern replication
        isMovable: false, // Cannot move after pinning
        visitStatus: 'planned',
        // ... other fields
      },
    });
  }

  return visits;
}
```

---

## 7. Mapper Summary Table

**Note:** This table includes **ALL scheduling mappers** (regular scheduling + pre-planning). Pre-planning specific mappers are marked with ⭐.

| Mapper                                       | Input              | Output                              | Location                                             | Use Case                                | Status     |
| -------------------------------------------- | ------------------ | ----------------------------------- | ---------------------------------------------------- | --------------------------------------- | ---------- |
| **External → Normalized DB**                 |
| `carefoxToNormalizedDb`                      | Carefox JSON       | Prisma inserts                      | `packages/server/src/integrations/mappers/`          | All scheduling                          | ❌ Missing |
| `ecareCsvToNormalizedDb`                     | eCare CSV          | Prisma inserts                      | `packages/server/src/integrations/mappers/`          | All scheduling                          | ❌ Missing |
| `phoniroCsvToNormalizedDb`                   | Phoniro CSV        | Prisma inserts                      | `packages/server/src/integrations/mappers/`          | All scheduling                          | ❌ Missing |
| `customJsonToNormalizedDb`                   | Custom JSON/CSV    | Prisma inserts                      | `packages/server/src/integrations/mappers/`          | All scheduling                          | ❌ Missing |
| `pdfToMovableVisits`                         | PDF → JSON         | Prisma inserts to `visit_templates` | `packages/server/src/integrations/mappers/`          | ⭐ Pre-planning only                    | ❌ Missing |
| **Normalized DB → Timefold API (Temporary)** |
| `normalizedDbToTimefoldInput`                | Prisma data        | Timefold JSON (temp)                | `packages/server/src/integrations/timefold/`         | All scheduling (regular + pre-planning) | ❌ Missing |
| **Timefold API → Normalized DB**             |
| `timefoldSolutionToNormalizedDb`             | Timefold JSON      | Prisma inserts                      | `packages/server/src/integrations/timefold/`         | All scheduling (regular + pre-planning) | ❌ Missing |
| `timefoldSolutionToPattern`                  | Timefold JSON      | Pattern object                      | `packages/server/src/services/pre-planning/`         | ⭐ Pre-planning only                    | ❌ Missing |
| **Normalized DB → Bryntum**                  |
| `normalizedDbToBryntum`                      | Prisma data        | Bryntum format                      | `packages/server/src/services/mappers/`              | All scheduling (regular + pre-planning) | ❌ Missing |
| `prePlanningDataToBryntum`                   | Multiple schedules | Bryntum (multi-week)                | `packages/server/src/services/mappers/pre-planning/` | ⭐ Pre-planning only                    | ❌ Missing |
| `rawSolverDataToBryntum`                     | Raw Timefold data  | Minimal Bryntum                     | `packages/server/src/services/mappers/pre-planning/` | All scheduling (real-time updates)      | ❌ Missing |
| **Bryntum → Normalized DB**                  |
| `bryntumToNormalizedDb`                      | Bryntum edits      | Prisma updates                      | `packages/server/src/services/mappers/`              | All scheduling (regular + pre-planning) | ❌ Missing |
| **Pre-Planning Specific**                    |
| `visitTemplatesToNormalizedDb`               | `visit_templates`  | Prisma inserts to `visits`          | `packages/server/src/services/pre-planning/`         | ⭐ Pre-planning only                    | ❌ Missing |
| `patternToNormalizedDb`                      | Pattern + horizon  | Prisma inserts (pinned)             | `packages/server/src/services/pre-planning/`         | ⭐ Pre-planning only                    | ❌ Missing |

**Summary:**

- **12 mappers** for **all scheduling** (regular + pre-planning)
- **4 mappers** specific to **pre-planning only** (marked with ⭐)
- **Total: 14 mappers** covering the complete scheduling system

---

## 8. Implementation Guidelines

### 8.1 Mapper Structure

**Standard Mapper Interface:**

```typescript
interface Mapper<Input, Output> {
  map(input: Input): Output;
  validate?(input: Input): ValidationResult;
  transform?(input: Input): TransformedInput;
}
```

### 8.2 Error Handling

- **Validation errors:** Return user-friendly error messages
- **Database errors:** Log and return generic error (don't expose DB details)
- **External API errors:** Retry logic with exponential backoff
- **Data inconsistencies:** Log warnings, continue processing where possible

### 8.3 Performance Considerations

- **Batch operations:** Use Prisma batch inserts for multiple records
- **Parallel processing:** Process multiple service areas in parallel
- **Caching:** Cache geocoding results, skill lookups
- **Lazy loading:** Load related data only when needed

### 8.4 Testing

- **Unit tests:** Test each mapper function independently
- **Integration tests:** Test full data flow (external → DB → Bryntum)
- **Mock data:** Use realistic test data from actual systems
- **Edge cases:** Test with missing data, invalid formats, large datasets

---

## 9. Migration from v1.0

### Key Differences

| Aspect                   | v1.0 (Legacy)                         | v2.0 (New)                     |
| ------------------------ | ------------------------------------- | ------------------------------ |
| **Storage**              | Timefold JSON in database             | Normalized relational tables   |
| **External Import**      | External → Timefold JSON → Store JSON | External → Normalized DB       |
| **Timefold Integration** | Store Timefold JSON                   | Temporary JSON for API only    |
| **Bryntum Data**         | From stored JSON                      | From normalized DB via GraphQL |
| **User Edits**           | Update JSON                           | Direct Prisma updates          |

### Migration Path

1. **Keep v1.0 mappers** for legacy data migration
2. **Create v2.0 mappers** for new architecture
3. **Gradually migrate** existing data from JSON to normalized tables
4. **Deprecate v1.0 mappers** once migration complete

---

**Last Updated:** 2025-12-09  
**Version:** 2.0  
**Status:** Specification Complete - Ready for Implementation
