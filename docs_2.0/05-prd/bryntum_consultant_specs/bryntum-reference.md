# Bryntum References for Caire Scheduling UI

> **Note:** This is a technical implementation guide. For product requirements,
> user stories, and acceptance criteria, see: [CAIRE_SCHEDULING_PRD](../CAIRE_SCHEDULING_PRD.md), [CAIRE_PLANNING_PRD](../CAIRE_PLANNING_PRD.md), and [JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES](../JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES.md).

## Overview

Implementation: bryntum-reference.md (how to build with Bryntum)

This document collects and interprets a wide range of Bryntum SchedulerPro examples to demonstrate how each can be leveraged to implement Caire's scheduling UI. It is intended as a practical guide for developers, describing which examples map to specific features in our product and how to combine them. By following these recommendations a developer can build the complete front‑end without guessing which Bryntum capabilities to employ. Once the UI layer is in place, the remaining task is to connect the data model via API and mapper functions.

## Mapping Examples to Caire Features

To build our scheduling UI, we will combine and customise many of the above examples. The table below groups the examples by functional area and describes how they address our requirements. Developers should start from these examples and adapt them to fit Caire's data structures, permissions and styling.

### 1. Main Calendar & Basic Editing

- **Base Layout & Timeline** – Use the Timeline example as the foundation for the main schedule area. It provides a robust timeline view with drag‑and‑drop and editing. Combine with Row Height and Columns examples to control row size and add employee metadata columns (contract type, visits count, service time, efficiency).

- **Drag & Drop Unplanned Tasks** – Integrate patterns from Drag From Grid/Unplanned Tasks to implement the unplanned visits panel. Unassigned visits appear in a list; dragging them onto an employee row assigns them. Use Highlight Event Calendars/Resources to show valid drop targets based on skills and service area.

- **Editing & Constraints** – Adopt Task Editor or Docked Editor for editing visit details. Use the Constraints example to enforce start/end windows when resizing or moving events. For double visits and overlapping shifts, adapt Nested Events and Nested Events Configuration.

- **Pinned Visits & Event Menu** – Use the Event Menu example to implement right‑click actions such as pin/unpin, split, duplicate and delete. Pinned events should be visually distinct (e.g. lock icon) and protected from drag actions until unlocked.

- **Undo/Redo & State** – Integrate Undo/Redo and State examples to allow users to revert changes and persist settings. This safeguards against accidental edits and supports multi‑step workflows.

- **Recurring & Movable Visits** – Leverage Recurrence and Recurring Time Ranges to represent weekly/monthly visits. Combined with Resource Non‑Working Time for shift patterns, this supports pre‑planning and template editing.

### 2. Pre‑Planning & Demand/Supply Analysis

- **Capacity & Embedded Charts** – Use the Embedded Chart and Resource Histogram/Utilisation examples to display demand vs. supply curves underneath the scheduler during pre‑planning. These charts can show how many visits per time slot are required and available.

- **Recurrence & Pattern Detection** – The Recurrence example demonstrates repeated events; combine it with Timeline Histogram to detect and visualise recurring patterns. This informs movable visit suggestions and pre‑planning adjustments.

- **Maps & Travel Time** – Integrate the Maps and Maps + AG Grid examples to visualise visit locations and travel durations. The Maps + AG Grid example shows how to combine a data grid with map visualization for displaying visit data alongside geographic markers. This enhances the scheduler with geographic context during route planning.

- **Resource Heatmap & Tree Summary** – Use Tree Summary Heatmap and Resource Histogram to evaluate service area utilisation and decide when to move visits between areas or adjust staffing.

### 3. Fine‑Tuning, Optimisation & Comparison

- **Planned vs Actual** – Adapt this example for comparing baseline vs. optimised schedules or two revisions (e.g. fine‑tuned vs. previous). Use the Partners and Split examples to create dual timelines or overlay views. The Comparison View from the UI specification in the BRYNTUM‑PRD archive should align with these patterns.

- **WebSockets** – Incorporate WebSockets for real‑time schedule updates during long optimisation runs. Display progress and update events as soon as new solutions are available.

- **Lock Rows & Multi Assign** – Use Lock Rows to pin baseline schedules or specific rows (e.g. service areas). Use Multi Assign examples to support double visits and complex assignments in fine‑tune mode.

- **Charts & Sparklines** – Show metrics trends for different revisions using Sparklines, Scheduler Chart and Embedded Chart. This helps users evaluate the effects of each optimisation.

### 4. Multi‑Service Areas & Groups

- **Grouping & Group Summary** – Group employees by service area or contract type and show summary metrics per group. Use Tree Summary to collapse or expand groups and present aggregated data.

- **Drag Between Schedulers** – To transfer visits or employees between service areas, instantiate multiple SchedulerPro instances side by side and enable dragging between them using this example. Combine with Multi Groups for employees assigned to multiple service areas.

- **Resource Non‑Working Time & Calendar Editor** – Represent different shift types (day, evening, night) per area and allow editing via the calendar editor pattern. This ensures that when dragging a visit across areas, the recipient's availability is clear.

### 5. Filtering, Layers & Visual Styling

- **Field Filters & Layers** – Use Field Filters and Layers examples to implement our visit type filters (mandatory, optional, movable, priority). Layers allow toggling entire categories of events on/off and overlaying additional information.

- **Event Styles & Custom Layouts** – Apply Event Styles to differentiate statuses (assigned, unassigned, priority, movable, cancelled). Use Custom Layouts to manage overlapping events gracefully in dense schedules.

- **Highlight Time Spans & Non‑Working Time** – Shade preferred and allowed windows differently to guide drag‑and‑drop actions. Use Working Time to visualise non‑working hours per employee.

- **Localization** – Ensure the scheduler uses Bryntum's localisation API to provide Swedish and English labels. Combine with the Localization example to check available translations.

### 6. Exporting & Reporting

- **Export & Print** – Use the export examples to provide options for printing schedules or exporting them to PDF, PNG, Excel or iCalendar. Add an "Export" action in the header bar that calls these APIs.
  - **Excel:** Full schedule data export (employees, shifts, visits, clients, time windows, assignments, etc.) for analysis and backup.
  - **PDF:** Summary and metrics-focused report (schedule name/date, utilization, continuity, cost/revenue, concise summary); not full data.

- **Booking & Multi Summary** – Adapt Booking and Multi Summary examples to display calculated revenues, costs and other financial metrics per date or resource. These can feed into reports sent to clients or municipalities.

### 7. Advanced Interactions

- **Task Editor with TinyMCE** – For rich text descriptions of visits (e.g. care instructions), integrate the TinyMCE editor. This improves readability of long notes.

- **Highlight Event/Resource Calendars** – Provide visual guidance when dragging visits by highlighting valid caregiver rows or time slots. This reduces trial and error for schedulers.

