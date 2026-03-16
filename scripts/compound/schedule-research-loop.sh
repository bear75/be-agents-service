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
#   TRIM_SHIFTS_FROM_INPUT - Set to "1" to trim shifts before loop (smaller/faster solves)
#   TRIM_INPUT_SOURCE - Input to trim (default: data/DATASET/input/input_DATASET_FIXED.json)
#   TRIM_MAX_SHIFTS_PER_VEHICLE - Cap shifts per vehicle when no TRIM_SOLUTION (default 10)
#   TRIM_SOLUTION    - If set, keep only vehicles/shifts used in this solution JSON
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

# Optional: trim shifts from input before loop (uses trim_shifts_from_input.py)
# Set TRIM_SHIFTS_FROM_INPUT=1 to enable. Optionally set TRIM_INPUT_SOURCE (default:
# data/DATASET/input/input_DATASET_FIXED.json), TRIM_MAX_SHIFTS_PER_VEHICLE (default 10),
# or TRIM_SOLUTION (path to solution JSON for solution-based trim).
TRIM_SHIFTS_FROM_INPUT="${TRIM_SHIFTS_FROM_INPUT:-0}"

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

# Register run to database (body built with jq to avoid control chars / invalid JSON)
register_run() {
  local job_id="$1"
  local strategy="$2"
  local metrics="$3"

  if [[ "$DRY_RUN" == "true" ]]; then
    log_info "DRY-RUN: Would register run: job_id=$job_id strategy=$strategy"
    return 0
  fi

  # Ensure metrics is valid JSON (empty object if not)
  local metrics_json="{}"
  if echo "$metrics" | jq -e . >/dev/null 2>&1; then
    metrics_json="$metrics"
  fi

  local body
  body=$(jq -n -c \
    --arg id "$job_id" \
    --arg dataset "$DATASET" \
    --arg strategy "$strategy" \
    --argjson m "$metrics_json" \
    '{
      id: $id,
      dataset: $dataset,
      strategy: $strategy,
      status: "completed",
      continuity_avg: ($m.continuity_avg),
      continuity_max: ($m.continuity_max),
      unassigned_pct: ($m.unassigned_pct),
      routing_efficiency_pct: ($m.routing_efficiency_pct),
      total_visits: ($m.total_visits),
      unassigned_visits: ($m.unassigned_visits)
    }') || return 0

  curl -sS -X POST "${AGENT_SERVICE_URL}/api/schedule-runs/register" \
    -H "Content-Type: application/json" \
    -d "$body" || true
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

  # Call specialist; only stdout is the final JSON line (stderr is logged separately)
  local raw_output result
  raw_output=$("$AGENTS_DIR/timefold-specialist.sh" \
    --dataset "$DATASET" \
    --strategy "$strategy" 2>>"$LOG_FILE") || true
  # Take first line that is valid JSON (in case of any stray output)
  result=""
  while IFS= read -r line; do
    if echo "$line" | jq -e . >/dev/null 2>&1; then
      result="$line"
      break
    fi
  done <<< "$raw_output"
  if [[ -z "$result" ]]; then
    result=$(echo "$raw_output" | tail -1)
  fi
  if ! echo "$result" | jq -e . >/dev/null 2>&1; then
    log_error "Invalid result JSON from specialist (last line): ${result:0:200}"
    echo "{}"
    return 1
  fi
  echo "$result"
}

# Coerce to numeric for bc (strip newlines, default to fallback)
_safe_num() {
  local val="${1:-}"
  local fallback="${2:-0}"
  val=$(echo "$val" | tr -d '\n\r' | head -1)
  if [[ -z "$val" ]] || [[ "$val" == "null" ]]; then
    echo "$fallback"
    return
  fi
  if [[ "$val" =~ ^-?[0-9]+\.?[0-9]*$ ]]; then
    echo "$val"
  else
    echo "$fallback"
  fi
}

