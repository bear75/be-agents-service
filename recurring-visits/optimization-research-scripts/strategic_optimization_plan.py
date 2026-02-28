#!/usr/bin/env python3
"""
Strategic Optimization Plan
Based on detailed metrics analysis of run 41ce610c
Targeting: 70-75% efficiency + ≤15 continuity + <36 unassigned
"""

import json
import os
import requests
from datetime import datetime

TIMEFOLD_API_KEY = os.getenv('TIMEFOLD_API_KEY', 'tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8')
TIMEFOLD_BASE_URL = 'https://app.timefold.ai/api/models/field-service-routing/v1'

def analyze_current_gaps():
    """Analyze specific gaps from detailed metrics"""
    
    print("🔬 **DETAILED METRICS ANALYSIS (Run 41ce610c)**\n")
    
    current_metrics = {
        'efficiency': 62.24,  # vs target 70-75%
        'travel_efficiency': 90.18,  # excellent (>67.5% target)
        'idle_time_pct': 29.72,  # major problem
        'continuity_avg': 12.9,  # reasonable average
        'continuity_failures': 30,  # 30/81 clients over ≤15 target  
        'continuity_failure_rate': 37,  # 37% failure rate
        'unassigned': 42,  # vs target <36
        'margin_pct': 30.56,  # solid financial foundation
        'empty_shifts': 79,  # out of 340 total
        'total_shifts': 340
    }
    
    print("**TARGET ACHIEVEMENT:**")
    print(f"❌ Efficiency: {current_metrics['efficiency']}% (target: 70-75%) - GAP: -8 to -13%")
    print(f"❌ Continuity: {current_metrics['continuity_failures']}/81 clients over ≤15 ({current_metrics['continuity_failure_rate']}%) - GAP: Major")
    print(f"❌ Unassigned: {current_metrics['unassigned']} (target: <36) - GAP: +6 visits")
    
    print(f"\n**ROOT CAUSES:**")
    print(f"🔴 Idle Time: {current_metrics['idle_time_pct']}% of shift time (massive waste)")
    print(f"🔴 Empty Shifts: {current_metrics['empty_shifts']}/{current_metrics['total_shifts']} shifts have no visits")
    print(f"🔴 Continuity Distribution: 37% client failure rate unacceptable")
    print(f"🟡 Assignment Issues: Slightly over unassigned target")
    
    print(f"\n**WHAT'S WORKING:**")
    print(f"✅ Travel Efficiency: {current_metrics['travel_efficiency']}% (excellent vs >67.5% target)")
    print(f"✅ Financial Foundation: {current_metrics['margin_pct']}% margin")
    print(f"✅ Route Optimization: Only 6.56% of time spent traveling")
    
    return current_metrics

def design_multi_objective_optimization():
    """Design comprehensive optimization addressing all gaps"""
    
    print("\n🎯 **MULTI-OBJECTIVE OPTIMIZATION STRATEGY**\n")
    
    strategies = [
        {
            'name': 'Capacity-Optimized + Continuity',
            'description': 'Reduce capacity waste while improving continuity',
            'approach': {
                'shifts': 'Reduce from 340 to ~280 shifts',
                'continuity': 'High continuity weighting',
                'efficiency_target': '70-72%',
                'continuity_target': '<15 clients over ≤15',
                'expected_tradeoff': 'Slightly higher travel time'
            },
            'priority': 'highest',
            'expected_results': {
                'efficiency': '70-72%',
                'continuity_failures': '10-15 clients',
                'unassigned': '30-35',
                'idle_time': '20-25%'
            }
        },
        {
            'name': 'Continuity-First Optimization',
            'description': 'Maximize continuity control, optimize efficiency second',
            'approach': {
                'continuity': 'Very high continuity constraints',
                'shifts': 'Keep current capacity',
                'efficiency_target': '65-68%',
                'continuity_target': '<8 clients over ≤15',
                'expected_tradeoff': 'Lower efficiency but excellent continuity'
            },
            'priority': 'high',
            'expected_results': {
                'efficiency': '65-68%',
                'continuity_failures': '5-8 clients',
                'unassigned': '35-40',
                'idle_time': '25-30%'
            }
        },
        {
            'name': 'Efficiency-First Optimization',
            'description': 'Maximize capacity utilization, moderate continuity',
            'approach': {
                'shifts': 'Aggressive reduction to ~250 shifts',
                'continuity': 'Medium continuity weighting',
                'efficiency_target': '73-76%',
                'continuity_target': '<20 clients over ≤15',
                'expected_tradeoff': 'Some continuity compromise'
            },
            'priority': 'medium',
            'expected_results': {
                'efficiency': '73-76%',
                'continuity_failures': '15-20 clients',
                'unassigned': '25-32',
                'idle_time': '15-20%'
            }
        },
        {
            'name': 'Balanced Sweet Spot',
            'description': 'Balanced improvement across all metrics',
            'approach': {
                'shifts': 'Moderate reduction to ~300 shifts',
                'continuity': 'Balanced continuity weighting',
                'efficiency_target': '68-71%',
                'continuity_target': '<12 clients over ≤15',
                'expected_tradeoff': 'Compromise on all metrics'
            },
            'priority': 'high',
            'expected_results': {
                'efficiency': '68-71%',
                'continuity_failures': '8-12 clients',
                'unassigned': '32-36',
                'idle_time': '22-27%'
            }
        }
    ]
    
    for i, strategy in enumerate(strategies, 1):
        priority_stars = "⭐⭐⭐" if strategy['priority'] == 'highest' else "⭐⭐" if strategy['priority'] == 'high' else "⭐"
        
        print(f"**{i}. {strategy['name']}** {priority_stars}")
        print(f"   - {strategy['description']}")
        print(f"   - Efficiency target: {strategy['expected_results']['efficiency']}")
        print(f"   - Continuity target: {strategy['expected_results']['continuity_failures']} clients over ≤15")
        print(f"   - Unassigned target: {strategy['expected_results']['unassigned']}")
        print(f"   - Key approach: {strategy['approach']['shifts']}")
        print()
    
    return strategies

