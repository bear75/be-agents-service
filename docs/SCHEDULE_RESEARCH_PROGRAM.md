# Schedule Research Program

**Version:** 1.0.0
**Last Updated:** 2026-03-14
**Program Hash:** `{GIT_HASH_PLACEHOLDER}`

---

## Overview

This document defines the autonomous AI research program for Timefold schedule optimization. It provides instructions, constraints, and evaluation criteria for the mathematician and specialist agents to iteratively improve scheduling results.

**Purpose:** Achieve goal metrics through systematic experimentation, learning, and strategy refinement.

**Scope:** Isolated R&D in be-agent-service (not production beta-appcaire).

---

## Goal Metrics

The research program aims to achieve these target metrics:

| Metric | Target | Current Best | Status |
|--------|--------|--------------|--------|
| **Continuity Average** | ≤ 11.0 | 14.0 | 🔴 Not met |
| **Continuity Max** | ≤ 20.0 | TBD | ⚠️ Unknown |
| **Unassigned %** | < 1.0% | 0.1% | ✅ Met |
| **Routing Efficiency** | > 70.0% | 90.03% | ✅ Met |

**Primary Focus:** Reduce continuity average from 14.0 → ≤ 11.0 while maintaining efficiency and minimizing unassigned visits.

---

## Research Strategy

### Freedom to Explore

**You are free to propose ANY strategy**, not limited to documented families below. Use creativity, domain knowledge, and deep research when progress plateaus.

**Core Principle:** Systematic experimentation with clear hypotheses, measurable outcomes, and learning from both successes and failures.

### Strategy Families (Starting Points)

These are **examples** to seed initial exploration. Feel free to combine, modify, or invent entirely new approaches.

#### 1. Pool Size Variation
Test different continuity pool sizes to find optimal carer-client assignment balance.

**Variants:**
- Pool 3: Tight continuity, may sacrifice efficiency
- Pool 5: Balanced approach (baseline)
- Pool 8: Looser continuity, better efficiency potential

**Hypothesis:** Smaller pools reduce continuity average but may increase unassigned visits or reduce efficiency.

#### 2. Required vs Preferred Vehicles
Test vehicle assignment modes in FSR.

**Variants:**
- **Required:** Strict vehicle-to-shift assignment (hard constraint)
- **Preferred:** Soft preference, allows flexibility (soft constraint)
- **Hybrid:** Required for critical visits, preferred for others

**Hypothesis:** Preferred mode gives Timefold more flexibility to optimize routes, potentially improving both continuity and efficiency.

#### 3. From-Patch Optimization (Continuity Tightening)
Build from previous solution's assignment, pin visits to vehicles, then re-optimize with tighter continuity constraints.

**Approach:**
1. Run fresh solve (get baseline solution)
2. Build continuity pools from solution
3. Create from-patch payload (pin visits to vehicles)
4. Submit from-patch with stricter continuity targets

**Hypothesis:** Pinning visits preserves good assignments while allowing Timefold to refine routes and reduce continuity violations.

#### 4. Area Weighting & Clustering
Assign weight/penalty to geographic distance to encourage regional clustering.

**Variants:**
- Area weight 1.5x
- Area weight 2.0x
- Distance penalty for cross-region assignments

**Hypothesis:** Regional clustering reduces travel time and naturally improves continuity by keeping carers in familiar areas.

#### 5. ESS + FSR Integration (Shift-then-Route)
Use ESS (Employee Shift Scheduling) to first generate optimal shift patterns, then FSR to assign visits.

**Two-stage approach:**
1. **Stage 1 (ESS):** Optimize shift start/end times, breaks, capacity
2. **Stage 2 (FSR):** Route visits within optimized shifts

**Hypothesis:** Pre-optimized shifts provide better foundation for FSR, avoiding infeasible shift-visit combinations.

#### 6. Front-Loading & Binary Tree Strategies
Advanced combinatorial approaches (from past research).

**Examples:**
- Front-load high-continuity clients to preferred carers
- Binary tree search for optimal pool assignments
- Gradual constraint relaxation

**Hypothesis:** Strategic ordering and tree-based exploration may find solutions standard solvers miss.

---

## One Experiment Definition

An experiment is **one FSR solve** (or one from-patch variant) with a clear hypothesis.

### Experiment Structure

