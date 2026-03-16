# Per-day FSR workaround – efficiency report

**Purpose:** Run the per-day workaround end-to-end and report efficiency so we can verify the approach before implementing ESS+FSR in the app.

---

## What was run

- **Script:** `run_per_day_workaround.py`
- **Input:** Multi-day solution `fixed/from-patch-reduced/export-field-service-routing-5ff46c3d-*-output.json` and full input `fixed/from-patch-reduced/input-only-used-shifts.json`.
- **Process:** For each calendar day in the solution, build a per-day input (only that day’s visits and only shifts that had visits that day), set `pinningRequested` and `minStartTravelTime` from the multi-day solution, POST as new route plan (PT5M termination), poll until SOLVING_COMPLETED, then aggregate.

**Completed runs:**

- **2 days (2026-02-10, 2026-02-11):** Full run completed.
- **3 days (2026-02-10, 2026-02-11, 2026-02-12):** Outputs saved; aggregate below.

---

## Efficiency results

### Per-day workaround (3 days aggregated)

| Metric                    | Value                                            |
| ------------------------- | ------------------------------------------------ |
| Days                      | 3 (2026-02-10, 2026-02-11, 2026-02-12)           |
| Total visits              | 1,194                                            |
| Total shifts              | 81 (all with ≥1 visit; **0 empty shifts**)       |
| Shift time (excl. breaks) | 565.2 h                                          |
| Visit time                | 470.9 h                                          |
| Travel time               | 84.7 h                                           |
| **Efficiency**            | **83.3%** (visit time / shift time excl. breaks) |

### Comparison: multi-day from-patch vs per-day workaround

| Metric                               | Multi-day from-patch | Per-day workaround       |
| ------------------------------------ | -------------------- | ------------------------ |
| Empty shifts                         | 167                  | **0**                    |
| Shifts with ≥1 visit                 | 143                  | (all shifts have visits) |
| Efficiency (all shifts)              | 59.6%                | **83.3%**                |
| Efficiency (shifts with visits only) | 84.1%                | **83.3%**                |

So the workaround:

- **Removes empty shifts** (only shifts that have visits are sent each day).
- **Keeps utilization in line with “shifts with visits only”** (~84%).
- **Preserves assignments** via pinning (no unassigned visits in the runs above).

---

## How to reproduce

```bash
cd apps/dashboard/test_data_import

# Optional: dry-run to build per-day inputs only
python3 run_per_day_workaround.py --dry-run

# Run first N days (e.g. 2) for a quick check
python3 run_per_day_workaround.py --days 2

# Run all days (14 days; allow ~7–10 min per day)
export TIMEFOLD_API_KEY="your-key"
python3 run_per_day_workaround.py
```

Outputs:

- `fixed/per-day-workaround/input-{date}.json` – per-day modelInput
- `fixed/per-day-workaround/output-{date}.json` – per-day solution
- `fixed/per-day-workaround/efficiency_report.json` – aggregated KPIs

---

## Conclusion

The per-day workaround achieves **~83–84% efficiency** and **0 empty shifts** when aggregating over the days that were run, matching the “efficiency on used shifts only” of the multi-day from-patch solution (84.1%). It is suitable for **verifying efficiency** before implementing the full ESS+FSR loop in the app. For production, the preferred path remains **ESS (demand-driven shifts) + FSR (routing only)** so that shift count is decided by ESS and FSR does not need this workaround.
