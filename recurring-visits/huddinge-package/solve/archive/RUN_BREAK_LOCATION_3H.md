# Running break-location input with ~3h solve

## 1. Run break-location with 3h

Your break-location input is `solve/input_20260219_breakloc.json`. To get a long run (~3h) like the 073f6280 solve:

**Option A – Set termination in the input (recommended)**  
The Timefold FSR API accepts `config.run.termination`. Add a 3h limit so the run doesn’t rely on UI profile:

```json
"config": {
  "run": {
    "name": "Huddinge 2wk break location",
    "termination": {
      "spentLimit": "PT3H"
    }
  }
}
```

Then submit (script uses your configuration profile by default):

```bash
cd docs_2.0/recurring-visits/huddinge-package/scripts
export TIMEFOLD_API_KEY="your-key"
python3 submit_to_timefold.py solve ../../solve/input_20260219_breakloc.json --wait --save ../../solve/tf-19feb-breakloc/output.json
```

**Configuration profile:** The submit script uses configuration profile **`6a4e6b5f-8767-48f8-9365-7091f7e74a37`** by default (query param `configurationId`). Override with `--configuration-id ID` or `TIMEFOLD_CONFIGURATION_ID`.

**Option B – Use Timefold UI with same profile**  
Submit the same JSON via the Timefold UI and choose the **Huddinge-test-long** profile (5h spentLimit). The solver will run until completion or unimproved termination; the 073f6280 run used this and ran ~2h35m.

---

## 2. Input diff: break-location vs tf-16feb (073f6280 input)

Compared:

- **`solve/input_20260219_breakloc.json`** (break-location)
- **`solve/tf-16feb-0800/export-field-service-routing-v1-073f6280-9da5-44ca-8184-e1e00c97cd33-input.json`** (no break location)

**Same:** vehicles, visits, shift windows, break windows (minStartTime, maxEndTime, duration, costImpact, type FLOATING). Same depot (`startLocation`), same dataset size.

**Only difference:** break **location**.

| File            | requiredBreaks shape |
|-----------------|----------------------|
| break-location   | Each break has `"location": [59.2368721, 17.9942601]` (service area). |
| tf-16feb input  | Breaks have no `location` (FLOATING only: id, minStartTime, maxEndTime, duration, costImpact, type). |

Shift IDs differ (e.g. `005bb8e8` vs `c46a48bc`) because they come from different generation runs; the **only semantic diff** is that break-location pins the break to the given coordinates.

---

## 3. Where is travel to/from office in the output?

**From office (start):**

- **Per shift:** First visit in `itinerary` has `travelTimeFromPreviousStandstill` = travel from shift start (office) to that visit.
- **Per shift summary:** In that shift’s `metrics`: **`travelTimeFromStartLocationToFirstVisit`**.
- **Global:** In top-level **`kpis`**: **`travelTimeFromStartLocationToFirstVisit`** (sum over all shifts).

**To office (return):**

- There is **no** separate itinerary entry for “return to depot”. The last item in a shift’s `itinerary` is the last visit (or a break); the return leg is only in the shift summary.
- **Per shift:** In that shift’s **`metrics`**: **`travelTimeFromLastVisitToEndLocation`** and **`endLocationArrivalTime`**.
- **Global:** In top-level **`kpis`**: **`travelTimeFromLastVisitToEndLocation`**.

**Example (from 073f6280 output):**  
One shift has `metrics`:  
`travelTimeFromStartLocationToFirstVisit`: "PT16M19S",  
`travelTimeBetweenVisits`: "PT40M35S",  
`travelTimeFromLastVisitToEndLocation`: "PT1M19S",  
`totalTravelTime`: "PT58M13S".

So: **office → first visit** and **last visit → office** are in **shift `metrics`** and in **`kpis`**, not as extra itinerary items.

---

## 4. Travel for the break event / FLOATING + location

**FLOATING and location can be combined.** The [Timefold FSR API](https://app.timefold.ai/openapis/field-service-routing/v1) defines **FloatingBreak** with an optional `location` (array of two numbers). So a FLOATING break can have a time window (minStartTime, maxEndTime, duration) and optionally a place; the solver then schedules travel to/from that place. See [Lunch breaks and personal appointments](https://docs.timefold.ai/field-service-routing/latest/vehicle-resource-constraints/lunch-breaks-and-personal-appointments#_floating_lunch_breaks) for the doc; the OpenAPI schema explicitly allows `location` on FloatingBreak.

**Where is travel for the break in the output?**  
When the break has a **location**, the **BREAK** itinerary item in `modelOutput.vehicles[].shifts[].itinerary` can include:

- **`travelTimeFromPreviousStandstill`** – travel from the previous standstill (last visit or depot) to the break location
- **`travelDistanceMetersFromPreviousStandstill`** – same in meters

(These are omitted when the break has no location or is unreachable on the map.) The travel *from* the break to the *next* standstill is the next itinerary item’s `travelTimeFromPreviousStandstill` (that next item is either a VISIT or the implicit return leg reflected in the shift’s `travelTimeFromLastVisitToEndLocation` if the break is last).

---

## 5. Same source: with and without break location (same config profile)

To compare the **same** expanded dataset with and without break location, use the same configuration profile for both runs ([Configuration parameters and profiles](https://docs.timefold.ai/timefold-platform/latest/how-tos/configuration-parameters-and-profiles)). That way the only variable is break location.

**Step 1 – One input with break location**  
From your expanded CSV, generate the FSR input (this already includes break locations when the pipeline uses service area / break_lat/break_lon):

```bash
cd docs_2.0/recurring-visits/huddinge-package/scripts
python3 csv_to_timefold_fsr.py ../expanded/your_expanded.csv -o ../solve/input_with_breakloc.json --name "Huddinge 2wk with break location"
```

**Step 2 – No-break-location variant**  
Strip `location` from every break so the dataset is identical except breaks have no place:

```bash
python3 strip_break_location.py ../solve/input_with_breakloc.json -o ../solve/input_nobreakloc.json --name "Huddinge 2wk no break location"
```

**Step 3 – Run both with the same configuration ID**  
Use the same `configurationId` so constraint weights, termination, and other profile settings are identical:

```bash
export TIMEFOLD_API_KEY="your-key"
CONFIG_ID="6a4e6b5f-8767-48f8-9365-7091f7e74a37"

# With break location
python3 submit_to_timefold.py solve ../solve/input_with_breakloc.json --configuration-id "$CONFIG_ID" --wait --save ../solve/out_with_breakloc.json

# Without break location (same source, same config)
python3 submit_to_timefold.py solve ../solve/input_nobreakloc.json --configuration-id "$CONFIG_ID" --wait --save ../solve/out_nobreakloc.json
```

Then compare KPIs (unassigned, travel times, break travel in itinerary) between the two outputs. Same config profile is applied via the `configurationId` query parameter on the [POST route-plans](https://app.timefold.ai/openapis/field-service-routing/v1) request.
