"""
Agent Team GraphQL schema.

This module provides GraphQL types and resolvers for the agent team module.
"""

import logging
from typing import Any, Dict, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO, format=" % (asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    import strawberry
    from strawberry.types import Info

    STRAWBERRY_AVAILABLE = True
except ImportError:
    logger.warning("Strawberry GraphQL is required for GraphQL schema")
    STRAWBERRY_AVAILABLE = False

if STRAWBERRY_AVAILABLE:

    @strawberry.type
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
        """Agent team information"""

        id: strawberry.ID
        name: str
        description: str
        agents: List[AgentProfile]
        created_at: str
        updated_at: Optional[str]

    @strawberry.type
    class AgentMessage:
        """Message from an agent"""

        id: strawberry.ID
        agent_id: strawberry.ID
        agent_name: str
        content: str
        timestamp: str

    @strawberry.type
    class AgentConversation:
        """Conversation with agent team"""

        id: strawberry.ID
        team_id: strawberry.ID
        topic: str
        messages: List[AgentMessage]
        started_at: str
        updated_at: str

    @strawberry.input
    class AgentProfileInput:
        """Input for agent profile"""

        name: str
        description: str
        role: str
        capabilities: List[str]
        ai_model_id: Optional[strawberry.ID] = None
        parameters: Optional[Dict[str, Any]] = None

    @strawberry.input
    class CreateTeamInput:
        """Input for creating an agent team"""

        name: str
        description: str
        agent_profiles: List[AgentProfileInput]

    @strawberry.input
    class SendMessageInput:
        """Input for sending a message to an agent team"""

        team_id: strawberry.ID
        conversation_id: Optional[strawberry.ID] = None
        message: str
        topic: Optional[str] = None

    @strawberry.type
    class AgentTeamQuery:
        """Agent team query fields"""

        @strawberry.field
        def agent_profiles(self, info: Info) -> List[AgentProfile]:
            """
            Get all agent profiles.

            Returns:
                List of agent profiles
            """
            service = info.context["services"].get("agent_team")
            if not service:
                return []

            profiles = service.get_all_profiles()
            return [
                AgentProfile(
                    id=str(profile.id),
                    name=profile.name,
                    description=profile.description,
                    role=profile.role,
                    capabilities=profile.capabilities,
                    ai_model_id=str(profile.ai_model_id) if profile.ai_model_id else None,
                        
                    parameters=profile.parameters,
                )
                for profile in profiles
            ]

        @strawberry.field
        def agent_teams(self, info: Info) -> List[AgentTeam]:
            """
            Get all agent teams.

            Returns:
                List of agent teams
            """
            service = info.context["services"].get("agent_team")
            if not service:
                return []

            teams = service.get_all_teams()
            return [
                AgentTeam(
                    id=str(team.id),
                    name=team.name,
                    description=team.description,
                    agents=[
                        AgentProfile(
                            id=str(agent.id),
                            name=agent.name,
                            description=agent.description,
                            role=agent.role,
                            capabilities=agent.capabilities,
                            ai_model_id=str(agent.ai_model_id) if agent.ai_model_id else None,
                                
                            parameters=agent.parameters,
                        )
                        for agent in team.agents
                    ],
                    created_at=team.created_at.isoformat(),
                    updated_at=team.updated_at.isoformat() if team.updated_at else None,
                )
                for team in teams
            ]

        @strawberry.field
        def agent_team(self, info: Info, id: strawberry.ID) -> Optional[AgentTeam]:
            """
            Get a specific agent team.

            Args:
                id: ID of the agent team

            Returns:
                Agent team if found, None otherwise
            """
            service = info.context["services"].get("agent_team")
            if not service:
                return None

            team = service.get_team(id)
            if not team:
                return None

            return AgentTeam(
                id=str(team.id),
                name=team.name,
                description=team.description,
                agents=[
                    AgentProfile(
                        id=str(agent.id),
                        name=agent.name,
                        description=agent.description,
                        role=agent.role,
                        capabilities=agent.capabilities,
                        ai_model_id=str(agent.ai_model_id) if agent.ai_model_id else None,
                            
                        parameters=agent.parameters,
                    )
                    for agent in team.agents
                ],
                created_at=team.created_at.isoformat(),
                updated_at=team.updated_at.isoformat() if team.updated_at else None,
            )

        @strawberry.field
        def agent_conversations(
            self, info: Info, team_id: Optional[strawberry.ID] = None
        ) -> List[AgentConversation]:
            """
            Get agent conversations, optionally filtered by team ID.

            Args:
                team_id: Optional team ID to filter by

            Returns:
                List of agent conversations
            """
            service = info.context["services"].get("agent_team")
            if not service:
                return []

            conversations = service.get_conversations(team_id=team_id)
            return [
                AgentConversation(
                    id=str(conversation.id),
                    team_id=str(conversation.team_id),
                    topic=conversation.topic,
                    messages=[
                        AgentMessage(
                            id=str(message.id),
                            agent_id=str(message.agent_id),
                            agent_name=message.agent_name,
                            content=message.content,
                            timestamp=message.timestamp.isoformat(),
                        )
                        for message in conversation.messages
                    ],
                    started_at=conversation.started_at.isoformat(),
                    updated_at=conversation.updated_at.isoformat(),
                )
                for conversation in conversations
            ]

        @strawberry.field
        def agent_conversation(self, info: Info, 
            id: strawberry.ID) -> Optional[AgentConversation]:
            """
            Get a specific agent conversation.

            Args:
                id: ID of the agent conversation

            Returns:
                Agent conversation if found, None otherwise
            """
            service = info.context["services"].get("agent_team")
            if not service:
                return None

            conversation = service.get_conversation(id)
            if not conversation:
                return None

            return AgentConversation(
                id=str(conversation.id),
                team_id=str(conversation.team_id),
                topic=conversation.topic,
                messages=[
                    AgentMessage(
                        id=str(message.id),
                        agent_id=str(message.agent_id),
                        agent_name=message.agent_name,
                        content=message.content,
                        timestamp=message.timestamp.isoformat(),
                    )
                    for message in conversation.messages
                ],
                started_at=conversation.started_at.isoformat(),
                updated_at=conversation.updated_at.isoformat(),
            )

    @strawberry.type
    class AgentTeamMutation:
        """Agent team mutation fields"""

        @strawberry.mutation
        async def create_agent_team(self, info: Info, 
            input: CreateTeamInput) -> AgentTeam:
            """
            Create a new agent team.

            Args:
                input: Team creation input

            Returns:
                Created agent team
            """
            service = info.context["services"].get("agent_team")
            if not service:
                raise ValueError("Agent team service not available")

            # Convert agent profiles
            agent_profiles = [
                {
                    "name": profile.name,
                    "description": profile.description,
                    "role": profile.role,
                    "capabilities": profile.capabilities,
                    "ai_model_id": profile.ai_model_id,
                    "parameters": profile.parameters,
                }
                for profile in input.agent_profiles
            ]

            # Create team
            team = await service.create_team(
                name=input.name, description=input.description, 
                    agent_profiles=agent_profiles
            )

            return AgentTeam(
                id=str(team.id),
                name=team.name,
                description=team.description,
                agents=[
                    AgentProfile(
                        id=str(agent.id),
                        name=agent.name,
                        description=agent.description,
                        role=agent.role,
                        capabilities=agent.capabilities,
                        ai_model_id=str(agent.ai_model_id) if agent.ai_model_id else None,
                            
                        parameters=agent.parameters,
                    )
                    for agent in team.agents
                ],
                created_at=team.created_at.isoformat(),
                updated_at=team.updated_at.isoformat() if team.updated_at else None,
            )

        @strawberry.mutation
        async def send_message_to_team(
            self, info: Info, input: SendMessageInput
        ) -> AgentConversation:
            """
            Send a message to an agent team.

            Args:
                input: Message input

            Returns:
                Updated conversation with agent responses
            """
            service = info.context["services"].get("agent_team")
            if not service:
                raise ValueError("Agent team service not available")

            # Send message
            conversation = await service.send_message(
                team_id=input.team_id,
                conversation_id=input.conversation_id,
                message=input.message,
                topic=input.topic,
            )

            return AgentConversation(
                id=str(conversation.id),
                team_id=str(conversation.team_id),
                topic=conversation.topic,
                messages=[
                    AgentMessage(
                        id=str(message.id),
                        agent_id=str(message.agent_id),
                        agent_name=message.agent_name,
                        content=message.content,
                        timestamp=message.timestamp.isoformat(),
                    )
                    for message in conversation.messages
                ],
                started_at=conversation.started_at.isoformat(),
                updated_at=conversation.updated_at.isoformat(),
            )

else:
    # Fallbacks if Strawberry isn't available
    class AgentTeamQuery:
        pass

    class AgentTeamMutation:
        pass
