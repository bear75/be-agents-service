---
module: recurring-visits (huddinge-package)
date: 2026-03-06
problem_type: integration_issue
component: csv_to_fsr_mapping
symptoms:
  - "26 unassigned visits (H034, H038) when same-day dependencies used 18h between Morgon and Lunch"
  - "Unclear when to add visitDependencies between different insatser vs same insats across weeks"
  - "Need dusch (48h) placeable directly next to lunch without hard dependency"
root_cause: same_day_dependency_applied_to_all_pairs
severity: high
tags:
  - timefold
  - visit-dependencies
  - csv-mapping
  - hemtjanst
  - insats
---

# CSV → FSR JSON: visitDependencies (same-day vs spread)

## Problem

When mapping hemtjänst CSV to Timefold FSR input we had to support two dependency behaviours without breaking feasibility or over-constraining:

1. **Same-day between different insatser (e.g. meals):** Frukost → Lunch with 3.5h (different CSV rows, same customer same day). CSV has "Antal tim mellan besöken" = 3,5h on the lunch row.
2. **Spread within same insats (e.g. shower):** Dusch1 → Dusch2 with 48h (same CSV row, flexible_day, week 2,3,4). Same row has "Antal tim mellan besöken" = 48h.
3. **No dependency between dusch and lunch** so the solver can place dusch directly next to lunch (continuity, efficiency) when time windows and shift allow.

Using the same dependency logic for both caused infeasibility (e.g. 18h same-day between Morgon and Lunch) and prevented dusch from being placed next to lunch.

## Root cause

- Same-day dependencies were applied to **all** consecutive same-day visits (Morgon → Lunch → Kväll) regardless of whether the delay value was short (3.5h) or long (48h). Long values are intended only for **spread** (same insats across days), not for same-day ordering.
- There was no rule to **omit** same-day dependency when the later row had a long delay (48h), so insatser like dusch were incorrectly forced to follow the same-day chain and could not sit next to lunch.

## Solution

1. **Split dependency logic by delay length (in script):**
   - **Same-day dependencies:** Only for **pinned** visits, same (kundnr, date_iso), ordered Morgon → Lunch → Kväll. Add `precedingVisit` + minDelay **only when** the **later** visit’s row has "Antal tim mellan besöken" filled and the parsed value is **≤ 12 hours** (e.g. 3.5h). Use `SAME_DAY_DELAY_MAX_MINUTES = 12 * 60`.
   - **Spread dependencies:** Only for **same row** (`row_index`), **flexible_day**, multiple occurrences in same period. Use CSV value (48h, 24h) or 18h default. Never add same-day dependency from/to these when the row’s delay is > 12h.

2. **Timefold does not distinguish** dependency types; it only sees `precedingVisit` + `minDelay`. We control behaviour by **which** edges we emit: same-day edges only for short-delay rows, spread edges only within same row.

3. **Cap infeasible delays** (existing logic): Same-day delays are capped to what fits between time windows (or removed). Spread delays are never capped below 18h.

## Code references

- **Constants:** `SAME_DAY_DELAY_MAX_MINUTES`, `SPREAD_DELAY_DEFAULT_MIN`, `SPREAD_DELAY_DEFAULT_ISO` in `recurring-visits/huddinge-package/huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py`.
- **Same-day:** `per_client_date`, `preceding_map` built only for pinned visits and when `delay_min <= SAME_DAY_DELAY_MAX_MINUTES`.
- **Spread:** `per_row_period` for flexible_day, same `(row_index, period_start_iso)`.

## Prevention

- When adding or changing CSV columns that affect dependencies, follow the full mapping spec: **CSV_TO_FSR_JSON_MAPPING_SPEC.md** in `recurring-visits/huddinge-package/docs/`.
- Do not add same-day dependency for a row whose "Antal tim mellan besöken" is > 12h; that value is for spread (same insats) only.
- Run dependency feasibility check (e.g. `analyze_dependency_feasibility.py`) after changing dependency logic.

## Related

- **Full mapping spec (all CSV → JSON rules):** [CSV_TO_FSR_JSON_MAPPING_SPEC.md](../../../recurring-visits/huddinge-package/docs/CSV_TO_FSR_JSON_MAPPING_SPEC.md)
- **Attendo verification:** `huddinge-package/huddinge-4mars-csv/docs/CSV_TO_INPUT_VERIFICATION.md`, `CSV_TILL_INPUT_VERIFIERING.md`
- **Implementation:** `huddinge-package/huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py`
