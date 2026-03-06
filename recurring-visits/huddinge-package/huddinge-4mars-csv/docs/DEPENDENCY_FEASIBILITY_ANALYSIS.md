# Analys: Är dependencies fysiskt möjliga? (479a238d)

**Input:** `input_4mars_2w_with_extra_vehicles.json`  
**Fokus:** Kunderna med många unassigned (H034, H053, H035, H026, H038).  
**Script:** `scripts/analyze_dependency_feasibility.py`

---

## Resultat

**Alla 54 analyserade dependencies för dessa kunder är fysiskt omöjliga** med nuvarande tidsfönster.

Kravet är: *dependent måste kunna starta senast vid* `prev_end + minDelay`, dvs.  
`prev_max_end + minDelay <= dep_latest_start` (för någon dag-/fönsterpar).

| Typ | Exempel | Orsak |
|-----|--------|--------|
| **PT24H** | H034_r39_1 ← H034_r38_1 | Prev slutar 09:57; +24h = nästa dag 09:57. Dep har bara fönster samma dag med latest start 12:25. För 24h krävs att dep har fönster **nästa dag** – har den bara samma dag blir kedjan omöjlig. |
| **PT3H30M** | H034_r40_1 ← H034_r37_1 | Prev slutar 13:07 (efter service); dep latest start 13:00. Alltså 13:07 > 13:00 → dep kan inte starta i tid. |
| **PT1H30M** | H034_r41_1 ← H034_r39_1 | Required 14:25 > dep latest start 13:10 → för lite tid i fönstret. |

---

## Varför det blir omöjligt

1. **24h/36h/48h på samma dag**  
   När `minDelay` är 24h eller mer måste *dependent* ha ett fönster **minst en dag efter** föregående besök. Om båda bara har fönster **samma dag** (t.ex. båda “Morgon” på samma datum) kan kedjan aldrig uppfyllas.

2. **För kort dep-fönster**  
   När prev slutar 13:07 och minDelay är 3h30m måste dep kunna starta tidigast 13:07 (samma dag). Om dep bara får starta fram till 13:00 (latest start 13:00) blir det omöjligt.

3. **Capping i scriptet (åtgärdat)**  
   `attendo_4mars_to_fsr.py` använder nu **samma per-fönsterpar-logik** som `scripts/analyze_dependency_feasibility.py`: för varje (prev_dag, dep_dag)-par kollas att prev_end + delay ≤ dep_latest_start med **15 min marginal**. Om inget par är möjligt kapas delay till bästa möjliga med 15 min marginal, eller beroendet tas bort. Efter omgenerering av input från CSV bör därför dependencies antingen vara möjliga eller borttagna/kappade. Kör `analyze_dependency_feasibility.py` på nytt efter generering för att verifiera.

---

## Rekommendationer (justera så att kedjor blir möjliga)

### 1. Fönster för 24h+ delay

- **Krav:** När CSV har “Antal tim mellan besöken” ≥ 24h ska *dependent*-besöket få **period/tidsfönster som inkluderar nästa dag** (eller flera dagar), inte bara samma dag som prev.
- **I script:** Säkerställ att `_build_time_windows` för återkommande besök med sådan delay ger minst ett fönster på **nästa dag** (eller att perioden är många dagar så att nästa dag finns med).

### 2. Samma dag: minDelay vs dep-fönster

- Om prev slutar 13:07 och minDelay är 3h30m kan dep inte ha “latest start 13:00” samma dag.
- **Antingen:**  
  - förkorta minDelay (t.ex. capa till vad som får plats i dep-fönstret, med lite marginal),  
  **eller**  
  - vidga dep-fönstret (senare latest start / längre fönster) så att `prev_end + minDelay <= dep_latest_start`.

### 3. Ta bort eller sätt “optional” för omöjliga kedjor

- Om vissa kedjor enligt affären inte ska vara hårda: ta bort dependency eller markera som icke-mandatory så att solvern kan placera besöken även när kedjan är omöjlig.

### 4. Kontroll i pipeline

- Kör `scripts/analyze_dependency_feasibility.py` efter CSV→JSON (samma input som skickas till solve).  
- Om många “infeasible” för vissa kunder: justera CSV, fönsterlogik eller minDelay enligt ovan, generera om input och kör analysen igen.

---

## Artifacts

- **Rapport (JSON):** `docs/dependency_feasibility_479a238d.json`  
- **Kommando:**  
  `python3 scripts/analyze_dependency_feasibility.py input/input_4mars_2w_with_extra_vehicles.json --focus H034,H053,H035,H026,H038 -o docs/dependency_feasibility_479a238d.json`
