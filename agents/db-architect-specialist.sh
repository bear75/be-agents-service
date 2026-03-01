#!/bin/bash
#
# DB Architect Specialist Agent
# Handles database design, Prisma schema, Apollo GraphQL, PostgreSQL optimization
#
# Usage:
#   ./db-architect-specialist.sh <session_id> <target_repo> <priority_file>
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
PROMPT_FILE="$SCRIPT_DIR/prompts/db-architect-specialist.md"
# Fallback: check target repo for repo-specific overrides
if [[ -f "$TARGET_REPO/.claude/prompts/db-architect-specialist.md" ]]; then
  PROMPT_FILE="$TARGET_REPO/.claude/prompts/db-architect-specialist.md"
fi
LOG_DIR="$SERVICE_ROOT/logs/db-architect-sessions"
STATE_DIR="$SERVICE_ROOT/.compound-state"

export COMPOUND_STATE_DIR="$STATE_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[DB-ARCH]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[DB-ARCH]${NC} $1"; }
log_error() { echo -e "${RED}[DB-ARCH]${NC} $1"; }

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
LOG_FILE="$SESSION_LOG_DIR/db-architect.log"

log_info "Starting DB architect for session: $SESSION_ID" | tee -a "$LOG_FILE"
log_info "Target repo: $TARGET_REPO" | tee -a "$LOG_FILE"

START_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
INITIAL_STATE=$(cat <<EOF
{
  "status": "in_progress",
  "startTime": "$START_TIME",
  "tasks": { "schema": "pending", "migration": "pending", "optimization": "pending" },
  "completedTasks": []
}
EOF
)

write_state "$SESSION_ID" "db-architect" "$INITIAL_STATE" >> "$LOG_FILE" 2>&1

log_info "Analyzing priority for database design work..." | tee -a "$LOG_FILE"

PRIORITY_CONTENT=$(cat "$PRIORITY_FILE")

NEEDS_SCHEMA=false
NEEDS_OPTIMIZATION=false

if echo "$PRIORITY_CONTENT" | grep -qi "schema\|prisma\|database\|migration"; then
  NEEDS_SCHEMA=true
  log_info "Schema design work detected" | tee -a "$LOG_FILE"
fi

if echo "$PRIORITY_CONTENT" | grep -qi "optimization\|performance\|query\|index"; then
  NEEDS_OPTIMIZATION=true
  log_info "Optimization work detected" | tee -a "$LOG_FILE"
fi

log_info "Executing DB architect tasks..." | tee -a "$LOG_FILE"

cd "$TARGET_REPO"

LOOP_SCRIPT="$SERVICE_ROOT/scripts/compound/loop.sh"
if [[ ! -f "$LOOP_SCRIPT" ]]; then
  log_error "loop.sh not found: $LOOP_SCRIPT" | tee -a "$LOG_FILE"
  update_state "$SESSION_ID" "db-architect" '.status' 'failed'
  exit 2
fi

"$LOOP_SCRIPT" 8 >> "$LOG_FILE" 2>&1
IMPLEMENTATION_EXIT=$?

if [[ $IMPLEMENTATION_EXIT -ne 0 ]]; then
  log_error "DB architect implementation failed (exit code: $IMPLEMENTATION_EXIT)" | tee -a "$LOG_FILE"
  update_state "$SESSION_ID" "db-architect" '.status' 'failed'
  exit 1
fi

log_info "DB architect implementation completed" | tee -a "$LOG_FILE"

END_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

SCHEMA_UPDATED=false
if git diff HEAD~1 --name-only 2>/dev/null | grep -q "schema.prisma"; then
  SCHEMA_UPDATED=true
fi

MIGRATIONS_CREATED=false
if git diff HEAD~1 --name-only 2>/dev/null | grep -q "prisma/migrations"; then
  MIGRATIONS_CREATED=true
fi

COMPLETED_TASKS_JSON="[]"
[[ "$SCHEMA_UPDATED" == "true" ]] && COMPLETED_TASKS_JSON=$(echo "$COMPLETED_TASKS_JSON" | jq '. + [{"id": "db-schema", "description": "Database schema design"}]')
[[ "$MIGRATIONS_CREATED" == "true" ]] && COMPLETED_TASKS_JSON=$(echo "$COMPLETED_TASKS_JSON" | jq '. + [{"id": "db-migration", "description": "Migration generated"}]')

FINAL_STATE=$(cat <<EOF
{
  "agentName": "db-architect",
  "status": "completed",
  "timestamp": "$END_TIME",
  "startTime": "$START_TIME",
  "endTime": "$END_TIME",
  "completedTasks": $COMPLETED_TASKS_JSON,
  "artifacts": { "exports": { "schemaUpdated": $SCHEMA_UPDATED, "migrationsCreated": $MIGRATIONS_CREATED } },
  "concerns": [],
  "blockers": [],
  "nextSteps": [],
  "replanRequired": false
}
EOF
)

write_state "$SESSION_ID" "db-architect" "$FINAL_STATE" >> "$LOG_FILE" 2>&1

log_info "DB Architect Complete - Status: completed" | tee -a "$LOG_FILE"
exit 0
