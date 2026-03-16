# Indikator.org Integration Guide

**Status:** ✅ Investigation Complete - Manual collection possible  
**Priority:** HIGH (29 detailed quality indicators per municipality)

## Overview

Indikator.org (https://webreport.indikator.org/Survey.aspx) is **Socialstyrelsen's official survey platform** for "Öppna Jämförelser - Äldreundersökning" (Open Comparisons - Elderly Survey).

### What We Have

✅ Login credentials for all 290 municipalities  
✅ User manual PDF  
✅ Data structure documented  
❌ No API integration yet - web interface only

### What Indikator Provides

**29 detailed quality indicators** per municipality across 5 categories:

| Category                         | Indicators   | Example Metrics                                      |
| -------------------------------- | ------------ | ---------------------------------------------------- |
| **Influence & Autonomy**         | 6 indicators | "Kan påverka innehåll", "Bestämmer när hjälp utförs" |
| **Information & Accessibility**  | 5 indicators | "Vet vem att kontakta", "Känner till biståndsbeslut" |
| **Staff & Social Interaction**   | 6 indicators | "Personalen lyssnar", "Får hjälp när det passar mig" |
| **Security & Perceived Quality** | 6 indicators | "Känner trygghet", "Har förtroende för personal"     |
| **Complete**                     | 6 indicators | "Nöjd med kvalitet", "Rekommenderar till andra"      |

**Plus additional data:**

- Response rates per municipality
- Year-over-year trends (2022-2024)
- Demographic breakdowns (age groups, service types)

## Login System

**Authentication:**

- Username format: `BU2025_{municipality_code}` (e.g., `BU2025_1440` for Ale)
- Passwords are unique per municipality
- Credentials stored in: `docs/docs-seo/04-data-integration/marketing-data/oppna-jamforelser-aldreundersokningar-2025-inloggningsuppgifter-indikator (1).csv`

**Special logins:**

- `BU2025_AM` - Public & media access
- `BU2025_Famna` - Branschorganisationen Famna
- `BU2025_VF` - Vårdföretagarna

## Data Structure

```typescript
interface IndikatorSurveyData {
  municipalityCode: string;
  municipalityName: string;
  year: number;
  responseRate: number;
  totalRespondents: number;

  indicators: {
    influence: {
      canInfluenceContent: number; // "Kan påverka innehåll"
      decidesWhenHelpProvided: number; // "Bestämmer när hjälp utförs"
      receivesHelpWhenNeeded: number; // "Får hjälp när behov uppstår"
    };
    information: {
      knowsWhoToContact: number; // "Vet vem att kontakta"
      knowsDecision: number; // "Känner till biståndsbeslut"
      receivesInformation: number; // "Får information"
    };
    staff: {
      staffListens: number; // "Personalen lyssnar"
      getsHelpWhenSuitable: number; // "Får hjälp när det passar mig"
      staffRespectful: number; // "Personalen bemöter respektfullt"
    };
    security: {
      feelsSafe: number; // "Känner trygghet"
      trustsStaff: number; // "Har förtroende för personal"
      feelsSafety: number; // "Känner sig trygg"
    };
    complete: {
      satisfiedQuality: number; // "Nöjd med kvalitet"
      recommendsToOthers: number; // "Rekommenderar till andra"
      overallSatisfaction: number; // "Helhetsbedömning"
    };
  };
}
```

## Manual Data Collection

### Step 1: Access Platform

**URL:** https://webreport.indikator.org/Survey.aspx

**Test Login:**

- Username: `BU2025_0180` (Stockholm)
- Password: `cKMrNU`

### Step 2: Export Data

**Priority Municipalities (Top 10 for testing):**

1. Stockholm (0180) - Login: `BU2025_0180`, Password: `cKMrNU`
2. Göteborg (1480) - Login: `BU2025_1480`, Password: `s4efdi`
3. Malmö (1280) - Login: `BU2025_1280`, Password: `CS9L8R`
4. Uppsala (0380) - Login: `BU2025_0380`, Password: `EvKXCC`
5. Linköping (0580) - Login: `BU2025_0580`, Password: `sJNSHc`
6. Örebro (1880) - Login: `BU2025_1880`, Password: `YyReAX`
7. Västerås (1980) - Login: `BU2025_1980`, Password: `HkHPYL`
8. Helsingborg (1283) - Login: `BU2025_1283`, Password: `bfwVX8`
9. Jönköping (0680) - Login: `BU2025_0680`, Password: `N5hWVF`
10. Norrköping (0581) - Login: `BU2025_0581`, Password: `BtCRgM`

**Export Format:** Excel or CSV  
**Save Location:** `apps/stats-server/src/seed-scripts/seed-data/14-indikator-survey/`  
**File Naming:** `indikator-2025-{municipality_code}-{municipality_name}.xlsx`

### Step 3: Expected Data Structure

**Sheet 1: Indicators**

| Indicator Code | Category   | Question (Swedish)                            | Percentage | Response Count |
| -------------- | ---------- | --------------------------------------------- | ---------- | -------------- |
| IND001         | Inflytande | Kan påverka innehåll och genomförande av stöd | 85.5%      | 450            |
| IND002         | Inflytande | Bestämmer när hjälp utförs                    | 78.3%      | 450            |
| ...            | ...        | ...                                           | ...        | ...            |

**Total rows:** 29 indicators per municipality

## Integration Plan

### Phase 1: Manual Collection (Current)

**Time:** 1-2 days  
**Scope:** Top 10 municipalities

**Steps:**

1. Login to Indikator.org for each municipality
2. Export data to Excel/CSV
3. Save to `seed-data/14-indikator-survey/`
4. Create seed script `14-seed-indikator-survey.ts`
5. Test with 10 municipalities

### Phase 2: Automated Collection (Future)

**Time:** 2-3 days  
**Scope:** All 290 municipalities

**Approach:**

1. Investigate API endpoints (if available)
2. Create automated scraper (Puppeteer/Playwright)
3. Batch collection script
4. Error handling and retry logic

### Phase 3: Real-time Integration (Future)

**Time:** 1-2 weeks  
**Scope:** Continuous updates

**Features:**

- Scheduled data refresh (quarterly/annual)
- Change detection and notifications
- Historical tracking
- API integration with Socialstyrelsen (if available)

## Database Schema

### Existing Tables

**`municipality_quality_summaries`** (current)

- Basic quality metrics
- Customer satisfaction percentages

### New Table (Proposed)

**`indikator_survey_results`**

```prisma
model IndikatorSurveyResult {
  id                String       @id @default(cuid())
  municipalityId    String
  municipality      Municipality @relation(fields: [municipalityId], references: [id])
  year              Int
  responseRate      Float?
  totalRespondents  Int?

  // 29 indicators (Float = percentage)
  ind01_influence_content        Float?
  ind02_influence_timing         Float?
  ind03_influence_help_needed    Float?
  // ... 26 more indicators

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@unique([municipalityId, year])
  @@index([year])
}
```

## Seed Script Template

**File:** `apps/stats-server/src/seed-scripts/14-seed-indikator-survey.ts`

```typescript
import { PrismaClient } from "@prisma/client";
import * as XLSX from "xlsx";
import * as fs from "fs";
import * as path from "path";

const prisma = new PrismaClient();

async function seedIndikatorSurvey() {
  const dataDir = path.join(__dirname, "seed-data", "14-indikator-survey");
  const files = fs.readdirSync(dataDir).filter((f) => f.endsWith(".xlsx"));

  for (const file of files) {
    const filePath = path.join(dataDir, file);
    const workbook = XLSX.readFile(filePath);
    const sheet = workbook.Sheets[workbook.SheetNames[0]];
    const data = XLSX.utils.sheet_to_json(sheet);

    // Extract municipality code from filename
    const match = file.match(/indikator-2025-(\d{4})-/);
    if (!match) continue;

    const municipalityCode = match[1];
    const municipality = await prisma.municipality.findFirst({
      where: { municipalityCode },
    });

    if (!municipality) {
      console.warn(`Municipality not found: ${municipalityCode}`);
      continue;
    }

    // Process indicators and insert into database
    // ... mapping logic ...
  }
}

seedIndikatorSurvey();
```

## Benefits

**For municipalities:**

- Detailed quality breakdown (29 indicators vs. 1-3 current)
- Year-over-year trend analysis
- Benchmark against other municipalities

**For providers:**

- More granular quality insights
- Better ranking accuracy
- Improved transparency

**For users:**

- More informed decisions
- Detailed quality comparisons
- Trust in data completeness

## Next Steps

1. **Manual collection** (Top 10 municipalities) - Start here
2. Create seed script `14-seed-indikator-survey.ts`
3. Test integration with database
4. Document findings
5. Plan automation (Phase 2)

## Resources

- **Login credentials:** `docs/docs-seo/04-data-integration/marketing-data/oppna-jamforelser-aldreundersokningar-2025-inloggningsuppgifter-indikator (1).csv`
- **User manual:** `docs/docs-seo/04-data-integration/marketing-data/oppna-jamforelser-aldreundersokningar-2025-manual-indikators-webbverktyg.pdf`
- **Web platform:** https://webreport.indikator.org/Survey.aspx
