"""
"""
User GraphQL resolvers.
User GraphQL resolvers.


This module provides resolvers for user queries and mutations.
This module provides resolvers for user queries and mutations.
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
    from ..schemas.user import (CollaborationType, ProjectInput, ProjectType,
    from ..schemas.user import (CollaborationType, ProjectInput, ProjectType,
    UserInput, UserRoleEnum, UserType)
    UserInput, UserRoleEnum, UserType)


    @strawberry.type
    @strawberry.type
    class UserQuery:
    class UserQuery:
    """User query resolvers."""

    @strawberry.field
    async def me(self, info: Info) -> Optional[UserType]:
    """
    """
    Get the current authenticated user.
    Get the current authenticated user.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info


    Returns:
    Returns:
    Current user if authenticated, None otherwise
    Current user if authenticated, None otherwise
    """
    """
    # Get user from context
    # Get user from context
    user = info.context.get("user")
    user = info.context.get("user")
    if not user:
    if not user:
    return None
    return None


    return UserType(
    return UserType(
    id=str(user.id),
    id=str(user.id),
    username=user.username,
    username=user.username,
    email=user.email,
    email=user.email,
    full_name=user.full_name,
    full_name=user.full_name,
    role=UserRoleEnum(user.role),
    role=UserRoleEnum(user.role),
    created_at=user.created_at.isoformat() if user.created_at else None,
    created_at=user.created_at.isoformat() if user.created_at else None,
    updated_at=user.updated_at.isoformat() if user.updated_at else None,
    updated_at=user.updated_at.isoformat() if user.updated_at else None,
    )
    )


    @strawberry.field
    @strawberry.field
    async def users(
    async def users(
    self, info: Info, limit: Optional[int] = 10, offset: Optional[int] = 0
    self, info: Info, limit: Optional[int] = 10, offset: Optional[int] = 0
    ) -> List[UserType]:
    ) -> List[UserType]:
    """
    """
    Get a list of users.
    Get a list of users.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    limit: Maximum number of users to return
    limit: Maximum number of users to return
    offset: Number of users to skip
    offset: Number of users to skip


    Returns:
    Returns:
    List of users
    List of users
    """
    """
    # Get user service from context
    # Get user service from context
    service = info.context["services"].get("user")
    service = info.context["services"].get("user")
    if not service:
    if not service:
    logger.warning("User service not available")
    logger.warning("User service not available")
    return []
    return []


    # Get users from service
    # Get users from service
    try:
    try:
    users = await service.get_users(limit=limit, offset=offset)
    users = await service.get_users(limit=limit, offset=offset)


    return [
    return [
    UserType(
    UserType(
    id=str(user.id),
    id=str(user.id),
    username=user.username,
    username=user.username,
    email=user.email,
    email=user.email,
    full_name=user.full_name,
    full_name=user.full_name,
    role=UserRoleEnum(user.role),
    role=UserRoleEnum(user.role),
    created_at=(
    created_at=(
    user.created_at.isoformat() if user.created_at else None
    user.created_at.isoformat() if user.created_at else None
    ),
    ),
    updated_at=(
    updated_at=(
    user.updated_at.isoformat() if user.updated_at else None
    user.updated_at.isoformat() if user.updated_at else None
    ),
    ),
    )
    )
    for user in users
    for user in users
    ]
    ]
