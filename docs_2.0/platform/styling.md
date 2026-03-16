# Plattformssidor – Styling Guide

Denna guide harmoniserar marknadssidorna under `public/platform/**` så att de följer CAIRE:s brand manual (`docs/4. Reference/styling-branding.md`) och de senaste referenssidorna `ai-os-business.html` och `ai-os-system.html`. Målet är ett konsekvent glasiga skal, tydlig hero-struktur, mjukt tonade bakgrunder och korrekt bildanvändning för både svenska och engelska sidor.

---

## 1. Grundlayout & Typografi

- **Basbakgrund:** `linear-gradient(135deg, #f5f7fa 0%, #ebe7ff 100%)` för hela sidan. Sektioner kan växla till ren vit bakgrund (`#ffffff`) för kontrast.
- **Typografi:** Inter (300/400/600/700) med textfärg `#1f2937` (Slate-900). Sekundär text `#475569`–`#4b5563`.
- **Glasytor:** Använd glasmorfism-komponenter:
  - Bakgrund: `rgba(255,255,255,0.85–0.95)`
  - Border: `1px solid rgba(37, 99, 235, 0.12–0.18)` beroende på accent
  - Skugga: `0 16px 44px rgba(15, 23, 42, 0.1–0.14)` samt lätt blur (`backdrop-filter: blur(10px)`)
- **Grid & spacing:** Maxbredd `1400px`, `padding: 0 20px`, sektioner `padding: 90px 20px` (70px på ≤768px).
- **CTA-knappar:** Primär `linear-gradient(135deg, #2563EB 0%, #9333EA 100%)`; sekundär genomskinlig/outline enligt `styling-branding.md`.

---

## 2. Navbar

- **Placering:** `position: sticky; top: 0;` med glasbakgrund `rgba(255,255,255,0.94)` och `backdrop-filter: blur(12px)`.
- **Innehåll:** Logo (gradient), språkknappar (`EN`/`SV`), “Book demo”/”Boka demo” CTA och ev. snabbnavigation.
- **Hover:** Upphöjd känsla (`transform: translateY(-2px); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25)`).
- **Script:** `common-navbar.js` ska injicera nav i varje sida ‒ håll markup identiskt och undvik duplicerad HTML.
- **Schemaläggningens undermeny:** Använd etiketter `Overview`, `Daily Scheduling`, `Pre-Planning` (EN) respektive `Översikt`, `Dagsplanering`, `Förplanering` (SV). `overview`-länken pekar på huvudschemametodiken.
- **AI OS-markering:** Desktop- och mobilmenyn använder `title="Vision"` (EN) / `title="Vision"` (SV) för hover-tooltip. Länken har ljus bakgrund (`rgba(37,99,235,0.08)`), tunn border (`1px solid rgba(37,99,235,0.18)`) och subtil skugga för att signalera framtidsvision utan badge.

---

## 3. Hero-sektion

- **Layout:** Tvåkolumnig flex (`.hero-layout`) med text vänster, bild höger. På mobil staplas innehållet.
- **Tagline-pill:** `display: inline-flex; border-radius: 999px; background: rgba(37, 99, 235, 0.12); color: #2563EB; font-weight: 600;`
- **Rubrik:** Gradienttext (`gradient 135° från #0EA5E9 → #22C55E` eller brand-blå→lila). Storlek 56px desktop, 32px mobil.
- **Hero-copy:** Maxbredd 520–860px, `font-size: 20px`.
- **CTA-grupp:** Flex med `gap: 18px`. Primärknapp gradient, sekundär outline.
- **Hero-card:** Bildcontainer `border-radius: 24px`, `box-shadow: 0 28px 70px rgba(15, 23, 42, 0.38)`, `border: 1px solid rgba(148, 163, 184, 0.28)`, `overflow: hidden`.
- **AI OS-intro:** På AI OS-sidorna lägg till ett `p.hero-future-note` direkt efter hero-copy. Texten ska vara kort – använd “The Vision” (EN) / “Visionen” (SV) för att signalera framtidsinnehållet utan extra förklaringar.

