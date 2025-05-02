"""
Background tasks for the pAIssive Income UI.

This module defines Celery tasks for asynchronous processing.
"""

import logging
import time
import traceback
from typing import Any, Dict, List

from celery import current_task

from interfaces.ui_interfaces import (
    IAgentTeamService,
    IDeveloperService,
    IMarketingService,
    IMonetizationService,
    INicheAnalysisService,
)

from .celery_app import celery_app
from .service_registry import get_service

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Task state definition
TASK_STATES = {
    "PENDING": "Task is waiting to be executed",
    "STARTED": "Task has been started",
    "PROGRESS": "Task is in progress",  # Custom state
    "SUCCESS": "Task completed successfully",
    "FAILURE": "Task failed",
    "RETRY": "Task is being retried",
    "REVOKED": "Task was revoked",
}


# Services
def get_services():
    """Get services with dependency injection."""
    return {
        "agent_team_service": get_service(IAgentTeamService),
        "niche_analysis_service": get_service(INicheAnalysisService),
        "developer_service": get_service(IDeveloperService),
        "monetization_service": get_service(IMonetizationService),
        "marketing_service": get_service(IMarketingService),
    }


def update_task_progress(
    task_id: str,
    current: int,
    total: int,
    status: str,
    message: str = None,
    result: Any = None,
):
    """
    Update the progress of a task.

    Args:
        task_id: ID of the task
        current: Current progress value
        total: Total progress value
        status: Status of the task
        message: Status message
        result: Partial result data
    """
    if current_task and current_task.request.id == task_id:
        state = "PROGRESS" if status == "PROGRESS" else status
        meta = {
            "current": current,
            "total": total,
            "status": status,
            "message": message or "",
            "result": result,
        }
        current_task.update_state(state=state, meta=meta)
        return meta
    return None


@celery_app.task(bind=True, name="paissive_income.analyze_niches")
def analyze_niches(self, market_segments: List[str]) -> Dict[str, Any]:
    """
    Background task for niche analysis.

    Args:
        market_segments: List of market segments to analyze

    Returns:
        Dictionary with analysis results
    """
    task_id = self.request.id
    logger.info(f"Starting niche analysis task {task_id}")

    try:
        # Initialize services
        services = get_services()
        niche_service = services["niche_analysis_service"]

        # Update initial progress
        update_task_progress(task_id, 0, 100, "STARTED", "Starting niche analysis")

        # Start analysis
        segments_count = len(market_segments)
        niches = []

        # Process each segment
        for i, segment in enumerate(market_segments):
            # Update progress
            progress = int((i / segments_count) * 100)
            update_task_progress(
                task_id,
                progress,
                100,
                "PROGRESS",
                f"Analyzing segment {segment} ({i+1}/{segments_count})",
            )

            # Analyze segment
            segment_niches = niche_service.analyze_segment(segment)
            niches.extend(segment_niches)

            # Simulate work (remove in production)
            time.sleep(2)

        # Finalize results
        result = {
            "niches": niches,
            "count": len(niches),
            "segments_analyzed": market_segments,
        }

        # Update final progress
        update_task_progress(
            task_id, 100, 100, "SUCCESS", "Niche analysis complete", result
        )
        return result

    except Exception as e:
        logger.error(f"Error in niche analysis task {task_id}: {e}")
        logger.error(traceback.format_exc())
        update_task_progress(task_id, 0, 100, "FAILURE", f"Error: {str(e)}")
        raise


