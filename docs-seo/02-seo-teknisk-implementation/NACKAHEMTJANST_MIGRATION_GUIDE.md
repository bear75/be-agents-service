# Migration Guide: nackahemtjanst.se

## Från WordPress/MissHosting till Mono-repo/React (COMPLETED ✅)

### Översikt

Denna guide dokumenterar migrationen av nackahemtjanst.se från WordPress på MissHosting till det nya React-baserade mono-repot (`apps/nackahemtjanst`), utan att förlora uppbyggt SEO-värde.

**Status:** ✅ **MIGRATION COMPLETED** (2025-12)  
**App Location:** `apps/nackahemtjanst`  
**Deployment:** Live på nackahemtjanst.se

**Kritiska framgångsfaktorer:**

1. Behåll samma domän (nackahemtjanst.se)
2. Matcha eller 301-redirecta alla befintliga URL:er
3. Behåll eller förbättra sidinnehåll
4. Minimera nedtid

---

## Content Mapping: WordPress → React

### Publicerade sidor i WordPress

| WordPress URL                | Slug                       | Ny React Route                          | Status       | SEO Metadata                                           |
| ---------------------------- | -------------------------- | --------------------------------------- | ------------ | ------------------------------------------------------ |
| `/` (Hem)                    | `home`                     | `/`                                     | ✅ Existerar | Title: "Nacka - Nacka Hemtjänst bedriver hemtjänst..." |
| `/om-nacka-hemtjanst/`       | `om-nacka-hemtjanst`       | `/om-oss` → `/rattigheter`              | ⚠️ Pivot     | Title: "Om oss - Nacka"                                |
| `/kontakta-nacka-hemtjanst/` | `kontakta-nacka-hemtjanst` | `/kontakt`                              | ✅ Existerar | Title: "Kontakta Nacka Hemtjänst"                      |
| `/vanliga-fragor-och-svar/`  | `vanliga-fragor-och-svar`  | `/kontakt#faq` eller `/rattigheter#faq` | ⚠️ Merge     | Title: "Vanliga Frågor och Svar om Hemtjänst"          |
| `/hushallsnara-tjanster/`    | `hushallsnara-tjanster`    | `/hitta-hemtjanst`                      | ⚠️ Redirect  | Title: "Hushållsnära tjänster - Nacka"                 |

### URL-mappning och redirects

#### Direkta mappningar (behåll URL)

- `/` → `/` (startsida)
- `/kontakt/` → `/kontakt` (om WordPress använder kortare slug)

#### Redirects (301)

- `/om-nacka-hemtjanst/` → `/rattigheter` (pivot till konsumentguide)
- `/vanliga-fragor-och-svar/` → `/rattigheter#faq` (merge till rättigheter-sida)
- `/hushallsnara-tjanster/` → `/hitta-hemtjanst` (ny struktur)

### Innehållsanalys

#### 1. Startsida (`/`)

**Nuvarande innehåll:**

- Hero: "Välkommen till nacka hemtjänst"
- Värderingar: Respekt, omtanke, individualitet, fokus på livskvalitet, starkt team
- Tjänster: Städning, tvätt, inköp, matlagning, personlig omvårdnad, promenader, social samvaro, avlösning
- Vision: "Vi vill skapa en högre standard för hemtjänsten"

**Ny positionering (konsumentguide):**

- Pivot från utförar-branding till lokal guide
- Behåll värderingar men omformulera till konsumentperspektiv
- Fokus på att hjälpa brukare hitta och välja anordnare

#### 2. Om Nacka Hemtjänst (`/om-nacka-hemtjanst/`)

**Nuvarande innehåll:**

- Björns historia (grundaren)
- Värderingar: Omtanke, innovation, starkt team
- Vision: "Framtidens hemtjänst med kunden i fokus"
- 5 fokusområden: Innovation, förebyggande, attraktiv arbetsplats, samverkan, data

**Ny positionering:**

- Flytta till `/rattigheter` eller `/om-oss`
- Omformulera från utförar-perspektiv till konsumentguide
- Behåll information om Nackamodellen ur brukarperspektiv

#### 3. Kontakt (`/kontakt/`)

**Nuvarande innehåll:**

- Kontaktformulär
- Kontaktinformation

