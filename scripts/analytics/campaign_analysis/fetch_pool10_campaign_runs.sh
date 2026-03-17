#!/usr/bin/env bash
# Fetch all Pool 10 campaign runs from Timefold API and run metrics + continuity.
# Run from be-agent-service root. Requires TIMEFOLD_API_KEY.
#
# Usage: ./scripts/analytics/campaign_analysis/fetch_pool10_campaign_runs.sh

set -e
REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$REPO_ROOT"

V3_INPUT="${REPO_ROOT}/recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_from_Data_final_no_tags.json"
if [[ ! -f "$V3_INPUT" ]]; then
  V3_INPUT="${REPO_ROOT}/recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_from_Data_final.json"
fi
CAMPAIGN_DIR="${REPO_ROOT}/scripts/analytics/campaign_analysis"
FETCH_SCRIPT="${REPO_ROOT}/recurring-visits/scripts/fetch_timefold_solution.py"

if [[ ! -f "$FETCH_SCRIPT" ]]; then
  echo "Error: $FETCH_SCRIPT not found. Run from be-agent-service root." >&2
  exit 1
fi
if [[ ! -f "$V3_INPUT" ]]; then
  echo "Error: v3 input not found at $V3_INPUT" >&2
  exit 1
fi

fetch_one() {
  local variant="$1" id="$2"
  out_dir="${CAMPAIGN_DIR}/${variant}"
  mkdir -p "$out_dir"
  echo "Fetching $variant ($id)..."
  python3 "$FETCH_SCRIPT" "$id" \
    --save "$out_dir/output.json" \
    --input "$V3_INPUT" \
    --metrics-dir "$out_dir" || true
}

cd "$(dirname "$FETCH_SCRIPT")"
fetch_one pool10_required "08e70f70-9113-4edc-9bbc-a2adef725950"
fetch_one pool10_preferred_w2 "2f8ff28c-3ce5-4e00-9e8c-c09d50558d51"
fetch_one pool10_preferred_w10 "2b2fef45-2e40-4dfd-b546-19ab0bcbef91"
fetch_one pool10_preferred_w20 "67ab318e-e0d0-4982-9ae2-844d2e32635a"
fetch_one pool10_wait_min "f2fac40b-f6d1-4103-97ee-d10cb22129da"
fetch_one pool10_combo "1391e3d9-aba6-45c9-8154-f0d609e64398"
fetch_one pool10_travel "b7ba5473-6701-4215-9487-28296c64a5e6"
echo "Done. Run build_campaign_summary.py to regenerate SUMMARY.md."
echo "Update campaign_manifest.md Pool10 status to SOLVING_COMPLETED."
