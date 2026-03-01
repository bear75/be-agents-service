#!/usr/bin/env bash
#
# Install and start two independent OpenClaw gateway services:
# - Darwin: com.appcaire.openclaw-darwin (port 18789)
# - Hannes: com.appcaire.openclaw-hannes (port 19001)
#
# This replaces fragile shared label usage (ai.openclaw.gateway) and prevents
# one profile from overwriting/stopping the other.
#
# Usage:
#   ./scripts/openclaw/setup-dual-launchd.sh
#   ./scripts/openclaw/setup-dual-launchd.sh --darwin-only
#   ./scripts/openclaw/setup-dual-launchd.sh --hannes-only
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANAGER="$SCRIPT_DIR/manage-gateway-launchd.sh"

INSTALL_DARWIN=true
INSTALL_HANNES=true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --darwin-only)
      INSTALL_DARWIN=true
      INSTALL_HANNES=false
      shift
      ;;
    --hannes-only)
      INSTALL_DARWIN=false
      INSTALL_HANNES=true
      shift
      ;;
    -h|--help)
      cat <<'EOF'
Usage: ./scripts/openclaw/setup-dual-launchd.sh [options]

Options:
  --darwin-only    Install/start only Darwin gateway
  --hannes-only    Install/start only Hannes gateway
  -h, --help       Show this help
EOF
      exit 0
      ;;
    *)
      echo "[openclaw-dual] Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

[[ -x "$MANAGER" ]] || {
  echo "[openclaw-dual] Missing executable manager script: $MANAGER" >&2
  exit 1
}

uid="$(id -u)"

disable_legacy_shared_service() {
  local legacy_label="ai.openclaw.gateway"
  local legacy_plist="$HOME/Library/LaunchAgents/${legacy_label}.plist"
  if launchctl print "gui/$uid/$legacy_label" >/dev/null 2>&1; then
    echo "[openclaw-dual] Stopping legacy shared gateway label: $legacy_label"
    launchctl bootout "gui/$uid/$legacy_label" >/dev/null 2>&1 || true
  fi
  if [[ -f "$legacy_plist" ]]; then
    echo "[openclaw-dual] Legacy plist still present: $legacy_plist"
    echo "[openclaw-dual] Keeping file in place, but legacy service has been stopped."
  fi
}

disable_legacy_shared_service

if [[ "$INSTALL_DARWIN" == "true" ]]; then
  darwin_config="${OPENCLAW_DARWIN_CONFIG:-$HOME/.openclaw/openclaw.json}"
  if [[ -f "${darwin_config/#\~/$HOME}" ]]; then
    echo "[openclaw-dual] Installing Darwin gateway service..."
    "$MANAGER" darwin install
  else
    echo "[openclaw-dual] Skipping Darwin gateway (missing config: $darwin_config)"
  fi
fi

if [[ "$INSTALL_HANNES" == "true" ]]; then
  hannes_config="${OPENCLAW_HANNES_CONFIG:-$HOME/.openclaw-hannes/openclaw.json}"
  if [[ -f "${hannes_config/#\~/$HOME}" ]]; then
    echo "[openclaw-dual] Installing Hannes gateway service..."
    "$MANAGER" hannes install
  else
    echo "[openclaw-dual] Skipping Hannes gateway (missing config: $hannes_config)"
  fi
fi

echo
echo "[openclaw-dual] Done."
