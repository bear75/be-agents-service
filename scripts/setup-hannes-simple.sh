#!/usr/bin/env bash
#
# Bootstrap "simple mode" for Hannes on the same Mac mini.
# - Keeps primary DARWIN setup unchanged
# - Configures/initializes the hannes-projects workspace
# - Ensures local repo path exists and has required directories
#
# Usage:
#   ./scripts/setup-hannes-simple.sh
#   ./scripts/setup-hannes-simple.sh --owner-id 8399128208 --hannes-id 7604480012 --send-telegram-test
#   ./scripts/setup-hannes-simple.sh hannes-projects --owner-id 8399128208 --hannes-id 7604480012
#   ./scripts/setup-hannes-simple.sh --owner-id 8399128208 --hannes-id 7604480012 --send-telegram-test --telegram-token "<bot-token>"
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="$SERVICE_ROOT/config/repos.yaml"
INIT_WORKSPACE_SCRIPT="$SERVICE_ROOT/scripts/workspace/init-workspace.sh"
TELEGRAM_TEST_SCRIPT="$SERVICE_ROOT/scripts/notifications/send-telegram-test.sh"
OPENCLAW_TEMPLATE="$SERVICE_ROOT/config/openclaw/openclaw.json"
OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
ENV_FILE="$HOME/.config/caire/env"

REPO_KEY="${1:-hannes-projects}"
OWNER_ID=""
HANNES_ID=""
SEND_TELEGRAM_TEST=false
TELEGRAM_TOKEN=""

if [[ "$REPO_KEY" == "--owner-id" || "$REPO_KEY" == "--hannes-id" || "$REPO_KEY" == "--send-telegram-test" ]]; then
  REPO_KEY="hannes-projects"
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --owner-id)
      OWNER_ID="${2:-}"
      shift 2
      ;;
    --hannes-id)
      HANNES_ID="${2:-}"
      shift 2
      ;;
    --send-telegram-test)
      SEND_TELEGRAM_TEST=true
      shift
      ;;
    --telegram-token)
      TELEGRAM_TOKEN="${2:-}"
      shift 2
      ;;
    hannes-projects)
      REPO_KEY="$1"
      shift
      ;;
    *)
      if [[ "$1" != "$REPO_KEY" ]]; then
        fail "Unknown argument: $1"
      fi
      shift
      ;;
  esac
done

log() { echo "[setup-hannes] $*"; }
warn() { echo "[setup-hannes] WARNING: $*"; }
fail() { echo "[setup-hannes] ERROR: $*" >&2; exit 1; }

ensure_modern_openclaw_config() {
  if [[ -f "$OPENCLAW_CONFIG" ]] && grep -qE '^\s*agent:\s*' "$OPENCLAW_CONFIG"; then
    warn "Legacy OpenClaw config detected (agent.*). Replacing with template."
    mkdir -p "$HOME/.openclaw"
    cp "$OPENCLAW_TEMPLATE" "$OPENCLAW_CONFIG"
  fi
}

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck source=/dev/null
  source "$ENV_FILE" || true
fi

[[ -f "$CONFIG_FILE" ]] || fail "Missing config file: $CONFIG_FILE"
[[ -f "$INIT_WORKSPACE_SCRIPT" ]] || fail "Missing workspace init script: $INIT_WORKSPACE_SCRIPT"

REPO_BLOCK="$(grep -A 30 "^  ${REPO_KEY}:" "$CONFIG_FILE" | head -31 || true)"
[[ -n "$REPO_BLOCK" ]] || fail "Repo key '${REPO_KEY}' not found in config/repos.yaml"

REPO_PATH="$(echo "$REPO_BLOCK" | grep "path:" | head -1 | sed 's/.*path: *//' | sed "s|~|$HOME|")"
WORKSPACE_PATH="$(echo "$REPO_BLOCK" | grep -A 6 "workspace:" | grep "path:" | head -1 | sed 's/.*path: *//' | sed "s|~|$HOME|")"
GITHUB_OWNER="$(echo "$REPO_BLOCK" | grep "owner:" | head -1 | sed 's/.*owner: *//')"
GITHUB_REPO="$(echo "$REPO_BLOCK" | grep "repo:" | head -1 | sed 's/.*repo: *//')"

[[ -n "$REPO_PATH" ]] || fail "Could not resolve repo path from config"
[[ -n "$WORKSPACE_PATH" ]] || fail "Could not resolve workspace path from config"
[[ -n "$GITHUB_OWNER" && -n "$GITHUB_REPO" ]] || fail "Missing github.owner/repo in config"

log "Repo key:       $REPO_KEY"
log "Repo path:      $REPO_PATH"
log "Workspace path: $WORKSPACE_PATH"
log "GitHub repo:    $GITHUB_OWNER/$GITHUB_REPO"

