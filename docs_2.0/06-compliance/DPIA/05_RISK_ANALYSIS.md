# CAIRE Platform - Risk Analysis

**Document:** Detailed risk mapping and measures  
**Version:** 1.0  
**Date:** 2025-12-08  
**Purpose:** Basis for DPIA - identify, assess and manage risks

---

## 1. Risk Assessment Methodology

### 1.1 Risk Matrix

**Probability:**

- **Low (1):** Unlikely to occur (< 5% risk)
- **Medium (2):** May occur (5-25% risk)
- **High (3):** Likely to occur (> 25% risk)

**Consequence:**

- **Low (1):** Limited privacy intrusion, minimal damage
- **Medium (2):** Significant privacy intrusion, some damage
- **High (3):** Serious privacy intrusion, major damage

**Risk Level = Probability × Consequence**

| Risk Level | Score | Action                                         |
| ---------- | ----- | ---------------------------------------------- |
| **Low**    | 1-2   | Acceptable, standard measures                  |
| **Medium** | 3-4   | Requires measures, continuous monitoring       |
| **High**   | 6-9   | Must be addressed before operation, escalation |

---

## 2. Identified Risks

### RISK 1: Unauthorized Access to Employee Data

**Description:** External attacker or internal user gains unauthorized access to employee data (name, salary, contact information). Note: Employee home addresses are NOT stored.

**Probability:** Medium (2) - Cyberattacks are common  
**Consequence:** Medium (2) - Can harm staff privacy and finances  
**Risk Level:** **4 (MEDIUM)**

**Current Measures:**

- ✅ Multi-Factor Authentication (Clerk MFA)
- ✅ Role-Based Access Control (RBAC)
- ✅ Encryption at rest (AES-256)
- ✅ Encryption in transit (TLS 1.3)
- ✅ Tenant-isolation (organization_id filter)
- ✅ Audit logs (90 days retention)
- ✅ Rate limiting on API endpoints
- ✅ Regular security audits

**Remaining Risk:** **Low (2)** - Acceptable with current measures

**Additional Measures (recommended):**

- [ ] Penetration testing before pilot
- [ ] IP-whitelisting for admin users
- [ ] Anomaly detection on logins (e.g. AWS GuardDuty)

---

### RISK 2: Data Leakage from Database

**Description:** SQL injection, misconfiguration or insider threat leads to data leakage from PostgreSQL

**Probability:** Low (1) - Uses ORM (Prisma), professional hosting  
**Consequence:** High (3) - Extensive data can leak  
**Risk Level:** **3 (MEDIUM)**

**Current Measures:**

- ✅ Prisma ORM prevents SQL injection
- ✅ Parameterized queries
- ✅ AWS RDS security groups (restrictive firewall)
- ✅ Encrypted backups
- ✅ Row-Level Security in PostgreSQL
- ✅ Database audit logging
- ✅ Least privilege on DB users

**Remaining Risk:** **Low (1)** - Very low risk

**Additional Measures (recommended):**

- [ ] Database Activity Monitoring (DAM)
- [ ] Quarterly security reviews of DB configuration

---

### RISK 3: Data Leakage during AI Processing (Timefold)

**Description:** Sensitive data sent to Timefold and stored permanently or misused

**Probability:** Low (1) - Timefold receives only anonymized data  
**Consequence:** Medium (2) - Can reveal schedule info  
**Risk Level:** **2 (LOW)**

**Current Measures:**

- ✅ Data minimization - only technical info sent (ID, times, competencies)
- ✅ No names or sensitive info sent
- ✅ No persistent storage at Timefold
- ✅ Data deleted after processing (< 10 min)
- ✅ TLS 1.3 encrypted transport
- ✅ Alternative: Self-hosted Timefold within Attendo's infrastructure

**Remaining Risk:** **Low (1)** - Minimal risk

**Additional Measures (recommended):**

- [ ] DPA with Timefold (if cloud-hosted)
- [ ] Regular audit of what data is sent

---

### RISK 4: Identity Error - Wrong Person Gets Wrong Schema

**Description:** Bugs in system lead to personA receiving personB's schema or data

**Probability:** Low (1) - Tenant-isolation tested  
**Consequence:** Medium (2) - Privacy violation  
**Risk Level:** **2 (LOW)**

**Current Measures:**

- ✅ Tenant-isolation (organization_id on all queries)
- ✅ Automatic tests for tenant-isolation
- ✅ Row-Level Security in PostgreSQL
- ✅ JWT-tokens with organization_id embedded
- ✅ Code reviews for all database queries

**Remaining Risk:** **Low (1)** - Very low risk

**Additional Measures (recommended):**

- [ ] Integration tests for tenant-isolation
- [ ] Quarterly penetration testing

---

### RISK 5: Insider Threat - Caire Staff Misuses Access

**Description:** Caire employee with system access reads or exfiltrates data

**Probability:** Low (1) - Limited staff, NDA agreements  
**Consequence:** High (3) - Extensive data leakage possible  
**Risk Level:** **3 (MEDIUM)**

**Current Measures:**

