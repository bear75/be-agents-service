# Attendo Pilot: Data Requirements, Availability & Security Analysis

**Purpose**: Analyze data set requirements, assess data availability, and define security/privacy requirements for Caire optimization use cases in the Attendo pilot.

---

## Document Structure

This document covers three critical areas:

1. **Data Requirements Analysis** - What data is needed for Caire optimization use cases?
2. **Data Availability Assessment** - What data is available from Attendo's eCare system?
3. **Security & Privacy Requirements** - What security measures and compliance requirements apply?

---

## 1. Data Requirements Analysis

### 1.1 Optimization Use Cases & Required Data

Caire optimization requires data across multiple dimensions:

#### Use Case 1: Daily Schedule Optimization

**Required Data**:

- ✅ Visit time windows (minStartTime, maxStartTime, maxEndTime) - hard constraints
- ✅ Preferred time windows (preferredMinStartTime, preferredMaxStartTime, preferredMaxEndTime) - soft constraints for waiting minimization
- ✅ Visit duration
- ✅ Visit location (address, coordinates)
- ✅ Employee shifts (start/end times, service area)
- ✅ Employee skills and qualifications
- ✅ Employee transport mode
- ✅ Visit priority (mandatory/optional)
- ✅ Visit skills requirements

**Purpose**: Optimize daily visit assignments to minimize travel time, maximize efficiency, respect constraints.

#### Use Case 2: Pre-Planning with Movable Visits

**Required Data**:

- ✅ Movable visit templates (frequency, duration, time windows)
- ✅ Client preferences (continuity, preferred employees)
- ✅ Historic visit data with employee assignments per client (to calculate continuity baseline - number of different caregivers per client over time period)
- ✅ Employee availability patterns
- ✅ Service area boundaries
- ✅ Historical demand patterns

**Purpose**: Plan recurring visits across weeks/months, find optimal placement for flexible visits. Continuity and efficiency are both key metrics that must be optimized.

#### Use Case 3: Cross-Area Optimization

**Required Data**:

- ✅ Client addresses (coordinates)
- ✅ Service area boundaries
- ✅ Employee service area assignments
- ✅ Travel time matrices

**Purpose**: Optimize across multiple service areas, suggest client reassignments.

#### Use Case 4: Demand & Supply Management

**Required Data**:

- ✅ Unused hours (monthly allocated visit hours per client from biståndsbeslut that become unused when visits are cancelled)
- ✅ Visit priority levels (mandatory/optional)
- ✅ Employee capacity (shift hours)
- ✅ Demand forecasts

**Purpose**: Balance demand and supply, recapture unused hours, optimize capacity utilization. Unused hours are monthly allocated visit hours per client (derived from biståndsbeslut) that become unused when visits are cancelled (by client or organization if optional). This pool of unused hours can be used to balance supply and demand. The goal is to utilize all allocated visit hours per client per month, because hours reset each month and unused hours at month end represent lost revenue (>0 = lost revenue).

### 1.2 Data Classification by Criticality

| Data Category           | Criticality     | Impact if Missing           | Workaround                                                                                                                        |
| ----------------------- | --------------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Visit time windows**  | 🔴 Critical     | Cannot optimize             | Use fixed times                                                                                                                   |
| **Visit location**      | 🔴 Critical     | Cannot route optimize       | Use service area center                                                                                                           |
| **Employee shifts**     | 🔴 Critical     | Cannot assign visits        | Use default shifts                                                                                                                |
| **Visit duration**      | 🔴 Critical     | Cannot calculate efficiency | Use average duration                                                                                                              |
| **Employee skills**     | 🟡 Important    | May assign wrong employee   | Allow all skills                                                                                                                  |
| **Visit priority**      | 🟡 Important    | Cannot prioritize           | Treat all as mandatory                                                                                                            |
| **Continuity data**     | 🟡 Important    | Cannot optimize continuity  | No continuity optimization (continuity and efficiency are both key metrics)                                                       |
| **Historic visit data** | 🟡 Important    | Cannot calculate continuity | Need historic visits with employee assignments per client to calculate number of different caregivers per client over time period |
| **Preferred employees** | 🟢 Nice-to-have | Lower satisfaction          | No preference optimization                                                                                                        |

### 1.3 Data Quality Requirements

- **Completeness**: Minimum 80% of visits must have all critical fields
- **Accuracy**: Coordinates within 100m of actual address
- **Timeliness**: Data no older than 7 days for daily optimization
- **Consistency**: Time windows must be valid (minStartTime ≤ maxStartTime ≤ maxEndTime)

---

## 2. Data Availability Assessment

### 2.1 eCare System Data Export Capabilities

**Assessment Status**: ⏳ **To be validated with Attendo**

#### Available from eCare (Expected)

| Data Category              | Available? | Format                 | Notes                                                                                                                                                                                                        |
| -------------------------- | ---------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Visit assignments**      | ✅ Yes     | CSV export             | One row per visit                                                                                                                                                                                            |
| **Client information**     | ✅ Yes     | CSV columns            | ID, name, address                                                                                                                                                                                            |
| **Client service area**    | ⚠️ Unknown | CSV column             | Service area assignment for client                                                                                                                                                                           |
| **Client required skills** | ⚠️ Unknown | CSV column             | Required skills for client visits                                                                                                                                                                            |
| **Employee information**   | ✅ Yes     | CSV columns            | ID, name, skills                                                                                                                                                                                             |
| **Employee service area**  | ⚠️ Unknown | CSV column             | Service area assignment for employee                                                                                                                                                                         |
| **Visit times**            | ✅ Yes     | CSV columns            | Start/end times                                                                                                                                                                                              |
| **Visit locations**        | ✅ Yes     | CSV columns            | Address, possibly coordinates                                                                                                                                                                                |
| **Employee shifts**        | ⚠️ Unknown | CSV or separate export | Need to verify                                                                                                                                                                                               |
| **Visit priority**         | ⚠️ Unknown | CSV column             | May not be in eCare                                                                                                                                                                                          |
| **Historic visit data**    | ⚠️ Unknown | CSV export             | Need historic visits with employee assignments per client to calculate continuity (number of different caregivers per client over time period). Continuity and efficiency are both key metrics.              |
| **Unused hours**           | ⚠️ Unknown | CSV column (decimal)   | If eCare tracks unused hours: include as decimal field. If not: Caire calculates from cancellations and allocations (requires historic data via closed-loop API for accurate tracking - not in pilot scope). |

#### Data Gaps & Workarounds

**Gap 1: Employee Shift Information**

- **Impact**: Cannot optimize without knowing when employees work
- **Workaround**:
  - Option A: Export employee schedules separately
  - Option B: Infer from visit assignments (if employees only have visits during shifts)
  - Option C: Use default shift patterns (e.g., 8 AM - 4 PM)

**Gap 2: Visit Priority (Mandatory/Optional)**

- **Impact**: Cannot prioritize visits during capacity constraints
- **Workaround**:
  - Option A: Use visit type to infer priority (e.g., medication = mandatory)
  - Option B: Mark all as mandatory (conservative approach)
  - Option C: Add priority field to CSV manually

**Gap 3: Continuity Data (Historic Visits)**

