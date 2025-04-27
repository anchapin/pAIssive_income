"""
Content generators for the pAIssive Income project.

This module provides classes for generating marketing content based on templates,
including text content, social media content, and email marketing content.
"""

from typing import Dict, List, Any, Optional, Union, Tuple, Type
from abc import ABC, abstractmethod
import uuid
import json
import datetime
import re
import random

from .content_templates import (
    ContentTemplate,
    BlogPostTemplate,
    SocialMediaTemplate,
    EmailNewsletterTemplate,
    VideoScriptTemplate,
    LandingPageTemplate,
    ProductDescriptionTemplate,
    CaseStudyTemplate,
    TestimonialTemplate
)
from .user_personas import PersonaCreator


class ContentGenerator(ABC):
    """
    Abstract base class for content generators.

    This class provides common functionality for all content generators,
    including configuration, template management, and content generation.
    """

    def __init__(
        self,
        template: Optional[ContentTemplate] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a content generator.

        Args:
            template: Optional content template to use
            config: Optional configuration dictionary
        """
        self.id = str(uuid.uuid4())
        self.template = template
        self.config = config or {}
        self.created_at = datetime.datetime.now().isoformat()
        self.content_history = []

    def set_template(self, template: ContentTemplate) -> None:
        """
        Set the content template to use.

        Args:
            template: Content template to use
        """
        self.template = template

    def set_config(self, config: Dict[str, Any]) -> None:
        """
        Set the configuration dictionary.

        Args:
            config: Configuration dictionary
        """
        self.config = config

    def update_config(self, key: str, value: Any) -> None:
        """
        Update a specific configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value

    @abstractmethod
    def generate_content(self) -> Dict[str, Any]:
        """
        Generate content based on the template and configuration.

        Returns:
            Dictionary with generated content
        """
        pass

    def save_content_history(self, content: Dict[str, Any]) -> None:
        """
        Save generated content to history.

        Args:
            content: Generated content
        """
        # Add timestamp and ID to content
        content_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "content": content
        }

        # Add to history
        self.content_history.append(content_entry)

    def get_content_history(self) -> List[Dict[str, Any]]:
        """
        Get the content generation history.

        Returns:
            List of content generation history entries
        """
        return self.content_history

    def clear_content_history(self) -> None:
        """Clear the content generation history."""
        self.content_history = []

    def get_last_generated_content(self) -> Optional[Dict[str, Any]]:
        """
        Get the last generated content.

        Returns:
            Last generated content or None if no content has been generated
        """
        if not self.content_history:
            return None

        return self.content_history[-1]["content"]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the content generator to a dictionary.

        Returns:
            Dictionary representation of the content generator
        """
        return {
            "id": self.id,
            "template_id": self.template.id if self.template else None,
            "template_type": self.template.__class__.__name__ if self.template else None,
            "config": self.config,
            "created_at": self.created_at,
            "content_history_count": len(self.content_history)
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the content generator to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the content generator
        """
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def get_generator_for_template(
        cls,
        template: ContentTemplate,
        config: Optional[Dict[str, Any]] = None
    ) -> 'ContentGenerator':
        """
        Get the appropriate generator for a given template.

        Args:
            template: Content template
            config: Optional configuration dictionary

        Returns:
            Content generator instance
        """
        # Map template types to generator classes
        generator_map = {
            BlogPostTemplate: BlogPostGenerator,
            SocialMediaTemplate: SocialMediaPostGenerator,
            EmailNewsletterTemplate: EmailNewsletterGenerator,
            VideoScriptTemplate: VideoScriptGenerator,
            LandingPageTemplate: LandingPageGenerator,
            ProductDescriptionTemplate: ProductDescriptionGenerator,
            CaseStudyTemplate: CaseStudyGenerator,
            TestimonialTemplate: TestimonialGenerator
        }

        # Get the generator class for the template
        generator_class = generator_map.get(template.__class__)

        if not generator_class:
            raise ValueError(f"No generator found for template type: {template.__class__.__name__}")

        # Create and return the generator
        return generator_class(template, config)


