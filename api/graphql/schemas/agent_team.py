"""
"""
Agent Team GraphQL schema.
Agent Team GraphQL schema.


This module provides GraphQL types and resolvers for the agent team module.
This module provides GraphQL types and resolvers for the agent team module.
"""
"""




import logging
import logging
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


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
    logger.warning("Strawberry GraphQL is required for GraphQL schema")
    logger.warning("Strawberry GraphQL is required for GraphQL schema")
    STRAWBERRY_AVAILABLE = False
    STRAWBERRY_AVAILABLE = False


    if STRAWBERRY_AVAILABLE:
    if STRAWBERRY_AVAILABLE:


    @strawberry.type
    @strawberry.type
    class AgentProfile:
    class AgentProfile:
    """Agent profile information"""

    id: strawberry.ID
    name: str
    description: str
    role: str
    capabilities: List[str]
    ai_model_id: Optional[strawberry.ID]
    parameters: Optional[Dict[str, Any]]

    @strawberry.type
    class AgentTeam:

    id: strawberry.ID
    name: str
    description: str
    agents: List[AgentProfile]
    created_at: str
    updated_at: Optional[str]

    @strawberry.type
    class AgentMessage:

    id: strawberry.ID
    agent_id: strawberry.ID
    agent_name: str
    content: str
    timestamp: str

    @strawberry.type
    class AgentConversation:

    id: strawberry.ID
    team_id: strawberry.ID
    topic: str
    messages: List[AgentMessage]
    started_at: str
    updated_at: str

    @strawberry.input
    class AgentProfileInput:


    name: str
    name: str
    description: str
    description: str
    role: str
    role: str
    capabilities: List[str]
    capabilities: List[str]
    ai_model_id: Optional[strawberry.ID] = None
    ai_model_id: Optional[strawberry.ID] = None
    parameters: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None


    @strawberry.input
    @strawberry.input
    class CreateTeamInput:
    class CreateTeamInput:


    name: str
    name: str
    description: str
    description: str
    agent_profiles: List[AgentProfileInput]
    agent_profiles: List[AgentProfileInput]


    @strawberry.input
    @strawberry.input
    class SendMessageInput:
    class SendMessageInput:


    team_id: strawberry.ID
    team_id: strawberry.ID
    conversation_id: Optional[strawberry.ID] = None
    conversation_id: Optional[strawberry.ID] = None
    message: str
    message: str
    topic: Optional[str] = None
    topic: Optional[str] = None


    @strawberry.type
    @strawberry.type
    class AgentTeamQuery:
    class AgentTeamQuery:


    @strawberry.field
    @strawberry.field
    def agent_profiles(self, info: Info) -> List[AgentProfile]:
    def agent_profiles(self, info: Info) -> List[AgentProfile]:
    """
    """
    Get all agent profiles.
    Get all agent profiles.


    Returns:
    Returns:
    List of agent profiles
    List of agent profiles
    """
    """
    service = info.context["services"].get("agent_team")
    service = info.context["services"].get("agent_team")
    if not service:
    if not service:
    return []
    return []


    profiles = service.get_all_profiles()
    profiles = service.get_all_profiles()
    return [
    return [
    AgentProfile(
    AgentProfile(
    id=str(profile.id),
    id=str(profile.id),
    name=profile.name,
    name=profile.name,
    description=profile.description,
    description=profile.description,
    role=profile.role,
    role=profile.role,
    capabilities=profile.capabilities,
    capabilities=profile.capabilities,
    ai_model_id=(
    ai_model_id=(
    str(profile.ai_model_id) if profile.ai_model_id else None
    str(profile.ai_model_id) if profile.ai_model_id else None
    ),
    ),
    parameters=profile.parameters,
    parameters=profile.parameters,
    )
    )
    for profile in profiles
    for profile in profiles
    ]
    ]


    @strawberry.field
    @strawberry.field
    def agent_teams(self, info: Info) -> List[AgentTeam]:
    def agent_teams(self, info: Info) -> List[AgentTeam]:
    """
    """
    Get all agent teams.
    Get all agent teams.


    Returns:
    Returns:
    List of agent teams
    List of agent teams
    """
    """
    service = info.context["services"].get("agent_team")
    service = info.context["services"].get("agent_team")
    if not service:
    if not service:
    return []
    return []


    teams = service.get_all_teams()
    teams = service.get_all_teams()
    return [
    return [
    AgentTeam(
    AgentTeam(
    id=str(team.id),
    id=str(team.id),
    name=team.name,
    name=team.name,
    description=team.description,
    description=team.description,
    agents=[
    agents=[
    AgentProfile(
    AgentProfile(
    id=str(agent.id),
    id=str(agent.id),
    name=agent.name,
    name=agent.name,
    description=agent.description,
    description=agent.description,
    role=agent.role,
    role=agent.role,
    capabilities=agent.capabilities,
    capabilities=agent.capabilities,
    ai_model_id=(
    ai_model_id=(
    str(agent.ai_model_id) if agent.ai_model_id else None
    str(agent.ai_model_id) if agent.ai_model_id else None
    ),
    ),
    parameters=agent.parameters,
    parameters=agent.parameters,
    )
    )
    for agent in team.agents
    for agent in team.agents
    ],
    ],
    created_at=team.created_at.isoformat(),
    created_at=team.created_at.isoformat(),
    updated_at=team.updated_at.isoformat() if team.updated_at else None,
    updated_at=team.updated_at.isoformat() if team.updated_at else None,
    )
    )
    for team in teams
    for team in teams
    ]
    ]


    @strawberry.field
    @strawberry.field
    def agent_team(self, info: Info, id: strawberry.ID) -> Optional[AgentTeam]:
    def agent_team(self, info: Info, id: strawberry.ID) -> Optional[AgentTeam]:
    """
    """
    Get a specific agent team.
    Get a specific agent team.


    Args:
    Args:
    id: ID of the agent team
    id: ID of the agent team


    Returns:
    Returns:
    Agent team if found, None otherwise
    Agent team if found, None otherwise
    """
    """
    service = info.context["services"].get("agent_team")
    service = info.context["services"].get("agent_team")
    if not service:
    if not service:
    return None
    return None


    team = service.get_team(id)
    team = service.get_team(id)
    if not team:
    if not team:
    return None
    return None


    return AgentTeam(
    return AgentTeam(
    id=str(team.id),
    id=str(team.id),
    name=team.name,
    name=team.name,
    description=team.description,
    description=team.description,
    agents=[
    agents=[
    AgentProfile(
    AgentProfile(
    id=str(agent.id),
    id=str(agent.id),
    name=agent.name,
    name=agent.name,
    description=agent.description,
    description=agent.description,
    role=agent.role,
    role=agent.role,
    capabilities=agent.capabilities,
    capabilities=agent.capabilities,
    ai_model_id=(
    ai_model_id=(
    str(agent.ai_model_id) if agent.ai_model_id else None
    str(agent.ai_model_id) if agent.ai_model_id else None
    ),
    ),
    parameters=agent.parameters,
    parameters=agent.parameters,
    )
    )
    for agent in team.agents
    for agent in team.agents
    ],
    ],
    created_at=team.created_at.isoformat(),
    created_at=team.created_at.isoformat(),
    updated_at=team.updated_at.isoformat() if team.updated_at else None,
    updated_at=team.updated_at.isoformat() if team.updated_at else None,
    )
    )


    @strawberry.field
    @strawberry.field
    def agent_conversations(
    def agent_conversations(
    self, info: Info, team_id: Optional[strawberry.ID] = None
    self, info: Info, team_id: Optional[strawberry.ID] = None
    ) -> List[AgentConversation]:
    ) -> List[AgentConversation]:
    """
    """
    Get agent conversations, optionally filtered by team ID.
    Get agent conversations, optionally filtered by team ID.


    Args:
    Args:
    team_id: Optional team ID to filter by
    team_id: Optional team ID to filter by


    Returns:
    Returns:
    List of agent conversations
    List of agent conversations
    """
    """
    service = info.context["services"].get("agent_team")
    service = info.context["services"].get("agent_team")
    if not service:
    if not service:
    return []
    return []


    conversations = service.get_conversations(team_id=team_id)
    conversations = service.get_conversations(team_id=team_id)
    return [
    return [
    AgentConversation(
    AgentConversation(
    id=str(conversation.id),
    id=str(conversation.id),
    team_id=str(conversation.team_id),
    team_id=str(conversation.team_id),
    topic=conversation.topic,
    topic=conversation.topic,
    messages=[
    messages=[
    AgentMessage(
    AgentMessage(
    id=str(message.id),
    id=str(message.id),
    agent_id=str(message.agent_id),
    agent_id=str(message.agent_id),
    agent_name=message.agent_name,
    agent_name=message.agent_name,
    content=message.content,
    content=message.content,
    timestamp=message.timestamp.isoformat(),
    timestamp=message.timestamp.isoformat(),
    )
    )
    for message in conversation.messages
    for message in conversation.messages
    ],
    ],
    started_at=conversation.started_at.isoformat(),
    started_at=conversation.started_at.isoformat(),
    updated_at=conversation.updated_at.isoformat(),
    updated_at=conversation.updated_at.isoformat(),
    )
    )
    for conversation in conversations
    for conversation in conversations
    ]
    ]


    @strawberry.field
    @strawberry.field
    def agent_conversation(
    def agent_conversation(
    self, info: Info, id: strawberry.ID
    self, info: Info, id: strawberry.ID
    ) -> Optional[AgentConversation]:
    ) -> Optional[AgentConversation]:
    """
    """
    Get a specific agent conversation.
    Get a specific agent conversation.


    Args:
    Args:
    id: ID of the agent conversation
    id: ID of the agent conversation


    Returns:
    Returns:
    Agent conversation if found, None otherwise
    Agent conversation if found, None otherwise
    """
    """
    service = info.context["services"].get("agent_team")
    service = info.context["services"].get("agent_team")
    if not service:
    if not service:
    return None
    return None


    conversation = service.get_conversation(id)
    conversation = service.get_conversation(id)
    if not conversation:
    if not conversation:
    return None
    return None


    return AgentConversation(
    return AgentConversation(
    id=str(conversation.id),
    id=str(conversation.id),
    team_id=str(conversation.team_id),
    team_id=str(conversation.team_id),
    topic=conversation.topic,
    topic=conversation.topic,
    messages=[
    messages=[
    AgentMessage(
    AgentMessage(
    id=str(message.id),
    id=str(message.id),
    agent_id=str(message.agent_id),
    agent_id=str(message.agent_id),
    agent_name=message.agent_name,
    agent_name=message.agent_name,
    content=message.content,
    content=message.content,
    timestamp=message.timestamp.isoformat(),
    timestamp=message.timestamp.isoformat(),
    )
    )
    for message in conversation.messages
    for message in conversation.messages
    ],
    ],
    started_at=conversation.started_at.isoformat(),
    started_at=conversation.started_at.isoformat(),
    updated_at=conversation.updated_at.isoformat(),
    updated_at=conversation.updated_at.isoformat(),
    )
    )


    @strawberry.type
    @strawberry.type
    class AgentTeamMutation:
    class AgentTeamMutation:
    """Agent team mutation fields"""

    @strawberry.mutation
    async def create_agent_team(
    self, info: Info, input: CreateTeamInput
    ) -> AgentTeam:
    """
    """
    Create a new agent team.
    Create a new agent team.


    Args:
    Args:
    input: Team creation input
    input: Team creation input


    Returns:
    Returns:
    Created agent team
    Created agent team
    """
    """
    service = info.context["services"].get("agent_team")
    service = info.context["services"].get("agent_team")
    if not service:
    if not service:
    raise ValueError("Agent team service not available")
    raise ValueError("Agent team service not available")


    # Convert agent profiles
    # Convert agent profiles
    agent_profiles = [
    agent_profiles = [
    {
    {
    "name": profile.name,
    "name": profile.name,
    "description": profile.description,
    "description": profile.description,
    "role": profile.role,
    "role": profile.role,
    "capabilities": profile.capabilities,
    "capabilities": profile.capabilities,
    "ai_model_id": profile.ai_model_id,
    "ai_model_id": profile.ai_model_id,
    "parameters": profile.parameters,
    "parameters": profile.parameters,
    }
    }
    for profile in input.agent_profiles
    for profile in input.agent_profiles
    ]
    ]


    # Create team
    # Create team
    team = await service.create_team(
    team = await service.create_team(
    name=input.name,
    name=input.name,
    description=input.description,
    description=input.description,
    agent_profiles=agent_profiles,
    agent_profiles=agent_profiles,
    )
    )


    return AgentTeam(
    return AgentTeam(
    id=str(team.id),
    id=str(team.id),
    name=team.name,
    name=team.name,
    description=team.description,
    description=team.description,
    agents=[
    agents=[
    AgentProfile(
    AgentProfile(
    id=str(agent.id),
    id=str(agent.id),
    name=agent.name,
    name=agent.name,
    description=agent.description,
    description=agent.description,
    role=agent.role,
    role=agent.role,
    capabilities=agent.capabilities,
    capabilities=agent.capabilities,
    ai_model_id=(
    ai_model_id=(
    str(agent.ai_model_id) if agent.ai_model_id else None
    str(agent.ai_model_id) if agent.ai_model_id else None
    ),
    ),
    parameters=agent.parameters,
    parameters=agent.parameters,
    )
    )
    for agent in team.agents
    for agent in team.agents
    ],
    ],
    created_at=team.created_at.isoformat(),
    created_at=team.created_at.isoformat(),
    updated_at=team.updated_at.isoformat() if team.updated_at else None,
    updated_at=team.updated_at.isoformat() if team.updated_at else None,
    )
    )


    @strawberry.mutation
    @strawberry.mutation
    async def send_message_to_team(
    async def send_message_to_team(
    self, info: Info, input: SendMessageInput
    self, info: Info, input: SendMessageInput
    ) -> AgentConversation:
    ) -> AgentConversation:
    """
    """
    Send a message to an agent team.
    Send a message to an agent team.


    Args:
    Args:
    input: Message input
    input: Message input


    Returns:
    Returns:
    Updated conversation with agent responses
    Updated conversation with agent responses
    """
    """
    service = info.context["services"].get("agent_team")
    service = info.context["services"].get("agent_team")
    if not service:
    if not service:
    raise ValueError("Agent team service not available")
    raise ValueError("Agent team service not available")


    # Send message
    # Send message
    conversation = await service.send_message(
    conversation = await service.send_message(
    team_id=input.team_id,
    team_id=input.team_id,
    conversation_id=input.conversation_id,
    conversation_id=input.conversation_id,
    message=input.message,
    message=input.message,
    topic=input.topic,
    topic=input.topic,
    )
    )


    return AgentConversation(
    return AgentConversation(
    id=str(conversation.id),
    id=str(conversation.id),
    team_id=str(conversation.team_id),
    team_id=str(conversation.team_id),
    topic=conversation.topic,
    topic=conversation.topic,
    messages=[
    messages=[
    AgentMessage(
    AgentMessage(
    id=str(message.id),
    id=str(message.id),
    agent_id=str(message.agent_id),
    agent_id=str(message.agent_id),
    agent_name=message.agent_name,
    agent_name=message.agent_name,
    content=message.content,
    content=message.content,
    timestamp=message.timestamp.isoformat(),
    timestamp=message.timestamp.isoformat(),
    )
    )
    for message in conversation.messages
    for message in conversation.messages
    ],
    ],
    started_at=conversation.started_at.isoformat(),
    started_at=conversation.started_at.isoformat(),
    updated_at=conversation.updated_at.isoformat(),
    updated_at=conversation.updated_at.isoformat(),
    )
    )


    else:
    else:
    # Fallbacks if Strawberry isn't available
    # Fallbacks if Strawberry isn't available
    class AgentTeamQuery:
    class AgentTeamQuery:
    pass
    pass


    class AgentTeamMutation:
    class AgentTeamMutation:
    pass
    pass