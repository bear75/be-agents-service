#!/usr/bin/env bash
#
# Prepare huddinge-v3 FSR input with fewer vehicles and shifts so research runs
# don't use 195 vehicles / 2600+ shifts. Writes input_huddinge-v3_FIXED_trimmed.json
# so the specialist picks it up automatically.
#
# Usage:
#   ./prepare-huddinge-v3-input.sh [max_vehicles] [max_shifts_per_vehicle]
# Default: 40 vehicles, 10 shifts per vehicle (~400 shifts).
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DATA_DIR="$SERVICE_ROOT/recurring-visits/data"
DATASET="huddinge-v3"
INPUT="$DATA_DIR/$DATASET/input/input_${DATASET}_FIXED.json"
OUTPUT="$DATA_DIR/$DATASET/input/input_${DATASET}_FIXED_trimmed.json"
MAX_VEHICLES="${1:-40}"
MAX_SHIFTS="${2:-10}"

if [[ ! -f "$INPUT" ]]; then
  echo "Error: input not found: $INPUT" >&2
  echo "Generate it first from CSV (e.g. csv_to_fsr.py with --max-vehicles $MAX_VEHICLES --max-shifts-per-vehicle $MAX_SHIFTS) or copy from huddinge-package." >&2
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT")"
python3 "$SERVICE_ROOT/scripts/conversion/trim_shifts_from_input.py" \
  --input "$INPUT" \
  --max-vehicles "$MAX_VEHICLES" \
  --max-shifts-per-vehicle "$MAX_SHIFTS" \
  -o "$OUTPUT"

echo ""
echo "Done. Specialist will use: $OUTPUT"
echo "Run research with: ./scripts/compound/schedule-research-loop.sh $DATASET"
