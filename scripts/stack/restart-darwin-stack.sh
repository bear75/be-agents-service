#!/usr/bin/env bash
#
# Restart Darwin runtime:
# - OpenClaw gateway (darwin profile)
# - Darwin dashboard/API (port 3010)
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "[stack:darwin] Restarting Darwin gateway..."
"$SERVICE_ROOT/scripts/openclaw/manage-gateway-launchd.sh" darwin restart

echo "[stack:darwin] Restarting Darwin dashboard..."
"$SERVICE_ROOT/scripts/manage-darwin-dashboard-launchd.sh" restart

echo
echo "[stack:darwin] Current status"
"$SERVICE_ROOT/scripts/openclaw/manage-gateway-launchd.sh" darwin status
"$SERVICE_ROOT/scripts/manage-darwin-dashboard-launchd.sh" status
