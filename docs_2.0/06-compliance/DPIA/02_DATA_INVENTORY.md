# CAIRE Platform - Data Inventory

**Document:** Complete mapping of personal data
**Version:** 1.1
**Date:** 2025-12-08 (Updated: 2026-01-27)
**Purpose:** Basis for DPIA - identify all personal data processed

---

## 🆕 Update Log (2026-01-27)

**Migration:** `20260127063104_add_data_model_2_0_fields`

### Privacy-Focused Design Decisions

The following data minimization and privacy-first design decisions were implemented:

#### Employee Data

- ✅ **Home addresses kept OPTIONAL** (not required) - stored only when provided
- ✅ Added `gender` field (optional) - Low sensitivity, demographic data only
- ✅ Salary moved to separate `EmployeeCost` table with effective dates - Better audit trail

#### Client Data

- ✅ **birthYear instead of full dateOfBirth** - Reduced sensitivity (GDPR Art. 5)
  - Storing only year (e.g., 1950) instead of full date (1950-06-15)
  - Sufficient for age-related care planning
  - Significantly reduces re-identification risk
- ✅ **diagnoses field OPTIONAL** - Sensitive health data (Art. 9) made optional
  - Organizations can use skill-based matching instead (e.g., "dementia care" skill)
  - Avoids storing explicit medical diagnoses
  - Legal basis shifts from Art. 9 to Art. 6.1(f) when using skills
- ✅ **allergies stored separately** - Safety-critical but not medical diagnoses
  - Necessary for employee safety and service quality
  - Not considered sensitive health data in scheduling context
  - Legal basis: Art. 6.1(f) - Legitimate interest
- ✅ **contactPerson as text** - No FK to sensitive employee data
  - Stores employee name/ID as simple text
  - Avoids creating additional data relationships
  - Privacy-first design

### Data Minimization Impact

| Original Field             | Implemented              | Sensitivity Reduction   |
| -------------------------- | ------------------------ | ----------------------- |
| `dateOfBirth` (full date)  | `birthYear` (year only)  | High → Medium           |
| `diagnoses` (required)     | `diagnoses` (optional)   | High → Optional         |
| `homeAddress` (not stored) | `homeAddress` (optional) | N/A → Medium (optional) |

**Net Privacy Impact:** ✅ **Improved** - Reduced data collection while maintaining functionality

---

## 1. Summary

This data inventory maps **all personal data** that the CAIRE platform processes, from which source they come, how they are used, where they are stored, and which legal basis applies.

### Processing Scope (Pilot)

**Included in pilot:**

- ✅ Employee data (name, contact info, employment info)
- ✅ Customer data (basic - name, address, visit times)
- ✅ Schedule data (work hours, assignments)
- ✅ Technical metadata (logs, sessions)

**Excluded from pilot:**

- ❌ Sensitive health data (per GDPR Art. 9)
- ❌ Personal identification numbers (SSN)
- ❌ Detailed care plans and diagnoses

---

## 2. Data Categories - Overview

| Category           | Number of Fields | Storage Location     | Risk Level | Legal Basis |
| ------------------ | ---------------- | -------------------- | ---------- | ----------- |
| **Employee Data**  | 15               | AWS RDS (EU)         | Medium     | Art. 6.1(f) |
| **Customer Data**  | 9                | AWS RDS (EU)         | Medium     | Art. 6.1(f) |
| **Schedule Data**  | 20               | AWS RDS (EU)         | Low        | Art. 6.1(f) |
| **Authentication** | 8                | Clerk (EU)           | Medium     | Art. 6.1(f) |
| **System Logs**    | 10               | AWS RDS/CloudWatch   | Low        | Art. 6.1(f) |
| **AI Processing**  | 5                | Timefold (temporary) | Medium     | Art. 6.1(f) |

---

## 3. Detailed Data Inventory

### 3.1 EMPLOYEE DATA (employees table)

