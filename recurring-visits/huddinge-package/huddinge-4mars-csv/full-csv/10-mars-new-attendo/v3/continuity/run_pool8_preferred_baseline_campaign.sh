#!/usr/bin/env bash
# New variants from pool8_preferred_w10_3h baseline (76.52% eff, 3.70 continuity).
# Run from be-agent-service root. Requires TIMEFOLD_API_KEY. See POOL8_PREFERRED_BASELINE_CAMPAIGN.md.

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
V3="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$V3/../../../../../.." && pwd)"
RES="$V3/continuity/results"
CAMPAIGN_SPENT_LIMIT="${TIMEFOLD_CAMPAIGN_SPENT_LIMIT:-PT3H}"
CAMPAIGN_UNIMPROVED="${TIMEFOLD_CAMPAIGN_UNIMPROVED:-PT15M}"
BASELINE_DIR="$V3/continuity/variants/pool8_preferred_baseline"
PATCH_DIR="$V3/continuity/from_patch"
CA="${REPO_ROOT}/scripts/analytics/campaign_analysis"

# Baseline output: pool8_preferred_w10_3h (c52a3d44)
BASELINE_OUTPUT="$CA/pool8_preferred_w10_3h/output.json"
BASELINE_ROUTE_ID="c52a3d44-0141-4b10-8f33-b4fc942e8f15"
POOL8_INPUT="$V3/continuity/variants/input_pool8_preferred.json"

mkdir -p "$BASELINE_DIR" "$PATCH_DIR"

echo "=== 1. Build variant inputs from pool8_preferred_w10_3h baseline ==="

# pool8_preferred_w15_3h — preferred weight 15
python3 -c "
import json
from pathlib import Path
p = Path(\"$POOL8_INPUT\")
d = json.loads(p.read_text())
run = d.setdefault('config', {}).setdefault('run', {})
run['termination'] = {'spentLimit': \"$CAMPAIGN_SPENT_LIMIT\", 'unimprovedSpentLimit': \"$CAMPAIGN_UNIMPROVED\"}
ov = d.setdefault('config', {}).setdefault('model', {}).setdefault('overrides', {})
ov['preferVisitVehicleMatchPreferredVehiclesWeight'] = 15
Path(\"$BASELINE_DIR/input_pool8_preferred_w15_3h.json\").write_text(json.dumps(d, indent=2, ensure_ascii=False))
print('Wrote input_pool8_preferred_w15_3h.json')
"

# pool8_preferred_w20_3h — preferred weight 20
python3 -c "
import json
from pathlib import Path
p = Path(\"$POOL8_INPUT\")
d = json.loads(p.read_text())
run = d.setdefault('config', {}).setdefault('run', {})
run['termination'] = {'spentLimit': \"$CAMPAIGN_SPENT_LIMIT\", 'unimprovedSpentLimit': \"$CAMPAIGN_UNIMPROVED\"}
ov = d.setdefault('config', {}).setdefault('model', {}).setdefault('overrides', {})
ov['preferVisitVehicleMatchPreferredVehiclesWeight'] = 20
Path(\"$BASELINE_DIR/input_pool8_preferred_w20_3h.json\").write_text(json.dumps(d, indent=2, ensure_ascii=False))
print('Wrote input_pool8_preferred_w20_3h.json')
"

# pool8_preferred_w10_eff_3h — add travel+wait weights for efficiency
python3 -c "
import json
from pathlib import Path
p = Path(\"$POOL8_INPUT\")
d = json.loads(p.read_text())
run = d.setdefault('config', {}).setdefault('run', {})
run['termination'] = {'spentLimit': \"$CAMPAIGN_SPENT_LIMIT\", 'unimprovedSpentLimit': \"$CAMPAIGN_UNIMPROVED\"}
ov = d.setdefault('config', {}).setdefault('model', {}).setdefault('overrides', {})
ov['preferVisitVehicleMatchPreferredVehiclesWeight'] = 10
ov['minimizeTravelTimeWeight'] = 5
ov['minimizeWaitingTimeWeight'] = 5
Path(\"$BASELINE_DIR/input_pool8_preferred_w10_eff_3h.json\").write_text(json.dumps(d, indent=2, ensure_ascii=False))
print('Wrote input_pool8_preferred_w10_eff_3h.json')
"

echo "=== 2. Build from-patch payload (pool8_preferred_w10_3h output) ==="
if [[ -f "$BASELINE_OUTPUT" ]] && [[ -f "$POOL8_INPUT" ]]; then
  python3 "$REPO_ROOT/scripts/continuity/build_from_patch.py" \
    --output "$BASELINE_OUTPUT" --input "$POOL8_INPUT" \
    --out "$PATCH_DIR/pool8_preferred_w10_patch.json" --no-timestamp
  python3 -c "
import json
from pathlib import Path
p = Path(\"$PATCH_DIR/pool8_preferred_w10_patch.json\")
d = json.loads(p.read_text())
d.setdefault('config', {}).setdefault('run', {})['termination'] = {'spentLimit': \"$CAMPAIGN_SPENT_LIMIT\", 'unimprovedSpentLimit': \"$CAMPAIGN_UNIMPROVED\"}
p.write_text(json.dumps(d, indent=2, ensure_ascii=False))
print('Set termination on pool8_preferred_w10 patch')
"
else
  echo "Skip from-patch (missing $BASELINE_OUTPUT or $POOL8_INPUT)"
fi

echo "=== 3. Submit all in parallel ==="
cd "$REPO_ROOT"
mkdir -p "$RES"

submit_solve() {
  local name="$1" file="$2"
  if [[ ! -f "$file" ]]; then echo "Skip $name (missing $file)"; return 0; fi
  echo "Submitting solve $name..."
  python3 scripts/timefold/submit.py solve "$file" \
    --configuration-id "" --strategy "$name" --dataset huddinge-v3 \
    --save "$RES/$name"
}
submit_from_patch() {
  local name="$1" route_id="$2" patch_file="$3"
  if [[ ! -f "$patch_file" ]]; then echo "Skip $name (missing $patch_file)"; return 0; fi
  echo "Submitting from-patch $name -> $route_id..."
  python3 scripts/timefold/submit.py from-patch "$patch_file" \
    --route-plan-id "$route_id" --configuration-id "" \
    --strategy "$name" --dataset huddinge-v3 \
    --save "$RES/$name"
}

submit_solve pool8_preferred_w15_3h "$BASELINE_DIR/input_pool8_preferred_w15_3h.json" &
submit_solve pool8_preferred_w20_3h "$BASELINE_DIR/input_pool8_preferred_w20_3h.json" &
submit_solve pool8_preferred_w10_eff_3h "$BASELINE_DIR/input_pool8_preferred_w10_eff_3h.json" &
submit_from_patch pool8_preferred_w10_from_patch_3h "$BASELINE_ROUTE_ID" "$PATCH_DIR/pool8_preferred_w10_patch.json" &
wait
echo "Done. Record route plan IDs from output above. Update fetch_pool8_preferred_baseline.sh and run build_campaign_summary.py when completed."
