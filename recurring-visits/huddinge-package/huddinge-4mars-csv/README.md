# Huddinge 4mars CSV (Attendo databehov)

This folder contains the **Attendo** export and all 4mars artifacts: scripts, docs, input/output, reports, and metrics. Used for Timefold Field Service Routing (FSR) for the planning window **2 March–15 March 2026**.

## Folder layout

| Path | Contents |
|------|----------|
| `ATTENDO_DATABEHOV_PER_KUND_OCH_BESOK - data.csv` | Source CSV (Attendo databehov). |
| `export-field-service-routing-v1-4mars-input.json` | Latest FSR input (from CSV→JSON script). |
| **scripts/** | 4mars scripts + README: `attendo_4mars_to_fsr.py`, `analyze_4mars_csv_to_json.py`, `map_visits_time_windows.py`. |
| **docs/** | `CSV_TO_INPUT_VERIFICATION.md`, `CSV_TILL_INPUT_VERIFIERING.md`, `RECURRING_VISITS_HANDLING.md`. |
| `input/` | Timestamped or alternate input JSONs (e.g. `input_4mars_YYYYMMDD_HHMMSS.json`). |
| `output/` | Solve output JSONs: `<route_plan_id>_output.json` or named (e.g. `output_4mars.json`). |
| `reports/` | Mapping report (`map_visits_time_windows_report.txt`), CSV→JSON analysis. |
| `metrics/` | Metrics from fetch/solve (when using `--metrics-dir`): `metrics_*.json`, `metrics_report_*.txt`. |

**Documentation:** See **`docs/`** for CSV→input verification (Swedish + English), time-window mapping, and recurrence handling. Script details: **`scripts/README.md`**.

## Column meanings

| Column | Purpose |
|--------|--------|
| Slinga | Route/round name → vehicle ID and shift assignment |
| Starttid | Preferred start time (HH:MM) |
| Längd | Duration in minutes → visit `serviceDuration` |
| Återkommande | Recurrence: "Varje vecka, mån tis ons tor fre", "Varannan vecka, tis", "Varje dag", "Var 4:e vecka, mån" |
| Dubbel | Same number = two employees (visit group) |
| När på dagen | Morgon / Lunch / Kväll → time window |
| Schift | Dag / Helg / Kväll → shift type |
| Kundnr, Gata, Postnr, Ort | Client and address (geocoded to lat/lon) |
| Före, Efter | Minutes flex for time window |
| Antal tim mellan besöken | Min delay between visits (e.g. "3,5timmar" → visit dependency `minDelay`) |
| Kritisk insats Ja/nej | "Ja" → pin weekly visits to day (pinningRequested) where applicable |

## Planning window and time windows

- **Start:** Monday 2 March 2026  
- **End:** Sunday 15 March 2026 (2 weeks)

**Visit slots:** Morgon 07:00–10:30, Lunch 11:00–13:30, Kväll 16:00–19:00.

**Shifts:** Dag 07:00–15:00 (break 10:00–14:00, 30 min at office), Helg 07:00–14:30, Kväll 16:00–22:00.

## How to run

**4mars scripts** live in **`scripts/`** in this folder; **submit/fetch/metrics** use shared scripts in `recurring-visits/scripts/`. Run commands from **`recurring-visits/`** (or from `be-agent-service/` with paths adjusted). See **`scripts/README.md`** for script details.

**1. CSV → FSR input**

```bash
python huddinge-package/huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py \
  "huddinge-package/huddinge-4mars-csv/ATTENDO_DATABEHOV_PER_KUND_OCH_BESOK - data.csv" \
  -o huddinge-package/huddinge-4mars-csv/export-field-service-routing-v1-4mars-input.json
```

Optional timestamped output: `-o huddinge-package/huddinge-4mars-csv/input/input_4mars_$(date +%Y%m%d_%H%M%S).json`. Use `--no-geocode` to skip geocoding.

**2-week window with new visit id/name** (same CSV, same strategy; id = `Hxxx_r{row}_{occ}`, name = `Hxxx När på dagen Skift Insats`). Add `--no-supplementary-vehicles` to match reference (26 vehicles):

```bash
python huddinge-package/huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py \
  "huddinge-package/huddinge-4mars-csv/ATTENDO_DATABEHOV_PER_KUND_OCH_BESOK - data.csv" \
  --start-date 2026-03-02 --end-date 2026-03-15 \
  --no-supplementary-vehicles \
  -o huddinge-package/huddinge-4mars-csv/input/input_4mars_2w_$(date +%Y%m%d_%H%M%S).json
```

**Same input with new names only (no geocoding):** use the reference input and rewrite visit id/name so structure stays identical. See `scripts/README.md` — `rewrite_visit_ids_in_input.py` and `compare_input_structure.py`.

**2. Validate, submit, save output**

```bash
cd recurring-visits/scripts
python submit_to_timefold.py validate "../../huddinge-package/huddinge-4mars-csv/export-field-service-routing-v1-4mars-input.json"
python submit_to_timefold.py solve "../../huddinge-package/huddinge-4mars-csv/export-field-service-routing-v1-4mars-input.json" --wait --save "../../huddinge-package/huddinge-4mars-csv/output"
```

**3. Fetch and metrics**

```bash
python fetch_timefold_solution.py <route_plan_id> --save "../../huddinge-package/huddinge-4mars-csv/output/<id>_output.json" --metrics-dir "../../huddinge-package/huddinge-4mars-csv/metrics"
```

**4. Reports (default: this folder’s `reports/`)**

```bash
python huddinge-package/huddinge-4mars-csv/scripts/map_visits_time_windows.py \
  huddinge-package/huddinge-4mars-csv/export-field-service-routing-v1-4mars-input.json \
  "huddinge-package/huddinge-4mars-csv/ATTENDO_DATABEHOV_PER_KUND_OCH_BESOK - data.csv"

python huddinge-package/huddinge-4mars-csv/scripts/analyze_4mars_csv_to_json.py \
  "huddinge-package/huddinge-4mars-csv/ATTENDO_DATABEHOV_PER_KUND_OCH_BESOK - data.csv" \
  huddinge-package/huddinge-4mars-csv/export-field-service-routing-v1-4mars-input.json
```

## IDs in the JSON

| Entity | ID format | Source |
|--------|-----------|--------|
| **Visit** | `{Kundnr}_r{row}_{occ}` (new) or `{Kundnr}_{löpnr}` (legacy) | New: row = CSV row index, occ = occurrence within that row. Ex: `H015_r0_1`, `H015_r0_2`. Legacy: `H015_1`, `H015_2`. |
| **Visit group** | `VG_{dubbel}_{date}` | Dubbel (slugified) + date_iso. Same Dubbel + same date → one group with two visits. Ex: `VG_123_2026-03-02`. |
| **Vehicle** | Slug of Slinga | One vehicle per unique Slinga. Ex: `Dag_01_Central_1`. |
| **Shift** | `{vehicle_id}_{date_iso}_{type}` | Deterministic: vehicle + date + `dag` / `helg` / `kvall`. Ex: `Dag_01_Central_1_2026-03-02_dag`. |

## CSV vs JSON – sammanställning

After each run the script prints a summary to stderr:

- **CSV:** Rader (besöksrader), unika kunder (Kundnr), utökade besök (recurrence × planeringsfönster), rader med Dubbel, unika Slingor.
- **JSON:** Besök standalone, antal visit groups + besök i grupper, besök totalt, vehicles, shifts.

Besök totalt i JSON motsvarar utökade besök som har adress/koordinat (vid geocoding). Vehicles = en per Slinga. Shifts = vehicle_id + datum + typ (dag/helg/kväll).

## Related: full FSR pipeline and API key

For the **full pipeline** (new CSV → solve with TF config → fetch solution → analyze metrics and continuity → trim empty/adjust shifts → from-patch → fetch → analyze → metrics) and the **test tenant API key**, see the **tf-fsr-prototype** agent in the beta-appcaire repo:

- **Agent:** [tf-fsr-prototype](beta-appcaire/.cursor/agents/tf-fsr-prototype.md) (path when both repos are in workspace: `beta-appcaire/.cursor/agents/tf-fsr-prototype.md`)
- The agent doc includes the test tenant API key and references continuity vs efficiency analysis, from-patch trim, and test_tenant layout.
