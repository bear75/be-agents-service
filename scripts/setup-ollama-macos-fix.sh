#!/bin/bash
#
# Fix Ollama on macOS 26+ when MLX dynamic library fails
#
# The MLX library may not load on macOS 26.2+ / Apple Silicon.
# Forcing OLLAMA_LLM_LIBRARY=cpu_avx2 bypasses MLX and uses
# the embedded Metal library instead, which works.
#
# Usage:
#   ./scripts/setup-ollama-macos-fix.sh
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PLIST_TEMPLATE="$SERVICE_ROOT/launchd/com.appcaire.ollama.plist.template"
PLIST_DEST="$HOME/Library/LaunchAgents/com.appcaire.ollama.plist"

if [[ ! -f "$PLIST_TEMPLATE" ]]; then
  echo "❌ Plist template not found: $PLIST_TEMPLATE"
  exit 1
fi

if ! command -v ollama &>/dev/null; then
  echo "❌ Ollama not found. Run: brew install ollama && ollama pull phi"
  exit 1
fi

echo "Fixing Ollama for macOS 26+ (MLX → embedded Metal fallback)"
echo ""

# Stop brew-managed ollama if running
brew services stop ollama 2>/dev/null || true
launchctl unload ~/Library/LaunchAgents/com.appcaire.ollama.plist 2>/dev/null || true
pkill -9 ollama 2>/dev/null || true
sleep 2

# Install wrapper script (launchd may not pass EnvironmentVariables to child ollama runner)
mkdir -p "$HOME/bin"
WRAPPER="$HOME/bin/ollama-serve-fixed"
cp "$SERVICE_ROOT/scripts/ollama-serve-fixed.sh" "$WRAPPER"
chmod +x "$WRAPPER"
echo "✓ Installed wrapper: $WRAPPER"

# Generate plist from template (substitute __HOME__)
sed "s|__HOME__|$HOME|g" "$PLIST_TEMPLATE" > "$PLIST_DEST"
echo "✓ Installed com.appcaire.ollama.plist"

# Load
launchctl load "$PLIST_DEST" 2>/dev/null || true

sleep 3
echo ""
echo "✓ Done. Test with: echo 'Say hi' | ollama run phi"
