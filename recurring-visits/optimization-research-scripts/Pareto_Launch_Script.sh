#!/bin/bash
#
# Pareto Frontier Research Launch Script
# Execute systematic efficiency-continuity mapping based on proven methodology
#

set -e

echo "🎯 LAUNCHING PARETO FRONTIER RESEARCH SYSTEM"
echo "============================================="

# Configuration from the plan
export TIMEFOLD_API_KEY="tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8"
CONFIG_ID="a43d4eec-9f53-40b3-82ad-f135adc8c7e3"
BASE_INPUT="solve/input_20260224_202857.json"
SEED_OUTPUT="solve/iter1/391486da-output.json"
WORKING_DIR="docs_2.0/recurring-visits/huddinge-package"
SCRIPTS_DIR="../scripts"

# Pareto sweep N-values (N=4 minimum as requested, no manual/area approaches)
N_VALUES=(4 5 6 7 8 10 12 15 20)

echo "📊 RESEARCH PARAMETERS:"
echo "   N-values: ${N_VALUES[@]}"
echo "   Pool method: first-run (from 391486da output)"
echo "   Config: $CONFIG_ID (short, max-assigned)"
echo "   Sweet spot target: ≥77% efficiency, ≤10 continuity"
echo ""

# Change to working directory
cd "$HOME/HomeCare/caire-platform/appcaire/$WORKING_DIR"

# Verify prerequisites
echo "🔧 Checking prerequisites..."
if [ ! -f "$BASE_INPUT" ]; then
    echo "❌ Base input not found: $BASE_INPUT"
    exit 1
fi

if [ ! -f "$SEED_OUTPUT" ]; then
    echo "❌ Seed output not found: $SEED_OUTPUT"
    echo "   Run: fetch_timefold_solution.py 391486da-ca6f-4928-a928-056a589842e1"
    exit 1
fi

echo "✅ Prerequisites verified"

# Create research directory structure
echo "📁 Setting up research directories..."
mkdir -p solve/research/{sweep,pareto}
mkdir -p metrics/sweep

for N in "${N_VALUES[@]}"; do
    mkdir -p "solve/research/sweep/N${N}"
    mkdir -p "metrics/sweep/N${N}"
done

echo "✅ Directory structure created"

# Phase 1: Prepare all inputs with first-run pools
echo "🔧 Phase 1: Preparing first-run continuity pool inputs..."

for N in "${N_VALUES[@]}"; do
    echo "   Building N=${N} pool from first-run output..."
    
    python3 "$SCRIPTS_DIR/build_continuity_pools.py" \
        --source first-run \
        --input "$BASE_INPUT" \
        --output "$SEED_OUTPUT" \
        --max-per-client "${N}" \
        --out "solve/research/sweep/N${N}/pools.json" \
        --patch-fsr-input "$BASE_INPUT" \
        --patched-input "solve/research/sweep/N${N}/input.json"
    
    if [ $? -eq 0 ]; then
        echo "   ✅ N=${N} input prepared"
    else
        echo "   ❌ N=${N} input failed"
    fi
done

echo "✅ Phase 1 complete"

# Phase 2: Submit sweep jobs in parallel (max 4 concurrent)
echo "⚡ Phase 2: Submitting parallel sweep jobs..."

PIDS=()
JOB_COUNT=0

for N in "${N_VALUES[@]}"; do
    echo "   Submitting N=${N} to Timefold..."
    
    # Submit in background
    (
        python3 "$SCRIPTS_DIR/submit_to_timefold.py" \
            solve "solve/research/sweep/N${N}/input.json" \
            --configuration-id "$CONFIG_ID" \
            --wait \
            --save "solve/research/sweep/N${N}/plan_id.txt"
        
        if [ $? -eq 0 ]; then
            echo "   ✅ N=${N} completed"
        else
            echo "   ❌ N=${N} failed"
        fi
    ) &
    
    PIDS+=($!)
    JOB_COUNT=$((JOB_COUNT + 1))
    
    # Limit concurrent jobs
    if [ $JOB_COUNT -ge 4 ]; then
        echo "   Waiting for batch to complete..."
        wait "${PIDS[@]}"
        PIDS=()
        JOB_COUNT=0
    fi
done

