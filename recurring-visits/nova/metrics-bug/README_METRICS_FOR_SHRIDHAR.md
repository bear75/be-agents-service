# Metrics runs for Shridhar (plan 4a47b69a)

**Date:** 2026-03-09  
**Purpose:** Reference metrics for the three shift/break variants (see beta-appcaire `BUG_SOLUTION_METRICS_TOTAL_SHIFT_AND_VARIANTS.md`).

## Variants (break: A ≥ B ≥ C)

| Variant | Folder | Shift | Break | Idle | Efficiency |
|--------|--------|-------|-------|------|------------|
| **A – All shifts** | `variant_A_all_shifts/` | 3 827 h 0 min | 261 h 0 min | 2 414 h 49 min | 30.35% |
| **B – Active shifts** | `variant_B_active_shifts/` | 1 777 h 30 min | 128 h 30 min | 497 h 49 min | 65.63% |
| **C – Field time** | `variant_C_field_time/` | 1 248 h 49 min | 110 h 15 min | 0 h 0 min | 95.05% |

- **A:** All shifts (incl. empty, break-only). All breaks. Shift from input schedule.
- **B:** Only shifts with ≥ 1 visit. Break if shift has visits (any order). Tail break included.
- **C:** Field time only (first visit start → last visit end). Break only if there is a visit **after** the break (tail break excluded).

## Files to send

1. **Bug report (from beta-appcaire):**  
   `docs/docs_2.0/10-consistency/BUG_SOLUTION_METRICS_TOTAL_SHIFT_AND_VARIANTS.md`

2. **Script (this repo, private):**  
   `recurring-visits/scripts/metrics.py`

3. **Input/Output (this folder):**  
   - `export-field-service-routing-v1-4a47b69a-...-input.json`  
   - `export-field-service-routing-4a47b69a-...-output (2).json`

4. **Metrics runs (this folder):**  
   - `variant_A_all_shifts/metrics_report_4a47b69a.txt` + `metrics_*_4a47b69a.json`  
   - `variant_B_active_shifts/metrics_report_4a47b69a.txt` + `metrics_*_4a47b69a.json`  
   - `variant_C_field_time/metrics_report_4a47b69a.txt` + `metrics_*_4a47b69a.json`

## How to reproduce

From `be-agent-service/recurring-visits/scripts`:

```bash
OUT="../nova/metrics-bug/export-field-service-routing-4a47b69a-08c4-4f72-a9da-66d98a245b56-output (2).json"
IN="../nova/metrics-bug/export-field-service-routing-v1-4a47b69a-08c4-4f72-a9da-66d98a245b56-input.json"

# A – all shifts, all breaks
python3 metrics.py "$OUT" --input "$IN" --save ../nova/metrics-bug/variant_A_all_shifts

# B – active shifts, break any order
python3 metrics.py "$OUT" --input "$IN" --exclude-empty-shifts-only --save ../nova/metrics-bug/variant_B_active_shifts

# C – field time, break only if visit after
python3 metrics.py "$OUT" --input "$IN" --visit-span-only --save ../nova/metrics-bug/variant_C_field_time
```
