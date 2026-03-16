# Produkter

**Meta Title:** Produkter | Caire – AI-plattform för schemaläggning

**Meta Description:** Utforska Caires produkter: en AI-driven plattform med moduler för schemaläggning, ruttoptimering, administration och analys. Vår teknik effektiviserar planeringen i er hemtjänst.

## Caire-plattformen och produktmoduler

### Innehållsstruktur:

- **AI-motorn för schemaläggning**
- **Modul för ruttoptimering**
- **Administrationsverktyg och dokumentation**
- **Analysmodul för data & nyckeltal**
- **Integrationer och säkerhet**

### Target Keywords:

- AI-plattform hemtjänst
- Schemaläggningssystem med AI
- Produktmoduler schemaplanering
- Ruttoptimeringsverktyg
- Integrering hemtjänst system
- Dataskydd molnbaserad hemtjänst

### Image Alt Texts:

- "Skärmbild av Caires plattform som visar användargränssnittet för schemaläggning."
- "Illustration av Caires systemarkitektur med olika produktmoduler som samverkar."

---

Caires produktportfölj kretsar kring vår kraftfulla, molnbaserade plattform. Plattformen består av olika moduler – var och en skräddarsydd för ett viktigt område i planeringen av hemtjänst. Tillsammans bildar de ett sömlöst system. Här presenterar vi våra viktigaste produktkomponenter och hur de samverkar för att effektivisera er verksamhet.

## AI-motorn för schemaläggning

Hjärtat i Caires produkt är AI-schemaläggningsmotorn. Detta är den intelligenta kärnan som automatiskt genererar optimerade scheman. AI-motorn tar in mängder av data: personalens arbetstider och kompetenser, brukarnas beviljade insatser, geografiska avstånd, restriktioner enligt kollektivavtal med mera. Genom att väga in alla dessa faktorer skapar motorn ett schemaförslag som uppfyller behov och regler på bästa sätt.

Tekniskt sett bygger motorn på moderna algoritmer inom maskininlärning och optimering. Den lär sig av historisk data – till exempel vilka schemabyten som brukar behövas – och blir smartare över tid. AI-motorn är också självanpassande: om förutsättningarna ändras (nya brukare tillkommer, personal slutar eller byter availabilitet) justerar systemet förslagen. Resultatet är en dynamisk schemaläggningsmotor som alltid hittar lösningar, även när pusslet är komplext.

## Modul för ruttoptimering

Caires ruttoptimeringsmodul är en fristående produktkomponent som fokuserar på geografisk effektivitet. Den integreras med schemamotorn men kan även användas separat för planering av körvägar. Modulen använder geodata och trafikinfo för att beräkna de snabbaste och mest logiska rutterna för varje medarbetares besök.

Rent praktiskt fungerar det så att när schemat lagts, räknar ruttmodulen ut en optimal sekvens för besöken och föreslår navigering. Om schemat ändras under dagens lopp (t.ex. ett akutbesök skjuts in) kan modulen direkt räkna om rutten. Denna produkt sparar restid och bränsle, och ser till att personalen slipper stressa mellan besöken. För verksamheten innebär det lägre resekostnader och mer tid till omsorg.

## Administrationsverktyg och dokumentation

En annan central produkt är Caires administrationsverktyg, som utgör plattformens användargränssnitt för planering och uppföljning. Det är här som samordnare och chefer kan interagera med systemet. Verktyget har ett intuitivt webbgränssnitt där man kan:

- Överblicka dagens schema och kommande veckor via en visuell planeringskalender.
- Göra manuella justeringar vid behov – t.ex. flytta en insats från en personal till en annan via drag-and-drop.
- Hantera dokumentation: läsa och signera rapporter från personalens utförda besök, kontrollera att alla insatser loggats korrekt.

All data i administrationsverktyget uppdateras i realtid i takt med att personalen rapporterar in via mobilappen. Dessutom finns funktioner för notifieringar – om en insats riskerar att utebli (t.ex. personal inte checkat in hos brukare inom viss tid) kan systemet varna samordnaren så att åtgärd kan tas omedelbart. Administrationsverktyget är, kort sagt, kontrollcentralen för er hemtjänstplanering.

## Analysmodul för data & nyckeltal

Caire inkluderar en analysmodul som produkt, vilken ger er förmågan att omvandla rådata till användbara insikter. Denna modul samlar in data från schemamotorn, ruttoptimeringen och administrationsverktyget och presenterar det i form av interaktiva dashboards och rapporter.

Ni kan enkelt se nyckeltal som:

- Genomsnittlig tid som varje brukare får per vecka.
- Utnyttjandegrad per medarbetare (hur stor andel av arbetstiden som är utförd tid vs restid).
- Antal schemaändringar per månad (en indikator på stabilitet i planeringen).

