"""
Content Templates module for the pAIssive Income project.
Provides templates for creating marketing content.
"""

import time


import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .errors import ContentTemplateError, ValidationError, handle_exception



# Set up logging
logger = logging.getLogger(__name__)


class ContentTemplate:
    """
    Base class for all content templates.
    """

def __init__(
        self,
        name: str = "",
        description: str = "",
        title: str = "",
        target_persona: Optional[Dict[str, Any]] = None,
        key_points: Optional[List[str]] = None,
        tone: Optional[str] = "professional",
        call_to_action: Optional[str] = None,
    ):
        """
        Initialize a content template.

Args:
            name: Name of the template
            description: Description of the template
            title: Title of the content
            target_persona: The target user persona for this content
            key_points: List of key points to cover in the content
            tone: Optional tone for the content (e.g., "professional", "casual", "authoritative")
            call_to_action: Optional call to action for the content
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.title = title
        self.target_persona = target_persona or {
            "name": "Generic User",
            "pain_points": ["No specific pain points"],
            "goals": ["No specific goals"],
            "behavior": {"tech_savvy": "medium"},
        }
        self.key_points = key_points or []
        self.tone = tone
        self.call_to_action = call_to_action
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.content_type = "generic"
        self.sections = []

def generate_outline(self) -> Dict[str, Any]:
        """
        Generate an outline for the content.

Returns:
            Dictionary with outline details

Raises:
            ValidationError: If the template is invalid
            ContentTemplateError: If there's an issue generating the outline
        """
        try:
            # Validate required fields
            if not self.title:
                raise ValidationError(
                    message="Title is required to generate an outline",
                    field="title",
                    validation_errors=[
                        {"field": "title", "error": "Title is required"}
                    ],
                )

if not self.key_points or len(self.key_points) == 0:
                raise ValidationError(
                    message="Key points are required to generate an outline",
                    field="key_points",
                    validation_errors=[
                        {
                            "field": "key_points",
                            "error": "At least one key point is required",
                        }
                    ],
                )

sections = []

# Add introduction
            sections.append(
                {
                    "section_type": "introduction",
                    "title": "Introduction",
                    "description": f"Introduction to {self.title}",
                    "key_elements": [
                        "Hook to grab attention",
                        "Brief overview of the topic",
                        "Why this matters to the reader",
                    ],
                }
            )

# Add sections for each key point
            for i, point in enumerate(self.key_points):
                sections.append(
                    {
                        "section_type": "body",
                        "title": f"Section {i+1}: {point}",
                        "description": f"Details about {point}",
                        "key_elements": [
                            "Explanation of the point",
                            "Supporting evidence or examples",
                            "Practical application",
                        ],
                    }
                )

# Add conclusion
            sections.append(
                {
                    "section_type": "conclusion",
                    "title": "Conclusion",
                    "description": "Summary and next steps",
                    "key_elements": [
                        "Recap of key points",
                        "Final thoughts",
                        (
                            "Call to action"
                            if self.call_to_action
                            else "Closing statement"
                        ),
                    ],
                }
            )

outline = {
                "id": self.id,
                "title": self.title,
                "content_type": self.content_type,
                "target_persona": self.target_persona["name"],
                "tone": self.tone,
                "sections": sections,
                "call_to_action": self.call_to_action,
                "estimated_length": f"{len(self.key_points) * 300 + 600} words",
                "created_at": self.created_at,
            }

logger.info(f"Generated outline for content: {self.title}")
                        return outline

except ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Handle unexpected errors
            handle_exception(
                e,
                error_class=ContentTemplateError,
                message=f"Failed to generate outline for content: {self.title}",
                template_type=self.content_type,
                reraise=True,
                log_level=logging.ERROR,
            )
                        return {}  # This line won't be reached due to reraise=True

def get_style_guidelines(self) -> Dict[str, Any]:
        """
        Get style guidelines for the content based on tone.

Returns:
            Dictionary with style guidelines
        """
        tone_guidelines = {
            "professional": {
                "language": "Formal, clear, and precise",
                "sentence_structure": "Mix of simple and complex sentences",
                "vocabulary": "Industry-specific terminology with explanations where needed",
                "perspective": "Third person or first person plural (we)",
                "examples": "Real-world, data-backed examples",
            },
            "casual": {
                "language": "Conversational and approachable",
                "sentence_structure": "Shorter, simpler sentences",
                "vocabulary": "Everyday language, minimal jargon",
                "perspective": "First or second person (I/you)",
                "examples": "Relatable, everyday examples",
            },
            "authoritative": {
                "language": "Confident and assertive",
                "sentence_structure": "Clear, direct sentences",
                "vocabulary": "Precise terminology demonstrating expertise",
                "perspective": "Third person or first person (I/we with authority)",
                "examples": "Research-backed examples and case studies",
            },
            "inspirational": {
                "language": "Uplifting and motivational",
                "sentence_structure": "Varied, with rhetorical questions and powerful statements",
                "vocabulary": "Emotionally resonant words",
                "perspective": "Mix of perspectives, often second person (you)",
                "examples": "Success stories and transformational examples",
            },
            "educational": {
                "language": "Clear and instructional",
                "sentence_structure": "Logical, step-by-step structure",
                "vocabulary": "Mix of basic and technical terms with explanations",
                "perspective": "Second person (you) or first person plural (we)",
                "examples": "Practical examples and demonstrations",
            },
        }

# Get guidelines for the specified tone, or default to professional
        guidelines = tone_guidelines.get(
            self.tone.lower(), tone_guidelines["professional"]
        )

# Add persona-specific guidelines
        persona_guidelines = {
            "target_audience": self.target_persona["name"],
            "pain_points_to_address": self.target_persona["pain_points"],
            "goals_to_emphasize": self.target_persona["goals"],
            "knowledge_level": self.target_persona["behavior"].get(
                "tech_savvy", "medium"
            ),
        }

            return {
            "tone_guidelines": guidelines,
            "persona_guidelines": persona_guidelines,
            "general_guidelines": {
                "clarity": "Prioritize clarity over complexity",
                "specificity": "Use specific examples rather than generalizations",
                "actionability": "Provide actionable insights and next steps",
                "engagement": "Use engaging elements like questions, stories, or surprising facts",
            },
        }

def get_seo_recommendations(self) -> Dict[str, Any]:
        """
        Get SEO recommendations for the content.

Returns:
            Dictionary with SEO recommendations
        """
        # Extract potential keywords from title and key points
        title_words = self.title.lower().split()
        key_point_words = []
        for point in self.key_points:
            key_point_words.extend(point.lower().split())

all_words = title_words + key_point_words

# Filter out common stop words (simplified version)
        stop_words = [
            "the",
            "and",
            "a",
            "an",
            "in",
            "on",
            "at",
            "to",
            "for",
            "with",
            "by",
            "of",
        ]
        potential_keywords = [word for word in all_words if word not in stop_words]

# Count occurrences to find most common words
        keyword_counts = {}
        for word in potential_keywords:
            if word in keyword_counts:
                keyword_counts[word] += 1
            else:
                keyword_counts[word] = 1

# Sort by count and get top keywords
        sorted_keywords = sorted(
            keyword_counts.items(), key=lambda x: x[1], reverse=True
        )
        top_keywords = [k for k, v in sorted_keywords[:5]]

# Generate keyword phrases
        keyword_phrases = []
        if len(title_words) > 2:
            keyword_phrases.append(" ".join(title_words))
        for point in self.key_points:
            point_words = point.lower().split()
            if len(point_words) > 2:
                keyword_phrases.append(" ".join(point_words[:3]))

            return {
            "primary_keyword": top_keywords[0] if top_keywords else "",
            "secondary_keywords": top_keywords[1:] if len(top_keywords) > 1 else [],
            "keyword_phrases": keyword_phrases[:3],
            "recommended_meta_title": self.title,
            "recommended_meta_description": f"{self.title}: Learn about {', '.join(self.key_points[:2])} and more.",
            "content_recommendations": [
                "Include primary keyword in title, first paragraph, and at least one heading",
                "Use secondary keywords throughout the content naturally",
                "Include at least one image with alt text containing a keyword",
                "Link to related content on your site",
                "Ensure content is at least 800 words for blog posts",
            ],
        }

def add_section(
        self,
        name: str = "",
        description: str = "",
        content_type: str = "text",
        placeholder: str = "",
        required: bool = False,
        section_type: str = "",
        title: str = "",
        content: str = "",
    ) -> Dict[str, Any]:
        """
        Add a section to the content template.

Args:
            name: Name of the section
            description: Description of the section
            content_type: Type of content (e.g., "text", "image", "video")
            placeholder: Placeholder text for the section
            required: Whether the section is required
            section_type: Type of section (e.g., "introduction", "body", "conclusion")
            title: Title of the section
            content: Optional content for the section

Returns:
            Dictionary with section details
        """
        section = {
            "id": str(uuid.uuid4()),
            "name": name or title,
            "description": description,
            "content_type": content_type,
            "placeholder": placeholder,
            "required": required,
            "section_type": section_type or content_type,
            "title": title or name,
            "content": content,
            "order": len(self.sections) + 1,
        }

self.sections.append(section)
        self.updated_at = datetime.now().isoformat()
                    return section

def generate_content(
        self,
        topic: str = "",
        target_audience: str = "",
        tone: str = "",
        keywords: List[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate content based on the template.

Args:
            topic: Topic of the content
            target_audience: Target audience for the content
            tone: Tone of the content
            keywords: Keywords for the content
            **kwargs: Additional keyword arguments

Returns:
            Dictionary with generated content

Raises:
            ValidationError: If the template is invalid
            ContentTemplateError: If there's an issue generating the content
        """
        try:
            # Update template properties if provided
            if topic:
                self.title = topic

if target_audience:
                self.target_persona["name"] = target_audience

if tone:
                self.tone = tone

# Generate outline first
            try:
                outline = self.generate_outline()
            except ValidationError as e:
                # Add more context to the validation error
                field = getattr(e, "field", None)
                validation_errors = getattr(e, "validation_errors", None)

raise ValidationError(
                    message=f"Cannot generate content: {e.message}",
                    field=field,
                    validation_errors=validation_errors,
                    original_exception=e,
                )

# Create content structure
            content = {
                "id": self.id,
                "template_id": self.id,
                "name": self.name,
                "description": self.description,
                "title": self.title,
                "topic": topic or self.title,
                "content_type": self.content_type,
                "target_persona": self.target_persona["name"],
                "target_audience": target_audience or self.target_persona["name"],
                "tone": self.tone,
                "sections": [],
                "call_to_action": self.call_to_action,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
            }

# Add keywords if provided
            if keywords:
                content["keywords"] = keywords

# Only use the custom sections added by the user
            content["sections"] = []
            for section in self.sections:
                # Create a copy of the section
                section_copy = section.copy()

# Add sample content if the section doesn't have any
                if not section_copy.get("content"):
                    if section_copy.get("name") == "Introduction":
                        section_copy["content"] = (
                            f"Introduction to {self.title}. This addresses the needs of {self.target_persona['name']}."
                        )
                    elif section_copy.get("name") == "Main Content":
                        section_copy["content"] = (
                            f"Main content about {self.title}. This is important for {self.target_persona['name']}."
                        )
                    elif section_copy.get("name") == "Conclusion":
                        section_copy["content"] = (
                            f"In conclusion, {self.title} is valuable for {self.target_persona['name']}."
                        )
                    else:
                        section_copy["content"] = (
                            f"Content about {section_copy.get('name', 'this topic')}."
                        )

