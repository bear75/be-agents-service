# ESS→FSR Integration Design

**Purpose:** Define how roster/zone output from ESS (or manual/stub) maps to FSR input (preferred/required vehicles per visit) and how to iterate (FSR output → continuity/metrics → optional feedback into next roster). ESS API integration is out of scope; this document delivers design and orchestration so ESS can be plugged in later.

**Related:** [Efficiency–continuity implementation plan](plans/2026-03-11-efficiency-continuity-implementation-plan.md) (Track B).

---

## 1. ESS output shape (high level)

Timefold **Employee Shift Scheduling (ESS)** assigns employees to shifts over a planning period. For integration with FSR we care about:

- **Assignments:** Which caregiver (employee) is assigned to which **zone** or **client set** per day (or per planning window).
- **Output shape (conceptual):** For each day (or period) and each zone/client identifier, ESS returns a list of employee IDs (or shift IDs that map to caregivers). In Timefold ESS API terms: shift assignments link employees to shift templates; if shifts are zone- or client-based, we get “who can serve which clients” per day.

For Caire we reduce this to a **roster**: per **client** (or per zone, if we aggregate clients by zone), a list of **vehicle/caregiver IDs** that are allowed or preferred for that client over the planning period. Vehicle IDs in FSR correspond to caregivers (one vehicle = one caregiver).

- **ESS → roster mapping (when ESS is integrated):** ESS API returns assignments (e.g. employee_id → zone_id per day). We aggregate by client: for each client, collect all employee IDs assigned to that client’s zone (or to that client) across the planning period, then map employee_id to FSR vehicle_id (same ID or via a mapping table). Result: one list of vehicle IDs per client (e.g. top-K or all assigned), which is exactly the **roster provider** output below.

---

## 2. FSR input: preferredVehicles / requiredVehicles from roster

FSR (Field Service Routing) accepts per visit:

- **preferredVehicles:** soft constraint; solver prefers these vehicles but may assign others to improve wait/travel.
- **requiredVehicles:** hard constraint; only these vehicles may serve the visit.

**Orchestrator responsibility:** For each visit in the base FSR input:

1. Derive **client** from the visit (e.g. KOLADA person from visit name, same logic as in `continuity_report.py` / `build_continuity_pools.py`: `name_to_person_kolada`).
2. Look up the roster for that client: `roster[client_id]` = list of vehicle IDs.
3. Cap the list at a configurable maximum (e.g. 10) to avoid oversized pools.
4. Set either:
   - `visit.preferredVehicles = roster[client_id][:max_per_client]`, or  
   - `visit.requiredVehicles = roster[client_id][:max_per_client]`  
   depending on strategy (soft vs hard continuity).

Visits with no roster entry for their client are left unchanged (no preferred/required set). The script that applies the roster is `scripts/apply_roster_to_fsr_input.py`.

---

## 3. Iteration: FSR output → continuity/metrics → optional feedback

- **One-way (no feedback):** Run ESS (or use manual/stub roster) → roster file → apply to FSR input → run FSR → measure continuity and efficiency (e.g. `continuity_report.py`, `metrics.py`).

- **With feedback:** After FSR run, use the **FSR output** (visit → vehicle assignments) to build a **stub roster**: per client, list of vehicle IDs that actually served that client (e.g. top-K by visit count). This roster can be:
  - Fed into the next FSR run as preferred/required vehicles (warm start / continuity lock-in), or  
  - Compared to the ESS-derived roster to adjust ESS parameters in a later iteration.

So the loop is: **Roster (ESS/manual/stub) → apply_roster_to_fsr_input → FSR solve → metrics/continuity report → (optional) fsr_output_to_roster → roster for next run or analysis.**

---

## 4. Roster provider interface

The orchestrator expects a **roster** in a single, well-defined shape. The roster can be produced by:

- **ESS (future):** ESS API client returns the same JSON shape (per client, list of vehicle IDs for the planning period).
- **Manual:** Hand-edited or CSV-derived JSON.
- **Stub:** Generated from a previous FSR output (e.g. `scripts/fsr_output_to_roster.py`).

