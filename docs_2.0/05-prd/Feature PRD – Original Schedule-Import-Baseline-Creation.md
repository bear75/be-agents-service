# Feature PRD – Original Schedule Import & Baseline Creation

## Overview

This feature enables a scheduler to import an existing schedule from an external system (e.g. Carefox) or file, validate and map the data into CAIRE's normalised schema, create an Original schedule record, and optionally generate a Baseline schedule for comparison. It forms the starting point for optimisation and schedule comparison workflows.

## Goals & Scope

- Provide a self‑service import process for schedulers to upload or fetch source schedules.

- Validate incoming data to ensure required fields (visits, employees, clients, service areas, time windows) are present and consistent.

- Map external schemas to internal entities (visit templates, clients, employees) and persist them using the new data model.

- Create a schedule record of type `original` with flexible time windows and associate it with a domain‑level problem.

- Optionally derive a baseline schedule with fixed times from the same data, linked to the original schedule for side‑by‑side comparison.

- Support both API‑driven and UI‑driven workflows; expose GraphQL mutations and a front‑end wizard.

- Trigger an optimisation job on the original schedule if requested.

- Ensure multi‑tenant isolation and permission checks.

In addition, when a baseline schedule exists and contains a manually crafted or planned solution (e.g. from Carefox), the system should allow users to treat that baseline as a schedule template (Slinga) and use it as the starting point for fine‑tuning. This enables schedulers to apply small adjustments—either manually or via the solver—without starting optimisation from scratch.

The importer must also handle cases where the external data does not include information about the underlying `visit_template` (movable visit). In these cases CAIRE should automatically generate a placeholder `visit_template` (with status `undefined` or `placeholder`), link the imported visit to it and inform the user that further action is required. Users should be able to manually provide the missing frequency/pattern via the UI or by uploading the original kommunbeslut (e.g. PDF) and running a pre‑planning job to derive the correct movable visit context. The system should support running pre‑planning over a date range (e.g. weekly, bi‑weekly or monthly) to detect recurring patterns in the imported data and propose the appropriate movable visit definitions. These operations may occur after the initial import and are outside the critical path of the nightly batch import.

## User Stories

- **As a Scheduler**, I want to import my organisation's current schedule from Carefox or a CSV/JSON file so that I can optimise it with CAIRE.

- **As a Scheduler**, I want to preview the imported data and correct mapping issues before creating the schedule to prevent errors downstream.

- **As a Scheduler**, I want CAIRE to create a baseline schedule using the exact planned times from the source system so I can compare it to the optimised schedule.

- **As a Scheduler**, I want the system to kick off optimisation immediately after import (optional) so I don't have to trigger it separately.

- **As an Admin**, I want to control which users have permission to import schedules and view imported data.

## Workflow & Interaction

### UI Flow

1. **Select import source** – user chooses "Carefox", "CSV/JSON file" or another supported system. The system requests necessary credentials or file upload.

2. **Fetch/Upload & Parse** – the API retrieves the external data or parses the uploaded file. A preview of visits, employees and clients is displayed. The user can adjust mappings (e.g. assign service areas, fix employee names).

3. **Validation** – the system validates required fields (see Validation section). Errors or warnings are shown for missing or inconsistent data.

4. **Create Original Schedule** – upon confirmation, the API:
   - Creates or updates `clients`, `employees`, `service_areas` and `visit_templates` as needed.
   - Creates a `problem` record representing the imported visits, employees and constraints.
   - Creates a `schedule` record of type `original` linked to the problem, scenario and solver configuration.
   - Generates `visits` for the imported data with flexible windows.
   - For each imported visit without a movable visit context, create a placeholder `visit_template` with status `undefined` and link the visit to it. This placeholder indicates that the visit needs frequency and pattern information and can be updated later via pre‑planning or manual entry.
   - If the importer cannot attach a visit to an existing `visit_template`, it should mark the placeholder with a special status (`undefined` or `placeholder`) so the scheduler is informed that the data is incomplete. In the daily schedule UI this status should be clearly visible. The scheduler can later run pre‑planning or upload a kommunbeslut PDF to fill in the missing information, as described below.

