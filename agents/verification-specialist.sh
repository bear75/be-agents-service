#!/bin/bash
#
# Verification Specialist Agent
# Validates code changes meet quality, security, and architectural standards
#
# Usage:
#   ./verification-specialist.sh <session_id> [--auto-fix]
#
# Arguments:
#   session_id - Session ID for state coordination
#   --auto-fix - Automatically fix simple issues (codegen, etc.)
#
# Exit codes:
#   0 - All verifications passed
#   1 - Verification blocked (critical issues found)
#   2 - Script error
#

set -euo pipefail

# Script directory (be-agent-service)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LIB_DIR="$SERVICE_ROOT/lib"

# Target repo (current working directory when run by orchestrator)
REPO_ROOT="$(pwd)"

# Source state manager
source "$LIB_DIR/state-manager.sh"

# Configuration
SESSION_ID="${1:-}"
AUTO_FIX="${2:-}"
PROMPT_FILE="$REPO_ROOT/.claude/prompts/verification-specialist.md"
LOG_DIR="$SERVICE_ROOT/logs/verification-sessions"
STATE_DIR="$SERVICE_ROOT/.compound-state"

# Override state directory for state manager
export COMPOUND_STATE_DIR="$STATE_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

#
# Print colored output
#
log_info() {
  echo -e "${GREEN}[VERIFY]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[VERIFY]${NC} $1"
}

log_error() {
  echo -e "${RED}[VERIFY]${NC} $1"
}

#
# Validate inputs
#
if [[ -z "$SESSION_ID" ]]; then
  log_error "Session ID required"
  echo "Usage: $0 <session_id> [--auto-fix]"
  exit 2
fi

if [[ ! -f "$PROMPT_FILE" ]]; then
  log_error "Verification prompt not found: $PROMPT_FILE"
  exit 2
fi

# Create log directory for this session
SESSION_LOG_DIR="$LOG_DIR/$SESSION_ID"
mkdir -p "$SESSION_LOG_DIR"
LOG_FILE="$SESSION_LOG_DIR/verification.log"

log_info "Starting verification for session: $SESSION_ID"
log_info "Log file: $LOG_FILE"

# Write initial state
INITIAL_STATE=$(cat <<EOF
{
  "status": "in_progress",
  "startTime": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "checks": {
    "typeCheck": "pending",
    "build": "pending",
    "architecture": "pending",
    "security": "pending"
  },
  "blockers": [],
  "concerns": []
}
EOF
)

write_state "$SESSION_ID" "verification" "$INITIAL_STATE" >> "$LOG_FILE" 2>&1

#
# Run type check
#
log_info "Running type-check..."
update_state "$SESSION_ID" "verification" '.checks.typeCheck' 'in_progress'

TYPE_CHECK_OUTPUT=""
TYPE_CHECK_EXIT=0

cd "$REPO_ROOT"
if TYPE_CHECK_OUTPUT=$(turbo run type-check 2>&1); then
  TYPE_CHECK_EXIT=0
  log_info "✓ Type-check passed"
  update_state "$SESSION_ID" "verification" '.checks.typeCheck' 'passed'
else
  TYPE_CHECK_EXIT=$?
  log_error "✗ Type-check failed (exit code: $TYPE_CHECK_EXIT)"
  update_state "$SESSION_ID" "verification" '.checks.typeCheck' 'failed'

  # Save error output
  echo "$TYPE_CHECK_OUTPUT" >> "$LOG_FILE"
fi

#
# Run build check
#
log_info "Running build check..."
update_state "$SESSION_ID" "verification" '.checks.build' 'in_progress'

BUILD_OUTPUT=""
BUILD_EXIT=0

if BUILD_OUTPUT=$(turbo run build 2>&1); then
  BUILD_EXIT=0
  log_info "✓ Build passed"
  update_state "$SESSION_ID" "verification" '.checks.build' 'passed'
