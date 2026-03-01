#!/usr/bin/env bash
#
# Configure isolated OpenClaw runtime for Hannes on the same machine.
# Uses separate config/state paths to avoid touching primary DARWIN runtime.
#
# Usage:
#   ./scripts/setup-hannes-isolated-openclaw.sh --hannes-id 7604480012 --bot-token "<HANNES_BOT_TOKEN>"
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPOS_CONFIG="${REPOS_CONFIG_PATH:-$SERVICE_ROOT/config/repos.hannes.yaml}"
REPOS_CONFIG="${REPOS_CONFIG/#\~/$HOME}"

HANNES_ID=""
BOT_TOKEN="${HANNES_BOT_TOKEN:-}"
GATEWAY_PORT="${HANNES_GATEWAY_PORT:-19001}"
SEND_TEST=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --hannes-id)
      HANNES_ID="${2:-}"
      shift 2
      ;;
    --bot-token)
      BOT_TOKEN="${2:-}"
      shift 2
      ;;
    --gateway-port)
      GATEWAY_PORT="${2:-19001}"
      shift 2
      ;;
    --send-test)
      SEND_TEST=true
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

[[ -n "$HANNES_ID" ]] || { echo "Missing --hannes-id" >&2; exit 1; }
[[ -n "$BOT_TOKEN" ]] || { echo "Missing --bot-token (or HANNES_BOT_TOKEN env)" >&2; exit 1; }
command -v openclaw >/dev/null 2>&1 || { echo "openclaw CLI not found" >&2; exit 1; }

workspace_path="$(
  grep -A 10 '^  hannes-projects:' "$REPOS_CONFIG" \
    | grep -A 5 'workspace:' \
    | grep 'path:' \
    | head -1 \
    | sed 's/.*path: *//' \
    | sed "s|~|$HOME|" \
    || true
)"

[[ -n "$workspace_path" ]] || { echo "Could not resolve workspace path from $REPOS_CONFIG" >&2; exit 1; }

RUNTIME_ROOT="$HOME/.openclaw-hannes"
RUNTIME_CONFIG="$RUNTIME_ROOT/openclaw.json"
RUNTIME_STATE="$RUNTIME_ROOT/state"
mkdir -p "$RUNTIME_ROOT" "$RUNTIME_STATE"

cp "$SERVICE_ROOT/config/openclaw/openclaw.json" "$RUNTIME_CONFIG"

oc() {
  OPENCLAW_CONFIG_PATH="$RUNTIME_CONFIG" OPENCLAW_STATE_DIR="$RUNTIME_STATE" openclaw "$@"
}

oc config set agents.defaults.workspace "$workspace_path" >/dev/null || true
oc config set channels.telegram.enabled true >/dev/null || true
oc config set channels.telegram.botToken "$BOT_TOKEN" >/dev/null || true
oc config set channels.telegram.allowFrom "[\"$HANNES_ID\"]" >/dev/null || true
oc config set gateway.mode local >/dev/null || true
oc config set gateway.port "$GATEWAY_PORT" >/dev/null || true
oc doctor --fix >/dev/null || true

echo "[setup-hannes-openclaw] Configured isolated runtime:"
echo "  OPENCLAW_CONFIG_PATH=$RUNTIME_CONFIG"
echo "  OPENCLAW_STATE_DIR=$RUNTIME_STATE"
echo "  Workspace=$workspace_path"
echo "  Gateway port=$GATEWAY_PORT"

if [[ "$SEND_TEST" == "true" ]]; then
  if ! "$SERVICE_ROOT/scripts/notifications/send-telegram-test.sh" \
    --token "$BOT_TOKEN" \
    --ids "$HANNES_ID" \
    --label "hannes-isolated-openclaw"; then
    echo "[setup-hannes-openclaw] WARNING: Telegram test failed."
    echo "[setup-hannes-openclaw] Likely cause: Hannes has not opened the new bot and pressed /start yet."
    echo "[setup-hannes-openclaw] Ask Hannes to open the bot once, then rerun with --send-test."
  fi
fi

echo
echo "Start isolated Hannes gateway (foreground):"
echo "  OPENCLAW_CONFIG_PATH=\"$RUNTIME_CONFIG\" OPENCLAW_STATE_DIR=\"$RUNTIME_STATE\" openclaw gateway --port \"$GATEWAY_PORT\""
echo
echo "If you prefer service mode (and your OpenClaw build supports it), run:"
echo "  OPENCLAW_CONFIG_PATH=\"$RUNTIME_CONFIG\" OPENCLAW_STATE_DIR=\"$RUNTIME_STATE\" openclaw gateway restart"
