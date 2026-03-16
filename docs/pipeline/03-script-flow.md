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

## Time windows only (no "pinned" in TF input)

Timefold FSR has **no** "pinned" or "fixed day" field. The solver only uses **time windows** on each visit: one TW = single day (non-movable); multiple TWs = multi-day (movable). "Pinned" vs "flexible" in our code is internal shorthand for how we build those TWs.

---

## Movable (multi-TW) visits

**Definition**: A visit is “movable” when it has **more than one time window** (solver can place it on different days). Script and dashboard both use this meaning.

- **Script**: `flexible_day` → multiple TWs; else one TW per occurrence. Huddinge v3 (2-week): ~397 movable, ~3520 visits, 152 groups. The script should create at least as many visits and groups as the dashboard (align expansion and grouping).
- **Dashboard**: Same rule: templates with partial weekdays, biweekly, or “Varje vecka” with no days → flexible (multi-TW); daily or full weekday/weekend set → pinned (single-TW). Counts can differ from the script if CSV/date range or recurrence parsing differ (e.g. day names, empty “Varje vecka” handling).

To compare: run `./scripts/compare-script-vs-dashboard-fsr.sh` (be-agent-service), then `yarn workspace dashboard-server dump-fsr` (beta-appcaire); if dashboard movable is much lower (e.g. 157 vs 397), the gap is in CSV→DB recurrence or classification—align import/projection with the script.

---

## Script locations and CSV notes

**Canonical script**: `scripts/conversion/csv_to_fsr.py` (single source for CSV→FSR in this repo).

**Older copy**: `recurring-visits/huddinge-package/huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py` — same logic, historically had (1) typo `når_på_dagen` instead of `när_på_dagen` (CSV column is "När på dagen"), (2) visit group key `dubbel_date_iso` so different clients with the same Dubbel and date were merged into one group. Both are fixed in that file to match the canonical script: `när_på_dagen`, group key `kundnr_date_iso_dubbel`. Prefer the canonical script for new runs.

**CSV (Huddinge v3 Data_final.csv)**:
- **Coordinates**: All 664 rows have Lat/Lon. No visits are dropped for missing coords when using this file with `--no-geocode`. Fallback to office coords in the script is for other CSVs or when geocoding fails.
- **Återkommande**: The column contains "Varje vecka, weekdays" in many rows (e.g. "Varje vecka, mån tis ons tor fre", "Varje vecka, lör sön", "Varje vecka, mån"). In Data_final.csv there is no "Varje vecka" only (no weekdays); every row has weekdays after the comma. Recurrence parsing uses this column.
- **Dubbel / visit groups**: One group per (client, date, Dubbel). If the CSV has different clients with the same Dubbel id, that is a data issue; the script does not merge across clients (group key includes kundnr).

---

## Relation to dashboard flow

- **Script flow**: No DB. CSV and FSR JSON are the source of truth for that run. Counts can differ from the dashboard because recurrence, grouping, and dependency logic may differ.
- **Dashboard flow**: DB is the source; projection is in beta-appcaire. Same schedule in DB always yields the same input (deterministic).
- For **matching** script output to dashboard/input, align conversion logic (expansion, groups, dependencies) with `buildTimefoldModelInput` where possible; use `facit.json` for prototype verification.

See [01-source-of-truth.md](./01-source-of-truth.md), [04-e2e-to-solution.md](./04-e2e-to-solution.md), [TIMEFOLD_PIPELINE_GUIDE.md](../TIMEFOLD_PIPELINE_GUIDE.md).
