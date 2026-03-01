#!/usr/bin/env bash
#
# Manage isolated OpenClaw gateway launchd services per profile.
# This avoids shared ai.openclaw.gateway label conflicts between stacks.
#
# Usage:
#   ./scripts/openclaw/manage-gateway-launchd.sh darwin install
#   ./scripts/openclaw/manage-gateway-launchd.sh hannes restart
#   ./scripts/openclaw/manage-gateway-launchd.sh darwin status
#

set -euo pipefail

PROFILE="${1:-}"
ACTION="${2:-status}"

usage() {
  cat <<'EOF'
Usage:
  ./scripts/openclaw/manage-gateway-launchd.sh <darwin|hannes> <action>

Actions:
  install     Write plist + bootstrap service
  start       Start an installed service
  stop        Stop a running service
  restart     Restart service
  status      Show launchd + port status
  uninstall   Stop service and remove plist
EOF
}

expand_home() {
  local value="${1:-}"
  echo "${value/#\~/$HOME}"
}

if [[ -z "$PROFILE" ]]; then
  usage
  exit 1
fi

if [[ "$PROFILE" != "darwin" && "$PROFILE" != "hannes" ]]; then
  echo "[openclaw-service] Unknown profile: $PROFILE" >&2
  usage
  exit 1
fi

case "$PROFILE" in
  darwin)
    LABEL="${OPENCLAW_DARWIN_LABEL:-com.appcaire.openclaw-darwin}"
    CONFIG_PATH="$(expand_home "${OPENCLAW_DARWIN_CONFIG:-$HOME/.openclaw/openclaw.json}")"
    STATE_DIR="$(expand_home "${OPENCLAW_DARWIN_STATE:-$HOME/.openclaw/state}")"
    PORT="${OPENCLAW_DARWIN_PORT:-18789}"
    ;;
  hannes)
    LABEL="${OPENCLAW_HANNES_LABEL:-com.appcaire.openclaw-hannes}"
    CONFIG_PATH="$(expand_home "${OPENCLAW_HANNES_CONFIG:-$HOME/.openclaw-hannes/openclaw.json}")"
    STATE_DIR="$(expand_home "${OPENCLAW_HANNES_STATE:-$HOME/.openclaw-hannes/state}")"
    PORT="${OPENCLAW_HANNES_PORT:-19001}"
    ;;
esac

LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
LOG_DIR="$HOME/Library/Logs"
PLIST_PATH="$LAUNCH_AGENTS_DIR/${LABEL}.plist"
STDOUT_LOG="$LOG_DIR/${LABEL}.log"
STDERR_LOG="$LOG_DIR/${LABEL}-error.log"
USER_DOMAIN="gui/$(id -u)"

log() { echo "[openclaw-service:$PROFILE] $*"; }

ensure_prerequisites() {
  command -v launchctl >/dev/null 2>&1 || {
    echo "[openclaw-service:$PROFILE] launchctl not available (macOS required)" >&2
    exit 1
  }
}

ensure_runtime() {
  command -v openclaw >/dev/null 2>&1 || {
    echo "[openclaw-service:$PROFILE] openclaw CLI not found in PATH" >&2
    exit 1
  }
  if [[ ! -f "$CONFIG_PATH" ]]; then
    echo "[openclaw-service:$PROFILE] Missing OpenClaw config: $CONFIG_PATH" >&2
    exit 1
  fi
}

write_plist() {
  mkdir -p "$LAUNCH_AGENTS_DIR" "$LOG_DIR" "$STATE_DIR"
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
    <string>export OPENCLAW_CONFIG_PATH="${CONFIG_PATH}"; export OPENCLAW_STATE_DIR="${STATE_DIR}"; export OPENCLAW_GATEWAY_PORT="${PORT}"; exec openclaw gateway --port "${PORT}"</string>
  </array>

  <key>WorkingDirectory</key>
  <string>${HOME}</string>

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
  log "Wrote plist: $PLIST_PATH"
}

is_loaded() {
  launchctl print "${USER_DOMAIN}/${LABEL}" >/dev/null 2>&1
}

stop_job() {
  if is_loaded; then
    launchctl bootout "${USER_DOMAIN}/${LABEL}" >/dev/null 2>&1 || true
    log "Stopped: ${LABEL}"
  else
    log "Not loaded: ${LABEL}"
  fi
}

start_job() {
  if [[ ! -f "$PLIST_PATH" ]]; then
    echo "[openclaw-service:$PROFILE] Missing plist: $PLIST_PATH" >&2
    echo "[openclaw-service:$PROFILE] Run: $0 $PROFILE install" >&2
    exit 1
  fi

  if is_loaded; then
    launchctl kickstart -k "${USER_DOMAIN}/${LABEL}" >/dev/null 2>&1 || true
    log "Kickstarted: ${LABEL}"
  else
    launchctl bootstrap "${USER_DOMAIN}" "$PLIST_PATH" >/dev/null 2>&1
    log "Started: ${LABEL}"
  fi
}

status_job() {
  echo "Profile:      $PROFILE"
  echo "Label:        $LABEL"
  echo "Config path:  $CONFIG_PATH"
  echo "State dir:    $STATE_DIR"
  echo "Port:         $PORT"
  echo "Plist:        $PLIST_PATH"
  echo "Stdout log:   $STDOUT_LOG"
  echo "Stderr log:   $STDERR_LOG"
  if is_loaded; then
    echo "Service:      loaded"
  else
    echo "Service:      not loaded"
  fi
  if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Port status:  listening on $PORT"
  else
    echo "Port status:  not listening on $PORT"
  fi
}

ensure_prerequisites

case "$ACTION" in
  install)
    ensure_runtime
    write_plist
    start_job
    status_job
    ;;
  start)
    ensure_runtime
    start_job
    status_job
    ;;
  stop)
    stop_job
    status_job
    ;;
  restart)
    ensure_runtime
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
    log "Removed plist: $PLIST_PATH"
    status_job
    ;;
  *)
    echo "[openclaw-service:$PROFILE] Unknown action: $ACTION" >&2
    usage
    exit 1
    ;;
esac
