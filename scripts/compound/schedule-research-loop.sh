#!/bin/bash
#
# Schedule Research Loop (AI-Powered Autonomous Optimization)
# Implements the Schedule Research Program (docs/SCHEDULE_RESEARCH_PROGRAM.md)
#
# This script orchestrates the mathematician and specialist agents to:
# 1. Propose optimization strategies
# 2. Execute experiments via Timefold API
# 3. Evaluate results and update research state
# 4. Learn from successes and failures
# 5. Converge toward goal metrics or stop at max iterations/plateau
#
# Usage:
#   ./schedule-research-loop.sh <dataset> [max_iterations] [strategies_filter]
#
# Arguments:
#   dataset          - Dataset name (default: huddinge-v3)
#   max_iterations   - Max iterations before stopping (default: 50)
#   strategies_filter - Comma-separated strategy names to filter (optional)
#
# Environment:
#   AGENT_SERVICE_URL - be-agent-service API URL (default: http://localhost:3010)
#   DATASET           - Override dataset name
#   MAX_ITERATIONS    - Override max iterations
#   TIMEFOLD_API_KEY  - Required for Timefold API calls
#   DRY_RUN           - Set to "true" to simulate without API calls
#
# Exit Codes:
#   0 - Success (goals met or max iterations reached)
#   1 - Error (configuration, API, or script error)
#   2 - Cancelled by user
#

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
AGENTS_DIR="$SERVICE_ROOT/agents"
SCRIPTS_TIMEFOLD="$SERVICE_ROOT/scripts/timefold"
DATA_DIR="$SERVICE_ROOT/recurring-visits/data"

# Parse arguments
DATASET="${1:-${DATASET:-huddinge-v3}}"
MAX_ITERATIONS="${2:-${MAX_ITERATIONS:-50}}"
STRATEGIES_FILTER="${3:-}"

# API configuration
AGENT_SERVICE_URL="${AGENT_SERVICE_URL:-http://localhost:3010}"
DRY_RUN="${DRY_RUN:-false}"

# Logging
LOG_FILE="${LOG_FILE:-$SERVICE_ROOT/logs/research/${DATASET}_$(date +%Y%m%d_%H%M%S).log}"
mkdir -p "$(dirname "$LOG_FILE")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

log() {
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
  echo -e "$msg" | tee -a "$LOG_FILE" >&2
}

log_info() {
  log "${BLUE}[INFO]${NC} $*"
}

log_success() {
  log "${GREEN}[SUCCESS]${NC} $*"
}

log_warn() {
  log "${YELLOW}[WARN]${NC} $*"
}

log_error() {
  log "${RED}[ERROR]${NC} $*"
}

# ============================================================================
# API FUNCTIONS
# ============================================================================

# Get research state from API
get_research_state() {
  if [[ "$DRY_RUN" == "true" ]]; then
    echo '{"success":true,"data":{"state":{"iteration_count":0,"current_status":"idle","plateau_count":0},"history":[],"learnings":[]}}'
    return 0
  fi

  local response
  response=$(curl -sS "${AGENT_SERVICE_URL}/api/schedule-runs/research/state?dataset=${DATASET}" 2>/dev/null)
  if [[ $? -eq 0 && -n "$response" ]]; then
    echo "$response"
  else
    echo '{"success":false}'
  fi
}

# Update research state via API
update_research_state() {
  local updates="$1"

  if [[ "$DRY_RUN" == "true" ]]; then
    log_info "DRY-RUN: Would update research state: $updates"
    return 0
  fi

  curl -sS -X POST "${AGENT_SERVICE_URL}/api/schedule-runs/research/state" \
    -H "Content-Type: application/json" \
    -d "{\"dataset\":\"$DATASET\",\"updates\":$updates}" || true
}

# Increment iteration counter
increment_iteration() {
  local state=$(get_research_state)
  local current=$(echo "$state" | jq -r '.data.state.iteration_count // 0')
  local new=$((current + 1))

  if [[ "$DRY_RUN" != "true" ]]; then
    update_research_state "{\"iteration_count\":$new}"
  fi

  echo "$new"
}

