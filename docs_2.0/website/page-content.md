# Page Content Reference

This document serves as the single source of truth for all page content on caire.se. Any content changes should be made here first, then implemented in the components.

## Content Structure

### Index (Startsida)

```typescript
{
  hero: {
    title: "AI-driven hemtjänstplattform",
    description: "Vi revolutionerar hemtjänsten med en AI-driven plattform som minskar den manuella administrativa bördan och frigör tid för det som verkligen betyder något – omsorgen.",
  },
  stats: [
    {
      value: "90%",
      label: "AI-schemaläggningsnoggrannhet"
    },
    {
      value: "15%",
      label: "minskad restid"
    },
    {
      value: "50%",
      label: "automatiserad administration"
    }
  ],
  features: [
    {
      title: "AI-Schemaläggning",
      description: "Optimera personalplanering och rutter automatiskt"
    },
    {
      title: "Smart Administration",
      description: "Minska administrativ tid med automatisering"
    },
    {
      title: "Integrationer",
      description: "Sömlös koppling till befintliga system"
    }
  ],
  cta: {
    title: "Börja optimera din verksamhet idag",
    description: "Kontakta oss för en demo av hur Caire kan effektivisera er hemtjänst.",
    buttonText: "Boka Demo"
  }
}
```

### Features (Funktioner)

```typescript
{
  hero: {
    title: "Funktioner",
    description: "Upptäck våra kraftfulla funktioner som hjälper dig optimera din hemtjänstverksamhet."
  },
  features: [
    {
      title: "AI-Schemaläggning",
      description: "Intelligent planering med självlärande AI som matchar personal och brukare på ett optimalt sätt.",
      link: "/funktioner/schemaläggning",
      icon: "Calendar"
    },
    {
      title: "Administration",
      description: "Automatisera administrativa uppgifter och minska pappersarbetet.",
      link: "/funktioner/administration",
      icon: "FileText"
    },
    {
      title: "Integrationer",
      description: "Sömlös koppling till kommunala system och andra verktyg.",
      link: "/funktioner/integrationer",
      icon: "Puzzle"
    },
    {
      title: "Analysverktyg",
      description: "Få djupa insikter i verksamheten med realtidsanalyser.",
      link: "/funktioner/analysverktyg",
      icon: "BarChart"
    },
    {
      title: "Onboarding",
      description: "Snabb och smidig implementering för hela organisationen.",
      link: "/funktioner/onboarding",
      icon: "Rocket"
    }
  ]
}
```

### Features/Scheduling (Schemaläggning)

```typescript
{
  hero: {
    title: "AI-Driven Schemaläggning",
    description: "Optimera personalplanering och rutter automatiskt med vår AI-drivna schemaläggning."
  },
  benefits: [
    {
      title: "Intelligent Matchning",
      description: "AI matchar rätt personal med rätt brukare baserat på kompetens, preferenser och tillgänglighet."
    },
    {
      title: "Ruttoptimering",
      description: "Minimera restid och maximera vårdtid med smarta ruttförslag."
    },
    {
      title: "Realtidsanpassning",
      description: "Automatisk omplanering vid sjukdom eller andra oförutsedda händelser."
    }
  ],
  features: [
    {
      title: "Automatisk Schemaläggning",
      items: [
        "AI-baserad personalfördelning",
        "Smart ruttoptimering",
        "Kontinuitetshantering"
      ]
    },
    {
      title: "Personalpreferenser",
      items: [
        "Kompetensbaserad matchning",
        "Hänsyn till önskemål",
        "Rättvis arbetsfördelning"
      ]
    }
  ]
}
```

### Features/Administration

```typescript
{
  hero: {
    title: "Smart Administration",
    description: "Automatisera administrativa uppgifter och frigör tid för vård och omsorg."
  },
  benefits: [
    {
      title: "Automatisk Dokumentation",
      description: "Minska manuell inmatning med smarta mallar och automatisk journalföring."
    },
    {
      title: "Digital Signering",
      description: "Säker digital signering av dokument och insatser."
    },
    {
      title: "Integrerad Rapportering",
      description: "Automatisk generering av rapporter och statistik."
    }
  ],
  features: [
    {
      title: "Dokumenthantering",
      items: [
        "Digital journalföring",
        "Automatiska rapporter",
        "Säker arkivering"
      ]
    },
    {
      title: "Kvalitetssäkring",
      items: [
        "Avvikelsehantering",
        "Uppföljning",
        "Statistik"
      ]
    }
  ]
}
```

