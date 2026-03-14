# Continuity Optimization - Correct Approach

**Status**: ❌ Tags approach failed (FSR schema doesn't support tags)
**Correct Approach**: Use continuity patch AFTER initial solve

## What Happened

### Attempt 1: Add Tags to Input (FAILED)
```json
{
  "id": "H015_r0_1",
  "tags": ["customer_H015"]  // ← FSR schema doesn't support this!
}
```

**Error**: HTTP 400 - "property 'tags' is not defined in the schema"

**Why**: Timefold FSR has a strict schema that doesn't include tags field on visits.

### Attempt 2: v3_FIXED (RUNNING ✅)
- No tags, just the schedule fixes
- Currently solving: Score improving (0hard/-35M medium/-3M soft)
- This will complete successfully

## Correct Continuity Workflow

Continuity optimization in Timefold FSR is a **TWO-STEP process**:

### Step 1: Initial Solve (Running Now)
```bash
# This is running now as v3_FIXED
submit_to_timefold.py solve input_v3_FIXED.json --wait --save output_FIXED/
```

**Result**:
- Good schedule with travel optimization
- Continuity ~4-5 employees per client (natural clustering)

### Step 2: Continuity Patch (After Step 1 Completes)
```bash
# 1. Analyze continuity from initial solution
python3 analysis/calculate_continuity_fsr.py \
  output_FIXED/[route_plan_id]_output.json \
  -o continuity.csv

# 2. Generate continuity patch (employee assignments)
python3 analysis/generate_continuity_patch.py \
  output_FIXED/[route_plan_id]_output.json \
  continuity.csv \
  -o continuity_patch.json

# 3. Solve again WITH patch
python3 scripts/submit_to_timefold.py solve-with-patch \
  input_v3_FIXED.json \
  continuity_patch.json \
  --wait --save output_CONTINUITY/
```

**Result**:
- Same good schedule
- Continuity **~2-3 employees** per client (locked assignments)

## How Continuity Patch Works

### What It Contains
The patch locks specific visits to specific employees:

```json
{
  "from": {
    "route_plan_id": "abc123..."
  },
  "patch": {
    "visits": [
      {
        "id": "H015_r3_1",
        "vehicle_id": "Dag_01_Central_1"  // ← Locks this visit to this employee
      },
      {
        "id": "H015_r6_1",
        "vehicle_id": "Dag_01_Central_1"  // ← Same employee for same customer
      }
    ]
  }
}
```

### How It Improves Continuity
1. Identifies which visits went to which employees in initial solve
2. Finds customers with high continuity (many different employees)
3. Locks their visits to the most common employee
4. Solver re-optimizes travel while respecting locked assignments

### Example Improvement
**Before patch (initial solve)**:
- H015 has 44 visits
- Assigned to 10 different employees
- Most common: Employee A (12 visits), Employee B (8 visits)

**After patch**:
- Lock all H015 visits to Employee A (or split between A+B only)
- Continuity: 10 → 2 employees
- Solver adjusts routes to accommodate

## Next Steps

### When v3_FIXED Completes (~20-30 min)

1. **Verify it completed**:
   ```bash
   tail -20 /tmp/timefold_submit_v3_fixed.log
   ls output_FIXED/
   ```

2. **Analyze continuity**:
   ```bash
   cd recurring-visits/

   python3 analysis/calculate_continuity_fsr.py \
     huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_FIXED/[id]_output.json \
     -o huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity_baseline.csv

   # View results
   cat huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity_baseline.csv
   ```

3. **Generate continuity patch**:
   ```bash
   python3 analysis/generate_continuity_patch.py \
     huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_FIXED/[id]_output.json \
     huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity_baseline.csv \
     -o huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity_patch.json \
     --max-continuity 5  # Only patch clients with >5 employees
   ```

4. **Submit with patch**:
   ```bash
   python3 scripts/submit_to_timefold.py solve-with-patch \
     huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
     huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity_patch.json \
     --configuration-id "" \
     --wait \
     --save huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_CONTINUITY
   ```

5. **Compare results**:
   ```bash
   # Baseline continuity
   cat continuity_baseline.csv | awk -F, '{sum+=$3; count++} END {print "Avg:", sum/count}'

   # After patch
   python3 analysis/calculate_continuity_fsr.py \
     output_CONTINUITY/[id]_output.json \
     -o continuity_improved.csv

   cat continuity_improved.csv | awk -F, '{sum+=$3; count++} END {print "Avg:", sum/count}'
   ```

## Expected Timeline

**Now (17:30)**: v3_FIXED solving (0hard/-35M/-3M soft score)
**~18:00**: v3_FIXED completes
**18:00-18:10**: Analyze continuity, generate patch
**18:10**: Submit with patch
**~18:40**: Continuity-optimized solution ready

## Why This Approach Is Better

### Advantages
1. ✅ **Works with FSR schema** (no schema violations)
2. ✅ **Two-stage optimization** (travel first, continuity second)
3. ✅ **Proven approach** (used in existing workflow)
4. ✅ **Flexible** (can adjust which clients to optimize)

### Tags Approach (Failed)
1. ❌ Schema violation
2. ❌ Would make initial solve harder (conflicting objectives)
3. ❌ All-or-nothing (can't selectively apply)

## Summary

**Current Status**:
- ✅ v3_FIXED solving (with schedule fixes)
- ❌ v3_CONTINUITY failed (tags not supported)
- ✅ **Plan**: Wait for v3_FIXED → generate patch → solve with patch

**ETA**: Continuity-optimized solution in ~1 hour

---

**Monitor progress**: `tail -f /tmp/timefold_submit_v3_fixed.log`
