#!/usr/bin/env bash
#
# One-time migration: copy OpenClaw default workspace into the shared folder
# so all agent work lives in the be-agents-service repo.
#
# Usage:
#   ./scripts/openclaw-migrate-workspace.sh [TARGET_DIR]
#
# Default TARGET_DIR: $HOME/.openclaw/workspace/be-agents-service (Mac mini shared folder)
# Example (repo elsewhere): ./scripts/openclaw-migrate-workspace.sh ~/HomeCare/be-agents-service
#

set -e

DEFAULT_SOURCE="$HOME/.openclaw/workspace"
TARGET="${1:-$HOME/.openclaw/workspace/be-agents-service}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== OpenClaw workspace migration ==="
echo ""

if [[ ! -d "$DEFAULT_SOURCE" ]]; then
  echo "Nothing to migrate: default workspace not found at $DEFAULT_SOURCE"
  exit 0
fi

echo "Source: $DEFAULT_SOURCE"
echo "Target: $TARGET"
echo ""

mkdir -p "$TARGET"

# Copy contents; do not overwrite existing (preserve shared repo content)
if command -v rsync >/dev/null 2>&1; then
  rsync -av --ignore-existing "$DEFAULT_SOURCE/" "$TARGET/"
  echo ""
  echo "Migration done (rsync)."
else
  COPIED=0
  while IFS= read -r -d '' entry; do
    name="${entry#$DEFAULT_SOURCE/}"
    dest="$TARGET/$name"
    if [[ -e "$dest" ]]; then
      echo "  skip (exists): $name"
    else
      if [[ -d "$entry" ]]; then
        mkdir -p "$dest"
        cp -R "$entry"/* "$dest/" 2>/dev/null || true
      else
        mkdir -p "$(dirname "$dest")"
        cp "$entry" "$dest"
      fi
      echo "  copied: $name"
      ((COPIED++)) || true
    fi
  done < <(find "$DEFAULT_SOURCE" -mindepth 1 -maxdepth 1 -print0 2>/dev/null)
  echo ""
  if [[ $COPIED -gt 0 ]]; then
    echo "Migrated $COPIED top-level item(s) to $TARGET"
  else
    echo "No new items copied (target already had content or source empty)."
  fi
fi
echo ""
echo "Next steps:"
echo "  1. Set agent.workspace in ~/.openclaw/openclaw.json to: $TARGET"
echo "  2. Restart OpenClaw: openclaw gateway restart"
echo ""
