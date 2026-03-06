# CSV → Timefold FSR JSON: full mapping spec (Caire hemtjänstmodell)

**Mål:** En dev eller AI ska kunna använda detta för att mappa hemtjänstens besökskrav (CSV) till Caires modell (Timefold FSR JSON) för optimering. Besök ska vara **så flexibla som möjligt** så att solvern kan maximera assigned visits, kontinuitet och effektivitet; endast nödvändiga begränsningar (tidsfönster och dependencies) ska läggas in.

**Referensimplementation:** `huddinge-package/huddinge-4mars-csv/scripts/attendo_4mars_to_fsr.py`  
**Verifiering mot Attendo:** `huddinge-4mars-csv/docs/CSV_TO_INPUT_VERIFICATION.md`, `CSV_TILL_INPUT_VERIFIERING.md`

---

## 1. Hur Timefold skiljer på dependency-typer

**Timefold skiljer inte** mellan "samma insats spread" och "samma dag mellan olika insatser". I JSON finns bara:

```json
"visitDependencies": [{ "precedingVisit": "<visitId>", "minDelay": "PT3H30M" }]
```

Solvern ser endast: *"Besök B måste starta minst X efter att besök A slutat."*  
**Skillnaden** är hur **vi** bygger vilka länkar vi lägger in:

| Typ | Vi skapar dependency | Timefold ser |
|-----|----------------------|--------------|
| **Samma insats, spread** (t.ex. dusch1 → dusch2 48h, lunch1 → lunch2 24h, frukost1 → frukost2 24h) | Endast mellan förekomster av **samma CSV-rad** (samma `row_index`), **flexible_day**, flera besök per period. minDelay från CSV (48h, 24h) eller 18h standard. | `precedingVisit` = föregående förekomst av samma rad, `minDelay` = PT48H / PT24H etc. |
| **Samma dag, olika insatser** (t.ex. frukost1 → lunch1 3,5h; ingen dep dusch1→lunch1) | Endast mellan **pinnade** besök samma (kund, datum), sorterade Morgon → Lunch → Kväll. Lägg endast in om **den senare** besökets rad har "Antal tim mellan besöken" ifyllt med **kort** värde (≤ 12h). | `precedingVisit` = föregående slot (annan rad), `minDelay` = t.ex. PT3H30M. |

Exempel:

- **dusch1 (48h), dusch2 (48h):** Samma rad, flexible_day → vi lägger **spread** dusch1 → dusch2 med 48h. Ingen same-day-dep från lunch till dusch.
- **lunch1 (24h), lunch2 (24h):** Samma rad, flexible_day → **spread** lunch1 → lunch2 med 24h.
- **frukost1 (3,5h), lunch1 (3,5h):** Olika rader, pinnad samma dag → **same-day** frukost1 → lunch1 med 3,5h (frukost före lunch).
- **dusch1 (0h), lunch1 (0h):** Vi lägger **ingen** dependency mellan dusch och lunch (0h = ingen same-day-dep för 48h-raden), så dusch kan placeras direkt i anslutning till lunch.

---

## 2. Begrepp och modell

- **En CSV-rad = en insats** (en insatstyp, t.ex. "3 luncher/vecka" eller "2 duschar/vecka"). En insats kan ge ett eller flera besök per dag/vecka/period.
- **Pinnad dag:** Besök har exakt ett datum. Vi **pinnar endast** när veckodagarna utgör en **hel mängd**: alla vardagar (mån–fre), båda helgdagar (lör–sön), eller alla 7 (dagligt). Ett tidsfönster per besök.
- **Flexible_day:** Solvern väljer vilken dag/dagar inom en period. Används när veckodagar är **partiella** (t.ex. "mån tis tor", "ons", "tis fre") eller när inga veckodagar anges (t.ex. "Varannan vecka, tis"). Ett fönster per tillåten dag i perioden; spridningsberoenden (t.ex. 18h) håller besök på olika dagar.
- **Visit:** En FSR-visit = ett besök (en förekomst) med plats, tidsfönster, längd, eventuella visitDependencies och eventuell visitGroup.

---

## 3. Alla regler för CSV → JSON

### 3.1 Planeringsfönster och förekomster

- Beräkna planeringsfönster (start–slut) utifrån CSV (t.ex. längsta återkommande = 4 veckor).
- Expandera varje CSV-rad till **occurrences**: en per (rad, datum) för pinnade; en per (rad, period, period_visit_index) för flexible_day.
- Varje occurrence blir **en** visit i JSON (id, location, timeWindows, serviceDuration, visitDependencies, eventuellt visitGroup).

### 3.2 Visit-ID och namn

- **id:** `{kundnr}_r{row_index}_{räknare}` (t.ex. `H015_r12_1`). Unikt per besök.
- **name:** `{kundnr} {När på dagen} {Skift} {Insats}` (för spårbarhet).

### 3.3 Plats (location)

- Adress (Gata, Postnr, Ort) → geokodning till [lat, lon]. Normalisera gata (t.ex. ta bort LGH-nummer) före geokodning.

### 3.4 Tidsfönster (timeWindows)

- **När på dagen** mappas till slot:
  - Morgon → 07:00–10:30
  - Lunch → 11:00–13:30
  - Kväll → 16:00–19:00
  - Tomt/annat → heldag 07:00–22:00 (eller skiftfönster om Skift anges)
- **Pinnad:** Ett timeWindow per besök: samma datum, slotens start–slut (justerat med Starttid, Före, Efter om ifyllt; annars hela sloten).
- **Flexible_day:** Ett timeWindow per tillåten dag i perioden (begränsat av Skift och veckodagar från Återkommande), med samma slot (Morgon/Lunch/Kväll) eller heldag.
- **Krav:** Varje visit ska ha antingen tidsflex (minStartTime ≠ maxStartTime) eller dagflex (flera fönster). Ingen visit med exakt ett fönster med noll flex.

