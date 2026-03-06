# caire × Attendo — Huddinge Schedule Report

**Two solutions · Continuity analysis & conclusions**

*Attendo Schedule Pilot — Huddinge Hemtjänst · Recurring Visits · Powered by caire and EirTech*

bjorn@caire.se · caire.se · eirtech.ai

---

## 1. Both solutions (same basis)

Same 2-week Huddinge visit set (3,622 visits, 81 clients), compared on active time only (visit + travel + break).

| Metric | Run A | Run B | Difference |
|--------|--------|--------|------------|
| Visits assigned | 3,616 / 3,622 | 3,586 / 3,622 | −30 |
| Shifts with visits | 311 | 300 | −11 |
| Visit hours | 1,516 h | ~1,510 h | — |
| Travel hours | 227 h | ~170 h | −57 h |
| **Efficiency** (visit / visit+travel+break) | 87.0% | **89.9%** | **+2.9 pp** |
| **Continuity (avg caregivers per client)** | **19.6** | **2.5** | **−17.1** |
| Continuity (max) | 36 | 6 | −30 |
| **Clients over target (15)** | **58** | **0** | **−58** |

Run B has **better efficiency** and **far better continuity** on the same visit set.

---

## 2. Continuity analysis

**What we measure**  
Continuity = number of distinct caregivers serving each client over the 2-week window. Target: ≤15 per client.

**What we see**

- **Run A** — 81 clients, avg **19.6** caregivers per client, max 36. **58 of 81 clients** (72%) are over the target of 15. Care is spread across many staff; little stability.
- **Run B** — 81 clients, avg **2.5** caregivers per client, max 6. **All 81 clients** are at or below target; most see very few caregivers.

**Why the gap**

The two runs use different assignment and routing choices. Run B’s pattern — fewer shifts, less travel, more geographic clustering — gives:

1. **Stable routes** — The same shift tends to serve the same neighbourhood, so the same caregiver sees the same clients.
2. **Fewer handovers** — Fewer caregivers per client means less fragmentation and better continuity.

So the same structural choices that **reduce travel** (efficiency) also **reduce caregiver churn** (continuity).

---

## 3. Conclusions

1. **Continuity does not hurt efficiency**  
   Run B has both **higher efficiency** (89.9% vs 87.0%) and **much better continuity** (2.5 vs 19.6 avg, 0 vs 58 over target). In this pilot, better continuity goes with better efficiency.

2. **Efficiency and continuity go hand in hand**  
   Geographically sensible routing gives shorter travel and more stable assignments. “Same shift” and “same caregiver” align for many clients, so the run that is better on travel is also better on continuity.

3. **Implication for planning**  
   Optimising for efficiency (visit time vs travel, full shifts) can support continuity rather than work against it. The goal is routing that clusters visits by area and keeps assignment stable over the 2-week window.

---

## 4. Revenue & cost (same basis)

*Assumptions: 230 kr/h staff cost, 550 kr/h visit revenue; cost on active time only.*

| Item | Run A | Run B |
|------|--------|--------|
| Revenue (visit × 550 kr/h) | 833,589 kr | ~830,289 kr |
| Cost (active hours × 230 kr/h) | ~423,313 kr | ~411,449 kr |
| **Margin** | ~410,276 kr | ~418,840 kr |

---

## 5. Artifacts

| Run | Folder | Continuity |
|-----|--------|------------|
| A | `huddinge-datasets/28-feb/5ff7929f/` | `continuity.csv` |
| B | `huddinge-datasets/28-feb/203cf1d6/` | `continuity.csv` |

*Reference:* `Attendo_Schedule_Pilot_Report.pdf` — Manual vs Caire for the same Huddinge 2-week pilot.
