#!/bin/bash
#
# Update OpenClaw and restart the gateway.
# Run manually or via launchd (weekly).
#
# Manual: ./scripts/update-openclaw.sh
# Logs:  logs/update-openclaw.log
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="${SERVICE_ROOT}/logs"
LOG_FILE="${LOG_DIR}/update-openclaw.log"

mkdir -p "$LOG_DIR"

log() {
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG_FILE"
}

# Ensure PATH includes npm/node
export PATH="/opt/homebrew/bin:/opt/homebrew/opt/node@22/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
[[ -f "$HOME/.config/caire/env" ]] && source "$HOME/.config/caire/env" 2>/dev/null || true

log "=== OpenClaw update ==="

BEFORE=$(openclaw --version 2>/dev/null || echo "unknown")
log "Before: $BEFORE"

# npm update is fully non-interactive; openclaw update may prompt (doctor, completion, etc.)
npm update -g openclaw 2>&1 | tee -a "$LOG_FILE"

AFTER=$(openclaw --version 2>/dev/null || echo "unknown")
log "After: $AFTER"

# Ensure gateway is restarted (in case update didn't)
openclaw gateway restart 2>&1 | tee -a "$LOG_FILE"

log "Done. Gateway restarted."
echo ""
