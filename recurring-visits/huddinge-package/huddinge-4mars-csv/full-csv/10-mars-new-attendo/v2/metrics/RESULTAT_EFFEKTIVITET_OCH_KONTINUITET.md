# Resultat: effektivitet och kontinuitet (v2 Huddinge, 2 veckor)

**Plan:** d2a6a01b (baseline utan continuity-pools)  
**Data:** 115 klienter (Kundnr), 41 vårdgivare, 3832 besök (Timefold), 2 veckor.

---

## Sammanfattning

| Mått | Värde | Mål / kommentar |
|------|--------|------------------|
| **Wait efficiency** | **70,96%** | visit / (visit + travel + wait); mål >70% ✓ |
| **Travel efficiency** | 77,01% | visit / (visit + travel); mål >67,5% ✓ |
| **Otilldelade besök** | 36 | av 3832 (0,94%); mål <1% ✓ |
| **Kontinuitet (snitt unika vårdgivare per klient)** | **17,73** | KOLADA; mål ≤11 ✗ (för många vårdgivare per klient) |
| **CCI (Continuity of Care Index)** | **0,2209** | 0–1, högre = bättre; låg = många olika vårdgivare |

---

## Tolking

- **Effektivitet:** Bra – wait efficiency över 70%, färre än 1% otilldelade.
- **Kontinuitet:** Dålig – i snitt nästan 18 olika vårdgivare per klient över 2 veckor; CCI låg (0,22). Detta är baseline utan continuity-pools; pool 5–10 och högre preferred-vehicle-vikt ska förbättra kontinuitet.

---

## Filer

- **Sammanfattning (JSON):** `run_summary_d2a6a01b.json`
- **Sammanfattning (MD):** `run_summary_d2a6a01b.md`
- **Full metrics:** `metrics_report_d2a6a01b.txt`, `metrics_*.json`
- **Kontinuitet per klient:** `continuity.csv` (kolumnerna inkl. `cci`)

---

## Nästa steg (enligt plan)

1. Köra kampanj med pool 5, 8, 10 och fler vikter (preferred 2/10/20, combo, required).
2. Jämföra dessa resultat (effektivitet + kontinuitet + CCI) i en Pareto-tabell.
