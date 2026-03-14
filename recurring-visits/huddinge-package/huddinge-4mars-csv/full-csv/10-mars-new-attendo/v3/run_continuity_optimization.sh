#!/bin/bash
# Continuity Optimization Workflow
# Run this after v3_FIXED completes (~18:00)

set -e

BASE_DIR="/Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits"
V3_DIR="huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3"

cd "$BASE_DIR"

echo "=== Step 1: Check v3_FIXED completed ==="
if [ ! -f "$V3_DIR/output_FIXED/4cdfce61_output.json" ]; then
    echo "ERROR: v3_FIXED output not found. Wait for solve to complete."
    exit 1
fi
echo "✅ v3_FIXED output found"

echo ""
echo "=== Step 2: Analyze baseline continuity ==="
python3 scripts/continuity_report.py \
  --input "$V3_DIR/input_v3_FIXED.json" \
  --output "$V3_DIR/output_FIXED/4cdfce61_output.json" \
  --report "$V3_DIR/continuity_baseline.csv"

echo ""
echo "Baseline continuity (top 20 clients):"
head -21 "$V3_DIR/continuity_baseline.csv"

echo ""
echo "=== Step 3 & 4: Build continuity pools and patch input ==="
python3 scripts/build_continuity_pools.py \
  --source first-run \
  --input "$V3_DIR/input_v3_FIXED.json" \
  --output "$V3_DIR/output_FIXED/4cdfce61_output.json" \
  --out "$V3_DIR/continuity_pools.json" \
  --max-per-client 3 \
  --patch-fsr-input "$V3_DIR/input_v3_FIXED.json" \
  --patched-input "$V3_DIR/input_v3_CONTINUITY_v2.json"

echo ""
echo "✅ Created input_v3_CONTINUITY_v2.json with requiredVehicles constraints"

echo ""
echo "=== Step 5: Submit continuity-optimized solve ==="
python3 scripts/submit_to_timefold.py solve \
  "$V3_DIR/input_v3_CONTINUITY_v2.json" \
  --configuration-id "" \
  --wait \
  --save "$V3_DIR/output_CONTINUITY_v2" \
  > /tmp/timefold_submit_v3_continuity_v2.log 2>&1 &

CONTINUITY_PID=$!
echo "✅ Submitted v3_CONTINUITY_v2 (PID: $CONTINUITY_PID)"
echo "Monitor: tail -f /tmp/timefold_submit_v3_continuity_v2.log"

echo ""
echo "=== Waiting for continuity solve to complete ==="
echo "This will take ~30 minutes. Monitor progress with:"
echo "  tail -f /tmp/timefold_submit_v3_continuity_v2.log"

wait $CONTINUITY_PID

echo ""
echo "=== Step 6: Analyze improved continuity ==="
CONTINUITY_OUTPUT=$(ls "$V3_DIR/output_CONTINUITY_v2/"*_output.json 2>/dev/null | head -1)

if [ -z "$CONTINUITY_OUTPUT" ]; then
    echo "ERROR: Continuity output not found"
    exit 1
fi

python3 scripts/continuity_report.py \
  --input "$V3_DIR/input_v3_CONTINUITY_v2.json" \
  --output "$CONTINUITY_OUTPUT" \
  --report "$V3_DIR/continuity_improved.csv"

echo ""
echo "=== RESULTS COMPARISON ==="
echo ""
echo "Baseline (unconstrained):"
head -21 "$V3_DIR/continuity_baseline.csv"

echo ""
echo "Improved (with requiredVehicles):"
head -21 "$V3_DIR/continuity_improved.csv"

echo ""
echo "Average continuity:"
echo -n "Baseline: "
awk -F, 'NR>1 {sum+=$3; count++} END {printf "%.2f employees/client\n", sum/count}' "$V3_DIR/continuity_baseline.csv"
echo -n "Improved: "
awk -F, 'NR>1 {sum+=$3; count++} END {printf "%.2f employees/client\n", sum/count}' "$V3_DIR/continuity_improved.csv"

echo ""
echo "✅ CONTINUITY OPTIMIZATION COMPLETE"
