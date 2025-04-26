"""
Opportunity Scorer for the pAIssive Income project.
Scores niche opportunities based on various factors.
"""

from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime


class OpportunityScorer:
    """
    Scores niche opportunities based on various factors to identify the most promising niches.
    """

    def __init__(self):
        """Initialize the Opportunity Scorer."""
        self.name = "Opportunity Scorer"
        self.description = "Scores niche opportunities based on various factors"
        
        # Define scoring weights
        self.weights = {
            "market_size": 0.15,
            "growth_rate": 0.15,
            "competition": 0.15,
            "problem_severity": 0.20,
            "solution_feasibility": 0.15,
            "monetization_potential": 0.20,
        }
    
    def score_opportunity(self, niche: str, market_data: Dict[str, Any], problems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Score a niche opportunity based on market data and identified problems.

        Args:
            niche: Niche to score
            market_data: Market data for the niche from MarketAnalyzer
            problems: List of problems in the niche from ProblemIdentifier

        Returns:
            Opportunity score and analysis
        """
        # In a real implementation, this would use AI to score the opportunity
        # For now, we'll return a placeholder implementation
        
        # Calculate scores for each factor
        market_size_score = self._score_market_size(market_data.get("market_size", "unknown"))
        growth_rate_score = self._score_growth_rate(market_data.get("growth_rate", "unknown"))
        competition_score = self._score_competition(market_data.get("competition", "unknown"))
        problem_severity_score = self._score_problem_severity(problems)
        solution_feasibility_score = self._score_solution_feasibility(niche, problems)
        monetization_potential_score = self._score_monetization_potential(niche, market_data, problems)
        
        # Calculate weighted score
        weighted_score = (
            market_size_score * self.weights["market_size"] +
            growth_rate_score * self.weights["growth_rate"] +
            competition_score * self.weights["competition"] +
            problem_severity_score * self.weights["problem_severity"] +
            solution_feasibility_score * self.weights["solution_feasibility"] +
            monetization_potential_score * self.weights["monetization_potential"]
        )
        
        # Round to 2 decimal places
        weighted_score = round(weighted_score, 2)
        
        return {
            "id": str(uuid.uuid4()),
            "niche": niche,
            "overall_score": weighted_score,
            "factor_scores": {
                "market_size": {
                    "score": market_size_score,
                    "weight": self.weights["market_size"],
                    "weighted_score": round(market_size_score * self.weights["market_size"], 2),
                    "analysis": f"The market size is {market_data.get('market_size', 'unknown')}",
                },
                "growth_rate": {
                    "score": growth_rate_score,
                    "weight": self.weights["growth_rate"],
                    "weighted_score": round(growth_rate_score * self.weights["growth_rate"], 2),
                    "analysis": f"The growth rate is {market_data.get('growth_rate', 'unknown')}",
                },
                "competition": {
                    "score": competition_score,
                    "weight": self.weights["competition"],
                    "weighted_score": round(competition_score * self.weights["competition"], 2),
                    "analysis": f"The competition level is {market_data.get('competition', 'unknown')}",
                },
                "problem_severity": {
                    "score": problem_severity_score,
                    "weight": self.weights["problem_severity"],
                    "weighted_score": round(problem_severity_score * self.weights["problem_severity"], 2),
                    "analysis": f"The problems in this niche are {'severe' if problem_severity_score > 0.7 else 'moderate' if problem_severity_score > 0.4 else 'minor'}",
                },
                "solution_feasibility": {
                    "score": solution_feasibility_score,
                    "weight": self.weights["solution_feasibility"],
                    "weighted_score": round(solution_feasibility_score * self.weights["solution_feasibility"], 2),
                    "analysis": f"Creating an AI solution for this niche is {'highly feasible' if solution_feasibility_score > 0.7 else 'moderately feasible' if solution_feasibility_score > 0.4 else 'challenging'}",
                },
                "monetization_potential": {
                    "score": monetization_potential_score,
                    "weight": self.weights["monetization_potential"],
                    "weighted_score": round(monetization_potential_score * self.weights["monetization_potential"], 2),
                    "analysis": f"The monetization potential is {'high' if monetization_potential_score > 0.7 else 'medium' if monetization_potential_score > 0.4 else 'low'}",
                },
            },
            "opportunity_assessment": self._get_opportunity_assessment(weighted_score),
            "recommended_next_steps": self._get_recommended_next_steps(weighted_score),
            "timestamp": datetime.now().isoformat(),
        }
    
    def _score_market_size(self, market_size: str) -> float:
        """
        Score the market size factor.

        Args:
            market_size: Market size (large, medium, small, unknown)

        Returns:
            Score between 0 and 1
        """
        if market_size.lower() == "large":
            return 0.9
        elif market_size.lower() == "medium":
            return 0.6
        elif market_size.lower() == "small":
            return 0.3
        else:
            return 0.5  # Unknown
    
    def _score_growth_rate(self, growth_rate: str) -> float:
        """
        Score the growth rate factor.

        Args:
            growth_rate: Growth rate (high, medium, low, unknown)

        Returns:
            Score between 0 and 1
        """
        if growth_rate.lower() == "high":
            return 0.9
        elif growth_rate.lower() == "medium":
            return 0.6
        elif growth_rate.lower() == "low":
            return 0.3
        else:
            return 0.5  # Unknown
    
    def _score_competition(self, competition: str) -> float:
        """
        Score the competition factor.

        Args:
            competition: Competition level (high, medium, low, unknown)

        Returns:
            Score between 0 and 1
        """
        # Note: Lower competition is better, so the scoring is inverted
        if competition.lower() == "high":
            return 0.3
        elif competition.lower() == "medium":
            return 0.6
        elif competition.lower() == "low":
            return 0.9
        else:
            return 0.5  # Unknown
    
    def _score_problem_severity(self, problems: List[Dict[str, Any]]) -> float:
        """
        Score the problem severity factor.

        Args:
            problems: List of problems in the niche

        Returns:
            Score between 0 and 1
        """
        if not problems:
            return 0.5  # No problems identified
        
        # Calculate average severity
        severity_scores = []
        for problem in problems:
            severity = problem.get("severity", "medium").lower()
            if severity == "high":
                severity_scores.append(0.9)
            elif severity == "medium":
                severity_scores.append(0.6)
            elif severity == "low":
                severity_scores.append(0.3)
            else:
                severity_scores.append(0.5)  # Unknown
        
        return sum(severity_scores) / len(severity_scores) if severity_scores else 0.5
    
    def _score_solution_feasibility(self, niche: str, problems: List[Dict[str, Any]]) -> float:
        """
        Score the solution feasibility factor.

        Args:
            niche: Niche to score
            problems: List of problems in the niche

        Returns:
            Score between 0 and 1
        """
        # In a real implementation, this would use AI to assess feasibility
        # For now, we'll return a placeholder implementation
        
        # Example feasibility scores for different niches
        niche_feasibility = {
            "inventory management for small e-commerce": 0.8,
            "product description generation": 0.9,
            "youtube script generation": 0.9,
            "blog post optimization": 0.8,
            "freelance proposal writing": 0.9,
            "client communication assistant": 0.7,
            "study note generation": 0.8,
            "personalized learning path creator": 0.7,
            "property description generator": 0.9,
            "market analysis assistant": 0.7,
        }
        
        return niche_feasibility.get(niche.lower(), 0.7)  # Default to 0.7 if not found
    
    def _score_monetization_potential(self, niche: str, market_data: Dict[str, Any], problems: List[Dict[str, Any]]) -> float:
        """
        Score the monetization potential factor.

        Args:
            niche: Niche to score
            market_data: Market data for the niche
            problems: List of problems in the niche

        Returns:
            Score between 0 and 1
        """
        # In a real implementation, this would use AI to assess monetization potential
        # For now, we'll return a placeholder implementation
        
        # Example monetization potential scores for different niches
        niche_monetization = {
            "inventory management for small e-commerce": 0.9,
            "product description generation": 0.8,
            "youtube script generation": 0.8,
            "blog post optimization": 0.7,
            "freelance proposal writing": 0.8,
            "client communication assistant": 0.7,
            "study note generation": 0.7,
            "personalized learning path creator": 0.8,
            "property description generator": 0.8,
            "market analysis assistant": 0.9,
        }
        
        return niche_monetization.get(niche.lower(), 0.7)  # Default to 0.7 if not found
    
    def _get_opportunity_assessment(self, score: float) -> str:
        """
        Get an opportunity assessment based on the overall score.

        Args:
            score: Overall opportunity score

        Returns:
            Opportunity assessment
        """
        if score >= 0.8:
            return "Excellent opportunity with high potential for success"
        elif score >= 0.7:
            return "Very good opportunity with strong potential for success"
        elif score >= 0.6:
            return "Good opportunity with moderate potential for success"
        elif score >= 0.5:
            return "Fair opportunity with some potential for success"
        else:
            return "Limited opportunity with challenges to overcome"
    
    def _get_recommended_next_steps(self, score: float) -> List[str]:
        """
        Get recommended next steps based on the overall score.

        Args:
            score: Overall opportunity score

        Returns:
            List of recommended next steps
        """
        if score >= 0.8:
            return [
                "Proceed with detailed solution design",
                "Develop a comprehensive monetization strategy",
                "Create a marketing plan",
                "Begin development of an MVP",
            ]
        elif score >= 0.7:
            return [
                "Conduct additional market research to validate findings",
                "Develop a solution design",
                "Create a monetization strategy",
                "Begin planning for MVP development",
            ]
        elif score >= 0.6:
            return [
                "Conduct deeper market research to identify specific opportunities",
                "Analyze competition more thoroughly",
                "Develop a preliminary solution design",
                "Assess technical feasibility in more detail",
            ]
        elif score >= 0.5:
            return [
                "Reconsider the niche focus to identify more specific opportunities",
                "Conduct user interviews to better understand problems",
                "Analyze competition to identify gaps",
                "Consider alternative approaches to the solution",
            ]
        else:
            return [
                "Consider exploring different niches with higher potential",
                "If proceeding, conduct extensive market research",
                "Identify specific sub-niches that may have higher potential",
                "Develop a unique value proposition to overcome competition",
            ]
    
    def compare_opportunities(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple opportunities to identify the most promising ones.

        Args:
            opportunities: List of opportunity scores from score_opportunity

        Returns:
            Comparison of opportunities
        """
        if not opportunities:
            return {
                "id": str(uuid.uuid4()),
                "opportunities_count": 0,
                "ranked_opportunities": [],
                "top_recommendation": None,
                "timestamp": datetime.now().isoformat(),
            }
        
        # Sort opportunities by overall score
        ranked_opportunities = sorted(
            opportunities,
            key=lambda x: x["overall_score"],
            reverse=True
        )
        
        # Get top recommendation
        top_recommendation = ranked_opportunities[0] if ranked_opportunities else None
        
        return {
            "id": str(uuid.uuid4()),
            "opportunities_count": len(opportunities),
            "ranked_opportunities": [
                {
                    "niche": opp["niche"],
                    "overall_score": opp["overall_score"],
                    "rank": i + 1,
                }
                for i, opp in enumerate(ranked_opportunities)
            ],
            "top_recommendation": {
                "niche": top_recommendation["niche"],
                "overall_score": top_recommendation["overall_score"],
                "assessment": top_recommendation["opportunity_assessment"],
                "next_steps": top_recommendation["recommended_next_steps"],
            } if top_recommendation else None,
            "comparative_analysis": {
                "highest_score": max(opp["overall_score"] for opp in opportunities) if opportunities else None,
                "lowest_score": min(opp["overall_score"] for opp in opportunities) if opportunities else None,
                "average_score": sum(opp["overall_score"] for opp in opportunities) / len(opportunities) if opportunities else None,
                "score_distribution": {
                    "excellent": sum(1 for opp in opportunities if opp["overall_score"] >= 0.8),
                    "very_good": sum(1 for opp in opportunities if 0.7 <= opp["overall_score"] < 0.8),
                    "good": sum(1 for opp in opportunities if 0.6 <= opp["overall_score"] < 0.7),
                    "fair": sum(1 for opp in opportunities if 0.5 <= opp["overall_score"] < 0.6),
                    "limited": sum(1 for opp in opportunities if opp["overall_score"] < 0.5),
                },
            },
            "timestamp": datetime.now().isoformat(),
        }
    
    def __str__(self) -> str:
        """String representation of the Opportunity Scorer."""
        return f"{self.name}: {self.description}"
