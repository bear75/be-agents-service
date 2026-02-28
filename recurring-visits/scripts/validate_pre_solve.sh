#!/bin/bash
# Pre-solve validation: run all input correctness checks.
# See docs/PRIORITIES.md Priority 1.
set -e
PKG="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PKG"
echo "=== Validate source CSV (visitGroup weekday overlap) ==="
python3 scripts/validate_source_visit_groups.py source/Huddinge_recurring_v2.csv
echo ""
INPUT=$(ls -t solve/input_*.json 2>/dev/null | head -1)
if [ -z "$INPUT" ]; then
  echo "No solve/input_*.json found. Run process_huddinge.py first."
  exit 1
fi
echo "=== Validate input JSON (visit group time window overlap) ==="
python3 scripts/validate_visit_groups.py "$INPUT"
echo ""
echo "Pre-solve checks OK."