# Register run to database
register_run() {
  local job_id="$1"
  local strategy="$2"
  local metrics="$3"

  if [[ "$DRY_RUN" == "true" ]]; then
    log_info "DRY-RUN: Would register run: job_id=$job_id strategy=$strategy"
    return 0
  fi

  curl -sS -X POST "${AGENT_SERVICE_URL}/api/schedule-runs/register" \
    -H "Content-Type: application/json" \
    -d "{
      \"id\":\"$job_id\",
      \"dataset\":\"$DATASET\",
      \"strategy\":\"$strategy\",
      \"status\":\"completed\",
      $(echo "$metrics" | jq -c '{
        continuity_avg,
        continuity_max,
        unassigned_pct,
        routing_efficiency_pct,
        total_visits,
        unassigned_visits
      }')
    }" || true
}

# ============================================================================
# RESEARCH STATE CHECKS
# ============================================================================

# Check if goals are met
check_goals_met() {
  local state="$1"

  local continuity_avg=$(echo "$state" | jq -r '.data.state.best_continuity_avg // 999')
  local continuity_max=$(echo "$state" | jq -r '.data.state.best_continuity_max // 999')
  local unassigned_pct=$(echo "$state" | jq -r '.data.state.best_unassigned_pct // 999')
  local efficiency=$(echo "$state" | jq -r '.data.state.best_efficiency_pct // 0')

  local goal_continuity_avg=$(echo "$state" | jq -r '.data.state.goal_continuity_avg // 11.0')
  local goal_continuity_max=$(echo "$state" | jq -r '.data.state.goal_continuity_max // 20.0')
  local goal_unassigned_pct=$(echo "$state" | jq -r '.data.state.goal_unassigned_pct // 1.0')
  local goal_efficiency=$(echo "$state" | jq -r '.data.state.goal_efficiency_pct // 70.0')

  if (( $(echo "$continuity_avg <= $goal_continuity_avg" | bc -l) )) && \
     (( $(echo "$continuity_max <= $goal_continuity_max" | bc -l) )) && \
     (( $(echo "$unassigned_pct < $goal_unassigned_pct" | bc -l) )) && \
     (( $(echo "$efficiency > $goal_efficiency" | bc -l) )); then
    return 0
  else
    return 1
  fi
}

# Check if plateau detected (no improvement for 5+ iterations)
check_plateau() {
  local state="$1"
  local plateau_count=$(echo "$state" | jq -r '.data.state.plateau_count // 0')

  if [[ $plateau_count -ge 5 ]]; then
    return 0
  else
    return 1
  fi
}

# ============================================================================
# AGENT ORCHESTRATION
# ============================================================================

# Call mathematician agent to propose strategy
get_strategy_from_mathematician() {
  local state="$1"
  local iteration="$2"

  log_info "Calling optimization mathematician agent..."

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "{\"experiment_id\":\"pool5_test\",\"strategy\":\"pool_size_5\",\"hypothesis\":\"Test pool size 5\"}"
    return 0
  fi

  # Call mathematician agent with state context
  local strategy
  strategy=$("$AGENTS_DIR/optimization-mathematician.sh" \
    --dataset "$DATASET" \
    --iteration "$iteration" \
    --state "$state" 2>&1 | tail -1) || echo "{}"

  # Validate strategy JSON
  if ! echo "$strategy" | jq -e . >/dev/null 2>&1; then
    log_error "Invalid strategy JSON from mathematician: $strategy"
    echo "{\"experiment_id\":\"fallback_pool5\",\"strategy\":\"pool5_baseline\",\"hypothesis\":\"Fallback to pool 5 baseline\"}"
    return 1
  fi

  echo "$strategy"
}

