# KOLADA kontinuitet och combo-pools för v2 (115 kunder)

## Klientantal: v1 vs v2

| Dataset | Unika Kundnr | Filnamn |
|--------|----------------|--------|
| **v1** | 81 | huddinge-81-clients (gammal) |
| **v2** | **115** | `huddinge-81-clients-v2-with-coords.csv` |

v2-CSV:en har **115 unika Kundnr**, inte 81. 81 är från v1.

## KOLADA = kontinuitet per person (Kundnr)

- **KOLADA:** En rad per person (Kundnr). Genomsnitt antal unika vårdgivare per person över perioden (2 veckor). Mål t.ex. ≤ 15.
- **Dashboard/UI** räknar redan KOLADA (visit.clientId → person).
- **continuity_report.py** använder nu KOLADA som standard (`--kolada`, default): person härleds från visit-namn (v1: `H026_24 - ...` → H026; v2: `H015 Morgon Dag Tillsyn` → H015).

## Kontinuitet räknas från input/output JSON (inte CSV)

- **Källa:** FSR input JSON (visit → Kundnr/person) + FSR output JSON (visit → vehicle/caregiver).
- **115 kunder:** DB har 115 klienter; i output har 97 av dem minst ett tilldelat besök (18 kan vara unassigned).
- **41 anställda:** Output har 41 vehicles (fordon = vårdgivare), 474 shifts, 379 shifts med besök (1 tom).

## Nuvarande v2-lösning (d2a6a01b): katastrof enligt KOLADA

- **Kontinuitet (script, endast Kundnr):** 97 klienter med besök, **genomsnitt 17,16** unika vårdgivare per klient (41 aktiva fordon). Många klienter med 20–34 olika vårdgivare.
- **Kontinuitetspoäng (UI):** Beräknas från DB assignments (samma logik: genomsnitt unika vårdgivare per clientId).
- Oavsett exakt tal: kontinuitet är för dålig för KOLADA; behov av ny körning med **continuity pools** och **combo-strategi**.

Kör kontinuitet enbart för 115 Kundnr (H-nummer) från input/output JSON:
`continuity_report.py --input ... --output ... --only-kundnr [--report ...]`

## Strategi: combo pools (enligt continuity -3march)

- **Combo** = mjuka pools (`preferredVehicles`) + vikter: `preferVisitVehicleMatchPreferredVehiclesWeight=2`, `minimizeWaitingTimeWeight=3`.
- Referens: `continuity -3march/pipeline_da2de902/test_tenant/ANALYSIS_VS_GOAL.md` och `_archive/CONTINUITY_RUN_57b3a619.md`.
- På 3-mars-datan gav **Preferred** bäst kontinuitet (0 över 15), **Combo** bättre genomförbarhet (färre unassigned) men fler klienter över 15. För v2 (115 kunder) kör vi combo för att balansera genomförbarhet och kontinuitet.

## Steg för att köra v2 med combo-pools

### 1. Pools från nuvarande v2-lösning (first-run)

Bygg per-person-pools (max 15 fordon per Kundnr) från nuvarande output:

```bash
cd /Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits

python3 scripts/build_continuity_pools.py \
  --source first-run \
  --input "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/input/export-field-service-routing-v1-d2a6a01b-3309-4db5-ab4c-78ad1a218c19-input.json" \
  --output "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/output/export-field-service-routing-d2a6a01b-3309-4db5-ab4c-78ad1a218c19-output.json" \
  --out "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/continuity/client_pools_v2_115.json" \
  --max-per-client 15 \
  --use-preferred \
  --patch-fsr-input "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/input/export-field-service-routing-v1-d2a6a01b-3309-4db5-ab4c-78ad1a218c19-input.json" \
  --patched-input "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/continuity/input_v2_with_pools.json"
```

`--use-preferred` ger mjuka pools (preferredVehicles) som combo-varianten förväntar sig.

### 2. Skapa combo-variant

```bash
python3 scripts/prepare_continuity_test_variants.py \
  --input "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/continuity/input_v2_with_pools.json" \
  --out-dir "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/continuity/variants"
```

Det skrivs t.ex. `input_combo_preferred_and_wait_min.json` i `variants/`.

### 3. Skicka combo till Timefold

Använd test-tenant API-nyckel och submit-script som i övrig pipeline (t.ex. `submit_to_timefold.py solve` med payload från `variants/input_combo_preferred_and_wait_min.json`). Spara route_plan_id för fetch och analys.

### 4. Efter solve: hämta output, metrics, kontinuitet (KOLADA)

```bash
# Fetch output (ersätt ROUTE_PLAN_ID)
python3 scripts/fetch_timefold_solution.py --route-plan-id ROUTE_PLAN_ID --out "v2/continuity/combo_output.json"

# Metrics (utan idle)
python3 scripts/metrics.py --input "v2/input/..." --output "v2/continuity/combo_output.json" --exclude-inactive --save "v2/continuity/metrics"

# Kontinuitet KOLADA (per Kundnr, 115 personer)
python3 scripts/continuity_report.py \
  --input "v2/input/export-field-service-routing-v1-d2a6a01b-...-input.json" \
  --output "v2/continuity/combo_output.json" \
  --report "v2/continuity/continuity_kolada.csv"
```

Jämför genomsnitt kontinuitet och antal klienter > 15 med målet (KOLADA ≤ 15).

## Filer uppdaterade för KOLADA / v2

- **continuity_report.py:** `name_to_person_kolada()`, `load_visit_to_person_kolada()`, default `--kolada` (per Kundnr). v2-namn utan " - " tolkas som "H015 ..." → H015.
- **build_continuity_pools.py:** `visit_name_client_to_person()` hanterar `_rNN` (v2) så att first-run-pools blir per person (Kundnr).

## Strategier skickade till solve (flera körningar)

Samma v2-input med pools, olika vikter. Submit utan `--configuration-id` (payload config används).

| Strategi | Variant-fil | Route plan ID |
|----------|-------------|----------------|
| **Combo** (redan skickad) | `input_combo_preferred_and_wait_min.json` | `cdfbe510-093f-490e-8d9a-c8172e40710f` |
| **Preferred weight 2** | `input_preferred_vehicles_weight2.json` | `57c49c98-7786-4d0c-8cc4-34e29cdac339` |
| **Wait-min weight 3** | `input_wait_min_weight3.json` | `a80bf065-9c56-48c2-a7be-c5fee68f35a9` |
| **Preferred weight 10** | `input_preferred_weight10.json` | `22a3d602-89e2-4c6f-b862-b8acba05069d` |

Hämta output och räkna kontinuitet (KOLADA, `--only-kundnr`) för varje när solve är klar (kör från `recurring-visits/`):

```bash
python3 scripts/fetch_timefold_solution.py <ROUTE_PLAN_ID> --save "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/continuity/output_<STRATEGY>.json"
python3 scripts/continuity_report.py --input "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/continuity/input_v2_with_pools.json" --output "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/continuity/output_<STRATEGY>.json" --only-kundnr --report "huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/continuity/continuity_<STRATEGY>.csv"
```
