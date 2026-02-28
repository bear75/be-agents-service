#!/bin/bash
#
# Timefold Specialist Agent
# Submits, monitors, and cancels Timefold FSR optimization jobs.
# Runs metrics and continuity scripts in appcaire repo; writes results to DB.
#
# Usage:
#   ./timefold-specialist.sh <session_id> <appcaire_repo> [strategy_json_path]
#
# Arguments:
#   session_id         - Session ID for state coordination
#   appcaire_repo      - Path to caire-platform/appcaire (data + scripts)
#   strategy_json_path - Optional path to JSON with algorithm, strategy, hypothesis
#
# Exit codes:
#   0 - Success (job completed, metrics/continuity run, DB updated)
#   1 - Blocked or job failed
#   2 - Script error
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LIB_DIR="$SERVICE_ROOT/lib"

# Configuration
SESSION_ID="${1:-}"
APPCAIRE_REPO="${2:-}"
STRATEGY_JSON="${3:-}"
PROMPT_FILE="$SCRIPT_DIR/prompts/timefold-specialist.md"
LOG_DIR="$SERVICE_ROOT/logs/timefold-sessions"
RECURRING_DIR="${APPCAIRE_REPO}/docs_2.0/recurring-visits"
SCRIPTS_DIR="${RECURRING_DIR}/scripts"
HUDDINGE_DIR="${RECURRING_DIR}/huddinge-package"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[TIMEFOLD]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[TIMEFOLD]${NC} $1"; }
log_error() { echo -e "${RED}[TIMEFOLD]${NC} $1"; }

if [[ -z "$SESSION_ID" || -z "$APPCAIRE_REPO" ]]; then
  log_error "Missing required arguments"
  echo "Usage: $0 <session_id> <appcaire_repo> [strategy_json_path]"
  exit 2
fi

if [[ ! -d "$APPCAIRE_REPO" ]]; then
  log_error "Appcaire repo not found: $APPCAIRE_REPO"
  exit 2
fi

if [[ ! -f "$PROMPT_FILE" ]]; then
  log_error "Prompt not found: $PROMPT_FILE"
  exit 2
fi

if [[ ! -d "$SCRIPTS_DIR" ]]; then
  log_error "Scripts dir not found: $SCRIPTS_DIR"
  exit 2
fi

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/${SESSION_ID}.log"

log_info "Session: $SESSION_ID | Appcaire: $APPCAIRE_REPO" | tee -a "$LOG_FILE"
if [[ -n "$STRATEGY_JSON" && -f "$STRATEGY_JSON" ]]; then
  log_info "Strategy: $STRATEGY_JSON" | tee -a "$LOG_FILE"
fi

# Optional: source state manager if available
if [[ -f "$LIB_DIR/state-manager.sh" ]]; then
  # shellcheck source=../lib/state-manager.sh
  source "$LIB_DIR/state-manager.sh"
  export COMPOUND_STATE_DIR="${SERVICE_ROOT}/.compound-state"
fi

# Delegate to Claude Code CLI with specialist prompt when available.
# Until then, this script is a stub that validates env and logs intent.
# The schedule-optimization-loop.sh will call Python/curl for submit/poll/cancel.
if command -v claude >/dev/null 2>&1; then
  log_info "Invoking Claude with timefold-specialist prompt..." | tee -a "$LOG_FILE"
  cd "$APPCAIRE_REPO"
  export TIMEFOLD_SESSION_ID="$SESSION_ID"
  export TIMEFOLD_STRATEGY_JSON="$STRATEGY_JSON"
  # Claude Code would run here with prompt file and context
  log_warn "Claude CLI integration placeholder — use schedule-optimization-loop.sh for full pipeline" | tee -a "$LOG_FILE"
else
  log_info "Claude CLI not in PATH; timefold-specialist is ready for loop-driven invocation" | tee -a "$LOG_FILE"
fi

log_info "Timefold specialist setup complete. Use scripts/compound/schedule-optimization-loop.sh to dispatch jobs." | tee -a "$LOG_FILE"
exit 0
