# CAIRE Scheduling Platform – Architecture & Tech Stack

This document describes the high-level architecture, technology stack, and visual diagrams for the refactored CAIRE platform. It aligns with the umbrella PRD, the updated data model, and the new technology stack (React/Vite, Express/GraphQL, Prisma/PostgreSQL). The goal is to provide a clear mental model of the system's components, interactions, and responsibilities, enabling engineers to refactor legacy code into a well-structured, maintainable codebase.

---

## Architectural Goals

- **Separation of concerns**: Decouple the front-end, API layer, domain services, and external integrations. Each layer has a well-defined responsibility and communicates through clear interfaces.

- **Domain-driven design**: Model home-care scheduling concepts (organizations, schedules, visits, employees, constraints) explicitly in the data layer and services. Avoid leaking solver-specific details into the domain model.

- **Scalability and extensibility**: Support many organisations with large schedules while allowing new features (real-time telemetry, AI forecasting) and integrations to be added without major rewrites.

- **Testability and maintainability**: Facilitate unit and integration testing by keeping pure functions free of side effects. Use dependency injection and modular design to enable mocking and substitution.

- **Cloud-native deployment**: Deploy services in a scalable environment (Docker/Kubernetes), use managed databases (e.g. Supabase/PostgreSQL), and provide CI/CD pipelines for continuous delivery.

---

## Current State vs Target State

### Current Architecture (Legacy)

```
┌─────────────────────────────────────────────────────────┐
│                    Next.js Monolith                     │
│                                                         │
│  ┌─────────────┐    ┌──────────────┐                  │
│  │   Frontend  │◄──►│ API Routes   │                  │
│  │   (React)   │    │  (319 files) │                  │
│  └─────────────┘    └──────┬───────┘                  │
│                            │                            │
│                     ┌──────▼───────┐                   │
│                     │    Prisma    │                   │
│                     │     ORM      │                   │
│                     └──────┬───────┘                   │
└────────────────────────────┼────────────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │   PostgreSQL     │
                    │  (current schema)│
                    └──────────────────┘
```

**Problems:**

- ❌ Monolithic structure
- ❌ 319 API routes (messy)
- ❌ No type safety end-to-end
- ❌ No real-time updates
- ❌ Hard to test
- ❌ Schema issues

### Target Architecture (Refactored)

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Monorepo                                  │
│                                                                     │
│  ┌──────────────────┐         ┌─────────────────────────────────┐ │
│  │ packages/client/ │         │      packages/server/          │ │
│  │                  │         │                                 │ │
│  │  React + Vite    │         │    Express + Apollo             │ │
│  │  + Bryntum       │         │    + GraphQL                    │ │
│  │                  │         │                                 │ │
│  │  ┌────────────┐  │         │  ┌──────────────────────────┐  │ │
│  │  │   Apollo   │  │◄────────┼─►│  GraphQL Schema          │  │ │
│  │  │   Client   │  │ GraphQL │  │  (~71 operations)        │  │ │
│  │  └────────────┘  │         │  └───────────┬──────────────┘  │ │
│  │                  │         │              │                  │ │
│  │  ┌────────────┐  │         │  ┌───────────▼──────────────┐  │ │
│  │  │ WebSocket  │  │◄────WS──┼─►│     Resolvers            │  │ │
│  │  │   Client   │  │         │  │  (Business Logic)        │  │ │
│  │  └────────────┘  │         │  └───────────┬──────────────┘  │ │
│  └──────────────────┘         │              │                  │ │
│                               │  ┌───────────▼──────────────┐  │ │
│                               │  │      Services            │  │ │
│                               │  │  (Domain Logic)          │  │ │
│                               │  └───────────┬──────────────┘  │ │
│  ┌──────────────────┐         │              │                  │ │
│  │ packages/prisma/ │         │  ┌───────────▼──────────────┐  │ │
│  │                  │         │  │      Prisma Client       │  │ │
│  │  Schema + Migrations       │  │  (Type-safe ORM)         │  │ │
│  └──────────────────┘         │  └───────────┬──────────────┘  │ │
│                               └──────────────┼──────────────────┘ │
└────────────────────────────────────────────┼────────────────────┘
                                              │
                                    ┌─────────▼──────────┐
                                    │    PostgreSQL      │
                                    │   (new schema)     │
                                    └────────────────────┘
