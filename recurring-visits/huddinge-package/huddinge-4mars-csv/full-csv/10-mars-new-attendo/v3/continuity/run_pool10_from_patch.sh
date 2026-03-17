#!/usr/bin/env bash
# From-patch on pool10_required with long solve time. Run from be-agent-service root.
# Requires TIMEFOLD_API_KEY. Default: PT3H spentLimit, PT15M unimprovedSpentLimit (runConfiguration.termination). Override: TIMEFOLD_CAMPAIGN_SPENT_LIMIT=PT1H

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
V3="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$V3/../../../../../.." && pwd)"

POOL10_OUTPUT="${REPO_ROOT}/scripts/analytics/campaign_analysis/pool10_required/output.json"
POOL10_INPUT="$V3/continuity/variants/input_pool10_required.json"
PATCH_OUT="$V3/continuity/from_patch/pool10_required_patch.json"
RES="$V3/continuity/results"
CAMPAIGN_SPENT_LIMIT="${TIMEFOLD_CAMPAIGN_SPENT_LIMIT:-PT3H}"
CAMPAIGN_UNIMPROVED="${TIMEFOLD_CAMPAIGN_UNIMPROVED:-PT15M}"
ROUTE_PLAN_ID="08e70f70-9113-4edc-9bbc-a2adef725950"

if [[ ! -f "$POOL10_OUTPUT" ]]; then
  echo "Error: pool10_required output not found at $POOL10_OUTPUT. Run fetch_pool10_campaign_runs.sh first." >&2
  exit 1
fi
if [[ ! -f "$POOL10_INPUT" ]]; then
  echo "Error: pool10 input not found at $POOL10_INPUT." >&2
  exit 1
fi

echo "=== 1. Build from-patch payload (pin, trim, remove empty) ==="
mkdir -p "$(dirname "$PATCH_OUT")"
python3 "$REPO_ROOT/scripts/continuity/build_from_patch.py" \
  --output "$POOL10_OUTPUT" \
  --input "$POOL10_INPUT" \
  --out "$PATCH_OUT" \
  --no-timestamp

echo "=== 2. Inject long solve time (spentLimit=$CAMPAIGN_SPENT_LIMIT) ==="
python3 -c "
import json
from pathlib import Path
p = Path(\"$PATCH_OUT\")
d = json.loads(p.read_text())
d.setdefault('config', {}).setdefault('run', {})['termination'] = {
    'spentLimit': \"$CAMPAIGN_SPENT_LIMIT\",
    'unimprovedSpentLimit': \"$CAMPAIGN_UNIMPROVED\",
}
p.write_text(json.dumps(d, indent=2, ensure_ascii=False))
print('Set config.run.termination in payload')
"

echo "=== 3. Submit from-patch (--wait, long solve) ==="
cd "$REPO_ROOT"
mkdir -p "$RES"
python3 scripts/timefold/submit.py from-patch "$PATCH_OUT" \
  --route-plan-id "$ROUTE_PLAN_ID" \
  --configuration-id "" \
  --strategy "pool10_from_patch" \
  --dataset huddinge-v3 \
  --wait \
  --save "$RES/pool10_from_patch"

echo "Done. New route plan output saved under $RES/pool10_from_patch. Fetch with --metrics-dir to run metrics and continuity."
