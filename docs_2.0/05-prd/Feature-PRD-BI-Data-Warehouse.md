# BI Data Warehouse & Analytics Platform PRD

**Version:** 1.0  
**Date:** 2025-12-16
**Target Audience:** Home Care Organizations (Municipalities, Private Providers), Data Analysts, BI Teams  
**Purpose:** Product Requirements Document for enabling enterprise-grade Business Intelligence and analytics capabilities through a dedicated data warehouse architecture

---

## Executive Summary

CAIRE's scheduling platform generates rich operational data through daily scheduling, optimization runs, and care delivery. To unlock the full value of this data for strategic decision-making, compliance reporting, and operational insights, CAIRE requires a dedicated **BI Data Warehouse** that separates analytics workloads from real-time operational transactions.

This PRD outlines the architecture, implementation, and capabilities for a **BI Data Warehouse & Analytics Platform** that provides:

- **Separation of OLTP and Analytics**: Isolated analytics layer that prevents BI queries from impacting real-time scheduling operations
- **Enterprise BI Tool Support**: Integration with industry-standard BI tools (Power BI, Tableau, Looker, Metabase, etc.)
- **Pre-computed KPIs and Metrics**: Fast, consistent reporting using CAIRE's existing solution_metrics and breakdown tables
- **Historical Analysis**: Long-term trend analysis, comparison reporting, and audit trails
- **Multi-tenant Security**: Tenant-isolated analytics with GDPR-compliant data governance

**Value Proposition:** Enable data-driven decision-making, executive reporting, and operational insights without compromising the performance or reliability of CAIRE's real-time scheduling engine. Transform raw scheduling data into actionable intelligence for care organizations.

---

## Problem Statement

### Current Pain Points

1. **Operational Database Overload**
   - Heavy BI queries compete with real-time scheduling operations
   - Analytics workloads cause performance degradation during peak scheduling hours
   - Risk of timeouts and slow response times for schedulers and caregivers
   - No separation between transactional and analytical workloads

2. **Limited Analytics Capabilities**
   - Ad-hoc analysis requires direct database access (security risk)
   - No standardized KPI definitions across different reporting tools
   - Difficult to compare historical periods or baseline vs. optimized schedules
   - Lack of pre-aggregated metrics for fast dashboard rendering

3. **Scalability Constraints**
   - Operational database not optimized for large-scale aggregations
   - Historical data retention limited by OLTP performance concerns
   - Cross-organizational reporting requires complex multi-tenant queries
   - No support for near real-time analytics without impacting operations

4. **BI Tool Integration Gaps**
   - Organizations want to use their existing BI tools (Power BI, Tableau, etc.)
   - No semantic layer or standardized data models for consistent reporting
   - Manual data exports are error-prone and don't support real-time insights
   - KPI drift between product UI, BI dashboards, and executive reports

5. **Compliance and Governance Challenges**
   - Difficult to enforce tenant isolation in ad-hoc queries
   - No audit trail for data access and transformations
   - Retention policies not systematically applied
   - PII minimization not enforced in analytics exports

### Market Opportunity

- **Enterprise customers** require BI integration as a standard feature
- **Municipalities** need compliance reporting and audit trails
- **Executive teams** demand strategic dashboards and trend analysis
- **Competitive differentiation**: Most scheduling platforms lack enterprise BI capabilities
- **Upsell opportunity**: BI/analytics as a premium add-on product

---

## Solution Overview

### The BI Data Warehouse Architecture

**Core Principle:** Separate OLTP (operational scheduling) from OLAP (analytics and reporting)

