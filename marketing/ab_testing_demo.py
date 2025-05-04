"""
"""
Demo script for the A/B testing module.
Demo script for the A/B testing module.


This script demonstrates how to use the A/B testing tools to create and analyze
This script demonstrates how to use the A/B testing tools to create and analyze
A/B tests for various marketing assets.
A/B tests for various marketing assets.
"""
"""


import time
import time


from marketing.ab_testing import ABTesting
from marketing.ab_testing import ABTesting
from marketing.user_personas import PersonaCreator
from marketing.user_personas import PersonaCreator




def demo_email_subject_testing():
    def demo_email_subject_testing():
    ():
    ():
    """Demonstrate A/B testing for email subject lines."""
    print("\n=== A/B Testing Demo: Email Subject Lines ===\n")

    # Create an A/B testing instance
    ab_testing = ABTesting()

    # Create variants for testing
    variants = [
    {
    "name": "Problem-focused",
    "is_control": True,
    "content": {
    "subject_line": "Struggling with low conversion rates?",
    "preview_text": "Learn how to improve your marketing campaigns",
    },
    },
    {
    "name": "Benefit-focused",
    "is_control": False,
    "content": {
    "subject_line": "Boost your conversion rates by 30%",
    "preview_text": "Proven strategies to improve your marketing campaigns",
    },
    },
    {
    "name": "Curiosity-focused",
    "is_control": False,
    "content": {
    "subject_line": "The surprising truth about conversion rates",
    "preview_text": "This one change could transform your marketing",
    },
    },
    ]

    # Create an A/B test
    test = ab_testing.create_test(
    name="Email Subject Line Test",
    description="Testing different approaches to email subject lines",
    content_type="email",
    test_type="a_b",
    variants=variants,
    )

    print(f"Created test: {test['name']} (ID: {test['id']})")
    print(f"Test type: {test['test_type']}")
    print(f"Content type: {test['content_type']}")
    print(f"Number of variants: {len(test['variants'])}")

    print("\nVariants:")
    for variant in test["variants"]:
    print(f"- {variant['name']}: {variant['content']['subject_line']}")

    # Simulate interactions with the variants
    test_id = test["id"]
    control_id = next(v["id"] for v in test["variants"] if v["is_control"])
    variant1_id = next(
    v["id"] for v in test["variants"] if v["name"] == "Benefit-focused"
    )
    variant2_id = next(
    v["id"] for v in test["variants"] if v["name"] == "Curiosity-focused"
    )

    # Control variant: 1000 impressions, 150 clicks, 15 conversions
    for _ in range(1000):
    ab_testing.record_interaction(test_id, control_id, "impression")
    for _ in range(150):
    ab_testing.record_interaction(test_id, control_id, "click")
    for _ in range(15):
    ab_testing.record_interaction(test_id, control_id, "conversion")

    # Benefit variant: 1000 impressions, 200 clicks, 24 conversions
    for _ in range(1000):
    ab_testing.record_interaction(test_id, variant1_id, "impression")
    for _ in range(200):
    ab_testing.record_interaction(test_id, variant1_id, "click")
    for _ in range(24):
    ab_testing.record_interaction(test_id, variant1_id, "conversion")

    # Curiosity variant: 1000 impressions, 250 clicks, 20 conversions
    for _ in range(1000):
    ab_testing.record_interaction(test_id, variant2_id, "impression")
    for _ in range(250):
    ab_testing.record_interaction(test_id, variant2_id, "click")
    for _ in range(20):
    ab_testing.record_interaction(test_id, variant2_id, "conversion")

    # Get test results
    results = ab_testing.get_results(test_id)

    print("\nTest Results:")
    print(f"Total impressions: {results['total_impressions']}")
    print(f"Total clicks: {results['total_clicks']}")
    print(f"Overall click-through rate: {results['overall_click_through_rate']:.2%}")

    print("\nVariant Results:")
    for variant in results["variants"]:
    print(f"- {variant['name']}:")
    print(f"  Click-through rate: {variant['metrics']['click_through_rate']:.2%}")
    print(f"  Conversion rate: {variant['metrics']['conversion_rate']:.2%}")
    if "ctr_lift" in variant:
    print(f"  CTR lift vs control: {variant['ctr_lift']:.2f}%")
    if "conversion_lift" in variant:
    print(f"  Conversion lift vs control: {variant['conversion_lift']:.2f}%")

    # Analyze test for statistical significance
    analysis = ab_testing.analyze_test(test_id)

    print("\nTest Analysis:")
    print(f"Confidence level: {analysis['confidence_level']:.0%}")
    print(f"Has significant results: {analysis['has_significant_results']}")

    if analysis["recommended_winner"]:
    winner_id = analysis["recommended_winner"]
    winner = next(v for v in analysis["variants"] if v["id"] == winner_id)
    print(f"Recommended winner: {winner['name']}")
    else:
    print("No clear winner yet")

    print("\nVariant Analysis:")
    for variant in analysis["variants"]:
    if variant["is_control"]:
    print(f"- {variant['name']} (Control)")
    else:
    print(f"- {variant['name']}:")
    ctr_p_value = variant.get("ctr_p_value", "N/A")
    if isinstance(ctr_p_value, (int, float)):
    print(f"  CTR p-value: {ctr_p_value:.4f}")
    else:
    print(f"  CTR p-value: {ctr_p_value}")
    print(f"  CTR significant: {variant.get('ctr_is_significant', 'N/A')}")
    print(
    f"  Conversion p-value: {variant.get('conversion_p_value', 'N/A'):.4f}"
    )
    print(
    f"  Conversion significant: {variant.get('conversion_is_significant', 'N/A')}"
    )
    print(
    f"  Better than control: {variant.get('is_better_than_control', 'N/A')}"
    )

    # End the test
    end_result = ab_testing.end_test(test_id)

    print("\nTest ended:")
    print(f"Status: {end_result['status']}")
    print(f"Winning variant: {end_result['winning_variant_id'] or 'None'}")


    def demo_landing_page_testing():
    """Demonstrate A/B testing for landing pages."""
    print("\n=== A/B Testing Demo: Landing Page Components ===\n")

    # Create an A/B testing instance
    ab_testing = ABTesting()

    # Create a persona creator to get recommendations
    persona_creator = PersonaCreator()

    # Create a sample persona
    persona = persona_creator.create_persona(
    name="SaaS Manager",
    description="Product manager at a SaaS company",
    demographics={
    "age_range": "30-45",
    "gender": "any",
    "education": "college degree or higher",
    "income": "above average",
    "location": "urban areas",
    },
    pain_points=[
    "Not enough time to analyze marketing data",
    "Difficulty proving marketing ROI",
    "Trouble prioritizing marketing activities",
    ],
    goals=[
    "Increase marketing efficiency",
    "Generate more qualified leads",
    "Demonstrate marketing impact on revenue",
    ],
    )

    # Get test recommendations
    recommendations = ab_testing.generate_test_recommendation("landing_page", persona)

    print("Test Recommendations:")
    print(f"Content type: {recommendations['content_type']}")
    print(f"Suggested sample size: {recommendations['suggested_sample_size']} visitors")
    print(f"Suggested run time: {recommendations['suggested_run_time']}")
    print(f"Expected improvement: {recommendations['expected_improvement']}")

    print("\nRecommended test elements:")
    for element in recommendations["test_elements"]:
    print(f"- {element['element']} (Importance: {element['importance']})")
    print(f"  Reason: {element['reason']}")

    # Create variants for testing
    variants = [
    {
    "name": "Original",
    "is_control": True,
    "content": {
    "headline": "Marketing Analytics Platform",
    "hero_image": "dashboard.jpg",
    "call_to_action": "Start Free Trial",
    },
    },
    {
    "name": "Problem-focused",
    "is_control": False,
    "content": {
    "headline": "Stop Wasting Time on Manual Marketing Analysis",
    "hero_image": "frustrated_marketer.jpg",
    "call_to_action": "Solve My Analytics Problem",
    },
    },
    {
    "name": "Benefit-focused",
    "is_control": False,
    "content": {
    "headline": "Increase Marketing ROI by 40%",
    "hero_image": "success_graph.jpg",
    "call_to_action": "Boost My Marketing Results",
    },
    },
    ]

    # Create an A/B test
    test = ab_testing.create_test(
    name="Landing Page Headline and CTA Test",
    description="Testing different headline and CTA approaches",
    content_type="landing_page",
    test_type="multivariate",
    variants=variants,
    )

    print(f"\nCreated test: {test['name']} (ID: {test['id']})")

    # Note: In a real implementation, we would track actual user interactions
    # rather than simulating them


    def demo_test_recommendation():
    """Demonstrate generating test recommendations for different content types."""
    print("\n=== A/B Testing Demo: Test Recommendations ===\n")

    # Create an A/B testing instance
    ab_testing = ABTesting()

    # Create a persona creator
    persona_creator = PersonaCreator()

    # Create a sample persona
    persona = persona_creator.create_persona(
    name="E-commerce Owner",
    description="Owner of a medium-sized e-commerce store",
    demographics={
    "age_range": "25-45",
    "gender": "any",
    "education": "varied",
    "income": "above average",
    "location": "various",
    },
    pain_points=[
    "Low conversion rates",
    "High cart abandonment",
    "Difficulty standing out from competitors",
    ],
    goals=[
    "Increase revenue",
    "Improve customer loyalty",
    "Reduce marketing costs",
    ],
    )

    # Get test recommendations for different content types
    content_types = ["email", "landing_page", "ad"]

    for content_type in content_types:
    recommendations = ab_testing.generate_test_recommendation(content_type, persona)

    print(f"\n{content_type.capitalize()} Testing Recommendations:")
    print(f"Suggested sample size: {recommendations['suggested_sample_size']}")
    print(f"Suggested run time: {recommendations['suggested_run_time']}")

    print("\nTop test elements:")
    top_elements = sorted(
    recommendations["test_elements"],
    key=lambda x: {"high": 3, "medium": 2, "low": 1}.get(x["importance"], 0),
    reverse=True,
    )[:3]

    for element in top_elements:
    print(f"- {element['element']} ({element['importance']} importance)")

    if recommendations["test_variants"]:
    print(
    "\nSample variants for",
    recommendations["test_variants"][0]["element"],
    ":",
    )

    for variant in recommendations["test_variants"][0]["variants"][:2]:
    print(f"- {variant['type']}: \"{variant['value']}\"")


    if __name__ == "__main__":
    demo_email_subject_testing()
    demo_landing_page_testing()
    demo_test_recommendation()