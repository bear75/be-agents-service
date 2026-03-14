# Script Locations Reference - Schedule Research

**Last Updated**: 2026-03-14

## TL;DR - What to Use for Research

For the **Schedule Research Loop**, use scripts from **THREE locations**:

### 1. Conversion (CSV → FSR)
**USE**: `/recurring-visits/huddinge-package/huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py`

**Why**: This is the **active v3 conversion script** (last modified Mar 13 17:30) specifically for Huddinge v3 data with all the fixes (PT0M dependencies, time windows, etc.)

**NOT**: `/scripts/timefold/conversion/csv_to_fsr.py` (consolidated version from Mar 14 15:10 - different MD5, possibly out of sync)

### 2. Submission & Fetching
**USE**: `/recurring-visits/scripts/submit_to_timefold.py`

**Why**: This is the **working submission script** that agents currently use.

**Alternative**: `/scripts/timefold/submission/submit_solve.py` (consolidated, may work but not tested in research loop yet)

### 3. Analysis & Metrics
**USE**: `/recurring-visits/scripts/metrics.py` and `/recurring-visits/scripts/continuity_report.py`

**Why**: These are the **proven analysis scripts** used in v3 campaigns.

**Alternative**: `/scripts/timefold/analysis/` (consolidated versions exist but may differ)

---

## Directory Structure

### `/scripts/timefold/` (Consolidated - Partially Complete)

**Status**: Consolidation started but **NOT all scripts migrated** yet.

**What exists**:
```
scripts/timefold/
├── conversion/
│   ├── csv_to_fsr.py         ✅ Exists (but different from attendo_4mars_to_fsr.py!)
│   └── expand_recurring_visits.py  ❌ Missing
├── submission/
│   ├── submit_solve.py       ✅ Exists
│   └── fetch_solution.py     ✅ Exists
├── analysis/
│   ├── metrics.py            ✅ Exists
│   ├── continuity_report.py  ✅ Exists
│   ├── analyze_unassigned.py ✅ Exists
│   └── analyze_empty_shifts.py ✅ Exists
├── continuity/
│   ├── build_pools.py        ✅ Exists
│   └── build_from_patch.py   ✅ Exists
├── utils/
│   ├── anonymize.py          ✅ Exists
│   └── register_run.py       ✅ Exists
├── campaigns/               ❌ Empty
├── repair/                  ❌ Empty
└── monitoring/              ❌ Empty
```

**What's missing**: 40+ scripts from `recurring-visits/scripts/` not yet migrated.

---

### `/recurring-visits/scripts/` (Active Legacy Location)

**Status**: **ACTIVE** - Contains 50+ Python scripts still in use.

**Key scripts**:
- `submit_to_timefold.py` - **Primary submission script** ✅
- `fetch_timefold_solution.py` - Fetch solutions ✅
- `metrics.py` - Calculate routing metrics ✅
- `continuity_report.py` - Generate continuity reports ✅
- `build_continuity_pools.py` - Build continuity pools ✅
- `build_from_patch.py` - Build from-patch payloads ✅
- `analyze_*.py` - Various analysis scripts ✅

**Usage**: Research loop agents (`timefold-specialist.sh`) currently call scripts from HERE.

---

### `/recurring-visits/huddinge-package/huddinge-4mars-csv/scripts/` (v3 Specific)

**Status**: **ACTIVE** - Huddinge v3 dataset-specific scripts.

**Key scripts**:
- `attendo_4mars_to_fsr.py` - **Primary CSV→FSR converter for v3** ✅
  - Last modified: Mar 13 17:30
  - Includes PT0M dependencies, time window fixes, visit sequencing
  - **USE THIS for v3 research**

- `analyze_4mars_csv_to_json.py` - CSV↔JSON analysis ✅
- `build_address_coordinates.py` - Build coordinate cache ✅
- `map_visits_time_windows.py` - Time window mapping report ✅
- `verify_all_visits_have_flex.py` - Validation ✅

**Usage**: Use these for **Huddinge v3 specific** conversions and analysis.

---

