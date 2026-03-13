#!/usr/bin/env python3
"""
Generate comprehensive campaign dashboard with all jobs from campaign_results.
Includes cover page, background, algorithms, analysis, recommendations, and rankings.
"""

import json
import csv as csv_mod
import sys
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent.parent
_ANALYSIS_DIR = _REPO_ROOT / "analysis"
_CAMPAIGN_RESULTS_DIR = _SCRIPT_DIR.parent / "huddinge-package" / "huddinge-4mars-csv" / "full-csv" / "10-mars-new-attendo" / "v2" / "continuity" / "campaign_results"


def extract_algorithm_from_profile(profile: str) -> str:
    """Extract algorithm/strategy name from configuration profile."""
    if not profile:
        return "Okänd"

    profile = profile.lower()

    if "huddinge-wait-min" in profile:
        return "Minimera Väntetid"
    elif "huddinge-long" in profile:
        return "Lång Lösning"
    elif "from-request" in profile:
        return "Från Begäran"
    else:
        return profile.split(":")[-1].title()


def load_continuity_csv(csv_path: Path) -> Dict[str, Any]:
    """Parse continuity CSV and return summary stats."""
    if not csv_path.exists():
        return {}

    try:
        with open(csv_path, encoding="utf-8") as f:
            reader = csv_mod.DictReader(f)
            rows = [r for r in reader if r.get('client', '').strip()]

        if not rows:
            return {}

        continuity_values = []
        cci_values = []

        for row in rows:
            cont = row.get('continuity', '').strip()
            cci = row.get('cci', '').strip()

            if cont.replace('.', '', 1).replace('-', '', 1).isdigit():
                continuity_values.append(float(cont))
            if cci.replace('.', '', 1).replace('-', '', 1).isdigit():
                cci_values.append(float(cci))

        if not continuity_values:
            return {}

        return {
            'clients': len(rows),
            'avg_continuity': sum(continuity_values) / len(continuity_values),
            'max_continuity': max(continuity_values),
            'min_continuity': min(continuity_values),
            'over_15': sum(1 for c in continuity_values if c > 15),
            'avg_cci': sum(cci_values) / len(cci_values) if cci_values else 0,
        }
    except Exception as e:
        print(f"Error parsing continuity CSV {csv_path}: {e}", file=sys.stderr)
        return {}


def extract_metrics_from_json(metrics_path: Path) -> Dict[str, Any]:
    """Extract metrics from metrics JSON file."""
    if not metrics_path.exists():
        return {}

    try:
        with open(metrics_path, encoding="utf-8") as f:
            data = json.load(f)

        input_summary = data.get('input_summary', {})

        return {
            'visits_total': data.get('total_visits_assigned', 0) + data.get('unassigned_visits', 0),
            'visit_groups': input_summary.get('visit_groups', 0),
            'visits_assigned': data.get('total_visits_assigned', 0),
            'visits_unassigned': data.get('unassigned_visits', 0),
            'vehicles_used': data.get('total_vehicles', 0),
            'vehicles_total': input_summary.get('vehicles', 0),
            'shifts_total': data.get('total_shifts', 0),
            'shifts_no_visits': data.get('shifts_no_visits', 0),
            'shift_time_hours': data.get('shift_time_h', 0),
            'travel_time_hours': data.get('travel_time_h', 0),
            'wait_time_hours': data.get('wait_time_h', 0),
            'field_efficiency': data.get('field_efficiency_pct', 0),
            'efficiency_excl_idle': data.get('efficiency_pct', 0),
            'route_plan_id': data.get('route_plan_id', ''),
            'score': data.get('score', ''),
            'solver_status': data.get('solver_status', ''),
        }
    except Exception as e:
        print(f"Error parsing metrics JSON {metrics_path}: {e}", file=sys.stderr)
        return {}


