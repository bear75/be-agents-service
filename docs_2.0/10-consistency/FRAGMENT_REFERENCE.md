# GraphQL Fragment Reference

## Quick Reference

### Municipality Fragments

| Fragment                     | Fields                      | Used In                                        |
| ---------------------------- | --------------------------- | ---------------------------------------------- |
| `MunicipalityCore`           | 14 basic fields             | All municipality queries                       |
| `MunicipalityFinances`       | 14 finance fields           | All queries needing finances                   |
| `MunicipalityQuality`        | Quality metrics + summaries | All queries needing quality                    |
| `MunicipalityRankings`       | 6 ranking fields            | All queries needing rankings                   |
| `MunicipalityHemtjanstindex` | 9 hemtjänstindex fields     | Queries needing index data                     |
| `MunicipalityProviderStats`  | 5 provider stat fields      | Queries needing provider counts                |
| `MunicipalityBasic`          | 5 basic fields              | **Provider queries that include municipality** |

### Provider Fragments

| Fragment                     | Fields                     | Used In                       | Type                    |
| ---------------------------- | -------------------------- | ----------------------------- | ----------------------- |
| `ProviderCore`               | 20 core fields             | `GetProviders`, `GetProvider` | `Provider`              |
| `ProviderWithPresenceCore`   | 20 core fields             | `GetProvidersForMunicipality` | `ProviderWithPresence`  |
| `ProviderWithDetailsCore`    | 20 core fields             | `GetProviderWithDetails`      | `ProviderWithDetails`   |
| `ProviderCoreMinimal`        | 7 minimal fields           | `GetProviderMunicipalities`   | `Provider`              |
| `ProviderFinancialsBasic`    | 7 basic fields             | List queries                  | `ProviderFinancials`    |
| `ProviderFinancialsDetailed` | 18 detailed fields         | Detail queries                | `ProviderFinancials`    |
| `ProviderCertification`      | 7 certification fields     | Queries needing certification | `ProviderCertification` |
| `ProviderPresenceBasic`      | 6 presence fields          | Queries with presence data    | `ProviderMunicipality`  |
| `QualityMetricBasic`         | 5 basic quality fields     | List queries                  | `QualityMetric`         |
| `QualityMetricDetailed`      | 11 detailed quality fields | Detail queries                | `QualityMetric`         |

## Usage Examples

### Municipality Query

```graphql
#import "../fragments/municipalityCore.graphql"
#import "../fragments/municipalityFinances.graphql"
#import "../fragments/municipalityQuality.graphql"

query GetMunicipality($slug: String!) {
  municipality(slug: $slug) {
    ...MunicipalityCore
    ...MunicipalityFinances
    ...MunicipalityQuality
  }
}
```

### Provider Query with Municipality

```graphql
#import "../fragments/providerWithPresenceCore.graphql"
#import "../fragments/municipalityBasic.graphql"

query GetProvidersForMunicipality($slug: String!) {
  providersForMunicipality(municipalitySlug: $slug) {
    ...ProviderWithPresenceCore
    presence {
      municipality {
        ...MunicipalityBasic # Always use this for consistency
      }
    }
  }
}
```

## Fragment Locations

All fragments are in: `packages/graphql/operations/fragments/`

## Key Rule: Municipality in Provider Queries

**ALWAYS use `MunicipalityBasic` fragment when municipality data is included in provider queries:**

```graphql
# ✅ CORRECT
municipality {
  ...MunicipalityBasic
}

# ❌ WRONG - Inconsistent fields
municipality {
  id
  slug
  name
  # Missing region, municipalityCode
}
```

This ensures consistent municipality data (5 fields) across all provider queries.
