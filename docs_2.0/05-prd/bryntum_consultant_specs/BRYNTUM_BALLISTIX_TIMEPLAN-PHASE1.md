# Bryntum Development Timeplan for Ballistix Consultants

**Version:** 1.0  
**Date:** 2025-12-20  
**Purpose:** Specific 3-week Phase 1 timeplan for Bryntum SchedulerPro development  
**Target Audience:** Ballistix Consultants (Professional Bryntum Developers)

---

## Key Dates

| Milestone                  | Date                  |
| -------------------------- | --------------------- |
| Plan Review with Ballistix | Monday, Dec 22, 2025  |
| Phase 1 Start              | Thursday, Jan 1, 2026 |
| Phase 1 Deadline           | Friday, Jan 23, 2026  |
| Phase 2 Start              | Monday, Jan 26, 2026  |

**Phase 1 Duration:** 3 weeks (15 working days)

---

## Phase 1 Scope (Jan 1 - Jan 23)

Phase 1 must support Attendo Pilot Phase 1 requirements from [fas1-scope.md](../pilots/attendo/fas1-scope.md):

- **Grovplanering av slingor** / **Baseline scheduling of loops** (create weekly patterns from movable visits)
- **Sling-minne** / **Loop memory** (built-in continuity via pinned visits)
- **Realtidsändringar** / **Real-time changes** (simulation of schedule modifications)
- **Manuell planering + AI-stöd** / **Manual planning + AI support** (drag-drop with AI analysis)
- **Jämförelse mot manuella scheman** / **Comparison against manual schedules** (AI vs manual side-by-side)
- **KPI metrics display** / **KPI metrics display** (efficiency, supply/demand, financial summaries)

**Note:** Map view for travel time analysis is already implemented in CAIRE (`src/features/scheduling/components/optimizedSchedules/detail/SimpleScheduleMapView.tsx`) and will be integrated, not rebuilt.

--

## Schedule Import: Three States (Attendo Requirement)

The system must support import and comparison of three schedule states:

| Schematyp     | Svenska   | Description                           | Use Case                     |
| ------------- | --------- | ------------------------------------- | ---------------------------- |
| **Unplanned** | Oplanerat | Visits without assigned employee/time | Baseline for optimization    |
| **Planned**   | Planerat  | Manual schedule from eCare            | Comparison against optimized |
| **Actual**    | Utfört    | Actually executed schedule            | Verification and analysis    |

**Data Flow:**

1. Import unplanned → Run optimization → Compare with planned
2. Import actual → Compare with optimized → Identify deviations

> **Note:** All schedules (including actual) are imported via CSV from eCare.

---

## Sling-minne: Built-in Continuity (Attendo Requirement)

**Definition:** En slinga = område + dag + arbetspass (e.g., "Centrum, Måndag, 07-16")

Each slinga contains:

- One EmployeeID (same caregiver for all visits in slinga)
- Ordered list of ObjectID (visit sequence: 1, 2, 3, 4...)

### Sling-minne Levels (Phase 1)

| Level | Name                 | Description                                    | Phase 1 Support |
| ----- | -------------------- | ---------------------------------------------- | --------------- |
| **A** | Daglig kontinuitet   | Same employee per slinga each day              | ✅ Required     |
| **B** | Veckovis kontinuitet | Same slingor repeat same weekdays across month | ✅ Required     |

**Consequence:** Basic continuity is built-in through slingor, avoiding full contact person/preference logic in Phase 1.

---

## Key Design Concept: Unified Pre-Planning UI

A single unified UI serves all planning use cases. The core insight is that **real-time changes are essentially "from scratch optimization with some visits pinned"**.

### The "Tetris" Scheduling Metaphor

Scheduling is like Tetris: **fill the holes with the right color (visit type) and shape (time + employee)**. The daily summary metrics help planners quickly see:

- Where are the gaps? (unassigned shift time = empty space)
- What pieces are missing? (unassigned visits = pieces waiting to drop)
- Is it balanced? (efficiency = how well the board is filled)

```
┌─────────────────────────────────────────────────────────────────┐
│                    UNIFIED PLANNING UI                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Use Case 1: Generate Slingor from Scratch                     │
│  ├── All visits unpinned (movable)                             │
│  ├── AI creates optimal weekly patterns                         │
│  └── User reviews and approves/edits                           │
│                                                                 │
│  Use Case 2: Compare Slingor (AI vs Manual)                    │
│  ├── Side-by-side view                                          │
│  ├── "Why" explanations for AI decisions                       │
│  └── Metrics delta (travel time, efficiency, continuity)       │
│                                                                 │
│  Use Case 3: Real-time Changes                                 │
│  ├── Some visits pinned (🔒 locked)                            │
│  ├── Some visits unpinned (dashed border, available for AI)    │
│  └── Re-optimize around pinned constraints                     │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  VIEW PRESETS:                                                  │
│  [Daily] - Individual visits/events (for single-day editing)   │
│  [Weekly] [Bi-weekly] [Monthly] - Daily summary cells           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 30,000 Foot View: Supply/Demand Balance (All Views)

**Same core metrics visible at ALL zoom levels** - the "Tetris snapshot" stays consistent whether viewing a month, week, or single day. Detail increases as you drill down.

### Core Metrics (Always Visible)

```
┌─────────────────────────────────────────────────────────────────┐
│  SUPPLY/DEMAND BALANCE METRICS                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ⚡ EFFICIENCY: Visit Hours / Shift Hours = X%                  │
│                                                                 │
│  🔴 MANDATORY UNASSIGNED: X visits (Y hours)                    │
│     → Schedule Invalid, User Action Needed                      │
│                                                                 │
│  🟡 OPTIONAL UNASSIGNED: X visits (Y hours)                     │
│     → Probably OK, movable to other days                        │
│                                                                 │
│  🟡 UNASSIGNED SHIFT TIME: X hours (gaps)                       │
│     → Optimization opportunity                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Progressive Disclosure: View Hierarchy

