#!/usr/bin/env python3
"""
Test script to verify the mock_crewai module fixes.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_mock_crewai():
    """Test the mock_crewai module."""
    try:
        # Import the module
        import mock_crewai
        
        # Check version attribute
        print(f"Version: {mock_crewai.__version__}")
        assert hasattr(mock_crewai, "__version__")
        assert mock_crewai.__version__ == "0.120.0"
        
        # Check enum types
        print(f"AgentType: {mock_crewai.AgentType}")
        assert hasattr(mock_crewai, "AgentType")
        assert hasattr(mock_crewai.AgentType, "DEFAULT")
        assert hasattr(mock_crewai.AgentType, "OPENAI")
        assert hasattr(mock_crewai.AgentType, "ANTHROPIC")
        
        print(f"TaskType: {mock_crewai.TaskType}")
        assert hasattr(mock_crewai, "TaskType")
        assert hasattr(mock_crewai.TaskType, "DEFAULT")
        assert hasattr(mock_crewai.TaskType, "SEQUENTIAL")
        assert hasattr(mock_crewai.TaskType, "PARALLEL")
        
        print(f"CrewType: {mock_crewai.CrewType}")
        assert hasattr(mock_crewai, "CrewType")
        assert hasattr(mock_crewai.CrewType, "DEFAULT")
        assert hasattr(mock_crewai.CrewType, "HIERARCHICAL")
        
        # Test creating instances
        agent = mock_crewai.Agent(
            role="Test Agent",
            goal="Test Goal",
            backstory="Test Backstory",
            agent_type=mock_crewai.AgentType.DEFAULT
        )
        
        task = mock_crewai.Task(
            description="Test Task",
            agent=agent,
            task_type=mock_crewai.TaskType.DEFAULT
        )
        
        crew = mock_crewai.Crew(
            agents=[agent],
            tasks=[task],
            crew_type=mock_crewai.CrewType.DEFAULT
        )
        
        # Test methods
        result = agent.execute_task(task)
        print(f"Agent.execute_task result: {result}")
        
        result = crew.kickoff()
        print(f"Crew.kickoff result: {result}")
        
        # Test run alias
        assert crew.run == crew.kickoff
        
        print("All tests passed!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mock_crewai()
    sys.exit(0 if success else 1)
