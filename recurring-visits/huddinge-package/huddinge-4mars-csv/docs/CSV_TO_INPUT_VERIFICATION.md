# CSV → input JSON: verification for Attendo Huddinge

**Svenska:** Se **CSV_TILL_INPUT_VERIFIERING.md** i samma mapp.

**For Attendo:** This document describes how we interpret your CSV file (*ATTENDO_DATABEHOV_PER_KUND_OCH_BESOK - data.csv*) when building input for our route optimizer (Timefold Field Service Routing). The aim is for you to verify that our interpretation matches your intent — time windows, which visits belong together (Dubbel), gaps between visits, and recurrence. If anything is wrong we can adjust the rules before running. The final input is sent as JSON to Timefold. To inspect the JSON structure (visits, vehicles, shifts, time windows, visit groups), use Timefold’s open API schema: **[Timefold FSR OpenAPI (v1)](https://app.timefold.ai/openapis/field-service-routing/v1)**.

**Schema / API reference:** The generated JSON input conforms to the Timefold Field Service Routing (FSR) API model. To verify the exact structure (visits, timeWindows, visitDependencies, visitGroups, vehicles, shifts) and field types (e.g. ISO 8601 times and durations), you can use the official OpenAPI specification: **[Timefold FSR OpenAPI (v1)](https://app.timefold.ai/openapis/field-service-routing/v1)**. There you will find the `RoutePlanInput` (modelInput) schema and descriptions for `Visit`, `TimeWindow`, `VisitDependency` (minDelay), `VisitGroup`, `Vehicle`, and `VehicleShift`.

This document describes **how we interpret your CSV** when building the optimization input. Use it to confirm that our mapping matches your intent. If anything is wrong, we can adjust the rules before running the solver.

**Canonical mapping rules (for devs/AI):** The full CSV → FSR JSON spec (all rules in one place) is **[CSV_TO_FSR_JSON_MAPPING_SPEC.md](../../docs/CSV_TO_FSR_JSON_MAPPING_SPEC.md)** in `huddinge-package/docs/`. It uses the same rules as here and adds dependency-type logic (same-day ≤12 h vs spread 18 h+).

---

## 1. Purpose

- **Input:** Your CSV (e.g. *ATTENDO_DATABEHOV_PER_KUND_OCH_BESOK - data.csv*).
- **Output:** A JSON input to the route optimizer (visits, time windows, which visits belong together, and when they can be scheduled).
- **Goal:** One shared understanding of:
  - **When** each visit can happen (time windows),
  - **Which visits belong together** (same time, same frequency),
  - **How often** each visit occurs (recurrence).

---

## 2. Overview: what the CSV contains

### Columns we use

| CSV column | Purpose |
|------------|--------|
| Kundnr | Client id (e.g. H015); used for grouping and address. |
| Insats | Description (e.g. Tillsyn, Bad/Dusch); included in visit name. |
| Slinga | Route/round → vehicle; same Slinga = same vehicle. |
| Schift | Dag / Helg / Kväll → shift type and allowed days. |
| Återkommande | Frequency and weekdays → pinned days or flexible_day. |
| Dubbel | Same value = visit group (same time, same day). |
| När på dagen | Morgon / Lunch / Kväll → time slots; empty/other = full day. |
| Starttid | Preferred start time (HH:MM); used with Före/Efter. |
| Längd | Duration in minutes → serviceDuration. |
| Före, Efter | Minutes flex around start (0 = full slot). |
| Antal tim mellan besöken | Minimum gap between visits (same day or spread). |
| Kritisk insats Ja/nej | Ja = true, other/empty = false; used in pipeline (see 5.1). |
| Gata, Postnr, Ort | Address → geocoding to coordinates. |

The CSV has **107 rows** (visit descriptions). We expand to one occurrence per (row, date), then **one visit per (row, date)** — no deduplication (Morgon / Lunch / Kväll / Heldag). So if the CSV has several rows for the same customer and same “När på dagen” (e.g. 3 Lunch rows for H034), we keep one visit per matching day for that slot. That yields **1,486 visits** over 4 weeks (2026-03-02 – 2026-03-29).

> **Planning window:** We recommend **4 weeks** because the CSV contains visits with "Var 4:e vecka" (every 4 weeks) as the longest recurrence. A shorter window (e.g. 2 weeks) works but misses 4-week visits. The script auto-computes the planning window based on the longest recurrence in the CSV.

### 2.1 Clients and geography

| Key metric | Value |
|-----------|-------|
| **Clients** (unique Kundnr) | **15** (H015, H025, H026 … H053) — **test data: 15 of 81 Huddinge clients** |
| **Area** | Huddinge – Segeltorp, Stuvsta, Flemingsberg, Visättra, Central |

> **Test data:** This CSV contains only **15 of 81** clients’ visits. Result metrics from current runs (e.g. few visits per shift, lower field efficiency) may partly reflect the small dataset; with full Huddinge data (81 clients) we expect higher utilization per shift and better metrics. The mapping verification (time windows, Dubbel, dependencies) applies regardless.

### 2.2 Routes (Slingor) and shifts

The **Slinga** column indicates the route/team for the day. The **Schift** column indicates shift type.

| Shift | Number of routes | CSV rows | Allowed days | Typical time |
|-------|------------------|----------|--------------|------------|
| **Dag** (day) | 11 | 58 | Mon–Fri | 07:00 – 15:00 |
| **Helg** (weekend) | 9 | 27 | Sat–Sun | 07:00 – 14:30 |
| **Kväll** (evening) | 6 | 22 | All 7 days | 16:00 – 22:00 |
| **Total** | **26** | **107** | | |

> 26 routes ≈ 26 parallel routes. In practice it's not exactly 26 employees, since the same person may have a day-route one week and a weekend-route the next – but the optimizer treats them as separate routes.

### 2.3 Visit volumes

| Key metric | 2w window | 4w window (recommended) |
|-----------|-----------|-------------------------|
| **CSV rows** | 107 | 107 |
| **Expanded visits** | 744 | 1,486 |
| **Total planned time** | ~315 h | ~629 h |

**En kund kan ha flera rader med samma När på dagen:** Lunch = tidsfönster, inte insats. T.ex. H034 med Lunch + Bad/Dusch (mån tis tor) och Lunch + Måltid (mån–fre) ger två olika besök samma dag när dagarna överlappar (mån/tis/tor) — vi skapar **ett besök per (rad, datum)**.

**visit.id:** `kundid_r{rad}_{uträkning}` (t.ex. H034_r38_1). **visit.name:** `kundid När på dagen Skift Insatser` (t.ex. H034 Lunch Dag Bad/Dusch) så att insats(er) syns.

**Konfirmerat:**
- **Flera besök samma dag (olika rader)** — t.ex. H034 Lunch Bad/Dusch + Lunch Måltid — skickas till ruttoptimeringen som separata besök; optimeringen **planerar dem i följd** automatiskt med er konfig (samma fordon, ordning och tidsfönster).
- **En rad → flera besök över fönstret, men aldrig två på samma dag.** Pinnade rader: exakt ett besök per matchande datum. Flexible_day (solver väljer dag): N besök per period med **minDelay ≥ 18 h** (eller CSV "Antal tim mellan besöken") mellan besöken från samma rad så att de hamnar på **olika dagar** — oavsett om perioden är vardagar (mån–fre), helg (lör–sön) eller varje dag. **Fördröjningar under 24 h mellan sådana förekomster är felaktiga** (då kan de hamna samma dag). Dessa återkommande besök ska planeras med tidsfönster för **perioden** (t.ex. 1 vecka månd 07–fred 22 eller sönd 22 beroende på skift), med hänsyn till tid på dagen (Morgon/Lunch/Kväll), och minDelay minst 18 h. Scriptet kapar aldrig spridnings-minDelay under 18 h.

| **Average visit length** | 25 min | 25 min |
| **Group visits (Dubbel)** | 14 pairs (28 CSV rows) | 14 pairs (28 CSV rows) |

### 2.4 Recurrence patterns in the CSV

| Pattern (Återkommande) | Rows | Visits/week | Fixed/Solver? |
|------------------------|------|-------------|---------------|
| Varje vecka, mån tis ons tor fre | 26 | 5 | **Fixed** (pinned: exakt 5 besök/vecka, en per vardag) |
| Varje vecka, lör sön | 26 | 2 | **Fixed** (pinned: exakt 2 besök/vecka, lör + sön) |
| Varje dag | 13 | 7 | **Fixed** (all days) |
| Varje vecka, mån tis ons tor fre lör sön | 7 | 7 | **Fixed** (all 7 = daily) |
| Varje vecka, ons / mån / tis … | 10+ | 1 | **Solver picks** (1/vecka, vilken dag inom Skift) |
| Varannan vecka, tis / tor / fre / ons | 6 | 0.5 | Solver picks 1 day/2w |
| Varje vecka, tis fre / mån tor / mån ons fre … | 11 | 2–4 | **Solver picks** (N/vecka, solver väljer vilka N dagar) |
| Var 4:e vecka, mån / tis | 2 | 0.25 | Solver picks 1 day/4w |

---

## 3. When should the visit happen? (Time windows)

### 3.1 Rule: All visits have flex (time or day)

**Requirement:** Every visit must have either **time flex** (minStartTime ≠ maxStartTime on the same day) or **day flex** (multiple time windows or one window spanning several days/weeks). No visit may have exactly one window with minStartTime = maxStartTime (zero flex).

- **Före=Efter=0:** We always use the **full slot** (Morgon 07–10:30, Lunch 11–13:30, Kväll 16–19, Heldag 07–22). No exception.
- **Före/Efter filled:** Time window = start time ± före/efter. If the calculation ever yields min = max, we fall back to the slot bounds as a safeguard.

**Verification:** After building the input we run `_verify_all_visits_have_flex()` — if any visit has 0 flex we do not write JSON and the script exits with an error. You can also run `scripts/verify_all_visits_have_flex.py <input.json>` on an existing file.

### 3.2 Time of day: "När på dagen"

We map your **När på dagen** to three fixed time slots:

| När på dagen (CSV) | We interpret as | Time window (start–end) |
|--------------------|-----------------|--------------------------|
| Contains "morgon" | Morgon          | 07:00 – 10:30            |
| Contains "lunch"  | Lunch           | 11:00 – 13:30            |
| Contains "kväll"  | Kväll           | 16:00 – 19:00            |
| (empty) + Shift Dag   | Shift window   | 07:00 – 15:00 (Mon–Fri)  |
| (empty) + Shift Helg  | Shift window   | 07:00 – 14:30            |
| (empty) + Shift Kväll | Shift window   | 16:00 – 22:00            |
| (empty / other) no matching shift | Full day (free) | 07:00 – 22:00            |

Within the slot we adjust with **Starttid**, **Före** and **Efter** (e.g. Starttid 07:05, Före 0, Efter 120 → start window 07:05–09:05). For **empty När på dagen** with **Shift = Dag** we use the shift window 07:00–15:00 (e.g. H053 Inköp, Dag 14, weekly Mon → Mon–Fri 07–15). For empty + Helg/Kväll we use 07–14:30 and 16–22. Otherwise 07:00–22:00.

**Important: flexible_day visits (solver picks day):** If a visit has a period spanning multiple days (e.g. 1 week, 2 weeks) and a specific time slot (Morgon/Lunch/Kväll), we create **one separate time window per eligible day** in the period. This ensures the time-of-day rule applies regardless of which day the solver picks. Visits with full-day (07–22) or fixed days only need a single window.

**Examples from the CSV:**

| Kundnr | Service | När på dagen | Starttid | Före | Efter | → Time window |
|--------|---------|--------------|----------|------|-------|---------------|
| H015 | Tillsyn | Morgon | 07:05 | 0 | 120 | 07:05 – 09:05 (morning) |
| H029 | Måltid, Social Samvaro | Lunch | 11:00 | 0 | 120 | 11:00 – 13:00 (lunch) |
| H026 | Avklädning, Pers. Hygien Kväll | kvällen Dubbel | 19:40 | 15 | 15 | 19:25 – 19:55 (evening) |
| H026 | Städ | *(empty)* | 10:30 | – | – | 07:00 – 22:00 (full day) |
| H037 | Bad/Dusch | *(empty)* | 08:00 | 30 | 15 | 07:00 – 22:00 (full day) |

> Note: "Morgon Dubbel", "Lunch Dubbel", "kvällen Dubbel" are interpreted as morning/lunch/evening + Dubbel marking.

**Please confirm:** These windows are correct (morgon/lunch/kväll + full day 07–22 when the field is empty/other).

---

### 3.3 Which days: fixed vs "solver picks"

Whether the **day** is fixed or chosen by the optimizer depends on **Återkommande** and **Skift**:

#### Fixed days (pinned)

**Regel:** We pin only when the weekday set is **complete** (mån–fre, lör–sön, or all 7). Partial sets (e.g. mån tis tor) become flexible_day so the solver picks which N days.


**Pinned:**
- **"Varje dag"** → alla 7 dagar
- **"Varje vecka, mån tis ons tor fre"** → exakt 5 besök/vecka (en per vardag)
- **"Varje vecka, lör sön"** → exakt 2 besök/vecka (lör + sön)
- **"Varje vecka, mån tis ons tor fre lör sön"** → alla 7 = dagligt

#### Solver picks the day (flexible_day)

När veckodagarna är **partiella** (t.ex. "mån tis tor", "ons", "tis fre") eller **inga** veckodagar anges: solver väljer N dagar inom perioden (begränsat av Skift). Frekvensen (N besök/vecka) behålls; dagarna pinnas inte.

- **"Varje vecka"** (utan mån/tis/…) → 1 besök/vecka, solver väljer dag (begränsat av Skift)
- **Varannan / var 3:e / var 4:e vecka** (utan fasta dagar) → 1 besök per period, solver väljer dag

**Skift** restricts which days are allowed:

| Skift (CSV) | Allowed days   | Typical time range (shift) |
|-------------|----------------|----------------------------|
| Dag         | Mon–Fri only   | 07:00 – 15:00              |
| Helg        | Sat–Sun only   | 07:00 – 14:30              |
| Kväll       | All 7 days     | 16:00 – 22:00              |

**Examples from the CSV (4w window 2026-03-02 – 2026-03-29):**

| Kundnr | Service | Återkommande | Skift | → Interpretation | Visits/4w |
|--------|---------|--------------|-------|------------------|-----------|
| H015 | Tillsyn | Varje vecka, mån tis ons tor fre | Dag | **Fixed:** one visit every Mon–Fri | 20 |
| H015 | Tillsyn | Varje vecka, lör sön | Helg | **Fixed:** one visit every Sat + Sun | 8 |
| H015 | Tillsyn | Varje dag | Kväll | **Fixed:** one visit every day | 28 |
| H034 | Avklädning | Varje vecka, mån tis ons tor fre lör sön | Kväll | **Fixed:** all 7 days (= daily) | 28 |
| H027 | Bad/Dusch | Varje vecka, mån | Dag | **Solver picks:** 1/week, any weekday | 4 |
| H034 | Bad/Dusch | Varje vecka, mån tis tor | Dag | **Solver picks:** 3/week, any 3 weekdays | 12 |
| H015 | Städ | Varannan vecka, tis | Dag | **Solver picks:** 1/2w block, any weekday | 2 |
| H026 | Städ | Var 4:e vecka, mån | Dag | **Solver picks:** 1/4w block, any weekday | 1 |

**Note:** We pin only when the weekday set is **complete** (mån–fre, lör–sön, or all 7). When **partial** weekdays are given (e.g. "mån tis tor", "ons", "tis fre") the solver picks which N days within the period; we do not pin to those specific weekdays.

---

## 4. Which visits belong together?

### 4.1 Same time, same day: Dubbel (visit group)

- **CSV column:** **Dubbel**
- **Rule:** All rows with the **same Dubbel value** that end up on the **same date** are treated as one **visit group**.
- **Effect:** The optimizer must schedule them **at the same time** (same arrival window). Typical use: two carers for one client (dubbelbesök).

**Examples from the CSV:**

| Kundnr | Service | Dubbel | Slinga | Besökstyp | → Interpretation |
|--------|---------|--------|--------|-----------|------------------|
| H026 | Egenvård, Pers. Hygien Morgon… | **8** | Dag 14 ⭐ Stuvsta 2 | Hemtjänst | ↘ These two |
| H026 | Egenvård, Pers. Hygien Morgon… | **8** | Dag 11 ⭐ Snättringe | Dubbelbemanning | ↗ must happen **simultaneously** |
| H035 | Förflyttning | **2** | Kväll 03 ⭐ Visättra | Hemtjänst | ↘ These two |
| H035 | Toalettbesök | **2** | Kväll 02 ⭐ Kvarnen | Dubbelbemanning | ↗ must happen **simultaneously** |

> The CSV has **14 Dubbel groups**, all with exactly **2 rows** per group (= 2 carers for same client).

**Please confirm:** When Dubbel is set, you intend that those visits must happen together at the same time on the same day.

---

### 4.2 Order and minimum gap: "Antal tim mellan besöken"

- **CSV column:** **Antal tim mellan besöken**
- **Same-day chain (meals: breakfast → lunch):** Different rows (insatser) for the same customer, same day. We add a visitDependency from the previous slot (e.g. Morgon) to the next (e.g. Lunch) **only when** the later visit's row has "Antal tim mellan besöken" filled with a **short** value (≤ 12 h). We use that value **as-is** (e.g. PT3H30M); no subtraction. If it doesn't fit between the two visits' time windows we cap it (or remove the dependency). So breakfast comes before lunch with the requested gap.
- **Long delay = spread only (same insats):** If "Antal tim mellan besöken" is **long** (e.g. 48 h), we use it **only** between occurrences of the **same** insats (same row, flexible_day). We do **not** add a same-day dependency from other insats (e.g. lunch) to this one, so e.g. dusch (48 h) can be placed **directly next to** lunch; clustering is then via FSR weights.
- **Multiple visits per period (e.g. 3 showers per week):** When the solver picks the day and there are **several** visits per week/period for the same row, we add spread dependencies: if you specified "Antal tim mellan besöken" we use that (e.g. 48 h); otherwise **18 h** default (enough for different days; 24 h often makes lunch→lunch next day impossible) so they fall on different days.
- **One visit per period (e.g. 1× laundry per week):** No spread dependency is needed – there is only one visit to place. Only När på dagen and Skift (Morgon/Lunch/Kväll, Vardag/Kväll/Helg) constrain.
- **Effective delay for explicit intervals (24 h, 36 h, 48 h, etc.):** So that each following visit has the same preconditions as the first (can start at the start of its time window), we set **effective minDelay = interval − previous visit’s time-window length**. Example: interval 48 h, slot Morgon 07:00–10:30 (3.5 h) → effective delay = 48 h − 3.5 h = 44.5 h. That way, if the first visit ends at 10:30, the next can start at 07:00 two days later (no drift). This applies only to **spread**; same-day chains do **not** use this subtraction and use the CSV value as-is.

> For flexible_day with multiple visits per period we use 18 h default when the field is empty. Rows with "Antal tim" are used for spread (same insats only).

**One CSV row = one insats.** visitDependencies only between same insats (same row), flexible_day, multiple visits per period. Different insatser: no hard delay; clustering via FSR weights.

**Examples from the CSV:**

| Kundnr | Insats | Antal tim | Återkommande | → Interpretation |
|--------|--------|-----------|--------------|------------------|
| H026 | Bad/Dusch | 48 timmar | Varje vecka, tis fre | Spread (same insats): min 48 h between 2 showers/week |
| H038 | Bad/Dusch | 36 timmar | Varje vecka, mån tis fre | Spread (same insats): min 36 h between 3 showers/week |
| H015 | Tillsyn / Dusch | *(any)* | Varje vecka, mån–fre | No dependency between insatser; clustering by weights if desired |
| H029 | Tvätt | *(empty)* | Varannan vecka, tor | One visit per period — no dependency |

**Confirmed:** visitDependencies only between **same insats** (same row), **flexible_day**, multiple visits per period. Different insatser: no hard delay; clustering via FSR config weights.

---

### 4.3 Automated validations (automatic corrections)

We identified cases where **"Antal tim mellan besöken" is larger** than what fits between the time windows. In that case neither visit can be scheduled — the optimizer finds no valid time. We correct these automatically.

#### Problem: gap that doesn't fit

**Concrete examples from the CSV (H029, H034):**

| Kundnr | Visit 1 | Window 1 | → Gap → | Visit 2 | Window 2 | Problem |
|--------|---------|----------|---------|---------|----------|---------|
| H029 | Morning | 07:05 – 09:05 | 3.5 h | Lunch | 11:00 – 13:00 | Morning ends 09:05 + 30 min visit = 09:35. 09:35 + 3h30 = **13:05** → after lunch window closes (13:00). Visit cannot be scheduled! |
| H034 | Morning | 07:00 – 09:20 | 3.5 h | Lunch | 11:00 – 12:50 | Morning ends max 09:20 + 20 min = 09:40. 09:40 + 3h30 = **13:10** → after lunch window closes (12:50). Visit cannot be scheduled! |

**Our correction:**
- We compute the **maximum feasible gap** between the two visits' time windows.
- If the specified gap is too large, we **cap it** automatically (with 15 min margin).
- Example: H029 capped from 3h30 to **~1h46**, H034 from 3h30 to **~1h20**.
- If no gap at all fits (e.g. visits in the same window with long durations) the **dependency is removed** entirely.

> **Recommendation to Attendo:** Reduce "Antal tim mellan besöken" to max **2 hours** for same-day visits (Morgon → Lunch or Lunch → Kväll), so no automatic capping is needed. If no change is made, we still correct — it does not affect quality.

#### Problem: spread dependencies outside the planning window

Spread-over-days dependencies (e.g. 48 h between showers) are automatically clamped to fit within the planning window. If the chain's last visit falls outside the window, it cannot be scheduled. We shorten the chain so all visits fit.

#### Problem: spread delays mixed into same-day chain (fixed)

**Background:** Visits where the solver picks the day (flexible_day) have `date_iso` set to the period start (Monday), but the actual placement can be any day in the period. The "Antal tim mellan besöken" value (e.g. 36 h) specifies **spread between occurrences of the same visit type** (e.g. bath 1 → bath 2 → bath 3) — NOT the gap to a different visit type on the same day.

**The bug:** The script mixed flexible_day visits into the **same-day chain** (morning → lunch → evening) and used the spread value (36 h) as the gap to the preceding pinned visit. This created infeasible dependencies:

| Chain (before fix) | Problem |
|---|---|
| `H034_1` (pinned Mon 08:12) → `H034_2` (flex Mon–Fri, **PT36H!**) → ... → `H034_5` (pinned Mon 11:40) | 36 h delay forces bath visit to Wed+, but H034_5 requires it on Monday. |
| `H038_6` (flex) → `H038_7` (PT36H) → `H038_8` (PT36H) → `H038_9` (PT36H) with pinned lunch in chain | Same: spread constraint misinterpreted as same-day constraint. |
| `H053_1` (pinned Mon) → `H053_2` (flex, PT36H) → ... → `H053_5` (pinned Mon lunch) | Same: 36 h between morning and bath, but bath is flexible. |

**Fix:** Flexible_day visits are now **excluded from the same-day chain**. They only have **spread dependencies** (between their own occurrences, e.g. bath 1 → bath 2 → bath 3 with 36 h spacing). Pinned morning and lunch visits are still chained as before (with 3.5 h gap).

| Result (after fix) | |
|---|---|
| Spread dependencies (≥18 h, between same-type occurrences) | 48 |
| Same-day dependencies (morning → lunch, ≤ 3.5 h) | 188 |
| Total | **236** dependencies (down from 274 — 38 incorrect ones removed) |

We also added a **chain feasibility check**: if N visits with (N−1) delays + service time exceed the available window, the delay is automatically capped to the maximum feasible value (but never below 18 h, guaranteeing different days).

#### Problem: Zero Före/Efter with Morgon/Lunch/Kväll gave no slot flex – fixed

**Background:** Visits with **När på dagen = Morgon** (or Lunch/Kväll) and **Före=Efter=0** were interpreted as exact start time only (e.g. 07:09–07:09), so a weekly visit "any weekday morning" got 12 one-minute windows instead of the morning slot 07:00–10:30 per day. Correct interpretation: **morning = full morning slot** (07–10:30), i.e. flex 3.5 h × 5 weekdays = **17.5 h**.

**Fix:** When Före=Efter=0 and the visit has a **slot** (Morgon, Lunch, or Kväll), we now use the **full slot** as the time window:
- Morgon: 07:00–10:30 (max start 10:30 − duration)
- Lunch: 11:00–13:30 (max start 13:30 − duration)
- Kväll: 16:00–19:00 (max start 19:00 − duration)

So e.g. H029 Tvätt (1 min, Morgon, "Varannan vecka, tor") gets window **07:00–10:29** on each eligible day instead of 07:09–07:09.

---

## 5. How often? Recurrence (Återkommande)

We read **Återkommande** and derive:

1. **How many times** per week (or per 2/3/4 weeks) the visit should occur.
2. **Fixed days** vs **solver picks day**.

### Rules:

- **"Varje dag"** → one visit per calendar day (fixed, pinned).
- **"Varje vecka, mån tis ons tor fre"** → fixed weekdays, 5 per week (pinned).
- **"Varje vecka, lör sön"** → fixed weekend days, 2 per week (pinned).
- **"Varje vecka, mån tis ons tor fre lör sön"** → all 7 days = daily (pinned).
- **"Varje vecka"** (without weekdays) → **1 visit per week**, solver picks day within Skift (Mon–Sun). This is a fallback if future CSVs omit weekdays.
- **"Varje vecka, ons"** or **"Varje vecka, mån"** → 1 visit per week, solver picks best day within Skift.
- **"Varje vecka, mån ons fre"** or similar (2–4 days) → N visits per week, solver picks N days within Skift.
- **"Varannan vecka, tis"** → 1 visit per 2-week block, solver picks day.
- **"Var 3:e vecka"** → 1 visit per 3-week block.
- **"Var 4:e vecka, mån"** → 1 visit per 4-week block, solver picks day.

**Examples from the CSV (4w window 2026-03-02 – 2026-03-29):**

| Kundnr | Service | Återkommande (CSV) | Interpretation | Fixed/Solver? | Visits in 4w |
|--------|---------|--------------------|----|-------|------|
| H015 | Tillsyn | Varje dag | 1/day | Fixed: every day | **28** |
| H034 | Avklädning | Varje vecka, mån tis ons tor fre lör sön | 7/week | Fixed: all days | **28** |
| H029 | Måltid, Pers. Hygien… | Varje vecka, mån tis ons tor fre | 5/week | Fixed: Mon–Fri | **20** |
| H029 | Måltid, Social Samvaro | Varje vecka, lör sön | 2/week | Fixed: Sat–Sun | **8** |
| H034 | Bad/Dusch | Varje vecka, mån tis tor | 3/week | Solver picks 3 weekdays | **12** |
| H053 | Bad/Dusch | Varje vecka, mån ons fre | 3/week | Solver picks 3 weekdays | **12** |
| H038 | Bad/Dusch | Varje vecka, mån tis fre | 3/week | Solver picks 3 weekdays | **12** |
| H026 | Bad/Dusch | Varje vecka, tis fre | 2/week | Solver picks 2 weekdays | **8** |
| H027 | Bad/Dusch | Varje vecka, mån | 1/week | Solver picks 1 weekday | **4** |
| H037 | Bad/Dusch | Varje vecka, ons | 1/week | Solver picks 1 weekday | **4** |
| H015 | Städ | Varannan vecka, tis | 1/2w | Solver picks 1 weekday in 2w | **2** |
| H029 | Städ | Varannan vecka, tis | 1/2w | Solver picks 1 weekday in 2w | **2** |
| H026 | Städ | Var 4:e vecka, mån | 1/4w | Solver picks 1 weekday in 4w block | **1** |

### 5.1 Critical intervention (Kritisk insats Ja/nej)

We read the column **Kritisk insats Ja/nej**: **Ja** → true, empty or other → false. The value is used in our pipeline; we do not currently map it to a specific Timefold field (e.g. pinningRequested) but reserve it for future use. **Please confirm:** Should "Ja" mean the visit is to be pinned to the given day when applicable?

### 5.2 Planning window and longest recurrence

The script auto-computes the planning window:
- **Start:** Monday of the current week.
- **End:** Start + longest recurrence frequency in the CSV.
- **This CSV:** Longest = "Var 4:e vecka" → **28 days** (4 weeks).

If the window is set manually and is shorter than the longest recurrence, the script warns:
```
WARNING: planning window (14d) shorter than longest recurrence (28d). Recommend --end-date 2026-03-29
```

**Why 4 weeks:** With a 2-week window for 4-week visits (H026, H039 Städ), the visit gets a 14-day period to be placed within, even though it should occur every 4 weeks. With 4 weeks the period is correct: the visit is placed once within the full 4-week period.

---

## 6. Quick checklist

You can use this to tick off with your team:

- [ ] **När på dagen:** Morgon 07–10:30, Lunch 11–13:30, Kväll 16–19; empty/other = full day 07–22.
- [ ] **Skift:** Dag = Mon–Fri, Helg = Sat–Sun, Kväll = all days.
- [ ] **Dubbel:** Same value = same visit group = must be at same time, same day. (14 groups × 2 rows in the CSV.)
- [ ] **Antal tim mellan besöken:** Minimum delay between visits. Empty: same day = no gap; multiple visits/period = 18 h default (spread). One visit/period = no dependency. Same-day deps only when value ≤ 12 h (see **CSV_TO_FSR_JSON_MAPPING_SPEC.md**). We auto-correct if the specified gap doesn't fit (see section 4.3).
- [ ] **Återkommande:**
  - Fixed (pinned): "Varje dag", "mån tis ons tor fre", "lör sön", "mån tis ons tor fre lör sön".
  - Solver picks: all other patterns — we keep frequency but the solver picks days within Skift.
  - "Varje vecka" without weekdays → 1 per week (fallback).
- [ ] **Planning window:** Automatically 4 weeks (matches longest "Var 4:e vecka"). Start = Monday of current week.
- [ ] **Volume (4w):** ~1,486 visits, ~629 hours, 15 clients, 26 routes.

If you want to change any rule (e.g. different slot times or when to fix days), note it here and we'll align the conversion.

---

## 7. Outstanding questions

- **Can some visits get a freer "när på dagen"?** E.g. perhaps not meals, tillsyn, toilet, but maybe shower. That could yield more efficient schedules. Which visit types could use a full-day window (07–22) instead of morgon/lunch/kväll?
