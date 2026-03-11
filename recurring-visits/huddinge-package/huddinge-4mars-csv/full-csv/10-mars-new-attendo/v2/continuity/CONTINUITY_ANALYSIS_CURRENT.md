# Kontinuitetsanalys – nuvarande lösning (d2a6a01b)

## Resultat (115 kunder, 41 vårdgivare, 379 shifts med besök)

- **Genomsnittlig kontinuitet:** 17,16 (antal unika vårdgivare per klient).
- **97 klienter** har minst ett tilldelat besök; 18 av 115 har inga besök i denna lösning.

## Varför det blir “sämre”

Solveren har **ingen stark kontinuitetsmål**. Den minimerar resa och väntetid, så besök tilldelas “vem som är nära” – därav många olika vårdgivare per klient.

### Fördelning (antal vårdgivare per klient)

| Olika vårdgivare | Antal klienter |
|------------------|----------------|
| 1                | 11             |
| 2                | 7              |
| 3–10             | 16             |
| 11–20            | 22             |
| 21–34            | 41             |

Största delen av klienterna (41 st) har **21–34 olika vårdgivare** över 2 veckor.

### Värst (mest vårdgivare)

- H026, H238, H365: **34** olika vårdgivare  
- H035, H248, H363: **33**  
- H055, H086, H095, H145, H154, H182, H290, H332: **30–32**

### Bäst (färst vårdgivare)

- 11 klienter har bara **1** vårdgivare (t.ex. H061, H164, H240, H287, H297, H312, H339, H341, H342, H361).

## Combo-lösningen (cdfbe510)

- **Status:** SOLVING_ACTIVE (pågår fortfarande).  
- **Unassigned:** 138 (fler än i baslösningen som har 32).  
- **Kontinuitet på sparad output (delvis lösning):** ca 17,2 i snitt – i praktiken oförändrat mot 17,16.

**Slutsats:** Med nuvarande vikter (preferVisitVehicleMatchPreferredVehiclesWeight=2) prioriteras fortfarande resa/väntetid så mycket att kontinuiteten inte förbättras märkbart.

## Vad krävs för bättre kontinuitet

1. **Hårdare pool:** använda **requiredVehicles** (hård pool) istället för bara preferredVehicles, så varje klient bara kan tilldelas ett begränsat antal fordon (t.ex. 2–5).  
2. **Mycket högre vikt på kontinuitet:** t.ex. `preferVisitVehicleMatchPreferredVehiclesWeight` 10–50+ så att brytningar mot poolen blir dyra.  
3. **Mindre pool per klient:** t.ex. max 5–8 fordon per klient i poolen istället för 15, så solveren tvingas koncentrera besök till färre vårdgivare.

När combo-lösningen är färdig kan kontinuitet räknas om med:

```bash
python3 scripts/continuity_report.py --input "v2/input/export-field-service-routing-v1-d2a6a01b-...-input.json" --output "v2/continuity/combo_output.json" --only-kundnr --report "v2/continuity/continuity_combo_115.csv"
```

(Fetch output först med `fetch_timefold_solution.py cdfbe510-093f-490e-8d9a-c8172e40710f --save v2/continuity/combo_output.json` när status är SOLVING_COMPLETED.)
