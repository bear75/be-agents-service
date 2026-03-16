# Seed Scripts Detailed Reference

> 📅 **Last Updated:** 2026-01-04  
> **Version:** 3.0  
> **Status:** Detailed Reference (Supplementary)

> 📖 **MAIN GUIDE:** See [SEED_SYSTEM_GUIDE.md](./SEED_SYSTEM_GUIDE.md) for complete seed system documentation.  
> 📖 **See also:** [COMPLETE_SEED_ARCHITECTURE.md](./COMPLETE_SEED_ARCHITECTURE.md) for the unified data pipeline overview.

**This document provides detailed reference for each individual seed script.** For system overview, architecture, and quick start, see [SEED_SYSTEM_GUIDE.md](./SEED_SYSTEM_GUIDE.md).

## Quick Start

**Seed all data sources:**

```bash
yarn workspace stats-server db:seed
```

**Quick reset from snapshot (fast - seconds):**

```bash
yarn workspace stats-server db:quick-reset
```

**Full reset (slow - runs all seeds):**

```bash
yarn workspace stats-server db:reset-all
```

This runs all seed scripts in the correct order (steps 01-19).

## Overview

The seeding process populates the SEO database with provider and municipality data from multiple sources. The scripts are designed to work with the merged schema where quality indicator fields are directly on `Provider` and `Municipality` tables (previously stored in separate staging tables).

### Data Source Priority

1. **CSV Files (Official)** - Primary source of truth from Socialstyrelsen
   - `2025-10-9834-resultat - Hemtjänst, enheter.csv` - 1,800+ providers with quality indicators
   - `2025-10-9834-resultat - Hemtjänst, kommun, län, rike.csv` - Municipality aggregates
   - `2025-10-9793-bilaga-hemtjanst-verksamheter-2025/` - 292 CSV files with satisfaction data

2. **JSON Files (Test/Manual)** - Optional enrichment data
   - `sverige_kommuner.json` - All 290 municipalities metadata
   - `stockholm.json`, `nacka.json` - Manual scrapes for testing

3. **API Sources (Optional)** - Enrichment data
   - `tic.io` / `allabolag.se` - Financial data
   - `kommun.jensnylander.com` - Provider invoicing data

## Seed Order

The main `seed.ts` orchestrator runs scripts in this specific order. All files are prefixed with their step number (e.g., `01-seed-national-statistics.ts`):

| Step | Script                              | Description                                                                         |
| ---- | ----------------------------------- | ----------------------------------------------------------------------------------- |
| 01   | `01-seed-national-statistics.ts`    | National-level statistics from JSON                                                 |
| 02   | `02-seed-municipalities.ts`         | Municipalities from JSON (metadata + test data)                                     |
| 03   | `03-seed-providers-unified.ts`      | **PRIMARY** - 1,800+ providers from Socialstyrelsen CSV (auto-generates orgNumbers) |
| 03.5 | `03.5-seed-providers-enrichment.ts` | Enrich with financial/registration data                                             |
| 04   | `04-seed-municipality-survey.ts`    | Municipality aggregated survey data                                                 |
| 05   | `05-seed-provider-satisfaction.ts`  | Satisfaction data from 292 CSV files                                                |
| 05.5 | `05.5-seed-quality-metrics.ts`      | Quality metrics from scraped JSON                                                   |
| 05.7 | `05.7-seed-municipality-scraped.ts` | Provider websites, contacts, sourceUrls from municipality pages                     |
| 06   | `06-seed-quality-summaries.ts`      | Aggregated quality summaries                                                        |
| 07   | `07-seed-hemtjanstindex.ts`         | Hemtjänstindex 2025 rankings                                                        |
| 08   | `08-calculate-rankings.ts`          | CaireIndex rankings (Provider & Municipality)                                       |
| 09   | `09-seed-skr-data.ts`               | SKR municipality groups                                                             |
| 10   | `10-seed-homecare-recipients.ts`    | Home care recipient counts                                                          |
| 10.5 | `10.5-seed-kolada-kpis.ts`          | Kolada KPI data (API)                                                               |
| 11   | `11-seed-financials.ts`             | ⚪ Optional (TIC_API_KEY)                                                           |
| 12   | `12-seed-kommun-api.ts`             | ⚪ Optional (KOMMUN_API_KEY)                                                        |
| 13   | `13-seed-branschrapport.ts`         | ⚪ Optional (stores for review)                                                     |
| 14   | `14-seed-scb-data.ts`               | ⚪ Optional (SCB API)                                                               |
| 15   | `15-seed-gamification.ts`           | Badge definitions and quests                                                        |
| 16   | `16-seed-data-sources.ts`           | Data source configurations                                                          |
| 17   | `17-seed-municipality-finances.ts`  | Municipality finances (all 290)                                                     |
| 18   | `18-seed-sync-provider-rows.ts`     | Sync provider & presence rows                                                       |
| 19   | `19-seed-sync-counts.ts`            | **MUST BE LAST** - Sync counts                                                      |
| 28   | `28-seed-jensnylander-urls.ts`      | Jens Nylander URLs + Financial Data (see section 20 below)                          |

Standalone scripts (not in seed.ts):

- `standalone-seed-pdf-statistics.ts` - Requires manual PDF extraction
- `standalone-seed-kolada-ous.ts` - Optional API enrichment
- `standalone-seed-scraped-data.ts` - Pilot municipalities only

## Prerequisites

### 1. Environment Variable

All seed scripts require the `DATABASE_URL` environment variable:

```bash
exportDATABASE_URL="postgresql://user:password@host:port/database?schema=public"
```

Or add it to your `.env` file.

### 2. Database Schema

Ensure your database schema is up to date:

```bash
# Generate Prisma client
yarn workspace @appcaire/prisma-seo generate

# Apply migrations
yarn workspace @appcaire/prisma-seo db:migrate
```

### 3. Optional API Keys

For optional seed scripts:

```bash
# Optional - for premium financial data
VITE_TIC_API_KEY=your_tic_api_key

# Optional - for kommun API
KOMMUN_API_KEY=your_kommun_api_key
# or
VITE_KOMMUN_API_KEY=your_kommun_api_key
```

## Running Seed Scripts

