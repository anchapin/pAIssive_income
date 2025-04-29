"""
Examples of using the event bus for different services.

This module provides examples of how to use the event bus for different services.
"""

import time
import logging
import asyncio
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from services.shared.event_bus import (
    EventBus,
    AsyncEventBus,
    Event,
    EventSchema,
    EventType,
    EventMetadata
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Example 1: Niche Analysis Service - Domain Events
def niche_analysis_service_example():
    """Example of using the event bus in the Niche Analysis Service."""
    
    # Define event data schemas
    class NicheAnalysisCompleted(BaseModel):
        """Event data for when a niche analysis is completed."""
        niche_id: str
        niche_name: str
        score: float
        problems_count: int
        opportunities_count: int
        competition_level: str
    
    class NicheOpportunityIdentified(BaseModel):
        """Event data for when a niche opportunity is identified."""
        niche_id: str
        opportunity_id: str
        opportunity_name: str
        opportunity_score: float
        difficulty: str
    
    # Create event schemas
    analysis_completed_schema = EventSchema(
        data_model=NicheAnalysisCompleted,
        event_name="niche.analysis.completed"
    )
    
    opportunity_identified_schema = EventSchema(
        data_model=NicheOpportunityIdentified,
        event_name="niche.opportunity.identified"
    )
    
    # Create an event bus
    event_bus = EventBus(service_name="niche-analysis-service")
    
    try:
        # Start the event bus
        event_bus.start()
        
        # Simulate completing a niche analysis
        logger.info("Simulating niche analysis completion...")
        
        # Create an event for the completed analysis
        analysis_completed_data = NicheAnalysisCompleted(
            niche_id="niche-123",
            niche_name="fitness-apps",
            score=0.85,
            problems_count=3,
            opportunities_count=5,
            competition_level="medium"
        )
        
        analysis_completed_event = analysis_completed_schema.create_event(
            source="niche-analysis-service",
            data=analysis_completed_data,
            event_type=EventType.DOMAIN
        )
        
        # Publish the event
        event_bus.publish(analysis_completed_event)
        
        # Simulate identifying opportunities
        logger.info("Simulating opportunity identification...")
        
        # Create events for identified opportunities
        opportunities = [
            {
                "opportunity_id": "opp-1",
                "opportunity_name": "AI-powered workout planner",
                "opportunity_score": 0.9,
                "difficulty": "medium"
            },
            {
                "opportunity_id": "opp-2",
                "opportunity_name": "Nutrition tracking app",
                "opportunity_score": 0.8,
                "difficulty": "low"
            }
        ]
        
        for opp in opportunities:
            opportunity_data = NicheOpportunityIdentified(
                niche_id="niche-123",
                **opp
            )
            
            opportunity_event = opportunity_identified_schema.create_event(
                source="niche-analysis-service",
                data=opportunity_data,
                event_type=EventType.DOMAIN
            )
            
            # Publish the event
            event_bus.publish(opportunity_event)
        
        # Keep the service running for a bit
        time.sleep(2)
        
    finally:
        # Close the event bus
        event_bus.close()


# Example 2: Marketing Service - Event Handling
def marketing_service_example():
    """Example of using the event bus in the Marketing Service."""
    
    # Define event data schemas
    class NicheAnalysisCompleted(BaseModel):
        """Event data for when a niche analysis is completed."""
        niche_id: str
        niche_name: str
        score: float
        problems_count: int
        opportunities_count: int
        competition_level: str
    
    class NicheOpportunityIdentified(BaseModel):
        """Event data for when a niche opportunity is identified."""
        niche_id: str
        opportunity_id: str
        opportunity_name: str
        opportunity_score: float
        difficulty: str
    
    # Create event schemas
    analysis_completed_schema = EventSchema(
        data_model=NicheAnalysisCompleted,
        event_name="niche.analysis.completed"
    )
    
    opportunity_identified_schema = EventSchema(
        data_model=NicheOpportunityIdentified,
        event_name="niche.opportunity.identified"
    )
    
    # Create an event bus
    event_bus = EventBus(service_name="marketing-service")
    
    try:
        # Define event handlers
        def handle_niche_analysis_completed(event: Event):
            # Parse the event data
            analysis_data = analysis_completed_schema.parse_event(event)
            
            logger.info(f"Marketing Service: Received niche analysis completed event for {analysis_data.niche_name}")
            logger.info(f"Niche score: {analysis_data.score}, Competition: {analysis_data.competition_level}")
            logger.info(f"Starting marketing research for {analysis_data.niche_name}...")
        
        def handle_opportunity_identified(event: Event):
            # Parse the event data
            opportunity_data = opportunity_identified_schema.parse_event(event)
            
            logger.info(f"Marketing Service: Received opportunity identified event: {opportunity_data.opportunity_name}")
            logger.info(f"Opportunity score: {opportunity_data.opportunity_score}, Difficulty: {opportunity_data.difficulty}")
            logger.info(f"Analyzing marketing channels for {opportunity_data.opportunity_name}...")
        
        # Subscribe to events
        event_bus.subscribe(
            event_pattern="niche.analysis.completed",
            handler=handle_niche_analysis_completed
        )
        
        event_bus.subscribe(
            event_pattern="niche.opportunity.identified",
            handler=handle_opportunity_identified
        )
        
        # Start the event bus
        event_bus.start()
        
        logger.info("Marketing Service is listening for events...")
        
        # Keep the service running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down Marketing Service...")
        
    finally:
        # Close the event bus
        event_bus.close()


# Example 3: Asynchronous Event Handling
async def async_event_handling_example():
    """Example of asynchronous event handling."""
    
    # Define event data schemas
    class UserRegistered(BaseModel):
        """Event data for when a user registers."""
        user_id: str
        username: str
        email: str
        registration_time: float
    
    # Create event schemas
    user_registered_schema = EventSchema(
        data_model=UserRegistered,
        event_name="user.registered"
    )
    
    # Create async event buses for publisher and subscriber
    async with AsyncEventBus(service_name="auth-service") as publisher_bus:
        async with AsyncEventBus(service_name="notification-service") as subscriber_bus:
            # Define an async event handler
            async def handle_user_registered(event: Event):
                # Parse the event data
                user_data = user_registered_schema.parse_event(event)
                
                logger.info(f"Notification Service: Received user registered event for {user_data.username}")
                logger.info(f"Sending welcome email to {user_data.email}...")
                
                # Simulate sending an email
                await asyncio.sleep(1)
                
                logger.info(f"Welcome email sent to {user_data.email}")
            
            # Subscribe to events
            await subscriber_bus.subscribe(
                event_pattern="user.registered",
                handler=handle_user_registered
            )
            
            # Start the subscriber
            await subscriber_bus.start()
            
            logger.info("Notification Service is listening for events...")
            
            # Simulate user registration
            logger.info("Simulating user registration...")
            
            # Create an event for the user registration
            user_data = UserRegistered(
                user_id="user-123",
                username="john_doe",
                email="john.doe@example.com",
                registration_time=time.time()
            )
            
            user_registered_event = user_registered_schema.create_event(
                source="auth-service",
                data=user_data,
                event_type=EventType.DOMAIN
            )
            
            # Publish the event
            await publisher_bus.publish(user_registered_event)
            
            # Wait for the event to be processed
            await asyncio.sleep(2)


# Example 4: Event-Driven Workflow
def event_driven_workflow_example():
    """Example of an event-driven workflow across multiple services."""
    
    # Define event data schemas
    class NicheSelected(BaseModel):
        """Event data for when a niche is selected."""
        niche_id: str
        niche_name: str
        user_id: str
    
    class SolutionCreated(BaseModel):
        """Event data for when a solution is created."""
        solution_id: str
        niche_id: str
        solution_name: str
        user_id: str
    
    class MarketingPlanGenerated(BaseModel):
        """Event data for when a marketing plan is generated."""
        plan_id: str
        solution_id: str
        channels: List[str]
        user_id: str
    
    # Create event schemas
    niche_selected_schema = EventSchema(
        data_model=NicheSelected,
        event_name="workflow.niche.selected"
    )
    
    solution_created_schema = EventSchema(
        data_model=SolutionCreated,
        event_name="workflow.solution.created"
    )
    
    marketing_plan_schema = EventSchema(
        data_model=MarketingPlanGenerated,
        event_name="workflow.marketing.plan.generated"
    )
    
    # Create event buses for each service
    ui_bus = EventBus(service_name="ui-service")
    solution_bus = EventBus(service_name="solution-service")
    marketing_bus = EventBus(service_name="marketing-service")
    
    try:
        # Define event handlers
        def handle_niche_selected(event: Event):
            # Parse the event data
            niche_data = niche_selected_schema.parse_event(event)
            
            logger.info(f"Solution Service: Received niche selected event for {niche_data.niche_name}")
            logger.info(f"Creating solution for niche {niche_data.niche_name}...")
            
            # Simulate solution creation
            time.sleep(1)
            
            # Create an event for the solution creation
            solution_data = SolutionCreated(
                solution_id="solution-123",
                niche_id=niche_data.niche_id,
                solution_name=f"{niche_data.niche_name} Solution",
                user_id=niche_data.user_id
            )
            
            solution_event = solution_created_schema.create_event(
                source="solution-service",
                data=solution_data,
                event_type=EventType.DOMAIN,
                user_id=niche_data.user_id
            )
            
            # Publish the event
            solution_bus.publish(solution_event)
        
        def handle_solution_created(event: Event):
            # Parse the event data
            solution_data = solution_created_schema.parse_event(event)
            
            logger.info(f"Marketing Service: Received solution created event for {solution_data.solution_name}")
            logger.info(f"Generating marketing plan for {solution_data.solution_name}...")
            
            # Simulate marketing plan generation
            time.sleep(1)
            
            # Create an event for the marketing plan generation
            plan_data = MarketingPlanGenerated(
                plan_id="plan-123",
                solution_id=solution_data.solution_id,
                channels=["social-media", "content-marketing", "email"],
                user_id=solution_data.user_id
            )
            
            plan_event = marketing_plan_schema.create_event(
                source="marketing-service",
                data=plan_data,
                event_type=EventType.DOMAIN,
                user_id=solution_data.user_id
            )
            
            # Publish the event
            marketing_bus.publish(plan_event)
        
        def handle_marketing_plan_generated(event: Event):
            # Parse the event data
            plan_data = marketing_plan_schema.parse_event(event)
            
            logger.info(f"UI Service: Received marketing plan generated event")
            logger.info(f"Updating UI with marketing plan for solution {plan_data.solution_id}")
            logger.info(f"Marketing channels: {', '.join(plan_data.channels)}")
        
        # Subscribe to events
        solution_bus.subscribe(
            event_pattern="workflow.niche.selected",
            handler=handle_niche_selected
        )
        
        marketing_bus.subscribe(
            event_pattern="workflow.solution.created",
            handler=handle_solution_created
        )
        
        ui_bus.subscribe(
            event_pattern="workflow.marketing.plan.generated",
            handler=handle_marketing_plan_generated
        )
        
        # Start the event buses
        solution_bus.start()
        marketing_bus.start()
        ui_bus.start()
        
        logger.info("All services are listening for events...")
        
        # Simulate a user selecting a niche
        logger.info("Simulating user selecting a niche...")
        
        # Create an event for the niche selection
        niche_data = NicheSelected(
            niche_id="niche-123",
            niche_name="fitness-apps",
            user_id="user-123"
        )
        
        niche_event = niche_selected_schema.create_event(
            source="ui-service",
            data=niche_data,
            event_type=EventType.DOMAIN,
            user_id=niche_data.user_id
        )
        
        # Publish the event
        ui_bus.publish(niche_event)
        
        # Wait for the workflow to complete
        time.sleep(5)
        
    finally:
        # Close the event buses
        ui_bus.close()
        solution_bus.close()
        marketing_bus.close()


# Run the examples
if __name__ == "__main__":
    # Example 1: Niche Analysis Service - Domain Events
    # niche_analysis_service_example()
    
    # Example 2: Marketing Service - Event Handling
    # marketing_service_example()
    
    # Example 3: Asynchronous Event Handling
    # asyncio.run(async_event_handling_example())
    
    # Example 4: Event-Driven Workflow
    event_driven_workflow_example()
