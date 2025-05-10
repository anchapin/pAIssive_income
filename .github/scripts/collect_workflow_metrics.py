"""collect_workflow_metrics - Module for github/scripts.collect_workflow_metrics."""

# Standard library imports
import argparse
import json

# Third-party imports
# None required for basic functionality
# Local imports
# None required for basic functionality
import logging
import re

from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def validate_input(input_str: str, pattern: str, default_value: str) -> str:
    """Validate input string against a regex pattern.

    Args:
    ----
        input_str: The input string to validate
        pattern: Regex pattern to validate against
        default_value: Default value to return if validation fails

    Returns:
    -------
        str: Validated input or default value
    """
    if not input_str or not re.match(pattern, input_str):
        logging.warning(f"Invalid input detected: {input_str}. Using default value.")
        return default_value
    return input_str


def collect_metrics(
    workflow: str,
    status: str,
    duration: str,
    branch: str,
    commit: str,
    output_file: str,
) -> None:
    """Collect and save workflow metrics.

    Args:
    ----
        workflow: Name of the workflow
        status: Conclusion status of the workflow
        duration: Duration of the workflow in seconds
        branch: Branch name
        commit: Commit SHA
        output_file: Path to output JSON file
    """
    # Validate inputs
    workflow = validate_input(workflow, r"^[a-zA-Z0-9_\-\s]+$", "unknown-workflow")
    status = validate_input(status, r"^[a-zA-Z0-9_\-]+$", "unknown")

    # Validate duration is a number
    try:
        duration_int = int(duration)
    except (ValueError, TypeError):
        logging.warning(f"Invalid duration: {duration}. Using 0.")
        duration_int = 0

    # Validate branch name
    branch = validate_input(branch, r"^[a-zA-Z0-9_\-\/]+$", "unknown-branch")

    # Validate commit SHA
    commit = validate_input(commit, r"^[a-f0-9]{40}$", "unknown-commit")

    # Create metrics data
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "workflow": workflow,
        "status": status,
        "duration": duration_int,
        "branch": branch,
        "commit": commit,
    }

    # Save to file
    with open(output_file, "w") as f:
        json.dump(metrics, f, indent=2)

    logging.info(f"Metrics saved to {output_file}")


def main() -> None:
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