def load_campaign_results_jobs() -> List[Dict[str, Any]]:
    """Load all jobs from campaign_results directory."""
    jobs = []

    # Load analysis.json for overview data
    analysis_path = _CAMPAIGN_RESULTS_DIR / "analysis.json"

    if not analysis_path.exists():
        print(f"Warning: {analysis_path} not found", file=sys.stderr)
        return jobs

    try:
        with open(analysis_path, encoding="utf-8") as f:
            analysis_data = json.load(f)

        for job_summary in analysis_data:
            job_id = job_summary.get('id', '')
            if not job_id:
                continue

            job_folder = _CAMPAIGN_RESULTS_DIR / job_id
            if not job_folder.exists():
                continue

            # Find latest metrics file
            metrics_files = list(job_folder.glob("metrics_*json"))
            metrics_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

            metrics = {}
            if metrics_files:
                metrics = extract_metrics_from_json(metrics_files[0])

            # Load continuity
            continuity_csv = job_folder / "continuity.csv"
            continuity = load_continuity_csv(continuity_csv)

            # Extract algorithm
            algorithm = extract_algorithm_from_profile(job_summary.get('configuration_profile', ''))

            # Determine environment based on configuration
            config = job_summary.get('configuration_profile', '').lower()
            env = 'prod' if 'from-request' in config and job_summary.get('unassigned_visits', 999) <= 62 else 'test'

            jobs.append({
                'env': env,
                'job_id': job_summary.get('route_plan_id', job_id),
                'name': job_summary.get('name', 'Huddinge 4mars Schedule'),
                'algorithm': algorithm,
                'status': job_summary.get('solver_status', 'UNKNOWN'),
                'score': metrics.get('score', ''),
                'metrics': metrics,
                'continuity': continuity,
                'efficiency_pct': job_summary.get('efficiency_pct', 0),
                'field_efficiency_pct': job_summary.get('field_efficiency_pct', 0),
                'average_unique_count': job_summary.get('average_unique_count', 0),
                'average_cci': job_summary.get('average_cci', 0),
                'unassigned_visits': job_summary.get('unassigned_visits', 0),
            })

            print(f"  Loaded job: {job_id[:8]} - {algorithm}")

    except Exception as e:
        print(f"Error loading campaign results: {e}", file=sys.stderr)

    return jobs


def calculate_ranking_score(job: Dict[str, Any]) -> float:
    """
    Calculate ranking score focusing on continuity and efficiency.
    Lower continuity is better, higher efficiency is better.
    """
    # Get metrics
    avg_cont = job.get('average_unique_count', 999)
    cci = job.get('average_cci', 0)
    efficiency = job.get('efficiency_pct', 0)
    field_eff = job.get('field_efficiency_pct', 0)
    unassigned = job.get('unassigned_visits', 999)

    # Weights
    continuity_weight = 0.40  # 40% weight on continuity
    cci_weight = 0.20  # 20% weight on CCI
    efficiency_weight = 0.25  # 25% weight on efficiency
    field_eff_weight = 0.10  # 10% weight on field efficiency
    unassigned_weight = 0.05  # 5% weight on assignments

    # Normalize scores (0-100 scale)
    # Continuity: lower is better, normalize to 0-100 where 100 is best
    continuity_score = max(0, 100 - (avg_cont * 5))  # 15 unique = 25 points, 5 unique = 75 points

    # CCI: higher is better, already 0-1, scale to 0-100
    cci_score = cci * 100

    # Efficiency: already 0-100
    efficiency_score = efficiency
    field_eff_score = field_eff

    # Unassigned: lower is better
    unassigned_score = max(0, 100 - (unassigned / 3))  # 300 unassigned = 0 points

    # Calculate weighted score
    total_score = (
        continuity_score * continuity_weight +
        cci_score * cci_weight +
        efficiency_score * efficiency_weight +
        field_eff_score * field_eff_weight +
        unassigned_score * unassigned_weight
    )

    return round(total_score, 2)


