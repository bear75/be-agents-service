# Metrics and empty shifts – continuity runs (57b3a619, e77e9ea3)

## Where are the metrics from the solutions?

**For the March continuity runs (57b3a619, e77e9ea3):** there are **no metrics in the repo** yet. Those runs were submitted but the solutions were not fetched with `--metrics-dir`, so metrics were never generated.

**Where metrics usually live:**
- **Package root:** `huddinge-package/metrics/` (e.g. `metrics_report_5ff7929f.txt`, `metrics_*.json`)
- **Per-dataset:** `huddinge-package/huddinge-datasets/28-feb/<dataset_id>/metrics/` (e.g. `203cf1d6/metrics/`, `5ff7929f/metrics/`)
- **Per solve run:** `huddinge-package/solve/<folder>/metrics/` (e.g. `solve/24feb-tf-prod/metrics/`)

**How to get metrics for e77e9ea3 (or 57b3a619):**

From `be-agent-service/recurring-visits/scripts`:

```bash
# 1) Fetch solution and run metrics (saves output + input from API, then runs metrics into metrics dir)
TIMEFOLD_API_KEY=tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8 \
  python3 fetch_timefold_solution.py e77e9ea3-883f-4b1c-83f4-54f948b9e13f \
  --save ../huddinge-package/continuity\ -3march/e77e9ea3-output.json \
  --metrics-dir ../huddinge-package/continuity\ -3march/metrics
```

Or fetch without metrics, then run solve_report manually:

```bash
# Fetch only
python3 fetch_timefold_solution.py e77e9ea3-883f-4b1c-83f4-54f948b9e13f \
  --save ../huddinge-package/continuity\ -3march/e77e9ea3-output.json

# Then metrics + unassigned + empty-shifts report (input is saved next to output by fetch)
python3 solve_report.py ../huddinge-package/continuity\ -3march/e77e9ea3-output.json \
  --input ../huddinge-package/continuity\ -3march/input.json \
  --save ../huddinge-package/continuity\ -3march/metrics
```

See `beta-appcaire/.cursor/commands/fetchtimefoldsolution.md` for full fetch workflow.

---

## Were all empty shifts removed?

**No.** The continuity runs (57b3a619, e77e9ea3) were **fresh solves** (POST of modelInput with 42 vehicles, 412 shifts). We did **not** run a **from-patch** after them. So:

- **Input:** 412 shifts (same as base 5ff7929f; that’s already a trimmed capacity set).
- **Output:** The solver can still return some shifts with **no visits** (“empty shifts”). Those are only removed by a **from-patch** step: build a patch from the solution (pin visits, trim shift windows, remove empty shifts), then POST to `.../route-plans/{id}/from-patch`.

**To get 0 empty shifts:**

1. Fetch the solution (e.g. e77e9ea3).
2. Run `build_from_patch.py` on that output (with the same input) → produces a patch payload that removes empty shifts and trims to visit span.
3. Submit the patch: `submit_to_timefold.py from-patch <payload> --route-plan-id e77e9ea3-... --wait --save <new-output.json>`.
4. Fetch the new route plan and run metrics with `--exclude-inactive` (that run has 0 empty shifts by construction).

See `scripts/run_fetch_trim_patch_fetch_unmetrics.py` and `fetchtimefoldsolution.md` for the full fetch → trim → patch → fetch flow. Empty-shift count is reported by `solve_report.py` (and by `fetch_timefold_solution.py` when it runs metrics and then `run_analyze_metrics_frompatch.py` if empty shifts are detected).
