"""
run_tests.py - Phased test runner for the pAIssive Income project.

Supports running test phases (fast/unit, integration, slow, all) using pytest markers.

Examples:
    python run_tests.py
        # Run fast tests (default: unit/smoke, excludes slow/integration/dependency)
    python run_tests.py --phase all
    python run_tests.py --phase integration
    python run_tests.py --phase slow
    python run_tests.py --phase security
    python run_tests.py --phase custom -m 'api or webhook'

"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys

# Third-party imports

PHASE_MARKERS = {
    "fast": "not slow and not integration and not dependency and not performance",
    "all": "",
    "unit": "unit",
    "integration": "integration",
    "slow": "slow",
    "security": "security",
    "model": "model",
    "performance": "performance",
    "api": "api",
    "webhook": "webhook",
    "smoke": "smoke",
    # Add more as needed
}

# Create a dedicated logger for this module
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main() -> int:
    """
    Parse arguments and run pytest with markers and coverage enforcement.

    Returns:
        Exit code from pytest execution.

    """
    parser = argparse.ArgumentParser(
        description="Phased test runner for the pAIssive Income project"
    )
    parser.add_argument(
        "--phase",
        default="fast",
        choices=[*list(PHASE_MARKERS.keys()), "custom"],
        help=(
            "Test phase to run. "
            "Default: fast (unit/smoke, excludes slow/integration/dependency). "
            "Other options: all, unit, integration, slow, security, model, "
            "performance, api, webhook, smoke, custom"
        ),
    )
    parser.add_argument(
        "-m",
        "--marker",
        default=None,
        help="Custom pytest marker expression (used only with --phase custom).",
    )
    parser.add_argument(
        "--with-coverage",
        action="store_true",
        help="Run tests with coverage and enforce minimum coverage threshold (90%)",
    )
    parser.add_argument(
        "extra_pytest_args",
        nargs=argparse.REMAINDER,
        help="Extra arguments to pass to pytest (e.g., -k, --maxfail, etc.)",
    )

    args = parser.parse_args()
    phase = args.phase

    if phase == "custom":
        if not args.marker:
            logger.error(
                "--phase custom requires a marker expression with --marker/-m."
            )
            return 2
        marker_expr = args.marker
    else:
        marker_expr = PHASE_MARKERS[phase]

    pytest_cmd = [sys.executable, "-m", "pytest"]
    if args.with_coverage:
        pytest_cmd += [
            "--cov=.",
            "--cov-report=term-missing",
            "--cov-report=xml",
            "--cov-fail-under=90",
        ]
    if marker_expr:
        pytest_cmd += ["-m", marker_expr]
    if args.extra_pytest_args:
        pytest_cmd += args.extra_pytest_args

    logger.info("Running tests with phase: %s", phase)
    if marker_expr:
        logger.info("Pytest marker expression: %s", marker_expr)
    if args.with_coverage:
        logger.info("Coverage reporting enabled (minimum threshold: 90%)")
    if args.extra_pytest_args:
        logger.info("Extra pytest args: %s", " ".join(args.extra_pytest_args))

    try:
        # Use a list of validated arguments for security
        result: subprocess.CompletedProcess = subprocess.run(
            pytest_cmd,
            check=False,
            capture_output=False,  # Allow output to be shown directly
            text=True,
        )
        return int(result.returncode)
    except KeyboardInterrupt:
        logger.info("Test run interrupted by user.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
