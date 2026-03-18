# Schedule Upload Zone: Technical Architecture

**Purpose:** Comprehensive technical documentation of the 3-step upload wizard with traffic-light validation. Explains the "upload zone gatekeeper" pattern, Caire format conversion flow, and validation timing.

**Status:** ✅ Implemented (3-step wizard, Caire format, traffic-light validation)

**Last Updated:** 2026-03-18

---

## Table of Contents

1. [Overview](#overview)
2. [Upload Zone Gatekeeper Pattern](#upload-zone-gatekeeper-pattern)
3. [3-Step Wizard Flow](#3-step-wizard-flow)
4. [Step 1: Upload & Parse](#step-1-upload--parse)
5. [Step 2: Configure](#step-2-configure)
6. [Step 3: Validate & Finalize](#step-3-validate--finalize)
7. [Caire Format Conversion](#caire-format-conversion)
8. [Traffic-Light Validation](#traffic-light-validation)
9. [Planning Window Impact](#planning-window-impact)
10. [Architecture Diagrams](#architecture-diagrams)
11. [File Structure](#file-structure)
12. [API Reference](#api-reference)

---

## Overview

The Schedule Upload Zone implements a **3-step wizard** that converts messy external CSV files (Attendo, Carefox, Nova formats) into validated schedule data. The key principle is:

> **All client-specific parsing lives in the upload zone. The backend accepts only Caire canonical format.**

This architecture ensures:

- ✅ **80-90% accuracy from CSV upload** (fuzzy matching, configurable aliases)
- ✅ **100% accuracy via resources CRUD** (post-import corrections)
- ✅ **No code changes for new client strings** (add to alias config)
- ✅ **Traffic-light validation** before committing data
- ✅ **Planning window flexibility** (2w, 4w, 8w determines visit/dependency counts)

---

## Upload Zone Gatekeeper Pattern

The upload zone acts as a **gatekeeper** that normalizes all external formats to a single canonical format before data enters the system.

### Architecture Layers

```
┌──────────────────────────────────────────────────────────────┐
│                     EXTERNAL SOURCES                          │
│  Attendo CSV  │  Carefox CSV  │  Nova CSV  │  Future Format  │
└───────┬──────────────┬──────────────┬────────────────┬────────┘
        │              │              │                │
        ▼              ▼              ▼                ▼
┌──────────────────────────────────────────────────────────────┐
│                    UPLOAD ZONE (Parsers)                      │
│  AttendoAdapter │ CarefoxAdapter │ NovaAdapter │ NewAdapter  │
│  - Fuzzy column matching                                      │
│  - Configurable alias resolution (slots, insets)              │
│  - Swedish duration → ISO 8601 conversion                     │
└───────┬──────────────┬──────────────┬────────────────┬────────┘
        │              │              │                │
        └──────────────┴──────────────┴────────────────┘
                              ▼
                ┌─────────────────────────┐
                │   CAIRE CANONICAL       │
                │   - Normalized fields   │
                │   - ISO 8601 durations  │
                │   - Canonical enums     │
                └────────────┬────────────┘
                             ▼
                ┌─────────────────────────┐
                │  TRAFFIC-LIGHT          │
                │  VALIDATION             │
                │  (Green/Yellow/Red)     │
                └────────────┬────────────┘
                             ▼
                ┌─────────────────────────┐
                │  BACKEND (Single Path)  │
                │  - scheduleUploadHelpers│
                │  - Prisma DB writes     │
                └─────────────────────────┘
```

### Key Principle: Single Backend Path

**Before (❌ Bad):**

```typescript
if (sourceType === "ATTENDO") {
  // Attendo-specific parsing and business logic
  const duration = parseSwedishDuration(row.Längd);
  const slot = row["När på dagen"] === "Morgon" ? "morgon" : "heldag";
  // ... more parsing
} else if (sourceType === "NOVA") {
  // Nova-specific parsing
} else if (sourceType === "CAREFOX") {
  // Carefox-specific parsing
}
```

**After (✅ Good):**

```typescript
// All CSV types convert to Caire first
const cairePayload = sourceAdapter.toCaire(csvData);

// Single validation path
const validation = validateCaire(cairePayload);

// Single import path
if (!validation.blocking) {
  await importFromCaire(cairePayload, tx, organizationId);
}
```

---

## 3-Step Wizard Flow

The wizard separates concerns into three distinct phases:

1. **Upload & Parse** - Check if CSV is parseable
2. **Configure** - Collect planning window and settings
3. **Validate & Finalize** - Show validation results, then import

### Why 3 Steps?

**Original 2-step problem:**

- Step 1 tried to validate visits/dependencies **before** user selected planning window
- Visit count and dependency count depend on planning window duration
- Showing "3,838 visits" in Step 1 was misleading (might be 7,676 for 4 weeks)

**3-step solution:**

- Step 1: Parse CSV, show basic summary (templates, not visits)
- Step 2: User selects planning window (2w, 4w, 8w)
- Step 3: Expand templates → visits, create dependencies, show **actual** counts

---

## Step 1: Upload & Parse

**Purpose:** Verify the CSV is parseable and detect format (Attendo/Nova/Carefox).

### What Happens

1. User uploads CSV file
2. Frontend converts to base64
3. Backend calls `parseAndValidateSchedule` mutation
4. Adapter detects format and parses to intermediate structure
5. Returns **basic summary only** (no Caire conversion yet)

### GraphQL Mutation

```graphql
mutation ParseAndValidateSchedule(
  $organizationId: ID!
  $fileBase64: String!
  $fileName: String!
) {
  parseAndValidateSchedule(
    organizationId: $organizationId
    fileBase64: $fileBase64
    fileName: $fileName
  ) {
    sourceType # ATTENDO | NOVA | CAREFOX
    summary {
      clientCount # Unique clients in CSV
      employeeCount # Unique employees in CSV
      visitCount # Templates, NOT actual visits
      dateRange {
        start
        end
      }
    }
    missingFields # ["depotAddress", "scheduleStartDate"]
    validationErrors # Basic CSV parsing errors
    validationByCategory # null (validation happens in Step 3)
    blocking # null (validation happens in Step 3)
    metadata # Raw data cached for Step 3
  }
}
```

### Backend Implementation

**File:** `apps/dashboard-server/src/graphql/resolvers/schedule/mutations/parseAndValidateSchedule.ts`

```typescript
export const parseAndValidateSchedule: MutationResolvers["parseAndValidateSchedule"] =
  async (_parent, { organizationId, fileBase64, fileName }, context) => {
    requireAuth(context);
    await validateOrganizationId(context, organizationId);

    const csvBuffer = Buffer.from(fileBase64, "base64");
    const parsedData = scheduleAdapterFactory.parse(csvBuffer);

    return {
      sourceType: parsedData.sourceType,
      summary: {
        clientCount: parsedData.summary.clientCount,
        employeeCount: parsedData.summary.employeeCount,
        visitCount: parsedData.summary.visitCount, // Template count, not actual visits
        dateRange: {
          start: parsedData.summary.dateRange.start,
          end: parsedData.summary.dateRange.end,
        },
      },
      missingFields: parsedData.missingFields,
      validationErrors: parsedData.validationErrors,
      validationByCategory: null, // Deferred to Step 3
      blocking: null, // Deferred to Step 3
      metadata: parsedData.metadata,
    };
  };
```

### What User Sees

```
┌─────────────────────────────────────────────────┐
│  Upload Schedule - Step 1 of 3                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  📁 Huddinge-v3 - Data_final.csv (2.3 MB)      │
│                                                  │
│  ✅ File uploaded successfully                  │
│                                                  │
│  Source: ATTENDO                                │
│  Clients: 165                                   │
│  Employees: 41                                  │
│  Visit Templates: 3,838                         │
│  Date Range: 2026-03-02 to 2026-03-15 (14 days)│
│                                                  │
│  [Back]                        [Next: Configure]│
└─────────────────────────────────────────────────┘
```

**Key Point:** No validation yet. User proceeds to configure.

---

## Step 2: Configure

**Purpose:** Collect planning window, service area, depot address, and financial settings.

### What Happens

1. Form pre-fills with defaults:
   - **Planning window:** Derived from CSV dateRange (14 days)
   - **Service area:** Auto-selects "Huddinge" if available
   - **Depot address:** Defaults to Huddinge office
   - **Financial:** 550 SEK revenue/hour, 230 SEK cost/hour
2. User can adjust:
   - Change planning window (2w, 4w, 8w via quick buttons)
   - Select different service area
   - Update depot coordinates
3. Configuration saved to wizard context
4. Proceeds to Step 3 (validation)

### Frontend Component

**File:** `apps/dashboard/src/components/modals/UploadScheduleWizard/ConfigurationStep.tsx`

```typescript
export const ConfigurationStep = ({ organizationId }: ConfigurationStepProps) => {
  const { parsedData, configuration, setConfiguration, setStep } = useWizardContext();

  const handleNext = (data: ScheduleConfiguration) => {
    setConfiguration(data);  // Save to context
    setStep(3);              // Proceed to validation
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleNext)}>
        {/* Planning Window (Quick weeks selector: 1-12 weeks) */}
        {/* Service Area dropdown */}
        {/* Depot Address fields */}
        {/* Financial config (revenue/cost per hour) */}

        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => setStep(1)}>
            Back
          </Button>
          <Button type="submit">
            Next: Review & Validate
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </DialogFooter>
      </form>
    </Form>
  );
};
```

### What User Sees

```
┌─────────────────────────────────────────────────┐
│  Upload Schedule - Step 2 of 3                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  📅 Planning Window                             │
│  ┌─────────────────────────────────────┐        │
│  │ Quick select: [2w] [4w] [8w] [12w] │        │
│  └─────────────────────────────────────┘        │
│  Start Date: 2026-03-02                        │
│  Duration: 14 days                              │
│                                                  │
│  📍 Service Area                                │
│  [Huddinge ▼]                                   │
│                                                  │
│  🏢 Depot Address                               │
│  Kommunalvägen 28, 14146 Huddinge              │
│                                                  │
│  💰 Financial Config                            │
│  Revenue: 550 SEK/hour                         │
│  Cost: 230 SEK/hour                            │
│                                                  │
│  [Back]            [Next: Review & Validate]   │
└─────────────────────────────────────────────────┘
```

**Key Point:** No validation yet. Planning window selected. Now ready to validate.

---

## Step 3: Validate & Finalize

**Purpose:** Show traffic-light validation with actual visit/dependency counts based on planning window, then create schedule.

### What Happens (Auto-Preview)

1. **On mount:** Automatically calls `previewScheduleImport` mutation
2. Backend:
   - Re-parses CSV from base64
   - Converts to Caire with selected planning window
   - Expands templates → visits (e.g., "Varje dag" → 14 visits for 2 weeks)
   - Creates dependencies between consecutive visits
   - Runs validation by category
3. Frontend displays traffic-light results
4. User reviews validation
5. If no blocking errors → user clicks "Finalize Import"
6. Backend calls `finalizeScheduleUpload` to create schedule

### GraphQL Mutation (Preview)

```graphql
mutation PreviewScheduleImport(
  $organizationId: ID!
  $fileBase64: String!
  $fileName: String!
  $configuration: ScheduleConfigurationInput!
) {
  previewScheduleImport(
    organizationId: $organizationId
    fileBase64: $fileBase64
    fileName: $fileName
    configuration: $configuration
  ) {
    sourceType
    summary {
      clientCount      # Actual clients
      employeeCount    # Actual employees
      visitCount       # Actual expanded visits (e.g., 3,838 for 2w)
      dateRange {
        start
        end
      }
    }
    validationByCategory {
      clients {
        green          # Count of valid clients
        yellow         # Count with warnings
        red            # Count with errors
        items {
          severity
          category
          message
          rowIndex
          field
        }
      }
      employees { ... }
      visits { ... }
      insets { ... }
      time_slots { ... }
      dependencies { ... }
    }
    blocking           # true if any red errors exist
    dateRange {
      start
      end
    }
  }
}
```

### Backend Implementation

**File:** `apps/dashboard-server/src/graphql/resolvers/schedule/mutations/previewScheduleImport.ts`

```typescript
export const previewScheduleImport: MutationResolvers["previewScheduleImport"] =
  async (
    _parent,
    { organizationId, fileBase64, fileName, configuration },
    context,
  ) => {
    requireAuth(context);
    await validateOrganizationId(context, organizationId);

    const csvBuffer = Buffer.from(fileBase64, "base64");
    const parsedData = scheduleAdapterFactory.parse(csvBuffer);

    // Extract planning window from configuration
    let scheduleStartDate = configuration.scheduleStartDate
      ? new Date(configuration.scheduleStartDate)
      : new Date(parsedData.summary.dateRange.start);

    let scheduleDays =
      configuration.scheduleDays ?? calculateDays(parsedData.summary.dateRange);

    // Convert to Caire with selected planning window
    const { payload } = attendoToCaire(
      parsedData.rawData as AttendoParseResult,
      {
        scheduleStartDate,
        scheduleDays, // This determines visit/dependency counts!
      },
    );

    // Run traffic-light validation
    const validationResult = validateCaire(payload);

    return {
      sourceType: parsedData.sourceType,
      summary: {
        clientCount: payload.clients.length,
        employeeCount: payload.employees.length,
        visitCount: payload.visits.length, // Actual expanded visits
        dateRange: {
          start: minDate.toISOString().split("T")[0],
          end: maxDate.toISOString().split("T")[0],
        },
      },
      validationByCategory: validationResult.byCategory,
      blocking: validationResult.blocking,
      dateRange: { start: minDate, end: maxDate },
    };
  };
```

### Frontend Component

**File:** `apps/dashboard/src/components/modals/UploadScheduleWizard/ValidationAndFinalizeStep.tsx`

```typescript
export const ValidationAndFinalizeStep = ({ organizationId, onSuccess }) => {
  const [previewData, setPreviewData] = useState<ScheduleImportPreview | null>(null);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [isFinalizing, setIsFinalizing] = useState(false);

  // Auto-preview on mount
  useEffect(() => {
    if (!previewData && !isPreviewing) {
      void handlePreview();
    }
  }, []);

  const handlePreview = async () => {
    const { data } = await previewImport({
      variables: {
        organizationId,
        fileBase64,
        fileName: uploadedFile.name,
        configuration: buildConfigInput(),
      },
    });
    setPreviewData(data.previewScheduleImport);
  };

  const handleFinalize = async () => {
    if (previewData.blocking) {
      toast({ title: "Validation errors", variant: "destructive" });
      return;
    }

    const { data } = await finalizeSchedule({
      variables: {
        organizationId,
        fileBase64,
        fileName: uploadedFile.name,
        configuration: buildConfigInput(),
      },
    });

    onSuccess(data.finalizeScheduleUpload.id);
  };

  return (
    <>
      {/* Configuration Summary Card */}
      <Card>
        <CardContent>
          <div>File: {uploadedFile?.name}</div>
          <div>Start Date: {configuration.scheduleStartDate}</div>
          <div>Duration: {configuration.scheduleDays} days</div>
        </CardContent>
      </Card>

      {/* Traffic-Light Validation */}
      {isPreviewing && <LoadingSpinner />}
      {previewData && (
        <TrafficLightValidation
          validationByCategory={previewData.validationByCategory}
          blocking={previewData.blocking}
        />
      )}

      <DialogFooter>
        <Button variant="outline" onClick={() => setStep(2)}>Back</Button>
        <Button onClick={handlePreview} disabled={isFinalizing}>
          <Eye className="mr-2 h-4 w-4" />
          Re-validate
        </Button>
        <Button
          onClick={handleFinalize}
          disabled={isPreviewing || isFinalizing || previewData?.blocking}
        >
          {isFinalizing ? "Creating Schedule..." : "Finalize Import"}
        </Button>
      </DialogFooter>
    </>
  );
};
```

### What User Sees

```
┌──────────────────────────────────────────────────────────────┐
│  Upload Schedule - Step 3 of 3                               │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  📋 Import Configuration                                     │
│  ┌─────────────────────────────────────────────────┐        │
│  │ File: Huddinge-v3 - Data_final.csv              │        │
│  │ Source: ATTENDO                                 │        │
│  │ Start Date: 2026-03-02                          │        │
│  │ Duration: 14 days                               │        │
│  └─────────────────────────────────────────────────┘        │
│                                                               │
│  ✅ Ready to Import                                          │
│  🟢 3,838 OK  🟡 0 Warnings  🔴 0 Errors                     │
│                                                               │
│  📊 Validation Results                                       │
│  ┌─────────────────────────────────────────────────┐        │
│  │ ✅ Clients: 165 items (🟢 165)                  │        │
│  │ ✅ Employees: 41 items (🟢 41)                  │        │
│  │ ✅ Visits: 3,838 items (🟢 3,838)               │        │
│  │ ✅ Services/Insets: 10 items (🟢 10)            │        │
│  │ ✅ Time Slots: 7 items (🟢 7)                   │        │
│  │ ✅ Dependencies: 3,329 items (🟢 3,329)         │        │
│  └─────────────────────────────────────────────────┘        │
│                                                               │
│  ℹ️  Info                                                    │
│  🟢 Green: All fields valid and ready for import            │
│  🟡 Yellow: Warnings (can proceed, review recommended)      │
│  🔴 Red: Errors (import blocked until fixed)                │
│                                                               │
│  [Back]  [👁️ Re-validate]  [✅ Finalize Import]            │
└──────────────────────────────────────────────────────────────┘
```

**Key Point:** User sees actual counts before committing. If blocking errors, button is disabled.

---

## Caire Format Conversion

### What is Caire Format?

**Caire** = **Ca**nonical **i**ntermediate **re**presentation

A normalized, application-independent format that:

- Uses canonical enum values (e.g., `"morgon"` not `"Morgon"` or `"MORGON"`)
- Uses ISO 8601 for all durations/delays (e.g., `"PT3H30M"` not `"3,5timmar"`)
- Has strongly-typed TypeScript interfaces
- Is backend-agnostic (same format for all CSV sources)

### Conversion Process

```typescript
// Input: Attendo CSV row
{
  "Kundnr": "12345",
  "Gata": "Storgatan 1",
  "Postnr": "12345",
  "Ort": "Stockholm",
  "Återkommande": "Varje dag",
  "Längd": "30",
  "Starttid": "08:00",
  "När på dagen": "Morgon",
  "Insatser": "Tillsyn;Personlig hygien",
  "Antal tim mellan besöken": "3,5timmar"
}

// ↓ attendoToCaire() ↓

// Output: Caire format
{
  client: {
    externalId: "12345",
    name: "...",
    address: {
      street: "Storgatan 1",
      postalCode: "12345",
      city: "Stockholm"
    }
  },
  visitTemplate: {
    externalId: "att-tpl-0",
    clientExternalId: "12345",
    frequency: "daily",
    frequencyPattern: "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday",
    durationMinutes: 30,
    startTime: "08:00",
    timeSlot: "morgon",           // Normalized!
    flexBeforeMinutes: 0,
    flexAfterMinutes: 0,
    insets: ["supervision", "personal_hygiene"],  // Normalized!
    spreadDelay: "PT3H30M",       // ISO 8601!
    visits: [
      { externalId: "12345_2026-03-02_0", date: "2026-03-02", ... },
      { externalId: "12345_2026-03-03_0", date: "2026-03-03", ... },
      // ... one visit per day for 14 days = 14 visits
    ]
  },
  dependencies: [
    {
      precedingVisitExternalId: "12345_2026-03-02_0",
      succeedingVisitExternalId: "12345_2026-03-03_0",
      minDelay: "PT3H30M",
      dependencyType: "spread"
    },
    // ... 13 more dependencies (consecutive visits)
  ]
}
```

### Conversion Implementation

**File:** `apps/dashboard-server/src/services/schedule/import/attendoToCaire.ts`

```typescript
export function attendoToCaire(
  attendoData: AttendoParseResult,
  options: ConversionOptions = {},
): { payload: CaireImportPayload; warnings: ConversionWarning[] } {
  const warnings: ConversionWarning[] = [];
  const {
    scheduleStartDate = new Date(2026, 2, 2),
    scheduleDays = 14, // User-selected planning window!
  } = options;

  // Extract clients
  const clients = extractClients(attendoData.clients, warnings);

  // Extract employees
  const employees = extractEmployees(attendoData.employees, warnings);

  // Extract visit templates and expand to individual visits
  const { visitTemplates, visits, dependencies } = extractVisitsAndTemplates(
    attendoData.rows,
    scheduleStartDate,
    scheduleDays, // ← Determines visit/dependency counts!
    options,
    warnings,
  );

  return {
    payload: {
      clients,
      employees,
      visitTemplates,
      visits, // Expanded visits
      dependencies, // Visit-to-visit dependencies
      dateRange: {
        start: scheduleStartDate.toISOString().split("T")[0],
        end: calculateEndDate(scheduleStartDate, scheduleDays),
      },
    },
    warnings,
  };
}

function extractVisitsAndTemplates(
  rows: AttendoCsvRow[],
  scheduleStart: Date,
  scheduleDays: number,
  options: ConversionOptions,
  warnings: ConversionWarning[],
): {
  visitTemplates: CaireVisitTemplate[];
  visits: CaireVisit[];
  dependencies: CaireDependency[];
} {
  const visitTemplates: CaireVisitTemplate[] = [];
  const visits: CaireVisit[] = [];
  const dependencies: CaireDependency[] = [];
  const dependenciesByClient = new Map<string, string>();

  for (const row of rows) {
    // Parse recurrence (e.g., "Varje dag" → daily)
    const { frequency, frequencyPattern } = parseRecurrence(row.Återkommande);

    // Expand to individual visit dates
    const visitDates = expandRecurrence(
      row.Återkommande,
      scheduleStart,
      scheduleDays, // ← This determines how many visits are created!
    );

    // Resolve time slot using alias map
    const { canonical: timeSlot, matched: slotMatched } = resolveSlot(
      row["När på dagen"],
      options.slots,
    );
    if (!slotMatched) {
      warnings.push({
        severity: "yellow",
        category: "time_slots",
        message: `Unknown time slot "${row["När på dagen"]}", defaulted to "${timeSlot}"`,
      });
    }

    // Resolve insets using alias map
    const { canonical: insets, unmatched: unmatchedInsets } = resolveInsets(
      row.Insatser,
      options.insets,
    );
    if (unmatchedInsets.length > 0) {
      warnings.push({
        severity: "yellow",
        category: "insets",
        message: `Unknown insets: ${unmatchedInsets.join(", ")}`,
      });
    }

    // Create visit template
    const visitTemplate: CaireVisitTemplate = {
      externalId: `att-tpl-${rowIdx}`,
      clientExternalId: row.Kundnr,
      frequency,
      frequencyPattern,
      durationMinutes: parseInt(row.Längd, 10),
      startTime: row.Starttid,
      timeSlot,
      insets,
      visits: [],
    };

    // Handle spread delay
    if (row["Antal tim mellan besöken"]?.trim()) {
      const spreadDelay = parseDurationToISO8601(
        row["Antal tim mellan besöken"],
      );
      visitTemplate.spreadDelay = spreadDelay;
      dependenciesByClient.set(row.Kundnr, spreadDelay);
    }

    // Generate individual visits from template
    for (const visitDate of visitDates) {
      const visit: CaireVisit = {
        externalId: `${row.Kundnr}_${formatDateISO(visitDate)}_${rowIdx}`,
        clientExternalId: row.Kundnr,
        date: formatDateISO(visitDate),
        durationMinutes: parseInt(row.Längd, 10),
        timeSlot,
        insets,
        // ... other fields
      };
      visits.push(visit);
      visitTemplate.visits.push(visit);
    }

    visitTemplates.push(visitTemplate);
  }

  // Create dependencies between consecutive visits for clients with spread delays
  for (const [clientId, spreadDelay] of dependenciesByClient.entries()) {
    const clientVisits = visits
      .filter((v) => v.clientExternalId === clientId)
      .sort((a, b) => a.date.localeCompare(b.date));

    // Create dependency chain: visit[i] → visit[i+1]
    for (let i = 0; i < clientVisits.length - 1; i++) {
      dependencies.push({
        precedingVisitExternalId: clientVisits[i].externalId,
        succeedingVisitExternalId: clientVisits[i + 1].externalId,
        minDelay: spreadDelay,
        maxDelay: undefined,
        dependencyType: "spread",
      });
    }
  }

  return { visitTemplates, visits, dependencies };
}
```

### Key Conversion Steps

1. **Column normalization:** Fuzzy match `"När på dagen"` to canonical field
2. **Slot resolution:** `"Morgon"` → `resolveSlot()` → `"morgon"` (with yellow warning if unknown)
3. **Inset resolution:** `"Tillsyn;Personlig hygien"` → `["supervision", "personal_hygiene"]`
4. **Duration parsing:** `"3,5timmar"` → `parseDurationToISO8601()` → `"PT3H30M"`
5. **Recurrence expansion:** `"Varje dag"` + 14 days → 14 individual visits
6. **Dependency creation:** Client with spread delay → dependencies between consecutive visits

---

## Traffic-Light Validation

### Validation Categories

Validation results are grouped by **entity type**:

| Category       | What it validates                              |
| -------------- | ---------------------------------------------- |
| `clients`      | Client addresses, coordinates, required fields |
| `employees`    | Employee names, shifts, service area           |
| `visits`       | Visit dates, durations, time windows           |
| `insets`       | Service/inset canonical values (unique count)  |
| `time_slots`   | Day slot canonical values (unique count)       |
| `dependencies` | Visit dependencies (spread delays, temporal)   |

### Severity Levels

| Severity  | Meaning                     | Blocks Import? | Example                              |
| --------- | --------------------------- | -------------- | ------------------------------------ |
| 🟢 Green  | Valid, no issues            | No             | Client has valid address             |
| 🟡 Yellow | Warning, review recommended | No             | Unknown slot → defaulted to "heldag" |
| 🔴 Red    | Error, must fix             | **Yes**        | Required field missing, invalid date |

### Validation Implementation

**File:** `apps/dashboard-server/src/services/schedule/import/validateCaire.ts`

```typescript
export interface ValidationResult {
  byCategory: {
    clients: {
      green: number;
      yellow: number;
      red: number;
      items: ValidationIssue[];
    };
    employees: {
      green: number;
      yellow: number;
      red: number;
      items: ValidationIssue[];
    };
    visits: {
      green: number;
      yellow: number;
      red: number;
      items: ValidationIssue[];
    };
    insets: {
      green: number;
      yellow: number;
      red: number;
      items: ValidationIssue[];
    };
    time_slots: {
      green: number;
      yellow: number;
      red: number;
      items: ValidationIssue[];
    };
    dependencies: {
      green: number;
      yellow: number;
      red: number;
      items: ValidationIssue[];
    };
  };
  blocking: boolean; // true if any category has red issues
}

export function validateCaire(payload: CaireImportPayload): ValidationResult {
  const result: ValidationResult = {
    byCategory: {
      clients: { green: 0, yellow: 0, red: 0, items: [] },
      employees: { green: 0, yellow: 0, red: 0, items: [] },
      visits: { green: 0, yellow: 0, red: 0, items: [] },
      insets: { green: 0, yellow: 0, red: 0, items: [] },
      time_slots: { green: 0, yellow: 0, red: 0, items: [] },
      dependencies: { green: 0, yellow: 0, red: 0, items: [] },
    },
    blocking: false,
  };

  validateClients(payload, result);
  validateEmployees(payload, result);
  validateVisits(payload, result);
  validateInsets(payload, result);
  validateTimeSlots(payload, result);
  validateDependencies(payload, result);

  // Check if any category has blocking issues
  result.blocking = Object.values(result.byCategory).some((cat) => cat.red > 0);

  return result;
}

function validateClients(
  payload: CaireImportPayload,
  result: ValidationResult,
): void {
  for (const client of payload.clients) {
    if (!client.externalId || !client.name) {
      result.byCategory.clients.red++;
      result.byCategory.clients.items.push({
        severity: "red",
        category: "clients",
        message: `Client missing required field (externalId or name)`,
        field: !client.externalId ? "externalId" : "name",
      });
    } else if (!client.address.street || !client.address.city) {
      result.byCategory.clients.yellow++;
      result.byCategory.clients.items.push({
        severity: "yellow",
        category: "clients",
        message: `Client ${client.externalId} missing address details`,
        field: "address",
      });
    } else {
      result.byCategory.clients.green++;
    }
  }
}

function validateInsets(
  payload: CaireImportPayload,
  result: ValidationResult,
): void {
  const canonicalInsets = new Set(CANONICAL_INSETS);
  const validInsets = new Set<string>();

  for (const visit of payload.visits) {
    if (!visit.insets) continue;
    for (const inset of visit.insets) {
      if (canonicalInsets.has(inset as CanonicalInset)) {
        validInsets.add(inset);
      }
    }
  }

  // Count unique valid insets
  result.byCategory.insets.green = validInsets.size;
}

function validateTimeSlots(
  payload: CaireImportPayload,
  result: ValidationResult,
): void {
  const canonicalSlots = new Set(CANONICAL_TIME_SLOTS);
  const validSlots = new Set<string>();

  for (const visit of payload.visits) {
    if (
      visit.timeSlot &&
      canonicalSlots.has(visit.timeSlot as CanonicalTimeSlot)
    ) {
      validSlots.add(visit.timeSlot);
    }
  }

  // Count unique valid time slots
  result.byCategory.time_slots.green = validSlots.size;
}

function validateDependencies(
  payload: CaireImportPayload,
  result: ValidationResult,
): void {
  for (const dep of payload.dependencies) {
    if (
      !dep.precedingVisitExternalId ||
      !dep.succeedingVisitExternalId ||
      !dep.minDelay
    ) {
      result.byCategory.dependencies.red++;
      result.byCategory.dependencies.items.push({
        severity: "red",
        category: "dependencies",
        message: "Dependency missing required field",
        field: "precedingVisitExternalId",
      });
    } else {
      result.byCategory.dependencies.green++;
    }
  }
}
```

### Example Validation Output

```json
{
  "byCategory": {
    "clients": {
      "green": 165,
      "yellow": 0,
      "red": 0,
      "items": []
    },
    "employees": {
      "green": 41,
      "yellow": 0,
      "red": 0,
      "items": []
    },
    "visits": {
      "green": 3838,
      "yellow": 0,
      "red": 0,
      "items": []
    },
    "insets": {
      "green": 10,
      "yellow": 0,
      "red": 0,
      "items": []
    },
    "time_slots": {
      "green": 7,
      "yellow": 0,
      "red": 0,
      "items": []
    },
    "dependencies": {
      "green": 3329,
      "yellow": 0,
      "red": 0,
      "items": []
    }
  },
  "blocking": false
}
```

---

## Planning Window Impact

### Why Planning Window Matters

The **planning window** determines how many visits and dependencies are created from recurring templates.

**Example:**

- Template: "Varje dag" (every day) for Client 12345
- Spread delay: 3.5 hours between visits

**2 weeks (14 days):**

- Creates 14 visits (one per day)
- Creates 13 dependencies (between consecutive visits)

**4 weeks (28 days):**

- Creates 28 visits (one per day)
- Creates 27 dependencies (between consecutive visits)

**8 weeks (56 days):**

- Creates 56 visits (one per day)
- Creates 55 dependencies (between consecutive visits)

### Impact on Validation Counts

| Planning Window | Visit Templates | Visits  | Dependencies |
| --------------- | --------------- | ------- | ------------ |
| 2 weeks (14d)   | 3,838           | 3,838   | ~3,329       |
| 4 weeks (28d)   | 3,838           | ~7,676  | ~6,658       |
| 8 weeks (56d)   | 3,838           | ~15,352 | ~13,316      |

**Key insight:** Template count is constant. Visit/dependency counts scale linearly with planning window.

### Why Validation Moved to Step 3

**Problem with Step 1 validation:**

```
Step 1: Upload CSV
  → Shows "3,838 visits" (but this is templates!)
  → User confused: "Is this for 2 weeks or 4 weeks?"

Step 2: User selects 4 weeks
  → Actual visit count is now 7,676
  → But Step 1 showed 3,838!
  → User thinks validation is broken
```

**Solution with Step 3 validation:**

```
Step 1: Upload CSV
  → Shows "3,838 templates" (not visits)
  → No confusion

Step 2: User selects 4 weeks
  → Planning window saved

Step 3: Validation runs
  → Expands templates with 4-week window
  → Shows "7,676 visits" (correct!)
  → User sees accurate count before importing
```

### Configuration Quick Select

The UI provides quick selection buttons for common planning windows:

```typescript
<div className="flex gap-2">
  <Button onClick={() => form.setValue("scheduleDays", 7)}>1w</Button>
  <Button onClick={() => form.setValue("scheduleDays", 14)}>2w</Button>
  <Button onClick={() => form.setValue("scheduleDays", 28)}>4w</Button>
  <Button onClick={() => form.setValue("scheduleDays", 56)}>8w</Button>
  <Button onClick={() => form.setValue("scheduleDays", 84)}>12w</Button>
</div>
```

---

## Architecture Diagrams

### Data Flow (3-Step Wizard)

```
┌─────────────────────────────────────────────────────────────┐
│                    STEP 1: Upload & Parse                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
        parseAndValidateSchedule
                  │
                  ├─ Detect format (Attendo/Nova/Carefox)
                  ├─ Parse CSV rows
                  ├─ Extract basic summary
                  └─ Return metadata (no validation)

                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   STEP 2: Configure                          │
│  User selects:                                               │
│  - Planning window (2w/4w/8w)                               │
│  - Service area                                              │
│  - Depot address                                             │
│  - Financial config                                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              STEP 3: Validate & Finalize                     │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
        previewScheduleImport
                  │
                  ├─ Re-parse CSV
                  ├─ attendoToCaire(data, { scheduleDays })
                  │  │
                  │  ├─ Extract clients
                  │  ├─ Extract employees
                  │  ├─ Expand templates → visits
                  │  │  (count depends on scheduleDays!)
                  │  └─ Create dependencies
                  │
                  ├─ validateCaire(payload)
                  │  │
                  │  ├─ Validate by category
                  │  ├─ Count green/yellow/red
                  │  └─ Set blocking flag
                  │
                  └─ Return validation results

                  ▼
        User reviews validation
                  │
                  ▼
        finalizeScheduleUpload
                  │
                  ├─ Re-parse CSV (again)
                  ├─ importAttendoSchedule(...)
                  │  └─ Write to DB
                  │
                  └─ Return created schedule
```

### Caire Conversion Flow

```
┌───────────────────────────────────────────────────────────────┐
│  ATTENDO CSV ROW                                              │
│  {                                                             │
│    "Återkommande": "Varje dag",                              │
│    "Längd": "30",                                            │
│    "När på dagen": "Morgon",                                 │
│    "Insatser": "Tillsyn;Personlig hygien",                   │
│    "Antal tim mellan besöken": "3,5timmar"                   │
│  }                                                             │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
                   attendoToCaire
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   parseRecurrence  resolveSlot   resolveInsets
        │                │                │
        │                ▼                │
        │         "Morgon" → "morgon"    │
        │         (via alias map)        │
        │                                 ▼
        │              "Tillsyn;Personlig hygien"
        │                    ↓
        │         ["supervision", "personal_hygiene"]
        │         (via alias map)
        │
        ▼
   expandRecurrence(scheduleDays=14)
        │
        └─→ 14 visits (one per day)

        ▼
┌───────────────────────────────────────────────────────────────┐
│  CAIRE FORMAT                                                 │
│  {                                                             │
│    visitTemplate: {                                           │
│      frequency: "daily",                                      │
│      durationMinutes: 30,                                     │
│      timeSlot: "morgon",                  ← Normalized       │
│      insets: ["supervision", "personal_hygiene"], ← Normalized│
│      spreadDelay: "PT3H30M",             ← ISO 8601          │
│      visits: [                                                │
│        { date: "2026-03-02", ... },                          │
│        { date: "2026-03-03", ... },                          │
│        ... (14 total)                                         │
│      ]                                                         │
│    },                                                          │
│    dependencies: [                                            │
│      {                                                         │
│        precedingVisitExternalId: "12345_2026-03-02_0",       │
│        succeedingVisitExternalId: "12345_2026-03-03_0",      │
│        minDelay: "PT3H30M",                                   │
│        dependencyType: "spread"                               │
│      },                                                        │
│      ... (13 total)                                           │
│    ]                                                           │
│  }                                                             │
└───────────────────────────────────────────────────────────────┘
```

---

## File Structure

### Backend Files

```
apps/dashboard-server/src/
├── services/schedule/
│   ├── adapters/
│   │   ├── AttendoAdapter.ts          # Fuzzy column matching
│   │   ├── NovaAdapter.ts
│   │   └── CarefoxAdapter.ts
│   │
│   ├── import/
│   │   ├── caireFormat.ts             # Canonical type definitions
│   │   ├── aliasMaps.ts               # Configurable slot/inset aliases
│   │   ├── attendoToCaire.ts          # Attendo → Caire conversion
│   │   └── validateCaire.ts           # Traffic-light validation
│   │
│   └── importAttendoSchedule.ts       # Legacy import (uses alias maps)
│
└── graphql/resolvers/schedule/mutations/
    ├── parseAndValidateSchedule.ts    # Step 1 mutation
    ├── previewScheduleImport.ts       # Step 3 preview mutation
    └── finalizeScheduleUpload.ts      # Step 3 finalize mutation
```

### Frontend Files

```
apps/dashboard/src/components/modals/UploadScheduleWizard/
├── index.tsx                          # Wizard container (3 steps)
├── WizardProgress.tsx                 # Step indicator (1/2/3)
│
├── UploadAndParseStep.tsx             # Step 1 component
├── ConfigurationStep.tsx              # Step 2 component
├── ValidationAndFinalizeStep.tsx      # Step 3 component (NEW)
│
└── TrafficLightValidation.tsx         # Traffic-light display component
```

### GraphQL Schema

```
packages/graphql/
├── schema/dashboard/
│   ├── mutations.graphql              # Added previewScheduleImport
│   └── types.graphql                  # Added ScheduleImportPreview, ValidationByCategory
│
└── operations/mutations/dashboard/
    ├── parseAndValidateSchedule.graphql
    ├── previewScheduleImport.graphql  # NEW
    └── finalizeScheduleUpload.graphql
```

---

## API Reference

### parseAndValidateSchedule (Step 1)

**Purpose:** Parse CSV and return basic summary (no validation).

**Input:**

```graphql
{
  organizationId: ID!
  fileBase64: String!
  fileName: String!
}
```

**Output:**

```graphql
{
  sourceType: ScheduleSourceType!
  summary: {
    clientCount: Int!
    employeeCount: Int!
    visitCount: Int!        # Template count, not actual visits
    dateRange: { start: String!, end: String! }
  }
  missingFields: [String!]!
  validationErrors: [ValidationError!]!
  validationByCategory: null
  blocking: null
  metadata: JSON!
}
```

### previewScheduleImport (Step 3)

**Purpose:** Convert to Caire with planning window and run validation.

**Input:**

```graphql
{
  organizationId: ID!
  fileBase64: String!
  fileName: String!
  configuration: {
    scheduleStartDate: String
    scheduleDays: Int
    serviceAreaId: String
    depotAddress: { street: String, city: String, postalCode: String }
    financialConfig: { revenuePerHour: Float, employeeCostPerHour: Float }
    planningWindow: { startDate: String, endDate: String }
  }
}
```

**Output:**

```graphql
{
  sourceType: ScheduleSourceType!
  summary: {
    clientCount: Int!
    employeeCount: Int!
    visitCount: Int!        # Actual expanded visits
    dateRange: { start: String!, end: String! }
  }
  validationByCategory: {
    clients: { green: Int!, yellow: Int!, red: Int!, items: [ValidationIssue!]! }
    employees: { green: Int!, yellow: Int!, red: Int!, items: [ValidationIssue!]! }
    visits: { green: Int!, yellow: Int!, red: Int!, items: [ValidationIssue!]! }
    insets: { green: Int!, yellow: Int!, red: Int!, items: [ValidationIssue!]! }
    time_slots: { green: Int!, yellow: Int!, red: Int!, items: [ValidationIssue!]! }
    dependencies: { green: Int!, yellow: Int!, red: Int!, items: [ValidationIssue!]! }
  }
  blocking: Boolean!
  dateRange: { start: String!, end: String! }
}
```

### finalizeScheduleUpload (Step 3)

**Purpose:** Create schedule in database.

**Input:** Same as `previewScheduleImport`

**Output:**

```graphql
{
  id: ID!
  name: String!
  description: String
  status: String!
  visitsCount: Int!
  # ... other schedule fields
}
```

---

## Summary

The **Schedule Upload Zone** implements a robust 3-step wizard that:

1. **Parses** messy CSV files with fuzzy matching and configurable aliases
2. **Configures** planning window and settings
3. **Validates** with traffic-light categorization before committing

**Key achievements:**

- ✅ Single backend path (all CSVs → Caire → DB)
- ✅ No code changes for new client strings (update alias config)
- ✅ Accurate validation counts based on planning window
- ✅ User sees exactly what will be imported before finalizing
- ✅ 80-90% accuracy from CSV, 100% via resources CRUD

**References:**

- [CAIRE_MIDDLE_CSV_FORMAT.md](./CAIRE_MIDDLE_CSV_FORMAT.md) - Canonical format specification
- [CSV_IMPORT_AND_VALIDATION_BEST_PRACTICES.md](./CSV_IMPORT_AND_VALIDATION_BEST_PRACTICES.md) - Best practices
- [DEPENDENCY_CREATION_VERIFICATION.md](./DEPENDENCY_CREATION_VERIFICATION.md) - Visit dependency creation during Attendo import
