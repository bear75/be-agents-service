# Nova Recurring Visits Pipeline

Same pattern as **Huddinge**: one entry point (`process_nova.py`), source → expanded CSV → Timefold FSR JSON. Uses `nova/scripts/expand_nova_recurring_visits.py` for step 1 and **`../huddinge-package/scripts/`** for JSON, solve, from-patch, and metrics.

**Full pipeline:** Source CSV → Expanded CSV → **Input JSON** → Solve → Output JSON → Metrics → From-Patch → Final Metrics

## Pipeline (recommended): one command

Use **`process_nova.py`** like Huddinge’s `process_huddinge.py`: expand + generate Timefold JSON (with break location from service area when break coords are missing).

```bash
cd docs_2.0/recurring-visits
python nova/process_nova.py --weeks 2
python nova/process_nova.py --weeks 4 --output-dir nova
```

- **nova/scripts/expand_nova_recurring_visits.py** — Maps Nova columns to Huddinge format and expands (calls Huddinge expand).
- **process_nova.py** — Runs expand → `csv_to_timefold_fsr` (from `huddinge-package/scripts/`) with `source_format=nova`. Shifts get break location from `office_lat`/`office_lon` (or optional `slinga_break_lat`/`slinga_break_lon`); see [Two locations](#two-locations-service-area--break) below.

## Two locations (service area + break)

Same behaviour as [Huddinge](../huddinge-package/README.md#two-locations-service-area--break): two locations per shift — **service area** (depot) and **break location**. Nova uses `office_lat`/`office_lon` for service area; optional `slinga_break_lat`/`slinga_break_lon` for break. If break coords are missing or zero, **service area is used as break location** (placeholder). Generated JSON includes break `location` so Timefold schedules travel to/from the break.

## Overview

**Planning Window**: 4 weeks (has monthly recurring visits)
**Data Quality**: ⚠️ Fair (94 missing coordinates, 10.8% of source)
**Organization**: Real production data from Nova organization

## Data Counts

| Stage            | Count            | Notes                                               |
| ---------------- | ---------------- | --------------------------------------------------- |
| **Source CSV**   | 867 visits       | `source/Nova_Final_Verified_geocoded.csv`           |
| **Expanded CSV** | 2,740 visits     | `expanded/nova_4wk_expanded.csv` (3.16x expansion)  |
| **JSON Input**   | 2,740 visits     | `solve/input.json` (2,536 solo + 204 in 102 groups) |
| **Filtered**     | ~290 occurrences | 81 source visits with missing address (9.3%)        |

## ⚠️ Geocoding Issues

**~~94~~ 81 visits (~~10.8%~~ 9.3%) filtered out due to missing coordinates:**

- 81 visits: Missing address entirely (empty `Gata` field) - **STILL NEED RESOLUTION**
- ~~13 visits~~: ✅ **RESOLVED** - Manually geocoded and included (Feb 12, 2026)

**Current coverage: 90.7%** (786 of 867 source visits)

See [`GEOCODING_ISSUES.md`](./GEOCODING_ISSUES.md) for details.

## Scripts (where they live)

| Location | Scripts |
| -------- | ------- |
| **`nova/scripts/`** | `expand_nova_recurring_visits.py` (Nova → Huddinge format + expand) |
| **`../huddinge-package/scripts/`** | `metrics.py`, `submit_to_timefold.py`, `build_from_patch.py`, `csv_to_timefold_fsr.py`, `expand_recurring_visits.py`, and the rest of the pipeline |
| **`../scripts/`** (recurring-visits root) | `fsr_metrics.py` (alternative metrics from output JSON), `anonymize_huddinge_to_demo.py` |

Use **`../huddinge-package/scripts/`** for solve, from-patch, and metrics when running steps manually.

## Folder Structure

```
nova/
├── scripts/
│   └── expand_nova_recurring_visits.py   # Nova → Huddinge format + expand
├── process_nova.py                        # Pipeline: expand → Timefold JSON
├── source/                                # Original source CSV
│   └── Nova_Final_Verified_geocoded.csv
├── expanded/                              # Expanded to planning window
│   └── nova_*wk_expanded_*.csv
├── solve/                                 # Timefold FSR
│   ├── input_*.json
│   └── output.json
├── from-patch/                            # ESS simulation (optional)
├── metrics/                               # Efficiency metrics (timestamped)
│   ├── metrics_YYYYMMDD_HHMMSS_<route_id>.json
│   └── metrics_report_<route_id>.txt      # Full report (staffing, field, wait efficiency, time equation)
├── GEOCODING_ISSUES.md
└── README.md
```

## Alternative (legacy) pipeline steps

If not using `process_nova.py`, run steps manually. All scripts below are in **`../huddinge-package/scripts/`** (run from `nova/` or use that path).

### 1. Expansion (Source → Expanded)

```bash
cd docs_2.0/recurring-visits/nova
python3 scripts/expand_nova_recurring_visits.py \
  source/Nova_Final_Verified_geocoded.csv \
  -o expanded/nova_4wk_expanded.csv \
  --weeks 4
# Or use process_nova.py which does expand + JSON.
```

### 2. JSON Generation (Expanded → Solve Input)

Use **Nova source** and **format** so vehicles and break location come from Nova columns (`office_lat`/`office_lon`, optional `slinga_break_*`):

```bash
python3 ../huddinge-package/scripts/csv_to_timefold_fsr.py \
  expanded/nova_4wk_expanded.csv \
  -o solve/input.json \
  --weeks 4 \
  --source source/Nova_Final_Verified_geocoded.csv \
  --format nova
```

### 3. Fresh Solve (Input → Output)

```bash
python3 ../huddinge-package/scripts/submit_to_timefold.py solve \
  solve/input.json \
  --wait \
  --save solve/output.json
```

### 4. From-Patch Payload (Remove Empty Shifts)

```bash
python3 ../huddinge-package/scripts/build_from_patch.py \
  --output solve/output.json \
  --input solve/input.json \
  --remove-empty-shifts \
  --out from-patch/payload.json
```

### 5. From-Patch Solve (ESS Simulation)

```bash
ROUTE_PLAN_ID=$(jq -r '.metadata.id' solve/output.json)

python3 ../huddinge-package/scripts/submit_to_timefold.py from-patch \
  from-patch/payload.json \
  --route-plan-id $ROUTE_PLAN_ID \
  --wait \
  --save from-patch/output.json
```

### 6. Calculate Metrics

```bash
python3 ../huddinge-package/scripts/metrics.py \
  from-patch/output.json \
  --input solve/input.json \
  --exclude-inactive \
  --save metrics/
```

(Alternatively, **`../scripts/fsr_metrics.py`** in `docs_2.0/recurring-visits/scripts/` can be used with the same `--exclude-inactive` and `--save` options.)

## Expected Metrics

**Target**: 65%+ routing efficiency after from-patch

## Data Quality Notes

- ✅ **13 addresses manually geocoded** (Feb 12, 2026) - added 37 visit occurrences
- ⚠️ **81 visits still missing coordinates** (9.3% of source) - empty address field
- 📊 Smaller scale than Movable/Huddinge (~867 source → 2,740 expanded)
- 📅 Uses 4-week planning window (has monthly recurring visits)
- 📈 **Current coverage: 90.7%** (786 of 867 source visits)

## Remaining Resolution Required

To reach 100% coverage:

1. Contact Nova for 81 missing addresses
2. Re-run expansion after addresses provided

**Current state**: Running with 2,740 valid visits (90.7% coverage) - **GOOD ENOUGH FOR TESTING**
