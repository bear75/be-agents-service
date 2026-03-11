# Scripts for 4mars CSV (Attendo databehov)

These scripts are for the **new** Attendo 4mars CSV format and the FSR pipeline that uses it. All inputs, outputs, and reports for 4mars live in the parent folder (`huddinge-4mars-csv/`).

**All scripts take paths as arguments** — the same scripts work for the short test CSV and the long 81-client CSV. Use a **2-week** planning window (`--start-date` / `--end-date`) during testing to save solve time; use 4w for production.

| Script | Purpose |
|--------|--------|
| **attendo_4mars_to_fsr.py** | Convert 4mars CSV → Timefold FSR input JSON (expand recurrence, geocode, time windows, visit groups, vehicles). Use `--no-supplementary-vehicles` to match reference (26 vehicles for 2w). |
| **build_address_coordinates.py** | Build `address_coordinates.json` from CSV (Gata + Postnummer + Ort). Run before FSR input if geocoding; no fallback — fix CSV if any address fails. |
| **rewrite_visit_ids_in_input.py** | Rewrite visit `id` and `name` in an existing input JSON to the new scheme (`Hxxx_r{row}_{occ}`, `Hxxx Besök {occ}`). Use when you have a working reference and want the same structure with new names without re-geocoding. |
| **compare_input_structure.py** | Compare two input JSONs structurally (ignoring id/name). Verifies "same input except names". |
| **analyze_4mars_csv_to_json.py** | Verify CSV→JSON: row expansion, visit IDs, TF format; optional report to `../reports/`. |
| **map_visits_time_windows.py** | Report time windows, visit groups, dependencies; optional report to `../reports/`. |
| **analyze_dependency_feasibility.py** | Check visitDependencies (precedingVisit + minDelay) vs time windows; reports infeasible/tight/OK. Use `--all` for full dataset. |
| **verify_all_visits_have_flex.py** | Ensure every visit has flex (time or day). Pass FSR input JSON path. |

Run from repo root or from `huddinge-4mars-csv/`:

```bash
# From recurring-visits/
python huddinge-package/huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py \
  huddinge-package/huddinge-4mars-csv/ATTENDO_DATABEHOV_PER_KUND_OCH_BESOK\ -\ data.csv \
  -o huddinge-package/huddinge-4mars-csv/export-field-service-routing-v1-4mars-input.json
```

**Long CSV (81 clients, 2w for testing)** — same scripts, different paths; use 2w to save solve time:

```bash
# 1) Geocode (once; no fallback — fix Gata in CSV if any fail)
python huddinge-package/huddinge-4mars-csv/scripts/build_address_coordinates.py \
  huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/huddinge-81-clients\ -\ Data.csv \
  -o huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/address_coordinates.json

# 2) FSR input (2-week window)
python huddinge-package/huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py \
  huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/huddinge-81-clients\ -\ Data.csv \
  -o huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/input_81_10mars_2w.json \
  --start-date 2026-03-09 --end-date 2026-03-22 \
  --address-coordinates huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/address_coordinates.json

# 3) Analysis (optional)
python huddinge-package/huddinge-4mars-csv/scripts/analyze_4mars_csv_to_json.py \
  huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/huddinge-81-clients\ -\ Data.csv \
  huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/input_81_10mars_2w.json \
  -o huddinge-package/huddinge-4mars-csv/reports/analyze_csv_to_json_81_2w.txt

python huddinge-package/huddinge-4mars-csv/scripts/map_visits_time_windows.py \
  huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/input_81_10mars_2w.json \
  huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/huddinge-81-clients\ -\ Data.csv \
  -o huddinge-package/huddinge-4mars-csv/reports/map_visits_time_windows_81_2w.txt

python huddinge-package/huddinge-4mars-csv/scripts/analyze_dependency_feasibility.py \
  huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/input_81_10mars_2w.json --all \
  -o huddinge-package/huddinge-4mars-csv/reports/dependency_feasibility_81_2w.json

python huddinge-package/huddinge-4mars-csv/scripts/verify_all_visits_have_flex.py \
  huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/input_81_10mars_2w.json

# 4) Compare two inputs (e.g. short vs long or before/after rewrite)
python huddinge-package/huddinge-4mars-csv/scripts/compare_input_structure.py \
  path/to/reference_input.json path/to/candidate_input.json
```

Submit, validate, and solve use the **shared** scripts in `recurring-visits/scripts/`: `submit_to_timefold.py`, `fetch_timefold_solution.py`, etc.

**Same input with new visit names (no geocoding)**  
If you already have a working input (e.g. `solve_2v_output/input.json`) and only want new id/name:

```bash
python huddinge-package/huddinge-4mars-csv/scripts/rewrite_visit_ids_in_input.py \
  huddinge-package/huddinge-4mars-csv/solve_2v_output/input.json \
  -o huddinge-package/huddinge-4mars-csv/input/input_4mars_2w_newids.json

python huddinge-package/huddinge-4mars-csv/scripts/compare_input_structure.py \
  huddinge-package/huddinge-4mars-csv/solve_2v_output/input.json \
  huddinge-package/huddinge-4mars-csv/input/input_4mars_2w_newids.json
```
