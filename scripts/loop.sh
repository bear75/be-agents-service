#!/bin/bash

# scripts/compound/loop.sh
# Iterative execution loop - runs agent on tasks until completion or max iterations
# Enhanced with commit safety nets to prevent data loss

set -e

MAX_ITERATIONS=${1:-25}
TASKS_FILE="scripts/compound/prd.json"
COMMIT_LOG="logs/compound-commits.log"

if [ ! -f "$TASKS_FILE" ]; then
  echo "Error: Tasks file not found at $TASKS_FILE"
  exit 1
fi

# Ensure logs directory exists
mkdir -p logs

echo "Starting execution loop (max $MAX_ITERATIONS iterations)..."
echo "=== Execution started at $(date) ===" >> "$COMMIT_LOG"

for i in $(seq 1 $MAX_ITERATIONS); do
  echo ""
  echo "=== Iteration $i/$MAX_ITERATIONS ==="

  # Check task status
  PENDING=$(jq '[.tasks[] | select(.status == "pending")] | length' "$TASKS_FILE")
  COMPLETED=$(jq '[.tasks[] | select(.status == "completed")] | length' "$TASKS_FILE")
  TOTAL=$(jq '.tasks | length' "$TASKS_FILE")

  echo "Tasks: $COMPLETED/$TOTAL completed, $PENDING pending"

  # Exit if all tasks complete
  if [ "$PENDING" -eq 0 ]; then
    echo "✓ All tasks completed!"
    echo "=== All tasks completed at $(date) ===" >> "$COMMIT_LOG"
    exit 0
  fi

  # Get next pending task
  NEXT_TASK=$(jq -r '[.tasks[] | select(.status == "pending")] | first | .description' "$TASKS_FILE")
  NEXT_TASK_ID=$(jq -r '[.tasks[] | select(.status == "pending")] | first | .id' "$TASKS_FILE")

  echo "Next task (ID $NEXT_TASK_ID): $NEXT_TASK"

  # Create a recovery snapshot before executing (in case Claude forgets to commit)
  git stash push -u -m "pre-task-$NEXT_TASK_ID-snapshot-$(date +%s)" 2>/dev/null || true

  # Build context hint for agent (when REPORT_PATH/PRD_FILE set, e.g. mobile sprints)
  CONTEXT_HINT=""
  if [ -n "${REPORT_PATH:-}" ] && [ -f "${REPORT_PATH:-}" ]; then
    CONTEXT_HINT="For context, read $REPORT_PATH (required reading, architecture) and ${PRD_FILE:-$TASKS_FILE}. "
  fi

  # Execute task with Claude - emphasize commit requirement
  claude -p "${CONTEXT_HINT}Execute task #$NEXT_TASK_ID from $TASKS_FILE: '$NEXT_TASK'

IMPORTANT: When you complete this task, you MUST:
1. Update $TASKS_FILE to mark this task as 'completed'
2. Stage ALL your changes: git add -A
3. Create a commit with a clear, descriptive message
4. Verify the commit succeeded by checking git log -1

If you encounter errors or are blocked:
- Mark the task as 'blocked' in $TASKS_FILE
- Add a 'comment' field explaining what blocked you
- Commit the task file update so we know about the blocker" --dangerously-skip-permissions

  # Verify if Claude made a commit (check last 2 minutes)
  RECENT_COMMIT=$(git log -1 --since="2 minutes ago" --format="%H %s" 2>/dev/null || echo "")

  if [ -n "$RECENT_COMMIT" ]; then
    echo "✓ Commit detected: $RECENT_COMMIT" | tee -a "$COMMIT_LOG"
    # Clear the recovery stash since we have a good commit
    git stash drop "stash@{0}" 2>/dev/null || true
  else
    # No commit found - check if there are uncommitted changes
    if ! git diff --quiet || ! git diff --cached --quiet; then
      echo "⚠️  No commit found but changes detected. Creating safety commit..." | tee -a "$COMMIT_LOG"
      git add -A
      git commit -m "feat(task-$NEXT_TASK_ID): $NEXT_TASK

Auto-committed by compound workflow safety net.
Claude executed the task but did not create a commit.

Task ID: $NEXT_TASK_ID
Iteration: $i/$MAX_ITERATIONS

Co-Authored-By: Compound Agent <noreply@appcaire.com>" | tee -a "$COMMIT_LOG"

      # Clear the recovery stash
      git stash drop "stash@{0}" 2>/dev/null || true
    else
      echo "ℹ️  No changes detected for task #$NEXT_TASK_ID" | tee -a "$COMMIT_LOG"
      # Restore the stash (nothing was changed)
      git stash pop 2>/dev/null || true
    fi
  fi

  # Check if task was marked complete
  TASK_STATUS=$(jq -r ".tasks[] | select(.id == $NEXT_TASK_ID) | .status" "$TASKS_FILE" 2>/dev/null || echo "unknown")

  if [ "$TASK_STATUS" = "blocked" ]; then
    echo "⚠️  Task $NEXT_TASK_ID is blocked. Stopping execution." | tee -a "$COMMIT_LOG"
    BLOCK_REASON=$(jq -r ".tasks[] | select(.id == $NEXT_TASK_ID) | .comment // \"No reason provided\"" "$TASKS_FILE")
    echo "Reason: $BLOCK_REASON" | tee -a "$COMMIT_LOG"
    exit 1
  fi

  if [ "$TASK_STATUS" != "completed" ]; then
    echo "⚠️  Task $NEXT_TASK_ID was not marked as completed (status: $TASK_STATUS). Continuing anyway..." | tee -a "$COMMIT_LOG"
  fi

  # Brief pause between iterations
  sleep 2
done

echo "⚠️  Reached maximum iterations ($MAX_ITERATIONS). Some tasks may remain incomplete." | tee -a "$COMMIT_LOG"
echo "=== Loop ended at $(date) ===" >> "$COMMIT_LOG"
exit 0
