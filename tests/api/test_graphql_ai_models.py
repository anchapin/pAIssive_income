"""
Tests for the AI Models GraphQL API.

This module contains tests for AI Models GraphQL queries and mutations.
"""


from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import (
    generate_id, generate_ai_model_data
)
from tests.api.utils.test_validators import (
    validate_json_response, validate_field_exists,
    validate_field_equals, validate_field_type
)


class TestAIModelsGraphQLAPI:
    """Tests for the AI Models GraphQL API."""

    def test_models_query(self, api_test_client: APITestClient):
        """Test querying AI models."""
        # GraphQL query
        query = """
        query {
            aiModels {
                id
                name
                description
                modelType
                provider
                version
                capabilities
                parameters
                metrics {
                    requestCount
                    errorCount
                    tokenCount
                    latencyMeanMs
                    latencyP90Ms
                    latencyP99Ms
                }
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
            validate_field_exists(data, "aiModels")
            validate_field_type(data["aiModels"], list)

            # If there are models, validate their structure
            if data["aiModels"]:
                model = data["aiModels"][0]
                validate_field_exists(model, "id")
                validate_field_exists(model, "name")
                validate_field_exists(model, "description")
                validate_field_exists(model, "modelType")
                validate_field_exists(model, "provider")
                validate_field_exists(model, "version")
                validate_field_exists(model, "capabilities")
                validate_field_type(model["capabilities"], list)

    def test_model_query(self, api_test_client: APITestClient):
        """Test querying a specific AI model."""
        # Generate a random ID
        model_id = generate_id()

        # GraphQL query
        query = """
        query($id: ID!) {
            aiModel(id: $id) {
                id
                name
                description
                modelType
                provider
                version
                capabilities
                parameters
                metrics {
                    requestCount
                    errorCount
                    tokenCount
                    latencyMeanMs
                    latencyP90Ms
                    latencyP99Ms
                }
            }
        }
        """

        # Make request
        response = api_test_client.post(
            "graphql",
            json={
                "query": query,
                "variables": {"id": model_id}
            }
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "aiModel")
            
            # The model might not exist, which is fine
            if data["aiModel"]:
                model = data["aiModel"]
                validate_field_exists(model, "id")
                validate_field_equals(model, "id", model_id)
                validate_field_exists(model, "name")
                validate_field_exists(model, "description")
                validate_field_exists(model, "modelType")
                validate_field_exists(model, "provider")
                validate_field_exists(model, "version")
                validate_field_exists(model, "capabilities")
                validate_field_type(model["capabilities"], list)

    def test_model_inference(self, api_test_client: APITestClient):
        """Test running inference using GraphQL mutation."""
        # Generate test data
        model_id = generate_id()

        # GraphQL mutation
        mutation = """
        mutation($input: InferenceInput!) {
            runInference(input: $input) {
                requestId
                modelId
                output
                latency
                tokenUsage
            }
        }
        """

        # Variables
        variables = {
            "input": {
                "modelId": model_id,
                "inputData": {"prompt": "Hello, world!"},
                "parameters": {
                    "temperature": 0.7,
                    "maxTokens": 100
                }
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
            validate_field_exists(data, "runInference")
            
            # The inference response might be None if model doesn't exist
            if data["runInference"]:
                inference = data["runInference"]
                validate_field_exists(inference, "requestId")
                validate_field_exists(inference, "modelId")
                validate_field_equals(inference, "modelId", model_id)
                validate_field_exists(inference, "output")
                validate_field_exists(inference, "latency")
                validate_field_exists(inference, "tokenUsage")

    def test_model_versions_query(self, api_test_client: APITestClient):
        """Test querying model versions."""
        # Generate a random ID
        model_id = generate_id()

        # GraphQL query
        query = """
        query($modelId: ID!) {
            modelVersions(modelId: $modelId) {
                id
                modelId
                version
                description
                changes
                createdAt
            }
        }
        """

        # Make request
        response = api_test_client.post(
            "graphql",
            json={
                "query": query,
                "variables": {"modelId": model_id}
            }
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "modelVersions")
            validate_field_type(data["modelVersions"], list)

    def test_model_metrics_query(self, api_test_client: APITestClient):
        """Test querying model metrics."""
        # Generate a random ID
        model_id = generate_id()

        # GraphQL query
        query = """
        query($modelId: ID!) {
            modelMetrics(modelId: $modelId) {
                modelId
                inferenceCount
                averageLatency
                p95Latency
                p99Latency
                errorRate
                tokenUsage
                cost
            }
        }
        """

        # Make request
        response = api_test_client.post(
            "graphql",
            json={
                "query": query,
                "variables": {"modelId": model_id}
            }
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "modelMetrics")
            
            # Metrics might be None if model doesn't exist
            if data["modelMetrics"]:
                metrics = data["modelMetrics"]
                validate_field_exists(metrics, "modelId")
                validate_field_equals(metrics, "modelId", model_id)
                validate_field_exists(metrics, "inferenceCount")
                validate_field_exists(metrics, "averageLatency")
                validate_field_exists(metrics, "p95Latency")
                validate_field_exists(metrics, "p99Latency")
                validate_field_exists(metrics, "errorRate")
                validate_field_exists(metrics, "tokenUsage")
                validate_field_exists(metrics, "cost")

    def test_create_model_mutation(self, api_test_client: APITestClient):
        """Test creating an AI model using GraphQL mutation."""
        # Generate test data
        test_data = generate_ai_model_data()

        # GraphQL mutation
        mutation = """
        mutation($input: ModelInput!) {
            createModel(input: $input) {
                id
                name
                description
                modelType
                provider
                capabilities
                createdAt
                updatedAt
            }
        }
        """

        # Variables
        variables = {
            "input": {
                "name": test_data["name"],
                "description": test_data["description"],
                "modelType": test_data["model_type"],
                "provider": test_data["provider"],
                "capabilities": test_data["capabilities"]
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
            validate_field_exists(data, "createModel")
            
            if data["createModel"]:
                model = data["createModel"]
                validate_field_exists(model, "id")
                validate_field_exists(model, "name")
                validate_field_equals(model, "name", test_data["name"])
                validate_field_exists(model, "description")
                validate_field_equals(model, "description", test_data["description"])
                validate_field_exists(model, "modelType")
                validate_field_equals(model, "modelType", test_data["model_type"])
                validate_field_exists(model, "provider")
                validate_field_equals(model, "provider", test_data["provider"])
                validate_field_exists(model, "capabilities")
                validate_field_type(model["capabilities"], list)
                validate_field_exists(model, "createdAt")
                validate_field_exists(model, "updatedAt")

    def test_update_model_mutation(self, api_test_client: APITestClient):
        """Test updating an AI model using GraphQL mutation."""
        # Generate test data
        model_id = generate_id()
        test_data = generate_ai_model_data()

        # GraphQL mutation
        mutation = """
        mutation($id: ID!, $input: ModelInput!) {
            updateModel(id: $id, input: $input) {
                id
                name
                description
                modelType
                provider
                capabilities
                createdAt
                updatedAt
            }
        }
        """

        # Variables
        variables = {
            "id": model_id,
            "input": {
                "name": test_data["name"],
                "description": test_data["description"],
                "modelType": test_data["model_type"],
                "provider": test_data["provider"],
                "capabilities": test_data["capabilities"]
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
            validate_field_exists(data, "updateModel")
            
            # The update might return None if model doesn't exist
            if data["updateModel"]:
                model = data["updateModel"]
                validate_field_exists(model, "id")
                validate_field_equals(model, "id", model_id)
                validate_field_exists(model, "name")
                validate_field_equals(model, "name", test_data["name"])
                validate_field_exists(model, "description")
                validate_field_equals(model, "description", test_data["description"])
                validate_field_exists(model, "modelType")
                validate_field_equals(model, "modelType", test_data["model_type"])
                validate_field_exists(model, "provider")
                validate_field_equals(model, "provider", test_data["provider"])
                validate_field_exists(model, "capabilities")
                validate_field_type(model["capabilities"], list)
                validate_field_exists(model, "createdAt")
                validate_field_exists(model, "updatedAt")

    def test_delete_model_mutation(self, api_test_client: APITestClient):
        """Test deleting an AI model using GraphQL mutation."""
        # Generate a random ID
        model_id = generate_id()

        # GraphQL mutation
        mutation = """
        mutation($id: ID!) {
            deleteModel(id: $id)
        }
        """

        # Make request
        response = api_test_client.post(
            "graphql",
            json={
                "query": mutation,
                "variables": {"id": model_id}
            }
        )

        # Validate response structure
        result = validate_json_response(response)

        # GraphQL specific validation
        validate_field_exists(result, "data")
        if "errors" not in result:
            data = result["data"]
            validate_field_exists(data, "deleteModel")
            validate_field_type(data["deleteModel"], bool)

    def test_error_handling(self, api_test_client: APITestClient):
        """Test GraphQL error handling for AI models."""
        # Test invalid query field
        query = """
        query {
            aiModels {
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
        mutation($input: ModelInput!) {
            createModel(input: $input) {
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
                        "description": "Invalid model"
                    }
                }
            }
        )
        result = validate_json_response(response)
        validate_field_exists(result, "errors")