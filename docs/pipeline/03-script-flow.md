# Script flow: CSV → FSR JSON → Timefold

Flow in this repo (be-agent-service): CSV file → Python conversion to FSR JSON → submit to Timefold API → fetch solution. No database; the input JSON and solution JSON are the artifacts.

**Last updated**: 2026-03-14

---

## Overview

1. **CSV → FSR JSON**  
   `scripts/conversion/csv_to_fsr.py` (or under `scripts/timefold/conversion/` if present).  
   Input: Attendo-style CSV (e.g. Huddinge v3).  
   Output: FSR JSON (visits, vehicles, visitGroups, dependencies, time windows). Optionally writes `facit.json` next to the CSV with expected counts from expansion.

2. **Submit solve**  
   Submit the FSR JSON to the Timefold API (e.g. `scripts/timefold/submission/submit_solve.py` or equivalent). Get a route plan ID.

3. **Wait / poll**  
   Poll until status is COMPLETED (or FAILED).

4. **Fetch solution**  
   Download the solution JSON (e.g. `scripts/timefold/submission/fetch_solution.py`).

5. **Optional: metrics and continuity**  
   Run metrics and continuity scripts on the solution; optionally build continuity pools, patch input with `requiredVehicles`, and re-solve.

---

## Where it lives

- **Repo**: be-agent-service.
- **Conversion**: `scripts/conversion/csv_to_fsr.py` (writes `facit.json` next to CSV).
- **Submission / fetch**: See `scripts/timefold/` (or as documented in [TIMEFOLD_PIPELINE_GUIDE.md](../TIMEFOLD_PIPELINE_GUIDE.md) and [PIPELINE_SOURCE.md](../PIPELINE_SOURCE.md)).
- **Data**: e.g. `recurring-visits/huddinge-package/.../v3/` for Huddinge v3 CSV and outputs.

---

## Relation to dashboard flow

- **Script flow**: No DB. CSV and FSR JSON are the source of truth for that run. Counts can differ from the dashboard because recurrence, grouping, and dependency logic may differ.
- **Dashboard flow**: DB is the source; projection is in beta-appcaire. Same schedule in DB always yields the same input (deterministic).
- For **matching** script output to dashboard/input, align conversion logic (expansion, groups, dependencies) with `buildTimefoldModelInput` where possible; use `facit.json` for prototype verification.

See [01-source-of-truth.md](./01-source-of-truth.md), [04-e2e-to-solution.md](./04-e2e-to-solution.md), [TIMEFOLD_PIPELINE_GUIDE.md](../TIMEFOLD_PIPELINE_GUIDE.md).
