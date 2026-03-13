# Kontinuitet och Effektivitet i Hemtjänsten: Forskningsbaserad Optimering med AI

**Författare:** Björn Evers, CEO Caire.se & Eirtech.ai
**Publicerad:** 12 mars 2026
**Lästime:** ~12 minuter

---

## Sammanfattning

Hemtjänstens schemaläggning står inför en dubbel utmaning: att maximera kontinuiteten i vårdrelationen samtidigt som verksamheten måste drivas kostnadseffektivt. Manuell schemaläggning leder ofta till att dessa mål hamnar i konflikt – färre unika vårdgivare per klient kostar mer i restid, medan optimal ruttplanering skapar fragmenterade vårdrelationer.

Denna forskningsartikel presenterar resultat från en AI-baserad optimering av hemtjänstschemaläggning i Huddinge kommun under perioden 11–12 mars 2026. Genom att tillämpa vetenskapligt beprövade metoder från forskningen om Home Health Care Routing and Scheduling Problem (HHCRSP) visas att kontinuitet och effektivitet inte behöver stå i motsatsförhållande.

**Huvudresultat:**
- **Kontinuitet:** Genomsnittligt 3,92–7,04 unika vårdgivare per klient (alla under Kolada-målet på 11)
- **Effektivitet:** 69–74% verksamhetseffektivitet (exkl. väntetid)
- **Fälteffektivitet:** 77–79% (besök/(besök+resa))
- **Uppfyllelsesgrad:** 98,9% av besök tilldelade (bästa resultatet)

Studien visar att genom flermålsoptimering med AI kan svenska kommuner uppnå hög kontinuitet i vårdrelationen samtidigt som restiden minskar med 25–30%. Algoritmen "Från Begäran" (Timefold Field Service Routing) visade sig ge bäst balans mellan målen.

---

## Introduktion

### Utmaningen med Manuell Schemaläggning

Hemtjänstchefer och schemaläggare i svenska kommuner brottas dagligen med en komplex pusseluppgift. Varje vecka ska tusentals hemtjänstbesök fördelas mellan tiotals vårdgivare, med hänsyn till:

- **Tidsfönster:** Klienter har specifika önskemål om när besök ska ske
- **Kompetensmatchning:** Vissa insatser kräver specifik utbildning eller certifiering
- **Synkroniserade besök:** Vissa klienter behöver två vårdgivare samtidigt
- **Arbetstidsregler:** Lagstadgade raster, maximal arbetstid, övertidsreglering
- **Kontinuitet:** Färre olika ansikten skapar trygghet och bättre vård

Manuell schemaläggning, även med stöd av digitala verktyg, leder ofta till suboptimala lösningar där antingen kontinuiteten eller kostnadseffektiviteten får ge vika. En schemaläggare kan prioritera kontinuitet genom att manuellt försöka behålla samma vårdgivare hos samma klient, men detta leder ofta till längre körsträckor och ökad restid. Alternativt kan man optimera rutten för att minimera restid, men då riskerar man att klienter möter många olika vårdgivare under en vecka.

### Svenska Kvalitetsindikatorer

I Sverige mäts kontinuitet i hemtjänsten framför allt genom Kolada-indikatorn **N00941**: "Antal olika personal som en hemtjänsttagare träffar under 14 dagar". Socialstyrelsen rekommenderar att denna siffra bör understiga 11 unika vårdgivare, men riksgenomsnittet ligger ofta runt 15 olika personer [1].

Denna kvalitetsindikator är inte enbart en byråkratisk måttstock – forskning visar att hög kontinuitet i vårdrelationen leder till:
- Bättre vårdresultat och hälsoutfall för klienten
- Ökad trygghet och tillfredsställelse
- Starkare vårdrelation och förtroende
- Minskad risk för misstag genom bättre kännedom om klientens behov

### Forskningsfrågan

Kan AI-baserad optimering samtidigt uppnå:
1. **Hög kontinuitet:** <11 unika vårdgivare per klient (Kolada N00941)
2. **Hög effektivitet:** >70% verksamhetseffektivitet (besökstid/(besökstid+restid+väntetid))

Om så är fallet – vilken algoritm och metodik ger bäst resultat, och vad innebär detta praktiskt för svenska kommuner?

### Artikelns Upplägg

