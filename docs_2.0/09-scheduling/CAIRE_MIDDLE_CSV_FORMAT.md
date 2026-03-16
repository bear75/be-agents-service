# Caire Middle CSV Format Specification

## Overview

The **Caire format** is a canonical intermediate representation for schedule imports. It serves as a normalized bridge between any CSV source format (Attendo, custom exports, etc.) and the database.

**Design Goals:**

- **Adapter-agnostic**: Any CSV can be converted to Caire before DB import
- **Normalized**: All strings standardized (slots, insets, durations use ISO 8601)
- **Validated**: Traffic-light validation (green/yellow/red) happens on Caire data
- **Flexible**: New client-specific strings handled via configurable alias maps (no code changes)

**Flow:**

```
Source CSV → Adapter → Caire Format → Validation → DB Import
                ↑                         ↑
           Fuzzy matching          Traffic-light checks
           Alias resolution        Category-based errors
```

## Core Principles

### 1. Canonical Column Names with Flexible Aliases

Each Caire field has a **canonical name** and multiple **aliases** that adapters recognize via fuzzy matching.

**Example:**

- Canonical: `employeeId`
- Aliases: `Slinga`, `slinga`, `employee_id`, `anställd`, `Employee ID`

Fuzzy matching normalizes headers by:

1. Trimming whitespace
2. Converting to lowercase
3. Removing spaces, underscores, hyphens

### 2. Canonical Value Maps with Configurable Aliases

String values (time slots, insets) map to canonical IDs via alias maps.

**Example - Time Slots:**

- Input: `"Morgon"`, `"MORGON"`, `"förmiddag"` → Canonical: `"morgon"`
- Input: `"Kväll"`, `"KVÄLL"`, `"Evening"` → Canonical: `"kväll"`
- Unknown input → Default: `"heldag"` (with yellow warning)

**Example - Insets:**

- Input: `"Tillsyn"`, `"TILLSYN"`, `"supervision"` → Canonical: `"supervision"`
- Input: `"Dusch/bad"`, `"Shower"` → Canonical: `"bath_shower"`
- Unknown input → Skipped (with yellow warning)

### 3. ISO 8601 Duration Format

All durations normalized to ISO 8601:

- `"3,5timmar"` → `"PT3H30M"`
- `"2 timmar"` → `"PT2H"`
- `"30 minuter"` → `"PT30M"`
- `"1,5 tim"` → `"PT1H30M"`

**Parsing rules:**

- Decimal comma: `3,5` = 3.5 hours
- Swedish keywords: `timmar`, `tim`, `timme`, `minuter`, `min`
- Whitespace and case insensitive

## Canonical Field Definitions

### Client Fields

| Canonical Name  | Aliases                              | Type   | Required | Example            |
| --------------- | ------------------------------------ | ------ | -------- | ------------------ |
| `externalId`    | `client_id`, `Klient-ID`, `kund_id`  | string | Yes      | `"C123"`           |
| `name`          | `client_name`, `Namn`, `klient_namn` | string | Yes      | `"Anna Andersson"` |
| `street`        | `address`, `Adress`, `gata`          | string | Yes      | `"Storgatan 1"`    |
| `postalCode`    | `postal_code`, `Postnummer`, `zip`   | string | Yes      | `"12345"`          |
| `city`          | `Stad`, `ort`                        | string | Yes      | `"Stockholm"`      |
| `latitude`      | `lat`, `Latitude`                    | number | No       | `59.3293`          |
| `longitude`     | `lon`, `lng`, `Longitude`            | number | No       | `18.0686`          |
| `serviceAreaId` | `service_area`, `område`             | string | No       | `"SA1"`            |

**Validation:**

- Missing `street`, `postalCode`, or `city` → **RED** (blocking)
- Missing `latitude` or `longitude` → **YELLOW** (geocoding needed)

### Employee/Resource Fields

| Canonical Name | Aliases                                       | Type   | Required | Example      |
| -------------- | --------------------------------------------- | ------ | -------- | ------------ |
| `employeeId`   | `Slinga`, `slinga`, `employee_id`, `anställd` | string | Yes      | `"EMP001"`   |
| `firstName`    | `first_name`, `Förnamn`                       | string | Yes      | `"Maria"`    |
| `lastName`     | `last_name`, `Efternamn`                      | string | Yes      | `"Svensson"` |

**Shift Fields:**