### 3.5 Varaktighet (serviceDuration)

- **Längd** (minuter) → ISO 8601 varaktighet, t.ex. `PT25M`.

### 3.6 VisitDependencies (minDelay)

Två typer. Båda använder CSV-kolumnen **"Antal tim mellan besöken"** men på olika sätt.

#### A) Same-day (olika insatser, samma kund samma dag)

- **När:** Pinnade besök, samma (kundnr, datum). Sortering: Morgon (0) → Lunch (1) → Kväll (2), sedan Starttid.
- **Regel:** För varje par (föregående besök, nuvarande besök) i denna ordning: lägg in `precedingVisit` → nuvarande med minDelay **endast om** nuvarande besökets **rad** har "Antal tim mellan besöken" ifyllt **och** värdet är **≤ 12 timmar** (t.ex. 3,5h för frukost→lunch).
- **Varför 12h:** Långa värden (18h, 24h, 48h) är avsedda för **spridning inom samma insats** (flexible_day). Dusch (48h) ska inte få same-day-dep från lunch så att dusch kan ligga direkt i anslutning till lunch.
- **Delay-värde:** För same-day använder vi **CSV-värdet som det är** (t.ex. PT3H30M). Ingen subtraktion av föregående slotlängd; Timefold mäter från föregående besöks slut till nästa besöks start. Cappa om delay inte får plats mellan de två besökens tidsfönster (med marginal); ta bort dependency om helt omöjligt.

#### B) Spread (samma insats, samma rad, flexible_day)

- **När:** Samma CSV-rad (`row_index`), samma period (`period_start_iso`), **flexible_day**, minst 2 förekomster i perioden.
- **Regel:** Kedja förekomst 1 → 2 → 3 med minDelay. Värdet från "Antal tim mellan besöken" (t.ex. 48h, 24h); om tomt använd **18h** standard så att besök hamnar på olika dagar.
- **Effektiv delay:** `effective = interval - föregående slotlängd`, golv **18h** (aldrig under 18h för spread). Cappa om kedjan inte får plats i periodens fönster; behåll minst 18h.
- **En förekomst per period:** Ingen spread-dependency (bara ett besök att placera).

#### C) Övriga regler för dependencies

- Lägg **aldrig** dependency mellan två besök som tillhör samma **visitGroup** (Dubbel) – undvik loop i modellen.
- För same-day: om båda besöken tillhör samma spread-kedja (samma row_index + period) hoppa över (spread hanterar ordningen).
- Dependencies med ursprunglig delay ≥ 18h får **inte** kapas under 18h vid cappning.

### 3.7 VisitGroups (Dubbel)

- Samma **Dubbel**-värde + samma **datum** (eller samma period för flexible_day) → samma visitGroup. Alla besök i gruppen ska planeras tillsammans (samma tid, samma dag).

### 3.8 Fordon och skift (vehicles, shifts)

- **Slinga** → ett vehicle per unik Slinga.
- **Schift** (Dag / Helg / Kväll) → skift per vehicle: vilka dagar (mån–fre, lör–sön, alla 7) och tidsintervall (Dag 07–15, Helg 07–14:30, Kväll 16–22). Dag/Helg: requiredBreak (10–14, 30 min på kontor).
- Skapa en shift per (vehicle, datum) som matchar vehicleens tillåtna dagar i planeringsfönstret.

### 3.9 Automatiska korrigeringar

- **Flex:** Om Före=Efter=0, använd alltid hela sloten (ingen noll-flex).
- **Dependency:** Om angiven minDelay är större än vad som fysiskt får plats mellan två besöks tidsfönster, capa till max möjliga (med marginal) eller ta bort dependency om inget passar.

---

## 4. Sammanfattning: vad som begränsar optimeringen

| Element | Syfte | Flexibilitet |
|--------|--------|--------------|
| **timeWindows** | När besöket får ske (dag/tid) | Så breda som kravet tillåter (hela slot, flera dagar för flexible_day). |
| **visitDependencies** | Ordning och minsta gap (samma dag: måltider; spread: samma insats) | Endast där CSV kräver det (kort ≤12h för same-day; lång endast inom samma rad). |
| **visitGroups** | Samtidighet (Dubbel) | Endast när Dubbel är satt. |
| **Vehicles/shifts** | Tillgängliga resurser | En shift per tillåten dag. |

Övrigt (kontinuitet, restid, antal tilldelade besök) styrs av **solverns vikter**, inte av hårda dependencies mellan olika insatser. Därmed kan t.ex. dusch placeras direkt i anslutning till lunch när tidsfönster och skift tillåter.

---

## 5. Konstanter (referensimplementation)

- `SAME_DAY_DELAY_MAX_MINUTES = 12 * 60` – över denna gräns används "Antal tim mellan besöken" endast för spread.
- `SPREAD_DELAY_DEFAULT_MIN = 18 * 60`, `SPREAD_DELAY_DEFAULT_ISO = "PT18H"` – standard mellan flexible_day-förekomster när CSV är tom.
- Slot: Morgon 07:00–10:30, Lunch 11:00–13:30, Kväll 16:00–19:00, Heldag 07:00–22:00.

---

## 6. Relaterade dokument

- **CSV_TO_INPUT_VERIFICATION.md** / **CSV_TILL_INPUT_VERIFIERING.md** – verifiering mot Attendo, exempel.
- **Timefold FSR OpenAPI (v1)** – [schema](https://app.timefold.ai/openapis/field-service-routing/v1) för Visit, TimeWindow, VisitDependency, VisitGroup, Vehicle, VehicleShift.
- **attendo_4mars_to_fsr.py** – implementerade regler och konstanter.
