# Huddinge Recurring Visits Pipeline

Self-contained package for converting Huddinge recurring visit data to Timefold Field Service Routing (FSR) input and running optimizations. **Nova** uses the same pipeline pattern: see [../nova/README.md](../nova/README.md) and `process_nova.py` with `nova/scripts/expand_nova_recurring_visits.py`; both use these scripts for JSON, solve, from-patch, and metrics.

**Full pipeline:** Source CSV → Expanded CSV → **Input JSON** → Solve → Output JSON → Metrics → From-Patch (remove inactive) → Final Metrics

**First priority is 0 unassigned.** From-patch only trims empty/inactive shifts; it does not add capacity. If the solve has unassigned visits, **update the input** (step 1 or 2) with the shifts required (e.g. add evening vehicles or shifts in source CSV), then regenerate input and solve again. Only after 0 unassigned (and optionally 0 empty) run from-patch and then metrics for efficiency.

**Priorities & validation:** See [docs/PRIORITIES.md](docs/PRIORITIES.md) for input correctness, config profiles, demand/supply rebalancing, and metrics accuracy.

**Viewing on schedule page:** See [docs/PLATFORM_UPLOAD.md](docs/PLATFORM_UPLOAD.md) for output locations and how to use results for Caire platform visualization.

## Context & Goals

### Goal order (mandatory first, then optimize)

Visits are **mandatory**. Metrics are only relevant once the solution is feasible.

| Priority | Goal                     | Description                                                                                                                                                                                                         |
| -------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1**    | **0 unassigned**         | Every visit must be assigned. **Update the input** (step 1 or 2): add the shifts required (e.g. `add_evening_vehicles.py` or more shifts in source CSV), regenerate input, solve. From-patch does not add capacity. |
| **2**    | **0 empty shifts**       | No shift without visits. After 0 unassigned, use from-patch to trim empty shifts, or tune config so the solver doesn’t leave shifts empty.                                                                          |
| **3**    | **Metrics & efficiency** | Only after 1 and 2: run metrics and aim for **field efficiency > 67.5%** (Slingor benchmark). Test different Timefold configs to see how they affect efficiency.                                                    |

**Metrics from runs with unassigned visits or empty shifts are not valid for benchmarking.** First reach 0 unassigned and 0 empty shifts, then compare efficiency across configs.

### Optimization objective (once feasible)

Improve the care visit schedule by:

| Goal                       | Description                                                         |
| -------------------------- | ------------------------------------------------------------------- |
| **Minimize travel & wait** | Reduce driving and waiting so more time is spent at clients         |
| **Maximize visit time**    | Maximize time at client (care delivery) relative to shift duration  |
| **Remove idle time**       | Minimize empty shift time (travel to depot, gaps) — already 0 empty |

### Benchmark

**Manual planners achieve 67.5% efficiency** using Slingor. The Timefold solver must **beat this benchmark** to justify adoption.

Efficiency is measured as **field efficiency** = visit / (visit + travel): the share of field time spent at the client. Higher values mean less driving, less waiting, more care delivery. **Tune Timefold config** (weights, duration, constraints) and re-solve to see how config changes affect metrics.

### Two locations (service area + break)

The pipeline supports **two locations** per shift in the source CSV:

| Location        | CSV columns (Huddinge)     | Nova columns        | Use |
|----------------|----------------------------|---------------------|-----|
| **Service area** | `serviceArea_lat`, `serviceArea_lon` | `office_lat`, `office_lon` | Depot / shift start and end. |
| **Break location** | `break_lat`, `break_lon` (optional) | `slinga_break_lat`, `slinga_break_lon` (optional) | Where the break is taken; Timefold schedules travel to/from it. |

If `break_lat`/`break_lon` are missing or zero, **service area is used as the break location** (Huddinge/Nova placeholder). So existing source CSVs without break columns keep current behaviour (break at service area).

### Time equation

```
shift = visit + travel + wait + break + idle
```

- **visit**: Time at client (care delivery) — maximize
- **travel**: Driving between locations — minimize
- **wait**: Waiting for time windows — minimize
- **break**: Required rest — fixed
- **idle**: Empty shift time (unassigned) — eliminate

## File Naming: Timestamps

All **generated** files use timestamps (`YYYYMMDD_HHMMSS`) so you can identify which run produced them and compare runs.

