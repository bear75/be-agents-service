# FSR scripts bundle — analysis run (2026-03-20)

This folder captures outputs from `be-agent-service/scripts/` analysis tools.

## 1. Fetch from Timefold (not run here)

`scripts/timefold/fetch.py <ROUTE_PLAN_ID> --save output.json` returned **HTTP 404** with the workspace `TIMEFOLD_API_KEY` — the route plan IDs you see in the Caire/Timefold UI (`aaf9d57f-…`, etc.) are on **another tenant or account** than this machine’s key.

**To analyze your dashboard runs locally:** fetch with the **same API key** that submitted the job, then point the commands below at the saved `output.json`.

```bash
cd /path/to/be-agent-service
source ~/.config/caire/env   # or the key that owns the dataset
python3 scripts/timefold/fetch.py <ROUTE_PLAN_ID> --save docs/analysis-runs/my-run/output.json
```

---

## 2. Input-only: `export-field-service-routing-v1-aaf9d57f-…-input.json` (v3/19)

| Script | Result |
|--------|--------|
| `scripts/timefold/submit.py validate …` | **OK** (shifts, visit time windows, FSR schema) |
| `scripts/verification/analyze_dependency_feasibility.py … --all` | **2414** dependencies analyzed: **368 infeasible**, 14 tight, 2032 OK. See `aaf9_dependency_report.json`. |
| `scripts/verification/verify_flex.py …` | **Failed (exit 1):** **80** visits with **no time flex** (`minStartTime == maxStartTime`). |

**Interpretation:** Large unassigned counts are expected when hundreds of dependency chains are **physically infeasible** under current windows, and many visits are **fixed-time** (no flex). Fixing data (windows, delays, flex) comes before solver tuning.

---

## 3. Full pipeline (local sample): `19narch` d708 input + output

Paired files in repo:

- Input: `recurring-visits/huddinge-package/.../19narch/export-field-service-routing-v1-d708cb57-…-input.json`
- Output: `recurring-visits/huddinge-package/.../19narch/export-field-service-routing-d708cb57-…-output.json`

| Script | Output in `d708-sample/` |
|--------|-------------------------|
| `scripts/analytics/metrics.py` | `metrics.txt` — 363 unassigned, field efficiency **68.74%** |
| `scripts/analytics/analyze_unassigned.py` | `analyze_unassigned.txt`, `unassigned.csv` — **0 supply**, **421** config-classified slots; overlapping shifts exist |
| `scripts/analytics/analyze_supply_demand.py` | `supply_demand.md` — no empty shifts; unassigned listed |
| `scripts/continuity/report.py` | `continuity.csv` |

**Interpretation (d708):** Unassigned are **not** due to “no shift that day” (supply = 0). The solver left visits unassigned while shifts were loaded — typical of **constraints + objective** (dependencies, skills, continuity weights, fixed windows), not missing Slingor.

---

## 4. Re-run everything

Replace paths after you have `output.json`:

```bash
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
INPUT="recurring-visits/huddinge-package/.../your-input.json"
OUTPUT="path/to/output.json"
OUT="docs/analysis-runs/manual-run"
mkdir -p "$OUT"

python3 scripts/timefold/submit.py validate "$INPUT"
python3 scripts/verification/analyze_dependency_feasibility.py "$INPUT" --all -o "$OUT/dependency.json"
python3 scripts/verification/verify_flex.py "$INPUT"

python3 scripts/analytics/metrics.py "$OUTPUT" --input "$INPUT" | tee "$OUT/metrics.txt"
python3 scripts/analytics/analyze_unassigned.py "$INPUT" "$OUTPUT" --csv "$OUT/unassigned.csv" | tee "$OUT/unassigned.txt"
python3 scripts/analytics/analyze_supply_demand.py "$OUTPUT" "$INPUT" --report "$OUT/supply_demand.md"
python3 scripts/continuity/report.py --input "$INPUT" --output "$OUTPUT" --report "$OUT/continuity.csv"
```

Other useful scripts (not run in this bundle): `scripts/analytics/analyze_empty_shifts.py`, `scripts/verification/verify_solution.py`, `scripts/campaigns/analyze_all_jobs.py` (needs API + job list).