| Canonical Name | Aliases                       | Type           | Required | Example    |
| -------------- | ----------------------------- | -------------- | -------- | ---------- |
| `weekday`      | `day`, `dag`, `veckodag`      | string         | Yes      | `"Monday"` |
| `startTime`    | `start`, `Starttid`, `börjar` | string (HH:MM) | Yes      | `"08:00"`  |
| `endTime`      | `end`, `Sluttid`, `slutar`    | string (HH:MM) | Yes      | `"16:00"`  |
| `shiftType`    | `type`, `typ`, `skift_typ`    | string         | No       | `"day"`    |

**Canonical weekdays:** `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`, `Sunday`

### Visit Fields

| Canonical Name      | Aliases                                             | Type                | Required | Example        |
| ------------------- | --------------------------------------------------- | ------------------- | -------- | -------------- |
| `externalId`        | `visit_id`, `Besök-ID`                              | string              | Yes      | `"V001"`       |
| `clientExternalId`  | `client_id`, `Klient-ID`                            | string              | Yes      | `"C123"`       |
| `date`              | `datum`, `Date`                                     | string (YYYY-MM-DD) | Yes      | `"2026-03-20"` |
| `durationMinutes`   | `Längd`, `duration`, `tid_minuter`                  | number              | Yes      | `45`           |
| `startTime`         | `Starttid`, `start_time`, `tid`                     | string (HH:MM)      | No       | `"09:30"`      |
| `timeSlot`          | `När på dagen`, `nar_pa_dagen`, `time_slot`, `slot` | string              | Yes      | `"morgon"`     |
| `flexBeforeMinutes` | `flex_before`, `flex_före`                          | number              | No       | `30`           |
| `flexAfterMinutes`  | `flex_after`, `flex_efter`                          | number              | No       | `30`           |
| `groupId`           | `group`, `grupp_id`, `double_staffing`              | string              | No       | `"G1"`         |
| `priority`          | `prioritet`, `Prioritet`                            | number (1-10)       | No       | `5`            |
| `isCritical`        | `critical`, `kritisk`                               | boolean             | No       | `true`         |

**Insets field:**

| Canonical Name | Aliases                            | Type     | Required | Example                   |
| -------------- | ---------------------------------- | -------- | -------- | ------------------------- |
| `insets`       | `Insatser`, `services`, `tjänster` | string[] | No       | `["supervision", "meal"]` |

**Parsing:** Comma-separated list in CSV → Array of canonical inset IDs

### Visit Template Fields

Same as Visit fields, plus:

| Canonical Name     | Aliases                    | Type              | Required | Example                     |
| ------------------ | -------------------------- | ----------------- | -------- | --------------------------- |
| `frequency`        | `Återkommande`, `frekvens` | string            | Yes      | `"weekly"`                  |
| `frequencyPattern` | `pattern`, `mönster`       | string            | No       | `"Monday,Wednesday,Friday"` |
| `spreadDelay`      | `spread`, `spridning`      | string (ISO 8601) | No       | `"PT3H30M"`                 |

**Canonical frequencies:** `daily`, `weekly`, `bi_weekly`, `custom`

**Note:** Templates generate individual visits for the schedule date range.

### Dependency Fields

| Canonical Name              | Aliases                        | Type              | Required | Example    |
| --------------------------- | ------------------------------ | ----------------- | -------- | ---------- |
| `precedingVisitExternalId`  | `before_visit`, `föregående`   | string            | Yes      | `"V001"`   |
| `succeedingVisitExternalId` | `after_visit`, `efterföljande` | string            | Yes      | `"V002"`   |
| `minDelay`                  | `min_delay`, `min_fördröjning` | string (ISO 8601) | Yes      | `"PT2H"`   |
| `maxDelay`                  | `max_delay`, `max_fördröjning` | string (ISO 8601) | No       | `"PT4H"`   |
| `dependencyType`            | `type`, `typ`                  | string            | Yes      | `"spread"` |

**Canonical dependency types:** `spread`, `same_day`, `temporal`

## Canonical Time Slots

