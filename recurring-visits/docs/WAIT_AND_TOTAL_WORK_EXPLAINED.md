# Solution metrics: single definition (10-mars reference)

One set of rules. Break is **not** included in any metric.

---

## 1. How break and wait are calculated (your example)

**Break** comes from the itinerary: each `kind: "BREAK"` item has `startTime` and `endTime`. For your shift, item 5 is the break:

- **Break:** 10:11:31 → 10:41:31 = **30 min** (this is `totalBreakDuration: "PT30M"`).

**Wait** is, for each visit: time from `arrivalTime` to `startServiceTime`, **minus** any part of that interval that overlaps a BREAK.

For **visit 6 (H055_r119_2)**:

- Arrival: 10:11:31, start of service: 11:00:00 → raw “wait” = **48 min 29 s**.
- The break 10:11:31–10:41:31 (30 min) lies entirely inside that interval.
- So **wait for this visit (excl. break)** = 48m29s − 30m = **18 min 29 s**.

So the solver does **not** count the 30 min of break as wait. It reports **totalWaitingTime: "PT55M57S"** for this shift = sum over all visits of (startServiceTime − arrivalTime), with break overlap subtracted. That 55m57s is the “Väntar” time you see in the UI for this shift (excluding break).

**Summary for this shift:**

- **Break** = 30 min (from itinerary; same as `totalBreakDuration`).
- **Wait (excl. break)** = 55 min 57 s = `totalWaitingTime`.
- Break is **not** included in wait; wait is **only** the non-break part of arrival→service intervals.

---

## 2. How we define “shift” and the equation

- **Shift time (excl. breaks)** = assignable time = **visit + travel + wait**. So: shift (excl. break) = visit + travel + wait.
- **Break** = from itinerary (e.g. 30 min per shift). Reported as **info only**; not part of visit/travel/wait or utilization.

So:

```text
shift (excl. break) = visit + travel + wait
```

**Wait** is taken from the output: sum of each shift’s `totalWaitingTime` (already excl. break). That sum is **174 h** and matches the “Väntar” you see in the UI. So we use **one** wait number: **174 h**.

---

## 3. The one set of numbers (10-mars run)

| Metric | Value | Notes |
|--------|--------|--------|
| **Visit time** | 1600 h 2 m | From output (`totalServiceDuration` sum). |
| **Travel time** | 481 h 29 m | From output (`totalTravelTime` sum). |
| **Wait time (excl. breaks)** | **174 h 23 m** | From output: sum of each shift’s `totalWaitingTime`. Matches UI “Väntar”. Break is **not** included. |
| **Shift time (excl. breaks)** | **2255 h 54 m** | visit + travel + wait. Same as “Total arbetstid”. Use this as **shift** for field hours. |
| **Field hours** | **2082 h** | shift − wait = 2256 − 174 = **visit + travel** (no wait). |
| **Break time** | 127 h 30 m | Info only; not included in metrics above. |
| **Visit-span** (do not call “Total shift”) | 2225 h 1 m | First visit start → last visit end, summed; excludes depot legs. Label “Aktivt spann”. |
| **Utilization / efficiency** | **70,9%** (standard) | visit / (visit + travel + wait) = 1600 / 2255. UI 76,3% uses visit-span − break; see below. |
| **Travel efficiency ratio** | **76,9%** | visit / (visit + travel), **wait removed**. Same as field efficiency; use for revenue-relevant efficiency. |

So:

- **Shift time (excl. breaks)** = wait + travel + visit = **2255 h 54 m**
- **Wait time (excl. breaks)** = **174 h 23 m** (from output; matches UI)
- **Travel time** = 481 h 29 m  
- **Visit time** = 1600 h 2 m  
- **Efficiency** = visit / shift (excl. break) = **70,9%**
- **Break time** = 127 h 30 m (info only, not in metrics)

We use the solver’s **totalWaitingTime** sum (**174 h**) for wait. It is wait only (break overlap is already excluded per shift). The UI’s “Väntar” blocks and total wait correspond to this.

**Outside the visit-span**, (travel+wait) = **158 h**: ~119 h depot travel (included in 481 h total travel) + **~39 h wait** (before first visit or after last visit). So **wait outside span = ~39 h**. The remaining **~135 h wait** is **inside** the span (at/between visits — early arrival at clients). See §3c.

So the 481.5 h total travel **already includes** depot legs; there is no double-count. The 158 h is not “extra” travel—it is (119 h travel from 481 h + 39 h wait from 174 h) that lies outside the visit-span.

**Why 2256 − 2225 ≠ 158 h.** Total arbetstid = 2256 h, visit-span = 2225 h, so **2256 − 2225 = 31 h** (not 158 h). That 31 h = (work outside span) − break = 158 h − 127.5 h.

---