5. **Baseline Option** – if the user requests a baseline:
   - Derive a baseline problem from the original (set `preferred_window_start = allowed_window_start = scheduled start time` for each visit).
   - Create a `schedule` record of type `baseline` linked to the original schedule.
   - Mark baseline status as "ready" for comparison.

6. **Handle Missing Movable Visit Contexts** – after the original and baseline schedules are created, the system should provide several mechanisms to enrich visits whose movable visit context is undefined:
   - **Manual Update**: The scheduler can open a visit detail and fill in the missing frequency/pattern information (e.g. weekly, bi‑weekly, monthly), which updates the `visit_template` from `undefined` to `draft`.
   - **Pre‑Planning via PDF**: If the organisation has a kommunbeslut document (PDF) that specifies the client's visit plan, the scheduler can upload it and trigger a pre‑planning job for a relevant date range. This job analyses existing visits (including those imported from the external system) and creates proper `visit_templates` with suggested frequencies. The imported visits are updated accordingly.
   - **Automatic Pattern Detection**: The scheduler can run a pre‑planning job without a PDF to detect recurring visit patterns across the time horizon (e.g. using slingor and schedule groups). The system will suggest movable visit contexts (e.g. "this visit occurs every Thursday") and create or update `visit_templates` accordingly.
   - **Apply Slinga Template**: If a slinga template exists for that weekday, the scheduler can choose to apply it to the problem, which populates the missing movable visit context and assignments.

   These mechanisms can be executed at any time after import—either immediately in the wizard or later from the schedule detail view—and are not required to complete the initial import. Nightly batch jobs will typically import schedules and place visits with missing context into the current day view; schedulers will then resolve missing contexts as part of their daily workflow.

7. **Determine Working View** – when opening a schedule, the UI should determine the most appropriate base view:
   - If a baseline schedule exists, present the baseline (Slinga) as the default view. This represents what was planned or the most recent manual solution. All fine‑tuning actions (manual edits or optimisation) start from this baseline.
   - If no baseline exists but a Slinga template is available for the schedule's weekday, offer the option to apply the template. This populates visits and assignments according to the template and allows further editing.
   - If neither baseline nor template is present, display the imported problem in its unplanned state (flexible windows) and allow the scheduler to edit and optimise it directly.

8. **Optimise or Fine‑Tune Any View** – regardless of which view is active (baseline, template, unplanned problem or a revision), the scheduler can:
   - Optimise the schedule using the solver with a selected scenario and solver configuration. For baseline and template views, the solver will consider existing assignments as a starting point via the `from‑patch` endpoint.
   - Edit manually and save the changes as a new revision (solution). These edits may include drag‑and‑drop of visits, reassignments or time adjustments.
   - Apply scenarios and insert movable visits as needed. The system should support applying different scenarios, adding or removing movable visits and comparing outcomes.
   - Compare the current view against previous solutions (baseline, original optimisation, other revisions).

9. **Kick off Optimisation** (optional) – if the user ticks "optimise immediately" at import time, the server submits the original schedule's problem to the solver, creates an optimisation job and subscribes the client for progress updates.

### API Endpoints / GraphQL Schema

**Mutation: `importOriginalSchedule(source: ImportSourceInput!): ImportSchedulePayload`**

- **Inputs**: source credentials or file upload, scenario ID, solver config ID, baseline flag, optimise flag.
- **Process**: calls the appropriate importer service, validates data, persists domain entities, creates schedules, triggers optimisation if requested.
- **Outputs**: IDs of the created problem, original schedule, baseline schedule (if applicable), and optimisation job ID.

**Query: `previewImport(source: ImportSourceInput!): ImportPreview`**

- Allows the UI to fetch a preview of the external data for mapping and validation before creating anything.

**Types:**

- Define `ImportSourceInput` (e.g. `{ type: "Carefox", credentials: {...} }` or `{ type: "File", fileId: "..."}`), `ImportPreview` (lists of visits, employees, clients with mapping status), and `ImportSchedulePayload` (IDs of created resources and job status).

