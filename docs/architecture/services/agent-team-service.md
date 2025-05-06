# Agent Team Service Design

## Overview

The Agent Team Service manages AI agent teams, their configurations, and interactions for the pAIssive income platform. It orchestrates specialized AI agents that work together to accomplish complex tasks, allowing for the creation, configuration, and monitoring of agent teams.

## Responsibilities

- Manage agent team configurations
- Define agent roles and capabilities
- Coordinate agent interactions and workflows
- Manage agent execution and task allocation
- Track agent performance metrics
- Handle agent communication patterns
- Provide agent team templates for common use cases
- Support agent fallback and error handling

## API Design

### External API (Service-to-Service)

#### Team Management
- `POST /api/agents/teams` - Create a new agent team
- `GET /api/agents/teams` - List all agent teams
- `GET /api/agents/teams/{id}` - Get a specific team
- `PUT /api/agents/teams/{id}` - Update a team configuration
- `DELETE /api/agents/teams/{id}` - Delete a team
- `GET /api/agents/teams/templates` - List team templates

#### Agent Management
- `GET /api/agents/teams/{team_id}/agents` - List all agents in a team
- `POST /api/agents/teams/{team_id}/agents` - Add an agent to a team
- `GET /api/agents/teams/{team_id}/agents/{agent_id}` - Get specific agent details
- `PUT /api/agents/teams/{team_id}/agents/{agent_id}` - Update agent configuration
- `DELETE /api/agents/teams/{team_id}/agents/{agent_id}` - Remove agent from team

#### Task Execution
- `POST /api/agents/teams/{team_id}/tasks` - Create and execute a team task
- `GET /api/agents/teams/{team_id}/tasks` - List all tasks for a team
- `GET /api/agents/teams/{team_id}/tasks/{task_id}` - Get task details
- `PUT /api/agents/teams/{team_id}/tasks/{task_id}` - Update task status
- `DELETE /api/agents/teams/{team_id}/tasks/{task_id}` - Cancel a task

#### Performance Monitoring
- `GET /api/agents/teams/{team_id}/performance` - Get team performance metrics
- `GET /api/agents/teams/{team_id}/agents/{agent_id}/performance` - Get agent performance metrics

## Technology Stack

- **Framework**: FastAPI
- **Agent Communication**: Asynchronous messaging
- **State Management**: Redis for agent state
- **Task Queuing**: RabbitMQ for agent tasks
- **Data Storage**: MongoDB (via Database Service)
- **Coordination**: Custom agent coordinator module
- **Performance Tracking**: Prometheus metrics

## Service Dependencies

- **AI Models Service** - For AI model inference
- **Database Service** - For storing team configurations and task results
- **API Gateway** - For routing requests
- **Message Queue** - For asynchronous task processing

## Data Model

### Agent Team
```
{
  "id": "string",
  "name": "string",
  "description": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "status": "active|paused|archived",
  "team_type": "string",  // e.g., "content-creation", "market-research"
  "configuration": {
    "coordination_strategy": "string",
    "iteration_limit": int,
    "timeout_seconds": int,
    "error_handling": "string"
  },
  "agents": [
    {
      "agent_id": "string",
      "name": "string",
      "role": "string",
      "capabilities": ["string"],
      "model_config": {
        "model_id": "string",
        "parameters": {}
      },
      "input_requirements": ["string"],
      "output_format": "string",
      "position": int  // execution order
    }
  ],
  "workflows": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "steps": [
        {
          "agent_id": "string",
          "dependencies": ["string"],  // IDs of steps that must complete first
          "retry_policy": {
            "max_attempts": int,
            "backoff_seconds": int
          }
        }
      ]
    }
  ],
  "metrics": {
    "tasks_completed": int,
    "tasks_failed": int,
    "avg_completion_time_seconds": float,
    "last_execution": "datetime"
  }
}
```

### Agent Task
```
{
  "id": "string",
  "team_id": "string",
  "workflow_id": "string",
  "status": "pending|in_progress|completed|failed|cancelled",
  "created_at": "datetime",
  "updated_at": "datetime",
  "priority": int,
  "input": {
    "data": {},
    "instructions": "string"
  },
  "execution": {
    "current_step": int,
    "start_time": "datetime",
    "end_time": "datetime",
    "duration_seconds": float,
    "steps_completed": int,
    "steps_total": int
  },
  "agent_results": [
    {
      "agent_id": "string",
      "step": int,
      "start_time": "datetime",
      "end_time": "datetime",
      "input": {},
      "output": {},
      "status": "string",
      "error": "string"
    }
  ],
  "output": {},
  "metadata": {
    "user_id": "string",
    "source": "string",
    "tags": ["string"]
  },
  "error": {
    "message": "string",
    "agent_id": "string",
    "step": int,
    "timestamp": "datetime"
  }
}
```

