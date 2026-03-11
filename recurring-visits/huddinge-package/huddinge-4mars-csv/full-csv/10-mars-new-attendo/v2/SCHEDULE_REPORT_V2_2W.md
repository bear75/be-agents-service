# V2 schedule report (2-week, 2026-03-02–15)

**Route plan ID:** `d2a6a01b-3309-4db5-ab4c-78ad1a218c19`  
**Report date:** 2026-03-11  
**Solver status at fetch:** SOLVING_ACTIVE (solution may improve if solve continues)

---

## 1. Summary

| Metric | Value |
|--------|--------|
| **Visits assigned** | 3 780 / 3 832 (98.6%) |
| **Unassigned** | 52 (unique visit IDs) |
| **Vehicles** | 41 |
| **Shifts** | 474 (452 with visits, 22 empty) |
| **Score** | 0hard / -520 000 medium / -11 559 356 soft |

---

## 2. Efficiency (idle not counted)

Metrics use **--exclude-inactive**: shift duration is taken from actual work (visit + travel + wait + break), so idle is excluded from the denominator and from cost.

- **Staffing efficiency** (visit / assignable time): **61.71%**  
  Assignable time = shift − break (2 675 h 38 min). Visit time = 1 651 h 2 min.

- **Field efficiency** (visit / (visit + travel)): **73.97%** (target >67.5%)  
  Visit:travel ratio = **2.84**.

- **Wait efficiency** (visit / (visit + travel + wait)): **61.71%**.

- **Idle:** not counted (excluded from efficiency and cost).

---

## 3. Cost and margin (idle not counted)

| Item | Time | Cost (kr) | Revenue (kr) |
|------|------|-----------|--------------|
| Active shift | 2 863 h 38 min | 658 636 | — |
| Visit (value) | 1 651 h 2 min | 379 738 | 908 068 |
| Travel | 580 h 52 min | 133 599 | — |
| Wait | 443 h 44 min | 102 059 | — |
| Break | 188 h 0 min | 43 240 | — |

- **Revenue:** 908 068 kr  
- **Cost (active only):** 658 636 kr  
- **Margin:** 249 433 kr (**27.47%**)

(Assumptions: 230 kr/h cost, 550 kr/h revenue per visit hour. Idle / inactive time excluded from cost.)

---

## 4. Unassigned visits (52 unique in this run; may be 47 in a newer solve)

### 4.0 Time-window and visitDependency feasibility

**All unassigned visits are possible within their time windows.** None are unassigned because of a visitDependency that is “too broad” for the visit’s time window.

- **48 of 52** unassigned have **no** `visitDependencies` (solo visits). For these, only the visit’s own time window matters; there is no dependency constraint.
- **4 of 52** unassigned have `visitDependencies` (all customer H034):
  - H034_r44_3 (preceding H034_r44_2, minDelay PT23H15M) → **ok** (slack 15 min)
  - H034_r44_6 (preceding H034_r44_5, minDelay PT23H15M) → **ok** (slack 15 min)
  - H034_r46_1 (preceding H034_r44_3, minDelay PT0M) → **ok** (slack 15 min)
  - H034_r46_6 (preceding H034_r44_6, minDelay PT0M) → **ok** (slack 15 min)

Feasibility rule: for each dependency, `prev_end + minDelay <= dep_latest_start` must hold for at least one same-day (or next-day) window pair. All four dependencies above satisfy this with ≥15 min slack. So the 52 (or 47) unassigned are a **solver/config** issue, not time-window or dependency infeasibility.

### 4.1 Classification

- **Supply (no overlapping shift):** 0  
  No unassigned slot has zero shifts in that time window → no need to add shifts for coverage.
- **Config (≥1 overlapping shift):** 64  
  Every unassigned slot has at least one shift that could in principle serve it → issue is **solver/config**, not lack of capacity.

### 4.2 Idle in window

- **22 of 64** unassigned slots have at least one overlapping shift with **idle/gap** in that window.  
  So capacity exists in time; the solver did not assign these (tuning/constraints).

### 4.3 By date (demand bucket: day / evening)

