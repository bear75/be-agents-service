# Pre–Jira Sync Review & Dev Handoff (Advanced Planning + US-6 AI Chat)

> **Purpose:** Consistency check across PRD, roadmap, project plan, and implementation plan before syncing to Jira and handing off to the dev. Use this to confirm artifacts are aligned and to brief the developer.
> **Date:** 2026-02-25

---

## 1. Artifact set (PRD + roadmap + tasks + plans)

| Artifact                           | Path                                                                     | Role                                                                                                                                                                     |
| ---------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **PRD (advanced planning)**        | `docs/docs_2.0/05-prd/SCHEDULING_ADVANCED_PLANNING_PRD.md`               | User stories US-1–US-6, acceptance criteria, technical requirements                                                                                                      |
| **Feature roadmap**                | `docs/docs_2.0/09-scheduling/ess-fsr/CAIRE_FEATURE_ROADMAP.md`           | Feature → ESS/FSR mapping                                                                                                                                                |
| **Project plan (sprints/tasks)**   | `docs/docs_2.0/09-scheduling/ess-fsr/ESS_FSR_PROJECT_PLAN.md`            | Sprints 1–14 with task breakdown; US-6 track (chat shell + connect-to-feature). _Internal plan uses “Night” labels for automation; Jira uses human-readable task names._ |
| **Timefold guides alignment**      | `docs/docs_2.0/09-scheduling/TIMEFOLD_GUIDES_ALIGNMENT.md`               | Guide concept → CAIRE doc → implementation (includes US-6 row)                                                                                                           |
| **AI chat implementation plan**    | `docs/plans/2026-02-25-ai-chat-schedule-integration.md`                  | US-6 chat shell: context, registry, panel, four surfaces, connect-to-feature                                                                                             |
| **Brainstorm (AI chat)**           | `docs/brainstorms/2026-02-25-ai-chat-schedule-brainstorm.md`             | Design decisions for US-6                                                                                                                                                |
| **Architecture**                   | `docs/docs_2.0/09-scheduling/ess-fsr/ESS_FSR_DUAL_MODEL_ARCHITECTURE.md` | ESS+FSR, recommendations, real-time                                                                                                                                      |
| **Continuity/priorities**          | `docs/docs_2.0/09-scheduling/ess-fsr/CONTINUITY_AND_PRIORITIES.md`       | 0 unassigned, continuity; cross-refs PRD US-1                                                                                                                            |
| **Using ESS**                      | `docs/docs_2.0/09-scheduling/ess-fsr/USING_ESS.md`                       | When ESS is used; multi-area                                                                                                                                             |
| **Timefold roadmap relevance**     | `docs/docs_2.0/09-scheduling/ess-fsr/TIMEFOLD_ROADMAP_RELEVANCE.md`      | Timefold roadmap items relevant to CAIRE                                                                                                                                 |
| **Schedule/solution architecture** | `docs/docs_2.0/09-scheduling/SCHEDULE_SOLUTION_ARCHITECTURE.md`          | Solutions, what-if branches, fine-tuning                                                                                                                                 |

---

## 2. Consistency review (completed 2026-02-25)

### PRD ↔ Plan ↔ Roadmap ↔ Project plan

| Check                                                           | Status | Notes                                                                     |
| --------------------------------------------------------------- | ------ | ------------------------------------------------------------------------- |
| PRD US-6 present with acceptance criteria and touches           | OK     | SCHEDULING_ADVANCED_PLANNING_PRD.md § US-6                                |
| PRD scope table includes AI chat (cross-cutting)                | OK     | Row: AI chat for schedule, Bryntum AI link, build-first                   |
| PRD 3.4 UI components includes AI chat panel                    | OK     | Row: AI chat panel (all schedule surfaces)                                |
| PRD 3.5 table: US-1–US-6 AI chat equivalents                    | OK     | Button vs chat examples per story                                         |
| Roadmap: AI chat row under Supply/demand optimization           | OK     | US-6, plan link, Bryntum AI, experimental                                 |
| Project plan: US-6 note in header + link to implementation plan | OK     | ESS_FSR_PROJECT_PLAN Project Overview                                     |
| Project plan: US-6 sprint block + connect-to-feature checklist  | OK     | Table in ESS_FSR_PROJECT_PLAN (internal “Night X1–X5” = chat shell tasks) |
| Implementation plan: Parts A–D, tasks B1/B2, C1–C5, D1          | OK     | docs/plans/2026-02-25-ai-chat-schedule-integration.md                     |
| TIMEFOLD_GUIDES_ALIGNMENT: US-6 row (Bryntum, not Timefold)     | OK     | Added this session for traceability                                       |

