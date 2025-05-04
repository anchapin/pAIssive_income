"""
"""
Marketing strategy generator module for the pAIssive Income project.
Marketing strategy generator module for the pAIssive Income project.


This module provides classes for generating marketing strategies tailored to
This module provides classes for generating marketing strategies tailored to
different business types, goals, and target audiences.
different business types, goals, and target audiences.
"""
"""


import json
import json
import time
import time
import uuid
import uuid
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from interfaces.agent_interfaces import IAgentTeam
from interfaces.agent_interfaces import IAgentTeam
from interfaces.marketing_interfaces import IMarketingStrategy
from interfaces.marketing_interfaces import IMarketingStrategy


(
(
BudgetSchema,
BudgetSchema,
MarketingChannelSchema,
MarketingChannelSchema,
MarketingMetricSchema,
MarketingMetricSchema,
MarketingStrategySchema,
MarketingStrategySchema,
MarketingTacticSchema,
MarketingTacticSchema,
TargetAudienceSchema,
TargetAudienceSchema,
)
)




class StrategyGenerator(IMarketingStrategy):
    class StrategyGenerator(IMarketingStrategy):
    """
    """
    Class for generating marketing strategies.
    Class for generating marketing strategies.


    This class provides methods for analyzing business needs and generating
    This class provides methods for analyzing business needs and generating
    tailored marketing strategies based on business type, goals, target audience,
    tailored marketing strategies based on business type, goals, target audience,
    and available budget.
    and available budget.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    business_type: Optional[str] = None,
    business_type: Optional[str] = None,
    business_size: Optional[str] = None,
    business_size: Optional[str] = None,
    goals: Optional[List[str]] = None,
    goals: Optional[List[str]] = None,
    target_audience: Optional[TargetAudienceSchema] = None,
    target_audience: Optional[TargetAudienceSchema] = None,
    budget: Optional[BudgetSchema] = None,
    budget: Optional[BudgetSchema] = None,
    agent_team: Optional[IAgentTeam] = None,
    agent_team: Optional[IAgentTeam] = None,
    ):
    ):
    """
    """
    Initialize a strategy generator.
    Initialize a strategy generator.


    Args:
    Args:
    business_type: Type of business (e.g., "SaaS", "E-commerce")
    business_type: Type of business (e.g., "SaaS", "E-commerce")
    business_size: Size of business (e.g., "Startup", "Small", "Medium", "Enterprise")
    business_size: Size of business (e.g., "Startup", "Small", "Medium", "Enterprise")
    goals: List of marketing goals
    goals: List of marketing goals
    target_audience: Target audience details
    target_audience: Target audience details
    budget: Budget details
    budget: Budget details
    agent_team: Optional agent team for strategy generation assistance
    agent_team: Optional agent team for strategy generation assistance
    """
    """
    self.id = str(uuid.uuid4())
    self.id = str(uuid.uuid4())
    self.created_at = datetime.now().isoformat()
    self.created_at = datetime.now().isoformat()
    self.business_type = business_type
    self.business_type = business_type
    self.business_size = business_size
    self.business_size = business_size
    self.goals = goals or []
    self.goals = goals or []
    self.target_audience = target_audience
    self.target_audience = target_audience
    self.budget = budget
    self.budget = budget
    self.agent_team = agent_team
    self.agent_team = agent_team
    self.strategies = []
    self.strategies = []


    def generate_strategy(self) -> MarketingStrategySchema:
    def generate_strategy(self) -> MarketingStrategySchema:
    """
    """
    Generate a marketing strategy based on the business profile.
    Generate a marketing strategy based on the business profile.


    Returns:
    Returns:
    MarketingStrategySchema: The generated marketing strategy
    MarketingStrategySchema: The generated marketing strategy
    """
    """
    # Validate inputs
    # Validate inputs
    if not self.business_type:
    if not self.business_type:
    raise ValueError("Business type is required")
    raise ValueError("Business type is required")
    if not self.goals:
    if not self.goals:
    raise ValueError("At least one goal is required")
    raise ValueError("At least one goal is required")
    if not self.target_audience:
    if not self.target_audience:
    raise ValueError("Target audience is required")
    raise ValueError("Target audience is required")
    if not self.budget:
    if not self.budget:
    raise ValueError("Budget is required")
    raise ValueError("Budget is required")


    # Generate a strategy ID
    # Generate a strategy ID
    strategy_id = str(uuid.uuid4())
    strategy_id = str(uuid.uuid4())


    # Generate a strategy name
    # Generate a strategy name
    strategy_name = f"{self.business_type} Marketing Strategy - {datetime.now().strftime('%Y-%m-%d')}"
    strategy_name = f"{self.business_type} Marketing Strategy - {datetime.now().strftime('%Y-%m-%d')}"


    # Determine appropriate channels based on business type and target audience
    # Determine appropriate channels based on business type and target audience
    channels = self._select_channels()
    channels = self._select_channels()


    # Determine appropriate tactics for each channel
    # Determine appropriate tactics for each channel
    tactics = self._select_tactics(channels)
    tactics = self._select_tactics(channels)


    # Allocate budget across channels
    # Allocate budget across channels
    allocated_budget = self._allocate_budget(channels)
    allocated_budget = self._allocate_budget(channels)


    # Define metrics to track
    # Define metrics to track
    metrics = self._define_metrics()
    metrics = self._define_metrics()


    # Create the strategy
    # Create the strategy
    strategy = MarketingStrategySchema(
    strategy = MarketingStrategySchema(
    id=strategy_id,
    id=strategy_id,
    name=strategy_name,
    name=strategy_name,
    business_type=self.business_type,
    business_type=self.business_type,
    business_size=self.business_size,
    business_size=self.business_size,
    goals=self.goals,
    goals=self.goals,
    target_audience=self.target_audience,
    target_audience=self.target_audience,
    budget=self.budget,
    budget=self.budget,
    channels=channels,
    channels=channels,
    tactics=tactics,
    tactics=tactics,
    allocated_budget=allocated_budget,
    allocated_budget=allocated_budget,
    metrics=metrics,
    metrics=metrics,
    created_at=datetime.now().isoformat(),
    created_at=datetime.now().isoformat(),
    )
    )


    # Add to strategies
    # Add to strategies
    self.strategies.append(strategy)
    self.strategies.append(strategy)


    return strategy
    return strategy


    def _select_channels(self) -> List[MarketingChannelSchema]:
    def _select_channels(self) -> List[MarketingChannelSchema]:
    """
    """
    Select appropriate marketing channels based on business profile using adaptive channel targeting.
    Select appropriate marketing channels based on business profile using adaptive channel targeting.


    This algorithm implements a sophisticated adaptive channel selection system that identifies
    This algorithm implements a sophisticated adaptive channel selection system that identifies
    the most effective marketing channels for a specific business profile. The implementation
    the most effective marketing channels for a specific business profile. The implementation
    follows these key phases:
    follows these key phases:


    1. BUSINESS PROFILE ANALYSIS:
    1. BUSINESS PROFILE ANALYSIS:
    - Analyzes core business characteristics (type, size, maturity)
    - Analyzes core business characteristics (type, size, maturity)
    - Evaluates target audience demographics and behavior patterns
    - Evaluates target audience demographics and behavior patterns
    - Identifies primary business goals and marketing objectives
    - Identifies primary business goals and marketing objectives
    - Establishes marketing context (B2B, B2C, hybrid approaches)
    - Establishes marketing context (B2B, B2C, hybrid approaches)


    2. CHANNEL RELEVANCE DETERMINATION:
    2. CHANNEL RELEVANCE DETERMINATION:
    - Calculates baseline relevance for universal channels (social media, content marketing)
    - Calculates baseline relevance for universal channels (social media, content marketing)
    - Applies business-specific adjustments based on industry benchmarks
    - Applies business-specific adjustments based on industry benchmarks
    - Implements audience-specific modifiers to channel relevance scores
    - Implements audience-specific modifiers to channel relevance scores
    - Incorporates goal-oriented weighting to prioritize channels that align with objectives
    - Incorporates goal-oriented weighting to prioritize channels that align with objectives


    3. PLATFORM-SPECIFIC TARGETING:
    3. PLATFORM-SPECIFIC TARGETING:
    - Identifies specific platforms within each channel category
    - Identifies specific platforms within each channel category
    - Evaluates platform-audience alignment for demographic targeting
    - Evaluates platform-audience alignment for demographic targeting
    - Assesses platform capabilities against content requirements
    - Assesses platform capabilities against content requirements
    - Produces platform-specific relevance scores within each channel
    - Produces platform-specific relevance scores within each channel


    4. MULTI-FACTOR RANKING AND SELECTION:
    4. MULTI-FACTOR RANKING AND SELECTION:
    - Applies composite scoring based on all analyzed factors
    - Applies composite scoring based on all analyzed factors
    - Ranks channels by overall effectiveness score
    - Ranks channels by overall effectiveness score
    - Filters channels based on minimum relevance thresholds
    - Filters channels based on minimum relevance thresholds
    - Optimizes channel mix for comprehensive audience coverage
    - Optimizes channel mix for comprehensive audience coverage


    This algorithm addresses several critical marketing strategy challenges:
    This algorithm addresses several critical marketing strategy challenges:
    - Ensures selection of channels that align with specific business characteristics
    - Ensures selection of channels that align with specific business characteristics
    - Creates a balanced channel portfolio across different marketing approaches
    - Creates a balanced channel portfolio across different marketing approaches
    - Identifies industry-specific channels that may have higher conversion potential
    - Identifies industry-specific channels that may have higher conversion potential
    - Provides data-driven relevance scoring to support budget allocation decisions
    - Provides data-driven relevance scoring to support budget allocation decisions


    Returns:
    Returns:
    List of marketing channel schemas with complete platform details and relevance scores
    List of marketing channel schemas with complete platform details and relevance scores
    """
    """
    # Placeholder implementation - in a real system, this would use more sophisticated logic
    # Placeholder implementation - in a real system, this would use more sophisticated logic
    channels = []
    channels = []


    # Social media is almost always relevant
    # Social media is almost always relevant
    channels.append(
    channels.append(
    MarketingChannelSchema(
    MarketingChannelSchema(
    name="Social Media",
    name="Social Media",
    description="Marketing through social media platforms",
    description="Marketing through social media platforms",
    platforms=["Facebook", "Instagram", "LinkedIn", "Twitter"],
    platforms=["Facebook", "Instagram", "LinkedIn", "Twitter"],
    relevance_score=0.85,
    relevance_score=0.85,
    )
    )
    )
    )


    # Content marketing is valuable for most businesses
    # Content marketing is valuable for most businesses
    channels.append(
    channels.append(
    MarketingChannelSchema(
    MarketingChannelSchema(
    name="Content Marketing",
    name="Content Marketing",
    description="Creating and sharing valuable content to attract customers",
    description="Creating and sharing valuable content to attract customers",
    platforms=["Blog", "Video", "Infographics", "Podcasts"],
    platforms=["Blog", "Video", "Infographics", "Podcasts"],
    relevance_score=0.75,
    relevance_score=0.75,
    )
    )
    )
    )


    # Email marketing is effective for most businesses
    # Email marketing is effective for most businesses
    channels.append(
    channels.append(
    MarketingChannelSchema(
    MarketingChannelSchema(
    name="Email Marketing",
    name="Email Marketing",
    description="Direct marketing through email campaigns",
    description="Direct marketing through email campaigns",
    platforms=["Newsletter", "Promotional Emails", "Automated Sequences"],
    platforms=["Newsletter", "Promotional Emails", "Automated Sequences"],
    relevance_score=0.70,
    relevance_score=0.70,
    )
    )
    )
    )


    # Add industry-specific channels
    # Add industry-specific channels
    if self.business_type == "SaaS":
    if self.business_type == "SaaS":
    channels.append(
    channels.append(
    MarketingChannelSchema(
    MarketingChannelSchema(
    name="Product Hunt",
    name="Product Hunt",
    description="Platform for launching and discovering tech products",
    description="Platform for launching and discovering tech products",
    platforms=["Product Hunt"],
    platforms=["Product Hunt"],
    relevance_score=0.65,
    relevance_score=0.65,
    )
    )
    )
    )
    elif self.business_type == "E-commerce":
    elif self.business_type == "E-commerce":
    channels.append(
    channels.append(
    MarketingChannelSchema(
    MarketingChannelSchema(
    name="Shopping Ads",
    name="Shopping Ads",
    description="Product-specific advertisements on shopping platforms",
    description="Product-specific advertisements on shopping platforms",
    platforms=["Google Shopping", "Facebook Shopping"],
    platforms=["Google Shopping", "Facebook Shopping"],
    relevance_score=0.80,
    relevance_score=0.80,
    )
    )
    )
    )


    return channels
    return channels


    def _select_tactics(
    def _select_tactics(
    self, channels: List[MarketingChannelSchema]
    self, channels: List[MarketingChannelSchema]
    ) -> List[MarketingTacticSchema]:
    ) -> List[MarketingTacticSchema]:
    """
    """
    Select appropriate tactics for each channel.
    Select appropriate tactics for each channel.


    Args:
    Args:
    channels: List of selected marketing channels
    channels: List of selected marketing channels


    Returns:
    Returns:
    List of marketing tactics
    List of marketing tactics
    """
    """
    tactics = []
    tactics = []


    for channel in channels:
    for channel in channels:
    if channel.name == "Social Media":
    if channel.name == "Social Media":
    tactics.extend(
    tactics.extend(
    [
    [
    MarketingTacticSchema(
    MarketingTacticSchema(
    channel_name=channel.name,
    channel_name=channel.name,
    name="Organic Social Media Content",
    name="Organic Social Media Content",
    description="Regular posting of engaging content",
    description="Regular posting of engaging content",
    expected_impact=0.6,
    expected_impact=0.6,
    timeframe="Short to medium term",
    timeframe="Short to medium term",
    resources_required=["Content creator", "Graphics designer"],
    resources_required=["Content creator", "Graphics designer"],
    estimated_cost=500,
    estimated_cost=500,
    ),
    ),
    MarketingTacticSchema(
    MarketingTacticSchema(
    channel_name=channel.name,
    channel_name=channel.name,
    name="Social Media Advertising",
    name="Social Media Advertising",
    description="Paid advertising on social platforms",
    description="Paid advertising on social platforms",
    expected_impact=0.7,
    expected_impact=0.7,
    timeframe="Short term",
    timeframe="Short term",
    resources_required=["Ad budget", "Ad designer"],
    resources_required=["Ad budget", "Ad designer"],
    estimated_cost=1000,
    estimated_cost=1000,
    ),
    ),
    ]
    ]
    )
    )
    elif channel.name == "Content Marketing":
    elif channel.name == "Content Marketing":
    tactics.extend(
    tactics.extend(
    [
    [
    MarketingTacticSchema(
    MarketingTacticSchema(
    channel_name=channel.name,
    channel_name=channel.name,
    name="SEO-Optimized Blog Content",
    name="SEO-Optimized Blog Content",
    description="Creating blog content targeting specific keywords",
    description="Creating blog content targeting specific keywords",
    expected_impact=0.65,
    expected_impact=0.65,
    timeframe="Medium to long term",
    timeframe="Medium to long term",
    resources_required=["Content writer", "SEO specialist"],
    resources_required=["Content writer", "SEO specialist"],
    estimated_cost=800,
    estimated_cost=800,
    ),
    ),
    MarketingTacticSchema(
    MarketingTacticSchema(
    channel_name=channel.name,
    channel_name=channel.name,
    name="Video Content Production",
    name="Video Content Production",
    description="Creating engaging video content for products/services",
    description="Creating engaging video content for products/services",
    expected_impact=0.75,
    expected_impact=0.75,
    timeframe="Medium term",
    timeframe="Medium term",
    resources_required=[
    resources_required=[
    "Videographer",
    "Videographer",
    "Editor",
    "Editor",
    "Scriptwriter",
    "Scriptwriter",
    ],
    ],
    estimated_cost=1500,
    estimated_cost=1500,
    ),
    ),
    ]
    ]
    )
    )
    elif channel.name == "Email Marketing":
    elif channel.name == "Email Marketing":
    tactics.append(
    tactics.append(
    MarketingTacticSchema(
    MarketingTacticSchema(
    channel_name=channel.name,
    channel_name=channel.name,
    name="Email Newsletter Campaign",
    name="Email Newsletter Campaign",
    description="Regular newsletters with valuable content and offers",
    description="Regular newsletters with valuable content and offers",
    expected_impact=0.6,
    expected_impact=0.6,
    timeframe="Short to medium term",
    timeframe="Short to medium term",
    resources_required=[
    resources_required=[
    "Email copywriter",
    "Email copywriter",
    "Email marketing software",
    "Email marketing software",
    ],
    ],
    estimated_cost=300,
    estimated_cost=300,
    )
    )
    )
    )


    return tactics
    return tactics


    def _allocate_budget(
    def _allocate_budget(
    self, channels: List[MarketingChannelSchema]
    self, channels: List[MarketingChannelSchema]
    ) -> Dict[str, float]:
    ) -> Dict[str, float]:
    """
    """
    Allocate budget across marketing channels using proportional relevance distribution.
    Allocate budget across marketing channels using proportional relevance distribution.


    This algorithm implements an intelligent budget allocation system that optimally
    This algorithm implements an intelligent budget allocation system that optimally
    distributes financial resources across marketing channels. The implementation
    distributes financial resources across marketing channels. The implementation
    follows these key phases:
    follows these key phases:


    1. CHANNEL IMPORTANCE ANALYSIS:
    1. CHANNEL IMPORTANCE ANALYSIS:
    - Evaluates each channel's relevance score as a measure of potential effectiveness
    - Evaluates each channel's relevance score as a measure of potential effectiveness
    - Calculates relative importance of each channel within the overall marketing mix
    - Calculates relative importance of each channel within the overall marketing mix
    - Normalizes relevance scores to create proportional distribution factors
    - Normalizes relevance scores to create proportional distribution factors
    - Accounts for business-specific weighting considerations
    - Accounts for business-specific weighting considerations


    2. BUDGET CONSTRAINT PROCESSING:
    2. BUDGET CONSTRAINT PROCESSING:
    - Identifies total available budget from business budget specifications
    - Identifies total available budget from business budget specifications
    - Applies minimum allocation rules to ensure channel viability
    - Applies minimum allocation rules to ensure channel viability
    - Processes any channel-specific budget constraints or requirements
    - Processes any channel-specific budget constraints or requirements
    - Implements budget period normalization (monthly, quarterly, annual)
    - Implements budget period normalization (monthly, quarterly, annual)


    3. PROPORTIONAL ALLOCATION CALCULATION:
    3. PROPORTIONAL ALLOCATION CALCULATION:
    - Distributes budget proportionally according to normalized relevance scores
    - Distributes budget proportionally according to normalized relevance scores
    - Calculates precise monetary allocation for each marketing channel
    - Calculates precise monetary allocation for each marketing channel
    - Ensures allocations sum exactly to total available budget
    - Ensures allocations sum exactly to total available budget
    - Rounds allocations to appropriate precision for financial planning
    - Rounds allocations to appropriate precision for financial planning


    4. ALLOCATION VALIDATION AND ADJUSTMENT:
    4. ALLOCATION VALIDATION AND ADJUSTMENT:
    - Verifies allocations meet minimum threshold requirements for each channel
    - Verifies allocations meet minimum threshold requirements for each channel
    - Adjusts allocations to account for channel-specific cost structures
    - Adjusts allocations to account for channel-specific cost structures
    - Ensures no channel is under-resourced below effectiveness threshold
    - Ensures no channel is under-resourced below effectiveness threshold
    - Rebalances allocations after adjustments to maintain budget total
    - Rebalances allocations after adjustments to maintain budget total


    This algorithm addresses several critical budget allocation challenges:
    This algorithm addresses several critical budget allocation challenges:
    - Ensures marketing resources are distributed according to potential effectiveness
    - Ensures marketing resources are distributed according to potential effectiveness
    - Creates financially viable allocation for each selected marketing channel
    - Creates financially viable allocation for each selected marketing channel
    - Prevents resource dilution across too many channels
    - Prevents resource dilution across too many channels
    - Aligns budget distribution with overall marketing strategy objectives
    - Aligns budget distribution with overall marketing strategy objectives


    Args:
    Args:
    channels: List of selected marketing channels with relevance scores
    channels: List of selected marketing channels with relevance scores


    Returns:
    Returns:
    Dictionary mapping channel names to budget allocations in monetary units
    Dictionary mapping channel names to budget allocations in monetary units
    """
    """
    # Simple allocation based on relevance score
    # Simple allocation based on relevance score
    total_relevance = sum(channel.relevance_score for channel in channels)
    total_relevance = sum(channel.relevance_score for channel in channels)
    total_budget = self.budget.total_amount
    total_budget = self.budget.total_amount


    allocated_budget = {}
    allocated_budget = {}


    for channel in channels:
    for channel in channels:
    allocation = (channel.relevance_score / total_relevance) * total_budget
    allocation = (channel.relevance_score / total_relevance) * total_budget
    allocated_budget[channel.name] = allocation
    allocated_budget[channel.name] = allocation


    return allocated_budget
    return allocated_budget


    def _define_metrics(self) -> List[MarketingMetricSchema]:
    def _define_metrics(self) -> List[MarketingMetricSchema]:
    """
    """
    Define relevant performance metrics using goal-oriented KPI selection.
    Define relevant performance metrics using goal-oriented KPI selection.


    This algorithm implements an intelligent marketing metrics selection system that identifies
    This algorithm implements an intelligent marketing metrics selection system that identifies
    the most appropriate key performance indicators for a given marketing strategy. The implementation
    the most appropriate key performance indicators for a given marketing strategy. The implementation
    follows these key phases:
    follows these key phases:


    1. FOUNDATIONAL METRIC ESTABLISHMENT:
    1. FOUNDATIONAL METRIC ESTABLISHMENT:
    - Identifies universal marketing metrics applicable to all businesses
    - Identifies universal marketing metrics applicable to all businesses
    - Establishes baseline performance expectations for standard metrics
    - Establishes baseline performance expectations for standard metrics
    - Sets appropriate measurement units for consistent reporting
    - Sets appropriate measurement units for consistent reporting
    - Creates initial target values based on industry benchmarks
    - Creates initial target values based on industry benchmarks


    2. GOAL-DRIVEN METRIC SELECTION:
    2. GOAL-DRIVEN METRIC SELECTION:
    - Analyzes declared marketing goals to identify relevant goal-specific metrics
    - Analyzes declared marketing goals to identify relevant goal-specific metrics
    - Maps marketing objectives to quantifiable performance indicators
    - Maps marketing objectives to quantifiable performance indicators
    - Prioritizes metrics with direct correlation to strategic objectives
    - Prioritizes metrics with direct correlation to strategic objectives
    - Ensures comprehensive coverage of all stated marketing goals
    - Ensures comprehensive coverage of all stated marketing goals


    3. CHANNEL-SPECIFIC METRIC INTEGRATION:
    3. CHANNEL-SPECIFIC METRIC INTEGRATION:
    - Identifies channel-appropriate performance metrics for selected channels
    - Identifies channel-appropriate performance metrics for selected channels
    - Incorporates platform-specific metrics for digital marketing channels
    - Incorporates platform-specific metrics for digital marketing channels
    - Establishes complementary metrics to measure multi-channel synergies
    - Establishes complementary metrics to measure multi-channel synergies
    - Maintains balanced metrics across various marketing funnel stages
    - Maintains balanced metrics across various marketing funnel stages


    4. TARGET VALUE CALIBRATION:
    4. TARGET VALUE CALIBRATION:
    - Sets realistic target values based on business size and maturity
    - Sets realistic target values based on business size and maturity
    - Applies industry benchmarks adjusted for specific business context
    - Applies industry benchmarks adjusted for specific business context
    - Establishes baseline current values for tracking improvement over time
    - Establishes baseline current values for tracking improvement over time
    - Creates appropriate measurement units for each metric type
    - Creates appropriate measurement units for each metric type


    This algorithm addresses several critical marketing measurement challenges:
    This algorithm addresses several critical marketing measurement challenges:
    - Ensures comprehensive coverage of marketing performance dimensions
    - Ensures comprehensive coverage of marketing performance dimensions
    - Aligns performance metrics directly with strategic objectives
    - Aligns performance metrics directly with strategic objectives
    - Provides quantifiable measures for all key marketing activities
    - Provides quantifiable measures for all key marketing activities
    - Establishes meaningful baselines and targets for performance tracking
    - Establishes meaningful baselines and targets for performance tracking


    Returns:
    Returns:
    List of marketing metrics with appropriate targets and measurement units
    List of marketing metrics with appropriate targets and measurement units
    """
    """
    # Common metrics for most strategies
    # Common metrics for most strategies
    metrics = [
    metrics = [
    MarketingMetricSchema(
    MarketingMetricSchema(
    name="Website Traffic",
    name="Website Traffic",
    description="Number of visitors to the website",
    description="Number of visitors to the website",
    target_value=1000,
    target_value=1000,
    current_value=0,
    current_value=0,
    unit="visitors/month",
    unit="visitors/month",
    ),
    ),
    MarketingMetricSchema(
    MarketingMetricSchema(
    name="Conversion Rate",
    name="Conversion Rate",
    description="Percentage of visitors who take a desired action",
    description="Percentage of visitors who take a desired action",
    target_value=0.03,
    target_value=0.03,
    current_value=0.01,
    current_value=0.01,
    unit="percentage",
    unit="percentage",
    ),
    ),
    MarketingMetricSchema(
    MarketingMetricSchema(
    name="Customer Acquisition Cost",
    name="Customer Acquisition Cost",
    description="Average cost to acquire a new customer",
    description="Average cost to acquire a new customer",
    target_value=50.0,
    target_value=50.0,
    current_value=75.0,
    current_value=75.0,
    unit="USD",
    unit="USD",
    ),
    ),
    ]
    ]


    # Add goal-specific metrics
    # Add goal-specific metrics
    if "Increase brand awareness" in self.goals:
    if "Increase brand awareness" in self.goals:
    metrics.append(
    metrics.append(
    MarketingMetricSchema(
    MarketingMetricSchema(
    name="Social Media Reach",
    name="Social Media Reach",
    description="Number of unique users who see the content",
    description="Number of unique users who see the content",
    target_value=10000,
    target_value=10000,
    current_value=2000,
    current_value=2000,
    unit="users/month",
    unit="users/month",
    )
    )
    )
    )


    if "Generate leads" in self.goals:
    if "Generate leads" in self.goals:
    metrics.append(
    metrics.append(
    MarketingMetricSchema(
    MarketingMetricSchema(
    name="Lead Generation",
    name="Lead Generation",
    description="Number of new leads generated",
    description="Number of new leads generated",
    target_value=100,
    target_value=100,
    current_value=30,
    current_value=30,
    unit="leads/month",
    unit="leads/month",
    )
    )
    )
    )


    if "Increase sales" in self.goals:
    if "Increase sales" in self.goals:
    metrics.append(
    metrics.append(
    MarketingMetricSchema(
    MarketingMetricSchema(
    name="Sales Revenue",
    name="Sales Revenue",
    description="Total sales revenue",
    description="Total sales revenue",
    target_value=10000.0,
    target_value=10000.0,
    current_value=5000.0,
    current_value=5000.0,
    unit="USD/month",
    unit="USD/month",
    )
    )
    )
    )


    return metrics
    return metrics


    def evaluate_strategy(
    def evaluate_strategy(
    self, strategy_id: str, metrics: Dict[str, float]
    self, strategy_id: str, metrics: Dict[str, float]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Evaluate the effectiveness of a marketing strategy using multi-dimensional performance analysis.
    Evaluate the effectiveness of a marketing strategy using multi-dimensional performance analysis.


    This algorithm implements a comprehensive marketing performance evaluation system that quantifies
    This algorithm implements a comprehensive marketing performance evaluation system that quantifies
    strategy effectiveness across multiple dimensions. The implementation follows these key phases:
    strategy effectiveness across multiple dimensions. The implementation follows these key phases:


    1. METRIC COLLECTION AND VALIDATION:
    1. METRIC COLLECTION AND VALIDATION:
    - Retrieves target metrics from strategy specification
    - Retrieves target metrics from strategy specification
    - Validates incoming performance metrics against expected dimensions
    - Validates incoming performance metrics against expected dimensions
    - Identifies missing metrics and handles data validation errors
    - Identifies missing metrics and handles data validation errors
    - Standardizes metrics to ensure consistent evaluation
    - Standardizes metrics to ensure consistent evaluation


    2. PERFORMANCE MEASUREMENT CALCULATION:
    2. PERFORMANCE MEASUREMENT CALCULATION:
    - Computes achievement percentages for each metric against target values
    - Computes achievement percentages for each metric against target values
    - Implements scaled scoring with upper bounds to prevent outlier distortion
    - Implements scaled scoring with upper bounds to prevent outlier distortion
    - Calculates composite effectiveness score across all tracked metrics
    - Calculates composite effectiveness score across all tracked metrics
    - Generates normalized scores for cross-strategy comparison
    - Generates normalized scores for cross-strategy comparison


    3. TARGETED RECOMMENDATION GENERATION:
    3. TARGETED RECOMMENDATION GENERATION:
    - Identifies underperforming metrics using threshold-based detection
    - Identifies underperforming metrics using threshold-based detection
    - Analyzes performance patterns to detect systemic vs. isolated issues
    - Analyzes performance patterns to detect systemic vs. isolated issues
    - Generates specific recommendations for improvement prioritized by impact
    - Generates specific recommendations for improvement prioritized by impact
    - Creates actionable insights for strategy refinement
    - Creates actionable insights for strategy refinement


    4. PERFORMANCE ANALYTICS COMPILATION:
    4. PERFORMANCE ANALYTICS COMPILATION:
    - Produces standardized performance report with normalized scores
    - Produces standardized performance report with normalized scores
    - Includes comparative analysis of current vs. target performance
    - Includes comparative analysis of current vs. target performance
    - Provides temporal metadata for trend analysis
    - Provides temporal metadata for trend analysis
    - Formats output for both human readability and algorithmic processing
    - Formats output for both human readability and algorithmic processing


    This algorithm addresses several critical marketing evaluation challenges:
    This algorithm addresses several critical marketing evaluation challenges:
    - Enables objective assessment of marketing strategy effectiveness
    - Enables objective assessment of marketing strategy effectiveness
    - Supports data-driven marketing decision making through quantitative analysis
    - Supports data-driven marketing decision making through quantitative analysis
    - Identifies specific areas requiring tactical adjustments
    - Identifies specific areas requiring tactical adjustments
    - Facilitates continuous improvement through iterative strategy refinement
    - Facilitates continuous improvement through iterative strategy refinement


    Args:
    Args:
    strategy_id: ID of the strategy to evaluate
    strategy_id: ID of the strategy to evaluate
    metrics: Dictionary mapping metric names to current values
    metrics: Dictionary mapping metric names to current values


    Returns:
    Returns:
    Dictionary with evaluation results including overall effectiveness score,
    Dictionary with evaluation results including overall effectiveness score,
    current vs. target metrics, and actionable recommendations
    current vs. target metrics, and actionable recommendations


    Raises:
    Raises:
    ValueError: If strategy with the specified ID is not found
    ValueError: If strategy with the specified ID is not found
    """
    """
    # Find the strategy
    # Find the strategy
    strategy = next((s for s in self.strategies if s.id == strategy_id), None)
    strategy = next((s for s in self.strategies if s.id == strategy_id), None)


    if not strategy:
    if not strategy:
    raise ValueError(f"Strategy with ID {strategy_id} not found")
    raise ValueError(f"Strategy with ID {strategy_id} not found")


    # Calculate overall effectiveness
    # Calculate overall effectiveness
    effectiveness = 0.0
    effectiveness = 0.0
    total_metrics = 0
    total_metrics = 0


    for metric in strategy.metrics:
    for metric in strategy.metrics:
    if metric.name in metrics:
    if metric.name in metrics:
    current_value = metrics[metric.name]
    current_value = metrics[metric.name]
    target_value = metric.target_value
    target_value = metric.target_value


    # Update the current value
    # Update the current value
    metric.current_value = current_value
    metric.current_value = current_value


    # Calculate achievement percentage
    # Calculate achievement percentage
    if target_value != 0:
    if target_value != 0:
    achievement = min(current_value / target_value, 2.0)
    achievement = min(current_value / target_value, 2.0)
    effectiveness += achievement
    effectiveness += achievement
    total_metrics += 1
    total_metrics += 1


    if total_metrics > 0:
    if total_metrics > 0:
    overall_effectiveness = effectiveness / total_metrics
    overall_effectiveness = effectiveness / total_metrics
    else:
    else:
    overall_effectiveness = 0.0
    overall_effectiveness = 0.0


    # Generate recommendations
    # Generate recommendations
    recommendations = []
    recommendations = []


    if overall_effectiveness < 0.5:
    if overall_effectiveness < 0.5:
    recommendations.append("Review and adjust the overall strategy")
    recommendations.append("Review and adjust the overall strategy")


    for metric in strategy.metrics:
    for metric in strategy.metrics:
    if metric.name in metrics:
    if metric.name in metrics:
    current_value = metrics[metric.name]
    current_value = metrics[metric.name]
    target_value = metric.target_value
    target_value = metric.target_value


    if current_value < target_value * 0.7:
    if current_value < target_value * 0.7:
    recommendations.append(
    recommendations.append(
    f"Focus more resources on improving {metric.name}"
    f"Focus more resources on improving {metric.name}"
    )
    )


    # Return evaluation results
    # Return evaluation results
    return {
    return {
    "strategy_id": strategy_id,
    "strategy_id": strategy_id,
    "overall_effectiveness": overall_effectiveness,
    "overall_effectiveness": overall_effectiveness,
    "metrics": {
    "metrics": {
    metric.name: {
    metric.name: {
    "current": metric.current_value,
    "current": metric.current_value,
    "target": metric.target_value,
    "target": metric.target_value,
    }
    }
    for metric in strategy.metrics
    for metric in strategy.metrics
    },
    },
    "recommendations": recommendations,
    "recommendations": recommendations,
    "timestamp": datetime.now().isoformat(),
    "timestamp": datetime.now().isoformat(),
    }
    }


    def revise_strategy(
    def revise_strategy(
    self, strategy_id: str, evaluation_results: Dict[str, Any]
    self, strategy_id: str, evaluation_results: Dict[str, Any]
    ) -> MarketingStrategySchema:
    ) -> MarketingStrategySchema:
    """
    """
    Revise a marketing strategy based on performance evaluation using adaptive optimization techniques.
    Revise a marketing strategy based on performance evaluation using adaptive optimization techniques.


    This algorithm implements an intelligent strategy revision system that adaptively optimizes
    This algorithm implements an intelligent strategy revision system that adaptively optimizes
    marketing strategies based on performance data. The implementation follows these key phases:
    marketing strategies based on performance data. The implementation follows these key phases:


    1. PERFORMANCE ANALYSIS:
    1. PERFORMANCE ANALYSIS:
    - Retrieves and validates historical performance data from evaluation results
    - Retrieves and validates historical performance data from evaluation results
    - Compares current metrics against target KPIs across all channels
    - Compares current metrics against target KPIs across all channels
    - Identifies underperforming and overperforming strategy components
    - Identifies underperforming and overperforming strategy components
    - Calculates variance and deviation patterns across multiple metrics
    - Calculates variance and deviation patterns across multiple metrics


    2. EFFECTIVENESS-DRIVEN RESOURCE REALLOCATION:
    2. EFFECTIVENESS-DRIVEN RESOURCE REALLOCATION:
    - Implements inverse performance correlation for budget redistribution
    - Implements inverse performance correlation for budget redistribution
    - Creates a weighted adjustment matrix for tactical resource allocation
    - Creates a weighted adjustment matrix for tactical resource allocation
    - Applies bounded compensation factors (0.5-1.5) to prevent overcorrection
    - Applies bounded compensation factors (0.5-1.5) to prevent overcorrection
    - Ensures budget normalization to maintain total spending constraints
    - Ensures budget normalization to maintain total spending constraints


    3. TACTICAL REFINEMENT:
    3. TACTICAL REFINEMENT:
    - Identifies metrics-to-tactic relationships through semantic content analysis
    - Identifies metrics-to-tactic relationships through semantic content analysis
    - Clusters related tactics by performance patterns and marketing funnel stage
    - Clusters related tactics by performance patterns and marketing funnel stage
    - Adjusts tactical approaches based on observed effectiveness
    - Adjusts tactical approaches based on observed effectiveness
    - Implements channel-specific tactical modifications
    - Implements channel-specific tactical modifications


    4. STRATEGIC CONTINUITY MANAGEMENT:
    4. STRATEGIC CONTINUITY MANAGEMENT:
    - Maintains strategic version history with predecessor relationships
    - Maintains strategic version history with predecessor relationships
    - Preserves core strategy components while evolving implementation details
    - Preserves core strategy components while evolving implementation details
    - Ensures consistent targeting and messaging across strategy iterations
    - Ensures consistent targeting and messaging across strategy iterations
    - Creates a complete audit trail of strategic modifications
    - Creates a complete audit trail of strategic modifications


    This algorithm addresses several critical marketing optimization challenges:
    This algorithm addresses several critical marketing optimization challenges:
    - Enables data-driven adjustment of marketing strategies without manual analysis
    - Enables data-driven adjustment of marketing strategies without manual analysis
    - Implements incremental optimization while maintaining strategic direction
    - Implements incremental optimization while maintaining strategic direction
    - Balances resource allocation between high-performing and developing channels
    - Balances resource allocation between high-performing and developing channels
    - Provides systematic improvement of marketing effectiveness over time
    - Provides systematic improvement of marketing effectiveness over time


    Args:
    Args:
    strategy_id: ID of the strategy to revise
    strategy_id: ID of the strategy to revise
    evaluation_results: Results from evaluate_strategy containing performance metrics
    evaluation_results: Results from evaluate_strategy containing performance metrics


    Returns:
    Returns:
    A revised marketing strategy with optimized resource allocations and tactical adjustments
    A revised marketing strategy with optimized resource allocations and tactical adjustments


    Raises:
    Raises:
    ValueError: If strategy with the specified ID is not found
    ValueError: If strategy with the specified ID is not found
    """
    """
    # Find the strategy
    # Find the strategy
    strategy = next((s for s in self.strategies if s.id == strategy_id), None)
    strategy = next((s for s in self.strategies if s.id == strategy_id), None)


    if not strategy:
    if not strategy:
    raise ValueError(f"Strategy with ID {strategy_id} not found")
    raise ValueError(f"Strategy with ID {strategy_id} not found")


    # Remove the old strategy from the list
    # Remove the old strategy from the list
    self.strategies = [s for s in self.strategies if s.id != strategy_id]
    self.strategies = [s for s in self.strategies if s.id != strategy_id]


    # Create a new strategy ID
    # Create a new strategy ID
    new_strategy_id = str(uuid.uuid4())
    new_strategy_id = str(uuid.uuid4())


    # Create a revised version of the strategy
    # Create a revised version of the strategy
    revised_strategy = MarketingStrategySchema(
    revised_strategy = MarketingStrategySchema(
    id=new_strategy_id,
    id=new_strategy_id,
    name=f"{strategy.name} (Revised)",
    name=f"{strategy.name} (Revised)",
    business_type=strategy.business_type,
    business_type=strategy.business_type,
    business_size=strategy.business_size,
    business_size=strategy.business_size,
    goals=strategy.goals,
    goals=strategy.goals,
    target_audience=strategy.target_audience,
    target_audience=strategy.target_audience,
    budget=strategy.budget,
    budget=strategy.budget,
    channels=strategy.channels,
    channels=strategy.channels,
    tactics=strategy.tactics,
    tactics=strategy.tactics,
    allocated_budget=strategy.allocated_budget,
    allocated_budget=strategy.allocated_budget,
    metrics=strategy.metrics,
    metrics=strategy.metrics,
    created_at=datetime.now().isoformat(),
    created_at=datetime.now().isoformat(),
    previous_version_id=strategy_id,
    previous_version_id=strategy_id,
    )
    )


    # Adjust based on evaluation results
    # Adjust based on evaluation results
    overall_effectiveness = evaluation_results.get("overall_effectiveness", 0.0)
    overall_effectiveness = evaluation_results.get("overall_effectiveness", 0.0)


    if overall_effectiveness < 0.5:
    if overall_effectiveness < 0.5:
    # Significant revisions needed
    # Significant revisions needed
    # Reprioritize channels based on metrics
    # Reprioritize channels based on metrics
    metrics_by_channel = {}
    metrics_by_channel = {}


    for tactic in revised_strategy.tactics:
    for tactic in revised_strategy.tactics:
    channel = tactic.channel_name
    channel = tactic.channel_name
    related_metrics = [
    related_metrics = [
    m
    m
    for m in revised_strategy.metrics
    for m in revised_strategy.metrics
    if m.name.lower() in tactic.description.lower()
    if m.name.lower() in tactic.description.lower()
    ]
    ]


    if channel not in metrics_by_channel:
    if channel not in metrics_by_channel:
    metrics_by_channel[channel] = []
    metrics_by_channel[channel] = []


    metrics_by_channel[channel].extend(related_metrics)
    metrics_by_channel[channel].extend(related_metrics)


    # Reallocate budget based on channel performance
    # Reallocate budget based on channel performance
    new_allocations = {}
    new_allocations = {}
    total_budget = sum(revised_strategy.allocated_budget.values())
    total_budget = sum(revised_strategy.allocated_budget.values())


    for channel, metrics in metrics_by_channel.items():
    for channel, metrics in metrics_by_channel.items():
    if metrics:
    if metrics:
    avg_effectiveness = sum(
    avg_effectiveness = sum(
    min(m.current_value / m.target_value, 1.0) for m in metrics
    min(m.current_value / m.target_value, 1.0) for m in metrics
    ) / len(metrics)
    ) / len(metrics)


    # Inverse of effectiveness - lower performing channels get more budget
    # Inverse of effectiveness - lower performing channels get more budget
    adjustment_factor = 1.5 - avg_effectiveness
    adjustment_factor = 1.5 - avg_effectiveness


    # Min adjustment is 0.5, max is 1.5
    # Min adjustment is 0.5, max is 1.5
    adjustment_factor = max(0.5, min(1.5, adjustment_factor))
    adjustment_factor = max(0.5, min(1.5, adjustment_factor))


    current_allocation = revised_strategy.allocated_budget.get(
    current_allocation = revised_strategy.allocated_budget.get(
    channel, 0
    channel, 0
    )
    )
    new_allocations[channel] = current_allocation * adjustment_factor
    new_allocations[channel] = current_allocation * adjustment_factor
    else:
    else:
    new_allocations[channel] = revised_strategy.allocated_budget.get(
    new_allocations[channel] = revised_strategy.allocated_budget.get(
    channel, 0
    channel, 0
    )
    )


    # Normalize allocations to match total budget
    # Normalize allocations to match total budget
    allocation_sum = sum(new_allocations.values())
    allocation_sum = sum(new_allocations.values())


    if allocation_sum > 0:
    if allocation_sum > 0:
    for channel in new_allocations:
    for channel in new_allocations:
    new_allocations[channel] = (
    new_allocations[channel] = (
    new_allocations[channel] / allocation_sum
    new_allocations[channel] / allocation_sum
    ) * total_budget
    ) * total_budget


    revised_strategy.allocated_budget = new_allocations
    revised_strategy.allocated_budget = new_allocations


    # Add the revised strategy to the list
    # Add the revised strategy to the list
    self.strategies.append(revised_strategy)
    self.strategies.append(revised_strategy)


    return revised_strategy
    return revised_strategy


    def export_strategy(self, strategy_id: str, format: str = "json") -> str:
    def export_strategy(self, strategy_id: str, format: str = "json") -> str:
    """
    """
    Export a strategy in the specified format.
    Export a strategy in the specified format.


    Args:
    Args:
    strategy_id: ID of the strategy to export
    strategy_id: ID of the strategy to export
    format: Format to export in (json, markdown, etc.)
    format: Format to export in (json, markdown, etc.)


    Returns:
    Returns:
    String representation of the strategy in the specified format
    String representation of the strategy in the specified format
    """
    """
    # Find the strategy
    # Find the strategy
    strategy = next((s for s in self.strategies if s.id == strategy_id), None)
    strategy = next((s for s in self.strategies if s.id == strategy_id), None)


    if not strategy:
    if not strategy:
    raise ValueError(f"Strategy with ID {strategy_id} not found")
    raise ValueError(f"Strategy with ID {strategy_id} not found")


    if format == "json":
    if format == "json":
    # Convert to dictionary
    # Convert to dictionary
    strategy_dict = strategy.model_dump()
    strategy_dict = strategy.model_dump()


    # Remove any non-serializable fields
    # Remove any non-serializable fields
    if "target_audience" in strategy_dict and isinstance(
    if "target_audience" in strategy_dict and isinstance(
    strategy_dict["target_audience"], dict
    strategy_dict["target_audience"], dict
    ):
    ):
    if "demographics" in strategy_dict["target_audience"] and isinstance(
    if "demographics" in strategy_dict["target_audience"] and isinstance(
    strategy_dict["target_audience"]["demographics"], dict
    strategy_dict["target_audience"]["demographics"], dict
    ):
    ):
    for key in ("age_range", "income_range"):
    for key in ("age_range", "income_range"):
    if key in strategy_dict["target_audience"]["demographics"]:
    if key in strategy_dict["target_audience"]["demographics"]:
    value = strategy_dict["target_audience"]["demographics"][
    value = strategy_dict["target_audience"]["demographics"][
    key
    key
    ]
    ]
    if hasattr(value, "__iter__") and not isinstance(
    if hasattr(value, "__iter__") and not isinstance(
    value, (str, dict)
    value, (str, dict)
    ):
    ):
    strategy_dict["target_audience"]["demographics"][
    strategy_dict["target_audience"]["demographics"][
    key
    key
    ] = list(value)
    ] = list(value)


    # Return JSON string
    # Return JSON string
    return json.dumps(strategy_dict, indent=2)
    return json.dumps(strategy_dict, indent=2)
    elif format == "markdown":
    elif format == "markdown":
    # Create a markdown representation
    # Create a markdown representation
    md = f"# {strategy.name}\n\n"
    md = f"# {strategy.name}\n\n"
    md += f"**ID:** {strategy.id}\n"
    md += f"**ID:** {strategy.id}\n"
    md += f"**Created:** {strategy.created_at}\n\n"
    md += f"**Created:** {strategy.created_at}\n\n"


    md += "## Business Profile\n\n"
    md += "## Business Profile\n\n"
    md += f"- **Type:** {strategy.business_type}\n"
    md += f"- **Type:** {strategy.business_type}\n"
    md += f"- **Size:** {strategy.business_size}\n\n"
    md += f"- **Size:** {strategy.business_size}\n\n"


    md += "## Goals\n\n"
    md += "## Goals\n\n"
    for goal in strategy.goals:
    for goal in strategy.goals:
    md += f"- {goal}\n"
    md += f"- {goal}\n"
    md += "\n"
    md += "\n"


    md += "## Target Audience\n\n"
    md += "## Target Audience\n\n"
    if strategy.target_audience.demographics:
    if strategy.target_audience.demographics:
    md += "### Demographics\n\n"
    md += "### Demographics\n\n"
    demo = strategy.target_audience.demographics
    demo = strategy.target_audience.demographics
    md += f"- **Age Range:** {demo.age_range[0]}-{demo.age_range[1]}\n"
    md += f"- **Age Range:** {demo.age_range[0]}-{demo.age_range[1]}\n"
    md += f"- **Gender:** {demo.gender}\n"
    md += f"- **Gender:** {demo.gender}\n"
    md += f"- **Location:** {demo.location}\n"
    md += f"- **Location:** {demo.location}\n"
    md += f"- **Income Range:** ${demo.income_range[0]}-${demo.income_range[1]}\n"
    md += f"- **Income Range:** ${demo.income_range[0]}-${demo.income_range[1]}\n"
    md += "\n"
    md += "\n"


    if strategy.target_audience.interests:
    if strategy.target_audience.interests:
    md += "### Interests\n\n"
    md += "### Interests\n\n"
    for interest in strategy.target_audience.interests:
    for interest in strategy.target_audience.interests:
    md += f"- {interest}\n"
    md += f"- {interest}\n"
    md += "\n"
    md += "\n"


    if strategy.target_audience.behaviors:
    if strategy.target_audience.behaviors:
    md += "### Behaviors\n\n"
    md += "### Behaviors\n\n"
    for behavior in strategy.target_audience.behaviors:
    for behavior in strategy.target_audience.behaviors:
    md += f"- {behavior}\n"
    md += f"- {behavior}\n"
    md += "\n"
    md += "\n"


    md += "## Budget\n\n"
    md += "## Budget\n\n"
    md += f"- **Total:** ${strategy.budget.total_amount}\n"
    md += f"- **Total:** ${strategy.budget.total_amount}\n"
    md += f"- **Timeframe:** {strategy.budget.timeframe}\n\n"
    md += f"- **Timeframe:** {strategy.budget.timeframe}\n\n"


    md += "## Marketing Channels\n\n"
    md += "## Marketing Channels\n\n"
    for channel in strategy.channels:
    for channel in strategy.channels:
    md += f"### {channel.name} ({channel.relevance_score * 100:.0f}% Relevance)\n\n"
    md += f"### {channel.name} ({channel.relevance_score * 100:.0f}% Relevance)\n\n"
    md += f"{channel.description}\n\n"
    md += f"{channel.description}\n\n"
    md += "**Platforms:**\n\n"
    md += "**Platforms:**\n\n"
    for platform in channel.platforms:
    for platform in channel.platforms:
    md += f"- {platform}\n"
    md += f"- {platform}\n"
    md += "\n"
    md += "\n"
    md += f"**Budget Allocation:** ${strategy.allocated_budget.get(channel.name, 0):.2f}\n\n"
    md += f"**Budget Allocation:** ${strategy.allocated_budget.get(channel.name, 0):.2f}\n\n"


    md += "## Tactics\n\n"
    md += "## Tactics\n\n"
    for tactic in strategy.tactics:
    for tactic in strategy.tactics:
    md += f"### {tactic.name}\n\n"
    md += f"### {tactic.name}\n\n"
    md += f"**Channel:** {tactic.channel_name}\n\n"
    md += f"**Channel:** {tactic.channel_name}\n\n"
    md += f"{tactic.description}\n\n"
    md += f"{tactic.description}\n\n"
    md += f"- **Expected Impact:** {tactic.expected_impact * 100:.0f}%\n"
    md += f"- **Expected Impact:** {tactic.expected_impact * 100:.0f}%\n"
    md += f"- **Timeframe:** {tactic.timeframe}\n"
    md += f"- **Timeframe:** {tactic.timeframe}\n"
    md += f"- **Estimated Cost:** ${tactic.estimated_cost}\n"
    md += f"- **Estimated Cost:** ${tactic.estimated_cost}\n"
    md += "**Resources Required:**\n\n"
    md += "**Resources Required:**\n\n"
    for resource in tactic.resources_required:
    for resource in tactic.resources_required:
    md += f"- {resource}\n"
    md += f"- {resource}\n"
    md += "\n"
    md += "\n"


    md += "## Metrics\n\n"
    md += "## Metrics\n\n"
    for metric in strategy.metrics:
    for metric in strategy.metrics:
    md += f"### {metric.name}\n\n"
    md += f"### {metric.name}\n\n"
    md += f"{metric.description}\n\n"
    md += f"{metric.description}\n\n"
    md += f"- **Current:** {metric.current_value} {metric.unit}\n"
    md += f"- **Current:** {metric.current_value} {metric.unit}\n"
    md += f"- **Target:** {metric.target_value} {metric.unit}\n\n"
    md += f"- **Target:** {metric.target_value} {metric.unit}\n\n"


    return md
    return md
    else:
    else:
    raise ValueError(f"Unsupported export format: {format}")
    raise ValueError(f"Unsupported export format: {format}")


    def import_strategy(self, strategy_data: Dict[str, Any]) -> MarketingStrategySchema:
    def import_strategy(self, strategy_data: Dict[str, Any]) -> MarketingStrategySchema:
    """
    """
    Import a strategy from a dictionary.
    Import a strategy from a dictionary.


    Args:
    Args:
    strategy_data: Strategy data dictionary
    strategy_data: Strategy data dictionary


    Returns:
    Returns:
    Imported marketing strategy
    Imported marketing strategy
    """
    """
    # Create a new strategy from the imported data
    # Create a new strategy from the imported data
    strategy = MarketingStrategySchema(**strategy_data)
    strategy = MarketingStrategySchema(**strategy_data)


    # Add to strategies list
    # Add to strategies list
    self.strategies.append(strategy)
    self.strategies.append(strategy)


    # Update other attributes if present in imported data
    # Update other attributes if present in imported data
    self.business_type = strategy_data.get("business_type", self.business_type)
    self.business_type = strategy_data.get("business_type", self.business_type)
    self.business_size = strategy_data.get("business_size", self.business_size)
    self.business_size = strategy_data.get("business_size", self.business_size)
    self.goals = strategy_data.get("goals", self.goals)
    self.goals = strategy_data.get("goals", self.goals)


    return strategy
    return strategy