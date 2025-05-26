"""Advanced security test runner for the pAIssive income platform."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

# Configure logging with secure defaults
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message).100s",  # Limit message length
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("security_tests.log", mode="w"),  # Overwrite old logs
    ],
)
logger = logging.getLogger(__name__)

# Import test modules (these must be in PYTHONPATH)
from tests.security.test_advanced_authentication import TestAdvancedAuthentication
from tests.security.test_authorization_edge_cases import TestAuthorizationEdgeCases
from tests.security.test_security_scan import TestSecurityScan


class SecurityTestRunner:
    """Runner for security test suites."""

    def __init__(self) -> None:
        """Initialize test runner."""
        self.test_suites: list[type[unittest.TestCase]] = [
            TestAdvancedAuthentication,
            TestAuthorizationEdgeCases,
            TestSecurityScan,
        ]
        self.skipped_tests: set[str] = set()
        self.failed_tests: set[str] = set()
        self.duration: float | None = None

    def setup_test_environment(self) -> None:
        """Set up the test environment with secure defaults."""
        # Set secure environment defaults
        os.environ["PYTHONHASHSEED"] = "1"  # Deterministic hashes
        os.environ["PYTHONWARNINGS"] = "default"  # Show all warnings
        os.environ["PYTHONDEVMODE"] = "1"  # Development mode checks

        # Create secure test directories
        Path("test-results").mkdir(exist_ok=True)
        Path("test-artifacts").mkdir(exist_ok=True)

    def cleanup_test_environment(self) -> None:
        """Clean up the test environment."""
        try:
            # Clean up test artifacts
            for path in Path("test-artifacts").glob("*"):
                if path.is_file():
                    path.unlink()
        except Exception:
            logger.exception("Error cleaning up test environment")

    def run_test_suite(self, test_suite: type[unittest.TestCase]) -> bool:
        """Run a test suite and handle results."""
        logger.info("\nRunning test suite: %s", test_suite.__name__)
        try:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_suite)
            runner = unittest.TextTestRunner(
                verbosity=2,
                failfast=False,
                buffer=True,  # Capture stdout/stderr
            )
            result = runner.run(suite)

            # Handle skipped tests
            for test, reason in result.skipped:
                test_name = f"{test_suite.__name__}.{test._testMethodName}"
                self.skipped_tests.add(test_name)
                logger.warning("Skipped test %s: %s", test_name, reason)

            # Handle failed tests
            for test, traceback in result.failures + result.errors:
                test_name = f"{test_suite.__name__}.{test._testMethodName}"
                self.failed_tests.add(test_name)
                logger.error("Test %s failed:\n%s", test_name, traceback)

            return result.wasSuccessful()

        except Exception:
            logger.exception("Error running test suite %s", test_suite.__name__)
            return False

    async def run_async_tests(self) -> bool:
        """Run async test suites."""
        try:
            success = True
            for suite in self.test_suites:
                # Check if suite has async tests
                has_async = any(
                    callable(getattr(suite, name))
                    and asyncio.iscoroutinefunction(getattr(suite, name))
                    for name in dir(suite)
                    if name.startswith("test_")
                )

                if has_async:
                    # Create event loop for async tests
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        success &= await self._run_async_suite(suite)
                    finally:
                        loop.close()
                else:
                    success &= self.run_test_suite(suite)

            return success

        except Exception:
            logger.exception("Error running async tests")
            return False

    async def _run_async_suite(self, suite: type[unittest.TestCase]) -> bool:
        """Run an async test suite."""
        try:
            test_instance = suite()
            if hasattr(test_instance, "asyncSetUp"):
                await test_instance.asyncSetUp()

            success = True
            for name in dir(suite):
                if name.startswith("test_") and asyncio.iscoroutinefunction(
                    getattr(suite, name)
                ):
                    try:
                        await getattr(test_instance, name)()
                    except Exception:
                        test_name = f"{suite.__name__}.{name}"
                        self.failed_tests.add(test_name)
                        logger.exception("Async test %s failed", test_name)
                        success = False

            if hasattr(test_instance, "asyncTearDown"):
                await test_instance.asyncTearDown()

            return success

        except Exception:
            logger.exception("Error running async suite %s", suite.__name__)
            return False

    def generate_report(self) -> None:
        """Generate test execution report."""
        report_path = Path("test-results") / "security_test_report.txt"
        try:
            with report_path.open("w") as f:
                f.write("Security Test Report\n")
                f.write("===================\n\n")
                f.write(f"Date: {datetime.now(tz=timezone.utc)}\n")
                f.write(f"Duration: {self.duration:.2f} seconds\n\n")

                f.write("Test Suites:\n")
                for suite in self.test_suites:
                    f.write(f"- {suite.__name__}\n")

                if self.skipped_tests:
                    f.write("\nSkipped Tests:\n")
                    for test in sorted(self.skipped_tests):
                        f.write(f"- {test}\n")

                if self.failed_tests:
                    f.write("\nFailed Tests:\n")
                    for test in sorted(self.failed_tests):
                        f.write(f"- {test}\n")

        except Exception:
            logger.exception("Error generating report")

    def run(self) -> int:
        """
        Run all security tests.

        Returns:
            int: 0 for success, 1 for failure

        """
        start_time = datetime.now(tz=timezone.utc)
        success = True

        try:
            # Set up
            self.setup_test_environment()

            # Run tests
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(self.run_async_tests())
            finally:
                loop.close()

        except KeyboardInterrupt:
            logger.info("\nTest execution interrupted by user.")
            success = False

        except Exception:
            logger.exception("Error during test execution")
            success = False

        finally:
            # Calculate duration and generate report
            self.duration = (datetime.now(tz=timezone.utc) - start_time).total_seconds()
            self.generate_report()

            # Clean up
            self.cleanup_test_environment()

            # Log summary
            logger.info("\nTest Execution Summary:")
            logger.info("Duration: %.2f seconds", self.duration)
            logger.info("Skipped Tests: %d", len(self.skipped_tests))
            logger.info("Failed Tests: %d", len(self.failed_tests))
            logger.info("Overall Status: %s", "PASSED" if success else "FAILED")

        return 0 if success else 1


def main() -> int:
    """
    Run the main entry point.

    Returns:
        int: Exit code (0 for success, 1 for failure)

    """
    parser = argparse.ArgumentParser(description="Run advanced security tests")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    runner = SecurityTestRunner()
    return runner.run()


if __name__ == "__main__":
    sys.exit(main())
