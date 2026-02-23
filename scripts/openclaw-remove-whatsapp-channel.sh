#!/bin/bash
#
# Remove WhatsApp from the live OpenClaw config so the gateway stops replying
# to WhatsApp messages (no more "OpenClaw: access not configured" / pairing).
# Run on the machine where OpenClaw runs (e.g. Mac mini).
#
# Usage:
#   ./scripts/openclaw-remove-whatsapp-channel.sh
#   OPENCLAW_HOME=/Users/bjornevers_MacPro ./scripts/openclaw-remove-whatsapp-channel.sh
#

set -euo pipefail

BASE_HOME="${OPENCLAW_HOME:-$HOME}"
OPENCLAW_JSON="${BASE_HOME}/.openclaw/openclaw.json"
CLAWDBOT_JSON="${BASE_HOME}/.clawdbot/moltbot.json"

remove_whatsapp() {
  local path="$1"
  [[ ! -f "$path" ]] && return 0
  if node -e "
    const fs = require('fs');
    const path = process.argv[1];
    const data = JSON.parse(fs.readFileSync(path, 'utf8'));
    if (!data.channels || data.channels.whatsapp === undefined) process.exit(1);
    delete data.channels.whatsapp;
    const channelKeys = Object.keys(data.channels || {});
    if (channelKeys.length === 0) process.exit(2);
    fs.writeFileSync(path, JSON.stringify(data, null, 2));
    const back = JSON.parse(fs.readFileSync(path, 'utf8'));
    if (!back.channels || channelKeys.some(k => !(k in back.channels))) process.exit(3);
    process.exit(0);
  " "$path" 2>/dev/null; then
    echo "✓ Removed whatsapp from $path"
  else
    local exit=$?
    if [[ $exit -eq 2 ]]; then
      echo "  (skipped $path: would leave channels empty; keep at least telegram)"
    elif [[ $exit -eq 3 ]]; then
      echo "  ⚠ Write failed verification for $path"
    else
      echo "  (no whatsapp in $path)"
    fi
  fi
}

echo "Using home: $BASE_HOME"
remove_whatsapp "$OPENCLAW_JSON"
[[ -f "$CLAWDBOT_JSON" ]] && remove_whatsapp "$CLAWDBOT_JSON"
echo ""
echo "Restart the gateway so it stops using WhatsApp:"
echo "  openclaw gateway restart"
echo ""
