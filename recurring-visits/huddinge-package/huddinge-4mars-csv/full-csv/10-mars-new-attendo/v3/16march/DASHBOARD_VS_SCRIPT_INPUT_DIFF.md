# Dashboard vs Script FSR Input (16 March)

Comparison of the two FSR input JSON files in `16march/`:

| File | Source | Planning window | Visits | Vehicles | visitGroups |
|------|--------|------------------|--------|----------|-------------|
| **pilot-export-...-input.json** | Dashboard (Caire export) | 2026-03-16 → 2026-03-29 | 3,514 | 41 | 162 |
| **script-export-...-input.json** | Script (`csv_to_fsr.py`) | 2026-03-09 → 2026-03-22 | 3,802 | 41 | 162 |

## Differences

1. **Planning window**
   - **Dashboard:** 2026-03-16 to 2026-03-29 (2 weeks; matches “pilot” run name).
   - **Script:** 2026-03-09 to 2026-03-22 (different 2 weeks; matches script default/args).

2. **Visit count**
   - Dashboard has **288 fewer visits** (3,514 vs 3,802). Causes:
     - Different date range (different days in the horizon).
     - Possible differences in recurrence expansion or filtering (e.g. dashboard may exclude some visits or use a different window when building the model).

3. **Structure**
   - Both are valid FSR payloads: `config`, `modelInput` with `planningWindow`, `visits`, `visitGroups`, `vehicles`, `skills`, `tags`, `pinNextVisitDuringFreeze`.
   - Key order differs (vehicles first in dashboard, planningWindow/visits first in script); JSON key order does not affect Timefold.

4. **Config run name**
   - Dashboard: `"Optimization - Attendo Huddinge - 2026-03-16 to 2026-03-29"`.
   - Script: `"Optimization - Attendo Huddinge - 2026-03-09 to 2026-03-22"`.

5. **Identical**
   - Same vehicles (41), same visitGroups (162), same skills (1), same tags (0).
   - Visit shape (id, name, location, timeWindows, serviceDuration, priority, pinningRequested) is the same.

## When to use which

- **Dashboard export:** Use when you want to match exactly what the Caire dashboard sends to Timefold (same window and visit set as in the UI).
- **Script export:** Use when you want a reproducible pipeline from `Huddinge-v3 - Data_final.csv` with a chosen `--start-date` / `--end-date` (e.g. for research or parity with `compare-script-vs-dashboard-fsr.sh`).

To align script output with the dashboard window (16–29 March), run:

```bash
python3 scripts/conversion/csv_to_fsr.py "recurring-visits/.../v3/Huddinge-v3 - Data_final.csv" -o script_16_29.json \
  --start-date 2026-03-16 --end-date 2026-03-29 --no-geocode
```

Then compare visit/dependency counts with the dashboard export if needed.
