#!/bin/bash
#
# Submit one new v3 run: pool5_preferred (soft pool of 5 per client).
# Aims to balance continuity and efficiency; may improve field efficiency vs pool5_required.
#
# Usage:
#   cd be-agent-service
#   TIMEFOLD_API_KEY="tf_p_96b5507b-..." ./scripts/analytics/submit_pool5_preferred.sh
#   --dry-run  only build input, do not submit
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RECURRING="$SERVICE_ROOT/recurring-visits"
CONTINUITY_SCRIPTS="$SERVICE_ROOT/scripts/continuity"
V3_DIR="$RECURRING/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3"
V3_CONTINUITY="$V3_DIR/continuity"
VARIANTS_DIR="$V3_CONTINUITY/variants"
RESULTS_DIR="$V3_CONTINUITY/results"
BASELINE_OUTPUT="$SCRIPT_DIR/campaign_analysis/baseline_data_final/output.json"
BASE_INPUT="$V3_DIR/input_v3_from_Data_final.json"
BASE_INPUT_NO_TAGS="${V3_DIR}/input_v3_from_Data_final_no_tags.json"

DRY_RUN=false
for arg in "$@"; do [[ "$arg" == "--dry-run" ]] && DRY_RUN=true; done

if [[ ! -f "$BASE_INPUT" ]]; then echo "Error: Base input not found: $BASE_INPUT" >&2; exit 1; fi
if [[ ! -f "$BASELINE_OUTPUT" ]]; then echo "Error: Baseline output not found. Run analyze_job.sh on baseline first." >&2; exit 1; fi
BASE_FOR_PATCH="${BASE_INPUT_NO_TAGS}"
[[ ! -f "$BASE_FOR_PATCH" ]] && BASE_FOR_PATCH="$BASE_INPUT"

echo "[1/2] Building pool5_preferred input..."
mkdir -p "$VARIANTS_DIR"
python3 "$CONTINUITY_SCRIPTS/build_pools.py" \
  --source first-run \
  --input "$BASE_INPUT" \
  --output "$BASELINE_OUTPUT" \
  --out "$VARIANTS_DIR/pools_5.json" \
  --max-per-client 5 \
  --patch-fsr-input "$BASE_FOR_PATCH" \
  --patched-input "$VARIANTS_DIR/input_pool5_preferred.json" \
  --use-preferred
# Strip tags for FSR schema
python3 -c "
import json
p = \"$VARIANTS_DIR/input_pool5_preferred.json\"
with open(p, encoding='utf-8') as f: data = json.load(f)
mi = data.get('modelInput', {})
for v in mi.get('visits') or []: v.pop('tags', None)
for g in mi.get('visitGroups') or []:
  for v in g.get('visits') or []: v.pop('tags', None)
for veh in mi.get('vehicles') or []:
  for s in veh.get('shifts') or []: s.pop('tags', None)
with open(p, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2, ensure_ascii=False)
"
echo "  Written: $VARIANTS_DIR/input_pool5_preferred.json"

if [[ "$DRY_RUN" == "true" ]]; then
  echo "[2/2] Dry-run: skip submit. Input: $VARIANTS_DIR/input_pool5_preferred.json"
  exit 0
fi

if [[ -z "${TIMEFOLD_API_KEY:-}" ]]; then
  echo "Error: Set TIMEFOLD_API_KEY to submit." >&2
  exit 1
fi

SUBMIT_SCRIPT="$RECURRING/scripts/submit_to_timefold.py"
[[ ! -f "$SUBMIT_SCRIPT" ]] && echo "Error: Submit script not found: $SUBMIT_SCRIPT" >&2 && exit 1

echo "[2/2] Submitting pool5_preferred..."
mkdir -p "$RESULTS_DIR/pool5_preferred"
OUT=$(python3 "$SUBMIT_SCRIPT" solve "$VARIANTS_DIR/input_pool5_preferred.json" \
  --api-key "$TIMEFOLD_API_KEY" --skip-validate --no-register-darwin 2>&1) || true
echo "$OUT" > "$RESULTS_DIR/pool5_preferred/submit_stdout.txt"
if echo "$OUT" | grep -q "Route plan ID:"; then
  ID=$(echo "$OUT" | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1)
  echo "  pool5_preferred: $ID"
  echo "After SOLVING_COMPLETED run: ./scripts/analytics/analyze_job.sh $ID --input $BASE_INPUT --out-dir scripts/analytics/campaign_analysis/pool5_preferred"
else
  echo "  Submit failed. See $RESULTS_DIR/pool5_preferred/submit_stdout.txt" >&2
fi