- ✅ Least privilege principle
- ✅ Audit logs for all access
- ✅ MFA for all Caire users
- ✅ NDA agreements with all employees
- ✅ Quarterly access reviews
- ✅ Immediate revocation upon termination of assignment

**Remaining Risk:** **Low (2)** - Low risk with monitoring

**Additional Measures (recommended):**

- [ ] Background checks for Caire staff
- [ ] Anomaly detection on admin access
- [ ] Mandatory GDPR training for all staff

---

### RISK 6: Phishing/Social Engineering against Attendo Staff

**Description:** Attacker tricks Attendo planners into sharing login credentials

**Probability:** Medium (2) - Phishing is common  
**Consequence:** Medium (2) - Limited access (RBAC), but can affect schedule  
**Risk Level:** **4 (MEDIUM)**

**Current Measures:**

- ✅ MFA required for all users
- ✅ HttpOnly cookies (not accessible via JavaScript)
- ✅ SameSite cookies (CSRF protection)
- ✅ Session timeout (60 min)
- ✅ Audit logs for all logins

**Remaining Risk:** **Medium (3)** - Requires user training

**Additional Measures (MUST):**

- [ ] **Phishing awareness training** for all Attendo users
- [ ] Simulated phishing tests
- [ ] Incident response training

---

### RISK 7: System Outage - Lost Access to Schedules

**Description:** AWS outage, database crash or network problems make system unavailable

**Probability:** Low (1) - AWS has 99.9% uptime  
**Consequence:** Medium (2) - Affects daily operations  
**Risk Level:** **2 (LOW)**

**Current Measures:**

- ✅ AWS Multi-AZ deployment
- ✅ Automated daily backups
- ✅ Point-in-time recovery (7 days)
- ✅ Cross-region backup replication
- ✅ CloudWatch monitoring and alerts
- ✅ On-call engineer 24/7
- ✅ RTO < 4 hours, RPO < 24 hours

**Remaining Risk:** **Low (1)** - Minimal impact

**Additional Measures (recommended):**

- [ ] Disaster recovery drill (annual)
- [ ] Backup export to Attendo's own systems (weekly)

---

### RISK 8: Data Loss during Migration or Update

**Description:** Database migration or system update leads to data loss

**Probability:** Low (1) - Staging environment and tests  
**Consequence:** High (3) - Lost schedules affect operations  
**Risk Level:** **3 (MEDIUM)**

**Current Measures:**

- ✅ Prisma migrations with rollback capability
- ✅ Staging environment for testing
- ✅ Automated backups before each migration
- ✅ Blue-green deployment for zero-downtime
- ✅ CI/CD pipeline with automated tests

**Remaining Risk:** **Low (1)** - Very low risk

**Additional Measures (recommended):**

- [ ] Migration checklist and runbook
- [ ] Post-migration validation tests

---

### RISK 9: Incorrect Data from CSV Upload

**Description:** Incorrect or corrupt data imported from CSV files uploaded by Attendo planners

**Probability:** Medium (2) - Data quality issues are common  
**Consequence:** Low (1) - Validation catches errors  
**Risk Level:** **2 (LOW)**

**Current Measures:**

- ✅ Schema validation on import
- ✅ Data type checks (Prisma ORM)
- ✅ Business rule validation
- ✅ Import logs and error reporting
- ✅ Manual review of first import
- ✅ CSV format validation before processing

**Remaining Risk:** **Low (1)** - Acceptable

**Additional Measures (recommended):**

- [ ] Automated data quality checks
- [ ] Alert on anomalies (e.g. 50% fewer visits than usual)
- [ ] CSV template with validation rules

**Note:** Attendo does NOT use external systems like Carefox or Phoniro. All data is manually prepared and uploaded as CSV files.

---

### RISK 10: AI-Bias - Discriminatory Scheduling

**Description:** Optimization algorithm systematically gives worse schedules to certain staff (e.g. gender, age)

**Probability:** Low (1) - Constraint solver is rule-based, not ML  
**Consequence:** Medium (2) - Can violate discrimination law  
**Risk Level:** **2 (LOW)**

**Current Measures:**

- ✅ Rule-based optimization (not black-box ML)
- ✅ Transparent weights (can be reviewed)
- ✅ Manual review of suggestions before publishing
- ✅ Fairness metrics in solution_metrics (even workload)

**Remaining Risk:** **Low (1)** - Low risk with monitoring

**Additional Measures (recommended):**

- [ ] Monthly fairness audit (compare workload per staff)
- [ ] Feedback function for staff to report injustices

---

## 3. Risk Summary

