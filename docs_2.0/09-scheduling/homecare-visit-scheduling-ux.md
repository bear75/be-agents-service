# Executive Summary

Best practices for Swedish home care (hemtjänst) visit scheduling UX center on providing planners with a clear, at-a-glance, and highly functional interface to manage complex daily operations, often involving over 50-100 visits for 20-30 employees. The core of an effective UX is a dispatcher-style calendar or Gantt view that prioritizes visual clarity and information hierarchy. This view must immediately surface critical operational data, including route feasibility with travel times, staff availability, and real-time visit statuses. A key design principle is the strategic separation of information: essential details like client name, visit type, and critical alerts appear directly on visit 'tiles', while comprehensive data such as full care plans and access instructions are housed in non-disruptive side panels or modals. Critical visual indicators for planners include alerts for scheduling conflicts (e.g., overlaps, insufficient travel time), competence mismatches, and violations of labor rules. The UX must also be tailored to the Swedish context, visually distinguishing between social care (SoL) and healthcare (HSL) interventions and often structuring tasks according to the IBIC (Individens Behov i Centrum) framework. Leading Nordic vendors emphasize features that support realistic planning, continuity of care, and seamless communication of schedule changes to field staff via push notifications.

# Key Ux Recommendations

Here is a detailed list of actionable recommendations for designing an effective home care scheduling user experience:

- **Calendar/Gantt View Design:**
  - Utilize a Gantt-style layout with dedicated horizontal lanes for each employee to clearly visualize their daily schedule.
  - Implement intuitive drag-and-drop functionality for rescheduling visits.
  - Display visual overlays or distinct indicators for scheduling conflicts, such as overlapping visits or insufficient travel time.
  - Include a 'current time' line that moves across the schedule to provide real-time context.
  - Provide quick-filter 'chips' to allow planners to easily toggle views by intervention type (SoL/HSL), skill requirement, geographic zone (indelning), or continuity status.
  - Integrate a route preview feature that visually displays travel segments and buffer times between visits.

- **Visit Tile (Card) Information Hierarchy:**
  - **Visible at a Glance:** Display start/end time and duration, client name, staffing requirement (e.g., 1x/2x icons), and a short address or zone cue.
  - **Use Icons and Badges:** Employ icons for visit categories (e.g., personal care, service), required skills (e.g., delegated HSL task), and risks (e.g., fall risk). Use badges to indicate continuity status (met/unmet) and warnings.
  - **Travel Information:** Show the mode of transport (fädsätt) icon and the estimated time of arrival (ETA) to the next visit.
  - **Color Coding:** Use color to denote visit category, real-time status (e.g., scheduled, in progress, completed, delayed), or urgency.

- **Side Panel / Modal for Detailed Information:**
  - Consolidate comprehensive details here to keep the main view clean. Include the full client address with a map link and specific access notes (e.g., door codes, key location).
  - Provide a detailed checklist of tasks, ideally mapped to the Swedish IBIC framework's need areas.
  - List specifics on delegated tasks, medication administration, required equipment (e.g., lifts), client preferences, safety plans, and language needs.
  - Offer access to linked documents, care plan authorizations, and historical visit documentation.

- **Global Indicators and Dashboards:**
  - Implement capacity heatmaps or visit counters per hour/zone to visualize workload distribution.
  - Display a dashboard or meter tracking compliance with labor rules (e.g., overtime limits, required rest breaks).
  - Provide high-level continuity scorecards for clients or the entire unit.
  - Maintain a clear list or queue for unscheduled orders and pending schedule changes that need to be pushed to staff mobile devices.

- **Swedish-Specific Customizations:**
  - Incorporate filtering and iconography to clearly distinguish between SoL (social care) and HSL (healthcare) tasks.
  - Structure task lists within the visit details to align with IBIC need areas.
  - Implement automated warnings for staff whose delegations or specific authorizations are nearing expiration.
  - Support the inclusion of relevant classification codes like KVÅ where applicable for HSL tasks.

# Scheduler Calendar View Essentials

