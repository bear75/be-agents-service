#!/usr/bin/env bash
# Run the standard FSR analysis bundle (validate input + metrics/unassigned/supply/continuity on a pair).
# Usage:
#   ./scripts/analysis/run_full_fsr_analysis.sh path/to/input.json path/to/output.json [out_dir]
# Example:
#   ./scripts/analysis/run_full_fsr_analysis.sh \
#     recurring-visits/huddinge-package/.../export-*-input.json \
#     recurring-visits/huddinge-package/.../export-*-output.json \
#     docs/analysis-runs/my-run

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

INPUT="${1:?usage: $0 input.json output.json [out_dir]}"
OUTPUT="${2:?usage: $0 input.json output.json [out_dir]}"
OUT_DIR="${3:-docs/analysis-runs/manual-$(date +%Y%m%d_%H%M%S)}"
mkdir -p "$OUT_DIR"

echo "=== validate (submit.py) ==="
python3 scripts/timefold/submit.py validate "$INPUT"

echo "=== dependency feasibility --all ==="
python3 scripts/verification/analyze_dependency_feasibility.py "$INPUT" --all -o "$OUT_DIR/dependency_report.json"

echo "=== verify_flex (may exit 1) ==="
set +e
python3 scripts/verification/verify_flex.py "$INPUT"
FLEX_RC=$?
set -e
echo "(verify_flex exit code: $FLEX_RC)"

echo "=== metrics ==="
python3 scripts/analytics/metrics.py "$OUTPUT" --input "$INPUT" | tee "$OUT_DIR/metrics.txt"

echo "=== analyze_unassigned ==="
python3 scripts/analytics/analyze_unassigned.py "$INPUT" "$OUTPUT" --csv "$OUT_DIR/unassigned.csv" | tee "$OUT_DIR/analyze_unassigned.txt"

echo "=== analyze_supply_demand ==="
python3 scripts/analytics/analyze_supply_demand.py "$OUTPUT" "$INPUT" --report "$OUT_DIR/supply_demand.md" | tee "$OUT_DIR/supply_demand_console.txt"

echo "=== continuity report ==="
python3 scripts/continuity/report.py --input "$INPUT" --output "$OUTPUT" --report "$OUT_DIR/continuity.csv" | tee "$OUT_DIR/continuity_console.txt"

echo "Done. Outputs under: $OUT_DIR"
