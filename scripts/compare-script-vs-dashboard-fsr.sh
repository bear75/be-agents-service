#!/usr/bin/env bash
# Compare script v3 CSV→FSR output with dashboard FSR (run dump-fsr first).
# Usage: from be-agent-service root:
#   ./scripts/compare-script-vs-dashboard-fsr.sh
# Optionally pass CSV path and dashboard JSON path.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

CSV="${1:-recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/Huddinge-v3 - Data_final.csv}"
DASHBOARD_JSON="${2:-recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/dashboard_fsr_new.json}"
SCRIPT_OUT="$REPO_ROOT/recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/script_compare_output.json"

echo "=== Script v3 flow (CSV → FSR) ==="
echo "CSV: $CSV"
echo ""

# Run script with 2-week window (match script_fsr_no_extra_vehicles / facit)
python3 scripts/conversion/csv_to_fsr.py "$CSV" -o "$SCRIPT_OUT" \
  --start-date 2026-03-02 \
  --end-date 2026-03-15 \
  --no-geocode \
  --no-supplementary-vehicles 2>&1 | tail -8

echo ""
echo "=== Counts (script output) ==="
python3 -c "
import json
with open('$SCRIPT_OUT') as f:
    d = json.load(f)
v = d.get('modelInput', {}).get('visits', [])
mov = sum(1 for x in v if len(x.get('timeWindows', [])) > 1)
fix = len(v) - mov
deps = sum(len(x.get('visitDependencies', [])) for x in v)
print('  Visits:      ', len(v))
print('  Movable:     ', mov)
print('  Fixed:       ', fix)
print('  Dependencies:', deps)
"

if [[ -f "$DASHBOARD_JSON" ]]; then
  echo ""
  echo "=== Counts (dashboard FSR – from dump-fsr) ==="
  python3 -c "
import json
with open('$DASHBOARD_JSON') as f:
    d = json.load(f)
v = d.get('modelInput', {}).get('visits', [])
mov = sum(1 for x in v if len(x.get('timeWindows', [])) > 1)
fix = len(v) - mov
deps = sum(len(x.get('visitDependencies', [])) for x in v)
print('  Visits:      ', len(v))
print('  Movable:     ', mov)
print('  Fixed:       ', fix)
print('  Dependencies:', deps)
"
  echo ""
  echo "=== Delta (script − dashboard) ==="
  python3 -c "
import json
with open('$SCRIPT_OUT') as f:
    s = json.load(f)
with open('$DASHBOARD_JSON') as f:
    d = json.load(f)
sv = s.get('modelInput', {}).get('visits', [])
dv = d.get('modelInput', {}).get('visits', [])
sm = sum(1 for x in sv if len(x.get('timeWindows', [])) > 1)
dm = sum(1 for x in dv if len(x.get('timeWindows', [])) > 1)
print('  Visits:      ', len(sv) - len(dv))
print('  Movable:     ', sm - dm, '  ← dashboard should match script')
print('  Fixed:       ', (len(sv)-sm) - (len(dv)-dm))
"
else
  echo ""
  echo "Dashboard JSON not found: $DASHBOARD_JSON"
  echo "Run from beta-appcaire: yarn workspace dashboard-server dump-fsr"
  echo "Then re-run this script."
fi
