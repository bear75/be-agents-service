# Timefold Scripts - Consolidated Structure

This directory contains all Python scripts for the Timefold scheduling workflow, consolidated from multiple scattered locations.

## Directory Structure

### conversion/
CSV → FSR input transformation scripts.

**Primary scripts:**
- `csv_to_fsr.py` - Main CSV→FSR converter (consolidated from attendo_4mars_to_fsr.py)
- `expand_recurring_visits.py` - Expand recurring visits from CSV
- `analyze_csv_to_json.py` - CSV↔JSON analysis

**Usage:**
```bash
python scripts/timefold/conversion/csv_to_fsr.py \
  --input recurring-visits/data/huddinge-v3/raw/Huddinge-v3.csv \
  --output recurring-visits/data/huddinge-v3/input/input.json
```

### submission/
Timefold API interaction - submit jobs and fetch results.

**Primary scripts:**
- `submit_solve.py` - Submit FSR solve job to Timefold API
- `submit_from_patch.py` - Submit from-patch (continuity) job
- `fetch_solution.py` - Fetch completed solution by job ID

**Usage:**
```bash
# Submit solve
python scripts/timefold/submission/submit_solve.py \
  --input recurring-visits/data/huddinge-v3/input/input.json \
  --job-id my_job_123

# Fetch solution
python scripts/timefold/submission/fetch_solution.py \
  --job-id my_job_123 \
  --output recurring-visits/data/huddinge-v3/output/solution.json
```

### analysis/
Metrics calculation, reports, and solution analysis.

**Metrics:**
- `metrics.py` - Primary metrics calculation (efficiency, unassigned %, distance)
- `fsr_metrics.py` - FSR-specific metrics
- `solve_report.py` - Generate solve reports

**Continuity:**
- `continuity_report.py` - Generate continuity reports
- `analyze_continuity_batch.py` - Batch continuity analysis

**Analysis:**
- `analyze_unassigned.py` - Unassigned visits analysis
- `analyze_empty_shifts.py` - Empty shift detection
- `analyze_day.py` - Day-level analysis
- `analyze_supply_demand.py` - Supply/demand analysis

**Usage:**
```bash
# Calculate metrics
python scripts/timefold/analysis/metrics.py \
  --solution recurring-visits/data/huddinge-v3/output/solution.json

# Generate continuity report
python scripts/timefold/analysis/continuity_report.py \
  --input recurring-visits/data/huddinge-v3/input/input.json \
  --solution recurring-visits/data/huddinge-v3/output/solution.json \
  --output recurring-visits/data/huddinge-v3/continuity/reports/continuity.csv
```

### campaigns/
Multi-variant campaign orchestration and strategy execution.

**Orchestrators:**
- `orchestrator.py` - Main campaign orchestrator
- `enhanced_controller.py` - Enhanced optimization controller
- `pareto_optimizer.py` - Pareto optimization campaigns

**Strategy:**
- `strategy_generator.py` - Generate optimization strategies
- `campaign_runner.py` - Execute multi-variant campaigns

**Usage:**
```bash
# Run campaign
python scripts/timefold/campaigns/campaign_runner.py \
  --config recurring-visits/data/huddinge-v3/continuity/campaign_config.json
```

### continuity/
Continuity pool building and from-patch payload generation.

**Primary scripts:**
- `build_pools.py` - Build continuity pools from first-run output
- `build_from_patch.py` - Build from-patch payload
- `build_trimmed_input.py` - Build trimmed input (remove empty shifts)

**Usage:**
```bash
# Build continuity pools
python scripts/timefold/continuity/build_pools.py \
  --solution recurring-visits/data/huddinge-v3/output/solution.json \
  --pool-size 5 \
  --output recurring-visits/data/huddinge-v3/continuity/pools.json

# Build from-patch
python scripts/timefold/continuity/build_from_patch.py \
  --solution recurring-visits/data/huddinge-v3/output/solution.json \
  --pools recurring-visits/data/huddinge-v3/continuity/pools.json \
  --output recurring-visits/data/huddinge-v3/continuity/from_patch.json
```

### utils/
Validation, helpers, and utility functions.

**Validation:**
- `verify_visits_flex.py` - Verify all visits have flex time
- `validate_dependencies.py` - Dependency feasibility validation
- `compare_inputs.py` - Compare FSR inputs

**Helpers:**
- `anonymize.py` - Anonymize data for demos
- `calculate_time_windows.py` - Time window calculations
- `register_run.py` - Register run to be-agent-service database

**Usage:**
```bash
# Verify input
python scripts/timefold/utils/verify_visits_flex.py \
  --input recurring-visits/data/huddinge-v3/input/input.json

# Register run to database
python scripts/timefold/utils/register_run.py \
  --job-id my_job_123 \
  --dataset huddinge-v3 \
  --metrics-file /tmp/metrics.json
```

### repair/
Repair strategies for fixing infeasible solutions (experimental).

**Scripts:**
- `remove_constraints.py` - Remove hard constraints to find feasible solution
- `add_vehicles.py` - Add vehicles to improve capacity
- `fix_vehicle_conflicts.py` - Fix vehicle-shift conflicts