**Ny positionering:**

- Behåll som `/kontakt`
- Anpassa för konsumentguide (generell kontakt, inte specifik anordnare)

#### 4. Vanliga Frågor (`/vanliga-fragor-och-svar/`)

**Nuvarande innehåll:**

- Omfattande FAQ om hemtjänst i Nacka
- Länkar till Nacka kommuns sidor
- Information om ansökan, avgifter, rättigheter

**Ny positionering:**

- Merge till `/rattigheter` eller `/ansoka`
- Anpassa för konsumentguide (generella frågor, inte specifik anordnare)

#### 5. Hushållsnära tjänster (`/hushallsnara-tjanster/`)

**Nuvarande innehåll:**

- Lista över tjänster

**Ny positionering:**

- Redirect till `/hitta-hemtjanst`
- Innehållet kan användas i ny struktur

### SEO-metadata att behålla

#### Startsida

- **Title:** "Nacka - Nacka Hemtjänst bedriver hemtjänst, boendestöd, ledsagning och hushållsnära tjänster i Nacka kommun. Kontakta oss för rådgivning."
- **Meta desc:** "Vi erbjuder hemtjänst i Nacka kommun. Vi strävar efter att vara en viktig partner för att du ska få ett självständigt och meningsfullt liv."
- **Focus KW:** "Nacka Hemtjänst"
- **Yoast Score:** 83 (cornerstone)

#### Kontakt

- **Title:** "Kontakta Nacka Hemtjänst"
- **Meta desc:** "Kontakta Nacka Hemtjänst. Vi finns här för att hjälpa dig att leva ett aktivt och självständigt liv, oavsett dina behov."
- **Focus KW:** "Kontakta Nacka Hemtjänst"
- **Yoast Score:** 88

#### Vanliga Frågor

- **Title:** "Vanliga Frågor och Svar om Hemtjänst"
- **Meta desc:** "Allt du behöver veta om hemtjänst i Nacka Kommun. Vanliga frågor och svar om hemtjänst. Hur ansöker jag om hemtjänst i Nacka?"
- **Focus KW:** "Vanliga frågor och svar om hemtjänst"
- **Yoast Score:** 71

---

## Fas 1: Audit (FÖRE migration)

### 1.1 Dokumentera nuvarande URL-struktur

Kör dessa kommandon för att få en fullständig bild:

```bash
# Ladda ner sitemap om den finns
curl https://nackahemtjanst.se/sitemap.xml -o sitemap_backup.xml

# Eller använd screaming frog / site:nackahemtjanst.se i Google
```

**Dokumentera alla URL:er:**

| Nuvarande URL          | Sidtyp    | Rankar för        | Ny URL             |
| ---------------------- | --------- | ----------------- | ------------------ |
| /                      | Startsida | "nacka hemtjänst" | /                  |
| /kontakt               | Kontakt   | -                 | /kontakt           |
| /om-oss                | Om oss    | -                 | /om-oss (redirect) |
| /vanliga-fragor        | FAQ       | -                 | /kontakt#faq       |
| /hushallsnara-tjanster | Tjänster  | -                 | /hitta-hemtjanst   |

### 1.2 Exportera content från WordPress

```bash
# Via WP CLI (om tillgängligt)
wp export --path=/path/to/wordpress

# Eller manuellt via WP Admin:
# Verktyg → Exportera → Allt innehåll
```

### 1.3 Dokumentera nuvarande SEO-metadata

För varje viktig sida, spara:

- Title tag
- Meta description
- H1
- Canonical URL
- Backlinks (kolla via Ahrefs/Moz/Google Search Console)

### 1.4 Google Search Console snapshot

1. Gå till Google Search Console
2. Exportera:
   - Alla indexerade sidor
   - Sökord och positioner
   - Backlinks

---

## Fas 2: Förbered nya sidor

### 2.1 URL-mappning

Baserat på audit, uppdatera routing i den nya appen:

```typescript
// src/apps/nackahemtjanst/NackahemtjanstApp.tsx
<Routes>
  {/* Matcha existerande URL:er */}
  <Route index element={<Home />} />
  <Route path="kontakt" element={<Kontakt />} />
  <Route path="om-oss" element={<OmOss />} />

  {/* Nya sidor */}
  <Route path="hitta-hemtjanst" element={<HittaHemtjanst />} />
  <Route path="ansoka" element={<Ansoka />} />
  ...
</Routes>
```

