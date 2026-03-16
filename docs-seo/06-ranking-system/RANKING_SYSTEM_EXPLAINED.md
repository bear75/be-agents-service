# CaireIndex Ranking System

## Overview

CaireIndex is the quality ranking system used to evaluate and compare home care providers (anordnare) and municipalities in Sweden. It uses a single score model with 8 weighted components.

## Quick Reference

| Type                           | Storage Location                                          | Example                 |
| ------------------------------ | --------------------------------------------------------- | ----------------------- |
| **Provider National Ranking**  | `Provider.caireIndex` + `Provider.caireIndexRank`         | Score: 72.5, Rank: #175 |
| **Provider Municipal Ranking** | `ProviderMunicipality.caireIndexRank`                     | Nacka #10               |
| **Municipality Ranking**       | `Municipality.caireIndex` + `Municipality.caireIndexRank` | Score: 68.3, Rank: #45  |
| **Historical Tracking**        | `ProviderScoreHistory`                                    | Yearly/monthly trends   |

**Key Point:** Providers do NOT need multiple municipalities to get national rankings. A provider with only ONE municipality presence can get a national ranking if they have any quality data.

---

## Architecture (January 2026)

### Single Score Model

The current system uses a **single score per provider** that is used for all rankings:

1. **ONE score per provider** - Stored on `Provider.caireIndex`
2. **National rank** - Stored on `Provider.caireIndexRank` (sorted by score across all providers)
3. **Municipality-specific rank** - Stored on `ProviderMunicipality.caireIndexRank` (sorted within each municipality)
4. **Same score for both** - The provider's CaireIndex score is the same whether viewing national or municipal ranking

### Key Files

| File                                                       | Purpose                      |
| ---------------------------------------------------------- | ---------------------------- |
| `apps/stats-server/src/services/ranking/RankingService.ts` | Score calculation logic      |
| `apps/stats-server/src/scripts/fix-rankings.ts`            | Ranking recalculation script |
| `apps/stats-server/schema.prisma`                          | Database schema              |

---

## Provider Score Components (8 Components)

The CaireIndex score is calculated from 8 components grouped into 4 categories:

### Quality (50% total)

| Component                 | Weight | Source                               | Description                                                  |
| ------------------------- | ------ | ------------------------------------ | ------------------------------------------------------------ |
| **Customer Satisfaction** | 30%    | `QualityMetric.customerSatisfaction` | Average satisfaction from Socialstyrelsen surveys (0-100)    |
| **Staff Continuity**      | 20%    | `QualityMetric.staffContinuity`      | Number of different staff per user, converted to 0-100 score |

### Expertise (20% total)

| Component           | Weight | Source                                   | Description                               |
| ------------------- | ------ | ---------------------------------------- | ----------------------------------------- |
| **Education Level** | 15%    | `Provider.ind32UnderskoterskeDagarAndel` | Percentage of staff with formal education |
| **Employee Scale**  | 5%     | `Provider.jensLastKnownEmployees`        | Number of employees, normalized to 0-100  |

### Financial Health (20% total)

| Component          | Weight | Source                               | Description                         |
| ------------------ | ------ | ------------------------------------ | ----------------------------------- |
| **Profit Margin**  | 10%    | `Provider.jensLastKnownProfitMargin` | Profitability indicator, normalized |
| **Revenue Growth** | 10%    | `Provider.jensInvoicedSum2022-2024`  | Year-over-year revenue growth       |

### Stability (10% total)

| Component            | Weight | Source                                   | Description                     |
| -------------------- | ------ | ---------------------------------------- | ------------------------------- |
| **Geographic Reach** | 5%     | `Provider.jensPresentInMunicipalities`   | Number of municipalities served |
| **Tax Compliance**   | 5%     | `Provider.jensHasFTax/HasVat/HasPayroll` | Tax registration compliance     |

### Score Formula

