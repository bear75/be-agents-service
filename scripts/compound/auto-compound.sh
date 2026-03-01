#!/bin/bash

# scripts/compound/auto-compound.sh
# Full pipeline: report → PRD → tasks → implementation → PR

set -e

# Trap errors to record failed sessions in DB
trap 'on_error $? $LINENO' ERR
on_error() {
  local exit_code=$1
  local line_no=$2
  if type db_api_available &>/dev/null && db_api_available 2>/dev/null; then
    db_update_session "${SESSION_ID:-unknown}" "failed" "" "$exit_code"
    echo "📊 Session failed in DB (line $line_no, exit $exit_code)"
  fi
}

# Config-driven approach: Accept repo name as argument
REPO_NAME="${1:-appcaire}"

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
REPO_BLOCK=$(grep -A 25 "^  $REPO_NAME:" "$CONFIG_FILE" | head -26)
REPO_PATH=$(echo "$REPO_BLOCK" | grep "path:" | head -1 | sed 's/.*path: *//' | sed "s|~|$HOME|")
PRIORITIES_DIR=$(echo "$REPO_BLOCK" | grep "priorities_dir:" | head -1 | sed 's/.*priorities_dir: *//' | tr -d '"' | tr -d "'")

# Optional path overrides (useful in cloud/dev environments)
if [ -n "${REPO_PATH_OVERRIDE:-}" ]; then
  REPO_PATH="${REPO_PATH_OVERRIDE/#\~/$HOME}"
elif [ "$REPO_NAME" = "appcaire" ] && [ -n "${APPCAIRE_PATH:-}" ]; then
  REPO_PATH="${APPCAIRE_PATH/#\~/$HOME}"
fi

if [ -z "$REPO_PATH" ]; then
  echo "❌ Repository '$REPO_NAME' not found in config"
  exit 1
fi

# Cloud fallback: this repo may itself be the appcaire workspace.
if [ ! -d "$REPO_PATH" ] && [ "$REPO_NAME" = "appcaire" ] && [ -d "$SERVICE_ROOT/recurring-visits" ]; then
  echo "⚠️  appcaire path not found in config; using current workspace: $SERVICE_ROOT"
  REPO_PATH="$SERVICE_ROOT"
fi

# Verify repo path exists
if [ ! -d "$REPO_PATH" ]; then
  echo "❌ Repository path does not exist: $REPO_PATH"
  exit 1
fi

# ─── Source DB API helper (writes sessions/tasks to SQLite via API) ──────────
DB_API_SCRIPT="$SCRIPT_DIR/../db-api.sh"
if [ -f "$DB_API_SCRIPT" ]; then
  source "$DB_API_SCRIPT"
fi

# Generate a unique session ID for this run
SESSION_ID="session-$(date +%s)-$$"
SESSION_TEAM="team-engineering"  # Default team; orchestrator can override

echo "🤖 Darwin: Auto-Compound"
echo "Repository: $REPO_NAME"
echo "Path: $REPO_PATH"
echo "Session: $SESSION_ID"
echo ""

cd "$REPO_PATH"

# Source environment (API keys for Claude CLI, GitHub, etc.)
[[ -f "$HOME/.config/caire/env" ]] && source "$HOME/.config/caire/env"
if [ -f .env.local ]; then
  source .env.local
fi

# Ensure we're on main (auto-switch when run from dashboard / automation)
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
STASH_CREATED=false
STASH_MESSAGE=""

if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "📌 Current branch: $CURRENT_BRANCH — switching to main for compound run..."
  if ! git diff --quiet || ! git diff --cached --quiet; then
    STASH_MESSAGE="auto-compound-stash-$(date +%Y-%m-%d-%H-%M-%S)"
    git stash push -u -m "$STASH_MESSAGE"
    STASH_CREATED=true
    echo "   Stashed uncommitted changes (restore later with: git stash list; git stash pop)"
  fi
  git fetch origin 2>/dev/null || true
  git checkout main
  git pull origin main 2>/dev/null || true
  echo "✓ On main, continuing."
  echo ""
fi

# Handle uncommitted changes on main (e.g. after switch or already on main)
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

