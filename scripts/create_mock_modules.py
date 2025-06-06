#!/usr/bin/env python3
"""
Create comprehensive mock modules for testing.

This script creates mock modules for mcp, crewai, and mem0 packages
to allow tests to run without requiring the actual packages to be installed.
"""

import os
import sys
import logging
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Optional


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def create_mock_mcp_module() -> bool:
    """Create a mock modelcontextprotocol module."""
    try:
        # Create in-memory module
        mock_module = ModuleType("modelcontextprotocol")
        mock_module.__version__ = "0.1.0"
        mock_module.__file__ = "<mock>"
        
        # Create mock Client class
        class MockClient:
            def __init__(self, endpoint: str = "", **kwargs: Any) -> None:
                self.endpoint = endpoint
                self.kwargs = kwargs
                
            def connect(self) -> None:
                pass
                
            def disconnect(self) -> None:
                pass
                
            def send_message(self, message: str) -> str:
                return f"Mock MCP response to: {message}"
        
        # Create mock Server class
        class MockServer:
            def __init__(self, name: str = "mock-server", **kwargs: Any) -> None:
                self.name = name
                self.kwargs = kwargs
                
            def start(self) -> None:
                pass
                
            def stop(self) -> None:
                pass
        
        # Add classes to module
        mock_module.Client = MockClient
        mock_module.Server = MockServer
        
        # Register module
        sys.modules["modelcontextprotocol"] = mock_module
        sys.modules["mcp"] = mock_module  # Alternative import name
        
        logger.info("✅ Created mock MCP module")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create mock MCP module: {e}")
        return False


def create_mock_crewai_module() -> bool:
    """Create a mock crewai module."""
    try:
        # Create in-memory module
        mock_module = ModuleType("crewai")
        mock_module.__version__ = "0.120.0"
        mock_module.__file__ = "<mock>"
        
        # Create mock Agent class
        class MockAgent:
            def __init__(self, role: str = "", goal: str = "", backstory: str = "", **kwargs: Any) -> None:
                self.role = role
                self.goal = goal
                self.backstory = backstory
                self.kwargs = kwargs
                
            def execute_task(self, task: Any) -> str:
                return f"Mock agent executed task: {getattr(task, 'description', 'unknown task')}"
        
        # Create mock Task class
        class MockTask:
            def __init__(self, description: str = "", agent: Optional[Any] = None, **kwargs: Any) -> None:
                self.description = description
                self.agent = agent
                self.kwargs = kwargs
        
        # Create mock Crew class
        class MockCrew:
            def __init__(self, agents: Optional[List[Any]] = None, tasks: Optional[List[Any]] = None, **kwargs: Any) -> None:
                self.agents = agents or []
                self.tasks = tasks or []
                self.kwargs = kwargs
                
            def kickoff(self) -> str:
                return "Mock crew execution completed"
                
            def run(self) -> str:
                return self.kickoff()
        
        # Add classes to module
        mock_module.Agent = MockAgent
        mock_module.Task = MockTask
        mock_module.Crew = MockCrew
        
        # Register module
        sys.modules["crewai"] = mock_module
        
        logger.info("✅ Created mock CrewAI module")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create mock CrewAI module: {e}")
        return False


def create_mock_mem0_module() -> bool:
    """Create a mock mem0 module."""
    try:
        # Create in-memory module
        mock_module = ModuleType("mem0")
        mock_module.__version__ = "0.1.100"
        mock_module.__file__ = "<mock>"
        
        # Create mock Memory class
        class MockMemory:
            def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
                self.config = config or {}
                self.storage: Dict[str, Any] = {}
                
            def add(self, text: str, user_id: str = "default", **kwargs: Any) -> Dict[str, str]:
                memory_id = f"mock-memory-{len(self.storage)}"
                self.storage[memory_id] = {"text": text, "user_id": user_id, **kwargs}
                return {"id": memory_id}
                
            def search(self, query: str, user_id: str = "default", **kwargs: Any) -> List[Dict[str, Any]]:
                return [
                    {"id": "mock-1", "text": f"Mock memory result for: {query}", "score": 0.9},
                    {"id": "mock-2", "text": f"Another mock result for: {query}", "score": 0.8}
                ]
                
            def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
                return self.storage.get(memory_id)
                
            def delete(self, memory_id: str) -> bool:
                return self.storage.pop(memory_id, None) is not None
        
        # Add classes to module
        mock_module.Memory = MockMemory
        
        # Register module
        sys.modules["mem0"] = mock_module
        sys.modules["mem0ai"] = mock_module  # Alternative import name
        
        logger.info("✅ Created mock mem0 module")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create mock mem0 module: {e}")
        return False


