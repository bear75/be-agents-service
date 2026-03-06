# Spåra fel: Source 1 → 2 → 3 → input.json → output

Alla tider ska finnas i source (1). Om resultatet är fel måste vi spåra från 1, 2, 3, input.json.

- **1 → 2 (CSV):** Konvertering Attendo → vår source (gruppering till recurring, frequency).
- **2 → 3 (CSV):** Expansion till planeringsfönster; här sätts **tidsfönster per besök** (minStartTime, maxStartTime, maxEndTime).
- **3 → input.json:** csv_to_timefold_fsr sätter Timefold time windows från expanded.
- **input → output:** Solvern ska ge rätt om input är rätt. Om början är fel kan slutet aldrig bli rätt.

---

## 1. Är felet att vi grupperar fel (weekly x5 vs weekly x1)?

**Nej – vi grupperar inte weekly x5 till ett recurring + ett felaktigt weekly x1.**

- **Attendo (1):** H299 har 5 rader – en per veckodag (mån 12:21, tis 12:25, ons 12:25, tor 12:25, fre 12:25).
- **Source (2):** Vi har **en rad per veckodag**: H299_468 weekly x1 (mån), H299_470 weekly x2 (tis, ons), H299_469 weekly x1 (tor), H299_471 biweekly x1 (fre). Alltså **inte** en enda “weekly x5” och inte heller en “weekly x1 må–sön”.
- **Felet:** I **expansion (2→3)** behandlar vi **alla** “weekly x1”-rader som **helveckofönster** (mån 07:00–sön 19:40). Vi **ignorerar** att source-raden har `recurring_external = "Varje vecka, mån"`. Då får t.ex. H299_468 (måndagsbesöket) ett fönster över hela veckan, och solvern kan lägga det på onsdag – samma dag som H299_470 (ons 12:00–12:25) → två besök samma dag.

**Rätt beteende för extended (2→3):**

- **daily** = 7× weekly med smalt tidsfönster per dag (redan så).
- **weekly x2, x3, x4, x5, x6** = veckodag finns i `recurring_external` → **dag-specifikt fönster**, aldrig samma dag som annat besök för samma kund (redan så för x2–x6).
- **weekly x1** = om `recurring_external` innehåller en veckodag (mån, tis, …, sön) → **samma logik som weekly x2**: ett besök per vecka **på den angivna dagen**, med dag-specifikt fönster. Endast om det verkligen är “1 gång/vecka, valfri dag” (ingen veckodag i source) ska vi använda helveckofönster.

**Implementerad fix:** I `expand_recurring_visits.py` använder vi nu veckodag från `recurring_external` även för **weekly x1**, så att “Varje vecka, mån” ger måndagsfönster, inte helveckofönster.

---

## 2. Morgon (måltid + dusch) ihop med lunch (måltid) – gruppering 1→2

**Risk:** Om scriptet som bygger (2) från (1) **grupperar på samma tid + samma längd** kan två olika besök (frukost vs lunch) slås ihop om de har samma duration (t.ex. 20 min) men olika starttid (08:59 vs 11:17). Då blir det **en** recurring med bred flex (t.ex. 120 min efter) som kan hamna kl 11 – dvs “morgon” som ser ut som lunch.

**I Attendo (1) för H331 onsdag:**

- En rad: 08:59, 20 min, Måltid (morgon).
- En rad: 11:17, 20 min, Måltid (lunch).

Om 1→2-grupperingen **bara** använder (kund, insats typ, tid, längd) och slår ihop rader med “samma” tid (t.ex. avrunda till närmaste 15 min) eller ignorerar tid, kan morgon och lunch bli en grupp → fel.

**Rätt:** Frukost och lunch ska vara **två olika grupper** (olika recurringVisit_id eller olika rader per veckodag). Det blir extra tydligt när det är **samma dag**: två besök samma dag = två rader i (1) med samma veckodag. Då ska (2) ha två rader för den dagen (eller ett recurring med två “occurrences” på samma dag).

