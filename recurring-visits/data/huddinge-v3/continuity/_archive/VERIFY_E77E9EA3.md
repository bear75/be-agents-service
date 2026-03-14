# Continuity run e77e9ea3 – verify when back

**Route plan ID:** `e77e9ea3-883f-4b1c-83f4-54f948b9e13f`  
**Submitted:** 2026-03-03 (continuity input with 80 clients, same vehicle set as 5ff7929f)

## Input verified before submit

- **Dataset:** Expanded CSV `expanded/huddinge_2wk_expanded_20260224_043456.csv` (3622 visits)
- **Base input:** `continuity -3march/export-field-service-routing-v1-5ff7929f-738b-4cfa-9add-845c03089b0d-input.json`
- **Vehicles:** 42 (same as base)
- **Shifts:** 412 (same as base)
- **Total visits:** 3622
- **Continuity:** 80 of 81 clients with non-empty pool (requiredVehicles set); 3620 visits with requiredVehicles
- **Validation:** All requiredVehicles IDs are in the 42-vehicle set (0 invalid refs)

## Submitted artifact (exact payload sent)

- **File:** `solve/input_continuity_e77e9ea3_submitted.json`  
  (Copy of the continuity input that was sent; timestamped file is `solve/input_continuity_20260303_162640.json`)

## Config

- **Environment:** prod
- **Configuration ID:** default prod (8f3ffcc6-1cb4-4ef9-a4c4-770191a23834) – no `--config-id` override

## When you're back (5h)

1. **Check solve status** in Timefold dashboard for route plan `e77e9ea3-883f-4b1c-83f4-54f948b9e13f`.
2. **Fetch solution** when status is completed (export or API).
3. **Verify:** Continuity (same caregivers per client where possible), efficiency (routes, unassigned), client visit IDs preserved in output.

## Command used to submit

```bash
cd recurring-visits/huddinge-package
python3 process_huddinge.py \
  --expanded-csv expanded/huddinge_2wk_expanded_20260224_043456.csv \
  --weeks 2 \
  --base-input "continuity -3march/export-field-service-routing-v1-5ff7929f-738b-4cfa-9add-845c03089b0d-input.json" \
  --continuity --env prod --send
```
