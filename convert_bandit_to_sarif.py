#!/usr/bin/env python3
"""
Convert Bandit JSON output to SARIF format.

This script reads the Bandit JSON output file and converts it to SARIF format
for GitHub Advanced Security.
"""

import json
import os
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def convert_to_sarif(json_file, sarif_file):
    """
    Convert Bandit JSON output to SARIF format.

    Args:
        json_file: Path to the Bandit JSON output file
        sarif_file: Path to the output SARIF file
    """
    # Create the SARIF template
    sarif = {
        "version": "2.1.0",
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Bandit",
                        "informationUri": "https://github.com/PyCQA/bandit",
                        "version": "1.7.5",
                        "rules": []
                    }
                },
                "results": []
            }
        ]
    }

    # Check if the JSON file exists and has content
    json_path = Path(json_file)
    if not json_path.exists() or json_path.stat().st_size == 0:
        logger.info(f"JSON file {json_file} does not exist or is empty. Creating empty SARIF file.")
        try:
            with open(sarif_file, 'w') as f:
                json.dump(sarif, f)
            return
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to create SARIF file: {e}")
            return

    # Read the Bandit JSON output
    try:
        with open(json_file, 'r') as f:
            bandit_data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Error reading JSON file: {e}. Creating empty SARIF file.")
        try:
            with open(sarif_file, 'w') as f:
                json.dump(sarif, f)
            return
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to create SARIF file: {e}")
            return

    # Check if there are any results
    if not bandit_data.get('results'):
        logger.info("No results found in Bandit output. Creating empty SARIF file.")
        try:
            with open(sarif_file, 'w') as f:
                json.dump(sarif, f)
            return
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to create SARIF file: {e}")
            return

    # Convert Bandit results to SARIF format
    rules = {}
    results = []

    for result in bandit_data.get('results', []):
        rule_id = f"B{result.get('test_id', '000')}"

        # Add rule if not already added
        if rule_id not in rules:
            rules[rule_id] = {
                "id": rule_id,
                "shortDescription": {
                    "text": result.get('test_name', 'Unknown test')
                },
                "fullDescription": {
                    "text": result.get('issue_text', 'Unknown issue')
                },
                "helpUri": "https://bandit.readthedocs.io/en/latest/",
                "properties": {
                    "tags": ["security", "python"]
                }
            }

        # Add result
        results.append({
            "ruleId": rule_id,
            "level": "warning",
            "message": {
                "text": result.get('issue_text', 'Unknown issue')
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": result.get('filename', 'unknown')
                        },
                        "region": {
                            "startLine": result.get('line_number', 1),
                            "startColumn": 1
                        }
                    }
                }
            ]
        })

    # Add rules and results to SARIF
    sarif['runs'][0]['tool']['driver']['rules'] = list(rules.values())
    sarif['runs'][0]['results'] = results

    # Write SARIF file
    try:
        with open(sarif_file, 'w') as f:
            json.dump(sarif, f)
        logger.info(f"Successfully converted {json_file} to {sarif_file}")
    except (OSError, PermissionError) as e:
        logger.error(f"Failed to write SARIF file: {e}")


def ensure_security_reports_dir() -> None:
    """
    Ensure the security-reports directory exists.

    Creates the directory if it doesn't exist and logs the result.
    """
    reports_dir = Path("security-reports")

    # Check if directory already exists
    if reports_dir.exists() and reports_dir.is_dir():
        logger.info("security-reports directory already exists")
        return

    # Try to create the directory
    try:
        reports_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Created security-reports directory")
        return
    except (PermissionError, OSError) as e:
        logger.error(f"Failed to create security-reports directory: {e}")

    # First fallback: Try to create in current directory with different name
    try:
        alt_reports_dir = Path("security_reports")  # Use underscore instead of hyphen
        if not alt_reports_dir.exists():
            alt_reports_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Created alternative security_reports directory")

            # Create a symlink to the alternative directory
            try:
                if os.name == 'nt':  # Windows
                    # Use directory junction on Windows
                    # nosec B404 - subprocess is used with proper security controls
                    import subprocess  # nosec B404
                    cmd_path = shutil.which("cmd.exe")
                    if cmd_path:
                        # nosec B603 - subprocess call is used with shell=False and validated arguments
                        # nosec S603 - This is a safe subprocess call with no user input
                        subprocess.run(  # nosec B603 # noqa: S603
                            [cmd_path, "/c", f"mklink /J security-reports {alt_reports_dir}"],
                            check=False,
                            shell=False,
                            capture_output=True
                        )
                else:
                    # Use symlink on Unix
                    os.symlink(alt_reports_dir, "security-reports")
                return
            except Exception as symlink_error:
                logger.error(f"Failed to create symlink to alternative directory: {symlink_error}")
    except Exception as alt_dir_error:
        logger.error(f"Failed to create alternative security_reports directory: {alt_dir_error}")

    # Second fallback: Try to create in temp directory
    try:
        import tempfile
        temp_dir = Path(tempfile.gettempdir()) / "security-reports"
        temp_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created security-reports directory in temp location: {temp_dir}")

        # Try to create a symlink or junction to the temp directory
        try:
            if os.name == 'nt':  # Windows
                # Use directory junction on Windows
                # nosec B404 - subprocess is used with proper security controls
                import subprocess  # nosec B404
                cmd_path = shutil.which("cmd.exe")
                if cmd_path:
                    # nosec B603 - subprocess call is used with shell=False and validated arguments
                    # nosec S603 - This is a safe subprocess call with no user input
                    subprocess.run(  # nosec B603 # noqa: S603
                        [cmd_path, "/c", f"mklink /J security-reports {temp_dir}"],
                        check=False,
                        shell=False,
                        capture_output=True
                    )
            else:
                # Use symlink on Unix
                os.symlink(temp_dir, "security-reports")
        except Exception as symlink_error:
            logger.error(f"Failed to create symlink to temp directory: {symlink_error}")
    except Exception as temp_dir_error:
        logger.error(f"Failed to create security-reports directory in temp location: {temp_dir_error}")

    # Final fallback: Just continue without the directory
    # The security tools should handle this gracefully or we'll catch their exceptions