### Run All Seeds (Recommended)

```bash
# Seed all data sources (recommended)
yarn workspace server db:seed
```

### Reset and Seed Everything

```bash
# Reset database, run migrations, and seed all data
yarn workspace server db:reset-all
```

### Run Individual Seeds

```bash
# Individual seed scripts (if needed)
yarn workspace server db:seed:national
yarn workspace server db:seed:providers
yarn workspace server db:seed:providers-from-csv
yarn workspace server db:seed:providers-from-kommun-export
yarn workspace server db:seed:socialstyrelsen
yarn workspace server db:seed:provider-satisfaction
yarn workspace server db:seed:quality-summaries
yarn workspace server db:seed:financials
yarn workspace server db:seed:kommun
yarn workspace server db:seed:branschrapport
yarn workspace server db:seed:data-sources
yarn workspace server db:seed:hemtjanstindex
yarn workspace server db:seed:pdf-statistics
yarn workspace server db:seed:scb-tables
yarn workspace server scb:export-csv          # Export SCB tables to CSV
yarn workspace server scb:import-csv          # Import SCB tables from CSV
yarn workspace server db:seed:scb-municipality-data
yarn workspace server db:seed:municipality-finances
yarn workspace server db:seed:scraped
yarn workspace server scraper:sync-status
yarn workspace server db:seed:sync-provider-rows
yarn workspace server db:seed:sync-counts
```

**Note:** For `db:seed:pdf-statistics`, you must first run the extraction script:

```bash
# Step 1: Extract statistics from PDFs
yarn workspace server extract:pdf-statistics-enhanced

# Step 2: Seed extracted data to database
yarn workspace server db:seed:pdf-statistics
```

## Seed Scripts Reference

### Summary Table

| Script                                 | Command                                | Purpose                         | Data Source             | Tables Updated                                                                  | Status                                      |
| -------------------------------------- | -------------------------------------- | ------------------------------- | ----------------------- | ------------------------------------------------------------------------------- | ------------------------------------------- |
| `seed-national-statistics.ts`          | `db:seed:national`                     | National stats                  | JSON                    | `NationalStatistics`                                                            | ✅ Working                                  |
| `seed-providers.ts`                    | `db:seed:providers`                    | Municipalities & test providers | JSON                    | `Municipality`, `Provider`, `ProviderMunicipality`, `QualityMetric`, `District` | ✅ Working                                  |
| `seed-providers-unified.ts`            | `db:seed:03-providers-unified`         | **PRIMARY** provider data       | CSV (enheter) + mapping | `Provider`, `ProviderMunicipality`                                              | ✅ Working (auto-generates orgNumbers)      |
| `seed-providers-from-kommun-export.ts` | `db:seed:providers-from-kommun-export` | **NEW** - Enrich providers      | CSV (kommun_export)     | `Provider.scrapedMunicipalityData` (JSON)                                       | ✅ Working                                  |
| `seed-socialstyrelsen.ts`              | `db:seed:socialstyrelsen`              | Municipality aggregates         | CSV (kommun)            | `Municipality`                                                                  | ✅ Working                                  |
| `seed-provider-satisfaction.ts`        | `db:seed:provider-satisfaction`        | Provider satisfaction           | CSV (292 files)         | `QualityMetric`, `ProviderMunicipality`                                         | ✅ Working                                  |
| `seed-quality-metrics.ts`              | `db:seed:05.5-quality-metrics`         | Quality metrics from Infoval    | JSON (scraped)          | `QualityMetric`                                                                 | ✅ Working                                  |
| `seed-municipality-scraped.ts`         | `db:seed:05.7-municipality-scraped`    | Provider websites, contacts     | JSON (scraped)          | `Provider`, `ProviderMunicipality`                                              | ✅ Working                                  |
| `seed-quality-summaries.ts`            | `db:seed:quality-summaries`            | Aggregate summaries             | Aggregates from DB      | `MunicipalityQualitySummary`                                                    | ✅ Working                                  |
| `seed-hemtjanstindex.ts`               | `db:seed:hemtjanstindex`               | Hemtjänstindex rankings         | CSV                     | `Municipality`                                                                  | ✅ Working                                  |
| `seed-pdf-statistics.ts`               | `db:seed:pdf-statistics`               | PDF statistics                  | JSON (from extraction)  | `NationalStatistics`, `RegulatoryComplianceCosts`, `SalaryStatistics`           | ✅ Working                                  |
| `seed-financials.ts`                   | `db:seed:financials`                   | Financial data                  | APIs (tic.io/allabolag) | `ProviderFinancials`                                                            | ✅ Working                                  |
| `seed-kommun-api.ts`                   | `db:seed:kommun`                       | API provider data               | API                     | `Provider`, `ProviderFinancials`, `ProviderMunicipality`                        | ✅ Working                                  |
| `seed-branschrapport.ts`               | `db:seed:branschrapport`               | Financial data review           | CSV                     | `ProviderFinancials`, `UnmatchedImportRecord`                                   | ✅ Working                                  |
| `seed-data-sources.ts`                 | `db:seed:data-sources`                 | Data source configs             | Static data             | `DataSourceConfig`                                                              | ✅ Working                                  |
| `seed-scb-tables.ts`                   | `db:seed:scb-tables`                   | SCB tables config               | SCB API                 | `ScbTableConfig`                                                                | ✅ Working                                  |
| `seed-scb-municipality-data.ts`        | `db:seed:scb-municipality-data`        | SCB municipality data           | SCB API                 | `Municipality`, `MunicipalityFinance`                                           | ✅ Working                                  |
| `seed-municipality-finances.ts`        | `db:seed:municipality-finances`        | Municipality finances           | Creates placeholders    | `MunicipalityFinance`                                                           | ✅ Working                                  |
| `seed-scraped-data.ts`                 | `db:seed:scraped`                      | Scraped data                    | JSON tracking files     | `Municipality`, `Provider`                                                      | ✅ Working                                  |
| `seed-scraping-status.ts`              | `scraper:sync-status`                  | Scraping status sync            | JSON tracking files     | `ScrapingStatus`                                                                | ✅ Working                                  |
| `seed-sync-provider-rows.ts`           | `db:seed:sync-provider-rows`           | Sync 1:1 records                | Aggregates from DB      | `ProviderFinancials`, `QualityMetric`                                           | ✅ Working                                  |
| `seed-sync-counts.ts`                  | `db:seed:sync-counts`                  | Sync denormalized counts        | Aggregates from DB      | `Municipality`, `NationalStatistics`                                            | ✅ Working                                  |
| `seed-from-enheter.ts`                 | `db:seed:from-enheter`                 | ⚠️ **DEPRECATED**               | -                       | -                                                                               | ❌ Deprecated (use seed-providers-from-csv) |

