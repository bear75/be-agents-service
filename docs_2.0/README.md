# CAIRE Refactoring Documentation

**Status:** ✅ Organized & Ready for Implementation  
**Confluence:** [TWC Space](https://caire.atlassian.net/wiki/spaces/TWC/overview?homepageId=393372)  
**Last Updated:** 2025-12-11

**Recent Updates:**

- **2025-12-10:** Added `preferredTimeWindows` jsonb field to `visits` table for Timefold waiting time reduction (soft constraint). This is stored per-visit, not in `client_preferences`. See `data-model-v2.md` for details.

---

## 🎯 Quick Start

**For Architects/Developers (Read These 3):**

1. **CAIRE Refactoring: Complete Visual Guide** ⭐ (30 min)
   - All diagrams, complete overview

2. **CAIRE Database Schema – Complete Data Model v2.0** ⭐ (reference)
   - Complete database schema

3. **API Design – GraphQL + Express + Prisma** ⭐ (reference)
   - GraphQL + REST API specification

**Total reading time:** ~1 hour

**📋 Understanding the Structure**: See [DOCUMENTATION_STRUCTURE.md](./DOCUMENTATION_STRUCTURE.md) for clarification on PRD vs Technical documentation organization.

---

## 📁 Complete Folder Structure

```
docs_2.0/
│
├── 01-architecture/          System design & architecture
│   ├── VISUAL_GUIDE.md       ⭐ All diagrams, overview
│   ├── architecture.md        System architecture
│   └── REFACTORING_SUMMARY.md Executive summary
│
├── 02-api/                   API specifications
│   ├── API_DESIGN_V2.md      ⭐ GraphQL + REST API
│   └── AUTH_STRATEGY.md      Authentication & authorization
│
├── 03-data/                  Database schema
│   └── data-model-v2.md      ⭐ Complete database schema
│
├── 04-migration/             Schema refactoring strategy
│   └── MIGRATION_STRATEGY.md Schema refactoring (3-5 days, no data migration)
│
├── 05-prd/                   Product requirements
│   ├── prd-umbrella.md       Product vision
│   ├── Feature PRD – Bryntum Calendar View.md
│   ├── Feature PRD – Original Schedule-Import-Baseline-Creation.md
│   ├── schedule-VISUAL_SYSTEM.md Visual system design
│   ├── bryntum_consultant_specs/ Consultant specs/requests (RFQ)
│   │   ├── BRYNTUM_BACKEND_SPEC.md
│   │   ├── BRYNTUM_FROM_SCRATCH_PRD.md
│   │   └── bryntum-reference.md
│   └── prototype/            Prototype documentation
│
├── 06-compliance/            Compliance & DPIA
│   └── DPIA/                 Data Protection Impact Assessment (13 files)
│
├── 07-guides/                Implementation guides
│   └── INDEX.md              ⭐ Complete document index & navigation
│
├── 08-frontend/              Frontend refactoring
│   ├── FRONTEND_REFACTORING.md ⭐ Frontend refactoring strategy
│   ├── COMPONENT_STRUCTURE.md  Component organization guide
│   └── BRYNTUM_INTEGRATION.md  Bryntum integration guide
│
├── 09-scheduling/            Scheduling system documentation
│   ├── README.md             ⭐ Scheduling documentation hub
│   ├── OVERVIEW.md                    Complete scheduling system overview
│   ├── PINNED_VISITS_GUIDE.md         Timefold pinning guide
│   ├── BACKEND_ARCHITECTURE.md        Backend architecture
│   ├── FRONTEND_INTEGRATION.md        Bryntum UI integration
│   ├── TIMEFOLD_INTEGRATION.md        Timefold API integration
│   ├── MOVABLE_VISITS.md              Movable visits guide
│   ├── PLANNING_WINDOW_STRATEGY.md    Planning window strategy
│   ├── BACKEND_PLANNING_WINDOW_SUPPORT.md Backend support verification
│   └── pilots/               Feature-specific pilot documentation
│       ├── README.md         Pilot documentation overview
│       └── attendo/          Attendo pilot
│           ├── PILOT_PLAN.md Attendo pilot plan
│           └── DATA_REQUIREMENTS.md Attendo data requirements
│
├── DOCUMENTATION_STRUCTURE.md ⭐ Guide to PRD vs Technical docs
│
├── _confluence/              Confluence sync configuration
│   ├── FRONTEND_REFACTORING.md ⭐ Frontend refactoring strategy
│   ├── COMPONENT_STRUCTURE.md  Component organization guide
│   └── BRYNTUM_INTEGRATION.md  Bryntum integration guide
│
├── 09-scheduling/            Scheduling system documentation
│   ├── README.md             ⭐ Scheduling documentation hub
│   ├── OVERVIEW.md                    Complete scheduling system overview
│   ├── PINNED_VISITS_GUIDE.md         Timefold pinning guide
│   ├── BACKEND_ARCHITECTURE.md        Backend architecture
│   ├── FRONTEND_INTEGRATION.md        Bryntum UI integration
│   ├── TIMEFOLD_INTEGRATION.md        Timefold API integration
│   ├── MOVABLE_VISITS.md              Movable visits guide
│   ├── PLANNING_WINDOW_STRATEGY.md    Planning window strategy
│   ├── BACKEND_PLANNING_WINDOW_SUPPORT.md Backend support verification
│   └── pilots/               Pilot-specific documentation
│       ├── README.md         Pilot documentation overview
│       └── attendo/          Attendo pilot
│           ├── PILOT_PLAN.md Attendo pilot plan
│           └── DATA_REQUIREMENTS.md Attendo data requirements
│   └── pilots/               Pilot-specific documentation
│       ├── README.md         Pilot documentation overview
│       └── attendo/          Attendo pilot
│           ├── PILOT_PLAN.md Attendo pilot plan
│           └── DATA_REQUIREMENTS.md Attendo data requirements
│
├── _confluence/              Confluence sync configuration
│   ├── SIMPLE_SYNC.md        ⭐ Sync guide (MCP + GitHub Action)
│   └── sync-config.yml       Sync configuration (reference)
│
├── archive/                  Old versions (13 files)
│
└── README.md                 This file - main entry point
```

**Document Count:** 45+ active files (including scheduling documentation)

---

## 📚 Document Categories

### Architecture (01-architecture/)

| Document                   | Purpose                         | Audience        |
| -------------------------- | ------------------------------- | --------------- |
| **VISUAL_GUIDE.md** ⭐     | All diagrams, complete overview | Everyone        |
| **architecture.md**        | System architecture             | Architects, CTO |
| **REFACTORING_SUMMARY.md** | Executive summary               | Management      |

### API (02-api/)

| Document                | Purpose                 | Audience   |
| ----------------------- | ----------------------- | ---------- |
| **API_DESIGN_V2.md** ⭐ | GraphQL + REST API spec | Developers |
| **AUTH_STRATEGY.md**    | Auth implementation     | Developers |

### Data (03-data/)

| Document                | Purpose                  | Audience         |
| ----------------------- | ------------------------ | ---------------- |
| **data-model-v2.md** ⭐ | Complete database schema | Developers, DBAs |

### Schema Refactoring (04-migration/)

| Document                  | Purpose                                                   | Audience         |
| ------------------------- | --------------------------------------------------------- | ---------------- |
| **MIGRATION_STRATEGY.md** | Schema refactoring strategy (3-5 days, no data migration) | Architects, DBAs |

### Product Requirements (05-prd/)

**Purpose**: Define **WHAT** features should do, **WHY** they're needed (business requirements).

| Document                                                        | Purpose                              | Audience              |
| --------------------------------------------------------------- | ------------------------------------ | --------------------- |
| **prd-umbrella.md**                                             | Product vision                       | Product, stakeholders |
| **Feature PRD – Bryntum Calendar View.md**                      | Calendar UI requirements             | Product, developers   |
| **Feature PRD – Original Schedule-Import-Baseline-Creation.md** | Schedule import requirements         | Product, developers   |
| **schedule-VISUAL_SYSTEM.md**                                   | Visual system design                 | Designers, developers |
| **bryntum_consultant_specs/**                                   | Consultant specs/requests (RFQ)      | Product, consultants  |
| - BRYNTUM_BACKEND_SPEC.md                                       | Backend API specs for consultants    | Consultants           |
| - BRYNTUM_FROM_SCRATCH_PRD.md                                   | Greenfield build approach (112-152h) | Consultants           |
| - bryntum-reference.md                                          | Implementation reference             | Consultants           |
| **prototype/**                                                  | Prototype documentation              | Developers            |

**Note**: The `bryntum_consultant_specs/` folder contains technical specs, but they're business requirements/requests for external consultants (RFQ documents), so they belong in `05-prd/`. See [DOCUMENTATION_STRUCTURE.md](./DOCUMENTATION_STRUCTURE.md) for details.

### Compliance (06-compliance/)

| Document                                 | Purpose                                  | Audience          |
| ---------------------------------------- | ---------------------------------------- | ----------------- |
| **DPIA/**                                | Data Protection Impact Assessment        | Legal, compliance |
| - README.md                              | DPIA overview                            |
| - 01_SYSTEM_DESCRIPTION.md               | System description                       |
| - 02_DATA_INVENTORY.md                   | Data inventory                           |
| - 03_INFORMATION_CLASSIFICATION.md       | Information classification               |
| - 04_DPIA_MAIN_DOCUMENT.md               | Main DPIA document                       |
| - 05_RISK_ANALYSIS.md                    | Risk analysis                            |
| - 06_DPA_AGREEMENT_DRAFT.md              | DPA agreement draft                      |
| - 07_RACI_MATRIX.md                      | RACI matrix                              |
| - 08_CONTRACTOR_DATA_ACCESS_AGREEMENT.md | Contractor data access                   |
| - 09_INTERNAL_DATA_ACCESS_POLICY.md      | Internal data access policy (compliance) |
| - APPENDIX_A_PILOT_SETUP.md              | Pilot setup appendix                     |
| - CONFLUENCE_SETUP_GUIDE.md              | Confluence setup guide                   |
| - updates.md                             | DPIA updates log                         |

### Guides (07-guides/)

| Document        | Purpose                              | Audience |
| --------------- | ------------------------------------ | -------- |
| **INDEX.md** ⭐ | Complete document index & navigation | Everyone |

### Frontend (08-frontend/)

| Document                       | Purpose                       | Audience   |
| ------------------------------ | ----------------------------- | ---------- |
| **FRONTEND_REFACTORING.md** ⭐ | Frontend refactoring strategy | Developers |
| **COMPONENT_STRUCTURE.md**     | Component organization guide  | Developers |
| **BRYNTUM_INTEGRATION.md**     | Bryntum integration guide     | Developers |

### Scheduling (09-scheduling/)

| Document                                   | Purpose                                        | Audience               |
| ------------------------------------------ | ---------------------------------------------- | ---------------------- |
| **README.md** ⭐                           | Scheduling documentation hub                   | Everyone               |
| **OVERVIEW.md**                            | Complete scheduling system overview            | Everyone               |
| **PINNED_VISITS_GUIDE.md**                 | Pinned visits & Timefold behavior              | Developers             |
| **BACKEND_ARCHITECTURE.md**                | Backend architecture (GraphQL, Prisma)         | Backend developers     |
| **FRONTEND_INTEGRATION.md**                | Bryntum UI integration                         | Frontend developers    |
| **TIMEFOLD_INTEGRATION.md**                | Timefold API integration                       | Developers             |
| **MOVABLE_VISITS.md**                      | Movable visits guide                           | Developers, planners   |
| **PLANNING_WINDOW_STRATEGY.md**            | Planning window strategy (longer horizons)     | Architects, developers |
| **BACKEND_PLANNING_WINDOW_SUPPORT.md**     | Backend support verification                   | Backend developers     |
| **PREPLANNING_BACKEND_ANALYSIS.md**        | Backend architecture analysis for pre-planning | Backend developers     |
| **PREPLANNING_FRONTEND_IMPLEMENTATION.md** | Pre-planning frontend implementation guide     | Frontend developers    |
| **pilots/**                                | Feature-specific pilot documentation           | Product, stakeholders  |
| - attendo/PILOT_PLAN.md                    | Attendo pilot plan (business + technical)      | Product, stakeholders  |
| - attendo/DATA_REQUIREMENTS.md             | Attendo data requirements (CSV format)         | Product, data team     |

**Note**: Pilot plans are feature-specific (scheduling), so they're in `09-scheduling/pilots/` rather than `05-prd/`. See [DOCUMENTATION_STRUCTURE.md](./DOCUMENTATION_STRUCTURE.md) for details.

---

## 🔄 Confluence Sync

**How to sync:** Use MCP in Cursor (recommended) or GitHub Action (automatic)

**Guide:** [`_confluence/SIMPLE_SYNC.md`](./_confluence/SIMPLE_SYNC.md) ⭐

**Configuration:** `_confluence/sync-config.yml`

---

## 🎯 By Task

### Starting the Refactoring

1. Read **CAIRE Refactoring: Complete Visual Guide** (get the big picture)
2. Review architecture document (understand target)
3. Check migration strategy document (migration approach)

### Implementing Database

1. Reference **CAIRE Database Schema – Complete Data Model v2.0** (complete schema)
2. Generate Prisma schema
3. Create migration

### Implementing API

1. Reference **API Design – GraphQL + Express + Prisma** (GraphQL spec)
2. Follow GraphQL schema examples
3. Implement resolvers

### Authentication Questions

1. Read authentication strategy document
2. Understand Clerk sync via webhooks
3. See how to swap auth providers

### Understanding Scheduling System

1. Start with **09-scheduling/README.md** (navigation hub)
2. Read **OVERVIEW.md** (complete system overview)
3. For backend: **BACKEND_ARCHITECTURE.md** (GraphQL, Prisma)
4. For frontend: **FRONTEND_INTEGRATION.md** (Bryntum UI)
5. For optimization: **TIMEFOLD_INTEGRATION.md** (Timefold API)
6. For planning windows: **PLANNING_WINDOW_STRATEGY.md** (longer horizons)

### Working with Pilots

**Attendo Pilot:**

1. Read **09-scheduling/pilots/attendo/PILOT_PLAN.md** (pilot objectives & phases)
2. Review **09-scheduling/pilots/attendo/DATA_REQUIREMENTS.md** (CSV format specification)
3. Understand data mapping from eCare CSV to Timefold INPUT

**Other Pilots:**

- See **09-scheduling/pilots/README.md** for available pilots

---

## 📊 Quick Reference

| Question                     | Document                                                              |
| ---------------------------- | --------------------------------------------------------------------- |
| How does auth work?          | Authentication Strategy document                                      |
| What's the database schema?  | CAIRE Database Schema – Complete Data Model v2.0                      |
| What's the API design?       | API Design – GraphQL + Express + Prisma                               |
| How to refactor schema?      | Schema Refactoring Strategy (3-5 days)                                |
| How to refactor frontend?    | Frontend Refactoring Strategy (1-2 weeks) ⚡ Prototype already built! |
| What's the architecture?     | Architecture document                                                 |
| What's the timeline?         | Refactoring Summary document                                          |
| Where to start?              | CAIRE Refactoring: Complete Visual Guide ⭐                           |
| What's PRD vs Technical?     | DOCUMENTATION_STRUCTURE.md ⭐ (Understanding the structure)           |
| How does scheduling work?    | 09-scheduling/OVERVIEW.md ⭐                                          |
| What are pinned visits?      | 09-scheduling/PINNED_VISITS_GUIDE.md                                  |
| How to use planning windows? | 09-scheduling/PLANNING_WINDOW_STRATEGY.md                             |
| What's the Attendo pilot?    | 09-scheduling/pilots/attendo/PILOT_PLAN.md                            |

---

## 🚀 Implementation Status

### Documentation ✅ COMPLETE

- [x] Organized into folders
- [x] Confluence sync configured
- [x] All essential docs ready

### Implementation ⏸️ READY TO START

- [ ] Schema refactoring (3-5 days, no data migration)
- [ ] API development (3-4 weeks)
- [ ] Prototype features
- [ ] Testing and QA

---

## 🔗 External Links

- **Confluence:** [TWC Space](https://caire.atlassian.net/wiki/spaces/TWC/overview?homepageId=393372)
- **Atlassian Wiki:** For PRD discussions
- **GitHub:** This repository

---

## 📝 Maintenance

**When to update:**

- Schema changes → Update **CAIRE Database Schema – Complete Data Model v2.0**
- API changes → Update **API Design – GraphQL + Express + Prisma**
- Architecture changes → Update architecture document

**Sync frequency:** Monthly (or auto-sync via GitHub Action)

---

**Questions?**

- Check [`07-guides/INDEX.md`](./07-guides/INDEX.md) for complete document navigation
