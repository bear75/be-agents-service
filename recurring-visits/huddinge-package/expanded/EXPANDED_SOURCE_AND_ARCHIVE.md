# Expanded CSV: source for 28-feb solves and archive

## Where visits vs vehicles/shifts come from

- **Expanded CSV** (e.g. `huddinge_2wk_expanded_20260224_043456.csv`) contains **only visits**: one row per concrete visit in the planning window (date, client, time window, etc.). It has **no shift data**.
- **Vehicles and shifts** are **not** in the expanded CSV. They are generated in `scripts/generate_employees.py` from the **source CSV** (`source/Huddinge_recurring_v2.csv`):
  - One vehicle per unique `external_slinga_shiftName` (employee).
  - For each vehicle, one shift per (working weekday × date in 2-week window × shift type day/evening).
  - So with no trimming you get the **full** set (e.g. 38 vehicles × ~32 shifts each ≈ **1208 shifts**).
- The **412-shift** input (e.g. 5ff7929f export) was built with **trimmed output**: only shifts that appeared in a previous solution are created. Use `--base-input` in `process_huddinge.py` to reuse that vehicle/shift set so continuity runs are comparable.

## Source for `solve/28-feb/5ff7929f/input.json`

The FSR input for dataset **5ff7929f** (and the 28-feb prod runs) was built from the same 2-week Huddinge pipeline as the staging origin `c87d58dd` / `fa713a0d`. The **canonical expanded CSV** for that dataset is:

- **`huddinge_2wk_expanded_20260224_043456.csv`**
  - 3622 visit rows (+ header) → matches input’s 3622 Timefold visits / 3478 care visits
  - Referenced in docs (CONTINUITY_STRATEGIES, build_expanded_2w_trimmed, patch_visits_slinga_direct) as the 2-week expanded source
  - Pipeline: this CSV → `csv_to_timefold_fsr` (+ generate_employees) → FSR input → submit → 5ff7929f (prod first solve from 25feb-stagetf-corect origin)

**`huddinge_2wk_expanded_trimmed_2w.csv`** is a 2-week variant (e.g. from `build_expanded_2w_trimmed` or similar). Keep as current asset for continuity/compare or later runs; it is derived from the same dataset as the 20260224_043456 expansion.

## Safe to archive (old timestamped runs)

| File | Reason |
|------|--------|
| `huddinge_2wk_expanded_20260223_054544.csv` | Feb 23 05:45 – superseded by 20260224_043456 |
| `huddinge_2wk_expanded_20260223_095835.csv` | Feb 23 09:58 – superseded by 20260224_043456 |
| `huddinge_2wk_expanded_20260223_143133.csv` | Feb 23 14:31 – superseded by 20260224_043456 |
| `huddinge_4wk_expanded_20260223_143138.csv` | 4-week expansion; archive if 4-week runs not used |
| `huddinge_4wk_expanded_20260223_183726.csv` | 4-week expansion; archive if 4-week runs not used |

README: *"Only timestamped files from the current pipeline run are valid for downstream steps. Remove or archive old timestamped files when regenerating."*

## Keep (current)

- **`huddinge_2wk_expanded_20260224_043456.csv`** – source for 5ff7929f / 28-feb input
- **`huddinge_2wk_expanded_trimmed_2w.csv`** – current 2-week trimmed variant
