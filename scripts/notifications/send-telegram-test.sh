#!/usr/bin/env bash
#
# Send Telegram test message(s) to one or more chat IDs.
#
# Usage:
#   ./scripts/notifications/send-telegram-test.sh
#   ./scripts/notifications/send-telegram-test.sh --ids 8399128208 7604480012
#   ./scripts/notifications/send-telegram-test.sh --ids 8399128208 --label "post-restart"
#

set -euo pipefail

ENV_FILE="$HOME/.config/caire/env"
LABEL="manual"
IDS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ids)
      shift
      while [[ $# -gt 0 && "$1" != --* ]]; do
        IDS+=("$1")
        shift
      done
      ;;
    --label)
      LABEL="${2:-manual}"
      shift 2
      ;;
    -h|--help)
      cat <<'EOF'
Usage: ./scripts/notifications/send-telegram-test.sh [options]

Options:
  --ids <id1> [id2 ...]   One or more Telegram chat IDs
  --label <text>          Label to include in message (default: manual)
  -h, --help              Show this help
EOF
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck source=/dev/null
  source "$ENV_FILE" || true
fi

if [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]]; then
  echo "❌ TELEGRAM_BOT_TOKEN is not set (or missing in $ENV_FILE)" >&2
  exit 1
fi

if [[ "${#IDS[@]}" -eq 0 ]]; then
  if [[ -n "${TELEGRAM_CHAT_ID:-}" ]]; then
    IDS=("$TELEGRAM_CHAT_ID")
  else
    echo "❌ No chat IDs provided. Use --ids or set TELEGRAM_CHAT_ID." >&2
    exit 1
  fi
fi

timestamp="$(date +'%Y-%m-%d %H:%M:%S')"
hostname="$(hostname 2>/dev/null || echo mac-mini)"
msg="✅ Telegram test (${LABEL}) ${timestamp} from ${hostname}"

ok_count=0
fail_count=0

for chat_id in "${IDS[@]}"; do
  response="$(curl -s -X POST \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${chat_id}" \
    -d "text=${msg}" \
    2>/dev/null || echo '{"ok":false}')"

  if echo "$response" | jq -e '.ok == true' >/dev/null 2>&1; then
    echo "✅ Sent Telegram test to chat_id=${chat_id}"
    ok_count=$((ok_count + 1))
  else
    desc="$(echo "$response" | jq -r '.description // "unknown error"' 2>/dev/null || echo "unknown error")"
    echo "❌ Failed Telegram test for chat_id=${chat_id}: $desc"
    fail_count=$((fail_count + 1))
  fi
done

echo
echo "Summary: sent=${ok_count} failed=${fail_count}"
if [[ "$fail_count" -gt 0 ]]; then
  exit 1
fi

exit 0
