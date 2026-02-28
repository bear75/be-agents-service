#!/usr/bin/env python3
"""
Enhanced Optimization Campaign Controller
Hypothesis-driven iteration with automatic job launching capability
Goal: Reach 70-75% efficiency, ≤15 continuity, <36 unassigned visits through systematic testing
"""

import json
import time
import subprocess
import requests
from pathlib import Path
from datetime import datetime, timedelta
import os

TIMEFOLD_BASE = "https://app.timefold.ai/api/models/field-service-routing/v1/route-plans"
API_KEY = "tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8"

TARGET_EFFICIENCY = 70.0
TARGET_CONTINUITY_FAILURES = 8  # Max clients failing ≤15 caregiver target (10% of 81)
TARGET_UNASSIGNED = 36

class HypothesisDrivenController:
    def __init__(self):
        self.current_jobs = {
            "strategic": "b69e582b-9321-4cfe-be40-92bc27287b5e",
            "conservative": "48b04930-53ef-4b69-b34b-7235e97879cd"
        }
        self.iteration_count = 0
        self.hypothesis_results = {}
        self.successful_approaches = []
        self.failed_approaches = []
        
    def log(self, message: str):
        """Log with timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def check_job_status(self, job_id: str) -> dict:
        """Check Timefold job status with error handling"""
        url = f"{TIMEFOLD_BASE}/{job_id}"
        headers = {"Accept": "application/json", "X-API-KEY": API_KEY}
        
        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                data = r.json()
                return {
                    'id': job_id,
                    'status': data.get('status', 'UNKNOWN'),
                    'score': data.get('score'),
                    'metadata': data.get('metadata', {}),
                    'completed': data.get('status') == 'COMPLETED',
                    'error': None
                }
            else:
                return {'id': job_id, 'status': 'API_ERROR', 'completed': False, 'error': f"HTTP {r.status_code}"}
        except Exception as e:
            return {'id': job_id, 'status': 'CONNECTION_ERROR', 'completed': False, 'error': str(e)}
    
    def analyze_solution_detailed(self, job_id: str) -> dict:
        """Get comprehensive solution analysis"""
        self.log(f"📊 Analyzing solution {job_id}...")
        
        # Fetch solution if not cached
        solution_file = f"solution_{job_id}.json"
        if not Path(solution_file).exists():
            result = subprocess.run([
                "python3", "fetch_timefold_solution.py", job_id,
                "--save", solution_file
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self.log(f"❌ Failed to fetch solution: {result.stderr}")
                return {}
        
        # Run REFINED analysis (remove empty vehicles + exclude idle time after last visit)
        result = subprocess.run([
            "python3", "refined_efficiency_analysis.py", solution_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError as e:
                self.log(f"❌ Analysis output parse error: {e}")
                return {}
        else:
            self.log(f"❌ Analysis failed: {result.stderr}")
            return {}
    
    def test_hypothesis(self, name: str, metrics: dict) -> tuple[bool, str, dict]:
        """Test a specific hypothesis against results"""
        
        if not metrics:
            return False, f"No metrics available for {name}", {}
            
        efficiency = metrics.get('refined_efficiency_percentage', 0)
        continuity_failures = metrics.get('continuity_failure_count', 999)
        unassigned = metrics.get('unassigned_visits', 999)
        empty_ratio = metrics.get('empty_vehicle_ratio', 1.0)
        
        hypothesis_tests = {
            "strategic_solves_unassigned": {
                "test": unassigned <= TARGET_UNASSIGNED,
                "condition": "unassigned <= 36",
                "actual": unassigned
            },
            "strategic_hurts_efficiency": {
                "test": efficiency < TARGET_EFFICIENCY and empty_ratio > 0.3,
                "condition": "efficiency < 70% AND empty_ratio > 30%",
                "actual": f"{efficiency:.1f}% efficiency, {empty_ratio:.1%} empty"
            },
            "conservative_preserves_efficiency": {
                "test": efficiency >= TARGET_EFFICIENCY - 5 and empty_ratio <= 0.2,  # Allow 5% tolerance
                "condition": "efficiency >= 65% AND empty_ratio <= 20%",
                "actual": f"{efficiency:.1f}% efficiency, {empty_ratio:.1%} empty"
            },
            "conservative_fails_unassigned": {
                "test": unassigned > TARGET_UNASSIGNED,
                "condition": "unassigned > 36",
                "actual": unassigned
            },
            "meets_all_targets": {
                "test": (efficiency >= TARGET_EFFICIENCY and 
                        continuity_failures <= TARGET_CONTINUITY_FAILURES and 
                        unassigned <= TARGET_UNASSIGNED),
                "condition": f"efficiency >= {TARGET_EFFICIENCY}% AND continuity_failures <= {TARGET_CONTINUITY_FAILURES} AND unassigned <= {TARGET_UNASSIGNED}",
                "actual": f"{efficiency:.1f}% eff, {continuity_failures} cont fails, {unassigned} unassigned"
            }
        }
        
        if name in hypothesis_tests:
            test = hypothesis_tests[name]
            passed = test["test"]
            details = {
                "condition": test["condition"],
                "actual": test["actual"],
                "passed": passed
            }
            result_msg = f"{'✅ CONFIRMED' if passed else '❌ REJECTED'}: {test['condition']} → {test['actual']}"
            return passed, result_msg, details
        else:
            return False, f"Unknown hypothesis: {name}", {}
    
    def design_next_optimization(self, strategic_metrics: dict, conservative_metrics: dict) -> dict:
        """Design next optimization based on hypothesis testing results"""
        
        self.log("🧠 Analyzing hypothesis results to design next optimization...")
        
        # Test key hypotheses
        strategic_solves_unassigned, _, _ = self.test_hypothesis("strategic_solves_unassigned", strategic_metrics)
        strategic_hurts_efficiency, _, _ = self.test_hypothesis("strategic_hurts_efficiency", strategic_metrics)
        conservative_preserves_efficiency, _, _ = self.test_hypothesis("conservative_preserves_efficiency", conservative_metrics)
        conservative_fails_unassigned, _, _ = self.test_hypothesis("conservative_fails_unassigned", conservative_metrics)
        
        strategic_meets_all, _, _ = self.test_hypothesis("meets_all_targets", strategic_metrics)
        conservative_meets_all, _, _ = self.test_hypothesis("meets_all_targets", conservative_metrics)
        
        # Decision logic based on hypothesis results
        if strategic_meets_all:
            return {"action": "SUCCESS", "solution": "strategic", "reason": "Strategic approach meets all targets"}
        elif conservative_meets_all:
            return {"action": "SUCCESS", "solution": "conservative", "reason": "Conservative approach meets all targets"}
        
        # Determine next iteration based on patterns
        strategic_eff = strategic_metrics.get('refined_efficiency_percentage', 0)
        conservative_eff = conservative_metrics.get('refined_efficiency_percentage', 0)
        strategic_unassigned = strategic_metrics.get('unassigned_visits', 999)
        conservative_unassigned = conservative_metrics.get('unassigned_visits', 999)
        
        if strategic_solves_unassigned and not strategic_hurts_efficiency:
            # Strategic is good, try refinement
            return {
                "action": "REFINE_STRATEGIC",
                "strategy": "strategic_refinement",
                "vehicle_count": 50,  # Reduce from 53
                "constraints": {"min_utilization": 0.75, "max_empty_ratio": 0.25},
                "reason": "Strategic works but can be made more efficient"
            }
        elif conservative_preserves_efficiency and strategic_solves_unassigned:
            # Hybrid approach - combine best of both
            return {
                "action": "HYBRID",
                "strategy": "hybrid_balanced", 
                "vehicle_count": 48,  # Between 46 and 53
                "constraints": {
                    "min_utilization": 0.65,
                    "max_empty_ratio": 0.30,
                    "continuity_regular": 15,
                    "continuity_high_volume": 17  # Relaxed for >50 visit clients
                },
                "reason": f"Hybrid: Strategic unassigned {strategic_unassigned}, Conservative efficiency {conservative_eff:.1f}%"
            }
        elif strategic_eff < 60 and conservative_eff < 60:
            # Both have efficiency problems - multi-phase approach
            return {
                "action": "MULTI_PHASE",
                "strategy": "sequential_optimization",
                "phase_1": {"objective": "minimize_unassigned", "vehicles": 45, "duration": "PT3H"},
                "phase_2": {"objective": "maximize_efficiency", "vehicles": "dynamic", "duration": "PT2H"},
                "reason": "Both approaches have efficiency issues - try sequential optimization"
            }
        elif strategic_unassigned <= 10 and conservative_unassigned > 30:
            # Unassigned is the main issue
            return {
                "action": "CAPACITY_FOCUS",
                "strategy": "selective_capacity_increase",
                "vehicle_count": 52,
                "constraints": {
                    "target_high_volume_clients": True,  # Extra vehicles for Client-003, Client-074
                    "min_utilization": 0.60,
                    "continuity_regular": 15,
                    "continuity_high_volume": 18
                },
                "reason": f"Focus on unassigned: Strategic {strategic_unassigned}, Conservative {conservative_unassigned}"
            }
        else:
            # Default hybrid approach
            return {
                "action": "HYBRID_DEFAULT",
                "strategy": "balanced_hybrid",
                "vehicle_count": 47,
                "constraints": {"min_utilization": 0.67, "max_empty_ratio": 0.28},
                "reason": "Default hybrid approach between strategic and conservative"
            }
    
    def create_optimization_dataset(self, config: dict) -> str:
        """Create new optimization dataset based on configuration"""
        
        self.log(f"🔧 Creating dataset for strategy: {config['strategy']}")
        
        # Load baseline input
        if not Path("baseline_input.json").exists():
            self.log("❌ baseline_input.json not found")
            return None
            
        with open("baseline_input.json") as f:
            base_data = json.load(f)
        
        # Modify based on strategy
        modified_data = base_data.copy()
        
        # Adjust vehicle count
        vehicle_count = config.get('vehicle_count', 47)
        vehicles = modified_data['vehicles'][:vehicle_count] if len(modified_data['vehicles']) >= vehicle_count else modified_data['vehicles']
        
        # Add extra vehicles if needed
        while len(vehicles) < vehicle_count:
            # Clone last vehicle with unique ID
            new_vehicle = vehicles[-1].copy()
            new_vehicle['id'] = f"extra_vehicle_{len(vehicles)}"
            vehicles.append(new_vehicle)
        
        modified_data['vehicles'] = vehicles
        
        # Add strategy-specific constraints (would need proper constraint encoding)
        # This is simplified - real implementation would modify constraint structures
        
        # Save modified dataset
        timestamp = int(time.time())
        dataset_file = f"dataset_{config['strategy']}_{timestamp}.json"
        with open(dataset_file, 'w') as f:
            json.dump(modified_data, f, indent=2)
        
        self.log(f"✅ Created dataset: {dataset_file} with {len(vehicles)} vehicles")
        return dataset_file
    
    def launch_timefold_job(self, dataset_file: str, strategy: str) -> str:
        """Launch new Timefold optimization job"""
        
        self.log(f"🚀 Launching Timefold job for strategy: {strategy}")
        
        try:
            with open(dataset_file) as f:
                dataset = json.load(f)
            
            url = TIMEFOLD_BASE
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json", 
                "X-API-KEY": API_KEY
            }
            
            payload = {"modelInput": dataset}
            
            r = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if r.status_code == 202:
                job_id = r.json().get('id')
                self.log(f"✅ Job launched successfully: {job_id}")
                
                # Save job info
                job_info = {
                    "id": job_id,
                    "strategy": strategy,
                    "dataset_file": dataset_file,
                    "launched_at": datetime.now().isoformat(),
                    "config": dataset_file
                }
                
                with open(f"job_{job_id}_info.json", 'w') as f:
                    json.dump(job_info, f, indent=2)
                
                return job_id
            else:
                self.log(f"❌ Job launch failed: HTTP {r.status_code} - {r.text}")
                return None
                
        except Exception as e:
            self.log(f"❌ Launch error: {e}")
            return None
    
    def monitor_and_iterate(self):
        """Main monitoring loop with automatic iteration"""
        
        self.log("🧬 **ENHANCED OPTIMIZATION CONTROLLER ACTIVE**")
        self.log("🎯 Target: 70-75% efficiency, ≤15 continuity, <36 unassigned")
        self.log("🔄 Hypothesis-driven iteration enabled")
        self.log("=" * 70)
        
        while True:
            try:
                self.log(f"📊 Iteration {self.iteration_count + 1} - Checking job status...")
                
                # Check current jobs
                job_statuses = {}
                all_completed = True
                
                for name, job_id in self.current_jobs.items():
                    if job_id:
                        status = self.check_job_status(job_id)
                        job_statuses[name] = status
                        self.log(f"{name.capitalize()}: {status['status']} ({job_id})")
                        
                        if not status['completed']:
                            all_completed = False
                
                # Process results when all jobs complete
                if all_completed and any(self.current_jobs.values()):
                    self.log("\n🎯 **ALL JOBS COMPLETED - ANALYZING RESULTS**")
                    
                    # Analyze all solutions
                    results = {}
                    for name, job_id in self.current_jobs.items():
                        if job_id:
                            metrics = self.analyze_solution_detailed(job_id)
                            results[name] = metrics
                            
                            if metrics:
                                eff = metrics.get('refined_efficiency_percentage', 0)
                                cont = metrics.get('continuity_failure_count', 999)
                                unass = metrics.get('unassigned_visits', 999)
                                self.log(f"{name.capitalize()}: {eff:.1f}% eff, {cont} cont fails, {unass} unassigned")
                    
                    # Test hypotheses and decide next action
                    strategic_metrics = results.get('strategic', {})
                    conservative_metrics = results.get('conservative', {})
                    
                    next_config = self.design_next_optimization(strategic_metrics, conservative_metrics)
                    
                    if next_config["action"] == "SUCCESS":
                        self.log(f"🎉 **CAMPAIGN SUCCESSFUL!**")
                        self.log(f"Best solution: {next_config['solution']}")
                        self.log(f"Reason: {next_config['reason']}")
                        break
                    else:
                        self.log(f"\n🔄 **LAUNCHING NEXT ITERATION**")
                        self.log(f"Strategy: {next_config['strategy']}")
                        self.log(f"Reason: {next_config['reason']}")
                        
                        # Create and launch next optimization
                        dataset_file = self.create_optimization_dataset(next_config)
                        if dataset_file:
                            new_job_id = self.launch_timefold_job(dataset_file, next_config['strategy'])
                            if new_job_id:
                                # Update current jobs for next iteration
                                self.current_jobs = {"next_iteration": new_job_id}
                                self.iteration_count += 1
                                
                                self.log(f"✅ Next iteration {self.iteration_count} launched: {new_job_id}")
                            else:
                                self.log("❌ Failed to launch next iteration")
                                break
                        else:
                            self.log("❌ Failed to create dataset for next iteration") 
                            break
                
                else:
                    # Show progress for active jobs
                    active_jobs = [(name, job_id) for name, job_id in self.current_jobs.items() if job_id and not job_statuses.get(name, {}).get('completed', False)]
                    if active_jobs:
                        self.log(f"⏳ {len(active_jobs)} job(s) still running...")
                        for name, job_id in active_jobs:
                            status = job_statuses.get(name, {})
                            self.log(f"  {name}: {status.get('status', 'UNKNOWN')}")
                
                # Wait before next check
                time.sleep(300)  # 5 minutes
                
            except KeyboardInterrupt:
                self.log("\n🛑 Campaign stopped by user")
                break
            except Exception as e:
                self.log(f"❌ Controller error: {e}")
                time.sleep(60)  # Wait 1 minute before retry

if __name__ == "__main__":
    controller = HypothesisDrivenController()
    controller.monitor_and_iterate()