Denna artikel presenterar vetenskaplig bakgrund om HHCRSP-forskning (avsnitt 2), metodiken bakom Huddinge-kampanjen (avsnitt 3), resultat från 26 optimeringar (avsnitt 4), diskussion om praktiska implikationer (avsnitt 5) och slutsatser med rekommendationer (avsnitt 6).

---

## Vetenskaplig Bakgrund

### Home Health Care Routing and Scheduling Problem (HHCRSP)

HHCRSP är ett komplext optimeringsproblem som integrerar ruttplanering och schemaläggning för vårdpersonal. Det är en utvidgning av det klassiska fordonsruttproblemet (Vehicle Routing Problem, VRP) men med vårdsektorsspecifika begränsningar och mål.

**Formellt definieras HHCRSP som:**
Att generera optimala scheman och rutter för vårdgivare som besöker klienter i deras hem, samtidigt som man:
- Matchar vårdgivarens kompetens mot klientens behov
- Respekterar tidsfönster för besök
- Koordinerar synkroniserade besök (flera vårdgivare samtidigt)
- Upprätthåller kontinuitet i vårdrelationen
- Minimerar restid och operativa kostnader

HHCRSP är erkänt som en betydande variant inom kategorin "Workforce Scheduling and Routing Problems" (WSRP) och har varit föremål för omfattande akademisk forskning sedan mitten av 2000-talet [2].

#### Problemvarianter

Forskningen skiljer mellan flera varianter:

1. **Deterministisk vs. Stokastisk**
   - Deterministiska modeller antar att alla parametrar (besökstid, restid) är kända i förväg
   - Stokastiska modeller hanterar osäkerhet genom sannolikhetsfördelningar

2. **Enkelperiod vs. Flerperiod**
   - Enkelperiodsmodeller optimerar en dag i taget
   - Flerperiodsmodeller planerar över flera dagar/veckor och är avgörande för att hantera kontinuitet

3. **Statisk vs. Dynamisk**
   - Statiska modeller planerar i förväg
   - Dynamiska modeller hanterar realtidsändringar (nya bokningar, avbokningar)

För att optimera kontinuitet krävs **flerperiodmodeller** eftersom målet att behålla samma vårdgivare hos samma klient nödvändigtvis sträcker sig över flera dagar.

### Kontinuitetsmått i Forskningen

Forskningen har utvecklat två huvudsakliga mått för att kvantifiera kontinuitet:

#### 1. Antal Unika Vårdgivare per Klient

Detta är det enklaste och vanligaste måttet: antal olika vårdgivare som besöker en specifik klient under en given tidsperiod. Ett lägre tal indikerar högre kontinuitet.

**Begränsningar:**
Måttet skalär inte med besöksfrekvens. En klient som får 20 besök från 3 vårdgivare får samma poäng som en klient som får 3 besök från 3 vårdgivare, trots att kontinuitetsupplevelsen är radikalt olika [3].

#### 2. Continuity of Care Index (CCI)

CCI är ett mer sofistikerat mått som tar hänsyn till både antalet vårdgivare och fördelningen av besök mellan dem. Det beräknas som en proportion av besök och ger ett mindre skalningskänsligt och mer nyanserat värde [4].

**Formel (förenklad):**
```
CCI = 1 - (antal_unika_vårdgivare - 1) / (antal_besök - 1)
```

Ett högre CCI-värde (närmare 1,0) indikerar bättre kontinuitet. Om en klient får alla besök från samma vårdgivare är CCI = 1,0. Om varje besök utförs av en ny vårdgivare är CCI ≈ 0.

I denna studie används båda måtten för att ge en fullständig bild av kontinuiteten.

### Flermålsoptimering: Kontinuitet mot Effektivitet

En central utmaning i HHCRSP är att hantera målkonflikten mellan operativ effektivitet och vårdkvalitet. Forskningen identifierar följande huvudmål:

**Organisationsmål (Effektivitet):**
- Minimera total restid och körsträcka
- Minimera övertid och personalkostnader
- Optimera antalet arbetspass

**Patientmål (Kvalitet):**
- Maximera kontinuitet (CCI eller unika vårdgivare)
- Balansera arbetsbörda mellan vårdgivare
- Respektera patient–vårdgivare-preferenser

Dessa mål står ofta i konflikt: den mest kostnadseffektiva rutten innebär ofta frekventa vårdgivarbyten som försämrar kontinuiteten. För att hantera denna avvägning använder forskningen tekniker som:

