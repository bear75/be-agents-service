# CAIRE Platform - DPIA Main Document

**Data Protection Impact Assessment per GDPR Art. 35**

**Version:** 1.0  
**Date:** 2025-12-08  
**Status:** Draft for review with Attendo  
**Data Controller:** Attendo AB  
**Data Processor:** EirTech AB (Org. No. 559522-3800)

---

## 1. Description of Processing

### 1.1 Purpose of Processing

**Main Purpose:** Automated schedule optimization for home care staff

**Specific Goals:**

- Optimize staff schedules to maximize care time (75-80%)
- Minimize travel time and distances (up to 20% reduction)
- Ensure continuity between staff and care recipients
- Reduce manual planning work by 50%+
- Improve working conditions for home care staff

**Scope (Pilot):**

- **Time Period:** 8-12 weeks pilot
- **Number of Care Recipients:** 50-200 (depending on Attendo's pilot scope)
- **Number of Staff:** 20-50 employees
- **Geographic Area:** One or several service areas within Attendo
- **Type of Processing:** Schedule optimization via AI/constraint solver

### 1.2 Categories of Data Subjects

| Category            | Number (pilot) | Description                            |
| ------------------- | -------------- | -------------------------------------- |
| **Staff**           | 20-50          | Care staff performing home care visits |
| **Care Recipients** | 50-200         | Customers receiving home care          |
| **Planners**        | 2-5            | Attendo employees using the system     |
| **Administrators**  | 1-2            | IT staff with system access            |

### 1.3 Categories of Personal Data

#### ✅ Included in Pilot (Art. 6 - Regular Personal Data)

**Employee Data:**

- Identity information: name, employment number
- Contact information: email, phone
- Employment information: role, contract type, start/end dates, salary
- Work-related: schedule, shifts, competencies, transport mode
- Preferences: desired work times, continuity preferences
- **Note on competencies:** Employee competencies and certifications (e.g., "nurse qualification", "lifting certification", "driving license") are personal data per Art. 6.1(f) but are **not** sensitive personal data (Art. 9). These are necessary for matching staff to appropriate visits and ensuring safety and quality of care.

**Customer Data (basic):**

- Identity information: name, external ID (NOT SSN)
- Contact information: address, phone, port code
- Service-related: visit times, duration, number of staff required
- Continuity: preference for specific staff
- Geographic: address for route planning
- **Service requirements (non-sensitive):** Required competencies or skills needed for specific visits (e.g., "needs lifting certification", "requires nurse qualification", "two-person visit", "requires driving license", "requires Swedish language"). These are treated as **service requirements** and do not reveal health diagnoses or sensitive personal data. Stored as technical/competence-based labels, not medical causes. No Art. 9 data is stored. Legal basis: Art. 6.1(f) - Legitimate interest.

**Schedule Data:**

- Time planning: start/end times for visits and shifts
- Routes: planned travel paths between visits
- Assignments: link staff ↔ visits
- Costs: calculated staff cost per schedule

**System Data:**

- User logs: logins, actions, changes
- Technical metadata: IP addresses, sessions, API calls
- Audit trail: who did what, when

#### ❌ Excluded from Pilot (Art. 9 - Sensitive Personal Data)

**Sensitive Health Data:**

- ❌ Diagnoses and diseases
- ❌ Medications and dosages
- ❌ Detailed care plans and treatment instructions
- ❌ Disabilities and health conditions
- ❌ Sensitive comments ("dementia", "incontinence", etc.)

**Other Sensitive Information:**

- ❌ SSN (replaced with UUID)
- ❌ Pictures/photos of care recipients
- ❌ Ethnic background
- ❌ Religion or political views
- ❌ Sexual orientation

**Justification for Exclusion:** Data minimization per GDPR Art. 5.1(c) - only data necessary for schedule optimization is included. Sensitive health data requires special legal basis per Art. 9 and is excluded to reduce risk in pilot.

### 1.4 Storage Periods

| Data Type                      | Storage Period                   | Justification                    |
| ------------------------------ | -------------------------------- | -------------------------------- |
| **Employee Data (active)**     | During employment                | Ongoing processing               |
| **Employee Data (terminated)** | +1 year after termination        | History, rehire possibility      |
| **Salary Information**         | +7 years after termination       | Accounting law, tax authority    |
| **Customer Data (active)**     | During care relationship         | Ongoing processing               |
| **Customer Data (terminated)** | +1 year after termination        | History, quality assurance       |
| **Schedule History**           | 2 years                          | Quality assurance, analysis      |
| **Audit Logs**                 | 90 days                          | Security, incident investigation |
| **API Logs**                   | 30 days                          | Performance monitoring           |
| **Backups**                    | 7 days (daily), 4 weeks (weekly) | Disaster recovery                |

**Automatic Deletion:** System automatically deletes data after retention period (soft-delete → hard-delete).

---

## 2. Necessity and Proportionality

### 2.1 Necessity

**Is processing necessary to achieve the purpose?**

✅ **YES** - Schedule optimization is impossible without:

- Employee data: Identification of who is available, competencies. Route optimization uses office/depot locations (not employee home addresses) as start/end points.
- Customer data: Identification of who should be visited, where, when
- Schedule data: Technical data for optimization algorithm

**Can the purpose be achieved with less intrusion?**

✅ **YES - Data minimization applied:**

- Excludes sensitive health data (Art. 9) from pilot
- Uses UUID instead of SSN
- Anonymizes data during AI processing (Timefold)
- Geo-coordinates with max 100m precision (not exact GPS)
- Only technical info sent to optimization engine

### 2.2 Proportionality

**Balance between interest and privacy:**

| Factor                    | Attendo's Interest               | Individual's Privacy                           | Assessment                          |
| ------------------------- | -------------------------------- | ---------------------------------------------- | ----------------------------------- |
| **Employee Data**         | Necessary for scheduling         | Medium intrusion (normal employer information) | ✅ Proportionate                    |
| **Customer Data (basic)** | Necessary for route planning     | Medium intrusion (not sensitive health data)   | ✅ Proportionate                    |
| **Sensitive Health Data** | ❌ NOT necessary for pilot       | High intrusion                                 | ❌ **NOT proportionate - EXCLUDED** |
| **Salary Information**    | Necessary for cost calculation   | Medium intrusion (restricted access)           | ✅ Proportionate                    |
| **Geo-Position**          | Necessary for route optimization | Low intrusion (only address, not tracking)     | ✅ Proportionate                    |

**Conclusion:** Processing is **proportionate** as only necessary data is collected and sensitive health data is excluded.

### 2.3 Alternative Solutions

**Evaluated Alternatives:**

| Alternative                           | Assessment                                       | Why Not Chosen                          |
| ------------------------------------- | ------------------------------------------------ | --------------------------------------- |
| **Manual Scheduling**                 | ❌ Time-consuming, inefficient                   | Does not fulfill automation purpose     |
| **Anonymized Data**                   | ❌ Impossible to schedule without identification | Technically unfeasible                  |
| **Only Staff ID (no names)**          | ⚠️ Technically possible                          | Makes work harder for planners, poor UX |
| **Include All Health Data**           | ❌ Disproportionately high intrusion             | Overkill for schedule optimization      |
| **Current Solution (minimized data)** | ✅ Optimal balance                               | **CHOSEN**                              |

**Conclusion:** Chosen solution provides best balance between functionality and privacy protection.

---

## 3. Legal Basis and GDPR Relationship

### 3.1 Legal Basis (Art. 6.1 GDPR)

**Primary Basis: Art. 6.1(f) - Legitimate Interest**

**Legitimate Interests:**

- **Attendo:** Efficient staff planning, cost optimization, quality assurance
- **Staff:** Better working conditions, reduced stress, optimized routes
- **Care Recipients:** Continuity, reliable service

**Interest Balancing:**

- Interest in efficient home care outweighs limited privacy intrusion
- Only regular personal data (Art. 6) processed
- Sensitive health data (Art. 9) excluded from pilot

**Secondary Basis: Art. 6.1(c) - Legal Obligation**

For certain data (salary data, employment info):

- Accounting law (7 years storage of salary data)
- Work environment law (employer's obligation to document work hours)

**❌ NOT Art. 9 - Sensitive Personal Data:**
Pilot does NOT process sensitive health data, therefore no Art. 9 basis required.

### 3.2 Roles per GDPR

**Data Controller:** Attendo AB

- Determines purpose and means of processing
- Responsible towards data subjects (staff and care recipients)
- Makes decisions about which data is processed

**Data Processor:** EirTech AB (Org. No. 559522-3800)

- Processes personal data on behalf of Attendo
- Follows instructions from Attendo
- Technical platform and system provider

**Sub-Processors:**

- **Clerk Inc** (Authentication, MFA, user management)
- **AWS** (Infrastructure, database, hosting)
- **Timefold** (AI optimization engine - temporary processing)

### 3.3 Data Processing Agreement (DPA)

**Status:**

- ✅ Draft DPA between Attendo and Caire (see 06_DPA_AGREEMENT_DRAFT.md)
- ✅ DPA signed with Clerk (SOC 2 Type II certified)
- ✅ AWS Data Processing Addendum (standard AWS DPA)
- ⏳ DPA with Timefold (can be skipped if self-hosted)

**Requirements in DPA:**

- Caire processes data only according to Attendo's instructions
- Security measures per Art. 32 GDPR
- Processor assists with data subject access requests (Art. 15)
- Processor deletes data upon termination of assignment
- Sub-processors require approval from Attendo

---

## 4. Rights of Data Subjects

### 4.1 Information to Data Subjects (Art. 13-14)

**Staff and care recipients informed via:**

- Privacy Policy on CAIRE platform
- Privacy information from Attendo (as data controller)
- Onboarding documents at pilot start

**Information includes:**

- Which data is processed (employee data, customer data)
- Purpose (schedule optimization)
- Legal basis (Art. 6.1(f))
- Storage periods (see 1.4)
- Recipients of data (Caire, AWS, Clerk, Timefold)
- Rights (access, rectification, erasure, objection)

### 4.2 Right of Access (Art. 15)

**Process:**

1. Data subject requests data export from Attendo
2. Attendo contacts Caire for technical export
3. Caire delivers data within 30 days
4. Attendo reviews and delivers to data subject

**Delivery Format:** JSON, CSV or PDF as requested

**Content:** All personal data stored about the individual (see example in 02_DATA_INVENTORY.md)

### 4.3 Right to Rectification (Art. 16)

**Process:**

- Data subject contacts Attendo
- Attendo updates data in CAIRE system
- Changes logged in audit trail

**Response Time:** Within 30 days

### 4.4 Right to Erasure (Art. 17 - "Right to be Forgotten")

**Possible when:**

- Data no longer needed for the purpose
- Data subject withdraws consent (not relevant here - no consent basis)
- Data subject objects to processing (Art. 21)
- Data processed unlawfully

**Limitations:**

- Accounting law requires 7 years storage of salary data
- Work environment law requires documentation of work hours
- Legal obligations take precedence over right to erasure

**Implementation:** Soft-delete (marked as deleted_at) → Hard-delete after retention period

### 4.5 Right to Data Portability (Art. 20)

**Applicable:** Yes, for data based on consent or contract

**Delivery:** JSON or CSV format with structured data

### 4.6 Right to Object (Art. 21)

**Applicable:** Yes, as legal basis is Art. 6.1(f) (legitimate interest)

**Process:**

1. Data subject objects to processing
2. Attendo assesses if compelling legitimate grounds exist
3. If no → processing stops
4. If yes → processing continues (e.g. legal obligation)

**Example:** Staff can object to processing of their data → Attendo assesses if the objection can be accommodated while maintaining optimization functionality. Note: Employee home addresses are not stored; route optimization uses office/depot locations instead.

---

## 5. Security Measures (Art. 32 GDPR)

### 5.1 Technical Measures

**Encryption:**

- ✅ TLS 1.3 for all transport (HTTPS, WSS)
- ✅ AES-256 encryption at rest (AWS RDS)
- ✅ Encrypted backups (AWS S3)
- ✅ Secure WebSocket for real-time updates

**Access Control:**

- ✅ Multi-Factor Authentication (Clerk MFA)
- ✅ Role-Based Access Control (Admin, Scheduler, Viewer)
- ✅ JWT-tokens with 60 min TTL
- ✅ Tenant-isolation (organization_id filter on all queries)
- ✅ Row-Level Security in PostgreSQL

**Logging and Monitoring:**

- ✅ Audit trail for all CRUD operations
- ✅ IP address and user logged
- ✅ Automatic alerts on anomalies (CloudWatch, Sentry)
- ✅ Retention: 90 days for audit logs, 30 days for API logs

**Backup and Disaster Recovery:**

- ✅ Automated daily backups (AWS RDS)
- ✅ Point-in-time recovery up to 7 days
- ✅ Cross-region replication (Stockholm → Frankfurt)
- ✅ RTO < 4 hours, RPO < 24 hours

**Network Security:**

- ✅ HTTPS enforced (HSTS headers)
- ✅ CSRF protection via SameSite cookies
- ✅ HttpOnly cookies (not accessible via JavaScript)
- ✅ Rate limiting on API endpoints
- ✅ DDoS protection via AWS Shield

### 5.2 Organizational Measures

**Access Management:**

- ✅ Least privilege principle (minimal necessary access)
- ✅ Quarterly access reviews
- ✅ Immediate revocation upon termination of assignment
- ✅ MFA enforcement for all users

**Security Training:**

- ✅ GDPR training for all users
- ✅ Data classification training (Open, Internal, Restricted, Confidential)
- ✅ Phishing awareness training
- ✅ Secure coding practices for developers

**Incident Management:**

- ✅ Incident response plan documented
- ✅ On-call engineer 24/7
- ✅ Data breach notification within 72h (GDPR Art. 33)
- ✅ Post-mortem after each incident

**Vendor Management:**

- ✅ DPA with all sub-processors
- ✅ Annual review of sub-processors
- ✅ SOC 2 / ISO 27001 requirements for critical vendors

### 5.3 Pseudonymization and Anonymization

**Pseudonymization:**

- ✅ SSN replaced with UUID
- ✅ External IDs used instead of internal
- ✅ Geo-coordinates truncated to 100m precision

**Anonymization during AI Processing:**

- ✅ Timefold receives only technical info (ID, competencies, times)
- ✅ No names or sensitive info sent to optimization engine
- ✅ No persistent storage at Timefold

---

## 6. Transfers to Third Countries

### 6.1 Status

**❌ NO transfers outside EU/EES**

All data stored and processed within EU:

- ✅ AWS RDS: Stockholm (eu-north-1)
- ✅ AWS EC2: Stockholm (eu-north-1)
- ✅ Clerk Auth: Frankfurt (EU-region)
- ✅ Timefold: EU (or self-hosted within Attendo's infrastructure)

### 6.2 On Future Transfers

If transfers become necessary in the future, requires:

- Standard Contractual Clauses (SCC) per EU Commission
- Transfer Impact Assessment (TIA)
- Technical measures (encryption, pseudonymization)

**Current Status:** NOT APPLICABLE for pilot

---

## 7. Consultation and Approval

### 7.1 Consultation with Data Protection Officer (DPO)

**Status:** ⏳ Ongoing

**Attendo's DPO should review:**

- [ ] This DPIA
- [ ] Risk Analysis (05_RISK_ANALYSIS.md)
- [ ] Data Processing Agreement (06_DPA_AGREEMENT_DRAFT.md)
- [ ] Security measures

**DPO's Assessment:** [To be filled in after review]

### 7.2 Consultation with Data Subjects (if applicable)

**Art. 36.4 GDPR:** Consultation with data subjects when appropriate

**For pilot:**

- ⏳ Information to staff via intranet/email
- ⏳ Information to care recipients via letter/phone call
- ⏳ Opportunity to ask questions and provide feedback
- ⏳ Right to object per Art. 21 informed

### 7.3 Consultation with Supervisory Authority (IMY)

**Art. 36.1 GDPR:** Consultation with IMY required only if high risk remains after measures

**Assessment for CAIRE:**

✅ **NOT NECESSARY** - Risk is medium and acceptable after measures

**Justification:**

- No sensitive health data (Art. 9) in pilot
- Robust security measures implemented
- Data minimization applied
- Limited pilot scope

**On future changes:** If sensitive health data is included, IMY consultation may become necessary.

---

## 8. Conclusion and Approval

### 8.1 Summary Assessment

**Are risks acceptable?**

✅ **YES** - With implemented measures, risks are acceptable

**Justification:**

1. **Data Minimization:** Only necessary data, no sensitive health data (Art. 9)
2. **Robust Security Measures:** Encryption, RBAC, MFA, audit logs, tenant-isolation
3. **EU-Hosting:** All data within EU/EES, no transfers to third countries
4. **Transparency:** Clear information to data subjects, easy to exercise rights
5. **Limited Pilot:** Controlled scope, can be adjusted before full production

### 8.2 Measures Before Production

**Must be done before pilot starts:**

- [ ] Sign DPA between Attendo and Caire
- [ ] Inform staff and care recipients (Privacy Notice)
- [ ] Configure RBAC and user roles
- [ ] Test backup/restore process
- [ ] Conduct security training for planners

**Recommended before pilot:**

- [ ] Penetration testing of platform
- [ ] Load testing to verify performance
- [ ] Dry-run with test data

### 8.3 Follow-up and Review

**Continuous Monitoring:**

- Monthly review of security alerts
- Quarterly access review
- Incident reporting within 72h

**DPIA Update Required When:**

- Inclusion of sensitive health data (Art. 9)
- Significant change in system architecture
- New sub-processors in third countries
- Changed legal basis
- Significant security incident

**Next Review:** 6 months after pilot start

### 8.4 Approval

**This document should be approved by:**

| Role                                  | Name        | Date   | Signature   |
| ------------------------------------- | ----------- | ------ | ----------- |
| **Data Controller (Attendo)**         | [Name]      | [Date] | [Signature] |
| **Data Protection Officer (Attendo)** | [Name]      | [Date] | [Signature] |
| **Data Processor (EirTech AB)**       | Björn Evers | [Date] | [Signature] |
| **IT Security Manager (Attendo)**     | [Name]      | [Date] | [Signature] |

---

## Appendices

1. **01_SYSTEM_DESCRIPTION.md** - Detailed technical architecture
2. **02_DATA_INVENTORY.md** - Complete list of all processed data
3. **03_INFORMATION_CLASSIFICATION.md** - Classification per Attendo's model
4. **05_RISK_ANALYSIS.md** - Detailed risk assessment with measures
5. **06_DPA_AGREEMENT_DRAFT.md** - Data Processing Agreement
6. **07_RACI_MATRIX.md** - Roles and responsibilities

---

**Document Validity:** This document is valid from approval date until 6 months thereafter, or until significant changes require new DPIA.

**Contact for Questions:**  
Björn Evers, EirTech AB (Org. No. 559522-3800)  
Tändkulevägen 33, 131 58 Nacka, Sweden  
https://www.eirtech.ai/  
bjorn@caire.se  
+46734177166
