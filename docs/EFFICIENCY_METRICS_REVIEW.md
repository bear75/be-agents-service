# Efficiency Metrics — Documentation & UI Review

**Date:** 2026-02-28  
**Source:** Review of docs and UI referencing the 5 efficiency metrics  
**Canonical definitions:** `docs/EFFICIENCY_METRICS_EXPLAINED.md`

---

## 1. Summary of the 5 Metrics (from EFFICIENCY_METRICS_EXPLAINED.md)

| Metric | Alias | Formula | Target |
|--------|-------|---------|--------|
| `efficiency_pct` | — | visit / (shift − break) | ≥70% |
| `efficiency_assignable_used_pct` | `routing_efficiency_pct`, `field_incl_wait_pct` | visit / (visit + travel + wait) | ≥70% |
| `field_efficiency_pct` | — | visit / (visit + travel) | >67.5% |
| `idle_efficiency_pct` | — | visit / (visit + travel + idle) | — |
| `efficiency_visit_span_pct` | — | visit / shift_hours_visit_span | — |

**Dashboard mapping (3 charts):**
- **Eff 1:** `efficiency_all_pct` = `efficiency_pct` (staffing)
- **Eff 2:** `efficiency_min_visit_pct` = `routing_efficiency_pct` = `efficiency_assignable_used_pct`
- **Eff 3:** `efficiency_visit_span_pct`

---

## 2. Doc Files Reviewed

### 2.1 `recurring-visits/SCHEDULING_DEVELOPER_GUIDE.md`

| Location | Content | Consistency |
|----------|---------|-------------|
| Line 97 | Lists `efficiency_pct` among metrics in JSON | ✅ OK |
| Line 311 | Lists `efficiency_pct`, `field_efficiency_pct`, `field_incl_wait_pct` | ⚠️ Incomplete |

**Recommended changes:**
- Add `idle_efficiency_pct` and `efficiency_visit_span_pct` to the metrics list.
- Add a one-line note: "See `docs/EFFICIENCY_METRICS_EXPLAINED.md` for definitions."
- Clarify that `field_incl_wait_pct` = `routing_efficiency_pct` = `efficiency_assignable_used_pct`.

---

### 2.2 `docs/TIMEFOLD_RESEARCH_TEST_PLAN.md`

| Location | Content | Consistency |
|----------|---------|-------------|
| Line 30 | `routing_efficiency_pct` in compare list | ✅ OK |
| Line 42 | "Routing efficiency: >70% (Wait efficiency = visit/(visit+travel+wait))" | ✅ Correct |

**Recommended changes:** None. Already accurate.

---

### 2.3 `agents/prompts/timefold-specialist.md`

| Location | Content | Consistency |
|----------|---------|-------------|
| Line 44 | "Use **Wait efficiency** from the report: `visit / (visit + travel + wait)`" | ✅ Correct |
| Line 69 | "Always use **Wait efficiency** (visit/(visit+travel+wait)) for routing efficiency" | ✅ Correct |

**Recommended changes:** Add a reference: "See `docs/EFFICIENCY_METRICS_EXPLAINED.md` for all 5 efficiency metrics."

---

### 2.4 `docs/SCHEDULE_OPTIMIZATION_TESTING.md`

| Location | Content | Consistency |
|----------|---------|-------------|
| Schema, seed, API | `routing_efficiency_pct` | ✅ OK |

**Recommended changes:** Add a short section under "What to test" or "Troubleshooting": "For efficiency metric definitions, see `docs/EFFICIENCY_METRICS_EXPLAINED.md`."

---

## 3. Scripts Reviewed

### 3.1 `recurring-visits/scripts/fsr_metrics.py`

Formulas match `EFFICIENCY_METRICS_EXPLAINED.md`:
- `efficiency_pct` = visit / (shift − break) ✅
- `routing_efficiency_pct` = `efficiency_assignable_used_pct` = visit / (visit + travel + wait) ✅
- `field_efficiency_pct` = visit / (visit + travel) ✅
- `idle_efficiency_pct` = visit / (visit + travel + idle) ✅

### 3.2 `recurring-visits/huddinge-package/scripts/merge-metrics-into-base.py`

Mapping is correct:
- `efficiency_all_pct` ← `system_efficiency_pct` (base)
- `efficiency_min_visit_pct` ← `routing_efficiency_pct` (variant1)
- `efficiency_visit_span_pct` ← `routing_efficiency_pct` (variant2, visit-span aggregation)

---

## 4. UI Review

### 4.1 RunDetailPage.tsx

| Element | Current | Issue |
|---------|---------|-------|
| KPI card "Routing efficiency" | Shows `run.routing_efficiency_pct` | No tooltip explaining formula or target |
| Section "3 efficiency definitions" | Eff 1/2/3 with short descs | No link to doc; "Eff 2" not labeled as "routing" |
| Chart labels | "Eff 1: All shifts", "Eff 2: Min 1 visit", "Eff 3: Visit span" | Descriptions are brief; users may not understand denominators |

