# Consolidated Scripts - Migration Map

This document maps old script locations to their new consolidated locations in the `scripts/timefold/` structure.

## Migration Summary

**Before:** 111 Python scripts scattered across 7+ directories
**After:** Core scripts consolidated into `scripts/timefold/` with clear categorization
**Status:** Old locations preserved for reference; new locations are canonical

---

## Script Migration Map

### CONVERSION (CSV → FSR)

| Old Location | New Location | Status |
|--------------|--------------|--------|
| `recurring-visits/huddinge-package/huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py` | `scripts/timefold/conversion/csv_to_fsr.py` | ✅ Migrated |
| `recurring-visits/scripts/csv_to_timefold_fsr.py` | `scripts/timefold/conversion/csv_to_fsr_legacy.py` | 📝 Reference (legacy) |
| `recurring-visits/scripts/expand_recurring_visits.py` | `scripts/timefold/conversion/expand_recurring.py` | 📝 Reference |
| `recurring-visits/huddinge-package/huddinge-4mars-csv/scripts/analyze_4mars_csv_to_json.py` | `scripts/timefold/conversion/analyze_csv.py` | 📝 Reference |
| `recurring-visits/huddinge-package/huddinge-4mars-csv/scripts/map_visits_time_windows.py` | `scripts/timefold/conversion/map_time_windows.py` | 📝 Reference |

**Primary script:** `scripts/timefold/conversion/csv_to_fsr.py` (formerly attendo_4mars_to_fsr.py)

---

### SUBMISSION (Timefold API)

| Old Location | New Location | Status |
|--------------|--------------|--------|
| `recurring-visits/scripts/submit_to_timefold.py` | `scripts/timefold/submission/submit_solve.py` | ✅ Migrated |
| `recurring-visits/scripts/fetch_timefold_solution.py` | `scripts/timefold/submission/fetch_solution.py` | ✅ Migrated |

**Usage:**
- `submit_solve.py` handles both fresh solves and from-patch submissions
- `fetch_solution.py` polls Timefold API and saves results

---

### ANALYSIS (Metrics & Reports)

| Old Location | New Location | Status |
|--------------|--------------|--------|
| `recurring-visits/scripts/metrics.py` | `scripts/timefold/analysis/metrics.py` | ✅ Migrated |
| `recurring-visits/scripts/fsr_metrics.py` | `scripts/timefold/analysis/fsr_metrics.py` | 📝 Reference |
| `recurring-visits/scripts/solve_report.py` | `scripts/timefold/analysis/solve_report.py` | 📝 Reference |
| `recurring-visits/scripts/continuity_report.py` | `scripts/timefold/analysis/continuity_report.py` | ✅ Migrated |
| `recurring-visits/scripts/analyze_continuity_batch.py` | `scripts/timefold/analysis/analyze_continuity_batch.py` | 📝 Reference |
| `recurring-visits/scripts/analyze_unassigned.py` | `scripts/timefold/analysis/analyze_unassigned.py` | ✅ Migrated |
| `recurring-visits/scripts/analyze_empty_shifts.py` | `scripts/timefold/analysis/analyze_empty_shifts.py` | ✅ Migrated |
| `recurring-visits/scripts/analyze_day.py` | `scripts/timefold/analysis/analyze_day.py` | 📝 Reference |
| `recurring-visits/scripts/analyze_supply_demand.py` | `scripts/timefold/analysis/analyze_supply_demand.py` | 📝 Reference |
| `recurring-visits/optimization-research-scripts/analyze_solution.py` | `scripts/timefold/analysis/analyze_solution.py` | 📝 Reference |
| `recurring-visits/optimization-research-scripts/analyze_continuity_patterns.py` | `scripts/timefold/analysis/analyze_continuity_patterns.py` | 📝 Reference |

**Primary scripts:**
- `metrics.py` - Core metrics calculation
- `continuity_report.py` - Continuity analysis and reporting

---

### CAMPAIGNS (Orchestration)

| Old Location | New Location | Status |
|--------------|--------------|--------|
| `recurring-visits/optimization-research-scripts/Timefold_Orchestrator.py` | `scripts/timefold/campaigns/orchestrator.py` | 📝 Reference |
| `recurring-visits/optimization-research-scripts/enhanced_optimization_controller.py` | `scripts/timefold/campaigns/enhanced_controller.py` | 📝 Reference |
| `recurring-visits/optimization-research-scripts/optimization_controller.py` | `scripts/timefold/campaigns/controller.py` | 📝 Reference |
| `recurring-visits/optimization-research-scripts/Pareto_Orchestrator.py` | `scripts/timefold/campaigns/pareto_orchestrator.py` | 📝 Reference |
| `recurring-visits/optimization-research-scripts/Timefold_Strategy_Generator.py` | `scripts/timefold/campaigns/strategy_generator.py` | 📝 Reference |
| `recurring-visits/optimization-research-scripts/tf_stage_optimization_campaign.py` | `scripts/timefold/campaigns/stage_campaign.py` | 📝 Reference |
| `recurring-visits/optimization-research-scripts/launch_continuity_focused_campaign.py` | `scripts/timefold/campaigns/launch_continuity.py` | 📝 Reference |

