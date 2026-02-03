#!/bin/bash

# scripts/compound/check-status.sh
# Check the status of compound workflow and commit safety

set -e

cd ~/HomeCare/beta-appcaire

echo "========================================"
echo "  Compound Workflow Status Check"
echo "========================================"
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
