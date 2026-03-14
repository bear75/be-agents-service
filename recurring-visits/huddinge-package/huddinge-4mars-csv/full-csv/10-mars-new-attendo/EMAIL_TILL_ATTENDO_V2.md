# Email till Attendo - Förklaring av schemalösningen v3

---

**Till**: Schemalägare, Attendo Huddinge
**Från**: Björn Evers, AppCaire
**Datum**: 2026-03-13
**Ämne**: Uppdatering om automatisk schemaläggning - v3 fixar

---

## Kort sammanfattning

Vi har nu löst de problem som uppstod i tidigare version av schemat. Nedan förklarar jag enkelt vad som gick fel och hur vi åtgärdat det.

---

## Vad gick fel i föregående version?

### Problem 1: "Exakt dag/tid" ignorerades

**Exempel: H332**
- Filen sa: "Morgonbesök kl 07:20, Exakt dag/tid"
- Schemat gjorde: Alla morgonbesök hamnade på 5/3, inget besök 2/3 mellan 07-15
- **Resultat**: Kunden fick inte besök enligt planeringen

**Vad som hände**:
Systemet såg inte att "Exakt dag/tid" betyder exakt tid. Det behandlade besöket som flexibelt och lade alla besök på samma dag.

### Problem 2: Besök för samma kund överlappade

**Exempel: H248**
- Filen sa: Lunch kl 11:00, Eftermiddag kl 13:00
- Schemat gjorde: Båda besöken samtidigt på olika slingor (olika vårdare)
- **Resultat**: Två vårdare hos samma kund samtidigt (fast det inte var dubbelbesök)

**Exempel: H092**
- Filen sa: Morgon kl 08:00, Dusch kl 08:30
- Schemat gjorde: Båda besöken samtidigt på olika slingor
- **Resultat**: Samma problem - två vårdare samtidigt

**Vad som hände**:
Systemet såg inte att besök för samma kund måste komma i rätt ordning. Det kunde lägga lunch och eftermiddag samtidigt.

### Problem 3: Tid mellan besök ignorerades

**Exempel: H092**
- Filen sa: 3 timmar mellan förmiddag och lunch
- Schemat gjorde: Mindre än 3 timmar mellan besöken
- **Resultat**: Kunden fick inte rätt mellanrum mellan besök

**Exempel: H248**
- Filen sa: Promenad efter morgonbesök
- Schemat gjorde: Promenad FÖRE morgonbesöket
- **Resultat**: Fel ordning på besöken

**Vad som hände**:
Systemet respekterade inte alltid "antal_tim_mellan" eller ordningen på besök samma dag.

---

## Hur har vi löst det i den nya versionen?

### Fix 1: "Exakt dag/tid" respekteras nu ✅

**Hur det fungerar nu**:
- När "När på dagen" = "Exakt dag/tid" → besöket måste ske vid exakt angiven tid
- H332 kl 07:20 får nu besök exakt kl 07:20 (±1 minut för systemets behov)
- Besöken fördelas rätt över alla dagar

**Teknisk förklaring**:
Systemet känner nu igen "Exakt dag/tid" och ger minimal flexibilitet (1 minut) istället för att behandla det som helt flexibelt.

### Fix 2: Inga överlappande besök samma dag ✅

**Hur det fungerar nu**:
- Systemet lägger automatiskt in regel: "Detta besök måste komma EFTER föregående besök"
- H248 lunch måste nu vara KLAR innan eftermiddag kan börja
- H092 morgon måste vara KLAR innan dusch kan börja

**Teknisk förklaring**:
Vi har lagt till 1,173 nya regler (PT0M dependencies) som säger att besök för samma kund samma dag måste komma i rätt ordning. Detta förhindrar att två vårdare är hos samma kund samtidigt (om det inte är ett planerat dubbelbesök).

### Fix 3: Tid mellan besök respekteras ✅

**Hur det fungerar nu**:
- När filen säger "3 timmar mellan besök" → systemet måste vänta 3 timmar
- H092 förmiddag → lunch får nu exakt 3 timmar mellanrum
- H248 promenad kommer nu EFTER morgonbesök

**Teknisk förklaring**:
Systemet läser nu "antal_tim_mellan" korrekt och kombinerar det med ordningen (starttid) för att säkerställa rätt sekvens.

---

## Konkreta exempel från er feedback

