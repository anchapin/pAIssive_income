"""
Tone analyzer module for the pAIssive Income project.

This module provides classes for analyzing and adjusting the tone of content.
"""

import time

from datetime import datetime


import datetime
import json
import math
import re
import string
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import sent_tokenize, word_tokenize

NLTK_AVAILABLE 

# Third-party imports
try:

= True
except ImportError:
    NLTK_AVAILABLE = False

# We'll define our own base class to avoid circular imports
# This is similar to SEOAnalyzer from content_optimization.py but independent


class ContentAnalyzer(ABC):
    """
    Abstract base class for content analyzers.

This class provides common functionality for all content analyzers,
    including configuration, analysis, and reporting.
    """

def __init__(
        self,
        content: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a content analyzer.

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
        Analyze the content.

Returns:
            Dictionary with analysis results
        """
        pass

@abstractmethod
    def get_score(self) -> float:
        """
        Get the overall score for the content.

Returns:
            Score between 0 and 1
        """
        pass

@abstractmethod
    def get_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get recommendations for the content.

Returns:
            List of recommendation dictionaries
        """
        pass

def get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration for the analyzer.

Returns:
            Default configuration dictionary
        """
                    return {"timestamp": datetime.datetime.now().isoformat()}

def validate_config(self) -> Tuple[bool, List[str]]:
        """
        Validate the configuration dictionary.

Returns:
            Tuple of (is_valid, error_messages)
        """
                    return True, []

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

def to_dict(self) -> Dict[str, Any]:
        """
        Convert the analyzer to a dictionary.

Returns:
            Dictionary representation of the analyzer
        """
                    return {
            "id": self.id,
            "config": self.config,
            "created_at": self.created_at,
            "results": self.results,
        }

def to_json(self, indent: int = 2) -> str:
        """
        Convert the analyzer to a JSON string.

Args:
            indent: Number of spaces for indentation

Returns:
            JSON string representation of the analyzer
        """
                    return json.dumps(self.to_dict(), indent=indent)


class ToneAnalyzer(ContentAnalyzer):
    """
    Class for analyzing and adjusting the tone of content.

This class provides methods for analyzing tone, sentiment, and style
    in content, and making recommendations for adjustments.
    """

# Define tone categories
    TONE_CATEGORIES = {
        "formal": {
            "description": "Professional, academic, or business-like tone",
            "patterns": [
                r"\b(?:therefore|consequently|furthermore|thus|hence|accordingly)\b",
                r"\b(?:utilize|implement|facilitate|demonstrate|indicate|necessitate)\b",
                r"\b(?:in conclusion|in summary|to summarize|in essence)\b",
                r"\b(?:it is|there are|this is|these are)\b",
                r"\b(?:one|we|our|us)\b",
            ],
            "anti_patterns": [
                r"\b(?:awesome|cool|wow|yeah|hey|ok|okay)\b",
                r"\b(?:gonna|wanna|gotta|kinda|sorta)\b",
                r"(?:!{2,}|\?{2,})",
                r"\b(?:lol|omg|btw|imo|tbh)\b",
                r"(?:\:D|\:P|\;\)|\:\))",
            ],
        },
        "conversational": {
            "description": "Friendly, casual, or personal tone",
            "patterns": [
                r"\b(?:you|your|you'll|you're|you've|you'd)\b",
                r"\b(?:I|me|my|mine|we|us|our|ours)\b",
                r"\b(?:let's|let me|here's|there's|that's)\b",
                r"\b(?:actually|basically|literally|honestly|seriously)\b",
                r"\b(?:great|awesome|amazing|fantastic|wonderful)\b",
            ],
            "anti_patterns": [
                r"\b(?:hereby|therein|aforementioned|heretofore)\b",
                r"\b(?:pursuant|notwithstanding|henceforth)\b",
                r"\b(?:it is necessary to|it is important to|it is essential to)\b",
                r"\b(?:the author|the researcher|the study)\b",
                r"\b(?:shall|must|ought)\b",
            ],
        },
        "persuasive": {
            "description": "Convincing, compelling, or sales-oriented tone",
            "patterns": [
                r"\b(?:you need|you want|you deserve|you can't afford to miss|you should)\b",
                r"\b(?:limited time|exclusive|special offer|bonus|free)\b",
                r"\b(?:guarantee|proven|results|success|transform)\b",
                r"\b(?:imagine|picture|consider|what if|how would)\b",
                r"\b(?:but wait|act now|don't miss|hurry|today)\b",
            ],
            "anti_patterns": [
                r"\b(?:perhaps|maybe|possibly|might|could be)\b",
                r"\b(?:somewhat|relatively|comparatively|moderately)\b",
                r"\b(?:it seems|it appears|it may be|it could be)\b",
                r"\b(?:in my opinion|I think|I believe|I feel)\b",
                r"\b(?:unclear|uncertain|unknown|undetermined)\b",
            ],
        },
        "informative": {
            "description": "Educational, explanatory, or factual tone",
            "patterns": [
                r"\b(?:according to|research shows|studies indicate|data suggests|experts say)\b",
                r"\b(?:for example|for instance|such as|including|specifically)\b",
                r"\b(?:defined as|refers to|means|consists of|comprises)\b",
                r"\b(?:first|second|third|finally|lastly|next|then)\b",
                r"\b(?:causes|effects|results in|leads to|contributes to)\b",
            ],
            "anti_patterns": [
                r"\b(?:I guess|I suppose|I assume|I reckon)\b",
                r"\b(?:kinda|sorta|pretty much|more or less)\b",
                r"\b(?:stuff|things|whatever|anyway|somehow)\b",
                r"\b(?:like|you know|I mean|well|so)\b",
                r"\b(?:probably|hopefully|maybe|perhaps)\b",
            ],
        },
        "inspirational": {
            "description": "Motivational, uplifting, or encouraging tone",
            "patterns": [
                r"\b(?:achieve|accomplish|overcome|succeed|excel)\b",
                r"\b(?:dream|passion|purpose|mission|vision)\b",
                r"\b(?:potential|possibility|opportunity|chance|prospect)\b",
                r"\b(?:believe|trust|faith|hope|courage)\b",
                r"\b(?:inspire|motivate|encourage|empower|uplift)\b",
            ],
            "anti_patterns": [
                r"\b(?:impossible|hopeless|pointless|useless|worthless)\b",
                r"\b(?:fail|failure|defeat|lose|loss)\b",
                r"\b(?:problem|issue|trouble|difficulty|obstacle)\b",
                r"\b(?:hard|difficult|challenging|tough|demanding)\b",
                r"\b(?:unfortunately|sadly|regrettably|disappointingly)\b",
            ],
        },
        "humorous": {
            "description": "Funny, witty, or entertaining tone",
            "patterns": [
                r"\b(?:funny|hilarious|amusing|entertaining|comical)\b",
                r"\b(?:joke|laugh|humor|wit|pun)\b",
                r"\b(?:ridiculous|absurd|silly|crazy|wild)\b",
                r"(?:!{2,}|\?{2,}|…)",
                r"(?:\:D|\:P|\;\)|\:\))",
            ],
            "anti_patterns": [
                r"\b(?:serious|solemn|grave|somber|formal)\b",
                r"\b(?:tragic|sad|unfortunate|regrettable|lamentable)\b",
                r"\b(?:professional|business|corporate|official)\b",
                r"\b(?:analysis|research|study|investigation|examination)\b",
                r"\b(?:pursuant|henceforth|therefore|thus|hence)\b",
            ],
        },
    }

# Define sentiment categories
    SENTIMENT_CATEGORIES = {
        "positive": [
            "good",
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "fantastic",
            "terrific",
            "outstanding",
            "superb",
            "brilliant",
            "exceptional",
            "marvelous",
            "fabulous",
            "splendid",
            "delightful",
            "happy",
            "glad",
            "pleased",
            "satisfied",
            "content",
            "joyful",
            "cheerful",
            "thrilled",
            "excited",
            "enthusiastic",
            "passionate",
            "eager",
            "motivated",
            "inspired",
            "encouraged",
            "love",
            "like",
            "enjoy",
            "appreciate",
            "admire",
            "respect",
            "value",
            "cherish",
            "benefit",
            "advantage",
            "gain",
            "profit",
            "reward",
            "success",
            "achievement",
            "accomplishment",
            "improve",
            "enhance",
            "boost",
            "increase",
            "grow",
            "develop",
            "progress",
            "advance",
        ],
        "negative": [
            "bad",
            "poor",
            "terrible",
            "horrible",
            "awful",
            "dreadful",
            "abysmal",
            "atrocious",
            "subpar",
            "inferior",
            "mediocre",
            "disappointing",
            "unsatisfactory",
            "inadequate",
            "insufficient",
            "sad",
            "unhappy",
            "upset",
            "disappointed",
            "frustrated",
            "annoyed",
            "angry",
            "irritated",
            "worried",
            "concerned",
            "anxious",
            "nervous",
            "stressed",
            "overwhelmed",
            "exhausted",
            "hate",
            "dislike",
            "despise",
            "detest",
            "loathe",
            "resent",
            "reject",
            "avoid",
            "problem",
            "issue",
            "challenge",
            "difficulty",
            "obstacle",
            "barrier",
            "hurdle",
            "setback",
            "fail",
            "failure",
            "loss",
            "defeat",
            "decline",
            "decrease",
            "reduce",
            "diminish",
        ],
        "neutral": [
            "okay",
            "fine",
            "average",
            "moderate",
            "fair",
            "reasonable",
            "acceptable",
            "adequate",
            "normal",
            "standard",
            "typical",
            "common",
            "usual",
            "regular",
            "ordinary",
            "conventional",
            "think",
            "believe",
            "consider",
            "regard",
            "view",
            "perceive",
            "understand",
            "comprehend",
            "seem",
            "appear",
            "look",
            "sound",
            "feel",
            "sense",
            "experience",
            "observe",
            "perhaps",
            "maybe",
            "possibly",
            "potentially",
            "conceivably",
            "presumably",
            "supposedly",
            "apparently",
            "sometimes",
            "occasionally",
            "periodically",
            "intermittently",
            "sporadically",
            "infrequently",
            "rarely",
            "seldom",
        ],
    }

def __init__(
        self,
        content: Optional[Dict[str, Any]] = None,
        target_tone: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a tone analyzer.

Args:
            content: Optional content to analyze
            target_tone: Optional target tone for the content
            config: Optional configuration dictionary
        """
        super().__init__(content, config)

# Set target tone
        self.target_tone = target_tone

# Initialize NLTK if available
        if NLTK_AVAILABLE:
            try:
                nltk.data.find("tokenizers/punkt")
            except LookupError:
                nltk.download("punkt")

def get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration for the tone analyzer.

Returns:
            Default configuration dictionary
        """
        # Start with base config
        config = super().get_default_config()

# Add tone-specific config
        config.update(
            {
                "min_tone_consistency": 0.7,  # Minimum consistency score for the target tone
                "min_sentiment_consistency": 0.6,  # Minimum consistency score for the target sentiment
                "tone_pattern_weight": 0.6,  # Weight for tone pattern matching
                "tone_anti_pattern_weight": 0.4,  # Weight for tone anti-pattern matching
                "sentiment_weight": 0.3,  # Weight for sentiment analysis
                "check_tone_consistency": True,  # Whether to check tone consistency
                "check_sentiment_consistency": True,  # Whether to check sentiment consistency
                "check_style_consistency": True,  # Whether to check style consistency
                "target_tone": self.target_tone
                or "conversational",  # Default target tone
                "target_sentiment": "positive",  # Default target sentiment
                "timestamp": datetime.datetime.now().isoformat(),
            }
        )

            return config

def set_target_tone(self, target_tone: str) -> None:
        """
        Set the target tone for the content.

Args:
            target_tone: Target tone
        """
        if target_tone not in self.TONE_CATEGORIES:
            raise ValueError(
                f"Invalid target tone: {target_tone}. Must be one of: {', '.join(self.TONE_CATEGORIES.keys())}"
            )

self.target_tone = target_tone
        self.config["target_tone"] = target_tone
        self.results = None  # Reset results

def validate_content(self) -> Tuple[bool, List[str]]:
        """
        Validate the content for tone analysis.

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

# Check if target tone is valid
        if self.target_tone and self.target_tone not in self.TONE_CATEGORIES:
            errors.append(
                f"Invalid target tone: {self.target_tone}. Must be one of: {', '.join(self.TONE_CATEGORIES.keys())}"
            )

            return len(errors) == 0, errors

def analyze(self) -> Dict[str, Any]:
        """
        Analyze the content for tone and sentiment.

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
            "target_tone": self.config["target_tone"],
            "target_sentiment": self.config["target_sentiment"],
            "tone_analysis": {},
            "sentiment_analysis": {},
            "style_analysis": {},
            "overall_score": 0.0,
            "recommendations": [],
        }

# Analyze tone
        self.results["tone_analysis"] = self._analyze_tone(text)

# Analyze sentiment
        self.results["sentiment_analysis"] = self._analyze_sentiment(text)

# Analyze style
        self.results["style_analysis"] = self._analyze_style(text)

# Calculate overall score
        self.results["overall_score"] = self.get_score()

# Generate recommendations
        self.results["recommendations"] = self.get_recommendations()

            return self.results

def _analyze_tone(self, text: str) -> Dict[str, Any]:
        """
        Analyze the tone of the text.

Args:
            text: Text to analyze

Returns:
            Dictionary with tone analysis results
        """
        # Get sentences
        sentences = self._get_sentences(text)

# Initialize tone scores
        tone_scores = {}

# Analyze each tone category
        for tone, tone_data in self.TONE_CATEGORIES.items():
            # Count pattern matches
            pattern_matches = 0

for pattern in tone_data["patterns"]:
                pattern_matches += len(re.findall(pattern, text, re.IGNORECASE))

# Count anti-pattern matches
            anti_pattern_matches = 0

for pattern in tone_data["anti_patterns"]:
                anti_pattern_matches += len(re.findall(pattern, text, re.IGNORECASE))

# Calculate tone score
            pattern_weight = self.config["tone_pattern_weight"]
            anti_pattern_weight = self.config["tone_anti_pattern_weight"]

# Normalize by number of sentences
            pattern_score = pattern_matches / len(sentences) if sentences else 0
            anti_pattern_score = (
                anti_pattern_matches / len(sentences) if sentences else 0
            )

# Calculate weighted score
            tone_score = (pattern_score * pattern_weight) - (
                anti_pattern_score * anti_pattern_weight
            )

# Clamp score to 0-1 range
            tone_score = max(0, min(1, tone_score))

# Store tone score
            tone_scores[tone] = {
                "score": tone_score,
                "pattern_matches": pattern_matches,
                "anti_pattern_matches": anti_pattern_matches,
                "is_target": tone == self.config["target_tone"],
            }

# Determine dominant tone
        dominant_tone = max(tone_scores.items(), key=lambda x: x[1]["score"])

# Calculate consistency with target tone
        target_tone = self.config["target_tone"]
        target_score = tone_scores[target_tone]["score"]
        consistency = (
            target_score / dominant_tone[1]["score"]
            if dominant_tone[1]["score"] > 0
            else 0
        )

            return {
            "tone_scores": tone_scores,
            "dominant_tone": dominant_tone[0],
            "dominant_tone_score": dominant_tone[1]["score"],
            "target_tone": target_tone,
            "target_tone_score": target_score,
            "consistency": consistency,
            "is_consistent": consistency >= self.config["min_tone_consistency"],
        }

def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of the text.

Args:
            text: Text to analyze

Returns:
            Dictionary with sentiment analysis results
        """
        # Get words
        words = self._get_words(text)

# Initialize sentiment counts
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}

