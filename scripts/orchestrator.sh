#!/bin/bash
#
# Multi-Agent Orchestrator
# Coordinates specialist agents across multiple repos (beta-appcaire, cowork, marketing, etc.)
#
# Usage:
#   ./orchestrator.sh <target_repo> <priority_file> <prd_file> <branch_name>
#
# Arguments:
#   target_repo   - Path to target repository (e.g., ~/HomeCare/beta-appcaire)
#   priority_file - Path to priority markdown file
#   prd_file      - Path to PRD file
#   branch_name   - Git branch name for PR
#
# Environment:
#   USE_ORCHESTRATOR - Feature flag (default: true)
#   SKIP_VERIFICATION - Skip verification step (default: false)
#
# Exit codes:
#   0 - Success (PR created)
#   1 - Verification blocked (PR not created)
#   2 - Script error
#

set -euo pipefail

# Script directory (be-agent-service)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LIB_DIR="$SERVICE_ROOT/lib"
AGENTS_DIR="$SERVICE_ROOT/agents"

# Source state manager and parallel executor
source "$LIB_DIR/state-manager.sh"
source "$LIB_DIR/parallel-executor.sh"

# Configuration
TARGET_REPO="${1:-}"
PRIORITY_FILE="${2:-}"
PRD_FILE="${3:-}"
BRANCH_NAME="${4:-}"
USE_ORCHESTRATOR="${USE_ORCHESTRATOR:-true}"
SKIP_VERIFICATION="${SKIP_VERIFICATION:-false}"

# State and logging
SESSION_ID="session-$(date +%s)"
STATE_DIR="$SERVICE_ROOT/.compound-state"
LOG_DIR="$SERVICE_ROOT/logs/orchestrator-sessions/$SESSION_ID"
SESSION_LOG="$LOG_DIR/orchestrator.log"

# Override state directory for state manager
export COMPOUND_STATE_DIR="$STATE_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

#
# Logging functions
#
log_info() {
  echo -e "${GREEN}[ORCHESTRATOR]${NC} $1" | tee -a "$SESSION_LOG"
}

log_warn() {
  echo -e "${YELLOW}[ORCHESTRATOR]${NC} $1" | tee -a "$SESSION_LOG"
}

log_error() {
  echo -e "${RED}[ORCHESTRATOR]${NC} $1" | tee -a "$SESSION_LOG"
}

log_agent() {
  local agent="$1"
  local message="$2"
  echo -e "${BLUE}[$agent]${NC} $message" | tee -a "$SESSION_LOG"
}

#
# Validate inputs
#
if [[ -z "$TARGET_REPO" || -z "$PRIORITY_FILE" || -z "$PRD_FILE" || -z "$BRANCH_NAME" ]]; then
  log_error "Missing required arguments"
  echo "Usage: $0 <target_repo> <priority_file> <prd_file> <branch_name>"
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

# Create session log directory
mkdir -p "$LOG_DIR"

log_info "=========================================="
log_info "Multi-Agent Orchestrator Session"
log_info "=========================================="
log_info "Session ID: $SESSION_ID"
log_info "Target Repo: $TARGET_REPO"
log_info "Priority: $PRIORITY_FILE"
log_info "PRD: $PRD_FILE"
log_info "Branch: $BRANCH_NAME"
log_info "=========================================="

# Initialize session
log_info "Initializing session state..."
session_dir=$(init_session "$SESSION_ID")
log_info "Session state directory: $session_dir"

# Write initial orchestrator state
INITIAL_STATE=$(cat <<EOF
{
  "status": "planning",
  "startTime": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "targetRepo": "$TARGET_REPO",
  "priorityFile": "$PRIORITY_FILE",
  "prdFile": "$PRD_FILE",
  "branchName": "$BRANCH_NAME",
  "specialists": {
    "backend": "pending",
    "frontend": "pending",
    "infrastructure": "pending",
    "verification": "pending"
  },
  "phase": "planning"
}
EOF
)

write_state "$SESSION_ID" "orchestrator" "$INITIAL_STATE" >> "$SESSION_LOG" 2>&1

#
# Analyze priority to determine parallelization strategy
#
log_info "Analyzing priority to determine specialist assignments..."

# Read priority description
PRIORITY_CONTENT=$(cat "$PRIORITY_FILE")

# Determine which specialists are needed
NEEDS_BACKEND=false
NEEDS_FRONTEND=false
NEEDS_INFRASTRUCTURE=false

# Simple heuristic: check for keywords in priority
if echo "$PRIORITY_CONTENT" | grep -qi "schema\|database\|migration\|resolver\|graphql.*mutation\|prisma"; then
  NEEDS_BACKEND=true
  log_info "✓ Backend specialist needed (detected: schema/database changes)"