### Validation Rules

- A schedule must belong to an existing organisation and scenario.

- Each visit must reference a client (creating a new client if necessary) and contain duration and at least one of `preferred_window_start`/`allowed_window_start` and `preferred_window_end`/`allowed_window_end`.

- Employee identifiers (ID or external ID) must map to existing employees or create new ones with default attributes.

- Service areas must either exist or be created with a default salary and continuity threshold.

- If a baseline is requested, all visits must have a fixed planned start time; otherwise warn the user.

- Visits imported without a movable visit context must either be linked to an existing `visit_template` or cause the importer to create a placeholder template with status `undefined`. The system should alert the scheduler to fill in the frequency and pattern information for these placeholders.

### Data Model Mapping

- **visit_templates**: For each imported task, create or update a `visit_template` record storing frequency (e.g. daily/weekly), duration, required staff, preferred and allowed time windows, priority and notes. Link to the appropriate client and `service_area`. If the import does not provide frequency information, create a placeholder template with status `undefined` and minimal fields; this placeholder can later be completed manually or via pre‑planning.

- **clients**: Create or update client records with contact details and municipality information. Use addresses to geocode the location if provided.

- **employees**: Create or update employees based on external IDs, names and skills. Store contract type and salary if provided.

- **problem & schedule**: Create a `problem` record summarising the import and a `schedule` of type `original` referencing the problem, scenario and solver config. Each imported visit becomes a `visit` linked to the problem and schedule with flexible windows.

- **baseline schedule**: If requested, create a second problem derived from the first by fixing windows, and a `schedule` of type `baseline` referencing the derived problem. Do not duplicate clients or employees; reuse the same records.

### Integration & External Services

- **Carefox API Client**: Implement a service to authenticate with Carefox, fetch schedule data, map fields to CAIRE's visit/employees/clients and handle paging.

- **CSV/JSON Parser**: Support uploading a file (via GraphQL file upload or REST endpoint) and parse it into the internal data structures. Provide a preview to the UI.

- **Solver Integration**: Use the existing solver client to send the original problem to Timefold. The job ID and dataset ID should be stored in the solutions table once the solver returns.

- **Authentication & Authorization**: Ensure the user making the request is a member of the organisation and has permission to create schedules. Use Clerk JWTs to determine context.

### UI Requirements

- **Import Wizard**: Multi‑step form guiding the scheduler through source selection, data mapping/preview, validation and confirmation.

- **Error Handling**: Display validation errors with actionable messages; allow the user to fix issues before proceeding.

- **Progress Indicators**: Show a spinner or progress bar during data fetch and import. If optimisation is triggered, display job status via a subscription.

- **Schedule List & Detail**: After import, the new schedules appear in the schedule list with status (e.g. Draft, Baseline, Optimising). Clicking a schedule opens its detail page with visits, metrics and actions (run optimisation, create baseline, compare baseline, delete).

- **Daily Calendar View**: Most imports will occur via nightly batch jobs. When a scheduler logs in during the day they should land directly on the calendar view showing the current day's schedule (last revision of baseline or optimisation). Visits with missing movable context should be flagged (e.g. coloured or badged) so the scheduler knows additional information is required. The import wizard UI can be hidden or minimised in this default view; focus is on managing and adjusting the schedule rather than monitoring import progress.

- **Baseline Fine‑Tune Controls**: On a baseline schedule's detail page, provide a "Fine‑Tune" button that opens the baseline in editable form. Users can adjust visit times or assignments and either save manually or run a patch‑based optimisation. Changes should be visualised on the calendar and captured in a new solution record.

### Acceptance Criteria

- Users with the scheduler role can successfully import a schedule from Carefox or file into their organisation.

- Imported data is persisted in normalised tables (`clients`, `employees`, `visit_templates`, `service_areas`, `visits`, `problems`, `schedules`). No raw JSON is stored internally.

