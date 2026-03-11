# Compare dashboard (seed) vs script FSR inputs

Same source CSV and same planning window so the two Timefold inputs can be compared.

## Source

- **CSV:** `huddinge-81-clients-with-coords.csv` (81 clients, 614 rows, 2-week expansion)
- **Planning window:** 2026-03-02 (Monday) to 2026-03-15 (14 days)

## 1. Reseed dashboard (beta-appcaire)

```bash
cd /path/to/beta-appcaire
ATTENDO_CSV_PATH=/path/to/be-agent-service/.../10-mars-new-attendo/huddinge-81-clients-with-coords.csv \
ATTENDO_SCHEDULE_START_DATE=2026-03-02 \
yarn workspace dashboard-server db:seed:attendo:reset
```

Clients without Lat/Lon in the CSV (e.g. HN02, HN07) get office coordinates as fallback so the seed completes.

## 2. Dump dashboard FSR

```bash
cd /path/to/beta-appcaire
E2E_DUMP_JSON=/path/to/be-agent-service/.../10-mars-new-attendo/dashboard_fsr.json \
yarn workspace dashboard-server e2e:timefold
```

This builds the FSR from the seeded DB (buildTimefoldModelInput) and writes the full request to `dashboard_fsr.json`.

## 3. Run script pipeline (be-agent-service)

```bash
cd be-agent-service/recurring-visits/huddinge-package/huddinge-4mars-csv/scripts
python3 attendo_4mars_to_fsr.py \
  "../full-csv/10-mars-new-attendo/huddinge-81-clients-with-coords.csv" \
  -o "../full-csv/10-mars-new-attendo/script_fsr_no_extra_vehicles.json" \
  --start-date 2026-03-02 --end-date 2026-03-15 \
  --no-geocode --no-supplementary-vehicles
```

Use `--no-supplementary-vehicles` so vehicle count is comparable to the seed (Slinga-only).

## 4. Compare

```bash
cd be-agent-service/.../10-mars-new-attendo
python3 compare_fsr_inputs.py
```

Optionally:

```bash
python3 compare_fsr_inputs.py --dashboard dashboard_fsr.json --script script_fsr_no_extra_vehicles.json
```

The script prints:

- **Counts:** total visits, visit groups, vehicles, shifts (dashboard vs script)
- **Time window check:** dashboard visits whose time window is smaller than service duration (would trigger Timefold warnings)
- **Planning window:** start/end for both

## Expected differences

| Metric        | Dashboard | Script | Note |
|---------------|-----------|--------|------|
| Vehicles      | 40        | 39     | Seed may have one more Slinga mapping. |
| Shifts        | 366       | 446    | Different shift/break rules (Dag/Helg/Kväll). |
| Visit groups  | 162       | 152    | Different grouping (Dubbel) or dedup. |
| Total visits  | ~3709     | ~3744  | Script drops 2 with no coords; seed keeps them (office fallback). |

**Time window parity:** The platform projection (`resolveVisitTimeWindows` + `buildTimefoldVisitFromDbVisit`) now ensures every emitted time window has span ≥ visit duration via `ensureTimeWindowMinDuration`. So the “14 dashboard visits” with narrow windows are fixed: seed/CSV → FSR matches the script and the solution flow does not fail on Timefold warnings.
