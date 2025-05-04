"""
"""
Agent Team GraphQL resolvers.
Agent Team GraphQL resolvers.


This module provides resolvers for agent team queries and mutations.
This module provides resolvers for agent team queries and mutations.
"""
"""




import logging
import logging
from typing import List, Optional
from typing import List, Optional


import strawberry
import strawberry
from strawberry.types import Info
from strawberry.types import Info


STRAWBERRY_AVAILABLE
STRAWBERRY_AVAILABLE


# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


try:
    try:


    = True
    = True
except ImportError:
except ImportError:
    logger.warning("Strawberry GraphQL is required for GraphQL resolvers")
    logger.warning("Strawberry GraphQL is required for GraphQL resolvers")
    STRAWBERRY_AVAILABLE = False
    STRAWBERRY_AVAILABLE = False


    if STRAWBERRY_AVAILABLE:
    if STRAWBERRY_AVAILABLE:
    from ..schemas.agent_team import (AgentInput, AgentRoleEnum, AgentType,
    from ..schemas.agent_team import (AgentInput, AgentRoleEnum, AgentType,
    TaskInput, TaskPriorityEnum,
    TaskInput, TaskPriorityEnum,
    TaskStatusEnum, TaskType, TeamInput,
    TaskStatusEnum, TaskType, TeamInput,
    TeamType)
    TeamType)


    @strawberry.type
    @strawberry.type
    class AgentTeamQuery:
    class AgentTeamQuery:
    """Agent team query resolvers."""

    @strawberry.field
    async def agents(
    self,
    info: Info,
    team_id: Optional[str] = None,
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    ) -> List[AgentType]:
    """
    """
    Get a list of agents.
    Get a list of agents.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    team_id: Filter by team ID
    team_id: Filter by team ID
    limit: Maximum number of agents to return
    limit: Maximum number of agents to return
    offset: Number of agents to skip
    offset: Number of agents to skip


    Returns:
    Returns:
    List of agents
    List of agents
    """
    """
    # Get agent team service from context
    # Get agent team service from context
    service = info.context["services"].get("agent_team")
    service = info.context["services"].get("agent_team")
    if not service:
    if not service:
    logger.warning("Agent team service not available")
    logger.warning("Agent team service not available")
    return []
    return []


    # Get agents from service
    # Get agents from service
    try:
    try:
    agents = await service.get_agents(
    agents = await service.get_agents(
    team_id=team_id, limit=limit, offset=offset
    team_id=team_id, limit=limit, offset=offset
    )
    )


    return [
    return [
    AgentType(
    AgentType(
    id=str(agent.id),
    id=str(agent.id),
    name=agent.name,
    name=agent.name,
    description=agent.description,
    description=agent.description,
    role=AgentRoleEnum(agent.role),
    role=AgentRoleEnum(agent.role),
    capabilities=agent.capabilities,
    capabilities=agent.capabilities,
    model_id=str(agent.model_id) if agent.model_id else None,
    model_id=str(agent.model_id) if agent.model_id else None,
    created_at=(
    created_at=(
    agent.created_at.isoformat() if agent.created_at else None
    agent.created_at.isoformat() if agent.created_at else None
    ),
    ),
    updated_at=(
    updated_at=(
    agent.updated_at.isoformat() if agent.updated_at else None
    agent.updated_at.isoformat() if agent.updated_at else None
    ),
    ),
    )
    )
    for agent in agents
    for agent in agents
    ]
    ]