- The system generates an original schedule of type `draft` with flexible windows and, if requested, a baseline schedule with fixed times. Baseline schedules are linked to their original schedule for comparison.

- The UI displays imported data for preview and allows mapping corrections before final creation.

- Validation errors (missing clients, invalid time windows, unknown employees) are surfaced to the user and prevent schedule creation until resolved.

- If "optimise immediately" is selected, the system enqueues an optimisation job and updates the schedule status to `running`. A subscription event notifies the UI upon completion.

- Permissions are enforced: only authorised users can import schedules; imported schedules are visible only to their organisation.

- The feature includes unit tests for the importer services, validation logic and schedule creation, and integration tests for the GraphQL mutations.

- For visits without an associated movable visit context, the importer creates placeholder templates with status `undefined` or `placeholder`, links visits to them and surfaces these missing contexts in the UI. Users can run pre‑planning jobs or manually update the templates to convert them to valid movable visit definitions.

- The scheduler can upload a kommunbeslut (PDF) and trigger a pre‑planning job that analyses existing visits and generates suggested movable visit contexts.

- The scheduler can run an automatic pattern detection pre‑planning job without a PDF to identify recurring visit patterns and update `visit_templates` accordingly.

- The UI clearly flags visits with unresolved movable contexts and provides actions to resolve them, and the default calendar view shows the current day's schedule rather than the import progress UI.

### Future Enhancements

- **Additional import sources**: Add mappers for eCare, Parasol, Combine and other systems using the same import workflow.

- **Batch Import**: Allow importing multiple schedules at once and showing aggregated progress.

- **Conflict Resolution**: Provide tools for reconciling overlapping visit templates or duplicate employees during import.

- **Auto‑mapping Improvements**: Incorporate AI or fuzzy matching to improve mapping accuracy without user intervention.

- **Localization**: Support Swedish and English localisations for field labels, error messages and date/time formats.

### UI Mockups & Wireframes

To ensure a user‑friendly experience, design mockups and wireframes should be created for this feature. These mockups should reflect the following screens and components:

**Import Wizard**: A multi‑step modal or page guiding the scheduler through source selection, data preview/mapping, validation and confirmation. Include a progress indicator and clear error states. Use Bryntum's grid/table components to display preview data (visits, employees, clients) with inline editing for mapping corrections.

**Schedule List Page**: A dashboard listing schedules with columns for type (Original, Baseline), date/horizon, status (Draft, Optimising, Complete), scenario and solver config. Provide actions (View, Optimise, Fine‑Tune, Delete) as buttons or dropdowns. Consider a filter by organisation, scenario or date range.

**Schedule Detail Page**: A page or tabbed view showing:

- **Calendar/Timeline View**: Use Bryntum Scheduler or Calendar components to visualise visits across employees and time. For the baseline fine‑tune view, enable drag‑and‑drop editing of visits and display conflicts.

- **Metrics Panel**: Summarise KPIs such as visit count, travel time, utilisation, costs and revenues. Compare original vs. baseline vs. optimised metrics when available.

- **Actions Panel**: Buttons to run optimisation, create baseline, fine‑tune from baseline, compare schedules and delete.

**Baseline Fine‑Tune Modal/Page**: When a scheduler clicks "Fine‑Tune," open a detailed calendar view of the baseline schedule. Allow dragging visits to new times, reassigning caregivers, editing durations or marking visits as optional. Provide "Save As Baseline Solution" and "Optimise Changes" buttons. If the user chooses optimisation, call the `from‑patch` endpoint with the differences.

When creating these mockups, provide annotations describing the intended user interactions and link to specific Bryntum components (e.g. SchedulerPro, CalendarPro) that should be used. These designs will serve as a prompt for UX/UI tools such as Figma, Lovable or Miro.

---

This feature PRD is intended as a detailed specification for engineers refactoring the Original Schedule Import & Baseline Creation functionality. It should be reviewed alongside the architecture and data model documents to ensure alignment. As implementation progresses, update this PRD to reflect decisions, constraints and lessons learned.

---
