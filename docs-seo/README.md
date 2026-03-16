# Dokumentation - Caire SEO Sites

Denna mapp innehåller all dokumentation för Caire SEO Sites-projektet. Dokumenten är organiserade i kategorier för enkel navigering.

## 📁 Dokumentstruktur

Dokumenten är organiserade i 5 kategorier med numrerade undermappar för enkel navigering:

### 🏗️ 01. Arkitektur & Strategi

- **[dev-context.md](./01-arkitektur-strategi/dev-context.md)** - Utvecklingskontext och arkitekturöversikt
- **[STRATEGY_ECOSYSTEM_2025.md](./01-arkitektur-strategi/STRATEGY_ECOSYSTEM_2025.md)** - Övergripande strategi för ekosystemet 2025
- **[APP_DOMAIN_MAPPING.md](./01-arkitektur-strategi/APP_DOMAIN_MAPPING.md)** - Mappning mellan React-appar och domäner
- **[CONSOLIDATION_VERIFICATION.md](./01-arkitektur-strategi/CONSOLIDATION_VERIFICATION.md)** - Verifiering av konsolidering till SverigesHemtjanst.se

### 🔍 02. SEO & Teknisk Implementation

- **[SEO_AUDIT_REPORT.md](./02-seo-teknisk-implementation/SEO_AUDIT_REPORT.md)** - Komplett SEO-audit och implementation status
- **[SEO_BEST_PRACTICES_IMPLEMENTATION.md](./02-seo-teknisk-implementation/SEO_BEST_PRACTICES_IMPLEMENTATION.md)** - SEO best practices och implementation
- **[SEO_META_TAGS_STRUCTURE.md](./02-seo-teknisk-implementation/SEO_META_TAGS_STRUCTURE.md)** - Struktur för SEO meta tags
- **[STRUCTURED_DATA_GUIDE.md](./02-seo-teknisk-implementation/STRUCTURED_DATA_GUIDE.md)** - Guide för structured data (JSON-LD)
- **[GRAPHQL_SETUP_GUIDE.md](./02-seo-teknisk-implementation/GRAPHQL_SETUP_GUIDE.md)** - Guide för GraphQL-implementation för SEO-sites

### 🎨 03. Brand & Design

- **[Brand-Identity-Guidelines–EirTech-SEO-Brands.md](./03-brand-design/Brand-Identity-Guidelines–EirTech-SEO-Brands.md)** - Brand identity guidelines för alla SEO-varumärken
- **[FAVICON_GUIDE.md](./03-brand-design/FAVICON_GUIDE.md)** - Guide för favicon design och setup

### 📊 04. Data & Integration

- **[HEMTJANST_DATA_MODEL.md](./04-data-integration/HEMTJANST_DATA_MODEL.md)** - 📌 **Huvuddokument** - Komplett datamodell för hemtjänstdata i Sverige
- **[DATABASE_SETUP.md](./04-data-integration/DATABASE_SETUP.md)** - Guide för databas-setup (AWS RDS eller lokal Docker)
- **[PROVIDER_DATA_ARCHITECTURE.md](./04-data-integration/PROVIDER_DATA_ARCHITECTURE.md)** - API-integrationer och teknisk arkitektur
- **[DATA_COLLECTION_STRATEGY.md](./04-data-integration/DATA_COLLECTION_STRATEGY.md)** - Strategi för datainsamling
- **[BADGE_CERTIFICATION_STRATEGY.md](./04-data-integration/BADGE_CERTIFICATION_STRATEGY.md)** - Strategi för badge och certifiering

### 🚀 05. Migration & Operations

