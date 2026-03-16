# CAIRE Platform - Information Classification

**Document:** Data classification per Attendo's model  
**Version:** 1.0  
**Date:** 2025-12-08  
**Purpose:** Basis for DPIA - classify all data according to risk level

---

## 1. Classification Model

CAIRE uses a four-level classification model that is standard in Swedish public sector and large care providers:

| Classification   | Definition                 | Examples                                | Measures                                    |
| ---------------- | -------------------------- | --------------------------------------- | ------------------------------------------- |
| **Open**         | Can be shared publicly     | Product info, general documentation     | No special requirements                     |
| **Internal**     | For internal use           | System logs, technical metadata         | Standard access control                     |
| **Restricted**   | Confidential business info | Employee data, schedules, customer data | Encryption, RBAC, audit logs                |
| **Confidential** | Sensitive personal info    | Health data, SSN, sensitive comments    | **AVOIDED IN PILOT**, requires Art. 9 basis |

---

## 2. Information Classification per Data Type

### 2.1 EMPLOYEE DATA

| Data Field                   | Classification | Justification                                                                                                      | Measures                                   |
| ---------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------ |
| **Name**                     | **Restricted** | Identifies individual, but not sensitive                                                                           | Encryption at rest, RBAC, tenant-isolation |
| **Email**                    | **Restricted** | Contact info, can be used for phishing                                                                             | Encryption, MFA on access                  |
| **Phone**                    | **Restricted** | Contact info                                                                                                       | Encryption, RBAC                           |
| **Office/Depot Location**    | **Restricted** | Used for route optimization (start/end points) - employee home addresses are NOT stored                            | Encryption, restricted access              |
| **Salary (monthly, hourly)** | **Restricted** | Business-sensitive economic info                                                                                   | Encryption, Admin/Finance role only        |
| **Employment Info**          | **Restricted** | Contract, start/end dates                                                                                          | RBAC, audit logs                           |
| **Competencies**             | **Restricted** | Personal data (Art. 6.1(f)) - necessary for matching staff to visits, but **not** sensitive personal data (Art. 9) | RBAC, encryption                           |
| **Work Schedule**            | **Restricted** | Can reveal routines                                                                                                | RBAC, tenant-isolation                     |

**Summary:** Employee data is classified as **Restricted** - contains personal information requiring protection but not sensitive personal data per GDPR Art. 9. Employee competencies (e.g., "nurse qualification", "lifting certification", "driving license") are personal data per Art. 6.1(f) but are **not** sensitive personal data (Art. 9). They are necessary for matching staff to appropriate visits and ensuring safety and quality of care.

---

### 2.2 CUSTOMER DATA (CARE RECIPIENTS) - BASIC

| Data Field                   | Classification | Justification                                                                                                   | Measures                     |
| ---------------------------- | -------------- | --------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| **Name**                     | **Restricted** | Identifies care recipient                                                                                       | Encryption, RBAC, audit logs |
| **Address**                  | **Restricted** | Necessary for route planning                                                                                    | Encryption, tenant-isolation |
| **Visit Times**              | **Restricted** | Can reveal routines, but normal in home care                                                                    | RBAC, audit logs             |
| **Continuity Preference**    | **Restricted** | "Anna prefers staff Lisa" - relational info                                                                     | RBAC                         |
| **Visit Duration**           | **Internal**   | Technical planning data                                                                                         | Standard access              |
| **Number of Staff Required** | **Internal**   | Technical planning data                                                                                         | Standard access              |
| **Municipality ID**          | **Internal**   | External reference                                                                                              | Standard access              |
| **Port Code**                | **Restricted** | Access information                                                                                              | Encryption                   |
| **Mobile Number**            | **Restricted** | Contact info                                                                                                    | Encryption, RBAC             |
| **Service Requirements**     | **Restricted** | Required competencies (e.g., "needs lifting certification", "requires nurse qualification", "two-person visit") | Encryption, RBAC             |

**Summary:** Basic customer data is classified as **Restricted** - regular personal data per GDPR Art. 6. **NOT sensitive personal data per Art. 9.**

**Important:** This is **NOT** health data - it is only logistical information necessary for scheduling. Service requirements are stored as technical/competence-based labels (e.g., "needs lifting certification", "requires nurse qualification"), not as medical causes or diagnoses. They do **not** reveal health diagnoses and are therefore **not** sensitive personal data per Art. 9.

---

### 2.3 SENSITIVE HEALTH DATA (Art. 9) - ❌ EXCLUDED FROM PILOT

| Data Field             | Classification   | Status in Pilot     | Why Excluded                             |
| ---------------------- | ---------------- | ------------------- | ---------------------------------------- |
| **Diagnoses**          | **Confidential** | ❌ **NOT INCLUDED** | Art. 9 - requires special legal basis    |
| **Medications**        | **Confidential** | ❌ **NOT INCLUDED** | Art. 9 - sensitive health data           |
| **Care Plans**         | **Confidential** | ❌ **NOT INCLUDED** | Art. 9 - detailed health info            |
| **SSN**                | **Confidential** | ❌ **NOT INCLUDED** | High-risk identifier, replaced with UUID |
| **Sensitive Comments** | **Confidential** | ❌ **NOT INCLUDED** | "Dementia", "incontinence" etc - Art. 9  |
| **Disabilities**       | **Confidential** | ❌ **NOT INCLUDED** | Art. 9 - health-related                  |

