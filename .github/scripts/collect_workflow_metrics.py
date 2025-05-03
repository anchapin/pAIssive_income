#!/usr/bin/env python3
"""
Script to collect GitHub Actions workflow metrics.

This script collects metrics about GitHub Actions workflow runs and stores them
in a JSON file for later analysis and visualization.
"""

import argparse
import datetime
import json
import os
import sys


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Collect GitHub Actions workflow metrics")
    parser.add_argument("--workflow", required=True, help="Name of the workflow")
    parser.add_argument("--status", required=True, help="Status of the workflow run")
    parser.add_argument("--duration", required=True, help="Duration of the workflow run")
    parser.add_argument("--branch", required=True, help="Branch name")
    parser.add_argument("--commit", required=True, help="Commit SHA")
    parser.add_argument("--output", required=True, help="Output file path")
    return parser.parse_args()


def load_existing_metrics(file_path):
    """Load existing metrics from file if it exists."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Could not parse existing metrics file {file_path}")
            return {"workflows": []}
    return {"workflows": []}


def save_metrics(metrics, file_path):
    """Save metrics to file."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

    with open(file_path, "w") as f:
        json.dump(metrics, f, indent=2)


def main():
    """Main function."""
    args = parse_args()

    # Parse duration string to seconds
    try:
        duration_seconds = float(args.duration)
    except ValueError:
        print(f"Error: Could not parse duration '{args.duration}' as a number")
        duration_seconds = 0

    # Create metrics entry
    timestamp = datetime.datetime.now().isoformat()
    metrics_entry = {
        "timestamp": timestamp,
        "workflow": args.workflow,
        "status": args.status,
        "duration_seconds": duration_seconds,
        "branch": args.branch,
        "commit": args.commit
    }

    # Load existing metrics
    metrics = load_existing_metrics(args.output)

    # Add new entry
    metrics["workflows"].append(metrics_entry)

    # Save updated metrics
    save_metrics(metrics, args.output)

    print(f"Metrics saved to {args.output}")

    # Exit with status code based on workflow status
    if args.status.lower() != "success":
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
