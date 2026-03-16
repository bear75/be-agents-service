# Caire Hybrid Menu System: Requirements & Implementation

This document consolidates all navigation requirements, implementation details and current status of the hybrid menu system.

## 1. Overview & Goals

The Caire website uses a 2-level hybrid navigation system:

- **Desktop**: Top bar + mega-menus for Product and Resources
- **Mobile**: Hamburger → accordion (only one nested level)
- "Book demo" CTA always visible
- Swedish and English language support throughout

Key objectives:

- Simplify navigation for better UX (especially on mobile)
- Create a logical "topic-cluster" architecture for stronger SEO signals
- Ensure no existing link equity is lost through proper redirects

## 2. Menu Structure

### Desktop Navigation

```
┌logo── Home │ Product▼ │ Solutions▼ │ Resources▼ │ About │ \[Book demo]
```

- **Product** dropdown: Shows full-width mega-menu with:
  - Overview column (title + description + CTA)
  - Features column with child links
  - Services column with child links
- **Solutions** dropdown: Shows simpler menu with:
  - Solutions overview
  - Child solution pages
- **Resources** dropdown: Shows full-width mega-menu with:
  - Overview column (title + description)
  - Category columns: Guides, Comparisons, Whitepapers, Blog

### Mobile Navigation

- Hamburger icon on < 768px
- Accordion shows second level only
- No third level in accordion
- Example: Tapping "Product" reveals:
  - Overview
  - Features
  - Integrations
  - Services & Support

### Footer Structure

```
┌────────────────────────────────────────────────────────────────────────────┐
│  CTA bar  • "Ready to optimise your home-care schedules?"  [Book demo]     │
├────────────────────────────────────────────────────────────────────────────┤
│  Product           Solutions           Resources            Company        │
│  – Overview        – Private HC        – Guides             – About        │
│  – Features        – Chain             – Whitepapers        – Contact      │
│  – Integrations    – Scheduler         – Blog               – FAQ          │
│  – Services & Sup. – Ops-manager       – Comparisons                       │
├────────────────────────────────────────────────────────────────────────────┤
│  [ISO 27001] [GDPR] [WCAG]                                                 │
├────────────────────────────────────────────────────────────────────────────┤
│  © 2025 EirTech AB  |  Privacy | Terms | Cookies | LinkedIn                │
└────────────────────────────────────────────────────────────────────────────┘
```

Mobile footer becomes stacked (1-column) with expandable sections.

## 3. URL Structure & Routes

| Menu group        | Label → Path (sv / en)                                                                                                     | Status     |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------- | ---------- |
| **Home**          | `/` / `/en`                                                                                                                | ✅ Working |
| **Product**       | Overview `/produkter` / `/en/products`                                                                                     | ✅ Working |
|                   | **Features index** `/produkt/funktioner` / `/en/product/features`                                                          | ✅ Working |
|                   | AI Scheduling `/produkt/funktioner/ai-schemalaggning` / `/en/product/features/ai-scheduling`                               | ✅ Working |
|                   | Route Optimisation HC `/produkt/funktioner/ruttoptimering-hemtjanst` / `/en/product/features/route-optimization-home-care` | ✅ Working |
|                   | Administration `/produkt/funktioner/administration` / `/en/product/features/administration`                                | ✅ Working |
|                   | Analytics `/produkt/funktioner/analysverktyg` / `/en/product/features/analytics`                                           | ✅ Working |
|                   | Integrations `/produkt/integrationer` / `/en/product/integrations`                                                         | ✅ Working |
|                   | **Services & Support index** `/produkt/tjanster` / `/en/product/services`                                                  | ✅ Working |
|                   | Extra Integrations `/produkt/tjanster/extra-integrationer` / `/en/product/services/extra-integrations`                     | ✅ Working |
|                   | Web Dev `/produkt/tjanster/webb-utveckling` / `/en/product/services/web-dev`                                               | ✅ Working |
|                   | Digital Handbook `/produkt/tjanster/personalhandbok` / `/en/product/services/employee-handbook`                            | ✅ Working |
| **Solutions**     | Index `/losningar` / `/en/solutions`                                                                                       | ✅ Working |
|                   | Private home-care `/losningar/privat-hemtjanst` / `/en/solutions/private-home-care`                                        | ✅ Working |
|                   | Home-care chain `/losningar/hemtjanstkedja` / `/en/solutions/home-care-chain`                                              | ✅ Working |
|                   | Scheduler persona `/losningar/samordnare` / `/en/solutions/scheduler`                                                      | ✅ Working |
|                   | Ops-manager persona `/losningar/verksamhetschef` / `/en/solutions/operations-manager`                                      | ✅ Working |
| **Resources**     | Index `/resurser` / `/en/resources`                                                                                        | ✅ Working |
|                   | Guides index `/resurser/guider` / `/en/resources/guides`                                                                   | ✅ Working |
|                   | Comparisons index `/resurser/jamforelser` / `/en/resources/comparisons`                                                    | ✅ Working |
|                   | Whitepapers `/resurser/whitepapers` / `/en/resources/whitepapers`                                                          | ✅ Working |
|                   | Blog (placeholder) `/resurser/blogg` / `/en/resources/blog`                                                                | ✅ Working |
| **About**         | `/om-oss` / `/en/about`                                                                                                    | ✅ Working |
| **CTA Book demo** | `/kontakt` / `/en/contact`                                                                                                 | ✅ Working |

