#!/usr/bin/env bash
#
# Manage isolated Hannes dashboard as a dedicated launchd service.
#
# Usage:
#   ./scripts/manage-hannes-dashboard-launchd.sh install
#   ./scripts/manage-hannes-dashboard-launchd.sh restart
#   ./scripts/manage-hannes-dashboard-launchd.sh status
#

set -euo pipefail

ACTION="${1:-status}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

LABEL="com.appcaire.hannes-dashboard"
PLIST_PATH="$HOME/Library/LaunchAgents/${LABEL}.plist"
STDOUT_LOG="$HOME/Library/Logs/${LABEL}.log"
STDERR_LOG="$HOME/Library/Logs/${LABEL}-error.log"
USER_DOMAIN="gui/$(id -u)"

usage() {
  cat <<'EOF'
Usage: ./scripts/manage-hannes-dashboard-launchd.sh <action>

Actions:
  install     Write plist + bootstrap service
  start       Start an installed service
  stop        Stop service
  restart     Restart service
  status      Show launchd + port status
  uninstall   Stop and remove plist
EOF
}

is_loaded() {
  launchctl print "${USER_DOMAIN}/${LABEL}" >/dev/null 2>&1
}

free_dashboard_port() {
  local pid
  pid="$(lsof -ti :3011 2>/dev/null || true)"
  if [[ -n "$pid" ]]; then
    echo "[hannes-dashboard] Killing stale process on 3011 (PID $pid)"
    kill -9 $pid >/dev/null 2>&1 || true
    sleep 1
  fi
}

write_plist() {
  mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
  cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>

  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>cd "${SERVICE_ROOT}" && exec ./scripts/start-hannes-dashboard.sh</string>
  </array>

  <key>WorkingDirectory</key>
  <string>${SERVICE_ROOT}</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>

  <key>StandardOutPath</key>
  <string>${STDOUT_LOG}</string>
  <key>StandardErrorPath</key>
  <string>${STDERR_LOG}</string>

  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>
</dict>
</plist>
EOF
  echo "[hannes-dashboard] Wrote plist: $PLIST_PATH"
}

start_job() {
  free_dashboard_port
  if [[ ! -f "$PLIST_PATH" ]]; then
    echo "[hannes-dashboard] Missing plist: $PLIST_PATH" >&2
    echo "[hannes-dashboard] Run: $0 install" >&2
    exit 1
  fi

  if is_loaded; then
    launchctl kickstart -k "${USER_DOMAIN}/${LABEL}" >/dev/null 2>&1 || true
    echo "[hannes-dashboard] Kickstarted ${LABEL}"
  else
    launchctl bootstrap "${USER_DOMAIN}" "$PLIST_PATH" >/dev/null 2>&1
    echo "[hannes-dashboard] Started ${LABEL}"
  fi
}

stop_job() {
  if is_loaded; then
    launchctl bootout "${USER_DOMAIN}/${LABEL}" >/dev/null 2>&1 || true
    echo "[hannes-dashboard] Stopped ${LABEL}"
  else
    echo "[hannes-dashboard] Not loaded: ${LABEL}"
  fi
}

status_job() {
  echo "Label:       $LABEL"
  echo "Plist:       $PLIST_PATH"
  echo "Stdout log:  $STDOUT_LOG"
  echo "Stderr log:  $STDERR_LOG"
  if is_loaded; then
    echo "Service:     loaded"
  else
    echo "Service:     not loaded"
  fi
  if lsof -nP -iTCP:3011 -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Port:        listening on 3011"
  else
    echo "Port:        not listening on 3011"
  fi
}

case "$ACTION" in
  install)
    write_plist
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
    echo "[hannes-dashboard] Removed plist: $PLIST_PATH"
    status_job
    ;;
  *)
    echo "[hannes-dashboard] Unknown action: $ACTION" >&2
    usage
    exit 1
    ;;
esac