content["sections"].append(section_copy)

# If no custom sections, use the outline sections
            if not content["sections"]:
                content["sections"] = outline["sections"]

# Update timestamp
            self.updated_at = datetime.now().isoformat()

logger.info(f"Generated content for: {self.title}")
                        return content

except ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Handle unexpected errors
            handle_exception(
                e,
                error_class=ContentTemplateError,
                message=f"Failed to generate content for: {self.title}",
                template_type=self.content_type,
                reraise=True,
                log_level=logging.ERROR,
            )
                        return {}  # This line won't be reached due to reraise=True

def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the content template.

Returns:
            Dictionary with template summary
        """
                    return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "title": self.title,
            "content_type": self.content_type,
            "target_persona": self.target_persona["name"],
            "key_points_count": len(self.key_points),
            "sections_count": len(self.sections),
            "tone": self.tone,
            "call_to_action": self.call_to_action,
            "created_at": self.created_at,
        }


class BlogPostTemplate(ContentTemplate):
    """
    Template for creating blog post content.
    """

def __init__(
        self,
        name: str = "",
        description: str = "",
        title: str = "",
        target_persona: Optional[Dict[str, Any]] = None,
        key_points: Optional[List[str]] = None,
        tone: Optional[str] = "professional",
        call_to_action: Optional[str] = None,
        target_word_count: Optional[int] = 1200,
        include_images: bool = True,
        seo_keywords: Optional[List[str]] = None,
    ):
        """
        Initialize a blog post template.

Args:
            name: Name of the template
            description: Description of the template
            title: Title of the blog post
            target_persona: The target user persona for this blog post
            key_points: List of key points to cover in the blog post
            tone: Optional tone for the blog post
            call_to_action: Optional call to action for the blog post
            target_word_count: Optional target word count for the blog post
            include_images: Whether to include image recommendations
            seo_keywords: Optional list of SEO keywords to target
        """
        super().__init__(
            name, description, title, target_persona, key_points, tone, call_to_action
        )
        self.content_type = "blog_post"
        self.target_word_count = target_word_count
        self.include_images = include_images
        self.seo_keywords = seo_keywords or []

# Add default sections
        if not self.sections:
            self.add_section(
                name="Title",
                description="The title of the blog post",
                content_type="text",
                placeholder="Enter a compelling title...",
                required=True,
            )

self.add_section(
                name="Meta Description",
                description="SEO meta description",
                content_type="text",
                placeholder="Enter a meta description (150-160 characters)...",
                required=True,
            )

self.add_section(
                name="Introduction",
                description="The introduction of the blog post",
                content_type="text",
                placeholder="Write an engaging introduction...",
                required=True,
            )

self.add_section(
                name="Main Content",
                description="The main content of the blog post",
                content_type="text",
                placeholder="Write the main content here...",
                required=True,
            )

self.add_section(
                name="Conclusion",
                description="The conclusion of the blog post",
                content_type="text",
                placeholder="Write a compelling conclusion...",
                required=True,
            )

self.add_section(
                name="Call to Action",
                description="The call to action for the blog post",
                content_type="text",
                placeholder="Enter a call to action...",
                required=False,
            )

def generate_outline(self) -> Dict[str, Any]:
        """
        Generate an outline for the blog post.

Returns:
            Dictionary with blog post outline details
        """
        # Get base outline from parent class  super().generate_outline()

# Add blog-specific elements
        outline["estimated_length"] = f"{self.target_word_count} words"
        outline["estimated_reading_time"] = f"{self.target_word_count // 200} minutes"

# Add image recommendations if enabled
        if self.include_images:
            image_recommendations = []
            image_recommendations.append(
                {
                    "description": "Featured image for the blog post",
                    "placement": "top",
                    "purpose": "Attract attention and convey the main topic",
                }
            )

# Add image for each key point
            for i, point in enumerate(self.key_points):
                image_recommendations.append(
                    {
                        "description": f"Image illustrating {point}",
                        "placement": f"Section {i+1}",
                        "purpose": "Visualize the concept and break up text",
                    }
                )

outline["image_recommendations"] = image_recommendations

# Add SEO recommendations
        if self.seo_keywords:
            outline["seo_keywords"] = self.seo_keywords

# Add blog-specific section recommendations
        blog_sections = []

# Add table of contents recommendation for longer posts
        if len(self.key_points) > 3 or self.target_word_count > 1500:
            blog_sections.append(
                {
                    "section_type": "table_of_contents",
                    "title": "Table of Contents",
                    "description": "Links to each section of the blog post",
                    "placement": "after introduction",
                }
            )

# Add FAQ section recommendation
        suggested_questions = [f"What is the best way to {self.title.lower()}?"]

if self.key_points:
            suggested_questions.append(
                f"How long does it take to {self.key_points[0].lower()}?"
            )
        else:
            suggested_questions.append(
                f"How long does it take to implement {self.title.lower()}?"
            )

if self.target_persona and self.target_persona.get("pain_points"):
            suggested_questions.append(
                f"What tools do I need for {self.target_persona['pain_points'][0]}?"
            )
        else:
            suggested_questions.append(
                f"What tools do I need for {self.title.lower()}?"
            )

blog_sections.append(
            {
                "section_type": "faq",
                "title": "Frequently Asked Questions",
                "description": "Common questions and answers about the topic",
                "placement": "before conclusion",
                "suggested_questions": suggested_questions,
            }
        )

outline["blog_specific_sections"] = blog_sections

            return outline

def generate_headline_variations(self, count: int = 5) -> List[str]:
        """
        Generate variations of the blog post headline.

Args:
            count: Number of variations to generate

Returns:
            List of headline variations
        """
        variations = [self.title]  # Start with the original title

# Generate variations based on common blog headline patterns
        patterns = [
            f"How to {self.title}",
            f"{self.title}: A Complete Guide",
            f"{len(self.key_points)} Ways to {self.title}",
            f"The Ultimate Guide to {self.title}",
            f"Why {self.title} Matters for {self.target_persona['name']}s",
            f"{self.title}: Tips and Tricks for {self.target_persona['name']}s",
            f"Mastering {self.title}: A Step-by-Step Guide",
            f"{self.title} 101: Everything You Need to Know",
        ]

# Add variations until we reach the requested count
        for pattern in patterns:
            if len(variations) < count:
                variations.append(pattern)
            else:
                break

            return variations[:count]

def generate_blog_post(
        self,
        topic: str = "",
        target_audience: str = "",
        tone: str = "",
        keywords: List[str] = None,
        word_count: int = None,
        include_images: bool = None,
    ) -> Dict[str, Any]:
        """
        Generate a complete blog post.

Args:
            topic: Topic of the blog post
            target_audience: Target audience for the blog post
            tone: Tone of the blog post
            keywords: SEO keywords for the blog post
            word_count: Target word count for the blog post
            include_images: Whether to include images in the blog post

Returns:
            Dictionary with blog post content
        """
        # Update template properties if provided
        if topic:
            self.title = topic

if target_audience:
            self.target_persona["name"] = target_audience

if tone:
            self.tone = tone

if keywords is not None:
            self.seo_keywords = keywords

if word_count is not None:
            self.target_word_count = word_count

if include_images is not None:
            self.include_images = include_images

# Generate base content
        content = self.generate_content()

# Add blog-specific elements
        content["word_count"] = self.target_word_count
        content["reading_time"] = f"{self.target_word_count // 200} minutes"
        content["include_images"] = self.include_images

# Add SEO information
        seo_info = self.get_blog_seo_recommendations()
        content["seo_info"] = {
            "keywords": self.seo_keywords or seo_info.get("secondary_keywords", []),
            "meta_title": seo_info.get("recommended_meta_title", self.title),
            "meta_description": seo_info.get("recommended_meta_description", ""),
            "url_slug": f"/{'-'.join(self.title.lower().split()[:5])}/",
        }

# Add keywords to the main content
        content["keywords"] = self.seo_keywords or seo_info.get(
            "secondary_keywords", []
        )

# Add image recommendations if enabled
        if self.include_images:
            content["images"] = []

# Featured image
            content["images"].append(
                {
                    "type": "featured",
                    "description": f"Featured image for {self.title}",
                    "alt_text": f"{self.title} - {self.target_persona['name']}",
                }
            )

# Section images
            for i, section in enumerate(content["sections"]):
                if section["section_type"] == "body":
                    content["images"].append(
                        {
                            "type": "section",
                            "section_index": i,
                            "description": f"Image illustrating {section['title']}",
                            "alt_text": f"{section['title']} - {self.target_persona['name']}",
                        }
                    )

# Add headline variations
        content["headline_variations"] = self.generate_headline_variations()

# Update timestamp
        self.updated_at = datetime.now().isoformat()

            return content

def get_blog_seo_recommendations(self) -> Dict[str, Any]:
        """
        Get blog-specific SEO recommendations.

Returns:
            Dictionary with blog SEO recommendations
        """
        # Get base SEO recommendations
        base_recommendations = self.get_seo_recommendations()

# Add blog-specific recommendations
        blog_recommendations = {
            "headline_optimization": [
                "Include primary keyword in headline",
                "Keep headline under 60 characters",
                "Use numbers or power words in headline",
            ],
            "url_structure": f"/{'-'.join(self.title.lower().split()[:5])}/",
            "internal_linking": [
                "Link to at least 3 other relevant blog posts",
                "Include links to relevant product or service pages",
            ],
            "content_structure": [
                "Use H2 and H3 headings with keywords",
                "Keep paragraphs short (3-4 sentences)",
                "Use bullet points and numbered lists",
            ],
            "rich_snippets": [
                "Add schema markup for article",
                "Consider FAQ schema if including FAQ section",
            ],
        }

# Combine recommendations
        combined_recommendations = {**base_recommendations, **blog_recommendations}

            return combined_recommendations


class SocialMediaTemplate(ContentTemplate):
    """
    Template for creating social media posts.
    """

def __init__(
        self,
        name: str = "",
        description: str = "",
        title: str = "",
        target_persona: Optional[Dict[str, Any]] = None,
        key_points: Optional[List[str]] = None,
        platform: str = "instagram",
        platforms: Optional[List[str]] = None,
        tone: Optional[str] = "casual",
        call_to_action: Optional[str] = None,
        hashtags: Optional[List[str]] = None,
        include_image: bool = True,
    ):
        """
        Initialize a social media post template.

Args:
            name: Name of the template
            description: Description of the template
            title: Title or main topic of the social media post
            target_persona: The target user persona for this post
            key_points: List of key points to cover in the post
            platform: Primary social media platform for this post
            platforms: List of social media platforms for this post
            tone: Optional tone for the post
            call_to_action: Optional call to action for the post
            hashtags: Optional list of hashtags to include
            include_image: Whether to include image recommendations
        """
        super().__init__(
            name, description, title, target_persona, key_points, tone, call_to_action
        )
        self.content_type = "social_media"
        self.platform = platform
        self.platforms = platforms or [platform]
        self.hashtags = hashtags or []
        self.include_image = include_image

# Add default sections
        if not self.sections:
            self.add_section(
                name="Caption",
                description="The caption for the social media post",
                content_type="text",
                placeholder="Write an engaging caption...",
                required=True,
            )

self.add_section(
                name="Hashtags",
                description="Hashtags for the social media post",
                content_type="text",
                placeholder="Enter hashtags separated by spaces...",
                required=False,
            )

if self.include_image:
                self.add_section(
                    name="Image Description",
                    description="Description of the image to use",
                    content_type="text",
                    placeholder="Describe the image you want to use...",
                    required=True,
                )

def generate_outline(self) -> Dict[str, Any]:
        """
        Generate an outline for social media posts.