For a human scheduler managing Swedish home care (hemtjänst), the main calendar or Gantt-style view must provide a comprehensive, at-a-glance overview of the day's operations. This includes several essential information layers. Firstly, each staff member should have a dedicated resource lane, clearly displaying their real-time status such as being on-shift, on a break, absent, or otherwise unavailable, with a current time marker moving across the view. Within these lanes, individual visits are represented as time blocks, sized proportionally to their duration with explicit start and end times. Each block must show the client's name and a short identifier. To manage routes effectively, the view must visualize the travel segments between visits, including the estimated travel time, the mode of transport (fårdsätt), and the start/end location for each staff member's route. Secondly, the view needs to incorporate critical operational context through visual cues. This involves using color-coding or icons to denote the intervention category (e.g., social care/SoL vs. healthcare/HSL) and flags for special requirements like double staffing, lift usage, or medication administration. Thirdly, the system must surface alerts and capacity indicators directly on the calendar. This includes inline warnings on visit tiles or staff lanes for issues like scheduling overlaps, insufficient travel time, competence mismatches, out-of-zone assignments, labor rule violations (e.g., overtime), and unconfirmed visits. Capacity cues, such as a visual density/heat map or a simple count of visits per hour, along with Key Performance Indicators (KPIs) like planned vs. available time, are crucial. A continuity indicator showing if a preferred caregiver is assigned is also essential. Finally, the interface must be interactive, featuring quick filters to toggle the view by date range (day/week), organizational unit or zone, intervention category, required skills, continuity status, and vehicle type.

# Visit Card Information Hierarchy

## At A Glance Info

On a compact visit card or tile, the most critical information must be immediately visible to allow for rapid assessment and decision-making. This includes the visit's start and end time, total duration, and its live status (e.g., scheduled, en route, started, completed, missed). The client's name is essential, often accompanied by a short address cue like the street name or area, especially if the visit is outside the usual zone. Key operational details should be conveyed through icons to save space, such as icons for the intervention category (e.g., SoL, HSL), staffing needs (e.g., 1x for single staff, 2x for double staffing), and any required skills or authorizations (like 'delegerad HSL' for delegated healthcare tasks). A continuity badge indicating if the assigned caregiver meets the client's preference is also vital. To aid in route planning, the card should display the estimated travel time (ETA) to the next visit, a buffer indicator, and an icon for the mode of transport (fårdsätt). Finally, any urgent warnings, such as a risk flag for fall risks, key access issues, or alarms, should be present as prominent icons, often with tooltips for a brief explanation.

## Detailed View Info

Comprehensive information that is not required for immediate, at-a-glance understanding should be accessible upon interaction, such as clicking the visit card to open a side panel or modal window. This detailed view contains all necessary information for the caregiver to perform the visit correctly and safely. It includes the full client address with a map, specific notes on the entrance or door, and any access details like a lockbox or Phoniro digital key code, along with parking instructions. The core of the detailed view is the full breakdown of tasks, often structured according to the IBIC (Individens behov i centrum) framework, with specific instructions for each intervention. For healthcare tasks, this section includes delegation details, medication lists, and relevant KVÅ/HSL codes. It also houses crucial client-specific information such as personal preferences, continuity history, language or gender preferences, detailed safety plans, allergy information, infection control protocols, and specifics on required equipment like lifts. Lastly, this area provides administrative context, linking to the original service orders or authorizations, care plan periods, historical documentation, and tools for time reporting and logging exceptions.

# Critical Visual Indicators For Planners

## Status Indicators

To provide real-time operational awareness, the system must use clear visual cues for visit status. This is typically achieved through color-coding or distinct icons on the visit tiles. Key statuses to indicate include 'unconfirmed' or 'scheduled', 'en route', 'in-progress' or 'started', 'completed', 'late' or 'delayed', and 'missed'. Additionally, indicators should flag when a caregiver has missed a check-in for a visit or when an urgent push update with a schedule change has been sent but not yet acknowledged by the caregiver. Events triggered by clients, such as a 'trygghetslarm' (safety alarm), also require a unique and highly visible indicator to prompt immediate action from the planner.

