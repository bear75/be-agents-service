#!/bin/bash
#
# UX Designer Specialist Agent
# Handles modern UX 2026, responsive design, PWA, React Native, brand guidelines, accessibility
#
# Usage:
#   ./ux-designer-specialist.sh <session_id> <target_repo> <priority_file>
#
# Arguments:
#   session_id    - Session ID for state coordination
#   target_repo   - Path to target repository
#   priority_file - Path to priority markdown file
#
# Exit codes:
#   0 - Success
#   1 - Blocked (cannot proceed)
#   2 - Script error
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LIB_DIR="$SERVICE_ROOT/lib"

source "$LIB_DIR/state-manager.sh"

SESSION_ID="${1:-}"
TARGET_REPO="${2:-}"
PRIORITY_FILE="${3:-}"
PROMPT_FILE="$TARGET_REPO/.claude/prompts/ux-designer-specialist.md"
LOG_DIR="$SERVICE_ROOT/logs/ux-designer-sessions"
STATE_DIR="$SERVICE_ROOT/.compound-state"

export COMPOUND_STATE_DIR="$STATE_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[UX]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[UX]${NC} $1"; }
log_error() { echo -e "${RED}[UX]${NC} $1"; }

if [[ -z "$SESSION_ID" || -z "$TARGET_REPO" || -z "$PRIORITY_FILE" ]]; then
  log_error "Missing required arguments"
  echo "Usage: $0 <session_id> <target_repo> <priority_file>"
  exit 2
fi

if [[ ! -d "$TARGET_REPO" ]]; then
  log_error "Target repo not found: $TARGET_REPO"
  exit 2
fi

if [[ ! -f "$PRIORITY_FILE" ]]; then
  log_error "Priority file not found: $PRIORITY_FILE"
  exit 2
fi

if [[ -f "$PROMPT_FILE" ]]; then
  log_info "Using prompt: $PROMPT_FILE"
else
  log_warn "Prompt not found, using default behavior"
fi

SESSION_LOG_DIR="$LOG_DIR/$SESSION_ID"
mkdir -p "$SESSION_LOG_DIR"
LOG_FILE="$SESSION_LOG_DIR/ux-designer.log"

log_info "Starting UX designer for session: $SESSION_ID" | tee -a "$LOG_FILE"
log_info "Target repo: $TARGET_REPO" | tee -a "$LOG_FILE"

START_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
INITIAL_STATE=$(cat <<EOF
{
  "status": "in_progress",
  "startTime": "$START_TIME",
  "tasks": { "layout": "pending", "accessibility": "pending", "responsive": "pending" },
  "completedTasks": []
}
EOF
)

write_state "$SESSION_ID" "ux-designer" "$INITIAL_STATE" >> "$LOG_FILE" 2>&1

log_info "Analyzing priority for UX work..." | tee -a "$LOG_FILE"

PRIORITY_CONTENT=$(cat "$PRIORITY_FILE")

log_info "Executing UX designer tasks..." | tee -a "$LOG_FILE"

cd "$TARGET_REPO"

LOOP_SCRIPT="$SERVICE_ROOT/scripts/compound/loop.sh"
if [[ ! -f "$LOOP_SCRIPT" ]]; then
  log_error "loop.sh not found: $LOOP_SCRIPT" | tee -a "$LOG_FILE"
  update_state "$SESSION_ID" "ux-designer" '.status' 'failed'
  exit 2
fi

"$LOOP_SCRIPT" 8 >> "$LOG_FILE" 2>&1
IMPLEMENTATION_EXIT=$?

if [[ $IMPLEMENTATION_EXIT -ne 0 ]]; then
  log_error "UX designer implementation failed (exit code: $IMPLEMENTATION_EXIT)" | tee -a "$LOG_FILE"
  update_state "$SESSION_ID" "ux-designer" '.status' 'failed'
  exit 1
fi

log_info "UX designer implementation completed" | tee -a "$LOG_FILE"

END_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

UI_UPDATED=false
if git diff HEAD~1 --name-only 2>/dev/null | grep -qE "\.tsx?$|\.jsx?$|\.css$"; then
  UI_UPDATED=true
fi

COMPLETED_TASKS_JSON="[]"
[[ "$UI_UPDATED" == "true" ]] && COMPLETED_TASKS_JSON=$(echo "$COMPLETED_TASKS_JSON" | jq '. + [{"id": "ux-ui", "description": "UX/UI updates"}]')

FINAL_STATE=$(cat <<EOF
{
  "agentName": "ux-designer",
  "status": "completed",
  "timestamp": "$END_TIME",
  "startTime": "$START_TIME",
  "endTime": "$END_TIME",
  "completedTasks": $COMPLETED_TASKS_JSON,
  "artifacts": { "exports": { "uiUpdated": $UI_UPDATED } },
  "concerns": [],
  "blockers": [],
  "nextSteps": [],
  "replanRequired": false
}
EOF
)

write_state "$SESSION_ID" "ux-designer" "$FINAL_STATE" >> "$LOG_FILE" 2>&1

log_info "UX Designer Complete - Status: completed" | tee -a "$LOG_FILE"
exit 0