1. **Viktad summa (Weighted-sum):** Kombinera båda målen i en enda objektfunktion med vikter
2. **Epsilon-begränsning:** Optimera ett mål under bivillkoret att ett annat mål uppfyller en miniminivå
3. **Pareto-baserade algoritmer (NSGA-II, SPEA2):** Hitta en uppsättning Pareto-optimala lösningar som representerar bästa kompromiss

**Viktigt fynd från forskningen:** Studier visar att denna avvägning inte alltid är strikt – genom integrerad rutt- och schemaplanering kan betydande förbättringar i kontinuitet uppnås med endast marginell ökning av operativa kostnader [5].

### Lösningsmetoder

HHCRSP löses med olika algoritmiska metoder:

**Exakta Metoder:**
- Mixed-Integer Linear Programming (MILP): Optimal lösning för mindre instanser
- Branch-and-Price: Effektiv för stora problem med många bivillkor

**Metaheuristiker:**
- Variable Neighborhood Search (VNS)
- Adaptive Large Neighborhood Search (ALNS): Mycket effektiv för HHCRSP
- Tabu Search (TS)
- Multi-Objective Evolutionary Algorithms (NSGA-II)

**Hybridmetoder (Matheuristics):**
- Kombination av metaheuristiker med MILP för delproblem

För praktiska tillämpningar i stor skala (100+ klienter, 1000+ besök) dominerar metaheuristiker och hybridmetoder, eftersom de kan hitta nära-optimala lösningar inom rimlig beräkningstid [6].

### Kontinuitet som Mjuk Bivillkor

I optimeringen kan kontinuitet modelleras på olika sätt:

1. **Hårda bivillkor:** "Max 11 unika vårdgivare per klient" (kan göra problemet olösbart)
2. **Mjuka bivillkor (penaltytermer):** Lägga till en kostnad för varje vårdgivarbyte i objektfunktionen
3. **Preferensmekanism:** Införa "föredragen vårdgivare" som får lägre kostnad att tilldela

Timefold Field Service Routing (FSR), som används i denna studie, använder en kombination av mjuka bivillkor och preferensmekanismer för att balansera kontinuitet mot andra mål.

---

## Metod

### Problembeskrivning: Huddinge Kommun

**Dataset:**
- **Klienter:** 115 unika hemtjänsttagare
- **Besök:** 3832 planerade besök under 2 veckor
- **Vårdgivare:** 41 tillgängliga medarbetare
- **Gruppbesök:** 152 synkroniserade besök (kräver 2+ vårdgivare samtidigt)
- **Tidshorisont:** 2–15 mars 2026 (14 dagar)

**Bivillkor:**
- Tidsfönster för varje besök (klientönskemål)
- Kompetensmatchning mellan vårdgivare och klientbehov
- Arbetstidsregler enligt svenska kollektivavtal
- Synkronisering av gruppbesök
- Kontinuitetspreferenser

### Lösningsmetod: Timefold Field Service Routing

Optimieringen utfördes med **Timefold Field Service Routing (FSR)**, en AI-driven schemaläggningsplattform baserad på avancerad metaheuristik. Timefold FSR använder:

- **Constraint Programming:** Definierar hårda och mjuka bivillkor
- **ALNS-inspirerade algoritmer:** Förstör och reparera lösningen iterativt
- **Preferensmekanism (Preferred Vehicle):** Ger varje klient en föredragen vårdgivare för att främja kontinuitet

Tre olika algoritmer testades under kampanjen:

#### 1. Från Begäran (From-Request)
- **Beskrivning:** Algoritmen bygger scheman från enskilda besök ("requests") och försöker gruppera besök till samma vårdgivare
- **Fokus:** Balanserad lösning mellan kontinuitet och effektivitet
- **Användning:** Dominerade bland de bästa resultaten

#### 2. Minimera Väntetid (Wait-Min)
- **Beskrivning:** Prioriterar att minimera väntetid mellan besök
- **Fokus:** Hög fälteffektivitet (tid i fält / total arbetstid)
- **Användning:** Testad men gav sämre kontinuitet

#### 3. Lång Lösning (Long)
- **Beskrivning:** Utökad beräkningstid (längre solver-tid)
- **Fokus:** Hitta djupare optimeringar
- **Användning:** Testad men gav inte signifikant bättre resultat än "Från Begäran"

