#!/bin/bash
# Launch v3 Continuity Optimization Campaign
# Generates and submits multiple variants in parallel

set -e

BASE_DIR="/Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits"
V3_DIR="huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3"
ROUTE_PLAN_ID="4cdfce61-0d2d-46e0-9c16-674a7b9dab0f"

cd "$BASE_DIR"

echo "=========================================="
echo "v3 CONTINUITY CAMPAIGN LAUNCHER"
echo "=========================================="
echo ""

# Check if v3_FIXED output exists
if [ ! -f "$V3_DIR/output_FIXED/4cdfce61_output.json" ]; then
    echo "⏳ v3_FIXED not complete yet, fetching current state..."
    python3 scripts/fetch_timefold_solution.py "$ROUTE_PLAN_ID" \
        --save "$V3_DIR/output_FIXED/4cdfce61_output.json" || {
        echo "❌ v3_FIXED still solving or fetch failed"
        echo "Current solve status:"
        python3 scripts/fetch_timefold_solution.py "$ROUTE_PLAN_ID" 2>&1 | head -10
        exit 1
    }
fi

echo "✅ v3_FIXED output available"
echo ""

# Create directories
mkdir -p "$V3_DIR/continuity/pools"
mkdir -p "$V3_DIR/continuity/variants/pool3"
mkdir -p "$V3_DIR/continuity/variants/pool5"
mkdir -p "$V3_DIR/continuity/variants/pool8"
mkdir -p "$V3_DIR/continuity/results"
mkdir -p "$V3_DIR/continuity/logs"

# Step 1: Analyze baseline continuity
echo "=========================================="
echo "STEP 1: Baseline Continuity Analysis"
echo "=========================================="
python3 scripts/continuity_report.py \
    --input "$V3_DIR/input_v3_FIXED.json" \
    --output "$V3_DIR/output_FIXED/4cdfce61_output.json" \
    --report "$V3_DIR/continuity/continuity_baseline.csv"

echo ""
echo "Baseline continuity (top 10 clients):"
head -11 "$V3_DIR/continuity/continuity_baseline.csv"
echo ""

BASELINE_AVG=$(awk -F, 'NR>1 {sum+=$3; count++} END {printf "%.2f", sum/count}' "$V3_DIR/continuity/continuity_baseline.csv")
echo "Baseline average: $BASELINE_AVG employees/client"
echo ""

# Step 2: Build continuity pools
echo "=========================================="
echo "STEP 2: Build Continuity Pools"
echo "=========================================="

echo "Building pool size 3..."
python3 scripts/build_continuity_pools.py \
    --source first-run \
    --input "$V3_DIR/input_v3_FIXED.json" \
    --output "$V3_DIR/output_FIXED/4cdfce61_output.json" \
    --max-per-client 3 \
    --out "$V3_DIR/continuity/pools/pool3.json"

echo "Building pool size 5..."
python3 scripts/build_continuity_pools.py \
    --source first-run \
    --input "$V3_DIR/input_v3_FIXED.json" \
    --output "$V3_DIR/output_FIXED/4cdfce61_output.json" \
    --max-per-client 5 \
    --out "$V3_DIR/continuity/pools/pool5.json"

echo "Building pool size 8..."
python3 scripts/build_continuity_pools.py \
    --source first-run \
    --input "$V3_DIR/input_v3_FIXED.json" \
    --output "$V3_DIR/output_FIXED/4cdfce61_output.json" \
    --max-per-client 8 \
    --out "$V3_DIR/continuity/pools/pool8.json"

echo "✅ Continuity pools created"
echo ""

# Step 3: Generate variant inputs
echo "=========================================="
echo "STEP 3: Generate Variant Inputs"
echo "=========================================="

# Function to create variant input with pool and strategy
create_variant() {
    local POOL_SIZE=$1
    local POOL_FILE="$V3_DIR/continuity/pools/pool${POOL_SIZE}.json"
    local OUTPUT_DIR="$V3_DIR/continuity/variants/pool${POOL_SIZE}"

    echo "Generating variants for pool size ${POOL_SIZE}..."
    python3 scripts/prepare_continuity_test_variants.py \
        --base-input "$V3_DIR/input_v3_FIXED.json" \
        --pool-file "$POOL_FILE" \
        --output-dir "$OUTPUT_DIR" 2>&1 | grep -v "^$" | head -20
}

# Generate for each pool size
create_variant 3
create_variant 5
create_variant 8

echo "✅ All variant inputs generated"
echo ""

# Step 4: Submit variants in parallel
echo "=========================================="
echo "STEP 4: Submit Variants (Parallel)"
echo "=========================================="

# Create submission manifest
MANIFEST="$V3_DIR/continuity/campaign_manifest.md"
echo "# v3 Campaign Submissions" > "$MANIFEST"
echo "" >> "$MANIFEST"
echo "**Started**: $(date '+%Y-%m-%d %H:%M:%S')" >> "$MANIFEST"
echo "**Baseline**: $ROUTE_PLAN_ID (avg continuity: $BASELINE_AVG)" >> "$MANIFEST"
echo "" >> "$MANIFEST"
echo "| Variant | Route Plan ID | Status | Log |" >> "$MANIFEST"
echo "|---------|---------------|--------|-----|" >> "$MANIFEST"

