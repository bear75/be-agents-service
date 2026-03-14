#!/bin/bash
#
# Optimization Mathematician Agent
# Proposes optimization strategies based on research state and history.
# Called by schedule-research-loop.sh to determine next experiment.
#
# Usage:
#   ./optimization-mathematician.sh --dataset <dataset> --iteration <N> --state <state_json>
#
# Arguments:
#   --dataset    - Dataset name (e.g., huddinge-v3)
#   --iteration  - Current iteration number
#   --state      - Research state JSON (history, best result, etc.)
#
# Output (stdout): JSON object with:
#   {
#     "experiment_id": "unique-id",
#     "strategy": "strategy-name",
#     "hypothesis": "Expected outcome"
#   }
#
# Exit codes:
#   0 - Success
#   1 - Error
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROMPT_FILE="$SCRIPT_DIR/prompts/optimization-mathematician.md"

# Parse arguments
DATASET=""
ITERATION=""
STATE=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --dataset)
      DATASET="$2"
      shift 2
      ;;
    --iteration)
      ITERATION="$2"
      shift 2
      ;;
    --state)
      STATE="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$DATASET" || -z "$ITERATION" ]]; then
  echo "Error: Missing required arguments" >&2
  echo "Usage: $0 --dataset <dataset> --iteration <N> --state <state_json>" >&2
  exit 1
fi

# For now, return a simple test strategy
# In production, this would:
# 1. Analyze state.history to see what's been tried
# 2. Check state.best_result for current baseline
# 3. Propose novel strategy based on learnings
# 4. Use Claude CLI to generate sophisticated strategies

# Generate experiment ID
EXPERIMENT_ID="exp_$(date +%s)_iter${ITERATION}"

# Determine strategy based on iteration
if [[ "$ITERATION" -eq 1 ]]; then
  STRATEGY="pool_size_5"
  HYPOTHESIS="Test baseline with pool size 5 (known good configuration)"
elif [[ "$ITERATION" -eq 2 ]]; then
  STRATEGY="pool_size_8"
  HYPOTHESIS="Increase pool size to 8 for more flexibility, may reduce continuity"
else
  STRATEGY="pool_size_3"
  HYPOTHESIS="Reduce pool size to 3 for tighter continuity, may increase unassigned"
fi

# Output JSON as single line (compact) so tail -1 works
cat <<EOF | jq -c .
{
  "experiment_id": "$EXPERIMENT_ID",
  "strategy": "$STRATEGY",
  "hypothesis": "$HYPOTHESIS"
}
EOF

exit 0
