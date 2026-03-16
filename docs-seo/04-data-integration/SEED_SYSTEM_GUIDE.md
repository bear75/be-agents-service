# Seed System Guide - Complete Documentation

> **📅 Last Updated:** 2026-01-10  
> **Version:** 3.0  
> **Status:** Production Ready  
> **⚠️ CRITICAL:** This system is the **site's heart** - all SEO data depends on it

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [System Architecture](#system-architecture)
4. [Data Flow](#data-flow)
5. [Seed Scripts Reference](#seed-scripts-reference)
6. [Deduplication Strategy](#deduplication-strategy)
7. [Verification System](#verification-system)
8. [Troubleshooting](#troubleshooting)
9. [Data Sources](#data-sources)
10. [Maintenance & Updates](#maintenance--updates)

---

## Overview

The seed system is the **foundational data pipeline** for all SEO sites. It populates the database with provider and municipality data from multiple sources, creating the complete dataset that powers:

- Provider listings and rankings
- Municipality comparisons and statistics
- National statistics and trends
- Quality metrics and ratings
- Financial data and analyses

### Key Statistics

- **290 municipalities** (all Swedish kommuner)
- **~2,000 providers** (hemtjänstanordnare)
- **~2,000 provider-municipality presences** (where providers are active)
- **~1,600 quality metrics** (customer satisfaction, staff continuity)
- **~4,000 provider rankings** (across multiple categories)
- **15+ data sources** (Socialstyrelsen, Kolada, SCB, Infoval, etc.)

---

## Quick Start

### Full Seed (Recommended)

```bash
# Seed all data sources in correct order
yarn workspace stats-server db:seed

# Verify data quality after seeding
yarn workspace stats-server db:verify
```

### Quick Reset (Development)

```bash
# Fast reset from snapshot (seconds)
yarn workspace stats-server db:quick-reset

# Full reset (runs all seeds, slow)
yarn workspace stats-server db:reset-all
```

### Individual Scripts

```bash
# Run specific seed script
yarn workspace stats-server db:seed:03-providers-unified
yarn workspace stats-server db:seed:08-calculate-rankings
yarn workspace stats-server db:seed:19-sync-counts
```

---

## System Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│              DATA CREATION (Manual/Automated)                │
├─────────────────────────────────────────────────────────────┤
│  • Web Scrapers (Python/TS)                                 │
│  • PDF Extractors                                           │
│  • API Fetchers                                             │
│  • Excel/CSV Processors                                     │
│  Output: CSV/JSON files in seed-data/                       │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              SEED DATA DIRECTORY (Source Files)               │
├─────────────────────────────────────────────────────────────┤
│  apps/stats-server/src/seed-scripts/seed-data/               │
│  ├── 01-national-statistics/                                │
│  ├── 02-municipalities/                                     │
│  ├── 03-providers-csv/          ← PRIMARY SOURCE             │
│  ├── 03.5-providers-enrichment/                             │
│  ├── 05-provider-satisfaction/  ← 292 CSV files              │
│  ├── 07-hemtjanstindex/                                     │
│  └── ... (15+ data directories)                             │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              SEED SCRIPTS (01-31 in order)                    │
├─────────────────────────────────────────────────────────────┤
│  01. National Statistics                                    │
│  02. Municipalities                                         │
│  03. Providers (UNIFIED - PRIMARY) ← Creates all providers   │
│  03.5. Provider Enrichment                                  │
│  04-31. Enrichment & Aggregation scripts                    │
│  Each script: Reads seed-data/ → Writes to database         │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                        DATABASE                               │
├─────────────────────────────────────────────────────────────┤
│  • Municipality (290)                                       │
│  • Provider (~2,000)                                        │
│  • ProviderMunicipality (~2,000)                            │
│  • QualityMetric (~1,600)                                   │
│  • ProviderRanking (~4,000)                                 │
│  • NationalStatistics                                       │
│  • MunicipalityFinance (290)                                │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              VERIFICATION (Data Quality Checks)               │
├─────────────────────────────────────────────────────────────┤
│  • Duplicate detection                                      │
│  • Missing data checks                                      │
│  • Relationship validation                                  │
│  • Count verification                                       │
│  Output: verification-report.json + console output          │
└─────────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Files First, Database Second**
   - Data creators (scrapers) → Create seed-data files
   - Seed scripts → Read files → Write to database
   - Allows reproducible database from seed-data files

2. **Auto-Numbering for Providers**
   - Municipal providers: `MUN{code}-{hash}` (deterministic)
   - Private providers: Matched from Kommun API, or `PRV{code}-{hash}` (fallback)
   - **100% coverage** - No manual fixes needed

3. **Upsert Strategy**
   - All scripts use upsert to prevent duplicates
   - Matching priority: orgNumber > slug > name+legalName+orgType

4. **Order Matters**
   - Scripts must run in correct order (01-31)
   - Dependencies: providers before presences, presences before rankings
   - Last script (19) syncs denormalized counts

---

## Data Flow

### Complete Pipeline

#### Phase 1: Data Creation (Manual/As Needed)

**TypeScript Scrapers:**

- `municipality-scraper.ts` → `seed-data/02-municipalities/scraped/`
- `provider-detail-scraper.ts` → `seed-data/05.5-infoval-quality/`
- `scb-scraper.ts` → `seed-data/14-scb/`

**Python Scrapers:**

- `jens-filtered-sni.py` → `seed-data/03.5-providers-enrichment/`
- `jens-provider-details-sni.py` → Provider details JSON
- `scrape_hemtjanst_providers_all.py` → `seed-data/05.7-municipality-scraped/`

**PDF Extractors:**

- `extract-hemtjanstindex.ts` → `seed-data/07-hemtjanstindex/`
- `extract-pdf-statistics-enhanced.ts` → `seed-data/14.7-pdf-statistics/`

**⚠️ IMPORTANT:** Data creators create FILES, NOT database records. This allows reproducing the database from seed-data files.

#### Phase 2: Database Seeding (Automated)

**Main Seed Command:**

```bash
yarn workspace stats-server db:seed
```

**Execution Order (31 steps):**

1. **01-national-statistics** → Base national data
2. **02-municipalities** → All 290 municipalities + test providers (JSON)
3. **03-providers-unified** → **PRIMARY** - Creates all ~2,000 providers from CSV (auto-generates orgNumbers)
4. **03.5-providers-enrichment** → Enriches with financial data (updates only)
5. **04-municipality-survey** → Aggregated quality indicators (CSV)
6. **05-provider-satisfaction** → Customer satisfaction from 292 CSV files
7. **05.5-quality-metrics** → Quality data from scraped JSON (Infoval)
8. **05.7-municipality-scraped** → Provider websites, contacts, sourceUrls
9. **06-quality-summaries** → Aggregated municipality summaries (calculated)
10. **07-hemtjanstindex** → Hemtjänstindex 2025 rankings
11. **08-calculate-rankings** → CaireIndex rankings (Provider & Municipality)
12. **08.5-calculate-trends** → Year-over-year trends
13. **09-skr-data** → SKR municipality groups
14. **10-homecare-recipients** → Recipient counts (CSV)
15. **10.5-kolada-kpis** → Kolada KPI data (pre-scraped)
16. **11-financials** → Provider financials (optional, requires TIC_API_KEY)
17. **12-kommun-api** → Kommun API data (optional, requires KOMMUN_API_KEY)
18. **13-branschrapport** → Branschrapport data (optional)
19. **14-scb-data** → SCB municipality data (optional, API-based)
20. **15-gamification** → Badge definitions (hardcoded)
21. **16-data-sources** → Data source configurations (hardcoded)
22. **17-municipality-finances** → Municipality finance records (all 290)
23. **18-sync-provider-rows** → Sync 1:1 consistency
24. **19-sync-counts** → **MUST BE LAST** - Sync denormalized counts
25. **20-scb-table-configs** → SCB PxWeb API table configurations
26. **21-kolada-ous** → Kolada organizational units
27. **22-pdf-statistics** → Statistics from extracted PDFs
28. **23-salary-statistics** → SCB API salary data
29. **24-scraped-data** → Scraped provider data (pilot municipalities)
30. **25-scraping-status** → Scraping job status
31. **Verify** → Database integrity verification

#### Phase 3: Verification (Automated)

**Verification Script:** `00-verify-database-integrity.ts`

**Checks Performed:**

- ✅ Duplicate providers (by orgNumber, name, slug)
- ✅ Orphaned records (financials, rankings, presences)
- ✅ Missing critical data (orgNumbers, presences, rankings)
- ✅ Rankings consistency (kommun vs national)
- ✅ Expected record counts (providers, municipalities, etc.)
- ✅ National statistics accuracy

**Output:**

- Console: Color-coded verification results
- JSON: `apps/stats-server/verification-report.json` (for CI/CD)

---

## Seed Scripts Reference

### Core Scripts (Required - Run in seed.ts)

| Step | Script                              | Purpose                                                    | Data Source                           | Status      |
| ---- | ----------------------------------- | ---------------------------------------------------------- | ------------------------------------- | ----------- |
| 01   | `01-seed-national-statistics.ts`    | Base national statistics                                   | seed-data/01-national-statistics/     | ✅ Required |
| 02   | `02-seed-municipalities.ts`         | Municipalities & test providers from JSON                  | seed-data/02-municipalities/          | ✅ Required |
| 03   | `03-seed-providers-unified.ts`      | **PRIMARY** - 1,800+ providers (auto-generates orgNumbers) | seed-data/03-providers-csv/ + mapping | ✅ Required |
| 03.5 | `03.5-seed-providers-enrichment.ts` | Enrich with financial data (updates only)                  | seed-data/03.5-providers-enrichment/  | ✅ Required |
| 04   | `04-seed-municipality-survey.ts`    | Municipality survey aggregates                             | seed-data/04-municipality-survey/     | ✅ Required |
| 05   | `05-seed-provider-satisfaction.ts`  | Provider satisfaction metrics (292 CSV files)              | seed-data/05-provider-satisfaction/   | ✅ Required |
| 05.5 | `05.5-seed-quality-metrics.ts`      | Quality metrics from scraped JSON                          | seed-data/05.5-infoval-quality/       | ⚠️ Optional |
| 05.7 | `05.7-seed-municipality-scraped.ts` | Provider websites, contacts, sourceUrls                    | seed-data/05.7-municipality-scraped/  | ⚠️ Optional |
| 06   | `06-seed-quality-summaries.ts`      | Aggregate quality summaries                                | Calculated from DB                    | ✅ Required |
| 07   | `07-seed-hemtjanstindex.ts`         | Hemtjänstindex 2025 rankings                               | seed-data/07-hemtjanstindex/          | ✅ Required |
| 08   | `08-calculate-rankings.ts`          | CaireIndex rankings (weighted scores)                      | Calculated from DB                    | ✅ Required |
| 08.5 | `08.5-calculate-trends.ts`          | Year-over-year trends                                      | Calculated from DB                    | ✅ Required |
| 09   | `09-seed-skr-data.ts`               | SKR municipality groups                                    | seed-data/09-skr-data/                | ✅ Required |
| 10   | `10-seed-homecare-recipients.ts`    | Home care recipient counts                                 | seed-data/10-homecare-recipients/     | ✅ Required |
| 10.5 | `10.5-seed-kolada-kpis.ts`          | Kolada KPI data                                            | seed-data/10.5-kolada/                | ✅ Required |
| 14   | `14-seed-indikator-survey.ts`       | Indikator.org survey data (29 quality indicators)          | seed-data/14-indikator-survey/        | ⚠️ Optional |
| 15   | `15-seed-gamification.ts`           | Badge definitions & quests                                 | Hardcoded                             | ✅ Required |
| 16   | `16-seed-data-sources.ts`           | Data source configurations                                 | Hardcoded                             | ✅ Required |
| 17   | `17-seed-municipality-finances.ts`  | Municipality finances (all 290 municipalities)             | Multiple sources                      | ✅ Required |
| 18   | `18-seed-sync-provider-rows.ts`     | Sync provider & presence rows (1:1 consistency)            | Database                              | ✅ Required |
| 19   | `19-seed-sync-counts.ts`            | **MUST BE LAST** - Sync denormalized counts                | Calculated from DB                    | ✅ Required |
| 20   | `20-seed-scb-table-configs.ts`      | SCB PxWeb API table configurations                         | Hardcoded                             | ✅ Required |
| 21   | `21-seed-kolada-ous.ts`             | Kolada organizational units                                | Kolada API                            | ⚠️ Optional |
| 22   | `22-seed-pdf-statistics.ts`         | Statistics from extracted PDFs                             | seed-data/14.7-pdf-statistics/        | ⚠️ Optional |
| 23   | `23-seed-salary-statistics.ts`      | Salary statistics (SCB API TAB5696)                        | SCB API                               | ⚠️ Optional |
| 24   | `24-seed-scraped-data.ts`           | Scraped provider data (pilot municipalities)               | seed-data/02-utforare/                | ⚠️ Optional |
| 25   | `25-seed-scraping-status.ts`        | Scraping job status (pilot municipalities)                 | Database                              | ⚠️ Optional |

### Optional Scripts (May fail gracefully)

These scripts run automatically but can be skipped if they fail:

| Script                      | Purpose                   | Requirements                 |
| --------------------------- | ------------------------- | ---------------------------- |
| `11-seed-financials.ts`     | Provider financial data   | TIC_API_KEY                  |
| `12-seed-kommun-api.ts`     | Kommun API invoicing data | KOMMUN_API_KEY               |
| `13-seed-branschrapport.ts` | Branschrapport data       | seed-data/13-branschrapport/ |
| `14-seed-scb-data.ts`       | SCB municipality data     | SCB API (live)               |

### Extended Scripts (Run after step 25)

These scripts run automatically after step 25:

| Script                         | Purpose                                                   | Prerequisites                         |
| ------------------------------ | --------------------------------------------------------- | ------------------------------------- |
| `27-seed-provider-details.ts`  | Provider financials & rankings from Kommun API CSV        | Step 3.5 (enrichment)                 |
| `28-seed-jensnylander-urls.ts` | Auto-populate Jens Nylander URLs and IDs                  | CSV data from kommun.jensnylander.com |
| `29-seed-jens-scraped-data.ts` | Import complete scraped data from kommun.jensnylander.com | Step 28                               |
| `30-calculate-rankings-v2.ts`  | Enhanced CaireIndex v2 with financial data                | Step 29                               |
| `31-seed-corporate-groups.ts`  | Create corporate groups and link provider units           | Step 29                               |

**Note:** These scripts are now part of the automatic seed process and run in order after step 25.

---

## Deduplication Strategy

### Core Principles

1. **Use Unique Constraints**: Always rely on schema unique constraints (slug, orgNumber, etc.)
2. **Always Use Upsert**: Never use `create()` - always use `upsert()` or check existence first
3. **Match by Canonical Identifiers**: Priority order: orgNumber > slug > name+legalName+orgType
4. **Pilot Municipalities**: Stockholm and Nacka use JSON seed as source of truth - CSV seed should skip them

### Unique Constraints in Schema

**Provider:**

- `slug` @unique
- `orgNumber` @unique
- `hubspotCompanyId` @unique

**Municipality:**

- `slug` @unique
- `municipalityCode` @unique

**ProviderMunicipality:**

- `@@unique([providerId, municipalityId])`

**QualityMetric:**

- `@@unique([presenceId, year, source])`

**ProviderFinancials:**

- `@@unique([providerId, year, source])`

### Provider Deduplication Priority

1. **orgNumber** (most reliable)
   - Real orgNumbers (10 digits) are canonical identifiers
   - Auto-generated orgNumbers (MUN/PRV) are less reliable but still unique

2. **slug** (fallback)
   - URL-friendly identifier
   - Should be deterministic based on name

3. **name + legalName + orgType** (last resort)
   - For municipal: match by name only
   - For private: match by name + legalName
   - Allow orgType to differ (UNKNOWN vs PRIVATE/MUNICIPAL)

### Deduplication Utilities

Use centralized utilities in `utils/deduplication-strategy.ts`:

```typescript
import {
  isPilotMunicipality,
  findExistingProvider,
  findExistingMunicipality,
  findExistingPresence,
  normalizeOrgNumber,
  isAutoGeneratedOrgNumber,
} from "./utils/deduplication-strategy.js";
```

**Example Usage:**

```typescript
const existing = await findExistingProvider(prisma, {
  orgNumber: provider.orgNumber,
  slug: provider.slug,
  name: provider.name,
  legalName: provider.legalName,
  orgType: provider.orgType,
});

if (existing) {
  await prisma.provider.update({
    where: { id: existing.id },
    data: {
      /* updates */
    },
  });
} else {
  await prisma.provider.create({
    data: {
      /* new provider */
    },
  });
}
```

### Pilot Municipalities

Stockholm and Nacka are "pilot municipalities" that use JSON seed data as the source of truth. CSV seed scripts should skip these municipalities.

**Check if Pilot Municipality:**

```typescript
import { isPilotMunicipality } from "./utils/deduplication-strategy.js";

if (isPilotMunicipality(municipalitySlug)) {
  // Skip this municipality in CSV seed
  continue;
}
```

---

## Verification System

### Master Verification Script

**Location:** `apps/stats-server/src/seed-scripts/00-verify-database-integrity.ts`

**Command:**

```bash
yarn workspace stats-server db:verify
```

**Checks Performed:**

1. ✅ **Duplicate Providers** - By orgNumber, name, slug
2. ✅ **Orphaned Records** - Financials, rankings, presences without providers
3. ✅ **Missing Critical Data** - Providers without orgNumbers, presences without rankings
4. ✅ **Rankings Consistency** - Kommun vs national rankings
5. ✅ **Expected Record Counts** - Providers, municipalities, presences
6. ✅ **National Statistics Accuracy** - Aggregates match individual records

**Output Format:**

```json
{
  "timestamp": "2026-01-08T10:30:00.000Z",
  "summary": {
    "status": "PASS | WARN | FAIL",
    "totalChecks": 8,
    "passed": 6,
    "warnings": 2,
    "critical": 0
  },
  "checks": {
    "duplicatesByOrgNumber": { "passed": true, "count": 0 },
    "missingData": { "passed": false, "providersWithoutRankings": 150 }
  },
  "issues": [...],
  "recommendations": [...]
}
```

**Console Output Example:**

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
```

---

## Troubleshooting

### Missing Provider Data

**Problem:** Providers missing from database

**Solution:**

1. Check if unified provider seed ran: `yarn workspace stats-server db:seed:03-providers-unified`
2. Check if enrichment ran: `yarn workspace stats-server db:seed:03.5-providers-enrichment`
3. Verify data files exist in `seed-data/03-providers-csv/` and `seed-data/03.5-providers-enrichment/`

### Rankings Not Updating

**Problem:** Provider/municipality rankings are outdated

**Solution:**

```bash
# Recalculate standard rankings
yarn workspace stats-server db:seed:08-calculate-rankings

# Or use enhanced v2 rankings (after Jens data)
yarn workspace stats-server tsx src/seed-scripts/30-calculate-rankings-v2.ts
```

### Counts Out of Sync

**Problem:** Municipality/provider counts are incorrect

**Solution:**

```bash
# Run sync-counts (should be last in main seed)
yarn workspace stats-server db:seed:19-sync-counts
```

### Duplicate Providers

**Problem:** Duplicate providers in database

**Solution:**

1. Run verification: `yarn workspace stats-server db:verify`
2. Check duplicate report: `apps/stats-server/verification-report.json`
3. Use corporate groups script to link duplicates: `yarn workspace stats-server db:fix:duplicates-corporate-groups`

### Missing Quality Metrics

**Problem:** Quality indicators are missing

**Solution:**

```bash
# Import from CSV files (292 files)
yarn workspace stats-server db:seed:05-provider-satisfaction

# Import from scraped JSON
yarn workspace stats-server db:seed:05.5-quality-metrics
```

### Missing Seed Data Files

**Problem:** Seed script fails with "File not found"

**Solution:**

```bash
# Run data creators to generate seed-data files
yarn workspace stats-server data:create-all

# Or run specific creator
yarn workspace stats-server data:scrapers
yarn workspace stats-server data:extractors
```

### After Importing Jens Scraped Data

If you've imported Jens Nylander scraped data (steps 27-29), run these in order:

```bash
# 1. Populate URLs and IDs
yarn workspace stats-server tsx src/seed-scripts/28-seed-jensnylander-urls.ts

# 2. Import complete scraped data
yarn workspace stats-server tsx src/seed-scripts/29-seed-jens-scraped-data.ts

# 3. Calculate enhanced rankings with financial data
yarn workspace stats-server tsx src/seed-scripts/30-calculate-rankings-v2.ts

# 4. Create corporate groups
yarn workspace stats-server tsx src/seed-scripts/31-seed-corporate-groups.ts
```

---

## Data Sources

### Primary Sources (Critical)

| Source                      | Type       | Data Provided                           | Update Frequency | Priority    |
| --------------------------- | ---------- | --------------------------------------- | ---------------- | ----------- |
| **Socialstyrelsen CSV**     | CSV Files  | Quality indicators, provider data       | Annually (Oct)   | 🔥 Critical |
| **Infoval.se**              | Scraping   | Current provider lists, quality metrics | Weekly           | 🔥 Critical |
| **kommun.jensnylander.com** | API (Free) | Provider lists, invoicing, org numbers  | Real-time        | 🔥 Critical |
| **Kolada API**              | API/CSV    | Municipality KPIs, staff continuity     | Annually         | High        |

### Secondary Sources (Optional)

| Source        | Type          | Data Provided                   | Requirements             |
| ------------- | ------------- | ------------------------------- | ------------------------ |
| **tic.io**    | API (Premium) | Financial data, risk ratings    | TIC_API_KEY              |
| **SCB API**   | API           | Demographics, municipality data | Live API                 |
| **Allabolag** | API/Export    | Financial data (fallback)       | API key or manual export |

### Data Source Priority

When multiple sources contain the same provider, use this priority order:

1. **CSV Files (Socialstyrelsen)** - Primary source of truth for quality data
2. **JSON Files (Scraped)** - Current provider lists from Infoval/municipalities
3. **API Sources** - Real-time enrichment (Jens, Kolada, SCB)

---

## Maintenance & Updates

### Adding New Data Source

1. **Create Data Creator** (if needed):
   - Add scraper/extractor to `apps/stats-server/src/data-creators/`
   - Output to appropriate `seed-data/` subdirectory

2. **Create Seed Script**:
   - Add numbered script (e.g., `32-seed-new-source.ts`)
   - Add to `seed.ts` orchestrator in correct order
   - Follow deduplication patterns (use utilities)

3. **Update Documentation**:
   - Add to this guide
   - Update seed scripts reference table
   - Update data sources table

### Updating Existing Data

**For CSV/JSON Sources:**

1. Update files in `seed-data/` directory
2. Re-run appropriate seed script: `yarn workspace stats-server db:seed:XX-script-name`

**For API Sources:**

1. Re-run seed script (will fetch latest data): `yarn workspace stats-server db:seed:XX-api-script`

**For Calculated Data (rankings, summaries):**

1. Re-run calculation scripts: `yarn workspace stats-server db:seed:08-calculate-rankings`
2. Re-run sync script: `yarn workspace stats-server db:seed:19-sync-counts`

### Expected Database Counts

After complete seed:

| Table                | Expected Count | Notes                         |
| -------------------- | -------------- | ----------------------------- |
| Municipality         | 290            | All Swedish municipalities    |
| Provider             | 2,000+         | From Socialstyrelsen CSV      |
| ProviderMunicipality | 2,000+         | Provider-municipality links   |
| QualityMetric        | 1,600+         | Customer satisfaction data    |
| ProviderRanking      | 4,000+         | 4 categories per provider     |
| ProviderFinancials   | 2,000+         | Financial data per provider   |
| MunicipalityRanking  | 600+           | Municipality quality rankings |
| MunicipalityFinance  | 800+           | Municipality financial data   |
| NationalStatistics   | 1-4            | National aggregates per year  |

---

## V2 Seeding System (Alternative Approach)

**Location:** `apps/stats-server/src/seed-scripts/v2/`

**Note:** There is also a V2 seeding system that uses a master-file approach with consolidated JSON files. See `apps/stats-server/src/seed-scripts/v2/README.md` for details.

**Command:** `yarn workspace stats-server db:seed:v2`

**Status:** Alternative system - the main production system uses the 01-31 script approach documented above.

**When to Use V2:**

- If you have consolidated master JSON files ready
- For testing/master file approaches
- For specific enrichment workflows

**When to Use Main System (01-31):**

- Production seeding (default)
- When using raw CSV/JSON sources
- When following the standard data flow (scrapers → seed-data → database)

---

## Related Documentation

- **[DATA_STRUCTURE_GUIDE.md](./DATA_STRUCTURE_GUIDE.md)** - Complete database schema reference
- **[COMPLETE_SEED_ARCHITECTURE.md](./COMPLETE_SEED_ARCHITECTURE.md)** - Data pipeline architecture
- **[DEDUPLICATION_GUIDE.md](./DEDUPLICATION_GUIDE.md)** - Deduplication patterns and strategies
- **[SCB_COMPLETE_GUIDE.md](./SCB_COMPLETE_GUIDE.md)** - SCB API usage
- **[MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)** - Database migration guide

---

## Quick Reference Commands

```bash
# Full seed (all steps 1-31)
yarn workspace stats-server db:seed

# Verify data quality
yarn workspace stats-server db:verify

# Quick reset from snapshot
yarn workspace stats-server db:quick-reset

# Individual scripts
yarn workspace stats-server db:seed:03-providers-unified
yarn workspace stats-server db:seed:08-calculate-rankings
yarn workspace stats-server db:seed:19-sync-counts

# Troubleshooting
yarn workspace stats-server db:seed:08-calculate-rankings  # Fix rankings
yarn workspace stats-server db:seed:19-sync-counts         # Fix counts
yarn workspace stats-server db:fix:duplicates-corporate-groups  # Fix duplicates
```

---

**Last Updated:** 2026-01-10  
**Maintained By:** Development Team  
**Critical System:** This is the site's heart - handle with care! ⚠️