- **Row Locking & Nested Events** – Use row locking for unassigned visits displayed in the timeline, ensuring they remain visible while scrolling. Use nested events for modelling complex visits (double staffing, breaks within visits).

- **Undo/Redo** – Implement undo/redo stacks for drag‑and‑drop operations and edits. This gives users confidence to experiment with the schedule.

## ⚠️ REALITY CHECK - Implementation Status

**Last Updated:** 2026-03-07  
**Tested:** Manual testing + browser testing + console debugging

### Progress Summary

| Status             | Count  | %        | Description                                       |
| ------------------ | ------ | -------- | ------------------------------------------------- |
| ✅ **done**        | 30     | **50%**  | Tested and verified working                       |
| 🟡 **ux**          | 11     | **18%**  | Config enabled or UI exists, needs backend wiring |
| ❌ **not started** | 19     | **32%**  | Not implemented yet                               |
| **TOTAL**          | **60** | **100%** |                                                   |

**Major Refactor:** Visual system completely redesigned based on user feedback - removed care-type colors, now using scheduling status colors (optional/mandatory/priority/extra/cancelled/absent).

**Filter System:** Fixed to work intuitively - default shows all (buttons highlighted), click to hide specific types, OR logic for multiple selections.

**Features Added in Sprint:**

1. ✅ Employee management (CRUD with modal)
2. ✅ Grouping dropdown (👥 Gruppera by role/contract/transport)
3. ✅ Skill filter (🎯 Kompetens dropdown)
4. ✅ Time zoom (+/- buttons)
5. ✅ Export menu (PDF/Excel/Print)
6. ✅ Obligatoriska filter toggle
7. ✅ Natt/helg toggle
8. ✅ Contract types (Heltid/Timanställd)
9. ✅ Arbetstid format (HH:mm)
10. ✅ Optimization scenario modal (5 presets + custom)
11. ✅ Editable scenario settings (weights, constraints)

**Latest Addition:** Service Area Management with multi-select filtering, visual badges, Resource Utilization integration, and cross-area drag-and-drop workflow.

**Recently Completed:**

- ✅ Optimization scenario modal with 5 presets + custom scenario
- ✅ Embedded Chart (replaced with per-row utilization widget)
- ✅ Tree Summary Heatmap (native treeSummary feature)

---

## 📋 Remaining Features (32% - 19 core features)

### 🔥 High Priority - Core Modes (6 features, ~8 hours)

1. ❌ **Partners** - Side-by-side schedule comparison (1 hour)
2. ❌ **Split** - Clone and compare revisions (1 hour)
3. ✅ **Embedded Chart** - Charts below timeline (REPLACED with per-row utilization widget)
4. ✅ **Tree Summary Heatmap** - Visit density heatmap (native treeSummary feature)
5. 🔄 **Service Area Management** - Multi-select filtering, visual badges, Resource Utilization (IN PROGRESS)
6. ❌ **WebSockets** - Real-time optimization progress (2 hours)

### ⚡ Medium Priority - Advanced Scheduling (7 features, ~6 hours)

7. ❌ **Nested Events** - Double staffing, visit groups (1-2 hours)
8. ❌ **Nested Events Configuration** - Configure nesting rules (30 min)
9. ❌ **Multi Assign** - Multiple caregivers per visit (1 hour)
10. ❌ **Conflicts** - Show overlapping visits visually (30 min)
11. ❌ **Field Filters** - Built-in filter UI (30 min, currently using custom)
12. ❌ **Layers** - Toggle visit type visibility (30 min)
13. ❌ **Lock Rows** - Pin rows from scrolling (15 min)

### 💡 Low Priority - Polish & Nice-to-Have (6 features, ~4 hours)

14. ❌ **Collapsible Columns** - Hide/show employee columns (15 min)
15. ❌ **Export to iCalendar** - iCal export (20 min)
16. ❌ **Responsive** - Mobile adaptation (1 hour)
17. ❌ **Group Summary** - Summary rows for groups (15 min)
18. ❌ **Scroll To** - Navigate to specific event (10 min)
19. ❌ **Custom Event Buttons** - Quick action buttons on events (20 min)

### 🗂️ Out of Scope for MVP (9 features)

These are advanced/specialized features not critical for demo:

- Multi Groups, Recurring Time Ranges, Calendar Editor
- Effort, Booking, Docked Editor
- TinyMCE Event Editor

**MVP Focus:** Complete High + Medium priority = 75% done (13 features, ~14 hours)  
**Full Implementation:** All 19 features per `bryntum_timeplan.md` (14-19 days, 112-152 hours)

---

## Complete Reference with UX Patterns

The following table categorizes each Bryntum feature by UI interaction pattern AND shows actual implementation status.

**UX Categories:**

- **Toggle** = Simple on/off button in toolbar (5-10 min)
- **Filter** = Filter button or dropdown (10-15 min)
- **Panel** = Collapsible sidebar panel (30-60 min)
- **Modal** = Dialog overlay (20-40 min)
- **Mode** = Complete layout change, new view (2-4 hours)
- **Auto** = Automatic behavior, no UI control needed

**Status Values:**

- **done** = Fully working and tested ✅
- **ux added** = UI component added but feature not wired/working 🟡
- **missing** = Not started or not implemented ❌

