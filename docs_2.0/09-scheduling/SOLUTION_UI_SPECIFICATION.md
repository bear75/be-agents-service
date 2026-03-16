# Solution UI Specification

**Purpose:** Complete specification for displaying visits in the solutions/schedule UI
**Audience:** Backend developers, Frontend developers, Product
**Last Updated:** 2026-03-02

---

## Table of Contents

1. [Overview](#overview)
2. [User-Centered Data Presentation](#user-centered-data-presentation)
3. [Backend Requirements](#backend-requirements)
4. [Frontend UX Requirements](#frontend-ux-requirements)
5. [Data Model Reference](#data-model-reference)
6. [Visual Examples](#visual-examples)

---

## Overview

This document specifies what data the backend must provide and what visual/interactive features the frontend must implement for displaying visits in the schedule/solution UI (Bryntum SchedulerPro).

**Priority:** Ensure **all visit information** is available (backend data contract and queries). Colors, icons, and what appears on the card vs tooltip vs detail panel are UX decisions that can be changed once the data is in place. See [../../archive/SOLUTION_UI_PRD.md](../../archive/SOLUTION_UI_PRD.md) § Priority: Data First.

### Visual Dimensions

Visits have **two base dimensions plus additional indicators**:

#### Base Dimensions:

1. **Visit Category** (visitCategory) - Background color
   - 🔴 **Mandatory** (daily) - Must happen today, fixed time window
   - 🟢 **Optional** (recurring) - Can be rescheduled, flexible

2. **Visit Status** - Badge/Overlay
   - Regular (no badge)
   - ✨ Extra (added by planner)
   - ❌ Cancelled
   - 👤 Absent (employee absence, not a visit)

#### Additional Indicators:

3. **Priority** (1-10, default 6) — On **event card**: show ⚠️ only for critical (1-3). Low (8-10) in tooltip/detail only.
4. **Pinned** (isPinned) - 🔒 Lock icon on card if true.
5. **Other constraints:** On card only 👥 double staffing when `requiredStaff > 1`. In tooltip/detail: 🎯 Required skills, 📍 Address, 👤 Preferred employees, 🏷️ Tags. **Transport icon is per employee** (resource column), not on visit events.

#### Visit card space constraint

Visits can be **5–180 minutes**; card space is limited. Show only: category background colour, client + visit type, time + duration, and up to three icons when applicable (👥 double staffing, ⚠️ critical priority, 🔒 pinned). Cancelled/absent use greyed base colour (mandatory/optional tint). No low-priority badge, skills, address, preferences, tags, or transport on the card. See [../../archive/SOLUTION_UI_PRD.md](../../archive/SOLUTION_UI_PRD.md) § Visit Display Rules for full rules.

#### Allowed / flex time window

Do not draw the full allowed window on the timeline by default. On **hover**: show via shadow/ghost events, transparent band, or a Client & visit tab with calendar (e.g. Timefold-portal style). Tooltip can state allowed window (e.g. "⏰ Allowed: 08:00–09:00").

---

## User-Centered Data Presentation

### Use Cases & Information Hierarchy

Schedulers interact with visit data in different ways depending on their task:

#### 1. Quick Scan (Timeline View)

**User need:** "Which visits need my attention?"

**Must show immediately (without hovering):**

- **Background:** 🔴 Mandatory or 🟢 Optional (category colour only).
- Client name (truncate if needed) + visit type.
- Time slot + duration (e.g. 08:00–08:30 (30 min)).
- **Icons only when applicable:** 👥 double staffing, ⚠️ critical priority (1–3), 🔒 pinned. No low-priority badge, skills, address, preferences, tags, or transport on the card. Cancelled/absent: greyed base colour. Skill mismatch can be in tooltip.

**Visual budget:** ~80–120px wide; visits 5–180 min so space is limited. See PRD § Visit Display Rules.

```
┌─────────────────────────┐
│ Anna A.  Medication     │ ← Client + type (truncate if needed)
│ ⚠️ 👥 🔒 08:00-08:30   │ ← Icons only if applicable + time
│ (30 min)                │ ← Duration
└─────────────────────────┘
```

#### 2. Quick Validation (Hover/Tooltip)

**User need:** "Can I assign this visit to this employee?"

**Must show in tooltip (1-2 second hover):**

**Essential constraints:**

- ⏰ Allowed time window
- 🎯 Required skills + levels
- 👤 Preferred/avoided employees
- 📍 Address (for travel estimation)
- 📝 Critical notes

**Format for fast scanning:**

```
Anna Andersson - Medication

⏰ Must be: 08:00-09:00 (allowed window)
🎯 Required: Medication administration (Level 2)
👤 Prefers: Maria S., Karin L.
📍 Storgatan 123, 12345 Stockholm
⚠️ NOTE: Diabetes - insulin injection
```

#### 3. Detailed Inspection (Edit Modal/Panel)

**User need:** "I need to modify this visit or understand all constraints"

**Show all data organized by category:**

```
┌─────────────────────────────────────────────────────────┐
│ Visit Details - Anna Andersson                      [X] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ CLIENT INFORMATION                                      │
│ Name: Anna Andersson                                    │
│ Address: Storgatan 123, 12345 Stockholm                 │
│ Phone: 070-123 45 67                                    │
│                                                         │
│ ─────────────────────────────────────────────────────── │
│                                                         │
│ VISIT TYPE & CATEGORY                                  │
│ Type: Medication administration                        │
│ Category: 🔴 Fixed to today (must happen)              │
│ Frequency: Daily                                       │
│ Duration: 30 minutes                                   │
│                                                         │
│ ─────────────────────────────────────────────────────── │
│                                                         │
│ SCHEDULING CONSTRAINTS                                  │
│ Priority: 1 / 10 (⚠️ Critical)                         │
│ Allowed window: 08:00 - 09:00                          │
│ Preferred window: 08:15 - 08:45                        │
│ Required staff: 1                                      │
│                                                         │
│ ─────────────────────────────────────────────────────── │
│                                                         │
│ SKILLS REQUIRED                                        │
│ ✓ Medication administration (Level 2) - REQUIRED       │
│ ○ Diabetes care (Level 1) - Preferred                  │
│                                                         │
│ ─────────────────────────────────────────────────────── │
│                                                         │
│ EMPLOYEE PREFERENCES                                    │
│ ✓ Preferred: Maria S., Karin L.                        │
│ ✗ Avoid: Johan K. (client request)                     │
│ Continuity: 8 of last 10 visits with Maria S.          │
│                                                         │
│ ─────────────────────────────────────────────────────── │
│                                                         │
│ ASSIGNMENT STATUS                                       │
│ Status: 🔒 Locked                                      │
│ Assigned to: Maria Svensson                            │
│ Sequence: #3 in route                                  │
│ Travel before: 15 min (🚗 from previous visit)         │
│ Travel after: 10 min (🚗 to next visit)                │
│                                                         │
│ ─────────────────────────────────────────────────────── │
│                                                         │
│ NOTES                                                  │
│ "Insulin injection - use pen from fridge. Client       │
│  prefers right arm. Check blood sugar first."          │
│                                                         │
│ ─────────────────────────────────────────────────────── │
│                                                         │
│ EXECUTION HISTORY (if available)                       │
│ Last 5 visits:                                         │
│ • 2026-03-01 08:15-08:42 ✓ Maria S. (on time)         │
│ • 2026-02-29 08:20-08:48 ✓ Maria S. (+5 min late)     │
│ • 2026-02-28 08:10-08:35 ✓ Karin L. (early)           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Data Grouping & Progressive Disclosure

**Level 1 - Always Visible (Event Card)**

```typescript
interface VisitEventCard {
  // Identity (who, what)
  clientName: string; // "Anna A." (truncate)
  visitType: VisitType; // Icon + label

  // Time (when)
  startTime: string; // "08:00"
  endTime: string; // "08:30"
  duration: number; // 30 (show "30 min")

  // Critical indicators (problems/constraints)
  timeConstraint: "fixed" | "flexible"; // 🔴 or 🟢
  isPinned: boolean; // 🔒 if true
  priority: number; // Show ⚠️ if ≤3, ↓ if ≥8
  requiredStaff: number; // Show 👥 if >1
  hasSkillMismatch?: boolean; // Show ⚠️ if assigned to unqualified employee
}
```

**Level 2 - Hover Tooltip (Validation Info)**

```typescript
interface VisitTooltip {
  // From Level 1
  ...VisitEventCard;

  // Constraints for quick decision-making
  allowedTimeWindow: { start: string; end: string };
  requiredSkills: Array<{ name: string; level?: number; required: boolean }>;
  preferredEmployees: string[];  // Names
  avoidedEmployees: string[];    // Names
  address: string;               // Full address
  criticalNotes?: string;        // First 100 chars of notes if marked critical

  // Status
  assignmentStatus: 'unassigned' | 'assigned' | 'locked';
  currentEmployee?: string;
}
```

**Level 3 - Detail Panel (Complete Information)**

```typescript
interface VisitDetailPanel {
  // From Level 1 & 2
  ...VisitTooltip;

  // Complete client info
  client: {
    name: string;
    externalId: string;
    phone?: string;
    contactPerson?: string;
  };

  // Complete address
  address: {
    street: string;
    postalCode: string;
    city: string;
    coordinates?: { lat: number; lng: number };
  };

  // Complete scheduling
  preferredTimeWindow?: { start: string; end: string };
  allSkills: Array<{ name: string; level?: number; required: boolean }>;
  allTags: string[];

  // Template info (if recurring)
  template?: {
    frequency: string;
    lifecycleStatus: string;
    source: string;
    patternConfidence?: number;
  };

  // Full notes
  notes?: string;
  metadata?: any;

  // Assignment details
  assignment?: {
    employee: string;
    sequenceNumber: number;
    travelTimeBefore: number;
    travelTimeAfter: number;
    waitingTime: number;
  };

  // Execution history
  executionHistory?: Array<{
    date: string;
    employee: string;
    actualStart: string;
    actualEnd: string;
    deviation?: number;
    checkInSource?: string;
  }>;
}
```

### Essential vs Optional Data

#### ❗ ESSENTIAL - Backend MUST provide, UI MUST show

**For ANY visit to be usable in scheduling:**

```typescript
{
  // Identity
  id: string;
  clientId: string;
  clientName: string; // ← MUST show in event

  // Time
  visitDate: Date;
  startTime: Date; // ← MUST show in event
  endTime: Date; // ← MUST show in event
  durationMinutes: number; // ← MUST show in event

  // Classification
  visitCategory: "daily" | "recurring"; // ← MUST show (🔴/🟢)
  type: VisitType; // ← MUST show (icon + label)

  // Constraints
  priority: number; // ← MUST show if ≠6
  isPinned: boolean; // ← MUST show if true
  requiredStaff: number; // ← MUST show if >1

  // Status
  visitStatus: "unassigned" | "scheduled"; // ← Determines placement
}
```

**Total: 13 fields minimum for basic scheduling UI**

#### ⭐ IMPORTANT - Strongly recommended for good UX

**Makes scheduling decisions easier:**

```typescript
{
  // Time constraints
  allowedTimeWindowStart: Date;     // Show in tooltip
  allowedTimeWindowEnd: Date;       // Show in tooltip

  // Skills
  skills: Array<{
    skillName: string;              // Show in tooltip
    isRequired: boolean;            // Highlight required
    level?: number;                 // Show level if specified
  }>;

  // Location
  address: {
    street: string;                 // Show in tooltip
    city: string;                   // Show in tooltip
  };

  // Preferences
  preferences: {
    preferredEmployeeIds: string[]; // Show in tooltip
    avoidedEmployeeIds: string[];   // Show in tooltip
  };

  // Notes
  notes?: string;                   // Show first line in tooltip
}
```

**Total: +8 fields for good scheduling UX**

#### ℹ️ NICE TO HAVE - Enhances workflow, not critical

**Useful for analysis, history, and advanced features:**

```typescript
{
  // Template tracking
  visitTemplateId?: string;
  recurrenceType?: string;
  visitTemplate?: { /* ... */ };

  // Preferred time (softer than allowed)
  preferredTimeWindowStart?: Date;
  preferredTimeWindowEnd?: Date;

  // Tags
  tags?: string[];

  // Travel time (usually calculated by solver)
  travelTimeBefore?: number;
  travelTimeAfter?: number;
  waitingTime?: number;

  // Execution tracking
  actualStartTime?: Date;
  actualEndTime?: Date;
  checkInTime?: Date;
  checkInSource?: string;
  deviationMinutes?: number;
  deviationReason?: string;

  // Metadata
  metadata?: any;
  externalId?: string;
}
```

### Visual Encoding Principles

#### 1. Background Color = Visit Category (visitCategory)

**The MOST IMPORTANT visual indicator - determines scheduling flexibility:**

```
🔴 Red (#fef2f2)    = Mandatory (daily) - Must happen today, narrow time window
🟢 Green (#f0fdf4)  = Optional (recurring) - Can reschedule, flexible time window
```

**Accessibility (NOT color-blind dependent):**

- Red has **solid** left border (4px #dc2626)
- Green has **dashed** left border (4px #16a34a)

#### 2. Status Overlay/Badge = What Happened

**Shows lifecycle state of the visit:**

```
(no badge)  = Regular visit (normal)
✨          = Extra (added by planner after optimization)
❌          = Cancelled (grey overlay + strikethrough)
```

**Cancelled styling:**

```css
.visit-cancelled {
  background: #f3f4f6 !important; /* Override red/green */
  opacity: 0.6;
  text-decoration: line-through;
}
```

#### 3. Priority Badge = Urgency (1-10)

**Only show if priority ≠ 6 (default):**

```
⚠️ 1-3  = Critical priority (red badge)
(none)  = Normal priority 4-7 (no badge)
↓ 8-10  = Low priority (grey badge)
```

#### 4. Other Indicators = Constraints

**Always show when applicable:**

```
🔒  = Pinned/Locked (cannot be moved)
👥  = Double staffing (requiredStaff > 1)
🎯  = Required skills (show in tooltip)
📍  = Address (show in tooltip)
```

#### 5. Visit Type Icons = What Service

**Show icon + label:**

```
🏥  = Medical/Medication
🧹  = Cleaning
🍽️  = Meals
🚶  = Walk/Outing
🛁  = Bath/Shower
🛒  = Shopping
```

#### 6. Travel Mode Icons = How to Get There

```
🚗  = Car travel
🚴  = Bike travel
🚶  = Walking
🚌  = Public transit
```

#### 7. Spatial Positioning = Information Type

```
┌────────────────────────────────┐
│ Top:    Client name           │  ← Who (most important)
│ Middle: Visit type            │  ← What
│ Bottom: Time + Duration       │  ← When
│ Right:  Badges (⚠️🔒👥)       │  ← Constraints/warnings
└────────────────────────────────┘
```

### Readability Patterns

#### Pattern 1: Scannable Lists

**Problem:** 50+ visits in unplanned panel
**Solution:** Group and highlight

```
UNPLANNED VISITS (23)

CRITICAL (Priority 1-3)
  ⚠️ 1  Anna A. - Medication        08:00-08:30
  ⚠️ 2  Erik E. - Insulin            09:00-09:15

NORMAL (Priority 4-7)
  Maria S. - Cleaning              10:00-11:30
  Johan N. - Shopping              14:00-15:00

LOW PRIORITY (Priority 8-10)
  ↓ 9  Karin L. - Social visit      anytime today
```

#### Pattern 2: Progressive Disclosure in Tooltips

**Problem:** Too much text in tooltip
**Solution:** Collapse non-critical sections

```
Anna Andersson - Medication

🔴 MUST HAPPEN: 08:00-09:00 today
⚠️ PRIORITY: 1 (Critical)
🎯 REQUIRES: Medication admin (Level 2)
📍 Storgatan 123, Stockholm

▼ More details...  ← Collapsed by default
  ☑ Preferred: Maria S., Karin L.
  ☐ Template: Daily medication pattern
  ☐ History: 98% on-time last month
```

#### Pattern 3: Smart Truncation

**Client names in event cards:**

```typescript
function truncateClientName(name: string, maxWidth: number): string {
  if (name.length <= 12) return name;

  // Keep first name + last initial
  const parts = name.split(" ");
  if (parts.length >= 2) {
    return `${parts[0]} ${parts[parts.length - 1][0]}.`;
  }

  // Truncate single name
  return name.substring(0, 10) + "...";
}

// Examples:
// "Anna Andersson" → "Anna A."
// "Maria" → "Maria"
// "Erik Eriksson Svensson" → "Erik S."
```

#### Pattern 4: Contextual Information

**Show different data based on context:**

```typescript
// When dragging (focus on compatibility)
showOnDrag = {
  requiredSkills: true,
  employeeSkills: true, // Highlight on employee rows
  allowedTimeWindow: true,
  preferredEmployees: false, // Less important during drag
};

// When comparing solutions (focus on changes)
showOnCompare = {
  assignment: true,
  assignmentChange: true, // NEW, MOVED, REMOVED
  travelTimeChange: true,
  sequenceNumberChange: true,
};

// When filtering (focus on match criteria)
showOnFilter = {
  priority: true,
  skills: true,
  visitType: true,
  timeConstraint: true,
};
```

### Performance Considerations

**Data size matters for 100+ visit schedules:**

#### Lazy Load Detail Data

```typescript
// Level 1: Always loaded (in main query)
interface VisitSummary {
  id: string;
  clientName: string;
  visitType: VisitType;
  startTime: Date;
  endTime: Date;
  priority: number;
  isPinned: boolean;
  requiredStaff: number;
  visitCategory: "daily" | "recurring";
}

// Level 2: Load on hover (batch query for visible viewport)
interface VisitConstraints {
  id: string;
  allowedTimeWindow: { start: Date; end: Date };
  requiredSkills: string[];
  address: string;
}

// Level 3: Load on click (individual query)
interface VisitFullDetails {
  id: string;
  // Everything else...
}
```

#### Data Pagination

```typescript
// Don't load all execution history upfront
executionHistory: {
  recent: Visit[];        // Last 3 visits, loaded with main query
  count: number;          // Total count
  loadMore: () => Promise<Visit[]>;  // Load on demand
}
```

### Accessibility & Localization

#### Screen Reader Support

```typescript
// Event aria-label
aria-label={`
  ${visit.priority <= 3 ? 'Critical priority' : ''}
  ${visit.isPinned ? 'Locked' : ''}
  ${visit.visitCategory === 'daily' ? 'Fixed to today' : 'Flexible'}
  visit for ${visit.clientName},
  ${formatVisitType(visit.type)},
  ${formatTime(visit.startTime)} to ${formatTime(visit.endTime)},
  ${visit.durationMinutes} minutes
  ${visit.requiredStaff > 1 ? `, requires ${visit.requiredStaff} staff` : ''}
`}
```

#### Localization Keys

```typescript
{
  "visit.timeConstraint.fixed": "Fixed to today",
  "visit.timeConstraint.flexible": "Date flexible",
  "visit.priority.critical": "Critical",
  "visit.priority.low": "Low priority",
  "visit.status.pinned": "Locked",
  "visit.staffing.double": "Double staffing required",

  // Visit types (20 types)
  "visit.type.morning_care": "Morning care",
  "visit.type.medication": "Medication",
  // ... etc
}
```

---

## Backend Requirements

### 1. GraphQL Query: Get Schedule with Solution

**Query:**

```graphql
query GetScheduleWithSolution($scheduleId: ID!, $solutionId: ID) {
  schedule(id: $scheduleId) {
    id
    startDate
    endDate
    serviceAreaId

    # Current/selected solution
    solution(id: $solutionId) {
      id
      status
      score
      createdAt

      # Solution metrics
      metrics {
        totalTravelTimeSeconds
        totalWaitingTimeSeconds
        totalServiceHours
        staffUtilizationPercentage
        unassignedVisitsCount
        continuityScore
      }

      # Visit assignments
      assignments {
        id
        visitId
        scheduleEmployeeId
        eventType
        startTime
        endTime
        sequenceNumber
        travelTimeBefore
        travelTimeAfter
        waitingTime
      }
    }

    # All visits for this schedule
    visits {
      # Core identity
      id
      externalId
      scheduleId
      clientId
      addressId

      # Client info (populated)
      client {
        id
        name
        externalId
      }

      # Address info (populated)
      address {
        id
        street
        postalCode
        city
        latitude
        longitude
      }

      # Visit timing
      visitDate
      startTime
      endTime
      durationMinutes

      # Time constraints
      allowedTimeWindowStart
      allowedTimeWindowEnd
      preferredTimeWindowStart
      preferredTimeWindowEnd

      # Visit classification
      visitCategory # daily | recurring
      type # VisitType enum (20 types)
      recurrenceType
      visitTemplateId

      # Scheduling properties
      visitStatus # unassigned | scheduled
      priority # 1-10 (1=highest, 10=lowest, 6=default)
      requiredStaff # 1 or 2+ (for double staffing)
      isPinned # boolean
      pinnedEmployeeId # if pinned
      # Status flags
      isExtra # boolean - added by planner after optimization
      cancelled # boolean - visit cancelled
      # Skills & preferences
      skills {
        id
        skillName
        isRequired
        level
      }

      tags {
        id
        tagName
      }

      preferences {
        id
        preferredEmployeeIds
        avoidedEmployeeIds
        notes
      }

      # Metadata
      notes
      metadata

      # Execution data (if available)
      actualStartTime
      actualEndTime
      actualDurationMinutes
      checkInTime
      checkInSource # PHONIRO | NFC | GPS | MANUAL | CAREFOX | ECARE | OTHER
      checkInLatitude
      checkInLongitude
      checkOutTime
      checkOutSource
      deviationMinutes
      deviationReason

      # Template relationship
      visitTemplate {
        id
        frequency # daily | weekly | bi_weekly | monthly | custom
        lifecycleStatus # identified | user_accepted | planned_1st | etc.
        source # user_manual | pattern_detection | bulk_import | api
        patternConfidence
        lastOccurrence
        nextSuggested
      }

      # Timestamps
      createdAt
      updatedAt
    }

    # Employees
    scheduleEmployees {
      id
      employeeId

      employee {
        id
        name
        role
        contractType
        transportMode
        skills {
          skillName
          level
        }
      }

      # Shifts and breaks
      shifts {
        id
        shiftType
        startTime
        endTime
      }

      breaks {
        id
        startTime
        endTime
        breakMinutes
        isPaid
      }
    }
  }
}
```

### 2. Required GraphQL Mutations

**Update Visit Properties:**

```graphql
mutation UpdateVisit($id: ID!, $input: UpdateVisitInput!) {
  updateVisit(id: $id, input: $input) {
    id
    isPinned
    pinnedEmployeeId
    priority
    notes
    # ... other fields
  }
}
```

**Pin/Unpin Visit:**

```graphql
mutation ToggleVisitPin($visitId: ID!, $isPinned: Boolean!, $employeeId: ID) {
  toggleVisitPin(
    visitId: $visitId
    isPinned: $isPinned
    employeeId: $employeeId
  ) {
    id
    isPinned
    pinnedEmployeeId
  }
}
```

**Update Assignment:**

```graphql
mutation UpdateAssignment(
  $visitId: ID!
  $employeeId: ID!
  $startTime: DateTime!
) {
  updateAssignment(
    visitId: $visitId
    employeeId: $employeeId
    startTime: $startTime
  ) {
    id
    visitId
    scheduleEmployeeId
    startTime
    endTime
  }
}
```

### 3. Data Validation Rules

**Backend must enforce:**

- Priority: 1-10 (default 6)
- RequiredStaff: >= 1
- VisitCategory: enum validation (daily | recurring)
- VisitType: enum validation (20 types)
- Time windows: allowedTimeWindowStart <= startTime <= allowedTimeWindowEnd
- Pinned visits: if isPinned=true, must have pinnedEmployeeId

### 4. Enums to Provide

```typescript
enum VisitCategory {
  daily = "daily"
  recurring = "recurring"
}

enum VisitType {
  morning_care = "morning_care"
  mid_morning = "mid_morning"
  lunch_time = "lunch_time"
  afternoon = "afternoon"
  dinner_time = "dinner_time"
  evening = "evening"
  night_supervision = "night_supervision"
  cleaning_two_rooms_kitchen = "cleaning_two_rooms_kitchen"
  cleaning = "cleaning"
  window_cleaning = "window_cleaning"
  laundry = "laundry"
  shopping = "shopping"
  meal_distribution = "meal_distribution"
  walk_outing = "walk_outing"
  escort_companion = "escort_companion"
  social_interaction = "social_interaction"
  bath_shower = "bath_shower"
  self_care = "self_care"
  breakfast = "breakfast"
  lunch = "lunch"
  dinner = "dinner"
}

enum VisitFrequency {
  daily = "daily"
  weekly = "weekly"
  bi_weekly = "bi_weekly"
  monthly = "monthly"
  custom = "custom"
}

enum CheckInSource {
  PHONIRO = "PHONIRO"
  NFC = "NFC"
  GPS = "GPS"
  MANUAL = "MANUAL"
  CAREFOX = "CAREFOX"
  ECARE = "ECARE"
  OTHER = "OTHER"
}

enum MovableVisitLifecycleStatus {
  identified = "identified"
  user_accepted = "user_accepted"
  planned_1st = "planned_1st"
  client_preferences = "client_preferences"
  planned_client_preferences = "planned_client_preferences"
  planned_final = "planned_final"
  exported = "exported"
}

enum MovableVisitSource {
  user_manual = "user_manual"
  pattern_detection = "pattern_detection"
  bulk_import = "bulk_import"
  api = "api"
}
```

---

## Frontend UX Requirements

### 1. Event Visual Styling

#### Base Color = Time Constraint (visitCategory)

**Implementation:**

```typescript
function getBaseColor(visit: Visit): string {
  if (visit.cancelled) {
    return "grey"; // Cancelled/absent
  }

  if (visit.visitCategory === "daily") {
    return "red"; // Fixed to today - must happen
  }

  return "green"; // Flexible - can be rescheduled
}
```

**CSS Classes:**

```css
/* Visit Category Colors */
.visit-mandatory {
  background: #fef2f2; /* Light red background */
  border-left: 4px solid #dc2626; /* Solid red left border */
}

.visit-optional {
  background: #f0fdf4; /* Light green background */
  border-left: 4px dashed #16a34a; /* Dashed green left border */
}

.visit-cancelled {
  background: #f3f4f6 !important; /* Grey background (override others) */
  border-left: 4px solid #9ca3af; /* Grey left border */
  opacity: 0.6;
  text-decoration: line-through;
}

/* Badge Styling */
.extra-badge {
  display: inline-block;
  padding: 2px 4px;
  font-size: 14px;
}

.cancelled-badge {
  display: inline-block;
  padding: 2px 4px;
  font-size: 14px;
}

.priority-badge {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.priority-critical {
  background: #fee2e2;
  color: #dc2626;
}

.priority-low {
  background: #f3f4f6;
  color: #6b7280;
}

.icon-badge {
  display: inline-block;
  padding: 0 2px;
  font-size: 14px;
}
```

#### Priority Badge (Conditional)

**Show badge only when priority ≠ 6 (default):**

```typescript
function getPriorityBadge(priority: number) {
  if (priority <= 3) {
    return {
      icon: "⚠️",
      text: priority.toString(),
      color: "#dc2626",
      tooltip: `Critical priority (${priority}/10)`,
    };
  }

  if (priority >= 8) {
    return {
      icon: "↓",
      text: priority.toString(),
      color: "#6b7280",
      tooltip: `Low priority (${priority}/10)`,
    };
  }

  // No badge for priority 4-7 (normal)
  return null;
}
```

**CSS:**

```css
.priority-badge {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  margin-left: 4px;
}

.priority-critical {
  background: #fee2e2;
  color: #dc2626;
}

.priority-low {
  background: #f3f4f6;
  color: #6b7280;
}
```

#### Additional Icons/Badges

**Always show when applicable:**

```typescript
function getVisitBadges(visit: Visit) {
  const badges = [];

  // 1. Priority badge (if not default)
  const priorityBadge = getPriorityBadge(visit.priority);
  if (priorityBadge) badges.push(priorityBadge);

  // 2. Pinned/locked
  if (visit.isPinned) {
    badges.push({
      icon: "🔒",
      tooltip: "Locked - cannot be moved by optimization or manual editing",
    });
  }

  // 3. Double staffing
  if (visit.requiredStaff > 1) {
    badges.push({
      icon: "👥",
      tooltip: `Double staffing (${visit.requiredStaff} staff required)`,
    });
  }

  // 4. Template link
  if (visit.visitTemplateId) {
    badges.push({
      icon: "↑",
      tooltip: "Recurring visit from template",
    });
  }

  return badges;
}
```

#### Travel Time Buffer

**Show before/after visit:**

```typescript
// Bryntum SchedulerPro config
{
  eventStore: {
    fields: [
      { name: 'preamble', type: 'number' },  // travelTimeBefore in hours
      { name: 'postamble', type: 'number' }  // travelTimeAfter in hours
    ]
  },

  // Map from visit data
  preamble: visit.travelTimeBefore / 60,  // Convert minutes to hours
  postamble: visit.travelTimeAfter / 60
}
```

**Travel buffer styling:**

```css
.b-event-preamble,
.b-event-postamble {
  background: #f3f4f6;
  border: 1px dashed #9ca3af;
  opacity: 0.7;
}

/* Transport mode icon */
.travel-icon-car::before {
  content: "🚗";
}
.travel-icon-bike::before {
  content: "🚴";
}
.travel-icon-walk::before {
  content: "🚶";
}
.travel-icon-transit::before {
  content: "🚌";
}
```

### 2. Event Renderer Implementation

```typescript
// Bryntum SchedulerPro eventRenderer
eventRenderer({ eventRecord, renderData }) {
  const visit = eventRecord.data;

  // 1. Base color from visit category
  if (visit.cancelled) {
    renderData.cls.add('visit-cancelled');
  } else if (visit.visitCategory === 'daily') {
    renderData.cls.add('visit-mandatory');  // Red background
  } else {
    renderData.cls.add('visit-optional');   // Green background
  }

  // 2. Collect all badges
  const badges = getVisitBadges(visit);

  // 3. Build badge HTML
  const badgeHtml = badges
    .map((badge) => {
      if (badge.icon === '⚠️' || badge.icon === '↓') {
        // Priority badge
        const className =
          badge.icon === '⚠️' ? 'priority-critical' : 'priority-low';
        return `<span class="priority-badge ${className}" title="${badge.tooltip}">
          ${badge.icon} ${badge.text}
        </span>`;
      } else if (badge.icon === '✨') {
        // Extra badge (special styling)
        return `<span class="extra-badge" title="${badge.tooltip}">✨</span>`;
      } else if (badge.icon === '❌') {
        // Cancelled badge
        return `<span class="cancelled-badge" title="${badge.tooltip}">❌</span>`;
      } else {
        // Icon badges (lock, double staff, etc.)
        return `<span class="icon-badge" title="${badge.tooltip}">${badge.icon}</span>`;
      }
    })
    .join('');

  // 4. Event content
  const content = `
    <div class="visit-event-content">
      <div class="visit-client">${truncateClientName(visit.client?.name || 'Unknown')}</div>
      <div class="visit-type">${getVisitTypeIcon(visit.type)} ${formatVisitType(visit.type)}</div>
      <div class="visit-time">${formatTime(visit.startTime)}-${formatTime(visit.endTime)} (${visit.durationMinutes} min)</div>
      <div class="visit-badges">${badgeHtml}</div>
    </div>
  `;

  return content;
}

// Helper function to get visit badges
function getVisitBadges(visit: Visit) {
  const badges = [];

  // 1. Extra badge (if added by planner)
  if (visit.isExtra) {
    badges.push({
      icon: '✨',
      tooltip: 'Extra visit (added by planner)',
    });
  }

  // 2. Cancelled badge
  if (visit.cancelled) {
    badges.push({
      icon: '❌',
      tooltip: 'Cancelled',
    });
  }

  // 3. Priority badge (if not default)
  const priorityBadge = getPriorityBadge(visit.priority);
  if (priorityBadge) badges.push(priorityBadge);

  // 4. Pinned/locked
  if (visit.isPinned) {
    badges.push({
      icon: '🔒',
      tooltip: 'Locked - cannot be moved',
    });
  }

  // 5. Double staffing
  if (visit.requiredStaff > 1) {
    badges.push({
      icon: '👥',
      tooltip: `Double staffing (${visit.requiredStaff} staff required)`,
    });
  }

  return badges;
}
```

### 3. Event Tooltip

**Show comprehensive information on hover:**

```typescript
eventTooltip: {
  template: (data) => {
    const visit = data.eventRecord.data;

    return `
      <div class="visit-tooltip">
        <!-- Header -->
        <div class="tooltip-header">
          <h3>${visit.client?.name || "Unknown Client"}</h3>
          <div class="visit-type-label">${formatVisitType(visit.type)}</div>
        </div>

        <!-- Visit Category -->
        <div class="tooltip-section">
          <strong>Visit Category:</strong>
          ${
            visit.visitCategory === "daily"
              ? "🔴 Mandatory (must happen today)"
              : "🟢 Optional (can be rescheduled)"
          }
        </div>

        <!-- Visit Status -->
        ${
          visit.isExtra || visit.cancelled
            ? `
          <div class="tooltip-section">
            <strong>Status:</strong>
            ${visit.isExtra ? "✨ Extra (added by planner)" : ""}
            ${visit.cancelled ? "❌ Cancelled" : ""}
          </div>
        `
            : ""
        }

        <!-- Priority -->
        <div class="tooltip-section">
          <strong>Priority:</strong> ${visit.priority} / 10
          ${visit.priority <= 3 ? " ⚠️ Critical" : ""}
          ${visit.priority >= 8 ? " ↓ Low" : ""}
          ${visit.priority >= 4 && visit.priority <= 7 ? " (Normal)" : ""}
        </div>

        <!-- Assignment Status -->
        <div class="tooltip-section">
          <strong>Assignment Status:</strong>
          ${
            visit.isPinned
              ? "🔒 Locked (cannot be moved)"
              : "Unlocked (can be optimized)"
          }
        </div>

        <!-- Time & Duration -->
        <div class="tooltip-section">
          <strong>Time:</strong> ${formatTime(visit.startTime)} - ${formatTime(visit.endTime)}
          <br>
          <strong>Duration:</strong> ${visit.durationMinutes} minutes
        </div>

        <!-- Time Windows -->
        ${
          visit.allowedTimeWindowStart && visit.allowedTimeWindowEnd
            ? `
          <div class="tooltip-section">
            <strong>Allowed Window:</strong>
            ${formatTime(visit.allowedTimeWindowStart)} - ${formatTime(visit.allowedTimeWindowEnd)}
          </div>
        `
            : ""
        }

        ${
          visit.preferredTimeWindowStart && visit.preferredTimeWindowEnd
            ? `
          <div class="tooltip-section">
            <strong>Preferred Window:</strong>
            ${formatTime(visit.preferredTimeWindowStart)} - ${formatTime(visit.preferredTimeWindowEnd)}
          </div>
        `
            : ""
        }

        <!-- Staffing -->
        ${
          visit.requiredStaff > 1
            ? `
          <div class="tooltip-section">
            👥 <strong>Double staffing:</strong> ${visit.requiredStaff} staff required
          </div>
        `
            : ""
        }

        <!-- Skills -->
        ${
          visit.skills?.length > 0
            ? `
          <div class="tooltip-section">
            <strong>Required Skills:</strong>
            <ul>
              ${visit.skills
                .map(
                  (s) =>
                    `<li>${s.skillName}${s.level ? ` (Level ${s.level})` : ""}</li>`,
                )
                .join("")}
            </ul>
          </div>
        `
            : ""
        }

        <!-- Tags -->
        ${
          visit.tags?.length > 0
            ? `
          <div class="tooltip-section">
            <strong>Tags:</strong> ${visit.tags.map((t) => t.tagName).join(", ")}
          </div>
        `
            : ""
        }

        <!-- Address -->
        ${
          visit.address
            ? `
          <div class="tooltip-section">
            <strong>Address:</strong><br>
            ${visit.address.street}<br>
            ${visit.address.postalCode} ${visit.address.city}
          </div>
        `
            : ""
        }

        <!-- Travel Time -->
        ${
          visit.travelTimeBefore || visit.travelTimeAfter
            ? `
          <div class="tooltip-section">
            <strong>Travel Time:</strong><br>
            Before: ${visit.travelTimeBefore || 0} min<br>
            After: ${visit.travelTimeAfter || 0} min
          </div>
        `
            : ""
        }

        <!-- Notes -->
        ${
          visit.notes
            ? `
          <div class="tooltip-section">
            <strong>Notes:</strong><br>
            ${visit.notes}
          </div>
        `
            : ""
        }

        <!-- Template Info -->
        ${
          visit.visitTemplate
            ? `
          <div class="tooltip-section">
            <strong>Recurring Pattern:</strong><br>
            Frequency: ${visit.visitTemplate.frequency}<br>
            Status: ${visit.visitTemplate.lifecycleStatus}<br>
            Source: ${visit.visitTemplate.source}
          </div>
        `
            : ""
        }

        <!-- Execution Data (if available) -->
        ${
          visit.actualStartTime
            ? `
          <div class="tooltip-section execution-data">
            <strong>Actual Execution:</strong><br>
            Start: ${formatDateTime(visit.actualStartTime)}<br>
            End: ${formatDateTime(visit.actualEndTime)}<br>
            Duration: ${visit.actualDurationMinutes} min
            ${visit.deviationMinutes ? `<br>Deviation: ${visit.deviationMinutes} min` : ""}
            ${visit.checkInSource ? `<br>Check-in: ${visit.checkInSource}` : ""}
          </div>
        `
            : ""
        }
      </div>
    `;
  };
}
```

### 4. Filter System

**Required filters:**

```typescript
interface FilterState {
  // Time Constraint
  showFixed: boolean; // Show daily/fixed visits
  showFlexible: boolean; // Show recurring/flexible visits

  // Priority
  showCritical: boolean; // Show priority 1-3
  showNormal: boolean; // Show priority 4-7
  showLowPriority: boolean; // Show priority 8-10
  priorityMax: number; // Slider: show visits with priority <= value

  // Assignment Status
  showPinned: boolean; // Show locked visits
  showUnpinned: boolean; // Show unlocked visits

  // Visit Status
  showUnassigned: boolean; // visitStatus = 'unassigned'
  showScheduled: boolean; // visitStatus = 'scheduled'
  showCancelled: boolean; // cancelled = true

  // Staffing
  showSingleStaff: boolean; // requiredStaff = 1
  showDoubleStaff: boolean; // requiredStaff > 1

  // Skills (multi-select)
  selectedSkills: string[]; // Filter by required skills

  // Visit Types (multi-select from 20 types)
  selectedTypes: VisitType[];

  // Service Areas (multi-select)
  selectedAreas: string[];

  // Frequency
  selectedFrequencies: VisitFrequency[];
}
```

**Filter UI Component:**

```tsx
<FilterPanel>
  {/* Time Constraint */}
  <FilterGroup label="Time Constraint">
    <Checkbox
      checked={filters.showFixed}
      onChange={toggleFixed}
      label="🔴 Fixed to today (must happen today)"
    />
    <Checkbox
      checked={filters.showFlexible}
      onChange={toggleFlexible}
      label="🟢 Date flexible (can be rescheduled)"
    />
  </FilterGroup>

  {/* Priority */}
  <FilterGroup label="Priority">
    <Checkbox
      checked={filters.showCritical}
      onChange={toggleCritical}
      label="⚠️ Critical (1-3)"
    />
    <Checkbox
      checked={filters.showNormal}
      onChange={toggleNormal}
      label="Normal (4-7)"
    />
    <Checkbox
      checked={filters.showLowPriority}
      onChange={toggleLowPriority}
      label="↓ Low priority (8-10)"
    />

    <Divider />

    <Slider
      label="Show priority ≤"
      min={1}
      max={10}
      value={filters.priorityMax}
      onChange={setPriorityMax}
      marks={{
        1: "Critical",
        6: "Normal",
        10: "Low",
      }}
    />
  </FilterGroup>

  {/* Assignment Status */}
  <FilterGroup label="Assignment Status">
    <Checkbox
      checked={filters.showPinned}
      onChange={togglePinned}
      label="🔒 Locked (pinned)"
    />
    <Checkbox
      checked={filters.showUnpinned}
      onChange={toggleUnpinned}
      label="Unlocked (can be optimized)"
    />
  </FilterGroup>

  {/* Visit Status */}
  <FilterGroup label="Visit Status">
    <Checkbox
      checked={filters.showUnassigned}
      onChange={toggleUnassigned}
      label="Unassigned"
    />
    <Checkbox
      checked={filters.showScheduled}
      onChange={toggleScheduled}
      label="Scheduled"
    />
    <Checkbox
      checked={filters.showCancelled}
      onChange={toggleCancelled}
      label="Cancelled"
    />
  </FilterGroup>

  {/* Staffing */}
  <FilterGroup label="Staffing">
    <Checkbox
      checked={filters.showSingleStaff}
      onChange={toggleSingleStaff}
      label="Single staffing"
    />
    <Checkbox
      checked={filters.showDoubleStaff}
      onChange={toggleDoubleStaff}
      label="👥 Double staffing"
    />
  </FilterGroup>

  {/* Skills */}
  <FilterGroup label="Skills">
    <MultiSelect
      options={SKILL_OPTIONS}
      value={filters.selectedSkills}
      onChange={setSelectedSkills}
      placeholder="Filter by required skills..."
    />
  </FilterGroup>

  {/* Visit Types */}
  <FilterGroup label="Visit Types">
    <MultiSelect
      options={VISIT_TYPE_OPTIONS}
      value={filters.selectedTypes}
      onChange={setSelectedTypes}
      placeholder="Filter by visit type..."
      groupBy="category"
    />
  </FilterGroup>

  {/* Frequency */}
  <FilterGroup label="Frequency">
    <Checkbox label="Daily" />
    <Checkbox label="Weekly" />
    <Checkbox label="Bi-weekly" />
    <Checkbox label="Monthly" />
  </FilterGroup>
</FilterPanel>
```

**Filter implementation:**

```typescript
function filterVisits(visits: Visit[], filters: FilterState): Visit[] {
  return visits.filter((visit) => {
    // Time Constraint
    if (!filters.showFixed && visit.visitCategory === "daily") return false;
    if (!filters.showFlexible && visit.visitCategory === "recurring")
      return false;

    // Priority
    if (visit.priority > filters.priorityMax) return false;
    if (!filters.showCritical && visit.priority <= 3) return false;
    if (!filters.showNormal && visit.priority >= 4 && visit.priority <= 7)
      return false;
    if (!filters.showLowPriority && visit.priority >= 8) return false;

    // Assignment Status
    if (!filters.showPinned && visit.isPinned) return false;
    if (!filters.showUnpinned && !visit.isPinned) return false;

    // Visit Status
    if (!filters.showUnassigned && visit.visitStatus === "unassigned")
      return false;
    if (!filters.showScheduled && visit.visitStatus === "scheduled")
      return false;
    if (!filters.showCancelled && visit.cancelled) return false;

    // Staffing
    if (!filters.showSingleStaff && visit.requiredStaff === 1) return false;
    if (!filters.showDoubleStaff && visit.requiredStaff > 1) return false;

    // Skills
    if (filters.selectedSkills.length > 0) {
      const visitSkills = visit.skills?.map((s) => s.skillName) || [];
      const hasSkill = filters.selectedSkills.some((skill) =>
        visitSkills.includes(skill),
      );
      if (!hasSkill) return false;
    }

    // Visit Types
    if (filters.selectedTypes.length > 0) {
      if (!filters.selectedTypes.includes(visit.type)) return false;
    }

    return true;
  });
}
```

### 5. Context Menu Actions

**Right-click on visit:**

```typescript
eventMenu: {
  items: {
    // Pin/Unpin
    togglePin: {
      text: (data) => data.eventRecord.isPinned ? 'Unlock visit' : 'Lock visit',
      icon: '🔒',
      onItem: ({ eventRecord }) => {
        toggleVisitPin(eventRecord.id, !eventRecord.isPinned);
      }
    },

    // Edit
    edit: {
      text: 'Edit visit details',
      icon: '✏️',
      onItem: ({ eventRecord }) => {
        openEditModal(eventRecord);
      }
    },

    // Unassign
    unassign: {
      text: 'Unassign',
      icon: '↩️',
      disabled: (data) => data.eventRecord.isPinned,
      onItem: ({ eventRecord }) => {
        unassignVisit(eventRecord.id);
      }
    },

    // Split (for double visits)
    split: {
      text: 'Split into separate visits',
      icon: '✂️',
      hidden: (data) => data.eventRecord.requiredStaff <= 1,
      onItem: ({ eventRecord }) => {
        splitVisit(eventRecord.id);
      }
    },

    // Delete
    delete: {
      text: 'Cancel visit',
      icon: '🗑️',
      onItem: ({ eventRecord }) => {
        cancelVisit(eventRecord.id);
      }
    },

    // View details
    viewDetails: {
      text: 'View full details',
      icon: 'ℹ️',
      onItem: ({ eventRecord }) => {
        openDetailsPanel(eventRecord);
      }
    }
  }
}
```

### 6. Drag & Drop Validation

**Validate on drag:**

```typescript
beforeEventDrag: ({ eventRecord, resourceRecord }) => {
  const visit = eventRecord.data;

  // Cannot drag pinned visits
  if (visit.isPinned) {
    return {
      valid: false,
      message: 'This visit is locked and cannot be moved'
    };
  }

  return { valid: true };
},

beforeEventDropFinalize: ({ eventRecord, resourceRecord, startDate }) => {
  const visit = eventRecord.data;
  const employee = resourceRecord.data;

  // Skill validation
  const requiredSkills = visit.skills?.filter(s => s.isRequired) || [];
  const employeeSkills = employee.skills?.map(s => s.skillName) || [];

  const missingSkills = requiredSkills.filter(required =>
    !employeeSkills.includes(required.skillName)
  );

  if (missingSkills.length > 0) {
    return {
      valid: false,
      message: `Employee missing required skills: ${missingSkills.map(s => s.skillName).join(', ')}`
    };
  }

  // Time window validation
  if (visit.allowedTimeWindowStart && visit.allowedTimeWindowEnd) {
    if (startDate < visit.allowedTimeWindowStart || startDate > visit.allowedTimeWindowEnd) {
      return {
        valid: false,
        message: 'Visit cannot be scheduled outside allowed time window'
      };
    }
  }

  // Service area validation (if applicable)
  if (visit.serviceAreaId && employee.serviceAreaId) {
    if (visit.serviceAreaId !== employee.serviceAreaId) {
      return {
        valid: false,
        message: 'Employee is not assigned to this service area'
      };
    }
  }

  return { valid: true };
}
```

### 7. Highlight Valid Drop Targets

**Show valid employees when dragging:**

```typescript
eventDragStart: ({ eventRecord }) => {
  const visit = eventRecord.data;
  const requiredSkills = visit.skills?.filter(s => s.isRequired).map(s => s.skillName) || [];

  // Highlight resources that have all required skills
  scheduler.resourceStore.forEach(resource => {
    const employee = resource.data;
    const employeeSkills = employee.skills?.map(s => s.skillName) || [];

    const hasAllSkills = requiredSkills.every(skill =>
      employeeSkills.includes(skill)
    );

    if (hasAllSkills) {
      resource.cls.add('valid-drop-target');
    } else {
      resource.cls.add('invalid-drop-target');
    }
  });
},

eventDragEnd: () => {
  // Clear highlights
  scheduler.resourceStore.forEach(resource => {
    resource.cls.remove('valid-drop-target', 'invalid-drop-target');
  });
}
```

```css
.valid-drop-target {
  background: #f0fdf4 !important;
  border-left: 3px solid #16a34a !important;
}

.invalid-drop-target {
  background: #fef2f2 !important;
  opacity: 0.5;
}
```

---

## Data Model Reference

### Visit Model (Complete)

```typescript
interface Visit {
  // Identity
  id: string;
  externalId?: string;
  scheduleId: string;
  clientId: string;
  addressId?: string;

  // Client & Address (populated)
  client: {
    id: string;
    name: string;
    externalId?: string;
  };

  address?: {
    id: string;
    street: string;
    postalCode: string;
    city: string;
    latitude: number;
    longitude: number;
  };

  // Timing
  visitDate: Date;
  startTime?: Date;
  endTime?: Date;
  durationMinutes: number;

  // Time Constraints
  allowedTimeWindowStart?: Date;
  allowedTimeWindowEnd?: Date;
  preferredTimeWindowStart?: Date;
  preferredTimeWindowEnd?: Date;

  // Classification
  visitCategory: "daily" | "recurring";
  type?: VisitType;
  recurrenceType?: string;
  visitTemplateId?: string;

  // Scheduling Properties
  visitStatus: "unassigned" | "scheduled";
  priority: number; // 1-10 (1=highest, 6=default, 10=lowest)
  requiredStaff: number; // Default 1
  isPinned: boolean;
  pinnedEmployeeId?: string;

  // Skills, Tags, Preferences
  skills: VisitSkill[];
  tags: VisitTag[];
  preferences?: VisitPreference;

  // Metadata
  notes?: string;
  metadata?: any;

  // Execution (if available)
  actualStartTime?: Date;
  actualEndTime?: Date;
  actualDurationMinutes?: number;
  checkInTime?: Date;
  checkInSource?: CheckInSource;
  checkInLatitude?: number;
  checkInLongitude?: number;
  checkOutTime?: Date;
  checkOutSource?: CheckInSource;
  deviationMinutes?: number;
  deviationReason?: string;

  // Template
  visitTemplate?: VisitTemplate;

  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

interface VisitSkill {
  id: string;
  visitId: string;
  skillName: string;
  isRequired: boolean;
  level?: number;
}

interface VisitTag {
  id: string;
  visitId: string;
  tagName: string;
}

interface VisitPreference {
  id: string;
  visitId: string;
  preferredEmployeeIds: string[];
  avoidedEmployeeIds: string[];
  notes?: string;
}

interface VisitTemplate {
  id: string;
  frequency: VisitFrequency;
  lifecycleStatus: MovableVisitLifecycleStatus;
  source: MovableVisitSource;
  patternConfidence?: number;
  lastOccurrence?: Date;
  nextSuggested?: Date;
}
```

### SolutionAssignment Model

```typescript
interface SolutionAssignment {
  id: string;
  solutionId: string;
  visitId: string;
  scheduleEmployeeId: string;
  eventType: "visit" | "travel" | "break" | "waiting" | "office";
  startTime: Date;
  endTime: Date;
  sequenceNumber: number;
  travelTimeBefore: number; // minutes
  travelTimeAfter: number; // minutes
  waitingTime: number; // minutes
  metadata?: any;
  createdAt: Date;
}
```

### Determining "Extra" Visits

**Question:** How does the frontend know if a visit is "extra" (added by planner)?

**Options for backend implementation:**

#### Option A: Explicit Field (Recommended)

Add a field to the Visit model:

```typescript
interface Visit {
  isExtra: boolean; // True if added by planner after initial optimization
}
```

**Backend sets this when:**

- Visit is created manually by planner (not from template)
- Visit is created during fine-tuning/manual editing
- Visit has tag "planner_added" or "manual_addition"

#### Option B: Compare to Original Schedule

Backend compares current solution to original/baseline:

```typescript
// In solution metadata
interface Solution {
  addedVisitIds: string[]; // Visits not in original schedule
}

// Frontend checks
const isExtra = solution.addedVisitIds.includes(visit.id);
```

#### Option C: Metadata Tag

Use existing tags system:

```typescript
const isExtra = visit.tags?.some((t) => t.tagName === "extra");
```

**Recommendation:** **Option A (explicit field)** is clearest and most performant.

---

### Visit Lifecycle States

**Every visit goes through these states:**

```
1. Created (from template or manual)
   ↓
2. Unassigned (visitStatus = 'unassigned')
   ↓
3. Assigned (visitStatus = 'scheduled')
   ↓
   ├─→ 4a. Executed (actualStartTime set)
   │
   ├─→ 4b. Cancelled (cancelled = true)
   │
   └─→ 4c. Remained assigned (no execution yet)
```

**Additional states:**

- **Extra**: Visit added after initial optimization (isExtra = true)
- **Pinned**: Visit assignment locked (isPinned = true)

---

## Visual Examples

### Example 1: Mandatory Regular Visit with Critical Priority, Pinned

**Data:**

```json
{
  "visitCategory": "daily",
  "isExtra": false,
  "cancelled": false,
  "priority": 1,
  "isPinned": true,
  "requiredStaff": 1,
  "type": "morning_care",
  "client": { "name": "Anna Andersson" }
}
```

**Visual:**

```
┌──────────────────────────────────┐
│ 🔴 Anna A.              ⚠️ 1 🔒 │ ← Red bg (mandatory) + Critical + Locked
│ 🏥 Morning Care                  │
│ 08:00-08:30 (30 min)             │
└──────────────────────────────────┘
```

### Example 2: Mandatory Extra Visit (Added by Planner)

**Data:**

```json
{
  "visitCategory": "daily",
  "isExtra": true,
  "cancelled": false,
  "priority": 6,
  "isPinned": false,
  "requiredStaff": 1,
  "type": "medication",
  "client": { "name": "Anna Andersson" }
}
```

**Visual:**

```
┌──────────────────────────────────┐
│ 🔴 Anna A.                    ✨ │ ← Red bg (mandatory) + Extra badge
│ 🏥 Medication                    │
│ 08:00-08:30 (30 min)             │
└──────────────────────────────────┘
```

### Example 3: Optional Regular Visit with Normal Priority

**Data:**

```json
{
  "visitCategory": "recurring",
  "isExtra": false,
  "cancelled": false,
  "priority": 5,
  "isPinned": false,
  "requiredStaff": 1,
  "type": "cleaning",
  "client": { "name": "Erik Eriksson" }
}
```

**Visual:**

```
┌──────────────────────────────────┐
│ 🟢 Erik E.                       │ ← Green bg (optional), no badges
│ 🧹 Cleaning                      │
│ 10:00-11:30 (90 min)             │
└──────────────────────────────────┘
```

### Example 4: Optional Visit with High Priority, Double Staffing

**Data:**

```json
{
  "visitCategory": "recurring",
  "isExtra": false,
  "cancelled": false,
  "priority": 2,
  "isPinned": false,
  "requiredStaff": 2,
  "type": "walk_outing",
  "client": { "name": "Maria Svensson" }
}
```

**Visual:**

```
┌──────────────────────────────────┐
│ 🟢 Maria S.           ⚠️ 2 👥   │ ← Green bg + Critical + Double staff
│ 🚶 Walk/Outing                   │
│ 14:00-15:00 (60 min)             │
└──────────────────────────────────┘
```

### Example 5: Mandatory Cancelled Visit

**Data:**

```json
{
  "visitCategory": "daily",
  "isExtra": false,
  "cancelled": true,
  "priority": 6,
  "isPinned": false,
  "requiredStaff": 1,
  "type": "lunch",
  "client": { "name": "Johan Nilsson" }
}
```

**Visual:**

```
┌──────────────────────────────────┐
│ ⚫ Johan N.                   ❌ │ ← Grey bg (cancelled) + Cancelled badge
│ 🍽️ Lunch                         │ ← Strikethrough
│ 12:00-12:30 (30 min)             │
└──────────────────────────────────┘
```

### Example 6: Optional Extra Visit, Pinned, Low Priority

**Data:**

```json
{
  "visitCategory": "recurring",
  "isExtra": true,
  "cancelled": false,
  "priority": 9,
  "isPinned": true,
  "requiredStaff": 1,
  "type": "social_interaction",
  "client": { "name": "Karin Larsson" }
}
```

**Visual:**

```
┌──────────────────────────────────┐
│ 🟢 Karin L.          ✨ ↓ 9 🔒 │ ← Green bg + Extra + Low prio + Locked
│ 💬 Social Visit                  │
│ 15:00-16:00 (60 min)             │
└──────────────────────────────────┘
```

### Example 7: Mandatory Visit with Travel Time

**Data:**

```json
{
  "visitCategory": "daily",
  "isExtra": false,
  "cancelled": false,
  "priority": 6,
  "travelTimeBefore": 15,
  "travelTimeAfter": 10,
  "type": "lunch",
  "client": { "name": "Johan Nilsson" }
}
```

**Visual:**

```
┌────┬─────────────────────────┬────┐
│🚗15│ 🔴 Johan N.             │🚗10│ ← Travel buffers
│    │ 🍽️ Lunch                │    │
│    │ 12:00-12:30 (30 min)    │    │
└────┴─────────────────────────┴────┘
```

---

## Implementation Checklist

### Backend

- [ ] GraphQL query returns all visit fields
- [ ] GraphQL query populates client, address, skills, tags, preferences
- [ ] GraphQL query returns solution assignments with travel times
- [ ] Mutation to toggle isPinned
- [ ] Mutation to update priority
- [ ] Mutation to update assignment
- [ ] Enum types exported to frontend
- [ ] Priority validation (1-10, default 6)
- [ ] Time window validation enforced

### Frontend

- [ ] Base color styling (red=fixed, green=flexible, grey=cancelled)
- [ ] Priority badge (only for ≤3 or ≥8)
- [ ] Pinned lock icon
- [ ] Double staffing icon
- [ ] Template link icon
- [ ] Travel time buffers with transport icon
- [ ] Comprehensive tooltip with all data
- [ ] Filter system (9 filter categories)
- [ ] Context menu with actions
- [ ] Drag validation (skills, time windows)
- [ ] Drop target highlighting
- [ ] Event renderer implementation
- [ ] CSS classes for all visual states

---

**End of Document**
