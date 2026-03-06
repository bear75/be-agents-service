# Caire (CSV upload) vs pipeline script input – analysis

**Date:** 2026-03-04  
**Source CSV:** `expanded/huddinge_2wk_expanded_20260224_043456.csv` (3,622 data rows + header)  
**Caire input:** `huddinge-cairepilot app 4 mars/export-field-service-routing-v1-44098d5f-...-input.json`  
**Pipeline input:** `huddinge-cairepilot app 4 mars/scripts/export-field-service-routing-v1-5ff7929f-...-input.json`  
**Pipeline script:** `process_huddinge.py` → `scripts/csv_to_timefold_fsr.py` (+ `generate_employees.py` for vehicles)

**Source of truth:** The expanded CSV contains all fields both sides use: `visitGroup_id`, `minStartTime`, `maxStartTime`, `maxEndTime`, `duration`, `Prio (1-3)`, `original_visit_id`, etc. Caire and the pipeline both read from this same CSV; differences come from how each converts it to FSR JSON.

---

## Summary

**Same:** Both consume the same expanded CSV and produce valid Timefold FSR `modelInput` with the same **total visit count** (3,622) and equivalent **visit data** (location, duration, time windows). So “input from Caire (extended CSV upload)” and “our script pipeline” are **conceptually the same** for visits.

**Different:**  

