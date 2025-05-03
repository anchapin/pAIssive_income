"""
Integration tests for UI interactions with backend services.
"""


from unittest.mock import MagicMock, patch

import pytest

from ui.cli_ui import CommandLineInterface


from ui.web_ui import WebUI


    from ui.routes import init_services

    init_services

# Import UI modules
# Import test fixtures


@pytest.fixture
def initialize_ui_services(register_mock_services):
    """Initialize UI services for testing."""
    # Initialize routes services
()
    return True


@pytest.fixture
def web_ui(
    mock_agent_team,
    mock_model_manager,
    mock_subscription_manager,
    initialize_ui_services,
):
    """Create a WebUI instance with mock dependencies."""
    ui = WebUI(
        agent_team=mock_agent_team,
        model_manager=mock_model_manager,
        subscription_manager=mock_subscription_manager,
    )
    return ui


@pytest.fixture
def cli_ui(
    mock_agent_team,
    mock_model_manager,
    mock_subscription_manager,
    initialize_ui_services,
):
    """Create a CommandLineInterface instance with mock dependencies."""
    ui = CommandLineInterface(
        agent_team=mock_agent_team,
        model_manager=mock_model_manager,
        subscription_manager=mock_subscription_manager,
    )
    return ui


def test_web_ui_niche_analysis_integration(web_ui, mock_agent_team):
    """Test the WebUI integration with agent team for niche analysis."""
    # Simulate a user request to analyze niches
    market_segments = ["e-commerce", "digital-marketing"]
    niches = web_ui.analyze_market_segments(market_segments)

    # Check that the agent team's method was called with the right parameters
    mock_agent_team.run_niche_analysis.assert_called_once_with(market_segments)

    # Check that the UI returned the expected results
    assert len(niches) == 2
    assert niches[0]["name"] == "AI Inventory Management"
    assert niches[1]["name"] == "Content Generation for Marketing"

    # Verify that the UI processes the results correctly
    assert hasattr(web_ui, "current_niches")
    assert web_ui.current_niches == niches


def test_web_ui_solution_development_integration(web_ui, mock_agent_team):
    """Test the WebUI integration with agent team for solution development."""
    # Set up a selected niche
    selected_niche = {
        "id": "niche1",
        "name": "AI Inventory Management",
        "market_segment": "e-commerce",
        "opportunity_score": 0.85,
    }
    web_ui.current_niches = [selected_niche]

    # Simulate a user request to develop a solution
    solution = web_ui.develop_solution(selected_niche["id"])

    # Check that the agent team's method was called with the right parameters
    mock_agent_team.develop_solution.assert_called_once_with(selected_niche)

    # Check that the UI returned the expected results
    assert solution["name"] == "AI Inventory Optimizer"
    assert len(solution["features"]) == 2

    # Verify that the UI processes the results correctly
    assert hasattr(web_ui, "current_solution")
    assert web_ui.current_solution == solution


def test_web_ui_monetization_strategy_integration(web_ui, mock_agent_team):
    """Test the WebUI integration with agent team for monetization strategy creation."""
    # Set up a selected solution
    selected_solution = {
        "id": "solution1",
        "name": "AI Inventory Optimizer",
        "description": "An AI tool that helps e-commerce businesses optimize inventory levels.",
        "features": [
            {"id": "feature1", "name": "Demand Forecasting"},
            {"id": "feature2", "name": "Reorder Alerts"},
        ],
    }
    web_ui.current_solution = selected_solution

    # Simulate a user request to create a monetization strategy
    monetization = web_ui.create_monetization_strategy()

    # Check that the agent team's method was called with the right parameters
    mock_agent_team.create_monetization_strategy.assert_called_once_with(
        selected_solution
    )

    # Check that the UI returned the expected results
    assert monetization["name"] == "Freemium Strategy"
    assert len(monetization["subscription_model"]["tiers"]) == 2

    # Verify that the UI processes the results correctly
    assert hasattr(web_ui, "current_monetization")
    assert web_ui.current_monetization == monetization