```
┌─────────────────────────────────────────────────────────────┐
│              CAIRE Operational Layer (OLTP)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Scheduling   │  │ Optimization │  │ Real-time    │     │
│  │   Engine     │  │   Solver     │  │  Updates     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                        PostgreSQL (RDS)                      │
│                    Normalized, Transactional                 │
└────────────────────────────┬─────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Data Pipeline  │
                    │  (CDC or Batch) │
                    └────────┬────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│              Analytics Layer (Data Warehouse)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Dimensions │  │    Facts     │  │   Semantic   │     │
│  │   (Slow-     │  │  (High-      │  │     Layer    │     │
│  │   Changing)  │  │   Volume)    │  │  (dbt/LookML)│     │
│  └──────────────┘  └──────────────┘  └──────┬───────┘     │
│                                               │             │
│         BigQuery / Snowflake / ClickHouse    │             │
│              Denormalized, Read-Optimized    │             │
└────────────────────────────┬─────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   BI Tools      │
                    │ Power BI/Tableau│
                    │ Looker/Metabase │
                    └─────────────────┘
```

### Key Components

1. **Data Warehouse**
   - Purpose-built analytics database (BigQuery, Snowflake, ClickHouse, or Postgres read replica)
   - Denormalized star/snowflake schema optimized for aggregations
   - Historical data retention (configurable per dataset)
   - Multi-tenant isolation via row-level security or separate datasets

2. **Data Ingestion Pipeline**
   - **Option A (Preferred for Scale):** CDC (Change Data Capture) via Debezium, AWS DMS, or managed CDC
   - **Option B (Early Stage):** Batch ELT jobs (nightly or hourly extraction)
   - **Option C (Future):** Event-driven export from domain events
   - Near real-time or batch synchronization based on customer needs

3. **Dimensional Modeling**
   - **Dimensions:** dim_organization, dim_service_area, dim_employee, dim_client, dim_date, dim_time
   - **Facts:** fact_visit, fact_schedule, fact_solution_assignment, fact_solution_event, fact_kpi_daily
   - Pre-aggregated KPI tables for fast dashboard queries
   - Slowly changing dimensions (SCD Type 2) for historical tracking

4. **Semantic Layer (Optional but Recommended)**
   - Centralized metric definitions (dbt metrics, LookML, Cube, MetricFlow)
   - Prevents KPI drift between product UI, BI dashboards, and reports
   - Reusable business logic and calculations
   - Self-service analytics for non-technical users

5. **BI Tool Integration**
   - Direct warehouse access for enterprise BI tools
   - Standardized connection strings and authentication
   - Pre-built dashboard templates and data models
   - Export capabilities (CSV, Excel, PDF)

---

## Architecture & Technical Design

### 3.1 Operational Data Store (ODS / OLTP)

**System of Record:** PostgreSQL (AWS RDS)  
**Primary Goals:** Correctness, integrity, low-latency writes  
**Schema:** Normalized relational schema (Drizzle ORM)

**Key Tables:**

- Core entities: organizations, service_areas, employees, clients
- Scheduling: schedules, visits, shifts, breaks
- Optimization: problems, solutions, solution_assignments, solution_events
- Metrics: schedule_metrics, solution_metrics, employee/client/service_area breakdowns

**Design Principles:**

- Write-optimized for real-time scheduling operations
- Normalized to prevent data anomalies
- Transaction-safe with ACID guarantees
- No heavy aggregations or analytical queries

### 3.2 Analytics Store (Data Warehouse)

**Purpose:** BI, cross-org reporting, long historical retention, heavy aggregations, dashboards

**Technology Options:**

| Option                          | Use Case                     | Pros                                     | Cons                                     |
| ------------------------------- | ---------------------------- | ---------------------------------------- | ---------------------------------------- |
| **BigQuery**                    | Enterprise, multi-region     | Serverless, auto-scaling, ML integration | Cost at scale, Google ecosystem          |
| **Snowflake**                   | Enterprise, compliance-heavy | Excellent security, data sharing         | Higher cost, complexity                  |
| **ClickHouse**                  | High-performance analytics   | Extremely fast, cost-effective           | Requires more operational overhead       |
| **Postgres Read Replica + dbt** | Early stage, cost-sensitive  | Simple, familiar, low cost               | Limited scalability, same vendor lock-in |

**Recommendation:** Start with Postgres read replica + dbt for Phase 1, evolve to BigQuery/Snowflake for enterprise customers.

**Schema Design:**