Returns:
            Dictionary with social media post details
        """
        # Create platform-specific post variations
        platform_posts = {}

for platform in self.platforms:
            if platform.lower() == "twitter" or platform.lower() == "x":
                platform_posts["twitter"] = self._generate_twitter_post()
            elif platform.lower() == "linkedin":
                platform_posts["linkedin"] = self._generate_linkedin_post()
            elif platform.lower() == "facebook":
                platform_posts["facebook"] = self._generate_facebook_post()
            elif platform.lower() == "instagram":
                platform_posts["instagram"] = self._generate_instagram_post()

# Create a general outline
        outline = {
            "id": self.id,
            "title": self.title,
            "content_type": self.content_type,
            "target_persona": self.target_persona["name"],
            "platforms": self.platforms,
            "tone": self.tone,
            "call_to_action": self.call_to_action,
            "hashtags": self.hashtags,
            "platform_specific_posts": platform_posts,
            "created_at": self.created_at,
        }

# Add image recommendations if enabled
        if self.include_image:
            image_recommendations = {
                "description": f"Image related to {self.title}",
                "purpose": "Increase engagement and visibility",
                "platform_specific_sizes": {
                    "twitter": "1200 x 675 pixels",
                    "linkedin": "1200 x 627 pixels",
                    "facebook": "1200 x 630 pixels",
                    "instagram": "1080 x 1080 pixels (square) or 1080 x 1350 pixels (portrait)",
                },
            }
            outline["image_recommendations"] = image_recommendations

            return outline

def generate_post(
        self,
        topic: str = "",
        target_audience: str = "",
        tone: str = "",
        include_hashtags: bool = None,
        include_emoji: bool = None,
        include_call_to_action: bool = None,
        platform: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a social media post for a specific platform.

Args:
            topic: Topic of the post
            target_audience: Target audience for the post
            tone: Tone of the post
            include_hashtags: Whether to include hashtags
            include_emoji: Whether to include emojis
            include_call_to_action: Whether to include a call to action
            platform: Optional platform to generate the post for (defaults to self.platform)

Returns:
            Dictionary with post content
        """
        # Update template properties if provided
        if topic:
            self.title = topic

if target_audience:
            self.target_persona["name"] = target_audience

if tone:
            self.tone = tone

# Use specified platform or default to the first platform
        platform = platform or self.platform

# Generate platform-specific post
        if platform.lower() == "twitter" or platform.lower() == "x":
            post = self._generate_twitter_post()
        elif platform.lower() == "linkedin":
            post = self._generate_linkedin_post()
        elif platform.lower() == "facebook":
            post = self._generate_facebook_post()
        elif platform.lower() == "instagram":
            post = self._generate_instagram_post()
        else:
            # Default to a generic post
            post = {
                "platform": platform,
                "content": f"{self.title}\n\n{self.key_points[0] if self.key_points else ''}\n\n{self.call_to_action if self.call_to_action else ''}",
                "hashtags": self.hashtags,
                "character_count": len(
                    f"{self.title}\n\n{self.key_points[0] if self.key_points else ''}\n\n{self.call_to_action if self.call_to_action else ''}"
                ),
            }

# Add common elements
        post["id"] = self.id
        post["template_id"] = self.id
        post["title"] = self.title
        post["topic"] = topic or self.title
        post["target_persona"] = self.target_persona["name"]
        post["target_audience"] = target_audience or self.target_persona["name"]
        post["tone"] = self.tone
        post["created_at"] = self.created_at

# Add sections with content
        post["sections"] = []
        for section in self.sections:
            # Create a copy of the section
            section_copy = section.copy()

# Add sample content if the section doesn't have any
            if not section_copy.get("content"):
                if section_copy.get("name") == "Caption":
                    section_copy["content"] = (
                        f"Check out these amazing {self.title} that can help you achieve your goals! #trending"
                    )
                elif section_copy.get("name") == "Hashtags":
                    section_copy["content"] = (
                        " ".join([f"#{tag.replace(' ', '')}" for tag in self.hashtags])
                        if self.hashtags
                        else "#trending #socialmedia"
                    )
                elif section_copy.get("name") == "Image Description":
                    section_copy["content"] = f"Image showing {self.title} in action"
                else:
                    section_copy["content"] = (
                        f"Content about {section_copy.get('name', 'this topic')}."
                    )

post["sections"].append(section_copy)

# Add image recommendation if enabled
        if self.include_image:
            post["image"] = {
                "description": f"Image related to {self.title}",
                "alt_text": f"{self.title} - {self.target_persona['name']}",
                "recommended_size": self._get_image_size_for_platform(platform),
            }

# Add emojis if requested
        if include_emoji:
            post["content"] = self._add_emojis_to_content(post["content"])

# Add call to action if requested
        if include_call_to_action and not self.call_to_action:
            post["content"] += "\n\nClick the link in bio to learn more!"

# Update hashtags if requested
        post["include_hashtags"] = (
            include_hashtags if include_hashtags is not None else bool(self.hashtags)
        )
        post["include_emoji"] = include_emoji if include_emoji is not None else True
        post["include_call_to_action"] = (
            include_call_to_action
            if include_call_to_action is not None
            else bool(self.call_to_action)
        )

if include_hashtags is not None:
            if include_hashtags and not self.hashtags:
                self.hashtags = self.generate_hashtag_recommendations(5)
                post["hashtags"] = self.hashtags
            elif not include_hashtags:
                post["hashtags"] = []

# Update timestamp
        self.updated_at = datetime.now().isoformat()

            return post

def _add_emojis_to_content(self, content: str) -> str:
        """
        Add emojis to content.

Args:
            content: Content to add emojis to

Returns:
            Content with emojis
        """
        # Simple emoji mapping for common topics
        emoji_mapping = {
            "business": "💼",
            "money": "💰",
            "growth": "📈",
            "idea": "💡",
            "success": "🚀",
            "time": "⏰",
            "tip": "💯",
            "learn": "📚",
            "social": "🔗",
            "marketing": "📣",
            "content": "📝",
            "strategy": "🎯",
            "analytics": "📊",
            "customer": "👥",
            "product": "🛍️",
            "service": "🛠️",
            "digital": "💻",
            "mobile": "📱",
            "email": "📧",
            "video": "🎬",
        }

# Add emoji to title
        for keyword, emoji in emoji_mapping.items():
            if keyword in self.title.lower() and not content.startswith(emoji):
                content = f"{emoji} {content}"
                break

# If no emoji was added, add a default one
        if not any(emoji in content[:2] for emoji in emoji_mapping.values()):
            content = f"✨ {content}"

            return content

def _get_image_size_for_platform(self, platform: str) -> str:
        """
        Get the recommended image size for a platform.

Args:
            platform: Social media platform

Returns:
            Recommended image size
        """
        platform_sizes = {
            "twitter": "1200 x 675 pixels",
            "x": "1200 x 675 pixels",
            "linkedin": "1200 x 627 pixels",
            "facebook": "1200 x 630 pixels",
            "instagram": "1080 x 1080 pixels (square) or 1080 x 1350 pixels (portrait)",
        }

            return platform_sizes.get(platform.lower(), "1200 x 1200 pixels")

def _generate_twitter_post(self) -> Dict[str, Any]:
        """Generate a Twitter post."""
        # Create a short version of the post (max 280 characters)
        main_point = self.key_points[0] if self.key_points else self.title

# Format hashtags
        hashtag_text = " ".join(
            [f"#{tag.replace(' ', '')}" for tag in self.hashtags[:3]]
        )

# Create call to action
        cta = f" {self.call_to_action}" if self.call_to_action else ""

# Combine elements, ensuring we don't exceed character limit
        post_text = f"{main_point}{cta}"
        if len(post_text + " " + hashtag_text) <= 280:
            post_text = f"{post_text} {hashtag_text}"

            return {
            "platform": "Twitter",
            "character_limit": 280,
            "content": post_text[:280],
            "post_text": post_text[:280],  # For backward compatibility
            "estimated_length": len(post_text),
            "recommended_posting_times": ["8-10am", "12-1pm", "5-6pm"],
            "engagement_tips": [
                "Ask a question to encourage replies",
                "Tag relevant accounts when appropriate",
                "Consider creating a thread for longer content",
            ],
        }

def _generate_linkedin_post(self) -> Dict[str, Any]:
        """Generate a LinkedIn post."""
        # LinkedIn posts can be longer and more professional
        intro = f"📝 {self.title}\n\n"

# Add key points as bullet points
        body = ""
        for point in self.key_points[:3]:  # Limit to 3 key points
            body += f"• {point}\n"

# Add a space and the call to action
        cta = f"\n{self.call_to_action}" if self.call_to_action else ""

# Add hashtags at the end
        hashtag_text = "\n\n" + " ".join(
            [f"#{tag.replace(' ', '')}" for tag in self.hashtags[:5]]
        )

# Combine all elements
        post_text = intro + body + cta + hashtag_text

            return {
            "platform": "LinkedIn",
            "character_limit": 3000,
            "content": post_text[:3000],
            "post_text": post_text[:3000],  # For backward compatibility
            "estimated_length": len(post_text),
            "recommended_posting_times": ["8-9am", "10-11am", "1-2pm"],
            "engagement_tips": [
                "Start with a hook or question",
                "Use line breaks to make the post scannable",
                "Tag relevant connections or companies",
                "End with a clear call to action",
            ],
        }

def _generate_facebook_post(self) -> Dict[str, Any]:
        """Generate a Facebook post."""
        # Facebook posts can be conversational
        intro = f"💡 {self.title}\n\n"

# Add a brief description
        body = f"I wanted to share some thoughts on {self.title.lower()}:\n\n"

# Add key points
        for i, point in enumerate(self.key_points[:3]):
            body += f"{i+1}. {point}\n"

# Add call to action
        cta = f"\n{self.call_to_action}" if self.call_to_action else ""

# Add hashtags (fewer than Twitter/Instagram)
        hashtag_text = "\n\n" + " ".join(
            [f"#{tag.replace(' ', '')}" for tag in self.hashtags[:3]]
        )

# Combine all elements
        post_text = intro + body + cta + hashtag_text

            return {
            "platform": "Facebook",
            "content": post_text,
            "post_text": post_text,  # For backward compatibility
            "estimated_length": len(post_text),
            "recommended_posting_times": ["1-4pm", "6-8pm"],
            "engagement_tips": [
                "Ask a question to encourage comments",
                "Consider using emojis to add personality",
                "Tag relevant pages when appropriate",
                "Respond to comments to boost engagement",
            ],
        }

def _generate_instagram_post(self) -> Dict[str, Any]:
        """Generate an Instagram post caption."""
        # Instagram captions focus on the image with supporting text
        intro = f"✨ {self.title}\n\n"

# Add a brief, engaging description
        body = f"{self.key_points[0] if self.key_points else ''}\n\n"

# Add call to action
        cta = f"{self.call_to_action}\n\n" if self.call_to_action else ""

# Add hashtags (Instagram can have more hashtags)
        hashtag_text = ".\n.\n.\n" + " ".join(
            [f"#{tag.replace(' ', '')}" for tag in self.hashtags]
        )