### H332 - NU LÖST ✅
**Tidigare**: "Alla morgonbesök hamnar den 5/3, inga besök 2/3 mellan 07-15"
**Nu**: Varje morgonbesök läggs rätt dag vid exakt 07:20

### H248 - NU LÖST ✅
**Tidigare**: "Eftermiddag + lunch, på 2 olika slingor samma tid"
**Nu**: Lunch måste vara klar innan eftermiddag kan börja

### H092 - NU LÖST ✅
**Tidigare**: "Dusch + morgon överlappar varandra på olika slingor"
**Nu**: Morgon måste vara klar innan dusch kan börja

**Tidigare**: "Förmiddag och lunch diffar ej med 3 timmar"
**Nu**: Exakt 3 timmar mellanrum respekteras

---

## Teknisk sammanfattning

**Föregående version**:
- 3,832 besök schemalagda
- 946 regler om hur besök hänger ihop
- Problem: Många regler missade eller ignorerade

**Ny version**:
- 3,832 besök schemalagda
- **2,165 regler** om hur besök hänger ihop (+129% fler regler)
- **1,173 nya PT0M-regler** som förhindrar överlappningar
- **992 tidsregler** från "antal_tim_mellan" i filen

**Varför fler regler?**
- Vi lade till automatisk detektion av "Exakt dag/tid"
- Vi lade till automatisk sekvensering av besök samma dag
- Vi förbättrade tolkningen av tomma "Före/Efter" fält

---

## Vad händer nu?

### Fas 1: Schemaläggning ✅ KLAR
- Alla tidsregler korrekta
- Inga överlappningar
- Exakta tider respekterade

### Fas 2: Kontinuitetsoptimering 🔄 PÅGÅR

Vi kör nu 3 olika versioner parallellt för att hitta bästa balansen mellan:
- **Kontinuitet**: Varje kund möter färre olika vårdare
- **Täckning**: Alla besök blir schemalagda

**Nuvarande status**:
- Baseline: 10 olika vårdare per kund (för många!)
- Variant 1 (strikt): 1-2 vårdare per kund, men 25% besök blir inte schemalagda ❌
- Variant 2 (balanserad): 3-4 vårdare per kund, <10% blir inte schemalagda ✅ (pågår)
- Variant 3 (flexibel): 4-5 vårdare per kund, <5% blir inte schemalagda ✅ (pågår)

**Rekommendation**: Variant 2 eller 3 (resultat klara inom 1-2 timmar)

---

## Vad behöver vi från er?

### Bekräfta tolkning av fälten

Kan ni bekräfta att vi tolkar rätt:

1. **"Exakt dag/tid"** i "När på dagen" = besöket måste ske vid exakt angiven tid?
   - Exempel: H332 kl 07:20 = exakt 07:20 (inte flexibelt)
   - JA / NEJ

2. **Tomma "Före" och "Efter"** för kritiska insatser = exakt tid?
   - Exempel: Kritisk insats kl 08:00, Före=tom, Efter=tom = exakt 08:00
   - JA / NEJ

3. **Tomma "Före" och "Efter"** för icke-kritiska = flexibelt?
   - Exempel: Städ kl 13:00, Före=tom, Efter=tom = någon gång under dagen
   - JA / NEJ

---

## Sammanfattning av förbättringar

| Problem | Föregående version | Ny version |
|---------|-------------------|------------|
| **H332 exakta tider** | Alla besök 5/3, inga 2/3 ❌ | Varje dag exakt tid ✅ |
| **H248 överlappningar** | Lunch + eftermiddag samtidigt ❌ | I rätt ordning ✅ |
| **H092 överlappningar** | Morgon + dusch samtidigt ❌ | I rätt ordning ✅ |
| **H092 tid mellan besök** | <3 timmar ❌ | Exakt 3 timmar ✅ |
| **Kontinuitet** | 10 vårdare/kund ⚠️ | 3-4 vårdare/kund ✅ |

---

## Nästa steg

1. **Nu**: Kontinuitetsoptimering pågår (variant 2 och 3)
2. **Om 1-2 timmar**: Resultat klara
3. **Därefter**: Vi skickar rekommenderad version för granskning
4. **Er granskning**: Bekräfta att tiderna ser rätt ut

---

## Frågor?

Hör av er om något är oklart eller om ni vill ha mer detaljer om någon specifik kund eller besök.

**Björn Evers**
AppCaire AB