---

### 1. `seed-national-statistics.ts`

**Purpose:** Seed national-level statistics

**Data Source:**

- `apps/stats-server/src/seed-scripts/seed-data/01-national-statistics/socialstyrelsen_methodology_stats_2025.json`
- Generated by: `extract-methodology-stats.ts` (outputs to `seed-data/01-national-statistics/`)

**Database Tables:**

- `NationalStatistics`

**What it stores:**

- `year`: Survey year (2025)
- `totalRecipients`: Total hemtjänst recipients
- `totalMunicipalities`: Fixed at 290
- `description`: Description of methodology
- `country`: "Sverige"
- `version`: "2025-Q1"

**Schema Compatibility:** ✅ Works with merged schema

---

### 2. `seed-providers.ts`

**Purpose:** Seed municipalities and test providers from JSON files

**Data Source:**

- `packages/shared/src/seo/data/providers/sverige_kommuner.json` (municipalities)
- `packages/shared/src/seo/data/providers/stockholm.json` (test providers)
- `packages/shared/src/seo/data/providers/nacka.json` (test providers)

**Database Tables:**

- `Municipality` - All 290 municipalities with metadata
- `Provider` - Test providers (Stockholm/Nacka only)
- `ProviderMunicipality` - Provider-municipality relationships
- `QualityMetric` - Quality data from JSON (if present)
- `District` - Geographic districts
- `CorporateGroup` - Groups providers by legalName/parentName

**What it stores:**

- Municipalities: name, region, municipalityCode, population, hasLov, etc.
- Providers: name, orgNumber, orgType, address, system info, certifications
- Presences: status, customerCount, geographicAreas, quality metrics

**Schema Compatibility:** ✅ Works with merged schema (certification fields directly on Provider)

**Note:** JSON files are test/manual data. Official data comes from CSV.

---

### 3. `seed-providers-unified.ts` ⭐ **PRIMARY SOURCE**

**Purpose:** Extract providers from official Socialstyrelsen CSV with automatic orgNumber generation

**Data Source:**

- `apps/stats-server/src/seed-scripts/seed-data/03-providers-csv/enheter.csv`
- ~1,800 provider records from Socialstyrelsen

**OrgNumber Mapping:**

- **Municipal providers:** Auto-generated as `MUN{code}-{hash}` (deterministic, unique per unit)
- **Private providers:**
  1. First tries to match from Kommun API CSV (`seed-data/03.5-providers-enrichment/leverantorer_filtered_88101_88102.csv`)
  2. Falls back to auto-generated `PRV{code}-{hash}` if not found
  3. Manual overrides can be added to `seed-data/00-provider-mapping/manual-orgnumber-overrides.json`

**✅ Automatic Coverage:** 100% of providers get orgNumbers automatically - no manual fixes required!

**Database Tables:**

- `Provider` - Provider records with quality indicators
- `ProviderMunicipality` - Provider presence in municipalities

**What it stores:**

**Provider fields:**

- Basic: `name`, `legalName`, `orgType`, `slug`, `orgNumber` (always set)
- Services: `insatserService`, `insatserPersonligOmvardnad`, `insatserHemsjukvard`
- Languages: `sprakFinska`, `sprakMeankieli`, `sprakSamiska`
- Quality indicators (30+ fields):
  - `ind2GenomforandeplanAndel` through `ind32UnderskoterskeHelgerAndel`
  - `ind8HarRutinKontakt`, `b11AntalPerKontakt`
  - Safety routines (ind11-ind17)
  - Cooperation routines (ind24-ind28)
  - Medication routines (ind29-ind31)
  - Staffing metrics (ind32, b9)
- Metadata: `surveyDataYear` (2025), `surveyDataUpdated`

**ProviderMunicipality:**

- `status`: 'ACTIVE'
- `activeSinceYear`: 2025
- `isApprovedInLov`: true
- `sourceUrl`: Reference to CSV

**Schema Compatibility:** ✅ **UPDATED** - Writes directly to Provider table (fields merged from old socialstyrelsensEnhet table)

**Critical:** This is the PRIMARY source for provider data (1,800+ providers from official survey). All providers automatically get orgNumbers - no manual intervention needed.

---

### 3.5. `seed-providers-from-kommun-export.ts` ⭐ **NEW - ENRICHMENT**

**Purpose:** Enriches providers with detailed financial and registration data from kommun.jensnylander.com

**Data Source:**

- `packages/shared/src/seo/data/jenskommun-scraper/leverantorer_filtered_88101_88102.csv`
- 1,212 providers with enriched details

**Database Tables:**

- `Provider` - Updates `scrapedMunicipalityData` JSON field

**What it stores:**

**Provider.scrapedMunicipalityData JSON:**

- **Registration:** `registered` (date), `bolagstyp`, `status`
- **Tax:** `f_skatt`, `moms`, `arbetsgivare` (boolean)
- **Financial:**
  - `fakt_2022_sek`, `fakt_2023_sek`, `fakt_2024_sek` (invoiced amounts)
  - `last_turnover_tsek`, `last_profit_margin_pct`, `last_employees`
  - `af_support_2023_sek`, `af_support_2024_sek` (AF support)
- **Business:**
  - `num_municipalities` (number of municipalities served)
  - `sni_codes` (SNI codes with labels)
  - `purpose` (company purpose/description)
- **JSON Data:**
  - `financial_summary` - Full financial history (annual reports)
  - `invoiced_per_municipality` - Invoicing per municipality (2022-2024)
  - `invoiced_per_period` - Monthly invoicing trends

**Matching Results:**

- ✅ Matched by OrgNumber: 94.6%
- ✅ Matched by Name: 5.0%
- ❌ Unmatched: 0.4% (created as new providers)