class GeneratorConfig:
    """
    Class for managing content generator configurations.

    This class provides methods for creating, validating, and managing
    content generator configurations.
    """

    @staticmethod
    def create_default_config() -> Dict[str, Any]:
        """
        Create a default configuration dictionary.

        Returns:
            Default configuration dictionary
        """
        return {
            "creativity_level": 0.7,  # 0.0 to 1.0, higher means more creative
            "tone_consistency": 0.8,  # 0.0 to 1.0, higher means more consistent
            "max_length": 2000,  # Maximum content length in characters
            "min_length": 500,  # Minimum content length in characters
            "include_images": True,  # Whether to include image placeholders
            "include_links": True,  # Whether to include link placeholders
            "seo_optimization": True,  # Whether to optimize for SEO
            "target_reading_level": "intermediate",  # beginner, intermediate, advanced
            "language": "en-US",  # Content language
            "content_format": "markdown",  # markdown, html, plain_text
            "include_metadata": True,  # Whether to include metadata
            "use_ai_enhancement": True,  # Whether to use AI enhancement
            "ai_enhancement_level": 0.5,  # 0.0 to 1.0, higher means more AI enhancement
            "include_analytics_tags": False,  # Whether to include analytics tags
            "include_call_to_action": True,  # Whether to include call to action
            "call_to_action_strength": 0.7,  # 0.0 to 1.0, higher means stronger CTA
            "personalization_level": 0.5,  # 0.0 to 1.0, higher means more personalization
            "content_freshness": 0.8,  # 0.0 to 1.0, higher means more fresh content
            "content_uniqueness": 0.9,  # 0.0 to 1.0, higher means more unique content
            "content_relevance": 0.9,  # 0.0 to 1.0, higher means more relevant content
            "content_engagement": 0.8,  # 0.0 to 1.0, higher means more engaging content
            "content_conversion": 0.7,  # 0.0 to 1.0, higher means more conversion-focused
            "content_authority": 0.6,  # 0.0 to 1.0, higher means more authoritative
            "content_trustworthiness": 0.9,  # 0.0 to 1.0, higher means more trustworthy
            "content_expertise": 0.8,  # 0.0 to 1.0, higher means more expert
            "timestamp": datetime.datetime.now().isoformat()
        }

    @staticmethod
    def create_config_for_template(template: ContentTemplate) -> Dict[str, Any]:
        """
        Create a configuration dictionary for a specific template.

        Args:
            template: Content template

        Returns:
            Configuration dictionary for the template
        """
        # Start with default config
        config = GeneratorConfig.create_default_config()

        # Customize based on template type
        if isinstance(template, BlogPostTemplate):
            config.update({
                "max_length": 5000,
                "min_length": 1000,
                "include_images": True,
                "include_links": True,
                "seo_optimization": True,
                "target_reading_level": "intermediate",
                "content_format": "markdown",
                "include_table_of_contents": True,
                "include_featured_image": True,
                "include_meta_description": True,
                "include_categories": True,
                "include_tags": True,
                "include_author_bio": True,
                "include_related_posts": True,
                "include_social_sharing": True,
                "include_comments": True,
                "include_internal_links": True,
                "include_external_links": True,
                "include_statistics": True,
                "include_quotes": True,
                "include_examples": True,
                "include_case_studies": True,
                "include_action_steps": True,
                "include_summary": True,
                "include_faq": True
            })
        elif isinstance(template, SocialMediaTemplate):
            config.update({
                "max_length": 280 if template.platform == "twitter" else 2200,
                "min_length": 50,
                "include_images": True,
                "include_links": True,
                "seo_optimization": False,
                "target_reading_level": "beginner",
                "content_format": "plain_text",
                "include_hashtags": True,
                "include_emojis": True,
                "include_mentions": True,
                "include_trending_topics": True,
                "include_call_to_action": True,
                "include_engagement_question": True,
                "include_image_alt_text": True,
                "include_link_preview": True,
                "include_geolocation": False,
                "include_poll": False,
                "include_carousel": False,
                "include_story": False,
                "include_reel": False,
                "include_live": False,
                "include_event": False,
                "include_product_tag": False,
                "include_shop": False,
                "include_fundraiser": False,
                "include_collaboration": False
            })
        elif isinstance(template, EmailNewsletterTemplate):
            config.update({
                "max_length": 3000,
                "min_length": 500,
                "include_images": True,
                "include_links": True,
                "seo_optimization": False,
                "target_reading_level": "intermediate",
                "content_format": "html",
                "include_subject_line": True,
                "include_preview_text": True,
                "include_header": True,
                "include_footer": True,
                "include_unsubscribe_link": True,
                "include_social_links": True,
                "include_company_info": True,
                "include_personalization_tokens": True,
                "include_segmentation": True,
                "include_a_b_testing": True,
                "include_spam_check": True,
                "include_mobile_optimization": True,
                "include_tracking_pixels": True,
                "include_utm_parameters": True,
                "include_plain_text_version": True,
                "include_call_to_action_button": True,
                "include_forward_to_friend": True,
                "include_social_sharing": True,
                "include_preference_center": True
            })
        elif isinstance(template, VideoScriptTemplate):
            config.update({
                "max_length": 10000,
                "min_length": 1000,
                "include_images": False,
                "include_links": False,
                "seo_optimization": True,
                "target_reading_level": "intermediate",
                "content_format": "plain_text",
                "include_intro": True,
                "include_outro": True,
                "include_b_roll": True,
                "include_graphics": True,
                "include_music": True,
                "include_sound_effects": True,
                "include_captions": True,
                "include_timestamps": True,
                "include_scene_descriptions": True,
                "include_camera_angles": True,
                "include_transitions": True,
                "include_special_effects": True,
                "include_props": True,
                "include_wardrobe": True,
                "include_location": True,
                "include_talent": True,
                "include_voiceover": True,
                "include_graphics_overlay": True,
                "include_lower_thirds": True,
                "include_end_screen": True,
                "include_annotations": True,
                "include_cards": True,
                "include_chapters": True
            })
        elif isinstance(template, LandingPageTemplate):
            config.update({
                "max_length": 5000,
                "min_length": 1000,
                "include_images": True,
                "include_links": True,
                "seo_optimization": True,
                "target_reading_level": "beginner",
                "content_format": "html",
                "include_hero_section": True,
                "include_benefits_section": True,
                "include_features_section": True,
                "include_testimonials_section": True,
                "include_pricing_section": True,
                "include_faq_section": True,
                "include_about_section": True,
                "include_contact_section": True,
                "include_call_to_action_section": True,
                "include_social_proof_section": True,
                "include_guarantee_section": True,
                "include_comparison_section": True,
                "include_demo_section": True,
                "include_video_section": True,
                "include_case_study_section": True,
                "include_team_section": True,
                "include_partners_section": True,
                "include_press_section": True,
                "include_blog_section": True,
                "include_newsletter_section": True,
                "include_social_media_section": True,
                "include_trust_badges_section": True,
                "include_live_chat": True,
                "include_exit_intent_popup": True
            })
        elif isinstance(template, ProductDescriptionTemplate):
            config.update({
                "max_length": 2000,
                "min_length": 200,
                "include_images": True,
                "include_links": True,
                "seo_optimization": True,
                "target_reading_level": "beginner",
                "content_format": "html",
                "include_product_name": True,
                "include_product_tagline": True,
                "include_product_overview": True,
                "include_product_features": True,
                "include_product_benefits": True,
                "include_product_specifications": True,
                "include_product_pricing": True,
                "include_product_availability": True,
                "include_product_shipping": True,
                "include_product_warranty": True,
                "include_product_return_policy": True,
                "include_product_reviews": True,
                "include_product_ratings": True,
                "include_product_faqs": True,
                "include_product_videos": True,
                "include_product_images": True,
                "include_product_comparison": True,
                "include_product_bundles": True,
                "include_product_cross_sells": True,
                "include_product_upsells": True,
                "include_product_related": True,
                "include_product_accessories": True,
                "include_product_customization": True,
                "include_product_personalization": True
            })
        elif isinstance(template, CaseStudyTemplate):
            config.update({
                "max_length": 5000,
                "min_length": 1000,
                "include_images": True,
                "include_links": True,
                "seo_optimization": True,
                "target_reading_level": "advanced",
                "content_format": "markdown",
                "include_executive_summary": True,
                "include_client_background": True,
                "include_challenge": True,
                "include_solution": True,
                "include_implementation": True,
                "include_results": True,
                "include_testimonial": True,
                "include_conclusion": True,
                "include_client_logo": True,
                "include_client_quote": True,
                "include_client_photo": True,
                "include_client_video": True,
                "include_data_visualization": True,
                "include_before_after": True,
                "include_timeline": True,
                "include_team": True,
                "include_methodology": True,
                "include_challenges_overcome": True,
                "include_lessons_learned": True,
                "include_next_steps": True,
                "include_related_case_studies": True,
                "include_downloadable_pdf": True,
                "include_contact_information": True
            })
        elif isinstance(template, TestimonialTemplate):
            config.update({
                "max_length": 500,
                "min_length": 50,
                "include_images": True,
                "include_links": False,
                "seo_optimization": False,
                "target_reading_level": "beginner",
                "content_format": "plain_text",
                "include_client_name": True,
                "include_client_title": True,
                "include_client_company": True,
                "include_client_photo": True,
                "include_client_logo": True,
                "include_star_rating": True,
                "include_date": True,
                "include_verification_badge": True,
                "include_social_media_links": True,
                "include_full_testimonial": True,
                "include_short_testimonial": True,
                "include_video_testimonial": False,
                "include_audio_testimonial": False,
                "include_case_study_link": False,
                "include_product_used": True,
                "include_results_achieved": True,
                "include_time_period": True,
                "include_industry": True,
                "include_company_size": True,
                "include_use_case": True,
                "include_challenges_overcome": True,
                "include_decision_factors": True,
                "include_alternative_considered": True,
                "include_recommendation_likelihood": True
            })

        return config

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a configuration dictionary.

        Args:
            config: Configuration dictionary

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required fields
        required_fields = [
            "creativity_level",
            "tone_consistency",
            "max_length",
            "min_length",
            "include_images",
            "include_links",
            "seo_optimization",
            "target_reading_level",
            "language",
            "content_format"
        ]

        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        # Validate field types and values
        if "creativity_level" in config and not (isinstance(config["creativity_level"], (int, float)) and 0 <= config["creativity_level"] <= 1):
            errors.append("creativity_level must be a number between 0 and 1")

        if "tone_consistency" in config and not (isinstance(config["tone_consistency"], (int, float)) and 0 <= config["tone_consistency"] <= 1):
            errors.append("tone_consistency must be a number between 0 and 1")

        if "max_length" in config and not (isinstance(config["max_length"], int) and config["max_length"] > 0):
            errors.append("max_length must be a positive integer")

        if "min_length" in config and not (isinstance(config["min_length"], int) and config["min_length"] >= 0):
            errors.append("min_length must be a non-negative integer")

        if "include_images" in config and not isinstance(config["include_images"], bool):
            errors.append("include_images must be a boolean")

        if "include_links" in config and not isinstance(config["include_links"], bool):
            errors.append("include_links must be a boolean")

        if "seo_optimization" in config and not isinstance(config["seo_optimization"], bool):
            errors.append("seo_optimization must be a boolean")

        if "target_reading_level" in config and config["target_reading_level"] not in ["beginner", "intermediate", "advanced"]:
            errors.append("target_reading_level must be one of: beginner, intermediate, advanced")

        if "language" in config and not isinstance(config["language"], str):
            errors.append("language must be a string")

        if "content_format" in config and config["content_format"] not in ["markdown", "html", "plain_text"]:
            errors.append("content_format must be one of: markdown, html, plain_text")

        # Check min_length <= max_length
        if "min_length" in config and "max_length" in config and config["min_length"] > config["max_length"]:
            errors.append("min_length must be less than or equal to max_length")

        return len(errors) == 0, errors

    @staticmethod
    def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two configuration dictionaries.

        Args:
            base_config: Base configuration dictionary
            override_config: Override configuration dictionary

        Returns:
            Merged configuration dictionary
        """
        # Create a copy of the base config
        merged_config = base_config.copy()

        # Update with override config
        merged_config.update(override_config)

        # Update timestamp
        merged_config["timestamp"] = datetime.datetime.now().isoformat()

        return merged_config


class BlogPostGenerator(ContentGenerator):
    """
    Class for generating blog post content.

    This class provides methods for generating blog post content based on
    a BlogPostTemplate, including title, introduction, sections, and conclusion.
    """

    def __init__(
        self,
        template: Optional[BlogPostTemplate] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a blog post generator.

        Args:
            template: Optional blog post template to use
            config: Optional configuration dictionary
        """
        super().__init__(template, config)

        # Validate template type
        if template is not None and not isinstance(template, BlogPostTemplate):
            raise ValueError(f"Expected BlogPostTemplate, got {template.__class__.__name__}")

        # Set default config if not provided
        if config is None:
            if template is not None:
                self.config = GeneratorConfig.create_config_for_template(template)
            else:
                self.config = GeneratorConfig.create_default_config()

    def validate_template(self) -> Tuple[bool, List[str]]:
        """
        Validate the blog post template.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        if self.template is None:
            return False, ["No template provided"]

        errors = []

        # Check required fields
        if not self.template.title:
            errors.append("Template missing title")

        if not self.template.key_points or len(self.template.key_points) == 0:
            errors.append("Template missing key points")

        if not self.template.target_persona:
            errors.append("Template missing target persona")

        return len(errors) == 0, errors

    def generate_content(self) -> Dict[str, Any]:
        """
        Generate blog post content based on the template and configuration.

        Returns:
            Dictionary with generated blog post content
        """
        # Validate template
        is_valid, errors = self.validate_template()

        if not is_valid:
            raise ValueError(f"Invalid template: {', '.join(errors)}")

        # Generate content
        content = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "template_id": self.template.id,
            "title": self._generate_title(),
            "meta_description": self._generate_meta_description(),
            "introduction": self._generate_introduction(),
            "sections": self._generate_sections(),
            "conclusion": self._generate_conclusion(),
            "call_to_action": self._generate_call_to_action(),
            "tags": self._generate_tags(),
            "categories": self._generate_categories(),
            "featured_image": self._generate_featured_image(),
            "seo_data": self._generate_seo_data()
        }

        # Save to history
        self.save_content_history(content)

        return content

    def _generate_title(self) -> str:
        """
        Generate a blog post title.

        Returns:
            Generated title
        """
        # For now, use the template title
        # In a real implementation, this would generate variations or improvements
        return self.template.title

    def _generate_meta_description(self) -> str:
        """
        Generate a meta description for the blog post.

        Returns:
            Generated meta description
        """
        # Simple implementation for now
        # In a real implementation, this would generate a compelling meta description
        return f"Learn about {self.template.title.lower()} and discover how to implement these strategies for your business."

    def _generate_introduction(self) -> str:
        """
        Generate an introduction for the blog post.

        Returns:
            Generated introduction
        """
        # Simple implementation for now
        # In a real implementation, this would generate a compelling introduction
        persona = self.template.target_persona
        pain_points = persona.get("pain_points", [])
        goals = persona.get("goals", [])

        intro = f"# {self.template.title}\n\n"

        if pain_points:
            intro += f"Are you struggling with {', '.join(pain_points[:-1]) + ' and ' + pain_points[-1] if len(pain_points) > 1 else pain_points[0]}? "

        intro += f"In this article, we'll explore {self.template.title.lower()} and provide actionable insights to help you "

        if goals:
            intro += f"{', '.join(goals[:-1]) + ' and ' + goals[-1] if len(goals) > 1 else goals[0]}. "
        else:
            intro += "achieve your goals. "

        intro += "\n\nLet's dive in!\n\n"

        return intro

    def _generate_sections(self) -> List[Dict[str, Any]]:
        """
        Generate sections for the blog post.

        Returns:
            List of section dictionaries
        """
        sections = []

        for i, key_point in enumerate(self.template.key_points):
            section = {
                "id": str(uuid.uuid4()),
                "title": key_point,
                "content": self._generate_section_content(key_point, i),
                "order": i + 1
            }

            sections.append(section)

        return sections

    def _generate_section_content(self, key_point: str, section_index: int) -> str:
        """
        Generate content for a blog post section.

        Args:
            key_point: Key point for the section
            section_index: Index of the section

        Returns:
            Generated section content
        """
        # Simple implementation for now
        # In a real implementation, this would generate compelling section content
        content = f"## {key_point}\n\n"

        # Generate 2-3 paragraphs for each section
        num_paragraphs = random.randint(2, 3)

        for _ in range(num_paragraphs):
            paragraph = self._generate_paragraph(key_point, section_index)
            content += f"{paragraph}\n\n"

        # Add a subsection for some sections
        if section_index % 2 == 0:
            subsection_title = f"Tips for {key_point.lower()}"
            content += f"### {subsection_title}\n\n"

            # Add bullet points
            content += "Here are some tips to help you:\n\n"

            for i in range(3):
                content += f"* Tip {i+1} for {key_point.lower()}\n"

            content += "\n"

        return content

    def _generate_paragraph(self, key_point: str, section_index: int) -> str:
        """
        Generate a paragraph for a blog post section.

        Args:
            key_point: Key point for the section
            section_index: Index of the section

        Returns:
            Generated paragraph
        """
        # Simple implementation for now
        # In a real implementation, this would generate a compelling paragraph
        return f"This is a paragraph about {key_point.lower()}. It provides valuable information and insights about this topic. The reader will learn important concepts and practical applications related to {key_point.lower()}."

    def _generate_conclusion(self) -> str:
        """
        Generate a conclusion for the blog post.

        Returns:
            Generated conclusion
        """
        # Simple implementation for now
        # In a real implementation, this would generate a compelling conclusion
        conclusion = "## Conclusion\n\n"
        conclusion += f"In this article, we've explored {self.template.title.lower()} and provided actionable insights to help you achieve your goals. "
        conclusion += "By implementing these strategies, you'll be well on your way to success. "
        conclusion += "Remember, consistency is key, and small improvements over time can lead to significant results.\n\n"

        return conclusion

    def _generate_call_to_action(self) -> str:
        """
        Generate a call to action for the blog post.

        Returns:
            Generated call to action
        """
        # Use the template's call to action if available
        if hasattr(self.template, "call_to_action") and self.template.call_to_action:
            cta = self.template.call_to_action
        else:
            cta = "Sign up for our newsletter to get more tips and insights."

        return f"**{cta}**"

    def _generate_tags(self) -> List[str]:
        """
        Generate tags for the blog post.

        Returns:
            List of generated tags
        """
        # Simple implementation for now
        # In a real implementation, this would generate relevant tags
        title_words = self.template.title.lower().split()
        key_point_words = []

        for key_point in self.template.key_points:
            key_point_words.extend(key_point.lower().split())

        # Combine words and remove duplicates
        all_words = title_words + key_point_words
        unique_words = list(set(all_words))

        # Filter out common words
        common_words = ["the", "and", "or", "a", "an", "in", "on", "at", "to", "for", "with", "by", "of", "how"]
        filtered_words = [word for word in unique_words if word not in common_words and len(word) > 3]

        # Limit to 5 tags
        return filtered_words[:5]

    def _generate_categories(self) -> List[str]:
        """
        Generate categories for the blog post.

        Returns:
            List of generated categories
        """
        # Simple implementation for now
        # In a real implementation, this would generate relevant categories
        return ["Marketing", "Content Strategy", "Business Tips"]

    def _generate_featured_image(self) -> Dict[str, Any]:
        """
        Generate a featured image for the blog post.

        Returns:
            Dictionary with featured image information
        """
        # Simple implementation for now
        # In a real implementation, this would generate or suggest a relevant image
        return {
            "url": "https://example.com/placeholder-image.jpg",
            "alt_text": self.template.title,
            "caption": f"Featured image for {self.template.title}"
        }

    def _generate_seo_data(self) -> Dict[str, Any]:
        """
        Generate SEO data for the blog post.

        Returns:
            Dictionary with SEO data
        """
        # Simple implementation for now
        # In a real implementation, this would generate comprehensive SEO data
        return {
            "focus_keyword": self.template.title.lower().split()[0],
            "secondary_keywords": self._generate_tags(),
            "meta_description": self._generate_meta_description(),
            "slug": self._generate_slug(),
            "readability_score": "good",
            "seo_score": "good",
            "word_count": 1500,  # Estimated
            "reading_time": 7  # Estimated in minutes
        }

    def _generate_slug(self) -> str:
        """
        Generate a slug for the blog post.

        Returns:
            Generated slug
        """
        # Simple implementation for now
        # In a real implementation, this would generate a proper slug
        return self.template.title.lower().replace(" ", "-")


# Forward declarations for other generator classes
class SocialMediaPostGenerator(ContentGenerator):
    pass

class EmailNewsletterGenerator(ContentGenerator):
    pass

class VideoScriptGenerator(ContentGenerator):
    pass

class LandingPageGenerator(ContentGenerator):
    pass

class ProductDescriptionGenerator(ContentGenerator):
    """
    Class for generating product description content.

    This class provides methods for generating product description content based on
    a ProductDescriptionTemplate, including overview, features, benefits, and specifications.
    """

    def __init__(
        self,
        template: Optional[ProductDescriptionTemplate] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a product description generator.

        Args:
            template: Optional product description template to use
            config: Optional configuration dictionary
        """
        super().__init__(template, config)

        # Validate template type
        if template is not None and not isinstance(template, ProductDescriptionTemplate):
            raise ValueError(f"Expected ProductDescriptionTemplate, got {template.__class__.__name__}")

        # Set default config if not provided
        if config is None:
            if template is not None:
                self.config = GeneratorConfig.create_config_for_template(template)
            else:
                self.config = GeneratorConfig.create_default_config()

    def validate_template(self) -> Tuple[bool, List[str]]:
        """
        Validate the product description template.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        if self.template is None:
            return False, ["No template provided"]

        errors = []

        # Check required fields
        if not self.template.product_name:
            errors.append("Template missing product name")

        if not self.template.product_features or len(self.template.product_features) == 0:
            errors.append("Template missing product features")

        if not self.template.target_audience:
            errors.append("Template missing target audience")

        return len(errors) == 0, errors

    def generate_content(self) -> Dict[str, Any]:
        """
        Generate product description content based on the template and configuration.

        Returns:
            Dictionary with generated product description content
        """
        # Validate template
        is_valid, errors = self.validate_template()

        if not is_valid:
            raise ValueError(f"Invalid template: {', '.join(errors)}")

        # Generate content
        content = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "template_id": self.template.id,
            "product_name": self.template.product_name,
            "tagline": self._generate_tagline(),
            "overview": self._generate_overview(),
            "features": self._generate_features(),
            "benefits": self._generate_benefits(),
            "specifications": self._generate_specifications(),
            "pricing": self._generate_pricing(),
            "images": self._generate_images(),
            "call_to_action": self._generate_call_to_action(),
            "seo_data": self._generate_seo_data()
        }

        # Save to history
        self.save_content_history(content)

        return content

    def _generate_tagline(self) -> str:
        """
        Generate a tagline for the product.

        Returns:
            Generated tagline
        """
        # For now, use the template tagline if available
        if hasattr(self.template, "tagline") and self.template.tagline:
            return self.template.tagline

        # Simple implementation for now
        # In a real implementation, this would generate a compelling tagline
        return f"The ultimate solution for {self.template.target_audience}"

    def _generate_overview(self) -> str:
        """
        Generate an overview for the product.

        Returns:
            Generated overview
        """
        # Simple implementation for now
        # In a real implementation, this would generate a compelling overview
        overview = f"# {self.template.product_name}\n\n"

        if hasattr(self.template, "tagline") and self.template.tagline:
            overview += f"**{self.template.tagline}**\n\n"

        overview += f"{self.template.product_name} is designed specifically for {self.template.target_audience}. "

        if hasattr(self.template, "product_description") and self.template.product_description:
            overview += f"{self.template.product_description} "

        pain_points = self.template.pain_points if hasattr(self.template, "pain_points") else []

        if pain_points:
            overview += f"It solves common challenges such as {', '.join(pain_points[:-1]) + ' and ' + pain_points[-1] if len(pain_points) > 1 else pain_points[0]}. "

        overview += "\n\n"

        return overview

    def _generate_features(self) -> List[Dict[str, Any]]:
        """
        Generate features for the product.

        Returns:
            List of feature dictionaries
        """
        features = []

        for i, feature in enumerate(self.template.product_features):
            feature_dict = {
                "id": str(uuid.uuid4()),
                "name": feature,
                "description": self._generate_feature_description(feature),
                "order": i + 1
            }

            features.append(feature_dict)

        return features

    def _generate_feature_description(self, feature: str) -> str:
        """
        Generate a description for a product feature.

        Args:
            feature: Feature name

        Returns:
            Generated feature description
        """
        # Simple implementation for now
        # In a real implementation, this would generate a compelling feature description
        return f"This feature provides {feature.lower()} functionality, helping you achieve better results with less effort."

    def _generate_benefits(self) -> List[Dict[str, Any]]:
        """
        Generate benefits for the product.

        Returns:
            List of benefit dictionaries
        """
        benefits = []

        # Use template benefits if available
        template_benefits = self.template.product_benefits if hasattr(self.template, "product_benefits") else []

        # If no benefits are provided, generate from features
        if not template_benefits:
            for feature in self.template.product_features:
                benefit = self._generate_benefit_from_feature(feature)
                benefits.append({
                    "id": str(uuid.uuid4()),
                    "name": benefit,
                    "description": self._generate_benefit_description(benefit)
                })
        else:
            for i, benefit in enumerate(template_benefits):
                benefit_dict = {
                    "id": str(uuid.uuid4()),
                    "name": benefit,
                    "description": self._generate_benefit_description(benefit),
                    "order": i + 1
                }

                benefits.append(benefit_dict)

        return benefits

    def _generate_benefit_from_feature(self, feature: str) -> str:
        """
        Generate a benefit from a product feature.

        Args:
            feature: Feature name

        Returns:
            Generated benefit
        """
        # Simple implementation for now
        # In a real implementation, this would generate a compelling benefit
        benefit_phrases = [
            f"Save time with {feature.lower()}",
            f"Increase efficiency through {feature.lower()}",
            f"Reduce costs by utilizing {feature.lower()}",
            f"Improve results with {feature.lower()}",
            f"Enhance productivity with {feature.lower()}"
        ]

        return random.choice(benefit_phrases)

    def _generate_benefit_description(self, benefit: str) -> str:
        """
        Generate a description for a product benefit.

        Args:
            benefit: Benefit name

        Returns:
            Generated benefit description
        """
        # Simple implementation for now
        # In a real implementation, this would generate a compelling benefit description
        return f"This benefit allows you to {benefit.lower()}, resulting in improved outcomes and greater satisfaction."

    def _generate_specifications(self) -> Dict[str, Any]:
        """
        Generate specifications for the product.

        Returns:
            Dictionary with product specifications
        """
        # Use template specifications if available
        if hasattr(self.template, "product_specifications") and self.template.product_specifications:
            return self.template.product_specifications

        # Simple implementation for now
        # In a real implementation, this would generate relevant specifications
        return {
            "dimensions": "10 x 5 x 2 inches",
            "weight": "1.5 lbs",
            "materials": "High-quality materials",
            "compatibility": "Works with all major platforms",
            "requirements": "No special requirements",
            "warranty": "1-year limited warranty"
        }

    def _generate_pricing(self) -> Dict[str, Any]:
        """
        Generate pricing information for the product.

        Returns:
            Dictionary with pricing information
        """
        # Use template pricing if available
        if hasattr(self.template, "product_pricing") and self.template.product_pricing:
            return self.template.product_pricing

        # Simple implementation for now
        # In a real implementation, this would generate relevant pricing
        return {
            "regular_price": 99.99,
            "sale_price": 79.99,
            "currency": "USD",
            "discount_percentage": 20,
            "subscription_option": True,
            "subscription_price": 9.99,
            "subscription_interval": "month",
            "free_trial": True,
            "free_trial_days": 14,
            "money_back_guarantee": True,
            "money_back_guarantee_days": 30
        }

    def _generate_images(self) -> List[Dict[str, Any]]:
        """
        Generate image information for the product.

        Returns:
            List of image dictionaries
        """
        # Use template images if available
        if hasattr(self.template, "product_images") and self.template.product_images:
            return self.template.product_images

        # Simple implementation for now
        # In a real implementation, this would generate relevant image information
        return [
            {
                "id": str(uuid.uuid4()),
                "url": "https://example.com/product-main.jpg",
                "alt_text": f"{self.template.product_name} - Main Image",
                "caption": f"Main image of {self.template.product_name}",
                "is_primary": True
            },
            {
                "id": str(uuid.uuid4()),
                "url": "https://example.com/product-angle1.jpg",
                "alt_text": f"{self.template.product_name} - Angle 1",
                "caption": f"{self.template.product_name} from another angle",
                "is_primary": False
            },
            {
                "id": str(uuid.uuid4()),
                "url": "https://example.com/product-in-use.jpg",
                "alt_text": f"{self.template.product_name} - In Use",
                "caption": f"{self.template.product_name} being used by a customer",
                "is_primary": False
            }
        ]

    def _generate_call_to_action(self) -> str:
        """
        Generate a call to action for the product.

        Returns:
            Generated call to action
        """
        # Use template call to action if available
        if hasattr(self.template, "call_to_action") and self.template.call_to_action:
            return self.template.call_to_action

        # Simple implementation for now
        # In a real implementation, this would generate a compelling call to action
        cta_phrases = [
            f"Get your {self.template.product_name} today!",
            f"Start using {self.template.product_name} now!",
            f"Try {self.template.product_name} risk-free for 14 days!",
            f"Order now and experience the benefits of {self.template.product_name}!",
            f"Don't miss out on {self.template.product_name} - Order now!"
        ]

        return random.choice(cta_phrases)

    def _generate_seo_data(self) -> Dict[str, Any]:
        """
        Generate SEO data for the product.

        Returns:
            Dictionary with SEO data
        """
        # Simple implementation for now
        # In a real implementation, this would generate comprehensive SEO data
        return {
            "meta_title": self.template.product_name,
            "meta_description": self._generate_meta_description(),
            "focus_keyword": self.template.product_name.lower(),
            "secondary_keywords": self._generate_keywords(),
            "slug": self._generate_slug(),
            "schema_markup": self._generate_schema_markup()
        }

    def _generate_meta_description(self) -> str:
        """
        Generate a meta description for the product.

        Returns:
            Generated meta description
        """
        # Simple implementation for now
        # In a real implementation, this would generate a compelling meta description
        return f"Discover {self.template.product_name}, the ultimate solution for {self.template.target_audience}. Features include {', '.join(self.template.product_features[:3])}. Order now!"

    def _generate_keywords(self) -> List[str]:
        """
        Generate keywords for the product.

        Returns:
            List of generated keywords
        """
        # Simple implementation for now
        # In a real implementation, this would generate relevant keywords
        keywords = [self.template.product_name.lower()]

        # Add target audience
        keywords.append(self.template.target_audience.lower())

        # Add features
        for feature in self.template.product_features:
            keywords.append(feature.lower())

        # Add product type
        if hasattr(self.template, "product_type") and self.template.product_type:
            keywords.append(self.template.product_type.lower())

        # Add category
        if hasattr(self.template, "product_category") and self.template.product_category:
            keywords.append(self.template.product_category.lower())

        return keywords

    def _generate_slug(self) -> str:
        """
        Generate a slug for the product.

        Returns:
            Generated slug
        """
        # Simple implementation for now
        # In a real implementation, this would generate a proper slug
        return self.template.product_name.lower().replace(" ", "-")

    def _generate_schema_markup(self) -> Dict[str, Any]:
        """
        Generate schema markup for the product.

        Returns:
            Dictionary with schema markup
        """
        # Simple implementation for now
        # In a real implementation, this would generate proper schema markup
        pricing = self._generate_pricing()

        return {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": self.template.product_name,
            "description": self._generate_meta_description(),
            "image": "https://example.com/product-main.jpg",
            "brand": {
                "@type": "Brand",
                "name": "Your Brand"
            },
            "offers": {
                "@type": "Offer",
                "url": f"https://example.com/products/{self._generate_slug()}",
                "priceCurrency": pricing["currency"],
                "price": pricing["sale_price"],
                "availability": "https://schema.org/InStock",
                "priceValidUntil": (datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%Y-%m-%d")
            }
        }

class CaseStudyGenerator(ContentGenerator):
    """
    Class for generating case study content.

    This class provides methods for generating case study content based on
    a CaseStudyTemplate, including client background, challenge, solution, and results.
    """

    def __init__(
        self,
        template: Optional[CaseStudyTemplate] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a case study generator.

        Args:
            template: Optional case study template to use
            config: Optional configuration dictionary
        """
        super().__init__(template, config)

        # Validate template type
        if template is not None and not isinstance(template, CaseStudyTemplate):
            raise ValueError(f"Expected CaseStudyTemplate, got {template.__class__.__name__}")

        # Set default config if not provided
        if config is None:
            if template is not None:
                self.config = GeneratorConfig.create_config_for_template(template)
            else:
                self.config = GeneratorConfig.create_default_config()

    def validate_template(self) -> Tuple[bool, List[str]]:
        """
        Validate the case study template.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        if self.template is None:
            return False, ["No template provided"]

        errors = []

        # Check required fields
        if not self.template.title:
            errors.append("Template missing title")

        if not self.template.client_name:
            errors.append("Template missing client name")

        if not self.template.key_points or len(self.template.key_points) == 0:
            errors.append("Template missing key points")

        if not self.template.target_persona:
            errors.append("Template missing target persona")

        return len(errors) == 0, errors

    def generate_content(self) -> Dict[str, Any]:
        """
        Generate case study content based on the template and configuration.

        Returns:
            Dictionary with generated case study content
        """
        # Validate template
        is_valid, errors = self.validate_template()

        if not is_valid:
            raise ValueError(f"Invalid template: {', '.join(errors)}")

        # Generate content
        content = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "template_id": self.template.id,
            "title": self._generate_title(),
            "client_info": self._generate_client_info(),
            "executive_summary": self._generate_executive_summary(),
            "challenge": self._generate_challenge(),
            "solution": self._generate_solution(),
            "implementation": self._generate_implementation(),
            "results": self._generate_results(),
            "testimonial": self._generate_testimonial(),
            "conclusion": self._generate_conclusion(),
            "call_to_action": self._generate_call_to_action(),
            "related_case_studies": self._generate_related_case_studies(),
            "images": self._generate_images(),
            "seo_data": self._generate_seo_data()
        }

        # Save to history
        self.save_content_history(content)

        return content

    def _generate_title(self) -> str:
        """
        Generate a title for the case study.

        Returns:
            Generated title
        """
        # For now, use the template title
        # In a real implementation, this would generate variations or improvements
        return self.template.title

    def _generate_client_info(self) -> Dict[str, Any]:
        """
        Generate client information for the case study.

        Returns:
            Dictionary with client information
        """
        # Use template client information
        client_info = {
            "name": self.template.client_name,
            "industry": self.template.client_industry if hasattr(self.template, "client_industry") else "Industry",
            "size": "Medium-sized company",  # Default value
            "location": "United States",  # Default value
            "website": f"https://www.{self.template.client_name.lower().replace(' ', '')}.com",  # Generated website
            "logo_url": f"https://example.com/logos/{self.template.client_name.lower().replace(' ', '')}.png"  # Generated logo URL
        }

        # Add additional client information if available
        if hasattr(self.template, "client_size"):
            client_info["size"] = self.template.client_size

        if hasattr(self.template, "client_location"):
            client_info["location"] = self.template.client_location

        if hasattr(self.template, "client_website"):
            client_info["website"] = self.template.client_website

        if hasattr(self.template, "client_logo_url"):
            client_info["logo_url"] = self.template.client_logo_url

        return client_info

    def _generate_executive_summary(self) -> str:
        """
        Generate an executive summary for the case study.

        Returns:
            Generated executive summary
        """
        # Simple implementation for now
        # In a real implementation, this would generate a compelling executive summary
        client_name = self.template.client_name
        client_industry = self.template.client_industry if hasattr(self.template, "client_industry") else "their industry"

        summary = f"# {self.template.title}\n\n"
        summary += f"## Executive Summary\n\n"
        summary += f"{client_name}, a leading company in {client_industry}, faced significant challenges with "

        # Add challenges
        if hasattr(self.template, "challenge") and self.template.challenge:
            summary += f"{self.template.challenge.lower()}. "
        else:
            pain_points = self.template.target_persona.get("pain_points", [])
            if pain_points:
                summary += f"{', '.join(pain_points[:-1]) + ' and ' + pain_points[-1] if len(pain_points) > 1 else pain_points[0]}. "
            else:
                summary += "various operational challenges. "

        # Add solution
        if hasattr(self.template, "solution") and self.template.solution:
            summary += f"We implemented {self.template.solution} "
        else:
            summary += f"We implemented a comprehensive solution "

        summary += "to address these challenges. "

        # Add results
        if hasattr(self.template, "results") and self.template.results:
            summary += f"As a result, {client_name} achieved {', '.join(self.template.results[:-1]) + ' and ' + self.template.results[-1] if len(self.template.results) > 1 else self.template.results[0]}."
        else:
            goals = self.template.target_persona.get("goals", [])
            if goals:
                summary += f"As a result, {client_name} was able to {', '.join(goals[:-1]) + ' and ' + goals[-1] if len(goals) > 1 else goals[0]}."
            else:
                summary += f"As a result, {client_name} achieved significant improvements in their operations and business outcomes."

        return summary

    def _generate_challenge(self) -> str:
        """
        Generate a challenge section for the case study.

        Returns:
            Generated challenge section
        """
        # Simple implementation for now
        # In a real implementation, this would generate a compelling challenge section
        client_name = self.template.client_name

        challenge = f"## The Challenge\n\n"

        # Use template challenge if available
        if hasattr(self.template, "challenge") and self.template.challenge:
            challenge += f"{self.template.challenge}\n\n"
        else:
            challenge += f"{client_name} was facing several challenges that were impacting their business performance. "

            pain_points = self.template.target_persona.get("pain_points", [])
            if pain_points:
                challenge += f"These included:\n\n"
                for pain_point in pain_points:
                    challenge += f"- {pain_point}\n"
                challenge += "\n"

            challenge += f"These challenges were causing significant issues for {client_name}, including reduced efficiency, increased costs, and missed opportunities for growth.\n\n"

        return challenge

    def _generate_solution(self) -> str:
        """
        Generate a solution section for the case study.

        Returns:
            Generated solution section
        """
        # Simple implementation for now
        # In a real implementation, this would generate a compelling solution section
        client_name = self.template.client_name

        solution = f"## The Solution\n\n"

        # Use template solution if available
        if hasattr(self.template, "solution") and self.template.solution:
            solution += f"{self.template.solution}\n\n"
        else:
            solution += f"After a thorough analysis of {client_name}'s needs and challenges, we developed a customized solution that addressed their specific requirements. "
            solution += "Our approach included:\n\n"

            for key_point in self.template.key_points:
                solution += f"- {key_point}\n"

            solution += "\n"

        return solution

    def _generate_implementation(self) -> str:
        """
        Generate an implementation section for the case study.

        Returns:
            Generated implementation section
        """
        # Simple implementation for now
        # In a real implementation, this would generate a compelling implementation section
        client_name = self.template.client_name

        implementation = f"## Implementation Process\n\n"
        implementation += f"We worked closely with the {client_name} team to implement our solution efficiently and effectively. The implementation process included the following steps:\n\n"

        # Generate implementation steps
        steps = [
            f"### 1. Discovery and Analysis\n\nWe conducted a thorough analysis of {client_name}'s current processes, systems, and challenges to identify the root causes of their issues and determine the best approach for addressing them.",
            f"### 2. Solution Design\n\nBased on our analysis, we designed a customized solution that addressed {client_name}'s specific needs and challenges, taking into account their unique requirements and constraints.",
            f"### 3. Implementation\n\nWe implemented the solution in phases to minimize disruption to {client_name}'s operations and ensure a smooth transition. This included configuring the system, migrating data, and integrating with existing systems.",
            f"### 4. Training and Onboarding\n\nWe provided comprehensive training to the {client_name} team to ensure they were able to effectively use the new solution and maximize its benefits.",
            f"### 5. Ongoing Support\n\nWe continue to provide ongoing support to {client_name} to ensure the solution continues to meet their needs and address any issues that may arise."
        ]

        implementation += "\n\n".join(steps)

        return implementation

    def _generate_results(self) -> str:
        """
        Generate a results section for the case study.

        Returns:
            Generated results section
        """
        # Simple implementation for now
        # In a real implementation, this would generate a compelling results section
        client_name = self.template.client_name

        results = f"## Results\n\n"
        results += f"The implementation of our solution has delivered significant results for {client_name}:\n\n"

        # Use template results if available
        if hasattr(self.template, "results") and self.template.results:
            for result in self.template.results:
                results += f"- {result}\n"
        else:
            # Generate results based on target persona goals
            goals = self.template.target_persona.get("goals", [])
            if goals:
                for goal in goals:
                    results += f"- {goal}\n"
            else:
                # Generate generic results
                generic_results = [
                    "Increased efficiency by 30%",
                    "Reduced costs by 25%",
                    "Improved customer satisfaction by 40%",
                    "Increased revenue by 20%",
                    "Reduced time-to-market by 35%"
                ]

                for result in generic_results:
                    results += f"- {result}\n"

        results += "\n"

        # Add metrics
        results += "### Key Metrics\n\n"
        results += "| Metric | Before | After | Improvement |\n"
        results += "|--------|--------|-------|-------------|\n"
        results += "| Efficiency | 100% | 130% | +30% |\n"
        results += "| Costs | 100% | 75% | -25% |\n"
        results += "| Customer Satisfaction | 70% | 98% | +40% |\n"
        results += "| Revenue | 100% | 120% | +20% |\n"
        results += "| Time-to-Market | 100% | 65% | -35% |\n\n"

        return results

    def _generate_testimonial(self) -> str:
        """
        Generate a testimonial section for the case study.

        Returns:
            Generated testimonial section
        """
        # Simple implementation for now
        # In a real implementation, this would generate a compelling testimonial
        client_name = self.template.client_name

        # Skip if testimonial is not included
        if hasattr(self.template, "include_testimonial") and not self.template.include_testimonial:
            return ""

        testimonial = f"## Client Testimonial\n\n"
        testimonial += "> \"Working with the team has been a game-changer for our business. "

        # Add specific benefits
        goals = self.template.target_persona.get("goals", [])
        if goals:
            testimonial += f"We've been able to {goals[0].lower()} and {goals[1].lower() if len(goals) > 1 else 'achieve our other goals'}. "
        else:
            testimonial += "We've seen significant improvements across all areas of our business. "

        testimonial += "The solution has exceeded our expectations, and we would highly recommend it to others in our industry.\"\n\n"

        # Add attribution
        testimonial += f"**John Smith, CEO, {client_name}**\n\n"

        return testimonial

    def _generate_conclusion(self) -> str:
        """
        Generate a conclusion section for the case study.

        Returns:
            Generated conclusion section
        """
        # Simple implementation for now
        # In a real implementation, this would generate a compelling conclusion
        client_name = self.template.client_name

        conclusion = f"## Conclusion\n\n"
        conclusion += f"The partnership between our team and {client_name} has delivered significant results and demonstrates the value of our solution for companies in {self.template.client_industry if hasattr(self.template, 'client_industry') else 'this industry'}. "

        # Add specific benefits
        goals = self.template.target_persona.get("goals", [])
        if goals:
            conclusion += f"By addressing the challenges of {', '.join(self.template.target_persona.get('pain_points', ['the industry'])[:-1]) + ' and ' + self.template.target_persona.get('pain_points', ['the industry'])[-1] if len(self.template.target_persona.get('pain_points', ['the industry'])) > 1 else self.template.target_persona.get('pain_points', ['the industry'])[0]}, "
            conclusion += f"we've helped {client_name} {', '.join(goals[:-1]) + ' and ' + goals[-1] if len(goals) > 1 else goals[0]}. "
        else:
            conclusion += f"By addressing their specific challenges, we've helped {client_name} achieve significant improvements in their business performance. "

        conclusion += "We look forward to continuing our partnership and supporting their ongoing success.\n\n"

        return conclusion

    def _generate_call_to_action(self) -> str:
        """
        Generate a call to action for the case study.

        Returns:
            Generated call to action
        """
        # Use template call to action if available
        if hasattr(self.template, "call_to_action") and self.template.call_to_action:
            return f"**{self.template.call_to_action}**"

        # Simple implementation for now
        # In a real implementation, this would generate a compelling call to action
        return "**Ready to achieve similar results for your business? Contact us today for a free consultation.**"

    def _generate_related_case_studies(self) -> List[Dict[str, Any]]:
        """
        Generate related case studies for the case study.

        Returns:
            List of related case study dictionaries
        """
        # Simple implementation for now
        # In a real implementation, this would generate relevant related case studies
        return [
            {
                "id": str(uuid.uuid4()),
                "title": f"How Company A Increased Efficiency by 40%",
                "client_name": "Company A",
                "client_industry": self.template.client_industry if hasattr(self.template, "client_industry") else "Industry",
                "summary": "Learn how Company A overcame similar challenges and achieved even better results.",
                "url": "https://example.com/case-studies/company-a"
            },
            {
                "id": str(uuid.uuid4()),
                "title": f"Company B's Journey to Reducing Costs by 35%",
                "client_name": "Company B",
                "client_industry": self.template.client_industry if hasattr(self.template, "client_industry") else "Industry",
                "summary": "Discover how Company B addressed their cost challenges with our solution.",
                "url": "https://example.com/case-studies/company-b"
            },
            {
                "id": str(uuid.uuid4()),
                "title": f"Transforming Customer Experience at Company C",
                "client_name": "Company C",
                "client_industry": self.template.client_industry if hasattr(self.template, "client_industry") else "Industry",
                "summary": "See how Company C improved their customer satisfaction scores by 50%.",
                "url": "https://example.com/case-studies/company-c"
            }
        ]

    def _generate_images(self) -> List[Dict[str, Any]]:
        """
        Generate image information for the case study.

        Returns:
            List of image dictionaries
        """
        # Simple implementation for now
        # In a real implementation, this would generate relevant image information
        client_name = self.template.client_name

        return [
            {
                "id": str(uuid.uuid4()),
                "url": f"https://example.com/case-studies/{client_name.lower().replace(' ', '-')}-logo.png",
                "alt_text": f"{client_name} Logo",
                "caption": f"{client_name} Logo",
                "type": "logo"
            },
            {
                "id": str(uuid.uuid4()),
                "url": f"https://example.com/case-studies/{client_name.lower().replace(' ', '-')}-team.jpg",
                "alt_text": f"{client_name} Team",
                "caption": f"The {client_name} team working with our solution",
                "type": "team"
            },
            {
                "id": str(uuid.uuid4()),
                "url": f"https://example.com/case-studies/{client_name.lower().replace(' ', '-')}-results.png",
                "alt_text": f"{client_name} Results",
                "caption": f"Chart showing the results achieved by {client_name}",
                "type": "results"
            },
            {
                "id": str(uuid.uuid4()),
                "url": f"https://example.com/case-studies/{client_name.lower().replace(' ', '-')}-testimonial.jpg",
                "alt_text": f"{client_name} Testimonial",
                "caption": f"John Smith, CEO of {client_name}",
                "type": "testimonial"
            }
        ]

    def _generate_seo_data(self) -> Dict[str, Any]:
        """
        Generate SEO data for the case study.

        Returns:
            Dictionary with SEO data
        """
        # Simple implementation for now
        # In a real implementation, this would generate comprehensive SEO data
        client_name = self.template.client_name
        client_industry = self.template.client_industry if hasattr(self.template, "client_industry") else "Industry"

        return {
            "meta_title": f"Case Study: How {client_name} Achieved Success | Your Company",
            "meta_description": self._generate_meta_description(),
            "focus_keyword": f"{client_name} case study",
            "secondary_keywords": [
                client_name.lower(),
                client_industry.lower(),
                "success story",
                "case study",
                "business results"
            ],
            "slug": self._generate_slug(),
            "canonical_url": f"https://example.com/case-studies/{self._generate_slug()}"
        }

    def _generate_meta_description(self) -> str:
        """
        Generate a meta description for the case study.

        Returns:
            Generated meta description
        """
        # Simple implementation for now
        # In a real implementation, this would generate a compelling meta description
        client_name = self.template.client_name
        client_industry = self.template.client_industry if hasattr(self.template, "client_industry") else "their industry"

        return f"Discover how {client_name}, a leading company in {client_industry}, overcame their challenges and achieved significant results with our solution. Read the case study now."

    def _generate_slug(self) -> str:
        """
        Generate a slug for the case study.

        Returns:
            Generated slug
        """
        # Simple implementation for now
        # In a real implementation, this would generate a proper slug
        client_name = self.template.client_name

        return f"case-study-{client_name.lower().replace(' ', '-')}"

class TestimonialGenerator(ContentGenerator):
    pass
