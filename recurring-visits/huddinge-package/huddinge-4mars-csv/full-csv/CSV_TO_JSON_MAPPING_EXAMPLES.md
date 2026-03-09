# CSV → FSR JSON mapping examples (81 clients, 2w, no extra vehicles)

Generated from a full pipeline run with:
- **CSV:** `ATTENDO_DATABEHOV_ALL_81_CLIENTS.csv`
- **Script:** `attendo_4mars_to_fsr.py`
- **Options:** `--start-date 2026-03-02 --end-date 2026-03-15 --no-supplementary-vehicles`
- **Output:** `fsr_input_81_2w.json`

**Result:** 969 CSV rows → 3697 visits, 46 vehicles (Slingor only), 544 shifts. Full flex within visit_rules (time windows from När på dagen + Före/Efter; delay from "Antal tim mellan besöken").

---

## 1. Same day, different insats (e.g. breakfast → lunch)

**Rule (from docs):** Pinned visits, same (kundnr, date), ordered Morgon → Lunch → Kväll. If the **later** visit’s row has "Antal tim mellan besöken" ≤ 12h (e.g. 3,5 timmar), add a **same-day** dependency with that delay.

### CSV (H015 – Tillsyn Morgon + Lunch)

| Row | Kundnr | När på dagen | Insatser | Antal tim mellan besöken | Återkommande |
|-----|--------|--------------|----------|--------------------------|--------------|
| 0   | H015   | Morgon       | Tillsyn  | 3,5timmar                | Varje vecka, mån tis ons tor fre |
| 2   | H015   | Lunch        | Tillsyn  | 3,5timmar                | Varje vecka, mån tis ons tor fre |

- **Morgon:** Starttid 07:05, Längd 6, Före 0, Efter 120 → slot Morgon 07:00–10:30, flex 07:05–09:05.
- **Lunch:** Starttid 13:00, Längd 6, Före 60, Efter 90 → slot Lunch 11:00–13:30, flex 12:00–14:30.

### JSON (one date: 2026-03-02)

**Visit 1 – Morgon (H015_r0_1)**  
- One time window per pinned date.  
- Full flex within Morgon slot (minStartTime–maxStartTime ≠ 0).

```json
{
  "id": "H015_r0_1",
  "name": "H015 Morgon  Tillsyn",
  "location": [59.2334527, 17.9911485],
  "timeWindows": [{
    "minStartTime": "2026-03-02T07:05:00+01:00",
    "maxStartTime": "2026-03-02T09:05:00+01:00",
    "maxEndTime": "2026-03-02T09:11:00+01:00"
  }],
  "serviceDuration": "PT6M"
}
```

**Visit 2 – Lunch (H015_r2_1)**  
- Same date, later slot.  
- **visitDependencies:** Lunch must start at least **3.5 h** after end of Morgon (same client, same day).

```json
{
  "id": "H015_r2_1",
  "name": "H015 Lunch  Tillsyn",
  "location": [59.2334527, 17.9911485],
  "timeWindows": [{
    "minStartTime": "2026-03-02T12:00:00+01:00",
    "maxStartTime": "2026-03-02T14:30:00+01:00",
    "maxEndTime": "2026-03-02T14:36:00+01:00"
  }],
  "serviceDuration": "PT6M",
  "visitDependencies": [{
    "id": "dep_H015_r2_1_0",
    "precedingVisit": "H015_r0_1",
    "minDelay": "PT3H30M"
  }]
}
```

**Mapping summary**
- **Same-day dependency:** Only when "Antal tim mellan besöken" on the **later** row is short (≤ 12h). Value taken as-is (e.g. 3,5 timmar → `PT3H30M`). Timefold: “Lunch starts ≥ 3.5 h after Morgon ends.”
- **Time windows:** From När på dagen (Morgon/Lunch/Kväll) + Starttid, Före, Efter (full flex within slot).

### When the 3.5h delay doesn’t fit (time windows too short)

If the gap between **breakfast end** and **lunch start** is shorter than the requested delay (e.g. 3.5h), the dependency would make lunch impossible. The script avoids that by running **`_cap_infeasible_delay`** for every same-day dependency before writing JSON.

**Logic (same as `analyze_dependency_feasibility.py`):**

1. For each **same-date** window pair:
   - **prev_max_end** = latest end of the preceding visit (e.g. Morgon maxEndTime on that day).
   - **dep_latest_start** = latest time the dependent visit can start = Lunch maxEndTime − Lunch duration (so the visit still finishes inside the window).
   - **max_delay** = `dep_latest_start − prev_max_end − 15 min` (15 min margin). If negative, that day cannot satisfy any positive delay with margin.

2. **best_cap_min** = largest max_delay over all dates where both visits have a window (or None if none).

3. **Result:**
   - If CSV delay (e.g. 210 min for 3.5h) **≤ best_cap_min**: keep the CSV value (e.g. `PT3H30M`). At least one day can satisfy it.
   - If CSV delay **> best_cap_min** but **best_cap_min ≥ 0**: **cap** minDelay to `best_cap_min`, emit `WARNING: delay … infeasible for all window pairs, capped to PT… (15 min margin)`. Lunch stays feasible; the constraint is loosened.
   - If **best_cap_min** is None or **< 0**: **remove** the dependency, emit `WARNING: dependency … infeasible (no window pair with 15 min margin), removing`. Otherwise the model would be infeasible.

