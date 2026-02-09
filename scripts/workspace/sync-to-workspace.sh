#!/bin/bash
#
# Sync Agent State to Workspace
#
# Reads the latest session state from .compound-state/ and writes
# human-readable summaries to the shared markdown workspace.
#
# What it does:
#   1. Writes agent-reports/latest-session.md with readable summary
#   2. Appends agent activity to today's daily check-in
#   3. Writes a timestamped report for history
#
# Usage:
#   ./scripts/workspace/sync-to-workspace.sh <repo-name> [session-id]
#
# Called by:
#   - auto-compound.sh (at end of session)
#   - daily-compound-review.sh (at end of review)
#   - orchestrator.sh (at end of sprint)
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

log_info() { echo -e "${GREEN}[sync]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[sync]${NC} $1"; }

# ─── Parse arguments ──────────────────────────────────────────────────────────

REPO_NAME="${1:-}"
SESSION_ID="${2:-}"

if [[ -z "$REPO_NAME" ]]; then
  echo "Usage: $0 <repo-name> [session-id]"
  exit 1
fi

# ─── Resolve workspace path ──────────────────────────────────────────────────

WORKSPACE_PATH=$(get_workspace_path "$REPO_NAME")

if [[ -z "$WORKSPACE_PATH" ]]; then
  log_warn "No workspace configured for '$REPO_NAME'. Skipping sync."
  exit 0
fi

if [[ ! -d "$WORKSPACE_PATH" ]]; then
  log_warn "Workspace directory does not exist: $WORKSPACE_PATH"
  log_warn "Run init-workspace.sh first. Skipping sync."
  exit 0
fi

# ─── Find latest session ─────────────────────────────────────────────────────

STATE_DIR="$SERVICE_ROOT/.compound-state"

if [[ -n "$SESSION_ID" ]]; then
  SESSION_PATH="$STATE_DIR/$SESSION_ID"
else
  # Find most recent session
  SESSION_PATH=$(ls -d "$STATE_DIR"/session-* 2>/dev/null | sort -r | head -1 || echo "")
  if [[ -n "$SESSION_PATH" ]]; then
    SESSION_ID=$(basename "$SESSION_PATH")
  fi
fi

if [[ -z "$SESSION_PATH" || ! -d "$SESSION_PATH" ]]; then
  log_warn "No session state found. Nothing to sync."
  exit 0
fi

log_info "Syncing session: $SESSION_ID"
log_info "Workspace: $WORKSPACE_PATH"

# ─── Read session state ──────────────────────────────────────────────────────

ORCH_FILE="$SESSION_PATH/orchestrator.json"
BACKEND_FILE="$SESSION_PATH/backend.json"
FRONTEND_FILE="$SESSION_PATH/frontend.json"
VERIFICATION_FILE="$SESSION_PATH/verification.json"

# Read orchestrator state
STATUS="unknown"
PHASE="unknown"
PR_URL=""
BRANCH=""
START_TIME=""
END_TIME=""

if [[ -f "$ORCH_FILE" ]]; then
  STATUS=$(jq -r '.status // "unknown"' "$ORCH_FILE" 2>/dev/null || echo "unknown")
  PHASE=$(jq -r '.phase // "unknown"' "$ORCH_FILE" 2>/dev/null || echo "unknown")
  PR_URL=$(jq -r '.prUrl // ""' "$ORCH_FILE" 2>/dev/null || echo "")
  BRANCH=$(jq -r '.branchName // ""' "$ORCH_FILE" 2>/dev/null || echo "")
  START_TIME=$(jq -r '.startTime // ""' "$ORCH_FILE" 2>/dev/null || echo "")
  END_TIME=$(jq -r '.endTime // ""' "$ORCH_FILE" 2>/dev/null || echo "")
fi

# Read specialist statuses
BACKEND_STATUS="not run"
FRONTEND_STATUS="not run"
VERIFICATION_STATUS="not run"

