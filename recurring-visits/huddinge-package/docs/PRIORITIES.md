# Huddinge Pipeline Priorities

Improvement roadmap for the recurring visit scheduling pipeline.

**Goal order (mandatory first):** Visits are mandatory. (1) Reach **0 unassigned** and **0 empty shifts**; (2) then run metrics and aim for **field efficiency > 67.5%**; (3) test **many different Timefold configs** to see how they affect metrics. Metrics from runs with unassigned visits or empty shifts are not valid for benchmarking. See README "Goal order" section.

**First priority = 0 unassigned:** From-patch only trims inactive/empty shifts; it does **not** add capacity. Unassigned count is unchanged after from-patch. To get 0 unassigned, **update the input** (step 1 or 2) with the shifts required: run `analyze_unassigned.py` on the solve output, then add shifts (e.g. `add_evening_vehicles.py` or source CSV), regenerate input, and solve again. Only after 0 unassigned run from-patch to trim empty shifts.

**Order of operations:** Validate input correctness → **add shifts to input until solve has 0 unassigned** → (optional) from-patch to trim empty → rebalance/tune → evaluate with accurate metrics.

---

## Priority 1: Input Correctness

**Goal:** Ensure the JSON input has no impossible problems. Bad input guarantees poor results regardless of solver or config.

### 1.1 Visit groups: overlapping time windows

**Requirement:** For multi-vehicle visits, both employees must be at the client at the same time. Visits in a group must have **overlapping** time windows. Non-overlapping windows = impossible to schedule.

| Check                                      | Script                            | Pass criteria  |
| ------------------------------------------ | --------------------------------- | -------------- |
| Source CSV: same weekday per visitGroup_id | `validate_source_visit_groups.py` | 73 OK, 0 FAIL  |
| Input JSON: pairwise overlap per group     | `validate_visit_groups.py`        | 144 OK, 0 FAIL |

```bash
# Or run all pre-solve checks at once:
./scripts/validate_pre_solve.sh

# Or individually:
python3 scripts/validate_source_visit_groups.py source/Huddinge_recurring_v2.csv
python3 scripts/validate_visit_groups.py solve/input_*.json
```

**Root cause of non-overlap:** Weekday text lives in `recurring_external` when `occurence` is empty. The expand script uses both columns. See README validation section.

### 1.2 Visit time windows

- `minStartTime` < `maxEndTime` (valid window)
- `maxStartTime` within `[minStartTime, maxEndTime]` when present
- Windows are in ISO 8601 with timezone (e.g. `2026-02-16T08:00:00+01:00`)

**Validation:** `validate_visit_groups.py` implicitly checks valid windows when testing overlap.

### 1.3 Shifts distributed to demand

**Requirement:** Shift coverage (days, times) should match visit demand. Mismatch causes unassigned visits or empty shifts.

| Aspect             | Source                                  | Notes                                                        |
| ------------------ | --------------------------------------- | ------------------------------------------------------------ |
| Shifts per weekday | `generate_employees.py`                 | Parses `occurence` / `recurring_external` for weekday        |
| Shift hours        | Source CSV `shift_start`, `shift_end`   | day: 07:00–15:00, evening: 16:00–22:00, weekend: 07:00–14:30 |
| Depot location     | `DEFAULT_OFFICE` in csv_to_timefold_fsr | Must match visit locations (Huddinge area)                   |

**Check:** Run `analyze_empty_shifts.py` — empty shifts that overlap unassigned visit windows indicate supply/demand mismatch.

```bash
python3 scripts/analyze_empty_shifts.py solve/input_*.json solve/output_*.json
```

### Pre-solve checklist

- [ ] `validate_source_visit_groups.py` → 0 FAIL
- [ ] `validate_visit_groups.py` → 0 FAIL
- [ ] `analyze_empty_shifts.py` — review empty vs unassigned overlap
- [ ] Confirm shift coverage matches planning window (2 or 4 weeks)

---

## Priority 2: Timefold FSR Configuration Profiles

