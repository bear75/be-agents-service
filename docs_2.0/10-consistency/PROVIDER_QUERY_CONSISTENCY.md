# Provider Query Consistency Guide

## Problem Solved ✅

Fixed inconsistencies in provider queries where:

- Different queries fetched different municipality fields
- Provider core fields were duplicated
- Financial fields varied between queries
- Quality fields were inconsistent

## Solution Implemented

### 1. Created Provider Fragments ✅

**Location:** `packages/graphql/operations/fragments/`

- `providerCore.graphql` - Core provider fields (for `Provider` type)
- `providerWithPresenceCore.graphql` - Core fields for `ProviderWithPresence` type
- `providerCoreMinimal.graphql` - Minimal fields for basic listings
- `providerFinancialsBasic.graphql` - Basic financial fields (7 fields)
- `providerFinancialsDetailed.graphql` - Detailed financial fields (18 fields)
- `providerCertification.graphql` - Certification data
- `providerPresenceBasic.graphql` - Basic presence data
- `qualityMetricBasic.graphql` - Basic quality fields (5 fields)
- `qualityMetricDetailed.graphql` - Detailed quality fields (11 fields)
- `municipalityBasic.graphql` - **NEW** - Consistent municipality fields when included in provider queries

### 2. Updated Provider Queries ✅

All provider queries now use fragments:

- ✅ `GetProviders` - Uses `ProviderCore`, `ProviderFinancialsBasic`, `ProviderCertification`
- ✅ `GetProvider` - Uses `ProviderCore`
- ✅ `GetProvidersForMunicipality` - Uses `ProviderWithPresenceCore`, `ProviderFinancialsBasic`, `ProviderPresenceBasic`, `QualityMetricBasic`, `MunicipalityBasic`
- ✅ `GetProviderWithDetails` - Uses `ProviderCore`, `ProviderFinancialsDetailed`, `ProviderCertification`, `QualityMetricDetailed`, `MunicipalityBasic`
- ✅ `GetProviderMunicipalities` - Uses `ProviderCoreMinimal`, `ProviderPresenceBasic`, `QualityMetricDetailed`, `MunicipalityBasic`

### 3. Municipality Data Consistency ✅

**Before:**

- `GetProvidersForMunicipality`: municipality { id, slug, name } - 3 fields
- `GetProviderMunicipalities`: municipality { id, slug, name, municipalityCode } - 4 fields
- `GetProviderWithDetails`: municipality { id, slug, name, region } - 4 fields (different fields!)

**After:**

- All queries use `MunicipalityBasic` fragment: { id, slug, name, region, municipalityCode } - 5 fields consistently

## Key Improvements

### Before ❌

- Municipality fields inconsistent (3-4 fields, different fields)
- Provider core fields duplicated
- Financial fields varied (6-18 fields)
- Quality fields varied (4-11 fields)
- No fragments for providers

### After ✅

- Municipality fields consistent via `MunicipalityBasic` fragment
- Provider core fields in fragments
- Financial fields: Basic (7) or Detailed (18) via fragments
- Quality fields: Basic (5) or Detailed (11) via fragments
- All queries use fragments

## Fragment Usage Guide

### Provider Queries

| Query                         | Returns Type           | Core Fragment              | Financial Fragment           | Municipality Fragment |
| ----------------------------- | ---------------------- | -------------------------- | ---------------------------- | --------------------- |
| `GetProviders`                | `Provider`             | `ProviderCore`             | `ProviderFinancialsBasic`    | None                  |
| `GetProvider`                 | `Provider`             | `ProviderCore`             | None                         | None                  |
| `GetProvidersForMunicipality` | `ProviderWithPresence` | `ProviderWithPresenceCore` | `ProviderFinancialsBasic`    | `MunicipalityBasic`   |
| `GetProviderWithDetails`      | `ProviderWithDetails`  | `ProviderCore`             | `ProviderFinancialsDetailed` | `MunicipalityBasic`   |
| `GetProviderMunicipalities`   | `ProviderMunicipality` | `ProviderCoreMinimal`      | None                         | `MunicipalityBasic`   |

### Municipality in Provider Queries

**Always use `MunicipalityBasic` fragment:**

```graphql
municipality {
  ...MunicipalityBasic
}
```

This ensures consistent fields: `id`, `slug`, `name`, `region`, `municipalityCode`

## Files Created/Modified

### Created

- `packages/graphql/operations/fragments/providerCore.graphql`
- `packages/graphql/operations/fragments/providerWithPresenceCore.graphql`
- `packages/graphql/operations/fragments/providerCoreMinimal.graphql`
- `packages/graphql/operations/fragments/providerFinancialsBasic.graphql`
- `packages/graphql/operations/fragments/providerFinancialsDetailed.graphql`
- `packages/graphql/operations/fragments/providerCertification.graphql`
- `packages/graphql/operations/fragments/providerPresenceBasic.graphql`
- `packages/graphql/operations/fragments/qualityMetricBasic.graphql`
- `packages/graphql/operations/fragments/qualityMetricDetailed.graphql`
- `packages/graphql/operations/fragments/municipalityBasic.graphql`

### Modified

- `packages/graphql/operations/queries/seo/providers.graphql` - Uses fragments
- `packages/graphql/operations/queries/seo/provider.graphql` - Uses fragments
- `packages/graphql/operations/queries/seo/providersForMunicipality.graphql` - Uses fragments + `MunicipalityBasic`
- `packages/graphql/operations/queries/seo/providerDetail.graphql` - Uses fragments + `MunicipalityBasic`
- `packages/graphql/operations/queries/seo/providerMunicipalities.graphql` - Uses fragments + `MunicipalityBasic`

## Best Practices

### 1. Use Correct Fragment for Type

```graphql
# ✅ CORRECT - ProviderWithPresence type
query GetProvidersForMunicipality {
  providersForMunicipality {
    ...ProviderWithPresenceCore
  }
}

# ❌ WRONG - Wrong fragment type
query GetProvidersForMunicipality {
  providersForMunicipality {
    ...ProviderCore # Wrong - this is for Provider type
  }
}
```

### 2. Always Use MunicipalityBasic in Provider Queries

```graphql
# ✅ CORRECT - Consistent municipality fields
presence {
  municipality {
    ...MunicipalityBasic
  }
}

# ❌ WRONG - Inconsistent fields
presence {
  municipality {
    id
    slug
    name
    # Missing region, municipalityCode
  }
}
```

### 3. Use Appropriate Financial Fragment

```graphql
# ✅ CORRECT - Basic for lists
financials {
  ...ProviderFinancialsBasic
}

# ✅ CORRECT - Detailed for detail pages
financials {
  ...ProviderFinancialsDetailed
}
```

## Validation

The existing validation script (`validate-query-consistency.ts`) validates municipality queries. Provider queries are validated through:

- GraphQL schema validation (fragments must match types)
- TypeScript type checking
- Manual review of fragment usage

## Next Steps

1. ✅ All provider queries use fragments
2. ✅ Municipality data is consistent via `MunicipalityBasic`
3. ✅ Financial and quality fields standardized
4. ⏭️ Consider adding provider query validation to script
5. ⏭️ Document hook usage patterns for providers
