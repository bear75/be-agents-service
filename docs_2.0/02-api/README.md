# API Documentation

This directory contains API design and specification documents.

## Documents

### Core Specifications

1. **`GRAPHQL_SCHEMA_SPECIFICATION.md`** ⭐ **SINGLE SOURCE OF TRUTH**
   - Defines where GraphQL schema files should be located
   - Specifies that `.graphql` files are the primary source of truth
   - Documents how mappers should reference GraphQL schema files
   - **Status:** ⚠️ Schema files need to be created

2. **`MAPPER_SPECIFICATIONS.md`**
   - Complete mapper function specifications
   - References GraphQL schema files (once created)
   - Documents all data transformations (External → DB → GraphQL → Bryntum → Timefold)

3. **`API_DESIGN.md`**
   - Overall API architecture
   - GraphQL + Express + Prisma design decisions
   - Operation counts and structure

## Current State

### ✅ Completed

- [x] **NEW architecture documentation** (`../01-architecture/architecture.md`)
- [x] **NEW data model documentation** (`../03-data/data-model.md`) - Target schema for new architecture
- [x] Mapper specifications (`MAPPER_SPECIFICATIONS.md`)
- [x] API design documentation (`API_DESIGN.md`)
- [x] GraphQL schema specification document (`GRAPHQL_SCHEMA_SPECIFICATION.md`)

**⚠️ Important:** All specifications are based on the **NEW architecture** in `docs_2.0/`, NOT the old/existing database schema.

### ⚠️ To Be Implemented

- [ ] **GraphQL schema files** (`.graphql`) - **CRITICAL: Single source of truth**
  - Location: `packages/server/src/graphql/schema/` (to be created)
  - Should include mapper annotations in comments
  - Should reference data model documentation

- [ ] Update `MAPPER_SPECIFICATIONS.md` to reference actual GraphQL schema file locations
- [ ] GraphQL code generation setup
- [ ] TypeScript types generated from GraphQL schema

## Architecture Flow (NEW Architecture)

```
NEW Data Model Doc (../03-data/data-model.md) ← Target schema
    ↓
Prisma Schema (packages/prisma/schema.prisma) ← To be created
    ↓
GraphQL Schema Files (*.graphql) ← SINGLE SOURCE OF TRUTH
    ↓
Mapper Specifications (MAPPER_SPECIFICATIONS.md)
    ↓
Implementation (resolvers, mappers)
```

**⚠️ Important:** GraphQL schema is based on the **NEW architecture** (`docs_2.0/`), NOT the old/existing database schema.

## Next Steps

1. **Create GraphQL schema files** following `GRAPHQL_SCHEMA_SPECIFICATION.md`
   - Based on **NEW architecture** (`docs_2.0/`), NOT old schema
   - Reference `docs_2.0/03-data/data-model.md` (target schema)
2. **Add mapper annotations** in GraphQL schema comments
3. **Update mapper specifications** to reference schema file locations
4. **Set up code generation** from GraphQL schema

## Related Documents

- **Architecture:** `../01-architecture/architecture.md`
- **Data Model:** `../03-data/data-model.md`
- **Migration:** `../04-migration/MIGRATION_STRATEGY.md`