**Data Minimization Strategy:** Pilot runs **WITHOUT** sensitive health data to simplify DPIA and reduce risk.

---

### 2.4 SCHEDULE DATA

| Data Field               | Classification | Justification                      | Measures                |
| ------------------------ | -------------- | ---------------------------------- | ----------------------- |
| **Schedule Date**        | **Internal**   | Technical planning data            | Standard access         |
| **Schedule Name**        | **Internal**   | Descriptive info                   | Standard access         |
| **Schedule Status**      | **Internal**   | Workflow status                    | Standard access         |
| **Optimization Results** | **Restricted** | Can contain links staff ↔ customer | RBAC, audit logs        |
| **Route Information**    | **Restricted** | Shows staff movements              | RBAC                    |
| **Cost Calculations**    | **Restricted** | Business-sensitive economic info   | Admin/Finance role only |

**Summary:** Schedule data is primarily **Internal** or **Restricted** depending on whether it can be traced to individuals.

---

### 2.5 SYSTEM LOGS & METADATA

| Data Field             | Classification | Justification                        | Measures                      |
| ---------------------- | -------------- | ------------------------------------ | ----------------------------- |
| **Audit Logs**         | **Restricted** | Contains users, actions, changes     | 90 days retention, encryption |
| **API Logs**           | **Internal**   | Performance monitoring               | 30 days retention             |
| **Error Logs**         | **Internal**   | Troubleshooting (sanitized - no PII) | 30 days retention             |
| **IP Addresses**       | **Internal**   | Security, audit                      | Anonymized after 90 days      |
| **User-Agents**        | **Internal**   | Browser info                         | Truncated                     |
| **Session Tokens**     | **Restricted** | Authentication                       | HttpOnly, Secure, 60 min TTL  |
| **CloudWatch Metrics** | **Internal**   | Aggregated performance data          | Standard retention            |

**Summary:** System logs are primarily **Internal** with exception of audit logs which are **Restricted** due to person linkage.

---

### 2.6 AI PROCESSING (Timefold)

| Data Field               | Classification | Storage           | Justification                                 |
| ------------------------ | -------------- | ----------------- | --------------------------------------------- |
| **Anonymized Dataset**   | **Internal**   | ❌ Not persistent | Only technical info (ID, competencies, times) |
| **Geo-Coordinates**      | **Internal**   | ❌ Not persistent | Anonymized positions (no address)             |
| **Optimization Results** | **Restricted** | ✅ AWS RDS        | Contains links staff ↔ visits                 |
| **Dataset ID Reference** | **Internal**   | ✅ AWS RDS        | Only UUID reference                           |

**Summary:** AI processing uses **anonymized and minimized data**. Timefold never receives names or sensitive info.

---

## 3. Summary per Classification

### Classification Distribution

| Classification            | Number of Data Types | Percentage | Risk             |
| ------------------------- | -------------------- | ---------- | ---------------- |
| **Open**                  | 0                    | 0%         | None             |
| **Internal**              | 15                   | 30%        | Low              |
| **Restricted**            | 35                   | 70%        | Medium           |
| **Confidential (Art. 9)** | 0 (excluded)         | 0%         | **Not in pilot** |

**Observation:** Majority of data is classified as **Restricted**, which is normal for staff scheduling. **No Confidential-classified data in pilot.**

---

## 4. Measures per Classification

### Restricted Data (Majority of data)

**Technical Measures:**

- ✅ Encryption at rest (AES-256) via AWS RDS
- ✅ Encryption in transit (TLS 1.3) on all API calls
- ✅ Row-Level Security via `organization_id` filter
- ✅ RBAC - only authorized roles get access
- ✅ Audit logs for all CRUD operations

**Organizational Measures:**

- ✅ Access reviews (quarterly)
- ✅ Data classification training for all users
- ✅ Incident response plan
- ✅ Regular security audits

### Internal Data

**Technical Measures:**

- ✅ Standard access control (authentication required)
- ✅ Tenant-isolation
- ✅ Basic logging

**Organizational Measures:**

- ✅ Standard access policies
- ✅ Regular backups

---

## 5. Data Minimization - Practical Application

### ✅ What We DO include (necessary for function)

**Employee Data:**

- Name, email, phone (identification, communication)
- Employment info (contract, times, competencies)
- Office/depot location (route optimization start/end point - employee home addresses are NOT stored)
- Salary info (cost calculation, invoicing)

**Customer Data:**

- Name, address (identification, route planning)
- Visit times, duration (scheduling)
- Continuity preferences (quality assurance)
- Contact info (communication when needed)

**Schedule Data:**

- Times, routes, assignments (core functionality)
- Cost calculations (economic follow-up)

### ❌ What We DO NOT include (data minimization)

**Sensitive Health Data (Art. 9):**