### Cross-references

- PRD 1.2 Related Documents: ESS_FSR_PROJECT_PLAN, CAIRE_FEATURE_ROADMAP, TIMEFOLD_GUIDES_ALIGNMENT — present.
- Roadmap Notes: link to PRD US-6 and to implementation plan — present.
- Project plan: link to implementation plan and PRD US-6 — present.
- Implementation plan: references PRD US-6, brainstorm, Bryntum AI — present.

**Verdict:** Artifacts are aligned. Safe to sync to Jira and hand off to dev.

---

## 3. How Jira user stories relate to epics and tasks

### Hierarchy (typical Jira Cloud)

| Level              | Issue type                           | Purpose                                                               | Your mapping                                                                                                  |
| ------------------ | ------------------------------------ | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **Epic**           | Epic (or Initiative in Jira Premium) | Large body of work, multiple sprints, strategic goal                  | One epic: “Advanced planning (Timefold guides) + AI chat”                                                     |
| **Story**          | Story                                | User-facing value; “As a [role], I want [capability] so that [value]” | One story per PRD user story: US-1, US-2, US-3, US-4, US-5, US-6                                              |
| **Task / Subtask** | Task or Subtask                      | Concrete, implementable work; one owner, one sprint                   | One task per deliverable (e.g. “FSR time-window recommendation client”, “Schedule chat context and provider”) |

**Relationship:**

- **Epic** → contains **Stories** (link stories to the epic via “Epic Link” or parent in hierarchy).
- **Story** → contains **Tasks** or **Subtasks** (tasks are children of the story; each task = one dev deliverable with a clear, human-readable title).

So: **PRD user stories = Jira Stories**; **concrete deliverables from the project plan / implementation plan = Jira Tasks** under the matching story; all under one **Epic**. Use descriptive task names in Jira (no “Night X” or “Night 31”); the repo’s project plan keeps internal labels for automation if needed.

### Optional: PRD and project plan as links

- **PRD:** Don’t create a separate “PRD” issue. Put the PRD link in the **Epic description** (and optionally in each Story description) so everyone has one source of truth. Example: `PRD: [SCHEDULING_ADVANCED_PLANNING_PRD](link-to-doc-or-wiki).`
- **Project plan:** Link in the **Epic description** and/or in a **Story** that represents “implementation plan” (e.g. US-6). Example: `Project plan: [ESS_FSR_PROJECT_PLAN](link). Implementation plan (US-6): [2026-02-25-ai-chat-schedule-integration](link).`

---

## 4. What to sync to Jira

- **Epic:** Advanced planning (Timefold guides) + AI chat (US-6).
  - Description: Short goal + links to PRD, roadmap, project plan, implementation plan (see artifact set in §1).
- **Stories (from PRD):**
  - US-1: Unassigned visit time-window recommendations.
  - US-2: Multi-area scheduling.
  - US-3: Disruption impact analysis and strategy comparison.
  - US-4: Freeze horizon for real-time replanning.
  - US-5: What-if without disruption.
  - US-6: AI chat as first-class entry point.
- **Tasks (or Subtasks) under each Story — use human-readable titles in Jira:**
  - **US-1:** FSR time-window recommendation client; Time-window recommendation GraphQL + bridge; Unassigned visit recommendations UI.
  - **US-2:** Schedule multi-area schema; Multi-area data aggregation; Multi-area ESS demand curve; Multi-area schedule creation UI; Multi-area vs single-area comparison.
  - **US-3:** Impact analysis in disruption handler; optimizeStrategy mutation; compareSolutions query; Disruption Panel UI; Compare Panel UI.
  - **US-4:** Freeze horizon in from-patch (createSolutionFromPatch accepts freezeBeforeTime).
  - **US-5:** What-if entry point (button/modal → Compare Panel).
  - **US-6:** Add US-6 and chat sprint to project plan (docs); Ensure roadmap row for AI chat references US-6; Schedule chat context and provider; Action registry (intent → handler); Bryntum AI chat panel (or placeholder) in SchedulerContainer; Expose chat on all four schedule surfaces; Connect chat to filter/sort/selection; Add “Connect chat to [feature]” checklist to project plan.  
    _(Detailed steps for each task are in the project plan and implementation plan; link to those from the Jira task description.)_
