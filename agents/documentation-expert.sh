#!/bin/bash
#
# Documentation Expert Agent
# Keeps docs updated, archives obsolete docs, verifies with team, publishes to docs page
#
# Usage:
#   ./documentation-expert.sh <session_id> <target_repo> <priority_file>
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
PROMPT_FILE="$SCRIPT_DIR/prompts/documentation-expert.md"
# Fallback: check target repo for repo-specific overrides
if [[ -f "$TARGET_REPO/.claude/prompts/documentation-expert.md" ]]; then
  PROMPT_FILE="$TARGET_REPO/.claude/prompts/documentation-expert.md"
fi
LOG_DIR="$SERVICE_ROOT/logs/docs-expert-sessions"
STATE_DIR="$SERVICE_ROOT/.compound-state"

export COMPOUND_STATE_DIR="$STATE_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[DOCS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[DOCS]${NC} $1"; }
log_error() { echo -e "${RED}[DOCS]${NC} $1"; }

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
LOG_FILE="$SESSION_LOG_DIR/docs-expert.log"

log_info "Starting documentation expert for session: $SESSION_ID" | tee -a "$LOG_FILE"
log_info "Target repo: $TARGET_REPO" | tee -a "$LOG_FILE"

START_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
INITIAL_STATE=$(cat <<EOF
{
  "status": "in_progress",
  "startTime": "$START_TIME",
  "tasks": { "docs": "pending", "archive": "pending", "verify": "pending" },
  "completedTasks": []
}
EOF
)

write_state "$SESSION_ID" "docs-expert" "$INITIAL_STATE" >> "$LOG_FILE" 2>&1

log_info "Analyzing priority for documentation work..." | tee -a "$LOG_FILE"

PRIORITY_CONTENT=$(cat "$PRIORITY_FILE")

log_info "Executing documentation expert tasks..." | tee -a "$LOG_FILE"

cd "$TARGET_REPO"

LOOP_SCRIPT="$SERVICE_ROOT/scripts/compound/loop.sh"
if [[ ! -f "$LOOP_SCRIPT" ]]; then
  log_error "loop.sh not found: $LOOP_SCRIPT" | tee -a "$LOG_FILE"
  update_state "$SESSION_ID" "docs-expert" '.status' 'failed'
  exit 2
fi

"$LOOP_SCRIPT" 6 >> "$LOG_FILE" 2>&1
IMPLEMENTATION_EXIT=$?

if [[ $IMPLEMENTATION_EXIT -ne 0 ]]; then
  log_error "Documentation expert implementation failed (exit code: $IMPLEMENTATION_EXIT)" | tee -a "$LOG_FILE"
  update_state "$SESSION_ID" "docs-expert" '.status' 'failed'
  exit 1
fi

log_info "Documentation expert implementation completed" | tee -a "$LOG_FILE"

END_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

DOCS_UPDATED=false
if git diff HEAD~1 --name-only 2>/dev/null | grep -qE "\.md$|docs/|README"; then
  DOCS_UPDATED=true
fi

COMPLETED_TASKS_JSON="[]"
[[ "$DOCS_UPDATED" == "true" ]] && COMPLETED_TASKS_JSON=$(echo "$COMPLETED_TASKS_JSON" | jq '. + [{"id": "docs-update", "description": "Documentation updated"}]')

FINAL_STATE=$(cat <<EOF
{
  "agentName": "docs-expert",
  "status": "completed",
  "timestamp": "$END_TIME",
  "startTime": "$START_TIME",
  "endTime": "$END_TIME",
  "completedTasks": $COMPLETED_TASKS_JSON,
  "artifacts": { "exports": { "docsUpdated": $DOCS_UPDATED } },
  "concerns": [],
  "blockers": [],
  "nextSteps": [],
  "replanRequired": false
}
EOF
)

write_state "$SESSION_ID" "docs-expert" "$FINAL_STATE" >> "$LOG_FILE" 2>&1

log_info "Documentation Expert Complete - Status: completed" | tee -a "$LOG_FILE"
exit 0
