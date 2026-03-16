# 📋 Documentation Index

**Purpose:** ⭐ **Complete document catalog and navigation**  
**Last Updated:** 2025-12-08  
**Status:** ✅ Organized & Ready

> **Note:** This is the main navigation document. For folder structure, see [`../README.md`](../README.md).

---

## 🎯 Start Here

**New to the refactoring project?** Read these 3 docs (total ~1 hour):

1. **[01-architecture/VISUAL_GUIDE.md](../01-architecture/VISUAL_GUIDE.md)** ⭐ - All diagrams, complete overview (30 min)
2. **[03-data/data-model-v2.md](../03-data/data-model-v2.md)** ⭐ - Complete database schema (20 min)
3. **[02-api/API_DESIGN_V2.md](../02-api/API_DESIGN_V2.md)** ⭐ - GraphQL + REST API spec (20 min)

**That's it!** Everything you need is in those 3 files.

**Quick reference:**

- Architecture questions → `01-architecture/architecture.md`
- Auth questions → `02-api/AUTH_STRATEGY.md`
- Migration plan → `04-migration/MIGRATION_STRATEGY.md`
- Executive summary → `01-architecture/REFACTORING_SUMMARY.md`

---

## 📁 Folder Structure

```
docs_refactor/
├── 01-architecture/          System design & architecture
├── 02-api/                  API specifications
├── 03-data/                 Database schema
├── 04-migration/             Migration plans
├── 05-prd/                  Product requirements
├── 06-compliance/           Compliance & DPIA
├── 07-guides/               Implementation guides
├── _confluence/             Confluence sync configuration
└── archive/                 Old versions
```

---

## 📚 All Documents by Category

### Architecture (01-architecture/)

| Document                   | Purpose                             | Read Time | Priority |
| -------------------------- | ----------------------------------- | --------- | -------- |
| **VISUAL_GUIDE.md** ⭐     | All diagrams, architecture overview | 30 min    | ⭐⭐⭐   |
| **architecture.md**        | Target architecture                 | 15 min    | ⭐⭐     |
| **REFACTORING_SUMMARY.md** | Executive summary                   | 5 min     | ⭐⭐     |

### API (02-api/)

| Document                | Purpose                            | Read Time | Priority |
| ----------------------- | ---------------------------------- | --------- | -------- |
| **API_DESIGN_V2.md** ⭐ | GraphQL + REST API specification   | 20 min    | ⭐⭐⭐   |
| **AUTH_STRATEGY.md**    | Auth implementation & independence | 15 min    | ⭐⭐     |

### Data (03-data/)

| Document                | Purpose                  | Read Time | Priority |
| ----------------------- | ------------------------ | --------- | -------- |
| **data-model-v2.md** ⭐ | Complete database schema | 20 min    | ⭐⭐⭐   |

### Migration (04-migration/)

| Document                  | Purpose                 | Read Time | Priority |
| ------------------------- | ----------------------- | --------- | -------- |
| **MIGRATION_STRATEGY.md** | Database migration plan | 15 min    | ⭐⭐     |

### Product Requirements (05-prd/)

| Document                                                        | Purpose                      | Read Time | Priority |
| --------------------------------------------------------------- | ---------------------------- | --------- | -------- |
| **prd-umbrella.md**                                             | Overall product vision       | 10 min    | ⭐⭐⭐   |
| **Feature PRD – Bryntum Calendar View.md**                      | Calendar UI requirements     | 20 min    | ⭐⭐⭐   |
| **bryntum-reference.md**                                        | Bryntum implementation guide | 30 min    | ⭐⭐⭐   |
| **Feature PRD – Original Schedule-Import-Baseline-Creation.md** | Import/baseline flow         | 15 min    | ⭐⭐     |

### Compliance (06-compliance/)

