#!/usr/bin/env bash
#
# Restart Hannes runtime:
# - OpenClaw gateway (hannes profile)
# - Hannes dashboard/API (port 3011)
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "[stack:hannes] Restarting Hannes gateway..."
"$SERVICE_ROOT/scripts/openclaw/manage-gateway-launchd.sh" hannes restart

echo "[stack:hannes] Restarting Hannes dashboard..."
"$SERVICE_ROOT/scripts/manage-hannes-dashboard-launchd.sh" restart

echo
echo "[stack:hannes] Current status"
"$SERVICE_ROOT/scripts/openclaw/manage-gateway-launchd.sh" hannes status
"$SERVICE_ROOT/scripts/manage-hannes-dashboard-launchd.sh" status
