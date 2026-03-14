# Current Status - v3 Optimization Campaign

**Date**: 2026-03-13 17:40
**Location**: `/Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/`

## What's Running

### ✅ v3_FIXED - Schedule Fixes (SOLVING)
**Route Plan ID**: `4cdfce61-0d2d-46e0-9c16-674a7b9dab0f`
**Status**: SOLVING_ACTIVE
**Started**: 17:30:22
**ETA**: ~18:00 (30 minutes total)
**Last Score**: 0hard/-35160000medium/-3065472soft (improving)

**Monitor**:
```bash
tail -f /tmp/timefold_submit_v3_fixed.log
```

**Features**:
- ✅ "Exakt dag/tid" recognition (minimal flex)
- ✅ Empty före/efter handling (exact time for critical tasks)
- ✅ Same-day visit dependencies (PT0M to prevent overlaps)
- ❌ No continuity optimization yet

**Expected Outcome**:
- Schedule quality: EXCELLENT (all time fixes applied)
- Continuity: ~4-5 employees per client (baseline, natural clustering from travel optimization)
- No overlapping same-day visits
- Exact times respected for "Exakt dag/tid" and critical tasks

## What's Next

### Phase 2: Continuity Optimization (After v3_FIXED Completes)

**Workflow**: See `CONTINUITY_WORKFLOW_CORRECTED.md` for details

1. **Analyze baseline continuity** (Step 2)
   ```bash
   python3 scripts/continuity_report.py \
     --input input_v3_FIXED.json \
     --output output_FIXED/4cdfce61_output.json \
     --report continuity_baseline.csv
   ```

2. **Build continuity pools** (Step 3)
   ```bash
   python3 scripts/build_continuity_pools.py \
     --source first-run \
     --input input_v3_FIXED.json \
     --output output_FIXED/4cdfce61_output.json \
     --out continuity_pools.json \
     --max-per-client 3
   ```

3. **Patch input with requiredVehicles** (Step 4)
   ```bash
   python3 scripts/build_continuity_pools.py \
     --source first-run \
     --input input_v3_FIXED.json \
     --output output_FIXED/4cdfce61_output.json \
     --out continuity_pools.json \
     --max-per-client 3 \
     --patch-fsr-input input_v3_FIXED.json \
     --patched-input input_v3_CONTINUITY_v2.json
   ```

4. **Submit continuity-constrained solve** (Step 5)
   ```bash
   python3 scripts/submit_to_timefold.py solve \
     input_v3_CONTINUITY_v2.json \
     --wait \
     --save output_CONTINUITY_v2 \
     > /tmp/timefold_submit_v3_continuity_v2.log 2>&1 &
   ```

5. **Analyze improved continuity** (Step 6)
   ```bash
   python3 scripts/continuity_report.py \
     --input input_v3_CONTINUITY_v2.json \
     --output output_CONTINUITY_v2/[id]_output.json \
     --report continuity_improved.csv
   ```

**Expected Improvement**: 4-5 employees → 2-3 employees per client

## Files Overview

### Input Files
- ✅ `input_v3_FIXED.json` - Input with schedule fixes (solving now)
- ❌ `input_v3_CONTINUITY.json` - Failed attempt with tags (schema violation)
- ⏳ `input_v3_CONTINUITY_v2.json` - Will generate with requiredVehicles (Step 4)

### Output Files
- 🔄 `output_FIXED/4cdfce61_output.json` - Solving now
- ⏳ `output_CONTINUITY_v2/[id]_output.json` - Will generate in Step 5

### Analysis Files
- ⏳ `continuity_baseline.csv` - Will generate in Step 2
- ⏳ `continuity_pools.json` - Will generate in Step 3
- ⏳ `continuity_improved.csv` - Will generate in Step 6

### Documentation
- ✅ `SCHEDULE_ANALYSIS.md` - Root cause analysis of schedule issues
- ✅ `FIXES_IMPLEMENTED.md` - Documentation of fixes applied
- ✅ `REGENERATION_SUMMARY.md` - Summary answering geocoding & continuity questions
- ✅ `CONTINUITY_WORKFLOW_CORRECTED.md` - Correct continuity optimization workflow
- ✅ `CURRENT_STATUS.md` - This file

### Logs
- 🔄 `/tmp/timefold_submit_v3_fixed.log` - v3_FIXED solve log (active)
- ❌ `/tmp/timefold_submit_v3_continuity.log` - Failed tags attempt
- ⏳ `/tmp/timefold_submit_v3_continuity_v2.log` - Will create in Step 5

## What We Learned

### ❌ Attempt 1: Tags Approach
- Added `tags: ["customer_H015"]` to all 3,508 visits
- Submitted as `input_v3_CONTINUITY.json`
- **Failed**: HTTP 400 - "property 'tags' is not defined in the schema"
- **Lesson**: FSR schema is strict, doesn't support custom tags

### ✅ Correct Approach: RequiredVehicles
- Use `requiredVehicles` field to constrain which employees can serve each visit
- Two-stage process: unconstrained solve → analyze → constrained re-solve
- Proven approach used in existing scripts (`build_continuity_pools.py`)

## Timeline

| Time | Event | Status |
|------|-------|--------|
| 17:30 | v3_FIXED started | ✅ Running |
| ~18:00 | v3_FIXED completes | ⏳ Waiting |
| 18:00-18:10 | Build continuity optimization | ⏳ Pending |
| 18:10 | v3_CONTINUITY_v2 submitted | ⏳ Pending |
| ~18:40 | v3_CONTINUITY_v2 completes | ⏳ Pending |
| 18:40-18:45 | Final analysis | ⏳ Pending |

**Current Time**: 17:40
**Wait Time**: ~20 minutes until v3_FIXED completes

## Quick Commands

**Check v3_FIXED status**:
```bash
tail -f /tmp/timefold_submit_v3_fixed.log
```

**When v3_FIXED completes, run all steps**:
```bash
cd /Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits

# Step 2: Analyze
python3 scripts/continuity_report.py \
  --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
  --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_FIXED/4cdfce61_output.json \
  --report huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity_baseline.csv

# Step 3 & 4: Build pools and patch input (combined)
python3 scripts/build_continuity_pools.py \
  --source first-run \
  --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
  --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_FIXED/4cdfce61_output.json \
  --out huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity_pools.json \
  --max-per-client 3 \
  --patch-fsr-input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
  --patched-input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_CONTINUITY_v2.json

# Step 5: Submit
python3 scripts/submit_to_timefold.py solve \
  huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_CONTINUITY_v2.json \
  --wait \
  --save huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_CONTINUITY_v2 \
  > /tmp/timefold_submit_v3_continuity_v2.log 2>&1 &

# Monitor
tail -f /tmp/timefold_submit_v3_continuity_v2.log
```

---

**Check back at ~18:00** to proceed with continuity optimization!