## Conflict Alerts

Prominent, impossible-to-miss alerts are essential for preventing scheduling errors. These indicators should flag any logistical conflicts directly on the calendar view. Common conflicts include overlapping visits for the same staff member, double-booking a client, or failing to assign a second staff member for a visit explicitly marked as requiring 'dubbelbemanning' (double staffing). Route feasibility warnings are also critical, such as alerts for insufficient travel time between visits based on the calculated route and mode of transport (fårdsätt), or violations of zone boundaries. The system should also flag violations of labor rules, such as exceeding overtime limits, insufficient rest breaks between shifts, or other union agreement constraints, which are often imported from staffing systems like CGI Heroma.

## Qualification Warnings

To ensure safety, compliance, and quality of care, the system must provide clear warnings for any mismatch between the visit's requirements and the assigned employee's qualifications. This includes flagging when a caregiver is assigned to a task for which they lack the necessary skill or certification. A particularly critical warning is for assignments involving delegated healthcare tasks (delegerade HSL-insatser), where the system should verify and flag if the caregiver's specific delegation is expired or not valid for that particular task. These warnings help the planner quickly identify and rectify potentially non-compliant or unsafe assignments.

## Client Specific Flags

To support person-centered care, visual tags or icons should be used to highlight important client-specific information that impacts scheduling or service delivery. This includes flags for critical safety information, such as fall risks, the presence of pets that may affect caregivers, or specific allergies. Icons can also denote special access needs, such as requirements for a key, a digital lock code (e.g., Phoniro), or specific instructions for entering the home. A continuity flag or badge is also crucial, indicating whether the assigned caregiver is the client's preferred or a regular caregiver, helping the planner to optimize for client satisfaction and quality of care.

# Swedish Hemtjanst Intervention Categories

## Legal Frameworks

Interventions in Swedish home care are governed by two primary legal acts. The Social Services Act (Socialtjänstlagen, SoL) covers social care and support to ensure individuals have a reasonable quality of life. The Health and Medical Services Act (Hälso- och sjukvårdslagen, HSL) governs healthcare tasks. Municipalities are responsible for planning and providing interventions under both frameworks, often distinguishing between them in their decision-making and IT systems.

## Guiding Model

The national model 'Individens behov i centrum' (IBIC), or its predecessor ÄBIC, serves as a guiding framework for needs assessment and intervention planning. Developed by the National Board of Health and Welfare (Socialstyrelsen), its intention is to create more equitable and consistent decisions across municipalities. It provides a structured way to document an individual's needs and map them to specific interventions, which facilitates national data collection and analysis.

## Personal Care Tasks

This category, known as 'personlig omvårdnad,' falls under the Social Services Act (SoL). It includes tasks that are fundamental to personal well-being and daily life. Examples provided in the context include assistance with personal hygiene, dressing and undressing ('på/avklädning'), mobility support and transfers ('förflyttning'), and support with meals ('måltidsstöd').

## Service Tasks

Also governed by the Social Services Act (SoL), 'serviceinsatser' are practical support tasks that enable an individual to manage their home and daily life. Common examples include cleaning ('städ'), laundry ('tvätt'), shopping ('inköp'), and running errands ('ärenden'). This category can also encompass safety alarms ('trygghetslarm'), social support and activities, respite care for family members ('avlösning'), general supervision ('tillsyn'), and meal delivery ('matdistribution').

## Delegated Healthcare Tasks

These are healthcare tasks that are delegated from registered nurses to home care staff under the authority of the Health and Medical Services Act (HSL). These 'delegerade insatser' require specific authorization and documentation. Common examples include medication administration ('läkemedelshantering') and simple wound care ('såromläggning'). These tasks are often coded with KVÅ (Classification of Health Care Measures) codes where applicable and require careful planning to ensure staff have the correct and valid delegation for the task at hand.

# Nordic Scheduling System Analysis

## System Name

Pulsen Combine (Combine Plan)

## Scheduler View Features

