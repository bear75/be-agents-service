# Expanded CSV Format - Usage Guide

**Generated**: 2026-03-16
**Status**: ✅ Working - Generated from Huddinge v3 CSV

---

## Overview

The **Expanded CSV Format** is a normalized, pre-processed version of the Attendo CSV where:

- All recurrence patterns are expanded into individual visits
- All dependencies are explicitly listed
- All dates are in ISO format
- All durations are in ISO 8601 format

This format serves as **clean input** before importing to the database.

## Why Use Expanded CSV?

**Benefits:**

1. ✅ **Verify Before Import** - Review all expanded visits before upload
2. ✅ **No Recurrence Logic** - All visits already expanded, no runtime calculation
3. ✅ **Explicit Dependencies** - See exactly which visits are related
4. ✅ **Clean Data** - Normalized time slots, insets, durations
5. ✅ **Faster Upload** - No complex parsing during import

**Trade-offs:**

- ❌ Larger file sizes (3,793 visits vs 664 templates)
- ❌ Fixed planning window (must regenerate for different dates)

---

## Generated Files

From Huddinge v3 CSV (`Huddinge-v3 - Data_final.csv`):

| File               | Rows  | Description                                         |
| ------------------ | ----- | --------------------------------------------------- |
| `clients.csv`      | 115   | Client master data with addresses                   |
| `employees.csv`    | 0     | Employee data (extracted from visits during import) |
| `visits.csv`       | 3,793 | All expanded visits (from 664 templates)            |
| `dependencies.csv` | 573   | Visit-to-visit temporal dependencies                |
| `SUMMARY.md`       | -     | Statistics and verification queries                 |

---

## File Formats

### 1. clients.csv

**Columns:**

- `externalId` - Client ID (e.g., "H015")
- `name` - Client full name
- `street` - Street address
- `postalCode` - Postal code
- `city` - City name
- `latitude` - GPS latitude (empty if not available)
- `longitude` - GPS longitude (empty if not available)
- `serviceAreaId` - Service area ID (empty for auto-assignment)

**Example:**

```csv
externalId,name,street,postalCode,city,latitude,longitude,serviceAreaId
H015,Peter Andersson,Ängsnäsvägen 6,14146,HUDDINGE,59.2334527,17.9911485,
H025,Maria Svensson,Storgatan 12,14100,HUDDINGE,59.2368,17.9942,
```

### 2. employees.csv

**Columns:**

- `externalId` - Employee/shift ID (e.g., "Dag 01 Central 1")
- `firstName` - First name (extracted from externalId)
- `lastName` - Last name (extracted from externalId)
- `weekday` - Day of week (Monday, Tuesday, etc.)
- `startTime` - Shift start time (HH:MM)
- `endTime` - Shift end time (HH:MM)
- `shiftType` - Shift type (day, evening, weekend)
- `breakDurationMinutes` - Break duration
- `breakMinStart` - Earliest break start time
- `breakMaxEnd` - Latest break end time

**Note:** Currently empty because `attendoToCaire()` doesn't extract employee data from Attendo CSV. Employees are created during import from visit assignments.

### 3. visits.csv

**Columns:**

- `externalId` - Unique visit ID (e.g., "H015_2026-03-16_1")
- `clientExternalId` - Client ID reference
- `date` - Visit date (YYYY-MM-DD)
- `durationMinutes` - Visit duration in minutes
- `startTime` - Preferred start time (HH:MM, empty if flexible)
- `timeSlot` - Canonical time slot (morgon, lunch, kväll, heldag)
- `flexBeforeMinutes` - Minutes visit can start before preferred time
- `flexAfterMinutes` - Minutes visit can start after preferred time
- `insets` - Services/insets (semicolon-separated, e.g., "supervision;meal")
- `groupId` - Group ID for double-staffing (empty if none)
- `priority` - Priority 1-10 (higher = more important)
- `isCritical` - Whether visit is critical (true/false)

**Example:**

