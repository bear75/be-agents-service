#!/usr/bin/env bash
#
# Start isolated Hannes dashboard/API stack using shared be-agents-service code.
# Runs on a separate port, repo config, and SQLite DB file.
#
# Usage:
#   ./scripts/start-hannes-dashboard.sh
#   PORT=3011 ./scripts/start-hannes-dashboard.sh
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

export PORT="${PORT:-3011}"
export AGENT_API_URL="${AGENT_API_URL:-http://localhost:${PORT}}"
export REPOS_CONFIG_PATH="${REPOS_CONFIG_PATH:-$SERVICE_ROOT/config/repos.hannes.yaml}"
export AGENT_DB_PATH="${AGENT_DB_PATH:-$SERVICE_ROOT/.compound-state/agent-service-hannes.db}"

cd "$SERVICE_ROOT"

echo "[start-hannes-dashboard] PORT=$PORT"
echo "[start-hannes-dashboard] AGENT_API_URL=$AGENT_API_URL"
echo "[start-hannes-dashboard] REPOS_CONFIG_PATH=$REPOS_CONFIG_PATH"
echo "[start-hannes-dashboard] AGENT_DB_PATH=$AGENT_DB_PATH"

yarn build:unified 2>/dev/null || true
yarn workspace server build 2>/dev/null || true

exec yarn workspace server start