### Monthly View (Highest Level)

**Focus: Strategic overview - supply/demand trends across the month**

```
┌─────────────────────────────────────────────────────────────────┐
│  JANUARY 2026                               [←] [Month ▾] [→]  │
├────────┬────────┬────────┬────────┬────────┬────────┬────────┤
│  Mon   │  Tue   │  Wed   │  Thu   │  Fri   │  Sat   │  Sun   │
├────────┼────────┼────────┼────────┼────────┼────────┼────────┤
│   6    │   7    │   8    │   9    │   10   │   11   │   12   │
│ ⚡ 82% │ ⚡ 78% │ ⚡ 85% │ ⚡ 71% │ ⚡ 80% │        │        │
│ 🟢     │ 🟡 3   │ 🟢     │ 🔴 2   │ 🟢     │        │        │
├────────┼────────┼────────┼────────┼────────┼────────┼────────┤
│   13   │   14   │   15   │   16   │   17   │   18   │   19   │
│ ...    │ ...    │ ...    │ ...    │ ...    │        │        │
└────────┴────────┴────────┴────────┴────────┴────────┴────────┘

📊 MONTHLY TOTALS (drillable)
├── Efficiency avg: 79%
├── Mandatory unassigned: 2 days with issues
├── Total shift gaps: 45h
└── [▼ Financial Summary]
    ├── Revenue: 245,000 kr
    ├── Staff Cost: 198,000 kr
    └── Margin: 47,000 kr (19%)

⚠️ No schedule details shown - only metrics
```

### Weekly / Bi-weekly View (Medium Level)

**Focus: Operational planning - balance across days**

```
┌─────────────────────────────────────────────────────────────────┐
│  WEEK 3 (Jan 13-17, 2026)                  [←] [Week ▾] [→]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐      │
│  │  Mon 13  │  Tue 14  │  Wed 15  │  Thu 16  │  Fri 17  │      │
│  ├──────────┼──────────┼──────────┼──────────┼──────────┤      │
│  │ ⚡ 78%   │ ⚡ 82%   │ ⚡ 85%   │ ⚡ 71%   │ ⚡ 80%   │      │
│  │ 🔴 2     │ 🟢       │ 🟢       │ 🔴 1     │ 🟢       │      │
│  │ 🟡 5/1.5h│ 🟡 2/0.5h│ 🟡 3/1h  │ 🟡 8/2h  │ 🟡 4/1h  │      │
│  │          │          │          │          │          │      │
│  │ [Click→] │ [Click→] │ [Click→] │ [Click→] │ [Click→] │      │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘      │
│                                                                 │
│  📊 WEEK TOTALS (drillable)                                    │
│  ├── Efficiency avg: 79%                                        │
│  ├── Mandatory unassigned: 3 visits (2 days)                   │
│  ├── Optional unassigned: 22 visits                            │
│  ├── Total shift gaps: 6h                                       │
│  │                                                              │
│  └── [▼ Time Breakdown]                                         │
│      ├── 📋 Visits: 156h (79%)                                 │
│      ├── 🚗 Traveling: 18h (9%)                                │
│      ├── ⏳ Waiting: 6h (3%)                                    │
│      └── ☕ Breaks: 18h (9%)                                    │
│                                                                 │
│  └── [▼ Financial Summary]                                      │
│      ├── Revenue: 58,500 kr                                     │
│      ├── Staff Cost: 47,200 kr                                  │
│      └── Margin: 11,300 kr (19%)                               │
│                                                                 │
│  ⚠️ Less schedule details - summary per day                    │
└─────────────────────────────────────────────────────────────────┘
```

### Daily View (Full Detail)

**Focus: Operational execution - all details for slinga, employees, visits**

