# CAIRE Scheduling Platform – Umbrella Product Requirements Document

## Purpose

CAIRE is an AI‑powered scheduling platform for home‑care organisations. Its goal is to reduce manual scheduling effort, improve route efficiency and continuity of care, and provide data‑driven insights. The platform ingests schedules from external systems, runs constraint‑based optimisation, visualises and compares alternatives, supports pre‑planning of recurring visits, and provides a foundation for real‑time adaptation and predictive forecasting.

CAIRE operates as a hybrid scheduling system that balances **human planning** and **AI optimization**, using recurring weekly patterns (slingor) as stable baselines with AI optimization handling movable visits, disruptions, and fine-tuning. The platform supports multi-dimensional optimization across time, location, and scope (template vs instance).

This document summarises the overall requirements, use cases, user roles, features and constraints for CAIRE. Feature‑specific PRDs should be derived from this umbrella document.

## Target Users and Roles

| Role                               | Responsibilities                                                                                                                                                                |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Administrator**                  | Manages organisation settings, user accounts and subscriptions; configures labour rules, service areas and default scenarios.                                                   |
| **Scheduler / Operations Manager** | Imports original schedules, runs optimisations and compares results; manages daily and horizon planning; interacts with templates, movable visits and pre‑planning suggestions. |
| **Caregiver / Field Staff**        | Views assigned schedules via mobile or web; receives updates when plans change; may adjust availability or request shifts.                                                      |
| **Finance / Analyst**              | Reviews KPIs, cost and revenue metrics; analyses schedule efficiency and utilisation; informs staffing decisions; uses BI tools for strategic reporting.                        |
| **Care Manager**                   | Reviews clinical notes and risk alerts; manages care plan updates; handles deviation (avvikelse) workflows; uses AI copilot for cohort analysis and decision support.           |
| **Integration Developer / IT**     | Manages API keys and external integrations (Carefox, Phoniro, eCare, GPS); implements data exchange; monitors system health; configures BI tool connections.                    |

## Core Use Cases

### 1. Original Schedule Import and Baseline Comparison

- **Import Source Schedules**: Allow a scheduler to fetch schedules from external systems (e.g. Carefox) or upload CSV/JSON files. Validate the data and map it into CAIRE's normalised schema (visits, employees, clients, service areas, constraints).

- **Create Original Schedule Record**: Store the imported plan as an "Original" schedule and preserve flexible time windows, constraints and staff assignments for optimisation.

- **Baseline Generation**: Derive a manual baseline that mirrors the source plan with fixed visit times for comparison. Baselines support side‑by‑side comparison with optimised results and serve as a record of what was planned externally.

### 2. AI‑Powered Optimisation

- **Optimisation Job Submission**: Send the normalised "problem" (visits, employees, constraints) to the solver (Timefold) using the configured scenario and solver parameters. Support different types of optimisation runs (original optimisation, fine‑tune via patch, batch jobs).

- **Job Monitoring**: Poll the solver for status updates and display progress in the dashboard. Handle errors and timeouts gracefully.

- **Result Processing**: Receive the solver output, map assignments and KPIs back into CAIRE's `solutions`, `solution_assignments`, `solution_events` and metrics tables. Update the schedule status accordingly.

- **Fine‑Tuning**: Allow schedulers to adjust constraints or visit times after an initial optimisation and submit a patch‑based re‑optimisation without duplicating the underlying problem.

### 3. Movable Visits and Pre‑Planning

- **Movable Visit Templates**: Capture long‑term work orders (frequency, duration, priority, flexible windows) from municipalities (biståndsbeslut) or manual entry. Preserve this record even after converting visits into a daily schedule. Support multi-day time windows (e.g., weekly visit that can be placed Monday-Friday).

- **Pre‑Planning Sessions**: Group a horizon of days/weeks/months for planning. Suggest optimal days and times for movable visits based on supply/demand balance, continuity goals, and unused hours recapture. Record draft, suggested, preferred, final and converted statuses.

- **Supply/Demand Balancing**: Analyze available employee capacity (supply) vs required visit hours (demand) across planning horizons. Identify unused client allocation hours that can be recaptured when excess staff capacity is available.

- **Unused Hours Management**: Track monthly allocated visit hours per client (from biståndsbeslut) that become unused when visits are cancelled. Utilize unused hours pool to balance supply/demand and minimize lost revenue (unused hours > 0 at month end = lost revenue).

