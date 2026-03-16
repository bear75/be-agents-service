# Solution UI Product Requirements

**Product:** Home care scheduling UI — visits, caregivers, coverage, continuity
**Audience:** Product, Backend, Frontend, QA
**Last Updated:** 2026-03-02
**Status:** Ready for Implementation

**Source of truth:** This document is the **single source of truth** for scheduling product and UI (what we build and why). We are building a **home care scheduling product**, not an optimization-engine UI. Use this doc for scope, behaviour, and priorities. For metric formulas: [METRICS_SPECIFICATION.md](METRICS_SPECIFICATION.md). For schedule/solution/scenario architecture: [SCHEDULE_SOLUTION_ARCHITECTURE.md](SCHEDULE_SOLUTION_ARCHITECTURE.md).

---

## Table of Contents

1. [Product Goal](#product-goal)
2. [Jira Index](#jira-index)
3. [Essential UI (80/20)](#essential-ui-8020)
4. [Priority: Data First](#priority-data-first)
5. [Core Principles](#core-principles)
6. [Visit Display Rules (Event Card)](#visit-display-rules-event-card)
7. [Metrics Display](#metrics-display)
8. [Epics](#epics)
9. [Data Responsibilities](#data-responsibilities)
10. [Success Metrics](#success-metrics)

---

## Product Goal

Build a **home care scheduling UI** that allows planners to:

1. See which visits need staff and which are covered
2. Understand utilization and continuity (caregivers per client per 14 days; target < 15)
3. Assign and adjust visits with confidence (drag & drop, pin, unassign)
4. Compare two schedule options (future)
5. Work efficiently at 100+ visits per schedule

The UI must support:

- Multi-day scheduling
- Suggested assignments plus full manual control
- Assignment rules (skills, time windows, preferences) — clear feedback when a move is invalid
- Progressive disclosure (scan → validate → inspect)
- High data density with clarity

---

## Jira Index

**For humans:** The requirements in this PRD should live in the Jira ticket descriptions. Copy the relevant section (e.g. Visit Display Rules, EPIC 1, Metrics Display) into each ticket so the team has one place to look — Jira.

Where this PRD is implemented in Jira (epics and key tasks):

| PRD section / area                                                                 | Jira epic                    | Jira tasks                                                                                                                                                                         |
| ---------------------------------------------------------------------------------- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Core Principles**, **Visit Display Rules**, EPIC 1 (Core Schedule Visualization) | C0-125 Scheduler Core        | C0-130 (FE-CORE-05 filters), C0-133 (FE-CORE-08), C0-317 (FE-CORE-09 tooltip), C0-318 (FE-CORE-10 detail panel), C0-319 (FE-CORE-11 D&D validation), C0-320 (FE-CORE-12 travel UX) |
| **Metrics Display** — Level 1 (schedule-level panel)                               | C0-125                       | C0-138 (FE-METR-01)                                                                                                                                                                |
| **Metrics Display** — Level 2 (per-employee)                                       | C0-125                       | C0-139 (FE-METR-02)                                                                                                                                                                |
| **Metrics Display** — Level 3 (per-visit tooltip/detail)                           | C0-125                       | C0-140 (FE-METR-03)                                                                                                                                                                |
| **Metrics Display** — Comparing two schedules                                      | C0-134 Comparison Mode       | C0-135 (FE-COMP-01), C0-136 (FE-COMP-02)                                                                                                                                           |
| EPIC 2 (Progressive Disclosure), EPIC 3 (Data contract)                            | C0-125                       | C0-317, C0-318; backend C0-276                                                                                                                                                     |
| EPIC 3 — Backend visit/solution support                                            | C0-276 Scheduling 2.0 Master | C0-321 (isExtra, cancelled), C0-322 (togglePin), C0-323 (updatePriority, updateAssignment), C0-324 (visitDetail query)                                                             |
| EPIC 5 (Filters), EPIC 6 (Context menu)                                            | C0-125                       | C0-130 (FE-CORE-05), C0-133 (FE-CORE-08)                                                                                                                                           |
| EPIC 7 (Travel time visualization)                                                 | C0-125                       | C0-320 (FE-CORE-12)                                                                                                                                                                |
| EPIC 8 (Performance & scalability)                                                 | C0-326                       | —                                                                                                                                                                                  |
| EPIC 9 (Accessibility & localization)                                              | C0-325                       | —                                                                                                                                                                                  |
| EPIC 10 (Solution awareness, comparison)                                           | C0-134                       | C0-135, C0-136                                                                                                                                                                     |
| EPIC 11 (AI Chat Module)                                                           | C0-327                       | C0-328–C0-336                                                                                                                                                                      |

**Related:** C0-24 (metrics event-level storage), C0-281 (Revision & Solution Storage) — see [REVISION_AND_STORAGE_STRATEGY.md](REVISION_AND_STORAGE_STRATEGY.md).

### Implementation tickets (PRD-only — single source of truth)

To avoid confusion with Done tasks that had mixed/legacy scope, **implement from these tickets only.** Each contains the full PRD requirements in the description; the "ref" is the previous task for context only.

| Implement this | Ref (context only) | Area                                |
| -------------- | ------------------ | ----------------------------------- |
| **C0-337**     | C0-129             | Visit card                          |
| **C0-338**     | C0-130             | Pin/Unpin + context menu            |
| **C0-339**     | C0-133             | Filter system                       |
| **C0-340**     | C0-317             | Tooltip                             |
| **C0-341**     | C0-318             | Visit detail panel                  |
| **C0-342**     | C0-319             | D&D skill & area validation         |
| **C0-343**     | C0-320             | Travel time UX                      |
| **C0-344**     | C0-138             | Metrics Level 1 (schedule panel)    |
| **C0-345**     | C0-139             | Metrics Level 2 (per-employee)      |
| **C0-346**     | C0-140             | Metrics Level 3 (per-visit tooltip) |

---

## Essential UI (80/20)

The 20% of the UI that delivers most of the value. Get this right first; colors and polish are TBD.

**1. On the visit card (timeline)**

- **Category** — Background: Mandatory (daily) vs Optional (recurring). Cancelled/Absent = same base, greyed out.
- **Text** — Client name, visit type, time + duration.
- **Icons only when needed** — 👥 double staffing, ⚠️ critical priority (1–3), 🔒 pinned. Nothing else on the card.
- Transport icon is **per employee** (resource column), not on visits.

**2. Tooltip (hover)**

- Time window, required skills, preferred/avoided employees, address, assignment status, priority.
- Flex/allowed window (e.g. “Allowed: 08:00–09:00”) or show on hover as shadow/ghost.

**3. Filters**

- Category (Mandatory, Optional), Status (Regular, Extra, Cancelled), Priority (Critical/Normal/Low or slider), Pinned/Unpinned, Unassigned/Scheduled, Single/Double staff, Skills, Visit types (20), Frequency, Service area.
- Fast, combinable, multi-select.

**4. Drag & drop rules**

- Pinned visits: no drag.
- Drop only inside allowed time window and on employees with required skills.
- Clear rejection message when invalid.

**5. Metrics (one place)**  
One metrics panel (sidebar or header): **unassigned count, utilization (%), continuity** (nr of caregivers per 14 days per client; target < 15), **travel time**. Same panel on Schedule View and Compare; optional delta when comparing. Financials after time & % if shown.

**6. Context**

- Lock/Unlock (pin) from context menu; Unassign; Open details.
- Pinned visits restrict some actions.

Everything else (detail panel layout, full filter set, accessibility, export, etc.) builds on this. **Exact colors TBD** — ensure colour-blind safe contrast.

---

## Priority: Data First

**The critical foundation is that all visit information is available.** The backend must provide the full set of visit fields (identity, timing, constraints, status, skills, preferences, address, execution data, etc.) as defined in [Data Responsibilities](#data-responsibilities) and Epic 3. Once that data contract is in place, the UI can display it; **colors, icons, and what appears on the card vs tooltip vs detail panel are UX choices that can be refined later.** Implement and expose all visit data first; then iterate on visual encoding and layout.

---

## Core Principles

### Visual Dimensions

Every visit communicates **two base dimensions plus additional indicators**:

#### Base Dimensions (Always Visible)

1. **Visit Category** — Background color

- 🔴 Mandatory (daily) - Must happen today, narrow time window
- 🟢 Optional (recurring) - Can be rescheduled, flexible time window

2. **Visit Status** — Badge/Overlay

- Regular (no badge)
- ✨ Extra (added by planner)
- ❌ Cancelled
- 👤 Absent (employee absence, separate entity)

#### Additional Indicators (Conditional)

1. **Priority** (1-10, default 6) — On **card**: show ⚠️ only for critical (1-3). Low (8-10) in tooltip/detail only.
2. **Pinned** — 🔒 Lock icon on card if assignment locked.
3. **Other rules on card** — 👥 Double staffing (requiredStaff > 1) only. All others in tooltip/detail:

- 🎯 Required skills (tooltip/detail)
- 📍 Address (tooltip/detail)
- 👤 Preferred employees (tooltip/detail)
- 🏷️ Tags (tooltip/detail)
- **Transport:** Per employee only (resource column/card), never on visit events.

### Information Hierarchy

**Three Interaction Layers:**

1. **Quick Scan** (Timeline View) — Minimal set on card (see Visit Display Rules below)
2. **Quick Validation** (Tooltip, 1-2s hover) — Constraints for decision-making
3. **Detailed Inspection** (Modal/Panel) — Complete information organized

**Visual Budget:**

- Event card: ~80-120px wide; visits can be 5–180 minutes so space is limited
- Show only priority information on the card; no irrelevant icons
- Everything else (skills, addresAs, preferences, tags, low-priority) in tooltip or detail panel

---

### Visit Display Rules (Event Card)

**Note:** These are UX guidelines for how to use the visit data on the timeline. They can be changed (e.g. which icons appear, colors, layout) once all visit info is available. See [Priority: Data First](#priority-data-first).

**Constraint:** Visits can be short (5 min) or long (180 min). Card space is limited. Show only what is essential for scanning; keep icons to a minimum.

#### Always on the card

| What                    | How                                                                                                |
| ----------------------- | -------------------------------------------------------------------------------------------------- |
| **Visit category**      | Background color only: 🔴 Mandatory (daily), 🟢 Optional (recurring). No extra badge for category. |
| **Client + visit type** | Text (truncate if needed).                                                                         |
| **Time + duration**     | e.g. `08:00–08:30 (30 min)`.                                                                       |

#### Icons on card (only when applicable)

| Condition                | Icon | When to show        |
| ------------------------ | ---- | ------------------- |
| Double staffing          | 👥   | `requiredStaff > 1` |
| High priority (critical) | ⚠️   | Priority 1–3 only   |
| Pinned                   | 🔒   | `isPinned === true` |

**Do not put on the card:** Low-priority badge (8–10), skills, address, preferred employees, tags, transport icon. Those belong in tooltip or detail panel only.

#### Cancelled / Absent

- Use **greyed-out** styling.
- Keep the same base (mandatory = red tint, optional = green tint) but muted so they read as inactive.
- No need for extra ❌/👤 on the card if the greyed state is clear.

#### Extra (planner-added)

- Small ✨ badge or subtle style (e.g. border) if space allows.
- If space is very tight, "Extra" can live only in tooltip/detail.

#### Allowed / flex time window

- **Do not** draw the full allowed window on the timeline by default (too noisy).
- **On hover:** Show flex window via one of:
  - **Option A:** Shadow or ghost events, or a transparent band before/after the visit.
  - **Option B:** A **Client & visit** tab/panel with a small calendar showing that visit’s flex window.
- Tooltip can still state e.g. "⏰ Allowed: 08:00–09:00" for quick validation.

#### Transport icon

- **Do not** show transport icon on visit events.
- Transport is **per employee** (e.g. in resource column or employee card). Showing it on every visit would be redundant and clutter the card.

#### Tooltip (hover)

Use for validation; keep it short. Include when relevant: allowed time window, required skills (+ levels), preferred/avoided employees, address, critical notes (first line or 100 chars), assignment status, priority interpretation. **Not in tooltip:** Transport mode (per employee, not per visit).

---

## Metrics Display

The metrics panel shows **home care outcomes**: coverage, utilization, continuity, travel. Formulas and fields are in [METRICS_SPECIFICATION.md](METRICS_SPECIFICATION.md).

### Metrics panel structure (for devs)

Order and types in the panel:

| Type                      | Metrics                                                                              |
| ------------------------- | ------------------------------------------------------------------------------------ |
| **Time**                  | Shift, Visit, Travel, Wait, Idle (durations)                                         |
| **%**                     | **Efficiency** = visit time / (shift − break), as %                                  |
| **Nr and %**              | Assigned & unassigned visits (count and %), visit groups (count and %)               |
| **Nr**                    | Distance (km), **Continuity** (nr of caregivers per client per 14 days; target < 15) |
| **Financials** (if shown) | After the above; e.g. cost, margin                                                   |

**Efficiency** is productive (visit) time as a share of paid time excluding break: **Efficiency (%) = (total visit time) / (total shift time − total break time) × 100.** The value can depend on how shift time is defined (all shifts vs only shifts with visits vs visit-span); see [METRICS_SPECIFICATION.md](METRICS_SPECIFICATION.md).

### Level 1: Schedule-Level Metrics Panel

**Jira:** C0-138 (FE-METR-01). Epic: C0-125.

**Where:** One metrics panel (sidebar or header). Same panel on Schedule View and Compare; optional delta when comparing.

**What to show:**

1. **Home care metrics** in the order above: time (shift, visit, travel, wait, idle), then % (efficiency), then nr and % (assigned/unassigned visits, visit groups), then nr (distance km, continuity).
2. **Financials (if shown):** After time & %; e.g. total cost, margin — see [METRICS_SPECIFICATION.md](METRICS_SPECIFICATION.md).

**Why:** Planners need to see coverage, utilization, and continuity at a glance. This is a home care product; the panel speaks in home care terms only.

### Level 2: Per-Employee Metrics

**Jira:** C0-139 (FE-METR-02). Epic: C0-125.

**Where:** Employee column tooltip or popover, or expandable row detail in the scheduler.

**What to show:**

- Utilization rate, visit count, total work minutes, travel minutes, waiting minutes. Overtime/undertime when applicable.
- Assignment issues attributed to this employee when available (e.g. skill mismatch, overtime).

**Why:** Planners need to see who is over- or under-utilized and who has assignment issues.

### Level 3: Per-Visit/Event (Tooltip and Detail Panel)

**Jira:** C0-140 (FE-METR-03). Epic: C0-125.

**Where:** Event tooltip and detail panel only — **not** on the event card (per [Visit Display Rules](#visit-display-rules-event-card)).

**What to show:**

- Assignment issues for this visit when available (e.g. skill mismatch, time window breach).
- Preferred employee match, continuity for the client, travel time to/from this visit.

**Why:** Planners need to see why an assignment might be problematic when adjusting the schedule.

### Comparing Two Schedules

**Jira:** C0-134 (Comparison Mode), C0-135 (FE-COMP-01), C0-136 (FE-COMP-02).

When comparing two schedules: same metrics panel, with **delta** between the two (e.g. unassigned −2, utilization +3%, continuity improved). How solutions and scenarios are produced is backend/architecture — see [SCHEDULE_SOLUTION_ARCHITECTURE.md](SCHEDULE_SOLUTION_ARCHITECTURE.md).

---

## EPIC 1 — Core Schedule Visualization

**Jira epic:** C0-125 (Scheduler Core)

### Why

Planners must scan 50–100+ visits in seconds and understand:

- What is fixed vs flexible
- What is high risk
- What is locked
- What requires special staffing

### User Stories

**1.1 As a planner**
I want to immediately see whether a visit is mandatory or optional
So that I know what I can reschedule.

**1.2 As a planner**
I want to see critical priority visits without opening anything
So that I can handle risk first.

**1.3 As a planner**
I want locked visits to be unmistakable
So I do not attempt to move something that cannot move.

**1.4 As a planner**
I want double staffing clearly indicated
So I avoid breaking staffing requirements.

**1.5 As a planner**
I want to distinguish planner-added "extra" visits from regular visits
So I can see where manual interventions happened.

### Tasks

**Frontend:**

- Implement base color encoding (mandatory=red, optional=green, cancelled=grey)
- Implement badge logic (extra, cancelled, priority, pinned, double staffing)
- Ensure event card shows: Client name (truncated), visit type icon, time, duration, critical indicators
- Ensure color-blind accessibility (not color-only communication)
- Add dashed border for optional visits, solid for mandatory

**Backend:**

- Provide isExtra flag on Visit model
- Provide cancelled flag on Visit model
- Include both in GraphQL query

**Design:**

- Define icon set for visit types (20 types: medical, cleaning, meals, social, etc.)
- Transport icons (car, bike, walk, transit) are per **employee** (resource column), not on visit events
- On event card: only three icons when applicable — double staffing, critical priority, pinned (see [Visit Display Rules](#visit-display-rules-event-card))
- Ensure colour-blind accessibility (e.g. dashed border optional, solid mandatory)

---

## EPIC 2 — Progressive Disclosure & Validation UX

**Jira epic:** C0-125 (Scheduler Core; tooltip C0-317, detail panel C0-318)

### Why

Planners need three interaction layers:

1. **Scan** — Identify problems quickly
2. **Validate** — Check if assignment is safe
3. **Inspect** — Understand visit and assignment rules deeply

Too much information at once destroys usability.

### User Stories

**2.1 As a planner**
When hovering a visit
I want to see essential rules (time window, skills, address, preferences)
So I can validate assignment quickly.

**2.2 As a planner**
When opening details
I want to see all visit rules grouped logically
So I understand everything affecting it.

**2.3 As a planner**
I want execution history separated from planning data
So I do not confuse plan vs reality.

### Tasks

**Frontend:**

**Tooltip Layer (Validation)** — Must include:

- Visit category (mandatory/optional)
- Visit status (extra/cancelled if applicable)
- Allowed time window
- Required skills with levels
- Preferred/avoided employees
- Address (for travel estimation)
- Critical notes
- Assignment status
- Priority interpretation

**Detail Panel** — Must group into sections:

- Client information
- Visit type & category
- Scheduling constraints (priority, time windows, staffing)
- Skills required
- Employee preferences (preferred/avoided, continuity = caregivers per 14 days per client)
- Assignment details (employee, sequence, travel times)
- Execution history (last 3-5 visits, pagination for older)
- Template metadata (if recurring)

Must support:

- Scrollable layout
- Clear section dividers
- Logical hierarchy
- Progressive loading (don't load execution history until panel opened)

**Backend:**

- Provide separate query for full visit details (lazy load)
- Provide paginated execution history
- Include continuity metrics (nr of caregivers per client per 14 days; target < 15)

---

## EPIC 3 — Backend Data Contract

**Jira epic:** C0-276 (Scheduling 2.0 Master; tasks C0-321–C0-324)

### Why

The UI must not infer scheduling logic.
Backend must provide authoritative data.

### User Stories

**3.1 As a frontend**
I need all visit identity, timing, constraint, and status data
So I can render events correctly.

**3.2 As the system**
Pinned visits must always be validated server-side
So UI cannot create illegal states.

**3.3 As the system**
Priority and enum values must be validated
So scheduling integrity is maintained.

### Data Responsibilities

#### Essential Fields (13) — Backend MUST provide

**For ANY visit to be usable in scheduling:**

- `id`, `clientId`, `clientName` — Identity
- `visitDate`, `startTime`, `endTime`, `durationMinutes` — Time
- `visitCategory` (daily | recurring) — Determines flexibility
- `type` (enum: 20 visit types) — Service category
- `priority` (1-10, default 6) — Importance
- `isPinned` (boolean) — Lock status
- `requiredStaff` (int, default 1) — Staffing level
- `visitStatus` (unassigned | scheduled) — Assignment state

**Total: 13 fields minimum for basic scheduling UI**

#### Important Fields (+8) — Strongly recommended for good UX

**Makes scheduling decisions easier:**

- `allowedTimeWindowStart`, `allowedTimeWindowEnd` — Time window (required)
- `skills` array — Required skills with levels and required flag
- `address` object — Street, city, coordinates
- `preferences` object — Preferred/avoided employee IDs
- `notes` — Critical information

#### Nice to Have — Enhances workflow, not critical

- `isExtra` (boolean) — Added by planner after optimization
- `cancelled` (boolean) — Visit cancelled
- `visitTemplateId`, `recurrenceType`, `visitTemplate` — Template tracking
- `preferredTimeWindowStart`, `preferredTimeWindowEnd` — Soft preferences
- `tags` — Flexible categorization
- `travelTimeBefore`, `travelTimeAfter`, `waitingTime` — Calculated by backend from assignment
- `actualStartTime`, `actualEndTime`, `checkInTime`, `checkInSource`, etc. — Execution tracking
- `metadata`, `externalId` — Integration data

### Tasks

**Backend:**

**Must Implement:**

- Query: Get schedule with solution (includes all visits, assignments, metrics)
- Query: Get full visit details (lazy load, includes execution history)
- Mutation: Toggle pin/unpin
- Mutation: Update priority
- Mutation: Update assignment (visitId, employeeId, startTime)
- Enum validation (VisitType, VisitCategory, CheckInSource, etc.)
- Time window enforcement (allowedTimeWindowStart <= startTime <= allowedTimeWindowEnd)
- Pinned validation (if isPinned=true, must have pinnedEmployeeId)

**Must Provide:**

- All 13 essential fields in main query
- All 8 important fields for tooltip/validation
- Lazy-loaded detail data (execution history, template metadata)

---

## EPIC 4 — Filtering System

**Jira epic:** C0-125 (FE-CORE-08 C0-133)

### Why

Planners must isolate subsets quickly:

- Critical visits
- Unassigned visits
- Skill-specific visits
- Double staffing
- Specific visit types

### User Stories

**4.1 As a planner**
I want to filter by priority
So I can focus on urgent visits.

**4.2 As a planner**
I want to filter by skill
So I can see high-risk assignments.

**4.3 As a planner**
I want to filter by pinned state
So I can see locked decisions.

**4.4 As a planner**
I want to filter by visit type
So I can review specific service categories.

**4.5 As a planner**
I want to filter by extra/cancelled status
So I can review manual changes or cancelled visits.

### Tasks

**Frontend:**

Implement filter panel supporting:

- **Visit Category:** Mandatory, Optional
- **Visit Status:** Regular, Extra, Cancelled
- **Priority:** Critical (1-3), Normal (4-7), Low (8-10), Slider (show priority ≤ N)
- **Assignment Status:** Pinned, Unpinned
- **Visit Status:** Unassigned, Scheduled
- **Staffing:** Single staff, Double staff
- **Skills:** Multi-select from available skills
- **Visit Types:** Multi-select from 20 types (grouped by category)
- **Frequency:** Daily, Weekly, Bi-weekly, Monthly
- **Service Area:** Multi-select (if applicable)

Filtering must:

- Be fast (client-side, no API calls)
- Combine conditions (AND logic)
- Support multi-select
- Show count of filtered results

---

## EPIC 5 — Drag & Drop Validation

**Jira epic:** C0-125 (FE-CORE-11 C0-319; extends C0-270)

### Why

Manual changes must never violate assignment rules (skills, time window, etc.).

### User Stories

**5.1 As a planner**
I cannot drag a pinned visit
So locked decisions are respected.

**5.2 As a planner**
If I drag to an employee without required skills
I want clear feedback
So I avoid illegal assignments.

**5.3 As a planner**
If I drag outside allowed time window
I want immediate rejection
So I stay compliant.

**5.4 As a planner**
When dragging, I want valid drop targets highlighted
So I can see which employees can take this visit.

### Tasks

**Frontend:**

- Block drag for pinned visits
- Validate required skills on drop (employee must have all required skills)
- Validate time windows on drop (startTime must be within allowedTimeWindow)
- Validate service area on drop (if applicable)
- Highlight valid drop targets during drag (green highlight)
- Show invalid drop targets (grey out or red highlight)
- Provide clear rejection messages (toast or inline)

**Backend:**

- No additional work (validation happens client-side with existing data)
- Server-side validation on save (mutation must re-check assignment rules)

---

## EPIC 6 — Context Menu Actions

**Jira epic:** C0-125 (FE-CORE-05 C0-130)

### Why

Planners must act quickly without leaving timeline.

### User Stories

**6.1 As a planner**
I want to lock/unlock from right-click
So I can control optimization behavior.

**6.2 As a planner**
I want to unassign quickly
So I can rebalance manually.

**6.3 As a planner**
I want to open details instantly
So I can inspect visit and assignment rules.

**6.4 As a planner**
I want to cancel a visit
So I can mark it as inactive.

### Tasks

**Frontend:**

Context menu must include:

- Lock / Unlock (toggle isPinned)
- Edit (open detail panel)
- Unassign (remove assignment, set visitStatus=unassigned)
- Cancel visit (set cancelled=true)
- Split (if requiredStaff > 1, create separate visits)
- View details (open full detail panel)

Conditional menu items:

- Unassign disabled if pinned
- Split disabled if single staffing
- Lock shows "Unlock" if already pinned

**Backend:**

- Mutation: togglePin
- Mutation: unassign
- Mutation: cancel
- Mutation: split (if double staffing feature implemented)

---

## EPIC 7 — Travel Time Visualization

**Jira epic:** C0-125 (FE-CORE-12 C0-320)

### Why

Travel time is core efficiency driver in Caire.
It must be visible, not hidden.

### User Stories

**7.1 As a planner**
I want to see travel before and after each visit
So I understand route efficiency.

**7.2 As a planner**
I want travel visually separated from service time
So I can distinguish productive vs non-productive time.

**7.3 As a planner**
I want to see transport mode (car, bike, walk, transit)
So I understand how travel happens.

### Tasks

**Frontend:**

- Display travel buffers before/after visit (preamble/postamble in Bryntum)
- Show transport icon (🚗🚴🚶🚌) on **employee/resource row** only (from employee's transport mode), not on visit events
- Include travel duration in buffer
- Visually distinguish travel from visit (lighter background, dashed border)
- Show travel time in tooltip

**Backend:**

- Provide travelTimeBefore, travelTimeAfter (minutes) in SolutionAssignment
- Provide employee transportMode in ScheduleEmployee
- Calculate travel times (backend from assignment)

---

## EPIC 8 — Performance & Scalability

**Jira epic:** C0-326 (FRONTEND - Performance & Scalability)

### Why

Schedules can contain 100+ visits.
UI must remain responsive.

### User Stories

**8.1 As a planner**
I want smooth scrolling and dragging
So I can operate efficiently.

**8.2 As the system**
I only load detailed data when needed
So performance remains high.

**8.3 As a planner**
I want filters to apply instantly
So I can explore different views quickly.

### Tasks

**Frontend:**

- Load summary visit data initially (13 essential fields)
- Load visit/assignment rules on hover (batch query for visible viewport)
- Load full detail on click (individual query)
- Paginate execution history (show last 3-5, load more on demand)
- Avoid loading full metadata upfront
- Use virtual scrolling for long employee lists
- Use debouncing for filter updates
- Cache tooltip data (don't re-fetch on every hover)

**Backend:**

- Provide separate query for full visit details
- Provide paginated execution history
- Optimize query performance (indexes on visitDate, clientId, scheduleId)

---

## EPIC 9 — Accessibility & Localization

**Jira epic:** C0-325 (FRONTEND - Accessibility & Localization)

### Why

Public care sector requires accessibility compliance.
Multi-language organizations need localized labels.

### User Stories

**9.1 As a screen reader user**
I need meaningful event descriptions
So I understand visit and assignment rules.

**9.2 As a multilingual organization**
I need localized labels
So staff can operate in their language.

**9.3 As a keyboard-only user**
I need to navigate and act without a mouse
So I can use the system efficiently.

### Tasks

**Frontend:**

**Accessibility:**

- Provide ARIA labels describing: Priority, Locked state, Time window, Staffing requirement
- Support keyboard navigation (Tab, Enter, Escape)
- Ensure color contrast meets WCAG AA standards
- Don't rely on color alone (use icons, borders, text)

**Localization:**

- Localize visit types (20 types)
- Localize priority labels (Critical, Normal, Low)
- Localize labels (Mandatory, Optional, Locked, etc.)
- Localize lifecycle states (identified, user_accepted, planned, etc.)
- Support Swedish and English (initial languages)

**Backend:**

- Provide localization keys for visit types
- Provide localization keys for lifecycle states

---

## EPIC 10 — Solution Awareness

**Jira epic:** C0-134 (Comparison Mode; FE-COMP-01 C0-135, FE-COMP-02 C0-136)

(Strategic for Caire positioning)

### Why

This UI must support suggested schedules and comparison of two schedule options.

### User Stories

**10.1 As a planner**
I want to see which visits are unassigned
So I understand coverage and assignment gaps.

**10.2 As a planner**
I want clear distinction between planned, assigned, locked, and cancelled
So the system is transparent.

**10.3 As a planner (future)**
I want to compare two solutions side-by-side
So I can choose the better one.

### Tasks

**Frontend:**

- Show assignment state clearly (unassigned vs scheduled)
- Reflect travel times from assignment (SolutionAssignment)
- Support solution switching (future extension — already in GraphQL schema)
- Support comparison deltas (future extension)

**Backend:**

- Provide solution metrics (travel time, waiting time, utilization, unassigned count, continuity = nr of caregivers per 14 days per client; target < 15)
- Provide multiple solutions per schedule (already supported)
- Include solution ID in queries

---

## EPIC 11 — AI Chat Module

**Jira epic:** C0-327 (FRONTEND - AI Chat Module; tasks C0-328–C0-336). Related: C0-28 (Solution Explanation).

Planners ask natural-language questions about the current schedule and assignments in an AI chat panel; answers are grounded in schedule/solution and metrics data. Full epic, user stories, and task breakdown: Jira epic C0-327 and tasks C0-328–C0-336.

---

## Data Responsibilities

### Backend Must Provide

#### GraphQL Query: GetScheduleWithSolution

**Returns:**

- Schedule (id, startDate, endDate, serviceAreaId)
- Solution (id, status, metrics)
- Visits (all fields per priority list above)
- ScheduleEmployees (with shifts, breaks, skills)
- SolutionAssignments (with travel times, sequence)

#### GraphQL Query: GetVisitDetails (lazy load)

**Returns:**

- Full visit details (all fields)
- Execution history (paginated)
- Template metadata (if recurring)

#### Mutations

- `toggleVisitPin(visitId, isPinned, employeeId)` → Updated visit
- `updateVisit(id, input)` → Updated visit
- `updateAssignment(visitId, employeeId, startTime)` → Updated assignment
- `cancelVisit(visitId)` → Updated visit with cancelled=true

#### Validation

Backend must enforce:

- Priority: 1-10 (default 6)
- RequiredStaff: >= 1
- VisitCategory: enum validation (daily | recurring)
- VisitType: enum validation (20 types)
- Time windows: allowedTimeWindowStart <= startTime <= allowedTimeWindowEnd
- Pinned visits: if isPinned=true, must have pinnedEmployeeId
- Cancelled visits: cannot be assigned (visitStatus must be unassigned)

### Frontend Must Provide

#### Visual Encoding

- Base color = visitCategory (mandatory=red, optional=green)
- Status badge = lifecycle state (extra, cancelled)
- Priority badge = urgency (critical, low)
- Other indicators = rules (pinned, double staffing)

#### Interaction

- Drag & drop with validation
- Context menu actions
- Progressive disclosure (tooltip, detail panel)
- Filtering
- Highlighting valid drop targets

#### Performance

- Lazy loading
- Pagination
- Caching
- Virtual scrolling

---

## Success Metrics

### User Experience

- **Time to understand visit requirements:** < 2 seconds (scan + tooltip)
- **Time to validate assignment:** < 5 seconds (drag + feedback)
- **Time to modify schedule:** < 30 seconds (drag + save)

### Performance

- **Timeline load time:** < 2 seconds for 100 visits
- **Filter response time:** < 100ms
- **Drag & drop response time:** < 50ms
- **Tooltip display time:** < 300ms

### Quality

- **Constraint validation accuracy:** 100% (no illegal assignments saved)
- **WCAG AA compliance:** 100%
- **Mobile responsiveness:** Support tablets (future)

---

## Implementation Phases

### Phase 1 — MVP (Core Visualization)

- EPIC 1: Core Schedule Visualization
- EPIC 3: Backend Data Contract (essential fields only)
- EPIC 7: Travel Time Visualization

**Deliverable:** Planners can view schedules with visits colored by category, see critical indicators, and understand travel times.

### Phase 2 — Interaction (Manual Editing)

- EPIC 2: Progressive Disclosure
- EPIC 5: Drag & Drop Validation
- EPIC 6: Context Menu Actions

**Deliverable:** Planners can validate assignments, drag visits safely, and lock decisions.

### Phase 3 — Optimization (Filters & Performance)

- EPIC 4: Filtering System
- EPIC 8: Performance & Scalability

**Deliverable:** Planners can filter complex schedules and operate efficiently at 100+ visits.

### Phase 4 — Compliance & Polish

- EPIC 9: Accessibility & Localization

**Deliverable:** System meets accessibility standards and supports multilingual teams.

### Phase 5 — Advanced Features

- EPIC 10: Solution Awareness (comparison view)

**Deliverable:** Planners can compare two schedule options and choose the best.

---

## Next Steps

**For Product:**

1. Review and approve epics priority
2. Confirm MVP scope for Attendo pilot

**For Backend:**

1. Implement essential fields (13) in GraphQL query
2. Add isExtra and cancelled flags to Visit model
3. Implement pin/unpin mutation

**For Frontend:**

1. Implement base color encoding (mandatory/optional)
2. Implement badge system (extra, cancelled, priority, pinned)
3. Implement tooltip with essential rules (time window, skills, etc.)

**For Design:**

1. Define icon set for 20 visit types
2. Define badge styling hierarchy
3. Review color-blind accessibility

---

**End of PRD**