**Goal:** Once the solution is feasible (0 unassigned, 0 empty shifts), try different solver profiles to improve **efficiency** (field efficiency > 67.5%). Edit profiles in the **Timefold Dashboard** — no need to modify the input JSON. Run multiple solves with different configs and compare metrics to see how weights and duration affect results.

### Profile location

- Dashboard: **Configuration profiles** (e.g. "Caire")
- File reference: `solve/tf/config.md` documents the current profile

### Key constraint weights (model configuration)

| Weight                                     | Default | Purpose                          | Tune for                                 |
| ------------------------------------------ | ------- | -------------------------------- | ---------------------------------------- |
| `minimizeTravelTimeWeight`                 | 1       | Less driving                     | Higher = reduce travel                   |
| `minimizeWaitingTimeWeight`                | 2       | Less waiting                     | Higher = tighter routing                 |
| `minimizeShiftCostsWeight`                 | 3       | Fewer shifts used                | Lower = allow more shifts to fill visits |
| `preferVisitsScheduledToEarliestDayWeight` | 3       | Front-load visits                | Adjust for movable visits                |
| `preferSchedulingOptionalVisitsWeight`     | 1       | Schedule optional visits         | Higher = more visits assigned            |
| `minimizeVisitCompletionRiskWeight`        | 2       | Prioritize high-priority earlier | Adjust if priorities matter              |
| `minimizeUnnecessarySkillsWeight`          | 1       | Avoid over-skilled techs         | Usually low                              |
| `minimizeTravelDistanceWeight`             | 0       | Distance vs time                 | 0 = ignore distance                      |

### Profile ideas to test

| Profile        | Focus                  | Suggested changes                                                        |
| -------------- | ---------------------- | ------------------------------------------------------------------------ |
| **Travel-min** | Minimize travel        | `minimizeTravelTimeWeight` 2–3                                           |
| **Assign-all** | Maximize assignments   | `preferSchedulingOptionalVisitsWeight` 2–3, `minimizeShiftCostsWeight` 1 |
| **Wait-min**   | Reduce waiting         | `minimizeWaitingTimeWeight` 3                                            |
| **Balanced**   | Current Caire defaults | As in config.md                                                          |

### Solve settings

- **Max solve duration:** 1h (PT1H) — increase for harder instances
- **Thread count:** 4
- **Maps:** Sweden (Car), OSRM

### How to apply

1. Open Timefold Dashboard → Route plan → Configuration
2. Select or create a profile
3. Edit weights and solve settings
4. Re-run solve (same input, new config)

---

## Priority 3: Rebalance Demand and Supply

**Goal:** Match shifts (supply) to visits (demand) over time. Reduce unassigned visits and empty shifts.

### Options

| Approach                 | When               | How                                                                            |
| ------------------------ | ------------------ | ------------------------------------------------------------------------------ |
| **Enhanced CSV**         | Structural change  | Add/remove shifts in source, regenerate                                        |
| **Input JSON edit**      | One-off tweak      | Add shifts, remove visits, or adjust time windows                              |
| **From-patch (FSR API)** | After 0 unassigned | Pin assigned visits, remove empty shifts, re-solve (does **not** add capacity) |

### 3.1 Enhanced CSV

- Edit `source/Huddinge_recurring_v2.csv`
- Add rows for new shifts (employee × weekday)
- Or mark inactive rows to exclude
- Re-run: `process_huddinge.py --weeks 2`

### 3.2 Input JSON edit

- Add vehicles/shifts to `modelInput.vehicles`
- Remove or relax visit time windows
- Add `add_monday_shifts.py` for extra Monday coverage

### 3.3 From-patch (ESS)

**Use only after the solve has 0 unassigned.** From-patch does not add capacity; it only trims empty shifts. If you still have unassigned visits, add shifts to the **input** (3.1 or 3.2) and re-solve first.

1. **Pin** all assigned visits
2. **End shifts at depot** (remove tail idle)
3. **Remove** empty shifts and empty vehicles
4. **Re-solve** with leaner fleet

