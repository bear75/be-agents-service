#!/bin/bash
#
# CEO - Chief Executive Officer
# Strategic oversight, prioritization, final decisions
#
# Usage:
#   ./ceo.sh <session_id> <target_repo> <priority_file>
#
# Note: Management agents are strategic/delegation roles.
# This script documents the agent; full automation may delegate to Orchestrator or Jarvis.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [[ -z "${2:-}" ]]; then
  echo "[CEO] Strategic agent - oversight and prioritization"
  echo "[CEO] Usage: $0 <session_id> <target_repo> <priority_file>"
  echo "[CEO] Delegates to Orchestrator for implementation"
  exit 0
fi

TARGET_REPO="$2"
PRIORITY_FILE="${3:-$TARGET_REPO/reports/priorities-$(date +%Y-%m-%d).md}"
PRD_FILE="$TARGET_REPO/tasks/prd.json"
BRANCH_NAME="feature/ceo-priority-$(date +%Y%m%d)"

exec "$SERVICE_ROOT/scripts/orchestrator.sh" "$TARGET_REPO" "$PRIORITY_FILE" "$PRD_FILE" "$BRANCH_NAME"