```

**Benefits:**

- ✅ Modular monorepo
- ✅ ~60-85 operations (clean)
- ✅ Complete type safety
- ✅ Real-time subscriptions
- ✅ Easy to test
- ✅ Optimized schema

---

## High-Level Component Diagram

At a high level, the platform consists of three major packages managed in a monorepo (e.g. with Turborepo):

```
appcaire-v2/
├── packages/
│   ├── client/    # React + Vite front-end (UI and UX)
│   ├── server/    # Express + GraphQL API (HTTP & WebSocket)
│   └── prisma/    # Shared Prisma schema and migrations
└── turbo.json    # Build and caching config
```

---

## Technology Stack

### Core Architectural Practices

#### Typed API Layer

**Decision: GraphQL primary, REST secondary**

- **GraphQL** (~71 operations) provides strong typing, flexible queries, and real-time subscriptions via WebSocket. Apollo Server handles schema, resolvers, and subscriptions.
- **REST** (~15 endpoints) handles webhooks, file operations, and health checks where GraphQL is less suitable.
- End-to-end TypeScript type safety from Prisma schema → GraphQL schema → frontend via code generation.

#### Separate Concerns

**Decision: Monorepo with three packages**

- **Client** (`packages/client/`): React 18 + Vite frontend
- **Server** (`packages/server/`): Express.js standalone API server (not Next.js)
- **Prisma** (`packages/prisma/`): Shared schema and migrations

Clear boundaries between UI, API, services, and data layers enable independent development, testing, and deployment.

#### Relational Database with Schema-Aware ORM

**Decision: PostgreSQL + Prisma**

- PostgreSQL 15+ for relational data, JSONB columns, array types, and advanced indexing
- Prisma ORM provides schema-first design, type-safe queries, and robust migrations
- Single source of truth in `schema.prisma` with auto-generated TypeScript types
- Normalized data model from `data-model-v2.md` ensures data integrity and query performance

#### Event-Driven Background Jobs

**Decision: BullMQ for job queue**

- Offload long-running optimization jobs to background workers
- Handle retries, job status tracking, and progress updates
- Job status exposed via GraphQL subscriptions for real-time UI updates
- Supports multiple parallel optimization runs per organization

#### Modular Normalised Data Model

Adopt the three-layer architecture described in your internal docs (external data → mappers → standardised JSON → normalised tables). This ensures each schedule maintains its own input and output data and simplifies AI model training.

### Stack Overview

| Layer         | Technology                           | Rationale                                                  |
| ------------- | ------------------------------------ | ---------------------------------------------------------- |
| **Frontend**  | React 18 + Vite + TypeScript         | Fast development, optimized builds, no SSR overhead needed |
| **Routing**   | React Router                         | Client-side routing sufficient for authenticated app       |
| **State**     | Apollo Client + Zustand              | GraphQL state management + minimal global state            |
| **UI**        | Tailwind CSS + shadcn/ui             | Utility-first CSS + component library                      |
| **Calendar**  | Bryntum SchedulerPro                 | Industry-standard scheduling component                     |
| **Backend**   | Express.js + Apollo Server           | Standalone server, flexible deployment                     |
| **API**       | GraphQL (primary) + REST (secondary) | Type-safe queries, real-time subscriptions, webhooks       |
| **Database**  | PostgreSQL 15+                       | Robust relational database with JSONB support              |
| **ORM**       | Prisma                               | Schema-first, type-safe, excellent migration support       |
| **Jobs**      | BullMQ                               | Reliable job queue for optimization tasks                  |
| **Auth**      | Clerk                                | Managed identity and organization management               |
| **Real-time** | WebSocket subscriptions              | Live optimization progress updates                         |

### Frontend Stack Visual

```
┌─────────────────────────────────────────┐
│         packages/client/                │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │        React 18                 │   │
│  │        + TypeScript              │   │
│  └──────────────┬──────────────────┘   │
│                 │                       │
│  ┌──────────────▼──────────────────┐   │
│  │         Vite                     │   │
│  │    (Build tool & dev server)    │   │
│  └──────────────┬──────────────────┘   │
│                 │                       │
│  ┌──────────────▼──────────────────┐   │
│  │      Apollo Client              │   │
│  │   (GraphQL + WebSocket)         │   │
│  └──────────────┬──────────────────┘   │
│                 │                       │
│  ┌──────────────▼──────────────────┐   │
│  │    Bryntum SchedulerPro         │   │
│  │    (Calendar UI Component)      │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Backend Stack Visual