**Flex:** Även om grupperingen är rätt kan **120 min flex efter** morgon (08:59 + 120 min = 10:59) göra att morgonbesöket får ett tidsfönster som sträcker sig till 11:00. Då kan solvern placera “morgon” kl 11 – det ser ut som lunch. Där behöver antingen:

- tidsfönster i (3) / input.json begränsas (t.ex. maxStartTime för morgon typ “senast 10:00”), eller  
- flex i (1)/(2) justeras så att morgon inte får 120 min efter på den raden.

**Sammanfattning:** Om morgon och lunch ligger ihop på **samma dag** i (1) som **två rader** men i (2) blir **en** grupp med bred flex → felet är i **1→2 (gruppering)**. Om (2) har två separata besök men morgon får 120 min flex och hamnar 11:00 → felet är **flex/tidsfönster** (1 eller 2→3).

---

## 3. Övriga Martina-fall – förklaring med exempel

### 3.1 Samma mönster som H299 (weekly x1 kolliderar med fast veckodag)

**Exempel: H335** – Måltid+promenad (tisdag) och Dusch (torsdag) på olika slingor samma dag.

- **Orsak:** I (2) finns t.ex. en rad “weekly x1” (eller liknande) utan att veckodag används i (3), så expansionen ger helveckofönster. Solvern lägger då det ena besöket på en dag då kunden redan har ett annat besök → två besök samma dag (ibland på olika slingor).
- **Var:** **Extended (2→3)** – samma bugg som H299: weekly x1 (eller liknande) får helveckofönster istället för dag-bunden.
- **Åtgärd:** Samma fix som för H299: använd veckodag från source för weekly x1 så att besöket bara kan hamna på angiven dag.

### 3.2 Fel tid på dagen (morgon på kvällen, lunch för sent)

**Exempel: H172** morgon 07:42 (diff 5 min) planerad 16:05. **H362** morgon planerad på kvällen. **H095** lunch 90 min före 13:22 planerad 16:10.

- **Två möjliga orsaker:**
  1. **Extended / input:** Tidsfönstret i (3) och input.json är **för brett** (t.ex. morgon med fönster 07:00–17:00). Då är felet i **2→3** eller 3→input (hur vi sätter minStartTime/maxStartTime).
  2. **Output:** Tidsfönstret är **snävt** (t.ex. morgon 07:00–09:00) men solvern sätter ändå besöket 16:05. Då är felet i **output** (solver) – eller att fel jobb hamnat på fel shift (kvällsskift).
- **Spåra:** Jämför i input.json det aktuella besökets time windows med den planerade tiden i output. Om 16:05 ligger **inom** fönstret → problemet är att fönstret är för brett (extended/input). Om 16:05 ligger **utanför** fönstret → bug i solver eller mappning.

### 3.3 Patch

- **Vem:** Steg där vi applicerar Timefold-output till Attendo/Slinga (from-patch, patch_visits_slinga_direct, etc.).
- **Slutsats:** Ingen indikation på att **patch** introducerar dessa fel. Fel som “två besök samma dag” eller “fel tid på dagen” kommer från (2)→(3) eller input→output; patch skickar vidare det som redan är fel.

---

## Snabbreferens: var ligger felet?

| Symptom | Först kolla | Vanlig orsak |
|--------|-------------|--------------|
| Två besök samma dag (samma kund) | (2) har en rad per veckodag? | (3) ger weekly x1 helveckofönster → **Extended** |
| Morgon som hamnar på kvällen | input.json time window för det jobbet | För brett fönster → **Extended/input**; snävt men fel tid → **Output** |
| Två måltider samma dag (t.ex. H331) | (1) har en eller två rader den dagen? | Två rader i (1) → (2) ska ha två; om (2) har en grupp → **1→2**. Om (2) rätt men flex för bred → **Flex/tidsfönster** |
| Back-to-back (för många besök samma dag) | (1) och (2): antal rader per kund/dag | Fler rader i (2) än avsett → **1→2**. Rätt antal men fel dag i (3) → **Extended** |
