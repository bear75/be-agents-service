#!/bin/bash
#
# Session Complete Notification
#
# Sends a notification after an agent session completes.
# Called at the end of auto-compound.sh.
#
# Usage:
#   ./scripts/notifications/session-complete.sh <repo-name> [status] [pr-url]
#   ./scripts/notifications/session-complete.sh beta-appcaire completed "https://github.com/..."
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load environment
if [[ -f "$HOME/.config/caire/env" ]]; then
  source "$HOME/.config/caire/env"
fi

# ─── Parse arguments ──────────────────────────────────────────────────────────

REPO_NAME="${1:-beta-appcaire}"
STATUS="${2:-completed}"
PR_URL="${3:-}"

# ─── Build message ───────────────────────────────────────────────────────────

case "$STATUS" in
  completed) EMOJI="✅" ;;
  failed)    EMOJI="❌" ;;
  blocked)   EMOJI="🚫" ;;
  *)         EMOJI="🔄" ;;
esac

MSG="${EMOJI} *Agent session ${STATUS}*

📋 *Repository:* ${REPO_NAME}"

if [[ -n "$PR_URL" ]]; then
  MSG+="
🔀 *PR:* ${PR_URL}"
fi

MSG+="
⏰ *Time:* $(date +'%H:%M')"

echo "$MSG"

# ─── Send via Telegram ───────────────────────────────────────────────────────

if [[ -n "${TELEGRAM_BOT_TOKEN:-}" && -n "${TELEGRAM_CHAT_ID:-}" ]]; then
  curl -s -X POST \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=${MSG}" \
    -d "parse_mode=Markdown" \
    >/dev/null 2>&1 || echo "⚠️  Failed to send Telegram notification"
fi