The scheduler view is designed for 'realistic planning,' incorporating parameters like travel time ('restid'), vehicle type ('färdsätt'), double staffing, and continuity. It features a Gantt-style view where planners can manually adjust schedules and plan for extra interventions. The system displays warnings for rule violations, such as booking staff without the required competence. It also provides overview reports showing the daily plan for all staff in a unit, allowing for a high-level assessment of resource allocation.

## Visit Card Design

While not explicitly detailed, the visit card on the scheduler would logically display key planning parameters such as the assigned staff, visit duration, intervention type, and any warnings related to competence or continuity. Given the emphasis on travel, it likely shows travel segments between visits.

## Mobile App Experience

The mobile experience is tightly integrated with the planning console. Field staff receive push notifications about any changes to their work schedule, ensuring they always have the most up-to-date information. This real-time communication is critical for managing the dynamic nature of home care.

## Key Differentiators

A key differentiator is its focus on highly realistic and detailed planning, calculating travel time based on the specific mode of transport and allowing manual overrides for real-world conditions like traffic or weather. It has strong, unique functions for matching client needs with staff competencies and prioritizing caregiver continuity. The system's built-in warning functions and push notifications for schedule changes are also notable features.

## System Name

Tietoevry Lifecare (Planering/Service Planner)

## Scheduler View Features

This system provides clear, intuitive calendar views for personnel and facilities. The staff schedule view includes critical details like start/end addresses, transport mode ('färdsätt'), and planned breaks or ancillary time ('kringtider'). A major feature is its ability to import schedules from dedicated staffing systems like CGI Heroma and Time Care, which ensures that visit planning aligns with complex labor rules, union agreements, and staff absences.

## Visit Card Design

The visit cards are part of an easy-to-use interface designed to reduce planner stress. They would display shift information and visit details within the clear calendar views, likely color-coded or icon-driven to represent different visit types or statuses.

## Mobile App Experience

The system aims to provide a unified mobile application where personnel can easily see all relevant information in one place, including shift details and resource availability, consolidating data from different backend systems.

## Key Differentiators

Its primary differentiator is its strong integration capability, particularly with schema-intensive staffing systems. This allows for robust resource management that respects labor rules and real-time staff availability. By collecting and presenting resource data from various systems in a uniform format, it serves as a central hub for time management and planning.

## System Name

AlayaCare

## Scheduler View Features

AlayaCare offers multiple, flexible scheduling views, including by employee, by client, or an all-encompassing view. These views use colors and icons for clarity and allow planners to add, edit, cancel, or hold visits directly from any view. The interface also provides quick access to reference information such as client contact details and total service hours, facilitating strategic scheduling.

## Visit Card Design

Visit cards (tiles) on the schedule are designed to show core information at a glance, using a taxonomy of colors and icons to represent visit types, statuses, or conflicts. More detailed information, such as comprehensive client data or service instructions, is accessible in side panels to avoid cluttering the main view.

## Mobile App Experience

The mobile app is a key focus, featuring a simplified, rolling calendar view that makes it easy for caregivers to see upcoming visits. This design, based on caregiver feedback, aims to reduce friction and improve clarity for staff working in the field. The app allows viewing schedules up to 30 days in the future and 45 days in the past.

## Key Differentiators

The system's flexibility, with multiple schedule views and the ability to manage visits from any of them, is a key strength. It has a demonstrably strong focus on the caregiver's mobile user experience, with a simplified and intuitive calendar layout. This user-centric approach to both the planner and caregiver interfaces is a significant differentiator.

## System Name

Phoniro Care

## Scheduler View Features

Phoniro Care is primarily positioned as a mobile execution system for time and task tracking ('tid- och insatsuppföljning'), rather than a primary scheduling console. It receives finalized plans from a core planning system, such as Pulsen Combine. Therefore, its 'scheduler' is more of a task list for the caregiver, showing the visits that have been assigned to them.

## Visit Card Design

Within the mobile app, a visit card displays the basic planned intervention details. Its main function is interactive: caregivers use it to log the start and end times of visits and confirm the completion of specific tasks, providing granular data for follow-up.

