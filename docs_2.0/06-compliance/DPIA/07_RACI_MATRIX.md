# CAIRE Platform - RACI Matrix

**Document:** Roles and Responsibilities for GDPR Compliance  
**Version:** 1.0  
**Date:** 2025-12-08  
**Purpose:** Clarify who is Responsible, Accountable, Consulted and Informed

---

## 1. RACI Model

**R** = **Responsible** (Execution) - Does the work  
**A** = **Accountable** (Accountable) - Ultimately responsible, decision maker (only ONE per activity)  
**C** = **Consulted** (Consulted) - Provides input, two-way communication  
**I** = **Informed** (Informed) - Kept informed, one-way communication

---

## 2. Roles

### Attendo (Data Controller)

| Role                              | Responsibility                             |
| --------------------------------- | ------------------------------------------ |
| **Business Manager**              | Overall responsibility for pilot project   |
| **IT Security Manager**           | Security architecture, incident management |
| **Data Protection Officer (DPO)** | GDPR compliance, legal advice              |
| **Planner**                       | Daily use of system                        |
| **HR Manager**                    | Employee data, consents                    |

### EirTech (Data Processor)

| Role                      | Responsibility                      |
| ------------------------- | ----------------------------------- |
| **CEO / Project Manager** | Overall responsibility for delivery |
| **Tech Lead**             | Technical architecture, security    |
| **DevOps Engineer**       | Infrastructure, backup, monitoring  |
| **Backend Developer**     | API, database, integration          |
| **Frontend Developer**    | UI, user experience                 |
| **Support Engineer**      | User support, bug fixes             |

---

## 3. RACI Matrix - GDPR Activities

### 3.1 BEFORE PILOT

| Activity                                 | Attendo Business Manager | Attendo IT Security | Attendo DPO | Caire CEO | Caire Tech Lead | Caire DevOps |
| ---------------------------------------- | ------------------------ | ------------------- | ----------- | --------- | --------------- | ------------ |
| **Conduct DPIA**                         | A                        | C                   | R           | C         | C               | I            |
| **Approve DPIA**                         | A                        | C                   | C           | I         | I               | I            |
| **Sign DPA (Data Processing Agreement)** | A                        | I                   | C           | A         | I               | I            |
| **Inform Staff**                         | R                        | I                   | C           | I         | I               | I            |
| **Inform Care Recipients**               | R                        | I                   | C           | I         | I               | I            |
| **Configure RBAC**                       | I                        | C                   | I           | A         | R               | R            |
| **Security Training (Attendo)**          | A                        | R                   | C           | I         | I               | I            |
| **Phishing Awareness Training**          | A                        | R                   | I           | I         | I               | I            |
| **Penetration Testing**                  | I                        | C                   | I           | A         | R               | R            |
| **Backup Test**                          | I                        | C                   | I           | A         | I               | R            |

### 3.2 DURING PILOT

| Activity                                  | Attendo Business Manager | Attendo IT Security | Attendo DPO | Attendo Planner | EirTech CEO | EirTech Tech Lead | EirTech Support |
| ----------------------------------------- | ------------------------ | ------------------- | ----------- | --------------- | ----------- | ----------------- | --------------- |
| **Daily Use**                             | I                        | I                   | I           | **R**           | I           | I                 | C               |
| **Data Subject Access Request (Art. 15)** | A                        | I                   | C           | I               | I           | R                 | R               |
| **Data Rectification (Art. 16)**          | A                        | I                   | C           | R               | I           | I                 | C               |
| **Data Erasure (Art. 17)**                | A                        | C                   | C           | I               | I           | R                 | R               |
| **Security Monitoring**                   | I                        | C                   | I           | I               | A           | R                 | I               |
| **Incident Management**                   | A                        | R                   | C           | I               | R           | R                 | C               |
| **Data Breach Notification**              | A                        | R                   | C           | I               | R           | C                 | I               |
| **Monthly Security Report**               | I                        | A                   | C           | I               | I           | R                 | I               |
| **User Support**                          | I                        | I                   | I           | C               | I           | C                 | **R**           |
| **Bug Fixes**                             | I                        | I                   | I           | C               | A           | R                 | C               |

### 3.3 AFTER PILOT

| Activity                                   | Attendo Business Manager | Attendo IT Security | Attendo DPO | EirTech CEO | EirTech Tech Lead |
| ------------------------------------------ | ------------------------ | ------------------- | ----------- | ----------- | ----------------- |
| **Evaluate Pilot**                         | A                        | C                   | C           | R           | R                 |
| **Update DPIA (if necessary)**             | A                        | C                   | R           | I           | I                 |
| **Decision on Full Production**            | A                        | C                   | C           | I           | I                 |
| **Delete Pilot Data (if no continuation)** | A                        | I                   | C           | I           | R                 |
| **Return Data (upon termination)**         | A                        | C                   | C           | I           | R                 |
| **Archive DPIA Documentation**             | A                        | I                   | R           | I           | I                 |

