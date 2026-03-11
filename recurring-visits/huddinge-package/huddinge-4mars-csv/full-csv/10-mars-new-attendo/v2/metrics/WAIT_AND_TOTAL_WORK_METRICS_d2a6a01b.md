# Wait and total work metrics (d2a6a01b)

Run: **d2a6a01b-3309-4db5-ab4c-78ad1a218c19**. Definitions follow `docs/WAIT_AND_TOTAL_WORK_EXPLAINED.md`. Idle employees (0 visits) excluded from per-employee metrics; totals include all shifts.

---

## One set of numbers

| Metric | Value | Notes |
|--------|--------|--------|
| **Visit time** | 1656 h 52 min | From output (`totalServiceDuration` sum). |
| **Travel time** | 448 h 38 min | From output (`totalTravelTime` sum). |
| **Wait time (excl. breaks)** | **135 h 12 min** | Sum of each shift’s `totalWaitingTime`. Matches UI "Väntar". Break not included. |
| **Shift time (excl. breaks)** | **2240 h 42 min** | visit + travel + wait = "Total arbetstid". (2240.70 h from JSON.) |
| **Field hours** | **2105 h 30 min** | shift − wait = visit + travel (no wait). (2105.50 h from JSON.) |
| **Break time** | 188 h 0 min | Info only; not included in metrics above. |
| **Visit-span** ("Aktivt spann") | 2217 h 4 min | First visit start → last visit end, summed over shifts; excludes depot legs. |
| **Utilization (standard)** | **73,9%** | visit / (visit + travel + wait). |
| **Travel efficiency ratio** | **78,7%** | visit / (visit + travel); wait excluded. |

---

## Formulas (from WAIT_AND_TOTAL_WORK_EXPLAINED.md)

- **Shift time (excl. breaks)** = visit + travel + wait  
- **Field hours** = shift (excl. break) − wait = visit + travel  
- **Utilization (standard)** = visit / (visit + travel + wait)  
- **Travel efficiency ratio** = visit / (visit + travel)

Break is not part of shift time or utilization; it is reported for information only.
