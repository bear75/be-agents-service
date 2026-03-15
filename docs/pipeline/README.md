# Pipeline documentation: CSV, dashboard, script, and e2e to solution

This folder documents the scheduling pipeline from data source to Timefold solution, including where "the truth" lives and how the different flows (dashboard vs script) relate.

**Last updated**: 2026-03-14

---

## Contents

| Doc | Description |
|-----|-------------|
| [01-source-of-truth.md](./01-source-of-truth.md) | **Schedule ↔ Timefold input ↔ Solution**: single source of truth; one schedule → one input; one schedule → many solutions. |
| [02-csv-upload-dashboard.md](./02-csv-upload-dashboard.md) | **CSV upload via dashboard**: beta-appcaire flow (upload CSV → DB → projection → counts; optional start optimization). |
| [03-script-flow.md](./03-script-flow.md) | **Script flow**: be-agent-service CSV → FSR JSON → Timefold API (no DB; prototype/research). |
| [04-e2e-to-solution.md](./04-e2e-to-solution.md) | **E2E to solution**: full path from CSV or dashboard to optimized schedule (both flows, then metrics and continuity). |

---

## Quick reference

- **Production (dashboard)**: CSV → upload to beta-appcaire → Schedule in DB → `buildTimefoldModelInput` → Timefold → Solution. See [02-csv-upload-dashboard.md](./02-csv-upload-dashboard.md) and [04-e2e-to-solution.md](./04-e2e-to-solution.md).
- **Prototype (script)**: CSV → `scripts/conversion/csv_to_fsr.py` → FSR JSON → submit to Timefold → solution. See [03-script-flow.md](./03-script-flow.md) and [TIMEFOLD_PIPELINE_GUIDE.md](../TIMEFOLD_PIPELINE_GUIDE.md).
- **Source of truth**: What we send to Timefold as input. That input is built deterministically from the schedule in DB (dashboard) or from the script’s FSR JSON. One schedule in DB = same input every time until the schedule changes. One schedule → many solutions. See [01-source-of-truth.md](./01-source-of-truth.md).

Related top-level docs: [PIPELINE_SOURCE.md](../PIPELINE_SOURCE.md), [TIMEFOLD_PIPELINE_GUIDE.md](../TIMEFOLD_PIPELINE_GUIDE.md).
