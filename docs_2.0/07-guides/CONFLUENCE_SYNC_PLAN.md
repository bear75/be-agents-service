# Confluence Sync Strategy & Refactoring Plan Summary

**Last Updated:** 2025-12-08  
**Status:** Ready for Implementation  
**Confluence Space:** [TWC Space](https://caire.atlassian.net/wiki/spaces/TWC/overview?homepageId=393372)

---

## 🎯 Quick Summary

**Documentation:** ✅ Complete  
**Refactoring Plan:** ✅ Defined (Clean Slate Schema Creation + GraphQL API + Frontend)  
**Timeline:** 4-5 weeks with 2 developers (5-7 weeks with 1 developer)  
**Developer Time:** 224-320 hours (includes frontend)

---

## 📊 Confluence Sync Strategy

### What Goes to Confluence? (Stakeholder-Facing)

**Upload these 5 docs to Confluence:**

| Document                   | Why Confluence                          | Audience                      |
| -------------------------- | --------------------------------------- | ----------------------------- |
| **VISUAL_GUIDE.md** ⭐     | Diagrams, easy overview                 | Everyone (CTO, PM, Architect) |
| **REFACTORING_SUMMARY.md** | Executive summary                       | Management, stakeholders      |
| **architecture.md**        | Architecture decisions (needs approval) | Architect, CTO                |
| **MIGRATION_STRATEGY.md**  | Migration plan (needs sign-off)         | Architect, DBA, DevOps        |
| **prd/prd-umbrella.md**    | Product vision                          | Product, stakeholders         |

**Total:** 5 documents for collaboration and approval

### What Stays in Repository? (Developer-Facing)

**Keep these in GitHub (link from Confluence):**

| Document                                                            | Why Repo                      | Audience   |
| ------------------------------------------------------------------- | ----------------------------- | ---------- |
| **data-model-v2.md** ⭐                                             | Technical, changes frequently | Developers |
| **API_DESIGN_V2.md** ⭐                                             | Technical, changes frequently | Developers |
| **AUTH_STRATEGY.md**                                                | Technical reference           | Developers |
| **prd/bryntum-reference.md**                                        | Implementation guide          | Developers |
| **prd/Feature PRD – Bryntum Calendar View.md**                      | Feature specs                 | Developers |
| **prd/Feature PRD – Original Schedule-Import-Baseline-Creation.md** | Feature specs                 | Developers |

**Total:** 6 documents for technical reference

### Supporting Docs (Either Location)

| Document                      | Location | Purpose          |
| ----------------------------- | -------- | ---------------- |
| **INDEX.md**                  | Repo     | Navigation guide |
| **README.md**                 | Repo     | Quick start      |
| **DOC_STATUS.md**             | Repo     | Status tracking  |
| **BRYNTUM_EXAMPLES_GUIDE.md** | Either   | Examples catalog |

---

## 🔄 Sync Methods

### Option 1: Atlassian Rovo MCP Server (Recommended) ⭐

**Native Atlassian solution - works in Cursor!**

**Setup:**

1. Enable MCP in Cursor
2. Add server: `https://mcp.atlassian.com/v1/sse`
3. Complete OAuth 2.1 flow
4. Start syncing with natural language!

**Benefits:**

- ✅ Native Atlassian solution
- ✅ Real-time sync (no git push)
- ✅ Works directly in Cursor
- ✅ Natural language commands
- ✅ Secure OAuth 2.1

**Use cases:**

- "Create Confluence page from this markdown"
- "Update the refactoring summary page"
- "Search for architecture docs in Confluence"

**See:** `_confluence/ROVO_MCP_SETUP.md` for complete guide

**Reference:** [Official Rovo MCP Docs](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/)

---

### Option 2: Manual Copy/Paste (Start Here) ✅

**Steps:**

1. Go to [Confluence TWC Space](https://caire.atlassian.net/wiki/spaces/TWC/overview)
2. Create parent page: "CAIRE Refactoring Project"
3. Create child pages for each doc:
   - "Visual Guide" (copy from `VISUAL_GUIDE.md`)
   - "Refactoring Summary" (copy from `REFACTORING_SUMMARY.md`)
   - "Architecture" (copy from `architecture.md`)
   - "Migration Strategy" (copy from `MIGRATION_STRATEGY.md`)
   - "Product Vision" (copy from `prd/prd-umbrella.md`)
4. Add links section pointing to GitHub for technical docs

**Time:** ~30 minutes  
**Frequency:** Update when docs change (monthly)

### Option 3: GitHub Action (Automated) 🔄

**Setup automated sync:**

```yaml
# .github/workflows/sync-confluence.yml
name: Sync Docs to Confluence

on:
  push:
    paths:
      - "docs_refactor/VISUAL_GUIDE.md"
      - "docs_refactor/REFACTORING_SUMMARY.md"
      - "docs_refactor/architecture.md"
      - "docs_refactor/MIGRATION_STRATEGY.md"

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Sync to Confluence
        uses: cupcakearmy/confluence-markdown-sync@v1
        with:
          confluence-base-url: "https://caire.atlassian.net/wiki"
          confluence-space-key: "TWC"
          confluence-parent-page-id: "393372"
          files: |
            docs_refactor/VISUAL_GUIDE.md
            docs_refactor/REFACTORING_SUMMARY.md
            docs_refactor/architecture.md
            docs_refactor/MIGRATION_STRATEGY.md
          confluence-username: ${{ secrets.CONFLUENCE_USERNAME }}
          confluence-api-token: ${{ secrets.CONFLUENCE_API_TOKEN }}
```

**Time:** Setup once (1 hour)  
**Frequency:** Auto-sync on every push

### Option 4: Single Confluence Page with Links (Easiest) ⚡

**Create one page that links to GitHub:**

```markdown
# CAIRE Refactoring Documentation

## 🎯 Start Here

**For Architects/Developers:**

- [Visual Guide](https://github.com/yourorg/caire-platform/blob/main/appcaire/docs_refactor/VISUAL_GUIDE.md) ⭐
- [Database Schema](https://github.com/yourorg/caire-platform/blob/main/appcaire/docs_refactor/data-model-v2.md) ⭐
- [API Design](https://github.com/yourorg/caire-platform/blob/main/appcaire/docs_refactor/API_DESIGN_V2.md) ⭐

**For Management:**

- [Executive Summary](https://github.com/yourorg/caire-platform/blob/main/appcaire/docs_refactor/REFACTORING_SUMMARY.md)
- [Migration Plan](https://github.com/yourorg/caire-platform/blob/main/appcaire/docs_refactor/MIGRATION_STRATEGY.md)

**Architecture:**

- [System Architecture](https://github.com/yourorg/caire-platform/blob/main/appcaire/docs_refactor/architecture.md)
- [Auth Strategy](https://github.com/yourorg/caire-platform/blob/main/appcaire/docs_refactor/AUTH_STRATEGY.md)

**Product Requirements:**

- [Product Vision](https://github.com/yourorg/caire-platform/blob/main/appcaire/docs_refactor/prd/prd-umbrella.md)
- [Calendar View PRD](https://github.com/yourorg/caire-platform/blob/main/appcaire/docs_refactor/prd/Feature%20PRD%20–%20Bryntum%20Calendar%20View.md)
- [Bryntum Reference](https://github.com/yourorg/caire-platform/blob/main/appcaire/docs_refactor/prd/bryntum-reference.md)
```

**Time:** 5 minutes  
**Frequency:** Update links when docs move

---

## 📋 Recommended Confluence Structure

```
TWC Space
└── CAIRE Refactoring Project
    │
    ├── 📊 Visual Guide (VISUAL_GUIDE.md)
    │   └── All diagrams, architecture overview
    │
    ├── 📋 Executive Summary (REFACTORING_SUMMARY.md)
    │   └── Quick reference, timeline, cost
    │
    ├── 🏗️ Architecture (architecture.md)
    │   └── System design, tech stack
    │
    ├── 🔄 Migration Strategy (MIGRATION_STRATEGY.md)
    │   └── Database migration plan
    │
    ├── 🎯 Product Vision (prd/prd-umbrella.md)
    │   └── Overall product goals
    │
    └── 📁 Technical Specs (Links to GitHub)
        ├── → Database Schema (data-model-v2.md)
        ├── → API Design (API_DESIGN_V2.md)
        ├── → Auth Strategy (AUTH_STRATEGY.md)
        ├── → Bryntum Reference (bryntum-reference.md)
        └── → Feature PRDs (Feature PRD files)
```

---

## 🚀 Refactoring Plan Summary

### Overview

**Current State:**

- ❌ 319 Next.js API routes (messy)
- ❌ 40+ database tables (many unused)
- ❌ Drizzle ORM (partial type safety)
- ❌ Monolithic structure

**Target State:**

- ✅ ~60-85 GraphQL + REST operations (clean)
- ✅ 32 database tables (optimized)
- ✅ Prisma ORM (complete type safety)
- ✅ Monorepo (client/server/prisma)

**Timeline:** 4-5 weeks with 2 developers (5-7 weeks with 1 developer)  
**Developer Time:** 224-320 hours (includes frontend)

---

## 📅 Implementation Timeline

### Phase 1: Schema Refactoring (Days 1-5)

**Goal:** Migrate to new schema

**Tasks:**

- [ ] Review current schema (informational only - no backup needed)
- [ ] Generate Prisma schema from `data-model-v2.md`
- [ ] Create migration scripts
- [ ] Test on staging
- [ ] Deploy new schema
- [ ] Seed reference data (no data import needed)
- [ ] Verify relationships

**Deliverable:** New database schema live

**See:** `MIGRATION_STRATEGY.md`

---

### Phase 2: Core API (Week 1-2, parallel with DB)

**Goal:** Build GraphQL API foundation

**Tasks:**

- [ ] Setup monorepo (client/server/prisma)
- [ ] Setup Express + Apollo Server
- [ ] Setup Prisma client
- [ ] Implement auth middleware
- [ ] Create GraphQL schema
- [ ] Implement core resolvers:
  - Organizations (5 operations)
  - Employees (7 operations)
  - Clients (7 operations)
  - Schedules (10 operations)
  - Visits (6 operations)

**Deliverable:** Core CRUD operations working

**See:** `API_DESIGN_V2.md`

---

### Phase 3: Scheduling Features (Week 3)

**Goal:** Complete scheduling functionality

**Tasks:**

- [ ] Implement Visit Templates (7 operations)
- [ ] Implement Templates/Slinga (5 operations)
- [ ] Implement Schedule Groups (5 operations)
- [ ] Implement Optimization (7 operations)
- [ ] Implement Solutions (4 operations)
- [ ] Implement Scenarios (5 operations)
- [ ] Setup WebSocket subscriptions (3)

**Deliverable:** Full scheduling + optimization working

**See:** `API_DESIGN_V2.md`

---

### Phase 4: Analytics + REST (Week 4)

**Goal:** Complete API

**Tasks:**

- [ ] Implement Metrics (4 operations)
- [ ] Implement Analytics (4 operations)
- [ ] Implement REST endpoints (15):
  - Webhooks (5)
  - Files (3)
  - Integrations (3)
  - Auth (2)
  - Health (2)
- [ ] Complete API testing (>90% coverage)
- [ ] API documentation

**Deliverable:** Production-ready API

**See:** `../02-api/API_DESIGN_V2.md`

---

### Phase 5: Frontend Integration (Week 4-5, parallel with API)

**Goal:** Connect Bryntum prototype to GraphQL API

**Tasks:**

- [ ] Setup React + Vite + Apollo Client
- [ ] Copy Bryntum prototype components (already built!)
- [ ] Implement mapper functions (GraphQL ↔ Bryntum)
- [ ] Connect prototype to GraphQL queries/mutations
- [ ] Build simple CRUD pages (resources, analytics, admin)
- [ ] Real-time subscriptions for optimization progress
- [ ] Frontend testing

**Deliverable:** Working frontend with real data

**See:** `../08-frontend/FRONTEND_REFACTORING.md`

---

### Phase 6: Integration & Testing (Week 5)

**Goal:** End-to-end testing and polish

**Tasks:**

- [ ] Integration testing (frontend ↔ backend)
- [ ] E2E tests for critical flows
- [ ] Bug fixes and performance optimization
- [ ] Documentation complete

**Deliverable:** Production-ready application

---

## 🗄️ Database Migration Details

### Strategy: Clean Slate Migration ✅

**Why:**

- ✅ Pre-launch (downtime acceptable)
- ✅ Much faster than incremental (3-5 days vs 4+ weeks)
- ✅ No technical debt
- ✅ Clean foundation

**Process:**

1. **Days 1-2: Preparation**
   - Review current schema (informational only)
   - Create schema creation scripts
   - Test on staging

2. **Days 2-4: Schema Creation**
   - Generate new schema from `data-model-v2.md`
   - Create Prisma migrations
   - Seed reference data
   - Validate schema structure

3. **Day 5: Deployment**
   - Deploy to production
   - Verify relationships and indexes
   - Test schema

**Risk:** LOW ✅  
**Timeline:** 3-5 days (no data migration needed)  
**See:** `../04-migration/MIGRATION_STRATEGY.md`

---

## 🔌 API Refactoring Details

### Strategy: Build Fresh (Don't Port) ✅

**Why:**

- ❌ Current 319 routes are messy
- ❌ Many broken/unused
- ❌ Inconsistent patterns
- ✅ Fresh start = type-safe from day 1

### Tech Stack

**Backend:**

- Express (standalone server)
- Apollo Server (GraphQL)
- Prisma (ORM)
- WebSocket (subscriptions)

**Frontend:**

- React + Vite
- Apollo Client
- Bryntum SchedulerPro

**See:** `architecture.md`, `API_DESIGN_V2.md`

### API Structure

**GraphQL (Primary): ~71 operations**

- Queries: 30
- Mutations: 38
- Subscriptions: 3

**REST (Secondary): ~15 endpoints**

- Webhooks: 5
- Files: 3
- Integrations: 3
- Auth: 2
- Health: 2

**Total: ~60-85 operations** (vs 319 current)

**See:** `API_DESIGN_V2.md`

---

## 🔐 Authentication Strategy

### Current Pattern (KEEP) ✅

**Auth Bridge Table:**

```prisma
model OrganizationMember {
  id             String @id
  organizationId String
  userId         String @unique  // Clerk ID
  role           String
}
```

**Why this is good:**

- ✅ Isolates auth data to one table
- ✅ Easy to swap providers (1-2 days)
- ✅ Domain data stays clean

**Sync Method:**

```
Clerk webhook → POST /webhooks/clerk → organization_members table
```

**Auth at Every Endpoint:**

- ✅ Authentication (verify JWT)
- ✅ Authorization (check role)
- ✅ Multi-tenancy (scope to org)

**See:** `AUTH_STRATEGY.md`

---

## 📊 Key Metrics

### Database

| Metric            | Current | Target   | Improvement   |
| ----------------- | ------- | -------- | ------------- |
| **Tables**        | 40+     | 32       | 20% reduction |
| **Unused Tables** | ~8      | 0        | 100% cleanup  |
| **Type Safety**   | Partial | Complete | ✅ Full       |

### API

| Metric            | Current | Target    | Improvement       |
| ----------------- | ------- | --------- | ----------------- |
| **Endpoints**     | 319     | ~60-85    | 73% reduction     |
| **Type Safety**   | None    | Complete  | ✅ Full           |
| **Real-time**     | Polling | WebSocket | ✅ Live updates   |
| **Documentation** | Manual  | Auto      | ✅ Always current |

---

## ⏱️ Time Breakdown

| Component                 | Time                       |
| ------------------------- | -------------------------- |
| **Schema Refactoring**    | 24-40 hours (3-5 days)     |
| **API Development**       | 120-160 hours (3-4 weeks)  |
| **Frontend Development**  | 40-80 hours (1-2 weeks) ⚡ |
| **Integration & Testing** | 40 hours (1 week)          |
| **Total**                 | **224-320 hours**          |

---

## ✅ Success Criteria

### Database Migration

- [ ] All data migrated without loss
- [ ] All relationships validated
- [ ] Performance acceptable
- [ ] Rollback plan tested

### API Refactoring

- [ ] ~60-85 operations implemented
- [ ] All tests passing (>90% coverage)
- [ ] Type safety complete
- [ ] Real-time subscriptions working
- [ ] Documentation complete

### Prototype

- [ ] All features working with new API
- [ ] Data loading correctly
- [ ] Bryntum calendar rendering
- [ ] Optimization running
- [ ] Client feedback positive

---

## 📚 Document Reference

### Essential Reading (Architect/Developer)

1. **VISUAL_GUIDE.md** ⭐ (30 min)
   - All diagrams, complete overview

2. **data-model-v2.md** ⭐ (reference)
   - Complete database schema

3. **API_DESIGN_V2.md** ⭐ (reference)
   - GraphQL + REST API specification

### Supporting Documents

- **REFACTORING_SUMMARY.md** - Executive summary
- **architecture.md** - System architecture
- **MIGRATION_STRATEGY.md** - Database migration plan
- **AUTH_STRATEGY.md** - Auth implementation
- **prd/prd-umbrella.md** - Product vision
- **prd/bryntum-reference.md** - Implementation guide
- **prd/Feature PRD – Bryntum Calendar View.md** - Feature specs

**See:** `README.md` for complete navigation

---

## 🎯 Next Steps

### This Week

1. **Upload to Confluence**
   - Create "CAIRE Refactoring Project" page
   - Upload 5 stakeholder docs
   - Add links to GitHub for technical docs

2. **Team Alignment**
   - Review refactoring plan
   - Confirm timeline acceptable
   - Assign responsibilities

3. **Setup Development**
   - Create monorepo structure
   - Setup Prisma
   - Setup Express + Apollo
   - Test basic GraphQL query

### Next 2-4 Weeks

1. **Execute schema refactoring** (Days 1-5, no data migration needed)
2. **Build core API** (Week 1-2, parallel)
3. **Build scheduling features** (Week 3)
4. **Complete analytics + polish** (Week 4)
5. **Deploy and test** (Week 5)

---

## 🔗 Quick Links

**Confluence:**

- [TWC Space](https://caire.atlassian.net/wiki/spaces/TWC/overview?homepageId=393372)

**GitHub:**

- `docs_refactor/` - All documentation
- `docs_refactor/README.md` - Quick start
- `docs_refactor/INDEX.md` - Complete index

**Key Documents:**

- `VISUAL_GUIDE.md` - Start here ⭐
- `data-model-v2.md` - Schema reference ⭐
- `API_DESIGN_V2.md` - API specification ⭐

---

## 📝 Maintenance

### When to Update Confluence

**Update monthly or when:**

- Major architecture changes
- Timeline/cost changes
- Migration strategy updates
- New stakeholder questions

### When to Update Repo Docs

**Update immediately when:**

- Schema changes
- API changes
- Implementation details change
- New features added

**Sync frequency:** Monthly (or use GitHub Action for auto-sync)

---

## ✅ Summary Checklist

### Documentation ✅

- [x] All docs consolidated (11 → 3 essential)
- [x] Confluence sync strategy defined
- [x] Refactoring plan complete
- [x] Timeline and cost estimated

### Ready for Implementation ✅

- [x] Database schema defined (`data-model-v2.md`)
- [x] API design complete (`API_DESIGN_V2.md`)
- [x] Architecture documented (`architecture.md`)
- [x] Migration strategy clear (`MIGRATION_STRATEGY.md`)
- [x] Auth strategy documented (`AUTH_STRATEGY.md`)

### Next Actions ⏸️

- [ ] Upload to Confluence
- [ ] Team review
- [ ] Start implementation

---

**Status:** ✅ Ready to proceed with refactoring!

**Questions?** Check `README.md` or `INDEX.md` for guidance.