| Layer                  | Has Timestamp       | Example                                              |
| ---------------------- | ------------------- | ---------------------------------------------------- |
| **Source**             | No (upstream input) | `source/Huddinge_recurring_v2.csv`                   |
| **Expanded CSV**       | Yes                 | `expanded/huddinge_2wk_expanded_20260213_194425.csv` |
| **Input JSON**         | Yes                 | `solve/input_20260213_194425.json`                   |
| **Output JSON**        | Yes                 | `solve/output_20260213_194425.json`                  |
| **From-patch payload** | Yes                 | `from-patch/payload_20260213_194425.json`            |
| **Metrics**            | Yes                 | `metrics/metrics_20260213_194425_<route_id>.json`    |

Only timestamped files from the current pipeline run are valid for downstream steps. Remove or archive old timestamped files when regenerating.

## Folder Structure

```
huddinge-package/
├── README.md                 # This file
├── process_huddinge.py       # Main pipeline orchestrator
│
├── source/                   # Source data (no timestamp)
│   └── Huddinge_recurring_v2.csv
│
├── expanded/                 # Expanded visit occurrences (timestamped)
│   └── huddinge_2wk_expanded_YYYYMMDD_HHMMSS.csv
│
├── solve/                    # Timefold FSR input/output (timestamped)
│   ├── input_YYYYMMDD_HHMMSS.json
│   └── output_YYYYMMDD_HHMMSS.json
│
├── from-patch/               # ESS: remove inactive shifts (timestamped)
│   ├── payload_YYYYMMDD_HHMMSS.json
│   └── output_YYYYMMDD_HHMMSS.json
│
├── metrics/                  # Efficiency metrics (timestamped)
│   ├── metrics_YYYYMMDD_HHMMSS_<route_id>.json
│   └── metrics_report_<route_id>.txt   # Full report (staffing, field, wait efficiency, time equation)
│
└── scripts/
    ├── calculate_time_windows.py
    ├── expand_recurring_visits.py
    ├── generate_employees.py
    ├── csv_to_timefold_fsr.py
    ├── submit_to_timefold.py
    ├── metrics.py
    ├── solve_report.py      # Combined: metrics + unassigned + empty-shifts
    ├── build_from_patch.py
    ├── add_monday_shifts.py   # Add extra Monday vehicles (optional)
    ├── add_evening_vehicles.py # Add extra evening vehicles (optional)
    ├── validate_pre_solve.sh   # Run all pre-solve checks
    ├── validate_source_visit_groups.py
    ├── validate_visit_groups.py
    └── analyze_empty_shifts.py
```

## Pipeline Overview

```
Source CSV  →  Expanded CSV  →  Input JSON  →  Solve  →  Output JSON
     ↓              ↓                ↓                      ↓
  (no ts)     (timestamped)    (timestamped)          (timestamped)
                                                           ↓
                                                    Metrics  →  from-patch  →  Final metrics
```

### Steps 1–3: CSV → JSON → Solve

| Step      | Input                              | Output                                               |
| --------- | ---------------------------------- | ---------------------------------------------------- |
| 1. Expand | `source/Huddinge_recurring_v2.csv` | `expanded/huddinge_2wk_expanded_YYYYMMDD_HHMMSS.csv` |
| 2. JSON   | Expanded CSV + Source CSV          | `solve/input_YYYYMMDD_HHMMSS.json`                   |
| 3. Solve  | Input JSON                         | `solve/output_YYYYMMDD_HHMMSS.json`                  |

### Step 4: Metrics

Calculate efficiency from the solve output: visit time, travel, wait, inactive time, routing efficiency %.

### Steps 5–6: From-Patch (ESS — remove inactive shifts)

1. **Pin** all assigned visits
2. **End shifts at depot** (remove idle time)
3. **Remove** empty shifts and empty vehicles
4. **Re-solve** with leaner fleet

**From-patch does not change wait time.** It only trims structure (idle, empty shifts/vehicles) and pins visits. Wait = `startServiceTime − arrivalTime` per visit; those times come from the **base solve** and are preserved. So if you see higher wait in one run than another (e.g. 5.9% vs 0.3%), the difference is from the **base solve** (input or solver config), not from from-patch. To reduce wait, tune the base solve (e.g. penalize wait in Timefold config) or relax time windows; week-day separation in expansion can also increase wait by tightening day-specific windows.