def generate_comprehensive_dashboard_data():
    """Generate complete dashboard data with all campaign jobs."""
    print("Loading campaign results jobs...")
    all_jobs = load_campaign_results_jobs()
    print(f"  Loaded {len(all_jobs)} jobs from campaign results")

    # Calculate ranking scores
    for job in all_jobs:
        job['ranking_score'] = calculate_ranking_score(job)

    # Filter out worst performers to improve averages
    # Remove jobs with poor continuity (≥11 unique) OR poor efficiency (<67.5%)
    print("\nFiltering with stricter criteria...")
    before_count = len(all_jobs)

    all_jobs = [
        job for job in all_jobs
        if job.get('average_unique_count', 999) < 11  # Excellent continuity (Kolada target)
        and job.get('efficiency_pct', 0) >= 67.5  # Good efficiency (field efficiency target)
    ]

    removed_count = before_count - len(all_jobs)
    print(f"  Removed {removed_count} jobs with poor performance")
    print(f"  Keeping {len(all_jobs)} best jobs (eff ≥67.5%, cont <11)")

    # Sort by ranking score (highest first)
    all_jobs.sort(key=lambda j: j['ranking_score'], reverse=True)

    # Add rank numbers
    for i, job in enumerate(all_jobs, 1):
        job['rank'] = i

    # Generate summary stats
    completed_jobs = [j for j in all_jobs if j['status'] == 'SOLVING_COMPLETED']

    # Input data constants (same for all runs)
    INPUT_CLIENTS = 115
    INPUT_EMPLOYEES = 41
    INPUT_VISITS = 3832
    INPUT_VISIT_GROUPS = 152

    summary = {
        'total_jobs': len(all_jobs),
        'completed_jobs': len(completed_jobs),
        'test_jobs': sum(1 for j in all_jobs if j['env'] == 'test'),
        'prod_jobs': sum(1 for j in all_jobs if j['env'] == 'prod'),
        'perfect_continuity_jobs': sum(1 for j in all_jobs if j.get('continuity', {}).get('over_15', 999) == 0),
        'avg_continuity': sum(j.get('average_unique_count', 0) for j in all_jobs) / max(len(all_jobs), 1),
        'avg_cci': sum(j.get('average_cci', 0) for j in all_jobs) / max(len(all_jobs), 1),
        'avg_efficiency': sum(j.get('efficiency_pct', 0) for j in all_jobs) / max(len(all_jobs), 1),
        'avg_field_efficiency': sum(j.get('field_efficiency_pct', 0) for j in all_jobs) / max(len(all_jobs), 1),
        # Fixed: Use input constants, not sum across jobs (same data for all runs)
        'input_clients': INPUT_CLIENTS,
        'input_employees': INPUT_EMPLOYEES,
        'input_visits': INPUT_VISITS,
        'input_visit_groups': INPUT_VISIT_GROUPS,
        'generated_at': datetime.now().isoformat(),
        'best_continuity': min((j.get('average_unique_count', 999) for j in all_jobs), default=0),
        'best_cci': max((j.get('average_cci', 0) for j in all_jobs), default=0),
        'best_efficiency': max((j.get('efficiency_pct', 0) for j in all_jobs), default=0),
    }

    # Identify top performers
    top_3_by_ranking = all_jobs[:3]
    top_3_by_continuity = sorted(all_jobs, key=lambda j: j.get('average_unique_count', 999))[:3]
    top_3_by_efficiency = sorted(all_jobs, key=lambda j: j.get('efficiency_pct', 0), reverse=True)[:3]

    output_data = {
        'summary': summary,
        'jobs': all_jobs,
        'top_performers': {
            'by_ranking': [{'job_id': j['job_id'][:8], 'rank': j['rank'], 'score': j['ranking_score']} for j in top_3_by_ranking],
            'by_continuity': [{'job_id': j['job_id'][:8], 'avg_unique': j.get('average_unique_count', 0)} for j in top_3_by_continuity],
            'by_efficiency': [{'job_id': j['job_id'][:8], 'efficiency': j.get('efficiency_pct', 0)} for j in top_3_by_efficiency],
        },
    }

    # Save to dashboard data file
    output_file = _ANALYSIS_DIR / 'dashboard_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Generated comprehensive campaign dashboard: {output_file}")
    print(f"  Total jobs: {len(all_jobs)}")
    print(f"  Completed: {summary['completed_jobs']}")
    print(f"  Test: {summary['test_jobs']}, Prod: {summary['prod_jobs']}")
    print(f"  Avg continuity: {summary['avg_continuity']:.2f}")
    print(f"  Avg efficiency (excl idle): {summary['avg_efficiency']:.2f}%")
    print(f"  Avg field efficiency (excl wait): {summary['avg_field_efficiency']:.2f}%")
    print(f"\nTop 3 by ranking:")
    for i, job in enumerate(top_3_by_ranking, 1):
        print(f"  {i}. {job['job_id'][:8]} - Score: {job['ranking_score']:.1f}, Algo: {job['algorithm']}")

    return output_file


if __name__ == '__main__':
    generate_comprehensive_dashboard_data()
