"""
Demo script for the content generators module.

This script demonstrates how to use the content generators to create
blog posts, product descriptions, and case studies.
"""

from marketing.content_generators import (
    BlogPostGenerator,
    CaseStudyGenerator,
    ProductDescriptionGenerator,
)
from marketing.content_templates import (
    BlogPostTemplate,
    CaseStudyTemplate,
    ProductDescriptionTemplate,
)
from marketing.user_personas import PersonaCreator


def create_demo_persona():
    """Create a demo persona for the examples."""
    persona_creator = PersonaCreator()

    return persona_creator.create_persona(
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


def demo_blog_post_generator():
    """Demonstrate the BlogPostGenerator."""
    print("\n" + "=" * 80)
    print("BLOG POST GENERATOR DEMO")
    print("=" * 80)

    # Create a persona
    persona = create_demo_persona()

    # Create a blog post template
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

    # Print the generated content
    print("\nGenerated Blog Post:")
    print(f"Title: {content['title']}")
    print(f"Meta Description: {content['meta_description']}")
    print("\nIntroduction:")
    print(content["introduction"])

    print("\nSections:")
    for section in content["sections"]:
        print(f"\n{section['title']}:")
        print(section["content"][:200] + "...")  # Print first 200 chars of each section

    print("\nConclusion:")
    print(content["conclusion"])

    print("\nCall to Action:")
    print(content["call_to_action"])

    print("\nTags:", ", ".join(content["tags"]))
    print("Categories:", ", ".join(content["categories"]))

    print("\nSEO Data:")
    print(f"Focus Keyword: {content['seo_data']['focus_keyword']}")
    print(f"Secondary Keywords: {', '.join(content['seo_data']['secondary_keywords'])}")
    print(f"Slug: {content['seo_data']['slug']}")


def demo_product_description_generator():
    """Demonstrate the ProductDescriptionGenerator."""
    print("\n" + "=" * 80)
    print("PRODUCT DESCRIPTION GENERATOR DEMO")
    print("=" * 80)

    # Create a persona
    persona = create_demo_persona()

    # Create a product description template
    template = ProductDescriptionTemplate(
        title="AI Script Assistant Pro",
        target_persona=persona,
        key_points=[
            "AI-powered script generation",
            "Time-saving templates",
            "SEO optimization for YouTube",
            "Engagement analytics",
        ],
        tone="professional",
        call_to_action="Get started with a 14-day free trial",
        product_features=[
            {
                "name": "AI Script Generator",
                "description": "Generate complete scripts or outlines based on your topic",
            },
            {
                "name": "Template Library",
                "description": "Access 50+ templates for different video types",
            },
            {
                "name": "SEO Keyword Tool",
                "description": "Find the best keywords to rank your videos",
            },
            {
                "name": "Engagement Predictor",
                "description": "AI analysis of script engagement potential",
            },
        ],
        product_specs={
            "platforms": "Web, iOS, Android",
            "languages": "English, Spanish, French, German",
            "integration": "YouTube, Vimeo, TikTok",
            "support": "24/7 chat and email support",
        },
        product_type="software",
        include_pricing=True,
    )

    # Create a product description generator
    generator = ProductDescriptionGenerator(template)

    # Generate content
    content = generator.generate_content()

    # Print the generated content
    print("\nGenerated Product Description:")
    print(f"Product Name: {content['product_name']}")
    print(f"Tagline: {content['tagline']}")

    print("\nOverview:")
    print(content["overview"])

    print("\nFeatures:")
    for feature in content["features"]:
        print(f"- {feature['name']}: {feature['description']}")

    print("\nBenefits:")
    for benefit in content["benefits"]:
        print(f"- {benefit['name']}: {benefit['description']}")

    print("\nSpecifications:")
    for key, value in content["specifications"].items():
        print(f"- {key}: {value}")

    print("\nPricing:")
    print(f"Regular Price: ${content['pricing']['regular_price']}")
    print(f"Sale Price: ${content['pricing']['sale_price']}")
    print(
        f"Subscription: ${content['pricing']['subscription_price']}/{content['pricing']['subscription_interval']}"
    )

    print("\nCall to Action:")
    print(content["call_to_action"])

    print("\nSEO Data:")
    print(f"Meta Title: {content['seo_data']['meta_title']}")
    print(f"Meta Description: {content['seo_data']['meta_description']}")
    print(f"Focus Keyword: {content['seo_data']['focus_keyword']}")
    print(f"Secondary Keywords: {', '.join(content['seo_data']['secondary_keywords'])}")
    print(f"Slug: {content['seo_data']['slug']}")


def demo_case_study_generator():
    """Demonstrate the CaseStudyGenerator."""
    print("\n" + "=" * 80)
    print("CASE STUDY GENERATOR DEMO")
    print("=" * 80)

    # Create a persona
    persona = create_demo_persona()

    # Create a case study template
    template = CaseStudyTemplate(
        title="How VideoStar Increased Production Speed by 40% with AI Script Assistant Pro",
        target_persona=persona,
        key_points=[
            "Implementing AI for script creation",
            "Streamlining the content production workflow",
            "Training team members on the new system",
            "Measuring and optimizing results",
        ],
        tone="professional",
        call_to_action="Book a demo to see how we can help your content creation team",
        client_name="VideoStar Productions",
        client_industry="Video Production",
        challenge="VideoStar Productions was struggling to keep up with client demands, with script creation being a major bottleneck in their production process.",
        solution="We implemented AI Script Assistant Pro to automate and streamline their script creation process, integrated it with their existing workflow, and provided comprehensive training to their team.",
        results=[
            "Reduced script creation time by 60%",
            "Increased overall production speed by 40%",
            "Improved client satisfaction scores by 35%",
            "Enabled the team to take on 25% more projects",
        ],
        include_testimonial=True,
    )

    # Create a case study generator
    generator = CaseStudyGenerator(template)

    # Generate content
    content = generator.generate_content()

    # Print the generated content
    print("\nGenerated Case Study:")
    print(f"Title: {content['title']}")

    print("\nClient Info:")
    print(f"Name: {content['client_info']['name']}")
    print(f"Industry: {content['client_info']['industry']}")

    print("\nExecutive Summary:")
    print(content["executive_summary"][:300] + "...")  # Print first 300 chars

    print("\nChallenge:")
    print(content["challenge"][:300] + "...")  # Print first 300 chars

    print("\nSolution:")
    print(content["solution"][:300] + "...")  # Print first 300 chars

    print("\nResults:")
    print(content["results"][:300] + "...")  # Print first 300 chars

    print("\nTestimonial:")
    print(
        content["testimonial"][:300] + "..."
        if content["testimonial"]
        else "No testimonial included"
    )  # Print first 300 chars

    print("\nConclusion:")
    print(content["conclusion"][:300] + "...")  # Print first 300 chars

    print("\nCall to Action:")
    print(content["call_to_action"])

    print("\nRelated Case Studies:")
    for case_study in content["related_case_studies"]:
        print(f"- {case_study['title']}")

    print("\nSEO Data:")
    print(f"Meta Title: {content['seo_data']['meta_title']}")
    print(f"Meta Description: {content['seo_data']['meta_description']}")
    print(f"Focus Keyword: {content['seo_data']['focus_keyword']}")
    print(f"Secondary Keywords: {', '.join(content['seo_data']['secondary_keywords'])}")
    print(f"Slug: {content['seo_data']['slug']}")


if __name__ == "__main__":
    demo_blog_post_generator()
    demo_product_description_generator()
    demo_case_study_generator()
