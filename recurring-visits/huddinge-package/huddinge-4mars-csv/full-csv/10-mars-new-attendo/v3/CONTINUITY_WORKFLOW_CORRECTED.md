# Continuity Optimization - Corrected Workflow

**Date**: 2026-03-13 17:40
**Status**: v3_FIXED solving, preparing continuity optimization

## What We Learned

### ❌ Tags Approach (Failed)
- Tried adding `tags: ["customer_H015"]` to visits
- **Result**: HTTP 400 - schema violation
- **Why**: FSR schema doesn't support tags field

### ❌ From-Patch Reassignment (Won't Work)
- Considered using from-patch to reassign visits to different vehicles
- **Problem**: From-patch can only PIN visits, not reassign them
- Pinning locks visits to their current vehicle assignment

### ✅ Correct Approach: RequiredVehicles Constraint
FSR supports `requiredVehicles` field on visits to limit which employees can serve them.

**How it works:**
```json
{
  "id": "H015_r3_1",
  "name": "H015 Morgon...",
  "requiredVehicles": ["Dag_01_Central_1", "Dag_02_Central_1"]
}
```

This tells the solver: "This visit can ONLY be assigned to these 2 vehicles"

## Continuity Optimization Workflow

### Step 1: Initial Solve (Running Now) ✅
```bash
# Status: SOLVING_ACTIVE
# Route Plan ID: 4cdfce61-0d2d-46e0-9c16-674a7b9dab0f
# ETA: ~18:00
```

### Step 2: Analyze Continuity from Initial Solution
```bash
cd /Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits

# Run continuity analysis
python3 scripts/continuity_report.py \
  --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
  --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_FIXED/4cdfce61_output.json \
  --report huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity_baseline.csv

# View results
cat huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity_baseline.csv
```

**Expected**: Continuity ~4-5 employees per client (natural clustering)

### Step 3: Build Continuity Pools
```bash
# Build continuity pools from initial solution
# Strategy: For each client, find top 2-3 vehicles by visit count
python3 scripts/build_continuity_pools.py \
  --source first-run \
  --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
  --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_FIXED/4cdfce61_output.json \
  --out huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity_pools.json \
  --max-per-client 3
```

**Result**: `continuity_pools.json` with format:
```json
{
  "H015": ["Dag_01_Central_1", "Dag_02_Central_1", "Kväll_01_Central_1"],
  "H026": ["Dag_03_Fullersta_1", "Dag_04_Fullersta_1"],
  ...
}
```

### Step 4: Patch Input with RequiredVehicles
```bash
# Apply continuity pools to input JSON
python3 scripts/build_continuity_pools.py \
  --source first-run \
  --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
  --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_FIXED/4cdfce61_output.json \
  --out huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity_pools.json \
  --max-per-client 3 \
  --patch-fsr-input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
  --patched-input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_CONTINUITY.json
```

**Result**: `input_v3_CONTINUITY.json` with requiredVehicles added to each visit

### Step 5: Submit Continuity-Constrained Solve
```bash
# Submit new solve with requiredVehicles constraints
python3 scripts/submit_to_timefold.py solve \
  huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_CONTINUITY.json \
  --configuration-id "" \
  --wait \
  --save huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_CONTINUITY \
  > /tmp/timefold_submit_v3_continuity_v2.log 2>&1 &
```

### Step 6: Analyze Improved Continuity
```bash
# After continuity solve completes
python3 scripts/continuity_report.py \
  --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_CONTINUITY.json \
  --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_CONTINUITY/[route_plan_id]_output.json \
  --report huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity_improved.csv

# Compare
echo "=== Baseline ==="
cat huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity_baseline.csv | head -20

echo "=== Improved ==="
cat huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity_improved.csv | head -20
```

**Expected Improvement**: 4-5 employees → 2-3 employees per client

## How RequiredVehicles Works

### Before (Unconstrained)
```
H015 breakfast → Assigned to any of 41 vehicles (solver chooses based on travel)
H015 lunch → Assigned to any of 41 vehicles (might be different!)
H015 dinner → Assigned to any of 41 vehicles (might be different again!)

Result: 4-5 different employees for H015
```

### After (With RequiredVehicles)
```json
{
  "id": "H015_r0_1",
  "name": "H015 FRUKOST...",
  "requiredVehicles": ["Dag_01_Central_1", "Dag_02_Central_1"]
}
{
  "id": "H015_r1_1",
  "name": "H015 LUNCH...",
  "requiredVehicles": ["Dag_01_Central_1", "Dag_02_Central_1"]
}
```

**Result**: All H015 visits constrained to 2 specific vehicles → 2 employees for H015

## Timeline

**17:30** - v3_FIXED started solving
**~18:00** - v3_FIXED completes (ETA)
**18:00-18:10** - Analyze continuity, build pools, patch input
**18:10** - Submit v3_CONTINUITY
**~18:40** - v3_CONTINUITY completes
**18:40-18:45** - Final analysis and comparison

## Key Insights

1. **Tags don't work** - FSR schema is strict, no custom tags
2. **From-patch is for locking** - Can't reassign visits to new vehicles
3. **RequiredVehicles is the solution** - Constrains which vehicles can serve each visit
4. **Two-stage process** - Unconstrained solve → analyze → constrained re-solve
5. **Natural clustering helps** - Initial solve often has decent continuity (4-5) from travel optimization

## References

- `scripts/build_continuity_pools.py` - The key script for this workflow
- `scripts/continuity_report.py` - Continuity analysis
- Campaign 117a4aa3 - Original campaign with continuity ~4.3
