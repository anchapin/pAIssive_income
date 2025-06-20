#!/usr/bin/env python3
"""
Test mock modules to ensure they work correctly.

This test file verifies that all mock modules can be imported and used
without errors, providing the necessary functionality for testing.
"""

import sys
import unittest
from unittest.mock import patch


class TestMockModules(unittest.TestCase):
    """Test cases for mock modules."""

    def setUp(self):
        """Set up test environment."""
        # Create mock modules before each test
        try:
            from scripts.create_mock_modules import (
                create_mock_crewai_module,
                create_mock_mcp_module,
                create_mock_mem0_module,
            )

            create_mock_mcp_module()
            create_mock_crewai_module()
            create_mock_mem0_module()
        except ImportError:
            # If the script is not available, skip these tests
            self.skipTest("Mock module creation script not available")

    def test_mock_mcp_module(self):
        """Test that mock MCP module works correctly."""
        try:
            import modelcontextprotocol

            # Test version attribute
            assert hasattr(modelcontextprotocol, "__version__")
            assert modelcontextprotocol.__version__ == "0.1.0"

            # Test Client class
            assert hasattr(modelcontextprotocol, "Client")
            client = modelcontextprotocol.Client("test-endpoint")
            assert client.endpoint == "test-endpoint"

            # Test Client methods
            client.connect()  # Should not raise
            client.disconnect()  # Should not raise
            response = client.send_message("test message")
            assert "test message" in response

            # Test Server class
            assert hasattr(modelcontextprotocol, "Server")
            server = modelcontextprotocol.Server("test-server")
            assert server.name == "test-server"

            # Test Server methods
            server.start()  # Should not raise
            server.stop()  # Should not raise

        except ImportError as e:
            self.fail(f"Failed to import mock MCP module: {e}")

    def test_mock_crewai_module(self):
        """Test that mock CrewAI module works correctly."""
        try:
            import crewai

            # Test version attribute
            assert hasattr(crewai, "__version__")
            assert crewai.__version__ == "0.120.0"

            # Test Agent class
            assert hasattr(crewai, "Agent")
            agent = crewai.Agent(
                role="test-role", goal="test-goal", backstory="test-backstory"
            )
            assert agent.role == "test-role"
            assert agent.goal == "test-goal"
            assert agent.backstory == "test-backstory"

            # Test Task class
            assert hasattr(crewai, "Task")
            task = crewai.Task(description="test task")
            assert task.description == "test task"

            # Test Agent execute_task method
            result = agent.execute_task(task)
            assert "test task" in result

            # Test Crew class
            assert hasattr(crewai, "Crew")
            crew = crewai.Crew(agents=[agent], tasks=[task])
            assert len(crew.agents) == 1
            assert len(crew.tasks) == 1

            # Test Crew methods
            result = crew.kickoff()
            assert isinstance(result, str)

            result = crew.run()
            assert isinstance(result, str)

        except ImportError as e:
            self.fail(f"Failed to import mock CrewAI module: {e}")

    def test_mock_mem0_module(self):
        """Test that mock mem0 module works correctly."""
        try:
            import mem0

            # Test version attribute
            assert hasattr(mem0, "__version__")
            assert mem0.__version__ == "0.1.100"

            # Test Memory class
            assert hasattr(mem0, "Memory")
            memory = mem0.Memory()

            # Test add method
            result = memory.add("test memory", user_id="test-user")
            assert "id" in result
            memory_id = result["id"]

            # Test search method
            search_results = memory.search("test query", user_id="test-user")
            assert isinstance(search_results, list)
            assert len(search_results) > 0

            # Test get method
            retrieved = memory.get(memory_id)
            assert retrieved is not None
            assert retrieved["text"] == "test memory"

            # Test delete method
            deleted = memory.delete(memory_id)
            assert deleted

            # Verify deletion
            retrieved_after_delete = memory.get(memory_id)
            assert retrieved_after_delete is None

        except ImportError as e:
            self.fail(f"Failed to import mock mem0 module: {e}")

    def test_alternative_import_names(self):
        """Test that alternative import names work."""
        try:
            # Test MCP alternative import
            import mcp

            assert hasattr(mcp, "Client")

            # Test mem0ai alternative import
            import mem0ai

            assert hasattr(mem0ai, "Memory")

        except ImportError as e:
            self.fail(f"Failed to import alternative module names: {e}")

    def test_mock_modules_in_tests(self):
        """Test that mock modules work in test scenarios."""
        # This test simulates how the mock modules would be used in actual tests

        try:
            import mem0
            import modelcontextprotocol

            import crewai

            # Create instances as they would be used in tests
            mcp_client = modelcontextprotocol.Client("test://endpoint")
            agent = crewai.Agent(role="tester")
            memory = mem0.Memory()

            # Perform operations
            mcp_response = mcp_client.send_message("test")
            assert isinstance(mcp_response, str)

            task = crewai.Task(description="test task")
            agent_result = agent.execute_task(task)
            assert isinstance(agent_result, str)

            memory_result = memory.add("test memory")
            assert "id" in memory_result

        except Exception as e:
            self.fail(f"Mock modules failed in test scenario: {e}")


class TestMockModuleCompatibility(unittest.TestCase):
    """Test compatibility with existing code patterns."""

    def test_import_patterns(self):
        """Test various import patterns that might be used."""
        # Test direct imports
        try:
            import mem0
            import modelcontextprotocol
            import crewai

            Memory = mem0.Memory
            Client = modelcontextprotocol.Client
            Agent = crewai.Agent
            Crew = crewai.Crew
            Task = crewai.Task

            # Test that classes can be instantiated
            client = Client()
            agent = Agent()
            task = Task()
            crew = Crew()
            memory = Memory()

            # Basic functionality test
            assert client is not None
            assert agent is not None
            assert task is not None
            assert crew is not None
            assert memory is not None

        except ImportError as e:
            self.fail(f"Import pattern test failed: {e}")

    def test_version_attributes(self):
        """Test that version attributes are properly set."""
        import mem0
        import modelcontextprotocol

        import crewai

        # Check that all modules have version attributes
        assert hasattr(modelcontextprotocol, "__version__")
        assert hasattr(crewai, "__version__")
        assert hasattr(mem0, "__version__")

        # Check that versions are strings
        assert isinstance(modelcontextprotocol.__version__, str)
        assert isinstance(crewai.__version__, str)
        assert isinstance(mem0.__version__, str)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
