# How to Upload Attendo CSV

## Quick Start

```bash
cd apps/dashboard-server

# Step 1: Generate enriched CSV for REVIEW
npx tsx src/scripts/generate-expanded-csv.ts

# Step 2: Review the enriched CSV
open expanded-csv/visits-enriched.csv

# Step 3: If satisfied, upload the ORIGINAL Attendo CSV via seed script
yarn db:seed:attendo
```

## What Each File Does

### 1. Enriched CSV (`visits-enriched.csv`)

**Purpose:** Preview and verify what will be created

**Contains:**

- All original Attendo columns (Slinga, När på dagen, Skift, Dubbel, etc.)
- Plus expansion fields (templateRowId, date, dependencies embedded)
- 3,793 expanded visits (from 664 templates)
- All dependencies visible in each row

**Use this to:**

- ✅ Review expanded visits before upload
- ✅ Check dependencies are correct
- ✅ Verify time slots, shifts, and descriptions
- ✅ See double-staffing groups (Dubbel column)
- ✅ Trace back to original CSV row (templateRowId)

**Do NOT use for:** Uploading to database (use original CSV instead)

### 2. Original Attendo CSV

**Location:** `~/HomeCare/be-agent-service/.../Huddinge-v3 - Data_final.csv`

**Purpose:** Upload to database

**Use the seed script:**

```bash
yarn db:seed:attendo
```

This will:

1. Create/find the Attendo organization
2. Import the CSV using `importAttendoSchedule()`
3. Expand recurrence patterns
4. Create dependencies
5. Generate the schedule

## File Locations

**Enriched CSV (for review):**

```
apps/dashboard-server/expanded-csv/
├── visits-enriched.csv     ⭐ Main file - all info in one place
├── clients.csv             (reference)
├── employees.csv           (reference)
├── dependencies.csv        (reference)
└── SUMMARY.md
```

**Original CSV (for upload):**

```
~/HomeCare/be-agent-service/recurring-visits/huddinge-package/
  huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/
  Huddinge-v3 - Data_final.csv
```

## Workflow

1. **Generate enriched CSV** - Preview what will be created

   ```bash
   npx tsx src/scripts/generate-expanded-csv.ts
   ```

2. **Review in Excel/Sheets** - Check all fields are correct

   ```bash
   open expanded-csv/visits-enriched.csv
   ```

3. **Upload original CSV** - Import to database

   ```bash
   yarn db:seed:attendo
   ```

4. **Verify in database** - Check the data was imported correctly
   ```sql
   SELECT COUNT(*) FROM "Visit" WHERE "scheduleId" = '[schedule-id]';
   SELECT COUNT(*) FROM "VisitDependency" WHERE "scheduleId" = '[schedule-id]';
   ```

## Why Two Files?

The enriched CSV shows you EXACTLY what the original CSV will produce when uploaded. It's like a "dry run" or preview.

Think of it like:

- **Enriched CSV** = Preview/Report
- **Original CSV** = Source of truth for upload

## Troubleshooting

### "Where do I upload the enriched CSV?"

You don't! Use it for review only. Upload the original Attendo CSV instead.

### "How do I upload via the dashboard wizard?"

Not yet implemented. Use the seed script for now:

```bash
yarn db:seed:attendo
```

### "Can I upload the enriched CSV programmatically?"

Yes, but it's incomplete. The `importFromEnrichedCsv()` function exists but needs more work to match all the logic in `importAttendoSchedule()`. For now, use the original CSV.
