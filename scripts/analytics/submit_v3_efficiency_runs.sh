#!/bin/bash
#
# Submit new v3 runs aimed at field efficiency >75%.
# Creates: pool10_required (more capacity per client), pool8_preferred (soft pool to reduce travel).
# Uses test tenant API key for campaign consistency.
#
# Usage:
#   cd be-agent-service
#   TIMEFOLD_API_KEY="tf_p_96b5507b-..." ./scripts/analytics/submit_v3_efficiency_runs.sh
#
# Optional: --dry-run to only build inputs, no submit.
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
POOL8_INPUT="$VARIANTS_DIR/input_pool8_required.json"

DRY_RUN=false
for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

if [[ ! -f "$BASE_INPUT" ]]; then
  echo "Error: Base input not found: $BASE_INPUT" >&2
  exit 1
fi
# Use no-tags base for pool10 so patched input is FSR schema compliant
if [[ ! -f "$BASE_INPUT_NO_TAGS" ]]; then
  echo "Warning: No-tags base not found, using base input (may fail submit if visits have tags): $BASE_INPUT_NO_TAGS" >&2
  BASE_FOR_POOL10="$BASE_INPUT"
else
  BASE_FOR_POOL10="$BASE_INPUT_NO_TAGS"
fi
if [[ ! -f "$BASELINE_OUTPUT" ]]; then
  echo "Error: Baseline output required for pool10 (first-run pools). Run analyze_job.sh on baseline first. Path: $BASELINE_OUTPUT" >&2
  exit 1
fi
if [[ ! -f "$POOL8_INPUT" ]]; then
  echo "Error: Pool8 input not found: $POOL8_INPUT" >&2
  exit 1
fi

# 1) Build pool10 input from baseline (first-run pools, max 10 per client). Use no-tags base so submit succeeds.
echo "[1/3] Building pool10_required input from baseline first-run..."
mkdir -p "$VARIANTS_DIR"
python3 "$CONTINUITY_SCRIPTS/build_pools.py" \
  --source first-run \
  --input "$BASE_INPUT" \
  --output "$BASELINE_OUTPUT" \
  --out "$VARIANTS_DIR/pools_10.json" \
  --max-per-client 10 \
  --patch-fsr-input "$BASE_FOR_POOL10" \
  --patched-input "$VARIANTS_DIR/input_pool10_required.json"
echo "  Written: $VARIANTS_DIR/input_pool10_required.json"
# Strip tags from pool10 if present (FSR schema does not allow tags on visits)
python3 -c "
import json
p = \"$VARIANTS_DIR/input_pool10_required.json\"
with open(p, encoding='utf-8') as f: data = json.load(f)
mi = data.get('modelInput', {})
for v in mi.get('visits') or []: v.pop('tags', None)
for g in mi.get('visitGroups') or []:
  for v in g.get('visits') or []: v.pop('tags', None)
for veh in mi.get('vehicles') or []:
  for s in veh.get('shifts') or []: s.pop('tags', None)
with open(p, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2, ensure_ascii=False)
" 2>/dev/null || true

# 2) Build pool8_preferred: same as pool8 but preferredVehicles instead of requiredVehicles; strip tags for FSR schema
echo "[2/3] Building pool8_preferred input..."
python3 - "$POOL8_INPUT" "$VARIANTS_DIR/input_pool8_preferred.json" << 'PY'
import json, sys
def strip_tags(obj):
    if isinstance(obj, dict):
        obj.pop("tags", None)
        for k, v in obj.items():
            strip_tags(v)
    elif isinstance(obj, list):
        for x in obj:
            strip_tags(x)
with open(sys.argv[1], "r", encoding="utf-8") as f:
    data = json.load(f)
mi = data.get("modelInput", {})
for v in mi.get("visits") or []:
    if "requiredVehicles" in v:
        v["preferredVehicles"] = v.pop("requiredVehicles")
    v.pop("tags", None)
