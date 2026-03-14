# Schedule TF FSR Input Generation Analysis
**Date**: 2026-03-13
**Analysis of**: Huddinge v3 Data → TF FSR Input Pipeline
**Campaign**: 117a4aa3

## Executive Summary

The script flow (`attendo_4mars_to_fsr.py`) generates incorrect schedule constraints in the Timefold FSR input, leading to:
1. **Overly flexible time windows** when exact times are specified
2. **Missing or incorrect visit dependencies** between related visits
3. **Incorrect handling of "Exakt dag/tid" entries**
4. **Same-day visit conflicts** (overlapping visits for same customer)

## Root Cause Analysis

### Issue 1: Time Window Calculation with Före=Efter=0

**Location**: `attendo_4mars_to_fsr.py` lines 606-636 (`_compute_slot_bounds`)

**Problem**: When both "Före" and "Efter" columns are 0 (or empty), the script uses the **entire slot window** instead of the specified "Starttid".

```python
# Före=Efter=0 → alltid hela sloten (både Morgon/Lunch/Kväll och Heldag)
if före == 0 and efter == 0:
    return (slot_start_min, max(slot_start_min, slot_end_min - längd), is_heldag)
```

**Example from H332** (line 501 in data):
- Starttid: 07:20
- När på dagen: "Exakt dag/tid"
- Före: 0, Efter: 0
- **Expected**: Visit must start at 07:20
- **Actual**: Gets full "Dag" shift window (07:00-15:00), allowing scheduler to place it anywhere

**Impact**:
- Visits marked as "Exakt dag/tid" have 8-hour flex instead of 0 flex
- Critical time-sensitive visits (DVS transport at 08:15 in H332) miss their deadlines
- Notes report: "H332,Besök ej planerade efter filen"

### Issue 2: Missing "Exakt dag/tid" Recognition

**Location**: Throughout the script - no special handling for "När på dagen" = "Exakt dag/tid"

**Problem**: The script doesn't recognize "Exakt dag/tid" as a special case requiring exact time adherence.

**Current Flow**:
```python
def _slot_for_nar_pa_dagen(nar: str, schift: str = "") -> Tuple[str, str]:
    n = (nar or "").strip().lower()
    if "morgon" in n:
        return SLOT_MORGON
    # ... other slots ...
    # "Exakt dag/tid" falls through to SLOT_HELDAG or shift-based window
```

**Expected Flow**:
- "Exakt dag/tid" should:
  1. Use the exact "Starttid" value
  2. Set minStartTime = maxStartTime = Starttid (zero flex). Timefold FSR allows this; our pipeline’s `_verify_all_visits_have_flex()` optionally enforces non-zero flex.
  3. Ignore "Före" and "Efter" columns

**Impact**:
- All "Exakt dag/tid" entries get flexible windows
- Notes report: "Alla kunder,Exakt dag/tid,Ta bort rörlig start/stopp"

### Issue 3: Visit Dependency Logic for Same-Day Chains

**Location**: `attendo_4mars_to_fsr.py` lines 933-1013 (`_build_visits_and_groups`)

**Problem**: The dependency logic has two issues:

#### 3a. Long Delay Exclusion from Same-Day Chains

```python
if delay_min > SAME_DAY_DELAY_MAX_MINUTES:
    continue  # Long delay = spread only; no same-day dep
```

**Explanation**:
- Same-day chains only use delays ≤ 12 hours
- Visits with "Antal tim mellan besöken" = "36 timmar" or "48 timmar" get NO same-day dependency
- This allows visits that should be sequenced (e.g., shower after morning) to be scheduled independently

**Example from H092**:
- Row 163: Shower at 08:30, "36 timmar" delay
- Row 164: Morning meal at 09:00
- **Expected**: Shower should come after morning (or before) with proper sequencing
- **Actual**: Both treated independently, leading to overlaps
- Notes report: "H092,2/3+6/3 dusch + morgon överlappar varandra"

#### 3b. "3,5timmar" Parsing and Application