# Combine all elements
        post_text = intro + body + cta + hashtag_text

            return {
            "platform": "instagram",
            "content": post_text,
            "post_text": post_text,  # For backward compatibility
            "estimated_length": len(post_text),
            "recommended_posting_times": ["11am-1pm", "7-9pm"],
            "engagement_tips": [
                "Start with a hook to grab attention",
                "Use line breaks to make the caption readable",
                "Include a clear call to action",
                "Use up to 30 relevant hashtags",
                "Consider hiding hashtags with periods or in a comment",
            ],
        }

def generate_hashtag_recommendations(self, count: int = 10) -> List[str]:
        """
        Generate hashtag recommendations based on the content.

Args:
            count: Number of hashtags to recommend

Returns:
            List of recommended hashtags
        """
        # Start with any existing hashtags
        recommendations = list(self.hashtags)

# Add hashtags based on the title
        title_words = self.title.lower().split()
        for word in title_words:
            if len(word) > 3 and word not in [
                "with",
                "from",
                "that",
                "this",
                "what",
                "when",
                "where",
                "which",
            ]:
                recommendations.append(word)

# Add hashtags based on key points
        for point in self.key_points:
            point_words = point.lower().split()
            potential_tag = "".join([word.capitalize() for word in point_words[:3]])
            if (
                potential_tag and len(potential_tag) < 30
            ):  # Avoid excessively long hashtags
                recommendations.append(potential_tag)

# Add hashtags based on target persona
        recommendations.append(self.target_persona["name"].replace(" ", ""))

# Add industry-standard hashtags
        industry_hashtags = [
            "ContentCreation",
            "DigitalMarketing",
            "SocialMediaTips",
            "MarketingStrategy",
            "BusinessTips",
            "Entrepreneurship",
            "GrowthHacking",
            "SmallBusiness",
            "StartupLife",
            "Innovation",
        ]

# Combine all hashtags, remove duplicates, and limit to requested count
        all_hashtags = list(set(recommendations + industry_hashtags))
                    return all_hashtags[:count]


class EmailNewsletterTemplate(ContentTemplate):
    """
    Template for creating email newsletter content.
    """

def __init__(
        self,
        name: str = "",
        description: str = "",
        title: str = "",
        target_persona: Optional[Dict[str, Any]] = None,
        key_points: Optional[List[str]] = None,
        tone: Optional[str] = "professional",
        call_to_action: Optional[str] = None,
        subject_line: Optional[str] = None,
        newsletter_type: str = "general",
        include_images: bool = True,
        sender_name: Optional[str] = None,
        sender_email: Optional[str] = None,
    ):
        """
        Initialize an email newsletter template.

Args:
            name: Name of the template
            description: Description of the template
            title: Title of the email newsletter
            target_persona: The target user persona for this newsletter
            key_points: List of key points to cover in the newsletter
            tone: Optional tone for the newsletter
            call_to_action: Optional call to action for the newsletter
            subject_line: Optional subject line for the email
            newsletter_type: Type of newsletter (general, promotional, educational, etc.)
            include_images: Whether to include image recommendations
            sender_name: Optional name of the sender
            sender_email: Optional email of the sender
        """
        super().__init__(
            name, description, title, target_persona, key_points, tone, call_to_action
        )
        self.content_type = "email_newsletter"
        self.subject_line = subject_line or title
        self.newsletter_type = newsletter_type
        self.include_images = include_images
        self.sender_name = sender_name
        self.sender_email = sender_email

# Add default sections
        if not self.sections:
            self.add_section(
                name="Subject Line",
                description="The subject line of the email",
                content_type="text",
                placeholder="Enter a compelling subject line...",
                required=True,
            )

self.add_section(
                name="Preheader",
                description="The preheader text that appears in email clients",
                content_type="text",
                placeholder="Enter preheader text (50-100 characters)...",
                required=True,
            )

self.add_section(
                name="Greeting",
                description="The greeting for the recipient",
                content_type="text",
                placeholder="Enter a greeting...",
                required=True,
            )

self.add_section(
                name="Introduction",
                description="The introduction of the email",
                content_type="text",
                placeholder="Write an engaging introduction...",
                required=True,
            )

self.add_section(
                name="Main Content",
                description="The main content of the email",
                content_type="text",
                placeholder="Write the main content here...",
                required=True,
            )

self.add_section(
                name="Call to Action",
                description="The call to action for the email",
                content_type="text",
                placeholder="Enter a call to action...",
                required=False,
            )

self.add_section(
                name="Footer",
                description="The footer of the email",
                content_type="text",
                placeholder="Enter footer text...",
                required=True,
            )

def generate_outline(self) -> Dict[str, Any]:
        """
        Generate an outline for the email newsletter.

Returns:
            Dictionary with email newsletter outline details
        """
        # Create sections based on newsletter type
        sections = []

# Add header section
        sections.append(
            {
                "section_type": "header",
                "title": "Header",
                "description": "Email header with logo and preheader text",
                "content": f"Newsletter: {self.title}",
                "preheader_text": f"Check out our latest insights on {self.title}",
            }
        )

# Add greeting section
        sections.append(
            {
                "section_type": "greeting",
                "title": "Greeting",
                "description": "Personalized greeting for the recipient",
                "content": "Hi {first_name},",
            }
        )

# Add introduction section
        sections.append(
            {
                "section_type": "introduction",
                "title": "Introduction",
                "description": "Brief introduction to the newsletter topic",
                "content": f"Welcome to our newsletter about {self.title}. {self.key_points[0] if self.key_points else ''}",
            }
        )

# Add main content sections based on newsletter type
        if self.newsletter_type == "general":
            # Add a section for each key point
            for i, point in enumerate(self.key_points):
                sections.append(
                    {
                        "section_type": "content",
                        "title": f"Section {i+1}: {point}",
                        "description": f"Content about {point}",
                        "content": f"## {point}\n\nDetails about {point} would go here.",
                    }
                )

elif self.newsletter_type == "promotional":
            # Add product/service highlight section
            sections.append(
                {
                    "section_type": "product_highlight",
                    "title": "Product Highlight",
                    "description": "Highlight of the product or service being promoted",
                    "content": f"## Introducing {self.title}\n\nDetails about the product/service would go here.",
                }
            )

# Add benefits section
            sections.append(
                {
                    "section_type": "benefits",
                    "title": "Benefits",
                    "description": "Benefits of the product or service",
                    "content": "## Benefits\n\n"
                    + "\n".join([f"- {point}" for point in self.key_points]),
                }
            )

# Add pricing section
            sections.append(
                {
                    "section_type": "pricing",
                    "title": "Pricing",
                    "description": "Pricing information",
                    "content": "## Pricing\n\nPricing details would go here.",
                }
            )

elif self.newsletter_type == "educational":
            # Add educational content sections
            sections.append(
                {
                    "section_type": "main_content",
                    "title": "Main Content",
                    "description": "Main educational content",
                    "content": f"## {self.title}\n\n"
                    + "\n\n".join(
                        [
                            f"### {point}\n\nDetails about {point} would go here."
                            for point in self.key_points
                        ]
                    ),
                }
            )

# Add resources section
            sections.append(
                {
                    "section_type": "resources",
                    "title": "Additional Resources",
                    "description": "Links to additional resources",
                    "content": "## Additional Resources\n\n- Resource 1\n- Resource 2\n- Resource 3",
                }
            )

# Add call-to-action section
        if self.call_to_action:
            sections.append(
                {
                    "section_type": "call_to_action",
                    "title": "Call to Action",
                    "description": "Call to action button or link",
                    "content": self.call_to_action,
                    "button_text": "Click Here",
                    "button_url": "{{cta_url}}",
                }
            )

# Add footer section
        sections.append(
            {
                "section_type": "footer",
                "title": "Footer",
                "description": "Email footer with unsubscribe link and contact information",
                "content": f"© {datetime.now().year} {self.sender_name or 'Company Name'}. All rights reserved.",
                "unsubscribe_text": "If you no longer wish to receive these emails, you can {{unsubscribe}}.",
                "contact_info": self.sender_email or "contact@example.com",
            }
        )

# Create the outline
        outline = {
            "id": self.id,
            "title": self.title,
            "content_type": self.content_type,
            "newsletter_type": self.newsletter_type,
            "subject_line": self.subject_line,
            "target_persona": self.target_persona["name"],
            "tone": self.tone,
            "sender_name": self.sender_name,
            "sender_email": self.sender_email,
            "sections": sections,
            "created_at": self.created_at,
        }

# Add image recommendations if enabled
        if self.include_images:
            image_recommendations = []

# Header image
            image_recommendations.append(
                {
                    "description": "Header image or logo",
                    "placement": "header",
                    "size": "600 x 200 pixels",
                    "purpose": "Brand recognition",
                }
            )

# Main content image
            image_recommendations.append(
                {
                    "description": f"Main image related to {self.title}",
                    "placement": "after introduction",
                    "size": "600 x 400 pixels",
                    "purpose": "Illustrate the main topic",
                }
            )

# Add image for call to action if present
            if self.call_to_action:
                image_recommendations.append(
                    {
                        "description": "Call to action button or banner",
                        "placement": "call to action section",
                        "size": "600 x 100 pixels",
                        "purpose": "Draw attention to the call to action",
                    }
                )

outline["image_recommendations"] = image_recommendations

            return outline

def generate_subject_line_variations(self, count: int = 5) -> List[str]:
        """
        Generate variations of the email subject line.

Args:
            count: Number of variations to generate

Returns:
            List of subject line variations
        """
        variations = [self.subject_line]  # Start with the original subject line

# Generate variations based on common email subject line patterns
        patterns = [
            f"[Newsletter] {self.title}",
            f"{self.target_persona['name']}'s Guide to {self.title}",
            f"{len(self.key_points)} Tips for {self.title}",
            f"How to {self.title} - {self.target_persona['name']} Newsletter",
            f"The Latest on {self.title}",
            f"Exclusive: {self.title} Insights",
            f"Quick Read: {self.title} for {self.target_persona['name']}s",
            f"🔥 {self.title}: What You Need to Know",
        ]

# Add variations until we reach the requested count
        for pattern in patterns:
            if len(variations) < count:
                variations.append(pattern)
            else:
                break

            return variations[:count]

def generate_newsletter(
        self,
        topic: str = "",
        target_audience: str = "",
        tone: str = "",
        include_images: bool = None,
        include_personalization: bool = None,
        include_call_to_action: bool = None,
    ) -> Dict[str, Any]:
        """
        Generate a complete email newsletter.

Args:
            topic: Topic of the newsletter
            target_audience: Target audience for the newsletter
            tone: Tone of the newsletter
            include_images: Whether to include images
            include_personalization: Whether to include personalization
            include_call_to_action: Whether to include a call to action

Returns:
            Dictionary with newsletter content
        """
        # Update template properties if provided
        if topic:
            self.title = topic
            self.subject_line = topic

if target_audience:
            self.target_persona["name"] = target_audience

if tone:
            self.tone = tone

if include_images is not None:
            self.include_images = include_images

if include_call_to_action and not self.call_to_action:
            self.call_to_action = "Click here to learn more"

# Generate base content
        outline = self.generate_outline()