else
  BUILD_EXIT=$?
  log_error "✗ Build failed (exit code: $BUILD_EXIT)"
  update_state "$SESSION_ID" "verification" '.checks.build' 'failed'

  # Save error output
  echo "$BUILD_OUTPUT" >> "$LOG_FILE"
fi

#
# Architecture compliance checks
#
log_info "Checking architecture compliance..."
update_state "$SESSION_ID" "verification" '.checks.architecture' 'in_progress'

ARCH_ISSUES=0

# Check 1: No wrapper hooks around GraphQL hooks
log_info "  Checking for wrapper hooks..."
if grep -r "export.*use.*Query\|export.*use.*Mutation" apps/*/src/hooks/ 2>/dev/null | grep -v "node_modules" | grep -q "use.*Query\|use.*Mutation"; then
  log_warn "  ⚠ Found potential wrapper hooks around GraphQL hooks"
  ARCH_ISSUES=$((ARCH_ISSUES + 1))
fi

# Check 2: BigInt conversion in resolvers
log_info "  Checking for BigInt conversion..."
if grep -r "return.*prisma\." apps/*/src/graphql/resolvers/ 2>/dev/null | grep -v "Number(" | grep -v "node_modules" | grep -q "\.id"; then
  log_warn "  ⚠ Found potential missing BigInt → Number conversion"
  ARCH_ISSUES=$((ARCH_ISSUES + 1))
fi

# Check 3: organizationId filtering
log_info "  Checking for organizationId filtering..."
RESOLVER_FILES=$(find apps/*/src/graphql/resolvers -name "*.ts" 2>/dev/null || true)
if [[ -n "$RESOLVER_FILES" ]]; then
  for file in $RESOLVER_FILES; do
    if grep -q "findMany\|findFirst\|findUnique" "$file" 2>/dev/null; then
      if ! grep -q "organizationId" "$file"; then
        log_warn "  ⚠ Resolver may be missing organizationId filter: $file"
        ARCH_ISSUES=$((ARCH_ISSUES + 1))
      fi
    fi
  done
fi

# Check 4: Apollo Client timing (CRITICAL - see CLAUDE.md #9)
log_info "  Checking Apollo Client setup..."
APOLLO_FILES=$(find apps/*/src -name "apollo*.ts" -o -name "apollo*.tsx" 2>/dev/null || true)
if [[ -n "$APOLLO_FILES" ]]; then
  for file in $APOLLO_FILES; do
    # Check if ApolloClient is created at module level (bad pattern)
    if grep -q "const.*apolloClient.*=.*new ApolloClient" "$file" 2>/dev/null; then
      log_error "  ✗ CRITICAL: Apollo Client created at module level in $file"
      log_error "    This causes silent mutation failures! See CLAUDE.md #9"
      ARCH_ISSUES=$((ARCH_ISSUES + 10)) # High severity
    fi
  done
fi

if [[ $ARCH_ISSUES -eq 0 ]]; then
  log_info "✓ Architecture compliance passed"
  update_state "$SESSION_ID" "verification" '.checks.architecture' 'passed'
else
  log_warn "⚠ Found $ARCH_ISSUES architecture concerns"
  update_state "$SESSION_ID" "verification" '.checks.architecture' 'warning'
fi

#
# Security checks
#
log_info "Checking security..."
update_state "$SESSION_ID" "verification" '.checks.security' 'in_progress'

SECURITY_ISSUES=0

# Check 1: No committed secrets
log_info "  Checking for committed secrets..."
if find . -name ".env" -not -path "./node_modules/*" -not -path "./.git/*" 2>/dev/null | grep -q ".env$"; then
  log_error "  ✗ Found .env file committed to repo"
  SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
fi