for g in mi.get("visitGroups") or []:
    for v in g.get("visits") or []:
        if "requiredVehicles" in v:
            v["preferredVehicles"] = v.pop("requiredVehicles")
        v.pop("tags", None)
for veh in mi.get("vehicles") or []:
    for s in veh.get("shifts") or []:
        s.pop("tags", None)
with open(sys.argv[2], "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("  Written: " + sys.argv[2])
PY

# 3) Submit both (unless --dry-run)
if [[ "$DRY_RUN" == "true" ]]; then
  echo "[3/3] Dry-run: skip submit. Inputs ready: input_pool10_required.json, input_pool8_preferred.json"
  exit 0
fi

if [[ -z "${TIMEFOLD_API_KEY:-}" ]]; then
  echo "Error: Set TIMEFOLD_API_KEY (e.g. test tenant tf_p_96b5507b-...) to submit." >&2
  exit 1
fi

SUBMIT_SCRIPT="$RECURRING/scripts/submit_to_timefold.py"
if [[ ! -f "$SUBMIT_SCRIPT" ]]; then
  echo "Error: Submit script not found: $SUBMIT_SCRIPT" >&2
  exit 1
fi

echo "[3/3] Submitting to Timefold (test tenant)..."
mkdir -p "$RESULTS_DIR/pool10_required" "$RESULTS_DIR/pool8_preferred"

ID_POOL10=""
ID_POOL8P=""

# Submit pool10_required
OUT_POOL10=$(python3 "$SUBMIT_SCRIPT" solve "$VARIANTS_DIR/input_pool10_required.json" \
  --api-key "$TIMEFOLD_API_KEY" \
  --skip-validate \
  --no-register-darwin 2>&1) || true
if echo "$OUT_POOL10" | grep -q "Route plan ID:"; then
  ID_POOL10=$(echo "$OUT_POOL10" | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1)
  echo "$OUT_POOL10" > "$RESULTS_DIR/pool10_required/submit_stdout.txt"
  echo "  pool10_required: $ID_POOL10"
else
  echo "  pool10_required submit failed: $OUT_POOL10" >&2
fi

# Submit pool8_preferred
OUT_POOL8P=$(python3 "$SUBMIT_SCRIPT" solve "$VARIANTS_DIR/input_pool8_preferred.json" \
  --api-key "$TIMEFOLD_API_KEY" \
  --skip-validate \
  --no-register-darwin 2>&1) || true
if echo "$OUT_POOL8P" | grep -q "Route plan ID:"; then
  ID_POOL8P=$(echo "$OUT_POOL8P" | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1)
  echo "$OUT_POOL8P" > "$RESULTS_DIR/pool8_preferred/submit_stdout.txt"
  echo "  pool8_preferred:  $ID_POOL8P"
else
  echo "  pool8_preferred submit failed: $OUT_POOL8P" >&2
fi

# Manifest for later analysis
MANIFEST="$SCRIPT_DIR/campaign_analysis/efficiency_runs_manifest.md"
BASE_REL="recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_from_Data_final.json"
{
  echo "# Efficiency runs (goal >75% field efficiency)"
  echo ""
  echo "| Variant | Route Plan ID | Status |"
  echo "|---------|---------------|--------|"
  echo "| pool10_required | ${ID_POOL10:-—} | SUBMITTED |"
  echo "| pool8_preferred | ${ID_POOL8P:-—} | SUBMITTED |"
  echo ""
  echo "After SOLVING_COMPLETED, run (from be-agent-service):"
  echo "  ./scripts/analytics/analyze_job.sh $ID_POOL10 --input $BASE_REL --out-dir scripts/analytics/campaign_analysis/pool10_required"
  echo "  ./scripts/analytics/analyze_job.sh $ID_POOL8P --input $BASE_REL --out-dir scripts/analytics/campaign_analysis/pool8_preferred"
} > "$MANIFEST"
echo "Written: $MANIFEST"