# Count sentiment words
        for word in words:
            word = word.lower()

if word in self.SENTIMENT_CATEGORIES["positive"]:
                sentiment_counts["positive"] += 1
            elif word in self.SENTIMENT_CATEGORIES["negative"]:
                sentiment_counts["negative"] += 1
            elif word in self.SENTIMENT_CATEGORIES["neutral"]:
                sentiment_counts["neutral"] += 1

# Calculate total sentiment words
        total_sentiment_words = sum(sentiment_counts.values())

# Calculate sentiment scores
        sentiment_scores = {}

for sentiment, count in sentiment_counts.items():
            score = count / total_sentiment_words if total_sentiment_words > 0 else 0

sentiment_scores[sentiment] = {
                "count": count,
                "score": score,
                "is_target": sentiment == self.config["target_sentiment"],
            }

# Determine dominant sentiment
        dominant_sentiment = max(sentiment_scores.items(), key=lambda x: x[1]["score"])

# Calculate consistency with target sentiment
        target_sentiment = self.config["target_sentiment"]
        target_score = sentiment_scores[target_sentiment]["score"]
        consistency = (
            target_score / dominant_sentiment[1]["score"]
            if dominant_sentiment[1]["score"] > 0
            else 0
        )

            return {
            "sentiment_scores": sentiment_scores,
            "dominant_sentiment": dominant_sentiment[0],
            "dominant_sentiment_score": dominant_sentiment[1]["score"],
            "target_sentiment": target_sentiment,
            "target_sentiment_score": target_score,
            "consistency": consistency,
            "is_consistent": consistency >= self.config["min_sentiment_consistency"],
        }

