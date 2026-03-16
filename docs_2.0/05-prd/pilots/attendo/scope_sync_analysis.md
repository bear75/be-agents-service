# Scope Synchronization Analysis: Attendo Phase 1 vs. Bryntum Spec Phase 1

**Status:** Sync Verified
**Date:** 2025-12-20

## Overview

This analysis compares the functional requirements defined in the **Attendo Pilot Phase 1 Scope** (`fas1-scope.md`, `PILOT_PLAN.md`) with the development roadmap in the **Bryntum Component Specification** (`bryntum_timeplan.md`).

## Key Alignment Points

| Feature / Requirement  | Attendo Phase 1 (Scope)                          | Bryntum Spec Phase 1 (Dev)                                             | Status     | Note                                                                                                    |
| :--------------------- | :----------------------------------------------- | :--------------------------------------------------------------------- | :--------- | :------------------------------------------------------------------------------------------------------ |
| **Movable Visits**     | Required for pre-planning & "slinga" generation. | **Included** (Category 9: Pre-Planning & Movable Visits).              | ✅ Aligned | Bryntum spec explicitly includes "Movable visits panel" and "Pre-planning optimization".                |
| **Slingor (Patterns)** | Import existing, generate new from scratch.      | **Included** (Category 9: Pre-Planning & Movable Visits).              | ✅ Aligned | Spec covers "Generate new slingor from scratch" and "New slinga proposals".                             |
| **Manual vs AI**       | Drag & drop, pin/unpin, validation.              | **Included** (Category 1, 2, 3: Core Viewing, Assignment, CRUD).       | ✅ Aligned | Core functionality covering drag-drop, pinning (Category 3), and validation.                            |
| **Comparison**         | Unplanned vs Planned vs Optimized vs Actual.     | **Included** (Category 6: Schedule & Service Area Comparison).         | ✅ Aligned | "Compare planned vs optimized schedules", "Planned vs Actual" example cited.                            |
| **Real-time Changes**  | Simulate disruptions (sick, cancel).             | **Included** (Category 8: Real-time Optimization).                     | ✅ Aligned | Optimization button, scenario selection, handling changes.                                              |
| **Map View**           | Visualize travel times (Section 7).              | **Included** (Category 1: Core Viewing - "Kartvy" listed in overview). | ✅ Aligned | "Kartvy (restidsvisualisering)" is explicitly listed in Bryntum Phase 1 scope summary in `TIMEPLAN.md`. |
| **Data Import**        | CSV import (eCare).                              | **Included** (Category 11: Integration).                               | ✅ Aligned | "Data requirements template" and mappers for CSV->JSON are part of the dev plan.                        |

## Discrepancies / Clarifications

1.  **Transport Mode**: Attendo Phase 1 specifies **Driving Only** (`fas1-scope.md` Section 1.4). Bryntum Spec mentions "Transport mode icon" and "Travel time display".
    - _Resolution_: This is a simplification on the _optimization_ side. The UI should still display the transport mode (Driving), but doesn't need complex mode switching logic for Phase 1. Access to "Cycling" or "Walking" might be hidden or disabled in UI for this pilot phase.

2.  **Skills/Competencies**: Attendo Phase 1 explicitly excludes Skills/Competencies (`fas1-scope.md` Section 1.1 "Medvetet utanför scope"). However, Bryntum Spec Category 2 mentions "Skill matching validation".
    - _Resolution_: The Bryntum component is being built for the wider _Caire Platform_, so it includes skills. For the **Attendo Pilot Phase 1**, these features might be present but either unused (all employees have "all skills") or hidden. The pilot scope excludes them as _optimization constraints_, but having the UI capability doesn't hurt.

3.  **Map View Detail**: `fas1-scope.md` Section 7 asks for "Kartvy per slinga/dag" with route lines. `bryntum_timeplan.md` mentions "Kartvy" in the overview but detailed map integration (e.g. Google Maps/Leaflet inside/alongside Bryntum) is a significant task.
    - _Resolution_: Ensure "Kartvy" in Bryntum plan covers the specific requirement of visualizing the route line, not just a static map.

## Conclusion

The **Bryntum Phase 1 Spec is in synchronization with the Attendo Phase 1 Scope**. The development plan covers all critical operational requirements (movable visits, slingor, comparison, manual adjustments). Minor "extra" capabilities in the Bryntum spec (Skills) do not conflict with the pilot scope; they just won't be actively used/constrained in the first pilot phase.
