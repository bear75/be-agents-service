# Input-kontroll: delays och pin/flex efter ändringar (6 mars)

**Fil:** `export-field-service-routing-input.json` (genererad med fixad `attendo_4mars_to_fsr.py`)

## 1. Same-day delay – fungerar som tänkt

- **Före fix:** Same-day dependencies fick `minDelay: "PT0S"` (effective = interval − slot_length → 0 för Morgon→Lunch).
- **Efter fix:** Samma-dag-kedjor använder **faktisk delay** från CSV (ingen slot-subtraktion):
  - **PT3H30M** – där 3,5 h får plats mellan Morgon (07–10:30) och Lunch (11–13:30), t.ex. H015_r0_* → H015_r1_*, H029_r29_*.
  - **PT3H**, **PT3H20M**, **PT3H8M**, **PT2H58M**, **PT2H** – där `_cap_infeasible_delay` har kapat till max möjlig delay med 15 min marginal (t.ex. H025_r7_*, H029_r33_*, H034_*, H053_*).
- **PT0S:** **0 st** i input → ingen same-day-delay är noll längre.

## 2. Spread (flexible_day) – oförändrat

- **PT18H** mellan besök i samma flexible_day-kedja (t.ex. H025_r8_1 → H025_r8_2 → …), som förväntat.
- **PT23H15M** där längre intervall (t.ex. 33,5 h / 28 h) kapats till vad som får plats i perioden.

## 3. Pin vs flexible_day (veckodagar)

- **Pinnade besök:** En timeWindow per datum (ett fönster per dag). T.ex. H015_r0_1 har ett fönster per dag i planeringsfönstret.
- **Flexible_day:** Flera timeWindows som spänner **olika dagar i perioden** (solver väljer dag). T.ex. H025_r8_2 har fönster 2, 3, 4 och 6 mars (och r8_5 har 9, 10, 11 mars) – alltså “N besök per period” med 18 h mellanrum, inte pinnade på specifika veckodagar.
- Partiella veckodagsmängder (”mån tis tor” etc.) ger nu flexible_day med spread; endast hela mängder (mån–fre, lör–sön, alla 7) pinnas.

## 4. Sammanfattning

| Kontroll | Resultat |
|----------|-----------|
| Same-day delay inte PT0S | OK – alla same-day har PT2H–PT3H30M (eller kapad variant). |
| 3,5 h används där möjligt | OK – PT3H30M förekommer; annars kapad till max möjlig. |
| Spread 18h kvar | OK – PT18H för flexible_day-kedjor. |
| Pin endast hela mängder | OK – flexible_day-besök har period-fönster över flera dagar. |

**Slutsats:** Inputen i `6march-tf/5` reflekterar våra ändringar. Delays beter sig som förväntat; nästa steg är att köra solve (utan --wait om du vill) och sedan hämta senaste lösning från TF och verifiera att solvern respekterar dessa delays i output.