| Document  | Purpose                           | Read Time | Priority |
| --------- | --------------------------------- | --------- | -------- |
| **DPIA/** | Data Protection Impact Assessment | Varies    | ⭐⭐     |

### Guides (07-guides/)

| Document                 | Purpose                         | Read Time | Priority |
| ------------------------ | ------------------------------- | --------- | -------- |
| **INDEX.md** ⭐          | This file - document navigation | 5 min     | ⭐⭐⭐   |
| **employee-handbook.md** | Employee handbook               | 10 min    | ⭐       |

---

## 🎯 By Task

### Planning a Feature

1. `05-prd/Feature PRD – Bryntum Calendar View.md` - What to build
2. `05-prd/bryntum-reference.md` - Which Bryntum example to use
3. `03-data/data-model-v2.md` - Check schema support
4. `02-api/API_DESIGN_V2.md` - API design patterns

### Implementing a Feature

1. `_confluence/SIMPLE_SYNC.md` - Confluence sync (use MCP)
2. `03-data/data-model-v2.md` - Reference schema fields
3. `02-api/API_DESIGN_V2.md` - GraphQL schema/resolvers
4. `01-architecture/architecture.md` - Service layer patterns

### Database Work

1. `03-data/data-model-v2.md` - Complete schema reference
2. `04-migration/MIGRATION_STRATEGY.md` - Migration approach

### API Development

1. `02-api/API_DESIGN_V2.md` - GraphQL schema and examples
2. `01-architecture/architecture.md` - Server structure
3. `02-api/AUTH_STRATEGY.md` - Authentication patterns

### Client Demo

1. `05-prd/Feature PRD – Bryntum Calendar View.md` - Feature list
2. `05-prd/prd-umbrella.md` - Product vision
3. `05-prd/bryntum-reference.md` - Implementation status

---

## 🔑 Key Decisions

### Tech Stack ✅ DECIDED

| Component     | Technology              | Why                    |
| ------------- | ----------------------- | ---------------------- |
| **Frontend**  | React + Vite            | Fast dev, modern       |
| **Backend**   | Express + Apollo        | Flexible, GraphQL      |
| **API**       | GraphQL (primary)       | Type-safe, efficient   |
| **Database**  | PostgreSQL + Prisma     | Relational, migrations |
| **Real-time** | WebSocket subscriptions | Live updates           |
| **Monorepo**  | Turborepo               | Modular packages       |

**See:** `01-architecture/architecture.md`

### Migration Approach ✅ DECIDED

**Clean Slate Migration**

- Timeline: 3-5 days (no data migration)
- Downtime: Acceptable (pre-launch)
- Risk: Low
- Benefit: No technical debt

**See:** `04-migration/MIGRATION_STRATEGY.md`

### API Design ✅ DECIDED

**GraphQL + REST Hybrid**

- GraphQL: ~71 operations (primary)
- REST: ~15 endpoints (webhooks, files)
- Total: ~60-85 operations
- Timeline: 3-4 weeks

**See:** `02-api/API_DESIGN_V2.md`

---

## 📊 Progress Tracking

### Documentation: ✅ COMPLETE

- [x] Product requirements (PRDs)
- [x] Technical architecture
- [x] Database schema (complete)
- [x] API design (GraphQL)
- [x] Migration strategy
- [x] Development roadmap
- [x] **Folder structure organized** ✅

### Implementation: ⏸️ NOT STARTED

- [ ] Schema refactoring (3-5 days, no data migration)
- [ ] API development (3-4 weeks)
- [ ] Prototype features (see bryntum-reference.md)
- [ ] Testing and QA
- [ ] Deployment

---

## 🚀 Next Steps

### This Week

1. **Review all documentation**
   - Read `01-architecture/REFACTORING_SUMMARY.md`
   - Review `01-architecture/architecture.md`
   - Validate `03-data/data-model-v2.md`
   - Review `02-api/API_DESIGN_V2.md`

2. **Team alignment**
   - Discuss migration approach
   - Confirm timeline acceptable
   - Assign responsibilities

3. **Setup development environment**
   - Create monorepo structure
   - Setup Prisma
   - Setup Express + Apollo
   - Test basic GraphQL query

### Next 2-4 Weeks

1. **Execute schema refactoring** (Days 1-5, no data migration)
2. **Build core API** (Week 1-2)
3. **Build scheduling features** (Week 3)
4. **Build analytics + polish** (Week 4)

---

## 💡 Tips

**When stuck:**

- Check `01-architecture/REFACTORING_SUMMARY.md` for quick answers
- Search documentation: `grep -r "your_question" docs_refactor/`
- Review `_confluence/SIMPLE_SYNC.md` for Confluence sync (use MCP)

**Before adding features:**

- Always check `03-data/data-model-v2.md` for schema support
- Update `05-prd/bryntum-reference.md` status when done

**When building APIs:**

- Follow patterns in `02-api/API_DESIGN_V2.md`
- Use Prisma for database access
- Use GraphQL for client communication

---

## 🔄 Confluence Sync

**See:** `_confluence/SIMPLE_SYNC.md` for complete Confluence sync guide

**Methods:**

- MCP in Cursor (recommended) ⭐
- GitHub Action (automatic on push)

**What syncs:**

- `01-architecture/VISUAL_GUIDE.md` ⭐
- `01-architecture/REFACTORING_SUMMARY.md`
- `01-architecture/architecture.md`
- `04-migration/MIGRATION_STRATEGY.md`
- `05-prd/prd-umbrella.md`

---

## 📞 Support

- **Atlassian Wiki:** [TWC Space](https://caire.atlassian.net/wiki/spaces/TWC/overview)
- **Documentation:** This folder (`docs_refactor/`)
- **Questions:** Update relevant document or create new doc

---

**Documentation Complete! Ready to start implementation.** 🎉