```
┌─────────────────────────────────────────┐
│         packages/server/                │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │        Express                  │   │
│  │    (HTTP Server)                │   │
│  └──────────────┬──────────────────┘   │
│                 │                       │
│  ┌──────────────▼──────────────────┐   │
│  │     Apollo Server               │   │
│  │   (GraphQL Engine)              │   │
│  └──────────────┬──────────────────┘   │
│                 │                       │
│  ┌──────────────▼──────────────────┐   │
│  │       Resolvers                 │   │
│  │   (GraphQL Functions)           │   │
│  └──────────────┬──────────────────┘   │
│                 │                       │
│  ┌──────────────▼──────────────────┐   │
│  │       Services                  │   │
│  │   (Business Logic)              │   │
│  └──────────────┬──────────────────┘   │
│                 │                       │
│  ┌──────────────▼──────────────────┐   │
│  │     Prisma Client               │   │
│  │   (Type-safe ORM)               │   │
│  └──────────────┬──────────────────┘   │
└──────────────────┼──────────────────────┘
                   │
         ┌─────────▼──────────┐
         │    PostgreSQL      │
         │   (New Schema)     │
         └────────────────────┘
```

### Database Stack Visual

```
┌─────────────────────────────────────────┐
│         packages/prisma/                │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │      schema.prisma              │   │
│  │  (From data-model-v2.md)        │   │
│  └──────────────┬──────────────────┘   │
│                 │                       │
│                 │ Generate              │
│                 ▼                       │
│  ┌─────────────────────────────────┐   │
│  │   Prisma Client (Generated)     │   │
│  │   - TypeScript types            │   │
│  │   - Query builder               │   │
│  └──────────────┬──────────────────┘   │
│                 │                       │
│                 │ Migrate               │
│                 ▼                       │
│  ┌─────────────────────────────────┐   │
│  │      migrations/                │   │
│  │   - SQL migration files         │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## Component Details

### Front-End (`packages/client/`)

- **Framework**: React 18 with Vite for fast local development and build times. The app uses TypeScript, Tailwind or another utility CSS framework, and a component library like shadcn/ui for consistent UI elements.

- **Routing**: Vite does not provide built-in routing; use React Router for client-side navigation. Alternatively, consider Next.js or Remix if server-side rendering, static generation or SEO become priorities.

- **State management**: Use React context, hooks and possibly a state management library (e.g. Zustand) for global state (current organisation, user session, schedules being edited). Apollo Client or urql manages GraphQL queries, mutations and caching.

- **Authentication**: Integrate Clerk's React SDK to handle sign-in/sign-up, organisation selection and token management. Include role-based guards to restrict access to certain routes.

- **UI Composition**: Break the UI into feature modules (Original Schedule, Optimisation Jobs, Baselines, Movable Visits, Templates, Comparisons, Analytics, Resources, Admin) under `/src/features/`. Shared components live in `/src/components/`. Custom hooks (e.g. `useSchedules`) live in `/src/hooks/`.

- **Real-time updates**: Use GraphQL subscriptions over WebSockets to stream optimisation progress and solution updates to the UI. Employ optimistic UI patterns when updating schedules.

### API & Services (`packages/server/`)

- **Framework**: An Express server hosts both the GraphQL API and any REST endpoints required for legacy compatibility. The GraphQL layer uses Apollo Server or Yoga to define the schema, resolvers and context (user, organisation).

- **GraphQL Schema**: The schema exposes queries and mutations that align with the domain model (e.g. `getSchedules`, `createOriginalSchedule`, `updateVisit`, `runOptimisation`, `getSolutionMetrics`). Types map directly to Prisma models. Subscriptions are used for long-running jobs and real-time notifications. **Schema files are the single source of truth** (see `../02-api/GRAPHQL_SCHEMA_SPECIFICATION.md`).

- **API Design**:
  - **Primary**: GraphQL (~71 operations)
    - ~30 Queries (organizations, employees, clients, schedules, visits, templates, metrics)
    - ~38 Mutations (CRUD operations for all resources)
    - ~3 Subscriptions (optimizationProgress, solutionUpdated, scheduleUpdated)
  - **Secondary**: REST (~15 endpoints)
    - Webhooks (Clerk, Timefold, Carefox, Phoniro, eCare)
    - File operations (upload, download, export)
    - Auth endpoints (token refresh, current user)
    - Health checks

- **Service layer**: Business logic resides in domain services under `/src/services/`. These services perform validation, apply labour rules, orchestrate imports (Carefox, CSV), prepare solver input, call the solver adapter, process results, and manage transactions.

- **Integration layer**: `/src/integrations/` contains adapters for external systems (Carefox API client, Phoniro CSV importer, eCare client, GPS feed handler, Timefold solver client). Each adapter translates between external schemas and internal domain models via mappers.

- **Background jobs**: Use a job queue (e.g. BullMQ or a managed queue like AWS SQS + Lambda) to offload heavy tasks such as optimisation runs, pre-planning computations or large data imports. Job status is stored in the database and surfaced via GraphQL subscriptions.

- **Authentication & authorisation**: Middleware verifies Clerk JWTs, loads the user and organisation context, and checks role permissions. A policy layer ensures that users can only access or mutate resources belonging to their organisation.

### Data & Persistence (`packages/prisma/`)

- **Database**: PostgreSQL serves as the primary data store. Prisma's schema defines tables for organisations, templates, visit templates, schedule groups, schedules, problems, solutions, visits, employees, clients, service areas, vehicles, skills, tags, labour rules, metrics and administrative tables (users, organisation_members, plans, subscriptions, settings, API keys) as described in the updated data model.

- **Migrations**: Prisma migrations live in `packages/prisma/migrations/`. Seed scripts populate reference data (e.g. default scenarios, sample service areas) and can be extended to import real data for development.

- **Repository pattern**: The server exposes data access through repositories or data access services, encapsulating Prisma queries and transactions. This abstraction facilitates unit testing and future ORM changes.

- **No internal JSON blobs**: The database stores normalised rows and references the solver's dataset ID instead of storing raw input/output. Snapshots can be retrieved from Timefold or reconstructed on demand from the domain tables.

---

## Operations Breakdown

### GraphQL Operations: 71

```
Queries (30)              Mutations (38)           Subscriptions (3)
├─ Organizations (2)      ├─ Organizations (3)     ├─ optimizationProgress
├─ Employees (3)          ├─ Employees (4)         ├─ solutionUpdated
├─ Clients (3)            ├─ Clients (4)           └─ scheduleUpdated
├─ Schedules (4)          ├─ Schedules (5)
├─ Visits (2)             ├─ Visits (4)
├─ Visit Templates (2)    ├─ Visit Templates (5)
├─ Templates (2)          ├─ Templates (3)
├─ Schedule Groups (2)    ├─ Schedule Groups (3)
├─ Optimization (2)      ├─ Optimization (3)
├─ Solutions (3)          ├─ Solutions (1)
├─ Scenarios (2)         └─ Scenarios (3)
└─ Metrics (4)

