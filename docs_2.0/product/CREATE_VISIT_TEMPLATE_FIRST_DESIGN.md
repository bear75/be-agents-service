# Create Visit Flow: Template-First Design

**Purpose:** In Caire, every visit must have a recurring VisitTemplate. One-off visits use a template with frequency set to **one_off**. The create-new-visit flow should support choosing or defining that pattern (frequency, preferred days, timeslot) in one place.

---

## 1. Product rules

- **Every visit has a template.** No visit without `visitTemplateId`.
- **One-offs** = template with `frequency: one_off`. Same model; no special “one-off visit” type.
- **Create flow:** User either picks an **existing template** for the client or defines a **new pattern** (frequency, preferred days, preferred timeslot). If new, we create the template then the visit.

---

## 2. UX design direction

**Tone:** Calm, clear, healthcare-appropriate. Refined minimal with one strong block for “pattern” so it’s obvious that recurrence is first-class.

**Layout:**

1. **Basic info** (existing): Schedule, client, duration, type, etc.
2. **Återkommande mönster** (new, prominent):
   - **Choice:** “Använd befintligt mönster” vs “Nytt mönster”.
   - **If existing:** Dropdown of templates for the selected client (label: frequency + preferred days/timeslot summary).
   - **If new:**
     - **Frekvens:** Daglig, Veckovis, Varannan vecka, Månadsvis, Anpassad, **Enstaka gång** (one_off).
     - **Föredragna dagar:** Weekday checkboxes (Mån–Sön). Optional for one_off.
     - **Tidsfönster:** Dropdown: Förmiddag, Eftermiddag, Kväll, Flexibel (maps to `preferredTimeSlot`).
   - Visually: card or bordered block so “pattern” is one unit; optional soft background to separate from rest of form.
3. **Rest of form** (time windows, pinning, notes, etc.) unchanged in structure.

**Differentiator:** The recurrence block is the hero: one place to “use existing” or “define new” (frequency + days + slot). No hidden templates; one-offs are explicit (Enstaka gång).

---

## 3. Data model

- **VisitFrequency:** Add `one_off`. `frequencyToVisitCategory(one_off)` → `recurring`.
- **VisitTemplate:** Already has `frequency`, `preferredDays: String[]`, `preferredTimeSlot: String?`. No schema change.
- **visitTemplates(clientId, organizationId):** Query to list templates for a client (for dropdown).
- **createVisitTemplate(input):** Mutation to create a template (organizationId, clientId, frequency, durationMinutes, preferredDays, preferredTimeSlot, etc.). Returns `VisitTemplate`; form then calls `createVisit` with `visitTemplateId`.

---

## 4. Create-flow logic

**Create mode:**

1. User selects schedule + client.
2. **Pattern:** Either select existing template (dropdown) or choose “Nytt mönster” and fill frequency, preferred days, timeslot.
3. On submit:
   - If **existing template:** `createVisit({ ..., visitTemplateId: selectedId })`.
   - If **new pattern:** `createVisitTemplate({ organizationId, clientId, frequency, durationMinutes, preferredDays, preferredTimeSlot, ... })` → then `createVisit({ ..., visitTemplateId: newTemplate.id })`.
4. `createVisit` already derives `visitCategory` from template; with `one_off` we map it to `recurring`.

**Edit mode:** Visit already has a template; show read-only recurrence (frequency + preferred days/timeslot) or allow changing template (e.g. switch to another existing template) depending on product choice. Minimal change in this phase: keep current read-only “Återkommande” from template.

---

## 5. Preferred days and timeslot

- **preferredDays:** Array of strings. Use Swedish weekday abbreviations: `["Mån", "Tis", "Ons", "Tor", "Fre", "Lör", "Sön"]` for multi-select. Optional; stored as-is.
- **preferredTimeSlot:** Single string. **Not a FK to DaySlot** — `VisitTemplate.preferredTimeSlot` is a string column. Values should align with **DaySlot.name** (e.g. `morgon`, `formiddag`, `eftermiddag`, `kvall`, `lunch`, `middag`, `natt`, `custom`) so they stay consistent with the org’s day slots. The UI loads options from `daySlots(organizationId)` and stores `DaySlot.name`; display uses `DaySlot.displayName`. Optional.

---

## 6. Implementation checklist

- [x] Add `one_off` to enum `VisitFrequency` (Prisma + GraphQL).
- [x] Migration for new enum value (`20260311140000_add_visit_frequency_one_off`).
- [x] Update `frequencyToVisitCategory`: `one_off` → `recurring`.
- [x] GraphQL: `visitTemplates(clientId: ID!, organizationId: ID!)` query; `createVisitTemplate(input: CreateVisitTemplateInput!)` mutation; input type with organizationId, clientId, frequency, durationMinutes, preferredDays, preferredTimeSlot, etc.
- [x] Backend: Resolvers for `visitTemplates` and `createVisitTemplate` (auth: user’s org).
- [x] Frontend: “Återkommande mönster” section in VisitForm (create mode): use-existing vs new, frequency (incl. Enstaka gång), preferred days, timeslot; submit creates template when new then visit with `visitTemplateId`.
- [x] UI always sends `visitTemplateId` in create flow (existing or newly created template).
- [x] i18n: Labels for one_off (“Enstaka gång”), section title, preferred days/timeslot (keys in form).
- [x] FREQUENCY_LABELS + frequencyToMandatoryOptional: handle `one_off` (optional / no repeat).

---

## 7. References

- VisitTemplate: `apps/dashboard-server/schema.prisma` (VisitTemplate model).
- Create visit: `apps/dashboard-server/src/graphql/resolvers/visit/mutations/createVisit.ts`.
- Visit form: `apps/dashboard/src/components/Resources/Visit/VisitForm.tsx`.
- VISIT_IS_MOVABLE_USAGE.md (visitCategory deprecation, template.frequency).
