#!/bin/bash
#
# Archive completed inbox items and duplicate check-ins to keep DARWIN structured.
# - Moves [x] items from inbox.md to archive/inbox-archive-YYYY-MM.md
# - Moves check-ins with " 2" in name to archive/check-ins-duplicates/
#
# Usage: ./scripts/darwin/archive-completed.sh [workspace-path]
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
source "$SERVICE_ROOT/scripts/workspace/resolve-workspace.sh"

WORKSPACE_PATH="${1:-$(get_workspace_path "darwin")}"
WORKSPACE_PATH="${WORKSPACE_PATH/#\~/$HOME}"

if [[ -z "$WORKSPACE_PATH" || ! -d "$WORKSPACE_PATH" ]]; then
  echo "Workspace path not found: $WORKSPACE_PATH"
  exit 1
fi

# Support both my/ + machine/ layout and flat layout
if [[ -d "$WORKSPACE_PATH/my" ]]; then
  MY="$WORKSPACE_PATH/my"
  MACHINE="$WORKSPACE_PATH/machine"
else
  MY="$WORKSPACE_PATH"
  MACHINE="$WORKSPACE_PATH"
fi
ARCHIVE="$MACHINE/archive"
mkdir -p "$ARCHIVE/check-ins-duplicates"

# 1) Duplicate check-ins -> archive/check-ins-duplicates
for dir in "$MACHINE/check-ins/daily" "$MACHINE/check-ins/weekly"; do
  [[ ! -d "$dir" ]] && continue
  for f in "$dir"/*" 2."*; do
    [[ -f "$f" ]] || continue
    mv "$f" "$ARCHIVE/check-ins-duplicates/"
    echo "Archived duplicate: $(basename "$f")"
  done
done

# 2) Completed inbox items: append to archive/inbox-archive-YYYY-MM.md, remove from my/inbox.md
INBOX="$MY/inbox.md"
[[ ! -f "$INBOX" ]] && exit 0

MONTH=$(date +%Y-%m)
ARCHIVE_INBOX="$ARCHIVE/inbox-archive-$MONTH.md"

# Extract lines that are - [x]; append to archive file
DONE_ITEMS=$(grep -E '^\s*-\s*\[x\]' "$INBOX" 2>/dev/null || true)
if [[ -n "$DONE_ITEMS" ]]; then
  echo "" >> "$ARCHIVE_INBOX"
  echo "## $(date +%Y-%m-%d)" >> "$ARCHIVE_INBOX"
  echo "$DONE_ITEMS" >> "$ARCHIVE_INBOX"
  # Remove completed lines from inbox (macOS-safe: use temp file)
  grep -v -E '^\s*-\s*\[x\]' "$INBOX" > "${INBOX}.tmp" && mv "${INBOX}.tmp" "$INBOX"
  echo "Archived completed inbox items to $ARCHIVE_INBOX"
fi

echo "Archive-completed done."
