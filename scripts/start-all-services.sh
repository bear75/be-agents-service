#!/usr/bin/env bash
# Start Darwin/OpenClaw/compound services on macOS and verify health.
#
# Usage:
#   ./scripts/start-all-services.sh
#   ./scripts/start-all-services.sh --send-telegram-test
#   ./scripts/start-all-services.sh --skip-verify

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LAUNCHD_SRC="$SERVICE_ROOT/launchd"
LAUNCHD_DST="$HOME/Library/LaunchAgents"
ENV_FILE="$HOME/.config/caire/env"

SKIP_VERIFY=false
SEND_TELEGRAM_TEST=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-verify)
      SKIP_VERIFY=true
      shift
      ;;
    --send-telegram-test)
      SEND_TELEGRAM_TEST=true
      shift
      ;;
    -h|--help)
      cat <<'EOF'
Usage: ./scripts/start-all-services.sh [options]

Options:
  --send-telegram-test   Run Telegram send test in verification step
  --skip-verify          Skip verify-all-services.sh after startup
  -h, --help             Show this help
EOF
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

log() { echo "[start-all-services] $*"; }
warn() { echo "[start-all-services] ⚠️  $*"; }

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "[start-all-services] ❌ This script is intended for macOS (launchd)." >&2
  exit 1
fi

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck source=/dev/null
  source "$ENV_FILE" || true
  log "Loaded env: $ENV_FILE"
else
  warn "Env file not found: $ENV_FILE"
fi

mkdir -p "$LAUNCHD_DST"
cp "$LAUNCHD_SRC"/com.appcaire.*.plist "$LAUNCHD_DST"/
log "Copied com.appcaire launchd plists to $LAUNCHD_DST"

JOBS=(
  "com.appcaire.agent-server"
  "com.appcaire.caffeinate"
  "com.appcaire.daily-compound-review"
  "com.appcaire.auto-compound"
  "com.appcaire.morning-briefing"
  "com.appcaire.weekly-review"
)

for job in "${JOBS[@]}"; do
  plist="$LAUNCHD_DST/$job.plist"
  if [[ -f "$plist" ]]; then
    launchctl unload "$plist" 2>/dev/null || true
    if launchctl load "$plist" 2>/dev/null; then
      log "Loaded: $job"
    else
      warn "Failed to load: $job"
    fi
  else
    warn "Missing plist: $plist"
  fi
done

if command -v openclaw >/dev/null 2>&1; then
  if [[ -f "$HOME/.openclaw/openclaw.json" ]]; then
    if openclaw gateway restart >/dev/null 2>&1; then
      log "OpenClaw gateway restarted"
    else
      warn "OpenClaw gateway restart failed"
    fi
  else
    warn "OpenClaw config missing: $HOME/.openclaw/openclaw.json"
  fi
else
  warn "OpenClaw CLI not installed (skip gateway restart)"
fi

if [[ "$SKIP_VERIFY" == "false" ]]; then
  log "Running verification..."
  verify_cmd=("$SERVICE_ROOT/scripts/verify-all-services.sh")
  if [[ "$SEND_TELEGRAM_TEST" == "true" ]]; then
    verify_cmd+=("--send-telegram-test")
  fi
  "${verify_cmd[@]}"
else
  log "Skipping verification (--skip-verify)"
fi