**GraphQL Exposure:**

- Available via `Provider.scrapedData` field
- Type: `ProviderScrapedData`

**Schema Compatibility:** ✅ Works with merged schema (stores in JSON field)

**Frequency:** After scraping kommun.jensnylander.com

---

### 4. `seed-socialstyrelsen.ts`

**Purpose:** Update municipalities with aggregated survey data

**Data Source:**

- `packages/shared/src/seo/data/kommun-data/2025-10-9834-resultat - Hemtjänst, kommun, län, rike.csv`

**Database Tables:**

- `Municipality` - Aggregated quality indicators at municipality level

**What it stores:**

- `andelOffentligRegi` - % in public operation
- `sprakFinskaAndel`, `sprakMeankieliAndel`, `sprakSamiskaAndel` - Language support %
- All quality indicator percentages (same as Provider but aggregated):
  - `ind2GenomforandeplanAndel` through `ind32UnderskoterskeHelgerAndel`
  - `b9BrukarePerPersonalDagar`, `b9BrukarePerPersonalHelger`
- `surveyDataYear`: 2025
- `surveyDataUpdated`: timestamp

**Schema Compatibility:** ✅ **UPDATED** - Writes directly to Municipality table (fields merged from old socialstyrelsensKommun table)

**Note:** Only processes kommun-level rows (skips rike, län, stadsdel, Offentlig/Enskild variants)

---

### 5. `seed-provider-satisfaction.ts` 📊 **292 CSV FILES**

**Purpose:** Import customer satisfaction data from per-municipality CSV files

**Data Source:**

- `packages/shared/src/seo/data/kommun-data/2025-10-9793-bilaga-hemtjanst-verksamheter-2025/`
- **292 CSV files** (one per municipality)
- Format: `2025-10-9793-bilaga-hemtjanst-verksamheter-2025_0114_upplands_v_sby.csv`
- Municipality code extracted from filename (e.g., "0114")

**Database Tables:**

- `QualityMetric` - Customer satisfaction scores
- `ProviderMunicipality` - Creates presence if missing

**What it stores:**

**QualityMetric:**

- `presenceId`: Links to ProviderMunicipality
- `year`: 2025
- `source`: `SOCIALSTYRELSEN_BRUKARUNDERSOKNING`
- `customerSatisfaction`: Percentage from F21 question
- `overallSatisfaction`: Same as customerSatisfaction (F21 is overall)
- `sourceRef`: Filename and response interval

**ProviderMunicipality (if missing):**

- Creates presence record for provider-municipality relationship
- `status`: 'ACTIVE'
- `sourceUrl`: Reference to CSV file

**Process:**

1. Reads all 292 CSV files from directory
2. Extracts municipality code from filename
3. Parses "Totalt" rows starting at row 13
4. Matches provider names to existing providers
5. Creates/updates QualityMetric records
6. Creates ProviderMunicipality if missing

**Schema Compatibility:** ✅ Works with merged schema

**Note:** Provider matching uses `findMatchingProvider()` which handles name variations

---

### 6. `seed-quality-summaries.ts`

**Purpose:** Aggregate quality metrics into municipality-level summaries

**Data Source:**

- Aggregates from existing `QualityMetric` records in database

**Database Tables:**

- `MunicipalityQualitySummary` - Aggregated summaries per year/source

**What it stores:**

- `municipalityId`: Links to Municipality
- `year`: Survey year
- `source`: Source type (e.g., SOCIALSTYRELSEN_BRUKARUNDERSOKNING)
- `avgCustomerSatisfaction`: Average across all providers
- `avgStaffContinuity`: Average staff continuity score
- `avgHemtjanstIndex`: Average hemtjänst index
- `publicAvgSatisfaction`: Average for public providers only
- `privateAvgSatisfaction`: Average for private providers only
- `sourceRef`: Aggregation metadata

**Process:**

1. Fetches all municipalities
2. Finds unique year/source combinations from QualityMetric
3. For each municipality + year + source:
   - Aggregates all QualityMetric records
   - Calculates averages (overall, public-only, private-only)
   - Creates/updates MunicipalityQualitySummary

**Dependencies:** Requires `seed-provider-satisfaction.ts` to run first

**Schema Compatibility:** ✅ Works with merged schema

---

### 5.7. `seed-municipality-scraped.ts` 📊 **MUNICIPALITY SCRAPED DATA**

**Purpose:** Import provider websites, contacts, and sourceUrls from scraped municipality pages

**Data Source:**

- JSON files from `seed-data/05.7-municipality-scraped/`
- Generated by: `scrape_hemtjanst_providers_all.py` (Python scraper)

**Database Tables:**

- `Provider` - Updates with website, phone, email, scrapedOwnWebsiteUrl, scrapedMunicipalityPageUrl
- `ProviderMunicipality` - Updates with sourceUrl, customerCountRange, geographicAreas

**What it stores:**

**Provider:**

- `website`: Provider's own website URL
- `phone`: Contact phone number
- `email`: Contact email address
- `scrapedOwnWebsiteUrl`: External website URL (from municipality page)
- `scrapedMunicipalityPageUrl`: Provider detail page URL on municipality site
- `orgType`: Organization type (if available from scraping)

**ProviderMunicipality:**

- `sourceUrl`: Municipality provider listing page URL (infoval.se, aldreguiden.se, or custom)
- `customerCountRange`: Customer count range (e.g., "51-100")
- `geographicAreas`: Array of geographic areas covered

**Process:**

1. Loads all providers for matching
2. Reads combined JSON file or individual municipality files
3. For each municipality:
   - Finds municipality by slug, code, or name
   - For each provider in scraped data:
     - Matches provider using `findMatchingProvider()` (by orgNumber or name)
     - Updates Provider with scraped contact info and URLs
     - Updates or creates ProviderMunicipality with sourceUrl and geographic data

**Auto-fallback:** If seed data is missing, script provides instructions to run the Python scraper

**Prerequisites:**

1. Python scraper must have run: `scrape_hemtjanst_providers_all.py`
2. JSON files must exist in `seed-data/05.7-municipality-scraped/`

**Data Flow:**

