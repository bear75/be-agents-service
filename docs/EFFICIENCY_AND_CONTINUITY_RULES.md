# Efficiency and Continuity Rules for Agents

**When running strategic new data assets** (campaigns, research runs, new datasets), all agents **must** use the same definitions and the same tooling for efficiency and continuity. This keeps goals comparable across runs and ensures the research/optimization loops evaluate correctly.

---

## Rule 1: Which metrics count

| Metric | Definition | Goal (quick-win) | Goal (ultimate) |
|--------|------------|------------------|-----------------|
| **Efficiency** | **Field efficiency** = visit time / (visit + travel). No wait, no idle. | > 70% | > 75% |
| **Continuity (avg)** | Average number of **distinct caregivers per client** over the planning window. | ≤ 11 | ≤ 8 |
| **Continuity (max)** | Max distinct caregivers for any single client. | ≤ 20 | — |
| **Unassigned** | Share of visits not assigned. | < 1% | < 1% |

**Efficiency rule:** Use **field efficiency** only (Reseffektivitet). Do **not** use “Effektivitet” (visit / total arbetstid) or staffing efficiency for goal checks — that denominator includes idle and differs by run type.

**Continuity rule:** Use the **per-client distinct-caregiver** metric from `scripts/continuity/report.py` only. Do not use other “Kontinuitetspoäng” or dashboard scores unless they are defined as the same quantity.

---

## Rule 2: How to produce the metrics

For **every** new data asset or campaign run:

1. **Efficiency (field, no idle)**  
   - Run: `scripts/analytics/metrics.py <solution.json> --input <input.json> --visit-span-only`  
   - Use: `field_efficiency_pct` from the saved metrics JSON.  
   - Stored in loops as `routing_efficiency_pct` for compatibility (same value when from visit-span run).

2. **Continuity**  
   - Run: `scripts/continuity/report.py --input <input.json> --output <solution.json> --report <path>.csv`  
   - Read: **Average unique count** → `continuity_avg`, **Max** → `continuity_max` from the report (or CSV column 3 and max of that column).

3. **Unassigned**  
   - From metrics JSON: `unassigned_visits` and total visits; or from solution `modelOutput.unassignedVisits.length` and input visit count.  
   - unassigned_pct = 100 × unassigned_visits / total_visits.

**One-shot analytics for a job (fetch + metrics + continuity + empty-shifts):**  
`scripts/analytics/analyze_job.sh <plan_id> --input <input.json> [--out-dir DIR]`  
or with existing solution:  
`scripts/analytics/analyze_job.sh --output <solution.json> --input <input.json> [--out-dir DIR]`

---

## Rule 3: With vs without idle

| Use case | Shift / time basis | Efficiency metric |
|----------|--------------------|-------------------|
| **Goals and comparisons** (research loop, optimization loop, new assets) | **Without idle** (visit-span) | `field_efficiency_pct` from `metrics.py --visit-span-only` |
| Dashboard “Effektivitet” (visit / total arbetstid) | Full shift (all provisioned time) | Different denominator; do **not** use for agent goals. |

So: for **all** strategic runs and new data assets, **efficiency = field efficiency, without idle**, from `metrics.py --visit-span-only`.

---

## Rule 4: Where this is enforced

- **schedule-research-loop.sh** — Uses `field_efficiency_pct` and continuity from specialist result; goals: continuity_avg ≤ 11, unassigned < 1%, field efficiency > 70%.
- **schedule-optimization-loop.sh** — Convergence uses `routing_efficiency_pct` (filled from `field_efficiency_pct`), continuity_avg ≤ 11, unassigned < 1%.
- **agents/timefold-specialist.sh** — Runs `metrics.py` with `--visit-span-only` and `--input`, runs `scripts/continuity/report.py`, returns `continuity_avg`, `continuity_max`, `field_efficiency_pct`, `routing_efficiency_pct`.

When adding **new** agents or scripts that evaluate FSR solutions on new data assets, they **must** use the same metrics and the same production method (Rule 2).

---

## Summary

- **Efficiency:** field efficiency only, from `metrics.py --visit-span-only` → `field_efficiency_pct`.  
- **Continuity:** from `scripts/continuity/report.py` → `continuity_avg`, `continuity_max`.  
- **Unassigned:** &lt; 1%.  
- Same rules for every strategic new data asset and for all agents that assess runs.