```json
{
  "experiment_id": "pool5_from_patch_continuity_v2",
  "hypothesis": "From-patch with pool size 5 and stricter continuity target (10.0) will reduce avg continuity below 11.0",
  "base_job_id": "82a338b9",
  "strategy": {
    "type": "from_patch",
    "pool_size": 5,
    "continuity_target": 10.0,
    "pin_visits": true
  },
  "expected_outcome": "continuity_avg < 11.0, efficiency > 85%"
}
```

### Input Sizing (Vehicles & Shifts)

The **CSV with Slinga is the starting point**: conversion produces one vehicle per unique Slinga and shifts per vehicle per date in the planning window. There is **no hard cap** on vehicle or shift count; typical ranges are on the order of tens of vehicles and hundreds of shifts (e.g. 300–500 shifts can be relevant). **The researcher decides** sizing based on the problem and experiments.

- **csv_to_fsr.py:** optional `--max-vehicles` and `--max-shifts-per-vehicle` let you shape supply (e.g. to avoid sending far more shifts than needed). Use or omit as the researcher sees fit.
- Uncap conversion yields one vehicle per Slinga and many shifts; if that is too large for the solver or experiments, use the optional caps.

### Impossible Visit Time Windows (Researcher Must Analyze)

The researcher must **analyze impossible visit time windows (start, end, and delay)** and use that when proposing strategies:

- **Window too short:** visit time window (minStartTime → maxEndTime) shorter than serviceDuration → visit cannot be scheduled in that window.
- **Dependency impossible:** visitDependencies with minDelay; if predecessor’s earliest end + delay is after successor’s latest possible start (maxEndTime − serviceDuration), the pair cannot be satisfied.

**How to run:**  
`submit_to_timefold.py validate <input.json> --save-analysis <path>`  
This runs format validation and writes an `impossible_time_windows` report (window_too_short, dependency_impossible). Use this report to suggest fixes (e.g. relax time windows, adjust dependencies, or flag data errors).

### Execution Steps

1. **Prepare input** (CSV → FSR from Slinga; optionally use `--max-vehicles` / `--max-shifts-per-vehicle`, or from-patch payload)
2. **Optionally run impossible time window analysis** (`validate --save-analysis`) and consider in strategy.
3. **Submit to Timefold** (via `scripts/timefold/submission/submit_solve.py` or specialist)
4. **Fetch solution** (poll until complete)
5. **Calculate metrics** (via `scripts/timefold/analysis/metrics.py`)
6. **Compare to baseline** (vs. best result in research state)
7. **Make decision:** keep, kill, or double_down
8. **Update research state** (append to history, update best if improved)

### Outcome Evaluation

Compare metrics to baseline and targets:

| Decision | Criteria |
|----------|----------|
| **Keep** | Improvement in 1+ metrics without regression in others |
| **Kill** | Worse than baseline across all metrics OR introduces critical failure (e.g., >10% unassigned) |
| **Double Down** | Significant improvement (e.g., continuity reduced by >2.0 or efficiency gained >5%) → run variants |
| **Continue** | Marginal change, need more data or related experiments |

**Record decision and reasoning** in research state for learning.

---

## Stopping Conditions

The research loop stops when ANY of these conditions is met:

### 1. Goal Achieved ✅
- Continuity average ≤ 11.0
- Continuity max ≤ 20.0
- Unassigned % < 1.0%
- Efficiency > 70.0%

**Action:** Celebrate, document final strategy, prepare for production integration.

### 2. Max Iterations Reached 🛑
- Default: 50 iterations
- Configurable via `config/timefold.yaml`

**Reason:** Prevents infinite loops, enforces periodic human review.

**Action:** Generate summary report, recommend next steps (more iterations vs. different approach).

### 3. Plateau Detected 📉
- No improvement for 5+ consecutive runs
- Definition: No run in last 5 beats current best

**Action:** Trigger deep research (see below), then continue or stop.

### 4. Manual Cancellation 🚫
- User cancels via dashboard or API

**Action:** Clean up, save state, exit gracefully.

---

## Deep Research Triggers

Deep research is triggered when:

### Scheduled Intervals
- Every 10 runs (configurable)

### Plateau Detection
- No improvement for 5 consecutive runs

