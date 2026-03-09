# Why "dusch after morgon" exists — and correct pairing logic

## 1. Effect = same as one long visit (efficiency)

**Attendo rule:** "Dusch måste vara dikt med morgonbesöket" — dusch must be **right after** the morning visit (same day, same client).

**Effect:** The caregiver does morgon then dusch at the **same address**, so we **remove travel** between those two visits. That is **exactly the same as combining the two visits into one long visit** (morgon duration + dusch duration, same time window). So:

- Less travel, better field efficiency, care quality as per Attendo.

**If Timefold has issues with delay=0:** We can **merge** the two insatser into one long visit (one visit, duration = morgon + dusch, same time window) so the solver never sees two separate visits — same effect, no dependency.

---

## 2. Correct logic: pair by same client, återkommande dag, när på dagen + skift, and same time window

We must **not** add "dusch after morgon" just because there is *any* morgon and *any* dusch on (client, date). We must look at the **two separate visit insatser** (CSV rows) and only add delay=0 when:

- **Same client** (kundnr)
- **Same återkommande dag** (recurrence) — both rows expand to the same dates (e.g. same weekdays)
- **Same när på dagen och skift** (day slot and shift)
- **Starttid and före/efter** such that both visits fall **within the same time window** — i.e. their slot bounds (from starttid ± före/efter) **overlap**

Then they are a true pair: same care moment. Add precedingVisit dusch → morgon, minDelay PT0M (or combine into one long visit).

**Implementation (attendo_4mars_to_fsr.py):**

- Group occurrences by `(kundnr, date_iso, när_på_dagen, schift, recurrence_key)` where `recurrence_key = tuple(sorted(weekdays))` so only visits from the same recurrence pattern are grouped.
- In each group, for each dusch occurrence (insatser has bad/dusch, "Antal tim mellan" long): find a **morgon** occurrence in the same group whose **time window overlaps** the dusch's (via `_compute_slot_bounds` — starttid/före/efter). Only then add `preceding_map[dusch_visit_id] = (morgon_visit_id, "PT0M")`.

So we add the dependency only for **paired** morgon+dusch that share client, date, recurrence, day-slot, and overlapping time window — not for every dusch on a day that has any morgon.

---

## 3. What was wrong before (and what we fixed)

**Old (wrong) logic:** For each (client, date), if there is any morgon and any dusch with long "Antal tim mellan", add dusch → first_morgon PT0M. That tied **every** dusch that day to the **first** morgon, regardless of which row/recurrence/time window the dusch belonged to → too many deps, solver got 1364 unassigned.

**New (correct) logic:** Only add dusch → morgon PT0M when the two visits are a true pair: same client, same date, same recurrence (återkommande dag), same när på dagen + skift, and **time windows overlap** (starttid/före/efter). That should add far fewer dependencies (only the real morgon+dusch pairs, e.g. H035 and any other client where the two insatser share the same slot).

---

## 4. Optional: combine to one long visit for delay=0

If the solver still struggles with delay=0 dependencies, we can **merge** the two visits into one:

- One visit per (client, date) with duration = morgon_längd + dusch_längd, time window = overlap or morgon window extended by dusch length.
- No visitDependency; same travel reduction, no constraint for the solver to satisfy.
