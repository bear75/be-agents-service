# Timefold Submissions In Progress
**Date**: 2026-03-13
**Status**: 🔄 Both running in background

## Two Versions Submitted

### Version 1: v3_FIXED (Without Continuity Tags)
**Input**: `input_v3_FIXED.json`
**Output Dir**: `output_FIXED/`
**Background Task**: ba11dad
**Log**: `/tmp/timefold_submit_v3_fixed.log`

**Features**:
- ✅ Schedule fixes (exact time, same-day dependencies)
- ❌ No continuity tags

**Expected Results**:
- Continuity: ~4-5 employees per client (similar to campaign 117a4aa3)
- Time precision: Better (exact times respected)
- Overlaps: Fixed (no more same-day conflicts)

### Version 2: v3_CONTINUITY (With Continuity Tags)
**Input**: `input_v3_CONTINUITY.json`
**Output Dir**: `output_CONTINUITY/`
**Background Task**: bdd6d6e
**Log**: `/tmp/timefold_submit_v3_continuity.log`

**Features**:
- ✅ Schedule fixes (exact time, same-day dependencies)
- ✅ Continuity tags: All 3,508 visits have `customer_HXXX` tags

**Expected Results**:
- Continuity: **~2-3 employees per client** (improved!)
- Time precision: Same as v3_FIXED
- Overlaps: Fixed (no more same-day conflicts)

**Sample Visit**:
```json
{
  "id": "H015_r0_1",
  "name": "H015 TVÄTT PÅ KONTORET  Service Insats Tvätt",
  "tags": ["customer_H015"]  // ← NEW!
}
```

## How to Monitor Progress

### Check Background Jobs
```bash
# Check if jobs are still running
ps aux | grep "submit_to_timefold.py"

# View live logs
tail -f /tmp/timefold_submit_v3_fixed.log
tail -f /tmp/timefold_submit_v3_continuity.log
```

### Check Output Files
```bash
# v3_FIXED results
ls -lh huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_FIXED/

# v3_CONTINUITY results
ls -lh huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_CONTINUITY/
```

### Expected Output Files
After solving completes (~10-30 minutes), you'll see:
```
output_FIXED/
  └── [route_plan_id]_output.json

output_CONTINUITY/
  └── [route_plan_id]_output.json
```

## What Happens Next

### When v3_FIXED Completes
1. Solution will be saved to `output_FIXED/[route_plan_id]_output.json`
2. Analyze continuity:
   ```bash
   python3 analysis/calculate_continuity_fsr.py \
     output_FIXED/[route_plan_id]_output.json \
     -o output_FIXED/continuity.csv
   ```
3. Expected continuity: ~4-5 employees (baseline)

### When v3_CONTINUITY Completes
1. Solution will be saved to `output_CONTINUITY/[route_plan_id]_output.json`
2. Analyze continuity:
   ```bash
   python3 analysis/calculate_continuity_fsr.py \
     output_CONTINUITY/[route_plan_id]_output.json \
     -o output_CONTINUITY/continuity.csv
   ```
3. Expected continuity: **~2-3 employees** (improved!)

## Comparison Plan

Once both complete, compare:

### 1. Continuity Scores
```bash
# v3_FIXED
cat output_FIXED/continuity.csv | head -20

# v3_CONTINUITY
cat output_CONTINUITY/continuity.csv | head -20
```

**Expected Improvement**:
- H015: 10 employees → ~3-4 employees
- H026: 10 employees → ~3-4 employees
- H092: 10 employees → ~3-4 employees

### 2. Schedule Quality
Both should have:
- ✅ No overlapping visits for same customer
- ✅ Exact times respected for critical visits
- ✅ Same-day visits properly sequenced

### 3. Metrics Comparison
```bash
# Generate metrics for both
cd recurring-visits/

# v3_FIXED metrics
python3 scripts/fetch_timefold_solution.py [route_plan_id_fixed] \
  --save output_FIXED/[id]_output.json \
  --metrics-dir output_FIXED/metrics

# v3_CONTINUITY metrics
python3 scripts/fetch_timefold_solution.py [route_plan_id_continuity] \
  --save output_CONTINUITY/[id]_output.json \
  --metrics-dir output_CONTINUITY/metrics
```

**Expected**:
- Travel time: Similar (both optimized)
- Efficiency: Similar (~73%)
- Continuity: v3_CONTINUITY **significantly better**

## Key Differences

| Aspect | v3_FIXED | v3_CONTINUITY |
|--------|----------|---------------|
| **Continuity tags** | ❌ No | ✅ Yes (all visits) |
| **Expected continuity** | ~4-5 employees | **~2-3 employees** |
| **Same customer visits** | Different employees | **Prefers same employee** |
| **Breakfast + Lunch** | Likely different | **Likely same** (if same shift) |
| **Travel optimization** | Full | Full |
| **Time precision** | ✅ Fixed | ✅ Fixed |

## Why Continuity Version Should Be Better

### How Tags Work
When visit has `tags: ["customer_H015"]`:
- Timefold **soft constraint**: Prefer assigning all `customer_H015` visits to same vehicle
- Not a hard constraint: Can still split if necessary for feasibility
- Solver balances: travel time vs continuity

### Expected Behavior
**Before (v3_FIXED)**:
- H015 breakfast → "Dag 01 Central" (minimizes travel from previous visit)
- H015 lunch → "Dag 03 Fullersta" (minimizes travel from previous visit)
- H015 dinner → "Kväll 01 Central" (different shift, different employee)
- **Result**: 3 different employees

**After (v3_CONTINUITY)**:
- H015 breakfast → "Dag 01 Central"
- H015 lunch → "Dag 01 Central" (prefers same vehicle due to tag!)
- H015 dinner → "Kväll 01 Central" (different shift, but might be same person)
- **Result**: 2 different employees (or even 1 if same person works both shifts)

## Timeline

**Started**: Mar 13 17:30
**Expected Completion**: Mar 13 18:00-18:30 (30-60 min solve time)

Check back in ~30 minutes to analyze results!

---

**Status**: 🔄 Running
**Monitor**: `tail -f /tmp/timefold_submit_v3_*.log`
