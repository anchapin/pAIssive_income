"""collect_workflow_metrics - Module for github/scripts.collect_workflow_metrics."""

# Standard library imports
import argparse
import json
import re
from datetime import datetime

# Third-party imports
# None required for basic functionality

# Local imports
# None required for basic functionality


def validate_input(input_str, pattern, default_value):
    """Validate input string against a regex pattern.

    Args:
    ----
        input_str (str): The input string to validate
        pattern (str): Regex pattern to validate against
        default_value (str): Default value to return if validation fails

    Returns:
    -------
        str: Validated input or default value

    """
    if not input_str or not re.match(pattern, input_str):
        print(f"WARNING: Invalid input detected: {input_str}. Using default value.")
        return default_value
    return input_str


def collect_metrics(workflow, status, duration, branch, commit, output_file):
    """Collect and save workflow metrics.

    Args:
    ----
        workflow (str): Name of the workflow
        status (str): Conclusion status of the workflow
        duration (str): Duration of the workflow in seconds
        branch (str): Branch name
        commit (str): Commit SHA
        output_file (str): Path to output JSON file

    """
    # Validate inputs
    workflow = validate_input(workflow, r"^[a-zA-Z0-9_\-\s]+$", "unknown-workflow")
    status = validate_input(status, r"^[a-zA-Z0-9_\-]+$", "unknown")

    # Validate duration is a number
    try:
        duration = int(duration)
    except (ValueError, TypeError):
        print(f"WARNING: Invalid duration: {duration}. Using 0.")
        duration = 0

    # Validate branch name
    branch = validate_input(branch, r"^[a-zA-Z0-9_\-\/]+$", "unknown-branch")

    # Validate commit SHA
    commit = validate_input(commit, r"^[a-f0-9]{40}$", "unknown-commit")

    # Create metrics data
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "workflow": workflow,
        "status": status,
        "duration": duration,
        "branch": branch,
        "commit": commit,
    }

    # Save to file
    with open(output_file, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Metrics saved to {output_file}")


def main():
    """Implement the main entry point for the script."""
    parser = argparse.ArgumentParser(description="Collect workflow metrics")
    parser.add_argument("--workflow", required=True, help="Name of the workflow")
    parser.add_argument(
        "--status", required=True, help="Conclusion status of the workflow"
    )
    parser.add_argument(
        "--duration", required=True, help="Duration of the workflow in seconds"
    )
    parser.add_argument("--branch", required=True, help="Branch name")
    parser.add_argument("--commit", required=True, help="Commit SHA")
    parser.add_argument("--output", required=True, help="Path to output JSON file")

    args = parser.parse_args()

    collect_metrics(
        args.workflow, args.status, args.duration, args.branch, args.commit, args.output
    )


if __name__ == "__main__":
    main()
