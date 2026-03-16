# Complete Seed Architecture

> 📅 **Last Updated:** 2026-01-04  
> **Version:** 3.0  
> **Status:** Production Ready

## Overview

The Complete Seed Architecture consolidates ALL data creation, seeding, and verification into a unified system. This replaces the previous fragmented approach with scattered scripts across `scripts/` and `scrapers/` directories.

### Key Features

- **17 data creation scripts** organized into scrapers, extractors, and processors
- **Standardized output** to `seed-data/` directory
- **Auto-fallback** - seed scripts automatically run data creators if data is missing
- **Verification system** - confirms all data is correctly stored in database
- **Single command** - `yarn db:seed:fresh` for complete pipeline

---

## Quick Start

```bash
# Full pipeline: create data → seed → verify
yarn workspace stats-server db:seed:fresh

# Or run individual steps:
yarn workspace stats-server data:create-all    # Create all seed data
yarn workspace stats-server db:seed            # Seed database (auto-generates orgNumbers)
yarn workspace stats-server db:seed:verify     # Verify data
```

**✅ Automatic orgNumber Generation:** The seed process automatically generates orgNumbers for all providers:

- **Municipal providers:** `MUN{code}-{hash}` format
- **Private providers:** Matched from Kommun API, or auto-generated `PRV{code}-{hash}` as fallback
- **100% Coverage:** No manual fixes required - all providers get orgNumbers automatically

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL DATA SOURCES                        │
├─────────────────────────────────────────────────────────────────┤
│ • Infoval API          • SCB API           • Kolada API         │
│ • kommun.jensnylander  • Stockholm API     • Municipality webs  │
│ • Provider websites    • PDFs              • Excel files        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              DATA CREATORS (17 scripts)                         │
├─────────────────────────────────────────────────────────────────┤
│ 📡 TypeScript Scrapers (6)   │ 🐍 Python Scrapers (3)           │
│ • municipality-scraper       │ • jens-filtered-sni.py           │
│ • provider-detail-scraper    │ • jens-provider-details-sni.py   │
│ • provider-website-scraper   │ • jens-api-sni-filtered-amounts  │
│ • scb-scraper                │                                  │
│ • kolada-scraper             │                                  │
│ • url-discovery-from-json    │                                  │
├──────────────────────────────┼──────────────────────────────────┤
│ 📄 PDF Extractors (6)        │ ⚙️ Processors (2)                │
│ • extract-hemtjanstindex     │ • process-stockholm-api          │
│ • extract-methodology-stats  │ • convert-excel-to-csv           │
│ • extract-nova-omsorg        │                                  │
│ • extract-pdf-data           │                                  │
│ • extract-pdf-statistics     │                                  │
│ • extract-pdf-enhanced       │                                  │
└────────────────────────────┬─┴──────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SEED DATA DIRECTORY                         │
│              apps/stats-server/src/seed-scripts/seed-data/      │
├─────────────────────────────────────────────────────────────────┤
│ 01-national-statistics/    │ 10-homecare-recipients/           │
│ 02-municipalities/         │ 10.5-kolada/                      │
│ 03-providers-csv/          │ 13-branschrapport/                │
│ 03.5-providers-enrichment/ │ 14-scb/                           │
│ 04-municipality-survey/    │ 14.7-pdf-statistics/              │
│ 05-provider-satisfaction/  │ 15-gamification/                  │
│ 05.5-infoval-quality/      │                                   │
│ 05.6-provider-websites/    │                                   │
│ 07-hemtjanstindex/         │                                   │
│ 09-skr-data/               │                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              SEED SCRIPTS (with auto-fallback)                  │
├─────────────────────────────────────────────────────────────────┤
│ 01-seed-national-statistics   │ 09-seed-skr-data               │
│ 02-seed-municipalities        │ 10-seed-homecare-recipients    │
│ 03-seed-providers-csv         │ 10.5-seed-kolada-kpis          │
│ 03.5-seed-providers-enrichment│ 14-seed-scb-data               │
│ 04-seed-municipality-survey   │ 15-seed-gamification           │
│ 05-seed-provider-satisfaction │ 16-seed-data-sources           │
│ 05.5-seed-quality-metrics     │ 17-seed-municipality-finances  │
│ 07-seed-hemtjanstindex        │ 18-seed-sync-provider-rows     │
│ 08-calculate-rankings         │ 19-seed-sync-counts            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATABASE                                  │
├─────────────────────────────────────────────────────────────────┤
│ 📊 Core Tables              │ 📈 Analytics Tables              │
│ • Municipality (290)        │ • ProviderRanking                │
│ • Provider (2192+)          │ • MunicipalityRanking            │
│ • ProviderMunicipality      │ • MunicipalityQualitySummary     │
│ • QualityMetric             │ • NationalStatistics             │
│ • ProviderFinancials        │ • MunicipalityFinance            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VERIFICATION SCRIPT                           │
│                  verify-seed-data.ts                             │
├─────────────────────────────────────────────────────────────────┤
│ ✅ Checks all table counts   │ ✅ Validates relationships       │
│ ✅ Reports warnings/failures │ ✅ Detailed data quality checks  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
apps/stats-server/src/
├── data-creators/                    # 17 data creation scripts
│   ├── index.ts                      # Master orchestrator
│   ├── scrapers/
│   │   ├── index.ts                  # Scraper exports
│   │   ├── municipality-scraper.ts   # Municipality websites → JSON
│   │   ├── provider-detail-scraper.ts# Infoval API → JSON
│   │   ├── provider-website-scraper.ts# Provider websites → JSON
│   │   ├── scb-scraper.ts            # SCB API → JSON
│   │   ├── kolada-scraper.ts         # Kolada API → JSON
│   │   ├── url-discovery-from-json.ts# URL discovery
│   │   ├── types.ts                  # Shared types
│   │   ├── pilot-config-utils.ts     # Config utilities
│   │   ├── kommun_export/            # Python scrapers
│   │   │   ├── jens-filtered-sni.py
│   │   │   ├── jens-provider-details-sni.py
│   │   │   └── jens-api-sni-filtered-amounts.py
│   │   └── municipality-provider-scraper/  # Python scraper for all 290 municipalities
│   │       ├── input/                # INPUT files (kommundata)
│   │       │   └── hemtjanst_kommuner_seed_sanitized.json
│   │       ├── scrape_hemtjanst_providers_all.py
│   │       └── README_hemtjanst_scraper.md
│   ├── extractors/
│   │   ├── index.ts                  # Extractor exports
│   │   ├── extract-hemtjanstindex.ts # PDFs → JSON
│   │   ├── extract-methodology-stats.ts
│   │   ├── extract-nova-omsorg.ts
│   │   ├── extract-pdf-data.ts
│   │   ├── extract-pdf-statistics.ts
│   │   └── extract-pdf-statistics-enhanced.ts
│   └── processors/
│       ├── index.ts                  # Processor exports
│       ├── process-stockholm-api.ts  # API → JSON
│       └── convert-excel-to-csv.ts   # Excel → CSV
│
├── seed-scripts/
│   ├── seed-data/                    # All seed data files
│   │   ├── 01-national-statistics/   # National-level stats
│   │   ├── 02-municipalities/        # Municipality data
│   │   │   ├── scraped/              # From municipality-scraper
│   │   │   └── stockholm.json        # From Stockholm API
│   │   ├── 03-providers-csv/         # Socialstyrelsen enheter.csv
│   │   ├── 03.5-providers-enrichment/# From Jens scrapers
│   │   ├── 04-municipality-survey/   # Survey aggregates
│   │   ├── 05-provider-satisfaction/ # 292 CSV files
│   │   ├── 05.5-infoval-quality/     # From provider-detail-scraper
│   │   ├── 05.6-provider-websites/   # From provider-website-scraper
│   │   ├── 07-hemtjanstindex/        # Hemtjänstindex CSVs
│   │   ├── 09-skr-data/              # SKR municipality groups
│   │   ├── 10-homecare-recipients/   # Recipient counts
│   │   ├── 10.5-kolada/              # Kolada KPIs
│   │   ├── 13-branschrapport/        # Nova Omsorg, Excel exports
│   │   ├── 14-scb/                   # SCB data
│   │   ├── 14.7-pdf-statistics/      # Extracted PDF stats
│   │   └── 15-gamification/          # Badge definitions
│   │
│   ├── 01-seed-national-statistics.ts
│   ├── 02-seed-municipalities.ts
│   ├── ... (19 seed scripts)
│   └── verify-seed-data.ts           # Verification script
│
└── _archive/                         # Archived old scripts
```

---

## Data Creation Scripts (18 Total)

### TypeScript Web Scrapers (6)

| Script                        | Source                | Output                                             | Description                                 |
| ----------------------------- | --------------------- | -------------------------------------------------- | ------------------------------------------- |
| `municipality-scraper.ts`     | Municipality websites | `seed-data/02-municipalities/scraped/`             | Scrapes provider lists from municipal sites |
| `provider-detail-scraper.ts`  | Infoval API           | `seed-data/05.5-infoval-quality/`                  | Gets detailed quality metrics from Infoval  |
| `provider-website-scraper.ts` | Provider websites     | `seed-data/05.6-provider-websites/`                | Scrapes provider's own websites             |
| `scb-scraper.ts`              | SCB PxWeb API         | `seed-data/14-scb/`                                | Swedish official statistics                 |
| `kolada-scraper.ts`           | Kolada API            | `seed-data/10.5-kolada/`                           | Municipality KPIs                           |
| `url-discovery-from-json.ts`  | Municipality sites    | `seed-data/02-municipalities/urls-discovered.json` | Discovers hemtjänst page URLs               |

### Python Scrapers (4 - kommun.jensnylander.com + Municipality Pages)

| Script                              | Source                  | Output                                 | Description                                                                                |
| ----------------------------------- | ----------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------ |
| `jens-filtered-sni.py`              | kommun.jensnylander.com | `seed-data/03.5-providers-enrichment/` | Filters by SNI codes 88101/88102                                                           |
| `jens-provider-details-sni.py`      | kommun.jensnylander.com | `seed-data/03.5-providers-enrichment/` | Provider details with invoicing                                                            |
| `jens-api-sni-filtered-amounts.py`  | kommun.jensnylander.com | `seed-data/03.5-providers-enrichment/` | Financial amounts per provider                                                             |
| `scrape_hemtjanst_providers_all.py` | Municipality websites   | `seed-data/05.7-municipality-scraped/` | Scrapes provider lists from all 290 municipality pages → Creates JSON files (NOT database) |

### PDF Extractors (6)

| Script                               | Source PDFs                    | Output                              | Description                          |
| ------------------------------------ | ------------------------------ | ----------------------------------- | ------------------------------------ |
| `extract-hemtjanstindex.ts`          | `source-pdfs/hemtjanstindex/`  | `seed-data/07-hemtjanstindex/`      | Hemtjänstindex rankings              |
| `extract-methodology-stats.ts`       | `source-pdfs/socialstyrelsen/` | `seed-data/01-national-statistics/` | National statistics                  |
| `extract-nova-omsorg.ts`             | `source-pdfs/nova-omsorg/`     | `seed-data/13-branschrapport/`      | Nova Omsorg audit reports            |
| `extract-pdf-data.ts`                | `source-pdfs/socialstyrelsen/` | `seed-data/14.7-pdf-statistics/`    | General PDF extraction               |
| `extract-pdf-statistics.ts`          | `source-pdfs/socialstyrelsen/` | `seed-data/14.7-pdf-statistics/`    | Statistical tables                   |
| `extract-pdf-statistics-enhanced.ts` | `source-pdfs/socialstyrelsen/` | `seed-data/14.7-pdf-statistics/`    | Enhanced extraction with salary data |

### API/Excel Processors (2)

| Script                     | Source                  | Output                                       | Description           |
| -------------------------- | ----------------------- | -------------------------------------------- | --------------------- |
| `process-stockholm-api.ts` | Stockholm hemtjänst API | `seed-data/02-municipalities/stockholm.json` | Stockholm providers   |
| `convert-excel-to-csv.ts`  | `source-excel/*.xlsx`   | `seed-data/13-branschrapport/`               | Converts Excel to CSV |

---

## Seed Scripts (20 Total)

| Step | Script                              | Description                             | Auto-Fallback                        |
| ---- | ----------------------------------- | --------------------------------------- | ------------------------------------ |
| 01   | `01-seed-national-statistics.ts`    | National-level statistics               | ✅ extract-methodology-stats         |
| 02   | `02-seed-municipalities.ts`         | All 290 municipalities                  | -                                    |
| 03   | `03-seed-providers-csv.ts`          | **PRIMARY** - 1,800+ providers from CSV | -                                    |
| 03.5 | `03.5-seed-providers-enrichment.ts` | Enrichment from Jens scrapers           | ✅ Jens Python scripts               |
| 04   | `04-seed-municipality-survey.ts`    | Municipality survey aggregates          | -                                    |
| 05   | `05-seed-provider-satisfaction.ts`  | 292 CSV satisfaction files              | -                                    |
| 05.5 | `05.5-seed-quality-metrics.ts`      | Quality metrics from Infoval            | ✅ provider-detail-scraper           |
| 05.7 | `05.7-seed-municipality-scraped.ts` | Provider websites, contacts, sourceUrls | ✅ scrape_hemtjanst_providers_all.py |
| 07   | `07-seed-hemtjanstindex.ts`         | Hemtjänstindex 2025 rankings            | ✅ extract-hemtjanstindex            |
| 08   | `08-calculate-rankings.ts`          | CaireIndex rankings                     | -                                    |
| 09   | `09-seed-skr-data.ts`               | SKR municipality groups                 | -                                    |
| 10   | `10-seed-homecare-recipients.ts`    | Home care recipient counts              | -                                    |
| 10.5 | `10.5-seed-kolada-kpis.ts`          | Kolada KPI data                         | -                                    |
| 14   | `14-seed-scb-data.ts`               | SCB municipality data                   | -                                    |
| 15   | `15-seed-gamification.ts`           | Badge definitions and quests            | -                                    |
| 16   | `16-seed-data-sources.ts`           | Data source configurations              | -                                    |
| 17   | `17-seed-municipality-finances.ts`  | Municipality finances                   | -                                    |
| 18   | `18-seed-sync-provider-rows.ts`     | Sync 1:1 records                        | -                                    |
| 19   | `19-seed-sync-counts.ts`            | **MUST BE LAST** - Sync counts          | -                                    |
| 28   | `28-seed-jensnylander-urls.ts`      | Jens Nylander URLs + Financial Data     | ✅ Jens Python scrapers              |

---

## Commands Reference

### Data Creation

```bash
# Run all 17 data creators
yarn workspace stats-server data:create-all

# Run individual groups
yarn workspace stats-server data:scrapers     # TypeScript scrapers only
yarn workspace stats-server data:extractors   # PDF extractors only
yarn workspace stats-server data:processors   # API/Excel processors only
yarn workspace stats-server data:jens         # Python Jens scrapers
```

### Database Seeding

```bash
# Complete seed (all 19 scripts in order)
yarn workspace stats-server db:seed

# Quick reset from snapshot (fast)
yarn workspace stats-server db:quick-reset

# Full reset (runs all seeds)
yarn workspace stats-server db:reset-all

# Fresh seed (create + seed + verify)
yarn workspace stats-server db:seed:fresh
```

### Verification

```bash
# Verify all data is correctly seeded
yarn workspace stats-server db:seed:verify
```

---

## Verification System

The verification script checks all tables and relationships:

```
======================================================================
📊 SEED DATA VERIFICATION
======================================================================

----------------------------------------------------------------------
Table                             Expected      Actual      Status
----------------------------------------------------------------------
NationalStatistics                       1           4     ⚠️ WARN
Municipality                           290         290      ✅ PASS
Provider                             ≥2192        2192      ✅ PASS
ProviderMunicipality                 ≥2192        1629     ⚠️ WARN
QualityMetric                         ≥100        1631      ✅ PASS
ProviderRanking                      ≥8768        4786     ⚠️ WARN
ProviderFinancials                    ≥100        2197      ✅ PASS
MunicipalityRanking                   ≥290         638      ✅ PASS
MunicipalityQualitySummary            ≥100         290      ✅ PASS
MunicipalityFinance                   ≥100         856      ✅ PASS
DataSourceConfig                        ≥5           7      ✅ PASS
----------------------------------------------------------------------

📋 SUMMARY
   ✅ Passed: 8
   ⚠️ Warnings: 3
   ❌ Failed: 0

======================================================================
🔍 DETAILED CHECKS
======================================================================
📌 Providers without municipality links: 1025
📌 Providers without rankings: 1197
📌 Municipalities with providers: 278/290
📌 Quality metrics with continuity: 0/1631
📌 Nova Omsorg providers: 6 ✅
📌 Stockholm providers: 179 ✅
📌 Nacka providers: 15 ✅
```

### Interpreting Results

| Status  | Meaning                                               |
| ------- | ----------------------------------------------------- |
| ✅ PASS | Table meets or exceeds expected count                 |
| ⚠️ WARN | Table has data but below expected (run more scrapers) |
| ❌ FAIL | Critical - table is empty or severely under-populated |

---

## Auto-Fallback System

Seed scripts automatically run data creators if required data is missing:

```typescript
// Example from 05.5-seed-quality-metrics.ts
async function ensureSeedData(): Promise<boolean> {
  const dataDir = path.join(__dirname, "seed-data/05.5-infoval-quality");

  if (!fs.existsSync(dataDir) || fs.readdirSync(dataDir).length === 0) {
    console.log("⚠️ Seed data not found. Running provider-detail-scraper...");

    try {
      execSync(
        "npx tsx src/data-creators/scrapers/provider-detail-scraper.ts",
        {
          cwd: path.join(__dirname, ".."),
          stdio: "inherit",
        },
      );
      return true;
    } catch (error) {
      console.error("❌ Failed to create seed data:", error);
      return false;
    }
  }

  return true;
}
```

---

## Data Flow

### Complete Pipeline

```
1. SCRAPE/EXTRACT (Data Creators)
   └── data:create-all
       ├── municipality-scraper → seed-data/02-municipalities/scraped/ (JSON files)
       ├── provider-detail-scraper → seed-data/05.5-infoval-quality/ (JSON files)
       ├── scrape_hemtjanst_providers_all.py → seed-data/05.7-municipality-scraped/ (JSON files)
       │   └── Input: municipality-provider-scraper/input/hemtjanst_kommuner_seed_sanitized.json
       ├── extract-hemtjanstindex → seed-data/07-hemtjanstindex/ (JSON files)
       └── ... (14 more scripts)

   ⚠️ IMPORTANT: Data creators create FILES, NOT database records
   ✅ This allows reproducing the database from seed-data files

2. SEED (Seed Scripts)
   └── db:seed
       ├── 01-seed-national-statistics ← Reads seed-data/01-national-statistics/ → Saves to DB
       ├── 02-seed-municipalities ← Reads seed-data/02-municipalities/ → Saves to DB
       ├── 03-seed-providers-csv ← Reads seed-data/03-providers-csv/ → Saves to DB
       ├── 05.7-seed-municipality-scraped ← Reads seed-data/05.7-municipality-scraped/ → Saves to DB
       └── ... (16 more scripts)

   ✅ Seed scripts read JSON/CSV files and write to database
   ✅ Can re-run to update database from seed-data files

3. VERIFY
   └── db:seed:verify
       ├── Check Municipality count (290)
       ├── Check Provider count (2192+)
       ├── Check QualityMetric count
       └── Check all relationships
```

### Key Principle: Files First, Database Second

**Data creators (scrapers/extractors) → Create seed-data files → Seed scripts → Database**

This architecture allows:

- ✅ Reproducible database: Can recreate entire DB from seed-data files
- ✅ Version control: Seed-data files can be committed (or stored in backup repo)
- ✅ Testing: Can test seed scripts without running scrapers
- ✅ Flexibility: Can manually edit seed-data files if needed

### Data Priority Hierarchy

1. **CSV Files (Socialstyrelsen)** - Primary source of truth
2. **JSON Files (Scraped)** - Current provider lists from Infoval/municipalities
3. **API Sources** - Real-time enrichment (Jens, Kolada, SCB)

### Jens Nylander URL Management Flow

**Script 28** (`28-seed-jensnylander-urls.ts`) follows the proper data architecture:

```
1. SCRAPE (Python Scrapers - Data Creators)
   ├── jens-filtered-sni.py → leverantorer_filtered_88101_88102.csv
   ├── jens-provider-details-sni.py → provider_details_{id}.json
   └── jens-api-sni-filtered-amounts.py → provider_financials.json

   ⚠️ IMPORTANT: Scrapers create FILES in seed-data/, NOT database records
   ✅ Output: seed-data/03.5-providers-enrichment/

2. SEED (Seed Script reads files)
   └── 28-seed-jensnylander-urls.ts
       ├── Step 1: Populate URLs (slugs, IDs) from CSV files
       ├── Step 2: Read scraped data from seed-data/
       └── Step 3: Store in database

   ✅ Auto-fallback: If seed-data is empty, prompts to run scrapers first

3. ADMIN UPDATE (Admin UI)
   └── http://localhost:3001/admin/scout?tab=kallor
       ├── View current Jens Nylander URLs and data
       ├── Manual scrape button → Runs Python scrapers → Updates seed-data/
       └── Manual sync button → Re-runs seed script → Updates database
```

**Key Benefits:**

- ✅ **Reproducible**: Database can be recreated from seed-data files
- ✅ **Versionable**: Scraped data files can be committed to git (or backup repo)
- ✅ **Testable**: Can test seed script without running scrapers
- ✅ **Flexible**: Admin can re-scrape anytime via UI

**Commands:**

```bash
# 1. Run scrapers (creates seed-data files)
cd apps/stats-server/src/data-creators/scrapers/kommun_export
python3 jens-filtered-sni.py
python3 jens-provider-details-sni.py
python3 jens-api-sni-filtered-amounts.py

# 2. Run seed script (reads files, writes to DB)
yarn workspace stats-server db:seed:28-jensnylander

# 3. Verify in admin UI
open http://localhost:3001/admin/scout?tab=kallor
```

---

## Expected Database Counts

After complete seed:

| Table                | Expected Count | Notes                         |
| -------------------- | -------------- | ----------------------------- |
| Municipality         | 290            | All Swedish municipalities    |
| Provider             | 2,192+         | From Socialstyrelsen CSV      |
| ProviderMunicipality | 2,000+         | Provider-municipality links   |
| QualityMetric        | 1,600+         | Customer satisfaction data    |
| ProviderRanking      | 4,000+         | 4 categories per provider     |
| ProviderFinancials   | 2,000+         | Financial data per provider   |
| MunicipalityRanking  | 600+           | Municipality quality rankings |
| MunicipalityFinance  | 800+           | Municipality financial data   |
| NationalStatistics   | 1-4            | National aggregates per year  |

---

## Troubleshooting

### Missing Quality Metrics

**Problem:** `Quality metrics with continuity: 0/1631`

**Solution:** Run the Infoval scraper to populate staff continuity data:

```bash
yarn workspace stats-server tsx src/data-creators/scrapers/provider-detail-scraper.ts
yarn workspace stats-server db:seed
```

### Providers Without Rankings

**Problem:** Many providers without rankings

**Solution:** Re-run ranking calculation after quality metrics are populated:

```bash
yarn workspace stats-server tsx src/seed-scripts/08-calculate-rankings.ts
```

### Missing Seed Data

**Problem:** Seed script fails with "File not found"

**Solution:** Run the corresponding data creator:

```bash
yarn workspace stats-server data:create-all
```

### Python Scraper Issues

**Problem:** Jens scrapers fail

**Solution:** Ensure Python environment is set up:

```bash
cd apps/stats-server/src/data-creators/scrapers/kommun_export
pip install requests pandas
python3 jens-filtered-sni.py
```

---

## API Endpoints Reference

### Infoval.se API

```
GET https://infoval-backend.infoval.se/api/public/municipality/{slug}/category/{categoryId}
```

- **Returns:** List of organizers (providers) with full data
- **Example:** `https://infoval-backend.infoval.se/api/public/municipality/nacka/category/10`
- **Used by:** `provider-detail-scraper.ts`

### Stockholm API

```
GET https://aldreomsorg.stockholm/api/serviceunitsapi/serviceunits?page[limit]=200&page[offset]=0&sort=Name&filter[servicetype.id]=6
```

- **Returns:** JSON with service units (providers)
- **Pagination:** Via `page[offset]` parameter
- **Used by:** `process-stockholm-api.ts`

### kommun.jensnylander.com API

```
GET https://kommun.jensnylander.com/api/suppliers?sni=88101,88102
```

- **Returns:** Provider details with invoicing data
- **Used by:** Python scrapers (`jens-*.py`)

---

## Rate Limiting & Error Handling

### Rate Limits

All scrapers include rate limiting to avoid overloading external APIs:

| Scraper                   | Delay     | Notes                  |
| ------------------------- | --------- | ---------------------- |
| URL discovery             | 300-500ms | Between requests       |
| Municipality scraping     | 2000ms    | Between municipalities |
| Provider detail scraping  | 500ms     | Between API calls      |
| Provider website scraping | 2000ms    | Between websites       |

### Error Handling

All scrapers have robust error handling:

- **HTTP errors:** Logged but don't stop the process
- **Timeouts:** 10-30 seconds per request
- **Failed items:** Logged, process continues
- **Progress:** Intermediate saves to avoid data loss

---

## Data Sourcing Strategy

### Core Principles

1. **API-First Approach** - Always fetch from official APIs first (SCB, Kolada, Infoval)
2. **CSV as Backup** - Use CSV files when APIs fail or are unavailable
3. **Year-Based Versioning** - All data organized by year (2023, 2024, 2025)
4. **Local Storage** - Seed data stored in `seed-data/` directory

### Priority Hierarchy

1. **CSV Files (Socialstyrelsen)** - Primary source of truth for quality data
2. **JSON Files (Scraped)** - Current provider lists from Infoval/municipalities
3. **API Sources** - Real-time enrichment (Jens, Kolada, SCB)

### Future: Cloud Storage (Not Yet Implemented)

For production environments, consider cloud storage for large CSV files:

```
s3://your-bucket/seo-data/
├── scb/
│   ├── 2024/
│   └── 2025/
├── kolada/
└── socialstyrelsen/
```

Environment variables for cloud storage:

```bash
# Production (future)
SCB_CSV_STORAGE_TYPE=s3
SCB_CSV_BASE_PATH=s3://production-seo-data/scb
```

---

## Related Documentation

- [SEED_SYSTEM_GUIDE.md](./SEED_SYSTEM_GUIDE.md) - Complete seed system guide (MAIN REFERENCE)
- [DATA_STRUCTURE_GUIDE.md](./DATA_STRUCTURE_GUIDE.md) - Database schema reference
- [SCB_COMPLETE_GUIDE.md](./SCB_COMPLETE_GUIDE.md) - SCB API usage

---

**Last Updated:** 2026-01-04  
**Maintained By:** Development Team
