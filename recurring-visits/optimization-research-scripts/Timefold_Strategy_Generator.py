#!/usr/bin/env python3
"""
Timefold Strategy Generator - Multi-Agent Research System
Generates hundreds of strategy configurations for systematic optimization exploration
"""

import json
import itertools
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

class PoolMethod(Enum):
    MANUAL = "manual"
    AREA = "area"
    FIRST_RUN = "first-run"
    FREQUENCY = "frequency"
    TIME_BASED = "time-based"
    HYBRID = "hybrid"

class ConstraintType(Enum):
    HARD = "hard"
    SOFT = "soft"
    MIXED = "mixed"
    DYNAMIC = "dynamic"

class Objective(Enum):
    EFFICIENCY_FIRST = "efficiency-first"
    CONTINUITY_FIRST = "continuity-first"
    BALANCED = "balanced"
    COST_OPTIMIZED = "cost-optimized"
    QUALITY_OPTIMIZED = "quality-optimized"

@dataclass
class StrategyConfig:
    """Configuration for a single Timefold optimization strategy"""
    
    name: str
    n_value: int
    pool_method: PoolMethod
    constraint_type: ConstraintType
    objective: Objective
    priority: int
    expected_efficiency_range: tuple
    expected_continuity_range: tuple
    parent_strategy: str = None
    iteration: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "n_value": self.n_value,
            "pool_method": self.pool_method.value,
            "constraint_type": self.constraint_type.value,
            "objective": self.objective.value,
            "priority": self.priority,
            "expected_efficiency_range": self.expected_efficiency_range,
            "expected_continuity_range": self.expected_continuity_range,
            "parent_strategy": self.parent_strategy,
            "iteration": self.iteration
        }