- **[MIGRATION_HISTORY.md](./05-migration-operations/MIGRATION_HISTORY.md)** - Historik över migration från standalone repo till monorepo
- **[NACKAHEMTJANST_MIGRATION_GUIDE.md](./05-migration-operations/NACKAHEMTJANST_MIGRATION_GUIDE.md)** - Komplett migration guide för nackahemtjanst.se
- **[CONSUMER_SEO_STRATEGY.md](./05-migration-operations/CONSUMER_SEO_STRATEGY.md)** - SEO-strategi för konsumentfokuserade sites
- **[VERCEL_DEPLOYMENT_GUIDE.md](./05-migration-operations/VERCEL_DEPLOYMENT_GUIDE.md)** - Deployment guide för Vercel

## 🎯 Snabbguide

### För utvecklare

1. Börja med **[dev-context.md](./01-arkitektur-strategi/dev-context.md)** för arkitekturöversikt
2. Läs **[APP_DOMAIN_MAPPING.md](./01-arkitektur-strategi/APP_DOMAIN_MAPPING.md)** för routing-struktur
3. Se **[SEO_META_TAGS_STRUCTURE.md](./02-seo-teknisk-implementation/SEO_META_TAGS_STRUCTURE.md)** för SEO-implementation
4. För GraphQL-setup, se **[GRAPHQL_SETUP_GUIDE.md](./02-seo-teknisk-implementation/GRAPHQL_SETUP_GUIDE.md)**

### För SEO/Content

1. Läs **[SEO_AUDIT_REPORT.md](./02-seo-teknisk-implementation/SEO_AUDIT_REPORT.md)** för nuvarande status
2. Följ **[SEO_BEST_PRACTICES_IMPLEMENTATION.md](./02-seo-teknisk-implementation/SEO_BEST_PRACTICES_IMPLEMENTATION.md)** för best practices
3. Använd **[STRUCTURED_DATA_GUIDE.md](./02-seo-teknisk-implementation/STRUCTURED_DATA_GUIDE.md)** för structured data

### För design

1. Följ **[Brand-Identity-Guidelines–EirTech-SEO-Brands.md](./03-brand-design/Brand-Identity-Guidelines–EirTech-SEO-Brands.md)** för brand guidelines
2. Se **[FAVICON_GUIDE.md](./03-brand-design/FAVICON_GUIDE.md)** för favicon-implementation

### För strategi

1. Läs **[STRATEGY_ECOSYSTEM_2025.md](./01-arkitektur-strategi/STRATEGY_ECOSYSTEM_2025.md)** för övergripande strategi
2. Se **[CONSUMER_SEO_STRATEGY.md](./05-migration-operations/CONSUMER_SEO_STRATEGY.md)** för B2C-strategi
3. Läs **[BADGE_CERTIFICATION_STRATEGY.md](./04-data-integration/BADGE_CERTIFICATION_STRATEGY.md)** för badge-systemet

## 📝 Dokumentationsstandarder

### Naming Convention

- Använd `UPPERCASE_WITH_UNDERSCORES.md` för strategi- och arkitekturdokument
- Använd `PascalCase.md` för specifika guides och implementation-dokument
- Använd `kebab-case.md` för tekniska guider

### Dokumentstruktur

Varje dokument bör innehålla:

1. **Översikt** - Kort sammanfattning
2. **Huvudinnehåll** - Detaljerad information
3. **Nästa steg** - Action items eller rekommendationer
4. **Referenser** - Länkar till relaterade dokument

### Uppdateringspolicy

- Uppdatera dokument när implementation ändras
- Markera datum för senaste uppdatering
- Behåll historik för viktiga beslut

## 🔄 Konsoliderade dokument

Följande dokument har konsoliderats:

- ✅ `FAVICON_DESIGN.md` + `FAVICON_SETUP.md` → `FAVICON_GUIDE.md`
- ✅ `NACKAHEMTJANST_CONTENT_MAPPING.md` → Integrerat i `NACKAHEMTJANST_MIGRATION_GUIDE.md`
- ✅ `SEO_IMPLEMENTATION_STATUS.md` → Integrerat i `SEO_AUDIT_REPORT.md`
- ✅ `SEO_SITES_MIGRATION_PLAN.md` → Konsoliderat till `05-migration-operations/MIGRATION_HISTORY.md`
- ✅ GraphQL setup-dokument → Flyttat till `02-seo-teknisk-implementation/GRAPHQL_SETUP_GUIDE.md`

