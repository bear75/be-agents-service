#!/usr/bin/env bash
# Fetch all v3 campaign runs from Timefold API and run metrics + continuity.
# Run from be-agent-service root. Requires TIMEFOLD_API_KEY (e.g. test tenant).
#
# Usage: ./scripts/analytics/campaign_analysis/fetch_all_campaign_runs.sh

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
  python3 fetch_timefold_solution.py "$id" \
    --save "$out_dir/output.json" \
    --input "$V3_INPUT" \
    --metrics-dir "$out_dir" || true
}

cd "$(dirname "$FETCH_SCRIPT")"
fetch_one baseline_data_final "cf407218-27c7-4603-b797-32e373b7e53c"
fetch_one pool3_required "c1ea12a5-4507-4d9d-8d2c-3f70ac1e2685"
fetch_one pool5_required "d87e9a1a-ee5a-489a-bb07-f3c95cbe3b73"
fetch_one pool8_required "5e55bf3a-9768-4ac8-9a98-d38b857926e4"
echo "Done. Run build_campaign_summary.py to regenerate SUMMARY.md."
