#!/bin/bash

# scripts/sync-state-to-db.sh
# Syncs existing .compound-state/ JSON session files into the SQLite DB via API.
# Run this once to backfill historical sessions, or periodically to keep in sync.
#
# Usage: ./scripts/sync-state-to-db.sh [repo-name]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/db-api.sh"

# Check API is available
if ! db_api_available; then
  echo "API server not available at $API_BASE"
  echo "Start the server first: cd apps/server && npx tsx src/index.ts"
  exit 1
fi

echo "Syncing .compound-state/ to DB..."

REPO_NAME="${1:-}"
CONFIG_FILE="$SERVICE_ROOT/config/repos.yaml"

# If repo name is provided, sync that repo's state
# Otherwise, sync all repos from config
if [ -n "$REPO_NAME" ]; then
  REPO_PATH=$(grep -A 20 "^  $REPO_NAME:" "$CONFIG_FILE" | grep "path:" | head -1 | sed 's/.*path: *//' | sed "s|~|$HOME|")
  REPOS=("$REPO_NAME:$REPO_PATH")
else
  # Parse all repos from config
  REPOS=()
  while IFS= read -r line; do
    name=$(echo "$line" | cut -d: -f1 | xargs)
    path=$(grep -A 20 "^  $name:" "$CONFIG_FILE" | grep "path:" | head -1 | sed 's/.*path: *//' | sed "s|~|$HOME|")
    [ -n "$name" ] && [ -n "$path" ] && REPOS+=("$name:$path")
  done < <(grep -E '^\s{2}[a-z]' "$CONFIG_FILE" | sed 's/:.*//')
fi

SYNCED=0
SKIPPED=0

for entry in "${REPOS[@]}"; do
  repo_name="${entry%%:*}"
  repo_path="${entry#*:}"

  STATE_DIR="$repo_path/.compound-state"
  if [ ! -d "$STATE_DIR" ]; then
    echo "  No .compound-state/ in $repo_name, skipping"
    ((SKIPPED++)) || true
    continue
  fi

  echo "  Scanning $repo_name at $STATE_DIR..."

  # Find session directories
  for session_dir in "$STATE_DIR"/session-*/ "$STATE_DIR"/orchestrator-*/; do
    [ -d "$session_dir" ] || continue

    session_id=$(basename "$session_dir")

    # Check for orchestrator.json or session state files
    for json_file in "$session_dir"/*.json; do
      [ -f "$json_file" ] || continue

      # Read basic info from JSON
      status=$(python3 -c "import json; d=json.load(open('$json_file')); print(d.get('status','completed'))" 2>/dev/null || echo "completed")
      target_repo=$(python3 -c "import json; d=json.load(open('$json_file')); print(d.get('targetRepo','$repo_name'))" 2>/dev/null || echo "$repo_name")
      branch=$(python3 -c "import json; d=json.load(open('$json_file')); print(d.get('branchName',''))" 2>/dev/null || echo "")

      # Create session in DB
      db_create_session "$session_id" "team-engineering" "$target_repo" "" "$branch"
      db_update_session "$session_id" "$status"

      ((SYNCED++)) || true
      echo "    Synced: $session_id ($status)"

      break  # One JSON per session dir is enough
    done
  done
done

echo ""
echo "Sync complete: $SYNCED sessions synced, $SKIPPED repos skipped"
