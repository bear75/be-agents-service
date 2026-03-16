# **Caire.se MVP – Uppgiftsnedbrytning**

**Version:** 3.1  
**Datum:** 2025-01-06  
**Författare:** Björn Evers / VD

---

## **1. Introduktion**

Detta dokument beskriver uppgifter, deluppgifter och tidsplan för implementering av **Caire.se** MVP, med fokus på **AI-driven schemaläggning**, **backend-integrationer**, **landningssidor** och övriga sidor (t.ex. “Tjänster” och “Resurser”) enligt det uppdaterade PRD:t.

---

## **2. Fas 0: Projektuppstart**

| **Uppgifts-ID** | Uppgift             | Beskrivning                                                                                                                             | Ansvarig   | Tidsåtgång |
| --------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ---------- |
| **T0.1**        | PRD Färdigställande | Granska och färdigställ det uppdaterade PRD, inklusive ny sidstruktur (t.ex. Huvudsidor, Funktioner, Tjänster, Resurser, Kontakt, m.m.) | Produkt/PM | **1 dag**  |
| **T0.2**        | Repo-konfiguration  | Skapa GitHub-repo. Konfigurera **Vercel-deployment** och CI/CD-pipelines                                                                | DevOps     | **1 dag**  |
| **T0.3**        | Säkerhetsgrundande  | Konfigurera **HTTPS**, säkerhetshantering och miljövariabler                                                                            | DevOps     | **1 dag**  |

---

## **3. Fas 1: Huvudsidor och Juridiska sidor**

### **3.1 Huvudsidor**

| **Uppgifts-ID** | Uppgift            | Beskrivning                                                                                                                                                           | Ansvarig     | Tidsåtgång  | Status  |
| --------------- | ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | ------- |
| **T1.1**        | **Startsida**      | Implementera Hero-sektion med fokus på "Try Now", **nyckeltal**, **problem**, **fördelar**, **lead magnet (ROI-räknare)**, nyhetsbrev-opt-in och primära CTA-knappar. | Frontend-utv | **4 dagar** | ✅ Klar |
| **T1.2**        | **Om Oss**         | Företagets vision/mission, teampresentation, värderingar, syn på AI inom vården                                                                                       | Frontend-utv | **2 dagar** | ✅ Klar |
| **T1.3**        | **Funktioner**     | Övergripande sida som beskriver kärnfunktioner med demo-videos av testmiljön och success stories                                                                      | Frontend-utv | **3 dagar** | ✅ Klar |
| **T1.4**        | **Resurser**       | Whitepapers, artiklar, guider med fokus på optimal testning och best practices                                                                                        | Frontend-utv | **2 dagar** | ✅ Klar |
| **T1.5**        | **Kontakt**        | Kontaktformulär, kontorsadress, supportkanaler, bokningsalternativ för demo                                                                                           | Frontend-utv | **2 dagar** | ✅ Klar |
| **T1.6**        | **Tjänster (NY!)** | Särskild sida för "Webbutveckling & Underhåll", "Integrationer", "AI Caregiver Pool", "Partners"                                                                      | Frontend-utv | **3 dagar** | ✅ Klar |

### **3.2 SEO & Analytics Implementation**

| **Uppgifts-ID** | Uppgift             | Beskrivning                                                                           | Ansvarig     | Tidsåtgång  | Status  |
| --------------- | ------------------- | ------------------------------------------------------------------------------------- | ------------ | ----------- | ------- |
| **T2.1**        | **Meta Tags & SEO** | Implementera SEO meta tags, strukturerad data, och sociala media kort för alla sidor  | Frontend-utv | **2 dagar** | ✅ Klar |
| **T2.2**        | **Analytics Setup** | Konfigurera Google Analytics 4, implementera event tracking och användarinteraktioner | Frontend-utv | **2 dagar** | ✅ Klar |
| **T2.3**        | **Cookie Consent**  | Implementera GDPR-kompatibelt cookie samtycke system                                  | Frontend-utv | **1 dag**   | ✅ Klar |
| **T2.4**        | **Error Tracking**  | Implementera felspårning och övervakning                                              | Frontend-utv | **1 dag**   | ✅ Klar |
| **T2.5**        | **Performance**     | Optimera prestanda och implementera övervakning                                       | Frontend-utv | **2 dagar** | ✅ Klar |

### **3.2 Juridiska & Inloggningssidor**

| **Uppgifts-ID** | Uppgift               | Beskrivning                                                                          | Ansvarig     | Tidsåtgång  |
| --------------- | --------------------- | ------------------------------------------------------------------------------------ | ------------ | ----------- |
| **T2.1**        | **Inloggning**        | Auth-flöde, registrering, återställning av lösenord, grundläggande användarhantering | Frontend-utv | **3 dagar** |
| **T2.2**        | **Integritetspolicy** | GDPR-efterlevnad, datahantering, användarrättigheter                                 | Juridik      | **1 dag**   |
| **T2.3**        | **Användarvillkor**   | Tjänsteavtal, begränsningar, villkor                                                 | Juridik      | **1 dag**   |
| **T2.4**        | **Förhandsvisning**   | Demomiljö, funktionsvisning, testmöjligheter                                         | Frontend-utv | **2 dagar** |

