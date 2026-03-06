# How recurring visits (Återkommande) are handled

**Team verification:** For a short, Attendo-friendly explanation of how we map CSV → input (time windows, which visits belong together, recurrence), see **CSV_TO_INPUT_VERIFICATION.md** in this folder.

## Summary

- **CSV column:** `Återkommande`
- **Distinct values in 4mars CSV:** **24**
- **Derived recurrence types in code:** **5** — `daily`, `weekly`, `biweekly`, `3weekly`, `4weekly`

Weekdays in the text (mån, tis, ons, …) are parsed; for **weekly** we also decide whether to **pin** to those days or let the **solver pick** days (flexible_day).

---

## Recurrence type detection (`_recurrence_type`)


| CSV contains            | Recurrence type |
| ----------------------- | --------------- |
| "varje dag"             | `daily`         |
| "varannan vecka"        | `biweekly`      |
| "4:e vecka" / "var 4:e" | `4weekly`       |
| "3:e vecka" / "var 3:e" | `3weekly`       |
| else                    | `weekly`        |


---

## Weekday parsing (`_parse_weekdays_from_atterkommande`)

- Looks for Swedish weekday tokens: mån, tis, ons, tor, fre, lör, sön (and long forms).
- Returns a sorted list of Python weekdays `0–6` (Mon–Sun), or `None` for "varje dag", "varannan", "4:e vecka", "3:e vecka" (those are handled by recurrence type only).

---

## Pin vs solver-picks (`_should_pin_weekdays`)

Only for **weekly** with weekdays:

- **Pin (fixed days):**  
  - All weekdays: `{0,1,2,3,4}` (mån–fre)  
  - Both weekend: `{5,6}` (lör sön)  
  - All 7 days: `{0,1,2,3,4,5,6}` (mån–sön = functionally daily)  
  - Daily recurrence is always pinned to every day.
- **Solver picks (flexible_day):**  
Any other weekday set (e.g. "mån tis ons", "tis fre", "mån", "ons", "Var 4:e vecka mån", "Varannan vecka tis").

---

## Expansion behaviour (`_expand_row_to_occurrences`)


| Recurrence   | Weekdays / condition                     | Behaviour                                                                                                                                                                                        | Occurrences (2-week window example) |
| ------------ | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------- |
| **daily**    | —                                        | One occurrence per calendar day in window.                                                                                                                                                       | 14                                  |
| **weekly**   | weekdays + **pin** (mån–fre or lör sön)  | One occurrence per date where `date.weekday()` in weekdays.                                                                                                                                      | e.g. 10 for mån–fre, 4 for lör sön  |
| **weekly**   | weekdays + **solver picks**              | N occurrences per week (N = len(weekdays)), `flexible_day=True`, period = week (restricted by skift: Dag→Mon–Fri, Helg→Sat–Sun, Kväll→all days). Spread deps: Antal tim mellan besöken or PT18H. | e.g. 3/week → 6 in 2 weeks          |
| **weekly**   | no weekdays                              | One `flexible_day` occurrence per week, period = week (Mon–Sun, restricted by skift). Solver picks 1 day.                                                                                       | 4 (in 4-week window)                |
| **biweekly** | (single weekday in text ignored for pin) | One occurrence per 2-week block, `flexible_day=True`, period = 2 weeks (restricted by skift).                                                                                                    | 1                                   |
| **4weekly**  | same                                     | One occurrence per 4-week block, `flexible_day=True`, period = 4 weeks.                                                                                                                          | 1 in a 2-week window                |
| **3weekly**  | same                                     | One occurrence per 3-week block, `flexible_day=True`, period = 3 weeks.                                                                                                                          | 1 in a 2-week window                |


---

## The 24 distinct Återkommande values in the 4mars CSV


| #   | CSV value                                | Recurrence | Weekdays parsed | Pin?                | Handling                           |
| --- | ---------------------------------------- | ---------- | --------------- | ------------------- | ---------------------------------- |
| 1   | Varje vecka, mån tis ons tor fre         | weekly     | [0,1,2,3,4]     | Yes (all weekdays)  | One occ per Mon–Fri in window      |
| 2   | Varje vecka, lör sön                     | weekly     | [5,6]           | Yes (weekend)       | One occ per Sat–Sun in window      |
| 3   | Varje dag                                | daily      | —               | —                   | One occ per day in window          |
| 4   | Varje vecka, mån tis ons tor fre lör sön | weekly     | [0,1,2,3,4,5,6] | Yes (all 7 = daily) | One occ per day in window          |
| 5   | Varje vecka, ons                         | weekly     | [2]             | No                  | 1 flexible_day per week            |
| 6   | Varje vecka, mån                         | weekly     | [0]             | No                  | 1 flexible_day per week            |
| 7   | Varannan vecka, tis                      | biweekly   | —               | —                   | 1 flexible_day per 2-week block    |
| 8   | Varje vecka, tor                         | weekly     | [3]             | No                  | 1 flexible_day per week            |
| 9   | Varje vecka, tis fre                     | weekly     | [1,4]           | No                  | 2 flexible_day per week            |
| 10  | Varje vecka, mån tor                     | weekly     | [0,3]           | No                  | 2 flexible_day per week            |
| 11  | Varje vecka, lör                         | weekly     | [5]             | No                  | 1 flexible_day per week (Sat only) |
| 12  | Varje vecka, fre                         | weekly     | [4]             | No                  | 1 flexible_day per week            |
| 13  | Varje vecka, mån tis ons fre             | weekly     | [0,1,2,4]       | No                  | 4 flexible_day per week            |
| 14  | Var 4:e vecka, mån                       | 4weekly    | —               | —                   | 1 flexible_day per 4-week block    |
| 15  | Varannan vecka, tor                      | biweekly   | —               | —                   | 1 flexible_day per 2-week block    |
| 16  | Varannan vecka, fre                      | biweekly   | —               | —                   | 1 flexible_day per 2-week block    |
| 17  | Varje vecka, mån tis tor                 | weekly     | [0,1,3]         | No                  | 3 flexible_day per week            |
| 18  | Varannan vecka, ons                      | biweekly   | —               | —                   | 1 flexible_day per 2-week block    |
| 19  | Varje vecka, mån tis ons tor             | weekly     | [0,1,2,3]       | No                  | 4 flexible_day per week            |
| 20  | Varje vecka, fre lör sön                 | weekly     | [4,5,6]         | No                  | 3 flexible_day per week            |
| 21  | Varje vecka, mån tis fre                 | weekly     | [0,1,4]         | No                  | 3 flexible_day per week            |
| 22  | Varje vecka, tis tor                     | weekly     | [1,3]           | No                  | 2 flexible_day per week            |
| 23  | Var 4:e vecka, tis                       | 4weekly    | —               | —                   | 1 flexible_day per 4-week block    |
| 24  | Varje vecka, mån ons fre                 | weekly     | [0,2,4]         | No                  | 3 flexible_day per week            |


