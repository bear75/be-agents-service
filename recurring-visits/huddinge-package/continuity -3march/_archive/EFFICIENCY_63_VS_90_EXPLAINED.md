# Why da2de902 from-patch shows ~63% efficiency (not ~90% like 203cf1d6)

Same 2-week Huddinge dataset; we added **continuity** (requiredVehicles) to get Run-B-style caregiver stability. The efficiency number is lower for two reasons: **which metric** is used, and **how much wait** the solution contains.

## 1. Two different efficiency definitions

| Source | Formula | Run B (203cf1d6) | da2de902 from-patch (e5de3f5d) |
|--------|--------|------------------|----------------------------------|
| **Huddinge report “89.9%”** | visit / **(visit + travel)** | **89.9%** (field) | **85.8%** (field) |
| **Our “staffing” (after idle removed)** | visit / **(visit + travel + wait)** | ~87%* | **~63%** |

- The **report’s “Efficiency (visit / visit+travel+break)”** in practice matches **field efficiency** = visit/(visit+travel). So the “90%” is **not** staffing; it ignores wait.
- Our **staffing** = visit / (shift − break). After from-patch, shift = visit + travel + wait + break (idle = 0), so staffing = visit / (visit + travel + **wait**). So **wait is in the denominator**.

So 63% is **staffing** (includes wait). The report’s 89.9% is **field** (excludes wait). They are different metrics.

## 2. Wait time is much higher in the continuity run

After from-patch (idle removed), the remaining “assignable” time is visit + travel + wait (+ break, which we exclude from the denominator). So:

- **203cf1d6 (Run B, no requiredVehicles):**  
  visit ~1502h, travel ~168h, **wait ~53h** → assignable ≈ 1723h → staffing ≈ 1502/1723 ≈ **87%** (and field 89.9%).
- **e5de3f5d (da2de902 from-patch, with requiredVehicles):**  
  visit ~1477h, travel ~244h, **wait ~624h** → assignable ≈ 2345h → staffing = 1477/2345 ≈ **63%** (field 85.8%).

So the continuity run has **about 12× more wait** (624h vs 53h). That wait is “paid but not at client” time, so it correctly lowers **staffing** efficiency.

## 3. Why continuity can increase wait

- **203cf1d6** was solved **without** requiredVehicles: any vehicle could serve any visit, so the solver could minimize travel and wait freely → 168h travel, 53h wait, 89.9% field.
- **da2de902** is the **same dataset + requiredVehicles** (continuity pools per client). The solver must assign each visit to one of a **limited set** of vehicles per client. That constraint often forces:
  - worse sequencing (more “arrive early, wait for time window”),
  - or more travel to satisfy both time windows and pool membership.

So we are not “just adding continuity to the same dataset” in a way that leaves the solution unchanged: we are **adding constraints** (requiredVehicles). Those constraints make it harder to achieve the same low wait (and same high staffing %) as 203cf1d6.

## 4. What to compare

- **Field efficiency** (visit / (visit+travel)): 203cf1d6 **89.9%**, da2de902 from-patch **85.8%** — same order of magnitude; continuity run a bit worse (more travel: 244h vs 168h).
- **Staffing** (visit / (visit+travel+wait)): 203cf1d6 would be **~87%** after removing idle; da2de902 from-patch **~63%** — the gap is mostly **extra wait** (624h vs 53h) in the continuity solution.

So the 63% is **expected** for our staffing definition when the continuity solution has high wait. To get staffing closer to the baseline we’d need to reduce wait (e.g. config tuning, or different continuity pools), not change the metric.

## 5. Reference numbers (from metrics outputs)

| Run | Visit h | Travel h | Wait h | Shift (trimmed) h | Field (visit/(v+t)) | Staffing (visit/(v+t+w)) |
|-----|---------|----------|--------|-------------------|----------------------|---------------------------|
| 203cf1d6 (Run B) orig | 1502 | 168 | 53 | 2502 (incl. idle) | 89.9% | 62.4%* (with idle) |
| 203cf1d6 after from-patch | — | — | ~53 | — | ~90% | ~87% |
| e5de3f5d (da2de902 from-patch) | 1477 | 244 | **~624** | 2454 | 85.8% | **~63%** |

\* 203cf1d6 original report shows 62.39% staffing because idle (684h) is still in the denominator; after removing idle, staffing would be ~87%.
