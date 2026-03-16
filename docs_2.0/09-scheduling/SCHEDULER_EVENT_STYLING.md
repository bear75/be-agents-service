# Scheduler event styling – exakt specifikation

Detta dokument beskriver exakt hur besökshändelser (visit events) och relaterade element stylas i Bryntum Scheduler Pro i dashboard-appen.

## Datakällor (inga gamla metadata)

- **Kategori (bakgrundsfärg):** `Visit.inset.category` från API (GraphQL `visit.inset.category`). Använd **aldrig** `template.metadata.insatser` för färg.
- **Frekvens (kant + filter):** `VisitTemplate.frequency` från API (GraphQL `visit.template.frequency`). Värden: `daily`, `weekly`, `bi_weekly`, `3_weekly`, `monthly`, `quarterly`, `yearly`, `custom`.
- **Varaktighet:** Visas alltid som **heltal minuter** (rundat från `durationMinutes` eller `endDate - startDate`).

---

## 1. Besökshändelse (visit event) – färger

### Bakgrundsfärg (event bar)

Styrs av **inset-kategori** (`inset.category`). Färger kommer från **central konfiguration** (defaults + env + framtida UI-inställningar), se nedan.

| Kategori (API)      | Bakgrund (hex) | Användning                 |
| ------------------- | -------------- | -------------------------- |
| `personal_care`     | `#93C5FD`      | Personlig vård (blå)       |
| `meals`             | `#FDA4AF`      | Måltider (rosa)            |
| `daily_support`     | `#E2E8F0`      | Dagligt stöd (grå)         |
| `supervision`       | `#C4B5FD`      | Tillsyn (lila)             |
| `social_activities` | `#86EFAC`      | Sociala aktiviteter (grön) |
| `cleaning`          | `#5EEAD4`      | Städning (teal)            |
| `laundry`           | `#7DD3FC`      | Tvätt (cyan)               |
| `shopping`          | `#FDBA74`      | Inköp (orange)             |
| `household`         | `#BEF264`      | Hushåll (lime)             |
| `alarm`             | `#FCA5A5`      | Larm (röd)                 |
| (saknas/null)       | `#E2E8F0`      | Fallback: daily_support    |

Paletten är vald för tydlig åtskillnad: varje kategori har egen nyans och något högre saturation så att de inte smälter ihop i vyn.

Bryntum-fält: `eventColor` (sätts i `assignmentMapper` och i `VisitModel.eventColor` calculate).

### Vänster kant (left border) – frekvens

Styrs av **frekvens** (`visit.template.frequency`). CSS-klass `visit-frequency-{class}`; färger sätts via CSS-variabler från samma centrala config (se nedan).

| Frekvens (API)        | CSS-klass                                             | Kantfärg (hex)     |
| --------------------- | ----------------------------------------------------- | ------------------ |
| `daily`               | `visit-frequency-daily`                               | `#3b82f6` (blå)    |
| `weekly`              | `visit-frequency-weekly`                              | `#22c55e` (grön)   |
| `bi_weekly`           | `visit-frequency-biweekly`                            | `#f59e0b` (gul)    |
| `3_weekly`            | `visit-frequency-3weekly`                             | `#ec4899` (rosa)   |
| `monthly` / `4weekly` | `visit-frequency-4weekly` / `visit-frequency-monthly` | `#8b5cf6` (lila)   |
| `quarterly`           | `visit-frequency-quarterly`                           | `#14b8a6` (teal)   |
| `yearly`              | `visit-frequency-yearly`                              | `#6366f1` (indigo) |
| `custom` / övrigt     | `visit-frequency-custom`                              | `#6b7280` (grå)    |

Kant: `border-left: 4px solid <färg> !important;`

---

## 2. Badges på event-baren (labels)

Varje besökshändelse kan visa följande badges (i `eventRenderers.ts`):

| Badge               | Källa               | Innehåll / betydelse                                                                                                                                                                                                                                  |
| ------------------- | ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Kategori**        | `insetCategory`     | Översatt `organization.insets.categoryLabel.{category}` (t.ex. "Personlig vård", "Måltider").                                                                                                                                                         |
| **Frekvenskod**     | `visitFrequency`    | Kort kod med tooltip: **D** = Varje dag, **V** = Varje vecka (veckobesök), **2V** = Varannan vecka, **3V** = Var 3:e vecka, **M** = Månadsvis, **Q** = Kvartalsvis, **Å** = Årsvis, **?** = Anpassad. Tooltip: `scheduler.frequencyCode.{frequency}`. |
| **Prioritet**       | `priority` ≤ 3      | "P1", "P2", "P3" (röd ton).                                                                                                                                                                                                                           |
| **Dubbel personal** | `requiredStaff` ≥ 2 | Endast dubbelikon (fa-users), ingen siffra.                                                                                                                                                                                                           |
| **Låst**            | `pinnedEmployeeId`  | Tumstick-ikon (orange).                                                                                                                                                                                                                               |

