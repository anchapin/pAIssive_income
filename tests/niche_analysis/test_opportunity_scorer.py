import pytest
from niche_analysis import OpportunityScorer
from niche_analysis.schemas import OpportunityScore, Problem

def sample_problem(severity="high"):
    return Problem(
        name="Fake Problem",
        description="desc",
        consequences=["conseq"],
        severity=severity,
        current_solutions={},
        solution_gaps={},
        timestamp="2023-01-01T00:00:00.000000"
    )

def test_score_opportunity_range():
    scorer = OpportunityScorer()
    market_data = {
        "market_size": "large",
        "growth_rate": "high",
        "competition": "medium",
    }
    problems = [sample_problem("high"), sample_problem("medium")]
    result = scorer.score_opportunity("inventory management for small e-commerce", market_data, problems)
    assert isinstance(result, OpportunityScore)
    assert 0.0 <= result.overall_score <= 1.0
    assert "market_size" in result.factor_scores
    assert result.recommendations

def test_compare_opportunities_ranking():
    scorer = OpportunityScorer()
    market_data = {
        "market_size": "large",
        "growth_rate": "medium",
        "competition": "low",
    }
    probs = [sample_problem("high")]
    opp1 = scorer.score_opportunity("niche1", market_data, probs)
    market_data2 = {"market_size": "small", "growth_rate": "low", "competition": "high"}
    opp2 = scorer.score_opportunity("niche2", market_data2, [sample_problem("low")])
    comparison = scorer.compare_opportunities([opp1, opp2])
    assert comparison.ranked_opportunities[0].overall_score >= comparison.ranked_opportunities[1].overall_score
