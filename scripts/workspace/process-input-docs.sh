#!/bin/bash
#
# Process Input Docs
#
# Reads .md files from input/ and uses Claude to convert content into:
#   - inbox.md (ideas, quick captures)
#   - priorities.md (what to build next)
#   - tasks.md (trackable work)
#
# After processing, moves docs to input/read/ (marked handled).
#
# Usage:
#   ./scripts/workspace/process-input-docs.sh <repo-name>
#   ./scripts/workspace/process-input-docs.sh beta-appcaire
#
# Sandbox mode (no repos.yaml entry needed):
#   WORKSPACE_PATH=/path/to/workspace ./scripts/workspace/process-input-docs.sh sandbox
#
# Can be run:
#   - Manually when you drop new docs
#   - Via OpenClaw ("process my input docs")
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

log_info() { echo -e "${GREEN}[input]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[input]${NC} $1"; }
log_step() { echo -e "${BLUE}[input]${NC} $1"; }

# ─── Parse arguments ──────────────────────────────────────────────────────────

REPO_NAME="${1:-}"

if [[ -z "$REPO_NAME" ]]; then
  echo "Usage: $0 <repo-name>"
  exit 1
fi

# ─── Resolve workspace path ──────────────────────────────────────────────────

# Allow WORKSPACE_PATH env override for sandbox mode (no repos.yaml entry needed)
if [[ -z "${WORKSPACE_PATH:-}" ]]; then
  WORKSPACE_PATH=$(get_workspace_path "$REPO_NAME")
fi

# Expand ~ in WORKSPACE_PATH if present
WORKSPACE_PATH="${WORKSPACE_PATH/#\~/$HOME}"

if [[ -z "$WORKSPACE_PATH" ]]; then
  log_warn "No workspace configured for '$REPO_NAME'. Set WORKSPACE_PATH for sandbox mode."
  exit 1
fi

INPUT_DIR="$WORKSPACE_PATH/input"
READ_DIR="$WORKSPACE_PATH/input/read"

if [[ ! -d "$INPUT_DIR" ]]; then
  log_warn "No input folder at: $INPUT_DIR"
  log_info "Run init-workspace.sh first."
  exit 0
fi

mkdir -p "$READ_DIR"

# ─── Find .md files to process (exclude README, input/read/) ───────────────────

FILES=()
while IFS= read -r -d '' f; do
  [[ "$(basename "$f")" == "README.md" ]] && continue
  FILES+=("$f")
done < <(find "$INPUT_DIR" -maxdepth 1 -name "*.md" -print0 2>/dev/null || true)

if [[ ${#FILES[@]} -eq 0 ]]; then
  log_info "No .md files to process in input/"
  exit 0
fi

log_info "Found ${#FILES[@]} doc(s) to process"

# ─── Read current workspace state ─────────────────────────────────────────────

INBOX_FILE="$WORKSPACE_PATH/inbox.md"
PRIORITIES_FILE="$WORKSPACE_PATH/priorities.md"
TASKS_FILE="$WORKSPACE_PATH/tasks.md"

INBOX_CONTENT=""
PRIORITIES_CONTENT=""
TASKS_CONTENT=""

[[ -f "$INBOX_FILE" ]] && INBOX_CONTENT=$(cat "$INBOX_FILE")
[[ -f "$PRIORITIES_FILE" ]] && PRIORITIES_CONTENT=$(cat "$PRIORITIES_FILE")
[[ -f "$TASKS_FILE" ]] && TASKS_CONTENT=$(cat "$TASKS_FILE")

# ─── Process each file ────────────────────────────────────────────────────────

TODAY=$(date +%Y-%m-%d)

for FILE_PATH in "${FILES[@]}"; do
  FILENAME=$(basename "$FILE_PATH")
  DOC_CONTENT=$(cat "$FILE_PATH")

  log_step "Processing: $FILENAME"

  CONVERT_PROMPT="You are converting a markdown document into a software workspace structure.

**Source doc:** $FILENAME

**Doc content:**
---
$DOC_CONTENT
---

**Current workspace state:**
- Inbox: $INBOX_FILE
- Priorities: $PRIORITIES_FILE
- Tasks: $TASKS_FILE

**Task:** Extract actionable items from the doc and categorize them as:
1. INBOX - Ideas, notes, or items needing human triage
2. PRIORITY - Clear features/fixes to implement (high/medium/low)
3. TASK - Trackable work with status (add to Pending section)

Output a JSON object:
{
  \"inbox\": [\"item 1\", \"item 2\"],
  \"priorities\": [{\"text\": \"...\", \"level\": \"high|medium|low\"}],
  \"tasks\": [{\"title\": \"...\", \"priority\": \"High|Medium|Low\"}]
}

Only include items that are actionable or useful. Skip generic fluff. Be concise.
Output ONLY the JSON, no other text."

  RESULT=$(claude -p "$CONVERT_PROMPT" --dangerously-skip-permissions 2>/dev/null || echo "")

  if [[ -z "$RESULT" ]]; then
    log_warn "  Claude returned empty. Skipping file."
    continue
  fi

  # Extract JSON (handle markdown code block)
  JSON=$(echo "$RESULT" | sed -n '/{/,/}/p' | head -1)
  if [[ -z "$JSON" ]]; then
    JSON=$(echo "$RESULT" | grep -E '^\s*\{' | head -1)
  fi

  if [[ -z "$JSON" ]]; then
    log_warn "  Could not parse JSON. Skipping file."
    continue
  fi

  # Append to inbox
  INBOX_ITEMS=$(echo "$JSON" | jq -r '.inbox[]? // empty' 2>/dev/null || true)
  if [[ -n "$INBOX_ITEMS" ]]; then
    if ! grep -q "## $TODAY" "$INBOX_FILE" 2>/dev/null; then
      echo "" >> "$INBOX_FILE"
      echo "## $TODAY" >> "$INBOX_FILE"
    fi
    while IFS= read -r item; do
      [[ -z "$item" ]] && continue
      echo "- [ ] $item (from: $FILENAME)" >> "$INBOX_FILE"
      log_info "  → inbox: $item"
    done <<< "$INBOX_ITEMS"
  fi

  # Append to priorities (at end; user can reorder)
  echo "$JSON" | jq -r '.priorities[]? | "\(.level)|\(.text)"' 2>/dev/null | while IFS='|' read -r level text; do
    [[ -z "$text" ]] && continue
    echo "" >> "$PRIORITIES_FILE"
    echo "1. **$text** (from $FILENAME)" >> "$PRIORITIES_FILE"
    log_info "  → priority ($level): $text"
  done

  # Append to tasks
  echo "$JSON" | jq -r '.tasks[]? | "\(.priority)|\(.title)"' 2>/dev/null | while IFS='|' read -r priority title; do
    [[ -z "$title" ]] && continue
    {
      echo ""
      echo "### $title"
      echo "- **Status:** Pending"
      echo "- **Priority:** ${priority:-Medium}"
      echo "- **Source:** $FILENAME"
      echo ""
    } >> "$TASKS_FILE"
    log_info "  → task: $title"
  done

  # Copy to input/read/, then delete original (avoid confusion from duplicates)
  READ_PATH="$READ_DIR/$FILENAME"
  if [[ -f "$READ_PATH" ]]; then
    READ_PATH="$READ_DIR/$(date +%H%M%S)-$FILENAME"
  fi
  cp "$FILE_PATH" "$READ_PATH" && rm -f "$FILE_PATH"
  log_info "  ✓ Moved to input/read/ (original removed)"
done

log_info "Done. Processed ${#FILES[@]} doc(s)."
