# v3 Campaign Status

**Started**: 2026-03-13 18:20
**Baseline Route Plan**: 4cdfce61-0d2d-46e0-9c16-674a7b9dab0f

---

## Baseline Results (v3_FIXED)

### Continuity Analysis
- **Average**: **10.16 employees/client** ⚠️ (target: 2-3)
- **Total clients**: 176
- **Total visits**: 3,739
- **Vehicles**: 41

### Top Worst Cases
| Client | Visits | Employees | CCI |
|--------|--------|-----------|-----|
| H026 | 115 | **33** | 0.0506 |
| H055 | 91 | **33** | 0.0397 |
| H086 | 95 | **34** | 0.0391 |
| H290 | 90 | **34** | 0.0422 |
| H035 | 120 | **30** | 0.0506 |

**This is worse than v2 baseline (4.3 avg)**

---

## Campaign Variants

### Track: Pool Size Variants (requiredVehicles)

| Variant | Pool Size | Strategy | Status | PID | Target Continuity |
|---------|-----------|----------|--------|-----|-------------------|
| **pool3_required** | 3 | requiredVehicles | 🔄 Solving | 11787 | 2-3 employees |
| **pool5_required** | 5 | requiredVehicles | 🔄 Solving | 11788 | 3-4 employees |
| **pool8_required** | 8 | requiredVehicles | 🔄 Solving | 11789 | 4-5 employees |

---

## Expected Results

### Pool 3 (Most Aggressive)
- **Target continuity**: 2-3 avg employees/client
- **Max continuity**: ≤6 employees
- **Risk**: May increase unassigned visits (less flexibility)
- **Best for**: Maximum continuity of care

### Pool 5 (Balanced)
- **Target continuity**: 3-4 avg employees/client
- **Max continuity**: ≤8 employees
- **Risk**: Moderate - good balance
- **Best for**: Recommended starting point

### Pool 8 (Conservative)
- **Target continuity**: 4-5 avg employees/client
- **Max continuity**: ≤10 employees
- **Risk**: Low - high flexibility
- **Best for**: High efficiency with improved continuity

---

## Comparison with v2 Baseline

| Metric | v2 (81 clients) | v3 Baseline | v3 Target |
|--------|-----------------|-------------|-----------|
| **Avg continuity** | 4.3 | **10.16** ⚠️ | 2-3 ✅ |
| **Max continuity** | 10 | **34** ⚠️ | ≤6 ✅ |
| **Field efficiency** | 73.25% | TBD | ≥67.5% |

---

## Monitoring

### Check Logs
```bash
# All variants
tail -f huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/logs/*.log

# Specific variant
tail -f huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/logs/pool5_required.log
```

### Check Processes
```bash
ps aux | grep submit_to_timefold | grep -v grep
```

### Files
```
v3/
├── input_v3_FIXED.json                    # Baseline input
├── output_FIXED/
│   └── 4cdfce61_output.json              # Baseline output (10.16 avg)
├── continuity/
│   ├── continuity_baseline.csv           # Full continuity analysis
│   ├── pools/
│   │   ├── pool3.json                    # Top 3 vehicles per client
│   │   ├── pool5.json                    # Top 5 vehicles per client
│   │   └── pool8.json                    # Top 8 vehicles per client
│   ├── variants/
│   │   ├── input_pool3_required.json     # 🔄 Solving
│   │   ├── input_pool5_required.json     # 🔄 Solving
│   │   └── input_pool8_required.json     # 🔄 Solving
│   ├── results/                          # Will contain outputs
│   │   ├── pool3_required/
│   │   ├── pool5_required/
│   │   └── pool8_required/
│   └── logs/                             # Solve logs
│       ├── pool3_required.log
│       ├── pool5_required.log
│       └── pool8_required.log
```

---

## Timeline

| Time | Event | Status |
|------|-------|--------|
| 18:00 | v3_FIXED completed | ✅ Done |
| 18:17 | Baseline analysis | ✅ Done (10.16 avg) |
| 18:20 | Build continuity pools | ✅ Done |
| 18:21 | Submit 3 variants | ✅ Running |
| ~18:50-19:20 | Variants complete | ⏳ Pending |
| 19:20-19:30 | Analysis & comparison | ⏳ Pending |
| 19:30 | Final recommendation | ⏳ Pending |

**Estimated completion**: 19:30

---

## Success Criteria

### Minimum Success
- ✅ At least 1 variant achieves <8 avg continuity (better than baseline)
- ✅ Field efficiency ≥67.5%
- ✅ Unassigned <10%

### Target Success
- ✅ At least 1 variant achieves <5 avg continuity
- ✅ Field efficiency ≥70%
- ✅ Unassigned <5%

### Stretch Goal
- ✅ pool3 or pool5 achieves 2-3 avg continuity
- ✅ Field efficiency ≥73%
- ✅ Max continuity ≤6

---

**Monitor progress**: `tail -f v3/continuity/logs/*.log`
