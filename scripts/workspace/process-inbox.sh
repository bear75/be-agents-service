#!/bin/bash
#
# Process Inbox Items
#
# Reads inbox.md and uses Claude to triage items into:
#   - priorities.md (ready to be worked on)
#   - tasks.md (actionable, needs tracking)
#   - follow-ups.md (revisit later)
#   - inbox.md (leave as-is, needs human decision)
#
# Usage:
#   ./scripts/workspace/process-inbox.sh <repo-name>
#   ./scripts/workspace/process-inbox.sh beta-appcaire
#
# Can be run:
#   - Manually when inbox gets cluttered
#   - As part of the nightly workflow (optional)
#   - Via Telegram/OpenClaw ("triage my inbox")
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source workspace resolver
source "$SCRIPT_DIR/resolve-workspace.sh"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[inbox]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[inbox]${NC} $1"; }
log_step() { echo -e "${BLUE}[inbox]${NC} $1"; }

# ─── Parse arguments ──────────────────────────────────────────────────────────

REPO_NAME="${1:-}"

if [[ -z "$REPO_NAME" ]]; then
  echo "Usage: $0 <repo-name>"
  exit 1
fi

# ─── Resolve workspace path ──────────────────────────────────────────────────

WORKSPACE_PATH=$(get_workspace_path "$REPO_NAME")

if [[ -z "$WORKSPACE_PATH" ]]; then
  echo "Error: No workspace configured for '$REPO_NAME'"
  exit 1
fi

INBOX_FILE="$WORKSPACE_PATH/inbox.md"

if [[ ! -f "$INBOX_FILE" ]]; then
  log_warn "No inbox.md found at: $INBOX_FILE"
  exit 0
fi

# ─── Count pending items ─────────────────────────────────────────────────────

PENDING_COUNT=$(grep -c '^\- \[ \]' "$INBOX_FILE" 2>/dev/null || echo "0")

if [[ "$PENDING_COUNT" -eq 0 ]]; then
  log_info "Inbox is empty (no pending items). Nothing to process."
  exit 0
fi

log_info "Found $PENDING_COUNT pending inbox items"
log_step "Sending to Claude for triage..."

# ─── Read workspace context ──────────────────────────────────────────────────

INBOX_CONTENT=$(cat "$INBOX_FILE")
PRIORITIES_CONTENT=""
TASKS_CONTENT=""

if [[ -f "$WORKSPACE_PATH/priorities.md" ]]; then
  PRIORITIES_CONTENT=$(cat "$WORKSPACE_PATH/priorities.md")
fi
if [[ -f "$WORKSPACE_PATH/tasks.md" ]]; then
  TASKS_CONTENT=$(cat "$WORKSPACE_PATH/tasks.md")
fi

# ─── Use Claude to triage ────────────────────────────────────────────────────

TRIAGE_PROMPT="You are triaging inbox items for a software development workspace.

Current inbox:
$INBOX_CONTENT

Current priorities:
$PRIORITIES_CONTENT

Current tasks:
$TASKS_CONTENT

