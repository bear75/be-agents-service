# Data Model 2.0 Implementation Status

**Date:** 2026-01-27
**Status:** Backend Complete, Frontend Pending

## ✅ Completed (Backend)

### Phase 1: Database Schema Updates

#### Employee Model Changes

- ✅ Renamed `homeServiceAreaId` → `serviceAreaId` (nullable for multi-area employees)
- ✅ Added `gender` (String?)
- ✅ Added `status` (String, default: "active")
- ✅ Added `role` (String, default: "CAREGIVER")
- ✅ Added `startDate` (DateTime?)
- ✅ Added `endDate` (DateTime?)
- ✅ Added `phoniroEmployeeId` (String?)
- ✅ Added `recentClientVisits` (Json?, default: "[]")
- ✅ Home address fields kept as optional (homeAddress, homeLatitude, homeLongitude)

#### Client Model Changes

- ✅ Added `gender` (String?)
- ✅ Added `birthYear` (Int?) - less sensitive than full dateOfBirth
- ✅ Added `contactPerson` (String?) - CRITICAL for continuity tracking
- ✅ Added `address` (String?) - denormalized for quick access
- ✅ Added `latitude`, `longitude` (Decimal?) - denormalized
- ✅ Added `municipality` (String?)
- ✅ Added `careLevel` (String?)
- ✅ Added `diagnoses` (String[], default: []) - optional sensitive data
- ✅ Added `allergies` (String[], default: [])
- ✅ Added `languagePreference` (String?)

#### EmployeePreference Model (New)

- ✅ Created new model for bidirectional employee-client preferences
- ✅ Fields: preferredClientIds, avoidedClientIds, preferredDays, avoidedDays

#### Database Migration

- ✅ Migration created: `20260127063104_add_data_model_2_0_fields`
- ✅ Migration applied successfully
- ✅ Prisma client regenerated

### Phase 2: GraphQL Schema & Backend

#### GraphQL Type Definitions

- ✅ Updated Employee type with all new fields and relationships
- ✅ Updated Client type with all new fields and relationships
- ✅ Added new relationship types:
  - Address
  - ClientContact
  - ClientPreference
  - MonthlyAllocation
  - EmployeeSkill
  - EmployeeTag
  - EmployeeCost
  - EmployeePreference

#### GraphQL Input Types

- ✅ Updated CreateEmployeeInput with new fields
- ✅ Updated UpdateEmployeeInput with new fields
- ✅ Updated CreateClientInput with new fields
- ✅ Updated UpdateClientInput with new fields

#### Field Resolvers

- ✅ Employee field resolvers: skills, tags, costs, preferences
- ✅ Client field resolvers: addresses, primaryAddress, contacts, preferences, allocations

#### GraphQL Operations

- ✅ Updated all employee queries/mutations to use `serviceAreaId` (renamed from `homeServiceAreaId`)
- ✅ Updated all employee queries/mutations to include new fields (status, role, dates, etc.)
- ✅ Updated all client queries/mutations to include new fields (contactPerson, gender, etc.)

#### Code Generation

- ✅ TypeScript types regenerated from GraphQL schema
- ✅ React hooks regenerated for frontend use

---

## ⏳ Pending (Frontend)

### Phase 3: Frontend Forms

#### EmployeeForm Component (`apps/dashboard/src/components/Resources/Employee/EmployeeForm.tsx`)

**Required Changes:**

1. Rename `homeServiceAreaId` → `serviceAreaId` throughout
2. Update Zod schema to include:
   ```typescript
   gender: z.string().optional(),
   status: z.enum(["active", "inactive", "on_leave"]).default("active"),
   role: z.enum(["CAREGIVER", "DRIVER", "COORDINATOR", "SCHEDULER", "ADMIN"]).default("CAREGIVER"),
   startDate: z.string().optional(), // ISO date string
   endDate: z.string().optional(),
   transportMode: z.string().optional(),
   ```
3. Add form fields:
   - Gender (optional text or select)
   - Status (select: active, inactive, on_leave)
   - Role (select: CAREGIVER, DRIVER, COORDINATOR, SCHEDULER, ADMIN)
   - Start Date (date picker)
   - End Date (date picker)
   - Transport Mode (select: DRIVING, CYCLING, WALKING, PUBLIC_TRANSIT)
4. Update GraphQL mutation calls to include new fields
5. Update form reset in useEffect to populate new fields when editing

