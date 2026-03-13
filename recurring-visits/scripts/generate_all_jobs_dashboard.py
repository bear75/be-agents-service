#!/usr/bin/env python3
"""
Generate comprehensive dashboard data from ALL Timefold job analysis results.
Includes jobs from:
- continuity_batch_test
- continuity_batch_prod
- huddinge v2 continuity analysis
- All submitted Timefold jobs from yesterday
"""

import json
import csv as csv_mod
import sys
from pathlib import Path
from typing import Any, Dict, List

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent.parent
_ANALYSIS_DIR = _REPO_ROOT / "analysis"
_HUDDINGE_V2_DIR = _SCRIPT_DIR.parent / "huddinge-package" / "huddinge-4mars-csv" / "full-csv" / "10-mars-new-attendo" / "v2"


def load_batch_results(batch_folder: str) -> List[Dict[str, Any]]:
    """Load batch_results.json from a continuity batch folder."""
    batch_path = _ANALYSIS_DIR / batch_folder / "batch_results.json"
    if not batch_path.exists():
        return []

    with open(batch_path, encoding="utf-8") as f:
        return json.load(f)


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

            if cont.replace('.', '', 1).isdigit():
                continuity_values.append(float(cont))
            if cci.replace('.', '', 1).isdigit():
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


def transform_job_data(job: Dict[str, Any], env: str, batch_folder: str) -> Dict[str, Any]:
    """Transform job data from batch_results format to dashboard format."""
    job_id = job.get('job_id', 'unknown')
    job_folder = _ANALYSIS_DIR / batch_folder / job_id[:8]

    # Load continuity
    continuity_csv = job_folder / "continuity.csv"
    continuity = load_continuity_csv(continuity_csv)

    # Merge with existing continuity data
    existing_cont = job.get('continuity', {})
    continuity.update(existing_cont)

    return {
        'env': env,
        'job_id': job_id,
        'name': job.get('name', ''),
        'status': job.get('status', ''),
        'score': job.get('score', ''),
        'metrics': job.get('metrics', {}),
        'continuity': continuity,
        'output_path': str(job.get('output_path', '')),
        'input_path': str(job.get('input_path', '')),
    }


def load_huddinge_v2_jobs() -> List[Dict[str, Any]]:
    """Load jobs from Huddinge v2 continuity analysis."""
    jobs = []

    # Load directly from metrics directory (manifest has failed jobs)
    metrics_dir = _HUDDINGE_V2_DIR / "metrics"

    # Look for run_summary files to find successful jobs
    run_summaries = list(metrics_dir.glob("run_summary_*.json"))

    for summary_path in run_summaries:
        try:
            with open(summary_path, encoding="utf-8") as f:
                summary = json.load(f)

            route_plan_id = summary.get('route_plan_id', '')
            if not route_plan_id:
                continue

            # Find corresponding metrics file
            metrics_pattern = f"metrics_*_{route_plan_id[:8]}*.json"
            metrics_files = list(metrics_dir.glob(metrics_pattern))

            # Use the latest metrics file if multiple exist
            if metrics_files:
                metrics_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                metrics = extract_metrics_from_json(metrics_files[0])
            else:
                metrics = {}

            # Load continuity
            continuity_csv = metrics_dir / "continuity.csv"
            continuity = load_continuity_csv(continuity_csv)

            # Create job name from route plan ID
            job_name = f"Huddinge 4mars v2 - {route_plan_id[:8]}"

            jobs.append({
                'env': 'test',
                'job_id': metrics.get('route_plan_id', route_plan_id),  # Use full ID from metrics
                'name': job_name,
                'status': metrics.get('solver_status', 'COMPLETED'),
                'score': metrics.get('score', ''),
                'metrics': metrics,
                'continuity': continuity,
                'output_path': '',
                'input_path': '',
            })

            print(f"  Loaded Huddinge v2 job: {route_plan_id[:8]}")

        except Exception as e:
            print(f"Error loading run summary {summary_path}: {e}", file=sys.stderr)
            continue

    return jobs


