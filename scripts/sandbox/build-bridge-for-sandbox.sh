#!/bin/bash
#
# Build and copy OpenClaw MCP bridge for sandbox distribution
#
# Use when sharing the bridge with someone who should NOT have access to the
# be-agents-service repo (e.g. son's sandbox). Copies the built bridge to a
# shared folder so they can run it with WORKSPACE_PATH pointing to their workspace.
#
# Usage:
#   ./scripts/sandbox/build-bridge-for-sandbox.sh
#   ./scripts/sandbox/build-bridge-for-sandbox.sh /path/to/destination
#   ./scripts/sandbox/build-bridge-for-sandbox.sh --skip-build /path/to/destination
#
# Default destination: ~/Shared/agent-workspace-bridge
# --skip-build: use existing dist (useful if build OOMs on low-memory machines)
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BRIDGE_DIR="$SERVICE_ROOT/apps/openclaw-bridge"

SKIP_BUILD=false
DEST=""
for arg in "$@"; do
  if [[ "$arg" == "--skip-build" ]]; then
    SKIP_BUILD=true
  else
    DEST="$arg"
  fi
done
DEST="${DEST:-$HOME/Shared/agent-workspace-bridge}"

if [[ "$SKIP_BUILD" != "true" ]]; then
  echo "[sandbox] Building openclaw-bridge..."
  cd "$SERVICE_ROOT"
  yarn install --silent 2>/dev/null || true
  yarn workspace openclaw-bridge build || {
    echo "[sandbox] Build failed. Using existing dist if present (run with --skip-build to skip build)."
    if [[ ! -d "$BRIDGE_DIR/dist" ]]; then
      exit 1
    fi
  }
else
  echo "[sandbox] Skipping build (using existing dist)"
fi

echo "[sandbox] Copying to $DEST..."
mkdir -p "$DEST"
rm -rf "$DEST/dist" "$DEST/package.json" "$DEST/node_modules"
cp -r "$BRIDGE_DIR/dist" "$DEST/"
cp "$BRIDGE_DIR/package.json" "$DEST/"

# Install production deps in destination (bridge needs @modelcontextprotocol/sdk, js-yaml, zod)
cd "$DEST" && yarn install --production 2>/dev/null || yarn install
cd - >/dev/null

echo "[sandbox] Done. Bridge is at: $DEST"
echo ""
echo "Sandbox OpenClaw config should use:"
echo "  \"command\": \"node\","
echo "  \"args\": [\"$DEST/dist/index.js\"],"
echo "  \"env\": { \"WORKSPACE_PATH\": \"/full/path/to/son/workspace\" }"
echo ""
echo "See config/openclaw/sandbox-openclaw.json for full template."