## Sequence Diagrams

### Agent Team Task Execution Flow

```
┌────────┐     ┌────────────────┐     ┌────────────────┐     ┌────────────┐     ┌───────────────┐
│ Client │     │ Agent Team Svc │     │ Task Coordinator│     │ AI Models  │     │ Database Svc  │
└───┬────┘     └───────┬────────┘     └────────┬───────┘     └─────┬──────┘     └───────┬───────┘
    │                  │                       │                   │                    │
    │ Create Task      │                       │                   │                    │
    │─────────────────>│                       │                   │                    │
    │                  │                       │                   │                    │
    │                  │ Load Team Config      │                   │                    │
    │                  │───────────────────────────────────────────────────────────────>│
    │                  │                       │                   │                    │
    │                  │ Return Config         │                   │                    │
    │                  │<───────────────────────────────────────────────────────────────│
    │                  │                       │                   │                    │
    │                  │ Initiate Task         │                   │                    │
    │                  │──────────────────────>│                   │                    │
    │                  │                       │                   │                    │
    │ Task Created     │                       │                   │                    │
    │<─────────────────│                       │                   │                    │
    │                  │                       │                   │                    │
    │                  │                       │ Execute Agent 1   │                    │
    │                  │                       │─────────────────->│                    │
    │                  │                       │                   │                    │
    │                  │                       │ Agent 1 Result    │                    │
    │                  │                       │<──────────────────│                    │
    │                  │                       │                   │                    │
    │                  │                       │ Execute Agent 2   │                    │
    │                  │                       │─────────────────->│                    │
    │                  │                       │                   │                    │
    │                  │                       │ Agent 2 Result    │                    │
    │                  │                       │<──────────────────│                    │
    │                  │                       │                   │                    │
    │                  │                       │ Update Task State │                    │
    │                  │                       │───────────────────────────────────────>│
    │                  │                       │                   │                    │
    │                  │                       │ Store Final Result│                    │
    │                  │                       │───────────────────────────────────────>│
    │                  │                       │                   │                    │
    │                  │ Task Completed        │                   │                    │
    │                  │<─────────────────────│                    │                    │
    │                  │                       │                   │                    │
    │ Check Task Status│                       │                   │                    │
    │─────────────────>│                       │                   │                    │
    │                  │                       │                   │                    │
    │ Task Result      │                       │                   │                    │
    │<─────────────────│                       │                   │                    │
    │                  │                       │                   │                    │
```

### Team Configuration Flow

```
┌────────┐          ┌────────────────┐          ┌───────────────────┐
│ Client │          │ Agent Team Svc │          │ Database Service  │
└───┬────┘          └───────┬────────┘          └─────────┬─────────┘
    │                       │                             │
    │ Create Team Request   │                             │
    │──────────────────────>│                             │
    │                       │                             │
    │                       │ Validate Agent Config       │
    │                       │──────┐                      │
    │                       │      │                      │
    │                       │<─────┘                      │
    │                       │                             │
    │                       │ Test Agent Compatibility    │
    │                       │──────┐                      │
    │                       │      │                      │
    │                       │<─────┘                      │
    │                       │                             │
    │                       │ Store Team Configuration    │
    │                       │───────────────────────────->│
    │                       │                             │
    │                       │ Configuration Stored        │
    │                       │<────────────────────────────│
    │                       │                             │
    │                       │ Create Default Workflows    │
    │                       │───────────────────────────->│
    │                       │                             │
    │                       │ Workflows Created           │
    │                       │<────────────────────────────│
    │                       │                             │
    │ Team Created Response │                             │
    │<──────────────────────│                             │
    │                       │                             │
```

## Scaling Considerations

- Horizontal scaling for concurrent task execution
- Agent task prioritization and queueing
- Stateless design for agent team service
- Smart task distribution based on agent load
- Timeout handling for long-running tasks
- Backpressure mechanisms to prevent overload

## Monitoring and Logging

- Agent task success/failure rates
- Agent execution time metrics
- Team completion time metrics
- Error types and frequencies
- Agent coordination overhead
- Queue depths and task wait times
- Resource utilization per agent type

## Security Considerations

- Input validation for agent instructions
- Output sanitization for agent responses
- Isolation between different team executions
- Rate limiting for resource-intensive agents
- Access control for team configurations
- Audit logging for agent actions
- Content filtering for AI-generated outputs

## Implementation Plan

1. Port existing agent team components to microservice
2. Implement core team management APIs
3. Create the agent coordination system
4. Implement task execution engine
5. Add agent performance monitoring
6. Create team templates for common use cases
7. Implement error handling and fallback strategies
8. Set up asynchronous task processing
