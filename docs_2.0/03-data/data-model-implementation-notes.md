# Data Model 2.0 - Implementation Notes

**Date:** 2026-01-27
**Migration:** `20260127063104_add_data_model_2_0_fields`
**Status:** Backend Complete, Frontend Pending

---

## Implementation vs Documentation Differences

This document captures the differences between the target schema in `data-model.md` and the actual implemented schema in `schema.prisma`.

### Employee Model

#### Differences from Documentation

| Field in Docs                               | Field in Implementation                                   | Notes                                                                                         |
| ------------------------------------------- | --------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `name` (single field)                       | `firstName`, `lastName`                                   | Split into two fields for better data structure                                               |
| `monthlySalary`, `hourlySalary` on employee | Moved to `EmployeeCost` table                             | Separate table allows salary history tracking                                                 |
| Home address NOT stored (docs line 232)     | `homeAddress`, `homeLatitude`, `homeLongitude` (optional) | **Kept as optional per user decision** for flexibility                                        |
| `homeServiceAreaId`                         | `serviceAreaId`                                           | **Renamed** - nullable to support multi-area employees and org-level staff (scheduler, admin) |

#### Implemented Fields (matching docs)

- ✅ `gender` (String?, optional)
- ✅ `status` (String, default: "active") - values: active, inactive, on_leave
- ✅ `role` (String, default: "CAREGIVER") - values: CAREGIVER, DRIVER, COORDINATOR, SCHEDULER, ADMIN
- ✅ `startDate` (DateTime?)
- ✅ `endDate` (DateTime?)
- ✅ `phoniroEmployeeId` (String?)
- ✅ `recentClientVisits` (Json?, default: "[]")
- ✅ `transportMode` (String?)
- ✅ `contractType` (Enum: full_time, part_time, hourly)
- ✅ `contractedHoursPerWeek` (Decimal?)
- ✅ `employmentPercentage` (Decimal?)
- ✅ `maxHoursPerDay` (Decimal?)
- ✅ `maxHoursPerWeek` (Decimal?)
- ✅ `maxVisitsPerDay` (Int?)
- ✅ `maxTravelTimePerDay` (Int?)
- ✅ `preferredWorkDays` (String[])
- ✅ `unavailableDates` (DateTime[])
- ✅ `languages` (String[])
- ✅ `certifications` (Json?)
- ✅ `notes` (String?)
- ✅ `isActive` (Boolean)

#### New Relationship: EmployeePreference (Not in docs)

Created bidirectional preference model:

```prisma
model EmployeePreference {
  id                 String   @id @default(uuid()) @db.Uuid
  employeeId         String   @db.Uuid
  preferenceType     String
  preferredClientIds String[] @db.Uuid
  avoidedClientIds   String[] @db.Uuid
  preferredDays      String[]
  avoidedDays        String[]
  notes              String?
  priority           Int      @default(5)
  createdAt          DateTime @default(now())
  updatedAt          DateTime @default(now()) @updatedAt

  employee Employee @relation(fields: [employeeId], references: [id], onDelete: Cascade)
}
```

### Client Model

#### Differences from Documentation

| Field in Docs                                              | Field in Implementation             | Notes                                                                    |
| ---------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------ |
| `name` (single field)                                      | `firstName`, `lastName`             | Split into two fields for better data structure                          |
| `ssn`                                                      | `personalNumber`                    | More generic term, same purpose                                          |
| `dateOfBirth`                                              | `birthYear`                         | **Privacy-first design** - year only is less sensitive (GDPR compliance) |
| `contactPerson`, `contactPhone`, `contactEmail` (3 fields) | `contactPerson` (single text field) | **Simplified for CSV imports** - stores employee name/ID as text         |
| `addressId`                                                | `primaryAddressId`                  | Renamed for clarity                                                      |

#### Implemented Fields (matching docs)