def generate_comprehensive_dashboard_data():
    """Generate complete dashboard data from ALL sources."""
    all_jobs = []

    # Load from batch test
    print("Loading test batch results...")
    test_jobs = load_batch_results('continuity_batch_test')
    for job in test_jobs:
        transformed = transform_job_data(job, 'test', 'continuity_batch_test')
        all_jobs.append(transformed)
    print(f"  Loaded {len(test_jobs)} test batch jobs")

    # Load from batch prod
    print("Loading prod batch results...")
    prod_jobs = load_batch_results('continuity_batch_prod')
    for job in prod_jobs:
        transformed = transform_job_data(job, 'prod', 'continuity_batch_prod')
        all_jobs.append(transformed)
    print(f"  Loaded {len(prod_jobs)} prod batch jobs")

    # Load from-patch results
    print("Loading from-patch results...")
    from_patch_folder = _ANALYSIS_DIR / 'continuity_batch_test' / '6d2d0476_from_patch'
    if from_patch_folder.exists():
        from_patch_output = from_patch_folder / 'output.json'
        if from_patch_output.exists():
            with open(from_patch_output, encoding='utf-8') as f:
                data = json.load(f)
                metadata = data.get('metadata', data.get('run', {}))

            # Extract metrics manually from output
            output_data = data.get('modelOutput', {})
            vehicles = output_data.get('vehicles', [])
            unassigned = output_data.get('unassignedVisits', [])

            assigned_visits = sum(len(v.get('visits', [])) for v in vehicles)
            total_shifts = sum(len(v.get('shifts', [])) for v in vehicles)
            empty_shifts = sum(1 for v in vehicles for s in v.get('shifts', []) if not s.get('visits'))

            metrics = {
                'visits_total': assigned_visits + len(unassigned),
                'visit_groups': 152,  # From known data
                'visits_assigned': assigned_visits,
                'visits_unassigned': len(unassigned),
                'vehicles_used': len(vehicles),
                'shifts_total': total_shifts,
                'shifts_no_visits': empty_shifts,
            }

            continuity = load_continuity_csv(from_patch_folder / 'continuity.csv')

            from_patch_job = {
                'env': 'test',
                'job_id': metadata.get('id', from_patch_output.stem.split('_')[0]),
                'name': metadata.get('name', 'from-patch-trim-empty'),
                'status': metadata.get('solverStatus', 'SOLVING_COMPLETED'),
                'score': str(metadata.get('score', '')),
                'metrics': metrics,
                'continuity': continuity,
                'output_path': str(from_patch_output),
                'input_path': str(from_patch_folder / 'input.json'),
            }
            all_jobs.append(from_patch_job)
            print(f"  Loaded from-patch job")

    # Load Huddinge v2 jobs
    print("Loading Huddinge v2 continuity jobs...")
    v2_jobs = load_huddinge_v2_jobs()
    all_jobs.extend(v2_jobs)
    print(f"  Loaded {len(v2_jobs)} Huddinge v2 jobs")

    # Generate summary stats
    summary = {
        'total_jobs': len(all_jobs),
        'test_jobs': sum(1 for j in all_jobs if j['env'] == 'test'),
        'prod_jobs': sum(1 for j in all_jobs if j['env'] == 'prod'),
        'perfect_continuity_jobs': sum(1 for j in all_jobs if j['continuity'].get('over_15', 999) == 0),
        'avg_continuity': sum(j['continuity'].get('avg_continuity', 0) for j in all_jobs if j['continuity'].get('avg_continuity')) / max(sum(1 for j in all_jobs if j['continuity'].get('avg_continuity')), 1),
        'total_visits': sum(j['metrics'].get('visits_total', 0) for j in all_jobs),
        'generated_at': datetime.now().isoformat(),
    }

    output_data = {
        'summary': summary,
        'jobs': all_jobs,
    }

    # Save to dashboard data file
    output_file = _ANALYSIS_DIR / 'dashboard_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Generated comprehensive dashboard data: {output_file}")
    print(f"  Total jobs: {len(all_jobs)}")
    print(f"  Test jobs: {summary['test_jobs']}")
    print(f"  Prod jobs: {summary['prod_jobs']}")
    print(f"  Perfect continuity: {summary['perfect_continuity_jobs']}")
    print(f"  Avg continuity: {summary['avg_continuity']:.1f}")

    return output_file


if __name__ == '__main__':
    from datetime import datetime
    generate_comprehensive_dashboard_data()
