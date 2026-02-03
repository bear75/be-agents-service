#!/bin/bash
# scripts/update-claude-md.sh
# Updates timestamp and counter in CLAUDE.md files

set -e

CLAUDE_MD=$1
DATE=$(date +%Y-%m-%d)

if [ -z "$CLAUDE_MD" ]; then
  echo "Usage: $0 <path-to-CLAUDE.md>"
  exit 1
fi

if [ ! -f "$CLAUDE_MD" ]; then
  echo "Error: File not found: $CLAUDE_MD"
  exit 1
fi

# Update "Last updated" timestamp
if grep -q "Last updated:" "$CLAUDE_MD"; then
  sed -i.bak "s/Last updated: .*/Last updated: $DATE/" "$CLAUDE_MD"
else
  echo "Warning: 'Last updated:' not found in $CLAUDE_MD"
fi

# Update "Times updated" counter
if grep -q "Times updated:" "$CLAUDE_MD"; then
  CURRENT=$(grep "Times updated:" "$CLAUDE_MD" | grep -o '[0-9]*' | head -1)
  if [ -n "$CURRENT" ]; then
    NEW=$((CURRENT + 1))
    sed -i.bak "s/Times updated: $CURRENT/Times updated: $NEW/" "$CLAUDE_MD"
  else
    echo "Warning: Could not parse 'Times updated' counter in $CLAUDE_MD"
  fi
else
  echo "Warning: 'Times updated:' not found in $CLAUDE_MD"
fi

# Remove backup file
rm -f "${CLAUDE_MD}.bak"

echo "✓ Updated $CLAUDE_MD (date: $DATE)"