Analysmodulen låter er filtrera och dyka ner i datan – till exempel kan ni jämföra olika geografiska områden eller tidsperioder. Alla rapporter kan exporteras för att delas med ledning eller myndigheter vid behov. Med denna produktmodul får ni stenkoll på verksamhetens effektivitet och kvalitet, och kan sätta in förbättringsåtgärder baserat på fakta.

## Integrationer och säkerhet

För att Caire ska passa in i just er IT-miljö erbjuder vi omfattande integrationer som en del av plattformen. Våra produkter kan kopplas samman med era befintliga verksamhetssystem: från personalsystem och lönesystem till existerande journalföringssystem. Vi använder moderna API:er för att se till att information flödar sömlöst mellan Caire och andra verktyg ni använder. Det innebär exempelvis att personalens frånvaro som registreras i HR-systemet automatiskt uppdaterar schemaläggningen i Caire, eller att utförda insatser kan skickas tillbaka till journalsystemet utan dubbelregistrering.

Parallellt har vi högsta fokus på datasäkerhet i alla delar av plattformen. Caire är en molnbaserad lösning som driftas i en säker miljö inom EU. All kommunikation är krypterad, och vi följer branschstandarder för skydd av känslig persondata (t.ex. i enlighet med GDPR). Åtkomst till olika moduler styrs med rollbaserade behörigheter, så att personal bara ser den information de behöver. Ni kan tryggt använda Caires produkter i vetskap om att säkerheten och integriteten för era uppgifter är prioriterad.

## CAIRE Plattformsöversikt – Arkitektur & Dataflöde

```mermaid
graph TB
    %% MAIN COMPONENTS
    subgraph Core["CAIRE Kärnplattform"]
        AI["AI-optimeringsmotor"] --- API["API Gateway"]
        API --- DB["Säker Databas"]
        API --- Auth["Autentisering & \nAutorisation"]
        DB --- Rules["Regelmotor"]
        DB --- Analytics["Analysmodul"]
    end

    %% MODULES
    subgraph Modules["Produktmoduler"]
        SchemaModule["Schemaläggnings-\nmodul"]
        RouteModule["Ruttoptimerings-\nmodul"]
        StaffModule["Personalplanerings-\nmodul"]
        ReportModule["Rapport- &\nanalysmodul"]
    end

    %% INTEGRATIONS
    subgraph Integrations["Integrationer"]
        Carefox["Carefox / eCare\nIntegration"]
        HR["HR-system\nIntegration"]
        ERP["Ekonomisystem\nIntegration"]
        Maps["Kartdata\nIntegration"]
        Other["Anpassade\nIntegrationer"]
    end

    %% INTERFACES
    subgraph Interfaces["Gränssnitt"]
        WebApp["Webbapplikation\nför administratörer"]
        MobileApp["Mobilapp för\nfältpersonal"]
        Dashboard["Ledningsrapporter\n& dashboards"]
        Export["Export & \nDatautbyte"]
    end

    %% DATA FLOW
    Carefox -->|"Brukare, besök,\ngrundschema"| API
    HR -->|"Personal, arbetstider,\nkompetenser"| API
    ERP -->|"Kostnadsdata,\nbudgetramar"| API
    Maps -->|"Geografiska data,\nrestider"| API

    API --> SchemaModule
    API --> RouteModule
    API --> StaffModule
    API --> ReportModule

    SchemaModule --> AI
    RouteModule --> AI
    StaffModule --> AI

    AI -->|"Optimerade\nscheman"| WebApp
    AI -->|"Optimerade\nrutter"| MobileApp
    Analytics -->|"KPI,\nrapporter"| Dashboard
    WebApp -->|"Export\nav data"| Export

    %% SECURITY LAYER
    subgraph Security["Säkerhet & Efterlevnad"]
        GDPR["GDPR\nCompliance"]
        Encrypt["Krypterad\nkommunikation"]
        Backup["Automatisk\nbackup"]
        Access["Rollbaserad\nåtkomst"]
    end

    %% CONNECT SECURITY
    Security -.->|"Skyddar"| Core
    Security -.->|"Skyddar"| Interfaces

    %% USER TYPES
    subgraph Users["Användare"]
        Planner["Planerare &\nSamordnare"]
        Manager["Verksamhetschef"]
        Staff["Hemtjänst-\npersonal"]
        Client["Brukare"]
    end

    %% USER CONNECTIONS
    Planner -->|"Använder"| WebApp
    Manager -->|"Följer upp med"| Dashboard
    Staff -->|"Använder"| MobileApp
    MobileApp -->|"Besöksinfo till"| Client

    %% SCALING AND CUSTOMIZATION
    subgraph Customization["Anpassning & Skalning"]
        Templates["Optimerings-\nmallar"]
        Config["Konfigurations-\nalternativ"]
        ML["Maskininlärnings-\nförbättringar"]
    end

    %% CUSTOMIZATION CONNECTIONS
    Planner -->|"Väljer"| Templates
    Manager -->|"Ställer in"| Config
    Analytics -->|"Förbättrar"| ML
    ML -->|"Finjusterar"| AI

    %% STYLING
    classDef core fill:#ddffdd,stroke:#333,stroke-width:2px;
    classDef module fill:#ddddff,stroke:#333,stroke-width:2px;
    classDef integration fill:#ffdddd,stroke:#333,stroke-width:2px;
    classDef interface fill:#ffffdd,stroke:#333,stroke-width:2px;
    classDef security fill:#ffddff,stroke:#333,stroke-width:2px;
    classDef user fill:#ddffff,stroke:#333,stroke-width:2px;
    classDef custom fill:#fff8dc,stroke:#333,stroke-width:2px;

    class AI,API,DB,Auth,Rules,Analytics core;
    class SchemaModule,RouteModule,StaffModule,ReportModule module;
    class Carefox,HR,ERP,Maps,Other integration;
    class WebApp,MobileApp,Dashboard,Export interface;
    class GDPR,Encrypt,Backup,Access security;
    class Planner,Manager,Staff,Client user;
    class Templates,Config,ML custom;
```

