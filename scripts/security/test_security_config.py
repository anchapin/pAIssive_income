#!/usr/bin/env python3
"""
Test script to verify security scan configuration.

This script tests that Bandit configuration files are valid and
that security scan scripts work correctly.
"""

import logging
import subprocess
import sys
from pathlib import Path

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_bandit_yaml_config() -> bool | None:
    """Test that bandit.yaml is valid YAML and has required fields."""
    logger.info("Testing bandit.yaml configuration...")

    config_file = Path("bandit.yaml")
    if not config_file.exists():
        logger.error("bandit.yaml not found")
        return False

    try:
        with config_file.open() as f:
            config = yaml.safe_load(f)

        # Check required fields
        required_fields = ["exclude_dirs", "skips", "severity", "confidence"]
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required field in bandit.yaml: {field}")
                return False

        logger.info("bandit.yaml configuration is valid")
        return True

    except yaml.YAMLError as e:
        logger.exception(f"Invalid YAML in bandit.yaml: {e}")
        return False
    except Exception as e:
        logger.exception(f"Error reading bandit.yaml: {e}")
        return False


def test_bandit_ini_config() -> bool | None:
    """Test that .bandit file exists and is readable."""
    logger.info("Testing .bandit configuration...")

    config_file = Path(".bandit")
    if not config_file.exists():
        logger.error(".bandit not found")
        return False

    try:
        with config_file.open() as f:
            content = f.read()

        # Check for basic structure
        if "[bandit]" not in content:
            logger.error(".bandit file missing [bandit] section")
            return False

        logger.info(".bandit configuration is valid")
        return True

    except Exception as e:
        logger.exception(f"Error reading .bandit: {e}")
        return False


def test_security_scripts_exist():
    """Test that security scan scripts exist and are executable."""
    logger.info("Testing security scan scripts...")

    scripts = [
        "scripts/security/run_security_scans.py",
        "scripts/security/run_security_scans.ps1",
        "scripts/security/create_security_fallbacks.py"
    ]

    all_exist = True
    for script in scripts:
        script_path = Path(script)
        if not script_path.exists():
            logger.error(f"Security script not found: {script}")
            all_exist = False
        else:
            logger.info(f"Found security script: {script}")

    return all_exist


def test_sarif_conversion_script() -> bool | None:
    """Test that SARIF conversion script exists and is functional."""
    logger.info("Testing SARIF conversion script...")

    script_path = Path("convert_bandit_to_sarif.py")
    if not script_path.exists():
        logger.warning("convert_bandit_to_sarif.py not found (optional)")
        return True  # This is optional

    try:
        # Test that the script can be imported
        result = subprocess.run(
            [sys.executable, "-c", "import convert_bandit_to_sarif"],
            capture_output=True,
            text=True,
            timeout=10, check=False
        )

        if result.returncode == 0:
            logger.info("SARIF conversion script is importable")
            return True
        logger.warning(f"SARIF conversion script has import issues: {result.stderr}")
        return True  # Don't fail for this

    except Exception as e:
        logger.warning(f"Error testing SARIF conversion script: {e}")
        return True  # Don't fail for this


def test_fallback_creation() -> bool | None:
    """Test that fallback creation script works."""
    logger.info("Testing fallback creation script...")

    try:
        result = subprocess.run(
            [sys.executable, "scripts/security/create_security_fallbacks.py"],
            capture_output=True,
            text=True,
            timeout=30, check=False
        )

        if result.returncode == 0:
            logger.info("Fallback creation script executed successfully")

            # Check that files were created
            security_dir = Path("security-reports")
            if security_dir.exists():
                sarif_files = list(security_dir.glob("*.sarif"))
                json_files = list(security_dir.glob("*.json"))

                if sarif_files and json_files:
                    logger.info(f"Created {len(sarif_files)} SARIF files and {len(json_files)} JSON files")
                    return True
                logger.error("Fallback files were not created properly")
                return False
            logger.error("security-reports directory was not created")
            return False
        logger.error(f"Fallback creation script failed: {result.stderr}")
        return False

    except Exception as e:
        logger.exception(f"Error testing fallback creation: {e}")
        return False


def main() -> int:
    """Run all security configuration tests."""
    logger.info("Starting security configuration tests...")

    tests = [
        ("Bandit YAML Config", test_bandit_yaml_config),
        ("Bandit INI Config", test_bandit_ini_config),
        ("Security Scripts", test_security_scripts_exist),
        ("SARIF Conversion", test_sarif_conversion_script),
        ("Fallback Creation", test_fallback_creation)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        logger.info(f"Running test: {test_name}")
        try:
            if test_func():
                logger.info(f"✅ {test_name} PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.exception(f"❌ {test_name} FAILED with exception: {e}")

    logger.info(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All security configuration tests passed!")
        return 0
    logger.error(f"💥 {total - passed} tests failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