### Hero-bilder per sida

| Sida             | Språk | Hero-bild                                       | Fil                         | Alt-text (engelska & svenska varianter)                                                                                                    |
| ---------------- | ----- | ----------------------------------------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Plattform Index  | EN    | `/images/CAIRE-AI-OS/caire-future-hq.png`       | `caire-future-hq.png`       | “CAIRE platform overview hero” / “CAIRE plattform övergripande vy”                                                                         |
| Plattform Index  | SV    | `/images/CAIRE-AI-OS/caire-future-hq.png`       | `caire-future-hq.png`       | Samma som ovan (svensk alt-text)                                                                                                           |
| AI OS Business   | EN    | `/images/CAIRE-AI-OS/ai-brain-ecosystem.jpg`    | `ai-brain-ecosystem.jpg`    | “Caire AI business ecosystem visualization” / “Visualisering av Caires AI-ekosystem för affären”                                           |
| AI OS Business   | SV    | `/images/CAIRE-AI-OS/ai-brain-ecosystem.jpg`    | `ai-brain-ecosystem.jpg`    | Samma alt-text spelad på svenska                                                                                                           |
| AI OS System     | EN    | `/images/CAIRE-AI-OS/caire-AI.png`              | `caire-AI.png`              | “Technical visualization of the CAIRE AI operating system” / “Teknisk visualisering av CAIRE:s AI-operativsystem”                          |
| AI OS System     | SV    | `/images/CAIRE-AI-OS/caire-AI.png`              | `caire-AI.png`              | Samma alt-text spelad på svenska                                                                                                           |
| Resources        | EN/SV | `/images/CAIRE-AI-OS/blue-hands-heart-chip.png` | `blue-hands-heart-chip.png` | “Hands holding AI heart chip representing resource center” / “Händer som håller AI-hjärtechip för resurscentret”                           |
| Scheduling       | EN/SV | `/images/CAIRE-AI-OS/caire-heart-chip.jpg`      | `caire-heart-chip.jpg`      | “Glowing CAIRE heart chip illustrating the scheduling platform” / “Glödande CAIRE-hjärtechip som representerar schemaläggningsplattformen” |
| Daily Scheduling | EN/SV | `/images/CAIRE-AI-OS/blue-ai-heart-power.png`   | `blue-ai-heart-power.png`   | “AI-optimized scheduling interface illustration” / “Illustration av AI-optimerad schemaläggning”                                           |
| Analytics        | EN/SV | `/images/CAIRE-AI-OS/blue-brain-ai.png`         | `blue-brain-ai.png`         | “CAIRE analytics intelligence visualization” / “CAIRE-visualisering av analysintelligens”                                                  |
| Pre-planning     | EN/SV | `/images/CAIRE-AI-OS/caire-flywheel-2.0.png`    | `caire-flywheel-2.0.png`    | “Pre-planning flywheel illustration” / “Illustration av förplaneringens flywheel”                                                          |

> **Notera:** Hero-bildsväljare kan justeras vid iterativ redesign. Uppdatera tabellen vid byte för att hålla docs i synk.

---

### 3.1 AI OS-sidors struktur

- **Affärssida (`ai-os-business.html`):** Följ narrativ ordning – Definition → Problem → Varför nu → Marknad → Lösning → Roadmap → Konkurrens → Varför CAIRE vinner → Affärsmodell. Lägg in `div.ai-os-vision-placeholder` för visionära visuals i lösningssektionen; ersätts senare med faktisk grafik.
- **System-/techsida (`ai-os-system.html`):** Ordning – Hero → AI OS-mognadsnivåer (tabell) → Arkitekturöversikt → Datamodellens fundament → Tekniska pelare → Infrastruktur & efterlevnad → Systemets dataflywheel & guardrails → Teknikstack → Nästa steg.
- **Bildplatshållare:** Använd kommentaren `<!-- Vision Visual Placeholder -->` eller motsvarande wrapper för framtida diagram (t.ex. roadmap, dataflywheel). Håll samma namn på både EN och SV för enkel ersättning.
- **Framtidsnotis:** Både business- och system-sidor visar hero-notis som tydliggör att AI OS är en framtidsvision medan plattformsflikarna täcker dagens produkt.

