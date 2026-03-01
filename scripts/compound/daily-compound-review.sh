#!/bin/bash

# scripts/compound/daily-compound-review.sh
# Runs BEFORE auto-compound.sh to update CLAUDE.md with learnings

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

echo "🤖 Darwin: Daily Compound Review"
echo "Repository: $REPO_NAME"
echo "Path: $REPO_PATH"
echo ""

cd "$REPO_PATH"

# Ensure logs directory exists
mkdir -p logs

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
  STASH_MESSAGE="compound-workflow-auto-stash-$(date +%Y-%m-%d-%H-%M-%S)"

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

echo "Starting daily compound review at $(date)"

# Use Claude Code to review threads and compound learnings
# Note: This assumes you have Claude Code CLI installed and configured
claude -p "Use the compound/extract-learnings skill. Look through and read each Claude Code thread from the last 24 hours.

For any thread where we did NOT extract learnings at the end, do so now:
- Extract the key learnings from that thread
- Update the relevant CLAUDE.md files so we can learn from our work and mistakes
- Use clear symptom/cause/fix format
- Include code examples where relevant
- Update BOTH specific CLAUDE.md files AND root /CLAUDE.md if applicable
- Stage your changes with: git add -A
- Create a clear commit message describing what you learned
- Push your changes to main: git push origin main

Be sure to actually commit and push - don't just say you will!" --dangerously-skip-permissions

# After Claude reviews, update timestamps for any changed CLAUDE.md files
echo ""
echo "📝 Updating CLAUDE.md timestamps for changed files..."
find . -name "CLAUDE.md" -type f | while read -r file; do
  if ! git diff --quiet "$file"; then
    echo "Updating timestamp: $file"
    "$SERVICE_ROOT/scripts/update-claude-md.sh" "$file"
  fi
done

# Safety net: Check if there are uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "⚠️  Uncommitted changes found after review. Creating safety commit..."
  git add -A
  git commit -m "docs: daily compound review - learnings update

Auto-committed by daily review safety net.
Claude updated CLAUDE.md files but did not commit.

Date: $(date +%Y-%m-%d)

Co-Authored-By: Compound Agent <noreply@appcaire.com>"
  git push origin main
  echo "✓ Safety commit created and pushed"
else
  echo "✓ No uncommitted changes - review completed properly"
fi

# ─── Sync to workspace ──────────────────────────────────────────────────────
# Write review summary to shared markdown workspace (if configured)
SYNC_SCRIPT="$SCRIPT_DIR/../workspace/sync-to-workspace.sh"
if [ -f "$SYNC_SCRIPT" ]; then
  echo "📝 Syncing review to workspace..."
  "$SYNC_SCRIPT" "$REPO_NAME" 2>/dev/null || echo "⚠️  Workspace sync failed (non-fatal)"
fi

# ─── Generate tomorrow's daily check-in ──────────────────────────────────────
CHECKIN_SCRIPT="$SCRIPT_DIR/../workspace/generate-checkin.sh"
if [ -f "$CHECKIN_SCRIPT" ]; then
  echo "📝 Generating tomorrow's daily check-in..."
  "$CHECKIN_SCRIPT" "$REPO_NAME" daily 2>/dev/null || echo "⚠️  Check-in generation failed (non-fatal)"
fi

# RESTORE STASH: If we stashed changes at the beginning, restore them now
if [ "$STASH_CREATED" = true ]; then
  echo ""
  echo "📦 Restoring your stashed work..."

  # Find the stash we created (it should be stash@{0} if nothing else was stashed during the workflow)
  STASH_REF=$(git stash list | grep "$STASH_MESSAGE" | head -1 | cut -d: -f1)

  if [ -n "$STASH_REF" ]; then
    git stash pop "$STASH_REF"
    if [ $? -eq 0 ]; then
      echo "✓ Your work has been restored successfully"
      echo "All uncommitted changes are back in your working directory"
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

echo "✓ Daily compound review completed at $(date)"
