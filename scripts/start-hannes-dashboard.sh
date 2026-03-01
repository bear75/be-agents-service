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
export APP_DISPLAY_NAME="${APP_DISPLAY_NAME:-Hannes AI}"
export OPENCLAW_CONFIG_PATH="${OPENCLAW_CONFIG_PATH:-$HOME/.openclaw-hannes/openclaw.json}"
export OPENCLAW_STATE_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw-hannes/state}"
export OPENCLAW_GATEWAY_PORT="${OPENCLAW_GATEWAY_PORT:-19001}"
export OPENCLAW_LAUNCHD_LABEL="${OPENCLAW_LAUNCHD_LABEL:-com.appcaire.openclaw-hannes}"
export APP_REQUIRED_LAUNCHD_JOBS="${APP_REQUIRED_LAUNCHD_JOBS:-com.appcaire.openclaw-hannes}"
export AGENT_JOBS_DIR="${AGENT_JOBS_DIR:-$SERVICE_ROOT/.compound-state/running-jobs-hannes}"
export AGENT_SESSION_LOGS_DIR="${AGENT_SESSION_LOGS_DIR:-$SERVICE_ROOT/.compound-state/orchestrator-sessions-hannes}"
export PLAN_DOCS_ROOT="${PLAN_DOCS_ROOT:-$HOME/HomeCare/strength-stride-coach/docs}"
export FILE_ACCESS_ALLOWED_PATHS="${FILE_ACCESS_ALLOWED_PATHS:-$HOME/HomeCare/strength-stride-coach}"
export DEFAULT_TARGET_REPO="${DEFAULT_TARGET_REPO:-hannes-projects}"
export ENABLE_NIGHTLY_TRIGGER="${ENABLE_NIGHTLY_TRIGGER:-false}"
export AUTO_COMPOUND_LAUNCHD_LABEL="${AUTO_COMPOUND_LAUNCHD_LABEL:-com.appcaire.auto-compound-hannes}"
export OPENCLAW_WORKSPACE_REPO_KEY="${OPENCLAW_WORKSPACE_REPO_KEY:-darwin}"

mkdir -p "$OPENCLAW_STATE_DIR" "$AGENT_JOBS_DIR" "$AGENT_SESSION_LOGS_DIR"

cd "$SERVICE_ROOT"

echo "[start-hannes-dashboard] PORT=$PORT"
echo "[start-hannes-dashboard] AGENT_API_URL=$AGENT_API_URL"
echo "[start-hannes-dashboard] REPOS_CONFIG_PATH=$REPOS_CONFIG_PATH"
echo "[start-hannes-dashboard] AGENT_DB_PATH=$AGENT_DB_PATH"
echo "[start-hannes-dashboard] APP_DISPLAY_NAME=$APP_DISPLAY_NAME"
echo "[start-hannes-dashboard] OPENCLAW_CONFIG_PATH=$OPENCLAW_CONFIG_PATH"
echo "[start-hannes-dashboard] OPENCLAW_STATE_DIR=$OPENCLAW_STATE_DIR"
echo "[start-hannes-dashboard] OPENCLAW_LAUNCHD_LABEL=$OPENCLAW_LAUNCHD_LABEL"
echo "[start-hannes-dashboard] AGENT_JOBS_DIR=$AGENT_JOBS_DIR"
echo "[start-hannes-dashboard] PLAN_DOCS_ROOT=$PLAN_DOCS_ROOT"
echo "[start-hannes-dashboard] FILE_ACCESS_ALLOWED_PATHS=$FILE_ACCESS_ALLOWED_PATHS"

yarn build:unified 2>/dev/null || true
yarn workspace server build 2>/dev/null || true

exec yarn workspace server start