def _extract_text_from_content(self) -> str:
        """
        Extract text from content for analysis.

Returns:
            Extracted text
        """
        if not self.content:
                        return ""

text = ""

# Add title
        if "title" in self.content:
            text += self.content["title"] + " "

# Add meta description
        if "meta_description" in self.content:
            text += self.content["meta_description"] + " "

# Add introduction
        if "introduction" in self.content:
            text += self.content["introduction"] + "\n\n"

# Add sections
        if "sections" in self.content:
            for section in self.content["sections"]:
                if "title" in section:
                    text += section["title"] + " "

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
                    text += feature["name"] + " "

if "description" in feature:
                    text += feature["description"] + "\n\n"

# Add benefits (for product descriptions)
        if "benefits" in self.content:
            for benefit in self.content["benefits"]:
                if "name" in benefit:
                    text += benefit["name"] + " "

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
            tokens = word_tokenize(text.lower())

# Remove punctuation and stopwords
            stop_words = set(stopwords.words("english"))
            tokens = [
                token for token in tokens if token.isalnum() and token not in stop_words
            ]
        else:
            # Simple word tokenization
            # Remove punctuation
            text = re.sub(r"[^\w\s]", "", text.lower())

# Split on whitespace
            tokens = text.split()

            return tokens

def _analyze_style(self, text: str) -> Dict[str, Any]:
        """
        Analyze the writing style of the text.

Args:
            text: Text to analyze

Returns:
            Dictionary with style analysis results
        """
        # Get sentences and words
        sentences = self._get_sentences(text)
        words = self._get_words(text)

