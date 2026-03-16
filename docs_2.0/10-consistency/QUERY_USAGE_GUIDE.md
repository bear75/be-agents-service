# GraphQL Query Usage Guide

## Overview

This guide ensures consistent usage of GraphQL queries and hooks across the frontend.

## Query Fragments

All queries should use fragments for common field sets to ensure consistency:

- `MunicipalityCore` - Basic municipality fields (id, slug, name, etc.)
- `MunicipalityFinances` - All finance fields
- `MunicipalityQuality` - Quality metrics and summaries
- `MunicipalityRankings` - Ranking data
- `MunicipalityHemtjanstindex` - Hemtjänstindex fields
- `MunicipalityProviderStats` - Provider counts and statistics

## Hook Usage Guide

### Municipality Hooks

| Hook                                      | Query Used                         | Use Case                         | When to Use                      |
| ----------------------------------------- | ---------------------------------- | -------------------------------- | -------------------------------- |
| `useGraphQLMunicipalityCompat`            | `GetMunicipality`                  | Single municipality detail page  | **RECOMMENDED** for detail pages |
| `useGraphQLMunicipality`                  | `GetMunicipality`                  | Single municipality (simple)     | Legacy - use Compat version      |
| `useGraphQLMunicipalities`                | `GetMunicipalities`                | All municipalities list          | Municipality listing/index pages |
| `useGraphQLTopMunicipalities`             | `GetTopMunicipalities`             | Top municipalities by category   | Top lists, rankings              |
| `useGraphQLMunicipalityWithProviderCount` | `GetMunicipalityWithProviderCount` | Municipality with provider count | When you only need count         |

### Provider Hooks

| Hook                              | Query Used                                   | Use Case                     | When to Use                                     |
| --------------------------------- | -------------------------------------------- | ---------------------------- | ----------------------------------------------- |
| `useGraphQLMunicipalityProviders` | `GetProvidersForMunicipality`                | Providers in a municipality  | **RECOMMENDED** for municipality provider lists |
| `useGraphQLProvidersCompat`       | `GetProviders` + `GetProviderMunicipalities` | Providers with presence data | Legacy - use MunicipalityProviders              |
| `useGraphQLProviders`             | `GetProviders`                               | All providers                | Global provider lists                           |
| `useGraphQLProvider`              | `GetProvider`                                | Single provider              | Provider detail page                            |

## Page Type → Query Mapping

### Municipality Pages

| Page Type                                 | Hook                           | Query                  | Fragments Used                      |
| ----------------------------------------- | ------------------------------ | ---------------------- | ----------------------------------- |
| Detail page (`/kommuner/:slug`)           | `useGraphQLMunicipalityCompat` | `GetMunicipality`      | All fragments + detailed indicators |
| List page (`/kommuner`)                   | `useGraphQLMunicipalities`     | `GetMunicipalities`    | All fragments                       |
| Top lists (`/topplistor/kommuner`)        | `useGraphQLTopMunicipalities`  | `GetTopMunicipalities` | All fragments                       |
| Region pages (`/kommuner/:slug/kvalitet`) | `useGraphQLMunicipalityCompat` | `GetMunicipality`      | All fragments                       |

### Provider Pages

| Page Type                                               | Hook                              | Query                         | Notes                  |
| ------------------------------------------------------- | --------------------------------- | ----------------------------- | ---------------------- |
| Municipality provider list (`/kommuner/:slug/utforare`) | `useGraphQLMunicipalityProviders` | `GetProvidersForMunicipality` | Includes presence data |
| Global provider list (`/hemtjanstanordnare`)            | `useGraphQLProviders`             | `GetProviders`                | All providers          |
| Provider detail (`/kommuner/:slug/utforare/:provider`)  | `useGraphQLProviderDetail`        | `GetProviderDetail`           | Full provider details  |

## Field Requirements

### Required Fields (All Municipality Queries)

All municipality queries MUST include:

- ✅ `homeCareRecipients` - Number of recipients
- ✅ `finances` - All finance fields (via fragment)
- ✅ `qualitySummaries` - All quality fields (via fragment)
- ✅ `rankings` - Ranking data (via fragment)

### Detail Page Only Fields

