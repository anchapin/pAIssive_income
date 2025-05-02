"""
User Personas module for the pAIssive Income project.
Provides tools for defining and understanding target user personas.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


class PersonaCreator:
    """
    Tool for creating detailed user personas for marketing campaigns.
    """

    def __init__(self):
        """Initialize the PersonaCreator."""
        self.name = "Persona Creator"
        self.description = "Creates detailed user personas for marketing campaigns"

    def create_persona(
        self,
        name: str,
        description: str,
        pain_points: List[str],
        goals: List[str],
        demographics: Dict[str, str],
        behaviors: List[str] = None,
        preferred_channels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a detailed user persona.

        Args:
            name: Name of the persona (e.g., "Professional YouTuber")
            description: Brief description of the persona
            pain_points: List of pain points the persona experiences
            goals: List of goals the persona wants to achieve
            demographics: Dictionary of demographic information
            behavior: Dictionary of behavioral traits
            preferred_channels: Optional list of preferred marketing channels

        Returns:
            A dictionary representing the user persona
        """
        # Create a unique ID for the persona
        persona_id = str(uuid.uuid4())

        # Create the persona dictionary
        persona = {
            "id": persona_id,
            "name": name,
            "description": description,
            "pain_points": pain_points,
            "goals": goals,
            "demographics": demographics,
            "behaviors": behaviors or [],
            "preferred_channels": preferred_channels or [],
            "created_at": datetime.now().isoformat(),
        }

        return persona

    def analyze_persona_market_fit(
        self, persona: Dict[str, Any], niche: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze how well a persona fits with a specific market niche.

        Args:
            persona: The user persona to analyze
            niche: The market niche to compare against

        Returns:
            A dictionary with the analysis results
        """
        # Calculate pain point overlap
        pain_point_overlap = [
            pain for pain in persona["pain_points"] if pain in niche["problem_areas"]
        ]
        pain_point_score = len(pain_point_overlap) / max(
            len(persona["pain_points"]), len(niche["problem_areas"]), 1
        )

        # Calculate overall fit score (0-1)
        fit_score = pain_point_score

        # TODO: Implement more sophisticated fit analysis based on demographics, behavior, etc.

        return {
            "persona_id": persona["id"],
            "niche_id": niche["id"],
            "pain_point_overlap": pain_point_overlap,
            "pain_point_score": pain_point_score,
            "overall_fit_score": fit_score,
            "recommendation": (
                "strong_fit"
                if fit_score > 0.7
                else "moderate_fit" if fit_score > 0.4 else "weak_fit"
            ),
        }


class DemographicAnalyzer:
    """
    Tool for analyzing demographic information for user personas.
    """

    def __init__(self):
        """Initialize the DemographicAnalyzer."""
        self.name = "Demographic Analyzer"
        self.description = "Analyzes demographic information for user personas"

    def analyze_demographics(
        self, demographics: Dict[str, Any], niche: str = None
    ) -> Dict[str, Any]:
        """
        Analyze demographics for a target audience.

        Args:
            demographics: Dictionary containing demographic information
            niche: Optional niche market to analyze for

        Returns:
            A dictionary with demographic analysis results
        """
        # Generate a unique ID for this analysis
        analysis_id = str(uuid.uuid4())

        # Extract demographic data
        age_range = demographics.get("age_range", "unknown")
        gender = demographics.get("gender", "unknown")
        location = demographics.get("location", "unknown")
        education = demographics.get("education", "unknown")
        income = demographics.get("income", "unknown")

        # Generate analysis based on demographics
        analysis = {
            "age_range": {
                "description": f"Target audience is in the {age_range} age range",
                "marketing_implications": self._get_age_implications(age_range),
            },
            "gender": {
                "description": f"Target audience gender is {gender}",
                "marketing_implications": self._get_gender_implications(gender),
            },
            "location": {
                "description": f"Target audience is primarily in {location} areas",
                "marketing_implications": self._get_location_implications(location),
            },
            "education": {
                "description": f"Target audience typically has {education} education level",
                "marketing_implications": self._get_education_implications(education),
            },
            "income": {
                "description": f"Target audience has {income} income level",
                "marketing_implications": self._get_income_implications(income),
            },
        }

        # Generate recommendations based on demographics
        recommendations = [
            f"Focus marketing efforts on {age_range} age group",
            f"Adjust messaging to appeal to {gender} audience",
            f"Consider {location}-specific marketing channels",
            f"Use language appropriate for {education} education level",
            f"Price products/services appropriately for {income} income level",
        ]

        if niche:
            recommendations.append(f"Tailor marketing to address specific needs of {niche} users")

        return {
            "id": analysis_id,
            "niche": niche or "general",
            "demographics": demographics,
            "analysis": analysis,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
        }

    def _count_occurrences(self, items: List[str]) -> Dict[str, int]:
        """
        Count occurrences of items in a list.

        Args:
            items: List of items to count

        Returns:
            Dictionary with counts of each item
        """
        result = {}
        for item in items:
            if item in result:
                result[item] += 1
            else:
                result[item] = 1
        return result

    def _get_age_implications(self, age_range: str) -> List[str]:
        """Get marketing implications for age range."""
        if "18-24" in age_range or "young" in age_range.lower():
            return [
                "Use social media platforms popular with younger audiences",
                "Emphasize mobile-first experiences",
                "Focus on trendy, visual content",
            ]
        elif "25-34" in age_range or "30" in age_range:
            return [
                "Balance social media with email marketing",
                "Focus on career advancement and efficiency",
                "Emphasize value and time-saving benefits",
            ]
        elif "35-44" in age_range or "40" in age_range:
            return [
                "Focus on professional networks and email",
                "Emphasize reliability and established solutions",
                "Address work-life balance concerns",
            ]
        elif "45" in age_range or "50" in age_range or "older" in age_range.lower():
            return [
                "Use more traditional marketing channels",
                "Focus on ease of use and customer support",
                "Address privacy and security concerns",
            ]
        else:
            return [
                "Use a mix of marketing channels",
                "Balance innovative features with ease of use",
                "Focus on universal benefits",
            ]

    def _get_gender_implications(self, gender: str) -> List[str]:
        """Get marketing implications for gender."""
        if gender.lower() == "male":
            return [
                "Consider male-oriented design elements",
                "Focus on direct, feature-oriented messaging",
                "Target platforms with higher male demographics",
            ]
        elif gender.lower() == "female":
            return [
                "Consider female-oriented design elements",
                "Focus on benefit-oriented messaging",
                "Target platforms with higher female demographics",
            ]
        else:  # mixed, non-binary, etc.
            return [
                "Use inclusive design and language",
                "Focus on universal benefits",
                "Test messaging across different audience segments",
            ]

    def _get_location_implications(self, location: str) -> List[str]:
        """Get marketing implications for location."""
        if location.lower() == "urban":
            return [
                "Focus on convenience and time-saving",
                "Consider higher price points",
                "Target urban-specific pain points",
            ]
        elif location.lower() == "suburban":
            return [
                "Balance value and quality messaging",
                "Focus on family and community benefits",
                "Consider moderate price points",
            ]
        elif location.lower() == "rural":
            return [
                "Emphasize reliability and practicality",
                "Consider connectivity limitations",
                "Focus on value and durability",
            ]
        else:
            return [
                "Use location-agnostic messaging",
                "Consider regional differences in marketing",
                "Test different approaches across locations",
            ]

    def _get_education_implications(self, education: str) -> List[str]:
        """Get marketing implications for education level."""
        if (
            "college" in education.lower()
            or "degree" in education.lower()
            or "higher" in education.lower()
        ):
            return [
                "Use more sophisticated language",
                "Include data and research in marketing",
                "Focus on advanced features and customization",
            ]
        elif "high school" in education.lower() or "basic" in education.lower():
            return [
                "Use clear, straightforward language",
                "Focus on practical benefits",
                "Emphasize ease of use and support",
            ]
        else:
            return [
                "Balance technical and accessible language",
                "Focus on universal benefits",
                "Include both basic and advanced use cases",
            ]

    def _get_income_implications(self, income: str) -> List[str]:
        """Get marketing implications for income level."""
        if "high" in income.lower() or "upper" in income.lower():
            return [
                "Focus on premium features and exclusivity",
                "Emphasize quality over cost",
                "Consider higher price points with premium positioning",
            ]
        elif "middle" in income.lower():
            return [
                "Balance value and quality messaging",
                "Offer tiered pricing options",
                "Focus on ROI and long-term benefits",
            ]
        elif "low" in income.lower():
            return [
                "Emphasize affordability and essential features",
                "Consider freemium models",
                "Focus on immediate value and necessity",
            ]
        else:
            return [
                "Offer flexible pricing options",
                "Focus on value for money",
                "Balance feature set with affordability",
            ]


class PainPointIdentifier:
    """
    Tool for identifying and analyzing pain points for user personas.
    """

    def __init__(self):
        """Initialize the PainPointIdentifier."""
        self.name = "Pain Point Identifier"
        self.description = "Identifies and analyzes pain points for user personas"

    def identify_pain_points(self, niche: Union[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify potential pain points for a specific niche.

        Args:
            niche: The market niche to analyze (string or dictionary)

        Returns:
            A list of pain points with severity and impact
        """
        # Handle string input (niche name)
        if isinstance(niche, str):
            niche_name = niche
            # Define common pain points for different niches
            niche_pain_points = {
                "e-commerce": [
                    {
                        "name": "Inventory Management",
                        "description": "Difficulty managing inventory levels across multiple platforms",
                        "severity": "high",
                        "impact": "Stockouts or excess inventory leading to lost sales or tied-up capital",
                        "current_solutions": {
                            "manual_processes": "Spreadsheets and manual tracking",
                            "basic_tools": "Basic inventory management software",
                            "enterprise_solutions": "Expensive enterprise solutions",
                        },
                        "solution_gaps": "Affordable, AI-powered inventory forecasting and management",
                    },
                    {
                        "name": "Product Descriptions",
                        "description": "Time-consuming process of writing unique product descriptions",
                        "severity": "medium",
                        "impact": "Generic descriptions leading to poor SEO and lower conversion rates",
                        "current_solutions": {
                            "manual_writing": "Manual writing by store owners",
                            "outsourcing": "Outsourcing to copywriters",
                            "templates": "Using templates with minor variations",
                        },
                        "solution_gaps": "AI-powered, unique product description generation",
                    },
                    {
                        "name": "Customer Support",
                        "description": "Managing customer inquiries efficiently",
                        "severity": "high",
                        "impact": "Slow response times leading to customer dissatisfaction",
                        "current_solutions": {
                            "manual_responses": "Manual email responses",
                            "basic_chatbots": "Basic rule-based chatbots",
                            "faq_pages": "FAQ pages requiring customer effort",
                        },
                        "solution_gaps": "AI-powered customer support automation with personalization",
                    },
                ],
                "content creation": [
                    {
                        "name": "Content Ideas",
                        "description": "Difficulty generating fresh content ideas consistently",
                        "severity": "high",
                        "impact": "Content gaps, inconsistent publishing, audience disengagement",
                        "current_solutions": {
                            "brainstorming": "Manual brainstorming sessions",
                            "competitor_research": "Researching competitor content",
                            "trend_monitoring": "Monitoring industry trends",
                        },
                        "solution_gaps": "AI-powered content idea generation based on audience interests",
                    },
                    {
                        "name": "SEO Optimization",
                        "description": "Optimizing content for search engines effectively",
                        "severity": "medium",
                        "impact": "Poor search rankings and reduced organic traffic",
                        "current_solutions": {
                            "keyword_research": "Manual keyword research tools",
                            "seo_plugins": "Basic SEO plugins and checkers",
                            "trial_and_error": "Trial and error approach",
                        },
                        "solution_gaps": "AI-powered SEO optimization with predictive analytics",
                    },
                ],
                "marketing": [
                    {
                        "name": "Campaign Planning",
                        "description": "Developing effective marketing campaigns",
                        "severity": "high",
                        "impact": "Ineffective campaigns and wasted marketing budget",
                        "current_solutions": {
                            "manual_planning": "Manual campaign planning",
                            "templates": "Using campaign templates",
                            "agency_services": "Expensive agency services",
                        },
                        "solution_gaps": "AI-powered campaign planning and optimization",
                    },
                    {
                        "name": "Performance Analysis",
                        "description": "Analyzing marketing performance across channels",
                        "severity": "medium",
                        "impact": "Difficulty identifying effective strategies and optimizing ROI",
                        "current_solutions": {
                            "manual_analysis": "Manual data analysis",
                            "basic_analytics": "Basic analytics tools",
                            "multiple_platforms": "Multiple disconnected platforms",
                        },
                        "solution_gaps": "Integrated AI-powered marketing analytics and insights",
                    },
                ],
            }

            # Return pain points for the specified niche or generic ones
            if niche_name.lower() in niche_pain_points:
                pain_points = []
                for pp in niche_pain_points[niche_name.lower()]:
                    pain_point = {
                        "id": str(uuid.uuid4()),
                        "name": pp["name"],
                        "description": pp["description"],
                        "severity": pp["severity"],
                        "impact": pp["impact"],
                        "current_solutions": pp["current_solutions"],
                        "solution_gaps": pp["solution_gaps"],
                    }
                    pain_points.append(pain_point)
                return pain_points
            else:
                # Return generic pain points for unknown niches
                return [
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Time Efficiency",
                        "description": f"Managing time effectively in {niche_name} activities",
                        "severity": "high",
                        "impact": "Reduced productivity and work-life balance issues",
                        "current_solutions": {
                            "manual_processes": "Manual time management",
                            "basic_tools": "Basic productivity tools",
                            "outsourcing": "Outsourcing when possible",
                        },
                        "solution_gaps": "AI-powered automation and time optimization",
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Quality Consistency",
                        "description": f"Maintaining consistent quality in {niche_name}",
                        "severity": "medium",
                        "impact": "Inconsistent results and customer satisfaction",
                        "current_solutions": {
                            "manual_checks": "Manual quality checks",
                            "basic_templates": "Basic templates and guidelines",
                            "training": "Staff training and documentation",
                        },
                        "solution_gaps": "AI-powered quality assurance and standardization",
                    },
                ]

        # Handle dictionary input (niche object)
        else:
            pain_points = []

            # Extract problem areas if available
            if "problem_areas" in niche:
                for i, problem in enumerate(niche["problem_areas"]):
                    # Calculate severity based on position in the list (first items are more severe)
                    severity = 1.0 - (i / max(len(niche["problem_areas"]), 1))
                    severity_level = (
                        "high" if severity > 0.7 else "medium" if severity > 0.4 else "low"
                    )

                    pain_points.append(
                        {
                            "id": str(uuid.uuid4()),
                            "name": f"Problem {i+1}",
                            "description": problem,
                            "severity": severity_level,
                            "impact": f"Significant impact on {niche.get('name', 'business')} operations",
                            "current_solutions": {
                                "manual_processes": "Users currently solve this manually",
                                "general_tools": "Users currently use general-purpose tools",
                                "outsourcing": "Users currently outsource this task",
                            },
                            "solution_gaps": f"AI-powered solution for {problem.lower()}",
                        }
                    )

            # If no problem areas found, return generic pain points
            if not pain_points:
                niche_name = niche.get("name", "this niche")
                return [
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Efficiency",
                        "description": f"Improving efficiency in {niche_name}",
                        "severity": "high",
                        "impact": "Reduced productivity and higher costs",
                        "current_solutions": {
                            "manual_processes": "Manual workflows",
                            "basic_tools": "Basic productivity tools",
                            "outsourcing": "Outsourcing to specialists",
                        },
                        "solution_gaps": "AI-powered automation and optimization",
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Decision Making",
                        "description": f"Making data-driven decisions in {niche_name}",
                        "severity": "medium",
                        "impact": "Suboptimal decisions and missed opportunities",
                        "current_solutions": {
                            "intuition": "Intuition-based decisions",
                            "basic_analytics": "Basic analytics tools",
                            "consultants": "Expensive consultants",
                        },
                        "solution_gaps": "AI-powered decision support and predictive analytics",
                    },
                ]

            return pain_points

    def analyze_pain_point(self, pain_point: Dict[str, Any], niche: str = None) -> Dict[str, Any]:
        """
        Analyze a specific pain point in detail.

        Args:
            pain_point: The pain point to analyze
            niche: Optional niche context for the analysis

        Returns:
            Detailed analysis of the pain point
        """
        # Generate a unique ID for this analysis
        analysis_id = str(uuid.uuid4())

        # Extract pain point information
        pain_point_id = pain_point.get("id", str(uuid.uuid4()))
        name = pain_point.get("name", "Unnamed Pain Point")
        description = pain_point.get("description", "")
        severity = pain_point.get("severity", "medium")
        impact = pain_point.get("impact", "")

        # Generate analysis based on severity
        if severity == "high":
            urgency = "High urgency - should be addressed immediately"
            market_opportunity = "Strong market opportunity"
            willingness_to_pay = "high"
        elif severity == "medium":
            urgency = "Medium urgency - should be addressed in the near term"
            market_opportunity = "Moderate market opportunity"
            willingness_to_pay = "medium"
        else:
            urgency = "Low urgency - can be addressed over time"
            market_opportunity = "Niche market opportunity"
            willingness_to_pay = "low"

        # Generate potential solutions
        potential_solutions = [
            {
                "name": f"AI-powered {name.lower()} assistant",
                "description": f"An AI tool that helps users with {description.lower()}",
                "implementation_complexity": "medium",
                "expected_impact": "high" if severity == "high" else "medium",
            },
            {
                "name": f"Automated {name.lower()} system",
                "description": f"A system that automates the process of {description.lower()}",
                "implementation_complexity": "high",
                "expected_impact": "high",
            },
            {
                "name": f"{name} templates and frameworks",
                "description": f"Pre-built templates and frameworks for {description.lower()}",
                "implementation_complexity": "low",
                "expected_impact": "medium",
            },
        ]

        # Create the analysis
        analysis = {
            "id": analysis_id,
            "pain_point_id": pain_point_id,
            "niche": niche or "general",
            "analysis": {
                "severity_assessment": severity,
                "urgency": urgency,
                "market_opportunity": market_opportunity,
                "root_causes": [
                    "Lack of specialized tools",
                    "Time constraints",
                    "Knowledge gaps",
                ],
                "impact_areas": [
                    "Productivity",
                    "Cost",
                    "Quality",
                    "Customer satisfaction",
                ],
            },
            "potential_solutions": potential_solutions,
            "user_willingness_to_pay": willingness_to_pay,
            "timestamp": datetime.now().isoformat(),
        }

        return analysis

    def categorize_pain_points(
        self, pain_points: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize pain points into different types.

        Args:
            pain_points: List of pain points to categorize

        Returns:
            Dictionary with pain points categorized by impact
        """
        categories = {"high_impact": [], "medium_impact": [], "low_impact": []}

        for pain_point in pain_points:
            if pain_point["impact"] == "high":
                categories["high_impact"].append(pain_point)
            elif pain_point["impact"] == "medium":
                categories["medium_impact"].append(pain_point)
            else:
                categories["low_impact"].append(pain_point)

        return categories


class GoalMapper:
    """
    Tool for mapping user goals to product features and marketing messages.
    """

    def __init__(self):
        """Initialize the GoalMapper."""

    def map_goals_to_features(
        self, persona: Dict[str, Any], solution: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Map user goals to product features.

        Args:
            persona: The user persona with goals
            solution: The product solution with features

        Returns:
            A list of mappings between goals and features
        """
        mappings = []

        for goal in persona["goals"]:
            relevant_features = []

            for feature in solution["features"]:
                # Simple relevance check - could be more sophisticated
                relevance = 0

                # Check if goal keywords appear in feature name or description
                goal_words = goal.lower().split()
                for word in goal_words:
                    if word in feature["name"].lower() or word in feature["description"].lower():
                        relevance += 1

                if relevance > 0:
                    relevant_features.append(
                        {
                            "feature_id": feature["id"],
                            "feature_name": feature["name"],
                            "relevance_score": relevance,
                        }
                    )

            mappings.append(
                {
                    "goal": goal,
                    "relevant_features": sorted(
                        relevant_features,
                        key=lambda x: x["relevance_score"],
                        reverse=True,
                    ),
                    "marketing_angles": [
                        f"Achieve {goal} faster with {solution['name']}",
                        f"How {solution['name']} helps you {goal.lower()}",
                        f"{goal.title()} made easy with {solution['name']}",
                    ],
                }
            )

        return mappings

    def generate_goal_based_messaging(
        self, persona: Dict[str, Any], solution: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Generate marketing messages based on user goals.

        Args:
            persona: The user persona with goals
            solution: The product solution

        Returns:
            Dictionary with marketing messages for different channels
        """
        messages = {
            "headlines": [],
            "email_subjects": [],
            "social_media": [],
            "value_propositions": [],
        }

        for goal in persona["goals"]:
            # Generate headlines
            messages["headlines"].append(f"Achieve {goal} with {solution['name']}")
            messages["headlines"].append(f"{solution['name']}: The key to {goal}")

            # Generate email subjects
            messages["email_subjects"].append(f"Want to {goal.lower()}? Try {solution['name']}")
            messages["email_subjects"].append(
                f"How {persona['name']}s are achieving {goal.lower()}"
            )

            # Generate social media posts
            messages["social_media"].append(
                f"Are you struggling to {goal.lower()}? {solution['name']} can help! #AI #Productivity"
            )
            messages["social_media"].append(
                f"See how {solution['name']} helps {persona['name']}s {goal.lower()} effortlessly. Try it today!"
            )

            # Generate value propositions
            messages["value_propositions"].append(
                f"{solution['name']} helps {persona['name']}s {goal.lower()} more efficiently"
            )
            messages["value_propositions"].append(
                f"Designed specifically to help you {goal.lower()}"
            )

        return messages


class BehaviorAnalyzer:
    """
    Tool for analyzing user behavior patterns and preferences.
    """

    def __init__(self):
        """Initialize the BehaviorAnalyzer."""

    def analyze_tech_adoption(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze technology adoption patterns for a persona.

        Args:
            persona: The user persona to analyze

        Returns:
            Analysis of technology adoption patterns
        """
        tech_savvy = persona["behavior"].get("tech_savvy", "medium")

        adoption_patterns = {
            "high": {
                "early_adopter": True,
                "requires_training": False,
                "prefers_advanced_features": True,
                "automation_comfort": "high",
                "ai_comfort": "high",
                "recommended_onboarding": "minimal",
                "feature_introduction_pace": "fast",
            },
            "medium": {
                "early_adopter": False,
                "requires_training": True,
                "prefers_advanced_features": False,
                "automation_comfort": "medium",
                "ai_comfort": "medium",
                "recommended_onboarding": "guided",
                "feature_introduction_pace": "moderate",
            },
            "low": {
                "early_adopter": False,
                "requires_training": True,
                "prefers_advanced_features": False,
                "automation_comfort": "low",
                "ai_comfort": "low",
                "recommended_onboarding": "extensive",
                "feature_introduction_pace": "slow",
            },
        }

        result = adoption_patterns.get(tech_savvy, adoption_patterns["medium"])
        result["tech_savvy_level"] = tech_savvy

        return result

    def analyze_price_sensitivity(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze price sensitivity for a persona.

        Args:
            persona: The user persona to analyze

        Returns:
            Analysis of price sensitivity
        """
        price_sensitivity = persona["behavior"].get("price_sensitivity", "medium")

        sensitivity_patterns = {
            "high": {
                "prefers_free_tier": True,
                "trial_importance": "critical",
                "discount_responsiveness": "high",
                "value_demonstration_needs": "extensive",
                "roi_focus": "strong",
                "recommended_pricing_strategy": "value-based with clear ROI",
                "upsell_difficulty": "high",
            },
            "medium": {
                "prefers_free_tier": True,
                "trial_importance": "important",
                "discount_responsiveness": "medium",
                "value_demonstration_needs": "moderate",
                "roi_focus": "moderate",
                "recommended_pricing_strategy": "competitive with clear benefits",
                "upsell_difficulty": "medium",
            },
            "low": {
                "prefers_free_tier": False,
                "trial_importance": "nice-to-have",
                "discount_responsiveness": "low",
                "value_demonstration_needs": "minimal",
                "roi_focus": "weak",
                "recommended_pricing_strategy": "premium with quality focus",
                "upsell_difficulty": "low",
            },
        }

        result = sensitivity_patterns.get(price_sensitivity, sensitivity_patterns["medium"])
        result["price_sensitivity_level"] = price_sensitivity

        return result

    def generate_behavior_based_recommendations(
        self, persona: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Generate recommendations based on user behavior.

        Args:
            persona: The user persona to analyze

        Returns:
            Dictionary with recommendations for product, marketing, and onboarding
        """
        tech_adoption = self.analyze_tech_adoption(persona)
        price_sensitivity = self.analyze_price_sensitivity(persona)

        recommendations = {
            "product_recommendations": [],
            "marketing_recommendations": [],
            "onboarding_recommendations": [],
        }

        # Product recommendations
        if tech_adoption["tech_savvy_level"] == "high":
            recommendations["product_recommendations"].append(
                "Include advanced features and customization options"
            )
            recommendations["product_recommendations"].append(
                "Provide API access and integration capabilities"
            )
        else:
            recommendations["product_recommendations"].append(
                "Focus on intuitive UI and simplified workflows"
            )
            recommendations["product_recommendations"].append(
                "Include templates and presets for common tasks"
            )

        # Marketing recommendations
        if price_sensitivity["price_sensitivity_level"] == "high":
            recommendations["marketing_recommendations"].append(
                "Emphasize ROI and cost savings in marketing materials"
            )
            recommendations["marketing_recommendations"].append("Offer free tier with upgrade path")
        else:
            recommendations["marketing_recommendations"].append(
                "Focus on quality and unique features in marketing"
            )
            recommendations["marketing_recommendations"].append(
                "Highlight premium aspects and exclusivity"
            )

        # Onboarding recommendations
        recommendations["onboarding_recommendations"].append(
            f"Provide {tech_adoption['recommended_onboarding']} onboarding"
        )
        recommendations["onboarding_recommendations"].append(
            f"Introduce features at a {tech_adoption['feature_introduction_pace']} pace"
        )

        return recommendations