### 2.2 Implementera 301-redirects

Skapa en redirect-konfiguration för URL:er som ändras:

```typescript
// src/config/redirects.ts
export const nackahemtjanstRedirects = [
  { from: "/hushallsnara-tjanster", to: "/hitta-hemtjanst", status: 301 },
  { from: "/vanliga-fragor", to: "/kontakt", status: 301 },
  { from: "/blogg/*", to: "/", status: 301 },
];
```

### 2.3 Behåll SEO-metadata

Säkerställ att SeoHead-komponenten matchar originalets metadata:

```typescript
// Exempel: Om originalet hade:
// <title>Nacka Hemtjänst - Personlig omsorg i ditt hem</title>
// <meta name="description" content="Vi erbjuder hemtjänst...">

<SeoHead
  title="Nacka Hemtjänst - Personlig omsorg i ditt hem"
  description="Vi erbjuder hemtjänst i Nacka kommun med fokus på trygghet och kvalitet."
  canonicalUrl="https://nackahemtjanst.se/"
/>
```

---

## Fas 3: AWS Deployment Setup

### 3.1 Arkitektur för SEO-vänlig deployment

```
nackahemtjanst.se
        │
        ▼
  [CloudFront CDN]
        │
        ├── /robots.txt ──────► S3
        ├── /sitemap.xml ─────► S3
        │
        └── /* ───────────────► S3 (React SPA)
                                  │
                                  └── _redirects / Lambda@Edge
                                      (för 301 redirects)
```

### 3.2 Konfigurera Lambda@Edge för redirects

```javascript
// lambda/redirect-handler.js
exports.handler = async (event) => {
  const request = event.Records[0].cf.request;
  const uri = request.uri;

  const redirects = {
    "/hushallsnara-tjanster": "/hitta-hemtjanst",
    "/vanliga-fragor": "/kontakt",
    "/blogg": "/",
  };

  if (redirects[uri]) {
    return {
      status: "301",
      statusDescription: "Moved Permanently",
      headers: {
        location: [{ value: `https://nackahemtjanst.se${redirects[uri]}` }],
        "cache-control": [{ value: "max-age=31536000" }],
      },
    };
  }

  return request;
};
```

### 3.3 S3 + CloudFront konfiguration

```yaml
# cloudformation/nackahemtjanst.yaml
Resources:
  WebsiteBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: nackahemtjanst-website
      WebsiteConfiguration:
        IndexDocument: index.html
        ErrorDocument: index.html # For SPA routing

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - DomainName: !GetAtt WebsiteBucket.DomainName
            Id: S3Origin
        DefaultCacheBehavior:
          ViewerProtocolPolicy: redirect-to-https
          LambdaFunctionAssociations:
            - EventType: origin-request
              LambdaFunctionARN: !Ref RedirectLambda
        Aliases:
          - nackahemtjanst.se
          - www.nackahemtjanst.se
```

---

## Fas 4: Migration Execution

### 4.1 Checklista före launch

- [ ] Alla viktiga URL:er har motsvarighet eller redirect
- [ ] Title/description matchar eller är förbättrade
- [ ] robots.txt tillåter crawling
- [ ] sitemap.xml genererad och korrekt
- [ ] HTTPS fungerar
- [ ] Canonical URLs satta korrekt
- [ ] Structured data (schema.org) implementerat
- [ ] Sidor laddar snabbt (<3s)
- [ ] Mobilvänligt (testa med Lighthouse)

### 4.2 DNS-ändring (minimal nedtid)

**Steg 1: Förbered (dagen före)**

```bash
# Sänk TTL på DNS till 300 sekunder
# I MissHosting eller domänregistratorn
```

**Steg 2: Verifiera ny site fungerar**

```bash
# Testa via CloudFront-URL:en direkt
curl -I https://d1234567890.cloudfront.net/
```

**Steg 3: Uppdatera DNS**

```
# Peka nackahemtjanst.se till CloudFront
# A-record eller CNAME till CloudFront distribution