---

## Visit dependencies (no loops)

- **Same-day chain:** For each (kundnr, date_iso), **pinned** visits only, ordered by slot (Morgon→Lunch→Kväll) and starttid. A visit gets a `visitDependency` on the previous **only if** the **current** visit's row has "Antal tim mellan besöken" set **and** the value is **≤ 12 hours** (e.g. 3.5h for breakfast→lunch). The **minDelay** used is the CSV value as-is (e.g. PT3H30M); no subtraction. Long values (18h, 24h, 48h) are used only for spread (same row); no same-day dep is added for those, so e.g. shower can sit next to lunch. Skipped when both visits are in the same **visit group** (Dubbel) or in the same **flexible_day (row, period)** (spread deps define order there).
- **Spread:** For each flexible_day (row, period) with ≥2 visits, consecutive visits get a dependency (prev → next) with minDelay = "Antal tim mellan besöken" or **PT18H**. Skipped when both visits are in the same **visit group** (avoids Timefold "loops not allowed"). See **../../docs/CSV_TO_FSR_JSON_MAPPING_SPEC.md** for full rules.

---

## Vilka besök får startfönster över flera dagar/veckor?

Endast besök med **flexible_day** får ett startfönster (minStartTime–maxStartTime) som sträcker sig över **flera dagar eller veckor**. Optimeraren väljer sedan *vilken dag* inom perioden.

| Återkommande (typ) | Period (startfönster) | Kommentar |
|--------------------|------------------------|-----------|
| **Weekly, solver picks** (t.ex. "Varje vecka, ons", "Varje vecka, mån tis fre") | **1 vecka** (5, 2 eller 7 dagar) | Begränsat av Skift: Dag → mån–fre, Helg → lör–sön, Kväll → alla 7. |
| **Biweekly** (varannan vecka) | **2 veckor** (14 dagar) | Samma Skift-begränsning. |
| **3weekly** (var 3:e vecka) | **3 veckor** (21 dagar) | Samma Skift-begränsning. |
| **4weekly** (var 4:e vecka) | **4 veckor** (28 dagar) | Samma Skift-begränsning. |

**Får *inte* flerdags-/flerveckorsfönster (endast en dag):**

- **Varje dag** → ett besök per kalenderdag, fast datum.
- **Varje vecka, mån–fre** eller **Varje vecka, lör sön** (pin) → ett besök per fast datum (mån–fre resp. lör–sön).
- **Varje vecka** utan veckodagar i texten → ett besök per kalenderdag i fönstret (ingen flexible_day).

---

## När på dagen (time-of-day slot)

- **Morgon** → 07:00–10:30, **Lunch** → 11:00–13:30, **Kväll** → 16:00–19:00.
- **Tomt eller annat** → inget snävt fönster: **heldag 07:00–22:00** (`SLOT_HELDAG`). Används t.ex. för besök med långa flexibla perioder (14 d, 4 v). Starttid/Före/Efter används inte för heldag.

---

## Outstanding questions

- When can we use larger time windows? Today we only allow free **day** when recurrence is not daily, not “varje vardag”, and not “lör sön” (flexible_day). Confirm current behaviour.
- Can some visit types (e.g. dusch) get full-day window (07–22) instead of morgon/lunch/kväll for more efficient schedules? (Not meals, tillsyn, toilet?)

---

## Code references

- `_recurrence_type()` — `attendo_4mars_to_fsr.py` ~254
- `_slot_for_nar_pa_dagen()` — returns `SLOT_HELDAG` ("07:00", "22:00") when När på dagen is empty or other
- `_parse_weekdays_from_atterkommande()` — ~234
- `_should_pin_weekdays()` — ~270
- `_expand_row_to_occurrences()` — ~337
- `_flexible_period_restrict_to_shift()` — ~299 (Dag→Mon–Fri, Helg→Sat–Sun, Kväll→all days)