| Data Field                       | Example                              | Source                | Usage                         | Storage Location | Retention                   | Legal Basis | Measures                      |
| -------------------------------- | ------------------------------------ | --------------------- | ----------------------------- | ---------------- | --------------------------- | ----------- | ----------------------------- |
| **id**                           | UUID                                 | System-generated      | Primary key                   | AWS RDS          | Permanent                   | Art. 6.1(f) | -                             |
| **organization_id**              | UUID                                 | System                | Tenant-isolation              | AWS RDS          | Permanent                   | Art. 6.1(f) | RBAC                          |
| **external_id**                  | "EMP-12345"                          | CSV Upload            | Reference to source system    | AWS RDS          | Permanent                   | Art. 6.1(f) | -                             |
| **name**                         | "Anna Andersson"                     | CSV Upload            | Identification, scheduling    | AWS RDS          | Until termination + 1 year  | Art. 6.1(f) | Encryption, RBAC              |
| **email**                        | "anna@example.com"                   | CSV Upload            | Communication, notifications  | AWS RDS          | Until termination + 1 year  | Art. 6.1(f) | Encryption, RBAC              |
| **phone**                        | "+46701234567"                       | CSV Upload            | Contact when needed           | AWS RDS          | Until termination + 1 year  | Art. 6.1(f) | Encryption, RBAC              |
| **role**                         | "CAREGIVER"                          | CSV Upload            | Scheduling, authorization     | AWS RDS          | Until termination           | Art. 6.1(f) | RBAC                          |
| **contract_type**                | "full_time"                          | CSV Upload            | Employment law planning       | AWS RDS          | Until termination + 7 years | Art. 6.1(c) | RBAC                          |
| **monthly_salary**               | 35000 SEK                            | CSV Upload            | Cost calculation              | AWS RDS          | Until termination + 7 years | Art. 6.1(c) | Encryption, restricted access |
| **hourly_salary**                | 220 SEK                              | CSV Upload            | Cost calculation              | AWS RDS          | Until termination + 7 years | Art. 6.1(c) | Encryption, restricted access |
| **start_date**                   | "2024-01-15"                         | CSV Upload            | Availability, scheduling      | AWS RDS          | Until termination + 1 year  | Art. 6.1(f) | -                             |
| **end_date**                     | "2025-12-31"                         | CSV Upload            | Availability, scheduling      | AWS RDS          | Until termination + 1 year  | Art. 6.1(f) | -                             |
| **transport_mode**               | "DRIVING"                            | CSV Upload            | Route optimization            | AWS RDS          | Until termination           | Art. 6.1(f) | -                             |
| **gender** _(new)_               | "male", "female", "other"            | CSV Upload            | Demographic data (optional)   | AWS RDS          | Until termination + 1 year  | Art. 6.1(f) | Optional field, RBAC          |
| **status** _(new)_               | "active", "inactive", "on_leave"     | CSV Upload            | Employment status, scheduling | AWS RDS          | Until termination + 1 year  | Art. 6.1(f) | -                             |
| **role** _(new)_                 | "CAREGIVER", "DRIVER", "COORDINATOR" | CSV Upload            | Authorization, scheduling     | AWS RDS          | Until termination + 1 year  | Art. 6.1(f) | RBAC                          |
| **phoniro_employee_id** _(new)_  | "PHON-12345"                         | CSV Upload            | Reference to Phoniro system   | AWS RDS          | Until termination + 1 year  | Art. 6.1(f) | -                             |
| **recent_client_visits** _(new)_ | JSON array                           | System-calculated     | Continuity tracking cache     | AWS RDS          | 90 days rolling             | Art. 6.1(f) | Temporary cache, auto-purge   |
| **homeAddress** _(optional)_     | "Storgatan 1, Stockholm"             | CSV Upload (optional) | Emergency contact, future use | AWS RDS          | Until termination + 1 year  | Art. 6.1(f) | Optional field, encryption    |
| **homeLatitude** _(optional)_    | 59.3293                              | System-calculated     | Geocoded from homeAddress     | AWS RDS          | Until termination + 1 year  | Art. 6.1(f) | Optional, derived data        |
| **homeLongitude** _(optional)_   | 18.0686                              | System-calculated     | Geocoded from homeAddress     | AWS RDS          | Until termination + 1 year  | Art. 6.1(f) | Optional, derived data        |
| **metadata**                     | JSON {"language": "sv", ...}         | CSV Upload            | Matching, preferences         | AWS RDS          | Until termination           | Art. 6.1(f) | -                             |
| **created_at**                   | Timestamp                            | System                | Audit trail                   | AWS RDS          | Permanent                   | Art. 6.1(f) | -                             |
| **updated_at**                   | Timestamp                            | System                | Audit trail                   | AWS RDS          | Permanent                   | Art. 6.1(f) | -                             |
| **deleted_at**                   | Timestamp (nullable)                 | System                | Soft-delete                   | AWS RDS          | Permanent                   | Art. 6.1(f) | Soft delete                   |