| Canonical ID  | Swedish Name | Typical Window | Aliases                                                  |
| ------------- | ------------ | -------------- | -------------------------------------------------------- |
| `morgon`      | Morgon       | 07:00-10:30    | `Morgon`, `MORGON`, `morgon`, `Morning`                  |
| `förmiddag`   | Förmiddag    | 09:00-12:00    | `Förmiddag`, `FÖRMIDDAG`, `förmiddag`, `Late Morning`    |
| `lunch`       | Lunch        | 11:00-14:00    | `Lunch`, `LUNCH`, `lunch`, `Midday`                      |
| `eftermiddag` | Eftermiddag  | 13:00-17:00    | `Eftermiddag`, `EFTERMIDDAG`, `eftermiddag`, `Afternoon` |
| `middag`      | Middag       | 16:00-19:00    | `Middag`, `MIDDAG`, `middag`, `Dinner`                   |
| `kväll`       | Kväll        | 18:00-22:00    | `Kväll`, `KVÄLL`, `kväll`, `Evening`                     |
| `natt`        | Natt         | 22:00-07:00    | `Natt`, `NATT`, `natt`, `Night`                          |
| `heldag`      | Heldag       | Flexible       | `Heldag`, `HELDAG`, `heldag`, `All Day`, `Whole Day`     |

**Default behavior:** Unknown slot values → `"heldag"` with **YELLOW** warning

**Time windows:** Used when no explicit `startTime` provided; visit scheduled within window

## Canonical Insets/Services

| Canonical ID       | Swedish Name     | Description                 | Aliases                                                              |
| ------------------ | ---------------- | --------------------------- | -------------------------------------------------------------------- |
| `supervision`      | Tillsyn          | Brief check-in              | `Tillsyn`, `TILLSYN`, `tillsyn`, `Supervision`                       |
| `bath_shower`      | Dusch/bad        | Bathing assistance          | `Dusch/bad`, `Dusch`, `Bad`, `Shower`, `Bath`                        |
| `meal`             | Måltid           | Meal preparation/assistance | `Måltid`, `MÅLTID`, `måltid`, `Meal`, `Food`                         |
| `medication`       | Medicinering     | Medication administration   | `Medicinering`, `MEDICINERING`, `medicinering`, `Medication`, `Meds` |
| `cleaning`         | Städning         | Cleaning services           | `Städning`, `STÄDNING`, `städning`, `Cleaning`                       |
| `shopping`         | Inköp            | Shopping assistance         | `Inköp`, `INKÖP`, `inköp`, `Shopping`                                |
| `social`           | Social aktivitet | Social interaction          | `Social aktivitet`, `Social`, `Sällskap`, `Company`                  |
| `exercise`         | Motion/promenad  | Exercise/walking            | `Motion`, `Promenad`, `Exercise`, `Walk`                             |
| `personal_hygiene` | Personlig hygien | Personal care               | `Personlig hygien`, `Hygien`, `Hygiene`                              |
| `dressing`         | Påklädning       | Dressing assistance         | `Påklädning`, `PÅKLÄDNING`, `påklädning`, `Dressing`                 |
| `transfer`         | Förflyttning     | Transfer assistance         | `Förflyttning`, `FÖRFLYTTNING`, `förflyttning`, `Transfer`           |
| `other`            | Övrigt           | Other services              | `Övrigt`, `ÖVRIGT`, `övrigt`, `Other`, `Annat`                       |

**Default behavior:** Unknown inset values → Skipped with **YELLOW** warning

**Multiple insets:** CSV cell contains comma-separated values → Split and map each individually

## Traffic-Light Validation

Caire data is validated by **category** with **severity levels**:

### Severity Levels

- **GREEN**: All valid, no issues
- **YELLOW**: Warnings (defaulted values, missing optional fields, geocoding needed)
- **RED**: Blocking errors (missing required fields, invalid formats, data inconsistencies)

### Validation Categories

#### 1. Clients

| Check           | Severity | Condition                                         |
| --------------- | -------- | ------------------------------------------------- |
| Required fields | RED      | Missing `name`, `street`, `postalCode`, or `city` |
| Address format  | RED      | Invalid postal code format                        |
| Coordinates     | YELLOW   | Missing `latitude` or `longitude`                 |
| Duplicate ID    | RED      | Same `externalId` used multiple times             |

#### 2. Employees

| Check           | Severity | Condition                                        |
| --------------- | -------- | ------------------------------------------------ |
| Required fields | RED      | Missing `employeeId`, `firstName`, or `lastName` |
| Shift times     | RED      | Invalid time format (not HH:MM)                  |
| Shift overlap   | YELLOW   | Employee has overlapping shifts                  |
| Duplicate ID    | RED      | Same `employeeId` used multiple times            |

