# Visit count (3457 vs 3697) and H035 dusch

**Timefold is source of truth.** The notes below align with the FSR model: visits in groups are only in `visitGroups[].visits`, not in top-level `visits`. There is no double counting in Timefold.

---

## Reference inputs (2-week window 2026-03-02 → 2026-03-15)

| File | Vehicles | Shifts | Visits | In groups | Notes |
|------|----------|--------|--------|-----------|--------|
| `9march/xtra-shifts/export-field-service-routing-v1-cece06c0-...-input.json` | 46 | **448** | 3,457 | 240 | cece06c0 run (0 unassigned except 2× H035 dusch) |
| `9march/less-shifts/export-field-service-routing-v1-5d66cc1c-...-input.json` | 46 | **544** | 3,457 | 240 | 5d66cc1c run (more shifts) |
| `fsr_input_81_2w.json` | 46 | **544** | 3,457 | 240 | Pipeline 2w (Attendo CSV → FSR, with dusch fix in script) |

Same visit structure (3457 standalone + 240 in 116 groups = 3,697 total). Only difference between these inputs is **shift count** (448 vs 544).

---

## How visit count works (3457 vs 3697)

- **`modelInput.visits`**: only **standalone** visits (not in any group). Our script puts a visit either in `visits` or in a visit group, never both. So **3,457** = count of standalone visits.
- **`modelInput.visitGroups`**: **116** groups (Dubbel). Each group has a `visits` array; those visits exist **only** in the group (multi-vehicle: same logical job, 2 vehicles, overlapping at same location). Total visit objects inside groups = **240**.
- **Total visit entities** in the problem = 3,457 + 240 = **3,697**. The Timefold UI shows 3,697 because that is the total number of visit entities (standalone + group members). Each visit is counted once; there is no double counting in Timefold.

So: **3697 = 3457 (standalone) + 240 (in groups)**. Group visits are unique and appear only under `visitGroups[].visits`, not in `modelInput.visits`.

---

## H035: visit group (Dubbel 6), and why it’s unassigned

The two DUSCH!! rows (Snättringe 10:30, Central 2 10:35) are **one** logical visit — a **visit group** (Dubbel id 6): two overlapping visits at the same location, served by two vehicles. So it’s one group with 2 visits, not two separate standalone visits.

Attendo: **“H035 dusch måste vara dikt med morgonbesöket”** — shower must be tied to (same day as, directly after) the morning visit.

### Likely problem: time window vs start time

- **Morgon** slot (när på dagen) = 07:00–**10:30**.
- Dusch row: Starttid **10:30**, Längd **20** min → visit ends at **10:50**.
- So the **end time** of the dusch visit (10:50) is **outside** the Morgon slot (which ends 10:30). With current logic we derive the dusch time window from the Morgon slot and length, so a 20‑min visit must **start** by 10:10 to end by 10:30. That forbids starting at 10:30 and can make the group unassignable.

So the issue can be: **day slot is Morgon 07–10:30, but the 20‑min visit starting at 10:30 ends at 10:50, i.e. outside “när på dagen”.**

### Intended care sequence

- **10:15** 20‑min visit (Morgon, e.g. personlig hygien) → ends 10:35.
- **10:30** shower (dusch) should follow **directly** after that morgon visit → e.g. **minDelay PT0M** from Morgon to Dusch.

So we want: **Morgon (10:15, 20 min) → Dusch (10:30)** with **delay 0** dependency in FSR.

### 42h / 48h: between shower days, not same‑day

- **“42 timmar”** (Antal tim mellan besöken) should apply **between the two shower occurrences** (e.g. Monday and Thursday), i.e. **spread** between days, not between same‑day different insats (morgon vs dusch).
- Same‑day we only need: **Morgon → Dusch** with **minDelay PT0M** (or a very short delay). That is supported by Timefold FSR visit dependencies.

### Suggested fix in the script

1. **Same-day dependency**  
   For H035 (and similar “dusch dikt med morgon”): add **Morgon → Dusch** with **minDelay PT0M** (dusch starts ≥ 0 after preceding morgon; solver can place 10:15 morgon then 10:30 dusch).

2. **Time window for dusch**  
   Either:
   - Extend the dusch visit’s time window so that a 10:30–10:50 (or 10:35–10:50) window is allowed (e.g. allow end time after Morgon slot end when “dikt med morgon”), or  
   - Use Starttid 10:30 (and 10:35) with a small Före/Efter so the window explicitly allows 10:30–10:50, and rely on the Morgon→Dusch PT0M dependency to order them.

3. **42h only for spread**  
   Keep using “42 timmar” only for **spread** between dusch occurrences (e.g. occurrence 1 on Monday, occurrence 2 on Thursday), not for same‑day Morgon vs Dusch.

Once Morgon→Dusch has a PT0M dependency and the dusch window allows 10:30 (and 10:35), the visit group should be assignable on the same day as the morning visit.

---

## Why this was the only failure (edge case)

- **Visit group**: Both dusch visits must be assigned together (same group, two vehicles). If the solver can’t satisfy the group (e.g. no valid time window + dependency combo), the whole group stays unassigned. Other visits are standalone, so they don’t have this “all-or-nothing” behaviour.
- **Time window vs dayslot**: With Före/Efter=15 the dusch window already allows 10:30–10:45 start. The main issue was the **missing same-day constraint**: without “dusch after morgon” (PT0M), the solver wasn’t told to place dusch on the same day as morgon, so the visit group could be left unassigned.
- **Long delay (42h)**: “42 timmar” is only used for **spread** (between dusch occurrences). The script previously added no same-day dependency when delay > 12h, so dusch never got “after morgon” on the same day.

**Fix applied in script:** For each (client, date), if an occurrence is Bad/Dusch with long delay (e.g. 42h) and has no preceding yet, we add `precedingVisit` = first Morgon visit on that day, `minDelay` = `PT0M`. Visit group counting is unchanged (standalone vs group-only); the pipeline output continues to report standalone + group visits correctly.
