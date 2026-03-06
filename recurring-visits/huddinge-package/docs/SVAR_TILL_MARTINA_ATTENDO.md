# Svar till Martina (Attendo) – Förklaring till avvikande besök

Hej Martina,

Tack för den noggranna genomgången. Vi har gått igenom varje fall och spårat var avvikelsen uppstår: antingen i vår process (konvertering från er fil, expansion till tidsfönster, eller optimerarens resultat) eller i källdatan. Nedan en kort förklaring per kund.

---

**H092** – Lunch planerad precis före morgon/dusch  
*Var felet ligger: Vår optimering (output)*  
Lunchbesöket hamnade i fel ordning i förhållande till morgon/dusch på rutten. Tidsfönstren var rimliga; felet är hur optimeraren ordnade besöken på slingan. Vi åtgärdar genom att justera prioritering/ordning i optimeringen.

---

**H299** – Ska ha 1 besök/dag, fick 09:07 och 12:00 samma dag (18/2)  
*Var felet ligger: Vår expansion (extended)*  
Er fil har korrekt en rad per veckodag (mån, tis, ons, tor, fre) med max ett besök per dag. I vår steg där vi bygger tidsfönster från källdatan gav vi “ett besök per vecka”-raderna (måndag och torsdag) ett tidsfönster över hela veckan istället för att binda dem till just måndag respektive torsdag. Därför kunde optimeraren lägga måndagsbesöket på onsdag – då kunden redan hade ett onsdagsbesök. Vi har ändrat så att “ett besök per vecka” alltid kopplas till den dag som står i er fil, så att detta inte ska upprepas.

---

**H331** – 2 måltidsbesök 10:56 och 11:22 (18/2)  
*Var felet ligger: Källdata (Attendo) eller vår expansion*  
I er export finns två separata rader för H331 på onsdag: ett måltidsbesök 08:59 och ett 11:17. Vi tolkar det som två besök den dagen, vilket gav 10:56 och 11:22 i planeringen. Om avtalet är att kunden endast ska ha **ett** måltidsbesök på onsdag behöver en av raderna justeras eller tas bort i er fil. Om två måltider (t.ex. frukost och lunch) är avsiktliga är datan i linje med det; i så fall kan vi i stället titta på tidsfönster så att de inte överlappar på ett oönskat sätt.

---

**H335** – Måltid+promenad och dusch på olika slingor samma dag  
*Var felet ligger: Vår expansion (extended)*  
Samma typ av fel som H299: ett “ett besök per vecka”-besök (t.ex. måltid+promenad tisdag) fick tidsfönster över hela veckan och kunde därför läggas på en dag då kunden redan hade ett annat besök (t.ex. dusch torsdag). Vi har åtgärdat expansionen så att veckodag från er fil används konsekvent, vilket ska förhindra att två besök hamnar samma dag på detta sätt.

---

**H172** – Morgon 07:42 planerad 16:05 (19/2)  
*Var felet ligger: Vår optimering (output) eller våra tidsfönster (input)*  
Morgonbesöket hamnade på eftermiddagen. Antingen tillät tidsfönstret det (för brett) – då är felet i vår beräkning av tidsfönster – eller så valde optimeraren fel tid inom ett snävt fönster. Vi kontrollerar tidsfönster för morgonbesök och justerar så att morgon inte kan planeras på kväll.

---

**H362** – Morgon planerad på kvällen  
*Var felet ligger: Vår optimering (output)*  
Samma typ som H172: morgonbesök har hamnat fel tid på dagen. Vi ser över tidsfönster och optimeringslogik så att morgonbesök hålls inom morgon-/förmiddagsfönster.

---

**H095** – Lunch (90 min före 13:22) planerad 16:10 (19/2) och 08:14–09:48 (20/2)  
*Var felet ligger: Vår optimering (output) eller våra tidsfönster (input)*  
Lunchbesöket har hamnat utanför det avsedda lunchfönstret (för sent respektive för tidigt). Vi går igenom om tidsfönstret för lunch var för brett eller om optimeraren valde fel tid, och justerar så att lunch hålls inom rimligt lunchfönster.

---

**H248** – 2 lunchbesök direkt efter varandra (19/2)  
*Var felet ligger: Källdata (Attendo) eller vår expansion*  
Två lunchbesök samma dag kan bero på att det i källdatan finns två rader för samma dag (då behöver ni eventuellt slå ihop eller justera i er fil), eller på att vår expansion skapat två besök från en rad. Vi dubbelkollar mot er export och justerar vår logik om det är vi som skapar dubbletten.

---

**H072** – 3 besök direkt efter varandra 08:31–10:31, ska inte planeras före 09:00 (19/2)  
*Var felet ligger: Våra tidsfönster (input) eller optimering (output)*  
Om kravet “inte före 09:00” fanns med i källdatan ska det ge ett tidsfönster som börjar 09:00 eller senare. Om det inte fanns med blir tidsfönstret fel hos oss. Om det fanns med men optimeraren ändå satte besök före 09:00 är felet i output. Vi säkerställer att “inte före 09:00” alltid respekteras i tidsfönster och i optimeringen.

---

**H077** – 2 morgonbesök direkt efter varandra 07:20–09:15, ska vara 07:20 (diff 0) (19/2)  
*Var felet ligger: Källdata (Attendo) eller våra tidsfönster (input)*  
Om det ska vara exakt ett morgonbesök 07:20 med diff 0 kan två rader för samma dag i källdatan ge två besök – då behöver ni justera er fil. Om ni bara har en rad men vi skapar två besök eller ger för bred flex är felet hos oss. Vi kontrollerar både källdata och hur vi sätter tidsfönster för denna kund.

---

**H087** – 3 besök direkt efter varandra 09:49 och 12:02 (20/2)  
*Var felet ligger: Källdata/expansion eller vår optimering (output)*  
För många besök samma dag kan bero på flera rader för samma dag i er fil (då behöver ni eventuellt justera) eller på att vår expansion/optimering dubblar eller triplar besök. Vi spårar mot er export och åtgärdar i vår process om det är vi som skapar för många besök.

---

**H034** – Morgon och lunch direkt efter varandra 11:05–12:05 (20/2)  
*Var felet ligger: Vår optimering (output) eller våra tidsfönster (input)*  
Morgon ska vara tidigare och lunch senare. Om tidsfönstren var korrekta har optimeraren valt fel ordning/tid. Om tidsfönstren var för breda eller felaktiga är felet i vår input. Vi justerar så att morgon och lunch får tydligt åtskilda tidsfönster och ordning.

---

**H238** – Lunch, morgon och middag samlade kring 10:37 (20/2)  
*Var felet ligger: Vår optimering (output) eller våra tidsfönster (input)*  
Besökstyperna har hamnat på fel tider (t.ex. morgon vid 10:37). Vi kontrollerar om tidsfönstren för morgon/lunch/middag var för breda eller felaktiga, och att optimeraren respekterar tid på dagen för varje besökstyp.

---

**Sammanfattning**

- **Vår process (expansion):** H299, H335 – “ett besök per vecka” var inte kopplat till rätt veckodag; det är nu åtgärdat.
- **Vår optimering (output):** H092, H172, H362, H095, H034, H238 – fel ordning eller fel tid på dagen; vi skärper tidsfönster och prioritering.
- **Källdata eller gemensam koll:** H331, H248, H077, H087 – fler besök samma dag än avsett; vi kollar er fil och vår expansion så att vi inte skapar dubbletter, och justerar tidsfönster där det behövs.

Vi återkommer med konkreta justeringar när de är genomförda.