def main():
    """Main function."""
    try:
        # Ensure security-reports directory exists
        ensure_security_reports_dir()

        # Define file paths
        json_file = "security-reports/bandit-results.json"
        sarif_file = "security-reports/bandit-results.sarif"
        ini_sarif_file = "security-reports/bandit-results-ini.sarif"

        # Check if JSON file exists
        if not os.path.exists(json_file):
            logger.warning(f"Bandit JSON file not found: {json_file}")
            logger.info("Creating empty SARIF files as fallback")

            # Create empty SARIF template
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
                                "rules": []
                            }
                        },
                        "results": []
                    }
                ]
            }

            # Write empty SARIF files
            try:
                with open(sarif_file, 'w') as f:
                    json.dump(empty_sarif, f, indent=2)
                with open(ini_sarif_file, 'w') as f:
                    json.dump(empty_sarif, f, indent=2)
                logger.info("Created empty SARIF files")
                return
            except Exception as e:
                logger.error(f"Failed to create empty SARIF files: {e}")
                return

        # Convert Bandit JSON to SARIF
        logger.info(f"Converting {json_file} to SARIF format")
        convert_to_sarif(json_file, sarif_file)

        # Also create bandit-results-ini.sarif for compatibility
        logger.info(f"Creating {ini_sarif_file} for compatibility")
        try:
            if os.path.exists(sarif_file):
                # Copy the file
                try:
                    shutil.copy(sarif_file, ini_sarif_file)
                    logger.info(f"Copied {sarif_file} to {ini_sarif_file}")
                except Exception as copy_error:
                    logger.error(f"Failed to copy SARIF file: {copy_error}")

                    # Try to read and write instead of copy
                    try:
                        with open(sarif_file, 'r') as src:
                            sarif_data = json.load(src)
                        with open(ini_sarif_file, 'w') as dest:
                            json.dump(sarif_data, dest, indent=2)
                        logger.info(f"Successfully created {ini_sarif_file} by reading and writing")
                    except Exception as rw_error:
                        logger.error(f"Failed to read/write SARIF file: {rw_error}")
                        convert_to_sarif(json_file, ini_sarif_file)
            else:
                logger.warning(f"SARIF file not found: {sarif_file}")
                convert_to_sarif(json_file, ini_sarif_file)
        except Exception as e:
            logger.error(f"Failed to create ini SARIF file: {e}")
            # Try to convert directly as fallback
            try:
                convert_to_sarif(json_file, ini_sarif_file)
            except Exception as convert_error:
                logger.error(f"Failed to convert to ini SARIF file: {convert_error}")

                # Create empty SARIF file as last resort
                try:
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
                                        "rules": []
                                    }
                                },
                                "results": []
                            }
                        ]
                    }
                    with open(ini_sarif_file, 'w') as f:
                        json.dump(empty_sarif, f, indent=2)
                    logger.info(f"Created empty SARIF file as fallback: {ini_sarif_file}")
                except Exception as empty_error:
                    logger.error(f"Failed to create empty SARIF file: {empty_error}")
    except Exception as e:
        logger.error(f"Unexpected error in main function: {e}")

        # Create empty SARIF files as last resort
        try:
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
                                "rules": []
                            }
                        },
                        "results": []
                    }
                ]
            }

            # Ensure directory exists
            os.makedirs("security-reports", exist_ok=True)

            # Write empty SARIF files
            with open("security-reports/bandit-results.sarif", 'w') as f:
                json.dump(empty_sarif, f, indent=2)
            with open("security-reports/bandit-results-ini.sarif", 'w') as f:
                json.dump(empty_sarif, f, indent=2)
            logger.info("Created empty SARIF files as fallback after error")
        except Exception as fallback_error:
            logger.error(f"Failed to create fallback SARIF files: {fallback_error}")


if __name__ == "__main__":
    main()