#### 3. Visits

| Check            | Severity | Condition                                                |
| ---------------- | -------- | -------------------------------------------------------- |
| Required fields  | RED      | Missing `date`, `clientExternalId`, or `durationMinutes` |
| Date format      | RED      | Invalid ISO date (not YYYY-MM-DD)                        |
| Client reference | RED      | `clientExternalId` doesn't match any client              |
| Duration         | YELLOW   | Duration > 4 hours (unusual)                             |
| Duplicate ID     | RED      | Same `externalId` used multiple times                    |

#### 4. Insets

| Check         | Severity | Condition                                   |
| ------------- | -------- | ------------------------------------------- |
| Unknown inset | YELLOW   | Inset value not in canonical list (skipped) |
| No insets     | YELLOW   | Visit has no insets defined                 |

#### 5. Time Slots

| Check         | Severity | Condition                                                |
| ------------- | -------- | -------------------------------------------------------- |
| Unknown slot  | YELLOW   | Slot value not in canonical list (defaulted to `heldag`) |
| Time conflict | YELLOW   | `startTime` outside slot's typical window                |

#### 6. Dependencies

| Check               | Severity | Condition                                   |
| ------------------- | -------- | ------------------------------------------- |
| Invalid duration    | RED      | `minDelay` or `maxDelay` not valid ISO 8601 |
| Visit reference     | RED      | Visit ID doesn't exist                      |
| Circular dependency | RED      | Dependency chain creates a loop             |
| Max < Min           | RED      | `maxDelay` < `minDelay`                     |

### Validation Result Format

```typescript
{
  byCategory: {
    clients: {
      green: 45,    // 45 clients fully valid
      yellow: 3,    // 3 missing coordinates
      red: 0,       // No blocking errors
      items: [
        {
          severity: 'yellow',
          category: 'clients',
          message: 'Missing coordinates for client C123, geocoding needed',
          rowIndex: 5,
          field: 'latitude'
        }
      ]
    },
    visits: {
      green: 120,
      yellow: 5,    // 5 with unknown insets
      red: 2,       // 2 with invalid dates
      items: [...]
    },
    // ... other categories
  },
  blocking: false  // true if any category has red > 0
}
```

**UI Display:**

- Show category cards with traffic-light colors
- Expandable lists of issues per category
- Disable "Finalize Import" button if `blocking === true`
- Allow download of error report CSV

## Example: Attendo v3 CSV → Caire Conversion

### Input (Attendo v3 CSV excerpt)

```csv
Slinga,Datum,Starttid,Längd,När på dagen,Insatser,Klient-ID,Namn,Adress
EMP001,2026-03-20,09:30,45,Morgon,"Tillsyn,Måltid",C123,Anna Andersson,Storgatan 1
EMP001,2026-03-20,14:00,30,Eftermiddag,Dusch/bad,C124,Bo Berg,Lillgatan 5
EMP002,2026-03-21,,,Kväll,Medicinering,C123,Anna Andersson,Storgatan 1
```

### Output (Caire Format)

```typescript
{
  clients: [
    {
      externalId: 'C123',
      name: 'Anna Andersson',
      address: {
        street: 'Storgatan 1',
        postalCode: '12345',  // Parsed from full address or separate column
        city: 'Stockholm'
      }
    },
    {
      externalId: 'C124',
      name: 'Bo Berg',
      address: {
        street: 'Lillgatan 5',
        postalCode: '12346',
        city: 'Stockholm'
      }
    }
  ],
  employees: [
    {
      externalId: 'EMP001',
      firstName: 'Maria',
      lastName: 'Svensson',
      shifts: [/* derived from rows or separate file */]
    },
    {
      externalId: 'EMP002',
      firstName: 'Johan',
      lastName: 'Nilsson',
      shifts: []
    }
  ],
  visits: [
    {
      externalId: 'V1',  // Generated
      clientExternalId: 'C123',
      date: '2026-03-20',
      durationMinutes: 45,
      startTime: '09:30',
      timeSlot: 'morgon',  // Normalized from "Morgon"
      flexBeforeMinutes: 30,
      flexAfterMinutes: 30,
      insets: ['supervision', 'meal']  // Normalized from "Tillsyn,Måltid"
    },
    {
      externalId: 'V2',
      clientExternalId: 'C124',
      date: '2026-03-20',
      durationMinutes: 30,
      startTime: '14:00',
      timeSlot: 'eftermiddag',  // Normalized from "Eftermiddag"
      flexBeforeMinutes: 30,
      flexAfterMinutes: 30,
      insets: ['bath_shower']  // Normalized from "Dusch/bad"
    },
    {
      externalId: 'V3',
      clientExternalId: 'C123',
      date: '2026-03-21',
      durationMinutes: 30,  // Default if not specified
      startTime: undefined,  // No specific time
      timeSlot: 'kväll',  // Normalized from "Kväll"
      flexBeforeMinutes: 60,
      flexAfterMinutes: 60,
      insets: ['medication']  // Normalized from "Medicinering"
    }
  ],
  visitTemplates: [],
  dependencies: [],
  dateRange: { start: '2026-03-20', end: '2026-03-21' }
}
```