---

## 4. Sektioner & Cards

- **Sektionstitlar:** `font-size: 42–44px`, centrerad, `margin-bottom: 16px`. Undertext `font-size: 20px`, maxbredd 820–900px.
- **Cards:** `border-radius: 18–20px`, `padding: 30–32px`, `box-shadow: 0 14px 40px rgba(15, 23, 42, 0.08)`.
  - Hover: `transform: translateY(-6px); box-shadow: 0 18px 50px rgba(15, 23, 42, 0.12)`
  - “Pill”-etiketter (`.pill`): `inline-flex`, gradient- eller blåtonad bakgrund, `font-size: 13px`.
- **Timeline-block:** Lodrät linje med gradient `rgba(16,185,129,0.2) → rgba(59,130,246,0.2)`. Item cards glasiga med `border: 1px solid rgba(37, 99, 235, 0.08–0.14)`.
- **Diagrams:** Använd `<pre class="mermaid">` med modulär import (`mermaid@10`). Håll container `max-width: 1080px`, glasbakgrund, centrerad text.

---

## 5. Bildanvändning & Skärmdumpar

- **Källa:** Alla hero- och stödvisualiseringar hämtas från `public/images/CAIRE-AI-OS`. Använd `.png/.jpg/.webp` i denna mapp först; `.avif` för lättvikt.
- **Skärmdumpar:** För process- och produktvisning används “blurred” varianterna från `public/platform/Screenshots`.
  - Använd `*_blurred.png` i hero-sektioner eller bakgrundskort där känsliga uppgifter kan förekomma.
  - Visa “skarpa” versioner (`*.png` utan `blurred`) endast i avsnitt där detaljer är viktiga och datan är anonymiserad/okänslig.
- **Bildattribut:** `loading="lazy"` på alla `<img>`. `alt`-texter ska ha svensk standardtext, komplettera med engelska när sidan är på engelska.
- **Bildstorlek:** Hero-bilder kan sträcka sig upp till 600 px för tydligare visuellt fokus. Inlinebilder som kompletterar brödtext ska använda `width: clamp(180px, 26vw, 320px)` och bör aldrig uppta mer än 40 % av bredden i desktopläge. Diagramkort kan gå upp till 1000 px. Använd alltid `object-fit: cover`.
- **Integrerad layout:** Bygg text- och bildblock med en gemensam wrapper `.section-content`. Använd grid: `display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(0, 0.9fr); gap: 48px; align-items: center;`. Placera den textbärande delen i `.section-text` och bilden i `.section-figure`.
- **Alternating pattern:** För att undvika “afterthought”-känsla ska sektioner alternera bildens position. På varannan sektion sätt `.section-content.inverse` och byt ordning med `grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.35fr);` eller `order`-klasser.
- **Responsivitet:** På ≤768 px sätter `.section-content` om till en kolumn (`grid-template-columns: 1fr; gap: 28px;`) och `.section-figure` placerar sig under rubriken men före sekundärtext. Se till att bilden då fyller bredden men håll kvar `max-width: 420px` och centrera med `margin: 0 auto`.
- **Figurer & bildtexter:** Använd `<figure class="section-figure">` och `<figcaption>` när bilden förklarar data eller flöden. Bildtexten ska ha `font-size: 13px; color: #64748B; margin-top: 12px; max-width: 320px`.
- **Inline-bildkomposition:** Följ glasmorfismens tonalitet (ljusa highlights, blå-lila accent) och använd `border-radius: 16px` + subtil skugga (`0 18px 40px rgba(15, 23, 42, 0.22)`).

### Rekommenderade inline-bilder per sida

