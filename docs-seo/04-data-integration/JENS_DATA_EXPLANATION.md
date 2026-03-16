# Jens Data vs Provider Financials - Förklaring

## Problem: Varför saknas data i provider_financials trots att Jens-data finns?

### Kort svar:

**Jens-data lagras i JSON-fält på Provider-tabellen, men konverteras INTE automatiskt till strukturerade `provider_financials` records.**

---

## Dataflöde och Struktur

### 1. Jens Nylander Data (Rådata - JSON)

**Var lagras:** Direkt på `providers` tabellen som JSON-fält

```typescript
// Provider-tabellen har dessa JSON-fält:
jensFinancialSummary: JSON; // [{turnover, profitMargin, numberOfEmployees, period...}]
jensInvoicedPerMunicipality: JSON; // [{name, slug, invoicedSum_2022, invoicedSum_2023...}]
jensInvoicedPerPeriod: JSON; // Månadsvis fakturering
```

**Exempel på `jensFinancialSummary`:**

```json
[
  {
    "turnover": 0,
    "profitMargin": 0,
    "periodFormattted": "2019-12",
    "numberOfEmployees": null,
    "annualReportPeriod": 201912,
    "resultAfterFinancialItems": -36
  },
  {
    "turnover": 21469,
    "profitMargin": 19.2549,
    "periodFormattted": "2021-12",
    "numberOfEmployees": 37,
    "annualReportPeriod": 202112,
    "resultAfterFinancialItems": 4185
  }
]
```

**Exempel på `jensInvoicedPerMunicipality`:**

```json
[
  {
    "name": "Järfälla",
    "slug": "jarfalla",
    "invoicedSum_2022": 4505052.98,
    "invoicedSum_2023": 7112508.99,
    "invoicedSum_2024": 0,
    "vendorOrganizationNumber": "5591798995"
  }
]
```

**När fylls detta:** När `enrich-providers.ts` scriptet körs och matchar providers med Jens Nylander scraped data.

---

### 2. Provider Financials Tabell (Strukturerad Data)

**Var lagras:** I `provider_financials` tabellen (separat tabell)

```sql
CREATE TABLE provider_financials (
  id TEXT PRIMARY KEY,
  providerId TEXT,
  year INT,
  revenueSek BIGINT,
  profitSek BIGINT,
  employeeCount INT,
  source SourceType,  -- BRANSCHRAPPORT, JENS_KOMMUN_API, TIC_IO, etc.
  ...
)
```

**När fylls detta:**

- **Från Branschrapport:** När Branschrapport-data seedas
- **Från TIC.io:** När TIC-data seedas
- **Från Jens:** **Saknas för närvarande!** Det finns INGET script som konverterar `jensFinancialSummary` JSON till `provider_financials` records.

---

### 3. Provider Monthly Invoices Tabell

**Var lagras:** I `provider_monthly_invoices` tabellen

```sql
CREATE TABLE provider_monthly_invoices (
  id TEXT PRIMARY KEY,
  providerId TEXT,
  year INT,
  month INT,
  period INT,  -- YYYYMM format
  amountSek BIGINT,
  source SourceType,
  ...
)
```

**När fylls detta:** **Saknas för närvarande!** Det finns INGET script som konverterar `jensInvoicedPerPeriod` JSON till `provider_monthly_invoices` records.

---

### 4. Provider Municipality Invoices Tabell

**Var lagras:** I `provider_municipality_invoices` tabellen

```sql
CREATE TABLE provider_municipality_invoices (
  id TEXT PRIMARY KEY,
  providerId TEXT,
  municipalityId TEXT,
  municipalityName TEXT,
  year INT,
  invoicedSumSek BIGINT,
  source SourceType,
  ...
)
```

**När fylls detta:** **Saknas för närvarande!** Det finns INGET script som konverterar `jensInvoicedPerMunicipality` JSON till `provider_municipality_invoices` records.

---

## Varför Saknas Data i provider_financials?

### Problemet:

1. ✅ Jens-data scrapas och lagras i JSON-fält på Provider-tabellen
2. ❌ **INGET script konverterar JSON-data till strukturerade tabeller**
3. ❌ Frontend koden försöker läsa från `provider_financials` tabellen
4. ❌ Tabellen är tom för de flesta providers (bara 227 providers har data från Branschrapport)

### Lösningen (som redan implementerats):

Frontend koden använder nu **fallback till Jens JSON-fält** när `provider_financials` saknas:

```typescript
// I TopListsProviders.tsx
employeeCount: latestFinancials?.employeeCount || jensEmployees,
revenue: latestFinancials?.revenueSek || jensTurnoverSek,
```

---

## Vad Borde Skapas (Framtida Förbättring)

### Script: `process-jens-financials.ts`

Detta script skulle:

1. Läsa `jensFinancialSummary` JSON från alla providers
2. Konvertera varje år till en `ProviderFinancials` record
3. Spara med `source: JENS_KOMMUN_API`

**Exempel:**

```typescript
// För varje provider med jensFinancialSummary:
for (const yearData of jensFinancialSummary) {
  await prisma.providerFinancials.upsert({
    where: {
      providerId_year_source: {
        providerId: provider.id,
        year: yearData.annualReportPeriod / 100, // 202112 -> 2021
        source: "JENS_KOMMUN_API",
      },
    },
    create: {
      providerId: provider.id,
      year: yearData.annualReportPeriod / 100,
      revenueSek: yearData.turnover * 1000, // Convert TSEK to SEK
      employeeCount: yearData.numberOfEmployees,
      profitMarginPct: yearData.profitMargin,
      source: "JENS_KOMMUN_API",
    },
    update: {
      /* ... */
    },
  });
}
```

### Script: `process-jens-invoices.ts`

Detta script skulle:

1. Läsa `jensInvoicedPerMunicipality` JSON
2. Skapa `ProviderMunicipalityInvoice` records
3. Läsa `jensInvoicedPerPeriod` JSON
4. Skapa `ProviderMonthlyInvoice` records

---

## Sammanfattning

| Data                             | Var Lagras                                     | Strukturerad? | Används i Frontend?         |
| -------------------------------- | ---------------------------------------------- | ------------- | --------------------------- |
| `jensFinancialSummary`           | `providers.jensFinancialSummary` (JSON)        | ❌ Nej        | ✅ Ja (via fallback)        |
| `jensInvoicedPerMunicipality`    | `providers.jensInvoicedPerMunicipality` (JSON) | ❌ Nej        | ❌ Nej (inte implementerat) |
| `jensInvoicedPerPeriod`          | `providers.jensInvoicedPerPeriod` (JSON)       | ❌ Nej        | ❌ Nej (inte implementerat) |
| `provider_financials`            | Separat tabell                                 | ✅ Ja         | ✅ Ja (primär källa)        |
| `provider_monthly_invoices`      | Separat tabell                                 | ✅ Ja         | ❌ Nej (inte används)       |
| `provider_municipality_invoices` | Separat tabell                                 | ✅ Ja         | ❌ Nej (inte används)       |

**Nuvarande Status:**

- ✅ Jens-data finns i JSON-fält
- ✅ Frontend använder Jens-data som fallback
- ❌ Ingen automatisk konvertering till strukturerade tabeller
- ❌ Många providers saknar data i `provider_financials` (bara 227 av 1,581)

**Rekommendation:**
Skapa scripts som konverterar Jens JSON-data till strukturerade tabeller för bättre query-prestanda och konsistens.