- **Impact**: Cannot optimize for continuity or calculate continuity metrics. Continuity and efficiency are both key metrics that must be great.
- **Definition**: Continuity is measured as the number of different caregivers assigned to a client during a time period. Lower numbers are better (1 = best, ~10 = typical in Swedish home care, 12+ = poor).
- **Required Data**: Historic visit data with employee assignments per client to calculate the number of different caregivers per client over a time period.
- **Workaround for Manual CSV Imports**:
  - Option A: Import historic visit data from eCare (actuals or planned schedules) with employee assignments to calculate baseline continuity
  - Option B: Start with no continuity optimization, build continuity data during pilot
  - Option C: Manual entry of continuity preferences if available from other sources
- **Note**: For accurate, real-time continuity metrics, closed-loop API integration is recommended (post-pilot) to fetch current visit history and calculate metrics automatically

**Gap 4: Unused Hours Tracking**

- **Impact**: Cannot accurately track and recapture unused capacity without closed-loop data
- **Definition**: Unused hours are monthly allocated visit hours per client (derived from biståndsbeslut) that become unused when visits are cancelled (by client or organization if optional). This pool of unused hours can be used to balance supply and demand. The goal is to utilize all allocated visit hours per client per month, because hours reset each month and unused hours at month end represent lost revenue (>0 = lost revenue).
- **Data Requirements**:
  - If eCare tracks unused hours: Include `unusedHours` as decimal (number of hours) in CSV per client
  - If eCare does NOT track unused hours: Caire can calculate from cancellations and allocations, but requires:
    - Historic actuals data with cancellations
    - Monthly allocation data from biståndsbeslut
    - Accurate tracking requires closed-loop API (not in pilot scope)
- **Workaround for Manual CSV Imports**:
  - Option A: If eCare tracks unused hours, include in CSV as decimal field
  - Option B: Calculate from cancellations (compare planned vs actual) and track monthly allocations from biståndsbeslut (requires complete historic data)
  - Option C: Manual entry of unused allocations per client per month (not recommended for scale)
- **Note**: For accurate, real-time unused hours tracking, closed-loop API integration is recommended (post-pilot)

### 2.2 Data Collection Plan

**Phase 1: Data Discovery** (Week 1)

- [ ] Attendo exports sample eCare CSV data
- [ ] Caire analyzes available fields
- [ ] Identify data gaps
- [ ] Document workarounds

**Phase 2: Data Validation** (Week 2)

- [ ] Validate data completeness
- [ ] Test data quality
- [ ] Verify coordinate accuracy
- [ ] Test import process

**Phase 3: Gap Resolution** (Week 2-3)

- [ ] Implement workarounds for missing data
- [ ] Add manual data entry if needed
- [ ] Validate optimization works with available data

---

## 3. Security & Privacy Requirements

### 3.1 Personal Data Involved

**Categories of Personal Data**:

| Data Type         | Examples                                 | Sensitivity | Legal Basis                                |
| ----------------- | ---------------------------------------- | ----------- | ------------------------------------------ |
| **Client Data**   | Name, address, coordinates               | 🔴 High     | Legitimate interest (service delivery)     |
| **Employee Data** | Name, skills, shifts, location           | 🟡 Medium   | Legitimate interest (workforce management) |
| **Visit Data**    | Time, location, tasks, assigned employee | 🔴 High     | Legitimate interest (care coordination)    |
| **Skills Data**   | Skills required for visits               | 🟡 Medium   | Legitimate interest (service requirements) |

**Note**: Skills required for visits are stored as technical/competence-based labels (service requirements), not medical causes. They do not reveal health diagnoses or sensitive personal data. The pilot does NOT process sensitive health data (diagnoses, medications, detailed care plans) - only basic scheduling data and required competencies/skills for service delivery.

### 3.2 Security Requirements

#### Data Protection Measures

**During Import**:

- ✅ Encrypted file transfer (SFTP, HTTPS)
- ✅ File validation before processing
- ✅ Secure file storage (encrypted at rest)
- ✅ Access logging

**During Processing**:

- ✅ Data processed in secure environment
- ✅ No data stored in logs
- ✅ Pseudonymization where possible
- ✅ Access controls (role-based)

**During Storage**:

- ✅ Encrypted database (at rest)
- ✅ Encrypted backups
- ✅ Access controls (authentication + authorization)
- ✅ Audit logging

**During Optimization**:

- ✅ Timefold API uses encrypted connection (HTTPS)
- ✅ Data sent to Timefold is pseudonymized (no names, only IDs)
- ✅ Timefold does not store data (stateless API)

#### Access Controls

- **Role-based access**: Only authorized users can access pilot data
- **Audit logging**: All data access logged
- **Data retention**: Pilot data deleted after pilot completion (unless otherwise agreed)
- **Data sharing**: No data shared with third parties except Timefold (via API)

### 3.3 Compliance Requirements

#### GDPR Compliance

- ✅ **Data Processing Agreement (DPA)** - Required between Caire and Attendo
- ✅ **Data Protection Impact Assessment (DPIA)** - See [`docs_2.0/06-compliance/DPIA/`](../../../06-compliance/DPIA/)
- ✅ **Lawful basis**: Legitimate interest (service delivery optimization)
- ✅ **Data minimization**: Only collect data necessary for optimization
- ✅ **Purpose limitation**: Data used only for scheduling optimization
- ✅ **Storage limitation**: Data retained only for pilot duration
- ✅ **Right to erasure**: Data can be deleted upon request

#### Healthcare Regulations

- ✅ **Patient confidentiality**: Healthcare data handled with extra care
- ✅ **Access controls**: Strict access controls for healthcare data
- ✅ **Audit trails**: Complete audit trail for healthcare data access

### 3.4 eCare CSV File Management

**File Source & Transfer**:

- **Source**: CSV files exported from Attendo's eCare system
- **Transfer Method**:
  - **Option A (Recommended)**: Secure file transfer via SFTP to Caire's secure server
  - **Option B**: Encrypted email or secure file sharing service (HTTPS)
  - **Option C**: Manual upload via secure web interface (HTTPS)
- **Initial Storage Location**: Files stored on Attendo's secure server until transfer

**File Handling by Caire**:

1. **Receipt & Temporary Storage**:
   - CSV files received via secure transfer (SFTP/HTTPS)
   - Files temporarily stored on AWS EC2 server in encrypted storage (encrypted at rest)
   - Files stored in isolated, access-controlled directory
   - Access logging enabled for all file operations

2. **Import Process**:
   - File validation (format, completeness, data quality checks)
   - Data mapping: CSV → Normalized database (Prisma + PostgreSQL)
   - Data stored in relational tables (schedules, visits, employees, etc.)
   - Import logs created (without personal data)

3. **Post-Import File Management**:
   - **Primary Approach**: CSV files deleted after successful import and validation
   - **Rationale**: Data minimization principle - data is now in normalized database, CSV files are redundant
   - **Exception**: Files may be retained for testing/verification if explicitly agreed with Attendo

