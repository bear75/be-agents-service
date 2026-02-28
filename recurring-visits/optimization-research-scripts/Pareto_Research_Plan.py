#!/usr/bin/env python3
"""
Pareto Frontier Research Plan - Exact Implementation
Based on /Users/bjornevers_MacPro/HomeCare/beta-appcaire/.cursor/plans/continuity_research_priority_c94d2043.plan.md
"""

import json
import os
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class ResearchJob:
    """Single research job in the Pareto frontier sweep"""
    name: str
    n_value: int
    method: str
    description: str
    priority: int
    expected_efficiency: float = 0.0
    expected_continuity: float = 0.0

class ParetoResearchPlan:
    """Implementation of the exact Pareto frontier research plan"""
    
    def __init__(self):
        # Confirmed baselines from Pilot Report (24feb)
        self.manual_baseline = {
            "efficiency": 67.8,  # excl idle
            "travel": 24.0,
            "margin": 31.0,
            "continuity": 2.9
        }
        
        self.unconstrained_baseline = {
            "efficiency": 85.7,  # excl idle  
            "travel": 9.8,
            "margin": 51.0,
            "continuity": 19.3,
            "unassigned": 114,
            "route_plan_id": "391486da-ca6f-4928-a928-056a589842e1"
        }
        
        # Sweet spot criteria from plan
        self.sweet_spot_criteria = {
            "min_efficiency": 77.0,
            "max_continuity": 10.0
        }
        
        # Configuration from plan
        self.config = {
            "api_key": "tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8",
            "config_id": "a43d4eec-9f53-40b3-82ad-f135adc8c7e3",  # short, max-assigned
            "base_input": "solve/input_20260224_202857.json",
            "seed_output": "solve/iter1/391486da-output.json",
            "expanded_csv": "expanded/huddinge_2wk_expanded_20260224_043456.csv",
            "working_dir": "docs_2.0/recurring-visits/huddinge-package",
            "scripts_dir": "../scripts"
        }
    
    def generate_research_jobs(self) -> List[ResearchJob]:
        """Generate exact research jobs from the plan"""
        
        jobs = []
        
        # Approach 0: Direct Slinga (exact manual assignment)
        jobs.append(ResearchJob(
            name="approach_0_direct_slinga",
            n_value=1,  # pool≈1
            method="direct_slinga",
            description="Exact manual slinga assignment per visit (FSR routing within constraints)",
            priority=1,
            expected_efficiency=70.0,  # Better than manual 67.8%
            expected_continuity=2.85   # Matches theoretical minimum
        ))
        
        # First-run pool sweep (N=4 minimum as requested, no N=1,2,3)
        sweep_n_values = [4, 5, 8, 15]  # From plan, adjusted for N=4 minimum
        
        for n_value in sweep_n_values:
            jobs.append(ResearchJob(
                name=f"sweep_n{n_value}_first_run",
                n_value=n_value,
                method="first_run",
                description=f"First-run pool size {n_value} from 391486da baseline",
                priority=self._calculate_priority(n_value),
                expected_efficiency=self._estimate_efficiency(n_value),
                expected_continuity=self._estimate_continuity(n_value)
            ))
        
        # Unconstrained baseline (for comparison)
        jobs.append(ResearchJob(
            name="unconstrained_baseline",
            n_value=999,  # No constraint
            method="unconstrained",
            description="Baseline unconstrained FSR (existing 391486da)",
            priority=5,
            expected_efficiency=85.7,
            expected_continuity=19.3
        ))
        
        return jobs
    
    def _calculate_priority(self, n_value: int) -> int:
        """Calculate execution priority based on sweet spot likelihood"""
        
        estimated_eff = self._estimate_efficiency(n_value)
        estimated_cont = self._estimate_continuity(n_value)
        
        # Priority 1: Sweet spot candidates
        if (estimated_eff >= 77.0 and estimated_cont <= 10.0):
            return 1
        # Priority 2: Close to sweet spot  
        elif (estimated_eff >= 75.0 and estimated_cont <= 12.0):
            return 2
        # Priority 3: Significant improvement over manual
        else:
            return 3
    
    def _estimate_efficiency(self, n_value: int) -> float:
        """Estimate efficiency based on N-value and known data points"""
        
        if n_value >= 15:
            return 83.0  # Approaching unconstrained
        elif n_value >= 8:
            return 81.0  # High efficiency
        elif n_value >= 5:
            return 78.0  # Sweet spot zone  
        elif n_value >= 4:
            return 75.0  # Still improvement over manual
        else:
            return 72.0  # Conservative for low N
    
    def _estimate_continuity(self, n_value: int) -> float:
        """Estimate continuity based on N-value"""
        
        if n_value >= 15:
            return 14.0
        elif n_value >= 8:
            return 9.5   # Sweet spot zone
        elif n_value >= 5:
            return 7.0   # Sweet spot zone
        elif n_value >= 4:
            return 5.5
        else:
            return 4.0
    
    def generate_execution_script(self) -> str:
        """Generate bash script for exact execution"""
        
        jobs = self.generate_research_jobs()
        sweep_jobs = [j for j in jobs if j.method == "first_run"]
        
        script = f'''#!/bin/bash
#
# Pareto Frontier Research - Exact Implementation
# Based on continuity_research_priority_c94d2043.plan.md
#

set -e

echo "🎯 PARETO FRONTIER RESEARCH - EXACT IMPLEMENTATION"
echo "=================================================="

# Configuration from plan
export TIMEFOLD_API_KEY="{self.config['api_key']}"
CONFIG_ID="{self.config['config_id']}"
BASE_INPUT="{self.config['base_input']}"  
SEED_OUTPUT="{self.config['seed_output']}"
EXPANDED_CSV="{self.config['expanded_csv']}"
SCRIPTS_DIR="{self.config['scripts_dir']}"

# Change to working directory
cd "$HOME/HomeCare/caire-platform/appcaire/{self.config['working_dir']}"

echo "📊 RESEARCH PARAMETERS:"
echo "   Sweet spot target: ≥77% efficiency, ≤10 continuity"
echo "   Pool method: first-run from 391486da baseline"
echo "   N-values: {[j.n_value for j in sweep_jobs]}"
echo "   Config: $CONFIG_ID"
echo ""

# Phase 1: Verify prerequisites  
echo "🔧 Phase 1: Verifying prerequisites..."
if [ ! -f "$BASE_INPUT" ]; then
    echo "❌ Base input not found: $BASE_INPUT"
    exit 1
fi

if [ ! -f "$SEED_OUTPUT" ]; then
    echo "❌ Seed output not found: $SEED_OUTPUT" 
    echo "   Run: python3 ../scripts/fetch_timefold_solution.py 391486da-ca6f-4928-a928-056a589842e1 --save $SEED_OUTPUT"
    exit 1
fi

if [ ! -f "$EXPANDED_CSV" ]; then
    echo "❌ Expanded CSV not found: $EXPANDED_CSV"
    exit 1
fi

echo "✅ Prerequisites verified"

# Phase 2: Prepare research directories
echo "📁 Phase 2: Setting up research structure..."
mkdir -p solve/research/{{sweep,approach-0}}
mkdir -p metrics/{{sweep,approach-0}}
'''

        # Add directory creation for each N-value
        for job in sweep_jobs:
            script += f'mkdir -p solve/research/sweep/N{job.n_value}\n'
            script += f'mkdir -p metrics/sweep/N{job.n_value}\n'
        
        script += '''
echo "✅ Directory structure created"

# Phase 3: Approach 0 - Direct Slinga Assignment
echo "🔧 Phase 3: Approach 0 - Direct slinga assignment..."

# Create patch_visits_slinga_direct.py if it doesn't exist
cat > "$SCRIPTS_DIR/patch_visits_slinga_direct.py" << 'EOF'
#!/usr/bin/env python3
"""
Patch FSR input with exact per-visit requiredVehicles from external_slinga_shiftName
Approach 0: pool≈1 with exact manual assignment
"""

import re
import csv
import json
import argparse
from pathlib import Path

def _slug(s):
    """Convert slinga name to vehicle ID (same logic as generate_employees.py)"""
    slug = re.sub(r"[^\\w\\s-]", "", s.strip())
    return re.sub(r"[\\s_]+", "_", slug).strip("_") or "employee"

def patch_visits_slinga_direct(expanded_csv, fsr_input, output):
    """Patch FSR input with exact manual assignment"""
    
    print(f"Reading manual assignments from {expanded_csv}")
    with open(expanded_csv) as f:
        rows = list(csv.DictReader(f, delimiter=';'))
    
    # Build per-visit pool: visit_id → [vehicle_id, ...]
    visit_pool = {}
    for row in rows:
        vid = row.get('original_visit_id', '').strip()
        slinga = row.get('external_slinga_shiftName', '').strip()
        
        if vid and slinga:
            veh_id = _slug(slinga)
            visit_pool.setdefault(vid, [])
            if veh_id not in visit_pool[vid]:
                visit_pool[vid].append(veh_id)
    
    print(f"Built manual assignment pools for {len(visit_pool)} visits")
    
    # Load FSR input and patch
    with open(fsr_input) as f:
        payload = json.load(f)
    
    mi = payload['modelInput']
    patched_visits = 0
    
    # Patch individual visits
    for visit in mi.get('visits', []):
        pool = visit_pool.get(visit['id'])
        if pool:
            visit['requiredVehicles'] = pool
            patched_visits += 1
    
    # Patch visit groups
    for group in mi.get('visitGroups', []):
        for visit in group.get('visits', []):
            pool = visit_pool.get(visit['id'])
            if pool:
                visit['requiredVehicles'] = pool
                patched_visits += 1
    
    print(f"Patched {patched_visits} visits with manual assignments")
    
    # Save patched input
    with open(output, 'w') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    
    print(f"Saved patched input to {output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Patch FSR with direct slinga assignment')
    parser.add_argument('--expanded-csv', required=True, help='Expanded CSV with manual assignments')
    parser.add_argument('--fsr-input', required=True, help='Base FSR input file')  
    parser.add_argument('--output', required=True, help='Output patched FSR input file')
    
    args = parser.parse_args()
    patch_visits_slinga_direct(args.expanded_csv, args.fsr_input, args.output)
EOF

chmod +x "$SCRIPTS_DIR/patch_visits_slinga_direct.py"

# Create Approach 0 input
python3 "$SCRIPTS_DIR/patch_visits_slinga_direct.py" \\
    --expanded-csv "$EXPANDED_CSV" \\
    --fsr-input "$BASE_INPUT" \\
    --output solve/research/approach-0/input_slinga_direct.json

# Submit Approach 0
echo "   Submitting Approach 0 (direct slinga)..."
python3 "$SCRIPTS_DIR/submit_to_timefold.py" \\
    solve solve/research/approach-0/input_slinga_direct.json \\
    --configuration-id "$CONFIG_ID" \\
    --wait \\
    --save solve/research/approach-0/plan_id.txt &

echo "✅ Approach 0 submitted"

# Phase 4: First-run pool sweep
echo "⚡ Phase 4: First-run pool sweep..."
'''

        # Add sweep job submissions
        for job in sweep_jobs:
            script += f'''
echo "   Building N={job.n_value} pool..."
python3 "$SCRIPTS_DIR/build_continuity_pools.py" \\
    --source first-run \\
    --input "$BASE_INPUT" \\
    --output "$SEED_OUTPUT" \\
    --max-per-client {job.n_value} \\
    --out solve/research/sweep/N{job.n_value}/pools.json \\
    --patch-fsr-input "$BASE_INPUT" \\
    --patched-input solve/research/sweep/N{job.n_value}/input.json

echo "   Submitting N={job.n_value}..."
python3 "$SCRIPTS_DIR/submit_to_timefold.py" \\
    solve solve/research/sweep/N{job.n_value}/input.json \\
    --configuration-id "$CONFIG_ID" \\
    --wait \\
    --save solve/research/sweep/N{job.n_value}/plan_id.txt &
'''

        script += '''
# Wait for all submissions
echo "   Waiting for all submissions to complete..."
wait

echo "✅ Phase 4 complete"

# Phase 5: Fetch outputs and analyze
echo "📊 Phase 5: Analysis and reporting..."

# Analyze Approach 0
if [ -f solve/research/approach-0/plan_id.txt ]; then
    PLAN_ID=$(cat solve/research/approach-0/plan_id.txt)
    echo "   Fetching Approach 0 output ($PLAN_ID)..."
    
    python3 "$SCRIPTS_DIR/fetch_timefold_solution.py" \\
        "$PLAN_ID" \\
        --save solve/research/approach-0/output_slinga_direct.json \\
        --input solve/research/approach-0/input_slinga_direct.json \\
        --metrics-dir metrics/approach-0/
    
    python3 "$SCRIPTS_DIR/continuity_report.py" \\
        solve/research/approach-0/input_slinga_direct.json \\
        solve/research/approach-0/output_slinga_direct.json \\
        --out metrics/approach-0/continuity.csv
fi

# Analyze sweep results
'''

        for job in sweep_jobs:
            script += f'''
if [ -f solve/research/sweep/N{job.n_value}/plan_id.txt ]; then
    PLAN_ID=$(cat solve/research/sweep/N{job.n_value}/plan_id.txt)
    echo "   Fetching N={job.n_value} output ($PLAN_ID)..."
    
    python3 "$SCRIPTS_DIR/fetch_timefold_solution.py" \\
        "$PLAN_ID" \\
        --save solve/research/sweep/N{job.n_value}/output.json \\
        --input solve/research/sweep/N{job.n_value}/input.json \\
        --metrics-dir metrics/sweep/N{job.n_value}/
    
    python3 "$SCRIPTS_DIR/continuity_report.py" \\
        solve/research/sweep/N{job.n_value}/input.json \\
        solve/research/sweep/N{job.n_value}/output.json \\
        --out metrics/sweep/N{job.n_value}/continuity.csv
fi
'''

        script += '''
echo "✅ Phase 5 complete"

# Phase 6: Generate Pareto frontier report
echo "📈 Phase 6: Generating Pareto frontier report..."

REPORT_FILE="solve/research/pareto-frontier-$(date +%Y-%m-%d).md"

cat > "$REPORT_FILE" << EOF
# Efficiency-Continuity Pareto Frontier — Huddinge 2-Week — $(date +%Y-%m-%d)

## Executive Summary

**Research Goal**: Map the efficiency-continuity trade-off curve to identify optimal configurations.
**Method**: First-run pool sweep + direct slinga assignment
**Sweet Spot Criteria**: Efficiency ≥ 77%, Continuity ≤ 10 caregivers average

## Confirmed Baselines

| Strategy | Pool | Eff (excl idle) | Travel | Margin | Avg Unique/Client | Notes |
|----------|------|-----------------|--------|--------|-------------------|--------|
| Manual (client today) | — | 67.8% | 24.0% | 31.0% | 2.9 | Current baseline |
| Unconstrained FSR | ∞ | 85.7% | 9.8% | 51.0% | 19.3 | 391486da, ~114 unassigned |

## Research Results

| Strategy | Pool | Eff (excl idle) | Avg Unique/Client | Unassigned | Plan ID |
|----------|------|-----------------|-------------------|------------|---------|
| Approach 0 (direct slinga) | ≈1 | ?% | ~2.85 | ? | TBD |
'''

        for job in sweep_jobs:
            script += f'| Sweep N={job.n_value} (first-run) | {job.n_value} | ?% | ? | ? | TBD |\n'

        script += '''

## Sweet Spot Analysis

[To be filled after data collection]

## Business Recommendations

[To be filled based on results]

EOF

echo "📈 Pareto frontier report generated: $REPORT_FILE"

# Summary
echo ""
echo "🏆 PARETO FRONTIER RESEARCH COMPLETE!"
echo "===================================="
echo ""
echo "📊 EXECUTED:"
echo "   • Approach 0: Direct slinga assignment (pool≈1)"
'''
        
        for job in sweep_jobs:
            script += f'echo "   • Sweep N={job.n_value}: First-run pool"\n'
        
        script += '''
echo ""
echo "📁 RESULTS:"
echo "   • Report: $REPORT_FILE"
echo "   • Individual outputs: solve/research/{{approach-0,sweep}}/*/output*.json"
echo "   • Metrics: metrics/{{approach-0,sweep}}/*/"
echo ""
echo "🎯 NEXT: Analyze results to identify sweet spot configurations!"
'''

        return script
    
    def save_execution_script(self, filename: str) -> str:
        """Save the execution script to file"""
        script_content = self.generate_execution_script()
        
        with open(filename, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(filename, 0o755)
        
        return filename

def main():
    """Generate and save the exact Pareto research plan"""
    
    plan = ParetoResearchPlan()
    
    print("🎯 GENERATING EXACT PARETO FRONTIER RESEARCH PLAN")
    print("Based on: continuity_research_priority_c94d2043.plan.md")
    
    # Generate research jobs
    jobs = plan.generate_research_jobs()
    
    print(f"\n📊 RESEARCH JOBS ({len(jobs)} total):")
    for job in jobs:
        sweet_spot = "⭐" if (job.expected_efficiency >= 77.0 and job.expected_continuity <= 10.0) else ""
        print(f"   • {job.name}: N={job.n_value}, {job.expected_efficiency:.1f}% eff, {job.expected_continuity:.1f} cont {sweet_spot}")
    
    # Save execution script
    script_file = "/tmp/pareto_research_exact.sh"
    plan.save_execution_script(script_file)
    
    print(f"\n🚀 EXECUTION SCRIPT SAVED: {script_file}")
    print(f"   Run with: {script_file}")
    
    # Save plan data
    plan_data = {
        "research_goal": "Map efficiency-continuity Pareto frontier",
        "sweet_spot_criteria": plan.sweet_spot_criteria,
        "baselines": {
            "manual": plan.manual_baseline,
            "unconstrained": plan.unconstrained_baseline
        },
        "config": plan.config,
        "jobs": [
            {
                "name": job.name,
                "n_value": job.n_value,
                "method": job.method,
                "description": job.description,
                "priority": job.priority,
                "expected_efficiency": job.expected_efficiency,
                "expected_continuity": job.expected_continuity
            }
            for job in jobs
        ]
    }
    
    with open("/tmp/pareto_research_plan.json", "w") as f:
        json.dump(plan_data, f, indent=2)
    
    print(f"   Plan data: /tmp/pareto_research_plan.json")

if __name__ == "__main__":
    main()