class TimefoldStrategyGenerator:
    """Generates systematic strategy configurations for multi-agent Timefold research"""
    
    def __init__(self):
        self.strategies = []
        self.strategy_tree = {}
        
    def generate_baseline_strategies(self) -> List[StrategyConfig]:
        """Generate Level 1 baseline strategies (10 core configurations)"""
        
        baseline_strategies = [
            # Core baseline comparisons
            StrategyConfig(
                name="unconstrained_baseline",
                n_value=999,
                pool_method=PoolMethod.MANUAL,
                constraint_type=ConstraintType.HARD,
                objective=Objective.EFFICIENCY_FIRST,
                priority=1,
                expected_efficiency_range=(82, 88),
                expected_continuity_range=(15, 25)
            ),
            
            StrategyConfig(
                name="manual_replication",
                n_value=5,
                pool_method=PoolMethod.MANUAL,
                constraint_type=ConstraintType.HARD,
                objective=Objective.CONTINUITY_FIRST,
                priority=1,
                expected_efficiency_range=(65, 70),
                expected_continuity_range=(3, 5)
            ),
            
            # Target sweet spot candidates
            StrategyConfig(
                name="manual_n10_balanced",
                n_value=10,
                pool_method=PoolMethod.MANUAL,
                constraint_type=ConstraintType.HARD,
                objective=Objective.BALANCED,
                priority=1,
                expected_efficiency_range=(72, 78),
                expected_continuity_range=(8, 12)
            ),
            
            StrategyConfig(
                name="first_run_n10",
                n_value=10,
                pool_method=PoolMethod.FIRST_RUN,
                constraint_type=ConstraintType.HARD,
                objective=Objective.EFFICIENCY_FIRST,
                priority=1,
                expected_efficiency_range=(74, 80),
                expected_continuity_range=(7, 11)
            ),
            
            # Area-based alternatives
            StrategyConfig(
                name="area_n8_geographic",
                n_value=8,
                pool_method=PoolMethod.AREA,
                constraint_type=ConstraintType.HARD,
                objective=Objective.BALANCED,
                priority=2,
                expected_efficiency_range=(70, 76),
                expected_continuity_range=(6, 10)
            ),
            
            # Soft constraint experiments
            StrategyConfig(
                name="soft_n15_preferences",
                n_value=15,
                pool_method=PoolMethod.FIRST_RUN,
                constraint_type=ConstraintType.SOFT,
                objective=Objective.EFFICIENCY_FIRST,
                priority=2,
                expected_efficiency_range=(78, 85),
                expected_continuity_range=(10, 16)
            ),
            
            # Hybrid approaches
            StrategyConfig(
                name="hybrid_n7_mixed",
                n_value=7,
                pool_method=PoolMethod.HYBRID,
                constraint_type=ConstraintType.MIXED,
                objective=Objective.BALANCED,
                priority=2,
                expected_efficiency_range=(71, 77),
                expected_continuity_range=(5, 9)
            ),
            
            # Frequency-based pools
            StrategyConfig(
                name="frequency_n12_common",
                n_value=12,
                pool_method=PoolMethod.FREQUENCY,
                constraint_type=ConstraintType.HARD,
                objective=Objective.BALANCED,
                priority=2,
                expected_efficiency_range=(75, 81),
                expected_continuity_range=(9, 13)
            ),
            
            # Time-based specialization
            StrategyConfig(
                name="time_based_n6_specialists",
                n_value=6,
                pool_method=PoolMethod.TIME_BASED,
                constraint_type=ConstraintType.HARD,
                objective=Objective.QUALITY_OPTIMIZED,
                priority=3,
                expected_efficiency_range=(68, 74),
                expected_continuity_range=(4, 8)
            ),
            
            # Cost-optimized
            StrategyConfig(
                name="cost_optimized_n9",
                n_value=9,
                pool_method=PoolMethod.FIRST_RUN,
                constraint_type=ConstraintType.MIXED,
                objective=Objective.COST_OPTIMIZED,
                priority=2,
                expected_efficiency_range=(73, 79),
                expected_continuity_range=(7, 11)
            )
        ]
        
        self.strategies.extend(baseline_strategies)
        return baseline_strategies
    
    def generate_refinement_strategies(self, parent_results: Dict[str, Any]) -> List[StrategyConfig]:
        """Generate Level 2 refinement strategies based on promising Level 1 results"""
        
        refinement_strategies = []
        
        # For each successful parent strategy, generate variations
        for parent_name, results in parent_results.items():
            if self._is_promising_result(results):
                parent_config = self._get_strategy_config(parent_name)
                
                # N-value variations (±2 from parent)
                for n_delta in [-2, -1, +1, +2]:
                    new_n = max(1, parent_config.n_value + n_delta)
                    
                    refinement_strategies.append(StrategyConfig(
                        name=f"{parent_name}_n{new_n}",
                        n_value=new_n,
                        pool_method=parent_config.pool_method,
                        constraint_type=parent_config.constraint_type,
                        objective=parent_config.objective,
                        priority=parent_config.priority,
                        expected_efficiency_range=self._adjust_efficiency_range(
                            parent_config.expected_efficiency_range, n_delta
                        ),
                        expected_continuity_range=self._adjust_continuity_range(
                            parent_config.expected_continuity_range, n_delta
                        ),
                        parent_strategy=parent_name,
                        iteration=2
                    ))
                
                # Constraint type variations
                for constraint_type in [ConstraintType.HARD, ConstraintType.SOFT, ConstraintType.MIXED]:
                    if constraint_type != parent_config.constraint_type:
                        refinement_strategies.append(StrategyConfig(
                            name=f"{parent_name}_{constraint_type.value}",
                            n_value=parent_config.n_value,
                            pool_method=parent_config.pool_method,
                            constraint_type=constraint_type,
                            objective=parent_config.objective,
                            priority=parent_config.priority + 1,
                            expected_efficiency_range=parent_config.expected_efficiency_range,
                            expected_continuity_range=parent_config.expected_continuity_range,
                            parent_strategy=parent_name,
                            iteration=2
                        ))
        
        self.strategies.extend(refinement_strategies)
        return refinement_strategies
    
    def generate_advanced_strategies(self, refinement_results: Dict[str, Any]) -> List[StrategyConfig]:
        """Generate Level 3 advanced strategies for final optimization"""
        
        advanced_strategies = []
        
        # Dynamic constraint strategies
        for n_value in [5, 7, 10, 12]:
            advanced_strategies.append(StrategyConfig(
                name=f"dynamic_n{n_value}_timevarying",
                n_value=n_value,
                pool_method=PoolMethod.HYBRID,
                constraint_type=ConstraintType.DYNAMIC,
                objective=Objective.BALANCED,
                priority=3,
                expected_efficiency_range=(70, 80),
                expected_continuity_range=(6, 14),
                iteration=3
            ))
        
        # Multi-objective optimization
        for n_value in [8, 10, 12]:
            for objective in [Objective.QUALITY_OPTIMIZED, Objective.COST_OPTIMIZED]:
                advanced_strategies.append(StrategyConfig(
                    name=f"multiobjective_n{n_value}_{objective.value}",
                    n_value=n_value,
                    pool_method=PoolMethod.FIRST_RUN,
                    constraint_type=ConstraintType.MIXED,
                    objective=objective,
                    priority=3,
                    expected_efficiency_range=(72, 82),
                    expected_continuity_range=(7, 13),
                    iteration=3
                ))
        
        self.strategies.extend(advanced_strategies)
        return advanced_strategies
    
    def generate_systematic_matrix(self) -> List[StrategyConfig]:
        """Generate systematic exploration matrix (100+ configurations)"""
        
        matrix_strategies = []
        
        # Systematic N-value exploration
        n_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 18, 20, 25]
        pool_methods = [PoolMethod.MANUAL, PoolMethod.FIRST_RUN, PoolMethod.AREA, PoolMethod.HYBRID]
        constraint_types = [ConstraintType.HARD, ConstraintType.SOFT, ConstraintType.MIXED]
        
        priority_counter = 1
        for n_value in n_values:
            for pool_method in pool_methods:
                for constraint_type in constraint_types:
                    # Calculate expected ranges based on N-value
                    eff_range = self._calculate_efficiency_range(n_value)
                    cont_range = self._calculate_continuity_range(n_value)
                    
                    matrix_strategies.append(StrategyConfig(
                        name=f"matrix_{pool_method.value}_n{n_value}_{constraint_type.value}",
                        n_value=n_value,
                        pool_method=pool_method,
                        constraint_type=constraint_type,
                        objective=Objective.BALANCED,
                        priority=priority_counter % 5 + 1,
                        expected_efficiency_range=eff_range,
                        expected_continuity_range=cont_range,
                        iteration=1
                    ))
                    priority_counter += 1
        
        return matrix_strategies
    
    def _is_promising_result(self, results: Dict[str, Any]) -> bool:
        """Determine if results warrant further exploration"""
        efficiency = results.get('efficiency', 0)
        continuity = results.get('continuity', 999)
        unassigned = results.get('unassigned', 999)
        
        # Promising if: efficiency > 70% AND continuity < 15 AND unassigned < 50
        return efficiency > 70 and continuity < 15 and unassigned < 50
    
    def _get_strategy_config(self, strategy_name: str) -> StrategyConfig:
        """Get strategy configuration by name"""
        for strategy in self.strategies:
            if strategy.name == strategy_name:
                return strategy
        return None
    
    def _adjust_efficiency_range(self, base_range: tuple, n_delta: int) -> tuple:
        """Adjust efficiency range based on N-value change"""
        # Higher N generally means higher efficiency
        adjustment = n_delta * 1.5
        return (base_range[0] + adjustment, base_range[1] + adjustment)
    
    def _adjust_continuity_range(self, base_range: tuple, n_delta: int) -> tuple:
        """Adjust continuity range based on N-value change"""
        # Higher N generally means higher continuity
        adjustment = n_delta * 0.8
        return (base_range[0] + adjustment, base_range[1] + adjustment)
    
    def _calculate_efficiency_range(self, n_value: int) -> tuple:
        """Calculate expected efficiency range based on N-value"""
        if n_value <= 3:
            return (65, 72)
        elif n_value <= 7:
            return (70, 78)
        elif n_value <= 12:
            return (75, 83)
        else:
            return (80, 87)
    
    def _calculate_continuity_range(self, n_value: int) -> tuple:
        """Calculate expected continuity range based on N-value"""
        return (min(3, n_value), min(n_value + 3, 25))
    
    def export_strategies(self, filename: str = None) -> Dict[str, Any]:
        """Export all strategies as JSON for agent execution"""
        
        strategy_data = {
            "total_strategies": len(self.strategies),
            "baseline_count": len([s for s in self.strategies if s.iteration == 1]),
            "refinement_count": len([s for s in self.strategies if s.iteration == 2]),
            "advanced_count": len([s for s in self.strategies if s.iteration == 3]),
            "strategies": [strategy.to_dict() for strategy in self.strategies]
        }
        
        if filename:
            with open(filename, 'w') as f:
                json.dump(strategy_data, f, indent=2)
        
        return strategy_data