```
┌─────────────────────────────────────────────────────────────────┐
│  MONDAY JAN 13, 2026                         [←] [Day ▾] [→]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 DAY METRICS (all drillable)                                │
│  ├── ⚡ Efficiency: 78% (156h visits / 200h shifts)            │
│  ├── 🔴 Mandatory unassigned: 2 visits (1.5h)                  │
│  ├── 🟡 Optional unassigned: 5 visits (3.5h)                   │
│  ├── 🟡 Shift gaps: 1.5h waiting time                          │
│  │                                                              │
│  ├── [▼ Time Breakdown]                                         │
│  │   ├── 📋 Visits: 31.2h (78%)                                │
│  │   ├── 🚗 Traveling: 3.6h (9%)                               │
│  │   ├── ⏳ Waiting: 1.5h (4%)                                  │
│  │   └── ☕ Breaks: 3.7h (9%)                                   │
│  │                                                              │
│  └── [▼ Financial Summary]                                      │
│      ├── Revenue: 11,700 kr                                     │
│      ├── Staff Cost: 9,440 kr                                   │
│      └── Margin: 2,260 kr (19%)                                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  🚗 SLINGOR (3 active)                                         │
│  ├── Centrum Morgon (07-12): 4 employees, 18 visits, ⚡ 82%    │
│  ├── Centrum Dag (12-17): 3 employees, 14 visits, ⚡ 75%       │
│  └── Norr Morgon (07-14): 5 employees, 22 visits, ⚡ 79%       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  👥 EMPLOYEES (12 scheduled)                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 07:00  08:00  09:00  10:00  11:00  12:00  13:00  14:00 ... │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │ Anna S  [████ Visit ████][🚗][████ Visit ████][☕][████]   │ │
│  │ Erik L  [████ Visit ████][⏳][████ Visit ████][🚗][████]   │ │
│  │ Maria K [████ Visit ████][████ Visit ████][☕][████ Vis...]│ │
│  │ ...                                                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Legend: 📋 Visit  🚗 Travel  ⏳ Waiting  ☕ Break  🔒 Pinned  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  ⚠️ TETRIS GUIDANCE (Quick Actions)                            │
│  ├── "Fill 1.5h gap on Erik (09:30-11:00) with optional visit" │
│  ├── "Move Tue frequency visits to fill waiting time"          │
│  └── "2 mandatory visits unassigned - action required!"        │
└─────────────────────────────────────────────────────────────────┘

✅ FULL schedule details: slingor, employees, visits, breaks, traveling, waiting
```

---

## Drillable Metrics: Collapsible Sections

All metrics are **clickable/drillable** with collapsible sections:

### Time Breakdown (Collapsible)

```
[▼ Time Breakdown]
├── 📋 Visits:     31.2h  (78%)  ████████████████████░░░░░
├── 🚗 Traveling:   3.6h  ( 9%)  ████░░░░░░░░░░░░░░░░░░░░
├── ⏳ Waiting:     1.5h  ( 4%)  ██░░░░░░░░░░░░░░░░░░░░░░
└── ☕ Breaks:      3.7h  ( 9%)  ████░░░░░░░░░░░░░░░░░░░░
                   ──────────
    Total Shifts:  40.0h (100%)
```

### Financial Summary (Collapsible)

```
[▼ Financial Summary]
├── 💰 Revenue:      11,700 kr
│   └── (Visit hours × avg rate)
├── 💵 Staff Cost:    9,440 kr
│   └── (Shift hours × avg salary)
├── 📊 Margin:        2,260 kr
└── 📈 Margin %:         19%
```

---

## Color-Coding Logic (All Views)

| Indicator        | Condition                                          | Meaning                                 |
| ---------------- | -------------------------------------------------- | --------------------------------------- |
| 🟢 Green border  | Efficiency ≥75% AND no mandatory unassigned        | Schedule valid, well-balanced           |
| 🟡 Yellow border | Efficiency <70% OR optional unassigned OR gaps >1h | Optimization opportunities exist        |
| 🔴 Red border    | ANY mandatory unassigned                           | Schedule invalid - user action required |

---

## Map View Integration (Attendo Requirement - Section 7)

**Status:** Already implemented in CAIRE, requires integration into Bryntum UI.

### Map View Features (Phase 1)

| Feature                    | Description                                   | Priority    |
| -------------------------- | --------------------------------------------- | ----------- |
| **Kartvy per slinga/dag**  | Display visit order with route line on map    | ✅ Required |
| **Travel time comparison** | Manual vs Timefold-estimate vs Actual         | ✅ Required |
| **Deviation marking**      | Flag differences >20% with warning icon       | ✅ Required |
| **Slinga visualization**   | Show all visits in a slinga on map with route | ✅ Required |

### Travel Time Comparison Table

| Metric           | Source Manual | Source Optimized    | Source Actual       |
| ---------------- | ------------- | ------------------- | ------------------- |
| Restid per besök | eCare CSV     | Timefold output     | eCare CSV (actuals) |
| Total restid/dag | Summering     | Timefold KPI        | Faktisk från CSV    |
| Restidsavvikelse | -             | Optimerad - manuell | Utförd - planerad   |

### Deviation Thresholds

```
Travel Time Deviation Indicators:
├── 🟢 Green: <10% difference (accurate estimate)
├── 🟡 Yellow: 10-20% difference (acceptable variance)
└── 🔴 Red: >20% difference (investigate - orealistiskt estimat)
```

**Integration Point:** Map view opens from calendar via:

- Click on slinga row → "Visa på karta" button
- Right-click context menu → "Visa rutt"
- Metrics panel → Travel time KPI → "Analysera restider"

---

### Phase 1 Categories (Mandatory)