```bash
python3 scripts/build_from_patch.py --output output.json --input input.json \
  --remove-empty-shifts --out ../from-patch/payload.json

python3 scripts/submit_to_timefold.py from-patch payload.json \
  --route-plan-id <id> --wait --save ../from-patch/output.json
```

### Demand/supply analysis

- **Empty shifts** = supply exceeds demand (or wrong day/time)
- **Unassigned visits** = demand exceeds supply (or impossible windows)
- **Overlap check** (`analyze_empty_shifts.py`): empty shifts that overlap unassigned windows suggest fixable mismatch
- **Supply vs config** (`analyze_unassigned.py`): unassigned with no overlapping shift → add shifts (placeholders); unassigned with overlapping (e.g. empty) shift → tune config. Aim for highest visit:travel first, then add placeholder shifts only for required visit+travel demand. Optionally plan movable visits for a specific shift type (day or evening) and add shifts to that demand so routing stays efficient.

---

## Priority 4: Metrics Accuracy

**Goal:** Metrics must be accurate for evaluation. Inaccurate metrics make comparisons meaningless.

### Time equation (must hold)

```
shift = visit + travel + wait + break + idle
```

All values in seconds (or hours). `idle` = inactive time (tail gap, empty shift).

### Metrics script sources

| Metric          | Source          | Field                                                         |
| --------------- | --------------- | ------------------------------------------------------------- |
| **Visit time**  | Shift itinerary | `effectiveServiceDuration` per VISIT item                     |
| **Travel time** | Shift metrics   | `totalTravelTime` (includes depot→first, between, last→depot) |
| **Wait time**   | Itinerary       | `startServiceTime` − `arrivalTime` per VISIT                  |
| **Break time**  | Itinerary       | BREAK items `endTime` − `startTime`                           |
| **Shift time**  | Input           | `minStartTime` to `maxEndTime` (scheduled, paid)              |
| **Inactive**    | Computed        | `shift − visit − travel − wait − break`                       |

### Efficiency definitions

| Metric                  | Formula                        | Notes                                 |
| ----------------------- | ------------------------------ | ------------------------------------- |
| **Staffing efficiency** | visit / (shift − break)        | Includes idle in denominator          |
| **Field efficiency**    | visit / (visit + travel)       | Target >67.5% (Slingor benchmark)     |
| **Assignable-used**     | visit / (shift − break − idle) | Use with `--exclude-inactive` for ESS |

### Verification

1. **Sanity check:** `visit + travel + wait + break + idle ≈ shift` (warn if >2% diff; small gaps can occur with input/output vehicle mismatch)
2. **Field efficiency:** Must be 0–100%; compare to 67.5% benchmark
3. **Per-shift CSV:** `metrics.py --csv out.csv` for manual spot-checks

### Cost and revenue (constants)

- **Cost:** 170 kr/h (all shift time paid)
- **Revenue:** 550 kr/h (visit time only)

Margin = visit_revenue − shift_cost. Used for economic comparison, not solver evaluation.

---

## Research Results — 2026-02-24

**Goal:** Map efficiency–continuity Pareto frontier for Huddinge 2-week (see `solve/research/pareto-frontier-2026-02-24.md`).

**Done:**
- Fetched iter1 runs (391486da, b288c5ed, 7632331d); metrics + continuity in `metrics/iter1/` and `solve/research/iter1-findings.md`.
- Added `patch_visits_slinga_direct.py` (patch FSR input with exact slinga requiredVehicles from expanded CSV).
- Approach 0 (direct slinga) submitted; plan ID `effb00f8-1aef-4440-b6bd-6e0436591ce1` — fetch when SOLVING_COMPLETED.
- Pool-size sweep N=1,2,3,5,8,15 submitted; plan IDs in `docs_2.0/recurring-visits/scripts/timefold_route_plan_ids.md` (research section).

**Next:** When all solves complete, run fetch + `solve_report.py` + `continuity_report.py` for Approach 0 and each sweep; fill pareto table and sweet-spot recommendation.
