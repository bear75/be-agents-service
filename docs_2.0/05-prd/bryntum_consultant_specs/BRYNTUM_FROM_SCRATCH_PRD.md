# Bryntum From Scratch PRD – For External Consultants

> **Archive notice:** This document is superseded by [bryntum_timeplan.md](bryntum_timeplan.md), which is the canonical work plan for Bryntum implementation (categories, hours, Bryntum examples, acceptance criteria). Use the timeplan for current scope and reference.

**Version:** 3.0  
**Date:** 2025-12-17  
**Purpose:** Request for Quote (RFQ) for building Bryntum SchedulerPro UI from scratch  
**Target Audience:** Ballistix Consultants (Professional Bryntum Developers)

---

## Executive Summary

Caire is a home-care scheduling platform that requires a professional scheduling calendar UI built with Bryntum SchedulerPro. We need experienced Bryntum developers to build this **from scratch**, following best practices and Bryntum's recommended patterns.

**Scope:**

1. **Build Bryntum SchedulerPro UI** from scratch using official Bryntum examples as reference
2. **Connect to GraphQL backend API** (to be provided during project)
3. **Implement data transformation** between backend format and Bryntum format
4. **Ensure all features work with production data**

**Key Requirement:** Build a production-ready, maintainable solution using Bryntum's recommended patterns and examples. This is a **greenfield build**, not an integration of existing code.

**Timeline Estimate:** 14-19 working days (112-152 hours) - See `bryntum_timeplan.md` for detailed breakdown.

**Note:**

- Backend API specifications and requirements are provided in a separate document (`BRYNTUM_BACKEND_SPEC.md`) that can be attached for reference.

---

## Project Context

### Current State

- ✅ **Requirements Defined:** Complete feature specifications and Bryntum example mappings
- ✅ **Backend API:** GraphQL API being developed (will be provided during project)
- ✅ **Data Model:** Normalized database schema documented
- ❌ **Frontend UI:** Needs to be built from scratch using Bryntum SchedulerPro

### Target State

- ✅ Professional Bryntum SchedulerPro calendar integrated into main application
- ✅ Connected to GraphQL API (Express + Apollo Server)
- ✅ Real-time optimization progress via WebSocket subscriptions
- ✅ All features working with production data
- ✅ Type-safe end-to-end (Prisma → GraphQL → React)
- ✅ Production-ready, maintainable code following Bryntum best practices

---

## Technology Stack

**Frontend:**

- React 18 with TypeScript
- Vite (build tool and dev server)
- Apollo Client for GraphQL
- Bryntum SchedulerPro 7.0.0+
- React Router for navigation
- Tailwind CSS for styling

**Backend (Provided by Caire):**

- Express.js + Apollo Server
- GraphQL API (queries, mutations, subscriptions)
- Prisma ORM with PostgreSQL
- WebSocket for real-time subscriptions

**Note:** Detailed backend API specifications are in the separate `BRYNTUM_BACKEND_SPEC.md` document.

---

## Scope of Work

### Phase 1: Core Calendar Implementation

**Task:** Build main scheduling calendar view using Bryntum SchedulerPro

**Primary Bryntum Examples to Reference:**

- **Timeline** - https://bryntum.com/products/schedulerpro/examples/timeline/ (Base timeline with drag & drop)
- **Columns** - https://bryntum.com/products/schedulerpro/examples-scheduler/columns/ (Employee metadata columns)
- **Row Height** - https://bryntum.com/products/schedulerpro/examples-scheduler/rowheight/ (Row sizing)
- **Time Resolution** - https://bryntum.com/products/schedulerpro/examples-scheduler/timeresolution/ (Zoom controls)

**Features Required:**

- Timeline view with employees as resources and visits as events
- Employee rows with metadata columns (name, role, contract type, transport mode, working hours)
- Time axis navigation (day/week/month views)
- Zoom in/out controls
- Drag-and-drop assignment of visits to employees
- Visit editing (time, duration) via drag/resize
- Event tooltips showing visit details

**Acceptance Criteria:**

