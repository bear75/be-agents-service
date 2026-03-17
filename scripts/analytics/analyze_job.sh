#!/bin/bash
#
# Fetch a Timefold route plan (job) and run full analytics, OR run analytics on an existing output file:
#   - Metrics without idle (--visit-span-only): field efficiency = visit/(visit+travel)
#   - Continuity report (per-client distinct caregivers; avg and max)
#   - Empty-shifts analysis (overlap with unassigned visit time windows)
#
# Usage (fetch by plan ID):
#   ./analyze_job.sh <plan_id> --input <path/to/input.json> [--out-dir DIR]
#
# Usage (existing output file — no fetch; use when you already have the solution JSON):
#   ./analyze_job.sh --output <path/to/output.json> --input <path/to/input.json> [--out-dir DIR]
#
# Example (existing file, e.g. from a completed run that saved output locally):
#   ./analyze_job.sh --output recurring-visits/data/huddinge-v3/research_output/exp_xxx/output.json --input recurring-visits/data/huddinge-v3/input/input_huddinge-v3_FIXED.json
#
# Requires: Python 3, jq. For fetch: TIMEFOLD_API_KEY, submit_to_timefold.py.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SCRIPTS_TIMEFOLD="${SCRIPTS_TIMEFOLD:-$SERVICE_ROOT/recurring-visits/scripts}"
CONTINUITY_DIR="$SERVICE_ROOT/scripts/continuity"

USE_EXISTING_OUTPUT=false
OUTPUT_JSON_ARG=""
PLAN_ID="${1:-}"
INPUT_JSON=""
OUT_DIR=""

if [[ "${1:-}" == "--output" ]]; then
  USE_EXISTING_OUTPUT=true
  OUTPUT_JSON_ARG="${2:-}"
  shift 2
  if [[ -z "$OUTPUT_JSON_ARG" || ! -f "$OUTPUT_JSON_ARG" ]]; then
    echo "Error: --output <path> must point to an existing solution JSON." >&2
    exit 1
  fi
fi

if [[ "$USE_EXISTING_OUTPUT" != "true" && ( -z "$PLAN_ID" || "$PLAN_ID" == --* ) ]]; then
  echo "Usage: $0 <plan_id> --input <input.json> [--out-dir DIR]" >&2
  echo "   OR: $0 --output <output.json> --input <input.json> [--out-dir DIR]" >&2
  echo "  plan_id   - Timefold route plan UUID" >&2
  echo "  --output  - Use existing solution JSON (no fetch)" >&2
  echo "  --input   - FSR input JSON (required)" >&2
  echo "  --out-dir - Where to save reports (default: ./analyze_<id>)" >&2
  exit 1
fi
[[ "$USE_EXISTING_OUTPUT" != "true" ]] && shift

while [[ $# -gt 0 ]]; do
  case "$1" in
    --input)   INPUT_JSON="$2"; shift 2 ;;
    --out-dir) OUT_DIR="$2";   shift 2 ;;
    *)         echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$INPUT_JSON" || ! -f "$INPUT_JSON" ]]; then
  echo "Error: --input <path> to existing input JSON is required." >&2
  exit 1
fi

if [[ "$USE_EXISTING_OUTPUT" == "true" ]]; then
  OUTPUT_JSON="$(cd "$(dirname "$OUTPUT_JSON_ARG")" && pwd)/$(basename "$OUTPUT_JSON_ARG")"
  SHORT_ID="$(basename "$(dirname "$OUTPUT_JSON")" | head -c 8)"
  OUT_DIR="${OUT_DIR:-$SCRIPT_DIR/analyze_$(basename "$OUTPUT_JSON" .json)}"