**Note:**

- Salary information is only stored if the customer provides it (optional)
- **Employee home addresses are OPTIONAL** (updated 2026-01-27). Fields `homeAddress`, `homeLatitude`, `homeLongitude` are nullable and only stored if provided. Route optimization uses office/depot locations (from organization or service area addresses) as the default start and end point for all employees. Home addresses may be stored for:
  - Emergency contact purposes
  - Special routing scenarios (if explicitly configured)
  - Future functionality requirements
  - **Privacy measure:** Fields are optional, not required for platform operation
- **Competencies and certifications:** Employee competencies (e.g., "nurse qualification", "lifting certification", "driving license") are stored in the metadata field or separate competencies table. These are personal data per Art. 6.1(f) but are **not** sensitive personal data (Art. 9). They are necessary for matching staff to appropriate visits and ensuring safety and quality of care.

---

### 3.2 CUSTOMER DATA (clients table - basic information)

| Data Field                      | Example                   | Source                | Usage                               | Storage Location | Retention | Legal Basis | Measures                                    |
| ------------------------------- | ------------------------- | --------------------- | ----------------------------------- | ---------------- | --------- | ----------- | ------------------------------------------- |
| **id**                          | UUID                      | System                | Primary key                         | AWS RDS          | 2 years   | Art. 6.1(f) | -                                           |
| **organization_id**             | UUID                      | System                | Tenant-isolation                    | AWS RDS          | 2 years   | Art. 6.1(f) | RBAC                                        |
| **external_id**                 | "CLIENT-12345"            | CSV Upload            | Reference to source                 | AWS RDS          | 2 years   | Art. 6.1(f) | -                                           |
| **name**                        | "Anna Larsson"            | CSV Upload            | Identification                      | AWS RDS          | 2 years   | Art. 6.1(f) | Encryption, RBAC                            |
| **address**                     | "Storgatan 1, Stockholm"  | CSV Upload            | Route planning                      | AWS RDS          | 2 years   | Art. 6.1(f) | Encryption, tenant-isolation                |
| **phone**                       | "+46701234567"            | CSV Upload            | Contact when needed                 | AWS RDS          | 2 years   | Art. 6.1(f) | Encryption, RBAC                            |
| **port_code**                   | "1234"                    | CSV Upload            | Access information                  | AWS RDS          | 2 years   | Art. 6.1(f) | Encryption                                  |
| **continuity_preference**       | "employee_e456"           | CSV Upload            | Quality assurance                   | AWS RDS          | 2 years   | Art. 6.1(f) | RBAC                                        |
| **gender** _(new)_              | "male", "female", "other" | CSV Upload            | Demographic data (optional)         | AWS RDS          | 2 years   | Art. 6.1(f) | Optional field, RBAC                        |
| **birthYear** _(new)_           | 1950                      | CSV Upload            | Age-related care planning           | AWS RDS          | 2 years   | Art. 6.1(f) | Year only (privacy-first)                   |
| **contactPerson** _(new)_       | "Anna Andersson"          | CSV Upload            | Continuity tracking (70% threshold) | AWS RDS          | 2 years   | Art. 6.1(f) | Text field, RBAC                            |
| **latitude** _(denormalized)_   | 59.3293                   | System-calculated     | Route optimization                  | AWS RDS          | 2 years   | Art. 6.1(f) | Derived from address                        |
| **longitude** _(denormalized)_  | 18.0686                   | System-calculated     | Route optimization                  | AWS RDS          | 2 years   | Art. 6.1(f) | Derived from address                        |
| **municipality** _(new)_        | "Stockholm"               | CSV Upload            | Service area planning               | AWS RDS          | 2 years   | Art. 6.1(f) | -                                           |
| **careLevel** _(new)_           | "Level 2"                 | CSV Upload (optional) | Care planning                       | AWS RDS          | 2 years   | Art. 6.1(f) | Optional, non-medical                       |
| **diagnoses** _(new, optional)_ | ["dementia"]              | CSV Upload (optional) | Care planning (sensitive)           | AWS RDS          | 2 years   | Art. 9      | **Optional**, encryption, restricted access |
| **allergies** _(new)_           | ["penicillin", "latex"]   | CSV Upload            | Safety-critical                     | AWS RDS          | 2 years   | Art. 6.1(f) | Safety data, not medical diagnosis          |
| **languagePreference** _(new)_  | "Swedish"                 | CSV Upload            | Service quality                     | AWS RDS          | 2 years   | Art. 6.1(f) | Matching criteria                           |
| **created_at**                  | Timestamp                 | System                | Audit trail                         | AWS RDS          | 2 years   | Art. 6.1(f) | -                                           |
| **updated_at**                  | Timestamp                 | System                | Audit trail                         | AWS RDS          | 2 years   | Art. 6.1(f) | -                                           |
| **deleted_at**                  | Timestamp (nullable)      | System                | Soft-delete                         | AWS RDS          | 2 years   | Art. 6.1(f) | Soft delete                                 |

