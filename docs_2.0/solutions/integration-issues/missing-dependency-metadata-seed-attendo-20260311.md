---
module: Timefold Projection
date: 2026-03-11
problem_type: integration_issue
component: database
symptoms:
  - "Dashboard FSR produces only 34 dependencies vs Python script's 145"
  - "Timefold solve fails or produces poor schedule due to missing visit ordering constraints"
  - "Same-day dependencies (e.g. Morgon->Lunch) entirely absent from dashboard FSR"
root_cause: logic_error
resolution_type: seed_data_update
severity: critical
tags: [seed, timefold, fsr, dependencies, metadata, antalTimMellanBesoken]
---

# Troubleshooting: Seed script omits dependency metadata, breaking Timefold solve

## Problem

The Attendo CSV seed script (`seed-attendo.ts`) did not store `antalTimMellanBesoken` (hours between visits) or `narPaDagen` (time-of-day slot) in visit or template metadata. The FSR projection (`buildTimefoldModelInput.ts`) reads these fields to generate same-day and spread dependencies. With null metadata, the platform produced only 34 dependencies (all from flexible visit defaults) instead of the expected 145.

## Environment

- Module: Timefold Projection / Seed Pipeline
- Stack: TypeScript, Prisma, PostgreSQL
- Affected Components: `seed-attendo.ts`, `buildTimefoldModelInput.ts`
- Date: 2026-03-11

## Symptoms

- Dashboard FSR JSON had 34 visit dependencies vs Python script's 145
- Same-day dependencies (Morgon -> Lunch for same client) were entirely missing (0 vs 81)
- Spread dependencies were partially present but with wrong delay values
- Timefold solve quality degraded because visit ordering constraints were absent
- The `importAttendoSchedule.ts` path worked correctly (stored metadata), but seed path did not

## What Didn't Work

**Direct solution:** The problem was identified by comparing the seed's visit metadata with the import path's metadata and tracing the projection code that reads `antalTimMellanBesoken`.

## Solution

**Two files changed:**

### 1. `seed-attendo.ts` - Add missing metadata fields

Template metadata (line ~1007):

```typescript
// Before (broken):
metadata: {
  seed: true,
  csvRowIndex: rowIdx,
  slinga: row.Slinga,
  // ... other fields ...
  recurrence,
  // MISSING: antalTimMellanBesoken
  // MISSING: narPaDagen
}

// After (fixed):
metadata: {
  seed: true,
  csvRowIndex: rowIdx,
  slinga: row.Slinga,
  // ... other fields ...
  recurrence,
  antalTimMellanBesoken: row["Antal tim mellan besoken"]?.trim() || null,
  narPaDagen: row["Nar pa dagen"]?.trim() || null,
}
```

Same change applied to visit metadata (line ~1054).

### 2. `buildTimefoldModelInput.ts` - Fix slot name handling

`getSlotOrder()` failed for canonical slot names like `"kvall"` (without a-umlaut) because it only checked for `"kvall"` (with a-umlaut). The `daySlotNameMap` maps Swedish display names to canonical ASCII names.

```typescript
// Before (broken):
function getSlotOrder(slot) {
  if (s.includes("morgon")) return 0;
  if (s.includes("lunch")) return 1;
  if (s.includes("kvall")) return 2; // "kvall" != "kvall"!
  if (s.includes("dag")) return 3;
}

// After (fixed):
function getSlotOrder(slot) {
  if (s.includes("morgon")) return 0;
  if (s === "formiddag" || s.includes("formiddag")) return 1;
  if (s.includes("lunch")) return 2;
  if (s === "eftermiddag") return 3;
  if (s === "middag") return 4;
  if (s === "kvall" || s.includes("kvall")) return 5;
}
```

Also fixed the `hasSlot` check in the spread dependency section to recognize canonical names.

## Why This Works

1. **Root cause:** The seed script was created separately from the import script. The import path (`importAttendoSchedule.ts`) correctly stored `antalTimMellanBesoken` in both visit and template metadata (lines 749, 805). The seed path was written later and omitted these fields.

2. **The projection reads metadata to build dependencies:** `buildTimefoldModelInput.ts` section 10c reads `visit.metadata.antalTimMellanBesoken` for same-day deps and section 10b reads `template.metadata.antalTimMellanBesoken` for spread deps. With null values, both branches produced zero dependencies.

3. **The slot name mismatch:** The seed maps Swedish display names ("Kvall") to ASCII canonical names ("kvall") via `daySlotNameMap`. But `getSlotOrder` and `hasSlot` only checked for the Swedish form ("kvall" with a-umlaut), so "kvall" visits were misclassified.

## Prevention

- When adding new data paths (seed, import, API), always verify metadata parity by checking which fields the downstream consumers (projection, resolvers) read
- The `compare_fsr_inputs.py` script should be run after any seed/import change to catch dependency count regressions
- Canonical slot names (ASCII without Swedish characters) should be tested explicitly in `getSlotOrder` and any slot-matching logic

## Related Issues

No related issues documented yet.