# Function to submit variant
submit_variant() {
    local VARIANT_NAME=$1
    local INPUT_FILE=$2
    local LOG_FILE="$V3_DIR/continuity/logs/${VARIANT_NAME}.log"

    echo "Submitting $VARIANT_NAME..."

    # Submit in background
    python3 scripts/submit_to_timefold.py solve \
        "$INPUT_FILE" \
        --configuration-id "" \
        --wait \
        --save "$V3_DIR/continuity/results/${VARIANT_NAME}" \
        > "$LOG_FILE" 2>&1 &

    local PID=$!
    echo "  → Background PID: $PID"

    # Save PID to manifest
    echo "| $VARIANT_NAME | _solving_ | 🔄 Running (PID: $PID) | [log](logs/${VARIANT_NAME}.log) |" >> "$MANIFEST"

    # Return PID for tracking
    echo "$PID"
}

# Track all PIDs
PIDS=()

# Track A: Pool size variants (pool3, pool5, pool8 with preferred_2)
if [ -f "$V3_DIR/continuity/variants/pool3/input_preferred_vehicles_weight2.json" ]; then
    PID=$(submit_variant "pool3_preferred2" "$V3_DIR/continuity/variants/pool3/input_preferred_vehicles_weight2.json")
    PIDS+=($PID)
fi

if [ -f "$V3_DIR/continuity/variants/pool5/input_preferred_vehicles_weight2.json" ]; then
    PID=$(submit_variant "pool5_preferred2" "$V3_DIR/continuity/variants/pool5/input_preferred_vehicles_weight2.json")
    PIDS+=($PID)
fi

if [ -f "$V3_DIR/continuity/variants/pool8/input_preferred_vehicles_weight2.json" ]; then
    PID=$(submit_variant "pool8_preferred2" "$V3_DIR/continuity/variants/pool8/input_preferred_vehicles_weight2.json")
    PIDS+=($PID)
fi

# Track B: Weight variants (pool5 with different weights)
if [ -f "$V3_DIR/continuity/variants/pool5/input_preferred_vehicles_weight10.json" ]; then
    PID=$(submit_variant "pool5_preferred10" "$V3_DIR/continuity/variants/pool5/input_preferred_vehicles_weight10.json")
    PIDS+=($PID)
fi

if [ -f "$V3_DIR/continuity/variants/pool5/input_preferred_vehicles_weight20.json" ]; then
    PID=$(submit_variant "pool5_preferred20" "$V3_DIR/continuity/variants/pool5/input_preferred_vehicles_weight20.json")
    PIDS+=($PID)
fi

if [ -f "$V3_DIR/continuity/variants/pool5/input_pool5.json" ]; then
    PID=$(submit_variant "pool5_required" "$V3_DIR/continuity/variants/pool5/input_pool5.json")
    PIDS+=($PID)
fi

# Track C: Combo strategies (pool5)
if [ -f "$V3_DIR/continuity/variants/pool5/input_combo_preferred_and_wait_min.json" ]; then
    PID=$(submit_variant "pool5_combo" "$V3_DIR/continuity/variants/pool5/input_combo_preferred_and_wait_min.json")
    PIDS+=($PID)
fi

if [ -f "$V3_DIR/continuity/variants/pool5/input_wait_min_weight3.json" ]; then
    PID=$(submit_variant "pool5_wait_min" "$V3_DIR/continuity/variants/pool5/input_wait_min_weight3.json")
    PIDS+=($PID)
fi

# Track D: Aggressive continuity (pool3)
if [ -f "$V3_DIR/continuity/variants/pool3/input_preferred_vehicles_weight10.json" ]; then
    PID=$(submit_variant "pool3_preferred10" "$V3_DIR/continuity/variants/pool3/input_preferred_vehicles_weight10.json")
    PIDS+=($PID)
fi

if [ -f "$V3_DIR/continuity/variants/pool3/input_pool3.json" ]; then
    PID=$(submit_variant "pool3_required" "$V3_DIR/continuity/variants/pool3/input_pool3.json")
    PIDS+=($PID)
fi

echo ""
echo "=========================================="
echo "CAMPAIGN STATUS"
echo "=========================================="
echo ""
echo "✅ ${#PIDS[@]} variants submitted in parallel"
echo ""
echo "Manifest: $V3_DIR/continuity/campaign_manifest.md"
echo "Logs: $V3_DIR/continuity/logs/"
echo ""
echo "Monitor progress:"
echo "  tail -f $V3_DIR/continuity/logs/*.log"
echo ""
echo "Check status:"
echo "  ps aux | grep submit_to_timefold"
echo ""
echo "Estimated completion: $(date -v+30M '+%H:%M:%S')"
echo ""
echo "=========================================="