**Note:** Campaign orchestration scripts are referenced but not yet actively migrated. Current automation uses shell scripts in continuity campaign directories.

---

### CONTINUITY (Pools & From-Patch)

| Old Location | New Location | Status |
|--------------|--------------|--------|
| `recurring-visits/scripts/build_continuity_pools.py` | `scripts/timefold/continuity/build_pools.py` | ✅ Migrated |
| `recurring-visits/scripts/build_from_patch.py` | `scripts/timefold/continuity/build_from_patch.py` | ✅ Migrated |
| `recurring-visits/scripts/build_trimmed_input.py` | `scripts/timefold/continuity/build_trimmed_input.py` | 📝 Reference |
| `recurring-visits/scripts/build_expanded_2w_trimmed.py` | `scripts/timefold/continuity/build_expanded_trimmed.py` | 📝 Reference |
| `recurring-visits/scripts/build_one_busy_day_input.py` | `scripts/timefold/continuity/build_one_day.py` | 📝 Reference |

**Primary scripts:**
- `build_pools.py` - Build continuity pools from first-run output
- `build_from_patch.py` - Build from-patch payload for continuity optimization

---

### UTILS (Validation & Helpers)

| Old Location | New Location | Status |
|--------------|--------------|--------|
| `recurring-visits/scripts/anonymize_huddinge_to_demo.py` | `scripts/timefold/utils/anonymize.py` | ✅ Migrated |
| `recurring-visits/scripts/calculate_time_windows.py` | `scripts/timefold/utils/calculate_time_windows.py` | 📝 Reference |
| `recurring-visits/scripts/compare_fsr_inputs.py` | `scripts/timefold/utils/compare_inputs.py` | 📝 Reference |
| `recurring-visits/huddinge-package/huddinge-4mars-csv/scripts/verify_all_visits_have_flex.py` | `scripts/timefold/utils/verify_flex.py` | 📝 Reference |
| `recurring-visits/huddinge-package/huddinge-4mars-csv/scripts/analyze_dependency_feasibility.py` | `scripts/timefold/utils/validate_dependencies.py` | 📝 Reference |
| `recurring-visits/huddinge-package/huddinge-4mars-csv/scripts/compare_time_windows.py` | `scripts/timefold/utils/compare_time_windows.py` | 📝 Reference |
| N/A (new) | `scripts/timefold/utils/register_run.py` | ✨ New (database integration) |

**New script:** `register_run.py` - Registers solve runs to be-agent-service database via API

---

### REPAIR (Experimental)

| Old Location | New Location | Status |
|--------------|--------------|--------|
| `recurring-visits/optimization-research-scripts/repair_strategy_1_remove_constraints.py` | `scripts/timefold/repair/remove_constraints.py` | 📝 Archive |
| `recurring-visits/optimization-research-scripts/repair_strategy_2_add_vehicles.py` | `scripts/timefold/repair/add_vehicles.py` | 📝 Archive |
| `recurring-visits/optimization-research-scripts/comprehensive_vehicle_fix.py` | `scripts/timefold/repair/vehicle_fix.py` | 📝 Archive |
| `recurring-visits/optimization-research-scripts/fix_vehicleshift_conflicts.py` | `scripts/timefold/repair/fix_conflicts.py` | 📝 Archive |
| `recurring-visits/scripts/add_evening_vehicles.py` | `scripts/timefold/repair/add_evening_vehicles.py` | 📝 Archive |
| `recurring-visits/scripts/add_monday_shifts.py` | `scripts/timefold/repair/add_monday_shifts.py` | 📝 Archive |

**Status:** Repair scripts are experimental and not actively used. Kept for reference.

---

### MONITORING & TESTING

| Old Location | New Location | Status |
|--------------|--------------|--------|
| `recurring-visits/optimization-research-scripts/monitor_strategic_test.py` | `scripts/timefold/monitoring/monitor_test.py` | 📝 Reference |
| `recurring-visits/optimization-research-scripts/quick_strategic_analysis.py` | `scripts/timefold/monitoring/quick_analysis.py` | 📝 Reference |
| `recurring-visits/optimization-research-scripts/tf_stage_monitor.py` | `scripts/timefold/monitoring/stage_monitor.py` | 📝 Reference |
| `recurring-visits/huddinge-package/huddinge-4mars-csv/scripts/test_time_window_fixes.py` | `scripts/timefold/monitoring/test_time_windows.py` | 📝 Reference |

