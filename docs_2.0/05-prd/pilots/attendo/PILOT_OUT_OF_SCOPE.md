# Attendo Pilot - Out of Scope

## Overview

This document defines what is **explicitly excluded** from the Attendo pilot scope. The pilot focuses on validating Caire's **Level 2** capabilities (production-ready AI-assisted scheduling) with manual data imports. Future capabilities (Level 3, Level 4) and API integrations are excluded from this pilot.

---

## Automation Levels Excluded

### Level 3 — Auto-Optimize + Approve (Excluded)

**What it is**: Streaming ingestion (absences, urgent visits, traffic) triggers background re-plans. Planners review exception queues instead of re-running jobs.

**Features excluded**:

- EventBridge/Kinesis streaming data ingestion
- Background optimization triggered by events
- Guardrail alerts and automated exception handling
- Vector embeddings for matching
- Approval queues and auto-suggested swaps
- Sub-5-minute latency for intraday reruns

**Why excluded**: Level 3 is planned for Phase 2 (Q2 2026 → Q1 2028) and requires streaming architecture, Feature Store, and closed-loop learning infrastructure that is not part of the current pilot scope.

**Pilot alternative**: Manual optimization runs triggered by planners, with manual approval required for each run.

---

### Level 4 — Fully Adaptive Scheduling (Excluded)

**What it is**: Reinforcement-learning policies and automated retraining keep schedules aligned with continuity targets and demand swings.

**Features excluded**:

- Reinforcement learning (RL) policies for adaptive scheduling
- Ray RLlib integration
- SageMaker Pipelines + Feature Store for automated retraining
- Guardrail automation
- Proactive compliance monitoring
- Continuous telemetry and policy tuning

**Why excluded**: Level 4 is planned for Phase 2 months 18-24 and represents industry-first RL-based home care scheduling capabilities that are still in research/development phase.

**Pilot alternative**: Static constraint-based optimization with manual scenario configuration and approval workflows.

---

## System Integrations Excluded

### API Integration with eCare (Excluded)

**What it is**: Direct API integration with Attendo's eCare system for automated data synchronization.

**Excluded capabilities**:

- Real-time data synchronization via API
- Automated schedule imports from eCare
- Automated export of optimized schedules back to eCare
- Bidirectional data flow between Caire and eCare

**Why excluded**: The pilot focuses on data validation and optimization capabilities, not system integration. API integration requires:

- eCare API access and documentation
- Authentication and security setup
- Data mapping and transformation pipelines
- Error handling and reconciliation workflows
- Ongoing maintenance and support agreements

**Pilot alternative**: All data will be uploaded manually via:

- **CSV files**: Schedule data (unplanned, planned, actuals)
- **JSON files**: Structured data exports from eCare
- **PDF files**: Biståndsbeslut documents for movable visit extraction
- **Excel files**: Additional data formats as needed

---

### API Integration with Other Attendo Systems (Excluded)

**What it is**: Integration with any other Attendo systems (HR systems, payroll, billing, etc.).

**Excluded capabilities**:

- Employee data synchronization
- Payroll integration
- Billing system integration
- HR system integration
- Any other third-party system integrations

**Why excluded**: The pilot scope is limited to scheduling optimization validation. System integrations are production deployment considerations that come after pilot validation.

**Pilot alternative**: All data provided via manual file uploads (CSV, JSON, PDF, Excel).

---

## Future Integrations (Not in Pilot)

### Corti.ai Integration (Future Consideration)

**What it is**: Potential integration with Corti.ai for speech-to-text and clinical documentation automation.

**Potential use cases** (not in pilot):

- **Journals**: Speech-to-text for visit documentation, reducing administrative burden
- **Avvikelserapportering**: Automated incident reporting from voice recordings
- **Kundmöten genomförandeplan**: Voice-to-structured documentation for client meetings and care plan execution

**Why not in pilot**: Corti.ai integration is a strategic partnership consideration for future phases. It requires:

- Corti.ai API access and integration
- Audio recording infrastructure
- Clinical documentation templates
- Privacy and consent workflows
- Pilot validation of core scheduling capabilities must come first

**Future potential**: Once core scheduling is validated, Corti.ai integration could be evaluated as a value-add feature for:

- Reducing documentation time (50-80% reduction potential)
- Improving data quality for optimization (structured notes → optimization constraints)
- Risk detection and escalation workflows
- Revenue cycle management automation

---

## What IS Included in Pilot

### Level 2 — AI-Assisted Proposals (Included)

**What it is**: Constraint-based optimization produces ready-to-publish proposals. Planners review KPIs and approve each run.

**Included features**:

- Manual-triggered optimization
- Scenario lab (pre-configured optimization scenarios)
- Pre-planning with long time horizons (weekly, monthly)
- KPI dashboards and analytics
- Schedule comparison (unplanned vs planned vs optimized vs actuals)
- Movable visits pre-planning
- Slingor import and optimization
- Fine-tuning existing schedules

**Human role**: Trigger runs, compare KPIs, approve publication.

**Business impact expected**: 50%+ less manual scheduling, 15–20% travel reductions, 75–80% utilization, higher continuity, board-ready reporting.

---

### Manual Data Import (Included)

**Supported formats**:

- **CSV**: Schedule data (unplanned, planned, actuals) from eCare exports
- **JSON**: Structured data exports from eCare or other systems
- **PDF**: Biståndsbeslut documents for movable visit template extraction
- **Excel**: Additional data formats as needed

**Import capabilities**:

- Multiple schedule states in single CSV (unplanned, planned, actuals)
- Movable visit templates from biståndsbeslut PDFs
- Employee and client data
- Service area and location data
- Financial data (revenues, costs, transport types)

---

## Summary

| Category                   | Status          | Notes                                       |
| -------------------------- | --------------- | ------------------------------------------- |
| **Level 2 Features**       | ✅ **Included** | Production-ready AI-assisted scheduling     |
| **Level 3 Features**       | ❌ **Excluded** | Streaming, auto-optimize (future phase)     |
| **Level 4 Features**       | ❌ **Excluded** | RL-based adaptive scheduling (future phase) |
| **eCare API Integration**  | ❌ **Excluded** | Manual CSV/JSON uploads only                |
| **Other API Integrations** | ❌ **Excluded** | Manual file uploads only                    |
| **Corti.ai Integration**   | ❌ **Excluded** | Future consideration post-pilot             |
| **Manual Data Import**     | ✅ **Included** | CSV, JSON, PDF, Excel                       |

---

## References

- [Attendo Pilot Plan](./PILOT_PLAN.md) - Main pilot documentation
- [Attendo Data Requirements](./DATA_REQUIREMENTS.md) - Data format specifications
- [CAIRE AI OS Business Roadmap](https://app.caire.se/platform/en/ai-os-business.html) - Level 2, 3, 4 definitions, pwd CAIREROADMAP
