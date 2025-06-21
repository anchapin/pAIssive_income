import pytest
from niche_analysis import ProblemIdentifier
from niche_analysis.schemas import Problem, ProblemSeverityAnalysis

def test_identify_problems_known_niche():
    identifier = ProblemIdentifier()
    problems = identifier.identify_problems("inventory management for small e-commerce")
    assert isinstance(problems, list)
    assert len(problems) > 0
    assert all(isinstance(p, Problem) for p in problems)
    assert problems[0].name == "Overstocking"

def test_identify_problems_unknown_niche_fallback():
    identifier = ProblemIdentifier()
    problems = identifier.identify_problems("totally new niche")
    assert isinstance(problems, list)
    assert len(problems) > 0
    assert all(isinstance(p, Problem) for p in problems)

def test_analyze_problem_severity_high():
    identifier = ProblemIdentifier()
    problems = identifier.identify_problems("inventory management for small e-commerce")
    sev = identifier.analyze_problem_severity(problems[0])
    assert isinstance(sev, ProblemSeverityAnalysis)
    assert sev.severity == "high"
    assert "impact_on_users" in sev.analysis