else
  SHORT_ID="${PLAN_ID:0:8}"
  OUT_DIR="${OUT_DIR:-$SCRIPT_DIR/analyze_$SHORT_ID}"
  mkdir -p "$OUT_DIR"
  OUT_DIR="$(cd "$OUT_DIR" && pwd)"
  OUTPUT_JSON="$OUT_DIR/output.json"

  # 1) Fetch current state/output
  echo "[1/4] Fetching route plan $PLAN_ID..."
  if [[ -z "${TIMEFOLD_API_KEY:-}" && -f "$HOME/.config/caire/env" ]]; then
    source "$HOME/.config/caire/env"
  fi
  if [[ -z "${TIMEFOLD_API_KEY:-}" ]]; then
    echo "Error: TIMEFOLD_API_KEY not set." >&2
    exit 1
  fi
  cd "$SCRIPTS_TIMEFOLD"
  if ! python3 submit_to_timefold.py fetch "$PLAN_ID" --save "$OUTPUT_JSON" 2>"$OUT_DIR/fetch.log"; then
    echo "Fetch failed (see $OUT_DIR/fetch.log). Use --output <path> if you have the solution JSON locally." >&2
    exit 1
  fi
  # Check if we have modelOutput (full solution)
  if ! jq -e '.modelOutput.vehicles // .modelOutput' "$OUTPUT_JSON" >/dev/null 2>&1; then
    STATUS=$(jq -r '.metadata.solverStatus // .run.solverStatus // "UNKNOWN"' "$OUTPUT_JSON" 2>/dev/null || echo "?")
    echo "Job not yet solved (status: $STATUS). Re-run when SOLVED or use --output <path> with saved solution." >&2
    exit 0
  fi
fi

mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"
[[ "$USE_EXISTING_OUTPUT" == "true" ]] && echo "[1/4] Using existing output: $OUTPUT_JSON"

# 2a) Metrics without idle (visit-span-only: field efficiency = visit/(visit+travel))
echo "[2/4] Running metrics (visit-span-only + full shifts for dashboard)..."
python3 "$SERVICE_ROOT/scripts/analytics/metrics.py" "$OUTPUT_JSON" --input "$INPUT_JSON" \
  --visit-span-only --save "$OUT_DIR" 2>>"$OUT_DIR/metrics.log" || true
# 2b) Full-shift metrics (all provisioned time) for dashboard "Effektivitet" and "Total arbetstid"
python3 "$SERVICE_ROOT/scripts/analytics/metrics.py" "$OUTPUT_JSON" --input "$INPUT_JSON" \
  --save "$OUT_DIR" 2>>"$OUT_DIR/metrics.log" || true
METRICS_JSON=""
METRICS_FULL_JSON=""
for f in "$OUT_DIR"/metrics_*.json; do
  [[ -f "$f" ]] || continue
  if jq -e '.visit_span_only == true' "$f" >/dev/null 2>&1; then
    METRICS_JSON="$f"
  elif jq -e '.visit_span_only != true' "$f" >/dev/null 2>&1; then
    METRICS_FULL_JSON="$f"
  fi
done
[[ -z "$METRICS_JSON" ]] && METRICS_JSON=$(find "$OUT_DIR" -maxdepth 1 -name 'metrics_*.json' -type f | head -1)
if [[ -n "$METRICS_JSON" ]]; then
  echo "  Metrics (visit-span): $METRICS_JSON"
  echo "  field_efficiency_pct (Reseffektivitet): $(jq -r '.field_efficiency_pct // "N/A"' "$METRICS_JSON")%"
  echo "  unassigned_visits: $(jq -r '.unassigned_visits // "N/A"' "$METRICS_JSON")"
fi

# 3) Continuity (per-client distinct caregivers)
echo "[3/4] Running continuity report..."
CONTINUITY_CSV="$OUT_DIR/continuity.csv"
python3 "$CONTINUITY_DIR/report.py" --input "$INPUT_JSON" --output "$OUTPUT_JSON" --report "$CONTINUITY_CSV" --no-cci 2>>"$OUT_DIR/continuity.log" | tee "$OUT_DIR/continuity_summary.txt" || true
if [[ -f "$CONTINUITY_CSV" ]]; then
  # continuity = column 3 (0-indexed 2); skip header
  AVG=$(awk -F',' 'NR>1 {s+=$3; n++} END {printf "%.2f", (n>0 ? s/n : 0)}' "$CONTINUITY_CSV")
  MAX=$(awk -F',' 'NR>1 {if($3>m) m=$3} END {print (m=="" ? "0" : m)}' "$CONTINUITY_CSV")
  echo "  continuity_avg: $AVG  continuity_max: $MAX"
fi

# 4) Empty-shifts analysis
echo "[4/4] Running empty-shifts analysis..."
python3 "$SERVICE_ROOT/scripts/analytics/analyze_empty_shifts.py" "$INPUT_JSON" "$OUTPUT_JSON" 2>>"$OUT_DIR/empty_shifts.log" | tee "$OUT_DIR/empty_shifts.txt" || true

echo "Done. Outputs in $OUT_DIR"
