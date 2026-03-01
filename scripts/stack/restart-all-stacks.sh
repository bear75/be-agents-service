#!/usr/bin/env bash
#
# Restart all runtime surfaces:
# - Darwin gateway + dashboard
# - Hannes gateway + dashboard
#
# Also ensures launchd services are installed and loaded.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "[stack:all] Ensuring dual OpenClaw launchd services..."
"$SERVICE_ROOT/scripts/openclaw/setup-dual-launchd.sh"

echo "[stack:all] Ensuring Darwin dashboard launchd service..."
"$SERVICE_ROOT/scripts/manage-darwin-dashboard-launchd.sh" install

echo "[stack:all] Ensuring Hannes dashboard launchd service..."
"$SERVICE_ROOT/scripts/manage-hannes-dashboard-launchd.sh" install

echo
echo "[stack:all] Restarting Darwin runtime..."
"$SERVICE_ROOT/scripts/stack/restart-darwin-stack.sh"

echo
echo "[stack:all] Restarting Hannes runtime..."
"$SERVICE_ROOT/scripts/stack/restart-hannes-stack.sh"

echo
echo "[stack:all] Done."
