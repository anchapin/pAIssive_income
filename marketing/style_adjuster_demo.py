"""
Demo script for the style adjuster module.

This script demonstrates how to use the style adjuster to analyze and adjust
the style of marketing content.
"""

from marketing.user_personas import PersonaCreator
from marketing.content_templates import BlogPostTemplate
from marketing.content_generators import BlogPostGenerator
from marketing.tone_analyzer import ToneAnalyzer
from marketing.style_adjuster import StyleAdjuster


def demo_style_adjuster():
    """Demonstrate the StyleAdjuster."""
    print("\n" + "=" * 80)
    print("STYLE ADJUSTER DEMO")
    print("=" * 80)

    # Create a persona
    persona_creator = PersonaCreator()
    persona = persona_creator.create_persona(
        name="Professional YouTuber",
        description="Professional content creator on YouTube",
        pain_points=[
            "time-consuming script writing",
            "maintaining viewer engagement",
            "staying consistent with uploads",
        ],
        goals=[
            "increase video quality",
            "save time on content creation",
            "grow audience and engagement",
        ],
        demographics={
            "age_range": "25-45",
            "education": "college degree",
            "income": "middle to high",
        },
        behavior={
            "tech_savvy": "high",
            "price_sensitivity": "medium",
            "decision_making": "rational",
        },
    )

    # Create a blog post template with conversational tone
    template = BlogPostTemplate(
        title="How to Save 5 Hours a Week on YouTube Script Writing",
        target_persona=persona,
        key_points=[
            "The challenges of script writing for YouTube",
            "How AI can help streamline the process",
            "Step-by-step guide to using AI for script writing",
            "Real results from content creators",
        ],
        tone="conversational",
        call_to_action="Sign up for a free trial of our AI script writing tool",
        target_word_count=1500,
        include_images=True,
        seo_keywords=[
            "YouTube script writing",
            "AI for content creators",
            "save time on YouTube",
        ],
    )

    # Create a blog post generator
    generator = BlogPostGenerator(template)

    # Generate content
    content = generator.generate_content()

    print("\nGenerated Blog Post (Conversational Style):")
    print(f"Title: {content['title']}")
    print(f"Introduction: {content['introduction'][:200]}...")

    # Create a tone analyzer
    analyzer = ToneAnalyzer(content, target_tone="conversational")

    # Analyze content
    analysis_results = analyzer.analyze()

    print("\nTone Analysis Results:")
    print(f"Dominant Tone: {analysis_results['tone_analysis']['dominant_tone']}")
    print(f"Target Tone: {analysis_results['tone_analysis']['target_tone']}")
    print(f"Tone Consistency: {analysis_results['tone_analysis']['consistency']:.2f}")

    # Create a style adjuster to convert to formal style
    adjuster = StyleAdjuster(content, target_style="formal", analyzer=analyzer)

    # Analyze content for style adjustment
    adjuster.analyze()

    # Get style report
    report = adjuster.get_style_report()

    print("\nStyle Report:")
    print(f"Current Style: {report['current_style']}")
    print(f"Target Style: {report['target_style']}")
    print(f"Style Match: {report['style_match']}")
    print(f"Style Consistency: {report['style_consistency']:.2f}")
    print(f"Improvement Potential: {report['improvement_potential']:.2f}")

    # Get suggestions
    suggestions = adjuster.get_suggestions()

    print(f"\nTop {len(suggestions)} Style Adjustment Suggestions:")
    for i, suggestion in enumerate(suggestions[:5], 1):
        print(f"{i}. {suggestion['message']}")
        print(f"   Original: \"{suggestion['original'][:50]}...\"")
        print(f"   Replacement: \"{suggestion['replacement'][:50]}...\"")
        print(
            f"   Impact: {suggestion['impact']}, Confidence: {suggestion['confidence']:.2f}"
        )

    # Adjust content
    adjusted_content = adjuster.adjust()

    print("\nAdjusted Blog Post (Formal Style):")
    print(f"Title: {adjusted_content['adjusted_content']['title']}")
    print(
        f"Introduction: {adjusted_content['adjusted_content']['introduction'][:200]}..."
    )

    # Get adjustment statistics
    word_choice_count = len(adjusted_content["adjustments"]["word_choice"])
    sentence_structure_count = len(
        adjusted_content["adjustments"]["sentence_structure"]
    )
    paragraph_structure_count = len(
        adjusted_content["adjustments"]["paragraph_structure"]
    )
    punctuation_count = len(adjusted_content["adjustments"]["punctuation"])
    voice_count = len(adjusted_content["adjustments"]["voice"])

    print("\nAdjustment Statistics:")
    print(f"Word Choice Adjustments: {word_choice_count}")
    print(f"Sentence Structure Adjustments: {sentence_structure_count}")
    print(f"Paragraph Structure Adjustments: {paragraph_structure_count}")
    print(f"Punctuation Adjustments: {punctuation_count}")
    print(f"Voice Adjustments: {voice_count}")
    print(
        f"Total Adjustments: {word_choice_count + sentence_structure_count + paragraph_structure_count + punctuation_count + voice_count}"
    )


if __name__ == "__main__":
    demo_style_adjuster()