---

## 4. RACI Matrix - Technical Activities

### 4.1 Infrastructure & Security

| Activity                          | Attendo IT Security | EirTech DevOps | EirTech Tech Lead |
| --------------------------------- | ------------------- | -------------- | ----------------- |
| **AWS Configuration**             | C                   | **R**          | A                 |
| **Database Setup (RDS)**          | C                   | **R**          | A                 |
| **Backup Configuration**          | C                   | **R**          | A                 |
| **Monitoring Setup (CloudWatch)** | C                   | **R**          | A                 |
| **SSL Certificates**              | I                   | **R**          | A                 |
| **Firewall Rules**                | C                   | **R**          | A                 |
| **MFA Enforcement**               | C                   | **R**          | A                 |
| **Audit Logging Setup**           | C                   | **R**          | A                 |

### 4.2 Development & Deployment

| Activity                     | EirTech CEO | EirTech Tech Lead | EirTech Backend | EirTech Frontend | EirTech DevOps |
| ---------------------------- | ----------- | ----------------- | --------------- | ---------------- | -------------- |
| **API Development**          | I           | A                 | **R**           | I                | I              |
| **UI Development**           | I           | A                 | I               | **R**            | I              |
| **CSV Upload Integration**   | C           | A                 | **R**           | I                | I              |
| **Database Migrations**      | I           | A                 | **R**           | I                | C              |
| **CI/CD Pipeline**           | I           | A                 | C               | C                | **R**          |
| **Deployment to Staging**    | I           | A                 | C               | C                | **R**          |
| **Deployment to Production** | A           | C                 | C               | C                | **R**          |
| **Code Reviews**             | I           | **R**             | C               | C                | I              |

### 4.3 Support & Maintenance

| Activity                     | Attendo Planner | EirTech Support | EirTech Backend | EirTech Frontend | EirTech DevOps |
| ---------------------------- | --------------- | --------------- | --------------- | ---------------- | -------------- |
| **User Support (Level 1)**   | I               | **R**           | I               | I                | I              |
| **Bug Investigation**        | I               | **R**           | C               | C                | C              |
| **Hotfixes**                 | I               | A               | **R**           | **R**            | **R**          |
| **Performance Optimization** | I               | C               | **R**           | **R**            | A              |
| **Security Patches**         | I               | I               | C               | C                | **R**          |

---

## 5. Escalation Matrix - Incidents

### Severity 1: Data Breach, System Down

| Step                                                | Time       | Responsible                  | Contact               |
| --------------------------------------------------- | ---------- | ---------------------------- | --------------------- |
| **1. Detection**                                    | 0 min      | Caire DevOps                 | Automatic alert       |
| **2. Triage**                                       | < 15 min   | Caire Tech Lead              | On-call engineer      |
| **3. Notification to Attendo**                      | < 4 hours  | Caire CEO                    | Attendo IT Security   |
| **4. Notification to DPO**                          | < 4 hours  | Attendo IT Security          | Attendo DPO           |
| **5. Notification to IMY (if breach)**              | < 72 hours | Attendo DPO                  | IMY                   |
| **6. Notification to Data Subjects (if high risk)** | < 72 hours | Attendo Business Manager     | Staff/Care Recipients |
| **7. Post-mortem**                                  | < 7 days   | Caire Tech Lead + Attendo IT | Documentation         |

### Severity 2: Degraded Performance, Security Issue

| Step                           | Time      | Responsible            | Contact                   |
| ------------------------------ | --------- | ---------------------- | ------------------------- |
| **1. Detection**               | 0 min     | Caire DevOps           | Automatic alert           |
| **2. Triage**                  | < 30 min  | Caire Tech Lead        | On-call engineer          |
| **3. Notification to Attendo** | < 4 hours | Caire Support          | Attendo Planner           |
| **4. Resolution**              | < 4 hours | Caire Backend/Frontend | Attendo IT (if necessary) |
| **5. Post-mortem**             | < 14 days | Caire Tech Lead        | Documentation             |

### Severity 3: Minor Bug, UX Issue

| Step          | Time         | Responsible            | Contact                        |
| ------------- | ------------ | ---------------------- | ------------------------------ |
| **1. Report** | -            | Attendo Planner        | Caire Support                  |
| **2. Triage** | < 2 hours    | Caire Support          | Caire Tech Lead                |
| **3. Fix**    | < 24 hours   | Caire Backend/Frontend | -                              |
| **4. Deploy** | Next release | Caire DevOps           | Attendo Planner (notification) |

---

## 6. Communication Matrix

### Regular Meetings