except Exception as e:
except Exception as e:
    logger.error(f"Error getting agents: {str(e)}")
    logger.error(f"Error getting agents: {str(e)}")
    return []
    return []


    @strawberry.field
    @strawberry.field
    async def agent(self, info: Info, id: str) -> Optional[AgentType]:
    async def agent(self, info: Info, id: str) -> Optional[AgentType]:
    """
    """
    Get an agent by ID.
    Get an agent by ID.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    id: Agent ID
    id: Agent ID


    Returns:
    Returns:
    Agent if found, None otherwise
    Agent if found, None otherwise
    """
    """
    # Get agent team service from context
    # Get agent team service from context
    service = info.context["services"].get("agent_team")
    service = info.context["services"].get("agent_team")
    if not service:
    if not service:
    logger.warning("Agent team service not available")
    logger.warning("Agent team service not available")
    return None
    return None


    # Get agent from service
    # Get agent from service
    try:
    try:
    agent = await service.get_agent(id)
    agent = await service.get_agent(id)
    if not agent:
    if not agent:
    return None
    return None


    return AgentType(
    return AgentType(
    id=str(agent.id),
    id=str(agent.id),
    name=agent.name,
    name=agent.name,
    description=agent.description,
    description=agent.description,
    role=AgentRoleEnum(agent.role),
    role=AgentRoleEnum(agent.role),
    capabilities=agent.capabilities,
    capabilities=agent.capabilities,
    model_id=str(agent.model_id) if agent.model_id else None,
    model_id=str(agent.model_id) if agent.model_id else None,
    created_at=(
    created_at=(
    agent.created_at.isoformat() if agent.created_at else None
    agent.created_at.isoformat() if agent.created_at else None
    ),
    ),
    updated_at=(
    updated_at=(
    agent.updated_at.isoformat() if agent.updated_at else None
    agent.updated_at.isoformat() if agent.updated_at else None
    ),
    ),
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error getting agent: {str(e)}")
    logger.error(f"Error getting agent: {str(e)}")
    return None
    return None


    @strawberry.field
    @strawberry.field
    async def teams(
    async def teams(
    self, info: Info, limit: Optional[int] = 10, offset: Optional[int] = 0
    self, info: Info, limit: Optional[int] = 10, offset: Optional[int] = 0
    ) -> List[TeamType]:
    ) -> List[TeamType]:
    """
    """
    Get a list of teams.
    Get a list of teams.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    limit: Maximum number of teams to return
    limit: Maximum number of teams to return
    offset: Number of teams to skip
    offset: Number of teams to skip


    Returns:
    Returns:
    List of teams
    List of teams
    """
    """
    # Get agent team service from context
    # Get agent team service from context
    service = info.context["services"].get("agent_team")
    service = info.context["services"].get("agent_team")
    if not service:
    if not service:
    logger.warning("Agent team service not available")
    logger.warning("Agent team service not available")
    return []
    return []


    # Get teams from service
    # Get teams from service
    try:
    try:
    teams = await service.get_teams(limit=limit, offset=offset)
    teams = await service.get_teams(limit=limit, offset=offset)


    return [
    return [
    TeamType(
    TeamType(
    id=str(team.id),
    id=str(team.id),
    name=team.name,
    name=team.name,
    description=team.description,
    description=team.description,
    created_at=(
    created_at=(
    team.created_at.isoformat() if team.created_at else None
    team.created_at.isoformat() if team.created_at else None
    ),
    ),
    updated_at=(
    updated_at=(
    team.updated_at.isoformat() if team.updated_at else None
    team.updated_at.isoformat() if team.updated_at else None
    ),
    ),
    )
    )
    for team in teams
    for team in teams
    ]
    ]
except Exception as e:
except Exception as e:
    logger.error(f"Error getting teams: {str(e)}")
    logger.error(f"Error getting teams: {str(e)}")
    return []
    return []


    @strawberry.field
    @strawberry.field
    async def tasks(
    async def tasks(
    self,
    self,
    info: Info,
    info: Info,
    team_id: Optional[str] = None,
    team_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    status: Optional[TaskStatusEnum] = None,
    status: Optional[TaskStatusEnum] = None,
    limit: Optional[int] = 10,
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    offset: Optional[int] = 0,
    ) -> List[TaskType]:
    ) -> List[TaskType]:
    """
    """
    Get a list of tasks.
    Get a list of tasks.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    team_id: Filter by team ID
    team_id: Filter by team ID
    agent_id: Filter by agent ID
    agent_id: Filter by agent ID
    status: Filter by task status
    status: Filter by task status
    limit: Maximum number of tasks to return
    limit: Maximum number of tasks to return
    offset: Number of tasks to skip
    offset: Number of tasks to skip


    Returns:
    Returns:
    List of tasks
    List of tasks
    """
    """
    # Get agent team service from context
    # Get agent team service from context
    service = info.context["services"].get("agent_team")
    service = info.context["services"].get("agent_team")
    if not service:
    if not service:
    logger.warning("Agent team service not available")
    logger.warning("Agent team service not available")
    return []
    return []


    # Get tasks from service
    # Get tasks from service
    try:
    try:
    tasks = await service.get_tasks(
    tasks = await service.get_tasks(
    team_id=team_id,
    team_id=team_id,
    agent_id=agent_id,
    agent_id=agent_id,
    status=status.value if status else None,
    status=status.value if status else None,
    limit=limit,
    limit=limit,
    offset=offset,
    offset=offset,
    )
    )


    return [
    return [
    TaskType(
    TaskType(
    id=str(task.id),
    id=str(task.id),
    team_id=str(task.team_id) if task.team_id else None,
    team_id=str(task.team_id) if task.team_id else None,
    agent_id=str(task.agent_id) if task.agent_id else None,
    agent_id=str(task.agent_id) if task.agent_id else None,
    title=task.title,
    title=task.title,
    description=task.description,
    description=task.description,
    status=TaskStatusEnum(task.status),
    status=TaskStatusEnum(task.status),
    priority=TaskPriorityEnum(task.priority),
    priority=TaskPriorityEnum(task.priority),
    due_date=task.due_date.isoformat() if task.due_date else None,
    due_date=task.due_date.isoformat() if task.due_date else None,
    created_at=(
    created_at=(
    task.created_at.isoformat() if task.created_at else None
    task.created_at.isoformat() if task.created_at else None
    ),
    ),
    updated_at=(
    updated_at=(
    task.updated_at.isoformat() if task.updated_at else None
    task.updated_at.isoformat() if task.updated_at else None
    ),
    ),
    )
    )
    for task in tasks
    for task in tasks
    ]
    ]
except Exception as e:
except Exception as e:
    logger.error(f"Error getting tasks: {str(e)}")
    logger.error(f"Error getting tasks: {str(e)}")
    return []
    return []


    @strawberry.type
    @strawberry.type
    class AgentTeamMutation:
    class AgentTeamMutation:
    """Agent team mutation resolvers."""

    @strawberry.mutation
    async def create_agent(
    self, info: Info, input: AgentInput
    ) -> Optional[AgentType]:
    """
    """
    Create a new agent.
    Create a new agent.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    input: Agent input
    input: Agent input


    Returns:
    Returns:
    Created agent if successful, None otherwise
    Created agent if successful, None otherwise
    """
    """
    # Get agent team service from context
    # Get agent team service from context
    service = info.context["services"].get("agent_team")
    service = info.context["services"].get("agent_team")
    if not service:
    if not service:
    logger.warning("Agent team service not available")
    logger.warning("Agent team service not available")
    return None
    return None


    # Create agent
    # Create agent
    try:
    try:
    agent = await service.create_agent(
    agent = await service.create_agent(
    name=input.name,
    name=input.name,
    description=input.description,
    description=input.description,
    role=input.role.value,
    role=input.role.value,
    capabilities=input.capabilities,
    capabilities=input.capabilities,
    model_id=input.model_id,
    model_id=input.model_id,
    )
    )


    return AgentType(
    return AgentType(
    id=str(agent.id),
    id=str(agent.id),
    name=agent.name,
    name=agent.name,
    description=agent.description,
    description=agent.description,
    role=AgentRoleEnum(agent.role),
    role=AgentRoleEnum(agent.role),
    capabilities=agent.capabilities,
    capabilities=agent.capabilities,
    model_id=str(agent.model_id) if agent.model_id else None,
    model_id=str(agent.model_id) if agent.model_id else None,
    created_at=(
    created_at=(
    agent.created_at.isoformat() if agent.created_at else None
    agent.created_at.isoformat() if agent.created_at else None
    ),
    ),
    updated_at=(
    updated_at=(
    agent.updated_at.isoformat() if agent.updated_at else None
    agent.updated_at.isoformat() if agent.updated_at else None
    ),
    ),
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error creating agent: {str(e)}")
    logger.error(f"Error creating agent: {str(e)}")
    return None
    return None


    @strawberry.mutation
    @strawberry.mutation
    async def update_agent(
    async def update_agent(
    self, info: Info, id: str, input: AgentInput
    self, info: Info, id: str, input: AgentInput
    ) -> Optional[AgentType]:
    ) -> Optional[AgentType]:
    """
    """
    Update an agent.
    Update an agent.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    id: Agent ID
    id: Agent ID
    input: Agent input
    input: Agent input


    Returns:
    Returns:
    Updated agent if successful, None otherwise
    Updated agent if successful, None otherwise
    """
    """
    # Get agent team service from context
    # Get agent team service from context
    service = info.context["services"].get("agent_team")
    service = info.context["services"].get("agent_team")
    if not service:
    if not service:
    logger.warning("Agent team service not available")
    logger.warning("Agent team service not available")
    return None
    return None


    # Update agent
    # Update agent
    try:
    try:
    agent = await service.update_agent(
    agent = await service.update_agent(
    id=id,
    id=id,
    name=input.name,
    name=input.name,
    description=input.description,
    description=input.description,
    role=input.role.value,
    role=input.role.value,
    capabilities=input.capabilities,
    capabilities=input.capabilities,
    model_id=input.model_id,
    model_id=input.model_id,
    )
    )


    if not agent:
    if not agent:
    return None
    return None


    return AgentType(
    return AgentType(
    id=str(agent.id),
    id=str(agent.id),
    name=agent.name,
    name=agent.name,
    description=agent.description,
    description=agent.description,
    role=AgentRoleEnum(agent.role),
    role=AgentRoleEnum(agent.role),
    capabilities=agent.capabilities,
    capabilities=agent.capabilities,
    model_id=str(agent.model_id) if agent.model_id else None,
    model_id=str(agent.model_id) if agent.model_id else None,
    created_at=(
    created_at=(
    agent.created_at.isoformat() if agent.created_at else None
    agent.created_at.isoformat() if agent.created_at else None
    ),
    ),
    updated_at=(
    updated_at=(
    agent.updated_at.isoformat() if agent.updated_at else None
    agent.updated_at.isoformat() if agent.updated_at else None
    ),
    ),
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error updating agent: {str(e)}")
    logger.error(f"Error updating agent: {str(e)}")
    return None
    return None


    @strawberry.mutation
    @strawberry.mutation
    async def delete_agent(self, info: Info, id: str) -> bool:
    async def delete_agent(self, info: Info, id: str) -> bool:
    """
    """
    Delete an agent.
    Delete an agent.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    id: Agent ID
    id: Agent ID


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    # Get agent team service from context
    # Get agent team service from context
    service = info.context["services"].get("agent_team")
    service = info.context["services"].get("agent_team")
    if not service:
    if not service:
    logger.warning("Agent team service not available")
    logger.warning("Agent team service not available")
    return False
    return False


    # Delete agent
    # Delete agent
    try:
    try:
    success = await service.delete_agent(id)
    success = await service.delete_agent(id)
    return success
    return success
except Exception as e:
except Exception as e:
    logger.error(f"Error deleting agent: {str(e)}")
    logger.error(f"Error deleting agent: {str(e)}")
    return False
    return False


    @strawberry.mutation
    @strawberry.mutation
    async def create_team(self, info: Info, input: TeamInput) -> Optional[TeamType]:
    async def create_team(self, info: Info, input: TeamInput) -> Optional[TeamType]:
    """
    """
    Create a new team.
    Create a new team.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    input: Team input
    input: Team input


    Returns:
    Returns:
    Created team if successful, None otherwise
    Created team if successful, None otherwise
    """
    """
    # Get agent team service from context
    # Get agent team service from context
    service = info.context["services"].get("agent_team")
    service = info.context["services"].get("agent_team")
    if not service:
    if not service:
    logger.warning("Agent team service not available")
    logger.warning("Agent team service not available")
    return None
    return None


    # Create team
    # Create team
    try:
    try:
    team = await service.create_team(
    team = await service.create_team(
    name=input.name,
    name=input.name,
    description=input.description,
    description=input.description,
    agent_ids=input.agent_ids,
    agent_ids=input.agent_ids,
    )
    )


    return TeamType(
    return TeamType(
    id=str(team.id),
    id=str(team.id),
    name=team.name,
    name=team.name,
    description=team.description,
    description=team.description,
    created_at=team.created_at.isoformat() if team.created_at else None,
    created_at=team.created_at.isoformat() if team.created_at else None,
    updated_at=team.updated_at.isoformat() if team.updated_at else None,
    updated_at=team.updated_at.isoformat() if team.updated_at else None,
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error creating team: {str(e)}")
    logger.error(f"Error creating team: {str(e)}")
    return None
    return None


    @strawberry.mutation
    @strawberry.mutation
    async def create_task(self, info: Info, input: TaskInput) -> Optional[TaskType]:
    async def create_task(self, info: Info, input: TaskInput) -> Optional[TaskType]:
    """
    """
    Create a new task.
    Create a new task.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    input: Task input
    input: Task input


    Returns:
    Returns:
    Created task if successful, None otherwise
    Created task if successful, None otherwise
    """
    """
    # Get agent team service from context
    # Get agent team service from context
    service = info.context["services"].get("agent_team")
    service = info.context["services"].get("agent_team")
    if not service:
    if not service:
    logger.warning("Agent team service not available")
    logger.warning("Agent team service not available")
    return None
    return None


    # Create task
    # Create task
    try:
    try:
    task = await service.create_task(
    task = await service.create_task(
    team_id=input.team_id,
    team_id=input.team_id,
    agent_id=input.agent_id,
    agent_id=input.agent_id,
    title=input.title,
    title=input.title,
    description=input.description,
    description=input.description,
    priority=input.priority.value,
    priority=input.priority.value,
    due_date=input.due_date,
    due_date=input.due_date,
    )
    )


    return TaskType(
    return TaskType(
    id=str(task.id),
    id=str(task.id),
    team_id=str(task.team_id) if task.team_id else None,
    team_id=str(task.team_id) if task.team_id else None,
    agent_id=str(task.agent_id) if task.agent_id else None,
    agent_id=str(task.agent_id) if task.agent_id else None,
    title=task.title,
    title=task.title,
    description=task.description,
    description=task.description,
    status=TaskStatusEnum(task.status),
    status=TaskStatusEnum(task.status),
    priority=TaskPriorityEnum(task.priority),
    priority=TaskPriorityEnum(task.priority),
    due_date=task.due_date.isoformat() if task.due_date else None,
    due_date=task.due_date.isoformat() if task.due_date else None,
    created_at=task.created_at.isoformat() if task.created_at else None,
    created_at=task.created_at.isoformat() if task.created_at else None,
    updated_at=task.updated_at.isoformat() if task.updated_at else None,
    updated_at=task.updated_at.isoformat() if task.updated_at else None,
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error creating task: {str(e)}")
    logger.error(f"Error creating task: {str(e)}")
    return None
    return None