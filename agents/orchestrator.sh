#!/bin/bash
#
# Orchestrator (Scrum Master) - Engineering team coordinator
# Delegates to scripts/orchestrator.sh for actual coordination
#
# Usage:
#   ./orchestrator.sh <session_id> <target_repo> <priority_file> [branch_name]
#
# Arguments:
#   session_id    - Session ID for state coordination
#   target_repo   - Path to target repository
#   priority_file - Path to priority markdown file
#   branch_name   - Optional feature branch name
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MAIN_ORCHESTRATOR="$SERVICE_ROOT/scripts/orchestrator.sh"

if [[ ! -f "$MAIN_ORCHESTRATOR" ]]; then
  echo "[ORCHESTRATOR] Error: scripts/orchestrator.sh not found"
  exit 2
fi

# Forward: scripts/orchestrator.sh expects target_repo priority_file prd_file branch_name
TARGET_REPO="${2:-}"
PRIORITY_FILE="${3:-}"
PRD_FILE="${TARGET_REPO}/tasks/prd.json"
BRANCH_NAME="${4:-feature/agent-priority-$(date +%Y%m%d-%H%M)}"

exec "$MAIN_ORCHESTRATOR" "$TARGET_REPO" "$PRIORITY_FILE" "$PRD_FILE" "$BRANCH_NAME"
