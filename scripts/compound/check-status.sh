#!/bin/bash
#
# scripts/compound/check-status.sh
# Check the status of compound workflow and commit safety.
#
# Usage:
#   ./scripts/compound/check-status.sh [repo-name] [repo-path-override]
#
# Examples:
#   ./scripts/compound/check-status.sh appcaire
#   ./scripts/compound/check-status.sh appcaire /workspace
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="${REPOS_CONFIG_PATH:-$SERVICE_ROOT/config/repos.yaml}"
CONFIG_FILE="${CONFIG_FILE/#\~/$HOME}"

REPO_NAME="${1:-appcaire}"
REPO_OVERRIDE="${2:-${APPCAIRE_PATH:-}}"

resolve_repo_path() {
  local repo_name="$1"
  local override_path="$2"
  local repo_path=""

  if [[ -n "$override_path" ]]; then
    repo_path="${override_path/#\~/$HOME}"
    echo "$repo_path"
    return 0
  fi

  if [[ -f "$CONFIG_FILE" ]]; then
    local repo_block
    repo_block=$(grep -A 30 "^  $repo_name:" "$CONFIG_FILE" 2>/dev/null || true)
    repo_path=$(echo "$repo_block" | grep "path:" | head -1 | sed 's/.*path: *//' | sed "s|~|$HOME|" || true)
  fi

  # Cloud fallback: this repository may itself be the appcaire workspace.
  if [[ -z "$repo_path" || ! -d "$repo_path" ]]; then
    if [[ "$repo_name" == "appcaire" && -d "$SERVICE_ROOT/recurring-visits" ]]; then
      repo_path="$SERVICE_ROOT"
    fi
  fi

  echo "$repo_path"
}

REPO_PATH="$(resolve_repo_path "$REPO_NAME" "$REPO_OVERRIDE")"

if [[ -z "$REPO_PATH" || ! -d "$REPO_PATH" ]]; then
  echo "❌ Could not resolve repository path for '$REPO_NAME'"
  echo "Checked config: $CONFIG_FILE"
  echo "You can pass an explicit path:"
  echo "  $0 $REPO_NAME /absolute/path/to/repo"
  exit 1
fi

cd "$REPO_PATH"

echo "========================================"
echo "  Compound Workflow Status Check"
echo "========================================"
echo ""
echo "Repository: $REPO_NAME"
echo "Path:       $REPO_PATH"
echo ""

# Check current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "📍 Current Branch: $CURRENT_BRANCH"
echo ""

# Check for uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "⚠️  UNCOMMITTED CHANGES DETECTED"
  echo ""
  echo "Modified files:"
  git status --short
  echo ""
  echo "💡 Tip: Run 'git add -A && git commit -m \"your message\"' to commit"
else
  echo "✓ No uncommitted changes"
fi
echo ""

# Check recent commits
echo "📝 Recent Commits (last 5):"
git log -5 --oneline --decorate
echo ""

# Check if there are unpushed commits
UNPUSHED=$(git log @{u}.. --oneline 2>/dev/null || echo "")
if [ -n "$UNPUSHED" ]; then
  echo "⚠️  UNPUSHED COMMITS DETECTED"
  echo ""
  echo "$UNPUSHED"
  echo ""
  echo "💡 Tip: Run 'git push' to push these commits"
else
  echo "✓ All commits are pushed"
fi
echo ""

# Check commit log
if [ -f logs/compound-commits.log ]; then
  echo "📊 Recent Compound Workflow Activity:"
  tail -20 logs/compound-commits.log
  echo ""
else
  echo "ℹ️  No compound commit log found yet"
  echo ""
fi

# Check task status if exists
if [ -f scripts/compound/prd.json ]; then
  echo "📋 Current Task Status:"
  PENDING=$(jq '[.tasks[] | select(.status == "pending")] | length' scripts/compound/prd.json)
  COMPLETED=$(jq '[.tasks[] | select(.status == "completed")] | length' scripts/compound/prd.json)
  BLOCKED=$(jq '[.tasks[] | select(.status == "blocked")] | length' scripts/compound/prd.json)
  TOTAL=$(jq '.tasks | length' scripts/compound/prd.json)

  echo "  Total: $TOTAL tasks"
  echo "  ✓ Completed: $COMPLETED"
  echo "  ⏳ Pending: $PENDING"
  echo "  ⚠️  Blocked: $BLOCKED"

  if [ "$BLOCKED" -gt 0 ]; then
    echo ""
    echo "Blocked tasks:"
    jq -r '.tasks[] | select(.status == "blocked") | "  - Task #\(.id): \(.description)\n    Reason: \(.comment // "No reason provided")"' scripts/compound/prd.json
  fi
else
  echo "ℹ️  No active PRD/tasks found"
fi

echo ""
echo "========================================"
echo "💡 Tips:"
echo "  - Check logs/compound-commits.log for detailed commit history"
echo "  - Run 'git status' to see detailed file changes"
echo "  - Run 'git log' to see full commit history"
echo "========================================"
