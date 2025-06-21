"""Scores and compares niche opportunities."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Any

from .schemas import OpportunityScore, OpportunityComparison, Problem
from .errors import InvalidInputError, ScoringError

# -----------------------------------------------------------------------------
# Helper mappings – categorical to numeric scores
# -----------------------------------------------------------------------------


_CATEGORY_MAP = {
    "market_size": {"large": 0.9, "medium": 0.6, "small": 0.3, "unknown": 0.5},
    "growth_rate": {"high": 0.9, "medium": 0.6, "low": 0.3, "unknown": 0.5},
    "competition": {"low": 0.9, "medium": 0.5, "high": 0.2, "unknown": 0.5},
}

# Default weights – must sum to 1.0
_WEIGHTS = {
    "market_size": 0.2,
    "growth_rate": 0.15,
    "competition": 0.15,
    "problem_severity": 0.2,
    "solution_feasibility": 0.15,
    "monetization_potential": 0.15,
}


class OpportunityScorer:
    """Evaluate and compare niche opportunities."""

    # .....................................................................
    # Public API
    # .....................................................................

    def score_opportunity(
        self,
        niche: str,
        market_data: Dict[str, Any],
        problems: List[Problem],
    ) -> OpportunityScore:
        """Return a scoring object for a single *niche*."""

        if not niche or not isinstance(niche, str):
            raise InvalidInputError("niche must be a non-empty string")

        # 1. Derive factor scores ------------------------------------------------

        factor_scores: Dict[str, float] = {}

        # Qualitative mappings
        for cat in ("market_size", "growth_rate", "competition"):
            category_value = str(market_data.get(cat, "unknown")).lower()
            factor_scores[cat] = _CATEGORY_MAP[cat].get(category_value, 0.5)

        # Problem severity – average severity mapped to numeric
        severity_map = {"high": 1.0, "medium": 0.6, "low": 0.3}
        if problems:
            factor_scores["problem_severity"] = sum(
                severity_map[p.severity] for p in problems
            ) / len(problems)
        else:
            factor_scores["problem_severity"] = 0.3  # conservative default

        # Solution feasibility – simplistic heuristic based on keywords
        text_keywords = ("writing", "content", "script", "text")
        data_keywords = ("analytics", "report", "data")
        base_feasibility = 0.7
        text_bonus = 0.2 if any(k in niche.lower() for k in text_keywords) else 0.0
        data_bonus = 0.1 if any(k in niche.lower() for k in data_keywords) else 0.0
        factor_scores["solution_feasibility"] = max(
            0.0, min(1.0, base_feasibility + text_bonus + data_bonus)
        )

        # Monetization potential – uses market & severity heuristics
        market_bonus = (
            0.2
            if factor_scores["market_size"] >= 0.8
            else 0.1
            if factor_scores["market_size"] >= 0.6
            else -0.1
        )
        growth_bonus = (
            0.2
            if factor_scores["growth_rate"] >= 0.8
            else 0.1
            if factor_scores["growth_rate"] >= 0.6
            else -0.1
        )
        severity_bonus = 0.1 if factor_scores["problem_severity"] > 0.7 else 0.0
        business_bonus = 0.1 if any(k in niche.lower() for k in ("business", "enterprise")) else 0.0
        factor_scores["monetization_potential"] = max(
            0.0,
            min(1.0, 0.5 + market_bonus + growth_bonus + severity_bonus + business_bonus),
        )

        # 2. Weighted sum --------------------------------------------------------
        try:
            overall_score = sum(factor_scores[k] * _WEIGHTS[k] for k in _WEIGHTS)
        except KeyError as exc:
            raise ScoringError(f"Missing factor for scoring: {exc}") from exc

        # 3. Analysis & recommendations -----------------------------------------

        analysis = {
            "strengths": [k for k, v in factor_scores.items() if v >= 0.75],
            "weaknesses": [k for k, v in factor_scores.items() if v <= 0.4],
            "opportunities": ["address high-severity problems", "leverage growth trends"],
            "threats": ["competitive reaction", "market saturation"],
        }

        recommendations = []
        if overall_score >= 0.8:
            recommendations.append("Pursue immediately with significant resources")
        elif overall_score >= 0.6:
            recommendations.append("Worth pursuing; allocate appropriate resources")
        elif overall_score >= 0.4:
            recommendations.append("Investigate further before major investment")
        else:
            recommendations.append("Low priority – consider alternatives")

        return OpportunityScore(
            niche=niche,
            overall_score=round(overall_score, 2),
            factor_scores={k: round(v, 2) for k, v in factor_scores.items()},
            analysis=analysis,
            recommendations=recommendations,
            timestamp=datetime.utcnow(),
        )

    # .....................................................................

    def compare_opportunities(self, opportunities: List[OpportunityScore]) -> OpportunityComparison:
        """Rank and compare multiple OpportunityScore objects."""

        if not opportunities:
            raise InvalidInputError("opportunities list cannot be empty")

        ranked = sorted(opportunities, key=lambda o: o.overall_score, reverse=True)
        scores = [o.overall_score for o in ranked]

        comparison_factors = {
            "highest": max(scores),
            "lowest": min(scores),
            "average": round(sum(scores) / len(scores), 2),
        }

        return OpportunityComparison(
            ranked_opportunities=ranked,
            top_recommendation=ranked[0],
            comparison_factors=comparison_factors,
            recommendations=[
                "Focus on top-scoring opportunity first",
                "Allocate exploratory budget to 2nd and 3rd ranked niches",
            ],
        )