- **Conversion to Fixed Visits**: Once accepted, create concrete visit records linked back to the original movable visit. Support recalculating or undoing conversions if new information arises. Pinned visits become part of stable slingor (recurring patterns).

### 4. Schedule Templates (Slinga) and Recurring Patterns

- **Slinga Management**: Enable organisations to create, import, and edit weekly recurring patterns (slingor) that define stable visit assignments (employee + day + time). Every visit in a slinga is linked to a movable visit template that defines its recurring requirements. Slingor serve as stable baselines that generate daily schedules.

- **Slinga Import**: Import existing planned baselines (slingor) from external systems (eCare, Carefox). Create slinga templates with pinned visits from imported data. Link slinga visits to their corresponding movable visit templates.

- **Template Instantiation**: Instantiate a slinga over a planning horizon to populate schedules with default visits and shifts. All visits from slingor are pinned (locked) by default to preserve stable patterns.

- **New Slinga Generation**: Create optimal slingor from scratch using movable visit templates. Run full optimization to generate route patterns, then pin approved patterns to create stable slingor.

- **Fine‑Tune on Template Instances**: Apply fine‑tune workflows to specific days that diverge from the template due to cancellations, sickness or changes in demand. Unpin specific visits, make adjustments, then re-optimize while preserving pinned assignments.

- **Multi-Dimensional Optimization**: Optimize across time (daily/weekly/monthly), location (single/multiple service areas, cross-area optimization), and scope (temporary instance changes vs template updates).

### 5. Schedule Comparison and Analytics

- **Metrics Calculation**: Compute KPIs (travel time, service hours, utilisation, continuity scores, costs and revenues) for problems, schedules and solutions. Provide both aggregated and per‑entity metrics (employee, client, service area). Support home-care-specific metrics:
  - **Efficiency** (service hours / shift hours) - primary metric
  - **Continuity** (number of different caregivers per client, contact person percentage, preferred caregivers assignment rate)
  - **Unused hours recapture** (client allocation hours utilization)
  - **Skills utilization** and coverage
  - **Travel efficiency** (travel time / service hours)

- **Multi-State Comparison**: Compare all schedule states (unplanned, planned, optimized, actual, fine-tuned) side-by-side or in overlay mode. Highlight differences in assignments and metrics with color-coded visualizations. Calculate ROI improvements and optimization impact.

- **Dashboards & Reporting**: Expose dashboards for executives and schedulers to monitor efficiency, identify bottlenecks and support decision making. Support exporting data to external BI tools. Provide real-time metrics panels that update automatically when assignments change.

- **Visual Analytics**: Resource histograms showing demand vs supply curves, utilization charts, service area heatmaps, workload balance visualizations. Chart builders for trend analysis (travel time distribution, utilization trends, continuity scores over time).

### 6. Resource Management

- **Employees**: Manage caregivers' profiles (contact details, contract type, salary rates, driver licences, languages, certifications, availability, skills and tags). Support assignment to multiple schedules.

- **Clients**: Maintain client records (contact persons, municipality details, addresses, care plans, preferences, monthly allocations). Link clients to visits and movable visits.

- **Service Areas & Vehicles**: Define hierarchical service areas with default pay rates and continuity thresholds. Manage vehicles and assignments for employees including vehicle type and characteristics.

- **Labour Rules**: Store organisational and regional labour regulations (maximum hours per shift, minimum breaks, weekly hour limits) and apply them when validating schedules.

### 7. Integrations & Administration

- **External System Integration**: Configure API keys and credentials for external systems such as Carefox, Phoniro, eCare, GPS providers. Manage inbound and outbound data flows and map external schemas to CAIRE's domain model.

- **Authentication & Access Control**: Use an identity provider (Clerk) to manage users, organisation memberships and roles. Enforce multi‑tenancy and role‑based permissions across the UI and APIs.

- **Subscription and Billing**: Track product plans and organisation subscriptions (standard, premium, enterprise). Control feature access based on subscription tier and handle billing dates and statuses.

- **System Settings**: Allow organisations to configure default solver parameters, service area rules, salary structures, priority rules and UI preferences.

### 8. Clinical AI & Voice Documentation (Platform Add-On)

- **Medical Speech-to-Text**: Enable caregivers to document visits via voice notes using medical-grade STT (Swedish language, home-care domain vocabulary). Transform audio into structured clinical notes (SOAP format) with automatic extraction of vital signs, mobility status, medication adherence, mood/mental state, and risk indicators.

