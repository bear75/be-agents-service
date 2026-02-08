#!/bin/bash

# scripts/compound/auto-compound.sh
# Full pipeline: report → PRD → tasks → implementation → PR

set -e

# Config-driven approach: Accept repo name as argument
REPO_NAME="${1:-beta-appcaire}"

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load repo configuration from config/repos.yaml
CONFIG_FILE="$SERVICE_ROOT/config/repos.yaml"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "❌ Config file not found: $CONFIG_FILE"
  exit 1
fi

# Parse repo configuration (simple YAML parsing)
REPO_PATH=$(grep -A 20 "^  $REPO_NAME:" "$CONFIG_FILE" | grep "path:" | head -1 | sed 's/.*path: *//' | sed "s|~|$HOME|")

if [ -z "$REPO_PATH" ]; then
  echo "❌ Repository '$REPO_NAME' not found in config"
  exit 1
fi

# Verify repo path exists
if [ ! -d "$REPO_PATH" ]; then
  echo "❌ Repository path does not exist: $REPO_PATH"
  exit 1
fi

echo "🤖 Agent Service: Auto-Compound"
echo "Repository: $REPO_NAME"
echo "Path: $REPO_PATH"
echo ""

cd "$REPO_PATH"

# Source environment if exists
if [ -f .env.local ]; then
  source .env.local
fi

# SAFETY CHECK: Check current branch first
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "❌ SAFETY CHECK FAILED: Not on main branch!"
  echo "Current branch: $CURRENT_BRANCH"
  echo ""
  echo "⚠️  Running this script on a feature branch risks data loss."
  echo "Please switch to main before running compound workflows:"
  echo "  1. Commit your feature work: git add -A && git commit"
  echo "  2. Push to remote: git push"
  echo "  3. Switch to main: git checkout main"
  echo ""
  exit 1
fi

# SAFETY CHECK: Handle uncommitted changes on main
STASH_CREATED=false
STASH_MESSAGE=""
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "📦 Uncommitted changes detected on main branch"
  echo "Automatically stashing your work to preserve it..."
  echo ""

  # Create a descriptive stash message
  STASH_MESSAGE="auto-compound-stash-$(date +%Y-%m-%d-%H-%M-%S)"

  # Stash both staged and unstaged changes, including untracked files
  git stash push -u -m "$STASH_MESSAGE"

  if [ $? -eq 0 ]; then
    echo "✓ Work stashed successfully: $STASH_MESSAGE"
    echo "Your changes are safe and will be restored after the workflow completes."
    echo ""
    STASH_CREATED=true
  else
    echo "❌ Failed to stash changes!"
    echo "Cannot proceed safely. Please manually stash or commit your changes."
    exit 1
  fi
fi

# Now safe to update main
echo "✓ Safety checks passed - updating main branch"
git fetch origin main
git reset --hard origin/main

# ─── Find priorities: workspace first, then reports/ ─────────────────────────
# Source workspace resolver to check for shared markdown workspace
WORKSPACE_SCRIPT="$SCRIPT_DIR/../workspace/resolve-workspace.sh"
WORKSPACE_PATH=""
if [ -f "$WORKSPACE_SCRIPT" ]; then
  source "$WORKSPACE_SCRIPT"
  WORKSPACE_PATH=$(get_workspace_path "$REPO_NAME" 2>/dev/null || echo "")
fi

LATEST_REPORT=""

# Check workspace priorities first
if [ -n "$WORKSPACE_PATH" ] && [ -f "$WORKSPACE_PATH/priorities.md" ]; then
  LATEST_REPORT="$WORKSPACE_PATH/priorities.md"
  echo "Using workspace priorities: $LATEST_REPORT"
fi