def test_web_ui_marketing_plan_integration(web_ui, mock_agent_team):
    """Test the WebUI integration with agent team for marketing plan creation."""
    # Set up selected niche, solution, and monetization
    selected_niche = {
        "id": "niche1",
        "name": "AI Inventory Management",
        "market_segment": "e-commerce",
        "opportunity_score": 0.85,
    }
    selected_solution = {
        "id": "solution1",
        "name": "AI Inventory Optimizer",
        "description": "An AI tool that helps e-commerce businesses optimize inventory levels.",
        "features": [
            {"id": "feature1", "name": "Demand Forecasting"},
            {"id": "feature2", "name": "Reorder Alerts"},
        ],
    }
    selected_monetization = {
        "id": "monetization1",
        "name": "Freemium Strategy",
        "subscription_model": {
            "name": "Inventory Optimizer Subscription",
            "tiers": [
                {"name": "Free", "price_monthly": 0},
                {"name": "Pro", "price_monthly": 29.99},
            ],
        },
    }
    web_ui.current_niches = [selected_niche]
    web_ui.current_solution = selected_solution
    web_ui.current_monetization = selected_monetization

    # Simulate a user request to create a marketing plan
    marketing_plan = web_ui.create_marketing_plan()

    # Check that the agent team's method was called with the right parameters
    mock_agent_team.create_marketing_plan.assert_called_once_with(
        selected_niche, selected_solution, selected_monetization
    )

    # Check that the UI returned the expected results
    assert marketing_plan["name"] == "Inventory Optimizer Marketing Plan"
    assert "content" in marketing_plan["channels"]
    assert marketing_plan["target_audience"] == "E-commerce store owners"

    # Verify that the UI processes the results correctly
    assert hasattr(web_ui, "current_marketing_plan")
    assert web_ui.current_marketing_plan == marketing_plan


def test_cli_ui_full_workflow_integration(cli_ui, mock_agent_team):
    """Test the CommandLineInterface integration with the full workflow."""
    # Simulate a complete workflow through the CLI

    # Step 1: Run niche analysis
    cli_ui.handle_command("analyze e-commerce digital-marketing")
    mock_agent_team.run_niche_analysis.assert_called_once_with(
        ["e-commerce", "digital-marketing"]
    )

    # Step 2: Select a niche and develop a solution
    cli_ui.handle_command("select niche 0")  # Select the first niche
    cli_ui.handle_command("develop solution")
    mock_agent_team.develop_solution.assert_called_once()

    # Step 3: Create a monetization strategy
    cli_ui.handle_command("create monetization")
    mock_agent_team.create_monetization_strategy.assert_called_once()

    # Step 4: Create a marketing plan
    cli_ui.handle_command("create marketing")
    mock_agent_team.create_marketing_plan.assert_called_once()

    # Verify the final state
    assert hasattr(cli_ui, "current_niches")
    assert hasattr(cli_ui, "current_solution")
    assert hasattr(cli_ui, "current_monetization")
    assert hasattr(cli_ui, "current_marketing_plan")


@patch("ui.web_ui.WebUI.render_template")
def test_web_ui_render_integration(mock_render_template, web_ui, mock_agent_team):
    """Test the WebUI template rendering integration."""
    # Set up some data
    web_ui.current_niches = mock_agent_team.run_niche_analysis.return_value
    web_ui.current_solution = mock_agent_team.develop_solution.return_value

    # Set up the mock to return a tuple
    mock_render_template.return_value = (
        "dashboard.html",
        {
            "niches": web_ui.current_niches,
            "solution": web_ui.current_solution,
            "monetization": web_ui.current_monetization,
            "marketing_plan": web_ui.current_marketing_plan,
        },
    )

    # Simulate rendering the dashboard page
    web_ui.render_dashboard()

    # Check that the render_template method was called with the right parameters
    mock_render_template.assert_called_once()

    # Get the arguments passed to render_template
    args, kwargs = mock_render_template.call_args

    # Check that the template name is correct
    assert "dashboard.html" in args

    # Check that the context contains the expected keys
    assert "niches" in kwargs
    assert "solution" in kwargs
    assert kwargs["niches"] == web_ui.current_niches
    assert kwargs["solution"] == web_ui.current_solution


@patch("ui.web_ui.WebUI.handle_ajax_request")
def test_web_ui_ajax_integration(mock_handle_ajax_request, web_ui):
    """Test the WebUI AJAX request handling integration."""
    # Simulate an AJAX request
    request_data = {"action": "analyze_niche", "market_segments": ["e-commerce"]}

    # Set up the mock to return a success response
    mock_handle_ajax_request.return_value = {
        "success": True,
        "action": "analyze_niche",
        "data": {"market_segments": ["e-commerce"]},
    }

    web_ui.process_ajax_request(request_data)

    # Check that the handle_ajax_request method was called
    mock_handle_ajax_request.assert_called_once()

    # Get the arguments passed to handle_ajax_request
    args, kwargs = mock_handle_ajax_request.call_args

    # Check that the action is correct
    assert "analyze_niche" == args[0]

    # Check that the data contains the market_segments
    assert "market_segments" in args[1]
    assert args[1]["market_segments"] == ["e-commerce"]


