#!/usr/bin/env bash
#
# Verify isolated Hannes dashboard/API stack.
#
# Usage:
#   ./scripts/verify-hannes-stack.sh
#   ./scripts/verify-hannes-stack.sh --send-telegram-test
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

export REPOS_CONFIG_PATH="${REPOS_CONFIG_PATH:-$SERVICE_ROOT/config/repos.hannes.yaml}"
REPOS_CONFIG_PATH="${REPOS_CONFIG_PATH/#\~/$HOME}"
export REPOS_CONFIG_PATH
export OPENCLAW_CONFIG_PATH="${OPENCLAW_CONFIG_PATH:-$HOME/.openclaw-hannes/openclaw.json}"
export OPENCLAW_LAUNCHD_LABEL="${OPENCLAW_LAUNCHD_LABEL:-com.appcaire.openclaw-hannes}"
export OPENCLAW_WORKSPACE_REPO_KEY="${OPENCLAW_WORKSPACE_REPO_KEY:-darwin}"
export APP_REQUIRED_LAUNCHD_JOBS="${APP_REQUIRED_LAUNCHD_JOBS:-com.appcaire.openclaw-hannes}"

DARWIN_URL="${DARWIN_URL:-http://localhost:3011}"

ARGS=(--repo hannes-projects --darwin-url "$DARWIN_URL")
if [[ "${1:-}" == "--send-telegram-test" ]]; then
  ARGS+=(--send-telegram-test)
fi

exec "$SERVICE_ROOT/scripts/verify-all-services.sh" "${ARGS[@]}"