| Example                         | Application                                                                        | Individual CTA                  | Group/Mode CTA           | Time       | Status       | Notes                                                                                                            |
| ------------------------------- | ---------------------------------------------------------------------------------- | ------------------------------- | ------------------------ | ---------- | ------------ | ---------------------------------------------------------------------------------------------------------------- |
| **Timeline**                    | Base timeline view with drag & drop editing                                        | -                               | 📅 Schema Mode (default) | ✅ Done    | **done**     | 60 visits showing, drag works                                                                                    |
| **Drag Unplanned Tasks**        | Drag visits from panel to assign                                                   | Panel: "Oplanerade"             | 📅 Schema Mode           | ✅ Done    | **done**     | Works with skill validation                                                                                      |
| **Drag From Grid**              | Same as drag unplanned                                                             | Panel: "Oplanerade"             | 📅 Schema Mode           | ✅ Done    | **done**     | Same as above                                                                                                    |
| **Event Menu**                  | Right-click actions (delete, unassign, lock)                                       | Right-click menu                | 📅 Schema Mode           | ✅ Done    | **done**     | Menu shows, lock toggle works                                                                                    |
| **Task Editor**                 | Edit visit details in dialog                                                       | Double-click or Edit button     | 📅 Schema Mode           | ✅ Done    | **done**     | Dialog opens, all fields editable                                                                                |
| **Event Styles**                | Color-code by scheduling status                                                    | Auto (visitStatus field)        | 📅 Schema Mode           | ✅ Done    | **done**     | 6 status colors: optional(blue), mandatory(purple), priority(red), extra(green), cancelled(yellow), absent(grey) |
| **Localization**                | Swedish/English UI                                                                 | Dropdown: "Språk"               | Settings Modal           | ✅ Done    | **done**     | SvSE locale fully applied                                                                                        |
| **Highlight Calendars**         | Show valid drop targets when dragging                                              | Auto (during drag)              | 📅 Schema Mode           | ✅ Done    | **done**     | Highlights valid employees on drag                                                                               |
| **Optimization Scenarios**      | Select scenario before optimization                                                | Modal: "Välj Scenario"          | Scenario Modal           | ✅ Done    | **done**     | 5 presets (A/B/C/Continuity/Efficiency) + custom, editable weights/constraints, session persistence              |
|                                 |                                                                                    |                                 |                          |            |              |                                                                                                                  |
| **Planned vs Actual**           | Compare baseline vs optimized                                                      | Button: 🔀 Jämför               | 🔀 Comparison Mode       | 2-3 hours  | **ux added** | Placeholder UI, not functional                                                                                   |
| **Partners**                    | Side-by-side schedules                                                             | -                               | 🔀 Comparison Mode       | (included) | **missing**  | Not implemented                                                                                                  |
| **Split**                       | Clone and compare revisions                                                        | -                               | 🔀 Comparison Mode       | (included) | **missing**  | Not implemented                                                                                                  |
|                                 |                                                                                    |                                 |                          |            |              |                                                                                                                  |
| **Maps**                        | Geographic route visualization                                                     | Button: 🗺️ Karta                | 🗺️ Map Mode              | 2-3 hours  | **ux added** | Placeholder, have Mapbox token                                                                                   |
| **Maps + AG Grid**              | Grid + map integration                                                             | -                               | 🗺️ Map Mode              | 1-2 hours  | **missing**  | New example showing grid + map combo                                                                             |
| **Travel Time**                 | Show travel before/after visits (eventBuffer)                                      | Auto (always visible)           | 📅 Schema Mode           | ✅ Done    | **done**     | eventBuffer with transport icons (🚗🚴🚶🚌), duration text                                                       |
| **Drag Between Schedulers**     | Cross-area assignments                                                             | -                               | 🗺️ Map Mode (multi-area) | 1 hour     | **missing**  | Not implemented                                                                                                  |
|                                 |                                                                                    |                                 |                          |            |              |                                                                                                                  |
| **Resource Histogram**          | Capacity visualization                                                             | Panel: 📈 Kapacitet             | 📊 Analys Mode           | 45 min     | **ux added** | Enabled, button exists, not showing                                                                              |
| **Resource Utilisation**        | Utilization metrics                                                                | -                               | 📊 Analys Mode           | (included) | **ux added** | Static placeholder values                                                                                        |
| **Timeline Histogram**          | Demand/supply curves                                                               | Panel: 📉 Efterfrågan           | 📊 Analys Mode           | 45 min     | **ux added** | Enabled in config, not visible                                                                                   |
| **Embedded Chart**              | Charts below timeline                                                              | -                               | 📊 Analys Mode           | 30 min     | **missing**  | Not implemented                                                                                                  |
| **Tree Summary Heatmap**        | Heatmap of visit density                                                           | -                               | 📊 Analys Mode           | 1 hour     | **missing**  | Not implemented                                                                                                  |
| **Charts & Sparklines**         | KPI trends                                                                         | Panel: 📊 KPI                   | 📊 Analys Mode           | ✅ Done    | **ux added** | Static metrics panel, no real data                                                                               |
|                                 |                                                                                    |                                 |                          |            |
| **Non-Working Time**            | Hide off-hours                                                                     | Toggle: 🌙 Natt/helg            | 📅 Schema Mode           | 10 min     | **done**     | Toggle button added, feature wired                                                                               |
| **Resource Non-Working Time**   | Employee breaks, lunch                                                             | Toggle: ☕ Pauser               | 📅 Schema Mode           | 15 min     | **done**     | Toggle button working, toggles lunch breaks                                                                      |
| **Resource Time Ranges**        | Visualize availability                                                             | Auto (with breaks)              | 📅 Schema Mode           | 10 min     | **done**     | Lunch breaks data showing in calendar                                                                            |
|                                 |                                                                                    |                                 |                          |            |              |                                                                                                                  |
| **Field Filters**               | Filter by visit/employee attributes                                                | Button: 🔍 Filter               | Filter Panel             | 30 min     | **missing**  | Built-in filterBar disabled (have custom filters)                                                                |
| **Layers**                      | Toggle visit type visibility                                                       | Checkboxes in Filter Panel      | Filter Panel             | 20 min     | **missing**  | Not implemented                                                                                                  |
| **Collapsible Columns**         | Hide/show columns                                                                  | Column header menu              | Settings Modal           | 15 min     | **missing**  | Not implemented                                                                                                  |
|                                 |                                                                                    |                                 |                          |            |              |                                                                                                                  |
| **Constraints**                 | Enforce time windows                                                               | Auto (drag validation) + Visual | 📅 Schema Mode           | 1 hour     | **ux added** | Enabled in config, not tested                                                                                    |
| **Conflicts**                   | Show overlapping visits                                                            | Auto (visual indicator)         | 📅 Schema Mode           | 30 min     | **missing**  | Not configured                                                                                                   |
| **Skill Matching**              | Validate caregiver skills                                                          | Auto (drag validation)          | 📅 Schema Mode           | ✅ Done    | **done**     | Works during drag                                                                                                |
| **Validation**                  | General drag/edit validation                                                       | Auto                            | 📅 Schema Mode           | ✅ Done    | **done**     | Validation messages show                                                                                         |
|                                 |                                                                                    |                                 |                          |            |              |                                                                                                                  |
| **Grouping**                    | Group by area/contract/skill                                                       | Dropdown: 👥 Gruppera           | 📅 Schema Mode           | 20 min     | **done**     | Dropdown added, groups by role/contract/transport                                                                |
| **Group Summary**               | Show summary rows                                                                  | Auto (with grouping)            | 📅 Schema Mode           | 15 min     | **missing**  | Not implemented                                                                                                  |
| **Tree Summary**                | Collapse/expand groups                                                             | Auto (with grouping)            | 📅 Schema Mode           | 10 min     | **done**     | Works in unplanned panel                                                                                         |
| **Multi Groups**                | Employee in multiple groups                                                        | Auto (data-driven)              | 📅 Schema Mode           | 15 min     | **missing**  | Not configured                                                                                                   |
|                                 |                                                                                    |                                 |                          |            |              |                                                                                                                  |
| **Recurrence**                  | Recurring visit patterns                                                           | Toggle: 🔄 Rörliga besök        | 📋 Planning Mode         | 1 hour     | **ux added** | Button exists, feature not configured                                                                            |
| **Recurring Time Ranges**       | Recurring shifts                                                                   | -                               | 📋 Planning Mode         | 30 min     | **missing**  | Not implemented                                                                                                  |
| **Calendar Editor**             | Edit employee calendars                                                            | Modal: Edit Calendar            | Settings Modal           | 30 min     | **missing**  | Not implemented                                                                                                  |
|                                 |                                                                                    |                                 |                          |            |              |                                                                                                                  |
| **Nested Events**               | Double staffing, visit groups                                                      | Auto (data-driven) + Config     | 📅 Schema Mode           | 1-2 hours  | **missing**  | Not configured                                                                                                   |
| **Nested Events Configuration** | Configure nesting rules                                                            | Settings panel                  | Settings Modal           | 30 min     | **missing**  | Not implemented                                                                                                  |
| **Multi Assign**                | Multiple caregivers per visit                                                      | Auto (data-driven)              | 📅 Schema Mode           | 1 hour     | **missing**  | Not configured                                                                                                   |
|                                 |                                                                                    |                                 |                          |            |              |                                                                                                                  |
| **Undo/Redo**                   | Revert manual changes                                                              | Buttons: ↶ ↷                    | 📅 Schema Mode           | 30 min     | **ux added** | Buttons added, feature enabled, not tested                                                                       |
| **State**                       | Persist user settings                                                              | Auto (localStorage)             | All Modes                | 20 min     | **ux added** | Enabled in config, not tested                                                                                    |
| **Configuration**               | View presets (hour/day/week)                                                       | Dropdown: 📅 Visa               | 📅 Schema Mode           | ✅ Done    | **done**     | 1 day, 3 days, 1 week working                                                                                    |
| **Columns**                     | Employee metadata columns                                                          | Column config                   | 📅 Schema Mode           | ✅ Done    | **done**     | Name, role, arbetstid, contract, transport                                                                       |
| **Row Height**                  | Adjust row density                                                                 | Auto (config)                   | Settings Modal           | 5 min      | **done**     | Set to 95px, working                                                                                             |
| **Time Resolution**             | Zoom in/out timeline                                                               | Buttons: + - or Slider          | 📅 Schema Mode           | 15 min     | **done**     | Zoom in/out buttons added to toolbar                                                                             |
| **Scroll To**                   | Navigate to specific event                                                         | Auto (search result)            | 📅 Schema Mode           | 10 min     | **missing**  | Not implemented                                                                                                  |
|                                 |                                                                                    |                                 |                          |            |              |                                                                                                                  |
| **Export**                      | Export to PDF (summary/metrics report)                                             | Button: 💾 Exportera → PDF      | Export Modal             | 30 min     | **done**     | Export menu; PDF = summary + metrics, not full data                                                              |
| **Print**                       | Print schedule                                                                     | -                               | Export Modal             | 20 min     | **done**     | In export menu                                                                                                   |
| **Export to Excel**             | Export full schedule data (employees, shifts, visits, clients, time windows, etc.) | -                               | Export Modal             | 30 min     | **done**     | In export menu; Excel = full data export                                                                         |
| **Export to iCalendar**         | Export to iCal                                                                     | -                               | Export Modal             | 20 min     | **missing**  | Not implemented                                                                                                  |
|                                 |                                                                                    |                                 |                          |            |              |                                                                                                                  |
| **WebSockets**                  | Real-time updates                                                                  | Auto (background)               | All Modes                | 2 hours    | **missing**  | Not implemented                                                                                                  |
| **Infinite Scroll**             | Handle long horizons                                                               | Auto (when needed)              | 📅 Schema Mode           | 30 min     | **done**     | Enabled and working                                                                                              |
| **Big Dataset**                 | Performance for thousands                                                          | Auto (optimization)             | All Modes                | 1 hour     | **done**     | 60 visits performing well                                                                                        |
| **Lock Rows**                   | Pin certain rows from scrolling                                                    | Toggle per row                  | 📅 Schema Mode           | 15 min     | **missing**  | Not implemented                                                                                                  |
| **Responsive**                  | Mobile adaptation                                                                  | Auto (CSS)                      | All Modes                | 30 min     | **missing**  | Not implemented                                                                                                  |
| **Custom Layouts**              | Overlap handling                                                                   | Auto (algorithm)                | 📅 Schema Mode           | 30 min     | **done**     | allowOverlap: false configured                                                                                   |
| **Effort**                      | Workload balancing                                                                 | -                               | 📊 Analys Mode           | 45 min     | **missing**  | Not implemented                                                                                                  |
| **Booking**                     | Financial metrics                                                                  | -                               | 📊 Analys Mode           | 30 min     | **missing**  | Not implemented                                                                                                  |
| **Custom Event Buttons**        | Quick actions on events                                                            | Auto (eventRenderer)            | 📅 Schema Mode           | 20 min     | **missing**  | Not implemented                                                                                                  |
| **Custom Tooltips**             | Detailed event info                                                                | Auto (eventTooltip)             | 📅 Schema Mode           | ✅ Done    | **done**     | Full details in tooltip                                                                                          |
| **Docked Editor**               | Alternative editor UI                                                              | Toggle: Editor style            | Settings Modal           | 30 min     | **missing**  | Not implemented                                                                                                  |
| **TinyMCE Event Editor**        | Rich text notes                                                                    | -                               | Modal upgrade            | 1 hour     | **missing**  | Not implemented                                                                                                  |
| **Test Case**                   | Debug capabilities                                                                 | Dev-only                        | -                        | N/A        | **missing**  | N/A                                                                                                              |