### Redirect Scheme

| From                | To                          | Status          |
| ------------------- | --------------------------- | --------------- |
| `/funktioner`       | `/produkt/funktioner`       | 301 (permanent) |
| `/tjanster`         | `/produkt/tjanster`         | 301             |
| `/funktioner/:slug` | `/produkt/funktioner/:slug` | 301             |
| `/en/features/...`  | `/en/product/features/...`  | 301             |
| `/en/services/...`  | `/en/product/services/...`  | 301             |

## 4. Technical Implementation

### Components

- **MainNav.tsx**: Top bar navigation, desktop + mobile toggle
- **MegaMenu.tsx**: Generic panel; props: title, description, columns
- **MobileAccordion.tsx**: Renders level-2 lists
- **Footer.tsx**: CTA bar + link columns + legal

### Configuration

All menu data is driven by `navConfig.ts` which centralizes navigation paths, labels, and structure for reuse across components.

### Accessibility

- Full keyboard navigation
- Focus trapping in mega-menus
- ARIA attributes
- Proper semantics (`role="navigation"`)
- Escape key closes menus

### Technical Considerations

- Uses React Router DOM v6
- Fully responsive with CSS grid and Tailwind
- Language support via i18next with automatic routing
- SEO-optimized with breadcrumb schema

## 5. Implementation Status & Fixes

1. **Fixed footer translations**
   - Updated to use `getLocalizedPath` utility instead of hardcoded paths
   - Fixed namespace handling to properly support both languages
   - Added correct translation for whitepapers in resources section

2. **Simplified menu labels**
   - Changed "Products Overview" to just "Overview" for better UI consistency
   - Similarly updated "Resources Overview" to just "Overview" for consistency
   - Enhanced MegaMenu component to properly handle overview links

3. **Fixed Swedish language support**
   - Fixed translation utility functions to properly return translated text
   - Updated navConfig.ts to correctly use translation namespaces
   - Fixed all components to use the appropriate translation functions
   - Enhanced i18n configuration to prioritize loading critical namespaces

4. **Route path fixes**
   - Updated all route paths to match the specifications
   - Added missing routes in routes.ts
   - Fixed several path inconsistencies for better language support

## 6. UI/UX Enhancements