4. **Testing & Verification Storage** (if needed):
   - **Option A**: Retain CSV files on AWS EC2 server in encrypted storage for pilot duration
     - Files stored in separate, access-controlled directory
     - Encrypted at rest (AWS EBS encryption)
     - Access restricted to authorized Caire team members only
     - Files deleted after pilot completion (or earlier if requested)
   - **Option B**: Retain only anonymized/pseudonymized test data
     - Remove personal identifiers (names, addresses)
     - Keep only IDs and structural data for testing
     - Stored separately from production data
   - **Option C**: No retention - delete immediately after import
     - Recommended for maximum data minimization
     - Verification done through database queries and logs

**Storage on AWS EC2 Server** (if retention needed):

- ✅ **Encrypted Storage**: Files stored on encrypted EBS volumes (AWS encryption at rest)
- ✅ **Access Controls**:
  - Files in isolated directory with restricted permissions
  - Only authorized Caire team members can access
  - All access logged and audited
- ✅ **Network Security**:
  - EC2 instance in private subnet (not publicly accessible)
  - Access via VPN or secure bastion host only
- ✅ **Retention Policy**:
  - Files retained only for pilot duration (or shorter if agreed)
  - Automatic deletion after pilot completion
  - Can be deleted earlier upon Attendo's request
- ✅ **Backup**:
  - If files are retained, they are included in encrypted backups
  - Backups follow same retention policy

**Recommendation**:

- **For Production**: Delete CSV files immediately after successful import (data minimization)
- **For Testing/Verification**: If retention is needed, use Option A (encrypted storage on AWS EC2) with explicit agreement in DPA
- **Documentation**: File retention policy should be documented in DPA and agreed with Attendo before pilot start

**Questions for Phase 1**:

- Does Attendo have preferences for CSV file retention?
- Is there a need to retain CSV files for verification/audit purposes?
- What is the preferred file transfer method (SFTP, secure email, web upload)?

### 3.5 Data Processing Agreement (DPA)

**Status**: ⏳ **To be signed before pilot start**

**Key Points**:

- Caire acts as **data processor** (Attendo is data controller)
- Caire processes data only as instructed by Attendo
- Caire implements appropriate security measures
- Caire assists with data subject rights requests
- Caire deletes data after pilot completion
- **CSV file retention policy** should be explicitly defined in DPA

**Reference**: See [`docs_2.0/06-compliance/DPIA/06_DPA_AGREEMENT_DRAFT.md`](../../../06-compliance/DPIA/06_DPA_AGREEMENT_DRAFT.md)

### 3.6 Risk Assessment

| Risk                    | Probability | Impact    | Mitigation                              |
| ----------------------- | ----------- | --------- | --------------------------------------- |
| **Data breach**         | 🟡 Medium   | 🔴 High   | Encryption, access controls, monitoring |
| **Unauthorized access** | 🟡 Medium   | 🔴 High   | Role-based access, audit logging        |
| **Data loss**           | 🟢 Low      | 🟡 Medium | Regular backups, redundancy             |
| **Non-compliance**      | 🟡 Medium   | 🔴 High   | DPIA, DPA, compliance review            |

**Reference**: See [`docs_2.0/06-compliance/DPIA/05_RISK_ANALYSIS.md`](../../../06-compliance/DPIA/05_RISK_ANALYSIS.md) for detailed risk analysis.

---

## 4. Data Format Specifications

### 4.1 eCare CSV Format (Simple, Non-Technical)

This section describes the CSV format that Attendo should export from eCare. The format is designed to be simple and match what eCare can typically export. The mapper will convert this format directly to normalized database tables. Timefold JSON format is generated on-the-fly from the database when needed for optimization (temporary, not stored).

### Import Dimensions (To Be Assessed in Phase 1)

**Status**: ⏳ **To be validated with Attendo in Phase 1**

Caire ideally needs to specify both **time** and **location** dimensions during import. Whether eCare CSV export supports this will be assessed in Phase 1.

#### Time Dimension (Planning Window) - Question for Phase 1

**Ideal Capability**: The CSV import should support different time horizons:

- **Daily**: Single day (e.g., 2025-03-24)
- **Weekly**: Full week (e.g., 2025-03-24 to 2025-03-30)
- **Monthly**: Full month (e.g., 2025-03-01 to 2025-03-31)
- **Custom range**: Any date range (e.g., 2025-03-15 to 2025-04-15)

**Questions for Phase 1**:

- Can eCare export CSV data for a weekly/monthly date range, or only daily?
- Can eCare include planning window metadata in CSV export?
- If not, can Caire infer planning window from `visitDate` range in the CSV data?

**Benefits of Longer Planning Windows** (if supported):

- More context for optimization (better route planning, demand/supply balance)
- Support for movable visits with multi-day time windows
- Cross-day optimization (e.g., weekly patterns)

**Fallback**: If eCare only supports daily exports, Caire can:

- Import multiple daily CSVs and combine them
- Infer planning window from the date range of imported data

#### Location Dimension (Service Area Filtering) - Question for Phase 1

**Caire Capability**: Caire can handle service area filtering internally, as long as all clients, visits, and employees are tagged with service areas in the CSV data.

**Required CSV Data**:

- Each client row must include `clientServiceArea` (or similar) column
- Each visit row must include `serviceAreas` column (or visit-level service area tag)
- Each employee row must include `employeeServiceArea` (or similar) column

**Caire Filtering Options** (after import):

- **Single service area**: Filter to one specific service area (e.g., "Farsta") for optimization
- **Multiple service areas**: Filter to selected service areas (e.g., "Farsta,Tallkrogen") for cross-area optimization
- **All service areas**: Process all service areas in the organization (no filter) for organization-wide optimization

**Questions for Phase 1**:

- Does eCare CSV export include service area tags for clients, visits, and employees?
- What are the column names for service area data in eCare exports?
- Can eCare export data for all service areas in one CSV, or does it need to be filtered at export time?

**Benefits of Service Area Tagging**:

- Cross-area optimization (client reassignment, route optimization across boundaries)
- Better demand/supply balance across regions
- Flexible filtering: optimize single area, multiple areas, or all areas
- Unified view of operations with ability to focus on specific areas

**Note**: eCare does NOT need to pre-filter CSV exports by service area. Caire can import all service areas and filter internally during optimization based on the service area tags in the data.

### Metrics Tracking & Closed-Loop API

**Important**: Several key metrics require historic data and closed-loop tracking for accurate calculation:

**Metrics Requiring Historic Data**:

- **Unused hours**: Monthly allocated hours per client minus delivered hours (requires tracking cancellations and allocations over time)
- **Contact person %**: Percentage of visits assigned to designated contact person (requires historic visit assignments)
- **Continuity**: Number of different caregivers per client over time period (requires historic visit assignments with employee data)
- **Preferred caregivers %**: Percentage of visits assigned to preferred caregivers (requires historic visit assignments)

**For Manual CSV Imports** (Pilot Phase):

- **Limitation**: Manual CSV imports provide snapshot data, not continuous tracking
- **Caire Calculation**: Caire can calculate these metrics from imported historic data, but accuracy depends on:
  - Completeness of historic visit data (actuals with employee assignments)
  - Monthly allocation data from biståndsbeslut
  - Cancellation tracking in actuals data
