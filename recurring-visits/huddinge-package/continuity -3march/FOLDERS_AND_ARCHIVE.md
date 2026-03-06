# continuity -3march — folders used vs archived

**Used for continuity vs efficiency tests (keep here):**

| Folder / file | Purpose |
|---------------|---------|
| **pipeline_da2de902/test_tenant/** | All active runs in **one folder per test** (5 tests): preferred_688faece/, wait_min_a4be8810/, combo_8e07450d/, from_patch_preferred_963c3aa9/, from_patch_combo/. Each has input.json or payload.json, output.json, continuity.csv, metrics/. See test_tenant/FILE_INDEX.md. |
| **2323 3 march origin contin/** | Source export used to build test_tenant inputs: `export-field-service-routing-v1-da2de902-fa25-432c-b206-413b630dd4df-input.json`. Needed by `prepare_continuity_test_variants.py` and `build_one_busy_day_input.py`. |

**Archived (moved to _archive/):**

| Was | Reason |
|-----|--------|
| pipeline_39f35dc7/, pipeline_5ff7929f/ | Old pipeline runs (different configs), superseded by test_tenant. |
| metrics_39f35dc7/, metrics_5ff7929f/, metrics_da2de902/ | Metrics for those old pipelines; test_tenant has its own metrics/. |
| pipeline_da2de902/*.json, pipeline_da2de902/continuity.csv | Root-level solve/from-patch/continuity before test_tenant; duplicates replaced by test_tenant. |
| Root .md (PIPELINE_*, EFFICIENCY_*, METRICS_*, ANALYZE_*, etc.) | One-off run/verify docs; summary lives in test_tenant (ANALYSIS_VS_GOAL, README). |
| Root export JSONs (5ff7929f, b4881074) | Exports for other pipelines; da2de902 source is in 2323 3 march origin contin/. |

**test_tenant — archived into test_tenant/_archive/:**

| File(s) | Reason |
|---------|--------|
| input_one_day_2026-02-16.json | One-busy-day run (failed); not part of main continuity vs efficiency comparison. |
| input_pool25_required.json, pools_25.json | Pool-25 experiment; main comparison uses pool-15 variants. |
| from_patch_output_preferred.json | Duplicate; canonical output is from_patch_output_preferred_963c3aa9.json. |

Everything needed to run or interpret the continuity vs efficiency tests is in **pipeline_da2de902/test_tenant/** (plus the one source file in **2323 3 march origin contin/**).