# Analyze sentence length variety
        sentence_lengths = [len(self._get_words(sentence)) for sentence in sentences]

# Calculate standard deviation of sentence lengths
        mean_length = (
            sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        )
        variance = (
            sum((length - mean_length) ** 2 for length in sentence_lengths)
            / len(sentence_lengths)
            if sentence_lengths
            else 0
        )
        std_dev = math.sqrt(variance)

# Calculate coefficient of variation (normalized standard deviation)
        cv = std_dev / mean_length if mean_length > 0 else 0

# Analyze vocabulary variety
        unique_words = len(set(words))
        vocabulary_variety = unique_words / len(words) if words else 0

# Analyze punctuation
        punctuation_count = sum(1 for char in text if char in string.punctuation)
        punctuation_density = punctuation_count / len(text) if text else 0

            return {
            "sentence_length_variety": {"score": cv, "is_optimal": cv >= 0.2},
            "vocabulary_variety": {
                "score": vocabulary_variety,
                "unique_words": unique_words,
                "total_words": len(words),
                "is_optimal": vocabulary_variety >= 0.4,
            },
            "punctuation": {
                "count": punctuation_count,
                "density": punctuation_density,
                "is_optimal": 0.05 <= punctuation_density <= 0.1,
            },
        }

def get_score(self) -> float:
        """
        Get the overall tone score for the content.

Returns:
            Tone score between 0 and 1
        """
        if self.results is None:
            self.analyze()

