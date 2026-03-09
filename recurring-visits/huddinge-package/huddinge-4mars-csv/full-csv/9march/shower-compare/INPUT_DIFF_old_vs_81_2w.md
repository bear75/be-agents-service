# Input diff: old shower-bug (cece06c0) vs fsr_input_81_2w

## Summary: **same 3697 visits, not “only 8 different”**

| Metric | Old (cece06c0) | New (fsr_input_81_2w) |
|--------|----------------|------------------------|
| **Visits** | 3697 (3457 + 240 in 116 groups) | **3697** (identical) |
| **Visit IDs** | — | **0 only in old, 0 only in new** → same set |
| **Shifts** | 448 | **544** (+96) |
| **visitDependencies** | 474 | **508** (+34) |

So the two inputs have the **same visits and same visit IDs**. The differences are:

1. **+96 shifts** in the new input (544 vs 448) → more capacity.
2. **+34 visitDependencies** in the new input (508 vs 474) → **more constraints**.

## Where the 34 extra dependencies go

The 34 extra deps in the new dataset are **not** only on H035 (shower). They are spread across many clients, e.g.:

- H025, H034, H038, H053, H154, H157, H216, H235, H238, H243, H284, H327, H332, H337, H349, H354, H360, H362
- Typical pattern: “dusch/bad after morgon” (same-day, minDelay PT0M) or other precedingVisit + minDelay.

So the “shower fix” in the pipeline (dusch dikt med morgon) has been applied to **all** clients that have dusch/bad in the new run, not only to the 8 H035 shower visits. That adds many extra ordering constraints.

## Why 1364 vs 27 unassigned?

- **Same visits** ⇒ the 1364 unassigned are not from “extra visits” in the new input.
- **Same IDs** ⇒ no structural visit set difference.
- **More shifts** in the new input ⇒ capacity is higher, so by capacity alone the new run should not be worse.
- **+34 dependencies** ⇒ the new input is **more constrained**. If those constraints are tight or conflicting (e.g. same-day dusch-after-morgon across many clients), the solver can leave many visits unassigned (1364) even though the old run with fewer deps had only 27 (or 2) unassigned.

So the trend you see (1364 vs 27) is consistent with: **the only substantive difference in the inputs is the extra dependencies**, and that difference is enough to make the new run much worse in terms of unassigned visits.

## Litmus test

If we **removed the 8 shower visits** from the new input, we would still have **508 − (deps for those 8)** dependencies and the same 3689 other visits. So the main lever is not “8 visits” but “34 extra dependencies” applied across many clients. To test “only the 8 shower visits”:

- Build an input that is **old (cece06c0) + only the 8 H035 shower visit groups + only the dusch-after-morgon deps for those 8** (no extra deps for H034, H038, H154, …).
- Run solve and compare unassigned. If that run is close to 27 (or 2), the 34 extra deps elsewhere are the cause of 1364 unassigned.