- **Links in Jira:** In Epic (and optionally in each Story) add links to: PRD (`SCHEDULING_ADVANCED_PLANNING_PRD.md`), project plan (`ESS_FSR_PROJECT_PLAN.md`), implementation plan (`2026-02-25-ai-chat-schedule-integration.md`), roadmap (`CAIRE_FEATURE_ROADMAP.md`). Use Confluence pages or repo URLs so dev and PO have one place to look.

### Adding PRD, user stories, and project plan to Jira (concrete steps)

1. **Create the Epic**
   - Title: e.g. “Advanced planning (Timefold guides) + AI chat”.
   - Description: 2–3 sentences + links to PRD, project plan, implementation plan, roadmap (wiki or repo paths).
   - Optional: Add a “PRD” custom field or label and paste the repo path to the PRD file.

2. **Create one Story per PRD user story (US-1 through US-6)**
   - Story title: e.g. “US-1: Unassigned visit time-window recommendations”.
   - Description: Copy the “As a … I want … so that …” from the PRD; paste acceptance criteria (bullets); add link to PRD section.
   - **Epic Link:** Set the epic above as parent.
   - Repeat for US-2, US-3, US-4, US-5, US-6.

3. **Create Tasks (or Subtasks) under each Story**
   - Use **descriptive task titles** for human devs (e.g. “FSR time-window recommendation client”, “Schedule chat context and provider”). Do not use “Night 31” or “Night X1” in Jira.
   - From **project plan:** One task per deliverable listed in §4 above for US-1–US-5.
   - From **implementation plan (US-6):** One task per deliverable for US-6 (context, registry, panel, four surfaces, filter/sort wiring, connect-to-feature checklist).
   - Task description: Short “what” + link to the exact section in project plan or implementation plan (file path + section heading).

4. **Sprints**
   - Add Stories (or their Tasks) to the appropriate sprints (e.g. Sprint 7 for US-1 and US-4; Sprint 13 for US-3 and US-5; Sprint 14 for US-2; a dedicated or parallel sprint for US-6 chat shell).

5. **Optional: Confluence**
   - Create a Confluence page that embeds or links to the PRD, roadmap, and project plan; link that page from the Epic description so “PRD, user stories, project plan” live in one place that Jira points to.

---

## 5. What to tell the dev

**Handoff (copy or adapt):**

- **Source of truth:** Implementation is driven by the **implementation plan** for US-6 and by the **project plan** for the rest.
  - **US-6 (AI chat):** Follow `docs/plans/2026-02-25-ai-chat-schedule-integration.md`. Execute in order: roadmap/project plan updates → Schedule chat context → Action registry → Chat panel in SchedulerContainer → Expose chat on four surfaces → Connect chat to filter/sort/selection → Add connect-to-feature checklist. Part A (PRD/roadmap) is already done. Use the “Research Insights” and “Enhancement Summary” in the plan for context.
  - **US-1–US-5:** Follow `docs/docs_2.0/09-scheduling/ess-fsr/ESS_FSR_PROJECT_PLAN.md` for task breakdown by sprint. Acceptance criteria and technical details are in `docs/docs_2.0/05-prd/SCHEDULING_ADVANCED_PLANNING_PRD.md`.
- **Architecture:** Respect monorepo rules (`.cursor/rules/appcaire-monorepo.mdc`): resolver layout, GraphQL direct hooks only, docs in `docs/`, no config changes without approval. Schedule chat: provider inside schedule route layout; action registry with closure over refs (no refs in context).
- **When a feature (US-1–US-5) ships:** Add the corresponding “Connect chat to [feature]” task from the checklist in the project plan (and in the implementation plan Part D) so the new capability is also available via the AI chat panel.

---

## 6. Execution options (from implementation plan)

After Jira sync, the dev implements the tasks in the order given in the implementation plan. Plan path: `docs/plans/2026-02-25-ai-chat-schedule-integration.md`. Jira tasks should mirror the plan’s deliverables with human-readable titles (no “Night X” or “B1/C1” in Jira).
