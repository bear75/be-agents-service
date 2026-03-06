# E2E pipeline: 4mars CSV → solve → metrics & continuity

**Route plan ID:** `0cf9ea85-9afa-41f1-a9ae-e3f31ba4315b`  
**Status:** All visits assigned (1486/1486). Solve was still improving (SOLVING_ACTIVE) at fetch time.

## E2E flow (canonical)

1. **Input from CSV** — We generate `input.json` from your CSV with the script (we do not use a pre-made input). This is the single source of truth for the run.
   ```bash
   python huddinge-package/huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py \
     "huddinge-package/huddinge-4mars-csv/ATTENDO_DATABEHOV_PER_KUND_OCH_BESOK - data.csv" \
     -o huddinge-package/huddinge-4mars-csv/e2e_pipeline_0cf9ea85/input.json
   ```
2. **Solve** — Submit `input.json` to Timefold FSR (test tenant). Result: route plan `0cf9ea85-...`.
3. **Fetch** — Download solution → `output.json` in this folder.
4. **Metrics** — Run metrics with this folder’s `input.json` and `output.json` → `metrics/`.
5. **Continuity** — Run continuity report → `continuity.csv` in this folder.

All artifacts for this run live here so you can analyze: visit time windows vs CSV, empty shifts, efficiency, continuity.

## Contents of this folder

| File / folder | Description |
|---------------|-------------|
| `input.json` | FSR model input **generated from CSV** by `attendo_4mars_to_fsr.py` (planning window, visits, time windows, dependencies, vehicles, shifts). |
| `output.json` | Timefold FSR solution (route plan `0cf9ea85-...`): itineraries, assignments, score. |
| `metrics/` | Metrics from `metrics.py`: `metrics_*.json`, `metrics_report_*.txt` (efficiency, travel, wait, empty shifts, cost/revenue). |
| `continuity.csv` | Per-client continuity (distinct caregivers per client; lower is better). |

## Verification docs (CSV → input mapping)

- **Svenska:** `huddinge-package/huddinge-4mars-csv/docs/CSV_TILL_INPUT_VERIFIERING.md` — hur CSV kolumner mappas till tidsfönster, beroenden, slingor, återkommande.
- **Recurring:** `huddinge-package/huddinge-4mars-csv/docs/RECURRING_VISITS_HANDLING.md` — hantering av återkommande besök.

Use these to check that visits in `input.json` / `output.json` match what you expect from the CSV (När på dagen, Skift, Antal tim mellan besöken, Dubbel, etc.).

## Snapshot metrics (fetch time)

- **Visits assigned:** 1486 / 1486 (0 unassigned)
- **Shifts:** 1124 total; 629 with visits, **495 empty**
- **Travel efficiency:** 58.37% (target >67.5%)
- **Continuity:** 15 clients; distinct caregivers per client in `continuity.csv` (goal ≤15 per client; current run has many vehicles per client – config/weights can be tuned).

---

## Pipeline: nästa steg (färdig lösning → trim → from-patch → kontinuitet)

Vi väntar med att skicka verifieringsdokument till Attendo. Först: **analysera färdig lösning**, **trimma tomma skift**, **from-patch**, sedan **kontinuitet och metrics**. Troligen la vi till onödiga skift (Extra_Dag_/Extra_Kvall_) när problemet var omöjliga besök – nu är alla 1486 tilldelade, så efter trim förväntar vi färre skift.

### 1. När solve är SOLVING_COMPLETED

- **Fetch igen** (samma route plan ID) → skriv över `output.json` i denna mapp.
- **Kör metrics** på färdig lösning:
  ```bash
  cd recurring-visits/scripts
  python metrics.py ../huddinge-package/huddinge-4mars-csv/e2e_pipeline_0cf9ea85/output.json \
    --input ../huddinge-package/huddinge-4mars-csv/e2e_pipeline_0cf9ea85/input.json \
    --save ../huddinge-package/huddinge-4mars-csv/e2e_pipeline_0cf9ea85/metrics
  ```
- Notera: **antal tomma skift** (i senaste snabbet: 495). Detta är baseline före trim.

### 2. Trim tomma skift (build_from_patch) — **KLAR**

- Payload byggd: **629 skift** trimmas till besöksspann, **495 tomma skift** borttagna. Fil: `from_patch/payload.json`.
- **OBS:** From-patch accepteras endast när planen är **SOLVING_COMPLETED**. Plan 0cf9ea85 var SOLVING_ACTIVE → 404. Kör from-patch-kommandot nedan **när solve är färdig**.

### 2b. Parallell körning: ny input utan tomma skift (trimmed fresh) — **IGÅNG**