### Step 7: Final Metrics (ESS mode)

Metrics with `--exclude-inactive` to measure efficiency without inactive time in the denominator.

## Full rerun (after archiving)

1. Move old files into `expanded/archive/`, `solve/archive/`, `from-patch/archive/`, `metrics/archive/` (see archive READMEs).
2. From package root: `python3 process_huddinge.py --weeks 2` → new `expanded/huddinge_2wk_expanded_<ts>.csv` and `solve/input_<ts>.json`.
3. From appcaire root: solve (requires `TIMEFOLD_API_KEY`), then metrics, then from-patch if desired:
   ```bash
   pnpm timefold submit_to_timefold.py solve solve/input_<ts>.json --wait --save solve/output_<ts>.json
   pnpm timefold solve_report.py solve/output_<ts>.json --input solve/input_<ts>.json --save metrics/
   ```
4. Use `analyze_unassigned.py` output to decide: add shifts (supply) or tune Timefold config (config); aim visit:travel high, then add placeholder shifts for required demand.

## How to Run

### Prerequisites

- Python 3.10+
- `requests` (`pip install requests`)
- `TIMEFOLD_API_KEY` environment variable

### Regenerate pipeline output

```bash
# From package root (huddinge-package/)
python3 process_huddinge.py --weeks 2

# Or 4 weeks
python3 process_huddinge.py --weeks 4

# Custom start date
python3 process_huddinge.py --weeks 2 --start-date 2026-03-02
```

Creates timestamped: `expanded/huddinge_2wk_expanded_*.csv`, `solve/input_*.json`

### From appcaire root (recommended)

Run any script without `cd`-ing into the package. Paths are relative to the package.

```bash
# From appcaire/ (repo root)
pnpm timefold submit_to_timefold.py solve solve/input_20260213_180452.json --wait --save solve/output.json

pnpm timefold build_from_patch.py --output solve/output_xxx.json --input solve/input_xxx.json --out from-patch/payload.json

pnpm timefold submit_to_timefold.py from-patch from-patch/payload_xxx.json --route-plan-id <id> --wait --save from-patch/output.json

pnpm timefold metrics.py solve/output_xxx.json --input solve/input_xxx.json --save metrics/
```

### From package scripts directory (legacy)

```bash
cd docs_2.0/huddinge-package/scripts

INPUT=$(ls -t ../solve/input_*.json 2>/dev/null | head -1)
python3 submit_to_timefold.py solve "$INPUT" --wait --save ../solve/output.json

OUTPUT=$(ls -t ../solve/output_*.json 2>/dev/null | head -1)
INPUT=$(ls -t ../solve/input_*.json 2>/dev/null | head -1)
python3 metrics.py "$OUTPUT" --input "$INPUT" --save ../metrics/

python3 build_from_patch.py --output "$OUTPUT" --input "$INPUT" --out ../from-patch/payload.json
PAYLOAD=$(ls -t ../from-patch/payload_*.json 2>/dev/null | head -1)
python3 submit_to_timefold.py from-patch "$PAYLOAD" --route-plan-id <id> --wait --save ../from-patch/output.json
```

### Continuity compare (submit all strategies in parallel)

From `huddinge-package/`, submit base + manual + area (+ optional first-run) to Timefold FSR in parallel for comparison.

```bash
cd huddinge-package

# Submit all 4 (base + manual + area + first-run) to prod in parallel
python3 run_continuity_compare.py \
  --expanded-csv expanded/huddinge_2wk_expanded_20260224_043456.csv \
  --weeks 2 --env prod \
  --first-run-output solve/24feb/trimmed/export-field-service-routing-fa713a0d-f4e7-4c56-a019-65f41042e336-output.json

# Only 3 strategies (no first-run) if you omit --first-run-output
python3 run_continuity_compare.py --expanded-csv expanded/huddinge_2wk_expanded_20260224_043456.csv --weeks 2 --env prod
```


## Script Roles