For each PENDING (unchecked) inbox item, decide:
1. PRIORITY - Move to priorities.md (it's a clear feature/fix to implement)
2. TASK - Move to tasks.md (it needs active tracking with status)
3. FOLLOWUP - Move to follow-ups.md (revisit later, not actionable now)
4. KEEP - Leave in inbox (needs human decision, too vague)

Output a JSON array of decisions. Each item should have:
- \"text\": the inbox item text
- \"action\": one of PRIORITY, TASK, FOLLOWUP, KEEP
- \"priority_level\": (if PRIORITY) high, medium, or low
- \"reason\": brief reason for the decision (1 sentence)

Output ONLY the JSON array, no other text."

# Use Ollama (local) for triage when available, else Claude. See docs/LLM_ROUTING.md
LLM_INVOKE="$SERVICE_ROOT/scripts/compound/llm-invoke.sh"
if [[ -f "$LLM_INVOKE" ]]; then
  TRIAGE_RESULT=$(echo "$TRIAGE_PROMPT" | "$LLM_INVOKE" triage "" 2>/dev/null || echo "")
else
  TRIAGE_RESULT=$(claude -p "$TRIAGE_PROMPT" --dangerously-skip-permissions 2>/dev/null || echo "")
fi

if [[ -z "$TRIAGE_RESULT" ]]; then
  log_warn "Claude returned empty response. Skipping triage."
  exit 1
fi

# ─── Parse and apply triage decisions ─────────────────────────────────────────

log_step "Applying triage decisions..."

# Extract JSON from Claude's response (handle potential markdown wrapping)
JSON_RESULT=$(echo "$TRIAGE_RESULT" | sed -n '/\[/,/\]/p')

if [[ -z "$JSON_RESULT" ]]; then
  log_warn "Could not parse triage response. Raw output:"
  echo "$TRIAGE_RESULT"
  exit 1
fi

ITEM_COUNT=$(echo "$JSON_RESULT" | jq 'length' 2>/dev/null || echo "0")

if [[ "$ITEM_COUNT" -eq 0 ]]; then
  log_warn "No items in triage result."
  exit 0
fi

MOVED_TO_PRIORITY=0
MOVED_TO_TASK=0
MOVED_TO_FOLLOWUP=0
KEPT=0

for i in $(seq 0 $((ITEM_COUNT - 1))); do
  ITEM_TEXT=$(echo "$JSON_RESULT" | jq -r ".[$i].text" 2>/dev/null)
  ITEM_ACTION=$(echo "$JSON_RESULT" | jq -r ".[$i].action" 2>/dev/null)
  ITEM_PRIORITY=$(echo "$JSON_RESULT" | jq -r ".[$i].priority_level // \"medium\"" 2>/dev/null)
  ITEM_REASON=$(echo "$JSON_RESULT" | jq -r ".[$i].reason // \"\"" 2>/dev/null)

  case "$ITEM_ACTION" in
    PRIORITY)
      # Append to priorities.md under the right section
      log_info "  → PRIORITY ($ITEM_PRIORITY): $ITEM_TEXT"
      # Simple append: add as numbered item under the appropriate section
      # The human can reorder later
      echo "" >> "$WORKSPACE_PATH/priorities.md"
      MOVED_TO_PRIORITY=$((MOVED_TO_PRIORITY + 1))
      ;;
    TASK)
      log_info "  → TASK: $ITEM_TEXT"
      # Add to tasks.md under Pending
      {
        echo ""
        echo "### $ITEM_TEXT"
        echo "- **Status:** Pending"
        echo "- **Priority:** ${ITEM_PRIORITY^}"
        echo ""
      } >> "$WORKSPACE_PATH/tasks.md"
      MOVED_TO_TASK=$((MOVED_TO_TASK + 1))
      ;;
    FOLLOWUP)
      log_info "  → FOLLOW-UP: $ITEM_TEXT"
      echo "- [ ] $ITEM_TEXT" >> "$WORKSPACE_PATH/follow-ups.md"
      MOVED_TO_FOLLOWUP=$((MOVED_TO_FOLLOWUP + 1))
      ;;
    KEEP)
      log_info "  → KEEP: $ITEM_TEXT (${ITEM_REASON})"
      KEPT=$((KEPT + 1))
      ;;
  esac

  # Mark processed items as done in inbox (except KEEP)
  if [[ "$ITEM_ACTION" != "KEEP" ]]; then
    # Escape special regex chars in the item text
    ESCAPED_TEXT=$(echo "$ITEM_TEXT" | sed 's/[\/&]/\\&/g')
    sed -i "s/^- \[ \] ${ESCAPED_TEXT}/- [x] ${ESCAPED_TEXT} → moved to ${ITEM_ACTION,,}/" "$INBOX_FILE" 2>/dev/null || true
  fi
done

# ─── Summary ────────────────────────────────────────────────────────────────

echo ""
log_info "=========================================="
log_info "Inbox triage complete"
log_info "=========================================="
log_info "  Moved to priorities: $MOVED_TO_PRIORITY"
log_info "  Moved to tasks:      $MOVED_TO_TASK"
log_info "  Moved to follow-ups: $MOVED_TO_FOLLOWUP"
log_info "  Kept in inbox:       $KEPT"
log_info "=========================================="
