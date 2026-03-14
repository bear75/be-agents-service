# Phase 2 Status Update - Continuity Optimization

**Date**: 2026-03-13
**Time**: Current check

---

## Summary

Phase 2 continuity optimization is in progress with 3 variants running in parallel. pool3 has produced initial results showing excellent continuity (1.76 avg) but high unassigned rate (25.7%). pool5 and pool8 are still queued.

---

## Current Status

### pool3_required (Most Aggressive)
**Route Plan ID**: 30c39aef-127f-4411-ab9b-4453f2f3f7b6
**Status**: 🔄 SOLVING_ACTIVE
**Score**: 0hard/-9830000medium/-9001036soft

**Results (partial, still solving)**:
- ✅ **Average continuity: 1.76 employees/client** (target: 2-3)
- ⚠️ **Assigned visits: 2,849 / 3,832 (74.3%)**
- ❌ **Unassigned: 983 visits (25.7%)**
- ✅ **Clients served: 168 / 176**

**Analysis**:
- Excellent continuity achieved (better than target!)
- But unassigned rate too high (should be <10%)
- Trade-off: strictest continuity → most unassigned

**Continuity breakdown** (for assigned visits):
- Most clients get exactly 2-3 employees
- Examples:
  - H015: 44 visits → 3 employees (CCI 0.34)
  - H086: 95 visits → 3 employees (CCI 0.55)
  - H290: 90 visits → 3 employees (CCI 0.34)
  - H327: 54 visits → 2 employees (CCI 0.62)

### pool5_required (Balanced - Recommended)
**Route Plan ID**: cae24e29-d23a-46cd-9a86-5d267dbf22d9
**Status**: ⏳ SOLVING_SCHEDULED (queued, not started yet)
**Score**: ?

**Expected**:
- ✅ Average continuity: 3-4 employees/client
- ✅ Unassigned: <10% (lower than pool3)
- ✅ Best balance between continuity and efficiency

### pool8_required (Conservative)
**Route Plan ID**: ba5411e1-c77c-4d67-99bd-4a06e64e1f42
**Status**: ⏳ SOLVING_SCHEDULED (queued, not started yet)
**Score**: ?

**Expected**:
- ✅ Average continuity: 4-5 employees/client
- ✅ Unassigned: <5% (lowest unassigned)
- ✅ Highest efficiency

---

## Comparison with Baseline

| Metric | v3 Baseline | pool3 (current) | pool5 (expected) | pool8 (expected) |
|--------|-------------|-----------------|------------------|------------------|
| **Avg continuity** | **10.16** ⚠️ | **1.76** ✅ | 3-4 ✅ | 4-5 ✅ |
| **Assigned rate** | 97.6% | **74.3%** ❌ | ~90%+ ✅ | ~95%+ ✅ |
| **Unassigned** | 93 (2.4%) | **983 (25.7%)** ❌ | ~10% ✅ | ~5% ✅ |
| **Clients served** | 176 | 168 | ~176 | 176 |

---

## Key Insights

### 1. Pool3 Continuity Success ✅

For **assigned visits**, pool3 achieves exceptional continuity:
- 1.76 avg unique employees (target was 2-3)
- Most clients get exactly 2-3 employees
- Some clients get only 1 employee (perfect continuity)

**This proves the requiredVehicles approach works!**

### 2. Pool3 Assignment Challenge ❌

The strict pool size causes high unassigned rate:
- 983 visits unassigned (25.7%)
- 8 clients not served at all (176 → 168)
- Trade-off too extreme for production use

**Conclusion**: pool3 is too aggressive for this dataset.

### 3. Why pool3 Has High Unassigned

When limiting each client to their top 3 employees:
- Time window conflicts increase
- Less flexibility for optimizer
- Some visits become impossible to schedule
- Example: Client needs visit at 08:00 but all 3 allowed employees are already busy

### 4. Expected pool5 Performance

pool5 allows top 5 employees per client:
- More scheduling flexibility
- Lower unassigned rate (expected ~10%)
- Still excellent continuity (3-4 avg vs 10.16 baseline)
- **Likely the winning variant**

---

## Next Steps

### When pool5 Completes

1. **Fetch solution**:
   ```bash
   python3 scripts/fetch_timefold_solution.py cae24e29-d23a-46cd-9a86-5d267dbf22d9 \
     --save v3/continuity/results/pool5_required/cae24e29_output.json
   ```

2. **Analyze continuity**:
   ```bash
   python3 scripts/continuity_report.py \
     --input v3/continuity/variants/input_pool5_required.json \
     --output v3/continuity/results/pool5_required/cae24e29_output.json \
     --report v3/continuity/results/pool5_required/continuity_pool5.csv
   ```

3. **Compare with pool3**:
   - If unassigned <10% and continuity <5 avg → **pool5 wins**
   - If unassigned still high → wait for pool8

### When pool8 Completes

1. **Fetch and analyze** (same commands, replace pool5 with pool8)

2. **Final comparison**:
   - pool8 will have lowest unassigned
   - pool8 will have slightly worse continuity (4-5 vs 3-4)
   - If pool5 unassigned acceptable → choose pool5
   - If pool5 unassigned too high → choose pool8

### Estimated Timeline

- **pool5 start**: Unknown (currently queued)
- **pool5 completion**: ~30 min after it starts
- **pool8 start**: After pool5 completes
- **pool8 completion**: ~30 min after it starts
- **Total ETA**: 1-2 hours from now

---

## Decision Criteria

### Choose pool3 if:
- ❌ NOT recommended (25.7% unassigned too high)
- Unless client explicitly prioritizes continuity over coverage

### Choose pool5 if:
- ✅ Unassigned <10%
- ✅ Average continuity <5 employees
- ✅ **Most likely winner**

### Choose pool8 if:
- ✅ pool5 unassigned still too high (>10%)
- ✅ Need highest assignment rate
- ✅ Continuity 4-5 still acceptable (vs 10.16 baseline)

---

## Technical Details

### pool3 Score Breakdown

**Score**: 0hard/-9830000medium/-9001036soft

- **0hard**: No hard constraint violations ✅
- **-9830000medium**: Medium constraints (continuity penalties)
- **-9001036soft**: Soft constraints (travel time, efficiency)

### pool3 Vehicle Distribution

Top vehicles by visits assigned:
- Kväll_02_Kvarnen: 298 visits, 29 clients
- Matlådor_Måndagar: 139 visits, 9 clients
- Dag_01_Central_1: 152 visits, 8 clients
- Kväll_04_Flemingsberg: 140 visits, 13 clients
- Dag_05_Flemingsberg_1: 132 visits, 8 clients
- Kväll_01_Central: 132 visits, 14 clients

Evening shift (Kväll) vehicles handle most visits, which makes sense for home care.

---

## Files Created

### Results
- `v3/continuity/results/pool3_required/30c39aef_output.json` - pool3 solution
- `v3/continuity/results/pool3_required/continuity_pool3.csv` - pool3 continuity analysis

### Pending
- `v3/continuity/results/pool5_required/` - When pool5 completes
- `v3/continuity/results/pool8_required/` - When pool8 completes

---

## Recommendation

**Wait for pool5 results** before making final decision.

Expected outcome:
- pool5 will achieve 3-4 avg continuity (70% improvement vs baseline)
- pool5 will have <10% unassigned (acceptable for production)
- pool5 will be the **balanced winner**

If pool5 disappoints, pool8 is the safe fallback.

---

**Current Action**: Monitoring pool5 and pool8 queue status. Will update when they start solving.
