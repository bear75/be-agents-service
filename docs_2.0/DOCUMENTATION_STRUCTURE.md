# Documentation Structure Guide

**Purpose**: Clarify what goes where in the docs_2.0 structure

---

## The Problem

Currently we have:

- **05-prd/**: Product Requirements Documents (what features should do)
- **09-scheduling/**: Technical documentation (how scheduling works)

But there's overlap and confusion about what belongs where.

---

## Clear Separation: PRD vs Technical Docs

### PRD (Product Requirements) - `05-prd/`

**Purpose**: Define **WHAT** features should do, **WHY** they're needed, and **WHO** will use them.

**Contains**:

- ✅ Feature requirements (user stories, acceptance criteria)
- ✅ Business value and objectives
- ✅ User personas and use cases
- ✅ Success metrics and KPIs
- ✅ Visual designs and mockups
- ✅ **General** pilot plans (if applicable to multiple features)

**Audience**: Product managers, stakeholders, designers, business analysts

**Example**: "Users should be able to drag-and-drop visits to reassign them. This reduces planning time by 50%."

### Technical Documentation - `09-scheduling/`

**Purpose**: Define **HOW** the system works, **HOW** to implement it, and **HOW** to integrate with it.

**Contains**:

- ✅ Architecture and system design
- ✅ API specifications and integration guides
- ✅ Implementation guides (how to build features)
- ✅ Data models and schemas
- ✅ Technical guides (pinned visits, planning windows, etc.)
- ✅ **Feature-specific** pilot plans (scheduling pilots go here)

**Audience**: Developers, architects, technical leads

**Example**: "Use GraphQL mutation `updateSchedule` with `pinningRequested: true` to pin visits. See `BACKEND_ARCHITECTURE.md` for details."

---

## Current Structure Analysis

### What's in `05-prd/` (Should be PRDs)

| File                                     | Current Content                              | Should Be                       |
| ---------------------------------------- | -------------------------------------------- | ------------------------------- |
| `prd-umbrella.md`                        | ✅ Product vision                            | ✅ Keep (PRD)                   |
| `Feature PRD – Bryntum Calendar View.md` | ✅ Feature requirements                      | ✅ Keep (PRD)                   |
| `BRYNTUM_FROM_SCRATCH_PRD.md`            | ✅ Feature PRD (greenfield build)            | ✅ Keep (PRD)                   |
| `BRYNTUM_BACKEND_SPEC.md`                | ❌ **Technical spec** (API specs, data flow) | ⚠️ **Move to `09-scheduling/`** |
| `PREPLANNING_BACKEND_ANALYSIS.md`        | ❌ **Technical analysis**                    | ⚠️ **Move to `09-scheduling/`** |
| `PREPLANNING_FRONTEND_IMPLEMENTATION.md` | ❌ **Implementation guide**                  | ⚠️ **Move to `09-scheduling/`** |
| `bryntum-reference.md`                   | ❌ **Implementation reference**              | ⚠️ **Move to `08-frontend/`**   |
| `schedule-VISUAL_SYSTEM.md`              | ⚠️ Design system                             | ✅ Keep (PRD/Design)            |

### What's in `09-scheduling/` (Correctly Placed)

| File                                  | Current Content                | Should Be                                        |
| ------------------------------------- | ------------------------------ | ------------------------------------------------ |
| `OVERVIEW.md`                         | ✅ Technical overview          | ✅ Keep (Technical)                              |
| `BACKEND_ARCHITECTURE.md`             | ✅ Technical architecture      | ✅ Keep (Technical)                              |
| `FRONTEND_INTEGRATION.md`             | ✅ Implementation guide        | ✅ Keep (Technical)                              |
| `TIMEFOLD_INTEGRATION.md`             | ✅ Integration guide           | ✅ Keep (Technical)                              |
| `PINNED_VISITS_GUIDE.md`              | ✅ Technical guide             | ✅ Keep (Technical)                              |
| `MOVABLE_VISITS.md`                   | ✅ Technical guide             | ✅ Keep (Technical)                              |
| `pilots/attendo/PILOT_PLAN.md`        | ⚠️ Mix of business + technical | ✅ **Keep** (Pilot-specific, scheduling feature) |
| `pilots/attendo/DATA_REQUIREMENTS.md` | ✅ Technical spec              | ✅ Keep (Technical)                              |

**Note**: Pilot plans are **feature-specific** (scheduling), so they belong in `09-scheduling/pilots/` even if they contain business objectives. General platform PRDs go in `05-prd/`.

---

## Recommended Structure

### Keep Current Structure (Recommended)

**Both folders serve different purposes:**

```
docs_2.0/
├── 05-prd/                    # WHAT & WHY (Product Requirements)
│   ├── prd-umbrella.md        # Product vision (all features)
│   ├── Feature PRD – *.md    # Feature requirements (general)
│   ├── schedule-VISUAL_SYSTEM.md # Design system
│   └── [No pilots here]       # Pilots are feature-specific
│
└── 09-scheduling/             # HOW (Technical Documentation)
    ├── OVERVIEW.md            # Technical overview
    ├── BACKEND_ARCHITECTURE.md # How backend works
    ├── FRONTEND_INTEGRATION.md # How to integrate frontend
    ├── TIMEFOLD_INTEGRATION.md # How to integrate Timefold
    ├── PINNED_VISITS_GUIDE.md  # Technical guide
    ├── MOVABLE_VISITS.md      # Technical guide
    └── pilots/                # Feature-specific pilots
        └── attendo/
            ├── PILOT_PLAN.md      # Business + technical (scheduling-specific)
            └── DATA_REQUIREMENTS.md # Technical data format spec
```

**Key Principle**:

- **PRD (`05-prd/`)** = General feature requirements, user stories, business value (applies to all features)
- **Technical (`09-scheduling/`)** = Architecture, implementation, integration, feature-specific pilots

---

## Decision Matrix

| Document Type                    | Goes In                                                           | Example                                    |
| -------------------------------- | ----------------------------------------------------------------- | ------------------------------------------ |
| **General feature requirements** | `05-prd/`                                                         | "Users need to drag-and-drop visits"       |
| **User stories**                 | `05-prd/`                                                         | "As a planner, I want to..."               |
| **Business objectives**          | `05-prd/` (general) or `09-scheduling/pilots/` (feature-specific) | "Reduce planning time by 50%"              |
| **Success metrics**              | `05-prd/` (general) or `09-scheduling/pilots/` (feature-specific) | "Efficiency ≥75%, Travel time -20%"        |
| **Architecture**                 | `09-scheduling/`                                                  | "GraphQL API with Prisma ORM"              |
| **API specs**                    | `02-api/` or `09-scheduling/`                                     | "Mutation: updateSchedule"                 |
| **Implementation guides**        | `09-scheduling/` or `08-frontend/`                                | "How to integrate Bryntum"                 |
| **Data formats**                 | `09-scheduling/`                                                  | "CSV format specification"                 |
| **Technical guides**             | `09-scheduling/`                                                  | "How pinned visits work"                   |
| **Feature-specific pilot plans** | `09-scheduling/pilots/`                                           | "Attendo pilot plan" (scheduling-specific) |

---

## Best Practice: Feature-Agnostic vs Feature-Specific

**Yes, having both is best practice:**

1. **Platform-level docs** (`01-architecture/`, `02-api/`, `03-data/`, `05-prd/`):
   - Apply to ALL features
   - General patterns and standards
   - Example: "All APIs use GraphQL", "General feature requirements"

2. **Feature-specific docs** (`09-scheduling/`):
   - Specific to scheduling feature
   - Detailed implementation
   - Feature-specific pilots
   - Example: "How scheduling optimization works", "Attendo pilot plan"

**This is similar to**:

- React docs: General React patterns vs Feature-specific guides
- AWS docs: General AWS services vs Service-specific deep dives

---

## Proposed Reorganization

### Files to Move from `05-prd/` to Technical Folders

1. ✅ **`PREPLANNING_BACKEND_ANALYSIS.md`** → `09-scheduling/` (MOVED)
   - **Reason**: Technical architecture analysis
   - **Status**: ✅ Moved to `09-scheduling/`

2. ✅ **`PREPLANNING_FRONTEND_IMPLEMENTATION.md`** → `09-scheduling/` (MOVED)
   - **Reason**: Implementation guide, not a PRD
   - **Status**: ✅ Moved to `09-scheduling/`

### Files to Keep in `05-prd/`

- ✅ `prd-umbrella.md` - Product vision (all features)
- ✅ `Feature PRD – *.md` - Feature requirements (general)
- ✅ `schedule-VISUAL_SYSTEM.md` - Design system (PRD/Design)
- ✅ `bryntum_consultant_specs/` - **Consultant specs/requests** (business requirements for external consultants)
  - `BRYNTUM_BACKEND_SPEC.md` - Backend API specs for consultants
  - `BRYNTUM_FROM_SCRATCH_PRD.md` - Greenfield build approach (112-152 hours)
  - `bryntum-reference.md` - Implementation reference for consultants

**Note**: The `bryntum_consultant_specs/` folder contains technical specs, but they're **business requirements/requests for external consultants** (RFQ documents), so they belong in `05-prd/` as part of the procurement/consultant engagement process.

### Pilot Plans: Keep in `09-scheduling/pilots/`

**Why**: Pilots are **feature-specific** (scheduling), not general platform PRDs.

- ✅ `pilots/attendo/PILOT_PLAN.md` - Scheduling-specific pilot (business + technical)
- ✅ `pilots/attendo/DATA_REQUIREMENTS.md` - Technical spec for scheduling

---

## Summary

**PRD (`05-prd/`)**: WHAT features should do, WHY they're needed (general, all features)  
**Technical (`09-scheduling/`)**: HOW to build and integrate them (feature-specific)

**Both structures are needed**:

- Platform-level (feature-agnostic) for general patterns
- Feature-specific for detailed implementation and feature-specific pilots

**Action**: Clean up `05-prd/` by moving technical specs to appropriate technical folders.