## Mobile App Experience

This is the core of the Phoniro system. It provides a structured mobile workflow for caregivers to execute their planned visits and document their work in real-time. This structured data collection is crucial for ensuring quality of care and providing accurate data for financial administration and reporting.

## Key Differentiators

Its key differentiator is its specialization in the mobile execution and follow-up phase of home care. It excels at 'tid- och insatsuppföljning' (time and task tracking), integrating with planning systems to form a complete plan-execute-report workflow. This focus provides municipalities with robust tools for quality assurance and economic oversight.

## System Name

CGI (Heroma)

## Scheduler View Features

Heroma is a specialized, schema-intensive staffing and scheduling system ('Tid & Schema') rather than a visit-centric planning tool. It is used to manage the complex balancing act of staffing in sectors like home care, handling employee shifts, absences, and adherence to labor agreements. Its output—the master staff schedule—is a critical input for visit planning systems.

## Visit Card Design

Not directly applicable in the context of visit planning. The primary unit of scheduling in Heroma is the employee's shift or work pass, not an individual client visit.

## Mobile App Experience

While not detailed in the provided text, a modern system like Heroma would typically include a mobile app for employees to view their work schedules, request leave, and manage their time.

## Key Differentiators

Heroma's key role in the ecosystem is as a foundational HR and staffing system. Its strength lies in managing complex staff scheduling and ensuring compliance with labor rules. Its main value to a visit planner comes via integration, where it provides the definitive source of staff availability to systems like Tietoevry Lifecare, ensuring that visit plans are built on an accurate and compliant foundation.

# Core Calendar Ux Principles

The design of an effective home care scheduling calendar is governed by several fundamental UX principles aimed at managing high information density and supporting complex, time-sensitive workflows.

**1. Layout and Navigation Best Practices:**

- **Clarity is Paramount:** The primary goal of the calendar UI is to provide the quickest possible way for a planner to understand what is scheduled, what is currently in progress, and where there is available capacity. The interface must be clean and immediately comprehensible.
- **Flexible Views:** Users must have seamless control to switch between different contextual views. Essential views for home care planning include:
  - **Day View:** A detailed hourly breakdown for the current day, often in a Gantt format with lanes per employee.
  - **Week View:** A broader overview of the upcoming work week to facilitate forward planning.
  - **Team/Unit View:** An aggregated view showing the schedules for all staff within a specific team or geographical zone (indelning).
  - **Agenda View:** A list-based format that can be useful for reviewing a sequence of visits for a single employee or client.

**2. Establishing a Clear Visual Hierarchy:**
A strong visual hierarchy is critical to prevent cognitive overload and guide the planner's attention to the most important information.

- **Typography:** A clear typographic scale should be used. For instance, use a larger, bolder font for primary information like client names or visit times, and a smaller, lighter font for secondary details on the visit tile.
- **Color Usage:** Color should be used sparingly and with clear purpose. It is effective for categorizing visit types (e.g., blue for SoL, green for HSL), indicating visit status (e.g., red for a conflict, grey for completed), or highlighting urgency. Avoid using too many colors, which can create visual noise.
- **Spacing and Grouping:** Ample white space and logical grouping of elements are essential. Visit tiles, travel time blocks, and employee lanes should be visually distinct to ensure the schedule is scannable and easy to parse.

**3. Efficient Interaction Design:**

- **Minimize Clicks and Friction:** Workflows should be optimized for speed. Drag-and-drop functionality for rescheduling visits is a standard and highly effective interaction pattern.
- **Non-Disruptive Details:** To avoid breaking the planner's focus, detailed information about a visit or client should be displayed in side panels or slide-overs. This allows the user to access comprehensive data while keeping the main calendar view visible for context, which is superior to using disruptive, screen-covering modal windows.

# Interaction Design For Efficiency