- [ ] Calendar displays schedule data from GraphQL API
- [ ] All basic interactions work (drag, drop, edit, resize)
- [ ] Performance acceptable with 100+ employees and 1000+ visits
- [ ] Swedish localization applied

---

### Phase 2: Drag & Drop & Validation

**Task:** Implement advanced drag-and-drop with validation

**Primary Bryntum Examples to Reference:**

- **Drag Unplanned Tasks** - https://bryntum.com/products/schedulerpro/examples/drag-unplanned-tasks/ (Unassigned visits panel)
- **Skill Matching** - https://bryntum.com/products/schedulerpro/examples/skill-matching/ (Skill validation during drag)
- **Highlight Event Calendars** - https://bryntum.com/products/schedulerpro/examples/highlight-event-calendars/ (Valid drop targets)
- **Constraints** - https://bryntum.com/products/schedulerpro/examples/constraints/ (Time window validation)
- **Validation** - https://bryntum.com/products/schedulerpro/examples-scheduler/validation/ (Drag validation rules)

**Features Required:**

- Unplanned visits panel (sidebar) with draggable visits
- Drag visits from panel to employee rows
- Skill validation (highlight valid employees based on required skills)
- Time window validation (prevent moves outside allowed windows)
- Visual feedback during drag (highlight valid/invalid targets)
- Constraint enforcement (preferred vs allowed windows)

**Acceptance Criteria:**

- [ ] Unplanned visits can be dragged and assigned
- [ ] Skill matching works correctly
- [ ] Time constraints are enforced
- [ ] Visual feedback is clear and intuitive

---

https://caire.atlassian.net/wiki/spaces/CAIREHCDD/database/22380545?atl_f=PAGETREE
https://caire.atlassian.net/wiki/spaces/CAIREHCDD/database/22446081?atl_f=PAGETREE

### Phase 3: Editing & Event Management

**Task:** Implement visit editing and event management features

**Primary Bryntum Examples to Reference:**

- **Event Edit** - https://bryntum.com/products/schedulerpro/examples-scheduler/eventedit/ (Event editing UI)
- **Event Menu** - https://bryntum.com/products/schedulerpro/examples-scheduler/eventmenu/ (Context menu)
- **Event Tooltip** - https://bryntum.com/products/schedulerpro/examples-scheduler/eventtooltip/ (Hover tooltips)
- **Event Drag** - https://bryntum.com/products/schedulerpro/examples-scheduler/eventdrag/ (Drag to reschedule)

**Features Required:**

- Inline editing of visit details (time, duration, client)
- Context menu for visits (edit, delete, pin/unpin, assign)
- Visit tooltips with detailed information
- Resize visits to change duration
- Pin/unpin visits (lock time and assignment)
- Delete visits with confirmation

**Acceptance Criteria:**

- [ ] All editing features work correctly
- [ ] Changes save to database via GraphQL
- [ ] Validation prevents invalid edits
- [ ] User feedback is clear

---

### Phase 4: Filtering & Grouping

**Task:** Implement filtering and grouping capabilities

**Primary Bryntum Examples to Reference:**

- **Filter** - https://bryntum.com/products/schedulerpro/examples-scheduler/filter/ (Resource/event filtering)
- **Group** - https://bryntum.com/products/schedulerpro/examples-scheduler/group/ (Resource grouping)
- **Search** - https://bryntum.com/products/schedulerpro/examples-scheduler/search/ (Search functionality)

**Features Required:**

- Filter employees by service area, role, skills
- Filter visits by client, type, priority, status
- Group employees by service area or role
- Search for specific employees or visits
- Quick filters (unassigned visits, high priority, etc.)

**Acceptance Criteria:**

- [ ] All filters work with real data
- [ ] Grouping updates dynamically
- [ ] Search is fast and accurate
- [ ] Filter state persists across navigation

---

### Phase 5: Comparison Mode

**Task:** Implement schedule comparison functionality

**Primary Bryntum Examples to Reference:**

- **Multiple Resources** - https://bryntum.com/products/schedulerpro/examples-scheduler/multiassign/ (Multiple assignments)
- **Split View** - Custom implementation for side-by-side comparison

**Features Required:**

