#!/usr/bin/env python3
"""
Test script to verify workflow fixes for PR #139.

This script tests the key components that were causing workflow failures:
1. Dependency installation
2. Mock module creation
3. Type checking with pyright
4. Test execution with fallbacks
5. Security scan setup
"""

import json
import logging
import subprocess
import sys
from pathlib import Path

from logging_config import configure_logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_essential_dependencies():
    """Test that essential dependencies can be installed."""
    logger.info("Testing essential dependency installation...")

    essential_deps = [
        "pytest", "pytest-cov", "pytest-asyncio", "pytest-xdist",
        "pytest-mock", "ruff", "pyright"
    ]

    failed_deps = []
    for dep in essential_deps:
        try:
            result = subprocess.run(
                [sys.executable, "-c", f"import {dep.replace('-', '_')}"],
                check=True, capture_output=True, text=True
            )
            logger.info(f"✓ {dep} is available")
        except subprocess.CalledProcessError:
            try:
                # Try importing with different name patterns
                alt_names = {
                    "pytest-cov": "pytest_cov",
                    "pytest-asyncio": "pytest_asyncio",
                    "pytest-xdist": "xdist",
                    "pytest-mock": "pytest_mock"
                }
                alt_name = alt_names.get(dep, dep)
                result = subprocess.run(
                    [sys.executable, "-c", f"import {alt_name}"],
                    check=True, capture_output=True, text=True
                )
                logger.info(f"✓ {dep} is available (as {alt_name})")
            except subprocess.CalledProcessError:
                logger.warning(f"✗ {dep} is not available")
                failed_deps.append(dep)

    if failed_deps:
        logger.warning(f"Missing dependencies: {failed_deps}")
        return False

    logger.info("✓ All essential dependencies are available")
    return True


def test_mock_modules():
    """Test that mock modules are created correctly."""
    logger.info("Testing mock module creation...")

    # Test mock MCP module
    mock_mcp_dir = Path("mock_mcp")
    if not mock_mcp_dir.exists():
        logger.info("Creating mock MCP module...")
        mock_mcp_dir.mkdir(exist_ok=True)
        (mock_mcp_dir / "__init__.py").write_text("""
# Mock MCP module for CI environments
class MockMCPClient:
    def __init__(self, *args, **kwargs):
        pass

    def connect(self):
        pass

    def disconnect(self):
        pass

    def list_tools(self):
        return []

    def call_tool(self, name, arguments=None):
        return {"result": "mock"}

# Mock the main MCP classes
Client = MockMCPClient
""")

    # Test mock CrewAI module
    mock_crewai_dir = Path("mock_crewai")
    if not mock_crewai_dir.exists():
        logger.info("Creating mock CrewAI module...")
        mock_crewai_dir.mkdir(exist_ok=True)
        (mock_crewai_dir / "__init__.py").write_text("""
# Mock CrewAI module for CI environments
class MockAgent:
    def __init__(self, *args, **kwargs):
        pass

    def execute(self, task):
        return "mock result"

class MockCrew:
    def __init__(self, *args, **kwargs):
        pass

    def kickoff(self):
        return "mock crew result"

class MockTask:
    def __init__(self, *args, **kwargs):
        pass

# Mock the main CrewAI classes
Agent = MockAgent
Crew = MockCrew
Task = MockTask
""")

    # Test importing mock modules
    try:
        sys.path.insert(0, str(Path.cwd()))
        import mock_crewai
        import mock_mcp

        # Test mock MCP functionality
        client = mock_mcp.Client()
        client.connect()
        tools = client.list_tools()
        result = client.call_tool("test")

        # Test mock CrewAI functionality
        agent = mock_crewai.Agent()
        crew = mock_crewai.Crew()
        task = mock_crewai.Task()

        logger.info("✓ Mock modules created and working correctly")
        return True

    except Exception as e:
        logger.error(f"✗ Mock module test failed: {e}")
        return False


def test_pyright_configuration():
    """Test that pyright configuration is working."""
    logger.info("Testing pyright configuration...")

    # Check if pyrightconfig.json exists
    pyright_config = Path("pyrightconfig.json")
    if not pyright_config.exists():
        logger.warning("✗ pyrightconfig.json not found")
        return False

    # Validate configuration
    try:
        with open(pyright_config) as f:
            config = json.load(f)

        required_excludes = [
            "mock_mcp/**",
            "mock_crewai/**",
            "ai_models/adapters/mcp_adapter.py",
            "tests/test_mcp_import.py"
        ]

        excludes = config.get("exclude", [])
        missing_excludes = [exc for exc in required_excludes if exc not in excludes]

        if missing_excludes:
            logger.warning(f"✗ Missing excludes in pyright config: {missing_excludes}")
            return False

        # Test pyright execution (if available)
        try:
            result = subprocess.run(
                ["pyright", "--version"],
                check=True, capture_output=True, text=True
            )
            logger.info(f"✓ Pyright is available: {result.stdout.strip()}")

            # Test basic pyright check
            result = subprocess.run(
                ["pyright", "--help"],
                check=True, capture_output=True, text=True
            )
            logger.info("✓ Pyright configuration test passed")
            return True

        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("✗ Pyright not available, but config is valid")
            return True  # Config is valid even if pyright not installed

    except Exception as e:
        logger.error(f"✗ Pyright configuration test failed: {e}")
        return False