## 3a. Minute-by-minute accounting (every minute accounted for)

All in hours (10-mars). So every minute adds up.

| Component | Hours | Where it sits |
|-----------|--------|----------------|
| **Visit** | 1600.03 | All inside visit-span. |
| **Break** | 127.5 | All inside visit-span. |
| **Travel** | 481.48 | Inside span: 362.4 (between visits). Outside: 60.8 + 58.3 ≈ 119 (depot legs). |
| **Wait** | 174.38 | **Inside span: ~135 h** (at/between visits). **Outside span: ~39 h** (before first / after last visit). |

**Inside the visit-span (2225 h):** Visit 1600 + Break 127.5 + (Travel+wait) inside = 2225 ⇒ (Travel+wait) inside = **497.5 h**. Travel inside (between visits) = 362.4 h ⇒ **wait inside span = 497.5 − 362.4 = 135.1 h**. So **wait outside span** = 174.4 − 135.1 = **39.3 h**.

**(Travel+wait) outside span** = (481.48 + 174.38) − 497.5 = **158.4 h** = ~119 h depot travel + ~39 h wait. So **158 h is not “wait before/after”** — it is **depot travel (119 h) + wait before/after (39 h)**.

**Check:** 2255.9 − 2225 = 30.9 h = 158.4 − 127.5 ✓ So **2256 − 2225 = 31 h**; **158 h** is the (travel+wait) outside the span.

**Depot → depot (excl. break) = shift time.** Clock from leave depot to return depot = visit-span (2225) + (travel+wait) outside span (158) = 2383 h; minus break (127.5) = **2256 h**. So shift time and depot-to-depot (excl. break) are the same; no depot wait, no buffer.

---

## 3b. Travel efficiency ratio and field efficiency (wait removed)

**Travel efficiency ratio** = **visit / (visit + travel)** ≈ **76,9%**. Same as field efficiency: **wait is excluded** from the calculation. So it answers: of the time spent on visit + travel (revenue-generating travel + service), what share is visit?

- Formula: **visit / (visit + travel)** = 1600 / (1600 + 481) ≈ **76,9%**.
- Use this in the UI as the main “efficiency” that excludes waiting (and breaks). Keep wait as a separate metric for buffer / contingency.

---

## 3c. Wait split: where wait actually is (business insight)

**Correct split (10-mars):**

| Wait | Hours | Where |
|------|--------|--------|
| **Wait inside span** | **~135 h** | At/between visits (arriving early at clients; waiting for time window to start). |
| **Wait outside span** | **~39 h** | Before first visit (after leaving depot) or after last visit (before returning). |

So it is **not** “158 h wait before/after.” The **158 h** is **(travel + wait) outside the span** = 119 h depot travel + 39 h wait. **Wait before/after visits = ~39 h.** **Wait at/between visits (inside the span) = ~135 h.**

**Insight for time windows:** Most wait (**~135 h**) is **inside** the visit span — i.e. at the client or between visits, where staff arrive before the visit time window and stand still. Only ~39 h is outside (depot legs). So **adjusting visit time windows and sequencing has the biggest lever on the 135 h** of “at-door” wait. Reducing that (tighter or shifted windows, less early arrival) directly improves revenue share; wait is no revenue (and no revenue for travel or breaks). At ~174 h total wait vs 2256 h total arbetstid, wait is **~7,7%** of paid time; vs 1600 h visit time, wait is **~10,9%** “lost” relative to service — in that ballpark as a **~5–11%** efficiency loss from wait if not optimized.

---

**Shift hours: 2225 or 2256? Depot start to depot end (minus breaks)**

- **Shift time = 2256 h** = **depot → depot (excl. breaks)**. There is no waiting at depot and no buffer in config, so clock time from leave depot to return depot (minus break) = visit + travel + wait = **2256 h**. So **one shift number**: **2256 h**.
- **2225 h 1 m** = **visit-span** only: sum over shifts of (last visit end − first visit start). It **excludes** the (travel+wait) outside the span (158 h = depot legs + wait before/after). So 2225 is **not** depot-to-depot. Label it **“Aktivt spann” (visit-span)** in the UI, not “Total shift”.
- **2256 h** = **Total arbetstid** = visit + travel + wait = **shift (depot to depot, excl. break)**. Use this as **shift** for field hours and utilization.

**Field hours** = **shift time − wait time (174 h)** = 2256 − 174 = **2082 h** = visit + travel.

---

**What is "Total shift" 2225 h 1 m and why 70,9% vs 76,3%?**