Total GraphQL: ~71 operations
```

### REST Endpoints: 15

```
Webhooks (5)              Files (3)                Integration (3)
├─ Clerk                  ├─ Upload                ├─ Carefox token
├─ Timefold              ├─ Download              ├─ Timefold token
├─ Carefox               └─ Export                └─ Mapbox token
├─ Phoniro
└─ eCare                 Auth (2)                 Health (2)
                         ├─ Token refresh         ├─ Health check
                         └─ Current user          └─ DB health

Total REST: ~15 endpoints
```

**Grand Total: ~60-85 operations/endpoints**

---

## Data Flow Diagrams

### Schedule Optimization Flow

```
Frontend (React)
    │
    │ 1. Mutation: runOptimization
    ├──────────────────────────────────────┐
    │                                      │
    ▼                                      │
GraphQL API (Apollo)                       │
    │                                      │
    │ 2. Create solution record            │
    ▼                                      │
Prisma → PostgreSQL                        │
    │                                      │
    │ 3. Enqueue job                       │
    ▼                                      │
BullMQ / Background Job                    │
    │                                      │
    │ 4. Call Timefold                     │
    ▼                                      │
Timefold Solver                            │
    │                                      │
    │ 5. Progress updates                  │
    │                                      │
    ▼                                      │
WebSocket Subscription ◄───────────────────┘
    │
    │ 6. Publish progress
    ▼
Frontend (React)
    │
    │ Progress bar updates automatically
    ▼
User sees real-time progress! ✨
```

### Type Safety Flow

```
1. Database Schema (Prisma)
   ↓
   schema.prisma
   ↓ prisma generate
   ↓
