# Seed data for scheduling generation TDD

Fixtures for connecting **resources** (from Attendo CSV) to **scheduling generation** (Timefold FSR input/output).

## Files in seed-data folder

Seed data files live in `apps/dashboard-server/src/seed-scripts/seed-data/` (CSV/JSON only; all docs live under `docs/` per repo rules).

| File                                          | Purpose                                                                                                                                                                                                                      |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Huddinge-v3 - Data-substitute-locations.csv` | **Default seed CSV** for `yarn db:seed:attendo`. V3 schema with **Lat,Lon** (substitute coordinates, not real Attendo locations). No anonymization of address text. Source: be-agent-service v3 substitute_locations_csv.py. |
| `Huddinge-v3 - Data-anonymized.csv`           | Anonymized v3 CSV (Adress N, 14xxx, Anonym ort). No Lat/Lon; use `ATTENDO_CSV_PATH` to a geocoded or substitute CSV if seeding without override.                                                                             |
| `attendo-huddinge.csv`                        | Smaller Attendo CSV (same schema). Use `ATTENDO_CSV_PATH` to point to it if needed.                                                                                                                                          |
| `fsr_balanced_46v_448s_input.json`            | **Expected FSR input** for TDD: 46 vehicles, 448 shifts, 3457 visits, 116 groups, 2 dusch-after-morgon (PT0M) deps. Use when testing "CSV/resources → FSR input" or "schedule generation" flows.                             |

## Script that builds JSON from CSV

The converter **CSV → FSR JSON** lives in **be-agent-service** (Python):

- **Path:** `be-agent-service/recurring-visits/huddinge-package/huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py`
- **Usage (from that repo):**
  ```bash
  cd be-agent-service/recurring-visits/huddinge-package/huddinge-4mars-csv/scripts
  python3 attendo_4mars_to_fsr.py ../full-csv/ATTENDO_DATABEHOV_ALL_81_CLIENTS.csv -o out.json \
    --start-date 2026-03-02 --end-date 2026-03-15 --no-geocode --no-supplementary-vehicles
  ```
- **Balanced input:** The file `fsr_balanced_46v_448s_input.json` was produced by that script (visits + visitGroups) plus **vehicles from** the cece06c0 baseline (46v, 448 shifts). So "full" pipeline run + vehicle merge; see `be-agent-service/.../full-csv/9march/shower-compare/README.md`.

## TDD use

- **Given** `Huddinge-v3 - Data-substitute-locations.csv` (default) or DB seeded from it via `yarn db:seed:attendo`, **when** we build FSR input for scheduling, **then** the result should match (or be subset-equivalent to) expected FSR structure. The default CSV has Lat/Lon so seed runs without `ATTENDO_CSV_PATH`.
- CSV upload accepts CSVs with or without Lat/Lon; missing coordinates are stored as null. Seed requires Lat/Lon in the default CSV (substitute-locations has them).