## Mode Definitions

### 📅 Schema Mode (Default - Main Scheduling View)

**What:** Timeline calendar with drag & drop, filters, and inline editing  
**Includes:** Timeline, Drag unplanned, Filters, Grouping, Constraints, Travel time, Breaks, Event editing, Tooltips  
**Button:** Active by default  
**Time to build:** ✅ ~80% done (4 hours), needs 2-3 hours more

### 🔀 Comparison Mode (Baseline vs Optimized)

**What:** Split-screen showing two schedules side-by-side  
**Includes:** Planned vs Actual, Partners, Split, Side-by-side metrics, Delta highlighting  
**Button:** "🔀 Jämför"  
**Time to build:** 2-3 hours

### 🗺️ Map Mode (Geographic View)

**What:** Map with visit markers and routes  
**Includes:** Maps, Maps + AG Grid, Travel time routes, Drag between areas, Location markers  
**Button:** "🗺️ Karta"  
**Time to build:** 3-4 hours (needs Mapbox/Google Maps API)  
**Note:** The Maps + AG Grid example demonstrates combining a data grid with map visualization, useful for displaying visit data in tabular format alongside geographic markers.

### 📊 Analys Mode (Planning & Analytics)

**What:** Pre-planning view with demand/supply analysis  
**Includes:** Resource histogram, Timeline histogram, Embedded charts, Heatmaps, Effort analysis, Booking metrics  
**Button:** "📊 Planering"  
**Time to build:** 3-4 hours