- **Visit IDs:** Caire uses UUIDs; pipeline uses `original_visit_id` from CSV (numeric string).  
- **Time format:** Caire uses UTC (`…Z`); pipeline keeps CSV’s `+01:00`. Same instants.  
- **Visit names:** Caire uses short form (e.g. `H015 - H015 1`); pipeline uses `{client} - {inset_type}` (e.g. `H015_1 - Tillsyn`).  
- **Visit grouping:** Neither is correct; target is 145 same-day groups with 290 visits (see [Visit groups](#visit-groups) and [Bugs in Caire](#bugs-in-caire)).  
- **Priority:** Caire **hardcodes** `"5"` for every visit (bug); should be optional or from CSV `Prio (1-3)`; Timefold default is 6 if omitted.  
- **maxStartTime:** Caire **wrong for every visit** (bug): uses fixed 15-minute window instead of CSV `maxStartTime` (or maxEnd − duration).  
- **planningWindow:** Only Caire adds `modelInput.planningWindow`.  
- **Vehicles/shifts:** Different source and count (Caire 39/624; pipeline 42/412 in this sample).

---

## 1. Source and counts


| Item              | CSV   | Caire (44098d5f) | Pipeline (5ff7929f) |
| ----------------- | ----- | ---------------- | ------------------- |
| Data rows         | 3,622 | —                | —                   |
| Total visits      | 3,622 | 3,622            | 3,622               |
| Standalone visits | —     | 3,332            | 3,334               |
| Visit groups      | —     | 73               | 144                 |
| Visits in groups  | —     | 290              | 288                 |
| Vehicles          | —     | 39               | 42                  |
| Shifts            | —     | 624              | 412                 |


- Same CSV → same total visits in both inputs.  
- Slight difference in standalone vs group split (2 visits) due to different grouping logic.  
- Vehicle/shift counts differ because Caire builds vehicles from its own logic (or config) while this pipeline run likely used `--base-input` or a trimmed output (fewer shifts).

---

## 2. Visit structure (same logical visit: CSV row 1, original_visit_id=1)

**CSV (row 2):**  
`minStartTime=2026-02-16T07:05:00+01:00`, `maxStartTime=2026-02-16T09:35:00+01:00`, `maxEndTime=2026-02-16T09:41:00+01:00`, duration 6, client H015_1, inset Tillsyn.

**Caire:**  

- `id`: UUID (`626b4afb-7d6e-4c54-934b-e7738003dcb7`)  
- `name`: `"H015 - H015 1"`  
- `timeWindows`: UTC — `minStartTime`: `2026-02-16T06:05:00.000Z`, `maxStartTime`: `2026-02-16T08:26:00.000Z`, `maxEndTime`: `2026-02-16T08:41:00.000Z`  
- `serviceDuration`: `PT6M`  
- `priority`: `"5"`

**Pipeline:**  

- `id`: `"1"` (= `original_visit_id`)  
- `name`: `"H015_1 - Tillsyn"`  
- `timeWindows`: `+01:00` — same as CSV (07:05, 09:35, 09:41)  
- `serviceDuration`: `PT6M`  
- No `priority` in script (default 6 in output)

So for this visit:

- **Pipeline** matches CSV exactly (times, duration, id from CSV).  
- **Caire** matches minStartTime and maxEndTime (same instant, UTC); **maxStartTime** in Caire is 08:26Z (09:26 CET) vs CSV 09:35 CET — 9 minutes earlier. This is **not** a one-row bug: Caire uses a **fixed 15-minute** window (maxStartTime = maxEndTime − 15 min) for **every** visit, instead of the CSV `maxStartTime` or (maxEnd − visit duration). So all 3,622 visits get a wrong, tighter latest-start time.

---

## 3. Differences in detail


| Aspect             | Caire                                                    | Pipeline (`csv_to_timefold_fsr.py`)                                                                         |
| ------------------ | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Visit ID**       | UUID per visit                                           | `original_visit_id` from CSV                                                                                |
| **Visit name**     | Short: `{client} - {client} {n}` style                   | `{recurringVisit_clientName} - {inset_type}` (truncated)                                                    |
| **Time zone**      | UTC (`…Z`)                                               | Preserves CSV (`+01:00`)                                                                                    |
| **Priority**       | **Bug:** Hardcoded `"5"` for all 3,622 visits (optional in TF; default 6; CSV has `Prio (1-3)`) | Not set → Timefold default 6                                                                                |
| **planningWindow** | Present in `modelInput`                                  | Not added                                                                                                   |
| **Visit groups**   | **Bug:** One FSR group per `visitGroup_id` (73 groups) → mixes visits from different days; id `visitGroup_1` | Groups by `(visitGroup_id, week, date)` → 144 groups; id like `visitGroup_2_w0`; close to target 145        |
| **Group fields**   | No `alignment` / `serviceDurationStrategy` in sample     | Output file has `alignment`, `serviceDurationStrategy` (may be from older script or API)                    |
| **Vehicles**       | From Caire app/config (39 vehicles, 624 shifts)         | From source CSV + `generate_employees.py`; optional `--base-input` / trimmed (42 vehicles, 412 shifts here) |
| **Run name**       | `"Optimization - huddinge_2wk_expanded_20260224_043456"` | `"Huddinge 2-Week Schedule"` (or from `--name`)                                                             |

---

## Visit groups (intended semantics)

Double-staff (multi-vehicle) visits: each **same-day** pair (or 2, 4, 6… visits at the same time) should be **one** FSR visitGroup. With 290 visits that belong to groups in the CSV, the correct split is:

- **145 visit groups** (290 ÷ 2), each with 2 visits on the same day (or 2, 4, 6 etc. per group depending on the “double 6” pattern).
- **290 visits** in those groups.

So:

- **Caire:** 73 groups, 290 visits — **wrong**. One FSR group per distinct `visitGroup_id`, so visits from different days are in the same group (e.g. visitGroup_2 has 4 visits: 2 on 2026-02-16 and 2 on 2026-02-23). Timefold requires same-day overlapping windows for multi-vehicle groups.
- **Pipeline:** 144 groups, 288 visits — **close** (144 ≈ 145; 2 visits end up standalone due to grouping key), but not exactly 145 same-day groups.

---

## Bugs in Caire (for bug report)

1. **maxStartTime wrong for every visit**  
   Caire sets `maxStartTime = maxEndTime − 15 minutes` for **all** visits instead of using the CSV `maxStartTime` (or `maxEndTime − serviceDuration`). So the latest allowed start is 9 minutes too early for a 6‑minute visit, and wrong for every other duration. **Fix:** Use CSV column `maxStartTime` (or derive as maxEnd − duration); do not use a fixed 15‑minute offset.

2. **Priority hardcoded to "5"**  
   All 3,622 visits get `"priority": "5"`. Priority is optional in Timefold (default 6 if omitted). CSV has `Prio (1-3)`. **Fix:** Do not hardcode; either omit (TF default 6) or map from CSV `Prio (1-3)` if present.

3. **Visit groups span multiple days**  
   Caire builds one FSR `visitGroup` per distinct `visitGroup_id`, so each group contains visits from **multiple days** (e.g. week 0 and week 1). Timefold multi-vehicle groups must be **same-day** (overlapping time windows on one day). **Fix:** Build one FSR visitGroup per same-day set of visits that share a `visitGroup_id` (e.g. per `(visitGroup_id, date)`). Target: 145 groups, 290 visits.

4. **(Optional) planningWindow**  
   Only Caire adds `modelInput.planningWindow`; pipeline does not. Not a bug per se, but if Caire and pipeline should produce equivalent input, either both add it or neither.

5. **(Optional) Visit ID / name**  
   Caire uses UUIDs and a short name; pipeline uses `original_visit_id` and `{client} - {inset_type}` from CSV. For traceability and comparison, using CSV identifiers and names is preferable.

---

## 4. Pipeline script flow (for reference)

1. **process_huddinge.py**
  - Optionally expands recurring CSV; then calls `generate_timefold_json(expanded_csv, ...)`.
2. **csv_to_timefold_fsr.py**
  - Reads expanded CSV.  
  - Fills missing coordinates (geocode) if needed.  
  - Builds one visit per row from: `original_visit_id`, `client_lat/lon`, `minStartTime`, `maxStartTime`, `maxEndTime`, `duration`, `recurringVisit_clientName`, `inset_type`.  
  - Builds **visit groups** by `(visitGroup_id, week, date)`; visits in ≥2 per (same day) go into a group.  
  - **Vehicles:** from `generate_vehicles(source_csv, ...)` (source CSV under `source/`); optionally restricted by `--base-input` or trimmed output.  
  - Writes `config.run.name` + `modelInput`: `vehicles`, `visits`, `visitGroups` (no `planningWindow`).

So the pipeline does **not** add `planningWindow`; Caire does. Solver behavior differs because of the Caire bugs above (maxStartTime, priority, visit groups).

---

## 5. Conclusion

- **Is the input from Caire (extended CSV upload) the same as our script pipeline?**  
Same CSV and total visits; **semantic differences** come from **Caire bugs**: wrong maxStartTime (all visits), hardcoded priority, and wrong visit-group structure (groups spanning multiple days). See [Bugs in Caire](#bugs-in-caire). **Correct visit-group target:** 145 same-day groups, 290 visits; neither Caire (73) nor pipeline (144) is exactly right.  
- **Bugs to fix in Caire:** maxStartTime (use CSV or maxEnd − duration), priority (omit or from CSV `Prio (1-3)`), visit groups (same-day only; target 145 groups, 290 visits). Optional: planningWindow consistency, use CSV IDs/names.  