# Evaluate result vs. best (safe when metrics or state are missing)
evaluate_result() {
  local result="$1"
  local state="$2"

  local new_continuity=$(_safe_num "$(echo "$result" | jq -r '.metrics.continuity_avg // empty')" "999")
  local best_continuity=$(_safe_num "$(echo "$state" | jq -r '.data.state.best_continuity_avg // empty')" "999")
  local new_efficiency=$(_safe_num "$(echo "$result" | jq -r '.metrics.routing_efficiency_pct // empty')" "0")
  local best_efficiency=$(_safe_num "$(echo "$state" | jq -r '.data.state.best_efficiency_pct // empty')" "0")
  local new_unassigned=$(_safe_num "$(echo "$result" | jq -r '.metrics.unassigned_pct // empty')" "999")
  local best_unassigned=$(_safe_num "$(echo "$state" | jq -r '.data.state.best_unassigned_pct // empty')" "999")

  local decision="continue"
  local reason=""

  # bc with -l can fail on empty; ensure we pass numbers
  local c_gt_b=$(echo "$new_continuity > $best_continuity" | bc -l 2>/dev/null || echo "0")
  local e_lt_b=$(echo "$new_efficiency < $best_efficiency" | bc -l 2>/dev/null || echo "0")
  local u_gt_b=$(echo "$new_unassigned > $best_unassigned" | bc -l 2>/dev/null || echo "0")
  if [[ "${c_gt_b:-0}" == "1" ]] && [[ "${e_lt_b:-0}" == "1" ]] && [[ "${u_gt_b:-0}" == "1" ]]; then
    decision="kill"
    reason="Worse than baseline across all metrics"
  else
    local c_improve=$(echo "$new_continuity < ($best_continuity - 2.0)" | bc -l 2>/dev/null || echo "0")
    local e_improve=$(echo "$new_efficiency > ($best_efficiency + 5.0)" | bc -l 2>/dev/null || echo "0")
    if [[ "${c_improve:-0}" == "1" ]] || [[ "${e_improve:-0}" == "1" ]]; then
      decision="double_down"
      reason="Significant improvement (continuity or efficiency)"
    else
      local c_better=$(echo "$new_continuity < $best_continuity" | bc -l 2>/dev/null || echo "0")
      local e_better=$(echo "$new_efficiency > $best_efficiency" | bc -l 2>/dev/null || echo "0")
      local u_better=$(echo "$new_unassigned < $best_unassigned" | bc -l 2>/dev/null || echo "0")
      if [[ "${c_better:-0}" == "1" ]] || [[ "${e_better:-0}" == "1" ]] || [[ "${u_better:-0}" == "1" ]]; then
        decision="keep"
        reason="Improvement in at least one metric"
      else
        reason="No significant change, continue exploration"
      fi
    fi
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

# Optional: trim shifts from input (reduces solve size; specialist will use _trimmed.json)
if [[ "$TRIM_SHIFTS_FROM_INPUT" == "1" ]]; then
  TRIM_INPUT_SOURCE="${TRIM_INPUT_SOURCE:-$DATA_DIR/$DATASET/input/input_${DATASET}_FIXED.json}"
  TRIM_OUTPUT="$DATA_DIR/$DATASET/input/input_${DATASET}_FIXED_trimmed.json"
  if [[ -f "$TRIM_INPUT_SOURCE" ]]; then
    log_info "Trimming shifts from input: $TRIM_INPUT_SOURCE -> $TRIM_OUTPUT"
    if [[ -n "${TRIM_SOLUTION:-}" && -f "$TRIM_SOLUTION" ]]; then
      python3 "$SERVICE_ROOT/scripts/conversion/trim_shifts_from_input.py" \
        --input "$TRIM_INPUT_SOURCE" --solution "$TRIM_SOLUTION" -o "$TRIM_OUTPUT" 2>&1 | tee -a "$LOG_FILE" || true
    else
      python3 "$SERVICE_ROOT/scripts/conversion/trim_shifts_from_input.py" \
        --input "$TRIM_INPUT_SOURCE" --max-shifts-per-vehicle "${TRIM_MAX_SHIFTS_PER_VEHICLE:-10}" -o "$TRIM_OUTPUT" 2>&1 | tee -a "$LOG_FILE" || true
    fi
    if [[ -f "$TRIM_OUTPUT" ]]; then
      log_success "Trimmed input ready; specialist will use it"
    else
      log_warn "Trim failed; specialist will use original input"
    fi
  else
    log_warn "Trim requested but TRIM_INPUT_SOURCE not found: $TRIM_INPUT_SOURCE"
  fi
fi

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