| Risk ID | Risk                  | Probability | Consequence | Risk (before) | Risk (after) | Status               |
| ------- | --------------------- | ----------- | ----------- | ------------- | ------------ | -------------------- |
| **R1**  | Unauthorized access   | 2           | 2           | 4 (Medium)    | 2 (Low)      | ✅ Acceptable        |
| **R2**  | Data leakage from DB  | 1           | 3           | 3 (Medium)    | 1 (Low)      | ✅ Acceptable        |
| **R3**  | Data leakage at AI    | 1           | 2           | 2 (Low)       | 1 (Low)      | ✅ Acceptable        |
| **R4**  | Identity error        | 1           | 2           | 2 (Low)       | 1 (Low)      | ✅ Acceptable        |
| **R5**  | Insider threat        | 1           | 3           | 3 (Medium)    | 2 (Low)      | ✅ Acceptable        |
| **R6**  | Phishing              | 2           | 2           | 4 (Medium)    | 3 (Medium)   | ⚠️ Requires training |
| **R7**  | System outage         | 1           | 2           | 2 (Low)       | 1 (Low)      | ✅ Acceptable        |
| **R8**  | Data loss migration   | 1           | 3           | 3 (Medium)    | 1 (Low)      | ✅ Acceptable        |
| **R9**  | Incorrect import data | 2           | 1           | 2 (Low)       | 1 (Low)      | ✅ Acceptable        |
| **R10** | AI-bias               | 1           | 2           | 2 (Low)       | 1 (Low)      | ✅ Acceptable        |

**Highest remaining risk:** R6 (Phishing) - Medium (3)  
**Action:** Phishing awareness training before pilot

---

## 4. Risks NOT Identified (but considered)

| Risk                                  | Why NOT identified as risk                   |
| ------------------------------------- | -------------------------------------------- |
| **Health data leaks**                 | ❌ Sensitive health data excluded from pilot |
| **SSN leaks**                         | ❌ SSN not stored (replaced with UUID)       |
| **Transfer to third country**         | ❌ All data within EU/EES                    |
| **Mass processing of sensitive data** | ❌ Limited pilot scope, no Art. 9 data       |
| **Systematic profiling**              | ❌ Only schedule optimization, no profiling  |
| **CCTV/Biometric data**               | ❌ Not applicable to system                  |

---

## 5. Action Plan (Prioritized)

### Before Pilot Start (MUST)

1. **Phishing Awareness Training** for all Attendo users
   - **Responsible:** Attendo IT Security
   - **Deadline:** Before pilot start
   - **Status:** ⏳ Not started

2. **Sign DPA** between Attendo and Caire
   - **Responsible:** Attendo Legal + Caire
   - **Deadline:** Before pilot start
   - **Status:** ⏳ Draft ready

3. **Inform data subjects** (staff and care recipients)
   - **Responsible:** Attendo
   - **Deadline:** Before pilot start
   - **Status:** ⏳ Not started

### During Pilot (RECOMMENDED)

4. **Penetration Testing** of platform
   - **Responsible:** Caire (hire external consultant)
   - **Deadline:** Week 2 of pilot
   - **Status:** ⏳ Planned

5. **Monthly Fairness Audit** of scheduling
   - **Responsible:** Attendo + Caire
   - **Deadline:** Ongoing (monthly)
   - **Status:** ⏳ Planned

6. **Anomaly Detection** on logins (AWS GuardDuty)
   - **Responsible:** Caire DevOps
   - **Deadline:** Week 1 of pilot
   - **Status:** ⏳ Planned

### After Pilot (FUTURE)

7. **Disaster Recovery Drill** (annual)
   - **Responsible:** Caire + Attendo
   - **Deadline:** 6 months after pilot
   - **Status:** ⏳ Planned

8. **Regular Security Audits** (quarterly)
   - **Responsible:** Caire + external consultant
   - **Deadline:** Ongoing
   - **Status:** ⏳ Planned

---

## 6. Continuous Risk Management

### 6.1 Monitoring

**Daily:**

- Automatic alerts on security incidents (CloudWatch, Sentry)
- Monitoring of API errors and anomalies

**Weekly:**

- Review of audit logs (sample)
- Check backup status

**Monthly:**

- Fairness audit (comparison of scheduling)
- Review of new security threats (CVE databases)
- Access review (quarterly for critical roles)

**Quarterly:**

- Full security audit
- DPIA review (if significant changes)
- Penetration testing (after major updates)

### 6.2 Incident Management

**Process:**

1. **Detection:** Automatic alert or manual reporting
2. **Triage:** Assess severity (Sev 1-3)
3. **Response:** Remediate according to runbook
4. **Communication:** Notify Attendo within 4h, data subjects within 72h (if data breach)
5. **Post-mortem:** Document and learn from incident

**Escalation to IMY:** Within 72h if data breach (GDPR Art. 33)

---

## 7. Conclusion

**Overall Risk Level:** **MEDIUM (Acceptable)**

**Justification:**

- 9 of 10 risks are low after measures
- 1 risk is medium (phishing) and addressed with training
- No high risk remains
- Robust security measures implemented
- Data minimization (no Art. 9 data) significantly reduces risk

**Recommendation:** **Approved for pilot** with requirement for phishing training before start.

---

**Next review:** 3 months into pilot or upon significant changes

**Contact:**  
Björn Evers, EirTech AB (Org. No. 559522-3800)  
Tändkulevägen 33, 131 58 Nacka, Sweden  
https://www.eirtech.ai/  
bjorn@caire.se  
+46734177166
