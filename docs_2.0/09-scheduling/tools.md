# CAIRE Platform – Complete Tools & Code Architecture Guide

Status: Internal – authoritative reference
Audience: Founders, architects, engineers, contractors
Purpose: Single source of truth for all tools CAIRE uses today and in Platform 2.0, plus how these tools are integrated into the codebase in a maintainable, enterprise-grade way.

---

## 1. AI & Knowledge Work & AI IDEs (Core Thinking Layer)

### AI Assistants & Reasoning Models

- **ChatGPT** – Primary AI assistant for product thinking, architecture, documentation, legal drafts, and strategy.
- **Gemini** – Secondary assistant for cross-checking, second opinions, and model comparison.

### AI-Assisted Development Environments

- **Cursor** – Primary AI-assisted IDE for day-to-day development (TypeScript, React, backend).
- **Antigravity** – Alternative AI IDE for deep refactors, long-context reasoning, and architectural exploration.

### Knowledge Capture & Presentation

- **Granola** – Meeting notes, summaries, and shared context from calls and workshops.
- **Gamma** – Pitch decks, product storytelling, and lightweight presentation sites.

---

## 2. Product Development & Engineering (Production Stack)

### Core Architecture (Target State – Platform 2.0)

- **Frontend:** React 18 + Vite (modular SPA)
- **Backend API:** Node.js + Express with GraphQL (Apollo Server)
- **API Client:** Apollo Client
- **Database (OLTP):** PostgreSQL on AWS RDS
- **ORM:** Prisma (normalized data model)
- **Authentication & Multi-Tenancy:** Clerk
- **Scheduling UI:** Bryntum SchedulerPro
- **Optimisation Engine:** Timefold (external solver)

**Migration direction:** from a Next.js monolith (API routes + Drizzle) to a decoupled React + GraphQL + Prisma architecture.

### Engineering Tooling

- **GitHub** – source control, pull requests, code review, CI/CD workflows.
- **AWS (core services)** – compute, networking, IAM, security, infrastructure foundation.
- **AWS RDS (PostgreSQL)** – primary production OLTP database.

---

## 3. Observability, Analytics & Monitoring (Current)

### Observability (Current)

- **AWS CloudWatch** – primary infrastructure monitoring: logs, metrics, alarms for AWS services and backend runtime.

### Marketing Analytics (Current)

- **Google Analytics** – marketing and website analytics for caire.se and public pages.

---

## 4. Analytics & Data Platform (Enterprise Capability)

### Principle: Separate Operational Scheduling from Analytics

- **Operational DB (OLTP):** PostgreSQL (RDS) — write-optimized, normalized, transaction-safe, real-time scheduling.
- **Analytics DB / Warehouse:** separate read-optimized store for BI and long-term reporting.

### What this enables

- BI dashboards without performance risk to scheduling
- Long-range trend reporting (weeks/months/years)
- Executive/investor reporting
- Enterprise customer reporting

### Supported tooling patterns

- Warehouse options (examples): BigQuery / Snowflake / Redshift / ClickHouse / Postgres analytics replica
- Transformation layer: dbt (recommended when warehouse introduced)
- BI tools: Power BI / Tableau / Looker / Metabase / Superset

---

## 5. Collaboration & Documentation (Internal Source of Truth)

- **Google Workspace**
  - Docs – specifications, DPIAs, legal documents
  - Sheets – financial models, pilot ROI, pricing
  - Slides – internal and external presentations

- **Confluence (Atlassian)** – long-term internal documentation, system descriptions, architecture, governance, decision records.

---

## 6. Sales, CRM & Customer Operations (Go-to-Market)

- **HubSpot** – CRM, deal pipelines, contacts, sales tracking, customer communication.

---

## 7. Design, UX & Prototyping (Pre-Production)

- **Figma** – UI design, UX flows, brand assets, collaboration.
- **Lovable** – rapid prototyping of new features and websites.
- **21st.dev** – UX exploration and early concept validation.

