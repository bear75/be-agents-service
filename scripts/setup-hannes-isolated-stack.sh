#!/usr/bin/env bash
#
# One-shot bootstrap for isolated Hannes stack:
# - Separate repo/workspace config (config/repos.hannes.yaml)
# - Separate dashboard/api runtime (port 3011 + separate DB path)
# - Separate OpenClaw runtime config/state + Telegram bot
#
# Usage:
#   ./scripts/setup-hannes-isolated-stack.sh --hannes-id 7604480012 --bot-token "<HANNES_BOT_TOKEN>"
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HANNES_REPOS_CONFIG="$SERVICE_ROOT/config/repos.hannes.yaml"

HANNES_ID=""
BOT_TOKEN="${HANNES_BOT_TOKEN:-}"
SEND_TEST=true

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
    --no-test)
      SEND_TEST=false
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
[[ -f "$HANNES_REPOS_CONFIG" ]] || { echo "Missing $HANNES_REPOS_CONFIG" >&2; exit 1; }

export REPOS_CONFIG_PATH="$HANNES_REPOS_CONFIG"

echo "[setup-hannes-isolated] Bootstrapping repo/workspace from $REPOS_CONFIG_PATH"
"$SERVICE_ROOT/scripts/setup-hannes-simple.sh" hannes-projects

echo
echo "[setup-hannes-isolated] Configuring isolated OpenClaw runtime"
OPENCLAW_SETUP_ARGS=(--hannes-id "$HANNES_ID" --bot-token "$BOT_TOKEN")
if [[ "$SEND_TEST" == "true" ]]; then
  OPENCLAW_SETUP_ARGS+=(--send-test)
fi
"$SERVICE_ROOT/scripts/setup-hannes-isolated-openclaw.sh" "${OPENCLAW_SETUP_ARGS[@]}"

echo
echo "[setup-hannes-isolated] Done."
echo "Next:"
echo "  1) Start isolated Hannes dashboard/API:"
echo "     $SERVICE_ROOT/scripts/restart-hannes-dashboard.sh"
echo "  2) Verify isolated stack:"
echo "     $SERVICE_ROOT/scripts/verify-hannes-stack.sh"
