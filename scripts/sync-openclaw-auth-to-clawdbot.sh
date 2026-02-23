#!/bin/bash
#
# Copy auth from ~/.openclaw to ~/.clawdbot so the gateway finds the API key
# when it uses the .clawdbot agent dir. Run on the Mac mini (as the user in
# the error path) to fix: "No API key found for provider anthropic".
#
# Usage:
#   ./scripts/sync-openclaw-auth-to-clawdbot.sh
#   OPENCLAW_HOME=/Users/bjornevers_MacPro ./scripts/sync-openclaw-auth-to-clawdbot.sh
#

set -euo pipefail

BASE_HOME="${OPENCLAW_HOME:-$HOME}"
OPENCLAW_AGENT="${BASE_HOME}/.openclaw/agents/main/agent"
CLAWDBOT_AGENT="${BASE_HOME}/.clawdbot/agents/main/agent"

echo "Using home: $BASE_HOME"
echo ""

if [[ ! -d "$OPENCLAW_AGENT" ]]; then
  echo "❌ Source not found: $OPENCLAW_AGENT"
  echo "   Configure OpenClaw auth first (e.g. openclaw agents add main, or copy auth-profiles.json into .openclaw/agents/main/agent/)."
  exit 1
fi

mkdir -p "$CLAWDBOT_AGENT"
copied=0

for f in auth-profiles.json auth.json; do
  src="${OPENCLAW_AGENT}/${f}"
  dst="${CLAWDBOT_AGENT}/${f}"
  if [[ -f "$src" ]]; then
    cp -f "$src" "$dst"
    echo "✓ Copied $f → .clawdbot/agents/main/agent/"
    copied=1
  fi
done

if [[ $copied -eq 0 ]]; then
  echo "❌ No auth files found in $OPENCLAW_AGENT"
  echo "   Expected: auth-profiles.json and/or auth.json"
  exit 1
fi

echo ""
echo "Restart the gateway so it picks up the auth:"
echo "  openclaw gateway restart"
echo ""