| Category  | Description                                                              | Days        | Hours         |
| --------- | ------------------------------------------------------------------------ | ----------- | ------------- |
| 1         | Core Schedule Viewing and Navigation                                     | 1           | 8             |
| 2         | Visit Assignment and Management                                          | 1           | 8             |
| 3         | Visit CRUD Operations                                                    | 1.5         | 12            |
| 3.5       | Employee CRUD Operations                                                 | 1           | 8             |
| 4         | Three-State Schedule Import (Oplanerat/Planerat/Utfört)                  | 0.5         | 4             |
| 5         | Schedule Filtering and Search                                            | 0.5         | 4             |
| 6         | Schedule Comparison (3-state + Slingor + "Why" explanations)             | 1.5         | 12            |
| 7         | Analytics and Metrics Display (Tetris KPIs + collapsible time/financial) | 1.5         | 12            |
| 8         | Optimization Integration (Polling)                                       | 0.5         | 4             |
| 9         | Pre-Planning Core (Unified UI: Slingor + Real-time + Sling-minne A/B)    | 2           | 16            |
| 10        | Map View Integration (Travel time comparison + deviation marking)        | 0.5         | 4             |
| 11        | Manual + AI Analysis (Constraint validation + transparency)              | 1           | 8             |
| 12        | Integration and Infrastructure                                           | 1           | 8             |
| 13        | Testing and Documentation                                                | 1.5         | 12            |
| **Total** |                                                                          | **15 days** | **120 hours** |

**Buffer:** 0 days - Timeline is tight. Prioritize core features if behind schedule.

> **Note:** 15 working days = 3 weeks exactly. All features are required for Attendo Phase 1 support.

---

## Week-by-Week Breakdown

### Week 1 (Jan 1-3, 6-10): Foundation + Core Features

#### Days 1-2: Foundation

- Set up Bryntum SchedulerPro in React + Vite app (CAIRE 2.0 architecture)
- Create GraphQL client setup (Apollo)
- Build core mapper functions (schedule, employee, visit)
- Swedish localization

**Bryntum Examples:**