- Star schema (denormalized facts + dimensions)
- Pre-aggregated fact tables for common KPIs
- Partitioned by date for performance
- Indexed on common filter columns (org_id, service_area_id, date)

### 3.3 Data Ingestion Patterns

#### Option A: CDC (Change Data Capture) – Preferred for Scale

**Implementation:**

- Stream changes from PostgreSQL WAL (Write-Ahead Log) to warehouse
- Tools: Debezium, AWS DMS, Fivetran, or managed CDC services
- Near real-time synchronization (seconds to minutes latency)

**Benefits:**

- No impact on OLTP database performance
- Real-time analytics without batch windows
- Automatic handling of updates and deletes
- Supports high-volume, high-frequency changes

**Use Case:** Enterprise customers requiring near real-time BI dashboards

#### Option B: Batch ELT (Extract, Load, Transform) – Simple and Reliable

**Implementation:**

- Scheduled jobs (nightly or hourly) extract data from OLTP
- Load raw data into warehouse staging area
- Transform using dbt or similar tool
- Update fact and dimension tables

**Benefits:**

- Simple to implement and maintain
- Predictable resource usage
- Easy to debug and audit
- Sufficient for most reporting needs (daily/weekly dashboards)

**Use Case:** Early-stage implementation, customers with daily reporting needs

#### Option C: Event Export (Domain Events) – Future Enhancement

**Implementation:**

- Export stable event stream (schedule_changed, optimization_completed, visit_completed)
- Event-driven architecture with event sourcing
- Useful for real-time dashboards and event-based analytics

**Use Case:** Future real-time analytics and event-driven BI

**Recommendation:** Start with Option B (batch ELT), evolve to Option A (CDC) when enterprise needs require near real-time BI.

### 3.4 Warehouse Modeling Strategy

#### Dimensions (Slow-Changing)

**dim_organization**

- Organization attributes (name, region, subscription tier)
- SCD Type 2 for historical tracking of org changes
- Surrogate keys for fact table joins

**dim_service_area**

- Service area hierarchy and attributes
- Default pay rates, continuity thresholds
- Geographic boundaries and metadata

**dim_employee**

- Employee profiles (name, contract type, skills, certifications)
- SCD Type 2 for tracking employee attribute changes
- PII minimized (use surrogate keys in facts)

**dim_client**

- Client attributes (municipality, care plan type)
- SCD Type 2 for care plan changes
- PII minimized (use surrogate keys in facts)

**dim_date / dim_time**

- Standard date dimension (year, quarter, month, week, day)
- Time dimension for hourly analysis
- Holiday and business day flags

#### Facts (High-Volume)

**fact_visit**

- Planned and actual visit data
- Foreign keys to dim_employee, dim_client, dim_service_area, dim_date
- Measures: duration, travel_time, wait_time, service_hours
- Granularity: One row per visit per schedule version

**fact_schedule**

- Schedule versions and revisions
- Foreign keys to dim_organization, dim_service_area, dim_date
- Measures: total_visits, total_hours, optimization_status
- Granularity: One row per schedule per version

**fact_solution_assignment**

- Optimization solution assignments (who did what, when)
- Foreign keys to dim_employee, dim_client, dim_date
- Measures: assignment_start, assignment_end, travel_distance
- Granularity: One row per assignment

**fact_solution_event**

- Timeline events (travel, wait, break, visit)
- Foreign keys to dim_employee, dim_date, dim_time
- Measures: event_duration, event_type
- Granularity: One row per event (high volume)

**fact_kpi_daily** (Pre-aggregated)

- Daily KPI snapshots for fast BI queries
- Foreign keys to dim_organization, dim_service_area, dim_date
- Measures: utilization, travel_time, service_hours, continuity_score, cost, revenue
- Granularity: One row per org/service_area/date
- Updated via batch job or incremental refresh

#### KPI Sources

CAIRE already stores KPIs in `solution_metrics` and breakdown tables. The warehouse can:

- **Option 1:** Use pre-computed KPIs directly (fast, consistent with product UI)
- **Option 2:** Recompute KPIs in warehouse (auditing, alternative definitions)