```
Python Scraper → Creates JSON files → Seed Script → Reads JSON → Saves to Database
```

**Usage:**

```bash
# Step 1: Run Python scraper to CREATE seed-data files (NOT database)
cd apps/stats-server/src/data-creators/scrapers/municipality-provider-scraper
python3 scrape_hemtjanst_providers_all.py \
  --input input/hemtjanst_kommuner_seed_sanitized.json \
  --output ../../seed-scripts/seed-data/05.7-municipality-scraped \
  --concurrency 8 \
  --delay 0.5 \
  --enrich-own-sites \
  --max-own-site-pages 2 \
  --write-per-municipality

# This creates:
# - seed-data/05.7-municipality-scraped/municipalities_combined.json
# - seed-data/05.7-municipality-scraped/municipalities/{kommunkod}_{slug}.json

# Step 2: Seed script READS JSON files and SAVES to database
yarn workspace stats-server db:seed:05.7-municipality-scraped
```

**Note:** The scraper creates files, not database records. The seed script reads these files and saves to the database. This allows you to recreate the database from seed-data files.

**Schema Compatibility:** ✅ Works with merged schema

---

### 7. `seed-financials.ts`

**Purpose:** Fetch financial data from APIs

**Data Source:**

- APIs: tic.io (premium) or allabolag.se (fallback)
- Requires API keys

**Database Tables:**

- `ProviderFinancials` - Financial data per year

**What it stores:**

- `providerId`: Links to Provider
- `year`: Financial year
- `source`: TIC or ALLABOLAG
- `revenueSek`: Revenue in SEK
- `employeeCount`: Number of employees
- `profitMarginPct`: Profit margin %
- `ticRiskLevel`: Risk level (if from TIC)
- `totalInvoicedSek`: Total invoiced to municipalities
- `invoicedMunicipalities`: Array of municipality names

**Schema Compatibility:** ✅ Works with merged schema

**Note:** Only processes providers with `orgNumber`

---

### 8. `seed-kommun-api.ts`

**Purpose:** Fetch provider data from kommun.jensnylander.com API

**Data Source:**

- API: `https://kommun.jensnylander.com`
- Requires `KOMMUN_API_KEY` or `VITE_KOMMUN_API_KEY`

**Database Tables:**

- `Provider` - Provider records
- `ProviderFinancials` - Invoicing data
- `ProviderMunicipality` - Provider presence in municipalities

**What it stores:**

**Provider:**

- `name`, `orgNumber`, `kommunApiId`
- Contact info: `address`, `postalCode`, `city`, `phone`

**ProviderFinancials:**

- `totalInvoicedSek`: Total invoiced amount
- `invoicedMunicipalities`: List of municipalities
- `source`: KOMMUN_API

**ProviderMunicipality:**

- Creates presence for each municipality in `invoicedMunicipalities`

**Schema Compatibility:** ✅ Works with merged schema

**Note:** Optional - requires API key

---

### 9. `seed-branschrapport.ts`

**Purpose:** Store financial data for manual review

**Data Source:**

- CSV: `Branschrapport_Nova Omsorg i Stockholm AB_5568594385_316787_sv_Hemtjänst_blad_1.csv`

**Database Tables:**

- `UnmatchedImportRecord` - Stores records for admin review

**What it stores:**

- `source`: 'BRANSCHRAPPORT'
- `filename`: CSV filename
- `orgNumber`: From CSV
- `companyName`: From CSV
- `rawData`: Full CSV record as JSON
- `status`: 'pending'
- `matchAttempts`: Array of matching attempts

**Schema Compatibility:** ✅ Works with merged schema

**Note:** Does NOT automatically match providers - stores for admin review in dashboard

---

### 10. `seed-data-sources.ts`

**Purpose:** Seed data source configurations

**Data Source:**

- Static configuration in script

**Database Tables:**

- `DataSourceConfig` - Data source metadata

**What it stores:**

- Configurations for: infoval.se, kommun-api, socialstyrelsen, SCB, tic-io, allabolag, aldreguiden

**Schema Compatibility:** ✅ Works with merged schema

---

### 11. `seed-hemtjanstindex.ts` 📊 **HEMTJÄSTINDEX**

**Purpose:** Import Hemtjänstindex 2025 quality rankings and scores

**Data Source:**

- CSV files from `docs/docs-seo/06-market-researh/hemtjanstindex/`:
  - `Index25_hela.csv` - Main index with all scores
  - `Index25_start.csv` - Rankings and year-over-year changes

**Database Tables:**

- `Municipality` - Updates with Hemtjänstindex scores

**What it stores:**

- `hemtjanstindexYear`: 2025
- `hemtjanstindexRank`: Overall rank (1-290)
- `hemtjanstindexScore`: Overall score
- `hemtjanstindexRankChange`: Change from previous year
- `hemtjanstindexMissingData`: Missing data indicator
- Sub-index scores (calculated from rankings): `hemtjanstindexInfo`, `hemtjanstindexBistand`, `hemtjanstindexUtforande`, `hemtjanstindexStod`

**Process:**

1. Parses CSV files with municipality rankings
2. Matches municipalities by normalized name (handles "kommun"/"stad" suffixes)
3. Updates Municipality records with index data

**Schema Compatibility:** ✅ Works with merged schema

---

### 12. `seed-pdf-statistics.ts` 📊 **PDF STATISTICS**

**Purpose:** Import extracted statistics from Socialstyrelsen PDF reports

**Data Source:**

- JSON file: `apps/stats-server/src/seed-scripts/seed-data/14.7-pdf-statistics/socialstyrelsen-statistics-extracted.json`
- Generated by: `extract-pdf-statistics-enhanced.ts` (outputs to `seed-data/14.7-pdf-statistics/`)

**Database Tables:**

- `NationalStatistics` - Updates with new fields (company size, recipients with private care, etc.)
- `RegulatoryComplianceCosts` - Cost data from Tabell 9, 10
- `SalaryStatistics` - Salary data from Tabell 6

**What it stores:**

**NationalStatistics (updates):**

