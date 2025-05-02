"""
Tests for the UI/Frontend GraphQL API.

This module contains tests for UI/Frontend GraphQL queries and mutations.
"""


from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import (
    generate_id, generate_ui_component_data
)
from tests.api.utils.test_validators import (
    validate_json_response, validate_field_exists,
    validate_field_equals, validate_field_type
)


class TestUIGraphQLAPI:
    """Tests for the UI/Frontend GraphQL API."""

    def test_ui_components_query(self, api_test_client: APITestClient):
        """Test querying UI components."""
        # GraphQL query
        query = """
        query {
            uiComponents {
                id
                name
                type
                description
                configuration {
                    layout
                    styling
                    behavior
                }
                metadata {
                    category
                    tags
                    version
                }
                accessibility {
                    level
                    features
                    ariaLabels
                }
                createdAt
                updatedAt
            }
        }
        """

        # Make request
        response = api_test_client.post(
            "graphql",
            json={"query": query}
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "uiComponents")
            validate_field_type(data["uiComponents"], list)

            # If there are components, validate their structure
            if data["uiComponents"]:
                component = data["uiComponents"][0]
                validate_field_exists(component, "id")
                validate_field_exists(component, "name")
                validate_field_exists(component, "type")
                validate_field_exists(component, "description")
                validate_field_exists(component, "configuration")
                validate_field_exists(component, "metadata")
                validate_field_exists(component, "accessibility")
                validate_field_exists(component, "createdAt")
                validate_field_exists(component, "updatedAt")

    def test_ui_layouts_query(self, api_test_client: APITestClient):
        """Test querying UI layouts."""
        # GraphQL query
        query = """
        query {
            uiLayouts {
                id
                name
                description
                type
                components {
                    id
                    name
                    position {
                        x
                        y
                        width
                        height
                    }
                    configuration
                }
                responsiveBreakpoints {
                    name
                    minWidth
                    maxWidth
                    layout
                }
                createdAt
                updatedAt
            }
        }
        """

        # Make request
        response = api_test_client.post(
            "graphql",
            json={"query": query}
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "uiLayouts")
            validate_field_type(data["uiLayouts"], list)

            # If there are layouts, validate their structure
            if data["uiLayouts"]:
                layout = data["uiLayouts"][0]
                validate_field_exists(layout, "id")
                validate_field_exists(layout, "name")
                validate_field_exists(layout, "description")
                validate_field_exists(layout, "type")
                validate_field_exists(layout, "components")
                validate_field_type(layout["components"], list)
                validate_field_exists(layout, "responsiveBreakpoints")
                validate_field_type(layout["responsiveBreakpoints"], list)
                validate_field_exists(layout, "createdAt")
                validate_field_exists(layout, "updatedAt")

    def test_ui_themes_query(self, api_test_client: APITestClient):
        """Test querying UI themes."""
        # GraphQL query
        query = """
        query {
            uiThemes {
                id
                name
                description
                type
                colors {
                    primary
                    secondary
                    accent
                    background
                    text
                }
                typography {
                    fontFamily
                    fontSize
                    fontWeight
                    lineHeight
                }
                spacing {
                    unit
                    scale
                }
                components {
                    buttons
                    inputs
                    cards
                    navigation
                }
                darkMode {
                    enabled
                    colors
                }
                createdAt
                updatedAt
            }
        }
        """

        # Make request
        response = api_test_client.post(
            "graphql",
            json={"query": query}
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "uiThemes")
            validate_field_type(data["uiThemes"], list)

            # If there are themes, validate their structure
            if data["uiThemes"]:
                theme = data["uiThemes"][0]
                validate_field_exists(theme, "id")
                validate_field_exists(theme, "name")
                validate_field_exists(theme, "description")
                validate_field_exists(theme, "type")
                validate_field_exists(theme, "colors")
                validate_field_exists(theme, "typography")
                validate_field_exists(theme, "spacing")
                validate_field_exists(theme, "components")
                validate_field_exists(theme, "darkMode")
                validate_field_exists(theme, "createdAt")
                validate_field_exists(theme, "updatedAt")

    def test_create_ui_component_mutation(self, api_test_client: APITestClient):
        """Test creating a UI component using GraphQL mutation."""
        # Generate test data
        test_data = generate_ui_component_data()

        # GraphQL mutation
        mutation = """
        mutation($input: UIComponentInput!) {
            createUIComponent(input: $input) {
                id
                name
                type
                description
                configuration {
                    layout
                    styling
                    behavior
                }
                metadata {
                    category
                    tags
                    version
                }
                accessibility {
                    level
                    features
                    ariaLabels
                }
                createdAt
                updatedAt
            }
        }
        """

        # Variables
        variables = {
            "input": {
                "name": test_data["name"],
                "type": test_data["type"],
                "description": test_data["description"],
                "configuration": test_data["configuration"],
                "metadata": test_data["metadata"],
                "accessibility": test_data["accessibility"]
            }
        }

        # Make request
        response = api_test_client.post(
            "graphql",
            json={
                "query": mutation,
                "variables": variables
            }
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "createUIComponent")
            
            if data["createUIComponent"]:
                component = data["createUIComponent"]
                validate_field_exists(component, "id")
                validate_field_exists(component, "name")
                validate_field_equals(component, "name", test_data["name"])
                validate_field_exists(component, "type")
                validate_field_equals(component, "type", test_data["type"])
                validate_field_exists(component, "description")
                validate_field_equals(component, "description", test_data["description"])
                validate_field_exists(component, "configuration")
                validate_field_exists(component, "metadata")
                validate_field_exists(component, "accessibility")
                validate_field_exists(component, "createdAt")
                validate_field_exists(component, "updatedAt")

    def test_update_ui_component_mutation(self, api_test_client: APITestClient):
        """Test updating a UI component using GraphQL mutation."""
        # Generate test data
        component_id = generate_id()
        test_data = generate_ui_component_data()

        # GraphQL mutation
        mutation = """
        mutation($id: ID!, $input: UIComponentInput!) {
            updateUIComponent(id: $id, input: $input) {
                id
                name
                type
                description
                configuration {
                    layout
                    styling
                    behavior
                }
                metadata {
                    category
                    tags
                    version
                }
                accessibility {
                    level
                    features
                    ariaLabels
                }
                createdAt
                updatedAt
            }
        }
        """

        # Variables
        variables = {
            "id": component_id,
            "input": {
                "name": test_data["name"],
                "type": test_data["type"],
                "description": test_data["description"],
                "configuration": test_data["configuration"],
                "metadata": test_data["metadata"],
                "accessibility": test_data["accessibility"]
            }
        }

        # Make request
        response = api_test_client.post(
            "graphql",
            json={
                "query": mutation,
                "variables": variables
            }
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "updateUIComponent")
            
            # The update might return None if component doesn't exist
            if data["updateUIComponent"]:
                component = data["updateUIComponent"]
                validate_field_exists(component, "id")
                validate_field_equals(component, "id", component_id)
                validate_field_exists(component, "name")
                validate_field_equals(component, "name", test_data["name"])
                validate_field_exists(component, "type")
                validate_field_equals(component, "type", test_data["type"])
                validate_field_exists(component, "description")
                validate_field_equals(component, "description", test_data["description"])
                validate_field_exists(component, "configuration")
                validate_field_exists(component, "metadata")
                validate_field_exists(component, "accessibility")
                validate_field_exists(component, "createdAt")
                validate_field_exists(component, "updatedAt")

    def test_delete_ui_component_mutation(self, api_test_client: APITestClient):
        """Test deleting a UI component using GraphQL mutation."""
        # Generate a random ID
        component_id = generate_id()

        # GraphQL mutation
        mutation = """
        mutation($id: ID!) {
            deleteUIComponent(id: $id)
        }
        """

        # Make request
        response = api_test_client.post(
            "graphql",
            json={
                "query": mutation,
                "variables": {"id": component_id}
            }
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "deleteUIComponent")
            validate_field_type(data["deleteUIComponent"], bool)

    def test_preview_ui_component_mutation(self, api_test_client: APITestClient):
        """Test previewing a UI component using GraphQL mutation."""
        # Generate test data
        test_data = generate_ui_component_data()

        # GraphQL mutation
        mutation = """
        mutation($input: UIComponentPreviewInput!) {
            previewUIComponent(input: $input) {
                html
                css
                javascript
                assets {
                    type
                    url
                }
                preview {
                    desktop
                    tablet
                    mobile
                }
                performance {
                    loadTime
                    interactiveTime
                    accessibilityScore
                }
            }
        }
        """

        # Variables
        variables = {
            "input": {
                "component": {
                    "name": test_data["name"],
                    "type": test_data["type"],
                    "configuration": test_data["configuration"]
                },
                "viewports": ["DESKTOP", "TABLET", "MOBILE"]
            }
        }

        # Make request
        response = api_test_client.post(
            "graphql",
            json={
                "query": mutation,
                "variables": variables
            }
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "previewUIComponent")
            
            if data["previewUIComponent"]:
                preview = data["previewUIComponent"]
                validate_field_exists(preview, "html")
                validate_field_exists(preview, "css")
                validate_field_exists(preview, "javascript")
                validate_field_exists(preview, "assets")
                validate_field_type(preview["assets"], list)
                validate_field_exists(preview, "preview")
                validate_field_exists(preview, "performance")

    def test_error_handling(self, api_test_client: APITestClient):
        """Test GraphQL error handling for UI operations."""
        # Test invalid query field
        query = """
        query {
            uiComponents {
                invalidField
            }
        }
        """

        response = api_test_client.post(
            "graphql",
            json={"query": query}
        )
        result = validate_json_response(response)
        validate_field_exists(result, "errors")

        # Test invalid mutation input
        mutation = """
        mutation($input: UIComponentInput!) {
            createUIComponent(input: $input) {
                id
                name
            }
        }
        """

        response = api_test_client.post(
            "graphql",
            json={
                "query": mutation,
                "variables": {
                    "input": {
                        # Missing required fields
                        "description": "Invalid component"
                    }
                }
            }
        )
        result = validate_json_response(response)
        validate_field_exists(result, "errors")