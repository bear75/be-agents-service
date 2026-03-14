# Test tenant runs (da2de902 variants + one busy day)

**Analysis:** [ANALYSIS_combo_vs_wait_min.md](./ANALYSIS_combo_vs_wait_min.md) (combo vs wait-min). [ANALYSIS_VS_GOAL.md](./ANALYSIS_VS_GOAL.md) (all metrics and continuity vs brainstorm goal).

**Layout:** Each test has its own folder (see [FILE_INDEX.md](./FILE_INDEX.md)). 5 tests: `preferred_688faece/`, `wait_min_a4be8810/`, `combo_8e07450d/`, `from_patch_preferred_963c3aa9/`, `from_patch_combo/`. Inside each: `input.json` or `payload.json`, `output.json`, `continuity.csv`, `metrics/`.

**Efficiency metrics:** Run from `recurring-visits/scripts`. Example for preferred:
`python3 metrics.py <output.json> --input <input.json> --save <test_folder>/metrics`  
e.g. `--save "../huddinge-package/continuity -3march/pipeline_da2de902/test_tenant/preferred_688faece/metrics"`

**Continuity metrics:** Run `continuity_report.py` (from `recurring-visits/scripts`). Example for combo:
```bash
python3 continuity_report.py \
  --input ".../test_tenant/combo_8e07450d/input.json" \
  --output ".../test_tenant/combo_8e07450d/output.json" \
  --report ".../test_tenant/combo_8e07450d/continuity.csv"
```
Repeat for other test folders (use each folder’s `input.json` and `output.json`).

Or re-fetch a run with `--save` and `--metrics-dir` so the fetch script runs both metrics and continuity_report and writes `continuity.csv` next to the saved output. Target: ≤15 distinct caregivers per client.

**Tenant API key:** `tf_p_96b5507b-57be-4ab6-b0a6-08a9d3372938`  
**Important:** Use `--configuration-id ""` so the tenant uses its default config (no profile ID).

## Variants submitted

| Variant | Test folder | Route plan ID |
|--------|-------------|----------------|
| preferredVehicles + weight 2 | `preferred_688faece/input.json` | `688faece-5d53-4402-820f-267445310a04` |
| wait-min weight 3 | `wait_min_a4be8810/input.json` | `a4be8810-7812-4819-8aa5-1165e38a2b8d` |
| combo (preferred + wait-min) | `combo_8e07450d/input.json` | `8e07450d-69e1-414a-8cb7-8c09ca0849ed` |
| one busy day 2026-02-16 | `_archive/input_one_day_2026-02-16.json` | `78028dd1-...` (failed; see below) — **rebuilt with sanitized vehicle refs, resubmit** |

## Poll until complete and save output

```bash
cd recurring-visits
export TIMEFOLD_API_KEY=tf_p_96b5507b-57be-4ab6-b0a6-08a9d3372938

# Example: wait for preferred variant and save into its test folder
python3 scripts/submit_to_timefold.py solve "huddinge-package/continuity -3march/pipeline_da2de902/test_tenant/preferred_688faece/input.json" \
  --api-key "$TIMEFOLD_API_KEY" --configuration-id "" --no-register-darwin \
  --wait --save "huddinge-package/continuity -3march/pipeline_da2de902/test_tenant/preferred_688faece/output.json" --no-timestamp
```

## One-busy-day → full 2-week flow (after 1-day solve completes)

1. **Fetch 1-day solution**  
   Use `scripts/fetch_timefold_solution.py` with route plan ID `78028dd1-7711-4689-b384-3019e5762b86`.

2. **Extract client → vehicle**  
   From itineraries: visit `name` (e.g. `H026_24 - Bad/Dusch`) → person `H026`; vehicle id from the itinerary. Build map `client_id -> [vehicle_id]`.

3. **Patch full 2-week input**  
   For every visit in the full da2de902 input, set `preferredVehicles` from the client map (and remove or keep `requiredVehicles` as chosen).

4. **Submit full 2-week solve**  
   Submit the patched payload to the test tenant with `preferVisitVehicleMatchPreferredVehiclesWeight` (and optionally wait-min) to get the final 2-week plan.

## Regenerate variants

```bash
python3 scripts/prepare_continuity_test_variants.py \
  --input "huddinge-package/continuity -3march/2323 3 march origin contin/export-field-service-routing-v1-da2de902-fa25-432c-b206-413b630dd4df-input.json" \
  --out-dir "huddinge-package/continuity -3march/pipeline_da2de902/test_tenant"
```
Generated files (e.g. `input_preferred_vehicles_weight2.json`) appear in `test_tenant/`. Move each into the matching test folder and rename to `input.json` (e.g. into `preferred_688faece/input.json`).

## One-busy-day: fix for 78028dd1 failure

The first one-day run failed because visits still had `requiredVehicles` pointing to vehicles not on that day (e.g. weekend Helg_*). `build_one_busy_day_input.py` now **sanitizes** `requiredVehicles` and `preferredVehicles`: only IDs present in the filtered vehicle list are kept; if none remain, the field is removed. The one-day input is in `_archive/` (moved there as a side experiment). Resubmit from there or build a new one-day with the command below to get a new route plan for the one-busy-day → full 2-week flow.

## Build another one-busy-day input

```bash
python3 scripts/build_one_busy_day_input.py \
  --input "huddinge-package/continuity -3march/2323 3 march origin contin/export-field-service-routing-v1-da2de902-fa25-432c-b206-413b630dd4df-input.json" \
  --date 2026-02-17 \
  --output "huddinge-package/continuity -3march/pipeline_da2de902/test_tenant/input_one_day_2026-02-17.json"
```
