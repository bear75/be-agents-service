#!/bin/bash
#
# Generate Check-in Template
#
# Creates a daily, weekly, or monthly check-in file from template.
# Pre-populates the "Agent Activity" section with data from session state.
#
# Usage:
#   ./scripts/workspace/generate-checkin.sh <repo-name> <type>
#   ./scripts/workspace/generate-checkin.sh beta-appcaire daily
#   ./scripts/workspace/generate-checkin.sh beta-appcaire weekly
#   ./scripts/workspace/generate-checkin.sh beta-appcaire monthly
#
# Idempotent: will not overwrite existing check-in files.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source workspace resolver
source "$SCRIPT_DIR/resolve-workspace.sh"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[checkin]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[checkin]${NC} $1"; }

# ─── Parse arguments ──────────────────────────────────────────────────────────

REPO_NAME="${1:-}"
CHECKIN_TYPE="${2:-daily}"

if [[ -z "$REPO_NAME" ]]; then
  echo "Usage: $0 <repo-name> <daily|weekly|monthly>"
  exit 1
fi

if [[ ! "$CHECKIN_TYPE" =~ ^(daily|weekly|monthly)$ ]]; then
  echo "Error: type must be daily, weekly, or monthly"
  exit 1
fi

# ─── Resolve paths ────────────────────────────────────────────────────────────

WORKSPACE_PATH=$(get_workspace_path "$REPO_NAME")
TEMPLATES_DIR=$(get_templates_dir)

if [[ -z "$WORKSPACE_PATH" ]]; then
  echo "Error: No workspace configured for '$REPO_NAME'"
  exit 1
fi

# Ensure check-in directory exists
CHECKIN_DIR="$WORKSPACE_PATH/check-ins/$CHECKIN_TYPE"
mkdir -p "$CHECKIN_DIR"

# ─── Determine filename and display date ──────────────────────────────────────

case "$CHECKIN_TYPE" in
  daily)
    FILENAME="$(date +%Y-%m-%d).md"
    DISPLAY_DATE="$(date +'%A, %b %-d, %Y')"
    TEMPLATE_FILE="daily-checkin.md"
    PLACEHOLDER="__DATE_DISPLAY__"
    ;;
  weekly)
    # ISO week number
    WEEK_NUM=$(date +%V)
    YEAR=$(date +%Y)
    FILENAME="${YEAR}-W${WEEK_NUM}.md"

    # Week date range
    # Find Monday of this week
    DAY_OF_WEEK=$(date +%u)  # 1=Monday, 7=Sunday
    DAYS_SINCE_MONDAY=$((DAY_OF_WEEK - 1))
    MONDAY=$(date -d "-${DAYS_SINCE_MONDAY} days" +"%b %-d" 2>/dev/null || date -v-"${DAYS_SINCE_MONDAY}"d +"%b %-d" 2>/dev/null || echo "")
    SUNDAY=$(date -d "+$((6 - DAYS_SINCE_MONDAY)) days" +"%b %-d" 2>/dev/null || date -v+"$((6 - DAYS_SINCE_MONDAY))"d +"%b %-d" 2>/dev/null || echo "")

    if [[ -n "$MONDAY" && -n "$SUNDAY" ]]; then
      DISPLAY_DATE="Week ${WEEK_NUM}, ${YEAR} (${MONDAY}-${SUNDAY})"
    else
      DISPLAY_DATE="Week ${WEEK_NUM}, ${YEAR}"
    fi
    TEMPLATE_FILE="weekly-checkin.md"
    PLACEHOLDER="__WEEK_DISPLAY__"
    ;;
  monthly)
    FILENAME="$(date +%Y-%m).md"
    DISPLAY_DATE="$(date +'%B %Y')"
    TEMPLATE_FILE="monthly-checkin.md"
    PLACEHOLDER="__MONTH_DISPLAY__"
    ;;
esac

CHECKIN_FILE="$CHECKIN_DIR/$FILENAME"

# ─── Check if already exists ─────────────────────────────────────────────────

if [[ -f "$CHECKIN_FILE" ]]; then
  log_warn "Check-in already exists: $CHECKIN_FILE"
  log_warn "Not overwriting."
  exit 0
fi

# ─── Generate from template ──────────────────────────────────────────────────

TEMPLATE_PATH="$TEMPLATES_DIR/$TEMPLATE_FILE"

if [[ ! -f "$TEMPLATE_PATH" ]]; then
  log_warn "Template not found: $TEMPLATE_PATH"
  # Create minimal fallback
  echo "# ${CHECKIN_TYPE^} Check-in — $DISPLAY_DATE" > "$CHECKIN_FILE"
  echo "" >> "$CHECKIN_FILE"
  echo "## Notes" >> "$CHECKIN_FILE"
  echo "- " >> "$CHECKIN_FILE"
  log_info "Created minimal check-in: $CHECKIN_FILE"
  exit 0
fi

# Copy template and replace placeholder
sed "s/$PLACEHOLDER/$DISPLAY_DATE/g" "$TEMPLATE_PATH" > "$CHECKIN_FILE"

# ─── Pre-populate agent data (for daily check-ins) ────────────────────────────

if [[ "$CHECKIN_TYPE" == "daily" ]]; then
  # Try to read latest session state
  STATE_DIR="$SERVICE_ROOT/.compound-state"

  if [[ -d "$STATE_DIR" ]]; then
    LATEST_SESSION=$(ls -d "$STATE_DIR"/session-* 2>/dev/null | sort -r | head -1)

    if [[ -n "$LATEST_SESSION" ]]; then
      ORCH_FILE="$LATEST_SESSION/orchestrator.json"

      if [[ -f "$ORCH_FILE" ]]; then
        STATUS=$(jq -r '.status // "unknown"' "$ORCH_FILE" 2>/dev/null || echo "unknown")
        PR_URL=$(jq -r '.prUrl // ""' "$ORCH_FILE" 2>/dev/null || echo "")
        SESSION_ID=$(basename "$LATEST_SESSION")

        {
          echo "- Session $SESSION_ID: status=$STATUS"
          if [[ -n "$PR_URL" && "$PR_URL" != "null" ]]; then
            echo "- PR created: $PR_URL"
          fi
        } >> "$CHECKIN_FILE"
      fi
    fi
  fi
fi

log_info "Created $CHECKIN_TYPE check-in: $CHECKIN_FILE"
log_info "Display date: $DISPLAY_DATE"
