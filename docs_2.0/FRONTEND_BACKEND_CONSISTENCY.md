# Frontend-Backend Consistency Guide

## Problem Statement

There is a disconnect between frontend and backend where different pages use different queries and fetch different fields, leading to inconsistent data display and potential bugs.

## Current State Analysis

### Municipality Queries

#### 1. `GetMunicipality` (single municipality detail)

**File:** `packages/graphql/operations/queries/seo/municipality.graphql`
**Used by:**

- `MunicipalityDashboard.tsx` - Full detail page
- `RegionKvalitet.tsx` - Quality metrics
- `RegionMarknad.tsx` - Market analysis
- `RegionErsattning.tsx` - Compensation data

**Fields fetched:**

- ✅ All basic fields (id, slug, name, region, etc.)
- ✅ `homeCareRecipients` (recently added)
- ✅ All quality indicators (avgCustomerSatisfaction, avgStaffContinuity, etc.)
- ✅ All hemtjänstindex fields
- ✅ `finances` (full array with all fields)
- ✅ `qualitySummaries` (full array)
- ✅ `rankings` (full array)

#### 2. `GetMunicipalities` (all municipalities list)

**File:** `packages/graphql/operations/queries/seo/municipalities.graphql`
**Used by:**

- `MunicipalityIndex.tsx` - Municipality listing
- `DataDashboard.tsx` - Data overview
- `TopListsMunicipalities.tsx` - Top lists

**Fields fetched:**

- ✅ Basic fields
- ✅ `homeCareRecipients`
- ✅ Aggregated quality (avgCustomerSatisfaction, etc.)
- ✅ `finances` (full array)
- ✅ `qualitySummaries` (full array)
- ✅ `rankings` (full array)

**⚠️ INCONSISTENCY:** Missing many detailed quality indicators that `GetMunicipality` has

#### 3. `GetTopMunicipalities` (top municipalities by category)

**File:** `packages/graphql/operations/queries/seo/topMunicipalities.graphql`
**Used by:**

- `TopListsMunicipalities.tsx` - Top lists page

**Fields fetched:**

- ✅ Basic fields
- ✅ `homeCareRecipients`
- ✅ Aggregated quality
- ⚠️ `finances` (only 4 fields: id, year, totalExpenditureSek, homeCareTotalSek, homeCareShareOfEconomyPct, source)
- ⚠️ `qualitySummaries` (only 3 fields: id, year, avgCustomerSatisfaction, avgStaffContinuity)

**⚠️ INCONSISTENCY:** Missing many finance and quality fields

### Provider Queries

#### 1. `GetProvidersForMunicipality` (providers in a municipality)

**File:** `packages/graphql/operations/queries/seo/providersForMunicipality.graphql`
**Used by:**

- `ProviderListing.tsx` - Provider listing page
- `MunicipalityDashboard.tsx` - Provider preview

**Fields fetched:**

- ✅ Basic provider info
- ✅ `rankings` (full)
- ✅ `presence` (with municipality, quality)
- ✅ `financials` (full)

#### 2. `GetProviders` (all providers)

**File:** `packages/graphql/operations/queries/seo/providers.graphql`
**Used by:**

- `TopListsProviders.tsx` - Top provider lists

**⚠️ NEED TO CHECK:** What fields are fetched?

## Identified Inconsistencies

### 1. Finance Fields

- `GetMunicipality`: Fetches ALL finance fields (10 fields)
- `GetMunicipalities`: Fetches ALL finance fields (10 fields)
- `GetTopMunicipalities`: Only fetches 4 finance fields ❌

### 2. Quality Summary Fields

- `GetMunicipality`: Fetches ALL quality fields (7 fields)
- `GetMunicipalities`: Fetches ALL quality fields (7 fields)
- `GetTopMunicipalities`: Only fetches 3 quality fields ❌

### 3. Quality Indicator Fields

- `GetMunicipality`: Fetches ALL 30+ quality indicators
- `GetMunicipalities`: Missing all detailed quality indicators ❌

### 4. Hook Usage

- Some pages use `useGraphQLMunicipalityCompat`
- Some pages use `useGraphQLMunicipality`
- Some pages use `useGraphQLMunicipalities`
- **No clear pattern** for when to use which ❌

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
  homeCareRecipients
}

