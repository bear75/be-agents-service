# E2E flow: from CSV or dashboard to solution

End-to-end path from data (CSV or dashboard upload) to an optimized schedule (Timefold solution). Covers both the dashboard flow and the script flow, then metrics and continuity.

**Last updated**: 2026-03-14

---

## Two entry points

| Entry point | Path | Outcome |
|------------|------|--------|
| **Dashboard** | CSV upload → DB (Schedule) → Start optimization → Timefold → Solution stored in DB (Solution linked to Schedule). | One Schedule, one or more Solutions. Input = output of `buildTimefoldModelInput(scheduleId)`. |
| **Script** | CSV → `csv_to_fsr.py` → FSR JSON → submit to Timefold → solution JSON (and optional metrics/continuity). | No DB; input JSON and solution JSON are the artifacts. |

---

## Dashboard E2E (beta-appcaire)

1. User uploads CSV in dashboard (parse + validate + finalize).
2. Schedule and visits (and employees, groups, etc.) are created in DB.
3. Projection runs in count-only mode; dashboard shows counts that match what will be sent to Timefold.
4. User opens schedule detail and clicks “Start optimization”.
5. Server builds full FSR via `buildTimefoldModelInput(scheduleId, jobName)`, submits to Timefold, creates Problem + Solution records.
6. Webhook or polling can update Solution status and store result; UI shows solutions for that schedule.

One schedule → many solutions (e.g. different runs or parameters). No extra schedules needed.

---

## Script E2E (be-agent-service)

1. **Convert**: `python3 scripts/conversion/csv_to_fsr.py "<path>/Data_final.csv" -o input.json --start-date 2026-03-02 --weeks 2 --no-geocode` (and options as in [TIMEFOLD_PIPELINE_GUIDE.md](../TIMEFOLD_PIPELINE_GUIDE.md)).
2. **Submit**: Submit `input.json` to Timefold (e.g. `submit_solve.py solve input.json --wait --save output_dir`).
3. **Solution**: Solution JSON is saved under `output_dir/`.
4. **Metrics**: Run metrics and continuity scripts on input + solution (e.g. `metrics.py`, `continuity_report.py`).
5. **Optional continuity**: Build pools from baseline solution, patch input with `requiredVehicles`, re-submit; compare variants (pool3/pool5/pool8).

See [03-script-flow.md](./03-script-flow.md) and [TIMEFOLD_PIPELINE_GUIDE.md](../TIMEFOLD_PIPELINE_GUIDE.md) for commands and file locations.

---

## Summary

- **Dashboard**: CSV → DB → projection (count-only then full) → Timefold → Solution in DB. Single source of truth = what we send to Timefold; that input is built deterministically from the schedule.
- **Script**: CSV → FSR JSON → Timefold → solution JSON (+ optional metrics/continuity). Source of truth for that run = the FSR input file.
- **One schedule, many solutions**: In both flows, you can produce multiple solutions (e.g. different runs or continuity variants) without creating multiple schedules (dashboard) or multiple “schemas” (script); only the solution artifacts differ.

See [01-source-of-truth.md](./01-source-of-truth.md), [02-csv-upload-dashboard.md](./02-csv-upload-dashboard.md), [03-script-flow.md](./03-script-flow.md).
