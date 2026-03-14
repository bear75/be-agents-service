# Continuity Optimization Results Comparison

**Date**: 2026-03-13

---

## Overall Metrics

| Variant | Status | Avg Continuity | Assigned | Unassigned | Clients Served | Score |
|---------|--------|----------------|----------|------------|----------------|-------|
| **Baseline (v3_FIXED)** | ✅ Complete | **10.16** | 3,739 (97.6%) | 93 (2.4%) | 176 | N/A |
| **pool3** | 🔄 Solving | **1.76** ✅ | 2,849 (74.3%) | **983 (25.7%)** ❌ | 168 | 0h/-9.8M/-9.0M |
| **pool5** | ⏳ Queued | Expected: 3-4 | Expected: ~90% | Expected: ~10% | Expected: ~176 | TBD |
| **pool8** | ⏳ Queued | Expected: 4-5 | Expected: ~95% | Expected: ~5% | Expected: 176 | TBD |

---

## Detailed Analysis

### Baseline (v3_FIXED)
- **Route Plan ID**: 4cdfce61-0d2d-46e0-9c16-674a7b9dab0f
- **Problem**: No continuity optimization
- **Result**: Average client sees 10 different employees over 2 weeks
- **Worst case**: H026 sees 33 different employees

### pool3_required
- **Route Plan ID**: 30c39aef-127f-4411-ab9b-4453f2f3f7b6
- **Strategy**: Each client limited to top 3 employees from baseline
- **Continuity**: Excellent (1.76 avg)
- **Coverage**: Poor (25.7% unassigned)
- **Verdict**: ❌ Too aggressive - unassigned rate too high

### pool5_required (RECOMMENDED)
- **Route Plan ID**: cae24e29-d23a-46cd-9a86-5d267dbf22d9
- **Strategy**: Each client limited to top 5 employees from baseline
- **Expected**: Best balance between continuity and coverage
- **Status**: Waiting to start

### pool8_required
- **Route Plan ID**: ba5411e1-c77c-4d67-99bd-4a06e64e1f42
- **Strategy**: Each client limited to top 8 employees from baseline
- **Expected**: Safest option with highest coverage
- **Status**: Waiting to start

---

## Example Client Comparisons

### H015 (44 visits over 2 weeks)

| Variant | Employees | CCI | Bice CCI | Notes |
|---------|-----------|-----|----------|-------|
| Baseline | 10 | 0.15 | TBD | Too many employees |
| pool3 | 3 | 0.34 | 0.32 | ✅ Excellent continuity |
| pool5 | TBD | TBD | TBD | Expected: 3-4 |
| pool8 | TBD | TBD | TBD | Expected: 4-5 |

### H086 (95 visits over 2 weeks)

| Variant | Employees | CCI | Bice CCI | Notes |
|---------|-----------|-----|----------|-------|
| Baseline | 34 | 0.04 | TBD | Way too many |
| pool3 | 3 | 0.55 | 0.54 | ✅ Huge improvement |
| pool5 | TBD | TBD | TBD | Expected: 3-4 |
| pool8 | TBD | TBD | TBD | Expected: 4-5 |

### H290 (90 visits over 2 weeks)

| Variant | Employees | CCI | Bice CCI | Notes |
|---------|-----------|-----|----------|-------|
| Baseline | 34 | 0.04 | TBD | Way too many |
| pool3 | 3 | 0.34 | 0.34 | ✅ Excellent |
| pool5 | TBD | TBD | TBD | Expected: 3-4 |
| pool8 | TBD | TBD | TBD | Expected: 4-5 |

---

## Trade-off Analysis

### pool3 (Most Aggressive)
✅ **Pros**:
- Best continuity (1.76 avg)
- Most clients get exactly 2-3 employees
- Some get only 1 employee (perfect)

❌ **Cons**:
- 25.7% visits unassigned (983 visits!)
- 8 clients not served at all
- Not acceptable for production

### pool5 (Balanced)
✅ **Pros**:
- Good continuity (expected 3-4 avg)
- Acceptable unassigned rate (expected <10%)
- Serves all or most clients

❓ **Unknown**:
- Actual performance TBD

### pool8 (Conservative)
✅ **Pros**:
- Improved continuity (4-5 vs 10.16)
- Low unassigned rate (<5%)
- Serves all clients

⚠️ **Cons**:
- Slightly worse continuity than pool5
- Still much better than baseline

---

## Decision Matrix

| Priority | Choose |
|----------|--------|
| **Best continuity** | pool3 (but unusable due to coverage) |
| **Best balance** | pool5 (likely winner) |
| **Best coverage** | pool8 (safe fallback) |
| **Production ready** | pool5 or pool8 (wait for results) |

---

## Update Instructions

When pool5 completes:
```bash
# Fetch solution
python3 scripts/fetch_timefold_solution.py cae24e29-d23a-46cd-9a86-5d267dbf22d9 \
  --save v3/continuity/results/pool5_required/cae24e29_output.json

# Analyze
python3 scripts/continuity_report.py \
  --input v3/continuity/variants/input_pool5_required.json \
  --output v3/continuity/results/pool5_required/cae24e29_output.json \
  --report v3/continuity/results/pool5_required/continuity_pool5.csv

# Check results
head -20 v3/continuity/results/pool5_required/continuity_pool5.csv
```

Then update this table with actual numbers.

---

**Status**: pool3 analyzed, pool5 and pool8 pending
**Recommendation**: Wait for pool5, likely to be the winner
**Next Check**: Monitor queue status in 15-30 minutes
