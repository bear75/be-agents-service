#!/usr/bin/env bash
# Delete all rows from schedule_runs. Use when starting fresh with new formats/schedules.
# Run from repo root: ./scripts/clear-schedule-runs.sh

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DB="${REPO_ROOT}/.compound-state/agent-service.db"

if [[ ! -f "$DB" ]]; then
  echo "Database not found: $DB" >&2
  exit 1
fi

COUNT=$(sqlite3 "$DB" "SELECT COUNT(*) FROM schedule_runs;")
sqlite3 "$DB" "DELETE FROM schedule_runs;"
echo "Deleted ${COUNT} schedule run(s)."
