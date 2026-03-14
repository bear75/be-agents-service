#!/bin/bash
#
# Ensure DARWIN workspace has canonical structure: create missing dirs and template files.
# Does NOT overwrite existing files. Idempotent.
#
# Usage: ./scripts/darwin/ensure-structure.sh [workspace-path]
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TEMPLATES="$SERVICE_ROOT/scripts/workspace/templates"
source "$SERVICE_ROOT/scripts/workspace/resolve-workspace.sh"

WORKSPACE_PATH="${1:-$(get_workspace_path "darwin")}"
WORKSPACE_PATH="${WORKSPACE_PATH/#\~/$HOME}"

if [[ -z "$WORKSPACE_PATH" || ! -d "$WORKSPACE_PATH" ]]; then
  echo "Workspace path not found: $WORKSPACE_PATH"
  exit 1
fi

# my/ = your files; machine/ = agent output
mkdir -p "$WORKSPACE_PATH/my/memory" \
         "$WORKSPACE_PATH/my/input/read" \
         "$WORKSPACE_PATH/my/research" \
         "$WORKSPACE_PATH/machine/check-ins/daily" \
         "$WORKSPACE_PATH/machine/check-ins/weekly" \
         "$WORKSPACE_PATH/machine/check-ins/monthly" \
         "$WORKSPACE_PATH/machine/agent-reports" \
         "$WORKSPACE_PATH/machine/archive/notes" \
         "$WORKSPACE_PATH/machine/archive/check-ins-duplicates" \
         "$WORKSPACE_PATH/machine/archive/orphaned"

copy_if_missing() {
  local src="$1"
  local dst="$2"
  if [[ ! -f "$dst" ]] && [[ -f "$src" ]]; then
    cp "$src" "$dst"
    echo "Created: $dst"
  fi
}

copy_if_missing "$TEMPLATES/inbox.md"      "$WORKSPACE_PATH/my/inbox.md"
copy_if_missing "$TEMPLATES/priorities.md" "$WORKSPACE_PATH/my/priorities.md"
copy_if_missing "$TEMPLATES/tasks.md"      "$WORKSPACE_PATH/my/tasks.md"
copy_if_missing "$TEMPLATES/follow-ups.md" "$WORKSPACE_PATH/my/follow-ups.md"
copy_if_missing "$TEMPLATES/context.md"    "$WORKSPACE_PATH/my/memory/context.md"
copy_if_missing "$TEMPLATES/decisions.md"  "$WORKSPACE_PATH/my/memory/decisions.md"
copy_if_missing "$TEMPLATES/learnings.md"  "$WORKSPACE_PATH/my/memory/learnings.md"

# Optional: copy INSTR and README into workspace if missing
INSTR_SRC="$SERVICE_ROOT/docs/DARWIN_STRUCTURE.md"
if [[ -f "$INSTR_SRC" ]] && [[ ! -f "$WORKSPACE_PATH/INSTR.md" ]]; then
  cp "$INSTR_SRC" "$WORKSPACE_PATH/INSTR.md"
  echo "Created: $WORKSPACE_PATH/INSTR.md"
fi
README_SRC="$SERVICE_ROOT/docs/DARWIN_README_TEMPLATE.md"
if [[ -f "$README_SRC" ]] && [[ ! -f "$WORKSPACE_PATH/README.md" ]]; then
  cp "$README_SRC" "$WORKSPACE_PATH/README.md"
  echo "Created: $WORKSPACE_PATH/README.md"
fi

echo "Ensure-structure done."