Only `GetMunicipality` includes:

- Detailed quality indicators (ind2-ind32, b9, b11)
- `regiformData` - Regiform comparison data
- All hemtjänstindex sub-fields

## Validation

Run validation to check query consistency:

```bash
yarn workspace @appcaire/graphql validate:queries
```

This checks:

- ✅ Required fields are present
- ✅ Fragments are used consistently
- ✅ No duplicate field definitions
- ✅ Field consistency across queries

## Best Practices

### 1. Always Use Fragments

```graphql
# ✅ GOOD
#import "../fragments/municipalityCore.graphql"
query GetMunicipality($slug: String!) {
  municipality(slug: $slug) {
    ...MunicipalityCore
    ...MunicipalityFinances
  }
}

# ❌ BAD
query GetMunicipality($slug: String!) {
  municipality(slug: $slug) {
    id
    slug
    name
    # ... duplicate fields
  }
}
```

### 2. Use Correct Hook for Page Type

```typescript
// ✅ GOOD - Detail page
const { municipality } = useGraphQLMunicipalityCompat(slug);

// ❌ BAD - Using wrong hook
const { municipalities } = useGraphQLMunicipalities();
const municipality = municipalities.find((m) => m.slug === slug);
```

### 3. Don't Mix Hooks

```typescript
// ✅ GOOD - Consistent hook usage
const { municipality } = useGraphQLMunicipalityCompat(slug);
const { providers } = useGraphQLMunicipalityProviders(slug);

// ❌ BAD - Mixing different hooks
const { municipality } = useGraphQLMunicipalityCompat(slug);
const { providers } = useGraphQLProviders(); // Wrong - doesn't filter by municipality
```

### 4. Handle Loading States

```typescript
// ✅ GOOD
const { municipality, isLoading, error } = useGraphQLMunicipalityCompat(slug);

if (isLoading) return <Loading />;
if (error) return <Error message={error} />;
if (!municipality) return <NotFound />;

// ❌ BAD - No loading/error handling
const { municipality } = useGraphQLMunicipalityCompat(slug);
return <div>{municipality.name}</div>; // Crashes if loading/error
```

## Common Mistakes

### ❌ Mistake 1: Using Wrong Query

```typescript
// ❌ WRONG - Using GetMunicipalities for single municipality
const { municipalities } = useGraphQLMunicipalities();
const municipality = municipalities.find((m) => m.slug === slug);

// ✅ CORRECT - Use single municipality query
const { municipality } = useGraphQLMunicipalityCompat(slug);
```

### ❌ Mistake 2: Missing Required Fields

```graphql
# ❌ WRONG - Missing homeCareRecipients
query GetTopMunicipalities {
  topMunicipalities {
    id
    slug
    name
  }
}

# ✅ CORRECT - Use fragment with all required fields
query GetTopMunicipalities {
  topMunicipalities {
    ...MunicipalityCore
  }
}
```

### ❌ Mistake 3: Inconsistent Field Sets

```graphql
# ❌ WRONG - Different fields in different queries
query GetMunicipality {
  municipality {
    finances {
      homeCareTotalSek
    }
  }
}
query GetTopMunicipalities {
  topMunicipalities {
    finances {
      year
    }
  }
}

# ✅ CORRECT - Same fragment in both
query GetMunicipality {
  municipality {
    ...MunicipalityFinances
  }
}
query GetTopMunicipalities {
  topMunicipalities {
    ...MunicipalityFinances
  }
}
```

## Migration Checklist

When updating a page to use consistent queries:

- [ ] Identify correct hook for page type
- [ ] Replace old hook with correct one
- [ ] Ensure query uses fragments
- [ ] Verify all required fields are present
- [ ] Test loading/error states
- [ ] Run validation: `yarn workspace @appcaire/graphql validate:queries`
- [ ] Update documentation if needed

## Troubleshooting

### Issue: Missing fields in query result

**Solution:** Check if query uses correct fragments and includes all required fields.

### Issue: Data inconsistent between pages

**Solution:** Ensure both pages use same query/hook and same fragments.

### Issue: Validation fails

**Solution:**

1. Check fragment usage
2. Verify required fields are present
3. Ensure no duplicate field definitions