- ✅ `gender` (String?, optional) - values: male, female, other
- ✅ `contactPerson` (String?) - **CRITICAL for continuity tracking** (70% threshold)
- ✅ `address` (String?) - denormalized for quick access
- ✅ `latitude`, `longitude` (Decimal?) - denormalized for quick access
- ✅ `municipality` (String?)
- ✅ `careLevel` (String?)
- ✅ `diagnoses` (String[], default: []) - **Optional sensitive GDPR/DPIA data**
- ✅ `allergies` (String[], default: [])
- ✅ `languagePreference` (String?)
- ✅ `languages` (String[])
- ✅ `personalNumber` (String?)
- ✅ `email` (String?)
- ✅ `phone` (String?)
- ✅ `serviceAreaId` (String?)
- ✅ `notes` (String?)
- ✅ `isActive` (Boolean)

#### Relationship Tables (fully implemented)

All relationship tables from docs are implemented:

- ✅ `Address` - Multiple addresses per client
- ✅ `ClientContact` - Emergency contacts
- ✅ `ClientPreference` - Preferred/avoided employees
- ✅ `MonthlyAllocation` - Monthly hour tracking

---

## Design Decisions Rationale

### 1. Employee Home Address (Kept Optional)

**Documentation says (line 232):**

> Route optimization uses office/depot locations as the start and end point for all employees. This data minimization approach reduces privacy risk.

**Implementation Decision:**

- Kept `homeAddress`, `homeLatitude`, `homeLongitude` as **optional** fields
- **Rationale:** User requested flexibility for future use cases
- **Privacy:** Still optional, not required for route optimization
- **Usage:** Can be used for emergency contact info or future features

### 2. serviceAreaId Nullable

**Implementation:**

```prisma
serviceAreaId String? @db.Uuid  // Nullable
```

**Rationale:**

- Supports **multi-area employees** who can work across service areas
- Supports **org-level employees** (schedulers, admins) who don't belong to specific area
- Allows emergency coverage assignments without hard constraints

### 3. birthYear Instead of dateOfBirth

**Implementation:**

```prisma
birthYear Int?  // Year only (e.g., 1950)
```

**Rationale:**

- **GDPR compliance** - less sensitive than full date of birth
- Sufficient for age-related care planning
- Reduces privacy risk while maintaining utility

### 4. contactPerson as Text Field

**Implementation:**

```prisma
contactPerson String?  // Employee name or ID
```

**Rationale:**

- **CSV import flexibility** - can store employee name directly
- Avoids FK constraint issues during bulk imports
- Can be employee name, employee ID, or external ID
- Allows gradual data quality improvements

### 5. diagnoses Optional

**Implementation:**

```prisma
diagnoses String[] @default([])  // Optional
```

**Rationale:**

- **GDPR/DPIA sensitive data** - not required for scheduling
- **Alternative:** Use skill-based matching (e.g., "dementia care" skill)
- Keeps sensitive medical data optional
- Organizations can choose to use or not use

---

## GraphQL Schema Implementation

All GraphQL types, inputs, and resolvers have been updated to match the Prisma schema:

### Updated Types

- ✅ `Employee` type - all new fields + relationships (skills, tags, costs, preferences)
- ✅ `Client` type - all new fields + relationships (addresses, contacts, preferences, allocations)
- ✅ `CreateEmployeeInput` - all new fields
- ✅ `UpdateEmployeeInput` - all new fields
- ✅ `CreateClientInput` - all new fields
- ✅ `UpdateClientInput` - all new fields

### New Relationship Types

- ✅ `Address`
- ✅ `ClientContact`
- ✅ `ClientPreference`
- ✅ `MonthlyAllocation`
- ✅ `EmployeeSkill`
- ✅ `EmployeeTag`
- ✅ `EmployeeCost`
- ✅ `EmployeePreference`

### Field Resolvers

- ✅ Employee: `skills`, `tags`, `costs`, `preferences`
- ✅ Client: `addresses`, `primaryAddress`, `contacts`, `preferences`, `allocations`

### GraphQL Operations

