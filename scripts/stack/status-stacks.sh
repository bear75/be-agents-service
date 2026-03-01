#!/usr/bin/env bash
#
# Unified runtime status for Darwin + Hannes stacks.
# Can also send a status summary to Telegram.
#
# Usage:
#   ./scripts/stack/status-stacks.sh
#   ./scripts/stack/status-stacks.sh --darwin-only
#   ./scripts/stack/status-stacks.sh --hannes-only
#   ./scripts/stack/status-stacks.sh --telegram --ids 8399128208
#   ./scripts/stack/status-stacks.sh --telegram --token "<BOT_TOKEN>" --ids 7604480012
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="$HOME/.config/caire/env"

CHECK_DARWIN=true
CHECK_HANNES=true
SEND_TELEGRAM=false
BOT_TOKEN_OVERRIDE=""
IDS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --darwin-only)
      CHECK_DARWIN=true
      CHECK_HANNES=false
      shift
      ;;
    --hannes-only)
      CHECK_DARWIN=false
      CHECK_HANNES=true
      shift
      ;;
    --telegram)
      SEND_TELEGRAM=true
      shift
      ;;
    --token)
      BOT_TOKEN_OVERRIDE="${2:-}"
      shift 2
      ;;
    --ids)
      shift
      while [[ $# -gt 0 && "$1" != --* ]]; do
        IDS+=("$1")
        shift
      done
      ;;
    -h|--help)
      cat <<'EOF'
Usage: ./scripts/stack/status-stacks.sh [options]

Options:
  --darwin-only            Show Darwin stack only
  --hannes-only            Show Hannes stack only
  --telegram               Send summary via Telegram
  --token <bot-token>      Override TELEGRAM_BOT_TOKEN for --telegram
  --ids <id1> [id2 ...]    Telegram chat IDs (default: TELEGRAM_CHAT_ID)
  -h, --help               Show help
EOF
      exit 0
      ;;
    *)
      echo "[stack:status] Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck source=/dev/null
  source "$ENV_FILE" || true
fi

if [[ -n "$BOT_TOKEN_OVERRIDE" ]]; then
  TELEGRAM_BOT_TOKEN="$BOT_TOKEN_OVERRIDE"
fi

if [[ "${#IDS[@]}" -eq 0 && -n "${TELEGRAM_CHAT_ID:-}" ]]; then
  IDS=("$TELEGRAM_CHAT_ID")
fi

uid="$(id -u)"

launchd_loaded() {
  local label="$1"
  launchctl print "gui/$uid/$label" >/dev/null 2>&1
}

port_listening() {
  local port="$1"
  lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
}

health_ok() {
  local url="$1"
  local body
  body="$(curl -fsS "$url" 2>/dev/null || true)"
  [[ -n "$body" ]] && echo "$body" | jq -e '.success == true' >/dev/null 2>&1
}

line_status() {
  local label="$1"
  local ok="$2"
  if [[ "$ok" == "true" ]]; then
    echo "[OK]  $label"
  else
    echo "[ERR] $label"
  fi
}

SUMMARY_LINES=()
ALL_OK=true
timestamp="$(date +'%Y-%m-%d %H:%M:%S')"

if [[ "$CHECK_DARWIN" == "true" ]]; then
  darwin_gateway_loaded=false
  darwin_gateway_port=false
  darwin_dashboard_loaded=false
  darwin_dashboard_port=false
  darwin_dashboard_health=false

  launchd_loaded "com.appcaire.openclaw-darwin" && darwin_gateway_loaded=true
  port_listening 18789 && darwin_gateway_port=true
  launchd_loaded "com.appcaire.agent-server" && darwin_dashboard_loaded=true
  port_listening 3010 && darwin_dashboard_port=true
  health_ok "http://localhost:3010/health" && darwin_dashboard_health=true

  SUMMARY_LINES+=("DARWIN")
  SUMMARY_LINES+=("$(line_status "gateway launchd (com.appcaire.openclaw-darwin)" "$darwin_gateway_loaded")")
  SUMMARY_LINES+=("$(line_status "gateway port 18789" "$darwin_gateway_port")")
  SUMMARY_LINES+=("$(line_status "dashboard launchd (com.appcaire.agent-server)" "$darwin_dashboard_loaded")")
  SUMMARY_LINES+=("$(line_status "dashboard port 3010" "$darwin_dashboard_port")")
  SUMMARY_LINES+=("$(line_status "dashboard health /health" "$darwin_dashboard_health")")
  SUMMARY_LINES+=("")

  if [[ "$darwin_gateway_loaded" != "true" || "$darwin_gateway_port" != "true" || "$darwin_dashboard_loaded" != "true" || "$darwin_dashboard_port" != "true" || "$darwin_dashboard_health" != "true" ]]; then
    ALL_OK=false
  fi
