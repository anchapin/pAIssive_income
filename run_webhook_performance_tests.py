"""
Script to run webhook performance tests.
"""

import argparse
import asyncio


async def run_performance_tests():
    """Run the webhook performance tests."""
    parser = argparse.ArgumentParser(description="Run webhook performance tests")
    parser.add_argument(
        "--test",
        choices=["performance", "load", "scalability", "all"],
        default="all",
        help="Which test to run",
    )

    args = parser.parse_args()

    if args.test == "performance" or args.test == "all":
        print("\n=== Running Performance Tests ===")
        from tests.performance.test_webhook_performance import run_performance_tests

        await run_performance_tests()

    if args.test == "load" or args.test == "all":
        print("\n=== Running Load Tests ===")
        from tests.performance.test_webhook_load import main as run_load_tests

        await run_load_tests()

    if args.test == "scalability" or args.test == "all":
        print("\n=== Running Scalability Tests ===")
        from tests.performance.test_webhook_scalability import run_scalability_tests

        await run_scalability_tests()


if __name__ == "__main__":
    asyncio.run(run_performance_tests())