### Features/Analytics (Analysverktyg)

```typescript
{
  hero: {
    title: "Kraftfulla Analysverktyg",
    description: "Få djupa insikter i verksamheten med realtidsanalyser och prediktiv analys."
  },
  benefits: [
    {
      title: "Realtidsövervakning",
      description: "Se verksamhetens KPI:er i realtid och agera proaktivt."
    },
    {
      title: "Prediktiv Analys",
      description: "Förutse behov och optimera resurser med AI-driven analys."
    },
    {
      title: "Anpassade Rapporter",
      description: "Skapa skräddarsydda rapporter för olika intressenter."
    }
  ],
  features: [
    {
      title: "Datavisualisering",
      items: [
        "Interaktiva dashboards",
        "Anpassade rapporter",
        "Trendanalyser"
      ]
    },
    {
      title: "Prestationsmätning",
      items: [
        "KPI-uppföljning",
        "Resursoptimering",
        "Kvalitetsmätning"
      ]
    }
  ]
}
```

### Features/Integrations (Integrationer)

```typescript
{
  hero: {
    title: "Sömlösa Integrationer",
    description: "Koppla samman Caire med era befintliga system för effektivt informationsflöde."
  },
  integrations: [
   /*  {
      title: "Timefold.ai",
      description: "AI-driven schemaoptimering",
      logo: "/images/logos/timefold-logo.svg"
    }, */
    {
      title: "Quinyx",
      description: "Personalplanering och schemaläggning",
      logo: "/images/logos/quinyx-logo.svg"
    },
    {
      title: "Alfa eCare",
      description: "Journalsystem och dokumentation",
      logo: "/images/logos/alfaecare-logo.svg"
    },
    {
      title: "TietoEVRY",
      description: "IT-tjänster och systemintegration",
      logo: "/images/logos/tietoevry-logo.svg"
    },
    {
      title: "Carefox",
      description: "Vårdplanering och dokumentation",
      logo: "/images/logos/carefox-logo.svg"
    }
  ],
  features: [
    {
      title: "API-Integration",
      items: [
        "RESTful API",
        "Säker dataöverföring",
        "Realtidssynkronisering"
      ]
    },
    {
      title: "Datakvalitet",
      items: [
        "Validering",
        "Felhantering",
        "Loggning"
      ]
    }
  ]
}
```

### Features/Onboarding (Onboarding)

```typescript
{
  hero: {
    title: "Smidig Onboarding",
    description: "Snabb och effektiv implementering av Caire i er verksamhet."
  },
  benefits: [
    {
      title: "Dedikerad Support",
      description: "Personlig projektledare och support under hela implementeringen."
    },
    {
      title: "Anpassad Plan",
      description: "Skräddarsydd implementeringsplan baserad på era behov."
    },
    {
      title: "Utbildning",
      description: "Omfattande utbildning för all personal."
    }
  ],
  features: [
    {
      title: "Implementering",
      items: [
        "Systemintegration",
        "Datamigrering",
        "Konfiguration"
      ]
    },
    {
      title: "Utbildning",
      items: [
        "Personalutbildning",
        "Administratörsutbildning",
        "Dokumentation"
      ]
    }
  ]
}
```

### Tjänster

```typescript
{
  hero: {
    title: "Tjänster",
    description: "Förutom vår kärnplattform erbjuder vi även ett antal kringliggande tjänster som hjälper kunder att dra maximal nytta av våra lösningar."
  },
  services: [
    {
      title: "Webbutveckling och Underhåll",
      items: [
        "Skapa och underhålla webbplatser",
        "Anpassade design- och UX-lösningar",
        "Löpande teknisk support"
      ]
    },
    {
      title: "Integrationer",
      items: [
        "Anpassade API-lösningar",
        "Rådgivning och arkitektur",
        "Test och kvalitetssäkring"
      ]
    },
    {
      title: "AI Caregiver Pool",
      items: [
        "AI-driven personalpool integrerad i plattformen",
        "Möjlighet till snabb rekrytering vid toppar i efterfrågan"
      ]
    },
    {
      title: "Partners",
      items: [
        "Carefox, Alfa Ecare, Combine Pulse, etc.",
        "Samarbeten för att bredda våra kundlösningar"
      ]
    }
  ]
}
```

### Resurser