# Check 2: No hardcoded API keys
log_info "  Checking for hardcoded credentials..."
if grep -r "sk_\|pk_test_\|sk_live" apps/*/src 2>/dev/null | grep -v "node_modules" | grep -v "VITE_" | grep -q "sk_\|pk_"; then
  log_error "  ✗ Found potential hardcoded API keys"
  SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
fi

if [[ $SECURITY_ISSUES -eq 0 ]]; then
  log_info "✓ Security checks passed"
  update_state "$SESSION_ID" "verification" '.checks.security' 'passed'
else
  log_error "✗ Found $SECURITY_ISSUES security issues"
  update_state "$SESSION_ID" "verification" '.checks.security' 'failed'
fi

#
# Determine final status
#
log_info "Analyzing results..."

CRITICAL_FAILURES=0
BLOCKERS=()

# Type check failure is critical
if [[ $TYPE_CHECK_EXIT -ne 0 ]]; then
  CRITICAL_FAILURES=$((CRITICAL_FAILURES + 1))
  BLOCKERS+=("Type-check failed: $TYPE_CHECK_EXIT errors found")
fi

# Build failure is critical
if [[ $BUILD_EXIT -ne 0 ]]; then
  CRITICAL_FAILURES=$((CRITICAL_FAILURES + 1))
  BLOCKERS+=("Build failed: exit code $BUILD_EXIT")
fi

# Security issues are critical
if [[ $SECURITY_ISSUES -gt 0 ]]; then
  CRITICAL_FAILURES=$((CRITICAL_FAILURES + 1))
  BLOCKERS+=("Security check failed: $SECURITY_ISSUES issues found")
fi

# Critical architecture issues (Apollo Client timing)
if [[ $ARCH_ISSUES -ge 10 ]]; then
  CRITICAL_FAILURES=$((CRITICAL_FAILURES + 1))
  BLOCKERS+=("Critical architecture violation: Apollo Client created at module level")
fi

#
# Write final state
#
if [[ $CRITICAL_FAILURES -eq 0 ]]; then
  FINAL_STATUS="completed"
  log_info "✓ All verifications passed!"

  FINAL_STATE=$(cat <<EOF
{
  "status": "completed",
  "endTime": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "checks": $(read_state "$SESSION_ID" "verification" ".checks"),
  "blockers": [],
  "concerns": $(if [[ $ARCH_ISSUES -gt 0 && $ARCH_ISSUES -lt 10 ]]; then echo "[{\"severity\": \"warning\", \"message\": \"Found $ARCH_ISSUES architecture concerns\"}]"; else echo "[]"; fi),
  "nextSteps": [
    {
      "agent": "orchestrator",
      "action": "Proceed with PR creation",
      "priority": "required"
    }
  ]
}
EOF
  )

  write_state "$SESSION_ID" "verification" "$FINAL_STATE" >> "$LOG_FILE" 2>&1

  exit 0
else
  FINAL_STATUS="blocked"
  log_error "✗ Verification blocked: $CRITICAL_FAILURES critical failures"

  # Build blockers JSON array
  BLOCKERS_JSON="["
  for i in "${!BLOCKERS[@]}"; do
    if [[ $i -gt 0 ]]; then
      BLOCKERS_JSON+=","
    fi
    BLOCKERS_JSON+="{\"type\": \"error\", \"message\": \"${BLOCKERS[$i]}\", \"requiresHuman\": false}"
  done
  BLOCKERS_JSON+="]"

  FINAL_STATE=$(cat <<EOF
{
  "status": "blocked",
  "endTime": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "checks": $(read_state "$SESSION_ID" "verification" ".checks"),
  "blockers": $BLOCKERS_JSON,
  "concerns": [],
  "nextSteps": [
    {
      "agent": "orchestrator",
      "action": "Review blockers and assign to appropriate specialists",
      "priority": "required"
    }
  ]
}
EOF
  )

  write_state "$SESSION_ID" "verification" "$FINAL_STATE" >> "$LOG_FILE" 2>&1

  # Log blockers
  for blocker in "${BLOCKERS[@]}"; do
    log_error "  Blocker: $blocker"
  done

  exit 1
fi
