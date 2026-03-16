# Duplicate Provider Prevention Analysis

> **Date:** 2026-01-08
> **Status:** ✅ Master verification script created

## Problem: Varför skapas duplicerade providers?

Duplicerade providers skapas på **tre sätt** i seed-processen:

### 1. **Seed Step 2 (JSON) + Seed Step 3 (CSV) = Duplicates**

**Root Cause:**

- **Step 2** (`02-seed-municipalities.ts`): Skapar providers från JSON-filer (Stockholm, Nacka test data)
- **Step 3** (`03-seed-providers-unified.ts`): Skapar providers från Socialstyrelsen CSV
- **Problem:** Step 3 skippar pilot municipalities men kan INTE matcha providers som redan finns från step 2

**Exempel:**

```
Step 2: Skapar "Nova Omsorg Stockholm AB" (från stockholm.json)
        - orgNumber: null (JSON saknar orgNumber)
        - slug: "nova-omsorg-stockholm-ab"

Step 3: Skapar "Nova Omsorg Stockholm AB" (från Socialstyrelsen CSV)
        - orgNumber: "5568123456" (från mapping file)
        - slug: "nova-omsorg-stockholm-ab-0180" (ny slug p.g.a. collision)

RESULTAT: 2 providers med samma namn men olika slugs!
```

**Matchningslogik i Step 3 (lines 627-677):**

1. ✅ Försöker matcha på real orgNumber (inte MUN/PRV)
2. ✅ Försöker matcha på name+legalName+orgType
3. ✅ Försöker matcha på slug
4. ❌ **MEN**: Pilot municipalities skippas INNAN matching (line 525-528)!

### 2. **Auto-generated orgNumbers (MUN/PRV prefix)**

**Root Cause:**

- När mapping file saknar orgNumber, genereras auto-generated orgNumber: `MUN{code}-{hash}` eller `PRV{code}-{hash}`
- Dessa är **deterministiska** men kan ändå skapa duplicates om samma provider seedas från olika källor

**Exempel:**

```
Source 1: stockholm.json
  - name: "Stockholms stad hemtjänst"
  - orgNumber: null
  - Generated: MUN0180-stoc000123

Source 2: Socialstyrelsen CSV
  - name: "Stockholms stad hemtjänst"
  - orgNumber: null (inte i mapping)
  - Generated: MUN0180-stoc000123 (samma!)

MEN: Olika källfiler kan ha slight variations i namn:
  - "Stockholms stad hemtjänst" vs "Stockholm stad Hemtjänst"
  - Genererar olika hash → olika orgNumber → DUPLICATE!
```

### 3. **Multiple Seed Runs Without Proper Deduplication**

**Root Cause:**

- Om `db:seed` körs flera gånger utan att rensa databasen, kan providers skapas flera gånger
- Upsert-logiken fungerar bara om matching är perfekt (orgNumber, name, slug)

**Exempel:**

```
Run 1: Skapar "Hemtjänsten Nord AB" (orgNumber: PRV0180-hemt000456)
Run 2: CSV har slight skillnad i namn: "Hemtjänsten Nord AB " (extra space)
       - Matchar INTE på name (case-insensitive men inte trim)
       - Skapar ny provider: "hemtjansten-nord-ab-0180-2"
```

---

## Lösning: Master Verification Script

Skapade **ETT** omfattande verifieringsskript:

### `00-verify-database-integrity.ts`

**Checks performed:**

1. ✅ **Duplicate Providers by orgNumber** - Hittar providers med samma orgNumber
2. ✅ **Duplicate Providers by Name** - Hittar providers med samma namn (men olika/auto orgNumbers)
3. ✅ **Duplicate Slugs** - Hittar UNIQUE constraint violations
4. ✅ **Orphaned Records** - Financials, rankings, presences, quality metrics utan valid provider
5. ✅ **Missing Critical Data** - Providers utan orgNumber, presences, rankings
6. ✅ **Rankings Consistency** - Providers ska ha BÅDE kommun och national rankings
7. ✅ **Expected Record Counts** - Providers (1800-2200), Municipalities (290), etc.
8. ✅ **National Statistics Accuracy** - Verifierar att stats matchar faktiska counts

**Run with:**

```bash
yarn workspace stats-server db:verify
```

**Output example:**

```
🔍 Check 1: Duplicate Providers by orgNumber...
   ❌ 5568123456: 2 duplicates
      🎯 KEEP? [nova-omsorg-stockholm-ab] Nova Omsorg Stockholm AB - 15 presences, 4 rankings
      ❌ DELETE? [nova-omsorg-stockholm-ab-0180] Nova Omsorg Stockholm AB - 0 presences, 0 rankings

📊 VERIFICATION SUMMARY
❌ CRITICAL ISSUES (3):
1. [DUPLICATES] Found 15 org numbers with duplicate providers
2. [INTEGRITY] Found 5+ orphaned financial records
3. [DUPLICATES] Found 8 provider names with duplicate records

🔧 RECOMMENDED ACTIONS:
1. Fix duplicate providers:
   yarn workspace stats-server tsx src/scripts/find-and-merge-duplicates.ts
   yarn workspace stats-server tsx src/seed-scripts/batch-merge-duplicates.ts

2. Clean up orphaned records:
   yarn workspace stats-server db:seed:18-sync-provider-rows
   yarn workspace stats-server db:seed:19-sync-counts
```

