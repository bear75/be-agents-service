#!/usr/bin/env bash
#
# Manage Darwin dashboard/API launchd service (port 3010).
#
# Usage:
#   ./scripts/manage-darwin-dashboard-launchd.sh install
#   ./scripts/manage-darwin-dashboard-launchd.sh restart
#   ./scripts/manage-darwin-dashboard-launchd.sh status
#

set -euo pipefail

ACTION="${1:-status}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PLIST_TEMPLATE="$SERVICE_ROOT/launchd/com.appcaire.agent-server.plist"

LABEL="com.appcaire.agent-server"
PLIST_PATH="$HOME/Library/LaunchAgents/${LABEL}.plist"
STDOUT_LOG="$HOME/Library/Logs/agent-server.log"
STDERR_LOG="$HOME/Library/Logs/agent-server-error.log"
USER_DOMAIN="gui/$(id -u)"

usage() {
  cat <<'EOF'
Usage: ./scripts/manage-darwin-dashboard-launchd.sh <action>

Actions:
  install     Copy plist template + bootstrap service
  start       Start an installed service
  stop        Stop service
  restart     Restart service
  status      Show launchd + port + health status
  uninstall   Stop and remove plist
EOF
}

is_loaded() {
  launchctl print "${USER_DOMAIN}/${LABEL}" >/dev/null 2>&1
}

free_dashboard_port() {
  local pid
  pid="$(lsof -ti :3010 2>/dev/null || true)"
  if [[ -n "$pid" ]]; then
    echo "[darwin-dashboard] Killing stale process on 3010 (PID $pid)"
    kill -9 "$pid" >/dev/null 2>&1 || true
    sleep 1
  fi
}

install_plist() {
  [[ -f "$PLIST_TEMPLATE" ]] || {
    echo "[darwin-dashboard] Missing template: $PLIST_TEMPLATE" >&2
    exit 1
  }
  mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
  cp "$PLIST_TEMPLATE" "$PLIST_PATH"
  echo "[darwin-dashboard] Installed plist: $PLIST_PATH"
}

start_job() {
  free_dashboard_port
  if [[ ! -f "$PLIST_PATH" ]]; then
    echo "[darwin-dashboard] Missing plist: $PLIST_PATH" >&2
    echo "[darwin-dashboard] Run: $0 install" >&2
    exit 1
  fi

  if is_loaded; then
    launchctl kickstart -k "${USER_DOMAIN}/${LABEL}" >/dev/null 2>&1 || true
    echo "[darwin-dashboard] Kickstarted ${LABEL}"
  else
    launchctl bootstrap "${USER_DOMAIN}" "$PLIST_PATH" >/dev/null 2>&1
    echo "[darwin-dashboard] Started ${LABEL}"
  fi
}

stop_job() {
  if is_loaded; then
    launchctl bootout "${USER_DOMAIN}/${LABEL}" >/dev/null 2>&1 || true
    echo "[darwin-dashboard] Stopped ${LABEL}"
  else
    echo "[darwin-dashboard] Not loaded: ${LABEL}"
  fi
}

status_job() {
  local health="down"
  if curl -fsS "http://localhost:3010/health" >/dev/null 2>&1; then
    health="up"
  fi

  echo "Label:       $LABEL"
  echo "Plist:       $PLIST_PATH"
  echo "Stdout log:  $STDOUT_LOG"
  echo "Stderr log:  $STDERR_LOG"
  if is_loaded; then
    echo "Service:     loaded"
  else
    echo "Service:     not loaded"
  fi
  if lsof -nP -iTCP:3010 -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Port:        listening on 3010"
  else
    echo "Port:        not listening on 3010"
  fi
  echo "Health:      $health (http://localhost:3010/health)"
}

case "$ACTION" in
  install)
    install_plist
    start_job
    status_job
    ;;
  start)
    start_job
    status_job
    ;;
  stop)
    stop_job
    status_job
    ;;
  restart)
    stop_job
    start_job
    status_job
    ;;
  status)
    status_job
    ;;
  uninstall)
    stop_job
    rm -f "$PLIST_PATH"
    echo "[darwin-dashboard] Removed plist: $PLIST_PATH"
    status_job
    ;;
  *)
    echo "[darwin-dashboard] Unknown action: $ACTION" >&2
    usage
    exit 1
    ;;
esac