**Best Practice:** Treat backend KPIs as the official "product truth," use warehouse for slicing/dicing and historical dashboards.

### 3.5 Semantic Layer

**Purpose:** Define metrics once, reuse everywhere

**Technology Options:**

- **dbt metrics layer** (open-source, SQL-based)
- **LookML** (Looker-specific, powerful but vendor-locked)
- **Cube** (headless BI, API-first)
- **MetricFlow** (dbt Labs, emerging standard)

**Key Metrics to Define:**

- Utilization (service_hours / paid_hours)
- Travel efficiency (travel_time / service_hours)
- Continuity score (client-caregiver consistency)
- Cost per visit (employee_cost + travel_cost)
- Revenue per visit (billing_rate \* service_hours)
- Optimization ROI (baseline_cost - optimized_cost)

**Benefits:**

- Single source of truth for KPI definitions
- Prevents drift between product UI and BI dashboards
- Self-service analytics for business users
- Version control and auditability

---

## Functional Requirements

### 4.1 Data Pipeline

**FR-1: Data Extraction**

- System MUST extract data from operational PostgreSQL database
- System MUST support both batch and CDC extraction methods
- System MUST handle incremental updates (only changed records)
- System MUST preserve data lineage (source table, extraction timestamp, transformation version)

**FR-2: Data Transformation**

- System MUST transform normalized OLTP data into denormalized warehouse schema
- System MUST apply business logic and calculations (KPIs, aggregations)
- System MUST handle slowly changing dimensions (SCD Type 2)
- System MUST support idempotent transformations (re-runnable without duplicates)

**FR-3: Data Loading**

- System MUST load transformed data into warehouse fact and dimension tables
- System MUST support upsert operations (update existing, insert new)
- System MUST handle data quality checks (nulls, referential integrity)
- System MUST provide loading status and error reporting

**FR-4: Data Synchronization**

- System MUST support configurable sync frequency (hourly, daily, real-time)
- System MUST handle sync failures gracefully (retry, alerting)
- System MUST maintain sync lag metrics (time between OLTP update and warehouse refresh)

### 4.2 Data Modeling

**FR-5: Dimensional Model**

- System MUST implement star schema (facts + dimensions)
- System MUST provide pre-aggregated fact tables for common KPIs
- System MUST support date partitioning for performance
- System MUST maintain referential integrity between facts and dimensions

**FR-6: Historical Tracking**

- System MUST support SCD Type 2 for dimension changes
- System MUST preserve historical versions of schedules and solutions
- System MUST enable time-based analysis (trends, comparisons)

**FR-7: Multi-Tenant Isolation**

- System MUST enforce tenant isolation at the data layer (row-level security or separate datasets)
- System MUST prevent cross-tenant data access
- System MUST support organization-level data partitioning

### 4.3 BI Tool Integration

**FR-8: Warehouse Access**

- System MUST provide secure connection strings for BI tools
- System MUST support standard SQL queries
- System MUST enforce authentication and authorization
- System MUST provide connection documentation and examples

**FR-9: Dashboard Templates**

- System MUST provide pre-built dashboard templates for common use cases
- System MUST include templates for: utilization, travel efficiency, continuity, cost/revenue, optimization ROI
- System MUST support customization and organization-specific dashboards

**FR-10: Data Export**

- System MUST support CSV export for ad-hoc analysis
- System MUST support Excel export with formatting
- System MUST support PDF export for reports
- System MUST enforce export limits and access controls

### 4.4 KPI and Metrics

**FR-11: Core KPIs**

- System MUST calculate and store: utilization, travel_time, service_hours, continuity_score
- System MUST calculate and store: cost, revenue, profit by organization/service_area/client
- System MUST calculate and store: optimization ROI (baseline vs optimized deltas)
- System MUST support both pre-computed and on-demand KPI calculation

**FR-12: KPI Consistency**

- System MUST maintain consistency between product UI KPIs and warehouse KPIs
- System MUST support semantic layer for centralized metric definitions
- System MUST provide KPI drift detection and alerting

