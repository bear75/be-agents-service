# H299 – Vad kunden har för besök och hur de grupperas

## Vad kunden (H299) har för besök

I **Attendo (1)** finns för H299 **5 rader** – en rad per veckodag:

| Veckodag | Starttid | Längd | Insatser        |
|----------|----------|-------|-----------------|
| Mån      | 12:21    | 130   | Bad/Dusch, Måltid, Promenad |
| Tis      | 12:25    | 130   | Måltid, Promenad |
| Ons      | 12:25    | 130   | Måltid, Promenad |
| Tor      | 12:25    | 140   | Bad/Dusch, Måltid, Promenad |
| Fre      | 12:25    | 140   | Måltid, Promenad (varannan vecka) |

Alltså: **ett besök per dag**, olika dagar, ungefär samma tid (lunch). Kunden ska alltså **aldrig** ha två besök samma dag.

---

## Hur vi grupperar (1 → 2)

Vi **grupperar inte** alla 5 till ett enda “weekly x5” och ett “weekly x1 må–sön”.

I **source (2)** har vi **fortfarande en rad per veckodag**, men med ett mönster-id (recurringVisit_id) och en frekvensetikett:

| Rad   | recurringVisit_id | frequency   | recurring_external   | Betydelse              |
|-------|-------------------|-------------|----------------------|------------------------|
| 1     | 468               | weekly x1   | Varje vecka, **mån**  | Ett besök/vecka, måndag |
| 2–3   | 470               | weekly x2   | Varje vecka, **tis** / **ons** | Två besök/vecka, tisdag + onsdag |
| 4     | 469               | weekly x1   | Varje vecka, **tor**  | Ett besök/vecka, torsdag |
| 5     | 471               | biweekly x1 | Varannan vecka, **fre** | Ett besök varannan vecka, fredag |

- **weekly x1** = “1 gång per vecka” – och **vilken dag** står i `recurring_external` (mån, tor).
- **weekly x2** = “2 gånger per vecka” – tisdag och onsdag (två rader med samma 470).
- Vi skapar **inte** en extra rad “weekly x1 må–sön” (valfri dag). Varje rad är kopplad till **en specifik veckodag**.

---

## Vad som gick fel i extended (2 → 3)

I extended ska varje rad bli **konkreta besök med tidsfönster** i planeringsveckorna.

- **Rätt:** Raden “weekly x1, Varje vecka, mån” ska bli besök **endast på måndagar** med ett snävt tidsfönster (t.ex. 12:21 ± flex).
- **Fel (tidigare):** Vi behandlade **alla** “weekly x1”-rader som “1 besök någon dag i veckan” och gav ett **helveckofönster** (mån 07:00–sön 19:40) och **ignorerade** “Varje vecka, mån”. Då kunde optimeraren lägga **måndagsbesöket** (rad 468) på **onsdag** – och onsdag har H299 redan ett fast besök (rad 470, 12:00–12:25). Resultat: **två besök samma dag** (09:07 och 12:00).

Så: **Vi skapar inte “må–sön” som extra mönster.** Felet var att de **befintliga** weekly x1-raderna (mån, tor) fick **helveckofönster** istället för att vara bundna till just måndag respektive torsdag.

---

## Om vi *hade* grupperat weekly x5 + weekly x1

Om vi **hade** grupperat så här:

- Ett “weekly x5” (mån–fre) med snäva tidsfönster från source, **och**
- Ett “weekly x1” (må–sön) med valfri dag,

då hade extended fått både:

1. **Mån, tis, ons, tor, fre** med snäva fönster (rätt), och  
2. **Ett extra besök** med helveckofönster (fel – det skulle inte finnas).

Då hade felet varit i **grupperingen (1→2)**. Men så gör vi **inte**: vi har ingen “weekly x5”-grupp och ingen “weekly x1 må–sön”. Vi har bara **en rad per veckodag**, och felet var att **weekly x1 ska vara en specifik dag och tid** – det har vi nu åtgärdat i expansionen (2→3) genom att använda veckodag från `recurring_external` även för weekly x1.
