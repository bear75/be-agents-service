#!/usr/bin/env bash
# Quick test for schedule research API (used by Telegram/bridge).
# Usage:
#   ./scripts/openclaw/test-schedule-research.sh           # status only
#   ./scripts/openclaw/test-schedule-research.sh --trigger # status + trigger research

set -e

BASE="${SCHEDULE_RESEARCH_API_URL:-http://localhost:3010}"
DATASET="${DATASET:-huddinge-v3}"

echo "=== Schedule research API test ==="
echo "Base URL: $BASE"
echo "Dataset:  $DATASET"
echo ""

# 1. Health / reachability
if ! curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 3 "$BASE/health" 2>/dev/null | grep -q 200; then
  echo "❌ $BASE/health not OK. Start the agent service (e.g. PORT=3010 yarn workspace server dev)."
  exit 1
fi
echo "✅ $BASE/health OK"

# 2. GET status
echo ""
echo "--- GET research state ---"
curl -sS "$BASE/api/schedule-runs/research/state?dataset=$DATASET" | jq . 2>/dev/null || curl -sS "$BASE/api/schedule-runs/research/state?dataset=$DATASET"

# 3. Optional: POST trigger
if [[ "${1:-}" == "--trigger" ]]; then
  echo ""
  echo "--- POST trigger research ---"
  curl -sS -X POST "$BASE/api/schedule-runs/research/trigger" \
    -H "Content-Type: application/json" \
    -d "{\"dataset\":\"$DATASET\",\"max_iterations\":50}" | jq . 2>/dev/null || true
  echo ""
  echo "Trigger sent. Check status again or ask in Telegram: \"How's the schedule research going?\""
fi

echo ""
echo "Done. In Telegram try: \"Start schedule research\" or \"How's the schedule research going?\""