**Data Minimization for Pilot:**

- ✅ Basic customer data (name, address, visit times) - **NOT sensitive health data**
- ✅ Only anonymized geo-coordinates for route optimization
- ✅ Visits represented as "Assignment ID: X123" without sensitive info
- ✅ **Service requirements (non-sensitive):** Required competencies or skills needed for specific visits (e.g., "needs lifting certification", "requires nurse qualification", "two-person visit", "requires driving license"). These are stored as technical/competence-based labels (service requirements), not medical causes. They do **not** reveal health diagnoses or sensitive personal data. Legal basis: Art. 6.1(f) - Legitimate interest.
- ❌ NO health diagnoses, medications, or detailed care plans

---

### 3.3 SCHEDULE DATA (schedules, visits, shifts tables)

| Data Field                        | Example                     | Source        | Usage                   | Storage Location | Retention | Legal Basis | Measures             |
| --------------------------------- | --------------------------- | ------------- | ----------------------- | ---------------- | --------- | ----------- | -------------------- |
| **schedule.id**                   | UUID                        | System        | Primary key             | AWS RDS          | 2 years   | Art. 6.1(f) | -                    |
| **schedule.date**                 | "2025-01-15"                | System/Import | Schedule identification | AWS RDS          | 2 years   | Art. 6.1(f) | -                    |
| **schedule.name**                 | "Daily schedule 2025-01-15" | User          | Description             | AWS RDS          | 2 years   | Art. 6.1(f) | -                    |
| **schedule.organization_id**      | UUID                        | System        | Tenant-isolation        | AWS RDS          | 2 years   | Art. 6.1(f) | RBAC                 |
| **schedule.status**               | "published"                 | System        | Workflow status         | AWS RDS          | 2 years   | Art. 6.1(f) | -                    |
| **visits.id**                     | UUID                        | System        | Primary key             | AWS RDS          | 2 years   | Art. 6.1(f) | -                    |
| **visits.schedule_id**            | UUID                        | System        | Link to schedule        | AWS RDS          | 2 years   | Art. 6.1(f) | -                    |
| **visits.client_id**              | UUID                        | CSV Upload    | Link to customer        | AWS RDS          | 2 years   | Art. 6.1(f) | RBAC                 |
| **visits.planned_start_time**     | "09:00:00"                  | System/AI     | Schedule time           | AWS RDS          | 2 years   | Art. 6.1(f) | -                    |
| **visits.planned_end_time**       | "10:00:00"                  | System/AI     | Schedule time           | AWS RDS          | 2 years   | Art. 6.1(f) | -                    |
| **visits.duration**               | 60 (minutes)                | CSV Upload    | Planning                | AWS RDS          | 2 years   | Art. 6.1(f) | -                    |
| **visits.address**                | JSON (geo-coordinates)      | CSV Upload    | Route optimization      | AWS RDS          | 2 years   | Art. 6.1(f) | Anonymized geo-point |
| **visits.required_skills**        | ["lifting", "nurse"]        | CSV Upload    | Service requirements    | AWS RDS          | 2 years   | Art. 6.1(f) | RBAC                 |
| **employee_shifts.id**            | UUID                        | System        | Primary key             | AWS RDS          | 2 years   | Art. 6.1(f) | -                    |
| **employee_shifts.employee_id**   | UUID                        | System        | Link to employee        | AWS RDS          | 2 years   | Art. 6.1(f) | RBAC                 |
| **employee_shifts.schedule_id**   | UUID                        | System        | Link to schedule        | AWS RDS          | 2 years   | Art. 6.1(f) | -                    |
| **employee_shifts.start_time**    | "08:00:00"                  | System/AI     | Work time start         | AWS RDS          | 2 years   | Art. 6.1(f) | -                    |
| **employee_shifts.end_time**      | "16:00:00"                  | System/AI     | Work time end           | AWS RDS          | 2 years   | Art. 6.1(f) | -                    |
| **employee_shifts.break_minutes** | 30                          | System/Rules  | Breaks                  | AWS RDS          | 2 years   | Art. 6.1(f) | -                    |
| **employee_shifts.notes**         | "Prefers morning shift"     | Planner       | Comments                | AWS RDS          | 2 years   | Art. 6.1(f) | RBAC                 |