Key interaction design patterns that significantly improve a home care planner's efficiency focus on fluid task management and contextual information access. A primary feature is the ability to use drag-and-drop functionality for rescheduling visits directly on the main calendar or Gantt chart view. This provides an intuitive and immediate way to adjust schedules. Another critical pattern is the use of non-disruptive side panels or slide-overs for displaying and editing the detailed information of a visit. This is superior to traditional modal windows, which obscure the rest of the schedule and force the planner to lose context. By keeping the main schedule visible, planners can make informed decisions while viewing details. Efficiency is also enhanced by allowing planners to add, edit, delete, or cancel visits from multiple different views within the application, a feature highlighted by AlayaCare. Furthermore, the system should support the easy creation of recurring visits, potentially using natural language or smart defaults, to automate the scheduling of regular appointments. Quick filters and toggles are also essential, allowing planners to rapidly narrow down the view by day, week, unit, skill, or visit category, thereby reducing cognitive load and speeding up the search for specific information or available slots.

# Caregiver Mobile Ux Needs

The user experience for caregivers using a mobile application in the field must prioritize clarity, efficiency, and access to critical information, acknowledging the dynamic nature of their work. Key requirements include:

- **Simplified Calendar View**: Mobile applications, such as AlayaCare's, are moving towards simplified, rolling calendar layouts that make it easy for caregivers to see their upcoming visits at a glance. This includes the ability to swipe through recent past and near-future schedules (e.g., 45 days back, 30 days forward).

- **Real-time Updates and Notifications**: Caregivers must be informed of schedule changes immediately. Systems like Pulsen Combine utilize push notifications to alert staff about modifications to their work shifts, ensuring they have the most current information without needing to constantly check the app.

- **Comprehensive Visit Details**: While the main view is simplified, caregivers need one-tap access to a detailed breakdown of each visit. This information, often kept in a detail panel or modal, includes:
  - **Access Information**: Full client address with map integration, specific notes on entrances or doors, and digital lock codes (e.g., from integrated Phoniro systems).
  - **Task Checklists**: A full breakdown of the interventions ('insatser') to be performed, often structured according to frameworks like IBIC/ÄBIC. This includes details on delegated healthcare tasks (HSL), medication administration, and specific instructions.
  - **Client-Specific Information**: Critical data such as client preferences (language, gender), safety plans, allergy information, infection control protocols, and details on required equipment like lifts.

- **Status Reporting and Workflow Execution**: The mobile app is the primary tool for executing the plan. As seen in the workflow between Pulsen Combine and Phoniro Care, the app receives the planned interventions and allows the caregiver to follow the steps and report status. This includes functionality to see the visit status (e.g., scheduled, en route, started, completed, missed) and log time and tasks performed.

# Addressing Planner Challenges Through Ux

## Continuity Solution

The UX promotes continuity of care by providing planners with direct visual feedback and tools to assign familiar staff to clients. This is achieved through features like a 'continuity indicator' or 'continuity badge' displayed on the visit tile itself, which immediately shows if the assigned caregiver matches the client's preferred or historical caregiver. More advanced systems may offer a 'continuity score' for each client or even a global 'continuity scorecard' as a key performance indicator for the planner. The planning system, such as Pulsen Combine, incorporates 'kontinuitet' as a key parameter during the scheduling process, allowing the system to prioritize or automatically suggest assignments that maintain caregiver-client relationships. The detail panel for a visit would contain the client's full continuity history and preferences, giving the planner all the necessary context to make a decision that favors continuity.

## Travel Optimization Solution

UX features for travel optimization focus on providing a realistic and dynamic view of staff transit. The main scheduling view should visualize the 'travel segment' between visits, including the estimated travel time. This is often calculated based on the selected mode of transport ('färdsätt'), such as a car or bicycle, and the start and end addresses for each route. Systems like Pulsen Combine offer 'mer realistisk planering' by accounting for local conditions and allowing planners to manually adjust travel times for unforeseen events like a 'snöstorm' or road closure. The UX provides critical alerts for 'insufficient travel buffer' or 'out-of-area/zone' assignments. The detail panel for a visit includes the full address with map integration and specific notes on entrance or parking, further aiding in efficient travel. This ensures that schedules are not just theoretically possible but practical for staff in the field.

