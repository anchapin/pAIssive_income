"""
Tests for the ProblemIdentifier class.
"""

from datetime import datetime
from unittest.mock import patch

from niche_analysis.problem_identifier import ProblemIdentifier


def test_problem_identifier_init():
    """Test ProblemIdentifier initialization."""
    identifier = ProblemIdentifier()

    # Check that the identifier has the expected attributes
    assert identifier.name == "Problem Identifier"
    assert (
        identifier.description
        == "Identifies user problems and pain points in specific niches"
    )


def test_identify_problems():
    """Test identify_problems method."""
    identifier = ProblemIdentifier()

    # Identify problems for a niche
    problems = identifier.identify_problems("e-commerce")

    # Check that the result is a list of problems
    assert isinstance(problems, list)
    assert len(problems) > 0

    # Check that each problem has the expected keys
    for problem in problems:
        assert "id" in problem
        assert "name" in problem
        assert "description" in problem
        assert "consequences" in problem
        assert "severity" in problem
        assert "current_solutions" in problem
        assert "solution_gaps" in problem
        assert "timestamp" in problem


def test_identify_problems_unknown_niche():
    """Test identify_problems method with an unknown niche."""
    identifier = ProblemIdentifier()

    # Identify problems for an unknown niche
    problems = identifier.identify_problems("unknown_niche")

    # Check that the result is an empty list
    assert isinstance(problems, list)
    assert len(problems) == 0


def test_analyze_problem_severity():
    """Test analyze_problem_severity method."""
    identifier = ProblemIdentifier()

    # Create a test problem
    problem = {
        "id": "problem1",
        "name": "Inventory Management",
        "description": "Difficulty managing inventory levels",
        "consequences": ["stockouts", "excess inventory", "lost sales"],
        "severity": "high",
    }

    # Analyze the problem severity
    result = identifier.analyze_problem_severity(problem)

    # Check that the result has the expected keys
    assert "id" in result
    assert "problem_id" in result
    assert "severity" in result
    assert "analysis" in result
    assert "potential_impact_of_solution" in result
    assert "user_willingness_to_pay" in result
    assert "timestamp" in result

    # Check specific values
    assert result["problem_id"] == "problem1"
    assert result["severity"] == "high"
    assert isinstance(result["analysis"], dict)
    assert result["potential_impact_of_solution"] == "high"
    assert result["user_willingness_to_pay"] == "high"


def test_analyze_problem_severity_medium():
    """Test analyze_problem_severity method with medium severity."""
    identifier = ProblemIdentifier()

    # Create a test problem with medium severity
    problem = {
        "id": "problem1",
        "name": "Product Description",
        "description": "Difficulty writing product descriptions",
        "consequences": ["poor SEO", "lower conversion rates"],
        "severity": "medium",
    }

    # Analyze the problem severity
    result = identifier.analyze_problem_severity(problem)

    # Check specific values
    assert result["severity"] == "medium"
    assert result["potential_impact_of_solution"] == "medium"
    assert result["user_willingness_to_pay"] == "medium"


def test_analyze_problem_severity_low():
    """Test analyze_problem_severity method with low severity."""
    identifier = ProblemIdentifier()

    # Create a test problem with low severity
    problem = {
        "id": "problem1",
        "name": "Social Media Posting",
        "description": "Difficulty scheduling social media posts",
        "consequences": ["inconsistent posting", "lower engagement"],
        "severity": "low",
    }

    # Analyze the problem severity
    result = identifier.analyze_problem_severity(problem)

    # Check specific values
    assert result["severity"] == "low"
    assert result["potential_impact_of_solution"] == "low"
    assert result["user_willingness_to_pay"] == "low"


@patch("niche_analysis.problem_identifier.datetime")
def test_problem_timestamp(mock_datetime):
    """Test that problems include a timestamp."""
    # Mock datetime.now() to return a fixed datetime
    mock_now = datetime(2023, 1, 1, 12, 0, 0)
    mock_datetime.now.return_value = mock_now

    identifier = ProblemIdentifier()

    # Create a problem
    problem = identifier._create_problem(
        "Test Problem", "A test problem", ["consequence 1", "consequence 2"], "medium"
    )

    # Check that the timestamp is the mocked datetime
    assert problem["timestamp"] == mock_now.isoformat()


def test_create_problem():
    """Test _create_problem method."""
    identifier = ProblemIdentifier()

    # Create a problem
    problem = identifier._create_problem(
        "Test Problem", "A test problem", ["consequence 1", "consequence 2"], "medium"
    )

    # Check that the problem has the expected keys
    assert "id" in problem
    assert "name" in problem
    assert "description" in problem
    assert "consequences" in problem
    assert "severity" in problem
    assert "current_solutions" in problem
    assert "solution_gaps" in problem
    assert "timestamp" in problem

    # Check specific values
    assert problem["name"] == "Test Problem"
    assert problem["description"] == "A test problem"
    assert problem["consequences"] == ["consequence 1", "consequence 2"]
    assert problem["severity"] == "medium"
    assert isinstance(problem["current_solutions"], dict)
    assert isinstance(problem["solution_gaps"], dict)


def test_identify_problems_for_multiple_niches():
    """Test identify_problems method for multiple niches."""
    identifier = ProblemIdentifier()

    # Identify problems for multiple niches
    niches = ["e-commerce", "content creation", "freelancing"]
    all_problems = []

    for niche in niches:
        problems = identifier.identify_problems(niche)
        all_problems.extend(problems)

    # Check that problems were identified for each niche
    assert len(all_problems) > 0

    # Check that the problems are unique
    problem_ids = [problem["id"] for problem in all_problems]
    assert len(problem_ids) == len(set(problem_ids))


def test_str_representation():
    """Test string representation of ProblemIdentifier."""
    identifier = ProblemIdentifier()

    # Check the string representation
    assert (
        str(identifier)
        == "Problem Identifier: Identifies user problems and pain points in specific niches"
    )