# Create the newsletter content
        newsletter = {
            "id": self.id,
            "template_id": self.id,
            "name": self.name,
            "description": self.description,
            "title": self.title,
            "topic": topic or self.title,
            "content_type": self.content_type,
            "newsletter_type": self.newsletter_type,
            "subject_line": self.subject_line,
            "subject_line_variations": self.generate_subject_line_variations(),
            "target_persona": self.target_persona["name"],
            "target_audience": target_audience or self.target_persona["name"],
            "tone": self.tone,
            "sender_name": self.sender_name,
            "sender_email": self.sender_email,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "include_images": (
                include_images if include_images is not None else self.include_images
            ),
            "include_personalization": (
                include_personalization
                if include_personalization is not None
                else False
            ),
            "include_call_to_action": (
                include_call_to_action
                if include_call_to_action is not None
                else bool(self.call_to_action)
            ),
        }

# Add sections with content
        newsletter["sections"] = []
        for section in self.sections:
            # Create a copy of the section
            section_copy = section.copy()

# Add sample content if the section doesn't have any
            if not section_copy.get("content"):
                if section_copy.get("name") == "Subject Line":
                    section_copy["content"] = (
                        self.subject_line or f"Newsletter: {self.title}"
                    )
                elif section_copy.get("name") == "Preheader":
                    section_copy["content"] = (
                        f"The latest insights on {self.title} for {self.target_persona['name']}"
                    )
                elif section_copy.get("name") == "Greeting":
                    section_copy["content"] = "Hello {{first_name}},"
                elif section_copy.get("name") == "Introduction":
                    section_copy["content"] = (
                        f"Welcome to our newsletter about {self.title}. We have some exciting updates to share with you."
                    )
                elif section_copy.get("name") == "Main Content":
                    section_copy["content"] = (
                        f"Here are the key points about {self.title} that you should know about."
                    )
                elif section_copy.get("name") == "Call to Action":
                    section_copy["content"] = (
                        self.call_to_action or "Click here to learn more"
                    )
                elif section_copy.get("name") == "Footer":
                    section_copy["content"] = (
                        "Thank you for reading! If you have any questions, please reply to this email."
                    )
                else:
                    section_copy["content"] = (
                        f"Content about {section_copy.get('name', 'this topic')}."
                    )

newsletter["sections"].append(section_copy)

# Add image recommendations if enabled
        if self.include_images and "image_recommendations" in outline:
            newsletter["images"] = outline["image_recommendations"]

# Add personalization if requested
        if include_personalization:
            newsletter["personalization"] = {
                "merge_tags": [
                    {"tag": "{{first_name}}", "description": "Recipient's first name"},
                    {"tag": "{{last_name}}", "description": "Recipient's last name"},
                    {"tag": "{{company}}", "description": "Recipient's company name"},
                    {"tag": "{{unsubscribe}}", "description": "Unsubscribe link"},
                ],
                "dynamic_content": [
                    {
                        "condition": "industry",
                        "values": [
                            "technology",
                            "healthcare",
                            "finance",
                            "education",
                            "retail",
                        ],
                    },
                    {
                        "condition": "role",
                        "values": [
                            "manager",
                            "executive",
                            "individual contributor",
                            "consultant",
                        ],
                    },
                ],
            }

# Add best practices
        newsletter["best_practices"] = self.get_email_best_practices()

# Add preview text
        newsletter["preview_text"] = f"Check out our latest insights on {self.title}"

# Add email metrics to track
        newsletter["recommended_metrics"] = [
            "open_rate",
            "click_through_rate",
            "conversion_rate",
            "bounce_rate",
            "unsubscribe_rate",
        ]

# Update timestamp
        self.updated_at = datetime.now().isoformat()

            return newsletter

def get_email_best_practices(self) -> Dict[str, List[str]]:
        """
        Get best practices for email newsletters.

Returns:
            Dictionary with email best practices
        """
        best_practices = {
            "subject_line": [
                "Keep subject lines under 50 characters",
                "Avoid spam trigger words like 'free', 'guarantee', 'buy now'",
                "Create a sense of urgency or curiosity",
                "Personalize with recipient's name when possible",
            ],
            "content": [
                "Keep paragraphs short (2-3 sentences)",
                "Use bullet points for easy scanning",
                "Include a clear call-to-action",
                "Balance text and images (60% text, 40% images recommended)",
                f"Write in a {self.tone} tone that matches your brand",
            ],
            "design": [
                "Use a responsive email template",
                "Ensure your email looks good on mobile devices",
                "Keep the width around 600 pixels",
                "Use web-safe fonts",
                "Include alt text for all images",
            ],
            "technical": [
                "Test your email across different email clients",
                "Include a plain text version",
                "Ensure all links work correctly",
                "Include an unsubscribe link",
                "Follow CAN-SPAM and GDPR requirements",
            ],
            "timing": [
                "Send at optimal times based on your audience (typically Tuesday-Thursday mornings)",
                "Maintain a consistent sending schedule",
                "Avoid sending too frequently (usually no more than once per week)",
                "Consider time zones if you have an international audience",
            ],
        }

            return best_practices


class VideoScriptTemplate(ContentTemplate):
    """
    Template for creating video script content.
    """

def __init__(
        self,
        title: str,
        target_persona: Dict[str, Any],
        key_points: List[str],
        tone: Optional[str] = "conversational",
        call_to_action: Optional[str] = None,
        video_length: Optional[int] = 5,  # in minutes
        video_type: str = "educational",
        include_b_roll: bool = True,
    ):
        """
        Initialize a video script template.

Args:
            title: Title of the video
            target_persona: The target user persona for this video
            key_points: List of key points to cover in the video
            tone: Optional tone for the video
            call_to_action: Optional call to action for the video
            video_length: Optional target length of the video in minutes
            video_type: Type of video (educational, promotional, tutorial, etc.)
            include_b_roll: Whether to include B-roll recommendations
        """
        super().__init__(title, target_persona, key_points, tone, call_to_action)
        self.content_type = "video_script"
        self.video_length = video_length
        self.video_type = video_type
        self.include_b_roll = include_b_roll

# Calculate approximate word count based on video length
        # Average speaking rate is about 150 words per minute
        self.target_word_count = video_length * 150

def generate_outline(self) -> Dict[str, Any]:
        """
        Generate an outline for the video script.

Returns:
            Dictionary with video script outline details
        """
        # Create script sections
        script_sections = []

# Calculate approximate time per section
        # Reserve 15% for intro and outro
        main_content_time = self.video_length * 0.85
        time_per_point = main_content_time / max(len(self.key_points), 1)

# Add intro section
        script_sections.append(
            {
                "section_type": "intro",
                "title": "Introduction",
                "description": "Video introduction and hook",
                "duration": f"{int(self.video_length * 0.1 * 60)} seconds",
                "word_count": int(self.target_word_count * 0.1),
                "script": f"[HOST ON CAMERA]\n\nHi, I'm {{host_name}} and welcome to this video about {self.title}. "
                f"Today we're going to explore {', '.join(self.key_points[:-1]) + ' and ' + self.key_points[-1] if len(self.key_points) > 1 else self.key_points[0] if self.key_points else ''}. "
                f"If you've ever struggled with {self.target_persona['pain_points'][0] if self.target_persona['pain_points'] else 'this topic'}, this video is for you.",
            }
        )

# Add main content sections
        for i, point in enumerate(self.key_points):
            b_roll = ""
            if self.include_b_roll:
                b_roll = f"\n\n[B-ROLL: Footage showing {point}]"

script_sections.append(
                {
                    "section_type": "main_content",
                    "title": f"Section {i+1}: {point}",
                    "description": f"Content about {point}",
                    "duration": f"{int(time_per_point * 60)} seconds",
                    "word_count": int(
                        self.target_word_count * (time_per_point / self.video_length)
                    ),
                    "script": f"[HOST ON CAMERA]\n\nLet's talk about {point}. "
                    f"This is important because it helps {self.target_persona['name']}s achieve {self.target_persona['goals'][0] if self.target_persona['goals'] else 'their goals'}."
                    f"{b_roll}\n\n"
                    "[HOST ON CAMERA]\n\n"
                    f"The key thing to remember about {point} is...",
                }
            )

# Add outro section with call to action
        outro_script = (
            f"[HOST ON CAMERA]\n\nThanks for watching this video about {self.title}. "
        )
        if self.call_to_action:
            outro_script += f"Don't forget to {self.call_to_action}. "
        outro_script += "If you found this helpful, please like and subscribe for more content like this."

script_sections.append(
            {
                "section_type": "outro",
                "title": "Conclusion",
                "description": "Video conclusion and call to action",
                "duration": f"{int(self.video_length * 0.05 * 60)} seconds",
                "word_count": int(self.target_word_count * 0.05),
                "script": outro_script,
            }
        )

# Create the outline
        outline = {
            "id": self.id,
            "title": self.title,
            "content_type": self.content_type,
            "video_type": self.video_type,
            "target_persona": self.target_persona["name"],
            "tone": self.tone,
            "video_length": f"{self.video_length} minutes",
            "target_word_count": self.target_word_count,
            "script_sections": script_sections,
            "created_at": self.created_at,
        }

# Add B-roll recommendations if enabled
        if self.include_b_roll:
            b_roll_recommendations = []

# Add intro B-roll
            b_roll_recommendations.append(
                {
                    "description": f"Opening shots related to {self.title}",
                    "placement": "intro",
                    "duration": "5-10 seconds",
                    "purpose": "Set the tone and context for the video",
                }
            )

# Add B-roll for each key point
            for i, point in enumerate(self.key_points):
                b_roll_recommendations.append(
                    {
                        "description": f"Footage illustrating {point}",
                        "placement": f"Section {i+1}",
                        "duration": "10-15 seconds",
                        "purpose": "Visualize the concept being explained",
                    }
                )

# Add transition B-roll
            if len(self.key_points) > 1:
                b_roll_recommendations.append(
                    {
                        "description": "Transition shots between sections",
                        "placement": "Between main sections",
                        "duration": "3-5 seconds each",
                        "purpose": "Smooth transition between topics",
                    }
                )

outline["b_roll_recommendations"] = b_roll_recommendations

            return outline

def generate_script_with_timing(self) -> Dict[str, Any]:
        """
        Generate a detailed script with timing information.

Returns:
            Dictionary with detailed script information
        """
        # Get the basic outline first
        outline = self.generate_outline()
        script_sections = outline["script_sections"]

# Calculate cumulative timing
        current_time = 0
        for section in script_sections:
            # Convert duration from "X seconds" to integer seconds
            duration_seconds = int(section["duration"].split()[0])

# Add timing information
            section["start_time"] = self._format_timestamp(current_time)
            current_time += duration_seconds
            section["end_time"] = self._format_timestamp(current_time)

# Add total duration
        outline["total_duration"] = self._format_timestamp(current_time)

            return outline

def _format_timestamp(self, seconds: int) -> str:
        """Format seconds as MM:SS."""
        minutes = seconds // 60
        remaining_seconds = seconds % 60
                    return f"{minutes:02d}:{remaining_seconds:02d}"

