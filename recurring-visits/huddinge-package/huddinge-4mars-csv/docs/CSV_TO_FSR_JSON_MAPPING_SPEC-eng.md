# CSV → Timefold FSR JSON: full mapping spec (Caire home-care model)

**Purpose:** A dev or AI can use this to map home-care visit requirements (CSV) into Caire's model (Timefold FSR JSON) for optimization. Visits should be **as flexible as possible** so the solver can maximize assigned visits, continuity, and efficiency; only necessary constraints (time windows and dependencies) should be added.

**Reference implementation:** `huddinge-package/huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py`  
**Verification for Attendo:** `huddinge-4mars-csv/docs/CSV_TO_INPUT_VERIFICATION.md`, `CSV_TILL_INPUT_VERIFIERING.md`

---

## 1. How Timefold distinguishes dependency types

**Timefold does not** distinguish between "same insats spread" and "same day between different insatser". The JSON only contains:

```json
"visitDependencies": [{ "precedingVisit": "<visitId>", "minDelay": "PT3H30M" }]
```

The solver only sees: *"Visit B must start at least X after visit A ends."*  
**The difference** is how **we** build which links we add:

| Type | We create dependency | Timefold sees |
|------|----------------------|---------------|
| **Same insats, spread** (e.g. shower1 → shower2 48h, lunch1 → lunch2 24h, breakfast1 → breakfast2 24h) | Only between occurrences of **the same CSV row** (same `row_index`), **flexible_day**, multiple visits per period. minDelay from CSV (48h, 24h) or 18h default. | `precedingVisit` = previous occurrence of same row, `minDelay` = PT48H / PT24H etc. |
| **Same day, different insatser** (e.g. breakfast1 → lunch1 3.5h; no dep shower1→lunch1) | Only between **pinned** visits same (customer, date), ordered Morgon → Lunch → Kväll. Add only when **the later** visit's row has "Antal tim mellan besöken" filled with a **short** value (≤ 12h). | `precedingVisit` = previous slot (different row), `minDelay` = e.g. PT3H30M. |

Examples:

- **shower1 (48h), shower2 (48h):** Same row, flexible_day → we add **spread** shower1 → shower2 with 48h. No same-day dep from lunch to shower.
- **lunch1 (24h), lunch2 (24h):** Same row, flexible_day → **spread** lunch1 → lunch2 with 24h.
- **breakfast1 (3.5h), lunch1 (3.5h):** Different rows, pinned same day → **same-day** breakfast1 → lunch1 with 3.5h (breakfast before lunch).
- **shower1 (0h), lunch1 (0h):** We add **no** dependency between shower and lunch (0h = no same-day dep for 48h row), so shower can be placed directly next to lunch.

---

## 2. Concepts and model

- **One CSV row = one insats** (one intervention type, e.g. "3 lunches/week" or "2 showers/week"). An insats can yield one or more visits per day/week/period.
- **Pinned day:** Visit has exactly one date. We **pin only** when weekdays form a **complete set**: all weekdays (mån–fre), both weekend (lör–sön), or all 7 (daily). One time window per visit.
- **Flexible_day:** Solver chooses which day(s) within a period. Used when weekdays are **partial** (e.g. "mån tis tor", "ons", "tis fre") or when no weekdays are given (e.g. "Varannan vecka, tis"). One time window per eligible day in the period; spread dependencies (e.g. 18h) keep visits on different days.
- **Visit:** An FSR visit = one visit occurrence with location, time windows, duration, optional visitDependencies and optional visitGroup.

---

## 3. All rules for CSV → JSON

### 3.1 Planning window and occurrences

- Compute planning window (start–end) from CSV (e.g. longest recurrence = 4 weeks).
- Expand each CSV row to **occurrences**: one per (row, date) for pinned; one per (row, period, period_visit_index) for flexible_day.
- Each occurrence becomes **one** visit in JSON (id, location, timeWindows, serviceDuration, visitDependencies, optional visitGroup).

### 3.2 Visit ID and name

- **id:** `{kundnr}_r{row_index}_{counter}` (e.g. `H015_r12_1`). Unique per visit.
- **name:** `{kundnr} {När på dagen} {Skift} {Insats}` (for traceability).

### 3.3 Location

- Address (Gata, Postnr, Ort) → geocoding to [lat, lon]. Normalize street (e.g. strip LGH number) before geocoding.

### 3.4 Time windows (timeWindows)

- **När på dagen** maps to slot:
  - Morgon → 07:00–10:30
  - Lunch → 11:00–13:30
  - Kväll → 16:00–19:00
  - Empty/other → full day 07:00–22:00 (or shift window if Skift set)
- **Pinned:** One timeWindow per visit: same date, slot start–end (adjusted with Starttid, Före, Efter if set; otherwise full slot).
- **Flexible_day:** One timeWindow per eligible day in the period (restricted by Skift and weekdays from Återkommande), with same slot (Morgon/Lunch/Kväll) or full day.
- **Requirement:** Every visit must have either time flex (minStartTime ≠ maxStartTime) or day flex (multiple windows). No visit with exactly one window and zero flex.

