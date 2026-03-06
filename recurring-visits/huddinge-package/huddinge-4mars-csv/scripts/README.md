# Scripts for 4mars CSV (Attendo databehov)

These scripts are for the **new** Attendo 4mars CSV format and the FSR pipeline that uses it. All inputs, outputs, and reports for 4mars live in the parent folder (`huddinge-4mars-csv/`).

| Script | Purpose |
|--------|--------|
| **attendo_4mars_to_fsr.py** | Convert 4mars CSV → Timefold FSR input JSON (expand recurrence, geocode, time windows, visit groups, vehicles). Use `--no-supplementary-vehicles` to match reference (26 vehicles for 2w). |
| **rewrite_visit_ids_in_input.py** | Rewrite visit `id` and `name` in an existing input JSON to the new scheme (`Hxxx_r{row}_{occ}`, `Hxxx Besök {occ}`). Use when you have a working reference and want the same structure with new names without re-geocoding. |
| **compare_input_structure.py** | Compare two input JSONs structurally (ignoring id/name). Verifies "same input except names". |
| **analyze_4mars_csv_to_json.py** | Verify CSV→JSON: row expansion, visit IDs, TF format; optional report to `../reports/`. |
| **map_visits_time_windows.py** | Report time windows, visit groups, dependencies; optional report to `../reports/`. |

Run from repo root or from `huddinge-4mars-csv/`:

```bash
# From recurring-visits/
python huddinge-package/huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py \
  huddinge-package/huddinge-4mars-csv/ATTENDO_DATABEHOV_PER_KUND_OCH_BESOK\ -\ data.csv \
  -o huddinge-package/huddinge-4mars-csv/export-field-service-routing-v1-4mars-input.json
```

Submit, fetch, and metrics use the **shared** scripts in `recurring-visits/scripts/`: `submit_to_timefold.py`, `fetch_timefold_solution.py`, etc.

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