## Skill Matching Solution

The user experience is designed to ensure that employees with the right skills, certifications, and authorizations are assigned to visits with specific requirements. This is accomplished through several layers of information. On the main calendar, visit tiles can display icons representing key skill requirements, such as 'delegerad HSL' (delegated healthcare tasks) or the need for double staffing. The system actively prevents errors by generating alerts for 'competence/authorization mismatch' or 'out-of-skill assignments'. Vendors like Pulsen Combine emphasize functions that 'matchar brukarens behov med personalens kompetens'. When a planner accesses the detailed view of a visit, they can see a full breakdown of required interventions, including specific HSL tasks, delegation details, and necessary equipment, ensuring a precise match between the client's needs and the caregiver's qualifications.

## Workload Balancing Solution

To help planners distribute work evenly and prevent staff burnout, the UX incorporates tools that visualize workload and enforce labor rules. The main scheduler view can include 'capacity cues' such as a 'density/heat' map or a simple count of visits per hour, providing an at-a-glance understanding of how busy certain time slots or staff members are. Planners can also see Key Performance Indicator (KPI) snippets showing planned time versus available time for each employee. The system provides critical visual indicators for labor compliance, flagging potential violations of rules regarding overtime, rest breaks, and union agreements. Integrations with staffing systems like CGI Heroma or Time Care, as noted with Tietoevry Lifecare, ensure that imported shift plans, including breaks ('raster') and absences, are accurately reflected in the scheduling view, preventing staff from being overbooked.

# Staff Management And Communication Features

UX features for staff management and communication are designed to provide planners with a clear view of workforce availability and to streamline the flow of information to field staff. The main scheduling interface, often a Gantt chart, displays per-employee lanes that show real-time status and availability, including on-shift times, scheduled breaks, and absences. A crucial feature, highlighted by Tietoevry Lifecare's system, is the ability to import schedules ('Schemaimport') from dedicated staffing systems like Heroma or Time Care. This ensures that all labor rules, shift plans, and leave are automatically accounted for. Staff competency profiles are also integral, allowing planners to filter or search for employees based on specific skills or authorizations. For communication, a key feature is the ability to send updates directly to staff. Pulsen Combine, for example, allows planners to inform employees of schedule changes via push notifications to their mobile devices. Mobile apps, such as those from AlayaCare and Phoniro, provide staff with a rolling calendar of their upcoming visits, detailed instructions for each visit, and a means to confirm completion, effectively closing the loop between planning and execution.

# Data Optimization And Reporting Capabilities

Modern home care scheduling systems leverage data and algorithms to move beyond simple booking and provide significant optimization and reporting capabilities, enabling more efficient and effective planning. These features are critical for managing the complexity of hemtjänst operations.

- **Route and Travel Time Optimization**: Systems like Pulsen Combine enable 'more realistic planning' by automatically calculating travel time ('restid'). This calculation is sophisticated, based on parameters such as the assigned vehicle or mode of transport ('fårdsätt'), start and end addresses for each route, and even allows for manual overrides to account for real-time conditions like 'snöstorm' (snowstorm) or traffic diversions. The goal is to create feasible routes with adequate travel buffers.

- **Workload and Resource Balancing**: Planners are provided with tools to balance workloads and ensure efficient staff utilization. This includes visual indicators like capacity heatmaps ('heat/coverage by zone/indelning') that show staff density per hour in different areas. The systems also track and flag compliance with labor rules, such as required rest breaks and overtime limits, often by integrating with staffing systems like Heroma.

- **Automated Matching and Rule Enforcement**: The systems use data to automate the matching of caregivers to visits based on multiple criteria. Pulsen Combine, for instance, matches client needs with staff competencies ('kompetens'). It also tracks and scores continuity, indicating when a preferred caregiver is assigned. The system actively enforces rules by generating warnings ('varningsfunktioner') when a planner attempts to book a visit that violates constraints, such as assigning a caregiver without the required authorization, creating overlapping appointments, or scheduling a double-staffing visit with only one person.