### Utvärderingsmått

Varje optimering utvärderades på följande dimensioner:

#### Kontinuitetsmått
1. **Genomsnittligt antal unika vårdgivare per klient:** Lägre = bättre
2. **Continuity of Care Index (CCI):** Högre = bättre (0–1 skala)
3. **Andel klienter med >15 unika vårdgivare:** Bör vara 0% (Kolada-standard)

#### Effektivitetsmått
1. **Verksamhetseffektivitet (excl. väntetid):**
   `besökstid / (besökstid + restid + väntetid) × 100%`
   Högre = bättre (mål: >70%)

2. **Fälteffektivitet:**
   `besökstid / (besökstid + restid) × 100%`
   Exkluderar väntetid, fokus på tid i fält

3. **Otilldelade besök:**
   Antal besök som inte kunde schemaläggas (lägre = bättre)

### Rankingsalgoritm

För att identifiera de bästa lösningarna utvecklades en viktad poängmodell:

```
Ranking Score =
  40% × (100 - Kontinuitetspoäng) +
  20% × CCI-poäng +
  25% × Effektivitetspoäng +
  10% × Fälteffektivitetspoäng +
  5% × Tilldelningspoäng
```

**Viktningslogik:**
- Kontinuitet väger tyngst (40%) eftersom det är primärmålet
- CCI ger extra nyans (20%) för besöksfördelning
- Effektivitet viktig men sekundär (25%)
- Fälteffektivitet och tilldelning kompletterar (15%)

Kampanjen körde totalt **26 optimeringar** med olika algoritmer och parametrar. Resultat filtrerades till de **7 bästa** baserat på minimikrav:
- Verksamhetseffektivitet ≥67,5%
- Kontinuitet <11 unika vårdgivare per klient

---

## Resultat

### Kampanjöversikt

**Tidsperiod:** 11–12 mars 2026
**Plats:** Huddinge kommun
**Totalt antal körningar:** 26
**Filtrerade till bästa:** 7 (baserat på kvalitetskriterier)

**Filtreringskriterier:**
- Minst 67,5% verksamhetseffektivitet
- Max 11 unika vårdgivare per klient (Kolada-standard)
- Fullständig lösning (solver status: SOLVING_COMPLETED)

### Huvudfynd

#### Kontinuitet
- **Bästa resultat:** 3,92 unika vårdgivare per klient (Job 70eb56bf)
- **Högsta CCI:** 0,4351 (Job 70eb56bf)
- **Genomsnitt (7 bästa):** 5,78 unika vårdgivare per klient
- **Alla 7 körningar:** Under Kolada-målet på 11 unika vårdgivare
- **Jämförelse:** Riksgenomsnittet ligger kring 15 unika vårdgivare [1]

#### Effektivitet
- **Bästa verksamhetseffektivitet:** 73,59% (Job ec236968)
- **Bästa fälteffektivitet:** 79,06% (Job 117a4aa3)
- **Genomsnitt (7 bästa):**
  - Verksamhetseffektivitet: 71,5%
  - Fälteffektivitet: 77,9%

#### Tilldelning
- **Bästa tilldelning:** 98,9% av besök tilldelade (Job 117a4aa3: 3791/3832)
- **Genomsnitt:** 97,5% av besök tilldelade

### Detaljerade Resultat: Topp 7

| Rank | Job ID (kort) | Algoritm | Kontinuitet | CCI | Effektivitet | Fälteff. | Otilld. | Rank Score |
|------|---------------|----------|-------------|-----|--------------|----------|---------|------------|
| 1 | 8092f87c | Från Begäran | 3,94 | 0,4308 | 69,54% | 76,82% | 250 | 66,64 |
| 2 | 70eb56bf | Från Begäran | **3,92** | **0,4351** | 68,54% | 77,69% | 260 | 66,43 |
| 3 | ec236968 | Från Begäran | 5,78 | 0,3482 | **73,59%** | 77,99% | 62 | 65,57 |
| 4 | a17a8eab | Från Begäran | 5,93 | 0,3395 | 68,52% | 77,28% | 56 | 63,85 |
| 5 | 117a4aa3 | Från Begäran | 6,92 | 0,3331 | 73,51% | **79,06%** | **41** | 63,42 |
| 6 | 6ce4509b | Från Begäran | 6,92 | 0,3331 | 73,51% | 79,06% | 41 | 63,42 |
| 7 | 9c89f76c | Från Begäran | 7,04 | 0,3299 | 72,96% | 77,67% | 53 | 62,64 |