## 🗑️ Borttagna dokument

Följande dokument har tagits bort som irrelevanta, duplicerade eller temporära:

### Tidigare borttagna

- ❌ `domaner.md` - Information finns i `APP_DOMAIN_MAPPING.md`
- ❌ `seo-structure.md` - Information finns i `SEO_AUDIT_REPORT.md` och strategi-dokument
- ❌ `seo-details-hemtjanstistockholm.md` - Information finns i strategi-dokument
- ❌ `SEO-hemtjanstistockholm.md` - Information finns i strategi-dokument
- ❌ `SEO-hemtjanstnacka.md` - Information finns i strategi-dokument
- ❌ `SEO-stockholmhemtjanst.md` - Information finns i strategi-dokument

### Temporära setup/status-dokument (2025-12)

- ❌ `DATABASE_READY.md`, `DATABASE_SETUP_SUCCESS.md`, `SETUP_COMPLETE.md` - Temporära status-dokument
- ❌ `QUICK_DATABASE_SETUP.md`, `DATABASE_URL_AND_SEEDING.md` - Information finns i `04-data-integration/DATABASE_SETUP.md`
- ❌ `GRAPHQL_DB_SETUP_COMPLETE.md`, `MIGRATION_TO_GRAPHQL_COMPLETE.md` - Temporära status-dokument
- ❌ `START_HERE_DB_GRAPHQL.md`, `TESTING_GRAPHQL_SETUP.md` - Information finns i `02-seo-teknisk-implementation/GRAPHQL_SETUP_GUIDE.md`
- ❌ `SEO_MIGRATION_COMPLETE.md`, `SEO_MIGRATION_STATUS.md`, `SEO_APPS_MIGRATION_SUMMARY.md` - Information finns i `05-migration-operations/MIGRATION_HISTORY.md`
- ❌ `SEO_SITES_MIGRATION_PLAN.md` - Konsoliderat till `05-migration-operations/MIGRATION_HISTORY.md`

## 📋 Utvecklingsplaner

Aktiva utvecklingsplaner finns i `.cursor/plans/`:

### Design & UX

- **[Apple Glassmorphism Redesign](../.cursor/plans/apple_glassmorphism_redesign_1aefa6e5.plan.md)** - Implementering av "liquid glass" Apple-inspirerat designsystem med Tailwind + shadcn/ui

### Content & SEO

- **[SEO Content Expansion](../.cursor/plans/seo_content_expansion_8cd8c863.plan.md)** - Utbyggnad av innehåll för alla 5 SEO-sites (Stockholm ✅, Nacka ✅, Innovation ✅, Hemtjänstguiden ✅, Nackahemtjanst ⏳)
- **[Brukarperspektiv Om Oss](../.cursor/plans/brukarperspektiv_om_oss_d76573e6.plan.md)** - Omstrukturering av Om oss-sidan med fokus på brukarens perspektiv

### Arkitektur & Konsolidering

- **[SEO Sites Consolidation](../.cursor/plans/seo_sites_consolidation_8ed6eac0.plan.md)** - Konsolidering från 5 sites till 3 (SverigesHemtjanst.se, Hemtjanstguide.se, Nackahemtjanst.se) ✅
- **[Konsolidera sidor till SverigesHemtjanst](../.cursor/plans/konsolidera_sidor_till_sverigeshemtjanst_315ab937.plan.md)** - Flytt av alla sidor till sverigeshemtjanst/pages/ med undermappsstruktur ✅

### Data & Integration

