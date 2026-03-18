#!/usr/bin/env bash
# Fetch all tight-goals campaign runs and run metrics + continuity. Run from be-agent-service root.
# Requires TIMEFOLD_API_KEY. See TIGHT_GOALS_ANALYSIS.md.

set -e
REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$REPO_ROOT"
V3_INPUT="${REPO_ROOT}/recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_from_Data_final_no_tags.json"
[[ ! -f "$V3_INPUT" ]] && V3_INPUT="${REPO_ROOT}/recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_from_Data_final.json"
CAMPAIGN_DIR="${REPO_ROOT}/scripts/analytics/campaign_analysis"
FETCH_SCRIPT="${REPO_ROOT}/recurring-visits/scripts/fetch_timefold_solution.py"
if [[ ! -f "$FETCH_SCRIPT" ]] || [[ ! -f "$V3_INPUT" ]]; then
  echo "Error: fetch script or v3 input not found." >&2
  exit 1
fi

fetch_one() {
  local variant="$1" id="$2"
  out_dir="${CAMPAIGN_DIR}/${variant}"
  mkdir -p "$out_dir"
  echo "Fetching $variant ($id)..."
  python3 "$FETCH_SCRIPT" "$id" --save "$out_dir/output.json" --input "$V3_INPUT" --metrics-dir "$out_dir" || true
}

cd "$(dirname "$FETCH_SCRIPT")"
fetch_one pool8_required_3h "76b02f06-a74f-4ff6-a95e-fbf87d6e6d07"
fetch_one pool8_preferred_w10_3h "c52a3d44-0141-4b10-8f33-b4fc942e8f15"
fetch_one pool10_eff_3h "709eaa15-2bd6-47bd-b9b6-a7e1ad14ea18"
fetch_one pool8_from_patch_3h "769f8146-b250-43ad-ab03-201a2442612b"
fetch_one pool10_from_patch_v2_3h "17db45c7-985b-43ef-9e8e-77a3352509f4"
echo "Done. Run build_campaign_summary.py to regenerate SUMMARY.md. Target: eff >80%, continuity 6–10; some unassigned OK for manual handling."