if [[ -f "$BACKEND_FILE" ]]; then
  BACKEND_STATUS=$(jq -r '.status // "unknown"' "$BACKEND_FILE" 2>/dev/null || echo "unknown")
fi
if [[ -f "$FRONTEND_FILE" ]]; then
  FRONTEND_STATUS=$(jq -r '.status // "unknown"' "$FRONTEND_FILE" 2>/dev/null || echo "unknown")
fi
if [[ -f "$VERIFICATION_FILE" ]]; then
  VERIFICATION_STATUS=$(jq -r '.status // "unknown"' "$VERIFICATION_FILE" 2>/dev/null || echo "unknown")
fi

# ─── Generate report markdown ───────────────────────────────────────────────

STATUS_EMOJI="❓"
case "$STATUS" in
  completed) STATUS_EMOJI="✅" ;;
  failed)    STATUS_EMOJI="❌" ;;
  blocked)   STATUS_EMOJI="🚫" ;;
  *)         STATUS_EMOJI="🔄" ;;
esac

REPORT="# Agent Session Report

**Session:** $SESSION_ID
**Status:** $STATUS_EMOJI $STATUS
**Phase:** $PHASE"

if [[ -n "$BRANCH" && "$BRANCH" != "null" ]]; then
  REPORT="$REPORT
**Branch:** $BRANCH"
fi

if [[ -n "$START_TIME" && "$START_TIME" != "null" ]]; then
  REPORT="$REPORT
**Started:** $START_TIME"
fi

if [[ -n "$END_TIME" && "$END_TIME" != "null" ]]; then
  REPORT="$REPORT
**Ended:** $END_TIME"
fi

if [[ -n "$PR_URL" && "$PR_URL" != "null" ]]; then
  REPORT="$REPORT
**PR:** $PR_URL"
fi

REPORT="$REPORT

## Specialist Activity

| Specialist | Status |
|-----------|--------|
| Backend | $BACKEND_STATUS |
| Frontend | $FRONTEND_STATUS |
| Verification | $VERIFICATION_STATUS |

---
_Generated at $(date -u +%Y-%m-%dT%H:%M:%SZ)_
"

# ─── Write agent report ─────────────────────────────────────────────────────

REPORTS_DIR="$WORKSPACE_PATH/agent-reports"
mkdir -p "$REPORTS_DIR"

# Write latest
echo "$REPORT" > "$REPORTS_DIR/latest-session.md"
log_info "Wrote: agent-reports/latest-session.md"

# Write timestamped copy
TIMESTAMP=$(date +%Y-%m-%dT%H-%M-%S)
echo "$REPORT" > "$REPORTS_DIR/session-${TIMESTAMP}.md"
log_info "Wrote: agent-reports/session-${TIMESTAMP}.md"

# ─── Append to daily check-in ───────────────────────────────────────────────

TODAY=$(date +%Y-%m-%d)
CHECKIN_FILE="$WORKSPACE_PATH/check-ins/daily/$TODAY.md"

# Create check-in if it doesn't exist
if [[ ! -f "$CHECKIN_FILE" ]]; then
  "$SCRIPT_DIR/generate-checkin.sh" "$REPO_NAME" daily 2>/dev/null || true
fi

if [[ -f "$CHECKIN_FILE" ]]; then
  NOW_TIME=$(date +%H:%M)
  ACTIVITY_LINE="- **${NOW_TIME}** Session $SESSION_ID: $STATUS"

  if [[ -n "$PR_URL" && "$PR_URL" != "null" ]]; then
    ACTIVITY_LINE="$ACTIVITY_LINE — PR: $PR_URL"
  fi

  echo "$ACTIVITY_LINE" >> "$CHECKIN_FILE"
  log_info "Appended activity to: check-ins/daily/$TODAY.md"
fi

# ─── Done ────────────────────────────────────────────────────────────────────

log_info "Workspace sync complete"