- **Recommendation**: For accurate, real-time metrics, implement closed-loop API integration (not in pilot scope - see [PILOT_OUT_OF_SCOPE.md](./PILOT_OUT_OF_SCOPE.md))

**For Closed-Loop API Integration** (Post-Pilot):

- **Ideal Solution**: API integration with eCare to fetch current metrics and historic data
- **Benefits**:
  - Real-time unused hours tracking (current month allocations vs delivered)
  - Accurate continuity metrics (calculated from complete visit history)
  - Current contact person and preferred caregiver assignment rates
  - Automatic updates without manual CSV imports
- **Implementation**: Not included in pilot scope - to be evaluated post-pilot

**CSV Import Approach** (Pilot):

- If eCare tracks unused hours: Include `unusedHours` as decimal (number of hours) in CSV
- If eCare does NOT track unused hours: Omit field - Caire will calculate from cancellations and allocations (requires complete historic data)
- Contact person, continuity, preferred caregivers: Caire calculates from historic visit data with employee assignments

### CSV Structure

- **One row per visit assignment**
- **Columns can be present/absent** depending on available data
- **Supports all 8 combinations** of schedule states:
  - Unplanned only
  - Planned only
  - Actual only
  - Unplanned + Planned
  - Unplanned + Actual
  - Planned + Actual
  - All three (Unplanned + Planned + Actual)
  - None (invalid)

### Visit Identification Fields

| Field        | Type              | Required    | Description                                       |
| ------------ | ----------------- | ----------- | ------------------------------------------------- |
| `visitId`    | String            | Yes         | Unique visit identifier                           |
| `clientId`   | String            | Yes         | Client identifier (can be external ID from eCare) |
| `clientName` | String            | Recommended | Client name (for matching and display)            |
| `visitDate`  | Date (YYYY-MM-DD) | Yes         | Date of the visit                                 |

### Time Information Fields (Flexibility Support)

These fields handle visit time windows and flexibility. The system supports two formats:

#### Option 1: Time Windows (Direct Format)

**Hard Time Windows** (must be respected):

| Field               | Type              | Required    | Description                                                             |
| ------------------- | ----------------- | ----------- | ----------------------------------------------------------------------- |
| `visitMinStartTime` | ISO 8601 datetime | Conditional | Earliest start time (e.g., 2025-03-24T08:00:00+01:00) - hard constraint |
| `visitMaxStartTime` | ISO 8601 datetime | Conditional | Latest start time (e.g., 2025-03-24T10:00:00+01:00) - hard constraint   |
| `visitMaxEndTime`   | ISO 8601 datetime | Conditional | Latest end time (e.g., 2025-03-24T11:00:00+01:00) - hard constraint     |
| `serviceDuration`   | ISO 8601 duration | Yes         | Service duration (e.g., PT30M, PT1H30M)                                 |

**Preferred Time Windows** (soft constraints for waiting minimization):

| Field                   | Type              | Required | Description                                                                                        |
| ----------------------- | ----------------- | -------- | -------------------------------------------------------------------------------------------------- |
| `preferredMinStartTime` | ISO 8601 datetime | Optional | Preferred earliest start time (e.g., 2025-03-24T08:30:00+01:00) - soft constraint for optimization |
| `preferredMaxStartTime` | ISO 8601 datetime | Optional | Preferred latest start time (e.g., 2025-03-24T09:30:00+01:00) - soft constraint for optimization   |
| `preferredMaxEndTime`   | ISO 8601 datetime | Optional | Preferred latest end time (e.g., 2025-03-24T10:30:00+01:00) - soft constraint for optimization     |

**Note**: Preferred time windows are soft constraints used to minimize waiting time and start visits on arrival. The optimizer will prefer to schedule visits within the preferred time window, but can schedule outside if needed (within the hard time window constraints). If preferred time windows are not provided, the optimizer will use the hard time windows for optimization.

#### Option 2: Original + Flexibility (Can be Mapped to Time Windows)

**Hard Time Windows** (mapped from original + flexibility):

| Field                | Type              | Required    | Description                                                     |
| -------------------- | ----------------- | ----------- | --------------------------------------------------------------- |
| `originalStartTime`  | ISO 8601 datetime | Conditional | Original/requested start time (e.g., 2025-03-24T09:00:00+01:00) |
| `flexibilityMinutes` | Integer           | Conditional | Flexibility window in minutes (e.g., 60 = ±30 minutes)          |
| `serviceDuration`    | ISO 8601 duration | Yes         | Service duration (e.g., PT30M, PT1H30M)                         |

**Preferred Time Windows** (soft constraints for waiting minimization):

| Field                         | Type              | Required | Description                                                                               |
| ----------------------------- | ----------------- | -------- | ----------------------------------------------------------------------------------------- |
| `preferredStartTime`          | ISO 8601 datetime | Optional | Preferred start time (e.g., 2025-03-24T09:00:00+01:00) - soft constraint for optimization |
| `preferredFlexibilityMinutes` | Integer           | Optional | Preferred flexibility window in minutes (e.g., 30 = ±15 minutes) - soft constraint        |

**Note**: These fields handle flexibility. The system can map from `originalStartTime + flexibility + serviceDuration` format to `minStartTime/maxStartTime/maxEndTime` format (similar to how Carefox data is mapped). Use either Option 1 or Option 2, not both. The `serviceDuration` field is required in both options.

**Example Mapping** (Hard Time Windows):

- `originalStartTime`: 2025-03-24T09:00:00+01:00
- `flexibilityMinutes`: 60
- `serviceDuration`: PT30M
- **Maps to**:
  - `visitMinStartTime`: 2025-03-24T08:30:00+01:00
  - `visitMaxStartTime`: 2025-03-24T09:30:00+01:00
  - `visitMaxEndTime`: 2025-03-24T10:00:00+01:00

**Example Mapping** (Preferred Time Windows - if provided):

- `preferredStartTime`: 2025-03-24T09:00:00+01:00
- `preferredFlexibilityMinutes`: 30
- `serviceDuration`: PT30M
- **Maps to**:
  - `preferredMinStartTime`: 2025-03-24T08:45:00+01:00
  - `preferredMaxStartTime`: 2025-03-24T09:15:00+01:00
  - `preferredMaxEndTime`: 2025-03-24T09:45:00+01:00

**Note**: Preferred time windows are soft constraints used to minimize waiting time and start visits on arrival. The optimizer will prefer to schedule visits within the preferred time window, but can schedule outside if needed (within the hard time window constraints). If preferred time windows are not provided, the optimizer will use the hard time windows for optimization.

### Visit Details Fields

