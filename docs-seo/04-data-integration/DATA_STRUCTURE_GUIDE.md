# Hemtjänst Data Structure Guide

> 📅 **Last Updated:** 2026-01-04  
> **Version:** 2.1  
> **Status:** Production Ready

## Table of Contents

1. [Overview](#overview)
2. [Data Hierarchy](#data-hierarchy)
3. [Database Schema](#database-schema)
4. [Data Sources](#data-sources)
5. [Data Collection Strategy](#data-collection-strategy)
6. [Seeding & Import](#seeding--import)
7. [Data Relationships](#data-relationships)
8. [Implementation Status](#implementation-status)
9. [Quick Reference](#quick-reference)

---

## Overview

This document describes the complete data structure for Swedish home care (hemtjänst) websites. The system stores data about:

- **290 Swedish municipalities** (kommuner)
- **~2,000 home care providers** (anordnare)
- **~200,000 home care users. Elderly and disabled** (brukare)
- **Quality metrics** from official sources
- **Financial data** from company registries
- **National and regional statistics**

### Data Hierarchy

```
┌─────────────────────────────────────────┐
│     National Statistics                 │
│     (Sverige - Aggregated)              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│     Municipalities (290 kommuner)       │
│     - Demographics                      │
│     - LOV status                        │
│     - Finance                           │
│     - Quality summaries                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│     Providers (~2,000 anordnare)         │
│     - Contact info                      │
│     - Financials                        │
│     - System/technology                 │
│     - Certifications                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│     Provider-Municipality Presences     │
│     (Many-to-many relationship)         │
│     - Active status                     │
│     - Customer counts                   │
│     - Quality metrics                   │
│     - Geographic areas                 │
└─────────────────────────────────────────┘
```

---

## Database Schema

### Core Models

#### 1. Municipality (Kommun)

**Table:** `municipalities`

Stores data for all 290 Swedish municipalities.

| Field                     | Type          | Source          | Description                      |
| ------------------------- | ------------- | --------------- | -------------------------------- |
| `id`                      | String (CUID) | -               | Primary key                      |
| `slug`                    | String        | -               | URL-friendly ID (e.g., "nacka")  |
| `name`                    | String        | SCB             | Full name (e.g., "Nacka kommun") |
| `region`                  | String?       | SCB             | Län (e.g., "Stockholms län")     |
| `municipalityCode`        | String?       | SCB             | SCB code (e.g., "182")           |
| `population`              | Int?          | SCB             | Total population                 |
| `elderlyPopulation`       | Int?          | SCB             | Population 65+                   |
| `elderlyPercentage`       | Float?        | SCB             | % of population 65+              |
| `homeCareRecipients`      | Int?          | Socialstyrelsen | Number of home care recipients   |
| `hasLov`                  | Boolean       | Manual          | Has LOV (customer choice system) |
| `lovSince`                | Int?          | Manual          | Year LOV was introduced          |
| `primarySystem`           | String?       | Manual          | Primary scheduling system        |
| `hasPrivateProviders`     | Boolean?      | kommun API      | Has private providers            |
| `privatizationPercentage` | Float?        | kommun API      | % private providers              |
| `publicProviders`         | Int?          | Computed        | Count of public providers        |
| `privateProviders`        | Int?          | Computed        | Count of private providers       |
| `scrapedProviders`        | Int?          | Manual          | Providers we have data for       |
| `websiteUrl`              | String?       | Manual          | Municipality website             |
| `providerListUrl`         | String?       | infoval.se      | Official provider list URL       |
| `qualityDataUrl`          | String?       | Manual          | Quality data source URL          |
| `sourceUrl`               | String?       | Manual          | Data source URL                  |
| `lastSynced`              | DateTime?     | -               | Last sync timestamp              |
| `notes`                   | String?       | Manual          | Additional notes                 |
| `jensnylanderSlug`        | String?       | kommun API      | Jens Nylander URL slug           |
| `externalIdsVerified`     | Boolean       | Manual          | External IDs verified by admin   |
| `externalIdsVerifiedAt`   | DateTime?     | Manual          | Verification timestamp           |

**Relations:**

- `presences` → ProviderMunicipality[] (providers in this municipality)
- `finances` → MunicipalityFinance[] (financial data per year)
- `qualitySummaries` → MunicipalityQualitySummary[] (aggregated quality)
- `districts` → District[] (geographic districts)

**Note:** Survey aggregated data fields (quality indicators, language support, etc.) are stored directly on the `Municipality` model. These fields were previously in a separate `socialstyrelsensKommun` table but have been merged for better performance and simpler queries.

#### 2. Provider (anordnare)

**Table:** `providers`

Stores data for all home care providers.

| Field                   | Type          | Source     | Description                            |
| ----------------------- | ------------- | ---------- | -------------------------------------- |
| `id`                    | String (CUID) | -          | Primary key                            |
| `slug`                  | String        | -          | URL-friendly ID                        |
| `orgNumber`             | String?       | kommun API | Organisationsnummer (unique)           |
| `name`                  | String        | kommun API | Business name                          |
| `legalName`             | String?       | tic.io     | Legal company name                     |
| `orgType`               | OrgType       | -          | MUNICIPAL/PRIVATE/NONPROFIT/UNKNOWN    |
| `address`               | String?       | kommun API | Street address                         |
| `postalCode`            | String?       | kommun API | Postal code                            |
| `city`                  | String?       | kommun API | City                                   |
| `phone`                 | String?       | Scraping   | Phone number                           |
| `email`                 | String?       | Scraping   | Email address                          |
| `website`               | String?       | Scraping   | Website URL                            |
| `logoUrl`               | String?       | Manual     | Logo file path                         |
| `description`           | String?       | Manual     | Provider description                   |
| `systemType`            | String?       | Manual     | System type (caire/carefox/ecare/etc.) |
| `hasUserApp`            | Boolean       | Manual     | Has user app                           |
| `hasRelativeApp`        | Boolean       | Manual     | Has relative app                       |
| `isCaireCertified`      | Boolean       | Manual     | Uses Caire platform                    |
| `corporateGroupId`      | String?       | -          | FK to CorporateGroup                   |
| `hubspotCompanyId`      | String?       | HubSpot    | CRM integration                        |
| `kommunApiId`           | String?       | kommun API | API identifier                         |
| `languages`             | String[]      | Manual     | Languages spoken                       |
| `specialCompetencies`   | String[]      | Manual     | Special competencies                   |
| `ivoLicensed`           | Boolean       | Manual     | Has IVO license                        |
| `ivoLicenseDate`        | String?       | Manual     | IVO license date                       |
| `parentName`            | String?       | tic.io     | Parent group name (denormalized)       |
| `lastSynced`            | DateTime?     | -          | Last sync timestamp                    |
| `jensnylanderSlug`      | String?       | kommun API | Jens Nylander URL slug                 |
| `jensnylanderId`        | String?       | kommun API | Jens Nylander API identifier           |
| `allabolagUrl`          | String?       | Manual     | Allabolag URL                          |
| `externalIdsVerified`   | Boolean       | Manual     | External IDs verified by admin         |
| `externalIdsVerifiedAt` | DateTime?     | Manual     | Verification timestamp                 |

**Relations:**

- `presences` → ProviderMunicipality[] (municipalities where active)
- `brands` → ProviderBrand[] (brand names/history)
- `financials` → ProviderFinancials[] (financial data per year)
- `contacts` → ProviderContact[] (contact persons)
- `corporateGroup` → CorporateGroup (parent organization)

**Note:** Quality indicator fields (services, language support, routines, etc.) are stored directly on the `Provider` model. These fields were previously in a separate `socialstyrelsensEnhet` table but have been merged for better performance and simpler queries. Certification fields are also directly on the Provider model.

#### 3. ProviderMunicipality (Presence)

**Table:** `provider_municipality_presences`

Join table linking providers to municipalities with context-specific data.

| Field                | Type           | Source     | Description            |
| -------------------- | -------------- | ---------- | ---------------------- |
| `id`                 | String (CUID)  | -          | Primary key            |
| `providerId`         | String         | -          | FK to Provider         |
| `municipalityId`     | String         | -          | FK to Municipality     |
| `status`             | PresenceStatus | -          | ACTIVE/INACTIVE        |
| `activeSinceYear`    | Int?           | Manual     | Year provider started  |
| `isApprovedInLov`    | Boolean        | Manual     | Approved in LOV system |
| `customerCount`      | Int?           | infoval.se | Exact customer count   |
| `customerCountRange` | String?        | infoval.se | Range (e.g., "51-100") |
| `hoursPerMonth`      | Float?         | kommun API | Hours delivered/month  |
| `hoursPerYear`       | Float?         | kommun API | Hours delivered/year   |
| `geographicAreas`    | String[]       | Manual     | Areas covered          |
| `sourceUrl`          | String?        | infoval.se | Source URL             |
| `lastSyncedAt`       | DateTime?      | -          | Last sync timestamp    |

**Relations:**

- `qualityMetrics` → QualityMetric[] (quality data per year)

**Unique Constraint:** `[providerId, municipalityId]` (one presence per provider-municipality)

#### 4. QualityMetric

**Table:** `quality_metrics`

Quality metrics per provider-municipality per year.

| Field                   | Type          | Source             | Description                |
| ----------------------- | ------------- | ------------------ | -------------------------- |
| `id`                    | String (CUID) | -                  | Primary key                |
| `presenceId`            | String        | -                  | FK to ProviderMunicipality |
| `year`                  | Int           | -                  | Year of data               |
| `customerSatisfaction`  | Float?        | Brukarundersökning | Overall satisfaction (%)   |
| `overallSatisfaction`   | Float?        | Brukarundersökning | Overall rating             |
| `treatmentSatisfaction` | Float?        | Brukarundersökning | Treatment quality          |
| `influenceSatisfaction` | Float?        | Brukarundersökning | Ability to influence       |
| `safetySatisfaction`    | Float?        | Brukarundersökning | Safety feeling             |
| `staffContinuity`       | Float?        | Brukarundersökning | Staff per 14 days          |
| `staffContinuityScore`  | Float?        | Computed           | Continuity index (0-100)   |
| `hemtjanstIndex`        | Float?        | infoval.se         | Composite quality index    |
| `source`                | SourceType    | -                  | Data source                |
| `sourceRef`             | String?       | -                  | Source reference URL       |

**Unique Constraint:** `[presenceId, year, source]` (one metric per presence-year-source)

#### 5. ProviderFinancials

**Table:** `provider_financials`

Financial data per provider per year.

| Field                    | Type          | Source     | Description                      |
| ------------------------ | ------------- | ---------- | -------------------------------- |
| `id`                     | String (CUID) | -          | Primary key                      |
| `providerId`             | String        | -          | FK to Provider                   |
| `year`                   | Int           | -          | Financial year                   |
| `source`                 | SourceType    | -          | tic.io/allabolag/kommun API      |
| `revenueSek`             | BigInt?       | tic.io     | Annual revenue (SEK)             |
| `profitSek`              | BigInt?       | tic.io     | Profit/loss (SEK)                |
| `profitMarginPct`        | Float?        | tic.io     | Profit margin (%)                |
| `employeeCount`          | Int?          | tic.io     | Number of employees              |
| `fullTimeEquivalents`    | Int?          | tic.io     | FTE count                        |
| `ticRiskLevel`           | Int?          | tic.io     | Risk level (1-5)                 |
| `ticCreditRating`        | String?       | tic.io     | Credit rating (A-F)              |
| `totalInvoicedSek`       | BigInt?       | kommun API | Total invoiced to municipalities |
| `invoicedMunicipalities` | String[]      | kommun API | List of municipality slugs       |
| `sourceRef`              | String?       | -          | Source reference URL             |
| `lastUpdated`            | DateTime      | -          | Last update timestamp            |

**Unique Constraint:** `[providerId, year, source]` (one financial record per provider-year-source)

#### 6. MunicipalityFinance

**Table:** `municipality_finances`

Financial data per municipality per year.

| Field                       | Type          | Source   | Description                  |
| --------------------------- | ------------- | -------- | ---------------------------- |
| `id`                        | String (CUID) | -        | Primary key                  |
| `municipalityId`            | String        | -        | FK to Municipality           |
| `year`                      | Int           | -        | Financial year               |
| `totalExpenditureSek`       | BigInt?       | SCB      | Total expenditure            |
| `taxRevenueSek`             | BigInt?       | SCB      | Tax revenue                  |
| `homeCareElderlySek`        | BigInt?       | SCB      | Home care for elderly        |
| `homeCareDisabilitySek`     | BigInt?       | SCB      | Home care for disability     |
| `homeCareTotalSek`          | BigInt?       | SCB      | Total home care costs        |
| `homeCareShareOfEconomyPct` | Float?        | Computed | % of total expenditure       |
| `personalAssistanceSek`     | BigInt?       | SCB      | Personal assistance costs    |
| `costTrend`                 | CostTrend?    | Computed | INCREASING/STABLE/DECREASING |
| `source`                    | SourceType    | -        | SCB/manual                   |
| `sourceRef`                 | String?       | -        | Source reference URL         |

#### 7. CorporateGroup

**Table:** `corporate_groups`

Groups providers that belong to the same corporate group.

| Field                 | Type          | Description                            |
| --------------------- | ------------- | -------------------------------------- |
| `id`                  | String (CUID) | Primary key                            |
| `slug`                | String        | URL-friendly ID                        |
| `name`                | String        | Group name                             |
| `orgNumber`           | String?       | Shared org number                      |
| `website`             | String?       | Group website                          |
| `totalProviders`      | Int?          | Count of providers (denormalized)      |
| `totalMunicipalities` | Int?          | Count of municipalities (denormalized) |
| `totalCustomers`      | Int?          | Total customers (denormalized)         |
| `totalEmployees`      | Int?          | Total employees (denormalized)         |

**Relations:**

- `providers` → Provider[] (providers in this group)

#### 8. NationalStatistics

**Table:** `national_statistics`

Aggregated national-level statistics per year.

**Key Categories:**

- Welfare system description
- Privatization statistics
- Budget (total, public, private)
- Recipients (total, averages)
- Providers (total, public, private, groups)
- Employees (total, public, private, FTE)
- Hours (total, public, private, averages)
- Quality (national averages, targets)
- **Company Size Distribution** (micro, small, medium, large - absolute + percentages)
- **Recipients with Private Care** (from Socialstyrelsen PDFs)
- **JSON fields** for complex data (trends, municipality distributions)

**Relations:**

- `regions` → RegionBreakdown[] (regional statistics)
- `regulatoryComplianceCosts` → RegulatoryComplianceCosts[] (regulatory cost data)
- `salaryStatistics` → SalaryStatistics[] (salary data by profession)
- `dataSources` → DataSource[] (data sources used)

**New Fields (2025-12-29):**

- `microCompanies`, `smallCompanies`, `mediumCompanies`, `largeCompanies` (Int)
- `microCompaniesPercentage`, `smallCompaniesPercentage`, etc. (Float)
- `recipientsPrivateCare` (Int)
- `recipientsWithoutReportedCarePercentage` (Float)
- `municipalitiesWithoutReportingObligation` (Int)
- `companySizeTrends` (Json) - Trends over time
- `privatizationPercentageByMunicipality` (Json) - Per-municipality data
- `providersPerMunicipalityDistribution` (Json) - Distribution patterns
- `employeesWithLicensedProfessions` (Int)
- `companySizeByLicensedEmployees` (Json)

#### 8a. RegulatoryComplianceCosts

**Table:** `regulatory_compliance_costs`

Cost data for regulatory compliance (from Socialstyrelsen PDFs - Tabell 9, 10).

**Key Data:**

- Cost ranges (min/max) for various compliance activities
- Separate data for providers "with KVÅ" vs "without KVÅ"
- Separate data for micro companies vs all companies
- Administrative time costs (initial, annual)
- Consultant usage statistics

**Source:** Socialstyrelsen PDFs (2023-12-8864.pdf)

**Relations:**

- `nationalStats` → NationalStatistics (one-to-one via `nationalStatsId`)

#### 8b. SalaryStatistics

**Table:** `salary_statistics`

Salary data for private sector healthcare professions (from Socialstyrelsen PDFs - Tabell 6).

**Key Data:**

- Monthly salary (kr)
- Monthly salary including benefits (kr)
- Hourly salary (kr)
- By profession (Arbetsterapeut, Fysioterapeut, Sjuksköterska, etc.)

**Source:** SCB lönestatistik (via Socialstyrelsen PDFs)

**Relations:**

- `nationalStats` → NationalStatistics (many-to-one via `nationalStatsId`)

**Unique Constraint:** `[nationalStatsId, profession]`

#### 9. RegionBreakdown

**Table:** `region_breakdowns`

Regional (län) breakdowns of national statistics.

| Field                     | Type          | Description                                  |
| ------------------------- | ------------- | -------------------------------------------- |
| `id`                      | String (CUID) | Primary key                                  |
| `nationalStatsId`         | String        | FK to NationalStatistics                     |
| `regionId`                | String        | Länskod (e.g., "01" for Stockholms län)      |
| `regionName`              | String        | Länsnamn (e.g., "Stockholms län")            |
| `municipalityCount`       | Int?          | Number of municipalities in the region       |
| `providerCount`           | Int?          | Number of providers in the region            |
| `avgCustomerSatisfaction` | Float?        | Average customer satisfaction for the region |
| `avgStaffContinuity`      | Float?        | Average staff continuity for the region      |
| `regiformData`            | Json?         | Comparison data by regiform (Public/Private) |
| `indX...`                 | Float?        | 30+ quality indicators from Socialstyrelsen  |

**Status:** ✅ **POPULATED** - Updated annually by `seed-socialstyrelsen.ts`.

**Relations:**

- `nationalStats` → NationalStatistics (parent table)

---

## Data Sources

### Primary Sources

| Source                      | Type          | Data Provided                           | Update Frequency | Priority    |
| --------------------------- | ------------- | --------------------------------------- | ---------------- | ----------- |
| **infoval.se**              | Scraping      | Current provider lists, quality metrics | Weekly           | 🔥 Critical |
| **kommun.jensnylander.com** | API (Free)    | Provider lists, invoicing, org numbers  | Real-time        | 🔥 Critical |
| **Socialstyrelsen**         | CSV/PDF       | Quality indicators, survey data         | Annually (Oct)   | 🔥 Critical |
| **tic.io**                  | API (Premium) | Financial data, risk ratings, credit    | Real-time        | High        |
| **Allabolag**               | API/Export    | Financial data (fallback)               | On-demand        | Medium      |
| **SCB**                     | API           | Demographics, municipality finances     | Annually         | Medium      |
| **Äldreguiden**             | Scraping      | Quality comparisons                     | Annually         | Low         |

### Source Details

#### 1. infoval.se (Source of Truth - Current Providers)

**URL:** https://www.infoval.se/[municipality]/10

**Status:** ✅ **PRIMARY SOURCE** for current provider lists

**Data:**

- Official, up-to-date municipality provider lists
- Includes newer providers not yet in CSV surveys
- Quality metrics per provider
- Customer counts
- Contact information

**Example:** [infoval.se/nacka/10](https://www.infoval.se/nacka/10) lists all 15 current providers

**Note:** JSON files (`nacka.json`, `stockholm.json`) are sourced from infoval.se and serve as the source of truth for current providers.

### Data Priority Hierarchy

When multiple sources contain the same provider, use this priority order:

1. **Municipality Websites** (infoval.se, aldreomsorg.stockholm.se, aldreguiden.se)
   - **Source of truth** for current provider lists
   - Most up-to-date, includes newer providers
   - Updated regularly by municipalities

2. **JSON Files** (scraped from municipality websites)
   - Current provider lists + enrichment metadata
   - Contact information, descriptions, logos
   - **Takes priority over CSV data** when matching providers

3. **CSV Files** (Socialstyrelsen surveys)
   - Historical/quality data from specific survey periods
   - Quality indicators and metrics
   - **May miss newer providers** that started after survey period
   - Used to **enrich** existing providers, not create new ones

4. **API Sources** (kommun.jensnylander.com, tic.io, allabolag.se)
   - Financial and invoicing data
   - Provider identification (org numbers)
   - Real-time or on-demand updates

#### 2. kommun.jensnylander.com API

**URL:** https://kommun.jensnylander.com  
**API Docs:** https://kommundata.readme.io/

**Status:** ✅ **PRIMARY SOURCE** for provider identification

**Endpoints:**

```
GET /api/suppliers?snilabels=88101,88102  # Home care suppliers
GET /api/suppliers/{id}                   # Supplier details
```

**SNI Codes:**

- `88101` - Vård och omsorg i särskilda boendeformer för äldre
- `88102` - Hemtjänst och annan social omsorg utan boende för äldre

**Data:**

- Provider names and org numbers
- Municipal invoicing amounts
- Which municipalities each provider serves
- Contact information

**Environment Variable:**

```bash
KOMMUN_API_KEY=your_api_key  # Optional, may work without
```

#### 3. Socialstyrelsen (Enhetsundersökningen)

**URL:** https://www.socialstyrelsen.se/statistik-och-data/oppna-jamforelser/

**Status:** ✅ **IMPORTED** - Quality data source

**CSV Files:**

- `2025-10-9834-resultat - Hemtjänst, enheter.csv` - Unit-level data (~1,800+ providers)
  - Location: `packages/shared/seo/data/kommun-data/`
  - Used by: `apps/stats-server/src/seed-scripts/03-seed-providers-csv.ts`
  - Seeds: `Provider` and `ProviderMunicipality` tables (quality indicator fields directly on Provider)
- `2025-10-9834-resultat - Hemtjänst, kommun, län, rike.csv` - Aggregated statistics
  - Location: `packages/shared/seo/data/kommun-data/`
  - Used by: `apps/stats-server/src/seed-scripts/04-seed-municipality-survey.ts`
  - Updates: `Municipality` table with aggregated quality indicators
- `2025-10-9834-resultat - Information.csv` - Metadata about the survey
  - Location: `packages/shared/seo/data/kommun-data/`
  - Purpose: Reference material only
- `oppna-jamforelser-aldreundersokningar-2025-inloggningsuppgifter-indikator-login.csv` - Login credentials
  - Location: `packages/shared/seo/data/kommun-data/`
  - Purpose: Reference material for Indikator web tool

**PDF Files:**

- `2025-10-9834-enkater.pdf` - Unit survey questionnaire
  - Location: `docs/docs-seo/04-data-integration/socialstyrelsen/`
  - Purpose: Reference - survey questions
- `2025-10-9834-indikatorbeskrivning.pdf` - Indicator definitions
  - Location: `docs/docs-seo/04-data-integration/socialstyrelsen/`
  - Purpose: Reference - explains what each quality indicator means
- `2025-10-9834-metodbeskrivning.pdf` - Methodology description
  - Location: `docs/docs-seo/04-data-integration/socialstyrelsen/`
  - Purpose: Reference - explains survey methodology
- `oppna-jamforelser-aldreundersokningar-2025-manual-indikators-webbverktyg.pdf` - Web tool manual
  - Location: `docs/docs-seo/04-data-integration/socialstyrelsen/`
  - Purpose: Reference - manual for Socialstyrelsen's web comparison tool

**Data:**

- 32+ quality indicators per unit
- Safety routines
- Medication routines
- Staffing metrics
- Language support
- Background metrics

**Update Schedule:**

- March-April: Surveys sent
- May: Deadline
- October: Results published

**Note:** CSV data is **historical** - may miss newer providers that started after survey period.

#### 4. Socialstyrelsen (Brukarundersökningen)

**Status:** ✅ **SCRIPT READY** - Customer satisfaction data

**PDF Files:**

- `2025-10-9793-enkater2025.pdf` - Survey questionnaire
  - Location: `docs/docs-seo/04-data-integration/socialstyrelsen/`
  - Purpose: Reference - survey questions for customer satisfaction
- `2025-10-9793-metodbeskrivning2025.pdf` - Methodology description
  - Location: `docs/docs-seo/04-data-integration/socialstyrelsen/`
  - Purpose: Reference - explains survey methodology
- `2025-10-9793-nationella-resultat2025.pdf` - National results
  - Location: `docs/docs-seo/04-data-integration/socialstyrelsen/`
  - Purpose: Reference - aggregated national statistics
- `2025-10-9793.pdf` - General documentation
  - Location: `docs/docs-seo/04-data-integration/socialstyrelsen/`
  - Purpose: Reference material

**Excel Files:**

- `2025-10-9793-bilaga-hemtjanst-verksamheter-2025.xlsx` - Per provider data
- `2025-10-9793-bilaga-hemtjanst-rike-lan-kommun-2022-2024.xlsx` - Aggregated data

**Data:**

- Customer satisfaction (F21)
- Treatment satisfaction (F9)
- Influence satisfaction (F7)
- Safety satisfaction (F17)
- **Missing:** Staff continuity (not in Excel files, requires raw data)

**Import Command:**

```bash
yarn workspace stats-server db:seed:05-provider-satisfaction
```

#### 5. tic.io API (Premium)

**URL:** https://tic.io

**Status:** ⚠️ **OPTIONAL** - Premium financial data

**Data:**

- Revenue, profit, employees
- Credit ratings (A-F)
- Risk levels (1-5)
- Corporate relationships
- Real-time monitoring

**Environment Variable:**

```bash
TIC_API_KEY=your_api_key
```

**Fallback:** Allabolag API if tic.io unavailable

#### 6. Allabolag (Fallback)

**URL:** https://www.allabolag.se

**Status:** ⚠️ **FALLBACK** - Financial data

**Options:**

1. **Allabolag Plus API** (129 kr/month) - Recommended if no tic.io
2. **Allabolag Plus Export** - Manual export (100 companies/month)
3. **Web Scraping** - Not recommended (ToS issues)

**Data:**

- Financial reports (bokslut)
- Revenue, profit, equity
- Employee count
- Company valuations

#### 7. SCB (Statistics Sweden)

**URL:** https://www.statistikdatabasen.scb.se

**Status:** ⚠️ **NOT IMPLEMENTED** - Demographics and finances

**Data:**

- Population per municipality
- Population 65+
- Municipality finances
- Home care costs
- Personal assistance costs

**API:** Open API available

---

## Data Collection Strategy

### Recommended Approach: Hybrid API + Scraping

#### Phase 1: API-First (Quick Coverage)

**Use kommun.jensnylander.com API** to get provider lists for all 290 municipalities:

1. Iterate through all municipalities
2. Call API for SNI codes 88101, 88102
3. Store in database
4. **Time estimate:** 2-4 hours for all 290 municipalities

**Benefits:**

- ✅ Complete coverage (all 290 municipalities)
- ✅ Fast (API calls)
- ✅ Reliable (structured data)
- ✅ Org numbers for matching

#### Phase 2: Quality Data Enrichment (Selective Scraping)

**For municipalities with published quality data:**

**Sources:**

- `infoval.se` - Stockholm area (Nacka, Solna, etc.)
- `aldreomsorg.stockholm` - Stockholm specific
- `aldreguiden.se` - Many municipalities

#### 6. JSON Files (Manual Scraping from Municipality Websites)

**Status:** ✅ **PRIMARY SOURCE** - Current provider lists

**Location:** `packages/shared/seo/data/providers/` (if exists) or `apps/stats-server/src/seed-scripts/seed-data/`

**Files:**

- `nacka.json` - Scraped from infoval.se/nacka/10
  - Contains: 15 current providers for Nacka municipality
  - Used by: `apps/stats-server/src/seed-scripts/02-seed-municipalities.ts` (seed script)
  - Used by: Runtime (static import in `useProviders.ts`)
  - **DO NOT DELETE** - Required for app to function
- `stockholm.json` - Scraped from aldreomsorg.stockholm.se
  - Contains: Current providers for Stockholm municipality
  - Used by: `apps/stats-server/src/seed-scripts/02-seed-municipalities.ts` (seed script)
  - Used by: Runtime (static import in `useProviders.ts`)
  - **DO NOT DELETE** - Required for app to function
- `sverige_kommuner.json` - All 290 Swedish municipalities
  - Contains: Basic municipality data (name, region, codes, demographics)
  - Used by: `apps/stats-server/src/seed-scripts/02-seed-municipalities.ts` (seed script)
  - Used by: Runtime (static import in `useProviders.ts`)
  - **DO NOT DELETE** - Required for app to function
- `SaanDOmsorg_hemtjanst.json` - Example provider-specific format
  - Contains: Example structure for provider-specific JSON files
  - Status: Currently unused (example/reference only)
  - **Can be archived** if confirmed unused

**Purpose:**

- Current provider lists (sourced from municipality websites - source of truth)
- Contact information (phone, email, address)
- Descriptions and logos
- Quality metrics (from CSV/Socialstyrelsen when available)
- Provider contacts
- System/technology information

**Note:** JSON files are manually created by scraping municipality websites. They represent the **most current** provider lists and take priority over CSV data.

#### 7. Branschrapport Files (Financial Data)

**Status:** ⚠️ **IMPORT AVAILABLE** - Financial data from tic.io or similar sources

**Location:**

- PDF: `docs/docs-seo/04-data-integration/socialstyrelsen/Nova-omsorg/`
- CSV: `packages/shared/seo/data/kommun-data/` or `apps/stats-server/src/seed-scripts/seed-data/13-branschrapport/`

**Files:**

- `Branschrapport_Nova Omsorg i Stockholm AB_5568594385_316787_sv_Hemtjänst.pdf` - PDF report
  - Purpose: Financial report for specific provider
  - Contains: Revenue, employees, EBIT, EBITDA, profit margins, risk ratings
- `Branschrapport_Nova Omsorg i Stockholm AB_5568594385_316787_sv_Hemtjänst - Blad 1.csv` - CSV export
  - Purpose: Structured financial data for import
  - Contains: Same data as PDF in CSV format
  - Columns: Företagsnamn, Orgnummer, Nettoomsättning, Antal anställda, EBIT, EBITDA, etc.

**Data Schema:**

- Matches `ProviderFinancials` model in Prisma schema
- Can be imported via `seed-financials.ts` or dedicated Branschrapport import script
- Match providers by `orgNumber` to link financial data

**Usage:**

- Import financial data for providers when available
- Store in `provider_financials` table with source `TIC` or `MANUAL`
- Used for provider financial analysis and risk assessment

**Priority municipalities:**

1. Stockholm (25 providers) ✅ Done
2. Nacka (15 providers) ✅ Done
3. Top 20 largest municipalities (~60% of population)
4. Municipalities with LOV systems

**Data from scraping:**

- Customer satisfaction
- Staff continuity
- Hemtjänst index
- Customer counts
- Geographic coverage
- Contact information

#### Phase 3: Automated Updates

**Nightly cron job:**

1. Fetch providers from kommun API (updates org numbers, invoicing)
2. For priority municipalities, scrape quality data
3. Update database

**Annual updates:**

- October: Import Socialstyrelsen CSV data
- May-June: Update financial data (after annual reports)

---

## Seeding & Import

### Seed Scripts Overview

| Script                              | Command                            | Source                            | Tables                                                        | Status   |
| ----------------------------------- | ---------------------------------- | --------------------------------- | ------------------------------------------------------------- | -------- |
| `01-seed-national-statistics.ts`    | `db:seed:01-national`              | JSON                              | `national_statistics`                                         | ✅ Ready |
| `02-seed-municipalities.ts`         | `db:seed:02-municipalities`        | JSON files                        | `municipalities`, `providers`, `presences`, `quality_metrics` | ✅ Ready |
| `03-seed-providers-csv.ts`          | `db:seed:03-providers-csv`         | CSV (enheter)                     | `providers`, `provider_municipality`                          | ✅ Ready |
| `03.5-seed-providers-enrichment.ts` | `db:seed:03.5-enrichment`          | kommun export                     | `providers`, `provider_municipality`                          | ✅ Ready |
| `04-seed-municipality-survey.ts`    | `db:seed:04-survey`                | CSV (kommun)                      | `municipalities` (aggregated fields)                          | ✅ Ready |
| `05-seed-provider-satisfaction.ts`  | `db:seed:05-provider-satisfaction` | CSV (292 files)                   | `quality_metrics`, `provider_municipality`                    | ✅ Ready |
| `05.5-seed-quality-metrics.ts`      | `db:seed:05.5-quality-metrics`     | Scraped JSON                      | `quality_metrics`                                             | ✅ Ready |
| `06-seed-quality-summaries.ts`      | `db:seed:06-quality-summaries`     | Aggregated from `quality_metrics` | `municipality_quality_summaries`                              | ✅ Ready |
| `07-seed-hemtjanstindex.ts`         | `db:seed:07-hemtjanstindex`        | JSON                              | `municipalities` (hemtjanstindex fields)                      | ✅ Ready |
| `08-calculate-rankings.ts`          | `db:seed:08-rankings`              | Computed                          | `municipality_rankings`, `provider_rankings`                  | ✅ Ready |
| `09-seed-skr-data.ts`               | `db:seed:09-skr`                   | SKR data                          | `municipalities` (SKR fields)                                 | ✅ Ready |
| `10-seed-homecare-recipients.ts`    | `db:seed:10-recipients`            | SCB/Kolada                        | `municipalities` (recipient counts)                           | ✅ Ready |
| `10.5-seed-kolada-kpis.ts`          | `db:seed:10.5-kolada`              | Kolada API                        | `municipalities` (KPI fields)                                 | ✅ Ready |
| `11-seed-financials.ts`             | `db:seed:11-financials`            | tic.io/allabolag API              | `provider_financials`                                         | ✅ Ready |
| `12-seed-kommun-api.ts`             | `db:seed:12-kommun-api`            | kommun.jensnylander.com API       | `providers`, `provider_financials`, `presences`               | ✅ Ready |
| `13-seed-branschrapport.ts`         | `db:seed:13-branschrapport`        | CSV                               | `unmatched_import_records`                                    | ✅ Ready |
| `14-seed-scb-data.ts`               | `db:seed:14-scb`                   | SCB API                           | `municipalities` (SCB fields)                                 | ✅ Ready |
| `15-seed-gamification.ts`           | `db:seed:15-gamification`          | Static config                     | `provider_levels`, `provider_badges`, `provider_tasks`        | ✅ Ready |
| `16-seed-data-sources.ts`           | `db:seed:16-data-sources`          | Static config                     | `data_source_configs`                                         | ✅ Ready |
| `17-seed-municipality-finances.ts`  | `db:seed:17-finances`              | SCB/Manual                        | `municipality_finances`                                       | ✅ Ready |
| `18-seed-sync-provider-rows.ts`     | `db:seed:18-sync-rows`             | Computed                          | `providers` (sync consistency)                                | ✅ Ready |
| `19-seed-sync-counts.ts`            | `db:seed:19-sync-counts`           | Computed                          | Denormalized counts                                           | ✅ Ready |
| `20-seed-scb-table-configs.ts`      | `db:seed:20-scb-configs`           | Static config                     | `scb_table_configs`                                           | ✅ Ready |
| `21-seed-kolada-ous.ts`             | `db:seed:21-kolada-ous`            | Kolada API                        | `kolada_ous`                                                  | ✅ Ready |
| `22-seed-pdf-statistics.ts`         | `db:seed:22-pdf-statistics`        | PDF extraction                    | `national_statistics`                                         | ✅ Ready |
| `23-seed-salary-statistics.ts`      | `db:seed:23-salary-statistics`     | SCB API                           | `salary_statistics`                                           | ✅ Ready |
| `24-seed-scraped-data.ts`           | `db:seed:24-scraped-data`          | Scraped JSON                      | `providers`, `municipalities`                                 | ✅ Ready |
| `25-seed-scraping-status.ts`        | `db:seed:25-scraping-status`       | Computed                          | `scraping_status`                                             | ✅ Ready |

### Recommended Seeding Order

**Recommended: Full Seed (All Data Sources)**

```bash
# Seed all data sources in correct order
yarn workspace stats-server db:seed
```

This runs all seed scripts in the correct order (see [SEED_SYSTEM_GUIDE.md](./SEED_SYSTEM_GUIDE.md) for details):

1. National statistics from JSON
2. Municipalities & test providers from JSON
3. **Providers from CSV** (PRIMARY SOURCE - 1,800+ providers)
4. Provider enrichment from kommun export
5. Municipality aggregates from CSV
6. Provider satisfaction data from CSV
7. Quality metrics from scraped data
8. Quality summaries aggregation
9. Hemtjänstindex rankings
10. Calculate rankings (weighted scores)
11. SKR municipality groups
12. Home care recipients
13. Kolada KPI data
14. Financial data (optional, requires API keys)
15. Kommun API data (optional, requires API keys)
16. Branschrapport data
17. SCB municipality data
18. Gamification system
19. Data source configurations
20. Municipality finances
21. Sync provider rows
22. Sync counts
23. SCB table configs
24. Kolada OUs
25. PDF statistics
26. Salary statistics
27. Scraped data
28. Scraping status

### Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:password@host:port/database?schema=public

# Optional - API Keys (server-side, no VITE_ prefix)
KOMMUN_API_KEY=your_kommun_api_key
TIC_API_KEY=your_tic_api_key
ALLABOLAG_API_KEY=your_allabolag_api_key
```

### Database Setup

**Prisma Commands:**

```bash
# Generate Prisma Client
yarn workspace stats-server db:generate

# Create/migrate database (development)
yarn workspace stats-server db:migrate

# Push schema without migration (prototyping)
yarn workspace stats-server db:push

# Open Prisma Studio (GUI)
yarn workspace stats-server db:studio

# Deploy migrations (production)
yarn workspace stats-server db:migrate:deploy
```

---

## Data Relationships

### Provider ↔ Municipality (Many-to-Many)

**Via:** `provider_municipality_presences` table

**Key Points:**

- One provider can be active in multiple municipalities
- One municipality has multiple providers
- Presence table stores municipality-specific data:
  - Customer counts
  - Quality metrics
  - Geographic areas
  - Active status

**Example:**

```
Provider: "SaanD Omsorg"
  ├─ Presence in Nacka (15 customers, active since 2024)
  ├─ Presence in Stockholm (50 customers, active since 2023)
  └─ Presence in Värmdö (10 customers, active since 2025)
```

### Provider → CorporateGroup (Many-to-One)

**Via:** `corporateGroupId` field on Provider

**Key Points:**

- Multiple providers can belong to one corporate group
- Groups are automatically detected during seeding (by `legalName` or `parentName`)
- Only creates groups for 2+ providers sharing same parent

**Example:**

```
CorporateGroup: "Nova Omsorg i Stockholm AB"
  ├─ Provider: "Nova Omsorg Bromma"
  ├─ Provider: "Nova Omsorg Södermalm"
  └─ Provider: "Nova Omsorg Kungsholmen"
```

### Provider → ProviderFinancials (One-to-Many)

**Via:** `providerId` field on ProviderFinancials

**Key Points:**

- Multiple financial records per provider (one per year)
- Supports multiple sources (tic.io, allabolag, kommun API)
- Unique constraint: `[providerId, year, source]`

### ProviderMunicipality → QualityMetric (One-to-Many)

**Via:** `presenceId` field on QualityMetric

**Key Points:**

- Multiple quality metrics per presence (one per year)
- Supports multiple sources (Socialstyrelsen, infoval, etc.)
- Unique constraint: `[presenceId, year, source]`

### Municipality → MunicipalityFinance (One-to-Many)

**Via:** `municipalityId` field on MunicipalityFinance

**Key Points:**

- Multiple finance records per municipality (one per year)
- Tracks financial trends over time

---

## Implementation Status

### ✅ Completed

| Feature                    | Status      | Notes                               |
| -------------------------- | ----------- | ----------------------------------- |
| **Database Schema**        | ✅ Complete | All models defined in Prisma schema |
| **Municipality Data**      | ✅ Complete | All 290 municipalities seeded       |
| **Provider Data**          | ✅ Complete | JSON files + CSV extraction         |
| **Quality Metrics**        | ✅ Complete | From CSV + Brukarundersökning       |
| **Corporate Groups**       | ✅ Complete | Auto-detected during seeding        |
| **Socialstyrelsen Data**   | ✅ Complete | Enhetsundersökning imported         |
| **Seed Scripts**           | ✅ Complete | All 25 seed scripts ready           |
| **kommun API Integration** | ✅ Complete | API client + seed script            |

### ⚠️ Partially Implemented

| Feature                   | Status          | Notes                                                                  |
| ------------------------- | --------------- | ---------------------------------------------------------------------- |
| **Financial Data**        | ⚠️ Script Ready | APIs exist, but not auto-called during seeding                         |
| **Brukarundersökning**    | ⚠️ Script Ready | Excel import script exists, needs to be run                            |
| **Municipality Finances** | ✅ Script Ready | Seed script exists (17-seed-municipality-finances.ts)                  |
| **Quality Summaries**     | ⚠️ Script Ready | Aggregation script exists, needs to be run                             |
| **SCB Integration**       | ✅ Script Ready | Seed scripts exist (14-seed-scb-data.ts, 20-seed-scb-table-configs.ts) |

### ❌ Missing

| Feature                 | Status             | Notes                                       |
| ----------------------- | ------------------ | ------------------------------------------- |
| **SCB Demographics**    | ❌ Not Implemented | Need API client for population data         |
| **SCB Finances**        | ❌ Not Implemented | Need API client for municipality finances   |
| **Automated Updates**   | ❌ Not Implemented | No cron jobs or scheduled tasks             |
| **Acquisition History** | ❌ Not Implemented | Low priority, can use ProviderBrand for now |
| **Region Breakdowns**   | ✅ Populated       | Updated by 04-seed-municipality-survey.ts   |

### Data Completeness

**Current Coverage:**

- **Municipalities:** 290/290 (100%) ✅
- **Providers:** ~200+ (varies by municipality)
  - Stockholm: 28 in JSON (out of 173 total from CSV)
  - Nacka: 15/15 (100%) ✅
- **Quality Metrics:** Available for providers in JSON files
- **Financial Data:** Available for providers with API access

**Priority for Expansion:**

1. Complete Stockholm provider list (173 total, 28 in JSON)
2. Top 20 largest municipalities
3. Municipalities with LOV systems

---

## Quick Reference

### Key Files

| File              | Purpose                  | Location                                                                                   |
| ----------------- | ------------------------ | ------------------------------------------------------------------------------------------ |
| **Prisma Schema** | Database structure       | `apps/stats-server/schema.prisma`                                                          |
| **JSON Data**     | Current provider lists   | `packages/shared/seo/data/` or `apps/stats-server/src/seed-scripts/seed-data/`             |
| **CSV Data**      | Historical/quality data  | `packages/shared/seo/data/kommun-data/` or `apps/stats-server/src/seed-scripts/seed-data/` |
| **Seed Scripts**  | Database seeding         | `apps/stats-server/src/seed-scripts/*.ts`                                                  |
| **API Clients**   | External API integration | `packages/shared/seo/data/api/`                                                            |

### Key Commands

```bash
# Database
yarn workspace stats-server db:generate
yarn workspace stats-server db:migrate
yarn workspace stats-server db:studio

# Seeding
yarn workspace stats-server db:seed                    # All seeds in order (01-25)
yarn workspace stats-server db:seed:01-national          # National statistics
yarn workspace stats-server db:seed:02-municipalities    # Municipalities & test providers
yarn workspace stats-server db:seed:03-providers-csv    # Primary CSV source (1,800+ providers)
yarn workspace stats-server db:seed:03.5-enrichment     # Provider enrichment
yarn workspace stats-server db:seed:04-survey           # Municipality aggregates
yarn workspace stats-server db:seed:05-provider-satisfaction # Satisfaction CSVs
yarn workspace stats-server db:seed:06-quality-summaries  # Aggregate quality
yarn workspace stats-server db:seed:07-hemtjanstindex     # Hemtjänstindex rankings
yarn workspace stats-server db:seed:08-rankings          # Calculate rankings
yarn workspace stats-server db:seed:12-kommun-api        # kommun API (optional)
yarn workspace stats-server db:seed:11-financials         # Financial APIs (optional)
```

### Data Source Priority

1. **infoval.se** - Source of truth for current provider lists
2. **kommun.jensnylander.com API** - Provider identification and invoicing
3. **Socialstyrelsen CSV** - Quality metrics and historical data
4. **tic.io API** - Financial data (premium)
5. **Allabolag** - Financial data (fallback)
6. **SCB** - Demographics and municipality finances (not implemented)

### Common Issues

**Issue:** Duplicate providers in database

- **Solution:** Seed scripts use deduplication (match by orgNumber or normalized name)

**Issue:** Missing region data

- **Solution:** Re-run `db:seed:02-municipalities` to update regions from JSON

**Issue:** Empty financial data

- **Solution:** Run `db:seed:11-financials` (requires API keys)

**Issue:** CSV has fewer providers than JSON

- **Explanation:** CSV is historical survey data, JSON is current from infoval.se

---

## Related Documentation

- **Prisma Schema:** `apps/stats-server/schema.prisma` - Complete database schema
- **TypeScript Types:** `packages/shared/seo/data/schema.ts` - Frontend types
- **GraphQL Schema:** `packages/graphql/schema/seo/types.graphql` - API types
- **Database Seeding:** [SEED_SYSTEM_GUIDE.md](./SEED_SYSTEM_GUIDE.md) - Complete seed system guide
- **Data Files:** `docs/DATA_FILES_ARCHIVAL_GUIDE.md` - What files can be archived

---

**Last Updated:** 2026-01-04  
**Maintained By:** Development Team  
**Questions?** See individual seed script READMEs or Prisma schema comments