| Date | Config slots | Day | Evening |
|------|--------------|-----|---------|
| 2026-03-02 | 7 | 2 | 5 |
| 2026-03-03 | 7 | 5 | 2 |
| 2026-03-04 | 1 | 0 | 1 |
| 2026-03-05 | 3 | 1 | 2 |
| 2026-03-06 | 10 | 4 | 6 |
| 2026-03-07 | 2 | 0 | 2 |
| 2026-03-08 | 2 | 0 | 2 |
| 2026-03-09 | 6 | 2 | 4 |
| 2026-03-10 | 6 | 5 | 1 |
| 2026-03-11 | 4 | 0 | 4 |
| 2026-03-12 | 4 | 1 | 3 |
| 2026-03-13 | 9 | 4 | 5 |
| 2026-03-14 | 1 | 0 | 1 |
| 2026-03-15 | 2 | 0 | 2 |

Evening (Kväll) unassigned dominate; day unassigned concentrate on 03, 06, 09, 10, 12, 13.

### 4.4 Affected visit IDs (examples)

From `metrics/unassigned_visits.csv` (full list in that file):

- **H029** (r37): evening slots 04/10  
- **H034** (r44, r46): day slots 02, 03, 05, 09, 10, 12  
- **H086** (r156): evening 03, 13  
- **H157** (r253): evening 12, 14  
- **H269** (r351, r352): evening 02, 03  
- **H026** (r24, r25): evening 06, 07, 09 (Dubbel)  
- **H035** (r58, r59): evening 02, 05, 06, 08, 11, 13 (Dubbel)  
- **H301** (r423–r426): day 03, 06, 10, 13 and evening 02, 06, 09, 11, 12  

---

## 5. How to assign the unassigned visits

Because **all 64 unassigned slots are “config”** (overlapping shifts exist):

1. **Tune solver / configuration**
   - Reduce travel weight or adjust score so the solver prefers assigning these visits instead of leaving gaps.
   - Prefer movable visits to day/evening buckets so routing can use existing shifts better.
   - Allow longer solve time or more iterations so the solver can improve assignment.

2. **Use “idle in window” (22 slots)**  
   For the 22 slots where a shift has idle time in the unassigned window:
   - The solver could assign but did not (constraints or scoring).
   - Check dependencies, skills, and time windows for those visits; relax or reweight if acceptable.
   - Consider from-patch or manual pinning of high-priority unassigned visits to specific shifts that have idle in that window.

3. **Do not add shifts for coverage**  
   Supply is sufficient (0 “supply” slots); adding shifts would increase cost without fixing the 52 unassigned.

4. **Re-fetch after solve completes**  
   With status SOLVING_ACTIVE, the solution can still improve. Re-run fetch + metrics + `analyze_unassigned.py` when status is SOLVING_COMPLETED and optionally compare.

---

## 6. Artifacts and commands

- **Output:** `v2/output/d2a6a01b-3309-4db5-ab4c-78ad1a218c19_output.json`
- **Input:** `v2/input_v2_81_2w.json`
- **Metrics:** `v2/metrics/metrics_report_d2a6a01b.txt`, `v2/metrics/metrics_*_d2a6a01b.json`
- **Unassigned CSV:** `v2/metrics/unassigned_visits.csv`

**Re-run metrics (e.g. after solve completes):**

```bash
cd be-agent-service/recurring-visits

# Fetch latest solution and run metrics
python3 scripts/fetch_timefold_solution.py d2a6a01b-3309-4db5-ab4c-78ad1a218c19 \
  --save huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/output/d2a6a01b-3309-4db5-ab4c-78ad1a218c19_output.json \
  --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/input_v2_81_2w.json \
  --metrics-dir huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/metrics

# Metrics only (if output already saved)
python3 scripts/metrics.py huddinge-package/.../v2/output/d2a6a01b-3309-4db5-ab4c-78ad1a218c19_output.json \
  --input huddinge-package/.../v2/input_v2_81_2w.json \
  --save huddinge-package/.../v2/metrics

# Unassigned analysis
python3 scripts/analyze_unassigned.py huddinge-package/.../v2/input_v2_81_2w.json \
  huddinge-package/.../v2/output/d2a6a01b-3309-4db5-ab4c-78ad1a218c19_output.json \
  --csv huddinge-package/.../v2/metrics/unassigned_visits.csv
```

---

## 7. References

- E2E pipeline: `10-mars-new-attendo/E2E_RUN_10MARS.md` (V2 section)
- Metrics definitions: `recurring-visits/scripts/metrics.py` (efficiency, cost, time equation)
- Unassigned logic: `recurring-visits/scripts/analyze_unassigned.py` (supply vs config, idle in window)
