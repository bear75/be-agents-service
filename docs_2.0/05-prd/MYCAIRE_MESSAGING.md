# myCaire – Copy och 1-liners för visuals

Sammanställning för data, produkter och personas. Tonalitet: professionell, konkret, värdedriven (caire.se/eirtech).

---

## Data

- **CAIRE Platform**: Planering → utförande/actuals → avvikelser → kvalitetsindikatorer
- **Officiell statistik/ekonomi**: SCB, ekonomiska nyckeltal, regelverk → jämförelser och benchmarks
- **CaireIndex**: Sammanställning av kvalitet, rankning och insikter per organisation/kommun

---

## Produkter (value + flywheel-bidrag)

| Produkt              | 1-liner                                                                                                                                                                                                                                                                                               | Matar flywheel                   |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| **Schemaläggning**   | AI-driven planering som optimerar rutter och minskar administration                                                                                                                                                                                                                                   | Driver realtidsdata och actuals  |
| **Kunskapsportaler** | Portaler med information, guider och Sveriges Hemtjänst med all data och statistik. CaireIndex för jämförelser och rankning. MittCaire för org-claim. [Sveriges Hemtjänst](https://sverigeshemtjanst.se/), [HemtjänstGuide](https://hemtjanstguide.se/). Drivs av [EirTech](https://www.eirtech.ai/). | Acquisition, org-claim, insikter |
| **Personalhandbok**  | Digital personalhandbok med policy, rutiner och rollbaserad åtkomst                                                                                                                                                                                                                                   | Compliance, utbildning, ack      |
| **Caregiver-app**    | EVV, schema, uppgifter och noter för vårdgivare                                                                                                                                                                                                                                                       | Actuals, kvalitet, kontinuitet   |
| **Brukarapp**        | Schema, spårning och kommunikation för brukare och anhöriga                                                                                                                                                                                                                                           | Transparens, trygghet, nöjdhet   |

---

## Personas (top outcomes + primär use case)

- **Kommun**: Bättre styrning och kvalitetsjämförelser. _Use case: Följa upp utförare och kommunala indikatorer._
- **Hemtjänstutförare (bolag)**: Effektivare verksamhet och tydlig positionering. _Use case: Claima org, visa CaireIndex, optimera schemaläggning._
- **Ledning**: Datadrivna beslut och kontinuitet. _Use case: Översikt över actuals, avvikelser och kvalitet._
- **Samordnare**: Mindre manuellt arbete, bättre scheman. _Use case: AI-optimering, ruttplanering, omplanering._
- **Vårdgivare/anställd**: Tydligt schema, enkel check-in/out, fokus på vården. _Use case: Se dagens besök, EVV, notera avvikelser._
- **Brukare/anhörig**: Trygghet och insyn i vården. _Use case: Se schema, spåra ankomst, kommunicera._
- **Medborgare/skattebetalare**: Transparens i välfärden. _Use case: Jämföra kommuner och utförare via kunskapsportaler (Sveriges Hemtjänst, HemtjänstGuide)._

---

## myCaire-kärnan (moduler)

- **Identity + OrgClaim**: Organisationer kan claima sig via MittCaire (Sveriges Hemtjänst)
- **UnifiedActualsLayer**: Realtidsutfall (check-in/out, avvikelser, kontinuitet)
- **Entitlements/Modules**: Aktiva produkter och funktioner per org/roll
- **GamificationEngine**: Mål, nudges, badges per persona
- **InsightsLayer**: CaireIndex, jämförelser, rekommendationer
