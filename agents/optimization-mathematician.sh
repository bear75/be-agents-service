#!/bin/bash
#
# Optimization Mathematician Agent
# Analyses completed schedule runs, proposes next N strategies (exploitation + exploration).
# Outputs JSON array of strategy configs for the schedule-optimization loop.
#
# Usage:
#   ./optimization-mathematician.sh <session_id> <appcaire_repo> [runs_json_path]
#
# Arguments:
#   session_id     - Session ID for state coordination
#   appcaire_repo  - Path to caire-platform/appcaire
#   runs_json_path - Optional: path to JSON of completed runs (else read from API)
#
# Output (stdout): JSON array of strategy configs, e.g.:
#   [{"algorithm":"pool-tight-11","strategy":"...","hypothesis":"..."}, ...]
#
# Exit codes:
#   0 - Success
#   1 - Blocked (no data, invalid input)
#   2 - Script error
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROMPT_FILE="$SCRIPT_DIR/prompts/optimization-mathematician.md"
LOG_DIR="$SERVICE_ROOT/logs/optimization-mathematician"

SESSION_ID="${1:-}"
APPCAIRE_REPO="${2:-}"
RUNS_JSON="${3:-}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[MATH]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[MATH]${NC} $1"; }
log_error() { echo -e "${RED}[MATH]${NC} $1"; }

if [[ -z "$SESSION_ID" || -z "$APPCAIRE_REPO" ]]; then
  log_error "Missing required arguments"
  echo "Usage: $0 <session_id> <appcaire_repo> [runs_json_path]"
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

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/${SESSION_ID}.log"

log_info "Session: $SESSION_ID | Appcaire: $APPCAIRE_REPO" | tee -a "$LOG_FILE"

# When Claude CLI is used, this script would invoke it with runs data and prompt.
# Output is expected to be a JSON array of strategy configs.
if command -v claude >/dev/null 2>&1; then
  log_info "Claude CLI available; mathematician prompt ready for loop invocation" | tee -a "$LOG_FILE"
else
  log_info "Mathematician prompt ready; use schedule-optimization-loop.sh with GET /api/schedule-runs for input" | tee -a "$LOG_FILE"
fi

# Placeholder: emit a minimal valid strategy list so the loop can be tested
# In production the loop passes runs JSON to Claude and parses stdout for strategies.
if [[ -n "${EMIT_SAMPLE_STRATEGIES:-}" ]]; then
  cat <<'EOF'
[
  {"algorithm":"pool-tight-11","strategy":"Same as 82a338b9 but max pool size = 11","hypothesis":"Reduce continuity from 14 to ≤11 by tightening vehicle pool"},
  {"algorithm":"soft-weight-2x","strategy":"Double preferred-vehicle weight in Timefold config","hypothesis":"Stronger soft constraint improves continuity without losing assignments"}
]
EOF
fi

exit 0
