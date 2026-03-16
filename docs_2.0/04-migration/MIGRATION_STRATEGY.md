# Database Schema Refactoring Strategy

**Project:** CAIRE Platform Refactoring  
**Status:** Pre-Launch (Downtime Acceptable)  
**Target:** Zero-downtime not required  
**Related:** `REFACTORING_PLAN.md`, `data-model-v2.md`

> **Note:** This is a schema creation/refactoring strategy, not a data migration. Since there's no production data, we're creating a new schema from scratch.

---

## Executive Summary

**Recommendation: Clean Slate Schema Creation** ✅

Since you're not launched yet and downtime is acceptable, we recommend a **clean slate schema creation** approach:

1. ✅ **Create new schema from scratch** (based on `data-model-v2.md`)
2. ✅ **Deprecate old endpoints** (remove 200+ mess)
3. ✅ **Build new API** (60-80 well-designed endpoints)

> **Note:** No data migration needed - we're starting with a clean slate since there's no production data.

**Timeline:** 3-5 days  
**Risk:** Low (pre-launch, no production data)  
**Benefit:** Clean architecture, no technical debt

---

## Current State Analysis

### Database Issues

- ❌ 319 API route files (many unused)
- ❌ 8 deprecated endpoints still in codebase
- ❌ 32+ top-level API categories (too fragmented)
- ❌ Inconsistent naming conventions
- ❌ Unused tables and fields
- ❌ Performance issues (missing indexes)

### What to Keep

- ✅ Authentication setup (Clerk integration)
- ✅ Configuration and environment settings

> **Note:** No data to preserve - starting fresh with new schema.

### What to Discard

- ❌ Redundant endpoints
- ❌ Unused tables
- ❌ Deprecated code
- ❌ Test/debug routes
- ❌ Duplicate functionality

---

## Schema Refactoring Strategy: Clean Slate Approach

### Phase 1: Preparation (0.5-1 day)

**1.1 Review Current Schema**

> **Note:** Since we're not live and have no production data, we're starting with a clean slate. This phase focuses on understanding the current schema structure for reference only.

```sql
-- Review current schema structure (for reference)
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Document current schema for comparison
\dt  -- List all tables
\d+ table_name  -- Describe table structure
```

> **Note:** This is informational only - we're not preserving any data, just understanding the current structure before creating the new schema.

**1.2 Prepare Schema Migration Scripts**

```typescript
// scripts/migration/prepare-schema.ts
// No data export needed - clean slate migration

// Focus on schema validation and reference data seeding
async function prepareNewSchema() {
  // Validate new schema structure
  // Prepare seed scripts for reference data only
  // No data migration scripts needed
}
```

> **Note:** Since there's no data to migrate, Phase 1 focuses on schema preparation and validation only.

### Phase 2: New Schema Creation (1-2 days)

**2.1 Generate New Schema from data-model-v2.md**

```bash
# Option A: Write Drizzle schema from scratch
# Based on data-model-v2.md specifications

# Option B: Use Prisma migration
# Generate from Prisma schema
```

**2.2 Create Initial Migration**

```bash
# Create new migration
pnpm db:generate

# Review generated SQL
cat drizzle/migrations/0001_new_schema.sql

# Test on local database
pnpm db:migrate
```

**2.3 Seed Reference Data**

```typescript
// scripts/seed/reference-data.ts

async function seedReferenceData() {
  // 1. Global scenarios (5 presets from PRD)
  await db.insert(scenarios).values([
    {
      name: 'Daglig Planering',
      description: 'Regular stable days',
      organizationId: null, // Global
      configData: {
        weights: { continuity: 90, travel: 50, workload: 50 },
        constraints: { respectPinned: true, overtime: false }
      }
    },
    // ... other 4 presets
  ]);

  // 2. Default solver configs
  await db.insert(solver_configs).values([...]);

  // 3. Sample service areas (for testing)
  // 4. Skills reference data
}
```

### Phase 3: Schema Validation & Testing (0.5 day)

**3.1 Validate New Schema**

```typescript
// scripts/migration/validate-schema.ts

async function validateNewSchema() {
  // 1. Verify all tables created
  const tables = await db.query.informationSchema.tables.findMany({
    where: eq(informationSchema.tables.tableSchema, "public"),
  });

  // 2. Verify all indexes created
  const indexes = await db.query.informationSchema.statistics.findMany({
    where: eq(informationSchema.statistics.tableSchema, "public"),
  });

  // 3. Verify foreign key constraints
  const constraints =
    await db.query.informationSchema.tableConstraints.findMany({
      where: and(
        eq(informationSchema.tableConstraints.tableSchema, "public"),
        eq(informationSchema.tableConstraints.constraintType, "FOREIGN KEY"),
      ),
    });

  // 4. Run schema validation tests
  await runSchemaTests();
}
```

**3.2 Test Reference Data Seeding**

```typescript
// Verify that reference data seeding works correctly
// Test global scenarios, solver configs, etc.
// No data migration testing needed - clean slate
```

> **Note:** Phase 3 is now focused on schema validation and testing since there's no data to migrate.

### Phase 4: Deployment (0.5-1 day)

**4.1 Deploy to Staging**

```bash
# 1. Deploy new schema to staging database
DATABASE_URL=$STAGING_URL pnpm db:migrate

# 2. Seed reference data only
DATABASE_URL=$STAGING_URL tsx scripts/seed/reference-data.ts

# 3. Verify schema and reference data
DATABASE_URL=$STAGING_URL psql -c "\dt"  # List tables
DATABASE_URL=$STAGING_URL psql -c "SELECT * FROM scenarios LIMIT 5"  # Verify reference data
```