```csv
externalId,clientExternalId,date,durationMinutes,startTime,timeSlot,flexBeforeMinutes,flexAfterMinutes,insets,groupId,priority,isCritical
H015_2026-03-16_1,H015,2026-03-16,6,07:05,morgon,0,120,supervision,,5,false
H015_2026-03-16_4,H015,2026-03-16,6,13:30,lunch,60,90,supervision,,5,false
H015_2026-03-16_7,H015,2026-03-16,20,18:00,kväll,0,120,meal;medication,,5,false
```

**External ID Format:** `{ClientID}_{Date}_{SequenceNumber}`

- Client ID: Original Kundnr from CSV
- Date: ISO format (YYYY-MM-DD)
- Sequence: Auto-incremented per client per day (starts at 0)

### 4. dependencies.csv

**Columns:**

- `precedingVisitExternalId` - Visit that must happen first
- `succeedingVisitExternalId` - Visit that must happen after
- `minDelay` - Minimum delay (ISO 8601, e.g., "PT3H30M" = 3.5 hours)
- `maxDelay` - Maximum delay (empty = no max)
- `dependencyType` - Type: `same_day`, `spread`, `temporal`

**Example:**

```csv
precedingVisitExternalId,succeedingVisitExternalId,minDelay,maxDelay,dependencyType
H025_2026-03-16_8,H025_2026-03-16_10,PT3H30M,,same_day
H025_2026-03-16_10,H025_2026-03-16_12,PT3H30M,,same_day
```

**Dependency Types:**

- **same_day**: Visits on same date must be separated by minDelay (e.g., breakfast → lunch)
- **spread**: Visit chain across different days (e.g., Monday → Tuesday)
- **temporal**: Custom time-based constraint

---

## How to Generate

**Script:** `apps/dashboard-server/src/scripts/generate-expanded-csv.ts`

**Usage:**

```bash
cd apps/dashboard-server

# Use default input/output
npx tsx src/scripts/generate-expanded-csv.ts

# Custom input CSV
npx tsx src/scripts/generate-expanded-csv.ts \
  ~/path/to/Attendo.csv \
  ./my-output-dir

# Default input: ~/HomeCare/be-agent-service/.../Huddinge-v3 - Data_final.csv
# Default output: ./expanded-csv/
```

**Planning Window:**

- Default: 2026-03-16 for 14 days
- To change: Edit script (lines 55-56)

**Output:**

```
📂 expanded-csv/
  ├── clients.csv          (115 clients)
  ├── employees.csv        (0 employees - extracted from visits)
  ├── visits.csv           (3,793 visits)
  ├── dependencies.csv     (573 dependencies)
  └── SUMMARY.md           (Statistics and verification)
```

---

## Statistics (Huddinge v3 CSV, 14 days)

| Metric                | Count |
| --------------------- | ----- |
| **Input CSV rows**    | 664   |
| **Clients**           | 115   |
| **Visit Templates**   | 664   |
| **Visits (expanded)** | 3,793 |
| **Dependencies**      | 573   |
| - Same-day (< 12h)    | 239   |
| - Cross-day (≥ 18h)   | 334   |

**Expansion Ratio:** 5.7x (664 templates → 3,793 visits)

**Dependency Coverage:** 15% of visits have dependencies (573 deps / 3,793 visits)

---

## How to Use Expanded CSV

### Option A: Upload via Dashboard (Recommended)

**Not yet implemented** - Dashboard wizard needs update to accept expanded CSV format.

**Future flow:**

1. Generate expanded CSV
2. Upload `visits.csv` via dashboard wizard
3. Dashboard detects expanded format
4. Skips recurrence expansion (already done)
5. Creates schedule with all visits and dependencies

### Option B: Import Programmatically (Current)

**Current workaround:** Use the original Attendo CSV with current upload flow, which handles expansion internally.

**Future:** Create `importFromExpandedCsv()` helper that:

1. Reads all 4 CSV files
2. Creates schedule
3. Upserts clients from `clients.csv`
4. Creates visits from `visits.csv`
5. Creates dependencies from `dependencies.csv`

### Option C: Verify Before Upload

**Use case:** Review expanded data before committing to database.

**Steps:**

1. Generate expanded CSV
2. Open `visits.csv` in Excel/Sheets
3. Review expanded visits, check dates/times
4. Open `dependencies.csv`, verify relationships
5. Check `SUMMARY.md` for statistics
6. If correct, proceed with upload

