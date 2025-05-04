"""
"""
Marketing Agent for the pAIssive Income project.
Marketing Agent for the pAIssive Income project.
Specializes in marketing strategies and user acquisition.
Specializes in marketing strategies and user acquisition.
"""
"""


import uuid
import uuid
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List
from typing import Any, Dict, List




class MarketingAgent:
    class MarketingAgent:
    """
    """
    AI agent specialized in marketing strategies and user acquisition.
    AI agent specialized in marketing strategies and user acquisition.
    Creates marketing plans for niche AI tools to reach target users.
    Creates marketing plans for niche AI tools to reach target users.
    """
    """


    def __init__(self, team):
    def __init__(self, team):
    """
    """
    Initialize the Marketing Agent.
    Initialize the Marketing Agent.


    Args:
    Args:
    team: The parent AgentTeam instance
    team: The parent AgentTeam instance
    """
    """
    self.team = team
    self.team = team
    self.name = "Marketing Agent"
    self.name = "Marketing Agent"
    self.description = "Specializes in marketing strategies and user acquisition"
    self.description = "Specializes in marketing strategies and user acquisition"
    self.model_settings = team.config["model_settings"]["marketing"]
    self.model_settings = team.config["model_settings"]["marketing"]


    def create_plan(
    def create_plan(
    self,
    self,
    niche: Dict[str, Any],
    niche: Dict[str, Any],
    solution: Dict[str, Any],
    solution: Dict[str, Any],
    monetization: Dict[str, Any],
    monetization: Dict[str, Any],
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create a marketing plan for a specific solution.
    Create a marketing plan for a specific solution.


    Args:
    Args:
    niche: Niche dictionary from the Research Agent
    niche: Niche dictionary from the Research Agent
    solution: Solution design specification from the Developer Agent
    solution: Solution design specification from the Developer Agent
    monetization: Monetization strategy from the Monetization Agent
    monetization: Monetization strategy from the Monetization Agent


    Returns:
    Returns:
    Marketing plan specification
    Marketing plan specification
    """
    """
    # Create the marketing plan
    # Create the marketing plan
    plan = self._create_marketing_plan(niche, solution, monetization)
    plan = self._create_marketing_plan(niche, solution, monetization)


    # Store the marketing plan in the team's project state
    # Store the marketing plan in the team's project state
    self.team.project_state["marketing_plan"] = plan
    self.team.project_state["marketing_plan"] = plan


    return plan
    return plan


    def _create_marketing_plan(
    def _create_marketing_plan(
    self,
    self,
    niche: Dict[str, Any],
    niche: Dict[str, Any],
    solution: Dict[str, Any],
    solution: Dict[str, Any],
    monetization: Dict[str, Any],
    monetization: Dict[str, Any],
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create a detailed marketing plan for a specific solution.
    Create a detailed marketing plan for a specific solution.


    Args:
    Args:
    niche: Niche dictionary from the Research Agent
    niche: Niche dictionary from the Research Agent
    solution: Solution design specification from the Developer Agent
    solution: Solution design specification from the Developer Agent
    monetization: Monetization strategy from the Monetization Agent
    monetization: Monetization strategy from the Monetization Agent


    Returns:
    Returns:
    Marketing plan specification
    Marketing plan specification
    """
    """
    # In a real implementation, this would use AI to create the plan
    # In a real implementation, this would use AI to create the plan
    # For now, we'll return a placeholder implementation based on the niche, solution, and monetization
    # For now, we'll return a placeholder implementation based on the niche, solution, and monetization


    # Generate user personas based on the niche and solution
    # Generate user personas based on the niche and solution
    user_personas = [
    user_personas = [
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": f"{niche['name'].split(' ')[0].title()} Professional",
    "name": f"{niche['name'].split(' ')[0].title()} Professional",
    "description": f"Professional working in the {niche['name']} industry",
    "description": f"Professional working in the {niche['name']} industry",
    "pain_points": niche["problem_areas"],
    "pain_points": niche["problem_areas"],
    "goals": ["improve efficiency", "reduce costs", "increase quality"],
    "goals": ["improve efficiency", "reduce costs", "increase quality"],
    "demographics": {
    "demographics": {
    "age_range": "25-45",
    "age_range": "25-45",
    "education": "college degree",
    "education": "college degree",
    "income": "middle to high",
    "income": "middle to high",
    },
    },
    "behavior": {
    "behavior": {
    "tech_savvy": "medium to high",
    "tech_savvy": "medium to high",
    "price_sensitivity": "medium",
    "price_sensitivity": "medium",
    "decision_making": "rational",
    "decision_making": "rational",
    },
    },
    "preferred_channels": [
    "preferred_channels": [
    "linkedin",
    "linkedin",
    "industry forums",
    "industry forums",
    "professional networks",
    "professional networks",
    ],
    ],
    },
    },
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": f"{niche['name'].split(' ')[0].title()} Enthusiast",
    "name": f"{niche['name'].split(' ')[0].title()} Enthusiast",
    "description": f"Enthusiast interested in {niche['name']}",
    "description": f"Enthusiast interested in {niche['name']}",
    "pain_points": niche["problem_areas"][:2],  # Subset of pain points
    "pain_points": niche["problem_areas"][:2],  # Subset of pain points
    "goals": ["learn new skills", "improve quality", "save time"],
    "goals": ["learn new skills", "improve quality", "save time"],
    "demographics": {
    "demographics": {
    "age_range": "18-35",
    "age_range": "18-35",
    "education": "varied",
    "education": "varied",
    "income": "low to middle",
    "income": "low to middle",
    },
    },
    "behavior": {
    "behavior": {
    "tech_savvy": "high",
    "tech_savvy": "high",
    "price_sensitivity": "high",
    "price_sensitivity": "high",
    "decision_making": "emotional",
    "decision_making": "emotional",
    },
    },
    "preferred_channels": ["youtube", "reddit", "twitter", "discord"],
    "preferred_channels": ["youtube", "reddit", "twitter", "discord"],
    },
    },
    ]
    ]


    # Generate marketing channels based on the user personas
    # Generate marketing channels based on the user personas
    marketing_channels = [
    marketing_channels = [
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Content Marketing",
    "name": "Content Marketing",
    "description": f"Create valuable content related to {niche['name']}",
    "description": f"Create valuable content related to {niche['name']}",
    "platforms": ["blog", "youtube", "medium"],
    "platforms": ["blog", "youtube", "medium"],
    "content_types": ["tutorials", "case studies", "how-to guides"],
    "content_types": ["tutorials", "case studies", "how-to guides"],
    "target_personas": [persona["id"] for persona in user_personas],
    "target_personas": [persona["id"] for persona in user_personas],
    "cost_estimate": "$500 - $1,000 per month",
    "cost_estimate": "$500 - $1,000 per month",
    "expected_roi": "medium to high",
    "expected_roi": "medium to high",
    "timeline": "ongoing",
    "timeline": "ongoing",
    },
    },
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Social Media Marketing",
    "name": "Social Media Marketing",
    "description": f"Engage with {niche['name']} communities on social media",
    "description": f"Engage with {niche['name']} communities on social media",
    "platforms": ["twitter", "linkedin", "reddit"],
    "platforms": ["twitter", "linkedin", "reddit"],
    "content_types": ["tips", "product updates", "user success stories"],
    "content_types": ["tips", "product updates", "user success stories"],
    "target_personas": [persona["id"] for persona in user_personas],
    "target_personas": [persona["id"] for persona in user_personas],
    "cost_estimate": "$300 - $500 per month",
    "cost_estimate": "$300 - $500 per month",
    "expected_roi": "medium",
    "expected_roi": "medium",
    "timeline": "ongoing",
    "timeline": "ongoing",
    },
    },
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Email Marketing",
    "name": "Email Marketing",
    "description": f"Build and nurture an email list of {niche['name']} professionals",
    "description": f"Build and nurture an email list of {niche['name']} professionals",
    "platforms": ["mailchimp", "convertkit"],
    "platforms": ["mailchimp", "convertkit"],
    "content_types": ["newsletters", "product updates", "special offers"],
    "content_types": ["newsletters", "product updates", "special offers"],
    "target_personas": [user_personas[0]["id"]],  # Professional persona
    "target_personas": [user_personas[0]["id"]],  # Professional persona
    "cost_estimate": "$100 - $300 per month",
    "cost_estimate": "$100 - $300 per month",
    "expected_roi": "high",
    "expected_roi": "high",
    "timeline": "ongoing",
    "timeline": "ongoing",
    },
    },
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Paid Advertising",
    "name": "Paid Advertising",
    "description": f"Run targeted ads to reach {niche['name']} professionals",
    "description": f"Run targeted ads to reach {niche['name']} professionals",
    "platforms": ["google ads", "facebook ads", "linkedin ads"],
    "platforms": ["google ads", "facebook ads", "linkedin ads"],
    "content_types": ["product demos", "free trial offers", "testimonials"],
    "content_types": ["product demos", "free trial offers", "testimonials"],
    "target_personas": [persona["id"] for persona in user_personas],
    "target_personas": [persona["id"] for persona in user_personas],
    "cost_estimate": "$1,000 - $2,000 per month",
    "cost_estimate": "$1,000 - $2,000 per month",
    "expected_roi": "medium to high",
    "expected_roi": "medium to high",
    "timeline": "3-6 months",
    "timeline": "3-6 months",
    },
    },
    ]
    ]


    # Generate marketing campaigns based on the solution and monetization
    # Generate marketing campaigns based on the solution and monetization
    marketing_campaigns = [
    marketing_campaigns = [
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Product Launch",
    "name": "Product Launch",
    "description": f"Launch campaign for {solution['name']}",
    "description": f"Launch campaign for {solution['name']}",
    "channels": [channel["id"] for channel in marketing_channels],
    "channels": [channel["id"] for channel in marketing_channels],
    "budget": "$3,000 - $5,000",
    "budget": "$3,000 - $5,000",
    "duration": "1 month",
    "duration": "1 month",
    "goals": {
    "goals": {
    "awareness": "reach 10,000 potential users",
    "awareness": "reach 10,000 potential users",
    "acquisition": "acquire 100 free trial users",
    "acquisition": "acquire 100 free trial users",
    "conversion": "convert 50 users to paid subscriptions",
    "conversion": "convert 50 users to paid subscriptions",
    },
    },
    "timeline": "at product launch",
    "timeline": "at product launch",
    },
    },
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Free Trial Promotion",
    "name": "Free Trial Promotion",
    "description": f"Promote free trial of {solution['name']}",
    "description": f"Promote free trial of {solution['name']}",
    "channels": [
    "channels": [
    marketing_channels[0]["id"],
    marketing_channels[0]["id"],
    marketing_channels[1]["id"],
    marketing_channels[1]["id"],
    marketing_channels[3]["id"],
    marketing_channels[3]["id"],
    ],
    ],
    "budget": "$2,000 - $3,000",
    "budget": "$2,000 - $3,000",
    "duration": "ongoing",
    "duration": "ongoing",
    "goals": {
    "goals": {
    "awareness": "reach 5,000 potential users per month",
    "awareness": "reach 5,000 potential users per month",
    "acquisition": "acquire 50 free trial users per month",
    "acquisition": "acquire 50 free trial users per month",
    "conversion": "convert 25 users to paid subscriptions per month",
    "conversion": "convert 25 users to paid subscriptions per month",
    },
    },
    "timeline": "ongoing after launch",
    "timeline": "ongoing after launch",
    },
    },
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Yearly Subscription Promotion",
    "name": "Yearly Subscription Promotion",
    "description": f"Promote yearly subscription discount for {solution['name']}",
    "description": f"Promote yearly subscription discount for {solution['name']}",
    "channels": [marketing_channels[0]["id"], marketing_channels[2]["id"]],
    "channels": [marketing_channels[0]["id"], marketing_channels[2]["id"]],
    "budget": "$1,000 - $2,000",
    "budget": "$1,000 - $2,000",
    "duration": "1 month",
    "duration": "1 month",
    "goals": {
    "goals": {
    "awareness": "reach all free trial and monthly subscription users",
    "awareness": "reach all free trial and monthly subscription users",
    "conversion": "convert 20% of monthly subscribers to yearly",
    "conversion": "convert 20% of monthly subscribers to yearly",
    },
    },
    "timeline": "quarterly",
    "timeline": "quarterly",
    },
    },
    ]
    ]


    # Generate content strategy based on the niche and solution
    # Generate content strategy based on the niche and solution
    content_strategy = {
    content_strategy = {
    "blog_posts": [
    "blog_posts": [
    f"Top 10 Challenges in {niche['name']} and How to Solve Them",
    f"Top 10 Challenges in {niche['name']} and How to Solve Them",
    f"How {solution['name']} Can Save You X Hours per Week",
    f"How {solution['name']} Can Save You X Hours per Week",
    f"Case Study: How Company X Improved Their {niche['name']} Process with {solution['name']}",
    f"Case Study: How Company X Improved Their {niche['name']} Process with {solution['name']}",
    f"The Future of {niche['name']}: Trends and Predictions",
    f"The Future of {niche['name']}: Trends and Predictions",
    f"{niche['name']} Best Practices for 2023",
    f"{niche['name']} Best Practices for 2023",
    ],
    ],
    "videos": [
    "videos": [
    f"{solution['name']} Demo: Solving {niche['problem_areas'][0]}",
    f"{solution['name']} Demo: Solving {niche['problem_areas'][0]}",
    f"How to Get Started with {solution['name']} in 10 Minutes",
    f"How to Get Started with {solution['name']} in 10 Minutes",
    f"Customer Testimonial: {solution['name']} in Action",
    f"Customer Testimonial: {solution['name']} in Action",
    f"Comparing {solution['name']} to Traditional {niche['name']} Solutions",
    f"Comparing {solution['name']} to Traditional {niche['name']} Solutions",
    ],
    ],
    "social_media": [
    "social_media": [
    f"Tips for {niche['name']} professionals",
    f"Tips for {niche['name']} professionals",
    f"{solution['name']} feature highlights",
    f"{solution['name']} feature highlights",
    "User success stories",
    "User success stories",
    "Industry news and trends",
    "Industry news and trends",
    ],
    ],
    "email_sequences": [
    "email_sequences": [
    "Welcome sequence for new subscribers",
    "Welcome sequence for new subscribers",
    "Free trial onboarding sequence",
    "Free trial onboarding sequence",
    "Feature highlight sequence",
    "Feature highlight sequence",
    "Upgrade promotion sequence",
    "Upgrade promotion sequence",
    "Re-engagement sequence for inactive users",
    "Re-engagement sequence for inactive users",
    ],
    ],
    }
    }


    # Generate growth strategy based on the monetization
    # Generate growth strategy based on the monetization
    growth_strategy = {
    growth_strategy = {
    "user_acquisition": {
    "user_acquisition": {
    "target": f"{monetization['revenue_projections']['year_1']['users']} users in year 1",
    "target": f"{monetization['revenue_projections']['year_1']['users']} users in year 1",
    "channels": [channel["name"] for channel in marketing_channels],
    "channels": [channel["name"] for channel in marketing_channels],
    "cost_per_acquisition": "$20 - $50",
    "cost_per_acquisition": "$20 - $50",
    "strategies": [
    "strategies": [
    "Content marketing to build authority",
    "Content marketing to build authority",
    "Referral program for existing users",
    "Referral program for existing users",
    "Strategic partnerships with complementary tools",
    "Strategic partnerships with complementary tools",
    "Free tier with limited features",
    "Free tier with limited features",
    ],
    ],
    },
    },
    "user_retention": {
    "user_retention": {
    "target": "80% retention rate",
    "target": "80% retention rate",
    "strategies": [
    "strategies": [
    "Regular feature updates",
    "Regular feature updates",
    "Personalized onboarding",
    "Personalized onboarding",
    "Responsive customer support",
    "Responsive customer support",
    "Educational content for advanced usage",
    "Educational content for advanced usage",
    ],
    ],
    },
    },
    "user_expansion": {
    "user_expansion": {
    "target": "30% of users upgrade to higher tier",
    "target": "30% of users upgrade to higher tier",
    "strategies": [
    "strategies": [
    "Feature-based upselling",
    "Feature-based upselling",
    "Usage-based prompts",
    "Usage-based prompts",
    "Success-based prompts",
    "Success-based prompts",
    "Limited-time promotions",
    "Limited-time promotions",
    ],
    ],
    },
    },
    }
    }


    return {
    return {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "solution_id": solution["id"],
    "solution_id": solution["id"],
    "user_personas": user_personas,
    "user_personas": user_personas,
    "marketing_channels": marketing_channels,
    "marketing_channels": marketing_channels,
    "marketing_campaigns": marketing_campaigns,
    "marketing_campaigns": marketing_campaigns,
    "content_strategy": content_strategy,
    "content_strategy": content_strategy,
    "growth_strategy": growth_strategy,
    "growth_strategy": growth_strategy,
    "branding": {
    "branding": {
    "name": solution["name"],
    "name": solution["name"],
    "tagline": f"AI-powered {niche['name']} solution",
    "tagline": f"AI-powered {niche['name']} solution",
    "value_proposition": f"Save time and improve quality in your {niche['name']} process",
    "value_proposition": f"Save time and improve quality in your {niche['name']} process",
    "brand_voice": "professional, helpful, innovative",
    "brand_voice": "professional, helpful, innovative",
    "visual_identity": {
    "visual_identity": {
    "color_scheme": "blue and green",
    "color_scheme": "blue and green",
    "typography": "modern, clean",
    "typography": "modern, clean",
    "imagery": "professional, tech-focused",
    "imagery": "professional, tech-focused",
    },
    },
    },
    },
    "metrics_and_kpis": {
    "metrics_and_kpis": {
    "acquisition_metrics": [
    "acquisition_metrics": [
    "website visitors",
    "website visitors",
    "free trial signups",
    "free trial signups",
    "conversion rate",
    "conversion rate",
    ],
    ],
    "engagement_metrics": [
    "engagement_metrics": [
    "active users",
    "active users",
    "feature usage",
    "feature usage",
    "session duration",
    "session duration",
    ],
    ],
    "retention_metrics": ["churn rate", "renewal rate", "lifetime value"],
    "retention_metrics": ["churn rate", "renewal rate", "lifetime value"],
    "revenue_metrics": [
    "revenue_metrics": [
    "monthly recurring revenue",
    "monthly recurring revenue",
    "annual recurring revenue",
    "annual recurring revenue",
    "average revenue per user",
    "average revenue per user",
    ],
    ],
    },
    },
    "timeline": {
    "timeline": {
    "pre_launch": "1 month",
    "pre_launch": "1 month",
    "launch": "1 month",
    "launch": "1 month",
    "post_launch": "ongoing",
    "post_launch": "ongoing",
    },
    },
    "budget": {
    "budget": {
    "initial": "$5,000 - $10,000",
    "initial": "$5,000 - $10,000",
    "ongoing": "$2,000 - $5,000 per month",
    "ongoing": "$2,000 - $5,000 per month",
    "allocation": {
    "allocation": {
    "content_creation": "30%",
    "content_creation": "30%",
    "paid_advertising": "40%",
    "paid_advertising": "40%",
    "tools_and_software": "10%",
    "tools_and_software": "10%",
    "partnerships_and_collaborations": "20%",
    "partnerships_and_collaborations": "20%",
    },
    },
    },
    },
    "timestamp": datetime.now().isoformat(),
    "timestamp": datetime.now().isoformat(),
    }
    }


    def generate_content_ideas(
    def generate_content_ideas(
    self, niche: Dict[str, Any], solution: Dict[str, Any]
    self, niche: Dict[str, Any], solution: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Generate content ideas for marketing a specific solution.
    Generate content ideas for marketing a specific solution.


    Args:
    Args:
    niche: Niche dictionary from the Research Agent
    niche: Niche dictionary from the Research Agent
    solution: Solution design specification from the Developer Agent
    solution: Solution design specification from the Developer Agent


    Returns:
    Returns:
    List of content ideas
    List of content ideas
    """
    """
    # In a real implementation, this would use AI to generate content ideas
    # In a real implementation, this would use AI to generate content ideas
    # For now, we'll return a placeholder implementation
    # For now, we'll return a placeholder implementation


    content_types = ["blog_post", "video", "social_media", "email", "webinar"]
    content_types = ["blog_post", "video", "social_media", "email", "webinar"]


    content_ideas = []
    content_ideas = []


    for i in range(10):  # Generate 10 content ideas
    for i in range(10):  # Generate 10 content ideas
    content_type = content_types[i % len(content_types)]
    content_type = content_types[i % len(content_types)]


    if content_type == "blog_post":
    if content_type == "blog_post":
    title = f"How to Solve {niche['problem_areas'][i % len(niche['problem_areas'])]} in {niche['name']}"
    title = f"How to Solve {niche['problem_areas'][i % len(niche['problem_areas'])]} in {niche['name']}"
    description = f"A detailed guide on solving {niche['problem_areas'][i % len(niche['problem_areas'])]} using {solution['name']}"
    description = f"A detailed guide on solving {niche['problem_areas'][i % len(niche['problem_areas'])]} using {solution['name']}"
    elif content_type == "video":
    elif content_type == "video":
    title = f"{solution['name']} Demo: {solution['features'][i % len(solution['features'])]['name']}"
    title = f"{solution['name']} Demo: {solution['features'][i % len(solution['features'])]['name']}"
    description = f"A video demonstration of the {solution['features'][i % len(solution['features'])]['name']} feature"
    description = f"A video demonstration of the {solution['features'][i % len(solution['features'])]['name']} feature"
    elif content_type == "social_media":
    elif content_type == "social_media":
    title = f"Tip: {niche['problem_areas'][i % len(niche['problem_areas'])]} Solution"
    title = f"Tip: {niche['problem_areas'][i % len(niche['problem_areas'])]} Solution"
    description = f"A quick tip on solving {niche['problem_areas'][i % len(niche['problem_areas'])]} using {solution['name']}"
    description = f"A quick tip on solving {niche['problem_areas'][i % len(niche['problem_areas'])]} using {solution['name']}"
    elif content_type == "email":
    elif content_type == "email":
    title = f"Introducing {solution['features'][i % len(solution['features'])]['name']}"
    title = f"Introducing {solution['features'][i % len(solution['features'])]['name']}"
    description = f"An email introducing the {solution['features'][i % len(solution['features'])]['name']} feature to subscribers"
    description = f"An email introducing the {solution['features'][i % len(solution['features'])]['name']} feature to subscribers"
    elif content_type == "webinar":
    elif content_type == "webinar":
    title = f"Mastering {niche['name']}: Advanced Techniques with {solution['name']}"
    title = f"Mastering {niche['name']}: Advanced Techniques with {solution['name']}"
    description = f"A webinar on advanced techniques for {niche['name']} using {solution['name']}"
    description = f"A webinar on advanced techniques for {niche['name']} using {solution['name']}"


    content_ideas.append(
    content_ideas.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": content_type,
    "type": content_type,
    "title": title,
    "title": title,
    "description": description,
    "description": description,
    "target_audience": "professionals" if i % 2 == 0 else "enthusiasts",
    "target_audience": "professionals" if i % 2 == 0 else "enthusiasts",
    "goal": (
    "goal": (
    "education"
    "education"
    if i % 3 == 0
    if i % 3 == 0
    else "conversion" if i % 3 == 1 else "awareness"
    else "conversion" if i % 3 == 1 else "awareness"
    ),
    ),
    "estimated_impact": (
    "estimated_impact": (
    "high" if i % 3 == 0 else "medium" if i % 3 == 1 else "low"
    "high" if i % 3 == 0 else "medium" if i % 3 == 1 else "low"
    ),
    ),
    }
    }
    )
    )


    return content_ideas
    return content_ideas


    def __str__(self) -> str:
    def __str__(self) -> str:
    """String representation of the Marketing Agent."""
    return f"{self.name}: {self.description}"