**Problem**: When "Antal tim mellan besöken" = "3,5timmar":
- It's parsed to "PT3H30M" (210 minutes) ✓
- Creates a dependency: lunch must start 3.5h after morning departure ✓
- BUT: This is from **end of previous visit** to **start of next visit**
- If morning visit has 1h flex window, effective gap can be 2.5h-4.5h

**Example from H092**:
- Row 164: Morning at 09:00 (but with 60min före = starts 08:00-09:00)
- Row 167: Lunch at 13:05 with "3,5timmar" delay
- **Expected**: If morning is at 09:00, lunch should be at 12:30 (09:00 + 3.5h)
- **Actual**: If morning starts at 08:00, lunch can be at 11:30 (08:00 + 3.5h)
- Notes report: "H092,Förmiddag och lunch diffar ej med 3 timmar mellan besöken"

### Issue 4: Overlapping Visits from Different Slingor

**Location**: Shift/vehicle assignment and time window overlap checks

**Problem**: Multiple "Slinga" (loops) for the same customer can have visits at the same time.

**Example from H248**:
- Row 341: Promenad on "Dag 09" at 09:41, empty före/efter
- Row 342: Tillsyn on "Dag 09" at 10:30, "0 min före, 30 min efter"
- Row 344: Lunch on "Dag 09" at 12:54, "40 min före, 30 min efter"
- Row 346: Shower on "Dag 09" at 13:34, empty före/efter
- Row 348: Tillsyn on "Dag 09" at 14:08, "38 min före, 20 min efter"

**Issue**:
- Promenad (row 341) has empty före/efter → gets full slot (10:00-11:00 for Förmiddag context)
- This overlaps with Tillsyn at 10:30 (row 342)
- Notes report: "H248,2 promenader samtidigt 3/6 07:05"

### Issue 5: Empty Före/Efter Defaults to 0

**Location**: Line 442-443

```python
"före": _parse_int(row.get("Före"), 0),
"efter": _parse_int(row.get("Efter"), 0),
```

**Problem**: When "Före" and "Efter" are **empty in CSV**, they default to 0, triggering the "use full slot" logic.

**Impact**:
- Many visits in the CSV have empty före/efter
- All of these get full slot windows instead of exact times
- This is likely the **primary root cause** of most scheduling issues

## Affected Customers (from Notes)

| Customer | Issue | Root Cause |
|----------|-------|------------|
| H3047 | Schedule starts at 07:00 instead of 09:45-15:00 | Empty före/efter → full slot |
| H332 | Visits not scheduled correctly, wrong dates | "Exakt dag/tid" not recognized |
| H092 | Shower + morning overlap | Long delay (36h) excludes same-day dep |
| H092 | Lunch not 3h after morning | Time window flex + dependency gap |
| H248 | 2 walks at same time | Empty före/efter → overlapping slots |
| H248 | Walk before morning visit | No dependency enforcing sequence |
| H248 | Shower overlaps other visit | Empty före/efter + no dependency |
| H037 | Morning + lunch on different employees | No continuity constraint |
| H038 | Morning + shower + lunch on different employees | No continuity constraint |

## Recommendations

### Fix 1: Handle Empty Före/Efter as Exact Time (Not Full Slot)

**Change** in `_compute_slot_bounds`:

```python
# When före/efter are BOTH zero AND När på dagen is a specific slot (not Exakt dag/tid),
# give small flex (e.g., ±15 min) instead of full slot
if före == 0 and efter == 0:
    # Check if this is an "Exakt dag/tid" entry
    nar_lower = (occ.get("när_på_dagen") or "").strip().lower()
    if "exakt" in nar_lower:
        # Exact time: zero flex
        return (start_min, start_min, is_heldag)

    # For empty före/efter on normal slots, use small flex instead of full slot
    # This preserves some scheduler flexibility while respecting the scheduled time
    SMALL_FLEX_MIN = 15  # ±15 minutes
    min_start_min = max(slot_start_min, start_min - SMALL_FLEX_MIN)
    max_start_min = min(slot_end_min - längd, start_min + SMALL_FLEX_MIN)
    return (min_start_min, max_start_min, is_heldag)
```

### Fix 2: Add "Exakt dag/tid" Recognition

**Add** at the start of `_slot_for_nar_pa_dagen`:

