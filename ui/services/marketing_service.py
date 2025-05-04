"""
"""
Marketing Service for the pAIssive Income UI.
Marketing Service for the pAIssive Income UI.


This service provides methods for interacting with the Marketing Agent module.
This service provides methods for interacting with the Marketing Agent module.
"""
"""


import logging
import logging
import time
import time
import uuid
import uuid
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from agent_team.agent_profiles.marketing import MarketingAgent
from agent_team.agent_profiles.marketing import MarketingAgent
from common_utils import add_days, format_datetime
from common_utils import add_days, format_datetime
from interfaces.ui_interfaces import IMarketingService
from interfaces.ui_interfaces import IMarketingService


from .base_service import BaseService
from .base_service import BaseService
from .developer_service import DeveloperService
from .developer_service import DeveloperService


from agent_team import AgentTeam
from agent_team import AgentTeam






# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class MarketingService(BaseService, IMarketingService):
    class MarketingService(BaseService, IMarketingService):
    """
    """
    Service for interacting with the Marketing Agent module.
    Service for interacting with the Marketing Agent module.
    """
    """


    def __init__(self):
    def __init__(self):
    """Initialize the Marketing service."""
    super().__init__()
    self.campaigns_file = "marketing_campaigns.json"

    # Import the Marketing Agent class
    try:
    # noqa: F401
    self.marketing_agent_available = True
except ImportError:
    logger.warning("Marketing Agent module not available. Using mock data.")
    self.marketing_agent_available = False

    def create_campaign(
    self, solution_id: str, strategy_id: str = None
    ) -> Dict[str, Any]:
    """
    """
    Create a marketing campaign for a solution.
    Create a marketing campaign for a solution.


    Args:
    Args:
    solution_id: ID of the solution
    solution_id: ID of the solution


    Returns:
    Returns:
    Marketing campaign data
    Marketing campaign data
    """
    """
    # Get the solution data
    # Get the solution data
    developer_service = DeveloperService()
    developer_service = DeveloperService()
    solution = developer_service.get_solution(solution_id)
    solution = developer_service.get_solution(solution_id)


    if solution is None:
    if solution is None:
    logger.error(f"Solution with ID {solution_id} not found")
    logger.error(f"Solution with ID {solution_id} not found")
    return {}
    return {}


    if self.marketing_agent_available:
    if self.marketing_agent_available:
    try:
    try:
    # Create a new agent team for this campaign
    # Create a new agent team for this campaign
    team = AgentTeam(f"{solution['name']} Marketing")
    team = AgentTeam(f"{solution['name']} Marketing")


    # Create the marketing campaign
    # Create the marketing campaign
    campaign = team.marketing.create_marketing_plan(solution)
    campaign = team.marketing.create_marketing_plan(solution)


    # Add metadata
    # Add metadata
    campaign["id"] = str(uuid.uuid4())
    campaign["id"] = str(uuid.uuid4())
    campaign["solution_id"] = solution_id
    campaign["solution_id"] = solution_id
    campaign["created_at"] = datetime.now().isoformat()
    campaign["created_at"] = datetime.now().isoformat()
    campaign["updated_at"] = datetime.now().isoformat()
    campaign["updated_at"] = datetime.now().isoformat()
    campaign["status"] = "active"
    campaign["status"] = "active"
