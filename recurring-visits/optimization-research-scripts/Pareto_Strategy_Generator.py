#!/usr/bin/env python3
"""
Pareto Frontier Strategy Generator - Based on Proven Methodology
Focuses on first-run pool sweep to map efficiency-continuity trade-off curve
"""

import json
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class ParetoStrategy:
    """Strategy configuration for Pareto frontier mapping"""
    
    name: str
    n_value: int
    pool_method: str = "first-run"
    config_id: str = "a43d4eec-9f53-40b3-82ad-f135adc8c7e3"
    expected_efficiency: float = 0.0
    expected_continuity: float = 0.0
    priority: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "n_value": self.n_value,
            "pool_method": self.pool_method,
            "config_id": self.config_id,
            "expected_efficiency": self.expected_efficiency,
            "expected_continuity": self.expected_continuity,
            "priority": self.priority
        }

class ParetoFrontierGenerator:
    """Generates systematic Pareto frontier exploration strategies"""
    
    def __init__(self):
        # Confirmed baseline from pilot report
        self.manual_baseline = {
            "efficiency": 67.8,
            "continuity": 2.9,
            "margin": 31.0,
            "travel": 24.0
        }
        
        self.unconstrained_baseline = {
            "efficiency": 85.7,
            "continuity": 19.3,
            "margin": 51.0,
            "travel": 9.8,
            "unassigned": 114
        }
        
        # Target sweet spot criteria
        self.sweet_spot = {
            "min_efficiency": 77.0,
            "max_continuity": 10.0
        }
    
    def generate_pareto_sweep(self) -> List[ParetoStrategy]:
        """Generate systematic N-value sweep for Pareto frontier mapping"""
        
        strategies = []
        
        # Core N-values for systematic exploration (N=4 minimum as requested)
        n_values = [4, 5, 6, 7, 8, 10, 12, 15, 20]
        
        for n_value in n_values:
            # Calculate expected metrics based on interpolation
            efficiency = self._estimate_efficiency(n_value)
            continuity = self._estimate_continuity(n_value)
            
            strategy = ParetoStrategy(
                name=f"sweep_n{n_value}_first_run",
                n_value=n_value,
                expected_efficiency=efficiency,
                expected_continuity=continuity,
                priority=self._calculate_priority(n_value, efficiency, continuity)
            )
            
            strategies.append(strategy)
        
        # Add critical anchor points
        strategies.extend(self._generate_anchor_strategies())
        
        # Sort by priority (sweet spot candidates first)
        strategies.sort(key=lambda s: s.priority)
        
        return strategies
    
    def generate_refinement_sweep(self, promising_n: int) -> List[ParetoStrategy]:
        """Generate fine-grained sweep around promising N-value"""
        
        strategies = []
        
        # Fine-grained exploration around promising point
        for delta in [-2, -1, +1, +2]:
            refined_n = max(4, promising_n + delta)
            
            if refined_n <= 25:  # Keep reasonable upper bound
                efficiency = self._estimate_efficiency(refined_n)
                continuity = self._estimate_continuity(refined_n)
                
                strategy = ParetoStrategy(
                    name=f"refine_n{refined_n}_from_n{promising_n}",
                    n_value=refined_n,
                    expected_efficiency=efficiency,
                    expected_continuity=continuity,
                    priority=2
                )
                
                strategies.append(strategy)
        
        return strategies
    
    def _generate_anchor_strategies(self) -> List[ParetoStrategy]:
        """Generate anchor point strategies for comparison"""
        
        anchors = [
            # Unconstrained baseline (for comparison)
            ParetoStrategy(
                name="unconstrained_baseline",
                n_value=999,  # No constraint
                expected_efficiency=85.7,
                expected_continuity=19.3,
                priority=5
            ),
            
            # Sweet spot candidates (based on pilot analysis)
            ParetoStrategy(
                name="sweet_spot_candidate_low",
                n_value=6,
                expected_efficiency=78.5,
                expected_continuity=8.2,
                priority=1
            ),
            
            ParetoStrategy(
                name="sweet_spot_candidate_high", 
                n_value=8,
                expected_efficiency=81.2,
                expected_continuity=9.8,
                priority=1
            )
        ]
        
        return anchors
    
    def _estimate_efficiency(self, n_value: int) -> float:
        """Estimate efficiency based on N-value using interpolation"""
        
        # Known points: manual (2.9 cont, 67.8% eff), unconstrained (19.3 cont, 85.7% eff)
        # Efficiency generally increases with higher N (more vehicle options)
        
        if n_value >= 20:
            return 85.0  # Approaching unconstrained
        elif n_value >= 15:
            return 83.5
        elif n_value >= 12:
            return 82.0
        elif n_value >= 10:
            return 80.5
        elif n_value >= 8:
            return 79.0
        elif n_value >= 6:
            return 77.5  # Sweet spot zone
        elif n_value >= 5:
            return 75.5
        else:  # N=4
            return 73.0  # Still improvement over manual 67.8%
    
    def _estimate_continuity(self, n_value: int) -> float:
        """Estimate continuity based on N-value"""
        
        # Continuity generally increases with N-value but not linearly
        # Manual baseline: 2.9, unconstrained: 19.3
        
        if n_value >= 20:
            return 18.0  # Approaching unconstrained
        elif n_value >= 15:
            return 15.5
        elif n_value >= 12:
            return 13.0
        elif n_value >= 10:
            return 11.0  # Just over sweet spot threshold
        elif n_value >= 8:
            return 9.5   # Sweet spot zone
        elif n_value >= 6:
            return 7.8   # Sweet spot zone
        elif n_value >= 5:
            return 6.5
        else:  # N=4
            return 5.2   # Significant improvement over manual 2.9
    
    def _calculate_priority(self, n_value: int, efficiency: float, continuity: float) -> int:
        """Calculate execution priority based on sweet spot criteria"""
        
        # Priority 1: Sweet spot candidates (efficiency > 77%, continuity < 10)
        if efficiency >= self.sweet_spot["min_efficiency"] and continuity <= self.sweet_spot["max_continuity"]:
            return 1
        
        # Priority 2: Close to sweet spot
        elif efficiency >= 75.0 and continuity <= 12.0:
            return 2
        
        # Priority 3: Significant improvement over manual
        elif efficiency >= 72.0:
            return 3
        
        # Priority 4: Marginal cases
        else:
            return 4
    
    def generate_execution_plan(self) -> Dict[str, Any]:
        """Generate complete execution plan for Pareto frontier research"""
        
        strategies = self.generate_pareto_sweep()
        
        # Group strategies by priority
        priority_groups = {}
        for strategy in strategies:
            priority_groups.setdefault(strategy.priority, []).append(strategy)
        
        execution_plan = {
            "research_goal": "Map efficiency-continuity Pareto frontier",
            "baseline_manual": self.manual_baseline,
            "baseline_unconstrained": self.unconstrained_baseline,
            "sweet_spot_criteria": self.sweet_spot,
            "total_strategies": len(strategies),
            "priority_groups": {
                f"priority_{p}": [s.to_dict() for s in group] 
                for p, group in priority_groups.items()
            },
            "execution_config": {
                "timefold_api_key": "tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8",
                "config_id": "a43d4eec-9f53-40b3-82ad-f135adc8c7e3",
                "base_input": "solve/input_20260224_202857.json",
                "seed_output": "solve/iter1/391486da-output.json",
                "parallel_jobs": 4,
                "split_by_slinga_type": True
            },
            "expected_outcomes": {
                "identify_sweet_spot": "N-value achieving >77% efficiency + <10 continuity",
                "map_trade_off_curve": "Complete efficiency-continuity frontier",
                "business_recommendations": "3 optimal configurations for client decision"
            }
        }
        
        return execution_plan

def main():
    """Generate Pareto frontier research plan"""
    
    generator = ParetoFrontierGenerator()
    
    print("🎯 GENERATING PARETO FRONTIER RESEARCH PLAN...")
    
    # Generate execution plan
    plan = generator.generate_execution_plan()
    
    # Save plan
    with open("/tmp/pareto_frontier_plan.json", "w") as f:
        json.dump(plan, f, indent=2)
    
    print(f"✅ Generated {plan['total_strategies']} strategies")
    print("\n📊 EXECUTION PRIORITIES:")
    for priority, group in plan["priority_groups"].items():
        print(f"   {priority}: {len(group)} strategies")
        for strategy in group:
            print(f"      • N={strategy['n_value']:2d}: {strategy['expected_efficiency']:4.1f}% eff, {strategy['expected_continuity']:4.1f} cont")
    
    print(f"\n🎯 SWEET SPOT TARGETS:")
    print(f"   • Efficiency: >{plan['sweet_spot_criteria']['min_efficiency']}%")
    print(f"   • Continuity: <{plan['sweet_spot_criteria']['max_continuity']}")
    
    print(f"\n💾 Plan saved to: /tmp/pareto_frontier_plan.json")
    
    return plan

if __name__ == "__main__":
    main()