```typescript
{
  hero: {
    title: "Resurser",
    description: "Ta del av våra guider, whitepapers och artiklar om AI inom hemtjänsten."
  },
  sections: [
    {
      title: "Whitepapers",
      items: [
        {
          title: "AI i hemtjänsten – Från manuella processer till automatisering",
          description: "Överblick av AI-lösningar inom vård och omsorg"
        },
        {
          title: "Digital transformation i hemtjänsten",
          description: "Guide för implementering av digitala verktyg"
        }
      ]
    },
    {
      title: "Guider",
      items: [
        {
          title: "Kom igång med digital schemaläggning",
          description: "Steg-för-steg guide för effektiv personalplanering"
        },
        {
          title: "Optimera vårdkvalitet med AI",
          description: "Praktiska tips för AI-implementering"
        }
      ]
    }
  ]
}
```

### Contact (Kontakt)

```typescript
{
  hero: {
    title: "Kontakta Oss",
    description: "Vi hjälper dig gärna med frågor om våra tjänster och produkter."
  },
  contactInfo: {
    email: "info@caire.se",
    phone: "+46 123 456 789",
    address: {
      street: "Exempelgatan 123",
      city: "Stockholm",
      zip: "111 22"
    }
  },
  form: {
    title: "Skicka Meddelande",
    fields: [
      {
        label: "Namn",
        type: "text",
        required: true
      },
      {
        label: "E-post",
        type: "email",
        required: true
      },
      {
        label: "Telefon",
        type: "tel",
        required: false
      },
      {
        label: "Meddelande",
        type: "textarea",
        required: true
      }
    ]
  }
}
```

### About (Om Oss)

```typescript
{
  hero: {
    title: "Om Caire",
    description: "Vi digitaliserar och effektiviserar hemtjänsten med hjälp av AI och smart teknologi."
  },
  sections: [
    {
      title: "Vår Vision",
      content: "Att revolutionera hemtjänsten genom att kombinera mänsklig omsorg med intelligent teknologi."
    },
    {
      title: "Vårt Team",
      content: "Ett dedikerat team av experter inom AI, vård och teknologi."
    }
  ],
  values: [
    {
      title: "Innovation",
      description: "Vi driver utvecklingen framåt med ny teknologi"
    },
    {
      title: "Kvalitet",
      description: "Vi sätter kvalitet och säkerhet främst"
    },
    {
      title: "Hållbarhet",
      description: "Vi arbetar för en hållbar framtid inom vården"
    }
  ]
}
```

### FAQ (Vanliga Frågor)

```typescript
{
  hero: {
    title: "Vanliga Frågor",
    description: "Här hittar du svar på de vanligaste frågorna om Caire."
  },
  categories: [
    {
      title: "Allmänna Frågor",
      questions: [
        {
          question: "Vad är Caire?",
          answer: "Caire är en AI-driven plattform för hemtjänsten som optimerar schemaläggning och administration."
        },
        {
          question: "Hur kommer vi igång?",
          answer: "Vi erbjuder en strukturerad onboardingprocess med analys, implementation och utbildning."
        }
      ]
    },
    {
      title: "Tekniska Frågor",
      questions: [
        {
          question: "Vilka system kan ni integrera med?",
          answer: "Vi har färdiga integrationer med de flesta stora system inom vården."
        },
        {
          question: "Hur säker är plattformen?",
          answer: "Vi följer högsta säkerhetsstandarder och är GDPR-kompatibla."
        }
      ]
    }
  ]
}
```

### 404 (Sidan Kunde Inte Hittas)

```typescript
{
  hero: {
    title: "404 - Sidan kunde inte hittas",
    description: "Vi kunde tyvärr inte hitta sidan du söker. Den kan ha flyttats eller tagits bort."
  },
  suggestions: {
    title: "Populära sidor",
    links: [
      {
        text: "Startsida",
        url: "/"
      },
      {
        text: "Funktioner",
        url: "/funktioner"
      },
      {
        text: "Kontakta oss",
        url: "/kontakt"
      }
    ]
  }
}
```

## Usage Guidelines

1. **Content Updates**
   - Make changes to this file first
   - Create a PR with both content and component changes
   - Update tests to reflect new content

2. **Testing**
   - Use this content in unit tests
   - Test that components render the correct content
   - Verify content matches across all environments

3. **Maintenance**
   - Review content quarterly
   - Keep content in sync with PRD
   - Document any temporary content changes

## Content Migration Checklist

When implementing new features or fixing bugs:

- [ ] Check this file for the correct content
- [ ] Update component to match this content
- [ ] Update tests to use this content
- [ ] Verify no content was accidentally removed
- [ ] Document any content changes in PR
