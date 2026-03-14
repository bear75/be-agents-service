# Attendo FSR visit ID and naming format (canonical)

This document defines the **exact** visit id, visit name, visitGroup id, and vehicle id format produced by the Attendo 4mars pipeline so the dashboard (beta-appcaire) can align its Timefold FSR request and avoid duplicate-visit errors.

**Reference scripts:**
- `attendo_4mars_to_fsr.py` — CSV → FSR input (direct)
- `rewrite_visit_ids_in_input.py` — Rewrites existing input to canonical ids

---

## 1. Visit ID (required for no duplicates)

**Canonical format:** `{kundnr}_r{row}_{occ}`

| Part   | Meaning | Example |
|--------|--------|--------|
| `kundnr` | Client id from CSV (e.g. Kundnr column). No spaces. | `H015`, `H053` |
| `row`    | Row index: 0-based. In script: CSV row index; in rewrite: ordinal of that client among all clients. | `0`, `12`, `102` |
| `occ`    | Occurrence index: 1-based among visits that share the same `(kundnr, row)`. | `1`, `2`, `3` |

**Examples:** `H015_r0_1`, `H015_r0_2`, `H053_r1_1`, `H053_r12_3`.

**Rules:**
- Every visit must have a **globally unique** id. The triple `(kundnr, row, occ)` must be unique per visit.
- **Do not** use date in the id (e.g. no `att-6-2026-03-29`). Multiple visits same client same day must differ by `occ` (and/or `row` if you use CSV row).
- In **attendo_4mars_to_fsr.py**: `row` = CSV `row_index` (0-based), `occ` = 1-based counter per `(kundnr, row_index)` (see `_assign_visit_ids_kundnr_lopnr`).
- In **rewrite_visit_ids_in_input.py**: `row` = ordinal of kundnr (first client 0, second 1, …), `occ` = 1-based among all visits of that kundnr.

**Dashboard alignment:** Use a single scheme. Recommended: per client, assign `row` = 0 (or use template/CSV row index if you need to match script row semantics), and `occ` = 1-based for every visit of that client so each visit gets a unique id, e.g. `H015_r0_1`, `H015_r0_2`, … or, if you use a numeric client id, `att-6_r0_1`, `att-6_r0_2` (no date).

---

## 2. Visit name (display, no uniqueness requirement)

**Preferred (from attendo_4mars_to_fsr.py):**  
`{kundnr} {När på dagen} {Skift} {Insatser}` trimmed, max 100 chars.

- **När på dagen:** e.g. Morgon, Lunch, Kväll.
- **Skift:** e.g. Dag, Helg, Kväll.
- **Insatser:** e.g. Tillsyn, Bad/Dusch.

**Example:** `H015 Morgon Dag Tillsyn`.

**Rewrite fallback:** If rewriting existing input, strip a trailing date from the old name: strip `\s+YYYY-MM-DD` at end; if empty after strip, use `{kundnr} Besök {occ}`.

**Rule:** Do **not** put the visit date in the visit **id**; it can appear in the name if desired.

---

## 3. VisitGroup id

**Format:** `VG_{slug}`

- `slug` = Timefold-safe slug of the group key: remove non-alphanumeric (except spaces/hyphens), replace spaces/underscores with single `_`, trim. (See `_slug()` in attendo_4mars_to_fsr.py.)
- Group key in script: `{dubbel}_{date_iso}` (e.g. `Dubbel_2026-03-02`).

**Example:** `VG_Dubbel_2026_03_02` (after slug of `Dubbel_2026-03-02`).

**Slug implementation (script):**
```python
slug = re.sub(r"[^\w\s-]", "", s.strip())
slug = re.sub(r"[\s_]+", "_", slug).strip("_")
return slug or "unknown"
```

---

## 4. Vehicle id

**Format:** One vehicle per unique **Slinga** (route/team). Id = slug of Slinga; if collision, `{slinga}_1`, `{slinga}_2`, …

**Supplementary vehicles (script):** `Extra_Kvall_1`, `Extra_Dag_1`, etc.

---

## 5. Dependency id (visitDependencies)

**Format:** `dep_{visitId}_{index}`

- `visitId` = the visit that has the dependency (the “follower”).
- `index` = 0-based index of that dependency in the visit’s dependency list.

**Example:** `dep_H053_r12_2_0`, `dep_H053_r12_2_1`.

---

## 6. Why “duplicates att-6-2026-03-29” happens in the dashboard

- The dashboard currently uses **visit id** = `overrideId ?? visit.id`. For Attendo imports, `visit.id` is a DB UUID (unique). So duplicates come from **overrideId**.
- In the **group (Dubbel)** expansion, the code uses the same `visitId` for **every member** of the same occurrence:  
  `visitId = \`${repVisit.externalId ?? repVisit.id}_g${occCounter}\``  
  So two members in the same group get the same id (e.g. `att-6-2026-03-29_g1` twice) → duplicate visit id.
- **Fix:** Ensure every FSR visit has a **unique** id. Either:
  1. Use the canonical format `{kundnr}_r{row}_{occ}` for all visits (including group members), e.g. `att-6_r0_1`, `att-6_r0_2`, and for Dubbel members `…_1`, `…_2` or `…_g1_m0`, `…_g1_m1`; or  
  2. Keep using DB `visit.id` (UUID) when not using overrideId, and when building overrideId for groups include a member index so each visit has a distinct id (e.g. `…_g${occCounter}_m${memberIdx}`).

Using the canonical format also aligns dashboard output with the script pipeline and avoids date-based or non-unique ids.

---

## 7. Short checklist for dashboard

- [ ] **Visit id:** `{kundnr}_r{row}_{occ}` (no date). Ensure uniqueness for every visit (incl. group members).
- [ ] **Visit name:** `{kundnr} {När} {Skift} {Insatser}` or strip trailing date; fallback `{kundnr} Besök {occ}`.
- [ ] **VisitGroup id:** `VG_{slug(groupKey)}`, groupKey e.g. `{dubbel}_{date_iso}`.
- [ ] **Vehicle id:** Slug of Slinga (and `{slinga}_n` if collision).
- [ ] **Dependency id:** `dep_{visitId}_{index}`.
- [ ] **No duplicate ids:** Especially in group expansion, give each member a distinct id (e.g. include member index or use canonical occ numbering).