# Fall back to reports/ in target repo
if [ -z "$LATEST_REPORT" ]; then
  LATEST_REPORT=$(ls -t reports/*.md 2>/dev/null | head -1)
fi

if [ -z "$LATEST_REPORT" ]; then
  echo "No priorities found (checked workspace and reports/ directory). Exiting."
  exit 0
fi

echo "Using report: $LATEST_REPORT"

# Analyze and pick #1 priority
ANALYSIS=$("$SCRIPT_DIR/analyze-report.sh" "$LATEST_REPORT")
PRIORITY_ITEM=$(echo "$ANALYSIS" | jq -r '.priority_item')
BRANCH_NAME=$(echo "$ANALYSIS" | jq -r '.branch_name')

if [ -z "$PRIORITY_ITEM" ] || [ "$PRIORITY_ITEM" = "null" ]; then
  echo "Could not extract priority item from report. Exiting."
  exit 1
fi

echo "Priority: $PRIORITY_ITEM"
echo "Branch: $BRANCH_NAME"

# Create feature branch
git checkout -b "$BRANCH_NAME"

# Create PRD
echo "Creating PRD..."
claude -p "Load the prd skill if available, or create a detailed Product Requirements Document for: $PRIORITY_ITEM. Save it to tasks/prd-$(basename $BRANCH_NAME).md. Include: problem statement, proposed solution, technical approach, acceptance criteria, and edge cases to consider." --dangerously-skip-permissions

# Check if PRD was created
PRD_FILE="tasks/prd-$(basename $BRANCH_NAME).md"
if [ ! -f "$PRD_FILE" ]; then
  echo "PRD was not created. Exiting."
  exit 1
fi

# Convert PRD to tasks JSON
echo "Converting PRD to tasks..."
claude -p "Read the PRD at $PRD_FILE and convert it into a structured JSON task list. Save to scripts/compound/prd.json with format: {\"tasks\": [{\"id\": 1, \"description\": \"...\", \"status\": \"pending\"}]}. Break down the implementation into 5-10 concrete, testable tasks." --dangerously-skip-permissions

# Run the execution loop
if [ -f "$SCRIPT_DIR/loop.sh" ]; then
  echo "Running execution loop..."
  "$SCRIPT_DIR/loop.sh" 25
else
  echo "Warning: loop.sh not found. Implementing directly..."
  claude -p "Implement all tasks from scripts/compound/prd.json. For each task: read the description, implement it, test it, and commit when complete. Continue until all tasks are done or you encounter a blocker." --dangerously-skip-permissions
fi

# Final safety net: Check for uncommitted changes before pushing
echo "Checking for uncommitted changes..."
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "⚠️  Final safety check: uncommitted changes found!"
  echo "Creating final safety commit..."
  git add -A
  git commit -m "feat: final safety commit - remaining changes

These changes were made during compound workflow execution but were not committed.
This is an automatic safety commit to preserve all work before creating the PR.

Priority: $PRIORITY_ITEM
Branch: $BRANCH_NAME

Co-Authored-By: Compound Agent <noreply@appcaire.com>"
  echo "✓ Safety commit created"
else
  echo "✓ No uncommitted changes - all work was properly committed"
fi

# Create PR
echo "Creating pull request..."
git push -u origin "$BRANCH_NAME"
gh pr create --draft --title "Compound: $PRIORITY_ITEM" --body "Auto-generated PR from nightly compound workflow.

**Priority Item:** $PRIORITY_ITEM

**PRD:** See $PRD_FILE

**Generated:** $(date)" --base main

# ─── Sync to workspace ──────────────────────────────────────────────────────
# Write session summary to shared markdown workspace (if configured)
SYNC_SCRIPT="$SCRIPT_DIR/../workspace/sync-to-workspace.sh"
if [ -f "$SYNC_SCRIPT" ]; then
  echo "📝 Syncing session to workspace..."
  "$SYNC_SCRIPT" "$REPO_NAME" 2>/dev/null || echo "⚠️  Workspace sync failed (non-fatal)"
fi

# RESTORE STASH: If we stashed changes at the beginning, restore them now
# Note: We're still on the feature branch, so switch back to main first
if [ "$STASH_CREATED" = true ]; then
  echo ""
  echo "📦 Switching back to main and restoring your stashed work..."

  # Switch back to main
  git checkout main

  # Find the stash we created (it should be stash@{0} if nothing else was stashed during the workflow)
  STASH_REF=$(git stash list | grep "$STASH_MESSAGE" | head -1 | cut -d: -f1)

  if [ -n "$STASH_REF" ]; then
    git stash pop "$STASH_REF"
    if [ $? -eq 0 ]; then
      echo "✓ Your work has been restored successfully"
      echo "All uncommitted changes are back in your working directory on main"
    else
      echo "⚠️  Could not automatically restore stash (may have conflicts)"
      echo "Your work is still safe in stash: $STASH_MESSAGE"
      echo "Manually restore with: git stash pop"
    fi
  else
    echo "⚠️  Could not find the stash we created"
    echo "Check git stash list and manually restore if needed"
  fi
  echo ""
fi

echo "✓ Auto-compound completed at $(date)"
