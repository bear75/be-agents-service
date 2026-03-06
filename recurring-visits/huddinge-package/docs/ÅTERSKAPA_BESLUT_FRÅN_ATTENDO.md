# Återskapa kommunens beslut från Attendos fil

## Syftet

Hela syftet med pipeline är att **identifiera** vad som i källdatan ser ut som många rader (t.ex. H299_468 weekly x1 mån, H299_470 weekly x2 tis+ons, H299_469 weekly x1 tor) som **ett beslut** – t.ex. "besök varje vardag frukost" eller "besök 1 gång/vecka, lunch" – så att vi kan **optimera fritt** inom det beslutet.

**Beslutet är inte detaljerat i filen.** Kommunen/Attendo har tagit beslut (antal besök, typ, ungefärlig tid), men exporten ger oss bara detaljrader (en rad per veckodag, starttid, längd). Vi måste **ta deras fil och återskapa beslutet** – dvs inferera mönstret – och sedan bygga extended och input utifrån det.

---

## Idag vs önskat

**Idag (1→2):**  
Vi behåller i princip en rad per veckodag och sätter etiketter (weekly x1, weekly x2, recurring_external "Varje vecka, mån" osv.). Vi **grupperar inte** till ett enda beslut när samma typ av besök förekommer varje vardag (t.ex. 5 rader → "weekly x5").

**Konsekvens:**  

- I extended har vi många små beslut (en per rad).  
- "weekly x1" med veckodag (mån, tor) gav tidigare helveckofönster → fel (nu fixat till dag-bunden).  
- Vi **optimizar inte fritt** över "5 besök/vecka lunch" som ett beslut – vi har 5 separata beslut med fasta dagar.

**Önskat:**  

- **Återskapa beslutet:** Från Attendos rader inferera t.ex. "besök varje vardag frukost" → **ett** beslut: recurring med frekvens (t.ex. weekly x5) och tidsband (frukost).  
- **Extended:** Utifrån det beslutet skapa konkreta besök – t.ex. 5 dagar med snäva tidsfönster (mån–fre frukost), **eller** 1 besök/vecka med valfri dag om beslutet är "1 gång/vecka, flexibel dag".  
- Då kan vi **optimera fritt** inom beslutet (ordning, exakt tid inom fönster, vilken slinga) utan att skapa dubbletter eller fel dag.

---

## Inferens: från rader till beslut


| Vad vi ser i Attendo (1)                                              | Möjligt beslut vi vill återskapa                      | Hur vi kan gruppera (1→2)                                                         | Extended (2→3)                           |
| --------------------------------------------------------------------- | ----------------------------------------------------- | --------------------------------------------------------------------------------- | ---------------------------------------- |
| 5 rader: mån–fre, samma insats (t.ex. måltid), samma tidsband (lunch) | "Besök varje vardag, lunch"                           | **En** recurring: weekly x5, representativ tid (t.ex. 12:00) och flex från källan | 5 besök (mån–fre), snäva fönster per dag |
| 2 rader: lör+sön, samma insats                                        | "Besök varje helg"                                    | **En** recurring: weekly x2 (helg)                                                | 2 besök (lör, sön), snäva fönster        |
| 1 rad: "Varje vecka, ons" 12:00                                       | "Besök onsdag lunch"                                  | **En** recurring: weekly x1, ons                                                  | 1 besök onsdag, snävt fönster            |
| Flera rader olika veckodagar, olika tider (morgon vs lunch)           | Flera beslut (t.ex. frukost vissa dagar, lunch andra) | **Flera** recurrings, gruppera per veckodag + tidsband                            | Flera besök med respektive fönster       |
| Verkligen "1 gång/vecka, valfri dag" (sällan explicit)                | "Ett besök/vecka, optimeraren väljer dag"             | **En** recurring: weekly x1, **ingen** veckodag                                   | 1 besök med helveckofönster              |


Regel: **Samma beslut** = samma insats + samma tidsband (morgon/lunch/kväll) + frekvens som kan uttryckas som ett mönster (varje vardag, varje helg, 1 gång/vecka på dag X). När det är samma beslut ska vi **inte** ha en rad per veckodag som sedan expanderas till både dag-specifika besök och ett "extra" valfritt besök – vi ska ha antingen ett grupperat beslut (weekly x5 med 5 dagar) eller ett flexibelt (weekly x1 valfri dag).

---

## Nästa steg (för pipeline)

1. **1→2 (gruppering / konvertering):**
  - Identifiera när flera rader = **samma beslut** (samma kund, samma insatstyp, samma tidsband, regelbunden frekvens).  
  - Gruppera till **en** recurring med rätt frekvens (daily, weekly x2, weekly x5, …) och representativ starttid/flex.  
  - Behåll **separata** recurrings när beslutet är olika (t.ex. morgon måndag vs lunch onsdag).
2. **2→3 (expansion):**
  - **weekly x5 (vardag):** Skapa 5 besök (mån–fre) med **snäva** tidsfönster per dag (från beslutet).  
  - **weekly x1 med veckodag i källa:** Skapa 1 besök **på den dagen** med snävt fönster (redan fixat).  
  - **weekly x1 utan veckodag:** Skapa 1 besök med helveckofönster (optimera fritt vilken dag).
3. **Resultat:**
  Vi återskapar kommunens beslut (ett beslut = en recurring med tydlig frekvens och tidsband) och bygger extended så att vi **antingen** har många besök med snäva fönster (när beslutet är "varje vardag") **eller** ett besök med valfri dag (när beslutet är "1 gång/vecka, flexibel"). Då kan vi optimera fritt inom beslutet utan att skapa dubbletter eller fel dag.

---

## Sammanfattning

- **Syftet:** Ta Attendos fil och **återskapa beslutet från kommunen** – inte bara vidarebefordra en rad per veckodag.  
- **Beslutet är inte detaljerat** i filen; vi infererar det från mönster (antal dagar, insats, tidsband).  
- När flera rader = samma beslut (t.ex. besök varje vardag frukost) ska vi **gruppera** till ett beslut (t.ex. weekly x5) och i extended skapa motsvarande antal besök med snäva fönster – **inte** behålla en rad per dag plus ett "weekly x1 valfri dag".  
- Då kan vi **optimera fritt** inom det återskapade beslutet.