**Recommended UI changes:**
1. Add tooltip to "Routing efficiency" KPI: "Visit / (visit + travel + wait). Target ≥70%. See docs/EFFICIENCY_METRICS_EXPLAINED.md"
2. Add a "Learn more" link under the 3 efficiency charts → `docs/EFFICIENCY_METRICS_EXPLAINED.md` (or a `/docs/efficiency` route if you have one)
3. Improve chart labels:
   - Eff 1: "Staffing efficiency — visit / (shift − break)"
   - Eff 2: "Routing efficiency — visit / (visit + travel + wait)"
   - Eff 3: "Visit-span — visit / (first visit → last visit)"

---

### 4.2 SchedulesPage.tsx

| Element | Current | Issue |
|---------|---------|-------|
| Table headers | `title` attributes on Eff columns | Tooltips exist but are terse |
| Eff total % | "Visit time / total shift hours" | May include break; differs from `efficiency_pct` (shift − break) |
| Eff trimmed % | "Visit time / trimmed shift hours" | OK; trimmed = shift − idle |
| Eff all % | "All shifts and hours" | Vague |
| Eff min visit % | "Exclude empty shifts only" | OK; could add "= routing efficiency" |
| Eff visit span % | "Visit-span only (shift = first→last visit)" | OK |
| Scatter Y-axis | `efficiency_trimmed_pct ?? routing_efficiency_pct` | **Inconsistency:** Goal is routing ≥70%, but scatter may show `efficiency_trimmed_pct` when present |

**Recommended UI changes:**
1. Update table header tooltips to match `EFFICIENCY_METRICS_EXPLAINED.md`:
   - Eff all %: "Staffing: visit / (shift − break). All shifts, incl. empty."
   - Eff min visit %: "Routing: visit / (visit + travel + wait). Shifts with ≥1 visit. Target ≥70%."
   - Eff visit span %: "Visit-span: visit / (first→last visit). No idle."
2. **ScatterPlot:** Use `efficiency_min_visit_pct ?? routing_efficiency_pct` (or `routing_efficiency_pct ?? efficiency_min_visit_pct`) so the Y-axis matches the "routing efficiency ≥70%" goal. Avoid `efficiency_trimmed_pct` for the scatter.
3. Add a small "?" or info icon next to "Efficiency %" in the scatter caption that links to or opens a tooltip with the doc reference.

---

### 4.3 ScatterPlot.tsx

| Current | Issue |
|---------|-------|
| `getEfficiency(r)` = `efficiency_trimmed_pct ?? routing_efficiency_pct` | `efficiency_trimmed_pct` = visit / (shift − idle), which is different from routing. Success criterion is routing ≥70%. |

**Recommended change:** Prefer routing for the scatter:
```ts
function getEfficiency(r: ScheduleRun): number | null {
  return r.efficiency_min_visit_pct ?? r.routing_efficiency_pct ?? r.efficiency_trimmed_pct ?? null;
}
```
Or, if `efficiency_min_visit_pct` is always populated when metrics exist, use that first.

---

## 5. run-folder-parser.ts Note

`efficiency_total_pct` = visit / shift_time_h (does not subtract break).  
`efficiency_trimmed_pct` = visit / (shift_time_h − inactive_time_h).

These differ from `efficiency_pct` (visit / (shift − break)) in `EFFICIENCY_METRICS_EXPLAINED.md`. If you want strict alignment, consider computing `efficiency_total_pct` as visit / (shift − break) when break is available. For now, the table tooltips should clarify what each column represents.

---

## 6. Action Checklist

### Docs to update

| File | Change |
|------|--------|
| `recurring-visits/SCHEDULING_DEVELOPER_GUIDE.md` | Add `idle_efficiency_pct`, `efficiency_visit_span_pct`; add link to EFFICIENCY_METRICS_EXPLAINED.md; clarify `field_incl_wait_pct` = routing |
| `agents/prompts/timefold-specialist.md` | Add reference to EFFICIENCY_METRICS_EXPLAINED.md |
| `docs/SCHEDULE_OPTIMIZATION_TESTING.md` | Add one-line reference to EFFICIENCY_METRICS_EXPLAINED.md |

### UI to update

| File | Change |
|------|--------|
| `RunDetailPage.tsx` | Add tooltip to Routing efficiency KPI; add "Learn more" link under 3 charts; improve chart labels |
| `SchedulesPage.tsx` | Improve table header tooltips for Eff all %, Eff min visit %, Eff visit span % |
| `ScatterPlot.tsx` | Use `efficiency_min_visit_pct ?? routing_efficiency_pct` for Y-axis (drop `efficiency_trimmed_pct` as primary) |

### Optional

- Add a `/docs/efficiency` or help route that renders or links to `EFFICIENCY_METRICS_EXPLAINED.md` for in-app access.
- Extend `EFFICIENCY_METRICS_EXPLAINED.md` with a short section on `efficiency_total_pct` and `efficiency_trimmed_pct` (server/parser definitions) to avoid confusion.
