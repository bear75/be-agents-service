# Analysis summary: 81-client input (2w)

Run date: 2026-03-10 (script execution).

## Pre-step for dashboard seed / CSV upload (locations)

The Data CSV does not include Lat/Lon. To get coordinates into the dashboard (seed or upload), run the add-coordinates pre-step after building `address_coordinates.json`:

```bash
# From full-csv/ (be-agent-service/.../huddinge-4mars-csv/full-csv/)
cd full-csv
python3 add_coordinates_to_csv.py "10-mars-new-attendo/huddinge-81-clients - Data.csv" \
  --coordinates "10-mars-new-attendo/address_coordinates.json" \
  -o "10-mars-new-attendo/huddinge-81-clients-with-coords.csv"
```

Use the `-with-coords.csv` file for beta-appcaire seed or dashboard schedule import.

## Scripts run

All from `be-agent-service/recurring-visits/`:

1. **verify_all_visits_have_flex.py** — `input_81_10mars_2w.json`
2. **analyze_dependency_feasibility.py** — `input_81_10mars_2w.json --all -o dependency_feasibility_81_2w.json`
3. **map_visits_time_windows.py** — input + CSV → `map_visits_time_windows_81_2w.txt`
4. **analyze_4mars_csv_to_json.py** — CSV + input → `analyze_csv_to_json_81_2w.txt`

## Results

| Check | Result |
|-------|--------|
| **Flex** | OK: All **3746** visits have flex (time or day). |
| **Dependencies** | **145** dependencies analyzed: **0 infeasible**, **0 tight**, **145 OK**. |
| **CSV → JSON** | 614 CSV rows → 3746 occurrences; all visit_ids in JSON match expansion; Timefold format OK (timeWindows, location, serviceDuration). |
| **Time windows** | 3746 visits, 152 visit groups, 492 unique time-window patterns; report lists all patterns and examples. |

## Feasibility

- **Visits feasible:** Yes. Every visit has valid time windows, location, and service duration; all have flex.
- **Dependencies feasible:** Yes. Every `precedingVisit` + `minDelay` can be satisfied within the dependent visit’s latest start (prev_end + delay ≤ dep latest start); no infeasible or tight (< 15 min slack) pairs.

## Output files (this folder)

- `analyze_csv_to_json_81_2w.txt` — CSV/JSON consistency and per-row counts
- `map_visits_time_windows_81_2w.txt` — Time-window patterns, groups, dependencies
- `dependency_feasibility_81_2w.json` — Per-dependency status (ok/infeasible/tight) and slack

## Related

- **address_coordinates.json** — Built by `build_address_coordinates.py`; used by FSR input and by `add_coordinates_to_csv.py` to produce a CSV with Lat/Lon for seed/upload.
