# Optional: move or copy OpenClaw workspace into the shared folder.
# Use on other machines or future runs if you need to migrate workspace data.
# If you've already moved everything (e.g. on the Mac mini), you can ignore this script.
#
# Usage: ./scripts/openclaw-migrate-workspace.sh

set -e

OPENCLAW_WS="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace/be-agents-service}"
SERVICE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="${CONFIG:-$HOME/.openclaw/openclaw.json}"

echo "=== OpenClaw workspace migration ==="
echo "Target (agent.workspace): $OPENCLAW_WS"
echo ""

if [[ ! -f "$CONFIG" ]]; then
  echo "No config at $CONFIG — copy from config/openclaw/ first."
  echo "  cp $SERVICE_ROOT/config/openclaw/openclaw.json ~/.openclaw/openclaw.json"
  exit 1
fi

mkdir -p "$OPENCLAW_WS"
echo "Ensured directory exists: $OPENCLAW_WS"
echo ""
echo "If you had an old workspace elsewhere, copy its contents into: $OPENCLAW_WS"
echo "Then run: openclaw gateway restart"
echo ""
echo "Done. New agent work will use the path in agent.workspace."