2. TypeScript Types (Auto-generated)
   ↓
   PrismaClient with full types
   ↓
3. GraphQL Schema
   ↓
   schema.graphql (matches Prisma models)
   ↓ graphql-codegen
   ↓
4. Frontend Types (Auto-generated)
   ↓
   useGetScheduleQuery() - fully typed!
   ↓
5. Bryntum Config
   ↓
   Typed data mapping
   ↓
6. UI Components
   ↓
   No 'any' types - everything typed!
```

**Result:** Zero type mismatches, compile-time safety

---

## Migration Flow

### Database Migration Flow

**Clean Slate Approach - No Data Migration Needed** ✅

```
┌──────────────────┐
│  Current Schema  │
│  (Legacy)         │
│  - 40+ tables     │
│  - Issues         │
└────────┬──────────┘
         │
         │ 1. Create new schema
         │    (No backup needed - clean slate)
         ▼
┌──────────────────┐
│  New Schema      │
│  (Prisma)        │
│  - Clean design  │
│  - From data-    │
│    model-v2.md   │
└────────┬─────────┘
         │
         │ 2. Seed reference data only
         │    (Scenarios, configs - no user data)
         ▼
┌──────────────────┐
│  Reference Data  │
│  - Scenarios     │
│  - Configs       │
│  - Test fixtures │
└────────┬─────────┘
         │
         │ 3. Verify & Deploy
         ▼
┌──────────────────┐
│  Production      │
│  (New Schema)    │
│  Clean Slate ✅  │
└──────────────────┘
```

**Key Points:**

- ✅ No data migration needed (pre-launch, clean slate)
- ✅ Only reference data seeding (scenarios, configs)
- ✅ No user/org data to migrate
- ✅ Faster implementation (3-5 days vs 4+ weeks)

### API Migration Flow

**Don't Port, Build Fresh**

```
┌─────────────────────────────┐
│   Current API (Next.js)     │
│   - 319 route files         │
│   - Inconsistent            │
│   - Many broken             │
└──────────┬──────────────────┘
           │
           │ ❌ DON'T PORT
           │
           ▼
    ┌──────────────┐
    │   ARCHIVE    │
    │  (reference) │
    └──────────────┘

┌─────────────────────────────┐
│   Requirements (PRDs)       │
│   - Feature specs           │
│   - User flows              │
└──────────┬──────────────────┘
           │
           │ ✅ BUILD FRESH
           ▼
