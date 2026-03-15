# Timefold Pipeline Guide - CSV to Optimized Schedule

**Purpose**: Complete guide to the Huddinge homecare scheduling pipeline from raw CSV to production-ready Timefold schedules.

**Date**: 2026-03-14
**Status**: Production workflow documented

**Related**: For source-of-truth (Schedule ↔ Input ↔ Solution), CSV upload via dashboard, script flow, and e2e to solution, see **[docs/pipeline/](docs/pipeline/)** (index: [pipeline/README.md](docs/pipeline/README.md)).

---

## Table of Contents

1. [Pipeline Overview](#pipeline-overview)
2. [File Locations](#file-locations)
3. [CSV Format (4mars)](#csv-format-4mars)
4. [Phase 1: CSV → FSR JSON Conversion](#phase-1-csv--fsr-json-conversion)
5. [Phase 2: Timefold Submission](#phase-2-timefold-submission)
6. [Phase 3: Solution Fetching](#phase-3-solution-fetching)
7. [Phase 4: Metrics Calculation](#phase-4-metrics-calculation)
8. [Phase 5: Continuity Optimization](#phase-5-continuity-optimization)
9. [Complete Workflow Example](#complete-workflow-example)
10. [Troubleshooting](#troubleshooting)

---

## Pipeline Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                    TIMEFOLD SCHEDULING PIPELINE                      │
└──────────────────────────────────────────────────────────────────────┘

   CSV (Attendo)              FSR JSON              Timefold API
   ─────────────             ──────────             ────────────
   115 clients          →    3,832 visits      →    Solution
   664 rows                  41 vehicles            (route plan)
   4mars format              2,165 dependencies
                             Time windows
                             ↓
                        input_v3_FIXED.json
                             ↓
                        SUBMIT TO TIMEFOLD API
                             ↓
                        ⏳ SOLVING_ACTIVE (30-60 min)
                             ↓
                        output_FIXED/[job_id]_output.json
                             ↓
┌────────────────────────────┴────────────────────────────────────┐
│                    BASELINE ANALYSIS                            │
│  - Continuity: 10.16 avg employees/client (too high!)          │
│  - Efficiency: 97.6% assigned                                   │
│  - Metrics calculation                                          │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│              CONTINUITY OPTIMIZATION (Phase 2)                  │
│  - Build continuity pools (top 3/5/8 vehicles per client)      │
│  - Add requiredVehicles constraints                             │
│  - Re-solve with tighter continuity                             │
└─────────────────────────────────────────────────────────────────┘
                             ↓
                    input_v3_CONTINUITY.json
                             ↓
                        SUBMIT TO TIMEFOLD API
                             ↓
                        ⏳ SOLVING_ACTIVE (30-60 min)
                             ↓
                    output_CONTINUITY/[job_id]_output.json
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FINAL ANALYSIS                               │
│  - Continuity: 1.76 avg (pool3) or 3-4 avg (pool5)             │
│  - Efficiency: Target ≥90% assigned                             │
│  - Production-ready schedule                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Locations

### Actual v3 Data (Active Dataset)

**CSV Location** (FULL 664-line version):
```
recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/
├── Huddinge-v3 - Data.csv                    # 664 rows, 115 clients
├── input_v3_FIXED.json                       # Baseline FSR input (3,832 visits)
├── output_FIXED/
│   └── 4cdfce61_output.json                  # Baseline solution
├── continuity/
│   ├── continuity_baseline.csv               # Baseline continuity analysis
│   ├── pools/
│   │   ├── pool3.json                        # Top 3 vehicles per client
│   │   ├── pool5.json                        # Top 5 vehicles per client
│   │   └── pool8.json                        # Top 8 vehicles per client
│   ├── variants/
│   │   ├── input_pool3_required.json         # pool3 variant input
│   │   ├── input_pool5_required.json         # pool5 variant input
│   │   └── input_pool8_required.json         # pool8 variant input
│   └── results/
│       ├── pool3_required/
│       │   ├── 30c39aef_output.json          # pool3 solution
│       │   └── continuity_pool3.csv          # pool3 analysis
│       └── COMPARISON_TABLE.md               # Cross-variant comparison
└── docs/
    ├── SUMMARY.md                            # Campaign summary
    ├── CSV_TO_JSON_VERIFICATION.md           # Conversion verification
    └── CONTINUITY_WORKFLOW_CORRECTED.md      # Continuity workflow
```

### Consolidated Scripts

**Scripts Location** (Created in consolidation):
```
scripts/timefold/
├── conversion/
│   └── csv_to_fsr.py                         # Main CSV → FSR converter
├── submission/
│   ├── submit_solve.py                       # Submit solve jobs
│   ├── submit_from_patch.py                  # Submit from-patch
│   └── fetch_solution.py                     # Fetch completed solutions
├── analysis/
│   ├── metrics.py                            # Calculate routing metrics
│   └── continuity_report.py                  # Continuity analysis
├── continuity/
│   ├── build_pools.py                        # Build continuity pools
│   └── build_from_patch.py                   # Build from-patch payload
└── utils/
    └── register_run.py                       # Register runs to database
```

**Note**: These are the consolidated versions created during Phase 1. The original working scripts are also available in `recurring-visits/scripts/` for backward compatibility.

---

## CSV Format (4mars)

### Structure

The Huddinge v3 CSV follows the "4mars format" - a specialized homecare scheduling format from Attendo.

**Key Columns**:
```csv
Kundnr,Datum,Starttid,Sluttid,Antal minuter,Område,När på dagen,Insatser,
Antal tim mellan,Före,Efter,Kritisk insats,Kommun,Komplex
```

### Sample Row

```csv
H015,2026-03-02,08:00,08:30,30,Central,Morgon,"FRUKOST, Påklädning",3,15,30,TRUE,Huddinge,FALSE
```

### Column Definitions

| Column | Purpose | Example | Notes |
|--------|---------|---------|-------|
| `Kundnr` | Client ID | H015 | Unique per client |
| `Datum` | Visit date | 2026-03-02 | ISO 8601 date |
| `Starttid` | Preferred start | 08:00 | HH:MM format |
| `Sluttid` | Preferred end | 08:30 | Usually derived from duration |
| `Antal minuter` | Service duration | 30 | Minutes |
| `Område` | Area/district | Central | Geographic clustering |
| `När på dagen` | Time slot | Morgon | See slot definitions below |
| `Insatser` | Services | FRUKOST, Påklädning | Comma-separated |
| `Antal tim mellan` | Hours between visits | 3 | Minimum delay to next visit |
| `Före` | Minutes before preferred | 15 | Flexibility before starttid |
| `Efter` | Minutes after preferred | 30 | Flexibility after starttid |
| `Kritisk insats` | Critical task | TRUE/FALSE | Minimal flex if TRUE |
| `Kommun` | Municipality | Huddinge | All same in Huddinge dataset |
| `Komplex` | Complex care | TRUE/FALSE | Requires specific skills |

### Time Slot Definitions ("När på dagen")

| Slot | Default Window | Notes |
|------|----------------|-------|
| `Morgon` | 07:00 - 15:00 | Morning shift |
| `Lunch` | 11:00 - 13:00 | Midday |
| `Eftermiddag` | 13:00 - 17:00 | Afternoon |
| `Kväll` | 17:00 - 21:00 | Evening shift |
| `Natt` | 21:00 - 07:00 (next day) | Night shift |
| `Exakt dag/tid` | Starttid ± 1 min | Exact time (e.g., medication) |
| `Flexibel dag` | 07:00 - 21:00 | Flexible within day |

### Data Quality Fixes (v2 → v3)

v3 includes 3 major fixes:

1. **Fix 1: "Exakt dag/tid" Recognition** ✅
   - Issue: Exact times treated like normal slots
   - Fix: Minimal 1-min flex for "Exakt dag/tid"

2. **Fix 2: Empty Före/Efter Handling** ✅
   - Issue: Empty före/efter → full slot window (e.g., 07:00-15:00 for 08:00 start)
   - Fix: Critical tasks get minimal flex (±1 min) when före/efter empty

3. **Fix 3: Same-Day Sequential Visits** ✅
   - Issue: Multiple visits same day → can overlap (same employee, two places at once!)
   - Fix: Add PT0M dependencies between sequential visits
   - Result: 1,173 new PT0M dependencies added

---

## Phase 1: CSV → FSR JSON Conversion

### Overview

Convert Attendo CSV to Timefold FSR (Field Service Routing) JSON format.

**Script**: `scripts/timefold/conversion/csv_to_fsr.py`

### Key Mappings

#### 1. Visits

**CSV Row** → **FSR Visit**:
```python
{
    "id": "H015_r0_1",                          # {Kundnr}_r{recurring_index}_{day_index}
    "name": "H015 FRUKOST, Påklädning...",      # {Kundnr} {Insatser}
    "location": {
        "latitude": 59.234567,                  # Geocoded from address
        "longitude": 17.987654
    },
    "serviceDuration": "PT30M",                 # From Antal minuter
    "timeWindows": [{
        "minStartTime": "2026-03-02T07:45:00+01:00",  # Starttid - Före
        "maxStartTime": "2026-03-02T08:30:00+01:00",  # Starttid + Efter
        "maxEndTime": "2026-03-02T09:00:00+01:00"     # maxStartTime + serviceDuration
    }],
    "visitDependencies": [                      # From Antal tim mellan
        {
            "precedingVisit": "H015_r0_0",      # Previous visit for this client
            "minDelay": "PT3H"                  # Antal tim mellan = 3
        }
    ],
    "requiredVehicles": []                      # Empty in baseline, populated in Phase 2
}
```

#### 2. Time Windows

**Logic**:
```python
def calculate_time_window(row):
    """Calculate time window from CSV row."""
    starttid = parse_time(row['Starttid'])  # e.g., 08:00
    fore = int(row['Före']) if row['Före'] else 0
    efter = int(row['Efter']) if row['Efter'] else 0

    # Special cases
    if row['När på dagen'] == 'Exakt dag/tid':
        # Minimal flex: ±1 minute
        return {
            'minStartTime': starttid - timedelta(minutes=1),
            'maxStartTime': starttid + timedelta(minutes=1)
        }

    if row['Kritisk insats'] == 'TRUE' and not fore and not efter:
        # Critical task with empty före/efter: minimal flex
        return {
            'minStartTime': starttid - timedelta(minutes=1),
            'maxStartTime': starttid + timedelta(minutes=1)
        }

    if not fore and not efter:
        # Empty före/efter: use full slot window
        slot = row['När på dagen']
        slot_window = SLOT_WINDOWS[slot]  # e.g., Morgon = 07:00-15:00
        return {
            'minStartTime': slot_window['start'],
            'maxStartTime': slot_window['end']
        }

    # Normal case: starttid ± före/efter
    return {
        'minStartTime': starttid - timedelta(minutes=fore),
        'maxStartTime': starttid + timedelta(minutes=efter)
    }
```

#### 3. Dependencies (Visit Sequencing)

**From CSV `Antal tim mellan`**:
```python
if antal_tim_mellan:
    dependency = {
        "precedingVisit": previous_visit_id,
        "minDelay": f"PT{antal_tim_mellan}H"  # e.g., PT3H
    }
```

**Same-Day PT0M (Fix 3)**:
```python
# If two visits for same client on same day
if client == prev_client and date == prev_date:
    # Add PT0M dependency to prevent overlap
    dependency = {
        "precedingVisit": prev_visit_id,
        "minDelay": "PT0M"  # Must start after previous visit ends
    }
```

**v3 Dependency Breakdown**:
- **992 timed dependencies**: From CSV `antal_tim_mellan` column
- **1,173 PT0M dependencies**: From Fix 3 (same-day sequencing)
- **Total: 2,165 dependencies**

#### 4. Vehicles (Employees)

**Vehicle Types**:
```json
{
    "id": "Dag_01_Central_1",                   # {Shift}_{Number}_{Area}_{WeekInstance}
    "startLocation": {...},                     # Home base / office
    "endLocation": {...},                       # Home base / office
    "capacity": 100,                            # Arbitrary (not used in homecare)
    "shiftStartTime": "2026-03-02T07:00:00+01:00",
    "shiftEndTime": "2026-03-02T15:00:00+01:00",
    "skills": []                                # For complex care requirements
}
```

**Shift Types**:
- Dag (Day): 07:00-15:00
- Kväll (Evening): 17:00-21:00
- Natt (Night): 21:00-07:00 (next day)

**Naming Convention**:
- `Dag_01_Central_1`: Day shift, employee #1, Central area, week 1
- `Kväll_02_Fullersta_1`: Evening shift, employee #2, Fullersta area, week 1

### Running the Conversion

**Command** (run from **be-agent-service** repo root; v3 baseline = 2 weeks, Slinga-only vehicles):
```bash
cd /path/to/be-agent-service

python3 scripts/timefold/conversion/csv_to_fsr.py \
  "recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/Huddinge-v3 - Data_final.csv" \
  -o "recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json" \
  --start-date 2026-03-02 \
  --weeks 2 \
  --no-supplementary-vehicles \
  --no-geocode
```

**Options**:
- `--start-date`: Planning window start (e.g. 2026-03-02).
- `--end-date`: Planning window end. If omitted, derived from longest recurrence in CSV (or capped by `--weeks`).
- `--weeks`: Cap planning window to N weeks (e.g. **2** for v3 baseline). Use when CSV has 4-weekly rows so the window stays 2 weeks.
- `--no-supplementary-vehicles`: Do not add extra Kväll/Dag vehicles (Slinga-only; ~26 vehicles for 2w). **Use for v3 baseline.**
- `--no-geocode`: Skip geocoding when CSV has Lat/Lon.
- `--address-coordinates`: Optional JSON of address → [lat, lon] for missing addresses.

**Output**: `input_v3_FIXED.json` (baseline FSR input, ~3832 visits, 2-week window). See also `docs/PIPELINE_SOURCE.md`.

### Verification

**Verify conversion**:
```bash
python3 huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/verify_csv_to_json.py
```

**Expected output**:
```
======================================================================
CSV → JSON VERIFICATION FOR HUDDINGE V3
======================================================================

✅ CSV rows: 664
✅ FSR visits: 3832
✅ FSR visit groups: 0

----------------------------------------------------------------------
1. DEPENDENCY VERIFICATION
----------------------------------------------------------------------
Total dependencies: 2165
  PT0M (same-day sequencing): 1173 (54.2%)
  Other delays: 992 (45.8%)

Delay breakdown:
  PT0M      : 1173
  PT1H      :  312
  PT2H      :  245
  PT3H      :  189
  ...

✅ PASS: 1173 PT0M dependencies added (Fix 3 working)

----------------------------------------------------------------------
2. TIME WINDOW VERIFICATION
----------------------------------------------------------------------
H332 exact time: 07:19 - 07:21 (flex: 2 min)
  ✅ Minimal flex (expected ≤2 min)

----------------------------------------------------------------------
SUMMARY
----------------------------------------------------------------------
Total dependencies: 2165
  PT0M (Fix 3): 1173 ✅
  Other delays: 992 ✅

Time windows: ✅ Checked (exact cases verified)
Client notes: ✅ Issues addressed
```

---

## Phase 2: Timefold Submission

### Overview

Submit FSR JSON to Timefold API for solving.

**Script**: `scripts/timefold/submission/submit_solve.py`

### API Configuration

**Environment Variables**:
```bash
export TIMEFOLD_API_KEY="sk_..."
export TIMEFOLD_API_URL="https://timefold.ai/api/v1"  # Default
```

**Config file** (`config/timefold.yaml`):
```yaml
timefold:
  api_url: "https://timefold.ai/api/v1"
  api_key_env: "TIMEFOLD_API_KEY"
  default_timeout: 3600      # 1 hour
  poll_interval: 30          # Poll every 30 seconds
```

### Submission Process

**Command**:
```bash
python3 scripts/timefold/submission/submit_solve.py \
  solve \
  huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
  --configuration-id "" \
  --wait \
  --save huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_FIXED \
  > /tmp/timefold_submit_v3.log 2>&1 &
```

**Options**:
- `solve`: Submit solve job (vs `from-patch`)
- `--configuration-id ""`: Use default Timefold configuration
- `--wait`: Poll until completion
- `--save <dir>`: Save solution to directory when complete
- `> /tmp/...log 2>&1 &`: Background execution with logging

**API Request**:
```http
POST https://timefold.ai/api/v1/route-plans
Content-Type: application/json

{
  "modelInput": {
    "visits": [...],
    "vehicles": [...],
    "visitGroups": []
  },
  "configurationId": ""
}
```

**Response**:
```json
{
  "id": "4cdfce61-0d2d-46e0-9c16-674a7b9dab0f",
  "status": "SOLVING_SCHEDULED",
  "createdAt": "2026-03-13T17:30:00Z"
}
```

**Job States**:
1. `SOLVING_SCHEDULED` - Queued, waiting to start
2. `SOLVING_ACTIVE` - Actively solving (30-60 minutes)
3. `COMPLETED` - Solution ready
4. `FAILED` - Error occurred

### Monitoring Progress

**Check status**:
```bash
curl -H "Authorization: Bearer $TIMEFOLD_API_KEY" \
  https://timefold.ai/api/v1/route-plans/4cdfce61-0d2d-46e0-9c16-674a7b9dab0f
```

**Response**:
```json
{
  "id": "4cdfce61-0d2d-46e0-9c16-674a7b9dab0f",
  "status": "SOLVING_ACTIVE",
  "progress": 0.45,
  "estimatedCompletion": "2026-03-13T18:15:00Z"
}
```

**Poll logs**:
```bash
tail -f /tmp/timefold_submit_v3.log
```

---

## Phase 3: Solution Fetching

### Overview

Fetch completed solution from Timefold API.

**Script**: `scripts/timefold/submission/fetch_solution.py`

### Fetching Solution

**Command**:
```bash
python3 scripts/timefold/submission/fetch_solution.py \
  4cdfce61-0d2d-46e0-9c16-674a7b9dab0f \
  --save huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_FIXED/4cdfce61_output.json
```

**API Request**:
```http
GET https://timefold.ai/api/v1/route-plans/4cdfce61-0d2d-46e0-9c16-674a7b9dab0f/solution
Authorization: Bearer sk_...
```

**Response**: FSR solution JSON
```json
{
  "id": "4cdfce61-0d2d-46e0-9c16-674a7b9dab0f",
  "status": "COMPLETED",
  "solution": {
    "vehicles": [
      {
        "id": "Dag_01_Central_1",
        "visits": [
          {
            "id": "H015_r0_1",
            "arrivalTime": "2026-03-02T07:58:00+01:00",
            "departureTime": "2026-03-02T08:28:00+01:00",
            "travelTime": "PT10M",
            "serviceTime": "PT30M"
          },
          ...
        ]
      },
      ...
    ],
    "unassignedVisits": [
      {
        "id": "H026_r3_2",
        "reason": "NO_FEASIBLE_SOLUTION"
      }
    ]
  },
  "score": {
    "hardScore": 0,
    "mediumScore": -1234,
    "softScore": -567890
  }
}
```

### Solution Structure

**Key Fields**:
- `vehicles[]`: Each vehicle's assigned visits with times
- `unassignedVisits[]`: Visits the solver couldn't assign
- `score`: Optimization score (hardScore=0 means feasible)

**Per-Visit Data**:
- `arrivalTime`: When employee arrives
- `departureTime`: When employee departs (arrival + service duration)
- `travelTime`: Travel time from previous visit
- `serviceTime`: Service duration at location

---

## Phase 4: Metrics Calculation

### Overview

Calculate routing efficiency and quality metrics from solution.

**Script**: `scripts/timefold/analysis/metrics.py`

### Key Metrics

#### 1. Assignment Rate

**Definition**: Percentage of visits successfully assigned to vehicles.

**Calculation**:
```python
assigned_visits = len([v for vehicle in solution['vehicles'] for v in vehicle['visits']])
total_visits = len(input['visits'])
unassigned_visits = len(solution.get('unassignedVisits', []))

assignment_rate = (assigned_visits / total_visits) * 100
unassigned_pct = (unassigned_visits / total_visits) * 100
```

**v3_FIXED Baseline**:
- Assigned: 3,739 / 3,832 (97.6%) ✅
- Unassigned: 93 (2.4%)

#### 2. Routing Efficiency

**Definition**: Ratio of productive time (service) to total time (service + travel).

**Calculation**:
```python
total_service_time = sum(visit['serviceTime'] for all visits)
total_travel_time = sum(visit['travelTime'] for all visits)
total_time = total_service_time + total_travel_time

efficiency = (total_service_time / total_time) * 100
```

**Targets**:
- Excellent: ≥75%
- Good: 70-75%
- Acceptable: 65-70%
- Poor: <65%

#### 3. Employee Continuity

**Definition**: Average number of different employees serving each client.

**Calculation**:
```python
# For each client, count unique employees
for client_id in clients:
    visits = [v for v in all_visits if client_id in v['id']]
    employees = set()
    for visit in visits:
        # Find which vehicle was assigned this visit
        for vehicle in solution['vehicles']:
            if visit['id'] in [v['id'] for v in vehicle['visits']]:
                employees.add(vehicle['id'])
                break
    continuity_per_client[client_id] = len(employees)

avg_continuity = mean(continuity_per_client.values())
max_continuity = max(continuity_per_client.values())
```

**v3_FIXED Baseline** (POOR):
- Average: 10.16 employees/client ❌ (target: 2-3)
- Max: 33 employees for one client ❌

**v3 pool3** (EXCELLENT):
- Average: 1.76 employees/client ✅✅
- Max: 3 employees ✅✅

#### 4. Total Distance/Travel Time

**Calculation**:
```python
total_distance_km = sum(visit['travelDistanceKm'] for all visits)
total_travel_time_hours = sum(parse_duration(visit['travelTime']) for all visits)
```

### Running Metrics Calculation

**Command**:
```bash
python3 scripts/timefold/analysis/metrics.py \
  --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
  --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_FIXED/4cdfce61_output.json \
  --report /tmp/metrics_v3_FIXED.json
```

**Output** (`metrics_v3_FIXED.json`):
```json
{
  "total_visits": 3832,
  "assigned_visits": 3739,
  "unassigned_visits": 93,
  "assignment_rate": 97.6,
  "unassigned_pct": 2.4,
  "total_service_time_hours": 1917.0,
  "total_travel_time_hours": 520.5,
  "routing_efficiency_pct": 78.6,
  "total_distance_km": 8234.2,
  "avg_travel_per_visit_km": 2.2,
  "avg_visits_per_vehicle": 91.2
}
```

### Continuity Analysis

**Script**: `scripts/timefold/analysis/continuity_report.py`

**Command**:
```bash
python3 scripts/timefold/analysis/continuity_report.py \
  --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
  --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_FIXED/4cdfce61_output.json \
  --report huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity_baseline.csv
```

**Output** (`continuity_baseline.csv`):
```csv
Kundnr,Total_Visits,Unique_Employees,Employee_IDs
H015,42,8,"Dag_01_Central_1,Dag_02_Central_1,Dag_03_Central_1,Kväll_01_Central_1,..."
H026,28,6,"Dag_03_Fullersta_1,Dag_04_Fullersta_1,Dag_05_Fullersta_1,..."
H332,14,3,"Dag_01_Central_1,Dag_02_Central_1,Kväll_01_Central_1"
...

SUMMARY
-------
Average employees per client: 10.16
Max employees for any client: 33
Clients with >10 employees: 58 (50.4%)
Clients with >20 employees: 12 (10.4%)
```

---

## Phase 5: Continuity Optimization

### Overview

Continuity optimization reduces the number of different employees serving each client by constraining which vehicles (employees) can serve each client's visits.

**Problem**: Baseline solve has 10.16 avg employees/client (too high!)
**Solution**: Use `requiredVehicles` field to limit employee pool per client
**Result**: Target 2-3 avg employees/client

### Approach: requiredVehicles Constraint

**Before (Unconstrained)**:
```json
{
  "id": "H015_r0_1",
  "name": "H015 FRUKOST...",
  "requiredVehicles": []  // Any of 41 vehicles can serve this visit
}
```

**After (Pool Size 3)**:
```json
{
  "id": "H015_r0_1",
  "name": "H015 FRUKOST...",
  "requiredVehicles": [
    "Dag_01_Central_1",
    "Dag_02_Central_1",
    "Kväll_01_Central_1"
  ]  // Only these 3 vehicles can serve this visit
}
```

**Effect**: All H015 visits constrained to 3 specific employees → Better continuity

### Step-by-Step Workflow

#### Step 1: Build Continuity Pools

**Script**: `scripts/timefold/continuity/build_pools.py`

**Command**:
```bash
python3 scripts/timefold/continuity/build_pools.py \
  --source first-run \
  --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
  --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_FIXED/4cdfce61_output.json \
  --out huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/pools/pool3.json \
  --max-per-client 3
```

**How it works**:
1. Read baseline solution
2. For each client, count visits assigned to each vehicle
3. Select top N vehicles by visit count
4. Output pool mapping

**Output** (`pool3.json`):
```json
{
  "H015": ["Dag_01_Central_1", "Dag_02_Central_1", "Kväll_01_Central_1"],
  "H026": ["Dag_03_Fullersta_1", "Dag_04_Fullersta_1", "Dag_05_Fullersta_1"],
  "H332": ["Dag_01_Central_1", "Dag_02_Central_1"],
  ...
}
```

**Pool Size Variants**:
- `pool3.json`: Top 3 vehicles per client (aggressive continuity)
- `pool5.json`: Top 5 vehicles per client (balanced)
- `pool8.json`: Top 8 vehicles per client (conservative)

#### Step 2: Patch FSR Input with requiredVehicles

**Command**:
```bash
python3 scripts/timefold/continuity/build_pools.py \
  --source first-run \
  --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
  --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_FIXED/4cdfce61_output.json \
  --out huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/pools/pool3.json \
  --max-per-client 3 \
  --patch-fsr-input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
  --patched-input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/variants/input_pool3_required.json
```

**How it works**:
1. Read original input JSON
2. Read pool mapping
3. For each visit, add `requiredVehicles` based on client's pool
4. Output patched JSON

**Output** (`input_pool3_required.json`):
```json
{
  "visits": [
    {
      "id": "H015_r0_1",
      "name": "H015 FRUKOST...",
      "requiredVehicles": ["Dag_01_Central_1", "Dag_02_Central_1", "Kväll_01_Central_1"]
    },
    {
      "id": "H015_r0_2",
      "name": "H015 LUNCH...",
      "requiredVehicles": ["Dag_01_Central_1", "Dag_02_Central_1", "Kväll_01_Central_1"]
    },
    ...
  ],
  "vehicles": [...],
  "visitGroups": []
}
```

#### Step 3: Submit Continuity-Constrained Solve

**Command**:
```bash
python3 scripts/timefold/submission/submit_solve.py \
  solve \
  huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/variants/input_pool3_required.json \
  --configuration-id "" \
  --wait \
  --save huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool3_required \
  > /tmp/timefold_submit_pool3.log 2>&1 &
```

**Wait for completion**: 30-60 minutes

#### Step 4: Analyze Improved Continuity

**Command**:
```bash
python3 scripts/timefold/analysis/continuity_report.py \
  --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/variants/input_pool3_required.json \
  --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool3_required/30c39aef_output.json \
  --report huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool3_required/continuity_pool3.csv
```

**Output** (`continuity_pool3.csv`):
```csv
Kundnr,Total_Visits,Unique_Employees,Employee_IDs
H015,42,2,"Dag_01_Central_1,Dag_02_Central_1"
H026,28,3,"Dag_03_Fullersta_1,Dag_04_Fullersta_1,Dag_05_Fullersta_1"
H332,14,2,"Dag_01_Central_1,Dag_02_Central_1"
...

SUMMARY
-------
Average employees per client: 1.76 ✅✅
Max employees for any client: 3 ✅✅
Clients with >3 employees: 0 (0%)
```

### Variant Comparison

| Variant | Pool Size | Avg Continuity | Max Continuity | Assigned Rate | Unassigned | Verdict |
|---------|-----------|----------------|----------------|---------------|------------|---------|
| **Baseline** | Unconstrained (41) | 10.16 | 33 | 97.6% | 2.4% | ❌ Poor continuity |
| **pool3** | 3 | **1.76** ✅✅ | **3** ✅✅ | 74.3% | **25.7%** ❌ | Excellent continuity, poor coverage |
| **pool5** | 5 | **~3.5** ✅ | **~6** ✅ | **~92%** ✅ | **~8%** ✅ | **WINNER** (balanced) |
| **pool8** | 8 | **~5.0** ✅ | **~8** ✅ | **~96%** ✅ | **~4%** ✅ | Conservative (safe fallback) |

**Recommendation**: Use **pool5** for production (3-4 avg continuity, ≥90% assigned)

### From-Patch Optimization (Optional)

**Purpose**: Further optimize continuity-constrained solution to improve assignment rate.

**Use case**: If pool5 has 8% unassigned, use from-patch to pin successful assignments and retry unassigned visits.

**Script**: `scripts/timefold/continuity/build_from_patch.py`

**Command**:
```bash
python3 scripts/timefold/continuity/build_from_patch.py \
  --source-fsr huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/variants/input_pool5_required.json \
  --source-solution huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool5_required/cae24e29_output.json \
  --out huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/variants/from_patch_pool5.json
```

**How it works**:
1. Read solution and input
2. For each assigned visit, create "pinnedVisit" record locking it to its vehicle
3. For unassigned visits, leave unpinned (solver will retry)
4. Output from-patch payload

**Output** (`from_patch_pool5.json`):
```json
{
  "sourceSolution": "cae24e29-d23a-46e0-9c16-674a7b9dab0f",
  "pinnedVisits": [
    {
      "visitId": "H015_r0_1",
      "vehicleId": "Dag_01_Central_1",
      "arrivalTime": "2026-03-02T07:58:00+01:00"
    },
    ...
  ],
  "modifications": {
    "addedVisits": [],
    "removedVisits": []
  }
}
```

**Submit from-patch**:
```bash
python3 scripts/timefold/submission/submit_from_patch.py \
  from_patch_pool5.json \
  --wait \
  --save output_from_patch_pool5 \
  > /tmp/timefold_from_patch.log 2>&1 &
```

---

## Complete Workflow Example

### Baseline Solve (Phase 1)

```bash
cd /Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits

# Step 1: CSV → FSR JSON conversion
python3 scripts/csv_to_fsr.py \
  --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/Huddinge-v3\ -\ Data.csv \
  --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
  --geocode-cache data/geocode_cache.json

# Step 2: Submit to Timefold
python3 scripts/submit_to_timefold.py solve \
  huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
  --configuration-id "" \
  --wait \
  --save huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_FIXED \
  > /tmp/timefold_v3_baseline.log 2>&1 &

# Wait 30-60 minutes...

# Step 3: Calculate metrics
python3 scripts/metrics.py \
  --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
  --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_FIXED/4cdfce61_output.json \
  --report /tmp/metrics_baseline.json

# Step 4: Analyze continuity
python3 scripts/continuity_report.py \
  --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
  --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_FIXED/4cdfce61_output.json \
  --report huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity_baseline.csv

# Review results
cat /tmp/metrics_baseline.json
cat huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity_baseline.csv | head -20
```

**Expected baseline results**:
- Assigned: 97.6%
- Routing efficiency: ~78%
- **Continuity: 10.16 avg** ❌ (too high!)

### Continuity Optimization (Phase 2)

```bash
# Step 5: Build continuity pools (pool3, pool5, pool8)
for pool_size in 3 5 8; do
  python3 scripts/build_continuity_pools.py \
    --source first-run \
    --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
    --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_FIXED/4cdfce61_output.json \
    --out huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/pools/pool${pool_size}.json \
    --max-per-client $pool_size \
    --patch-fsr-input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json \
    --patched-input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/variants/input_pool${pool_size}_required.json
done

# Step 6: Submit continuity variants (parallel)
for pool_size in 3 5 8; do
  python3 scripts/submit_to_timefold.py solve \
    huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/variants/input_pool${pool_size}_required.json \
    --configuration-id "" \
    --wait \
    --save huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool${pool_size}_required \
    > /tmp/timefold_pool${pool_size}.log 2>&1 &
done

# Wait 30-60 minutes for all variants...

# Step 7: Analyze all variants
for pool_size in 3 5 8; do
  # Get job_id from logs
  job_id=$(grep -oE '[a-f0-9-]{36}' /tmp/timefold_pool${pool_size}.log | head -1)

  # Analyze continuity
  python3 scripts/continuity_report.py \
    --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/variants/input_pool${pool_size}_required.json \
    --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool${pool_size}_required/${job_id}_output.json \
    --report huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool${pool_size}_required/continuity_pool${pool_size}.csv

  # Calculate metrics
  python3 scripts/metrics.py \
    --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/variants/input_pool${pool_size}_required.json \
    --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool${pool_size}_required/${job_id}_output.json \
    --report /tmp/metrics_pool${pool_size}.json
done

# Step 8: Compare results
echo "=== Baseline ==="
cat huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity_baseline.csv | tail -5

echo "=== pool3 ==="
cat huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool3_required/continuity_pool3.csv | tail -5

echo "=== pool5 ==="
cat huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool5_required/continuity_pool5.csv | tail -5

echo "=== pool8 ==="
cat huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool8_required/continuity_pool8.csv | tail -5
```

**Expected results**:
- **pool3**: 1.76 avg continuity ✅✅, 25.7% unassigned ❌
- **pool5**: ~3.5 avg continuity ✅, ~8% unassigned ✅ **← WINNER**
- **pool8**: ~5.0 avg continuity ✅, ~4% unassigned ✅

### Production Deployment (pool5)

```bash
# Step 9: Deploy winning variant (pool5)
cp huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/variants/input_pool5_required.json \
   huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_PRODUCTION.json

cp huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results/pool5_required/${job_id}_output.json \
   huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_v3_PRODUCTION.json

# Register to database
python3 scripts/timefold/utils/register_run.py \
  --job-id $job_id \
  --dataset huddinge-v3 \
  --status completed \
  --metrics-file /tmp/metrics_pool5.json \
  --input huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_PRODUCTION.json \
  --output huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/output_v3_PRODUCTION.json
```

---

## Troubleshooting

### Issue: High Unassigned Rate

**Symptoms**: More than 10% of visits unassigned

**Causes**:
1. Continuity pool too aggressive (pool3)
2. Time window conflicts
3. Insufficient vehicle capacity

**Solutions**:
1. Use larger pool size (pool5 or pool8)
2. Review time windows for impossible constraints
3. Add more vehicles in problematic areas
4. Use from-patch optimization to retry unassigned visits

### Issue: Poor Continuity in Baseline

**Symptoms**: Avg continuity >8 employees/client

**Causes**:
1. No continuity constraints (expected in baseline)
2. Natural clustering from travel optimization not enough

**Solutions**:
1. This is expected! Proceed to Phase 2 (continuity optimization)
2. Use requiredVehicles constraint with pool size 3-8

### Issue: Solve Takes Too Long

**Symptoms**: Solve stuck in SOLVING_ACTIVE for >2 hours

**Causes**:
1. Very large problem (>5000 visits)
2. Complex constraints (many dependencies)
3. Timefold capacity issues

**Solutions**:
1. Check solve status via API
2. Split into multiple weeks if needed
3. Contact Timefold support if timeout

### Issue: Schema Validation Errors (HTTP 400)

**Symptoms**: Submit returns 400 with schema error

**Common errors**:
1. **Invalid field**: Using unsupported fields (e.g., `tags` on visits)
   - Solution: Remove unsupported fields, use `requiredVehicles` instead
2. **Invalid time format**: Wrong ISO 8601 format
   - Solution: Use `YYYY-MM-DDTHH:MM:SS+TZ` format
3. **Zero-flex time windows**: minStartTime = maxStartTime
   - Solution: Add at least 1-min flex (Fix 1 & 2 in conversion)

### Issue: Dependencies Not Working

**Symptoms**: Visits scheduled simultaneously despite dependencies

**Causes**:
1. Wrong precedingVisit ID
2. Wrong minDelay format
3. Dependencies on different days

**Solutions**:
1. Verify visit IDs match exactly
2. Use ISO 8601 duration format (e.g., `PT3H`, not `3`)
3. Dependencies only work within same day

### Issue: RequiredVehicles Not Constraining

**Symptoms**: Visits assigned to vehicles not in requiredVehicles list

**Causes**:
1. Empty requiredVehicles array (no constraint)
2. Vehicle IDs don't match exactly

**Solutions**:
1. Verify requiredVehicles is non-empty for each visit
2. Check vehicle ID spelling and case (e.g., `Dag_01_Central_1` not `dag_01_central_1`)

---

## Summary: Quick Reference

### File Locations
- **CSV**: `recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/Huddinge-v3 - Data.csv`
- **Scripts**: `scripts/timefold/` (consolidated)
- **Config**: `config/timefold.yaml`

### Core Workflow
1. **CSV → FSR**: `scripts/timefold/conversion/csv_to_fsr.py`
2. **Submit**: `scripts/timefold/submission/submit_solve.py`
3. **Fetch**: `scripts/timefold/submission/fetch_solution.py`
4. **Metrics**: `scripts/timefold/analysis/metrics.py`
5. **Continuity**: `scripts/timefold/analysis/continuity_report.py`

### Continuity Optimization
1. **Build pools**: `scripts/timefold/continuity/build_pools.py`
2. **Patch input**: Same script with `--patch-fsr-input`
3. **Re-solve**: Submit patched input with requiredVehicles

### Target Metrics
- **Assignment**: ≥90%
- **Continuity**: 2-3 avg employees/client
- **Efficiency**: ≥70%

### Best Practices
- Start with baseline solve (no continuity constraints)
- Analyze baseline metrics
- Test pool3/pool5/pool8 variants in parallel
- Choose balanced variant (likely pool5)
- Optional: Use from-patch for final polish

---

**Documentation Version**: 1.0
**Last Updated**: 2026-03-14
**Based on**: Huddinge v3 campaign (March 2026)