#### ClientForm Component (`apps/dashboard/src/components/Resources/Client/ClientForm.tsx`)

**Required Changes:**

1. Update Zod schema to include:
   ```typescript
   gender: z.string().optional(),
   birthYear: z.number().min(1900).max(new Date().getFullYear()).optional(),
   contactPerson: z.string().optional(), // CRITICAL field
   address: z.string().optional(),
   latitude: z.number().optional(),
   longitude: z.number().optional(),
   municipality: z.string().optional(),
   careLevel: z.string().optional(),
   diagnoses: z.array(z.string()).default([]),
   allergies: z.array(z.string()).default([]),
   languagePreference: z.string().optional(),
   ```
2. Add form fields:
   - Gender (optional select)
   - Birth Year (number input, 4 digits)
   - **Contact Person (text input) - PRIORITY FIELD**
   - Address (textarea for denormalized address)
   - Municipality (text input)
   - Care Level (text or select)
   - Diagnoses (tag input or comma-separated)
   - Allergies (tag input or comma-separated)
   - Language Preference (select)
3. Update GraphQL mutation calls to include new fields
4. Update form reset in useEffect to populate new fields when editing

#### New Components (Optional/Future)

These components can be created later for managing relationship data:

1. **EmployeeSkillsManager** - Manage employee skills with certification dates
2. **EmployeeCostManager** - Manage employee salary history
3. **ClientAddressManager** - Manage client addresses with geocoding
4. **ClientContactManager** - Manage emergency contacts
5. **ClientPreferenceManager** - Manage preferred/avoided employees
6. **MonthlyAllocationManager** - Track monthly hour allocations
7. **EmployeePreferenceManager** - Manage employee's preferred/avoided clients

---

## Implementation Notes

### Critical Fields Priority

**Must implement ASAP:**

1. `Client.contactPerson` - Required for caregiver continuity tracking (70% threshold)
2. `Employee.serviceAreaId` rename - Affects all employee queries
3. `Employee.status`, `Employee.role` - Core employment fields

**Should implement soon:** 4. `Client.gender`, `Client.birthYear` - Demographic data 5. `Employee.gender`, `Employee.startDate` - HR data 6. `Employee.transportMode` - Routing critical

**Can implement later:** 7. `Client.diagnoses`, `Client.allergies` - Safety/care data 8. Relationship management components - Nice to have for data entry

### Design Decisions

1. **serviceAreaId nullable** - Supports multi-area employees and org-level staff (scheduler, admin)
2. **birthYear instead of dateOfBirth** - Less sensitive (GDPR compliance)
3. **diagnoses optional** - Sensitive GDPR/DPIA data, use skill matching instead
4. **contactPerson as text** - Most flexible for CSV imports and initial rollout
5. **Home address kept optional** - User requested to keep for flexibility

### Data Migration Safety

- All new fields are nullable/optional - no data loss risk
- Field rename (homeServiceAreaId → serviceAreaId) completed via migration
- Existing data preserved

### Testing Requirements

Before deploying to production:

1. Test employee CRUD with new fields
2. Test client CRUD with new fields (especially contactPerson)
3. Verify relationship queries work (skills, contacts, preferences, etc.)
4. Test service area assignment for employees
5. Verify existing data still loads correctly

---

## Verification Commands

```bash
# Check database schema
yarn workspace dashboard-server db:studio

# Verify GraphQL schema
yarn workspace dashboard-server dev
# Open http://localhost:4000/graphql

# Test frontend forms
yarn workspace dashboard dev
# Open http://localhost:3001

# Run tests
yarn workspace dashboard-server test
```

---

## Documentation References

- **Data Model Spec:** `docs/docs_2.0/03-data/data-model.md`
- **Data Requirements:** `docs/docs_2.0/05-prd/pilots/attendo/DATA_REQUIREMENTS.md`
- **CSV Comparison:** `docs/docs_2.0/05-prd/bryntum_consultant_specs/CSV_DATA_MODEL_COMPARISON.md`
- **Schema File:** `apps/dashboard-server/schema.prisma`
- **Migration:** `apps/dashboard-server/migrations/20260127063104_add_data_model_2_0_fields/`

---

## Next Steps

1. Update EmployeeForm component (rename serviceAreaId, add new fields)
2. Update ClientForm component (add contactPerson and other new fields)
3. Test CRUD operations in dashboard UI
4. Optionally create relationship management components
5. Update CSV import/export to handle new fields
6. Deploy to staging for testing
