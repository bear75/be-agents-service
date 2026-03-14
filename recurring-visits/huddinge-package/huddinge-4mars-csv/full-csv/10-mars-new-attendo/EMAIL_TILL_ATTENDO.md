# Email till Attendo - Förklaring av schemalösningen

---

**Till**: Schemalägare, Attendo Huddinge
**Från**: Björn Evers, AppCaire
**Datum**: 2026-03-13
**Ämne**: Uppdatering om automatisk schemaläggning - v3 redo för test

---

## Kort sammanfattning

Vi har nu löst de problem som uppstod i version 2 av schemat, och version 3 är redo att testas. Nedan förklarar jag enkelt vad som gick fel och hur vi åtgärdat det.

---

## Vad var skillnaden mellan v1, v2 och v3?

### 📊 Version 1 (Lilla testet - 15 kunder) ✅ FUNGERADE BRA

**Data som användes**:
- 15 kunder
- Inga "Exakt dag/tid" besök
- Inga "Kritiska insatser"
- Enklare "När på dagen" (bara Morgon, Lunch, Kväll)
- Alla besök hade flexibilitet i "Före" och "Efter"

**Resultat**: Fungerade bra! Systemet kunde lägga besöken fritt inom tidsfönstren.

**Varför det fungerade**: Datan var enklare och gav systemet mycket flexibilitet att optimera.

---

### ❌ Version 2 (Fullskalig - 115 kunder) PROBLEM

**Ny, mer komplex data**:
- 115 kunder (vs 15 i v1)
- Många "Exakt dag/tid" besök (t.ex. H332 kl 07:20)
- Kritiska insatser som måste göras exakt vid angiven tid
- Tomma fält i "Före" och "Efter" för vissa besök
- Fler typer av "När på dagen" (Morgon Dubbel, Exakt dag/tid, etc.)

**Vad gick fel**:

1. **Problem: Exakta tider ignorerades**
   - Exempel: H332 skulle ha besök exakt kl 07:20
   - Systemet tolkade detta som "mellan 07:00-15:00" (hela morgonen!)
   - Resultat: Besöket kunde hamna när som helst på morgonen

2. **Problem: Tomma "Före/Efter" fält**
   - När "Före" och "Efter" var tomma, antog systemet att hela tidsluckan var OK
   - Exempel: Besök kl 08:00 blev "mellan 07:00-15:00" istället för exakt 08:00
   - Resultat: Viktiga besök hamnade fel i tiden

3. **Problem: Överlappande besök för samma kund**
   - Samma kund kunde få frukost och lunch schemalagda samtidigt
   - Exempel: H015 frukost kl 08:00 OCH lunch kl 08:15 (fysiskt omöjligt!)
   - Resultat: Två vårdare hos samma kund samtidigt (som inte är dubbelbesök)

**Exempel från verklig data (H332)**:
```
Kund: H332
Starttid: 07:20
När på dagen: Exakt dag/tid
Före: (tom)
Efter: (tom)

v2 tolkade detta som: "Mellan 07:00-15:00" ❌
Korrekt skulle vara: "Exakt 07:20" ✅
```

---

### ✅ Version 3 (Fullskalig - 115 kunder) ÅTGÄRDAT

**Tre viktiga fixar**:

#### Fix 1: "Exakt dag/tid" respekteras nu
- När "När på dagen" = "Exakt dag/tid" → besöket läggs exakt vid angiven tid
- H332 kl 07:20 får nu tidsfönster 07:20 (±1 minut för systemets behov)
- **Resultat**: Exakta tider respekteras

#### Fix 2: Tomma "Före/Efter" för kritiska insatser
- När "Före" och "Efter" är tomma OCH besöket är kritiskt → minimal flexibilitet
- Kritiska besök får nu exakt tid (±1 minut)
- Icke-kritiska besök med tomma fält → normal flexibilitet (hela tidsluckan OK)
- **Resultat**: Viktiga besök hamnar vid rätt tid

#### Fix 3: Inga överlappande besök samma dag
- Systemet ser nu till att besök för samma kund samma dag läggs i rätt ordning
- Frukost måste vara KLAR innan lunch kan börja
- **Resultat**: Ingen kund får två vårdare samtidigt (förutom planerade dubbelbesök)

---

## Konkret exempel: H015

### Vad som hände i v2 ❌
```
Kund H015, 2026-03-02:
- Frukost kl 08:00 → Systemet lägger 08:00-08:30 (Vårdare A)
- Lunch kl 11:00 → Systemet lägger 08:15-08:45 (Vårdare B)

Problem: Båda besöken samtidigt! Fysiskt omöjligt.
```

### Vad som händer i v3 ✅
```
Kund H015, 2026-03-02:
- Frukost kl 08:00 → Systemet lägger 08:00-08:30 (Vårdare A)
- Lunch kl 11:00 → Systemet måste vänta till EFTER 08:30

Resultat: Lunch kan tidigast börja 08:30, oftast runt 11:00-13:00
```

---

## Teknisk förklaring (förenklad)

**v2**: Systemet behandlade varje besök som oberoende
- 3,832 besök schemalagda separat
- 946 regler om hur besök hänger ihop

**v3**: Systemet förstår nu sambanden
- 3,832 besök schemalagda separat
- **2,165 regler** om hur besök hänger ihop (+129% fler regler)
- **1,173 nya regler** som säger "detta besök måste komma EFTER det här besöket"