---

## Verification

After upload (via any method), verify in database:

### 1. Check Visit Count

```sql
SELECT COUNT(*) FROM "Visit" WHERE "scheduleId" = '[schedule-id]';
-- Expected: ~3,793
```

### 2. Check Dependency Count

```sql
SELECT COUNT(*) FROM "VisitDependency" WHERE "scheduleId" = '[schedule-id]';
-- Expected: ~573
```

### 3. Check Dependency Types

```sql
SELECT dependencyType, COUNT(*) as count
FROM "VisitDependency"
WHERE "scheduleId" = '[schedule-id]'
GROUP BY dependencyType;
-- Expected:
--   same_day: 239
--   spread: 334
```

### 4. Verify Same-Day Dependencies

```sql
-- All same_day dependencies should be on same date
SELECT
  d.id,
  p.date as preceding_date,
  s.date as succeeding_date
FROM "VisitDependency" d
JOIN "Visit" p ON d."precedingVisitId" = p.id
JOIN "Visit" s ON d."succeedingVisitId" = s.id
WHERE d."scheduleId" = '[schedule-id]'
  AND d."dependencyType" = 'same_day'
  AND p.date != s.date;
-- Expected: 0 rows
```

### 5. Verify Cross-Day Dependencies

```sql
-- All spread dependencies should be across different dates
SELECT
  d.id,
  p.date as preceding_date,
  s.date as succeeding_date
FROM "VisitDependency" d
JOIN "Visit" p ON d."precedingVisitId" = p.id
JOIN "Visit" s ON d."succeedingVisitId" = s.id
WHERE d."scheduleId" = '[schedule-id]'
  AND d."dependencyType" = 'spread'
  AND p.date >= s.date;
-- Expected: 0 rows
```

---

## Troubleshooting

### Issue: employees.csv is empty

**Expected behavior** - Employee data is not extracted from Attendo CSV format. Employees are created during import from visit assignments (the "Slinga" column values).

**Future:** Update script to parse employee shifts from Attendo CSV.

### Issue: Dependency count lower than expected

**Expected behavior** - Only clients with spread delays ("Antal tim mellan besöken") get dependencies. Not all 115 clients have spread delays specified.

**Statistics:**

- Clients with spread delay: ~40-50
- Total dependencies: 573
- This is correct based on CSV data

### Issue: Wrong planning window

**Solution:** Edit script to change `scheduleStartDate` and `scheduleDays` (lines 55-56):

```typescript
const scheduleStartDate = new Date("2026-03-16"); // Change this
const scheduleDays = 14; // Change this
```

Regenerate expanded CSV.

### Issue: Visit external IDs don't match database

**Expected behavior** - External IDs are generated during expansion and may differ from Attendo CSV row numbers.

**Format:** `{ClientID}_{Date}_{Sequence}`

**Example:** `H015_2026-03-16_1` = Client H015, March 16, sequence 1

---

## Next Steps

1. ✅ **Generated** - Expanded CSV files created
2. ⏳ **Review** - Verify visits.csv and dependencies.csv are correct
3. ⏳ **Import** - Create `importFromExpandedCsv()` helper
4. ⏳ **Dashboard** - Update wizard to accept expanded CSV format
5. ⏳ **Test** - Upload and verify in database

---

## Related Documentation

- `UPLOAD_ZONE_STATUS.md` - Overall upload zone implementation status
- `DEPENDENCY_CREATION_VERIFICATION.md` - Dependency creation guide
- `CAIRE_MIDDLE_CSV_FORMAT.md` - Middle format specification
- `MIDDLE_CSV_FORMAT_PLAN.md` - Plan for offline preprocessing

---

## File Locations

**Generator Script:**

```
apps/dashboard-server/src/scripts/generate-expanded-csv.ts
```

**Output Directory (default):**

```
apps/dashboard-server/expanded-csv/
  ├── clients.csv
  ├── employees.csv (empty - extracted from visits)
  ├── visits.csv
  ├── dependencies.csv
  └── SUMMARY.md
```

**Input CSV (default):**

```
~/HomeCare/be-agent-service/recurring-visits/huddinge-package/
  huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/
  Huddinge-v3 - Data_final.csv
```
