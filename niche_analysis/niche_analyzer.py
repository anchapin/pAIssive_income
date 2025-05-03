"""
Niche analyzer for the Niche Analysis module.

This module provides the NicheAnalyzer class that analyzes niches and identifies opportunities.
"""

import time


import asyncio
import hashlib
import logging
import os
import sys
from typing import Any, Dict, List, Optional

sys.path.insert
from ai_models.async_utils import run_in_thread


from common_utils.caching import default_cache
from interfaces.agent_interfaces import IAgentTeam
from interfaces.niche_interfaces import INicheAnalyzer
from niche_analysis.errors import NicheAnalysisError



(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Import async utilities
# Import the centralized caching service
# Set up logging
logger = logging.getLogger(__name__)


class NicheAnalyzer(INicheAnalyzer):
    """
    Niche analyzer class.

This class analyzes niches and identifies opportunities.
    """

def __init__(self, agent_team: Optional[IAgentTeam] = None):
        """
        Initialize the niche analyzer.

Args:
            agent_team: Optional agent team instance
        """
        self.agent_team = agent_team

# Cache TTL in seconds (24 hours by default)
        self.cache_ttl = 86400

# Lock for concurrent access to shared resources
        self._lock = asyncio.Lock()

logger.debug("Created niche analyzer")

def analyze_niche(
        self, niche_name: str, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze a niche.

Args:
            niche_name: Name of the niche to analyze
            force_refresh: If True, bypasses cache and forces a fresh analysis

Returns:
            Niche analysis dictionary

Raises:
            NicheAnalysisError: If agent team or researcher is not available
        """
        logger.info(f"Analyzing niche: {niche_name}")

# Generate cache key
        cache_key = f"niche_analysis:{niche_name}"

# Try to get from cache first if not forcing refresh
        if not force_refresh:
            cached_result = default_cache.get(cache_key, namespace="niche_scores")
            if cached_result is not None:
                logger.info(f"Using cached niche analysis for niche: {niche_name}")
                            return cached_result

# Check for agent team and researcher
        if not self.agent_team:
            logger.error("Agent team not available")
            raise NicheAnalysisError("Agent team not available")

research_agent = self.agent_team.get_agent("researcher")
        if not research_agent:
            logger.error("Research agent not available")
            raise NicheAnalysisError("Research agent not available")

try:
            # Analyze problems in the niche
            problems = research_agent.analyze_problems(niche_name)

# Analyze competition
            competition = self.analyze_competition(niche_name, force_refresh)

# Get opportunities
            opportunities = self.get_niche_opportunities(niche_name, force_refresh)

# Create the niche analysis
            analysis = {
                "niche_name": niche_name,
                "problems": problems,
                "competition": competition,
                "opportunities": opportunities,
                "summary": f"Analysis of {niche_name} niche",
            }

logger.info(f"Completed analysis of niche: {niche_name}")

# Cache the result
            default_cache.set(
                cache_key, analysis, ttl=self.cache_ttl, namespace="niche_scores"
            )

            return analysis

except Exception as e:
            logger.error(f"Error analyzing niche: {e}")
            raise NicheAnalysisError("Error analyzing niche", original_exception=e)

def identify_niches(
        self, market_segments: List[str], force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Identify niches within market segments.

Args:
            market_segments: List of market segments to analyze
            force_refresh: If True, bypasses cache and forces a fresh identification

Returns:
            List of niche dictionaries

Raises:
            NicheAnalysisError: If agent team or researcher is not available
        """
        logger.info(f"Identifying niches in {len(market_segments)} market segments")

# Generate a cache key based on the market segments
        segments_str = ",".join(sorted(market_segments))
        cache_key = f"identify_niches:{hashlib.md5(segments_str.encode()).hexdigest()}"

# Try to get from cache first if not forcing refresh
        if not force_refresh:
            cached_result = default_cache.get(cache_key, namespace="niche_scores")
            if cached_result is not None:
                logger.info(
                    f"Using cached niche identification for segments: {segments_str[:50]}..."
                )
                            return cached_result

# Check for agent team and researcher
        if not self.agent_team:
            logger.error("Agent team not available")
            raise NicheAnalysisError("Agent team not available")

research_agent = self.agent_team.get_agent("researcher")
        if not research_agent:
            logger.error("Research agent not available")
            raise NicheAnalysisError("Research agent not available")

try:
            # Identify niches
            niches = research_agent.identify_niches(market_segments)

logger.info(f"Identified {len(niches)} niches")

# Cache the result
            default_cache.set(
                cache_key, niches, ttl=self.cache_ttl, namespace="niche_scores"
            )

            return niches

except Exception as e:
            logger.error(f"Error identifying niches: {e}")
            raise NicheAnalysisError("Error identifying niches", original_exception=e)

async def analyze_niche_async(
        self, niche_name: str, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze a niche asynchronously.

This is the asynchronous version of analyze_niche() that doesn't block the
        main event loop during potentially time-consuming operations.

Args:
            niche_name: Name of the niche to analyze
            force_refresh: If True, bypasses cache and forces a fresh analysis

Returns:
            Niche analysis dictionary
        """
        logger.info(f"Analyzing niche asynchronously: {niche_name}")

# Generate cache key
        cache_key = f"niche_analysis:{niche_name}"

# Try to get from cache first if not forcing refresh
        if not force_refresh:
            cached_result = await run_in_thread(
                default_cache.get, cache_key, namespace="niche_scores"
            )
            if cached_result is not None:
                logger.info(f"Using cached analysis for niche: {niche_name}")
                            return cached_result

try:
            # Get the research agent from the agent team
            if not self.agent_team:
                raise NicheAnalysisError("Agent team not available")

research_agent = self.agent_team.get_agent("researcher")
            if not research_agent:
                raise NicheAnalysisError("Research agent not available")

# We need to execute these tasks in parallel for performance
            # Create tasks for each analysis step

# For the research agent's analyze_problems, we need to run it in a thread
            # since it might not have an async version
            problems_task = run_in_thread(research_agent.analyze_problems, niche_name)

# For our own methods, we can use the async versions
            competition_task = self.analyze_competition_async(niche_name, force_refresh)
            opportunities_task = self.get_niche_opportunities_async(
                niche_name, force_refresh
            )

# Run all tasks concurrently and gather results
            problems, competition, opportunities = await asyncio.gather(
                problems_task, competition_task, opportunities_task
            )

# Create the niche analysis
            analysis = {
                "niche_name": niche_name,
                "problems": problems,
                "competition": competition,
                "opportunities": opportunities,
                "summary": f"Analysis of {niche_name} niche",
            }

logger.info(f"Completed async analysis of niche: {niche_name}")

# Cache the result
            await run_in_thread(
                default_cache.set,
                cache_key,
                analysis,
                ttl=self.cache_ttl,
                namespace="niche_scores",
            )

            return analysis

except Exception as e:
            logger.error(f"Error analyzing niche asynchronously {niche_name}: {e}")
            raise NicheAnalysisError(
                f"Error analyzing niche {niche_name}", original_exception=e
            )

def identify_niches(
        self, market_segments: List[str], force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Identify niches within market segments.

Args:
            market_segments: List of market segments to analyze
            force_refresh: If True, bypasses cache and forces a fresh identification

Returns:
            List of niche dictionaries

Raises:
            NicheAnalysisError: If agent team or researcher is not available
        """
        logger.info(f"Identifying niches in {len(market_segments)} market segments")

# Generate a cache key based on the market segments
        segments_str = ",".join(sorted(market_segments))
        cache_key = f"identify_niches:{hashlib.md5(segments_str.encode()).hexdigest()}"

# Try to get from cache first if not forcing refresh
        if not force_refresh:
            cached_result = default_cache.get(cache_key, namespace="niche_scores")
            if cached_result is not None:
                logger.info(
                    f"Using cached niche identification for segments: {segments_str[:50]}..."
                )
                            return cached_result

# Check for agent team and researcher
        if not self.agent_team:
            logger.error("Agent team not available")
            raise NicheAnalysisError("Agent team not available")

research_agent = self.agent_team.get_agent("researcher")
        if not research_agent:
            logger.error("Research agent not available")
            raise NicheAnalysisError("Research agent not available")

try:
            # Identify niches
            niches = research_agent.identify_niches(market_segments)

logger.info(f"Identified {len(niches)} niches")

# Cache the result
            default_cache.set(
                cache_key, niches, ttl=self.cache_ttl, namespace="niche_scores"
            )

            return niches

except NicheAnalysisError:
            raise  # Re-raise NicheAnalysisError exceptions
        except Exception as e:
            logger.error(f"Error identifying niches: {e}")
            raise NicheAnalysisError("Error identifying niches", original_exception=e)

async def identify_niches_async(
        self, market_segments: List[str], force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Identify niches within market segments asynchronously.

This is the asynchronous version of identify_niches() that doesn't block the
        main event loop during potentially time-consuming operations.

Args:
            market_segments: List of market segments to analyze
            force_refresh: If True, bypasses cache and forces a fresh identification

Returns:
            List of niche dictionaries
        """
        logger.info(
            f"Identifying niches asynchronously in {len(market_segments)} market segments"
        )

# Generate a cache key based on the market segments
        segments_str = ",".join(sorted(market_segments))
        cache_key = f"identify_niches:{hashlib.md5(segments_str.encode()).hexdigest()}"

# Try to get from cache first if not forcing refresh
        if not force_refresh:
            cached_result = await run_in_thread(
                default_cache.get, cache_key, namespace="niche_scores"
            )
            if cached_result is not None:
                logger.info(
                    f"Using cached niche identification for segments: {segments_str[:50]}..."
                )
                            return cached_result

try:
            # Get the research agent from the agent team
            if not self.agent_team:
                raise NicheAnalysisError("Agent team not available")

research_agent = self.agent_team.get_agent("researcher")
            if not research_agent:
                raise NicheAnalysisError("Research agent not available")

# Identify niches - run this in a thread since it might not have an async version
            niches = await run_in_thread(
                research_agent.identify_niches, market_segments
            )

logger.info(f"Identified {len(niches)} niches asynchronously")

# Cache the result
            await run_in_thread(
                default_cache.set,
                cache_key,
                niches,
                ttl=self.cache_ttl,
                namespace="niche_scores",
            )

            return niches

except Exception as e:
            logger.error(f"Error identifying niches asynchronously: {e}")
            raise NicheAnalysisError("Error identifying niches", original_exception=e)

def analyze_competition(
        self, niche_name: str, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze competition in a niche.

Args:
            niche_name: Name of the niche to analyze
            force_refresh: If True, bypasses cache and forces a fresh analysis

Returns:
            Competition analysis dictionary
        """
        logger.info(f"Analyzing competition in niche: {niche_name}")

# Generate cache key
        cache_key = f"competition_analysis:{niche_name}"

# Try to get from cache first if not forcing refresh
        if not force_refresh:
            cached_result = default_cache.get(cache_key, namespace="niche_scores")
            if cached_result is not None:
                logger.info(
                    f"Using cached competition analysis for niche: {niche_name}"
                )
                            return cached_result

# This is a placeholder implementation
        # In a real implementation, this would analyze competitors in the niche
        competition = {
            "niche_name": niche_name,
            "competitors": [],
            "market_leaders": [],
            "market_gaps": [],
            "summary": f"Competition analysis for {niche_name} niche",
        }

logger.info(f"Completed competition analysis for niche: {niche_name}")

# Cache the result
        default_cache.set(
            cache_key, competition, ttl=self.cache_ttl, namespace="niche_scores"
        )

            return competition

async def analyze_competition_async(
        self, niche_name: str, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze competition in a niche asynchronously.

This is the asynchronous version of analyze_competition() that doesn't block the
        main event loop during potentially time-consuming operations.

Args:
            niche_name: Name of the niche to analyze
            force_refresh: If True, bypasses cache and forces a fresh analysis

Returns:
            Competition analysis dictionary
        """
        logger.info(f"Analyzing competition in niche asynchronously: {niche_name}")

# Generate cache key
        cache_key = f"competition_analysis:{niche_name}"

# Try to get from cache first if not forcing refresh
        if not force_refresh:
            cached_result = await run_in_thread(
                default_cache.get, cache_key, namespace="niche_scores"
            )
            if cached_result is not None:
                logger.info(
                    f"Using cached competition analysis for niche: {niche_name}"
                )
                            return cached_result

# Simulate some async processing that would be done by AI models
        await asyncio.sleep(0.05)

# This is a placeholder implementation
        # In a real implementation, this would analyze competitors in the niche
        competition = {
            "niche_name": niche_name,
            "competitors": [],
            "market_leaders": [],
            "market_gaps": [],
            "summary": f"Competition analysis for {niche_name} niche",
        }

logger.info(
            f"Completed competition analysis for niche asynchronously: {niche_name}"
        )

# Cache the result
        await run_in_thread(
            default_cache.set,
            cache_key,
            competition,
            ttl=self.cache_ttl,
            namespace="niche_scores",
        )

            return competition

def get_niche_opportunities(
        self, niche_name: str, force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get opportunities in a niche.

Args:
            niche_name: Name of the niche to analyze
            force_refresh: If True, bypasses cache and forces a fresh retrieval

Returns:
            List of opportunity dictionaries
        """
        logger.info(f"Getting opportunities in niche: {niche_name}")

# Generate cache key
        cache_key = f"niche_opportunities:{niche_name}"

# Try to get from cache first if not forcing refresh
        if not force_refresh:
            cached_result = default_cache.get(cache_key, namespace="niche_scores")
            if cached_result is not None:
                logger.info(f"Using cached opportunities for niche: {niche_name}")
                            return cached_result

# This is a placeholder implementation
        # In a real implementation, this would identify opportunities in the niche
        opportunities = [
            {
                "name": f"Opportunity 1 in {niche_name}",
                "description": "Description of opportunity 1",
                "score": 0.8,
                "difficulty": "medium",
            },
            {
                "name": f"Opportunity 2 in {niche_name}",
                "description": "Description of opportunity 2",
                "score": 0.7,
                "difficulty": "low",
            },
        ]

logger.info(f"Found {len(opportunities)} opportunities in niche: {niche_name}")

# Cache the result
        default_cache.set(
            cache_key, opportunities, ttl=self.cache_ttl, namespace="niche_scores"
        )

            return opportunities

async def get_niche_opportunities_async(
        self, niche_name: str, force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get opportunities in a niche asynchronously.

This is the asynchronous version of get_niche_opportunities() that doesn't block the
        main event loop during potentially time-consuming operations.

Args:
            niche_name: Name of the niche to analyze
            force_refresh: If True, bypasses cache and forces a fresh retrieval

Returns:
            List of opportunity dictionaries
        """
        logger.info(f"Getting opportunities in niche asynchronously: {niche_name}")

# Generate cache key
        cache_key = f"niche_opportunities:{niche_name}"

# Try to get from cache first if not forcing refresh
        if not force_refresh:
            cached_result = await run_in_thread(
                default_cache.get, cache_key, namespace="niche_scores"
            )
            if cached_result is not None:
                logger.info(f"Using cached opportunities for niche: {niche_name}")
                            return cached_result

# Simulate some async processing that would be done by AI models
        await asyncio.sleep(0.05)

# This is a placeholder implementation
        # In a real implementation, this would identify opportunities in the niche
        opportunities = [
            {
                "name": f"Opportunity 1 in {niche_name}",
                "description": "Description of opportunity 1",
                "score": 0.8,
                "difficulty": "medium",
            },
            {
                "name": f"Opportunity 2 in {niche_name}",
                "description": "Description of opportunity 2",
                "score": 0.7,
                "difficulty": "low",
            },
        ]

logger.info(
            f"Found {len(opportunities)} opportunities in niche asynchronously: {niche_name}"
        )

# Cache the result
        await run_in_thread(
            default_cache.set,
            cache_key,
            opportunities,
            ttl=self.cache_ttl,
            namespace="niche_scores",
        )

            return opportunities

def set_cache_ttl(self, ttl_seconds: int) -> None:
        """
        Set the cache TTL (time to live) for niche analysis.

Args:
            ttl_seconds: Cache TTL in seconds
        """
        self.cache_ttl = ttl_seconds
        logger.info(f"Set niche analyzer cache TTL to {ttl_seconds} seconds")

async def set_cache_ttl_async(self, ttl_seconds: int) -> None:
        """
        Set the cache TTL (time to live) for niche analysis asynchronously.

Args:
            ttl_seconds: Cache TTL in seconds
        """
        self.cache_ttl = ttl_seconds
        logger.info(f"Set niche analyzer cache TTL to {ttl_seconds} seconds")

def clear_cache(self) -> bool:
        """
        Clear the niche analyzer cache.

Returns:
            True if successful, False otherwise
        """
        result = default_cache.clear(namespace="niche_scores")
        logger.info(f"Cleared niche analyzer cache: {result}")
                    return result

async def clear_cache_async(self) -> bool:
        """
        Clear the niche analyzer cache asynchronously.

Returns:
            True if successful, False otherwise
        """
        result = await run_in_thread(default_cache.clear, namespace="niche_scores")
        logger.info(f"Cleared niche analyzer cache asynchronously: {result}")
                    return result

async def analyze_multiple_niches_async(
        self, niche_names: List[str], force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple niches concurrently.

Args:
            niche_names: List of niche names to analyze
            force_refresh: If True, bypasses cache and forces fresh analyses

Returns:
            List of niche analyses
        """
        logger.info(f"Analyzing {len(niche_names)} niches concurrently")

# Create tasks for analyzing each niche
        tasks = [
            self.analyze_niche_async(niche, force_refresh) for niche in niche_names
        ]

# Run all tasks concurrently and gather results
        results = await asyncio.gather(*tasks)

logger.info(f"Completed analysis of {len(niche_names)} niches concurrently")

            return results

async def batch_process_market_segments_async(
        self, market_segments: List[str], force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Process multiple market segments to identify and analyze niches in a batch.

Args:
            market_segments: List of market segments to process
            force_refresh: If True, bypasses cache and forces fresh analyses

Returns:
            Dictionary containing identified niches and their analyses
        """
        logger.info(f"Batch processing {len(market_segments)} market segments")

# Step 1: Identify niches in all market segments
        niches = await self.identify_niches_async(market_segments, force_refresh)

# Step 2: Extract just the niche names
        niche_names = [niche["name"] for niche in niches]

# Step 3: Analyze all identified niches in parallel
        analyses = await self.analyze_multiple_niches_async(niche_names, force_refresh)

# Step 4: Map niche analyses to their corresponding niches
        result = {
            "market_segments": market_segments,
            "niches": niches,
            "analyses": analyses,
            "summary": f"Batch processed {len(market_segments)} market segments and identified {len(niches)} niches",
        }

logger.info(
            f"Completed batch processing of {len(market_segments)} market segments"
        )

            return result