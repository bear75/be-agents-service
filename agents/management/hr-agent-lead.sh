#!/bin/bash
#
# HR Agent Lead - Human Resources & Agent Development
# Agent competency development, onboarding, XP/gamification
#
# Usage:
#   ./hr-agent-lead.sh <session_id> <target_repo> [action]
#
# Actions: review-learnings | update-prompts | gamification-status
# Default: review-learnings (runs daily-compound-review for CLAUDE.md updates)
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
REVIEW_SCRIPT="$SERVICE_ROOT/scripts/compound/daily-compound-review.sh"

ACTION="${3:-review-learnings}"
TARGET_REPO="${2:-}"

case "$ACTION" in
  review-learnings)
    if [[ -n "$TARGET_REPO" && -f "$REVIEW_SCRIPT" ]]; then
      REPO_NAME=$(basename "$TARGET_REPO")
      echo "[HR] Running daily compound review for $REPO_NAME (extract learnings → CLAUDE.md)"
      exec "$REVIEW_SCRIPT" "$REPO_NAME"
    else
      echo "[HR] HR Agent Lead - agent development and learnings"
      echo "[HR] Run: ./scripts/compound/daily-compound-review.sh <repo> for learnings extraction"
      exit 0
    fi
    ;;
  *)
    echo "[HR] HR Agent Lead - agent development"
    echo "[HR] Supported: review-learnings (default), update-prompts, gamification-status"
    exit 0
    ;;
esac
