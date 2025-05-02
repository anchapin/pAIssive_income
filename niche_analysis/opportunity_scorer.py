"""
Opportunity Scorer for the pAIssive Income project.
Scores niche opportunities based on various factors.
"""

import asyncio
import hashlib
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

# Import async utilities
from ai_models.async_utils import run_in_thread

# Import the centralized caching service
from common_utils.caching import default_cache

from .schemas import (
    ComparativeAnalysisSchema,
    FactorScoreSchema,
    FactorScoresSchema,
    FactorsSchema,
    OpportunityComparisonSchema,
    OpportunityScoreSchema,
    RankedOpportunitySchema,
    ScoreDistributionSchema,
    TopRecommendationSchema,
)


class OpportunityScorer:
    """
    OpportunityScorer class for scoring niche opportunities.

    This class evaluates niche opportunities based on various factors and provides
    methods for scoring individual opportunities and comparing multiple opportunities.
    The scoring algorithm considers six main factors:

    1. Market size: The potential size of the market for the niche
    2. Growth rate: The growth rate of the market for the niche
    3. Competition: The level of competition in the niche
    4. Problem severity: The severity of the problems being addressed
    5. Solution feasibility: The feasibility of creating a solution for the niche
    6. Monetization potential: The potential for monetizing a solution in the niche

    Each factor is weighted according to its importance in determining overall
    opportunity value. The default weights are balanced but can be customized.
    """

    def __init__(self):
        """
        Initialize the OpportunityScorer.

        Sets up the default weights for each factor used in the scoring algorithm.
        The weights represent the relative importance of each factor and sum to 1.0.
        """
        self.name = "Opportunity Scorer"
        self.description = "Scores niche opportunities based on various factors"

        # Default weights for each factor (sum = 1.0)
        self.weights = {
            "market_size": 0.2,
            "growth_rate": 0.15,
            "competition": 0.15,
            "problem_severity": 0.2,
            "solution_feasibility": 0.15,
            "monetization_potential": 0.15,
        }

        # Cache TTL in seconds (24 hours by default)
        self.cache_ttl = 86400

        # Lock for concurrent access to shared resources
        self._lock = asyncio.Lock()

    def score_opportunity(
        self, niche: str, market_data: Dict[str, Any], problems: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Score a niche opportunity based on market data and identified problems.

        This method calculates scores for each evaluation factor and combines them into
        an overall opportunity score. It returns a comprehensive analysis of the opportunity,
        including factor scores, overall assessment, and recommendations.

        Algorithm:
        1. Calculate individual factor scores using specialized scoring methods
        2. Apply weights to each factor score
        3. Sum the weighted scores to get the overall opportunity score
        4. Generate an assessment and recommendations based on the overall score

        Args:
            niche: The name of the niche to score
            market_data: Dictionary containing market analysis data
            problems: List of dictionaries containing problem data

        Returns:
            Dictionary containing the opportunity score results
        """
        # Generate a cache key based on inputs
        cache_key = self._generate_cache_key(niche, market_data, problems)

        # Try to get from cache first
        cached_result = default_cache.get(cache_key, namespace="opportunity_scores")
        if cached_result is not None:
            return cached_result

        # Calculate factor scores
        market_size_score = self._score_market_size(market_data.get("market_size", "unknown"))
        growth_rate_score = self._score_growth_rate(market_data.get("growth_rate", "unknown"))
        competition_score = self._score_competition(market_data.get("competition", "unknown"))
        problem_severity_score = self._score_problem_severity(problems)
        solution_feasibility_score = self._score_solution_feasibility(niche, problems)
        monetization_potential_score = self._score_monetization_potential(
            niche, market_data, problems
        )

        # Create factor scores schema objects
        factor_scores = {
            "market_size": FactorScoreSchema(
                score=market_size_score,
                weight=self.weights["market_size"],
                weighted_score=market_size_score * self.weights["market_size"],
                analysis=self._analyze_market_size(market_size_score),
            ),
            "growth_rate": FactorScoreSchema(
                score=growth_rate_score,
                weight=self.weights["growth_rate"],
                weighted_score=growth_rate_score * self.weights["growth_rate"],
                analysis=self._analyze_growth_rate(growth_rate_score),
            ),
            "competition": FactorScoreSchema(
                score=competition_score,
                weight=self.weights["competition"],
                weighted_score=competition_score * self.weights["competition"],
                analysis=self._analyze_competition(competition_score),
            ),
            "problem_severity": FactorScoreSchema(
                score=problem_severity_score,
                weight=self.weights["problem_severity"],
                weighted_score=problem_severity_score * self.weights["problem_severity"],
                analysis=self._analyze_problem_severity(problem_severity_score),
            ),
            "solution_feasibility": FactorScoreSchema(
                score=solution_feasibility_score,
                weight=self.weights["solution_feasibility"],
                weighted_score=solution_feasibility_score * self.weights["solution_feasibility"],
                analysis=self._analyze_solution_feasibility(solution_feasibility_score),
            ),
            "monetization_potential": FactorScoreSchema(
                score=monetization_potential_score,
                weight=self.weights["monetization_potential"],
                weighted_score=monetization_potential_score
                * self.weights["monetization_potential"],
                analysis=self._analyze_monetization_potential(monetization_potential_score),
            ),
        }

        # Calculate the overall score (sum of weighted scores)
        overall_score = sum(score.weighted_score for score in factor_scores.values())

        # Create the factors schema
        factors = FactorsSchema(
            market_size=market_size_score,
            growth_rate=growth_rate_score,
            competition=competition_score,
            problem_severity=problem_severity_score,
            solution_feasibility=solution_feasibility_score,
            monetization_potential=monetization_potential_score,
        )

        # Generate assessment and recommendations based on score
        assessment, recommendations = self._generate_assessment_and_recommendations(
            overall_score, factor_scores, niche
        )

        # Create the full opportunity score object
        opportunity_score = OpportunityScoreSchema(
            id=str(uuid.uuid4()),
            niche=niche,
            score=overall_score,
            overall_score=overall_score,
            opportunity_assessment=assessment,
            factor_scores=FactorScoresSchema(**factor_scores),
            factors=factors,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat(),
        )

        # Convert to dictionary for API compatibility
        result = opportunity_score.dict()

        # Cache the result
        default_cache.set(cache_key, result, ttl=self.cache_ttl, namespace="opportunity_scores")

        return result

    async def score_opportunity_async(
        self, niche: str, market_data: Dict[str, Any], problems: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Asynchronously score a niche opportunity based on market data and identified problems.

        This method is the asynchronous version of score_opportunity() that doesn't block the
        main event loop during potentially time-consuming operations.

        Args:
            niche: The name of the niche to score
            market_data: Dictionary containing market analysis data
            problems: List of dictionaries containing problem data

        Returns:
            Dictionary containing the opportunity score results
        """
        # Generate a cache key based on inputs
        cache_key = self._generate_cache_key(niche, market_data, problems)

        # Try to get from cache first
        cached_result = await run_in_thread(
            default_cache.get, cache_key, namespace="opportunity_scores"
        )
        if cached_result is not None:
            return cached_result

        # Run the scoring operation asynchronously to avoid blocking
        # We'll use run_in_thread to run the CPU-intensive scoring in a separate thread
        result = await run_in_thread(
            self._score_opportunity_internal, niche, market_data, problems, cache_key
        )

        return result

    def _score_opportunity_internal(
        self,
        niche: str,
        market_data: Dict[str, Any],
        problems: List[Dict[str, Any]],
        cache_key: str,
    ) -> Dict[str, Any]:
        """
        Internal method that performs the actual opportunity scoring.

        This is used by both the synchronous and asynchronous versions of score_opportunity.

        Args:
            niche: The name of the niche to score
            market_data: Dictionary containing market analysis data
            problems: List of dictionaries containing problem data
            cache_key: Pre-generated cache key

        Returns:
            Dictionary containing the opportunity score results
        """
        # Calculate factor scores
        market_size_score = self._score_market_size(market_data.get("market_size", "unknown"))
        growth_rate_score = self._score_growth_rate(market_data.get("growth_rate", "unknown"))
        competition_score = self._score_competition(market_data.get("competition", "unknown"))
        problem_severity_score = self._score_problem_severity(problems)
        solution_feasibility_score = self._score_solution_feasibility(niche, problems)
        monetization_potential_score = self._score_monetization_potential(
            niche, market_data, problems
        )

        # Create factor scores schema objects
        factor_scores = {
            "market_size": FactorScoreSchema(
                score=market_size_score,
                weight=self.weights["market_size"],
                weighted_score=market_size_score * self.weights["market_size"],
                analysis=self._analyze_market_size(market_size_score),
            ),
            "growth_rate": FactorScoreSchema(
                score=growth_rate_score,
                weight=self.weights["growth_rate"],
                weighted_score=growth_rate_score * self.weights["growth_rate"],
                analysis=self._analyze_growth_rate(growth_rate_score),
            ),
            "competition": FactorScoreSchema(
                score=competition_score,
                weight=self.weights["competition"],
                weighted_score=competition_score * self.weights["competition"],
                analysis=self._analyze_competition(competition_score),
            ),
            "problem_severity": FactorScoreSchema(
                score=problem_severity_score,
                weight=self.weights["problem_severity"],
                weighted_score=problem_severity_score * self.weights["problem_severity"],
                analysis=self._analyze_problem_severity(problem_severity_score),
            ),
            "solution_feasibility": FactorScoreSchema(
                score=solution_feasibility_score,
                weight=self.weights["solution_feasibility"],
                weighted_score=solution_feasibility_score * self.weights["solution_feasibility"],
                analysis=self._analyze_solution_feasibility(solution_feasibility_score),
            ),
            "monetization_potential": FactorScoreSchema(
                score=monetization_potential_score,
                weight=self.weights["monetization_potential"],
                weighted_score=monetization_potential_score
                * self.weights["monetization_potential"],
                analysis=self._analyze_monetization_potential(monetization_potential_score),
            ),
        }

        # Calculate the overall score (sum of weighted scores)
        overall_score = sum(score.weighted_score for score in factor_scores.values())

        # Create the factors schema
        factors = FactorsSchema(
            market_size=market_size_score,
            growth_rate=growth_rate_score,
            competition=competition_score,
            problem_severity=problem_severity_score,
            solution_feasibility=solution_feasibility_score,
            monetization_potential=monetization_potential_score,
        )

        # Generate assessment and recommendations based on score
        assessment, recommendations = self._generate_assessment_and_recommendations(
            overall_score, factor_scores, niche
        )

        # Create the full opportunity score object
        opportunity_score = OpportunityScoreSchema(
            id=str(uuid.uuid4()),
            niche=niche,
            score=overall_score,
            overall_score=overall_score,
            opportunity_assessment=assessment,
            factor_scores=FactorScoresSchema(**factor_scores),
            factors=factors,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat(),
        )

        # Convert to dictionary for API compatibility
        result = opportunity_score.dict()

        # Cache the result
        default_cache.set(cache_key, result, ttl=self.cache_ttl, namespace="opportunity_scores")

        return result

    async def score_opportunities_batch_async(
        self,
        niches: List[str],
        market_data_list: List[Dict[str, Any]],
        problems_list: List[List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        """
        Score multiple opportunities in parallel asynchronously.

        This method processes multiple opportunity scoring tasks concurrently, which can
        significantly improve performance when scoring many opportunities.

        Args:
            niches: List of niche names to score
            market_data_list: List of market data dictionaries corresponding to each niche
            problems_list: List of problem lists corresponding to each niche

        Returns:
            List of opportunity score dictionaries
        """
        # Validate input lengths match
        if not (len(niches) == len(market_data_list) == len(problems_list)):
            raise ValueError("Input lists must have the same length")

        # Create tasks for each opportunity scoring operation
        tasks = []
        for i in range(len(niches)):
            tasks.append(
                self.score_opportunity_async(niches[i], market_data_list[i], problems_list[i])
            )

        # Run all tasks concurrently and gather results
        results = await asyncio.gather(*tasks)

        return results

    async def analyze_and_compare_opportunities_async(
        self,
        niches: List[str],
        market_data_list: List[Dict[str, Any]],
        problems_list: List[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """
        Score multiple opportunities and compare them in one operation asynchronously.

        This method combines scoring and comparison into a single asynchronous operation.

        Args:
            niches: List of niche names to score
            market_data_list: List of market data dictionaries corresponding to each niche
            problems_list: List of problem lists corresponding to each niche

        Returns:
            Dictionary containing both individual scores and comparison results
        """
        # First score all opportunities in parallel
        opportunity_scores = await self.score_opportunities_batch_async(
            niches, market_data_list, problems_list
        )

        # Then compare the opportunities
        comparison = await self.compare_opportunities_async(opportunity_scores)

        # Return both individual scores and comparison
        return {"individual_scores": opportunity_scores, "comparison": comparison}

    def compare_opportunities(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple opportunities to identify the most promising ones.

        This method ranks opportunities by their overall scores, identifies the top
        recommendation, and provides a comparative analysis across all opportunities.

        Algorithm:
        1. Sort opportunities by overall score
        2. Assign ranks to each opportunity
        3. Identify the highest-scoring opportunity as the top recommendation
        4. Calculate statistics like highest, lowest, average scores
        5. Generate comparative analysis and recommendations

        Args:
            opportunities: List of opportunity dictionaries from score_opportunity

        Returns:
            Dictionary containing the comparison results
        """
        # Generate a cache key based on the opportunities
        cache_key = self._generate_comparison_cache_key(opportunities)

        # Try to get from cache first
        cached_result = default_cache.get(cache_key, namespace="opportunity_comparisons")
        if cached_result is not None:
            return cached_result

        # Sort opportunities by overall score in descending order
        sorted_opportunities = sorted(
            opportunities, key=lambda x: x.get("overall_score", 0.0), reverse=True
        )

        # Create ranked opportunities
        ranked_opportunities = []
        for i, opp in enumerate(sorted_opportunities):
            ranked_opportunities.append(
                RankedOpportunitySchema(
                    id=opp.get("id", str(uuid.uuid4())),
                    niche=opp.get("niche", "Unknown"),
                    overall_score=opp.get("overall_score", 0.0),
                    rank=i + 1,
                )
            )

        # Get top recommendation
        if ranked_opportunities:
            top_opp = sorted_opportunities[0]
            top_recommendation = TopRecommendationSchema(
                id=top_opp.get("id", str(uuid.uuid4())),
                niche=top_opp.get("niche", "Unknown"),
                overall_score=top_opp.get("overall_score", 0.0),
                assessment=top_opp.get("opportunity_assessment", ""),
                next_steps=self._generate_next_steps(top_opp),
            )
        else:
            top_recommendation = None

        # Calculate score distribution
        score_distribution = self._calculate_score_distribution(sorted_opportunities)

        # Calculate statistics
        highest_score = (
            max([opp.get("overall_score", 0.0) for opp in sorted_opportunities])
            if sorted_opportunities
            else None
        )
        lowest_score = (
            min([opp.get("overall_score", 0.0) for opp in sorted_opportunities])
            if sorted_opportunities
            else None
        )
        average_score = (
            sum([opp.get("overall_score", 0.0) for opp in sorted_opportunities])
            / len(sorted_opportunities)
            if sorted_opportunities
            else None
        )

        # Create comparative analysis
        comparative_analysis = ComparativeAnalysisSchema(
            highest_score=highest_score,
            lowest_score=lowest_score,
            average_score=average_score,
            score_distribution=score_distribution,
        )

        # Create comparison factors
        comparison_factors = self._generate_comparison_factors(sorted_opportunities)

        # Generate recommendations based on comparison
        recommendations = self._generate_comparison_recommendations(
            sorted_opportunities, comparative_analysis
        )

        # Create the full comparison result
        comparison_result = OpportunityComparisonSchema(
            id=str(uuid.uuid4()),
            opportunities_count=len(opportunities),
            ranked_opportunities=ranked_opportunities,
            top_recommendation=top_recommendation,
            comparison_factors=comparison_factors,
            comparative_analysis=comparative_analysis,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat(),
        )

        # Convert to dictionary for API compatibility
        result = comparison_result.dict()

        # Cache the result
        default_cache.set(
            cache_key, result, ttl=self.cache_ttl, namespace="opportunity_comparisons"
        )

        return result

    async def compare_opportunities_async(
        self, opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Asynchronously compare multiple opportunities to identify the most promising ones.

        This method is the asynchronous version of compare_opportunities and should be used
        in an async context. It performs the same ranking and analysis but doesn't block
        the event loop.

        Args:
            opportunities: List of opportunity dictionaries from score_opportunity

        Returns:
            Dictionary containing the comparison results
        """
        async with self._lock:
            return await run_in_thread(self.compare_opportunities, opportunities)

    def get_scoring_factors(self) -> List[str]:
        """
        Get a list of scoring factors used by the OpportunityScorer.

        Returns:
            List of scoring factor names
        """
        return list(self.weights.keys())

    async def get_scoring_factors_async(self) -> List[str]:
        """
        Asynchronously get a list of scoring factors used by the OpportunityScorer.

        Returns:
            List of scoring factor names
        """
        return self.weights.keys()

    def _generate_cache_key(
        self, niche: str, market_data: Dict[str, Any], problems: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a cache key for opportunity scoring results.

        Args:
            niche: The niche name
            market_data: Market data dictionary
            problems: List of problem dictionaries

        Returns:
            Cache key string
        """
        # Create a stable representation of the inputs
        key_data = {
            "niche": niche,
            "market_data": market_data,
            "problems": self._normalize_problems_for_cache(problems),
            "weights": self.weights,
        }

        # Convert to stable string representation
        key_str = json.dumps(key_data, sort_keys=True)

        # Hash to get a fixed-length key
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _normalize_problems_for_cache(self, problems: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize problem dictionaries to ensure stable cache keys.

        Args:
            problems: List of problem dictionaries

        Returns:
            Normalized list of problem dictionaries
        """
        normalized = []

        # Extract only the fields needed for scoring to reduce key size
        for problem in problems:
            normalized.append(
                {
                    "severity": problem.get("severity", "low"),
                    "description": problem.get("description", ""),
                }
            )

        # Sort by description for stable order
        return sorted(normalized, key=lambda p: p["description"])

    def _generate_comparison_cache_key(self, opportunities: List[Dict[str, Any]]) -> str:
        """
        Generate a cache key for opportunity comparison results.

        Args:
            opportunities: List of opportunity dictionaries

        Returns:
            Cache key string
        """
        # Get a stable representation of the opportunities
        key_parts = []

        for opp in opportunities:
            # Use ID and score as the most important parts for comparison
            key_parts.append(
                {
                    "id": opp.get("id", ""),
                    "niche": opp.get("niche", ""),
                    "overall_score": opp.get("overall_score", 0.0),
                }
            )

        # Sort by ID for stable order
        key_parts.sort(key=lambda p: p["id"])

        # Convert to stable string representation and hash
        key_str = json.dumps(key_parts, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def invalidate_opportunity_cache(self, niche: Optional[str] = None) -> bool:
        """
        Invalidate cached opportunity scores.

        Args:
            niche: Optional niche name to invalidate. If None, invalidates all cached scores.

        Returns:
            True if successful, False otherwise
        """
        if niche is None:
            # Clear all opportunity scores
            return default_cache.clear(namespace="opportunity_scores")
        else:
            # TODO: For a more targeted approach, we would need to store
            # a mapping of niches to cache keys. For now, we clear all.
            return default_cache.clear(namespace="opportunity_scores")

    async def invalidate_opportunity_cache_async(self, niche: Optional[str] = None) -> bool:
        """
        Asynchronously invalidate cached opportunity scores.

        Args:
            niche: Optional niche name to invalidate. If None, invalidates all cached scores.

        Returns:
            True if successful, False otherwise
        """
        return await run_in_thread(self.invalidate_opportunity_cache, niche)

    def invalidate_comparison_cache(self) -> bool:
        """
        Invalidate all cached opportunity comparisons.

        Returns:
            True if successful, False otherwise
        """
        return default_cache.clear(namespace="opportunity_comparisons")

    async def invalidate_comparison_cache_async(self) -> bool:
        """
        Asynchronously invalidate all cached opportunity comparisons.

        Returns:
            True if successful, False otherwise
        """
        return await run_in_thread(self.invalidate_comparison_cache)

    def _score_market_size(self, market_size: str) -> float:
        """
        Score the market size factor.

        This method converts a qualitative market size assessment to a numerical
        score between 0 and 1.

        Algorithm:
        - "large" -> 0.9
        - "medium" -> 0.6
        - "small" -> 0.3
        - "unknown" -> 0.5 (neutral)

        Args:
            market_size: Qualitative assessment of market size

        Returns:
            Market size score between 0 and 1
        """
        market_size_scores = {"large": 0.9, "medium": 0.6, "small": 0.3, "unknown": 0.5}
        return market_size_scores.get(market_size.lower(), 0.5)

    def _score_growth_rate(self, growth_rate: str) -> float:
        """
        Score the growth rate factor.

        This method converts a qualitative growth rate assessment to a numerical
        score between 0 and 1.

        Algorithm:
        - "high" -> 0.9
        - "medium" -> 0.6
        - "low" -> 0.3
        - "unknown" -> 0.5 (neutral)

        Args:
            growth_rate: Qualitative assessment of growth rate

        Returns:
            Growth rate score between 0 and 1
        """
        growth_rate_scores = {"high": 0.9, "medium": 0.6, "low": 0.3, "unknown": 0.5}
        return growth_rate_scores.get(growth_rate.lower(), 0.5)

    def _score_competition(self, competition: str) -> float:
        """
        Score the competition factor.

        This method converts a qualitative competition assessment to a numerical
        score between 0 and 1. Note that this is inverted - lower competition
        results in a higher score.

        Algorithm:
        - "low" -> 0.9 (less competition is better)
        - "medium" -> 0.5
        - "high" -> 0.2 (high competition is worse)
        - "unknown" -> 0.5 (neutral)

        Args:
            competition: Qualitative assessment of competition

        Returns:
            Competition score between 0 and 1
        """
        competition_scores = {"low": 0.9, "medium": 0.5, "high": 0.2, "unknown": 0.5}
        return competition_scores.get(competition.lower(), 0.5)

    def _score_problem_severity(self, problems: List[Dict[str, Any]]) -> float:
        """
        Score the problem severity factor.

        This method calculates a score based on the severity of problems identified
        in the niche. Higher severity problems lead to higher scores.

        Algorithm:
        1. For each problem, convert severity to a numerical value:
           - "high" -> 1.0
           - "medium" -> 0.6
           - "low" -> 0.3
        2. Calculate weighted average of problem severities
        3. If no problems are provided, return 0 (no opportunity without problems)

        Args:
            problems: List of problem dictionaries

        Returns:
            Problem severity score between 0 and 1
        """
        if not problems:
            return 0.0

        severity_scores = {"high": 1.0, "medium": 0.6, "low": 0.3}

        # Calculate average severity
        total_severity = sum(
            severity_scores.get(p.get("severity", "low").lower(), 0.0) for p in problems
        )
        return total_severity / len(problems)

    def _score_solution_feasibility(self, niche: str, problems: List[Dict[str, Any]]) -> float:
        """
        Score the solution feasibility factor.

        This method evaluates how feasible it is to create an AI-powered solution
        for the identified problems in the niche.

        Algorithm:
        1. Base feasibility starts at 0.7 (moderately feasible)
        2. Adjust based on niche characteristics:
           - Text/content-focused niches (higher feasibility for AI)
           - Data processing niches (higher feasibility)
           - Physical product niches (lower feasibility)
        3. Normalize to ensure score is between 0 and 1

        Args:
            niche: Name of the niche
            problems: List of problem dictionaries

        Returns:
            Solution feasibility score between 0 and 1
        """
        # Start with a base feasibility score
        base_feasibility = 0.7

        # Adjust based on niche type
        # Text/content niches are more feasible for AI solutions
        text_content_niches = [
            "content",
            "writing",
            "translation",
            "summarization",
            "description",
            "copywriting",
            "editing",
        ]

        # Data processing niches are also more feasible
        data_niches = [
            "analytics",
            "analysis",
            "reporting",
            "monitoring",
            "tracking",
            "management",
            "automation",
        ]

        # Adjust score based on niche keywords
        niche_lower = niche.lower()

        # Check for text/content niche keywords
        if any(keyword in niche_lower for keyword in text_content_niches):
            base_feasibility += 0.2

        # Check for data niche keywords
        if any(keyword in niche_lower for keyword in data_niches):
            base_feasibility += 0.1

        # Ensure the score is between 0 and 1
        return min(max(base_feasibility, 0.0), 1.0)

    def _score_monetization_potential(
        self, niche: str, market_data: Dict[str, Any], problems: List[Dict[str, Any]]
    ) -> float:
        """
        Score the monetization potential factor.

        This method evaluates the potential to monetize a solution in the niche.

        Algorithm:
        1. Base potential starts at 0.5 (moderate potential)
        2. Adjust based on market size and growth rate:
           - Larger markets have higher monetization potential
           - Higher growth rates increase potential
        3. Adjust based on problem severity:
           - More severe problems generally have higher willingness to pay
        4. Normalize to ensure score is between 0 and 1

        Args:
            niche: Name of the niche
            market_data: Dictionary containing market analysis data
            problems: List of problem dictionaries

        Returns:
            Monetization potential score between 0 and 1
        """
        # Start with base monetization potential
        base_potential = 0.5

        # Adjust for market size
        market_size = market_data.get("market_size", "unknown").lower()
        if market_size == "large":
            base_potential += 0.2
        elif market_size == "medium":
            base_potential += 0.1
        elif market_size == "small":
            base_potential -= 0.1

        # Adjust for growth rate
        growth_rate = market_data.get("growth_rate", "unknown").lower()
        if growth_rate == "high":
            base_potential += 0.2
        elif growth_rate == "medium":
            base_potential += 0.1
        elif growth_rate == "low":
            base_potential -= 0.1

        # Adjust for problem severity (more severe = higher willingness to pay)
        problem_severity = self._score_problem_severity(problems)
        if problem_severity > 0.7:
            base_potential += 0.1

        # Business-oriented niches typically have higher monetization potential
        business_keywords = [
            "business",
            "enterprise",
            "professional",
            "b2b",
            "management",
            "productivity",
            "efficiency",
        ]

        # Check for business niche keywords
        niche_lower = niche.lower()
        if any(keyword in niche_lower for keyword in business_keywords):
            base_potential += 0.1

        # Ensure the score is between 0 and 1
        return min(max(base_potential, 0.0), 1.0)

    def _analyze_market_size(self, score: float) -> str:
        """
        Generate analysis text for market size score.

        Args:
            score: Market size score between 0 and 1

        Returns:
            Analysis text for the market size factor
        """
        if score >= 0.8:
            return "Large market size with significant potential customer base."
        elif score >= 0.5:
            return "Medium market size with a reasonable potential customer base."
        else:
            return "Small market size with limited potential customer base."

    def _analyze_growth_rate(self, score: float) -> str:
        """
        Generate analysis text for growth rate score.

        Args:
            score: Growth rate score between 0 and 1

        Returns:
            Analysis text for the growth rate factor
        """
        if score >= 0.8:
            return "High growth rate indicating a rapidly expanding market opportunity."
        elif score >= 0.5:
            return "Moderate growth rate showing steady market expansion."
        else:
            return "Low growth rate indicating a stable or declining market."

    def _analyze_competition(self, score: float) -> str:
        """
        Generate analysis text for competition score.

        Args:
            score: Competition score between 0 and 1

        Returns:
            Analysis text for the competition factor
        """
        if score >= 0.8:
            return "Low competition level with few established solutions."
        elif score >= 0.5:
            return "Moderate competition with some established solutions."
        else:
            return "High competition with many established solutions."

    def _analyze_problem_severity(self, score: float) -> str:
        """
        Generate analysis text for problem severity score.

        Args:
            score: Problem severity score between 0 and 1

        Returns:
            Analysis text for the problem severity factor
        """
        if score >= 0.8:
            return "High severity problems indicating significant pain points for users."
        elif score >= 0.5:
            return "Moderate severity problems with notable impact on users."
        else:
            return "Low severity problems with minimal impact on users."

    def _analyze_solution_feasibility(self, score: float) -> str:
        """
        Generate analysis text for solution feasibility score.

        Args:
            score: Solution feasibility score between 0 and 1

        Returns:
            Analysis text for the solution feasibility factor
        """
        if score >= 0.8:
            return "Highly feasible solution that can be readily implemented with AI technology."
        elif score >= 0.5:
            return "Moderately feasible solution with some implementation challenges."
        else:
            return "Challenging solution with significant technical barriers to implementation."

    def _analyze_monetization_potential(self, score: float) -> str:
        """
        Generate analysis text for monetization potential score.

        Args:
            score: Monetization potential score between 0 and 1

        Returns:
            Analysis text for the monetization potential factor
        """
        if score >= 0.8:
            return "High monetization potential with strong willingness to pay."
        elif score >= 0.5:
            return "Moderate monetization potential with reasonable willingness to pay."
        else:
            return "Limited monetization potential with low willingness to pay."

    def _generate_assessment_and_recommendations(
        self, score: float, factor_scores: Dict[str, FactorScoreSchema], niche: str
    ) -> tuple:
        """
        Generate opportunity assessment and recommendations based on the overall score.

        Algorithm:
        1. Determine assessment text category based on score range
        2. Identify strengths (high-scoring factors)
        3. Identify weaknesses (low-scoring factors)
        4. Generate actionable recommendations based on the overall assessment and factor scores

        Args:
            score: Overall opportunity score
            factor_scores: Dictionary of factor scores
            niche: Name of the niche

        Returns:
            Tuple of (assessment text, list of recommendation strings)
        """
        # Generate assessment text
        if score >= 0.8:
            assessment = "Excellent opportunity with high potential"
        elif score >= 0.6:
            assessment = "Very good opportunity worth pursuing"
        elif score >= 0.4:
            assessment = "Good opportunity with moderate potential"
        elif score >= 0.2:
            assessment = "Fair opportunity with limited potential"
        else:
            assessment = "Limited opportunity with minimal potential"

        # Generate recommendations
        recommendations = []

        # Add general recommendation based on score
        if score >= 0.8:
            recommendations.append("Proceed with high priority")
            recommendations.append("Allocate significant resources")
            recommendations.append("Develop a comprehensive implementation plan")
        elif score >= 0.6:
            recommendations.append("Proceed with medium-high priority")
            recommendations.append("Allocate appropriate resources")
            recommendations.append("Develop an implementation plan")
        elif score >= 0.4:
            recommendations.append("Proceed with medium priority")
            recommendations.append("Allocate moderate resources")
            recommendations.append("Develop an initial implementation plan")
        elif score >= 0.2:
            recommendations.append("Proceed with caution")
            recommendations.append("Allocate limited resources for exploration")
            recommendations.append("Consider further research before proceeding")
        else:
            recommendations.append("Deprioritize this opportunity")
            recommendations.append("Consider alternatives")
            recommendations.append("Reassess if market conditions change")

        # Add specific recommendations based on factor scores
        strengths = []
        weaknesses = []

        # Identify strengths and weaknesses
        for factor_name, factor_score in factor_scores.items():
            if factor_score.score >= 0.7:
                strengths.append(factor_name)
            elif factor_score.score <= 0.4:
                weaknesses.append(factor_name)

        # Add recommendations based on strengths
        if "market_size" in strengths:
            recommendations.append(f"Leverage the large market size in the {niche} niche")

        if "growth_rate" in strengths:
            recommendations.append(f"Position for rapid growth in the {niche} niche")

        if "competition" in strengths:
            recommendations.append("Capitalize on the low competition environment")

        if "problem_severity" in strengths:
            recommendations.append("Emphasize the significant pain point being solved")

        if "solution_feasibility" in strengths:
            recommendations.append("Move quickly to implement the technically feasible solution")

        if "monetization_potential" in strengths:
            recommendations.append(
                "Develop a premium pricing strategy based on high willingness to pay"
            )

        # Add recommendations based on weaknesses
        if "market_size" in weaknesses:
            recommendations.append(
                "Focus on a specific sub-segment of the market to maximize impact"
            )

        if "growth_rate" in weaknesses:
            recommendations.append("Consider a long-term strategy for steady growth")

        if "competition" in weaknesses:
            recommendations.append("Develop clear differentiation from existing competitors")

        if "problem_severity" in weaknesses:
            recommendations.append("Focus marketing on establishing the importance of the problem")

        if "solution_feasibility" in weaknesses:
            recommendations.append("Allocate additional resources to technical development")

        if "monetization_potential" in weaknesses:
            recommendations.append("Explore freemium or volume-based pricing models")

        return assessment, recommendations

    def _generate_next_steps(self, top_opportunity: Dict[str, Any]) -> List[str]:
        """
        Generate next steps for the top recommendation.

        Args:
            top_opportunity: Dictionary of the top opportunity

        Returns:
            List of next steps
        """
        next_steps = [
            f"Conduct detailed market research for {top_opportunity.get('niche', 'the niche')}",
            "Develop a prototype solution",
            "Test with potential users",
            "Refine business model",
            "Create implementation timeline",
        ]

        return next_steps

    def _calculate_score_distribution(
        self, opportunities: List[Dict[str, Any]]
    ) -> ScoreDistributionSchema:
        """
        Calculate the distribution of scores across opportunities.

        Args:
            opportunities: List of opportunity dictionaries

        Returns:
            ScoreDistributionSchema with count of opportunities in each score range
        """
        excellent = 0
        very_good = 0
        good = 0
        fair = 0
        limited = 0

        for opp in opportunities:
            score = opp.get("overall_score", 0.0)
            if score >= 0.8:
                excellent += 1
            elif score >= 0.6:
                very_good += 1
            elif score >= 0.4:
                good += 1
            elif score >= 0.2:
                fair += 1
            else:
                limited += 1

        return ScoreDistributionSchema(
            excellent=excellent,
            very_good=very_good,
            good=good,
            fair=fair,
            limited=limited,
        )

    def _generate_comparison_factors(self, opportunities: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Generate comparison factors based on the opportunities being compared.

        Args:
            opportunities: List of opportunity dictionaries

        Returns:
            Dictionary of comparison factor names and descriptions
        """
        comparison_factors = {
            "market_size": "Size of the potential market",
            "growth_rate": "Growth rate of the market",
            "competition": "Level of competition in the market",
            "problem_severity": "Severity of the problems being solved",
            "solution_feasibility": "Feasibility of implementing AI-powered solutions",
            "monetization_potential": "Potential for profitable monetization",
        }

        return comparison_factors

    def _generate_comparison_recommendations(
        self, opportunities: List[Dict[str, Any]], analysis: ComparativeAnalysisSchema
    ) -> List[str]:
        """
        Generate recommendations based on comparison of opportunities.

        Args:
            opportunities: List of opportunity dictionaries
            analysis: ComparativeAnalysis object

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # General recommendations based on distribution
        if analysis.score_distribution.excellent > 0:
            recommendations.append(
                f"Focus on the {analysis.score_distribution.excellent} excellent opportunities as high priority"
            )

        if analysis.score_distribution.very_good > 0:
            recommendations.append(
                f"Consider the {analysis.score_distribution.very_good} very good opportunities as medium priority"
            )

        # Add recommendations for top opportunities
        if opportunities:
            top_opp = opportunities[0]
            recommendations.append(
                f"Prioritize {top_opp.get('niche', 'the top niche')} as the primary opportunity"
            )

            # If there's a second best, mention it as well
            if len(opportunities) > 1:
                second_opp = opportunities[1]
                recommendations.append(
                    f"Keep {second_opp.get('niche', 'the second niche')} as a backup opportunity"
                )

        # Add portfolio recommendation if there are multiple good opportunities
        if analysis.score_distribution.excellent + analysis.score_distribution.very_good > 1:
            recommendations.append(
                "Consider a portfolio approach with multiple opportunities in parallel"
            )

        # Add recommendation for low-scoring opportunities
        if analysis.score_distribution.limited > 0:
            recommendations.append(
                f"Deprioritize or eliminate the {analysis.score_distribution.limited} limited opportunities"
            )

        return recommendations
