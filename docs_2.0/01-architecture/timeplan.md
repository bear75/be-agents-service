# CAIRE Platform Refactoring – Timeplan & Implementation Guide

**Project:** CAIRE Platform Refactoring  
**Status:** Pre-Launch Planning  
**Last Updated:** 2025-12-08

---

## Quick Answers

### Schema Refactoring

**Q: What's the best approach for schema refactoring?**  
**A: Clean Slate Schema Creation** ✅

- Timeline: 3-5 days
- Downtime: Acceptable (pre-launch)
- Developer Time: 24-40 hours (1 developer)
- Risk: Low
- No data migration needed (clean slate)
- See: `MIGRATION_STRATEGY.md`

### Timeline with 2 Developers

**Q: How long with 2 full-stack developers?**  
**A: 4-5 weeks calendar time (includes frontend)** ⚡ **Reduced!**

- **Total Developer Hours:** 224-320 hours
- **Calendar Time:** 4-5 weeks (vs 5-7 weeks with 1 developer - saves 1-2 weeks)
- **Scope:** Schema refactoring + API development + Frontend development + Integration
- **Key Advantage:** Bryntum prototype is already complete! Frontend is mostly integration work.
- **Parallel Work:** Backend and frontend can be developed in parallel after schema is done

### API Refactoring

**Q: How many endpoints do we need?**  
**A: ~60-85 operations/endpoints** (vs 319 current)

**Tech Stack:**

- ✅ **Express** (standalone server, not Next.js)
- ✅ **GraphQL** (Apollo Server - primary API)
- ✅ **Prisma** (ORM, not Drizzle)
- ✅ **WebSocket** (subscriptions for real-time)
- ✅ **REST** (secondary - webhooks, files)

**Operations:**

- GraphQL: ~71 operations (queries + mutations + subscriptions)
- REST: ~15 endpoints (webhooks, files, health)

**Timeline:** 3-4 weeks  
**See:** `API_DESIGN_V2.md`

---

## Migration Strategy Summary

### Current Problems

- 319 route files (too many, redundant)
- 8 deprecated endpoints still in code
- Inconsistent schema (unused tables, missing indexes)
- Performance issues

### Recommended Approach: Clean Slate

**Days 1-2: Preparation**

- Review current schema (informational only)
- Create schema creation scripts
- Test on staging

**Days 2-4: Schema Creation**

- Generate new schema from `data-model-v2.md`
- Seed reference data (scenarios, configs)
- Validate schema structure

**Day 5: Deployment**

- Deploy to production
- Verify relationships and indexes
- Test schema

### Why Clean Slate?

✅ Much faster than incremental (3-5 days vs 4+ weeks)  
✅ No technical debt  
✅ Clean foundation for launch  
✅ Downtime acceptable (pre-launch)  
✅ Lower risk and complexity

---

## API Design Summary

### Current State

- ❌ 319 route files
- ❌ 32+ fragmented categories
- ❌ No consistency
- ❌ Many unused/broken endpoints

### New Design

- ✅ **GraphQL as primary API** (type-safe, efficient)
- ✅ **~71 GraphQL operations** (queries, mutations, subscriptions)
- ✅ **~15 REST endpoints** (webhooks, files)
- ✅ **Express + Apollo + Prisma** (proper stack)
- ✅ **WebSocket subscriptions** (real-time)
- ✅ **Monorepo** (client/server/prisma)

### Endpoint Breakdown

| Phase                                            | Operations | Tech           | Priority      |
| ------------------------------------------------ | ---------- | -------------- | ------------- |
| Infrastructure + Core (Orgs, Employees, Clients) | ~25        | GraphQL        | Week 1-2 ✅   |
| Scheduling (Schedules, Visits, Templates)        | ~30        | GraphQL        | Week 2-3 ✅   |
| Optimization & Solutions                         | ~16        | GraphQL + WS   | Week 3 ✅     |
| Analytics & REST                                 | ~15        | GraphQL + REST | Week 4 ✅     |
| **Total**                                        | **~60-85** | **Mixed**      | **3-4 weeks** |

---

## Implementation Timeline

### Single Developer

**Total: 224-320 hours (5-7 weeks)** ⚡ **Reduced from 8-11 weeks!**

#### 1. Schema Refactoring: 24-40 hours (3-5 days)

- Days 1-2: Prepare schema creation scripts
- Days 2-4: Generate schema, test, seed reference data
- Day 5: Deploy and validate

#### 2. API Development: 120-160 hours (3-4 weeks)

- Week 1-2: Core GraphQL API (CRUD operations)
- Week 3: Scheduling features + Optimization
- Week 4: Analytics + REST endpoints + Real-time

#### 3. Frontend Development: 40-80 hours (1-2 weeks) ⚡ **Dramatically reduced!**

- Days 1-2: Setup React + Vite + Apollo Client, copy Bryntum prototype (already built!)
- Days 3-5: Connect prototype to GraphQL API, implement mappers (DB ↔ Bryntum)
- Days 6-8: Build simple CRUD pages (resources, analytics, admin - no complex logic)
- Days 9-10: Real-time subscriptions, polish, testing