def get_video_best_practices(self) -> Dict[str, List[str]]:
        """
        Get best practices for video creation.

Returns:
            Dictionary with video best practices
        """
        best_practices = {
            "scripting": [
                "Write for speaking, not reading (use conversational language)",
                "Keep sentences short and simple",
                "Use active voice rather than passive voice",
                "Include pauses for emphasis or transitions",
                "Address the viewer directly ('you')",
            ],
            "structure": [
                "Start with a hook in the first 15 seconds",
                "Preview what the video will cover",
                "Organize content in a logical sequence",
                "Recap key points at the end",
                "Include a clear call to action",
            ],
            "visual_elements": [
                "Change shots every 5-10 seconds to maintain interest",
                "Use text overlays for key points or complex terms",
                "Include relevant B-roll footage to illustrate concepts",
                "Consider adding graphics or animations for abstract concepts",
                "Ensure good lighting and clear audio",
            ],
            "engagement": [
                "Ask questions to encourage viewer reflection",
                "Mention comments or feedback from previous videos",
                "Encourage likes, subscriptions, and sharing",
                "Tease future content to build anticipation",
                "Respond to common questions or objections",
            ],
            "platform_specific": {
                "youtube": [
                    "Optimize title and description with keywords",
                    "Create an eye-catching thumbnail",
                    "Add timestamps for longer videos",
                    "Use end screens and cards to promote other content",
                    "Organize videos into playlists",
                ],
                "social_media": [
                    "Front-load key information in the first 5-10 seconds",
                    "Design for viewing without sound (captions, text overlays)",
                    "Keep videos under 2 minutes for most platforms",
                    "Use square or vertical format for mobile viewing",
                    "Include your branding within the first few seconds",
                ],
            },
        }

            return best_practices


class LandingPageTemplate(ContentTemplate):
    """
    Template for creating landing page content.
    """

def __init__(
        self,
        title: str,
        target_persona: Dict[str, Any],
        key_points: List[str],
        tone: Optional[str] = "persuasive",
        call_to_action: Optional[str] = None,
        unique_selling_proposition: Optional[str] = None,
        features: Optional[List[Dict[str, str]]] = None,
        testimonials: Optional[List[Dict[str, str]]] = None,
        include_faq: bool = True,
    ):
        """
        Initialize a landing page template.

Args:
            title: Title of the landing page
            target_persona: The target user persona for this landing page
            key_points: List of key points to cover (benefits)
            tone: Optional tone for the landing page
            call_to_action: Optional call to action for the landing page
            unique_selling_proposition: Optional unique selling proposition
            features: Optional list of features with descriptions
            testimonials: Optional list of testimonials
            include_faq: Whether to include FAQ section
        """
        super().__init__(title, target_persona, key_points, tone, call_to_action)
        self.content_type = "landing_page"
        self.unique_selling_proposition = (
            unique_selling_proposition
            or f"The best solution for {target_persona['name']}s"
        )
        self.features = features or []
        self.testimonials = testimonials or []
        self.include_faq = include_faq

def generate_outline(self) -> Dict[str, Any]:
        """
        Generate an outline for the landing page.

Returns:
            Dictionary with landing page outline details
        """
        # Create sections for the landing page
        sections = []

# Add hero section
        sections.append(
            {
                "section_type": "hero",
                "title": "Hero Section",
                "description": "Main headline, subheadline, and primary call to action",
                "elements": {
                    "headline": self.title,
                    "subheadline": self.unique_selling_proposition,
                    "primary_cta": self.call_to_action or "Get Started",
                    "hero_image": f"Image showing {self.target_persona['name']} using the product/service",
                },
            }
        )

# Add problem section
        sections.append(
            {
                "section_type": "problem",
                "title": "Problem Section",
                "description": "Describe the problem your target audience faces",
                "elements": {
                    "headline": f"Are you struggling with {self.target_persona['pain_points'][0] if self.target_persona['pain_points'] else 'this problem'}?",
                    "description": f"Many {self.target_persona['name']}s face challenges with "
                    f"{', '.join(self.target_persona['pain_points'][:-1]) + ' and ' + self.target_persona['pain_points'][-1] if len(self.target_persona['pain_points']) > 1 else self.target_persona['pain_points'][0] if self.target_persona['pain_points'] else 'various issues'}.",
                    "image": "Image illustrating the problem",
                },
            }
        )

# Add solution section
        sections.append(
            {
                "section_type": "solution",
                "title": "Solution Section",
                "description": "Present your solution to the problem",
                "elements": {
                    "headline": f"Introducing {self.title}",
                    "description": f"Our solution helps {self.target_persona['name']}s "
                    f"{self.target_persona['goals'][0] if self.target_persona['goals'] else 'achieve their goals'} "
                    "without the hassle.",
                    "image": "Image or screenshot of the product/service",
                },
            }
        )

# Add benefits section
        benefit_items = []
        for point in self.key_points:
            benefit_items.append(
                {
                    "title": point,
                    "description": f"Description of how {point} benefits the user",
                    "icon": "Relevant icon",
                }
            )

sections.append(
            {
                "section_type": "benefits",
                "title": "Benefits Section",
                "description": "Highlight the key benefits of your solution",
                "elements": {"headline": "Benefits", "benefit_items": benefit_items},
            }
        )

# Add features section if features are provided
        if self.features:
            sections.append(
                {
                    "section_type": "features",
                    "title": "Features Section",
                    "description": "Detail the features of your solution",
                    "elements": {
                        "headline": "Features",
                        "feature_items": self.features,
                    },
                }
            )

# Add testimonials section if testimonials are provided
        if self.testimonials:
            sections.append(
                {
                    "section_type": "testimonials",
                    "title": "Testimonials Section",
                    "description": "Display testimonials from satisfied customers",
                    "elements": {
                        "headline": "What Our Customers Say",
                        "testimonial_items": self.testimonials,
                    },
                }
            )

# Add FAQ section if enabled
        if self.include_faq:
            faq_items = []

# Generate FAQs based on key points and persona
            faq_items.append(
                {
                    "question": f"How does {self.title} work?",
                    "answer": f"Our solution is designed specifically for {self.target_persona['name']}s to help them achieve their goals easily and efficiently.",
                }
            )

faq_items.append(
                {
                    "question": f"How much does {self.title} cost?",
                    "answer": "We offer flexible pricing options to suit different needs. Contact us for a personalized quote.",
                }
            )

for point in self.key_points[:2]:  # Limit to first 2 key points
                faq_items.append(
                    {
                        "question": f"How does {self.title} help with {point.lower()}?",
                        "answer": f"Our solution provides specialized tools and features to address {point.lower()} effectively.",
                    }
                )

faq_items.append(
                {
                    "question": "How long does it take to get started?",
                    "answer": "You can get started in just a few minutes. Our onboarding process is designed to be quick and hassle-free.",
                }
            )

sections.append(
                {
                    "section_type": "faq",
                    "title": "FAQ Section",
                    "description": "Answer frequently asked questions",
                    "elements": {
                        "headline": "Frequently Asked Questions",
                        "faq_items": faq_items,
                    },
                }
            )

# Add CTA section
        sections.append(
            {
                "section_type": "cta",
                "title": "Call to Action Section",
                "description": "Final call to action",
                "elements": {
                    "headline": f"Ready to {self.target_persona['goals'][0] if self.target_persona['goals'] else 'get started'}?",
                    "description": f"Join thousands of {self.target_persona['name']}s who have already transformed their workflow.",
                    "cta_button": self.call_to_action or "Get Started Now",
                    "secondary_cta": "Contact Us",
                },
            }
        )

# Create the outline
        outline = {
            "id": self.id,
            "title": self.title,
            "content_type": self.content_type,
            "target_persona": self.target_persona["name"],
            "unique_selling_proposition": self.unique_selling_proposition,
            "tone": self.tone,
            "call_to_action": self.call_to_action,
            "sections": sections,
            "created_at": self.created_at,
        }

            return outline

def get_landing_page_best_practices(self) -> Dict[str, List[str]]:
        """
        Get best practices for landing pages.

Returns:
            Dictionary with landing page best practices
        """
        best_practices = {
            "headline": [
                "Keep it clear, specific, and benefit-focused",
                "Use numbers or specific results when possible",
                "Address the target persona's main pain point",
                "Keep it under 15 words",
                "Consider using a question format",
            ],
            "design": [
                "Use a clean, uncluttered layout",
                "Ensure mobile responsiveness",
                "Use whitespace effectively",
                "Maintain consistent branding",
                "Use high-quality, relevant images",
                "Ensure fast loading times",
            ],
            "content": [
                "Focus on benefits, not features",
                "Use customer-centric language",
                "Keep paragraphs short (3-4 lines max)",
                "Use bullet points for easy scanning",
                "Include social proof (testimonials, reviews, case studies)",
                "Address objections in FAQ section",
            ],
            "call_to_action": [
                "Make CTAs stand out visually",
                "Use action-oriented language",
                "Create a sense of urgency",
                "Reduce friction (minimize form fields)",
                "Include CTAs throughout the page",
                "Consider offering a lead magnet",
            ],
            "seo": [
                "Include target keywords in headline, subheads, and content",
                "Optimize meta title and description",
                "Use descriptive alt text for images",
                "Ensure proper heading structure (H1, H2, H3)",
                "Optimize page load speed",
            ],
        }

            return best_practices

def generate_headline_variations(self, count: int = 5) -> List[str]:
        """
        Generate variations of the landing page headline.

Args:
            count: Number of variations to generate

Returns:
            List of headline variations
        """
        variations = [self.title]  # Start with the original title

# Generate variations based on common landing page headline patterns
        patterns = [
            f"Introducing {self.title}: The Ultimate Solution for {self.target_persona['name']}s",
            f"How {self.target_persona['name']}s Are {self.target_persona['goals'][0] if self.target_persona['goals'] else 'Achieving Success'} With {self.title}",
            f"Say Goodbye to {self.target_persona['pain_points'][0] if self.target_persona['pain_points'] else 'Challenges'}: Introducing {self.title}",
            f"{self.title}: {len(self.key_points)}X {self.target_persona['goals'][0] if self.target_persona['goals'] else 'Better Results'} for {self.target_persona['name']}s",
            f"The Smart {self.target_persona['name']}'s Guide to {self.title}",
            f"Struggling with {self.target_persona['pain_points'][0] if self.target_persona['pain_points'] else 'Challenges'}? Discover {self.title}",
            f"Unlock Your {self.target_persona['goals'][0] if self.target_persona['goals'] else 'Potential'} with {self.title}",
        ]

# Add variations until we reach the requested count
        for pattern in patterns:
            if len(variations) < count:
                variations.append(pattern)
            else:
                break

            return variations[:count]


class ProductDescriptionTemplate(ContentTemplate):
    """
    Template for creating product description content.
    """

def __init__(
        self,
        title: str,
        target_persona: Dict[str, Any],
        key_points: List[str],
        tone: Optional[str] = "professional",
        call_to_action: Optional[str] = None,
        product_features: Optional[List[Dict[str, str]]] = None,
        product_specs: Optional[Dict[str, str]] = None,
        product_type: str = "software",
        include_pricing: bool = True,
    ):
        """
        Initialize a product description template.

Args:
            title: Title/name of the product
            target_persona: The target user persona for this product
            key_points: List of key points to cover (benefits)
            tone: Optional tone for the product description
            call_to_action: Optional call to action
            product_features: Optional list of product features with descriptions
            product_specs: Optional dictionary of product specifications
            product_type: Type of product (software, physical, service)
            include_pricing: Whether to include pricing section
        """
        super().__init__(title, target_persona, key_points, tone, call_to_action)
        self.content_type = "product_description"
        self.product_features = product_features or []
        self.product_specs = product_specs or {}
        self.product_type = product_type
        self.include_pricing = include_pricing

def generate_outline(self) -> Dict[str, Any]:
        """
        Generate an outline for the product description.

Returns:
            Dictionary with product description outline details
        """
        # Create sections for the product description
        sections = []