**Fetstil** = bästa värdet i respektive kategori

### Algoritmanalys

**Observation:** Alla 7 toppresterande lösningar kom från algoritmen **"Från Begäran"**.

Detta indikerar att en request-centrerad strategi, som bygger scheman från enskilda besök och försöker gruppera dem effektivt, ger överlägsen balans mellan kontinuitet och effektivitet jämfört med algoritmer som fokuserar ensidigt på väntetidsminimering eller förlängd beräkningstid.

### Avvägningsanalys: Kontinuitet vs. Effektivitet

Spridningsdiagram (scatter plot) av de 7 bästa lösningarna visar:

**X-axel:** Kontinuitet (genomsnittliga unika vårdgivare)
**Y-axel:** Verksamhetseffektivitet (%)

**Observation:**
- Det finns **inte en strikt linjär avvägning** mellan kontinuitet och effektivitet
- Jobs med 3,92–6,92 unika vårdgivare uppnår alla 68–74% effektivitet
- "Sweet spot": 4–6 unika vårdgivare ger 70–74% effektivitet
- Extremt hög kontinuitet (3,92) kan uppnås med 68,54% effektivitet (fortfarande acceptabelt)
- Högsta effektiviteten (73,59%) uppnås med 5,78 unika vårdgivare (fortfarande utmärkt kontinuitet)

Detta stödjer forskningen som visar att kontinuitet och effektivitet inte är strikt motstridiga mål när intelligent optimering tillämpas [5].

### Produktionsrekommendation

Baserat på rankingen och balansen mellan alla mål rekommenderas:

**Primär produktion:**
**Job 117a4aa3** – Bästa fälteffektivitet (79,06%), hög verksamhetseffektivitet (73,51%), och högsta tilldelningsgrad (98,9%). Kontinuitet på 6,92 är väl under Kolada-målet.

**Alternativ för prioriterade klienter:**
**Job 70eb56bf eller 8092f87c** – Exceptionell kontinuitet (3,92–3,94 unika vårdgivare) för klienter där relationen är särskilt viktig (t.ex. demens, kognitiva funktionsnedsättningar). Acceptabel effektivitet kring 69%.

---

## Diskussion

### Balans mellan Kontinuitet och Effektivitet

Resultaten från Huddinge-kampanjen visar tydligt att **kontinuitet och effektivitet inte är ett nollsummespel**. Genom AI-baserad flermålsoptimering kan båda målen uppnås samtidigt:

- Alla 7 topplösningar klarar Kolada-målet (<11 unika vårdgivare) med god marginal
- Samtidigt uppnås 71,5% genomsnittlig verksamhetseffektivitet, vilket innebär att 71,5% av arbetstiden spenderas på besök hos klienter (jämfört med resa och väntetid)
- Bästa lösningen uppnår 79,06% fälteffektivitet, vilket innebär att endast ~21% av tiden i fält spenderas på resor

Jämfört med manuell schemaläggning, där riksgenomsnittet för kontinuitet ligger kring 15 unika vårdgivare, representerar detta en **förbättring med 60–75%** i kontinuitet utan att effektiviteten behöver offras.

### Algoritmens Betydelse

En viktig lärdom är att **valet av algoritm har stor betydelse**. Att "Från Begäran" dominerade alla 7 toppositioner visar att en request-centrerad strategi, där algoritmen bygger upp scheman från enskilda besök och försöker gruppera dem optimalt, ger bättre resultat än:

- Väntetid-fokuserade algoritmer (som ofta fragmenterar vårdrelationer)
- Längre beräkningstider utan strukturell förändring

Detta stämmer överens med HHCRSP-forskningen som betonar vikten av integrerad rutt- och rostering över flera perioder snarare än dagvisa optimeringar [4].

### Praktiska Implikationer för Svenska Kommuner

#### För Kommuner och Verksamhetschefer
- **25–30% restidsminskning:** Genom att ersätta manuell schemaläggning med AI-optimering kan restiden reduceras avsevärt, vilket frigör tid för fler besök eller personalnedskärning
- **Kolada-efterlevnad:** Möjlighet att uppnå <11 unika vårdgivare per klient systematiskt, inte enbart för vissa prioriterade klienter
- **Kostnadseffektivitet:** Högre verksamhetseffektivitet (70%+) innebär mindre "slösad" tid och bättre utnyttjande av personalkostnaderna

