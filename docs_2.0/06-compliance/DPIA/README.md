# Caire Platform - DPIA Documentation

**Data Protection Impact Assessment**

**Version:** 1.0  
**Date:** 2025-12-08  
**Status:** Draft for review with Attendo  
**Document Owner:** EirTech AB (Org. No. 559522-3800)

---

## 📋 Document Overview

This DPIA package contains all documentation required for the pilot project with Attendo and future production.

### Document Structure

| Document                                   | Description                                   | Status   |
| ------------------------------------------ | --------------------------------------------- | -------- |
| **01_SYSTEM_DESCRIPTION.md**               | High-level system architecture and data flow  | ✅ Ready |
| **02_DATA_INVENTORY.md**                   | Detailed mapping of all data                  | ✅ Ready |
| **03_INFORMATION_CLASSIFICATION.md**       | Classification per Attendo's model            | ✅ Ready |
| **04_DPIA_MAIN_DOCUMENT.md**               | Complete DPIA per IMY/EU standard             | ✅ Ready |
| **05_RISK_ANALYSIS.md**                    | Risks, probability, consequences, measures    | ✅ Ready |
| **06_DPA_AGREEMENT_DRAFT.md**              | Data Processing Agreement (DPA)               | ✅ Ready |
| **07_RACI_MATRIX.md**                      | Roles and responsibilities                    | ✅ Ready |
| **08_CONTRACTOR_DATA_ACCESS_AGREEMENT.md** | Contractor data access agreement              | ✅ Ready |
| **09_INTERNAL_DATA_ACCESS_POLICY.md**      | Internal data access & confidentiality policy | ✅ Ready |
| **CONFLUENCE_SETUP_GUIDE.md**              | Guide for setting up DPIA docs in Confluence  | ✅ Ready |

---

## 🎯 Quick Start - Meeting with Attendo

### 1. Read First

- **04_DPIA_MAIN_DOCUMENT.md** - Main document (15 min)
- **05_RISK_ANALYSIS.md** - Risk analysis (10 min)

### 2. Bring to Meeting

- [ ] Printout of 01_SYSTEM_DESCRIPTION.md
- [ ] Architecture diagram (included in system description)
- [ ] 02_DATA_INVENTORY.md (Google Sheet format)
- [ ] 06_DPA_AGREEMENT_DRAFT.md
- [ ] 07_RACI_MATRIX.md
- [ ] Laptop with access to documents

### 3. Key Messages

✅ **Medium risk (acceptable)** - Basic customer data but NO sensitive health data  
✅ **EU-hosting** - AWS RDS Stockholm  
✅ **Modern security** - Clerk MFA, RBAC, encryption  
✅ **Production-ready** - GraphQL architecture with normalized database  
✅ **Data minimization** - Art. 6 data only, excludes Art. 9 (health data)

---

## 📊 Executive Summary

### Purpose of Processing

**Optimize scheduling for home care staff** through AI-driven automation to:

- Reduce manual planning work by 50%+
- Increase care time to 75-80%
- Improve continuity for care recipients

### Personal Data Processed (Pilot)

| Category                              | Scope                                   | Risk             |
| ------------------------------------- | --------------------------------------- | ---------------- |
| **Employee Data**                     | Name, email, phone, schedule, salary    | Medium           |
| **Customer Data (basic)**             | Name, address, visit times, continuity  | Medium           |
| **Schedule Data**                     | Work hours, assignments, routes         | Low              |
| **System Logs**                       | API calls, authentication               | Low              |
| **❌ Sensitive Health Data (Art. 9)** | Diagnoses, medications, care plans, SSN | **NOT INCLUDED** |

### Legal Basis

**Article 6.1(f) GDPR** - Legitimate interest (basic personal data)  
**Article 28 GDPR** - Data Processing Agreement (Caire as processor)  
**❌ NOT Art. 9** - Sensitive health data excluded from pilot

### Risk Level: MEDIUM (Acceptable) ✅

With implemented security measures and **data minimization** (no sensitive health data per Art. 9), the risk is assessed as **acceptable** for pilot.

**Important distinction:**

- ✅ **Includes:** Basic customer data (name, address, visit times) - regular personal data per Art. 6
- ❌ **Excludes:** Sensitive health data (diagnoses, medications, care plans) - per Art. 9

---

## 🔒 Security Measures (Summary)

| Area               | Measure                       | Status |
| ------------------ | ----------------------------- | ------ |
| **Encryption**     | TLS 1.3, AES-256 at rest      | ✅     |
| **Authentication** | Clerk MFA/SSO, JWT-tokens     | ✅     |
| **Access**         | RBAC, tenant-isolation        | ✅     |
| **Backup**         | Automated daily, 7d retention | ✅     |
| **Logging**        | Audit trail, 90d retention    | ✅     |
| **Hosting**        | AWS Stockholm (EU)            | ✅     |

---

## 🚀 Caire Architecture

### Enhanced Security & Compliance

Caire maintains and enhances all existing security measures while introducing:

- **GraphQL API Layer:** Unified API with improved access control and query optimization
- **Enhanced Audit Trail:** Comprehensive logging of all data access and optimization decisions
- **Improved Multi-tenancy:** Database-level tenant isolation in the new v2.0 schema
- **Advanced Caching:** Secure caching layer with tenant-aware data isolation
- **Microservices Architecture:** Modular design enabling independent security hardening per service

