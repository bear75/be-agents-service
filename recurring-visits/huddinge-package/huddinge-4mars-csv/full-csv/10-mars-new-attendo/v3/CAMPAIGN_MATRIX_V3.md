# v3 Campaign Matrix: Efficiency + Continuity Optimization

**Date**: 2026-03-13 18:17
**Based on**: v3_FIXED output (4cdfce61-0d2d-46e0-9c16-674a7b9dab0f)
**Goal**: Find optimal balance of efficiency (73%+) and continuity (2-3 employees/client)

---

## Research Insights

### From Production Campaign 117a4aa3 (v2 baseline)
- **Continuity**: 4.3 avg employees/client (EXCELLENT)
- **Max continuity**: 10 employees
- **Clients over 15**: 0 (PERFECT)
- **Approach**: Default preferred vehicles
- **Dataset**: 81 clients

### From From-Patch Optimization
- **Field efficiency**: 73.25% (exceeds 67.5% target)
- **Empty shifts eliminated**: 100% (27 → 0)
- **Unassigned improvement**: 36% reduction
- **Continuity maintained**: 6.1 → 6.11

### Key Learnings
1. **Pool size 5-10 optimal** (smaller = better continuity, less flexibility)
2. **Weight variants matter**: preferred_2 vs preferred_10 vs preferred_20
3. **Combo strategies** balance efficiency + continuity
4. **From-patch** eliminates waste after initial solve

---

## v3 Campaign Strategy

### Phase 1: Baseline (Running)
| Variant | Status | Route Plan ID | Notes |
|---------|--------|---------------|-------|
| **v3_FIXED** | 🔄 Solving | 4cdfce61-0d2d-46e0-9c16-674a7b9dab0f | Schedule fixes only, no continuity |

**Expected result**: ~4-5 employees/client (natural clustering from travel optimization)

### Phase 2: Continuity Variants (Parallel Launch)

#### Track A: Pool Size Variants
Test pool sizes 3, 5, 8 with preferred vehicles weight 2 (gentle)

| Variant | Pool Size | Strategy | Weight | Target Continuity |
|---------|-----------|----------|--------|-------------------|
| **pool3_preferred2** | 3 | preferredVehicles | 2 | 2-3 employees |
| **pool5_preferred2** | 5 | preferredVehicles | 2 | 3-4 employees |
| **pool8_preferred2** | 8 | preferredVehicles | 2 | 4-5 employees |

#### Track B: Weight Variants (Pool 5)
Test different weights with pool size 5 (middle ground)

| Variant | Pool Size | Strategy | Weight | Constraint Strength |
|---------|-----------|----------|--------|---------------------|
| **pool5_preferred2** | 5 | preferredVehicles | 2 | Gentle (from Track A) |
| **pool5_preferred10** | 5 | preferredVehicles | 10 | Medium |
| **pool5_preferred20** | 5 | preferredVehicles | 20 | Strong |
| **pool5_required** | 5 | requiredVehicles | N/A | Hard constraint |

#### Track C: Combo Strategies (Pool 5)
Balance continuity with efficiency

| Variant | Pool Size | Strategy | Features |
|---------|-----------|----------|----------|
| **pool5_combo** | 5 | preferred + wait_min | Continuity + efficiency |
| **pool5_wait_min** | 5 | wait_min only | Efficiency focus (baseline) |

#### Track D: Aggressive Continuity (Pool 3)
Maximum continuity with different weights

| Variant | Pool Size | Strategy | Weight | Target |
|---------|-----------|----------|--------|--------|
| **pool3_preferred2** | 3 | preferredVehicles | 2 | Gentle (from Track A) |
| **pool3_preferred10** | 3 | preferredVehicles | 10 | Medium |
| **pool3_required** | 3 | requiredVehicles | N/A | Hard (2-3 employees guaranteed) |

---

## Campaign Execution Plan

### Step 1: Wait for v3_FIXED Baseline ✅
```bash
# Already running
Route Plan ID: 4cdfce61-0d2d-46e0-9c16-674a7b9dab0f
Status: SOLVING_ACTIVE
```

### Step 2: Build Continuity Pools (Parallel)
```bash
# Pool 3
python3 scripts/build_continuity_pools.py \
  --source first-run \
  --input v3/input_v3_FIXED.json \
  --output v3/output_FIXED/4cdfce61_output.json \
  --max-per-client 3 \
  --out v3/continuity/pools/pool3.json

# Pool 5
python3 scripts/build_continuity_pools.py \
  --source first-run \
  --input v3/input_v3_FIXED.json \
  --output v3/output_FIXED/4cdfce61_output.json \
  --max-per-client 5 \
  --out v3/continuity/pools/pool5.json

# Pool 8
python3 scripts/build_continuity_pools.py \
  --source first-run \
  --input v3/input_v3_FIXED.json \
  --output v3/output_FIXED/4cdfce61_output.json \
  --max-per-client 8 \
  --out v3/continuity/pools/pool8.json
```

