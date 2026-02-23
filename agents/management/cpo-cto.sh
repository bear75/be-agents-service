#!/bin/bash
#
# CPO/CTO - Chief Product & Technology Officer
# Product vision, technical direction, architecture decisions
#
# Usage:
#   ./cpo-cto.sh <session_id> <target_repo> <priority_file>
#
# Delegates to Orchestrator (engineering) for implementation.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ORCHESTRATOR="$SERVICE_ROOT/scripts/orchestrator.sh"

if [[ ! -f "$ORCHESTRATOR" ]]; then
  echo "[CPO/CTO] Error: Orchestrator not found at $ORCHESTRATOR"
  exit 2
fi

if [[ -z "${2:-}" ]]; then
  echo "[CPO/CTO] Usage: $0 <session_id> <target_repo> <priority_file>"
  echo "[CPO/CTO] Delegates to Orchestrator (engineering)"
  exit 0
fi

TARGET_REPO="$2"
PRIORITY_FILE="${3:-$TARGET_REPO/reports/priorities-$(date +%Y-%m-%d).md}"
PRD_FILE="$TARGET_REPO/tasks/prd.json"
BRANCH_NAME="feature/cpo-priority-$(date +%Y%m%d)"

exec "$ORCHESTRATOR" "$TARGET_REPO" "$PRIORITY_FILE" "$PRD_FILE" "$BRANCH_NAME"