def test_web_ui_model_manager_integration(web_ui, mock_model_manager):
    """Test the WebUI integration with model manager."""
    # Simulate a request to list available models
    models = web_ui.list_available_models()

    # Check that the model manager's method was called
    mock_model_manager.list_models.assert_called_once()

    # Check that the UI returned the expected results
    assert len(models) == 2
    assert models[0]["name"] == "GPT-4"
    assert models[1]["name"] == "DALL-E 3"


def test_web_ui_subscription_manager_integration(web_ui, mock_subscription_manager):
    """Test the WebUI integration with subscription manager."""
    # Simulate a request to get subscription information for a user
    user_id = "user1"
    subscriptions = web_ui.get_user_subscriptions(user_id)

    # Check that the subscription manager's method was called with the right parameters
    mock_subscription_manager.get_active_subscriptions.assert_called_once_with(user_id)

    # Check that the UI returned the expected results
    assert len(subscriptions) == 1
    assert subscriptions[0]["user_id"] == "user1"
    assert subscriptions[0]["plan_name"] == "Pro Plan"
    assert subscriptions[0]["status"] == "active"


@patch("ui.event_handlers.handle_niche_selected")
def test_web_ui_event_handling_integration(mock_handle_niche_selected, web_ui):
    """Test the WebUI integration with event handlers."""
    # Set up some data
    niches = [
        {
            "id": "niche1",
            "name": "AI Inventory Management",
            "market_segment": "e-commerce",
            "opportunity_score": 0.85,
        }
    ]
    web_ui.current_niches = niches

    # Simulate a niche selection event
    event_data = {"niche_id": "niche1"}
    web_ui.handle_event("niche_selected", event_data)

    # Check that the event handler was called with the right parameters
    mock_handle_niche_selected.assert_called_once()
    ui_arg, data_arg = mock_handle_niche_selected.call_args[0]
    assert ui_arg == web_ui
    assert data_arg == event_data


def test_cli_ui_input_parsing_integration(cli_ui):
    """Test the CommandLineInterface integration with input parsing."""
    # Mock the process_command method
    cli_ui.process_command = MagicMock()

    # Simulate user input for various commands
    commands = [
        "help",
        "analyze e-commerce healthcare",
        "select niche 1",
        "develop solution",
        "create monetization",
        "create marketing",
        "export plan",
    ]

    # Process each command
    for command in commands:
        cli_ui.handle_command(command)

    # Verify each command was processed correctly
    expected_calls = [
        ("help", []),
        ("analyze", ["e-commerce", "healthcare"]),
        ("select", ["niche", "1"]),
        ("develop", ["solution"]),
        ("create", ["monetization"]),
        ("create", ["marketing"]),
        ("export", ["plan"]),
    ]

    actual_calls = cli_ui.process_command.call_args_list
    assert len(actual_calls) == len(expected_calls)

    for i, (expected_command, expected_args) in enumerate(expected_calls):
        actual_command, actual_args = actual_calls[i][0]
        assert actual_command == expected_command
        assert actual_args == expected_args


def test_persistence_integration(web_ui):
    """Test the UI integration with data persistence."""
    # Mock the persistence methods
    web_ui.save_data = MagicMock()
    web_ui.load_data = MagicMock(
        return_value={
            "niches": [{"id": "niche1", "name": "Saved Niche"}],
            "solution": {"id": "solution1", "name": "Saved Solution"},
            "monetization": {"id": "monetization1", "name": "Saved Monetization"},
            "marketing_plan": {"id": "marketing1", "name": "Saved Marketing Plan"},
        }
    )

    # Simulate saving the current state
    web_ui.current_niches = [{"id": "niche1", "name": "Test Niche"}]
    web_ui.current_solution = {"id": "solution1", "name": "Test Solution"}
    web_ui.save_project("test_project")

    # Check that save_data was called with the right parameters
    web_ui.save_data.assert_called_once()
    filename, data = web_ui.save_data.call_args[0]
    assert "test_project" in filename
    assert "niches" in data
    assert "solution" in data

    # Simulate loading a saved state
    web_ui.load_project("test_project")

    # Check that load_data was called and data was loaded
    web_ui.load_data.assert_called_once_with("test_project")
    assert web_ui.current_niches[0]["name"] == "Saved Niche"
    assert web_ui.current_solution["name"] == "Saved Solution"
    assert web_ui.current_monetization["name"] == "Saved Monetization"
    assert web_ui.current_marketing_plan["name"] == "Saved Marketing Plan"