Caires produkter utgör tillsammans en komplett plattform för modern hemtjänstplanering. Varje modul är kraftfull var för sig, men det är när de används ihop som den verkliga magin sker. AI-motorn skapar scheman, ruttmodulen finjusterar logistiken, administrationsverktyget ger kontroll och analysmodulen ger insikt. Allt detta integrerat och säkert. Genom att använda Caires produktplattform tar ni ett helhetsgrepp om er verksamhet – med teknik som främjar effektivitet, kvalitet och arbetsglädje.

## Teknisk Arkitektur – Dataflöde

```mermaid
flowchart TD
    %% DATA SOURCES
    subgraph Sources["Datakällor"]
        S1["Befintliga system\n(Carefox/eCare)"]
        S2["Personaldata"]
        S3["Brukardata"]
        S4["Geografiska data"]
    end

    %% DATA INGESTION
    subgraph Ingestion["Datainsamling"]
        I1["API Integrationer"]
        I2["Filimport\n(CSV, Excel)"]
        I3["Manuell inmatning"]
        I4["Sensorer & IoT"]
    end

    %% DATA PROCESSING
    subgraph Processing["Databearbetning"]
        P1["ETL & Transformationer"]
        P2["Datarengöring"]
        P3["Regelvalidering"]
        P4["Aggregering"]
    end

    %% DATA STORAGE
    subgraph Storage["Datalagring"]
        ST1["Primär databas"]
        ST2["Datalager"]
        ST3["Temporära cacher"]
        ST4["Säkerhetskopiering"]
    end

    %% AI LAYER
    subgraph AI["AI & Algoritmer"]
        AI1["Optimeringsalgoritmer"]
        AI2["Maskininlärning"]
        AI3["Prediktiva modeller"]
        AI4["Beslutsstödslogik"]
    end

    %% OUTPUT
    subgraph Output["Produktion"]
        O1["Optimerade scheman"]
        O2["Ruttplaner"]
        O3["Analyser & KPI"]
        O4["Rapporter"]
    end

    %% DATA FEEDBACK
    subgraph Feedback["Feedback Loop"]
        F1["Utförda besök"]
        F2["Personalrapporter"]
        F3["Avvikelsedata"]
        F4["Tjänstkvalitet"]
    end

    %% CONNECTIONS
    Sources --> Ingestion
    Ingestion --> Processing
    Processing --> Storage
    Storage --> AI
    AI --> Output
    Output --> Feedback
    Feedback -->|"AI-lärande"| Processing

    %% IMPLEMENTATION STAGES
    subgraph Stages["Implementeringsfaser"]
        ST1["Dataimport &\nGrunduppbyggnad"]
        ST2["Optimering &\nScenarioplanering"]
        ST3["Förfinad optimering\nmed historiska data"]
        ST4["Prediktiv planering"]
    end

    %% STYLING
    classDef sourceStyle fill:#ffdddd,stroke:#333;
    classDef ingestStyle fill:#ddffdd,stroke:#333;
    classDef processStyle fill:#ddddff,stroke:#333;
    classDef storeStyle fill:#ffffdd,stroke:#333;
    classDef aiStyle fill:#ffddff,stroke:#333;
    classDef outputStyle fill:#ddffff,stroke:#333;
    classDef feedbackStyle fill:#fff8dc,stroke:#333;
    classDef stageStyle fill:#f0e68c,stroke:#333;

    class S1,S2,S3,S4 sourceStyle;
    class I1,I2,I3,I4 ingestStyle;
    class P1,P2,P3,P4 processStyle;
    class ST1,ST2,ST3,ST4 storeStyle;
    class AI1,AI2,AI3,AI4 aiStyle;
    class O1,O2,O3,O4 outputStyle;
    class F1,F2,F3,F4 feedbackStyle;
    class ST1,ST2,ST3,ST4 stageStyle;
```
