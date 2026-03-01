#!/usr/bin/env bash
#
# Restart isolated Hannes dashboard/API stack.
# Kills configured port, then starts server in foreground.
#
# Usage:
#   ./scripts/restart-hannes-dashboard.sh
#   PORT=3011 ./scripts/restart-hannes-dashboard.sh
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

export PORT="${PORT:-3011}"

pid="$(lsof -ti ":$PORT" 2>/dev/null || true)"
if [[ -n "$pid" ]]; then
  echo "[restart-hannes-dashboard] Killing port $PORT (PID $pid)"
  kill -9 $pid 2>/dev/null || true
fi

sleep 1

exec "$SERVICE_ROOT/scripts/start-hannes-dashboard.sh"