## Current Research Pipeline (What's Actually Running)

### Step 1: CSV → FSR Input
```bash
cd /Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits

python3 huddinge-package/huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py \
  "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/Huddinge-v3 - Data_final.csv" \
  --start-date 2026-03-02 --end-date 2026-03-15 \
  --no-geocode \
  -o data/huddinge-v3/input/input_huddinge-v3_FIXED.json
```

### Step 2: Submit to Timefold
```bash
cd /Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits/scripts

python3 submit_to_timefold.py solve \
  "../data/huddinge-v3/input/input_huddinge-v3_FIXED.json" \
  --wait --save "../data/huddinge-v3/research_output/exp_123/output.json"
```

### Step 3: Calculate Metrics
```bash
python3 metrics.py \
  --solution "../data/huddinge-v3/research_output/exp_123/output.json"
```

### Step 4: Generate Continuity Report
```bash
python3 continuity_report.py \
  --input "../data/huddinge-v3/input/input_huddinge-v3_FIXED.json" \
  --solution "../data/huddinge-v3/research_output/exp_123/output.json" \
  --output "../data/huddinge-v3/continuity/reports/continuity_exp_123.csv"
```

---

## Why Three Locations?

### Historical Context

1. **`recurring-visits/scripts/`** - Original location, 50+ scripts, some generic
2. **`huddinge-package/huddinge-4mars-csv/scripts/`** - Huddinge v3 specific scripts with all fixes
3. **`scripts/timefold/`** - Planned consolidation (partially complete)

### Current State

**Consolidation is incomplete**:
- Some scripts copied to `/scripts/timefold/`
- Some scripts have diverged (different MD5 hashes)
- Most scripts still only exist in `/recurring-visits/scripts/`
- v3-specific scripts remain in `huddinge-4mars-csv/scripts/`

### Recommendation

**For Schedule Research**:
1. ✅ **Use `huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py`** for CSV conversion (v3-specific, latest fixes)
2. ✅ **Use `recurring-visits/scripts/submit_to_timefold.py`** for submission (proven, working)
3. ✅ **Use `recurring-visits/scripts/metrics.py`** for analysis (proven, working)

**For consolidation task**: Complete the migration later, test thoroughly, then update agent scripts.

---

## Agent Integration

### `agents/timefold-specialist.sh`

**Current paths**:
```bash
SCRIPTS_DIR="$SERVICE_ROOT/recurring-visits/scripts"

cd "$SCRIPTS_DIR"
python3 submit_to_timefold.py solve "$INPUT_JSON" --wait --save "$OUTPUT_DIR/output.json"
```

**Input location**:
```bash
DATA_DIR="$SERVICE_ROOT/recurring-visits/data"
INPUT_JSON="$DATA_DIR/$DATASET/input/input_${DATASET}_FIXED.json"
```

### `scripts/compound/schedule-research-loop.sh`

Orchestrates the research loop:
1. Calls `agents/optimization-mathematician.sh` (strategy)
2. Calls `agents/timefold-specialist.sh` (execution via `submit_to_timefold.py`)
3. Evaluates results and loops

---

## Data File Locations

### Input
`/recurring-visits/data/huddinge-v3/input/input_huddinge-v3_FIXED.json`
- **3,844 visits** (3,520 standalone + 324 in groups)
- **2,069 dependencies** (visit sequencing)
- Generated from: `Huddinge-v3 - Data_final.csv` (664 rows with Lat/Lon)

### Output
`/recurring-visits/data/huddinge-v3/research_output/exp_*/output.json`
- Timefold solve results

### Source CSV
`/recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/Huddinge-v3 - Data_final.csv`
- **664 data rows** (665 with header)
- **115 clients**
- **22 columns** (includes Lat, Lon)

---

## Summary

**For research, stick with the working scripts**:
- Conversion: `huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py`
- Submission: `recurring-visits/scripts/submit_to_timefold.py`
- Analysis: `recurring-visits/scripts/metrics.py`

**Don't switch to consolidated scripts yet** - they may have diverged and haven't been tested in the research loop.
