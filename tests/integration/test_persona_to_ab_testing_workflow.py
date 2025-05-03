"""
Integration tests for the user persona → content strategy → A/B testing workflow.

This module tests the complete workflow from user persona creation through content
strategy development to A/B testing of content.
"""

import pytest
from unittest.mock import patch, MagicMock

from marketing import 
from niche_analysis import MarketAnalyzer




(
    PersonaCreator, ContentGenerator, ContentTemplate,
    StyleAdjuster, ToneAnalyzer, ABTesting,
    ConcreteContentGenerator, ChannelStrategy
)
@pytest.fixture
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
    Test the complete workflow from user persona to A/B testing.
    
    This test verifies that:
    1. User personas can be created based on market analysis
    2. Content can be generated for specific personas
    3. Content can be adjusted for different tones and styles
    4. A/B tests can be created to test different content variations
    5. Test results can be analyzed
    """
    # Step 1: Analyze target users for a niche
    niche = "content creation"
    user_analysis = market_analyzer.analyze_target_users(niche)
    
    # Verify user analysis results
    assert "user_segments" in user_analysis
    assert len(user_analysis["user_segments"]) > 0
    
    # Step 2: Create user personas based on the analysis
    personas = []
    for segment in user_analysis["user_segments"]:
        # Extract demographic and psychographic information
        demographics = user_analysis["demographics"].get(segment, {})
        psychographics = user_analysis["psychographics"].get(segment, {})
        pain_points = user_analysis["pain_points"]
        goals = user_analysis["goals"]
        
        # Create a persona for this segment
        persona = persona_creator.create_persona(
            name=f"Persona for {segment}",
            segment=segment,
            demographics=demographics,
            psychographics=psychographics,
            pain_points=pain_points[:2],  # Use first two pain points
            goals=goals[:2],  # Use first two goals
            buying_behavior=user_analysis["buying_behavior"]
        )
        
        personas.append(persona)
    
    # Verify persona creation
    assert len(personas) == len(user_analysis["user_segments"])
    for persona in personas:
        assert "id" in persona
        assert "name" in persona
        assert "segment" in persona
        assert "pain_points" in persona
        assert "goals" in persona
    
    # Step 3: Generate content for each persona
    content_pieces = []
    for persona in personas:
        # Generate a landing page for this persona
        content = content_generator.generate_content(
            content_type="landing_page",
            target_persona=persona,
            key_messages=[
                f"Solve your {persona['pain_points'][0]}",
                f"Achieve your {persona['goals'][0]}"
            ],
            tone="professional",
            style="direct"
        )
        
        content_pieces.append({
            "persona_id": persona["id"],
            "content": content
        })
    
    # Verify content generation
    assert len(content_pieces) == len(personas)
    for piece in content_pieces:
        assert "headline" in piece["content"]
        assert "body" in piece["content"]
        assert "cta" in piece["content"]
    
    # Step 4: Create content variations with different tones and styles
    variations = []
    for piece in content_pieces:
        original_content = piece["content"]
        persona_id = piece["persona_id"]
        
        # Create variations with different tones
        tones = ["professional", "friendly", "authoritative"]
        for tone in tones:
            if tone != "professional":  # Skip the original tone
                tone_variation = tone_analyzer.adjust_tone(
                    content=original_content,
                    target_tone=tone
                )
                
                variations.append({
                    "persona_id": persona_id,
                    "variation_type": "tone",
                    "variation_value": tone,
                    "content": tone_variation
                })
        
        # Create variations with different styles
        styles = ["direct", "storytelling", "question-based"]
        for style in styles:
            if style != "direct":  # Skip the original style
                style_variation = style_adjuster.adjust_style(
                    content=original_content,
                    target_style=style
                )
                
                variations.append({
                    "persona_id": persona_id,
                    "variation_type": "style",
                    "variation_value": style,
                    "content": style_variation
                })
    
    # Verify variation creation
    assert len(variations) > 0
    
    # Step 5: Create A/B tests for each persona with its content variations
    tests = []
    for persona in personas:
        # Get the original content for this persona
        original_content = next(
            piece["content"] for piece in content_pieces 
            if piece["persona_id"] == persona["id"]
        )
        
        # Get variations for this persona
        persona_variations = [
            var for var in variations 
            if var["persona_id"] == persona["id"]
        ]
        
        # Create variants for the A/B test
        variants = [
            {
                "name": "Control",
                "is_control": True,
                "content": original_content
            }
        ]
        
        for var in persona_variations:
            variant = {
                "name": f"{var['variation_type'].capitalize()} - {var['variation_value']}",
                "is_control": False,
                "content": var["content"]
            }
            variants.append(variant)
        
        # Create the A/B test
        test = ab_testing.create_test(
            name=f"Content Test for {persona['name']}",
            description=f"Testing content variations for {persona['segment']} persona",
            content_type="landing_page",
            test_type="a_b",
            variants=variants
        )
        
        tests.append(test)
    
    # Verify test creation
    assert len(tests) == len(personas)
    for test in tests:
        assert "id" in test
        assert "variants" in test
        assert len(test["variants"]) > 1  # Should have control + variations
    
    # Step 6: Simulate interactions with the tests
    for test in tests:
        # Get the persona for this test
        persona_name = test["name"].replace("Content Test for ", "")
        persona = next(p for p in personas if p["name"] == persona_name)
        
        # Simulate different interaction patterns based on persona characteristics
        for variant in test["variants"]:
            variant_id = variant["id"]
            
            # Base impressions - higher for more common personas
            base_impressions = 1000
            if "age_range" in persona.get("demographics", {}):
                age_range = persona["demographics"]["age_range"]
                if "18-24" in age_range:
                    base_impressions = 1500  # More impressions for younger audience
                elif "55+" in age_range:
                    base_impressions = 800  # Fewer impressions for older audience
            
            # Simulate impressions
            for _ in range(base_impressions):
                ab_testing.record_interaction(test["id"], variant_id, "impression")
            
            # Calculate conversion rate based on variant and persona match
            base_conversion_rate = 0.1  # 10% base conversion rate
            
            # Adjust based on variant type
            if not variant["is_control"]:
                variant_name = variant["name"]
                if "Tone" in variant_name:
                    tone = variant_name.split(" - ")[1]
                    # Adjust conversion rate based on persona-tone match
                    if "professional" in persona.get("psychographics", {}).get("communication_preference", ""):
                        if tone == "professional":
                            base_conversion_rate *= 1.3  # 30% boost for matching tone
                        else:
                            base_conversion_rate *= 0.9  # 10% reduction for mismatched tone
                    elif "friendly" in persona.get("psychographics", {}).get("communication_preference", ""):
                        if tone == "friendly":
                            base_conversion_rate *= 1.3
                        else:
                            base_conversion_rate *= 0.9
                elif "Style" in variant_name:
                    style = variant_name.split(" - ")[1]
                    # Adjust conversion rate based on persona-style match
                    if "direct" in persona.get("psychographics", {}).get("decision_making", ""):
                        if style == "direct":
                            base_conversion_rate *= 1.2
                        else:
                            base_conversion_rate *= 0.95
                    elif "story" in persona.get("psychographics", {}).get("decision_making", ""):
                        if style == "storytelling":
                            base_conversion_rate *= 1.2
                        else:
                            base_conversion_rate *= 0.95
            
            # Simulate conversions
            conversion_count = int(base_impressions * base_conversion_rate)
            for _ in range(conversion_count):
                ab_testing.record_interaction(test["id"], variant_id, "conversion")
    
    # Step 7: Analyze test results
    results = []
    for test in tests:
        result = ab_testing.analyze_test(test["id"])
        results.append(result)
    
    # Verify analysis results
    assert len(results) == len(tests)
    for result in results:
        assert "variants" in result
        assert "winner" in result
        assert "confidence_level" in result
        assert result["confidence_level"] > 0


def test_persona_to_multichannel_content_strategy(
    persona_creator, content_generator, channel_strategy, market_analyzer
):
    """
    Test the workflow for creating a multi-channel content strategy based on personas.
    
    This test verifies that:
    1. User personas can be created based on market analysis
    2. Channel strategies can be developed for different personas
    3. Content can be generated for different channels and personas
    4. A complete content strategy can be created
    """
    # Step 1: Analyze target users for a niche
    niche = "digital marketing"
    user_analysis = market_analyzer.analyze_target_users(niche)
    
    # Step 2: Create user personas based on the analysis
    personas = []
    for segment in user_analysis["user_segments"][:2]:  # Use first two segments
        # Create a persona for this segment
        persona = persona_creator.create_persona(
            name=f"Persona for {segment}",
            segment=segment,
            demographics=user_analysis["demographics"].get(segment, {}),
            psychographics=user_analysis["psychographics"].get(segment, {}),
            pain_points=user_analysis["pain_points"][:2],
            goals=user_analysis["goals"][:2],
            buying_behavior=user_analysis["buying_behavior"]
        )
        
        personas.append(persona)
    
    # Step 3: Determine optimal channels for each persona
    persona_channels = {}
    for persona in personas:
        # Analyze channels for this persona
        channels = channel_strategy.analyze_channels_for_persona(persona)
        
        # Select top 3 channels
        top_channels = sorted(
            channels, 
            key=lambda c: c["effectiveness_score"], 
            reverse=True
        )[:3]
        
        persona_channels[persona["id"]] = top_channels
    
    # Verify channel selection
    assert len(persona_channels) == len(personas)
    for persona_id, channels in persona_channels.items():
        assert len(channels) > 0
    
    # Step 4: Generate content for each persona and channel
    content_strategy = {}
    for persona in personas:
        persona_id = persona["id"]
        channels = persona_channels[persona_id]
        
        persona_content = {}
        for channel in channels:
            channel_name = channel["name"]
            
            # Generate content for this channel
            content = content_generator.generate_content(
                content_type=channel_name,
                target_persona=persona,
                key_messages=[
                    f"Solve your {persona['pain_points'][0]}",
                    f"Achieve your {persona['goals'][0]}"
                ],
                tone=channel.get("recommended_tone", "professional"),
                style=channel.get("recommended_style", "direct")
            )
            
            persona_content[channel_name] = content
        
        content_strategy[persona_id] = persona_content
    
    # Verify content strategy
    assert len(content_strategy) == len(personas)
    for persona_id, channels_content in content_strategy.items():
        assert len(channels_content) > 0
        
    # Step 5: Create a content calendar
    content_calendar = channel_strategy.create_content_calendar(
        personas=personas,
        content_strategy=content_strategy,
        start_date="2023-01-01",
        end_date="2023-03-31"
    )
    
    # Verify content calendar
    assert "calendar_items" in content_calendar
    assert len(content_calendar["calendar_items"]) > 0
    for item in content_calendar["calendar_items"]:
        assert "date" in item
        assert "channel" in item
        assert "persona_id" in item
        assert "content_type" in item