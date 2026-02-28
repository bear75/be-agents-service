#!/usr/bin/env bash
# Convert the pilot report HTML to PDF so the map and calendar (timeline) are included.
# The map loads tiles from the network, so we need a real browser and a short wait before printing.
#
# Prerequisites:
#   - HTML report already generated (e.g. run run_generate_pilot_report_24feb.sh first)
#   - Chrome, Chromium, or Edge (for --headless --print-to-pdf)
#
# Usage:
#   ./scripts/html_to_pdf.sh [path/to/report.html [path/to/output.pdf]]
#   If omitted, uses huddinge-package/metrics/Huddinge_Pilot_Report_24feb.html and .pdf same name.

set -e
REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "$0")/../../.." && pwd)}"
cd "$REPO_ROOT"

METRICS_DIR="docs_2.0/recurring-visits/huddinge-package/metrics"
HTML_FILE="${1:-$METRICS_DIR/Huddinge_Pilot_Report_24feb.html}"
PDF_FILE="${2:-${HTML_FILE%.html}.pdf}"

if [ ! -f "$HTML_FILE" ]; then
  echo "Error: HTML file not found: $HTML_FILE"
  echo "Generate it first: ./docs_2.0/recurring-visits/scripts/run_generate_pilot_report_24feb.sh"
  exit 1
fi

# Absolute path for file:// URL
HTML_ABS="$(cd "$(dirname "$HTML_FILE")" && pwd)/$(basename "$HTML_FILE")"
PDF_ABS="$(cd "$(dirname "$PDF_FILE")" 2>/dev/null && pwd)/$(basename "$PDF_FILE")" || PDF_ABS="$(pwd)/$PDF_FILE"

# Prefer Chromium, then Chrome, then Edge (macOS/Linux)
CHROME=""
for cmd in chromium chromium-browser google-chrome "Google Chrome" chromium-edge msedge; do
  if command -v "$cmd" >/dev/null 2>&1; then
    CHROME="$cmd"
    break
  fi
  # macOS app path
  if [ -d "/Applications/$cmd.app" ]; then
    CHROME="/Applications/$cmd.app/Contents/MacOS/$cmd"
    break
  fi
done

if [ -z "$CHROME" ]; then
  echo "No Chrome/Chromium/Edge found. Print PDF manually:"
  echo "  1. Open $HTML_ABS in Chrome or Safari"
  echo "  2. Wait a few seconds for the map to load"
  echo "  3. File → Print → Save as PDF (or Cmd+P → Save as PDF)"
  exit 1
fi

# Give map tiles time to load before printing (milliseconds)
MAP_WAIT_MS=5000

echo "Converting to PDF (waiting ${MAP_WAIT_MS}ms for map tiles)..."
"$CHROME" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$PDF_ABS" \
  --run-all-compositor-stages-before-draw \
  --virtual-time-budget=$MAP_WAIT_MS \
  "file://$HTML_ABS" 2>/dev/null || true

if [ -f "$PDF_ABS" ]; then
  echo "Wrote $PDF_ABS"
else
  echo "Headless print failed. Print manually:"
  echo "  1. Open file://$HTML_ABS in Chrome or Safari"
  echo "  2. Wait for the map to load, then File → Print → Save as PDF"
  exit 1
fi