- Company size distribution (micro, small, medium, large - absolute + percentages)
- `recipientsPrivateCare` - Antal patienter med privat vård
- `recipientsWithoutReportedCarePercentage` - Patienter utan inrapporterad vårdåtgärd
- `municipalitiesWithoutReportingObligation` - Kommuner utan uppgiftsskyldighet
- JSON fields: `companySizeTrends`, `privatizationPercentageByMunicipality`, etc.

**RegulatoryComplianceCosts:**

- Cost ranges for compliance activities (with/without KVÅ)
- Micro company costs (with/without KVÅ)
- Administrative time costs (initial, annual)
- Consultant usage statistics

**SalaryStatistics:**

- Monthly salaries (with/without benefits)
- Hourly salaries
- By profession (Arbetsterapeut, Fysioterapeut, Sjuksköterska, etc.)

**Prerequisites:**

1. Run extraction script first: `yarn workspace stats-server data:create-all` (runs extract-pdf-statistics-enhanced)
2. JSON file must exist at: `apps/stats-server/src/seed-scripts/seed-data/14.7-pdf-statistics/socialstyrelsen-statistics-extracted.json`

**Usage:**

```bash
# Step 1: Extract statistics from PDFs
yarn workspace server extract:pdf-statistics-enhanced

# Step 2: Seed extracted data
yarn workspace server db:seed:pdf-statistics
```

**Schema Compatibility:** ✅ Works with extended schema (new tables and fields)

**Note:** This script reads from JSON file generated by the extraction script. It does not parse PDFs directly.

---

### 13. `seed-scb-tables.ts` 📊 **SCB TABLES CONFIGURATION**

**Purpose:** Seed SCB table configurations from PxWeb API 2.0

**Data Source:**

- SCB PxWeb API 2.0: `https://api.scb.se`
- Imports 117 pre-selected important tables (from PxWeb 2.0 filter: BE, OE, AM, HE, LE, SO 2023-2026)

**Database Tables:**

- `ScbTableConfig` - Table metadata and configuration

**What it stores:**

- `tableId`: SCB table identifier
- `label`: Table name
- `description`: Table description
- `dataLevels`: Inferred levels (NATIONAL, LAN, KOMMUN)
- `dataTypes`: Inferred types (population, economy, elderly_care, etc.)
- `priority`: Priority (1 = high, 4 = low)
- `isEnabled`: Whether table is enabled by default
- `firstPeriod`, `lastPeriod`: Available time periods
- `variableNames`: List of variables in the table

**Process:**

1. Imports 117 pre-selected important tables (not all 5144+ tables)
2. Fetches metadata for each table with rate limiting (200ms delay, exponential backoff on 429)
3. Infers data levels, types, and priority from metadata
4. Creates/updates ScbTableConfig records

**Schema Compatibility:** ✅ Works with merged schema

**Note:**

- Only imports 117 pre-selected tables to avoid importing all 5144+ tables
- Other tables can be discovered and imported via admin UI using the API search endpoint
- Tables can then be imported via admin UI after configuration

**CSV Export/Import:**

- **Export to CSV:** `yarn workspace server scb:export-csv`
  - Exports all SCB table configurations to CSV
  - Saves to: `packages/shared/src/seo/data/kommun-data/scb-tables-config.csv`
  - Also creates summary JSON: `scb-tables-summary.json`
- **Import from CSV:** `yarn workspace server scb:import-csv [path/to/file.csv]`
  - Imports SCB table configurations from CSV
  - Default path: `packages/shared/src/seo/data/kommun-data/scb-tables-config.csv`
  - Useful for restoring seed data or importing custom table selections
- **API Export:** `GET /api/scb-tables/export-csv` (from admin UI)
  - Downloads CSV directly from browser

---

### 14. `seed-scb-municipality-data.ts` 📊 **SCB MUNICIPALITY DATA**

**Purpose:** Import municipality population and financial data from SCB

**Data Source:**

- SCB PxWeb API 2.0 (new API)
- Legacy SCB API (for population data)

**Database Tables:**

- `Municipality` - Updates with population and demographic data
- `MunicipalityFinance` - Financial data per municipality per year

**What it stores:**

**Municipality:**

- Population data (current year)
- Elderly population (65+)
- Demographics

**MunicipalityFinance:**

- Financial data per year
- Costs, revenues, expenditures
- Home care specific costs

**Process:**

1. Fetches population data using legacy API
2. Fetches financial data using PxWeb API 2.0
3. Updates Municipality and MunicipalityFinance tables

**Schema Compatibility:** ✅ Works with merged schema

**Note:** Optional - requires SCB API access

---

### 15. `seed-municipality-finances.ts` 💰 **MUNICIPALITY FINANCES (ALL 290)**

**Purpose:** Create MunicipalityFinance records for all 290 municipalities

**Data Source:**

- Creates placeholder records (no external data source)

**Database Tables:**

- `MunicipalityFinance` - Financial records per municipality per year

**What it stores:**

- Creates records for ALL 290 municipalities
- All financial fields default to NULL (placeholders)
- Ensures data consistency - all municipalities have finance records

**Process:**

1. Fetches all municipalities
2. Creates MunicipalityFinance record for each municipality (current year)
3. All fields are NULL (awaiting SCB data import)

**Schema Compatibility:** ✅ Works with merged schema

**Note:** This ensures "every object sums up" - all municipalities have finance records for consistency

---

### 16. `seed-scraped-data.ts` 🕷️ **SCRAPED DATA**

**Purpose:** Import verified scraped data from JSON tracking files

**Data Source:**

- JSON tracking files: `packages/shared/src/seo/data/scraping-status/pilot-municipalities.json`

**Database Tables:**

- `Municipality` - Updates with scraped URLs and metadata
- `Provider` - Updates with scraped URLs and data

**What it stores:**

**Municipality:**

- `scrapedHomePageUrl`: URL of municipality hemtjänst page
- `scrapedHomePageStatus`: Scraping status
- `scrapedHomePageHttpStatus`: HTTP status code
- `scrapedHomePageAt`: Last scraped timestamp
- `scrapingPhase`: Current scraping phase
- `scrapingNotes`: Notes about scraping
- `scrapedProviders`: Count of providers discovered

**Provider:**

