# PT0M Dependency Explanation

**Question**: Does PT0M mean two visits use the same employee?

**Answer**: ❌ NO - PT0M only prevents **temporal overlap**, not **vehicle assignment**

---

## What PT0M Dependencies Actually Do

### The Problem Without PT0M

**Example from CSV**:
```csv
Kundnr,Datum,Starttid,När på dagen,Insatser,Längd
H015,2026-03-02,08:00,Morgon,Frukost,30
H015,2026-03-02,11:00,Lunch,Mat,30
```

**Without PT0M dependency**, Timefold FSR sees:
```json
{
  "id": "H015_breakfast",
  "location": [59.23, 17.99],  // H015's home
  "timeWindows": [{
    "minStartTime": "2026-03-02T07:45:00",
    "maxStartTime": "2026-03-02T08:15:00",
    "maxEndTime": "2026-03-02T08:45:00"
  }],
  "serviceDuration": "PT30M"
}

{
  "id": "H015_lunch",
  "location": [59.23, 17.99],  // SAME location (H015's home)
  "timeWindows": [{
    "minStartTime": "2026-03-02T10:45:00",
    "maxStartTime": "2026-03-02T11:15:00",
    "maxEndTime": "2026-03-02T11:45:00"
  }],
  "serviceDuration": "PT30M"
}
```

**What can happen**:
1. Employee A assigned to H015_breakfast → starts 08:00, ends 08:30
2. Employee B assigned to H015_lunch → starts **08:10**, ends 08:40

