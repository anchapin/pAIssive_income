# Agent Team

The Agent Team module is a core component of the pAIssive Income Framework. It provides a team of specialized AI agents that collaborate on developing and monetizing niche AI tools for passive income generation.

## Overview

The Agent Team consists of five specialized agents:

1. **Researcher Agent**: Analyzes market segments and identifies profitable niches.
2. **Developer Agent**: Designs and develops AI-powered solutions for specific niches.
3. **Monetization Agent**: Creates monetization strategies with subscription models.
4. **Marketing Agent**: Develops marketing strategies and content for target users.
5. **Feedback Agent**: Collects and analyzes user feedback to improve solutions.

These agents work together in a coordinated workflow to take a project from initial market research to a fully developed, monetized, and marketed AI tool.

## AgentTeam Class

The `AgentTeam` class is the main entry point for working with the agent team. It manages the team's configuration, state, and workflow.

```python
from agent_team import AgentTeam

# Create a team with default configuration
team = AgentTeam("My Team")

# Create a team with custom configuration
team = AgentTeam("My Team", config_path="path/to/config.json")
```

### Configuration

The `AgentTeam` class can be configured with a JSON configuration file. The configuration includes:

- **Model Settings**: AI model settings for each agent (model name, temperature, etc.)
- **Workflow Settings**: Settings for the team's workflow (auto progression, review required, etc.)

Example configuration:

```json
{
    "model_settings": {
        "researcher": {"model": "gpt-4", "temperature": 0.7},
        "developer": {"model": "gpt-4", "temperature": 0.2},
        "monetization": {"model": "gpt-4", "temperature": 0.5},
        "marketing": {"model": "gpt-4", "temperature": 0.8},
        "feedback": {"model": "gpt-4", "temperature": 0.3}
    },
    "workflow": {
        "auto_progression": false,
        "review_required": true
    }
}
```

### Project State

The `AgentTeam` class maintains a project state that tracks the progress of the project. The project state includes:

- **Identified Niches**: Niches identified by the Researcher Agent
- **Selected Niche**: The niche selected for development
- **User Problems**: User problems identified by the Researcher Agent
- **Solution Design**: Solution design created by the Developer Agent
- **Development Plan**: Development plan created by the Developer Agent
- **Monetization Strategy**: Monetization strategy created by the Monetization Agent
- **Marketing Campaign**: Marketing campaign created by the Marketing Agent
- **User Feedback**: User feedback collected by the Feedback Agent

## Agent Profiles

### Researcher Agent

The Researcher Agent is responsible for analyzing market segments and identifying profitable niches. It uses AI to:

- Analyze market segments to identify potential niches
- Evaluate market size, growth rate, and competition
- Identify user problems and pain points
- Score opportunities based on various factors

```python
from agent_team import ResearchAgent

# Create a researcher agent
researcher = ResearchAgent()

# Analyze a market segment
market_data = researcher.analyze_market("e-commerce")

# Identify problems in a niche
problems = researcher.identify_problems("inventory management for small e-commerce")

# Score an opportunity
opportunity = researcher.score_opportunity("inventory management for small e-commerce", market_data, problems)
```

### Developer Agent

The Developer Agent is responsible for designing and developing AI-powered solutions for specific niches. It uses AI to:

- Design solutions based on user problems
- Create development plans with phases and tasks
- Implement solutions with code and AI models
- Test and refine solutions

```python
from agent_team import DeveloperAgent

# Create a developer agent
developer = DeveloperAgent()

# Design a solution
solution = developer.design_solution(niche)

# Create a development plan
plan = developer.create_development_plan(solution)

# Implement a solution
implementation = developer.implement_solution(solution, plan)
```

### Monetization Agent

The Monetization Agent is responsible for creating monetization strategies with subscription models. It uses AI to:

- Create subscription models with different tiers and features
- Calculate optimal pricing for each tier
- Project revenue based on different scenarios
- Optimize monetization strategies for maximum revenue

```python
from agent_team import MonetizationAgent

# Create a monetization agent
monetization = MonetizationAgent()

# Create a monetization strategy
strategy = monetization.create_strategy(solution)

# Calculate pricing
pricing = monetization.calculate_pricing(strategy)

# Project revenue
projection = monetization.project_revenue(strategy, pricing)
```

### Marketing Agent

The Marketing Agent is responsible for developing marketing strategies and content for target users. It uses AI to:

- Create user personas for target users
- Develop marketing strategies for different channels
- Generate marketing content for various platforms
- Optimize content for maximum engagement