---

## Förbättringar i Seed Scripts

### 1. **Förbättra Step 3 Matching (REKOMMENDERAT)**

**Problem:** Step 3 skippar pilot municipalities INNAN matching körs.

**Lösning:** Matcha FÖRST, SEDAN skippa om match redan finns från JSON:

```typescript
// I 03-seed-providers-unified.ts, line ~505

// FÖRE (skippar för tidigt):
if (pilotMunicipalityIds.has(municipality.id)) {
  skippedPilotMunicipality++;
  continue; // ❌ Skippar INNAN matching!
}

// EFTER (matcha först):
// Check if provider exists (match by orgNumber, name, slug)
let existing = null;
// ... (matching logic) ...

if (existing) {
  // Provider already exists (from JSON or previous CSV run)
  if (pilotMunicipalityIds.has(municipality.id)) {
    // Skip updating pilot municipality providers (use JSON as source of truth)
    skippedPilotMunicipality++;
    continue;
  }
  // Update non-pilot providers
  await prismaSeo.provider.update({ ... });
} else {
  // Create new provider (no existing match)
  if (pilotMunicipalityIds.has(municipality.id)) {
    // Skip creating in pilot municipalities (JSON is source of truth)
    skippedPilotMunicipality++;
    continue;
  }
  await prismaSeo.provider.create({ ... });
}
```

### 2. **Förbättra Name Matching (REKOMMENDERAT)**

**Problem:** Name matching är case-insensitive men inte trim-safe.

**Lösning:** Normalisera namn INNAN matching:

```typescript
// Add normalize function
function normalizeName(name: string): string {
  return name
    .toLowerCase()
    .trim()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "") // Remove diacritics
    .replace(/\s+/g, " ") // Normalize whitespace
    .replace(/[^a-z0-9\s]/g, ""); // Remove special chars
}

// Use in matching
const normalizedName = normalizeName(row.enhetsNamn);
existing = await prismaSeo.provider.findFirst({
  where: {
    name: { equals: normalizedName, mode: "insensitive" },
    orgType: { in: ["MUNICIPAL", "UNKNOWN"] },
  },
});
```

### 3. **Add orgNumber to JSON Files (RECOMMENDED)**

**Problem:** JSON files saknar orgNumbers, vilket gör matching svår.

**Lösning:** Lägg till orgNumbers i JSON files (stockholm.json, nacka.json):

```json
{
  "name": "Nova Omsorg Stockholm AB",
  "orgNumber": "5568123456", // ✅ ADD THIS
  "legalName": "Nova Omsorg Stockholm AB",
  "orgType": "PRIVATE"
}
```

**Benefits:**

- Perfect matching mellan JSON (step 2) och CSV (step 3)
- Inga auto-generated orgNumbers för pilot municipalities
- Inga duplicates!

---

## Workflow: How to Use Verification Script

### 1. **After Every Seed**

```bash
# Seed database
yarn workspace stats-server db:seed

# Verify integrity
yarn workspace stats-server db:verify

# If errors found:
# - Fix duplicates (merge or delete)
# - Sync counts
# - Verify again
```

### 2. **Before Deployment**

```bash
# Quick reset (from snapshot)
yarn workspace stats-server db:quick-reset

# Verify integrity
yarn workspace stats-server db:verify

# Should show ✅ ALL CHECKS PASSED
```

### 3. **Fix Duplicates If Found**

```bash
# 1. Find duplicates
yarn workspace stats-server tsx src/scripts/find-and-merge-duplicates.ts

# 2. Merge duplicates (if confident)
yarn workspace stats-server tsx src/seed-scripts/batch-merge-duplicates.ts

# 3. Sync counts
yarn workspace stats-server db:seed:19-sync-counts

# 4. Verify again
yarn workspace stats-server db:verify
```

---

## Summary

### Root Causes of Duplicates:

1. ❌ JSON (step 2) + CSV (step 3) = Duplicates (olika sources, samma providers)
2. ❌ Auto-generated orgNumbers (MUN/PRV) = Duplicates (slight name variations)
3. ❌ Multiple seed runs = Duplicates (imperfect matching)

### Solution:

✅ **ONE** master verification script: `00-verify-database-integrity.ts`

- Run with: `yarn workspace stats-server db:verify`
- Checks: duplicates, orphans, missing data, rankings, counts, stats
- Provides: actionable recommendations

### Recommended Improvements:

1. ✅ Förbättra Step 3 matching logic (matcha FÖRST, skippa SEDAN)
2. ✅ Normalisera namn INNAN matching (trim, lowercase, remove diacritics)
3. ✅ Lägg till orgNumbers i JSON files (stockholm.json, nacka.json)

### Workflow:

```bash
db:seed → db:verify → (fix if needed) → db:verify again → ✅ deploy
```

**Resultat:** Zero duplicates, clean database, confident deployment! 🚀
