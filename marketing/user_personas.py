"""
User Personas module for the pAIssive Income project.
Provides tools for defining and understanding target user personas.
"""

from typing import Dict, List, Any, Optional, Union
import uuid
from datetime import datetime


class PersonaCreator:
    """
    Tool for creating detailed user personas for marketing campaigns.
    """

    def __init__(self):
        """Initialize the PersonaCreator."""
        pass

    def create_persona(
        self,
        name: str,
        description: str,
        pain_points: List[str],
        goals: List[str],
        demographics: Dict[str, str],
        behavior: Dict[str, str],
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
            "behavior": behavior,
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
            "recommendation": "strong_fit" if fit_score > 0.7 else "moderate_fit" if fit_score > 0.4 else "weak_fit",
        }


class DemographicAnalyzer:
    """
    Tool for analyzing demographic information for user personas.
    """

    def __init__(self):
        """Initialize the DemographicAnalyzer."""
        pass

    def analyze_demographics(self, personas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze demographics across multiple personas to identify patterns.

        Args:
            personas: List of user personas to analyze

        Returns:
            A dictionary with demographic analysis results
        """
        # Extract demographic data
        age_ranges = [p["demographics"].get("age_range", "unknown") for p in personas]
        education_levels = [p["demographics"].get("education", "unknown") for p in personas]
        income_levels = [p["demographics"].get("income", "unknown") for p in personas]

        # Count occurrences
        age_distribution = self._count_occurrences(age_ranges)
        education_distribution = self._count_occurrences(education_levels)
        income_distribution = self._count_occurrences(income_levels)

        # TODO: Implement more sophisticated demographic analysis

        return {
            "age_distribution": age_distribution,
            "education_distribution": education_distribution,
            "income_distribution": income_distribution,
            "total_personas": len(personas),
            "analysis_timestamp": datetime.now().isoformat(),
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


class PainPointIdentifier:
    """
    Tool for identifying and analyzing pain points for user personas.
    """

    def __init__(self):
        """Initialize the PainPointIdentifier."""
        pass

    def identify_pain_points(self, niche: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify potential pain points for a specific niche.

        Args:
            niche: The market niche to analyze

        Returns:
            A list of pain points with severity and impact
        """
        # Start with the problem areas from the niche
        pain_points = []
        
        for i, problem in enumerate(niche["problem_areas"]):
            # Calculate severity based on position in the list (first items are more severe)
            severity = 1.0 - (i / max(len(niche["problem_areas"]), 1))
            
            pain_points.append({
                "id": str(uuid.uuid4()),
                "description": problem,
                "severity": severity,
                "impact": "high" if severity > 0.7 else "medium" if severity > 0.4 else "low",
                "potential_solutions": [
                    f"Automate {problem.lower()} process",
                    f"Provide templates for {problem.lower()}",
                    f"Offer AI assistance for {problem.lower()}"
                ]
            })
        
        # TODO: Implement more sophisticated pain point analysis
        
        return pain_points

    def categorize_pain_points(self, pain_points: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize pain points into different types.

        Args:
            pain_points: List of pain points to categorize

        Returns:
            Dictionary with pain points categorized by impact
        """
        categories = {
            "high_impact": [],
            "medium_impact": [],
            "low_impact": []
        }
        
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
        pass

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
                    relevant_features.append({
                        "feature_id": feature["id"],
                        "feature_name": feature["name"],
                        "relevance_score": relevance
                    })
            
            mappings.append({
                "goal": goal,
                "relevant_features": sorted(relevant_features, key=lambda x: x["relevance_score"], reverse=True),
                "marketing_angles": [
                    f"Achieve {goal} faster with {solution['name']}",
                    f"How {solution['name']} helps you {goal.lower()}",
                    f"{goal.title()} made easy with {solution['name']}"
                ]
            })
        
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
            "value_propositions": []
        }
        
        for goal in persona["goals"]:
            # Generate headlines
            messages["headlines"].append(f"Achieve {goal} with {solution['name']}")
            messages["headlines"].append(f"{solution['name']}: The key to {goal}")
            
            # Generate email subjects
            messages["email_subjects"].append(f"Want to {goal.lower()}? Try {solution['name']}")
            messages["email_subjects"].append(f"How {persona['name']}s are achieving {goal.lower()}")
            
            # Generate social media posts
            messages["social_media"].append(f"Are you struggling to {goal.lower()}? {solution['name']} can help! #AI #Productivity")
            messages["social_media"].append(f"See how {solution['name']} helps {persona['name']}s {goal.lower()} effortlessly. Try it today!")
            
            # Generate value propositions
            messages["value_propositions"].append(f"{solution['name']} helps {persona['name']}s {goal.lower()} more efficiently")
            messages["value_propositions"].append(f"Designed specifically to help you {goal.lower()}")
        
        return messages


class BehaviorAnalyzer:
    """
    Tool for analyzing user behavior patterns and preferences.
    """

    def __init__(self):
        """Initialize the BehaviorAnalyzer."""
        pass

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
                "feature_introduction_pace": "fast"
            },
            "medium": {
                "early_adopter": False,
                "requires_training": True,
                "prefers_advanced_features": False,
                "automation_comfort": "medium",
                "ai_comfort": "medium",
                "recommended_onboarding": "guided",
                "feature_introduction_pace": "moderate"
            },
            "low": {
                "early_adopter": False,
                "requires_training": True,
                "prefers_advanced_features": False,
                "automation_comfort": "low",
                "ai_comfort": "low",
                "recommended_onboarding": "extensive",
                "feature_introduction_pace": "slow"
            }
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
                "upsell_difficulty": "high"
            },
            "medium": {
                "prefers_free_tier": True,
                "trial_importance": "important",
                "discount_responsiveness": "medium",
                "value_demonstration_needs": "moderate",
                "roi_focus": "moderate",
                "recommended_pricing_strategy": "competitive with clear benefits",
                "upsell_difficulty": "medium"
            },
            "low": {
                "prefers_free_tier": False,
                "trial_importance": "nice-to-have",
                "discount_responsiveness": "low",
                "value_demonstration_needs": "minimal",
                "roi_focus": "weak",
                "recommended_pricing_strategy": "premium with quality focus",
                "upsell_difficulty": "low"
            }
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
            "onboarding_recommendations": []
        }
        
        # Product recommendations
        if tech_adoption["tech_savvy_level"] == "high":
            recommendations["product_recommendations"].append("Include advanced features and customization options")
            recommendations["product_recommendations"].append("Provide API access and integration capabilities")
        else:
            recommendations["product_recommendations"].append("Focus on intuitive UI and simplified workflows")
            recommendations["product_recommendations"].append("Include templates and presets for common tasks")
        
        # Marketing recommendations
        if price_sensitivity["price_sensitivity_level"] == "high":
            recommendations["marketing_recommendations"].append("Emphasize ROI and cost savings in marketing materials")
            recommendations["marketing_recommendations"].append("Offer free tier with upgrade path")
        else:
            recommendations["marketing_recommendations"].append("Focus on quality and unique features in marketing")
            recommendations["marketing_recommendations"].append("Highlight premium aspects and exclusivity")
        
        # Onboarding recommendations
        recommendations["onboarding_recommendations"].append(f"Provide {tech_adoption['recommended_onboarding']} onboarding")
        recommendations["onboarding_recommendations"].append(f"Introduce features at a {tech_adoption['feature_introduction_pace']} pace")
        
        return recommendations