- **Real-Time Risk Detection**: Automatically score and detect clinical risks (fall risk, deterioration indicators, red-flag symptoms). Trigger escalation alerts to care managers and on-call nurses. Provide recommendations for urgent follow-ups.

- **Deviation Management (Avvikelser)**: Automatically detect, classify, and manage care deviations (missed visits, falls, medication errors, workplace safety risks) for Swedish regulatory compliance (SoL/HSL/Lex Maria, IVO audits). Create structured deviation records with responsibility assignment, follow-up workflows, and complete audit trails.

- **Care Plan Updates**: Automatically update care plans from voice notes (mobility level changes, skill requirements, visit duration adjustments). Feed real-time clinical context back into scheduling engine for constraint updates.

- **Agentic AI Copilot**: Natural language interface for care managers to query client cohorts, analyze trends, draft messages, and generate reports. Support Swedish language queries with domain-specific understanding.

- **Billing Automation**: Automatically code visits for billing (visit type, time spent, tasks completed, skill level). Generate structured billing outputs for municipal systems with audit-ready documentation.

### 9. BI Data Warehouse & Analytics (Platform Add-On)

- **Analytics Layer Separation**: Dedicated data warehouse (OLAP) separate from operational database (OLTP) to prevent BI queries from impacting real-time scheduling operations. Support enterprise BI tools (Power BI, Tableau, Looker, Metabase).

- **Dimensional Modeling**: Star/snowflake schema with pre-aggregated fact tables for fast dashboard queries. Support slowly changing dimensions (SCD Type 2) for historical tracking.

- **Data Pipeline**: Batch ELT or CDC (Change Data Capture) synchronization from operational database to warehouse. Configurable sync frequency (hourly, daily, near real-time).

- **Semantic Layer**: Centralized metric definitions (dbt metrics, LookML, Cube) to prevent KPI drift between product UI and BI dashboards. Single source of truth for business logic.

- **Historical Analysis**: Long-term trend analysis, comparison reporting, and audit trails. Support 1+ years of historical data retention with configurable policies.

- **Multi-Tenant Security**: Tenant-isolated analytics with GDPR-compliant data governance. Row-level security or separate datasets per organization.

### 10. Future AI & Real‑Time Features

- **Real‑Time Telemetry & Re‑scheduling**: Integrate GPS and mobile data to detect delays, cancellations or changes during the day. Automatically trigger re‑optimisation or suggest real‑time adjustments.

- **Demand Forecasting**: Use historical schedules and movable visit data to predict supply/demand imbalances. Recommend staffing levels and times for recurring visits months in advance.

- **Self‑Driving Scheduling**: Combine real‑time telemetry, forecast models and AI recommendations to continuously adjust schedules with minimal human intervention.

## Technology Stack

- **Frontend**: React 18 with TypeScript, Vite, Bryntum SchedulerPro 7.0+ for calendar UI, Apollo Client for GraphQL, Tailwind CSS for styling, Swedish localization.

- **Backend**: Express.js + Apollo Server (GraphQL API), Prisma ORM with PostgreSQL, WebSocket subscriptions for real-time optimization progress, Timefold optimization engine integration.

- **Data Architecture**: Normalized relational schema (OLTP) for operational scheduling, separate data warehouse (OLAP) for analytics (platform add-on), GraphQL API for data access, WebSocket for real-time subscriptions.

- **AI/ML**: Timefold constraint-based optimization, medical speech-to-text (platform add-on), clinical reasoning and risk scoring (platform add-on), agentic AI framework (platform add-on).

- **Integrations**: External systems (Carefox, Phoniro, eCare, GPS), BI tools (Power BI, Tableau, Looker, Metabase - platform add-on), municipal billing systems.

## Non‑Functional Requirements

- **Multi‑Tenancy & Security**: All data is tenant‑isolated. Users must authenticate via Clerk; API requests require valid JWTs. Sensitive data (password hashes, API keys, clinical notes) is encrypted at rest. Auditing and role‑based access control are enforced. BI warehouse supports row-level security or separate datasets per organization.

- **Performance & Scalability**: The system must handle thousands of organisations with daily schedules containing hundreds of visits. Optimisation jobs should complete within minutes for typical problems (<5 minutes for daily schedules, <10 minutes for weekly/monthly pre-planning). Metrics calculation and dashboards should remain responsive (<200ms for GraphQL queries, <10 seconds for warehouse queries). Bryntum UI handles 100+ employees and 1000+ visits with virtual scrolling and lazy loading.