- [Timeline](https://bryntum.com/products/schedulerpro/examples/timeline/)
- [Columns](https://bryntum.com/products/schedulerpro/examples-scheduler/columns/)
- [Localization](https://bryntum.com/products/schedulerpro/examples/localization/)

#### Days 3-5: Core Schedule View

- Timeline view with employees as resources
- Employee columns (name, role, contract type, transport mode, arbetstid)
- **Daily View Presets** (for single-day scheduling): 1 day with visits/events
- **Planning View Presets** (for pre-planning/slingor): Weekly, Bi-weekly, Monthly
  - Google Calendar style daily summary (not individual visits at this scale)
  - Per-day supply/demand indicators
  - Aggregated metrics per day (total visits, hours, utilization)
- Zoom controls
- Unplanned visits panel (Oplanerade)
- Drag from panel to assign visits

**Bryntum Examples:**

- [Drag Unplanned Tasks](https://bryntum.com/products/schedulerpro/examples/drag-unplanned-tasks/)
- [Skill Matching](https://bryntum.com/products/schedulerpro/examples/skill-matching/)
- [Highlight Event Calendars](https://bryntum.com/products/schedulerpro/examples/highlight-event-calendars/)
- [Time Resolution](https://bryntum.com/products/schedulerpro/examples-scheduler/timeresolution/)
- [Timeline Histogram](https://bryntum.com/products/schedulerpro/examples-scheduler/timelinehistogram/) (for daily summaries)

---

### Week 2 (Jan 13-17): CRUD + Comparison

#### Days 6-7: Visit CRUD

- Double-click to edit visit
- Right-click context menu
- Pin/unpin toggle with lock icon
- Time window constraints
- Status color coding (optional/mandatory/priority/extra/cancelled/absent)

**Bryntum Examples:**

- [Task Editor](https://bryntum.com/products/schedulerpro/examples/taskeditor/)
- [Event Menu](https://bryntum.com/products/schedulerpro/examples-scheduler/eventmenu/)
- [Constraints](https://bryntum.com/products/schedulerpro/examples/constraints/)
- [Event Styles](https://bryntum.com/products/schedulerpro/examples-scheduler/eventstyles/)

#### Days 8-9: Employee CRUD + Filtering

- Add/remove employees from schedule
- Edit shift times and breaks
- Filter by visit status, priority, pinned status
- Filter by employee skills and service area

**Bryntum Examples:**

- [Resource Non-Working Time](https://bryntum.com/products/schedulerpro/examples/resource-non-working-time/)
- [Field Filters](https://bryntum.com/products/schedulerpro/examples-scheduler/fieldfilters/)
- [Grouping](https://bryntum.com/products/schedulerpro/examples/grouping/)

#### Day 10: Comparison Mode

- Compare planned vs optimized schedules
- Split view layout
- Metrics delta display
- Changed visits highlighting

**Bryntum Examples:**

- [Planned vs Actual](https://bryntum.com/products/schedulerpro/examples/planned-vs-actual/)
- [Partners](https://bryntum.com/products/schedulerpro/examples-scheduler/partners/)
- [Split](https://bryntum.com/products/schedulerpro/examples-scheduler/split/)

---

### Week 3 (Jan 20-23): Optimization + Pre-Planning + Polish

#### Days 11-12: Pre-Planning Core (Unified UI for Slingor + Real-time)

**Concept:** Single unified UI serves three use cases:

1. **Generate slingor from scratch** - Create new weekly patterns from movable visits
2. **Compare slingor** - New AI-generated vs manual slingor with "why" explanations
3. **Real-time changes** - Same as from-scratch but with some visits pinned

### Real-time Change Scenarios (Attendo Section 5)

The system must handle these specific scenarios via UI or CSV import:

| Scenario             | Svenska         | UI Action                     | Optimization Impact                 |
| -------------------- | --------------- | ----------------------------- | ----------------------------------- |
| **Sick employee**    | Sjuk anställd   | Remove employee from schedule | Re-assign visits to other employees |
| **Cancelled visit**  | Avbokning       | Delete/cancel visit           | Recalculate gaps and metrics        |
| **New visit**        | Nytt besök      | Add visit to unplanned panel  | Assign to available employee        |
| **Changed time**     | Ändrad starttid | Edit visit time window        | Re-validate constraints             |
| **Changed duration** | Ändrad duration | Resize visit                  | Recalculate travel and gaps         |

### Frequency-Based Move Logic (Attendo Section 5)

When re-optimizing, visits are prioritized for movement based on frequency:

```
Move Priority (last resort → first to move):
1. 🔴 Dagliga besök - Move LAST (most constrained)
2. 🟡 Veckobesök - Can move between days within week
3. 🟢 Månadsbesök - Most flexible, move FIRST
```

**Constraint:** Grovplanerade och opåverkade besök/slingor är låsta (pinned).

### Time Horizon for Real-time Optimization

| Optimization Type     | Time Horizon | Reason                                     |
| --------------------- | ------------ | ------------------------------------------ |
| **Grovplanering**     | Monthly      | Full pattern discovery                     |
| **Real-time changes** | Weekly       | Performance + context for frequency visits |

**Calendar View (Weekly/Bi-weekly/Monthly):**

- Google Calendar style with daily summary cells (not individual visits)
- Per-day metrics: efficiency %, mandatory unassigned, optional unassigned, shift gaps
- Color-coded day borders: green (valid), yellow (opportunities), red (invalid - action needed)
- Click day to drill down to detailed visit view with full metrics panel

**Slinga Information Display:**

- Slinga = area + day + shift (e.g., "Centrum, Måndag, 07-16")
- Summary per slinga: visit count, total hours, travel time, efficiency %
- Comparison view: Manual slinga vs AI slinga side-by-side
- "Why" tooltips explaining AI recommendations

**Pinned/Unpinned Visual States:**

- Pinned visits: solid blue background with 🔒 icon (locked for optimization)
- Unpinned visits: dashed border (available for re-optimization)
- Movable visits panel for unassigned demand

### Manual Planning + AI Support (Attendo Section 6)

**Critical:** Both manual and AI-assisted planning use the SAME schedule view.

#### Manual Mode

- Drag & drop visits in schedule view
- **Only valid moves are allowed** (constraints enforced)
- Immediate visual validation (color, icon, blocking)
- Invalid moves show error tooltip explaining why

#### AI-Stöd Mode

- AI analyzes manual changes **without re-optimizing**
- Shows whether change improves or worsens schedule
- Displays which constraints/goals are affected
- Shows KPI delta (before/after)

```
┌─────────────────────────────────────────────────────────────────┐
│  AI ANALYSIS (after manual move)                                │
├─────────────────────────────────────────────────────────────────┤
│  Move: "Anna S → Erik L, 09:00-10:00"                          │
│                                                                 │
│  Impact:                                                        │
│  ├── ⚡ Efficiency: 78% → 76% 🔻 (-2%)                         │
│  ├── 🚗 Travel time: +12 min                                   │
│  ├── 📋 Continuity: Unchanged                                   │
│  └── ⚠️ Constraint: Time window exceeded by 5 min              │
│                                                                 │
│  Recommendation: ❌ This move worsens the schedule              │
│  Reason: Increases travel time without benefit                  │
│                                                                 │
│  [Undo Move] [Keep Anyway] [Get AI Suggestion]                 │
└─────────────────────────────────────────────────────────────────┘
```

### Configuration Options (Phase 1)

**Note:** Phase 1 does NOT include scenarios. The system will only offer basic configurations like the current manual override system, focusing on time flexibility for breaks and visits.

#### Basic Configuration Overrides

The optimization configuration modal supports:

1. **Time Flexibility for Breaks:**
   - Day shift breaks: start time window, duration, flexibility, paid/unpaid status
   - Evening shift breaks: start time window, duration, flexibility, paid/unpaid status
   - Break flexibility: time window within which breaks can be scheduled

2. **Time Flexibility for Visits:**
   - Visit time flexibility (MÅSTE starta inom): hard constraint window
   - Preferred time windows (BÖR starta inom): soft constraint window (optional)
   - Service duration delta: increase/decrease visit duration
   - Operation type: increase or decrease flexibility

3. **Cost Configuration (Future Enhancement):**
   - Costs per contract type (fixed, hourly)
   - Note: This is documented for future implementation but not required in Phase 1

#### Supply/Demand Balancing

When the system detects unbalanced supply & demand, users can optionally add/edit:

**Priority 1: Employee Shifts (Hourly Employees)**

- Add/remove hourly employees from schedule
- Edit shift times for hourly employees
- Adjust shift duration and breaks

**Priority 2: Visit Management**

- Add/remove/edit visits
- Move visits (if movable)
- Mark visits as movable/unmovable
- **Unused hours pool** - if system supports this (Phase 2 feature)

**Automatic AI Behavior:**

- AI automatically schedules mandatory daily visits first
- Then schedules optional movable visits (or moves dates if needed)
- This prioritization happens automatically during optimization

**Manual Actions in Schedule View:**

- Add/remove employees directly in the schedule view
- Move visits via drag-and-drop
- Edit visit assignments and times
- All manual changes are validated against constraints

#### Transparency Requirements (Attendo Section 8.2)

**"Transparens är A och O – inte bara siffror"**

CAIRE must ALWAYS show:

- **Vad** som ändrats (what changed)
- **Varför** det ändrats (why it changed)
- **Vilka constraints/mål** som påverkats (which constraints affected)

This is critical when:

- Manual schedule shows better KPIs
- But simultaneously breaks rules or goals
- System can verify if manual schedule is invalid
- OR adjust constraints to allow the manual approach

**Bryntum Examples:**

- [Timeline](https://bryntum.com/products/schedulerpro/examples/timeline/)
- [Timeline Histogram](https://bryntum.com/products/schedulerpro/examples-scheduler/timelinehistogram/)
- [Tree Summary Heatmap](https://bryntum.com/products/schedulerpro/examples/tree-summary-heatmap/)
- [Recurrence](https://bryntum.com/products/schedulerpro/examples/recurrence/)
- [Planned vs Actual](https://bryntum.com/products/schedulerpro/examples/planned-vs-actual/)

#### Day 13: Optimization Integration

- Optimization button with basic configuration (manual overrides only)
- Progress bar (polling-based, not WebSocket)
- Display optimized solution when complete
- Error handling

**Note:** Scenarios are NOT required in Phase 1. The system will only offer basic configurations like the current manual override system (time flexibility for breaks and visits).

#### Days 14-15: Integration + Testing

- Connect all mappers to GraphQL API
- Basic metrics panel (efficiency, supply/demand, unassigned count)
- Unit tests for mappers
- Integration testing with Attendo data
- Bug fixes and polish

---

## Phase 2 Scope (Starting Jan 26)

Features deferred from Phase 1:

| Category | Description                                                                     | Priority |
| -------- | ------------------------------------------------------------------------------- | -------- |
| 4        | Cross-Service Area Integration                                                  | P2       |
| 7.5      | Advanced Analytics (Histogram, Utilization)                                     | P2       |
| 7.6      | Advanced Scheduling Features (Dependencies)                                     | P2       |
| 8.5      | WebSocket Real-time Updates                                                     | P2       |
| 9+       | Pre-Planning Advanced (AI recommendations, demand curve, unused hours tracking) | P2       |
| 10       | Export and Reporting (PDF, Excel, iCal)                                         | P2       |

**Phase 2 Aligns with Attendo Phase 2:**

- Skills/kompetens-matching
- Preferenser (klient ↔ vårdgivare)
- Kontaktperson-logik
- Full kontinuitetslogik
- Outnyttjade timmar-pool
- Cross-area optimering
- WebSocket realtidsuppdateringar

---

## Deliverables

### Phase 1 Deliverables (Jan 23, 2026)

1. Bryntum SchedulerPro calendar integrated in CAIRE (React + Vite)
2. Core scheduling features (view, drag-drop, edit, pin/unpin)
3. **Unified Pre-Planning UI** supporting:
   - Generate slingor from scratch (weekly/bi-weekly/monthly time horizons)
   - Compare AI slingor vs manual slingor with "why" explanations
   - Real-time changes (same UI with partial unpinning for re-optimization)
4. **Three-state schedule import** (Attendo requirement):
   - Oplanerat (unplanned) - baseline for optimization
   - Planerat (planned/manual) - comparison against optimized
   - Utfört (actual) - verification and deviation analysis
5. **Sling-minne support** (built-in continuity):
   - Level A: Daily continuity (same employee per slinga)
   - Level B: Weekly continuity (same slingor repeat each week)
6. **Progressive disclosure view hierarchy**:
   - **Monthly**: Metrics only, no schedule details (strategic overview)
   - **Weekly/Bi-weekly**: Summary per day, aggregated metrics (operational planning)
   - **Daily**: Full details - slingor, employees, visits, breaks, traveling, waiting
7. **30,000 foot view metrics** (same at all levels, drillable):
   - Efficiency % (visit hours / shift hours)
   - Mandatory unassigned visits (🔴 RED = schedule invalid)
   - Optional unassigned visits (🟡 YELLOW = movable to other days)
   - Unassigned shift time (🟡 YELLOW = gaps to fill)
8. **Collapsible metric sections**:
   - Time breakdown: visits, traveling, waiting, breaks (hours + %)
   - Financial summary: revenue, staff cost, margin, margin %
9. **Map view integration** (existing CAIRE component):
   - Kartvy per slinga/dag with route visualization
   - Travel time comparison (manual vs optimized vs actual)
   - Deviation marking (>20% flagged with warning)
10. **Manual + AI-assisted planning**:
    - Drag-drop with constraint validation (only valid moves allowed)
    - AI analysis of manual changes (better/worse, why, which constraints)
    - Transparency: what changed, why, which goals affected
11. **Basic configuration overrides** (no scenarios in Phase 1):
    - Time flexibility for breaks (day/evening shift, start, duration, flex, paid/unpaid)
    - Time flexibility for visits (MÅSTE/BÖR time windows, duration delta)
    - Supply/demand balancing: add/remove/edit hourly employee shifts
    - Supply/demand balancing: add/remove/edit/move visits (movable status)
    - Automatic AI prioritization: mandatory daily visits first, then optional movable visits
12. Comparison mode (planned vs optimized, new slinga vs manual slinga)
13. Optimization integration (trigger with basic config, progress, display solution)
14. Swedish localization
15. Unit tests for mappers
16. Documentation

### Phase 2 Deliverables (TBD based on Attendo Phase 2)

1. Advanced pre-planning features
2. Cross-service area support
3. WebSocket real-time updates
4. Export functionality
5. Advanced analytics

---

## Reference Documents

| Document                                                  | Description                                       |
| --------------------------------------------------------- | ------------------------------------------------- |
| [Attendo Phase 1 Scope](../pilots/attendo/fas1-scope.md)  | ⭐ **PRIMARY** - Attendo pilot requirements       |
| [Bryntum From Scratch PRD](./BRYNTUM_FROM_SCRATCH_PRD.md) | ⭐ **PRIMARY** - Full feature PRD with all phases |
| [Bryntum Backend Spec](./BRYNTUM_BACKEND_SPEC.md)         | GraphQL API specifications                        |
| [Bryntum Reference](./bryntum-reference.md)               | Bryntum examples catalogue                        |
| [Bryntum Timeplan (Full)](./bryntum_timeplan.md)          | Complete timeplan with all categories             |
| [Attendo Timeplan](../pilots/attendo/TIMEPLAN.md)         | Overall pilot timeline                            |

**Existing CAIRE Components (Already Implemented):**

- Map View: `src/features/scheduling/components/optimizedSchedules/detail/SimpleScheduleMapView.tsx`

---

## Attendo Fas 1 Alignment Checklist

This timeplan is aligned with [Attendo Fas 1 Scope](../pilots/attendo/fas1-scope.md). Key requirements coverage:

| Attendo Section | Requirement                                       | Bryntum Phase 1 Coverage     |
| --------------- | ------------------------------------------------- | ---------------------------- |
| **Section 1.1** | Obligatorisk data (besök, anställd, geografi)     | ✅ Data model in GraphQL API |
| **Section 1.3** | Three schedule states (oplanerat/planerat/utfört) | ✅ Category 4 + 6            |
| **Section 1.4** | Transport mode (bil only)                         | ✅ Default in Timefold       |
| **Section 2**   | Sling-minne (Level A + B)                         | ✅ Category 9                |
| **Section 4**   | Grovplanering (baseline scheduling)               | ✅ Pre-Planning Core         |
| **Section 5**   | Realtidsändringar (simulation)                    | ✅ Real-time scenarios       |
| **Section 5**   | Frequency-based move logic                        | ✅ Category 9                |
| **Section 6**   | Manuell planering + AI-stöd                       | ✅ Category 11               |
| **Section 7**   | Restidsanalys med kartvy                          | ✅ Category 10               |
| **Section 7.2** | Deviation marking (>20%)                          | ✅ Category 10               |
| **Section 8.1** | KPI-jämförelse                                    | ✅ Category 7                |
| **Section 8.2** | Transparens & förklarbarhet                       | ✅ Category 11               |

### Explicitly Out of Scope (Fas 1)

Per Attendo Fas 1 Scope Section 1.1 "Medvetet utanför scope":

| Feature               | Status     | Notes                           |
| --------------------- | ---------- | ------------------------------- |
| Skills/kompetenser    | ❌ Phase 2 | No skill matching in Fas 1      |
| Preferenser           | ❌ Phase 2 | No client/caregiver preferences |
| Kontinuitet (full)    | ❌ Phase 2 | Basic via sling-minne only      |
| Outnyttjade timmar    | ❌ Phase 2 | Unused hours pool               |
| Kontaktpersoner       | ❌ Phase 2 | Contact person logic            |
| Cross-area optimering | ❌ Phase 2 | Single area per schedule        |
| WebSocket real-time   | ❌ Phase 2 | Polling in Phase 1              |

---

## Dependencies from CAIRE Team

Ballistix requires from CAIRE:

| Dependency                    | Required By | Status  |
| ----------------------------- | ----------- | ------- |
| GraphQL API Ready             | Jan 6, 2026 | Pending |
| Test Data (Attendo pilot)     | Jan 6, 2026 | Pending |
| Map Integration Access        | Jan 1, 2026 | Ready   |
| Authentication (Clerk tokens) | Jan 1, 2026 | Ready   |
| Design Specs                  | Jan 1, 2026 | Ready   |

---

## Risk Mitigation

| Risk                     | Impact | Mitigation                                  |
| ------------------------ | ------ | ------------------------------------------- |
| GraphQL API delays       | High   | Use mock JSON data for initial development  |
| Complex data mapping     | Medium | Start with mapper functions early (Day 1-2) |
| Attendo data issues      | Medium | Parallel testing with demo data             |
| Optimization integration | Low    | Use polling fallback (WebSocket in Phase 2) |

---

## Success Criteria for Phase 1

### Core Calendar

- [ ] Calendar loads schedule data from GraphQL in less than 2 seconds
- [ ] Drag-and-drop assignment works and saves to database
- [ ] Pin/unpin visits with visual feedback (🔒 icon, solid vs dashed border)
- [ ] Swedish localization complete

### Three-State Schedule Import (Attendo Requirement)

- [ ] Import oplanerat (unplanned) schedule as optimization baseline
- [ ] Import planerat (planned/manual) schedule for comparison
- [ ] Import utfört (actual) schedule for deviation analysis
- [ ] Compare all three states with clear visual diff

### Sling-minne (Built-in Continuity)

- [ ] Slinga = område + dag + arbetspass concept implemented
- [ ] Level A: Daily continuity (same employee per slinga)
- [ ] Level B: Weekly continuity (same slingor repeat each week)
- [ ] Slingor visualized as grouped rows or tabs in daily view

### Progressive Disclosure View Hierarchy

- [ ] Monthly view: Metrics only, no schedule details
- [ ] Weekly/Bi-weekly view: Summary per day, aggregated metrics
- [ ] Daily view: Full details (slingor, employees, visits, breaks, traveling, waiting)

### 30,000 Foot View Metrics (Same at All Zoom Levels)

- [ ] Efficiency (visit hours / shift hours) as percentage
- [ ] Mandatory unassigned visits (🔴 RED if > 0 = schedule invalid)
- [ ] Optional unassigned visits (🟡 YELLOW = ok, movable to other days)
- [ ] Unassigned shift time/gaps (🟡 YELLOW = optimization opportunity)

### Drillable/Collapsible Metric Sections

- [ ] Time breakdown: visits, traveling, waiting, breaks (hours + %)
- [ ] Financial summary: revenue, staff cost, margin, margin %
- [ ] Color-coded day borders: 🟢 green (valid), 🟡 yellow (opportunities), 🔴 red (invalid)

### Map View Integration (Attendo Section 7)

- [ ] Map view per slinga/dag showing visit order with route line
- [ ] Travel time comparison: manual vs optimized vs actual
- [ ] Deviation marking: >20% difference flagged with 🔴 warning
- [ ] Opens from calendar via click/context menu

### Manual + AI-Assisted Planning (Attendo Section 6)

- [ ] Drag-drop with constraint validation (only valid moves allowed)
- [ ] Invalid moves show error tooltip explaining why
- [ ] AI analysis: shows if change improves/worsens schedule
- [ ] AI analysis: shows which constraints/goals affected
- [ ] Transparency: what changed, why, KPI delta

### Real-time Change Scenarios

- [ ] Handle sjuk anställd (sick employee) - remove and re-assign
- [ ] Handle avbokning (cancelled visit) - delete and recalculate
- [ ] Handle nytt besök (new visit) - add and assign
- [ ] Handle ändrad starttid/duration - edit and re-validate
- [ ] Frequency-based move priority (daily last, monthly first)

### Comparison Mode

- [ ] Planned vs optimized with delta metrics
- [ ] AI slinga vs manual slinga with "why" explanations
- [ ] Highlight differences (added/removed/moved visits)

### Basic Configuration Overrides

- [ ] Time flexibility for breaks (day/evening shift, start, duration, flex, paid/unpaid)
- [ ] Time flexibility for visits (MÅSTE/BÖR time windows, duration delta)
- [ ] Supply/demand balancing: add/remove/edit hourly employee shifts in schedule view
- [ ] Supply/demand balancing: add/remove/edit/move visits (movable status) in schedule view
- [ ] Automatic AI prioritization: mandatory daily visits scheduled first, then optional movable visits
- [ ] No scenarios in Phase 1 - only basic manual override configurations

### Optimization Integration

- [ ] Triggers Timefold job with basic configuration (no scenarios)
- [ ] Displays progress and optimized solution when complete
- [ ] Ready to support Attendo Phase 1 testing (Jan 30, 2026)

---

## Contact

**CAIRE Team:** Questions about API, data model, or integration  
**Ballistix:** Bryntum implementation questions

---

**Document Status:** Ready for Review  
**Last Updated:** 2025-12-20  
**Version:** 1.2

---

## Changelog

| Version | Date       | Changes                                                                                                                                                                                                                                                            |
| ------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1.0     | 2025-12-20 | Initial timeplan with core features                                                                                                                                                                                                                                |
| 1.1     | 2025-12-20 | Enhanced with Attendo Fas 1 alignment: 3-state import, sling-minne levels, map view integration, real-time scenarios, manual+AI support, transparency requirements                                                                                                 |
| 1.2     | 2025-12-20 | Removed scenarios requirement from Phase 1. Added basic configuration options: time flexibility for breaks/visits, supply/demand balancing (employee shifts, visit management), automatic AI prioritization. Documented cost configuration for future enhancement. |