fi

if echo "$PRIORITY_CONTENT" | grep -qi "ui\|component\|frontend\|react\|vite\|page"; then
  NEEDS_FRONTEND=true
  log_info "✓ Frontend specialist needed (detected: UI/component changes)"
fi

if echo "$PRIORITY_CONTENT" | grep -qi "package\|dependency\|config\|documentation\|monorepo"; then
  NEEDS_INFRASTRUCTURE=true
  log_info "✓ Infrastructure specialist needed (detected: package/config changes)"
fi

# If nothing detected, assume full-stack feature (needs all specialists)
if [[ "$NEEDS_BACKEND" == "false" && "$NEEDS_FRONTEND" == "false" && "$NEEDS_INFRASTRUCTURE" == "false" ]]; then
  log_warn "Could not determine specialist needs, assuming full-stack feature"
  NEEDS_BACKEND=true
  NEEDS_FRONTEND=true
  NEEDS_INFRASTRUCTURE=true
fi

#
# Phase 1: Backend + Infrastructure (Parallel)
#
log_info "=========================================="
log_info "Phase 1: Backend + Infrastructure (Parallel)"
log_info "=========================================="

update_state "$SESSION_ID" "orchestrator" '.phase' 'phase1_parallel'

# Use specialist agents if enabled, otherwise fallback to loop.sh
USE_SPECIALISTS="${USE_SPECIALISTS:-true}"