- ✅ All employee queries/mutations updated with new fields
- ✅ All client queries/mutations updated with new fields
- ✅ TypeScript types regenerated
- ✅ React hooks regenerated

---

## Migration Details

**Migration File:** `apps/dashboard-server/migrations/20260127063104_add_data_model_2_0_fields/migration.sql`

**Changes Applied:**

1. Renamed `Employee.homeServiceAreaId` → `Employee.serviceAreaId`
2. Added Employee fields: gender, status, role, startDate, endDate, phoniroEmployeeId, recentClientVisits
3. Added Client fields: gender, birthYear, contactPerson, address, latitude, longitude, municipality, careLevel, diagnoses, allergies, languagePreference
4. Created `EmployeePreference` table
5. Updated indexes and constraints
6. All existing data preserved (new fields are nullable)

**Prisma Client:** Regenerated after migration

**GraphQL Codegen:** Regenerated after schema updates

---

## Frontend Implementation Status

### ⏳ Pending Updates

Both forms need updates to include new fields:

1. **EmployeeForm.tsx** - Must rename `homeServiceAreaId` → `serviceAreaId` and add new fields
2. **ClientForm.tsx** - Must add `contactPerson` (CRITICAL) and other new fields

See `DATA_MODEL_IMPLEMENTATION_STATUS.md` in repo root for detailed frontend implementation guide.

---

## GDPR & Privacy Notes

### Sensitive Data Fields

| Field                              | Sensitivity | GDPR/DPIA | Notes                                           |
| ---------------------------------- | ----------- | --------- | ----------------------------------------------- |
| `personalNumber` (SSN)             | **High**    | Yes       | Requires encryption at rest                     |
| `dateOfBirth` (if used)            | **High**    | Yes       | We use `birthYear` instead (Medium sensitivity) |
| `diagnoses`                        | **High**    | Yes       | Optional - use skill matching instead           |
| `allergies`                        | **Medium**  | Partial   | Safety-critical, minimal risk                   |
| `address`, `latitude`, `longitude` | **Medium**  | Partial   | Required for service delivery                   |
| `homeAddress` (employee)           | **Medium**  | Partial   | Optional field, not required                    |
| `gender`                           | **Low**     | Minimal   | Demographic data                                |

### Data Minimization Applied

1. **birthYear** instead of full dateOfBirth - reduced sensitivity
2. **homeAddress optional** for employees - not required for routing
3. **diagnoses optional** - use skill-based matching instead
4. **contactPerson as text** - no FK to sensitive data

---

## Testing Verification

### Database

```bash
cd apps/dashboard-server
yarn db:studio  # Verify schema in Prisma Studio
```

### GraphQL API

```bash
cd apps/dashboard-server
yarn dev  # Start server on port 4000
# Open http://localhost:4000/graphql
# Test employee/client queries with new fields
```

### Frontend

```bash
cd apps/dashboard
yarn dev  # Start on port 3001
# Test Resources > Employees
# Test Resources > Clients
```

---

## Related Documentation

- **Main Data Model:** `data-model.md` (target schema)
- **Schema Updates:** `data-model-updates.md` (change history)
- **Implementation Status:** `/DATA_MODEL_IMPLEMENTATION_STATUS.md` (repo root)
- **Prisma Schema:** `apps/dashboard-server/schema.prisma` (actual implementation)
- **Migration:** `apps/dashboard-server/migrations/20260127063104_add_data_model_2_0_fields/`

---

## Summary

**Backend: ✅ Complete**

- Database schema updated and migrated
- GraphQL schema updated
- Field resolvers implemented
- Types and hooks regenerated

**Frontend: ⏳ Pending**

- Form components need updates
- See implementation guide for details

**Key Decisions:**

- ✅ Home address kept optional for flexibility
- ✅ serviceAreaId nullable for multi-area employees
- ✅ birthYear instead of dateOfBirth for privacy
- ✅ contactPerson as text for CSV import flexibility
- ✅ diagnoses optional for GDPR compliance