# Call specialist agent to execute strategy
execute_strategy_via_specialist() {
  local strategy="$1"

  log_info "Calling timefold specialist agent to execute strategy..."

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "{\"job_id\":\"test_job_123\",\"status\":\"completed\",\"metrics\":{\"continuity_avg\":13.5,\"efficiency\":88.0,\"unassigned_pct\":0.2}}"
    return 0
  fi

  # Call specialist agent with strategy
  local result
  result=$("$AGENTS_DIR/timefold-specialist.sh" \
    --dataset "$DATASET" \
    --strategy "$strategy" 2>&1 | tail -1) || echo "{}"

  # Validate result JSON
  if ! echo "$result" | jq -e . >/dev/null 2>&1; then
    log_error "Invalid result JSON from specialist: $result"
    return 1
  fi

  echo "$result"
}

# Evaluate result vs. best
evaluate_result() {
  local result="$1"
  local state="$2"

  local new_continuity=$(echo "$result" | jq -r '.metrics.continuity_avg // 999')
  local best_continuity=$(echo "$state" | jq -r '.data.state.best_continuity_avg // 999')

  local new_efficiency=$(echo "$result" | jq -r '.metrics.routing_efficiency_pct // 0')
  local best_efficiency=$(echo "$state" | jq -r '.data.state.best_efficiency_pct // 0')

  local new_unassigned=$(echo "$result" | jq -r '.metrics.unassigned_pct // 999')
  local best_unassigned=$(echo "$state" | jq -r '.data.state.best_unassigned_pct // 999')

  # Decision logic
  local decision="continue"
  local reason=""

  # Kill if worse across all metrics
  if (( $(echo "$new_continuity > $best_continuity" | bc -l) )) && \
     (( $(echo "$new_efficiency < $best_efficiency" | bc -l) )) && \
     (( $(echo "$new_unassigned > $best_unassigned" | bc -l) )); then
    decision="kill"
    reason="Worse than baseline across all metrics"
  # Double down if significant improvement
  elif (( $(echo "$new_continuity < ($best_continuity - 2.0)" | bc -l) )) || \
       (( $(echo "$new_efficiency > ($best_efficiency + 5.0)" | bc -l) )); then
    decision="double_down"
    reason="Significant improvement (continuity -$(echo "$best_continuity - $new_continuity" | bc -l) or efficiency +$(echo "$new_efficiency - $best_efficiency" | bc -l))"
  # Keep if any improvement
  elif (( $(echo "$new_continuity < $best_continuity" | bc -l) )) || \
       (( $(echo "$new_efficiency > $best_efficiency" | bc -l) )) || \
       (( $(echo "$new_unassigned < $best_unassigned" | bc -l) )); then
    decision="keep"
    reason="Improvement in at least one metric"
  else
    decision="continue"
    reason="No significant change, continue exploration"
  fi

  echo "{\"decision\":\"$decision\",\"reason\":\"$reason\"}"
}

# Trigger deep research
trigger_deep_research() {
  local state="$1"

  log_warn "🔬 Plateau detected! Triggering deep research..."

  # TODO: Implement deep research agent
  # - Search Timefold docs
  # - Analyze run history patterns
  # - Research industry approaches
  # - Propose novel strategies

  log_info "Deep research triggered (placeholder - implement deep-research agent)"
}

# ============================================================================
# MAIN RESEARCH LOOP
# ============================================================================

log_info "======================================================================"
log_info "Schedule Research Loop Started"
log_info "======================================================================"
log_info "Dataset: $DATASET"
log_info "Max Iterations: $MAX_ITERATIONS"
log_info "API URL: $AGENT_SERVICE_URL"
log_info "Dry Run: $DRY_RUN"
log_info "Log File: $LOG_FILE"
log_info "======================================================================"

# Initialize research state
STATE=$(get_research_state)
if ! echo "$STATE" | jq -e '.success' >/dev/null 2>&1; then
  log_error "Failed to get research state. Is the server running at $AGENT_SERVICE_URL?"
  exit 1
fi

