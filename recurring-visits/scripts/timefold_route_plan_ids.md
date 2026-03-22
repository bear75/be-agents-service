# Timefold FSR route plan (dataset) IDs

Stored IDs for fetching solutions with `fetch_timefold_solution.py`.  
See [Timefold docs: Request the solution](https://docs.timefold.ai/field-service-routing/latest/getting-started-with-field-service-routing#requestTheSolution).

## API keys by env

| Env         | Name        | Use for |
| ----------- | ----------- | ------- |
| **caire-prod** | `tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8` | Prod route plans, e.g. `77de8407-e4af-415a-a6c9-442f4f4426dd`. |
| test tenant | `tf_p_96b5507b-57be-4ab6-b0a6-08a9d3372938` | v3 continuity campaign (cf407218, c1ea12a5, d87e9a1a, 5e55bf3a). |

Set `TIMEFOLD_API_KEY` to the key for the plan’s tenant before fetch.

## Huddinge 2-week runs

| ID                                     | Env     | Date       | Description                                                                                                                                             |
| -------------------------------------- | ------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `391486da-ca6f-4928-a928-056a589842e1` | prod    | 2026-02-24 | Iter 1 base (no continuity pools); config `a43d4eec-9f53-40b3-82ad-f135adc8c7e3`; ~114 unassigned; output in `solve/iter1/`                             |
| `b288c5ed-7604-4e39-9f33-b246b7764b98` | prod    | 2026-02-24 | Iter 1 manual client-pool 15 (per-client cross-type pool, old strategy); ~217 unassigned; output in `solve/iter1/`                                      |
| `7632331d-a423-4b86-8070-27f9c78ddbad` | prod    | 2026-02-24 | Iter 1 area pool 15; ~1199 unassigned; output in `solve/iter1/`                                                                                         |
| `b430b592-d04e-4b23-a9a1-147b068ae811` | prod    | 2026-02-24 | FAILED — check status only                                                                                                                              |
| `5ff7929f-738b-4cfa-9add-845c03089b0d` | prod    | 2026-02-25 | First solve (origin input from `25feb-stagetf-corect/`); config `a43d4eec-...`; parent for from-patch; output in `solve/25feb_prod/`                    |
| `c87d58dd-5200-41a9-a334-e075c54a7d94` | staging | 2026-02-24 | Staging run; input `export-field-service-routing-v1-c87d58dd-...-input.json`, output trimmed in `solve/24feb/`                                          |
| `fa713a0d-f4e7-4c56-a019-65f41042e336` | staging | 2026-02-25 | From-patch run (unique weekdays for recurring weekly 2–6); parent/origin `c87d58dd-5200-41a9-a334-e075c54a7d94`; files in `solve/25feb-stagetf-corect/` |
| `77de8407-e4af-415a-a6c9-442f4f4426dd` | prod    | 2026-03-16 | Huddinge v3; 41 vehicles, 464 shifts, 74 unassigned; field eff 76.5%; output in `data/huddinge-v3/fetched_77de8407/`. **Use prod API key** to fetch.   |

## Dataset origin and patch (fa713a0d — recurring weekly 2–6)

To replicate the **fa713a0d** dataset in Timefold (e.g. prod), use the same **origin** (first solve) and **from-patch** payload.

| What           | ID / file                                               |
| -------------- | ------------------------------------------------------- |
| **Dataset ID** | `fa713a0d-f4e7-4c56-a019-65f41042e336`                  |
| **Parent ID**  | `c87d58dd-5200-41a9-a334-e075c54a7d94`                  |
| **Origin ID**  | `c87d58dd-5200-41a9-a334-e075c54a7d94` (same as parent) |

**Files (all under `huddinge-package/solve/25feb-stagetf-corect/`):**

- **Origin input (first solve):** `export-field-service-routing-v1-c87d58dd-5200-41a9-a334-e075c54a7d94-input.json`
- **Origin output (baseline):** `export-field-service-routing-c87d58dd-5200-41a9-a334-e075c54a7d94-output.json`
- **Patched input (for metrics):** `export-field-service-routing-v1-fa713a0d-f4e7-4c56-a019-65f41042e336-input.json`
- **From-patch payload:** `export-field-service-routing-v1-fa713a0d-f4e7-4c56-a019-65f41042e336-patch-request.json`
- **Patched output (optimized):** `export-field-service-routing-fa713a0d-f4e7-4c56-a019-65f41042e336-output.json`

**Confirm dataset with metrics (unique weekdays, recurring weekly 2–6):**

```bash
cd docs_2.0/recurring-visits/scripts

python3 metrics.py \
  ../huddinge-package/solve/25feb-stagetf-corect/export-field-service-routing-fa713a0d-f4e7-4c56-a019-65f41042e336-output.json \
  --input ../huddinge-package/solve/25feb-stagetf-corect/export-field-service-routing-v1-fa713a0d-f4e7-4c56-a019-65f41042e336-input.json \
  --save ../huddinge-package/metrics/
```

Compare `total_visits_assigned`, `care_visits` (from input summary), and shift/visit counts to the baseline (c87d58dd) to confirm it’s the same recurring 2–6 dataset with pinned weekdays.

**Confirmed (2026-02-25):** Metrics run on `25feb-stagetf` fa713a0d output: **3478 care visits** (3334 solo + 144 double-employee), **3622 Timefold visits**, **3616 assigned** / 6 unassigned, **311 shifts** (0 empty), **42 vehicles**. Plan ID `fa713a0d-f4e7-4c56-a019-65f41042e336`. This matches the unique-weekdays recurring weekly 2–6 dataset.

**Replicate in Timefold prod (same dataset + prod config):**

- **Prod config ID:** `a43d4eec-9f53-40b3-82ad-f135adc8c7e3`
- **Stage config ID (reference):** `6a4e6b5f-8767-48f8-9365-7091f7e74a37`

```bash
cd docs_2.0/recurring-visits/scripts

# 1) Submit first solve (creates new route plan in prod)
TIMEFOLD_API_KEY=tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8 \
  python3 submit_to_timefold.py solve \
  ../huddinge-package/solve/25feb-stagetf-corect/export-field-service-routing-v1-c87d58dd-5200-41a9-a334-e075c54a7d94-input.json \
  --configuration-id a43d4eec-9f53-40b3-82ad-f135adc8c7e3 \
  --wait --save ../huddinge-package/solve/25feb_prod/output.json

# Note the new route plan ID from the script output (current prod parent: 5ff7929f-738b-4cfa-9add-845c03089b0d).

# 2) Submit from-patch (same payload as stage; use the prod parent ID from step 1, e.g. 5ff7929f-738b-4cfa-9add-845c03089b0d)
TIMEFOLD_API_KEY=tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8 \
  python3 submit_to_timefold.py from-patch \
  ../huddinge-package/solve/25feb-stagetf-corect/export-field-service-routing-v1-fa713a0d-f4e7-4c56-a019-65f41042e336-patch-request.json \
  --route-plan-id 5ff7929f-738b-4cfa-9add-845c03089b0d \
  --configuration-id a43d4eec-9f53-40b3-82ad-f135adc8c7e3 \
  --wait --save ../huddinge-package/solve/25feb_prod/from-patch-output.json
```

Then fetch the from-patch solution and run metrics:

```bash
# Replace <FROM_PATCH_ROUTE_PLAN_ID> with the ID printed after step 2
TIMEFOLD_API_KEY=tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8 \
  python3 fetch_timefold_solution.py <FROM_PATCH_ROUTE_PLAN_ID> \
  --save ../huddinge-package/solve/25feb_prod/export-field-service-routing-prod-from-patch-output.json \
  --input ../huddinge-package/solve/25feb-stagetf-corect/export-field-service-routing-v1-fa713a0d-f4e7-4c56-a019-65f41042e336-input.json \
  --metrics-dir ../huddinge-package/metrics/
```

## Research — Approach 0 & sweep (2026-02-24 / 25)

| ID                                     | Description                                                                                             |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `effb00f8-1aef-4440-b6bd-6e0436591ce1` | Approach 0 (direct slinga requiredVehicles); input `solve/research/approach-0/input_slinga_direct.json` |
| `2d81ea97-7239-48af-8397-ccd11981433b` | Sweep N=1 (first-run top-1 per client)                                                                  |
| `9c9da77d-c984-4f3c-b4a0-fc0ad2bbc0b8` | Sweep N=2                                                                                               |
| `eb1622e5-b460-44ab-8cee-5244409c63c2` | Sweep N=3                                                                                               |
| `6c6e1d8b-a449-4fa2-8d41-8f33260777ba` | Sweep N=5                                                                                               |
| `e2eecdc3-0103-4f7f-bb1e-b1dc071642d6` | Sweep N=8                                                                                               |
| `9c329734-f51d-4d43-8d01-7a717f71a07d` | Sweep N=15                                                                                              |

## Fetch examples

```bash
# From repo root (appcaire)
cd docs_2.0/recurring-visits/scripts

# Prod run (after solve completes): fetch and save only
TIMEFOLD_API_KEY=tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8 \
  python3 fetch_timefold_solution.py 391486da-ca6f-4928-a928-056a589842e1 \
  --save ../huddinge-package/solve/24feb_prod/export-field-service-routing-prod-391486da-output.json

# Fetch, save, run metrics (and run_analyze_metrics_frompatch if empty shifts)
TIMEFOLD_API_KEY=tf_p_... \
  python3 fetch_timefold_solution.py 391486da-ca6f-4928-a928-056a589842e1 \
  --save ../huddinge-package/solve/24feb_prod/output.json \
  --input ../huddinge-package/solve/input_20260224_202857.json \
  --metrics-dir ../huddinge-package/metrics/
```

## Huddinge v3/22 campaign — prod “rest” batch (2026-03-22)

Config: `09a98b7a-956c-456a-b478-00f89880b826`. Inputs: `huddinge-4mars-csv/.../v3/22/campaign_20260322/prepared/`.

| ID | Prepared variant |
| -- | ---------------- |
| `0ba5d5c7-d308-4bfe-b5b5-2c1d9cf08edf` | pool12 continuity-heavy |
| `85a24091-3866-4fcf-9f19-cd08d728507f` | pool12 combo |
| `54de1372-6fd4-4af9-bf3e-e004a868294f` | pool8_extra efficiency-first |
| `2fcded88-87d5-4125-8646-5b991d264d78` | pool8_extra balanced |
| `8ecab57b-240d-4874-a86a-6aff215d228b` | pool8_extra continuity-heavy |
| `1e96d8cb-2b37-410b-a82f-95d1cec253d4` | pool8_extra combo |

Fetch from **be-agent-service** root with `scripts/timefold/fetch.py` (or symlinked `fetch_timefold_solution.py`).
