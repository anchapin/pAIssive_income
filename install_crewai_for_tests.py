#!/usr/bin/env python3
"""
Install CrewAI and its dependencies for tests.
This script handles the installation of CrewAI with the correct dependency constraints
to avoid conflicts with other packages.
"""

import os
import sys
import subprocess
import logging
import platform

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

def install_crewai():
    """Install CrewAI with the correct dependency constraints."""
    logging.info("Installing CrewAI and its dependencies...")
    
    # Install dependency constraints first
    run_command([sys.executable, "-m", "pip", "install", "wrapt<2.0.0", "--no-deps"], check=False)
    run_command([sys.executable, "-m", "pip", "install", "deprecated>=1.2.6", "typing-extensions>=4.6.0"], check=False)
    run_command([sys.executable, "-m", "pip", "install", "opentelemetry-api>=1.30.0", "opentelemetry-sdk>=1.30.0", "--no-deps"], check=False)
    
    # Install CrewAI with relaxed dependencies
    run_command([sys.executable, "-m", "pip", "install", "crewai>=0.120.0", "--no-deps"], check=False)
    
    # Install additional dependencies that might be needed
    run_command([sys.executable, "-m", "pip", "install", "pydantic>=2.0.0", "langchain>=0.0.267"], check=False)
    
    # Verify installation
    try:
        import crewai
        logging.info(f"CrewAI installed successfully (version: {crewai.__version__})")
        return True
    except ImportError as e:
        logging.error(f"Failed to import CrewAI after installation: {e}")
        return False

def create_mock_crewai():
    """Create a mock CrewAI module for tests."""
    logging.info("Creating mock CrewAI module...")
    
    # Create a mock crewai package directory
    os.makedirs("mock_crewai", exist_ok=True)
    
    # Create __init__.py
    with open("mock_crewai/__init__.py", "w") as f:
        f.write("""
# Mock CrewAI module for tests
from .agent import Agent
from .task import Task
from .crew import Crew

__version__ = "0.120.0"
""")
    
    # Create agent.py
    with open("mock_crewai/agent.py", "w") as f:
        f.write("""
class Agent:
    def __init__(self, role="", goal="", backstory="", **kwargs):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.kwargs = kwargs
    
    def execute_task(self, task):
        return f"Executed task: {task.description}"
""")
    
    # Create task.py
    with open("mock_crewai/task.py", "w") as f:
        f.write("""
class Task:
    def __init__(self, description="", agent=None, **kwargs):
        self.description = description
        self.agent = agent
        self.kwargs = kwargs
""")
    
    # Create crew.py
    with open("mock_crewai/crew.py", "w") as f:
        f.write("""
class Crew:
    def __init__(self, agents=None, tasks=None, **kwargs):
        self.agents = agents or []
        self.tasks = tasks or []
        self.kwargs = kwargs
    
    def kickoff(self):
        return "Mock crew output"
""")
    
    # Add the mock_crewai directory to sys.path
    sys.path.insert(0, os.path.abspath("."))
    
    # Verify mock module
    try:
        import mock_crewai
        logging.info("Mock CrewAI module created successfully")
        return True
    except ImportError as e:
        logging.error(f"Failed to import mock CrewAI module: {e}")
        return False

def main():
    """Main function."""
    logging.info("Starting CrewAI installation for tests...")
    
    # Try to install CrewAI
    success = install_crewai()
    
    # If installation fails, create a mock module
    if not success:
        logging.warning("CrewAI installation failed, creating mock module...")
        create_mock_crewai()
    
    logging.info("CrewAI setup for tests completed")

if __name__ == "__main__":
    main()