**Data Minimization for Pilot:**

- ✅ Only basic customer data (name, address) - **NOT health data**
- ✅ Only anonymized geo-coordinates for route optimization
- ✅ Visits represented with assignment IDs without sensitive info

---

### 3.4 AUTHENTICATION & USERS (Clerk + organization_members)

| Data Field             | Example              | Source | Usage                | Storage Location     | Retention               | Legal Basis | Measures                |
| ---------------------- | -------------------- | ------ | -------------------- | -------------------- | ----------------------- | ----------- | ----------------------- |
| **user.id**            | Clerk User ID        | Clerk  | Primary key          | Clerk (EU)           | Until account deleted   | Art. 6.1(b) | MFA, SSO                |
| **user.email**         | "planner@attendo.se" | User   | Login, communication | Clerk (EU)           | Until account deleted   | Art. 6.1(b) | MFA, encryption         |
| **user.name**          | "Lisa Svensson"      | User   | Identification in UI | Clerk (EU)           | Until account deleted   | Art. 6.1(b) | -                       |
| **user.password_hash** | bcrypt hash          | Clerk  | Authentication       | Clerk (EU)           | Until account deleted   | Art. 6.1(b) | Hashed, salt            |
| **user.mfa_enabled**   | true/false           | User   | Security             | Clerk (EU)           | Until account deleted   | Art. 6.1(b) | MFA enforcement         |
| **session.jwt_token**  | JWT                  | Clerk  | Session management   | Clerk (EU) + client  | 60 min (token lifetime) | Art. 6.1(b) | HttpOnly cookie, secure |
| **session.ip_address** | "192.168.1.1"        | System | Security, audit      | AWS RDS (audit_logs) | 90 days                 | Art. 6.1(f) | Anonymized after 90d    |
| **session.user_agent** | "Mozilla/5.0..."     | System | Security, audit      | AWS RDS (audit_logs) | 90 days                 | Art. 6.1(f) | Anonymized after 90d    |
| **org_member.user_id** | UUID                 | System | Link user ↔ org      | AWS RDS              | Until account deleted   | Art. 6.1(b) | RBAC                    |
| **org_member.role**    | "scheduler"          | Admin  | Permission level     | AWS RDS              | Until account deleted   | Art. 6.1(b) | RBAC enforcement        |

