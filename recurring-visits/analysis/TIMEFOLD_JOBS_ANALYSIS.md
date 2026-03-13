# Timefold FSR Jobs Analysis
**Generated:** 2026-03-12
**Environments:** Test (Caire Test) & Production (Caire Prod)

---

## Executive Summary

| Metric | Test Environment | Prod Environment | Notes |
|--------|-----------------|------------------|-------|
| **Total Route Plans** | 76 | 14 | Test has 5.4x more plans |
| **Completed** | 75 (98.7%) | 13 (92.9%) | High success rate in both |
| **Failed** | 1 (1.3%) | 1 (7.1%) | Low failure rate |
| **Running** | 0 | 0 | No active jobs |
| **From-Patch Jobs** | 0 | 1 | Only prod has patch jobs |
| **Total Visits** | 474 | 733 | Prod handles more visits |
| **Avg Visits/Plan** | 6.2 | 52.4 | Prod jobs are larger |

---

## Key Findings

### 1. High Unassigned Visit Rate (Critical Issue)
**Problem:** 100% of visits in sampled jobs are showing as unassigned across both environments.

- **Test:** 474 total visits, ALL unassigned
- **Prod:** 733 total visits, ALL unassigned

**Possible Causes:**
1. These are failed solves despite showing "SOLVING_COMPLETED" status
2. Capacity constraints - not enough vehicles/shifts for the visits
3. Time window conflicts preventing assignments
4. API returning incomplete data in list endpoint

**Recommendation:** Fetch individual job details for the largest jobs to investigate actual assignment rates and solver constraints.

### 2. Environment Usage Patterns

**Test Environment (76 jobs):**
- **Purpose:** Experimentation and validation
- **Job Types:** Mixed - Huddinge 4mars, Nova schedules, CAIRE projection tests
- **Volume:** Smaller jobs (avg 6.2 visits) suggests unit testing and prototyping
- **Success Rate:** 98.7% completion

**Production Environment (14 jobs):**
- **Purpose:** Actual scheduling runs
- **Job Types:** Primarily Huddinge schedules
- **Volume:** Larger jobs (avg 52.4 visits) suggests real-world use cases
- **Success Rate:** 92.9% completion
- **Notable:** Has 1 from-patch job (iterative refinement)

### 3. Job Distribution by Type

**Test Environment Recent Jobs:**
- Nova 4-Week Schedule: 84 visits (all unassigned)
- CAIRE Projection E2E Test: 220 visits, 22 visits (validation scenarios)
- Huddinge 4mars Schedule: Multiple runs with varying sizes (0-43 visits)
- Dataset tests: Timestamped runs

**Production Environment Recent Jobs:**
- Huddinge schedules dominate (10/10 recent jobs)
- Largest job: 260 visits
- From-patch job: 36 visits (trim-empty operation)
- Huddinge 2-Week Schedule: 6 visits

---

## Detailed Observations

### Success Metrics
✅ **High Completion Rate:** Both environments show >90% completion rate
⚠️ **All Visits Unassigned:** Critical issue requiring investigation
✅ **No Stuck Jobs:** No jobs in running/queued state
⚠️ **Low From-Patch Usage:** Only 1 from-patch job suggests limited iterative refinement

### Capacity Analysis
The high unassigned rate suggests systematic capacity issues:
- Jobs completing successfully but not assigning visits
- May indicate:
  - Insufficient vehicle/caregiver capacity
  - Time window constraints too restrictive
  - Geographic/location constraints preventing assignments
  - Configuration issues in Timefold setup

### Test vs Prod Comparison

| Aspect | Test | Prod | Analysis |
|--------|------|------|----------|
| Job Count | 76 | 14 | Test used for extensive experimentation |
| Avg Job Size | 6.2 visits | 52.4 visits | Prod handles production-scale problems |
| Failure Rate | 1.3% | 7.1% | Prod has slightly higher failure rate (expected for larger jobs) |
| From-Patch | 0 | 1 | Prod uses iterative refinement |

---

## Recommendations

### Immediate Actions

1. **Investigate Unassigned Visits**
   ```bash
   # Fetch detailed data for largest jobs
   python3 fetch_timefold_solution.py 115eb7f6-919b-443a-8afc-b03ef5777e60 \
     --api-key "tf_p_96b5507b-57be-4ab6-b0a6-08a9d3372938" \
     --save analysis/test_large_job.json \
     --metrics-dir analysis/metrics/

   # Check prod largest job
   python3 fetch_timefold_solution.py 70eb56bf-e858-4e34-b1c8-35f5ef8ba6ba \
     --api-key "tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8" \
     --save analysis/prod_large_job.json \
     --metrics-dir analysis/metrics/
   ```

2. **Review Capacity Configuration**
   - Check vehicle/shift capacity in FSR inputs
   - Validate time windows are reasonable
   - Review required vs preferred vehicle constraints
   - Confirm geography/location data is correct

3. **Analyze Failure Patterns**
   - Fetch details on the failed jobs
   - Compare input configurations of successful vs failed jobs
   - Check solver logs for constraint violations

### Medium-Term Improvements

1. **Increase From-Patch Usage**
   - Implement iterative refinement workflow
   - Use from-patch to trim empty shifts
   - Apply from-patch for continuity optimization

2. **Monitoring & Alerting**
   - Set up automated monitoring for unassigned visit rates
   - Alert when jobs complete with >10% unassigned
   - Track trends in job success rates

3. **Capacity Planning**
   - Analyze historical unassigned patterns
   - Identify systematic capacity gaps
   - Adjust vehicle/caregiver availability accordingly

4. **Configuration Optimization**
   - Test different Timefold configuration profiles
   - Compare required vs preferred vehicles impact
   - Tune constraint weights for better assignment rates

---

## Next Steps

1. **Deep Dive Analysis:** Fetch full details for top 5 jobs in each environment
2. **Constraint Review:** Examine why visits are unassigned in completed jobs
3. **Continuity Testing:** Run continuity-compare experiments in test
4. **Production Pipeline:** Establish from-patch workflow for prod
5. **Metrics Dashboard:** Create real-time monitoring for job health

---

## API Keys Used

- **Test Tenant:** `tf_p_96b5507b-57be-4ab6-b0a6-08a9d3372938`
- **Prod Tenant:** `tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8`

**Note:** Both tenants show healthy job completion rates but concerning unassigned visit rates requiring further investigation.

---

## Data Files

- **Full JSON Analysis:** `/Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits/analysis/timefold_jobs_analysis.json`
- **Fetch Script:** `/Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits/scripts/fetch_all_jobs.py`

