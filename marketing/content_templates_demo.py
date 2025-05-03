"""
Demo script for the Content Templates module.

This script demonstrates how to use the various content templates
to create marketing content for different channels.
"""

import time

from user_personas import PersonaCreator


def main():
    from content_templates import (
    BlogPostTemplate,
    EmailNewsletterTemplate,
    LandingPageTemplate,
    SocialMediaTemplate,
    VideoScriptTemplate,
)
():
    """Main function to demonstrate the Content Templates module."""
    print("=" * 80)
    print("Content Templates Module Demo")
    print("=" * 80)

# Create a sample user persona
    persona_creator = PersonaCreator()
    persona = persona_creator.create_persona(
        name="Professional YouTuber",
        description="Professional content creator on YouTube",
        pain_points=[
            "time-consuming script writing",
            "maintaining viewer engagement",
            "content planning",
        ],
        goals=["increase video quality", "save time", "grow audience"],
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

print(f"\nCreated sample persona: {persona['name']}")
    print(f"Pain points: {', '.join(persona['pain_points'])}")
    print(f"Goals: {', '.join(persona['goals'])}")

# Define a sample product/service
    product_name = "AI Script Assistant"
    key_points = [
        "Generate video script outlines in seconds",
        "Optimize scripts for viewer engagement",
        "Maintain consistent brand voice across videos",
    ]
    call_to_action = "Sign up for a free trial at aiscriptassistant.com"

print(f"\nSample product: {product_name}")
    print(f"Key points: {', '.join(key_points)}")

# Demo 1: Blog Post Template
    print("\n" + "-" * 40)
    print("DEMO 1: BLOG POST TEMPLATE")
    print("-" * 40)

blog_post = BlogPostTemplate(
        title="How to Save 5 Hours a Week on YouTube Script Writing",
        target_persona=persona,
        key_points=key_points,
        call_to_action=call_to_action,
        target_word_count=1500,
        include_images=True,
        seo_keywords=["youtube script writing", "content creation", "AI for YouTubers"],
    )

blog_outline = blog_post.generate_outline()
    print(f"Blog Post Title: {blog_outline['title']}")
    print(f"Estimated Length: {blog_outline['estimated_length']}")
    print(f"Estimated Reading Time: {blog_outline['estimated_reading_time']}")

print("\nBlog Post Sections:")
    for section in blog_outline["sections"]:
        print(f"- {section['title']}")

print("\nHeadline Variations:")
    for headline in blog_post.generate_headline_variations(3):
        print(f"- {headline}")

# Demo 2: Social Media Template
    print("\n" + "-" * 40)
    print("DEMO 2: SOCIAL MEDIA TEMPLATE")
    print("-" * 40)

social_media = SocialMediaTemplate(
        title="AI Script Assistant for YouTubers",
        target_persona=persona,
        key_points=key_points,
        platforms=["twitter", "linkedin", "instagram"],
        call_to_action="Click the link in bio to start your free trial",
        hashtags=["ContentCreation", "YouTubers", "AItools"],
    )

social_outline = social_media.generate_outline()
    print(f"Social Media Post for: {', '.join(social_outline['platforms'])}")

print("\nTwitter Post:")
    twitter_post = social_outline["platform_specific_posts"].get("twitter", {})
    if twitter_post:
        print(f"Content: {twitter_post['post_text']}")
        print(f"Character Count: {twitter_post['estimated_length']}")

print("\nLinkedIn Post:")
    linkedin_post = social_outline["platform_specific_posts"].get("linkedin", {})
    if linkedin_post:
        print(f"Content Preview: {linkedin_post['post_text'][:100]}...")

print("\nRecommended Hashtags:")
    for hashtag in social_media.generate_hashtag_recommendations(5):
        print(f"- #{hashtag}")

# Demo 3: Email Newsletter Template
    print("\n" + "-" * 40)
    print("DEMO 3: EMAIL NEWSLETTER TEMPLATE")
    print("-" * 40)

email_newsletter = EmailNewsletterTemplate(
        title="Revolutionize Your YouTube Workflow",
        target_persona=persona,
        key_points=key_points,
        subject_line="5 Ways to Save Time on YouTube Script Writing",
        call_to_action=call_to_action,
        newsletter_type="educational",
        sender_name="AI Script Assistant Team",
        sender_email="hello@aiscriptassistant.com",
    )

email_outline = email_newsletter.generate_outline()
    print(f"Email Subject Line: {email_outline['subject_line']}")
    print(f"Newsletter Type: {email_outline['newsletter_type']}")

print("\nEmail Sections:")
    for section in email_outline["sections"]:
        print(f"- {section['title']}")

print("\nSubject Line Variations:")
    for subject in email_newsletter.generate_subject_line_variations(3):
        print(f"- {subject}")

# Demo 4: Video Script Template
    print("\n" + "-" * 40)
    print("DEMO 4: VIDEO SCRIPT TEMPLATE")
    print("-" * 40)

video_script = VideoScriptTemplate(
        title="AI Script Assistant Demo",
        target_persona=persona,
        key_points=key_points,
        call_to_action="Subscribe and hit the notification bell",
        video_length=5,  # 5 minutes
        video_type="tutorial",
        include_b_roll=True,
    )

script_outline = video_script.generate_outline()
    print(f"Video Title: {script_outline['title']}")
    print(f"Video Length: {script_outline['video_length']}")
    print(f"Target Word Count: {script_outline['target_word_count']} words")

print("\nScript Sections:")
    for section in script_outline["script_sections"]:
        print(f"- {section['title']} ({section['duration']})")

# Demo 5: Landing Page Template
    print("\n" + "-" * 40)
    print("DEMO 5: LANDING PAGE TEMPLATE")
    print("-" * 40)

landing_page = LandingPageTemplate(
        title="AI Script Assistant",
        target_persona=persona,
        key_points=key_points,
        call_to_action="Start Your Free 14-Day Trial",
        unique_selling_proposition="Write better YouTube scripts in half the time",
        features=[
            {
                "name": "AI-Powered Outline Generator",
                "description": "Create video outlines in seconds",
            },
            {
                "name": "Engagement Optimizer",
                "description": "Get suggestions to boost viewer retention",
            },
            {
                "name": "Brand Voice Consistency",
                "description": "Maintain your unique style across all videos",
            },
        ],
        testimonials=[
            {
                "name": "Jane Smith",
                "title": "YouTuber with 500K subscribers",
                "text": "AI Script Assistant cut my writing time in half!",
            }
        ],
    )

landing_outline = landing_page.generate_outline()
    print(f"Landing Page Title: {landing_outline['title']}")
    print(f"USP: {landing_outline['unique_selling_proposition']}")

print("\nLanding Page Sections:")
    for section in landing_outline["sections"]:
        print(f"- {section['title']}")

# Print conclusion
    print("\n" + "=" * 80)
    print("Demo Complete")
    print("=" * 80)
    print(
        "\nThe Content Templates module provides templates for creating various types of marketing content,"
    )
    print(
        "including blog posts, social media posts, email newsletters, video scripts, landing pages,"
    )
    print("product descriptions, case studies, and testimonials.")
    print(
        "\nEach template includes structure, tone and style guidelines, call-to-action recommendations,"
    )
    print("and optimization tips specific to the content type.")


if __name__ == "__main__":
    main()