- **2225 h 1 m** (currently “Total shift” in the UI) = **visit-span** summed over all shifts with visits: per shift, (last visit end − first visit start). So it is the "active window" from first visit to last visit; it does **not** include depot travel or wait before/after that window. In the backend this is `shiftMinutes` from `computeTimefoldMetricsFromOutput` (C_field_time). **Label it “Aktivt spann” or “Visit-span”**, not “Total shift”.
- **70,9%** = visit / (visit + travel + wait) = 1600 / 2255 = share of **working time** (Total arbetstid) that is visit. This is the **standard** utilization in vehicle routing.
- **76,3%** = visit / (2225 − 127.5) = visit / (visit-span − break). The UI currently stores this (from `assignableMinutes = shiftMinutes - breakMinutes` in `applyTimefoldPayloadToSolution.ts`). So 76,3% uses the smaller denominator (active span minus break), hence higher.
- **Recommendation:** use **70,9%** as the main "Utnyttjande" (visit / Total arbetstid). If the span-based value is kept, label it e.g. "Utnyttjande (aktivt spann)".

**Travel breakdown (from API):** totalTravelTime 481 h 29 m = travelTimeFromStartLocationToFirstVisit (60 h 50 m) + travelTimeBetweenVisits (362 h 22 m) + travelTimeFromLastVisitToEndLocation (58 h 17 m). Depot legs ≈ 119 h are included in the 481.5 h total.

---

## 4. Idle employees (e.g. “Helg_10_  0  2 h  0 m  0,0%”) — should not be in metrics

A row like **Helg_10_  0  2 h  0 m  0,0%** is an **idle employee**: 0 visits, some shift time (e.g. 2 h from a weekend “Helg” shift with no assignments), 0% utilization.

**They should not be included in employee metrics.** Many inactive/idle employees are already excluded from employee metrics; the same rule should apply here: only employees with at least one visit (or only “active” employees) should appear in the metrics list and counts. If Helg_10_ (or any 0-visit employee) appears in the metrics, that’s inconsistent and should be fixed so idle employees are excluded, same as other inactive employees.

---

## 5. What to implement (dashboard / backend)

- **Shift time (excl. breaks)** = visit + travel + wait = **2255 h 54 m** (same as Total arbetstid; we only need one label).
- **Wait time (excl. breaks)** = sum of each shift’s `totalWaitingTime` = **174 h 23 m**. Break is **not** included (solver already excludes break overlap per shift).
- **Travel time** = from output (481 h 29 m).
- **Visit time** = from output (1600 h 2 m).
- **Shift efficiency** = visit / shift (excl. break) = 1600 / 2255 ≈ **70,9%**.
- **Field/travel efficiency (highlight)** = **visit / (visit + travel)** ≈ **76,9%**. Excl. breaks, idle, wait. (This is the revenue-relevant efficiency; wait is buffer only.)
- **Break time** = from output (127 h 30 m), **info only**; not included in shift time, wait, or efficiency.

One definition, one wait number (174 h from output), break only as info.

---

## 6. Bug report for metrics UI (dev)

**Summary:** Metrics labels and formulas need to match the definitions below so every minute adds up and the right efficiency is highlighted.

**Facts (10-mars reference):**

- **2256 − 2225 = 31 h** (not 158 h). Total arbetstid = 2256 h, visit-span = 2225 h. The 31 h = (work outside span) − break = 158 − 127.5.
- **158 h** = (travel+wait) **outside** the visit-span = ~119 h depot travel + ~39 h wait. **Wait outside span = ~39 h**, not 158 h. **Wait inside span** (at/between visits) = **~135 h** — that’s where visit time windows drive early arrival and lost revenue.
- **Travel efficiency ratio** = **visit / (visit + travel)** ≈ 76,9% (wait removed). Same as field efficiency; use as the main revenue-relevant efficiency. Wait is buffer only; no revenue for wait/travel/break.

**Ask for:**

1. **Label 2225 h 1 m** as **“Aktivt spann” (visit-span)** — first visit start → last visit end, summed; **not** “Total shift”. **Shift time** = **2256 h** = depot → depot (excl. break) = total arbetstid (visit+travel+wait). **Field hours** = shift − wait = **2082 h** = visit + travel.
2. **Primary utilization:** Use **visit / (visit + travel + wait)** = 70,9% as main "Utnyttjande" (or label current 76,3% as "Utnyttjande (aktivt spann)" and add 70,9% as "Utnyttjande (arbetstid)").
3. **Travel efficiency ratio / field efficiency:** Add and emphasize **Reseffektivitet** or **Fälteffektivitet** = **visit / (visit + travel)** ≈ 76,9%, **wait excluded**. Same formula; use for revenue-relevant efficiency. Wait shown separately as buffer.
4. **Exclude idle employees** (0 visits) from employee metrics list, same as other inactive employees.
5. **Minute-by-minute consistency:** Ensure stored/displayed totals satisfy: total arbetstid = visit + travel + wait; 2256 − 2225 = 31 h; 158 h = work outside span (119 h travel + 39 h wait).