- Completely opaque black (#000000) menu backgrounds for better readability
- Consistent styling between Products and Resources dropdowns
- Solid header border to ensure menu visibility
- Hover effects with animated underlines for better UX
- Fixed issues with dropdowns disappearing when moving to sub-items
- Enhanced delay mechanism to keep menus open during navigation

## 7. Future Improvements

- Enable third-level mobile navigation for deeper content structures
- Add breadcrumb navigation for improved SEO and user orientation
- Implement split-testing on the CTA position and wording
- Add real-time analytics on menu usage patterns
- Consider sticky navigation on scroll

## 8. Exact menu-mapping for every page

### Var hamnar **`For-verksamheten.tsx`?**

| Fil                              | Roll                                           | Menyplacering                                                                          |
| -------------------------------- | ---------------------------------------------- | -------------------------------------------------------------------------------------- |
| `src/pages/For-verksamheten.tsx` | **Lösning → Scheduler-persona** (”Samordnare”) | _Desktop:_ **Solutions ▸ Scheduler persona** • *Mobil:* ☰ → **Solutions** → Scheduler |

Den sidan fortsätter alltså representera persona-caset _“Samordnare i hemtjänsten”_ och länkas:

- direkt i Solutions-dropdown på desktop
- via accordion-val “Scheduler persona” på mobil
- som kort på `/losningar` landningssidan
- i footer-kolumnen **Solutions**

---

## Komplett sidinventering (54 st) med **hybrid-meny-mappning**

**UPPDATERAD INVENTERING - Faktiska filer funna i systemet**

| #                          | Fil / innehåll                                  | **SV / EN-route**                                                                                                                      | **Desktop-meny**                 | **Mobil** (tapp-sekvens) | **Footer-kolumn** | Status     |
| -------------------------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- | ------------------------ | ----------------- | ---------- |
| **HUVUDSIDOR**             |
| 1                          | `Index.tsx` – Hem                               | `/` / `/en`                                                                                                                            | Home                             | 1 tap Home               | CTA-rad           | EXISTING   |
| **PRODUKTSEKTIONEN**       |
| 2                          | `Produkter.tsx` – Översikt                      | `/produkter` / `/en/products`                                                                                                          | Product ▸ **Overview**           | ☰ → Product             | Product           | EXIST      |
| 3                          | `Features.tsx` – Funktions­översikt             | `/produkt/funktioner` / `/en/product/features`                                                                                         | Product ▸ **Features**           | Product → Features       | Product           | EXIST      |
| 4                          | `Features/Scheduling.tsx` – AI-schemaläggning   | `/produkt/funktioner/ai-schemalaggning` / `/en/product/features/ai-scheduling`                                                         | **i mega-meny** under Features   | card på /funktioner      | —                 | EXIST      |
| 5                          | `Features/RouteOptimizationHomeCare.tsx`        | `/produkt/funktioner/ruttoptimering-hemtjanst` / `/en/product/features/route-optimization-home-care`                                   | dito                             | card                     | —                 | EXIST      |
| 6                          | `Features/Administration.tsx`                   | `/produkt/funktioner/administration` / `/en/product/features/administration`                                                           | dito                             | card                     | —                 | EXIST      |
| 7                          | `Features/Analytics.tsx`                        | `/produkt/funktioner/analysverktyg` / `/en/product/features/analytics`                                                                 | dito                             | card                     | —                 | EXIST      |
| 8                          | `Features/Integrations.tsx`                     | `/produkt/integrationer` / `/en/product/integrations`                                                                                  | Product ▸ **Integrations**       | Product → Integrations   | Product           | EXIST      |
| 9                          | `Features/AiSchedulingCarefox.tsx`              | `/produkt/funktioner/ai-schemalaggning-carefox` / `/en/product/features/ai-scheduling-carefox`                                         | **i mega-meny** under Features   | card på /funktioner      | —                 | NEW        |
| 10                         | `Features/AiStaffPlanning.tsx`                  | `/produkt/funktioner/ai-personalplanering` / `/en/product/features/ai-staff-planning`                                                  | **i mega-meny** under Features   | card på /funktioner      | —                 | NEW        |
| 11                         | `Features/Onboarding.tsx`                       | `/produkt/funktioner/onboarding` / `/en/product/features/onboarding`                                                                   | **i mega-meny** under Features   | card på /funktioner      | —                 | NEW        |
| 12                         | `Features/OnboardingCaireCarefox.tsx`           | `/produkt/funktioner/onboarding-caire-carefox` / `/en/product/features/onboarding-caire-carefox`                                       | **i mega-meny** under Features   | card på /funktioner      | —                 | NEW        |
| 13                         | `Tjanster.tsx` – Tjänster (index)               | `/produkt/tjanster` / `/en/product/services`                                                                                           | Product ▸ **Services & Support** | Product → Services       | Product           | EXIST      |
| 14                         | `Tjanster/Integrationer.tsx`                    | `/produkt/tjanster/extra-integrationer` / `/en/product/services/extra-integrations`                                                    | visa som kort i Services-panelen | card                     | —                 | EXIST      |
| 15                         | `Tjanster/Webb.tsx`                             | `/produkt/tjanster/webb-utveckling` / `/en/product/services/web-dev`                                                                   | kort                             | card                     | —                 | EXIST      |
| 16                         | `Tjanster/Personalhandbok.tsx`                  | `/produkt/tjanster/personalhandbok` / `/en/product/services/employee-handbook`                                                         | kort                             | card                     | —                 | EXIST      |
| **LÖSNINGSSEKTIONEN**      |
| 17                         | `For-verksamheten.tsx` – Lösningar index        | `/losningar` / `/en/solutions`                                                                                                         | Solutions ▸ (klick)              | ☰ → Solutions           | Solutions         | EXIST      |
| 18                         | `Solutions/PrivateHomeCare.tsx`                 | `/losningar/privat-hemtjanst` / `/en/solutions/private-home-care`                                                                      | Solutions ▸ Private              | Solutions → Private      | Solutions         | EXIST      |
| 19                         | `Solutions/HomeCareChain.tsx`                   | `/losningar/hemtjanstkedja` / `/en/solutions/home-care-chain`                                                                          | Solutions ▸ Chain                | Solutions → Chain        | Solutions         | EXIST      |
| 20                         | `Solutions/SchedulerPersona.tsx`                | `/losningar/samordnare` / `/en/solutions/scheduler`                                                                                    | Solutions ▸ Scheduler            | Solutions → Scheduler    | Solutions         | EXIST      |
| 21                         | `Solutions/OperationsManagerPersona.tsx`        | `/losningar/verksamhetschef` / `/en/solutions/operations-manager`                                                                      | Solutions ▸ Ops-manager          | Solutions → Ops-manager  | Solutions         | EXIST      |
| **RESURSSEKTIONEN**        |
| 22                         | `Resurser.tsx` – Resurser index                 | `/resurser` / `/en/resources`                                                                                                          | Resources ▸ (klick)              | ☰ → Resources           | Resources         | EXIST      |
| 23                         | `Resurser/Guides.tsx` – Guider index            | `/resurser/guider` / `/en/resources/guides`                                                                                            | Resources ▸ Guides               | Resources → Guides       | Resources         | BROKEN     |
| 24                         | `Resurser/implementeringsguide.tsx`             | `/resurser/guider/implementeringsguide` / `/en/resources/guides/implementation-guide`                                                  | Resources ▸ Guides (kort)        | Guides card              | —                 | BROKEN     |
| 25                         | `Resurser/steg-for-steg-ai-schemaläggning.tsx`  | `/resurser/guider/steg-for-steg-ai-schemaläggning` / `/en/resources/guides/step-by-step-ai-scheduling`                                 | Resources ▸ Guides (kort)        | Guides card              | —                 | BROKEN     |
| 26                         | `Resurser/Comparisons.tsx` – Jämförelser index  | `/resurser/jamforelser` / `/en/resources/comparisons`                                                                                  | Resources ▸ Comparisons          | Resources → Comparisons  | Resources         | BROKEN     |
| 27                         | `Resurser/jamforelse-schemalaggningssystem.tsx` | `/resurser/jamforelser/jamforelse-schemalaggningssystem-hemtjanst` / `/en/resources/comparisons/home-care-scheduling-tools-comparison` | Resources ▸ Comparisons (kort)   | card                     | —                 | BROKEN     |
| 28                         | `Resurser/SchedulingSystemsComparisonPage.tsx`  | **DUPLICATE - DELETE**                                                                                                                 | **DUPLICATE**                    | **DUPLICATE**            | —                 | DUPLICATE  |
| 29                         | `Resurser/CarefoxVsCarePage.tsx`                | `/resurser/jamforelser/carefox-vs-caire` / `/en/resources/comparisons/carefox-vs-caire`                                                | Resources ▸ Comparisons (kort)   | card                     | —                 | BROKEN     |
| 30                         | `Resurser/ExcelVsAiPage.tsx`                    | `/resurser/jamforelser/excel-vs-ai` / `/en/resources/comparisons/excel-vs-ai`                                                          | Resources ▸ Comparisons (kort)   | card                     | —                 | BROKEN     |
| 31                         | `Resurser/Articles.tsx` – Artiklar index        | `/resurser/artiklar` / `/en/resources/articles`                                                                                        | Resources ▸ Articles             | Resources → Articles     | Resources         | BROKEN     |
| 32                         | `Resurser/ai-schemaläggning-revolution.tsx`     | `/resurser/artiklar/ai-schemalaggning-revolution` / `/en/resources/articles/ai-scheduling-revolution`                                  | Resources → Articles-feed        | internal link            | —                 | BROKEN     |
| 33                         | `Resurser/framtidens-hemtjanst-trender.tsx`     | `/resurser/artiklar/framtidens-hemtjanst-trender` / `/en/resources/articles/future-home-care-trends`                                   | feed                             | internal                 | —                 | BROKEN     |
| 34                         | `Resurser/AiRiskOrRevolutionPage.tsx`           | `/resurser/artiklar/ai-i-hemtjansten-risk-eller-revolution` / `/en/resources/articles/ai-in-home-care-risk-or-revolution`              | feed                             | internal                 | —                 | BROKEN     |
| 35                         | `Resurser/Whitepapers.tsx`                      | `/resurser/whitepapers` / `/en/resources/whitepapers`                                                                                  | Resources ▸ Whitepapers          | Resources → Whitepapers  | Resources         | EXIST      |
| **FÖRETAGSSEKTIONEN**      |
| 36                         | `About.tsx`                                     | `/om-oss` / `/en/about`                                                                                                                | About                            | ☰ → About               | Company           | EXIST      |
| 37                         | `StaticAbout.tsx`                               | **REVIEW NEEDED**                                                                                                                      | **REVIEW**                       | **REVIEW**               | —                 | NEW        |
| 38                         | `Contact.tsx`                                   | `/kontakt` / `/en/contact`                                                                                                             | (Book-demo-knapp + footer)       | footer-länk              | Company           | EXIST      |
| 39                         | `vanliga-fragor.tsx` – FAQ                      | `/vanliga-fragor` / `/en/faq`                                                                                                          | —                                | footer-länk              | Company           | EXIST      |
| **JURIDISKA SEKTIONEN**    |
| 40                         | `Integritetspolicy.tsx`                         | `/integritetspolicy` / `/en/privacy`                                                                                                   | legal strip                      | legal strip              | Legal             | EXIST      |
| 41                         | `Villkor.tsx`                                   | `/anvandarvillkor` / `/en/terms`                                                                                                       | legal strip                      | legal strip              | Legal             | EXIST      |
| 42                         | `Unsubscribe.tsx`                               | `/avregistrera` / `/en/unsubscribe`                                                                                                    | —                                | — (länk via e-post)      | —                 | EXIST      |
| **SYSTEMSIDOR**            |
| 43                         | `404.tsx`                                       | `/404`                                                                                                                                 | —                                | —                        | —                 | EXIST      |
| 44                         | `Auth.tsx`                                      | **REVIEW NEEDED**                                                                                                                      | **REVIEW**                       | **REVIEW**               | —                 | NEW        |
| 45                         | `preview.tsx`                                   | `/preview`                                                                                                                             | —                                | —                        | —                 | EXIST      |
| **KOMPONENTER (EJ SIDOR)** |
| 46-54                      | `Features/components/` och `Features/sections/` | **KOMPONENTER - EJ SIDOR**                                                                                                             | —                                | —                        | —                 | COMPONENTS |

---

### **Uppdaterad Kontrollsumma**

- **Fungerande sidor**: 25 (Home, Product, Solutions, Company, Legal)
- **Brutna resurssidor**: 13 (Guides, Comparisons, Articles)
- **Nya sidor att granska**: 4 (AiSchedulingCarefox, AiStaffPlanning, Onboarding, OnboardingCaireCarefox, StaticAbout, Auth)
- **Duplicerade sidor att ta bort**: 1 (SchedulingSystemsComparisonPage)
- **Komponenter (ej sidor)**: 9
- **Systemsidor**: 3

**Totalt: 54 filer** – varav 38 faktiska sidor som behöver navigation/översättning

### **Kritiska åtgärder**

1. **OMEDELBART**: Ta bort `SchedulingSystemsComparisonPage.tsx` (duplikat)
2. **PRIORITET 1**: Fixa navigation för 13 brutna resurssidor
3. **PRIORITET 2**: Granska och integrera 4 nya sidor
4. **PRIORITET 3**: Fixa översättningar för alla sidor
5. **PRIORITET 4**: Optimera komponenter och systemsidor
