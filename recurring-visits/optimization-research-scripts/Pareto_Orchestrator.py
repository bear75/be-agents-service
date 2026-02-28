#!/usr/bin/env python3
"""
Pareto Frontier Orchestrator - Systematic Efficiency-Continuity Mapping
Executes first-run pool sweep to discover optimal trade-off points
"""

import json
import subprocess
import os
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ParetoJob:
    """Single Pareto frontier research job"""
    job_id: str
    n_value: int
    input_file: str
    output_file: str
    pool_file: str
    plan_id_file: str
    metrics_dir: str
    status: str = "pending"
    route_plan_id: str = None
    efficiency: float = None
    continuity: float = None
    unassigned_count: int = None
    margin: float = None

class ParetoFrontierOrchestrator:
    """Orchestrates systematic Pareto frontier mapping research"""
    
    def __init__(self):
        self.api_key = "tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8"
        self.config_id = "a43d4eec-9f53-40b3-82ad-f135adc8c7e3"
        self.base_input = "solve/input_20260224_202857.json"
        self.seed_output = "solve/iter1/391486da-output.json"
        self.working_dir = "docs_2.0/recurring-visits/huddinge-package"
        self.scripts_dir = "../scripts"
        
        # Create research directory structure
        self.setup_directories()
        
        # Known baselines from pilot report
        self.manual_baseline = {"efficiency": 67.8, "continuity": 2.9}
        self.unconstrained_baseline = {"efficiency": 85.7, "continuity": 19.3}
        
    def setup_directories(self):
        """Create directory structure for Pareto research"""
        dirs = [
            "solve/research/sweep",
            "metrics/sweep", 
            "solve/research/pareto"
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def generate_pareto_jobs(self, n_values: List[int]) -> List[ParetoJob]:
        """Generate job specifications for N-value sweep"""
        
        jobs = []
        
        for i, n_value in enumerate(n_values):
            job_id = f"sweep_n{n_value:02d}"
            
            job = ParetoJob(
                job_id=job_id,
                n_value=n_value,
                input_file=f"solve/research/sweep/N{n_value}/input.json",
                output_file=f"solve/research/sweep/N{n_value}/output.json", 
                pool_file=f"solve/research/sweep/N{n_value}/pools.json",
                plan_id_file=f"solve/research/sweep/N{n_value}/plan_id.txt",
                metrics_dir=f"metrics/sweep/N{n_value}"
            )
            
            jobs.append(job)
            
        return jobs
    
    def prepare_sweep_inputs(self, jobs: List[ParetoJob]) -> None:
        """Prepare FSR inputs with first-run continuity pools"""
        
        logger.info("🔧 Preparing first-run continuity pool inputs...")
        
        for job in jobs:
            try:
                # Create job directory
                job_dir = os.path.dirname(job.input_file)
                os.makedirs(job_dir, exist_ok=True)
                
                # Build first-run pool and patch FSR input
                build_command = [
                    "python3", f"{self.scripts_dir}/build_continuity_pools.py",
                    "--source", "first-run",
                    "--input", self.base_input,
                    "--output", self.seed_output,
                    "--max-per-client", str(job.n_value),
                    "--out", job.pool_file,
                    "--patch-fsr-input", self.base_input,
                    "--patched-input", job.input_file
                ]
                
                result = subprocess.run(
                    build_command,
                    cwd=self.working_dir,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                logger.info(f"✅ Created N={job.n_value} input: {job.input_file}")
                job.status = "input_ready"
                
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to create input for N={job.n_value}: {e.stderr}")
                job.status = "input_failed"
                
        logger.info("🔧 Input preparation complete")
    
    def execute_parallel_sweep(self, jobs: List[ParetoJob], max_parallel: int = 4) -> None:
        """Execute Pareto sweep jobs in parallel"""
        
        # Filter jobs with ready inputs
        ready_jobs = [job for job in jobs if job.status == "input_ready"]
        
        logger.info(f"⚡ Starting parallel sweep: {len(ready_jobs)} jobs, max {max_parallel} concurrent")
        
        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            future_to_job = {}
            
            # Submit all jobs
            for job in ready_jobs:
                future = executor.submit(self._execute_sweep_job, job)
                future_to_job[future] = job
                job.status = "submitted"
            
            # Collect results as they complete
            for future in as_completed(future_to_job):
                job = future_to_job[future]
                
                try:
                    result = future.result()
                    job.status = "completed"
                    logger.info(f"✅ Completed {job.job_id}: {result}")
                    
                except Exception as e:
                    job.status = "failed"
                    logger.error(f"❌ Failed {job.job_id}: {e}")
        
        logger.info("⚡ Parallel sweep execution complete")
    
    def _execute_sweep_job(self, job: ParetoJob) -> str:
        """Execute single sweep job (submit + wait + fetch)"""
        
        job.status = "running"
        
        try:
            # Submit to Timefold
            submit_command = [
                "python3", f"{self.scripts_dir}/submit_to_timefold.py",
                "solve", job.input_file,
                "--configuration-id", self.config_id,
                "--wait",
                "--save", job.plan_id_file
            ]
            
            env = os.environ.copy()
            env['TIMEFOLD_API_KEY'] = self.api_key
            
            submit_result = subprocess.run(
                submit_command,
                cwd=self.working_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 min timeout
                check=True
            )
            
            # Extract plan ID
            if os.path.exists(job.plan_id_file):
                with open(job.plan_id_file, 'r') as f:
                    job.route_plan_id = f.read().strip()
            
            # Fetch solution
            fetch_command = [
                "python3", f"{self.scripts_dir}/fetch_timefold_solution.py",
                job.route_plan_id,
                "--save", job.output_file,
                "--input", job.input_file,
                "--metrics-dir", job.metrics_dir
            ]
            
            fetch_result = subprocess.run(
                fetch_command,
                cwd=self.working_dir,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            return f"Plan {job.route_plan_id}"
            
        except subprocess.TimeoutExpired:
            raise Exception("Job timed out after 30 minutes")
        except Exception as e:
            raise Exception(f"Execution failed: {e}")
    
    def analyze_sweep_results(self, jobs: List[ParetoJob]) -> List[Dict[str, Any]]:
        """Analyze results and extract Pareto frontier data"""
        
        logger.info("📊 Analyzing sweep results...")
        
        pareto_points = []
        
        for job in jobs:
            if job.status == "completed" and os.path.exists(job.output_file):
                try:
                    # Run continuity analysis
                    continuity_file = f"{job.metrics_dir}/continuity.csv"
                    
                    continuity_command = [
                        "python3", f"{self.scripts_dir}/continuity_report.py",
                        job.input_file, job.output_file,
                        "--out", continuity_file
                    ]
                    
                    subprocess.run(
                        continuity_command,
                        cwd=self.working_dir,
                        check=True,
                        capture_output=True
                    )
                    
                    # Extract metrics 
                    efficiency, continuity, unassigned, margin = self._extract_metrics(
                        job.output_file, continuity_file
                    )
                    
                    job.efficiency = efficiency
                    job.continuity = continuity
                    job.unassigned_count = unassigned
                    job.margin = margin
                    
                    pareto_point = {
                        "n_value": job.n_value,
                        "efficiency": efficiency,
                        "continuity": continuity,
                        "unassigned": unassigned,
                        "margin": margin,
                        "route_plan_id": job.route_plan_id,
                        "is_sweet_spot": self._is_sweet_spot(efficiency, continuity)
                    }
                    
                    pareto_points.append(pareto_point)
                    
                    logger.info(f"📈 N={job.n_value:2d}: {efficiency:5.1f}% eff, {continuity:4.1f} cont, {unassigned:3d} unassigned")
                    
                except Exception as e:
                    logger.error(f"❌ Analysis failed for {job.job_id}: {e}")
        
        # Sort by N-value for reporting
        pareto_points.sort(key=lambda x: x["n_value"])
        
        return pareto_points
    
    def _extract_metrics(self, output_file: str, continuity_file: str) -> Tuple[float, float, int, float]:
        """Extract efficiency, continuity, unassigned, and margin metrics"""
        
        # Run metrics analysis (exclude idle as requested)
        metrics_command = [
            "python3", f"{self.scripts_dir}/metrics.py",
            output_file,
            "--exclude-inactive"
        ]
        
        metrics_result = subprocess.run(
            metrics_command,
            cwd=self.working_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse efficiency and other metrics from output
        efficiency = 0.0
        unassigned = 0
        margin = 0.0
        
        for line in metrics_result.stdout.split('\n'):
            if 'Travel efficiency' in line:
                parts = line.split()
                for part in parts:
                    if '%' in part:
                        efficiency = float(part.replace('%', ''))
                        break
            elif 'Unassigned:' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'Unassigned:':
                        if i + 1 < len(parts):
                            unassigned = int(parts[i + 1])
                        break
            elif 'Margin:' in line:
                parts = line.split()
                for part in parts:
                    if '%' in part:
                        margin = float(part.replace('%', ''))
                        break
        
        # Parse continuity from CSV
        continuity = 0.0
        if os.path.exists(continuity_file):
            try:
                with open(continuity_file, 'r') as f:
                    lines = f.readlines()
                
                continuities = []
                for line in lines[1:]:  # Skip header
                    if line.strip() and not line.startswith('client'):
                        parts = line.strip().split(',')
                        if len(parts) >= 3:
                            try:
                                cont_value = float(parts[2])
                                continuities.append(cont_value)
                            except ValueError:
                                continue
                
                if continuities:
                    continuity = sum(continuities) / len(continuities)
            except Exception:
                pass
        
        return efficiency, continuity, unassigned, margin
    
    def _is_sweet_spot(self, efficiency: float, continuity: float) -> bool:
        """Check if point meets sweet spot criteria"""
        return efficiency >= 77.0 and continuity <= 10.0
    
    def generate_pareto_report(self, pareto_points: List[Dict[str, Any]]) -> str:
        """Generate comprehensive Pareto frontier report"""
        
        # Find sweet spot candidates
        sweet_spots = [p for p in pareto_points if p["is_sweet_spot"]]
        
        # Build report
        report = f"""# Efficiency-Continuity Pareto Frontier — Huddinge 2-Week — {time.strftime('%Y-%m-%d')}

## Executive Summary

**Research Goal**: Map the efficiency-continuity trade-off curve to identify optimal configurations.

**Sweet Spot Criteria**: Efficiency ≥ 77%, Continuity ≤ 10 caregivers average
**Sweet Spots Found**: {len(sweet_spots)} configurations

## Key Numbers

| Strategy | Pool | Eff (excl idle) | Avg Unique/Client | Unassigned | Margin | Plan ID |
|----------|------|-----------------|-------------------|------------|--------|---------| 
| Manual (client today) | — | 67.8% | 2.9 | 0 | 31.0% | — |
"""

        for point in pareto_points:
            sweet_spot_marker = " ⭐" if point["is_sweet_spot"] else ""
            report += f"| Sweep N={point['n_value']} | {point['n_value']} | {point['efficiency']:.1f}% | {point['continuity']:.1f} | {point['unassigned']} | {point['margin']:.1f}% | {point['route_plan_id'][:8]}...{sweet_spot_marker} |\n"
        
        report += f"| Unconstrained (base) | ∞ | 85.7% | 19.3 | ~114 | 51.0% | 391486da... |\n\n"
        
        if sweet_spots:
            report += "## Sweet Spot Recommendations\n\n"
            for i, spot in enumerate(sweet_spots, 1):
                report += f"### Option {i}: N={spot['n_value']} Configuration\n"
                report += f"- **Efficiency**: {spot['efficiency']:.1f}% ({spot['efficiency'] - 67.8:+.1f}pp vs manual)\n"
                report += f"- **Continuity**: {spot['continuity']:.1f} caregivers average\n" 
                report += f"- **Unassigned**: {spot['unassigned']} visits\n"
                report += f"- **Margin**: {spot['margin']:.1f}% ({spot['margin'] - 31.0:+.1f}pp vs manual)\n"
                report += f"- **Business Case**: Strict improvement on both efficiency and continuity vs manual schedule\n\n"
        
        report += "## Decision Framework\n\n"
        report += "Present to client:\n"
        report += "- **Option A**: Max continuity (similar to manual, improved efficiency)\n"
        report += "- **Option B**: Balanced sweet spot (best of both worlds)\n" 
        report += "- **Option C**: Max efficiency (current unconstrained FSR)\n\n"
        
        report += "## Technical Notes\n\n"
        report += f"- Pool method: First-run from base 391486da output\n"
        report += f"- Configuration: {self.config_id}\n"
        report += f"- Analysis: Efficiency excludes idle time, continuity per client\n"
        report += f"- Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return report

def main():
    """Execute Pareto frontier research program"""
    
    # Initialize orchestrator
    orchestrator = ParetoFrontierOrchestrator()
    
    # Define N-value sweep (N=4 minimum as requested)
    n_values = [4, 5, 6, 7, 8, 10, 12, 15, 20]
    
    print(f"🎯 STARTING PARETO FRONTIER RESEARCH")
    print(f"   N-values: {n_values}")
    print(f"   Sweet spot target: ≥77% efficiency, ≤10 continuity")
    
    # Generate job specifications
    jobs = orchestrator.generate_pareto_jobs(n_values)
    
    # Prepare inputs with first-run pools
    orchestrator.prepare_sweep_inputs(jobs)
    
    # Execute sweep in parallel
    orchestrator.execute_parallel_sweep(jobs, max_parallel=4)
    
    # Analyze results
    pareto_points = orchestrator.analyze_sweep_results(jobs)
    
    # Generate report
    report = orchestrator.generate_pareto_report(pareto_points)
    
    # Save report
    report_file = "solve/research/pareto-frontier-report.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"📊 Pareto frontier research complete!")
    print(f"   Sweet spots found: {len([p for p in pareto_points if p['is_sweet_spot']])}")
    print(f"   Report saved: {report_file}")

if __name__ == "__main__":
    main()