- Compare two schedules side-by-side
- Highlight differences (added/removed/moved visits)
- Metrics comparison panel
- Switch between schedules quickly

**Acceptance Criteria:**

- [ ] Comparison mode works with real schedules
- [ ] Differences are clearly highlighted
- [ ] Metrics comparison is accurate
- [ ] Performance is acceptable

---

### Phase 6: Analytics & Charts

**Task:** Implement analytics and chart visualizations

**Primary Bryntum Examples to Reference:**

- **Timeline Histogram** - https://bryntum.com/products/schedulerpro/examples-scheduler/timelinehistogram/ (Demand visualization)
- **Resource Histogram** - https://bryntum.com/products/schedulerpro/examples-scheduler/resourcehistogram/ (Capacity visualization)

**Features Required:**

- Metrics panel showing KPIs (utilization, travel time, waiting time, unassigned visits)
- Visual indicators on resources and events (toggle show/hide)
- Metrics modal button
- Charts for demand curve, capacity utilization
- Tooltips showing individual metrics (employee and client level)
- Client profitability indicators (unprofitable clients, high travel/wait ratios)

**Acceptance Criteria:**

- [ ] Metrics panel displays accurate data
- [ ] Charts update with schedule changes
- [ ] Metrics tooltips display individual metrics
- [ ] Visual indicators toggle works
- [ ] Metrics modal opens and displays all clients and employees
- [ ] Client profitability indicators display correctly

---

### Phase 7: Advanced Features

**Task:** Implement advanced scheduling features

**Primary Bryntum Examples to Reference:**

- **Dependencies** - https://bryntum.com/products/schedulerpro/examples-scheduler/dependencies/ (Visit dependencies)
- **Non Working Time** - https://bryntum.com/products/schedulerpro/examples-scheduler/nonworkingtime/ (Break periods)
- **Time Ranges** - https://bryntum.com/products/schedulerpro/examples-scheduler/timeranges/ (Time overlays)

**Features Required:**

- Employee working hours visualization
- Break periods display
- Time range overlays (unused client allocation, capacity)
- Visit dependencies (if applicable)
- Continuity indicators (same caregiver, same time)

**Acceptance Criteria:**

- [ ] All advanced features work correctly
- [ ] Visual indicators are clear
- [ ] Performance is maintained

---

### Phase 8: Real-time & Optimization

**Task:** Implement real-time optimization integration

**Primary Bryntum Examples to Reference:**

- **WebSockets** - https://bryntum.com/products/schedulerpro/examples-scheduler/websockets/ (Real-time updates)
- **Progress Bar** - Custom implementation for optimization progress

**Features Required:**

- Trigger optimization via GraphQL mutation
- Real-time progress updates via WebSocket subscription
- Progress bar showing optimization status
- Display optimized solution when complete
- Diff view showing changes (before/after)
- Accept/reject optimized solution

**Acceptance Criteria:**

- [ ] Optimization triggers correctly
- [ ] Real-time updates work via WebSocket
- [ ] Progress is clearly displayed
- [ ] Solution updates calendar automatically
- [ ] Diff view is clear and intuitive

---

### Phase 9: Pre-Planning & Movable Visits

**Task:** Implement pre-planning workflow for weekly/monthly planning with movable visits

**Primary Bryntum Examples to Reference:**

- **Timeline** - https://bryntum.com/products/schedulerpro/examples/timeline/ (Multi-week/month view)
- **Timeline Histogram** - https://bryntum.com/products/schedulerpro/examples-scheduler/timelinehistogram/ (Demand curve visualization)
- **WebSockets** - https://bryntum.com/products/schedulerpro/examples-scheduler/websockets/ (Real-time pre-planning progress)
- **Drag Unplanned Tasks** - https://bryntum.com/products/schedulerpro/examples/drag-unplanned-tasks/ (Unassigned movable visits panel)
- **Highlight Time Spans** - https://bryntum.com/products/schedulerpro/examples/highlight-time-spans/ (Unused hours visualization)
- **Time Ranges** - https://bryntum.com/products/schedulerpro/examples-scheduler/timeranges/ (Supply/demand overlays)

#### Core Concepts

