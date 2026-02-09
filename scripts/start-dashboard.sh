#!/bin/bash
# Start Agent Service — single server on port 3030
set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
yarn build:unified 2>/dev/null || true
yarn workspace server build 2>/dev/null || true
export PORT=3030
exec yarn workspace server start
