#!/usr/bin/env bash
# Generate pool10 weight variants and submit all to Timefold.
# Run from be-agent-service root. Requires TIMEFOLD_API_KEY.
# Overrides default short solve: sets config.run.termination in payload (or use TIMEFOLD_CONFIGURATION_ID for a full-solve profile).
# See POOL10_WEIGHTS_CAMPAIGN.md for full doc and comparison table.

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
V3="$(cd "$SCRIPT_DIR/.." && pwd)"
# Be-agent-service root
REPO_ROOT="$(cd "$V3/../../../../../.." && pwd)"
POOL10_INPUT="$V3/continuity/variants/input_pool10_required.json"
OUT_DIR="$V3/continuity/variants/pool10"
RES="$V3/continuity/results"
# runConfiguration.termination: spentLimit (max solve time) + unimprovedSpentLimit (stop when score unchanged). ISO 8601 (e.g. PT3H, PT15M). Ref config: c522a20a-89c9-4a5b-aca2-46887a254ac7
CAMPAIGN_SPENT_LIMIT="${TIMEFOLD_CAMPAIGN_SPENT_LIMIT:-PT3H}"
CAMPAIGN_UNIMPROVED="${TIMEFOLD_CAMPAIGN_UNIMPROVED:-PT15M}"

if [[ ! -f "$POOL10_INPUT" ]]; then
  echo "Error: $POOL10_INPUT not found. Build pool10 first." >&2
  exit 1
fi

echo "=== 1. Generate variant inputs ==="
mkdir -p "$OUT_DIR"
python3 "$REPO_ROOT/recurring-visits/scripts/prepare_continuity_test_variants.py" \
  --input "$POOL10_INPUT" \
  --out-dir "$OUT_DIR" \
  --preferred-weights 2 10 20

echo "=== 2. Add travel variant (optional) ==="
python3 -c "
import json
from pathlib import Path
out_dir = Path(\"$OUT_DIR\")
p = out_dir / 'input_wait_min_weight3.json'
if p.exists():
    d = json.loads(p.read_text())
    overrides = d.setdefault('config', {}).setdefault('model', {}).setdefault('overrides', {})
    overrides['minimizeWaitingTimeWeight'] = 1
    overrides['minimizeTravelTimeWeight'] = 5
    (out_dir / 'input_travel_weight5.json').write_text(json.dumps(d, indent=2, ensure_ascii=False))
    print('Wrote input_travel_weight5.json')
"

echo "=== 3. Set campaign solve time in all payloads (spentLimit=$CAMPAIGN_SPENT_LIMIT) ==="
set_termination() {
  local f="$1"
  python3 -c "
import json, sys
p = \"$f\"
with open(p) as f: d = json.load(f)
run = d.setdefault('config', {}).setdefault('run', {})
term = run.setdefault('termination', {})
term['spentLimit'] = \"$CAMPAIGN_SPENT_LIMIT\"
term['unimprovedSpentLimit'] = \"$CAMPAIGN_UNIMPROVED\"
with open(p, 'w') as f: json.dump(d, f, indent=2, ensure_ascii=False)
print('Set termination:', p)
"
}
set_termination "$POOL10_INPUT"
for f in "$OUT_DIR"/input_*.json; do set_termination "$f"; done

echo "=== 4. Submit all variants in parallel (no-wait) ==="
cd "$REPO_ROOT"
mkdir -p "$RES"
submit_one() {
  local name="$1" file="$2"
  if [[ ! -f "$file" ]]; then echo "Skip $name (missing $file)"; return 0; fi
  echo "Submitting $name (config in payload: spentLimit=$CAMPAIGN_SPENT_LIMIT)..."
  python3 scripts/timefold/submit.py solve "$file" \
    --configuration-id "" --strategy "$name" --dataset huddinge-v3 \
    --save "$RES/$name"
}
submit_one pool10_required "$V3/continuity/variants/input_pool10_required.json" &
submit_one pool10_preferred_w2 "$OUT_DIR/input_preferred_vehicles_weight2.json" &
submit_one pool10_preferred_w10 "$OUT_DIR/input_preferred_vehicles_weight10.json" &
submit_one pool10_preferred_w20 "$OUT_DIR/input_preferred_vehicles_weight20.json" &
submit_one pool10_wait_min "$OUT_DIR/input_wait_min_weight3.json" &
submit_one pool10_combo "$OUT_DIR/input_combo_preferred_and_wait_min.json" &
submit_one pool10_travel "$OUT_DIR/input_travel_weight5.json" &
wait
echo "Done. Record route plan IDs from output above, then fetch and analyze (see POOL10_WEIGHTS_CAMPAIGN.md)."
