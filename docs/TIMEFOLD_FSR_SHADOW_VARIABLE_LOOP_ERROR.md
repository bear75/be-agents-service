# Timefold FSR Shadow Variable Loop Error

**Date:** 2026-03-19  
**Error Code:** `TIMEFOLD-20001`  
**Error ID:** `5b144d15-3926-4dac-854a-3c6b297cc10a`

## Error Summary

Timefold FSR solver is encountering **fixed dependency loops** in shadow variables for standalone visits (visits with `visitGroup=null`). The affected shadow variables are:

- `alignedVisitSchedule` (AlignedVisitSchedule)
- `singleVisitSchedule` (SingleVisitSchedule)  
- `visitGroupAlignmentTime` (OffsetDateTime)

## Error Details

The error occurs during model enrichment when Timefold tries to compute shadow variables. The solver detects circular dependencies where:

1. **Source-induced fixed loop**: Two shadow variables whose sources refer to each other
2. **Fact-induced fixed loop**: A shadow variable whose sources refer to itself transitively via a fact

The error message shows many standalone visits (e.g., `H332_2026-03-29_515, visitGroup=null`) that are causing these loops.

## Root Cause Analysis

**These shadow variables are meant for visit groups, not standalone visits.** The fact that standalone visits are triggering these shadow variable computations suggests:

1. **Possible Timefold bug**: The solver may be incorrectly trying to compute visit-group shadow variables for standalone visits
2. **Invalid input structure**: Circular dependencies in `visitDependencies` might be confusing the solver
3. **Data issue**: Standalone visits might have properties that make Timefold think they're part of groups

## Affected Visits

The error lists many visits with `visitGroup=null` that are causing loops, including:
- `H332_2026-03-29_515`
- `H332_2026-03-29_507`
- `H332_2026-03-27_515`
- `H362_2026-03-27_590`
- And many more...

All these visits are standalone (not in visit groups) but are triggering visit-group shadow variable computations.

## Potential Solutions

### 1. Check for Circular Dependencies

Verify that `visitDependencies` in the input JSON don't form cycles:

```bash
# Check input JSON for circular dependencies
python3 scripts/validation/check_circular_dependencies.py input.json
```

**If cycles exist:**
- Review the dependency creation logic in `csv_to_fsr.py`
- Ensure same-day dependencies (PT0M) don't create cycles
- Check spread dependencies don't loop back

### 2. Verify Visit Structure

Ensure standalone visits don't have properties that suggest they're in groups:

```bash
# Validate visit structure
python3 scripts/validation/validate_visit_structure.py input.json
```

**Check:**
- No `visitGroup` property on standalone visits (should be omitted, not `null`)
- No group-related properties on standalone visits
- Visit IDs are unique and don't conflict with group visit IDs

### 3. Review Dependency Logic

The dependency creation in `csv_to_fsr.py` (lines 980-1134) might be creating invalid dependencies:

- **Same-day dependencies** (PT0M) between visits that shouldn't be sequenced
- **Spread dependencies** that create cycles
- **Dependencies between standalone visits** that create circular references

### 4. Contact Timefold Support

If the input JSON is valid (no circular dependencies, correct structure), this appears to be a **Timefold FSR API bug**. Contact Timefold support with:

- Error ID: `5b144d15-3926-4dac-854a-3c6b297cc10a`
- Dataset ID: `08faa874-8b6b-405b-82ec-85d0790dd681`
- Error code: `TIMEFOLD-20001`
- Description: Shadow variables for standalone visits creating fixed loops

### 5. Workaround: Remove Problematic Dependencies

If circular dependencies are found, temporarily remove them to test:

```python
# In csv_to_fsr.py, add validation to prevent cycles
def _validate_no_cycles(preceding_map: Dict[str, Tuple[str, str]]) -> None:
    """Check for circular dependencies and raise error if found."""
    visited = set()
    for vid in preceding_map:
        if vid in visited:
            continue
        path = []
        current = vid
        while current in preceding_map:
            if current in path:
                raise ValueError(f"Circular dependency detected: {' -> '.join(path + [current])}")
            path.append(current)
            current = preceding_map[current][0]
        visited.update(path)
```

## Next Steps

1. **Immediate**: Check input JSON for circular dependencies
2. **Short-term**: Validate visit structure and dependency logic
3. **Long-term**: If input is valid, report to Timefold as a bug

## Related Files

- `scripts/conversion/csv_to_fsr.py` - Visit and dependency creation
- `recurring-visits/huddinge-package/README.md` - Pipeline documentation
- Timefold FSR API documentation on shadow variables

## References

- Timefold error message: "Fixed dependency loops indicate a problem in either the input problem or in the @ShadowSources of the looped @ShadowVariable"
- Error suggests checking that `@ShadowSources` don't form loops on the same entity
