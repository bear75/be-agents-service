# Continuity Campaign Summary

**Campaign**: continuity-focused-v3-19
**Input File**: `export-field-service-routing-v1-aaf9d57f-c03a-494b-afa1-f8d07a6de66e-input.json`
**Submitted**: 2026-03-19 22:50:51
**Termination**: PT3H (3 hours max)

## Variants

| Variant | Strategy | Route Plan ID | Status |
|---------|----------|---------------|--------|
| baseline | baseline | `4bb72c31-10c7-4180-959d-61afd92fb84d` | submitted |
| pool5_high_continuity | pool5-required-vehicles | `ce246ec9-a0dd-47df-a050-0aa89ffede71` | submitted |
| pool7_balanced | pool7-required-vehicles | `877c9802-307a-4158-9d99-81bd6da8a4ec` | submitted |
| pool8_preferred | pool8-preferred-vehicles | `907775ba-4962-49b6-9c11-264d7a6ecc61` | submitted |
| pool10_continuity_heavy | pool10-required-vehicles | `6f716c8b-fb67-49a0-b311-aeb9b6b248c4` | submitted |

## Fetch Commands

To fetch solutions after completion:

```bash
# baseline
python3 recurring-visits/scripts/submit_to_timefold.py fetch 4bb72c31-10c7-4180-959d-61afd92fb84d \
  --save /Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/19/baseline_output.json

# pool5_high_continuity
python3 recurring-visits/scripts/submit_to_timefold.py fetch ce246ec9-a0dd-47df-a050-0aa89ffede71 \
  --save /Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/19/pool5_high_continuity_output.json

# pool7_balanced
python3 recurring-visits/scripts/submit_to_timefold.py fetch 877c9802-307a-4158-9d99-81bd6da8a4ec \
  --save /Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/19/pool7_balanced_output.json

# pool8_preferred
python3 recurring-visits/scripts/submit_to_timefold.py fetch 907775ba-4962-49b6-9c11-264d7a6ecc61 \
  --save /Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/19/pool8_preferred_output.json

# pool10_continuity_heavy
python3 recurring-visits/scripts/submit_to_timefold.py fetch 6f716c8b-fb67-49a0-b311-aeb9b6b248c4 \
  --save /Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/19/pool10_continuity_heavy_output.json

```
