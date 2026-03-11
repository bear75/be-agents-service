# Så får CSV-filen rätt besök och tidsordning (för hemtjänstplanerare)

**Till:** Den som skapar eller exporterar CSV-filen med besöksdata.  
**Syfte:** Kort beskrivning av två kolumner som ofta glöms i den stora filen – **Dubbel** och **Antal tim mellan besöken**.

---

## Vad som saknas i den nya stora filen

I den lilla testfilen fylldes **Dubbel** och **Antal tim mellan besöken** i många fler rader (i förhållande till antal besök) än i den nya stora filen med 81 kunder. Därför får planeringssystemet för få “besöksgrupper” och för få “samma-dag-ordningar” – trots att antalet besök i sig stämmer.

---

## 1. Kolumnen **Dubbel**

**Vad den gör:** Besök som ska utföras **tillsammans** samma dag (samma kund) ska ha **samma siffra** i kolumnen Dubbel.  
Till exempel: Morgonbesök och lunchbesök som alltid ska göras ihop får samma Dubbel-nummer (t.ex. 8) på båda raderna.

**Om Dubbel är tom:** Systemet räknar inte besöken som ett par/grupp och kan planera dem oberoende av varandra.

**Vad du ska göra:** Fyll i Dubbel på **alla** rader där besöket hör ihop med ett annat besök samma dag (samma kund). Ange samma nummer på de rader som ska utföras tillsammans.

---

## 2. Kolumnen **Antal tim mellan besöken**

**Vad den gör:** Om ett besök ska vara **efter** ett annat besök samma dag (t.ex. lunch efter frukost), ska den **senare** raden ha tiden mellan besöken här.  
Exempel: Lunch som ska vara minst 3,5 timmar efter frukost → skriv t.ex. **3,5timmar** på lunch-raden.

**Om kolumnen är tom:** Systemet vet inte att lunch måste komma efter frukost och kan inte hålla rätt ordning eller mellanrum.

**Vad du ska göra:** För varje besök som **måste** komma efter ett annat besök samma dag (t.ex. måltider: frukost → lunch, eller andra kedjor), fyll i **Antal tim mellan besöken** på den **senare** raden med rätt värde (t.ex. 3,5timmar, 2 timmar).

---

## Kort sammanfattning

| Kolumn | När den behövs | Exempel |
|--------|----------------|---------|
| **Dubbel** | Besök som ska utföras tillsammans samma dag (samma kund) | Samma nummer på morgon- och lunchraden som ska göras ihop |
| **Antal tim mellan besöken** | Besök som ska vara **efter** ett annat besök samma dag | På lunchraden: 3,5timmar (om lunch ska vara minst 3,5 h efter frukost) |

När dessa kolumner fylls i i den stora filen får planeringssystemet rätt besöksgrupper och rätt tidsordning mellan besök samma dag.
