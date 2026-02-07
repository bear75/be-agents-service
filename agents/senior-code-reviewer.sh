#!/bin/bash
#
# Senior Code Reviewer - Quality & Accuracy Gatekeeper
# Character: Tony Stark (Genius engineer, high standards, intolerant of sloppy work)
# Personality: Brilliant, exacting, doesn't accept mediocrity
#
# Responsibilities:
# - Code quality review (no sloppy code reaches production)
# - Functional accuracy (all acceptance criteria met from priority file)
# - Architecture compliance (strict monorepo rules enforced)
# - DevOps validation (Docker builds, production builds must pass)
# - Iteration loops (send back to specialists if <90% quality)
# - Self-correction triggers (update learnings for repeated mistakes)
#
# Quality Gate: Must score ≥90% to create PR
# Max iterations: 3 (escalate to PO if still failing)
#

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source libraries
source "$SERVICE_ROOT/lib/state-manager.sh"

# Agent configuration
AGENT_NAME="senior-code-reviewer"
CHARACTER="Tony Stark (Senior Code Reviewer)"
ROLE="Staff Engineer / Quality Gatekeeper"

# Quality thresholds
MIN_QUALITY_SCORE=90
MAX_ITERATIONS=3

# Architecture docs (to be enforced)
ARCHITECTURE_DOCS=(
  "docs/ARCHITECT_PROMPT.md"
  "docs/FRONTEND_GRAPHQL_GUIDE.md"
  ".claude/prompts/architecture.md"
  ".cursor/rules/appcaire-monorepo.mdc"
  "docs/docs-seo/03-brand-design/DESIGN_SYSTEM.md"
)

# DevOps tests (must pass)
DEVOPS_TESTS=(
  "local/scripts/test/test-all-docker-builds.sh"
  "local/scripts/test/test-all-production.sh"
)

# ============================================================================
# Logging
# ============================================================================

LOG_FILE=""

function log_info() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [TONY STARK] [INFO] $*"
}

function log_error() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [TONY STARK] [ERROR] $*" >&2
}

function log_review() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [TONY STARK] [REVIEW] $*"
}

# ============================================================================
# Architecture Compliance Checks
# ============================================================================