### monitoring/
Campaign monitoring and testing scripts.

**Scripts:**
- `monitor_campaign.py` - Monitor running campaigns
- `quick_analysis.py` - Quick strategic analysis
- `test_fixtures.py` - Testing helpers

## Migration from Old Locations

This consolidated structure replaces the old scattered locations:

**Old → New:**
- `recurring-visits/scripts/*.py` → `scripts/timefold/{category}/`
- `recurring-visits/optimization-research-scripts/*.py` → `scripts/timefold/campaigns/`
- `recurring-visits/huddinge-package/huddinge-4mars-csv/scripts/*.py` → `scripts/timefold/conversion/`

**See:** `docs/CONSOLIDATED_SCRIPTS.md` for complete migration map.

## Data Locations

Scripts read/write data from `recurring-visits/data/`:

```
recurring-visits/data/
├── huddinge-v3/         # Active dataset
│   ├── raw/             # CSV files
│   ├── input/           # FSR JSON inputs
│   ├── output/          # Solutions
│   ├── continuity/      # Pool campaigns
│   └── docs/            # Campaign docs
├── nova/                # Nova region
└── archive/             # Old versions (v2, experiments)
```

## Environment Variables

Scripts use these environment variables:

- `TIMEFOLD_API_KEY` - Timefold API key (required for submission)
- `AGENT_SERVICE_URL` - be-agent-service API URL (default: http://localhost:3010)
- `DATASET` - Dataset name (default: huddinge-v3)

**Setup:**
```bash
export TIMEFOLD_API_KEY="sk_xxx"
export AGENT_SERVICE_URL="http://localhost:3010"
export DATASET="huddinge-v3"
```

## Integration with Agent Automation

These scripts are called by agent shells:

- `agents/timefold-specialist.sh` - Calls submission, analysis scripts
- `agents/optimization-mathematician.sh` - Uses metrics, reports for strategy
- `scripts/compound/schedule-research-loop.sh` - Orchestrates workflow

## Common Workflows

### Full Pipeline (CSV → Solution → Metrics)
```bash
# 1. Convert CSV to FSR
python scripts/timefold/conversion/csv_to_fsr.py \
  --input recurring-visits/data/huddinge-v3/raw/Huddinge-v3.csv \
  --output recurring-visits/data/huddinge-v3/input/input.json

# 2. Submit to Timefold
python scripts/timefold/submission/submit_solve.py \
  --input recurring-visits/data/huddinge-v3/input/input.json \
  --job-id job_$(date +%s)

# 3. Fetch solution (poll until complete)
python scripts/timefold/submission/fetch_solution.py \
  --job-id job_123456789 \
  --output recurring-visits/data/huddinge-v3/output/solution.json

# 4. Calculate metrics
python scripts/timefold/analysis/metrics.py \
  --solution recurring-visits/data/huddinge-v3/output/solution.json

# 5. Generate continuity report
python scripts/timefold/analysis/continuity_report.py \
  --input recurring-visits/data/huddinge-v3/input/input.json \
  --solution recurring-visits/data/huddinge-v3/output/solution.json \
  --output recurring-visits/data/huddinge-v3/continuity/reports/report.csv
```

### Continuity Optimization (From-Patch)
```bash
# 1. Build continuity pools from first run
python scripts/timefold/continuity/build_pools.py \
  --solution recurring-visits/data/huddinge-v3/output/solution.json \
  --pool-size 5 \
  --output recurring-visits/data/huddinge-v3/continuity/pools.json

# 2. Build from-patch payload
python scripts/timefold/continuity/build_from_patch.py \
  --solution recurring-visits/data/huddinge-v3/output/solution.json \
  --pools recurring-visits/data/huddinge-v3/continuity/pools.json \
  --output recurring-visits/data/huddinge-v3/continuity/from_patch.json

# 3. Submit from-patch
python scripts/timefold/submission/submit_from_patch.py \
  --from-patch recurring-visits/data/huddinge-v3/continuity/from_patch.json \
  --job-id continuity_job_$(date +%s)

# 4. Fetch and analyze
python scripts/timefold/submission/fetch_solution.py \
  --job-id continuity_job_123456789 \
  --output recurring-visits/data/huddinge-v3/output/solution_continuity.json
```

## Development

**Adding new scripts:**
1. Place in appropriate category directory
2. Follow naming convention: `verb_noun.py` (e.g., `build_pools.py`, `analyze_metrics.py`)
3. Add docstring with usage example
4. Use environment variables for configuration
5. Write results to `recurring-visits/data/{dataset}/`
6. Register run to database via `utils/register_run.py`

**Import conventions:**
```python
# Use relative imports within timefold scripts
from ..utils.validation import verify_visits
from ..analysis.metrics import calculate_metrics

# Use absolute imports for external dependencies
import json
import sys
from pathlib import Path
```

## See Also

- `docs/CONSOLIDATED_SCRIPTS.md` - Complete migration map
- `docs/TIMEFOLD_WORKFLOW.md` - Detailed workflow documentation
- `docs/SCHEDULE_RESEARCH_GUIDE.md` - User guide for Schedule Research UI
- `config/timefold.yaml` - Timefold API configuration
