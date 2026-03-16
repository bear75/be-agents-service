# Data Processing Agreement (DPA)

**Between Attendo AB (Data Controller) and EirTech AB (Data Processor)**

**Version:** 1.0  
**Date:** 2025-12-08  
**Status:** Draft for review

---

## Parties

**DATA CONTROLLER ("Customer")**  
Attendo AB  
Organization Number: [XXXXX-XXXX]  
Address: [Address]  
Contact Person: [Name]  
Email: [Email]

**DATA PROCESSOR ("Processor")**  
EirTech AB  
Organization Number: 559522-3800  
Address: Tändkulevägen 33, 131 58 Nacka, Sweden  
Website: https://www.eirtech.ai/  
Contact Person: Björn Evers  
Email: bjorn@caire.se  
Phone: +46734177166

---

## 1. Background and Purpose

1.1 Processor provides AI-driven schedule optimization service ("Service") to Customer for home care operations.

1.2 In connection with the Service, Processor will process personal data on behalf of Customer.

1.3 This agreement regulates Processor's processing of personal data per GDPR (EU 2016/679) and supplements the main agreement between the parties.

---

## 2. Scope of Processing

### 2.1 Purpose

Processor shall only process personal data for the following purposes:

a) **Schedule Optimization** - Optimize staff schedules for home care  
b) **Route Planning** - Calculate efficient routes between visits  
c) **Cost Calculation** - Estimate staff costs for schedules  
d) **Reporting** - Provide analytics and KPIs  
e) **System Operations** - Maintenance, support and security monitoring

### 2.2 Categories of Data Subjects

- Staff employed by Customer (20-50 persons in pilot)
- Care recipients of Customer (50-200 persons in pilot)
- Administrators and planners of Customer (2-5 persons)

### 2.3 Categories of Personal Data

**Employee Data:**

- Identity information: name, employment number
- Contact information: email, phone
- Employment information: role, contract type, salary, work hours
- Competencies and certifications (e.g., "nurse qualification", "lifting certification", "driving license") - These are personal data per Art. 6.1(f) but are **not** sensitive personal data (Art. 9). Necessary for matching staff to appropriate visits and ensuring safety and quality of care.

**Customer Data (basic, NOT sensitive personal data Art. 9):**

- Identity information: name, external ID (NOT SSN)
- Contact information: address, phone
- Service-related: visit times, continuity preferences
- **Service requirements (non-sensitive):** Required competencies or skills needed for specific visits (e.g., "needs lifting certification", "requires nurse qualification", "two-person visit", "requires driving license"). These do **not** contain or imply health diagnoses and are not classified as sensitive personal data per GDPR Art. 9. Stored as technical/competence-based labels (service requirements), not medical causes. Legal basis: Art. 6.1(f) - Legitimate interest.

**System Data:**

- User logs: logins, actions
- Technical metadata: IP addresses, sessions

**❌ EXCEPTION - NOT INCLUDED:**
Sensitive personal data per GDPR Art. 9 (health data, diagnoses, medications, care plans) is NOT included in this processing for pilot phase.

### 2.4 Duration of Processing

From: [Agreement Start]  
To: [Agreement Termination] + 30 days (for data deletion)

---

## 3. Processor's Obligations

### 3.1 Instructions from Customer

Processor undertakes to:

a) Process personal data only according to Customer's written instructions (this agreement constitutes such instructions)  
b) Immediately inform Customer if instructions conflict with GDPR or other data protection legislation  
c) Not process personal data for own purposes  
d) Not sell or otherwise commercialize personal data

### 3.2 Confidentiality

Processor ensures that:

a) Only authorized staff have access to personal data  
b) All staff have signed confidentiality agreements  
c) Staff are trained in GDPR and data protection  
d) Access is granted according to "least privilege" principle

### 3.3 Security (Art. 32 GDPR)

**Technical Measures:**

- **Encryption:**
  - TLS 1.3 for all transport
  - AES-256 encryption at rest (AWS RDS)
  - Encrypted backups

- **Access Control:**
  - Multi-Factor Authentication (MFA)
  - Role-Based Access Control (RBAC)
  - JWT-tokens with 60 min TTL
  - Tenant-isolation (organization_id on all queries)

- **Logging:**
  - Audit logs for all CRUD operations
  - 90 days retention
  - Automatic security alerts

- **Backup:**
  - Automated daily backups (AWS RDS)
  - Point-in-time recovery up to 7 days
  - Cross-region replication