**Contract:** The roster provider (file or API) returns:

- **Per client (or zone):** a list of caregiver/vehicle IDs for the planning period. Client ID must match how visits are resolved to clients in FSR input (e.g. KOLADA person: H001, H002, …).
- **Format:** JSON object: `client_id → [ vehicle_id_1, vehicle_id_2, … ]`, with optional metadata (see schema below). When ESS is integrated, an adapter converts ESS API response into this JSON and writes it to a file (or the orchestrator reads the same shape from an API response).

---

## 5. Roster JSON schema

Roster file (or API response) format:

```json
{
  "source": "ess",
  "assignments": {
    "H001": ["Dag_01_Central_1", "Dag_02_Central_1"],
    "H002": ["Dag_01_Central_2"]
  }
}
```

- **Top-level optional metadata:**
  - `source`: `"ess"` | `"manual"` | `"stub"` (origin of the roster).
  - Other keys (e.g. `_meta`, `planningPeriod`) may be added later; the orchestrator ignores unknown top-level keys when building assignments.

- **Assignments:** Either:
  - under key `"assignments"`: object mapping **client_id** (string) to **array of vehicle IDs** (strings); or  
  - **flat format:** top-level object where every key except reserved metadata (`source`, `_meta`) is a client_id and the value is an array of vehicle IDs.  
  The apply script accepts both: if `assignments` exists, use it; otherwise treat all non-reserved keys as client_id → vehicle list.

- **Max vehicles per client:** The orchestrator caps the number of vehicles per client (e.g. 10). So roster may contain more than 10 per client; only the first `max_per_client` are used when patching FSR input.

**Reserved top-level keys (ignored as client IDs):** `source`, `_meta`, `assignments` (when used as the container for client→vehicles).

**Example (flat format, stub from FSR output):**

```json
{
  "source": "stub",
  "H001": ["Dag_01_Central_1", "Dag_02_Central_1", "Dag_03_Central_1"],
  "H002": ["Dag_01_Central_2"]
}
```

---

## 6. Timefold ESS API (reference)

- **API:** `https://app.timefold.ai/api/models/employee-scheduling/v1` (shift scheduling, demand curves, shift templates).
- **Use case:** Rostering: who works when and where (zone/area). Output can be mapped to “which caregivers are assigned to which clients/zones” and then to the roster format above.
- **Integration point:** When ESS is integrated, a small adapter will (1) call ESS API, (2) map employee/shift assignments to client (or zone) and vehicle_id, (3) write the same roster JSON that `apply_roster_to_fsr_input.py` reads. No change to the apply script.

---

## 7. Scripts and E2E runbook

| Script | Role |
|--------|------|
| `scripts/apply_roster_to_fsr_input.py` | Reads base FSR input + roster JSON; sets preferredVehicles or requiredVehicles per visit from roster; writes patched FSR input. |
| `scripts/fsr_output_to_roster.py` | Reads FSR output (+ optional FSR input for visit→client); outputs roster JSON (client → top-K vehicles by visit count). |

### E2E: First-run → roster stub → patched input → re-solve and compare

1. **First-run FSR** (no roster): Submit base FSR input; fetch solution to `output_firstrun.json`.
2. **Build roster from first-run:**  
   `python scripts/fsr_output_to_roster.py --output output_firstrun.json --input base_input.json --out roster.json [--max-per-client 10]`
3. **Patch FSR input with roster:**  
   `python scripts/apply_roster_to_fsr_input.py --input base_input.json --roster roster.json --out input_with_roster.json [--max-per-client 10] [--use-required]`
4. **Re-solve:** Submit `input_with_roster.json` to FSR (e.g. via `submit_to_timefold.py solve`).
5. **Compare:** Run `continuity_report.py` and `metrics.py` on the new output vs first-run. Expect similar or better continuity (same or fewer caregivers per client) and comparable or acceptable efficiency (wait/travel); tuning preferred vs required and pool size affects the trade-off.

This pipeline validates the orchestrator and roster format without ESS; when ESS is added, replace step 2 with “get roster from ESS API (or ESS adapter that writes roster.json).”
