# Source of truth: Schedule ↔ Timefold input ↔ Solution

**Sanningen = det vi skickar till Timefold som input.** That input is built deterministically from the schedule (in DB or as FSR JSON). One schedule gives one input; one schedule can have many solutions.

**Last updated**: 2026-03-14

---

## Concepts

| Concept | Meaning |
|--------|--------|
| **Schedule (DB)** | One schedule in the database: visits, employees, groups, dependencies, etc. Source for everything in the dashboard flow. |
| **Timefold input** | The JSON payload sent to the Timefold FSR API. Built by `buildTimefoldModelInput(scheduleId)` (dashboard) or by the script pipeline (CSV → FSR JSON). |
| **Solution** | One optimization run: one submission to Timefold, one result (assignments, score). Linked to a Schedule via `scheduleId` in the dashboard; in the script flow it is the output JSON. |

---

## Deterministic projection

For a **given** schedule (same visits, employees, groups, dependencies in DB), `buildTimefoldModelInput(scheduleId)` always produces the same input. The schedule does **not** “change” between submissions—if nothing in the DB has changed, the input is identical. If you edit visits, re-import, or change employees, the next build produces a different payload.

---

## One schedule → many solutions

One schedule can have **many** solutions (different optimization runs: different parameters, seeds, or simply multiple runs). You do **not** need multiple schedules in the DB to have multiple solutions.

- **Dashboard (beta-appcaire)**: `Schedule` 1 → N `Solution`. Each solution = one run, one Problem snapshot, one Timefold job.
- **Script (this repo)**: One FSR input file can be submitted multiple times; each run produces a different solution file (e.g. different job IDs, different continuity variants).

---

## Where this is implemented

- **Dashboard**: `buildTimefoldModelInput(scheduleId, jobName?, options?)` in beta-appcaire `apps/dashboard-server/src/services/timefold/projection/buildTimefoldModelInput.ts`. Called on `startOptimization` (full build) and `finalizeScheduleUpload` (count-only after import).
- **Script**: FSR JSON is produced by `scripts/conversion/csv_to_fsr.py`; submission by `scripts/timefold/submission/submit_solve.py` (or equivalent). No DB; the input file is the source of truth for that run.

See also: [02-csv-upload-dashboard.md](./02-csv-upload-dashboard.md), [03-script-flow.md](./03-script-flow.md), [04-e2e-to-solution.md](./04-e2e-to-solution.md).