**Organizational Measures:**

- Quarterly access reviews
- Incident management plan
- Regular security audits
- Background checks for staff with data access

### 3.4 Sub-Processors

**Approved Sub-Processors:**

| Sub-Processor                 | Service                     | Country                | Security                   |
| ----------------------------- | --------------------------- | ---------------------- | -------------------------- |
| **Amazon Web Services (AWS)** | Infrastructure, database    | 🇸🇪 Sweden (eu-north-1) | ISO 27001, SOC 2, GDPR DPA |
| **Clerk Inc**                 | Authentication, MFA         | 🇩🇪 Germany (EU)        | SOC 2 Type II, GDPR DPA    |
| **Timefold**                  | AI optimization (temporary) | 🇪🇺 EU or self-hosted   | No persistent storage      |

**Process for New Sub-Processors:**

a) Processor must obtain Customer's written approval before engaging new sub-processor  
b) Notification 30 days in advance  
c) Customer has right to object within 14 days  
d) Processor ensures sub-processor meets same security requirements as Processor

**Responsibility:**
Processor is fully responsible for sub-processors' processing of personal data.

---

## 4. Customer's Rights and Processor's Assistance

### 4.1 Data Subject Access Request (Art. 15)

Upon request from data subject, Processor shall within **30 days** provide:

- All data stored about the individual
- Format: JSON, CSV or PDF as requested
- Free of charge for first request

### 4.2 Rectification and Erasure (Art. 16-17)

Processor shall upon Customer's instruction:

- Correct inaccurate data within 30 days
- Erase data (soft-delete immediately, hard-delete per retention policy)
- Confirm action to Customer

### 4.3 Restriction and Objection (Art. 18-21)

Processor shall technically enable:

- Restriction of processing (flag data as "restricted")
- Stop processing upon objection
- Data portability (export in structured format)

### 4.4 Assistance with DPIA and Supervisory Authority Control

Processor shall:

- Provide information for DPIA execution
- Participate in supervisory control from IMY or other authority
- Answer questions from Customer within 5 business days

---

## 5. Data Storage and Transfer

### 5.1 Storage Location

All data stored within **EU/EES**:

- Primary: AWS RDS Stockholm (eu-north-1)
- Backup: AWS Frankfurt (eu-central-1)
- **❌ NO data stored outside EU/EES**

### 5.2 Transfer to Third Country

**Status:** Not applicable for pilot

**If future need:** Requires Standard Contractual Clauses (SCC) and Customer approval

---

## 6. Personal Data Incident (Data Breach)

### 6.1 Notification to Customer

Upon personal data incident, Processor shall **immediately** (within 4 hours) inform Customer about:

a) Type of incident  
b) Affected categories and number of data subjects  
c) Likely consequences  
d) Measures taken and planned

### 6.2 Documentation

Processor shall document all personal data incidents and provide documentation to Customer upon request.

### 6.3 Responsibility

Customer is responsible for notification to IMY (within 72h per GDPR Art. 33) and to data subjects (if high risk, Art. 34).

Processor assists with information for notification.

---

## 7. Audit and Control

### 7.1 Customer's Audit Right

Customer has right to:

a) Perform audits of Processor's security measures (with 14 days notice)  
b) Request documentation (security policies, incident reports, etc.)  
c) Hire external auditor (Processor has right to require confidentiality agreement)

Cost: Customer bears own costs. Processor may charge for extensive audits (max 1 per year free of charge).

### 7.2 Processor's Self-Audit

Processor conducts annually:

- Internal security audit
- Penetration testing
- SOC 2 / ISO 27001 review (recommended)

Reports provided to Customer upon request.

---

## 8. Agreement Termination

### 8.1 Deletion or Return of Data

Upon agreement termination, Processor shall within **30 days**:

a) **Delete** all personal data (including backups), OR  
b) **Return** data to Customer in structured format (JSON/CSV)

Customer chooses alternative upon termination.

### 8.2 Exception

Data that must be stored per law (e.g. accounting law, 7 years) may be retained but isolated and used only for legally required purpose.

### 8.3 Confirmation

Processor shall confirm in writing that deletion is completed.

---

## 9. Liability and Damages

### 9.1 Processor's Liability

Processor is liable for damages caused by:

- Violation of GDPR
- Violation of instructions from Customer
- Failure to take appropriate security measures