def main():
    """Generate comprehensive strategy matrix for Timefold research"""
    
    generator = TimefoldStrategyGenerator()
    
    print("🧬 GENERATING TIMEFOLD STRATEGY MATRIX...")
    
    # Generate baseline strategies
    baseline = generator.generate_baseline_strategies()
    print(f"✅ Generated {len(baseline)} baseline strategies")
    
    # Generate systematic matrix
    matrix = generator.generate_systematic_matrix()
    print(f"✅ Generated {len(matrix)} matrix strategies")
    
    # Export for agent execution
    strategy_data = generator.export_strategies("/tmp/timefold_strategy_matrix.json")
    
    print(f"🚀 TOTAL STRATEGIES: {strategy_data['total_strategies']}")
    print(f"📊 Baseline: {strategy_data['baseline_count']}")
    print(f"🔬 Matrix exploration: {len(matrix)}")
    
    # Print summary by priority
    priorities = {}
    for strategy in generator.strategies:
        priorities[strategy.priority] = priorities.get(strategy.priority, 0) + 1
    
    print("\n📋 EXECUTION PRIORITIES:")
    for priority in sorted(priorities.keys()):
        print(f"   Priority {priority}: {priorities[priority]} strategies")
    
    print(f"\n💾 Exported to: /tmp/timefold_strategy_matrix.json")
    return strategy_data

if __name__ == "__main__":
    main()