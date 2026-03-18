#!/usr/bin/env bash
# Fetch all overnight campaign runs from overnight_manifest.md and run metrics + continuity. Run in the morning from be-agent-service root.
# Requires TIMEFOLD_API_KEY. See OVERNIGHT_CAMPAIGNS.md.

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
V3="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$V3/../../../../../.." && pwd)"
MANIFEST="$V3/continuity/overnight_manifest.md"
V3_INPUT="${REPO_ROOT}/recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_from_Data_final_no_tags.json"
[[ ! -f "$V3_INPUT" ]] && V3_INPUT="${REPO_ROOT}/recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_from_Data_final.json"
CAMPAIGN_DIR="${REPO_ROOT}/scripts/analytics/campaign_analysis"
FETCH_SCRIPT="${REPO_ROOT}/recurring-visits/scripts/fetch_timefold_solution.py"

if [[ ! -f "$MANIFEST" ]]; then
  echo "Error: $MANIFEST not found. Run run_overnight_campaigns.sh first." >&2
  exit 1
fi
if [[ ! -f "$FETCH_SCRIPT" ]] || [[ ! -f "$V3_INPUT" ]]; then
  echo "Error: fetch script or v3 input not found." >&2
  exit 1
fi

cd "$(dirname "$FETCH_SCRIPT")"
# Parse markdown table: | name | uuid | status |
while IFS='|' read -r _ name id status _; do
  name=$(echo "$name" | tr -d ' ')
  id=$(echo "$id" | tr -d ' ')
  [[ -z "$name" || "$name" == "Strategy" || "$name" == "---" ]] && continue
  [[ -z "$id" || "$id" == "—" || "$id" == "Route plan ID" ]] && continue
  out_dir="${CAMPAIGN_DIR}/${name}"
  mkdir -p "$out_dir"
  echo "Fetching $name ($id)..."
  python3 "$FETCH_SCRIPT" "$id" --save "$out_dir/output.json" --input "$V3_INPUT" --metrics-dir "$out_dir" || true
done < <(grep '^|' "$MANIFEST" | tail -n +4)
echo "Done. Run build_campaign_summary.py (add overnight strategy names to VARIANTS if needed) to regenerate SUMMARY.md."
