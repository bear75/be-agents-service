# Timefold FSR pipeline: where things live

**Purpose**: Clarify which paths are canonical for the Huddinge CSV → FSR JSON → Timefold solve pipeline, and how script consolidation relates to `recurring-visits/`.

**Last updated**: 2026-03-14

---

## 1. Which scripts to use

| Role | Canonical location | Notes |
|------|--------------------|--------|
| **CSV → FSR JSON** | `scripts/timefold/conversion/csv_to_fsr.py` | Single consolidated converter. Run from repo root. |
| **Submit solve** | `scripts/timefold/submission/submit_solve.py` | Submit input JSON to Timefold API, optional --wait and --save. |
| **Fetch solution** | `scripts/timefold/submission/fetch_solution.py` | Fetch completed solution by route plan ID. |
| **Continuity (pools, from-patch)** | `scripts/timefold/continuity/` and `scripts/timefold/analysis/` | build_pools, build_from_patch, continuity_report, metrics. |

**`scripts/timefold-optimization/`** (separate from main pipeline):

- `build_tunable_continuity_dataset.py`, `build_slinga_geo_dataset.py`, `build_c_vehicle_constraint_dataset.py` — dataset builders for tuning/experiments. Not part of the standard CSV → FSR → solve flow.

---

## 2. Data_fixed.csv vs Data_final.csv (v3)

| File | Columns | Use |
|------|---------|-----|
| **Huddinge-v3 - Data_fixed.csv** | Same as final but **no Lat,Lon**. 20 columns, 664 data rows. | Pre-geocoding version; use if you run with geocoding. |
| **Huddinge-v3 - Data_final.csv** | **Has Lat,Lon** (22 columns). 664 data rows. | Use for v3 pipeline with `--no-geocode` (canonical for current runs). |

So **Data_final** = Data_fixed + geocoded Lat/Lon (and possibly minor cleanup). For `scripts/timefold/conversion/csv_to_fsr.py` with `--no-geocode`, use **Data_final.csv**.

---

## 3. Where the v3 data lives

| Data | Path | Use |
|------|------|-----|
| **Active v3 dataset** | `recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/` | Current campaign: CSV, input_v3_FIXED.json, continuity variants, output_FIXED, docs (SUMMARY.md, VERIFICATION_RESULTS.md). **Use this for v3 runs.** |
| **Reference “no extra vehicles”** | `recurring-visits/huddinge-package/.../10-mars-new-attendo/script_fsr_no_extra_vehicles.json` | Example FSR input with 2-week window and Slinga-only vehicles (no supplementary). |
| **Older / continuity test data** | `recurring-visits/data/huddinge-v3/` | Docs (HUDDINGE_V3_README.md), continuity pipelines (e.g. pipeline_da2de902, test_tenant), older exports. Not the primary v3 campaign path. |

For the v3 baseline (2 weeks, ~26 vehicles, ~3832 visits), use the **v3** folder under `full-csv/10-mars-new-attendo/v3/`, not `data/huddinge-v3`.

---

## 4. Consolidation: which recurring-visits scripts are in `scripts/timefold`?