# packages/graphql/operations/fragments/municipalityFinances.graphql
fragment MunicipalityFinances on Municipality {
  finances {
    id
    year
    totalExpenditureSek
    taxRevenueSek
    taxBase
    homeCareElderlySek
    homeCareDisabilitySek
    personalAssistanceSek
    homeCareTotalSek
    homeCareShareOfEconomyPct
    costTrendNote
    costTrend
    source
    sourceRef
  }
}

# packages/graphql/operations/fragments/municipalityQuality.graphql
fragment MunicipalityQuality on Municipality {
  avgCustomerSatisfaction
  avgStaffContinuity
  avgHemtjanstIndex
  qualitySummaries {
    id
    year
    avgCustomerSatisfaction
    avgStaffContinuity
    avgHemtjanstIndex
    publicAvgSatisfaction
    privateAvgSatisfaction
    source
  }
}
```

### 2. Standardize Queries

All queries should use the same fragments for consistency:

```graphql
query GetMunicipality($slug: String!) {
  municipality(slug: $slug) {
    ...MunicipalityCore
    ...MunicipalityFinances
    ...MunicipalityQuality
    # Additional fields specific to this query
  }
}
```

### 3. Create Validation Script

Script to check:

- All queries use fragments where possible
- Required fields are present in all queries
- No duplicate field definitions
- Hook usage is consistent

### 4. Document Hook Usage

Clear guidelines for which hook to use:

| Hook                           | Use Case                        | Query Used             |
| ------------------------------ | ------------------------------- | ---------------------- |
| `useGraphQLMunicipalityCompat` | Single municipality detail page | `GetMunicipality`      |
| `useGraphQLMunicipality`       | Single municipality (simple)    | `GetMunicipality`      |
| `useGraphQLMunicipalities`     | All municipalities list         | `GetMunicipalities`    |
| `useGraphQLTopMunicipalities`  | Top municipalities by category  | `GetTopMunicipalities` |

## Implementation Plan

### Phase 1: Create Fragments

1. Create fragment files for common field sets
2. Update existing queries to use fragments
3. Regenerate GraphQL types

### Phase 2: Standardize Queries

1. Update `GetTopMunicipalities` to include all finance/quality fields
2. Ensure all queries use same fragments
3. Add missing fields to queries

### Phase 3: Validation

1. Create validation script
2. Add to CI/CD pipeline
3. Document validation rules

### Phase 4: Documentation

1. Update hook documentation
2. Create query usage guide
3. Document field requirements per page type

## Validation Rules

### Rule 1: Fragment Usage

- ✅ All common fields MUST use fragments
- ❌ No duplicate field definitions across queries

### Rule 2: Required Fields

- ✅ All municipality queries MUST include `homeCareRecipients`
- ✅ All municipality queries MUST include `finances` (all fields)
- ✅ All municipality queries MUST include `qualitySummaries` (all fields)

### Rule 3: Hook Consistency

- ✅ Use `useGraphQLMunicipalityCompat` for detail pages
- ✅ Use `useGraphQLMunicipalities` for list pages
- ❌ Don't mix different hooks for same data type

### Rule 4: Field Completeness

- ✅ Detail pages: Fetch ALL fields
- ✅ List pages: Fetch core + aggregated fields
- ✅ Top lists: Fetch same fields as list pages

## Testing Strategy

### 1. Query Validation Test

```typescript
// tests/query-consistency.test.ts
describe("Query Consistency", () => {
  it("should fetch same finance fields in all municipality queries", () => {
    // Check GetMunicipality, GetMunicipalities, GetTopMunicipalities
    // All should have same finance fields
  });

  it("should fetch same quality fields in all municipality queries", () => {
    // Check all queries have same quality fields
  });
});
```

### 2. Hook Validation Test

```typescript
// tests/hook-consistency.test.ts
describe("Hook Consistency", () => {
  it("should use correct hook for each page type", () => {
    // Validate hook usage matches page type
  });
});
```

### 3. Data Completeness Test

```typescript
// tests/data-completeness.test.ts
describe("Data Completeness", () => {
  it("should have all required fields for municipality detail", () => {
    // Check MunicipalityDashboard has all needed fields
  });
});
```

## Next Steps

1. ✅ Create fragment files
2. ✅ Update queries to use fragments
3. ✅ Create validation script
4. ✅ Add to CI/CD
5. ✅ Update documentation
