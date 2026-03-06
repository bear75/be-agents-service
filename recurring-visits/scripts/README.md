# Recurring-visits scripts

## 4mars CSV (new Attendo format)

Scripts for the **4mars** CSV and FSR pipeline live in:

**`huddinge-package/huddinge-4mars-csv/scripts/`**

- `attendo_4mars_to_fsr.py` – CSV → FSR input JSON  
- `analyze_4mars_csv_to_json.py` – CSV↔JSON analysis  
- `map_visits_time_windows.py` – Time windows / groups / dependencies report  

All 4mars data (CSV, input/output JSONs, reports, metrics) is under `huddinge-package/huddinge-4mars-csv/`.

---

## Scripts in this folder (legacy / shared)

Used for **old** CSV formats, continuity runs, from-patch, metrics, and generic FSR:

| Script | Use |
|--------|-----|
| **submit_to_timefold.py** | Submit solve / from-patch, validate, wait, save output (shared by 4mars and legacy). |
| **fetch_timefold_solution.py** | Fetch solution by route plan ID, optional metrics/continuity. |
| **expand_recurring_visits.py** | Expand recurring visits CSV (legacy format). |
| **csv_to_timefold_fsr.py** | Legacy CSV → FSR input. |
| **build_continuity_pools.py** | Continuity pools from first-run output. |
| **continuity_report.py** | Continuity report from input + output. |
| **metrics.py**, **solve_report.py**, **fsr_metrics.py** | Metrics and reports. |
| **analyze_empty_shifts.py**, **analyze_unassigned.py**, **analyze_*.*** | Analysis on output. |
| **build_from_patch.py** | Build from-patch payload from output (pin visits, trim shifts, remove empty shifts/vehicles). |
| **build_trimmed_input.py** | Build trimmed input from output: remove empty shifts and unused vehicles for a parallel fresh solve. |
| **build_*.py**, **run_*.py**, **patch_*.py**, etc. | Other build/run/patch helpers for legacy pipeline. |

For 4mars, run the scripts in `huddinge-package/huddinge-4mars-csv/scripts/` and use `submit_to_timefold.py` / `fetch_timefold_solution.py` from here with paths into `huddinge-4mars-csv/`.