# Add product overview section
        sections.append(
            {
                "section_type": "overview",
                "title": "Product Overview",
                "description": "Brief overview of the product",
                "content": f"{self.title} is a {self.product_type} designed specifically for {self.target_persona['name']}s. "
                f"It helps you {self.target_persona['goals'][0] if self.target_persona['goals'] else 'achieve your goals'} "
                f"while addressing {self.target_persona['pain_points'][0] if self.target_persona['pain_points'] else 'your challenges'}.",
            }
        )

# Add key benefits section
        benefit_items = []
        for point in self.key_points:
            benefit_items.append(
                {
                    "title": point,
                    "description": f"Description of how {point} benefits the user",
                }
            )

sections.append(
            {
                "section_type": "benefits",
                "title": "Key Benefits",
                "description": "Highlight the key benefits of the product",
                "content": "## Key Benefits\n\n"
                + "\n".join(
                    [
                        f"- **{item['title']}**: {item['description']}"
                        for item in benefit_items
                    ]
                ),
            }
        )

# Add features section if features are provided
        if self.product_features:
            feature_content = "## Features\n\n"
            for feature in self.product_features:
                feature_content += f"- **{feature.get('name', 'Feature')}**: {feature.get('description', 'Description')}\n"

sections.append(
                {
                    "section_type": "features",
                    "title": "Features",
                    "description": "Detail the features of the product",
                    "content": feature_content,
                }
            )

# Add specifications section if specs are provided
        if self.product_specs:
            spec_content = "## Specifications\n\n"
            for key, value in self.product_specs.items():
                spec_content += f"- **{key}**: {value}\n"

sections.append(
                {
                    "section_type": "specifications",
                    "title": "Specifications",
                    "description": "Technical specifications of the product",
                    "content": spec_content,
                }
            )

# Add use cases section
        use_cases = []
        for i, goal in enumerate(self.target_persona.get("goals", [])[:3]):
            use_cases.append(
                f"- **Use Case {i+1}**: How {self.title} helps {self.target_persona['name']}s {goal.lower()}"
            )

if use_cases:
            sections.append(
                {
                    "section_type": "use_cases",
                    "title": "Use Cases",
                    "description": "Examples of how the product can be used",
                    "content": "## Use Cases\n\n" + "\n".join(use_cases),
                }
            )

# Add pricing section if enabled
        if self.include_pricing:
            sections.append(
                {
                    "section_type": "pricing",
                    "title": "Pricing",
                    "description": "Pricing information",
                    "content": "## Pricing\n\nContact us for pricing information or visit our pricing page.",
                }
            )

# Add call to action section
        if self.call_to_action:
            sections.append(
                {
                    "section_type": "call_to_action",
                    "title": "Call to Action",
                    "description": "Call to action for the product",
                    "content": f"## Get Started\n\n{self.call_to_action}",
                }
            )

# Create the outline
        outline = {
            "id": self.id,
            "title": self.title,
            "content_type": self.content_type,
            "product_type": self.product_type,
            "target_persona": self.target_persona["name"],
            "tone": self.tone,
            "sections": sections,
            "created_at": self.created_at,
        }

            return outline

def get_product_description_best_practices(self) -> Dict[str, List[str]]:
        """
        Get best practices for product descriptions.

Returns:
            Dictionary with product description best practices
        """
        best_practices = {
            "general": [
                "Focus on benefits, not just features",
                "Use the language your customers use",
                "Address pain points directly",
                "Keep it scannable with bullet points and short paragraphs",
                "Include social proof when possible",
            ],
            "structure": [
                "Start with a compelling overview",
                "Highlight key benefits early",
                "Detail features with explanations of why they matter",
                "Include specifications in an easy-to-scan format",
                "End with a clear call to action",
            ],
            "language": [
                f"Maintain a consistent {self.tone} tone throughout",
                "Use active voice and present tense",
                "Be specific and avoid vague claims",
                "Use sensory and emotional language",
                "Address the reader directly ('you')",
            ],
            "seo": [
                "Include relevant keywords naturally",
                "Use descriptive subheadings",
                "Optimize product title for search",
                "Include product specifications in a structured format",
                "Consider adding FAQ content for long-tail keywords",
            ],
        }

# Add product type specific best practices
        if self.product_type == "software":
            best_practices["software_specific"] = [
                "Highlight compatibility with different systems",
                "Mention integration capabilities",
                "Address security and privacy concerns",
                "Explain the onboarding/setup process",
                "Mention support and update policies",
            ]
        elif self.product_type == "physical":
            best_practices["physical_specific"] = [
                "Include dimensions and materials",
                "Address durability and maintenance",
                "Mention shipping and delivery information",
                "Include care instructions",
                "Consider adding unboxing experience details",
            ]
        elif self.product_type == "service":
            best_practices["service_specific"] = [
                "Clearly explain the service process",
                "Mention timeframes and deliverables",
                "Address qualifications and expertise",
                "Explain how the service is delivered",
                "Include information about support and follow-up",
            ]

            return best_practices


class CaseStudyTemplate(ContentTemplate):
    """
    Template for creating case study content.
    """

def __init__(
        self,
        title: str,
        target_persona: Dict[str, Any],
        key_points: List[str],
        tone: Optional[str] = "professional",
        call_to_action: Optional[str] = None,
        client_name: str = "Client Name",
        client_industry: Optional[str] = None,
        challenge: Optional[str] = None,
        solution: Optional[str] = None,
        results: Optional[List[str]] = None,
        include_testimonial: bool = True,
    ):
        """
        Initialize a case study template.

Args:
            title: Title of the case study
            target_persona: The target user persona for this case study
            key_points: List of key points to cover
            tone: Optional tone for the case study
            call_to_action: Optional call to action
            client_name: Name of the client featured in the case study
            client_industry: Optional industry of the client
            challenge: Optional description of the client's challenge
            solution: Optional description of the solution provided
            results: Optional list of results achieved
            include_testimonial: Whether to include a testimonial section
        """
        super().__init__(title, target_persona, key_points, tone, call_to_action)
        self.content_type = "case_study"
        self.client_name = client_name
        self.client_industry = client_industry or f"{target_persona['name']} industry"
        self.challenge = (
            challenge
            or f"The {client_name} team was struggling with {target_persona['pain_points'][0] if target_persona['pain_points'] else 'significant challenges'}."
        )
        self.solution = (
            solution or f"We implemented {title} to address their specific needs."
        )
        self.results = results or [
            f"Achieved {target_persona['goals'][0] if target_persona['goals'] else 'significant improvements'}"
        ]
        self.include_testimonial = include_testimonial

def generate_outline(self) -> Dict[str, Any]:
        """
        Generate an outline for the case study.

Returns:
            Dictionary with case study outline details
        """
        # Create sections for the case study
        sections = []

# Add executive summary section
        sections.append(
            {
                "section_type": "executive_summary",
                "title": "Executive Summary",
                "description": "Brief overview of the case study",
                "content": f"This case study explores how {self.client_name}, a {self.client_industry} company, "
                f"overcame {self.target_persona['pain_points'][0] if self.target_persona['pain_points'] else 'significant challenges'} "
                f"and achieved {self.target_persona['goals'][0] if self.target_persona['goals'] else 'impressive results'} "
                f"with {self.title}.",
            }
        )

# Add client background section
        sections.append(
            {
                "section_type": "client_background",
                "title": "About the Client",
                "description": "Background information about the client",
                "content": f"## About {self.client_name}\n\n"
                f"{self.client_name} is a {self.client_industry} company that [client description]. "
                f"As a {self.target_persona['name']}, they faced unique challenges in their industry.",
            }
        )

# Add challenge section
        sections.append(
            {
                "section_type": "challenge",
                "title": "The Challenge",
                "description": "Description of the client's challenge",
                "content": f"## The Challenge\n\n{self.challenge}\n\n"
                "Specifically, they were struggling with:\n\n"
                + "\n".join(
                    [
                        f"- {point}"
                        for point in self.target_persona.get(
                            "pain_points", ["Significant industry challenges"]
                        )
                    ]
                ),
            }
        )

# Add solution section
        sections.append(
            {
                "section_type": "solution",
                "title": "The Solution",
                "description": "Description of the solution provided",
                "content": f"## The Solution\n\n{self.solution}\n\n"
                "Our approach included:\n\n"
                + "\n".join([f"- {point}" for point in self.key_points]),
            }
        )

# Add implementation section
        sections.append(
            {
                "section_type": "implementation",
                "title": "Implementation Process",
                "description": "Description of how the solution was implemented",
                "content": "## Implementation Process\n\n"
                f"The implementation of {self.title} for {self.client_name} followed these key steps:\n\n"
                f"1. **Discovery and Analysis**: We conducted a thorough analysis of {self.client_name}'s needs and challenges.\n\n"
                "2. **Customized Solution Design**: We designed a tailored solution based on their specific requirements.\n\n"
                "3. **Implementation**: Our team implemented the solution with minimal disruption to their operations.\n\n"
                "4. **Training and Onboarding**: We provided comprehensive training to ensure smooth adoption.\n\n"
                "5. **Ongoing Support**: We continue to provide support and optimization.",
            }
        )

# Add results section
        results_content = f"## Results\n\nAfter implementing {self.title}, {self.client_name} achieved the following results:\n\n"
        for result in self.results:
            results_content += f"- {result}\n"

sections.append(
            {
                "section_type": "results",
                "title": "Results",
                "description": "Description of the results achieved",
                "content": results_content,
            }
        )

# Add testimonial section if enabled
        if self.include_testimonial:
            sections.append(
                {
                    "section_type": "testimonial",
                    "title": "Client Testimonial",
                    "description": "Testimonial from the client",
                    "content": f"## What {self.client_name} Says\n\n"
                    f'> "{self.title} has been a game-changer for our team. '
                    f"We've seen significant improvements in {self.target_persona['goals'][0] if self.target_persona['goals'] else 'our operations'} "
                    f"and would highly recommend this solution to other {self.target_persona['name']}s.\"\n\n"
                    "**[Client Representative Name]**\n"
                    f"[Client Representative Title], {self.client_name}",
                }
            )

# Add conclusion section with call to action
        conclusion_content = "## Conclusion\n\n"
        conclusion_content += f"This case study demonstrates how {self.title} can help {self.target_persona['name']}s "
        conclusion_content += f"overcome {self.target_persona['pain_points'][0] if self.target_persona['pain_points'] else 'challenges'} "
        conclusion_content += f"and achieve {self.target_persona['goals'][0] if self.target_persona['goals'] else 'their goals'}. "

if self.call_to_action:
            conclusion_content += f"\n\n{self.call_to_action}"

sections.append(
            {
                "section_type": "conclusion",
                "title": "Conclusion",
                "description": "Conclusion and call to action",
                "content": conclusion_content,
            }
        )

# Create the outline
        outline = {
            "id": self.id,
            "title": self.title,
            "content_type": self.content_type,
            "client_name": self.client_name,
            "client_industry": self.client_industry,
            "target_persona": self.target_persona["name"],
            "tone": self.tone,
            "sections": sections,
            "created_at": self.created_at,
        }

            return outline