```
CaireIndex = (Brukarnöjdhet × 30%)
           + (Personalkontinuitet × 20%)
           + (Utbildningsnivå × 15%)
           + (Personalstyrka × 5%)
           + (Lönsamhet × 10%)
           + (Tillväxt × 10%)
           + (Geografisk spridning × 5%)
           + (Regelefterlevnad × 5%)
```

### Handling Missing Data

- If a component has no data, it receives **0 points** for that component
- This means providers with more complete data naturally score higher
- A "completeness" indicator (0-100%) shows how many of the 8 components have data
- All providers now receive a ranking (no score threshold requirement)

---

## Grading Scale

Providers and municipalities receive a letter grade based on their score:

| Grade  | Score Range | Description   |
| ------ | ----------- | ------------- |
| **A+** | >= 80       | Excellent     |
| **A**  | 70-79       | Very Good     |
| **B+** | 60-69       | Good          |
| **B**  | 50-59       | Above Average |
| **C**  | 40-49       | Average       |
| **D**  | < 40        | Below Average |

---

## Municipality Score Components

Municipalities are ranked using different components:

| Category        | Component                 | Weight | Source                                   |
| --------------- | ------------------------- | ------ | ---------------------------------------- |
| **Quality**     | Avg Customer Satisfaction | 35%    | `QualitySummary.avgCustomerSatisfaction` |
|                 | Avg Staff Continuity      | 25%    | `QualitySummary.avgStaffContinuity`      |
| **Economy**     | Financial Health          | 15%    | `Municipality.jensCashOnBankYearEndTkr`  |
|                 | Market Activity           | 10%    | Invoices per capita                      |
| **Development** | Population Growth         | 10%    | `Municipality.jensPopulationHistory`     |
|                 | Tax Competitiveness       | 5%     | `Municipality.jensTaxRateHistory`        |

### Municipality Formula

```
Municipality Score = (Brukarnöjdhet × 35%)
                   + (Personalkontinuitet × 25%)
                   + (Finansiell hälsa × 15%)
                   + (Marknadsaktivitet × 10%)
                   + (Befolkningstillväxt × 10%)
                   + (Skattkonkurrenskraft × 5%)
```

---

## Database Schema

### Provider Fields

```prisma
model Provider {
  caireIndex           Float?    // The calculated CaireIndex score (0-100)
  caireIndexRank       Int?      // National ranking position
  caireIndexGrade      String?   // Letter grade (A+, A, B+, B, C, D)
  caireIndexRankChange Int?      // Change since last calculation
  caireIndexComponents Json?     // Breakdown of score components
}
```

### ProviderMunicipality Fields

```prisma
model ProviderMunicipality {
  caireIndexRank       Int?      // Municipality-specific ranking position
  caireIndexRankChange Int?      // Change since last calculation
}
```

### Municipality Fields

```prisma
model Municipality {
  caireIndex           Float?    // The calculated CaireIndex score (0-100)
  caireIndexRank       Int?      // National ranking position
  caireIndexGrade      String?   // Letter grade
  caireIndexRankChange Int?      // Change since last calculation
  caireIndexComponents Json?     // Breakdown of score components
}
```

### Historical Tracking

```prisma
model ProviderScoreHistory {
  id            String   @id
  providerId    String
  period        String   // e.g., "2025", "2025-01"
  periodType    String   // "YEARLY" or "MONTHLY"
  score         Float
  nationalRank  Int?
  components    Json?
  scoreChange   Float?
  scoreChangePct Float?
  rankChange    Int?
  createdAt     DateTime
}
```

---

## Ranking Categories

Rankings are calculated for multiple categories:

| Category      | Description                        | Use                             |
| ------------- | ---------------------------------- | ------------------------------- |
| **TOTAL**     | Overall CaireIndex score           | Primary ranking displayed in UI |
| **QUALITY**   | Customer satisfaction + continuity | Quality sub-ranking             |
| **FINANCIAL** | Profit margin + revenue growth     | Financial health sub-ranking    |
| **STABILITY** | Geographic reach + compliance      | Stability sub-ranking           |