| Script                         | Input                     | Output                                         |
| ------------------------------ | ------------------------- | ---------------------------------------------- |
| `expand_recurring_visits`      | Source CSV                | Expanded CSV                                   |
| `generate_employees`           | Source CSV                | (in-memory vehicles/shifts; two locations: service area + optional `break_lat`/`break_lon`; if break location missing, service area used as placeholder) |
| `csv_to_timefold_fsr`          | Expanded CSV + Source CSV | Input JSON                                     |
| `submit_to_timefold`           | Input JSON or payload     | Output JSON                                    |
| `metrics`                      | Output JSON + Input JSON  | metrics/\*.json                                |
| `build_from_patch`             | Output JSON + Input JSON  | from-patch payload                             |
| `add_monday_shifts`            | Input JSON                | Input JSON with extra Monday vehicles          |
| `add_evening_vehicles`         | Input JSON                | Input JSON with extra evening vehicles         |
| `validate_source_visit_groups` | Source CSV                | stdout (OK/FAIL per group)                     |
| `validate_visit_groups`        | Input JSON                | stdout (OK/FAIL per group)                     |
| `solve_report`                 | Output JSON + Input JSON  | metrics + unassigned + empty-shifts (combined) |
| `run_continuity_compare`       | Expanded CSV (+ optional first-run output) | Submits base + manual + area (+ first-run) to FSR in parallel |
| `analyze_empty_shifts`         | Input JSON + Output JSON  | stdout                                         |
| `analyze_unassigned`           | Input JSON + Output JSON  | stdout (+ optional CSV)                        |

## Visit:travel first, then add shifts (placeholders)

1. **Maximize visit:travel ratio** (field efficiency) with the current fleet: tune Timefold config (reduce travel weight, distribute movable visits to day or evening so routing is more efficient). Optionally pin movable visits to a specific shift type (day vs evening) and add shifts only to that demand.
2. **Analyze:** Run `solve_report.py` for metrics, unassigned (supply vs config), and empty-shifts in one go.
3. **Add placeholder shifts** only for the required visit+travel demand: add shifts to the dates/periods (day or evening) where supply is short. Use `add_evening_vehicles.py` or `add_monday_shifts.py`, or add vehicles/shifts in source CSV for that demand.

## Data Summary (2-week run)

- **Source**: ~1,861 recurring rows (`Huddinge_recurring_v2.csv`)
- **Expanded**: 3,622 visit occurrences
- **Standalone visits**: 3,334
- **Visit groups**: 144 (288 visits, 2 per group; grouped by `visitGroup_id` + week + date)
- **Vehicles**: 38
- **Shifts**: 340

## Validation & Analysis Scripts

| Script                            | Purpose                                                                                                         |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `validate_source_visit_groups.py` | Validate source CSV: all `visitGroup_id` pairs have overlapping weekdays (occurence/recurring_external)         |
| `validate_visit_groups.py`        | Ensure all visits in each group have overlapping time windows in input JSON (required for multi-vehicle visits) |
| `solve_report.py`                 | **Combined:** metrics + unassigned analysis + empty-shifts analysis (one script, one load)                      |
| `analyze_empty_shifts.py`         | List empty shifts and check if they overlap with unassigned visit time windows                                  |
| `analyze_unassigned.py`           | Classify unassigned: supply (add shifts) vs config (tune solver); report visit:travel and by date/day/evening   |

```bash
./scripts/validate_pre_solve.sh   # Run all pre-solve checks
python3 scripts/validate_source_visit_groups.py source/Huddinge_recurring_v2.csv
python3 scripts/validate_visit_groups.py solve/input_*.json
# Combined: metrics + unassigned analysis + empty-shifts analysis
python3 scripts/solve_report.py solve/output_*.json --input solve/input_*.json --save ../metrics/
# Optional: export unassigned rows to CSV
python3 scripts/solve_report.py solve/output_*.json --input solve/input_*.json --save ../metrics/ --csv ../metrics/unassigned.csv
# Or run individually:
python3 scripts/analyze_empty_shifts.py solve/input_*.json solve/output_*.json
python3 scripts/analyze_unassigned.py solve/input_*.json solve/output_*.json --csv unassigned.csv
```

## Efficiency Definitions

- **Staffing efficiency** = visit / (shift − break). Includes inactive time in denominator.
- **Field efficiency** = visit / (visit + travel). Share of field time at client. **Target: >67.5%** (manual Slingor benchmark).
- **Time equation**: shift = visit + travel + wait + break + idle (inactive/empty shift time)