| Meeting             | Frequency     | Participants (R=Required, O=Optional)                                                             | Purpose                      |
| ------------------- | ------------- | ------------------------------------------------------------------------------------------------- | ---------------------------- |
| **Pilot Kickoff**   | Once          | Attendo Business Manager (R), Attendo IT (R), Attendo DPO (R), Caire CEO (R), Caire Tech Lead (R) | Start pilot, DPIA overview   |
| **Weekly Status**   | Weekly        | Attendo Planner (R), Caire Support (R), Caire Tech Lead (O)                                       | Status, issues, feedback     |
| **Monthly Review**  | Monthly       | Attendo Business Manager (R), Attendo IT (R), Caire CEO (R), Caire Tech Lead (R)                  | KPIs, security, next steps   |
| **Incident Review** | After Sev 1-2 | Attendo IT (R), Attendo DPO (O), Caire CEO (R), Caire Tech Lead (R)                               | Post-mortem, lessons learned |
| **DPIA Review**     | Quarterly     | Attendo DPO (R), Attendo IT (R), Caire CEO (R)                                                    | Update DPIA upon changes     |

### Escalation Contacts

| Role                            | Primary Contact  | Email            | Phone        | Availability               |
| ------------------------------- | ---------------- | ---------------- | ------------ | -------------------------- |
| **Attendo Business Manager**    | [Name]           | [Email]          | [Tel]        | Business hours             |
| **Attendo IT Security Manager** | [Name]           | [Email]          | [Tel]        | 24/7 (incident)            |
| **Attendo DPO**                 | [Name]           | [Email]          | [Tel]        | Business hours             |
| **EirTech CEO**                 | Björn Evers      | bjorn@caire.se   | +46734177166 | 24/7 (incident)            |
| **EirTech Tech Lead**           | [Name]           | [Email]          | [Tel]        | 24/7 (on-call)             |
| **EirTech Support**             | support@caire.se | support@caire.se | [Tel]        | Business hours (+ on-call) |

---

## 7. Decision Matrix

| Decision                          | Decision Maker (Accountable) | Must Consult                         | Can Consult     |
| --------------------------------- | ---------------------------- | ------------------------------------ | --------------- |
| **Start Pilot**                   | Attendo Business Manager     | Attendo DPO, Attendo IT              | Caire CEO       |
| **Stop Pilot (security reasons)** | Attendo DPO                  | Attendo IT Security                  | Caire CEO       |
| **Change Data Scope**             | Attendo DPO                  | Attendo Business Manager, Attendo IT | Caire Tech Lead |
| **Add Sub-Processor**             | Attendo DPO                  | Attendo IT Security                  | Caire CEO       |
| **Deployment to Production**      | Caire Tech Lead              | Caire DevOps                         | Attendo IT      |
| **Emergency Rollback**            | Caire Tech Lead              | Attendo IT (notification)            | -               |
| **Proceed to Full Production**    | Attendo Business Manager     | Attendo DPO, Attendo IT, Caire CEO   | -               |

---

## 8. Summary - Key Personnel

### Attendo (Data Controller)

| Role                    | Main Responsibility              | Critical Activities                       |
| ----------------------- | -------------------------------- | ----------------------------------------- |
| **Business Manager**    | Overall project responsibility   | Approve DPIA, decide on continuation      |
| **IT Security Manager** | Security and incident management | Security monitoring, incident response    |
| **DPO**                 | GDPR compliance                  | Review DPIA, IMY notification upon breach |
| **Planner**             | Daily use                        | Feedback, report problems                 |

### EirTech (Data Processor)

| Role          | Main Responsibility                 | Critical Activities                         |
| ------------- | ----------------------------------- | ------------------------------------------- |
| **CEO**       | Delivery and customer relations     | Sign DPA, escalation, decisions             |
| **Tech Lead** | Technical architecture and security | DPIA input, code reviews, incident response |
| **DevOps**    | Infrastructure and operations       | AWS setup, backup, monitoring, deployment   |
| **Support**   | User support                        | Daily support, bug reporting                |

---

## 9. Checklist - Who Does What Before Pilot?

| Activity                   | Responsible                          | Deadline     | Status |
| -------------------------- | ------------------------------------ | ------------ | ------ |
| [ ] Conduct DPIA           | Attendo DPO                          | Before pilot | ⏳     |
| [ ] Approve DPIA           | Attendo Business Manager             | Before pilot | ⏳     |
| [ ] Sign DPA               | Attendo Business Manager + Caire CEO | Before pilot | ⏳     |
| [ ] Inform Staff           | Attendo Business Manager             | Before pilot | ⏳     |
| [ ] Inform Care Recipients | Attendo Business Manager             | Before pilot | ⏳     |
| [ ] Phishing Training      | Attendo IT Security                  | Before pilot | ⏳     |
| [ ] Configure RBAC         | Caire DevOps                         | Before pilot | ⏳     |
| [ ] Penetration Test       | Caire Tech Lead                      | Week 1 pilot | ⏳     |
| [ ] Backup Test            | Caire DevOps                         | Before pilot | ⏳     |

---

**This document should be updated if roles or responsibilities change.**

**Contact:**  
Björn Evers, EirTech AB (Org. No. 559522-3800)  
Tändkulevägen 33, 131 58 Nacka, Sweden  
https://www.eirtech.ai/  
bjorn@caire.se  
+46734177166
