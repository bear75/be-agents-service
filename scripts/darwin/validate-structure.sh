#!/bin/bash
#
# Validate DARWIN workspace against docs/DARWIN_STRUCTURE.md.
# Reports violations; exit 0 if valid, 1 if any violation.
#
# Usage: ./scripts/darwin/validate-structure.sh [workspace-path]
#   Default: resolve darwin workspace from config/repos.yaml
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
source "$SERVICE_ROOT/scripts/workspace/resolve-workspace.sh"

WORKSPACE_PATH="${1:-$(get_workspace_path "darwin")}"
WORKSPACE_PATH="${WORKSPACE_PATH/#\~/$HOME}"

VIOLATIONS=0

report() {
  echo "❌ $1"
  (( VIOLATIONS++ )) || true
}

ok() {
  echo "✓ $1"
}

if [[ -z "$WORKSPACE_PATH" || ! -d "$WORKSPACE_PATH" ]]; then
  echo "❌ Workspace path not found or not a directory: $WORKSPACE_PATH"
  exit 2
fi

echo "Validating: $WORKSPACE_PATH"
echo ""

# Support both my/ + machine/ layout and flat layout
if [[ -d "$WORKSPACE_PATH/my" ]]; then
  MY="$WORKSPACE_PATH/my"
  MACHINE="$WORKSPACE_PATH/machine"
  LAYOUT="my/ + machine/"
else
  MY="$WORKSPACE_PATH"
  MACHINE="$WORKSPACE_PATH"
  LAYOUT="flat"
fi
ok "Layout: $LAYOUT"

# Required list files (in my/ or root)
for f in inbox.md priorities.md tasks.md follow-ups.md; do
  [[ -f "$MY/$f" ]] || report "Missing $f (expected in my/ or root)"
done
[[ -f "$MY/inbox.md" ]] && ok "inbox.md"
[[ -f "$MY/priorities.md" ]] && ok "priorities.md"

# Single priorities only (no priorities-*.md)
found_prio=0
for f in "$MY"/priorities-*.md; do
  [[ -f "$f" ]] || continue
  report "Dated priorities (use only priorities.md): $(basename "$f")"
  found_prio=1
done
[[ $found_prio -eq 0 ]] && ok "No dated priorities"

# Required dirs (memory, check-ins, agent-reports, etc.)
[[ -d "$MY/memory" ]] || report "Missing memory dir (my/memory or memory)"
[[ -d "$MACHINE/agent-reports" ]] || report "Missing agent-reports dir (machine/agent-reports or agent-reports)"
for sub in daily weekly monthly; do
  [[ -d "$MACHINE/check-ins/$sub" ]] || report "Missing check-ins/$sub"
done

# memory/ allowed files only
ALLOWED_MEMORY="context.md context.json decisions.md decisions.json learnings.md learnings.json"
for f in "$MY/memory"/*; do
  [[ -e "$f" ]] || continue
  base=$(basename "$f")
  if [[ " $ALLOWED_MEMORY " != *" $base "* ]]; then
    report "memory/ contains disallowed file: $base"
  fi
done
ok "memory/ has only allowed files (or empty)"

# Check-in naming: no " 2" duplicates
for dir in "$MACHINE/check-ins/daily" "$MACHINE/check-ins/weekly"; do
  [[ ! -d "$dir" ]] && continue
  while IFS= read -r -d '' f; do
    if [[ "$(basename "$f")" == *" 2."* ]]; then
      report "Duplicate check-in name (move to archive): $(basename "$f")"
    fi
  done < <(find "$dir" -maxdepth 1 -type f -name "* 2.*" 2>/dev/null | tr '\n' '\0' || true)
done
ok "No duplicate check-in filenames (e.g. ' 2.md')"

echo ""
if [[ $VIOLATIONS -gt 0 ]]; then
  echo "Total violations: $VIOLATIONS"
  exit 1
fi
echo "Structure valid."
exit 0