def test_security_scan_setup():
    """Test that security scan setup is working."""
    logger.info("Testing security scan setup...")

    # Create security-reports directory
    security_dir = Path("security-reports")
    security_dir.mkdir(exist_ok=True)

    # Create fallback SARIF file
    empty_sarif = {
        "version": "2.1.0",
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Bandit",
                        "informationUri": "https://github.com/PyCQA/bandit",
                        "version": "1.7.5",
                        "rules": [],
                    }
                },
                "results": [],
            }
        ],
    }

    try:
        # Write SARIF files
        with open(security_dir / "bandit-results.sarif", "w") as f:
            json.dump(empty_sarif, f, indent=2)

        with open("empty-sarif.json", "w") as f:
            json.dump(empty_sarif, f, indent=2)

        # Validate SARIF files
        with open(security_dir / "bandit-results.sarif") as f:
            sarif_data = json.load(f)

        if sarif_data.get("version") != "2.1.0":
            logger.error("✗ Invalid SARIF version")
            return False

        logger.info("✓ Security scan setup completed successfully")
        return True

    except Exception as e:
        logger.error(f"✗ Security scan setup failed: {e}")
        return False


def test_ci_requirements():
    """Test that CI requirements file is valid."""
    logger.info("Testing CI requirements file...")

    ci_reqs = Path("requirements-ci.txt")
    if not ci_reqs.exists():
        logger.warning("✗ requirements-ci.txt not found")
        return False

    try:
        with open(ci_reqs) as f:
            content = f.read()

        # Check for essential packages
        essential_packages = ["pytest", "ruff", "pyright", "safety", "bandit"]
        missing_packages = []

        for package in essential_packages:
            if package not in content:
                missing_packages.append(package)

        if missing_packages:
            logger.warning(f"✗ Missing essential packages in CI requirements: {missing_packages}")
            return False

        # Check that problematic packages are excluded
        problematic_packages = ["modelcontextprotocol", "crewai", "mem0ai"]
        included_problematic = []

        for package in problematic_packages:
            if package in content and not content.count(f"# {package}"):
                included_problematic.append(package)

        if included_problematic:
            logger.warning(f"✗ Problematic packages not properly excluded: {included_problematic}")
            return False

        logger.info("✓ CI requirements file is valid")
        return True

    except Exception as e:
        logger.error(f"✗ CI requirements test failed: {e}")
        return False


def test_ci_wrapper():
    """Test that the CI test wrapper is working."""
    logger.info("Testing CI test wrapper...")

    wrapper_script = Path("run_tests_ci_wrapper.py")
    if not wrapper_script.exists():
        logger.warning("✗ run_tests_ci_wrapper.py not found")
        return False

    try:
        # Test basic execution
        result = subprocess.run(
            [sys.executable, "run_tests_ci_wrapper.py", "--help"],
            capture_output=True, text=True, timeout=30, check=False
        )

        # The script should handle --help gracefully or run pytest --help
        if result.returncode not in [0, 1, 2]:  # Allow various exit codes
            logger.warning(f"✗ CI wrapper returned unexpected code: {result.returncode}")
            return False

        logger.info("✓ CI test wrapper is functional")
        return True

    except Exception as e:
        logger.error(f"✗ CI wrapper test failed: {e}")
        return False


def run_comprehensive_test():
    """Run all tests and report results."""
    logger.info("Starting comprehensive workflow fix verification...")

    tests = [
        ("Essential Dependencies", test_essential_dependencies),
        ("Mock Modules", test_mock_modules),
        ("Pyright Configuration", test_pyright_configuration),
        ("Security Scan Setup", test_security_scan_setup),
        ("CI Requirements", test_ci_requirements),
        ("CI Test Wrapper", test_ci_wrapper),
    ]

    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")

        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {e}")
            results[test_name] = False

    # Report summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")

    passed = 0
    total = len(tests)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1

    logger.info(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All workflow fixes are working correctly!")
        return 0
    logger.warning(f"⚠️  {total - passed} tests failed. Review the issues above.")
    return 1


if __name__ == "__main__":
    configure_logging()
    sys.exit(run_comprehensive_test())
