#!/usr/bin/env bash
# Generate Attendo-style pilot report for the 24feb dataset.
# Run from repo root (caire-platform/appcaire) or with REPO_ROOT set.
#
# Prerequisites:
#   - Baseline metrics: huddinge-package/metrics/metrics_*_c87d58dd.json
#   - Optimized metrics: huddinge-package/metrics/metrics_*_fa713a0d.json
#   - Optional: trimmed FSR output for sample day + visit detail
#
# Usage:
#   ./scripts/run_generate_pilot_report_24feb.sh
#   REPO_ROOT=/path/to/appcaire ./scripts/run_generate_pilot_report_24feb.sh

set -e
REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "$0")/../../.." && pwd)}"
cd "$REPO_ROOT"
SCRIPT_DIR="docs_2.0/recurring-visits/scripts"
METRICS_DIR="docs_2.0/recurring-visits/huddinge-package/metrics"
SOLVE_DIR="docs_2.0/recurring-visits/huddinge-package/solve/24feb"

# Resolve latest metrics files by pattern (most recent timestamp)
BASELINE=$(ls -t "$METRICS_DIR"/metrics_*_c87d58dd.json 2>/dev/null | head -1)
OPTIMIZED=$(ls -t "$METRICS_DIR"/metrics_*_fa713a0d.json 2>/dev/null | head -1)
OUTPUT_HTML="$METRICS_DIR/Huddinge_Pilot_Report_24feb.html"
OPTIMIZED_OUTPUT=""
if [ -d "$SOLVE_DIR/trimmed" ]; then
  OPTIMIZED_OUTPUT=$(ls "$SOLVE_DIR/trimmed"/export-field-service-routing-fa713a0d-*-output.json 2>/dev/null | head -1)
fi

if [ -z "$BASELINE" ] || [ ! -f "$BASELINE" ]; then
  echo "Error: baseline metrics not found. Expected: $METRICS_DIR/metrics_*_c87d58dd.json"
  exit 1
fi
if [ -z "$OPTIMIZED" ] || [ ! -f "$OPTIMIZED" ]; then
  echo "Error: optimized metrics not found. Expected: $METRICS_DIR/metrics_*_fa713a0d.json"
  exit 1
fi

# Optional: FSR input for map of all locations
SOLVE_INPUT_DIR="docs_2.0/recurring-visits/huddinge-package/solve"
FSR_INPUT=""
if [ -d "$SOLVE_INPUT_DIR" ]; then
  FSR_INPUT=$(ls -t "$SOLVE_INPUT_DIR"/input_*.json 2>/dev/null | head -1)
fi

ARGS=(
  --baseline-metrics "$BASELINE"
  --optimized-metrics "$OPTIMIZED"
  --output "$OUTPUT_HTML"
  --title "Huddinge Hemtjänst — Recurring Visits"
  --window "2-Week Window"
  --days 14
  --use-attendo-values
)
if [ -n "$OPTIMIZED_OUTPUT" ] && [ -f "$OPTIMIZED_OUTPUT" ]; then
  ARGS+=(--optimized-output "$OPTIMIZED_OUTPUT")
fi
if [ -n "$FSR_INPUT" ] && [ -f "$FSR_INPUT" ]; then
  ARGS+=(--fsr-input "$FSR_INPUT")
fi

python3 "$SCRIPT_DIR/generate_pilot_report.py" "${ARGS[@]}"
echo "Open: $OUTPUT_HTML"
echo ""
echo "To get PDF (map + calendar):"
echo "  $SCRIPT_DIR/html_to_pdf.sh"
echo "  or: open the HTML in Chrome/Safari, wait for map to load, then Print → Save as PDF"