def calculate_improvement_potential():
    """Calculate financial and operational improvement potential"""
    
    print("💰 **IMPROVEMENT POTENTIAL ANALYSIS**\n")
    
    current = {
        'efficiency': 62.24,
        'visit_hours': 1507,
        'revenue': 828722,
        'cost': 575460,
        'margin': 253262,
        'margin_pct': 30.56
    }
    
    scenarios = [
        ('Conservative (68% efficiency)', 68, 0.68),
        ('Target Low (70% efficiency)', 70, 0.70),
        ('Target High (75% efficiency)', 75, 0.75)
    ]
    
    print("**FINANCIAL IMPACT SCENARIOS:**")
    for name, eff_pct, eff_ratio in scenarios:
        # Calculate additional visit hours at target efficiency
        current_paid_hours = current['visit_hours'] / (current['efficiency'] / 100)
        target_visit_hours = current_paid_hours * eff_ratio
        additional_hours = target_visit_hours - current['visit_hours']
        
        # Estimate additional revenue (assuming same rate per hour)
        hourly_revenue = current['revenue'] / current['visit_hours']
        additional_revenue = additional_hours * hourly_revenue
        new_revenue = current['revenue'] + additional_revenue
        new_margin = new_revenue - current['cost']  # Same cost (shift costs fixed)
        new_margin_pct = (new_margin / new_revenue) * 100
        
        print(f"**{name}:**")
        print(f"  - Additional visit time: {additional_hours:.0f}h")
        print(f"  - Additional revenue: {additional_revenue:,.0f} kr")
        print(f"  - New margin: {new_margin:,.0f} kr ({new_margin_pct:.1f}%)")
        print(f"  - Improvement: +{new_margin - current['margin']:,.0f} kr")
        print()

def create_test_campaign():
    """Create comprehensive test campaign"""
    
    print("🚀 **COMPREHENSIVE TEST CAMPAIGN**\n")
    
    campaign = {
        'name': 'Multi-Objective Optimization Campaign',
        'goal': 'Achieve 70-75% efficiency + ≤15 continuity + <36 unassigned',
        'baseline': 'Run 41ce610c (62.24% eff, 30 continuity failures, 42 unassigned)',
        'tests': [
            {
                'priority': 1,
                'name': 'Capacity-Optimized + Continuity Focus',
                'timeline': '4-6 hours',
                'success_criteria': '70%+ efficiency, <15 continuity failures'
            },
            {
                'priority': 2, 
                'name': 'Balanced Sweet Spot',
                'timeline': '3-5 hours',
                'success_criteria': '68%+ efficiency, <12 continuity failures'
            },
            {
                'priority': 3,
                'name': 'Continuity-First Optimization',
                'timeline': '3-5 hours', 
                'success_criteria': '<8 continuity failures, maintain 65%+ efficiency'
            }
        ]
    }
    
    print(f"**Campaign: {campaign['name']}**")
    print(f"**Goal:** {campaign['goal']}")
    print(f"**Baseline:** {campaign['baseline']}")
    print()
    
    for test in campaign['tests']:
        print(f"**Test {test['priority']}: {test['name']}**")
        print(f"- Timeline: {test['timeline']}")
        print(f"- Success: {test['success_criteria']}")
        print()
    
    return campaign

def main():
    print("🧬 **STRATEGIC OPTIMIZATION PLAN**")
    print("Based on detailed metrics analysis of run 41ce610c")
    print("="*70)
    
    # Analyze current performance gaps
    current_metrics = analyze_current_gaps()
    
    print("\n" + "="*70)
    
    # Design multi-objective strategies
    strategies = design_multi_objective_optimization()
    
    print("="*70)
    
    # Calculate improvement potential
    calculate_improvement_potential()
    
    print("="*70)
    
    # Create test campaign
    campaign = create_test_campaign()
    
    print("="*70 + "\n")
    
    print("🎯 **EXECUTIVE SUMMARY:**")
    print("Current run 41ce610c does NOT meet your goals but shows clear optimization paths:")
    print(f"- **Efficiency Gap:** -8 to -13% (mainly from 29.72% idle time)")
    print(f"- **Continuity Crisis:** 37% client failure rate (30/81 clients)")
    print(f"- **Assignment:** Slightly over target (+6 visits)")
    print(f"- **Financial Opportunity:** +175,000 kr revenue potential at 75% efficiency")
    
    print(f"\n🚀 **NEXT ACTIONS:**")
    print(f"1. Launch 3-test campaign addressing efficiency + continuity + assignment")
    print(f"2. Monitor results in 6-8 hours") 
    print(f"3. Expected outcome: 1-2 runs hitting your targets")
    print(f"4. Financial upside: 35-40% margins (vs current 30.56%)")

if __name__ == '__main__':
    main()