fi

if [[ "$CHECK_HANNES" == "true" ]]; then
  hannes_gateway_loaded=false
  hannes_gateway_port=false
  hannes_dashboard_loaded=false
  hannes_dashboard_port=false
  hannes_dashboard_health=false

  launchd_loaded "com.appcaire.openclaw-hannes" && hannes_gateway_loaded=true
  port_listening 19001 && hannes_gateway_port=true
  launchd_loaded "com.appcaire.hannes-dashboard" && hannes_dashboard_loaded=true
  port_listening 3011 && hannes_dashboard_port=true
  health_ok "http://localhost:3011/health" && hannes_dashboard_health=true

  SUMMARY_LINES+=("HANNES")
  SUMMARY_LINES+=("$(line_status "gateway launchd (com.appcaire.openclaw-hannes)" "$hannes_gateway_loaded")")
  SUMMARY_LINES+=("$(line_status "gateway port 19001" "$hannes_gateway_port")")
  SUMMARY_LINES+=("$(line_status "dashboard launchd (com.appcaire.hannes-dashboard)" "$hannes_dashboard_loaded")")
  SUMMARY_LINES+=("$(line_status "dashboard port 3011" "$hannes_dashboard_port")")
  SUMMARY_LINES+=("$(line_status "dashboard health /health" "$hannes_dashboard_health")")
  SUMMARY_LINES+=("")

  if [[ "$hannes_gateway_loaded" != "true" || "$hannes_gateway_port" != "true" || "$hannes_dashboard_loaded" != "true" || "$hannes_dashboard_port" != "true" || "$hannes_dashboard_health" != "true" ]]; then
    ALL_OK=false
  fi
fi

echo "Stack status @ $timestamp"
for line in "${SUMMARY_LINES[@]}"; do
  echo "$line"
done

overall_text="DOWN"
if [[ "$ALL_OK" == "true" ]]; then
  overall_text="RUNNING"
fi
echo "Overall: $overall_text"

if [[ "$SEND_TELEGRAM" == "true" ]]; then
  if [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]]; then
    echo "[stack:status] TELEGRAM_BOT_TOKEN is missing for --telegram" >&2
    exit 1
  fi
  if [[ "${#IDS[@]}" -eq 0 ]]; then
    echo "[stack:status] No Telegram IDs provided (use --ids or TELEGRAM_CHAT_ID)" >&2
    exit 1
  fi

  msg=$(
    {
      echo "Stack status: $overall_text"
      echo "Time: $timestamp"
      for line in "${SUMMARY_LINES[@]}"; do
        echo "$line"
      done
    } | sed '/^$/N;/^\n$/D'
  )

  for chat_id in "${IDS[@]}"; do
    response="$(curl -s -X POST \
      "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d "chat_id=${chat_id}" \
      --data-urlencode "text=${msg}" \
      2>/dev/null || echo '{"ok":false}')"
    if echo "$response" | jq -e '.ok == true' >/dev/null 2>&1; then
      echo "[stack:status] Telegram sent to chat_id=${chat_id}"
    else
      desc="$(echo "$response" | jq -r '.description // "unknown error"' 2>/dev/null || echo "unknown error")"
      echo "[stack:status] Telegram failed for chat_id=${chat_id}: $desc" >&2
    fi
  done
fi

if [[ "$ALL_OK" != "true" ]]; then
  exit 1
fi