---

## How Rankings Work

### National Ranking Process

1. Calculate CaireIndex score for each provider by averaging quality metrics across all presences
2. Sort all providers by score (highest first)
3. Assign rank: 1st = highest score, 2nd = second highest, etc.
4. Store score on `Provider.caireIndex`, rank on `Provider.caireIndexRank`
5. Create `ProviderScoreHistory` entry for trend tracking

### Municipality Ranking Process

1. Group providers by municipality (via `ProviderMunicipality`)
2. Within each municipality, sort providers by their CaireIndex score
3. Assign municipality-specific rank: 1st = highest in that municipality
4. Store rank on `ProviderMunicipality.caireIndexRank`

### Key Point: Same Score, Different Ranks

A provider has ONE CaireIndex score but can have MULTIPLE ranks:

- National rank (e.g., #175 in Sweden)
- Municipality rank for each presence (e.g., #5 in Nacka, #12 in Stockholm)

---

## Running Rankings

### Recalculate All Rankings

```bash
yarn workspace stats-server tsx src/scripts/fix-rankings.ts
```

This script:

1. Calculates normalization statistics
2. Computes CaireIndex for all providers
3. Assigns national and municipality rankings
4. Updates municipality rankings
5. Creates historical tracking entries
6. Refreshes NationalStatistics aggregates

### When to Run

- After importing new quality data from Socialstyrelsen
- After importing new financial data from Kommun API
- After significant provider data updates
- Periodically (weekly/monthly) to keep rankings current

---

## Common Questions

### Q: Why does a provider have a low score?

**A:** Check the completeness indicator. If they're missing data for several components, those receive 0 points. For example, a provider with only satisfaction data (30% weight) will have a maximum possible score of 30.

### Q: Do providers need multiple municipalities for national ranking?

**A:** NO. A provider with only ONE municipality presence gets a national ranking if they have any quality data.

### Q: Why are two providers with the same score ranked differently?

**A:** When scores are tied, providers are sorted by ID (alphabetically) as a tiebreaker to ensure stable, consistent rankings.

### Q: How is staff continuity converted to a score?

**A:** The formula is: `Score = 100 - (persons - 10) × (100 / 15)`

- 10 persons = 100 points (best)
- 25+ persons = 0 points (worst)

### Q: What's the difference between caireIndex and caireIndexRank?

**A:**

- `caireIndex` = The actual score (0-100)
- `caireIndexRank` = The position when sorted by score (#1, #2, #3...)

---

## UI Integration

### Data Used in Frontend

The frontend pages (`packages/shared/seo/pages/`) display:

1. **Provider Lists:** Sorted by `caireIndex` score
2. **Rank Badges:** Show both national and municipal rank
3. **Score Display:** Shows CaireIndex score with grade
4. **Components:** Can show breakdown from `caireIndexComponents` JSON

### Key Shared Components

| Component               | Location                     | Purpose                     |
| ----------------------- | ---------------------------- | --------------------------- |
| `CaireIndexMethodology` | `packages/shared/seo/pages/` | Explains the scoring system |
| `RankingExplanation`    | `packages/shared/seo/pages/` | Explains ranking types      |
| `DataSources`           | `packages/shared/seo/pages/` | Lists data sources          |

---

## Code References

| File                                                       | Description                    |
| ---------------------------------------------------------- | ------------------------------ |
| `apps/stats-server/src/services/ranking/RankingService.ts` | Main ranking calculation logic |
| `apps/stats-server/src/scripts/fix-rankings.ts`            | Script to recalculate rankings |
| `apps/stats-server/schema.prisma`                          | Database schema definitions    |
| `packages/shared/seo/data/caireIndexMethodology.ts`        | UI constants for components    |
| `packages/shared/seo/pages/CaireIndexMethodology.tsx`      | Methodology explanation page   |

---

**Last Updated:** January 2026