- **[Provider Database with APIs](../.cursor/plans/provider_database_with_apis_c959c619.plan.md)** - Utförardatabas med kommun.jensnylander.com API, tic.io och kvalitetsdata ✅

## 🏗️ Projektstruktur

### Domänarkitektur

```
B2B Sites (Beslutsfattare):
├── sverigeshemtjanst.se (Master B2B hub)
│   ├── /regioner/stockholm/* (17 sidor)
│   ├── /regioner/nacka/* (7 sidor)
│   └── /innovation/* (6 sidor)
│
B2C Sites (Konsumenter):
├── hemtjanstguide.se (Nationell guide - 22 sidor)
└── nackahemtjanst.se (Lokal Nacka-guide - 6 sidor)
```

### App-struktur

```
src/apps/
├── sverigeshemtjanst/     # B2B authority hub
│   └── pages/
│       ├── Home.tsx
│       ├── OmOss.tsx
│       ├── regioner/
│       │   ├── stockholm/  # 17 sidor
│       │   └── nacka/     # 7 sidor
│       └── innovation/    # 6 sidor
├── hemtjanstguiden/        # B2C nationell guide (22 sidor)
└── nackahemtjanst/         # B2C lokal guide (6 sidor)
```

### Design System

- **Glassmorphism**: Frosted glass panels med `backdrop-blur`
- **Typography**: Geist/Inter med förfinade vikter
- **Colors**: Neutral base (slate/zinc), vibrant blue accent
- **Components**: shadcn/ui primitives + custom glass components

Se [Apple Glassmorphism Redesign plan](../.cursor/plans/apple_glassmorphism_redesign_1aefa6e5.plan.md) för detaljer.

## 📚 Ytterligare resurser

### Externa länkar

- [Vite Documentation](https://vitejs.dev/)
- [React Router Documentation](https://reactrouter.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Schema.org Documentation](https://schema.org/)
- [shadcn/ui Documentation](https://ui.shadcn.com/)

### Internt

- [Brand Identity Guidelines](./03-brand-design/Brand-Identity-Guidelines–EirTech-SEO-Brands.md) - Design guidelines för alla varumärken
- [Provider Data Architecture](./04-data-integration/PROVIDER_DATA_ARCHITECTURE.md) - Datamodell och API-integrationer
- [SEO Best Practices](./02-seo-teknisk-implementation/SEO_BEST_PRACTICES_IMPLEMENTATION.md) - SEO implementation guide

## 🤝 Bidrag

När du skapar eller uppdaterar dokumentation:

1. Följ dokumentationsstandarderna ovan
2. Uppdatera denna README om du lägger till nya dokument
3. Konsolidera relaterad information i befintliga dokument när möjligt
4. Ta bort gamla eller irrelevanta dokument
5. Uppdatera relevanta planer i `.cursor/plans/` när implementation ändras

## 📊 Projektstatus

### ✅ Genomförda faser

- **Phase 1**: Stockholm B2B site (17 sidor) - ✅ Complete
- **Phase 2**: Nacka B2B site (7 sidor) - ✅ Complete
- **Phase 3**: Innovation B2B site (6 sidor) - ✅ Complete
- **Phase 4**: Hemtjanstguiden B2C site (22 sidor) - ✅ Complete
- **SEO Sites Consolidation**: Konsolidering till 3 sites - ✅ Complete
- **Provider Database**: API-integration och databas - ✅ Complete

### ⏳ Pågående

- **Phase 5**: Nackahemtjanst B2C site (6 sidor) - Content enhancement
- **Glassmorphism Design**: Rollout till alla sidor

### 📅 Planerat

- Mono-repo migration till `beta-appcaire`
- Ytterligare content expansion
- Performance optimization

---

---

**Senaste uppdatering:** 2025-12-25  
**Underhålls av:** Caire Development Team  
**Notera:** Denna dokumentation kommer att migreras till `docs/` när SEO-sites är fullt integrerade i huvudrepo.