# Calculate tone score
        tone_score = 0.0

# Score based on tone consistency
        if self.results["tone_analysis"]["is_consistent"]:
            tone_score += 0.4
        else:
            # Calculate partial score based on how close to consistent
            consistency = self.results["tone_analysis"]["consistency"]
            min_consistency = self.config["min_tone_consistency"]
            tone_score += (
                0.4 * (consistency / min_consistency) if min_consistency > 0 else 0
            )

# Score based on sentiment consistency
        if self.results["sentiment_analysis"]["is_consistent"]:
            tone_score += 0.3
        else:
            # Calculate partial score based on how close to consistent
            consistency = self.results["sentiment_analysis"]["consistency"]
            min_consistency = self.config["min_sentiment_consistency"]
            tone_score += (
                0.3 * (consistency / min_consistency) if min_consistency > 0 else 0
            )

# Score based on style
        style_score = 0.0

if self.results["style_analysis"]["sentence_length_variety"]["is_optimal"]:
            style_score += 0.33

if self.results["style_analysis"]["vocabulary_variety"]["is_optimal"]:
            style_score += 0.33

if self.results["style_analysis"]["punctuation"]["is_optimal"]:
            style_score += 0.34

tone_score += 0.3 * style_score

            return tone_score

def get_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get tone recommendations for the content.