```python
from agent_team import MarketingAgent

# Create a marketing agent
marketing = MarketingAgent()

# Create user personas
personas = marketing.create_personas(solution)

# Develop a marketing strategy
strategy = marketing.develop_strategy(solution, personas)

# Generate marketing content
content = marketing.generate_content(strategy)
```

### Feedback Agent

The Feedback Agent is responsible for collecting and analyzing user feedback to improve solutions. It uses AI to:

- Collect feedback from users
- Analyze feedback to identify patterns and insights
- Generate improvement recommendations
- Track user satisfaction over time

```python
from agent_team import FeedbackAgent

# Create a feedback agent
feedback = FeedbackAgent()

# Collect feedback
user_feedback = feedback.collect_feedback(solution)

# Analyze feedback
analysis = feedback.analyze_feedback(user_feedback)

# Generate recommendations
recommendations = feedback.generate_recommendations(analysis)
```

## Workflow

The typical workflow for using the Agent Team is as follows:

1. **Create a Team**: Create an `AgentTeam` instance with a name and optional configuration.
2. **Run Niche Analysis**: Use the Researcher Agent to identify profitable niches.
3. **Select a Niche**: Select a niche from the identified niches.
4. **Develop a Solution**: Use the Developer Agent to design and develop a solution.
5. **Create a Monetization Strategy**: Use the Monetization Agent to create a monetization strategy.
6. **Create a Marketing Campaign**: Use the Marketing Agent to create a marketing campaign.
7. **Collect and Analyze Feedback**: Use the Feedback Agent to collect and analyze user feedback.
8. **Iterate and Improve**: Use the feedback to iterate and improve the solution.

```python
from agent_team import AgentTeam

# Create a team
team = AgentTeam("Niche AI Tools")

# Run niche analysis
niches = team.run_niche_analysis(["e-commerce", "content creation"])

# Select a niche
selected_niche = niches[0]

# Develop a solution
solution = team.develop_solution(selected_niche["id"])

# Create a monetization strategy
monetization_strategy = team.create_monetization_strategy(solution["id"])

# Create a marketing campaign
marketing_campaign = team.create_marketing_campaign(solution["id"], monetization_strategy["id"])

# Collect and analyze feedback
feedback_analysis = team.collect_and_analyze_feedback(solution["id"])

# Iterate and improve
improved_solution = team.iterate_and_improve(solution["id"], feedback_analysis["id"])
```

## Integration with AI Models

The Agent Team can be integrated with local AI models using the `AgentModelProvider` class from the `ai_models` module. This allows the agents to use local AI models for their tasks instead of relying on external API calls.

```python
from agent_team import AgentTeam
from ai_models import ModelManager, AgentModelProvider

# Create a model manager
manager = ModelManager()

# Create an agent model provider
provider = AgentModelProvider(manager)

# Create a team with the agent model provider
team = AgentTeam("My Team", agent_model_provider=provider)

# Now the team will use local AI models for its tasks
```

## Example: Complete Workflow

Here's a complete example that demonstrates the entire workflow of the Agent Team:

```python
from agent_team import AgentTeam

# Create a team
team = AgentTeam("Niche AI Tools")

# Define market segments to analyze
market_segments = [
    "e-commerce",
    "content creation",
    "freelancing",
    "education",
    "real estate",
]

# Run niche analysis
niches = team.run_niche_analysis(market_segments)

# Print identified niches
for i, niche in enumerate(niches):
    print(f"{i+1}. {niche['name']} (Score: {niche['opportunity_score']:.2f})")

# Select the highest-scoring niche
selected_niche = max(niches, key=lambda x: x["opportunity_score"])
print(f"Selected niche: {selected_niche['name']}")

# Develop a solution
solution = team.develop_solution(selected_niche["id"])
print(f"Developed solution: {solution['name']}")

# Create a monetization strategy
monetization_strategy = team.create_monetization_strategy(solution["id"])
print(f"Created monetization strategy: {monetization_strategy['name']}")

# Create a marketing campaign
marketing_campaign = team.create_marketing_campaign(solution["id"], monetization_strategy["id"])
print(f"Created marketing campaign: {marketing_campaign['name']}")

# Collect and analyze feedback
feedback_analysis = team.collect_and_analyze_feedback(solution["id"])
print(f"Collected and analyzed feedback: {len(feedback_analysis['feedback_items'])} items")

# Iterate and improve
improved_solution = team.iterate_and_improve(solution["id"], feedback_analysis["id"])
print(f"Improved solution: {improved_solution['name']}")
```