**Rule:** Prototypes are for validation only and later rebuilt into the production AWS stack.

---

## 8. Project & Delivery Management (Execution)

- **Jira** – epics, stories, sprint planning, delivery tracking.
- **Miro** – workshops, system maps, process flows, collaborative design.

---

## 9. Security, Compliance & Governance (Mandatory)

- **Google Drive (controlled access)** – secure sharing with partners, auditors, customers.
- **DPIA & GDPR documentation** – internal frameworks and documents supporting compliance.
- **Access control & least privilege** – enforced via AWS IAM, Clerk, and internal processes.

---

## 10. Finance, Bookkeeping & Payments (Internal)

- **Fortnox** – accounting, invoicing, VAT, reporting.
- **Swedbank** – primary banking partner for CAIRE / EirTech AB.
- **Pleo** – expense management, cards, receipts.

---

## 11. Explicitly Not Used

- ❌ Supabase
- ❌ Firebase
- ❌ Vercel (frontend hosted on AWS)

---

## 12. Planned Additions – Platform 2.0

### Core 2.0 Additions

- **Feature Flags (Unleash, self-hosted on AWS)**
  Controlled rollout per customer, per organisation, or cohort.
- **Async Jobs & Event Orchestration (AWS SQS / EventBridge)**
  Background processing for optimisation runs, imports, simulations, and re-planning.
- **Product Analytics (PostHog – self-hosted)**
  In-product analytics (feature usage/adoption/workflow efficiency). Complements Google Analytics (marketing).

### Operational & Platform Enhancements

- Internal Admin / Ops Console
- Extended observability (building on CloudWatch + Sentry)
- Data lifecycle, retention, anonymisation, deletion controls

---

## 13. Code Architecture – How Tools Are Integrated (Mandatory Pattern)

### Core Principle

Application code must never import or depend directly on third-party vendor SDKs.
All tools are accessed via CAIRE platform abstraction layers.

UI / Backend / Jobs
↓
CAIRE Platform Layer
↓
Vendor SDKs (Sentry, PostHog, Flags, etc.)

---

## 13.1 Platform Modules (Required)

### Config Module

- Centralized, typed environment configuration
- Enables/disables tools per environment (dev/staging/prod)

### Telemetry Module (Errors & Events)

- `telemetry.error(error, context)`
- `telemetry.event(name, properties)`
  Wraps Sentry (and future telemetry providers)
- Auto-enrich: tenantId, userId, requestId, environment

### Analytics Module (Product Analytics)

- `analytics.track(eventName, properties)`
  Wraps PostHog
- Strict event schema
- No PII by default

### Feature Flags Module

- `flags.isEnabled(flagKey, context)`
  Server-side evaluation, tenant-aware
- Backed by Unleash (or LaunchDarkly later)

---

## 13.2 Frontend Integration (React + Vite)

- Initialize platform modules once in `main.tsx`
- Use a single React error boundary
- UI components never import vendor SDKs

---

## 13.3 Backend Integration (Express + Apollo)

- Platform modules initialized at server startup
- Request middleware attaches: tenantId, userId, requestId
- Global error handler routes errors to telemetry

---

## 13.4 Async Jobs & Optimisation Workers

- Use same platform modules as main app
- Emit lifecycle events: started / completed / failed
- Ensures consistent observability and analytics

---

## 14. Why This Architecture

This approach:

- Minimizes long-term maintenance
- Avoids vendor lock-in
- Enables safe enterprise pilots
- Supports GDPR & DPIA requirements
- Allows tooling to evolve without refactoring product code

---

## 15. Purpose of This Document

This document exists to:

- Onboard new team members and contractors
- Provide shared context across engineering, product, sales, operations
- Support audits, DPIA work, and enterprise customer reviews
- Ensure architectural and operational consistency as CAIRE scales