- Baserat på **pågående** lösning (0cf9ea85) byggdes en **ny input** där de **495 tomma skiften** redan är borttagna (extra skift vi lagt till under processen), så vi sparar tid med **parallella solves**.
- **Script:** `recurring-visits/scripts/build_trimmed_input.py` (läser output + input → skriver input utan tomma skift och oanvända fordon).

| Körning | Input | Skift | Fordon | Route plan ID | Status |
|---------|-------|-------|--------|----------------|--------|
| 1 (original) | `input.json` | 1124 | 48 | `0cf9ea85-...` | Pågår |
| 2 (trim 1) | `trimmed_fresh/input_trimmed.json` | 629 | 48 | **`7e1b6b57-...`** | Pågår (alla tilldelade, optimerar rutterna). **324 tomma skift** i nuvarande lösning. |
| 3 (trim 2) | `trimmed_fresh/trimmed2/input_trimmed2.json` | 305 | 46 | **`3e4c5eb1-...`** | Alla tilldelade på ~10 s. **19 tomma skift** i nuvarande lösning. |
| 4 (trim 3) | `trimmed_fresh/trimmed3/input_trimmed3.json` | **286** | 46 | **`2f08d3d2-...`** | Ny, parallell solve (19 tomma borttagna). |

- När 7e1b6b57 är färdig: fetch → `trimmed_fresh/output.json`, metrics + continuity i `trimmed_fresh/`.
- Trim 2 byggd från 7e1b6b57 output: 324 tomma skift + 2 oanvända fordon borttagna → 305 skift, 46 fordon. Tredje solve startad parallellt.

### 3. From-patch (kör när 0cf9ea85 är SOLVING_COMPLETED)

- Skicka from-patch mot **samma route plan ID** (0cf9ea85-...). Timefold kräver att planen är färdig (SOLVING_COMPLETED); annars 404.
  ```bash
  cd recurring-visits/scripts
  python submit_to_timefold.py from-patch ../huddinge-package/huddinge-4mars-csv/e2e_pipeline_0cf9ea85/from_patch/payload.json \
    --route-plan-id 0cf9ea85-9afa-41f1-a9ae-e3f31ba4315b \
    --api-key "tf_p_96b5507b-57be-4ab6-b0a6-08a9d3372938" \
    --configuration-id "" --wait \
    --save ../huddinge-package/huddinge-4mars-csv/e2e_pipeline_0cf9ea85/from_patch \
    --save-id ../huddinge-package/huddinge-4mars-csv/e2e_pipeline_0cf9ea85/from_patch/route_plan_id.txt
  ```
- Efter körning: ny route plan ID i `from_patch/route_plan_id.txt`, output i `from_patch/<ny_id>_output.json`.

### 4. Fetch from-patch-lösning + metrics + kontinuitet

- Hämta den **nya** route plan ID från `from_patch/route_plan_id.txt`.
- Fetch → spara som `e2e_pipeline_0cf9ea85/from_patch/output.json`.
- Kör metrics med `--exclude-inactive` (from-patch: trimmade fönster):
  ```bash
  python fetch_timefold_solution.py <NY_ROUTE_PLAN_ID> --api-key "..." \
    --save ../huddinge-package/huddinge-4mars-csv/e2e_pipeline_0cf9ea85/from_patch/output.json \
    --input ../huddinge-package/huddinge-4mars-csv/e2e_pipeline_0cf9ea85/input.json \
    --metrics-dir ../huddinge-package/huddinge-4mars-csv/e2e_pipeline_0cf9ea85/from_patch/metrics
  ```
  (Om metrics inte körs automatiskt pga status: kör `metrics.py` manuellt med `--exclude-inactive`.)
- Kör continuity_report.py mot from_patch/output.json → `from_patch/continuity.csv`.

### 5. Analysera mot mål

- **Referens:** `huddinge-package/continuity -3march/pipeline_da2de902/test_tenant/ANALYSIS_VS_GOAL.md` (kontinuitet ≤15, fälteffektivitet >67,5%).
- **Konfig/vikter:** `recurring-visits/docs/brainstorms/2026-03-03-continuity-config-weights-brainstorm.md`.
- Efter trim: jämför antal skift (förväntat mycket färre än 1124), tomma skift (0), field efficiency och kontinuitet per klient.

### 6. Därefter: kontinuitet och full Huddinge-data

- **Först:** Säkerställa att besöken är rätt tolkade (CSV_TILL_INPUT_VERIFIERING.md + Attendo verifiering).
- **Sedan:** Attendo lägger till alla besök för Huddinge i denna nya CSV-tolkning.
- **Därefter:** Konfigurera kontinuitet (requiredVehicles / preferredVehicles, vikter) enligt brainstorm och ANALYSIS_VS_GOAL; köra profiler (Preferred, Wait-min, Combo) på full dataset vid behov.
