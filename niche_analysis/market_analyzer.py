"""Implementation of :class:`MarketAnalyzer` – performs basic market intelligence.

The algorithms are intentionally *heuristic* and knowledge-base driven to
eliminate external dependencies while still providing deterministic,
actionable outputs that are useful for unit testing and MVP workflows.
"""

from __future__ import annotations

import logging
from typing import Any

from .errors import InvalidInputError
from .schemas import (
    MarketSegmentAnalysis,
    CompetitionAnalysis,
    TrendAnalysis,
    CompetitorProfile,
    TrendProfile,
    PredictionProfile,
)

logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """Analyze market segments, competition and trends."""

    # ---------------------------------------------------------------------
    # Internal static knowledge-base – keeps the implementation *pure-py* and
    # fully deterministic so that tests don’t require network or databases.
    # ---------------------------------------------------------------------

    _SEGMENT_DB: dict[str, dict[str, Any]] = {
        "e-commerce": {
            "description": "Online buying and selling of goods and services",
            "market_size": "large",
            "growth_rate": "high",
            "competition": "high",
            "barriers_to_entry": "medium",
            "technological_adoption": "high",
            "potential_niches": [
                "inventory management for small e-commerce",
                "product description generation",
                "pricing optimization",
                "customer service automation",
                "return management",
            ],
            "target_users": [
                "small e-commerce business owners",
                "e-commerce marketers",
                "e-commerce operations managers",
            ],
        },
        "content creation": {
            "description": "Creation and distribution of digital content across channels",
            "market_size": "large",
            "growth_rate": "medium",
            "competition": "medium",
            "barriers_to_entry": "low",
            "technological_adoption": "high",
            "potential_niches": [
                "youtube script generation",
                "podcast show-note summarisation",
                "blog SEO optimisation",
            ],
            "target_users": [
                "content creators",
                "small media agencies",
                "freelance writers",
            ],
        },
        # Add more pre-defined segments as needed
    }

    # _SATURATION_MAP removed, use saturation_level directly

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_segment(self, segment: str) -> MarketSegmentAnalysis:
        """Return a high-level analysis of *segment*.

        Unrecognised segments yield a graceful *unknown* default object so
        downstream algorithms can still operate.
        """

        if not segment or not isinstance(segment, str):
            raise InvalidInputError("segment must be a non-empty string")

        data = self._SEGMENT_DB.get(segment.lower())

        if not data:
            logger.debug("Unknown segment '%s' – generating default analysis", segment)
            data = {
                "description": "Unknown market segment",
                "market_size": "unknown",
                "growth_rate": "unknown",
                "competition": "unknown",
                "barriers_to_entry": "unknown",
                "technological_adoption": "unknown",
                "potential_niches": [],
                "target_users": [],
            }

        return MarketSegmentAnalysis(name=segment.title(), **data)

    # ..................................................................

    def analyze_competition(self, niche: str) -> CompetitionAnalysis:
        """Return a synthetic competition analysis for *niche*."""

        if not niche or not isinstance(niche, str):
            raise InvalidInputError("niche must be a non-empty string")

        # Deterministic competitor count based on hash to keep repeatability
        competitor_count = (abs(hash(niche)) % 5) + 3  # 3-7 competitors

        top_competitors: list[CompetitorProfile] = []
        for i in range(min(3, competitor_count)):
            name = f"{niche.title()} Solutions #{i+1}"
            profile = CompetitorProfile(
                name=name,
                description=f"Hypothetical competitor {i+1} in the {niche} space",
                estimated_market_share=round(1 / competitor_count, 2),
                key_strengths=["feature-rich", "brand recognition" if i == 0 else "niche focus"],
                key_weaknesses=["high pricing" if i == 0 else "limited features"],
                pricing_info="SaaS subscription",
            )
            top_competitors.append(profile)

        saturation_level = (
            "high" if competitor_count > 5 else "medium" if competitor_count > 3 else "low"
        )

        analysis = CompetitionAnalysis(
            niche=niche,
            competitor_count=competitor_count,
            top_competitors=top_competitors,
            market_saturation=saturation_level,
            entry_barriers="medium" if competitor_count > 4 else "low",
            differentiation_opportunities=[
                "specialised workflow integration",
                "AI-powered personalisation",
                "freemium pricing",
            ],
        )

        return analysis

    # ..................................................................

    def analyze_trends(self, segment: str) -> TrendAnalysis:
        """Return current and future trend analysis for *segment*."""

        if not segment or not isinstance(segment, str):
            raise InvalidInputError("segment must be a non-empty string")

        current_trends = [
            TrendProfile(
                name="AI automation",
                description="Increasing adoption of AI-driven workflow automation",
                impact_level="high",
                maturity_level="growing",
            ),
            TrendProfile(
                name="Subscription fatigue",
                description="Users are more selective about recurring SaaS spend",
                impact_level="medium",
                maturity_level="mature",
            ),
        ]

        future_predictions = [
            PredictionProfile(
                name="Low-code customisation",
                description="Rise of low-code tooling for niche apps",
                likelihood="high",
                timeframe="medium-term",
            ),
            PredictionProfile(
                name="Hyper-personalised UX",
                description="Deep personalisation driven by LLM user modelling",
                likelihood="medium",
                timeframe="long-term",
            ),
        ]

        technological_shifts = [
            "Widespread LLM APIs",
            "Edge compute for latency-sensitive tasks",
            "Privacy-preserving analytics",
        ]

        return TrendAnalysis(
            segment=segment,
            current_trends=current_trends,
            future_predictions=future_predictions,
            technological_shifts=technological_shifts,
        )