# Main loop
iteration=0
while [[ $iteration -lt $MAX_ITERATIONS ]]; do
  iteration=$((iteration + 1))

  # Update API state (only in non-dry-run mode)
  if [[ "$DRY_RUN" != "true" ]]; then
    update_research_state "{\"iteration_count\":$iteration}"
  fi

  log_info ""
  log_info "======================================================================"
  log_info "Iteration $iteration / $MAX_ITERATIONS"
  log_info "======================================================================"

  # Reload state
  STATE=$(get_research_state)

  # Check stopping conditions
  if check_goals_met "$STATE"; then
    log_success "🎯 GOALS ACHIEVED!"
    log_success "Continuity: $(echo "$STATE" | jq -r '.data.state.best_continuity_avg') (goal: ≤11.0)"
    log_success "Efficiency: $(echo "$STATE" | jq -r '.data.state.best_efficiency_pct')% (goal: >70%)"
    log_success "Unassigned: $(echo "$STATE" | jq -r '.data.state.best_unassigned_pct')% (goal: <1%)"
    log_success "Best Job ID: $(echo "$STATE" | jq -r '.data.state.best_job_id')"
    exit 0
  fi

  if check_plateau "$STATE"; then
    trigger_deep_research "$STATE"
  fi

  # Get strategy from mathematician
  STRATEGY=$(get_strategy_from_mathematician "$STATE" "$iteration")
  if [[ $? -ne 0 ]]; then
    log_warn "Mathematician failed to propose strategy, using fallback"
  fi

  experiment_id=$(echo "$STRATEGY" | jq -r '.experiment_id // "unknown"')
  strategy_name=$(echo "$STRATEGY" | jq -r '.strategy // "unknown"')
  hypothesis=$(echo "$STRATEGY" | jq -r '.hypothesis // "No hypothesis"')

  log_info "Experiment: $experiment_id"
  log_info "Strategy: $strategy_name"
  log_info "Hypothesis: $hypothesis"

  # Execute strategy via specialist
  RESULT=$(execute_strategy_via_specialist "$STRATEGY")
  if [[ $? -ne 0 ]]; then
    log_error "Specialist failed to execute strategy"
    continue
  fi

  job_id=$(echo "$RESULT" | jq -r '.job_id // "unknown"')
  status=$(echo "$RESULT" | jq -r '.status // "unknown"')
  metrics=$(echo "$RESULT" | jq -c '.metrics // {}')

  log_info "Job ID: $job_id"
  log_info "Status: $status"
  log_info "Metrics: $(echo "$metrics" | jq -c .)"

  # Register run to database
  register_run "$job_id" "$strategy_name" "$metrics"

  # Evaluate result
  EVALUATION=$(evaluate_result "$RESULT" "$STATE")
  decision=$(echo "$EVALUATION" | jq -r '.decision')
  reason=$(echo "$EVALUATION" | jq -r '.reason')

  log_info "Decision: $decision"
  log_info "Reason: $reason"

  # Update research state based on decision
  if [[ "$decision" == "keep" ]] || [[ "$decision" == "double_down" ]]; then
    log_success "✓ Result accepted: $reason"
    # TODO: Update best result if improved
  elif [[ "$decision" == "kill" ]]; then
    log_warn "✗ Result rejected: $reason"
  fi

  # Sleep between iterations
  sleep 2
done

log_warn "Max iterations ($MAX_ITERATIONS) reached without achieving goals"
log_info "Best result so far:"
log_info "  Continuity: $(echo "$STATE" | jq -r '.data.state.best_continuity_avg // "N/A"')"
log_info "  Efficiency: $(echo "$STATE" | jq -r '.data.state.best_efficiency_pct // "N/A"')%"
log_info "  Unassigned: $(echo "$STATE" | jq -r '.data.state.best_unassigned_pct // "N/A"')%"
log_info "  Job ID: $(echo "$STATE" | jq -r '.data.state.best_job_id // "N/A"')"

exit 0