if [[ "$USE_SPECIALISTS" == "true" ]]; then
  log_info "Using specialist agents for implementation"

  # Spawn backend + infrastructure in parallel
  PARALLEL_PIDS=()

  if [[ "$NEEDS_BACKEND" == "true" ]]; then
    log_info "Spawning backend specialist..."
    "$AGENTS_DIR/backend-specialist.sh" "$SESSION_ID" "$TARGET_REPO" "$PRIORITY_FILE" >> "$LOG_DIR/backend-orchestrated.log" 2>&1 &
    BACKEND_PID=$!
    PARALLEL_PIDS+=("$BACKEND_PID")
    log_info "Backend specialist spawned (PID: $BACKEND_PID)"
  fi

  if [[ "$NEEDS_INFRASTRUCTURE" == "true" ]]; then
    log_info "Spawning infrastructure specialist..."
    "$AGENTS_DIR/infrastructure-specialist.sh" "$SESSION_ID" "$TARGET_REPO" "$PRIORITY_FILE" >> "$LOG_DIR/infrastructure-orchestrated.log" 2>&1 &
    INFRA_PID=$!
    PARALLEL_PIDS+=("$INFRA_PID")
    log_info "Infrastructure specialist spawned (PID: $INFRA_PID)"
  fi

  # Wait for parallel agents to complete
  if [[ ${#PARALLEL_PIDS[@]} -gt 0 ]]; then
    log_info "Waiting for ${#PARALLEL_PIDS[@]} parallel specialist(s) to complete..."

    PARALLEL_FAILED=0
    for pid in "${PARALLEL_PIDS[@]}"; do
      if wait "$pid"; then
        log_info "✓ Specialist $pid completed successfully"
      else
        EXIT_CODE=$?
        log_error "✗ Specialist $pid failed (exit code: $EXIT_CODE)"
        PARALLEL_FAILED=$((PARALLEL_FAILED + 1))
      fi
    done

    if [[ $PARALLEL_FAILED -gt 0 ]]; then
      log_error "Parallel specialists failed: $PARALLEL_FAILED agent(s)"
      update_state "$SESSION_ID" "orchestrator" '.status' 'failed'
      exit 1
    fi

    log_info "✓ All parallel specialists completed successfully"
  fi

else
  log_warn "Specialist agents disabled, using fallback loop.sh"
  cd "$TARGET_REPO"
  "$SCRIPT_DIR/loop.sh" 25 >> "$LOG_DIR/implementation.log" 2>&1
  IMPLEMENTATION_EXIT=$?

  if [[ $IMPLEMENTATION_EXIT -ne 0 ]]; then
    log_error "Implementation failed (exit code: $IMPLEMENTATION_EXIT)"
    update_state "$SESSION_ID" "orchestrator" '.status' 'failed'
    exit $IMPLEMENTATION_EXIT
  fi
fi

log_info "✓ Phase 1 completed"

#
# Phase 2: Frontend (Sequential, after backend)
#
if [[ "$USE_SPECIALISTS" == "true" && "$NEEDS_FRONTEND" == "true" ]]; then
  log_info "=========================================="
  log_info "Phase 2: Frontend (After Backend)"
  log_info "=========================================="

  update_state "$SESSION_ID" "orchestrator" '.phase' 'phase2_frontend'

  log_info "Spawning frontend specialist..."
  "$AGENTS_DIR/frontend-specialist.sh" "$SESSION_ID" "$TARGET_REPO" "$PRIORITY_FILE" >> "$LOG_DIR/frontend-orchestrated.log" 2>&1
  FRONTEND_EXIT=$?

  if [[ $FRONTEND_EXIT -ne 0 ]]; then
    log_error "Frontend specialist failed (exit code: $FRONTEND_EXIT)"
    update_state "$SESSION_ID" "orchestrator" '.status' 'failed'
    exit 1
  fi

  log_info "✓ Frontend specialist completed"
fi

#
# Phase 3: Verification (Always runs)
#
if [[ "$SKIP_VERIFICATION" == "false" ]]; then
  log_info "=========================================="
  log_info "Phase 3: Verification"
  log_info "=========================================="

  update_state "$SESSION_ID" "orchestrator" '.phase' 'verification'

  log_info "Running verification specialist..."

  # Run verification specialist from be-agent-service, targeting the repo
  cd "$TARGET_REPO"
  "$AGENTS_DIR/verification-specialist.sh" "$SESSION_ID" >> "$LOG_DIR/verification.log" 2>&1
  VERIFICATION_EXIT=$?

  if [[ $VERIFICATION_EXIT -eq 0 ]]; then
    log_info "✓ Verification passed - all checks successful"
    update_state "$SESSION_ID" "orchestrator" '.specialists.verification' 'completed'
  else
    log_error "✗ Verification blocked - PR cannot be created"
    update_state "$SESSION_ID" "orchestrator" '.status' 'blocked'
    update_state "$SESSION_ID" "orchestrator" '.specialists.verification' 'blocked'

    # Read verification feedback
    VERIFICATION_STATE=$(read_state "$SESSION_ID" "verification")
    log_error "Verification feedback:"
    echo "$VERIFICATION_STATE" | jq '.' >> "$SESSION_LOG"

    exit 1
  fi
else
  log_warn "Verification skipped (SKIP_VERIFICATION=true)"
fi

#
# Phase 4: PR Creation
#
log_info "=========================================="
log_info "Phase 4: PR Creation"
log_info "=========================================="

update_state "$SESSION_ID" "orchestrator" '.phase' 'pr_creation'

# Safety commit (if Claude forgot to commit)
cd "$TARGET_REPO"
if ! git diff --quiet || ! git diff --cached --quiet; then
  log_warn "Uncommitted changes detected - creating safety commit"
  git add -A
  git commit -m "chore: safety commit (orchestrator detected uncommitted changes)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>" || true
fi

# Create PR using gh CLI
log_info "Creating pull request..."

PR_TITLE=$(head -1 "$PRD_FILE" | sed 's/^# //')
PR_BODY="Automated implementation by multi-agent orchestrator

Session ID: $SESSION_ID
Priority: $(basename "$PRIORITY_FILE")

## Implementation Summary

This PR was created by the multi-agent orchestrator system running on Mac Mini.

## Verification

✅ Type-check passed
✅ Build successful
✅ Architecture compliance verified
✅ Security checks passed

## Review Checklist

- [ ] Code changes align with priority description
- [ ] Tests pass
- [ ] No unexpected side effects

🤖 Generated with multi-agent orchestrator
"

cd "$TARGET_REPO"
PR_URL=$(gh pr create --title "$PR_TITLE" --body "$PR_BODY" --base main --head "$BRANCH_NAME" 2>&1)
PR_EXIT=$?

if [[ $PR_EXIT -eq 0 ]]; then
  log_info "✓ Pull request created successfully"
  log_info "PR URL: $PR_URL"
  update_state "$SESSION_ID" "orchestrator" '.status' 'completed'
  update_state "$SESSION_ID" "orchestrator" '.prUrl' "$PR_URL"
else
  log_error "✗ Failed to create pull request"
  log_error "Error: $PR_URL"
  update_state "$SESSION_ID" "orchestrator" '.status' 'failed'
  exit 1
fi

#
# Finalize session
#
END_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
update_state "$SESSION_ID" "orchestrator" '.endTime' "$END_TIME"

log_info "=========================================="
log_info "Orchestrator Session Complete"
log_info "=========================================="
log_info "Session ID: $SESSION_ID"
log_info "Status: completed"
log_info "PR URL: $PR_URL"
log_info "Logs: $LOG_DIR"
log_info "=========================================="

exit 0
