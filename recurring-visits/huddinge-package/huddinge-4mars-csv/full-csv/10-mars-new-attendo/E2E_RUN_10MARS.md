# E2E pipeline run – 10-mars 81-clients (2026-03-10)

Pipeline: **huddinge-81-clients - Data.csv** + **Lathund** (reference) → input → validate → solve.

## CSV format

- **Data CSV:** `huddinge-81-clients - Data.csv` (Skift, extra columns Column-9/10, När på dagen: Morgon, Förmiddag, Lunch, Eftermiddag, Middag, Kväll, Lördag).
- **Lathund:** `huddinge-81-clients - Lathund.csv` (slot/shift reference only; not read by the pipeline).
- Differences vs small test CSV: see `CSV_DIFF_ANALYSIS.md`.

## Script updates

- **attendo_4mars_to_fsr.py:** Accepts both `Schift` and `Skift`; added slots for Förmiddag, Eftermiddag, Middag, Lördag (→ Morgon).
- **Fallback:** `Gran Backen 19, 14131 Huddinge` added to `_FALLBACK_COORDINATES` (Nominatim miss).

## Steps run

1. **Geocode addresses**  
   `build_address_coordinates.py "huddinge-81-clients - Data.csv" -o address_coordinates.json`  
   → 95 unique addresses in `address_coordinates.json` (plus built-in fallback for Gran Backen 19).

2. **Add coordinates to CSV (pre-step for seed/upload)**  
   So the dashboard seed and CSV upload get Lat/Lon, run from `full-csv/`:
   ```bash
   cd full-csv
   python3 add_coordinates_to_csv.py "10-mars-new-attendo/huddinge-81-clients - Data.csv" \
     --coordinates "10-mars-new-attendo/address_coordinates.json" \
     -o "10-mars-new-attendo/huddinge-81-clients-with-coords.csv"
   ```
   Use the `-with-coords.csv` file for beta-appcaire seed or dashboard CSV upload.

3. **FSR input**  
   `attendo_4mars_to_fsr.py "huddinge-81-clients - Data.csv" -o input_81_10mars_2w.json --start-date 2026-03-02 --end-date 2026-03-15 --address-coordinates address_coordinates.json --no-supplementary-vehicles`  
   → **input_81_10mars_2w.json**: 3746 visits (3422 standalone + 324 in visit groups), 39 vehicles, 446 shifts.

4. **Validate**  
   `submit_to_timefold.py validate .../input_81_10mars_2w.json`  
   → Validation OK.

5. **Solve**  
   `submit_to_timefold.py solve .../input_81_10mars_2w.json --configuration-id "" --wait --save .../output`  
   → Submitted; **route plan ID:** `f53554f1-5e8c-411f-8596-6ac7316cfe5e`.  
   Use `--configuration-id ""` if the default config ID is not found for the tenant.

## Reference

- Small dataset (TF Caire production): `57081ade-27e1-452f-900f-4107d3509ca6`.
- After solve completes, fetch solution and metrics as in main README (e.g. `fetch_timefold_solution.py <route_plan_id> --save output/<id>_output.json --metrics-dir metrics`).

---

# V2 pipeline (more rows, new Lathund, no geocode fallback)

Pipeline: **v2/huddinge-81-clients-v2 - Data.csv** + **v2 Lathund** → clean → geocode (all rows, no fallback) → add coords → FSR input → validate → solve.

## V2 time windows (Lathund)

| När på dagen | Window   |
|--------------|----------|
| Morgon       | 07:00–10:00 |
| Förmiddag    | 10:00–11:00 |
| Lunch        | 11:00–13:30 |
| Eftermiddag  | 13:30–15:00 |
| Middag       | 16:00–19:00 |
| Kväll        | 19:00–22:00 |

## V2 steps (run from recurring-visits/)

1. **Clean addresses** (LGH, VÅN, våning, tr/trappor, whitespace; same normalization as FSR)
   ```bash
   python3 huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/cleanup_addresses_in_csv.py \
     "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/huddinge-81-clients-v2 - Data.csv" \
     -o "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/huddinge-81-clients-v2 - Data-cleaned.csv"
   ```

2. **Geocode** (no fallback; use `--merge-existing` to reuse previous run’s JSON if needed)
   ```bash
   python3 huddinge-package/huddinge-4mars-csv/scripts/build_address_coordinates.py \
     "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/huddinge-81-clients-v2 - Data-cleaned.csv" \
     -o "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/address_coordinates_v2.json" \
     [--merge-existing "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/address_coordinates.json"]
   ```

3. **Add coordinates to CSV**
   ```bash
   python3 huddinge-package/huddinge-4mars-csv/full-csv/add_coordinates_to_csv.py \
     "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/huddinge-81-clients-v2 - Data-cleaned.csv" \
     --coordinates "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/address_coordinates_v2.json" \
     -o "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/huddinge-81-clients-v2-with-coords.csv"
   ```

4. **FSR input**
   ```bash
   python3 huddinge-package/huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py \
     "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/huddinge-81-clients-v2 - Data-cleaned.csv" \
     -o "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/input_v2_81_2w.json" \
     --start-date 2026-03-02 --end-date 2026-03-15 \
     --address-coordinates "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/address_coordinates_v2.json" \
     --no-supplementary-vehicles
   ```

5. **Validate**
   ```bash
   python3 scripts/submit_to_timefold.py validate \
     "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/input_v2_81_2w.json"
   ```

6. **Solve**
   ```bash
   python3 scripts/submit_to_timefold.py solve \
     "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/input_v2_81_2w.json" \
     --configuration-id "" --wait --save "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/output"
   ```

7. **Optional: feasibility and time-window reports**
   ```bash
   python3 huddinge-package/huddinge-4mars-csv/scripts/analyze_dependency_feasibility.py \
     "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/input_v2_81_2w.json" --all \
     -o "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/dependency_feasibility_v2_2w.json"

   python3 huddinge-package/huddinge-4mars-csv/scripts/map_visits_time_windows.py \
     "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/input_v2_81_2w.json" \
     "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/huddinge-81-clients-v2 - Data-cleaned.csv" \
     -o "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/map_visits_time_windows_v2_2w.txt"
   ```

## Seed (beta-appcaire) with V2 CSV

Use the v2 CSV that has Lat/Lon for dashboard seed:

```bash
ATTENDO_CSV_PATH=/path/to/recurring-visits/.../v2/huddinge-81-clients-v2-with-coords.csv yarn db:seed:attendo
ATTENDO_SCHEDULE_START_DATE=2026-03-02 yarn db:seed:attendo   # optional, for comparison with script pipeline
```

Or copy `v2/huddinge-81-clients-v2-with-coords.csv` to `apps/dashboard-server/src/seed-scripts/seed-data/attendo-huddinge-81-clients.csv` to make it the default seed file.
