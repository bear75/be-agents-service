#!/bin/bash
#
# Morning Briefing
#
# Generates a morning briefing message and sends it via Telegram.
# Called daily at 8:00 AM by launchd.
#
# Usage:
#   ./scripts/notifications/morning-briefing.sh <repo-name>
#   ./scripts/notifications/morning-briefing.sh beta-appcaire
#
# Requirements:
#   - TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables
#   - Or set in ~/.config/caire/env
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

# Colors
GREEN='\033[0;32m'
NC='\033[0m'
log_info() { echo -e "${GREEN}[briefing]${NC} $1"; }

# ─── Parse arguments ──────────────────────────────────────────────────────────

REPO_NAME="${1:-beta-appcaire}"
WORKSPACE_PATH=$(get_workspace_path "$REPO_NAME")

if [[ -z "$WORKSPACE_PATH" ]]; then
  echo "No workspace configured for '$REPO_NAME'"
  exit 1
fi

# ─── Generate daily check-in if not exists ───────────────────────────────────

"$SERVICE_ROOT/scripts/workspace/generate-checkin.sh" "$REPO_NAME" daily 2>/dev/null || true

# ─── Gather data ─────────────────────────────────────────────────────────────

# Count inbox items (grep -c exits 1 when no matches; use || true to avoid pipefail exit)
INBOX_PENDING=0
if [[ -f "$WORKSPACE_PATH/inbox.md" ]]; then
  INBOX_PENDING=$(grep -c '^\- \[ \]' "$WORKSPACE_PATH/inbox.md" 2>/dev/null | head -1) || true
  INBOX_PENDING=${INBOX_PENDING:-0}
fi

# Get priority #1
PRIORITY1="None set"
if [[ -f "$WORKSPACE_PATH/priorities.md" ]]; then
  # Find first numbered item under High Priority
  PRIORITY1=$(awk '/^## High Priority/,/^## /' "$WORKSPACE_PATH/priorities.md" \
    | grep -m1 '^1\.' \
    | sed 's/^1\.\s*//' \
    | sed 's/\*\*//g' \
    | sed 's/\s*—.*//' \
    | head -1 || echo "None set")
  if [[ -z "$PRIORITY1" ]]; then
    PRIORITY1="None set"
  fi
fi

# Get latest agent report
AGENT_SUMMARY=""
REPORT_FILE="$WORKSPACE_PATH/agent-reports/latest-session.md"
if [[ -f "$REPORT_FILE" ]]; then
  STATUS=$(grep "Status:" "$REPORT_FILE" | head -1 | sed 's/.*Status:\*\* //' | sed 's/\*\*//g' || echo "")
  PR_LINE=$(grep "PR:" "$REPORT_FILE" | head -1 | sed 's/.*PR:\*\* //' | sed 's/\*\*//g' || echo "")

  if [[ -n "$STATUS" ]]; then
    AGENT_SUMMARY="$STATUS"
    if [[ -n "$PR_LINE" && "$PR_LINE" != "null" ]]; then
      AGENT_SUMMARY="$AGENT_SUMMARY | PR: $PR_LINE"
    fi
  fi
fi

# Count follow-ups (grep -c exits 1 when no matches; use || true to avoid pipefail exit)
FOLLOWUP_PENDING=0
if [[ -f "$WORKSPACE_PATH/follow-ups.md" ]]; then
  FOLLOWUP_PENDING=$(grep -c '^\- \[ \]' "$WORKSPACE_PATH/follow-ups.md" 2>/dev/null | head -1) || true
  FOLLOWUP_PENDING=${FOLLOWUP_PENDING:-0}
fi

# ─── Build message ───────────────────────────────────────────────────────────

MSG="☀️ *Good morning!*

"

if [[ -n "$AGENT_SUMMARY" ]]; then
  MSG+="🤖 *Last night:* ${AGENT_SUMMARY}
"
fi

MSG+="🎯 *Priority #1:* ${PRIORITY1}
📥 *Inbox:* ${INBOX_PENDING} items"

if [[ "$FOLLOWUP_PENDING" -gt 0 ]]; then
  MSG+=" | 📋 *Follow-ups:* ${FOLLOWUP_PENDING}"
fi

MSG+="

What's on your mind today?"

log_info "Generated briefing:"
echo "$MSG"

# ─── Send via Telegram ───────────────────────────────────────────────────────

if [[ -n "${TELEGRAM_BOT_TOKEN:-}" && -n "${TELEGRAM_CHAT_ID:-}" ]]; then
  log_info "Sending via Telegram..."

  RESPONSE=$(curl -s -X POST \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=${MSG}" \
    -d "parse_mode=Markdown" \
    2>/dev/null || echo '{"ok":false}')

  if echo "$RESPONSE" | jq -r '.ok' 2>/dev/null | grep -q "true"; then
    log_info "✅ Sent to Telegram"
  else
    log_info "⚠️  Failed to send to Telegram"
    echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
  fi
else
  log_info "⚠️  TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set. Message not sent."
  log_info "Set these in ~/.config/caire/env"
fi
