"""
User GraphQL resolvers.

This module provides resolvers for user queries and mutations.
"""


import logging
from typing import List, Optional


    import strawberry
    from strawberry.types import Info

    STRAWBERRY_AVAILABLE 

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:

= True
except ImportError:
    logger.warning("Strawberry GraphQL is required for GraphQL resolvers")
    STRAWBERRY_AVAILABLE = False

if STRAWBERRY_AVAILABLE:
    from ..schemas.user import (
        CollaborationType,
        ProjectInput,
        ProjectType,
        UserInput,
        UserRoleEnum,
        UserType,
    )

    @strawberry.type
    class UserQuery:
        """User query resolvers."""

        @strawberry.field
        async def me(self, info: Info) -> Optional[UserType]:
            """
            Get the current authenticated user.

            Args:
                info: GraphQL resolver info

            Returns:
                Current user if authenticated, None otherwise
            """
            # Get user from context
            user = info.context.get("user")
            if not user:
                return None

            return UserType(
                id=str(user.id),
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                role=UserRoleEnum(user.role),
                created_at=user.created_at.isoformat() if user.created_at else None,
                updated_at=user.updated_at.isoformat() if user.updated_at else None,
            )

        @strawberry.field
        async def users(
            self, info: Info, limit: Optional[int] = 10, offset: Optional[int] = 0
        ) -> List[UserType]:
            """
            Get a list of users.

            Args:
                info: GraphQL resolver info
                limit: Maximum number of users to return
                offset: Number of users to skip

            Returns:
                List of users
            """
            # Get user service from context
            service = info.context["services"].get("user")
            if not service:
                logger.warning("User service not available")
                return []

            # Get users from service
            try:
                users = await service.get_users(limit=limit, offset=offset)

                return [
                    UserType(
                        id=str(user.id),
                        username=user.username,
                        email=user.email,
                        full_name=user.full_name,
                        role=UserRoleEnum(user.role),
                        created_at=(
                            user.created_at.isoformat() if user.created_at else None
                        ),
                        updated_at=(
                            user.updated_at.isoformat() if user.updated_at else None
                        ),
                    )
                    for user in users
                ]
            except Exception as e:
                logger.error(f"Error getting users: {str(e)}")
                return []

        @strawberry.field
        async def user(self, info: Info, id: str) -> Optional[UserType]:
            """
            Get a user by ID.

            Args:
                info: GraphQL resolver info
                id: User ID

            Returns:
                User if found, None otherwise
            """
            # Get user service from context
            service = info.context["services"].get("user")
            if not service:
                logger.warning("User service not available")
                return None

            # Get user from service
            try:
                user = await service.get_user(id)
                if not user:
                    return None

                return UserType(
                    id=str(user.id),
                    username=user.username,
                    email=user.email,
                    full_name=user.full_name,
                    role=UserRoleEnum(user.role),
                    created_at=user.created_at.isoformat() if user.created_at else None,
                    updated_at=user.updated_at.isoformat() if user.updated_at else None,
                )
            except Exception as e:
                logger.error(f"Error getting user: {str(e)}")
                return None

        @strawberry.field
        async def projects(
            self,
            info: Info,
            user_id: Optional[str] = None,
            limit: Optional[int] = 10,
            offset: Optional[int] = 0,
        ) -> List[ProjectType]:
            """
            Get a list of projects.

            Args:
                info: GraphQL resolver info
                user_id: Filter by user ID
                limit: Maximum number of projects to return
                offset: Number of projects to skip

            Returns:
                List of projects
            """
            # Get user service from context
            service = info.context["services"].get("user")
            if not service:
                logger.warning("User service not available")
                return []

            # Get projects from service
            try:
                projects = await service.get_projects(
                    user_id=user_id, limit=limit, offset=offset
                )

                return [
                    ProjectType(
                        id=str(project.id),
                        user_id=str(project.user_id),
                        name=project.name,
                        description=project.description,
                        is_public=project.is_public,
                        created_at=(
                            project.created_at.isoformat()
                            if project.created_at
                            else None
                        ),
                        updated_at=(
                            project.updated_at.isoformat()
                            if project.updated_at
                            else None
                        ),
                    )
                    for project in projects
                ]
            except Exception as e:
                logger.error(f"Error getting projects: {str(e)}")
                return []

    @strawberry.type
    class UserMutation:
        """User mutation resolvers."""

        @strawberry.mutation
        async def create_user(self, info: Info, input: UserInput) -> Optional[UserType]:
            """
            Create a new user.

            Args:
                info: GraphQL resolver info
                input: User input

            Returns:
                Created user if successful, None otherwise
            """
            # Get user service from context
            service = info.context["services"].get("user")
            if not service:
                logger.warning("User service not available")
                return None

            # Create user
            try:
                user = await service.create_user(
                    username=input.username,
                    email=input.email,
                    password=input.password,
                    full_name=input.full_name,
                    role=input.role.value,
                )

                return UserType(
                    id=str(user.id),
                    username=user.username,
                    email=user.email,
                    full_name=user.full_name,
                    role=UserRoleEnum(user.role),
                    created_at=user.created_at.isoformat() if user.created_at else None,
                    updated_at=user.updated_at.isoformat() if user.updated_at else None,
                )
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}")
                return None

        @strawberry.mutation
        async def update_user(
            self, info: Info, id: str, input: UserInput
        ) -> Optional[UserType]:
            """
            Update a user.

            Args:
                info: GraphQL resolver info
                id: User ID
                input: User input

            Returns:
                Updated user if successful, None otherwise
            """
            # Get user service from context
            service = info.context["services"].get("user")
            if not service:
                logger.warning("User service not available")
                return None

            # Update user
            try:
                user = await service.update_user(
                    id=id,
                    username=input.username,
                    email=input.email,
                    password=input.password,
                    full_name=input.full_name,
                    role=input.role.value,
                )

                if not user:
                    return None

                return UserType(
                    id=str(user.id),
                    username=user.username,
                    email=user.email,
                    full_name=user.full_name,
                    role=UserRoleEnum(user.role),
                    created_at=user.created_at.isoformat() if user.created_at else None,
                    updated_at=user.updated_at.isoformat() if user.updated_at else None,
                )
            except Exception as e:
                logger.error(f"Error updating user: {str(e)}")
                return None

        @strawberry.mutation
        async def delete_user(self, info: Info, id: str) -> bool:
            """
            Delete a user.

            Args:
                info: GraphQL resolver info
                id: User ID

            Returns:
                True if successful, False otherwise
            """
            # Get user service from context
            service = info.context["services"].get("user")
            if not service:
                logger.warning("User service not available")
                return False

            # Delete user
            try:
                success = await service.delete_user(id)
                return success
            except Exception as e:
                logger.error(f"Error deleting user: {str(e)}")
                return False

        @strawberry.mutation
        async def create_project(
            self, info: Info, input: ProjectInput
        ) -> Optional[ProjectType]:
            """
            Create a new project.

            Args:
                info: GraphQL resolver info
                input: Project input

            Returns:
                Created project if successful, None otherwise
            """
            # Get user service from context
            service = info.context["services"].get("user")
            if not service:
                logger.warning("User service not available")
                return None

            # Get current user
            user = info.context.get("user")
            if not user:
                logger.warning("User not authenticated")
                return None

            # Create project
            try:
                project = await service.create_project(
                    user_id=str(user.id),
                    name=input.name,
                    description=input.description,
                    is_public=input.is_public,
                )

                return ProjectType(
                    id=str(project.id),
                    user_id=str(project.user_id),
                    name=project.name,
                    description=project.description,
                    is_public=project.is_public,
                    created_at=(
                        project.created_at.isoformat() if project.created_at else None
                    ),
                    updated_at=(
                        project.updated_at.isoformat() if project.updated_at else None
                    ),
                )
            except Exception as e:
                logger.error(f"Error creating project: {str(e)}")
                return None

        @strawberry.mutation
        async def share_project(
            self, info: Info, project_id: str, user_id: str, role: UserRoleEnum
        ) -> Optional[CollaborationType]:
            """
            Share a project with another user.

            Args:
                info: GraphQL resolver info
                project_id: Project ID
                user_id: User ID to share with
                role: User role in the project

            Returns:
                Collaboration if successful, None otherwise
            """
            # Get user service from context
            service = info.context["services"].get("user")
            if not service:
                logger.warning("User service not available")
                return None

            # Share project
            try:
                collaboration = await service.share_project(
                    project_id=project_id, user_id=user_id, role=role.value
                )

                return CollaborationType(
                    id=str(collaboration.id),
                    project_id=str(collaboration.project_id),
                    user_id=str(collaboration.user_id),
                    role=UserRoleEnum(collaboration.role),
                    created_at=(
                        collaboration.created_at.isoformat()
                        if collaboration.created_at
                        else None
                    ),
                    updated_at=(
                        collaboration.updated_at.isoformat()
                        if collaboration.updated_at
                        else None
                    ),
                )
            except Exception as e:
                logger.error(f"Error sharing project: {str(e)}")
                return None