if [[ ! -d "$REPO_PATH/.git" ]]; then
  log "Local repo not found at $REPO_PATH; cloning..."
  mkdir -p "$(dirname "$REPO_PATH")"
  if command -v gh >/dev/null 2>&1; then
    if ! gh repo clone "$GITHUB_OWNER/$GITHUB_REPO" "$REPO_PATH"; then
      warn "gh clone failed for $GITHUB_OWNER/$GITHUB_REPO (continuing in workspace-only mode)"
      mkdir -p "$REPO_PATH"
    fi
  else
    if ! git clone "https://github.com/$GITHUB_OWNER/$GITHUB_REPO.git" "$REPO_PATH"; then
      warn "git clone failed for $GITHUB_OWNER/$GITHUB_REPO (continuing in workspace-only mode)"
      mkdir -p "$REPO_PATH"
    fi
  fi
else
  log "Local repo exists: $REPO_PATH"
fi

mkdir -p "$REPO_PATH/reports" "$REPO_PATH/logs" "$REPO_PATH/tasks"
log "Ensured reports/logs/tasks in target repo"

"$INIT_WORKSPACE_SCRIPT" "$REPO_KEY" "$WORKSPACE_PATH"

if [[ -n "$OWNER_ID" || -n "$HANNES_ID" ]]; then
  MERGED_IDS=()
  [[ -n "$OWNER_ID" ]] && MERGED_IDS+=("$OWNER_ID")
  [[ -n "$HANNES_ID" ]] && MERGED_IDS+=("$HANNES_ID")
  if command -v openclaw >/dev/null 2>&1; then
    ensure_modern_openclaw_config

    log "Running OpenClaw doctor fix (safe no-op if already clean)"
    openclaw doctor --fix >/dev/null || true
    ensure_modern_openclaw_config

    ACTIVE_TELEGRAM_TOKEN="${TELEGRAM_TOKEN:-${TELEGRAM_BOT_TOKEN:-}}"
    if [[ -n "$ACTIVE_TELEGRAM_TOKEN" ]]; then
      log "Setting Telegram bot token in OpenClaw config"
      openclaw config set channels.telegram.botToken "$ACTIVE_TELEGRAM_TOKEN" >/dev/null || true
    else
      warn "No Telegram token provided or found in env; bot may not reply to inbound messages"
    fi

    log "Ensuring OpenClaw gateway.mode=local"
    openclaw config set gateway.mode local >/dev/null || true
    log "Ensuring Telegram channel is enabled"
    openclaw config set channels.telegram.enabled true >/dev/null || true

    IDS_JSON="$(printf '%s\n' "${MERGED_IDS[@]}" | jq -R . | jq -s .)"
    log "Updating Telegram allowFrom via openclaw config set"
    if ! openclaw config set channels.telegram.allowFrom "$IDS_JSON" >/dev/null; then
      warn "allowFrom update failed once; refreshing config template and retrying"
      ensure_modern_openclaw_config
      openclaw config set channels.telegram.allowFrom "$IDS_JSON" >/dev/null || true
    fi
    log "allowFrom => $(echo "$IDS_JSON" | jq -r 'join(", ")')"
    log "Restarting OpenClaw gateway to apply allowFrom"
    openclaw gateway restart >/dev/null || warn "OpenClaw gateway restart reported issues"
  else
    warn "OpenClaw CLI not found; skipping allowFrom update"
  fi
fi

if [[ "$SEND_TELEGRAM_TEST" == "true" ]]; then
  [[ -x "$TELEGRAM_TEST_SCRIPT" ]] || fail "Missing executable telegram test script: $TELEGRAM_TEST_SCRIPT"
  TEST_IDS=()
  [[ -n "$OWNER_ID" ]] && TEST_IDS+=("$OWNER_ID")
  [[ -n "$HANNES_ID" ]] && TEST_IDS+=("$HANNES_ID")
  if [[ "${#TEST_IDS[@]}" -eq 0 ]]; then
    fail "--send-telegram-test requires --owner-id and/or --hannes-id"
  fi
  log "Sending Telegram test message to: ${TEST_IDS[*]}"
  TELEGRAM_CMD=("$TELEGRAM_TEST_SCRIPT" --ids "${TEST_IDS[@]}" --label "hannes-simple-setup")
  if [[ -n "$TELEGRAM_TOKEN" ]]; then
    TELEGRAM_CMD+=(--token "$TELEGRAM_TOKEN")
  fi
  "${TELEGRAM_CMD[@]}"
fi

log "Done."
echo
echo "Next steps:"
echo "  1) Add priorities in: $WORKSPACE_PATH/priorities.md"
echo "  2) (Optional) Add docs in: $WORKSPACE_PATH/input/"
echo "  3) Run Hannes compound manually:"
echo "     cd \"$SERVICE_ROOT\" && ./scripts/compound/auto-compound.sh $REPO_KEY"
echo "  4) Verify workspace API (if dashboard server is running):"
echo "     curl -s http://localhost:3010/api/workspace/$REPO_KEY/status | jq ."