- **Reliability & Resilience**: Scheduler and solver integrations should retry on transient failures. Schedule and problem data must never be lost; snapshots can be regenerated from normalised tables and solver dataset IDs. Backups and monitoring are in place. Data pipeline (BI add-on) has 99.9% uptime with automatic retry for transient failures.

- **Extensibility**: The domain model and architecture are designed to support new entities (e.g. new visit types, vehicle attributes), new solvers or AI models, and additional integration points without major structural changes. Platform add-ons (BI, Clinical AI) are built once and reused across customers.

- **Compliance**: Respect labour laws and municipal regulations (arbetsrätt) by validating schedules against configured labour rules. Support Swedish regulatory compliance (SoL, HSL, Lex Maria, IVO audits) for deviation management. GDPR-compliant data handling with EU/EES data residency. Support localisation (language, currency, regional date/time formats) for deployments beyond Sweden.

## High‑Level Workflows

- **Daily Scheduling**: Scheduler imports or instantiates a schedule (from unplanned visits or slingor), reviews and edits it in Bryntum UI (drag-and-drop, pin/unpin), runs optimisation with real-time progress via WebSocket, compares baseline and optimised results side-by-side, fine‑tunes by unpinning visits and re-optimizing, then publishes the final plan to caregivers.

- **Horizon Pre‑Planning**: Scheduler creates a planning session covering multiple weeks/months, imports movable visit templates (from biståndsbeslut or manual entry), runs pre-planning optimization to assign movable visits to optimal days based on supply/demand balance and unused hours recapture, reviews recommendations with diff view (ghost tracks + solid blocks), accepts/rejects individual recommendations, pins approved visits to create stable slingor.

- **Slinga Management**: Import existing slingor from external systems, link slinga visits to movable visit templates, generate daily schedules from slingor (all visits pinned), fine-tune by unpinning specific visits and re-optimizing, create new slingor from scratch using movable visit templates.

- **Multi-Dimensional Optimization**: Optimize across time (daily/weekly/monthly planning windows), location (single/multiple service areas, cross-area optimization with boundary recommendations), and scope (temporary instance changes vs template/slinga updates).

- **Actuals Processing**: At the end of a period, actual visit data (e.g. Phoniro exports) is imported, matched to schedules, and stored as a benchmark for KPI calculation and future forecasting. Compare actual vs planned vs optimized schedules with comprehensive metrics.

- **Clinical Documentation** (Platform Add-On): Caregiver completes visit, speaks voice note via mobile app, Clinical AI Layer processes audio (STT → structured note → risk scoring → care plan updates), care manager receives alerts for high-risk situations, deviation records created automatically for compliance (avvikelser), scheduling constraints updated in real-time.

- **BI Analytics** (Platform Add-On): Data pipeline syncs operational data to warehouse (batch or CDC), dimensional models updated with facts and dimensions, BI tools connect to warehouse for dashboards and reports, analysts query semantic layer for consistent KPIs, executives review strategic dashboards and trend analysis.

- **Real‑Time Adjustment** (Future): During the day, telemetry events (e.g. delays, cancellations) trigger re‑optimisation. Schedulers receive notifications and can approve or reject changes.

## Data Model Alignment

The platform uses a normalised relational schema (see `updated_db_schema_visual.md`) to store organisations, templates, visit templates, schedules, problems, solutions, visits, employees, clients, service areas, vehicles, skills, tags, labour rules and metrics. External solver payloads are referenced via `dataset_id` rather than stored internally. Movable visits and schedule templates capture recurring patterns; schedule groups organise horizons; schedules bind problems to scenarios and solutions; and metrics tables support analytics.

**Key Data Structures**:

- **Slingor**: Weekly recurring patterns of assigned visits (employee + day + time), stored as schedule templates with pinned visits
- **Movable Visits**: Recurring visit templates defining requirements (frequency, duration, time windows, skills), linked to slinga visits
- **Schedule States**: Unplanned, planned, optimized, actual, fine-tuned - all comparable with consistent metrics
- **Clinical Data** (Platform Add-On): Clinical notes, risk scores, escalation history, care plan changes, deviations, deviation follow-ups
- **Analytics Data** (Platform Add-On): Dimensional warehouse with facts (visits, schedules, assignments, events, KPIs) and dimensions (organization, service area, employee, client, date, time)

## Success Metrics

- **Operational Efficiency**: Reduction in travel time and distance (15-30% reduction vs manual planning); improved staff utilisation (targeting 75% or higher from a baseline of ~65%). Primary metric: Efficiency = service hours / shift hours.