| Field                       | Type                   | Required    | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| --------------------------- | ---------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `skills`                    | Comma-separated string | Recommended | Required skills (e.g., "Dusch,Medicinering")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `serviceAreas`              | Comma-separated string | Recommended | Service area tags (e.g., "Farsta,Tallkrogen") - can also be specified as CSV metadata for filtering                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `serviceAreaOfficeLocation` | String (lat,lng)       | Recommended | Office location coordinates used for all employees (e.g., "59.254417,18.081677")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `priority`                  | String (1-10)          | Recommended | Visit priority (1 = highest, 10 = lowest)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `mandatory`                 | Boolean (TRUE/FALSE)   | Optional    | Whether visit is mandatory (TRUE) or optional (FALSE)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `movable`                   | Boolean (TRUE/FALSE)   | Optional    | Whether this is a movable visit (TRUE) or fixed (FALSE)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `movableFrequency`          | String                 | Optional    | Frequency if movable: "daily", "weekly", "bi-weekly", "monthly"                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `continuity`                | String                 | Optional    | Continuity requirement: "high", "medium", "low". Note: Continuity is measured as the number of different caregivers assigned to a client during a time period. Lower numbers are better (1 = best, ~10 = typical in Swedish home care, 12+ = poor).                                                                                                                                                                                                                                                                                                                                                                        |
| `contactPerson`             | String                 | Optional    | Contact person (scheduling context): The responsible caregiver for a specific client (client-caregiver contact person). This contact person should have a certain percentage of the assigned visits for that client. Not related to preferred caregivers, but usually included in the preferred caregiver list. Note: This is different from "Client Contact Persons" (standing data: emergency contacts) which are not used for scheduling optimization.                                                                                                                                                                  |
| `preferredEmployees`        | Comma-separated string | Optional    | Preferred employee IDs or names (e.g., "Anna,Björn")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `nonPreferredEmployees`     | Comma-separated string | Optional    | Non-preferred employee IDs or names                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `unusedHours`               | Decimal (hours)        | Optional    | Number of unused hours per client for current month (if eCare tracks this). Note: Unused hours are monthly allocated visit hours per client (derived from biståndsbeslut) that become unused when visits are cancelled. Hours reset each month and unused hours at month end represent lost revenue (>0 = lost revenue). **If eCare does NOT track this**: Omit this field - Caire will calculate from cancellations and allocations, but accurate tracking requires historic data via closed-loop API (not in pilot scope). For manual CSV imports, Caire can calculate from imported historic actuals data if available. |

**Note**: `serviceDuration` is included in the time information fields (Option 1 or Option 2) and should not be duplicated here.

### Location Fields

| Field              | Type    | Required | Description                                                                                  |
| ------------------ | ------- | -------- | -------------------------------------------------------------------------------------------- |
| `visitAddress`     | String  | Yes      | Full address (e.g., "Brunskogsbacken 84, 12371 Farsta")                                      |
| `visitLocationLat` | Decimal | Optional | Visit location latitude (e.g., 59.254417) - Caire will geocode from address if not provided  |
| `visitLocationLng` | Decimal | Optional | Visit location longitude (e.g., 18.081677) - Caire will geocode from address if not provided |

**Note**: `visitAddress` is required. Latitude/longitude are optional - Caire will perform geocoding from the address if coordinates are not provided.

### Planned Information Fields (If Available)

These fields represent what was planned in eCare. When present, they will be used to create an INPUT file with pinned visits for metrics generation.

| Field                       | Type              | Required    | Description                 |
| --------------------------- | ----------------- | ----------- | --------------------------- |
| `plannedStart`              | ISO 8601 datetime | Conditional | Planned start time          |
| `plannedDuration`           | ISO 8601 duration | Conditional | Planned duration            |
| `plannedEmployee`           | String            | Conditional | Planned employee ID or name |
| `plannedEmployeeShiftStart` | ISO 8601 datetime | Conditional | Employee shift start time   |
| `plannedEmployeeShiftEnd`   | ISO 8601 datetime | Conditional | Employee shift end time     |

**Note**: Planned employee shift start/end locations are not needed - Caire uses `serviceAreaOfficeLocation` (from visit details) for all employees.

### Actual Information Fields (If Available)

These fields represent what actually happened during execution. When present, they will be used to create an INPUT file with pinned visits for metrics generation.

| Field                        | Type              | Required    | Description                                          |
| ---------------------------- | ----------------- | ----------- | ---------------------------------------------------- |
| `actualStart`                | ISO 8601 datetime | Conditional | Actual start time                                    |
| `actualDuration`             | ISO 8601 duration | Conditional | Actual duration                                      |
| `actualEmployee`             | String            | Conditional | Actual employee ID or name who performed visit       |
| `actualStatus`               | String            | Conditional | Status: "COMPLETED", "CANCELLED", "NO_SHOW", "EXTRA" |
| `actualTravelTimeSeconds`    | Integer           | Optional    | Actual travel time in seconds                        |
| `actualTravelDistanceMeters` | Integer           | Optional    | Actual travel distance in meters                     |

**Note**: `actualStatus` must include "EXTRA" for visits that were not part of the original or planned schedules (e.g., urgent visits added during execution).

### Employee/Vehicle Fields (Required for Unplanned)

These fields define employee availability and capabilities. Required when importing unplanned visits.

| Field                       | Type                   | Required    | Description                                  |
| --------------------------- | ---------------------- | ----------- | -------------------------------------------- |
| `employeeId`                | String                 | Conditional | Employee identifier (can be external ID)     |
| `employeeName`              | String                 | Recommended | Employee name (for matching)                 |
| `employeeShiftId`           | String                 | Conditional | Shift identifier                             |
| `employeeShiftMinStartTime` | ISO 8601 datetime      | Conditional | Shift start time                             |
| `employeeShiftMaxEndTime`   | ISO 8601 datetime      | Conditional | Shift end time                               |
| `employeeShiftSkills`       | Comma-separated string | Optional    | Employee skills (e.g., "Dusch,Medicinering") |
| `employeeShiftTags`         | Comma-separated string | Optional    | Employee tags/service areas                  |
| `employeeShiftBreaksJSON`   | JSON string            | Optional    | Breaks as JSON array (see format below)      |
| `employeeShiftCostJSON`     | JSON string            | Optional    | Cost structure as JSON (see format below)    |

**Note**: Employee shift start/end locations are not needed - Caire uses `serviceAreaOfficeLocation` (from visit details) for all employees in the schedule. This location is used as the start and end point for all employee routes.

### Financial Data Fields

| Field                   | Type                            | Required | Description                                                           |
| ----------------------- | ------------------------------- | -------- | --------------------------------------------------------------------- |
| `revenuePerServiceArea` | JSON string or separate columns | Optional | Revenue per service area (e.g., `{"Farsta": 500, "Tallkrogen": 450}`) |
| `employeeCostMonthly`   | Decimal                         | Optional | Monthly cost per employee (in SEK)                                    |
| `employeeCostPerHour`   | Decimal                         | Optional | Hourly cost per employee (in SEK)                                     |
| `transportType`         | String                          | Optional | Transport type: "CAR", "BIKE", "WALK", "PUBLIC_TRANSPORT"             |

### Break JSON Format

If `employeeShiftBreaksJSON` is provided, use this format:

```json
[
  {
    "id": "break_1",
    "type": "FLOATING",
    "minStartTime": "2025-03-24T11:00:00+01:00",
    "maxEndTime": "2025-03-24T13:00:00+01:00",
    "duration": "PT30M",
    "costImpact": "PAID"
  }
]
```

**Break Types**: "FIXED", "FLOATING", "LEGACY"
**Cost Impact**: "PAID", "UNPAID"

### Cost JSON Format

If `employeeShiftCostJSON` is provided, use this format:

