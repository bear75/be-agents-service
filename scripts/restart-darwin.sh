#!/usr/bin/env bash
# One command for any machine: kill everything, build, start (launchd if present, else foreground).
# Usage: yarn restart  or  ./scripts/restart-darwin.sh
set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
PLIST="$HOME/Library/LaunchAgents/com.appcaire.agent-server.plist"

# Stop: unload launchd (Mac mini / any machine with plist)
launchctl unload "$PLIST" 2>/dev/null || true

# Free ports 3010 and 3030
for p in 3010 3030; do
  pid=$(lsof -ti ":$p" 2>/dev/null || true)
  [ -z "$pid" ] || { echo "Killing port $p (PID $pid)"; kill -9 $pid 2>/dev/null || true; }
done
sleep 1

# Build
echo "Building..."
yarn build:unified && yarn workspace server build

# Start: use launchd if plist exists (runs in background), else foreground
if [ -f "$PLIST" ]; then
  launchctl load "$PLIST" && echo "Started via launchd. Dashboard: http://localhost:3010/" && exit 0
fi
echo "Starting in foreground..."
exec env PORT=3010 yarn workspace server start
