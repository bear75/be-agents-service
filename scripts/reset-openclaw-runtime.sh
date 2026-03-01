#!/usr/bin/env bash
#
# Hard reset OpenClaw runtime on macOS for Telegram inbound reliability.
# Fixes common failure loop:
# - legacy config keys (agent.*)
# - stale launchd jobs (com.appcaire.openclaw / com.appcaire.update-openclaw)
# - mismatched gateway token/runtime state
#
# Usage:
#   ./scripts/reset-openclaw-runtime.sh <owner-id> [second-id]
# Example:
#   ./scripts/reset-openclaw-runtime.sh 8399128208 7604480012
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$HOME/.config/caire/env"
CONFIG_TEMPLATE="$SERVICE_ROOT/config/openclaw/openclaw.json"
RUNTIME_CONFIG="$HOME/.openclaw/openclaw.json"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"

OWNER_ID="${1:-}"
SECOND_ID="${2:-}"

log() { echo "[reset-openclaw] $*"; }
warn() { echo "[reset-openclaw] WARNING: $*"; }
fail() { echo "[reset-openclaw] ERROR: $*" >&2; exit 1; }

[[ -n "$OWNER_ID" ]] || fail "Usage: $0 <owner-id> [second-id]"
[[ -f "$CONFIG_TEMPLATE" ]] || fail "Missing template: $CONFIG_TEMPLATE"
command -v openclaw >/dev/null 2>&1 || fail "openclaw CLI is required"
command -v jq >/dev/null 2>&1 || fail "jq is required"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck source=/dev/null
  source "$ENV_FILE" || true
fi

[[ -n "${TELEGRAM_BOT_TOKEN:-}" ]] || fail "TELEGRAM_BOT_TOKEN is required in $ENV_FILE"

uid="$(id -u)"

bootout_if_loaded() {
  local label="$1"
  if launchctl list 2>/dev/null | grep -Fq "$label"; then
    log "Bootout launchd job: $label"
    launchctl bootout "gui/$uid/$label" 2>/dev/null || true
  fi
}

# Remove stale jobs that frequently conflict with ai.openclaw.gateway
bootout_if_loaded "com.appcaire.openclaw"
bootout_if_loaded "com.appcaire.update-openclaw"
bootout_if_loaded "ai.openclaw.gateway"

rm -f "$LAUNCH_AGENTS/com.appcaire.openclaw.plist" "$LAUNCH_AGENTS/com.appcaire.update-openclaw.plist" 2>/dev/null || true

mkdir -p "$HOME/.openclaw"
cp "$CONFIG_TEMPLATE" "$RUNTIME_CONFIG"
log "Copied runtime config template to $RUNTIME_CONFIG"

ids=("$OWNER_ID")
if [[ -n "$SECOND_ID" ]]; then
  ids+=("$SECOND_ID")
fi
ids_json="$(printf '%s\n' "${ids[@]}" | jq -R . | jq -s .)"

openclaw config set channels.telegram.enabled true >/dev/null
openclaw config set channels.telegram.botToken "$TELEGRAM_BOT_TOKEN" >/dev/null
openclaw config set channels.telegram.allowFrom "$ids_json" >/dev/null
openclaw config set gateway.mode local >/dev/null

# Let doctor repair and regenerate launch agent using current config
openclaw doctor --fix >/dev/null || true

if grep -qE '^\s*agent:\s*' "$RUNTIME_CONFIG"; then
  warn "Legacy key detected after doctor; forcing modern template once more"
  cp "$CONFIG_TEMPLATE" "$RUNTIME_CONFIG"
  openclaw config set channels.telegram.enabled true >/dev/null
  openclaw config set channels.telegram.botToken "$TELEGRAM_BOT_TOKEN" >/dev/null
  openclaw config set channels.telegram.allowFrom "$ids_json" >/dev/null
  openclaw config set gateway.mode local >/dev/null
fi

log "Restarting OpenClaw gateway"
if ! openclaw gateway restart >/dev/null; then
  warn "gateway restart returned non-zero; trying stop/start"
  openclaw gateway stop >/dev/null 2>&1 || true
  openclaw gateway start >/dev/null || true
fi

sleep 2

if ! lsof -nP -iTCP:18789 -sTCP:LISTEN >/dev/null 2>&1; then
  warn "Gateway not listening on 18789"
  warn "Check runtime errors:"
  warn "  ~/.openclaw/logs/gateway.err.log"
  warn "  /tmp/openclaw/openclaw-*.log"
  exit 1
fi

log "Gateway is listening on 18789"

if [[ -x "$SERVICE_ROOT/scripts/notifications/send-telegram-test.sh" ]]; then
  log "Sending Telegram test to configured IDs"
  "$SERVICE_ROOT/scripts/notifications/send-telegram-test.sh" --ids "${ids[@]}" --label "openclaw-runtime-reset"
fi

log "OpenClaw runtime reset complete"
