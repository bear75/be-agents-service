# Recurring Visits Data - Consolidated Structure

This directory contains all datasets, inputs, outputs, and campaign results for Timefold scheduling research.

## Directory Structure

### huddinge-v3/
Active dataset for Huddinge v3 (115 clients, 4mars CSV format).

```
huddinge-v3/
├── raw/                    # CSV source files
│   └── Huddinge-v3 - Data.csv
├── input/                  # FSR JSON inputs
│   ├── input.json
│   ├── input_v3_FIXED.json
│   └── ...
├── output/                 # Timefold solutions
│   ├── solution_82a338b9.json
│   ├── solution_f3d21abc.json
│   └── ...
├── continuity/             # Continuity optimization campaigns
│   ├── pools/              # Continuity pool definitions
│   ├── from-patch/         # From-patch payloads
│   ├── results/            # Campaign results
│   └── reports/            # Continuity reports
└── docs/                   # Campaign documentation
    ├── SUMMARY.md
    └── campaign_notes.md
```

**Current status:**
- CSV: Huddinge v3 format (4mars structure)
- Clients: 115 clients with recurring visits
- Time window: 2-week planning horizon
- Best result: Job 82a338b9 (continuity: 14.0, efficiency: 90.03%)

### nova/
Nova region dataset (future).

**Status:** Not yet populated. Structure mirrors huddinge-v3/.

### archive/
Old datasets, experiments, and deprecated versions.

**Contents:**
- `v2/` - Huddinge v2 dataset (old CSV format)
- `demos/` - Demo data for testing
- `experiments/` - One-off experimental runs
- Old campaign results moved from scattered locations

## Data Flow

### 1. CSV Input → FSR Input
```
raw/Huddinge-v3.csv
  ↓ [conversion/csv_to_fsr.py]
input/input.json
```

### 2. FSR Input → Timefold API → Solution
```
input/input.json
  ↓ [submission/submit_solve.py]
Timefold API (solve job)
  ↓ [submission/fetch_solution.py]
output/solution_<job_id>.json
```

### 3. Solution → Metrics & Reports
```
output/solution.json
  ↓ [analysis/metrics.py]
metrics: {efficiency, continuity, unassigned}
  ↓ [analysis/continuity_report.py]
continuity/reports/report.csv
```

### 4. Solution → Continuity Pools → From-Patch
```
output/solution.json
  ↓ [continuity/build_pools.py]
continuity/pools/pool5.json
  ↓ [continuity/build_from_patch.py]
continuity/from-patch/from_patch.json
  ↓ [submission/submit_from_patch.py]
Timefold API (from-patch job)
  ↓ [submission/fetch_solution.py]
output/solution_continuity.json
```

## Dataset Versioning

Datasets are version-controlled via git:

- **Inputs:** Committed to git (FSR JSON files)
- **Outputs:** Not committed (too large, regenerable)
- **Continuity configs:** Committed to git (campaign definitions)
- **Reports:** Committed to git (CSVs, summaries)

**Gitignore patterns:**
```gitignore
recurring-visits/data/*/output/*.json
recurring-visits/data/*/raw/*.csv  # Large CSV files
recurring-visits/data/archive/
```

**Committed to git:**
```
recurring-visits/data/huddinge-v3/input/*.json
recurring-visits/data/huddinge-v3/continuity/pools/*.json
recurring-visits/data/huddinge-v3/continuity/reports/*.csv
recurring-visits/data/huddinge-v3/docs/*.md
```

## Campaign Organization

Continuity campaigns are organized by strategy:

```
huddinge-v3/continuity/
├── pool3/                  # Pool size 3 campaigns
│   ├── config.json
│   ├── launch.sh
│   └── results/
├── pool5/                  # Pool size 5 campaigns
│   ├── config.json
│   ├── launch.sh
│   └── results/
└── pool8/                  # Pool size 8 campaigns
    ├── config.json
    ├── launch.sh
    └── results/
```

**Campaign config format:**
```json
{
  "name": "pool5_continuity_v2",
  "base_job_id": "82a338b9",
  "pool_size": 5,
  "variants": [
    {"name": "required", "vehicle_mode": "required"},
    {"name": "preferred", "vehicle_mode": "preferred"},
    {"name": "weighted", "area_weight": 2.0}
  ]
}
```

## Migration from Old Locations

Data has been consolidated from these old scattered locations:

**Old → New:**
- `recurring-visits/huddinge-package/huddinge-4mars-csv/` → `data/huddinge-v3/`
- `recurring-visits/huddinge-package/solve/` → `data/archive/v2/`
- `recurring-visits/huddinge-package/continuity -3march/` → `data/huddinge-v3/continuity/`
- `recurring-visits/demo-data/` → `data/archive/demos/`

**See:** `docs/CONSOLIDATED_SCRIPTS.md` for complete migration map.

## Environment Variables

Scripts use `DATASET` environment variable to locate data:

```bash
export DATASET="huddinge-v3"

# Scripts will read/write from:
# recurring-visits/data/$DATASET/
```

**Default:** `huddinge-v3`

## Database Integration

Solve runs are registered to be-agent-service database:

```sql
-- schedule_runs table
INSERT INTO schedule_runs (
  job_id,
  dataset,
  status,
  efficiency,
  continuity_avg,
  unassigned_pct,
  total_distance,
  input_file,
  output_file,
  created_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
```

**Registered via:**
```bash
python scripts/timefold/utils/register_run.py \
  --job-id my_job_123 \
  --dataset huddinge-v3 \
  --metrics-file /tmp/metrics.json
```

## Best Practices

### File Naming Conventions

**Inputs:**
- `input.json` - Primary input
- `input_v{N}.json` - Versioned inputs
- `input_v{N}_FIXED.json` - Fixed versions

**Outputs:**
- `solution_{job_id}.json` - Solution by job ID
- `solution_{job_id}_continuity.json` - Continuity-optimized solution

**Reports:**
- `continuity_report_{job_id}.csv` - Continuity report
- `metrics_{job_id}.json` - Metrics JSON
- `summary_{campaign_name}.md` - Campaign summary

### Data Retention

**Keep:**
- Best results (top 5 by efficiency/continuity)
- Campaign milestones
- Failed runs with insights

**Archive:**
- Intermediate experiments (after 30 days)
- Duplicate results
- Old versions (after new version validated)

### Backup

Critical data is backed up:
- Inputs: Committed to git
- Best results: Copied to `best-results/` (committed to git)
- Campaign configs: Committed to git

**Backup strategy:**
```bash
# Copy best result
cp output/solution_82a338b9.json best-results/solution_best_2026-03-14.json

# Commit to git
git add data/huddinge-v3/input/ data/huddinge-v3/best-results/
git commit -m "data: Save best result (continuity 14.0)"
```

## See Also

- `scripts/timefold/README.md` - Script documentation
- `docs/TIMEFOLD_WORKFLOW.md` - Workflow guide
- `docs/CONSOLIDATED_SCRIPTS.md` - Migration map
- `docs/SCHEDULE_RESEARCH_GUIDE.md` - Research UI guide
