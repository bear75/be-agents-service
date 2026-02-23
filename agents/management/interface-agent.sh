#!/bin/bash
#
# Interface Agent - Human-Agent Interface
# Shared folder, Telegram only, workspace sync (WhatsApp removed)
#
# Usage:
#   ./interface-agent.sh [status]
#
# Note: The Interface Agent runs via OpenClaw gateway (launchd).
# This script is for manual status/health checks.
# Messages are routed by the gateway to appropriate agents.
#

set -euo pipefail

ACTION="${1:-status}"

case "$ACTION" in
  status)
    echo "[Interface] Human-Agent Interface"
    echo "[Interface] Gateway: check ai.openclaw.gateway (port 18789)"
    echo "[Interface] Workspace: workspace/ (inbox, priorities, tasks)"
    echo "[Interface] Channels: Telegram only (WhatsApp removed)"
    lsof -i :18789 2>/dev/null && echo "[Interface] Gateway is running" || echo "[Interface] Gateway may not be running"
    exit 0
    ;;
  *)
    echo "[Interface] Use: $0 status"
    exit 0
    ;;
esac
