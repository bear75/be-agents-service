#!/bin/bash
#
# House-clean DARWIN workspace: run full Darwin pipeline and optionally migrate
# flat layout into my/ + machine/.
#
# Usage:
#   ./scripts/darwin/house-clean.sh [workspace-path]           # validate, archive, ensure, memory-to-json
#   ./scripts/darwin/house-clean.sh [workspace-path] --migrate  # same + move root files into my/ and machine/
#
# When to use:
#   - Regularly: run without --migrate to keep structure valid and memory JSON in sync.
#   - Once: run with --migrate to move an existing flat DARWIN into my/ and machine/.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
source "$SERVICE_ROOT/scripts/workspace/resolve-workspace.sh"

WORKSPACE_PATH="${1:-$(get_workspace_path "darwin")}"
WORKSPACE_PATH="${WORKSPACE_PATH/#\~/$HOME}"
MIGRATE=""
[[ "${2:-}" == "--migrate" ]] && MIGRATE=1

if [[ -z "$WORKSPACE_PATH" || ! -d "$WORKSPACE_PATH" ]]; then
  echo "Workspace path not found or not a directory: $WORKSPACE_PATH"
  exit 1
fi

echo "House-clean: $WORKSPACE_PATH"
[[ -n "$MIGRATE" ]] && echo "Mode: migrate (move root → my/ and machine/)"
echo ""

# When --migrate: do migration first so ensure-structure then fills only missing files
if [[ -n "$MIGRATE" ]]; then
  MY="$WORKSPACE_PATH/my"
  MACHINE="$WORKSPACE_PATH/machine"
  mkdir -p "$MY/memory" "$MY/input/read" "$MY/research" \
           "$MACHINE/check-ins/daily" "$MACHINE/check-ins/weekly" "$MACHINE/check-ins/monthly" \
           "$MACHINE/agent-reports" "$MACHINE/archive/notes" "$MACHINE/archive/check-ins-duplicates" "$MACHINE/archive/orphaned"

  # Move your files from root → my/ (only if not already in my/)
  for f in inbox.md priorities.md tasks.md follow-ups.md; do
    if [[ -f "$WORKSPACE_PATH/$f" ]] && [[ ! -f "$MY/$f" ]]; then
      mv "$WORKSPACE_PATH/$f" "$MY/$f"
      echo "Migrated: $f → my/$f"
    fi
  done

  # Move memory/* → my/memory/
  if [[ -d "$WORKSPACE_PATH/memory" ]]; then
    for f in "$WORKSPACE_PATH/memory"/*; do
      [[ -e "$f" ]] || continue
      base=$(basename "$f")
      if [[ ! -f "$MY/memory/$base" ]]; then
        mv "$f" "$MY/memory/$base"
        echo "Migrated: memory/$base → my/memory/$base"
      fi
    done
    rmdir "$WORKSPACE_PATH/memory" 2>/dev/null || true
  fi

  # Move input/ → my/input/
  if [[ -d "$WORKSPACE_PATH/input" ]]; then
    for f in "$WORKSPACE_PATH/input"/*; do
      [[ -e "$f" ]] || continue
      base=$(basename "$f")
      [[ "$base" == "read" ]] && continue
      if [[ ! -e "$MY/input/$base" ]]; then
        mv "$f" "$MY/input/$base"
        echo "Migrated: input/$base → my/input/$base"
      fi
    done
    [[ -d "$WORKSPACE_PATH/input/read" ]] && mv "$WORKSPACE_PATH/input/read"/* "$MY/input/read/" 2>/dev/null || true
    rm -rf "$WORKSPACE_PATH/input" 2>/dev/null || true
  fi

  # Move research/ → my/research/
  if [[ -d "$WORKSPACE_PATH/research" ]]; then
    for f in "$WORKSPACE_PATH/research"/*; do
      [[ -e "$f" ]] || continue
      base=$(basename "$f")
      if [[ ! -e "$MY/research/$base" ]]; then
        mv "$f" "$MY/research/$base"
        echo "Migrated: research/$base → my/research/$base"
      fi
    done
    rmdir "$WORKSPACE_PATH/research" 2>/dev/null || true
  fi

  # Move agent-reports, check-ins, archive → machine/
  if [[ -d "$WORKSPACE_PATH/agent-reports" ]]; then
    for f in "$WORKSPACE_PATH/agent-reports"/*; do
      [[ -e "$f" ]] || continue
      mv "$f" "$MACHINE/agent-reports/"
      echo "Migrated: agent-reports/$(basename "$f") → machine/agent-reports/"
    done
    rmdir "$WORKSPACE_PATH/agent-reports" 2>/dev/null || true
  fi
  if [[ -d "$WORKSPACE_PATH/check-ins" ]]; then
    for sub in daily weekly monthly; do
      [[ ! -d "$WORKSPACE_PATH/check-ins/$sub" ]] && continue
      for f in "$WORKSPACE_PATH/check-ins/$sub"/*; do
        [[ -e "$f" ]] || continue
        mv "$f" "$MACHINE/check-ins/$sub/"
        echo "Migrated: check-ins/$sub/$(basename "$f") → machine/check-ins/$sub/"
      done
    done
    rm -rf "$WORKSPACE_PATH/check-ins" 2>/dev/null || true
  fi
  if [[ -d "$WORKSPACE_PATH/archive" ]]; then
    for f in "$WORKSPACE_PATH/archive"/*; do
      [[ -e "$f" ]] || continue
      base=$(basename "$f")
      if [[ -d "$f" ]]; then
        cp -R "$f" "$MACHINE/archive/" 2>/dev/null || true
        rm -rf "$f"
      else
        mv "$f" "$MACHINE/archive/"
      fi
      echo "Migrated: archive/$base → machine/archive/"
    done
    rmdir "$WORKSPACE_PATH/archive" 2>/dev/null || true
  fi

  # Orphan root .md files that are not allowed at root (move to machine/archive/orphaned/)
  ALLOWED_ROOT="README.md INSTR.md MEMORY.md AGENTS.md USER.md SOUL.md IDENTITY.md BOOTSTRAP.md HEARTBEAT.md TOOLS.md"
  for f in "$WORKSPACE_PATH"/*.md; do
    [[ -f "$f" ]] || continue
    base=$(basename "$f")
    if [[ " $ALLOWED_ROOT " != *" $base "* ]]; then
      mv "$f" "$MACHINE/archive/orphaned/"
      echo "Orphaned: $base → machine/archive/orphaned/"
    fi
  done
  echo ""
fi

# Run Darwin manager pipeline (after migrate so structure exists)
"$SCRIPT_DIR/validate-structure.sh" "$WORKSPACE_PATH" 2>/dev/null || true
"$SCRIPT_DIR/archive-completed.sh" "$WORKSPACE_PATH"
"$SCRIPT_DIR/ensure-structure.sh" "$WORKSPACE_PATH"
node "$SCRIPT_DIR/memory-to-structured.js" "$WORKSPACE_PATH" 2>/dev/null || true

echo ""
echo "House-clean done."
