#!/bin/bash
#
# Frontend Specialist Agent
# Handles GraphQL operations, codegen, and UI components
#
# Usage:
#   ./frontend-specialist.sh <session_id> <target_repo> <priority_file>
#
# Arguments:
#   session_id    - Session ID for state coordination
#   target_repo   - Path to target repository
#   priority_file - Path to priority markdown file
#
# Exit codes:
#   0 - Success (frontend work completed)
#   1 - Blocked (cannot proceed, backend not ready)
#   2 - Script error
#

set -euo pipefail

# Script directory (be-agent-service)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LIB_DIR="$SERVICE_ROOT/lib"

# Source state manager
source "$LIB_DIR/state-manager.sh"

# Configuration
SESSION_ID="${1:-}"
TARGET_REPO="${2:-}"
PRIORITY_FILE="${3:-}"
PROMPT_FILE="$SCRIPT_DIR/prompts/frontend-specialist.md"
# Fallback: check target repo for repo-specific overrides
if [[ -f "$TARGET_REPO/.claude/prompts/frontend-specialist.md" ]]; then
  PROMPT_FILE="$TARGET_REPO/.claude/prompts/frontend-specialist.md"
fi
LOG_DIR="$SERVICE_ROOT/logs/frontend-sessions"
STATE_DIR="$SERVICE_ROOT/.compound-state"

# Override state directory for state manager
export COMPOUND_STATE_DIR="$STATE_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

#
# Logging functions
#
log_info() {
  echo -e "${GREEN}[FRONTEND]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[FRONTEND]${NC} $1"
}

log_error() {
  echo -e "${RED}[FRONTEND]${NC} $1"
}

#
# Validate inputs
#
if [[ -z "$SESSION_ID" || -z "$TARGET_REPO" || -z "$PRIORITY_FILE" ]]; then
  log_error "Missing required arguments"
  echo "Usage: $0 <session_id> <target_repo> <priority_file>"
  exit 2
fi

if [[ ! -d "$TARGET_REPO" ]]; then
  log_error "Target repo not found: $TARGET_REPO"
  exit 2
fi

# Create log directory
SESSION_LOG_DIR="$LOG_DIR/$SESSION_ID"
mkdir -p "$SESSION_LOG_DIR"
LOG_FILE="$SESSION_LOG_DIR/frontend.log"

log_info "Starting frontend specialist for session: $SESSION_ID" | tee -a "$LOG_FILE"
log_info "Target repo: $TARGET_REPO" | tee -a "$LOG_FILE"

# Write initial state
START_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
INITIAL_STATE=$(cat <<EOF
{
  "status": "waiting_for_backend",
  "startTime": "$START_TIME",
  "tasks": {
    "operations": "pending",
    "codegen": "pending",
    "ui": "pending"
  },
  "completedTasks": []
}
EOF
)

write_state "$SESSION_ID" "frontend" "$INITIAL_STATE" >> "$LOG_FILE" 2>&1

#
# Check if backend is ready
#
log_info "Checking backend completion status..." | tee -a "$LOG_FILE"

BACKEND_STATUS=$(read_state "$SESSION_ID" "backend" ".status" 2>/dev/null || echo "unknown")

if [[ "$BACKEND_STATUS" != "completed" ]]; then
  log_warn "Backend not completed yet (status: $BACKEND_STATUS)" | tee -a "$LOG_FILE"
  log_info "Frontend waiting for backend..." | tee -a "$LOG_FILE"

  # Wait for backend (with timeout)
  WAIT_TIMEOUT=600  # 10 minutes
  if wait_for_status "$SESSION_ID" "backend" "completed" "$WAIT_TIMEOUT"; then
    log_info "✓ Backend completed, proceeding with frontend" | tee -a "$LOG_FILE"
  else
    log_error "Timeout waiting for backend to complete" | tee -a "$LOG_FILE"

    # Update state to blocked
    BLOCKED_STATE=$(cat <<EOF
{
  "status": "blocked",
  "endTime": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "blockers": [
    {
      "type": "dependency",
      "message": "Timeout waiting for backend to complete",
      "requiresAgent": "backend"
    }
  ]
}
EOF
    )

    write_state "$SESSION_ID" "frontend" "$BLOCKED_STATE" >> "$LOG_FILE" 2>&1
    exit 1
  fi
fi

# Check if backend updated GraphQL schema
BACKEND_STATE=$(read_state "$SESSION_ID" "backend")
SCHEMA_UPDATED=$(echo "$BACKEND_STATE" | jq -r '.artifacts.exports.schemaUpdated // false')

if [[ "$SCHEMA_UPDATED" != "true" ]]; then
  log_warn "Backend did not update GraphQL schema, frontend may have limited work" | tee -a "$LOG_FILE"
fi

# Update status to in_progress
update_state "$SESSION_ID" "frontend" '.status' 'in_progress'

#
# Execute frontend tasks
#
log_info "Executing frontend tasks..." | tee -a "$LOG_FILE"

cd "$TARGET_REPO"

# For Phase 2-3, frontend work is handled by loop.sh continuation
# In future, this will use Claude Code CLI with frontend-specialist prompt

log_info "Frontend tasks delegated to main workflow" | tee -a "$LOG_FILE"

# Check if codegen was run (evidence of frontend work)
CODEGEN_RUN=false
if git log --oneline -10 | grep -qi "codegen\|graphql.*generate"; then
  CODEGEN_RUN=true
  log_info "✓ GraphQL codegen detected in recent commits" | tee -a "$LOG_FILE"
fi

# Check if UI components were added
UI_ADDED=false
if git diff HEAD~5..HEAD --name-only | grep -q "src/pages\|src/components"; then
  UI_ADDED=true
  log_info "✓ UI components added" | tee -a "$LOG_FILE"
fi

#
# Write final state
#
END_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

COMPLETED_TASKS_JSON="[]"
if [[ "$CODEGEN_RUN" == "true" ]]; then
  COMPLETED_TASKS_JSON=$(echo "$COMPLETED_TASKS_JSON" | jq '. + [{"id": "frontend-codegen", "description": "Ran GraphQL codegen"}]')
fi
if [[ "$UI_ADDED" == "true" ]]; then
  COMPLETED_TASKS_JSON=$(echo "$COMPLETED_TASKS_JSON" | jq '. + [{"id": "frontend-ui", "description": "Added UI components"}]')
fi

FINAL_STATE=$(cat <<EOF
{
  "agentName": "frontend",
  "status": "completed",
  "timestamp": "$END_TIME",
  "startTime": "$START_TIME",
  "endTime": "$END_TIME",
  "completedTasks": $COMPLETED_TASKS_JSON,
  "artifacts": {
    "exports": {
      "codegenRun": $CODEGEN_RUN,
      "uiComponentsAdded": $UI_ADDED
    }
  },
  "concerns": [],
  "blockers": [],
  "nextSteps": [
    {
      "agent": "verification",
      "action": "Verify type-check and build pass",
      "priority": "required"
    }
  ],
  "replanRequired": false
}
EOF
)

write_state "$SESSION_ID" "frontend" "$FINAL_STATE" >> "$LOG_FILE" 2>&1

log_info "========================================" | tee -a "$LOG_FILE"
log_info "Frontend Specialist Complete" | tee -a "$LOG_FILE"
log_info "========================================" | tee -a "$LOG_FILE"
log_info "Status: completed" | tee -a "$LOG_FILE"
log_info "Codegen run: $CODEGEN_RUN" | tee -a "$LOG_FILE"
log_info "UI added: $UI_ADDED" | tee -a "$LOG_FILE"
log_info "========================================" | tee -a "$LOG_FILE"

exit 0
