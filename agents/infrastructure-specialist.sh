#!/bin/bash
#
# Infrastructure Specialist Agent
# Handles package management, configuration, and documentation
#
# Usage:
#   ./infrastructure-specialist.sh <session_id> <target_repo> <priority_file>
#
# Arguments:
#   session_id    - Session ID for state coordination
#   target_repo   - Path to target repository
#   priority_file - Path to priority markdown file
#
# Exit codes:
#   0 - Success (infrastructure work completed)
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
PROMPT_FILE="$TARGET_REPO/.claude/prompts/infrastructure-specialist.md"
LOG_DIR="$SERVICE_ROOT/logs/infrastructure-sessions"
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
  echo -e "${GREEN}[INFRA]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[INFRA]${NC} $1"
}

log_error() {
  echo -e "${RED}[INFRA]${NC} $1"
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
LOG_FILE="$SESSION_LOG_DIR/infrastructure.log"

log_info "Starting infrastructure specialist for session: $SESSION_ID" | tee -a "$LOG_FILE"
log_info "Target repo: $TARGET_REPO" | tee -a "$LOG_FILE"

# Write initial state
START_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
INITIAL_STATE=$(cat <<EOF
{
  "status": "in_progress",
  "startTime": "$START_TIME",
  "tasks": {
    "packages": "pending",
    "config": "pending",
    "documentation": "pending"
  },
  "completedTasks": []
}
EOF
)

write_state "$SESSION_ID" "infrastructure" "$INITIAL_STATE" >> "$LOG_FILE" 2>&1

#
# Analyze priority for infrastructure work
#
log_info "Analyzing priority for infrastructure work..." | tee -a "$LOG_FILE"

PRIORITY_CONTENT=$(cat "$PRIORITY_FILE")

NEEDS_PACKAGES=false
NEEDS_CONFIG=false
NEEDS_DOCS=false

if echo "$PRIORITY_CONTENT" | grep -qi "package\|dependency\|yarn.*add\|npm.*install"; then
  NEEDS_PACKAGES=true
  log_info "✓ Package management work detected" | tee -a "$LOG_FILE"
fi

if echo "$PRIORITY_CONTENT" | grep -qi "config\|tsconfig\|vite\.config\|\.env"; then
  NEEDS_CONFIG=true
  log_info "✓ Configuration work detected" | tee -a "$LOG_FILE"
fi

if echo "$PRIORITY_CONTENT" | grep -qi "documentation\|readme\|claude\.md\|docs/"; then
  NEEDS_DOCS=true
  log_info "✓ Documentation work detected" | tee -a "$LOG_FILE"
fi

#
# Infrastructure work can run in parallel with backend
# No dependencies needed
#
log_info "Executing infrastructure tasks (parallel with backend)..." | tee -a "$LOG_FILE"

cd "$TARGET_REPO"

# For Phase 2-3, infrastructure work is minimal or handled by loop.sh
# In future, this will handle:
# - yarn workspace commands
# - Config file updates
# - CLAUDE.md updates

# Check for package.json changes
PACKAGES_UPDATED=false
if git diff HEAD~5..HEAD --name-only | grep -q "package.json\|yarn.lock"; then
  PACKAGES_UPDATED=true
  log_info "✓ Packages updated" | tee -a "$LOG_FILE"
fi

# Check for config changes
CONFIG_UPDATED=false
if git diff HEAD~5..HEAD --name-only | grep -q "tsconfig.json\|vite.config\|\.env.example"; then
  CONFIG_UPDATED=true
  log_info "✓ Configuration updated" | tee -a "$LOG_FILE"
fi

# Check for documentation changes
DOCS_UPDATED=false
if git diff HEAD~5..HEAD --name-only | grep -q "CLAUDE.md\|docs/\|README.md"; then
  DOCS_UPDATED=true
  log_info "✓ Documentation updated" | tee -a "$LOG_FILE"
fi

#
# Write final state
#
END_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

COMPLETED_TASKS_JSON="[]"
if [[ "$PACKAGES_UPDATED" == "true" ]]; then
  COMPLETED_TASKS_JSON=$(echo "$COMPLETED_TASKS_JSON" | jq '. + [{"id": "infra-packages", "description": "Updated package dependencies"}]')
fi
if [[ "$CONFIG_UPDATED" == "true" ]]; then
  COMPLETED_TASKS_JSON=$(echo "$COMPLETED_TASKS_JSON" | jq '. + [{"id": "infra-config", "description": "Updated configuration files"}]')
fi
if [[ "$DOCS_UPDATED" == "true" ]]; then
  COMPLETED_TASKS_JSON=$(echo "$COMPLETED_TASKS_JSON" | jq '. + [{"id": "infra-docs", "description": "Updated documentation"}]')
fi

FINAL_STATE=$(cat <<EOF
{
  "agentName": "infrastructure",
  "status": "completed",
  "timestamp": "$END_TIME",
  "startTime": "$START_TIME",
  "endTime": "$END_TIME",
  "completedTasks": $COMPLETED_TASKS_JSON,
  "artifacts": {
    "exports": {
      "packagesUpdated": $PACKAGES_UPDATED,
      "configUpdated": $CONFIG_UPDATED,
      "docsUpdated": $DOCS_UPDATED
    }
  },
  "concerns": [],
  "blockers": [],
  "nextSteps": [],
  "replanRequired": false
}
EOF
)

write_state "$SESSION_ID" "infrastructure" "$FINAL_STATE" >> "$LOG_FILE" 2>&1

log_info "========================================" | tee -a "$LOG_FILE"
log_info "Infrastructure Specialist Complete" | tee -a "$LOG_FILE"
log_info "========================================" | tee -a "$LOG_FILE"
log_info "Status: completed" | tee -a "$LOG_FILE"
log_info "Packages: $PACKAGES_UPDATED" | tee -a "$LOG_FILE"
log_info "Config: $CONFIG_UPDATED" | tee -a "$LOG_FILE"
log_info "Docs: $DOCS_UPDATED" | tee -a "$LOG_FILE"
log_info "========================================" | tee -a "$LOG_FILE"

exit 0
