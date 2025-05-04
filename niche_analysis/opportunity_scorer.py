"""
"""
Opportunity Scorer for the pAIssive Income project.
Opportunity Scorer for the pAIssive Income project.
Scores niche opportunities based on various factors.
Scores niche opportunities based on various factors.
"""
"""


import asyncio
import asyncio
import hashlib
import hashlib
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


from ai_models.async_utils import run_in_thread
from ai_models.async_utils import run_in_thread
from common_utils.caching import default_cache
from common_utils.caching import default_cache


# Import async utilities
# Import async utilities
# Import the centralized caching service
# Import the centralized caching service
(
(
ComparativeAnalysisSchema,
ComparativeAnalysisSchema,
FactorScoreSchema,
FactorScoreSchema,
FactorScoresSchema,
FactorScoresSchema,
FactorsSchema,
FactorsSchema,
OpportunityComparisonSchema,
OpportunityComparisonSchema,
OpportunityScoreSchema,
OpportunityScoreSchema,
RankedOpportunitySchema,
RankedOpportunitySchema,
ScoreDistributionSchema,
ScoreDistributionSchema,
TopRecommendationSchema,
TopRecommendationSchema,
)
)




class OpportunityScorer:
    class OpportunityScorer:
    """
    """
    OpportunityScorer class for scoring niche opportunities.
    OpportunityScorer class for scoring niche opportunities.


    This class evaluates niche opportunities based on various factors and provides
    This class evaluates niche opportunities based on various factors and provides
    methods for scoring individual opportunities and comparing multiple opportunities.
    methods for scoring individual opportunities and comparing multiple opportunities.
    The scoring algorithm considers six main factors:
    The scoring algorithm considers six main factors:


    1. Market size: The potential size of the market for the niche
    1. Market size: The potential size of the market for the niche
    2. Growth rate: The growth rate of the market for the niche
    2. Growth rate: The growth rate of the market for the niche
    3. Competition: The level of competition in the niche
    3. Competition: The level of competition in the niche
    4. Problem severity: The severity of the problems being addressed
    4. Problem severity: The severity of the problems being addressed
    5. Solution feasibility: The feasibility of creating a solution for the niche
    5. Solution feasibility: The feasibility of creating a solution for the niche
    6. Monetization potential: The potential for monetizing a solution in the niche
    6. Monetization potential: The potential for monetizing a solution in the niche


    Each factor is weighted according to its importance in determining overall
    Each factor is weighted according to its importance in determining overall
    opportunity value. The default weights are balanced but can be customized.
    opportunity value. The default weights are balanced but can be customized.
    """
    """


    def __init__(self):
    def __init__(self):
    """
    """
    Initialize the OpportunityScorer.
    Initialize the OpportunityScorer.


    Sets up the default weights for each factor used in the scoring algorithm.
    Sets up the default weights for each factor used in the scoring algorithm.
    The weights represent the relative importance of each factor and sum to 1.0.
    The weights represent the relative importance of each factor and sum to 1.0.
    """
    """
    self.name = "Opportunity Scorer"
    self.name = "Opportunity Scorer"
    self.description = "Scores niche opportunities based on various factors"
    self.description = "Scores niche opportunities based on various factors"


    # Default weights for each factor (sum = 1.0)
    # Default weights for each factor (sum = 1.0)
    self.weights = {
    self.weights = {
    "market_size": 0.2,
    "market_size": 0.2,
    "growth_rate": 0.15,
    "growth_rate": 0.15,
    "competition": 0.15,
    "competition": 0.15,
    "problem_severity": 0.2,
    "problem_severity": 0.2,
    "solution_feasibility": 0.15,
    "solution_feasibility": 0.15,
    "monetization_potential": 0.15,
    "monetization_potential": 0.15,
    }
    }


    # Cache TTL in seconds (24 hours by default)
    # Cache TTL in seconds (24 hours by default)
    self.cache_ttl = 86400
    self.cache_ttl = 86400


    # Lock for concurrent access to shared resources
    # Lock for concurrent access to shared resources
    self._lock = asyncio.Lock()
    self._lock = asyncio.Lock()


    def score_opportunity(
    def score_opportunity(
    self, niche: str, market_data: Dict[str, Any], problems: List[Dict[str, Any]]
    self, niche: str, market_data: Dict[str, Any], problems: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Score a niche opportunity based on market data and identified problems.
    Score a niche opportunity based on market data and identified problems.


    This method calculates scores for each evaluation factor and combines them into
    This method calculates scores for each evaluation factor and combines them into
    an overall opportunity score. It returns a comprehensive analysis of the opportunity,
    an overall opportunity score. It returns a comprehensive analysis of the opportunity,
    including factor scores, overall assessment, and recommendations.
    including factor scores, overall assessment, and recommendations.


    Algorithm:
    Algorithm:
    1. Calculate individual factor scores using specialized scoring methods
    1. Calculate individual factor scores using specialized scoring methods
    2. Apply weights to each factor score
    2. Apply weights to each factor score
    3. Sum the weighted scores to get the overall opportunity score
    3. Sum the weighted scores to get the overall opportunity score
    4. Generate an assessment and recommendations based on the overall score
    4. Generate an assessment and recommendations based on the overall score


    Args:
    Args:
    niche: The name of the niche to score
    niche: The name of the niche to score
    market_data: Dictionary containing market analysis data
    market_data: Dictionary containing market analysis data
    problems: List of dictionaries containing problem data
    problems: List of dictionaries containing problem data


    Returns:
    Returns:
    Dictionary containing the opportunity score results
    Dictionary containing the opportunity score results
    """
    """
    # Generate a cache key based on inputs
    # Generate a cache key based on inputs
    cache_key = self._generate_cache_key(niche, market_data, problems)
    cache_key = self._generate_cache_key(niche, market_data, problems)


    # Try to get from cache first
    # Try to get from cache first
    cached_result = default_cache.get(cache_key, namespace="opportunity_scores")
    cached_result = default_cache.get(cache_key, namespace="opportunity_scores")
    if cached_result is not None:
    if cached_result is not None:
    return cached_result
    return cached_result


    # Calculate factor scores
    # Calculate factor scores
    market_size_score = self._score_market_size(
    market_size_score = self._score_market_size(
    market_data.get("market_size", "unknown")
    market_data.get("market_size", "unknown")
    )
    )
    growth_rate_score = self._score_growth_rate(
    growth_rate_score = self._score_growth_rate(
    market_data.get("growth_rate", "unknown")
    market_data.get("growth_rate", "unknown")
    )
    )
    competition_score = self._score_competition(
    competition_score = self._score_competition(
    market_data.get("competition", "unknown")
    market_data.get("competition", "unknown")
    )
    )
    problem_severity_score = self._score_problem_severity(problems)
    problem_severity_score = self._score_problem_severity(problems)
    solution_feasibility_score = self._score_solution_feasibility(niche, problems)
    solution_feasibility_score = self._score_solution_feasibility(niche, problems)
    monetization_potential_score = self._score_monetization_potential(
    monetization_potential_score = self._score_monetization_potential(
    niche, market_data, problems
    niche, market_data, problems
    )
    )


    # Create factor scores schema objects
    # Create factor scores schema objects
    factor_scores = {
    factor_scores = {
    "market_size": FactorScoreSchema(
    "market_size": FactorScoreSchema(
    score=market_size_score,
    score=market_size_score,
    weight=self.weights["market_size"],
    weight=self.weights["market_size"],
    weighted_score=market_size_score * self.weights["market_size"],
    weighted_score=market_size_score * self.weights["market_size"],
    analysis=self._analyze_market_size(market_size_score),
    analysis=self._analyze_market_size(market_size_score),
    ),
    ),
    "growth_rate": FactorScoreSchema(
    "growth_rate": FactorScoreSchema(
    score=growth_rate_score,
    score=growth_rate_score,
    weight=self.weights["growth_rate"],
    weight=self.weights["growth_rate"],
    weighted_score=growth_rate_score * self.weights["growth_rate"],
    weighted_score=growth_rate_score * self.weights["growth_rate"],
    analysis=self._analyze_growth_rate(growth_rate_score),
    analysis=self._analyze_growth_rate(growth_rate_score),
    ),
    ),
    "competition": FactorScoreSchema(
    "competition": FactorScoreSchema(
    score=competition_score,
    score=competition_score,
    weight=self.weights["competition"],
    weight=self.weights["competition"],
    weighted_score=competition_score * self.weights["competition"],
    weighted_score=competition_score * self.weights["competition"],
    analysis=self._analyze_competition(competition_score),
    analysis=self._analyze_competition(competition_score),
    ),
    ),
    "problem_severity": FactorScoreSchema(
    "problem_severity": FactorScoreSchema(
    score=problem_severity_score,
    score=problem_severity_score,
    weight=self.weights["problem_severity"],
    weight=self.weights["problem_severity"],
    weighted_score=problem_severity_score
    weighted_score=problem_severity_score
    * self.weights["problem_severity"],
    * self.weights["problem_severity"],
    analysis=self._analyze_problem_severity(problem_severity_score),
    analysis=self._analyze_problem_severity(problem_severity_score),
    ),
    ),
    "solution_feasibility": FactorScoreSchema(
    "solution_feasibility": FactorScoreSchema(
    score=solution_feasibility_score,
    score=solution_feasibility_score,
    weight=self.weights["solution_feasibility"],
    weight=self.weights["solution_feasibility"],
    weighted_score=solution_feasibility_score
    weighted_score=solution_feasibility_score
    * self.weights["solution_feasibility"],
    * self.weights["solution_feasibility"],
    analysis=self._analyze_solution_feasibility(solution_feasibility_score),
    analysis=self._analyze_solution_feasibility(solution_feasibility_score),
    ),
    ),
    "monetization_potential": FactorScoreSchema(
    "monetization_potential": FactorScoreSchema(
    score=monetization_potential_score,
    score=monetization_potential_score,
    weight=self.weights["monetization_potential"],
    weight=self.weights["monetization_potential"],
    weighted_score=monetization_potential_score
    weighted_score=monetization_potential_score
    * self.weights["monetization_potential"],
    * self.weights["monetization_potential"],
    analysis=self._analyze_monetization_potential(
    analysis=self._analyze_monetization_potential(
    monetization_potential_score
    monetization_potential_score
    ),
    ),
    ),
    ),
    }
    }


    # Calculate the overall score (sum of weighted scores)
    # Calculate the overall score (sum of weighted scores)
    overall_score = sum(score.weighted_score for score in factor_scores.values())
    overall_score = sum(score.weighted_score for score in factor_scores.values())


    # Create the factors schema
    # Create the factors schema
    factors = FactorsSchema(
    factors = FactorsSchema(
    market_size=market_size_score,
    market_size=market_size_score,
    growth_rate=growth_rate_score,
    growth_rate=growth_rate_score,
    competition=competition_score,
    competition=competition_score,
    problem_severity=problem_severity_score,
    problem_severity=problem_severity_score,
    solution_feasibility=solution_feasibility_score,
    solution_feasibility=solution_feasibility_score,
    monetization_potential=monetization_potential_score,
    monetization_potential=monetization_potential_score,
    )
    )


    # Generate assessment and recommendations based on score
    # Generate assessment and recommendations based on score
    assessment, recommendations = self._generate_assessment_and_recommendations(
    assessment, recommendations = self._generate_assessment_and_recommendations(
    overall_score, factor_scores, niche
    overall_score, factor_scores, niche
    )
    )


    # Create the full opportunity score object
    # Create the full opportunity score object
    opportunity_score = OpportunityScoreSchema(
    opportunity_score = OpportunityScoreSchema(
    id=str(uuid.uuid4()),
    id=str(uuid.uuid4()),
    niche=niche,
    niche=niche,
    score=overall_score,
    score=overall_score,
    overall_score=overall_score,
    overall_score=overall_score,
    opportunity_assessment=assessment,
    opportunity_assessment=assessment,
    factor_scores=FactorScoresSchema(**factor_scores),
    factor_scores=FactorScoresSchema(**factor_scores),
    factors=factors,
    factors=factors,
    recommendations=recommendations,
    recommendations=recommendations,
    timestamp=datetime.now().isoformat(),
    timestamp=datetime.now().isoformat(),
    )
    )


    # Convert to dictionary for API compatibility
    # Convert to dictionary for API compatibility
    result = opportunity_score.dict()
    result = opportunity_score.dict()


    # Cache the result
    # Cache the result
    default_cache.set(
    default_cache.set(
    cache_key, result, ttl=self.cache_ttl, namespace="opportunity_scores"
    cache_key, result, ttl=self.cache_ttl, namespace="opportunity_scores"
    )
    )


    return result
    return result


    async def score_opportunity_async(
    async def score_opportunity_async(
    self, niche: str, market_data: Dict[str, Any], problems: List[Dict[str, Any]]
    self, niche: str, market_data: Dict[str, Any], problems: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Asynchronously score a niche opportunity based on market data and identified problems.
    Asynchronously score a niche opportunity based on market data and identified problems.


    This method is the asynchronous version of score_opportunity() that doesn't block the
    This method is the asynchronous version of score_opportunity() that doesn't block the
    main event loop during potentially time-consuming operations.
    main event loop during potentially time-consuming operations.


    Args:
    Args:
    niche: The name of the niche to score
    niche: The name of the niche to score
    market_data: Dictionary containing market analysis data
    market_data: Dictionary containing market analysis data
    problems: List of dictionaries containing problem data
    problems: List of dictionaries containing problem data


    Returns:
    Returns:
    Dictionary containing the opportunity score results
    Dictionary containing the opportunity score results
    """
    """
    # Generate a cache key based on inputs
    # Generate a cache key based on inputs
    cache_key = self._generate_cache_key(niche, market_data, problems)
    cache_key = self._generate_cache_key(niche, market_data, problems)


    # Try to get from cache first
    # Try to get from cache first
    cached_result = await run_in_thread(
    cached_result = await run_in_thread(
    default_cache.get, cache_key, namespace="opportunity_scores"
    default_cache.get, cache_key, namespace="opportunity_scores"
    )
    )
    if cached_result is not None:
    if cached_result is not None:
    return cached_result
    return cached_result


    # Run the scoring operation asynchronously to avoid blocking
    # Run the scoring operation asynchronously to avoid blocking
    # We'll use run_in_thread to run the CPU-intensive scoring in a separate thread
    # We'll use run_in_thread to run the CPU-intensive scoring in a separate thread
    result = await run_in_thread(
    result = await run_in_thread(
    self._score_opportunity_internal, niche, market_data, problems, cache_key
    self._score_opportunity_internal, niche, market_data, problems, cache_key
    )
    )


    return result
    return result


    def _score_opportunity_internal(
    def _score_opportunity_internal(
    self,
    self,
    niche: str,
    niche: str,
    market_data: Dict[str, Any],
    market_data: Dict[str, Any],
    problems: List[Dict[str, Any]],
    problems: List[Dict[str, Any]],
    cache_key: str,
    cache_key: str,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Internal method that performs the actual opportunity scoring.
    Internal method that performs the actual opportunity scoring.


    This is used by both the synchronous and asynchronous versions of score_opportunity.
    This is used by both the synchronous and asynchronous versions of score_opportunity.


    Args:
    Args:
    niche: The name of the niche to score
    niche: The name of the niche to score
    market_data: Dictionary containing market analysis data
    market_data: Dictionary containing market analysis data
    problems: List of dictionaries containing problem data
    problems: List of dictionaries containing problem data
    cache_key: Pre-generated cache key
    cache_key: Pre-generated cache key


    Returns:
    Returns:
    Dictionary containing the opportunity score results
    Dictionary containing the opportunity score results
    """
    """
    # Calculate factor scores
    # Calculate factor scores
    market_size_score = self._score_market_size(
    market_size_score = self._score_market_size(
    market_data.get("market_size", "unknown")
    market_data.get("market_size", "unknown")
    )
    )
    growth_rate_score = self._score_growth_rate(
    growth_rate_score = self._score_growth_rate(
    market_data.get("growth_rate", "unknown")
    market_data.get("growth_rate", "unknown")
    )
    )
    competition_score = self._score_competition(
    competition_score = self._score_competition(
    market_data.get("competition", "unknown")
    market_data.get("competition", "unknown")
    )
    )
    problem_severity_score = self._score_problem_severity(problems)
    problem_severity_score = self._score_problem_severity(problems)
    solution_feasibility_score = self._score_solution_feasibility(niche, problems)
    solution_feasibility_score = self._score_solution_feasibility(niche, problems)
    monetization_potential_score = self._score_monetization_potential(
    monetization_potential_score = self._score_monetization_potential(
    niche, market_data, problems
    niche, market_data, problems
    )
    )


    # Create factor scores schema objects
    # Create factor scores schema objects
    factor_scores = {
    factor_scores = {
    "market_size": FactorScoreSchema(
    "market_size": FactorScoreSchema(
    score=market_size_score,
    score=market_size_score,
    weight=self.weights["market_size"],
    weight=self.weights["market_size"],
    weighted_score=market_size_score * self.weights["market_size"],
    weighted_score=market_size_score * self.weights["market_size"],
    analysis=self._analyze_market_size(market_size_score),
    analysis=self._analyze_market_size(market_size_score),
    ),
    ),
    "growth_rate": FactorScoreSchema(
    "growth_rate": FactorScoreSchema(
    score=growth_rate_score,
    score=growth_rate_score,
    weight=self.weights["growth_rate"],
    weight=self.weights["growth_rate"],
    weighted_score=growth_rate_score * self.weights["growth_rate"],
    weighted_score=growth_rate_score * self.weights["growth_rate"],
    analysis=self._analyze_growth_rate(growth_rate_score),
    analysis=self._analyze_growth_rate(growth_rate_score),
    ),
    ),
    "competition": FactorScoreSchema(
    "competition": FactorScoreSchema(
    score=competition_score,
    score=competition_score,
    weight=self.weights["competition"],
    weight=self.weights["competition"],
    weighted_score=competition_score * self.weights["competition"],
    weighted_score=competition_score * self.weights["competition"],
    analysis=self._analyze_competition(competition_score),
    analysis=self._analyze_competition(competition_score),
    ),
    ),
    "problem_severity": FactorScoreSchema(
    "problem_severity": FactorScoreSchema(
    score=problem_severity_score,
    score=problem_severity_score,
    weight=self.weights["problem_severity"],
    weight=self.weights["problem_severity"],
    weighted_score=problem_severity_score
    weighted_score=problem_severity_score
    * self.weights["problem_severity"],
    * self.weights["problem_severity"],
    analysis=self._analyze_problem_severity(problem_severity_score),
    analysis=self._analyze_problem_severity(problem_severity_score),
    ),
    ),
    "solution_feasibility": FactorScoreSchema(
    "solution_feasibility": FactorScoreSchema(
    score=solution_feasibility_score,
    score=solution_feasibility_score,
    weight=self.weights["solution_feasibility"],
    weight=self.weights["solution_feasibility"],
    weighted_score=solution_feasibility_score
    weighted_score=solution_feasibility_score
    * self.weights["solution_feasibility"],
    * self.weights["solution_feasibility"],
    analysis=self._analyze_solution_feasibility(solution_feasibility_score),
    analysis=self._analyze_solution_feasibility(solution_feasibility_score),
    ),
    ),
    "monetization_potential": FactorScoreSchema(
    "monetization_potential": FactorScoreSchema(
    score=monetization_potential_score,
    score=monetization_potential_score,
    weight=self.weights["monetization_potential"],
    weight=self.weights["monetization_potential"],
    weighted_score=monetization_potential_score
    weighted_score=monetization_potential_score
    * self.weights["monetization_potential"],
    * self.weights["monetization_potential"],
    analysis=self._analyze_monetization_potential(
    analysis=self._analyze_monetization_potential(
    monetization_potential_score
    monetization_potential_score
    ),
    ),
    ),
    ),
    }
    }


    # Calculate the overall score (sum of weighted scores)
    # Calculate the overall score (sum of weighted scores)
    overall_score = sum(score.weighted_score for score in factor_scores.values())
    overall_score = sum(score.weighted_score for score in factor_scores.values())


    # Create the factors schema
    # Create the factors schema
    factors = FactorsSchema(
    factors = FactorsSchema(
    market_size=market_size_score,
    market_size=market_size_score,
    growth_rate=growth_rate_score,
    growth_rate=growth_rate_score,
    competition=competition_score,
    competition=competition_score,
    problem_severity=problem_severity_score,
    problem_severity=problem_severity_score,
    solution_feasibility=solution_feasibility_score,
    solution_feasibility=solution_feasibility_score,
    monetization_potential=monetization_potential_score,
    monetization_potential=monetization_potential_score,
    )
    )


    # Generate assessment and recommendations based on score
    # Generate assessment and recommendations based on score
    assessment, recommendations = self._generate_assessment_and_recommendations(
    assessment, recommendations = self._generate_assessment_and_recommendations(
    overall_score, factor_scores, niche
    overall_score, factor_scores, niche
    )
    )


    # Create the full opportunity score object
    # Create the full opportunity score object
    opportunity_score = OpportunityScoreSchema(
    opportunity_score = OpportunityScoreSchema(
    id=str(uuid.uuid4()),
    id=str(uuid.uuid4()),
    niche=niche,
    niche=niche,
    score=overall_score,
    score=overall_score,
    overall_score=overall_score,
    overall_score=overall_score,
    opportunity_assessment=assessment,
    opportunity_assessment=assessment,
    factor_scores=FactorScoresSchema(**factor_scores),
    factor_scores=FactorScoresSchema(**factor_scores),
    factors=factors,
    factors=factors,
    recommendations=recommendations,
    recommendations=recommendations,
    timestamp=datetime.now().isoformat(),
    timestamp=datetime.now().isoformat(),
    )
    )


    # Convert to dictionary for API compatibility
    # Convert to dictionary for API compatibility
    result = opportunity_score.dict()
    result = opportunity_score.dict()


    # Cache the result
    # Cache the result
    default_cache.set(
    default_cache.set(
    cache_key, result, ttl=self.cache_ttl, namespace="opportunity_scores"
    cache_key, result, ttl=self.cache_ttl, namespace="opportunity_scores"
    )
    )


    return result
    return result


    async def score_opportunities_batch_async(
    async def score_opportunities_batch_async(
    self,
    self,
    niches: List[str],
    niches: List[str],
    market_data_list: List[Dict[str, Any]],
    market_data_list: List[Dict[str, Any]],
    problems_list: List[List[Dict[str, Any]]],
    problems_list: List[List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Score multiple opportunities in parallel asynchronously.
    Score multiple opportunities in parallel asynchronously.


    This method processes multiple opportunity scoring tasks concurrently, which can
    This method processes multiple opportunity scoring tasks concurrently, which can
    significantly improve performance when scoring many opportunities.
    significantly improve performance when scoring many opportunities.


    Args:
    Args:
    niches: List of niche names to score
    niches: List of niche names to score
    market_data_list: List of market data dictionaries corresponding to each niche
    market_data_list: List of market data dictionaries corresponding to each niche
    problems_list: List of problem lists corresponding to each niche
    problems_list: List of problem lists corresponding to each niche


    Returns:
    Returns:
    List of opportunity score dictionaries
    List of opportunity score dictionaries
    """
    """
    # Validate input lengths match
    # Validate input lengths match
    if not (len(niches) == len(market_data_list) == len(problems_list)):
    if not (len(niches) == len(market_data_list) == len(problems_list)):
    raise ValueError("Input lists must have the same length")
    raise ValueError("Input lists must have the same length")


    # Create tasks for each opportunity scoring operation
    # Create tasks for each opportunity scoring operation
    tasks = []
    tasks = []
    for i in range(len(niches)):
    for i in range(len(niches)):
    tasks.append(
    tasks.append(
    self.score_opportunity_async(
    self.score_opportunity_async(
    niches[i], market_data_list[i], problems_list[i]
    niches[i], market_data_list[i], problems_list[i]
    )
    )
    )
    )


    # Run all tasks concurrently and gather results
    # Run all tasks concurrently and gather results
    results = await asyncio.gather(*tasks)
    results = await asyncio.gather(*tasks)


    return results
    return results


    async def analyze_and_compare_opportunities_async(
    async def analyze_and_compare_opportunities_async(
    self,
    self,
    niches: List[str],
    niches: List[str],
    market_data_list: List[Dict[str, Any]],
    market_data_list: List[Dict[str, Any]],
    problems_list: List[List[Dict[str, Any]]],
    problems_list: List[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Score multiple opportunities and compare them in one operation asynchronously.
    Score multiple opportunities and compare them in one operation asynchronously.


    This method combines scoring and comparison into a single asynchronous operation.
    This method combines scoring and comparison into a single asynchronous operation.


    Args:
    Args:
    niches: List of niche names to score
    niches: List of niche names to score
    market_data_list: List of market data dictionaries corresponding to each niche
    market_data_list: List of market data dictionaries corresponding to each niche
    problems_list: List of problem lists corresponding to each niche
    problems_list: List of problem lists corresponding to each niche


    Returns:
    Returns:
    Dictionary containing both individual scores and comparison results
    Dictionary containing both individual scores and comparison results
    """
    """
    # First score all opportunities in parallel
    # First score all opportunities in parallel
    opportunity_scores = await self.score_opportunities_batch_async(
    opportunity_scores = await self.score_opportunities_batch_async(
    niches, market_data_list, problems_list
    niches, market_data_list, problems_list
    )
    )


    # Then compare the opportunities
    # Then compare the opportunities
    comparison = await self.compare_opportunities_async(opportunity_scores)
    comparison = await self.compare_opportunities_async(opportunity_scores)


    # Return both individual scores and comparison
    # Return both individual scores and comparison
    return {"individual_scores": opportunity_scores, "comparison": comparison}
    return {"individual_scores": opportunity_scores, "comparison": comparison}


    def compare_opportunities(
    def compare_opportunities(
    self, opportunities: List[Dict[str, Any]]
    self, opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Compare multiple opportunities to identify the most promising ones.
    Compare multiple opportunities to identify the most promising ones.


    This method ranks opportunities by their overall scores, identifies the top
    This method ranks opportunities by their overall scores, identifies the top
    recommendation, and provides a comparative analysis across all opportunities.
    recommendation, and provides a comparative analysis across all opportunities.


    Algorithm:
    Algorithm:
    1. Sort opportunities by overall score
    1. Sort opportunities by overall score
    2. Assign ranks to each opportunity
    2. Assign ranks to each opportunity
    3. Identify the highest-scoring opportunity as the top recommendation
    3. Identify the highest-scoring opportunity as the top recommendation
    4. Calculate statistics like highest, lowest, average scores
    4. Calculate statistics like highest, lowest, average scores
    5. Generate comparative analysis and recommendations
    5. Generate comparative analysis and recommendations


    Args:
    Args:
    opportunities: List of opportunity dictionaries from score_opportunity
    opportunities: List of opportunity dictionaries from score_opportunity


    Returns:
    Returns:
    Dictionary containing the comparison results
    Dictionary containing the comparison results
    """
    """
    # Generate a cache key based on the opportunities
    # Generate a cache key based on the opportunities
    cache_key = self._generate_comparison_cache_key(opportunities)
    cache_key = self._generate_comparison_cache_key(opportunities)


    # Try to get from cache first
    # Try to get from cache first
    cached_result = default_cache.get(
    cached_result = default_cache.get(
    cache_key, namespace="opportunity_comparisons"
    cache_key, namespace="opportunity_comparisons"
    )
    )
    if cached_result is not None:
    if cached_result is not None:
    return cached_result
    return cached_result


    # Sort opportunities by overall score in descending order
    # Sort opportunities by overall score in descending order
    sorted_opportunities = sorted(
    sorted_opportunities = sorted(
    opportunities, key=lambda x: x.get("overall_score", 0.0), reverse=True
    opportunities, key=lambda x: x.get("overall_score", 0.0), reverse=True
    )
    )


    # Create ranked opportunities
    # Create ranked opportunities
    ranked_opportunities = []
    ranked_opportunities = []
    for i, opp in enumerate(sorted_opportunities):
    for i, opp in enumerate(sorted_opportunities):
    ranked_opportunities.append(
    ranked_opportunities.append(
    RankedOpportunitySchema(
    RankedOpportunitySchema(
    id=opp.get("id", str(uuid.uuid4())),
    id=opp.get("id", str(uuid.uuid4())),
    niche=opp.get("niche", "Unknown"),
    niche=opp.get("niche", "Unknown"),
    overall_score=opp.get("overall_score", 0.0),
    overall_score=opp.get("overall_score", 0.0),
    rank=i + 1,
    rank=i + 1,
    )
    )
    )
    )


    # Get top recommendation
    # Get top recommendation
    if ranked_opportunities:
    if ranked_opportunities:
    top_opp = sorted_opportunities[0]
    top_opp = sorted_opportunities[0]
    top_recommendation = TopRecommendationSchema(
    top_recommendation = TopRecommendationSchema(
    id=top_opp.get("id", str(uuid.uuid4())),
    id=top_opp.get("id", str(uuid.uuid4())),
    niche=top_opp.get("niche", "Unknown"),
    niche=top_opp.get("niche", "Unknown"),
    overall_score=top_opp.get("overall_score", 0.0),
    overall_score=top_opp.get("overall_score", 0.0),
    assessment=top_opp.get("opportunity_assessment", ""),
    assessment=top_opp.get("opportunity_assessment", ""),
    next_steps=self._generate_next_steps(top_opp),
    next_steps=self._generate_next_steps(top_opp),
    )
    )
    else:
    else:
    top_recommendation = None
    top_recommendation = None


    # Calculate score distribution
    # Calculate score distribution
    score_distribution = self._calculate_score_distribution(sorted_opportunities)
    score_distribution = self._calculate_score_distribution(sorted_opportunities)


    # Calculate statistics
    # Calculate statistics
    highest_score = (
    highest_score = (
    max([opp.get("overall_score", 0.0) for opp in sorted_opportunities])
    max([opp.get("overall_score", 0.0) for opp in sorted_opportunities])
    if sorted_opportunities
    if sorted_opportunities
    else None
    else None
    )
    )
    lowest_score = (
    lowest_score = (
    min([opp.get("overall_score", 0.0) for opp in sorted_opportunities])
    min([opp.get("overall_score", 0.0) for opp in sorted_opportunities])
    if sorted_opportunities
    if sorted_opportunities
    else None
    else None
    )
    )
    average_score = (
    average_score = (
    sum([opp.get("overall_score", 0.0) for opp in sorted_opportunities])
    sum([opp.get("overall_score", 0.0) for opp in sorted_opportunities])
    / len(sorted_opportunities)
    / len(sorted_opportunities)
    if sorted_opportunities
    if sorted_opportunities
    else None
    else None
    )
    )


    # Create comparative analysis
    # Create comparative analysis
    comparative_analysis = ComparativeAnalysisSchema(
    comparative_analysis = ComparativeAnalysisSchema(
    highest_score=highest_score,
    highest_score=highest_score,
    lowest_score=lowest_score,
    lowest_score=lowest_score,
    average_score=average_score,
    average_score=average_score,
    score_distribution=score_distribution,
    score_distribution=score_distribution,
    )
    )


    # Create comparison factors
    # Create comparison factors
    comparison_factors = self._generate_comparison_factors(sorted_opportunities)
    comparison_factors = self._generate_comparison_factors(sorted_opportunities)


    # Generate recommendations based on comparison
    # Generate recommendations based on comparison
    recommendations = self._generate_comparison_recommendations(
    recommendations = self._generate_comparison_recommendations(
    sorted_opportunities, comparative_analysis
    sorted_opportunities, comparative_analysis
    )
    )


    # Create the full comparison result
    # Create the full comparison result
    comparison_result = OpportunityComparisonSchema(
    comparison_result = OpportunityComparisonSchema(
    id=str(uuid.uuid4()),
    id=str(uuid.uuid4()),
    opportunities_count=len(opportunities),
    opportunities_count=len(opportunities),
    ranked_opportunities=ranked_opportunities,
    ranked_opportunities=ranked_opportunities,
    top_recommendation=top_recommendation,
    top_recommendation=top_recommendation,
    comparison_factors=comparison_factors,
    comparison_factors=comparison_factors,
    comparative_analysis=comparative_analysis,
    comparative_analysis=comparative_analysis,
    recommendations=recommendations,
    recommendations=recommendations,
    timestamp=datetime.now().isoformat(),
    timestamp=datetime.now().isoformat(),
    )
    )


    # Convert to dictionary for API compatibility
    # Convert to dictionary for API compatibility
    result = comparison_result.dict()
    result = comparison_result.dict()


    # Cache the result
    # Cache the result
    default_cache.set(
    default_cache.set(
    cache_key, result, ttl=self.cache_ttl, namespace="opportunity_comparisons"
    cache_key, result, ttl=self.cache_ttl, namespace="opportunity_comparisons"
    )
    )


    return result
    return result


    async def compare_opportunities_async(
    async def compare_opportunities_async(
    self, opportunities: List[Dict[str, Any]]
    self, opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Asynchronously compare multiple opportunities to identify the most promising ones.
    Asynchronously compare multiple opportunities to identify the most promising ones.


    This method is the asynchronous version of compare_opportunities and should be used
    This method is the asynchronous version of compare_opportunities and should be used
    in an async context. It performs the same ranking and analysis but doesn't block
    in an async context. It performs the same ranking and analysis but doesn't block
    the event loop.
    the event loop.


    Args:
    Args:
    opportunities: List of opportunity dictionaries from score_opportunity
    opportunities: List of opportunity dictionaries from score_opportunity


    Returns:
    Returns:
    Dictionary containing the comparison results
    Dictionary containing the comparison results
    """
    """
    async with self._lock:
    async with self._lock:
    return await run_in_thread(self.compare_opportunities, opportunities)
    return await run_in_thread(self.compare_opportunities, opportunities)


    def get_scoring_factors(self) -> List[str]:
    def get_scoring_factors(self) -> List[str]:
    """
    """
    Get a list of scoring factors used by the OpportunityScorer.
    Get a list of scoring factors used by the OpportunityScorer.


    Returns:
    Returns:
    List of scoring factor names
    List of scoring factor names
    """
    """
    return list(self.weights.keys())
    return list(self.weights.keys())


    async def get_scoring_factors_async(self) -> List[str]:
    async def get_scoring_factors_async(self) -> List[str]:
    """
    """
    Asynchronously get a list of scoring factors used by the OpportunityScorer.
    Asynchronously get a list of scoring factors used by the OpportunityScorer.


    Returns:
    Returns:
    List of scoring factor names
    List of scoring factor names
    """
    """
    return self.weights.keys()
    return self.weights.keys()


    def _generate_cache_key(
    def _generate_cache_key(
    self, niche: str, market_data: Dict[str, Any], problems: List[Dict[str, Any]]
    self, niche: str, market_data: Dict[str, Any], problems: List[Dict[str, Any]]
    ) -> str:
    ) -> str:
    """
    """
    Generate a cache key for opportunity scoring results.
    Generate a cache key for opportunity scoring results.


    Args:
    Args:
    niche: The niche name
    niche: The niche name
    market_data: Market data dictionary
    market_data: Market data dictionary
    problems: List of problem dictionaries
    problems: List of problem dictionaries


    Returns:
    Returns:
    Cache key string
    Cache key string
    """
    """
    # Create a stable representation of the inputs
    # Create a stable representation of the inputs
    key_data = {
    key_data = {
    "niche": niche,
    "niche": niche,
    "market_data": market_data,
    "market_data": market_data,
    "problems": self._normalize_problems_for_cache(problems),
    "problems": self._normalize_problems_for_cache(problems),
    "weights": self.weights,
    "weights": self.weights,
    }
    }


    # Convert to stable string representation
    # Convert to stable string representation
    key_str = json.dumps(key_data, sort_keys=True)
    key_str = json.dumps(key_data, sort_keys=True)


    # Hash to get a fixed-length key
    # Hash to get a fixed-length key
    return hashlib.md5(key_str.encode()).hexdigest()
    return hashlib.md5(key_str.encode()).hexdigest()


    def _normalize_problems_for_cache(
    def _normalize_problems_for_cache(
    self, problems: List[Dict[str, Any]]
    self, problems: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Normalize problem dictionaries to ensure stable cache keys.
    Normalize problem dictionaries to ensure stable cache keys.


    Args:
    Args:
    problems: List of problem dictionaries
    problems: List of problem dictionaries


    Returns:
    Returns:
    Normalized list of problem dictionaries
    Normalized list of problem dictionaries
    """
    """
    normalized = []
    normalized = []


    # Extract only the fields needed for scoring to reduce key size
    # Extract only the fields needed for scoring to reduce key size
    for problem in problems:
    for problem in problems:
    normalized.append(
    normalized.append(
    {
    {
    "severity": problem.get("severity", "low"),
    "severity": problem.get("severity", "low"),
    "description": problem.get("description", ""),
    "description": problem.get("description", ""),
    }
    }
    )
    )


    # Sort by description for stable order
    # Sort by description for stable order
    return sorted(normalized, key=lambda p: p["description"])
    return sorted(normalized, key=lambda p: p["description"])


    def _generate_comparison_cache_key(
    def _generate_comparison_cache_key(
    self, opportunities: List[Dict[str, Any]]
    self, opportunities: List[Dict[str, Any]]
    ) -> str:
    ) -> str:
    """
    """
    Generate a cache key for opportunity comparison results.
    Generate a cache key for opportunity comparison results.


    Args:
    Args:
    opportunities: List of opportunity dictionaries
    opportunities: List of opportunity dictionaries


    Returns:
    Returns:
    Cache key string
    Cache key string
    """
    """
    # Get a stable representation of the opportunities
    # Get a stable representation of the opportunities
    key_parts = []
    key_parts = []


    for opp in opportunities:
    for opp in opportunities:
    # Use ID and score as the most important parts for comparison
    # Use ID and score as the most important parts for comparison
    key_parts.append(
    key_parts.append(
    {
    {
    "id": opp.get("id", ""),
    "id": opp.get("id", ""),
    "niche": opp.get("niche", ""),
    "niche": opp.get("niche", ""),
    "overall_score": opp.get("overall_score", 0.0),
    "overall_score": opp.get("overall_score", 0.0),
    }
    }
    )
    )


    # Sort by ID for stable order
    # Sort by ID for stable order
    key_parts.sort(key=lambda p: p["id"])
    key_parts.sort(key=lambda p: p["id"])


    # Convert to stable string representation and hash
    # Convert to stable string representation and hash
    key_str = json.dumps(key_parts, sort_keys=True)
    key_str = json.dumps(key_parts, sort_keys=True)
    return hashlib.md5(key_str.encode()).hexdigest()
    return hashlib.md5(key_str.encode()).hexdigest()


    def invalidate_opportunity_cache(self, niche: Optional[str] = None) -> bool:
    def invalidate_opportunity_cache(self, niche: Optional[str] = None) -> bool:
    """
    """
    Invalidate cached opportunity scores.
    Invalidate cached opportunity scores.


    Args:
    Args:
    niche: Optional niche name to invalidate. If None, invalidates all cached scores.
    niche: Optional niche name to invalidate. If None, invalidates all cached scores.


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    if niche is None:
    if niche is None:
    # Clear all opportunity scores
    # Clear all opportunity scores
    return default_cache.clear(namespace="opportunity_scores")
    return default_cache.clear(namespace="opportunity_scores")
    else:
    else:
    # TODO: For a more targeted approach, we would need to store
    # TODO: For a more targeted approach, we would need to store
    # a mapping of niches to cache keys. For now, we clear all.
    # a mapping of niches to cache keys. For now, we clear all.
    return default_cache.clear(namespace="opportunity_scores")
    return default_cache.clear(namespace="opportunity_scores")


    async def invalidate_opportunity_cache_async(
    async def invalidate_opportunity_cache_async(
    self, niche: Optional[str] = None
    self, niche: Optional[str] = None
    ) -> bool:
    ) -> bool:
    """
    """
    Asynchronously invalidate cached opportunity scores.
    Asynchronously invalidate cached opportunity scores.


    Args:
    Args:
    niche: Optional niche name to invalidate. If None, invalidates all cached scores.
    niche: Optional niche name to invalidate. If None, invalidates all cached scores.


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    return await run_in_thread(self.invalidate_opportunity_cache, niche)
    return await run_in_thread(self.invalidate_opportunity_cache, niche)


    def invalidate_comparison_cache(self) -> bool:
    def invalidate_comparison_cache(self) -> bool:
    """
    """
    Invalidate all cached opportunity comparisons.
    Invalidate all cached opportunity comparisons.


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    return default_cache.clear(namespace="opportunity_comparisons")
    return default_cache.clear(namespace="opportunity_comparisons")


    async def invalidate_comparison_cache_async(self) -> bool:
    async def invalidate_comparison_cache_async(self) -> bool:
    """
    """
    Asynchronously invalidate all cached opportunity comparisons.
    Asynchronously invalidate all cached opportunity comparisons.


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    return await run_in_thread(self.invalidate_comparison_cache)
    return await run_in_thread(self.invalidate_comparison_cache)


    def _score_market_size(self, market_size: str) -> float:
    def _score_market_size(self, market_size: str) -> float:
    """
    """
    Score the market size factor.
    Score the market size factor.


    This method converts a qualitative market size assessment to a numerical
    This method converts a qualitative market size assessment to a numerical
    score between 0 and 1.
    score between 0 and 1.


    Algorithm:
    Algorithm:
    - "large" -> 0.9
    - "large" -> 0.9
    - "medium" -> 0.6
    - "medium" -> 0.6
    - "small" -> 0.3
    - "small" -> 0.3
    - "unknown" -> 0.5 (neutral)
    - "unknown" -> 0.5 (neutral)


    Args:
    Args:
    market_size: Qualitative assessment of market size
    market_size: Qualitative assessment of market size


    Returns:
    Returns:
    Market size score between 0 and 1
    Market size score between 0 and 1
    """
    """
    market_size_scores = {"large": 0.9, "medium": 0.6, "small": 0.3, "unknown": 0.5}
    market_size_scores = {"large": 0.9, "medium": 0.6, "small": 0.3, "unknown": 0.5}
    return market_size_scores.get(market_size.lower(), 0.5)
    return market_size_scores.get(market_size.lower(), 0.5)


    def _score_growth_rate(self, growth_rate: str) -> float:
    def _score_growth_rate(self, growth_rate: str) -> float:
    """
    """
    Score the growth rate factor.
    Score the growth rate factor.


    This method converts a qualitative growth rate assessment to a numerical
    This method converts a qualitative growth rate assessment to a numerical
    score between 0 and 1.
    score between 0 and 1.


    Algorithm:
    Algorithm:
    - "high" -> 0.9
    - "high" -> 0.9
    - "medium" -> 0.6
    - "medium" -> 0.6
    - "low" -> 0.3
    - "low" -> 0.3
    - "unknown" -> 0.5 (neutral)
    - "unknown" -> 0.5 (neutral)


    Args:
    Args:
    growth_rate: Qualitative assessment of growth rate
    growth_rate: Qualitative assessment of growth rate


    Returns:
    Returns:
    Growth rate score between 0 and 1
    Growth rate score between 0 and 1
    """
    """
    growth_rate_scores = {"high": 0.9, "medium": 0.6, "low": 0.3, "unknown": 0.5}
    growth_rate_scores = {"high": 0.9, "medium": 0.6, "low": 0.3, "unknown": 0.5}
    return growth_rate_scores.get(growth_rate.lower(), 0.5)
    return growth_rate_scores.get(growth_rate.lower(), 0.5)


    def _score_competition(self, competition: str) -> float:
    def _score_competition(self, competition: str) -> float:
    """
    """
    Score the competition factor.
    Score the competition factor.


    This method converts a qualitative competition assessment to a numerical
    This method converts a qualitative competition assessment to a numerical
    score between 0 and 1. Note that this is inverted - lower competition
    score between 0 and 1. Note that this is inverted - lower competition
    results in a higher score.
    results in a higher score.


    Algorithm:
    Algorithm:
    - "low" -> 0.9 (less competition is better)
    - "low" -> 0.9 (less competition is better)
    - "medium" -> 0.5
    - "medium" -> 0.5
    - "high" -> 0.2 (high competition is worse)
    - "high" -> 0.2 (high competition is worse)
    - "unknown" -> 0.5 (neutral)
    - "unknown" -> 0.5 (neutral)


    Args:
    Args:
    competition: Qualitative assessment of competition
    competition: Qualitative assessment of competition


    Returns:
    Returns:
    Competition score between 0 and 1
    Competition score between 0 and 1
    """
    """
    competition_scores = {"low": 0.9, "medium": 0.5, "high": 0.2, "unknown": 0.5}
    competition_scores = {"low": 0.9, "medium": 0.5, "high": 0.2, "unknown": 0.5}
    return competition_scores.get(competition.lower(), 0.5)
    return competition_scores.get(competition.lower(), 0.5)


    def _score_problem_severity(self, problems: List[Dict[str, Any]]) -> float:
    def _score_problem_severity(self, problems: List[Dict[str, Any]]) -> float:
    """
    """
    Score the problem severity factor.
    Score the problem severity factor.


    This method calculates a score based on the severity of problems identified
    This method calculates a score based on the severity of problems identified
    in the niche. Higher severity problems lead to higher scores.
    in the niche. Higher severity problems lead to higher scores.


    Algorithm:
    Algorithm:
    1. For each problem, convert severity to a numerical value:
    1. For each problem, convert severity to a numerical value:
    - "high" -> 1.0
    - "high" -> 1.0
    - "medium" -> 0.6
    - "medium" -> 0.6
    - "low" -> 0.3
    - "low" -> 0.3
    2. Calculate weighted average of problem severities
    2. Calculate weighted average of problem severities
    3. If no problems are provided, return 0 (no opportunity without problems)
    3. If no problems are provided, return 0 (no opportunity without problems)


    Args:
    Args:
    problems: List of problem dictionaries
    problems: List of problem dictionaries


    Returns:
    Returns:
    Problem severity score between 0 and 1
    Problem severity score between 0 and 1
    """
    """
    if not problems:
    if not problems:
    return 0.0
    return 0.0


    severity_scores = {"high": 1.0, "medium": 0.6, "low": 0.3}
    severity_scores = {"high": 1.0, "medium": 0.6, "low": 0.3}


    # Calculate average severity
    # Calculate average severity
    total_severity = sum(
    total_severity = sum(
    severity_scores.get(p.get("severity", "low").lower(), 0.0) for p in problems
    severity_scores.get(p.get("severity", "low").lower(), 0.0) for p in problems
    )
    )
    return total_severity / len(problems)
    return total_severity / len(problems)


    def _score_solution_feasibility(
    def _score_solution_feasibility(
    self, niche: str, problems: List[Dict[str, Any]]
    self, niche: str, problems: List[Dict[str, Any]]
    ) -> float:
    ) -> float:
    """
    """
    Score the solution feasibility factor.
    Score the solution feasibility factor.


    This method evaluates how feasible it is to create an AI-powered solution
    This method evaluates how feasible it is to create an AI-powered solution
    for the identified problems in the niche.
    for the identified problems in the niche.


    Algorithm:
    Algorithm:
    1. Base feasibility starts at 0.7 (moderately feasible)
    1. Base feasibility starts at 0.7 (moderately feasible)
    2. Adjust based on niche characteristics:
    2. Adjust based on niche characteristics:
    - Text/content-focused niches (higher feasibility for AI)
    - Text/content-focused niches (higher feasibility for AI)
    - Data processing niches (higher feasibility)
    - Data processing niches (higher feasibility)
    - Physical product niches (lower feasibility)
    - Physical product niches (lower feasibility)
    3. Normalize to ensure score is between 0 and 1
    3. Normalize to ensure score is between 0 and 1


    Args:
    Args:
    niche: Name of the niche
    niche: Name of the niche
    problems: List of problem dictionaries
    problems: List of problem dictionaries


    Returns:
    Returns:
    Solution feasibility score between 0 and 1
    Solution feasibility score between 0 and 1
    """
    """
    # Start with a base feasibility score
    # Start with a base feasibility score
    base_feasibility = 0.7
    base_feasibility = 0.7


    # Adjust based on niche type
    # Adjust based on niche type
    # Text/content niches are more feasible for AI solutions
    # Text/content niches are more feasible for AI solutions
    text_content_niches = [
    text_content_niches = [
    "content",
    "content",
    "writing",
    "writing",
    "translation",
    "translation",
    "summarization",
    "summarization",
    "description",
    "description",
    "copywriting",
    "copywriting",
    "editing",
    "editing",
    ]
    ]


    # Data processing niches are also more feasible
    # Data processing niches are also more feasible
    data_niches = [
    data_niches = [
    "analytics",
    "analytics",
    "analysis",
    "analysis",
    "reporting",
    "reporting",
    "monitoring",
    "monitoring",
    "tracking",
    "tracking",
    "management",
    "management",
    "automation",
    "automation",
    ]
    ]


    # Adjust score based on niche keywords
    # Adjust score based on niche keywords
    niche_lower = niche.lower()
    niche_lower = niche.lower()


    # Check for text/content niche keywords
    # Check for text/content niche keywords
    if any(keyword in niche_lower for keyword in text_content_niches):
    if any(keyword in niche_lower for keyword in text_content_niches):
    base_feasibility += 0.2
    base_feasibility += 0.2


    # Check for data niche keywords
    # Check for data niche keywords
    if any(keyword in niche_lower for keyword in data_niches):
    if any(keyword in niche_lower for keyword in data_niches):
    base_feasibility += 0.1
    base_feasibility += 0.1


    # Ensure the score is between 0 and 1
    # Ensure the score is between 0 and 1
    return min(max(base_feasibility, 0.0), 1.0)
    return min(max(base_feasibility, 0.0), 1.0)


    def _score_monetization_potential(
    def _score_monetization_potential(
    self, niche: str, market_data: Dict[str, Any], problems: List[Dict[str, Any]]
    self, niche: str, market_data: Dict[str, Any], problems: List[Dict[str, Any]]
    ) -> float:
    ) -> float:
    """
    """
    Score the monetization potential factor.
    Score the monetization potential factor.


    This method evaluates the potential to monetize a solution in the niche.
    This method evaluates the potential to monetize a solution in the niche.


    Algorithm:
    Algorithm:
    1. Base potential starts at 0.5 (moderate potential)
    1. Base potential starts at 0.5 (moderate potential)
    2. Adjust based on market size and growth rate:
    2. Adjust based on market size and growth rate:
    - Larger markets have higher monetization potential
    - Larger markets have higher monetization potential
    - Higher growth rates increase potential
    - Higher growth rates increase potential
    3. Adjust based on problem severity:
    3. Adjust based on problem severity:
    - More severe problems generally have higher willingness to pay
    - More severe problems generally have higher willingness to pay
    4. Normalize to ensure score is between 0 and 1
    4. Normalize to ensure score is between 0 and 1


    Args:
    Args:
    niche: Name of the niche
    niche: Name of the niche
    market_data: Dictionary containing market analysis data
    market_data: Dictionary containing market analysis data
    problems: List of problem dictionaries
    problems: List of problem dictionaries


    Returns:
    Returns:
    Monetization potential score between 0 and 1
    Monetization potential score between 0 and 1
    """
    """
    # Start with base monetization potential
    # Start with base monetization potential
    base_potential = 0.5
    base_potential = 0.5


    # Adjust for market size
    # Adjust for market size
    market_size = market_data.get("market_size", "unknown").lower()
    market_size = market_data.get("market_size", "unknown").lower()
    if market_size == "large":
    if market_size == "large":
    base_potential += 0.2
    base_potential += 0.2
    elif market_size == "medium":
    elif market_size == "medium":
    base_potential += 0.1
    base_potential += 0.1
    elif market_size == "small":
    elif market_size == "small":
    base_potential -= 0.1
    base_potential -= 0.1


    # Adjust for growth rate
    # Adjust for growth rate
    growth_rate = market_data.get("growth_rate", "unknown").lower()
    growth_rate = market_data.get("growth_rate", "unknown").lower()
    if growth_rate == "high":
    if growth_rate == "high":
    base_potential += 0.2
    base_potential += 0.2
    elif growth_rate == "medium":
    elif growth_rate == "medium":
    base_potential += 0.1
    base_potential += 0.1
    elif growth_rate == "low":
    elif growth_rate == "low":
    base_potential -= 0.1
    base_potential -= 0.1


    # Adjust for problem severity (more severe = higher willingness to pay)
    # Adjust for problem severity (more severe = higher willingness to pay)
    problem_severity = self._score_problem_severity(problems)
    problem_severity = self._score_problem_severity(problems)
    if problem_severity > 0.7:
    if problem_severity > 0.7:
    base_potential += 0.1
    base_potential += 0.1


    # Business-oriented niches typically have higher monetization potential
    # Business-oriented niches typically have higher monetization potential
    business_keywords = [
    business_keywords = [
    "business",
    "business",
    "enterprise",
    "enterprise",
    "professional",
    "professional",
    "b2b",
    "b2b",
    "management",
    "management",
    "productivity",
    "productivity",
    "efficiency",
    "efficiency",
    ]
    ]


    # Check for business niche keywords
    # Check for business niche keywords
    niche_lower = niche.lower()
    niche_lower = niche.lower()
    if any(keyword in niche_lower for keyword in business_keywords):
    if any(keyword in niche_lower for keyword in business_keywords):
    base_potential += 0.1
    base_potential += 0.1


    # Ensure the score is between 0 and 1
    # Ensure the score is between 0 and 1
    return min(max(base_potential, 0.0), 1.0)
    return min(max(base_potential, 0.0), 1.0)


    def _analyze_market_size(self, score: float) -> str:
    def _analyze_market_size(self, score: float) -> str:
    """
    """
    Generate analysis text for market size score.
    Generate analysis text for market size score.


    Args:
    Args:
    score: Market size score between 0 and 1
    score: Market size score between 0 and 1


    Returns:
    Returns:
    Analysis text for the market size factor
    Analysis text for the market size factor
    """
    """
    if score >= 0.8:
    if score >= 0.8:
    return "Large market size with significant potential customer base."
    return "Large market size with significant potential customer base."
    elif score >= 0.5:
    elif score >= 0.5:
    return "Medium market size with a reasonable potential customer base."
    return "Medium market size with a reasonable potential customer base."
    else:
    else:
    return "Small market size with limited potential customer base."
    return "Small market size with limited potential customer base."


    def _analyze_growth_rate(self, score: float) -> str:
    def _analyze_growth_rate(self, score: float) -> str:
    """
    """
    Generate analysis text for growth rate score.
    Generate analysis text for growth rate score.


    Args:
    Args:
    score: Growth rate score between 0 and 1
    score: Growth rate score between 0 and 1


    Returns:
    Returns:
    Analysis text for the growth rate factor
    Analysis text for the growth rate factor
    """
    """
    if score >= 0.8:
    if score >= 0.8:
    return "High growth rate indicating a rapidly expanding market opportunity."
    return "High growth rate indicating a rapidly expanding market opportunity."
    elif score >= 0.5:
    elif score >= 0.5:
    return "Moderate growth rate showing steady market expansion."
    return "Moderate growth rate showing steady market expansion."
    else:
    else:
    return "Low growth rate indicating a stable or declining market."
    return "Low growth rate indicating a stable or declining market."


    def _analyze_competition(self, score: float) -> str:
    def _analyze_competition(self, score: float) -> str:
    """
    """
    Generate analysis text for competition score.
    Generate analysis text for competition score.


    Args:
    Args:
    score: Competition score between 0 and 1
    score: Competition score between 0 and 1


    Returns:
    Returns:
    Analysis text for the competition factor
    Analysis text for the competition factor
    """
    """
    if score >= 0.8:
    if score >= 0.8:
    return "Low competition level with few established solutions."
    return "Low competition level with few established solutions."
    elif score >= 0.5:
    elif score >= 0.5:
    return "Moderate competition with some established solutions."
    return "Moderate competition with some established solutions."
    else:
    else:
    return "High competition with many established solutions."
    return "High competition with many established solutions."


    def _analyze_problem_severity(self, score: float) -> str:
    def _analyze_problem_severity(self, score: float) -> str:
    """
    """
    Generate analysis text for problem severity score.
    Generate analysis text for problem severity score.


    Args:
    Args:
    score: Problem severity score between 0 and 1
    score: Problem severity score between 0 and 1


    Returns:
    Returns:
    Analysis text for the problem severity factor
    Analysis text for the problem severity factor
    """
    """
    if score >= 0.8:
    if score >= 0.8:
    return (
    return (
    "High severity problems indicating significant pain points for users."
    "High severity problems indicating significant pain points for users."
    )
    )
    elif score >= 0.5:
    elif score >= 0.5:
    return "Moderate severity problems with notable impact on users."
    return "Moderate severity problems with notable impact on users."
    else:
    else:
    return "Low severity problems with minimal impact on users."
    return "Low severity problems with minimal impact on users."


    def _analyze_solution_feasibility(self, score: float) -> str:
    def _analyze_solution_feasibility(self, score: float) -> str:
    """
    """
    Generate analysis text for solution feasibility score.
    Generate analysis text for solution feasibility score.


    Args:
    Args:
    score: Solution feasibility score between 0 and 1
    score: Solution feasibility score between 0 and 1


    Returns:
    Returns:
    Analysis text for the solution feasibility factor
    Analysis text for the solution feasibility factor
    """
    """
    if score >= 0.8:
    if score >= 0.8:
    return "Highly feasible solution that can be readily implemented with AI technology."
    return "Highly feasible solution that can be readily implemented with AI technology."
    elif score >= 0.5:
    elif score >= 0.5:
    return "Moderately feasible solution with some implementation challenges."
    return "Moderately feasible solution with some implementation challenges."
    else:
    else:
    return "Challenging solution with significant technical barriers to implementation."
    return "Challenging solution with significant technical barriers to implementation."


    def _analyze_monetization_potential(self, score: float) -> str:
    def _analyze_monetization_potential(self, score: float) -> str:
    """
    """
    Generate analysis text for monetization potential score.
    Generate analysis text for monetization potential score.


    Args:
    Args:
    score: Monetization potential score between 0 and 1
    score: Monetization potential score between 0 and 1


    Returns:
    Returns:
    Analysis text for the monetization potential factor
    Analysis text for the monetization potential factor
    """
    """
    if score >= 0.8:
    if score >= 0.8:
    return "High monetization potential with strong willingness to pay."
    return "High monetization potential with strong willingness to pay."
    elif score >= 0.5:
    elif score >= 0.5:
    return "Moderate monetization potential with reasonable willingness to pay."
    return "Moderate monetization potential with reasonable willingness to pay."
    else:
    else:
    return "Limited monetization potential with low willingness to pay."
    return "Limited monetization potential with low willingness to pay."


    def _generate_assessment_and_recommendations(
    def _generate_assessment_and_recommendations(
    self, score: float, factor_scores: Dict[str, FactorScoreSchema], niche: str
    self, score: float, factor_scores: Dict[str, FactorScoreSchema], niche: str
    ) -> tuple:
    ) -> tuple:
    """
    """
    Generate opportunity assessment and recommendations based on the overall score.
    Generate opportunity assessment and recommendations based on the overall score.


    Algorithm:
    Algorithm:
    1. Determine assessment text category based on score range
    1. Determine assessment text category based on score range
    2. Identify strengths (high-scoring factors)
    2. Identify strengths (high-scoring factors)
    3. Identify weaknesses (low-scoring factors)
    3. Identify weaknesses (low-scoring factors)
    4. Generate actionable recommendations based on the overall assessment and factor scores
    4. Generate actionable recommendations based on the overall assessment and factor scores


    Args:
    Args:
    score: Overall opportunity score
    score: Overall opportunity score
    factor_scores: Dictionary of factor scores
    factor_scores: Dictionary of factor scores
    niche: Name of the niche
    niche: Name of the niche


    Returns:
    Returns:
    Tuple of (assessment text, list of recommendation strings)
    Tuple of (assessment text, list of recommendation strings)
    """
    """
    # Generate assessment text
    # Generate assessment text
    if score >= 0.8:
    if score >= 0.8:
    assessment = "Excellent opportunity with high potential"
    assessment = "Excellent opportunity with high potential"
    elif score >= 0.6:
    elif score >= 0.6:
    assessment = "Very good opportunity worth pursuing"
    assessment = "Very good opportunity worth pursuing"
    elif score >= 0.4:
    elif score >= 0.4:
    assessment = "Good opportunity with moderate potential"
    assessment = "Good opportunity with moderate potential"
    elif score >= 0.2:
    elif score >= 0.2:
    assessment = "Fair opportunity with limited potential"
    assessment = "Fair opportunity with limited potential"
    else:
    else:
    assessment = "Limited opportunity with minimal potential"
    assessment = "Limited opportunity with minimal potential"


    # Generate recommendations
    # Generate recommendations
    recommendations = []
    recommendations = []


    # Add general recommendation based on score
    # Add general recommendation based on score
    if score >= 0.8:
    if score >= 0.8:
    recommendations.append("Proceed with high priority")
    recommendations.append("Proceed with high priority")
    recommendations.append("Allocate significant resources")
    recommendations.append("Allocate significant resources")
    recommendations.append("Develop a comprehensive implementation plan")
    recommendations.append("Develop a comprehensive implementation plan")
    elif score >= 0.6:
    elif score >= 0.6:
    recommendations.append("Proceed with medium-high priority")
    recommendations.append("Proceed with medium-high priority")
    recommendations.append("Allocate appropriate resources")
    recommendations.append("Allocate appropriate resources")
    recommendations.append("Develop an implementation plan")
    recommendations.append("Develop an implementation plan")
    elif score >= 0.4:
    elif score >= 0.4:
    recommendations.append("Proceed with medium priority")
    recommendations.append("Proceed with medium priority")
    recommendations.append("Allocate moderate resources")
    recommendations.append("Allocate moderate resources")
    recommendations.append("Develop an initial implementation plan")
    recommendations.append("Develop an initial implementation plan")
    elif score >= 0.2:
    elif score >= 0.2:
    recommendations.append("Proceed with caution")
    recommendations.append("Proceed with caution")
    recommendations.append("Allocate limited resources for exploration")
    recommendations.append("Allocate limited resources for exploration")
    recommendations.append("Consider further research before proceeding")
    recommendations.append("Consider further research before proceeding")
    else:
    else:
    recommendations.append("Deprioritize this opportunity")
    recommendations.append("Deprioritize this opportunity")
    recommendations.append("Consider alternatives")
    recommendations.append("Consider alternatives")
    recommendations.append("Reassess if market conditions change")
    recommendations.append("Reassess if market conditions change")


    # Add specific recommendations based on factor scores
    # Add specific recommendations based on factor scores
    strengths = []
    strengths = []
    weaknesses = []
    weaknesses = []


    # Identify strengths and weaknesses
    # Identify strengths and weaknesses
    for factor_name, factor_score in factor_scores.items():
    for factor_name, factor_score in factor_scores.items():
    if factor_score.score >= 0.7:
    if factor_score.score >= 0.7:
    strengths.append(factor_name)
    strengths.append(factor_name)
    elif factor_score.score <= 0.4:
    elif factor_score.score <= 0.4:
    weaknesses.append(factor_name)
    weaknesses.append(factor_name)


    # Add recommendations based on strengths
    # Add recommendations based on strengths
    if "market_size" in strengths:
    if "market_size" in strengths:
    recommendations.append(
    recommendations.append(
    f"Leverage the large market size in the {niche} niche"
    f"Leverage the large market size in the {niche} niche"
    )
    )


    if "growth_rate" in strengths:
    if "growth_rate" in strengths:
    recommendations.append(f"Position for rapid growth in the {niche} niche")
    recommendations.append(f"Position for rapid growth in the {niche} niche")


    if "competition" in strengths:
    if "competition" in strengths:
    recommendations.append("Capitalize on the low competition environment")
    recommendations.append("Capitalize on the low competition environment")


    if "problem_severity" in strengths:
    if "problem_severity" in strengths:
    recommendations.append("Emphasize the significant pain point being solved")
    recommendations.append("Emphasize the significant pain point being solved")


    if "solution_feasibility" in strengths:
    if "solution_feasibility" in strengths:
    recommendations.append(
    recommendations.append(
    "Move quickly to implement the technically feasible solution"
    "Move quickly to implement the technically feasible solution"
    )
    )


    if "monetization_potential" in strengths:
    if "monetization_potential" in strengths:
    recommendations.append(
    recommendations.append(
    "Develop a premium pricing strategy based on high willingness to pay"
    "Develop a premium pricing strategy based on high willingness to pay"
    )
    )


    # Add recommendations based on weaknesses
    # Add recommendations based on weaknesses
    if "market_size" in weaknesses:
    if "market_size" in weaknesses:
    recommendations.append(
    recommendations.append(
    "Focus on a specific sub-segment of the market to maximize impact"
    "Focus on a specific sub-segment of the market to maximize impact"
    )
    )


    if "growth_rate" in weaknesses:
    if "growth_rate" in weaknesses:
    recommendations.append("Consider a long-term strategy for steady growth")
    recommendations.append("Consider a long-term strategy for steady growth")


    if "competition" in weaknesses:
    if "competition" in weaknesses:
    recommendations.append(
    recommendations.append(
    "Develop clear differentiation from existing competitors"
    "Develop clear differentiation from existing competitors"
    )
    )


    if "problem_severity" in weaknesses:
    if "problem_severity" in weaknesses:
    recommendations.append(
    recommendations.append(
    "Focus marketing on establishing the importance of the problem"
    "Focus marketing on establishing the importance of the problem"
    )
    )


    if "solution_feasibility" in weaknesses:
    if "solution_feasibility" in weaknesses:
    recommendations.append(
    recommendations.append(
    "Allocate additional resources to technical development"
    "Allocate additional resources to technical development"
    )
    )


    if "monetization_potential" in weaknesses:
    if "monetization_potential" in weaknesses:
    recommendations.append("Explore freemium or volume-based pricing models")
    recommendations.append("Explore freemium or volume-based pricing models")


    return assessment, recommendations
    return assessment, recommendations


    def _generate_next_steps(self, top_opportunity: Dict[str, Any]) -> List[str]:
    def _generate_next_steps(self, top_opportunity: Dict[str, Any]) -> List[str]:
    """
    """
    Generate next steps for the top recommendation.
    Generate next steps for the top recommendation.


    Args:
    Args:
    top_opportunity: Dictionary of the top opportunity
    top_opportunity: Dictionary of the top opportunity


    Returns:
    Returns:
    List of next steps
    List of next steps
    """
    """
    next_steps = [
    next_steps = [
    f"Conduct detailed market research for {top_opportunity.get('niche', 'the niche')}",
    f"Conduct detailed market research for {top_opportunity.get('niche', 'the niche')}",
    "Develop a prototype solution",
    "Develop a prototype solution",
    "Test with potential users",
    "Test with potential users",
    "Refine business model",
    "Refine business model",
    "Create implementation timeline",
    "Create implementation timeline",
    ]
    ]


    return next_steps
    return next_steps


    def _calculate_score_distribution(
    def _calculate_score_distribution(
    self, opportunities: List[Dict[str, Any]]
    self, opportunities: List[Dict[str, Any]]
    ) -> ScoreDistributionSchema:
    ) -> ScoreDistributionSchema:
    """
    """
    Calculate the distribution of scores across opportunities.
    Calculate the distribution of scores across opportunities.


    Args:
    Args:
    opportunities: List of opportunity dictionaries
    opportunities: List of opportunity dictionaries


    Returns:
    Returns:
    ScoreDistributionSchema with count of opportunities in each score range
    ScoreDistributionSchema with count of opportunities in each score range
    """
    """
    excellent = 0
    excellent = 0
    very_good = 0
    very_good = 0
    good = 0
    good = 0
    fair = 0
    fair = 0
    limited = 0
    limited = 0


    for opp in opportunities:
    for opp in opportunities:
    score = opp.get("overall_score", 0.0)
    score = opp.get("overall_score", 0.0)
    if score >= 0.8:
    if score >= 0.8:
    excellent += 1
    excellent += 1
    elif score >= 0.6:
    elif score >= 0.6:
    very_good += 1
    very_good += 1
    elif score >= 0.4:
    elif score >= 0.4:
    good += 1
    good += 1
    elif score >= 0.2:
    elif score >= 0.2:
    fair += 1
    fair += 1
    else:
    else:
    limited += 1
    limited += 1


    return ScoreDistributionSchema(
    return ScoreDistributionSchema(
    excellent=excellent,
    excellent=excellent,
    very_good=very_good,
    very_good=very_good,
    good=good,
    good=good,
    fair=fair,
    fair=fair,
    limited=limited,
    limited=limited,
    )
    )


    def _generate_comparison_factors(
    def _generate_comparison_factors(
    self, opportunities: List[Dict[str, Any]]
    self, opportunities: List[Dict[str, Any]]
    ) -> Dict[str, str]:
    ) -> Dict[str, str]:
    """
    """
    Generate comparison factors based on the opportunities being compared.
    Generate comparison factors based on the opportunities being compared.


    Args:
    Args:
    opportunities: List of opportunity dictionaries
    opportunities: List of opportunity dictionaries


    Returns:
    Returns:
    Dictionary of comparison factor names and descriptions
    Dictionary of comparison factor names and descriptions
    """
    """
    comparison_factors = {
    comparison_factors = {
    "market_size": "Size of the potential market",
    "market_size": "Size of the potential market",
    "growth_rate": "Growth rate of the market",
    "growth_rate": "Growth rate of the market",
    "competition": "Level of competition in the market",
    "competition": "Level of competition in the market",
    "problem_severity": "Severity of the problems being solved",
    "problem_severity": "Severity of the problems being solved",
    "solution_feasibility": "Feasibility of implementing AI-powered solutions",
    "solution_feasibility": "Feasibility of implementing AI-powered solutions",
    "monetization_potential": "Potential for profitable monetization",
    "monetization_potential": "Potential for profitable monetization",
    }
    }


    return comparison_factors
    return comparison_factors


    def _generate_comparison_recommendations(
    def _generate_comparison_recommendations(
    self, opportunities: List[Dict[str, Any]], analysis: ComparativeAnalysisSchema
    self, opportunities: List[Dict[str, Any]], analysis: ComparativeAnalysisSchema
    ) -> List[str]:
    ) -> List[str]:
    """
    """
    Generate recommendations based on comparison of opportunities.
    Generate recommendations based on comparison of opportunities.


    Args:
    Args:
    opportunities: List of opportunity dictionaries
    opportunities: List of opportunity dictionaries
    analysis: ComparativeAnalysis object
    analysis: ComparativeAnalysis object


    Returns:
    Returns:
    List of recommendation strings
    List of recommendation strings
    """
    """
    recommendations = []
    recommendations = []


    # General recommendations based on distribution
    # General recommendations based on distribution
    if analysis.score_distribution.excellent > 0:
    if analysis.score_distribution.excellent > 0:
    recommendations.append(
    recommendations.append(
    f"Focus on the {analysis.score_distribution.excellent} excellent opportunities as high priority"
    f"Focus on the {analysis.score_distribution.excellent} excellent opportunities as high priority"
    )
    )


    if analysis.score_distribution.very_good > 0:
    if analysis.score_distribution.very_good > 0:
    recommendations.append(
    recommendations.append(
    f"Consider the {analysis.score_distribution.very_good} very good opportunities as medium priority"
    f"Consider the {analysis.score_distribution.very_good} very good opportunities as medium priority"
    )
    )


    # Add recommendations for top opportunities
    # Add recommendations for top opportunities
    if opportunities:
    if opportunities:
    top_opp = opportunities[0]
    top_opp = opportunities[0]
    recommendations.append(
    recommendations.append(
    f"Prioritize {top_opp.get('niche', 'the top niche')} as the primary opportunity"
    f"Prioritize {top_opp.get('niche', 'the top niche')} as the primary opportunity"
    )
    )


    # If there's a second best, mention it as well
    # If there's a second best, mention it as well
    if len(opportunities) > 1:
    if len(opportunities) > 1:
    second_opp = opportunities[1]
    second_opp = opportunities[1]
    recommendations.append(
    recommendations.append(
    f"Keep {second_opp.get('niche', 'the second niche')} as a backup opportunity"
    f"Keep {second_opp.get('niche', 'the second niche')} as a backup opportunity"
    )
    )


    # Add portfolio recommendation if there are multiple good opportunities
    # Add portfolio recommendation if there are multiple good opportunities
    if (
    if (
    analysis.score_distribution.excellent
    analysis.score_distribution.excellent
    + analysis.score_distribution.very_good
    + analysis.score_distribution.very_good
    > 1
    > 1
    ):
    ):
    recommendations.append(
    recommendations.append(
    "Consider a portfolio approach with multiple opportunities in parallel"
    "Consider a portfolio approach with multiple opportunities in parallel"
    )
    )


    # Add recommendation for low-scoring opportunities
    # Add recommendation for low-scoring opportunities
    if analysis.score_distribution.limited > 0:
    if analysis.score_distribution.limited > 0:
    recommendations.append(
    recommendations.append(
    f"Deprioritize or eliminate the {analysis.score_distribution.limited} limited opportunities"
    f"Deprioritize or eliminate the {analysis.score_distribution.limited} limited opportunities"
    )
    )


    return recommendations
    return recommendations