### Step 3: Generate Variant Inputs
```bash
# For each pool, generate variants using prepare_continuity_test_variants.py
python3 scripts/prepare_continuity_test_variants.py \
  --base-input v3/input_v3_FIXED.json \
  --pool-file v3/continuity/pools/pool3.json \
  --output-dir v3/continuity/variants/pool3

python3 scripts/prepare_continuity_test_variants.py \
  --base-input v3/input_v3_FIXED.json \
  --pool-file v3/continuity/pools/pool5.json \
  --output-dir v3/continuity/variants/pool5

python3 scripts/prepare_continuity_test_variants.py \
  --base-input v3/input_v3_FIXED.json \
  --pool-file v3/continuity/pools/pool8.json \
  --output-dir v3/continuity/variants/pool8
```

### Step 4: Submit All Variants in Parallel
```bash
# Track A: Pool variants (3 submits)
# Track B: Weight variants (4 submits)
# Track C: Combo variants (2 submits)
# Track D: Aggressive continuity (3 submits)
# Total: ~12 parallel solves
```

### Step 5: Monitor and Compare
```bash
# For each completed solve:
# 1. Fetch solution
# 2. Calculate metrics (efficiency, unassigned)
# 3. Calculate continuity (unique count + CCI)
# 4. Generate comparison report
```

---

## Expected Results

### Continuity Targets by Pool Size

| Pool Size | Expected Avg | Expected Max | Use Case |
|-----------|--------------|--------------|----------|
| **3** | 2-3 | ≤6 | Maximum continuity (may reduce flexibility) |
| **5** | 3-4 | ≤8 | Balanced (recommended) |
| **8** | 4-5 | ≤10 | More flexibility, good continuity |

### Efficiency Targets

- **Field efficiency**: ≥67.5% (target), aim for 73%+
- **Unassigned visits**: <5% (<176 visits)
- **Empty shifts**: 0 (via from-patch if needed)

### Pareto Front

We expect to see trade-offs:
- **pool3_required**: Best continuity, may have more unassigned
- **pool8_preferred2**: Best efficiency, slightly worse continuity
- **pool5_combo**: Balanced sweet spot

---

## Files Structure

```
v3/
├── input_v3_FIXED.json              # Baseline (schedule fixes only)
├── output_FIXED/
│   └── 4cdfce61_output.json         # Baseline result
├── continuity/
│   ├── pools/
│   │   ├── pool3.json               # Client → top 3 vehicles
│   │   ├── pool5.json               # Client → top 5 vehicles
│   │   └── pool8.json               # Client → top 8 vehicles
│   ├── variants/
│   │   ├── pool3/
│   │   │   ├── input_preferred_weight2.json
│   │   │   ├── input_preferred_weight10.json
│   │   │   └── input_required.json
│   │   ├── pool5/
│   │   │   ├── input_preferred_weight2.json
│   │   │   ├── input_preferred_weight10.json
│   │   │   ├── input_preferred_weight20.json
│   │   │   ├── input_required.json
│   │   │   ├── input_combo.json
│   │   │   └── input_wait_min.json
│   │   └── pool8/
│   │       └── input_preferred_weight2.json
│   ├── results/
│   │   ├── pool3_preferred2/
│   │   ├── pool5_preferred10/
│   │   └── ... (one dir per variant)
│   └── analysis/
│       ├── continuity_comparison.csv
│       ├── efficiency_comparison.csv
│       └── pareto_analysis.md
```

---

## Success Criteria

### Minimum Acceptable
- ✅ At least 1 variant achieves ≤4 avg continuity
- ✅ Field efficiency ≥67.5%
- ✅ Unassigned <5%

### Target
- ✅ At least 1 variant achieves ≤3 avg continuity
- ✅ Field efficiency ≥70%
- ✅ Unassigned <3%

### Stretch Goal
- ✅ Multiple variants on Pareto front (continuity vs efficiency)
- ✅ 2-3 avg continuity with 73%+ efficiency
- ✅ Zero clients over 10 employees

---

## Timeline

| Time | Event |
|------|-------|
| 18:17 | Campaign plan created |
| 18:20 | Start variant generation |
| 18:30 | Submit all variants in parallel |
| 19:00-19:30 | Solves complete (30-60 min each) |
| 19:30-20:00 | Analysis and comparison |
| 20:00 | Final recommendation |

**Total duration**: ~2 hours for complete campaign

---

## Next Steps

1. ✅ Create campaign automation script
2. ✅ Generate all variant inputs
3. ✅ Submit in parallel
4. ⏳ Monitor progress
5. ⏳ Analyze results
6. ⏳ Select winning variant
7. ⏳ Optional: From-patch optimization on winner
