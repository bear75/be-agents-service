# Monitoring Guide - v3 Campaign

**Quick reference for checking solve status and analyzing results**

---

## Current Status (Quick Check)

```bash
# Check all three solves at once
for id in 30c39aef-127f-4411-ab9b-4453f2f3f7b6 cae24e29-d23a-46cd-9a86-5d267dbf22d9 ba5411e1-c77c-4d67-99bd-4a06e64e1f42; do
  echo "=== Checking $id ==="
  python3 scripts/fetch_timefold_solution.py $id 2>&1 | grep -E "(Route plan ID|Solver status|Score|Unassigned)"
  echo ""
done
```

---

## Individual Solve Status

### pool3_required (Most Aggressive)
```bash
python3 scripts/fetch_timefold_solution.py 30c39aef-127f-4411-ab9b-4453f2f3f7b6 \
  --save v3/continuity/results/pool3_required/30c39aef_output.json
```

**Current Status**: SOLVING_ACTIVE
**Result**: 1.76 avg continuity, 25.7% unassigned ❌

### pool5_required (Balanced - Recommended)
```bash
python3 scripts/fetch_timefold_solution.py cae24e29-d23a-46cd-9a86-5d267dbf22d9 \
  --save v3/continuity/results/pool5_required/cae24e29_output.json
```

**Current Status**: SOLVING_SCHEDULED (queued)
**Expected**: 3-4 avg continuity, <10% unassigned ✅

### pool8_required (Conservative)
```bash
python3 scripts/fetch_timefold_solution.py ba5411e1-c77c-4d67-99bd-4a06e64e1f42 \
  --save v3/continuity/results/pool8_required/ba5411e1_output.json
```

**Current Status**: SOLVING_SCHEDULED (queued)
**Expected**: 4-5 avg continuity, <5% unassigned ✅

---

## When pool5 Completes

### 1. Fetch Solution
```bash
python3 scripts/fetch_timefold_solution.py cae24e29-d23a-46cd-9a86-5d267dbf22d9 \
  --save huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool5_required/cae24e29_output.json
```

### 2. Analyze Continuity
```bash
python3 scripts/continuity_report.py \
  --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/variants/input_pool5_required.json \
  --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool5_required/cae24e29_output.json \
  --report huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool5_required/continuity_pool5.csv
```

### 3. View Results
```bash
# Summary stats
head -5 huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool5_required/continuity_pool5.csv

# Full report
cat huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool5_required/continuity_pool5.csv | less
```

### 4. Compare with pool3
```bash
echo "=== pool3 ==="
grep "Average unique count" huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool3_required/continuity_pool3.csv

echo ""
echo "=== pool5 ==="
grep "Average unique count" huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool5_required/continuity_pool5.csv
```

---

## When pool8 Completes

Same commands as pool5, just replace `pool5` with `pool8` and use route plan ID `ba5411e1-c77c-4d67-99bd-4a06e64e1f42`.

---

## Decision Criteria

### Choose pool5 if:
- ✅ Average continuity <5 employees/client
- ✅ Unassigned <10% (<383 visits)
- ✅ Most clients served (≥170)

### Choose pool8 if:
- ⚠️ pool5 unassigned >10%
- ✅ Average continuity still <8 employees/client
- ✅ Need maximum coverage

### Don't choose pool3 because:
- ❌ 25.7% unassigned rate too high
- ❌ 8 clients completely unserved
- (Even though continuity is excellent at 1.76 avg)

---

## Key Metrics to Check

### 1. Average Continuity
```bash
grep "Average unique count" <continuity_report.csv>
```
**Target**: <5 employees per client (pool5), <8 (pool8)
**Baseline**: 10.16 (pool3: 1.76 ✅)

### 2. Unassigned Rate
From fetch output: `Unassigned: X`
**Target**: <10% (pool5), <5% (pool8)
**Baseline**: 93 (2.4%) - (pool3: 983 (25.7%) ❌)

### 3. Clients Served
Count unique clients in continuity report
**Target**: 176 clients
**Baseline**: 176 - (pool3: 168 ⚠️)

### 4. Max Continuity
Look for highest "continuity" value in report
**Target**: ≤8 employees for worst client
**Baseline**: 33 - (pool3: 3 ✅)

---

## Quick Comparison Script

```bash
#!/bin/bash
# save as compare_variants.sh

echo "=== Variant Comparison ==="
echo ""

for variant in pool3 pool5 pool8; do
  report="v3/continuity/results/${variant}_required/continuity_${variant}.csv"

  if [ -f "$report" ]; then
    echo "=== $variant ==="

    # Average continuity
    avg=$(grep "Average unique count" "$report" | awk '{print $4}')
    echo "Avg continuity: $avg"

    # CCI
    cci=$(grep "Average CCI" "$report" | head -1 | awk '{print $4}')
    echo "Avg CCI: $cci"

    # Client count
    clients=$(grep "Clients:" "$report" | awk '{print $2}')
    echo "Clients: $clients"

    echo ""
  else
    echo "=== $variant ==="
    echo "Not available yet"
    echo ""
  fi
done
```

---

## Logs

### Check solve logs
```bash
tail -f huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/logs/pool5_required.log
```

### Check for errors
```bash
grep -i error huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/logs/*.log
```

---

## Files to Review

### Phase 2 Status
- `v3/PHASE2_STATUS_UPDATE.md` - Detailed status update
- `v3/continuity/results/COMPARISON_TABLE.md` - Cross-variant comparison
- `v3/SUMMARY.md` - Overall campaign summary

### pool3 Results
- `v3/continuity/results/pool3_required/30c39aef_output.json` - Full output
- `v3/continuity/results/pool3_required/continuity_pool3.csv` - Continuity analysis

### Baseline Results
- `v3/output_FIXED/4cdfce61_output.json` - Baseline output
- `v3/continuity/continuity_baseline.csv` - Baseline continuity (10.16 avg)

---

## Next Steps After Analysis

### If pool5 is good (likely):
1. Use pool5 as the production solution
2. Generate final reports for Attendo
3. Optional: Run from-patch optimization to reduce empty shifts

### If pool5 has issues:
1. Wait for pool8 results
2. Use pool8 as safer alternative
3. Consider intermediate pool size (e.g., pool6 or pool7)

### If both pool5 and pool8 have issues:
1. Review what went wrong
2. Adjust pool sizes or strategy
3. May need to relax some constraints

---

## Expected Timeline

| Time | Event |
|------|-------|
| Now | pool3 analyzed, pool5/8 queued |
| +30 min | pool5 starts solving |
| +60 min | pool5 completes |
| +60 min | pool8 starts solving |
| +90 min | pool8 completes |
| +90 min | Final analysis & decision |

**Total ETA**: ~1.5-2 hours from now for complete results

---

**Current recommendation**: Wait for pool5, likely to be the winner with 3-4 avg continuity and <10% unassigned.
