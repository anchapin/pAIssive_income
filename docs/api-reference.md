# API Reference

This document provides a reference for the APIs provided by the pAIssive Income Framework.

## Table of Contents

1. [Agent Team API](#agent-team-api)
2. [Niche Analysis API](#niche-analysis-api)
3. [AI Models API](#ai-models-api)
4. [Monetization API](#monetization-api)
5. [Marketing API](#marketing-api)
6. [UI API](#ui-api)
7. [Tool Templates API](#tool-templates-api)

## Agent Team API

### AgentTeam

```python
class AgentTeam(name: str, config_path: Optional[str] = None, agent_model_provider: Optional[AgentModelProvider] = None)
```

A team of specialized AI agents that collaborate on developing and monetizing niche AI tools for passive income generation.

#### Parameters

- `name` (str): Name of the agent team
- `config_path` (Optional[str]): Path to a JSON configuration file
- `agent_model_provider` (Optional[AgentModelProvider]): Provider for AI models for the agents

#### Methods

##### run_niche_analysis

```python
def run_niche_analysis(self, market_segments: List[str]) -> List[Dict[str, Any]]
```

Run niche analysis on a list of market segments.

###### Parameters

- `market_segments` (List[str]): List of market segments to analyze

###### Returns

- List[Dict[str, Any]]: List of identified niches

##### develop_solution

```python
def develop_solution(self, niche_id: str) -> Dict[str, Any]
```

Develop an AI solution for a selected niche using the developer agent.

###### Parameters

- `niche_id` (str): ID of the selected niche from the niche analysis

###### Returns

- Dict[str, Any]: Solution design specification

##### create_monetization_strategy

```python
def create_monetization_strategy(self, solution_id: str) -> Dict[str, Any]
```

Create a monetization strategy for a solution using the monetization agent.

###### Parameters

- `solution_id` (str): ID of the solution to create a monetization strategy for

###### Returns

- Dict[str, Any]: Monetization strategy

##### create_marketing_campaign

```python
def create_marketing_campaign(self, solution_id: str, strategy_id: str) -> Dict[str, Any]
```

Create a marketing campaign for a solution using the marketing agent.

###### Parameters

- `solution_id` (str): ID of the solution to create a marketing campaign for
- `strategy_id` (str): ID of the monetization strategy to use

###### Returns

- Dict[str, Any]: Marketing campaign

##### collect_and_analyze_feedback

```python
def collect_and_analyze_feedback(self, solution_id: str) -> Dict[str, Any]
```

Collect and analyze user feedback for a solution using the feedback agent.

###### Parameters

- `solution_id` (str): ID of the solution to collect feedback for

###### Returns

- Dict[str, Any]: Feedback analysis

##### iterate_and_improve

```python
def iterate_and_improve(self, solution_id: str, feedback_id: str) -> Dict[str, Any]
```

Iterate and improve a solution based on feedback.

###### Parameters

- `solution_id` (str): ID of the solution to improve
- `feedback_id` (str): ID of the feedback to use

###### Returns

- Dict[str, Any]: Improved solution

### ResearchAgent

```python
class ResearchAgent(team: AgentTeam)
```

Agent responsible for analyzing market segments and identifying profitable niches.

#### Parameters

- `team` (AgentTeam): The agent team this agent belongs to

#### Methods

##### analyze_market

```python
def analyze_market(self, segment: str) -> Dict[str, Any]
```

Analyze a market segment to identify potential niches.

###### Parameters

- `segment` (str): Market segment to analyze

###### Returns

- Dict[str, Any]: Analysis of the market segment

##### identify_problems

```python
def identify_problems(self, niche: str) -> List[Dict[str, Any]]
```

Identify problems and pain points in a specific niche.

###### Parameters

- `niche` (str): Niche to analyze

###### Returns

- List[Dict[str, Any]]: List of identified problems

##### score_opportunity

```python
def score_opportunity(self, niche: str, market_data: Dict[str, Any], problems: List[Dict[str, Any]]) -> Dict[str, Any]
```

Score a niche opportunity based on market data and identified problems.

###### Parameters

- `niche` (str): Niche to score
- `market_data` (Dict[str, Any]): Market data for the niche
- `problems` (List[Dict[str, Any]]): List of problems in the niche

###### Returns

- Dict[str, Any]: Opportunity score and analysis

### DeveloperAgent

```python
class DeveloperAgent(team: AgentTeam)
```

Agent responsible for designing and developing AI-powered solutions for specific niches.

#### Parameters

- `team` (AgentTeam): The agent team this agent belongs to

#### Methods

##### design_solution

```python
def design_solution(self, niche: Dict[str, Any]) -> Dict[str, Any]
```

Design an AI-powered software solution for a specific niche.

###### Parameters

- `niche` (Dict[str, Any]): Niche dictionary from the Research Agent

###### Returns

- Dict[str, Any]: Solution design specification

##### create_development_plan

```python
def create_development_plan(self, solution: Dict[str, Any]) -> Dict[str, Any]
```

Create a development plan for a solution.

###### Parameters

- `solution` (Dict[str, Any]): Solution design specification

###### Returns

- Dict[str, Any]: Development plan

##### implement_solution

```python
def implement_solution(self, solution: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]
```

Implement a solution based on the design and plan.

###### Parameters

- `solution` (Dict[str, Any]): Solution design specification
- `plan` (Dict[str, Any]): Development plan

###### Returns

- Dict[str, Any]: Implementation details

### MonetizationAgent

```python
class MonetizationAgent(team: AgentTeam)
```

Agent responsible for creating monetization strategies with subscription models.

#### Parameters

- `team` (AgentTeam): The agent team this agent belongs to

#### Methods

##### create_strategy

```python
def create_strategy(self, solution: Dict[str, Any]) -> Dict[str, Any]
```

Create a monetization strategy for a solution.

###### Parameters

- `solution` (Dict[str, Any]): Solution design specification

###### Returns

- Dict[str, Any]: Monetization strategy

##### calculate_pricing

```python
def calculate_pricing(self, strategy: Dict[str, Any]) -> Dict[str, Any]
```

Calculate optimal pricing for a monetization strategy.

###### Parameters

- `strategy` (Dict[str, Any]): Monetization strategy

###### Returns

- Dict[str, Any]: Pricing details

##### project_revenue

```python
def project_revenue(self, strategy: Dict[str, Any], pricing: Dict[str, Any]) -> Dict[str, Any]
```

Project revenue for a monetization strategy.

###### Parameters

- `strategy` (Dict[str, Any]): Monetization strategy
- `pricing` (Dict[str, Any]): Pricing details

###### Returns

- Dict[str, Any]: Revenue projection

### MarketingAgent

```python
class MarketingAgent(team: AgentTeam)
```

Agent responsible for developing marketing strategies and content for target users.

#### Parameters

- `team` (AgentTeam): The agent team this agent belongs to

#### Methods

##### create_personas

```python
def create_personas(self, solution: Dict[str, Any]) -> List[Dict[str, Any]]
```

Create user personas for a solution.

###### Parameters

- `solution` (Dict[str, Any]): Solution design specification

###### Returns

- List[Dict[str, Any]]: List of user personas

##### develop_strategy

```python
def develop_strategy(self, solution: Dict[str, Any], personas: List[Dict[str, Any]]) -> Dict[str, Any]
```

Develop a marketing strategy for a solution.

###### Parameters

- `solution` (Dict[str, Any]): Solution design specification
- `personas` (List[Dict[str, Any]]): List of user personas

###### Returns

- Dict[str, Any]: Marketing strategy

##### generate_content

```python
def generate_content(self, strategy: Dict[str, Any]) -> Dict[str, Any]
```

Generate marketing content based on a strategy.

###### Parameters

- `strategy` (Dict[str, Any]): Marketing strategy

###### Returns

- Dict[str, Any]: Marketing content

### FeedbackAgent

```python
class FeedbackAgent(team: AgentTeam)
```

Agent responsible for collecting and analyzing user feedback to improve solutions.

#### Parameters

- `team` (AgentTeam): The agent team this agent belongs to

#### Methods

##### collect_feedback

```python
def collect_feedback(self, solution: Dict[str, Any]) -> List[Dict[str, Any]]
```

Collect feedback from users for a solution.

###### Parameters

- `solution` (Dict[str, Any]): Solution design specification

###### Returns

- List[Dict[str, Any]]: List of feedback items

##### analyze_feedback

```python
def analyze_feedback(self, feedback: List[Dict[str, Any]]) -> Dict[str, Any]
```

Analyze feedback to identify patterns and insights.

###### Parameters

- `feedback` (List[Dict[str, Any]]): List of feedback items

###### Returns

- Dict[str, Any]: Feedback analysis

##### generate_recommendations

```python
def generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]
```

Generate improvement recommendations based on feedback analysis.

###### Parameters

- `analysis` (Dict[str, Any]): Feedback analysis

###### Returns

- List[Dict[str, Any]]: List of recommendations

## Niche Analysis API

### MarketAnalyzer

```python
class MarketAnalyzer()
```

Analyzes market segments to identify potential niches for AI tools.

#### Methods

##### analyze_segment

```python
def analyze_segment(self, segment: str) -> Dict[str, Any]
```

Analyze a market segment to identify potential niches.

Parameters:
- `segment` (str): Market segment to analyze

Returns:
- Dict[str, Any]: Analysis of the market segment

##### analyze_competition

```python
def analyze_competition(self, niche: str) -> Dict[str, Any]
```

Analyze competition in a specific niche.

Parameters:
- `niche` (str): Niche to analyze

Returns:
- Dict[str, Any]: Competition analysis for the niche

##### analyze_trends

```python
def analyze_trends(self, segment: str) -> Dict[str, Any]
```

Analyze trends in a specific market segment.

Parameters:
- `segment` (str): Market segment to analyze

Returns:
- Dict[str, Any]: Trend analysis for the segment

### ProblemIdentifier

```python
class ProblemIdentifier()
```

Identifies user problems and pain points in specific niches.

#### Methods

##### identify_problems

```python
def identify_problems(self, niche: str) -> List[Dict[str, Any]]
```

Identify problems and pain points in a specific niche.

Parameters:
- `niche` (str): Niche to analyze

Returns:
- List[Dict[str, Any]]: List of identified problems

##### analyze_problem_severity

```python
def analyze_problem_severity(self, problem: Dict[str, Any]) -> Dict[str, Any]
```

Analyze the severity of a specific problem.

Parameters:
- `problem` (Dict[str, Any]): Problem dictionary from identify_problems

Returns:
- Dict[str, Any]: Analysis of the problem severity

### OpportunityScorer

```python
class OpportunityScorer()
```

Scores niche opportunities based on various factors to identify the most promising niches.

#### Methods

##### score_opportunity

```python
def score_opportunity(self, niche: str, market_data: Dict[str, Any], problems: List[Dict[str, Any]]) -> Dict[str, Any]
```

Score a niche opportunity based on market data and identified problems.

Parameters:
- `niche` (str): Niche to score
- `market_data` (Dict[str, Any]): Market data for the niche from MarketAnalyzer
- `problems` (List[Dict[str, Any]]): List of problems in the niche from ProblemIdentifier

Returns:
- Dict[str, Any]: Opportunity score and analysis

##### compare_opportunities

```python
def compare_opportunities(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]
```

Compare multiple opportunities to identify the most promising ones.

Parameters:
- `opportunities` (List[Dict[str, Any]]): List of opportunity scores from score_opportunity

Returns:
- Dict[str, Any]: Comparison of opportunities