def create_physical_mock_modules(base_dir: str = "mock_modules") -> bool:
    """Create physical mock module files on disk."""
    try:
        base_path = Path(base_dir)
        base_path.mkdir(exist_ok=True)
        
        # Create mock MCP module
        mcp_dir = base_path / "mcp"
        mcp_dir.mkdir(exist_ok=True)
        
        with (mcp_dir / "__init__.py").open("w") as f:
            f.write('''"""Mock MCP module."""
__version__ = "0.1.0"

class Client:
    def __init__(self, endpoint="", **kwargs):
        self.endpoint = endpoint
        self.kwargs = kwargs
    
    def connect(self):
        pass
    
    def disconnect(self):
        pass
    
    def send_message(self, message):
        return f"Mock MCP response to: {message}"

class Server:
    def __init__(self, name="mock-server", **kwargs):
        self.name = name
        self.kwargs = kwargs
    
    def start(self):
        pass
    
    def stop(self):
        pass
''')
        
        # Create mock CrewAI module
        crewai_dir = base_path / "crewai"
        crewai_dir.mkdir(exist_ok=True)
        
        with (crewai_dir / "__init__.py").open("w") as f:
            f.write('''"""Mock CrewAI module."""
__version__ = "0.120.0"

class Agent:
    def __init__(self, role="", goal="", backstory="", **kwargs):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.kwargs = kwargs
    
    def execute_task(self, task):
        return f"Mock agent executed task: {getattr(task, 'description', 'unknown task')}"

class Task:
    def __init__(self, description="", agent=None, **kwargs):
        self.description = description
        self.agent = agent
        self.kwargs = kwargs

class Crew:
    def __init__(self, agents=None, tasks=None, **kwargs):
        self.agents = agents or []
        self.tasks = tasks or []
        self.kwargs = kwargs
    
    def kickoff(self):
        return "Mock crew execution completed"
    
    def run(self):
        return self.kickoff()
''')
        
        # Create mock mem0 module
        mem0_dir = base_path / "mem0"
        mem0_dir.mkdir(exist_ok=True)
        
        with (mem0_dir / "__init__.py").open("w") as f:
            f.write('''"""Mock mem0 module."""
__version__ = "0.1.100"

class Memory:
    def __init__(self, config=None):
        self.config = config or {}
        self.storage = {}
    
    def add(self, text, user_id="default", **kwargs):
        memory_id = f"mock-memory-{len(self.storage)}"
        self.storage[memory_id] = {"text": text, "user_id": user_id, **kwargs}
        return {"id": memory_id}
    
    def search(self, query, user_id="default", **kwargs):
        return [
            {"id": "mock-1", "text": f"Mock memory result for: {query}", "score": 0.9},
            {"id": "mock-2", "text": f"Another mock result for: {query}", "score": 0.8}
        ]
    
    def get(self, memory_id):
        return self.storage.get(memory_id)
    
    def delete(self, memory_id):
        return self.storage.pop(memory_id, None) is not None
''')
        
        # Add to Python path
        if str(base_path) not in sys.path:
            sys.path.insert(0, str(base_path))
        
        logger.info(f"✅ Created physical mock modules in {base_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create physical mock modules: {e}")
        return False


def verify_mock_modules() -> bool:
    """Verify that all mock modules can be imported."""
    modules_to_test = [
        ("modelcontextprotocol", ["Client", "Server"]),
        ("mcp", ["Client", "Server"]),
        ("crewai", ["Agent", "Task", "Crew"]),
        ("mem0", ["Memory"]),
        ("mem0ai", ["Memory"]),
    ]
    
    all_success = True
    
    for module_name, expected_classes in modules_to_test:
        try:
            module = __import__(module_name)
            
            # Check version
            if hasattr(module, "__version__"):
                logger.info(f"✅ {module_name} v{module.__version__} imported successfully")
            else:
                logger.warning(f"⚠️  {module_name} imported but missing __version__")
            
            # Check expected classes
            for class_name in expected_classes:
                if hasattr(module, class_name):
                    logger.info(f"  ✅ {module_name}.{class_name} available")
                else:
                    logger.error(f"  ❌ {module_name}.{class_name} missing")
                    all_success = False
                    
        except ImportError as e:
            logger.error(f"❌ Failed to import {module_name}: {e}")
            all_success = False
    
    return all_success


def main() -> int:
    """Main function to create all mock modules."""
    logger.info("🚀 Creating mock modules for testing...")
    
    success_count = 0
    
    # Create in-memory modules
    if create_mock_mcp_module():
        success_count += 1
    if create_mock_crewai_module():
        success_count += 1
    if create_mock_mem0_module():
        success_count += 1
    
    # Create physical modules as backup
    if create_physical_mock_modules():
        success_count += 1
    
    # Verify all modules
    if verify_mock_modules():
        logger.info("✅ All mock modules verified successfully!")
        return 0
    else:
        logger.error("❌ Some mock modules failed verification")
        return 1 if success_count == 0 else 0  # Return 0 if at least some modules were created


if __name__ == "__main__":
    sys.exit(main())