> **Key:** Bryntum prototype is already complete! We're just plugging it in and connecting to real data.

#### 4. Integration & Testing: 40 hours (1 week)

- Integration testing (frontend ↔ backend), E2E tests
- Bug fixes, performance optimization, documentation

### Two Developers (Parallel Work) - Full Stack

**Total: 4-5 weeks calendar time** ⚡ **Reduced from 5-7 weeks with 1 developer (saves 1-2 weeks)!**

#### Developer 1 (Backend-focused):

- Schema Refactoring: 24-40 hours (3-5 days)
- API Development: 120-160 hours (3-4 weeks)
- Integration Testing: 20 hours (0.5 week)

#### Developer 2 (Frontend-focused):

- Frontend Setup & Prototype Integration: 8-12 hours (1-1.5 days)
- GraphQL Integration (mappers): 16-20 hours (2-2.5 days)
- Simple CRUD Pages: 20-24 hours (2.5-3 days)
- Real-time & Polish: 12-16 hours (1.5-2 days)
- Integration Testing: 20 hours (0.5 week)

#### Parallel Execution:

- **Days 1-5:** Dev 1 does schema refactoring, Dev 2 sets up frontend + copies Bryntum prototype
- **Weeks 2-3:** Dev 1 builds core API (weeks 1-2 of API work), Dev 2 prepares frontend mappers and structure
- **Week 3-4:** Dev 1 completes API (scheduling, analytics), Dev 2 connects prototype to GraphQL + builds CRUD pages (parallel)
- **Week 4-5:** Both developers work on integration testing and polish

**Total Developer Hours: 224-320 hours (same as single developer)**  
**Total Calendar Time: 4-5 weeks (vs 5-7 weeks with 1 developer - saves 1-2 weeks)**

> **Key Advantage:** Bryntum prototype is already complete! Frontend work is mostly integration, not building from scratch.

> **Key:** Bryntum prototype is **already complete**! Frontend work is mostly:
>
> - Plugging in existing prototype (copy components)
> - Replacing mock data with GraphQL (mapper functions)
> - Building simple CRUD pages (resources, analytics, admin - no complex logic)

---

## Implementation Phases

### Phase 1: Infrastructure (Week 1)

```
┌────────────────────────────────────────┐
│         Setup Monorepo                 │
├────────────────────────────────────────┤
│ ✅ Create packages/client/             │
│ ✅ Create packages/server/             │
│ ✅ Create packages/prisma/             │
│ ✅ Setup Turborepo                     │
│ ✅ Setup Express + Apollo              │
│ ✅ Generate Prisma schema              │
│ ✅ Create initial migration            │
│ ✅ Setup authentication                │
└────────────────────────────────────────┘
       Deliverable: Infrastructure ready
```

### Phase 2: Core API (Week 2)

```
┌────────────────────────────────────────┐
│         Implement Core Resources       │
├────────────────────────────────────────┤
│ ✅ Organizations (5 operations)        │
│ ✅ Employees (7 operations)            │
│ ✅ Clients (7 operations)              │
│ ✅ Schedules (10 operations)           │
│ ✅ Visits (6 operations)               │
│ ✅ Setup Apollo Client                 │
│ ✅ Test end-to-end                     │
└────────────────────────────────────────┘
       Deliverable: CRUD working
```

### Phase 3: Scheduling (Week 3)

```
┌────────────────────────────────────────┐
│      Implement Scheduling Features     │
├────────────────────────────────────────┤
│ ✅ Optimization (8 operations)         │
│ ✅ Solutions (4 operations)            │
│ ✅ Visit Templates (7 operations)      │
│ ✅ Templates/Slinga (5 operations)     │
│ ✅ Schedule Groups (5 operations)      │
│ ✅ WebSocket subscriptions (3)         │
│ ✅ Test real-time updates              │
└────────────────────────────────────────┘
       Deliverable: Optimization working
```

### Phase 4: Analytics + Polish (Week 4)

```
┌────────────────────────────────────────┐
│      Implement Analytics & Polish      │
├────────────────────────────────────────┤
│ ✅ Metrics (6 operations)              │
│ ✅ Analytics (4 operations)            │
│ ✅ REST endpoints (15)                 │
│ ✅ Complete testing                    │
│ ✅ API documentation                   │
│ ✅ Performance optimization            │
└────────────────────────────────────────┘
       Deliverable: Production-ready API
```

---

## Migration Timeline Visual

```
Week 1              Week 2              Week 3              Week 4
│                   │                   │                   │
├─ Setup Monorepo   ├─ Core GraphQL     ├─ Scheduling      ├─ Analytics
├─ Express+Apollo   ├─ Organizations    ├─ Optimization    ├─ REST endpoints
├─ Prisma Schema    ├─ Employees        ├─ Templates       ├─ Testing
├─ DB Migration     ├─ Clients          ├─ Solutions       ├─ Documentation
│                   ├─ Schedules        ├─ WebSockets      ├─ Deployment
│                   │  Visits            │                   │
│                   │                   │                   │
└─────────────────┴─────────────────┴─────────────────┴──────────────►
     Setup              Core API          Features           Polish
    (20h)              (60h)              (48h)             (32h)
```

