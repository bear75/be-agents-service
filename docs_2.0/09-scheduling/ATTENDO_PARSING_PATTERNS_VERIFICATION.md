# Attendo Parsing Patterns – Verification Report

**Date:** 2026-03-16  
**Input:** `recurring-visits/.../v3/input_e2e_verification.json` (from `Huddinge-v3 - Data_final.csv`)  
**Reference:** [ATTENDO_PARSING_PATTERNS.md](ATTENDO_PARSING_PATTERNS.md)

---

## Summary: Mapped Patterns Worked ✅

The generated FSR input aligns with the documented Attendo parsing patterns. Counts, dependency types, time-window behavior, visit groups, and FSR schema (no tags on visits) all match expectations.

---

## 1. Recurrence & expansion ✅

| Check | Result |
|-------|--------|
| **Total visits** | 3,844 (3,520 standalone + 324 in groups) |
| **Visit groups** | 152 groups (Dubbel) |
| **Vehicles** | 195 (from Slinga) |

Expansion from CSV rows to visit occurrences over the planning window is consistent with **§1 Recurrence Patterns** (daily/weekly/biweekly, weekday mapping). No anomaly in total visit count.

---

## 2. Time slot mapping ("När på dagen" + "Skift") ✅

| Same-day window width | Count | Interpretation |
|------------------------|-------|----------------|
| **0–2 min** (exact) | 209 | Exakt dag/tid, or explicit 0,0 Före/Efter, or Kritisk insats |
| **2 min–3 h** (slot) | 3,125 | Full slot (morgon 3h, lunch 2.5h, kväll 3h, etc.) per §2 |
| **3 h–15 h** | 139 | Heldag or long slot |
| **Period-based** (multi-day) | 47 | Flexible day in window |

Distribution matches **§2 Time Slot Mapping** and **§3 Time Window Calculation**: mix of exact (±1 min), full-slot, and heldag/flexible.

---

## 3. Time window calculation (four cases) ✅

- **Case 1 – Exakt dag/tid:** Reflected in 209 visits with 0–2 min start window.
- **Case 2 – Empty Före/Efter:** Reflected in 3,125+ visits with slot-sized windows (morgon/lunch/kväll/heldag).
- **Case 3 – Explicit 0,0:** Treated as exact; included in exact-window count.
- **Case 4 – Non-zero Före/Efter:** Reflected in various PT*H*M dependency delays and any remaining custom window widths.

**Planning window:** `2026-03-02`–`2026-03-15` (14 days), consistent with doc and v3 campaign.

---

## 4. Dependency creation ("Antal tim mellan besöken") ✅

| Delay type | Count | Pattern (§4) |
|------------|-------|--------------|
| **PT0M** | 1,060 | Same-day sequencing (prevent overlap) |
| **PT0H30M – PT3H30M** | ~900+ | Same-day spread (&lt;12 h): frukost→lunch, lunch→middag, etc. |
| **PT18H, PT19H28M, PT21H29M, PT23H15M** | 46+6+4+8 | Cross-day spread (≥18 h) |
| **Total** | 2,006 | Within expected ~2,000 for v3 |

Spread semantics (§4) are respected: short delays for same-day ordering, long delays (e.g. PT18H) for cross-day.

---

## 5. Visit groups ("Dubbel") ✅

- **Group ID format:** `VG_{client}_{date_iso}_{dubbel}` (e.g. `VG_H026_2026-03-07_9`).
- Aligns with **§6 Visit Group**: same client, date, and dubbel value grouped; 152 groups, 324 visits in groups.

---

## 6. FSR schema (no tags on visits) ✅

| Check | Result |
|-------|--------|
| Standalone visits with `tags` | 0 |
| Group visits with `tags` | 0 |

**§ and FSR compliance:** No `tags` on any visit; schema-safe for Timefold FSR.

---

## 7. Locations ✅

All 3,520 standalone visits have `location` with `[lat, lon]`. Geocoding or fallback (e.g. DEFAULT_OFFICE) is applied; no visits dropped for missing coordinates.

---

## Conclusion

The mapped patterns from **ATTENDO_PARSING_PATTERNS.md** are correctly applied in the e2e conversion from `Huddinge-v3 - Data_final.csv` to `input_e2e_verification.json`: recurrence, time slots, time windows (four cases), dependencies (PT0M + same-day/cross-day spread), visit groups (Dubbel), and no tags on visits. No corrections needed for this run.