- **Platform Home (`index.html`):**
  - `running-caregiver.png` för texter om personalstress / “Staff Burnout”.
  - `admin-chaos-caregiver.png` vid avsnitt om administrativt kaos.
  - `ai-ticking-bomb.png` för samhälls-/systemiska utmaningar.
  - `ai-caire-stetoscope.png` som visualisering av CAIRE-lösningen.
  - `data-flywheel.png` när flywheel/“data free tier”-strategin beskrivs.
  - `40-percent-cost-increase.png` för statistik/kostnadsproblematik.
- **AI OS Business (`ai-os-business.html`):**
  - `ai-robot-rocket.png` till roadmap-/tillväxt- eller lanseringssektioner.
  - `blue-ai-heart-power.png` för avsnitt om AI-impact på personal/kunder.
  - `caire-futuristic-ai-person.png` när framtida operativmodeller beskrivs.
  - `data-flywheel.png` i stycke om värdedrivande data/fre-tierinsikter.
- **Resources (`resources.html`):**
  - `blue-hands-heart-chip.png` utanför heron för kompetens-/resurshantering.
- **Analytics (`analytics.html`):**
  - `blue-brain-ai.png` i sektioner som lyfter AI-insikter eller dashboards.
- **Flywheel-/Free-tier-avsnitt (över flera sidor):**
  - Återanvänd `data-flywheel.png` där gratisnivå och datainsamling förklaras.

---

## 6. Färg & Accent

- **Primärgradient:** `var(--brand-gradient)` = `linear-gradient(135deg, #2563EB 0%, #9333EA 100%)`.
- **Sektionstoner:** Hämta från `sectionColors.ts` när tabeller/diagram vill ha färgaccent (t.ex. Scheduling Original = blå, Optimized = grön).
- **Pills & badges:** Följ brandguiden – informationspills i blå/lila, framgångsbudskap i grön gradient, varningar i amber.

---

## 7. Responsivitet

- **Breakpoint 1024px:** Sänk hero-font till 40px, justera card-grid till två kolumner.
- **Breakpoint 768px:** Stapla hero, centrera text, `padding` 70px per sektion, `cta-buttons` kolumn.
- **Breakpoint 480px:** Öka inre `padding` i kort till 24px, rubriker 28–30px.

---

## 8. Lokalisering

- **Språkbrytning:** `lang="sv"` på svenska filer, `lang="en"` på engelska.
- **Copy:** Översätt all text manuellt; ingen maskinöversättning i produktion. Hero alt-texter ska följa lexikon ovan och uppdateras vid copy-ändring.
- **CTA:** “Book Demo” ↔ “Boka Demo”, “Explore” ↔ “Utforska”, etc. Se `public/platform/sv/**/*.html` som referens.

---

## 9. Kvalitetssäkring

- **Tillgänglighet:** Säkerställ AA-kontrast för text på gradientbakgrunder. Lägg till `focus-visible` ringar.
- **Prestanda:** Optimera bilder via `next/image` när de flyttas till applikationen. På statiska HTML-sidor komprimera via `.webp` eller `.avif` när möjligt.
- **Versionering:** Uppdatera “Last Updated” i sidfot när layouten förändras. Senaste referens: 7 november 2025.

---

## 10. Checklista vid nya plattformssektioner

1. Välj hero-bild från CAIRE-AI-OS-mappen (revidera tabellen ovan).
2. Skapa nav enligt `common-navbar.js`.
3. Sätt bakgrundsgradient och glasmorfism-block.
4. Strukturera innehållet med `.section`-block, card grids och timeline där relevant.
5. Lägg in relevanta “blurred” skärmdumpar i storytelling-delar.
6. Säkerställ svenska baseline-texter och en uppdaterad engelsk version om sidan har `lang="en"`.
7. Kör Lighthouse för tillgänglighet och layoutfeedback.

Genom att följa denna guide får samtliga plattforms- och marknadssidor en enhetlig premiumkänsla som matchar CAIRE:s produktupplevelse.