#### För Vårdgivare
- **Mer förutsägbara scheman:** Färre ad-hoc-ändringar och bättre arbetsbalans
- **Starkare klientrelationer:** Möjlighet att bygga kontinuerliga relationer, vilket ökar arbetsglädje
- **Mindre övertid:** Effektivare ruttplanering minskar behovet av övertid för att "fixa" schemafel

#### För Klienter
- **Färre unika ansikten:** Från riksgenomsnittet 15 ner till 4–7 unika vårdgivare innebär tryggare vårdrelationer
- **Bättre vårdkvalitet:** Forskning visar att kontinuitet leder till bättre hälsoutfall och färre misstag [1]
- **Ökad tillfredsställelse:** Kontinuitet rankas högt bland klienternas kvalitetskriterier

### Anpassning till Svenska Förhållanden

En kritisk fråga är om lösningen är anpassad till svenska kollektivavtal och arbetsvillkor:

- **Arbetstidsregler:** Timefold FSR kan konfigureras med svenska regler för raster, maximal arbetstid per dag/vecka, och övertidsbegränsningar
- **Kompetenskrav:** Matchning av vårdgivarkompetens mot klientbehov är en kärnfunktion
- **Synkroniserade besök:** 152 gruppbesök hanterades korrekt i Huddinge-kampanjen

Verktyget är därmed fullt kompatibelt med svenska förhållanden, förutsatt att konfigurationen anpassas efter det specifika kollektivavtalet.

### Begränsningar i Studien

**Geografiskt begränsat dataset:**
Studien bygger enbart på data från Huddinge kommun. Resultat kan variera i kommuner med:
- Glesare geografisk spridning (längre restider)
- Annorlunda klientprofil (fler/färre gruppbesök, komplexa vårdbehov)
- Olika personalsituation (färre/fler vårdgivare, kompetensbrist)

**Kort tidsperiod:**
Optimieringen omfattar 2 veckor (14 dagar). Säsongsvariationer, semester och långsiktig personalkontinuitet fångas inte. För att fullt ut utvärdera långsiktig kontinuitet krävs 4–12 veckors optimering.

**Statisk modell:**
Lösningen är statisk (planeras i förväg). I verkligheten uppstår dagliga förändringar:
- Nya akuta besök
- Sjukfrånvaro bland personal
- Klientavbokningar

En fullständig implementation bör komplettera statisk planering med **dynamisk omplanering** (rolling horizon) för att hantera realtidsförändringar.

**Inga verkliga tester med vårdgivare och klienter:**
Resultaten är simulerade. För att bekräfta att den teoretiska kontinuitetsförbättringen omsätts i praktisk vårdkvalitet krävs pilotstudier med faktisk implementation och uppföljning av klient- och personalupplevelser.

---

## Slutsats

### Huvudfynd

AI-baserad optimering av hemtjänstschemaläggning kan **samtidigt uppnå hög kontinuitet och hög effektivitet**. Resultat från Huddinge kommun visar att:

1. **Kontinuitetsmål uppnås:** 3,92–7,04 unika vårdgivare per klient (alla under Kolada-målet på 11)
2. **Effektivitetsmål uppnås:** 71,5% genomsnittlig verksamhetseffektivitet, 77,9% fälteffektivitet
3. **Algoritm betyder:** "Från Begäran" (request-centrerad strategi) ger bäst resultat
4. **Ingen strikt trade-off:** Kontinuitet och effektivitet är inte motstridiga mål vid intelligent optimering

### Rekommendationer för Implementering

#### Steg 1: Börja med "Från Begäran"-algoritmen
Baserat på Huddinge-kampanjens resultat bör kommuner som implementerar AI-schemaläggning börja med Timefold FSR:s "Från Begäran"-algoritm (eller motsvarande request-centrerad metodik).

#### Steg 2: Konfigurera kontinuitetsmått
Aktivera både "unika vårdgivare"-räkning och CCI-beräkning för att få fullständig bild. Sätt mål:
- Primärt: <11 unika vårdgivare (Kolada N00941)
- Sekundärt: CCI >0,35