**FR-13: Trend Analysis**

- System MUST support day/week/month/year trend analysis
- System MUST enable comparison of baseline vs optimized schedules
- System MUST support period-over-period comparisons

### 4.5 Security and Governance

**FR-14: Authentication and Authorization**

- System MUST integrate with CAIRE's authentication system (Clerk)
- System MUST enforce role-based access control (RBAC)
- System MUST support read-only analytics roles
- System MUST provide audit logs for data access

**FR-15: Data Privacy**

- System MUST minimize PII in warehouse (prefer surrogate keys)
- System MUST enforce GDPR-compliant data retention policies
- System MUST support data deletion requests (right to be forgotten)
- System MUST maintain data processing agreements (DPIA compliance)

**FR-16: Data Governance**

- System MUST maintain data lineage (source → transformation → warehouse)
- System MUST support data quality monitoring and alerting
- System MUST provide data catalog (table descriptions, column definitions)
- System MUST support retention policies per dataset

---

## Non-Functional Requirements

### 5.1 Performance

**NFR-1: Query Performance**

- Warehouse queries MUST complete within 10 seconds for standard dashboards
- Pre-aggregated fact tables MUST support sub-second queries
- System MUST support concurrent queries from multiple BI tools
- System MUST scale to handle 100+ concurrent analytical queries

**NFR-2: Data Freshness**

- Batch sync MUST complete within 2 hours for daily extraction
- CDC sync MUST maintain < 5 minute lag for near real-time analytics
- System MUST provide data freshness indicators in dashboards

**NFR-3: Resource Isolation**

- Analytics workloads MUST NOT impact OLTP database performance
- Warehouse queries MUST NOT cause timeouts or slowdowns in scheduling operations
- System MUST support resource quotas and query limits

### 5.2 Scalability

**NFR-4: Data Volume**

- System MUST handle 1+ years of historical data retention
- System MUST support 1000+ organizations with daily schedule data
- System MUST scale to 100M+ fact table rows
- System MUST support partitioning and archiving strategies

**NFR-5: Concurrent Users**

- System MUST support 50+ concurrent BI tool connections
- System MUST handle 100+ concurrent dashboard views
- System MUST support query queuing and resource management

### 5.3 Reliability

**NFR-6: Data Pipeline Reliability**

- Data pipeline MUST have 99.9% uptime
- Pipeline failures MUST be detected and alerted within 15 minutes
- System MUST support automatic retry for transient failures
- System MUST maintain data consistency (no duplicates, no missing data)

**NFR-7: Data Quality**

- System MUST detect and alert on data quality issues (nulls, outliers, referential integrity)
- System MUST support data validation rules
- System MUST provide data quality dashboards and reports

### 5.4 Security

**NFR-8: Data Security**

- Warehouse data MUST be encrypted at rest
- Data in transit MUST use TLS 1.2+
- System MUST support encryption key rotation
- System MUST comply with SOC 2, ISO 27001 (where applicable)

**NFR-9: Access Control**

- System MUST enforce tenant isolation (no cross-org data access)
- System MUST support IP whitelisting for BI tool connections
- System MUST provide audit logs for all data access
- System MUST support role-based permissions (viewer, analyst, admin)

### 5.5 Compliance

**NFR-10: GDPR Compliance**

- System MUST support data retention policies (configurable per dataset)
- System MUST support data deletion (right to be forgotten)
- System MUST maintain data processing agreements
- System MUST minimize PII in analytics layer

**NFR-11: Data Residency**

- Warehouse MUST be hosted in EU/EES region (for EU customers)
- System MUST support region-specific data storage
- System MUST comply with local data protection regulations

---

## User Stories

### 6.1 Data Analyst

**US-1: Ad-Hoc Analysis**

- **As a** data analyst
- **I want to** query the warehouse directly using SQL
- **So that** I can perform custom analysis and answer business questions

**US-2: KPI Consistency**

- **As a** data analyst
- **I want to** use pre-defined KPI definitions from the semantic layer
- **So that** my reports match the KPIs shown in the product UI

**US-3: Historical Trends**

