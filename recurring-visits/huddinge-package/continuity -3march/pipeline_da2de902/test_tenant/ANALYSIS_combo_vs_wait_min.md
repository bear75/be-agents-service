# Test tenant: Combo vs Wait-min (da2de902 variants)

Fetched and compared the two completed runs (same input: 3334 visits, 42 vehicles, 412 shifts).

## Summary

| Run        | Route plan ID     | Config                          | Score (hard/medium/soft)     | Unassigned | Assigned stops |
|-----------|-------------------|----------------------------------|-----------------------------|------------|----------------|
| **Combo** | 8e07450d-69e1-... | preferredVehicles weight 2 + minimizeWaitingTime weight 3 | 0hard / **-60000** medium / **16769506** soft | **6**  | 3894 |
| **Wait-min** | a4be8810-7812-... | minimizeWaitingTime weight 3 only (requiredVehicles kept) | 0hard / **-940000** medium / **-3986611** soft | **94** | 3806 |

## Findings

1. **Combo assigns many more visits.** Combo has 6 unassigned vs 94 for wait-min. So combining preferredVehicles (soft continuity) with wait-min achieves far better feasibility: the solver can assign outside the pool when needed (preferredVehicles) while still being guided toward continuity and lower wait.

2. **Wait-min alone leaves 94 visits unassigned.** With requiredVehicles (hard pool of 15 per client), the solver could not place 94 visits within their pools; the wait-min objective does not help if the constraint set is too tight.

3. **Medium score:** Wait-min has a much better (more negative) medium score (-940000 vs -60000), which likely reflects “minimize waiting time” — so when it can assign, it minimizes wait more. But the trade-off is 88 fewer visits assigned.

4. **Recommendation:** For this dataset, **combo (preferred + wait-min)** is the better choice: only 6 unassigned and a feasible plan. Use combo for the one-busy-day → full 2-week flow.

## One-busy-day run (78028dd1) — fix applied

That run failed because the one-day subset kept visits whose `requiredVehicles` referenced vehicles not on the day (e.g. weekend-only Helg_*). The script `build_one_busy_day_input.py` was updated to use **preferredVehicles only** for the one-day input: any `requiredVehicles` from the full input are merged into `preferredVehicles` (intersected with vehicles on the day), and `requiredVehicles` is never written. That way the busy-day solve is soft on continuity and the optimizer can balance efficiency vs continuity; `requiredVehicles` would be a hard constraint and force travel/wait regardless of config.

**To re-run the one-busy-day solve:**

```bash
# Rebuilt one-day input (already written)
# huddinge-package/continuity -3march/pipeline_da2de902/test_tenant/input_one_day_2026-02-16.json

python3 scripts/submit_to_timefold.py solve "huddinge-package/continuity -3march/pipeline_da2de902/test_tenant/input_one_day_2026-02-16.json" \
  --api-key "tf_p_96b5507b-57be-4ab6-b0a6-08a9d3372938" --configuration-id "" --no-register-darwin
```

Then use the new route plan’s output to extract client→vehicle and patch the full 2-week input for a fresh solve.

---

## From-patch status

**We do not have from-patch for any of the 3 strategies yet.** All three (preferred 688faece, wait-min a4be8810, combo 8e07450d) are **fresh solves** only. To get trimmed/from-patch:

1. Pick a base run (recommended: **combo** 8e07450d — best feasibility, 6 unassigned).
2. Build trimmed input (trim-to-visit-span: drop empty shifts, trim shift windows to first visit start → last visit end). Use `build_trimmed_input.py` or the workflow in `run_fetch_trim_patch_fetch_unmetrics.py`.
3. Submit from-patch to that route plan (or submit trimmed input as a new solve if from-patch is not available on test tenant).
4. Fetch the from-patch solution and run metrics with `--exclude-inactive`, and run `continuity_report.py` for continuity CSV.

Repeat for the other two strategies if you want comparable from-patch metrics (preferred, wait-min).

---

## Next steps for fine-tuning

1. **From-patch for combo (and optionally preferred/wait-min)** — Trim empty shifts, run from-patch (or trimmed solve), then metrics + continuity. Validates efficiency and continuity after trim.
2. **Generate continuity for current runs** — Run `continuity_report.py` for combo and wait-min outputs so we have per-client distinct-caregiver counts (target ≤15). See test_tenant README.
3. **One-busy-day → full 2-week** — Resubmit the fixed one-day input (preferredVehicles only), fetch output, extract client→vehicle from itineraries, patch full da2de902 with those preferredVehicles, solve full 2-week with combo weights.
4. **Larger pool (25)** — Rebuild input with `--continuity-max-per-client 25` (same base as da2de902), submit to test tenant, compare unassigned and efficiency vs pool 15.
5. **Weight tuning** — Try different `preferVisitVehicleMatchPreferredVehiclesWeight` and `minimizeWaitingTimeWeight` (e.g. 1 vs 2 vs 3) on combo input; compare scores and metrics.
6. **Preferred-only run (688faece)** — Fetch and run metrics for the preferred variant when complete, so all 3 strategies have efficiency (and optionally continuity) for comparison.
