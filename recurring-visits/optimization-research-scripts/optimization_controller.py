#!/usr/bin/env python3
"""
Optimization Campaign Controller
Monitors active jobs, analyzes results, and launches next optimization phases
Goal: Reach 70-75% efficiency, ≤15 continuity, <36 unassigned visits
"""

import json
import time
import subprocess
import requests
from pathlib import Path
from datetime import datetime, timedelta

TIMEFOLD_BASE = "https://app.timefold.ai/api/models/field-service-routing/v1/route-plans"
API_KEY = "tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8"

TARGET_EFFICIENCY = 75.0  # Target efficiency percentage
TARGET_CONTINUITY_FAILURES = 8  # Max clients failing ≤15 caregiver target (10% of 81)
TARGET_UNASSIGNED = 36

class OptimizationController:
    def __init__(self):
        self.strategic_id = "b69e582b-9321-4cfe-be40-92bc27287b5e"
        self.conservative_id = "48b04930-53ef-4b69-b34b-7235e97879cd"
        self.results_log = []
        
    def check_job_status(self, job_id: str) -> dict:
        """Check Timefold job status and extract key metrics"""
        url = f"{TIMEFOLD_BASE}/{job_id}"
        headers = {"Accept": "application/json", "X-API-KEY": API_KEY}
        
        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                data = r.json()
                return {
                    'id': job_id,
                    'status': data.get('status'),
                    'score': data.get('score'),
                    'metadata': data.get('metadata', {}),
                    'completed': data.get('status') == 'COMPLETED',
                    'raw_data': data
                }
        except Exception as e:
            print(f"❌ Error checking job {job_id}: {e}")
            
        return {'id': job_id, 'status': 'ERROR', 'completed': False}
    
    def analyze_solution(self, job_id: str) -> dict:
        """Extract detailed metrics from completed solution"""
        if not Path(f"solution_{job_id}.json").exists():
            # Fetch solution if not already saved
            result = subprocess.run([
                "python3", "fetch_timefold_solution.py", job_id,
                "--save", f"solution_{job_id}.json"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to fetch solution for {job_id}")
                return {}
        
        try:
            with open(f"solution_{job_id}.json") as f:
                solution = json.load(f)
            
            # Run analysis script to extract metrics
            analysis_result = subprocess.run([
                "python3", "analyze_solution.py", f"solution_{job_id}.json"
            ], capture_output=True, text=True)
            
            if analysis_result.returncode == 0:
                metrics = json.loads(analysis_result.stdout)
                return metrics
            else:
                print(f"⚠️ Analysis failed for {job_id}: {analysis_result.stderr}")
                
        except Exception as e:
            print(f"❌ Error analyzing solution {job_id}: {e}")
            
        return {}
    
    def meets_target_criteria(self, metrics: dict) -> tuple[bool, str]:
        """Check if solution meets all target criteria"""
        if not metrics:
            return False, "No metrics available"
            
        efficiency = metrics.get('efficiency_percentage', 0)
        continuity_failures = metrics.get('continuity_failure_count', 999)
        unassigned_count = metrics.get('unassigned_visits', 999)
        
        issues = []
        
        if efficiency < 70.0:
            issues.append(f"Efficiency {efficiency:.1f}% < 70%")
        if continuity_failures > TARGET_CONTINUITY_FAILURES:
            issues.append(f"Continuity failures {continuity_failures} > {TARGET_CONTINUITY_FAILURES}")
        if unassigned_count > TARGET_UNASSIGNED:
            issues.append(f"Unassigned {unassigned_count} > {TARGET_UNASSIGNED}")
            
        if issues:
            return False, "; ".join(issues)
        else:
            return True, f"✅ All targets met: {efficiency:.1f}% efficiency, {continuity_failures} continuity failures, {unassigned_count} unassigned"
    
    def design_next_test(self, strategic_metrics: dict, conservative_metrics: dict) -> dict:
        """Design next optimization test based on current results"""
        
        # Analyze performance gaps
        strategic_efficiency = strategic_metrics.get('efficiency_percentage', 0)
        strategic_continuity = strategic_metrics.get('continuity_failure_count', 999)
        strategic_unassigned = strategic_metrics.get('unassigned_visits', 999)
        
        conservative_efficiency = conservative_metrics.get('efficiency_percentage', 0)
        conservative_continuity = conservative_metrics.get('continuity_failure_count', 999)
        conservative_unassigned = conservative_metrics.get('unassigned_visits', 999)
        
        # Determine hybrid strategy
        if strategic_unassigned <= 10 and conservative_efficiency >= 65:
            # Hybrid: Strategic unassigned performance + Conservative efficiency
            strategy = "hybrid_balanced"
            vehicle_count = 48  # Between strategic 53 and conservative 46
            constraints = {
                "max_continuity_regular": 15,  # ≤50 visits
                "max_continuity_high": 17,    # >50 visits
                "min_vehicle_utilization": 0.65,
                "max_empty_shift_ratio": 0.25
            }
        elif strategic_efficiency < 60:
            # Strategic has efficiency problems - reduce capacity
            strategy = "efficiency_focused"  
            vehicle_count = 44
            constraints = {
                "max_continuity_regular": 16,  # Slightly relaxed
                "max_continuity_high": 18,
                "min_vehicle_utilization": 0.70,
                "max_empty_shift_ratio": 0.20
            }
        elif conservative_unassigned > 20:
            # Conservative has unassigned problems - increase capacity selectively
            strategy = "selective_capacity"
            vehicle_count = 49
            constraints = {
                "max_continuity_regular": 15,
                "max_continuity_high": 16,
                "targeted_capacity_increase": True,
                "min_vehicle_utilization": 0.60
            }
        else:
            # Fine-tuning approach
            strategy = "fine_tuning"
            vehicle_count = 47
            constraints = {
                "max_continuity_regular": 15,
                "max_continuity_high": 16,
                "min_vehicle_utilization": 0.67,
                "max_empty_shift_ratio": 0.22
            }
        
        return {
            "strategy": strategy,
            "vehicle_count": vehicle_count,
            "constraints": constraints,
            "rationale": f"Strategic: {strategic_efficiency:.1f}% eff, {strategic_unassigned} unassigned; Conservative: {conservative_efficiency:.1f}% eff, {conservative_unassigned} unassigned"
        }
    
    def launch_next_optimization(self, config: dict) -> str:
        """Launch next optimization test based on configuration"""
        print(f"🚀 Launching {config['strategy']} optimization...")
        print(f"📊 Config: {config['vehicle_count']} vehicles, constraints: {config['constraints']}")
        
        # Create modified dataset based on config
        # This would involve modifying the baseline input with new vehicle count and constraints
        # Implementation depends on your data structure and constraint encoding
        
        # For now, return a placeholder
        return f"next_test_{int(time.time())}"
    
    def monitor_campaign(self):
        """Main monitoring loop"""
        print("🧬 **OPTIMIZATION CAMPAIGN CONTROLLER ACTIVE**")
        print("=" * 70)
        
        while True:
            print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Checking job status...")
            
            strategic_status = self.check_job_status(self.strategic_id)
            conservative_status = self.check_job_status(self.conservative_id)
            
            print(f"Strategic (+15): {strategic_status['status']}")
            print(f"Conservative (+8): {conservative_status['status']}")
            
            # Check if both jobs completed
            if strategic_status['completed'] and conservative_status['completed']:
                print("\n🎯 **BOTH OPTIMIZATIONS COMPLETED - ANALYZING RESULTS**")
                
                strategic_metrics = self.analyze_solution(self.strategic_id)
                conservative_metrics = self.analyze_solution(self.conservative_id)
                
                # Check if either meets targets
                strategic_success, strategic_msg = self.meets_target_criteria(strategic_metrics)
                conservative_success, conservative_msg = self.meets_target_criteria(conservative_metrics)
                
                print(f"\nStrategic Result: {strategic_msg}")
                print(f"Conservative Result: {conservative_msg}")
                
                if strategic_success or conservative_success:
                    print("🎉 **TARGET ACHIEVED!**")
                    best_solution = "strategic" if strategic_success else "conservative"
                    print(f"Best solution: {best_solution}")
                    break
                else:
                    print("\n🔄 **DESIGNING NEXT OPTIMIZATION PHASE**")
                    next_config = self.design_next_test(strategic_metrics, conservative_metrics)
                    print(f"Next strategy: {next_config}")
                    
                    # Launch next test
                    next_job_id = self.launch_next_optimization(next_config)
                    print(f"Next job ID: {next_job_id}")
                    
                    # Continue monitoring with new job
                    self.strategic_id = next_job_id
                    self.conservative_id = None  # Single job for next phase
                    
            else:
                # Show current progress
                if strategic_status['status'] == 'SOLVING_ACTIVE':
                    print("Strategic test: Actively optimizing...")
                if conservative_status['status'] == 'SOLVING_ACTIVE':
                    print("Conservative test: Actively optimizing...")
                    
                print("⏳ Waiting for completion...")
                
            # Wait before next check
            time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    controller = OptimizationController()
    try:
        controller.monitor_campaign()
    except KeyboardInterrupt:
        print("\n🛑 Campaign monitoring stopped by user")
    except Exception as e:
        print(f"❌ Campaign controller error: {e}")