So breakfast → lunch is never left as “3.5h” when the slots don’t allow it: the script either **caps** the delay to what fits (so lunch remains possible) or **drops** the dependency (if no day has room even with 0 delay and 15 min margin).

**Example from the pipeline run:** Several same-day dependencies were capped, e.g.  
`H029_r33_1 ← H029_r30_1: delay PT3H30M infeasible for all window pairs, capped to PT3H20M`  
and  
`H034_r40_1 ← H034_r37_1: delay PT3H30M … capped to PT3H8M`.  
So for those clients, the written minDelay is the capped value, not 3.5h.

---

## 2. Same insats, multi-day spread (e.g. shower / flexible visits)

**Rule (from docs):** Same CSV row (`row_index`), **flexible_day**, several occurrences per period. Chain occurrence 1 → 2 → … with **spread** minDelay. Value from "Antal tim mellan besöken" (e.g. 42h, 48h); if empty, **18h** default so visits tend to fall on different days. Effective delay can be capped to fit the period; never below 18h for spread.

### CSV (H025 – Lunch Förflyttning, 4×/week, solver picks which days)

| Row | Kundnr | När på dagen | Insatser   | Antal tim mellan besöken | Återkommande    |
|-----|--------|--------------|------------|--------------------------|-----------------|
| 8   | H025   | Lunch        | Förflyttning | (empty)                | Varje vecka, mån tis ons fre |

- **Återkommande** is **"mån tis ons fre"** — Monday, Tuesday, Wednesday, Friday. **Thursday (tor) is not in the list**, so the visit is only eligible on those four weekdays.
- Not a full weekday set (mån–fre would be all 5) → **flexible_day**: the script creates **4 visits per week** (one per weekday in the set), so **8 visits in a 2-week window** (H025_r8_1 … H025_r8_8). Each of those visits gets one time window per eligible day in its week (Mon, Tue, Wed, Fri); the solver picks which day for each visit.
- No "Antal tim mellan besöken" → spread uses **default PT18H** between consecutive occurrences (so visit 2 ≥ 18h after visit 1, etc.).

### JSON (2 weeks → 8 visits, spread 18h between consecutive)

**Visit 1 – Week 1 (H025_r8_1)**  
- **Multiple time windows:** One per eligible day in the period. The CSV says "mån tis ons fre", so only Mon, Tue, Wed, Fri — **Thursday is excluded by the CSV**, hence no window on Thu. Solver picks one of the four days.

```json
{
  "id": "H025_r8_1",
  "name": "H025 Lunch  Förflyttning",
  "location": [59.238847, 17.9605585],
  "timeWindows": [
    { "minStartTime": "2026-03-02T11:00:00+01:00", "maxStartTime": "2026-03-02T12:00:00+01:00", "maxEndTime": "2026-03-02T12:09:00+01:00" },
    { "minStartTime": "2026-03-03T11:00:00+01:00", "maxStartTime": "2026-03-03T12:00:00+01:00", "maxEndTime": "2026-03-03T12:09:00+01:00" },
    { "minStartTime": "2026-03-04T11:00:00+01:00", "maxStartTime": "2026-03-04T12:00:00+01:00", "maxEndTime": "2026-03-04T12:09:00+01:00" },
    { "minStartTime": "2026-03-06T11:00:00+01:00", "maxStartTime": "2026-03-06T12:00:00+01:00", "maxEndTime": "2026-03-06T12:09:00+01:00" }
  ],
  "serviceDuration": "PT9M"
}
```

**Visit 2 – second of the 8 (H025_r8_2)**  
- Same row, next occurrence.  
- **visitDependencies:** Must start at least **18 h** after the previous occurrence (spread over days).

```json
{
  "id": "H025_r8_2",
  "name": "H025 Lunch  Förflyttning",
  "location": [59.238847, 17.9605585],
  "timeWindows": [
    { "minStartTime": "2026-03-09T11:00:00+01:00", "maxStartTime": "2026-03-09T12:00:00+01:00", "maxEndTime": "2026-03-09T12:09:00+01:00" },
    ...
  ],
  "serviceDuration": "PT9M",
  "visitDependencies": [{
    "id": "dep_H025_r8_2_0",
    "precedingVisit": "H025_r8_1",
    "minDelay": "PT18H"
  }]
}
```

### Shower example (H038 Bad/Dusch – 3×/week, 24h spread)

CSV: "Varje vecka, mån tis fre", Bad/Dusch, "24 timmar".  
→ 3 flexible_day visits per week (solver picks which of Mon/Tue/Fri), 6 in 2 weeks.  
→ Spread dependency between consecutive occurrences: minDelay from CSV (24h), effective delay may be reduced by previous slot length but floored at 18h.  
→ Each visit has **one time window per eligible day** in its week (full flex within slot).

**Mapping summary**
- **Spread dependency:** Same **row**, **flexible_day**, ≥ 2 occurrences in the period. Delay = "Antal tim mellan besöken" or **PT18H** default; effective delay ≥ 18h.
- **Time windows:** One window per eligible day in the period (and per weekday when applicable), so solver gets full flex on which day to place the visit within the slot rules.

---

## 3. Reference

- **Spec:** `docs/CSV_TO_FSR_JSON_MAPPING_SPEC-eng.md`
- **Recurrence / pin vs flexible:** `docs/RECURRING_VISITS_HANDLING.md`
- **Script:** `scripts/attendo_4mars_to_fsr.py`
