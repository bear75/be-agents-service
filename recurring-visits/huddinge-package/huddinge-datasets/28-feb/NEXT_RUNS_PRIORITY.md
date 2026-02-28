# Nästa körningar – prioritet och konfiguration

Varje körning ska göras **separat** (samma baseline-input 203cf1d6, en ändring per körning) så att vi kan mäta effekt på metrics. Namn på körningen = "namn på ny körning" nedan.

**Baseline:** `28-feb/203cf1d6` (Continuity pool first-run style).  
**Jämförelse:** Efficiency %, travel, wait, break, idle, unassigned, continuity.

---

## Prioritet 1: "break location"

**Namn på ny körning:** `break location`

**Beskrivning:** Sätt break-plats till kontorsadress för alla raster (endast skift som inte är idle – i input kan vi bara sätta alla raster; idle definieras i output).

**Input-ändring:**
- För varje skift: varje `requiredBreaks[]`-objekt ska ha `location: [59.2368721, 17.9942601]` (samma som `startLocation`).
- I 203cf1d6 har alla raster redan denna `location`. Om baseline för körningen är 203cf1d6 behövs ingen input-ändring; använd då detta som “kontroll” eller applicera på en annan baseline som saknar break location.

**Timefold:** Ingen config-override.  
**Referens:** [Lunch breaks and personal appointments](https://docs.timefold.ai/field-service-routing/latest/vehicle-resource-constraints/lunch-breaks-and-personal-appointments) – FLOATING break med `location` ger resa till/från rastplats.

---

## Prioritet 2: "travel extra"

**Namn på ny körning:** `travel extra`

**Beskrivning:** 20 % längre restid (trafik) + 30 s extra per sträcka (parkering).

**Input-ändring:** Ingen. Samma `input.json` som baseline.

**Config-ändring (model overrides):**

```json
{
  "config": {
    "model": {
      "overrides": {
        "travelTimeAdjustment": {
          "multiplier": 1.2,
          "extraTime": "PT30S"
        }
      }
    }
  }
}
```

**Formel:** `adjustedTravelTime = 1.2 * mapTravelTime + PT30S`  
**Referens:** [Configuration overrides – Travel Time Adjustment](https://docs.timefold.ai/field-service-routing/latest/user-guide/configuration-overrides#_travel_time_adjustment).

**Förväntad effekt:** Högre total travel, eventuellt fler otilldelade eller sämre efficiency; bra att mäta i metrics.

---

## Prioritet 3: "office setup time"

**Namn på ny körning:** `office setup time`

**Beskrivning:** 5 min “kontorsuppstart” i början av varje skift (team meeting 07:00–07:05) och 5 min buffert i slutet (redan hanterat via config).

**Input-ändring:**
- För **varje skift**: lägg till en **FIXED** break i början av skiftet:
  - `startTime` = skiftets `minStartTime`
  - `endTime` = minStartTime + 5 minuter (ISO 8601)
  - `location`: `[59.2368721, 17.9942601]` (kontoret)
  - Unikt `id` per skift, t.ex. `{shiftId}_office_setup`
- Exempel för skift som börjar 07:00:
  - `"id": "9ab84ab9_office_setup"`
  - `"type": "FIXED"`
  - `"startTime": "2026-02-16T07:00:00+01:00"`
  - `"endTime": "2026-02-16T07:05:00+01:00"`
  - `"location": [59.2368721, 17.9942601]`
- Befintlig FLOATING lunch-rast (30 min 10:00–14:00) behålls.

**Slut av skift (5 min):** Du nämnde 16:00–16:05; i detta dataset slutar skiften 15:00 (eller 14:30). De 5 minuterna före skiftslut hanteras redan med **model configuration**  
`visitCompletionRiskMinimalTimeToShiftEnd` = **5 minuter** – ingen FIXED break 16:00–16:05 i input.

**Timefold:** Ingen extra config för denna körning (om visitCompletionRiskMinimalTimeToShiftEnd redan är satt i er nuvarande config, behåll den).  
**Referens:** [Team meetings](https://docs.timefold.ai/field-service-routing/latest/vehicle-resource-constraints/lunch-breaks-and-personal-appointments#_team_meetings) (FIXED break med plats och tid).

**Förväntad effekt:** Mindre “ren” besökstid per skift (5 min setup), möjligt något fler otilldelade eller lägre efficiency – mät i metrics.

---

## Sammanfattning – körningsnamn och vad som ändras

| Prio | Namn på ny körning | Input | Config |
|------|--------------------|--------|--------|
| 1 | **break location** | Alla raster: `location` = kontoret (redan så i 203cf1d6) | – |
| 2 | **travel extra** | – | `travelTimeAdjustment`: multiplier 1.2, extraTime PT30S |
| 3 | **office setup time** | +1 FIXED break per skift: 07:00–07:05 (eller minStartTime till +5 min) vid kontoret | visitCompletionRiskMinimalTimeToShiftEnd = 5 min (redan satt) |

---

## Rekommenderad körordning

1. **travel extra** – enkel (endast config), tydlig effekt på travel.
2. **office setup time** – kräver input-patch (nya FIXED breaks).
3. **break location** – om ni använder en baseline utan break location; annars hoppa över eller använd som kontroll.

Efter varje körning: spara plan-id, kör metrics + continuity på samma sätt som för 203cf1d6 och jämför med baseline i DATASET_203cf1d6_ANALYSIS.md.
