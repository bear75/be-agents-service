#!/usr/bin/env python3
"""
Timefold Research Orchestrator - Multi-Agent Coordination System
Orchestrates hundreds of parallel Timefold runs with adaptive learning
"""

import json
import asyncio
import subprocess
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted" 
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ANALYZING = "analyzing"

@dataclass
class TimefoldJob:
    """Represents a single Timefold optimization job"""
    job_id: str
    strategy_name: str
    n_value: int
    input_file: str
    output_file: str
    status: JobStatus = JobStatus.PENDING
    route_plan_id: str = None
    efficiency: float = None
    continuity: float = None
    unassigned_count: int = None
    execution_time: float = None
    error_message: str = None
    parent_job: str = None
    iteration: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class TimefoldOrchestrator:
    """Orchestrates massive parallel Timefold research program"""
    
    def __init__(self, api_key: str, max_parallel_jobs: int = 8, results_dir: str = "/tmp/timefold_research"):
        self.api_key = api_key
        self.max_parallel_jobs = max_parallel_jobs
        self.results_dir = results_dir
        self.jobs = {}
        self.completed_jobs = {}
        self.research_tree = {}
        self.performance_patterns = {}
        
        # Create results directory
        os.makedirs(results_dir, exist_ok=True)
        os.makedirs(f"{results_dir}/inputs", exist_ok=True)
        os.makedirs(f"{results_dir}/outputs", exist_ok=True)
        os.makedirs(f"{results_dir}/analysis", exist_ok=True)
        
        logger.info(f"🚀 Initialized Timefold Research Orchestrator")
        logger.info(f"📁 Results directory: {results_dir}")
        logger.info(f"⚡ Max parallel jobs: {max_parallel_jobs}")
    
    def load_strategy_matrix(self, matrix_file: str) -> List[Dict[str, Any]]:
        """Load strategy configurations from file"""
        try:
            with open(matrix_file, 'r') as f:
                data = json.load(f)
            
            strategies = data.get('strategies', [])
            logger.info(f"📋 Loaded {len(strategies)} strategies from {matrix_file}")
            return strategies
            
        except Exception as e:
            logger.error(f"❌ Failed to load strategies: {e}")
            return []
    
    def create_job_queue(self, strategies: List[Dict[str, Any]]) -> List[TimefoldJob]:
        """Create prioritized job queue from strategies"""
        job_queue = []
        
        # Sort strategies by priority (1 = highest)
        sorted_strategies = sorted(strategies, key=lambda s: s.get('priority', 5))
        
        for i, strategy in enumerate(sorted_strategies):
            job_id = f"tf_{i+1:03d}_{strategy['name']}"
            
            job = TimefoldJob(
                job_id=job_id,
                strategy_name=strategy['name'],
                n_value=strategy['n_value'],
                input_file=f"{self.results_dir}/inputs/{job_id}_input.json",
                output_file=f"{self.results_dir}/outputs/{job_id}_output.json",
                iteration=strategy.get('iteration', 1)
            )
            
            job_queue.append(job)
            self.jobs[job_id] = job
        
        logger.info(f"📊 Created job queue with {len(job_queue)} jobs")
        return job_queue
    
    def prepare_input_files(self, job_queue: List[TimefoldJob]) -> None:
        """Prepare FSR input files for all jobs"""
        logger.info("🔧 Preparing input files...")
        
        # Load base Huddinge input
        base_input_path = "/tmp/huddinge_base_input.json"
        if not os.path.exists(base_input_path):
            logger.error(f"❌ Base input file not found: {base_input_path}")
            return
        
        with open(base_input_path, 'r') as f:
            base_input = json.load(f)
        
        # Load continuity pools
        pools = {}
        for n in [5, 10, 15]:
            pool_file = f"/tmp/huddinge_pools_n{n}.json"
            if os.path.exists(pool_file):
                with open(pool_file, 'r') as f:
                    pools[n] = json.load(f)
        
        for job in job_queue:
            try:
                # Create strategy-specific input
                strategy_input = self._create_strategy_input(
                    base_input=base_input,
                    strategy_name=job.strategy_name,
                    n_value=job.n_value,
                    pools=pools
                )
                
                # Save input file
                with open(job.input_file, 'w') as f:
                    json.dump(strategy_input, f)
                
                logger.debug(f"✅ Created input for {job.job_id}")
                
            except Exception as e:
                logger.error(f"❌ Failed to create input for {job.job_id}: {e}")
                job.status = JobStatus.FAILED
                job.error_message = str(e)
    
    def execute_parallel_research(self, job_queue: List[TimefoldJob]) -> None:
        """Execute jobs in parallel with adaptive scheduling"""
        logger.info(f"⚡ Starting parallel execution of {len(job_queue)} jobs")
        
        # Filter out failed jobs
        executable_jobs = [job for job in job_queue if job.status != JobStatus.FAILED]
        
        with ThreadPoolExecutor(max_workers=self.max_parallel_jobs) as executor:
            # Submit initial batch
            future_to_job = {}
            active_jobs = 0
            job_index = 0
            
            while job_index < len(executable_jobs) or active_jobs > 0:
                # Submit new jobs up to limit
                while active_jobs < self.max_parallel_jobs and job_index < len(executable_jobs):
                    job = executable_jobs[job_index]
                    
                    # Submit job
                    future = executor.submit(self._execute_timefold_job, job)
                    future_to_job[future] = job
                    
                    job.status = JobStatus.SUBMITTED
                    active_jobs += 1
                    job_index += 1
                    
                    logger.info(f"🚀 Submitted {job.job_id} ({active_jobs}/{self.max_parallel_jobs} active)")
                
                # Check for completed jobs
                if future_to_job:
                    completed_futures = []
                    
                    for future in as_completed(future_to_job, timeout=60):
                        completed_futures.append(future)
                        job = future_to_job[future]
                        
                        try:
                            result = future.result()
                            job.status = JobStatus.COMPLETED
                            self._process_job_result(job, result)
                            
                            logger.info(f"✅ Completed {job.job_id}: {job.efficiency:.1f}% eff, {job.continuity:.1f} cont")
                            
                            # Check if this result suggests new strategies
                            self._analyze_result_for_adaptations(job)
                            
                        except Exception as e:
                            job.status = JobStatus.FAILED
                            job.error_message = str(e)
                            logger.error(f"❌ Failed {job.job_id}: {e}")
                        
                        finally:
                            active_jobs -= 1
                            self.completed_jobs[job.job_id] = job
                    
                    # Clean up completed futures
                    for future in completed_futures:
                        del future_to_job[future]
                
                # Brief pause to avoid busy waiting
                time.sleep(1)
        
        logger.info("🎯 Parallel execution completed")
        self._generate_research_summary()
    
    def _create_strategy_input(self, base_input: Dict, strategy_name: str, n_value: int, pools: Dict) -> Dict:
        """Create FSR input for specific strategy"""
        
        import copy
        strategy_input = copy.deepcopy(base_input)
        
        # Apply strategy-specific modifications
        if 'manual' in strategy_name.lower() and n_value in pools:
            # Apply manual continuity pools
            visits = strategy_input['modelInput']['visits']
            for visit in visits:
                visit_name = visit.get('name', '')
                if '_' in visit_name and ' - ' in visit_name:
                    client_part = visit_name.split(' - ')[0]
                    if '_' in client_part:
                        client_id = client_part.split('_')[0]
                        if client_id in pools[n_value]:
                            visit['requiredVehicles'] = pools[n_value][client_id][:n_value]
        
        elif 'unconstrained' in strategy_name.lower():
            # No constraints - baseline comparison
            pass
        
        elif 'soft' in strategy_name.lower():
            # Apply soft preferences instead of hard constraints
            visits = strategy_input['modelInput']['visits']
            for visit in visits:
                if 'requiredVehicles' in visit:
                    visit['preferredVehicles'] = visit.pop('requiredVehicles')
        
        # Add strategy metadata
        if 'config' not in strategy_input:
            strategy_input['config'] = {}
        
        strategy_input['config']['strategy_name'] = strategy_name
        strategy_input['config']['n_value'] = n_value
        
        return strategy_input
    
    def _execute_timefold_job(self, job: TimefoldJob) -> Dict[str, Any]:
        """Execute single Timefold job"""
        job.status = JobStatus.RUNNING
        start_time = time.time()
        
        try:
            # Submit to Timefold API
            submit_command = [
                "python3", 
                "/Users/be-agent-service/HomeCare/appcaire/docs_2.0/recurring-visits/scripts/submit_to_timefold.py",
                "solve",
                job.input_file,
                "--wait",
                "--save", job.output_file
            ]
            
            env = os.environ.copy()
            env['TIMEFOLD_API_KEY'] = self.api_key
            
            result = subprocess.run(
                submit_command,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minute timeout
                env=env
            )
            
            job.execution_time = time.time() - start_time
            
            if result.returncode == 0:
                # Parse output for route plan ID
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if 'route-plan' in line or 'id:' in line.lower():
                        # Extract route plan ID
                        parts = line.split()
                        for part in parts:
                            if len(part) > 20 and '-' in part:
                                job.route_plan_id = part.strip()
                                break
                
                return {"success": True, "output_file": job.output_file}
            else:
                raise Exception(f"Timefold submission failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception("Job timed out after 30 minutes")
        except Exception as e:
            job.execution_time = time.time() - start_time
            raise e
    
    def _process_job_result(self, job: TimefoldJob, result: Dict[str, Any]) -> None:
        """Analyze job result and extract metrics"""
        try:
            if os.path.exists(job.output_file):
                # Run continuity analysis
                continuity_file = f"{self.results_dir}/analysis/{job.job_id}_continuity.csv"
                
                subprocess.run([
                    "python3",
                    "/Users/be-agent-service/HomeCare/appcaire/docs_2.0/recurring-visits/scripts/continuity_report.py",
                    "--input", job.input_file,
                    "--output", job.output_file,
                    "--report", continuity_file
                ], check=True, capture_output=True)
                
                # Run efficiency analysis
                metrics_result = subprocess.run([
                    "python3",
                    "/Users/be-agent-service/HomeCare/appcaire/docs_2.0/recurring-visits/scripts/metrics.py",
                    job.output_file,
                    "--exclude-inactive"
                ], capture_output=True, text=True, check=True)
                
                # Parse metrics from output
                job.efficiency, job.continuity, job.unassigned_count = self._parse_metrics(
                    metrics_result.stdout, continuity_file
                )
                
        except Exception as e:
            logger.error(f"❌ Failed to analyze {job.job_id}: {e}")
            job.error_message = f"Analysis failed: {e}"
    
    def _parse_metrics(self, metrics_output: str, continuity_file: str) -> Tuple[float, float, int]:
        """Extract efficiency, continuity, and unassigned metrics"""
        
        efficiency = 0.0
        continuity = 0.0
        unassigned = 0
        
        try:
            # Parse efficiency from metrics output
            for line in metrics_output.split('\n'):
                if 'Travel efficiency' in line:
                    # Extract percentage
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
            
            # Parse continuity from CSV
            if os.path.exists(continuity_file):
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
        
        except Exception as e:
            logger.error(f"❌ Failed to parse metrics: {e}")
        
        return efficiency, continuity, unassigned
    
    def _analyze_result_for_adaptations(self, job: TimefoldJob) -> None:
        """Analyze job result to identify potential new strategies"""
        
        # Check if result hits target criteria
        if (job.efficiency and job.continuity and 
            74 <= job.efficiency <= 78 and 8 <= job.continuity <= 12):
            
            logger.info(f"🎯 TARGET HIT! {job.job_id} achieved {job.efficiency:.1f}% eff, {job.continuity:.1f} cont")
            
            # Generate refinement strategies around this successful configuration
            self._generate_refinement_jobs(job)
    
    def _generate_refinement_jobs(self, successful_job: TimefoldJob) -> None:
        """Generate new jobs based on successful result"""
        
        refinements = []
        base_n = successful_job.n_value
        
        # Generate N-value refinements
        for delta in [-1, +1]:
            new_n = max(1, base_n + delta)
            if new_n != base_n:
                job_id = f"refine_{successful_job.job_id}_n{new_n}"
                
                refinement_job = TimefoldJob(
                    job_id=job_id,
                    strategy_name=f"{successful_job.strategy_name}_refined_n{new_n}",
                    n_value=new_n,
                    input_file=f"{self.results_dir}/inputs/{job_id}_input.json",
                    output_file=f"{self.results_dir}/outputs/{job_id}_output.json",
                    parent_job=successful_job.job_id,
                    iteration=successful_job.iteration + 1
                )
                
                refinements.append(refinement_job)
        
        if refinements:
            logger.info(f"🔄 Generated {len(refinements)} refinement jobs from {successful_job.job_id}")
            # Add to job queue for next iteration
            # (Implementation depends on how you want to handle dynamic job addition)
    
    def _generate_research_summary(self) -> None:
        """Generate comprehensive research summary"""
        
        summary = {
            "total_jobs": len(self.completed_jobs),
            "successful_jobs": len([j for j in self.completed_jobs.values() if j.status == JobStatus.COMPLETED]),
            "failed_jobs": len([j for j in self.completed_jobs.values() if j.status == JobStatus.FAILED]),
            "results": []
        }
        
        # Analyze all completed jobs
        for job in self.completed_jobs.values():
            if job.status == JobStatus.COMPLETED and job.efficiency:
                summary["results"].append({
                    "job_id": job.job_id,
                    "strategy": job.strategy_name,
                    "n_value": job.n_value,
                    "efficiency": job.efficiency,
                    "continuity": job.continuity,
                    "unassigned": job.unassigned_count,
                    "execution_time": job.execution_time
                })
        
        # Sort results by efficiency
        summary["results"] = sorted(summary["results"], key=lambda x: x["efficiency"], reverse=True)
        
        # Find optimal configurations
        targets_hit = [
            r for r in summary["results"] 
            if 74 <= r["efficiency"] <= 78 and 8 <= r["continuity"] <= 12
        ]
        
        summary["targets_achieved"] = len(targets_hit)
        summary["optimal_configurations"] = targets_hit[:5]  # Top 5
        
        # Save summary
        summary_file = f"{self.results_dir}/research_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"📊 Research Summary:")
        logger.info(f"   Total jobs: {summary['total_jobs']}")
        logger.info(f"   Successful: {summary['successful_jobs']}")
        logger.info(f"   Failed: {summary['failed_jobs']}")
        logger.info(f"   Targets hit: {summary['targets_achieved']}")
        logger.info(f"💾 Detailed summary: {summary_file}")

def main():
    """Main orchestration entry point"""
    
    # Configuration
    api_key = "tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8"
    strategy_matrix_file = "/tmp/timefold_strategy_matrix.json"
    
    # Initialize orchestrator
    orchestrator = TimefoldOrchestrator(
        api_key=api_key,
        max_parallel_jobs=6,  # Conservative for initial run
        results_dir="/tmp/timefold_research"
    )
    
    # Load strategies
    strategies = orchestrator.load_strategy_matrix(strategy_matrix_file)
    if not strategies:
        logger.error("❌ No strategies loaded, exiting")
        return
    
    # Create job queue
    job_queue = orchestrator.create_job_queue(strategies)
    
    # Prepare input files
    orchestrator.prepare_input_files(job_queue)
    
    # Execute research program
    orchestrator.execute_parallel_research(job_queue)
    
    logger.info("🏆 Multi-agent Timefold research program completed!")

if __name__ == "__main__":
    main()