### 💾 Export Modal (Export Options)

**What:** Dialog with export format choices  
**Includes:** PDF (summary and metrics report), Excel (full schedule data: employees, shifts, visits, clients, time windows, etc.), iCal, Print  
**Button:** "💾 Exportera"  
**Time to build:** 1-2 hours

### ⚙️ Settings Modal (Configuration)

**What:** User preferences and view settings  
**Includes:** Localization, Editor style, Row height, Theme, Column visibility  
**Button:** "⚙️ Inställningar"  
**Time to build:** 1-2 hours

## Recommended Toolbar Layout

```
┌────────────────────────────────────────────────────────────────┐
│  [📅 Schema] [🔀 Jämför] [🗺️ Karta] [📊 Planering]            │  ← Mode switchers
│  ────────────────────────────────────────────────────────────  │
│  [🔍 Filter] [🔒 Låsta] [⚠️ Prioritet] [🚗 Restid] [☕ Pauser]│  ← Quick toggles
│  [👥 Gruppera ▼] [📅 Visa ▼]                                  │  ← Dropdowns
│  ────────────────────────────────────────────────────────────  │
│  [◀ Föregående] [Idag] [Nästa ▶] [📅]    [💾] [⚙️] [❓]      │  ← Navigation + Actions
└────────────────────────────────────────────────────────────────┘
```

## Implementation Strategy

### Phase 1: Finish Default Mode (Schema) - 3 hours

- ✅ Timeline (done)
- ✅ Drag & drop (done)
- ✅ Filters (done)
- ⏸️ Fix KPI panel visibility (30 min)
- ⏸️ Add constraints visualization (1 hour)
- ⏸️ Add more toggle filters (1 hour)
- ⏸️ Test all interactions (30 min)

### Phase 2: Add Comparison Mode - 2-3 hours

- Create baseline.json and optimized.json
- Add "Jämför" button
- Implement split layout
- Show metrics delta
- **Result:** Can compare before/after optimization

### Phase 3: Add Map Mode - 3-4 hours

- Integrate Mapbox GL
- Add "Karta" button
- Plot visit markers
- Draw routes
- **Result:** Geographic visualization

### Phase 4: Add Analys Mode - 3-4 hours

- Add Resource Histogram
- Add Timeline Histogram
- Add demand/supply curves
- Add "Planering" button
- **Result:** Capacity planning tools

### Phase 5: Connect Backend - 3-4 hours

- Build mapper layer
- Replace JSON with API
- Hook up save/optimize
- **Result:** Working with real data

**Total: 14-18 hours = 2-3 days**

## Implementation Timeline

**Building from Scratch:** Following `BRYNTUM_FROM_SCRATCH_PRD.md` and `bryntum_timeplan.md`  
**Total Timeline:** 14-19 days (112-152 hours)  
**Approach:** Phased implementation with priority-based development (P0 → P1 → P2)

Build efficiently by:

1. ✅ Reference Bryntum examples from this document
2. ✅ Follow PRD specifications
3. ✅ Implement incrementally by phase
4. ✅ Test as you build

## How to Use This Document

1. Start by reviewing the **Example Catalogue** to familiarise yourself with the available demonstrations. Open each example and interact with it to understand its features and configuration.

2. Use the **Mapping Examples to Caire Features** section as a blueprint: identify which examples correspond to the feature you are implementing and study their implementation details in Bryntum's source.

3. Refer to the **Complete Reference** table when deciding which components to import or customise. If a required feature is not directly available, combine patterns from multiple examples (e.g. nested events with resource histogram for double visits and workload visualisation).

4. When integrating with Caire's API, adapt the data models shown in the examples to use our normalised schema. Provide mapper functions to transform between Bryntum's expected JSON structures and our domain entities.

By following this reference, developers can build a comprehensive scheduling UI that meets all the requirements in [CAIRE_SCHEDULING_PRD](../CAIRE_SCHEDULING_PRD.md) and [CAIRE_PLANNING_PRD](../CAIRE_PLANNING_PRD.md) (and [JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES](../JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES.md) for schema/constraints/dependencies). Implementation tracking: Jira 262, 303–306 (Resources UI), C0-366, CO-43, 201, 203 (schema/resources backend).

---

## Implementation Guide

**Approach:** Building from scratch following `BRYNTUM_FROM_SCRATCH_PRD.md` specifications.

**Backend Interface:** See `BRYNTUM_BACKEND_SPEC.md` for complete GraphQL API specifications.

**Key Implementation Steps:**

1. **Set Up Component Structure** - Create `src/features/scheduling/components/bryntum-calendar/`
2. **Implement Mapper Functions** - Transform GraphQL data to Bryntum format (see `BRYNTUM_BACKEND_SPEC.md`)
3. **Build Core Components** - Follow `BRYNTUM_FROM_SCRATCH_PRD.md` Phase 1-5
4. **Connect to GraphQL** - Use Apollo Client for queries, mutations, subscriptions
5. **Add Swedish Translations** - Use existing i18n setup

**Reference Documents:**

- **Implementation PRD:** `BRYNTUM_FROM_SCRATCH_PRD.md`
- **Timeplan:** `bryntum_timeplan.md`
- **Backend Spec:** `BRYNTUM_BACKEND_SPEC.md`
- **Integration Guide:** `../../08-frontend/BRYNTUM_INTEGRATION.md`

### Data Mapping (Database → Bryntum)

**From DB tables to Bryntum format:**

```typescript
// Server-side mapper (services/bryntum-mapper.ts)
export function mapScheduleToBryntum(
  schedule,
  visits,
  assignments,
  employees,
  breaks,
) {
  return {
    resources: employees.map((e) => ({
      id: e.id,
      name: e.name,
      role: e.role,
      contractType: e.contractType,
      transportMode: e.transportMode,
      calendar: mapEmployeeCalendar(e, breaks), // Working hours + lunch
      // ... Doctor model fields
    })),
    events: visits.map((v) => ({
      id: v.id,
      name: v.name,
      patient: v.clientName,
      startDate: v.plannedStartTime,
      endDate: v.plannedEndTime,
      duration: v.duration / 60, // minutes to hours
      visitStatus: mapVisitStatus(v), // optional/mandatory/priority/etc
      recurrence: v.recurrenceType,
      pinned: v.pinned,
      preamble: v.travelTimeBefore / 60, // minutes to hours
      postamble: v.travelTimeAfter / 60,
      lat: v.address?.latitude,
      lng: v.address?.longitude,
      // ... Appointment model fields
    })),
    assignments: assignments.map((a) => ({
      id: a.id,
      resourceId: a.employeeId,
      eventId: a.visitId,
    })),
  };
}

function mapEmployeeCalendar(employee, breaks) {
  return {
    intervals: [
      {
        startDate: employee.shiftStart,
        endDate: employee.shiftEnd,
        isWorking: true,
      },
    ],
    breaks: breaks
      .filter((b) => b.employeeId === employee.id)
      .map((b) => ({
        startDate: b.startTime,
        endDate: b.endTime,
        name: "Lunch",
        cls: "lunch-break",
      })),
  };
}

function mapVisitStatus(visit) {
  // Business logic to determine status from DB fields
  if (visit.cancelled) return "cancelled";
  if (visit.absent) return "absent";
  if (visit.addedByPlanner) return "extra";
  if (visit.priority === "akut") return "priority";
  if (visit.mandatory) return "mandatory";
  return "optional";
}
```