except Exception as e:
except Exception as e:
    logger.error(f"Error getting users: {str(e)}")
    logger.error(f"Error getting users: {str(e)}")
    return []
    return []


    @strawberry.field
    @strawberry.field
    async def user(self, info: Info, id: str) -> Optional[UserType]:
    async def user(self, info: Info, id: str) -> Optional[UserType]:
    """
    """
    Get a user by ID.
    Get a user by ID.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    id: User ID
    id: User ID


    Returns:
    Returns:
    User if found, None otherwise
    User if found, None otherwise
    """
    """
    # Get user service from context
    # Get user service from context
    service = info.context["services"].get("user")
    service = info.context["services"].get("user")
    if not service:
    if not service:
    logger.warning("User service not available")
    logger.warning("User service not available")
    return None
    return None


    # Get user from service
    # Get user from service
    try:
    try:
    user = await service.get_user(id)
    user = await service.get_user(id)
    if not user:
    if not user:
    return None
    return None


    return UserType(
    return UserType(
    id=str(user.id),
    id=str(user.id),
    username=user.username,
    username=user.username,
    email=user.email,
    email=user.email,
    full_name=user.full_name,
    full_name=user.full_name,
    role=UserRoleEnum(user.role),
    role=UserRoleEnum(user.role),
    created_at=user.created_at.isoformat() if user.created_at else None,
    created_at=user.created_at.isoformat() if user.created_at else None,
    updated_at=user.updated_at.isoformat() if user.updated_at else None,
    updated_at=user.updated_at.isoformat() if user.updated_at else None,
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error getting user: {str(e)}")
    logger.error(f"Error getting user: {str(e)}")
    return None
    return None


    @strawberry.field
    @strawberry.field
    async def projects(
    async def projects(
    self,
    self,
    info: Info,
    info: Info,
    user_id: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: Optional[int] = 10,
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    offset: Optional[int] = 0,
    ) -> List[ProjectType]:
    ) -> List[ProjectType]:
    """
    """
    Get a list of projects.
    Get a list of projects.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    user_id: Filter by user ID
    user_id: Filter by user ID
    limit: Maximum number of projects to return
    limit: Maximum number of projects to return
    offset: Number of projects to skip
    offset: Number of projects to skip


    Returns:
    Returns:
    List of projects
    List of projects
    """
    """
    # Get user service from context
    # Get user service from context
    service = info.context["services"].get("user")
    service = info.context["services"].get("user")
    if not service:
    if not service:
    logger.warning("User service not available")
    logger.warning("User service not available")
    return []
    return []


    # Get projects from service
    # Get projects from service
    try:
    try:
    projects = await service.get_projects(
    projects = await service.get_projects(
    user_id=user_id, limit=limit, offset=offset
    user_id=user_id, limit=limit, offset=offset
    )
    )


    return [
    return [
    ProjectType(
    ProjectType(
    id=str(project.id),
    id=str(project.id),
    user_id=str(project.user_id),
    user_id=str(project.user_id),
    name=project.name,
    name=project.name,
    description=project.description,
    description=project.description,
    is_public=project.is_public,
    is_public=project.is_public,
    created_at=(
    created_at=(
    project.created_at.isoformat()
    project.created_at.isoformat()
    if project.created_at
    if project.created_at
    else None
    else None
    ),
    ),
    updated_at=(
    updated_at=(
    project.updated_at.isoformat()
    project.updated_at.isoformat()
    if project.updated_at
    if project.updated_at
    else None
    else None
    ),
    ),
    )
    )
    for project in projects
    for project in projects
    ]
    ]
except Exception as e:
except Exception as e:
    logger.error(f"Error getting projects: {str(e)}")
    logger.error(f"Error getting projects: {str(e)}")
    return []
    return []


    @strawberry.type
    @strawberry.type
    class UserMutation:
    class UserMutation:
    """User mutation resolvers."""

    @strawberry.mutation
    async def create_user(self, info: Info, input: UserInput) -> Optional[UserType]:
    """
    """
    Create a new user.
    Create a new user.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    input: User input
    input: User input


    Returns:
    Returns:
    Created user if successful, None otherwise
    Created user if successful, None otherwise
    """
    """
    # Get user service from context
    # Get user service from context
    service = info.context["services"].get("user")
    service = info.context["services"].get("user")
    if not service:
    if not service:
    logger.warning("User service not available")
    logger.warning("User service not available")
    return None
    return None


    # Create user
    # Create user
    try:
    try:
    user = await service.create_user(
    user = await service.create_user(
    username=input.username,
    username=input.username,
    email=input.email,
    email=input.email,
    password=input.password,
    password=input.password,
    full_name=input.full_name,
    full_name=input.full_name,
    role=input.role.value,
    role=input.role.value,
    )
    )


    return UserType(
    return UserType(
    id=str(user.id),
    id=str(user.id),
    username=user.username,
    username=user.username,
    email=user.email,
    email=user.email,
    full_name=user.full_name,
    full_name=user.full_name,
    role=UserRoleEnum(user.role),
    role=UserRoleEnum(user.role),
    created_at=user.created_at.isoformat() if user.created_at else None,
    created_at=user.created_at.isoformat() if user.created_at else None,
    updated_at=user.updated_at.isoformat() if user.updated_at else None,
    updated_at=user.updated_at.isoformat() if user.updated_at else None,
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error creating user: {str(e)}")
    logger.error(f"Error creating user: {str(e)}")
    return None
    return None


    @strawberry.mutation
    @strawberry.mutation
    async def update_user(
    async def update_user(
    self, info: Info, id: str, input: UserInput
    self, info: Info, id: str, input: UserInput
    ) -> Optional[UserType]:
    ) -> Optional[UserType]:
    """
    """
    Update a user.
    Update a user.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    id: User ID
    id: User ID
    input: User input
    input: User input


    Returns:
    Returns:
    Updated user if successful, None otherwise
    Updated user if successful, None otherwise
    """
    """
    # Get user service from context
    # Get user service from context
    service = info.context["services"].get("user")
    service = info.context["services"].get("user")
    if not service:
    if not service:
    logger.warning("User service not available")
    logger.warning("User service not available")
    return None
    return None


    # Update user
    # Update user
    try:
    try:
    user = await service.update_user(
    user = await service.update_user(
    id=id,
    id=id,
    username=input.username,
    username=input.username,
    email=input.email,
    email=input.email,
    password=input.password,
    password=input.password,
    full_name=input.full_name,
    full_name=input.full_name,
    role=input.role.value,
    role=input.role.value,
    )
    )


    if not user:
    if not user:
    return None
    return None


    return UserType(
    return UserType(
    id=str(user.id),
    id=str(user.id),
    username=user.username,
    username=user.username,
    email=user.email,
    email=user.email,
    full_name=user.full_name,
    full_name=user.full_name,
    role=UserRoleEnum(user.role),
    role=UserRoleEnum(user.role),
    created_at=user.created_at.isoformat() if user.created_at else None,
    created_at=user.created_at.isoformat() if user.created_at else None,
    updated_at=user.updated_at.isoformat() if user.updated_at else None,
    updated_at=user.updated_at.isoformat() if user.updated_at else None,
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error updating user: {str(e)}")
    logger.error(f"Error updating user: {str(e)}")
    return None
    return None


    @strawberry.mutation
    @strawberry.mutation
    async def delete_user(self, info: Info, id: str) -> bool:
    async def delete_user(self, info: Info, id: str) -> bool:
    """
    """
    Delete a user.
    Delete a user.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    id: User ID
    id: User ID


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    # Get user service from context
    # Get user service from context
    service = info.context["services"].get("user")
    service = info.context["services"].get("user")
    if not service:
    if not service:
    logger.warning("User service not available")
    logger.warning("User service not available")
    return False
    return False


    # Delete user
    # Delete user
    try:
    try:
    success = await service.delete_user(id)
    success = await service.delete_user(id)
    return success
    return success
except Exception as e:
except Exception as e:
    logger.error(f"Error deleting user: {str(e)}")
    logger.error(f"Error deleting user: {str(e)}")
    return False
    return False


    @strawberry.mutation
    @strawberry.mutation
    async def create_project(
    async def create_project(
    self, info: Info, input: ProjectInput
    self, info: Info, input: ProjectInput
    ) -> Optional[ProjectType]:
    ) -> Optional[ProjectType]:
    """
    """
    Create a new project.
    Create a new project.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    input: Project input
    input: Project input


    Returns:
    Returns:
    Created project if successful, None otherwise
    Created project if successful, None otherwise
    """
    """
    # Get user service from context
    # Get user service from context
    service = info.context["services"].get("user")
    service = info.context["services"].get("user")
    if not service:
    if not service:
    logger.warning("User service not available")
    logger.warning("User service not available")
    return None
    return None


    # Get current user
    # Get current user
    user = info.context.get("user")
    user = info.context.get("user")
    if not user:
    if not user:
    logger.warning("User not authenticated")
    logger.warning("User not authenticated")
    return None
    return None


    # Create project
    # Create project
    try:
    try:
    project = await service.create_project(
    project = await service.create_project(
    user_id=str(user.id),
    user_id=str(user.id),
    name=input.name,
    name=input.name,
    description=input.description,
    description=input.description,
    is_public=input.is_public,
    is_public=input.is_public,
    )
    )


    return ProjectType(
    return ProjectType(
    id=str(project.id),
    id=str(project.id),
    user_id=str(project.user_id),
    user_id=str(project.user_id),
    name=project.name,
    name=project.name,
    description=project.description,
    description=project.description,
    is_public=project.is_public,
    is_public=project.is_public,
    created_at=(
    created_at=(
    project.created_at.isoformat() if project.created_at else None
    project.created_at.isoformat() if project.created_at else None
    ),
    ),
    updated_at=(
    updated_at=(
    project.updated_at.isoformat() if project.updated_at else None
    project.updated_at.isoformat() if project.updated_at else None
    ),
    ),
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error creating project: {str(e)}")
    logger.error(f"Error creating project: {str(e)}")
    return None
    return None


    @strawberry.mutation
    @strawberry.mutation
    async def share_project(
    async def share_project(
    self, info: Info, project_id: str, user_id: str, role: UserRoleEnum
    self, info: Info, project_id: str, user_id: str, role: UserRoleEnum
    ) -> Optional[CollaborationType]:
    ) -> Optional[CollaborationType]:
    """
    """
    Share a project with another user.
    Share a project with another user.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info
    project_id: Project ID
    project_id: Project ID
    user_id: User ID to share with
    user_id: User ID to share with
    role: User role in the project
    role: User role in the project


    Returns:
    Returns:
    Collaboration if successful, None otherwise
    Collaboration if successful, None otherwise
    """
    """
    # Get user service from context
    # Get user service from context
    service = info.context["services"].get("user")
    service = info.context["services"].get("user")
    if not service:
    if not service:
    logger.warning("User service not available")
    logger.warning("User service not available")
    return None
    return None


    # Share project
    # Share project
    try:
    try:
    collaboration = await service.share_project(
    collaboration = await service.share_project(
    project_id=project_id, user_id=user_id, role=role.value
    project_id=project_id, user_id=user_id, role=role.value
    )
    )


    return CollaborationType(
    return CollaborationType(
    id=str(collaboration.id),
    id=str(collaboration.id),
    project_id=str(collaboration.project_id),
    project_id=str(collaboration.project_id),
    user_id=str(collaboration.user_id),
    user_id=str(collaboration.user_id),
    role=UserRoleEnum(collaboration.role),
    role=UserRoleEnum(collaboration.role),
    created_at=(
    created_at=(
    collaboration.created_at.isoformat()
    collaboration.created_at.isoformat()
    if collaboration.created_at
    if collaboration.created_at
    else None
    else None
    ),
    ),
    updated_at=(
    updated_at=(
    collaboration.updated_at.isoformat()
    collaboration.updated_at.isoformat()
    if collaboration.updated_at
    if collaboration.updated_at
    else None
    else None
    ),
    ),
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error sharing project: {str(e)}")
    logger.error(f"Error sharing project: {str(e)}")
    return None
    return None