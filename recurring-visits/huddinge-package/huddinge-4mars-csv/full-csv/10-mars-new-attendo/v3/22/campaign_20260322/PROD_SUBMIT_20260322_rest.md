# Prod submit — “rest” batch (6 solves)

Submitted via `scripts/timefold/submit.py solve` with configuration profile  
`09a98b7a-956c-456a-b478-00f89880b826` (prod).  
Prepared inputs from `prepared/` (custom `config.model.overrides` + `maxThreadCount` per campaign script).

| Prepared input | Route plan ID |
|----------------|---------------|
| `v322-pool12-continuity-heavy.json` | `0ba5d5c7-d308-4bfe-b5b5-2c1d9cf08edf` |
| `v322-pool12-combo.json` | `85a24091-3866-4fcf-9f19-cd08d728507f` |
| `v322-pool8_extra-efficiency-first.json` | `54de1372-6fd4-4af9-bf3e-e004a868294f` |
| `v322-pool8_extra-balanced.json` | `2fcded88-87d5-4125-8646-5b991d264d78` |
| `v322-pool8_extra-continuity-heavy.json` | `8ecab57b-240d-4874-a86a-6aff215d228b` |
| `v322-pool8_extra-combo.json` | `1e96d8cb-2b37-410b-a82f-95d1cec253d4` |

**Fetch (when completed):**

```bash
cd /path/to/be-agent-service
export TIMEFOLD_API_KEY='(prod key from secure store)'
python3 scripts/timefold/fetch.py <ROUTE_PLAN_ID> --save .../output.json --metrics-dir .../metrics
```

Do not commit API keys; use `~/.config/caire/env` locally.