- **As a** data analyst
- **I want to** analyze trends over multiple months/years
- **So that** I can identify patterns and inform strategic decisions

### 6.2 Executive / Finance

**US-4: Executive Dashboard**

- **As an** executive
- **I want to** view high-level KPIs in a dashboard (utilization, cost, revenue)
- **So that** I can monitor organizational performance at a glance

**US-5: Cost Analysis**

- **As a** finance manager
- **I want to** analyze costs and revenues by service area, employee, or client
- **So that** I can optimize profitability and resource allocation

**US-6: Optimization ROI**

- **As an** executive
- **I want to** compare baseline vs optimized schedule costs
- **So that** I can quantify the value of CAIRE's optimization engine

### 6.3 Operations Manager

**US-7: Operational Efficiency**

- **As an** operations manager
- **I want to** view utilization and travel efficiency metrics
- **So that** I can identify bottlenecks and improve scheduling

**US-8: Continuity Reporting**

- **As an** operations manager
- **I want to** analyze continuity scores and caregiver variation
- **So that** I can ensure quality of care and client satisfaction

**US-9: Workforce Planning**

- **As an** operations manager
- **I want to** analyze supply vs demand trends
- **So that** I can plan staffing levels and identify capacity gaps

### 6.4 IT / Integration

**US-10: BI Tool Integration**

- **As an** IT administrator
- **I want to** connect our existing BI tool (Power BI, Tableau) to the warehouse
- **So that** we can use our preferred analytics platform

**US-11: Data Export**

- **As an** IT administrator
- **I want to** export data to CSV/Excel for external analysis
- **So that** we can integrate with other systems and reporting tools

---

## Pilot Enablement Plan (Early Access)

### Purpose

This section describes the **CAIRE Analytics & BI** as a **platform add-on** for early-access customers (e.g., Attendo pilot). The analytics platform is built **once for CAIRE**, with per-organization configuration. This is **not** a bespoke customer solution.

### Architectural Principle

- **Operational system (OLTP):** Real-time scheduling, optimisation, planner workflows
- **Analytics layer (BI / Data Warehouse):** Reporting, historical analysis, ad-hoc queries

No analytics queries run against the operational scheduling database.

### Data & DPIA Alignment

- No new personal data categories introduced
- No sensitive health data (GDPR Art. 9)
- Same legal basis as core platform (Art. 6.1(f) – Legitimate Interest)
- EU/EES hosting only
- Tenant-isolated, read-only analytics access

This constitutes a **purpose extension**, documented as a **DPIA addendum**, not a new DPIA.

### Pilot Scope of Delivery

#### Capabilities Enabled

- Custom dashboards and charts
- Ad-hoc analysis and querying
- Saved reports and views
- Data export (CSV / Excel / PDF)
- Trend analysis (day / week / month)
- Comparison of baseline vs optimised schedules

#### Typical KPIs

- Utilisation / efficiency
- Travel and waiting time
- Service hours vs paid hours
- Continuity and staffing effects (where available)
- Per service area and aggregate views

### Pilot Project Plan & Timeline

**Total duration:** ~4 weeks  
**Delivery model:** Platform enablement + customer configuration

#### Week 1 – Scope & Governance

- Confirm KPIs and reporting priorities
- Define access roles and permissions
- Finalise DPIA addendum wording
- Confirm retention rules

#### Week 2 – Data Pipeline & Modelling

- Enable analytics / warehouse layer
- Structure facts and dimensions
- Validate KPI definitions vs operational metrics

#### Week 3 – Dashboards & Analysis

- Build initial dashboards
- Enable ad-hoc querying
- Configure exports and saved reports

#### Week 4 – Validation & Handover

- Validate numbers against operational UI
- User access testing
- Documentation and reporting templates

### Budget & Commercial Terms

#### One-Time Enablement Fee (Early Access)

| Item           | Value                                                  |
| -------------- | ------------------------------------------------------ |
| Duration       | ~4 weeks                                               |
| Scope          | Platform analytics enablement + customer configuration |
| Estimated cost | **≈ 200 000 SEK**                                      |

