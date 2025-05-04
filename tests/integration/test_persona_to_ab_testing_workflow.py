"""
"""
Integration tests for the user persona → content strategy → A/B testing workflow.
Integration tests for the user persona → content strategy → A/B testing workflow.


This module tests the complete workflow from user persona creation through content
This module tests the complete workflow from user persona creation through content
strategy development to A/B testing of content.
strategy development to A/B testing of content.
"""
"""


from unittest.mock import MagicMock, patch
from unittest.mock import MagicMock, patch


import pytest
import pytest


from niche_analysis import MarketAnalyzer
from niche_analysis import MarketAnalyzer


(
(
PersonaCreator, ContentGenerator, ContentTemplate,
PersonaCreator, ContentGenerator, ContentTemplate,
StyleAdjuster, ToneAnalyzer, ABTesting,
StyleAdjuster, ToneAnalyzer, ABTesting,
ConcreteContentGenerator, ChannelStrategy
ConcreteContentGenerator, ChannelStrategy
)
)
@pytest.fixture
@pytest.fixture
def persona_creator():
    def persona_creator():
    """Create a persona creator instance for testing."""
    return PersonaCreator()


    @pytest.fixture
    def content_generator():
    """Create a content generator instance for testing."""
    return ConcreteContentGenerator()


    @pytest.fixture
    def style_adjuster():
    """Create a style adjuster instance for testing."""
    return StyleAdjuster()


    @pytest.fixture
    def tone_analyzer():
    """Create a tone analyzer instance for testing."""
    return ToneAnalyzer()


    @pytest.fixture
    def ab_testing():
    """Create an A/B testing instance for testing."""
    return ABTesting()


    @pytest.fixture
    def market_analyzer():
    """Create a market analyzer instance for testing."""
    return MarketAnalyzer()


    @pytest.fixture
    def channel_strategy():
    """Create a channel strategy instance for testing."""
    return ChannelStrategy()


    def test_persona_to_content_to_ab_testing_workflow(
    persona_creator, content_generator, style_adjuster,
    tone_analyzer, ab_testing, market_analyzer
    ):
    """
    """
    Test the complete workflow from user persona to A/B testing.
    Test the complete workflow from user persona to A/B testing.


    This test verifies that:
    This test verifies that:
    1. User personas can be created based on market analysis
    1. User personas can be created based on market analysis
    2. Content can be generated for specific personas
    2. Content can be generated for specific personas
    3. Content can be adjusted for different tones and styles
    3. Content can be adjusted for different tones and styles
    4. A/B tests can be created to test different content variations
    4. A/B tests can be created to test different content variations
    5. Test results can be analyzed
    5. Test results can be analyzed
    """
    """
    # Step 1: Analyze target users for a niche
    # Step 1: Analyze target users for a niche
    niche = "content creation"
    niche = "content creation"
    user_analysis = market_analyzer.analyze_target_users(niche)
    user_analysis = market_analyzer.analyze_target_users(niche)


    # Verify user analysis results
    # Verify user analysis results
    assert "user_segments" in user_analysis
    assert "user_segments" in user_analysis
    assert len(user_analysis["user_segments"]) > 0
    assert len(user_analysis["user_segments"]) > 0


    # Step 2: Create user personas based on the analysis
    # Step 2: Create user personas based on the analysis
    personas = []
    personas = []
    for segment in user_analysis["user_segments"]:
    for segment in user_analysis["user_segments"]:
    # Extract demographic and psychographic information
    # Extract demographic and psychographic information
    demographics = user_analysis["demographics"].get(segment, {})
    demographics = user_analysis["demographics"].get(segment, {})
    psychographics = user_analysis["psychographics"].get(segment, {})
    psychographics = user_analysis["psychographics"].get(segment, {})
    pain_points = user_analysis["pain_points"]
    pain_points = user_analysis["pain_points"]
    goals = user_analysis["goals"]
    goals = user_analysis["goals"]


    # Create a persona for this segment
    # Create a persona for this segment
    persona = persona_creator.create_persona(
    persona = persona_creator.create_persona(
    name=f"Persona for {segment}",
    name=f"Persona for {segment}",
    segment=segment,
    segment=segment,
    demographics=demographics,
    demographics=demographics,
    psychographics=psychographics,
    psychographics=psychographics,
    pain_points=pain_points[:2],  # Use first two pain points
    pain_points=pain_points[:2],  # Use first two pain points
    goals=goals[:2],  # Use first two goals
    goals=goals[:2],  # Use first two goals
    buying_behavior=user_analysis["buying_behavior"]
    buying_behavior=user_analysis["buying_behavior"]
    )
    )


    personas.append(persona)
    personas.append(persona)


    # Verify persona creation
    # Verify persona creation
    assert len(personas) == len(user_analysis["user_segments"])
    assert len(personas) == len(user_analysis["user_segments"])
    for persona in personas:
    for persona in personas:
    assert "id" in persona
    assert "id" in persona
    assert "name" in persona
    assert "name" in persona
    assert "segment" in persona
    assert "segment" in persona
    assert "pain_points" in persona
    assert "pain_points" in persona
    assert "goals" in persona
    assert "goals" in persona


    # Step 3: Generate content for each persona
    # Step 3: Generate content for each persona
    content_pieces = []
    content_pieces = []
    for persona in personas:
    for persona in personas:
    # Generate a landing page for this persona
    # Generate a landing page for this persona
    content = content_generator.generate_content(
    content = content_generator.generate_content(
    content_type="landing_page",
    content_type="landing_page",
    target_persona=persona,
    target_persona=persona,
    key_messages=[
    key_messages=[
    f"Solve your {persona['pain_points'][0]}",
    f"Solve your {persona['pain_points'][0]}",
    f"Achieve your {persona['goals'][0]}"
    f"Achieve your {persona['goals'][0]}"
    ],
    ],
    tone="professional",
    tone="professional",
    style="direct"
    style="direct"
    )
    )


    content_pieces.append({
    content_pieces.append({
    "persona_id": persona["id"],
    "persona_id": persona["id"],
    "content": content
    "content": content
    })
    })


    # Verify content generation
    # Verify content generation
    assert len(content_pieces) == len(personas)
    assert len(content_pieces) == len(personas)
    for piece in content_pieces:
    for piece in content_pieces:
    assert "headline" in piece["content"]
    assert "headline" in piece["content"]
    assert "body" in piece["content"]
    assert "body" in piece["content"]
    assert "cta" in piece["content"]
    assert "cta" in piece["content"]


    # Step 4: Create content variations with different tones and styles
    # Step 4: Create content variations with different tones and styles
    variations = []
    variations = []
    for piece in content_pieces:
    for piece in content_pieces:
    original_content = piece["content"]
    original_content = piece["content"]
    persona_id = piece["persona_id"]
    persona_id = piece["persona_id"]


    # Create variations with different tones
    # Create variations with different tones
    tones = ["professional", "friendly", "authoritative"]
    tones = ["professional", "friendly", "authoritative"]
    for tone in tones:
    for tone in tones:
    if tone != "professional":  # Skip the original tone
    if tone != "professional":  # Skip the original tone
    tone_variation = tone_analyzer.adjust_tone(
    tone_variation = tone_analyzer.adjust_tone(
    content=original_content,
    content=original_content,
    target_tone=tone
    target_tone=tone
    )
    )


    variations.append({
    variations.append({
    "persona_id": persona_id,
    "persona_id": persona_id,
    "variation_type": "tone",
    "variation_type": "tone",
    "variation_value": tone,
    "variation_value": tone,
    "content": tone_variation
    "content": tone_variation
    })
    })


    # Create variations with different styles
    # Create variations with different styles
    styles = ["direct", "storytelling", "question-based"]
    styles = ["direct", "storytelling", "question-based"]
    for style in styles:
    for style in styles:
    if style != "direct":  # Skip the original style
    if style != "direct":  # Skip the original style
    style_variation = style_adjuster.adjust_style(
    style_variation = style_adjuster.adjust_style(
    content=original_content,
    content=original_content,
    target_style=style
    target_style=style
    )
    )


    variations.append({
    variations.append({
    "persona_id": persona_id,
    "persona_id": persona_id,
    "variation_type": "style",
    "variation_type": "style",
    "variation_value": style,
    "variation_value": style,
    "content": style_variation
    "content": style_variation
    })
    })


    # Verify variation creation
    # Verify variation creation
    assert len(variations) > 0
    assert len(variations) > 0


    # Step 5: Create A/B tests for each persona with its content variations
    # Step 5: Create A/B tests for each persona with its content variations
    tests = []
    tests = []
    for persona in personas:
    for persona in personas:
    # Get the original content for this persona
    # Get the original content for this persona
    original_content = next(
    original_content = next(
    piece["content"] for piece in content_pieces
    piece["content"] for piece in content_pieces
    if piece["persona_id"] == persona["id"]
    if piece["persona_id"] == persona["id"]
    )
    )


    # Get variations for this persona
    # Get variations for this persona
    persona_variations = [
    persona_variations = [
    var for var in variations
    var for var in variations
    if var["persona_id"] == persona["id"]
    if var["persona_id"] == persona["id"]
    ]
    ]


    # Create variants for the A/B test
    # Create variants for the A/B test
    variants = [
    variants = [
    {
    {
    "name": "Control",
    "name": "Control",
    "is_control": True,
    "is_control": True,
    "content": original_content
    "content": original_content
    }
    }
    ]
    ]


    for var in persona_variations:
    for var in persona_variations:
    variant = {
    variant = {
    "name": f"{var['variation_type'].capitalize()} - {var['variation_value']}",
    "name": f"{var['variation_type'].capitalize()} - {var['variation_value']}",
    "is_control": False,
    "is_control": False,
    "content": var["content"]
    "content": var["content"]
    }
    }
    variants.append(variant)
    variants.append(variant)


    # Create the A/B test
    # Create the A/B test
    test = ab_testing.create_test(
    test = ab_testing.create_test(
    name=f"Content Test for {persona['name']}",
    name=f"Content Test for {persona['name']}",
    description=f"Testing content variations for {persona['segment']} persona",
    description=f"Testing content variations for {persona['segment']} persona",
    content_type="landing_page",
    content_type="landing_page",
    test_type="a_b",
    test_type="a_b",
    variants=variants
    variants=variants
    )
    )


    tests.append(test)
    tests.append(test)


    # Verify test creation
    # Verify test creation
    assert len(tests) == len(personas)
    assert len(tests) == len(personas)
    for test in tests:
    for test in tests:
    assert "id" in test
    assert "id" in test
    assert "variants" in test
    assert "variants" in test
    assert len(test["variants"]) > 1  # Should have control + variations
    assert len(test["variants"]) > 1  # Should have control + variations


    # Step 6: Simulate interactions with the tests
    # Step 6: Simulate interactions with the tests
    for test in tests:
    for test in tests:
    # Get the persona for this test
    # Get the persona for this test
    persona_name = test["name"].replace("Content Test for ", "")
    persona_name = test["name"].replace("Content Test for ", "")
    persona = next(p for p in personas if p["name"] == persona_name)
    persona = next(p for p in personas if p["name"] == persona_name)


    # Simulate different interaction patterns based on persona characteristics
    # Simulate different interaction patterns based on persona characteristics
    for variant in test["variants"]:
    for variant in test["variants"]:
    variant_id = variant["id"]
    variant_id = variant["id"]


    # Base impressions - higher for more common personas
    # Base impressions - higher for more common personas
    base_impressions = 1000
    base_impressions = 1000
    if "age_range" in persona.get("demographics", {}):
    if "age_range" in persona.get("demographics", {}):
    age_range = persona["demographics"]["age_range"]
    age_range = persona["demographics"]["age_range"]
    if "18-24" in age_range:
    if "18-24" in age_range:
    base_impressions = 1500  # More impressions for younger audience
    base_impressions = 1500  # More impressions for younger audience
    elif "55+" in age_range:
    elif "55+" in age_range:
    base_impressions = 800  # Fewer impressions for older audience
    base_impressions = 800  # Fewer impressions for older audience


    # Simulate impressions
    # Simulate impressions
    for _ in range(base_impressions):
    for _ in range(base_impressions):
    ab_testing.record_interaction(test["id"], variant_id, "impression")
    ab_testing.record_interaction(test["id"], variant_id, "impression")


    # Calculate conversion rate based on variant and persona match
    # Calculate conversion rate based on variant and persona match
    base_conversion_rate = 0.1  # 10% base conversion rate
    base_conversion_rate = 0.1  # 10% base conversion rate


    # Adjust based on variant type
    # Adjust based on variant type
    if not variant["is_control"]:
    if not variant["is_control"]:
    variant_name = variant["name"]
    variant_name = variant["name"]
    if "Tone" in variant_name:
    if "Tone" in variant_name:
    tone = variant_name.split(" - ")[1]
    tone = variant_name.split(" - ")[1]
    # Adjust conversion rate based on persona-tone match
    # Adjust conversion rate based on persona-tone match
    if "professional" in persona.get("psychographics", {}).get("communication_preference", ""):
    if "professional" in persona.get("psychographics", {}).get("communication_preference", ""):
    if tone == "professional":
    if tone == "professional":
    base_conversion_rate *= 1.3  # 30% boost for matching tone
    base_conversion_rate *= 1.3  # 30% boost for matching tone
    else:
    else:
    base_conversion_rate *= 0.9  # 10% reduction for mismatched tone
    base_conversion_rate *= 0.9  # 10% reduction for mismatched tone
    elif "friendly" in persona.get("psychographics", {}).get("communication_preference", ""):
    elif "friendly" in persona.get("psychographics", {}).get("communication_preference", ""):
    if tone == "friendly":
    if tone == "friendly":
    base_conversion_rate *= 1.3
    base_conversion_rate *= 1.3
    else:
    else:
    base_conversion_rate *= 0.9
    base_conversion_rate *= 0.9
    elif "Style" in variant_name:
    elif "Style" in variant_name:
    style = variant_name.split(" - ")[1]
    style = variant_name.split(" - ")[1]
    # Adjust conversion rate based on persona-style match
    # Adjust conversion rate based on persona-style match
    if "direct" in persona.get("psychographics", {}).get("decision_making", ""):
    if "direct" in persona.get("psychographics", {}).get("decision_making", ""):
    if style == "direct":
    if style == "direct":
    base_conversion_rate *= 1.2
    base_conversion_rate *= 1.2
    else:
    else:
    base_conversion_rate *= 0.95
    base_conversion_rate *= 0.95
    elif "story" in persona.get("psychographics", {}).get("decision_making", ""):
    elif "story" in persona.get("psychographics", {}).get("decision_making", ""):
    if style == "storytelling":
    if style == "storytelling":
    base_conversion_rate *= 1.2
    base_conversion_rate *= 1.2
    else:
    else:
    base_conversion_rate *= 0.95
    base_conversion_rate *= 0.95


    # Simulate conversions
    # Simulate conversions
    conversion_count = int(base_impressions * base_conversion_rate)
    conversion_count = int(base_impressions * base_conversion_rate)
    for _ in range(conversion_count):
    for _ in range(conversion_count):
    ab_testing.record_interaction(test["id"], variant_id, "conversion")
    ab_testing.record_interaction(test["id"], variant_id, "conversion")


    # Step 7: Analyze test results
    # Step 7: Analyze test results
    results = []
    results = []
    for test in tests:
    for test in tests:
    result = ab_testing.analyze_test(test["id"])
    result = ab_testing.analyze_test(test["id"])
    results.append(result)
    results.append(result)


    # Verify analysis results
    # Verify analysis results
    assert len(results) == len(tests)
    assert len(results) == len(tests)
    for result in results:
    for result in results:
    assert "variants" in result
    assert "variants" in result
    assert "winner" in result
    assert "winner" in result
    assert "confidence_level" in result
    assert "confidence_level" in result
    assert result["confidence_level"] > 0
    assert result["confidence_level"] > 0




    def test_persona_to_multichannel_content_strategy(
    def test_persona_to_multichannel_content_strategy(
    persona_creator, content_generator, channel_strategy, market_analyzer
    persona_creator, content_generator, channel_strategy, market_analyzer
    ):
    ):
    """
    """
    Test the workflow for creating a multi-channel content strategy based on personas.
    Test the workflow for creating a multi-channel content strategy based on personas.


    This test verifies that:
    This test verifies that:
    1. User personas can be created based on market analysis
    1. User personas can be created based on market analysis
    2. Channel strategies can be developed for different personas
    2. Channel strategies can be developed for different personas
    3. Content can be generated for different channels and personas
    3. Content can be generated for different channels and personas
    4. A complete content strategy can be created
    4. A complete content strategy can be created
    """
    """
    # Step 1: Analyze target users for a niche
    # Step 1: Analyze target users for a niche
    niche = "digital marketing"
    niche = "digital marketing"
    user_analysis = market_analyzer.analyze_target_users(niche)
    user_analysis = market_analyzer.analyze_target_users(niche)


    # Step 2: Create user personas based on the analysis
    # Step 2: Create user personas based on the analysis
    personas = []
    personas = []
    for segment in user_analysis["user_segments"][:2]:  # Use first two segments
    for segment in user_analysis["user_segments"][:2]:  # Use first two segments
    # Create a persona for this segment
    # Create a persona for this segment
    persona = persona_creator.create_persona(
    persona = persona_creator.create_persona(
    name=f"Persona for {segment}",
    name=f"Persona for {segment}",
    segment=segment,
    segment=segment,
    demographics=user_analysis["demographics"].get(segment, {}),
    demographics=user_analysis["demographics"].get(segment, {}),
    psychographics=user_analysis["psychographics"].get(segment, {}),
    psychographics=user_analysis["psychographics"].get(segment, {}),
    pain_points=user_analysis["pain_points"][:2],
    pain_points=user_analysis["pain_points"][:2],
    goals=user_analysis["goals"][:2],
    goals=user_analysis["goals"][:2],
    buying_behavior=user_analysis["buying_behavior"]
    buying_behavior=user_analysis["buying_behavior"]
    )
    )


    personas.append(persona)
    personas.append(persona)


    # Step 3: Determine optimal channels for each persona
    # Step 3: Determine optimal channels for each persona
    persona_channels = {}
    persona_channels = {}
    for persona in personas:
    for persona in personas:
    # Analyze channels for this persona
    # Analyze channels for this persona
    channels = channel_strategy.analyze_channels_for_persona(persona)
    channels = channel_strategy.analyze_channels_for_persona(persona)


    # Select top 3 channels
    # Select top 3 channels
    top_channels = sorted(
    top_channels = sorted(
    channels,
    channels,
    key=lambda c: c["effectiveness_score"],
    key=lambda c: c["effectiveness_score"],
    reverse=True
    reverse=True
    )[:3]
    )[:3]


    persona_channels[persona["id"]] = top_channels
    persona_channels[persona["id"]] = top_channels


    # Verify channel selection
    # Verify channel selection
    assert len(persona_channels) == len(personas)
    assert len(persona_channels) == len(personas)
    for persona_id, channels in persona_channels.items():
    for persona_id, channels in persona_channels.items():
    assert len(channels) > 0
    assert len(channels) > 0


    # Step 4: Generate content for each persona and channel
    # Step 4: Generate content for each persona and channel
    content_strategy = {}
    content_strategy = {}
    for persona in personas:
    for persona in personas:
    persona_id = persona["id"]
    persona_id = persona["id"]
    channels = persona_channels[persona_id]
    channels = persona_channels[persona_id]


    persona_content = {}
    persona_content = {}
    for channel in channels:
    for channel in channels:
    channel_name = channel["name"]
    channel_name = channel["name"]


    # Generate content for this channel
    # Generate content for this channel
    content = content_generator.generate_content(
    content = content_generator.generate_content(
    content_type=channel_name,
    content_type=channel_name,
    target_persona=persona,
    target_persona=persona,
    key_messages=[
    key_messages=[
    f"Solve your {persona['pain_points'][0]}",
    f"Solve your {persona['pain_points'][0]}",
    f"Achieve your {persona['goals'][0]}"
    f"Achieve your {persona['goals'][0]}"
    ],
    ],
    tone=channel.get("recommended_tone", "professional"),
    tone=channel.get("recommended_tone", "professional"),
    style=channel.get("recommended_style", "direct")
    style=channel.get("recommended_style", "direct")
    )
    )


    persona_content[channel_name] = content
    persona_content[channel_name] = content


    content_strategy[persona_id] = persona_content
    content_strategy[persona_id] = persona_content


    # Verify content strategy
    # Verify content strategy
    assert len(content_strategy) == len(personas)
    assert len(content_strategy) == len(personas)
    for persona_id, channels_content in content_strategy.items():
    for persona_id, channels_content in content_strategy.items():
    assert len(channels_content) > 0
    assert len(channels_content) > 0


    # Step 5: Create a content calendar
    # Step 5: Create a content calendar
    content_calendar = channel_strategy.create_content_calendar(
    content_calendar = channel_strategy.create_content_calendar(
    personas=personas,
    personas=personas,
    content_strategy=content_strategy,
    content_strategy=content_strategy,
    start_date="2023-01-01",
    start_date="2023-01-01",
    end_date="2023-03-31"
    end_date="2023-03-31"
    )
    )


    # Verify content calendar
    # Verify content calendar
    assert "calendar_items" in content_calendar
    assert "calendar_items" in content_calendar
    assert len(content_calendar["calendar_items"]) > 0
    assert len(content_calendar["calendar_items"]) > 0
    for item in content_calendar["calendar_items"]:
    for item in content_calendar["calendar_items"]:
    assert "date" in item
    assert "date" in item
    assert "channel" in item
    assert "channel" in item
    assert "persona_id" in item
    assert "persona_id" in item
    assert "content_type" in item
    assert "content_type" in item