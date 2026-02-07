#!/bin/bash
#
# Start Multi-Agent Dashboard
# Simple HTTP server for monitoring agent sessions
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "Starting Multi-Agent Dashboard"
echo "========================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
  echo "Error: Node.js is not installed"
  echo "Please install Node.js: https://nodejs.org/"
  exit 1
fi

echo "Node.js version: $(node --version)"
echo "Dashboard directory: $SCRIPT_DIR"
echo ""

# Start server
cd "$SCRIPT_DIR"
exec node server.js