- **Administrative Savings**: Decrease in manual scheduling hours per coordinator. With Clinical AI add-on: 50-80% reduction in documentation time (from 10-15 min to 2-3 min per visit).

- **Continuity & Quality**: Increase in continuity scores and client satisfaction; fewer missed or late visits. Reduce number of different caregivers per client (target: <10, typical Swedish home care has ~10, 12+ is poor). Improve contact person percentage and preferred caregivers assignment rate.

- **Unused Hours Management**: Minimize unused allocated hours per client per month (goal: 0 unused hours at month end, unused hours > 0 = lost revenue). System identifies and utilizes unused hours to balance supply/demand.

- **Financial Performance**: Improved ratio of service hours to paid hours; visibility into costs and revenues at the schedule, employee and service area levels. With Clinical AI add-on: >95% billing automation rate, <2% dispute rate.

- **Risk Detection** (Clinical AI Add-On): >95% true positive rate, <5% false positive rate for risk alerts. 10-15% reduction in emergency hospital admissions. <1 hour time-to-detection for high-risk situations.

- **User Adoption**: Active users per organisation; frequency of optimisation runs; uptake of pre‑planning and fine‑tuning features. Planner satisfaction ≥70%, recommendation acceptance rate ≥70%.

- **Performance**: Optimization completes in <5 minutes for daily schedules, <10 minutes for weekly/monthly pre-planning. GraphQL queries <200ms, warehouse queries <10 seconds for dashboards.

## Platform Add-Ons

CAIRE offers two **platform add-ons** that extend core scheduling capabilities:

### CAIRE Analytics & BI

Enterprise-grade Business Intelligence and analytics platform providing:

- Separation of OLTP (operational) and OLAP (analytics) workloads
- Enterprise BI tool integration (Power BI, Tableau, Looker, Metabase)
- Pre-computed KPIs and metrics with semantic layer
- Historical analysis and trend reporting
- Multi-tenant security with GDPR compliance

**Positioning**: Built once for CAIRE platform, configured per organization. Offered as paid product add-on with per-organization pricing.

**Reference**: See `Feature-PRD-BI-Data-Warehouse.md` for complete specifications.

### CAIRE Speech-to-Text & Clinical AI (Corti)

Clinical AI layer providing:

- Medical-grade speech-to-text for ambient documentation
- Real-time risk detection and escalation
- Deviation management (avvikelser) for Swedish regulatory compliance
- Care plan updates from voice notes
- Agentic AI copilot for care managers

**Positioning**: Delivered via partnership with Corti, built once for CAIRE platform, configured per organization. Offered as paid product add-on.

**Reference**: See `Feature-PRD-speech-to-text.md` for complete specifications.

## Pilot Programs

CAIRE supports structured pilot programs to validate capabilities with real-world data and workflows. Pilots typically include:

- **Phase 1**: Data requirements analysis and feasibility testing
- **Phase 2**: System launch and core workflow testing
- **Phase 3**: Advanced features and user acceptance testing

Pilots can include early access to platform add-ons (Analytics & BI, Clinical AI) with one-time enablement fees that can be credited against rollout.

**Reference**: See `09-scheduling/pilots/attendo/PILOT_PLAN_V2.md` for example pilot structure.

---

This umbrella PRD encapsulates the product vision and main requirements for the CAIRE platform. Use it as the starting point for creating feature‑specific PRDs (e.g. "Original Schedule Import," "Manual Baseline," "Fine‑Tune Optimisation," "Movable Visit Pre‑Planning," "Slinga Template Management," "Schedule Comparison & Analytics," "Resource Management," "Integration & Admin," "BI Data Warehouse," "Clinical AI & Speech-to-Text"). Each feature PRD should elaborate on inputs, outputs, data flows, user interactions, API endpoints, edge cases and acceptance criteria while remaining aligned with the high‑level purpose and constraints defined here.

**Related Documentation**:

- `Feature-PRD-BI-Data-Warehouse.md` - BI Analytics platform add-on specifications
- `Feature-PRD-speech-to-text.md` - Clinical AI platform add-on specifications
- `bryntum_consultant_specs/BRYNTUM_FROM_SCRATCH_PRD.md` - Bryntum SchedulerPro UI specifications
- `09-scheduling/pilots/attendo/PILOT_PLAN_V2.md` - Example pilot plan structure
- `09-scheduling/README.md` - Scheduling documentation overview

---
