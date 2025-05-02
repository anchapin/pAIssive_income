"""
Agent Team GraphQL resolvers.

This module provides resolvers for agent team queries and mutations.
"""

import logging
from typing import Optional, List, Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import strawberry
    from strawberry.types import Info
    STRAWBERRY_AVAILABLE = True
except ImportError:
    logger.warning("Strawberry GraphQL is required for GraphQL resolvers")
    STRAWBERRY_AVAILABLE = False

if STRAWBERRY_AVAILABLE:
    from ..schemas.agent_team import (
        AgentType, TeamType, TaskType, WorkspaceType,
        AgentInput, TeamInput, TaskInput, WorkspaceInput,
        AgentRoleEnum, TaskStatusEnum, TaskPriorityEnum
    )
    
    @strawberry.type
    class AgentTeamQuery:
        """Agent team query resolvers."""
        
        @strawberry.field
        async def agents(self, info: Info, team_id: Optional[str] = None,
                       limit: Optional[int] = 10, offset: Optional[int] = 0) -> List[AgentType]:
            """
            Get a list of agents.
            
            Args:
                info: GraphQL resolver info
                team_id: Filter by team ID
                limit: Maximum number of agents to return
                offset: Number of agents to skip
                
            Returns:
                List of agents
            """
            # Get agent team service from context
            service = info.context["services"].get("agent_team")
            if not service:
                logger.warning("Agent team service not available")
                return []
            
            # Get agents from service
            try:
                agents = await service.get_agents(
                    team_id=team_id,
                    limit=limit,
                    offset=offset
                )
                
                return [
                    AgentType(
                        id=str(agent.id),
                        name=agent.name,
                        description=agent.description,
                        role=AgentRoleEnum(agent.role),
                        capabilities=agent.capabilities,
                        model_id=str(agent.model_id) if agent.model_id else None,
                        created_at=agent.created_at.isoformat() if agent.created_at else None,
                        updated_at=agent.updated_at.isoformat() if agent.updated_at else None
                    )
                    for agent in agents
                ]
            except Exception as e:
                logger.error(f"Error getting agents: {str(e)}")
                return []
        
        @strawberry.field
        async def agent(self, info: Info, id: str) -> Optional[AgentType]:
            """
            Get an agent by ID.
            
            Args:
                info: GraphQL resolver info
                id: Agent ID
                
            Returns:
                Agent if found, None otherwise
            """
            # Get agent team service from context
            service = info.context["services"].get("agent_team")
            if not service:
                logger.warning("Agent team service not available")
                return None
            
            # Get agent from service
            try:
                agent = await service.get_agent(id)
                if not agent:
                    return None
                
                return AgentType(
                    id=str(agent.id),
                    name=agent.name,
                    description=agent.description,
                    role=AgentRoleEnum(agent.role),
                    capabilities=agent.capabilities,
                    model_id=str(agent.model_id) if agent.model_id else None,
                    created_at=agent.created_at.isoformat() if agent.created_at else None,
                    updated_at=agent.updated_at.isoformat() if agent.updated_at else None
                )
            except Exception as e:
                logger.error(f"Error getting agent: {str(e)}")
                return None
        
        @strawberry.field
        async def teams(self, info: Info, limit: Optional[int] = 10, 
                      offset: Optional[int] = 0) -> List[TeamType]:
            """
            Get a list of teams.
            
            Args:
                info: GraphQL resolver info
                limit: Maximum number of teams to return
                offset: Number of teams to skip
                
            Returns:
                List of teams
            """
            # Get agent team service from context
            service = info.context["services"].get("agent_team")
            if not service:
                logger.warning("Agent team service not available")
                return []
            
            # Get teams from service
            try:
                teams = await service.get_teams(limit=limit, offset=offset)
                
                return [
                    TeamType(
                        id=str(team.id),
                        name=team.name,
                        description=team.description,
                        created_at=team.created_at.isoformat() if team.created_at else None,
                        updated_at=team.updated_at.isoformat() if team.updated_at else None
                    )
                    for team in teams
                ]
            except Exception as e:
                logger.error(f"Error getting teams: {str(e)}")
                return []
        
        @strawberry.field
        async def tasks(self, info: Info, team_id: Optional[str] = None, agent_id: Optional[str] = None,
                      status: Optional[TaskStatusEnum] = None, limit: Optional[int] = 10, 
                      offset: Optional[int] = 0) -> List[TaskType]:
            """
            Get a list of tasks.
            
            Args:
                info: GraphQL resolver info
                team_id: Filter by team ID
                agent_id: Filter by agent ID
                status: Filter by task status
                limit: Maximum number of tasks to return
                offset: Number of tasks to skip
                
            Returns:
                List of tasks
            """
            # Get agent team service from context
            service = info.context["services"].get("agent_team")
            if not service:
                logger.warning("Agent team service not available")
                return []
            
            # Get tasks from service
            try:
                tasks = await service.get_tasks(
                    team_id=team_id,
                    agent_id=agent_id,
                    status=status.value if status else None,
                    limit=limit,
                    offset=offset
                )
                
                return [
                    TaskType(
                        id=str(task.id),
                        team_id=str(task.team_id) if task.team_id else None,
                        agent_id=str(task.agent_id) if task.agent_id else None,
                        title=task.title,
                        description=task.description,
                        status=TaskStatusEnum(task.status),
                        priority=TaskPriorityEnum(task.priority),
                        due_date=task.due_date.isoformat() if task.due_date else None,
                        created_at=task.created_at.isoformat() if task.created_at else None,
                        updated_at=task.updated_at.isoformat() if task.updated_at else None
                    )
                    for task in tasks
                ]
            except Exception as e:
                logger.error(f"Error getting tasks: {str(e)}")
                return []
    
    @strawberry.type
    class AgentTeamMutation:
        """Agent team mutation resolvers."""
        
        @strawberry.mutation
        async def create_agent(self, info: Info, input: AgentInput) -> Optional[AgentType]:
            """
            Create a new agent.
            
            Args:
                info: GraphQL resolver info
                input: Agent input
                
            Returns:
                Created agent if successful, None otherwise
            """
            # Get agent team service from context
            service = info.context["services"].get("agent_team")
            if not service:
                logger.warning("Agent team service not available")
                return None
            
            # Create agent
            try:
                agent = await service.create_agent(
                    name=input.name,
                    description=input.description,
                    role=input.role.value,
                    capabilities=input.capabilities,
                    model_id=input.model_id
                )
                
                return AgentType(
                    id=str(agent.id),
                    name=agent.name,
                    description=agent.description,
                    role=AgentRoleEnum(agent.role),
                    capabilities=agent.capabilities,
                    model_id=str(agent.model_id) if agent.model_id else None,
                    created_at=agent.created_at.isoformat() if agent.created_at else None,
                    updated_at=agent.updated_at.isoformat() if agent.updated_at else None
                )
            except Exception as e:
                logger.error(f"Error creating agent: {str(e)}")
                return None
        
        @strawberry.mutation
        async def update_agent(self, info: Info, id: str, input: AgentInput) -> Optional[AgentType]:
            """
            Update an agent.
            
            Args:
                info: GraphQL resolver info
                id: Agent ID
                input: Agent input
                
            Returns:
                Updated agent if successful, None otherwise
            """
            # Get agent team service from context
            service = info.context["services"].get("agent_team")
            if not service:
                logger.warning("Agent team service not available")
                return None
            
            # Update agent
            try:
                agent = await service.update_agent(
                    id=id,
                    name=input.name,
                    description=input.description,
                    role=input.role.value,
                    capabilities=input.capabilities,
                    model_id=input.model_id
                )
                
                if not agent:
                    return None
                
                return AgentType(
                    id=str(agent.id),
                    name=agent.name,
                    description=agent.description,
                    role=AgentRoleEnum(agent.role),
                    capabilities=agent.capabilities,
                    model_id=str(agent.model_id) if agent.model_id else None,
                    created_at=agent.created_at.isoformat() if agent.created_at else None,
                    updated_at=agent.updated_at.isoformat() if agent.updated_at else None
                )
            except Exception as e:
                logger.error(f"Error updating agent: {str(e)}")
                return None
        
        @strawberry.mutation
        async def delete_agent(self, info: Info, id: str) -> bool:
            """
            Delete an agent.
            
            Args:
                info: GraphQL resolver info
                id: Agent ID
                
            Returns:
                True if successful, False otherwise
            """
            # Get agent team service from context
            service = info.context["services"].get("agent_team")
            if not service:
                logger.warning("Agent team service not available")
                return False
            
            # Delete agent
            try:
                success = await service.delete_agent(id)
                return success
            except Exception as e:
                logger.error(f"Error deleting agent: {str(e)}")
                return False
        
        @strawberry.mutation
        async def create_team(self, info: Info, input: TeamInput) -> Optional[TeamType]:
            """
            Create a new team.
            
            Args:
                info: GraphQL resolver info
                input: Team input
                
            Returns:
                Created team if successful, None otherwise
            """
            # Get agent team service from context
            service = info.context["services"].get("agent_team")
            if not service:
                logger.warning("Agent team service not available")
                return None
            
            # Create team
            try:
                team = await service.create_team(
                    name=input.name,
                    description=input.description,
                    agent_ids=input.agent_ids
                )
                
                return TeamType(
                    id=str(team.id),
                    name=team.name,
                    description=team.description,
                    created_at=team.created_at.isoformat() if team.created_at else None,
                    updated_at=team.updated_at.isoformat() if team.updated_at else None
                )
            except Exception as e:
                logger.error(f"Error creating team: {str(e)}")
                return None
        
        @strawberry.mutation
        async def create_task(self, info: Info, input: TaskInput) -> Optional[TaskType]:
            """
            Create a new task.
            
            Args:
                info: GraphQL resolver info
                input: Task input
                
            Returns:
                Created task if successful, None otherwise
            """
            # Get agent team service from context
            service = info.context["services"].get("agent_team")
            if not service:
                logger.warning("Agent team service not available")
                return None
            
            # Create task
            try:
                task = await service.create_task(
                    team_id=input.team_id,
                    agent_id=input.agent_id,
                    title=input.title,
                    description=input.description,
                    priority=input.priority.value,
                    due_date=input.due_date
                )
                
                return TaskType(
                    id=str(task.id),
                    team_id=str(task.team_id) if task.team_id else None,
                    agent_id=str(task.agent_id) if task.agent_id else None,
                    title=task.title,
                    description=task.description,
                    status=TaskStatusEnum(task.status),
                    priority=TaskPriorityEnum(task.priority),
                    due_date=task.due_date.isoformat() if task.due_date else None,
                    created_at=task.created_at.isoformat() if task.created_at else None,
                    updated_at=task.updated_at.isoformat() if task.updated_at else None
                )
            except Exception as e:
                logger.error(f"Error creating task: {str(e)}")
                return None
