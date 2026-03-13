#!/usr/bin/env python3
"""
Generate dashboard data JSON from Timefold job analysis results.
Combines data from batch analysis and creates a comprehensive dataset for the web dashboard.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent.parent
_ANALYSIS_DIR = _REPO_ROOT / "analysis"


def load_batch_results(batch_folder: str) -> List[Dict[str, Any]]:
    """Load batch_results.json from a continuity batch folder."""
    batch_path = _ANALYSIS_DIR / batch_folder / "batch_results.json"
    if not batch_path.exists():
        print(f"Warning: {batch_path} not found", file=sys.stderr)
        return []

    with open(batch_path, encoding="utf-8") as f:
        return json.load(f)


def load_continuity_csv_summary(job_folder: Path) -> Dict[str, Any]:
    """Parse continuity CSV and return summary stats."""
    continuity_csv = job_folder / "continuity.csv"
    if not continuity_csv.exists():
        return {}

    try:
        import csv
        with open(continuity_csv, encoding="utf-8") as f:
            reader = csv.DictReader(f)
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
        print(f"Error parsing continuity CSV {continuity_csv}: {e}", file=sys.stderr)
        return {}


def extract_metrics_from_output(output_path: Path) -> Dict[str, Any]:
    """Extract key metrics from output.json."""
    if not output_path.exists():
        return {}

    try:
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)

        metadata = data.get('metadata', data.get('run', {}))
        model_output = data.get('modelOutput', {})
        model_input = data.get('modelInput', {})

        vehicles = model_output.get('vehicles', [])
        unassigned = model_output.get('unassignedVisits', [])

        # Count visits
        assigned_visits = 0
        for vehicle in vehicles:
            assigned_visits += len(vehicle.get('visits', []))

        # Count empty shifts
        empty_shifts = 0
        total_shifts = 0
        for vehicle in vehicles:
            for shift in vehicle.get('shifts', []):
                total_shifts += 1
                if not shift.get('visits'):
                    empty_shifts += 1

        # Get input counts
        input_visits = len(model_input.get('visits', [])) if model_input else 0
        input_groups = len(model_input.get('visitGroups', [])) if model_input else 0
        input_vehicles = len(model_input.get('vehicles', [])) if model_input else 0

        return {
            'visits_total': assigned_visits + len(unassigned),
            'visit_groups': input_groups,
            'visits_assigned': assigned_visits,
            'visits_unassigned': len(unassigned),
            'vehicles_used': len(vehicles),
            'vehicles_total': input_vehicles,
            'shifts_total': total_shifts,
            'shifts_no_visits': empty_shifts,
            'solver_status': metadata.get('solverStatus', ''),
            'score': metadata.get('score', ''),
        }
    except Exception as e:
        print(f"Error extracting metrics from {output_path}: {e}", file=sys.stderr)
        return {}


def transform_job_data(job: Dict[str, Any], env: str, batch_folder: str) -> Dict[str, Any]:
    """Transform job data from batch_results format to dashboard format."""
    job_id = job.get('job_id', 'unknown')
    job_folder = _ANALYSIS_DIR / batch_folder / job_id[:8]

    # Load additional data from files
    output_path = job_folder / "output.json"
    metrics_from_output = extract_metrics_from_output(output_path)
    continuity_summary = load_continuity_csv_summary(job_folder)

    # Merge metrics
    metrics = job.get('metrics', {})
    metrics.update(metrics_from_output)

    # Merge continuity
    continuity = job.get('continuity', {})
    continuity.update(continuity_summary)

    return {
        'env': env,
        'job_id': job_id,
        'name': job.get('name', ''),
        'status': job.get('status', ''),
        'score': job.get('score', ''),
        'metrics': metrics,
        'continuity': continuity,
        'output_path': str(job.get('output_path', '')),
        'input_path': str(job.get('input_path', '')),
    }


def generate_dashboard_data():
    """Generate complete dashboard data from all batch results."""
    all_jobs = []

    # Load test environment jobs
    test_jobs = load_batch_results('continuity_batch_test')
    for job in test_jobs:
        transformed = transform_job_data(job, 'test', 'continuity_batch_test')
        all_jobs.append(transformed)

    # Load prod environment jobs
    prod_jobs = load_batch_results('continuity_batch_prod')
    for job in prod_jobs:
        transformed = transform_job_data(job, 'prod', 'continuity_batch_prod')
        all_jobs.append(transformed)

    # Also load from-patch results if they exist
    from_patch_folder = _ANALYSIS_DIR / 'continuity_batch_test' / '6d2d0476_from_patch'
    if from_patch_folder.exists():
        from_patch_output = from_patch_folder / 'output.json'
        if from_patch_output.exists():
            metrics = extract_metrics_from_output(from_patch_output)
            continuity = load_continuity_csv_summary(from_patch_folder)

            with open(from_patch_output, encoding='utf-8') as f:
                data = json.load(f)
                metadata = data.get('metadata', data.get('run', {}))

            from_patch_job = {
                'env': 'test',
                'job_id': from_patch_output.stem.split('_')[0],
                'name': metadata.get('name', 'from-patch-trim-empty'),
                'status': metadata.get('solverStatus', 'SOLVING_COMPLETED'),
                'score': metadata.get('score', ''),
                'metrics': metrics,
                'continuity': continuity,
                'output_path': str(from_patch_output),
                'input_path': str(from_patch_folder / 'input.json'),
            }
            all_jobs.append(from_patch_job)

    # Generate summary stats
    summary = {
        'total_jobs': len(all_jobs),
        'test_jobs': sum(1 for j in all_jobs if j['env'] == 'test'),
        'prod_jobs': sum(1 for j in all_jobs if j['env'] == 'prod'),
        'perfect_continuity_jobs': sum(1 for j in all_jobs if j['continuity'].get('over_15', 999) == 0),
        'avg_continuity': sum(j['continuity'].get('avg_continuity', 0) for j in all_jobs) / len(all_jobs) if all_jobs else 0,
        'total_visits': sum(j['metrics'].get('visits_total', 0) for j in all_jobs),
        'generated_at': Path(__file__).name,
    }

    output_data = {
        'summary': summary,
        'jobs': all_jobs,
    }

    # Save to dashboard data file
    output_file = _ANALYSIS_DIR / 'dashboard_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Generated dashboard data: {output_file}")
    print(f"  Total jobs: {len(all_jobs)}")
    print(f"  Test jobs: {summary['test_jobs']}")
    print(f"  Prod jobs: {summary['prod_jobs']}")
    print(f"  Perfect continuity: {summary['perfect_continuity_jobs']}")

    return output_file


if __name__ == '__main__':
    generate_dashboard_data()
