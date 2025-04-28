"""
Content optimization module for the pAIssive Income project.

This module provides classes for optimizing marketing content, including
SEO optimization, readability analysis, and tone/style adjustment.
"""

# Standard library imports
from typing import Dict, List, Any, Optional, Union, Tuple, Type
from abc import ABC, abstractmethod
import uuid
import json
import datetime
import re
import math
import string
import random
from collections import Counter

# Third-party imports
try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

# Local imports
from .content_templates import ContentTemplate
from .content_generators import ContentGenerator
from .tone_analyzer import ToneAnalyzer


class SEOAnalyzer(ABC):
    """
    Abstract base class for SEO analyzers.

    This class provides common functionality for all SEO analyzers,
    including configuration, analysis, and reporting.
    """

    def __init__(
        self,
        content: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an SEO analyzer.

        Args:
            content: Optional content to analyze
            config: Optional configuration dictionary
        """
        self.id = str(uuid.uuid4())
        self.content = content
        self.config = config or self.get_default_config()
        self.created_at = datetime.datetime.now().isoformat()
        self.results = None

    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze the content for SEO optimization.

        Returns:
            Dictionary with analysis results
        """
        pass

    @abstractmethod
    def get_score(self) -> float:
        """
        Get the overall SEO score for the content.

        Returns:
            SEO score between 0 and 1
        """
        pass

    @abstractmethod
    def get_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get SEO recommendations for the content.

        Returns:
            List of recommendation dictionaries
        """
        pass

    def get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration for the SEO analyzer.

        Returns:
            Default configuration dictionary
        """
        return {
            "min_keyword_density": 0.01,  # 1%
            "max_keyword_density": 0.03,  # 3%
            "min_word_count": 300,
            "optimal_word_count": 1500,
            "min_title_length": 30,
            "max_title_length": 60,
            "min_meta_description_length": 120,
            "max_meta_description_length": 160,
            "min_heading_count": 3,
            "min_internal_links": 2,
            "min_external_links": 1,
            "max_paragraph_length": 300,  # characters
            "check_image_alt_text": True,
            "check_keyword_in_title": True,
            "check_keyword_in_headings": True,
            "check_keyword_in_first_paragraph": True,
            "check_keyword_in_url": True,
            "check_keyword_in_meta_description": True,
            "timestamp": datetime.datetime.now().isoformat()
        }

    def validate_config(self) -> Tuple[bool, List[str]]:
        """
        Validate the configuration dictionary.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required fields
        required_fields = [
            "min_keyword_density",
            "max_keyword_density",
            "min_word_count",
            "optimal_word_count",
            "min_title_length",
            "max_title_length",
            "min_meta_description_length",
            "max_meta_description_length"
        ]

        for field in required_fields:
            if field not in self.config:
                errors.append(f"Missing required field: {field}")

        # Validate field types and values
        if "min_keyword_density" in self.config and not (isinstance(self.config["min_keyword_density"], (int, float)) and 0 <= self.config["min_keyword_density"] <= 1):
            errors.append("min_keyword_density must be a number between 0 and 1")

        if "max_keyword_density" in self.config and not (isinstance(self.config["max_keyword_density"], (int, float)) and 0 <= self.config["max_keyword_density"] <= 1):
            errors.append("max_keyword_density must be a number between 0 and 1")

        if "min_word_count" in self.config and not (isinstance(self.config["min_word_count"], int) and self.config["min_word_count"] > 0):
            errors.append("min_word_count must be a positive integer")

        if "optimal_word_count" in self.config and not (isinstance(self.config["optimal_word_count"], int) and self.config["optimal_word_count"] > 0):
            errors.append("optimal_word_count must be a positive integer")

        if "min_title_length" in self.config and not (isinstance(self.config["min_title_length"], int) and self.config["min_title_length"] > 0):
            errors.append("min_title_length must be a positive integer")

        if "max_title_length" in self.config and not (isinstance(self.config["max_title_length"], int) and self.config["max_title_length"] > 0):
            errors.append("max_title_length must be a positive integer")

        if "min_meta_description_length" in self.config and not (isinstance(self.config["min_meta_description_length"], int) and self.config["min_meta_description_length"] > 0):
            errors.append("min_meta_description_length must be a positive integer")

        if "max_meta_description_length" in self.config and not (isinstance(self.config["max_meta_description_length"], int) and self.config["max_meta_description_length"] > 0):
            errors.append("max_meta_description_length must be a positive integer")

        # Check min <= max
        if "min_keyword_density" in self.config and "max_keyword_density" in self.config and self.config["min_keyword_density"] > self.config["max_keyword_density"]:
            errors.append("min_keyword_density must be less than or equal to max_keyword_density")

        if "min_title_length" in self.config and "max_title_length" in self.config and self.config["min_title_length"] > self.config["max_title_length"]:
            errors.append("min_title_length must be less than or equal to max_title_length")

        if "min_meta_description_length" in self.config and "max_meta_description_length" in self.config and self.config["min_meta_description_length"] > self.config["max_meta_description_length"]:
            errors.append("min_meta_description_length must be less than or equal to max_meta_description_length")

        if "min_word_count" in self.config and "optimal_word_count" in self.config and self.config["min_word_count"] > self.config["optimal_word_count"]:
            errors.append("min_word_count must be less than or equal to optimal_word_count")

        return len(errors) == 0, errors

    def set_content(self, content: Dict[str, Any]) -> None:
        """
        Set the content to analyze.

        Args:
            content: Content dictionary
        """
        self.content = content
        self.results = None  # Reset results

    def set_config(self, config: Dict[str, Any]) -> None:
        """
        Set the configuration dictionary.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.results = None  # Reset results

    def update_config(self, key: str, value: Any) -> None:
        """
        Update a specific configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
        self.results = None  # Reset results

    def merge_configs(self, override_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two configuration dictionaries.

        Args:
            override_config: Override configuration dictionary

        Returns:
            Merged configuration dictionary
        """
        # Create a copy of the base config
        merged_config = self.config.copy()

        # Update with override config
        merged_config.update(override_config)

        # Update timestamp
        merged_config["timestamp"] = datetime.datetime.now().isoformat()

        return merged_config

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the SEO analyzer to a dictionary.

        Returns:
            Dictionary representation of the SEO analyzer
        """
        return {
            "id": self.id,
            "config": self.config,
            "created_at": self.created_at,
            "results": self.results
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the SEO analyzer to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the SEO analyzer
        """
        return json.dumps(self.to_dict(), indent=indent)


class KeywordAnalyzer(SEOAnalyzer):
    """
    Class for analyzing keyword usage in content.

    This class provides methods for analyzing keyword density, placement,
    and optimization in content.
    """

    def __init__(
        self,
        content: Optional[Dict[str, Any]] = None,
        keywords: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a keyword analyzer.

        Args:
            content: Optional content to analyze
            keywords: Optional list of keywords to analyze
            config: Optional configuration dictionary
        """
        super().__init__(content, config)
        self.keywords = keywords or []

        # Initialize NLTK if available
        if NLTK_AVAILABLE:
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')

            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords')

    def set_keywords(self, keywords: List[str]) -> None:
        """
        Set the keywords to analyze.

        Args:
            keywords: List of keywords
        """
        self.keywords = keywords
        self.results = None  # Reset results

    def validate_content(self) -> Tuple[bool, List[str]]:
        """
        Validate the content for keyword analysis.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        if self.content is None:
            return False, ["No content provided"]

        errors = []

        # Check required fields
        required_fields = ["title"]

        for field in required_fields:
            if field not in self.content:
                errors.append(f"Missing required field: {field}")

        # Check if keywords are provided
        if not self.keywords:
            errors.append("No keywords provided")

        return len(errors) == 0, errors

    def analyze(self) -> Dict[str, Any]:
        """
        Analyze the content for keyword optimization.

        Returns:
            Dictionary with analysis results
        """
        # Validate content
        is_valid, errors = self.validate_content()

        if not is_valid:
            raise ValueError(f"Invalid content: {', '.join(errors)}")

        # Initialize results
        self.results = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "content_id": self.content.get("id", "unknown"),
            "keywords": self.keywords,
            "keyword_density": {},
            "keyword_placement": {},
            "overall_score": 0.0,
            "recommendations": []
        }

        # Analyze keyword density
        self.results["keyword_density"] = self._analyze_keyword_density()

        # Analyze keyword placement
        self.results["keyword_placement"] = self._analyze_keyword_placement()

        # Calculate overall score
        self.results["overall_score"] = self.get_score()

        # Generate recommendations
        self.results["recommendations"] = self.get_recommendations()

        return self.results

    def _analyze_keyword_density(self) -> Dict[str, Any]:
        """
        Analyze keyword density in the content.

        This method implements a sophisticated algorithm for calculating optimal keyword density
        for SEO purposes. The process includes:

        1. Extract text from all content sections (title, meta description, body content, etc.)
        2. Tokenize the text and count total words
        3. For each keyword:
           - Count exact occurrences using word boundary matching to prevent partial matches
           - Calculate density ratio (keyword occurrences ÷ total words)
           - Evaluate if the density falls within the optimal range (typically 1-3%)
        4. Return detailed metrics for each keyword with optimization status

        The optimal keyword density is configured through:
        - min_keyword_density (default: 1%)
        - max_keyword_density (default: 3%)

        These parameters can be adjusted based on specific SEO requirements and content type.

        Returns:
            Dictionary with keyword density analysis including:
            - total_words: Total word count in the content
            - keywords: Dictionary mapping each keyword to its metrics:
              - count: Number of occurrences
              - density: Keyword density percentage
              - is_optimal: Whether density falls within optimal range
              - optimal_range: Configuration values for min/max density
        """
        # Extract text from content
        text = self._extract_text_from_content()

        # Count total words
        total_words = len(self._tokenize_text(text))

        # Calculate keyword density for each keyword
        keyword_density = {}

        for keyword in self.keywords:
            # Count keyword occurrences
            keyword_count = self._count_keyword_occurrences(text, keyword)

            # Calculate density
            density = keyword_count / total_words if total_words > 0 else 0

            # Determine if density is within optimal range
            is_optimal = self.config["min_keyword_density"] <= density <= self.config["max_keyword_density"]

            keyword_density[keyword] = {
                "count": keyword_count,
                "density": density,
                "is_optimal": is_optimal,
                "optimal_range": {
                    "min": self.config["min_keyword_density"],
                    "max": self.config["max_keyword_density"]
                }
            }

        return {
            "total_words": total_words,
            "keywords": keyword_density
        }

    def _analyze_keyword_placement(self) -> Dict[str, Any]:
        """
        Analyze keyword placement in strategic content locations.

        This method evaluates the strategic placement of keywords in high-value content locations
        that have significant impact on SEO performance. The algorithm:

        1. Identifies key content sections with higher SEO weight:
           - Title (H1) - highest importance
           - Meta description - high importance for SERP display
           - First paragraph - crucial for establishing relevance
           - Headings (H2, H3) - important for topic structure
           - URL slug - significant for search indexing
           - Alt text in images - important for image search and accessibility

        2. For each keyword:
           - Checks presence in each strategic location
           - Assigns placement score based on configured weights
           - Calculates overall placement effectiveness score (0-100)

        3. Provides placement recommendations based on gaps identified

        Returns:
            Dictionary with placement analysis for each keyword:
            - locations: Dict mapping locations to boolean presence indicator
            - placement_score: Overall placement effectiveness score (0-100)
            - recommendations: List of recommended placement improvements
        """
        # Extract text from different content sections
        title = self.content.get("title", "")
        meta_description = self.content.get("meta_description", "")
        first_paragraph = self._extract_first_paragraph()
        headings = self._extract_headings()
        url = self.content.get("url", "")
        alt_texts = self._extract_image_alt_texts()

        # Initialize placement analysis
        placement_analysis = {}

        for keyword in self.keywords:
            # Check keyword presence in each location
            locations = {
                "title": self._contains_keyword(title, keyword),
                "meta_description": self._contains_keyword(meta_description, keyword),
                "first_paragraph": self._contains_keyword(first_paragraph, keyword),
                "headings": any(self._contains_keyword(heading, keyword) for heading in headings),
                "url": self._contains_keyword(url, keyword),
                "alt_texts": any(self._contains_keyword(alt, keyword) for alt in alt_texts)
            }

            # Calculate placement score based on location weights
            placement_score = self._calculate_placement_score(locations)

            # Generate placement recommendations
            recommendations = self._generate_placement_recommendations(locations, keyword)

            placement_analysis[keyword] = {
                "locations": locations,
                "placement_score": placement_score,
                "recommendations": recommendations
            }

        return placement_analysis

    def _extract_text_from_content(self) -> str:
        """
        Extract text from content for analysis.

        Returns:
            Extracted text
        """
        text = ""

        # Add title
        if "title" in self.content:
            text += self.content["title"] + "\n\n"

        # Add meta description
        if "meta_description" in self.content:
            text += self.content["meta_description"] + "\n\n"

        # Add introduction
        if "introduction" in self.content:
            text += self.content["introduction"] + "\n\n"

        # Add sections
        if "sections" in self.content:
            for section in self.content["sections"]:
                if "title" in section:
                    text += section["title"] + "\n\n"
                if "content" in section:
                    text += section["content"] + "\n\n"

        # Add conclusion
        if "conclusion" in self.content:
            text += self.content["conclusion"] + "\n\n"

        # Add overview (for product descriptions)
        if "overview" in self.content:
            text += self.content["overview"] + "\n\n"

        # Add features (for product descriptions)
        if "features" in self.content:
            for feature in self.content["features"]:
                if "description" in feature:
                    text += feature["description"] + "\n\n"

        # Add benefits (for product descriptions)
        if "benefits" in self.content:
            for benefit in self.content["benefits"]:
                if "description" in benefit:
                    text += benefit["description"] + "\n\n"

        # Add executive summary (for case studies)
        if "executive_summary" in self.content:
            text += self.content["executive_summary"] + "\n\n"

        # Add challenge (for case studies)
        if "challenge" in self.content:
            text += self.content["challenge"] + "\n\n"

        # Add solution (for case studies)
        if "solution" in self.content:
            text += self.content["solution"] + "\n\n"

        # Add implementation (for case studies)
        if "implementation" in self.content:
            text += self.content["implementation"] + "\n\n"

        # Add results (for case studies)
        if "results" in self.content:
            text += self.content["results"] + "\n\n"

        # Add testimonial (for case studies)
        if "testimonial" in self.content:
            text += self.content["testimonial"] + "\n\n"

        return text

    def _extract_first_paragraph(self) -> str:
        """
        Extract the first paragraph from the content.

        Returns:
            The first paragraph as a string
        """
        # Implementation depends on content structure
        # Placeholder implementation:
        return self.content.get("introduction", "")

    def _extract_headings(self) -> List[str]:
        """
        Extract headings from the content.

        Returns:
            List of headings as strings
        """
        # Implementation depends on content structure
        # Placeholder implementation:
        return [section.get("title", "") for section in self.content.get("sections", [])]

    def _extract_image_alt_texts(self) -> List[str]:
        """
        Extract alt texts from images in the content.

        Returns:
            List of alt texts as strings
        """
        # Implementation depends on content structure
        # Placeholder implementation:
        return [image.get("alt", "") for image in self.content.get("images", [])]

    def _tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize text into words.

        Args:
            text: The text to tokenize

        Returns:
            List of words
        """
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text.lower())

        # Split on whitespace
        return text.split()

    def _count_keyword_occurrences(self, text: str, keyword: str) -> int:
        """
        Count the number of occurrences of a keyword in text.

        This method uses word boundary matching to prevent partial matches.
        For example, searching for "car" won't match "carpet" or "scar".

        Args:
            text: The text to search in
            keyword: The keyword to count

        Returns:
            Number of occurrences
        """
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        keyword_lower = keyword.lower()

        # Use word boundary matching to count occurrences
        pattern = r'\b' + re.escape(keyword_lower) + r'\b'
        matches = re.findall(pattern, text_lower)

        return len(matches)

    def _contains_keyword(self, text: str, keyword: str) -> bool:
        """
        Check if the text contains the keyword.

        Args:
            text: The text to check
            keyword: The keyword to look for

        Returns:
            True if the text contains the keyword, False otherwise
        """
        return keyword.lower() in text.lower()

    def _calculate_placement_score(self, locations: Dict[str, bool]) -> float:
        """
        Calculate the placement score based on keyword locations.

        Args:
            locations: Dictionary mapping locations to boolean presence indicator

        Returns:
            Placement score (0-100)
        """
        # Weights for each location
        weights = {
            "title": 3.0,
            "meta_description": 2.0,
            "first_paragraph": 2.0,
            "headings": 1.5,
            "url": 1.0,
            "alt_texts": 1.0
        }

        # Calculate score
        score = sum(weights[loc] for loc, present in locations.items() if present)

        # Normalize score to 0-100 range
        max_score = sum(weights.values())
        placement_score = (score / max_score) * 100 if max_score > 0 else 0

        return placement_score

    def _generate_placement_recommendations(self, locations: Dict[str, bool], keyword: str) -> List[str]:
        """
        Generate recommendations for improving keyword placement.

        Args:
            locations: Dictionary mapping locations to boolean presence indicator
            keyword: The keyword being analyzed

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Check each location and suggest improvements if keyword is missing
        for loc, present in locations.items():
            if not present:
                recommendations.append(f"Consider including the keyword '{keyword}' in the {loc.replace('_', ' ')}.")

        return recommendations

    def get_score(self) -> float:
        """
        Get the overall SEO score for the content.

        Returns:
            SEO score between 0 and 1
        """
        if self.results is None:
            self.analyze()

        # Calculate density score
        density_scores = []

        for keyword, data in self.results["keyword_density"]["keywords"].items():
            if data["is_optimal"]:
                density_scores.append(1.0)
            else:
                # Calculate how close the density is to the optimal range
                density = data["density"]
                min_density = data["optimal_range"]["min"]
                max_density = data["optimal_range"]["max"]

                if density < min_density:
                    # Score based on how close to min_density
                    density_scores.append(density / min_density)
                else:  # density > max_density
                    # Score based on how close to max_density
                    density_scores.append(max_density / density)

        density_score = sum(density_scores) / len(density_scores) if density_scores else 0

        # Calculate placement score
        placement_scores = []

        for keyword, data in self.results["keyword_placement"].items():
            placement_scores.append(data["score"])

        placement_score = sum(placement_scores) / len(placement_scores) if placement_scores else 0

        # Calculate overall score (50% density, 50% placement)
        overall_score = (density_score * 0.5) + (placement_score * 0.5)

        return overall_score

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get SEO recommendations for the content.

        Returns:
            List of recommendation dictionaries
        """
        if self.results is None:
            self.analyze()

        recommendations = []

        # Check keyword density
        for keyword, data in self.results["keyword_density"]["keywords"].items():
            if not data["is_optimal"]:
                density = data["density"]
                min_density = data["optimal_range"]["min"]
                max_density = data["optimal_range"]["max"]

                if density < min_density:
                    recommendations.append({
                        "id": str(uuid.uuid4()),
                        "type": "keyword_density",
                        "keyword": keyword,
                        "severity": "medium",
                        "message": f"Keyword '{keyword}' density is too low ({density:.2%}). Aim for at least {min_density:.2%}.",
                        "suggestion": f"Add more instances of '{keyword}' throughout the content."
                    })
                else:  # density > max_density
                    recommendations.append({
                        "id": str(uuid.uuid4()),
                        "type": "keyword_density",
                        "keyword": keyword,
                        "severity": "medium",
                        "message": f"Keyword '{keyword}' density is too high ({density:.2%}). Aim for at most {max_density:.2%}.",
                        "suggestion": f"Reduce the number of instances of '{keyword}' or add more content to dilute the density."
                    })

        # Check keyword placement
        for keyword, data in self.results["keyword_placement"].items():
            # Check title
            if not data["in_title"] and self.config.get("check_keyword_in_title", True):
                recommendations.append({
                    "id": str(uuid.uuid4()),
                    "type": "keyword_placement",
                    "keyword": keyword,
                    "severity": "high",
                    "message": f"Keyword '{keyword}' is not in the title.",
                    "suggestion": f"Include '{keyword}' in the title for better SEO."
                })

            # Check headings
            if not data["in_headings"] and self.config.get("check_keyword_in_headings", True):
                recommendations.append({
                    "id": str(uuid.uuid4()),
                    "type": "keyword_placement",
                    "keyword": keyword,
                    "severity": "medium",
                    "message": f"Keyword '{keyword}' is not in any headings.",
                    "suggestion": f"Include '{keyword}' in at least one heading for better SEO."
                })

            # Check first paragraph
            if not data["in_first_paragraph"] and self.config.get("check_keyword_in_first_paragraph", True):
                recommendations.append({
                    "id": str(uuid.uuid4()),
                    "type": "keyword_placement",
                    "keyword": keyword,
                    "severity": "medium",
                    "message": f"Keyword '{keyword}' is not in the first paragraph.",
                    "suggestion": f"Include '{keyword}' in the first paragraph for better SEO."
                })

            # Check meta description
            if not data["in_meta_description"] and self.config.get("check_keyword_in_meta_description", True):
                recommendations.append({
                    "id": str(uuid.uuid4()),
                    "type": "keyword_placement",
                    "keyword": keyword,
                    "severity": "medium",
                    "message": f"Keyword '{keyword}' is not in the meta description.",
                    "suggestion": f"Include '{keyword}' in the meta description for better SEO."
                })

            # Check URL
            if not data["in_url"] and self.config.get("check_keyword_in_url", True):
                recommendations.append({
                    "id": str(uuid.uuid4()),
                    "type": "keyword_placement",
                    "keyword": keyword,
                    "severity": "medium",
                    "message": f"Keyword '{keyword}' is not in the URL.",
                    "suggestion": f"Include '{keyword}' in the URL for better SEO."
                })

        # Check word count
        total_words = self.results["keyword_density"]["total_words"]
        min_word_count = self.config["min_word_count"]
        optimal_word_count = self.config["optimal_word_count"]

        if total_words < min_word_count:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "content_length",
                "severity": "high",
                "message": f"Content is too short ({total_words} words). Aim for at least {min_word_count} words.",
                "suggestion": "Add more content to provide more value and improve SEO."
            })
        elif total_words < optimal_word_count:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "content_length",
                "severity": "low",
                "message": f"Content is shorter than optimal ({total_words} words). Aim for around {optimal_word_count} words for best results.",
                "suggestion": "Consider adding more content to provide more value and improve SEO."
            })

        return recommendations


class ReadabilityAnalyzer(SEOAnalyzer):
    """
    Class for analyzing the readability of content.

    This class provides methods for analyzing readability metrics, sentence structure,
    and text complexity in content.
    """

    def __init__(
        self,
        content: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a readability analyzer.

        Args:
            content: Optional content to analyze
            config: Optional configuration dictionary
        """
        super().__init__(content, config)

        # Initialize NLTK if available
        if NLTK_AVAILABLE:
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')

    def get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration for the readability analyzer.

        Returns:
            Default configuration dictionary
        """
        # Start with base config
        config = super().get_default_config()

        # Add readability-specific config
        config.update({
            "target_reading_level": "intermediate",  # beginner, intermediate, advanced
            "max_sentence_length": 25,  # words
            "min_sentence_length": 5,  # words
            "max_paragraph_length": 150,  # words
            "min_paragraph_length": 30,  # words
            "max_passive_voice_percentage": 0.15,  # 15%
            "max_complex_word_percentage": 0.1,  # 10%
            "min_flesch_reading_ease": 60.0,  # 60-70 is standard
            "max_flesch_kincaid_grade": 9.0,  # 9th grade level
            "max_smog_index": 9.0,  # 9th grade level
            "max_coleman_liau_index": 9.0,  # 9th grade level
            "max_automated_readability_index": 9.0,  # 9th grade level
            "max_gunning_fog_index": 12.0,  # 12th grade level
            "check_transition_words": True,
            "check_sentence_beginnings": True,
            "check_adverb_usage": True,
            "check_passive_voice": True,
            "check_consecutive_sentences": True
        })

        return config

    def validate_content(self) -> Tuple[bool, List[str]]:
        """
        Validate the content for readability analysis.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        if self.content is None:
            return False, ["No content provided"]

        errors = []

        # Check if there's text to analyze
        text = self._extract_text_from_content()
        if not text:
            errors.append("No text found in content")

        return len(errors) == 0, errors

    def _extract_text_from_content(self) -> str:
        """
        Extract text from content for analysis.

        Returns:
            Extracted text
        """
        text = ""

        # Add introduction
        if "introduction" in self.content:
            text += self.content["introduction"] + "\n\n"

        # Add sections
        if "sections" in self.content:
            for section in self.content["sections"]:
                if "content" in section:
                    text += section["content"] + "\n\n"

        # Add conclusion
        if "conclusion" in self.content:
            text += self.content["conclusion"] + "\n\n"

        # Add overview (for product descriptions)
        if "overview" in self.content:
            text += self.content["overview"] + "\n\n"

        # Add features (for product descriptions)
        if "features" in self.content:
            for feature in self.content["features"]:
                if "description" in feature:
                    text += feature["description"] + "\n\n"

        # Add benefits (for product descriptions)
        if "benefits" in self.content:
            for benefit in self.content["benefits"]:
                if "description" in benefit:
                    text += benefit["description"] + "\n\n"

        # Add executive summary (for case studies)
        if "executive_summary" in self.content:
            text += self.content["executive_summary"] + "\n\n"

        # Add challenge (for case studies)
        if "challenge" in self.content:
            text += self.content["challenge"] + "\n\n"

        # Add solution (for case studies)
        if "solution" in self.content:
            text += self.content["solution"] + "\n\n"

        # Add implementation (for case studies)
        if "implementation" in self.content:
            text += self.content["implementation"] + "\n\n"

        # Add results (for case studies)
        if "results" in self.content:
            text += self.content["results"] + "\n\n"

        # Add testimonial (for case studies)
        if "testimonial" in self.content:
            text += self.content["testimonial"] + "\n\n"

        return text

    def analyze(self) -> Dict[str, Any]:
        """
        Analyze the content for readability.

        Returns:
            Dictionary with analysis results
        """
        # Validate content
        is_valid, errors = self.validate_content()

        if not is_valid:
            raise ValueError(f"Invalid content: {', '.join(errors)}")

        # Extract text
        text = self._extract_text_from_content()

        # Initialize results
        self.results = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "content_id": self.content.get("id", "unknown"),
            "text_statistics": {},
            "readability_scores": {},
            "sentence_analysis": {},
            "paragraph_analysis": {},
            "style_analysis": {},
            "overall_score": 0.0,
            "recommendations": []
        }

        # Analyze text statistics
        self.results["text_statistics"] = self._analyze_text_statistics(text)

        # Analyze readability scores
        self.results["readability_scores"] = self._analyze_readability_scores(text)

        # Analyze sentence structure
        self.results["sentence_analysis"] = self._analyze_sentence_structure(text)

        # Analyze paragraph structure
        self.results["paragraph_analysis"] = self._analyze_paragraph_structure(text)

        # Analyze writing style
        self.results["style_analysis"] = self._analyze_writing_style(text)

        # Calculate overall score
        self.results["overall_score"] = self.get_score()

        # Generate recommendations
        self.results["recommendations"] = self.get_recommendations()

        return self.results

    def _get_sentences(self, text: str) -> List[str]:
        """
        Get sentences from text.

        Args:
            text: Text to analyze

        Returns:
            List of sentences
        """
        if NLTK_AVAILABLE:
            # Use NLTK for sentence tokenization
            return sent_tokenize(text)
        else:
            # Simple sentence tokenization
            # Split on periods, exclamation points, and question marks
            sentences = re.split(r'(?<=[.!?])\s+', text)

            # Filter out empty sentences
            return [s.strip() for s in sentences if s.strip()]

    def _get_words(self, text: str) -> List[str]:
        """
        Get words from text.

        Args:
            text: Text to analyze

        Returns:
            List of words
        """
        if NLTK_AVAILABLE:
            # Use NLTK for word tokenization
            return word_tokenize(text.lower())
        else:
            # Simple word tokenization
            # Remove punctuation
            text = re.sub(r'[^\w\s]', '', text.lower())

            # Split on whitespace
            return text.split()

    def _get_paragraphs(self, text: str) -> List[str]:
        """
        Get paragraphs from text.

        Args:
            text: Text to analyze

        Returns:
            List of paragraphs
        """
        # Split on double newlines
        paragraphs = text.split('\n\n')

        # Filter out empty paragraphs
        return [p.strip() for p in paragraphs if p.strip()]

    def _count_syllables(self, text: str) -> int:
        """
        Count syllables in text.

        Args:
            text: Text to analyze

        Returns:
            Number of syllables
        """
        words = self._get_words(text)

        # Count syllables in each word
        return sum(self._count_syllables_in_word(word) for word in words)

    def _count_syllables_in_word(self, word: str) -> int:
        """
        Count syllables in a word.

        Args:
            word: Word to analyze

        Returns:
            Number of syllables
        """
        # Remove non-alphabetic characters
        word = re.sub(r'[^a-zA-Z]', '', word.lower())

        if not word:
            return 0

        # Count vowel groups
        count = len(re.findall(r'[aeiouy]+', word))

        # Adjust for silent e at end of word
        if word.endswith('e') and len(word) > 2 and word[-2] not in 'aeiouy':
            count -= 1

        # Adjust for words ending in 'le'
        if word.endswith('le') and len(word) > 2 and word[-3] not in 'aeiouy':
            count += 1

        # Ensure at least one syllable
        return max(1, count)

    def _analyze_text_statistics(self, text: str) -> Dict[str, Any]:
        """
        Analyze text statistics.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with text statistics
        """
        # Get sentences
        sentences = self._get_sentences(text)
        num_sentences = len(sentences)

        # Get words
        words = self._get_words(text)
        num_words = len(words)

        # Get paragraphs
        paragraphs = self._get_paragraphs(text)
        num_paragraphs = len(paragraphs)

        # Get syllables
        num_syllables = self._count_syllables(text)

        # Get complex words (words with 3+ syllables)
        complex_words = [word for word in words if self._count_syllables_in_word(word) >= 3]
        num_complex_words = len(complex_words)

        # Calculate averages
        avg_words_per_sentence = num_words / num_sentences if num_sentences > 0 else 0
        avg_syllables_per_word = num_syllables / num_words if num_words > 0 else 0
        avg_words_per_paragraph = num_words / num_paragraphs if num_paragraphs > 0 else 0

        # Calculate percentages
        complex_word_percentage = num_complex_words / num_words if num_words > 0 else 0

        return {
            "num_sentences": num_sentences,
            "num_words": num_words,
            "num_paragraphs": num_paragraphs,
            "num_syllables": num_syllables,
            "num_complex_words": num_complex_words,
            "avg_words_per_sentence": avg_words_per_sentence,
            "avg_syllables_per_word": avg_syllables_per_word,
            "avg_words_per_paragraph": avg_words_per_paragraph,
            "complex_word_percentage": complex_word_percentage
        }

    def _analyze_readability_scores(self, text: str) -> Dict[str, Any]:
        """
        Analyze text and calculate comprehensive readability scores using multiple algorithms.

        This method computes a suite of industry-standard readability metrics including:
        - Flesch Reading Ease: Scores text from 0-100, with higher scores indicating easier readability
        - Flesch-Kincaid Grade Level: Estimates the US grade level needed to understand the text
        - SMOG Index: Measures readability based on polysyllabic words per sentence
        - Coleman-Liau Index: Bases readability on character count rather than syllables
        - Automated Readability Index: Calculates readability based on characters per word and words per sentence
        - Gunning Fog Index: Measures readability based on sentence length and complex words

        The method also determines an overall grade level by averaging multiple algorithms and
        provides a qualitative reading level assessment (e.g., "Easy", "Medium", "Difficult").

        Args:
            text: The content text to analyze

        Returns:
            Dictionary containing all readability scores, interpretations, and optimal status flags
        """
        # Get text statistics
        stats = self._analyze_text_statistics(text)

        # Calculate Flesch Reading Ease
        flesch_reading_ease = self._calculate_flesch_reading_ease(
            stats["avg_words_per_sentence"],
            stats["avg_syllables_per_word"]
        )

        # Calculate Flesch-Kincaid Grade Level
        flesch_kincaid_grade = self._calculate_flesch_kincaid_grade(
            stats["avg_words_per_sentence"],
            stats["avg_syllables_per_word"]
        )

        # Calculate SMOG Index
        smog_index = self._calculate_smog_index(
            stats["num_complex_words"],
            stats["num_sentences"]
        )

        # Calculate Coleman-Liau Index
        coleman_liau_index = self._calculate_coleman_liau_index(
            stats["num_words"],
            stats["num_sentences"],
            text
        )

        # Calculate Automated Readability Index
        automated_readability_index = self._calculate_automated_readability_index(
            stats["num_words"],
            stats["num_sentences"],
            text
        )

        # Calculate Gunning Fog Index
        gunning_fog_index = self._calculate_gunning_fog(
            stats["avg_words_per_sentence"],
            stats["complex_word_percentage"]
        )

        # Determine reading level
        reading_level = self._determine_reading_level(flesch_reading_ease)

        # Determine grade level
        grade_level = self._determine_grade_level([
            flesch_kincaid_grade,
            smog_index,
            coleman_liau_index,
            automated_readability_index,
            gunning_fog_index
        ])

        return {
            "flesch_reading_ease": {
                "score": flesch_reading_ease,
                "interpretation": self._interpret_flesch_reading_ease(flesch_reading_ease),
                "is_optimal": flesch_reading_ease >= self.config["min_flesch_reading_ease"]
            },
            "flesch_kincaid_grade": {
                "score": flesch_kincaid_grade,
                "interpretation": f"{flesch_kincaid_grade:.1f} grade level",
                "is_optimal": flesch_kincaid_grade <= self.config["max_flesch_kincaid_grade"]
            },
            "smog_index": {
                "score": smog_index,
                "interpretation": f"{smog_index:.1f} grade level",
                "is_optimal": smog_index <= self.config["max_smog_index"]
            },
            "coleman_liau_index": {
                "score": coleman_liau_index,
                "interpretation": f"{coleman_liau_index:.1f} grade level",
                "is_optimal": coleman_liau_index <= self.config["max_coleman_liau_index"]
            },
            "automated_readability_index": {
                "score": automated_readability_index,
                "interpretation": f"{automated_readability_index:.1f} grade level",
                "is_optimal": automated_readability_index <= self.config["max_automated_readability_index"]
            },
            "gunning_fog_index": {
                "score": gunning_fog_index,
                "interpretation": f"{gunning_fog_index:.1f} grade level",
                "is_optimal": gunning_fog_index <= self.config["max_gunning_fog_index"]
            },
            "reading_level": reading_level,
            "grade_level": grade_level
        }

    def _calculate_flesch_reading_ease(self, avg_words_per_sentence: float, avg_syllables_per_word: float) -> float:
        """
        Calculate the Flesch Reading Ease score for the text.

        The Flesch Reading Ease algorithm quantifies text readability using sentence length
        and syllable count. The algorithm works as follows:

        1. Count the total number of words, sentences, and syllables in the text
        2. Calculate average sentence length (ASL) = words / sentences
        3. Calculate average syllables per word (ASW) = syllables / words
        4. Apply the formula: 206.835 - (1.015 * ASL) - (84.6 * ASW)

        The score ranges from 0-100:
        - 0-30: Very difficult (College graduate level)
        - 30-50: Difficult (College level)
        - 50-60: Fairly difficult (10th-12th grade)
        - 60-70: Standard (8th-9th grade)
        - 70-80: Fairly easy (7th grade)
        - 80-90: Easy (6th grade)
        - 90-100: Very easy (5th grade)

        Args:
            avg_words_per_sentence: Average words per sentence
            avg_syllables_per_word: Average syllables per word

        Returns:
            Flesch Reading Ease score (0-100, higher is easier to read)
        """
        # Formula: 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)

        # Clamp score to 0-100 range
        return max(0, min(100, score))

    def _calculate_flesch_kincaid_grade(self, avg_words_per_sentence: float, avg_syllables_per_word: float) -> float:
        """
        Calculate Flesch-Kincaid Grade Level.

        Args:
            avg_words_per_sentence: Average words per sentence
            avg_syllables_per_word: Average syllables per word

        Returns:
            Flesch-Kincaid Grade Level
        """
        # Formula: 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
        score = (0.39 * avg_words_per_sentence) + (11.8 * avg_syllables_per_word) - 15.59

        # Clamp score to 0-18 range
        return max(0, min(18, score))

    def _calculate_smog_index(self, num_complex_words: int, num_sentences: int) -> float:
        """
        Calculate SMOG Index.

        Args:
            num_complex_words: Number of complex words (3+ syllables)
            num_sentences: Number of sentences

        Returns:
            SMOG Index
        """
        # Need at least 30 sentences for accurate SMOG calculation
        if num_sentences < 30:
            # Adjust formula for fewer sentences
            adjusted_complex_words = num_complex_words * (30 / num_sentences) if num_sentences > 0 else 0
        else:
            adjusted_complex_words = num_complex_words

        # Formula: 1.043 * sqrt(complex_words * (30 / sentences)) + 3.1291
        score = 1.043 * math.sqrt(adjusted_complex_words * (30 / max(1, num_sentences))) + 3.1291

        # Clamp score to 0-18 range
        return max(0, min(18, score))

    def _calculate_coleman_liau_index(self, num_words: int, num_sentences: int, text: str) -> float:
        """
        Calculate Coleman-Liau Index.

        Args:
            num_words: Number of words
            num_sentences: Number of sentences
            text: Text to analyze

        Returns:
            Coleman-Liau Index
        """
        # Count characters (excluding spaces)
        num_chars = len(text.replace(" ", ""))

        # Calculate L (average number of characters per 100 words)
        L = (num_chars / num_words) * 100 if num_words > 0 else 0

        # Calculate S (average number of sentences per 100 words)
        S = (num_sentences / num_words) * 100 if num_words > 0 else 0

        # Formula: 0.0588 * L - 0.296 * S - 15.8
        score = (0.0588 * L) - (0.296 * S) - 15.8

        # Clamp score to 0-18 range
        return max(0, min(18, score))

    def _calculate_automated_readability_index(self, num_words: int, num_sentences: int, text: str) -> float:
        """
        Calculate Automated Readability Index.

        Args:
            num_words: Number of words
            num_sentences: Number of sentences
            text: Text to analyze

        Returns:
            Automated Readability Index
        """
        # Count characters (excluding spaces)
        num_chars = len(text.replace(" ", ""))

        # Calculate average characters per word
        chars_per_word = num_chars / num_words if num_words > 0 else 0

        # Calculate average words per sentence
        words_per_sentence = num_words / num_sentences if num_sentences > 0 else 0

        # Formula: 4.71 * (chars / words) + 0.5 * (words / sentences) - 21.43
        score = (4.71 * chars_per_word) + (0.5 * words_per_sentence) - 21.43

        # Clamp score to 0-18 range
        return max(0, min(18, score))

    def _calculate_gunning_fog(self, avg_words_per_sentence: float, complex_word_percentage: float) -> float:
        """
        Calculate the Gunning Fog Index for the text.

        The Gunning Fog Index algorithm measures the readability of English writing by
        estimating the years of formal education needed to understand the text on first
        reading. The algorithm operates as follows:

        1. Count the total number of words and sentences in the text
        2. Calculate the percentage of complex words (words with 3+ syllables,
           excluding proper nouns, compound words, and technical jargon)
        3. Calculate average sentence length (ASL) = words / sentences
        4. Calculate percentage of complex words (PCW) = (complex_words / words) * 100
        5. Apply the formula: 0.4 * (ASL + PCW)

        Interpretation of the index:
        - 6: Sixth grade reading level
        - 8: Eighth grade reading level
        - 10: High school sophomore
        - 12: High school senior
        - 14: College sophomore
        - 16: College senior
        - 18+: Graduate/Professional level

        For general audiences, a fog index of 12 or below is recommended.

        Args:
            avg_words_per_sentence: Average words per sentence
            complex_word_percentage: Percentage of complex words

        Returns:
            Gunning Fog Index (representing years of formal education needed)
        """
        # Formula: 0.4 * ((words / sentences) + 100 * (complex_words / words))
        score = 0.4 * (avg_words_per_sentence + (100 * complex_word_percentage))

        # Clamp score to 0-18 range
        return max(0, min(18, score))

    def _interpret_flesch_reading_ease(self, score: float) -> str:
        """
        Interpret Flesch Reading Ease score.

        Args:
            score: Flesch Reading Ease score

        Returns:
            Interpretation of the score
        """
        if score >= 90:
            return "Very Easy - 5th grade level"
        elif score >= 80:
            return "Easy - 6th grade level"
        elif score >= 70:
            return "Fairly Easy - 7th grade level"
        elif score >= 60:
            return "Standard - 8th-9th grade level"
        elif score >= 50:
            return "Fairly Difficult - 10th-12th grade level"
        elif score >= 30:
            return "Difficult - College level"
        else:
            return "Very Difficult - College graduate level"

    def _determine_reading_level(self, flesch_reading_ease: float) -> str:
        """
        Determine reading level based on Flesch Reading Ease score.

        Args:
            flesch_reading_ease: Flesch Reading Ease score

        Returns:
            Reading level (beginner, intermediate, advanced)
        """
        if flesch_reading_ease >= 80:
            return "beginner"
        elif flesch_reading_ease >= 50:
            return "intermediate"
        else:
            return "advanced"

    def _determine_grade_level(self, grade_scores: List[float]) -> float:
        """
        Determine average grade level from multiple readability scores.

        Args:
            grade_scores: List of grade level scores

        Returns:
            Average grade level
        """
        # Calculate average grade level
        avg_grade = sum(grade_scores) / len(grade_scores) if grade_scores else 0

        # Round to nearest 0.5
        return round(avg_grade * 2) / 2

    def _analyze_sentence_structure(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentence structure.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentence structure analysis
        """
        # Get sentences
        sentences = self._get_sentences(text)

        # Calculate sentence lengths
        sentence_lengths = [len(self._get_words(sentence)) for sentence in sentences]

        # Calculate sentence length statistics
        min_length = min(sentence_lengths) if sentence_lengths else 0
        max_length = max(sentence_lengths) if sentence_lengths else 0
        avg_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0

        # Count sentences by length
        short_sentences = sum(1 for length in sentence_lengths if length < self.config["min_sentence_length"])
        long_sentences = sum(1 for length in sentence_lengths if length > self.config["max_sentence_length"])
        optimal_sentences = sum(1 for length in sentence_lengths if self.config["min_sentence_length"] <= length <= self.config["max_sentence_length"])

        # Calculate percentages
        short_sentence_percentage = short_sentences / len(sentences) if sentences else 0
        long_sentence_percentage = long_sentences / len(sentences) if sentences else 0
        optimal_sentence_percentage = optimal_sentences / len(sentences) if sentences else 0

        # Analyze sentence beginnings
        sentence_beginnings = self._analyze_sentence_beginnings(sentences)

        # Analyze sentence variety
        sentence_variety = self._analyze_sentence_variety(sentences)

        # Analyze transition words
        transition_words = self._analyze_transition_words(sentences)

        return {
            "sentence_count": len(sentences),
            "sentence_length": {
                "min": min_length,
                "max": max_length,
                "avg": avg_length,
                "short_count": short_sentences,
                "long_count": long_sentences,
                "optimal_count": optimal_sentences,
                "short_percentage": short_sentence_percentage,
                "long_percentage": long_sentence_percentage,
                "optimal_percentage": optimal_sentence_percentage,
                "is_optimal": long_sentence_percentage <= 0.2 and short_sentence_percentage <= 0.1
            },
            "sentence_beginnings": sentence_beginnings,
            "sentence_variety": sentence_variety,
            "transition_words": transition_words
        }

    def _analyze_sentence_beginnings(self, sentences: List[str]) -> Dict[str, Any]:
        """
        Analyze sentence beginnings.

        Args:
            sentences: List of sentences

        Returns:
            Dictionary with sentence beginnings analysis
        """
        if not sentences:
            return {
                "unique_beginnings_count": 0,
                "unique_beginnings_percentage": 0,
                "common_beginnings": {},
                "is_optimal": False
            }

        # Get first word of each sentence
        first_words = []

        for sentence in sentences:
            words = self._get_words(sentence)
            if words:
                first_words.append(words[0].lower())

        # Count occurrences of each first word
        first_word_counts = Counter(first_words)

        # Get most common first words
        most_common = first_word_counts.most_common(5)

        # Calculate unique beginnings
        unique_beginnings = len(first_word_counts)
        unique_beginnings_percentage = unique_beginnings / len(sentences) if sentences else 0

        return {
            "unique_beginnings_count": unique_beginnings,
            "unique_beginnings_percentage": unique_beginnings_percentage,
            "common_beginnings": {word: count for word, count in most_common},
            "is_optimal": unique_beginnings_percentage >= 0.7
        }

    def _analyze_sentence_variety(self, sentences: List[str]) -> Dict[str, Any]:
        """
        Analyze sentence variety.

        Args:
            sentences: List of sentences

        Returns:
            Dictionary with sentence variety analysis
        """
        if not sentences:
            return {
                "length_variety": 0,
                "is_optimal": False
            }

        # Calculate sentence lengths
        sentence_lengths = [len(self._get_words(sentence)) for sentence in sentences]

        # Calculate standard deviation of sentence lengths
        mean_length = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((length - mean_length) ** 2 for length in sentence_lengths) / len(sentence_lengths)
        std_dev = math.sqrt(variance)

        # Calculate coefficient of variation (normalized standard deviation)
        cv = std_dev / mean_length if mean_length > 0 else 0

        # Determine if variety is optimal
        is_optimal = cv >= 0.2

        return {
            "length_variety": cv,
            "is_optimal": is_optimal
        }

    def _analyze_transition_words(self, sentences: List[str]) -> Dict[str, Any]:
        """
        Analyze transition words in sentences.

        Args:
            sentences: List of sentences

        Returns:
            Dictionary with transition words analysis
        """
        # Common transition words
        transition_words = [
            "additionally", "also", "furthermore", "moreover", "in addition",
            "similarly", "likewise", "in the same way", "equally",
            "however", "but", "yet", "nevertheless", "nonetheless", "on the other hand",
            "in contrast", "conversely", "instead", "alternatively",
            "therefore", "thus", "consequently", "as a result", "hence",
            "for example", "for instance", "specifically", "namely", "to illustrate",
            "in fact", "indeed", "actually", "to clarify", "in other words",
            "first", "second", "third", "next", "then", "finally", "lastly",
            "in conclusion", "to summarize", "in summary", "to conclude"
        ]

        # Count sentences with transition words
        sentences_with_transitions = 0
        transition_word_counts = Counter()

        for sentence in sentences:
            has_transition = False

            for word in transition_words:
                if word in sentence.lower():
                    has_transition = True
                    transition_word_counts[word] += 1

            if has_transition:
                sentences_with_transitions += 1

        # Calculate percentage of sentences with transition words
        transition_percentage = sentences_with_transitions / len(sentences) if sentences else 0

        # Get most common transition words
        most_common = transition_word_counts.most_common(5)

        return {
            "sentences_with_transitions": sentences_with_transitions,
            "transition_percentage": transition_percentage,
            "common_transitions": {word: count for word, count in most_common},
            "is_optimal": transition_percentage >= 0.3
        }

    def _analyze_paragraph_structure(self, text: str) -> Dict[str, Any]:
        """
        Analyze paragraph structure.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with paragraph structure analysis
        """
        # Get paragraphs
        paragraphs = self._get_paragraphs(text)

        # Calculate paragraph lengths
        paragraph_lengths = [len(self._get_words(paragraph)) for paragraph in paragraphs]

        # Calculate paragraph length statistics
        min_length = min(paragraph_lengths) if paragraph_lengths else 0
        max_length = max(paragraph_lengths) if paragraph_lengths else 0
        avg_length = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0

        # Count paragraphs by length
        short_paragraphs = sum(1 for length in paragraph_lengths if length < self.config["min_paragraph_length"])
        long_paragraphs = sum(1 for length in paragraph_lengths if length > self.config["max_paragraph_length"])
        optimal_paragraphs = sum(1 for length in paragraph_lengths if self.config["min_paragraph_length"] <= length <= self.config["max_paragraph_length"])

        # Calculate percentages
        short_paragraph_percentage = short_paragraphs / len(paragraphs) if paragraphs else 0
        long_paragraph_percentage = long_paragraphs / len(paragraphs) if paragraphs else 0
        optimal_paragraph_percentage = optimal_paragraphs / len(paragraphs) if paragraphs else 0

        # Analyze paragraph variety
        paragraph_variety = self._analyze_paragraph_variety(paragraphs)

        return {
            "paragraph_count": len(paragraphs),
            "paragraph_length": {
                "min": min_length,
                "max": max_length,
                "avg": avg_length,
                "short_count": short_paragraphs,
                "long_count": long_paragraphs,
                "optimal_count": optimal_paragraphs,
                "short_percentage": short_paragraph_percentage,
                "long_percentage": long_paragraph_percentage,
                "optimal_percentage": optimal_paragraph_percentage,
                "is_optimal": long_paragraph_percentage <= 0.2 and short_paragraph_percentage <= 0.1
            },
            "paragraph_variety": paragraph_variety
        }

    def _analyze_paragraph_variety(self, paragraphs: List[str]) -> Dict[str, Any]:
        """
        Analyze paragraph variety.

        Args:
            paragraphs: List of paragraphs

        Returns:
            Dictionary with paragraph variety analysis
        """
        if not paragraphs:
            return {
                "length_variety": 0,
                "is_optimal": False
            }

        # Calculate paragraph lengths
        paragraph_lengths = [len(self._get_words(paragraph)) for paragraph in paragraphs]

        # Calculate standard deviation of paragraph lengths
        mean_length = sum(paragraph_lengths) / len(paragraph_lengths)
        variance = sum((length - mean_length) ** 2 for length in paragraph_lengths) / len(paragraph_lengths)
        std_dev = math.sqrt(variance)

        # Calculate coefficient of variation (normalized standard deviation)
        cv = std_dev / mean_length if mean_length > 0 else 0

        # Determine if variety is optimal
        is_optimal = cv >= 0.2

        return {
            "length_variety": cv,
            "is_optimal": is_optimal
        }

    def _analyze_writing_style(self, text: str) -> Dict[str, Any]:
        """
        Analyze writing style.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with writing style analysis
        """
        # Analyze passive voice
        passive_voice = self._analyze_passive_voice(text)

        # Analyze adverb usage
        adverb_usage = self._analyze_adverb_usage(text)

        # Analyze complex words
        complex_words = self._analyze_complex_words(text)

        return {
            "passive_voice": passive_voice,
            "adverb_usage": adverb_usage,
            "complex_words": complex_words
        }

    def _analyze_passive_voice(self, text: str) -> Dict[str, Any]:
        """
        Analyze passive voice usage.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with passive voice analysis
        """
        # Simple passive voice detection patterns
        passive_patterns = [
            r'\b(?:am|is|are|was|were|be|being|been)\s+(\w+ed)\b',
            r'\b(?:am|is|are|was|were|be|being|been)\s+(\w+en)\b',
            r'\b(?:am|is|are|was|were|be|being|been)\s+(\w+t)\b'
        ]

        # Count passive voice instances
        passive_count = 0

        for pattern in passive_patterns:
            passive_count += len(re.findall(pattern, text, re.IGNORECASE))

        # Get sentences
        sentences = self._get_sentences(text)

        # Calculate passive voice percentage
        passive_percentage = passive_count / len(sentences) if sentences else 0

        # Determine if passive voice usage is optimal
        is_optimal = passive_percentage <= self.config["max_passive_voice_percentage"]

        return {
            "passive_count": passive_count,
            "passive_percentage": passive_percentage,
            "is_optimal": is_optimal
        }

    def _analyze_adverb_usage(self, text: str) -> Dict[str, Any]:
        """
        Analyze adverb usage.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with adverb usage analysis
        """
        # Simple adverb detection pattern (words ending in 'ly')
        adverb_pattern = r'\b\w+ly\b'

        # Find adverbs
        adverbs = re.findall(adverb_pattern, text, re.IGNORECASE)

        # Count adverbs
        adverb_count = len(adverbs)

        # Get words
        words = self._get_words(text)

        # Calculate adverb percentage
        adverb_percentage = adverb_count / len(words) if words else 0

        # Determine if adverb usage is optimal
        is_optimal = adverb_percentage <= 0.05

        # Count adverb occurrences
        adverb_counts = Counter(adverb.lower() for adverb in adverbs)

        # Get most common adverbs
        most_common = adverb_counts.most_common(5)

        return {
            "adverb_count": adverb_count,
            "adverb_percentage": adverb_percentage,
            "common_adverbs": {word: count for word, count in most_common},
            "is_optimal": is_optimal
        }

    def _analyze_complex_words(self, text: str) -> Dict[str, Any]:
        """
        Analyze complex word usage.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with complex word analysis
        """
        # Get words
        words = self._get_words(text)

        # Find complex words (words with 3+ syllables)
        complex_words = [word for word in words if self._count_syllables_in_word(word) >= 3]

        # Count complex words
        complex_word_count = len(complex_words)

        # Calculate complex word percentage
        complex_word_percentage = complex_word_count / len(words) if words else 0

        # Determine if complex word usage is optimal
        is_optimal = complex_word_percentage <= self.config["max_complex_word_percentage"]

        # Count complex word occurrences
        complex_word_counts = Counter(word.lower() for word in complex_words)

        # Get most common complex words
        most_common = complex_word_counts.most_common(5)

        return {
            "complex_word_count": complex_word_count,
            "complex_word_percentage": complex_word_percentage,
            "common_complex_words": {word: count for word, count in most_common},
            "is_optimal": is_optimal
        }

    def get_score(self) -> float:
        """
        Get the overall readability score for the content.

        Returns:
            Readability score between 0 and 1
        """
        if self.results is None:
            self.analyze()

        # Calculate readability score
        readability_score = 0.0

        # Score based on Flesch Reading Ease
        if self.results["readability_scores"]["flesch_reading_ease"]["is_optimal"]:
            readability_score += 0.2
        else:
            # Calculate partial score based on how close to optimal
            flesch_score = self.results["readability_scores"]["flesch_reading_ease"]["score"]
            min_flesch = self.config["min_flesch_reading_ease"]
            readability_score += 0.2 * (flesch_score / min_flesch) if min_flesh > 0 else 0

        # Score based on grade level
        target_grade = self.config["max_flesch_kincaid_grade"]
        actual_grade = self.results["readability_scores"]["grade_level"]

        if actual_grade <= target_grade:
            readability_score += 0.2
        else:
            # Calculate partial score based on how close to target
            readability_score += 0.2 * (target_grade / actual_grade) if actual_grade > 0 else 0

        # Score based on sentence structure
        sentence_score = 0.0

        if self.results["sentence_analysis"]["sentence_length"]["is_optimal"]:
            sentence_score += 0.33

        if self.results["sentence_analysis"]["sentence_beginnings"]["is_optimal"]:
            sentence_score += 0.33

        if self.results["sentence_analysis"]["sentence_variety"]["is_optimal"]:
            sentence_score += 0.34

        readability_score += 0.2 * sentence_score

        # Score based on paragraph structure
        paragraph_score = 0.0

        if self.results["paragraph_analysis"]["paragraph_length"]["is_optimal"]:
            paragraph_score += 0.5

        if self.results["paragraph_analysis"]["paragraph_variety"]["is_optimal"]:
            paragraph_score += 0.5

        readability_score += 0.2 * paragraph_score

        # Score based on writing style
        style_score = 0.0

        if self.results["style_analysis"]["passive_voice"]["is_optimal"]:
            style_score += 0.33

        if self.results["style_analysis"]["adverb_usage"]["is_optimal"]:
            style_score += 0.33

        if self.results["style_analysis"]["complex_words"]["is_optimal"]:
            style_score += 0.34

        readability_score += 0.2 * style_score

        return readability_score

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get readability recommendations for the content.

        Returns:
            List of recommendation dictionaries
        """
        if self.results is None:
            self.analyze()

        recommendations = []

        # Check Flesch Reading Ease
        flesch_score = self.results["readability_scores"]["flesch_reading_ease"]["score"]
        min_flesch = self.config["min_flesch_reading_ease"]

        if flesch_score < min_flesch:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "readability_score",
                "severity": "high",
                "message": f"Flesch Reading Ease score ({flesch_score:.1f}) is below the recommended minimum ({min_flesch:.1f}).",
                "suggestion": "Use shorter sentences and simpler words to improve readability."
            })

        # Check grade level
        grade_level = self.results["readability_scores"]["grade_level"]
        max_grade = self.config["max_flesch_kincaid_grade"]

        if grade_level > max_grade:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "grade_level",
                "severity": "medium",
                "message": f"Content grade level ({grade_level:.1f}) is above the recommended maximum ({max_grade:.1f}).",
                "suggestion": "Simplify language and sentence structure to lower the grade level."
            })

        # Check sentence length
        avg_sentence_length = self.results["sentence_analysis"]["sentence_length"]["avg"]
        max_sentence_length = self.config["max_sentence_length"]
        long_sentence_percentage = self.results["sentence_analysis"]["sentence_length"]["long_percentage"]

        if avg_sentence_length > max_sentence_length * 0.8:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "sentence_length",
                "severity": "medium",
                "message": f"Average sentence length ({avg_sentence_length:.1f} words) is approaching the maximum recommended length ({max_sentence_length} words).",
                "suggestion": "Break longer sentences into shorter ones to improve readability."
            })

        if long_sentence_percentage > 0.2:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "sentence_length",
                "severity": "medium",
                "message": f"{long_sentence_percentage:.1%} of sentences are longer than the recommended maximum ({max_sentence_length} words).",
                "suggestion": "Identify and break up long sentences to improve readability."
            })

        # Check sentence beginnings
        unique_beginnings_percentage = self.results["sentence_analysis"]["sentence_beginnings"]["unique_beginnings_percentage"]

        if unique_beginnings_percentage < 0.7:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "sentence_beginnings",
                "severity": "low",
                "message": f"Only {unique_beginnings_percentage:.1%} of sentences have unique beginnings.",
                "suggestion": "Vary sentence beginnings to improve flow and engagement."
            })

        # Check transition words
        transition_percentage = self.results["sentence_analysis"]["transition_words"]["transition_percentage"]

        if transition_percentage < 0.3:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "transition_words",
                "severity": "low",
                "message": f"Only {transition_percentage:.1%} of sentences contain transition words.",
                "suggestion": "Add more transition words to improve flow and coherence."
            })

        # Check paragraph length
        avg_paragraph_length = self.results["paragraph_analysis"]["paragraph_length"]["avg"]
        max_paragraph_length = self.config["max_paragraph_length"]
        long_paragraph_percentage = self.results["paragraph_analysis"]["paragraph_length"]["long_percentage"]

        if avg_paragraph_length > max_paragraph_length * 0.8:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "paragraph_length",
                "severity": "medium",
                "message": f"Average paragraph length ({avg_paragraph_length:.1f} words) is approaching the maximum recommended length ({max_paragraph_length} words).",
                "suggestion": "Break longer paragraphs into shorter ones to improve readability."
            })

        if long_paragraph_percentage > 0.2:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "paragraph_length",
                "severity": "medium",
                "message": f"{long_paragraph_percentage:.1%} of paragraphs are longer than the recommended maximum ({max_paragraph_length} words).",
                "suggestion": "Identify and break up long paragraphs to improve readability."
            })

        # Check passive voice
        passive_percentage = self.results["style_analysis"]["passive_voice"]["passive_percentage"]
        max_passive = self.config["max_passive_voice_percentage"]

        if passive_percentage > max_passive:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "passive_voice",
                "severity": "medium",
                "message": f"Passive voice usage ({passive_percentage:.1%}) exceeds the recommended maximum ({max_passive:.1%}).",
                "suggestion": "Replace passive voice with active voice to improve clarity and engagement."
            })

        # Check adverb usage
        adverb_percentage = self.results["style_analysis"]["adverb_usage"]["adverb_percentage"]

        if adverb_percentage > 0.05:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "adverb_usage",
                "severity": "low",
                "message": f"Adverb usage ({adverb_percentage:.1%}) is higher than recommended (5%).",
                "suggestion": "Replace adverbs with stronger verbs to improve clarity and impact."
            })

        # Check complex words
        complex_word_percentage = self.results["style_analysis"]["complex_words"]["complex_word_percentage"]
        max_complex = self.config["max_complex_word_percentage"]

        if complex_word_percentage > max_complex:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "complex_words",
                "severity": "medium",
                "message": f"Complex word usage ({complex_word_percentage:.1%}) exceeds the recommended maximum ({max_complex:.1%}).",
                "suggestion": "Replace complex words with simpler alternatives to improve readability."
            })

        return recommendations