### 9.2 Limitation of Liability

Processor's liability for damages is limited to **[AMOUNT]** per incident and **[AMOUNT]** total per year.

**Exception:** No limitation in case of gross negligence or intent.

### 9.3 Insurance

Processor shall have valid liability insurance covering personal data incidents.

---

## 10. Agreement Validity and Changes

### 10.1 Validity Period

This agreement is valid from signing date and as long as Processor processes personal data on behalf of Customer.

### 10.2 Agreement Changes

Changes require written agreement between parties.

Processor may propose changes upon:

- Changes in GDPR or other legislation
- New security threats
- Technical changes

### 10.3 Termination

Upon material breach, Customer has right to terminate agreement with immediate effect.

---

## 11. Other

### 11.1 Applicable Law

Swedish law.

### 11.2 Dispute Resolution

Disputes shall be resolved through negotiation. If not possible, dispute is decided by Swedish general court.

### 11.3 GDPR Compliance

Both parties undertake to follow GDPR and Swedish data protection legislation.

---

## 12. Signatures

**For Customer (Data Controller):**

Name: \***\*\*\*\*\*\*\***\_\_\_\***\*\*\*\*\*\*\***  
Title: \***\*\*\*\*\*\*\***\_\_\_\***\*\*\*\*\*\*\***  
Date: \***\*\*\*\*\*\*\***\_\_\_\***\*\*\*\*\*\*\***  
Signature: \***\*\*\*\*\*\*\***\_\_\_\***\*\*\*\*\*\*\***

**For Processor (Data Processor):**

Name: Björn Evers  
Title: CEO, EirTech AB (Org. No. 559522-3800)  
Date: \***\*\*\*\*\*\*\***\_\_\_\***\*\*\*\*\*\*\***  
Signature: \***\*\*\*\*\*\*\***\_\_\_\***\*\*\*\*\*\*\***

---

## Appendix A: Technical and Organizational Security (Art. 32)

### Technical Measures

| Measure                   | Implementation                       | Status |
| ------------------------- | ------------------------------------ | ------ |
| **Encryption in transit** | TLS 1.3, HTTPS enforced              | ✅     |
| **Encryption at rest**    | AES-256 (AWS RDS)                    | ✅     |
| **Authentication**        | Clerk MFA, JWT-tokens                | ✅     |
| **Access Control**        | RBAC (Admin, Scheduler, Viewer)      | ✅     |
| **Tenant-isolation**      | organization_id filter               | ✅     |
| **Audit logging**         | 90 days retention                    | ✅     |
| **Backup**                | Daily automated, 7d retention        | ✅     |
| **Network security**      | HSTS, CSRF protection, rate limiting | ✅     |

### Organizational Measures

| Measure                 | Implementation                     | Status |
| ----------------------- | ---------------------------------- | ------ |
| **Access Management**   | Least privilege, quarterly reviews | ✅     |
| **Security Training**   | GDPR training, phishing awareness  | ✅     |
| **Incident Management** | 24/7 on-call, 4h response          | ✅     |
| **Background Checks**   | For staff with data access         | ✅     |
| **NDA Agreements**      | All employees                      | ✅     |

---

## Appendix B: Approved Sub-Processors

### 1. Amazon Web Services (AWS)

**Service:** Infrastructure, database, hosting  
**Region:** Stockholm (eu-north-1)  
**DPA:** AWS Data Processing Addendum (standard)  
**Certifications:** ISO 27001, SOC 2, GDPR-compliant  
**Data Processed:** All data (database, backups, logs)

### 2. Clerk Inc

**Service:** Authentication, MFA, user management  
**Region:** Frankfurt, Germany (EU)  
**DPA:** Clerk Data Processing Addendum  
**Certifications:** SOC 2 Type II, GDPR-compliant  
**Data Processed:** Email, name, password hash, sessions

### 3. Timefold

**Service:** AI optimization engine  
**Region:** EU (or self-hosted)  
**DPA:** [Required if cloud-hosted]  
**Storage:** ❌ No persistent storage (temporary processing < 10 min)  
**Data Processed:** Anonymized technical info (ID, times, competencies)

---

**This is a DRAFT. Legal review required before signing.**

**Contact:**  
Björn Evers, EirTech AB (Org. No. 559522-3800)  
Tändkulevägen 33, 131 58 Nacka, Sweden  
https://www.eirtech.ai/  
bjorn@caire.se  
+46734177166