---

### 3.5 SYSTEM LOGS & AUDIT TRAIL

| Data Field                  | Example             | Source | Usage                  | Storage Location | Retention | Legal Basis | Measures                |
| --------------------------- | ------------------- | ------ | ---------------------- | ---------------- | --------- | ----------- | ----------------------- |
| **audit_log.id**            | UUID                | System | Primary key            | AWS RDS          | 90 days   | Art. 6.1(f) | Auto-deletion after 90d |
| **audit_log.user_id**       | UUID                | System | Who performed action   | AWS RDS          | 90 days   | Art. 6.1(f) | Auto-deletion           |
| **audit_log.action**        | "UPDATE"            | System | Type of action         | AWS RDS          | 90 days   | Art. 6.1(f) | -                       |
| **audit_log.entity_type**   | "schedules"         | System | What was changed       | AWS RDS          | 90 days   | Art. 6.1(f) | -                       |
| **audit_log.entity_id**     | UUID                | System | Which object           | AWS RDS          | 90 days   | Art. 6.1(f) | -                       |
| **audit_log.changes**       | JSON (before/after) | System | What was changed       | AWS RDS          | 90 days   | Art. 6.1(f) | Encrypted               |
| **audit_log.ip_address**    | "192.168.1.1"       | System | From where             | AWS RDS          | 90 days   | Art. 6.1(f) | Anonymized              |
| **audit_log.created_at**    | Timestamp           | System | When                   | AWS RDS          | 90 days   | Art. 6.1(f) | -                       |
| **api_log.request_id**      | UUID                | System | Request tracking       | CloudWatch       | 30 days   | Art. 6.1(f) | Auto-deletion           |
| **api_log.endpoint**        | "/api/schedules"    | System | Which endpoint         | CloudWatch       | 30 days   | Art. 6.1(f) | -                       |
| **api_log.response_time**   | 150ms               | System | Performance monitoring | CloudWatch       | 30 days   | Art. 6.1(f) | Aggregated              |
| **error_log.error_message** | "Database timeout"  | System | Troubleshooting        | Sentry           | 30 days   | Art. 6.1(f) | Sanitized (no PII)      |

**Data Sanitization:**

- IP addresses anonymized after 90 days (last octet replaced with "0")
- User-agents truncated to browser type only
- Sensitive data (passwords, tokens) is **never** logged

---

### 3.6 AI PROCESSING (Timefold)

| Data Field              | Example                         | Source   | Usage                | Storage Location     | Retention              | Legal Basis | Measures              |
| ----------------------- | ------------------------------- | -------- | -------------------- | -------------------- | ---------------------- | ----------- | --------------------- |
| **dataset.id**          | "ds_abc123"                     | Timefold | Dataset reference    | AWS RDS (metadata)   | 2 years                | Art. 6.1(f) | Only ID stored        |
| **employee_anonymized** | {"id": "e123", "skills": [...]} | CAIRE    | Optimization         | Timefold (temporary) | ❌ Deleted immediately | Art. 6.1(f) | No persistent storage |
| **visit_anonymized**    | {"id": "v456", "duration": 60}  | CAIRE    | Optimization         | Timefold (temporary) | ❌ Deleted immediately | Art. 6.1(f) | No persistent storage |
| **geo_coordinates**     | {"lat": 59.3, "lng": 18.1}      | CAIRE    | Route optimization   | Timefold (temporary) | ❌ Deleted immediately | Art. 6.1(f) | Anonymized            |
| **optimization_result** | JSON (suggestions)              | Timefold | Schedule suggestions | AWS RDS              | 2 years                | Art. 6.1(f) | Encrypted             |

