#!/bin/bash
#
# Weekly Review Notification
#
# Generates and sends a weekly review summary via Telegram.
# Called on Monday mornings by launchd.
#
# Usage:
#   ./scripts/notifications/weekly-review.sh <repo-name>
#   ./scripts/notifications/weekly-review.sh beta-appcaire
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source workspace resolver
source "$SERVICE_ROOT/scripts/workspace/resolve-workspace.sh"

# Load environment
if [[ -f "$HOME/.config/caire/env" ]]; then
  source "$HOME/.config/caire/env"
fi

log_info() { echo "[weekly-review] $1"; }

# ─── Parse arguments ──────────────────────────────────────────────────────────

REPO_NAME="${1:-beta-appcaire}"
WORKSPACE_PATH=$(get_workspace_path "$REPO_NAME")

if [[ -z "$WORKSPACE_PATH" ]]; then
  echo "No workspace configured for '$REPO_NAME'"
  exit 1
fi

# ─── Generate weekly check-in ────────────────────────────────────────────────

"$SERVICE_ROOT/scripts/workspace/generate-checkin.sh" "$REPO_NAME" weekly 2>/dev/null || true

# ─── Count sessions this week ────────────────────────────────────────────────

STATE_DIR="$SERVICE_ROOT/.compound-state"
SESSION_COUNT=0
COMPLETED=0
FAILED=0
BLOCKED=0

if [[ -d "$STATE_DIR" ]]; then
  # Count sessions from the last 7 days
  SEVEN_DAYS_AGO=$(date -d "7 days ago" +%s 2>/dev/null || date -v-7d +%s 2>/dev/null || echo "0")

  for session_dir in "$STATE_DIR"/session-*; do
    if [[ ! -d "$session_dir" ]]; then continue; fi

    # Extract timestamp from session name (session-TIMESTAMP)
    SESSION_TS=$(basename "$session_dir" | sed 's/session-//')

    # Only count recent sessions
    if [[ "$SESSION_TS" -gt "$SEVEN_DAYS_AGO" ]] 2>/dev/null; then
      SESSION_COUNT=$((SESSION_COUNT + 1))

      # Check status
      ORCH_FILE="$session_dir/orchestrator.json"
      if [[ -f "$ORCH_FILE" ]]; then
        STATUS=$(jq -r '.status // "unknown"' "$ORCH_FILE" 2>/dev/null || echo "unknown")
        case "$STATUS" in
          completed) COMPLETED=$((COMPLETED + 1)) ;;
          failed)    FAILED=$((FAILED + 1)) ;;
          blocked)   BLOCKED=$((BLOCKED + 1)) ;;
        esac
      fi
    fi
  done
fi

# ─── Count daily check-ins this week ─────────────────────────────────────────

CHECKIN_COUNT=0
CHECKIN_DIR="$WORKSPACE_PATH/check-ins/daily"
if [[ -d "$CHECKIN_DIR" ]]; then
  CHECKIN_COUNT=$(ls "$CHECKIN_DIR"/*.md 2>/dev/null | wc -l || echo "0")
fi

# ─── Build message ───────────────────────────────────────────────────────────

WEEK_NUM=$(date +%V)
YEAR=$(date +%Y)

MSG="📊 *Week ${WEEK_NUM} Review*

*Sessions:* ${SESSION_COUNT} | *Completed:* ${COMPLETED} | *Failed:* ${FAILED}"

if [[ "$BLOCKED" -gt 0 ]]; then
  MSG+=" | *Blocked:* ${BLOCKED}"
fi

MSG+="
*Daily check-ins:* ${CHECKIN_COUNT}

What were your wins this week?
What should we focus on next?"

echo "$MSG"

# ─── Send via Telegram ───────────────────────────────────────────────────────

if [[ -n "${TELEGRAM_BOT_TOKEN:-}" && -n "${TELEGRAM_CHAT_ID:-}" ]]; then
  log_info "Sending weekly review via Telegram..."

  curl -s -X POST \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=${MSG}" \
    -d "parse_mode=Markdown" \
    >/dev/null 2>&1 || echo "⚠️  Failed to send Telegram notification"

  log_info "✅ Sent"
else
  log_info "⚠️  TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set"
fi