#### Notes

- One-time fee
- Based on actual resource cost
- Can be credited against future rollout or license
- No long-term commitment

### Post-Pilot (Commercial Product)

After the pilot, **CAIRE Analytics & BI** is offered as a **paid product add-on**, with per-organization pricing (monthly), independent of pilot fees.

### Pilot Summary

- **Type:** CAIRE product add-on
- **Setup:** One shared platform, per-org configuration
- **Time:** ~4 weeks
- **Cost:** ~200 000 SEK (one-time enablement)
- **GDPR impact:** No new data, DPIA addendum only

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)

**Goal:** Establish basic warehouse infrastructure and data pipeline

**Deliverables:**

- Set up warehouse database (Postgres read replica or cloud warehouse)
- Implement batch ELT pipeline (nightly extraction)
- Create initial dimensional model (dim_organization, dim_service_area, dim_date)
- Build fact_visit and fact_schedule tables
- Validate data quality and sync accuracy

**Success Criteria:**

- Data successfully syncing from OLTP to warehouse daily
- Basic dimensional model in place
- Data quality checks passing

### Phase 2: Modeling & KPIs (Weeks 5-8)

**Goal:** Complete dimensional model and implement core KPIs

**Deliverables:**

- Complete all dimension tables (dim_employee, dim_client, dim_time)
- Build all fact tables (fact_solution_assignment, fact_solution_event, fact_kpi_daily)
- Implement pre-aggregated KPI tables
- Create dbt transformations and models
- Validate KPI calculations against product UI

**Success Criteria:**

- All fact and dimension tables populated
- KPIs matching product UI calculations
- dbt models tested and documented

### Phase 3: BI Integration (Weeks 9-12)

**Goal:** Enable BI tool access and build initial dashboards

**Deliverables:**

- Configure warehouse access for BI tools
- Create connection documentation and examples
- Build initial dashboard templates (utilization, travel, continuity, cost/revenue)
- Implement semantic layer (dbt metrics or equivalent)
- Enable data export (CSV, Excel)

**Success Criteria:**

- At least one BI tool successfully connected
- Initial dashboards showing accurate data
- Export functionality working

### Phase 4: Enterprise Features (Weeks 13-16)

**Goal:** Add enterprise capabilities (CDC, advanced security, governance)

**Deliverables:**

- Implement CDC pipeline (if required for enterprise customers)
- Add row-level security and advanced access controls
- Implement data governance (lineage, catalog, quality monitoring)
- Add retention policies and data deletion workflows
- Performance optimization (partitioning, indexing, query optimization)

**Success Criteria:**

- CDC pipeline operational (if applicable)
- Security and governance features in place
- Performance targets met

### Phase 5: Production & Scale (Ongoing)

**Goal:** Production hardening and scaling

**Deliverables:**

- Monitoring and alerting for data pipeline
- Documentation and runbooks
- Customer onboarding process
- Support and maintenance procedures
- Continuous optimization and improvements

---

## Success Metrics

### 7.1 Technical Metrics

- **Data Pipeline Reliability:** 99.9% uptime
- **Query Performance:** 90% of dashboard queries < 5 seconds
- **Data Freshness:** Batch sync completes within 2 hours, CDC lag < 5 minutes
- **Data Quality:** < 0.1% data quality issues (nulls, duplicates, referential integrity)

### 7.2 Business Metrics

- **Customer Adoption:** 80% of enterprise customers using BI features within 6 months
- **Dashboard Usage:** 50+ active dashboard users per organization
- **Query Volume:** 1000+ analytical queries per day
- **Export Usage:** 100+ data exports per month

### 7.3 Operational Metrics

- **OLTP Impact:** Zero performance degradation on scheduling operations
- **Resource Isolation:** Analytics queries never cause OLTP timeouts
- **Support Tickets:** < 5% of tickets related to BI/data warehouse issues

---

## Risks and Mitigations

### 8.1 Technical Risks

**Risk:** Data pipeline failures causing stale or missing data  
**Mitigation:** Implement robust error handling, retry logic, and alerting. Maintain data quality monitoring.

