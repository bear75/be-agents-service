# v3 Campaign Summary

**Date**: 2026-03-13
**Status**: Phase 2 continuity optimization in progress

---

## What We Did

### Phase 1: Schedule Fixes ✅ COMPLETE

**Input**: Huddinge v3 CSV (115 clients, 664 rows)
**Output**: v3_FIXED (`4cdfce61-0d2d-46e0-9c16-674a7b9dab0f`)

**Fixes Applied**:
1. ✅ "Exakt dag/tid" recognition → minimal 1-min flex
2. ✅ Empty före/efter for critical tasks → minimal flex
3. ✅ Same-day PT0M dependencies → 1173 dependencies added
4. ✅ All zero-flex violations fixed (78 visits)

**Verification**:
- ✅ 2165 total dependencies (946 → 2165, +129%)
- ✅ 1173 PT0M dependencies (prevent temporal overlaps)
- ✅ 992 timed dependencies (from CSV)
- ✅ All time windows correct
- ✅ Client notes issues resolved

**Problem Discovered**:
- ❌ **Continuity: 10.16 avg employees/client** (should be 2-3!)
- ❌ **Worst case: 33 employees** for one client
- ❌ **Much worse than v2** (which had 4.3 avg)

### Phase 2: Continuity Optimization 🔄 IN PROGRESS

**Strategy**: requiredVehicles constraint (limit employee pool per client)

**Variants Submitted** (parallel):

| Variant | Route Plan ID | Pool | Target | Status | Result |
|---------|---------------|------|--------|--------|--------|
| pool3_required | 30c39aef-127f-... | 3 | 2-3 employees | 🔄 SOLVING_ACTIVE | ✅ 1.76 avg BUT ❌ 25.7% unassigned |
| pool5_required | cae24e29-d23a-... | 5 | 3-4 employees | ⏳ SCHEDULED | Pending |
| pool8_required | ba5411e1-c77c-... | 8 | 4-5 employees | ⏳ SCHEDULED | Pending |

**pool3 Initial Results**:
- ✅ **Excellent continuity: 1.76 avg** (target: 2-3)
- ❌ **High unassigned: 983 visits (25.7%)**
- ⚠️ **Verdict**: Too aggressive, wait for pool5

**Next**: pool5 and pool8 still queued, will start sequentially

---

## Key Learnings

### 1. Tags vs requiredVehicles ✅ CORRECTED

**What I said initially** (WRONG):
- ❌ "Tags don't work in FSR schema"

