"""
Routes for the pAIssive Income UI.

This module defines the routes for the web interface, handling requests
for different parts of the application.
"""

import logging
import os
import traceback
import uuid
from datetime import datetime

from flask import flash, jsonify, redirect, render_template, request, session, url_for

from . import app
from .errors import (
    RouteError,
    ServiceError,
    UIError,
    ValidationError,
    api_error_handler,
    handle_exception,
)
from .task_manager import (
    cancel_task,
    get_task_id,
    get_task_status,
    store_task_id,
)
from .tasks import (
    analyze_niches,
    create_marketing_campaign,
    create_monetization_strategy,
    create_solution,
)

# Set up logging
logger = logging.getLogger(__name__)

# Services - these will be initialized later
agent_team_service = None
niche_analysis_service = None
developer_service = None
monetization_service = None
marketing_service = None


def init_services():
    """Initialize services from the dependency container."""
    global agent_team_service, niche_analysis_service, developer_service, monetization_service, marketing_service

    # Import here to avoid circular imports
    from interfaces.ui_interfaces import (
        IAgentTeamService,
        IDeveloperService,
        IMarketingService,
        IMonetizationService,
        INicheAnalysisService,
    )

    from .service_registry import get_ui_service

    # Initialize services
    agent_team_service = get_ui_service(IAgentTeamService)
    niche_analysis_service = get_ui_service(INicheAnalysisService)
    developer_service = get_ui_service(IDeveloperService)
    monetization_service = get_ui_service(IMonetizationService)
    marketing_service = get_ui_service(IMarketingService)

    logger.info("UI services initialized")


# Home route
@app.route("/")
def index():
    """Render the home page."""
    return render_template(
        "index.html",
        title="pAIssive Income Framework",
        description="A comprehensive framework for developing and monetizing niche AI agents",
    )


# Dashboard route
@app.route("/dashboard")
def dashboard():
    """Render the dashboard page."""
    # Get project data
    projects = agent_team_service.get_projects()

    return render_template("dashboard.html", title="Dashboard", projects=projects)


# Niche Analysis routes
@app.route("/niche-analysis")
def niche_analysis():
    """Render the niche analysis page."""
    # Get market segments
    market_segments = niche_analysis_service.get_market_segments()

    return render_template(
        "niche_analysis.html", title="Niche Analysis", market_segments=market_segments
    )