### Estimated Integration Effort

| Task                        | Time         | Notes                                       |
| --------------------------- | ------------ | ------------------------------------------- |
| Copy components to main app | 30 min       | File copy + import path updates             |
| Create API endpoints        | 2-3 hours    | If using existing services, otherwise 1 day |
| Implement Bryntum mapper    | 2-3 hours    | Map DB → Bryntum format                     |
| Wire save/optimize handlers | 2 hours      | Connect to existing Timefold flow           |
| Add Swedish translations    | 1 hour       | Extract strings, add to locale files        |
| Test with real data         | 2 hours      | Debug edge cases, timezone issues           |
| **TOTAL**                   | **1-2 days** | Assumes backend services already exist      |

---

## Example Catalogue

Below is a catalogue of Bryntum SchedulerPro examples with links and notes on what each demonstrates. Refer back to this table when planning which features to reuse or customise.

| Example                                  | Link                                                                                                                                                                                                                                                                                              | Key Features & Notes                                                                                                                                                                                                                                 |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Maps                                     | https://bryntum.com/products/schedulerpro/examples/maps/                                                                                                                                                                                                                                          | Demonstrates integration of a map layer with the scheduler. Useful for visualising geographic routes or viewing visit locations in pre‑planning.                                                                                                     |
| Maps + AG Grid                           | https://bryntum.com/products/schedulerpro/examples/maps-ag-grid/                                                                                                                                                                                                                                  | Combines AG Grid data grid with map visualization. Shows how to display visit data in a grid alongside geographic map view. Useful for map mode with tabular data display and filtering capabilities.                                                |
| Flight Dispatch                          | https://bryntum.com/products/schedulerpro/examples/flight-dispatch/                                                                                                                                                                                                                               | Shows dynamic label resizing and row height adjustments. Applicable for adjusting employee row heights and event labels based on content.                                                                                                            |
| Embedded Chart                           | https://bryntum.com/products/schedulerpro/examples/embedded-chart/                                                                                                                                                                                                                                | Embeds charts (Chart.js) below the timeline to show capacity utilisation. Ideal for pre‑planning views that need to display demand/supply curves or capacity dashboards.                                                                             |
| Skill Matching                           | https://bryntum.com/products/schedulerpro/examples/skill-matching/                                                                                                                                                                                                                                | Implements drag‑and‑drop with skill validation. Use this pattern to validate caregiver skills against visit requirements when assigning visits.                                                                                                      |
| Table Booking                            | https://bryntum.com/products/schedulerpro/examples/table-booking/                                                                                                                                                                                                                                 | Combines date navigation, a resource (table) schedule and a grid showing booking details. The left panel contains extra resources. Adapt this layout for our conflict management and supply/demand panels (e.g. showing concurrent visits per hour). |
| Planned vs Actual                        | https://bryntum.com/products/schedulerpro/examples/planned-vs-actual/                                                                                                                                                                                                                             | Demonstrates comparing two schedules: planned and actual. Shows side‑by‑side timelines and deltas. Useful for our revision comparison feature.                                                                                                       |
| Resource Histogram & Utilisation         | https://bryntum.com/products/schedulerpro/examples/resourcehistogram/, https://bryntum.com/products/schedulerpro/examples/resourceutilization/                                                                                                                                                    | Adds histograms below the schedule to visualise resource utilisation. We can adopt similar charts to show service area load, travelling vs. service time or capacity vs. demand.                                                                     |
| Timeline                                 | https://bryntum.com/products/schedulerpro/examples/timeline/                                                                                                                                                                                                                                      | A base example with timeline navigation, event editing, and simple drag‑and‑drop. Provides a template for basic schedule editing pages.                                                                                                              |
| Infinite Scroll CRUD Manager             | https://bryntum.com/products/schedulerpro/examples/infinite-scroll-crudmanager/                                                                                                                                                                                                                   | Implements infinite scrolling and CRUD operations on a large dataset. Relevant for schedules spanning many days or with thousands of visits.                                                                                                         |
| Nested Events                            | https://bryntum.com/products/schedulerpro/examples/nested-events/                                                                                                                                                                                                                                 | Shows nested events (shifts within shifts) and drag‑and‑drop support. Use this pattern for modelling double visits or overlapping shifts.                                                                                                            |
| Nested Events Configuration              | https://bryntum.com/products/schedulerpro/examples/nested-events-configuration/                                                                                                                                                                                                                   | Extends nested events with configuration panels. Useful for setting up double staffing options and linking multiple caregivers to a visit.                                                                                                           |
| Conflicts                                | https://bryntum.com/products/schedulerpro/examples/conflicts/                                                                                                                                                                                                                                     | Displays conflict tooltips when events overlap or violate constraints. We can use a similar overlay to show scheduling constraint violations (continuity, skills).                                                                                   |
| Constraints                              | https://bryntum.com/products/schedulerpro/examples/constraints/                                                                                                                                                                                                                                   | Demonstrates "must start on/before/after" constraints. Maps directly to our preferred and allowed time windows.                                                                                                                                      |
| Effort                                   | https://bryntum.com/products/schedulerpro/examples/effort/                                                                                                                                                                                                                                        | Shows redistributing effort across resources. Can inspire UI for balancing workloads across caregivers.                                                                                                                                              |
| Grouping                                 | https://bryntum.com/products/schedulerpro/examples/grouping/                                                                                                                                                                                                                                      | Allows users to group resources and edit group attributes. Suitable for editing shifts or grouping employees by service area, contract type or skill.                                                                                                |
| Non‑Working Time                         | https://bryntum.com/products/schedulerpro/examples/non-working-time/, https://bryntum.com/products/schedulerpro/examples/event-non-working-time/                                                                                                                                                  | Filters out non‑working hours from the timeline. Necessary for compact views that hide nights or off‑hours.                                                                                                                                          |
| Recurrence                               | https://bryntum.com/products/schedulerpro/examples/recurrence/                                                                                                                                                                                                                                    | Implements recurring events with repeat rules. Use this for weekly or monthly movable visits in pre‑planning.                                                                                                                                        |
| Calendar Editor                          | https://bryntum.com/products/schedulerpro/examples/calendar-editor/                                                                                                                                                                                                                               | Enables editing of resource calendars (availability). Useful for managing caregiver working hours and personal calendars.                                                                                                                            |
| Resource Non‑Working Time                | https://bryntum.com/products/schedulerpro/examples/resource-non-working-time/                                                                                                                                                                                                                     | Differentiates day, evening and night shifts; use to visualise shift patterns.                                                                                                                                                                       |
| Travel Time                              | https://bryntum.com/products/schedulerpro/examples/travel-time/                                                                                                                                                                                                                                   | Shows travel time between jobs; could be integrated into event tooltips or map overlays.                                                                                                                                                             |
| Tree Summary Heatmap                     | https://bryntum.com/products/schedulerpro/examples/tree-summary-heatmap/                                                                                                                                                                                                                          | Offers heatmap visualisation summarising events per day. Could be used for demand curves by area or employee.                                                                                                                                        |
| Custom Layouts                           | https://bryntum.com/products/schedulerpro/examples/custom-layouts/                                                                                                                                                                                                                                | Illustrates custom event layout algorithms to handle overlapping events. Helps manage visits that overlap due to double staffing or overlapping time windows.                                                                                        |
| Localization                             | https://bryntum.com/products/schedulerpro/examples/localization/                                                                                                                                                                                                                                  | Demonstrates multi‑language support for SchedulerPro. Essential for Swedish/English localisation.                                                                                                                                                    |
| Task Editor                              | https://bryntum.com/products/schedulerpro/examples/taskeditor/                                                                                                                                                                                                                                    | Provides a rich event editor with tabs for general info, assignments, predecessors and successors. Use this to edit visit and client details.                                                                                                        |
| Highlight Event Calendars & Resources    | https://bryntum.com/products/schedulerpro/examples/highlight-event-calendars/, https://bryntum.com/products/schedulerpro/examples/highlight-resource-calendars/                                                                                                                                   | Shows how to highlight valid drop targets when dragging. Useful for constraint feedback (available caregivers, valid time slots).                                                                                                                    |
| Highlight Time Spans                     | https://bryntum.com/products/schedulerpro/examples/highlight-time-spans/                                                                                                                                                                                                                          | Highlights working hours or opening hours. Could be adapted to highlight preferred windows.                                                                                                                                                          |
| Drag From Grid / Drag Unplanned Tasks    | https://bryntum.com/products/schedulerpro/examples/drag-from-grid/, https://bryntum.com/products/schedulerpro/examples/drag-unplanned-tasks/                                                                                                                                                      | Demonstrates dragging tasks from a grid or list into the scheduler. Aligns with our Unplanned panel for unassigned visits.                                                                                                                           |
| Nested Events Drag From Grid             | https://bryntum.com/products/schedulerpro/examples/nested-events-drag-from-grid/                                                                                                                                                                                                                  | Shows dragging nested events into the schedule. Useful for double visits or group visits where multiple caregivers are assigned.                                                                                                                     |
| Big Dataset                              | https://bryntum.com/products/schedulerpro/examples/bigdataset/                                                                                                                                                                                                                                    | Handles thousands of events and hundreds of resources. Ensures performance at scale.                                                                                                                                                                 |
| Booking (Scheduler)                      | https://bryntum.com/products/schedulerpro/examples-scheduler/booking/                                                                                                                                                                                                                             | Displays calculated sums per date. Could be adapted to show revenue, cost or service hours per resource or service area.                                                                                                                             |
| Infinite Scroll                          | https://bryntum.com/products/schedulerpro/examples-scheduler/infinite-scroll/                                                                                                                                                                                                                     | Supports infinite scrolling along the time axis. Useful for long‑horizon planning.                                                                                                                                                                   |
| Partners                                 | https://bryntum.com/products/schedulerpro/examples-scheduler/partners/                                                                                                                                                                                                                            | Shows duplicate, synchronised schedules side by side. Can be used for revision comparison.                                                                                                                                                           |
| Timeline Histogram                       | https://bryntum.com/products/schedulerpro/examples-scheduler/timelinehistogram/                                                                                                                                                                                                                   | Adds a histogram under the timeline to show aggregated values per tick. Could display demand, supply or travel time distribution.                                                                                                                    |
| WebSockets                               | https://bryntum.com/products/schedulerpro/examples-scheduler/websockets/                                                                                                                                                                                                                          | Demonstrates real‑time updates via WebSockets. Use this to reflect live changes (cancellations, sick calls) in the schedule.                                                                                                                         |
| Drag Between Schedulers                  | https://bryntum.com/products/schedulerpro/examples-scheduler/drag-between-schedulers/                                                                                                                                                                                                             | Enables dragging resources/events across two scheduler instances. Perfect for moving visits or employees between service areas.                                                                                                                      |
| Drag From List                           | https://bryntum.com/products/schedulerpro/examples-scheduler/drag-from-list/                                                                                                                                                                                                                      | Provides a list of items (e.g. skills) that can be dragged onto events. Useful for assigning skills or tags to visits.                                                                                                                               |
| Charts & Sparklines                      | https://bryntum.com/products/schedulerpro/examples-scheduler/charts/, https://bryntum.com/products/schedulerpro/examples-scheduler/sparklines/, https://bryntum.com/products/schedulerpro/examples-scheduler/scheduler-chart/                                                                     | Integrates charts directly into the scheduler or alongside it. Use these components to visualise metrics like travel time, utilisation and continuity trends.                                                                                        |
| Configuration                            | https://bryntum.com/products/schedulerpro/examples-scheduler/configuration/                                                                                                                                                                                                                       | Shows how to create view presets and date horizons. Relevant for monthly/weekly planning and pre‑planning windows.                                                                                                                                   |
| Columns                                  | https://bryntum.com/products/schedulerpro/examples-scheduler/columns/                                                                                                                                                                                                                             | Demonstrates adding extra columns for resources. We can include contract type, number of visits, total service time and efficiency per employee.                                                                                                     |
| Row Height                               | https://bryntum.com/products/schedulerpro/examples-scheduler/rowheight/                                                                                                                                                                                                                           | Adjusts row height, margins and event sizes. Useful for dense schedules or responsive design.                                                                                                                                                        |
| Scroll To                                | https://bryntum.com/products/schedulerpro/examples-scheduler/scrollto/                                                                                                                                                                                                                            | Programmatically scrolls to a specific event. Could be tied to search or alerting functions.                                                                                                                                                         |
| Time Resolution                          | https://bryntum.com/products/schedulerpro/examples-scheduler/timeresolution/                                                                                                                                                                                                                      | Demonstrates zooming and changing time resolution. Use for zoom in/out controls.                                                                                                                                                                     |
| State                                    | https://bryntum.com/products/schedulerpro/examples-scheduler/state/                                                                                                                                                                                                                               | Implements auto‑save and reset. Use this pattern to persist user settings and unsaved changes.                                                                                                                                                       |
| Event Styles                             | https://bryntum.com/products/schedulerpro/examples-scheduler/eventstyles/                                                                                                                                                                                                                         | Shows various event styling options. Use for colour‑coding visits based on status or type.                                                                                                                                                           |
| Collapsible Columns                      | https://bryntum.com/products/schedulerpro/examples-scheduler/collapsible-columns/                                                                                                                                                                                                                 | Allows columns to be collapsed or expanded. Useful for hiding less important employee fields.                                                                                                                                                        |
| Field Filters & Advanced Filtering       | https://bryntum.com/products/schedulerpro/examples-scheduler/fieldfilters/, https://bryntum.com/products/schedulerpro/examples-scheduler/filtering/                                                                                                                                               | Provides built‑in filtering UIs. Adapt these for our visit and employee filters.                                                                                                                                                                     |
| Grouping & Group Summary                 | https://bryntum.com/products/schedulerpro/examples-scheduler/grouping/, https://bryntum.com/products/schedulerpro/examples-scheduler/groupsummary/                                                                                                                                                | Groups resources and displays summary rows. Use to group employees by service area, contract type or skill and show aggregated metrics.                                                                                                              |
| Multi Assign & Multi Assign Resource IDs | https://bryntum.com/products/schedulerpro/examples-scheduler/multiassign/, https://bryntum.com/products/schedulerpro/examples-scheduler/multiassign-resourceids/                                                                                                                                  | Supports assigning multiple resources to a single event. Necessary for double visits and group visits.                                                                                                                                               |
| Multi Summary                            | https://bryntum.com/products/schedulerpro/examples-scheduler/multisummary/                                                                                                                                                                                                                        | Shows summaries for both events and resources. Useful for aggregated metrics across multiple schedules.                                                                                                                                              |
| Recurring Time Ranges                    | https://bryntum.com/products/schedulerpro/examples-scheduler/recurringtimeranges/                                                                                                                                                                                                                 | Adds recurring time ranges to the schedule (e.g. daily morning meeting). Use for recurring caregiver shifts or availability.                                                                                                                         |
| Resource Time Ranges                     | https://bryntum.com/products/schedulerpro/examples-scheduler/resourcetimeranges/                                                                                                                                                                                                                  | Defines time ranges per resource. Helps visualise shift availability and non‑working periods.                                                                                                                                                        |
| Responsive                               | https://bryntum.com/products/schedulerpro/examples-scheduler/responsive/                                                                                                                                                                                                                          | Demonstrates responsive layouts. Use this to design caregiver mobile and client views.                                                                                                                                                               |
| Split                                    | https://bryntum.com/products/schedulerpro/examples-scheduler/split/                                                                                                                                                                                                                               | Clones and splits schedules. Use to create fine‑tune revisions and compare them side by side.                                                                                                                                                        |
| Tree Summary                             | https://bryntum.com/products/schedulerpro/examples-scheduler/tree-summary/                                                                                                                                                                                                                        | Summarises hierarchical groups (e.g. service areas). Use for collapsing and summarising groups of employees.                                                                                                                                         |
| Undo/Redo                                | https://bryntum.com/products/schedulerpro/examples-scheduler/undoredo/                                                                                                                                                                                                                            | Provides undo/redo functionality. Essential for safe editing.                                                                                                                                                                                        |
| Working Time                             | https://bryntum.com/products/schedulerpro/examples-scheduler/workingtime/                                                                                                                                                                                                                         | Visualises working vs. non‑working time. Use to shade non‑working hours and enforce constraints.                                                                                                                                                     |
| Multi Groups                             | https://bryntum.com/products/schedulerpro/examples-scheduler/multi-groups/                                                                                                                                                                                                                        | Shows resources appearing in multiple groups. Supports employees belonging to multiple service areas.                                                                                                                                                |
| Lock Rows                                | https://bryntum.com/products/schedulerpro/examples-scheduler/lock-rows/                                                                                                                                                                                                                           | Locks certain rows from scrolling. Could be applied to unassigned visits displayed in the timeline.                                                                                                                                                  |
| Docked Editor                            | https://bryntum.com/products/schedulerpro/examples-scheduler/docked-editor/                                                                                                                                                                                                                       | A task editor docked next to the timeline. Use for editing visits without a modal.                                                                                                                                                                   |
| Event Menu                               | https://bryntum.com/products/schedulerpro/examples-scheduler/eventmenu/                                                                                                                                                                                                                           | Provides context menu actions on events (cut, copy, lock, split, move). Adapt this to implement pinning/unpinning and quick edits.                                                                                                                   |
| Layers                                   | https://bryntum.com/products/schedulerpro/examples-scheduler/layers/                                                                                                                                                                                                                              | Demonstrates filtering by layers. Use for toggling visibility of different visit types (mandatory, skills, priorities).                                                                                                                              |
| Custom Event Buttons                     | https://bryntum.com/products/schedulerpro/examples-scheduler/custom-event-buttons/                                                                                                                                                                                                                | Shows buttons on events for quick actions. Could include "mark as completed," "open details," etc.                                                                                                                                                   |
| Event Editor with TinyMCE                | https://bryntum.com/products/schedulerpro/examples-scheduler/eventeditor-tinymce/                                                                                                                                                                                                                 | Integrates a rich text editor for editing event descriptions or notes.                                                                                                                                                                               |
| Validation                               | https://bryntum.com/products/schedulerpro/examples-scheduler/validation/                                                                                                                                                                                                                          | Implements drag‑and‑drop validation and resizing rules. Use to enforce labour law and continuity constraints during editing.                                                                                                                         |
| Export & Print                           | https://bryntum.com/products/schedulerpro/examples-scheduler/export/, https://bryntum.com/products/schedulerpro/examples-scheduler/print/, https://bryntum.com/products/schedulerpro/examples-scheduler/exporttoexcel/, https://bryntum.com/products/schedulerpro/examples-scheduler/exporttoics/ | Demonstrates exporting schedules to PDF, PNG, Excel or iCalendar. Use for reporting and hand‑offs to external systems.                                                                                                                               |
| Test Case & Debugging                    | https://bryntum.com/products/schedulerpro/examples-scheduler/test-case/                                                                                                                                                                                                                           | Provides tools for generating reproducible test cases and downloading data. Can be adapted for QA and debugging our scheduler.                                                                                                                       |