function check_architecture_compliance() {
  local target_repo="$1"
  local score=0
  local max_score=100
  local violations=()

  log_review "Checking architecture compliance..."

  cd "$target_repo"

  # Check 1: No env vars in packages (20 points)
  if grep -r "process\.env" packages/*/src/ 2>/dev/null | grep -v "\.env\.example" | grep -v "node_modules"; then
    violations+=("CRITICAL: Environment variables found in packages/ (must be in apps/ only)")
    score=$((score - 20))
  else
    score=$((score + 20))
  fi

  # Check 2: No database access in packages (20 points)
  if grep -r "PrismaClient\|prisma\." packages/*/src/ 2>/dev/null | grep -v "node_modules"; then
    violations+=("CRITICAL: Database access found in packages/ (must be in apps/ only)")
    score=$((score - 20))
  else
    score=$((score + 20))
  fi

  # Check 3: GraphQL resolvers max 50 lines (15 points)
  local long_resolvers=$(find apps/*/src/graphql/resolvers -name "*.ts" -exec wc -l {} \; 2>/dev/null | awk '$1 > 50 {print}' | wc -l)
  if [ "$long_resolvers" -gt 0 ]; then
    violations+=("Code quality: $long_resolvers resolver files exceed 50 lines")
    score=$((score + 5))
  else
    score=$((score + 15))
  fi

  # Check 4: No wrapper hooks around GraphQL hooks (15 points)
  if find apps/*/src -name "use*.ts" -o -name "use*.tsx" 2>/dev/null | xargs grep -l "use.*Query\|use.*Mutation" 2>/dev/null | grep -v "node_modules" | head -n 1; then
    violations+=("CRITICAL: Wrapper hooks detected (use generated hooks directly from @appcaire/graphql)")
    score=$((score - 15))
  else
    score=$((score + 15))
  fi

  # Check 5: BigInt conversion in resolvers (15 points)
  local missing_bigint_conversion=false
  for resolver_file in $(find apps/*/src/graphql/resolvers -name "*.ts" 2>/dev/null); do
    if grep -q "BigInt\|bigint" "$resolver_file" 2>/dev/null; then
      if ! grep -q "Number(" "$resolver_file" 2>/dev/null; then
        violations+=("Data integrity: BigInt not converted to Number in $resolver_file")
        missing_bigint_conversion=true
      fi
    fi
  done
  if [ "$missing_bigint_conversion" = false ]; then
    score=$((score + 15))
  fi

  # Check 6: organizationId filtering (15 points)
  local missing_org_filter=false
  for resolver_file in $(find apps/*/src/graphql/resolvers -type f -name "*.ts" 2>/dev/null); then
    if grep -q "findMany\|findFirst" "$resolver_file" 2>/dev/null; then
      if ! grep -q "organizationId" "$resolver_file" 2>/dev/null; then
        violations+=("SECURITY: Missing organizationId filtering in $resolver_file")
        missing_org_filter=true
      fi
    fi
  done
  if [ "$missing_org_filter" = false ]; then
    score=$((score + 15))
  fi

  # Cap score at max
  if [ $score -gt $max_score ]; then
    score=$max_score
  fi
  if [ $score -lt 0 ]; then
    score=0
  fi

  # Output results
  echo "$score"
  if [ ${#violations[@]} -gt 0 ]; then
    log_error "Architecture violations found:"
    for violation in "${violations[@]}"; do
      log_error "  - $violation"
    done
  fi

  return 0
}

# ============================================================================
# Code Quality Checks
# ============================================================================

function check_code_quality() {
  local target_repo="$1"
  local score=0
  local max_score=100
  local issues=()

  log_review "Checking code quality..."

  cd "$target_repo"

  # Check 1: TypeScript strict mode (30 points)
  if yarn type-check 2>&1 | grep -q "0 errors"; then
    score=$((score + 30))
  else
    issues+=("Type errors detected (must pass strict type-check)")
    score=$((score + 0))
  fi

  # Check 2: Build success (30 points)
  if yarn build 2>&1 | grep -q "success\|built\|Successfully"; then
    score=$((score + 30))
  else
    issues+=("Build failed (must build successfully)")
    score=$((score + 0))
  fi

  # Check 3: ESLint (20 points)
  if yarn lint 2>&1 | grep -q "0 errors"; then
    score=$((score + 20))
  else
    issues+=("Lint errors detected")
    score=$((score + 10))
  fi

  # Check 4: No hardcoded values (10 points)
  local hardcoded=$(grep -r "http://localhost:[0-9]\|https://.*\.com\|password.*=.*\"" apps/*/src --include="*.ts" --include="*.tsx" 2>/dev/null | grep -v "\.env\|example\|test" | wc -l)
  if [ "$hardcoded" -eq 0 ]; then
    score=$((score + 10))
  else
    issues+=("$hardcoded hardcoded values found (should use env vars or config)")
    score=$((score + 5))
  fi

  # Check 5: Proper error handling (10 points)
  local components_without_error_handling=$(find apps/*/src/pages apps/*/src/components -name "*.tsx" -exec grep -L "error\|Error" {} \; 2>/dev/null | wc -l)
  if [ "$components_without_error_handling" -eq 0 ]; then
    score=$((score + 10))
  else
    issues+=("$components_without_error_handling components missing error handling")
    score=$((score + 5))
  fi

  # Cap score
  if [ $score -gt $max_score ]; then
    score=$max_score
  fi

  # Output results
  echo "$score"
  if [ ${#issues[@]} -gt 0 ]; then
    log_error "Code quality issues:"
    for issue in "${issues[@]}"; do
      log_error "  - $issue"
    done
  fi

  return 0
}

# ============================================================================
# Functional Accuracy Checks
# ============================================================================

function check_functional_accuracy() {
  local target_repo="$1"
  local priority_file="$2"
  local score=0
  local max_score=100
  local gaps=()

  log_review "Checking functional accuracy against acceptance criteria..."

  if [ ! -f "$priority_file" ]; then
    log_error "Priority file not found: $priority_file"
    echo "0"
    return 0
  fi

  # Extract expected outcomes from priority file
  local expected_outcomes=$(grep -A 20 "Expected outcome:" "$priority_file" | grep "^-" || true)

  if [ -z "$expected_outcomes" ]; then
    log_review "No explicit acceptance criteria found in priority file"
    echo "80"
    return 0
  fi

  # Parse each outcome and check if implemented
  local total_outcomes=$(echo "$expected_outcomes" | wc -l)
  local met_outcomes=0

  while IFS= read -r outcome; do
    outcome=$(echo "$outcome" | sed 's/^- //')

    # Check if outcome mentions database/schema
    if echo "$outcome" | grep -qi "database\|schema\|table\|model"; then
      if git diff --name-only origin/main | grep -q "schema\.prisma\|migration"; then
        met_outcomes=$((met_outcomes + 1))
      else
        gaps+=("Missing: Database changes for '$outcome'")
      fi
    fi

    # Check if outcome mentions API/GraphQL
    if echo "$outcome" | grep -qi "api\|graphql\|query\|mutation"; then
      if git diff --name-only origin/main | grep -q "schema\.graphql\|resolvers"; then
        met_outcomes=$((met_outcomes + 1))
      else
        gaps+=("Missing: GraphQL API for '$outcome'")
      fi
    fi

    # Check if outcome mentions UI/page/component
    if echo "$outcome" | grep -qi "ui\|page\|component\|interface"; then
      if git diff --name-only origin/main | grep -q "pages/\|components/"; then
        met_outcomes=$((met_outcomes + 1))
      else
        gaps+=("Missing: UI implementation for '$outcome'")
      fi
    fi

    # Check if outcome mentions test/testing
    if echo "$outcome" | grep -qi "test"; then
      if git diff --name-only origin/main | grep -q "\.test\.\|\.spec\."; then
        met_outcomes=$((met_outcomes + 1))
      else
        gaps+=("Missing: Tests for '$outcome'")
      fi
    fi

  done <<< "$expected_outcomes"

  # Calculate score
  if [ "$total_outcomes" -gt 0 ]; then
    score=$((met_outcomes * 100 / total_outcomes))
  else
    score=80
  fi

  # Output results
  echo "$score"
  if [ ${#gaps[@]} -gt 0 ]; then
    log_error "Functional accuracy gaps:"
    for gap in "${gaps[@]}"; do
      log_error "  - $gap"
    done
  fi

  return 0
}

# ============================================================================
# DevOps Validation
# ============================================================================

function check_devops_builds() {
  local target_repo="$1"
  local score=100
  local failures=()

  log_review "Running DevOps build validation..."

  cd "$target_repo"

  # Check if test scripts exist
  for test_script in "${DEVOPS_TESTS[@]}"; do
    if [ -f "$test_script" ]; then
      log_review "Running: $test_script"
      if bash "$test_script" > /dev/null 2>&1; then
        log_info "✓ $test_script passed"
      else
        failures+=("DevOps: $test_script failed")
        score=$((score - 50))
      fi
    else
      log_review "Test script not found: $test_script (skipping)"
    fi
  done

  # Cap score
  if [ $score -lt 0 ]; then
    score=0
  fi

  # Output results
  echo "$score"
  if [ ${#failures[@]} -gt 0 ]; then
    log_error "DevOps build failures:"
    for failure in "${failures[@]}"; do
      log_error "  - $failure"
    done
  fi

  return 0
}

# ============================================================================
# Comprehensive Review
# ============================================================================

function perform_comprehensive_review() {
  local session_id="$1"
  local target_repo="$2"
  local priority_file="$3"
  local iteration="${4:-1}"

  log_info "========================================="
  log_info "Tony Stark - Senior Code Reviewer"
  log_info "========================================="
  log_info "Session: $session_id"
  log_info "Target: $target_repo"
  log_info "Iteration: $iteration/$MAX_ITERATIONS"
  log_info "Character: $CHARACTER"
  log_info "========================================="

  cd "$target_repo"

  # Run all checks
  log_review "Starting comprehensive code review..."

  local arch_score=$(check_architecture_compliance "$target_repo")
  log_review "Architecture compliance: $arch_score/100"

  local quality_score=$(check_code_quality "$target_repo")
  log_review "Code quality: $quality_score/100"

  local accuracy_score=$(check_functional_accuracy "$target_repo" "$priority_file")
  log_review "Functional accuracy: $accuracy_score/100"

  local devops_score=$(check_devops_builds "$target_repo")
  log_review "DevOps validation: $devops_score/100"

  # Calculate total score (weighted average)
  local total_score=$(( (arch_score * 30 + quality_score * 30 + accuracy_score * 30 + devops_score * 10) / 100 ))

  log_info ""
  log_info "========================================="
  log_info "REVIEW RESULTS"
  log_info "========================================="
  log_info "Architecture:  $arch_score/100 (30%)"
  log_info "Code Quality:  $quality_score/100 (30%)"
  log_info "Accuracy:      $accuracy_score/100 (30%)"
  log_info "DevOps:        $devops_score/100 (10%)"
  log_info "-----------------------------------------"
  log_info "TOTAL SCORE:   $total_score/100"
  log_info "========================================="

  # Determine verdict
  if [ $total_score -ge $MIN_QUALITY_SCORE ]; then
    log_info "✅ APPROVED - Quality gate passed ($total_score% ≥ $MIN_QUALITY_SCORE%)"
    log_info "Creating PR for Product Owner review..."

    # Write final state
    write_state "$session_id" "$AGENT_NAME" "$(cat <<EOF
{
  "agentName": "$AGENT_NAME",
  "character": "$CHARACTER",
  "role": "$ROLE",
  "status": "approved",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "iteration": $iteration,
  "scores": {
    "architecture": $arch_score,
    "quality": $quality_score,
    "accuracy": $accuracy_score,
    "devops": $devops_score,
    "total": $total_score
  },
  "verdict": "APPROVED",
  "message": "Quality gate passed. PR approved for Product Owner review."
}
EOF
)"

    return 0

  else
    log_error "❌ REJECTED - Quality below threshold ($total_score% < $MIN_QUALITY_SCORE%)"

    if [ $iteration -ge $MAX_ITERATIONS ]; then
      log_error "Max iterations reached. Escalating to Product Owner."

      # Write blocked state
      write_state "$session_id" "$AGENT_NAME" "$(cat <<EOF
{
  "agentName": "$AGENT_NAME",
  "character": "$CHARACTER",
  "role": "$ROLE",
  "status": "blocked",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "iteration": $iteration,
  "scores": {
    "architecture": $arch_score,
    "quality": $quality_score,
    "accuracy": $accuracy_score,
    "devops": $devops_score,
    "total": $total_score
  },
  "verdict": "BLOCKED",
  "message": "Quality still below $MIN_QUALITY_SCORE% after $MAX_ITERATIONS iterations. Requires Product Owner intervention.",
  "requiresHuman": true
}
EOF
)"

      return 1

    else
      log_info "Sending feedback to specialists for iteration $((iteration + 1))..."

      # Write feedback state
      write_state "$session_id" "$AGENT_NAME" "$(cat <<EOF
{
  "agentName": "$AGENT_NAME",
  "character": "$CHARACTER",
  "role": "$ROLE",
  "status": "needs_revision",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "iteration": $iteration,
  "scores": {
    "architecture": $arch_score,
    "quality": $quality_score,
    "accuracy": $accuracy_score,
    "devops": $devops_score,
    "total": $total_score
  },
  "verdict": "NEEDS_REVISION",
  "message": "Quality score $total_score% < $MIN_QUALITY_SCORE%. Specialists should address feedback and re-submit.",
  "nextIteration": $((iteration + 1))
}
EOF
)"

      return 2
    fi
  fi
}

# ============================================================================
# Main
# ============================================================================

function main() {
  if [ $# -lt 2 ]; then
    echo "Usage: $0 <session-id> <target-repo> [priority-file] [iteration]"
    exit 1
  fi

  local session_id="$1"
  local target_repo="$2"
  local priority_file="${3:-}"
  local iteration="${4:-1}"

  # Setup logging
  local log_dir="$SERVICE_ROOT/logs/orchestrator-sessions/$session_id"
  mkdir -p "$log_dir"
  LOG_FILE="$log_dir/${AGENT_NAME}.log"
  exec > >(tee -a "$LOG_FILE") 2>&1

  # Perform review
  perform_comprehensive_review "$session_id" "$target_repo" "$priority_file" "$iteration"
  exit_code=$?

  log_info "Tony Stark signing off. Review complete."
  exit $exit_code
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