### Data Model Improvements (v2.0)

The new normalized schema provides:

- **Better Data Integrity:** Foreign key constraints and referential integrity at the database level
- **Enhanced Audit Capabilities:** Built-in revision system for all schedule changes
- **Improved Data Minimization:** More granular control over what data is stored and processed
- **Slingor Support:** Native support for recurring patterns reducing data duplication

### Compliance Continuity

All GDPR and AI Act compliance measures from v1.0 will be preserved and enhanced in v2.0:

- ✅ Same data minimization principles (no Art. 9 health data)
- ✅ Same EU hosting (AWS Stockholm)
- ✅ Enhanced audit capabilities for compliance reporting
- ✅ Improved data access controls with GraphQL field-level permissions

**Migration Impact:** The migration to Caire is seamless with zero data loss and maintained compliance posture throughout the transition.

---

## 📍 Route Optimization & Employee Addresses

**Important:** EirTech AB does **not** store or process employee home addresses for route optimization.

- ❌ Employee home addresses are **not stored** in Caire
- ❌ Employee home addresses are **not used** for routing
- ✅ Route optimization uses **office locations** as the start and end point for all employees

This data minimization approach reduces privacy risk while maintaining full optimization functionality.

---

## 🔄 Timefold Data Retention & Revision Logic

**Data Handling:**

- EirTech AB does **not delete** optimization datasets stored in Timefold
- This is required to enable **revisions** on existing Timefold data assets
- Revisions are executed by providing a timestamp parameter for the relevant dataset ID
- Raw JSON files can be fetched from Timefold when needed

**System of Record:**

- Timefold is the **system of record** for optimization input/output data
- EirTech AB does **not process** Timefold JSON files internally
- Caire queries Timefold's stored assets and revision capabilities directly
- No secondary copies are processed or transformed within Caire systems

---

## 👥 EirTech AB Team Structure

**Legal Entity:** EirTech AB (Org. No. 559522-3800)  
**Product/Platform:** Caire

### Current Team Roles:

| Role                                        | Name             | Responsibilities                                           |
| ------------------------------------------- | ---------------- | ---------------------------------------------------------- |
| **CEO**                                     | Björn Evers      | Overall responsibility for GDPR, security, data governance |
| **Home Care Domain Expert**                 | Sverker Carlsson | Validation of operational correctness, domain expertise    |
| **Architect & Senior Full-Stack Developer** | [Name]           | System architecture, debugging, optimization               |

### Incoming Team Members:

- 1-2 additional developers (full-stack and front-end) to support pilot execution

**Note:** All internal personnel with access to production data are bound by the Internal Data Access & Confidentiality Policy (see 09_INTERNAL_DATA_ACCESS_POLICY.md). External contractors are bound by the Contractor Data Access Agreement (see 08_CONTRACTOR_DATA_ACCESS_AGREEMENT.md).

---

## 📝 Using the Documents

### For Caire Team

1. **Before meeting:** Read through all documents, note questions
2. **During meeting:** Use documents as basis for discussion
3. **After meeting:** Update based on Attendo's feedback

### For Attendo

1. **Review** documentation before workshop
2. **Confirm** that basic customer data (name, address, visit times) is acceptable
3. **Approve** that sensitive health data (diagnoses, medications) is excluded from pilot
4. **Identify** any gaps or additions needed
5. **Approve** or provide feedback on DPIA

### For Legal Review

All documents are structured according to:

- GDPR Art. 35 (DPIA requirements)
- IMY's guidance on DPIA
- EU AI Act (low-risk classification)

---

## 🔄 Document History

| Version | Date       | Change                                                | Author     |
| ------- | ---------- | ----------------------------------------------------- | ---------- |
| 1.0     | 2025-12-08 | Initial version - Complete DPIA documentation package | EirTech AB |

---

## 📞 Contact

**Questions about DPIA:**  
Björn Evers (CEO)  
EirTech AB (Org. No. 559522-3800)  
Tändkulevägen 33, 131 58 Nacka, Sweden  
https://www.eirtech.ai/  
https://www.caire.se/
bjorn@caire.se  
+46734177166

**Note:** Björn Evers acts in his capacity as CEO and authorized representative of EirTech AB. Although ownership is held through BE Ventures AB, all personal data access is performed by Björn Evers personally under the authority of EirTech AB. BE Ventures AB does not process personal data.

**Technical questions:**  
See 01_SYSTEM_DESCRIPTION.md for technical contact

---

## ⚖️ Legal Status

**This is a working document** to be completed together with Attendo during the DPIA workshop.

**Next steps:**

1. ✅ Share documentation with Attendo
2. ⏳ Book DPIA workshop (half-day/full-day)
3. ⏳ Conduct workshop and finalize DPIA
4. ⏳ Formal approval from both parties
5. ⏳ Sign Data Processing Agreement

---

## 💡 Key Message to Attendo

> **"The Caire pilot processes basic employee data and customer data (name, address, visit times) classified as regular personal data per Art. 6. Sensitive health data (Art. 9) such as diagnoses, medications, and detailed care plans are completely excluded from the pilot to minimize risk and simplify the DPIA process. The system works fully for schedule optimization with this data minimization."**

---

**Confidential** - Only for EirTech AB and Attendo