**Important:**

- Timefold **NEVER** receives names of staff or customers
- Only technical info (ID, competencies, times, anonymized positions)
- **No persistent storage** at Timefold - data deleted after processing
- Dataset-ID stored in CAIRE for traceability, but actual data only exists in AWS RDS

---

## 4. Data Flow Diagram with Personal Data

```
┌──────────────────┐
│  Attendo Planner │ (Data Controller: Attendo)
│  CSV Upload      │
└────────┬─────────┘
         │ CSV File
         │ (Encrypted TLS 1.3)
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  CAIRE Import & Validation                         │
│  • Validates format                                │
│  • Normalizes data                                 │
│  • Assigns organization_id (tenant-isolation)      │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  AWS RDS PostgreSQL (Stockholm)                    │
│  • Encrypted at rest (AES-256)                     │
│  • Row-level security (organization_id filter)     │
│  • Soft-deletes (deleted_at)                       │
│                                                     │
│  Contains:                                         │
│  • Employee data (name, email, phone, salary)      │
│  • Customer data (name, address, visit times)      │
│  • Schedule data (times, shifts, routes)           │
│  • Audit logs (who did what, when)                 │
└────────┬────────────────────────────────────────────┘
         │
         ├─────► (READ) GraphQL API ─► React UI
         │       (Clerk JWT auth, RBAC)
         │
         └─────► (READ) Optimization Engine
                 │
                 ▼
         ┌───────────────────────────┐
         │  Timefold (Temporary)     │
         │  • ANONYMIZED data         │
         │  • No persistent storage  │
         │  • Deleted after 5-10 min │
         └───────────┬───────────────┘
                     │
                     ▼ (Returns suggestions)
         ┌───────────────────────────┐
         │  AWS RDS (Store results)  │
         └───────────────────────────┘
```

---

## 5. Summary per GDPR Category

### Personal Data (Art. 6.1)

| Category                      | Number of Fields                    | Storage       | Retention             | Legal Basis       |
| ----------------------------- | ----------------------------------- | ------------- | --------------------- | ----------------- |
| **Identity Information**      | 3 (name, email, phone)              | AWS RDS       | Termination + 1 year  | Art. 6.1(f)       |
| **Contact Information**       | 3 (email, phone, address)           | AWS RDS       | Termination + 1 year  | Art. 6.1(f)       |
| **Employment Information**    | 8 (role, contract, salary, dates)   | AWS RDS       | Termination + 7 years | Art. 6.1(c) + (f) |
| **Location Information**      | 1 (geo-coordinates for visits only) | AWS RDS       | 2 years               | Art. 6.1(f)       |
| **Electronic Identification** | 3 (IP, user-agent, session)         | AWS RDS/Clerk | 90 days               | Art. 6.1(f)       |

### Sensitive Personal Data (Art. 9)

| Category               | Status              |
| ---------------------- | ------------------- |
| **Health Data**        | ❌ **NOT IN PILOT** |
| **SSN**                | ❌ **NOT IN PILOT** |
| **Ethnic Background**  | ❌ Not processed    |
| **Political Views**    | ❌ Not processed    |
| **Religion**           | ❌ Not processed    |
| **Sexual Orientation** | ❌ Not processed    |

---

## 6. Data Minimization - Measures

### What We DO

✅ Store only data needed for schedule optimization  
✅ Anonymize data before AI processing (Timefold)  
✅ Use UUID instead of SSN  
✅ Soft-deletes - data can be restored if mistake  
✅ Automatic deletion of logs after 90 days

### What We DO NOT do

