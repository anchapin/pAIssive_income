#!/usr/bin/env python3
"""
Run CrewAI-specific tests.
This script installs CrewAI and runs the tests that require it.
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_command(command, check=True, shell=False):
    """Run a command and return its output."""
    try:
        if isinstance(command, str) and not shell:
            command = command.split()
        
        logging.info(f"Running command: {command}")
        result = subprocess.run(
            command,
            check=check,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed with exit code {e.returncode}")
        logging.error(f"Error output: {e.stderr}")
        if check:
            raise
        return None

def main():
    """Main function."""
    logging.info("Starting CrewAI tests...")
    
    # First, install CrewAI
    logging.info("Installing CrewAI...")
    run_command([sys.executable, "install_crewai_for_tests.py"], check=False)
    
    # Run the CrewAI-specific tests
    logging.info("Running CrewAI tests...")
    result = run_command(
        [sys.executable, "-m", "pytest", "tests/test_crewai_agents.py", "-v"],
        check=False
    )
    
    logging.info("CrewAI tests completed")
    logging.info(f"Test results:\n{result}")

if __name__ == "__main__":
    main()