- **Insight and Performance Reporting**: The platforms provide both real-time and summary reports to give planners and managers insight into operational performance. This includes 'översiktsrapporter' showing the daily plan for an entire unit, as mentioned for Pulsen Combine. The UI often surfaces key performance indicators (KPIs) directly, such as planned vs. available time, continuity scores per client, and alerts for missed check-ins or delays. Tietoevry Lifecare emphasizes collecting resource data from various systems to present it in clear, uniform views for better time management.

# System Integration Patterns

Effective home care scheduling systems do not operate in isolation; they are a central hub within a broader ecosystem of municipal software. Integration is critical for data consistency and workflow automation. Common patterns include:

1.  **Integration with HR and Payroll Systems (e.g., Heroma)**: The scheduling platform must have accurate, up-to-date information on staff availability. This is achieved by integrating with the municipality's primary staffing system, such as CGI Heroma or Time Care. As noted in the documentation for Tietoevry Lifecare, a 'Schemaimport' (schedule import) function pulls in employee shifts, scheduled absences, breaks, and other time-related data. This ensures that planners are working with a correct view of available resources and that labor rules defined in the HR system are respected.

2.  **Integration with Client Record Systems (e.g., Pulsen Combine Core)**: The 'insatser' (interventions or care services) that need to be scheduled originate from client assessments and decisions made in a core client record or case management system. The scheduling system (e.g., Combine Plan) integrates with this core system (e.g., Combine Core) to receive the list of authorized services, their frequency, duration, and any specific requirements for each client. This creates a seamless flow from care authorization to operational planning.

3.  **Integration with Mobile Execution and Digital Lock Systems (e.g., Phoniro)**: Once the daily schedule is planned, it must be dispatched to caregivers in the field. This involves integrating with a mobile application platform. A common workflow, as documented by Nacka municipality, involves the scheduling system (Pulsen Combine) pushing the finalized plan to a mobile execution system like Phoniro Care. This system not only displays the schedule and task list on the caregiver's mobile device but also handles time and attendance tracking ('Tid- och insatsuppföljning') and integrates with physical hardware like digital door locks, enabling secure access to client homes.

# Accessibility Best Practices

While not explicitly detailed in the provided context, key accessibility considerations for a dense, data-rich scheduling UI can be inferred from general UX best practices and the nature of the interface. Ensuring the system is usable by people with diverse abilities, including those with visual, motor, or cognitive impairments, is crucial.

- **Do Not Rely on Color Alone**: The UI heavily uses color-coding for visit categories, statuses, and warnings. To be accessible, this information must also be conveyed through other means. The provided research supports this by mentioning the use of both 'Category color or icon' and 'warning badges'. This ensures that users with color vision deficiency can distinguish between different elements. Text labels or patterns should also be available as an alternative to color.

- **Sufficient Color Contrast and Scalable Text**: All text, icons, and visual indicators must have sufficient color contrast against their backgrounds to be readable for users with low vision. Furthermore, the interface should support browser-level text scaling, allowing users to increase the font size without breaking the layout. The recommendation to establish a clear 'typographic hierarchy' with different sizes for dates and events supports overall readability.

- **Full Keyboard Navigability**: A planner must be able to perform all core tasks using only a keyboard. This includes navigating between days in the calendar, moving between different staff members' schedules (lanes in a Gantt chart), tabbing through individual visits, opening detail panels (e.g., with the Enter key), and performing actions like drag-and-drop (via keyboard commands, such as cut and paste).

- **Screen Reader Compatibility with ARIA**: To be usable by screen reader users, all elements must be properly labeled. WAI-ARIA (Accessible Rich Internet Applications) attributes are essential for a complex UI like a scheduling grid. For example, a visit tile should be announced with all its key information (e.g., 'Visit for Client Andersson, 10:00 AM to 10:30 AM, Personal Care, Status: Scheduled'). Staff lanes, conflict warnings, and filter buttons must all have descriptive labels that allow a non-visual user to understand the schedule and interact with it effectively.
