# Why 78 visits are unassigned despite 364 empty shifts (479a238d)

**Route plan:** `479a238d-c410-4a55-89a0-c9d00a309dbb`  
**Input:** `input_4mars_2w_with_extra_vehicles.json` (744 visits, 40 vehicles, 448 shifts)  
**Result:** 666 assigned, **78 unassigned**, 364 empty shifts, 84 shifts with visits.

---

## Short answer

**Det är inte brist på kapacitet.** För alla 78 unassigned finns minst ett skift som både överlappar besökets tidsfönster och har ledig tid. Solvern har *valt* att lämna dem unassigned (eller hittade inte en tilldelning innan den avslutade) på grund av **konfiguration/tuning**, inte brist på skift.

---

## Evidence (from fetch metrics report)

| Metric | Value |
|--------|--------|
| Supply (no overlapping shift) | **0** → ingen unassigned saknar ett överlappande skift |
| Config (≥1 overlapping shift) | **78** → alla 78 har ≥1 skift som överlappar tidsfönstret |
| Unassigned with ≥1 overlapping shift that has idle in window | **78 / 78** → alla har tillgänglig kapacitet i sitt fönster |

Alla unassigned är alltså klassade som **Config**: problemet sitter i solver-inställningar (vikter, termination), inte i input.

---

## Why the solver leaves them unassigned

1. **Soft constraints / vikter**  
   Unassigned-bestraffning (medium) vägs mot travel/wait. Om vikten för att minimera travel eller wait är hög kan solvern föredra att lämna några besök unassigned om det ger bättre total score (mindre restid/väntan på de tilldelade).

2. **Termination / tid**  
   Solvern kan ha avbrutits innan den hittade en lösning där alla 78 får plats. Då får man en suboptimal lösning med kvarvarande unassigned trots tillräcklig kapacitet.

3. **Dependencies (visitDependencies)**  
   Många av de unassigned tillhör kunder med tuffa kedjor (H034, H053, H035, H026, H038). Input-genereringen rapporterade "delay capped", "infeasible, removing". Det kan göra det svårt att placera besöken i rätt ordning inom ett skift utan att bryta mot `precedingVisit`/`minDelay`, så solvern kan ha svårt att hitta en tillåten tilldelning även när skiftet är tomt.

---

## Recommended next steps

1. **Tune Timefold config (tenant/profil)**  
   - Öka vikt för att **minimera unassigned** (medium constraint) så att fler besök prioriteras att få en tilldelning.  
   - Minska relativ vikt för **travel/wait** om det behövs för att solvern ska våga fylla fler skift.  
   - Referens: test_tenant `ANALYSIS_VS_GOAL.md`, `recurring-visits/docs/brainstorms/2026-03-03-continuity-config-weights-brainstorm.md`.

2. **Längre solve-tid**  
   Om termination sker efter tid, öka `secondsSpentLimit` (eller motsvarande) så att solvern har mer tid att hitta lösningar där de 78 får plats.

3. **Granska dependencies för H034, H053, H035, H026, H038**  
   Om capped/removed dependencies gör ordningen opraktisk, justera käll-CSV eller logiken i `attendo_4mars_to_fsr.py` (t.ex. minDelay, vilka dependencies som behålls) så att kedjor blir genomförbara inom tillgängliga skift.

---

## Artifacts

- **Output:** `output/479a238d-c410-4a55-89a0-c9d00a309dbb_output.json`  
- **Metrics report:** `metrics/metrics_report_479a238d.txt`  
- **Unassigned visit IDs:** H034_r38_*, H053_r101_*, H053_r102_*, H035_r45_*, H035_r46_*, H035_r47_*, H035_r48_*, H034_r39_*, H053_r103_*, H034_r41_*, H053_r106_*, H026_r12_*, H026_r13_*, H038_r65_*, H026_r16_*, H026_r17_*, H038_r71_* (78 total).
