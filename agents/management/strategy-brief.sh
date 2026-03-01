#!/bin/bash
#
# Strategy Brief - Management phase
# Produces a one-page strategy/alignment brief from the priority for use by engineering and marketing.
#
# Usage:
#   ./strategy-brief.sh <session_id> <target_repo> <priority_file>
#
# Writes: .compound-state/<session_id>/strategy-brief.md
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
STATE_DIR="${SERVICE_ROOT}/.compound-state"

SESSION_ID="${1:-}"
TARGET_REPO="${2:-}"
PRIORITY_FILE="${3:-}"

if [[ -z "$SESSION_ID" || -z "$TARGET_REPO" || -z "$PRIORITY_FILE" ]]; then
  echo "[Strategy] Usage: $0 <session_id> <target_repo> <priority_file>"
  exit 0
fi

if [[ ! -f "$PRIORITY_FILE" ]]; then
  echo "[Strategy] Priority file not found: $PRIORITY_FILE"
  exit 1
fi

SESSION_DIR="$STATE_DIR/$SESSION_ID"
mkdir -p "$SESSION_DIR"
BRIEF_FILE="$SESSION_DIR/strategy-brief.md"

PRIORITY_CONTENT=$(cat "$PRIORITY_FILE")

echo "[Strategy] Producing strategy brief for session $SESSION_ID..."
# Capture Claude stdout to file (Claude may not write directly to path)
if claude -p "You are a strategy advisor (CEO/CPO/CMO perspective). Based on this priority:

---
$PRIORITY_CONTENT
---

Produce a one-page strategy brief (markdown) with:
1. Strategic intent (why this matters)
2. Success criteria (how we know we're done)
3. Alignment notes (product, tech, marketing angles)
4. Risks or dependencies to watch

Output only the markdown brief, no preamble or filename." --dangerously-skip-permissions 2>/dev/null > "$BRIEF_FILE"; then
  [[ -s "$BRIEF_FILE" ]] && echo "[Strategy] Brief written to $BRIEF_FILE" || rm -f "$BRIEF_FILE"
fi

if [[ ! -f "$BRIEF_FILE" || ! -s "$BRIEF_FILE" ]]; then
  echo "# Strategy brief (fallback)" > "$BRIEF_FILE"
  echo "" >> "$BRIEF_FILE"
  echo "Priority: see priority file. Proceed with engineering and marketing." >> "$BRIEF_FILE"
  echo "[Strategy] Fallback brief written"
fi
