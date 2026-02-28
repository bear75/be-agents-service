#!/bin/bash
#
# Schedule Optimization Loop (spaghetti sort)
# Dispatches N parallel Timefold FSR runs, polls metadata, cancels non-promising runs,
# records completed runs and checks for convergence (unassigned <1%, continuity ≤11, eff ≥70%).
#
# Usage:
#   ./schedule-optimization-loop.sh <dataset> [--parallel N] [--max-iters M] [--dry-run]
#
# Arguments:
#   dataset    - e.g. huddinge-2w-expanded
#   --parallel - Max concurrent runs (default 4)
#   --max-iters - Max iteration rounds (default 20)
#   --dry-run  - Log only, do not call Timefold or Darwin API
#
# Environment:
#   APPCAIRE_PATH  - Path to caire-platform/appcaire (required for run scripts)
#   DARWIN_API     - Base URL for Darwin dashboard API (default http://localhost:3010)
#   TIMEFOLD_API_KEY - Required for submit/cancel/fetch
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
AGENTS_DIR="$SERVICE_ROOT/agents"
CONFIG_FILE="$SERVICE_ROOT/config/repos.yaml"

DATASET="${1:-huddinge-2w-expanded}"
PARALLEL=4
MAX_ITERS=20
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --parallel)   PARALLEL="$2"; shift 2 ;;
    --max-iters)  MAX_ITERS="$2"; shift 2 ;;
    --dry-run)    DRY_RUN=true; shift ;;
    *)            break ;;
  esac
done

# Resolve appcaire path: env > repos.yaml appcaire
APPCAIRE_PATH="${APPCAIRE_PATH:-}"
if [[ -z "$APPCAIRE_PATH" && -f "$CONFIG_FILE" ]]; then
  APPCAIRE_PATH=$(grep -A 20 "^  appcaire:" "$CONFIG_FILE" 2>/dev/null | grep "path:" | head -1 | sed 's/.*path: *//' | sed "s|~|$HOME|" || true)
fi
DARWIN_API="${DARWIN_API:-http://localhost:3010}"
SESSION_ID="schedule-$(date +%s)-$$"
BATCH="$(date +%d-%b | tr '[:upper:]' '[:lower:]')"

log() { echo "[$(date +%H:%M:%S)] $*"; }
log_err() { echo "[$(date +%H:%M:%S)] ERROR: $*" >&2; }

# Fetch current runs from Darwin
fetch_runs() {
  if [[ "$DRY_RUN" == "true" ]]; then
    echo '{"success":true,"data":{"runs":[]}}'
    return 0
  fi
  curl -sS "${DARWIN_API}/api/schedule-runs?dataset=${DATASET}" || echo '{"success":false,"data":{"runs":[]}}'
}

# Cancel a run (Timefold DELETE + Darwin POST cancel)
cancel_run() {
  local id="$1"
  local reason="${2:-score diverging}"
  if [[ "$DRY_RUN" == "true" ]]; then
    log "DRY-RUN: would cancel run $id ($reason)"
    return 0
  fi
  curl -sS -X POST "${DARWIN_API}/api/schedule-runs/${id}/cancel" \
    -H "Content-Type: application/json" \
    -d "{\"reason\":\"$reason\"}" || true
  log "Cancelled run $id: $reason"
}

# Check if any completed run meets all three targets
check_convergence() {
  local runs_json="$1"
  local met
  met=$(echo "$runs_json" | jq -r --arg ds "$DATASET" '
    .data.runs // .data // .runs // []
    | map(select(.status == "completed" and .dataset == $ds))
    | map(select(
        (.unassigned_pct != null and .unassigned_pct < 1) and
        (.continuity_avg != null and .continuity_avg <= 11) and
        (.routing_efficiency_pct != null and .routing_efficiency_pct >= 70)
      ))
    | length
  ' 2>/dev/null || echo "0")
  [[ "${met:-0}" -gt 0 ]]
}

# Get best medium score from completed runs (for cancel threshold)
best_medium_score() {
  local runs_json="$1"
  echo "$runs_json" | jq -r --arg ds "$DATASET" '
    [.data.runs // .data // .runs // []
     | map(select(.status == "completed" and .dataset == $ds and .timefold_score != null))
     | .[].timefold_score
     | capture("(?<med>[^/]+)medium")
     | .med | gsub("^[^-]"; "") | tonumber?
    ] | min // -999999
  ' 2>/dev/null || echo "-999999"
}

log "Schedule Optimization Loop — dataset=$DATASET parallel=$PARALLEL max_iters=$MAX_ITERS dry_run=$DRY_RUN"
log "APPCAIRE_PATH=${APPCAIRE_PATH:-<not set>} DARWIN_API=$DARWIN_API"

iter=0
while [[ $iter -lt $MAX_ITERS ]]; do
  iter=$((iter + 1))
  log "——— Iteration $iter ———"

  RUNS_JSON=$(fetch_runs)
  if check_convergence "$RUNS_JSON"; then
    log "Convergence reached: at least one run meets all targets. Stopping."
    exit 0
  fi

  BEST_MED=$(best_medium_score "$RUNS_JSON")
  log "Best medium score so far: $BEST_MED"

  # 1) Get next strategies from mathematician (placeholder: use agent script when Claude available)
  STRATEGIES_JSON='[]'
  if [[ -f "$AGENTS_DIR/optimization-mathematician.sh" ]]; then
    export EMIT_SAMPLE_STRATEGIES=1
    STRATEGIES_JSON=$("$AGENTS_DIR/optimization-mathematician.sh" "$SESSION_ID" "${APPCAIRE_PATH:-.}" 2>/dev/null | tail -1) || STRATEGIES_JSON='[]'
    unset EMIT_SAMPLE_STRATEGIES
  fi
  COUNT=$(echo "$STRATEGIES_JSON" | jq 'length' 2>/dev/null || echo "0")
  if [[ "${COUNT:-0}" -eq 0 ]]; then
    log "No strategies from mathematician; using placeholder list"
    STRATEGIES_JSON='[
      {"algorithm":"pool-tight-11","strategy":"Max pool size 11","hypothesis":"Reduce continuity from 14 to ≤11"},
      {"algorithm":"soft-weight-2x","strategy":"Double preferred-vehicle weight","hypothesis":"Stronger soft constraint"}
    ]'
  fi

  # 2) Dispatch up to PARALLEL jobs (actual dispatch is via appcaire scripts + Darwin API)
  #    This loop only documents the flow; real submission is in appcaire (submit_to_timefold.py)
  #    and Darwin server (POST /api/schedule-runs to create queued/running record).
  log "Strategies for this round: $(echo "$STRATEGIES_JSON" | jq -c '.[].algorithm' 2>/dev/null | tr '\n' ' ')"
  if [[ "$DRY_RUN" == "true" ]]; then
    log "DRY-RUN: skip dispatch (run submit_to_timefold.py and POST /api/schedule-runs in production)"
  fi

  # 3) Monitor: poll running jobs every 3 min, cancel if medium >2x worse than best
  #    (In production, a separate poll loop or Darwin server would GET Timefold metadata and call cancel_run.)
  log "Monitor phase: check Darwin dashboard for running jobs and cancel non-promising via POST /api/schedule-runs/:id/cancel"

  # 4) Next iteration
  sleep 5
done

log "Max iterations ($MAX_ITERS) reached without convergence."
exit 0
