# Run analyze, metrics, and from-patch for this solve

From **huddinge-package** root:

```bash
# 1. Combined report: metrics + unassigned analysis + empty-shifts analysis (one script)
python scripts/solve_report.py \
  solve/tf/export-field-service-routing-9789141a-f9b9-4dcb-aca6-9eb5c2dbe0eb-output.json \
  --input solve/input_20260214_171612.json \
  --save metrics/ \
  --csv metrics/unassigned_9789141a.csv

# 2. Build from-patch payload (pin visits, end shifts at depot, remove empty)
python scripts/build_from_patch.py \
  --output solve/tf/export-field-service-routing-9789141a-f9b9-4dcb-aca6-9eb5c2dbe0eb-output.json \
  --input solve/input_20260214_171612.json \
  --out from-patch/payload_9789141a.json \
  --no-timestamp
```

**3. Submit from-patch** (trimmed solution; requires `TIMEFOLD_API_KEY`):

```bash
python scripts/submit_to_timefold.py from-patch from-patch/payload_9789141a.json \
  --route-plan-id 9789141a-f9b9-4dcb-aca6-9eb5c2dbe0eb \
  --wait --save from-patch/output_9789141a.json
```

Or from appcaire root (if `pnpm timefold` points at this package):

```bash
pnpm timefold submit_to_timefold.py from-patch from-patch/payload_9789141a.json \
  --route-plan-id 9789141a-f9b9-4dcb-aca6-9eb5c2dbe0eb \
  --wait --save from-patch/output_9789141a.json
```

Config used for this solve: see [config.md](config.md) (profile: huddinge-test-long, 2h solve).
