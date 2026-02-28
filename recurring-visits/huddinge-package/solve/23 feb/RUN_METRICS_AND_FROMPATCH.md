# Run metrics and from-patch for f506797a (23 Feb solve)

Run these from the **appcaire** repo, **huddinge-package** root. Not from beta-appcaire.

```bash
cd /path/to/caire-platform/appcaire/docs_2.0/recurring-visits/huddinge-package
```

## Two-step flow: add shifts → then trim idle

**Step 1 — Add shifts to cover unassigned, then submit new solve**

```bash
# 1a) Add placeholder shifts (use --add-anyway if analysis says "config only, 0 supply")
python3 scripts/add_shifts_from_unassigned.py \
  "solve/23 feb/export-field-service-routing-v1-f506797a-9f51-4022-ad90-1965ba9db788-input.json" \
  "solve/23 feb/export-field-service-routing-f506797a-9f51-4022-ad90-1965ba9db788-output.json" \
  --out "solve/23 feb/input_plus_shifts.json" --no-timestamp --add-anyway

# 1b) Submit new solve to Timefold (saves to output_plus_shifts.json; use --no-timestamp for fixed filename)
python3 scripts/submit_to_timefold.py solve "solve/23 feb/input_plus_shifts.json" \
  --save "solve/23 feb/output_plus_shifts.json" --no-timestamp --wait
```

After 1b completes, note the **new route plan ID** from the script output or from the saved JSON.

**Step 2 — Trim idle and empty shifts (from-patch on the new solve)**

```bash
# 2a) Build from-patch payload from the NEW output (use the new output file and new input)
python3 scripts/build_from_patch.py \
  --output "solve/23 feb/output_plus_shifts.json" \
  --input "solve/23 feb/input_plus_shifts.json" \
  --out "solve/23 feb/from-patch/payload_plus_shifts.json" --no-timestamp

# 2b) Submit from-patch using the NEW route plan ID (from step 1b)
python3 scripts/submit_to_timefold.py from-patch "solve/23 feb/from-patch/payload_plus_shifts.json" \
  --route-plan-id <NEW_ROUTE_PLAN_ID> \
  --save "solve/23 feb/from-patch/output_trimmed.json" --wait
```

Replace `<NEW_ROUTE_PLAN_ID>` with the ID printed when step 1b completed (or read from `solve/23 feb/output_plus_shifts.json` → `metadata.id`).

### Iterate: still unassigned (add more shifts, re-solve)

If the new solve still has unassigned, add more shifts from the **latest** output and submit again. Use the last input and last output; increase `--per-date` for more capacity per day.

**Example: 23febv2 solve (77970141)** — add more shifts from that output, then submit next solve:

```bash
python3 scripts/add_shifts_from_unassigned.py \
  "solve/23febv2/export-field-service-routing-v1-77970141-cb4f-42fd-adb3-50291494eb30-input.json" \
  "solve/23febv2/export-field-service-routing-77970141-cb4f-42fd-adb3-50291494eb30-output.json" \
  --out "solve/23febv2/input_plus_shifts_v2.json" --no-timestamp --add-anyway --per-date 2

python3 scripts/submit_to_timefold.py solve "solve/23febv2/input_plus_shifts_v2.json" \
  --save "solve/23febv2/output_plus_shifts_v2.json" --no-timestamp --wait
```

Repeat with the new input/output (e.g. _v3), until 0 unassigned; then run from-patch (step 2) to trim idle/empty.

---

## 0. Reach 0 unassigned (add shifts from supply/demand)

From-patch does **not** add capacity. To assign all visits:

1. **Supply/demand:** `python3 scripts/analyze_supply_demand.py "solve/23 feb/export-field-service-routing-f506797a-9f51-4022-ad90-1965ba9db788-output.json" "solve/23 feb/export-field-service-routing-v1-f506797a-9f51-4022-ad90-1965ba9db788-input.json" --report "solve/23 feb/Supply_Demand_Analysis_f506797a.md"`
2. **Unassigned (supply vs config):** `python3 scripts/analyze_unassigned.py "solve/23 feb/export-field-service-routing-v1-f506797a-9f51-4022-ad90-1965ba9db788-input.json" "solve/23 feb/export-field-service-routing-f506797a-9f51-4022-ad90-1965ba9db788-output.json"`
3. **Add shifts** on dates where demand exceeds supply. If analysis says "0 supply" (config only), add `--add-anyway`:
   ```bash
   python3 scripts/add_shifts_from_unassigned.py \
     "solve/23 feb/export-field-service-routing-v1-f506797a-9f51-4022-ad90-1965ba9db788-input.json" \
     "solve/23 feb/export-field-service-routing-f506797a-9f51-4022-ad90-1965ba9db788-output.json" \
     --out "solve/23 feb/input_plus_shifts.json" --no-timestamp --add-anyway
   ```
   Or add generic evening capacity: `python3 scripts/add_evening_vehicles.py "solve/23 feb/...-input.json" --out "solve/23 feb/input_evening.json" --count 3 --no-timestamp`
4. **Submit new solve to Timefold** (so the solve appears in the TF dashboard). From huddinge-package root:
   ```bash
   python3 scripts/submit_to_timefold.py solve "solve/23 feb/input_plus_shifts.json" --save "solve/23 feb/output_plus_shifts.json"
   ```
   Add `--wait` to poll until the solve completes and save the output. The script will print the new **route plan ID** — use that in the Timefold dashboard or for a later from-patch. Only after this solve has 0 unassigned, run from-patch (section 2) to trim idle/empty.

## 1. Metrics + from-patch payload

```bash
# From huddinge-package root (inside appcaire)
python3 scripts/run_23feb_metrics_and_patch.py
```

This runs:
- **solve_report** → metrics, unassigned analysis, empty-shifts; saves to `solve/23 feb/metrics/`
- **build_from_patch** → writes `solve/23 feb/from-patch/payload_f506797a.json`

## 2. Remove idle and empty shifts (submit from-patch)

From-patch **removes idle time** (end each shift at depot arrival) and **removes empty shifts and vehicles**. Run it only after the solve has 0 unassigned (or when you accept current unassigned and want to trim the rest).

Requires `TIMEFOLD_API_KEY` (or default in script).

```bash
python3 scripts/submit_to_timefold.py from-patch "solve/23 feb/from-patch/payload_f506797a.json" \
  --route-plan-id f506797a-9f51-4022-ad90-1965ba9db788 \
  --save "solve/23 feb/from-patch/output_f506797a.json"
```

Add `--wait` to poll until the new solve completes.

What from-patch does:
- **Pin** assigned visits (lock the solution).
- **End shifts at depot** → removes idle (tail time after last visit).
- **Remove** shifts with no visits (empty shifts).
- **Remove** vehicles that end up with no shifts.

## Route plan ID

- **f506797a-9f51-4022-ad90-1965ba9db788** (from filenames)

## Files

- Output: `export-field-service-routing-f506797a-9f51-4022-ad90-1965ba9db788-output.json`
- Input: `export-field-service-routing-v1-f506797a-9f51-4022-ad90-1965ba9db788-input.json`
