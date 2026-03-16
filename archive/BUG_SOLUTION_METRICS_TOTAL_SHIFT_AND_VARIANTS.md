# Bug report: Solution metrics – wrong total shift & three shift variants

**To:** Shridhar  
**Date:** 2026-03-09  
**Related Jira 2.0:** See [JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES.md](../05-prd/JIRA_2.0_USER_STORIES_SCHEMA_RESOURCES.md#solution-metrics-bug--shift-variants).

**Note:** The metrics script and bug dataset live in the **be-agent-service** repo (private). When sharing this report, the relevant files are **attached** so recipients can run the script and reproduce the reference values without repo access.

---

## 1. Summary

The Caire UI shows incorrect solution-level metrics (Total shift, Utilization, Total break, Travel). Per-employee metrics are correct. Root cause: **Total shift** is computed from event time spans instead of actual shift lengths. This is a **bug** (quick fix required). Separately, we need **two new metric variants** (active shifts, field time) as feature requests until the “remove empty shifts from patch” scenario is implemented.

**Data source:** Metrics must always be calculated from the **solution** (optimizer output). The input/schedule is used only as reference (e.g. unassigned visit count). No mixing of input vs solution for the same metric.

**Display:** Use **hours and minutes** for all human-facing duration values (e.g. `1 082 h 15 min`) for consistency.

---

## 2. The total-shift bug (explained)

**Current UI:** Total shift (min) ≈ **744 930** → Utilization ≈ **8.7%**.

**Expected (for “all shifts”):** ~**75 000–76 000 min** (~1 261 h) for this 4-week solution.

**Cause:** In the solution metrics service, “total shift” is computed as:

- For each **employee**: (last solution event time − first solution event time).
- **Sum** those spans over all employees.

Over a **4-week** schedule that becomes “sum of up to 4 weeks per employee” (e.g. 24 × ~4 weeks in minutes ≈ 744k). So we are **not** summing shift lengths; we are summing **per-employee calendar span** (earliest-to-latest event). Shift length is (shift end − shift start) per shift; the shift **ends when the employee arrives at the end location (office/depot)** after the last visit, not at the last visit end.

**Correct “all shifts”:** Sum over **every shift** in the solution of (shift end − shift start), where shift end = arrival at end location. Use **shift boundaries** from the solution (or schedule), not (first event, last event) per employee.

**Fix:** Compute total shift from **shift start/end** (solution or schedule), not from event min/max per employee. Then Utilization (visit / total shift) will be correct.

---

## 3. Three shift metrics (definitions)

Across all three variants:

- **Visit count and visit time** are the same (from solution).
- **Travel and wait totals** are the same (from solution).
- **Only shift time and break time** differ by variant. Idle is implied: idle = shift − (visit + travel + wait + break). Break rules per variant below.

| Variant                     | Name (suggested)                            | Shift definition                                                                                                                                                                                                                                                                                                                         | Break rule                                                                                                                                                                   |
| --------------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. All shifts**           | **All shift hours** (or “Total shift”)      | Sum of (shift end − shift start) for **all** shifts. Shift end = arrival at end location (office). Includes empty shifts and tail idle.                                                                                                                                                                                                  | All breaks in the solution (every shift that has a break).                                                                                                                   |
| **2. Active shifts**        | **Active shift hours** (shifts with visits) | Same as above but only for shifts that have **at least one visit**. Still includes tail idle (from last visit to arrival at office).                                                                                                                                                                                                     | Include break if the shift has visits, **no matter the order** (before, between, or after visits). Empty shifts contribute no break.                                         |
| **3. Field time (no idle)** | **Field time** (or “Assignable time”)       | Exclude (a) **empty shifts** entirely, (b) **tail idle**: for each shift, shift end = **arrival at end location** (office) after last visit—so we do **not** count idle time from “last visit end” to “arrival at office”. In other words: only count time that is visit, travel, wait, or break; shift ends when they arrive at office. | Only break if the shift has **at least one visit after the break**. Tail break (e.g. last visit ends 10, break 11–14) **excluded** in C but **included** in B. So 1 ≥ 2 ≥ 3. |

- **3.1** = **Bug:** current “total shift” uses wrong formula (event span). Fix: use shift boundaries for “All shift hours.”
- **3.2** and **3.3** = **New feature requests** (quick fix until “scenario remove empty shifts from patch” is implemented).

---

### 3a. How shift and break are calculated per variant

Break and shift are always taken from the **solution** (itinerary + shift boundaries). The only difference between variants is **which shifts** contribute to the totals.

| Variant              | Which shifts count?                            | Total shift =                                                                                                               | Total break =                                                                                                     |
| -------------------- | ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **1. All shifts**    | **All** shifts (incl. empty, incl. break-only) | Sum of (shift end − shift start) for every shift. Shift end = arrival at end location.                                      | Sum of break time in **every** shift that has a break in the solution (incl. break-only shifts).                  |
| **2. Active shifts** | Only shifts with **≥ 1 visit**                 | Same as variant 1 but only over those shifts.                                                                               | Break in those shifts **no matter the order** (before, between, or after visits). Break-only shifts contribute 0. |
| **3. Field time**    | Only shifts with ≥ 1 visit; no tail idle       | Sum of (visit + travel + wait + break) per shift; shift end = arrival at end location. Empty shifts and tail idle excluded. | Only break that has **at least one visit after it** in the shift. Tail break (after last visit end) **excluded**. |

So:

- **Break total:** **1 ≥ 2 ≥ 3.** A = all breaks. B = break in any shift with visits (order doesn’t matter). C = only break that has a visit after it (tail break excluded). Example: last visit ends 10, break 11–14 → included in B, excluded in C.
- **Shift total:** Variant 1 = all scheduled shift length (incl. empty and idle). Variant 2 = same definition, only over shifts with visits. Variant 3 = only "used" time (visit+travel+wait+break), no empty shifts and no tail idle.

### 3b. Script note: itinerary vs API for break (break-only shifts)

In the reference script (`metrics.py`), break time is first summed from the **itinerary** (each item with `kind: "BREAK"`). The Timefold API also returns per-shift `metrics.totalBreakDuration`, but for **break-only shifts** (no visits) it often returns `"PT0S"`. If the script overwrote with that, break-only shifts would contribute 0.

**Change in script:** Use the API's `totalBreakDuration` only when it is **> 0**; otherwise keep the break already computed from the itinerary. Then break-only shifts (e.g. shift `5815ff36`) add their break to total break and, in the output-only run, to total shift (because for those shifts shift = break when there is no visit/travel/wait).

That is why the **output-only** reference numbers increased after the fix: before, only breaks from shifts where the API reported break (typically shifts with visits) were counted (~110 h); after, all breaks in the solution are counted (~261 h), including those in break-only shifts.

### 3c. Example: tail break (last visit 10, break 11–14)

One shift: last visit ends at 10, break 11–14 (after the last visit).

- **A (Variant 1):** All breaks → this break **included**.
- **B (Variant 2):** Break if the shift has visits, no matter the order → shift has visits, so this break **included**.
- **C (Variant 3):** Only break that has at least one visit **after** it → no visit after 11–14, so this break **excluded** (tail break).

So the same break is in A and B but not in C. That gives **1 ≥ 2 ≥ 3** and "when removing idle / field time, breaks do not increase."

---

## 4. Other issues

- **Total break:** UI ~15 660 min vs solution-derived ~6 615 min. Likely using schedule breaks or double-count. Breaks must follow the three variants above (all shifts vs active shifts vs field time).
- **Travel:** UI ~54 h vs reference ~60 h 42 min. Align source (solution itinerary events) and duration parsing (e.g. PT…S seconds).
- **Units:** Use **hours and minutes** for human-facing format everywhere (e.g. `1 082 h 15 min`, not mixed “X h Y min” and “Z min” for the same kind of metric).

---

## 5. Reference: metrics from Python (expected values)

**Script:** `metrics.py` (from `be-agent-service/recurring-visits/scripts/` — repo is private; script is **attached** with this report). Run: `python metrics.py <output.json> [--input <input.json>]`.

**Does the solution have idle?** Yes. The solution has **243 empty shifts** (no visits) and **1 empty vehicle**. The output JSON only contains itinerary _events_ (visit, travel, wait, break) for time that was used. Empty shifts have no visit/travel in the output, and tail idle (last visit → arrival at office) is not emitted as events. So when metrics run **without input**, the script only sums time that appears in the output → total shift = visit+travel+wait+break, idle = 0. **The three variants are not the same** when we use input (schedule): variant 1 = all shifts (3 827 h, 2 565 h idle); variant 2 = active shifts only; variant 3 = field time (1 261 h, no idle counted).

### Values common to all three variants (from solution)

Visit count, visit time, travel, and wait are the same for all variants (from solution itinerary).

| Metric                                         | Value                              | Notes                            |
| ---------------------------------------------- | ---------------------------------- | -------------------------------- |
| **Visit (service) time**                       | 1 082 h 15 min                     | Same for all three variants.     |
| **Travel**                                     | 60 h 42 min                        | From solution itinerary.         |
| **Wait**                                       | 8 h 14 min                         | From solution.                   |
| **Employees (vehicles)**                       | 24 (empty: 1)                      |                                  |
| **Shifts**                                     | 456 (with visits: 213, empty: 243) |                                  |
| **Visits assigned**                            | 2 750 / 2 762                      | Unassigned: 12.                  |
| **Travel efficiency (visit / (visit+travel))** | 94.69%                             | Field efficiency; target >67.5%. |

### Variant 1 – All shift hours (with input)

Shift and break from **schedule** (all shifts). Use as reference for “total shift” and cost when including empty shifts.

| Metric                              | Value                                 | Notes                                                               |
| ----------------------------------- | ------------------------------------- | ------------------------------------------------------------------- |
| **Total shift**                     | 3 827 h 0 min                         | Sum of (shift end − shift start) for _all_ 456 shifts (from input). |
| **Break**                           | 110 h 15 min                          | From solution (breaks in itinerary).                                |
| **Idle**                            | 2 565 h 34 min                        | Shift − (visit+travel+wait+break).                                  |
| **Efficiency (visit / assignable)** | 29.12%                                |                                                                     |
| **Cost / Revenue / Margin**         | 880 210 kr / 595 238 kr / −284 972 kr |                                                                     |

### Variant 3 – Field time (output only, no input)

When the script runs **without** `--input`, it infers shift only from the **output** itinerary (no schedule). It sums time that has **any** itinerary activity: **visits** and/or **breaks**. So it includes shifts with visits, and **shifts with breaks but no visits** (e.g. shift `5815ff36` in the bug dataset: itinerary has one BREAK 11:00–11:45; the API often returns `totalBreakDuration: "PT0S"` for such shifts). The script uses itinerary break when the metrics block reports zero, so break-only shifts contribute their break time to total shift and total break. Effectively **field time** (no empty shifts, no tail idle). Use as reference for “shift when only counting used time”.

| Metric                              | Value                                         | Notes                                                                                                        |
| ----------------------------------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **Total shift**                     | 1 412 h 11 min                                | Sum of activity from output (visit+travel+wait+break). Includes shifts with only breaks (e.g. 5815ff36).     |
| **Break**                           | 261 h 0 min                                   | From solution itinerary; script uses itinerary when API reports totalBreakDuration PT0S (break-only shifts). |
| **Idle**                            | 0 h 0 min                                     | Not in output itinerary; empty shifts and tail idle not counted.                                             |
| **Efficiency (visit / assignable)** | 94.01%                                        |                                                                                                              |
| **Cost / Revenue / Margin**         | 324 801 kr / 595 238 kr / 270 437 kr (45.44%) |                                                                                                              |

**Cost/revenue constants in script:** 230 kr/h (cost), 550 kr/h (visit revenue).

The script supports `--exclude-empty-shifts-only` and `--visit-span-only` for variants 2 and 3; see docstring and `--help`.

---

## 6. Bug dataset (plan 4a47b69a) — files attached

**Timefold:** Plan ID `4a47b69a-08c4-4f72-a9da-66d98a245b56`; API key (stage) `tf_p_411fa75d-ffeb-40ec-b491-9d925bd1d1f3`.

The **be-agent-service** repo is private. The following files are **attached** with this report so recipients can reproduce the metrics without repo access:

| Role               | File (attached)                                             | Description                                      |
| ------------------ | ----------------------------------------------------------- | ------------------------------------------------ |
| **Input**          | `export-field-service-routing-v1-4a47b69a-...-input.json`   | Timefold FSR input (schedule, visits, vehicles). |
| **Output**         | `export-field-service-routing-4a47b69a-...-output (2).json` | Timefold FSR solution (itineraries, metrics).    |
| **Metrics script** | `metrics.py`                                                | Python script to compute reference metrics.      |

**Run metrics (output only – shift from solution itinerary, no idle):**

```bash
python3 metrics.py "export-field-service-routing-4a47b69a-08c4-4f72-a9da-66d98a245b56-output (2).json"
```

**Run metrics (with input – shift from schedule, includes idle):**

```bash
python3 metrics.py "export-field-service-routing-4a47b69a-08c4-4f72-a9da-66d98a245b56-output (2).json" \
  --input "export-field-service-routing-v1-4a47b69a-08c4-4f72-a9da-66d98a245b56-input.json"
```

(Use the actual attached filenames; run from the folder where you saved the attachments.)

- **Without input:** Total shift = 1 412 h 11 min (shifts with any itinerary activity: visits and/or breaks; idle = 0). Efficiency 94.01%.
- **With input:** Total shift = 3 827 h 0 min (all scheduled shift lengths); idle = 2 565 h 34 min. Efficiency 29.12%.

---

## 7. Suggested approach

We **always** run metrics for every solution — original solve and any from-patch revision. The only difference is which metrics flags to use so totals are correct.

### Step 1: Full solve

Run a normal solve. You get **original output** (e.g. 448 shifts, 136 empty) and **input**.

### Step 2: Metrics for original solution (3 variants)

Run metrics on the **original** output. The three variants differ because there are empty shifts and idle:

| Variant               | Command                                                                              |
| --------------------- | ------------------------------------------------------------------------------------ |
| **A – All shifts**    | `metrics.py <original_output.json> --input <input.json>`                             |
| **B – Active shifts** | `metrics.py <original_output.json> --input <input.json> --exclude-empty-shifts-only` |
| **C – Field time**    | `metrics.py <original_output.json> --visit-span-only` (or omit `--input`)            |

Store and display these totals.

### Step 3: From-patch (remove idle), then metrics for the revision

Run from-patch: **pin visits + remove empty shifts/vehicles only** (do **not** trim shift windows to visit span; use `--no-trim-shifts` in build_from_patch). Fetch the **from-patch output**. That output has correct shift times (startTime, totalWaitingTime); use it as the solution for Bryntum (no empty shifts in the data).

**Always run metrics for this revision.** Use the **same** metrics commands as for the original (with the from-patch **input** for variant A/B). The three variants may coincide (all shifts = active shifts). You may see **more assigned visits** if the re-solve placed some previously unassigned.

```bash
# Same as original: A, B, C (no special flags needed when patch did not trim shift times)
metrics.py <from_patch_output.json> --input <from_patch_input.json>
metrics.py <from_patch_output.json> --input <from_patch_input.json> --exclude-empty-shifts-only
metrics.py <from_patch_output.json> --visit-span-only
```

_If_ a from-patch was run **with** trim-to-visit-span, that API response can have wrong shift/wait; then use `--visit-span-only --exclude-inactive` for that output.

### Step 4: Workflow summary

| Step | Action                                                                                                                                     |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 1    | **Solve** → original output (e.g. 46 vehicles, 448 shifts) + input.                                                                        |
| 2    | **Metrics (original)** → A, B, C on original output + input. Store all three.                                                              |
| 3    | **Build patch** → pin visits, remove empty shifts/vehicles, **no** trim (`build_from_patch.py --no-trim-shifts --no-end-shifts-at-depot`). |
| 4    | **From-patch** → submit patch, wait, fetch new output (e.g. 42 vehicles, 312 shifts). New input = patched model.                           |
| 5    | **Metrics (revision)** → A, B, C on from-patch output + from-patch input (same commands as step 2).                                        |
| 6    | **Schedule (Bryntum)** → use from-patch output (only active shifts; no empty rows).                                                        |

**Data check:** Original = 46 vehicles, 448 shifts. From-patch = 42 vehicles, 312 shifts (136 empty removed). Always run metrics for both.

### Exact commands (be-agent-service)

Scripts live in `be-agent-service/recurring-visits/scripts/`. All support this workflow:

| Step | Script                  | Command                                                                                                                                                                                                   |
| ---- | ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2    | `metrics.py`            | `metrics.py <output.json> --input <input.json>` (A). Same + `--exclude-empty-shifts-only` (B). Same + `--visit-span-only` or no `--input` (C).                                                            |
| 3    | `build_from_patch.py`   | `build_from_patch.py --output <original_output.json> --input <original_input.json> --no-trim-shifts --no-end-shifts-at-depot --out payload.json [--no-timestamp]`                                         |
| 4    | `submit_to_timefold.py` | `submit_to_timefold.py from-patch payload.json --route-plan-id <original_plan_id> [--wait] [--save <path>]`. Then fetch: `fetch_timefold_solution.py <new_plan_id> --save <path>` (saves output + input). |
| 5    | `metrics.py`            | Same as step 2, with from-patch output and from-patch input.                                                                                                                                              |

So the workflow is implemented; run the steps in order (no single end-to-end script).
