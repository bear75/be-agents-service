# Feature PRD – Bryntum Calendar View

**Version:** 2.1 - Status-Based Visual System + Optimization Scenarios  
**Last Updated:** 2025-12-08

```markdown
> **Note:** This is a product requirements document. For technical implementation
> details, Bryntum example mappings, and integration guides, see: `bryntum-reference.md`
```

## Overview

Features: Feature PRD – Bryntum Calendar View.md (what to build)

The calendar view is the primary workspace for schedulers. It presents a visual timetable of visits and employee shifts over one or more days and allows users to interactively edit, assign and optimise schedules. The view is built with the Bryntum Scheduler/Calendar component to leverage rich drag‑and‑drop functionality, time‑axis navigation and event rendering. It integrates tightly with CAIRE's data model, supporting pinned visits, movable visits, baseline templates and fine‑tune workflows. This PRD defines the functional and UI requirements for the calendar view based on the umbrella PRD, the refactored architecture and data model.

## Visual System (v2.0)

**Design Philosophy:** Colors show **scheduling status**, NOT care type

### Color Coding

Background colors indicate the visit's scheduling status:

- 🔵 **Blue** (Valfritt) = Optional/standard visit
- 🟣 **Purple** (Obligatoriskt) = Mandatory (can't skip)
- 🔴 **Red** (Prioritet/Akut) = High priority or emergency
- 🟢 **Green** (Extra) = Extra visits added by planner
- 🟡 **Yellow** (Inställt) = Cancelled
- ⚪ **Grey** (Frånvaro) = Absent

### Icons (Top-Right Badges)

- 📅**1** = Daily recurring (`visitRecurrence: "daily"` or `null`, `visitCategory: "daily"`)
- 📅**7** = Weekly recurring (`visitRecurrence: "weekly"`, `visitCategory: "recurring"`)
- 📅**14** = Bi-weekly recurring (`visitRecurrence: "bi-weekly"`, `visitCategory: "recurring"`)
- 📅**30** = Monthly recurring (`visitRecurrence: "monthly"`, `visitCategory: "recurring"`)
- 🔒 = Locked/pinned visit
- 👥 = Double staffing required

**Note:** `visitCategory` is derived from `visitRecurrence`:

- `visitCategory: "daily"` = `visitRecurrence` is `null`, `"daily"`, or `"other"` (shows as 📅1)
- `visitCategory: "recurring"` = `visitRecurrence` is `"weekly"`, `"bi-weekly"`, or `"monthly"` (shows as 📅7/14/30)

### Travel & Breaks (Automatic)

- **Travel:** Transparent + dashed border, transport icon (🚗🚴🚶🚌), duration
- **Lunch:** Transparent + dotted frame (12:00-12:30)
- **Not filterable** - Always visible as scheduling constraints

**See:** Visual system documentation in `CairePlatform/bryntum-prototype` repository or `docs_2.0/05-prd/schedule-VISUAL_SYSTEM.md` for complete specification

---

## Optimization Scenarios (NEW - 2025-12-05)

When clicking "Optimera", users select from predefined scenarios that wrap Timefold optimization settings:

### Scenario Presets (Based on SLINGOR PRD)

| Scenario                 | Icon | Use Case                  | Key Settings                                           |
| ------------------------ | ---- | ------------------------- | ------------------------------------------------------ |
| **Daglig Planering** ⭐  | 📅   | Regular stable days       | High continuity (90%), respect pinned (✓), no overtime |
| **Nya Klienter**         | 👤+  | Pre-planning with growth  | High workload balance (90%), allow overtime (30min)    |
| **Störningshantering**   | ⚡   | Sick leave, cancellations | High unused hours recapture (80%), unpin visits        |
| **Kontinuitetsfokus**    | ❤️   | Dementia clients          | Maximum continuity (100%), low travel priority         |
| **Maximal Effektivitet** | 🚀   | Capacity shortage         | Maximum travel reduction (100%), unpin visits          |
| **Anpassad**             | ⚙️   | Experimentation           | Fully customizable from scratch                        |

### Editable Settings

**All scenarios support editing:**

- **5 Weight Sliders** (0-100%): Travel time, Continuity, Workload balance, Overtime, Unused hours recapture
- **4 Constraint Toggles**: Respect pinned visits, Time windows, Skills, Overtime allowance
- **Overtime Input**: Max overtime minutes (0-180 min, 15 min increments)
- **Reset Button**: Restore to defaults
- **Copy From** (custom only): Start from any preset

**Session Persistence:**

- Changes saved in component state for current session
- Modified scenarios show purple "Anpassad" badge
- Start button shows `*` indicator when using modified scenario

---

## Goals & Scope

- Display schedules for a single day or multi‑day horizon with employees/resources listed on the vertical axis and time on the horizontal axis.
- Provide controls to navigate dates (previous/next day, week, month), jump to today and select a custom date range.
- Allow filtering by service area/office and by visit type (mandatory vs. optional, movable vs. fixed, assigned vs. unassigned, priority levels). Filters should persist across sessions and be easily toggled.
- Support drag‑and‑drop assignment of unplanned visits to employees and reordering of visits within an employee's schedule. Validate constraints (skills, service area, contract hours, continuity) during drag operations and provide visual feedback on violations.
- Enable editing of visit start time and duration by dragging/resizing events on the timeline. Respect preferred and allowed windows; disallow moves outside the allowed window unless explicitly overridden.
- Distinguish between pinned (locked) visits/employees and editable ones. In optimised schedules all events are pinned by default; users must unlock a visit or employee before editing or including it in a new optimisation run. Pinned status is stored in the data model and passed to the solver via the patch API.
- Represent different visit states with colours and icons: unassigned (grey outline), assigned (solid colour), priority (red or accent colour), mandatory (lock icon), movable/flexible (striped pattern or icon), missed/cancelled (dashed outline). Weekly/monthly recurring visits should be clearly marked with a recurrence icon. Employee rows should indicate contract type and status (active/inactive) with coloured badges.
- Display tooltips and detail popovers on hover/click, showing client name, visit description/task, continuity status, preferred caregiver, contact caregiver, unused hours, skills required, links to the client and visit detail pages and metrics summary. Allow inline editing of fields where appropriate (e.g. notes, duration).
- Provide a panel or drawer for Unplanned visits and Inactive employees, enabling users to drag visits and employees into and out of the schedule. The panel should list visits grouped by type (mandatory, optional, movable) with search and sort capabilities.
- Offer a Metrics panel summarising KPIs (utilisation, travel time, waiting time, cost, revenue, continuity scores) for the current view. When comparing revisions, display metrics side by side.
- Support viewing and editing schedules across multiple service areas simultaneously, including the ability to drag visits or employees between areas if organisational rules allow.
- Enable comparison of two schedule revisions by overlaying or splitting the calendar to show both sets of events and a differential metrics panel.
- Integrate baseline templates (Slinga) and visit templates: when available, load the baseline as the default view; allow switching to another revision or to an unplanned/movable template. Movable visits should be toggleable on/off to visualise weekly/monthly patterns.
- Adhere to tenant permissions and language settings (Swedish and English) and ensure the UI performs smoothly with large data sets (hundreds of employees and thousands of visits).

## User Roles & Personas

### Scheduler/Operations Manager

Primary user of the calendar. Responsible for planning daily schedules, assigning unplanned visits, adjusting times, running optimisations and reviewing metrics. Needs to see and edit all relevant data, including pinned status and template information.

### Caregiver/Field Staff

View‑only access to their own schedule via a mobile app. They see assignments but cannot modify them. Not covered in this PRD but relevant for data permissions.

### Administrator

Manages configurations, service areas and scenarios. Has the same calendar view as the scheduler but may have additional controls for configurations.

## Functional Requirements

### Layout & Navigation

| Component               | Individual CTA                             | Group/Mode                    | Implementation Time      |
| ----------------------- | ------------------------------------------ | ----------------------------- | ------------------------ |
| **Header bar**          | -                                          | Always visible                | ✅ Done (ScenarioHeader) |
| Organisation selector   | Dropdown: "Organisation"                   | Header                        | 15 min                   |
| Service area selector   | Dropdown: "📍 Serviceområde"               | Header                        | 15 min                   |
| Date navigation         | Buttons: ◀ Idag ▶ + 📅                     | Header/Toolbar                | ✅ Done                  |
| View selector           | Dropdown: "📅 Visa" (Dag/Vecka/Månad)      | Header/Toolbar                | ✅ Done (partial)        |
| Filter toggles          | Buttons: 🔍 Filter, 🔒 Låsta, ⚠️ Prioritet | Toolbar                       | ✅ Done                  |
| Run Optimization        | Button: "▶️ Optimera" → Scenario Modal     | Toolbar → Modal               | ✅ Done                  |
| Scenario selection      | 5 presets + custom with editable settings  | Optimization Modal            | ✅ Done                  |
| Fine-Tune               | Button: "🎯 Finjustera"                    | Toolbar                       | 30 min                   |
| Apply Template          | Button: "📋 Använd mall"                   | Toolbar                       | 1 hour                   |
| Compare                 | Button: "🔀 Jämför" → Comparison Mode      | Mode switch                   | 2-3 hours                |
| Export                  | Button: "💾 Exportera" → Export Modal      | Modal                         | 1-2 hours                |
| **Main schedule area**  | -                                          | 📅 Schema Mode (default)      | ✅ Done                  |
| Timeline with time axis | -                                          | 📅 Schema Mode                | ✅ Done                  |
| Employee rows           | -                                          | 📅 Schema Mode                | ✅ Done                  |
| Virtual scrolling       | Auto (performance)                         | 📅 Schema Mode                | Auto                     |
| Zooming                 | Slider or +/- buttons                      | Toolbar                       | 15 min                   |
| **Side panel (drawer)** | Toggle: "📋 Oplanerade"                    | 📅 Schema Mode                | ✅ Done                  |
| Unplanned visits list   | -                                          | Side panel                    | ✅ Done                  |
| Inactive employees      | Tab in side panel                          | Side panel                    | 30 min                   |
| Movable visits tab      | Tab in side panel                          | Side panel + 📋 Planning Mode | 1 hour                   |
| Baseline templates tab  | Tab in side panel                          | Side panel                    | 30 min                   |
| **Metrics panel**       | Panel: "📊 KPI" (collapsible)              | 📅 Schema + All Modes         | ✅ Done (not visible)    |
| Comparison metrics      | -                                          | 🔀 Comparison Mode            | 30 min                   |
| **Detail dialogs**      | Double-click event                         | Modal                         | ✅ Done                  |
| Edit visit dialog       | -                                          | Modal: "Redigera besök"       | ✅ Done                  |
| Edit employee dialog    | Click employee row                         | Modal: "Redigera medarbetare" | 30 min                   |

### Editing & Drag and Drop

| Feature                        | Individual CTA                   | Group/Mode              | Implementation Time |
| ------------------------------ | -------------------------------- | ----------------------- | ------------------- |
| **Assigning unplanned visits** | Drag from sidebar → employee row | 📅 Schema Mode          | ✅ Done             |
| Skill validation               | Auto (during drag)               | 📅 Schema Mode          | ✅ Done             |
| Visual feedback (highlight)    | Auto (during drag)               | 📅 Schema Mode          | ✅ Done             |
| Constraint validation          | Auto (tooltip on invalid drop)   | 📅 Schema Mode          | 1 hour              |
| **Reassigning visits**         | Drag event → different employee  | 📅 Schema Mode          | ✅ Works (built-in) |
| Pinned warning                 | Auto (dialog on drag pinned)     | 📅 Schema Mode          | 30 min              |
| **Adjusting time**             | Drag event horizontally          | 📅 Schema Mode          | ✅ Works (built-in) |
| **Adjusting duration**         | Drag event edges                 | 📅 Schema Mode          | ✅ Works (built-in) |
| Snap to increments             | Config: `snap: true`             | 📅 Schema Mode          | ✅ Done             |
| Window validation              | Auto (color feedback)            | 📅 Schema Mode          | 1 hour              |
| **Pinning/unpinning**          | Right-click → "Lås/Lås upp"      | Event menu              | ✅ Done             |
| Pin icon display               | Auto (lock icon on event)        | 📅 Schema Mode          | ✅ Done             |
| Pin enforcement                | Auto (prevent drag if pinned)    | 📅 Schema Mode          | 30 min              |
| **Editing details**            | Double-click event               | Modal: "Redigera besök" | ✅ Done             |
| Edit notes/tags                | -                                | Edit modal              | ✅ Done (basic)     |
| Edit duration                  | -                                | Edit modal              | ✅ Done             |
| Set priority                   | -                                | Edit modal              | 20 min              |
| Toggle movable/fixed           | -                                | Edit modal              | 15 min              |
| Toggle recurrence              | -                                | Edit modal              | 20 min              |
| **Drag to unassign**           | Drag event → sidebar             | 📅 Schema Mode          | 1 hour              |

### Status & Styling

| Visual Element                            | Individual CTA               | Group/Mode     | Implementation Time  |
| ----------------------------------------- | ---------------------------- | -------------- | -------------------- |
| **Unassigned visits** (grey outline)      | Auto (data-driven style)     | 📅 Schema Mode | 20 min               |
| **Assigned visits** (solid color by type) | Auto (eventColor field)      | 📅 Schema Mode | ✅ Done              |
| **Flexible/movable** (striped pattern)    | Auto (CSS class)             | 📅 Schema Mode | 15 min               |
| **Priority visits** (accent border)       | Auto (priority field)        | 📅 Schema Mode | ✅ Done (red border) |
| **Mandatory visits** (lock icon)          | Auto (mandatory field)       | 📅 Schema Mode | ✅ Done (lock icon)  |
| **Constraint violations** (warning color) | Auto (validation result)     | 📅 Schema Mode | 30 min               |
| **Employee badges** (contract, status)    | Auto (resourceInfo showMeta) | 📅 Schema Mode | 30 min               |
| **Hover tooltips** (full details)         | Auto (eventTooltip)          | 📅 Schema Mode | ✅ Done              |

### Filters & Toggles

| Filter/Toggle                     | Individual CTA               | Group/Mode   | Implementation Time |
| --------------------------------- | ---------------------------- | ------------ | ------------------- |
| **Mandatory/Optional**            | Toggle: "📌 Obligatoriska"   | Filter Panel | 10 min              |
| **Priority levels**               | Toggle: "⚠️ Prioritet"       | Filter Panel | ✅ Done             |
| **Recurrence (Daily/Weekly/etc)** | Multi-select: "Återkommande" | Filter Panel | ✅ Done             |
| **Staffing (Single/Double)**      | Multi-select: "Bemanning"    | Filter Panel | ✅ Done             |
| **Transport modes**               | Multi-select: "Transport"    | Filter Panel | ✅ Done             |
| **Filter by service area**        | Multi-select: "📍 Område"    | Filter Panel | ✅ Done             |
| **Filter by skill**               | Dropdown: "🎯 Kompetens"     | Filter Panel | 15 min              |
| **Pinned/Locked**                 | Toggle: "🔒 Låsta"           | Filter Panel | ✅ Done             |
| **Show/hide travel breaks**       | Toggle: "🚗 Restid"          | Toolbar      | ✅ Done             |
| **Show/hide waiting time**        | Toggle: "⏱️ Väntetid"        | Toolbar      | 10 min              |

**Note:** Recurrence filters show visits by frequency pattern. `visitCategory` ("daily" vs "recurring") is automatically derived from `visitRecurrence`:

- `visitCategory: "daily"` = `visitRecurrence: "daily"` or `null` (shows 📅1)
- `visitCategory: "recurring"` = `visitRecurrence: "weekly"/"bi-weekly"/"monthly"` (shows 📅7/14/30)

### Optimization & Scenarios

| Feature                       | Individual CTA                         | Group/Mode         | Implementation Time |
| ----------------------------- | -------------------------------------- | ------------------ | ------------------- |
| **Optimization button**       | Button: "▶️ Optimera"                  | Toolbar            | ✅ Done             |
| **Scenario selection modal**  | Modal: "Välj Optimeringsscenario"      | Optimization Modal | ✅ Done             |
| Scenario A - Daglig Planering | Preset with weights/constraints        | Modal              | ✅ Done             |
| Scenario B - Nya Klienter     | Preset for pre-planning                | Modal              | ✅ Done             |
| Scenario C - Störning (Kaos)  | Preset for real-time disruptions       | Modal              | ✅ Done             |
| Kontinuitetsfokus             | Preset for high continuity             | Modal              | ✅ Done             |
| Maximal Effektivitet          | Preset for maximum efficiency          | Modal              | ✅ Done             |
| Anpassad (Custom scenario)    | Fully editable from scratch            | Modal              | ✅ Done             |
| **Editable weights**          | Sliders for 5 weight factors (0-100%)  | Scenario details   | ✅ Done             |
| **Editable constraints**      | Toggle switches for 4 constraint types | Scenario details   | ✅ Done             |
| Overtime limit input          | Number input for max overtime minutes  | Constraint toggle  | ✅ Done             |
| Reset to defaults             | Button: "Återställ"                    | Scenario details   | ✅ Done             |
| Copy from preset              | Dropdown: "Kopiera från..."            | Custom scenario    | ✅ Done             |
| Modified indicator            | Badge showing customized scenarios     | Scenario card      | ✅ Done             |
| **Progress overlay**          | Shows scenario being used during opt   | Full-screen        | ✅ Done             |
| Progress bar                  | Real-time optimization progress        | Progress overlay   | ✅ Done (mock)      |

### Baseline, Templates & Pre‑Planning

| Feature                      | Individual CTA                  | Group/Mode                | Implementation Time |
| ---------------------------- | ------------------------------- | ------------------------- | ------------------- |
| **Baseline as default**      | Auto (data load logic)          | 📅 Schema Mode            | 1 hour              |
| **Apply template**           | Button: "📋 Använd Slinga"      | Toolbar → Preview Modal   | 1-2 hours           |
| Template preview             | -                               | Modal: Shows before/after | (included)          |
| **Movable visits toggle**    | Toggle: "🔄 Visa rörliga besök" | Toolbar                   | 1 hour              |
| Recurrence icon              | Auto (icon on event)            | 📅 Schema Mode            | ✅ Done             |
| Template status badge        | Auto (color-coded badge)        | 📅 Schema Mode            | 15 min              |
| Template tooltip             | Auto (hover)                    | 📅 Schema Mode            | 10 min              |
| **Pre-planning suggestions** | Banner/Toast notification       | 📅 Schema Mode            | 30 min              |
| Accept/reject suggestion     | Buttons in banner               | Banner                    | 15 min              |

### Comparison Mode

| Feature                   | Individual CTA                         | Group/Mode         | Implementation Time |
| ------------------------- | -------------------------------------- | ------------------ | ------------------- |
| **Enter comparison mode** | Button: "🔀 Jämför"                    | 🔀 Comparison Mode | 2-3 hours           |
| **Select revisions**      | Dropdowns: "Revision 1" + "Revision 2" | Comparison toolbar | 30 min              |
| **Split-screen layout**   | Auto (layout change)                   | 🔀 Comparison Mode | (included)          |
| **Overlay with colors**   | Toggle: "Overlay/Split"                | Comparison toolbar | 30 min              |
| **Color legend**          | Auto (panel)                           | 🔀 Comparison Mode | 15 min              |
| **Side-by-side metrics**  | Auto (two metric panels)               | 🔀 Comparison Mode | 30 min              |
| **Delta highlighting**    | Auto (green ↑ / red ↓)                 | Metrics panel      | 20 min              |
| **Exit comparison**       | Button: "Tillbaka till Schema"         | Comparison header  | (included)          |

**Total time for Comparison Mode: 2-3 hours**  
**Result:** One "Jämför" button unlocks entire comparison workflow

## Non‑Functional Requirements

- **Performance**: The calendar must handle schedules with hundreds of employees and thousands of visits without noticeable lag. Lazy loading and virtual scrolling should be used.
- **Responsiveness**: The UI should adapt to different screen sizes, with mobile and tablet layouts where feasible. The scheduler view can be desktop‑only if mobile is reserved for caregivers.
- **Internationalisation**: All labels, tooltips and messages should support Swedish and English. Date and time formats adapt to the user's locale.
- **Accessibility**: Ensure keyboard navigation, screen‑reader support, and colour‑blind‑friendly palettes. Provide text alternatives for icons.
- **Security**: Enforce access controls based on roles and organisations. Do not display data from other tenants. Validate all drag‑and‑drop operations on the server when saving.

## Data Model Considerations

- **Visits & Visit Templates**: Each calendar event is backed by a visit record linked to an underlying `visit_template` (movable visit) when applicable. The view displays fields such as `pinned`, `preferred_window_start`, `allowed_window_end`, `priority_level`, `status`, and `recurrence_pattern`.
- **Pinned Status**: The `pinned` attribute on visits and employees controls editability. After an optimisation run, all visits and employees are pinned by default. Unpinning flags the record for inclusion in the next patch operation.
- **Metrics**: The `schedule_metrics`, `employee_metrics` and `visit_metrics` tables provide data for the metrics panel. Real‑time updates should occur when the user edits assignments or durations.
- **Revisions**: The calendar view should display a single schedule revision at a time but support switching and comparing. Each revision corresponds to a solution record. Users can create new revisions by saving manual edits or triggering an optimisation.
- **Service Areas & Hierarchies**: Employees and visits are associated with `service_area_id`. The calendar must respect organisational constraints (e.g. employees cannot be dragged between non‑neighbouring areas unless allowed). Filters derive from the `service_areas` hierarchy.

## Acceptance Criteria

1. The calendar renders schedules for selected dates and service areas, with employees and visits displayed accurately according to the data model.
2. Users can navigate dates, filter visits and employees, and view baseline or template schedules as the default when available.
3. Drag‑and‑drop assignment and reassignments respect constraints, with clear feedback on violations and success. Pinned events cannot be moved until unlocked.
4. Editing a visit's time or duration updates the corresponding visit record within allowed constraints. Pinned or mandatory visits require explicit confirmation or unlocking.
5. Unplanned visits and inactive employees appear in a side panel and can be dragged into the calendar. Removed visits or employees return to the panel.
6. Movable visits toggle shows and hides recurring events; recurrence icons indicate frequency. Undefined/placeholder templates are flagged.
7. The metrics panel updates in real time when assignments change and displays comparative metrics when two revisions are selected.
8. Comparison mode accurately overlays or splits schedules and highlights differences in both events and metrics.
9. The UI performs smoothly with up to 200 employees and 5 000 visits across multiple days.
10. The design supports Swedish and English localisation and meets accessibility guidelines.

## Wireframe & Mock‑up Guidance

To aid designers, create wireframes covering the following key screens:

### Daily Schedule View

Shows one day with ~20 employees and 100 visits. Include the header bar, filters, side panel for unplanned visits and the metrics panel. Demonstrate assigned vs. unassigned events, movable visit icons, pinned status and drag validation feedback.

### Multi‑Day View

Shows a week view across multiple service areas. Include area selector and demonstrate dragging events between areas (if allowed). Show how movable visits are visualised across days.

### Comparison View

Split or overlay calendar showing baseline vs. optimised schedule. Show legend and metrics comparison. Highlight improved and degraded metrics.

### Visit Detail Dialog

Modal with fields for client name, address (with link to addresses), duration, preferred/allowed windows, priority, recurrence, skills, tags, pinned status and links to client/metrics pages. Include edit controls and save/cancel actions.

### Implementation Notes

When creating mock‑ups, leverage Bryntum Scheduler/Calendar components for authenticity. Annotate interactive elements and specify their connection to the data model (e.g. "this field binds to `visit.preferred_window_start`"). Include notes on colour usage, icons, and responsive behaviour.

## UX Pattern Summary

### Toolbar Organization

**Top Row - Mode Switchers (4 buttons):**

```
[📅 Schema]  [🔀 Jämför]  [🗺️ Karta]  [📊 Planering]
```

**Map Mode Notes:** The Maps + AG Grid example (https://bryntum.com/products/schedulerpro/examples/maps-ag-grid/) demonstrates combining a data grid with map visualization, useful for displaying visit data in tabular format alongside geographic markers in map mode.

Each mode = complete layout change (2-4 hours each)

**Second Row - Quick Toggles (8-12 buttons):**

```
[🔍 Filter]  [🔒 Låsta]  [⚠️ Prioritet]  [🚗 Restid]  [☕ Pauser]  [🔄 Rörliga]
```

Each toggle = filter/show/hide (5-15 min each)

**Third Row - Dropdowns (3-5 selectors):**

```
[📅 Visa: 1 dag ▼]  [📍 Område: Alla ▼]  [👥 Gruppera: Ingen ▼]
```

Each dropdown = select option (10-20 min each)

**Right Side - Actions:**

```
[▶️ Optimera]  [🎯 Finjustera]  [💾 Exportera]  [⚙️ Inställningar]
```

Each action = start workflow (30 min - 2 hours)

### Implementation Strategy

**Single "Restaurant Scheduler" approach:** ❌ DON'T DO THIS

- One button that does everything
- Inflexible, hard to customize
- All-or-nothing

**Granular buttons approach:** ✅ DO THIS

- Many small, focused buttons
- Users pick what they need
- Composable, flexible
- Each button = 5-30 min to add

**Mode grouping approach:** ✅ ALSO DO THIS

- 4 big mode buttons for layout changes
- Many small toggles within each mode
- Best of both worlds

### Time Budget

**Total features in this PRD:** ~45  
**Quick toggles (Category A):** 20 × 10 min = 3-4 hours  
**Mode switches (Category E):** 4 × 3 hours = 12 hours  
**Panels & modals:** 10 × 30 min = 5 hours

**Total: 20-21 hours = 3 days**

**NOT 6-8 weeks!** That was completely wrong.

## Future Enhancements

- **Embedded Analytics Charts**: Integrate mini‑charts (e.g. travel time distribution, utilisation trends) within the calendar view using a charting library. See Bryntum demos for embedded Chart.js examples.
- **AI‑Powered Recommendations**: Surface suggested reassignments or schedule adjustments based on forecasting models, with accept/reject actions from within the calendar.
- **Customisable Views**: Allow users to save and recall personalised layouts (selected filters, date ranges, column widths).
- **Real‑time Collaboration**: Support multiple schedulers editing the same schedule concurrently with conflict resolution and presence indicators.
