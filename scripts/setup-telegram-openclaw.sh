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

set -e

CONFIG="$HOME/.openclaw/openclaw.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

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
  if [[ -n "$1" ]]; then
    echo "Updating config with your Telegram user ID: $1"
    # Use sed to replace the placeholder (macOS compatible)
    sed -i '' "s/\"YOUR_TELEGRAM_USER_ID\"/\"$1\"/g" "$CONFIG"
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

# Verify Darwin is reachable
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3030/health 2>/dev/null | grep -q 200; then
  echo "✅ Darwin server (3030) is running"
else
  echo "⚠️  Darwin server (3030) not reachable. Start with: yarn start"
fi

# Inject TELEGRAM_BOT_TOKEN into OpenClaw gateway plist (launchd doesn't source env)
if [[ -n "$TELEGRAM_BOT_TOKEN" ]] && [[ -f "$HOME/Library/LaunchAgents/ai.openclaw.gateway.plist" ]]; then
  /usr/libexec/PlistBuddy -c "Add :EnvironmentVariables:TELEGRAM_BOT_TOKEN string '$TELEGRAM_BOT_TOKEN'" "$HOME/Library/LaunchAgents/ai.openclaw.gateway.plist" 2>/dev/null || \
  /usr/libexec/PlistBuddy -c "Set :EnvironmentVariables:TELEGRAM_BOT_TOKEN '$TELEGRAM_BOT_TOKEN'" "$HOME/Library/LaunchAgents/ai.openclaw.gateway.plist" 2>/dev/null
  echo "✅ Injected TELEGRAM_BOT_TOKEN into gateway plist"
fi

# Restart OpenClaw gateway
echo ""
echo "Restart OpenClaw gateway to apply config:"
echo "  source ~/.config/caire/env"
echo "  openclaw gateway restart"
echo ""
