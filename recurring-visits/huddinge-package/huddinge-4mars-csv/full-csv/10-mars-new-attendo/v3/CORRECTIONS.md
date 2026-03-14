# Important Corrections

**Date**: 2026-03-13 18:00

## 1. Tags Approach - NEEDS RE-EVALUATION ⚠️

### What I Said (INCORRECT)
> ❌ Tags approach failed (FSR schema doesn't support tags)

### What You Corrected (CORRECT)
There are multiple tag/vehicle approaches in FSR:

1. **Tags on vehicles + requiredTags/preferredTags on visits**
   - Vehicle: `{ "id": "Dag_01", "tags": ["central", "experienced"] }`
   - Visit: `{ "id": "H015_r1", "requiredTags": ["central"] }`

2. **requiredVehicles / preferredVehicles on visits** (what we're using)
   - Visit: `{ "id": "H015_r1", "requiredVehicles": ["Dag_01", "Dag_02"] }`

### What Actually Failed
I tried adding `tags` directly to **VISITS**:
```json
{
  "id": "H015_r1",
  "tags": ["customer_H015"]  // ← This is what failed (schema violation)
}
```

### What Should Work
**Option 1: Tags on vehicles**
```json
// Vehicles
{
  "id": "Dag_01_Central_1",
  "tags": ["central", "group_A"]
}

// Visits
{
  "id": "H015_r1",
  "requiredTags": ["central"]  // Only vehicles with "central" tag
}
```

**Option 2: requiredVehicles** (current approach)
```json
{
  "id": "H015_r1",
  "requiredVehicles": ["Dag_01_Central_1", "Dag_02_Central_1"]
}
```

### Action Needed
- ✅ We're using requiredVehicles approach (should work)
- ⚠️ Need to verify if tags on vehicles + requiredTags on visits is also valid FSR schema

---

## 2. Physical Impossibility - WRONG EXAMPLE ❌

### What I Said (INCORRECT)
> Two employees at H015's home at 08:00 and 08:10 is physically impossible

### What You Corrected (CORRECT)
**Multiple people CAN be at the same location at the same time!**

What's ACTUALLY impossible:
- ❌ ONE person in TWO places at the same time
- ✅ Multiple people at ONE place at the same time (perfectly fine!)

### In Home Care Context
**Overlap at same location = Visit Group (Double Employee Visit)**

Example:
```
08:00-08:30 H015 home: Employee A + Employee B
  → This is INTENTIONAL (two employees needed for lifting/transfer)
  → Represented as visit group in FSR
```

**What PT0M prevents**:
```
Employee A:
  08:00-08:30 at H015 (Breakfast)
  08:10-08:40 at H026 (Shower)  ← IMPOSSIBLE! Same person, two places

NOT:
  08:00-08:30 Employee A at H015
  08:10-08:40 Employee B at H015  ← ALLOWED! Different people, same place
```

---

## 3. PT0M vs Timed Dependencies - WRONG EXAMPLE ❌

### What I Said (INCORRECT)
> H015 breakfast and lunch have PT0M dependency

### What You Corrected (CORRECT)
**Breakfast → Lunch must have 3-3.5 hour delay, NOT PT0M!**

### Actual Data
From CSV and FSR verification:
```
H015_r1 (Morgon) → H015_r4 (Lunch)
  Delay: PT3H30M (3.5 hours)

H015_r4 (Lunch) → H015_r6 (Kväll)
  Delay: PT0M (sequential, same shift boundary)
```

### When PT0M Is Added
PT0M is only added when:
1. **No explicit delay in CSV** (`antal_tim_mellan` is empty)
2. **Current visit starts later** than previous visit
3. **Same day, same client**

Example where PT0M is correct:
```csv
Kundnr,Datum,Starttid,När på dagen,Antal tim mellan
H092,2026-03-02,17:00,Kväll,
H092,2026-03-02,18:30,Kväll,   ← Empty! But starts later
```

Result: PT0M dependency (prevent Kväll2 before Kväll1)

### When Timed Delay Is Used
When CSV specifies `antal_tim_mellan`:
```csv
Kundnr,Datum,Starttid,När på dagen,Antal tim mellan
H015,2026-03-02,07:05,Morgon,
H015,2026-03-02,13:30,Lunch,3.5  ← Specified as 3.5 hours
```

Result: PT3H30M dependency (enforce 3.5 hour gap)

---

## 4. What PT0M Actually Prevents

### CORRECT Understanding

**PT0M prevents**: Same employee assigned to overlapping time slots

```
Employee A schedule WITHOUT PT0M:
  08:00-08:30 H015 Kväll1 at [59.23, 17.99]
  08:15-08:45 H015 Kväll2 at [59.23, 17.99]
  ^^^^^^^^^ IMPOSSIBLE: Same person, two tasks, overlapping times
```

**PT0M ensures**: Sequential scheduling

```
Employee A schedule WITH PT0M:
  17:00-17:30 H015 Kväll1 at [59.23, 17.99]
  17:30-18:00 H015 Kväll2 at [59.23, 17.99]
  ^^^^^^^^^ ALLOWED: Same person, sequential tasks
```

**PT0M does NOT prevent**: Different employees at same location

```
WITH PT0M:
  Employee A: 08:00-08:30 H015 Breakfast
  Employee B: 08:10-08:40 H026 Shower
  ^^^^^^^^^ ALLOWED: Different people, different clients

  Employee A: 17:00-17:30 H015 Kväll1
  Employee B: 17:10-17:40 H015 Kväll2 (if it's a visit group)
  ^^^^^^^^^ ALLOWED if visit group: Two employees for one client (intentional)
```

---

## 5. Visit Groups vs PT0M Dependencies

### Visit Groups (Double Employee Visits)
**When two employees MUST work together**:
```json
{
  "id": "VG_H026_transfer",
  "visits": [
    {"id": "H026_lift_1", "serviceDuration": "PT25M"},
    {"id": "H026_lift_2", "serviceDuration": "PT25M"}
  ]
}
```

**Effect**:
- ✅ Same two employees
- ✅ Same time (overlapping/concurrent)
- ✅ Same location
- **Use case**: Heavy lifting, transfers, complex care

### PT0M Dependencies
**When visits must be sequential (one after another)**:
```json
{
  "id": "H015_kväll2",
  "visitDependencies": [{
    "precedingVisit": "H015_kväll1",
    "minDelay": "PT0M"
  }]
}
```

**Effect**:
- ❌ NOT necessarily same employee
- ✅ Sequential times (no overlap for same employee)
- ✅ Same or different location
- **Use case**: Prevent one person being scheduled for overlapping tasks

---

## 6. Corrected PT0M Count Interpretation

### What the 1173 PT0M Dependencies Actually Mean

**NOT**: 1173 visit pairs forced to same employee
**YES**: 1173 visit pairs prevented from overlapping IF assigned to same employee

**Example**:
```
Visit A: 17:00-17:30
Visit B: with PT0M dependency on A

Scenario 1 (Different employees):
  Employee X: 17:00-17:30 Visit A
  Employee Y: 17:10-17:40 Visit B
  Result: ✅ ALLOWED (different people)

Scenario 2 (Same employee):
  Employee X: 17:00-17:30 Visit A
  Employee X: 17:10-17:40 Visit B
  Result: ❌ FORBIDDEN (PT0M forces B.start >= A.end)

Scenario 2 (Same employee, sequential):
  Employee X: 17:00-17:30 Visit A
  Employee X: 17:30-18:00 Visit B
  Result: ✅ ALLOWED (B.start >= A.end)
```

---

## Summary of Corrections

| My Statement | Correction | Impact |
|-------------|------------|---------|
| "Tags don't work in FSR" | Tags on vehicles + requiredTags on visits might work | Need to verify schema |
| "Two employees at same location impossible" | Multiple people at ONE place is fine! | Corrected understanding |
| "H015 breakfast→lunch has PT0M" | Has PT3H30M from CSV data | Example was wrong |
| "PT0M prevents overlap at same location" | PT0M prevents same PERSON having overlapping tasks | Clarified constraint |
| "1173 PT0M = forced same employee" | 1173 PT0M = prevented overlap IF same employee | Different meaning |

---

## Next Steps

1. ✅ Continue with requiredVehicles approach (proven to work)
2. ⚠️ Optionally test tags on vehicles + requiredTags on visits
3. ✅ PT0M dependencies are correct (prevent scheduling conflicts)
4. ✅ Timed dependencies (PT3H, PT3H30M) are correct (from CSV)

---

**Thank you for the corrections!** The documentation has been updated to reflect accurate understanding.