### 3.5 Duration (serviceDuration)

- **Längd** (minutes) → ISO 8601 duration, e.g. `PT25M`.

### 3.6 VisitDependencies (minDelay)

Two types. Both use the CSV column **"Antal tim mellan besöken"** but in different ways.

#### A) Same-day (different insatser, same customer same day)

- **When:** Pinned visits, same (kundnr, date). Order: Morgon (0) → Lunch (1) → Kväll (2), then Starttid.
- **Rule:** For each pair (previous visit, current visit) in this order: add `precedingVisit` → current with minDelay **only if** the current visit's **row** has "Antal tim mellan besöken" filled **and** the value is **≤ 12 hours** (e.g. 3.5h for breakfast→lunch).
- **Why 12h:** Long values (18h, 24h, 48h) are for **spread within the same insats** (flexible_day). Shower (48h) must not get a same-day dep from lunch so shower can sit directly next to lunch.
- **Delay value:** For same-day we use the **CSV value as-is** (e.g. PT3H30M). No subtraction of previous slot length; Timefold measures from end of preceding visit to start of next. Cap if the delay does not fit between the two visits' time windows (with margin); remove dependency if infeasible.

#### B) Spread (same insats, same row, flexible_day)

- **When:** Same CSV row (`row_index`), same period (`period_start_iso`), **flexible_day**, at least 2 occurrences in the period.
- **Rule:** Chain occurrence 1 → 2 → 3 with minDelay. Value from "Antal tim mellan besöken" (e.g. 48h, 24h); if empty use **18h** default so visits fall on different days.
- **Effective delay:** `effective = interval - previous slot length`, floor **18h** (never below 18h for spread). Cap if chain does not fit in period window; keep at least 18h.
- **One occurrence per period:** No spread dependency (only one visit to place).

#### C) Other dependency rules

- **Never** add a dependency between two visits that belong to the same **visitGroup** (Dubbel) — avoids loops in the model.
- For same-day: if both visits belong to the same spread chain (same row_index + period) skip (spread defines order there).
- Dependencies with original delay ≥ 18h must **not** be capped below 18h when capping.

### 3.7 VisitGroups (Dubbel)

- Same **Dubbel** value + same **date** (or same period for flexible_day) → same visitGroup. All visits in the group must be scheduled together (same time, same day).

### 3.8 Vehicles and shifts

- **Slinga** → one vehicle per unique Slinga.
- **Schift** (Dag / Helg / Kväll) → shift per vehicle: which days (Mon–Fri, Sat–Sun, all 7) and time ranges (Dag 07–15, Helg 07–14:30, Kväll 16–22). Dag/Helg: requiredBreak (10–14, 30 min at office).
- Create one shift per (vehicle, date) that matches the vehicle's allowed days in the planning window.

### 3.9 Automatic corrections

- **Flex:** If Före=Efter=0, always use the full slot (no zero flex).
- **Dependency:** If the given minDelay is larger than what physically fits between two visits' time windows, cap to the maximum feasible (with margin) or remove the dependency if nothing fits.

---

## 4. Summary: what constrains optimization

| Element | Purpose | Flexibility |
|---------|---------|--------------|
| **timeWindows** | When the visit may occur (day/time) | As wide as the requirement allows (full slot, multiple days for flexible_day). |
| **visitDependencies** | Order and minimum gap (same day: meals; spread: same insats) | Only where CSV requires it (short ≤12h for same-day; long only within same row). |
| **visitGroups** | Simultaneity (Dubbel) | Only when Dubbel is set. |
| **Vehicles/shifts** | Available resources | One shift per allowed day. |

Everything else (continuity, travel, number of assigned visits) is driven by **solver weights**, not hard dependencies between different insatser. So e.g. shower can be placed directly next to lunch when time windows and shift allow.

---

## 5. Constants (reference implementation)

- `SAME_DAY_DELAY_MAX_MINUTES = 12 * 60` — above this, "Antal tim mellan besöken" is used only for spread.
- `SPREAD_DELAY_DEFAULT_MIN = 18 * 60`, `SPREAD_DELAY_DEFAULT_ISO = "PT18H"` — default between flexible_day occurrences when CSV is empty.
- Slots: Morgon 07:00–10:30, Lunch 11:00–13:30, Kväll 16:00–19:00, Full day 07:00–22:00.

---

## 6. Related documents

- **CSV_TO_INPUT_VERIFICATION.md** / **CSV_TILL_INPUT_VERIFIERING.md** — verification for Attendo, examples.
- **Timefold FSR OpenAPI (v1)** — [schema](https://app.timefold.ai/openapis/field-service-routing/v1) for Visit, TimeWindow, VisitDependency, VisitGroup, Vehicle, VehicleShift.
- **attendo_4mars_to_fsr.py** — implemented rules and constants.
