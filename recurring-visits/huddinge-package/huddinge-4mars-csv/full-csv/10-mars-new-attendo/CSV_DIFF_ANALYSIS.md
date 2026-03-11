# CSV format comparison: small test vs 10-mars 81-clients

Comparison of **ATTENDO_DATABEHOV_PER_KUND_OCH_BESOK - data.csv** (small test) and **huddinge-81-clients - Data.csv** (10-mars new Attendo, 81 clients).

## Column / header differences


| Aspect            | Small test CSV  | 10-mars Data CSV                                                                                                                                                                |
| ----------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Shift column**  | `Schift` (typo) | `Skift` (correct spelling)                                                                                                                                                      |
| **Extra columns** | None            | `Column-9`, `Column-10` between Beskrivning and Kundnr (e.g. "Kopiera besök")                                                                                                   |
| **Other headers** | Same            | Same: Slinga, Starttid, Längd, Återkommande, Dubbel, När på dagen, Besökstyp, Insatser, Kundnr, Gata, Postnr, Ort, Före, Efter, Antal tim mellan besöken, Kritisk insats Ja/nej |


Script `attendo_4mars_to_fsr.py` uses header names (DictReader), so it now accepts both **Schift** and **Skift**; extra columns are ignored.

## När på dagen (time-of-day slots)


| Small test                    | 10-mars (Lathund)                                            | Slot (script mapping)                                                                                                                         |
| ----------------------------- | ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Morgon, Lunch, Kväll, (empty) | Morgon, Förmiddag, Lunch, Eftermiddag, Middag, Kväll, Lördag | Morgon 07:00–10:30, Förmiddag 10:00–11:00, Lunch 11:00–13:30, Eftermiddag 13:30–14:30, Middag 16:00–18:30, Kväll 16:00–19:00, Lördag → Morgon |


The **Lathund** file (`huddinge-81-clients - Lathund.csv`) defines the 10-mars slot names and shift times; the pipeline uses only the **Data** CSV. New slot names are handled in `_slot_for_nar_pa_dagen()`.

## Other differences

- **Slinga**: 10-mars has some rows with `städ` as Slinga (generic) instead of a named route; script creates one vehicle per unique Slinga.
- **Row count**: Small test ~107 data rows; 10-mars Data ~615 data rows (81 clients).
- **Planning window**: Same 2-week window (e.g. 2026-03-02–2026-03-15) used for both when generating FSR input.

## Reference

- Small dataset in TF Caire production: `57081ade-27e1-452f-900f-4107d3509ca6`
- Pipeline: CSV → `attendo_4mars_to_fsr.py` → input JSON → `submit_to_timefold.py validate` → `submit_to_timefold.py solve`

