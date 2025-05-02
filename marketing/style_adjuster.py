"""
Style adjuster module for the pAIssive Income project.

This module provides classes for adjusting the style and tone of content.
"""

import datetime
import json
import random
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple

# Third-party imports
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import sent_tokenize, word_tokenize

    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

# Local imports
from .tone_analyzer import ToneAnalyzer


class StyleAdjuster:
    """
    Class for adjusting the style and tone of content.

    This class provides methods for adjusting tone, sentiment, and style
    in content based on analysis and target style preferences.
    """

    # Define style categories
    STYLE_CATEGORIES = {
        "formal": {
            "description": "Professional, academic, or business-like style",
            "avoid_words": [
                "awesome",
                "cool",
                "wow",
                "yeah",
                "hey",
                "ok",
                "okay",
                "gonna",
                "wanna",
                "gotta",
                "kinda",
                "sorta",
                "stuff",
                "things",
                "whatever",
                "anyway",
                "somehow",
                "like",
                "you know",
                "I mean",
                "well",
                "so",
            ],
            "prefer_words": [
                "excellent",
                "impressive",
                "remarkable",
                "indeed",
                "greetings",
                "acceptable",
                "certainly",
                "going to",
                "want to",
                "got to",
                "somewhat",
                "rather",
                "items",
                "elements",
                "regardless",
                "nevertheless",
                "in some manner",
                "such as",
                "as you are aware",
                "to clarify",
                "in any case",
                "therefore",
            ],
            "sentence_structure": "complex",
            "paragraph_length": "medium to long",
            "punctuation": "standard",
            "voice": "passive often acceptable",
        },
        "conversational": {
            "description": "Friendly, casual, or personal style",
            "avoid_words": [
                "hereby",
                "therein",
                "aforementioned",
                "heretofore",
                "pursuant",
                "notwithstanding",
                "henceforth",
                "it is necessary to",
                "it is important to",
                "it is essential to",
                "the author",
                "the researcher",
                "the study",
                "shall",
                "must",
                "ought",
            ],
            "prefer_words": [
                "here",
                "in this",
                "mentioned earlier",
                "before now",
                "according to",
                "despite",
                "from now on",
                "you need to",
                "it's important to",
                "it's essential to",
                "I",
                "we",
                "our team",
                "will",
                "need to",
                "should",
            ],
            "sentence_structure": "simple to moderate",
            "paragraph_length": "short to medium",
            "punctuation": "relaxed",
            "voice": "active preferred",
        },
        "persuasive": {
            "description": "Convincing, compelling, or sales-oriented style",
            "avoid_words": [
                "perhaps",
                "maybe",
                "possibly",
                "might",
                "could be",
                "somewhat",
                "relatively",
                "comparatively",
                "moderately",
                "it seems",
                "it appears",
                "it may be",
                "it could be",
                "in my opinion",
                "I think",
                "I believe",
                "I feel",
                "unclear",
                "uncertain",
                "unknown",
                "undetermined",
            ],
            "prefer_words": [
                "definitely",
                "certainly",
                "absolutely",
                "will",
                "is",
                "extremely",
                "highly",
                "significantly",
                "substantially",
                "it is clear",
                "it is evident",
                "it is certain",
                "it will",
                "without doubt",
                "clearly",
                "obviously",
                "undoubtedly",
                "proven",
                "established",
                "confirmed",
                "verified",
            ],
            "sentence_structure": "varied, with strong statements",
            "paragraph_length": "short to medium",
            "punctuation": "emphatic",
            "voice": "active required",
        },
        "informative": {
            "description": "Educational, explanatory, or factual style",
            "avoid_words": [
                "I guess",
                "I suppose",
                "I assume",
                "I reckon",
                "kinda",
                "sorta",
                "pretty much",
                "more or less",
                "stuff",
                "things",
                "whatever",
                "anyway",
                "somehow",
                "like",
                "you know",
                "I mean",
                "well",
                "so",
                "probably",
                "hopefully",
                "maybe",
                "perhaps",
            ],
            "prefer_words": [
                "research indicates",
                "evidence suggests",
                "data shows",
                "analysis reveals",
                "approximately",
                "roughly",
                "nearly",
                "about",
                "components",
                "elements",
                "factors",
                "aspects",
                "characteristics",
                "for example",
                "specifically",
                "in particular",
                "namely",
                "likely",
                "potentially",
                "possibly",
                "theoretically",
            ],
            "sentence_structure": "clear and direct",
            "paragraph_length": "medium",
            "punctuation": "standard",
            "voice": "mix of active and passive",
        },
    }

    # Define word replacement dictionaries
    WORD_REPLACEMENTS = {
        "formal": {
            # Casual to formal word replacements
            "awesome": ["excellent", "outstanding", "exceptional"],
            "cool": ["impressive", "remarkable", "noteworthy"],
            "wow": ["impressive", "remarkable", "extraordinary"],
            "yeah": ["yes", "indeed", "certainly"],
            "hey": ["greetings", "hello", "good day"],
            "ok": ["acceptable", "satisfactory", "adequate"],
            "okay": ["acceptable", "satisfactory", "adequate"],
            "gonna": ["going to", "will", "intend to"],
            "wanna": ["want to", "wish to", "desire to"],
            "gotta": ["have to", "must", "need to"],
            "kinda": ["somewhat", "rather", "relatively"],
            "sorta": ["somewhat", "rather", "relatively"],
            "stuff": ["items", "materials", "elements"],
            "things": ["items", "elements", "components"],
            "whatever": ["regardless", "irrespective", "notwithstanding"],
            "anyway": ["nevertheless", "nonetheless", "however"],
            "somehow": ["in some manner", "by some means", "in some way"],
            "like": ["such as", "similar to", "comparable to"],
            "you know": ["as you are aware", "as you understand", "as you recognize"],
            "I mean": ["to clarify", "to be precise", "specifically"],
            "well": ["in any case", "at any rate", "in fact"],
            "so": ["therefore", "consequently", "thus"],
        },
        "conversational": {
            # Formal to conversational word replacements
            "hereby": ["here", "by this", "with this"],
            "therein": ["in this", "in there", "inside"],
            "aforementioned": [
                "mentioned earlier",
                "mentioned above",
                "that I talked about",
            ],
            "heretofore": ["before now", "until now", "previously"],
            "pursuant": ["according to", "following", "based on"],
            "notwithstanding": ["despite", "even though", "still"],
            "henceforth": ["from now on", "going forward", "from this point on"],
            "it is necessary to": ["you need to", "you should", "it's important to"],
            "it is important to": ["you need to", "you should", "it's key to"],
            "it is essential to": ["you have to", "you must", "it's vital to"],
            "the author": ["I", "me", "we"],
            "the researcher": ["I", "me", "we"],
            "the study": ["we", "our research", "our work"],
            "shall": ["will", "going to", "plan to"],
            "must": ["need to", "have to", "should"],
            "ought": ["should", "need to", "might want to"],
        },
        "persuasive": {
            # Uncertain to persuasive word replacements
            "perhaps": ["definitely", "certainly", "absolutely"],
            "maybe": ["definitely", "certainly", "without doubt"],
            "possibly": ["definitely", "certainly", "absolutely"],
            "might": ["will", "can", "does"],
            "could be": ["is", "will be", "definitely is"],
            "somewhat": ["extremely", "highly", "significantly"],
            "relatively": ["extremely", "highly", "significantly"],
            "comparatively": ["extremely", "highly", "significantly"],
            "moderately": ["substantially", "considerably", "greatly"],
            "it seems": ["it is clear", "it is evident", "it is certain"],
            "it appears": ["it is clear", "it is evident", "it is certain"],
            "it may be": ["it is", "it will be", "it certainly is"],
            "it could be": ["it is", "it will be", "it certainly is"],
            "in my opinion": ["without doubt", "clearly", "obviously"],
            "I think": ["I know", "I am certain", "I guarantee"],
            "I believe": ["I know", "I am certain", "I guarantee"],
            "I feel": ["I know", "I am certain", "I guarantee"],
            "unclear": ["proven", "established", "confirmed"],
            "uncertain": ["proven", "established", "confirmed"],
            "unknown": ["well-known", "established", "recognized"],
            "undetermined": ["verified", "confirmed", "established"],
        },
        "informative": {
            # Casual/subjective to informative word replacements
            "I guess": ["research indicates", "evidence suggests", "data shows"],
            "I suppose": ["research indicates", "evidence suggests", "data shows"],
            "I assume": ["research indicates", "evidence suggests", "data shows"],
            "I reckon": ["research indicates", "evidence suggests", "data shows"],
            "kinda": ["approximately", "roughly", "nearly"],
            "sorta": ["approximately", "roughly", "nearly"],
            "pretty much": ["approximately", "roughly", "nearly"],
            "more or less": ["approximately", "roughly", "nearly"],
            "stuff": ["components", "elements", "factors"],
            "things": ["components", "elements", "factors"],
            "whatever": [
                "any relevant factors",
                "all applicable elements",
                "various components",
            ],
            "anyway": ["in any case", "regardless", "nevertheless"],
            "somehow": ["through some mechanism", "by some process", "via some means"],
            "like": ["for example", "such as", "including"],
            "you know": ["specifically", "in particular", "namely"],
            "I mean": ["specifically", "in particular", "namely"],
            "well": ["in fact", "indeed", "notably"],
            "so": ["therefore", "consequently", "as a result"],
            "probably": ["likely", "with high probability", "most likely"],
            "hopefully": ["potentially", "possibly", "it is expected that"],
            "maybe": ["potentially", "possibly", "it is possible that"],
            "perhaps": ["potentially", "possibly", "it is possible that"],
        },
    }

    # Define sentence structure patterns
    SENTENCE_STRUCTURE_PATTERNS = {
        "simple": {
            "description": "Short, direct sentences with a single clause",
            "examples": [
                "We offer the best solution.",
                "Our product saves time.",
                "Customers love our service.",
                "The results are impressive.",
                "This approach works well.",
            ],
            "pattern": r"^[^,;:]{10,40}[.!?]$",
        },
        "compound": {
            "description": "Two independent clauses joined by a conjunction",
            "examples": [
                "We developed this product, and customers love it.",
                "The software is powerful, but it's easy to use.",
                "You can start today, or you can wait until tomorrow.",
                "The price is affordable, yet the quality is premium.",
                "We provide the tools, and you create the magic.",
            ],
            "pattern": r"^[^,;:]{10,30},[^,;:]{10,30}[.!?]$",
        },
        "complex": {
            "description": "An independent clause with one or more dependent clauses",
            "examples": [
                "When you use our product, you'll save hours of work.",
                "Although the process is sophisticated, the interface is intuitive.",
                "If you want to increase productivity, our solution is ideal.",
                "Because we focus on quality, our customers stay with us.",
                "While other options exist, our approach offers unique benefits.",
            ],
            "pattern": r"^[^,;:]{10,30},[^,;:]{10,30}[.!?]$",
        },
        "compound-complex": {
            "description": "Multiple independent clauses with one or more dependent clauses",
            "examples": [
                "When you implement our system, efficiency improves, and costs decrease.",
                "Although the market is competitive, our product stands out, and customers recognize the difference.",
                "If you're looking for results, our solution delivers, and our support team ensures your success.",
                "Because we understand your challenges, we've designed this tool, and we continue to enhance it.",
                "While traditional methods work, our approach is innovative, and it produces superior outcomes.",
            ],
            "pattern": r"^[^,;:]{10,30},[^,;:]{10,30},[^,;:]{10,30}[.!?]$",
        },
    }

    def __init__(
        self,
        content: Optional[Dict[str, Any]] = None,
        target_style: Optional[str] = None,
        analyzer: Optional[ToneAnalyzer] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a style adjuster.

        Args:
            content: Optional content to adjust
            target_style: Optional target style for the content
            analyzer: Optional ToneAnalyzer instance
            config: Optional configuration dictionary
        """
        self.id = str(uuid.uuid4())
        self.content = content
        self.target_style = target_style or "conversational"
        self.analyzer = analyzer
        self.config = config or self.get_default_config()
        self.created_at = datetime.datetime.now().isoformat()
        self.results = None

        # Initialize NLTK if available
        if NLTK_AVAILABLE:
            try:
                nltk.data.find("tokenizers/punkt")
            except LookupError:
                nltk.download("punkt")

    def get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration for the style adjuster.

        Returns:
            Default configuration dictionary
        """
        return {
            "max_suggestions": 10,  # Maximum number of suggestions to generate
            "min_suggestion_confidence": 0.7,  # Minimum confidence score for suggestions
            "prioritize_by": "impact",  # How to prioritize suggestions: impact, confidence, or position
            "adjust_word_choice": True,  # Whether to adjust word choice
            "adjust_sentence_structure": True,  # Whether to adjust sentence structure
            "adjust_paragraph_structure": True,  # Whether to adjust paragraph structure
            "adjust_punctuation": True,  # Whether to adjust punctuation
            "adjust_voice": True,  # Whether to adjust voice (active/passive)
            "target_style": self.target_style,  # Target style
            "timestamp": datetime.datetime.now().isoformat(),
        }

    def validate_content(self) -> Tuple[bool, List[str]]:
        """
        Validate the content for style adjustment.

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

        # Check if target style is valid
        if self.target_style and self.target_style not in self.STYLE_CATEGORIES:
            errors.append(
                f"Invalid target style: {self.target_style}. Must be one of: {', '.join(self.STYLE_CATEGORIES.keys())}"
            )

        return len(errors) == 0, errors

    def validate_config(self) -> Tuple[bool, List[str]]:
        """
        Validate the configuration dictionary.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required fields
        required_fields = [
            "max_suggestions",
            "min_suggestion_confidence",
            "prioritize_by",
            "target_style",
        ]

        for field in required_fields:
            if field not in self.config:
                errors.append(f"Missing required field: {field}")

        # Validate field types and values
        if "max_suggestions" in self.config and not (
            isinstance(self.config["max_suggestions"], int) and self.config["max_suggestions"] > 0
        ):
            errors.append("max_suggestions must be a positive integer")

        if "min_suggestion_confidence" in self.config and not (
            isinstance(self.config["min_suggestion_confidence"], (int, float))
            and 0 <= self.config["min_suggestion_confidence"] <= 1
        ):
            errors.append("min_suggestion_confidence must be a number between 0 and 1")

        if "prioritize_by" in self.config and self.config["prioritize_by"] not in [
            "impact",
            "confidence",
            "position",
        ]:
            errors.append("prioritize_by must be one of: impact, confidence, position")

        if (
            "target_style" in self.config
            and self.config["target_style"] not in self.STYLE_CATEGORIES
        ):
            errors.append(f"target_style must be one of: {', '.join(self.STYLE_CATEGORIES.keys())}")

        # Check boolean fields
        boolean_fields = [
            "adjust_word_choice",
            "adjust_sentence_structure",
            "adjust_paragraph_structure",
            "adjust_punctuation",
            "adjust_voice",
        ]

        for field in boolean_fields:
            if field in self.config and not isinstance(self.config[field], bool):
                errors.append(f"{field} must be a boolean")

        return len(errors) == 0, errors

    def set_content(self, content: Dict[str, Any]) -> None:
        """
        Set the content to adjust.

        Args:
            content: Content dictionary
        """
        self.content = content
        self.results = None  # Reset results

    def set_target_style(self, target_style: str) -> None:
        """
        Set the target style for the content.

        Args:
            target_style: Target style
        """
        if target_style not in self.STYLE_CATEGORIES:
            raise ValueError(
                f"Invalid target style: {target_style}. Must be one of: {', '.join(self.STYLE_CATEGORIES.keys())}"
            )

        self.target_style = target_style
        self.config["target_style"] = target_style
        self.results = None  # Reset results

    def set_analyzer(self, analyzer: ToneAnalyzer) -> None:
        """
        Set the tone analyzer.

        Args:
            analyzer: ToneAnalyzer instance
        """
        self.analyzer = analyzer
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

    def _extract_text_from_content(self) -> str:
        """
        Extract text from content for analysis.

        Returns:
            Extracted text
        """
        if self.content is None:
            return ""

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
                if "name" in feature:
                    text += feature["name"] + "\n"

                if "description" in feature:
                    text += feature["description"] + "\n\n"

        # Add benefits (for product descriptions)
        if "benefits" in self.content:
            for benefit in self.content["benefits"]:
                if "name" in benefit:
                    text += benefit["name"] + "\n"

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
            sentences = re.split(r"(?<=[.!?])\s+", text)

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
            text = re.sub(r"[^\w\s]", "", text.lower())

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
        paragraphs = text.split("\n\n")

        # Filter out empty paragraphs
        return [p.strip() for p in paragraphs if p.strip()]

    def _get_stopwords(self) -> List[str]:
        """
        Get stopwords.

        Returns:
            List of stopwords
        """
        if NLTK_AVAILABLE:
            # Use NLTK for stopwords
            return stopwords.words("english")
        else:
            # Simple stopwords list
            return [
                "a",
                "an",
                "the",
                "and",
                "but",
                "or",
                "for",
                "nor",
                "on",
                "at",
                "to",
                "by",
                "in",
                "of",
                "with",
                "about",
                "against",
                "between",
                "into",
                "through",
                "during",
                "before",
                "after",
                "above",
                "below",
                "from",
                "up",
                "down",
                "out",
                "off",
                "over",
                "under",
                "again",
                "further",
                "then",
                "once",
                "here",
                "there",
                "when",
                "where",
                "why",
                "how",
                "all",
                "any",
                "both",
                "each",
                "few",
                "more",
                "most",
                "other",
                "some",
                "such",
                "no",
                "nor",
                "not",
                "only",
                "own",
                "same",
                "so",
                "than",
                "too",
                "very",
                "s",
                "t",
                "can",
                "will",
                "just",
                "don",
                "don't",
                "should",
                "should've",
                "now",
                "d",
                "ll",
                "m",
                "o",
                "re",
                "ve",
                "y",
                "ain",
                "aren",
                "aren't",
                "couldn",
                "couldn't",
                "didn",
                "didn't",
                "doesn",
                "doesn't",
                "hadn",
                "hadn't",
                "hasn",
                "hasn't",
                "haven",
                "haven't",
                "isn",
                "isn't",
                "ma",
                "mightn",
                "mightn't",
                "mustn",
                "mustn't",
                "needn",
                "needn't",
                "shan",
                "shan't",
                "shouldn",
                "shouldn't",
                "wasn",
                "wasn't",
                "weren",
                "weren't",
                "won",
                "won't",
                "wouldn",
                "wouldn't",
                "i",
                "me",
                "my",
                "myself",
                "we",
                "our",
                "ours",
                "ourselves",
                "you",
                "your",
                "yours",
                "yourself",
                "yourselves",
                "he",
                "him",
                "his",
                "himself",
                "she",
                "her",
                "hers",
                "herself",
                "it",
                "its",
                "itself",
                "they",
                "them",
                "their",
                "theirs",
                "themselves",
                "what",
                "which",
                "who",
                "whom",
                "this",
                "that",
                "these",
                "those",
                "am",
                "is",
                "are",
                "was",
                "were",
                "be",
                "been",
                "being",
                "have",
                "has",
                "had",
                "having",
                "do",
                "does",
                "did",
                "doing",
                "would",
                "could",
                "should",
                "ought",
                "i'm",
                "you're",
                "he's",
                "she's",
                "it's",
                "we're",
                "they're",
                "i've",
                "you've",
                "we've",
                "they've",
                "i'd",
                "you'd",
                "he'd",
                "she'd",
                "we'd",
                "they'd",
                "i'll",
                "you'll",
                "he'll",
                "she'll",
                "we'll",
                "they'll",
                "isn't",
                "aren't",
                "wasn't",
                "weren't",
                "hasn't",
                "haven't",
                "hadn't",
                "doesn't",
                "don't",
                "didn't",
                "won't",
                "wouldn't",
                "shan't",
                "shouldn't",
                "can't",
                "cannot",
                "couldn't",
                "mustn't",
            ]

    def _is_passive_voice(self, sentence: str) -> bool:
        """
        Check if a sentence is in passive voice.

        Args:
            sentence: Sentence to check

        Returns:
            True if the sentence is in passive voice, False otherwise
        """
        # Simple passive voice detection patterns
        passive_patterns = [
            r"\b(?:am|is|are|was|were|be|being|been)\s+(\w+ed)\b",
            r"\b(?:am|is|are|was|were|be|being|been)\s+(\w+en)\b",
            r"\b(?:am|is|are|was|were|be|being|been)\s+(\w+t)\b",
        ]

        # Check if any pattern matches
        for pattern in passive_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                return True

        return False

    def _convert_to_active_voice(self, sentence: str) -> str:
        """
        Convert a passive voice sentence to active voice.

        Args:
            sentence: Sentence to convert

        Returns:
            Sentence in active voice
        """
        # This is a simplified implementation
        # A full implementation would require more complex NLP

        # Passive voice patterns and their active voice transformations
        passive_patterns = [
            (r"\b(am|is|are)\s+(\w+ed)\s+by\s+(.+)", r"\3 \2s \1"),
            (r"\b(was|were)\s+(\w+ed)\s+by\s+(.+)", r"\3 \2ed \1"),
            (r"\b(am|is|are)\s+being\s+(\w+ed)\s+by\s+(.+)", r"\3 is \2ing \1"),
            (r"\b(was|were)\s+being\s+(\w+ed)\s+by\s+(.+)", r"\3 was \2ing \1"),
            (r"\b(have|has)\s+been\s+(\w+ed)\s+by\s+(.+)", r"\3 has \2ed \1"),
            (r"\b(had)\s+been\s+(\w+ed)\s+by\s+(.+)", r"\3 had \2ed \1"),
            (r"\b(will|shall)\s+be\s+(\w+ed)\s+by\s+(.+)", r"\3 will \2 \1"),
            (
                r"\b(would|should|could|might)\s+be\s+(\w+ed)\s+by\s+(.+)",
                r"\3 would \2 \1",
            ),
        ]

        # Try each pattern
        for pattern, replacement in passive_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                return re.sub(pattern, replacement, sentence, flags=re.IGNORECASE)

        # If no pattern matches, return the original sentence
        return sentence

    def _convert_to_passive_voice(self, sentence: str) -> str:
        """
        Convert an active voice sentence to passive voice.

        Args:
            sentence: Sentence to convert

        Returns:
            Sentence in passive voice
        """
        # This is a simplified implementation
        # A full implementation would require more complex NLP

        # Active voice patterns and their passive voice transformations
        active_patterns = [
            (r"\b(.+)\s+(\w+s)\s+(.+)", r"\3 is \2ed by \1"),
            (r"\b(.+)\s+(\w+ed)\s+(.+)", r"\3 was \2ed by \1"),
            (r"\b(.+)\s+is\s+(\w+ing)\s+(.+)", r"\3 is being \2ed by \1"),
            (r"\b(.+)\s+was\s+(\w+ing)\s+(.+)", r"\3 was being \2ed by \1"),
            (r"\b(.+)\s+has\s+(\w+ed)\s+(.+)", r"\3 has been \2ed by \1"),
            (r"\b(.+)\s+had\s+(\w+ed)\s+(.+)", r"\3 had been \2ed by \1"),
            (r"\b(.+)\s+will\s+(\w+)\s+(.+)", r"\3 will be \2ed by \1"),
            (r"\b(.+)\s+would\s+(\w+)\s+(.+)", r"\3 would be \2ed by \1"),
        ]

        # Try each pattern
        for pattern, replacement in active_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                return re.sub(pattern, replacement, sentence, flags=re.IGNORECASE)

        # If no pattern matches, return the original sentence
        return sentence

    def _get_sentence_structure(self, sentence: str) -> str:
        """
        Determine the structure of a sentence.

        Args:
            sentence: Sentence to analyze

        Returns:
            Sentence structure type
        """
        # Count clauses
        independent_clauses = len(re.findall(r"[^,;:]+(?:[,;:]|$)", sentence))
        dependent_clauses = len(
            re.findall(
                r"(?:because|although|while|if|when|after|before|since|unless|until|as|though)[^,;:.]*[,;:]",
                sentence,
            )
        )

        # Determine sentence structure
        if independent_clauses == 1 and dependent_clauses == 0:
            return "simple"
        elif independent_clauses > 1 and dependent_clauses == 0:
            return "compound"
        elif independent_clauses == 1 and dependent_clauses >= 1:
            return "complex"
        elif independent_clauses > 1 and dependent_clauses >= 1:
            return "compound-complex"
        else:
            return "unknown"

    def _get_sentence_complexity(self, sentence: str) -> float:
        """
        Calculate the complexity of a sentence.

        Args:
            sentence: Sentence to analyze

        Returns:
            Complexity score
        """
        # Count words
        words = self._get_words(sentence)
        word_count = len(words)

        # Count clauses
        clauses = len(re.findall(r"[^,;:]+(?:[,;:]|$)", sentence))

        # Count commas, semicolons, and colons
        punctuation_count = len(re.findall(r"[,;:]", sentence))

        # Calculate complexity
        complexity = (word_count / 10) + clauses + (punctuation_count / 2)

        return complexity

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the style adjuster to a dictionary.

        Returns:
            Dictionary representation of the style adjuster
        """
        return {
            "id": self.id,
            "target_style": self.target_style,
            "config": self.config,
            "created_at": self.created_at,
            "results": self.results,
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the style adjuster to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the style adjuster
        """
        return json.dumps(self.to_dict(), indent=indent)

    def analyze(self) -> Dict[str, Any]:
        """
        Analyze the content for style adjustment.

        Returns:
            Dictionary with analysis results
        """
        # Validate content
        is_valid, errors = self.validate_content()

        if not is_valid:
            raise ValueError(f"Invalid content: {', '.join(errors)}")

        # Use existing analyzer if available
        if self.analyzer is not None:
            # Set content and target tone
            self.analyzer.content = self.content
            self.analyzer.set_target_tone(self.target_style)

            # Analyze content
            analysis_results = self.analyzer.analyze()
        else:
            # Create a new analyzer
            analyzer = ToneAnalyzer(self.content, self.target_style)

            # Analyze content
            analysis_results = analyzer.analyze()

            # Store analyzer
            self.analyzer = analyzer

        # Initialize results
        self.results = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "content_id": self.content.get("id", "unknown"),
            "target_style": self.target_style,
            "analysis": analysis_results,
            "adjustments": {
                "word_choice": [],
                "sentence_structure": [],
                "paragraph_structure": [],
                "punctuation": [],
                "voice": [],
            },
            "adjusted_content": None,
        }

        return self.results

    def adjust(self) -> Dict[str, Any]:
        """
        Adjust the content to match the target style.

        Returns:
            Dictionary with adjustment results
        """
        # Analyze content if not already analyzed
        if self.results is None:
            self.analyze()

        # Initialize adjusted content
        adjusted_content = self.content.copy()

        # Apply adjustments
        if self.config["adjust_word_choice"]:
            adjusted_content = self._adjust_word_choice(adjusted_content)

        if self.config["adjust_sentence_structure"]:
            adjusted_content = self._adjust_sentence_structure(adjusted_content)

        if self.config["adjust_paragraph_structure"]:
            adjusted_content = self._adjust_paragraph_structure(adjusted_content)

        if self.config["adjust_punctuation"]:
            adjusted_content = self._adjust_punctuation(adjusted_content)

        if self.config["adjust_voice"]:
            adjusted_content = self._adjust_voice(adjusted_content)

        # Store adjusted content
        self.results["adjusted_content"] = adjusted_content

        return self.results

    def _adjust_word_choice(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adjust word choice in content.

        Args:
            content: Content to adjust

        Returns:
            Adjusted content
        """
        # Get target style word replacements
        if self.target_style not in self.WORD_REPLACEMENTS:
            return content

        word_replacements = self.WORD_REPLACEMENTS[self.target_style]

        # Create a copy of the content
        adjusted_content = content.copy()

        # Extract text from content
        text = self._extract_text_from_content()

        # Get sentences
        sentences = self._get_sentences(text)

        # Initialize adjustments
        adjustments = []

        # Process each sentence
        for sentence in sentences:
            # Check for words to replace
            for word, replacements in word_replacements.items():
                # Create pattern to match whole word
                pattern = r"\b" + re.escape(word) + r"\b"

                # Find all matches
                matches = list(re.finditer(pattern, sentence, re.IGNORECASE))

                # Process each match
                for match in matches:
                    # Get replacement word
                    replacement = random.choice(replacements)

                    # Create adjustment
                    adjustment = {
                        "id": str(uuid.uuid4()),
                        "type": "word_choice",
                        "original": match.group(0),
                        "replacement": replacement,
                        "sentence": sentence,
                        "position": match.span(),
                        "confidence": 0.9,
                        "impact": "medium",
                    }

                    # Add adjustment
                    adjustments.append(adjustment)

                    # Replace in content
                    for key in adjusted_content:
                        if isinstance(adjusted_content[key], str):
                            adjusted_content[key] = re.sub(
                                pattern,
                                replacement,
                                adjusted_content[key],
                                flags=re.IGNORECASE,
                            )
                        elif isinstance(adjusted_content[key], list):
                            for i, item in enumerate(adjusted_content[key]):
                                if isinstance(item, str):
                                    adjusted_content[key][i] = re.sub(
                                        pattern, replacement, item, flags=re.IGNORECASE
                                    )
                                elif isinstance(item, dict):
                                    for subkey in item:
                                        if isinstance(item[subkey], str):
                                            item[subkey] = re.sub(
                                                pattern,
                                                replacement,
                                                item[subkey],
                                                flags=re.IGNORECASE,
                                            )

        # Store adjustments
        self.results["adjustments"]["word_choice"] = adjustments

        return adjusted_content

    def _adjust_sentence_structure(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adjust sentence structure in content.

        Args:
            content: Content to adjust

        Returns:
            Adjusted content
        """
        # Get target style
        style_data = self.STYLE_CATEGORIES.get(self.target_style, {})
        target_sentence_structure = style_data.get("sentence_structure", "")

        # If no target sentence structure, return content
        if not target_sentence_structure:
            return content

        # Create a copy of the content
        adjusted_content = content.copy()

        # Extract text from content
        text = self._extract_text_from_content()

        # Get sentences
        sentences = self._get_sentences(text)

        # Initialize adjustments
        adjustments = []

        # Process each sentence
        for sentence in sentences:
            # Get sentence structure
            structure = self._get_sentence_structure(sentence)

            # Check if adjustment needed
            if structure != target_sentence_structure:
                # Get sentence complexity
                complexity = self._get_sentence_complexity(sentence)

                # Determine adjustment type
                if "simple" in target_sentence_structure and complexity > 2:
                    # Split into simpler sentences
                    adjusted_sentence = self._simplify_sentence(sentence)

                    # Create adjustment
                    adjustment = {
                        "id": str(uuid.uuid4()),
                        "type": "sentence_structure",
                        "original": sentence,
                        "replacement": adjusted_sentence,
                        "original_structure": structure,
                        "target_structure": target_sentence_structure,
                        "confidence": 0.7,
                        "impact": "high",
                    }

                    # Add adjustment
                    adjustments.append(adjustment)

                    # Replace in content
                    for key in adjusted_content:
                        if isinstance(adjusted_content[key], str):
                            adjusted_content[key] = adjusted_content[key].replace(
                                sentence, adjusted_sentence
                            )
                        elif isinstance(adjusted_content[key], list):
                            for i, item in enumerate(adjusted_content[key]):
                                if isinstance(item, str):
                                    adjusted_content[key][i] = item.replace(
                                        sentence, adjusted_sentence
                                    )
                                elif isinstance(item, dict):
                                    for subkey in item:
                                        if isinstance(item[subkey], str):
                                            item[subkey] = item[subkey].replace(
                                                sentence, adjusted_sentence
                                            )

                elif "complex" in target_sentence_structure and complexity < 3:
                    # Combine with adjacent sentence or add complexity
                    adjusted_sentence = self._complexify_sentence(sentence, sentences)

                    # Create adjustment
                    adjustment = {
                        "id": str(uuid.uuid4()),
                        "type": "sentence_structure",
                        "original": sentence,
                        "replacement": adjusted_sentence,
                        "original_structure": structure,
                        "target_structure": target_sentence_structure,
                        "confidence": 0.6,
                        "impact": "high",
                    }

                    # Add adjustment
                    adjustments.append(adjustment)

                    # Replace in content
                    for key in adjusted_content:
                        if isinstance(adjusted_content[key], str):
                            adjusted_content[key] = adjusted_content[key].replace(
                                sentence, adjusted_sentence
                            )
                        elif isinstance(adjusted_content[key], list):
                            for i, item in enumerate(adjusted_content[key]):
                                if isinstance(item, str):
                                    adjusted_content[key][i] = item.replace(
                                        sentence, adjusted_sentence
                                    )
                                elif isinstance(item, dict):
                                    for subkey in item:
                                        if isinstance(item[subkey], str):
                                            item[subkey] = item[subkey].replace(
                                                sentence, adjusted_sentence
                                            )

        # Store adjustments
        self.results["adjustments"]["sentence_structure"] = adjustments

        return adjusted_content

    def _simplify_sentence(self, sentence: str) -> str:
        """
        Simplify a complex sentence.

        Args:
            sentence: Sentence to simplify

        Returns:
            Simplified sentence
        """
        # Split on conjunctions
        conjunctions = [", and ", ", but ", ", or ", ", nor ", ", yet ", ", so "]

        for conjunction in conjunctions:
            if conjunction in sentence:
                parts = sentence.split(conjunction, 1)
                return parts[0] + ". " + parts[1].capitalize()

        # Split on dependent clause markers
        markers = [
            ", which ",
            ", who ",
            ", whom ",
            ", whose ",
            ", where ",
            ", when ",
            ", why ",
            " because ",
            " although ",
            " though ",
            " even though ",
            " while ",
            " whereas ",
            " if ",
            " unless ",
            " until ",
            " since ",
            " as ",
            " as if ",
            " as though ",
        ]

        for marker in markers:
            if marker in sentence.lower():
                parts = sentence.lower().split(marker, 1)

                # Determine which part is the independent clause
                if "." in parts[0] or "!" in parts[0] or "?" in parts[0]:
                    # First part is a complete sentence
                    return parts[0] + ". " + parts[1].capitalize()
                else:
                    # Second part might be the independent clause
                    return parts[0] + ". " + parts[1].capitalize()

        # If no clear way to split, return original
        return sentence

    def _complexify_sentence(self, sentence: str, all_sentences: List[str]) -> str:
        """
        Make a simple sentence more complex.

        Args:
            sentence: Sentence to make more complex
            all_sentences: All sentences in the text

        Returns:
            More complex sentence
        """
        # Try to combine with adjacent sentence
        index = all_sentences.index(sentence)

        if index < len(all_sentences) - 1:
            next_sentence = all_sentences[index + 1]

            # Check if next sentence is short
            if len(self._get_words(next_sentence)) < 10:
                # Combine with conjunction
                conjunctions = [", and ", ", but ", ", or ", ", yet ", ", so "]
                conjunction = random.choice(conjunctions)

                return sentence + conjunction + next_sentence[0].lower() + next_sentence[1:]

        # Add a dependent clause
        dependent_clauses = [
            "which is important",
            "which is significant",
            "which is noteworthy",
            "which is beneficial",
            "which is advantageous",
            "which is valuable",
            "which is essential",
            "which is critical",
            "which is crucial",
            "which is necessary",
        ]

        return sentence[:-1] + ", " + random.choice(dependent_clauses) + sentence[-1]

    def _adjust_paragraph_structure(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adjust paragraph structure in content.

        Args:
            content: Content to adjust

        Returns:
            Adjusted content
        """
        # Get target style
        style_data = self.STYLE_CATEGORIES.get(self.target_style, {})
        target_paragraph_length = style_data.get("paragraph_length", "")

        # If no target paragraph length, return content
        if not target_paragraph_length:
            return content

        # Create a copy of the content
        adjusted_content = content.copy()

        # Extract text from content
        text = self._extract_text_from_content()

        # Get paragraphs
        paragraphs = self._get_paragraphs(text)

        # Initialize adjustments
        adjustments = []

        # Process each paragraph
        for paragraph in paragraphs:
            # Get paragraph length
            word_count = len(self._get_words(paragraph))

            # Check if adjustment needed
            if "short" in target_paragraph_length and word_count > 75:
                # Split into shorter paragraphs
                sentences = self._get_sentences(paragraph)
                mid_point = len(sentences) // 2

                first_half = " ".join(sentences[:mid_point])
                second_half = " ".join(sentences[mid_point:])

                adjusted_paragraph = first_half + "\n\n" + second_half

                # Create adjustment
                adjustment = {
                    "id": str(uuid.uuid4()),
                    "type": "paragraph_structure",
                    "original": paragraph,
                    "replacement": adjusted_paragraph,
                    "original_length": word_count,
                    "target_length": "short",
                    "confidence": 0.8,
                    "impact": "medium",
                }

                # Add adjustment
                adjustments.append(adjustment)

                # Replace in content
                for key in adjusted_content:
                    if isinstance(adjusted_content[key], str):
                        adjusted_content[key] = adjusted_content[key].replace(
                            paragraph, adjusted_paragraph
                        )
                    elif isinstance(adjusted_content[key], list):
                        for i, item in enumerate(adjusted_content[key]):
                            if isinstance(item, str):
                                adjusted_content[key][i] = item.replace(
                                    paragraph, adjusted_paragraph
                                )
                            elif isinstance(item, dict):
                                for subkey in item:
                                    if isinstance(item[subkey], str):
                                        item[subkey] = item[subkey].replace(
                                            paragraph, adjusted_paragraph
                                        )

            elif "long" in target_paragraph_length and word_count < 50 and len(paragraphs) > 1:
                # Try to combine with adjacent paragraph
                index = paragraphs.index(paragraph)

                if index < len(paragraphs) - 1:
                    next_paragraph = paragraphs[index + 1]
                    combined = paragraph + " " + next_paragraph

                    # Create adjustment
                    adjustment = {
                        "id": str(uuid.uuid4()),
                        "type": "paragraph_structure",
                        "original": paragraph + "\n\n" + next_paragraph,
                        "replacement": combined,
                        "original_length": word_count,
                        "target_length": "long",
                        "confidence": 0.7,
                        "impact": "medium",
                    }

                    # Add adjustment
                    adjustments.append(adjustment)

                    # Replace in content
                    for key in adjusted_content:
                        if isinstance(adjusted_content[key], str):
                            adjusted_content[key] = adjusted_content[key].replace(
                                paragraph + "\n\n" + next_paragraph, combined
                            )
                        elif isinstance(adjusted_content[key], list):
                            for i, item in enumerate(adjusted_content[key]):
                                if isinstance(item, str):
                                    adjusted_content[key][i] = item.replace(
                                        paragraph + "\n\n" + next_paragraph, combined
                                    )
                                elif isinstance(item, dict):
                                    for subkey in item:
                                        if isinstance(item[subkey], str):
                                            item[subkey] = item[subkey].replace(
                                                paragraph + "\n\n" + next_paragraph,
                                                combined,
                                            )

        # Store adjustments
        self.results["adjustments"]["paragraph_structure"] = adjustments

        return adjusted_content

    def _adjust_punctuation(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adjust punctuation in content.

        Args:
            content: Content to adjust

        Returns:
            Adjusted content
        """
        # Get target style
        style_data = self.STYLE_CATEGORIES.get(self.target_style, {})
        target_punctuation = style_data.get("punctuation", "")

        # If no target punctuation, return content
        if not target_punctuation:
            return content

        # Create a copy of the content
        adjusted_content = content.copy()

        # Extract text from content
        text = self._extract_text_from_content()

        # Get sentences
        sentences = self._get_sentences(text)

        # Initialize adjustments
        adjustments = []

        # Process each sentence
        for sentence in sentences:
            # Count punctuation
            exclamation_count = sentence.count("!")
            question_count = sentence.count("?")
            ellipsis_count = sentence.count("...")
            semicolon_count = sentence.count(";")
            dash_count = sentence.count("-") + sentence.count("—")

            # Check if adjustment needed
            if "emphatic" in target_punctuation:
                # Add more emphatic punctuation
                if (
                    not any([exclamation_count, question_count, ellipsis_count, dash_count])
                    and len(sentence) > 20
                ):
                    # Replace period with exclamation point or add emphasis
                    if sentence.endswith("."):
                        adjusted_sentence = sentence[:-1] + "!"
                    else:
                        adjusted_sentence = sentence + "!"

                    # Create adjustment
                    adjustment = {
                        "id": str(uuid.uuid4()),
                        "type": "punctuation",
                        "original": sentence,
                        "replacement": adjusted_sentence,
                        "target_punctuation": "emphatic",
                        "confidence": 0.6,
                        "impact": "low",
                    }

                    # Add adjustment
                    adjustments.append(adjustment)

                    # Replace in content
                    for key in adjusted_content:
                        if isinstance(adjusted_content[key], str):
                            adjusted_content[key] = adjusted_content[key].replace(
                                sentence, adjusted_sentence
                            )
                        elif isinstance(adjusted_content[key], list):
                            for i, item in enumerate(adjusted_content[key]):
                                if isinstance(item, str):
                                    adjusted_content[key][i] = item.replace(
                                        sentence, adjusted_sentence
                                    )
                                elif isinstance(item, dict):
                                    for subkey in item:
                                        if isinstance(item[subkey], str):
                                            item[subkey] = item[subkey].replace(
                                                sentence, adjusted_sentence
                                            )

            elif "standard" in target_punctuation:
                # Normalize punctuation
                if exclamation_count > 0 or question_count > 0 or ellipsis_count > 0:
                    # Replace excessive punctuation
                    adjusted_sentence = re.sub(r"!+", ".", sentence)
                    adjusted_sentence = re.sub(r"\?+", "?", adjusted_sentence)
                    adjusted_sentence = re.sub(r"\.{3,}", ".", adjusted_sentence)

                    # Create adjustment
                    adjustment = {
                        "id": str(uuid.uuid4()),
                        "type": "punctuation",
                        "original": sentence,
                        "replacement": adjusted_sentence,
                        "target_punctuation": "standard",
                        "confidence": 0.7,
                        "impact": "low",
                    }

                    # Add adjustment
                    adjustments.append(adjustment)

                    # Replace in content
                    for key in adjusted_content:
                        if isinstance(adjusted_content[key], str):
                            adjusted_content[key] = adjusted_content[key].replace(
                                sentence, adjusted_sentence
                            )
                        elif isinstance(adjusted_content[key], list):
                            for i, item in enumerate(adjusted_content[key]):
                                if isinstance(item, str):
                                    adjusted_content[key][i] = item.replace(
                                        sentence, adjusted_sentence
                                    )
                                elif isinstance(item, dict):
                                    for subkey in item:
                                        if isinstance(item[subkey], str):
                                            item[subkey] = item[subkey].replace(
                                                sentence, adjusted_sentence
                                            )

            elif "relaxed" in target_punctuation:
                # Add more casual punctuation
                if (
                    not any([exclamation_count, question_count, ellipsis_count])
                    and len(sentence) > 20
                ):
                    # Add ellipsis or exclamation
                    if random.random() < 0.5:
                        adjusted_sentence = sentence[:-1] + "..."
                    else:
                        adjusted_sentence = sentence[:-1] + "!"

                    # Create adjustment
                    adjustment = {
                        "id": str(uuid.uuid4()),
                        "type": "punctuation",
                        "original": sentence,
                        "replacement": adjusted_sentence,
                        "target_punctuation": "relaxed",
                        "confidence": 0.6,
                        "impact": "low",
                    }

                    # Add adjustment
                    adjustments.append(adjustment)

                    # Replace in content
                    for key in adjusted_content:
                        if isinstance(adjusted_content[key], str):
                            adjusted_content[key] = adjusted_content[key].replace(
                                sentence, adjusted_sentence
                            )
                        elif isinstance(adjusted_content[key], list):
                            for i, item in enumerate(adjusted_content[key]):
                                if isinstance(item, str):
                                    adjusted_content[key][i] = item.replace(
                                        sentence, adjusted_sentence
                                    )
                                elif isinstance(item, dict):
                                    for subkey in item:
                                        if isinstance(item[subkey], str):
                                            item[subkey] = item[subkey].replace(
                                                sentence, adjusted_sentence
                                            )

        # Store adjustments
        self.results["adjustments"]["punctuation"] = adjustments

        return adjusted_content

    def _adjust_voice(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adjust voice in content.

        Args:
            content: Content to adjust

        Returns:
            Adjusted content
        """
        # Get target style
        style_data = self.STYLE_CATEGORIES.get(self.target_style, {})
        target_voice = style_data.get("voice", "")

        # If no target voice, return content
        if not target_voice:
            return content

        # Create a copy of the content
        adjusted_content = content.copy()

        # Extract text from content
        text = self._extract_text_from_content()

        # Get sentences
        sentences = self._get_sentences(text)

        # Initialize adjustments
        adjustments = []

        # Process each sentence
        for sentence in sentences:
            # Check if sentence is in passive voice
            is_passive = self._is_passive_voice(sentence)

            # Check if adjustment needed
            if "active" in target_voice and is_passive:
                # Convert to active voice
                adjusted_sentence = self._convert_to_active_voice(sentence)

                # Only adjust if the sentence actually changed
                if adjusted_sentence != sentence:
                    # Create adjustment
                    adjustment = {
                        "id": str(uuid.uuid4()),
                        "type": "voice",
                        "original": sentence,
                        "replacement": adjusted_sentence,
                        "original_voice": "passive",
                        "target_voice": "active",
                        "confidence": 0.7,
                        "impact": "medium",
                    }

                    # Add adjustment
                    adjustments.append(adjustment)

                    # Replace in content
                    for key in adjusted_content:
                        if isinstance(adjusted_content[key], str):
                            adjusted_content[key] = adjusted_content[key].replace(
                                sentence, adjusted_sentence
                            )
                        elif isinstance(adjusted_content[key], list):
                            for i, item in enumerate(adjusted_content[key]):
                                if isinstance(item, str):
                                    adjusted_content[key][i] = item.replace(
                                        sentence, adjusted_sentence
                                    )
                                elif isinstance(item, dict):
                                    for subkey in item:
                                        if isinstance(item[subkey], str):
                                            item[subkey] = item[subkey].replace(
                                                sentence, adjusted_sentence
                                            )

            elif "passive" in target_voice and not is_passive:
                # Convert to passive voice
                adjusted_sentence = self._convert_to_passive_voice(sentence)

                # Only adjust if the sentence actually changed
                if adjusted_sentence != sentence:
                    # Create adjustment
                    adjustment = {
                        "id": str(uuid.uuid4()),
                        "type": "voice",
                        "original": sentence,
                        "replacement": adjusted_sentence,
                        "original_voice": "active",
                        "target_voice": "passive",
                        "confidence": 0.6,
                        "impact": "medium",
                    }

                    # Add adjustment
                    adjustments.append(adjustment)

                    # Replace in content
                    for key in adjusted_content:
                        if isinstance(adjusted_content[key], str):
                            adjusted_content[key] = adjusted_content[key].replace(
                                sentence, adjusted_sentence
                            )
                        elif isinstance(adjusted_content[key], list):
                            for i, item in enumerate(adjusted_content[key]):
                                if isinstance(item, str):
                                    adjusted_content[key][i] = item.replace(
                                        sentence, adjusted_sentence
                                    )
                                elif isinstance(item, dict):
                                    for subkey in item:
                                        if isinstance(item[subkey], str):
                                            item[subkey] = item[subkey].replace(
                                                sentence, adjusted_sentence
                                            )

        # Store adjustments
        self.results["adjustments"]["voice"] = adjustments

        return adjusted_content

    def get_suggestions(self) -> List[Dict[str, Any]]:
        """
        Get suggestions for style adjustments.

        Returns:
            List of suggestion dictionaries
        """
        # Analyze content if not already analyzed
        if self.results is None:
            self.analyze()

        # Get all adjustments
        all_adjustments = []

        for adjustment_type, adjustments in self.results["adjustments"].items():
            all_adjustments.extend(adjustments)

        # Sort adjustments by priority
        prioritized_adjustments = self._prioritize_adjustments(all_adjustments)

        # Limit to max suggestions
        max_suggestions = self.config["max_suggestions"]
        limited_adjustments = prioritized_adjustments[:max_suggestions]

        # Convert adjustments to suggestions
        suggestions = []

        for adjustment in limited_adjustments:
            suggestion = self._adjustment_to_suggestion(adjustment)
            suggestions.append(suggestion)

        return suggestions

    def _prioritize_adjustments(self, adjustments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize adjustments.

        Args:
            adjustments: List of adjustments

        Returns:
            Prioritized list of adjustments
        """
        # Get prioritization method
        prioritize_by = self.config["prioritize_by"]

        if prioritize_by == "impact":
            # Sort by impact (high, medium, low)
            impact_order = {"high": 0, "medium": 1, "low": 2}
            return sorted(
                adjustments,
                key=lambda x: (
                    impact_order.get(x["impact"], 3),
                    -x.get("confidence", 0),
                ),
            )

        elif prioritize_by == "confidence":
            # Sort by confidence (highest first)
            return sorted(adjustments, key=lambda x: -x.get("confidence", 0))

        elif prioritize_by == "position":
            # Sort by position in text (earliest first)
            # This requires position information, which we don't always have
            # Fall back to impact if position is not available
            if all("position" in adjustment for adjustment in adjustments):
                return sorted(
                    adjustments,
                    key=lambda x: x["position"][0] if "position" in x else float("inf"),
                )
            else:
                impact_order = {"high": 0, "medium": 1, "low": 2}
                return sorted(
                    adjustments,
                    key=lambda x: (
                        impact_order.get(x["impact"], 3),
                        -x.get("confidence", 0),
                    ),
                )

        # Default to impact
        impact_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            adjustments,
            key=lambda x: (impact_order.get(x["impact"], 3), -x.get("confidence", 0)),
        )

    def _adjustment_to_suggestion(self, adjustment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert an adjustment to a suggestion.

        Args:
            adjustment: Adjustment dictionary

        Returns:
            Suggestion dictionary
        """
        # Create base suggestion
        suggestion = {
            "id": adjustment["id"],
            "type": adjustment["type"],
            "original": adjustment["original"],
            "replacement": adjustment["replacement"],
            "confidence": adjustment.get("confidence", 0.0),
            "impact": adjustment.get("impact", "low"),
        }

        # Add type-specific fields
        if adjustment["type"] == "word_choice":
            suggestion["message"] = (
                f"Replace '{adjustment['original']}' with '{adjustment['replacement']}' for a more {self.target_style} style."
            )
            suggestion["explanation"] = (
                f"The word '{adjustment['original']}' is not typical of {self.target_style} writing. '{adjustment['replacement']}' is a better choice for this style."
            )

        elif adjustment["type"] == "sentence_structure":
            if "simple" in adjustment.get("target_structure", ""):
                suggestion["message"] = "Simplify this sentence for a more direct style."
                suggestion["explanation"] = (
                    "This sentence is too complex for the target style. Breaking it into shorter, simpler sentences will improve readability and match the desired style better."
                )
            else:
                suggestion["message"] = (
                    "Make this sentence more complex for a more sophisticated style."
                )
                suggestion["explanation"] = (
                    "This sentence is too simple for the target style. Adding more complexity will make it match the desired style better."
                )

        elif adjustment["type"] == "paragraph_structure":
            if adjustment.get("target_length", "") == "short":
                suggestion["message"] = "Break this paragraph into smaller ones."
                suggestion["explanation"] = (
                    "This paragraph is too long for the target style. Shorter paragraphs improve readability and match the desired style better."
                )
            else:
                suggestion["message"] = "Combine this paragraph with the next one."
                suggestion["explanation"] = (
                    "This paragraph is too short for the target style. Combining it with another paragraph will make it match the desired style better."
                )

        elif adjustment["type"] == "punctuation":
            if adjustment.get("target_punctuation", "") == "emphatic":
                suggestion["message"] = "Use more emphatic punctuation."
                suggestion["explanation"] = (
                    "The target style uses more emphatic punctuation to engage readers. Adding exclamation points or other emphatic punctuation will make the content more engaging."
                )
            elif adjustment.get("target_punctuation", "") == "standard":
                suggestion["message"] = "Use more standard punctuation."
                suggestion["explanation"] = (
                    "The target style uses more standard punctuation. Normalizing punctuation will make the content more professional and match the desired style better."
                )
            else:
                suggestion["message"] = "Use more relaxed punctuation."
                suggestion["explanation"] = (
                    "The target style uses more relaxed punctuation. Adding ellipses or other casual punctuation will make the content more conversational."
                )

        elif adjustment["type"] == "voice":
            if adjustment.get("target_voice", "") == "active":
                suggestion["message"] = "Convert this sentence to active voice."
                suggestion["explanation"] = (
                    "The target style prefers active voice. Converting passive voice to active voice will make the content more direct and engaging."
                )
            else:
                suggestion["message"] = "Convert this sentence to passive voice."
                suggestion["explanation"] = (
                    "The target style allows or prefers passive voice in some contexts. Converting active voice to passive voice can make the content more formal or objective."
                )

        # Add examples
        suggestion["examples"] = [
            {
                "original": adjustment["original"],
                "replacement": adjustment["replacement"],
            }
        ]

        return suggestion

    def apply_suggestion(self, suggestion_id: str) -> Dict[str, Any]:
        """
        Apply a specific suggestion to the content.

        Args:
            suggestion_id: ID of the suggestion to apply

        Returns:
            Updated content
        """
        # Find the suggestion
        suggestion = None

        for adjustment_type, adjustments in self.results["adjustments"].items():
            for adjustment in adjustments:
                if adjustment["id"] == suggestion_id:
                    suggestion = adjustment
                    break

            if suggestion:
                break

        if not suggestion:
            raise ValueError(f"Suggestion with ID {suggestion_id} not found")

        # Create a copy of the content
        adjusted_content = self.content.copy()

        # Apply the suggestion
        for key in adjusted_content:
            if isinstance(adjusted_content[key], str):
                adjusted_content[key] = adjusted_content[key].replace(
                    suggestion["original"], suggestion["replacement"]
                )
            elif isinstance(adjusted_content[key], list):
                for i, item in enumerate(adjusted_content[key]):
                    if isinstance(item, str):
                        adjusted_content[key][i] = item.replace(
                            suggestion["original"], suggestion["replacement"]
                        )
                    elif isinstance(item, dict):
                        for subkey in item:
                            if isinstance(item[subkey], str):
                                item[subkey] = item[subkey].replace(
                                    suggestion["original"], suggestion["replacement"]
                                )

        # Update content
        self.content = adjusted_content

        # Re-analyze
        self.analyze()

        return self.content

    def apply_all_suggestions(self) -> Dict[str, Any]:
        """
        Apply all suggestions to the content.

        Returns:
            Updated content
        """
        # Get all suggestions
        suggestions = self.get_suggestions()

        # Apply each suggestion
        for suggestion in suggestions:
            self.apply_suggestion(suggestion["id"])

        return self.content

    def get_style_report(self) -> Dict[str, Any]:
        """
        Get a report on the style of the content.

        Returns:
            Style report dictionary
        """
        # Analyze content if not already analyzed
        if self.results is None:
            self.analyze()

        # Get analysis results
        analysis = self.results["analysis"]

        # Create report
        report = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "content_id": self.content.get("id", "unknown"),
            "target_style": self.target_style,
            "current_style": analysis["tone_analysis"]["dominant_tone"],
            "style_match": analysis["tone_analysis"]["target_tone"]
            == analysis["tone_analysis"]["dominant_tone"],
            "style_consistency": analysis["tone_analysis"]["consistency"],
            "sentiment": analysis["sentiment_analysis"]["dominant_sentiment"],
            "sentiment_consistency": analysis["sentiment_analysis"]["consistency"],
            "readability": {
                "grade_level": analysis.get("readability_scores", {}).get("grade_level", 0),
                "reading_ease": analysis.get("readability_scores", {})
                .get("flesch_reading_ease", {})
                .get("score", 0),
            },
            "style_elements": {
                "word_choice": self._get_word_choice_report(),
                "sentence_structure": self._get_sentence_structure_report(),
                "paragraph_structure": self._get_paragraph_structure_report(),
                "punctuation": self._get_punctuation_report(),
                "voice": self._get_voice_report(),
            },
            "suggestions_count": len(self.get_suggestions()),
            "improvement_potential": self._get_improvement_potential(),
        }

        return report

    def _get_word_choice_report(self) -> Dict[str, Any]:
        """
        Get a report on word choice.

        Returns:
            Word choice report dictionary
        """
        # Get word choice adjustments
        adjustments = self.results["adjustments"]["word_choice"]

        # Count adjustments
        count = len(adjustments)

        # Calculate impact
        impact = sum(1 for adj in adjustments if adj["impact"] == "high") * 3
        impact += sum(1 for adj in adjustments if adj["impact"] == "medium") * 2
        impact += sum(1 for adj in adjustments if adj["impact"] == "low")

        # Normalize impact
        if count > 0:
            impact = impact / (count * 3)
        else:
            impact = 0

        return {
            "count": count,
            "impact": impact,
            "examples": [adj["original"] for adj in adjustments[:3]],
        }

    def _get_sentence_structure_report(self) -> Dict[str, Any]:
        """
        Get a report on sentence structure.

        Returns:
            Sentence structure report dictionary
        """
        # Get sentence structure adjustments
        adjustments = self.results["adjustments"]["sentence_structure"]

        # Count adjustments
        count = len(adjustments)

        # Calculate impact
        impact = sum(1 for adj in adjustments if adj["impact"] == "high") * 3
        impact += sum(1 for adj in adjustments if adj["impact"] == "medium") * 2
        impact += sum(1 for adj in adjustments if adj["impact"] == "low")

        # Normalize impact
        if count > 0:
            impact = impact / (count * 3)
        else:
            impact = 0

        return {
            "count": count,
            "impact": impact,
            "examples": [adj["original"] for adj in adjustments[:3]],
        }

    def _get_paragraph_structure_report(self) -> Dict[str, Any]:
        """
        Get a report on paragraph structure.

        Returns:
            Paragraph structure report dictionary
        """
        # Get paragraph structure adjustments
        adjustments = self.results["adjustments"]["paragraph_structure"]

        # Count adjustments
        count = len(adjustments)

        # Calculate impact
        impact = sum(1 for adj in adjustments if adj["impact"] == "high") * 3
        impact += sum(1 for adj in adjustments if adj["impact"] == "medium") * 2
        impact += sum(1 for adj in adjustments if adj["impact"] == "low")

        # Normalize impact
        if count > 0:
            impact = impact / (count * 3)
        else:
            impact = 0

        return {
            "count": count,
            "impact": impact,
            "examples": [adj["original"][:100] + "..." for adj in adjustments[:3]],
        }

    def _get_punctuation_report(self) -> Dict[str, Any]:
        """
        Get a report on punctuation.

        Returns:
            Punctuation report dictionary
        """
        # Get punctuation adjustments
        adjustments = self.results["adjustments"]["punctuation"]

        # Count adjustments
        count = len(adjustments)

        # Calculate impact
        impact = sum(1 for adj in adjustments if adj["impact"] == "high") * 3
        impact += sum(1 for adj in adjustments if adj["impact"] == "medium") * 2
        impact += sum(1 for adj in adjustments if adj["impact"] == "low")

        # Normalize impact
        if count > 0:
            impact = impact / (count * 3)
        else:
            impact = 0

        return {
            "count": count,
            "impact": impact,
            "examples": [adj["original"] for adj in adjustments[:3]],
        }

    def _get_voice_report(self) -> Dict[str, Any]:
        """
        Get a report on voice.

        Returns:
            Voice report dictionary
        """
        # Get voice adjustments
        adjustments = self.results["adjustments"]["voice"]

        # Count adjustments
        count = len(adjustments)

        # Calculate impact
        impact = sum(1 for adj in adjustments if adj["impact"] == "high") * 3
        impact += sum(1 for adj in adjustments if adj["impact"] == "medium") * 2
        impact += sum(1 for adj in adjustments if adj["impact"] == "low")

        # Normalize impact
        if count > 0:
            impact = impact / (count * 3)
        else:
            impact = 0

        return {
            "count": count,
            "impact": impact,
            "examples": [adj["original"] for adj in adjustments[:3]],
        }

    def _get_improvement_potential(self) -> float:
        """
        Calculate the potential for improvement.

        Returns:
            Improvement potential score (0-1)
        """
        # Get all adjustments
        all_adjustments = []

        for adjustment_type, adjustments in self.results["adjustments"].items():
            all_adjustments.extend(adjustments)

        # Count adjustments by impact
        high_impact = sum(1 for adj in all_adjustments if adj["impact"] == "high")
        medium_impact = sum(1 for adj in all_adjustments if adj["impact"] == "medium")
        low_impact = sum(1 for adj in all_adjustments if adj["impact"] == "low")

        # Calculate weighted impact
        weighted_impact = (high_impact * 3) + (medium_impact * 2) + low_impact

        # Get text length
        text = self._extract_text_from_content()
        word_count = len(self._get_words(text))

        # Normalize by text length
        if word_count > 0:
            normalized_impact = weighted_impact / (word_count / 100)
        else:
            normalized_impact = 0

        # Clamp to 0-1 range
        return min(1.0, normalized_impact / 10)
