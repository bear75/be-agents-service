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

# Extract the priority item from the report
# This uses Claude Code to analyze the report and pick the top priority
ANALYSIS=$(claude -p "Analyze this report: $(cat "$REPORT_FILE"). Identify the #1 priority item that should be implemented next. Output a JSON object with two fields: 'priority_item' (a concise description) and 'branch_name' (a git-friendly branch name like 'feature/description'). Output ONLY the JSON, no other text." --dangerously-skip-permissions)

# Output the JSON
echo "$ANALYSIS"