except Exception as e:
except Exception as e:
    logger.error(f"Error creating marketing campaign: {e}")
    logger.error(f"Error creating marketing campaign: {e}")
    campaign = self._create_mock_campaign(solution)
    campaign = self._create_mock_campaign(solution)
    else:
    else:
    campaign = self._create_mock_campaign(solution)
    campaign = self._create_mock_campaign(solution)


    # Save the campaign
    # Save the campaign
    campaigns = self.get_campaigns()
    campaigns = self.get_campaigns()
    campaigns.append(campaign)
    campaigns.append(campaign)
    self.save_data(self.campaigns_file, campaigns)
    self.save_data(self.campaigns_file, campaigns)


    return campaign
    return campaign


    def get_campaigns(self) -> List[Dict[str, Any]]:
    def get_campaigns(self) -> List[Dict[str, Any]]:
    """
    """
    Get all marketing campaigns.
    Get all marketing campaigns.


    Returns:
    Returns:
    List of marketing campaigns
    List of marketing campaigns
    """
    """
    campaigns = self.load_data(self.campaigns_file)
    campaigns = self.load_data(self.campaigns_file)
    if campaigns is None:
    if campaigns is None:
    campaigns = []
    campaigns = []
    self.save_data(self.campaigns_file, campaigns)
    self.save_data(self.campaigns_file, campaigns)
    return campaigns
    return campaigns


    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
    """
    """
    Get a marketing campaign by ID.
    Get a marketing campaign by ID.


    Args:
    Args:
    campaign_id: ID of the campaign
    campaign_id: ID of the campaign


    Returns:
    Returns:
    Marketing campaign data, or None if not found
    Marketing campaign data, or None if not found
    """
    """
    campaigns = self.get_campaigns()
    campaigns = self.get_campaigns()
    for campaign in campaigns:
    for campaign in campaigns:
    if campaign["id"] == campaign_id:
    if campaign["id"] == campaign_id:
    return campaign
    return campaign
    return None
    return None


    def save_campaign(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
    def save_campaign(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Save a marketing campaign.
    Save a marketing campaign.


    Args:
    Args:
    campaign: Campaign dictionary
    campaign: Campaign dictionary


    Returns:
    Returns:
    Saved campaign dictionary
    Saved campaign dictionary
    """
    """
    campaigns = self.get_campaigns()
    campaigns = self.get_campaigns()


    # Check if the campaign already exists
    # Check if the campaign already exists
    for i, existing_campaign in enumerate(campaigns):
    for i, existing_campaign in enumerate(campaigns):
    if existing_campaign["id"] == campaign["id"]:
    if existing_campaign["id"] == campaign["id"]:
    # Update existing campaign
    # Update existing campaign
    campaign["updated_at"] = datetime.now().isoformat()
    campaign["updated_at"] = datetime.now().isoformat()
    campaigns[i] = campaign
    campaigns[i] = campaign
    self.save_data(self.campaigns_file, campaigns)
    self.save_data(self.campaigns_file, campaigns)
    return campaign
    return campaign


    # Add new campaign
    # Add new campaign
    if "created_at" not in campaign:
    if "created_at" not in campaign:
    campaign["created_at"] = datetime.now().isoformat()
    campaign["created_at"] = datetime.now().isoformat()
    if "updated_at" not in campaign:
    if "updated_at" not in campaign:
    campaign["updated_at"] = datetime.now().isoformat()
    campaign["updated_at"] = datetime.now().isoformat()
    campaigns.append(campaign)
    campaigns.append(campaign)
    self.save_data(self.campaigns_file, campaigns)
    self.save_data(self.campaigns_file, campaigns)
    return campaign
    return campaign


    def _create_mock_campaign(self, solution: Dict[str, Any]) -> Dict[str, Any]:
    def _create_mock_campaign(self, solution: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Create a mock marketing campaign for testing.
    Create a mock marketing campaign for testing.


    Args:
    Args:
    solution: Solution data
    solution: Solution data


    Returns:
    Returns:
    Mock marketing campaign data
    Mock marketing campaign data
    """
    """
    # Create user personas
    # Create user personas
    personas = [
    personas = [
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Professional User",
    "name": "Professional User",
    "demographics": {
    "demographics": {
    "age_range": "25-45",
    "age_range": "25-45",
    "gender": "all",
    "gender": "all",
    "education": "college degree or higher",
    "education": "college degree or higher",
    "income": "middle to upper",
    "income": "middle to upper",
    "location": "global, urban areas",
    "location": "global, urban areas",
    },
    },
    "pain_points": [
    "pain_points": [
    "Time constraints",
    "Time constraints",
    "Need for high-quality output",
    "Need for high-quality output",
    "Competitive pressure",
    "Competitive pressure",
    ],
    ],
    "goals": [
    "goals": [
    "Increase productivity",
    "Increase productivity",
    "Improve quality of work",
    "Improve quality of work",
    "Reduce costs",
    "Reduce costs",
    ],
    ],
    "behavior": {
    "behavior": {
    "tech_savvy": "high",
    "tech_savvy": "high",
    "price_sensitivity": "medium",
    "price_sensitivity": "medium",
    "brand_loyalty": "medium",
    "brand_loyalty": "medium",
    "decision_making": "rational",
    "decision_making": "rational",
    },
    },
    },
    },
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Hobbyist User",
    "name": "Hobbyist User",
    "demographics": {
    "demographics": {
    "age_range": "18-65",
    "age_range": "18-65",
    "gender": "all",
    "gender": "all",
    "education": "varied",
    "education": "varied",
    "income": "varied",
    "income": "varied",
    "location": "global",
    "location": "global",
    },
    },
    "pain_points": [
    "pain_points": [
    "Limited skills",
    "Limited skills",
    "Budget constraints",
    "Budget constraints",
    "Learning curve",
    "Learning curve",
    ],
    ],
    "goals": [
    "goals": [
    "Create professional-looking output",
    "Create professional-looking output",
    "Learn new skills",
    "Learn new skills",
    "Express creativity",
    "Express creativity",
    ],
    ],
    "behavior": {
    "behavior": {
    "tech_savvy": "medium",
    "tech_savvy": "medium",
    "price_sensitivity": "high",
    "price_sensitivity": "high",
    "brand_loyalty": "low",
    "brand_loyalty": "low",
    "decision_making": "emotional",
    "decision_making": "emotional",
    },
    },
    },
    },
    ]
    ]


    # Create channel strategies
    # Create channel strategies
    channels = [
    channels = [
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Content Marketing",
    "name": "Content Marketing",
    "description": "Create valuable content to attract and engage target audience",
    "description": "Create valuable content to attract and engage target audience",
    "platforms": ["Blog", "YouTube", "Medium"],
    "platforms": ["Blog", "YouTube", "Medium"],
    "content_types": ["Tutorials", "Case studies", "How-to guides"],
    "content_types": ["Tutorials", "Case studies", "How-to guides"],
    "kpis": ["Website traffic", "Time on page", "Conversion rate"],
    "kpis": ["Website traffic", "Time on page", "Conversion rate"],
    "budget_allocation": "30%",
    "budget_allocation": "30%",
    },
    },
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Social Media Marketing",
    "name": "Social Media Marketing",
    "description": "Engage with audience on social platforms",
    "description": "Engage with audience on social platforms",
    "platforms": ["Twitter", "LinkedIn", "Instagram"],
    "platforms": ["Twitter", "LinkedIn", "Instagram"],
    "content_types": [
    "content_types": [
    "Tips and tricks",
    "Tips and tricks",
    "Success stories",
    "Success stories",
    "Product updates",
    "Product updates",
    ],
    ],
    "kpis": ["Followers", "Engagement rate", "Click-through rate"],
    "kpis": ["Followers", "Engagement rate", "Click-through rate"],
    "budget_allocation": "25%",
    "budget_allocation": "25%",
    },
    },
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Email Marketing",
    "name": "Email Marketing",
    "description": "Nurture leads and retain customers through email",
    "description": "Nurture leads and retain customers through email",
    "platforms": ["Mailchimp", "ConvertKit"],
    "platforms": ["Mailchimp", "ConvertKit"],
    "content_types": [
    "content_types": [
    "Newsletters",
    "Newsletters",
    "Product announcements",
    "Product announcements",
    "Tips and resources",
    "Tips and resources",
    ],
    ],
    "kpis": ["Open rate", "Click-through rate", "Conversion rate"],
    "kpis": ["Open rate", "Click-through rate", "Conversion rate"],
    "budget_allocation": "20%",
    "budget_allocation": "20%",
    },
    },
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Influencer Marketing",
    "name": "Influencer Marketing",
    "description": "Partner with influencers in the niche",
    "description": "Partner with influencers in the niche",
    "platforms": ["YouTube", "Instagram", "TikTok"],
    "platforms": ["YouTube", "Instagram", "TikTok"],
    "content_types": ["Reviews", "Tutorials", "Testimonials"],
    "content_types": ["Reviews", "Tutorials", "Testimonials"],
    "kpis": ["Reach", "Engagement", "Conversions"],
    "kpis": ["Reach", "Engagement", "Conversions"],
    "budget_allocation": "15%",
    "budget_allocation": "15%",
    },
    },
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "SEO",
    "name": "SEO",
    "description": "Optimize for search engines to drive organic traffic",
    "description": "Optimize for search engines to drive organic traffic",
    "platforms": ["Google", "Bing"],
    "platforms": ["Google", "Bing"],
    "content_types": ["Blog posts", "Landing pages", "FAQ pages"],
    "content_types": ["Blog posts", "Landing pages", "FAQ pages"],
    "kpis": ["Organic traffic", "Keyword rankings", "Conversion rate"],
    "kpis": ["Organic traffic", "Keyword rankings", "Conversion rate"],
    "budget_allocation": "10%",
    "budget_allocation": "10%",
    },
    },
    ]
    ]


    # Create content templates
    # Create content templates
    content_templates = [
    content_templates = [
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Blog Post Template",
    "name": "Blog Post Template",
    "description": "Template for creating blog posts",
    "description": "Template for creating blog posts",
    "content_type": "blog_post",
    "content_type": "blog_post",
    "target_persona": personas[0]["name"],
    "target_persona": personas[0]["name"],
    "tone": "professional",
    "tone": "professional",
    "sections": [
    "sections": [
    "Introduction",
    "Introduction",
    "Problem statement",
    "Problem statement",
    "Solution overview",
    "Solution overview",
    "Step-by-step guide",
    "Step-by-step guide",
    "Benefits",
    "Benefits",
    "Case study/example",
    "Case study/example",
    "Conclusion with call to action",
    "Conclusion with call to action",
    ],
    ],
    "estimated_length": "1500-2000 words",
    "estimated_length": "1500-2000 words",
    },
    },
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Social Media Template",
    "name": "Social Media Template",
    "description": "Template for creating social media posts",
    "description": "Template for creating social media posts",
    "content_type": "social_media",
    "content_type": "social_media",
    "target_persona": personas[1]["name"],
    "target_persona": personas[1]["name"],
    "tone": "casual",
    "tone": "casual",
    "sections": [
    "sections": [
    "Attention-grabbing headline",
    "Attention-grabbing headline",
    "Value proposition",
    "Value proposition",
    "Social proof",
    "Social proof",
    "Call to action",
    "Call to action",
    ],
    ],
    "estimated_length": "50-100 words",
    "estimated_length": "50-100 words",
    },
    },
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": "Email Newsletter Template",
    "name": "Email Newsletter Template",
    "description": "Template for creating email newsletters",
    "description": "Template for creating email newsletters",
    "content_type": "email_newsletter",
    "content_type": "email_newsletter",
    "target_persona": personas[0]["name"],
    "target_persona": personas[0]["name"],
    "tone": "professional",
    "tone": "professional",
    "sections": [
    "sections": [
    "Personalized greeting",
    "Personalized greeting",
    "Value-packed introduction",
    "Value-packed introduction",
    "Main content with tips or news",
    "Main content with tips or news",
    "Product spotlight",
    "Product spotlight",
    "Call to action",
    "Call to action",
    "Footer with contact information",
    "Footer with contact information",
    ],
    ],
    "estimated_length": "500-700 words",
    "estimated_length": "500-700 words",
    },
    },
    ]
    ]


    # Create mock campaign
    # Create mock campaign
    return {
    return {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": f"{solution['name']} Marketing Campaign",
    "name": f"{solution['name']} Marketing Campaign",
    "description": f"Marketing campaign for {solution['name']}",
    "description": f"Marketing campaign for {solution['name']}",
    "solution_id": solution["id"],
    "solution_id": solution["id"],
    "target_audience": {
    "target_audience": {
    "primary_persona": personas[0],
    "primary_persona": personas[0],
    "secondary_persona": personas[1],
    "secondary_persona": personas[1],
    },
    },
    "value_proposition": f"Help users save time and improve quality with AI-powered {solution['name'].lower()}",
    "value_proposition": f"Help users save time and improve quality with AI-powered {solution['name'].lower()}",
    "channel_strategy": {
    "channel_strategy": {
    "primary_channels": channels[:3],
    "primary_channels": channels[:3],
    "secondary_channels": channels[3:],
    "secondary_channels": channels[3:],
    "budget": {
    "budget": {
    "total": "$5000",
    "total": "$5000",
    "allocation": {
    "allocation": {
    channel["name"]: channel["budget_allocation"]
    channel["name"]: channel["budget_allocation"]
    for channel in channels
    for channel in channels
    },
    },
    },
    },
    },
    },
    "content_strategy": {
    "content_strategy": {
    "themes": [
    "themes": [
    "Productivity enhancement",
    "Productivity enhancement",
    "Quality improvement",
    "Quality improvement",
    "Cost reduction",
    "Cost reduction",
    "Competitive advantage",
    "Competitive advantage",
    ],
    ],
    "content_calendar": {
    "content_calendar": {
    "frequency": {
    "frequency": {
    "blog_posts": "weekly",
    "blog_posts": "weekly",
    "social_media": "daily",
    "social_media": "daily",
    "email_newsletters": "bi-weekly",
    "email_newsletters": "bi-weekly",
    },
    },
    "upcoming_content": [
    "upcoming_content": [
    {
    {
    "title": f"How {solution['name']} Can Save You 10 Hours a Week",
    "title": f"How {solution['name']} Can Save You 10 Hours a Week",
    "type": "blog_post",
    "type": "blog_post",
    "publish_date": format_datetime(
    "publish_date": format_datetime(
    add_days(datetime.now(), 7), "%Y-%m-%dT%H:%M:%S.%fZ"
    add_days(datetime.now(), 7), "%Y-%m-%dT%H:%M:%S.%fZ"
    ),
    ),
    "status": "planned",
    "status": "planned",
    },
    },
    {
    {
    "title": f"5 Ways {solution['name']} Improves Your Work Quality",
    "title": f"5 Ways {solution['name']} Improves Your Work Quality",
    "type": "blog_post",
    "type": "blog_post",
    "publish_date": format_datetime(
    "publish_date": format_datetime(
    add_days(datetime.now(), 14), "%Y-%m-%dT%H:%M:%S.%fZ"
    add_days(datetime.now(), 14), "%Y-%m-%dT%H:%M:%S.%fZ"
    ),
    ),
    "status": "planned",
    "status": "planned",
    },
    },
    {
    {
    "title": f"Welcome to {solution['name']}",
    "title": f"Welcome to {solution['name']}",
    "type": "email_newsletter",
    "type": "email_newsletter",
    "publish_date": format_datetime(
    "publish_date": format_datetime(
    add_days(datetime.now(), 1), "%Y-%m-%dT%H:%M:%S.%fZ"
    add_days(datetime.now(), 1), "%Y-%m-%dT%H:%M:%S.%fZ"
    ),
    ),
    "status": "planned",
    "status": "planned",
    },
    },
    ],
    ],
    },
    },
    "content_templates": content_templates,
    "content_templates": content_templates,
    },
    },
    "launch_plan": {
    "launch_plan": {
    "phases": [
    "phases": [
    {
    {
    "name": "Pre-launch",
    "name": "Pre-launch",
    "duration": "4 weeks",
    "duration": "4 weeks",
    "activities": [
    "activities": [
    "Create landing page",
    "Create landing page",
    "Set up email list",
    "Set up email list",
    "Prepare launch content",
    "Prepare launch content",
    "Reach out to influencers",
    "Reach out to influencers",
    ],
    ],
    },
    },
    {
    {
    "name": "Launch",
    "name": "Launch",
    "duration": "2 weeks",
    "duration": "2 weeks",
    "activities": [
    "activities": [
    "Announce on all channels",
    "Announce on all channels",
    "Run limited-time promotion",
    "Run limited-time promotion",
    "Host webinar or live demo",
    "Host webinar or live demo",
    "Engage with early adopters",
    "Engage with early adopters",
    ],
    ],
    },
    },
    {
    {
    "name": "Post-launch",
    "name": "Post-launch",
    "duration": "Ongoing",
    "duration": "Ongoing",
    "activities": [
    "activities": [
    "Collect and showcase testimonials",
    "Collect and showcase testimonials",
    "Optimize based on user feedback",
    "Optimize based on user feedback",
    "Scale successful channels",
    "Scale successful channels",
    "Implement referral program",
    "Implement referral program",
    ],
    ],
    },
    },
    ]
    ]
    },
    },
    "kpis": {
    "kpis": {
    "awareness": [
    "awareness": [
    "Website traffic",
    "Website traffic",
    "Social media followers",
    "Social media followers",
    "Email subscribers",
    "Email subscribers",
    ],
    ],
    "acquisition": [
    "acquisition": [
    "Free trial signups",
    "Free trial signups",
    "Conversion rate",
    "Conversion rate",
    "Cost per acquisition",
    "Cost per acquisition",
    ],
    ],
    "retention": ["Churn rate", "Renewal rate", "User engagement"],
    "retention": ["Churn rate", "Renewal rate", "User engagement"],
    },
    },
    "created_at": format_datetime(datetime.now(), "%Y-%m-%dT%H:%M:%S.%fZ"),
    "created_at": format_datetime(datetime.now(), "%Y-%m-%dT%H:%M:%S.%fZ"),
    "updated_at": format_datetime(datetime.now(), "%Y-%m-%dT%H:%M:%S.%fZ"),
    "updated_at": format_datetime(datetime.now(), "%Y-%m-%dT%H:%M:%S.%fZ"),
    "status": "active",
    "status": "active",
    "is_mock": True,
    "is_mock": True,
    }
    }