```python
def _slot_for_nar_pa_dagen(nar: str, schift: str = "") -> Tuple[str, str]:
    n = (nar or "").strip().lower()

    # "Exakt dag/tid" should return a marker that _compute_slot_bounds can recognize
    if "exakt" in n:
        return ("EXACT", "EXACT")  # Marker for exact time

    # ... rest of function
```

Then handle "EXACT" in `_compute_slot_bounds`.

### Fix 3: Create Same-Day Dependencies for All Same-Customer Visits

**Change** in `_build_visits_and_groups` (around line 950):

```python
# Instead of skipping long delays:
if delay_min > SAME_DAY_DELAY_MAX_MINUTES:
    # Still create dependency but with the raw delay value
    # This ensures shower (48h) still sequences after morning on the same day
    preceding_map[occ["visit_id"]] = (occs[i - 1]["visit_id"], delay_str)
```

**Alternative**: Keep the long-delay exclusion but add explicit same-day sequencing based on time windows:

```python
# For same customer, same date, different rows:
# If visit B's time window starts after visit A's, add a PT0M dependency to enforce sequence
for i, occ in enumerate(occs):
    if i == 0:
        continue
    prev_occ = occs[i - 1]
    if occ["visit_id"] not in preceding_map:
        # No delay specified, but if time windows suggest sequence, enforce it
        occ_start = _parse_time_minutes(occ.get("starttid", "08:00"))
        prev_start = _parse_time_minutes(prev_occ.get("starttid", "08:00"))
        if occ_start > prev_start:
            # B starts after A: add PT0M dependency to prevent overlap
            preceding_map[occ["visit_id"]] = (prev_occ["visit_id"], "PT0M")
```

### Fix 4: Add Continuity Constraints (Same Employee for Same Customer)

**New Feature**: Add tags or skills to visits from the same customer to encourage same employee:

```python
# In _build_visits_and_groups, add customer tag
visit["tags"] = [f"customer_{kundnr}"]

# In vehicle/shift generation, add:
# "preferredTags": ["customer_HXXX"] to shifts, so solver prefers same employee
```

This would address notes like "H037,Morgon + lunch hamnar på olika medarbetare samma dag?"

### Fix 5: Validate CSV Data Before Conversion

**New Script**: `validate_csv_before_conversion.py` to check:
- Empty "Före" and "Efter" for non-flexible visits
- "Exakt dag/tid" entries have critical flag
- "Antal tim mellan besöken" values are reasonable
- Time windows don't overlap for same customer

## Testing Plan

1. **Create test cases** for each issue type:
   - Exakt dag/tid with före=efter=0
   - Empty före/efter with specific starttid
   - Same-customer visits with 36h/48h delays
   - Multiple visits same customer same day

2. **Compare outputs**:
   - Before fix: Current `input.json` with full slot windows
   - After fix: New `input.json` with exact times
   - Verify time windows match expectations

3. **Run continuity campaign**:
   - Use fixed input with continuity optimization
   - Check if same-customer visits get same employee

## Files to Modify

1. **Primary**: `scripts/attendo_4mars_to_fsr.py`
   - `_compute_slot_bounds` (lines 606-636)
   - `_slot_for_nar_pa_dagen` (lines 572-603)
   - `_build_visits_and_groups` (lines 899-1075)

2. **Validation** (new): `scripts/validate_csv_before_conversion.py`

3. **Documentation**: Update `E2E_RUN_10MARS.md` with:
   - Known issues and fixes
   - CSV data quality requirements
   - Expected vs actual behavior

## Next Steps

1. ✅ Identify root causes (this document)
2. ⬜ Implement Fix 1: Empty före/efter handling
3. ⬜ Implement Fix 2: Exakt dag/tid recognition
4. ⬜ Implement Fix 3: Same-day dependencies
5. ⬜ Test with v3 data
6. ⬜ Generate new input.json and compare
7. ⬜ Submit to Timefold and validate results
8. ⬜ Update CSV data with correct före/efter values if needed

---

**Analysis completed**: 2026-03-13
**Analyzer**: Claude Code
**Campaign ID**: 117a4aa3
