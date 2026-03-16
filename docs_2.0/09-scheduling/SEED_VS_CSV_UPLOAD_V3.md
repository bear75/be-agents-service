# Seed vs CSV Upload vs v3 Python Pipeline

Alignment between **seed-attendo.ts**, **dashboard CSV upload** (importAttendoSchedule + AttendoAdapter), and the **be-agent-service v3 Python pipeline** (attendo_4mars_to_fsr.py, verify_csv_to_json.py).

---

## Three time-window cases (with examples)

These rules determine the **allowed time window** for a visit (minStartTime–maxEndTime in FSR, or `allowedTimeWindowStart`/`allowedTimeWindowEnd` in the DB).

### 1. Exakt dag/tid — exact time, no flex

**Meaning:** The visit must happen exactly at the given **Starttid** on the **Återkommande** day. No flexibility.

**CSV signal:** "När på dagen" contains **"Exakt"** (e.g. "Exakt dag/tid").

**Example:**

| När på dagen  | Starttid | Före  | Efter | Intended window     |
| ------------- | -------- | ----- | ----- | ------------------- |
| Exakt dag/tid | 07:20    | (any) | (any) | 07:20–07:21 (1 min) |

**Python v3:** Uses an EXACT slot (1‑min flex so validation passes).  
**Dashboard:** "Exakt" in När på dagen → exact window (Starttid to Starttid + max(duration, 1 min)).

---

### 2. Empty/null Före and Efter — full flex from När på dagen + Skift

**Meaning:** No specific time is given; the visit can be placed anywhere in the **slot** defined by "När på dagen" and Skift (Morgon, Lunch, Kväll, etc.).

**CSV signal:** **Före** and **Efter** cells are **empty** (blank or missing), not the digit 0.

**Example:**

| När på dagen | Skift | Före      | Efter     | Intended window                |
| ------------ | ----- | --------- | --------- | ------------------------------ |
| Morgon       | Dag   | _(empty)_ | _(empty)_ | 07:00–10:30 (full Morgon slot) |
| Lunch        | Dag   | _(empty)_ | _(empty)_ | 11:00–13:30 (full Lunch slot)  |
| _(empty)_    | —     | _(empty)_ | _(empty)_ | 07:00–22:00 (heldag)           |

**Python v3:** Full slot from "När på dagen".  
**Dashboard:** Empty Före/Efter (trimmed cell `""`) → full slot from getSlotBounds; we distinguish empty from explicit "0".

---

### 3. 0 0 Före Efter — exact time (same as case 1)

**Meaning:** Explicit **Före=0, Efter=0** means "at this exact Starttid," i.e. no flex. Same intent as "Exakt dag/tid" but expressed via numbers.

**CSV signal:** **Före** = `0` and **Efter** = `0` (the string "0" or number 0 in the cell).

**Example:**

| När på dagen | Starttid | Före | Efter | Intended window                     |
| ------------ | -------- | ---- | ----- | ----------------------------------- |
| Morgon       | 07:05    | 0    | 0     | 07:05–07:11 (exact; 6 min duration) |
| Lunch        | 13:30    | 0    | 0     | 13:30–13:36 (exact)                 |

**Python v3:** When före=0 and efter=0 the script uses full slot by default; "0 0 = exact" is the **intended** business rule you're describing.  
**Dashboard:** We now treat **explicit** 0,0 as exact time; only **empty** Före/Efter give full slot.

---

### Summary table (intended vs implemented)

| Case                    | CSV signal                      | Intended window                  | Dashboard (seed + import)                                    |
| ----------------------- | ------------------------------- | -------------------------------- | ------------------------------------------------------------ |
| **1. Exakt dag/tid**    | "När på dagen" contains "Exakt" | Exact Starttid (e.g. 1‑min flex) | ✅ Exact window (Starttid → Starttid + max(duration, 1 min)) |
| **2. Empty Före/Efter** | Före and Efter cells empty      | Full slot (När på dagen + Skift) | ✅ Full slot via getSlotBounds                               |
| **3. 0 0 Före Efter**   | Före=0, Efter=0 (explicit)      | Exact Starttid (no flex)         | ✅ Exact window (same as case 1)                             |

Implementation: we distinguish **empty** (trimmed cell `""`) from **explicit "0"**. Empty → full slot; explicit 0,0 or "Exakt" in När på dagen → exact time window.

---

## Time windows (Före/Efter) — current implementation

| Scenario                    | Seed / CSV upload                                         |
| --------------------------- | --------------------------------------------------------- |
| **Exakt in När på dagen**   | Exact window (Starttid → Starttid + max(duration, 1 min)) |
| **Explicit 0,0 Före/Efter** | Same (exact window)                                       |
| **Empty Före/Efter**        | Full slot from getSlotBounds("När på dagen")              |
| **Non-zero Före/Efter**     | Starttid ± Före/Efter                                     |

Seed and CSV upload use the **same three-way logic** (see table above).

## v3 Python fixes (FIXES_IMPLEMENTED.md)

1. **Exakt dag/tid** → minimal flex (1 min in pipeline). Dashboard: **implemented** — "Exakt" in När på dagen → exact window; explicit 0,0 Före/Efter → exact. Projection uses DB `allowedTimeWindowStart/End` as-is.
2. **Empty Före/Efter with specific time** → ±15 min in Python. Dashboard: when Före=Efter=0 we use **full slot** (same as script default), not ±15 min; when Före/Efter non-zero we use exact Starttid ± Före/Efter.
3. **Same-day PT0M dependencies** → 1173 added in Python. Dashboard: **projection** (buildTimefoldModelInput) generates same-day dependencies when building the FSR payload; seed and CSV upload do **not** create VisitDependency records for PT0M — the projection derives them from visit order and client/date.

## Same-day dependencies

- **Stored in DB**: Only **ClientDependencyRule** ("Antal tim mellan besöken") from CSV. No PT0M rows in DB.
- **In FSR payload**: **buildTimefoldModelInput** adds same-day ordering (PT0M) for pinned visits so Timefold respects sequence. So seed and CSV upload both feed the same projection; PT0M behavior is shared.

## Verification

- **be-agent-service**: `verify_csv_to_json.py` checks CSV → JSON (Python pipeline) dependency counts and time windows.
- **beta-appcaire**: Seed and upload produce the same `allowedTimeWindowStart/End` for the same CSV row; FSR input is built by the same projection from DB. To compare with v3 JSON, run seed or upload then `yarn workspace dashboard-server e2e:timefold` and compare payload stats (visit count, dependency count) with VERIFICATION_RESULTS.md.

## Summary

- **Seed** and **CSV upload** are aligned: same time-window rules (slot when Före=Efter=0, else Starttid ± Före/Efter), same recurrence/visit-id handling, same catalog usage.
- **v3 fixes**: Same-day PT0M is handled in the **projection**. Time-window rules match v3 for the default (full slot when Före=Efter=0). Exakt dag/tid and ±15 min small flex are Python-pipeline refinements; dashboard uses full-slot or explicit windows only.