**4.2 Deploy to Production**

```bash
# 1. Schedule maintenance window (if needed)
# 2. Drop old schema (or create new database)
# 3. Apply new schema
# 4. Seed reference data
# 5. Verify schema and test
# 6. Deploy new API endpoints
```

**4.3 Rollback Plan**

> **Note:** Since there's no production data and we're starting with a clean slate, rollback is not needed. If issues occur during deployment, simply fix and redeploy. No data will be lost since there's no data to lose.

---

## Alternative: Incremental Migration (Not Applicable)

> **Note:** This approach is not applicable since there's no production data. Included for reference only if the situation changes in the future.

**Only if you have active pilot users and can't afford downtime:**

### Phase 1: Parallel Schema (1 week)

- Keep old schema
- Create new tables with `_v2` suffix
- Dual-write to both schemas

### Phase 2: Gradual Migration (2 weeks)

- Migrate feature by feature
- Update endpoints one by one
- Test thoroughly

### Phase 3: Cutover (1 day)

- Switch reads to new schema
- Deprecate old tables
- Remove dual-write logic

**Timeline:** 4 weeks  
**Risk:** Medium (complexity)  
**Benefit:** Zero downtime

---

## Recommended: Clean Slate Timeline

| Day          | Phase                   | Tasks                                                                                       | Status |
| ------------ | ----------------------- | ------------------------------------------------------------------------------------------- | ------ |
| **Day 1**    | Preparation             | Prepare schema creation scripts                                                             | ⏸️     |
| **Days 2-3** | New Schema              | Generate schema, test locally, seed reference data                                          | ⏸️     |
| **Days 4-5** | Validation & Deployment | Validate schema, test reference data seeding, deploy to staging, test, deploy to production | ⏸️     |

**Total: 3-5 days**

---

## Schema Refactoring Checklist

### Pre-Refactoring

- [ ] Schema creation scripts prepared
- [ ] Reference data seed scripts ready
- [ ] Schema validation scripts tested locally
- [ ] Team notified of refactoring window

### Refactoring

- [ ] New schema deployed
- [ ] Reference data seeded
- [ ] Schema structure validated
- [ ] Indexes created and verified
- [ ] Foreign keys validated
- [ ] Schema tests passing

### Post-Refactoring

- [ ] All tests passing
- [ ] Prototype working with new schema
- [ ] Performance benchmarks met
- [ ] Schema refactoring documented

---

## Schema Integrity Verification

```sql
-- After schema creation, verify schema structure:

-- 1. All tables created
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- 2. All indexes created
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- 3. All foreign key constraints exist
SELECT
  tc.table_name,
  kcu.column_name,
  ccu.table_name AS foreign_table_name,
  ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public';

-- 4. Reference data seeded correctly
SELECT COUNT(*) as scenario_count FROM scenarios;
SELECT COUNT(*) as solver_config_count FROM solver_configs;

-- 5. Data types correct
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

---

## Risk Assessment

| Risk                    | Likelihood | Impact   | Mitigation                            |
| ----------------------- | ---------- | -------- | ------------------------------------- |
| Data loss               | N/A        | N/A      | No data exists to lose                |
| Schema errors           | Medium     | Medium   | Test on staging first                 |
| Downtime exceeds window | Low        | Low      | Pre-launch, acceptable                |
| Rollback needed         | Very Low   | Very Low | No rollback needed - fix and redeploy |
| Performance issues      | Low        | Medium   | Index creation verified               |

---

## Time & Effort Analysis

### Clean Slate Approach

- **Developer Time:** 24-40 hours (3-5 days)
- **Infrastructure:** Same infrastructure (no additional setup)
- **Downtime:** None required (pre-launch)
- **Backup:** Not needed (no production data)
- **Risk Level:** Low

### Incremental Approach (For Comparison - Not Applicable)

- **Developer Time:** 160+ hours (4+ weeks)
- **Infrastructure:** Higher complexity (dual schemas)
- **Downtime:** None required
- **Risk Level:** Medium (complexity)

**Recommendation:** Clean Slate (much faster, lower risk, no data complexity)

---

## Post-Refactoring Benefits

✅ **Clean Architecture**

- No technical debt
- Consistent naming
- Proper relationships

✅ **Better Performance**

- Optimized indexes
- Normalized structure
- Efficient queries

✅ **Easier Development**

- Clear schema
- Type-safe
- Well-documented

✅ **Scalability**

- Designed for growth
- Flexible structure
- Maintainable

---

## Next Steps

1. **Review this plan** with team
2. **Schedule refactoring window** (can be done during weekdays)
3. **Test schema creation scripts** on local/staging
4. **Execute Phase 1** (Preparation)
5. **Execute Phase 2** (New Schema Creation)
6. **Execute Phase 3** (Schema Validation)
7. **Execute Phase 4** (Deployment)
8. **Verify and celebrate** 🎉

---

## Related Documents

- **Schema Reference:** `data-model-v2.md`
- **Refactoring Plan:** `REFACTORING_PLAN.md`
- **API Design:** `API_DESIGN.md` (see next document)
- **Prototype Roadmap:** `PROTOTYPE_ROADMAP.md`

---

**Recommendation Summary:**

🎯 **Go with Clean Slate Schema Creation**

- ✅ 3-5 days (vs 4+ weeks for incremental migration)
- ✅ Lower risk and complexity
- ✅ No technical debt
- ✅ No data migration complexity
- ✅ Downtime acceptable (pre-launch)
- ✅ Clean foundation for launch

**Start Date:** When ready  
**Estimated Completion:** 3-5 days  
**Team Review:** Recommended before starting
