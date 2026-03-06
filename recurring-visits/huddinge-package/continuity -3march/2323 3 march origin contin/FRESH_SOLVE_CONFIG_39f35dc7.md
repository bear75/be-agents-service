# Fresh solve with config 39f35dc7 (comparison run)

**Input:** `export-field-service-routing-v1-da2de902-fa25-432c-b206-413b630dd4df-input.json`  
- 42 vehicles, 412 shifts, 3334 solo + 144 groups (3622 visits), 3332 with requiredVehicles (continuity).

**Config:** `39f35dc7-aaa6-4bc6-9be5-4ea960ffaa40`

**Submitted:** 2026-03-03 · **Route plan ID:** `f292fb0b-fc7e-4765-8496-762c8c68fafa`

**Done:** Fetched f292fb0b (SOLVING_COMPLETED), ran metrics (51.09%, 78 empty shifts), built from-patch (trim 334, remove 6 empty shifts + 4 vehicles), submitted from-patch → **93c933e2-25ac-4c3e-9522-a864b353ee52**.

To fetch the from-patch solution and run metrics with --exclude-inactive when 93c933e2 completes:
```bash
cd be-agent-service/recurring-visits/scripts
TIMEFOLD_API_KEY=tf_p_... python3 fetch_timefold_solution.py 93c933e2-25ac-4c3e-9522-a864b353ee52 --save "../huddinge-package/continuity -3march/pipeline_39f35dc7/from_patch_output.json" --input "../huddinge-package/continuity -3march/2323 3 march origin contin/export-field-service-routing-v1-da2de902-fa25-432c-b206-413b630dd4df-input.json" --metrics-dir "../huddinge-package/continuity -3march/metrics_39f35dc7"
python3 solve_report.py "../huddinge-package/continuity -3march/pipeline_39f35dc7/from_patch_output.json" --input "../huddinge-package/continuity -3march/2323 3 march origin contin/export-field-service-routing-v1-da2de902-fa25-432c-b206-413b630dd4df-input.json" --save "../huddinge-package/continuity -3march/metrics_39f35dc7" --exclude-inactive
```
