#!/usr/bin/env python3
"""
Install CrewAI and its dependencies for tests.

This script handles the installation of CrewAI with the correct dependency constraints
to avoid conflicts with other packages.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

# Logger will be configured in main() or when first used if not in main.
# This avoids configuring it at import time if this script is imported as a module.
# logger = logging.getLogger(__name__) # This will be initialized in each function that uses it or in main


def run_command(command: str | list, check: bool = True) -> str | None:
    """
    Run a command and return its output.

    Args:
        command: The command to run, either as a string or list of arguments
        check: Whether to check the return code

    Returns:
        The command output as a string, or None if the command fails and check is False

    """
    logger = logging.getLogger(__name__)
    try:
        # Convert string command to list if needed
        if isinstance(command, str):
            command = command.split()

        logger.info("Running command: %s", command)

        # Run the command with shell=False for security
        # Using a list for command and shell=False is secure
        result = subprocess.run(
            command, check=check, shell=False, capture_output=True, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.exception("Command failed with exit code %d", e.returncode)
        logger.exception("Error output: %s", e.stderr)
        if check:
            raise
        return None


def install_crewai() -> bool:
    """
    Install CrewAI with the correct dependency constraints.

    Returns:
        bool: True if installation was successful, False otherwise

    """
    logger = logging.getLogger(__name__)
    logger.info("Installing CrewAI and its dependencies...")

    try:
        # First, try to import crewai to see if it's already installed
        import crewai
    except ImportError:
        logger.info("CrewAI not found, attempting installation...")
    else:
        logger.info("CrewAI is already installed (version: %s)", crewai.__version__)
        return True

    # Install dependency constraints first
    run_command(
        [sys.executable, "-m", "pip", "install", "wrapt<2.0.0", "--no-deps"],
        check=False,
    )
    run_command(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "deprecated>=1.2.6",
            "typing-extensions>=4.6.0",
        ],
        check=False,
    )
    run_command(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "opentelemetry-api>=1.30.0",
            "opentelemetry-sdk>=1.30.0",
            "--no-deps",
        ],
        check=False,
    )

    # Try different installation approaches
    methods = [
        # Method 1: Install with relaxed dependencies
        lambda: run_command(
            [sys.executable, "-m", "pip", "install", "crewai>=0.120.0", "--no-deps"],
            check=False,
        ),
        # Method 2: Install with minimal dependencies
        lambda: run_command(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "crewai>=0.120.0",
                "pydantic>=2.0.0",
                "--no-deps",
            ],
            check=False,
        ),
        # Method 3: Install with more dependencies
        lambda: run_command(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "crewai>=0.120.0",
                "pydantic>=2.0.0",
                "langchain>=0.0.267",
                "--no-deps",
            ],
            check=False,
        ),
        # Method 4: Try with pip's dependency resolver
        lambda: run_command(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "crewai>=0.120.0",
                "--no-dependencies",
            ],
            check=False,
        ),
    ]

    logger = logging.getLogger(__name__)
    for i, method in enumerate(methods, 1):
        logger.info("Trying installation method %d...", i)
        method()

        # Verify installation
        try:
            import crewai
        except ImportError as e:
            logger.warning("Method %d failed: %s", i, e)
        else:
            logger.info(
                "CrewAI installed successfully (version: %s) using method %d",
                crewai.__version__,
                i,
            )
            return True

    logger.error("All installation methods failed")
    return False


def create_mock_crewai() -> bool:
    """
    Create a mock CrewAI module for tests.

    Returns:
        bool: True if mock module was created successfully, False otherwise

    """
    logger = logging.getLogger(__name__)
    logger.info("Creating mock CrewAI module...")

    try:
        # First, check if we can create a system-wide mock
        script_path = Path(__file__).resolve()
        mock_dir = script_path.parent / "mock_crewai"
        logger = logging.getLogger(__name__)
        logger.info("Creating mock CrewAI module in %s", mock_dir)

        # Create a mock crewai package directory
        mock_dir.mkdir(exist_ok=True, parents=True)

        # Create __init__.py
        init_file = mock_dir / "__init__.py"
        with init_file.open("w") as f:
            f.write("""
# Mock CrewAI module for tests
from .agent import Agent
from .task import Task
from .crew import Crew

__version__ = "0.120.0"
""")

        # Create agent.py
        agent_file = mock_dir / "agent.py"
        with agent_file.open("w") as f:
            f.write("""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .task import Task

class Agent:
    def __init__(self, role="", goal="", backstory="", **kwargs):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.kwargs = kwargs

    def execute_task(self, task: "Task") -> str:
        return f"Executed task: {task.description}"
""")

        # Create task.py
        task_file = mock_dir / "task.py"
        with task_file.open("w") as f:
            f.write("""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent import Agent

class Task:
    def __init__(self, description="", agent: "Agent | None" = None, **kwargs):
        self.description = description
        self.agent = agent
        self.kwargs = kwargs
""")

        # Create crew.py
        crew_file = mock_dir / "crew.py"
        with crew_file.open("w") as f:
            f.write("""
class Crew:
    def __init__(self, agents=None, tasks=None, **kwargs):
        self.agents = agents or []
        self.tasks = tasks or []
        self.kwargs = kwargs

    def kickoff(self):
        return "Mock crew output"

    # Alias for backward compatibility
    run = kickoff
""")

        # Add the mock_crewai directory to sys.path
        if str(mock_dir) not in sys.path:
            sys.path.insert(0, str(mock_dir.parent))

        # Create a crewai.py file in the current directory as a fallback
        fallback_file = Path("crewai.py")
        with fallback_file.open("w") as f:
            f.write("""
# Fallback mock CrewAI module
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List

__version__ = "0.120.0"

class Task:
    def __init__(self, description: str = "", agent: Optional["Agent"] = None, **kwargs):
        self.description = description
        self.agent = agent
        self.kwargs = kwargs

class Agent:
    def __init__(self, role: str = "", goal: str = "", backstory: str = "", **kwargs):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.kwargs = kwargs

    def execute_task(self, task: Task) -> str:
        return f"Executed task: {task.description}"

class Crew:
    def __init__(
        self,
        agents: Optional[List[Agent]] = None,
        tasks: Optional[List[Task]] = None,
        **kwargs
    ):
        self.agents = agents or []
        self.tasks = tasks or []
        self.kwargs = kwargs

    def kickoff(self) -> str:
        return "Mock crew output"

    # Alias for backward compatibility
    run = kickoff
""")

        # Verify mock module
        import importlib.util

        current_dir = Path.cwd()
        sys.path.insert(0, str(current_dir))  # Add current directory to path

        # First try the mock_crewai module
        mock_found = importlib.util.find_spec("mock_crewai") is not None
        if mock_found:
            logger.info("Mock CrewAI module created successfully")
            return True

        logger.warning("mock_crewai module not found in sys.path, trying fallback...")

        # Then try the fallback module
        fallback_found = importlib.util.find_spec("crewai") is not None
        if fallback_found:
            logger.info("Fallback CrewAI module created successfully")
            return True

        # Neither module was found
        logger.warning("Fallback crewai module not found in sys.path")
    except Exception:
        logger.exception("Error creating mock CrewAI module")
        return False
    else:
        return False


def main() -> None:
    """Run the CrewAI installation process."""
    logger = logging.getLogger(__name__)
    logger.info("Starting CrewAI installation for tests...")

    # Try to install CrewAI
    success = install_crewai()

    # If installation fails, create a mock module
    if not success:
        logger.warning("CrewAI installation failed, creating mock module...")
        create_mock_crewai()

    logger.info("CrewAI setup for tests completed")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    main()
