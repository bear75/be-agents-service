#!/bin/bash
#
# Remove the .clawdbot agent directory so the gateway stops using it and stops
# sending the "[clawdbot] No API key found for provider anthropic" error.
# The gateway will use ~/.openclaw only (where auth is configured).
#
# Usage:
#   ./scripts/remove-clawdbot-agent-dir.sh
#
# Then: openclaw gateway restart
#

set -euo pipefail

BASE_HOME="${OPENCLAW_HOME:-$HOME}"
CLAWDBOT_AGENT_DIR="${BASE_HOME}/.clawdbot/agents"
CLAWDBOT_ROOT="${BASE_HOME}/.clawdbot"

echo "Using home: $BASE_HOME"
echo ""

if [[ ! -d "$CLAWDBOT_AGENT_DIR" ]] && [[ ! -d "$CLAWDBOT_ROOT" ]]; then
  echo "ℹ️  No .clawdbot directory found. Nothing to remove."
  exit 0
fi

# Back up then remove
if [[ -d "$CLAWDBOT_ROOT" ]]; then
  BACKUP="${CLAWDBOT_ROOT}.bak.$(date +%Y%m%d-%H%M%S)"
  echo "Moving $CLAWDBOT_ROOT to $BACKUP"
  mv "$CLAWDBOT_ROOT" "$BACKUP"
  echo "✓ Removed .clawdbot (backed up to $BACKUP)"
else
  echo "ℹ️  .clawdbot not found."
fi

echo ""
echo "Restart the gateway so it uses only ~/.openclaw:"
echo "  openclaw gateway restart"
echo ""