**Pre-Planning:** Process of planning recurring visits across multiple weeks/months before they enter daily scheduling. Allows finding optimal patterns (day-of-week, time-of-day) for recurring visits.

**Movable Visit:** A recurring visit with flexible time window (e.g., "weekly, any day 8 AM-12 PM") that can be optimized to find best placement.

**Pinned Visit:** Fixed time, duration, and caregiver (🔒 icon, solid background). Cannot move unless explicitly unlocked. Represents stable recurring patterns (slingor).

**Unpinned Visit:** Movable within allowed window (dashed border). Can be moved by optimizer or user. Used for new clients and flexible tasks.

**Time Horizon:** Planning period (1 week, 1 month, 3 months, custom) for pre-planning optimization.

**Unused Hours:** Client allocation hours that were not utilized (monthly allocation - actual service hours delivered). If a client has 100h total allowed visits per month and 5h are cancelled (by client or by org if optional visit during supply limitation), the unused hours = 5h. These unused hours can be recaptured when we have excess staff capacity.

**Supply/Demand Balance:** Comparison of available employee capacity (supply) vs required visit hours (demand) across time horizon.

#### Features Required

**1. Pre-Planning Hub (Main Entry Point)**

- **Location:** `/dashboard/scheduling/pre-planning`
- **Time Horizon Selector:** Dropdown/buttons to select planning period (1 week, 1 month, 3 months, custom date range)
- **Movable Visits Panel:** Sidebar showing all unassigned/unpinned visits
  - Grouped by client and frequency
  - Shows time window, priority, skills required
  - Drag-and-drop to calendar or "Get Recommendations" button
- **Consolidated Schedule View:** Multi-week/month Bryntum calendar
  - Shows all schedules in planning horizon
  - Pinned visits: Solid blue background with 🔒 icon
  - Unpinned visits: Dashed border, can be moved
  - Unassigned visits: Shown in panel, not on calendar until placed
- **Supply/Demand Dashboard:** Panel showing capacity vs demand metrics
  - Total supply hours (all employees)
  - Total demand hours (all visits)
  - Balance (supply - demand)
  - Utilization percentage
  - Color-coded indicators (green: balanced 75-85%, yellow: <75%, red: >90%)