```json
{
  "fixedCost": 1375,
  "rates": [
    {
      "duration": "PT9H",
      "activationCost": 0,
      "costPerUnit": 300,
      "unit": "HOUR"
    },
    {
      "duration": "PT1H",
      "activationCost": 0,
      "costPerUnit": 350,
      "unit": "HOUR"
    }
  ]
}
```

---

### 4.2 Caire Normalized Database Format (Detailed, Technical)

**Note**: This section describes the normalized database structure that eCare CSV data is mapped to. Timefold JSON format is generated on-the-fly from this normalized data when calling the Timefold API (temporary, not stored).

**Caire Architecture**:

- eCare CSV → **Normalized Database** (Prisma + PostgreSQL) - **This is what's stored**
- Normalized Database → **Timefold JSON** (temporary, generated on-the-fly for API calls)
- Timefold JSON → **Normalized Database** (solution stored in normalized tables)

The sections below describe the Timefold JSON format that is **temporarily generated** from the normalized database when calling the Timefold API. This JSON is **not stored** - it's only used for API communication.

### INPUT Structure for Unplanned Schedule

The system generates Timefold INPUT JSON from normalized database (temporary, for API call):

```json
{
  "modelInput": {
    "visits": [
      {
        "id": "visit_123",
        "name": "Client Name",
        "location": [59.254417, 18.081677], // Geocoded from visitAddress
        "serviceDuration": "PT30M",
        "timeWindows": [
          {
            "minStartTime": "2025-03-24T08:00:00+01:00",
            "maxStartTime": "2025-03-24T10:00:00+01:00",
            "maxEndTime": "2025-03-24T11:00:00+01:00"
          }
        ],
        "requiredSkills": [{ "name": "Dusch", "minLevel": 1 }],
        "requiredTags": ["Farsta"],
        "priority": "10",
        "pinningRequested": false
      }
    ],
    "vehicles": [
      {
        "id": "employee_456",
        "vehicleType": "VAN",
        "shifts": [
          {
            "id": "shift_789",
            "startLocation": [59.254417, 18.081677], // From serviceAreaOfficeLocation
            "endLocation": [59.254417, 18.081677], // From serviceAreaOfficeLocation
            "minStartTime": "2025-03-24T07:00:00+01:00",
            "maxEndTime": "2025-03-24T16:00:00+01:00",
            "skills": [{ "name": "Dusch", "level": 1 }],
            "tags": ["Farsta"],
            "requiredBreaks": [
              {
                "id": "break_1",
                "type": "FLOATING",
                "minStartTime": "2025-03-24T11:00:00+01:00",
                "maxEndTime": "2025-03-24T13:00:00+01:00",
                "duration": "PT30M",
                "costImpact": "PAID"
              }
            ],
            "cost": {
              "fixedCost": 1375,
              "rates": []
            }
          }
        ]
      }
    ],
    "planningWindow": {
      "startDate": "2025-03-24T00:00:00+01:00",
      "endDate": "2025-03-24T23:59:59+01:00"
    }
  }
}
```

### INPUT Structure for Planned Schedule (with Pinned Visits)

When planned data is present in CSV, the mapper creates an INPUT file with all visits pinned:

```json
{
  "modelInput": {
    "visits": [
      {
        "id": "visit_123",
        "location": [59.254417, 18.081677],
        "serviceDuration": "PT30M",
        "timeWindows": [
          {
            "minStartTime": "2025-03-24T09:00:00+01:00",
            "maxStartTime": "2025-03-24T09:00:00+01:00",
            "maxEndTime": "2025-03-24T09:30:00+01:00"
          }
        ],
        "requiredSkills": [{ "name": "Dusch" }],
        "requiredTags": ["Farsta"],
        "priority": "10",
        "pinningRequested": true
      }
    ],
    "vehicles": [
      {
        "id": "employee_456",
        "shifts": [
          {
            "id": "shift_789",
            "minStartTime": "2025-03-24T07:00:00+01:00",
            "maxEndTime": "2025-03-24T16:00:00+01:00",
            "startLocation": [59.254417, 18.081677],
            "endLocation": [59.254417, 18.081677]
          }
        ]
      }
    ]
  }
}
```

**Key Points**:

- All visits have `pinningRequested: true`
- Time windows are fixed (minStartTime = maxStartTime = planned start time)
- This INPUT enables metrics generation without changing assignments

### INPUT Structure for Actual Schedule (with Pinned Visits)

When actual data is present in CSV, the mapper creates an INPUT file with all visits pinned to actual times:

```json
{
  "modelInput": {
    "visits": [
      {
        "id": "visit_123",
        "location": [59.254417, 18.081677],
        "serviceDuration": "PT35M",
        "timeWindows": [
          {
            "minStartTime": "2025-03-24T09:15:00+01:00",
            "maxStartTime": "2025-03-24T09:15:00+01:00",
            "maxEndTime": "2025-03-24T09:50:00+01:00"
          }
        ],
        "requiredSkills": [{ "name": "Dusch" }],
        "requiredTags": ["Farsta"],
        "priority": "10",
        "pinningRequested": true
      }
    ],
    "vehicles": [
      {
        "id": "employee_789",
        "shifts": [
          {
            "id": "shift_actual",
            "minStartTime": "2025-03-24T07:00:00+01:00",
            "maxEndTime": "2025-03-24T16:00:00+01:00",
            "startLocation": [59.254417, 18.081677], // From serviceAreaOfficeLocation
            "endLocation": [59.254417, 18.081677] // From serviceAreaOfficeLocation
          }
        ]
      }
    ]
  }
}
```

**Key Points**:

- All visits have `pinningRequested: true`
- Time windows are fixed to actual execution times
- Duration may differ from planned (actual duration)
- Employee may differ from planned (actual employee)
- Visits with `actualStatus=EXTRA` are included (visits not in original/planned schedules)
- This INPUT enables metrics generation for actual execution

### OUTPUT Structure

The OUTPUT structure represents the solution from Timefold optimization or the planned/actual assignments:

```json
{
  "state": "SOLVING_COMPLETED",
  "run": {
    "id": "run_123",
    "status": "SOLVING_COMPLETED"
  },
  "kpis": {
    "totalTravelTime": "PT2H30M",
    "totalTravelDistance": 150000,
    "totalUnassignedVisits": 2,
    "assignedVisitCount": 98,
    "totalAssignedServiceTime": "PT45H",
    "workingTimeFairness": 0.85
  },
  "modelOutput": {
    "itineraries": [
      {
        "vehicleId": "employee_456",
        "route": [
          {
            "type": "VISIT",
            "visitId": "visit_123",
            "arrivalTime": "2025-03-24T08:15:00+01:00",
            "startServiceTime": "2025-03-24T08:15:00+01:00",
            "departureTime": "2025-03-24T08:45:00+01:00",
            "travelTimeFromPreviousInSeconds": 900,
            "travelDistanceFromPreviousInMeters": 3500
          }
        ]
      }
    ],
    "unassignedVisits": ["visit_456", "visit_789"]
  }
}
```

---

## Mapping Process

### CSV → Normalized Database Conversion

