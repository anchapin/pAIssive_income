"""run_tests.py - Phased test runner for the pAIssive Income project.

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

import argparse
import subprocess
import sys


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


def main():
    """Parse arguments and run the appropriate pytest command with markers."""
    parser = argparse.ArgumentParser(
        description="Phased test runner for the pAIssive Income project"
    )
    parser.add_argument(
        "--phase",
        default="fast",
        choices=list(PHASE_MARKERS.keys()) + ["custom"],
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
        "extra_pytest_args",
        nargs=argparse.REMAINDER,
        help="Extra arguments to pass to pytest (e.g., -k, --maxfail, etc.)",
    )

    args = parser.parse_args()
    phase = args.phase

    if phase == "custom":
        if not args.marker:
            print(
                "ERROR: --phase custom requires a marker expression with --marker/-m."
            )
            return 2
        marker_expr = args.marker
    else:
        marker_expr = PHASE_MARKERS[phase]

    pytest_cmd = [sys.executable, "-m", "pytest"]
    if marker_expr:
        pytest_cmd += ["-m", marker_expr]
    if args.extra_pytest_args:
        pytest_cmd += args.extra_pytest_args

    print(f"Running tests with phase: {phase}")
    if marker_expr:
        print(f"Pytest marker expression: {marker_expr}")
    if args.extra_pytest_args:
        print(f"Extra pytest args: {' '.join(args.extra_pytest_args)}")

    try:
        result = subprocess.run(pytest_cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("Test run interrupted by user.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