@celery_app.task(bind=True, name="paissive_income.create_solution")
def create_solution(self, niche_id: str) -> Dict[str, Any]:
    """
    Background task for solution development.

    Args:
        niche_id: ID of the niche to develop a solution for

    Returns:
        Dictionary with solution details
    """
    task_id = self.request.id
    logger.info(f"Starting solution development task {task_id}")

    try:
        # Initialize services
        services = get_services()
        developer_service = services["developer_service"]

        # Update initial progress
        update_task_progress(
            task_id, 0, 100, "STARTED", "Starting solution development"
        )

        # Development stages
        stages = [
            "Analyzing niche requirements",
            "Defining solution architecture",
            "Designing agent capabilities",
            "Creating solution prototype",
            "Estimating implementation efforts",
            "Finalizing solution proposal",
        ]

        # Process each development stage
        for i, stage in enumerate(stages):
            # Update progress
            progress = int(((i + 1) / len(stages)) * 100)
            update_task_progress(
                task_id,
                progress,
                100,
                "PROGRESS",
                f"Stage {i+1}/{len(stages)}: {stage}",
            )

            # Simulate work (remove in production)
            time.sleep(3)

        # Create the actual solution
        solution = developer_service.create_solution(niche_id)

        # Update final progress
        update_task_progress(
            task_id, 100, 100, "SUCCESS", "Solution development complete", solution
        )
        return solution

    except Exception as e:
        logger.error(f"Error in solution development task {task_id}: {e}")
        logger.error(traceback.format_exc())
        update_task_progress(task_id, 0, 100, "FAILURE", f"Error: {str(e)}")
        raise


@celery_app.task(bind=True, name="paissive_income.create_monetization_strategy")
def create_monetization_strategy(self, solution_id: str) -> Dict[str, Any]:
    """
    Background task for creating a monetization strategy.

    Args:
        solution_id: ID of the solution to monetize

    Returns:
        Dictionary with monetization strategy details
    """
    task_id = self.request.id
    logger.info(f"Starting monetization strategy task {task_id}")

    try:
        # Initialize services
        services = get_services()
        monetization_service = services["monetization_service"]

        # Update initial progress
        update_task_progress(
            task_id, 0, 100, "STARTED", "Starting monetization strategy development"
        )

        # Strategy development stages
        stages = [
            "Analyzing target audience",
            "Researching pricing models",
            "Evaluating revenue streams",
            "Calculating profitability metrics",
            "Defining subscription tiers",
            "Creating growth projections",
        ]

        # Process each stage
        for i, stage in enumerate(stages):
            # Update progress
            progress = int(((i + 1) / len(stages)) * 100)
            update_task_progress(
                task_id,
                progress,
                100,
                "PROGRESS",
                f"Stage {i+1}/{len(stages)}: {stage}",
            )

            # Simulate work (remove in production)
            time.sleep(2)

        # Create the actual monetization strategy
        strategy = monetization_service.create_strategy(solution_id)

        # Update final progress
        update_task_progress(
            task_id, 100, 100, "SUCCESS", "Monetization strategy complete", strategy
        )
        return strategy

    except Exception as e:
        logger.error(f"Error in monetization strategy task {task_id}: {e}")
        logger.error(traceback.format_exc())
        update_task_progress(task_id, 0, 100, "FAILURE", f"Error: {str(e)}")
        raise


@celery_app.task(bind=True, name="paissive_income.create_marketing_campaign")
def create_marketing_campaign(self, solution_id: str) -> Dict[str, Any]:
    """
    Background task for creating a marketing campaign.

    Args:
        solution_id: ID of the solution to market

    Returns:
        Dictionary with marketing campaign details
    """
    task_id = self.request.id
    logger.info(f"Starting marketing campaign task {task_id}")

    try:
        # Initialize services
        services = get_services()
        marketing_service = services["marketing_service"]

        # Update initial progress
        update_task_progress(
            task_id, 0, 100, "STARTED", "Starting marketing campaign development"
        )

        # Campaign development stages
        stages = [
            "Analyzing target audience",
            "Defining brand messaging",
            "Selecting marketing channels",
            "Creating content strategy",
            "Setting up analytics",
            "Finalizing campaign calendar",
        ]

        # Process each stage
        for i, stage in enumerate(stages):
            # Update progress
            progress = int(((i + 1) / len(stages)) * 100)
            update_task_progress(
                task_id,
                progress,
                100,
                "PROGRESS",
                f"Stage {i+1}/{len(stages)}: {stage}",
            )

            # Simulate work (remove in production)
            time.sleep(2)

        # Create the actual marketing campaign
        campaign = marketing_service.create_campaign(solution_id)

        # Update final progress
        update_task_progress(
            task_id, 100, 100, "SUCCESS", "Marketing campaign complete", campaign
        )
        return campaign

    except Exception as e:
        logger.error(f"Error in marketing campaign task {task_id}: {e}")
        logger.error(traceback.format_exc())
        update_task_progress(task_id, 0, 100, "FAILURE", f"Error: {str(e)}")
        raise
