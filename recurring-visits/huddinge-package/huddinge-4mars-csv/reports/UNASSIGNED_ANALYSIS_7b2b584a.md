# Unassigned-besök: analys och åtgärd (plan 7b2b584a)

## Resultat från körning

- **599/744** besök tilldelade, **145** unassigned
- **154** tomma skift (av 254 totalt)
- **Idle** 1358h (73,6 % av skift-tid)

## Analys (analyze_unassigned + analyze_empty_shifts)

| Klassificering | Antal | Betydelse |
|----------------|-------|-----------|
| **Supply** (ingen överlappande skift) | **0** | Behöver inte fler skift i indata |
| **Config** (≥1 överlappande skift) | **145** | Solver valde att inte tilldela trots tillgänglig kapacitet |
| Unassigned med ≥1 överlappande skift som har **idle** i fönstret | **145/145** | Kapacitet fanns; solver prioriterade bort (t.ex. resa) |

**Tomma skift vs unassigned:** 154 tomma skift överlappar tidsfönster för unassigned-besök. Alltså finns **kapacitet** (idle) som hade kunnat ta dessa besök.

## Slutsats: inte supply – config/tuning

- **Omfördela skift “idle → supply” i indata behövs inte** – det är inte brist på skift. Varje unassigned har redan överlappande skift (många tomma).
- **Åtgärd:** **Timefold-config** så att solver prioriterar att tilldela alla besök:
  - Sänk t.ex. `minimizeTravelTimeWeight` eller öka vikt för “assign all”-mål.
  - Testa tenant default (inga config-id) eller en “Assign-all”-profil i Timefold Dashboard.

## Nästa steg

1. **Ny solve med test-tenant** (redan skickad): plan **e6f0d14a-3830-4a5b-a736-62f3ed274b69** med `--configuration-id ""` (tenant default). Hämta när klar:  
   `python fetch_timefold_solution.py e6f0d14a-3830-4a5b-a736-62f3ed274b69 --save …/output/ --metrics-dir …/metrics/`
2. Jämför antal unassigned efter e6f0d14a; om fortfarande många, skapa/ändra en config-profil i Timefold som prioriterar tilldelning.
3. Efter **0 unassigned**: använd from-patch för att trimma tomma skift (omfördela inte skift i JSON, utan ta bort onödiga skift i lösningen).

## Test-tenant API

- **API-nyckel:** `tf_p_96b5507b-57be-4ab6-b0a6-08a9d3372938`
- **Solve utan config-profil (tenant default):**  
  `--api-key "tf_p_96b5507b-57be-4ab6-b0a6-08a9d3372938" --configuration-id ""`  
  (Om `--configuration-id` utelämnas används en annan default som kan ge 400 för denna tenant.)