### **3.7 Try Now Implementation (NY!)**

| **Uppgifts-ID** | Uppgift                  | Beskrivning                                                           | Ansvarig     | Tidsåtgång  | Status   |
| --------------- | ------------------------ | --------------------------------------------------------------------- | ------------ | ----------- | -------- |
| **T10.1**       | Try Now CTA Integration  | Implementera "Try Now" CTA-knappar och länkar på alla relevanta sidor | Frontend-utv | **2 dagar** | 🟡 Pågår |
| **T10.2**       | Demo Video Production    | Skapa och integrera demo-videos som visar testmiljön i användning     | Frontend-utv | **3 dagar** | 🟡 Pågår |
| **T10.3**       | Success Stories          | Samla och implementera testimonials från testanvändare                | Frontend-utv | **2 dagar** | 🟡 Pågår |
| **T10.4**       | Test Environment Guides  | Skapa och integrera guider för optimal användning av testmiljön       | Frontend-utv | **3 dagar** | 🟡 Pågår |
| **T10.5**       | Analytics Implementation | Implementera spårning av Try Now-konverteringar och användarbeteende  | Frontend-utv | **2 dagar** | 🟡 Pågår |

### **3.8 Try Now Analytics & Tracking**

| **Uppgifts-ID** | Uppgift                    | Beskrivning                                                           | Ansvarig     | Tidsåtgång  | Status   |
| --------------- | -------------------------- | --------------------------------------------------------------------- | ------------ | ----------- | -------- |
| **T11.1**       | Conversion Tracking        | Implementera spårning av Try Now-konverteringar och dropoffs          | Frontend-utv | **2 dagar** | 🟡 Pågår |
| **T11.2**       | User Journey Analysis      | Sätt upp spårning av användarresor från marketing site till testmiljö | Frontend-utv | **2 dagar** | 🟡 Pågår |
| **T11.3**       | ROI Calculator Integration | Integrera ROI-beräkning baserad på testdata                           | Frontend-utv | **3 dagar** | 🟡 Pågår |
| **T11.4**       | Automated Follow-up        | Implementera automatiserad uppföljning för testanvändare              | Frontend-utv | **3 dagar** | 🟡 Pågår |

---

## **4. Fas 2: Funktionssidor Implementation**

### **4.1 AI-Schemaläggning**

Speglar PRD-sektionen _3.2 Schemaläggning – AI-optimerad planering_.

| **Uppgifts-ID** | Uppgift               | Beskrivning                                                     | Ansvarig     | Tidsåtgång  |
| --------------- | --------------------- | --------------------------------------------------------------- | ------------ | ----------- |
| **T3.1**        | Kontinuitetshantering | AI-optimering för brukarkontinuitet                             | Backend-utv  | **4 dagar** |
| **T3.2**        | Ruttoptimering        | Optimering av körtider och resvägar                             | Backend-utv  | **3 dagar** |
| **T3.3**        | Preferenshantering    | Hantering av brukar- och personalpreferenser                    | Backend-utv  | **3 dagar** |
| **T3.4**        | Kalendervy            | Dag/vecka/månad-vy, färgkodade pass, statusindikatorer          | Frontend-utv | **4 dagar** |
| **T3.5**        | Akutplanering         | Snabbtilldelning av sista-minuten-bokningar + notiser i realtid | Backend-utv  | **2 dagar** |

### **4.2 Integrationer**

Speglar PRD-sektionen _3.3 Integrationer (Uppdaterad)_.

| **Uppgifts-ID** | Uppgift                 | Beskrivning                            | Ansvarig    | Tidsåtgång  |
| --------------- | ----------------------- | -------------------------------------- | ----------- | ----------- |
| **T4.1**        | Carefox Integration     | API-integration för planering          | Backend-utv | **3 dagar** |
| **T4.2**        | Alfa eCare Integration  | Avvikelsehantering och tidrapportering | Backend-utv | **3 dagar** |
| **T4.3**        | Timefold.ai Integration | AI-schemaläggningsoptimering           | Backend-utv | **4 dagar** |
| **T4.4**        | Kommunala System        | Datasynkronisering med kommunsystem    | Backend-utv | **4 dagar** |

### **4.3 Analysverktyg**

Speglar PRD-sektionen _3.4 Analysverktyg – KPI och Insikter_.

| **Uppgifts-ID** | Uppgift            | Beskrivning                                                                          | Ansvarig     | Tidsåtgång  |
| --------------- | ------------------ | ------------------------------------------------------------------------------------ | ------------ | ----------- |
| **T5.1**        | KPI Dashboard      | Realtids-KPI:er, automatiska varningar, rapporter                                    | Frontend-utv | **4 dagar** |
| **T5.2**        | Avvikelsehantering | Spårning och analys av avvikelser (inkl. integration med Alfa eCare där tillämpligt) | Backend-utv  | **3 dagar** |
| **T5.3**        | Trendanalyser      | Visualisering av trender och prognoser                                               | Frontend-utv | **3 dagar** |

