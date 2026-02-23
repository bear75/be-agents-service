#!/bin/bash
#
# CMO/CSO - Chief Marketing & Sales Officer
# Marketing strategy, sales alignment, campaign oversight
#
# Usage:
#   ./cmo-cso.sh <session_id> <target_repo> <priority_file>
#
# Delegates to Jarvis (marketing squad lead) for execution.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
JARVIS="$SERVICE_ROOT/agents/marketing/jarvis-orchestrator.sh"

if [[ ! -f "$JARVIS" ]]; then
  echo "[CMO/CSO] Error: Jarvis not found at $JARVIS"
  exit 2
fi

if [[ -z "${2:-}" ]]; then
  echo "[CMO/CSO] Usage: $0 <session_id> <target_repo> <priority_file>"
  echo "[CMO/CSO] Delegates to Jarvis (marketing squad lead)"
  exit 0
fi

TARGET_REPO="$2"
PRIORITY_FILE="${3:-$TARGET_REPO/reports/marketing-priorities-$(date +%Y-%m-%d).md}"
PRD_FILE="$TARGET_REPO/tasks/marketing-prd.json"
BRANCH_NAME="feature/marketing-$(date +%Y%m%d)"

exec "$JARVIS" "$TARGET_REPO" "$PRIORITY_FILE" "$PRD_FILE" "$BRANCH_NAME"