**PROBLEM**: Both visits happen at **the same location** (H015's home) with **overlapping times**!
- 08:00-08:30: Employee A doing breakfast
- 08:10-08:40: Employee B doing lunch
- **Physical impossibility**: H015 cannot receive breakfast AND lunch simultaneously

### The Solution With PT0M

**With PT0M dependency**:
```json
{
  "id": "H015_lunch",
  "location": [59.23, 17.99],
  "timeWindows": [...],
  "serviceDuration": "PT30M",
  "visitDependencies": [{
    "id": "dep_H015_lunch_0",
    "precedingVisit": "H015_breakfast",
    "minDelay": "PT0M"  // ← 0 minutes minimum delay
  }]
}
```

**What this means**:
```
H015_lunch.startTime >= H015_breakfast.endTime + 0 minutes
```

**Effect**:
1. Employee A does breakfast: 08:00-08:30
2. Employee B does lunch: Must start ≥ 08:30 (after breakfast ends)
3. **No overlap**: Lunch cannot start until 08:30 or later

**Employees can still be different!** The dependency only controls TIME, not VEHICLE.

---

## Why Timefold Could Assign Overlaps Without Dependencies

### Timefold FSR Optimization Goals

Without dependencies, FSR optimizes for:
1. **Minimize travel time**
2. **Maximize vehicle utilization**
3. **Respect time windows**

**Each visit is independent**. FSR doesn't know that two visits at the same location = same person.

### Example Scenario

**Client H015 lives at [59.23, 17.99]**

**Solver's perspective**:
```
Visit 1: H015_breakfast
  - Location: [59.23, 17.99]
  - Time window: 07:45-08:45
  - Duration: 30 min

Visit 2: H015_lunch
  - Location: [59.23, 17.99]  ← Solver doesn't realize this is SAME PERSON
  - Time window: 10:45-11:45
  - Duration: 30 min
```

**Optimal solution (from FSR's perspective)**:
```
Employee A route:
  07:00 Start depot
  08:00-08:30 H015_breakfast ← Client H015's home
  09:00-09:30 H026_breakfast
  10:00-10:30 H092_lunch

Employee B route:
  07:00 Start depot
  08:10-08:40 H015_lunch ← SAME location as Employee A at 08:00!
  09:00-09:30 H041_breakfast
```

**Why FSR thinks this is good**:
- ✅ All time windows respected
- ✅ Travel time minimized
- ✅ High vehicle utilization

**Why this is WRONG**:
- ❌ H015 cannot receive breakfast AND lunch simultaneously
- ❌ Physical impossibility

**FSR doesn't know** that:
- Two visits at same location = same person
- Same person cannot receive two services at once

---

## How PT0M Fixes This

### Before PT0M (Overlap Possible)

```
Timeline for H015's home [59.23, 17.99]:

08:00    08:10    08:30    08:40
|--------|--------|--------|
[Employee A: Breakfast    ]
         [Employee B: Lunch        ]
         ^^^^^^^^ OVERLAP!
```

### After PT0M (Overlap Prevented)

```
Timeline for H015's home [59.23, 17.99]:

08:00    08:30    11:00    11:30
|--------|--------|--------|
[Employee A: Breakfast]
                  [Employee B: Lunch    ]
                  No overlap!
```

**PT0M dependency adds constraint**:
```
Lunch.startTime >= Breakfast.endTime + PT0M
Lunch.startTime >= 08:30 + 0 min
Lunch.startTime >= 08:30
```

**Result**:
- Breakfast: 08:00-08:30 (Employee A)
- Lunch: Must start ≥ 08:30 (Employee B)
- **No temporal overlap possible**

---

## PT0M vs Visit Groups

### Visit Groups
**Force same vehicle AND temporal sequence**:
```json
{
  "id": "VG_H026_morning",
  "visits": [
    {"id": "H026_shower", ...},
    {"id": "H026_dressing", ...}
  ]
}
```

**Effect**:
- ✅ Same employee
- ✅ Sequential (shower → dressing)
- ✅ No other visits in between

### PT0M Dependencies
**Force only temporal sequence**:
```json
{
  "id": "H015_lunch",
  "visitDependencies": [{
    "precedingVisit": "H015_breakfast",
    "minDelay": "PT0M"
  }]
}
```

**Effect**:
- ❌ NOT same employee (can be different)
- ✅ Sequential (breakfast → lunch)
- ✅ Other visits can happen in between

---

## Real Example from v3

### H015 Dependencies (28 total, 14 PT0M)

**Sample**:
```
H015_r3_1 depends on H015_r1_1 with minDelay: PT3H30M
  → Lunch must start ≥3.5 hours after breakfast
  → Can be different employees

H015_r6_1 depends on H015_r5_1 with minDelay: PT0M
  → Visit 6 must start after visit 5 ends
  → Can be different employees
```

**Why different delays?**
- `PT3H30M`: CSV has "3.5" in `antal_tim_mellan` column
- `PT0M`: CSV has empty or same-day visits with different start times

---

## Why This Matters

### Without PT0M Dependencies

**Campaign 117a4aa3 had issues**:
- Same-day visits at same location overlapping
- Client notes: "H015 breakfast and lunch scheduled simultaneously"
- Physically impossible to execute

### With PT0M Dependencies (v3)

**1173 PT0M dependencies prevent**:
- Temporal overlaps at same location
- Same client receiving multiple services simultaneously
- Infeasible schedules

**Still allows**:
- Different employees for different visits (continuity optimization comes later)
- Flexible routing (solver can choose best vehicle)
- Travel time optimization

---

## How Continuity Will Work (Phase 2)

### Current (v3_FIXED with PT0M)
```
H015 Breakfast → Employee A (07:00-08:30)
H015 Lunch → Employee B (11:00-11:30)  ← Different employee, no overlap!
H015 Dinner → Employee C (17:00-17:30)
```

**Result**: No overlaps, but 3 different employees

### After Continuity Optimization (v3_CONTINUITY_v2)
```json
{
  "id": "H015_breakfast",
  "requiredVehicles": ["Dag_01_Central_1", "Dag_02_Central_1"]
}
{
  "id": "H015_lunch",
  "requiredVehicles": ["Dag_01_Central_1", "Dag_02_Central_1"]
}
{
  "id": "H015_dinner",
  "requiredVehicles": ["Kväll_01_Central_1"]
}
```

**Result**: All H015 visits constrained to 2-3 specific employees

```
H015 Breakfast → Dag_01_Central_1 (Employee A)
H015 Lunch → Dag_01_Central_1 (Employee A) ← Same employee!
H015 Dinner → Kväll_01_Central_1 (Employee C, different shift)
```

**Continuity**: 3 employees → 2 employees

---

## Summary

| Feature | Forces Same Employee? | Prevents Time Overlap? |
|---------|----------------------|------------------------|
| **PT0M dependency** | ❌ No | ✅ Yes |
| **Visit groups** | ✅ Yes | ✅ Yes |
| **requiredVehicles** | ✅ Yes (limited set) | ❌ No |

**PT0M dependencies**:
- ✅ Prevent temporal overlaps
- ✅ Allow different employees
- ✅ Solve the physical impossibility problem
- ❌ Do NOT force same employee

**Continuity optimization** (Phase 2) will use `requiredVehicles` to reduce employee count while keeping PT0M to prevent overlaps.

---

**Key Insight**:

Overlap prevention ≠ Same employee

- **PT0M** = No time overlap (different employees OK)
- **Visit groups** = Same employee + no time overlap
- **requiredVehicles** = Limited employee pool (continuity)

The 1173 PT0M dependencies in v3 solve the overlap problem WITHOUT forcing same employee. Continuity optimization comes next!