**What's actually true**:
- ✅ Tags on **VISITS** don't work (schema violation)
- ✅ Tags on **VEHICLES** + requiredTags on visits DOES work
- ✅ requiredVehicles on visits also works (what we're using)

### 2. PT0M Dependencies ✅ CORRECTED

**What I said initially** (WRONG):
- ❌ "Two employees at same location is physically impossible"

**What's actually true**:
- ✅ Multiple people CAN be at same location (visit groups!)
- ❌ ONE person in TWO places is impossible
- ✅ PT0M prevents same EMPLOYEE having overlapping tasks
- ✅ PT0M does NOT prevent different employees at same location

### 3. Dependency Increase: 946 → 2165 ✅ VERIFIED CORRECT

**Breakdown**:
- 992 timed dependencies (from CSV `antal_tim_mellan`)
- **1173 PT0M** dependencies (Fix 3 - same-day sequencing)

**Why this is correct**:
- More clients (81 → 115 = +42%)
- Fix 3 intentionally adds PT0M to prevent overlaps
- Prevents same employee being scheduled for overlapping tasks

### 4. Continuity Baseline is Poor

**v3_FIXED continuity**: 10.16 avg (vs v2: 4.3 avg)

**Why worse**:
- More clients (115 vs 81)
- No continuity constraints yet
- Natural clustering from travel optimization isn't enough

**Solution**: requiredVehicles constraint (Phase 2)

---

## Files Created

### Documentation
- `SCHEDULE_ANALYSIS.md` - Root cause analysis
- `FIXES_IMPLEMENTED.md` - Technical implementation
- `REGENERATION_SUMMARY.md` - Geocoding & continuity Q&A
- `CSV_TO_JSON_VERIFICATION.md` - Verification methodology
- `VERIFICATION_RESULTS.md` - Detailed verification
- `PT0M_EXPLANATION.md` - PT0M dependencies explained
- `CORRECTIONS.md` - Corrections to misunderstandings
- `CAMPAIGN_MATRIX_V3.md` - Campaign strategy
- `CAMPAIGN_STATUS.md` - Live status
- `PARALLEL_SOLVES_ACTIVE.md` - Active solves tracking
- `PHASE2_STATUS_UPDATE.md` - Phase 2 results and analysis
- `EMAIL_TILL_ATTENDO.md` - Email to Attendo (Swedish)
- `EMAIL_KORT_VERSION.txt` - Short email version
- `SUMMARY.md` - This file

### Scripts
- `verify_csv_to_json.py` - Automated verification
- `run_continuity_optimization.sh` - Phase 2 workflow
- `launch_campaign.sh` - Campaign automation

### Data
- `input_v3_FIXED.json` - Baseline input (3,832 visits)
- `output_FIXED/4cdfce61_output.json` - Baseline output
- `continuity/continuity_baseline.csv` - Baseline analysis
- `continuity/pools/pool*.json` - Continuity pools (3, 5, 8)
- `continuity/variants/input_pool*_required.json` - Variant inputs
- `continuity/results/pool3_required/30c39aef_output.json` - pool3 output
- `continuity/results/pool3_required/continuity_pool3.csv` - pool3 analysis
- `continuity/results/COMPARISON_TABLE.md` - Cross-variant comparison

---

## Actual Results (pool3) and Expected Results (pool5/pool8)

### pool3_required - ACTUAL RESULTS ✅ Continuity ❌ Coverage

**Continuity** (ACTUAL):
- Average: **1.76 employees/client** ✅✅ (better than target!)
- Max: **3 employees** ✅✅ (much better than 33 baseline)
- Improvement: **83% reduction** from baseline

**Efficiency** (ACTUAL):
- Assigned: **2,849 / 3,832 (74.3%)** ❌
- Unassigned: **983 visits (25.7%)** ❌ (too high!)
- Clients served: **168 / 176** ⚠️ (8 clients completely unserved)

**Schedule Quality**:
- ✅ All time windows correct (from v3_FIXED)
- ✅ No same-day overlaps (PT0M dependencies)
- ✅ Exact times respected ("Exakt dag/tid")
- ✅ Critical tasks have minimal flex

**Verdict**: Pool3 proves the concept works but is too aggressive for production.

### Expected pool5 Results (Balanced - LIKELY WINNER)

**Continuity** (expected):
- Average: **3-4 employees/client** ✅ (vs 10.16 baseline)
- Max: **≤6 employees** ✅ (vs 33 baseline)
- Improvement: **60-70% reduction**

**Efficiency** (expected):
- Assigned: **≥90%** ✅ (~3,450 visits)
- Unassigned: **<10%** ✅ (<383 visits)
- Clients served: **176 / 176** ✅

**Schedule Quality**:
- ✅ All time windows correct (from v3_FIXED)
- ✅ No same-day overlaps (PT0M dependencies)
- ✅ Exact times respected ("Exakt dag/tid")
- ✅ Critical tasks have minimal flex

### Expected pool8 Results (Conservative - SAFE FALLBACK)

**Continuity** (expected):
- Average: **4-5 employees/client** ✅ (vs 10.16 baseline)
- Max: **≤8 employees** ✅ (vs 33 baseline)
- Improvement: **50-60% reduction**

**Efficiency** (expected):
- Assigned: **≥95%** ✅ (~3,640 visits)
- Unassigned: **<5%** ✅ (<192 visits)
- Clients served: **176 / 176** ✅

**Schedule Quality**: Same as pool5 ✅

### Comparison Table

| Metric | v2 (81 clients) | v3 Baseline | pool3 (aggressive) | v3 Target (pool5) | v3 Expected (pool5/8) |
|--------|-----------------|-------------|-------------------|-------------------|------------------------|
| **Clients** | 81 | 115 | 168 (8 unserved) | 115 | 115 |
| **Avg continuity** | 4.3 | **10.16** ⚠️ | **1.76** ✅✅ | 2-3 | **3-4** ✅ |
| **Max continuity** | 10 | **33** ⚠️ | **3** ✅ | ≤6 | **≤8** ✅ |
| **Assigned rate** | ~97% | 97.6% | **74.3%** ❌ | ≥90% | **≥90%** ✅ |
| **Unassigned** | ~3% | 93 (2.4%) | **983 (25.7%)** ❌ | <10% | **<10%** ✅ |
| **Field efficiency** | 73.25% | TBD | TBD | ≥67.5% | **≥70%** ✅ |
| **Time windows** | ❌ Issues | ✅ Fixed | ✅ Fixed | ✅ Correct | ✅ Correct |
| **Same-day overlaps** | ❌ Issues | ✅ Fixed | ✅ Fixed | ✅ None | ✅ None |

**pool3 verdict**: Excellent continuity (1.76 avg!) but unassigned rate too high (25.7%). Waiting for pool5.

---

## Next Steps

### When Solves Complete (~18:52)

1. **Fetch solutions**
   ```bash
   python3 scripts/fetch_timefold_solution.py 30c39aef-127f-... --save pool3_output.json
   python3 scripts/fetch_timefold_solution.py cae24e29-d23a-... --save pool5_output.json
   python3 scripts/fetch_timefold_solution.py ba5411e1-c77c-... --save pool8_output.json
   ```

2. **Analyze continuity**
   ```bash
   python3 scripts/continuity_report.py --input pool3_input.json --output pool3_output.json --report pool3_continuity.csv
   # Repeat for pool5 and pool8
   ```

3. **Compare results**
   - Which variant has best continuity?
   - Which has best efficiency?
   - Which is the balanced winner?

4. **Optional: From-patch optimization**
   - Eliminate empty shifts (like in v2 campaign)
   - Improve assignment rate
   - Maintain continuity

5. **Deploy winner**
   - Likely pool5_required
   - Expected: 3-4 avg continuity, 70%+ efficiency
   - Use for production scheduling

---

## Success Criteria

### ✅ Phase 1 Success
- [x] Schedule fixes implemented
- [x] All time windows correct
- [x] No same-day overlaps
- [x] Dependencies verified (2165 total)

### 🔄 Phase 2 Success (Partial - pool3 complete)
- [x] At least 1 variant achieves <5 avg continuity (**pool3: 1.76** ✅✅)
- [ ] Assigned ≥90% (**pool3: 74.3%** ❌ - need pool5/pool8)
- [ ] Unassigned <10% (**pool3: 25.7%** ❌ - need pool5/pool8)
- [x] Max continuity ≤8 (**pool3: 3** ✅✅)

### 🎯 Stretch Goals (pool3 exceeded!)
- [x] pool3 achieves <2 avg continuity (**1.76** ✅✅)
- [ ] Field efficiency ≥73% (TBD - waiting for pool5/8)
- [ ] Unassigned <5% (**pool3: 25.7%** ❌ - need pool5/8)
- [x] Max continuity ≤6 (**pool3: 3** ✅✅)

**pool3 proves**: Excellent continuity is achievable with requiredVehicles!
**Waiting for**: pool5 to balance continuity + coverage

---

## Monitoring

**Live logs**:
```bash
tail -f v3/continuity/logs/*.log
```

**Check status**:
```bash
ps aux | grep submit_to_timefold
```

**Estimated completion**: 18:52 (30 minutes from 18:22)

---

**Status**: ✅ Phase 1 complete, 🔄 Phase 2 in progress (pool3 analyzed, pool5/8 queued)
**Latest**: pool3 shows excellent continuity (1.76 avg) but high unassigned (25.7%)
**Next**: Waiting for pool5 to start (expected to be the winner)