| Script / path | Consolidated to `scripts/timefold/`? | Notes |
|---------------|--------------------------------------|--------|
| **huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py** | **Yes** | Canonical version: `scripts/timefold/conversion/csv_to_fsr.py`. Use the timefold one. |
| **v3/run_continuity_optimization.sh** | No | Shell orchestrator for continuity; calls Python. No 1:1 copy in timefold; timefold has `continuity/build_pools.py`, `build_from_patch.py` to run directly. |
| **v3/verify_csv_to_json.py** | No | Verifies CSV→JSON output (deps, time windows). Lives only in v3 folder. |
| **v3/launch_campaign.sh** | No | Launches submit/solve for v3 variants. No copy in scripts/timefold. |
| **10-mars-new-attendo/cleanup_addresses_in_csv.py** | No | CSV address cleanup. Not in timefold. |
| **10-mars-new-attendo/compare_fsr_inputs.py** | No | Compares two FSR JSON inputs. Not in timefold. |
| **10-mars-new-attendo/compare_fsr_v2.py** | No | Compares FSR v2 vs other. Not in timefold. |
| **huddinge-package/scripts/** (merge-metrics, etc.) | No | Package-level scripts; not under timefold. |
| **huddinge-4mars-csv/scripts/** (build_address_coordinates, analyze_*, compare_*, etc.) | No | Helpers (geocode, analyze, compare). Not consolidated into timefold. |

So only the **CSV → FSR converter** is consolidated: use `scripts/timefold/conversion/csv_to_fsr.py` instead of `attendo_4mars_to_fsr.py`. All other listed scripts remain only in `recurring-visits/` and are **not** moved to `scripts/timefold/`.

---

## 5. Is `recurring-visits/` consolidated?

**Yes and no:**

- **Scripts**: The **canonical** conversion and submission scripts are in **`scripts/timefold/`** (repo root). The guide calls these “consolidated.”
- **Backward compatibility**: Some older or duplicate scripts remain under `recurring-visits/scripts/` (e.g. `submit_to_timefold.py`) and under `recurring-visits/huddinge-package/.../scripts/` (e.g. `attendo_4mars_to_fsr.py`). Prefer `scripts/timefold/` for new runs.
- **Data**: `recurring-visits/` is still the place for **data**: Huddinge package (CSV, v2/v3 inputs/outputs), Nova, and `data/huddinge-v3` (continuity/test). So **recurring-visits is used** for all data and for backward-compat scripts; **scripts/timefold** is used for the main pipeline.

**Summary**: Use **`scripts/timefold/`** for conversion and solve; use **`recurring-visits/huddinge-package/.../v3/`** for v3 CSV and outputs.

---

## 6. v3 baseline: 2 weeks and vehicle count

The CSV contains some “Var 4:e vecka” (4-weekly) recurrence. The converter’s default is to set the planning end from the **longest recurrence** in the CSV, so without options you get a **4-week** window and extra visits.

To get the **v3 baseline** (2 weeks, Slinga-only vehicles, matching `script_fsr_no_extra_vehicles.json` and SUMMARY.md):

```bash
cd /path/to/be-agent-service

python3 scripts/timefold/conversion/csv_to_fsr.py \
  "recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/Huddinge-v3 - Data_final.csv" \
  -o "recurring-visits/.../v3/input_v3_FIXED.json" \
  --start-date 2026-03-02 \
  --weeks 2 \
  --no-supplementary-vehicles \
  --no-geocode
```

- **`--weeks 2`**: Caps the planning window to 2 weeks even when the CSV has 4-weekly recurrence (planning end = start + 14 days).
- **`--no-supplementary-vehicles`**: Only vehicles from the CSV (Slinga); no extra Kväll/Dag vehicles (~26 for 2w baseline).
- **`--no-geocode`**: Use when CSV already has Lat/Lon.

Without `--weeks 2` you get 4 weeks; without `--no-supplementary-vehicles` you get many more vehicles (and shifts).

---

## 7. Pipeline flow (canonical)

1. **CSV → FSR JSON**  
   `scripts/timefold/conversion/csv_to_fsr.py`  
   Input: CSV in `recurring-visits/.../v3/`.  
   Output: FSR JSON (e.g. in same v3 folder).

2. **Optional: validate**  
   `scripts/timefold/submission/submit_solve.py validate <input.json>`

3. **Submit solve**  
   `scripts/timefold/submission/submit_solve.py solve <input.json> --wait --save <output_dir>`

4. **Continuity** (if needed): build pools from baseline solution, patch `requiredVehicles`, then submit again using scripts under `scripts/timefold/continuity/` and `scripts/timefold/analysis/`.

All paths in this doc are relative to **be-agent-service** repo root unless otherwise noted.