### Validation Warnings

```typescript
{
  byCategory: {
    clients: {
      green: 2,
      yellow: 2,  // Both missing coordinates
      red: 0,
      items: [
        {
          severity: 'yellow',
          category: 'clients',
          message: 'Missing coordinates for client C123, geocoding needed',
          field: 'latitude'
        },
        {
          severity: 'yellow',
          category: 'clients',
          message: 'Missing coordinates for client C124, geocoding needed',
          field: 'latitude'
        }
      ]
    },
    visits: {
      green: 3,
      yellow: 0,
      red: 0,
      items: []
    },
    // ... other categories all green
  },
  blocking: false
}
```

## Adapter Implementation Guide

### Step 1: Fuzzy Column Matching

```typescript
function normalizeHeader(header: string): string {
  return header
    .trim()
    .toLowerCase()
    .replace(/[_\s-]/g, "");
}

function matchColumn(
  actualHeaders: string[],
  canonical: string,
  aliases: string[],
): number {
  const allNames = [canonical, ...aliases];

  // 1. Exact match
  for (const name of allNames) {
    const idx = actualHeaders.indexOf(name);
    if (idx !== -1) return idx;
  }

  // 2. Case-insensitive match
  const lowerHeaders = actualHeaders.map((h) => h.toLowerCase());
  for (const name of allNames) {
    const idx = lowerHeaders.indexOf(name.toLowerCase());
    if (idx !== -1) return idx;
  }

  // 3. Normalized match
  const normalizedHeaders = actualHeaders.map(normalizeHeader);
  for (const name of allNames) {
    const idx = normalizedHeaders.indexOf(normalizeHeader(name));
    if (idx !== -1) return idx;
  }

  return -1; // Not found
}
```

### Step 2: Value Alias Resolution

```typescript
import { resolveSlot, resolveInset } from "./aliasMaps";

// In conversion logic:
const rawSlot = row[slotColumnIndex];
const { canonical: timeSlot, matched } = resolveSlot(
  rawSlot,
  DEFAULT_SLOT_ALIASES,
);

if (!matched) {
  warnings.push({
    severity: "yellow",
    category: "time_slots",
    message: `Unknown time slot "${rawSlot}", defaulted to "${timeSlot}"`,
    rowIndex: i,
    field: "timeSlot",
  });
}
```

### Step 3: Duration Normalization

```typescript
function parseDuration(input: string): string {
  // Parse Swedish duration formats to ISO 8601
  const normalized = input.toLowerCase().trim();

  // Match patterns like "3,5timmar", "2 timmar", "30 minuter"
  const hoursMatch = normalized.match(/(\d+(?:,\d+)?)\s*(?:timmar|timme|tim)/);
  const minutesMatch = normalized.match(/(\d+)\s*(?:minuter|min)/);

  let hours = 0;
  let minutes = 0;

  if (hoursMatch) {
    hours = parseFloat(hoursMatch[1].replace(",", "."));
  }

  if (minutesMatch) {
    minutes = parseInt(minutesMatch[1], 10);
  }

  // Convert to total minutes, then to ISO 8601
  const totalMinutes = hours * 60 + minutes;
  const h = Math.floor(totalMinutes / 60);
  const m = totalMinutes % 60;

  if (h > 0 && m > 0) {
    return `PT${h}H${m}M`;
  } else if (h > 0) {
    return `PT${h}H`;
  } else {
    return `PT${m}M`;
  }
}
```

