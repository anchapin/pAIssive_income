"""
Demo script for the content optimization module.

This script demonstrates how to use the content optimization tools to analyze
and optimize marketing content.
"""

import time


from marketing.content_generators import BlogPostGenerator
from marketing.content_optimization import KeywordAnalyzer, ReadabilityAnalyzer
from marketing.content_templates import BlogPostTemplate
from marketing.tone_analyzer import ToneAnalyzer
from marketing.user_personas import PersonaCreator


def demo_keyword_analyzer():
    ():
    """Demonstrate the KeywordAnalyzer."""
    print("\n" + "=" * 80)
    print("KEYWORD ANALYZER DEMO")
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

print("\nGenerated Blog Post:")
    print(f"Title: {content['title']}")
    print(f"Meta Description: {content['meta_description']}")
    print(f"Introduction: {content['introduction'][:200]}...")

# Create a keyword analyzer
    keywords = ["YouTube script writing", "AI", "content creators", "save time"]
    analyzer = KeywordAnalyzer(content, keywords)

# Analyze content
    results = analyzer.analyze()

print("\nKeyword Analysis Results:")
    print(f"Overall SEO Score: {results['overall_score']:.2f}")

print("\nKeyword Density:")
    for keyword, data in results["keyword_density"]["keywords"].items():
        print(
            f"- '{keyword}': {data['count']} occurrences, {data['density']:.2%} density, Optimal: {data['is_optimal']}"
        )

print("\nKeyword Placement:")
    for keyword, data in results["keyword_placement"].items():
        print(f"- '{keyword}':")
        print(f"  - In Title: {data['in_title']}")
        print(f"  - In Headings: {data['in_headings']}")
        print(f"  - In First Paragraph: {data['in_first_paragraph']}")
        print(f"  - In Meta Description: {data['in_meta_description']}")
        print(f"  - In URL: {data['in_url']}")
        print(f"  - Placement Score: {data['score']:.2f}")

print("\nRecommendations:")
    for recommendation in results["recommendations"]:
        print(f"- [{recommendation['severity'].upper()}] {recommendation['message']}")
        print(f"  Suggestion: {recommendation['suggestion']}")


def demo_readability_analyzer():
    """Demonstrate the ReadabilityAnalyzer."""
    print("\n" + "=" * 80)
    print("READABILITY ANALYZER DEMO")
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

print("\nGenerated Blog Post:")
    print(f"Title: {content['title']}")
    print(f"Introduction: {content['introduction'][:200]}...")

# Create a readability analyzer
    analyzer = ReadabilityAnalyzer(content)

# Analyze content
    results = analyzer.analyze()

print("\nReadability Analysis Results:")
    print(f"Overall Readability Score: {results['overall_score']:.2f}")

print("\nText Statistics:")
    stats = results["text_statistics"]
    print(f"- Sentences: {stats['num_sentences']}")
    print(f"- Words: {stats['num_words']}")
    print(f"- Paragraphs: {stats['num_paragraphs']}")
    print(f"- Average Words per Sentence: {stats['avg_words_per_sentence']:.1f}")
    print(f"- Average Words per Paragraph: {stats['avg_words_per_paragraph']:.1f}")
    print(f"- Complex Word Percentage: {stats['complex_word_percentage']:.1%}")

print("\nReadability Scores:")
    scores = results["readability_scores"]
    print(
        f"- Flesch Reading Ease: {scores['flesch_reading_ease']['score']:.1f} ({scores['flesch_reading_ease']['interpretation']})"
    )
    print(
        f"- Flesch-Kincaid Grade Level: {scores['flesch_kincaid_grade']['score']:.1f}"
    )
    print(f"- SMOG Index: {scores['smog_index']['score']:.1f}")
    print(f"- Coleman-Liau Index: {scores['coleman_liau_index']['score']:.1f}")
    print(
        f"- Automated Readability Index: {scores['automated_readability_index']['score']:.1f}"
    )
    print(f"- Gunning Fog Index: {scores['gunning_fog_index']['score']:.1f}")
    print(f"- Average Grade Level: {scores['grade_level']:.1f}")
    print(f"- Reading Level: {scores['reading_level']}")

print("\nSentence Analysis:")
    sentence = results["sentence_analysis"]["sentence_length"]
    print(
        f"- Sentence Length: Min={sentence['min']}, Max={sentence['max']}, Avg={sentence['avg']:.1f}"
    )
    print(
        f"- Short Sentences: {sentence['short_count']} ({sentence['short_percentage']:.1%})"
    )
    print(
        f"- Long Sentences: {sentence['long_count']} ({sentence['long_percentage']:.1%})"
    )
    print(
        f"- Optimal Sentences: {sentence['optimal_count']} ({sentence['optimal_percentage']:.1%})"
    )

