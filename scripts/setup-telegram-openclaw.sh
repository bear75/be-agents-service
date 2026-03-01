#!/bin/bash
#
# Fix Telegram connection for Darwin/OpenClaw
#
# Run with your Telegram user ID (get it from @userinfobot):
#   ./scripts/setup-telegram-openclaw.sh 123456789
#
# Or run without args to see what's wrong:
#   ./scripts/setup-telegram-openclaw.sh
#

set -euo pipefail

CONFIG="$HOME/.openclaw/openclaw.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
USER_ID_ARG=""
SEND_TEST=false

for arg in "$@"; do
  if [[ "$arg" == "--test" ]]; then
    SEND_TEST=true
  elif [[ -z "$USER_ID_ARG" ]]; then
    USER_ID_ARG="$arg"
  fi
done

echo "=== Darwin + OpenClaw Telegram Setup ==="
echo ""

# Check config exists
if [[ ! -f "$CONFIG" ]]; then
  echo "❌ Config not found: $CONFIG"
  echo ""
  echo "Copy the template first:"
  echo "  cp $SERVICE_ROOT/config/openclaw/openclaw.json ~/.openclaw/openclaw.json"
  exit 1
fi

# Check for placeholder
if grep -q "YOUR_TELEGRAM_USER_ID" "$CONFIG"; then
  if [[ -n "$USER_ID_ARG" ]]; then
    echo "Updating config with your Telegram user ID: $USER_ID_ARG"
    # Use sed to replace the placeholder (macOS compatible)
    sed -i '' "s/\"YOUR_TELEGRAM_USER_ID\"/\"$USER_ID_ARG\"/g" "$CONFIG"
    echo "✅ Updated allowFrom with your user ID"
  else
    echo "❌ Telegram user ID is still the placeholder."
    echo ""
    echo "1. Open Telegram, message @userinfobot"
    echo "2. Copy your numeric user ID (e.g. 123456789)"
    echo "3. Run: $0 YOUR_USER_ID"
    echo "   Example: $0 123456789"
    exit 1
  fi
fi

# Check for placeholder bot token in OpenClaw config
if grep -q "YOUR_TELEGRAM_BOT_TOKEN" "$CONFIG"; then
  echo "⚠️  OpenClaw config still has bot token placeholder:"
  echo "   $CONFIG"
  echo "   Replace YOUR_TELEGRAM_BOT_TOKEN with your real token."
  echo ""
fi

# Check TELEGRAM_BOT_TOKEN
if [[ -z "$TELEGRAM_BOT_TOKEN" ]]; then
  if [[ -f "$HOME/.config/caire/env" ]]; then
    source "$HOME/.config/caire/env" 2>/dev/null || true
  fi
fi

if [[ -z "$TELEGRAM_BOT_TOKEN" ]]; then
  echo "⚠️  TELEGRAM_BOT_TOKEN not set."
  echo "   Add to ~/.config/caire/env:"
  echo "   export TELEGRAM_BOT_TOKEN=\"your-bot-token-from-botfather\""
  echo ""
fi

# Check TELEGRAM_CHAT_ID (required for notification scripts)
if [[ -z "${TELEGRAM_CHAT_ID:-}" ]]; then
  echo "⚠️  TELEGRAM_CHAT_ID not set."
  echo "   Add to ~/.config/caire/env:"
  echo "   export TELEGRAM_CHAT_ID=\"your-chat-id\""
  echo ""
fi

# Verify Darwin is reachable (current default 3010; legacy 3030 fallback)
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3010/health 2>/dev/null | rg -q '^200$'; then
  echo "✅ Darwin server (3010) is running"
elif curl -s -o /dev/null -w "%{http_code}" http://localhost:3030/health 2>/dev/null | rg -q '^200$'; then
  echo "✅ Darwin server (3030) is running"
else
  echo "⚠️  Darwin server not reachable on 3010 or 3030. Start with: yarn start"
fi

# Inject TELEGRAM_BOT_TOKEN into OpenClaw gateway plist (launchd doesn't source env)
if [[ -n "$TELEGRAM_BOT_TOKEN" ]] && [[ -f "$HOME/Library/LaunchAgents/ai.openclaw.gateway.plist" ]]; then
  /usr/libexec/PlistBuddy -c "Add :EnvironmentVariables:TELEGRAM_BOT_TOKEN string '$TELEGRAM_BOT_TOKEN'" "$HOME/Library/LaunchAgents/ai.openclaw.gateway.plist" 2>/dev/null || \
  /usr/libexec/PlistBuddy -c "Set :EnvironmentVariables:TELEGRAM_BOT_TOKEN '$TELEGRAM_BOT_TOKEN'" "$HOME/Library/LaunchAgents/ai.openclaw.gateway.plist" 2>/dev/null
  echo "✅ Injected TELEGRAM_BOT_TOKEN into gateway plist"
fi

# Optional live send test for notification channel
if [[ "$SEND_TEST" == "true" ]]; then
  echo ""
  echo "Running Telegram send test..."
  if [[ -n "${TELEGRAM_BOT_TOKEN:-}" && -n "${TELEGRAM_CHAT_ID:-}" ]]; then
    TEST_MSG="✅ Darwin Telegram test $(date +'%Y-%m-%d %H:%M:%S')"
    RESPONSE=$(curl -s -X POST \
      "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d "chat_id=${TELEGRAM_CHAT_ID}" \
      -d "text=${TEST_MSG}" \
      2>/dev/null || echo '{"ok":false}')
    if echo "$RESPONSE" | jq -r '.ok // false' 2>/dev/null | rg -q '^true$'; then
      echo "✅ Telegram send test succeeded"
    else
      echo "❌ Telegram send test failed"
      echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
    fi
  else
    echo "❌ Cannot run send test: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required."
  fi
fi

# Restart OpenClaw gateway
echo ""
echo "Restart OpenClaw gateway to apply config:"
echo "  source ~/.config/caire/env"
echo "  openclaw gateway restart"
echo ""
echo "Optional: send test notification"
echo "  ./scripts/setup-telegram-openclaw.sh ${USER_ID_ARG:-YOUR_USER_ID} --test"
echo ""
