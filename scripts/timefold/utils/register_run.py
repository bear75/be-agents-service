#!/usr/bin/env python3
"""
Register a Timefold solve run to the be-agent-service database.

This script is called after a solve completes to record metrics and results
in the schedule_runs table.

Usage:
    python scripts/timefold/utils/register_run.py \
        --job-id my_job_123 \
        --dataset huddinge-v3 \
        --metrics-file /tmp/metrics.json \
        --input-file recurring-visits/data/huddinge-v3/input/input.json \
        --output-file recurring-visits/data/huddinge-v3/output/solution.json

Environment:
    AGENT_SERVICE_URL - be-agent-service API URL (default: http://localhost:3010)
    DATASET - Default dataset name (default: huddinge-v3)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests library not installed. Run: pip install requests", file=sys.stderr)
    sys.exit(1)


def load_json(file_path):
    """Load JSON from file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def register_run(job_id, dataset, metrics, input_file=None, output_file=None, status='completed'):
    """Register run to be-agent-service database via API."""

    api_url = os.environ.get('AGENT_SERVICE_URL', 'http://localhost:3010')
    endpoint = f"{api_url}/api/schedule-runs/register"

    payload = {
        'job_id': job_id,
        'dataset': dataset,
        'status': status,
        'created_at': datetime.now().isoformat(),
    }

    # Add metrics if provided
    if metrics:
        payload.update({
            'efficiency': metrics.get('efficiency'),
            'continuity_avg': metrics.get('continuity_avg'),
            'continuity_max': metrics.get('continuity_max'),
            'unassigned_pct': metrics.get('unassigned_pct'),
            'unassigned_count': metrics.get('unassigned_count'),
            'total_distance': metrics.get('total_distance'),
            'total_duration': metrics.get('total_duration'),
            'total_shifts': metrics.get('total_shifts'),
            'total_visits': metrics.get('total_visits'),
            'over_continuity_target_count': metrics.get('over_continuity_target_count'),
        })

    # Add file paths if provided
    if input_file:
        payload['input_file'] = str(Path(input_file).resolve())
    if output_file:
        payload['output_file'] = str(Path(output_file).resolve())

    # POST to API
    try:
        response = requests.post(endpoint, json=payload, timeout=10)
        response.raise_for_status()

        result = response.json()
        print(f"✓ Run registered successfully: {result.get('id')}")
        return result

    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to register run: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Register Timefold solve run to be-agent-service database'
    )

    parser.add_argument(
        '--job-id',
        required=True,
        help='Timefold job ID'
    )

    parser.add_argument(
        '--dataset',
        default=os.environ.get('DATASET', 'huddinge-v3'),
        help='Dataset name (default: huddinge-v3 or $DATASET)'
    )

    parser.add_argument(
        '--metrics-file',
        help='Path to metrics JSON file'
    )

    parser.add_argument(
        '--metrics-json',
        help='Metrics as JSON string'
    )

    parser.add_argument(
        '--input-file',
        help='Path to FSR input file'
    )

    parser.add_argument(
        '--output-file',
        help='Path to solution output file'
    )

    parser.add_argument(
        '--status',
        default='completed',
        choices=['completed', 'failed', 'running'],
        help='Run status (default: completed)'
    )

    args = parser.parse_args()

    # Load metrics
    metrics = None
    if args.metrics_file:
        metrics = load_json(args.metrics_file)
    elif args.metrics_json:
        metrics = json.loads(args.metrics_json)

    # Register run
    register_run(
        job_id=args.job_id,
        dataset=args.dataset,
        metrics=metrics,
        input_file=args.input_file,
        output_file=args.output_file,
        status=args.status
    )


if __name__ == '__main__':
    main()