- `scrapedMunicipalityPageUrl`: Provider page URL on municipality site
- `scrapedMunicipalityPageStatus`: Status
- `scrapedOwnWebsiteUrl`: Provider's own website URL
- `scrapedOwnWebsiteStatus`: Status
- `scrapedAt`: Last scraped timestamp
- `scrapedMunicipalityData`: Extracted data as JSON
- `scrapedOwnWebsiteData`: Extracted data as JSON

**Schema Compatibility:** ✅ Works with merged schema

**Note:** Optional - requires scraping to run first

---

### 17. `seed-scraping-status.ts` 📊 **SCRAPING STATUS SYNC**

**Purpose:** Sync scraping status from JSON tracking files to database

**Data Source:**

- JSON tracking files: `packages/shared/src/seo/data/scraping-status/pilot-municipalities.json`

**Database Tables:**

- `ScrapingStatus` - Scraping status for municipalities and providers

**What it stores:**

- Entity type (municipality or provider)
- Entity ID and name
- Scraping phase and status
- URLs, HTTP status codes, timestamps
- Data extraction status and fields
- Notes and metadata

**Process:**

1. Reads JSON tracking file
2. Syncs status for each municipality
3. Syncs status for each provider
4. Updates ScrapingStatus records

**Schema Compatibility:** ✅ Works with merged schema

**Note:** Optional - for admin dashboard visibility

---

### 18. `seed-sync-provider-rows.ts` 🔄 **SYNC PROVIDER ROWS (1:1)**

**Purpose:** Ensure every Provider has ProviderFinancials and every Presence has QualityMetric

**Data Source:**

- Aggregates from existing database records

**Database Tables:**

- `ProviderFinancials` - Creates placeholder records if missing
- `QualityMetric` - Creates placeholder records if missing

**What it stores:**

- Creates placeholder ProviderFinancials for providers without financial data
- Creates placeholder QualityMetric for presences without quality data
- All fields default to NULL (placeholders)

**Process:**

1. Fetches all providers
2. Checks if each has ProviderFinancials record
3. Creates placeholder if missing
4. Fetches all presences
5. Checks if each has QualityMetric record
6. Creates placeholder if missing

**Schema Compatibility:** ✅ Works with merged schema

**Note:** This ensures "every object sums up" - avoids data gaps in dashboards

---

### 19. `seed-sync-counts.ts` 🔄 **SYNC COUNTS (MUST BE LAST)**

**Purpose:** Sync denormalized counts on Municipality and NationalStatistics

**Data Source:**

- Aggregates from existing database records

**Database Tables:**

- `Municipality` - Updates provider counts
- `NationalStatistics` - Updates national totals

**What it stores:**

**Municipality:**

- `scrapedProviders`: Total provider count in municipality
- `publicProviders`: Count of public (MUNICIPAL) providers
- `privateProviders`: Count of private (PRIVATE) providers

**NationalStatistics:**

- `totalProviders`: Total unique providers
- `publicProviders`: Total public providers
- `privateProviders`: Total private providers
- `totalRecipients`: Sum of municipality recipients (or existing value, whichever is larger)

**Process:**

1. For each municipality: Counts providers from ProviderMunicipality
2. Separates public vs private counts
3. Updates Municipality records
4. Counts national totals
5. Updates NationalStatistics record

**Schema Compatibility:** ✅ Works with merged schema

**Note:** **MUST RUN LAST** - Depends on all other seed scripts completing first

---

### 20. `seed-jensnylander-urls.ts` 🔗 **JENS NYLANDER URL & DATA MANAGEMENT**

**Purpose:** Auto-populate Jens Nylander URLs and import financial/invoice data following proper data architecture

**Data Source:**

- **Seed-data files** (created by Python scrapers):
  - `seed-data/03.5-providers-enrichment/leverantorer_filtered_88101_88102.csv`
  - `seed-data/03.5-providers-enrichment/provider_details_{id}.json`
  - `seed-data/03.5-providers-enrichment/provider_financials.json`

**Data Architecture: Scraper → Seed Data Files → Seed Script → Database**

```
1. SCRAPE (Python Scrapers - Run First)
   ├── jens-filtered-sni.py → Creates CSV with providers
   ├── jens-provider-details-sni.py → Creates JSON with details
   └── jens-api-sni-filtered-amounts.py → Creates JSON with financials

   📂 Output: seed-data/03.5-providers-enrichment/
   ⚠️  Scrapers create FILES, NOT database records

2. SEED (This Script - Reads Files)
   └── 28-seed-jensnylander-urls.ts
       ├── Step 1: Read CSV and populate jensnylanderSlug, jensnylanderId
       ├── Step 2: Read JSON files for additional data
       └── Step 3: Store everything in database

   ✅ Auto-fallback: If seed-data is empty, shows instructions to run scrapers

3. ADMIN UPDATE (Future Enhancement)
   └── Admin UI button to re-run scrapers → Update seed-data → Re-run seed script
```

**Database Tables:**

- `Municipality` - Updates with `jensnylanderSlug`
- `Provider` - Updates with `jensnylanderSlug`, `jensnylanderId`
- `ProviderFinancials` - Financial data from Jens Nylander API
- `ProviderMunicipality` - Provider presences per municipality

**What it stores:**

**Municipality:**

- `jensnylanderSlug`: URL-friendly slug (usually same as municipality slug)
- `externalIdsVerified`: false (requires manual verification)
- `population`, `elderlyPopulation`, `hasLov` (from API if available)

**Provider:**

- `jensnylanderSlug`: URL-friendly slug generated from provider name
- `jensnylanderId`: Jens Nylander API identifier
- `externalIdsVerified`: false (requires manual verification)

**ProviderFinancials:**

- `source`: `JENS_KOMMUN_API`
- `totalInvoicedSek`: Total invoiced amount
- `invoicedMunicipalities`: Array of municipality names
- `sourceRef`: API URL reference

**Process:**

1. **Step 1 - Populate URLs from CSV:**
   - Reads `leverantorer_filtered_88101_88102.csv`
   - Matches providers by `orgNumber`
   - Generates `jensnylanderSlug` from provider name
   - Stores `jensnylanderId` from API
   - Municipalities auto-populate slug from their existing slug

2. **Step 2 - Read Additional Data from JSON:**
   - Reads JSON files created by `jens-provider-details-sni.py`
   - Reads financial JSON from `jens-api-sni-filtered-amounts.py`

