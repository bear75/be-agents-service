#!/usr/bin/env bash
# Generate 15 overnight variants (preferred pools, P/W/T weight balance) and submit all to Timefold (no --wait). Queue before bed, analyze in the morning.
# Run from be-agent-service root. Requires TIMEFOLD_API_KEY. See OVERNIGHT_CAMPAIGNS.md.

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
V3="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$V3/../../../../../.." && pwd)"
POOL10_INPUT="$V3/continuity/variants/input_pool10_required.json"
POOL8_INPUT="$V3/continuity/variants/input_pool8_preferred.json"
OUT_DIR="$V3/continuity/variants/overnight"
RES="$V3/continuity/results"
MANIFEST="$V3/continuity/overnight_manifest.md"
CAMPAIGN_SPENT_LIMIT="${TIMEFOLD_CAMPAIGN_SPENT_LIMIT:-PT3H}"
CAMPAIGN_UNIMPROVED="${TIMEFOLD_CAMPAIGN_UNIMPROVED:-PT15M}"

if [[ ! -f "$POOL10_INPUT" ]]; then
  echo "Error: $POOL10_INPUT not found." >&2
  exit 1
fi
if [[ ! -f "$POOL8_INPUT" ]]; then
  echo "Error: $POOL8_INPUT not found." >&2
  exit 1
fi

echo "=== 1. Generate 15 overnight variant JSONs (preferred only, P/W/T balance) ==="
python3 "$V3/continuity/generate_overnight_variants.py" \
  --pool10-input "$POOL10_INPUT" \
  --pool8-input "$POOL8_INPUT" \
  --out-dir "$OUT_DIR" \
  --spent-limit "$CAMPAIGN_SPENT_LIMIT" \
  --unimproved "$CAMPAIGN_UNIMPROVED"

echo "=== 2. Submit all to Timefold (no --wait; they will queue) ==="
cd "$REPO_ROOT"
mkdir -p "$RES"
{
  echo "## Overnight campaign runs — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "| Strategy | Route plan ID | Status |"
  echo "|----------|---------------|--------|"
} > "$MANIFEST"

for f in "$OUT_DIR"/*.json; do
  [[ -f "$f" ]] || continue
  name="$(basename "$f" .json)"
  echo "Submitting $name..."
  out=$(python3 scripts/timefold/submit.py solve "$f" \
    --configuration-id "" --strategy "$name" --dataset huddinge-v3 \
    --save "$RES/$name" 2>&1) || true
  id=""
  if echo "$out" | grep -q "Route plan ID:"; then
    id=$(echo "$out" | grep "Route plan ID:" | sed 's/.*Route plan ID: *//' | tr -d '\r\n ')
  fi
  echo "| $name | ${id:-—} | SOLVING_SCHEDULED |" >> "$MANIFEST"
done

echo ""
echo "Done. All 15 submitted to queue. Manifest: $MANIFEST"
echo "In the morning: check status, then fetch with a script that reads the manifest and runs fetch_timefold_solution.py for each ID with --metrics-dir. Target: eff >80%, continuity 6–10."
