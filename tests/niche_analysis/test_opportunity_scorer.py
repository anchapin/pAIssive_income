"""
Tests for the OpportunityScorer class.
"""


from niche_analysis.opportunity_scorer import OpportunityScorer


def test_opportunity_scorer_init():
    """Test OpportunityScorer initialization."""
    scorer = OpportunityScorer()

    # Check that the scorer has the expected attributes
    assert scorer.name == "Opportunity Scorer"
    assert scorer.description == "Scores niche opportunities based on various factors"
    assert isinstance(scorer.weights, dict)
    assert "market_size" in scorer.weights
    assert "growth_rate" in scorer.weights
    assert "competition" in scorer.weights
    assert "problem_severity" in scorer.weights
    assert "solution_feasibility" in scorer.weights
    assert "monetization_potential" in scorer.weights
    assert sum(scorer.weights.values()) == 1.0  # Weights should sum to 1


def test_score_opportunity():
    """Test score_opportunity method."""
    scorer = OpportunityScorer()

    # Create test data
    market_data = {
        "market_size": "large",
        "growth_rate": "high",
        "competition": "low",
    }

    problems = [
        {
            "id": "problem1",
            "name": "Problem 1",
            "description": "A test problem",
            "consequences": ["consequence 1", "consequence 2"],
            "severity": "high",
        }
    ]

    # Score the opportunity
    result = scorer.score_opportunity("inventory management", market_data, problems)

    # Check that the result has the expected keys
    assert "score" in result
    assert "factors" in result
    assert "recommendations" in result
    assert "timestamp" in result

    # Check that the score is a float between 0 and 1
    assert isinstance(result["score"], float)
    assert 0 <= result["score"] <= 1

    # Check that the factors have the expected keys
    assert "market_size" in result["factors"]
    assert "growth_rate" in result["factors"]
    assert "competition" in result["factors"]
    assert "problem_severity" in result["factors"]
    assert "solution_feasibility" in result["factors"]
    assert "monetization_potential" in result["factors"]

    # Check that the recommendations is a list of strings
    assert isinstance(result["recommendations"], list)
    assert all(isinstance(r, str) for r in result["recommendations"])


def test_score_market_size():
    """Test _score_market_size method."""
    scorer = OpportunityScorer()

    # Test different market sizes
    assert scorer._score_market_size("large") > scorer._score_market_size("medium")
    assert scorer._score_market_size("medium") > scorer._score_market_size("small")
    assert scorer._score_market_size("unknown") == 0.5  # Default for unknown


def test_score_growth_rate():
    """Test _score_growth_rate method."""
    scorer = OpportunityScorer()

    # Test different growth rates
    assert scorer._score_growth_rate("high") > scorer._score_growth_rate("medium")
    assert scorer._score_growth_rate("medium") > scorer._score_growth_rate("low")
    assert scorer._score_growth_rate("unknown") == 0.5  # Default for unknown


def test_score_competition():
    """Test _score_competition method."""
    scorer = OpportunityScorer()

    # Test different competition levels
    assert scorer._score_competition("low") > scorer._score_competition("medium")
    assert scorer._score_competition("medium") > scorer._score_competition("high")
    assert scorer._score_competition("unknown") == 0.5  # Default for unknown


def test_score_problem_severity():
    """Test _score_problem_severity method."""
    scorer = OpportunityScorer()

    # Create test problems with different severities
    high_severity_problems = [
        {"severity": "high"},
        {"severity": "high"},
    ]

    medium_severity_problems = [
        {"severity": "medium"},
        {"severity": "medium"},
    ]

    low_severity_problems = [
        {"severity": "low"},
        {"severity": "low"},
    ]

    mixed_severity_problems = [
        {"severity": "high"},
        {"severity": "medium"},
        {"severity": "low"},
    ]

    # Test different problem severities
    assert scorer._score_problem_severity(
        high_severity_problems
    ) > scorer._score_problem_severity(medium_severity_problems)
    assert scorer._score_problem_severity(
        medium_severity_problems
    ) > scorer._score_problem_severity(low_severity_problems)

    # Test mixed severity
    mixed_score = scorer._score_problem_severity(mixed_severity_problems)
    assert (
        scorer._score_problem_severity(low_severity_problems)
        < mixed_score
        < scorer._score_problem_severity(high_severity_problems)
    )

    # Test empty problems list
    assert scorer._score_problem_severity([]) == 0.0


def test_score_solution_feasibility():
    """Test _score_solution_feasibility method."""
    scorer = OpportunityScorer()

    # Test different niches
    assert 0 <= scorer._score_solution_feasibility("inventory management", []) <= 1
    assert (
        0
        <= scorer._score_solution_feasibility("product description generation", [])
        <= 1
    )
    assert 0 <= scorer._score_solution_feasibility("unknown niche", []) <= 1


def test_score_monetization_potential():
    """Test _score_monetization_potential method."""
    scorer = OpportunityScorer()

    # Create test data
    market_data = {
        "market_size": "large",
        "growth_rate": "high",
    }

    problems = [
        {"severity": "high"},
    ]

    # Test different niches
    assert (
        0
        <= scorer._score_monetization_potential(
            "inventory management", market_data, problems
        )
        <= 1
    )
    assert (
        0
        <= scorer._score_monetization_potential(
            "product description generation", market_data, problems
        )
        <= 1
    )
    assert (
        0
        <= scorer._score_monetization_potential("unknown niche", market_data, problems)
        <= 1
    )


def test_compare_opportunities():
    """Test compare_opportunities method."""
    scorer = OpportunityScorer()

    # Create test opportunities
    opportunities = [
        {
            "id": "opportunity1",
            "name": "Opportunity 1",
            "description": "A test opportunity",
            "opportunity_score": 0.8,
            "market_data": {
                "market_size": "large",
                "growth_rate": "high",
                "competition": "low",
            },
            "problems": [{"severity": "high"}],
        },
        {
            "id": "opportunity2",
            "name": "Opportunity 2",
            "description": "Another test opportunity",
            "opportunity_score": 0.6,
            "market_data": {
                "market_size": "medium",
                "growth_rate": "medium",
                "competition": "medium",
            },
            "problems": [{"severity": "medium"}],
        },
        {
            "id": "opportunity3",
            "name": "Opportunity 3",
            "description": "Yet another test opportunity",
            "opportunity_score": 0.4,
            "market_data": {
                "market_size": "small",
                "growth_rate": "low",
                "competition": "high",
            },
            "problems": [{"severity": "low"}],
        },
    ]

    # Compare the opportunities
    result = scorer.compare_opportunities(opportunities)

    # Check that the result has the expected keys
    assert "ranked_opportunities" in result
    assert "top_recommendation" in result
    assert "comparison_factors" in result
    assert "recommendations" in result
    assert "timestamp" in result

    # Check that the ranked opportunities are in the correct order
    assert len(result["ranked_opportunities"]) == 3
    assert result["ranked_opportunities"][0]["id"] == "opportunity1"
    assert result["ranked_opportunities"][1]["id"] == "opportunity2"
    assert result["ranked_opportunities"][2]["id"] == "opportunity3"

    # Check that the top recommendation is the highest-scoring opportunity
    assert result["top_recommendation"]["id"] == "opportunity1"

    # Check that the comparison factors include the expected keys
    assert "market_size" in result["comparison_factors"]
    assert "growth_rate" in result["comparison_factors"]
    assert "competition" in result["comparison_factors"]
    assert "problem_severity" in result["comparison_factors"]

    # Check that the recommendations is a list of strings
    assert isinstance(result["recommendations"], list)
    assert all(isinstance(r, str) for r in result["recommendations"])