**Risk:** Performance degradation as data volume grows  
**Mitigation:** Implement partitioning, archiving, and query optimization. Use pre-aggregated fact tables.

**Risk:** KPI drift between product UI and warehouse  
**Mitigation:** Use semantic layer for centralized metric definitions. Implement automated KPI validation tests.

### 8.2 Business Risks

**Risk:** Low adoption due to complexity or lack of documentation  
**Mitigation:** Provide comprehensive documentation, dashboard templates, and onboarding support.

**Risk:** Cost overruns from cloud warehouse usage  
**Mitigation:** Implement query limits, resource quotas, and cost monitoring. Use cost-effective options (Postgres read replica) for early stage.

**Risk:** Security or compliance issues  
**Mitigation:** Implement robust access controls, audit logging, and GDPR compliance features from day one.

### 8.3 Operational Risks

**Risk:** Analytics workloads impacting OLTP performance  
**Mitigation:** Strict separation of OLTP and analytics. Use read replicas or separate warehouse. Monitor resource usage.

**Risk:** Data quality issues causing incorrect reporting  
**Mitigation:** Implement data validation rules, quality checks, and monitoring. Provide data quality dashboards.

---

## Dependencies

### 9.1 Technical Dependencies

- **Operational Database:** PostgreSQL (AWS RDS) with normalized schema
- **Warehouse Platform:** BigQuery, Snowflake, ClickHouse, or Postgres read replica
- **ETL/ELT Tool:** dbt, Fivetran, or custom pipeline
- **BI Tools:** Power BI, Tableau, Looker, Metabase (customer-provided)
- **Authentication:** Clerk integration for user authentication

### 9.2 Data Dependencies

- **Solution Metrics:** Existing solution_metrics and breakdown tables in OLTP
- **Schedule Data:** Schedules, visits, employees, clients, service areas
- **Optimization Data:** Problems, solutions, solution_assignments, solution_events

### 9.3 Organizational Dependencies

- **Data Team:** Data engineers for pipeline development and maintenance
- **BI Partners:** Customer BI teams for integration and dashboard development
- **Compliance:** Legal/compliance team for GDPR and data governance requirements

---

## Open Questions

1. **Warehouse Platform Selection:** Should we standardize on one platform (BigQuery, Snowflake) or support multiple? What are the cost implications?

2. **CDC vs Batch:** For Phase 1, should we start with batch ELT or invest in CDC from the beginning? What are the customer requirements?

3. **Semantic Layer:** Which semantic layer technology should we adopt (dbt metrics, LookML, Cube)? Should this be customer-configurable?

4. **Multi-Tenant Architecture:** Should we use row-level security, separate datasets per org, or a hybrid approach? What are the scalability implications?

5. **Historical Data Retention:** What retention period should we support? Should this be configurable per organization?

6. **Pricing Model:** Should BI/analytics be included in base product, premium tier, or sold as separate add-on?

---

## Appendix

### A.1 Data Model Reference

See `docs_2.0/03-data/BI.md` for detailed data architecture and modeling strategy.

### A.2 Related Documents

- **Umbrella PRD:** `docs_2.0/05-prd/prd-umbrella.md`
- **BI Architecture:** `docs_2.0/03-data/BI.md`
- **Attendo BI Addon:** `docs_2.0/09-scheduling/pilots/attendo/ADDON_ANALYTICS_DW_BI.md`

### A.3 Glossary

- **OLTP:** Online Transaction Processing (operational database)
- **OLAP:** Online Analytical Processing (analytics database)
- **CDC:** Change Data Capture (real-time data synchronization)
- **ELT:** Extract, Load, Transform (data pipeline pattern)
- **SCD:** Slowly Changing Dimension (historical tracking)
- **Star Schema:** Denormalized data model with facts and dimensions
- **Semantic Layer:** Centralized metric definitions and business logic

---

**Document Status:** Draft v1.0  
**Last Updated:** 2025-01-27  
**Next Review:** After Phase 1 completion
