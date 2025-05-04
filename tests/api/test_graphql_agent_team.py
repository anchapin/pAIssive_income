"""
"""
Tests for the Agent Team GraphQL API.
Tests for the Agent Team GraphQL API.


This module contains tests for Agent Team GraphQL queries and mutations.
This module contains tests for Agent Team GraphQL queries and mutations.
"""
"""




from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import generate_agent_team_data, generate_id
from tests.api.utils.test_data import generate_agent_team_data, generate_id


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




class TestAgentTeamGraphQLAPI:
    class TestAgentTeamGraphQLAPI:
    """Tests for the Agent Team GraphQL API."""

    def test_agent_teams_query(self, api_test_client: APITestClient):
    """Test querying agent teams."""
    # GraphQL query
    query = """
    query = """
    query {
    query {
    agentTeams {
    agentTeams {
    id
    id
    name
    name
    description
    description
    agents {
    agents {
    id
    id
    name
    name
    role
    role
    modelId
    modelId
    capabilities
    capabilities
    }
    }
    workflowSettings {
    workflowSettings {
    parallelExecution
    parallelExecution
    reviewSteps
    reviewSteps
    autoCorrection
    autoCorrection
    }
    }
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
    validate_field_exists(data, "agentTeams")
    validate_field_exists(data, "agentTeams")
    validate_field_type(data["agentTeams"], list)
    validate_field_type(data["agentTeams"], list)


    # If there are teams, validate their structure
    # If there are teams, validate their structure
    if data["agentTeams"]:
    if data["agentTeams"]:
    team = data["agentTeams"][0]
    team = data["agentTeams"][0]
    validate_field_exists(team, "id")
    validate_field_exists(team, "id")
    validate_field_exists(team, "name")
    validate_field_exists(team, "name")
    validate_field_exists(team, "description")
    validate_field_exists(team, "description")
    validate_field_exists(team, "agents")
    validate_field_exists(team, "agents")
    validate_field_type(team["agents"], list)
    validate_field_type(team["agents"], list)
    validate_field_exists(team, "workflowSettings")
    validate_field_exists(team, "workflowSettings")
    validate_field_exists(team, "createdAt")
    validate_field_exists(team, "createdAt")
    validate_field_exists(team, "updatedAt")
    validate_field_exists(team, "updatedAt")


    def test_agent_team_query(self, api_test_client: APITestClient):
    def test_agent_team_query(self, api_test_client: APITestClient):
    """Test querying a specific agent team."""
    # Generate a random ID
    team_id = generate_id()

    # GraphQL query
    query = """
    query = """
    query($id: ID!) {
    query($id: ID!) {
    agentTeam(id: $id) {
    agentTeam(id: $id) {
    id
    id
    name
    name
    description
    description
    agents {
    agents {
    id
    id
    name
    name
    role
    role
    modelId
    modelId
    capabilities
    capabilities
    }
    }
    workflowSettings {
    workflowSettings {
    parallelExecution
    parallelExecution
    reviewSteps
    reviewSteps
    autoCorrection
    autoCorrection
    }
    }
    metrics {
    metrics {
    completedTasks
    completedTasks
    successRate
    successRate
    averageResponseTime
    averageResponseTime
    activeAgents
    activeAgents
    }
    }
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


    # Make request
    # Make request
    response = api_test_client.graphql_query(query, {"id": team_id})
    response = api_test_client.graphql_query(query, {"id": team_id})


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
    validate_field_exists(data, "agentTeam")
    validate_field_exists(data, "agentTeam")


    # The team might not exist, which is fine
    # The team might not exist, which is fine
    if data["agentTeam"]:
    if data["agentTeam"]:
    team = data["agentTeam"]
    team = data["agentTeam"]
    validate_field_exists(team, "id")
    validate_field_exists(team, "id")
    validate_field_equals(team, "id", team_id)
    validate_field_equals(team, "id", team_id)
    validate_field_exists(team, "name")
    validate_field_exists(team, "name")
    validate_field_exists(team, "description")
    validate_field_exists(team, "description")
    validate_field_exists(team, "agents")
    validate_field_exists(team, "agents")
    validate_field_type(team["agents"], list)
    validate_field_type(team["agents"], list)
    validate_field_exists(team, "workflowSettings")
    validate_field_exists(team, "workflowSettings")
    validate_field_exists(team, "metrics")
    validate_field_exists(team, "metrics")
    validate_field_exists(team, "createdAt")
    validate_field_exists(team, "createdAt")
    validate_field_exists(team, "updatedAt")
    validate_field_exists(team, "updatedAt")


    def test_agent_conversations_query(self, api_test_client: APITestClient):
    def test_agent_conversations_query(self, api_test_client: APITestClient):
    """Test querying agent conversations."""
    # Generate a random ID
    team_id = generate_id()

    # GraphQL query
    query = """
    query = """
    query($teamId: ID!) {
    query($teamId: ID!) {
    agentConversations(teamId: $teamId) {
    agentConversations(teamId: $teamId) {
    id
    id
    teamId
    teamId
    agents {
    agents {
    id
    id
    name
    name
    role
    role
    }
    }
    messages {
    messages {
    id
    id
    agentId
    agentId
    content
    content
    type
    type
    timestamp
    timestamp
    }
    }
    status
    status
    startedAt
    startedAt
    completedAt
    completedAt
    }
    }
    }
    }
    """
    """


    # Make request
    # Make request
    response = api_test_client.graphql_query(query, {"teamId": team_id})
    response = api_test_client.graphql_query(query, {"teamId": team_id})


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
    validate_field_exists(data, "agentConversations")
    validate_field_exists(data, "agentConversations")
    validate_field_type(data["agentConversations"], list)
    validate_field_type(data["agentConversations"], list)


    # If there are conversations, validate their structure
    # If there are conversations, validate their structure
    if data["agentConversations"]:
    if data["agentConversations"]:
    conversation = data["agentConversations"][0]
    conversation = data["agentConversations"][0]
    validate_field_exists(conversation, "id")
    validate_field_exists(conversation, "id")
    validate_field_exists(conversation, "teamId")
    validate_field_exists(conversation, "teamId")
    validate_field_exists(conversation, "agents")
    validate_field_exists(conversation, "agents")
    validate_field_type(conversation["agents"], list)
    validate_field_type(conversation["agents"], list)
    validate_field_exists(conversation, "messages")
    validate_field_exists(conversation, "messages")
    validate_field_type(conversation["messages"], list)
    validate_field_type(conversation["messages"], list)
    validate_field_exists(conversation, "status")
    validate_field_exists(conversation, "status")
    validate_field_exists(conversation, "startedAt")
    validate_field_exists(conversation, "startedAt")
    validate_field_exists(conversation, "completedAt")
    validate_field_exists(conversation, "completedAt")


    def test_create_agent_team_mutation(self, api_test_client: APITestClient):
    def test_create_agent_team_mutation(self, api_test_client: APITestClient):
    """Test creating an agent team using GraphQL mutation."""
    # Generate test data
    test_data = generate_agent_team_data()

    # GraphQL mutation
    mutation = """
    mutation = """
    mutation($input: AgentTeamInput!) {
    mutation($input: AgentTeamInput!) {
    createAgentTeam(input: $input) {
    createAgentTeam(input: $input) {
    id
    id
    name
    name
    description
    description
    agents {
    agents {
    id
    id
    name
    name
    role
    role
    modelId
    modelId
    capabilities
    capabilities
    }
    }
    workflowSettings {
    workflowSettings {
    parallelExecution
    parallelExecution
    reviewSteps
    reviewSteps
    autoCorrection
    autoCorrection
    }
    }
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
    "agents": test_data["agents"],
    "agents": test_data["agents"],
    "workflowSettings": test_data["workflow_settings"],
    "workflowSettings": test_data["workflow_settings"],
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
    validate_field_exists(data, "createAgentTeam")
    validate_field_exists(data, "createAgentTeam")


    if data["createAgentTeam"]:
    if data["createAgentTeam"]:
    team = data["createAgentTeam"]
    team = data["createAgentTeam"]
    validate_field_exists(team, "id")
    validate_field_exists(team, "id")
    validate_field_exists(team, "name")
    validate_field_exists(team, "name")
    validate_field_equals(team, "name", test_data["name"])
    validate_field_equals(team, "name", test_data["name"])
    validate_field_exists(team, "description")
    validate_field_exists(team, "description")
    validate_field_equals(team, "description", test_data["description"])
    validate_field_equals(team, "description", test_data["description"])
    validate_field_exists(team, "agents")
    validate_field_exists(team, "agents")
    validate_field_type(team["agents"], list)
    validate_field_type(team["agents"], list)
    validate_field_exists(team, "workflowSettings")
    validate_field_exists(team, "workflowSettings")
    validate_field_exists(team, "createdAt")
    validate_field_exists(team, "createdAt")
    validate_field_exists(team, "updatedAt")
    validate_field_exists(team, "updatedAt")


    def test_update_agent_team_mutation(self, api_test_client: APITestClient):
    def test_update_agent_team_mutation(self, api_test_client: APITestClient):
    """Test updating an agent team using GraphQL mutation."""
    # Generate test data
    team_id = generate_id()
    test_data = generate_agent_team_data()

    # GraphQL mutation
    mutation = """
    mutation = """
    mutation($id: ID!, $input: AgentTeamInput!) {
    mutation($id: ID!, $input: AgentTeamInput!) {
    updateAgentTeam(id: $id, input: $input) {
    updateAgentTeam(id: $id, input: $input) {
    id
    id
    name
    name
    description
    description
    agents {
    agents {
    id
    id
    name
    name
    role
    role
    modelId
    modelId
    capabilities
    capabilities
    }
    }
    workflowSettings {
    workflowSettings {
    parallelExecution
    parallelExecution
    reviewSteps
    reviewSteps
    autoCorrection
    autoCorrection
    }
    }
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
    "id": team_id,
    "id": team_id,
    "input": {
    "input": {
    "name": test_data["name"],
    "name": test_data["name"],
    "description": test_data["description"],
    "description": test_data["description"],
    "agents": test_data["agents"],
    "agents": test_data["agents"],
    "workflowSettings": test_data["workflow_settings"],
    "workflowSettings": test_data["workflow_settings"],
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
    validate_field_exists(data, "updateAgentTeam")
    validate_field_exists(data, "updateAgentTeam")


    # The update might return None if team doesn't exist
    # The update might return None if team doesn't exist
    if data["updateAgentTeam"]:
    if data["updateAgentTeam"]:
    team = data["updateAgentTeam"]
    team = data["updateAgentTeam"]
    validate_field_exists(team, "id")
    validate_field_exists(team, "id")
    validate_field_equals(team, "id", team_id)
    validate_field_equals(team, "id", team_id)
    validate_field_exists(team, "name")
    validate_field_exists(team, "name")
    validate_field_equals(team, "name", test_data["name"])
    validate_field_equals(team, "name", test_data["name"])
    validate_field_exists(team, "description")
    validate_field_exists(team, "description")
    validate_field_equals(team, "description", test_data["description"])
    validate_field_equals(team, "description", test_data["description"])
    validate_field_exists(team, "agents")
    validate_field_exists(team, "agents")
    validate_field_type(team["agents"], list)
    validate_field_type(team["agents"], list)
    validate_field_exists(team, "workflowSettings")
    validate_field_exists(team, "workflowSettings")
    validate_field_exists(team, "createdAt")
    validate_field_exists(team, "createdAt")
    validate_field_exists(team, "updatedAt")
    validate_field_exists(team, "updatedAt")


    def test_delete_agent_team_mutation(self, api_test_client: APITestClient):
    def test_delete_agent_team_mutation(self, api_test_client: APITestClient):
    """Test deleting an agent team using GraphQL mutation."""
    # Generate a random ID
    team_id = generate_id()

    # GraphQL mutation
    mutation = """
    mutation = """
    mutation($id: ID!) {
    mutation($id: ID!) {
    deleteAgentTeam(id: $id)
    deleteAgentTeam(id: $id)
    }
    }
    """
    """


    # Make request
    # Make request
    response = api_test_client.graphql_mutation(mutation, {"id": team_id})
    response = api_test_client.graphql_mutation(mutation, {"id": team_id})


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
    validate_field_exists(data, "deleteAgentTeam")
    validate_field_exists(data, "deleteAgentTeam")
    validate_field_type(data["deleteAgentTeam"], bool)
    validate_field_type(data["deleteAgentTeam"], bool)


    def test_agent_task_mutation(self, api_test_client: APITestClient):
    def test_agent_task_mutation(self, api_test_client: APITestClient):
    """Test running an agent task using GraphQL mutation."""
    # Generate test data
    team_id = generate_id()
    agent_id = generate_id()

    # GraphQL mutation
    mutation = """
    mutation = """
    mutation($input: AgentTaskInput!) {
    mutation($input: AgentTaskInput!) {
    runAgentTask(input: $input) {
    runAgentTask(input: $input) {
    taskId
    taskId
    agentId
    agentId
    teamId
    teamId
    status
    status
    result {
    result {
    output
    output
    metadata
    metadata
    timestamp
    timestamp
    }
    }
    metrics {
    metrics {
    startTime
    startTime
    completionTime
    completionTime
    processingTime
    processingTime
    tokens {
    tokens {
    input
    input
    output
    output
    total
    total
    }
    }
    }
    }
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
    "teamId": team_id,
    "teamId": team_id,
    "agentId": agent_id,
    "agentId": agent_id,
    "task": {
    "task": {
    "type": "analyze_niche",
    "type": "analyze_niche",
    "parameters": {
    "parameters": {
    "marketSegment": "e-commerce",
    "marketSegment": "e-commerce",
    "targetAudience": "small businesses",
    "targetAudience": "small businesses",
    },
    },
    },
    },
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
    validate_field_exists(data, "runAgentTask")
    validate_field_exists(data, "runAgentTask")


    if data["runAgentTask"]:
    if data["runAgentTask"]:
    task = data["runAgentTask"]
    task = data["runAgentTask"]
    validate_field_exists(task, "taskId")
    validate_field_exists(task, "taskId")
    validate_field_exists(task, "agentId")
    validate_field_exists(task, "agentId")
    validate_field_equals(task, "agentId", agent_id)
    validate_field_equals(task, "agentId", agent_id)
    validate_field_exists(task, "teamId")
    validate_field_exists(task, "teamId")
    validate_field_equals(task, "teamId", team_id)
    validate_field_equals(task, "teamId", team_id)
    validate_field_exists(task, "status")
    validate_field_exists(task, "status")
    validate_field_exists(task, "result")
    validate_field_exists(task, "result")
    validate_field_exists(task, "metrics")
    validate_field_exists(task, "metrics")


    def test_error_handling(self, api_test_client: APITestClient):
    def test_error_handling(self, api_test_client: APITestClient):
    """Test GraphQL error handling for agent team operations."""
    # Test invalid query field
    query = """
    query = """
    query {
    query {
    agentTeams {
    agentTeams {
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
    mutation($input: AgentTeamInput!) {
    mutation($input: AgentTeamInput!) {
    createAgentTeam(input: $input) {
    createAgentTeam(input: $input) {
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
    "description": "Invalid team"
    "description": "Invalid team"
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