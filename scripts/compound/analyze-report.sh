#!/bin/bash

# scripts/compound/analyze-report.sh
# Analyzes a report and extracts the #1 priority item

set -e

REPORT_FILE="$1"

if [ -z "$REPORT_FILE" ]; then
  echo "Usage: $0 <report-file>"
  exit 1
fi

if [ ! -f "$REPORT_FILE" ]; then
  echo "Error: Report file not found: $REPORT_FILE"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Extract the priority item from the report
# Uses Ollama (local) for simple analysis when available, else Claude
# See docs/LLM_ROUTING.md for routing rules
LLM_INVOKE="$SCRIPT_DIR/llm-invoke.sh"
if [ -f "$LLM_INVOKE" ]; then
  REPORT_CONTENT=$(cat "$REPORT_FILE")
  ANALYSIS=$("$LLM_INVOKE" analyze "Analyze this report: $REPORT_CONTENT. Identify the #1 priority item that should be implemented next. Output a JSON object with two fields: 'priority_item' (a concise description) and 'branch_name' (a git-friendly branch name like 'feature/description'). Output ONLY the JSON, no other text.")
else
  ANALYSIS=$(claude -p "Analyze this report: $(cat "$REPORT_FILE"). Identify the #1 priority item that should be implemented next. Output a JSON object with two fields: 'priority_item' (a concise description) and 'branch_name' (a git-friendly branch name like 'feature/description'). Output ONLY the JSON, no other text." --dangerously-skip-permissions)
fi

# Output the JSON
echo "$ANALYSIS"