print("\nParagraph Analysis:")
    paragraph = results["paragraph_analysis"]["paragraph_length"]
    print(
        f"- Paragraph Length: Min={paragraph['min']}, Max={paragraph['max']}, Avg={paragraph['avg']:.1f}"
    )
    print(
        f"- Short Paragraphs: {paragraph['short_count']} ({paragraph['short_percentage']:.1%})"
    )
    print(
        f"- Long Paragraphs: {paragraph['long_count']} ({paragraph['long_percentage']:.1%})"
    )
    print(
        f"- Optimal Paragraphs: {paragraph['optimal_count']} ({paragraph['optimal_percentage']:.1%})"
    )

print("\nWriting Style Analysis:")
    passive = results["style_analysis"]["passive_voice"]
    print(
        f"- Passive Voice: {passive['passive_count']} instances ({passive['passive_percentage']:.1%})"
    )

adverbs = results["style_analysis"]["adverb_usage"]
    print(
        f"- Adverbs: {adverbs['adverb_count']} instances ({adverbs['adverb_percentage']:.1%})"
    )

complex_words = results["style_analysis"]["complex_words"]
    print(
        f"- Complex Words: {complex_words['complex_word_count']} instances ({complex_words['complex_word_percentage']:.1%})"
    )

print("\nRecommendations:")
    for recommendation in results["recommendations"]:
        print(f"- [{recommendation['severity'].upper()}] {recommendation['message']}")
        print(f"  Suggestion: {recommendation['suggestion']}")


def demo_tone_analyzer():
    """Demonstrate the ToneAnalyzer."""
    print("\n" + "=" * 80)
    print("TONE ANALYZER DEMO")
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

print("\nGenerated Blog Post:")
    print(f"Title: {content['title']}")
    print(f"Introduction: {content['introduction'][:200]}...")

# Create a tone analyzer
    analyzer = ToneAnalyzer(content, target_tone="conversational")

# Analyze content
    results = analyzer.analyze()

print("\nTone Analysis Results:")
    print(f"Overall Tone Score: {results['overall_score']:.2f}")

print("\nTone Scores:")
    for tone, data in results["tone_analysis"]["tone_scores"].items():
        print(
            f"- {tone}: {data['score']:.2f}"
            + (" (target)" if data["is_target"] else "")
        )

print(
        f"\nDominant Tone: {results['tone_analysis']['dominant_tone']} ({results['tone_analysis']['dominant_tone_score']:.2f})"
    )
    print(
        f"Target Tone: {results['tone_analysis']['target_tone']} ({results['tone_analysis']['target_tone_score']:.2f})"
    )
    print(f"Tone Consistency: {results['tone_analysis']['consistency']:.2f}")
    print(f"Is Consistent: {results['tone_analysis']['is_consistent']}")

print("\nSentiment Analysis:")
    for sentiment, data in results["sentiment_analysis"]["sentiment_scores"].items():
        print(
            f"- {sentiment}: {data['score']:.2f}"
            + (" (target)" if data["is_target"] else "")
        )

print(
        f"\nDominant Sentiment: {results['sentiment_analysis']['dominant_sentiment']} ({results['sentiment_analysis']['dominant_sentiment_score']:.2f})"
    )
    print(
        f"Target Sentiment: {results['sentiment_analysis']['target_sentiment']} ({results['sentiment_analysis']['target_sentiment_score']:.2f})"
    )
    print(f"Sentiment Consistency: {results['sentiment_analysis']['consistency']:.2f}")
    print(f"Is Consistent: {results['sentiment_analysis']['is_consistent']}")

print("\nStyle Analysis:")
    print(
        f"- Sentence Length Variety: {results['style_analysis']['sentence_length_variety']['score']:.2f}"
    )
    print(
        f"- Vocabulary Variety: {results['style_analysis']['vocabulary_variety']['score']:.2f}"
    )
    print(
        f"- Punctuation Density: {results['style_analysis']['punctuation']['density']:.2f}"
    )

print("\nRecommendations:")
    for recommendation in results["recommendations"]:
        print(f"- [{recommendation['severity'].upper()}] {recommendation['message']}")
        print(f"  Suggestion: {recommendation['suggestion']}")


if __name__ == "__main__":
    demo_keyword_analyzer()
    demo_readability_analyzer()
    demo_tone_analyzer()