# Fall back to repo: priorities_dir from config if set, else reports/
if [ -z "$LATEST_REPORT" ]; then
  if [ -n "$PRIORITIES_DIR" ]; then
    REPORT_DIR="$REPO_PATH/$PRIORITIES_DIR"
    LATEST_REPORT=$(ls -t "$REPORT_DIR"/*.md 2>/dev/null | head -1)
    [ -n "$LATEST_REPORT" ] && echo "Using priorities_dir: $PRIORITIES_DIR"
  fi
fi
if [ -z "$LATEST_REPORT" ]; then
  LATEST_REPORT=$(ls -t reports/*.md 2>/dev/null | head -1)
fi

if [ -z "$LATEST_REPORT" ]; then
  echo "No priorities found (checked workspace, priorities_dir, and reports/). Exiting."
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

# ─── Record session in DB ────────────────────────────────────────────────────
if type db_api_available &>/dev/null && db_api_available; then
  db_create_session "$SESSION_ID" "$SESSION_TEAM" "$REPO_NAME" "$LATEST_REPORT" "$BRANCH_NAME"
  echo "📊 Session recorded in DB: $SESSION_ID"
fi

# Create feature branch (use unique name if branch already exists, e.g. after auto-switch from it)
if git show-ref --quiet "refs/heads/$BRANCH_NAME"; then
  UNIQUE_SUFFIX="${SESSION_ID#session-}"
  UNIQUE_SUFFIX="${UNIQUE_SUFFIX%-*}"
  BRANCH_NAME="${BRANCH_NAME}-run-${UNIQUE_SUFFIX}"
  echo "Branch already exists locally; using unique name: $BRANCH_NAME"
fi
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

# Sync prd.json tasks to dashboard DB (so Work page shows them)
PRD_JSON="$REPO_PATH/scripts/compound/prd.json"
if [ -f "$PRD_JSON" ]; then
  node "$SERVICE_ROOT/scripts/compound/sync-prd-to-tasks.js" "$SESSION_ID" "$PRD_JSON" 2>/dev/null || echo "⚠️ Task sync failed (non-fatal)"
fi

# Run implementation via orchestrator (specialist agents) or fallback to loop
# Set USE_ORCHESTRATOR_AGENTS=false to use the legacy loop (single generic agent per task)
USE_ORCHESTRATOR_AGENTS="${USE_ORCHESTRATOR_AGENTS:-true}"
ORCHESTRATOR_SCRIPT="$SERVICE_ROOT/scripts/orchestrator.sh"

if [ "$USE_ORCHESTRATOR_AGENTS" = "true" ] && [ -f "$ORCHESTRATOR_SCRIPT" ]; then
  echo "Running implementation via orchestrator (specialist agents)..."
  PRIORITY_ABS="$LATEST_REPORT"
  [ "${LATEST_REPORT#/}" = "$LATEST_REPORT" ] && PRIORITY_ABS="$REPO_PATH/$LATEST_REPORT"
  PRD_ABS="$REPO_PATH/tasks/prd-$(basename $BRANCH_NAME).md"
  if "$ORCHESTRATOR_SCRIPT" "$REPO_PATH" "$PRIORITY_ABS" "$PRD_ABS" "$BRANCH_NAME"; then
    ORCHESTRATOR_SUCCEEDED=true
  else
    ORCHESTRATOR_SUCCEEDED=false
  fi
else
  ORCHESTRATOR_SUCCEEDED=false
  if [ -f "$SCRIPT_DIR/loop.sh" ]; then
    echo "Running execution loop (generic agent)..."
    "$SCRIPT_DIR/loop.sh" 25
    if [ -f "$PRD_JSON" ]; then
      node "$SERVICE_ROOT/scripts/compound/sync-prd-to-tasks.js" "$SESSION_ID" "$PRD_JSON" 2>/dev/null || echo "⚠️ Task sync (post-loop) failed (non-fatal)"
    fi
  else
    echo "Warning: loop.sh not found. Implementing directly..."
    claude -p "Implement all tasks from scripts/compound/prd.json. For each task: read the description, implement it, test it, and commit when complete. Continue until all tasks are done or you encounter a blocker." --dangerously-skip-permissions
  fi
fi

if [ "$ORCHESTRATOR_SUCCEEDED" = "true" ]; then
  echo "✓ Orchestrator completed (specialists + verification + PR)"
  PR_URL=$(cd "$REPO_PATH" && gh pr view --json url -q '.url' 2>/dev/null || echo "")
fi

# Final safety net and PR (skip if orchestrator already did it)
if [ "$ORCHESTRATOR_SUCCEEDED" = "true" ]; then
  echo "Skipping safety commit and PR (orchestrator already created PR)."
else
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
PR_URL=$(gh pr create --draft --title "Compound: $PRIORITY_ITEM" --body "Auto-generated PR from nightly compound workflow.

**Priority Item:** $PRIORITY_ITEM

**PRD:** See $PRD_FILE

**Generated:** $(date)" --base main)

echo "✓ PR created: $PR_URL"
fi

# ─── Sync to workspace ──────────────────────────────────────────────────────
# Write session summary to shared markdown workspace (if configured)
SYNC_SCRIPT="$SCRIPT_DIR/../workspace/sync-to-workspace.sh"
if [ -f "$SYNC_SCRIPT" ]; then
  echo "📝 Syncing session to workspace..."
  "$SYNC_SCRIPT" "$REPO_NAME" 2>/dev/null || echo "⚠️  Workspace sync failed (non-fatal)"
fi

# ─── Send completion notification ───────────────────────────────────────────
# Notify via Telegram that the session is complete
NOTIFICATION_SCRIPT="$SCRIPT_DIR/../notifications/session-complete.sh"
if [ -f "$NOTIFICATION_SCRIPT" ]; then
  echo "📱 Sending completion notification..."
  "$NOTIFICATION_SCRIPT" "$REPO_NAME" "completed" "$PR_URL" 2>/dev/null || echo "⚠️  Notification failed (non-fatal)"
fi

# ─── Update session status in DB ─────────────────────────────────────────────
PR_URL=$(gh pr view --json url -q '.url' 2>/dev/null || echo "")
if type db_api_available &>/dev/null && db_api_available; then
  db_update_session "$SESSION_ID" "completed" "$PR_URL" "0"
  db_record_metric "session" "$SESSION_ID" "duration_seconds" "$(( $(date +%s) - ${SESSION_ID##*-} ))"
  echo "📊 Session completed in DB: $SESSION_ID"
fi

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
