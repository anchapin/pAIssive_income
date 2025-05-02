"""
Test data utilities for API tests.

This module provides utilities for generating test data for API tests.
"""

import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict


def generate_id() -> str:
    """
    Generate a random ID.

    Returns:
        Random ID
    """
    return str(uuid.uuid4())


def generate_string(length: int = 10) -> str:
    """
    Generate a random string.

    Args:
        length: Length of the string

    Returns:
        Random string
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_email() -> str:
    """
    Generate a random email address.

    Returns:
        Random email address
    """
    return f"{generate_string(8)}@example.com"


def generate_date(days_ago: int = 0) -> str:
    """
    Generate a date string.

    Args:
        days_ago: Number of days ago

    Returns:
        Date string in ISO format
    """
    return (datetime.now() - timedelta(days=days_ago)).isoformat()


def generate_niche_analysis_data() -> Dict[str, Any]:
    """
    Generate test data for niche analysis.

    Returns:
        Test data for niche analysis
    """
    return {
        "market_segments": ["e-commerce", "digital-marketing", "education"],
        "target_audience": "small businesses",
        "problem_statement": "Small businesses struggle with inventory management",
        "opportunity_score_threshold": 0.7,
    }


def generate_niche_data() -> Dict[str, Any]:
    """
    Generate test data for a niche.

    Returns:
        Test data for a niche
    """
    return {
        "id": generate_id(),
        "name": f"AI {generate_string(8)} Solution",
        "description": f"An AI solution for {generate_string(12)}",
        "market_segments": ["e-commerce", "digital-marketing"],
        "target_audience": "small businesses",
        "problem_statement": f"Small businesses struggle with {generate_string(15)}",
        "opportunity_score": random.uniform(0.5, 1.0),
        "created_at": generate_date(10),
        "updated_at": generate_date(),
    }


def generate_monetization_data() -> Dict[str, Any]:
    """
    Generate test data for monetization.

    Returns:
        Test data for monetization
    """
    return {
        "subscription_type": random.choice(["freemium", "premium", "enterprise"]),
        "billing_period": random.choice(["monthly", "quarterly", "annual"]),
        "base_price": random.uniform(10, 100),
        "features": [
            {"name": f"Feature {i}", "description": f"Description for feature {i}"}
            for i in range(1, 6)
        ],
        "tiers": [
            {
                "name": "Basic",
                "price": random.uniform(10, 30),
                "features": ["Feature 1", "Feature 2"],
            },
            {
                "name": "Pro",
                "price": random.uniform(30, 70),
                "features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4"],
            },
            {
                "name": "Enterprise",
                "price": random.uniform(70, 150),
                "features": [
                    "Feature 1",
                    "Feature 2",
                    "Feature 3",
                    "Feature 4",
                    "Feature 5",
                ],
            },
        ],
    }


def generate_revenue_projection_data() -> Dict[str, Any]:
    """
    Generate test data for revenue projection.

    Returns:
        Test data for revenue projection
    """
    return {
        "subscription_model_id": generate_id(),
        "initial_users": random.randint(10, 100),
        "growth_rate": random.uniform(0.05, 0.2),
        "churn_rate": random.uniform(0.01, 0.1),
        "time_period_months": random.randint(12, 60),
    }


def generate_marketing_strategy_data() -> Dict[str, Any]:
    """
    Generate test data for marketing strategy.

    Returns:
        Test data for marketing strategy
    """
    return {
        "niche_id": generate_id(),
        "target_audience": {
            "demographics": {
                "age_range": [25, 45],
                "gender": "all",
                "income_level": "middle",
                "education_level": "college",
                "location": "global",
            },
            "psychographics": {
                "interests": ["technology", "business", "productivity"],
                "values": ["efficiency", "innovation", "cost-effectiveness"],
                "pain_points": [
                    "time management",
                    "resource allocation",
                    "cost control",
                ],
            },
        },
        "channels": [
            {
                "name": "Content Marketing",
                "priority": "high",
                "description": "Blog posts, whitepapers, case studies",
            },
            {
                "name": "Social Media",
                "priority": "medium",
                "description": "LinkedIn, Twitter, Facebook",
            },
            {
                "name": "Email Marketing",
                "priority": "high",
                "description": "Newsletter, drip campaigns",
            },
        ],
        "content_types": [
            "blog_posts",
            "case_studies",
            "webinars",
            "social_media_posts",
        ],
        "kpis": [
            "website_traffic",
            "lead_generation",
            "conversion_rate",
            "customer_acquisition_cost",
        ],
    }


def generate_ai_model_data() -> Dict[str, Any]:
    """
    Generate test data for AI model.

    Returns:
        Test data for AI model
    """
    return {
        "id": generate_id(),
        "name": f"Model-{generate_string(6)}",
        "description": f"An AI model for {generate_string(12)}",
        "model_type": random.choice(
            ["text-generation", "text-classification", "embedding", "image", "audio"]
        ),
        "provider": random.choice(["openai", "ollama", "lmstudio", "huggingface"]),
        "version": f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
        "capabilities": [
            random.choice(
                [
                    "text-generation",
                    "text-classification",
                    "embedding",
                    "image-generation",
                    "audio-transcription",
                ]
            )
            for _ in range(random.randint(1, 3))
        ],
        "parameters": {
            "temperature": random.uniform(0.1, 1.0),
            "max_tokens": random.randint(100, 2000),
            "top_p": random.uniform(0.1, 1.0),
        },
    }


def generate_agent_team_data() -> Dict[str, Any]:
    """
    Generate test data for agent team.

    Returns:
        Test data for agent team
    """
    return {
        "name": f"Team-{generate_string(6)}",
        "description": f"A team for {generate_string(12)}",
        "agents": [
            {
                "id": generate_id(),
                "name": f"Agent-{generate_string(4)}",
                "role": random.choice(
                    ["researcher", "developer", "monetization", "marketing"]
                ),
                "model_id": generate_id(),
                "capabilities": [
                    random.choice(
                        [
                            "market_analysis",
                            "problem_identification",
                            "solution_development",
                            "monetization_strategy",
                            "marketing_plan",
                        ]
                    )
                    for _ in range(random.randint(1, 3))
                ],
            }
            for _ in range(random.randint(2, 5))
        ],
        "workflow_settings": {
            "parallel_execution": random.choice([True, False]),
            "review_steps": random.choice([True, False]),
            "auto_correction": random.choice([True, False]),
        },
    }


def generate_user_data() -> Dict[str, Any]:
    """
    Generate test data for user.

    Returns:
        Test data for user
    """
    return {
        "username": generate_string(8),
        "email": generate_email(),
        "password": generate_string(12),
        "first_name": generate_string(6),
        "last_name": generate_string(8),
    }


def generate_api_key_data() -> Dict[str, Any]:
    """
    Generate test data for API key.

    Returns:
        Test data for API key
    """
    return {
        "name": f"Key-{generate_string(6)}",
        "description": f"API key for {generate_string(12)}",
        "permissions": [
            random.choice(["read", "write", "admin"])
            for _ in range(random.randint(1, 3))
        ],
        "expires_at": generate_date(-random.randint(30, 365)),
    }


def generate_webhook_data() -> Dict[str, Any]:
    """
    Generate test data for webhook.

    Returns:
        Test data for webhook
    """
    return {
        "url": f"https://example.com/webhook/{generate_string(8)}",
        "event_types": [
            random.choice(
                [
                    "niche.created",
                    "solution.created",
                    "monetization.created",
                    "marketing.created",
                ]
            )
            for _ in range(random.randint(1, 4))
        ],
        "description": f"Webhook for {generate_string(12)}",
        "is_active": random.choice([True, False]),
        "secret": generate_string(16),
    }


def generate_solution_data() -> Dict[str, Any]:
    """Generate test data for a solution."""
    return {
        "name": f"Test Solution {generate_id()}",
        "description": "A test solution for automated testing",
        "tech_stack": ["python", "fastapi", "react", "postgresql"],
        "niche_id": generate_id(),
        "template_id": generate_id(),
        "requirements": {
            "features": ["user_auth", "api", "database"],
            "scalability": "medium",
            "deployment": "cloud",
        },
    }


def generate_template_data() -> Dict[str, Any]:
    """Generate test data for a template."""
    return {
        "name": f"Test Template {generate_id()}",
        "description": "A test template for automated testing",
        "tech_stack": ["python", "fastapi", "react", "postgresql"],
        "features": ["user_auth", "api", "database"],
        "complexity": "medium",
        "estimated_time": "2-4 weeks",
        "requirements": {
            "min_experience": "intermediate",
            "team_size": "1-3",
            "tools": ["git", "docker", "vscode"],
        },
    }


def generate_monetization_strategy_data() -> Dict[str, Any]:
    """
    Generate test data for monetization strategy.

    Returns:
        Test data for monetization strategy
    """
    return {
        "id": generate_id(),
        "name": f"Strategy-{generate_string(6)}",
        "description": f"A monetization strategy for {generate_string(12)}",
        "model_type": random.choice(
            ["subscription", "freemium", "one-time", "usage-based"]
        ),
        "pricing_tiers": [
            {
                "name": "Basic",
                "price": random.uniform(10, 30),
                "features": ["Feature 1", "Feature 2"],
                "billing_cycle": random.choice(["monthly", "quarterly", "annual"]),
            },
            {
                "name": "Pro",
                "price": random.uniform(30, 70),
                "features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4"],
                "billing_cycle": random.choice(["monthly", "quarterly", "annual"]),
            },
            {
                "name": "Enterprise",
                "price": random.uniform(70, 150),
                "features": [
                    "Feature 1",
                    "Feature 2",
                    "Feature 3",
                    "Feature 4",
                    "Feature 5",
                ],
                "billing_cycle": random.choice(["monthly", "quarterly", "annual"]),
            },
        ],
        "revenue_projections": {
            "initial_users": random.randint(10, 100),
            "growth_rate": random.uniform(0.05, 0.2),
            "churn_rate": random.uniform(0.01, 0.1),
            "time_period_months": random.randint(12, 60),
        },
        "payment_providers": [
            random.choice(["stripe", "paypal", "braintree", "square"])
            for _ in range(random.randint(1, 3))
        ],
        "created_at": generate_date(10),
        "updated_at": generate_date(),
    }


def generate_ui_component_data() -> Dict[str, Any]:
    """
    Generate test data for UI component.

    Returns:
        Test data for UI component
    """
    return {
        "id": generate_id(),
        "name": f"Component-{generate_string(6)}",
        "description": f"A UI component for {generate_string(12)}",
        "type": random.choice(["button", "form", "card", "modal", "table", "chart"]),
        "framework": random.choice(["react", "vue", "angular", "svelte"]),
        "properties": {
            "color": random.choice(
                ["primary", "secondary", "success", "danger", "warning", "info"]
            ),
            "size": random.choice(["small", "medium", "large"]),
            "variant": random.choice(["outlined", "contained", "text"]),
            "disabled": random.choice([True, False]),
        },
        "events": [
            {
                "name": random.choice(["click", "hover", "focus", "blur"]),
                "description": f"Event triggered on {random.choice(['click', 'hover', 'focus', 'blur'])}",
            }
            for _ in range(random.randint(1, 4))
        ],
        "children": [
            {
                "id": generate_id(),
                "name": f"Child-{generate_string(4)}",
                "type": random.choice(["text", "icon", "image"]),
            }
            for _ in range(random.randint(0, 3))
        ],
        "styles": {
            "padding": f"{random.randint(0, 20)}px",
            "margin": f"{random.randint(0, 20)}px",
            "borderRadius": f"{random.randint(0, 10)}px",
            "backgroundColor": random.choice(
                ["#f5f5f5", "#e0e0e0", "#ffffff", "#000000"]
            ),
        },
        "created_at": generate_date(10),
        "updated_at": generate_date(),
    }
