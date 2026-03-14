# Parallel Solves Active - v3 Campaign

**Time**: 2026-03-13 18:22
**Status**: ✅ 3 variants solving in parallel

---

## Active Solves

| Variant | Route Plan ID | Status | Pool Size | Expected Continuity |
|---------|---------------|--------|-----------|---------------------|
| **pool3_required** | `30c39aef-127f-4411-ab9b-4453f2f3f7b6` | 🔄 SOLVING | 3 | **2-3 employees** |
| **pool5_required** | `cae24e29-d23a-46cd-9a86-5d267dbf22d9` | 🔄 SOLVING | 5 | **3-4 employees** |
| **pool8_required** | `ba5411e1-c77c-4d67-99bd-4a06e64e1f42` | 🔄 SOLVING | 8 | **4-5 employees** |

---

## Baseline for Comparison

**v3_FIXED** (`4cdfce61-0d2d-46e0-9c16-674a7b9dab0f`):
- Average continuity: **10.16 employees/client** ⚠️
- Worst case: **H026 = 33 employees**
- Total visits: 3,739
- Unassigned: 93 (2.5%)

**Target**: Reduce avg continuity to 2-3 employees/client

---

## How requiredVehicles Works

Each variant limits which employees can serve each client:

### Pool 3 (Most Aggressive)
```json
{
  "id": "H015_r1_1",
  "name": "H015 Morgon...",
  "requiredVehicles": ["Dag_01_Central_1", "Dag_02_Central_2", "Kväll_01_Central"]
}
```

**Effect**: H015 visits can ONLY be assigned to these 3 specific employees
**Expected**: 2-3 employees (from top 3 in baseline)

### Pool 5 (Balanced)
```json
{
  "id": "H015_r1_1",
  "requiredVehicles": ["Dag_01_Central_1", "Dag_02_Central_2", "Dag_05_Flemingsberg_1", "Kväll_01_Central", "Kväll_02_Kvarnen"]
}
```

**Effect**: H015 visits limited to top 5 employees
**Expected**: 3-4 employees (more flexibility than pool3)

### Pool 8 (Conservative)
```json
{
  "id": "H015_r1_1",
  "requiredVehicles": [/* top 8 employees */]
}
```

**Effect**: H015 visits limited to top 8 employees
**Expected**: 4-5 employees (most flexibility)

---

## Expected Trade-offs

### Pool 3 (Strictest)
✅ **Best continuity**: 2-3 avg
❌ **Higher risk**: May increase unassigned visits (less flexibility)
✅ **Best for**: Clients needing maximum consistency

### Pool 5 (Recommended)
✅ **Good continuity**: 3-4 avg
✅ **Balanced risk**: Moderate flexibility
✅ **Best for**: Most scenarios

### Pool 8 (Safest)
✅ **Improved continuity**: 4-5 avg (vs 10.16 baseline)
✅ **Low risk**: High flexibility
✅ **Best for**: High efficiency priority

---

## Monitoring

### Live Progress
```bash
# Watch all solves
tail -f huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/logs/*.log

# Watch specific solve
tail -f huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/logs/pool5_required.log
```

### Check Status
```bash
cd /Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits

# Fetch current state
python3 scripts/fetch_timefold_solution.py 30c39aef-127f-4411-ab9b-4453f2f3f7b6  # pool3
python3 scripts/fetch_timefold_solution.py cae24e29-d23a-46cd-9a86-5d267dbf22d9  # pool5
python3 scripts/fetch_timefold_solution.py ba5411e1-c77c-4d67-99bd-4a06e64e1f42  # pool8
```

---

## When Solves Complete

### Analysis Commands

For each completed variant:

```bash
cd /Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits

# 1. Fetch solution
python3 scripts/fetch_timefold_solution.py <route_plan_id> \
  --save v3/continuity/results/<variant>/<route_plan_id>_output.json

# 2. Analyze continuity
python3 scripts/continuity_report.py \
  --input v3/continuity/variants/input_<variant>.json \
  --output v3/continuity/results/<variant>/<route_plan_id>_output.json \
  --report v3/continuity/results/<variant>/continuity.csv

# 3. View results
head -20 v3/continuity/results/<variant>/continuity.csv

# 4. Compare with baseline
echo "Baseline: 10.16 avg"
echo "New: $(awk -F, 'NR>1 {sum+=$3; count++} END {printf "%.2f", sum/count}' v3/continuity/results/<variant>/continuity.csv) avg"
```

---

## Expected Timeline

| Time | Event |
|------|-------|
| 18:22 | All variants submitted ✅ |
| 18:52 | Solves complete (estimated 30 min) |
| 18:52-19:00 | Fetch solutions and analyze |
| 19:00 | Compare results |
| 19:05 | Select winning variant |

---

## Success Metrics

### pool3_required (Aggressive)
- ✅ **Target**: 2-3 avg continuity
- ✅ **Max**: ≤6 employees per client
- ⚠️ **Watch**: Unassigned visits (should be <10%)

### pool5_required (Balanced - Recommended)
- ✅ **Target**: 3-4 avg continuity
- ✅ **Max**: ≤8 employees per client
- ✅ **Watch**: Efficiency + unassigned

### pool8_required (Conservative)
- ✅ **Target**: 4-5 avg continuity (vs 10.16 baseline)
- ✅ **Max**: ≤10 employees per client
- ✅ **Watch**: Should have lowest unassigned

---

## Files

```
v3/
├── input_v3_FIXED.json               # Baseline (schedule fixes)
├── output_FIXED/
│   └── 4cdfce61_output.json         # Baseline (10.16 avg continuity)
├── continuity/
│   ├── continuity_baseline.csv      # Full baseline analysis
│   ├── pools/
│   │   ├── pool3.json               # Client → top 3 vehicles
│   │   ├── pool5.json               # Client → top 5 vehicles
│   │   └── pool8.json               # Client → top 8 vehicles
│   ├── variants/
│   │   ├── input_pool3_required.json  # 🔄 Solving (30c39aef)
│   │   ├── input_pool5_required.json  # 🔄 Solving (cae24e29)
│   │   └── input_pool8_required.json  # 🔄 Solving (ba5411e1)
│   ├── results/
│   │   ├── pool3_required/          # ⏳ Will contain output + analysis
│   │   ├── pool5_required/          # ⏳ Will contain output + analysis
│   │   └── pool8_required/          # ⏳ Will contain output + analysis
│   └── logs/
│       ├── pool3_required.log       # Live solve log
│       ├── pool5_required.log       # Live solve log
│       └── pool8_required.log       # Live solve log
```

---

## What Happens Next

1. ⏳ **Wait ~30 min** for solves to complete (ETA: 18:52)
2. 📊 **Analyze results** - continuity, efficiency, unassigned
3. 🏆 **Select winner** - likely pool5 (balanced)
4. 🔧 **Optional**: From-patch optimization to eliminate empty shifts
5. ✅ **Deploy** - use winning variant for production

---

**Current Status**: ✅ All 3 variants solving in parallel
**Estimated Completion**: 18:52 (30 minutes)
**Monitor**: `tail -f v3/continuity/logs/*.log`
