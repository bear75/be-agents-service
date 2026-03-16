# Scheduling Master PRD

> **Purpose**: Single authoritative document for implementing CAIRE's scheduling system.
> **Audience**: Frontend developer (Bryntum), Backend developer (GraphQL/Prisma)
> **Last Updated**: 2026-02-05

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Core Workflows](#2-core-workflows)
3. [Visit Lifecycle](#3-visit-lifecycle)
4. [Key Concepts](#4-key-concepts)
5. [Data Model](#5-data-model)
6. [CSV Import Specification](#6-csv-import-specification)
7. [UI Specifications (Bryntum)](#7-ui-specifications-bryntum)
8. [GraphQL API Specification](#8-graphql-api-specification)
9. [Implementation Status](#9-implementation-status)
10. [Appendix](#10-appendix)

---

## 1. Executive Summary

### Problem Statement

Home care organizations manage complex scheduling with:

- Hundreds of visits per day across multiple employees
- Mix of mandatory (daily medication) and optional (weekly cleaning) visits
- External scheduling systems (eCare, Carefox) with pre-planned "slingor"
- Need to optimize travel time, workload balance, and client continuity
- Real-time disruptions (sick employees, cancelled visits)

### Solution Overview

CAIRE provides AI-powered scheduling in two phases:

1. **Pre-Planning Phase** (14-30 days horizon)
   - Import movable visit templates from municipal decisions
   - AI optimizes placement into weekly patterns (Caire-Slinga)
   - Customer approves optimized schedule

2. **Daily Scheduling Phase** (1-7 days horizon)
   - Nightly sync with external systems
   - AI optimizes daily assignments
   - Real-time disruption handling

### Key Stakeholders

| Stakeholder            | Needs                                        |
| ---------------------- | -------------------------------------------- |
| **Scheduler/Planner**  | Visual calendar, drag-drop, comparison views |
| **Operations Manager** | Metrics, KPIs, cost analysis                 |
| **Care Worker**        | Clear daily schedule, route information      |
| **Client**             | Consistent care times, preferred caregivers  |

---

## 2. Core Workflows

### 2.1 Pre-Planning: Movable Visits → Visits

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Municipal PDF   │───▶│ Movable Visits   │───▶│ Pre-Planning    │
│ (Decision)      │    │ (Broad Windows)  │    │ Optimization    │
└─────────────────┘    └──────────────────┘    └────────┬────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐    ┌────────▼────────┐
│ Fixed Daily     │◀───│ Customer         │◀───│ Caire-Slinga    │
│ Visits          │    │ Approval         │    │ (Weekly Pattern)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

**Workflow:**

1. Import movable visit templates from CSV (extracted from municipal PDFs)
2. Each template defines: client, duration, frequency, broad time window
3. AI optimization places visits into optimal day/time slots
4. Result becomes "Caire-Slinga" - weekly recurring patterns
5. Customer reviews and approves
6. Approved patterns become fixed daily visits

### 2.2 Daily Planning: Changes & Optional Visits

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Fixed Schedule  │───▶│ Disruption       │───▶│ Re-Optimization │
│ (From Slinga)   │    │ (Sick Employee)  │    │ (AI)            │
└─────────────────┘    └──────────────────┘    └────────┬────────┘
                                                        │
                       ┌──────────────────┐    ┌────────▼────────┐
                       │ Published        │◀───│ Human Review    │
                       │ Schedule         │    │ & Approval      │
                       └──────────────────┘    └─────────────────┘
```

**Key Rules:**

- **Mandatory visits** (daily medication, toilet): Must happen at fixed time ± flexibility buffer
- **Optional visits** (weekly cleaning): Can be moved to different day/time
- Solver prioritizes mandatory visits first, then fills optional

### 2.3 External Import: Slinga with Pre-Planned Visits

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ External System │───▶│ External Slinga  │───▶│ Import to CAIRE │
│ (eCare/Carefox) │    │ (CSV Export)     │    │ (Pinned=true)   │
└─────────────────┘    └──────────────────┘    └────────┬────────┘
                                                        │
                       ┌──────────────────┐    ┌────────▼────────┐
                       │ Comparison       │◀───│ Linked to       │
                       │ Baseline         │    │ Parent Movable  │
                       └──────────────────┘    └─────────────────┘
```

**Import creates:**

- Visits linked to parent movable templates via `parentId`
- All imported visits are `pinned=true` (locked baseline)
- Used for comparison against Caire optimization

### 2.4 Caire-Slinga: AI-Generated Weekly Patterns

Pre-planning optimization creates Caire's own slinga:

- "Mondays for Employee X will always have these visits"
- Optimized for travel time, workload balance
- Can be used as new baseline or merged with external

### 2.5 Comparison & Metrics

| Metric                 | Description                       | Goal     |
| ---------------------- | --------------------------------- | -------- |
| Total Travel Time      | Sum of all travel between visits  | Minimize |
| Workload Balance       | Variance in hours per employee    | Minimize |
| Client Continuity      | % visits with preferred caregiver | Maximize |
| Time Window Violations | Visits outside flexibility buffer | Zero     |
| Unassigned Visits      | Visits without employee           | Zero     |

### 2.6 Hybrid Mode: External + AI

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ External Slinga │───▶│ Pin as Baseline  │───▶│ AI Optimizes    │
│ (Imported)      │    │ (locked visits)  │    │ Around Pinned   │
└─────────────────┘    └──────────────────┘    └────────┬────────┘
                                                        │
                       ┌──────────────────┐    ┌────────▼────────┐
                       │ Hybrid Solution  │◀───│ Fill Gaps       │
                       │ (Best of Both)   │    │ (New visits)    │
                       └──────────────────┘    └─────────────────┘
```

**Adjustment Types:**

- **One-off**: Move visit for specific day only (doesn't affect future)
- **Permanent**: Move visit for all future occurrences (updates Slinga pattern)

### 2.7 Employee Placeholder Pool

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Optimization    │───▶│ Placeholder      │───▶│ Staffing Need   │
│ Request         │    │ Pool Created     │    │ Determined      │
└─────────────────┘    └──────────────────┘    └────────┬────────┘
                                                        │
                       ┌──────────────────┐    ┌────────▼────────┐
                       │ Real Employee    │◀───│ Swap Modal      │
                       │ Assigned         │    │ (Select Person) │
                       └──────────────────┘    └─────────────────┘
```

**Purpose:**

- Determine staffing needs before real employees are known
- Generic "Slot 1", "Slot 2" employees used in optimization
- After optimization, swap placeholders for real employees

---

## 3. Visit Lifecycle

### 3.1 Parent-Child Relationship (CRITICAL)

**Every concrete Visit has exactly one parent MovableVisit (n:1 relationship)**

```
MovableVisit: "Weekly Cleaning for Client A"
├── Visit: Mon 2026-01-06 10:00
├── Visit: Mon 2026-01-13 10:00
├── Visit: Mon 2026-01-20 10:00
└── Visit: Mon 2026-01-27 10:00

MovableVisit: "Daily Medication for Client B"
├── Visit: Mon 2026-01-06 08:00
├── Visit: Tue 2026-01-07 08:00
├── Visit: Wed 2026-01-08 08:00
└── ... (every day)
```

**Database Link:** `Visit.parentId` → `MovableVisit.movableVisitTemplateId`

**Why This Matters:**

- When re-optimizing, system knows which visits can be moved (recurring) vs must stay (daily)
- Parent contains constraints: allowed time windows, required skills, frequency
- Changes to parent can propagate to future visits

### 3.2 Complete Lifecycle

```
┌───────────────┐
│ 1. IMPORT     │  Municipal PDF → CSV → MovableVisit templates
└───────┬───────┘
        │
┌───────▼───────┐
│ 2. PRE-PLAN   │  AI places movables into optimal day/time → Caire-Slinga
└───────┬───────┘
        │
┌───────▼───────┐
│ 3. APPROVE    │  Customer reviews, approves patterns
└───────┬───────┘
        │
┌───────▼───────┐
│ 4. EXPAND     │  Slinga → concrete Visits for date range
└───────┬───────┘
        │
┌───────▼───────┐
│ 5. DAILY OPT  │  Nightly: sync external, optimize assignments
└───────┬───────┘
        │
┌───────▼───────┐
│ 6. EXECUTE    │  Publish to operations, care workers perform
└───────┬───────┘
        │
┌───────▼───────┐
│ 7. TRACK      │  Actual vs planned, variance analysis
└───────────────┘
```

---

## 4. Key Concepts

### 4.1 Movable vs Fixed Visits

> **Key Insight (from Maarten)**: A movable visit is "just the same as any other visit, but with an additional flag".
> Recurrence comes from templates - when creating a schedule, visits are generated based on movable visit configuration.

| Property                       | Movable Visit                      | Fixed/Daily Visit         |
| ------------------------------ | ---------------------------------- | ------------------------- |
| **Frequency**                  | Weekly, bi-weekly, monthly         | Daily                     |
| **Time Window (Pre-Planning)** | Broad (Mon 07:00 - Sun 22:00)      | N/A                       |
| **Time Window (Daily)**        | Can move within original window    | ± flexibility buffer only |
| **Mandatory for Day**          | No (can skip/move to another day)  | Yes (must be assigned)    |
| **Examples**                   | Weekly cleaning, shopping, laundry | Medication, toilet, meals |
| **Visual (Bryntum)**           | Green, dashed border               | Red, solid border         |

**How scheduling works:**

1. **Pre-planning**: Uses movable time window (e.g., Mon 07:00 - Sun 22:00, duration 30 min)
2. **Pre-planning solution**: Every movable visit gets a child fixed visit (e.g., Thursday 10:00-10:30)
3. **Daily planning** (if real-time changes needed like sick employee):
   - Movable visits CAN be moved within their original window
   - Daily visits (e.g., toilet 07:15-07:30) CANNOT be moved, must be assigned
4. **No changes**: Regular schedule is used as-is (all visits already assigned from pre-planning)

### 4.2 Pinned vs Unpinned (Timefold Concept)

| Property         | Pinned                                | Unpinned                   |
| ---------------- | ------------------------------------- | -------------------------- |
| **Definition**   | **LOCKED for BOTH solver AND human**  | Available for optimization |
| **Who can move** | Nobody (until explicitly unpinned)    | Solver can reassign        |
| **Visual**       | Solid blue, 🔒 icon                   | Dashed amber border        |
| **Use case**     | Approved patterns, locked schedules   | New visits, flexible tasks |
| **NOT same as**  | `is_movable` (recurrence flexibility) | N/A                        |

> **CRITICAL**: `pinned=true` means neither the AI solver NOR the human planner can move the visit. It's a hard lock until explicitly unpinned.

**Key distinction:**

- `pinned` = "locked for THIS solve AND for manual editing"
- `is_movable` = "can be rescheduled to different day/time in future solves"

### 4.3 Time Windows vs Flexibility Minutes

| Concept                | Pre-Planning                            | Daily Scheduling                                  |
| ---------------------- | --------------------------------------- | ------------------------------------------------- |
| **Time Window**        | Broad                                   | narrow start-end same day using duration and flex |
| **Flexibility Buffer** | N/A                                     | Custom per visit from CSV                         |
| **Purpose**            | Find optimal day/time pattern           | Fine-tune around fixed time                       |
| **Horizon**            | 14-30 days or longer                    | 1-7 days                                          |
| **Source**             | Municipal decision, customer preference | Pre-planning output + CSV config                  |

**Custom Flexibility Buffer:**

```
CSV Input:
  originalStartTime = 2026-01-06T08:00:00
  flexibilityMinutes = 60  (custom per visit!)

Database Output:
  minStartTime = 2026-01-06T07:30:00  (originalStartTime - 30 min)
  maxStartTime = 2026-01-06T08:30:00  (originalStartTime + 30 min)
  maxEndTime = 2026-01-06T09:00:00    (maxStartTime + duration)
```

### 4.4 Slinga Types

| Type                | Source                    | Pinned on Import    | Purpose               |
| ------------------- | ------------------------- | ------------------- | --------------------- |
| **External Slinga** | eCare, Carefox,           | Yes                 | Comparison baseline   |
| **Caire-Slinga**    | Pre-planning optimization | No (until approved) | AI-optimized patterns |
| **Hybrid Slinga**   | External + AI fill        | Mixed               | Best of both          |

---

## 5. Data Model

### 5.1 Database Schema (Prisma)

**Core Models:**

```prisma
model VisitTemplate {
  id                    Int      @id @default(autoincrement())
  organizationId        Int
  clientId              Int
  visitTitle            String
  visitCategory         String   // 'daily' | 'recurring'
  frequencyPeriod       String   // 'week' | 'month' | 'year'
  daysInPeriod          Int
  durationMinutes       Int
  preferredWindowStart  DateTime
  preferredWindowEnd    DateTime
  allowedWindowStart    DateTime
  allowedWindowEnd      DateTime
  skills                String[] // Required skills
  isDubbelbemanning     Boolean  @default(false)

  visits                Visit[]
}

model Visit {
  id                    Int       @id @default(autoincrement())
  scheduleId            Int
  clientId              Int
  visitTemplateId       Int?      // Link to parent movable (n:1)

  visitDate             DateTime
  startTime             DateTime
  endTime               DateTime
  duration              Int

  flexBefore            Int?      // Minutes flexibility before
  flexAfter             Int?      // Minutes flexibility after

  visitCategory         String    // 'daily' | 'recurring'
  mandatory             Boolean   @default(true)
  pinned                Boolean   @default(false)

  skills                VisitSkill[]
  assignments           SolutionAssignment[]

  visitTemplate         VisitTemplate? @relation(fields: [visitTemplateId])
  schedule              Schedule       @relation(fields: [scheduleId])
}

model Template {
  id                    Int       @id @default(autoincrement())
  organizationId        Int
  name                  String
  description           String?
  status                String    // 'draft' | 'active' | 'inactive'
  source                String    // 'external' | 'caire' | 'hybrid'

  templateVisits        TemplateVisit[]
}

model Employee {
  id                    Int       @id @default(autoincrement())
  organizationId        Int
  firstName             String
  lastName              String
  isPlaceholder         Boolean   @default(false)
  slotNumber            Int?      // For placeholders: Slot 1, Slot 2, etc.

  scheduleEmployees     ScheduleEmployee[]
}
```

### 5.2 Key Enums

```typescript
enum VisitCategory {
  daily = "daily", // Mandatory, high time sensitivity
  recurring = "recurring", // Optional, can be moved
}

enum ScheduleStatus {
  draft = "draft",
  unplanned = "unplanned",
  planned = "planned",
  published = "published",
  archived = "archived",
}

enum ScheduleType {
  original = "original",
  baseline = "baseline",
  manual = "manual",
  production = "production",
}

enum SlingaSource {
  external = "external", // eCare, Carefox
  caire = "caire", // AI-generated
  hybrid = "hybrid", // Mixed
}
```

---

## 6. CSV Import Specification

### 6.1 Import Modes

| Button                    | Location        | Mode            | Purpose                       |
| ------------------------- | --------------- | --------------- | ----------------------------- |
| "Upload schedule"         | Schedules list  | Fresh Import    | Create new schedule from CSV  |
| "Upload schedule updates" | Schedule detail | Update Import   | Add/modify visits in existing |
| "Upload solution"         | Schedule detail | Solution Import | Upload optimization result    |

### 6.2 Movable Visits CSV Format (Source of Truth)

**File:** `movable_visits_anonymized.csv`
**Delimiter:** Semicolon (`;`)
**Purpose:** Pre-planning phase - import movable visits with slinga patterns

**Row Structure:**

- Row 1: Required/Optional markers (REQ/OPT)
- Row 2: Column names

#### Complete Column Mapping (CSV → Database)

##### Slinga/Route Information

| CSV Column          | Req | DB Model.Field            | Type   | Description                     |
| ------------------- | --- | ------------------------- | ------ | ------------------------------- |
| `Slinga`            | REQ | `Template.name`           | String | Route name (e.g., "Route A1")   |
| `slinga_skills`     | OPT | `Template.metadata`       | CSV    | Skills for this slinga          |
| `slinga_frequency`  | OPT | `Template.recurrence`     | String | Pattern: "Every week, Mon"      |
| `slinga_weekday`    | REQ | `TemplateVisit.dayOffset` | String | Day: mån, tis, ons, tor, fre... |
| `slinga_start_time` | REQ | `TemplateVisit.startTime` | Time   | Shift start time                |

##### Movable Visit (Parent Template)

| CSV Column             | Req | DB Model.Field                    | Type    | Description               |
| ---------------------- | --- | --------------------------------- | ------- | ------------------------- |
| `movable_visit_id`     | REQ | `VisitTemplate.id` (external)     | String  | Parent movable ID         |
| `is_movable`           | REQ | Linkage determination             | Boolean | FALSE=daily, TRUE=movable |
| `frequency`            | REQ | `VisitTemplate.frequency`         | Enum    | daily, weekly, bi_weekly  |
| `preferred_weekday`    | OPT | `VisitTemplate.preferredDays`     | String  | Preferred day             |
| `preferred_start_time` | OPT | `VisitTemplate.preferredTimeSlot` | Time    | Preferred time            |
| `preferred_Min_before` | OPT | `VisitTemplate.metadata`          | Integer | Preferred flex before     |
| `preferred_Min_after`  | OPT | `VisitTemplate.metadata`          | Integer | Preferred flex after      |

##### Visit (Child Instance)

| CSV Column            | Req | DB Model.Field                   | Type    | Description             |
| --------------------- | --- | -------------------------------- | ------- | ----------------------- |
| `visit_id`            | REQ | `Visit.externalId`               | String  | Child visit ID          |
| `original_start_time` | REQ | `Visit.startTime`                | Time    | Requested start (HH:MM) |
| `duration`            | REQ | `Visit.durationMinutes`          | Integer | Duration in minutes     |
| `Min_before`          | REQ | → `Visit.allowedTimeWindowStart` | Integer | Flex minutes before     |
| `Min_after`           | REQ | → `Visit.allowedTimeWindowEnd`   | Integer | Flex minutes after      |
| `Prio (1-10)`         | REQ | `Visit.priority`                 | Integer | Priority 1-10           |
| `visit_category`      | OPT | `Visit.visitCategory`            | Enum    | daily, recurring        |
| `Inset_type`          | OPT | `Visit.type`                     | Enum    | VisitType enum value    |
| `description`         | OPT | `Visit.notes`                    | String  | Visit description       |
| `visit_skills`        | OPT | `VisitSkill` records             | CSV     | Required skills         |
| `double_id`           | OPT | `Visit.requiredStaff = 2`        | String  | Double staffing link    |

##### Client Information

| CSV Column            | Req | DB Model.Field         | Type    | Description      |
| --------------------- | --- | ---------------------- | ------- | ---------------- |
| `client_id`           | REQ | `Client.externalId`    | String  | Client ID        |
| `Street`              | REQ | `Address.street`       | String  | Street address   |
| `Postal_code`         | REQ | `Address.postalCode`   | String  | Postal code      |
| `City`                | REQ | `Address.city`         | String  | City             |
| `client_lat`          | REQ | `Address.latitude`     | Decimal | Latitude (10,7)  |
| `client_lon`          | REQ | `Address.longitude`    | Decimal | Longitude (10,7) |
| `care_contact_person` | OPT | `Client.contactPerson` | String  | Contact person   |

##### Shift Information

| CSV Column               | Req | DB Model.Field                       | Type    | Description         |
| ------------------------ | --- | ------------------------------------ | ------- | ------------------- |
| `shift_type`             | REQ | `ScheduleEmployeeShift.shiftType`    | Enum    | day, evening, night |
| `shift_start`            | REQ | `ScheduleEmployeeShift.startTime`    | Time    | Shift start         |
| `shift_end`              | REQ | `ScheduleEmployeeShift.endTime`      | Time    | Shift end           |
| `slinga_break_duration`  | OPT | `ScheduleEmployeeBreak.breakMinutes` | Integer | Break minutes       |
| `slinga_break_paid`      | OPT | `ScheduleEmployeeBreak.isPaid`       | Boolean | Paid break?         |
| `slinga_break_min_start` | OPT | `ScheduleEmployeeBreak.startTime`    | Time    | Break window start  |
| `slinga_break_max_end`   | OPT | `ScheduleEmployeeBreak.endTime`      | Time    | Break window end    |

##### Office Location

| CSV Column       | Req | DB Model.Field          | Type    | Description     |
| ---------------- | --- | ----------------------- | ------- | --------------- |
| `office_address` | OPT | `ServiceArea.address`   | String  | Office location |
| `office_lat`     | OPT | `ServiceArea.latitude`  | Decimal | Office lat      |
| `office_lon`     | OPT | `ServiceArea.longitude` | Decimal | Office lon      |

##### Decision Period

| CSV Column       | Req | DB Model.Field                 | Type | Description    |
| ---------------- | --- | ------------------------------ | ---- | -------------- |
| `start_decision` | OPT | `Visit.metadata.decisionStart` | Date | Decision start |
| `decision_end`   | OPT | `Visit.metadata.decisionEnd`   | Date | Decision end   |

##### Other Fields

| CSV Column             | Req | Purpose                |
| ---------------------- | --- | ---------------------- |
| `Note`                 | OPT | Import notes           |
| `inactive_visit besök` | OPT | Filter out if inactive |
| `break_address`        | OPT | Break location         |
| `break_lat/lon`        | OPT | Break coordinates      |

#### Key Relationships in Database

```
VisitTemplate (movable_visit_id)
    ↓ 1:N via Visit.visitTemplateId
Visit (visit_id)
    ↓ 1:N via SolutionAssignment.visitId
SolutionAssignment (when assigned to employee)
```

**Prisma Schema Reference:**

```prisma
model VisitTemplate {
  id                String                      @id @default(uuid())
  organizationId    String
  clientId          String
  frequency         VisitFrequency              // daily, weekly, bi_weekly, monthly
  durationMinutes   Int
  preferredDays     String[]
  preferredTimeSlot String?
  requiredSkills    String[]
  lifecycleStatus   MovableVisitLifecycleStatus
  source            MovableVisitSource
  visits            Visit[]                     // Child visits
}

model Visit {
  id                       String        @id @default(uuid())
  scheduleId               String
  clientId                 String
  visitTemplateId          String?       // → Link to parent VisitTemplate
  visitDate                DateTime
  startTime                DateTime?
  endTime                  DateTime?
  durationMinutes          Int
  visitCategory            VisitCategory // daily, recurring
  allowedTimeWindowStart   DateTime?     // Calculated from Min_before
  allowedTimeWindowEnd     DateTime?     // Calculated from Min_after
  isPinned                 Boolean       @default(false)
  priority                 Int           @default(5)
  requiredStaff            Int           @default(1)
  visitTemplate            VisitTemplate? @relation(fields: [visitTemplateId])
}
```

#### Time Window Calculation

```
CSV Input:
  original_start_time = 07:05
  Min_before = 0
  Min_after = 150

Database Output:
  Visit.startTime = 07:05
  Visit.allowedTimeWindowStart = 07:05 - 0 min = 07:05
  Visit.allowedTimeWindowEnd = 07:05 + 150 min = 09:35
```

### 6.3 Database Enums (from schema.prisma)

```prisma
enum VisitCategory { daily, recurring }
enum VisitFrequency { daily, weekly, bi_weekly, monthly, custom }
enum ShiftType { day, evening, night }
enum MovableVisitLifecycleStatus {
  identified
  user_accepted
  planned_1st
  client_preferences
  planned_client_preferences
  planned_final
  exported
}
enum MovableVisitSource { user_manual, pattern_detection, bulk_import, api }
```

### 6.4 Real Test Data

**Location:** `test-import-csv-files/3.0/caire-formated-no-empty-clientid/`

| File Pattern         | Purpose              | Key Fields                          |
| -------------------- | -------------------- | ----------------------------------- |
| `Unplanned visits *` | No employee assigned | Base visit fields only              |
| `Planned visits *`   | Slinga output        | + `plannedEmployeeId`, `slingaName` |
| `Actual visits *`    | What happened        | + `actualStart/End`, `diffMinutes`  |

**Time Spans:**

- `01-01_--01_02`: Daily (1 day)
- `01-01_--01_08`: Weekly (7 days)
- `01-01_--02_01`: Monthly (31 days)

---

## 7. UI Specifications (Bryntum)

### 7.1 Pre-Planning Hub (NEW PAGE)

**Route:** `/schedules/pre-planning`

| Feature                   | Bryntum Component                                    | Reference                                                                                        |
| ------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Multi-week calendar       | `SchedulerPro` with `viewPreset: 'weekAndDayLetter'` | [weekview](https://bryntum.com/products/schedulerpro/examples/weekview/)                         |
| Movable visits sidebar    | `Grid` with drag source                              | [drag-from-grid](https://bryntum.com/products/schedulerpro/examples/drag-from-grid/)             |
| Time window visualization | `ResourceTimeRanges`                                 | [resource-time-ranges](https://bryntum.com/products/schedulerpro/examples/resource-time-ranges/) |
| Supply/demand chart       | `Histogram` widget                                   | [histogram](https://bryntum.com/products/schedulerpro/examples/histogram/)                       |
| Optimization progress     | Custom overlay + progress bar                        | React state                                                                                      |
| Diff view (before/after)  | Two `SchedulerPro` side-by-side                      | `partners` config                                                                                |

**Visual States:**

```css
/* Movable (unoptimized) */
.b-movable-unoptimized {
  background: #dcfce7; /* light green */
  border: 2px dashed #22c55e;
}

/* Optimized (pending approval) */
.b-optimized-pending {
  background: #fef3c7; /* light yellow */
  border: 2px solid #f59e0b;
}

/* Approved */
.b-approved {
  background: #dbeafe; /* light blue */
  border: 2px solid #3b82f6;
}
```

**Page Layout:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Pre-Planning Hub                    [Optimize] [Accept] [Reject]│
├─────────────────────────────────────────────────────────────────┤
│ ┌───────────────┐ ┌───────────────────────────────────────────┐ │
│ │ Movable       │ │                                           │ │
│ │ Visits        │ │    Multi-Week SchedulerPro                │ │
│ │ (Draggable)   │ │    (14-30 days)                           │ │
│ │               │ │                                           │ │
│ │ [Cleaning]    │ │    Employee 1 |████|    |████|    |████|  │ │
│ │ [Shopping]    │ │    Employee 2 |  ████|  ████|  ████|      │ │
│ │ [Laundry]     │ │    Employee 3 |████████|████████|         │ │
│ │               │ │                                           │ │
│ └───────────────┘ └───────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ Supply/Demand Balance                                           │
│ [Histogram: Hours needed vs available per day]                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Daily Scheduling (ENHANCE EXISTING)

**Existing Files:**

- `SchedulesPage.tsx` - List view
- `ScheduleDetailPage.tsx` - Detail with solutions
- `ScheduleView.tsx` - Bryntum Scheduler
- `Scheduler.tsx` - Main scheduler
- `UnplannedScheduler.tsx` - Unplanned panel

**Enhancements Needed:**

| Enhancement           | Bryntum Feature       | Implementation                |
| --------------------- | --------------------- | ----------------------------- |
| Mandatory vs Optional | `eventRenderer`       | Color by `visitCategory`      |
| Time flexibility      | `EventTooltip`        | Show `flexBefore`/`flexAfter` |
| Parent movable link   | `eventRenderer` badge | Icon linking to parent        |
| Pinned lock icon      | `eventRenderer`       | Show 🔒 for `pinned=true`     |

**Event Renderer Example:**

```typescript
eventRenderer({ eventRecord, renderData }) {
  const visit = eventRecord.data;

  // Set CSS class based on category
  if (visit.visitCategory === 'daily') {
    renderData.cls.add('b-mandatory');
  } else {
    renderData.cls.add('b-optional');
  }

  // Add pinned icon
  if (visit.pinned) {
    renderData.cls.add('b-pinned');
    renderData.iconCls = 'b-fa b-fa-lock';
  }

  // Add parent link badge
  if (visit.parentId) {
    renderData.children.push({
      tag: 'span',
      class: 'b-parent-badge',
      text: '↑'
    });
  }

  return visit.visitTitle;
}
```

### 7.3 Slinga Management (NEW PAGE)

**Route:** `/schedules/slinga`

| Feature                  | Bryntum Component     | Reference                                                                |
| ------------------------ | --------------------- | ------------------------------------------------------------------------ |
| Weekly template view     | `SchedulerPro`        | [weekview](https://bryntum.com/products/schedulerpro/examples/weekview/) |
| Recurring pattern editor | Custom modal          | Template → Visit expansion                                               |
| Comparison overlay       | `eventRenderer` ghost | Semi-transparent baseline                                                |

**Page Layout:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Slinga Management                   [Import] [Export] [Compare] │
├─────────────────────────────────────────────────────────────────┤
│ ┌───────────────────────────────────────────────────────────────┐
│ │ External Slinga: "eCare Import 2026-01"                       │
│ │ ─────────────────────────────────────────                     │
│ │ Mon | Tue | Wed | Thu | Fri | Sat | Sun                       │
│ │ ████  ████  ████  ████  ████                                  │
│ └───────────────────────────────────────────────────────────────┘
│ ┌───────────────────────────────────────────────────────────────┐
│ │ Caire-Slinga: "Optimized 2026-01"                    [Accept] │
│ │ ─────────────────────────────────────────                     │
│ │ Mon | Tue | Wed | Thu | Fri | Sat | Sun                       │
│ │ ████  ░░░░  ████  ░░░░  ████                  (░ = ghost)     │
│ └───────────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────┘
```

### 7.4 Comparison View (NEW COMPONENT)

| Feature                | Bryntum Component  | Implementation           |
| ---------------------- | ------------------ | ------------------------ |
| Side-by-side schedules | Two `SchedulerPro` | Linked via `partners`    |
| Metrics panel          | `Panel`            | Custom React component   |
| Diff highlighting      | `eventRenderer`    | Green=added, Red=removed |

**Diff Colors:**

```css
.b-diff-added {
  background: #22c55e;
} /* Green */
.b-diff-removed {
  background: #ef4444;
} /* Red */
.b-diff-modified {
  background: #f59e0b;
} /* Yellow */
.b-diff-unchanged {
  opacity: 0.5;
} /* Faded */
```

### 7.5 Employee Placeholder UI

| Feature          | Bryntum Component | Implementation                      |
| ---------------- | ----------------- | ----------------------------------- |
| Placeholder rows | `ResourceColumn`  | Gray styling via `resourceRenderer` |
| Swap modal       | React Dialog      | Employee dropdown                   |
| Pool status      | Badge             | "3 placeholders to fill"            |

**Resource Renderer Example:**

```typescript
resourceRenderer({ resourceRecord, renderData }) {
  if (resourceRecord.data.isPlaceholder) {
    renderData.cls.add('b-placeholder');
    return `Slot ${resourceRecord.data.slotNumber}`;
  }
  return `${resourceRecord.data.firstName} ${resourceRecord.data.lastName}`;
}
```

### 7.6 Visual System Summary

> **UI Prototype** (no BE integration): [bryntum-vite.vercel.app](https://bryntum-vite.vercel.app/)
>
> This is a frontend prototype showing the target UI design. Maarten will build the integrated version with GraphQL backend.

#### Schedule-Level (Header)

| Element           | Current UI                   | Description               |
| ----------------- | ---------------------------- | ------------------------- |
| Revision dropdown | "Rev 1 - Baseline (Carefox)" | Schedule version + source |
| Actions           | Spara, Optimera, Jämför      | Save, Optimize, Compare   |

#### Filter Panel (Already Built)

| Category          | Swedish      | Options                                            |
| ----------------- | ------------ | -------------------------------------------------- |
| **BESÖK**         | Visit type   | Standard, Obligatorisk, Extra, Inställt, Frånvaro  |
| **Frequency**     | Frekvens     | Daglig, Veckovis, Varannan vecka, Månadsvis        |
| **Locked**        | Låst         | Pinned visits filter                               |
| **PRIORITET**     | Priority     | Slider 0-10 (no visual on visits)                  |
| **BEMANNING**     | Staffing     | Enkelbemanning, Dubbelbemanning                    |
| **KOMPETENS**     | Skills       | Balans, Demens, Dusch, Medicin, etc. (FILTER ONLY) |
| **SERVICEOMRÅDE** | Service area | Västra, Östra, Södra                               |

#### Visit Event Colors (from current UI)

| Type         | Swedish   | Color   | Description      |
| ------------ | --------- | ------- | ---------------- |
| Standard     | Standard  | Blue    | Regular visits   |
| Obligatorisk | Mandatory | Red     | Must happen      |
| Extra        | Extra     | Striped | Additional visit |
| Inställt     | Cancelled | Gray    | Cancelled        |
| Frånvaro     | Absence   | -       | Employee absence |

#### Frequency Filters (affects which visits shown)

| Frequency      | Swedish   | Description     |
| -------------- | --------- | --------------- |
| Daglig         | Daily     | Every day       |
| Veckovis       | Weekly    | Once per week   |
| Varannan vecka | Bi-weekly | Every two weeks |
| Månadsvis      | Monthly   | Once per month  |

#### Staffing Visual

| Type            | Swedish | Visual                          |
| --------------- | ------- | ------------------------------- |
| Enkelbemanning  | Single  | Normal event                    |
| Dubbelbemanning | Double  | Event with 👥 or thicker border |

#### Skills (FILTER ONLY - not shown per visit)

Skills are used for **filtering** the view, not as visual indicators on events:

- Balans, Demens, Dusch, Inkop, Insulin, Matlagning, Medicin
- Palliativ vård, Personlig omvårdnad, Promenad, Provtagning
- Rehab, Städning, Sällskap, Sårvård, Träning

#### Employee Row Styling

| Type                 | Row Background       | Icon | CSS Class       |
| -------------------- | -------------------- | ---- | --------------- |
| Real Employee        | White/default        | -    | -               |
| Placeholder Employee | Light gray `#f3f4f6` | 👤   | `b-placeholder` |

---

## 8. GraphQL API Specification

### 8.1 Pre-Planning Operations

**Queries:**

```graphql
# Get supply/demand balance for date range
query SupplyDemandBalance(
  $organizationId: ID!
  $startDate: DateTime!
  $endDate: DateTime!
) {
  supplyDemandBalance(
    organizationId: $organizationId
    startDate: $startDate
    endDate: $endDate
  ) {
    date
    requiredHours
    availableHours
    gap
    employees {
      id
      name
      availableHours
      assignedHours
    }
  }
}

# Get movable visits for organization
query MovableVisits($organizationId: ID!, $limit: Int, $offset: Int) {
  movableVisits(
    organizationId: $organizationId
    limit: $limit
    offset: $offset
  ) {
    records {
      id
      clientId
      clientName
      visitTitle
      visitCategory
      frequencyPeriod
      daysInPeriod
      durationMinutes
      preferredWindowStart
      preferredWindowEnd
      skills
    }
    total
  }
}
```

**Mutations:**

```graphql
# Start pre-planning optimization
mutation StartPrePlanningOptimization($input: PrePlanningInput!) {
  startPrePlanningOptimization(input: $input) {
    id
    status
    progress
    estimatedCompletion
  }
}

# Accept pre-planning solution
mutation AcceptPrePlanningSolution($solutionId: ID!) {
  acceptPrePlanningSolution(solutionId: $solutionId) {
    id
    status
    templateId # Created Caire-Slinga
  }
}
```

**Subscriptions:**

```graphql
# Real-time optimization progress
subscription PrePlanningProgress($jobId: ID!) {
  prePlanningProgress(jobId: $jobId) {
    progress
    currentPhase
    estimatedRemaining
    intermediateScore
  }
}
```

### 8.2 Slinga Operations

**Mutations:**

```graphql
# Import external slinga from CSV
mutation ImportSlinga(
  $organizationId: ID!
  $fileBase64: String!
  $fileName: String!
) {
  importSlinga(
    organizationId: $organizationId
    fileBase64: $fileBase64
    fileName: $fileName
  ) {
    id
    name
    source
    visitCount
    employeeCount
  }
}

# Expand slinga to concrete visits
mutation ExpandSlingaToVisits(
  $templateId: ID!
  $startDate: DateTime!
  $endDate: DateTime!
) {
  expandSlingaToVisits(
    templateId: $templateId
    startDate: $startDate
    endDate: $endDate
  ) {
    scheduleId
    visitCount
  }
}

# Hybrid optimization (external + AI)
mutation HybridOptimization($input: HybridOptimizationInput!) {
  hybridOptimization(input: $input) {
    id
    status
    baselineTemplateId
    pinnedVisitCount
    optimizedVisitCount
  }
}
```

### 8.3 Placeholder Operations

**Mutations:**

```graphql
# Ensure placeholder pool exists
mutation EnsurePlaceholderPool($organizationId: ID!, $count: Int!) {
  ensurePlaceholderPool(organizationId: $organizationId, count: $count) {
    placeholders {
      id
      slotNumber
    }
    created
    existing
  }
}

# Swap placeholder for real employee
mutation SwapPlaceholderToEmployee(
  $placeholderId: ID!
  $employeeId: ID!
  $scheduleId: ID!
) {
  swapPlaceholderToEmployee(
    placeholderId: $placeholderId
    employeeId: $employeeId
    scheduleId: $scheduleId
  ) {
    success
    assignmentsTransferred
  }
}
```

### 8.4 Comparison Operations

**Queries:**

```graphql
# Compare two schedules/solutions
query CompareSchedules($scheduleIds: [ID!]!) {
  compareSchedules(scheduleIds: $scheduleIds) {
    schedules {
      id
      name
      metrics {
        totalTravelTime
        workloadVariance
        clientContinuity
        unassignedCount
      }
    }
    diff {
      added {
        visitId
        reason
      }
      removed {
        visitId
        reason
      }
      modified {
        visitId
        field
        oldValue
        newValue
      }
    }
    winner {
      scheduleId
      reason
    }
  }
}
```

---

## 9. Implementation Status

### 9.0 UI Prototype (No BE Integration)

**URL:** [bryntum-vite.vercel.app](https://bryntum-vite.vercel.app/)

This is a frontend-only prototype showing the target UI design:

- Filter system (visit types, frequency, staffing, skills, service areas)
- Revision dropdown (schedule source)
- Bryntum Scheduler layout
- **No backend integration yet** - Maarten will build the integrated version

### 9.1 Already Implemented (in beta-appcaire)

| Component                  | Status  | Files                                         |
| -------------------------- | ------- | --------------------------------------------- |
| Schedule list/detail pages | ✅ Done | `SchedulesPage.tsx`, `ScheduleDetailPage.tsx` |
| CSV upload (3 types)       | ✅ Done | `UploadCsvModal.tsx`                          |
| Bryntum Scheduler (basic)  | ✅ Done | `Scheduler.tsx`, `UnplannedScheduler.tsx`     |
| Solution management        | ✅ Done | `solution/` resolvers                         |
| Timefold optimization      | ✅ Done | `timefold.service.ts`                         |
| Drag/drop assignments      | ✅ Done | `SchedulerContainer.tsx`                      |
| Visit pinning              | ✅ Done | `visit-pinning.service.ts`                    |

**Gap:** The basic Bryntum integration in beta-appcaire needs to be enhanced with the filter system and visual styling from the prototype.

### 9.2 Needs Implementation

| Epic                                 | Priority | Effort |
| ------------------------------------ | -------- | ------ |
| **1. Pre-Planning Backend**          | High     | Large  |
| - Movable visits GraphQL API         |          |        |
| - Pre-planning orchestrator          |          |        |
| - Supply/demand query                |          |        |
| **2. Slinga Integration**            | High     | Medium |
| - Slinga CSV import                  |          |        |
| - Slinga → Visit expansion           |          |        |
| - Comparison service                 |          |        |
| **3. Placeholder Pool**              | Medium   | Small  |
| - Placeholder management API         |          |        |
| - Swap mutation                      |          |        |
| **4. Pre-Planning UI**               | High     | Large  |
| - Multi-week calendar page           |          |        |
| - Movable visits sidebar             |          |        |
| - Supply/demand histogram            |          |        |
| **5. Daily Scheduling Enhancements** | Medium   | Medium |
| - Mandatory/optional visual          |          |        |
| - Parent link badge                  |          |        |
| - Comparison mode                    |          |        |
| **6. Schedule Versioning**           | Low      | Medium |
| - Version history UI                 |          |        |
| - Rollback functionality             |          |        |
| **7. Integration & Testing**         | Medium   | Medium |
| - E2E flows                          |          |        |
| - Performance testing                |          |        |

---

## 10. Appendix

### 10.1 Related Documentation

- [BRYNTUM_FROM_SCRATCH_PRD.md](bryntum_consultant_specs/BRYNTUM_FROM_SCRATCH_PRD.md) - Bryntum-specific details
- [PREPLANNING_FRONTEND_IMPLEMENTATION.md](../09-scheduling/PREPLANNING_FRONTEND_IMPLEMENTATION.md) - Frontend guide
- [PINNED_VISITS_GUIDE.md](../09-scheduling/PINNED_VISITS_GUIDE.md) - Pinned visits explanation
- [MOVABLE_VISITS.md](../09-scheduling/MOVABLE_VISITS.md) - Movable visit lifecycle

### 10.2 Bryntum Example Links

| Feature              | Example URL                                                                              |
| -------------------- | ---------------------------------------------------------------------------------------- |
| Week view            | https://bryntum.com/products/schedulerpro/examples/weekview/                             |
| Drag from grid       | https://bryntum.com/products/schedulerpro/examples/drag-from-grid/                       |
| Resource time ranges | https://bryntum.com/products/schedulerpro/examples/resource-time-ranges/                 |
| Histogram            | https://bryntum.com/products/schedulerpro/examples/histogram/                            |
| Advanced React       | https://bryntum.com/products/schedulerpro/examples/frameworks/react/javascript/advanced/ |

### 10.3 Test Data Location

```
test-import-csv-files/3.0/caire-formated-no-empty-clientid/
├── Unplanned visits 01-01_--01_02.csv      # 1 day, no employees
├── Unplanned visits 01-01_--01_08.csv      # 1 week, no employees
├── Unplanned visits 01-01_--02_01.csv      # 1 month, no employees
├── Planned visits 01-01_--01_02.csv        # 1 day, with slinga
├── Planned visits 01-01_--01_08.csv        # 1 week, with slinga
├── Actual visits 01-01_--01_08.csv         # 1 week, what happened
└── *-with-locations.csv                    # Geocoded versions
```

### 10.4 Jira Epic References

- C0-26, C0-27, C0-125, C0-141, C0-240, C0-259

**Recommended:** Create umbrella epic "Scheduling 2.0 - Unified Implementation" linking all related epics.

---

_Document created: 2026-02-05_
_Next review: After stakeholder feedback_
