"""
Integration tests for UI event handling and state management.

This module contains tests for UI event handling and state management across
different UI components.
"""


import pytest
from unittest.mock import patch, MagicMock

from ui.web_ui import WebUI
from ui.cli_ui import CommandLineInterface
from ui.state_management import StateManager, UIState, StateTransition
from ui.event_handlers import EventHandler




@pytest.fixture
def state_manager():
    """Create a state manager instance."""
            return StateManager()


@pytest.fixture
def event_handler():
    """Create an event handler instance."""
            return EventHandler()


@pytest.fixture
def web_ui_with_state(state_manager):
    """Create a Web UI instance with state management."""
    ui = WebUI()
    ui.state_manager = state_manager
            return ui


@pytest.fixture
def cli_ui_with_state(state_manager):
    """Create a CLI UI instance with state management."""
    ui = CommandLineInterface()
    ui.state_manager = state_manager
            return ui


class TestUIStateManagement:
    """Test UI event handling and state management."""

    def test_state_initialization(self, state_manager):
        """Test state initialization."""
        # Check initial state
        assert state_manager.current_state == UIState.INITIAL
        assert state_manager.previous_state is None
        assert state_manager.state_data == {}

    def test_state_transition(self, state_manager):
        """Test state transition."""
        # Transition to a new state
        state_manager.transition_to(UIState.NICHE_ANALYSIS, {"market_segments": ["e-commerce"]})
        
        # Check new state
        assert state_manager.current_state == UIState.NICHE_ANALYSIS
        assert state_manager.previous_state == UIState.INITIAL
        assert state_manager.state_data == {"market_segments": ["e-commerce"]}
        
        # Transition to another state
        state_manager.transition_to(UIState.SOLUTION_DEVELOPMENT, {"niche_id": "niche1"})
        
        # Check new state
        assert state_manager.current_state == UIState.SOLUTION_DEVELOPMENT
        assert state_manager.previous_state == UIState.NICHE_ANALYSIS
        assert state_manager.state_data == {"niche_id": "niche1"}

    def test_state_history(self, state_manager):
        """Test state history tracking."""
        # Transition through several states
        state_manager.transition_to(UIState.NICHE_ANALYSIS, {"market_segments": ["e-commerce"]})
        state_manager.transition_to(UIState.SOLUTION_DEVELOPMENT, {"niche_id": "niche1"})
        state_manager.transition_to(UIState.MONETIZATION, {"solution_id": "solution1"})
        
        # Check state history
        history = state_manager.get_state_history()
        assert len(history) == 4  # Including initial state
        assert history[0][0] == UIState.INITIAL
        assert history[1][0] == UIState.NICHE_ANALYSIS
        assert history[2][0] == UIState.SOLUTION_DEVELOPMENT
        assert history[3][0] == UIState.MONETIZATION

    def test_state_rollback(self, state_manager):
        """Test state rollback."""
        # Transition through several states
        state_manager.transition_to(UIState.NICHE_ANALYSIS, {"market_segments": ["e-commerce"]})
        state_manager.transition_to(UIState.SOLUTION_DEVELOPMENT, {"niche_id": "niche1"})
        
        # Rollback to previous state
        state_manager.rollback()
        
        # Check current state
        assert state_manager.current_state == UIState.NICHE_ANALYSIS
        assert state_manager.state_data == {"market_segments": ["e-commerce"]}
        
        # Rollback again
        state_manager.rollback()
        
        # Check current state
        assert state_manager.current_state == UIState.INITIAL
        assert state_manager.state_data == {}

    def test_web_ui_state_integration(self, web_ui_with_state):
        """Test Web UI integration with state management."""
        ui = web_ui_with_state
        
        # Simulate user actions that change state
        ui.state_manager.transition_to(UIState.NICHE_ANALYSIS, {"market_segments": ["e-commerce"]})
        
        # Check UI state
        assert ui.state_manager.current_state == UIState.NICHE_ANALYSIS
        
        # Simulate selecting a niche
        ui.state_manager.transition_to(UIState.SOLUTION_DEVELOPMENT, {"niche_id": "niche1"})
        
        # Check UI state
        assert ui.state_manager.current_state == UIState.SOLUTION_DEVELOPMENT

    def test_cli_ui_state_integration(self, cli_ui_with_state):
        """Test CLI UI integration with state management."""
        ui = cli_ui_with_state
        
        # Simulate user commands that change state
        ui.state_manager.transition_to(UIState.NICHE_ANALYSIS, {"market_segments": ["e-commerce"]})
        
        # Check UI state
        assert ui.state_manager.current_state == UIState.NICHE_ANALYSIS
        
        # Simulate selecting a niche
        ui.state_manager.transition_to(UIState.SOLUTION_DEVELOPMENT, {"niche_id": "niche1"})
        
        # Check UI state
        assert ui.state_manager.current_state == UIState.SOLUTION_DEVELOPMENT

    def test_event_handling(self, web_ui_with_state, event_handler):
        """Test event handling."""
        ui = web_ui_with_state
        ui.event_handler = event_handler
        
        # Mock event handlers
        event_handler.handle_niche_selected = MagicMock()
        event_handler.handle_solution_developed = MagicMock()
        
        # Simulate events
        ui.handle_event("niche_selected", {"niche_id": "niche1"})
        ui.handle_event("solution_developed", {"solution_id": "solution1"})
        
        # Check that event handlers were called
        event_handler.handle_niche_selected.assert_called_once_with(ui, {"niche_id": "niche1"})
        event_handler.handle_solution_developed.assert_called_once_with(ui, {"solution_id": "solution1"})

    def test_state_validation(self, state_manager):
        """Test state validation."""
        # Define valid state transitions
        valid_transitions = {
            UIState.INITIAL: [UIState.NICHE_ANALYSIS],
            UIState.NICHE_ANALYSIS: [UIState.SOLUTION_DEVELOPMENT],
            UIState.SOLUTION_DEVELOPMENT: [UIState.MONETIZATION, UIState.MARKETING],
            UIState.MONETIZATION: [UIState.MARKETING, UIState.EXPORT],
            UIState.MARKETING: [UIState.EXPORT],
            UIState.EXPORT: [UIState.INITIAL]
        }
        
        # Set valid transitions
        state_manager.set_valid_transitions(valid_transitions)
        
        # Test valid transition
        assert state_manager.is_valid_transition(UIState.INITIAL, UIState.NICHE_ANALYSIS)
        assert state_manager.is_valid_transition(UIState.NICHE_ANALYSIS, UIState.SOLUTION_DEVELOPMENT)
        
        # Test invalid transition
        assert not state_manager.is_valid_transition(UIState.INITIAL, UIState.MONETIZATION)
        assert not state_manager.is_valid_transition(UIState.NICHE_ANALYSIS, UIState.MARKETING)
        
        # Test transition with validation
        state_manager.transition_to(UIState.NICHE_ANALYSIS, {"market_segments": ["e-commerce"]}, validate=True)
        assert state_manager.current_state == UIState.NICHE_ANALYSIS
        
        # Test invalid transition with validation
        with pytest.raises(StateTransition.InvalidTransitionError):
            state_manager.transition_to(UIState.EXPORT, {}, validate=True)

    def test_state_persistence(self, state_manager):
        """Test state persistence."""
        # Transition to a state
        state_manager.transition_to(UIState.NICHE_ANALYSIS, {"market_segments": ["e-commerce"]})
        
        # Save state
        state_data = state_manager.serialize()
        
        # Create a new state manager
        new_state_manager = StateManager()
        
        # Load state
        new_state_manager.deserialize(state_data)
        
        # Check state
        assert new_state_manager.current_state == UIState.NICHE_ANALYSIS
        assert new_state_manager.state_data == {"market_segments": ["e-commerce"]}

    def test_cross_ui_state_synchronization(self, web_ui_with_state, cli_ui_with_state):
        """Test state synchronization between different UI components."""
        web_ui = web_ui_with_state
        cli_ui = cli_ui_with_state
        
        # Share the same state manager
        cli_ui.state_manager = web_ui.state_manager
        
        # Change state in web UI
        web_ui.state_manager.transition_to(UIState.NICHE_ANALYSIS, {"market_segments": ["e-commerce"]})
        
        # Check state in CLI UI
        assert cli_ui.state_manager.current_state == UIState.NICHE_ANALYSIS
        assert cli_ui.state_manager.state_data == {"market_segments": ["e-commerce"]}
        
        # Change state in CLI UI
        cli_ui.state_manager.transition_to(UIState.SOLUTION_DEVELOPMENT, {"niche_id": "niche1"})
        
        # Check state in web UI
        assert web_ui.state_manager.current_state == UIState.SOLUTION_DEVELOPMENT
        assert web_ui.state_manager.state_data == {"niche_id": "niche1"}


if __name__ == "__main__":
    pytest.main(["-v", "test_ui_state_management.py"])