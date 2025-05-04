"""
Marketing Service for the pAIssive Income UI.

This service provides methods for interacting with the Marketing Agent module.
"""

import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from agent_team.agent_profiles.marketing import MarketingAgent
from common_utils import add_days, format_datetime
from interfaces.ui_interfaces import IMarketingService

from .base_service import BaseService
from .developer_service import DeveloperService

from agent_team import AgentTeam


# Set up logging
logger = logging.getLogger(__name__)


class MarketingService(BaseService, IMarketingService):
    """
    Service for interacting with the Marketing Agent module.
    """

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
        Create a marketing campaign for a solution.

        Args:
            solution_id: ID of the solution

        Returns:
            Marketing campaign data
        """
        # Get the solution data
        developer_service = DeveloperService()
        solution = developer_service.get_solution(solution_id)

        if solution is None:
            logger.error(f"Solution with ID {solution_id} not found")
            return {}

        if self.marketing_agent_available:
            try:
                # Create a new agent team for this campaign
                team = AgentTeam(f"{solution['name']} Marketing")

                # Create the marketing campaign
                campaign = team.marketing.create_marketing_plan(solution)

                # Add metadata
                campaign["id"] = str(uuid.uuid4())
                campaign["solution_id"] = solution_id
                campaign["created_at"] = datetime.now().isoformat()
                campaign["updated_at"] = datetime.now().isoformat()
                campaign["status"] = "active"
            except Exception as e:
                logger.error(f"Error creating marketing campaign: {e}")
                campaign = self._create_mock_campaign(solution)
        else:
            campaign = self._create_mock_campaign(solution)

        # Save the campaign
        campaigns = self.get_campaigns()
        campaigns.append(campaign)
        self.save_data(self.campaigns_file, campaigns)

        return campaign

    def get_campaigns(self) -> List[Dict[str, Any]]:
        """
        Get all marketing campaigns.

        Returns:
            List of marketing campaigns
        """
        campaigns = self.load_data(self.campaigns_file)
        if campaigns is None:
            campaigns = []
            self.save_data(self.campaigns_file, campaigns)
        return campaigns

    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a marketing campaign by ID.

        Args:
            campaign_id: ID of the campaign

        Returns:
            Marketing campaign data, or None if not found
        """
        campaigns = self.get_campaigns()
        for campaign in campaigns:
            if campaign["id"] == campaign_id:
                return campaign
        return None

    def save_campaign(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a marketing campaign.

        Args:
            campaign: Campaign dictionary

        Returns:
            Saved campaign dictionary
        """
        campaigns = self.get_campaigns()

        # Check if the campaign already exists
        for i, existing_campaign in enumerate(campaigns):
            if existing_campaign["id"] == campaign["id"]:
                # Update existing campaign
                campaign["updated_at"] = datetime.now().isoformat()
                campaigns[i] = campaign
                self.save_data(self.campaigns_file, campaigns)
                return campaign

        # Add new campaign
        if "created_at" not in campaign:
            campaign["created_at"] = datetime.now().isoformat()
        if "updated_at" not in campaign:
            campaign["updated_at"] = datetime.now().isoformat()
        campaigns.append(campaign)
        self.save_data(self.campaigns_file, campaigns)
        return campaign

    def _create_mock_campaign(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a mock marketing campaign for testing.

        Args:
            solution: Solution data

        Returns:
            Mock marketing campaign data
        """
        # Create user personas
        personas = [
            {
                "id": str(uuid.uuid4()),
                "name": "Professional User",
                "demographics": {
                    "age_range": "25-45",
                    "gender": "all",
                    "education": "college degree or higher",
                    "income": "middle to upper",
                    "location": "global, urban areas",
                },
                "pain_points": [
                    "Time constraints",
                    "Need for high-quality output",
                    "Competitive pressure",
                ],
                "goals": [
                    "Increase productivity",
                    "Improve quality of work",
                    "Reduce costs",
                ],
                "behavior": {
                    "tech_savvy": "high",
                    "price_sensitivity": "medium",
                    "brand_loyalty": "medium",
                    "decision_making": "rational",
                },
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Hobbyist User",
                "demographics": {
                    "age_range": "18-65",
                    "gender": "all",
                    "education": "varied",
                    "income": "varied",
                    "location": "global",
                },
                "pain_points": [
                    "Limited skills",
                    "Budget constraints",
                    "Learning curve",
                ],
                "goals": [
                    "Create professional-looking output",
                    "Learn new skills",
                    "Express creativity",
                ],
                "behavior": {
                    "tech_savvy": "medium",
                    "price_sensitivity": "high",
                    "brand_loyalty": "low",
                    "decision_making": "emotional",
                },
            },
        ]

        # Create channel strategies
        channels = [
            {
                "id": str(uuid.uuid4()),
                "name": "Content Marketing",
                "description": "Create valuable content to attract and engage target audience",
                "platforms": ["Blog", "YouTube", "Medium"],
                "content_types": ["Tutorials", "Case studies", "How-to guides"],
                "kpis": ["Website traffic", "Time on page", "Conversion rate"],
                "budget_allocation": "30%",
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Social Media Marketing",
                "description": "Engage with audience on social platforms",
                "platforms": ["Twitter", "LinkedIn", "Instagram"],
                "content_types": [
                    "Tips and tricks",
                    "Success stories",
                    "Product updates",
                ],
                "kpis": ["Followers", "Engagement rate", "Click-through rate"],
                "budget_allocation": "25%",
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Email Marketing",
                "description": "Nurture leads and retain customers through email",
                "platforms": ["Mailchimp", "ConvertKit"],
                "content_types": [
                    "Newsletters",
                    "Product announcements",
                    "Tips and resources",
                ],
                "kpis": ["Open rate", "Click-through rate", "Conversion rate"],
                "budget_allocation": "20%",
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Influencer Marketing",
                "description": "Partner with influencers in the niche",
                "platforms": ["YouTube", "Instagram", "TikTok"],
                "content_types": ["Reviews", "Tutorials", "Testimonials"],
                "kpis": ["Reach", "Engagement", "Conversions"],
                "budget_allocation": "15%",
            },
            {
                "id": str(uuid.uuid4()),
                "name": "SEO",
                "description": "Optimize for search engines to drive organic traffic",
                "platforms": ["Google", "Bing"],
                "content_types": ["Blog posts", "Landing pages", "FAQ pages"],
                "kpis": ["Organic traffic", "Keyword rankings", "Conversion rate"],
                "budget_allocation": "10%",
            },
        ]

        # Create content templates
        content_templates = [
            {
                "id": str(uuid.uuid4()),
                "name": "Blog Post Template",
                "description": "Template for creating blog posts",
                "content_type": "blog_post",
                "target_persona": personas[0]["name"],
                "tone": "professional",
                "sections": [
                    "Introduction",
                    "Problem statement",
                    "Solution overview",
                    "Step-by-step guide",
                    "Benefits",
                    "Case study/example",
                    "Conclusion with call to action",
                ],
                "estimated_length": "1500-2000 words",
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Social Media Template",
                "description": "Template for creating social media posts",
                "content_type": "social_media",
                "target_persona": personas[1]["name"],
                "tone": "casual",
                "sections": [
                    "Attention-grabbing headline",
                    "Value proposition",
                    "Social proof",
                    "Call to action",
                ],
                "estimated_length": "50-100 words",
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Email Newsletter Template",
                "description": "Template for creating email newsletters",
                "content_type": "email_newsletter",
                "target_persona": personas[0]["name"],
                "tone": "professional",
                "sections": [
                    "Personalized greeting",
                    "Value-packed introduction",
                    "Main content with tips or news",
                    "Product spotlight",
                    "Call to action",
                    "Footer with contact information",
                ],
                "estimated_length": "500-700 words",
            },
        ]

        # Create mock campaign
        return {
            "id": str(uuid.uuid4()),
            "name": f"{solution['name']} Marketing Campaign",
            "description": f"Marketing campaign for {solution['name']}",
            "solution_id": solution["id"],
            "target_audience": {
                "primary_persona": personas[0],
                "secondary_persona": personas[1],
            },
            "value_proposition": f"Help users save time and improve quality with AI-powered {solution['name'].lower()}",
            "channel_strategy": {
                "primary_channels": channels[:3],
                "secondary_channels": channels[3:],
                "budget": {
                    "total": "$5000",
                    "allocation": {
                        channel["name"]: channel["budget_allocation"]
                        for channel in channels
                    },
                },
            },
            "content_strategy": {
                "themes": [
                    "Productivity enhancement",
                    "Quality improvement",
                    "Cost reduction",
                    "Competitive advantage",
                ],
                "content_calendar": {
                    "frequency": {
                        "blog_posts": "weekly",
                        "social_media": "daily",
                        "email_newsletters": "bi-weekly",
                    },
                    "upcoming_content": [
                        {
                            "title": f"How {solution['name']} Can Save You 10 Hours a Week",
                            "type": "blog_post",
                            "publish_date": format_datetime(
                                add_days(datetime.now(), 7), "%Y-%m-%dT%H:%M:%S.%fZ"
                            ),
                            "status": "planned",
                        },
                        {
                            "title": f"5 Ways {solution['name']} Improves Your Work Quality",
                            "type": "blog_post",
                            "publish_date": format_datetime(
                                add_days(datetime.now(), 14), "%Y-%m-%dT%H:%M:%S.%fZ"
                            ),
                            "status": "planned",
                        },
                        {
                            "title": f"Welcome to {solution['name']}",
                            "type": "email_newsletter",
                            "publish_date": format_datetime(
                                add_days(datetime.now(), 1), "%Y-%m-%dT%H:%M:%S.%fZ"
                            ),
                            "status": "planned",
                        },
                    ],
                },
                "content_templates": content_templates,
            },
            "launch_plan": {
                "phases": [
                    {
                        "name": "Pre-launch",
                        "duration": "4 weeks",
                        "activities": [
                            "Create landing page",
                            "Set up email list",
                            "Prepare launch content",
                            "Reach out to influencers",
                        ],
                    },
                    {
                        "name": "Launch",
                        "duration": "2 weeks",
                        "activities": [
                            "Announce on all channels",
                            "Run limited-time promotion",
                            "Host webinar or live demo",
                            "Engage with early adopters",
                        ],
                    },
                    {
                        "name": "Post-launch",
                        "duration": "Ongoing",
                        "activities": [
                            "Collect and showcase testimonials",
                            "Optimize based on user feedback",
                            "Scale successful channels",
                            "Implement referral program",
                        ],
                    },
                ]
            },
            "kpis": {
                "awareness": [
                    "Website traffic",
                    "Social media followers",
                    "Email subscribers",
                ],
                "acquisition": [
                    "Free trial signups",
                    "Conversion rate",
                    "Cost per acquisition",
                ],
                "retention": ["Churn rate", "Renewal rate", "User engagement"],
            },
            "created_at": format_datetime(datetime.now(), "%Y-%m-%dT%H:%M:%S.%fZ"),
            "updated_at": format_datetime(datetime.now(), "%Y-%m-%dT%H:%M:%S.%fZ"),
            "status": "active",
            "is_mock": True,
        }
