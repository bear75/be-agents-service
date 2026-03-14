# Fetch solution: continuity run with config a43d4eec (621c8ba8)

Same input as b4881074 (continuity, original IDs), but submitted with config **a43d4eec-9f53-40b3-82ad-f135adc8c7e3** (Huddinge 2-week long run).

When the solve has completed in Timefold, run from **recurring-visits/scripts** (with `TIMEFOLD_API_KEY` set or in `~/.config/caire/env`):

```bash
cd /Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits/scripts
python3 fetch_timefold_solution.py 621c8ba8-6174-4efe-ad09-5aa0ede3a335 \
  --save ../huddinge-package/continuity\ -3march/export-field-service-routing-v1-621c8ba8-6174-4efe-ad09-5aa0ede3a335-output.json
```

Or from huddinge-package:

```bash
cd /Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits/huddinge-package
python3 ../scripts/fetch_timefold_solution.py 621c8ba8-6174-4efe-ad09-5aa0ede3a335 \
  --save "continuity -3march/export-field-service-routing-v1-621c8ba8-6174-4efe-ad09-5aa0ede3a335-output.json"
```

Then compare with b4881074 output (same input, default config) to confirm the only difference is config.