nackahemtjanst.se.    300    IN    A      <CloudFront IP>
# ELLER
nackahemtjanst.se.    300    IN    CNAME  d1234567890.cloudfront.net.
```

**Steg 4: Verifiera**

```bash
# Vänta på DNS-propagering (5-15 min med låg TTL)
dig nackahemtjanst.se

# Testa alla viktiga URL:er
curl -I https://nackahemtjanst.se/
curl -I https://nackahemtjanst.se/kontakt
curl -I https://nackahemtjanst.se/hushallsnara-tjanster  # Ska ge 301
```

---

## Fas 5: Post-migration

### 5.1 Google Search Console

1. Lägg till property för nya URL:en (om inte redan gjort)
2. Skicka in ny sitemap: `https://nackahemtjanst.se/sitemap.xml`
3. Begär indexering av viktiga sidor
4. Övervaka "Täckning"-rapporten för fel

### 5.2 Övervakning första veckan

| Dag | Kontrollera                                 |
| --- | ------------------------------------------- |
| 1   | Alla sidor svarar, redirects fungerar       |
| 2   | Google Search Console för crawl-fel         |
| 3   | Sökpositioner (kolla samma sökord som före) |
| 7   | Indexeringsstatus, eventuella problem       |

### 5.3 Vanliga problem och lösningar

| Problem               | Orsak                             | Lösning                                        |
| --------------------- | --------------------------------- | ---------------------------------------------- |
| Sidor ej indexerade   | robots.txt blockerar              | Kontrollera robots.txt, skicka in sitemap igen |
| 404-fel i GSC         | URL-struktur ändrad utan redirect | Lägg till 301-redirect                         |
| Sökpositioner sjunker | Innehåll saknas eller ändrat      | Återställ original-content                     |
| Dubbla indexeringar   | Både www och non-www              | Sätt canonical, 301-redirect                   |

---

## Teknisk checklista

### robots.txt (måste finnas i public/)

```txt
User-agent: *
Allow: /

Sitemap: https://nackahemtjanst.se/sitemap.xml
```

### sitemap.xml (genereras dynamiskt eller statiskt)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://nackahemtjanst.se/</loc>
    <lastmod>2025-12-22</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://nackahemtjanst.se/hitta-hemtjanst</loc>
    <lastmod>2025-12-22</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <!-- Lägg till alla sidor -->
</urlset>
```

---

## Sammanfattning

**Kritiska steg för att behålla SEO-värde:**

1. ✅ **Behåll domänen** - Alla backlinks fortsätter fungera
2. ✅ **Matcha URL:er** - Eller implementera 301-redirects
3. ✅ **Behåll content** - Samma eller bättre innehåll
4. ✅ **Snabb site** - Ny React-site är troligen snabbare
5. ✅ **HTTPS** - CloudFront ger gratis SSL
6. ✅ **Mobile-first** - Ny site är responsiv

**Förväntad SEO-påverkan:**

- Kortsiktigt (1-2 veckor): Möjlig liten fluktuation
- Medellång sikt (1-2 månader): Återhämtning till samma eller bättre positioner
- Långsiktigt: Förbättrad ranking tack vare snabbare, bättre strukturerad site

---

## Migration Status

### ✅ Completed Steps

1. ✅ URL-audit genomförd på WordPress-site
2. ✅ Content exporterad och migrerad
3. ✅ React-sidor implementerade med korrekt content
4. ✅ SEO-metadata behållen och förbättrad
5. ✅ Redirects implementerade (se SEO_CONTENT_AUDIT_NACKAHEMTJANST.md)
6. ✅ DNS-byte genomförd
7. ✅ Site live på nackahemtjanst.se

### 📊 Post-Migration Status

**App:** `apps/nackahemtjanst`  
**Routes:**

- `/` - Startsida
- `/hitta-hemtjanst` - Hitta anordnare
- `/ansoka` - Ansökningsguide
- `/rattigheter` - Rättigheter och FAQ
- `/utforare` - anordnare-lista
- `/kontakt` - Kontakt

**SEO Status:** ✅ Rankings behållna, content förbättrat

### 🔄 Ongoing Monitoring

- [ ] Fortsätt övervaka Google Search Console
- [ ] Track ranking positions för "hemtjänst Nacka"
- [ ] Monitor 404 errors
- [ ] Optimera baserat på analytics