## Integration with Existing System

### Current Flow (Before Caire)

```
CSV Upload → AttendoAdapter.parse() → importAttendoSchedule() → DB
                ↓
         Hardcoded column names
         Hardcoded INSET_NAME_MAP
         Ad-hoc string parsing
```

### New Flow (With Caire)

```
CSV Upload → AttendoAdapter.parse() → attendoToCaire() → validateCaire() → importFromCaire() → DB
                ↓                            ↓                  ↓
         Fuzzy column matching      Normalize values    Traffic-light check
         Flexible aliases          ISO 8601 durations   Category-based errors
```

**Benefits:**

- V3 CSV works without code changes
- New client strings added via config (no deployment)
- Single validation point (no scattered checks)
- Preview shows exactly what will be imported
- 80-90% data via CSV, 100% via resources CRUD

## Offline CSV Preparation (Future)

Python script to convert custom CSV → Caire middle CSV:

```python
# caire_converter.py
import pandas as pd

def convert_to_caire(input_csv, output_csv, column_map, slot_map, inset_map):
    """
    Convert custom CSV to Caire middle format

    Args:
        input_csv: Path to source CSV
        output_csv: Path to output Caire CSV
        column_map: Dict mapping source columns to canonical names
        slot_map: Dict mapping slot values to canonical IDs
        inset_map: Dict mapping inset values to canonical IDs
    """
    df = pd.read_csv(input_csv)

    # Rename columns using map
    df = df.rename(columns=column_map)

    # Map slot values
    df['timeSlot'] = df['timeSlot'].map(slot_map).fillna('heldag')

    # Map inset values (comma-separated)
    def map_insets(insets_str):
        if pd.isna(insets_str):
            return ''
        insets = [i.strip() for i in insets_str.split(',')]
        canonical = [inset_map.get(i, '') for i in insets]
        return ','.join([c for c in canonical if c])

    df['insets'] = df['insets'].apply(map_insets)

    # Normalize durations
    # ... (similar logic to TypeScript parser)

    df.to_csv(output_csv, index=False)
```

**Use case:** Client prepares CSV offline, uploads Caire-formatted file (100% green validation)

## Best Practices

1. **Always validate before finalizing**: Check traffic-light summary, address red issues
2. **Review yellow warnings**: Decide if defaults are acceptable or data needs fixes
3. **Use canonical values in CSV if possible**: Avoids alias matching edge cases
4. **Include all required fields**: Reduces red errors
5. **Provide coordinates when available**: Avoids geocoding step (yellow warning)
6. **Test with sample data first**: Verify column matching and value mapping before full import
7. **Document custom aliases**: If adding new client-specific strings, update alias maps
8. **Use ISO 8601 for durations in source CSV**: Bypasses parsing (e.g., `PT2H30M` instead of `"2,5timmar"`)

## FAQ

**Q: What if my CSV has different column names?**
A: Fuzzy matching handles most variations. If not recognized, update alias maps in `aliasMaps.ts`.

**Q: Can I skip optional fields?**
A: Yes. Missing optional fields may create yellow warnings (e.g., missing coordinates), but won't block import.

**Q: What happens to unknown inset values?**
A: They're skipped with a yellow warning. Visit is still created without that inset.

**Q: What if my time slot names are different?**
A: Update `DEFAULT_SLOT_ALIASES` in `aliasMaps.ts` to include new aliases, or use canonical names in CSV.

**Q: Can I upload a CSV without visit templates (only individual visits)?**
A: Yes. `visitTemplates` can be empty; all visits go in the `visits` array.

**Q: How do I handle double-staffing?**
A: Use the `groupId` field. Visits with the same `groupId` must be scheduled simultaneously.

**Q: Can I re-upload a CSV with corrections?**
A: Yes. Re-parse to see updated validation, then finalize. Existing schedule is replaced.

## References

- **Type definitions**: `apps/dashboard-server/src/services/schedule/import/caireFormat.ts`
- **Alias maps**: `apps/dashboard-server/src/services/schedule/import/aliasMaps.ts`
- **Validation logic**: `apps/dashboard-server/src/services/schedule/import/validateCaire.ts`
- **Attendo adapter**: `apps/dashboard-server/src/services/schedule/adapters/AttendoAdapter.ts`
- **Import flow**: `CSV_IMPORT_AND_VALIDATION_BEST_PRACTICES.md`
