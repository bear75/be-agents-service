# CSV → input-JSON: verifiering för Attendo Huddinge

**English:** See **CSV_TO_INPUT_VERIFICATION.md** in the same folder.

**För Attendo:** Det här dokumentet beskriver hur vi tolkar er CSV-fil (*ATTENDO_DATABEHOV_PER_KUND_OCH_BESOK - data.csv*) när vi bygger indata till vår ruttoptimerare (Timefold Field Service Routing). Syftet är att ni ska kunna verifiera att vår tolkning stämmer med er avsikt — tidsfönster, vilka besök som hör ihop (Dubbel), mellanrum mellan besök och återkommande mönster. Om något är fel kan vi justera reglerna innan körning. Den färdiga indatan skickas som JSON till Timefold. För att granska JSON-strukturen (besök, fordon, skift, tidsfönster, besöksgrupper) kan ni använda Timefolds öppna API-schema: **[Timefold FSR OpenAPI (v1)](https://app.timefold.ai/openapis/field-service-routing/v1)**.

**Schema / API-referens:** Den genererade JSON-indatan följer Timefold Field Service Routing (FSR) API:ets modell. För att kontrollera exakt struktur (visits, timeWindows, visitDependencies, visitGroups, vehicles, shifts) och fälttyper (t.ex. ISO 8601-tider och -varaktigheter) kan ni använda den officiella OpenAPI-specifikationen: **[Timefold FSR OpenAPI (v1)](https://app.timefold.ai/openapis/field-service-routing/v1)**. Där hittar ni schemat `RoutePlanInput` (modelInput) med beskrivningar av `Visit`, `TimeWindow`, `VisitDependency` (minDelay), `VisitGroup`, `Vehicle` och `VehicleShift`.

Det här dokumentet beskriver **hur vi tolkar er CSV** när vi bygger optimeringsindata. Använd det för att bekräfta att vår mapping stämmer med er avsikt. Om något är fel kan vi justera reglerna innan körning.

---

## 1. Syfte

- **Indata:** Er CSV (t.ex. *ATTENDO_DATABEHOV_PER_KUND_OCH_BESOK - data.csv*).
- **Utdata:** En JSON-indata till route-optimeraren (besök, tidsfönster, vilka besök som hör ihop och när de får planeras).
- **Mål:** En gemensam förståelse för:
  - **När** varje besök får ske (tidsfönster),
  - **Vilka besök som hör ihop** (samma tid, samma frekvens),
  - **Hur ofta** varje besök ska ske (återkommande mönster).

---

## 2. Översikt: CSV → JSON

### Kolumner vi använder

| CSV-kolumn | Syfte |
|------------|--------|
| Kundnr | Klientidentifierare (t.ex. H015); används för gruppering och adress. |
| Insats | Beskrivning (t.ex. Tillsyn, Bad/Dusch); ingår i besöksnamn. |
| Slinga | Rutt/slinga → vehicle (fordon); samma Slinga = samma vehicle. |
| Schift | Dag / Helg / Kväll → skifttyp och tillåtna dagar. |
| Återkommande | Frekvens och veckodagar → pinnade dagar eller flexible_day. |
| Dubbel | Samma värde = besöksgrupp (samtidigt, samma dag). |
| När på dagen | Morgon / Lunch / Kväll → tidsfönster; tomt/annat = heldag. |
| Starttid | Önskad starttid (HH:MM); används med Före/Efter. |
| Längd | Varaktighet i minuter → serviceDuration. |
| Före, Efter | Minuter flex runt starttid (0 = hela sloten). |
| Antal tim mellan besöken | Minsta mellanrum mellan besök (samma dag eller spridning). |
| Kritisk insats Ja/nej | Ja = true, annat/tomt = false; används i pipeline (se 5.1). |
| Gata, Postnr, Ort | Adress → geokodning till koordinater. |
| Column-0 (unchecked/checked) | Finns i CSV men används **inte** idag – alla rader inkluderas. Om ni vill exkludera "unchecked" rader kan vi lägga till ett filter. |

CSV:n har **107 rader** (besöksbeskrivningar) som expanderas till **744 besök** (JSON) under ett 2-veckors planeringsfönster (2026-03-02 – 2026-03-15).

> **Planeringsfönster:** Vi rekommenderar **4 veckor** om er CSV innehåller besök med "Var 4:e vecka". Scriptet beräknar fönstret automatiskt baserat på längsta återkommande frekvensen. **Aktuella körningar:** som standard används 4-veckorsfönster (~1 486 besök); 2-veckorsfönster (744 besök) används vid behov. Nedanstående tabeller visar 2v-fönster med JSON-motsvarigheter.

### 2.1 Kunder och geografi

| Nyckeltal | CSV | JSON |
|-----------|-----|------|
| **Kunder** (unika Kundnr) | **15 st** (H015, H025 … H053) — **testdata: 15 av 81 Huddinge-kunder** | 15 st (unika location-koordinater: 14*) |
| **Område** | Huddinge – Segeltorp, Stuvsta, Flemingsberg, Visättra | Geocodade adresser (Nominatim) |

> *14 koordinater: H037 (Diagnosvägen 1F) och H038 (Diagnosvägen 4A) har olika adresser men geocodern löser dem till samma punkt. Optimerarens körtider hanterar detta korrekt – besök på samma koordinat har 0 restid.
>
> **Testdata:** Denna CSV innehåller endast **15 av 81** kunders besök. Därför kan resultat från nuvarande körningar (t.ex. få besök per skift, låg fälteffektivitet) delvis bero på den lilla datamängden — med full Huddinge-data (81 kunder) förväntar vi oss högre utnyttjande per skift och bättre nyckeltal. Verifieringen av mapping (tidsfönster, Dubbel, beroenden) gäller oavsett.

### 2.2 Slingor → vehicles och skift → shifts

CSV-kolumnen **Slinga** blir ett **vehicle** i JSON. Kolumnen **Schift** styr vilka **shifts** (arbetspass) varje vehicle har.

| Skift | CSV-slingor | CSV-rader | → JSON shifts (2v) | Tillåtna dagar | Tid |
|-------|-------------|-----------|---------------------|----------------|-----|
| **Dag** | 12* | 58 | 110 | mån–fre | 07:00 – 15:00 |
| **Helg** | 9 | 27 | 60 | lör–sön | 07:00 – 14:30 |
| **Kväll** | 6 | 22 | 84 | alla 7 dagar | 16:00 – 22:00 |
| **Totalt** | **26*** | **107** | **254** | | |

> *En Helg-slinga ("Helg 00 ⭐ Flempan 1") har även Dag-rader, därför 12 slingor med Dag-rader men 26 unika slingor totalt (1 mixed). Vehicle skapas per unik slinga med shifts för alla skifttyper i dess rader.
>
> 26 **basfordon** (en per unik Slinga). Scriptet kan lägga till Extra_Dag_/Extra_Kvall_-fordon vid behov, så antal vehicles i JSON kan överstiga 26. Varje vehicle har shifts per tillåten dag (t.ex. Dag-slinga → 10 shifts för mån–fre × 2v).

### 2.3 Besöksvolymer: CSV → JSON

| Nyckeltal | CSV | → JSON (2v) |
|-----------|-----|-------------|
| **Rader / besöksdefinitioner** | 107 rader | 107 → expanderas nedan |
| **Expanderade besök** (recurrence × dagar) | 107 rader × återkommande | **744 besök** |
| **…varav fristående besök** | 79 rader utan Dubbel | 504 besök |
| **…varav i besöksgrupper (Dubbel)** | 28 rader (14 par) | 240 besök i 116 grupper |
| **Besöksberoenden (dependencies)** | 39 rader med "Antal tim" | 236 (eller något färre efter automatisk borttagning av omöjliga) |
| **Automatiskt korrigerade beroenden** | — | 3 kappade + 2 borttagna + 38 felaktiga flexible_day-beroenden borttagna (se avsnitt 4.3) |
| **Genomsnittlig besökslängd** | 25 min (per CSV-rad) | ~21 min (per JSON-besök)* |
| **Total planerad tid** | 45 h (107 × 25 min) | ~255 h (744 × 21 min) |
| **Vehicles** | 26 slingor | 26 vehicles |
| **Shifts** | 3 skifttyper (Dag/Helg/Kväll) | 254 shifts |

> *Skillnad snittlängd: korta besök (Tillsyn 6 min) upprepas dagligen (7/vecka) och väger tungt i JSON-snittet, medan långa besök (Städ 150 min) sker var 4:e vecka. CSV-snittet räknar varje rad lika.

**Besöks-ID och namn i JSON:** Varje besök får **visit.id** på formen `kundid_r{rad}_{förekomst}` (t.ex. `H034_r38_1`) och **visit.name** som `kundid När på dagen Skift Insatser` (t.ex. `H034 Lunch Dag Bad/Dusch`) så att ni kan koppla tillbaka till CSV-rad och insats(er). Samma id/namn återfinns i optimerarens output så att ni kan verifiera att besöken stämmer.

**Konfirmerat:**
- **Flera besök samma dag (olika rader)** — t.ex. H034 Lunch Bad/Dusch + Lunch Måltid — skickas till ruttoptimeringen som separata besök; optimeringen **planerar dem i följd** automatiskt (samma fordon, ordning och tidsfönster).
- **En rad → flera besök över fönstret, men aldrig två på samma dag.** Pinnade rader: exakt ett besök per matchande datum. Flexible_day (optimeraren väljer dag): N besök per period med **minDelay ≥ 18 h** (eller CSV "Antal tim mellan besöken") mellan besöken från samma rad så att de hamnar på **olika dagar** — oavsett om perioden är vardagar (mån–fre), helg (lör–sön) eller varje dag. **Fördröjningar under 18 h mellan sådana förekomster är felaktiga** (då kan de hamna samma dag). Dessa återkommande besök ska planeras med tidsfönster för **perioden** (t.ex. 1 vecka månd 07–fred 22 eller sönd 22 beroende på skift), med hänsyn till tid på dagen (Morgon/Lunch/Kväll), och minDelay minst 18 h. Scriptet kapar aldrig minDelay under 18 h när ursprunglig fördröjning är ≥ 18 h.

### 2.4 Återkommande mönster: CSV → JSON (2v)

| Mönster (Återkommande) | CSV-rader | Besök/vecka | Fast/Optimeraren? | → JSON-besök (2v) |
|------------------------|-----------|-------------|-------------------|--------------------|
| Varje vecka, mån tis ons tor fre | 26 | 5 | **Fast** (pinnade) | 260 |
| Varje vecka, lör sön | 26 | 2 | **Fast** (pinnade) | 104 |
| Varje dag | 13 | 7 | **Fast** (pinnade) | 182 |
| Varje vecka, mån tis ons tor fre lör sön | 7 | 7 | **Fast** (= dagligt) | 98 |
| Varje vecka, 1 dag (ons, mån, tor, fre, lör) | 16 | 1 | Optimeraren väljer | 32 |
| Varje vecka, 2 dagar (tis fre, mån tor) | 5 | 2 | Optimeraren väljer | 20 |
| Varje vecka, 3 dagar (mån ons fre, mån tis tor…) | 4 | 3 | Optimeraren väljer | 24 |
| Varje vecka, 4 dagar (mån tis ons fre, mån tis ons tor) | 2 | 4 | Optimeraren väljer | 16 |
| Varannan vecka (tis, tor, fre, ons) | 6 | 0,5 | Optimeraren väljer | 6 |
| Var 4:e vecka (mån, tis) | 2 | 0,25 | Optimeraren väljer | 2 |
| **Totalt** | **107** | | | **744** |

### 2.5 Tidsfönster i JSON

| Typ | Antal besök | Beskrivning |
|-----|-------------|-------------|
| 1 tidsfönster (pinnad dag eller heldag) | 676 | Fasta dagar + besök med heldag (07–22) |
| Flera tidsfönster (flexible_day, Morgon/Lunch/Kväll) | 68 | Ett fönster per tillåten dag i perioden |

---

## 3. När ska besöket ske? (Tidsfönster)

### 3.1 Regel: Alla besök har flex (tid eller dag)

**Krav:** Varje besök ska ha antingen **tid-flex** (minStartTime ≠ maxStartTime inom samma dag) eller **dag-flex** (flera tidsfönster eller ett fönster som spänner flera dagar/veckor). Inget besök får ha exakt ett fönster med minStartTime = maxStartTime (noll flex).

- **Före=Efter=0:** Vi använder alltid **hela sloten** (Morgon 07–10:30, Lunch 11–13:30, Kväll 16–19, Heldag 07–22). Ingen undantag.
- **Före/Efter ifyllda:** Tidsfönster = starttid ± före/efter. Om beräkning av någon anledning ger min = max används sloten som säkerhetsnät.

**Verifiering:** Efter generering körs `_verify_all_visits_have_flex()` — om något besök har 0 flex skrivs inget JSON och scriptet avbryts med fel. Man kan även köra `scripts/verify_all_visits_have_flex.py <input.json>` på befintlig fil.

### 3.2 Tid på dagen: "När på dagen"

Vi mappar **När på dagen** till tre fasta tidsfönster:

| När på dagen (CSV) | Vi tolkar som | Tidsfönster (start–slut) |
|--------------------|----------------|---------------------------|
| Innehåller "morgon" | Morgon         | 07:00 – 10:30             |
| Innehåller "lunch"  | Lunch          | 11:00 – 13:30             |
| Innehåller "kväll"  | Kväll          | 16:00 – 19:00             |
| (tomt) + Skift Dag  | Skiftens fönster | 07:00 – 15:00 (månd–fred) |
| (tomt) + Skift Helg | Skiftens fönster | 07:00 – 14:30             |
| (tomt) + Skift Kväll| Skiftens fönster | 16:00 – 22:00             |
| (tomt / annat) utan matchande skift | Heldag (fritt) | 07:00 – 22:00             |

När **Före** och **Efter** är ifyllda använder vi **Starttid ± Före/Efter** inom sloten (t.ex. 07:05, Före 0, Efter 120 → 07:05–09:05). När **Före=Efter=0** använder vi **hela sloten** (t.ex. Morgon 07:00–10:30), så att "veckobesök morgon" får flex 3,5 h × antal dagar. För **tomt När på dagen** och **Skift = Dag** används skiftets fönster 07:00–15:00 (t.ex. H053 Inköp, Slinga "Dag 14 ⭐ Stuvsta 2", Varje vecka mån → månd–fred 07–15). *Slingans namn har inget med besökets dag att göra.* För tomt + Helg/Kväll används 07–14:30 respektive 16–22.

**Viktigt: flexible_day-besök (optimeraren väljer dag):** Om besöket har en period över flera dagar (t.ex. 1 vecka, 2 veckor) och ett specifikt tidsfönster (Morgon/Lunch/Kväll), skapar vi **ett separat tidsfönster per tillåten dag** i perioden. Så att tidsregeln gäller oavsett vilken dag optimeraren väljer. Besök med heldag (07–22) eller fasta dagar behöver bara ett enda fönster.

**Exempel från CSV:n:**

| Kundnr | Insats | När på dagen | Starttid | Före | Efter | → Tidsfönster |
|--------|--------|--------------|----------|------|-------|---------------|
| H015 | Tillsyn | Morgon | 07:05 | 0 | 120 | 07:05 – 09:05 (morgon) |
| H029 | Måltid, Social Samvaro | Lunch | 11:00 | 0 | 120 | 11:00 – 13:00 (lunch) |
| H026 | Avklädning, Personlig Hygien Kväll | kvällen Dubbel | 19:40 | 15 | 15 | 19:25 – 19:55 (kväll) |
| H029 | Tvätt | Morgon | 07:09 | 0 | 0 | **07:00 – 10:30** (hela morgon, flex 3,5 h × dagar) |
| H026 | Städ | *(tomt)* | 10:30 | – | – | 07:00 – 22:00 (heldag) |
| H037 | Bad/Dusch | *(tomt)* | 08:00 | 30 | 15 | 07:00 – 22:00 (heldag) |

> Notera: "Morgon Dubbel", "Lunch Dubbel", "kvällen Dubbel" tolkas som morgon/lunch/kväll + Dubbel-markering.

**Vänligen bekräfta:** Att dessa fönster stämmer (morgon/lunch/kväll + heldag 07–22 när fältet är tomt/annat).

---

### 3.3 Vilka dagar: fasta dagar vs "optimeraren väljer"

Om **dagen** är fast eller väljs av optimeraren beror på **Återkommande** och **Skift**:

#### Fasta dagar (pinnade)

Vi pinnar **endast** när veckodagarna i CSV utgör en **hel mängd**: alla vardagar (mån–fre), båda helgdagar (lör–sön), eller alla 7 (dagligt). Då skapas besök för varje matchande datum.

**Pinnas som fasta:**
- **"Varje dag"** → alla 7 dagar per vecka
- **"Varje vecka, mån tis ons tor fre"** → alla 5 vardagar
- **"Varje vecka, lör sön"** → båda helgdagar
- **"Varje vecka, mån tis ons tor fre lör sön"** → alla 7 = dagligt

#### Optimeraren väljer dag (flexible_day)

När veckodagarna är **partiella** (t.ex. "mån tis tor", "ons", "tis fre") eller **inga** veckodagar anges: solver väljer N dagar inom perioden (begränsat av Skift). Frekvensen (N besök/vecka) behålls; dagarna pinnas inte.

**Gäller för:**
- Enstaka dagar (t.ex. "Varje vecka, ons" → 1/vecka, solver väljer bland Dag=mån–fre)
- Delmängder (t.ex. "Varje vecka, mån ons fre" → 3/vecka, solver väljer 3 dagar)
- Varannan / var 3:e / var 4:e vecka
- **"Varje vecka" utan veckodagar** → 1 per vecka, solver väljer dag (mån–sön, begränsat av Skift)

**Skift** begränsar vilka dagar som är tillåtna:

| Skift (CSV) | Tillåtna dagar | Typiskt tidsintervall (skift) |
|-------------|-----------------|-------------------------------|
| Dag         | Endast mån–fre  | 07:00 – 15:00                 |
| Helg        | Endast lör–sön  | 07:00 – 14:30                 |
| Kväll       | Alla 7 dagar    | 16:00 – 22:00                 |

**Exempel från CSV:n (4v-fönster 2026-03-02 – 2026-03-29):**

| Kundnr | Insats | Återkommande | Skift | → Tolkning | Besök/4v |
|--------|--------|--------------|-------|------------|----------|
| H015 | Tillsyn | Varje vecka, mån tis ons tor fre | Dag | **Fast:** ett besök varje mån–fre | 20 |
| H015 | Tillsyn | Varje vecka, lör sön | Helg | **Fast:** ett besök varje lör + sön | 8 |
| H015 | Tillsyn | Varje dag | Kväll | **Fast:** ett besök varje dag | 28 |
| H034 | Avklädning | Varje vecka, mån tis ons tor fre lör sön | Kväll | **Fast:** alla 7 dagar (= dagligt) | 28 |
| H027 | Bad/Dusch | Varje vecka, mån | Dag | **Optimeraren väljer:** 1/vecka, vilken vardag som helst | 4 |
| H034 | Bad/Dusch | Varje vecka, mån tis tor | Dag | **Optimeraren väljer:** 3/vecka, vilka 3 vardagar som helst (ej pinnade mån/tis/tor) | 12 |
| H015 | Städ | Varannan vecka, tis | Dag | **Optimeraren väljer:** 1/2v-block, vilken vardag som helst | 2 |
| H026 | Städ | Var 4:e vecka, mån | Dag | **Optimeraren väljer:** 1/4v-block, vilken vardag som helst | 1 |

**OBS:** Vi pinnar endast när veckodagsmängden är **hel** (mån–fre, lör–sön eller alla 7). Vid **partiella** veckodagar (t.ex. "mån tis tor", "ons", "tis fre") väljer optimeraren vilka N dagar inom perioden; vi pinnar inte till de specifika veckodagarna.

**Vänligen bekräfta:** För fall där optimeraren väljer dag – är det korrekt att vi bara begränsar via Skift (Dag = vardagar, Helg = helg, Kväll = vilken dag som helst) och inte via den exakta veckodagstexten i Återkommande?

---

## 4. Vilka besök hör ihop?

### 4.1 Samma tid, samma dag: Dubbel (besöksgrupp)

- **CSV-kolumn:** **Dubbel**
- **Regel:** Alla rader med **samma Dubbel-värde** som hamnar på **samma datum** behandlas som en **besöksgrupp**.
- **Effekt:** Optimeraren måste planera dem **samtidigt** (samma ankomstfönster). Vanligt användning: två vårdare till en brukare (dubbelbesök).

**Exempel från CSV:n:**

| Kundnr | Insats | Dubbel | Slinga | Besökstyp | → Tolkning |
|--------|--------|--------|--------|-----------|------------|
| H026 | Egenvård, Personlig Hygien Morgon… | **8** | Dag 14 ⭐ Stuvsta 2 | Hemtjänst | ↘ Dessa två |
| H026 | Egenvård, Personlig Hygien Morgon… | **8** | Dag 11 ⭐ Snättringe | Dubbelbemanning | ↗ ska ske **samtidigt** |
| H035 | Förflyttning | **2** | Kväll 03 ⭐ Visättra | Hemtjänst | ↘ Dessa två |
| H035 | Toalettbesök | **2** | Kväll 02 ⭐ Kvarnen | Dubbelbemanning | ↗ ska ske **samtidigt** |

> I CSV:n finns **14 Dubbel-grupper**, alla med exakt **2 rader** per grupp (= 2 vårdare till samma kund).

**Vänligen bekräfta:** När Dubbel är ifyllt avser ni att dessa besök ska ske tillsammans, samma tid samma dag.

---

### 4.2 Ordning och minsta mellanrum: "Antal tim mellan besöken"

**En CSV-rad = en insats** (en insatstyp). En insats kan vara ett eller flera besök för kunden över 1 dag, 1–4 veckor, återkommande.

- **CSV-kolumn:** **Antal tim mellan besöken**
- **Same-day-kedja (måltider: frukost → lunch):** Olika rader (insatser) för samma kund, samma dag. Vi lägger visitDependency från föregående slot (t.ex. Morgon) till nästa (t.ex. Lunch) **endast när** den senare besökets rad har "Antal tim mellan besöken" ifyllt med ett **kort** värde (≤ 12 h). Vi använder värdet **som det är** (t.ex. PT3H30M); ingen subtraktion. Om det inte får plats mellan de två besökens tidsfönster kapar vi (eller tar bort beroendet). Så frukost kommer före lunch med önskat mellanrum.
- **Lång delay = endast spridning (samma insats):** Om "Antal tim mellan besöken" är **långt** (t.ex. 48 h) använder vi det **bara** mellan förekomster av **samma** insats (samma rad, flexible_day, vecka 2, 3, 4). Vi lägger **inte** in same-day-beroende från andra insatser (t.ex. lunch) till denna, så t.ex. dusch (48 h) kan placeras **direkt i anslutning till** lunch; klustring sker då via FSR-vikter.
- **Delay endast mellan samma insats över veckor (spridning):** När en insats (en CSV-rad) har **flera flexible_day-besök** i samma period (t.ex. 2 eller 3 duschar per vecka) lägger vi in **spridnings-**visitDependencies: förekomst 1 → 2 → 3 med minDelay från "Antal tim mellan besöken" (eller **18 h** standard) så att de hamnar på olika dagar. Samma rad, samma period endast.
- **Ett besök per period (t.ex. 1× tvätt/vecka):** Inget spridningsberoende — bara ett besök att placera. När på dagen och Skift begränsar.
- **Effektiv delay för spridning:** För **spridning** (samma insats, flexible_day) sätter vi **effektiv minDelay = intervall − föregående besöks tidsfönsterlängd**, golv 18 h. Same-day-kedjor använder **inte** denna subtraktion utan CSV-värdet som det är.

**Exempel från CSV:n:**

| Kundnr | Insats | Antal tim | Återkommande | → Tolkning |
|--------|--------|-----------|--------------|------------|
| H026 | Bad/Dusch | 48 timmar | Varje vecka, tis fre | Spridning (samma insats): min 48 h mellan 2 duschar/vecka → olika dagar |
| H038 | Bad/Dusch | 36 timmar | Varje vecka, mån tis fre | Spridning (samma insats): min 36 h mellan 3 duschar/vecka |
| H015 | Tillsyn / Dusch | *(valfritt)* | Varje vecka, mån–fre | Ingen dependency mellan Tillsyn och Dusch; klustring via vikter om önskat |
| H029 | Tvätt | *(tomt)* | Varannan vecka, tor | Ett besök per period — ingen dependency |

**Bekräftat:** visitDependencies endast mellan **samma insats** (samma rad), **flexible_day**, flera besök per period. Olika insatser för samma kund: ingen hård delay; klustring via FSR-config-vikter.

---

### 4.3 Åtgärdade valideringar (automatiska korrigeringar)

Vi har identifierat fall där **"Antal tim mellan besöken" är större** än vad som ryms mellan tidsfönstren. Då kan inget av besöken planeras – optimeraren hittar ingen giltig tid. Vi korrigerar dessa automatiskt.

#### Problem: mellanrum som inte ryms

**Konkreta exempel från genererad JSON (verifierat mot CSV och input):**

| Besök A (id) | Fönster A | Längd A | → Krav → | Besök B (id) | Fönster B | Problem |
|-------------|-----------|---------|----------|-------------|-----------|---------|
| H029_1 | 07:09 (fast) | 1 min | 3,5 h | H029_2 | 07:15 – 08:45 | Besök A klart 07:10 + 3h30 = **10:40** → efter B:s fönster (08:45). |
| H034_4 | 11:25 – 12:25 | 30 min | 3,5 h | H034_5 | 11:40 – 13:00 | Besök A klart tidigast 11:55 + 3h30 = **15:25** → efter B:s fönster (13:00). |
| H038_2 | 12:00 – 13:00 | 25 min | 3,5 h | H038_3 | 11:00 – 12:50 | Besök A klart 12:25 + 3h30 = **15:55** → helt utanför B:s fönster. |

**Vår korrigering (3 kappade + 2 borttagna):**
- Vi beräknar det **maximala möjliga mellanrummet** mellan besökens tidsfönster.
- Om angivet mellanrum är för stort, **kortar vi det** automatiskt (med marginal).
- H029: 3h30 → **1h46** (kapat). H034: 3h30 → **1h20** (kapat, 2 par).
- H038: inget mellanrum ryms → **beroendet borttaget** (2 par).

> **Rekommendation till Attendo:** Minska "Antal tim mellan besöken" till max **2 timmar** för besök samma dag (Morgon → Lunch eller Lunch → Kväll), så slipper ni automatiska korrigeringar. Om inget ändras korrigerar vi ändå – det påverkar inte kvaliteten.

#### Problem: spridningsberoenden utanför planeringsfönstret

Spridning över dagar (t.ex. 48 h mellan duschar) begränsas automatiskt till planeringsfönstret. Om kedjans sista besök hamnar utanför fönstret kan det inte planeras. Vi kortar kedjan så att alla besök ryms.

#### Problem: spridningsberoenden blandat med samma-dags-kedjan (åtgärdat)

**Bakgrund:** Besök som "optimeraren väljer dag" (flexible_day) har ett `date_iso` satt till periodens startdag (måndag), men besöket kan i praktiken hamna vilken dag som helst inom perioden. "Antal tim mellan besöken" (t.ex. 36 h) anger **spridningen mellan duschbesök av samma typ** — inte mellanrummet till morgon- eller lunchbesöket samma dag.

**Problemet:** Scriptet blandade in dessa flexible_day-besök i **samma-dags-kedjan** (morgon → lunch → kväll), och använde spridningsvärdet (36 h) som mellanrum till föregående fasta besök. Detta skapade omöjliga beroenden:

| Kedja (före fix) | Problem |
|---|---|
| `H034_1` (fast mån 08:12) → `H034_2` (flex mån–fre, **PT36H!**) → `H034_3` (PT36H) → `H034_4` (PT36H) → `H034_5` (fast mån 11:40) | 36 h × 3 = 108 h minimum — men fönstret mån–fre = 120 h. Dessutom kräver `H034_5` att `H034_4` är klar + 1,5 h **samma måndag**, men `H034_4` kan hamna på fredag. |
| `H038_6` (flex) → `H038_7` (PT36H) → `H038_8` (PT36H) → `H038_9` (PT36H) → med fast lunchbesök i kedjan | Samma mönster: 36 h-kravet från ett fristående morgonbesök tvingar hela kedjan framåt. |
| `H053_1` (fast mån) → `H053_2` (flex, PT36H) → `H053_3` → `H053_4` → `H053_5` (fast mån lunch) | Samma: spridningskravet (36 h) felaktigt tolkat som mellanrum till morgonbesöket. |

**Åtgärd:** Flexible_day-besök **exkluderas nu från samma-dags-kedjan**. De har bara **spridningsberoenden** (mellan sina egna förekomster, t.ex. dusch 1 → dusch 2 → dusch 3 med 36 h mellanrum). Fasta morgon- och lunchbesök kopplas fortfarande till varandra som förut (med 3,5 h mellanrum).

| Resultat (efter fix) | |
|---|---|
| Spridningsberoenden (≥18 h, mellan duschar av samma typ) | 48 st |
| Samma-dags-beroenden (morgon → lunch, ≤ 3,5 h) | 188 st |
| Totalt | **236** beroenden (eller färre om några kappas bort som helt omöjliga; ned från 274 – 38 felaktiga flexible_day borttagna) |

Vi har också lagt till en **kedjevalideringskontroll**: om N besök med (N−1) fördröjningar + servicetid inte ryms i det tillgängliga tidsfönstret, kapas fördröjningen automatiskt till det maximalt möjliga (men aldrig under 18 h, vilket garanterar olika dagar).

#### Problem: Noll Före/Efter med Morgon/Lunch/Kväll gav ingen slot-flex – åtgärdat

**Bakgrund:** Besök med **När på dagen = Morgon** (eller Lunch/Kväll) och **Före=Efter=0** tolkades som exakt starttid (t.ex. 07:09–07:09), så att ett veckobesök "vilken vardag som helst morgon" fick 12 stycken 1-minutersfönster i stället för morgonfönstret 07:00–10:30 per dag. Rätt tolkning: **morgon = hela morgonfönstret** (07–10:30), dvs flex 3,5 h × 5 vardagar = **17,5 h**.

**Åtgärd:** När Före=Efter=0 och besöket har en **slot** (Morgon, Lunch eller Kväll), använder vi nu **hela sloten** som tidsfönster:
- Morgon: 07:00–10:30 (max start 10:30 − längd)
- Lunch: 11:00–13:30 (max start 13:30 − längd)
- Kväll: 16:00–19:00 (max start 19:00 − längd)

Då får t.ex. H029 Tvätt (1 min, Morgon, "Varannan vecka, tor") ett fönster **07:00–10:29** på varje tillåten dag i stället för 07:09–07:09.

---

## 5. Hur ofta? Återkommande (Återkommande)

Vi läser **Återkommande** och får fram:

1. **Hur många gånger** per vecka (eller per 2/3/4 veckor) besöket ska ske.
2. **Fasta dagar** vs **optimeraren väljer dag**.

### Regler:

- **"Varje dag"** → ett besök per kalenderdag (fast, pinnad).
- **"Varje vecka, mån tis ons tor fre"** → fasta vardagar, 5 per vecka (pinnad).
- **"Varje vecka, lör sön"** → fasta helgdagar, 2 per vecka (pinnad).
- **"Varje vecka, mån tis ons tor fre lör sön"** → alla 7 dagar = dagligt (pinnad).
- **"Varje vecka"** (utan veckodagar) → **1 besök per vecka**, optimeraren väljer dag inom Skift (mån–sön). Detta är en fallback om framtida CSV:er saknar veckodagar.
- **"Varje vecka, ons"** eller **"Varje vecka, mån"** → 1 besök per vecka, optimeraren väljer bästa dag inom Skift.
- **"Varje vecka, mån ons fre"** eller liknande (2–4 dagar) → N besök per vecka, optimeraren väljer N dagar inom Skift.
- **"Varannan vecka, tis"** → 1 besök per 2-veckorsblock, optimeraren väljer dag.
- **"Var 3:e vecka"** → 1 besök per 3-veckorsblock.
- **"Var 4:e vecka, mån"** → 1 besök per 4-veckorsblock, optimeraren väljer dag.

**Exempel från CSV:n med expansion (4v-fönster 2026-03-02 – 2026-03-29):**

| Kundnr | Insats | Återkommande (CSV) | Vi tolkar | Fast/Optimeraren? | Besök i 4v |
|--------|--------|--------------------|-----------|-------------------|------------|
| H015 | Tillsyn | Varje dag | 1/dag | Fast: varje dag | **28** |
| H034 | Avklädning | Varje vecka, mån tis ons tor fre lör sön | 7/vecka | Fast: alla dagar | **28** |
| H029 | Måltid, Personlig Hygien… | Varje vecka, mån tis ons tor fre | 5/vecka | Fast: mån–fre | **20** |
| H029 | Måltid, Social Samvaro | Varje vecka, lör sön | 2/vecka | Fast: lör–sön | **8** |
| H034 | Bad/Dusch | Varje vecka, mån tis tor | 3/vecka | Optimeraren väljer 3 vardagar | **12** |
| H053 | Bad/Dusch | Varje vecka, mån ons fre | 3/vecka | Optimeraren väljer 3 vardagar | **12** |
| H038 | Bad/Dusch | Varje vecka, mån tis fre | 3/vecka | Optimeraren väljer 3 vardagar | **12** |
| H026 | Bad/Dusch | Varje vecka, tis fre | 2/vecka | Optimeraren väljer 2 vardagar | **8** |
| H027 | Bad/Dusch | Varje vecka, mån | 1/vecka | Optimeraren väljer 1 vardag | **4** |
| H037 | Bad/Dusch | Varje vecka, ons | 1/vecka | Optimeraren väljer 1 vardag | **4** |
| H015 | Städ | Varannan vecka, tis | 1/2v | Optimeraren väljer 1 vardag i 2v | **2** |
| H029 | Städ | Varannan vecka, tis | 1/2v | Optimeraren väljer 1 vardag i 2v | **2** |
| H026 | Städ | Var 4:e vecka, mån | 1/4v | Optimeraren väljer 1 vardag i 4v-block | **1** |

### 5.1 Kritisk insats (Kritisk insats Ja/nej)

Vi läser kolumnen **Kritisk insats Ja/nej**: **Ja** → true, tomt eller annat → false. Värdet används i vår pipeline; i dag mappar vi det inte till ett särskilt fält i Timefold-modellen (t.ex. pinningRequested) men reserverar det för framtida användning. **Vänligen bekräfta:** Ska "Ja" betyda att besöket ska pinnas till angiven dag när tillämpligt?

### 5.2 Planeringsfönster och längsta återkommande

Scriptet beräknar planeringsfönstret automatiskt:
- **Start:** Måndag samma vecka som scriptet körs.
- **Slut:** Start + längsta återkommande frekvens i CSV:n.
- **Denna CSV:** Längsta = "Var 4:e vecka" → **28 dagar** (4 veckor).

Om fönstret anges manuellt och är kortare än längsta återkommande varnar scriptet:
```
WARNING: planning window (14d) shorter than longest recurrence (28d). Recommend --end-date 2026-03-29
```

**Varför 4 veckor:** Med 2 veckor fönster för 4-veckorsbesök (H026, H039 Städ) får besöket en 14-dagarsperiod att placeras inom, trots att det egentligen ska ske var 4:e vecka. Med 4 veckor blir det korrekt: besöket placeras en gång inom hela 4-veckorsperioden.

---

## 6. Snabb checklista

Ni kan använda denna tillsammans med er grupp:

- [ ] **När på dagen:** Morgon 07–10:30, Lunch 11–13:30, Kväll 16–19; tomt/annat = heldag 07–22.
- [ ] **Skift:** Dag = mån–fre, Helg = lör–sön, Kväll = alla dagar.
- [ ] **Dubbel:** Samma värde = samma besöksgrupp = ska ske samtidigt, samma dag. (14 grupper × 2 rader i CSV:n.)
- [ ] **Antal tim mellan besöken:** Minsta mellanrum mellan besök. Tomt: samma dag = inget mellanrum; flera besök/period = 18 h standard. Ett besök/period = inget dependency. Vi korrigerar automatiskt om angivet mellanrum inte ryms (se avsnitt 4.3).
- [ ] **Återkommande:**
  - Fast (pinnad): "Varje dag", "mån tis ons tor fre", "lör sön", "mån tis ons tor fre lör sön".
  - Optimeraren väljer: alla andra mönster – vi behåller frekvensen men optimeraren väljer dagar inom Skift.
  - "Varje vecka" utan veckodagar → 1 per vecka (fallback).
- [ ] **Planeringsfönster:** Automatiskt 4 veckor (matchar längsta "Var 4:e vecka"). Start = måndag samma vecka.
- [ ] **Volym (2v):** 744 besök, ~255 timmar, 15 kunder, 26 slingor (→ minst 26 vehicles; kan bli fler vid tillägg av extra skift). **(4v):** ~1 486 besök, ~510 timmar.

Om ni vill ändra någon regel (t.ex. andra fönstertider eller när dagar ska vara fasta), skriv det här så tar vi det i konverteringen.

---

## 7. Köra optimering (solve)

För att köra optimeringen (submit input till Timefold och hämta lösning) krävs en **Timefold API-nyckel**. Test-tenant-nyckel, exakt kommando (inkl. `--configuration-id ""` för test-tenant) och pipeline-steg (solve → fetch → metrics) beskrivs i **Cursor-agenten tf-fsr-prototype** (filer under `beta-appcaire/.cursor/agents/tf-fsr-prototype.md`). Samma kommandon används från `be-agent-service/recurring-visits/scripts/` (t.ex. `submit_to_timefold.py solve <input.json> --wait --save <output-dir>`).

---

## 8. Öppna frågor

- **Kan vissa besök få friare "när på dagen"?** T.ex. kanske inte måltider, tillsyn, toalett, men kanske dusch. Det ger effektivare scheman. Vilka insatstyper kan få heldagsfönster (07–22) i stället för morgon/lunch/kväll?