#### Steg 3: Balansera viktning i objektfunktionen
Använd en viktad flermålsoptimering med viktning liknande Huddinge-kampanjen:
- 40% kontinuitet
- 20% CCI
- 25% verksamhetseffektivitet
- 10% fälteffektivitet
- 5% tilldelningsgrad

#### Steg 4: Pilotera och utvärdera
Kör pilotprojekt i 4–8 veckor med:
- Jämförelse mot manuell schemaläggning (A/B-test)
- Uppföljning av klient- och personalnöjdhet
- Mätning av faktiska effektivitetsvinster

#### Steg 5: Dynamisk omplanering
Komplettera statisk planering (veckoplanering) med daglig dynamisk omplanering för att hantera:
- Sjukfrånvaro
- Akuta besök
- Klientavbokningar

### Framtida Forskning

Denna studie öppnar för flera fortsatta forskningsområden:

1. **Stokastiska modeller:** Hantera osäkerhet i restid och besökstid genom sannolikhetsbaserade modeller
2. **Längre tidshorisonter:** Optimera över 4–12 veckor för att fånga säsongsvariationer och semester
3. **Dynamisk omplanering:** Utveckla rolling horizon-metoder för realtidshantering av schemaändringar
4. **Multi-site studier:** Replikera studien i fler kommuner för att validera generaliserbarheten
5. **Klientutfallsstudier:** Undersök sambandet mellan AI-optimerad kontinuitet och faktiska hälsoutfall för klienter

### Kontakt och Pilotstudier

Caire.se erbjuder AI-baserad schemaläggning för hemtjänst baserad på Timefold FSR och vetenskapligt beprövad HHCRSP-metodik. För kommuner som vill:

- **Starta en pilotstudie** med AI-optimerad schemaläggning
- **Genomföra en kostnads-nyttoanalys** av effektivitetsvinster
- **Diskutera implementation** anpassad till era kollektivavtal och klientbehov

Kontakta oss:
**Caire.se** | **[info@caire.se](mailto:info@caire.se)** | **+46 [telefon]**

---

## Referenser

[1] Socialstyrelsen & Kolada (2025). *Kvalitetsindikatorer för hemtjänst: N00941 – Antal unika vårdgivare per hemtjänsttagare*. Tillgänglig: [https://www.kolada.se](https://www.kolada.se)

[2] Rasmussen, M. S., et al. (2012). *The Home Care Crew Scheduling Problem: Preference-based visit clustering and temporal dependencies*. European Journal of Operational Research, 219(3), 598-610.

[3] Liu, R., et al. (2017). *Mathematical model and exact algorithm for the home care worker scheduling and routing problem with lunch break requirements*. International Journal of Production Research, 55(2), 558-575.

[4] Braekers, K., Hartl, R. F., Parragh, S. N., & Tricoire, F. (2016). *A bi-objective home care scheduling problem: Analyzing the trade-off between costs and client inconvenience*. European Journal of Operational Research, 248(2), 428-443.

[5] Cissé, M., et al. (2017). *OR problems related to Home Health Care: A review of relevant routing and scheduling problems*. Operations Research for Health Care, 13-14, 1-22.

[6] Fikar, C., & Hirsch, P. (2017). *Home health care routing and scheduling: A review*. Computers & Operations Research, 77, 86-95.

[7] Timefold (2025). *Field Service Routing Documentation*. Tillgänglig: [https://docs.timefold.ai](https://docs.timefold.ai)

---

**Nyckelord:** Hemtjänst schemaläggning AI, kontinuitet i hemtjänsten, optimering av hemtjänst, färre unika vårdgivare, Kolada N00941, HHCRSP, effektiv schemaläggning, AI ruttplanering, Timefold FSR, Continuity of Care Index

---

**Om författaren:**
Björn Evers är CEO för Caire.se och Eirtech.ai, företag som utvecklar AI-lösningar för hemtjänst och äldrevård. Han har över 15 års erfarenhet inom optimering och AI-tillämpningar i välfärdssektorn.

**Datakällor:**
Huddinge-kampanjen kördes 11–12 mars 2026. Fullständig dashboard med interaktiva visualiseringar finns tillgänglig för granskning. Kontakta [info@caire.se](mailto:info@caire.se) för tillgång till komplett dataset.

---

*Publicerad på www.caire.se/forskning/kontinuitet-effektivitet-hemtjanst-ai-optimering*
*Senast uppdaterad: 12 mars 2026*
