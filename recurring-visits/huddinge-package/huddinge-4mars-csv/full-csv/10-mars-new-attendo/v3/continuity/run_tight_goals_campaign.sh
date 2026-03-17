#!/usr/bin/env bash
# Submit strategies targeting unassigned <1%, field eff. >75%, continuity <8. All PT3H/PT15M.
# Run from be-agent-service root. Requires TIMEFOLD_API_KEY. See TIGHT_GOALS_ANALYSIS.md.

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
V3="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$V3/../../../../../.." && pwd)"
RES="$V3/continuity/results"
CAMPAIGN_SPENT_LIMIT="${TIMEFOLD_CAMPAIGN_SPENT_LIMIT:-PT3H}"
CAMPAIGN_UNIMPROVED="${TIMEFOLD_CAMPAIGN_UNIMPROVED:-PT15M}"
TIGHT_DIR="$V3/continuity/variants/tight_goals"
PATCH_DIR="$V3/continuity/from_patch"
CA="${REPO_ROOT}/scripts/analytics/campaign_analysis"

mkdir -p "$TIGHT_DIR" "$PATCH_DIR"

echo "=== 1. Build tight-goals variant inputs (PT3H/PT15M) ==="
# pool8_required + termination
python3 -c "
import json
from pathlib import Path
p = Path(\"$V3/continuity/variants/input_pool8_required.json\")
d = json.loads(p.read_text())
run = d.setdefault('config', {}).setdefault('run', {})
run['termination'] = {'spentLimit': \"$CAMPAIGN_SPENT_LIMIT\", 'unimprovedSpentLimit': \"$CAMPAIGN_UNIMPROVED\"}
Path(\"$TIGHT_DIR/input_pool8_required_3h.json\").write_text(json.dumps(d, indent=2, ensure_ascii=False))
print('Wrote input_pool8_required_3h.json')
"

# pool8_preferred + preferVisitVehicleMatchPreferredVehiclesWeight=10 + termination
python3 -c "
import json
from pathlib import Path
p = Path(\"$V3/continuity/variants/input_pool8_preferred.json\")
d = json.loads(p.read_text())
run = d.setdefault('config', {}).setdefault('run', {})
run['termination'] = {'spentLimit': \"$CAMPAIGN_SPENT_LIMIT\", 'unimprovedSpentLimit': \"$CAMPAIGN_UNIMPROVED\"}
ov = d.setdefault('config', {}).setdefault('model', {}).setdefault('overrides', {})
ov['preferVisitVehicleMatchPreferredVehiclesWeight'] = 10
Path(\"$TIGHT_DIR/input_pool8_preferred_w10_3h.json\").write_text(json.dumps(d, indent=2, ensure_ascii=False))
print('Wrote input_pool8_preferred_w10_3h.json')
"

# pool10_eff: pool10 required + travel 5 + wait 5 + termination
python3 -c "
import json
from pathlib import Path
p = Path(\"$V3/continuity/variants/input_pool10_required.json\")
d = json.loads(p.read_text())
run = d.setdefault('config', {}).setdefault('run', {})
run['termination'] = {'spentLimit': \"$CAMPAIGN_SPENT_LIMIT\", 'unimprovedSpentLimit': \"$CAMPAIGN_UNIMPROVED\"}
ov = d.setdefault('config', {}).setdefault('model', {}).setdefault('overrides', {})
ov['minimizeTravelTimeWeight'] = 5
ov['minimizeWaitingTimeWeight'] = 5
Path(\"$TIGHT_DIR/input_pool10_eff_3h.json\").write_text(json.dumps(d, indent=2, ensure_ascii=False))
print('Wrote input_pool10_eff_3h.json')
"

echo "=== 2. Build from-patch payloads (pool8, pool10_from_patch) + termination ==="
# Pool8 from-patch
POOL8_OUT="$CA/pool8_required/output.json"
POOL8_INPUT="$V3/continuity/variants/input_pool8_required.json"
if [[ -f "$POOL8_OUT" ]] && [[ -f "$POOL8_INPUT" ]]; then
  python3 "$REPO_ROOT/scripts/continuity/build_from_patch.py" \
    --output "$POOL8_OUT" --input "$POOL8_INPUT" \
    --out "$PATCH_DIR/pool8_required_patch.json" --no-timestamp
  python3 -c "
import json
from pathlib import Path
p = Path(\"$PATCH_DIR/pool8_required_patch.json\")
d = json.loads(p.read_text())
d.setdefault('config', {}).setdefault('run', {})['termination'] = {'spentLimit': \"$CAMPAIGN_SPENT_LIMIT\", 'unimprovedSpentLimit': \"$CAMPAIGN_UNIMPROVED\"}
p.write_text(json.dumps(d, indent=2, ensure_ascii=False))
print('Set termination on pool8 patch')
"
else
  echo "Skip pool8 from-patch (missing $POOL8_OUT or $POOL8_INPUT)"
fi

# Pool10_from_patch v2
FP10_OUT="$RES/pool10_from_patch/4b5536f2-df02-431a-a7f4-d24fee45ed55_output.json"
if [[ ! -f "$FP10_OUT" ]]; then
  FP10_OUT="$CA/pool10_from_patch/output.json"
fi
POOL10_INPUT="$V3/continuity/variants/input_pool10_required.json"
if [[ -f "$FP10_OUT" ]] && [[ -f "$POOL10_INPUT" ]]; then
  python3 "$REPO_ROOT/scripts/continuity/build_from_patch.py" \
    --output "$FP10_OUT" --input "$POOL10_INPUT" \
    --out "$PATCH_DIR/pool10_from_patch_patch.json" --no-timestamp
  python3 -c "
import json
from pathlib import Path
p = Path(\"$PATCH_DIR/pool10_from_patch_patch.json\")
d = json.loads(p.read_text())
d.setdefault('config', {}).setdefault('run', {})['termination'] = {'spentLimit': \"$CAMPAIGN_SPENT_LIMIT\", 'unimprovedSpentLimit': \"$CAMPAIGN_UNIMPROVED\"}
p.write_text(json.dumps(d, indent=2, ensure_ascii=False))
print('Set termination on pool10_from_patch patch')
"
else
  echo "Skip pool10_from_patch v2 (missing $FP10_OUT or $POOL10_INPUT)"
fi

echo "=== 3. Submit all in parallel (solves + from-patches) ==="
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

submit_solve pool8_required_3h "$TIGHT_DIR/input_pool8_required_3h.json" &
submit_solve pool8_preferred_w10_3h "$TIGHT_DIR/input_pool8_preferred_w10_3h.json" &
submit_solve pool10_eff_3h "$TIGHT_DIR/input_pool10_eff_3h.json" &
submit_from_patch pool8_from_patch_3h "5e55bf3a-9768-4ac8-9a98-d38b857926e4" "$PATCH_DIR/pool8_required_patch.json" &
submit_from_patch pool10_from_patch_v2_3h "4b5536f2-df02-431a-a7f4-d24fee45ed55" "$PATCH_DIR/pool10_from_patch_patch.json" &
wait
echo "Done. Record route plan IDs from output above. Update TIGHT_GOALS_ANALYSIS.md and fetch with --metrics-dir when completed."
echo "Target: unassigned <1%, field eff. >75%, continuity <8."
