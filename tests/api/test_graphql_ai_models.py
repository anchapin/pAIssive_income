"""
"""
Tests for the AI Models GraphQL API.
Tests for the AI Models GraphQL API.


This module contains tests for AI Models GraphQL queries and mutations.
This module contains tests for AI Models GraphQL queries and mutations.
"""
"""




from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import generate_ai_model_data, generate_id
from tests.api.utils.test_data import generate_ai_model_data, generate_id


(
(
validate_field_equals,
validate_field_equals,
validate_field_exists,
validate_field_exists,
validate_field_type,
validate_field_type,
validate_json_response,
validate_json_response,
)
)




class TestAIModelsGraphQLAPI:
    class TestAIModelsGraphQLAPI:
    """Tests for the AI Models GraphQL API."""

    def test_models_query(self, api_test_client: APITestClient):
    """Test querying AI models."""
    # GraphQL query
    query = """
    query = """
    query {
    query {
    aiModels {
    aiModels {
    id
    id
    name
    name
    description
    description
    modelType
    modelType
    provider
    provider
    version
    version
    capabilities
    capabilities
    parameters
    parameters
    metrics {
    metrics {
    requestCount
    requestCount
    errorCount
    errorCount
    tokenCount
    tokenCount
    latencyMeanMs
    latencyMeanMs
    latencyP90Ms
    latencyP90Ms
    latencyP99Ms
    latencyP99Ms
    }
    }
    }
    }
    }
    }
    """
    """


    # Make request
    # Make request
    response = api_test_client.graphql_query(query)
    response = api_test_client.graphql_query(query)


    # Validate response structure
    # Validate response structure
    result = validate_json_response(response)
    result = validate_json_response(response)


    # GraphQL specific validation
    # GraphQL specific validation
    validate_field_exists(result, "data")
    validate_field_exists(result, "data")
    if "errors" not in result:
    if "errors" not in result:
    data = result["data"]
    data = result["data"]
    validate_field_exists(data, "aiModels")
    validate_field_exists(data, "aiModels")
    validate_field_type(data["aiModels"], list)
    validate_field_type(data["aiModels"], list)


    # If there are models, validate their structure
    # If there are models, validate their structure
    if data["aiModels"]:
    if data["aiModels"]:
    model = data["aiModels"][0]
    model = data["aiModels"][0]
    validate_field_exists(model, "id")
    validate_field_exists(model, "id")
    validate_field_exists(model, "name")
    validate_field_exists(model, "name")
    validate_field_exists(model, "description")
    validate_field_exists(model, "description")
    validate_field_exists(model, "modelType")
    validate_field_exists(model, "modelType")
    validate_field_exists(model, "provider")
    validate_field_exists(model, "provider")
    validate_field_exists(model, "version")
    validate_field_exists(model, "version")
    validate_field_exists(model, "capabilities")
    validate_field_exists(model, "capabilities")
    validate_field_type(model["capabilities"], list)
    validate_field_type(model["capabilities"], list)


    def test_model_query(self, api_test_client: APITestClient):
    def test_model_query(self, api_test_client: APITestClient):
    """Test querying a specific AI model."""
    # Generate a random ID
    model_id = generate_id()

    # GraphQL query
    query = """
    query = """
    query($id: ID!) {
    query($id: ID!) {
    aiModel(id: $id) {
    aiModel(id: $id) {
    id
    id
    name
    name
    description
    description
    modelType
    modelType
    provider
    provider
    version
    version
    capabilities
    capabilities
    parameters
    parameters
    metrics {
    metrics {
    requestCount
    requestCount
    errorCount
    errorCount
    tokenCount
    tokenCount
    latencyMeanMs
    latencyMeanMs
    latencyP90Ms
    latencyP90Ms
    latencyP99Ms
    latencyP99Ms
    }
    }
    }
    }
    }
    }
    """
    """


    # Make request
    # Make request
    response = api_test_client.graphql_query(query, {"id": model_id})
    response = api_test_client.graphql_query(query, {"id": model_id})


    # Validate response structure
    # Validate response structure
    result = validate_json_response(response)
    result = validate_json_response(response)


    # GraphQL specific validation
    # GraphQL specific validation
    validate_field_exists(result, "data")
    validate_field_exists(result, "data")
    if "errors" not in result:
    if "errors" not in result:
    data = result["data"]
    data = result["data"]
    validate_field_exists(data, "aiModel")
    validate_field_exists(data, "aiModel")


    # The model might not exist, which is fine
    # The model might not exist, which is fine
    if data["aiModel"]:
    if data["aiModel"]:
    model = data["aiModel"]
    model = data["aiModel"]
    validate_field_exists(model, "id")
    validate_field_exists(model, "id")
    validate_field_equals(model, "id", model_id)
    validate_field_equals(model, "id", model_id)
    validate_field_exists(model, "name")
    validate_field_exists(model, "name")
    validate_field_exists(model, "description")
    validate_field_exists(model, "description")
    validate_field_exists(model, "modelType")
    validate_field_exists(model, "modelType")
    validate_field_exists(model, "provider")
    validate_field_exists(model, "provider")
    validate_field_exists(model, "version")
    validate_field_exists(model, "version")
    validate_field_exists(model, "capabilities")
    validate_field_exists(model, "capabilities")
    validate_field_type(model["capabilities"], list)
    validate_field_type(model["capabilities"], list)


    def test_model_inference(self, api_test_client: APITestClient):
    def test_model_inference(self, api_test_client: APITestClient):
    """Test running inference using GraphQL mutation."""
    # Generate test data
    model_id = generate_id()

    # GraphQL mutation
    mutation = """
    mutation = """
    mutation($input: InferenceInput!) {
    mutation($input: InferenceInput!) {
    runInference(input: $input) {
    runInference(input: $input) {
    requestId
    requestId
    modelId
    modelId
    output
    output
    latency
    latency
    tokenUsage
    tokenUsage
    }
    }
    }
    }
    """
    """


    # Variables
    # Variables
    variables = {
    variables = {
    "input": {
    "input": {
    "modelId": model_id,
    "modelId": model_id,
    "inputData": {"prompt": "Hello, world!"},
    "inputData": {"prompt": "Hello, world!"},
    "parameters": {"temperature": 0.7, "maxTokens": 100},
    "parameters": {"temperature": 0.7, "maxTokens": 100},
    }
    }
    }
    }


    # Make request
    # Make request
    response = api_test_client.graphql_mutation(mutation, variables)
    response = api_test_client.graphql_mutation(mutation, variables)


    # Validate response structure
    # Validate response structure
    result = validate_json_response(response)
    result = validate_json_response(response)


    # GraphQL specific validation
    # GraphQL specific validation
    validate_field_exists(result, "data")
    validate_field_exists(result, "data")
    if "errors" not in result:
    if "errors" not in result:
    data = result["data"]
    data = result["data"]
    validate_field_exists(data, "runInference")
    validate_field_exists(data, "runInference")


    # The inference response might be None if model doesn't exist
    # The inference response might be None if model doesn't exist
    if data["runInference"]:
    if data["runInference"]:
    inference = data["runInference"]
    inference = data["runInference"]
    validate_field_exists(inference, "requestId")
    validate_field_exists(inference, "requestId")
    validate_field_exists(inference, "modelId")
    validate_field_exists(inference, "modelId")
    validate_field_equals(inference, "modelId", model_id)
    validate_field_equals(inference, "modelId", model_id)
    validate_field_exists(inference, "output")
    validate_field_exists(inference, "output")
    validate_field_exists(inference, "latency")
    validate_field_exists(inference, "latency")
    validate_field_exists(inference, "tokenUsage")
    validate_field_exists(inference, "tokenUsage")


    def test_model_versions_query(self, api_test_client: APITestClient):
    def test_model_versions_query(self, api_test_client: APITestClient):
    """Test querying model versions."""
    # Generate a random ID
    model_id = generate_id()

    # GraphQL query
    query = """
    query = """
    query($modelId: ID!) {
    query($modelId: ID!) {
    modelVersions(modelId: $modelId) {
    modelVersions(modelId: $modelId) {
    id
    id
    modelId
    modelId
    version
    version
    description
    description
    changes
    changes
    createdAt
    createdAt
    }
    }
    }
    }
    """
    """


    # Make request
    # Make request
    response = api_test_client.graphql_query(query, {"modelId": model_id})
    response = api_test_client.graphql_query(query, {"modelId": model_id})


    # Validate response structure
    # Validate response structure
    result = validate_json_response(response)
    result = validate_json_response(response)


    # GraphQL specific validation
    # GraphQL specific validation
    validate_field_exists(result, "data")
    validate_field_exists(result, "data")
    if "errors" not in result:
    if "errors" not in result:
    data = result["data"]
    data = result["data"]
    validate_field_exists(data, "modelVersions")
    validate_field_exists(data, "modelVersions")
    validate_field_type(data["modelVersions"], list)
    validate_field_type(data["modelVersions"], list)


    def test_model_metrics_query(self, api_test_client: APITestClient):
    def test_model_metrics_query(self, api_test_client: APITestClient):
    """Test querying model metrics."""
    # Generate a random ID
    model_id = generate_id()

    # GraphQL query
    query = """
    query = """
    query($modelId: ID!) {
    query($modelId: ID!) {
    modelMetrics(modelId: $modelId) {
    modelMetrics(modelId: $modelId) {
    modelId
    modelId
    inferenceCount
    inferenceCount
    averageLatency
    averageLatency
    p95Latency
    p95Latency
    p99Latency
    p99Latency
    errorRate
    errorRate
    tokenUsage
    tokenUsage
    cost
    cost
    }
    }
    }
    }
    """
    """


    # Make request
    # Make request
    response = api_test_client.graphql_query(query, {"modelId": model_id})
    response = api_test_client.graphql_query(query, {"modelId": model_id})


    # Validate response structure
    # Validate response structure
    result = validate_json_response(response)
    result = validate_json_response(response)


    # GraphQL specific validation
    # GraphQL specific validation
    validate_field_exists(result, "data")
    validate_field_exists(result, "data")
    if "errors" not in result:
    if "errors" not in result:
    data = result["data"]
    data = result["data"]
    validate_field_exists(data, "modelMetrics")
    validate_field_exists(data, "modelMetrics")


    # Metrics might be None if model doesn't exist
    # Metrics might be None if model doesn't exist
    if data["modelMetrics"]:
    if data["modelMetrics"]:
    metrics = data["modelMetrics"]
    metrics = data["modelMetrics"]
    validate_field_exists(metrics, "modelId")
    validate_field_exists(metrics, "modelId")
    validate_field_equals(metrics, "modelId", model_id)
    validate_field_equals(metrics, "modelId", model_id)
    validate_field_exists(metrics, "inferenceCount")
    validate_field_exists(metrics, "inferenceCount")
    validate_field_exists(metrics, "averageLatency")
    validate_field_exists(metrics, "averageLatency")
    validate_field_exists(metrics, "p95Latency")
    validate_field_exists(metrics, "p95Latency")
    validate_field_exists(metrics, "p99Latency")
    validate_field_exists(metrics, "p99Latency")
    validate_field_exists(metrics, "errorRate")
    validate_field_exists(metrics, "errorRate")
    validate_field_exists(metrics, "tokenUsage")
    validate_field_exists(metrics, "tokenUsage")
    validate_field_exists(metrics, "cost")
    validate_field_exists(metrics, "cost")


    def test_create_model_mutation(self, api_test_client: APITestClient):
    def test_create_model_mutation(self, api_test_client: APITestClient):
    """Test creating an AI model using GraphQL mutation."""
    # Generate test data
    test_data = generate_ai_model_data()

    # GraphQL mutation
    mutation = """
    mutation = """
    mutation($input: ModelInput!) {
    mutation($input: ModelInput!) {
    createModel(input: $input) {
    createModel(input: $input) {
    id
    id
    name
    name
    description
    description
    modelType
    modelType
    provider
    provider
    capabilities
    capabilities
    createdAt
    createdAt
    updatedAt
    updatedAt
    }
    }
    }
    }
    """
    """


    # Variables
    # Variables
    variables = {
    variables = {
    "input": {
    "input": {
    "name": test_data["name"],
    "name": test_data["name"],
    "description": test_data["description"],
    "description": test_data["description"],
    "modelType": test_data["model_type"],
    "modelType": test_data["model_type"],
    "provider": test_data["provider"],
    "provider": test_data["provider"],
    "capabilities": test_data["capabilities"],
    "capabilities": test_data["capabilities"],
    }
    }
    }
    }


    # Make request
    # Make request
    response = api_test_client.graphql_mutation(mutation, variables)
    response = api_test_client.graphql_mutation(mutation, variables)


    # Validate response structure
    # Validate response structure
    result = validate_json_response(response)
    result = validate_json_response(response)


    # GraphQL specific validation
    # GraphQL specific validation
    validate_field_exists(result, "data")
    validate_field_exists(result, "data")
    if "errors" not in result:
    if "errors" not in result:
    data = result["data"]
    data = result["data"]
    validate_field_exists(data, "createModel")
    validate_field_exists(data, "createModel")


    if data["createModel"]:
    if data["createModel"]:
    model = data["createModel"]
    model = data["createModel"]
    validate_field_exists(model, "id")
    validate_field_exists(model, "id")
    validate_field_exists(model, "name")
    validate_field_exists(model, "name")
    validate_field_equals(model, "name", test_data["name"])
    validate_field_equals(model, "name", test_data["name"])
    validate_field_exists(model, "description")
    validate_field_exists(model, "description")
    validate_field_equals(model, "description", test_data["description"])
    validate_field_equals(model, "description", test_data["description"])
    validate_field_exists(model, "modelType")
    validate_field_exists(model, "modelType")
    validate_field_equals(model, "modelType", test_data["model_type"])
    validate_field_equals(model, "modelType", test_data["model_type"])
    validate_field_exists(model, "provider")
    validate_field_exists(model, "provider")
    validate_field_equals(model, "provider", test_data["provider"])
    validate_field_equals(model, "provider", test_data["provider"])
    validate_field_exists(model, "capabilities")
    validate_field_exists(model, "capabilities")
    validate_field_type(model["capabilities"], list)
    validate_field_type(model["capabilities"], list)
    validate_field_exists(model, "createdAt")
    validate_field_exists(model, "createdAt")
    validate_field_exists(model, "updatedAt")
    validate_field_exists(model, "updatedAt")


    def test_update_model_mutation(self, api_test_client: APITestClient):
    def test_update_model_mutation(self, api_test_client: APITestClient):
    """Test updating an AI model using GraphQL mutation."""
    # Generate test data
    model_id = generate_id()
    test_data = generate_ai_model_data()

    # GraphQL mutation
    mutation = """
    mutation = """
    mutation($id: ID!, $input: ModelInput!) {
    mutation($id: ID!, $input: ModelInput!) {
    updateModel(id: $id, input: $input) {
    updateModel(id: $id, input: $input) {
    id
    id
    name
    name
    description
    description
    modelType
    modelType
    provider
    provider
    capabilities
    capabilities
    createdAt
    createdAt
    updatedAt
    updatedAt
    }
    }
    }
    }
    """
    """


    # Variables
    # Variables
    variables = {
    variables = {
    "id": model_id,
    "id": model_id,
    "input": {
    "input": {
    "name": test_data["name"],
    "name": test_data["name"],
    "description": test_data["description"],
    "description": test_data["description"],
    "modelType": test_data["model_type"],
    "modelType": test_data["model_type"],
    "provider": test_data["provider"],
    "provider": test_data["provider"],
    "capabilities": test_data["capabilities"],
    "capabilities": test_data["capabilities"],
    },
    },
    }
    }


    # Make request
    # Make request
    response = api_test_client.graphql_mutation(mutation, variables)
    response = api_test_client.graphql_mutation(mutation, variables)


    # Validate response structure
    # Validate response structure
    result = validate_json_response(response)
    result = validate_json_response(response)


    # GraphQL specific validation
    # GraphQL specific validation
    validate_field_exists(result, "data")
    validate_field_exists(result, "data")
    if "errors" not in result:
    if "errors" not in result:
    data = result["data"]
    data = result["data"]
    validate_field_exists(data, "updateModel")
    validate_field_exists(data, "updateModel")


    # The update might return None if model doesn't exist
    # The update might return None if model doesn't exist
    if data["updateModel"]:
    if data["updateModel"]:
    model = data["updateModel"]
    model = data["updateModel"]
    validate_field_exists(model, "id")
    validate_field_exists(model, "id")
    validate_field_equals(model, "id", model_id)
    validate_field_equals(model, "id", model_id)
    validate_field_exists(model, "name")
    validate_field_exists(model, "name")
    validate_field_equals(model, "name", test_data["name"])
    validate_field_equals(model, "name", test_data["name"])
    validate_field_exists(model, "description")
    validate_field_exists(model, "description")
    validate_field_equals(model, "description", test_data["description"])
    validate_field_equals(model, "description", test_data["description"])
    validate_field_exists(model, "modelType")
    validate_field_exists(model, "modelType")
    validate_field_equals(model, "modelType", test_data["model_type"])
    validate_field_equals(model, "modelType", test_data["model_type"])
    validate_field_exists(model, "provider")
    validate_field_exists(model, "provider")
    validate_field_equals(model, "provider", test_data["provider"])
    validate_field_equals(model, "provider", test_data["provider"])
    validate_field_exists(model, "capabilities")
    validate_field_exists(model, "capabilities")
    validate_field_type(model["capabilities"], list)
    validate_field_type(model["capabilities"], list)
    validate_field_exists(model, "createdAt")
    validate_field_exists(model, "createdAt")
    validate_field_exists(model, "updatedAt")
    validate_field_exists(model, "updatedAt")


    def test_delete_model_mutation(self, api_test_client: APITestClient):
    def test_delete_model_mutation(self, api_test_client: APITestClient):
    """Test deleting an AI model using GraphQL mutation."""
    # Generate a random ID
    model_id = generate_id()

    # GraphQL mutation
    mutation = """
    mutation = """
    mutation($id: ID!) {
    mutation($id: ID!) {
    deleteModel(id: $id)
    deleteModel(id: $id)
    }
    }
    """
    """


    # Make request
    # Make request
    response = api_test_client.graphql_mutation(mutation, {"id": model_id})
    response = api_test_client.graphql_mutation(mutation, {"id": model_id})


    # Validate response structure
    # Validate response structure
    result = validate_json_response(response)
    result = validate_json_response(response)


    # GraphQL specific validation
    # GraphQL specific validation
    validate_field_exists(result, "data")
    validate_field_exists(result, "data")
    if "errors" not in result:
    if "errors" not in result:
    data = result["data"]
    data = result["data"]
    validate_field_exists(data, "deleteModel")
    validate_field_exists(data, "deleteModel")
    validate_field_type(data["deleteModel"], bool)
    validate_field_type(data["deleteModel"], bool)


    def test_error_handling(self, api_test_client: APITestClient):
    def test_error_handling(self, api_test_client: APITestClient):
    """Test GraphQL error handling for AI models."""
    # Test invalid query field
    query = """
    query = """
    query {
    query {
    aiModels {
    aiModels {
    invalidField
    invalidField
    }
    }
    }
    }
    """
    """


    response = api_test_client.graphql_query(query)
    response = api_test_client.graphql_query(query)
    result = validate_json_response(response)
    result = validate_json_response(response)
    validate_field_exists(result, "errors")
    validate_field_exists(result, "errors")


    # Test invalid mutation input
    # Test invalid mutation input
    mutation = """
    mutation = """
    mutation($input: ModelInput!) {
    mutation($input: ModelInput!) {
    createModel(input: $input) {
    createModel(input: $input) {
    id
    id
    name
    name
    }
    }
    }
    }
    """
    """


    response = api_test_client.graphql_mutation(
    response = api_test_client.graphql_mutation(
    mutation,
    mutation,
    {
    {
    "input": {
    "input": {
    # Missing required fields
    # Missing required fields
    "description": "Invalid model"
    "description": "Invalid model"
    }
    }
    },
    },
    )
    )
    result = validate_json_response(response)
    result = validate_json_response(response)
    validate_field_exists(result, "errors")
    validate_field_exists(result, "errors")