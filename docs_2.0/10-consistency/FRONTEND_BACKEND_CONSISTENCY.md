# Frontend-Backend Consistency Guide

## Problem Statement

There is a disconnect between frontend and backend where different pages use different queries and fetch different fields from the database, leading to inconsistent data display.

## Goals

1. **Single Source of Truth**: Each data type should have one canonical query
2. **Query Fragments**: Reusable fragments for common field sets
3. **Validation**: Automated checks to ensure queries match schema
4. **Documentation**: Clear mapping of which queries are used where

## Current State Analysis

### Municipality Queries

| Query                  | Used In                               | Fields Fetched                             | Issues                 |
| ---------------------- | ------------------------------------- | ------------------------------------------ | ---------------------- |
| `GetMunicipality`      | MunicipalityDashboard, ProviderDetail | Full details + finances + qualitySummaries | ✅ Complete            |
| `GetMunicipalities`    | MunicipalityIndex, DataDashboard      | Basic + finances + qualitySummaries        | ⚠️ Missing some fields |
| `GetTopMunicipalities` | TopListsMunicipalities                | Limited fields                             | ⚠️ Incomplete finances |

### Provider Queries

| Query                         | Used In         | Fields Fetched                        | Issues               |
| ----------------------------- | --------------- | ------------------------------------- | -------------------- |
| `GetProvidersForMunicipality` | ProviderListing | Full provider + presence + financials | ✅ Complete          |
| `GetProvider`                 | ProviderDetail  | Basic provider info                   | ⚠️ May be incomplete |
| `GetProviderDetail`           | ProviderDetail  | Full details                          | ✅ Complete          |

## Best Practices

### 1. Use Query Fragments

Create reusable fragments for common field sets:

```graphql
# packages/graphql/operations/fragments/municipalityCore.graphql
fragment MunicipalityCore on Municipality {
  id
  slug
  name
  region
  municipalityCode
  population
  elderlyPopulation
  elderlyPercentage
  hasLov
  lovSince
}

fragment MunicipalityFinances on Municipality {
  finances {
    id
    year
    totalExpenditureSek
    taxRevenueSek
    homeCareTotalSek
    homeCareShareOfEconomyPct
    costTrend
    source
  }
}

fragment MunicipalityQuality on Municipality {
  qualitySummaries {
    id
    year
    avgCustomerSatisfaction
    avgStaffContinuity
    avgHemtjanstIndex
    source
  }
}
```

### 2. Standardized Queries

Each page type should use a standardized query:

- **Municipality Detail Page**: `GetMunicipality` (full details)
- **Municipality List Page**: `GetMunicipalities` (with core + finances)
- **Provider Detail Page**: `GetProviderDetail` (full details)
- **Provider List Page**: `GetProvidersForMunicipality` (with presence)

### 3. Validation Rules

1. **Required Fields**: Each query must include all fields used by the page
2. **Fragment Usage**: Use fragments instead of duplicating fields
3. **Type Safety**: Generated TypeScript types must match query fields
4. **Backend Alignment**: Query fields must match resolver return types

## Implementation Plan

### Phase 1: Create Fragments

1. Create fragment files for:
   - `MunicipalityCore`
   - `MunicipalityFinances`
   - `MunicipalityQuality`
   - `ProviderCore`
   - `ProviderFinancials`
   - `ProviderPresence`

### Phase 2: Refactor Queries

1. Update all queries to use fragments
2. Ensure all queries for same entity type fetch same core fields
3. Add missing fields to incomplete queries

### Phase 3: Validation Script

1. Create script to validate:
   - All queries use fragments
   - Required fields are present
   - No duplicate field definitions
   - Queries match schema

### Phase 4: Documentation

1. Document which query is used on which page
2. Document field requirements per page type
3. Create query decision tree

## Query Mapping

### Municipality Pages

| Page                   | Route                  | Query                  | Required Fragments                   |
| ---------------------- | ---------------------- | ---------------------- | ------------------------------------ |
| MunicipalityDashboard  | `/kommuner/:slug`      | `GetMunicipality`      | Core + Finances + Quality + Rankings |
| MunicipalityIndex      | `/kommuner`            | `GetMunicipalities`    | Core + Finances + Quality            |
| TopListsMunicipalities | `/topplistor/kommuner` | `GetTopMunicipalities` | Core + Finances + Rankings           |

### Provider Pages

| Page            | Route                                | Query                         | Required Fragments                      |
| --------------- | ------------------------------------ | ----------------------------- | --------------------------------------- |
| ProviderListing | `/kommuner/:slug/utforare`           | `GetProvidersForMunicipality` | Core + Presence + Financials            |
| ProviderDetail  | `/kommuner/:slug/utforare/:provider` | `GetProviderDetail`           | Core + Presence + Financials + Rankings |

## Validation Checklist

Before merging any query changes:

- [ ] Query uses fragments (no duplicate field definitions)
- [ ] All required fields for page are included
- [ ] Query matches schema (no invalid fields)
- [ ] TypeScript types generated successfully
- [ ] Page renders without missing data errors
- [ ] Data displayed matches database values

## Tools

### Query Validator Script

```bash
yarn workspace @appcaire/graphql validate-queries
```

This script will:

1. Check all queries use fragments
2. Validate fields against schema
3. Check for missing required fields
4. Generate report of inconsistencies

### Query Usage Mapper

```bash
yarn workspace @appcaire/graphql map-query-usage
```

This script will:

1. Scan frontend code for query usage
2. Map queries to pages
3. Identify unused queries
4. Identify pages using wrong queries

## Migration Guide

### Step 1: Identify Current Usage

Run query usage mapper to see current state.

### Step 2: Create Fragments

Create fragment files for common field sets.

### Step 3: Update Queries

Refactor queries to use fragments.

### Step 4: Update Pages

Ensure pages use correct queries.

### Step 5: Validate

Run validation script and fix issues.

### Step 6: Test

Test all pages to ensure data displays correctly.

## Examples

### Before (Inconsistent)

```graphql
# Query 1
query GetMunicipalities {
  municipalities {
    id
    name
    finances {
      year
      homeCareTotalSek
    }
  }
}

# Query 2
query GetTopMunicipalities {
  topMunicipalities {
    id
    name
    finances {
      year
      homeCareTotalSek
      source
    }
  }
}
```

### After (Consistent with Fragments)

```graphql
# Fragment
fragment MunicipalityFinances on Municipality {
  finances {
    id
    year
    homeCareTotalSek
    source
  }
}

# Query 1
query GetMunicipalities {
  municipalities {
    ...MunicipalityCore
    ...MunicipalityFinances
  }
}

# Query 2
query GetTopMunicipalities {
  topMunicipalities {
    ...MunicipalityCore
    ...MunicipalityFinances
  }
}
```

## Next Steps

1. ✅ Create this documentation
2. ⏳ Create fragment files
3. ⏳ Refactor queries to use fragments
4. ⏳ Create validation script
5. ⏳ Run validation and fix issues
6. ⏳ Update all pages to use standardized queries
