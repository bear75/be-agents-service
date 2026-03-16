---
title: Dashboard FSR Diverges from Python Script on Attendo CSV
slug: dashboard-fsr-diverges-python-script-attendo-20260311
category: logic-errors
tags:
  - fsr
  - attendo
  - csv
  - seed
  - projection
  - recurrence
  - time-windows
  - priority-gate
severity: critical
components:
  - apps/dashboard-server/src/seed-attendo.ts
  - apps/dashboard-server/src/services/timefold/projection/buildTimefoldModelInput.ts
  - apps/dashboard-server/src/services/timefold/projection/classifyRecurrence.ts
date_resolved: 2026-03-11
---

# Dashboard FSR Diverges from Python Script on Attendo CSV

## Problem

The dashboard platform's FSR (Field Service Routing) JSON output differs significantly from the reference Python script (`attendo_4mars_to_fsr.py`) when processing the same Attendo CSV data (81 clients, 2-week schedule). Key metrics diverged:

| Metric          | Script | Dashboard (before) | Gap  |
| --------------- | ------ | ------------------ | ---- |
| Dependencies    | 145    | 34                 | -111 |
| Flexible visits | 436    | ~100               | -336 |
| Total visits    | 3744   | ~3500              | -244 |

This caused the Timefold optimizer to produce far worse schedules from the dashboard than from the script.

## Root Causes (4 independent issues)

### 1. Priority Gate Incorrectly Pinning Visits

**File:** `buildTimefoldModelInput.ts` (lines 294-306)

The projection used `resolvePriority()` to determine pin/flex classification. This cascaded from `inset.defaultPriority` through the priority chain. Many common insets had `defaultPriority ≤ 3` (Morgonvård=3, Måltid=3, Toalettbesök=2), hitting the `CRITICAL_PRIORITY_MAX = 3` gate and pinning visits that the CSV never marked as "Kritisk insats = Ja".

**Impact:** ~137 visits incorrectly pinned instead of flexible.

**Fix:** Replace priority cascade with `visit.isMandatory` check (set only when CSV "Kritisk insats" = "Ja").

```typescript
// Before (wrong): cascaded inset priority pins common visit types
const resolvedP = resolvePriority(
  visit.inset,
  visit.visitTemplate,
  visit.priority,
);
if (resolvedP <= CRITICAL_PRIORITY_MAX) {
  pinnedVisits.push(visit);
  continue;
}

// After (correct): only explicit CSV flag pins visits
if (visit.isMandatory) {
  pinnedVisits.push(visit);
  continue;
}
```

### 2. Day Name Parsing Failures in Seed

**File:** `seed-attendo.ts` (lines 356-372)

`parseDayNamesToEnglish()` only recognized 3-letter abbreviations (mån, tis, ons) but CSV contains:

- Full names: "måndag", "tisdag", "torsdag"
- Plurals: "fredagar", "torsdagar"
- Capitalized: "Onsdag", "Fre"
- Trailing commas: "mån,", "tis,"

**Impact:** `preferredDays` arrays were empty/incomplete → `shouldPinWeekdays()` incorrectly classified flexible visits as pinned.

**Fix:** Comprehensive `SWEDISH_DAY_TO_ENGLISH` lookup with all variants, split on `[\s,]+`, lowercase normalization.

### 3. Regex Missing Comma-less Recurrence Patterns

**File:** `seed-attendo.ts` (lines 329-351)

Recurrence regex `^Varje vecka,\s*(.+)$` required a comma after "Varje vecka" but CSV has:

- "Varje vecka Fre" (space, no comma)
- "Varannan vecka Onsdag"
- "Varje vecka tis fre"

**Impact:** These patterns fell through to `{ frequency: "custom", preferredDays: [] }` → visits not expanded correctly.

**Fix:** Changed regex to `^Varje vecka[,\s]\s*(.+)$` (accept comma OR space).

### 4. Slot/Timezone/Normalization Issues (earlier session)

**File:** `classifyRecurrence.ts`

- `SLOTS` had incorrect time ranges vs script's `_compute_slot_bounds`
- `setUTCHours` caused 1-hour timezone shift (should be `setHours` for CET)
- `normalizeSlot` didn't recognize canonical ASCII names ("kvall" vs "kväll")
- `getSlotOrder` used `.includes("kväll")` which missed "kvall" canonical form

## Prevention

- Inset fields (defaultPriority, defaultDurationMinutes, defaultSpreadDelay) are UI defaults only — never use them as truth for FSR projection
- CSV data stored in visit/template metadata JSON is the source of truth
- When adding Swedish text parsing, always handle: abbreviations, full names, plurals, capitalization, trailing punctuation
- Test recurrence parsing against actual CSV data patterns, not just expected clean input
- The `visit.isMandatory` flag is the only reliable indicator for "Kritisk insats"

## Verification

After each fix: re-seed database → run `dump-fsr.ts` → compare with `compare_fsr_v2.py` against script's `script_fsr.json`.