---

## Data Migration Map

### Huddinge V3 (Active Dataset)

| Old Location | New Location | Status |
|--------------|--------------|--------|
| `recurring-visits/huddinge-package/huddinge-4mars-csv/ATTENDO_DATABEHOV_PER_KUND_OCH_BESOK - data.csv` | `recurring-visits/data/huddinge-v3/raw/Huddinge-v3 - Data.csv` | ✅ Migrated |
| `recurring-visits/huddinge-package/huddinge-4mars-csv/input/*.json` | `recurring-visits/data/huddinge-v3/input/` | ✅ Migrated |
| `recurring-visits/huddinge-package/huddinge-4mars-csv/output/*.json` | `recurring-visits/data/huddinge-v3/output/` | ✅ Migrated |
| `recurring-visits/huddinge-package/continuity -3march/*` | `recurring-visits/data/huddinge-v3/continuity/` | ✅ Migrated |
| `recurring-visits/huddinge-package/huddinge-4mars-csv/README.md` | `recurring-visits/data/huddinge-v3/docs/HUDDINGE_V3_README.md` | ✅ Migrated |
| `recurring-visits/huddinge-package/huddinge-4mars-csv/E2E_RUN_20260305.md` | `recurring-visits/data/huddinge-v3/docs/E2E_RUN_20260305.md` | ✅ Migrated |

### Old Versions (Archived)

| Old Location | New Location | Status |
|--------------|--------------|--------|
| `recurring-visits/huddinge-package/solve/*` | `recurring-visits/data/archive/v2/` | 📝 To be archived |
| `recurring-visits/demo-data/*` | `recurring-visits/data/archive/demos/` | 📝 To be archived |
| `recurring-visits/huddinge-package/huddinge-4mars-csv/old-csv-format/*` | `recurring-visits/data/archive/old-csv-format/` | 📝 To be archived |

---

## Usage Changes

### Before (Old Paths)
```bash
# Old: Scattered paths
python recurring-visits/scripts/submit_to_timefold.py \
  --input recurring-visits/huddinge-package/huddinge-4mars-csv/input/input.json

python recurring-visits/scripts/fetch_timefold_solution.py \
  --job-id abc123

python recurring-visits/scripts/metrics.py \
  --solution recurring-visits/huddinge-package/huddinge-4mars-csv/output/solution.json
```

### After (Consolidated Paths)
```bash
# New: Consolidated structure
python scripts/timefold/submission/submit_solve.py \
  --input recurring-visits/data/huddinge-v3/input/input.json

python scripts/timefold/submission/fetch_solution.py \
  --job-id abc123 \
  --output recurring-visits/data/huddinge-v3/output/solution.json

python scripts/timefold/analysis/metrics.py \
  --solution recurring-visits/data/huddinge-v3/output/solution.json

# Register to database
python scripts/timefold/utils/register_run.py \
  --job-id abc123 \
  --dataset huddinge-v3 \
  --metrics-file /tmp/metrics.json
```

---

## Migration Status Legend

- ✅ **Migrated** - Script copied to new location, actively used
- 📝 **Reference** - Script referenced in old location, not yet migrated (available for future use)
- ✨ **New** - Newly created script (no old equivalent)
- 🗄️ **Archive** - Old script, deprecated or experimental

---

## Backward Compatibility

Old script locations are **preserved** and remain accessible. This ensures:
- Existing shell scripts continue to work
- Historical references remain valid
- No breaking changes to existing workflows

**Recommendation:** Update scripts and agent shells to use new consolidated paths going forward.

---

## Environment Variables

Scripts now support environment variables for configuration:

```bash
# Dataset selection
export DATASET="huddinge-v3"  # Default dataset

# API configuration
export TIMEFOLD_API_KEY="sk_xxx"
export AGENT_SERVICE_URL="http://localhost:3010"

# Data paths are inferred from DATASET:
# recurring-visits/data/$DATASET/
```

---

## Next Steps

### Immediate (Done)
- ✅ Core scripts migrated to consolidated locations
- ✅ V3 data migrated to new structure
- ✅ Directory structure created
- ✅ Migration documentation complete

### Phase 2 (In Progress)
- Create `config/timefold.yaml` for API configuration
- Update agent shells to use consolidated scripts
- Add database integration via `register_run.py`
- Test full workflow with new structure

### Future
- Migrate campaign orchestration scripts
- Archive deprecated/experimental scripts
- Consolidate remaining analysis scripts as needed

---

## See Also

- `scripts/timefold/README.md` - Consolidated scripts documentation
- `recurring-visits/data/README.md` - Data structure documentation
- `docs/TIMEFOLD_WORKFLOW.md` - End-to-end workflow guide
- `docs/SCHEDULE_RESEARCH_GUIDE.md` - Schedule Research UI guide
