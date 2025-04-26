"""
Marketing package for the pAIssive Income project.

This package provides tools and templates for marketing AI-powered software tools
to target users in specific niches.
"""

from .user_personas import PersonaCreator, DemographicAnalyzer, PainPointIdentifier, GoalMapper, BehaviorAnalyzer
from .channel_strategies import (
    MarketingStrategy, 
    ContentMarketingStrategy, 
    SocialMediaStrategy, 
    EmailMarketingStrategy
)
from .content_templates import (
    ContentTemplate,
    BlogPostTemplate,
    SocialMediaTemplate,
    EmailNewsletterTemplate,
    VideoScriptTemplate,
    LandingPageTemplate,
    ProductDescriptionTemplate,
    CaseStudyTemplate,
    TestimonialTemplate
)

__all__ = [
    # User Personas
    'PersonaCreator',
    'DemographicAnalyzer',
    'PainPointIdentifier',
    'GoalMapper',
    'BehaviorAnalyzer',
    
    # Channel Strategies
    'MarketingStrategy',
    'ContentMarketingStrategy',
    'SocialMediaStrategy',
    'EmailMarketingStrategy',
    
    # Content Templates
    'ContentTemplate',
    'BlogPostTemplate',
    'SocialMediaTemplate',
    'EmailNewsletterTemplate',
    'VideoScriptTemplate',
    'LandingPageTemplate',
    'ProductDescriptionTemplate',
    'CaseStudyTemplate',
    'TestimonialTemplate',
]
