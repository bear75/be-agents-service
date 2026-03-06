# Var ligger felet? Attendo-fil vs vår pipeline

**Flöde:**  
(1) **Attendo** `1-Huddinge - Blad1.csv` → (2) **Vår source** `2-Huddinge_caire - Huddinge_recurring_v2.csv` → (3) **Vår extended** `3-...huddinge_2wk_expanded_....csv` → Timefold input → output → patch

**Regel:** Om felet ligger **efter** source (dvs i extended, Timefold input, output eller patch) är det **vår bugg**. Om felet redan finns i **Attendo-filen (1)** är det **Attendos fil**.

---

## H299 (2 besök samma dag 18/2: 09:07 och 12:00)

| Steg | Innehåll |
|------|----------|
| **Attendo (1)** | 5 rader: H299 **mån** 12:21, **tis** 12:25, **ons** 12:25, **tor** 12:25, **fre** (varannan) 12:25. Varje rad = en veckodag med fast tid. **Max ett besök per dag** i filen. |
| **Source (2)** | H299_468 weekly x1 (mån), H299_470 weekly x2 (tis, ons), H299_469 weekly x1 (tor), H299_471 biweekly x1 (fre). Korrekt: en rad per veckodag. |
| **Extended (3)** | Weekly x1 (t.ex. H299_468, H299_469) får i vår expansion ett **helveckofönster** (mån 07:00–sön 19:40). Solvern kan då lägga det besöket **vilken dag som helst**, inklusive onsdag – då H299 redan har ett fast onsdagsbesök (12:00–12:25). → **Två besök samma dag.** |

**Verdikt: Vår bugg (extended).**  
Attendo och source är konsekventa: en veckodag per besök. Felet är att **expansionen** ger weekly x1 ett helveckofönster istället för att binda besöket till den angivna veckodagen.

---

## H331 (2 måltidsbesök 18/2: 10:56 och 11:22)

| Steg | Innehåll |
|------|----------|
| **Attendo (1)** | H331 har **två separata rader för onsdag**: rad 860 "Varje vecka, ons" **08:59** Måltid (20 min), rad 865 "Varje vecka, ons" **11:17** Måltid (20 min). Alltså **två måltidsbesök onsdag** i Attendos fil. |
| **Source (2)** | H331_557 finns med **två** rader för onsdag (olika flex/tider), motsvarande de två Attendo-raderna. |
| **Extended (3)** | Två jobb för H331 på 18/2 (onsdag) → två måltider 10:56 och 11:22. |

**Verdikt: Attendos fil** (om avtalet är “max ett måltidsbesök per dag”).  
Attendo-filen innehåller **två** onsdagsrader för H331 (08:59 och 11:17). Om det ska vara bara **ett** måltidsbesök på onsdag är det **Attendos fil** som är fel. Om två måltider (frukost + lunch) är avsiktligt är datan rätt och eventuellt problem är tidsfönster/ordning (då kan det vara extended/output).

---

## Övriga fall (kort)

- **Weekly x1 som kolliderar med fast veckodagsbesök (t.ex. H335):** Samma mönster som H299 → **vår bugg (extended)**.
- **Flera besök samma dag från flera rader i Attendo:** Om (1) har flera rader samma kund + samma dag = **Attendos fil**. Om (1) bara har en rad men (2) eller (3) skapar flera = **vår bugg (source eller extended)**.
- **Fel tid på dagen (morgon på kvällen, lunch för sent):** Vanligtvis **vår bugg**: antingen **extended** (för breda fönster) eller **output** (solver väljer fel tid inom fönster).

---

## Sammanfattning

| Typ av fel | Var | Vem |
|------------|-----|-----|
| Weekly x1 kan hamna på en dag som redan har besök (H299, H335) | **Extended** | **Vår bugg** |
| Två måltidsbesök samma dag när Attendo har två rader för den dagen (H331) | **Attendo (1)** | **Attendos fil** (om regeln är 1 måltid/dag) |
| Morgon planerad på kvällen / lunch för sent | **Extended** eller **output** | **Vår bugg** |
| Patch/applicering | Ingen indikation på fel här | – |

**Rekommenderad åtgärd (vår sida):**  
1. I expansionen: **weekly x1** ska inte få helveckofönster; antingen binda till angiven veckodag eller begränsa så att det inte kan läggas på en dag som redan har ett annat besök för samma kund.  
2. Eventuellt: constraint eller post-process “max ett besök per kund per dag” (eller per typ).
