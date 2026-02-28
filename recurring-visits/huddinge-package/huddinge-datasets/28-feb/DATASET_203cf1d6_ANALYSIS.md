# Dataset 203cf1d6 – Detaljanalys

Baseline för nästa körningar: **Continuity pool (first-run style)** (manifest.json).

---

## 1. Input-struktur

| Fält | Värde |
|------|--------|
| **Kontor/depot** | `[59.2368721, 17.9942601]` (startLocation för alla skift) |
| **Fordon** | 38 (Driver-01 … Driver-38) |
| **Skift** | 340 totalt (10 skift/dag × 34 dagar; vissa fordon har 7,5h-dagar) |
| **Skiftlängd** | 8h: 07:00–15:00 (mån–fre 16–20 feb, 23–27 feb); 7,5h: 07:00–14:30 (21, 22, 28 feb) |
| **Rast** | 1 × FLOATING 30 min per skift; fönster 10:00–14:00 (minStartTime–maxEndTime) |
| **Rast plats** | Redan satt: `location: [59.2368721, 17.9942601]` (kontoret) för alla raster |

---

## 2. Besök och grupper

| Fält | Värde |
|------|--------|
| Care visits | 3478 (3334 solo + 144 dubbelpersonal) |
| Timefold visits | 3622 (3334 solo + 288 i 144 visitGroups) |
| Time window slots | 3622 (flyttbara över veckor) |

---

## 3. Nuvarande metrics (203cf1d6)

| Metric | Värde |
|--------|--------|
| Efficiency (visit / (shift − break)) | 62,39 % |
| Travel | 168h 34min |
| Wait | 53h 4min |
| Break | 93h 30min |
| Idle | 684h 16min |
| Skift med besök / tomma | 300 / 40 |
| Tilldelade / otilldelade besök | 3554 / 68 |
| Score | 0hard/-680000medium/-2011536soft |

---

## 4. Relevanta Timefold-dokument

- **Raster med plats:** [Lunch breaks and personal appointments](https://docs.timefold.ai/field-service-routing/latest/vehicle-resource-constraints/lunch-breaks-and-personal-appointments) (FLOATING med `location`, FIXED team meetings).
- **Resejustering:** [Configuration overrides – Travel Time Adjustment](https://docs.timefold.ai/field-service-routing/latest/user-guide/configuration-overrides#_travel_time_adjustment):  
  `adjustedTravelTime = multiplier * mapTravelTime + extraTime`
- **Risk mot skiftslut:** `visitCompletionRiskMinimalTimeToShiftEnd` (model configuration) – redan satt till 5 minuter för denna körning.