### **4.4 Automatiserad Administration**

Speglar PRD-sektionen _3.5 Automatiserad Administration (Uppdaterad)_.

| **Uppgifts-ID** | Uppgift           | Beskrivning                                                          | Ansvarig    | Tidsåtgång  |
| --------------- | ----------------- | -------------------------------------------------------------------- | ----------- | ----------- |
| **T6.1**        | Dokumenthantering | GDPR-säker dokumentation, mallar för avvikelse- och journalhantering | Backend-utv | **3 dagar** |
| **T6.2**        | Rapportering      | Automatgenererade månadsrapporter, export till PDF/Excel             | Backend-utv | **3 dagar** |
| **T6.3**        | Ekonomihantering  | Fakturering och löneadministration (koppling till bokföringsprogram) | Backend-utv | **4 dagar** |

### **4.5 Onboarding & Integration (NY!)**

Speglar PRD-sektionen _3.6 Onboarding och Integration_.

| **Uppgifts-ID** | Uppgift                   | Beskrivning                                                                            | Ansvarig     | Tidsåtgång  |
| --------------- | ------------------------- | -------------------------------------------------------------------------------------- | ------------ | ----------- |
| **T7.1**        | Implementeringsguide      | Steg-för-steg för att snabbt starta igång nya kunder, inkl. personalutbildning         | Backend-utv  | **2 dagar** |
| **T7.2**        | Onboarding-flöde i system | GUI-lösning som guidar nya kunder genom konfigurering och första schemaläggningsstegen | Frontend-utv | **3 dagar** |

---

## **5. Fas 3: Resurser & SEO**

### **5.1 Innehållsproduktion (Resurser)**

Speglar PRD-sektionen _5. Resurser (NY! Meny)_.

| **Uppgifts-ID** | Uppgift      | Beskrivning                                                    | Ansvarig      | Tidsåtgång  | Status  |
| --------------- | ------------ | -------------------------------------------------------------- | ------------- | ----------- | ------- |
| **T8.1**        | Content Page | Kombinerad sida för artiklar och nyheter med tabbat gränssnitt | Frontend-utv  | **3 dagar** | ✅ Klar |
| **T8.2**        | Whitepapers  | Djupgående analyser med GDPR-säker spårning, lead-generering   | Innehållsteam | **5 dagar** | ✅ Klar |
| **T8.3**        | Nyhetsbrev   | Prenumerationsformulär och hantering av utskick                | Frontend-utv  | **2 dagar** | ✅ Klar |

### **5.2 SEO-optimering**

Speglar PRD-sektionen _7. SEO-Strategi_.

| **Uppgifts-ID** | Uppgift                | Beskrivning                                                                  | Ansvarig      | Tidsåtgång  |
| --------------- | ---------------------- | ---------------------------------------------------------------------------- | ------------- | ----------- |
| **T9.1**        | Meta-taggar & Struktur | SEO-optimering av sidor, semantisk HTML, korrekt språkangivelse              | Frontend-utv  | **2 dagar** |
| **T9.2**        | Prestandaoptimering    | Core Web Vitals, laddningstider, caching-lösningar                           | Frontend-utv  | **3 dagar** |
| **T9.3**        | Innehållsstrategi      | Plan för kontinuerliga bloggposter, kundberättelser, fallstudier (inkl. ROI) | Innehållsteam | **3 dagar** |

---

## **6. Tidsplan (~12 Veckor)**

1. **Vecka 1-2** – Projektuppstart (Fas 0) & Huvudsidor (Fas 1)
2. **Vecka 3-4** – AI-schemaläggning & Integrationer (Fas 2, del 1)
3. **Vecka 5-6** – Analysverktyg & Administration (Fas 2, del 2)
4. **Vecka 7-8** – Onboarding (NY!), Tjänstesida & slutlig funktionstest
5. **Vecka 9-10** – Try Now Implementation & Analytics
6. **Vecka 11-12** – Resurser, SEO (Fas 3) och övergripande optimering

---

## **7. Framgångsmått**

- **90% AI-schemaläggningsnoggrannhet**
- **15% minskad restid**
- **50% automatiserad administration**
- **NPS > 8.0**
- **Try Now Konvertering > 25%**
- **Test till Pilot Konvertering > 40%**

---

### **Slutkommentar**

Denna uppdaterade uppgiftsnedbrytning återspeglar innehållet i det **nya PRD:t**, inklusive nya/uppdaterade sidor (t.ex. **Tjänster**, **Resurser**), mer detaljer kring **AI-schemaläggning** samt fokus på **onboarding** och **SEO**. Tidsplanen är en översikt som kan justeras efter resurstillgång och projektprioriteringar.