Returns:
            List of recommendation dictionaries
        """
        if self.results is None:
            self.analyze()

recommendations = []

# Check tone consistency
        if not self.results["tone_analysis"]["is_consistent"]:
            target_tone = self.config["target_tone"]
            dominant_tone = self.results["tone_analysis"]["dominant_tone"]

if dominant_tone != target_tone:
                recommendations.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "tone_consistency",
                        "severity": "high",
                        "message": f"Content tone is predominantly {dominant_tone}, but the target tone is {target_tone}.",
                        "suggestion": f"Adjust the content to use more {target_tone} language and less {dominant_tone} language.",
                    }
                )

# Check sentiment consistency
        if not self.results["sentiment_analysis"]["is_consistent"]:
            target_sentiment = self.config["target_sentiment"]
            dominant_sentiment = self.results["sentiment_analysis"][
                "dominant_sentiment"
            ]

if dominant_sentiment != target_sentiment:
                recommendations.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "sentiment_consistency",
                        "severity": "medium",
                        "message": f"Content sentiment is predominantly {dominant_sentiment}, but the target sentiment is {target_sentiment}.",
                        "suggestion": f"Adjust the content to use more {target_sentiment} language and less {dominant_sentiment} language.",
                    }
                )

# Check sentence length variety
        if not self.results["style_analysis"]["sentence_length_variety"]["is_optimal"]:
            recommendations.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "sentence_variety",
                    "severity": "medium",
                    "message": "Sentence length variety is low, which can make the content monotonous.",
                    "suggestion": "Mix short, medium, and long sentences to improve flow and engagement.",
                }
            )

# Check vocabulary variety
        if not self.results["style_analysis"]["vocabulary_variety"]["is_optimal"]:
            recommendations.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "vocabulary_variety",
                    "severity": "medium",
                    "message": "Vocabulary variety is low, which can make the content repetitive.",
                    "suggestion": "Use a wider range of words and avoid repeating the same terms frequently.",
                }
            )

# Check punctuation
        punctuation = self.results["style_analysis"]["punctuation"]

if not punctuation["is_optimal"]:
            if punctuation["density"] < 0.05:
                recommendations.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "punctuation",
                        "severity": "low",
                        "message": "Punctuation usage is low, which can make the content hard to read.",
                        "suggestion": "Add more punctuation to break up long sentences and improve readability.",
                    }
                
            elif punctuation["density"] > 0.1:
                recommendations.append(
                    {
                        "id": str(uuid.uuid4(,
                        "type": "punctuation",
                        "severity": "low",
                        "message": "Punctuation usage is high, which can make the content choppy.",
                        "suggestion": "Reduce excessive punctuation and combine some shorter sentences.",
                    }
                

            return recommendations