**Primary Mapping** (What's Stored):

1. **Parse CSV**: Read eCare CSV file
2. **Identify Schedule States**: Determine which states are present (unplanned, planned, actual)
3. **Map to Normalized Database**: Convert CSV rows to Prisma inserts:
   - Visits → `visits` table
   - Employees → `employees` table
   - Clients → `clients` table
   - Schedules → `schedules` table
   - Assignments → `solution_assignments` table (for planned/actual)
4. **Handle Flexibility**: Convert `originalStartTime + flexibility + duration` to time windows
5. **Set Pinning**: Set `pinned: true` in database for planned/actual visits

**Secondary Mapping** (Temporary, for Timefold API):

6. **Generate TF INPUT**: Query normalized database → Generate Timefold INPUT JSON (temporary)
7. **Call Timefold API**: Send temporary INPUT JSON to Timefold
8. **Process TF OUTPUT**: Convert Timefold OUTPUT JSON → Normalized database (solution tables)
9. **Create INPUT**: Generate Timefold INPUT JSON

### OUTPUT Generation from Planned/Actual Data

1. **Read Planned/Actual Assignments**: Extract employee assignments and times from CSV
2. **Create Itineraries**: Build route/itinerary structure
3. **Calculate Travel Times**: Use location data to calculate travel times/distances
4. **Generate Metrics**:
   - General schedule metrics: Travel time, efficiency, assignment rate, etc.
   - Home care-specific metrics: Continuity, contact person %, preferred caregivers, unused hours, skills utilization, etc.
5. **Create OUTPUT**: Generate Timefold OUTPUT format JSON

### Comparison Setup

1. **Create Multiple INPUTs**: One for each schedule state (unplanned, planned, actual)
2. **Generate OUTPUTs**:
   - Generate general schedule metrics for planned/actual schedules
   - Calculate home care-specific metrics using metrics engine
3. **Store in Database**: All states stored with same rootId for comparison
4. **Display Comparison**: UI shows side-by-side comparison with metrics

---

## Example CSV Rows

### Example 1: Unplanned Only

```csv
visitId,clientId,clientName,visitDate,originalStartTime,flexibilityMinutes,serviceDuration,visitAddress,visitLocationLat,visitLocationLng,skills,serviceAreas,serviceAreaOfficeLocation,priority,employeeId,employeeName,employeeShiftMinStartTime,employeeShiftMaxEndTime
visit_001,client_123,Anna Andersson,2025-03-24,2025-03-24T09:00:00+01:00,60,PT30M,"Brunskogsbacken 84, 12371 Farsta",59.254417,18.081677,Dusch,Farsta,59.254417,18.081677,10,emp_456,Lisa,2025-03-24T07:00:00+01:00,2025-03-24T16:00:00+01:00
```

### Example 2: Unplanned + Planned + Actual

```csv
visitId,clientId,visitDate,originalStartTime,flexibilityMinutes,serviceDuration,plannedStart,plannedEmployee,actualStart,actualEmployee,actualStatus,visitAddress,visitLocationLat,visitLocationLng,skills,serviceAreas,serviceAreaOfficeLocation
visit_001,client_123,2025-03-24,2025-03-24T09:00:00+01:00,60,PT30M,2025-03-24T09:00:00+01:00,emp_456,2025-03-24T09:15:00+01:00,emp_456,COMPLETED,"Brunskogsbacken 84, 12371 Farsta",59.254417,18.081677,Dusch,Farsta,59.254417,18.081677
```

### Example 2b: Actual with EXTRA Visit

```csv
visitId,clientId,visitDate,originalStartTime,flexibilityMinutes,serviceDuration,actualStart,actualEmployee,actualStatus,visitAddress,skills,serviceAreas
visit_999,client_999,2025-03-24,2025-03-24T14:00:00+01:00,0,PT45M,2025-03-24T14:30:00+01:00,emp_789,EXTRA,"Urgent Address 123, Farsta",Dusch,Farsta
```

**Note**: Visit `visit_999` has `actualStatus=EXTRA` because it was not part of the original or planned schedule (e.g., urgent visit added during execution).

### Example 3: Movable Visit with Frequency

```csv
visitId,clientId,visitDate,originalStartTime,flexibilityMinutes,serviceDuration,movable,movableFrequency,continuity,preferredEmployees,visitAddress,visitLocationLat,visitLocationLng,skills,serviceAreas
visit_002,client_456,2025-03-24,2025-03-24T14:00:00+01:00,120,PT1H,TRUE,weekly,medium,"Anna,Björn","Another Address 45, 12371 Farsta",59.256803,18.084355,Cleaning,Farsta
```

### Example 4: With Breaks and Costs

```csv
visitId,clientId,visitDate,employeeId,employeeShiftMinStartTime,employeeShiftMaxEndTime,employeeShiftBreaksJSON,employeeShiftCostJSON
visit_001,client_123,2025-03-24,emp_456,2025-03-24T07:00:00+01:00,2025-03-24T16:00:00+01:00,"[{""id"": ""break_1"", ""type"": ""FLOATING"", ""minStartTime"": ""2025-03-24T11:00:00+01:00"", ""maxEndTime"": ""2025-03-24T13:00:00+01:00"", ""duration"": ""PT30M"", ""costImpact"": ""PAID""}]","{""fixedCost"": 1375, ""rates"": []}"
```

---

## Biståndsbeslut Format (Movable Visits)

Biståndsbeslut (municipal decisions) define recurring visit requirements for clients. These documents contain the **basic requirements** - Caire will optimize the flexibility, priority, continuity, and preferred times.

### What's in Biståndsbeslut (Source Data)

Biståndsbeslut documents typically contain:

- Client information (ID, name)
- Task type (e.g., "Cleaning", "Personal Care")
- Number of visits per period (e.g., "2 x weekly", "3 x daily", "1 x monthly")
- Visit duration
- Required skills (if specified)

### What Caire Will Optimize

The following are **NOT** in biståndsbeslut - Caire will optimize these:

- **Flexibility**: Time windows for when visits can be scheduled
- **Priority**: Visit priority levels
- **Continuity**: Continuity preferences (Caire will optimize for best continuity)
- **Preferred time**: Preferred time bands/windows (Caire will find optimal times)

### Option 1: CSV Format

| Field             | Type              | Required | Description                                                                  |
| ----------------- | ----------------- | -------- | ---------------------------------------------------------------------------- |
| `clientId`        | String            | Yes      | Client identifier                                                            |
| `clientName`      | String            | Yes      | Client name                                                                  |
| `taskType`        | String            | Yes      | Task type (e.g., "Cleaning", "Personal Care")                                |
| `visitsPerPeriod` | String            | Yes      | Number of visits per period (e.g., "2 x weekly", "3 x daily", "1 x monthly") |
| `period`          | String            | Yes      | Period type: "daily", "weekly", "bi-weekly", "monthly"                       |
| `duration`        | ISO 8601 duration | Yes      | Visit duration (e.g., PT30M, PT1H)                                           |
| `requiredSkills`  | Comma-separated   | Optional | Required skills (if specified in biståndsbeslut)                             |

**Note**: The `visitsPerPeriod` field should specify both the count and period, e.g.:

- "2 x weekly" = 2 visits per week
- "3 x daily" = 3 visits per day
- "1 x monthly" = 1 visit per month

### Option 2: PDF Format

If biståndsbeslut are provided as PDFs, Caire will use OCR to extract:

- Client information (ID, name)
- Task type
- Number of visits per period (e.g., "2 x weekly")
- Visit duration
- Required skills (if specified)

**Note**: Caire will NOT extract flexibility, priority, continuity, or preferred times from PDFs - these will be optimized by Caire based on the schedule context.

---

## Validation and Error Handling

### Required Field Combinations

- **Unplanned**: visitId, clientId, visitDate, visitAddress (required), time information (windows OR original+flexibility), serviceDuration, employee shift information
- **Planned**: All unplanned fields + plannedStart, plannedEmployee
- **Actual**: All unplanned fields + actualStart, actualEmployee, actualStatus (must include "EXTRA" for visits not in original/planned)

### Time Window Validation

- `minStartTime <= maxStartTime <= maxEndTime`
- Time windows must be within employee shift times
- Duration must be positive

### Format Validation

- ISO 8601 datetime format: `YYYY-MM-DDTHH:MM:SS+TZ:TZ`
- ISO 8601 duration format: `PT30M`, `PT1H30M`
- Coordinates: Decimal degrees (lat: -90 to 90, lng: -180 to 180)
- JSON fields: Valid JSON syntax

### Error Messages

The system will provide clear error messages for:

- Missing required fields
- Invalid date/time formats
- Invalid coordinate values
- Invalid JSON syntax
- Time window violations
- Missing employee data

---

## CSV Metadata/Header Fields (To Be Assessed in Phase 1)

**Status**: ⏳ **To be validated with Attendo in Phase 1**

**Note**: Service area filtering is handled by Caire internally based on service area tags in the CSV data (client, visit, and employee service area columns). No metadata needed for service area filtering.

**Ideal Capability**: To specify planning window, include these fields as CSV metadata or header comments:

| Field                 | Type          | Required | Description                                                                                         |
| --------------------- | ------------- | -------- | --------------------------------------------------------------------------------------------------- |
| `planningWindowStart` | ISO 8601 date | Optional | Start date of planning window (e.g., 2025-03-24) - if not provided, inferred from `visitDate` range |
| `planningWindowEnd`   | ISO 8601 date | Optional | End date of planning window (e.g., 2025-03-30) - if not provided, inferred from `visitDate` range   |

**Example CSV with metadata** (if eCare supports it):

```csv
# planningWindowStart=2025-03-24
# planningWindowEnd=2025-03-30
visitId,clientId,visitDate,visitAddress,serviceAreas,...
```

**Questions for Phase 1**:

- Does eCare CSV export support metadata/header comments?
- Can eCare include planning window dates in export?

**Fallback Options** (if eCare doesn't support metadata):

- Caire will infer planning window from the date range of `visitDate` values in the CSV
- Caire can combine multiple daily CSVs to create weekly/monthly planning windows
- Service area filtering is handled by Caire based on service area tags in the data (no metadata needed)

## Supported Schedule Combinations

The CSV format supports any combination of the three schedule states:

1. **Unplanned only** - For new schedule optimization
2. **Planned only** - For importing existing planned schedules (creates INPUT with pinned visits)
3. **Actual only** - For importing actual execution data (creates INPUT with pinned visits)
4. **Unplanned + Planned** - Compare unplanned vs planned
5. **Unplanned + Actual** - Compare unplanned vs actual
6. **Planned + Actual** - Compare planned vs actual (plan vs reality)
7. **All three** - Complete comparison (unplanned vs planned vs actual vs optimized)

---

## Metrics Generation for Planned and Actual Schedules

**Architecture**: When Planned or Actual schedules are imported:

1. **Database Storage**: Data stored in normalized database tables (schedules, visits, solution_assignments)
2. **TF INPUT Generation**: Timefold INPUT JSON generated on-the-fly with all visits pinned (`pinningRequested: true`)
3. **Time Setting**: Visit times are set to the planned/actual start times in the generated INPUT
4. **Metrics Generation**:
   - **General schedule metrics**: Travel time, efficiency, assignment rate, etc. (calculated from schedule structure)
   - **Home care-specific metrics**: Continuity, contact person %, preferred caregivers, unused hours, skills utilization, etc. (calculated by metrics engine)
5. **No Assignment Changes**: Metrics are calculated without changing visit assignments
6. **Solution Storage**: Metrics stored in normalized database (solution_metrics table)

**Key Points**:

- ✅ Planned/actual data stored in **normalized database** (not Timefold JSON)
- ✅ Timefold INPUT generated **on-the-fly** when needed (temporary)
- ✅ **General schedule metrics**: Domain-agnostic metrics (travel time, efficiency, assignment rate)
- ✅ **Home care-specific metrics**: Domain-specific metrics calculated by metrics engine
- ✅ Metrics stored in **normalized database** (solution_metrics table)
- ✅ All schedule states comparable with consistent metrics
- ✅ No historical assignments changed

---

## Next Steps

1. **Data Collection**: Attendo exports eCare CSV data according to this specification
2. **Data Validation**: Caire validates imported data and reports any issues
3. **Mapping**: Caire mapper converts CSV to normalized database (Prisma inserts)
4. **TF INPUT Generation**: Timefold INPUT JSON generated on-the-fly from database when needed
5. **Optimization**: Timefold optimizes schedules as needed
6. **Solution Storage**: Timefold OUTPUT stored in normalized database (solution tables)
7. **Comparison**: All schedule states are compared with consistent metrics

---

---

## 5. Next Steps

### 5.1 Data Collection & Validation

1. **Data Discovery** (Week 1)
   - [ ] Attendo exports sample eCare CSV data
   - [ ] Caire analyzes available fields
   - [ ] Identify data gaps
   - [ ] Document workarounds

2. **Data Validation** (Week 2)
   - [ ] Validate data completeness
   - [ ] Test data quality
   - [ ] Verify coordinate accuracy
   - [ ] Test import process

3. **Gap Resolution** (Week 2-3)
   - [ ] Implement workarounds for missing data
   - [ ] Add manual data entry if needed
   - [ ] Validate optimization works with available data

### 5.2 Security & Compliance Setup

1. **DPA Agreement** (Before pilot start)
   - [ ] Review DPA draft with Attendo
   - [ ] Sign DPA agreement
   - [ ] Document data processing procedures

2. **Security Implementation** (Before pilot start)
   - [ ] Implement encryption (at rest and in transit)
   - [ ] Set up access controls
   - [ ] Configure audit logging
   - [ ] Test security measures

3. **Compliance Review** (Ongoing)
   - [ ] Review DPIA documentation
   - [ ] Ensure GDPR compliance
   - [ ] Monitor data access
   - [ ] Document data retention

---

## References

- [Attendo Pilot Plan](./PILOT_PLAN.md) - Pilot objectives, timeline, phases
- [PILOT_PLAN.md](./PILOT_PLAN.md) - Complete pilot plan with system overview
- [PILOT_OUT_OF_SCOPE.md](./PILOT_OUT_OF_SCOPE.md) - What's excluded from pilot