❌ Do NOT store sensitive health data in pilot  
❌ Do NOT store sensitive personal data (Art. 9)  
❌ Do NOT share data with third parties for marketing  
❌ Do NOT use data for AI training  
❌ Do NOT store credit card info or payment data

---

## 7. Retention Policy (Storage Periods)

| Data Type                      | Storage Period                   | Justification                    |
| ------------------------------ | -------------------------------- | -------------------------------- |
| **Employee Data (active)**     | During employment                | Ongoing processing               |
| **Employee Data (terminated)** | +1 year after termination        | Possibility to rehire, history   |
| **Salary Information**         | +7 years after termination       | Accounting law, tax authority    |
| **Customer Data (active)**     | During care relationship         | Ongoing processing               |
| **Customer Data (terminated)** | +1 year after termination        | History, quality assurance       |
| **Schedule History**           | 2 years                          | Quality assurance, analysis      |
| **Audit Logs**                 | 90 days                          | Security, incident investigation |
| **API Logs**                   | 30 days                          | Performance monitoring           |
| **Session Tokens**             | 60 minutes                       | Security (short-lived tokens)    |
| **Backups**                    | 7 days (daily), 4 weeks (weekly) | Disaster recovery                |

**Automatic Deletion:**
The system automatically deletes data when the retention period expires (soft-delete → hard-delete).

---

## 8. Data Subject Access Request (for registered)

Upon request per GDPR Art. 15 (Right of Access), we provide:

```json
{
  "personal_information": {
    "name": "Anna Andersson",
    "email": "anna@example.com",
    "phone": "+46701234567",
    "role": "CAREGIVER",
    "contract_type": "full_time",
    "start_date": "2024-01-15",
    "home_address": "Storgatan 1, 123 45 Stockholm"
  },
  "employment_data": {
    "organization": "Attendo AB",
    "salary": {
      "monthly": 35000,
      "currency": "SEK"
    },
    "transport_mode": "DRIVING"
  },
  "recent_schedules": [
    {
      "date": "2025-01-15",
      "shift_start": "08:00",
      "shift_end": "16:00",
      "visits_count": 8
    }
  ],
  "audit_trail": [
    {
      "action": "Profile updated",
      "timestamp": "2025-01-10T14:30:00Z",
      "changed_by": "lisa.svensson@attendo.se"
    }
  ]
}
```

**Delivery Format:** JSON, CSV or PDF as requested  
**Response Time:** Within 30 days

---

## 9. Data Protection Principles in Practice

### Principle 1: Lawfulness, Fairness and Transparency

✅ Legal basis documented (Art. 6.1(f))  
✅ Users informed via Privacy Policy  
✅ Clear communication about how data is used

### Principle 2: Purpose Limitation

✅ Data used only for schedule optimization  
❌ No secondary use (marketing, research)

### Principle 3: Data Minimization

✅ Only necessary data collected  
✅ Sensitive health data excluded from pilot

### Principle 4: Accuracy

✅ Validation on import  
✅ Users can update their profile  
✅ Audit trail for changes

### Principle 5: Storage Limitation

✅ Automatic deletion after retention period  
✅ Soft-deletes with possibility to restore

### Principle 6: Integrity and Confidentiality

✅ Encryption (TLS 1.3, AES-256)  
✅ Access control (RBAC, tenant-isolation)  
✅ MFA enforcement

### Principle 7: Accountability

✅ This DPIA documents compliance  
✅ DPA with all sub-processors  
✅ Regular security reviews

---

## 10. Next Steps

- [ ] Review data inventory with Attendo
- [ ] Identify any missing data fields
- [ ] Confirm retention periods
- [ ] Approve legal bases
- [ ] Sign DPA with sub-processors

---

**Summary:** CAIRE primarily processes employee data and basic customer data (name, address, visit times) with low-medium risk level. Sensitive personal data (Art. 9) is **not** processed in pilot. All data stored in EU (AWS Stockholm) with robust security and clear retention policies.