3. **Step 3 - Store in Database:**
   - Saves all URLs to `Municipality` and `Provider` tables
   - Creates `ProviderFinancials` records with `JENS_KOMMUN_API` source
   - Creates/updates `ProviderMunicipality` presences
   - Fetches invoice data for municipalities and providers

**Prerequisites:**

1. **Python scrapers must have run first:**

   ```bash
   cd apps/stats-server/src/data-creators/scrapers/kommun_export
   python3 jens-filtered-sni.py
   python3 jens-provider-details-sni.py
   python3 jens-api-sni-filtered-amounts.py
   ```

2. **Environment variable (optional for step 3):**
   ```bash
   KOMMUN_API_KEY=your_api_key  # Optional but recommended
   ```

**Usage:**

```bash
# Full process:
# 1. Run Python scrapers (creates seed-data files)
cd apps/stats-server/src/data-creators/scrapers/kommun_export
python3 jens-filtered-sni.py

# 2. Run seed script (reads files, writes to DB)
yarn workspace stats-server db:seed:28-jensnylander

# 3. Verify in admin UI
open http://localhost:3001/admin/scout?tab=kallor
```

**Auto-fallback:**

If `seed-data/03.5-providers-enrichment/` is empty or missing, the script will:

1. Show instructions to run the Python scrapers
2. Provide exact commands to execute
3. Exit with helpful error message

**Schema Compatibility:** ✅ Works with merged schema

**Note:** This script follows the proper data architecture: scrapers create files first, then seed script reads those files and populates the database. This allows reproducing the database from seed-data files.

---

## Schema Compatibility

✅ **All scripts work with merged schema:**

- Old `socialstyrelsensEnhet` → Fields merged into `Provider`
- Old `socialstyrelsensKommun` → Fields merged into `Municipality`
- Old `provider_certifications` → Fields merged into `Provider`
- Scripts updated to write directly to merged tables

## What Gets Seeded

### Municipalities

- Basic information (name, slug, region, codes)
- Demographics (population, elderly population)
- LOV information
- Aggregated quality indicators from survey data
- URLs and metadata

### Providers

- Basic information (name, legal name, org number)
- Contact details (address, phone, email, website)
- System information (type, apps, certifications)
- Languages and special competencies
- Quality indicators (30+ fields from survey)
- Contacts (stored as JSON array)

### Provider-Municipality Presences

- Active status and approval information
- Customer counts and geographic areas
- Quality metrics (customer satisfaction, staff continuity, hemtjänst index)
- Source URLs

### Quality Metrics

- Customer satisfaction scores
- Staff continuity metrics
- Hemtjänst index
- Per provider-municipality-year-source

### Districts

- District names and slugs for municipalities (e.g., Stockholm's districts)

## Deduplication & Matching

The seed scripts use intelligent provider matching to prevent duplicates:

**Matching Strategies (in order):**

1. **Match by orgNumber** (most reliable)
2. **Match by normalized name** (handles "AB" suffix variations)
3. **Match by normalized legalName** against name or legalName
4. **Reverse match** (search name matches provider's legalName)

**Implementation:**

- Shared utility: `apps/server/src/utils/provider-matching.ts`
- Used by: `seed-providers.ts`, `seed-providers-from-csv.ts`, `seed-provider-satisfaction.ts`

**Expected Result:**

- 1,800+ providers from CSV (primary source)
- JSON providers matched/deduplicated (no duplicates)
- Quality metrics linked correctly

## Verification

### Check Data Counts

After seeding, verify the data:

```bash
# Open Prisma Studio
yarn workspace @appcaire/prisma-seo db:studio
```

Or use SQL:

```sql
-- Check municipality count
SELECT COUNT(*) FROM municipalities;

-- Check provider count (should be ~1,800+)
SELECT COUNT(*) FROM providers;

-- Check presence count
SELECT COUNT(*) FROM provider_municipality_presences;

-- Check quality metrics
SELECT COUNT(*) FROM quality_metrics;

-- Check quality summaries
SELECT COUNT(*) FROM municipality_quality_summaries;
```

### Expected Counts

After running all seeds:

- **Municipalities**: ~290 (all Swedish municipalities)
- **Providers**: ~1,800+ (from official CSV)
- **Presences**: Multiple per provider if active in multiple municipalities
- **Quality Metrics**: Data from satisfaction CSVs (292 files)
- **Quality Summaries**: Aggregated summaries after step 6 runs

## Troubleshooting

### Missing Environment Variable

If you get an error about `DATABASE_URL`:

```bash
exportDATABASE_URL="your-connection-string"
```

### File Not Found

Ensure the data files exist in:

- `packages/shared/src/seo/data/kommun-data/`
- `packages/shared/src/seo/data/providers/`

### Database Connection Issues

Verify your database is running and the connection string is correct:

```bash
# Test connection with Prisma Studio
yarn workspace @appcaire/prisma-seo db:studio
```

### API Key Issues

Optional seed scripts (financials, kommun API) will skip gracefully if API keys are not configured.

### Foreign Key Constraint Failed

Ensure you run seeds in the correct order (see "Seed Order" section above).

### Duplicate Providers

The matching utility handles most cases. If you see duplicates:

1. Check if providers have different orgNumbers
2. Verify name normalization is working
3. Review the matching logic in `provider-matching.ts`

## Data Structure

The seed scripts use upsert operations, so you can safely run them multiple times. They will:

- Create new records if they don't exist
- Update existing records with new data
- Match and deduplicate providers intelligently

## Related Documentation

- [DATA_STRUCTURE_GUIDE.md](./DATA_STRUCTURE_GUIDE.md) - Complete data structure
- [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) - Database migration guide
- [DATA_MANAGEMENT_GUIDE.md](./DATA_MANAGEMENT_GUIDE.md) - Data management best practices
- [RUNTIME_API_USAGE.md](./RUNTIME_API_USAGE.md) - API usage and data update strategy
- [MISSING_DATA_IMPLEMENTATION.md](./MISSING_DATA_IMPLEMENTATION.md) - Missing data implementation guide

---

**Last Updated:** 2025-12-28  
**Maintained By:** Development Team
