# Project Structure

This document provides an overview of the pAIssive Income Framework's project structure, explaining how the different components are organized and how they relate to each other.

## Directory Structure

The framework is organized into the following main directories:

```
pAIssive_income/
├── agent_team/           # Agent Team module
├── ai_models/            # AI Models module
├── docs/                 # Documentation
├── marketing/            # Marketing module
├── monetization/         # Monetization module
├── niche_analysis/       # Niche Analysis module
├── tool_templates/       # Tool Templates module
├── ui/                   # UI module
├── tests/                # Tests
├── examples/             # Example scripts
├── LICENSE               # MIT License
└── README.md             # Project README
```

## Module Descriptions

### Agent Team Module

The `agent_team` directory contains the implementation of the Agent Team, which is a team of specialized AI agents that collaborate on developing and monetizing niche AI tools.

Key files:
- `__init__.py`: Module initialization
- `agent_team.py`: Main AgentTeam class
- `researcher_agent.py`: Researcher Agent implementation
- `developer_agent.py`: Developer Agent implementation
- `monetization_agent.py`: Monetization Agent implementation
- `marketing_agent.py`: Marketing Agent implementation
- `feedback_agent.py`: Feedback Agent implementation

### AI Models Module

The `ai_models` directory contains the implementation of the AI Models system, which manages and uses local AI models for various tasks.

Key files:
- `__init__.py`: Module initialization
- `model_manager.py`: Model Manager implementation
- `model_config.py`: Model configuration
- `model_downloader.py`: Model downloader
- `performance_monitor.py`: Performance monitoring
- `adapters/`: Adapters for different model backends

### Niche Analysis Module

The `niche_analysis` directory contains the implementation of the Niche Analysis system, which analyzes market segments and identifies profitable niches.

Key files:
- `__init__.py`: Module initialization
- `market_analyzer.py`: Market Analyzer implementation
- `problem_identifier.py`: Problem Identifier implementation
- `opportunity_scorer.py`: Opportunity Scorer implementation

### Monetization Module

The `monetization` directory contains the implementation of the Monetization system, which creates subscription models and pricing strategies.

Key files:
- `__init__.py`: Module initialization
- `subscription_models.py`: Subscription Models implementation
- `pricing_calculator.py`: Pricing Calculator implementation
- `revenue_projector.py`: Revenue Projector implementation
- `subscription_management.py`: Subscription Management implementation
- `payment_processing.py`: Payment Processing implementation

### Marketing Module

The `marketing` directory contains the implementation of the Marketing system, which creates marketing strategies and content.

Key files:
- `__init__.py`: Module initialization
- `user_personas.py`: User Personas implementation
- `channel_strategies.py`: Channel Strategies implementation
- `content_templates.py`: Content Templates implementation
- `content_generators.py`: Content Generators implementation
- `content_optimization.py`: Content Optimization implementation

### Tool Templates Module

The `tool_templates` directory contains templates for creating different types of AI-powered tools.

Key files:
- `__init__.py`: Module initialization
- `ui_templates.py`: UI Templates implementation
- `backend_templates.py`: Backend Templates implementation
- `integration_templates.py`: Integration Templates implementation
- `deployment_templates.py`: Deployment Templates implementation

### UI Module

The `ui` directory contains the implementation of the web interface for interacting with the framework.

Key files:
- `__init__.py`: Module initialization
- `app.py`: Entry point for running the web interface
- `routes.py`: URL routes and request handlers
- `services/`: Service classes for interacting with the framework components
- `templates/`: HTML templates for the web interface
- `static/`: Static files (CSS, JavaScript, images)
- `data/`: Data storage for the UI (JSON files)

## Relationships Between Components

The components of the framework are designed to work together to provide a complete solution for developing and monetizing niche AI tools:

1. The **Agent Team** coordinates the overall process, using the other components to perform specific tasks.
2. The **Niche Analysis** component identifies profitable niches for AI tools.
3. The **AI Models** component provides the AI capabilities for the tools.
4. The **Tool Templates** component provides templates for creating the tools.
5. The **Monetization** component creates subscription models and pricing strategies.
6. The **Marketing** component creates marketing strategies and content.
7. The **UI** component provides a web interface for interacting with the framework.

## Flow of Information

The typical flow of information through the framework is as follows:

1. The user selects market segments to analyze.
2. The Researcher Agent uses the Niche Analysis component to identify profitable niches.
3. The user selects a niche to develop a solution for.
4. The Developer Agent uses the AI Models and Tool Templates components to design and develop a solution.
5. The Monetization Agent uses the Monetization component to create a monetization strategy.
6. The Marketing Agent uses the Marketing component to create a marketing campaign.
7. The Feedback Agent collects and analyzes user feedback to improve the solution.

## Extending the Framework

The framework is designed to be extensible, allowing users to add new components or modify existing ones. To extend the framework:

1. Create a new directory for your component.
2. Implement the necessary classes and functions.
3. Update the documentation to reflect your changes.
4. Add tests for your component.
5. Submit a pull request if you want to contribute your changes to the main repository.

For more information on contributing to the framework, see the [Contributing](contributing.md) guide.