@app.route("/niche-analysis/run", methods=["POST"])
def run_niche_analysis():
    """Run niche analysis on selected market segments as a background task."""
    from .validation_schemas import NicheAnalysisRequest
    from .validators import validate_form_data

    # Validate input using Pydantic schema
    validated_data = validate_form_data(NicheAnalysisRequest)
    market_segments = validated_data.market_segments

    try:
        # Start background task
        task = analyze_niches.delay(market_segments)
        logger.info(f"Started niche analysis task {task.id}")

        # Store task ID in session
        store_task_id(session, "niche_analysis", task.id)

        # Redirect to task status page
        return redirect(url_for("niche_analysis_status"))
    except Exception as e:
        logger.error(f"Error starting niche analysis task: {e}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("niche_analysis"))


@app.route("/niche-analysis/status")
def niche_analysis_status():
    """Show status of niche analysis task."""
    # Get task ID from session
    task_id = get_task_id(session, "niche_analysis")
    if not task_id:
        flash("No active niche analysis task found.", "error")
        return redirect(url_for("niche_analysis"))

    # Get task status
    status = get_task_status(task_id)

    # Check if task is completed
    if status["state"] == "SUCCESS":
        # Store results in session
        session["niches"] = status["result"]["niches"]
        # Redirect to results page
        return redirect(url_for("niche_results"))

    # Render status page
    return render_template(
        "task_status.html",
        title="Niche Analysis Progress",
        task_id=task_id,
        task_name="Niche Analysis",
        status=status,
    )


@app.route("/niche-analysis/results")
def niche_results():
    """Render the niche analysis results page."""
    # Get niches from session
    niches = session.get("niches", [])

    return render_template(
        "niche_results.html", title="Niche Analysis Results", niches=niches
    )


# Developer routes
@app.route("/developer")
def developer():
    """Render the developer page."""
    # Get niches
    niches = niche_analysis_service.get_niches()

    return render_template(
        "developer.html", title="Solution Development", niches=niches
    )


@app.route("/developer/solution", methods=["POST"])
def develop_solution():
    """Develop a solution for a selected niche as a background task."""
    from .validation_schemas import DeveloperSolutionRequest
    from .validators import validate_form_data

    # Validate input using Pydantic schema
    validated_data = validate_form_data(DeveloperSolutionRequest)
    niche_id = validated_data.niche_id

    try:
        # Start background task
        task = create_solution.delay(niche_id)
        logger.info(f"Started solution development task {task.id}")

        # Store task ID in session
        store_task_id(session, "solution", task.id)

        # Redirect to task status page
        return redirect(url_for("solution_status"))
    except Exception as e:
        logger.error(f"Error starting solution development task: {e}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("developer"))


@app.route("/developer/status")
def solution_status():
    """Show status of solution development task."""
    # Get task ID from session
    task_id = get_task_id(session, "solution")
    if not task_id:
        flash("No active solution development task found.", "error")
        return redirect(url_for("developer"))

    # Get task status
    status = get_task_status(task_id)

    # Check if task is completed
    if status["state"] == "SUCCESS":
        # Store results in session
        session["solution"] = status["result"]
        # Redirect to results page
        return redirect(url_for("solution_results"))

    # Render status page
    return render_template(
        "task_status.html",
        title="Solution Development Progress",
        task_id=task_id,
        task_name="Solution Development",
        status=status,
    )


@app.route("/developer/results")
def solution_results():
    """Render the solution results page."""
    # Get solution from session
    solution = session.get("solution", {})

    return render_template(
        "solution_results.html", title="Solution Results", solution=solution
    )


# Monetization routes
@app.route("/monetization")
def monetization():
    """Render the monetization page."""
    # Get solutions
    solutions = developer_service.get_solutions()

    return render_template(
        "monetization.html", title="Monetization Strategy", solutions=solutions
    )


@app.route("/monetization/strategy", methods=["POST"])
def create_monetization_strategy_route():
    """Create a monetization strategy for a selected solution as a background task."""
    from .validation_schemas import MonetizationStrategyRequest
    from .validators import validate_form_data

    # Validate input using Pydantic schema
    validated_data = validate_form_data(MonetizationStrategyRequest)
    solution_id = validated_data.solution_id

    try:
        # Start background task
        task = create_monetization_strategy.delay(solution_id)
        logger.info(f"Started monetization strategy task {task.id}")

        # Store task ID in session
        store_task_id(session, "monetization", task.id)

        # Redirect to task status page
        return redirect(url_for("monetization_status"))
    except Exception as e:
        logger.error(f"Error starting monetization strategy task: {e}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("monetization"))


@app.route("/monetization/status")
def monetization_status():
    """Show status of monetization strategy task."""
    # Get task ID from session
    task_id = get_task_id(session, "monetization")
    if not task_id:
        flash("No active monetization strategy task found.", "error")
        return redirect(url_for("monetization"))

    # Get task status
    status = get_task_status(task_id)

    # Check if task is completed
    if status["state"] == "SUCCESS":
        # Store results in session
        session["monetization_strategy"] = status["result"]
        # Redirect to results page
        return redirect(url_for("monetization_results"))

    # Render status page
    return render_template(
        "task_status.html",
        title="Monetization Strategy Progress",
        task_id=task_id,
        task_name="Monetization Strategy",
        status=status,
    )


@app.route("/monetization/results")
def monetization_results():
    """Render the monetization results page."""
    # Get monetization strategy from session
    strategy = session.get("monetization_strategy", {})

    return render_template(
        "monetization_results.html",
        title="Monetization Strategy Results",
        strategy=strategy,
    )


# Marketing routes
@app.route("/marketing")
def marketing():
    """Render the marketing page."""
    # Get solutions
    solutions = developer_service.get_solutions()

    return render_template(
        "marketing.html", title="Marketing Campaign", solutions=solutions
    )


@app.route("/marketing/campaign", methods=["POST"])
def create_marketing_campaign_route():
    """Create a marketing campaign for a selected solution as a background task."""
    from .validation_schemas import MarketingCampaignRequest
    from .validators import validate_form_data

    # Validate input using Pydantic schema
    validated_data = validate_form_data(MarketingCampaignRequest)
    solution_id = validated_data.solution_id

    try:
        # Start background task
        task = create_marketing_campaign.delay(solution_id)
        logger.info(f"Started marketing campaign task {task.id}")

        # Store task ID in session
        store_task_id(session, "marketing", task.id)

        # Redirect to task status page
        return redirect(url_for("marketing_status"))
    except Exception as e:
        logger.error(f"Error starting marketing campaign task: {e}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("marketing"))


@app.route("/marketing/status")
def marketing_status():
    """Show status of marketing campaign task."""
    # Get task ID from session
    task_id = get_task_id(session, "marketing")
    if not task_id:
        flash("No active marketing campaign task found.", "error")
        return redirect(url_for("marketing"))

    # Get task status
    status = get_task_status(task_id)

    # Check if task is completed
    if status["state"] == "SUCCESS":
        # Store results in session
        session["marketing_campaign"] = status["result"]
        # Redirect to results page
        return redirect(url_for("marketing_results"))

    # Render status page
    return render_template(
        "task_status.html",
        title="Marketing Campaign Progress",
        task_id=task_id,
        task_name="Marketing Campaign",
        status=status,
    )


@app.route("/marketing/results")
def marketing_results():
    """Render the marketing results page."""
    # Get marketing campaign from session
    campaign = session.get("marketing_campaign", {})

    return render_template(
        "marketing_results.html", title="Marketing Campaign Results", campaign=campaign
    )


# About route
@app.route("/about")
def about():
    """Render the about page."""
    return render_template("about.html", title="About pAIssive Income Framework")


# Health check route for containerization
@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for container monitoring."""
    try:
        # Check if critical services are available
        agent_team_service.is_healthy()
        niche_analysis_service.is_healthy()
        developer_service.is_healthy()
        monetization_service.is_healthy()
        marketing_service.is_healthy()

        return (
            jsonify(
                {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "version": os.environ.get("APP_VERSION", "development"),
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e),
                }
            ),
            500,
        )


# Task management API endpoints
@app.route("/api/task/<task_id>", methods=["GET"])
def get_task(task_id):
    """API endpoint to get task status."""
    from .validators import sanitize_input

    try:
        # Sanitize the task_id to prevent injection attacks
        sanitized_task_id = sanitize_input(task_id)

        # Validate the task_id format (basic UUID validation)
        try:
            uuid.UUID(sanitized_task_id)
        except ValueError:
            raise ValidationError(
                message="Invalid task ID format",
                validation_errors=[
                    {"field": "task_id", "error": "Task ID must be a valid UUID"}
                ],
            )

        status = get_task_status(sanitized_task_id)
        return jsonify(status)
    except Exception as e:
        return api_error_handler(e)


@app.route("/api/task/<task_id>/cancel", methods=["POST"])
def cancel_task_route(task_id):
    """API endpoint to cancel a task."""
    from .validators import sanitize_input

    try:
        # Sanitize the task_id to prevent injection attacks
        sanitized_task_id = sanitize_input(task_id)

        # Validate the task_id format (basic UUID validation)
        try:
            uuid.UUID(sanitized_task_id)
        except ValueError:
            raise ValidationError(
                message="Invalid task ID format",
                validation_errors=[
                    {"field": "task_id", "error": "Task ID must be a valid UUID"}
                ],
            )

        result = cancel_task(sanitized_task_id)
        return jsonify(
            {
                "success": result,
                "message": (
                    "Task cancelled" if result else "Task could not be cancelled"
                ),
            }
        )
    except Exception as e:
        return api_error_handler(e)


# API routes
@app.route("/api/niches", methods=["GET"])
def api_get_niches():
    """API endpoint to get niches."""
    from .validation_schemas import ApiQueryParams
    from .validators import validate_query_params

    try:
        # Validate query parameters
        params = validate_query_params(ApiQueryParams)

        # Get niches with pagination and sorting
        niches = niche_analysis_service.get_niches(
            limit=params.limit,
            offset=params.offset,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
        )
        return jsonify(niches)
    except Exception as e:
        return api_error_handler(e)


@app.route("/api/solutions", methods=["GET"])
def api_get_solutions():
    """API endpoint to get solutions."""
    from .validation_schemas import ApiQueryParams
    from .validators import validate_query_params

    try:
        # Validate query parameters
        params = validate_query_params(ApiQueryParams)

        # Get solutions with pagination and sorting
        solutions = developer_service.get_solutions(
            limit=params.limit,
            offset=params.offset,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
        )
        return jsonify(solutions)
    except Exception as e:
        return api_error_handler(e)


@app.route("/api/monetization-strategies", methods=["GET"])
def api_get_monetization_strategies():
    """API endpoint to get monetization strategies."""
    from .validation_schemas import ApiQueryParams
    from .validators import validate_query_params

    try:
        # Validate query parameters
        params = validate_query_params(ApiQueryParams)

        # Get strategies with pagination and sorting
        strategies = monetization_service.get_strategies(
            limit=params.limit,
            offset=params.offset,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
        )
        return jsonify(strategies)
    except Exception as e:
        return api_error_handler(e)


@app.route("/api/marketing-campaigns", methods=["GET"])
def api_get_marketing_campaigns():
    """API endpoint to get marketing campaigns."""
    from .validation_schemas import ApiQueryParams
    from .validators import validate_query_params

    try:
        # Validate query parameters
        params = validate_query_params(ApiQueryParams)

        # Get campaigns with pagination and sorting
        campaigns = marketing_service.get_campaigns(
            limit=params.limit,
            offset=params.offset,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
        )
        return jsonify(campaigns)
    except Exception as e:
        return api_error_handler(e)


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    error = RouteError(
        message="The requested page was not found",
        route=request.path,
        method=request.method,
        http_status=404,
    )
    error.log(logging.WARNING)
    return render_template("errors/404.html", title="Page Not Found", error=error), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    # If it's already a UIError, use it directly
    if isinstance(e, UIError):
        error = e
    else:
        # Create a UIError from the exception
        error = UIError(
            message=f"An unexpected error occurred: {str(e)}",
            details={"traceback": traceback.format_exc()},
            original_exception=e,
        )

    error.log(logging.ERROR)
    return render_template("errors/500.html", title="Server Error", error=error), 500


@app.errorhandler(ValidationError)
def validation_error(e):
    """Handle validation errors."""
    e.log(logging.WARNING)

    # For API requests, return JSON
    if request.path.startswith("/api/"):
        return api_error_handler(e)

    # For form submissions, flash error messages and redirect back
    if e.validation_errors:
        for error in e.validation_errors:
            flash(f"{error.get('field', '')}: {error.get('error', '')}", "error")
    else:
        flash(e.message, "error")

    # Try to redirect back to the previous page
    return redirect(request.referrer or url_for("index"))


@app.errorhandler(ServiceError)
def service_error(e):
    """Handle service errors."""
    e.log(logging.ERROR)

    # For API requests, return JSON
    if request.path.startswith("/api/"):
        return api_error_handler(e)

    # For regular requests, show error page
    return (
        render_template("errors/500.html", title="Service Error", error=e),
        e.http_status,
    )


@app.errorhandler(Exception)
def handle_exception(e):  # noqa: F811
    """Handle all other exceptions."""
    # Create a UIError from the exception
    error = UIError(
        message=f"An unexpected error occurred: {str(e)}",
        details={"traceback": traceback.format_exc()},
        original_exception=e,
    )

    error.log(logging.ERROR)

    # For API requests, return JSON
    if request.path.startswith("/api/"):
        return api_error_handler(error)

    # For regular requests, show error page
    return render_template("errors/500.html", title="Server Error", error=error), 500
