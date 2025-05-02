"""
Tests for the user personas components in the Marketing module.
"""



from marketing.user_personas import (
    DemographicAnalyzer,
    PainPointIdentifier,
    PersonaCreator,
)


def test_persona_creator_init():
    """Test PersonaCreator initialization."""
    creator = PersonaCreator()

    # Check that the creator has the expected attributes
    assert hasattr(creator, "name")
    assert hasattr(creator, "description")


def test_create_persona():
    """Test create_persona method."""
    creator = PersonaCreator()

    # Create a persona
    persona = creator.create_persona(
        name="Small Business Owner",
        description="Owner of a small e-commerce business",
        demographics={
            "age_range": "30-45",
            "gender": "mixed",
            "location": "urban",
            "education": "college degree",
            "income": "middle to upper-middle",
        },
        pain_points=[
            "Limited time for marketing",
            "Difficulty creating product descriptions",
            "Inventory management challenges",
        ],
        goals=[
            "Increase sales",
            "Reduce time spent on routine tasks",
            "Improve customer satisfaction",
        ],
        behaviors=[
            "Price-conscious but willing to invest in time-saving tools",
            "Tech-savvy but not technical",
            "Values ease of use and quick results",
        ],
    )

    # Check that the persona has the expected attributes
    assert "id" in persona
    assert persona["name"] == "Small Business Owner"
    assert persona["description"] == "Owner of a small e-commerce business"
    assert "demographics" in persona
    assert "pain_points" in persona
    assert "goals" in persona
    assert "behaviors" in persona
    assert "created_at" in persona

    # Check specific values
    assert persona["demographics"]["age_range"] == "30-45"
    assert "Limited time for marketing" in persona["pain_points"]
    assert "Increase sales" in persona["goals"]
    assert "Price-conscious but willing to invest in time-saving tools" in persona["behaviors"]


def test_demographic_analyzer_init():
    """Test DemographicAnalyzer initialization."""
    analyzer = DemographicAnalyzer()

    # Check that the analyzer has the expected attributes
    assert hasattr(analyzer, "name")
    assert hasattr(analyzer, "description")


def test_analyze_demographics():
    """Test analyze_demographics method."""
    analyzer = DemographicAnalyzer()

    # Create test demographics
    demographics = {
        "age_range": "30-45",
        "gender": "mixed",
        "location": "urban",
        "education": "college degree",
        "income": "middle to upper-middle",
    }

    # Analyze demographics
    result = analyzer.analyze_demographics(demographics, niche="e-commerce")

    # Check that the result has the expected keys
    assert "id" in result
    assert "niche" in result
    assert "demographics" in result
    assert "analysis" in result
    assert "recommendations" in result
    assert "timestamp" in result

    # Check specific values
    assert result["niche"] == "e-commerce"
    assert result["demographics"] == demographics
    assert "analysis" in result
    assert isinstance(result["recommendations"], list)
    assert len(result["recommendations"]) > 0


def test_pain_point_identifier_init():
    """Test PainPointIdentifier initialization."""
    identifier = PainPointIdentifier()

    # Check that the identifier has the expected attributes
    assert hasattr(identifier, "name")
    assert hasattr(identifier, "description")


def test_identify_pain_points():
    """Test identify_pain_points method."""
    identifier = PainPointIdentifier()

    # Identify pain points for a niche
    result = identifier.identify_pain_points("e-commerce")

    # Check that the result is a list of pain points
    assert isinstance(result, list)
    assert len(result) > 0

    # Check that each pain point has the expected keys
    for pain_point in result:
        assert "id" in pain_point
        assert "name" in pain_point
        assert "description" in pain_point
        assert "severity" in pain_point
        assert "impact" in pain_point
        assert "current_solutions" in pain_point
        assert "solution_gaps" in pain_point


def test_analyze_pain_point():
    """Test analyze_pain_point method."""
    identifier = PainPointIdentifier()

    # Create a test pain point
    pain_point = {
        "id": "pp1",
        "name": "Limited time for marketing",
        "description": "Small business owners have limited time for marketing activities",
        "severity": "high",
        "impact": "Reduced visibility and sales",
    }

    # Analyze the pain point
    result = identifier.analyze_pain_point(pain_point, niche="e-commerce")

    # Check that the result has the expected keys
    assert "id" in result
    assert "pain_point_id" in result
    assert "niche" in result
    assert "analysis" in result
    assert "potential_solutions" in result
    assert "user_willingness_to_pay" in result
    assert "timestamp" in result

    # Check specific values
    assert result["pain_point_id"] == "pp1"
    assert result["niche"] == "e-commerce"
    assert isinstance(result["analysis"], dict)
    assert isinstance(result["potential_solutions"], list)
    assert len(result["potential_solutions"]) > 0
    assert result["user_willingness_to_pay"] in ["low", "medium", "high"]