# Wait for remaining jobs
if [ ${#PIDS[@]} -gt 0 ]; then
    echo "   Waiting for final batch..."
    wait "${PIDS[@]}"
fi

echo "✅ Phase 2 complete"

# Phase 3: Fetch outputs and run analysis
echo "📊 Phase 3: Fetching outputs and analyzing results..."

for N in "${N_VALUES[@]}"; do
    if [ -f "solve/research/sweep/N${N}/plan_id.txt" ]; then
        PLAN_ID=$(cat "solve/research/sweep/N${N}/plan_id.txt")
        echo "   Fetching N=${N} output (${PLAN_ID})..."
        
        python3 "$SCRIPTS_DIR/fetch_timefold_solution.py" \
            "$PLAN_ID" \
            --save "solve/research/sweep/N${N}/output.json" \
            --input "solve/research/sweep/N${N}/input.json" \
            --metrics-dir "metrics/sweep/N${N}"
        
        # Run continuity analysis
        python3 "$SCRIPTS_DIR/continuity_report.py" \
            "solve/research/sweep/N${N}/input.json" \
            "solve/research/sweep/N${N}/output.json" \
            --out "metrics/sweep/N${N}/continuity.csv"
        
        # Extract metrics (exclude idle as requested)
        python3 "$SCRIPTS_DIR/metrics.py" \
            "solve/research/sweep/N${N}/output.json" \
            --exclude-inactive > "metrics/sweep/N${N}/metrics.txt"
        
        echo "   ✅ N=${N} analysis complete"
    else
        echo "   ❌ N=${N} plan ID not found"
    fi
done

echo "✅ Phase 3 complete"

# Phase 4: Generate Pareto frontier report
echo "📈 Phase 4: Generating Pareto frontier report..."

# Build summary table
REPORT_FILE="solve/research/pareto-frontier-$(date +%Y-%m-%d).md"

cat > "$REPORT_FILE" << EOF
# Efficiency-Continuity Pareto Frontier — Huddinge 2-Week — $(date +%Y-%m-%d)

## Executive Summary

**Research Goal**: Map the efficiency-continuity trade-off curve to identify optimal configurations.
**Method**: First-run pool sweep from base 391486da output  
**Sweet Spot Criteria**: Efficiency ≥ 77%, Continuity ≤ 10 caregivers average

## Key Numbers

| Strategy | Pool | Eff (excl idle) | Avg Unique/Client | Unassigned | Plan ID |
|----------|------|-----------------|-------------------|------------|---------|
| Manual (client today) | — | 67.8% | 2.9 | 0 | — |
EOF

# Extract results from each N-value
for N in "${N_VALUES[@]}"; do
    if [ -f "solve/research/sweep/N${N}/output.json" ]; then
        # Extract metrics (simplified for script)
        PLAN_ID=$(cat "solve/research/sweep/N${N}/plan_id.txt" 2>/dev/null || echo "unknown")
        echo "| Sweep N=${N} | ${N} | ?% | ? | ? | ${PLAN_ID:0:8}... |" >> "$REPORT_FILE"
    fi
done

cat >> "$REPORT_FILE" << EOF
| Unconstrained (base) | ∞ | 85.7% | 19.3 | ~114 | 391486da... |

## Next Steps

1. **Analyze metrics**: Extract exact efficiency/continuity from metrics files
2. **Identify sweet spots**: Find N-values achieving ≥77% eff, ≤10 cont  
3. **Business case**: Calculate ROI for top 3 configurations
4. **Client presentation**: Present optimal trade-off options

## Technical Notes

- Pool method: First-run from base 391486da output
- Configuration: $CONFIG_ID
- Analysis: Efficiency excludes idle time, continuity per client
- Generated: $(date +'%Y-%m-%d %H:%M:%S')
EOF

echo "📈 Pareto frontier report generated: $REPORT_FILE"

# Summary
echo ""
echo "🏆 PARETO FRONTIER RESEARCH COMPLETE!"
echo "================================================="
echo ""
echo "📊 RESULTS SUMMARY:"
echo "   • N-values tested: ${N_VALUES[@]}"
echo "   • Method: First-run pool sweep (proven methodology)"
echo "   • Analysis: Efficiency with idle removed (as requested)"
echo "   • Target: Sweet spot with ≥77% efficiency, ≤10 continuity"
echo ""
echo "📁 OUTPUT FILES:"
echo "   • Main report: $REPORT_FILE"
echo "   • Individual results: solve/research/sweep/N*/output.json"
echo "   • Metrics: metrics/sweep/N*/"
echo ""
echo "🎯 NEXT STEPS:"
echo "   1. Review metrics to identify optimal N-value"
echo "   2. Update Huddinge strategic presentation"
echo "   3. Generate business case for top configurations"
echo ""
echo "🚀 Ready to revolutionize home care optimization!"