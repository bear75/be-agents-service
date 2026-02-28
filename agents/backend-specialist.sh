#!/bin/bash
#
# Backend Specialist Agent
# Handles database schema, migrations, GraphQL schema, and resolvers
#
# Usage:
#   ./backend-specialist.sh <session_id> <target_repo> <priority_file>
#
# Arguments:
#   session_id    - Session ID for state coordination
#   target_repo   - Path to target repository
#   priority_file - Path to priority markdown file
#
# Exit codes:
#   0 - Success (backend work completed)
#   1 - Blocked (cannot proceed)
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
PROMPT_FILE="$TARGET_REPO/.claude/prompts/backend-specialist.md"
LOG_DIR="$SERVICE_ROOT/logs/backend-sessions"
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
  echo -e "${GREEN}[BACKEND]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[BACKEND]${NC} $1"
}

log_error() {
  echo -e "${RED}[BACKEND]${NC} $1"
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

if [[ ! -f "$PRIORITY_FILE" ]]; then
  log_error "Priority file not found: $PRIORITY_FILE"
  exit 2
fi

if [[ ! -f "$PROMPT_FILE" ]]; then
  log_error "Backend specialist prompt not found: $PROMPT_FILE"
  exit 2
fi

# Create log directory
SESSION_LOG_DIR="$LOG_DIR/$SESSION_ID"
mkdir -p "$SESSION_LOG_DIR"
LOG_FILE="$SESSION_LOG_DIR/backend.log"

log_info "Starting backend specialist for session: $SESSION_ID" | tee -a "$LOG_FILE"
log_info "Target repo: $TARGET_REPO" | tee -a "$LOG_FILE"
log_info "Priority: $PRIORITY_FILE" | tee -a "$LOG_FILE"

# Write initial state
START_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
INITIAL_STATE=$(cat <<EOF
{
  "status": "in_progress",
  "startTime": "$START_TIME",
  "tasks": {
    "schema": "pending",
    "migration": "pending",
    "graphql": "pending",
    "resolvers": "pending"
  },
  "completedTasks": []
}
EOF
)

write_state "$SESSION_ID" "backend" "$INITIAL_STATE" >> "$LOG_FILE" 2>&1

#
# Read priority content to determine backend scope
#
log_info "Analyzing priority for backend work..." | tee -a "$LOG_FILE"

PRIORITY_CONTENT=$(cat "$PRIORITY_FILE")

# Determine what backend tasks are needed
NEEDS_SCHEMA=false
NEEDS_GRAPHQL=false

if echo "$PRIORITY_CONTENT" | grep -qi "schema\|database\|migration\|prisma\|table\|model"; then
  NEEDS_SCHEMA=true
  log_info "✓ Database schema work detected" | tee -a "$LOG_FILE"
fi

if echo "$PRIORITY_CONTENT" | grep -qi "graphql\|resolver\|mutation\|query\|type.*{"; then
  NEEDS_GRAPHQL=true
  log_info "✓ GraphQL schema work detected" | tee -a "$LOG_FILE"
fi

# If nothing detected, assume full backend work
if [[ "$NEEDS_SCHEMA" == "false" && "$NEEDS_GRAPHQL" == "false" ]]; then
  log_warn "Could not determine backend scope, assuming full backend work" | tee -a "$LOG_FILE"
  NEEDS_SCHEMA=true
  NEEDS_GRAPHQL=true
fi

#
# Execute backend tasks
#
# NOTE: For now, this delegates to the existing loop.sh implementation
# In future iterations, this will use Claude Code CLI with the backend-specialist prompt
#
log_info "Executing backend tasks..." | tee -a "$LOG_FILE"

cd "$TARGET_REPO"

# For Phase 2-3, we use the existing loop.sh as the implementation
# The specialist agent provides structure, coordination, and feedback
# Phase 4+ will use Claude Code CLI directly with specialist prompts

# Check if loop.sh exists in be-agent-service
LOOP_SCRIPT="$SERVICE_ROOT/scripts/compound/loop.sh"
if [[ ! -f "$LOOP_SCRIPT" ]]; then
  log_error "loop.sh not found: $LOOP_SCRIPT" | tee -a "$LOG_FILE"

  # Update state to failed
  update_state "$SESSION_ID" "backend" '.status' 'failed'
  exit 2
fi

# Execute tasks via loop.sh
# This is a transitional approach - Phase 4 will replace with direct Claude Code CLI calls
log_info "Delegating to loop.sh for implementation (Phase 4 will use Claude Code CLI)" | tee -a "$LOG_FILE"

# Run limited iterations (backend should be quick)
BACKEND_TASKS=10  # Limit to 10 iterations for backend work

"$LOOP_SCRIPT" "$BACKEND_TASKS" >> "$LOG_FILE" 2>&1
IMPLEMENTATION_EXIT=$?

if [[ $IMPLEMENTATION_EXIT -ne 0 ]]; then
  log_error "Backend implementation failed (exit code: $IMPLEMENTATION_EXIT)" | tee -a "$LOG_FILE"

  # Update state to failed
  update_state "$SESSION_ID" "backend" '.status' 'failed'

  # Write blocker feedback
  FAILED_STATE=$(cat <<EOF
{
  "status": "failed",
  "endTime": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "blockers": [
    {
      "type": "error",
      "message": "Backend implementation failed with exit code $IMPLEMENTATION_EXIT",
      "requiresHuman": true
    }
  ]
}
EOF
  )

  write_state "$SESSION_ID" "backend" "$FAILED_STATE" >> "$LOG_FILE" 2>&1
  exit 1
fi

log_info "✓ Backend implementation completed" | tee -a "$LOG_FILE"

#
# Determine what was actually completed
#
log_info "Analyzing completed work..." | tee -a "$LOG_FILE"

cd "$TARGET_REPO"

# Check if schema was modified
SCHEMA_UPDATED=false
if git diff HEAD~1 --name-only | grep -q "schema.prisma"; then
  SCHEMA_UPDATED=true
  log_info "✓ Prisma schema updated" | tee -a "$LOG_FILE"
fi

# Check if migrations were created
MIGRATIONS_CREATED=false
MIGRATION_NAMES=()
if git diff HEAD~1 --name-only | grep -q "prisma/migrations"; then
  MIGRATIONS_CREATED=true
  # Extract migration names
  while IFS= read -r migration_path; do
    migration_name=$(basename "$(dirname "$migration_path")")
    MIGRATION_NAMES+=("$migration_name")
  done < <(git diff HEAD~1 --name-only | grep "prisma/migrations" | head -5)
  log_info "✓ Migrations created: ${MIGRATION_NAMES[*]}" | tee -a "$LOG_FILE"
fi

# Check if GraphQL schema was modified
GRAPHQL_UPDATED=false
if git diff HEAD~1 --name-only | grep -q "schema.graphql"; then
  GRAPHQL_UPDATED=true
  log_info "✓ GraphQL schema updated" | tee -a "$LOG_FILE"
fi

# Check if resolvers were added
RESOLVERS_ADDED=false
RESOLVER_FILES=()
if git diff HEAD~1 --name-only | grep -q "src/graphql/resolvers"; then
  RESOLVERS_ADDED=true
  # Extract resolver file names
  while IFS= read -r resolver_path; do
    RESOLVER_FILES+=("$(basename "$resolver_path" .ts)")
  done < <(git diff HEAD~1 --name-only | grep "src/graphql/resolvers.*\.ts$" | head -5)
  log_info "✓ Resolvers added: ${RESOLVER_FILES[*]}" | tee -a "$LOG_FILE"
fi

#
# Write final state with structured feedback
#
END_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Build artifacts exports
EXPORTS_JSON=$(cat <<EOF
{
  "schemaUpdated": $SCHEMA_UPDATED,
  "migrationsCreated": $(printf '%s\n' "${MIGRATION_NAMES[@]}" | jq -R . | jq -s .),
  "resolversAdded": $(printf '%s\n' "${RESOLVER_FILES[@]}" | jq -R . | jq -s .)
}
EOF
)

# Build completed tasks list
COMPLETED_TASKS_JSON="[]"
if [[ "$SCHEMA_UPDATED" == "true" ]]; then
  COMPLETED_TASKS_JSON=$(echo "$COMPLETED_TASKS_JSON" | jq '. + [{"id": "backend-schema", "description": "Updated Prisma schema"}]')
fi
if [[ "$MIGRATIONS_CREATED" == "true" ]]; then
  COMPLETED_TASKS_JSON=$(echo "$COMPLETED_TASKS_JSON" | jq '. + [{"id": "backend-migration", "description": "Generated database migrations"}]')
fi
if [[ "$GRAPHQL_UPDATED" == "true" ]]; then
  COMPLETED_TASKS_JSON=$(echo "$COMPLETED_TASKS_JSON" | jq '. + [{"id": "backend-graphql", "description": "Updated GraphQL schema"}]')
fi
if [[ "$RESOLVERS_ADDED" == "true" ]]; then
  COMPLETED_TASKS_JSON=$(echo "$COMPLETED_TASKS_JSON" | jq '. + [{"id": "backend-resolvers", "description": "Implemented GraphQL resolvers"}]')
fi

# Next steps for orchestrator
NEXT_STEPS_JSON='[]'
if [[ "$GRAPHQL_UPDATED" == "true" ]]; then
  NEXT_STEPS_JSON=$(cat <<EOF
[
  {
    "agent": "frontend",
    "action": "Create GraphQL operations and run codegen",
    "priority": "required",
    "dependencies": ["backend-completed"]
  }
]
EOF
  )
fi

FINAL_STATE=$(cat <<EOF
{
  "agentName": "backend",
  "status": "completed",
  "timestamp": "$END_TIME",
  "startTime": "$START_TIME",
  "endTime": "$END_TIME",
  "completedTasks": $COMPLETED_TASKS_JSON,
  "artifacts": {
    "exports": $EXPORTS_JSON
  },
  "concerns": [],
  "blockers": [],
  "nextSteps": $NEXT_STEPS_JSON,
  "replanRequired": false
}
EOF
)

write_state "$SESSION_ID" "backend" "$FINAL_STATE" >> "$LOG_FILE" 2>&1

log_info "========================================" | tee -a "$LOG_FILE"
log_info "Backend Specialist Complete" | tee -a "$LOG_FILE"
log_info "========================================" | tee -a "$LOG_FILE"
log_info "Status: completed" | tee -a "$LOG_FILE"
log_info "Schema updated: $SCHEMA_UPDATED" | tee -a "$LOG_FILE"
log_info "GraphQL updated: $GRAPHQL_UPDATED" | tee -a "$LOG_FILE"
log_info "Feedback written to state" | tee -a "$LOG_FILE"
log_info "========================================" | tee -a "$LOG_FILE"

exit 0
