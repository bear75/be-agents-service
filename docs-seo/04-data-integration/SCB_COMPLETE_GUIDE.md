# SCB (Statistiska Centralbyrån) - Complete Guide

> **Last Updated:** 2026-01-04
> **Version:** 1.0  
> **Status:** Production Ready

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Data Levels](#data-levels)
4. [API Usage](#api-usage)
5. [CSV Import](#csv-import)
6. [Seed Scripts](#seed-scripts)
7. [Tables Reference](#tables-reference)
8. [Troubleshooting](#troubleshooting)

---

## Overview

SCB (Statistiska Centralbyrån) provides Sweden's official statistics. This guide covers:

- **PxWeb API 2.0** - REST API for accessing statistics
- **CSV Import** - Fallback when API fails
- **Seed Scripts** - Automated data import
- **117 Pre-selected Tables** - Population, economy, elderly care

### Key Tables for Hemtjänst

| Table       | Description                                 | Period    | Usage                              |
| ----------- | ------------------------------------------- | --------- | ---------------------------------- |
| **TAB4980** | Kostnader för kommunernas omsorg om äldre   | 2014-2024 | Hemtjänstkostnader per kommun      |
| **TAB3529** | Resultaträkning för kommuner                | 1998-2024 | Total kommunbudget, skatteintäkter |
| **TAB1267** | Folkmängden efter region, ålder och kön     | 2002-2024 | Befolkning 65+ per kommun          |
| **TAB638**  | Folkmängden efter region, civilstånd, ålder | 1968-2024 | Total befolkning per kommun        |

---

## Quick Start

### 1. Explore Tables

```bash
# Search for tables
yarn workspace server scb:explore "folkmängd kommun ålder"
yarn workspace server scb:explore "kommun ekonomi kostnader"
yarn workspace server scb:explore "hemtjänst kommun"

# Filter by subject codes and year
yarn workspace server scb:explore -s BE,OE,SO --from 2023 --to 2026
```

### 2. Inspect a Table

```bash
# See table structure
yarn workspace server scb:explore "" "TAB4980"
yarn workspace server scb:explore "" "TAB3529"
yarn workspace server scb:explore "" "TAB1267"
```

### 3. Seed Data

```bash
# Seed SCB table configurations (117 tables)
yarn workspace server db:seed:scb-tables

# Seed municipality data from SCB
yarn workspace server db:seed:scb-municipality-data

# Export tables to CSV
yarn workspace server scb:export-csv

# Import tables from CSV
yarn workspace server scb:import-csv
```

### Subject Codes

| Code | Description                             |
| ---- | --------------------------------------- |
| `BE` | Befolkning (Population)                 |
| `OE` | Offentlig ekonomi (Public Economy)      |
| `AM` | Arbetsmarknad (Labor Market)            |
| `HE` | Hushållens ekonomi (Household Economy)  |
| `LE` | Levnadsförhållanden (Living Conditions) |
| `SO` | Socialtjänst (Social Services)          |

---

## Data Levels

### 1. Rike (National Level)

Aggregated data for all of Sweden.

**Sources:**

- SCB: National population statistics, economic aggregations
- Socialstyrelsen: National quality indicators

**Example Data:**

- Total population 65+
- Total cost for elderly care
- Average quality indicators
- National trends

### 2. Region/Län Level

Data aggregated per county (21 län in Sweden).

**Sources:**

- SCB: Population data, economic data per county
- Socialstyrelsen: Regional aggregations

### 3. Kommun Level (Most Important)

Data per municipality (290 kommuner).

**Sources:**

- **TAB4980**: Kostnader och intäkter för kommunernas omsorg om äldre
- **TAB3529**: Resultaträkning för kommuner
- **TAB4202**: Verksamhetskostnader för kommuner
- Population data per kommun

**Example Data:**

- Hemtjänstkostnader per kommun
- Antal hemtjänstbrukare per kommun
- Kommunal befolkning 65+
- Kommunala kvalitetsindikatorer

### 4. anordnare (Provider Level)

Data per hemtjänst provider (from Socialstyrelsen, not SCB).

### Data Mapping

| Data Type            | Rike        | Region      | Kommun      | anordnare   |
| -------------------- | ----------- | ----------- | ----------- | ----------- |
| Befolkning 65+       | ✅ SCB      | ✅ SCB      | ✅ SCB      | ❌          |
| Hemtjänstkostnader   | ✅ TAB4980  | ✅ TAB4980  | ✅ TAB4980  | ❌          |
| Kommunal ekonomi     | ✅ TAB3529  | ✅ TAB3529  | ✅ TAB3529  | ❌          |
| Kvalitetsindikatorer | ✅ Soc.styr | ✅ Soc.styr | ✅ Soc.styr | ✅ Soc.styr |

---

## API Usage

### PxWeb API 2.0

**Documentation:** https://www.scb.se/vara-tjanster/oppna-data/pxwebapi/pxwebapi-2.0

**Endpoints:**

```
# Metadata
GET https://statistikdatabasen.scb.se/api/v2/tables/{tableId}?lang=sv

# Data
POST https://statistikdatabasen.scb.se/api/v2/tables/{tableId}/data?lang=sv
```

**Rate Limits:**

- Max 30 requests per 10 seconds per IP
- Max 150,000 data cells per request

### Implementation

**Files:**

- `apps/stats-server/src/services/data-import/ScbApiService.ts` - API client
- `apps/stats-server/src/services/data-import/ScbMunicipalityDataService.ts` - Data parsing

**API Endpoints in Server:**

```
GET /api/scb-tables - List configured tables
GET /api/scb-tables/search - Search tables
GET /api/scb-tables/:tableId/metadata - Get table metadata
POST /api/scb-tables - Add/update table
PATCH /api/scb-tables/:tableId - Update table
DELETE /api/scb-tables/:tableId - Remove table
POST /api/scb-tables/:tableId/import - Import data
```

---

## CSV Import

### When to Use CSV

- API failures or timeouts
- Offline analysis
- Historical data backup
- API rate limiting issues

### CSV Files Location

```
docs/docs-seo/06-market-researh/scb/
├── TAB4980_sv 2.csv - Hemtjänstkostnader
├── TAB3529_sv.csv - Kommunbudget
└── ...
```

### Encoding

CSV files from SCB are in ISO-8859-1 (Latin-1). The import script converts automatically to UTF-8.

### Import Command

```bash
# Import from CSV (fallback)
yarn workspace server db:seed:scb-csv
```

### Current Status

- ✅ Budget data: 289/289 kommuner (100%)
- ✅ Hemtjänstkostnader: 289/289 kommuner (100%)

---

## Seed Scripts

### seed-scb-tables.ts

**Purpose:** Seed SCB table configurations from PxWeb API 2.0

**Command:**

```bash
yarn workspace server db:seed:scb-tables
```

**What it does:**

1. Imports 117 pre-selected important tables
2. Fetches metadata for each table with rate limiting
3. Infers data levels, types, and priority from metadata
4. Creates/updates `ScbTableConfig` records

**Database Table:** `scb_table_configs`

### seed-scb-municipality-data.ts

**Purpose:** Import municipality population and financial data

**Command:**

```bash
yarn workspace server db:seed:scb-municipality-data
```

**What it stores:**

**Municipality:**

- Population data (current year)
- Elderly population (65+)
- Demographics

**MunicipalityFinance:**

- `totalExpenditureSek` - Total budget
- `taxRevenueSek` - Tax revenue
- `homeCareElderlySek` - Home care for elderly
- `homeCareDisabilitySek` - Home care for disability
- `homeCareTotalSek` - Total home care (calculated)
- `homeCareShareOfEconomyPct` - % of budget (calculated)
- `costTrend` - Trend (calculated)

### Seed Strategy

1. **Try API first** - Uses `ScbMunicipalityDataService.importAll()`
2. **Fallback to CSV** - If API fails or returns <100 records

### CSV Export/Import

```bash
# Export all SCB tables to CSV
yarn workspace server scb:export-csv

# Import from CSV
yarn workspace server scb:import-csv [path/to/file.csv]
```

**Output locations:**

- `packages/shared/src/seo/data/kommun-data/scb-tables-config.csv`
- `packages/shared/src/seo/data/kommun-data/scb-tables-summary.json`

---

## Tables Reference

### Priority 1: Critical Tables

| Table ID | Name                          | Period    | Data                                |
| -------- | ----------------------------- | --------- | ----------------------------------- |
| TAB4980  | Kostnader för omsorg om äldre | 2014-2024 | Hemtjänstkostnader, särskilt boende |
| TAB3529  | Resultaträkning för kommuner  | 1998-2024 | Total budget, skatteintäkter        |
| TAB1267  | Folkmängden 1 november        | 2002-2024 | Befolkning per ålder/kommun         |

### Priority 2: Important Tables

| Table ID | Name                          | Period    | Data                  |
| -------- | ----------------------------- | --------- | --------------------- |
| TAB638   | Folkmängden region/civilstånd | 1968-2024 | Total befolkning      |
| TAB4202  | Verksamhetskostnader          | 2011-2024 | Detaljerade kostnader |
| TAB2017  | Kommunala skattesatser        | 2000-2026 | Skatter               |

### Priority 3: Population Forecasts

117 tables total including population forecasts from 2006-2023. See full list in `seed-scb-tables.ts`.

### Viewing Seeded Tables

```sql
-- Count tables
SELECT COUNT(*) FROM "scb_table_configs";
-- Expected: 117

-- See examples
SELECT "tableId", "label", "isEnabled", "priority"
FROM "scb_table_configs"
ORDER BY "priority", "label"
LIMIT 10;
```

---

## Troubleshooting

### API Timeout

**Problem:** SCB API returns timeout or 429 (rate limit)

**Solution:**

1. Increase delay between requests (currently 200ms)
2. Use CSV fallback: `yarn workspace server db:seed:scb-csv`
3. Try again later

### Missing Municipality Data

**Problem:** Only 2 kommuner have elderly population

**Solution:**

1. Check if TAB1267 is being parsed correctly
2. Verify CSV files contain data
3. Run: `yarn workspace server db:seed:scb-municipality-data`

### CSV Encoding Issues

**Problem:** Special characters (ö, ä, å) display incorrectly

**Solution:** CSV files are Latin-1 encoded. The import script handles conversion automatically.

### No Data After Seed

**Problem:** Tables show 0 records

**Solution:**

1. Check database connection: `echo $DATABASE_URL`
2. Verify migrations: `yarn workspace @appcaire/prisma-seo db:migrate`
3. Check logs for errors during seed

---

## Related Documentation

- [SEED_SYSTEM_GUIDE.md](./SEED_SYSTEM_GUIDE.md) - Complete seed system guide
- [DATA_STRUCTURE_GUIDE.md](./DATA_STRUCTURE_GUIDE.md) - Database schema
- [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) - Prisma migrations

---

**Last Updated:** 2025-12-30  
**Maintained By:** Development Team
