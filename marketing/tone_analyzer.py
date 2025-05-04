"""
"""
Tone analyzer module for the pAIssive Income project.
Tone analyzer module for the pAIssive Income project.


This module provides classes for analyzing and adjusting the tone of content.
This module provides classes for analyzing and adjusting the tone of content.
"""
"""


import datetime
import datetime
import json
import json
import math
import math
import re
import re
import string
import string
import time
import time
import uuid
import uuid
from abc import ABC, abstractmethod
from abc import ABC, abstractmethod
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from typing import Any, Dict, List, Optional, Tuple


import nltk
import nltk
from nltk.corpus import stopwords
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tokenize import sent_tokenize, word_tokenize


NLTK_AVAILABLE
NLTK_AVAILABLE


# Third-party imports
# Third-party imports
try:
    try:


    = True
    = True
except ImportError:
except ImportError:
    NLTK_AVAILABLE = False
    NLTK_AVAILABLE = False


    # We'll define our own base class to avoid circular imports
    # We'll define our own base class to avoid circular imports
    # This is similar to SEOAnalyzer from content_optimization.py but independent
    # This is similar to SEOAnalyzer from content_optimization.py but independent




    class ContentAnalyzer(ABC):
    class ContentAnalyzer(ABC):
    """
    """
    Abstract base class for content analyzers.
    Abstract base class for content analyzers.


    This class provides common functionality for all content analyzers,
    This class provides common functionality for all content analyzers,
    including configuration, analysis, and reporting.
    including configuration, analysis, and reporting.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    content: Optional[Dict[str, Any]] = None,
    content: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize a content analyzer.
    Initialize a content analyzer.


    Args:
    Args:
    content: Optional content to analyze
    content: Optional content to analyze
    config: Optional configuration dictionary
    config: Optional configuration dictionary
    """
    """
    self.id = str(uuid.uuid4())
    self.id = str(uuid.uuid4())
    self.content = content
    self.content = content
    self.config = config or self.get_default_config()
    self.config = config or self.get_default_config()
    self.created_at = datetime.datetime.now().isoformat()
    self.created_at = datetime.datetime.now().isoformat()
    self.results = None
    self.results = None


    @abstractmethod
    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
    def analyze(self) -> Dict[str, Any]:
    """
    """
    Analyze the content.
    Analyze the content.


    Returns:
    Returns:
    Dictionary with analysis results
    Dictionary with analysis results
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def get_score(self) -> float:
    def get_score(self) -> float:
    """
    """
    Get the overall score for the content.
    Get the overall score for the content.


    Returns:
    Returns:
    Score between 0 and 1
    Score between 0 and 1
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def get_recommendations(self) -> List[Dict[str, Any]]:
    def get_recommendations(self) -> List[Dict[str, Any]]:
    """
    """
    Get recommendations for the content.
    Get recommendations for the content.


    Returns:
    Returns:
    List of recommendation dictionaries
    List of recommendation dictionaries
    """
    """
    pass
    pass


    def get_default_config(self) -> Dict[str, Any]:
    def get_default_config(self) -> Dict[str, Any]:
    """
    """
    Get the default configuration for the analyzer.
    Get the default configuration for the analyzer.


    Returns:
    Returns:
    Default configuration dictionary
    Default configuration dictionary
    """
    """
    return {"timestamp": datetime.datetime.now().isoformat()}
    return {"timestamp": datetime.datetime.now().isoformat()}


    def validate_config(self) -> Tuple[bool, List[str]]:
    def validate_config(self) -> Tuple[bool, List[str]]:
    """
    """
    Validate the configuration dictionary.
    Validate the configuration dictionary.


    Returns:
    Returns:
    Tuple of (is_valid, error_messages)
    Tuple of (is_valid, error_messages)
    """
    """
    return True, []
    return True, []


    def set_content(self, content: Dict[str, Any]) -> None:
    def set_content(self, content: Dict[str, Any]) -> None:
    """
    """
    Set the content to analyze.
    Set the content to analyze.


    Args:
    Args:
    content: Content dictionary
    content: Content dictionary
    """
    """
    self.content = content
    self.content = content
    self.results = None  # Reset results
    self.results = None  # Reset results


    def set_config(self, config: Dict[str, Any]) -> None:
    def set_config(self, config: Dict[str, Any]) -> None:
    """
    """
    Set the configuration dictionary.
    Set the configuration dictionary.


    Args:
    Args:
    config: Configuration dictionary
    config: Configuration dictionary
    """
    """
    self.config = config
    self.config = config
    self.results = None  # Reset results
    self.results = None  # Reset results


    def update_config(self, key: str, value: Any) -> None:
    def update_config(self, key: str, value: Any) -> None:
    """
    """
    Update a specific configuration value.
    Update a specific configuration value.


    Args:
    Args:
    key: Configuration key
    key: Configuration key
    value: Configuration value
    value: Configuration value
    """
    """
    self.config[key] = value
    self.config[key] = value
    self.results = None  # Reset results
    self.results = None  # Reset results


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the analyzer to a dictionary.
    Convert the analyzer to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the analyzer
    Dictionary representation of the analyzer
    """
    """
    return {
    return {
    "id": self.id,
    "id": self.id,
    "config": self.config,
    "config": self.config,
    "created_at": self.created_at,
    "created_at": self.created_at,
    "results": self.results,
    "results": self.results,
    }
    }


    def to_json(self, indent: int = 2) -> str:
    def to_json(self, indent: int = 2) -> str:
    """
    """
    Convert the analyzer to a JSON string.
    Convert the analyzer to a JSON string.


    Args:
    Args:
    indent: Number of spaces for indentation
    indent: Number of spaces for indentation


    Returns:
    Returns:
    JSON string representation of the analyzer
    JSON string representation of the analyzer
    """
    """
    return json.dumps(self.to_dict(), indent=indent)
    return json.dumps(self.to_dict(), indent=indent)




    class ToneAnalyzer(ContentAnalyzer):
    class ToneAnalyzer(ContentAnalyzer):
    """
    """
    Class for analyzing and adjusting the tone of content.
    Class for analyzing and adjusting the tone of content.


    This class provides methods for analyzing tone, sentiment, and style
    This class provides methods for analyzing tone, sentiment, and style
    in content, and making recommendations for adjustments.
    in content, and making recommendations for adjustments.
    """
    """


    # Define tone categories
    # Define tone categories
    TONE_CATEGORIES = {
    TONE_CATEGORIES = {
    "formal": {
    "formal": {
    "description": "Professional, academic, or business-like tone",
    "description": "Professional, academic, or business-like tone",
    "patterns": [
    "patterns": [
    r"\b(?:therefore|consequently|furthermore|thus|hence|accordingly)\b",
    r"\b(?:therefore|consequently|furthermore|thus|hence|accordingly)\b",
    r"\b(?:utilize|implement|facilitate|demonstrate|indicate|necessitate)\b",
    r"\b(?:utilize|implement|facilitate|demonstrate|indicate|necessitate)\b",
    r"\b(?:in conclusion|in summary|to summarize|in essence)\b",
    r"\b(?:in conclusion|in summary|to summarize|in essence)\b",
    r"\b(?:it is|there are|this is|these are)\b",
    r"\b(?:it is|there are|this is|these are)\b",
    r"\b(?:one|we|our|us)\b",
    r"\b(?:one|we|our|us)\b",
    ],
    ],
    "anti_patterns": [
    "anti_patterns": [
    r"\b(?:awesome|cool|wow|yeah|hey|ok|okay)\b",
    r"\b(?:awesome|cool|wow|yeah|hey|ok|okay)\b",
    r"\b(?:gonna|wanna|gotta|kinda|sorta)\b",
    r"\b(?:gonna|wanna|gotta|kinda|sorta)\b",
    r"(?:!{2,}|\?{2,})",
    r"(?:!{2,}|\?{2,})",
    r"\b(?:lol|omg|btw|imo|tbh)\b",
    r"\b(?:lol|omg|btw|imo|tbh)\b",
    r"(?:\:D|\:P|\;\)|\:\))",
    r"(?:\:D|\:P|\;\)|\:\))",
    ],
    ],
    },
    },
    "conversational": {
    "conversational": {
    "description": "Friendly, casual, or personal tone",
    "description": "Friendly, casual, or personal tone",
    "patterns": [
    "patterns": [
    r"\b(?:you|your|you'll|you're|you've|you'd)\b",
    r"\b(?:you|your|you'll|you're|you've|you'd)\b",
    r"\b(?:I|me|my|mine|we|us|our|ours)\b",
    r"\b(?:I|me|my|mine|we|us|our|ours)\b",
    r"\b(?:let's|let me|here's|there's|that's)\b",
    r"\b(?:let's|let me|here's|there's|that's)\b",
    r"\b(?:actually|basically|literally|honestly|seriously)\b",
    r"\b(?:actually|basically|literally|honestly|seriously)\b",
    r"\b(?:great|awesome|amazing|fantastic|wonderful)\b",
    r"\b(?:great|awesome|amazing|fantastic|wonderful)\b",
    ],
    ],
    "anti_patterns": [
    "anti_patterns": [
    r"\b(?:hereby|therein|aforementioned|heretofore)\b",
    r"\b(?:hereby|therein|aforementioned|heretofore)\b",
    r"\b(?:pursuant|notwithstanding|henceforth)\b",
    r"\b(?:pursuant|notwithstanding|henceforth)\b",
    r"\b(?:it is necessary to|it is important to|it is essential to)\b",
    r"\b(?:it is necessary to|it is important to|it is essential to)\b",
    r"\b(?:the author|the researcher|the study)\b",
    r"\b(?:the author|the researcher|the study)\b",
    r"\b(?:shall|must|ought)\b",
    r"\b(?:shall|must|ought)\b",
    ],
    ],
    },
    },
    "persuasive": {
    "persuasive": {
    "description": "Convincing, compelling, or sales-oriented tone",
    "description": "Convincing, compelling, or sales-oriented tone",
    "patterns": [
    "patterns": [
    r"\b(?:you need|you want|you deserve|you can't afford to miss|you should)\b",
    r"\b(?:you need|you want|you deserve|you can't afford to miss|you should)\b",
    r"\b(?:limited time|exclusive|special offer|bonus|free)\b",
    r"\b(?:limited time|exclusive|special offer|bonus|free)\b",
    r"\b(?:guarantee|proven|results|success|transform)\b",
    r"\b(?:guarantee|proven|results|success|transform)\b",
    r"\b(?:imagine|picture|consider|what if|how would)\b",
    r"\b(?:imagine|picture|consider|what if|how would)\b",
    r"\b(?:but wait|act now|don't miss|hurry|today)\b",
    r"\b(?:but wait|act now|don't miss|hurry|today)\b",
    ],
    ],
    "anti_patterns": [
    "anti_patterns": [
    r"\b(?:perhaps|maybe|possibly|might|could be)\b",
    r"\b(?:perhaps|maybe|possibly|might|could be)\b",
    r"\b(?:somewhat|relatively|comparatively|moderately)\b",
    r"\b(?:somewhat|relatively|comparatively|moderately)\b",
    r"\b(?:it seems|it appears|it may be|it could be)\b",
    r"\b(?:it seems|it appears|it may be|it could be)\b",
    r"\b(?:in my opinion|I think|I believe|I feel)\b",
    r"\b(?:in my opinion|I think|I believe|I feel)\b",
    r"\b(?:unclear|uncertain|unknown|undetermined)\b",
    r"\b(?:unclear|uncertain|unknown|undetermined)\b",
    ],
    ],
    },
    },
    "informative": {
    "informative": {
    "description": "Educational, explanatory, or factual tone",
    "description": "Educational, explanatory, or factual tone",
    "patterns": [
    "patterns": [
    r"\b(?:according to|research shows|studies indicate|data suggests|experts say)\b",
    r"\b(?:according to|research shows|studies indicate|data suggests|experts say)\b",
    r"\b(?:for example|for instance|such as|including|specifically)\b",
    r"\b(?:for example|for instance|such as|including|specifically)\b",
    r"\b(?:defined as|refers to|means|consists of|comprises)\b",
    r"\b(?:defined as|refers to|means|consists of|comprises)\b",
    r"\b(?:first|second|third|finally|lastly|next|then)\b",
    r"\b(?:first|second|third|finally|lastly|next|then)\b",
    r"\b(?:causes|effects|results in|leads to|contributes to)\b",
    r"\b(?:causes|effects|results in|leads to|contributes to)\b",
    ],
    ],
    "anti_patterns": [
    "anti_patterns": [
    r"\b(?:I guess|I suppose|I assume|I reckon)\b",
    r"\b(?:I guess|I suppose|I assume|I reckon)\b",
    r"\b(?:kinda|sorta|pretty much|more or less)\b",
    r"\b(?:kinda|sorta|pretty much|more or less)\b",
    r"\b(?:stuff|things|whatever|anyway|somehow)\b",
    r"\b(?:stuff|things|whatever|anyway|somehow)\b",
    r"\b(?:like|you know|I mean|well|so)\b",
    r"\b(?:like|you know|I mean|well|so)\b",
    r"\b(?:probably|hopefully|maybe|perhaps)\b",
    r"\b(?:probably|hopefully|maybe|perhaps)\b",
    ],
    ],
    },
    },
    "inspirational": {
    "inspirational": {
    "description": "Motivational, uplifting, or encouraging tone",
    "description": "Motivational, uplifting, or encouraging tone",
    "patterns": [
    "patterns": [
    r"\b(?:achieve|accomplish|overcome|succeed|excel)\b",
    r"\b(?:achieve|accomplish|overcome|succeed|excel)\b",
    r"\b(?:dream|passion|purpose|mission|vision)\b",
    r"\b(?:dream|passion|purpose|mission|vision)\b",
    r"\b(?:potential|possibility|opportunity|chance|prospect)\b",
    r"\b(?:potential|possibility|opportunity|chance|prospect)\b",
    r"\b(?:believe|trust|faith|hope|courage)\b",
    r"\b(?:believe|trust|faith|hope|courage)\b",
    r"\b(?:inspire|motivate|encourage|empower|uplift)\b",
    r"\b(?:inspire|motivate|encourage|empower|uplift)\b",
    ],
    ],
    "anti_patterns": [
    "anti_patterns": [
    r"\b(?:impossible|hopeless|pointless|useless|worthless)\b",
    r"\b(?:impossible|hopeless|pointless|useless|worthless)\b",
    r"\b(?:fail|failure|defeat|lose|loss)\b",
    r"\b(?:fail|failure|defeat|lose|loss)\b",
    r"\b(?:problem|issue|trouble|difficulty|obstacle)\b",
    r"\b(?:problem|issue|trouble|difficulty|obstacle)\b",
    r"\b(?:hard|difficult|challenging|tough|demanding)\b",
    r"\b(?:hard|difficult|challenging|tough|demanding)\b",
    r"\b(?:unfortunately|sadly|regrettably|disappointingly)\b",
    r"\b(?:unfortunately|sadly|regrettably|disappointingly)\b",
    ],
    ],
    },
    },
    "humorous": {
    "humorous": {
    "description": "Funny, witty, or entertaining tone",
    "description": "Funny, witty, or entertaining tone",
    "patterns": [
    "patterns": [
    r"\b(?:funny|hilarious|amusing|entertaining|comical)\b",
    r"\b(?:funny|hilarious|amusing|entertaining|comical)\b",
    r"\b(?:joke|laugh|humor|wit|pun)\b",
    r"\b(?:joke|laugh|humor|wit|pun)\b",
    r"\b(?:ridiculous|absurd|silly|crazy|wild)\b",
    r"\b(?:ridiculous|absurd|silly|crazy|wild)\b",
    r"(?:!{2,}|\?{2,}|…)",
    r"(?:!{2,}|\?{2,}|…)",
    r"(?:\:D|\:P|\;\)|\:\))",
    r"(?:\:D|\:P|\;\)|\:\))",
    ],
    ],
    "anti_patterns": [
    "anti_patterns": [
    r"\b(?:serious|solemn|grave|somber|formal)\b",
    r"\b(?:serious|solemn|grave|somber|formal)\b",
    r"\b(?:tragic|sad|unfortunate|regrettable|lamentable)\b",
    r"\b(?:tragic|sad|unfortunate|regrettable|lamentable)\b",
    r"\b(?:professional|business|corporate|official)\b",
    r"\b(?:professional|business|corporate|official)\b",
    r"\b(?:analysis|research|study|investigation|examination)\b",
    r"\b(?:analysis|research|study|investigation|examination)\b",
    r"\b(?:pursuant|henceforth|therefore|thus|hence)\b",
    r"\b(?:pursuant|henceforth|therefore|thus|hence)\b",
    ],
    ],
    },
    },
    }
    }


    # Define sentiment categories
    # Define sentiment categories
    SENTIMENT_CATEGORIES = {
    SENTIMENT_CATEGORIES = {
    "positive": [
    "positive": [
    "good",
    "good",
    "great",
    "great",
    "excellent",
    "excellent",
    "amazing",
    "amazing",
    "wonderful",
    "wonderful",
    "fantastic",
    "fantastic",
    "terrific",
    "terrific",
    "outstanding",
    "outstanding",
    "superb",
    "superb",
    "brilliant",
    "brilliant",
    "exceptional",
    "exceptional",
    "marvelous",
    "marvelous",
    "fabulous",
    "fabulous",
    "splendid",
    "splendid",
    "delightful",
    "delightful",
    "happy",
    "happy",
    "glad",
    "glad",
    "pleased",
    "pleased",
    "satisfied",
    "satisfied",
    "content",
    "content",
    "joyful",
    "joyful",
    "cheerful",
    "cheerful",
    "thrilled",
    "thrilled",
    "excited",
    "excited",
    "enthusiastic",
    "enthusiastic",
    "passionate",
    "passionate",
    "eager",
    "eager",
    "motivated",
    "motivated",
    "inspired",
    "inspired",
    "encouraged",
    "encouraged",
    "love",
    "love",
    "like",
    "like",
    "enjoy",
    "enjoy",
    "appreciate",
    "appreciate",
    "admire",
    "admire",
    "respect",
    "respect",
    "value",
    "value",
    "cherish",
    "cherish",
    "benefit",
    "benefit",
    "advantage",
    "advantage",
    "gain",
    "gain",
    "profit",
    "profit",
    "reward",
    "reward",
    "success",
    "success",
    "achievement",
    "achievement",
    "accomplishment",
    "accomplishment",
    "improve",
    "improve",
    "enhance",
    "enhance",
    "boost",
    "boost",
    "increase",
    "increase",
    "grow",
    "grow",
    "develop",
    "develop",
    "progress",
    "progress",
    "advance",
    "advance",
    ],
    ],
    "negative": [
    "negative": [
    "bad",
    "bad",
    "poor",
    "poor",
    "terrible",
    "terrible",
    "horrible",
    "horrible",
    "awful",
    "awful",
    "dreadful",
    "dreadful",
    "abysmal",
    "abysmal",
    "atrocious",
    "atrocious",
    "subpar",
    "subpar",
    "inferior",
    "inferior",
    "mediocre",
    "mediocre",
    "disappointing",
    "disappointing",
    "unsatisfactory",
    "unsatisfactory",
    "inadequate",
    "inadequate",
    "insufficient",
    "insufficient",
    "sad",
    "sad",
    "unhappy",
    "unhappy",
    "upset",
    "upset",
    "disappointed",
    "disappointed",
    "frustrated",
    "frustrated",
    "annoyed",
    "annoyed",
    "angry",
    "angry",
    "irritated",
    "irritated",
    "worried",
    "worried",
    "concerned",
    "concerned",
    "anxious",
    "anxious",
    "nervous",
    "nervous",
    "stressed",
    "stressed",
    "overwhelmed",
    "overwhelmed",
    "exhausted",
    "exhausted",
    "hate",
    "hate",
    "dislike",
    "dislike",
    "despise",
    "despise",
    "detest",
    "detest",
    "loathe",
    "loathe",
    "resent",
    "resent",
    "reject",
    "reject",
    "avoid",
    "avoid",
    "problem",
    "problem",
    "issue",
    "issue",
    "challenge",
    "challenge",
    "difficulty",
    "difficulty",
    "obstacle",
    "obstacle",
    "barrier",
    "barrier",
    "hurdle",
    "hurdle",
    "setback",
    "setback",
    "fail",
    "fail",
    "failure",
    "failure",
    "loss",
    "loss",
    "defeat",
    "defeat",
    "decline",
    "decline",
    "decrease",
    "decrease",
    "reduce",
    "reduce",
    "diminish",
    "diminish",
    ],
    ],
    "neutral": [
    "neutral": [
    "okay",
    "okay",
    "fine",
    "fine",
    "average",
    "average",
    "moderate",
    "moderate",
    "fair",
    "fair",
    "reasonable",
    "reasonable",
    "acceptable",
    "acceptable",
    "adequate",
    "adequate",
    "normal",
    "normal",
    "standard",
    "standard",
    "typical",
    "typical",
    "common",
    "common",
    "usual",
    "usual",
    "regular",
    "regular",
    "ordinary",
    "ordinary",
    "conventional",
    "conventional",
    "think",
    "think",
    "believe",
    "believe",
    "consider",
    "consider",
    "regard",
    "regard",
    "view",
    "view",
    "perceive",
    "perceive",
    "understand",
    "understand",
    "comprehend",
    "comprehend",
    "seem",
    "seem",
    "appear",
    "appear",
    "look",
    "look",
    "sound",
    "sound",
    "feel",
    "feel",
    "sense",
    "sense",
    "experience",
    "experience",
    "observe",
    "observe",
    "perhaps",
    "perhaps",
    "maybe",
    "maybe",
    "possibly",
    "possibly",
    "potentially",
    "potentially",
    "conceivably",
    "conceivably",
    "presumably",
    "presumably",
    "supposedly",
    "supposedly",
    "apparently",
    "apparently",
    "sometimes",
    "sometimes",
    "occasionally",
    "occasionally",
    "periodically",
    "periodically",
    "intermittently",
    "intermittently",
    "sporadically",
    "sporadically",
    "infrequently",
    "infrequently",
    "rarely",
    "rarely",
    "seldom",
    "seldom",
    ],
    ],
    }
    }


    def __init__(
    def __init__(
    self,
    self,
    content: Optional[Dict[str, Any]] = None,
    content: Optional[Dict[str, Any]] = None,
    target_tone: Optional[str] = None,
    target_tone: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize a tone analyzer.
    Initialize a tone analyzer.


    Args:
    Args:
    content: Optional content to analyze
    content: Optional content to analyze
    target_tone: Optional target tone for the content
    target_tone: Optional target tone for the content
    config: Optional configuration dictionary
    config: Optional configuration dictionary
    """
    """
    super().__init__(content, config)
    super().__init__(content, config)


    # Set target tone
    # Set target tone
    self.target_tone = target_tone
    self.target_tone = target_tone


    # Initialize NLTK if available
    # Initialize NLTK if available
    if NLTK_AVAILABLE:
    if NLTK_AVAILABLE:
    try:
    try:
    nltk.data.find("tokenizers/punkt")
    nltk.data.find("tokenizers/punkt")
except LookupError:
except LookupError:
    nltk.download("punkt")
    nltk.download("punkt")


    def get_default_config(self) -> Dict[str, Any]:
    def get_default_config(self) -> Dict[str, Any]:
    """
    """
    Get the default configuration for the tone analyzer.
    Get the default configuration for the tone analyzer.


    Returns:
    Returns:
    Default configuration dictionary
    Default configuration dictionary
    """
    """
    # Start with base config
    # Start with base config
    config = super().get_default_config()
    config = super().get_default_config()


    # Add tone-specific config
    # Add tone-specific config
    config.update(
    config.update(
    {
    {
    "min_tone_consistency": 0.7,  # Minimum consistency score for the target tone
    "min_tone_consistency": 0.7,  # Minimum consistency score for the target tone
    "min_sentiment_consistency": 0.6,  # Minimum consistency score for the target sentiment
    "min_sentiment_consistency": 0.6,  # Minimum consistency score for the target sentiment
    "tone_pattern_weight": 0.6,  # Weight for tone pattern matching
    "tone_pattern_weight": 0.6,  # Weight for tone pattern matching
    "tone_anti_pattern_weight": 0.4,  # Weight for tone anti-pattern matching
    "tone_anti_pattern_weight": 0.4,  # Weight for tone anti-pattern matching
    "sentiment_weight": 0.3,  # Weight for sentiment analysis
    "sentiment_weight": 0.3,  # Weight for sentiment analysis
    "check_tone_consistency": True,  # Whether to check tone consistency
    "check_tone_consistency": True,  # Whether to check tone consistency
    "check_sentiment_consistency": True,  # Whether to check sentiment consistency
    "check_sentiment_consistency": True,  # Whether to check sentiment consistency
    "check_style_consistency": True,  # Whether to check style consistency
    "check_style_consistency": True,  # Whether to check style consistency
    "target_tone": self.target_tone
    "target_tone": self.target_tone
    or "conversational",  # Default target tone
    or "conversational",  # Default target tone
    "target_sentiment": "positive",  # Default target sentiment
    "target_sentiment": "positive",  # Default target sentiment
    "timestamp": datetime.datetime.now().isoformat(),
    "timestamp": datetime.datetime.now().isoformat(),
    }
    }
    )
    )


    return config
    return config


    def set_target_tone(self, target_tone: str) -> None:
    def set_target_tone(self, target_tone: str) -> None:
    """
    """
    Set the target tone for the content.
    Set the target tone for the content.


    Args:
    Args:
    target_tone: Target tone
    target_tone: Target tone
    """
    """
    if target_tone not in self.TONE_CATEGORIES:
    if target_tone not in self.TONE_CATEGORIES:
    raise ValueError(
    raise ValueError(
    f"Invalid target tone: {target_tone}. Must be one of: {', '.join(self.TONE_CATEGORIES.keys())}"
    f"Invalid target tone: {target_tone}. Must be one of: {', '.join(self.TONE_CATEGORIES.keys())}"
    )
    )


    self.target_tone = target_tone
    self.target_tone = target_tone
    self.config["target_tone"] = target_tone
    self.config["target_tone"] = target_tone
    self.results = None  # Reset results
    self.results = None  # Reset results


    def validate_content(self) -> Tuple[bool, List[str]]:
    def validate_content(self) -> Tuple[bool, List[str]]:
    """
    """
    Validate the content for tone analysis.
    Validate the content for tone analysis.


    Returns:
    Returns:
    Tuple of (is_valid, error_messages)
    Tuple of (is_valid, error_messages)
    """
    """
    if self.content is None:
    if self.content is None:
    return False, ["No content provided"]
    return False, ["No content provided"]


    errors = []
    errors = []


    # Check if there's text to analyze
    # Check if there's text to analyze
    text = self._extract_text_from_content()
    text = self._extract_text_from_content()
    if not text:
    if not text:
    errors.append("No text found in content")
    errors.append("No text found in content")


    # Check if target tone is valid
    # Check if target tone is valid
    if self.target_tone and self.target_tone not in self.TONE_CATEGORIES:
    if self.target_tone and self.target_tone not in self.TONE_CATEGORIES:
    errors.append(
    errors.append(
    f"Invalid target tone: {self.target_tone}. Must be one of: {', '.join(self.TONE_CATEGORIES.keys())}"
    f"Invalid target tone: {self.target_tone}. Must be one of: {', '.join(self.TONE_CATEGORIES.keys())}"
    )
    )


    return len(errors) == 0, errors
    return len(errors) == 0, errors


    def analyze(self) -> Dict[str, Any]:
    def analyze(self) -> Dict[str, Any]:
    """
    """
    Analyze the content for tone and sentiment.
    Analyze the content for tone and sentiment.


    Returns:
    Returns:
    Dictionary with analysis results
    Dictionary with analysis results
    """
    """
    # Validate content
    # Validate content
    is_valid, errors = self.validate_content()
    is_valid, errors = self.validate_content()


    if not is_valid:
    if not is_valid:
    raise ValueError(f"Invalid content: {', '.join(errors)}")
    raise ValueError(f"Invalid content: {', '.join(errors)}")


    # Extract text
    # Extract text
    text = self._extract_text_from_content()
    text = self._extract_text_from_content()


    # Initialize results
    # Initialize results
    self.results = {
    self.results = {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "timestamp": datetime.datetime.now().isoformat(),
    "timestamp": datetime.datetime.now().isoformat(),
    "content_id": self.content.get("id", "unknown"),
    "content_id": self.content.get("id", "unknown"),
    "target_tone": self.config["target_tone"],
    "target_tone": self.config["target_tone"],
    "target_sentiment": self.config["target_sentiment"],
    "target_sentiment": self.config["target_sentiment"],
    "tone_analysis": {},
    "tone_analysis": {},
    "sentiment_analysis": {},
    "sentiment_analysis": {},
    "style_analysis": {},
    "style_analysis": {},
    "overall_score": 0.0,
    "overall_score": 0.0,
    "recommendations": [],
    "recommendations": [],
    }
    }


    # Analyze tone
    # Analyze tone
    self.results["tone_analysis"] = self._analyze_tone(text)
    self.results["tone_analysis"] = self._analyze_tone(text)


    # Analyze sentiment
    # Analyze sentiment
    self.results["sentiment_analysis"] = self._analyze_sentiment(text)
    self.results["sentiment_analysis"] = self._analyze_sentiment(text)


    # Analyze style
    # Analyze style
    self.results["style_analysis"] = self._analyze_style(text)
    self.results["style_analysis"] = self._analyze_style(text)


    # Calculate overall score
    # Calculate overall score
    self.results["overall_score"] = self.get_score()
    self.results["overall_score"] = self.get_score()


    # Generate recommendations
    # Generate recommendations
    self.results["recommendations"] = self.get_recommendations()
    self.results["recommendations"] = self.get_recommendations()


    return self.results
    return self.results


    def _analyze_tone(self, text: str) -> Dict[str, Any]:
    def _analyze_tone(self, text: str) -> Dict[str, Any]:
    """
    """
    Analyze the tone of the text.
    Analyze the tone of the text.


    Args:
    Args:
    text: Text to analyze
    text: Text to analyze


    Returns:
    Returns:
    Dictionary with tone analysis results
    Dictionary with tone analysis results
    """
    """
    # Get sentences
    # Get sentences
    sentences = self._get_sentences(text)
    sentences = self._get_sentences(text)


    # Initialize tone scores
    # Initialize tone scores
    tone_scores = {}
    tone_scores = {}


    # Analyze each tone category
    # Analyze each tone category
    for tone, tone_data in self.TONE_CATEGORIES.items():
    for tone, tone_data in self.TONE_CATEGORIES.items():
    # Count pattern matches
    # Count pattern matches
    pattern_matches = 0
    pattern_matches = 0


    for pattern in tone_data["patterns"]:
    for pattern in tone_data["patterns"]:
    pattern_matches += len(re.findall(pattern, text, re.IGNORECASE))
    pattern_matches += len(re.findall(pattern, text, re.IGNORECASE))


    # Count anti-pattern matches
    # Count anti-pattern matches
    anti_pattern_matches = 0
    anti_pattern_matches = 0


    for pattern in tone_data["anti_patterns"]:
    for pattern in tone_data["anti_patterns"]:
    anti_pattern_matches += len(re.findall(pattern, text, re.IGNORECASE))
    anti_pattern_matches += len(re.findall(pattern, text, re.IGNORECASE))


    # Calculate tone score
    # Calculate tone score
    pattern_weight = self.config["tone_pattern_weight"]
    pattern_weight = self.config["tone_pattern_weight"]
    anti_pattern_weight = self.config["tone_anti_pattern_weight"]
    anti_pattern_weight = self.config["tone_anti_pattern_weight"]


    # Normalize by number of sentences
    # Normalize by number of sentences
    pattern_score = pattern_matches / len(sentences) if sentences else 0
    pattern_score = pattern_matches / len(sentences) if sentences else 0
    anti_pattern_score = (
    anti_pattern_score = (
    anti_pattern_matches / len(sentences) if sentences else 0
    anti_pattern_matches / len(sentences) if sentences else 0
    )
    )


    # Calculate weighted score
    # Calculate weighted score
    tone_score = (pattern_score * pattern_weight) - (
    tone_score = (pattern_score * pattern_weight) - (
    anti_pattern_score * anti_pattern_weight
    anti_pattern_score * anti_pattern_weight
    )
    )


    # Clamp score to 0-1 range
    # Clamp score to 0-1 range
    tone_score = max(0, min(1, tone_score))
    tone_score = max(0, min(1, tone_score))


    # Store tone score
    # Store tone score
    tone_scores[tone] = {
    tone_scores[tone] = {
    "score": tone_score,
    "score": tone_score,
    "pattern_matches": pattern_matches,
    "pattern_matches": pattern_matches,
    "anti_pattern_matches": anti_pattern_matches,
    "anti_pattern_matches": anti_pattern_matches,
    "is_target": tone == self.config["target_tone"],
    "is_target": tone == self.config["target_tone"],
    }
    }


    # Determine dominant tone
    # Determine dominant tone
    dominant_tone = max(tone_scores.items(), key=lambda x: x[1]["score"])
    dominant_tone = max(tone_scores.items(), key=lambda x: x[1]["score"])


    # Calculate consistency with target tone
    # Calculate consistency with target tone
    target_tone = self.config["target_tone"]
    target_tone = self.config["target_tone"]
    target_score = tone_scores[target_tone]["score"]
    target_score = tone_scores[target_tone]["score"]
    consistency = (
    consistency = (
    target_score / dominant_tone[1]["score"]
    target_score / dominant_tone[1]["score"]
    if dominant_tone[1]["score"] > 0
    if dominant_tone[1]["score"] > 0
    else 0
    else 0
    )
    )


    return {
    return {
    "tone_scores": tone_scores,
    "tone_scores": tone_scores,
    "dominant_tone": dominant_tone[0],
    "dominant_tone": dominant_tone[0],
    "dominant_tone_score": dominant_tone[1]["score"],
    "dominant_tone_score": dominant_tone[1]["score"],
    "target_tone": target_tone,
    "target_tone": target_tone,
    "target_tone_score": target_score,
    "target_tone_score": target_score,
    "consistency": consistency,
    "consistency": consistency,
    "is_consistent": consistency >= self.config["min_tone_consistency"],
    "is_consistent": consistency >= self.config["min_tone_consistency"],
    }
    }


    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
    """
    """
    Analyze the sentiment of the text.
    Analyze the sentiment of the text.


    Args:
    Args:
    text: Text to analyze
    text: Text to analyze


    Returns:
    Returns:
    Dictionary with sentiment analysis results
    Dictionary with sentiment analysis results
    """
    """
    # Get words
    # Get words
    words = self._get_words(text)
    words = self._get_words(text)


    # Initialize sentiment counts
    # Initialize sentiment counts
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}


    # Count sentiment words
    # Count sentiment words
    for word in words:
    for word in words:
    word = word.lower()
    word = word.lower()


    if word in self.SENTIMENT_CATEGORIES["positive"]:
    if word in self.SENTIMENT_CATEGORIES["positive"]:
    sentiment_counts["positive"] += 1
    sentiment_counts["positive"] += 1
    elif word in self.SENTIMENT_CATEGORIES["negative"]:
    elif word in self.SENTIMENT_CATEGORIES["negative"]:
    sentiment_counts["negative"] += 1
    sentiment_counts["negative"] += 1
    elif word in self.SENTIMENT_CATEGORIES["neutral"]:
    elif word in self.SENTIMENT_CATEGORIES["neutral"]:
    sentiment_counts["neutral"] += 1
    sentiment_counts["neutral"] += 1


    # Calculate total sentiment words
    # Calculate total sentiment words
    total_sentiment_words = sum(sentiment_counts.values())
    total_sentiment_words = sum(sentiment_counts.values())


    # Calculate sentiment scores
    # Calculate sentiment scores
    sentiment_scores = {}
    sentiment_scores = {}


    for sentiment, count in sentiment_counts.items():
    for sentiment, count in sentiment_counts.items():
    score = count / total_sentiment_words if total_sentiment_words > 0 else 0
    score = count / total_sentiment_words if total_sentiment_words > 0 else 0


    sentiment_scores[sentiment] = {
    sentiment_scores[sentiment] = {
    "count": count,
    "count": count,
    "score": score,
    "score": score,
    "is_target": sentiment == self.config["target_sentiment"],
    "is_target": sentiment == self.config["target_sentiment"],
    }
    }


    # Determine dominant sentiment
    # Determine dominant sentiment
    dominant_sentiment = max(sentiment_scores.items(), key=lambda x: x[1]["score"])
    dominant_sentiment = max(sentiment_scores.items(), key=lambda x: x[1]["score"])


    # Calculate consistency with target sentiment
    # Calculate consistency with target sentiment
    target_sentiment = self.config["target_sentiment"]
    target_sentiment = self.config["target_sentiment"]
    target_score = sentiment_scores[target_sentiment]["score"]
    target_score = sentiment_scores[target_sentiment]["score"]
    consistency = (
    consistency = (
    target_score / dominant_sentiment[1]["score"]
    target_score / dominant_sentiment[1]["score"]
    if dominant_sentiment[1]["score"] > 0
    if dominant_sentiment[1]["score"] > 0
    else 0
    else 0
    )
    )


    return {
    return {
    "sentiment_scores": sentiment_scores,
    "sentiment_scores": sentiment_scores,
    "dominant_sentiment": dominant_sentiment[0],
    "dominant_sentiment": dominant_sentiment[0],
    "dominant_sentiment_score": dominant_sentiment[1]["score"],
    "dominant_sentiment_score": dominant_sentiment[1]["score"],
    "target_sentiment": target_sentiment,
    "target_sentiment": target_sentiment,
    "target_sentiment_score": target_score,
    "target_sentiment_score": target_score,
    "consistency": consistency,
    "consistency": consistency,
    "is_consistent": consistency >= self.config["min_sentiment_consistency"],
    "is_consistent": consistency >= self.config["min_sentiment_consistency"],
    }
    }


    def _extract_text_from_content(self) -> str:
    def _extract_text_from_content(self) -> str:
    """
    """
    Extract text from content for analysis.
    Extract text from content for analysis.


    Returns:
    Returns:
    Extracted text
    Extracted text
    """
    """
    if not self.content:
    if not self.content:
    return ""
    return ""


    text = ""
    text = ""


    # Add title
    # Add title
    if "title" in self.content:
    if "title" in self.content:
    text += self.content["title"] + " "
    text += self.content["title"] + " "


    # Add meta description
    # Add meta description
    if "meta_description" in self.content:
    if "meta_description" in self.content:
    text += self.content["meta_description"] + " "
    text += self.content["meta_description"] + " "


    # Add introduction
    # Add introduction
    if "introduction" in self.content:
    if "introduction" in self.content:
    text += self.content["introduction"] + "\n\n"
    text += self.content["introduction"] + "\n\n"


    # Add sections
    # Add sections
    if "sections" in self.content:
    if "sections" in self.content:
    for section in self.content["sections"]:
    for section in self.content["sections"]:
    if "title" in section:
    if "title" in section:
    text += section["title"] + " "
    text += section["title"] + " "


    if "content" in section:
    if "content" in section:
    text += section["content"] + "\n\n"
    text += section["content"] + "\n\n"


    # Add conclusion
    # Add conclusion
    if "conclusion" in self.content:
    if "conclusion" in self.content:
    text += self.content["conclusion"] + "\n\n"
    text += self.content["conclusion"] + "\n\n"


    # Add overview (for product descriptions)
    # Add overview (for product descriptions)
    if "overview" in self.content:
    if "overview" in self.content:
    text += self.content["overview"] + "\n\n"
    text += self.content["overview"] + "\n\n"


    # Add features (for product descriptions)
    # Add features (for product descriptions)
    if "features" in self.content:
    if "features" in self.content:
    for feature in self.content["features"]:
    for feature in self.content["features"]:
    if "name" in feature:
    if "name" in feature:
    text += feature["name"] + " "
    text += feature["name"] + " "


    if "description" in feature:
    if "description" in feature:
    text += feature["description"] + "\n\n"
    text += feature["description"] + "\n\n"


    # Add benefits (for product descriptions)
    # Add benefits (for product descriptions)
    if "benefits" in self.content:
    if "benefits" in self.content:
    for benefit in self.content["benefits"]:
    for benefit in self.content["benefits"]:
    if "name" in benefit:
    if "name" in benefit:
    text += benefit["name"] + " "
    text += benefit["name"] + " "


    if "description" in benefit:
    if "description" in benefit:
    text += benefit["description"] + "\n\n"
    text += benefit["description"] + "\n\n"


    # Add executive summary (for case studies)
    # Add executive summary (for case studies)
    if "executive_summary" in self.content:
    if "executive_summary" in self.content:
    text += self.content["executive_summary"] + "\n\n"
    text += self.content["executive_summary"] + "\n\n"


    # Add challenge (for case studies)
    # Add challenge (for case studies)
    if "challenge" in self.content:
    if "challenge" in self.content:
    text += self.content["challenge"] + "\n\n"
    text += self.content["challenge"] + "\n\n"


    # Add solution (for case studies)
    # Add solution (for case studies)
    if "solution" in self.content:
    if "solution" in self.content:
    text += self.content["solution"] + "\n\n"
    text += self.content["solution"] + "\n\n"


    # Add implementation (for case studies)
    # Add implementation (for case studies)
    if "implementation" in self.content:
    if "implementation" in self.content:
    text += self.content["implementation"] + "\n\n"
    text += self.content["implementation"] + "\n\n"


    # Add results (for case studies)
    # Add results (for case studies)
    if "results" in self.content:
    if "results" in self.content:
    text += self.content["results"] + "\n\n"
    text += self.content["results"] + "\n\n"


    # Add testimonial (for case studies)
    # Add testimonial (for case studies)
    if "testimonial" in self.content:
    if "testimonial" in self.content:
    text += self.content["testimonial"] + "\n\n"
    text += self.content["testimonial"] + "\n\n"


    return text
    return text


    def _get_sentences(self, text: str) -> List[str]:
    def _get_sentences(self, text: str) -> List[str]:
    """
    """
    Get sentences from text.
    Get sentences from text.


    Args:
    Args:
    text: Text to analyze
    text: Text to analyze


    Returns:
    Returns:
    List of sentences
    List of sentences
    """
    """
    if NLTK_AVAILABLE:
    if NLTK_AVAILABLE:
    # Use NLTK for sentence tokenization
    # Use NLTK for sentence tokenization
    return sent_tokenize(text)
    return sent_tokenize(text)
    else:
    else:
    # Simple sentence tokenization
    # Simple sentence tokenization
    # Split on periods, exclamation points, and question marks
    # Split on periods, exclamation points, and question marks
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = re.split(r"(?<=[.!?])\s+", text)


    # Filter out empty sentences
    # Filter out empty sentences
    return [s.strip() for s in sentences if s.strip()]
    return [s.strip() for s in sentences if s.strip()]


    def _get_words(self, text: str) -> List[str]:
    def _get_words(self, text: str) -> List[str]:
    """
    """
    Get words from text.
    Get words from text.


    Args:
    Args:
    text: Text to analyze
    text: Text to analyze


    Returns:
    Returns:
    List of words
    List of words
    """
    """
    if NLTK_AVAILABLE:
    if NLTK_AVAILABLE:
    # Use NLTK for word tokenization
    # Use NLTK for word tokenization
    tokens = word_tokenize(text.lower())
    tokens = word_tokenize(text.lower())


    # Remove punctuation and stopwords
    # Remove punctuation and stopwords
    stop_words = set(stopwords.words("english"))
    stop_words = set(stopwords.words("english"))
    tokens = [
    tokens = [
    token for token in tokens if token.isalnum() and token not in stop_words
    token for token in tokens if token.isalnum() and token not in stop_words
    ]
    ]
    else:
    else:
    # Simple word tokenization
    # Simple word tokenization
    # Remove punctuation
    # Remove punctuation
    text = re.sub(r"[^\w\s]", "", text.lower())
    text = re.sub(r"[^\w\s]", "", text.lower())


    # Split on whitespace
    # Split on whitespace
    tokens = text.split()
    tokens = text.split()


    return tokens
    return tokens


    def _analyze_style(self, text: str) -> Dict[str, Any]:
    def _analyze_style(self, text: str) -> Dict[str, Any]:
    """
    """
    Analyze the writing style of the text.
    Analyze the writing style of the text.


    Args:
    Args:
    text: Text to analyze
    text: Text to analyze


    Returns:
    Returns:
    Dictionary with style analysis results
    Dictionary with style analysis results
    """
    """
    # Get sentences and words
    # Get sentences and words
    sentences = self._get_sentences(text)
    sentences = self._get_sentences(text)
    words = self._get_words(text)
    words = self._get_words(text)


    # Analyze sentence length variety
    # Analyze sentence length variety
    sentence_lengths = [len(self._get_words(sentence)) for sentence in sentences]
    sentence_lengths = [len(self._get_words(sentence)) for sentence in sentences]


    # Calculate standard deviation of sentence lengths
    # Calculate standard deviation of sentence lengths
    mean_length = (
    mean_length = (
    sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
    sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
    )
    )
    variance = (
    variance = (
    sum((length - mean_length) ** 2 for length in sentence_lengths)
    sum((length - mean_length) ** 2 for length in sentence_lengths)
    / len(sentence_lengths)
    / len(sentence_lengths)
    if sentence_lengths
    if sentence_lengths
    else 0
    else 0
    )
    )
    std_dev = math.sqrt(variance)
    std_dev = math.sqrt(variance)


    # Calculate coefficient of variation (normalized standard deviation)
    # Calculate coefficient of variation (normalized standard deviation)
    cv = std_dev / mean_length if mean_length > 0 else 0
    cv = std_dev / mean_length if mean_length > 0 else 0


    # Analyze vocabulary variety
    # Analyze vocabulary variety
    unique_words = len(set(words))
    unique_words = len(set(words))
    vocabulary_variety = unique_words / len(words) if words else 0
    vocabulary_variety = unique_words / len(words) if words else 0


    # Analyze punctuation
    # Analyze punctuation
    punctuation_count = sum(1 for char in text if char in string.punctuation)
    punctuation_count = sum(1 for char in text if char in string.punctuation)
    punctuation_density = punctuation_count / len(text) if text else 0
    punctuation_density = punctuation_count / len(text) if text else 0


    return {
    return {
    "sentence_length_variety": {"score": cv, "is_optimal": cv >= 0.2},
    "sentence_length_variety": {"score": cv, "is_optimal": cv >= 0.2},
    "vocabulary_variety": {
    "vocabulary_variety": {
    "score": vocabulary_variety,
    "score": vocabulary_variety,
    "unique_words": unique_words,
    "unique_words": unique_words,
    "total_words": len(words),
    "total_words": len(words),
    "is_optimal": vocabulary_variety >= 0.4,
    "is_optimal": vocabulary_variety >= 0.4,
    },
    },
    "punctuation": {
    "punctuation": {
    "count": punctuation_count,
    "count": punctuation_count,
    "density": punctuation_density,
    "density": punctuation_density,
    "is_optimal": 0.05 <= punctuation_density <= 0.1,
    "is_optimal": 0.05 <= punctuation_density <= 0.1,
    },
    },
    }
    }


    def get_score(self) -> float:
    def get_score(self) -> float:
    """
    """
    Get the overall tone score for the content.
    Get the overall tone score for the content.


    Returns:
    Returns:
    Tone score between 0 and 1
    Tone score between 0 and 1
    """
    """
    if self.results is None:
    if self.results is None:
    self.analyze()
    self.analyze()


    # Calculate tone score
    # Calculate tone score
    tone_score = 0.0
    tone_score = 0.0


    # Score based on tone consistency
    # Score based on tone consistency
    if self.results["tone_analysis"]["is_consistent"]:
    if self.results["tone_analysis"]["is_consistent"]:
    tone_score += 0.4
    tone_score += 0.4
    else:
    else:
    # Calculate partial score based on how close to consistent
    # Calculate partial score based on how close to consistent
    consistency = self.results["tone_analysis"]["consistency"]
    consistency = self.results["tone_analysis"]["consistency"]
    min_consistency = self.config["min_tone_consistency"]
    min_consistency = self.config["min_tone_consistency"]
    tone_score += (
    tone_score += (
    0.4 * (consistency / min_consistency) if min_consistency > 0 else 0
    0.4 * (consistency / min_consistency) if min_consistency > 0 else 0
    )
    )


    # Score based on sentiment consistency
    # Score based on sentiment consistency
    if self.results["sentiment_analysis"]["is_consistent"]:
    if self.results["sentiment_analysis"]["is_consistent"]:
    tone_score += 0.3
    tone_score += 0.3
    else:
    else:
    # Calculate partial score based on how close to consistent
    # Calculate partial score based on how close to consistent
    consistency = self.results["sentiment_analysis"]["consistency"]
    consistency = self.results["sentiment_analysis"]["consistency"]
    min_consistency = self.config["min_sentiment_consistency"]
    min_consistency = self.config["min_sentiment_consistency"]
    tone_score += (
    tone_score += (
    0.3 * (consistency / min_consistency) if min_consistency > 0 else 0
    0.3 * (consistency / min_consistency) if min_consistency > 0 else 0
    )
    )


    # Score based on style
    # Score based on style
    style_score = 0.0
    style_score = 0.0


    if self.results["style_analysis"]["sentence_length_variety"]["is_optimal"]:
    if self.results["style_analysis"]["sentence_length_variety"]["is_optimal"]:
    style_score += 0.33
    style_score += 0.33


    if self.results["style_analysis"]["vocabulary_variety"]["is_optimal"]:
    if self.results["style_analysis"]["vocabulary_variety"]["is_optimal"]:
    style_score += 0.33
    style_score += 0.33


    if self.results["style_analysis"]["punctuation"]["is_optimal"]:
    if self.results["style_analysis"]["punctuation"]["is_optimal"]:
    style_score += 0.34
    style_score += 0.34


    tone_score += 0.3 * style_score
    tone_score += 0.3 * style_score


    return tone_score
    return tone_score


    def get_recommendations(self) -> List[Dict[str, Any]]:
    def get_recommendations(self) -> List[Dict[str, Any]]:
    """
    """
    Get tone recommendations for the content.
    Get tone recommendations for the content.


    Returns:
    Returns:
    List of recommendation dictionaries
    List of recommendation dictionaries
    """
    """
    if self.results is None:
    if self.results is None:
    self.analyze()
    self.analyze()


    recommendations = []
    recommendations = []


    # Check tone consistency
    # Check tone consistency
    if not self.results["tone_analysis"]["is_consistent"]:
    if not self.results["tone_analysis"]["is_consistent"]:
    target_tone = self.config["target_tone"]
    target_tone = self.config["target_tone"]
    dominant_tone = self.results["tone_analysis"]["dominant_tone"]
    dominant_tone = self.results["tone_analysis"]["dominant_tone"]


    if dominant_tone != target_tone:
    if dominant_tone != target_tone:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "tone_consistency",
    "type": "tone_consistency",
    "severity": "high",
    "severity": "high",
    "message": f"Content tone is predominantly {dominant_tone}, but the target tone is {target_tone}.",
    "message": f"Content tone is predominantly {dominant_tone}, but the target tone is {target_tone}.",
    "suggestion": f"Adjust the content to use more {target_tone} language and less {dominant_tone} language.",
    "suggestion": f"Adjust the content to use more {target_tone} language and less {dominant_tone} language.",
    }
    }
    )
    )


    # Check sentiment consistency
    # Check sentiment consistency
    if not self.results["sentiment_analysis"]["is_consistent"]:
    if not self.results["sentiment_analysis"]["is_consistent"]:
    target_sentiment = self.config["target_sentiment"]
    target_sentiment = self.config["target_sentiment"]
    dominant_sentiment = self.results["sentiment_analysis"][
    dominant_sentiment = self.results["sentiment_analysis"][
    "dominant_sentiment"
    "dominant_sentiment"
    ]
    ]


    if dominant_sentiment != target_sentiment:
    if dominant_sentiment != target_sentiment:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "sentiment_consistency",
    "type": "sentiment_consistency",
    "severity": "medium",
    "severity": "medium",
    "message": f"Content sentiment is predominantly {dominant_sentiment}, but the target sentiment is {target_sentiment}.",
    "message": f"Content sentiment is predominantly {dominant_sentiment}, but the target sentiment is {target_sentiment}.",
    "suggestion": f"Adjust the content to use more {target_sentiment} language and less {dominant_sentiment} language.",
    "suggestion": f"Adjust the content to use more {target_sentiment} language and less {dominant_sentiment} language.",
    }
    }
    )
    )


    # Check sentence length variety
    # Check sentence length variety
    if not self.results["style_analysis"]["sentence_length_variety"]["is_optimal"]:
    if not self.results["style_analysis"]["sentence_length_variety"]["is_optimal"]:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "sentence_variety",
    "type": "sentence_variety",
    "severity": "medium",
    "severity": "medium",
    "message": "Sentence length variety is low, which can make the content monotonous.",
    "message": "Sentence length variety is low, which can make the content monotonous.",
    "suggestion": "Mix short, medium, and long sentences to improve flow and engagement.",
    "suggestion": "Mix short, medium, and long sentences to improve flow and engagement.",
    }
    }
    )
    )


    # Check vocabulary variety
    # Check vocabulary variety
    if not self.results["style_analysis"]["vocabulary_variety"]["is_optimal"]:
    if not self.results["style_analysis"]["vocabulary_variety"]["is_optimal"]:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "vocabulary_variety",
    "type": "vocabulary_variety",
    "severity": "medium",
    "severity": "medium",
    "message": "Vocabulary variety is low, which can make the content repetitive.",
    "message": "Vocabulary variety is low, which can make the content repetitive.",
    "suggestion": "Use a wider range of words and avoid repeating the same terms frequently.",
    "suggestion": "Use a wider range of words and avoid repeating the same terms frequently.",
    }
    }
    )
    )


    # Check punctuation
    # Check punctuation
    punctuation = self.results["style_analysis"]["punctuation"]
    punctuation = self.results["style_analysis"]["punctuation"]


    if not punctuation["is_optimal"]:
    if not punctuation["is_optimal"]:
    if punctuation["density"] < 0.05:
    if punctuation["density"] < 0.05:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "punctuation",
    "type": "punctuation",
    "severity": "low",
    "severity": "low",
    "message": "Punctuation usage is low, which can make the content hard to read.",
    "message": "Punctuation usage is low, which can make the content hard to read.",
    "suggestion": "Add more punctuation to break up long sentences and improve readability.",
    "suggestion": "Add more punctuation to break up long sentences and improve readability.",
    }
    }


    elif punctuation["density"] > 0.1:
    elif punctuation["density"] > 0.1:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4(,
    "id": str(uuid.uuid4(,
    "type": "punctuation",
    "type": "punctuation",
    "severity": "low",
    "severity": "low",
    "message": "Punctuation usage is high, which can make the content choppy.",
    "message": "Punctuation usage is high, which can make the content choppy.",
    "suggestion": "Reduce excessive punctuation and combine some shorter sentences.",
    "suggestion": "Reduce excessive punctuation and combine some shorter sentences.",
    }
    }




    return recommendations
    return recommendations