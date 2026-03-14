# Pipeline: continuity da2de902 (original + continuity, correct IDs)

**da2de902-fa25-432c-b206-413b630dd4df** is the **continuity** run (same structure as original 5ff7929f but with requiredVehicles and correct client IDs). 5ff7929f is the non-continuity run we already had metrics for.

## What was run

1. **Fetch da2de902** – Continuity solution (42 vehicles, 412 shifts, 3526 assigned, 96 unassigned, 78 empty shifts).
2. **Metrics (before)** – Paid time (shift, incl. break) = 3000h; Assignable (shift − break) = 2891h; efficiency 51.09%; 78 empty shifts.
3. **Trim + from-patch** – Pinned 3526 visits, trimmed 334 shifts to visit span, removed 6 empty shifts and 4 empty vehicles → submitted.
4. **New from-patch plan** – **e5de3f5d-d235-4c6c-944b-01845827dbed** (parent/origin da2de902).
5. **Metrics again** – Fetched e5de3f5d (was still SOLVING_ACTIVE), ran `solve_report --exclude-inactive`: **0 empty shifts**, 334 shifts with visits. Reported efficiency 2.67% is an artifact of in-progress solve (untrimmed shift windows).

## When e5de3f5d is SOLVING_COMPLETED

Re-fetch and re-run metrics to get **efficiency ≈ 90%** (same as original after idle removal):

```bash
cd be-agent-service/recurring-visits/scripts

TIMEFOLD_API_KEY=tf_p_... python3 fetch_timefold_solution.py e5de3f5d-d235-4c6c-944b-01845827dbed \
  --save "../huddinge-package/continuity -3march/pipeline_da2de902/from_patch_output.json"

python3 solve_report.py "../huddinge-package/continuity -3march/pipeline_da2de902/from_patch_output.json" \
  --input "../huddinge-package/solve/input_continuity_e77e9ea3_submitted.json" \
  --save "../huddinge-package/continuity -3march/metrics_da2de902" \
  --exclude-inactive
```

Then check **Efficiency (visit / (shift − break))** in the new report; it should be ~90% when the solve is complete and shift times are trimmed.

## Metrics script update (paid vs assignable)

- **Paid time** = shift (includes break) → used for **salary cost**.
- **Assignable time** = shift − break → used for **efficiency denominator** (breaks paid but not assignable).
- Reports now show both lines and the efficiency formula unchanged: visit / (shift − break).

## Artifacts

| Path | Description |
|------|-------------|
| `continuity -3march/pipeline_da2de902/output.json` | da2de902 solution (before from-patch) |
| `continuity -3march/pipeline_da2de902/from_patch_payload.json` | Patch payload (trim + remove empty) |
| `continuity -3march/pipeline_da2de902/from_patch_output.json` | From-patch e5de3f5d (re-fetch when completed) |
| `continuity -3march/pipeline_da2de902/from_patch_route_plan_id.txt` | e5de3f5d-d235-4c6c-944b-01845827dbed |
| `continuity -3march/metrics_da2de902/` | metrics_report_da2de902.txt (before), metrics_report_e5de3f5d.txt (after; re-run when e5de3f5d completed) |
