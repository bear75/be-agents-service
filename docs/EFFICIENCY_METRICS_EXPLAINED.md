# 5 Efficiency Metrics Explained

From `metrics_20260228_170830_203cf1d6.json` and `recurring-visits/scripts/fsr_metrics.py`.

**Time equation:** `shift = visit + travel + wait + break + idle`

---

## 1. `efficiency_pct` (62.39%) — Staffing efficiency

**Formula:** `visit_time_h / (shift_time_h - break_time_h) × 100`

**Denominator:** All paid shift hours (excl. break). Includes empty shifts and idle time.

**Meaning:** What share of paid caregiver time is spent on actual visits. Low when many empty shifts or lots of idle time.

**Target:** ≥70% (see `huddinge-package/docs/PRIORITIES.md`)

---

## 2. `efficiency_assignable_used_pct` (87.15%) — Assignable time used

**Formula:** `visit_time_h / (visit_time_h + travel_time_h + wait_time_h) × 100`

**Alias:** `routing_efficiency_pct`, `field_incl_wait_pct`

**Denominator:** Only assignable time: visit + travel + wait. Excludes break and idle.

**Meaning:** Of the time actually used for visits/travel/wait, how much is visit. Measures routing quality (minimize travel+wait).

**Target:** ≥70%

---

## 3. `field_efficiency_pct` (89.91%) — Field / travel efficiency

**Formula:** `visit_time_h / (visit_time_h + travel_time_h) × 100`

**Denominator:** Visit + travel only (no wait).

**Meaning:** Of visit+travel time, how much is visit. Pure travel vs care ratio.

**Target:** >67.5% (field target)

---

## 4. `idle_efficiency_pct` (63.79%) — Idle-aware efficiency

**Formula:** `visit_time_h / (visit_time_h + travel_time_h + inactive_time_h) × 100`

**Denominator:** Visit + travel + idle. Excludes wait and break.

**Meaning:** Similar to staffing efficiency but uses a different denominator (visit+travel+idle). Idle is unassigned time within shifts.

**Note:** ≈ efficiency_pct when wait is small; differs when wait is significant.

---

## 5. `efficiency_visit_span_pct` (92.17%) — Visit-span efficiency

**Formula:** `visit_time_h / shift_hours_visit_span × 100`

**Denominator:** Visit span = first visit start → last visit end per shift, summed. No idle (idle_hours_visit_span = 0).

**Meaning:** Of the time between first and last visit (per shift), how much is visit. Best-case view: ignores empty shifts and idle before/after visits.

**Source:** From variant2 metrics (visit-span-only aggregation). Merge script: `merge-metrics-into-base.py`.

---

## Summary table

| Metric | Denominator | Break | Idle | Empty shifts |
|--------|-------------|-------|------|--------------|
| efficiency_pct | shift − break | Excl | Incl | Incl |
| efficiency_assignable_used_pct | visit + travel + wait | Excl | Excl | N/A (assignable only) |
| field_efficiency_pct | visit + travel | Excl | Excl | N/A |
| idle_efficiency_pct | visit + travel + idle | Excl | Incl | N/A |
| efficiency_visit_span_pct | first visit → last visit | In span | Excl (0) | Excl |

---

## Dashboard mapping (3 charts)

The Run Detail page shows 3 efficiency definitions with time breakdown charts. **Each bar must match its displayed percentage.**

| Chart | Metric | Total (denominator) | Segments | Example |
|-------|--------|--------------------|----------|---------|
| **Eff 1** | 62.4% | shift − break | visit, travel, wait, idle | All shifts, includes idle |
| **Eff 2** | 87.2% | shift − break (shifts with ≥1 visit only) | visit, travel, wait, idle (idle within those shifts) | Min-1-visit; idle = unassigned within non-empty shifts. Eff 3 = visit span, no idle. |
| **Eff 3** | 92.2% | visit / (pct/100) | visit, travel, wait (scaled) | Visit span; no idle |

- **Eff 1 (All shifts):** `efficiency_all_pct` = `system_efficiency_pct` = `efficiency_pct`
- **Eff 2 (Min 1 visit):** `efficiency_min_visit_pct` = `routing_efficiency_pct` = `efficiency_assignable_used_pct`
- **Eff 3 (Visit span):** `efficiency_visit_span_pct`
