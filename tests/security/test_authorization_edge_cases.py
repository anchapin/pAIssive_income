"""
Tests for authorization edge cases.

This module implements the authorization edge case tests recommended in the security testing section:
1. Test resource access during role transitions
2. Test inherited permissions scenarios
3. Test temporary permission elevation
"""

import threading
import time
import unittest
from datetime import datetime, timedelta
from typing import Any, Dict, List, Set
from unittest.mock import MagicMock, patch

import jwt

from api.config import APIConfig
from api.middleware.auth import AuthMiddleware


class TestAuthorizationEdgeCases(unittest.TestCase):
    """Test cases for authorization edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = APIConfig(
            jwt_secret="test-secret",
            jwt_algorithm="HS256",
            jwt_expires_minutes=60,
            api_keys=["test-api-key"],
        )
        self.auth_middleware = AuthMiddleware(self.config)

        # Mock permission service
        self.permission_service = MagicMock()
        self.auth_middleware.permission_service = self.permission_service

        # Set up role hierarchy
        self.role_hierarchy = {"admin": ["manager", "user"], "manager": ["user"], "user": []}

        # Set up role permissions
        self.role_permissions = {
            "admin": {"read", "write", "delete", "manage_users", "manage_roles"},
            "manager": {"read", "write", "manage_team"},
            "user": {"read"},
        }

        # Mock permission methods
        self.permission_service.get_role_hierarchy.return_value = self.role_hierarchy
        self.permission_service.get_role_permissions.side_effect = self._get_role_permissions
        self.permission_service.has_permission.side_effect = self._has_permission

    def _get_role_permissions(self, role: str) -> Set[str]:
        """Mock getting permissions for a role."""
        return self.role_permissions.get(role, set())

    def _has_permission(self, user_data: Dict[str, Any], permission: str) -> bool:
        """Mock checking if a user has a permission."""
        # Get user's role
        role = user_data.get("role")
        if not role:
            return False

        # Get permissions for role
        role_perms = self.permission_service.get_role_permissions(role)

        # Check direct permission
        if permission in role_perms:
            return True

        # Check additional permissions
        additional_perms = user_data.get("permissions", [])
        if permission in additional_perms:
            return True

        return False

    def test_role_transition_basic(self):
        """Test basic role transition scenario."""
        # Create user with initial role
        user_data = {"user_id": "123", "username": "testuser", "role": "user"}

        # Create token with initial role
        token = self.auth_middleware.create_token(user_data)

        # Verify initial permissions
        payload = self.auth_middleware.verify_token(token)
        self.assertTrue(self.permission_service.has_permission(payload, "read"))
        self.assertFalse(self.permission_service.has_permission(payload, "write"))

        # Transition to new role
        user_data["role"] = "manager"
        new_token = self.auth_middleware.create_token(user_data)

        # Verify new permissions
        new_payload = self.auth_middleware.verify_token(new_token)
        self.assertTrue(self.permission_service.has_permission(new_payload, "read"))
        self.assertTrue(self.permission_service.has_permission(new_payload, "write"))
        self.assertTrue(self.permission_service.has_permission(new_payload, "manage_team"))

    def test_role_transition_with_active_sessions(self):
        """Test role transition with active sessions."""
        # Mock session store
        session_store = MagicMock()
        self.auth_middleware.session_store = session_store

        # Create active sessions for user
        user_id = "123"
        active_sessions = {
            "session1": {"token": "token1", "created_at": datetime.now().isoformat()},
            "session2": {"token": "token2", "created_at": datetime.now().isoformat()},
        }
        session_store.get_user_sessions.return_value = active_sessions

        # Mock token verification to return different user data based on token
        def mock_verify_token(token):
            if token == "token1":
                return {"user_id": "123", "username": "testuser", "role": "user"}
            elif token == "token2":
                return {"user_id": "123", "username": "testuser", "role": "manager"}
            return None

        self.auth_middleware.verify_token = MagicMock(side_effect=mock_verify_token)

        # Test resource access with different sessions
        resources = {
            "basic_report": {"required_permission": "read"},
            "edit_report": {"required_permission": "write"},
            "manage_team_members": {"required_permission": "manage_team"},
        }

        # Check access with user role (token1)
        user_data = mock_verify_token("token1")
        self.assertTrue(self.permission_service.has_permission(user_data, "read"))
        self.assertFalse(self.permission_service.has_permission(user_data, "write"))
        self.assertFalse(self.permission_service.has_permission(user_data, "manage_team"))

        # Check access with manager role (token2)
        manager_data = mock_verify_token("token2")
        self.assertTrue(self.permission_service.has_permission(manager_data, "read"))
        self.assertTrue(self.permission_service.has_permission(manager_data, "write"))
        self.assertTrue(self.permission_service.has_permission(manager_data, "manage_team"))

    def test_resource_access_during_role_transition(self):
        """Test resource access during role transition process."""
        # Create user with initial role
        user_id = "123"
        username = "testuser"
        initial_role = "user"
        new_role = "manager"

        # Mock role transition process
        def transition_role(user_id, new_role):
            # Step 1: Start transition
            transition_id = f"transition-{user_id}-{int(time.time())}"

            # Step 2: Create transition record
            transition = {
                "id": transition_id,
                "user_id": user_id,
                "from_role": initial_role,
                "to_role": new_role,
                "status": "in_progress",
                "started_at": datetime.now().isoformat(),
                "completed_at": None,
            }

            # Step 3: Apply transition after delay (simulating background process)
            def complete_transition():
                time.sleep(2)  # Simulate delay in role transition
                transition["status"] = "completed"
                transition["completed_at"] = datetime.now().isoformat()

            threading.Thread(target=complete_transition).start()

            return transition

        # Start role transition
        transition = transition_role(user_id, new_role)
        self.assertEqual(transition["status"], "in_progress")

        # Create user data during transition
        user_data = {
            "user_id": user_id,
            "username": username,
            "role": initial_role,  # Still has old role
            "pending_role": new_role,  # But has pending new role
            "role_transition": transition["id"],
        }

        # Test access during transition
        # Should still have old role permissions
        self.assertTrue(self.permission_service.has_permission(user_data, "read"))
        self.assertFalse(self.permission_service.has_permission(user_data, "write"))

        # Wait for transition to complete
        time.sleep(3)

        # Update user data after transition
        user_data["role"] = new_role
        del user_data["pending_role"]
        del user_data["role_transition"]

        # Test access after transition
        # Should now have new role permissions
        self.assertTrue(self.permission_service.has_permission(user_data, "read"))
        self.assertTrue(self.permission_service.has_permission(user_data, "write"))
        self.assertTrue(self.permission_service.has_permission(user_data, "manage_team"))

    def test_inherited_permissions_basic(self):
        """Test basic inherited permissions scenario."""
        # Test admin inherits manager and user permissions
        admin_data = {"user_id": "123", "username": "admin_user", "role": "admin"}

        # Admin should have all permissions from admin, manager, and user roles
        self.assertTrue(
            self.permission_service.has_permission(admin_data, "read")
        )  # user permission
        self.assertTrue(
            self.permission_service.has_permission(admin_data, "write")
        )  # manager permission
        self.assertTrue(
            self.permission_service.has_permission(admin_data, "manage_team")
        )  # manager permission
        self.assertTrue(
            self.permission_service.has_permission(admin_data, "delete")
        )  # admin permission
        self.assertTrue(
            self.permission_service.has_permission(admin_data, "manage_users")
        )  # admin permission

        # Test manager inherits user permissions
        manager_data = {"user_id": "456", "username": "manager_user", "role": "manager"}

        # Manager should have all permissions from manager and user roles
        self.assertTrue(
            self.permission_service.has_permission(manager_data, "read")
        )  # user permission
        self.assertTrue(
            self.permission_service.has_permission(manager_data, "write")
        )  # manager permission
        self.assertTrue(
            self.permission_service.has_permission(manager_data, "manage_team")
        )  # manager permission
        self.assertFalse(
            self.permission_service.has_permission(manager_data, "delete")
        )  # admin permission
        self.assertFalse(
            self.permission_service.has_permission(manager_data, "manage_users")
        )  # admin permission

    def test_inherited_permissions_with_overrides(self):
        """Test inherited permissions with overrides."""
        # Create custom role hierarchy with overrides
        custom_hierarchy = {"admin": ["manager", "user"], "manager": ["user"], "user": []}

        # Create custom permissions with overrides
        custom_permissions = {
            "admin": {"read", "write", "delete", "manage_users", "manage_roles"},
            "manager": {"read", "write", "manage_team", "limited_delete"},
            "user": {"read", "limited_write"},
        }

        # Override mocks
        self.permission_service.get_role_hierarchy.return_value = custom_hierarchy
        self.role_permissions = custom_permissions

        # Test admin with overrides
        admin_data = {"user_id": "123", "username": "admin_user", "role": "admin"}

        # Admin should have all permissions including overrides
        self.assertTrue(self.permission_service.has_permission(admin_data, "read"))
        self.assertTrue(self.permission_service.has_permission(admin_data, "write"))
        self.assertTrue(self.permission_service.has_permission(admin_data, "delete"))
        self.assertTrue(
            self.permission_service.has_permission(admin_data, "limited_write")
        )  # from user
        self.assertTrue(
            self.permission_service.has_permission(admin_data, "limited_delete")
        )  # from manager

        # Test manager with overrides
        manager_data = {"user_id": "456", "username": "manager_user", "role": "manager"}

        # Manager should have manager and user permissions with overrides
        self.assertTrue(self.permission_service.has_permission(manager_data, "read"))
        self.assertTrue(self.permission_service.has_permission(manager_data, "write"))
        self.assertTrue(
            self.permission_service.has_permission(manager_data, "limited_write")
        )  # from user
        self.assertTrue(
            self.permission_service.has_permission(manager_data, "limited_delete")
        )  # manager override
        self.assertFalse(
            self.permission_service.has_permission(manager_data, "delete")
        )  # admin only

    def test_inherited_permissions_deep_hierarchy(self):
        """Test inherited permissions in a deep role hierarchy."""
        # Create deep role hierarchy
        deep_hierarchy = {
            "super_admin": ["admin"],
            "admin": ["senior_manager"],
            "senior_manager": ["manager"],
            "manager": ["team_lead"],
            "team_lead": ["senior_user"],
            "senior_user": ["user"],
            "user": [],
        }

        # Create permissions for deep hierarchy
        deep_permissions = {
            "super_admin": {"system_config"},
            "admin": {"user_management"},
            "senior_manager": {"budget_approval"},
            "manager": {"hire_fire"},
            "team_lead": {"assign_tasks"},
            "senior_user": {"review_work"},
            "user": {"do_work"},
        }

        # Override mocks
        self.permission_service.get_role_hierarchy.return_value = deep_hierarchy
        self.role_permissions = deep_permissions

        # Test inheritance at different levels
        roles_to_test = list(deep_hierarchy.keys())

        for i, role in enumerate(roles_to_test):
            user_data = {"user_id": f"{i}", "username": f"{role}_user", "role": role}

            # User should have permissions from their role and all roles below
            for j in range(i, len(roles_to_test)):
                test_role = roles_to_test[j]
                for permission in deep_permissions[test_role]:
                    self.assertTrue(
                        self.permission_service.has_permission(user_data, permission),
                        f"User with role '{role}' should have permission '{permission}' from role '{test_role}'",
                    )

            # User should not have permissions from roles above them
            for j in range(0, i):
                test_role = roles_to_test[j]
                for permission in deep_permissions[test_role]:
                    self.assertFalse(
                        self.permission_service.has_permission(user_data, permission),
                        f"User with role '{role}' should not have permission '{permission}' from role '{test_role}'",
                    )

    def test_temporary_permission_elevation_basic(self):
        """Test basic temporary permission elevation."""
        # Create user with base permissions
        user_data = {"user_id": "123", "username": "testuser", "role": "user"}

        # Create token with base permissions
        token = self.auth_middleware.create_token(user_data)
        payload = self.auth_middleware.verify_token(token)

        # Verify base permissions
        self.assertTrue(self.permission_service.has_permission(payload, "read"))
        self.assertFalse(self.permission_service.has_permission(payload, "write"))

        # Elevate permissions temporarily
        elevated_data = dict(payload)
        elevated_data["permissions"] = ["write", "temporary_admin"]
        elevated_data["elevated_until"] = (datetime.now() + timedelta(minutes=30)).isoformat()

        elevated_token = self.auth_middleware.create_token(elevated_data)
        elevated_payload = self.auth_middleware.verify_token(elevated_token)

        # Verify elevated permissions
        self.assertTrue(self.permission_service.has_permission(elevated_payload, "read"))
        self.assertTrue(self.permission_service.has_permission(elevated_payload, "write"))
        self.assertTrue(self.permission_service.has_permission(elevated_payload, "temporary_admin"))

    def test_temporary_permission_elevation_expiry(self):
        """Test expiration of temporary elevated permissions."""

        # Create auth middleware with permission expiry checking
        def has_permission_with_expiry(user_data, permission):
            # Check if permission is in elevated permissions and if elevation has expired
            if "elevated_until" in user_data and "permissions" in user_data:
                elevated_until = datetime.fromisoformat(user_data["elevated_until"])
                if elevated_until < datetime.now():
                    # Elevation has expired, fall back to role-based permissions
                    return self._has_permission({"role": user_data["role"]}, permission)
                else:
                    # Elevation is still valid
                    if permission in user_data["permissions"]:
                        return True

            # Fall back to regular permission check
            return self._has_permission(user_data, permission)

        # Override permission check
        self.permission_service.has_permission.side_effect = has_permission_with_expiry

        # Create user with elevated permissions that expire soon
        user_data = {
            "user_id": "123",
            "username": "testuser",
            "role": "user",
            "permissions": ["write", "temporary_admin"],
            "elevated_until": (datetime.now() + timedelta(seconds=2)).isoformat(),
        }

        # Verify elevated permissions are active
        self.assertTrue(self.permission_service.has_permission(user_data, "read"))  # from role
        self.assertTrue(self.permission_service.has_permission(user_data, "write"))  # elevated
        self.assertTrue(
            self.permission_service.has_permission(user_data, "temporary_admin")
        )  # elevated

        # Wait for elevation to expire
        time.sleep(3)

        # Verify elevated permissions have expired
        self.assertTrue(
            self.permission_service.has_permission(user_data, "read")
        )  # still from role
        self.assertFalse(self.permission_service.has_permission(user_data, "write"))  # expired
        self.assertFalse(
            self.permission_service.has_permission(user_data, "temporary_admin")
        )  # expired

    def test_temporary_permission_elevation_with_approval(self):
        """Test temporary permission elevation with approval workflow."""
        # Create user with base permissions
        user_id = "123"
        username = "testuser"
        user_role = "user"

        user_data = {"user_id": user_id, "username": username, "role": user_role}

        # Mock approval workflow
        def request_elevation(user_id, requested_permissions, reason, duration_minutes):
            # Create elevation request
            request_id = f"elevation-{user_id}-{int(time.time())}"

            elevation_request = {
                "id": request_id,
                "user_id": user_id,
                "requested_permissions": requested_permissions,
                "reason": reason,
                "duration_minutes": duration_minutes,
                "status": "pending",
                "requested_at": datetime.now().isoformat(),
                "approved_at": None,
                "approved_by": None,
                "expires_at": None,
            }

            return elevation_request

        def approve_elevation(request_id, approver_id):
            # Simulate approval
            now = datetime.now()
            expires_at = now + timedelta(minutes=30)

            # Update request
            elevation_request = {
                "id": request_id,
                "status": "approved",
                "approved_at": now.isoformat(),
                "approved_by": approver_id,
                "expires_at": expires_at.isoformat(),
            }

            return elevation_request

        # Request elevation
        requested_permissions = ["write", "temporary_admin"]
        elevation_request = request_elevation(
            user_id, requested_permissions, "Emergency system maintenance", 30
        )

        # Verify request is pending
        self.assertEqual(elevation_request["status"], "pending")

        # Approve request
        approver_id = "admin-456"
        approved_request = approve_elevation(elevation_request["id"], approver_id)

        # Create elevated token
        elevated_data = dict(user_data)
        elevated_data["permissions"] = requested_permissions
        elevated_data["elevated_until"] = approved_request["expires_at"]
        elevated_data["elevation_request_id"] = approved_request["id"]
        elevated_data["elevation_approved_by"] = approved_request["approved_by"]

        # Verify elevated permissions
        self.assertTrue(self.permission_service.has_permission(elevated_data, "read"))  # from role
        self.assertTrue(self.permission_service.has_permission(elevated_data, "write"))  # elevated
        self.assertTrue(
            self.permission_service.has_permission(elevated_data, "temporary_admin")
        )  # elevated


if __name__ == "__main__":
    unittest.main()
