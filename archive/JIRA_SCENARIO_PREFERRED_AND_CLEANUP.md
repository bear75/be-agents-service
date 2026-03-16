# Jira 2.0: Preferred scenario (Planning) + scenario-ticket cleanup

**Purpose:** Whether to add a new Jira ticket for the "Preferred (continuity & efficiency)" scenario, and how to reduce overlap across scenario-related tickets.

**Reference:** [CAIRE_PLANNING_PRD.md § Scenario: Continuity & efficiency](../05-prd/CAIRE_PLANNING_PRD.md#scenario-continuity--efficiency-solver-strategy) — Preferred is the chosen solver strategy for **Visit Planning**; goals (continuity ≤15, field eff. >67.5%); config: preferredVehicles, pool 15, weight 2.

---

## Planning vs Scheduling (important)

**Most existing scenario tickets (C0-151, SCEN-_, ADM-SCEN-_) are described for real-time/daily scheduling** (CAIRE_SCHEDULING_PRD — optimization of a single schedule, scenario selection in the scheduler UI). The **Preferred** scenario is for **Visit Planning** (CAIRE_PLANNING_PRD): generating a **repeating pattern** (slingor) with continuity and efficiency goals, not for daily re-optimization. When updating Jira, make this distinction explicit: the scenario system may serve **both** Planning and Scheduling, but **Preferred** is the **planning** default preset; other presets (e.g. A–E in 1.0) may remain for scheduling flows.

---

## 1. Do not add a new ticket for "Preferred scenario"

The **scenario system** is already covered by existing epics/tasks (today mostly scoped to scheduling in their descriptions). Adding the **Preferred** scenario is an **operational/content task**: ensure default presets include **Preferred (continuity & efficiency)** as the **planning** default, with the correct Timefold weights. That belongs **inside** the tasks that implement presets, not as a separate ticket.

- **C0-151 (Optimization Scenario Selection):** SCEN-FE-03 (Scenario Presets), SCEN-BE-03 (Default Scenario Presets), SCEN-FE-04 (Scenario Selection in Optimization), SCEN-BE-04 (Optimization with Scenario).
- **C0-153 (Admin Expanded):** ADM-SCEN-FE-01/02, ADM-SCEN-BE-01/02 (Scenarios Management — list/CRUD, form/detail, GraphQL, resolvers).

---

## 2. Update existing tasks (Preferred as **planning** default preset)

**Tasks to update (description or acceptance criteria)** — state clearly that this preset is for **Visit Planning**, not only scheduling:

| Task / Jira key                           | Update                                                                                                                                                                                                                                                                                                                                |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **SCEN-BE-03** (Default Scenario Presets) | Add: "Seed presets must include **Preferred (continuity & efficiency)** as the **default for Visit Planning** (CAIRE_PLANNING_PRD). Used when generating the repeating pattern (slingor), not for real-time scheduling. Config: preferredVehicles, pool 15, weight 2. See CAIRE_PLANNING_PRD.md § Scenario: Continuity & efficiency." |
| **SCEN-FE-03** (Scenario Presets)         | Add: "Presets must include **Preferred** as the **planning** default — balanced continuity (≤15 distinct caregivers per client) and field efficiency (>67.5%). Used in the **planning** flow (pattern generation); scheduling flows may use other presets (e.g. A–E)."                                                                |

**Visit Planning US-3 (Jira story for "AI generates repeating pattern"):** Add acceptance criterion: "Pattern generation uses the **Preferred** scenario by default (or planner explicitly selects it from planning presets)."

No new sub-tasks or new tickets required.

---

## 3. Scenario-ticket merge/cleanup (37 tickets)

Scenario-related work is split across:

- **C0-151** — Scenario **selection** (presets, modal, use scenario in optimization).
- **C0-153** — Admin **scenario management** (full CRUD, list, form, detail).

**Planning vs Scheduling:** C0-151 and C0-153 are currently described around **scheduling** (real-time optimization). Clarify in epic/task descriptions that the scenario system also supports **Visit Planning**: the **Preferred** preset is the planning default; scheduling may use other presets (A–E or custom).

**Overlap:** Both touch "scenarios" (create, list, edit). The difference is: C0-151 = presets + in-flow selection; C0-153 = admin CRUD for scenarios. If the same backend (GraphQL, resolvers) serves both, consider:

1. **Keep both epics** but clarify in epic descriptions:
   - C0-151: "User selects a scenario when running optimization (**scheduling**) or when generating a repeating pattern (**planning**). Includes default presets: **Preferred** for planning (CAIRE_PLANNING_PRD), plus presets for scheduling (e.g. A–E) and optional custom."
   - C0-153: "Admin creates/edits/deletes scenario definitions; shared with C0-151 for selection in both planning and scheduling flows."

2. **Or merge** "Scenario CRUD" into one epic (e.g. C0-151) and move "Admin scenarios **page**" (list/form UI under Admin) to C0-153 as a single "Scenarios admin UI" task that consumes the same API. That can reduce duplicate BE tasks (SCEN-BE-01/02 vs ADM-SCEN-BE-01/02) to one set of schema/resolvers and one "Admin scenarios page" FE task.

**Recommendation:** Do **not** create 37+ fine-grained scenario tickets. Keep C0-151 and C0-153; add the Preferred requirement to SCEN-BE-03/SCEN-FE-03 as above; then review C0-151 vs C0-153 and either document the split (selection vs admin) or merge duplicate BE work and keep one "seed Preferred" + one "Admin scenarios UI" flow.

---

## 4. Summary

| Action                                                                                                                | Do it                                                                    |
| --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Add new ticket "Preferred scenario"                                                                                   | **No**                                                                   |
| Update SCEN-BE-03 / SCEN-FE-03 with **Preferred as planning default** preset                                          | **Yes** — state explicitly "for Visit Planning" (not only scheduling)    |
| Add US-3 (Visit Planning) acceptance criterion: pattern generation uses Preferred by default                          | **Yes**                                                                  |
| Clarify in epic/task descriptions: scenario system serves **Planning** (Preferred) and **Scheduling** (other presets) | **Yes**                                                                  |
| Merge/cleanup scenario epics (C0-151 vs C0-153)                                                                       | **Review** — clarify or merge duplicate BE; keep ticket count manageable |