**Total: 160 hours = 3-4 weeks**

---

## Decision Matrix

### When to Use Clean Slate Migration?

✅ Pre-launch (downtime OK)  
✅ Significant schema changes  
✅ Want to eliminate technical debt  
✅ Have time for testing

### When to Use Incremental Migration?

⚠️ Active production users  
⚠️ Zero-downtime required  
⚠️ Complex data dependencies  
⚠️ Limited testing time

**Your Case: Clean Slate** ✅

---

## Risk Assessment

| Risk             | Likelihood | Impact | Mitigation                 |
| ---------------- | ---------- | ------ | -------------------------- |
| Data loss        | N/A        | N/A    | No production data to lose |
| Schema errors    | Medium     | Medium | Test on staging first      |
| API bugs         | Medium     | Medium | Comprehensive testing      |
| Timeline overrun | Low        | Low    | Buffer time built in       |

**Overall Risk: LOW** ✅

---

## Time & Effort Estimate

### Schema Refactoring

- Developer time: 24-40 hours (3-5 days)
- Infrastructure: Same database (no additional setup)
- No data migration needed (clean slate)

### API Refactoring

- Developer time: 120-160 hours (3-4 weeks)
- Testing: 40 hours (1 week)
- **Total: 160-200 hours (4-5 weeks)**

### Frontend Refactoring

- Developer time: 40-80 hours (1-2 weeks) ⚡ **Dramatically reduced!**
- Integration with new API: Included above
- **Key:** Bryntum prototype is already complete! We're just:
  - Plugging it into the new app structure
  - Replacing mock data with GraphQL queries (mapper functions)
  - Building simple CRUD pages (resources, analytics, admin - no complex logic)

### Grand Total: 224-320 hours (5-7 weeks with 1 developer, 4-5 weeks with 2 developers - saves 1-2 weeks)

_Note: Frontend timeline reduced because Bryntum prototype is already built and working. Other pages are simple CRUD with normalized data model._

---

## Success Metrics

### Database Migration:

- [ ] All data migrated without loss
- [ ] All relationships validated
- [ ] Performance improved (faster queries)
- [ ] No orphaned records

### API Refactoring:

- [ ] 60-80 endpoints implemented
- [ ] All tests passing (>90% coverage)
- [ ] Response times < targets
- [ ] Complete API documentation

### Prototype:

- [ ] All features working with new API
- [ ] Data loading correctly
- [ ] No console errors
- [ ] Performance acceptable

---

## Next Steps

1. **Review Documents**
   - Read `MIGRATION_STRATEGY.md` in detail
   - Review `API_DESIGN_V2.md` specifications (GraphQL + Express + Prisma)
   - Validate `data-model-v2.md` meets requirements
   - Review `architecture.md` for target stack

2. **Schedule Migration**
   - Schedule refactoring window (can be done during weekdays)
   - Notify team
   - Prepare rollback plan

3. **Start API Development**
   - Begin with Phase 1 (Core CRUD)
   - Can start before DB migration
   - Test with local DB

4. **Execute Migration**
   - Follow `MIGRATION_STRATEGY.md` checklist
   - Verify at each step
   - Test thoroughly

5. **Deploy and Test**
   - Deploy new APIs
   - Test prototype
   - Gather feedback

---

## Quick Commands

```bash
# Database backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Generate new schema migration
pnpm db:generate

# Apply migration
pnpm db:migrate

# Run API tests
pnpm test:api

# Start dev server with new API
pnpm dev
```

---

## File Reference

| Document                | Purpose                            | When to Use              |
| ----------------------- | ---------------------------------- | ------------------------ |
| `architecture.md`       | Architecture, tech stack & visuals | Start here ⭐            |
| `data-model-v2.md`      | Complete schema reference          | Schema implementation ⭐ |
| `API_DESIGN_V2.md`      | Complete GraphQL + REST API spec   | API development ⭐       |
| `MIGRATION_STRATEGY.md` | Database migration plan            | Before schema changes    |
| `AUTH_STRATEGY.md`      | Auth implementation & independence | Auth questions           |
| `timeplan.md`           | This file - timeline & planning    | Quick lookup             |

---

## Questions?

- Schema questions → Check `data-model-v2.md`
- Migration questions → Check `MIGRATION_STRATEGY.md`
- API questions → Check `API_DESIGN_V2.md` (GraphQL + REST)
- Auth questions → Check `AUTH_STRATEGY.md` (Clerk sync & independence)
- Architecture questions → Check `architecture.md`
- Timeline questions → Check this file (`timeplan.md`)

---

**Recommendation: Proceed with Clean Slate Migration + New API Design**

✅ Best long-term decision  
✅ Fastest implementation  
✅ Lowest risk  
✅ Clean foundation for launch
