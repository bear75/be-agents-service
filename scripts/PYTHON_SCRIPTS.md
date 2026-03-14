# Consolidated Python Scripts

Timefold FSR schedule optimization scripts organized by function.

## Directory Structure

```
scripts/
├── timefold/          # Timefold API interaction
├── conversion/        # CSV → FSR JSON conversion
├── continuity/        # Continuity optimization (pools, from-patch)
├── analytics/         # Metrics calculation and analysis
├── verification/      # Input validation
├── geocoding/         # Address geocoding
└── utils/             # Shared utilities
```

## Timefold API (`timefold/`)

**submit.py** - Submit solve or from-patch jobs to Timefold API
```bash
python3 scripts/timefold/submit.py solve INPUT.json --wait --save OUTPUT.json
python3 scripts/timefold/submit.py from-patch INPUT.json PATCH.json --wait
```

**fetch.py** - Fetch solution from Timefold by route plan ID
```bash
python3 scripts/timefold/fetch.py ROUTE_PLAN_ID --save OUTPUT.json
```

## Conversion (`conversion/`)

**csv_to_fsr.py** - Convert Attendo CSV to Timefold FSR JSON (v3 4mars format)
```bash
python3 scripts/conversion/csv_to_fsr.py \
  "Huddinge-v3 - Data_final.csv" \
  --start-date 2026-03-02 \
  --end-date 2026-03-15 \
  --no-geocode \
  -o input.json
```

Primary script for Huddinge v3 dataset with:
- Time window generation (Morgon/Lunch/Kväll slots)
- Visit dependencies (PT0M same-day, PT3H30M spacing)
- Visit groups (Dubbel visits)
- Coordinate integration (if geocoded)

## Continuity (`continuity/`)

**build_pools.py** - Generate vehicle pools per client (pool3/pool5/pool8)
```bash
python3 scripts/continuity/build_pools.py \
  --input input.json \
  --pool-size 5 \
  --output input_pool5.json
```

**build_from_patch.py** - Create from-patch payload for continuity tightening
```bash
python3 scripts/continuity/build_from_patch.py \
  --baseline baseline.json \
  --target 11.0 \
  --output from_patch.json
```

**build_trimmed_input.py** - Remove empty shifts and unused vehicles
```bash
python3 scripts/continuity/build_trimmed_input.py \
  --output solution.json \
  --input input.json \
  --out input_trimmed.json
```

**report.py** - Generate continuity analysis report
```bash
python3 scripts/continuity/report.py solution.json
```

## Analytics (`analytics/`)

**metrics.py** - Calculate routing metrics (efficiency, continuity, unassigned)
```bash
python3 scripts/analytics/metrics.py solution.json
```

**analyze_unassigned.py** - Analyze why visits are unassigned
```bash
python3 scripts/analytics/analyze_unassigned.py solution.json input.json
```

**analyze_empty_shifts.py** - Find empty vehicle shifts
```bash
python3 scripts/analytics/analyze_empty_shifts.py solution.json
```

**analyze_supply_demand.py** - Supply vs demand analysis by day
```bash
python3 scripts/analytics/analyze_supply_demand.py solution.json input.json
```

**compare_csv_json.py** - Verify CSV → JSON mapping
```bash
python3 scripts/analytics/compare_csv_json.py source.csv input.json
```

**analyze_dependency_feasibility.py** - Check if dependencies are physically feasible
```bash
python3 scripts/analytics/analyze_dependency_feasibility.py input.json
```

## Verification (`verification/`)

**verify_flex.py** - Verify all visits have time window flexibility
```bash
python3 scripts/verification/verify_flex.py input.json
```

**compare_time_windows.py** - Compare time windows between old and new inputs
```bash
python3 scripts/verification/compare_time_windows.py old_input.json new_input.json
```

## Geocoding (`geocoding/`)

**build_coordinates.py** - Geocode addresses to lat/lon coordinates
```bash
python3 scripts/geocoding/build_coordinates.py \
  --csv "addresses.csv" \
  --output coordinates.json
```

## Utils (`utils/`)

**anonymize.py** - Remove PII from FSR JSON for sharing
```bash
python3 scripts/utils/anonymize.py input.json --output anonymized.json
```

## Common Workflows

### Full Research Pipeline

1. **Convert CSV to FSR JSON**
```bash
python3 scripts/conversion/csv_to_fsr.py \
  "Huddinge-v3 - Data_final.csv" \
  --start-date 2026-03-02 \
  --end-date 2026-03-15 \
  --no-geocode \
  -o input.json
```

2. **Submit to Timefold**
```bash
python3 scripts/timefold/submit.py solve input.json --wait --save solution.json
```

3. **Calculate Metrics**
```bash
python3 scripts/analytics/metrics.py solution.json
```

4. **Generate Continuity Report**
```bash
python3 scripts/continuity/report.py solution.json
```

### Continuity Optimization

1. **Build Vehicle Pools**
```bash
python3 scripts/continuity/build_pools.py \
  --input input.json \
  --pool-size 5 \
  --output input_pool5.json
```

2. **Submit Pool Variant**
```bash
python3 scripts/timefold/submit.py solve input_pool5.json --wait --save solution_pool5.json
```

3. **Build From-Patch for Best Result**
```bash
python3 scripts/continuity/build_from_patch.py \
  --baseline solution_pool5.json \
  --target 11.0 \
  --output from_patch.json
```

4. **Submit From-Patch**
```bash
python3 scripts/timefold/submit.py from-patch input_pool5.json from_patch.json --wait --save solution_continuity.json
```

### Validation

1. **Verify Time Window Flexibility**
```bash
python3 scripts/verification/verify_flex.py input.json
```

2. **Check Dependency Feasibility**
```bash
python3 scripts/analytics/analyze_dependency_feasibility.py input.json
```

3. **Verify CSV Mapping**
```bash
python3 scripts/analytics/compare_csv_json.py source.csv input.json
```

## Agent Integration

Agents (`agents/timefold-specialist.sh`, `agents/optimization-mathematician.sh`) use these consolidated scripts:

- Specialist calls `scripts/timefold/submit.py` and `scripts/analytics/metrics.py`
- Mathematician reads metrics from schedule_runs database
- Research loop (`scripts/compound/schedule-research-loop.sh`) orchestrates

## Source Locations

Scripts consolidated from:
- `/recurring-visits/scripts/` (50+ legacy scripts)
- `/recurring-visits/huddinge-package/huddinge-4mars-csv/scripts/` (v3-specific conversion)

See `/docs/SCRIPT_LOCATIONS.md` for detailed migration map.

## Dataset Locations

**Active Dataset:** `/recurring-visits/data/huddinge-v3/`
```
huddinge-v3/
├── raw/
│   └── Huddinge-v3 - Data_final.csv       # Source CSV (22 cols with Lat/Lon)
├── input/
│   └── input_huddinge-v3_FIXED.json       # Research input (3,844 visits)
└── output/
    └── [solution files from Timefold]
```

**Source CSV:** `/recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/Huddinge-v3 - Data_final.csv`
- 665 rows (664 data + header)
- 22 columns (includes Lat, Lon)
- 115 clients

## Notes

- **Primary conversion script:** `scripts/conversion/csv_to_fsr.py` (from attendo_4mars_to_fsr.py)
- **Tags removed:** FSR schema doesn't accept `tags` property on visits
- **Current input:** 3,844 visits (3,520 standalone + 324 in groups), 2,069 dependencies
- **Planning window:** March 2-15, 2026 (2 weeks)