def get_case_study_best_practices(self) -> Dict[str, List[str]]:
        """
        Get best practices for case studies.

Returns:
            Dictionary with case study best practices
        """
        best_practices = {
            "structure": [
                "Start with a compelling executive summary",
                "Clearly define the challenge, solution, and results",
                "Use a narrative structure with a clear beginning, middle, and end",
                "Include specific, measurable results",
                "End with a strong call to action",
            ],
            "content": [
                "Focus on the client's journey and transformation",
                "Include specific details and metrics to build credibility",
                "Use direct quotes from the client",
                "Explain how your solution addressed specific pain points",
                "Connect the results to the initial challenges",
            ],
            "formatting": [
                "Use headers and subheaders to organize content",
                "Include visuals like charts or before/after comparisons",
                "Highlight key metrics and results",
                "Keep paragraphs short and scannable",
                "Use bullet points for lists of features or benefits",
            ],
            "storytelling": [
                "Create an emotional connection through storytelling",
                "Show the human impact, not just business metrics",
                "Present a clear problem-solution-outcome narrative",
                "Include challenges faced during implementation and how they were overcome",
                "Make the client the hero of the story, not your product",
            ],
            "distribution": [
                "Create multiple formats (PDF, web page, slide deck)",
                "Share on relevant industry platforms",
                "Use in sales presentations and proposals",
                "Create social media snippets from key points",
                "Include in email marketing campaigns",
            ],
        }

            return best_practices

def generate_title_variations(self, count: int = 5) -> List[str]:
        """
        Generate variations of the case study title.

Args:
            count: Number of variations to generate

Returns:
            List of title variations
        """
        variations = [self.title]  # Start with the original title

# Generate variations based on common case study title patterns
        patterns = [
            f"How {self.client_name} {self.target_persona['goals'][0] if self.target_persona['goals'] else 'Achieved Success'} with {self.title}",
            f"Case Study: {self.client_name} Overcomes {self.target_persona['pain_points'][0] if self.target_persona['pain_points'] else 'Challenges'} with {self.title}",
            f"{self.client_name} Success Story: Transforming {self.client_industry} with {self.title}",
            f"From Challenge to Success: {self.client_name}'s Journey with {self.title}",
            f"{self.client_industry} Case Study: {self.client_name} + {self.title}",
            f"Achieving {self.results[0] if self.results else 'Results'}: {self.client_name}'s {self.title} Implementation",
            f"{self.client_name} Increases {self.target_persona['goals'][0] if self.target_persona['goals'] else 'Efficiency'} with {self.title}",
        ]

# Add variations until we reach the requested count
        for pattern in patterns:
            if len(variations) < count:
                variations.append(pattern)
            else:
                break

            return variations[:count]


class TestimonialTemplate(ContentTemplate):
    """
    Template for creating testimonial content.
    """

def __init__(
        self,
        title: str,
        target_persona: Dict[str, Any],
        key_points: List[str],
        tone: Optional[str] = "authentic",
        call_to_action: Optional[str] = None,
        client_name: str = "Client Name",
        client_title: Optional[str] = None,
        client_company: Optional[str] = None,
        testimonial_type: str = "product",
        include_headshot: bool = True,
    ):
        """
        Initialize a testimonial template.

Args:
            title: Title/subject of the testimonial
            target_persona: The target user persona for this testimonial
            key_points: List of key points to cover in the testimonial
            tone: Optional tone for the testimonial
            call_to_action: Optional call to action
            client_name: Name of the client giving the testimonial
            client_title: Optional title/position of the client
            client_company: Optional company of the client
            testimonial_type: Type of testimonial (product, service, case study)
            include_headshot: Whether to include a client headshot
        """
        super().__init__(title, target_persona, key_points, tone, call_to_action)
        self.content_type = "testimonial"
        self.client_name = client_name
        self.client_title = client_title or f"{target_persona['name']}"
        self.client_company = client_company or "Company Name"
        self.testimonial_type = testimonial_type
        self.include_headshot = include_headshot

def generate_outline(self) -> Dict[str, Any]:
        """
        Generate an outline for the testimonial.

Returns:
            Dictionary with testimonial outline details
        """
        # Create the testimonial content
        testimonial_content = self._generate_testimonial_content()

# Create the client attribution
        attribution = f"{self.client_name}"
        if self.client_title:
            attribution += f", {self.client_title}"
        if self.client_company:
            attribution += f", {self.client_company}"

# Create the outline
        outline = {
            "id": self.id,
            "title": self.title,
            "content_type": self.content_type,
            "testimonial_type": self.testimonial_type,
            "client_name": self.client_name,
            "client_title": self.client_title,
            "client_company": self.client_company,
            "target_persona": self.target_persona["name"],
            "tone": self.tone,
            "testimonial_content": testimonial_content,
            "attribution": attribution,
            "include_headshot": self.include_headshot,
            "created_at": self.created_at,
        }

# Add headshot recommendation if enabled
        if self.include_headshot:
            outline["headshot_recommendation"] = {
                "description": f"Professional headshot of {self.client_name}",
                "size": "200 x 200 pixels",
                "format": "High-quality JPEG or PNG with transparent background",
                "style": "Professional, friendly, and approachable",
            }

# Add formatting variations
        outline["format_variations"] = self._generate_format_variations()

            return outline

def _generate_testimonial_content(self) -> str:
        """Generate the testimonial content based on key points and type."""
        # Start with an opening statement based on testimonial type
        if self.testimonial_type == "product":
            opening = f"{self.title} has been a game-changer for our team. "
        elif self.testimonial_type == "service":
            opening = f"Working with the team on {self.title} has been an exceptional experience. "
        elif self.testimonial_type == "case_study":
            opening = f"Our experience implementing {self.title} has transformed our business. "
        else:
            opening = f"{self.title} has made a significant impact on our work. "

# Add statements based on key points
        middle = ""
        for point in self.key_points:
            middle += f"Thanks to this {self.testimonial_type}, we've been able to {point.lower()}. "

# Add a statement about pain points being solved
        if self.target_persona.get("pain_points"):
            pain_point = self.target_persona["pain_points"][0]
            middle += f"Before, we struggled with {pain_point.lower()}, but now that's no longer an issue. "

# Add a statement about goals being achieved
        if self.target_persona.get("goals"):
            goal = self.target_persona["goals"][0]
            middle += (
                f"We're now able to {goal.lower()} more effectively than ever before. "
            )

# Add a closing statement
        if self.testimonial_type == "product":
            closing = f"I would highly recommend {self.title} to any {self.target_persona['name']} looking to improve their results."
        elif self.testimonial_type == "service":
            closing = f"The team's expertise in {self.title} has been invaluable, and I wouldn't hesitate to recommend their services."
        elif self.testimonial_type == "case_study":
            closing = f"The results speak for themselves, and we're extremely satisfied with our decision to implement {self.title}."
        else:
            closing = f"Overall, our experience with {self.title} has exceeded our expectations in every way."

# Combine all parts
        testimonial = opening + middle + closing

            return testimonial

def _generate_format_variations(self) -> Dict[str, Any]:
        """Generate different format variations of the testimonial."""
        # Get the basic testimonial content
        full_testimonial = self._generate_testimonial_content()

# Create a short version (1-2 sentences)
        sentences = full_testimonial.split(". ")
        short_version = ". ".join(sentences[:2]) + "."
        if short_version[-1] != ".":
            short_version += "."

# Create a medium version (about half the full version)
        medium_length = max(len(sentences) // 2, 2)
        medium_version = ". ".join(sentences[:medium_length]) + "."
        if medium_version[-1] != ".":
            medium_version += "."

# Create a one-liner focused on the main benefit
        if self.key_points:
            one_liner = f'"{self.title} helped us {self.key_points[0].lower()}." - {self.client_name}, {self.client_company}'
        else:
            one_liner = f'"{self.title} has been a game-changer for our team." - {self.client_name}, {self.client_company}'

# Create a quote highlight (key quote from the testimonial)
        if len(sentences) > 2:
            highlight = sentences[1]
            if highlight[-1] != ".":
                highlight += "."
        else:
            highlight = short_version

            return {
            "full_testimonial": full_testimonial,
            "short_version": short_version,
            "medium_version": medium_version,
            "one_liner": one_liner,
            "highlight_quote": highlight,
            "attribution": f"{self.client_name}, {self.client_title}, {self.client_company}",
        }

def get_testimonial_best_practices(self) -> Dict[str, List[str]]:
        """
        Get best practices for testimonials.

Returns:
            Dictionary with testimonial best practices
        """
        best_practices = {
            "content": [
                "Focus on specific results and benefits",
                "Include concrete metrics when possible",
                "Address specific pain points that were solved",
                "Keep it authentic and conversational",
                "Include before/after comparisons",
            ],
            "structure": [
                "Start with a strong opening statement",
                "Focus on 1-3 key benefits in the middle",
                "End with a recommendation or conclusion",
                "Keep it concise (2-4 sentences for most uses)",
                "Include full name, title, and company for credibility",
            ],
            "presentation": [
                "Use pull quotes to highlight key statements",
                "Include a professional headshot when possible",
                "Consider video testimonials for higher impact",
                "Format with quotation marks and proper attribution",
                "Group testimonials by industry or use case",
            ],
            "collection": [
                "Ask specific questions to guide the testimonial",
                "Request testimonials at moments of success",
                "Make it easy for clients to provide testimonials",
                "Get permission to edit for clarity and length",
                "Always get approval on the final version",
            ],
            "usage": [
                "Place testimonials strategically near calls to action",
                "Rotate testimonials to keep content fresh",
                "Use different formats for different channels",
                "Pair testimonials with relevant product features",
                "Create testimonial clusters for social proo",
            ],
        }

            return best_practices

def generate_request_template(self) -> Dict[str, Any]:
        """
        Generate a template for requesting testimonials from clients.

Returns:
            Dictionary with testimonial request template
        """
        request_template = {
            "email_subject": f"Request for Feedback on Your Experience with {self.title}",
            "email_body": """
Dear {self.client_name},

I hope this email finds you well. We value your partnership and would love to hear about your experience with {self.title}.

Would you be willing to share a brief testimonial about how {self.title} has helped your team? Your feedback would be incredibly valuable to us and helpful for other {self.target_persona['name']}s considering our solution.

To make this as easy as possible, I've included a few questions below that might help guide your response:

1. What challenges were you facing before using {self.title}?
2. How has {self.title} helped you address these challenges?
3. What specific results or benefits have you experienced?
4. What would you tell someone who is considering {self.title}?

A few sentences would be perfect, but feel free to write as much or as little as you'd like. We may edit for length while preserving the meaning, and we'll be sure to get your approval on the final version before using it.

If you're comfortable, we'd also love to include your photo alongside your testimonial. This adds a personal touch that resonates with potential clients.

Thank you for considering this request. Your insights are invaluable to us.

Best regards,
[Your Name]
[Your Title]
            """,
            "follow_up_email": """
Dear {self.client_name},

I'm just following up on my previous email requesting your feedback on {self.title}. We would greatly value your perspective and would be honored to feature your testimonial.

If it's easier, I'd be happy to schedule a quick 10-minute call to capture your thoughts directly.

Thank you for your consideration.

Best regards,
[Your Name]
[Your Title]
            """,
            "thank_you_email": """
Dear {self.client_name},

Thank you so much for providing your testimonial about {self.title}! We truly appreciate you taking the time to share your experience.

I've attached a draft of how we'd like to use your testimonial. Please review it and let me know if you'd like to make any changes or adjustments.

Once again, thank you for your support and partnership.

Best regards,
[Your Name]
[Your Title]
            """,
        }

            return request_template