#!/usr/bin/env bash
#
# Complete reseed and solve workflow for FSR (standalone, no dashboard DB)
#
# This script:
# 1. Converts CSV to FSR JSON
# 2. Adds 7 extra evening shifts
# 3. Submits to Timefold
# 4. Analyzes results
#
# Usage:
#   ./reseed-and-solve-fsr.sh <csv-path> [options]
#
# Options:
#   --add-shifts <count>    Add N extra evening shifts (default: 7)
#   --start-date <date>     Planning start date (YYYY-MM-DD, default: 2026-03-02)
#   --end-date <date>       Planning end date (YYYY-MM-DD, default: 2026-03-15)
#   --no-geocode           Skip geocoding
#   --wait                 Wait for solve to complete
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SCRIPTS_DIR="$SERVICE_ROOT/scripts"
DATA_DIR="$SERVICE_ROOT/recurring-visits/data/huddinge-v3"

CSV_PATH=""
ADD_SHIFTS=7
START_DATE="2026-03-02"
END_DATE="2026-03-15"
NO_GEOCODE=false
WAIT=false

# Parse arguments
if [[ $# -eq 0 ]]; then
  echo "Usage: $0 <csv-path> [options]"
  echo ""
  echo "Options:"
  echo "  --add-shifts <count>    Add N extra evening shifts (default: 7)"
  echo "  --start-date <date>     Planning start date (YYYY-MM-DD)"
  echo "  --end-date <date>       Planning end date (YYYY-MM-DD)"
  echo "  --no-geocode           Skip geocoding"
  echo "  --wait                 Wait for solve to complete"
  exit 1
fi

CSV_PATH="$1"
shift

while [[ $# -gt 0 ]]; do
  case $1 in
    --add-shifts)
      ADD_SHIFTS="$2"
      shift 2
      ;;
    --start-date)
      START_DATE="$2"
      shift 2
      ;;
    --end-date)
      END_DATE="$2"
      shift 2
      ;;
    --no-geocode)
      NO_GEOCODE=true
      shift
      ;;
    --wait)
      WAIT=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if [[ ! -f "$CSV_PATH" ]]; then
  echo "Error: CSV file not found: $CSV_PATH" >&2
  exit 1
fi

echo "🔄 FSR Reseed and Solve Workflow (Standalone)"
echo "=============================================="
echo ""
echo "CSV: $CSV_PATH"
echo "Planning window: $START_DATE to $END_DATE"
echo "Extra evening shifts: $ADD_SHIFTS"
echo ""

# Step 1: Convert CSV to FSR JSON
echo "1️⃣  Converting CSV to FSR JSON..."
INPUT_JSON="$DATA_DIR/input/input_huddinge-v3_$(date +%Y%m%d_%H%M%S).json"
mkdir -p "$(dirname "$INPUT_JSON")"

GEOCODE_FLAG=""
if [[ "$NO_GEOCODE" == "true" ]]; then
  GEOCODE_FLAG="--no-geocode"
fi

python3 "$SCRIPTS_DIR/conversion/csv_to_fsr.py" \
  "$CSV_PATH" \
  -o "$INPUT_JSON" \
  --start-date "$START_DATE" \
  --end-date "$END_DATE" \
  $GEOCODE_FLAG

if [[ $? -ne 0 ]]; then
  echo "   ❌ CSV conversion failed"
  exit 1
fi

echo "   ✅ Created: $INPUT_JSON"
echo ""

# Step 2: Add evening shifts
if [[ $ADD_SHIFTS -gt 0 ]]; then
  echo "2️⃣  Adding $ADD_SHIFTS extra evening shifts..."
  OUTPUT_JSON="${INPUT_JSON%.json}_with_shifts.json"

  python3 "$SCRIPTS_DIR/conversion/add_evening_shifts_to_fsr.py" \
    "$INPUT_JSON" \
    -o "$OUTPUT_JSON" \
    --count "$ADD_SHIFTS" \
    --start-date "$START_DATE" \
    --end-date "$END_DATE"

  if [[ $? -ne 0 ]]; then
    echo "   ❌ Failed to add shifts"
    exit 1
  fi

  echo "   ✅ Created: $OUTPUT_JSON"
  INPUT_JSON="$OUTPUT_JSON"
  echo ""
fi

# Step 3: Submit to Timefold
echo "3️⃣  Submitting to Timefold..."
WAIT_FLAG=""
if [[ "$WAIT" == "true" ]]; then
  WAIT_FLAG="--wait"
fi

ROUTE_PLAN_ID=$(python3 "$SCRIPTS_DIR/timefold/submit.py" solve "$INPUT_JSON" $WAIT_FLAG --save "${INPUT_JSON%.json}_output.json" 2>&1 | grep -oP 'routePlanId[":\s]+\K[^"]+' | head -1)

if [[ -z "$ROUTE_PLAN_ID" ]]; then
  echo "   ⚠️  Could not extract route plan ID (solve may still be running)"
  echo "   Check Timefold dashboard or logs for route plan ID"
else
  echo "   ✅ Route plan ID: $ROUTE_PLAN_ID"
fi

echo ""

# Step 4: Instructions
echo "4️⃣  Next Steps"
echo "=============="
echo ""
echo "✅ FSR JSON created: $INPUT_JSON"
if [[ -n "$ROUTE_PLAN_ID" ]]; then
  echo "✅ Solve submitted: $ROUTE_PLAN_ID"
fi
echo ""
echo "📋 To complete the workflow:"
echo ""
if [[ -z "$ROUTE_PLAN_ID" ]] || [[ "$WAIT" != "true" ]]; then
  echo "1. Wait for solve to complete (check Timefold dashboard)"
  echo "2. Fetch solution:"
  echo "   python3 $SCRIPTS_DIR/timefold/fetch.py $ROUTE_PLAN_ID -o solution.json"
  echo ""
fi
echo "3. Analyze results:"
echo "   python3 $SCRIPTS_DIR/analytics/analyze_supply_demand.py solution.json $INPUT_JSON"
echo "   python3 $SCRIPTS_DIR/analytics/metrics.py solution.json"
echo "   python3 $SCRIPTS_DIR/continuity/report.py solution.json"
echo ""
echo "✨ Workflow complete!"
echo ""