### Mathematician Request
- Agent explicitly requests deep research (e.g., \"stuck, need new ideas\")

### Deep Research Tasks

When deep research is triggered, the mathematician agent should:

1. **Search Timefold Documentation**
   - FSR best practices
   - ESS shift scheduling patterns
   - Constraint tuning guidance
   - Latest optimization techniques

2. **Analyze Run History**
   - Pattern detection: What strategies worked? What failed?
   - Metric correlations: Do certain strategies always trade off efficiency for continuity?
   - Outlier identification: Any anomalous results worth investigating?

3. **Research Industry Approaches**
   - Academic papers on shift-then-route
   - VRP (Vehicle Routing Problem) with continuity constraints
   - Home healthcare scheduling optimization

4. **Propose Novel Combinations**
   - Combine successful elements from past runs
   - Suggest untested constraint combinations
   - Propose hybrid strategies

**Output:** New experiment proposals with clear hypotheses and expected outcomes.

---

## Research Loop Workflow

```
┌─────────────────────────────────────────────────────┐
│ 1. Read research state + program                    │
│    - Last run, best result, history                 │
│    - Program version (git hash)                     │
│    - Iteration count, phase (exploration/exploitation)│
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 2. Check stopping conditions                        │
│    - Goal met? Max iterations? Plateau?             │
│    - If stop → exit with summary                    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 3. Mathematician proposes strategy                  │
│    Input: research state, best result, history      │
│    Output: experiment JSON (hypothesis, strategy)   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 4. Specialist executes strategy                     │
│    - Prepare input (CSV → FSR or from-patch)        │
│    - Submit to Timefold                             │
│    - Fetch solution (poll until complete)           │
│    - Calculate metrics                              │
│    - Register run to database                       │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 5. Evaluate result                                  │
│    - Compare to best                                │
│    - Decision: keep / kill / double_down            │
│    - Record reasoning                               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 6. Update research state                            │
│    - Append run to history                          │
│    - Update best if improved                        │
│    - Increment iteration count                      │
│    - Adjust research phase if needed                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 7. Deep research check                              │
│    - Scheduled interval (every 10)?                 │
│    - Plateau detected?                              │
│    - If yes → trigger deep research                 │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
                LOOP (iteration += 1)
```

---

## Research Phases

The research program operates in phases:

### Exploration Phase (Iterations 1-20)
**Goal:** Broad sampling of strategy families to identify promising directions.

**Characteristics:**
- High diversity in strategies
- Test extremes (e.g., pool 3 vs pool 8)
- Quick kills for obviously bad strategies
- Build intuition about metric trade-offs

**Success Criteria:** Identify 2-3 promising strategy families.

### Exploitation Phase (Iterations 21-40)
**Goal:** Refine best strategies with systematic variants.

**Characteristics:**
- Focus on top performers from exploration
- Fine-tune parameters (e.g., continuity target 10.5 vs 11.0)
- Run from-patch variants to squeeze out improvements
- Document what works and why

**Success Criteria:** Achieve goal metrics or identify optimal configuration within explored space.

### Deep Dive Phase (Iterations 41-50)
**Goal:** Last-resort novel approaches if goals not yet met.

**Characteristics:**
- Aggressive deep research
- Hybrid/combined strategies
- High-risk, high-reward experiments
- Consider declaring plateau if no progress

**Success Criteria:** Either achieve goals or recommend stopping with best-known solution.

---

## Decision Framework

### Keep
- Improvement in 1+ goal metrics
- No critical regressions (e.g., unassigned doesn't spike >5%)
- Document: "What improved? Why?"

**Example:**
```
Decision: Keep
Reason: Continuity avg improved from 14.0 → 13.2 (-0.8), efficiency maintained at 89.5%. Pool 5 from-patch showing promise.
Next: Test stricter continuity target (10.0 vs 11.0)
```

### Kill
- Worse than baseline across all metrics
- Critical failure (e.g., >10% unassigned, infeasible solution)
- Document: "Why failed? What learned?"

**Example:**
```
Decision: Kill
Reason: Pool 3 required vehicles resulted in 8% unassigned (vs 0.1% baseline). Too restrictive, Timefold couldn't find feasible solution.
Learning: Pool 3 not viable with required mode. Try pool 3 with preferred mode or pool 5.
```

### Double Down
- Significant improvement (continuity -2.0 or efficiency +5%)
- Clear signal this direction is promising
- Document: "What worked? What variants to try?"

**Example:**
```
Decision: Double Down
Reason: From-patch with area weight 2.0x reduced continuity from 14.0 → 12.1 (-1.9) and improved efficiency from 90.0% → 92.5% (+2.5%). Strong signal.
Next variants:
1. From-patch + area weight 2.5x
2. From-patch + area weight 2.0x + stricter continuity target (10.0)
3. From-patch + area weight 2.0x + pool 3
```

---

## Metrics Definitions

### Continuity Average
Average number of different carers visiting each client over the planning horizon.

**Target:** ≤ 11.0
**Formula:** `sum(carers_per_client) / total_clients`

**Lower is better.** Ideal = 1.0 (same carer always).

### Continuity Max
Maximum number of different carers visiting any single client.

**Target:** ≤ 20.0
**Formula:** `max(carers_per_client_i for all clients i)`

**Identifies worst-case outliers.**

### Unassigned %
Percentage of visits not assigned to any vehicle/carer.

**Target:** < 1.0%
**Formula:** `(unassigned_visits / total_visits) * 100`

**Critical:** >5% indicates infeasible solution.

### Routing Efficiency
Ratio of productive field time to total shift time.

**Target:** > 70.0%
**Formula:** `field_time / (field_time + travel_time + idle_time) * 100`

**Measures how well routes are optimized.**

---

## Experimentation Guidelines

### Hypothesis-Driven

Every experiment must have:
1. **Clear hypothesis** - What do you expect to happen and why?
2. **Testable prediction** - Specific metric targets (e.g., "continuity < 12.0")
3. **Success criteria** - How will you evaluate the result?

**Bad Example:**
```
"Try pool 5 and see what happens"
```

**Good Example:**
```
Hypothesis: Pool 5 from-patch with continuity target 10.0 will reduce avg continuity below 11.0 while maintaining >85% efficiency.
Prediction: continuity_avg ∈ [10.5, 11.5], efficiency > 85%, unassigned < 1%
Success: If continuity < 11.0 → Double Down, else → Kill
```

### Learn from Failures

Failed experiments are valuable. Document:
- **Why it failed** (infeasible? Worse metrics? Timefold error?)
- **What was learned** (constraint too tight? Wrong assumption?)
- **What NOT to try again** (avoid repeating known failures)

### Incremental Changes

When refining a strategy:
- Change ONE parameter at a time
- Makes it clear what caused improvement/regression
- Exception: Hybrid strategies that intentionally combine multiple changes

### Parallel Experimentation (Future)

Currently runs sequentially. Future enhancement: Run multiple variants in parallel.

**Example:** Submit pool3, pool5, pool8 simultaneously, compare when all complete.

---

## State Management

### Research State Schema

```json
{
  "dataset": "huddinge-v3",
  "program_version": "abc123ef",
  "iteration_count": 12,
  "research_phase": "exploitation",
  "last_run": {
    "job_id": "f3d21abc",
    "experiment_id": "pool5_from_patch_v2",
    "timestamp": "2026-03-14T10:45:00Z",
    "status": "completed",
    "metrics": {
      "continuity_avg": 13.2,
      "continuity_max": 19,
      "unassigned_pct": 0.3,
      "efficiency": 89.5
    },
    "decision": "keep",
    "decision_reason": "Continuity improved by 0.8, no regressions"
  },
  "best_result": {
    "job_id": "82a338b9",
    "experiment_id": "pool5_baseline",
    "achieved_at": "2026-02-28T14:30:00Z",
    "metrics": {
      "continuity_avg": 14.0,
      "continuity_max": 22,
      "unassigned_pct": 0.1,
      "efficiency": 90.03
    }
  },
  "history": [
    {
      "iteration": 11,
      "job_id": "abc123",
      "experiment_id": "pool3_required",
      "metrics": { ... },
      "decision": "kill",
      "decision_reason": "8% unassigned, infeasible"
    },
    ...
  ],
  "learnings": [
    "Pool 3 with required vehicles causes high unassigned %",
    "From-patch with area weighting shows promise",
    "Efficiency and continuity sometimes trade off, sometimes improve together"
  ]
}
```

### State Persistence

**Storage:** Database table `research_state` (see Phase 3.2)

**Versioning:** Program version tracked via git hash to detect program changes.

**Rollback:** If program version changes mid-research, reset iteration count but preserve history.

---

## Integration Points

### Database

Research state and run results stored in be-agent-service database:

- `schedule_runs` table - Individual run results
- `research_state` table - Current research state (Phase 3.2)

### API Endpoints

- `GET /api/research/state?dataset=huddinge-v3` - Get current state
- `POST /api/research/state` - Update state
- `POST /api/research/trigger` - Start research loop
- `POST /api/research/cancel` - Cancel running loop
- `GET /api/research/logs` - Fetch loop logs

### Agents

- **Mathematician** (`agents/optimization-mathematician.sh`) - Proposes strategies
- **Specialist** (`agents/timefold-specialist.sh`) - Executes strategies

### Scripts

- **Loop** (`scripts/compound/schedule-research-loop.sh`) - Main orchestration
- **Conversion** (`scripts/timefold/conversion/csv_to_fsr.py`) - CSV → FSR
- **Submission** (`scripts/timefold/submission/submit_solve.py`) - Submit to Timefold
- **Analysis** (`scripts/timefold/analysis/metrics.py`) - Calculate metrics

---

## Reporting

### Per-Run Report

After each experiment:

```markdown
## Run #12: pool5_from_patch_v2

**Hypothesis:** From-patch with stricter continuity target (10.0) will reduce avg < 11.0

**Result:**
- Job ID: f3d21abc
- Status: Completed
- Duration: 847 seconds

**Metrics:**
| Metric | Value | Baseline | Delta | Target | Status |
|--------|-------|----------|-------|--------|--------|
| Continuity Avg | 13.2 | 14.0 | -0.8 | ≤11.0 | 🟡 Improving |
| Continuity Max | 19 | 22 | -3 | ≤20.0 | ✅ Met |
| Unassigned % | 0.3% | 0.1% | +0.2% | <1.0% | ✅ Met |
| Efficiency | 89.5% | 90.03% | -0.53% | >70% | ✅ Met |

**Decision:** Keep

**Reasoning:** Continuity improved by 0.8 points with minimal efficiency regression. From-patch approach showing promise. Next: Test area weighting.

**Next Steps:**
1. pool5_from_patch_area_weight_2x
2. pool5_from_patch_continuity_target_9.5
```

### Loop Summary Report

At the end of research loop (goals met or stopped):

```markdown
# Schedule Research Summary

**Dataset:** huddinge-v3
**Program Version:** abc123ef
**Total Iterations:** 28
**Duration:** 6.5 hours
**Final Status:** ✅ Goals Achieved

## Results

**Best Solution:**
- Job ID: xyz789
- Experiment: pool5_from_patch_area_2x_target_10
- Continuity Avg: 10.8 (Target: ≤11.0) ✅
- Continuity Max: 18 (Target: ≤20.0) ✅
- Unassigned %: 0.4% (Target: <1.0%) ✅
- Efficiency: 88.2% (Target: >70%) ✅

## Key Learnings

1. **From-patch optimization is critical** - Fresh solves plateaued at 14.0, from-patch broke through to 10.8
2. **Area weighting 2.0x** - Encouraged regional clustering, reduced both continuity and travel time
3. **Pool size 5 is optimal** - Pool 3 too restrictive (high unassigned), pool 8 too loose (high continuity)
4. **Required vs preferred vehicles** - Preferred mode gives Timefold flexibility, performed better

## Strategy Recommendation

**Production Strategy:** pool5_from_patch_area_2x_target_10

**Steps:**
1. Fresh solve with pool 5, preferred vehicles, area weight 2.0x
2. Build continuity pools from solution
3. From-patch with continuity target 10.0, pin visits to vehicles
4. Submit from-patch to Timefold
5. Expected result: continuity ≤ 11.0, efficiency > 85%, unassigned < 1%

## Failed Approaches (Do Not Repeat)

1. Pool 3 with required vehicles → 8% unassigned
2. Continuity target < 9.0 → infeasible solutions
3. Area weight > 3.0x → over-penalizes cross-region, fragments routes

## Next Steps

1. Integrate winning strategy into beta-appcaire production flow
2. Monitor real-world performance (may differ from test data)
3. Consider ESS + FSR two-stage approach for further optimization
```

---

## Version Control

This research program is version-controlled via git. Track program version (git hash) in research state to detect when program changes mid-research.

**On Program Update:**
- Notify running research loops
- Option: Continue with old program or restart with new program
- Preserve history for learning

---

## See Also

- `config/timefold.yaml` - Configuration and goal metrics
- `docs/TIMEFOLD_WORKFLOW.md` - End-to-end workflow guide
- `docs/CONSOLIDATED_SCRIPTS.md` - Script migration map
- `scripts/timefold/README.md` - Script documentation
- `schema.sql` - Database schema including `schedule_runs` and `research_state`

---

**Last Updated:** 2026-03-14
**Program Version:** To be set on first commit