Frekvenskoden **V** står alltså för **veckobesök** (Varje vecka).

---

## 3. Varaktighet (duration)

- **Event-bar text:** `(HH:MM – HH:MM) (Xm)` där **X** alltid är **heltal minuter** (beräknat från `durationMS` eller `durationMinutes`, rundat med `Math.round`).
- **Reseblock:** Visar **heltal minuter** (travel).
- **Tooltip:** Varaktighet visas som "X min" med heltal.

Källor: `durationMinutes` från API (rundas i mapper/context), eller `endDate - startDate` i tooltip/renderer (rundat till minuter).

---

## 4. Övriga event-typer

| Typ         | Bakgrund / stil                                           |
| ----------- | --------------------------------------------------------- |
| **Travel**  | Svart bar, höjd 2px, ingen kant. Text: "Xm" (heltal min). |
| **Break**   | Svart bakgrund, ingen kant. Ikon + "Rast".                |
| **Waiting** | Svart bakgrund, ingen kant. Ikon + "Väntar".              |

---

## 5. Filreferenser

| Syfte                      | Fil                                                                                    |
| -------------------------- | -------------------------------------------------------------------------------------- |
| **Central config (källa)** | `apps/dashboard/src/config/scheduler/schedulerAppearanceConfig.ts`                     |
| Kategorifärger             | `visitTypeConfig.ts` (läser från central config); `assignmentMapper`, `VisitModel`     |
| Frekvens-CSS               | `visit-frequency.css` (använder CSS-var från central config)                           |
| Event-färg + badges        | `apps/dashboard/src/components/Scheduler/helpers/eventRenderers.ts`                    |
| Legend (förklaring)        | `SchedulerLegend.tsx` (använder `getCategoryColors()`, `getFrequencyBorderColors()`)   |
| Mappning API → UI          | `assignmentMapper.ts`, `ScheduleDataContext.tsx`                                       |
| Lokalisering               | `scheduler.frequencyCode.*`, `resources.organization.insets.categoryLabel.*` i locales |

---

## 6. Var visa labels (best practice)

- **Legend:** Visas endast i verktygsfältet via **?**-ikonen (HelpCircle). Klick öppnar en popover med förklaring av kategorifärger, frekvenskanter och event-badges. Filterpanelen innehåller ingen legend.
- **Innehåll:** Kategorier (färgruta + namn), frekvens (vänsterkant + kod D/V/2V/M…), ikoner (dubbel personal, låst, P1–P3).
- **Källa:** `getCategoryColors()`, `getFrequencyBorderColors()` (central config), locale-nycklar för etiketter.

---

## 7. Central konfiguration (env + UI-inställningar)

Alla färger och standardvärden för kategorier och frekvenskanter kommer från **en källa**:

**Fil:** `apps/dashboard/src/config/scheduler/schedulerAppearanceConfig.ts`

- **Default:** `DEFAULT_CATEGORY_COLORS`, `DEFAULT_FREQUENCY_BORDER_COLORS` (hardkodade i filen).
- **Env (valfritt):** Överskriv med JSON i miljövariabler:
  - `VITE_SCHEDULER_CATEGORY_COLORS` – partiell merge av kategorifärger, t.ex. `{"meals":{"background":"#XXX"}}`.
  - `VITE_SCHEDULER_FREQUENCY_COLORS` – partiell merge av frekvenskanter, t.ex. `{"daily":"#XXX"}`.
- **UI-inställningar (framtid):** Anropa `setAppearanceOverrides({ categoryColors: {...}, frequencyBorderColors: {...} })` från inställningssidan (t.ex. efter hämtning från API eller localStorage). Getters `getCategoryColors()` och `getFrequencyBorderColors()` returnerar då mergerade värden. För att färger ska uppdateras i vyn kan scheduler/assignments laddas om eller komponenter som använder getters re-rendras.

**Användning:**

- `visitTypeConfig.ts` exporterar `CATEGORY_COLORS = getCategoryColors()` (vid modulladdning).
- `SchedulerLegend` anropar `getCategoryColors()` och `getFrequencyBorderColors()` i render.
- Frekvenskanter i CSS: `visit-frequency.css` använder `var(--scheduler-frequency-daily, #3b82f6)` etc. Variablerna sätts vid scheduler-mount via `applyFrequencyCssVariables()` i `SchedulerContainer`.

---

## 8. Frekvensfilter

Filtervärdet i UI (t.ex. "Daglig") mappas till API-värde `daily`. Filter använder **normaliserad** frekvens:

- `bi-weekly` / `biweekly` → `bi_weekly`
- `4weekly` / `monthly` → `monthly`
- Jämförelse sker mot `record.getData("visitFrequency")` och `record.get("visitFrequency")` (sträng, trimmat, lowercased).
- Om frekvens saknas (null/undefined) visas **inte** händelsen när användaren valt t.ex. "Daglig" (endast matchande frekvenser visas).