┌─────────────────────────────┐
│   New API (Express)         │
│   - GraphQL (71 operations) │
│   - REST (15 endpoints)      │
│   - Type-safe (Prisma)      │
│   - Real-time (WebSocket)   │
└─────────────────────────────┘
```

### Schema Migration Visual

```
Current (Legacy)                     New (Prisma)
├─ organizations                     ├─ organizations ✅
├─ employees                         ├─ employees ✅
├─ clients                           ├─ clients ✅
├─ schedules                         ├─ schedules ✅ (enhanced)
├─ visits                            ├─ visits ✅ (enhanced)
├─ scheduleEmployees                 ├─ schedule_employees ✅ (renamed)
├─ optimizationJobs                  ├─ solutions ✅ (refactored)
├─ solutionVisitAssignments          ├─ solution_assignments ✅
├─ movableVisits                     ├─ visit_templates ✅ (refactored)
├─ serviceAreas                      ├─ service_areas ✅
├─ scenarios                         ├─ scenarios ✅
├─ [unused tables]                   ├─ [REMOVED]
│                                    │
│                                    ├─ templates ➕ NEW
│                                    ├─ template_visits ➕ NEW
│                                    ├─ schedule_groups ➕ NEW
│                                    ├─ problems ➕ NEW
│                                    ├─ addresses ➕ NEW
│                                    ├─ solution_events ➕ NEW
│                                    ├─ schedule_metrics ➕ NEW
│                                    └─ [8 more new tables]
```

**Changes:**

- ✅ Keep: 15 tables (with enhancements)
- ⚠️ Refactor: 5 tables (rename/restructure)
- ➕ Add: 12 new tables
- ❌ Remove: Deprecated/unused tables

---

## External Integrations

- **Timefold Solver**: The solver client submits problems and patch operations and polls for job completion. Dataset IDs returned by Timefold are stored in solutions. Fine-tune runs use the from-patch endpoint to avoid cloning problems. KPIs and solution events are imported and normalised via mappers.

- **Carefox, eCare, Phoniro**: Importers fetch or parse data from these systems and map to visit templates, clients and employees. They create or update schedules accordingly. Exporters may push optimised schedules back to these systems when required.

- **GPS & Telemetry**: Real-time location updates are ingested via a stream (e.g. WebSockets, Kafka or MQTT) and can trigger re-optimisation or updates to solution events.

- **Authentication (Clerk)**: Offload identity management; use webhooks to synchronize organisation membership changes. The server validates tokens and enforces RBAC.

---

## Interaction Flows

- **Original schedule import**: A scheduler calls `createOriginalSchedule` via GraphQL. The API validates the payload, stores it as a problem and schedule, enqueues an optimisation job and returns a schedule ID. The client subscribes to `onOptimisationProgress` to show job status. Once complete, the server processes the solver output and updates the solution tables.

- **Manual baseline creation**: After an original schedule exists, the scheduler triggers `createBaseline`. The server derives a baseline problem from the original (fixed time windows), stores a new schedule record and marks it as baseline.

- **Movable visit pre-planning**: The scheduler creates or updates visit templates. Pre-planning runs generate proposed day/time assignments based on capacity and scenario settings. Results are stored in `proposed_changes` and surfaced via the UI.

- **Fine-tune optimisation**: A scheduler adjusts a visit's time window or changes constraints. The server computes patch operations against the existing solver dataset, invokes the from-patch endpoint and updates the solution record. Assignments and metrics are updated incrementally.

- **Real-time adjustments** (future): Telemetry events trigger updates to solution events and may enqueue a re-optimisation job. Subscriptions notify the client of new assignment recommendations.

---

## DevOps & Deployment

- **Monorepo builds**: Turborepo coordinates builds of client and server packages, sharing cache where possible. CI pipelines run linting, type checking, unit tests (Vitest), integration tests (Playwright) and deploy preview environments.

- **Containerisation**: Build Docker images for the server and client. Use multi-stage builds to optimise image size. Deploy to Kubernetes or a serverless container platform.

- **Environment & configuration**: Use `.env` files for secrets in development and a secrets manager (e.g. AWS Secrets Manager) in production. Configuration includes database connection strings, Clerk keys, external API credentials and solver endpoints.

- **Observability**: Integrate logging, metrics and tracing via a platform like Grafana/Prometheus or Datadog. Monitor job durations, API latencies, solver response times and database queries. Alert on failures (failed imports, optimisation timeouts, subscription billing issues).

---

## Key Architecture Decisions

1. **Monorepo Structure**: Three packages (client, server, prisma) enable code sharing and type safety
2. **GraphQL Primary**: ~71 operations provide flexible queries and real-time subscriptions
3. **Clean Slate Migration**: New Prisma schema without legacy technical debt
4. **Express Standalone**: Not Next.js, allowing independent frontend/backend deployment
5. **Type Safety End-to-End**: Database → Prisma → GraphQL → Frontend with auto-generated types

---

## Future Considerations

- **Server-side rendering (SSR)**: If SEO or public marketing pages become important, you might adopt Next.js or Remix for the front-end. This would also enable API routes within the same framework, though a standalone Express server offers more flexibility.

- **Microservices**: As the platform grows, core services (scheduling, optimisation orchestration, integrations, analytics) could be extracted into separate microservices communicating via a message bus. Start with a modular monolith to keep complexity manageable.

- **AI & ML pipelines**: Future features such as demand forecasting and automatic scenario recommendations will require model training workflows. Consider using a feature store and model repository and integrate them as a separate service that feeds suggestions back into scheduling.

- **AI/ML Infrastructure**: AWS SageMaker pipelines and feature store, as described in the AI-OS roadmap, for training cancellation/continuity models and feeding results back into the optimiser.

---

## Related Documents

- **Timeplan**: `timeplan.md` - Implementation timeline and planning
- **Data Model**: `data-model-v2.md` - Complete schema reference
- **API Design**: `API_DESIGN_V2.md` - Complete GraphQL + REST API spec
- **Migration Strategy**: `MIGRATION_STRATEGY.md` - Database migration plan
- **Auth Strategy**: `AUTH_STRATEGY.md` - Auth implementation & independence

---

This architecture document provides a high-level blueprint for refactoring CAIRE into a modular, scalable platform. Each feature PRD and service implementation should trace back to this architecture to ensure consistency and alignment.