- ❌ Diagnoses and disease history
- ❌ Medications and dosages
- ❌ Care plans and treatment instructions
- ❌ Disabilities
- ❌ Sensitive comments ("dementia", "incontinence")

**Other Sensitive Information:**

- ❌ SSN (replaced with UUID)
- ❌ Pictures/photos of care recipients
- ❌ Family relations (if not necessary)
- ❌ Economic situation of care recipients

**Justification:** System works fully for schedule optimization without sensitive health data.

---

## 6. Comparison Table: Pilot vs Full Production

| Data Type                          | Pilot (Phase 1)       | Full Production (Phase 2+)                      |
| ---------------------------------- | --------------------- | ----------------------------------------------- |
| **Employee Data**                  | ✅ Included           | ✅ Included                                     |
| **Customer Data - basic**          | ✅ Included           | ✅ Included                                     |
| **Sensitive Health Data (Art. 9)** | ❌ **NOT included**   | ⚠️ Can be included with extended DPIA           |
| **SSN**                            | ❌ Replaced with UUID | ⚠️ Can be included with enhanced security       |
| **Care Plans/Documents**           | ❌ Not included       | ⚠️ Can be included with document classification |

**Upgrade Path:** If Attendo wants to include sensitive health data after pilot, requires:

1. Extended DPIA with Art. 9 analysis
2. Enhanced technical measures (pseudonymization, more access levels)
3. Legal basis per Art. 9.2 (likely 9.2(h) - health care)
4. Possible data protection impact assessment (DPIA) from IMY

---

## 7. Special Considerations

### 7.1 Continuity Information

**Data:** "Anna Larsson prefers staff Lisa Svensson"

**Classification:** Restricted  
**Justification:** Not health data, but relational preference that is normal in home care context  
**Legal Basis:** Art. 6.1(f) - Legitimate interest (quality assurance)

### 7.2 Geo-Coordinates and Route Information

**Data:** Latitude/Longitude for visit addresses and office/depot locations

**Classification:** Restricted  
**Justification:** Necessary for route optimization. Employee home addresses are NOT stored - only office/depot locations are used as start/end points.  
**Measures:**

- Precision max 100m (not exact GPS point)
- Only planners with need can see location data
- Anonymized during AI processing (only coordinates, no address)

### 7.3 Economic Information (Salaries, Costs)

**Data:** Monthly salary, hourly salary, total costs per schedule

**Classification:** Restricted  
**Justification:** Business-sensitive info, not sensitive personal data per GDPR  
**Measures:**

- Only Admin and Finance roles can see salaries
- Aggregated data (total costs) can be shown to Scheduler
- Audit logs for all access to economic data

---

## 8. Recommendations for Attendo

### Approve the following classification:

- [ ] **Employee Data:** Restricted ✅
- [ ] **Customer Data (basic):** Restricted ✅
- [ ] **Sensitive Health Data:** Confidential - ❌ **NOT in pilot**
- [ ] **System Logs:** Internal ✅
- [ ] **AI Processing:** Internal (anonymized) ✅

### Confirm data minimization:

- [ ] Pilot runs **WITHOUT** sensitive health data (Art. 9)
- [ ] Only basic customer data included (name, address, visit times)
- [ ] SSN replaced with UUID
- [ ] Detailed care plans excluded

### Security Requirements for Restricted data:

- [ ] Encryption at rest and in transit
- [ ] RBAC with at least 3 role levels (Admin, Scheduler, Viewer)
- [ ] Audit logs with 90 days retention
- [ ] Tenant-isolation (organization_id on all queries)
- [ ] MFA for all users

---

## 9. Classification Checklist

When adding new data field, use this checklist:

```
1. Is it sensitive personal data per Art. 9? (health, ethnicity, religion)
   → YES: Classification = Confidential, requires special legal basis
   → NO: Go to step 2

2. Can it identify an individual?
   → YES: Classification = at least Restricted, go to step 3
   → NO: Classification = Internal, implement standard access

3. Is it necessary for core functionality?
   → NO: Consider NOT collecting (data minimization)
   → YES: Go to step 4

4. What risk does leakage entail?
   → HIGH (economic damage, privacy violation): Classification = Restricted
   → LOW (not sensitive): Classification = Internal

5. Implement measures according to classification
```

---

## 10. Summary

**Classification Model:** Four-level (Open, Internal, Restricted, Confidential)

**Pilot Profile:**

- 70% Restricted data (employee data, basic customer data, schedules)
- 30% Internal data (system logs, metadata)
- 0% Confidential data (sensitive health data excluded)

**Risk Level:** MEDIUM - with implemented security measures acceptable for pilot

**Key Message to Attendo:**

> "The CAIRE pilot processes basic employee data and customer data (name, address, visit times) classified as **Restricted** per regular personal data (Art. 6). Sensitive health data (Art. 9) such as diagnoses, medications, and care plans **are completely excluded from pilot** to minimize risk and simplify the DPIA process. The system works fully for schedule optimization with this data minimization."

---

**Next Steps:**

1. Attendo reviews and approves classification model
2. Confirms that Restricted classification is acceptable for pilot
3. Signs that sensitive health data (Confidential) is excluded from pilot
