# Continuity metrics

This document defines the continuity metrics used in scripts (e.g. `continuity_report.py`) and how they relate to KOLADA-style reporting.

---

## Unique count (current KOLADA metric)

**Definition:** For each client (person / Kundnr), the number of **distinct caregivers** (vehicles) who performed at least one visit for that client over the planning period.

- **Interpretation:** Lower is better (fewer caregivers = more continuity).
- **Range:** 1 to N (N = number of visits for that client in the limit; in practice often 1–15).
- **Aggregation:** Reported per client; summary uses **average unique count** across clients (e.g. average 3.2 caregivers per client).

Used in KOLADA and in the existing continuity report as the `continuity` column (distinct caregivers per client).

---

## CCI (Continuity of Care Index)

**Definition:** For each client,  
**CCI = Σ (n_i / N)²**  
where:

- **i** indexes caregivers (vehicles) who served that client,
- **n_i** = number of visits from caregiver *i* to that client,
- **N** = total visits for that client.

So CCI is the sum of squared shares of visits per caregiver. One caregiver doing all visits gives CCI = 1; visits spread evenly over K caregivers gives CCI = 1/K.

- **Interpretation:** **Higher is better** (more concentration of visits with fewer caregivers).
- **Range:** (0, 1]. CCI = 1 when one caregiver does all visits; CCI → 0 as visits are spread over many caregivers.
- **Aggregation:** Reported per client; summary uses **average CCI** across clients.

**Example:** Client with 10 visits: 6 from caregiver A, 4 from B.  
CCI = (6/10)² + (4/10)² = 0.36 + 0.16 = **0.52**.

---

## Primary-caregiver proportion (simplified option)

**Definition:** For each client, the **proportion of visits** performed by the **top-1 (primary) caregiver** — i.e. the caregiver with the most visits for that client.

- **Formula:** max(n_i) / N over caregivers *i*.
- **Interpretation:** Higher is better (more visits from a single caregiver).
- **Range:** (0, 1]. Equals 1 when one caregiver does all visits.

This is a simpler, single-number summary than full CCI. The current implementation uses **full CCI** in `continuity_report.py`; primary proportion can be added later as an optional column if needed.

---

## Script usage

- **continuity_report.py** outputs:
  - **client**, **nr_visits**, **continuity** (unique count), and optionally **cci** (when `--cci` is used, which is the default).
  - A summary line with **average CCI** and **average unique count**.
- With **--only-kundnr**, only clients matching Kundnr (e.g. H001, H002, …) are included (e.g. 115 clients for Huddinge v2).
- See script help: `python continuity_report.py --help`.