- **Unused Hours Tracker:** Display unused client allocation
  - Total unused hours across horizon (sum of all clients' unused allocation)
  - Per-client breakdown (which clients have unused allocation)
  - Per-day breakdown
  - Recapture opportunities (can be used when we have excess staff capacity)

**2. Movable Visits Management**

- **Create New Movable Visit Form:**
  - Client selection (search/select or create new)
  - Visit title (e.g., "Frukosthjälp", "Medicinering")
  - Duration (minutes)
  - Frequency (daily, weekly, bi-weekly, monthly)
  - Time window (e.g., "Morgon 07:00-10:00", "Lunch 11:00-13:00")
  - Priority (mandatory/optional)
  - Skills required (delegation, language, gender)
  - Preferred staff (optional)
  - Non-preferred staff (optional)
- **Configure Existing Movable Visit:**
  - Edit time windows, frequency, priority
  - Update skills requirements
  - Adjust preferred/non-preferred staff
- **Movable Visits List:**
  - Status indicators (draft, optimized, exported, synced)
  - Filter by status, client, frequency
  - Bulk operations (freeze, unfreeze, delete)

**3. Consolidated Schedule View (Bryntum Calendar)**

- **Multi-Week/Month Display:**
  - View preset: Day/Week/Month/Custom
  - Scroll/zoom to navigate across planning horizon
  - All schedules in horizon visible simultaneously
- **Visual Indicators:**
  - **Pinned visits:** Solid blue background, 🔒 icon in corner, cannot be moved
  - **Unpinned visits:** Dashed border (color-coded by priority), can be dragged
  - **Unused allocation periods:** Gray/transparent time range overlays showing when unused client allocation could be recaptured (toggle show/hide)
  - **Supply/demand indicators:** Color-coded bars on resource rows (green/yellow/red)
- **Time Horizon Navigation:**
  - Date picker to jump to specific week/month
  - Previous/Next buttons to navigate
  - Zoom controls (day/week/month view)
- **Event Tooltips:**
  - Visit details (client, duration, skills, priority)
  - Assignment info (employee, time, travel)
  - Metrics (unused allocation hours if moved, recapture impact)

**4. Supply/Demand Balance Dashboard**

- **Aggregated Metrics:**
  - Total supply hours (all employees across horizon)
  - Total demand hours (all visits across horizon)
  - Balance (supply - demand)
  - Average utilization percentage
  - Total unused allocation hours (sum of all clients' unused allocation)
- **Per-Day Breakdown:**
  - Bar chart showing supply/demand for each day
  - Stacked bars: Service hours (bottom), Travel+Wait (middle), Unused (top)
  - Target line: Optimal utilization (75-85%)
  - Color coding: Green (balanced), Yellow (moderate), Red (critical)
- **Per-Client Breakdown:**
  - Table showing each client's allocation vs delivered
  - Monthly allocation
  - Actual service hours delivered
  - Unused allocation hours
  - Can recapture when excess staff capacity available
- **Recommendations Panel:**
  - AI-powered suggestions based on supply/demand
  - "Recapture Unused Allocation" (high unused client allocation + excess staff capacity)
  - "Monitor Unused Allocation" (persistent high unused client allocation)
  - "Adjust Schedule" (moderate unused allocation)
  - Click recommendation to see detailed impact analysis

**5. Demand Curve Visualization**

- **Line Chart:** Show visit hours per day/week over time horizon
- **Capacity Line:** Overlay employee capacity (supply)
- **Trend Indicators:**
  - Upward trend (increasing demand) - green arrow up
  - Downward trend (decreasing demand) - red arrow down
  - Stable (consistent demand) - gray horizontal line
- **Anomaly Detection:** Highlight days with unusual demand spikes/drops
- **Historical Comparison:** Compare current horizon with previous periods

**6. Pre-Planning Optimization**

- **Optimization Trigger Button:** "Run Pre-Planning Optimization"
- **Progress Tracking:**
  - WebSocket subscription for real-time updates
  - Progress bar showing current stage (Pattern Discovery / Employee Assignment)
  - Estimated time remaining
  - Current metrics (travel time saved, continuity score, utilization)
- **Diff View (After Optimization):**
  - **Ghost tracks:** Faded original positions of moved visits
  - **Solid blocks:** New optimized positions
  - **Connector lines:** Show where visits moved from/to
  - **Tooltips:** Explain moves ("Moved 15 min earlier to sync with neighbor visit")
- **Review & Accept:**
  - Accept all changes button
  - Accept individual changes (checkbox per visit)
  - Reject and re-optimize with adjusted parameters
  - Metrics comparison (before vs after)

**7. Unused Hours Display**

- **Visual Indicators:**
  - **Client Badge:** Show unused allocation hours as badge on client visits (e.g., "5h unused allocation")
  - **Time Range Overlay:** Highlight periods where unused allocation could be recaptured
  - **Tooltip:** Show unused allocation hours when hovering over client visits
- **Unused Hours Panel:**
  - Total unused hours across horizon (sum of all clients' unused allocation)
  - Per-client breakdown (which clients have unused allocation and how much)
  - Per-day breakdown
  - Recapture opportunities (can be used when we have excess staff capacity)
- **Toggle:** "Show Unused Hours" checkbox in toolbar
  - When enabled: Badges, overlays, tooltips visible
  - When disabled: Normal calendar view (still calculated, not displayed)

**8. Recommendations for Optimal Placement**

- **AI-Powered Recommendations:**
  - Based on supply/demand balance analysis
  - Ranked suggestions (score 0-100)
  - Shows day-of-week, time window, recommended employee
  - Reasoning text ("Fits existing gap", "Minimizes travel", "Maintains continuity")
  - Impact metrics (utilization change, travel time change, continuity score)
- **Display:**
  - Recommendations shown in tooltip when hovering over calendar cells
  - "Best Fit" badge on recommended time slots
  - Recommendations panel with list of all suggestions
  - Click recommendation to auto-fill visit configuration

**9. Schedule Health Tracking**

- **Health Metrics Panel:**
  - **Stability Score:** How consistent are visit patterns? (0-100)
  - **Capacity Utilization:** Average utilization across time horizon
  - **Unused Hours Trend:** Are clients' unused allocation hours increasing/decreasing?
  - **Continuity Score:** How well are continuity promises maintained?
  - **Travel Efficiency:** Average travel time per visit
- **Visual Indicators:**
  - 🟢 Green: Healthy (stability > 80%, utilization 75-85%)
  - 🟡 Yellow: Warning (stability 60-80%, utilization < 75% or > 90%)
  - 🔴 Red: Critical (stability < 60%, utilization < 60% or > 95%)
- **Long-Term Tracking:**
  - Timeline view showing health metrics over past 3/6/12 months
  - Trend arrows (improving/declining/stable)
  - Recommendations based on trends

**10. Adding New Client's Movable Visit to Existing Schedules**

- **Workflow:**
  1. User creates new movable visit (form in Pre-Planning Hub)
  2. System generates unassigned visits for planning horizon
  3. Visits appear in "Unassigned Visits" panel
  4. User runs pre-planning optimization
  5. Optimizer inserts new visits around pinned patterns (doesn't disrupt existing)
  6. User reviews optimized schedule with diff view
  7. User accepts and pins approved visits
  8. Pinned visits become part of slingor (recurring patterns)
- **Visual Feedback:**
  - New visits shown as unpinned (dashed border) until accepted
  - After pinning: Become solid blue with 🔒 icon
  - Existing pinned visits remain unchanged (solid blue, locked)

#### GraphQL Operations Required

**Queries:**

- `prePlanningData(timeHorizon)` - Get all schedules, visits, employees for planning horizon
- `supplyDemandBalance(timeHorizon)` - Get supply/demand metrics
- `demandCurve(timeHorizon)` - Get demand trend data
- `unusedHours(timeHorizon)` - Get unused hours analysis
- `getOptimalPlacementRecommendations(visitInput)` - Get AI recommendations

**Mutations:**

- `createMovableVisit(input)` - Create new recurring visit
- `updateMovableVisit(id, input)` - Update existing movable visit
- `runPrePlanningOptimization(input)` - Trigger optimization
- `acceptPrePlanningSolution(input)` - Pin approved visits

**Subscriptions:**

- `prePlanningProgress(jobId)` - Real-time optimization progress

#### Bryntum Configuration Examples

**Consolidated Schedule View:**

```javascript
{
  viewPreset: 'weekAndMonth', // Multi-week view
  startDate: planningWindowStart,
  endDate: planningWindowEnd,
  resources: employees, // All employees
  events: allVisits, // Pinned + unpinned
  features: {
    eventTooltip: true,
    eventEdit: true,
    drag: {
      constrainDragToResource: false, // Allow moving between weeks
    },
    timeRanges: {
      // Show periods where unused client allocation could be recaptured
      data: unusedAllocationPeriods.map(period => ({
        resourceId: period.employeeId,
        startDate: period.startTime,
        endDate: period.endTime,
        name: `Unused allocation: ${period.hours}h`,
        cls: 'unused-allocation-period',
      })),
    },
  },
  columns: [
    { text: 'Employee', field: 'name', width: 150 },
    {
      text: 'Unused Allocation',
      field: 'unusedHours',
      width: 120,
      renderer: ({ record }) => {
        const hours = record.unusedHours || 0; // Client's unused allocation hours
        const color = hours > 5 ? 'red' : hours > 2 ? 'orange' : 'green';
        return `<span style="color: ${color}">${hours.toFixed(1)}h</span>`;
      },
    },
  ],
}
```

**Pinned vs Unpinned Styling:**

```javascript
eventRenderer: ({ eventRecord }) => {
  const isPinned = eventRecord.pinned;
  return {
    style: isPinned
      ? "background: #3b82f6; color: white;" // Solid blue for pinned
      : "border: 2px dashed #10b981; background: white;", // Dashed green for unpinned
    icon: isPinned ? "🔒" : "", // Lock icon for pinned
  };
};
```

#### Acceptance Criteria

- [ ] Pre-planning hub displays consolidated schedules across time horizon
- [ ] Time horizon selector works (1 week, 1 month, 3 months, custom)
- [ ] Movable visits can be created with all required fields
- [ ] Movable visits appear in unassigned panel after creation
- [ ] Pinned visits show 🔒 icon and solid blue background
- [ ] Unpinned visits show dashed border
- [ ] Pre-planning optimization runs and shows progress via WebSocket
- [ ] Diff view clearly shows optimized changes (ghost tracks + solid blocks)
- [ ] Supply/demand balance dashboard displays correctly with color coding
- [ ] Unused hours are visible as badges, overlays, and in tooltips
- [ ] Unused hours toggle works (show/hide)
- [ ] Demand curve shows trends over time
- [ ] Recommendations panel displays AI suggestions
- [ ] Recommendations can be clicked to auto-fill visit configuration
- [ ] New movable visits can be added without disrupting pinned patterns
- [ ] Accept/pin workflow updates visits correctly
- [ ] Schedule health metrics display correctly
- [ ] Long-term health tracking shows trends
- [ ] All interactions work smoothly with 100+ employees and 1000+ visits across 3-month horizon

---

### Phase 10: Export & Reporting

**Task:** Implement export and reporting features

**Primary Bryntum Examples to Reference:**

- **Export** - https://bryntum.com/products/schedulerpro/examples-scheduler/export/ (PDF export)
- **Print** - https://bryntum.com/products/schedulerpro/examples-scheduler/print/ (Print functionality)
- **Export to Excel** - https://bryntum.com/products/schedulerpro/examples-scheduler/exporttoexcel/ (Excel export)
- **Export to iCalendar** - https://bryntum.com/products/schedulerpro/examples-scheduler/exporttoics/ (iCal export)

**Features Required:**

- Export to PDF
- Export to Excel
- Print functionality
- Export to iCalendar (optional)

**Acceptance Criteria:**

- [ ] All export formats work correctly
- [ ] Exported data is accurate
- [ ] Print layout is professional

---

### Phase 11: Testing & Documentation

**Task:** Comprehensive testing and documentation

**Deliverables:**

- Unit tests for critical functions
- Integration tests for API interactions
- E2E tests for key workflows
- Performance testing
- Documentation (setup, API integration, customization)

**Acceptance Criteria:**

- [ ] Test coverage >80% for critical paths
- [ ] All tests passing
- [ ] Performance benchmarks met
- [ ] Documentation complete

---

## Deliverables

### Code Deliverables

1. **Bryntum SchedulerPro Components**
   - Main calendar component
   - All feature components (filters, charts, modals, etc.)
   - Mapper functions (backend data → Bryntum format)
   - Type definitions

2. **GraphQL Integration**
   - Apollo Client setup
   - Query/mutation/subscription hooks
   - Error handling
   - Loading states

3. **State Management**
   - Schedule state management
   - Filter state
   - UI state (modals, panels, etc.)

4. **Styling**
   - Tailwind CSS integration
   - Custom Bryntum themes
   - Responsive design
   - Swedish localization

### Documentation Deliverables

1. **Technical Documentation**
   - Architecture overview
   - Component structure
   - Data flow diagrams
   - API integration patterns

2. **User Documentation**
   - Feature usage guide
   - Customization options
   - Troubleshooting common issues
   - Performance optimization tips

---

## Acceptance Criteria

### Functional Requirements

- [ ] Calendar loads real schedule data from GraphQL
- [ ] All visits and employees display correctly
- [ ] Drag-and-drop assignment works and saves to database
- [ ] Visit editing (time, duration) saves to database
- [ ] Optimization triggers Timefold job via GraphQL
- [ ] Real-time progress updates during optimization
- [ ] Calendar updates automatically when solution arrives
- [ ] All filters work with real data
- [ ] Metrics panel shows accurate KPIs
- [ ] Metrics tooltips display individual metrics (employee and client level)
- [ ] Visual indicators toggle works (show/hide indicators on resources and events)
- [ ] Metrics modal opens and displays all clients and employees with complete metrics tables
- [ ] Client profitability indicators display correctly (unprofitable clients, high travel/wait ratios)
- [ ] Comparison mode works with real schedules
- [ ] Pre-planning features work correctly (see Phase 9 acceptance criteria)
- [ ] Swedish localization preserved
- [ ] All visual indicators display correctly

### Non-Functional Requirements

- [ ] Type-safe throughout (no `any` types)
- [ ] Error handling for all operations
- [ ] Loading states for async operations
- [ ] Performance: <200ms for GraphQL queries
- [ ] No console errors or warnings
- [ ] Responsive design maintained
- [ ] Accessibility standards met

### Code Quality

- [ ] TypeScript strict mode passes
- [ ] ESLint passes with no errors
- [ ] Unit test coverage >80%
- [ ] Integration tests for critical flows
- [ ] Code follows project conventions
- [ ] Comments on complex logic

---

## Dependencies & Prerequisites

### Provided by Caire

- ✅ GraphQL API (to be provided during project)
- ✅ Database schema documentation
- ✅ API documentation (see `BRYNTUM_BACKEND_SPEC.md`)
- ✅ Design system and visual specifications

### Required from Consultant

- ✅ Access to development environment
- ✅ Node.js 18+ and npm/pnpm
- ✅ Git access to repository
- ✅ Development API credentials
- ✅ Understanding of GraphQL and React

---

## Risk Assessment

### Low Risk

- ✅ Data model is normalized (straightforward mapping)
- ✅ GraphQL API follows standard patterns
- ✅ Clear requirements and acceptance criteria

### Medium Risk

- ⚠️ GraphQL API may need adjustments during integration
- ⚠️ Performance with large datasets (1000+ visits)
- ⚠️ Real-time subscription stability

### Mitigation

- Regular communication and API reviews
- Performance testing with realistic data volumes
- Fallback to polling if WebSocket issues occur

---

## Questions for Clarification

Before providing a quote, please confirm understanding of:

1. **Feature Scope:** All features listed in this PRD are required
2. **Bryntum Examples:** You will reference the provided Bryntum examples for implementation patterns
3. **Backend API:** GraphQL API will be provided during project (detailed specs in `BRYNTUM_BACKEND_SPEC.md`)
4. **Data Volumes:** Typical daily schedules per service area have 10-30 employees and 100-500 visits. An enterprise organization can have 5000 employees
5. **Performance Requirements:** Calendar should load in <2 seconds, interactions should feel instant
6. **Browser Support:** Modern browsers (Chrome, Firefox, Safari, Edge - latest 2 versions)
7. **Mobile Support:** Desktop-first, responsive design preferred but not critical
8. **Testing Requirements:** Unit tests for critical functions, integration tests for API, E2E for key workflows
9. **Code Quality:** TypeScript strict mode, ESLint compliance, following Bryntum best practices
10. **Documentation:** Technical documentation and user guide required

---

## Next Steps

1. **Review this PRD** and confirm understanding
2. **Review Backend Spec** (`BRYNTUM_BACKEND_SPEC.md`) for API details
3. **Provide Quote** with timeline and cost estimate
4. **Schedule Kickoff** meeting to discuss details
5. **Begin Implementation** once approved

---

## Contact & References

**Related Documentation:**

- **`BRYNTUM_BACKEND_SPEC.md`** - ⭐ **BACKEND REFERENCE** - Complete backend API specifications, data flow, mappers, and metrics
- **`bryntum-reference.md`** - ⭐ **PRIMARY REFERENCE** - Complete guide with all Bryntum examples mapped to Caire features, implementation patterns, and example catalogue with links
- **`Feature PRD – Bryntum Calendar View.md`** - Product requirements, user stories, and acceptance criteria
- **`API_DESIGN_V2.md`** - Backend API specification (high-level, detailed schema to be provided during project)

**Key Reference Documents:**

- The `BRYNTUM_BACKEND_SPEC.md` document contains all backend API specifications, data flow patterns, mapper requirements, and metrics calculations.
- The `bryntum-reference.md` document is the primary technical reference for Bryntum implementation patterns.

**Questions?** Please reach out for clarification on any aspect of this PRD.

---