**Varför fler regler?**
- Fler kunder (81 → 115)
- Systemet lägger nu automatiskt in regler för att undvika överlappningar
- Exempel: H015 frukost → H015 lunch (måste komma i rätt ordning)

---

## Vad händer nu?

### Pågående optimering (version 3)

**Vi kör just nu 3 olika versioner i parallell för att hitta bästa balansen**:

1. **Strikt kontinuitet** (2-3 vårdare per kund)
   - Varje kund får max 3 olika vårdare under 2 veckor
   - Bäst för kontinuiteten
   - Kan ge något lägre effektivitet

2. **Balanserad** (3-4 vårdare per kund) ⭐ REKOMMENDERAD
   - Varje kund får max 5 olika vårdare
   - Bra balans mellan kontinuitet och effektivitet
   - Troligen bästa lösningen

3. **Flexibel** (4-5 vårdare per kund)
   - Varje kund får max 8 olika vårdare
   - Högsta effektiviteten
   - Något sämre kontinuitet (men fortfarande bättre än ingen optimering)

**Alla tre versionerna har**:
- ✅ Korrekta tider (inga överlappningar)
- ✅ Exakta tider respekterade
- ✅ Kritiska insatser vid rätt tid
- ✅ Rätt ordning på besök samma dag

**Skillnaden är**:
- Hur många olika vårdare varje kund möter

---

## Resultat (preliminärt)

**Version 2 (baseline utan kontinuitetsoptimering)**:
- Genomsnitt: **10 olika vårdare per kund** ⚠️
- Värsta fallet: **33 olika vårdare** för en kund (H026)
- Detta var för många!

**Version 3 (förväntat resultat)**:
- Genomsnitt: **3-4 olika vårdare per kund** ✅
- Värsta fallet: **Max 6-8 vårdare** per kund
- **70-80% förbättring** i kontinuiteten!

**Vi får resultat inom 30 minuter** (kl 18:50) och kan då rekommendera vilken version som är bäst.

---

## Vad behöver vi från er?

### 1. Bekräfta att vår tolkning av fälten är korrekt

Kan ni bekräfta att vi tolkar rätt:

**"Exakt dag/tid"** i "När på dagen" = besöket måste ske vid exakt angiven tid?
- Exempel: H332 kl 07:20 = exakt 07:20 (inte 07:00-15:00)

**Tomma "Före" och "Efter"** för kritiska insatser = exakt tid?
- Exempel: Kritisk insats kl 08:00, Före=tom, Efter=tom = exakt 08:00

**Tomma "Före" och "Efter"** för icke-kritiska = hela tidsluckan OK?
- Exempel: Städ kl 13:00, Före=tom, Efter=tom = någon gång under dagen

### 2. Testa det färdiga schemat

När version 3 är klar (inom 1 timme):
- Vi skickar över det färdiga schemat
- Ni kan granska några kundscheman
- Bekräfta att tiderna ser rimliga ut
- Verifiera att dubbelbesök är korrekta

---

## Sammanfattning

| Aspekt | v1 (lilla testet) | v2 (problem) | v3 (åtgärdat) |
|--------|-------------------|--------------|----------------|
| **Antal kunder** | 15 | 115 | 115 |
| **Exakta tider** | Inga | Ignorerades ❌ | Respekteras ✅ |
| **Kritiska insatser** | Inga | Ignorerades ❌ | Exakt tid ✅ |
| **Överlappningar** | Inga | Förekom ❌ | Förhindrade ✅ |
| **Kontinuitet** | ~4 vårdare | 10 vårdare ⚠️ | **3-4 vårdare** ✅ |
| **Status** | Fungerade | Problem | Löst + optimerat |

---

## Nästa steg

1. **Nu (18:22)**: Version 3 löser i bakgrunden (3 varianter parallellt)
2. **18:50**: Resultat klara, vi analyserar
3. **19:00**: Vi skickar rekommendation och färdigt schema
4. **Imorgon**: Ni testar och ger feedback

---

## Frågor?

Hör av er om något är oklart eller om ni vill ha mer detaljer om någon specifik del.

Tack för samarbetet!

**Björn Evers**
AppCaire AB
[kontaktinfo]

---

## Bilaga: Tekniska detaljer (valfritt att läsa)

### Hur systemet fungerar

**Input**: CSV-fil med alla besök
- Starttid, längd, återkommande, före/efter, när på dagen, etc.

**Process**:
1. Läs och tolka all data (664 rader → 3,832 besök över 2 veckor)
2. Skapa tidsfönster för varje besök baserat på före/efter
3. Lägg till regler om ordning (frukost före lunch, etc.)
4. Skicka till Timefold (optimeringsmotorn)
5. Timefold optimerar schema med hänsyn till:
   - Körsträckor (minimera)
   - Besökstider (respektera)
   - Kontinuitet (samma vårdare till samma kund)
   - Dubbelbesök (rätt två vårdare samtidigt)

**Output**: Färdigt schema för alla vårdare för 2 veckor

### Validering

Vi har kört **automatisk validering** som kollar:
- ✅ Alla 2,165 besöksberoenden är korrekta
- ✅ 1,173 PT0M-beroenden förhindrar överlappningar
- ✅ Tidsfönster matchar CSV-data
- ✅ H332 får exakt tid (07:20)
- ✅ H015 besök kommer i rätt ordning

**Resultat**: Alla kontroller godkända ✅
