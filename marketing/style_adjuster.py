"""
"""
Style adjuster module for the pAIssive Income project.
Style adjuster module for the pAIssive Income project.


This module provides classes for adjusting the style and tone of content.
This module provides classes for adjusting the style and tone of content.
"""
"""


import datetime
import datetime
import json
import json
import random
import random
import re
import re
import time
import time
import uuid
import uuid
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
from .tone_analyzer import ToneAnalyzer
from .tone_analyzer import ToneAnalyzer




class StyleAdjuster
class StyleAdjuster


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


    # Local imports
    # Local imports
    :
    :
    """
    """
    Class for adjusting the style and tone of content.
    Class for adjusting the style and tone of content.


    This class provides methods for adjusting tone, sentiment, and style
    This class provides methods for adjusting tone, sentiment, and style
    in content based on analysis and target style preferences.
    in content based on analysis and target style preferences.
    """
    """


    # Define style categories
    # Define style categories
    STYLE_CATEGORIES = {
    STYLE_CATEGORIES = {
    "formal": {
    "formal": {
    "description": "Professional, academic, or business-like style",
    "description": "Professional, academic, or business-like style",
    "avoid_words": [
    "avoid_words": [
    "awesome",
    "awesome",
    "cool",
    "cool",
    "wow",
    "wow",
    "yeah",
    "yeah",
    "hey",
    "hey",
    "ok",
    "ok",
    "okay",
    "okay",
    "gonna",
    "gonna",
    "wanna",
    "wanna",
    "gotta",
    "gotta",
    "kinda",
    "kinda",
    "sorta",
    "sorta",
    "stuf",
    "stuf",
    "things",
    "things",
    "whatever",
    "whatever",
    "anyway",
    "anyway",
    "somehow",
    "somehow",
    "like",
    "like",
    "you know",
    "you know",
    "I mean",
    "I mean",
    "well",
    "well",
    "so",
    "so",
    ],
    ],
    "prefer_words": [
    "prefer_words": [
    "excellent",
    "excellent",
    "impressive",
    "impressive",
    "remarkable",
    "remarkable",
    "indeed",
    "indeed",
    "greetings",
    "greetings",
    "acceptable",
    "acceptable",
    "certainly",
    "certainly",
    "going to",
    "going to",
    "want to",
    "want to",
    "got to",
    "got to",
    "somewhat",
    "somewhat",
    "rather",
    "rather",
    "items",
    "items",
    "elements",
    "elements",
    "regardless",
    "regardless",
    "nevertheless",
    "nevertheless",
    "in some manner",
    "in some manner",
    "such as",
    "such as",
    "as you are aware",
    "as you are aware",
    "to clarify",
    "to clarify",
    "in any case",
    "in any case",
    "therefore",
    "therefore",
    ],
    ],
    "sentence_structure": "complex",
    "sentence_structure": "complex",
    "paragraph_length": "medium to long",
    "paragraph_length": "medium to long",
    "punctuation": "standard",
    "punctuation": "standard",
    "voice": "passive often acceptable",
    "voice": "passive often acceptable",
    },
    },
    "conversational": {
    "conversational": {
    "description": "Friendly, casual, or personal style",
    "description": "Friendly, casual, or personal style",
    "avoid_words": [
    "avoid_words": [
    "hereby",
    "hereby",
    "therein",
    "therein",
    "aforementioned",
    "aforementioned",
    "heretofore",
    "heretofore",
    "pursuant",
    "pursuant",
    "notwithstanding",
    "notwithstanding",
    "henceforth",
    "henceforth",
    "it is necessary to",
    "it is necessary to",
    "it is important to",
    "it is important to",
    "it is essential to",
    "it is essential to",
    "the author",
    "the author",
    "the researcher",
    "the researcher",
    "the study",
    "the study",
    "shall",
    "shall",
    "must",
    "must",
    "ought",
    "ought",
    ],
    ],
    "prefer_words": [
    "prefer_words": [
    "here",
    "here",
    "in this",
    "in this",
    "mentioned earlier",
    "mentioned earlier",
    "before now",
    "before now",
    "according to",
    "according to",
    "despite",
    "despite",
    "from now on",
    "from now on",
    "you need to",
    "you need to",
    "it's important to",
    "it's important to",
    "it's essential to",
    "it's essential to",
    "I",
    "I",
    "we",
    "we",
    "our team",
    "our team",
    "will",
    "will",
    "need to",
    "need to",
    "should",
    "should",
    ],
    ],
    "sentence_structure": "simple to moderate",
    "sentence_structure": "simple to moderate",
    "paragraph_length": "short to medium",
    "paragraph_length": "short to medium",
    "punctuation": "relaxed",
    "punctuation": "relaxed",
    "voice": "active preferred",
    "voice": "active preferred",
    },
    },
    "persuasive": {
    "persuasive": {
    "description": "Convincing, compelling, or sales-oriented style",
    "description": "Convincing, compelling, or sales-oriented style",
    "avoid_words": [
    "avoid_words": [
    "perhaps",
    "perhaps",
    "maybe",
    "maybe",
    "possibly",
    "possibly",
    "might",
    "might",
    "could be",
    "could be",
    "somewhat",
    "somewhat",
    "relatively",
    "relatively",
    "comparatively",
    "comparatively",
    "moderately",
    "moderately",
    "it seems",
    "it seems",
    "it appears",
    "it appears",
    "it may be",
    "it may be",
    "it could be",
    "it could be",
    "in my opinion",
    "in my opinion",
    "I think",
    "I think",
    "I believe",
    "I believe",
    "I feel",
    "I feel",
    "unclear",
    "unclear",
    "uncertain",
    "uncertain",
    "unknown",
    "unknown",
    "undetermined",
    "undetermined",
    ],
    ],
    "prefer_words": [
    "prefer_words": [
    "definitely",
    "definitely",
    "certainly",
    "certainly",
    "absolutely",
    "absolutely",
    "will",
    "will",
    "is",
    "is",
    "extremely",
    "extremely",
    "highly",
    "highly",
    "significantly",
    "significantly",
    "substantially",
    "substantially",
    "it is clear",
    "it is clear",
    "it is evident",
    "it is evident",
    "it is certain",
    "it is certain",
    "it will",
    "it will",
    "without doubt",
    "without doubt",
    "clearly",
    "clearly",
    "obviously",
    "obviously",
    "undoubtedly",
    "undoubtedly",
    "proven",
    "proven",
    "established",
    "established",
    "confirmed",
    "confirmed",
    "verified",
    "verified",
    ],
    ],
    "sentence_structure": "varied, with strong statements",
    "sentence_structure": "varied, with strong statements",
    "paragraph_length": "short to medium",
    "paragraph_length": "short to medium",
    "punctuation": "emphatic",
    "punctuation": "emphatic",
    "voice": "active required",
    "voice": "active required",
    },
    },
    "informative": {
    "informative": {
    "description": "Educational, explanatory, or factual style",
    "description": "Educational, explanatory, or factual style",
    "avoid_words": [
    "avoid_words": [
    "I guess",
    "I guess",
    "I suppose",
    "I suppose",
    "I assume",
    "I assume",
    "I reckon",
    "I reckon",
    "kinda",
    "kinda",
    "sorta",
    "sorta",
    "pretty much",
    "pretty much",
    "more or less",
    "more or less",
    "stuf",
    "stuf",
    "things",
    "things",
    "whatever",
    "whatever",
    "anyway",
    "anyway",
    "somehow",
    "somehow",
    "like",
    "like",
    "you know",
    "you know",
    "I mean",
    "I mean",
    "well",
    "well",
    "so",
    "so",
    "probably",
    "probably",
    "hopefully",
    "hopefully",
    "maybe",
    "maybe",
    "perhaps",
    "perhaps",
    ],
    ],
    "prefer_words": [
    "prefer_words": [
    "research indicates",
    "research indicates",
    "evidence suggests",
    "evidence suggests",
    "data shows",
    "data shows",
    "analysis reveals",
    "analysis reveals",
    "approximately",
    "approximately",
    "roughly",
    "roughly",
    "nearly",
    "nearly",
    "about",
    "about",
    "components",
    "components",
    "elements",
    "elements",
    "factors",
    "factors",
    "aspects",
    "aspects",
    "characteristics",
    "characteristics",
    "for example",
    "for example",
    "specifically",
    "specifically",
    "in particular",
    "in particular",
    "namely",
    "namely",
    "likely",
    "likely",
    "potentially",
    "potentially",
    "possibly",
    "possibly",
    "theoretically",
    "theoretically",
    ],
    ],
    "sentence_structure": "clear and direct",
    "sentence_structure": "clear and direct",
    "paragraph_length": "medium",
    "paragraph_length": "medium",
    "punctuation": "standard",
    "punctuation": "standard",
    "voice": "mix of active and passive",
    "voice": "mix of active and passive",
    },
    },
    }
    }


    # Define word replacement dictionaries
    # Define word replacement dictionaries
    WORD_REPLACEMENTS = {
    WORD_REPLACEMENTS = {
    "formal": {
    "formal": {
    # Casual to formal word replacements
    # Casual to formal word replacements
    "awesome": ["excellent", "outstanding", "exceptional"],
    "awesome": ["excellent", "outstanding", "exceptional"],
    "cool": ["impressive", "remarkable", "noteworthy"],
    "cool": ["impressive", "remarkable", "noteworthy"],
    "wow": ["impressive", "remarkable", "extraordinary"],
    "wow": ["impressive", "remarkable", "extraordinary"],
    "yeah": ["yes", "indeed", "certainly"],
    "yeah": ["yes", "indeed", "certainly"],
    "hey": ["greetings", "hello", "good day"],
    "hey": ["greetings", "hello", "good day"],
    "ok": ["acceptable", "satisfactory", "adequate"],
    "ok": ["acceptable", "satisfactory", "adequate"],
    "okay": ["acceptable", "satisfactory", "adequate"],
    "okay": ["acceptable", "satisfactory", "adequate"],
    "gonna": ["going to", "will", "intend to"],
    "gonna": ["going to", "will", "intend to"],
    "wanna": ["want to", "wish to", "desire to"],
    "wanna": ["want to", "wish to", "desire to"],
    "gotta": ["have to", "must", "need to"],
    "gotta": ["have to", "must", "need to"],
    "kinda": ["somewhat", "rather", "relatively"],
    "kinda": ["somewhat", "rather", "relatively"],
    "sorta": ["somewhat", "rather", "relatively"],
    "sorta": ["somewhat", "rather", "relatively"],
    "stuf": ["items", "materials", "elements"],
    "stuf": ["items", "materials", "elements"],
    "things": ["items", "elements", "components"],
    "things": ["items", "elements", "components"],
    "whatever": ["regardless", "irrespective", "notwithstanding"],
    "whatever": ["regardless", "irrespective", "notwithstanding"],
    "anyway": ["nevertheless", "nonetheless", "however"],
    "anyway": ["nevertheless", "nonetheless", "however"],
    "somehow": ["in some manner", "by some means", "in some way"],
    "somehow": ["in some manner", "by some means", "in some way"],
    "like": ["such as", "similar to", "comparable to"],
    "like": ["such as", "similar to", "comparable to"],
    "you know": ["as you are aware", "as you understand", "as you recognize"],
    "you know": ["as you are aware", "as you understand", "as you recognize"],
    "I mean": ["to clarify", "to be precise", "specifically"],
    "I mean": ["to clarify", "to be precise", "specifically"],
    "well": ["in any case", "at any rate", "in fact"],
    "well": ["in any case", "at any rate", "in fact"],
    "so": ["therefore", "consequently", "thus"],
    "so": ["therefore", "consequently", "thus"],
    },
    },
    "conversational": {
    "conversational": {
    # Formal to conversational word replacements
    # Formal to conversational word replacements
    "hereby": ["here", "by this", "with this"],
    "hereby": ["here", "by this", "with this"],
    "therein": ["in this", "in there", "inside"],
    "therein": ["in this", "in there", "inside"],
    "aforementioned": [
    "aforementioned": [
    "mentioned earlier",
    "mentioned earlier",
    "mentioned above",
    "mentioned above",
    "that I talked about",
    "that I talked about",
    ],
    ],
    "heretofore": ["before now", "until now", "previously"],
    "heretofore": ["before now", "until now", "previously"],
    "pursuant": ["according to", "following", "based on"],
    "pursuant": ["according to", "following", "based on"],
    "notwithstanding": ["despite", "even though", "still"],
    "notwithstanding": ["despite", "even though", "still"],
    "henceforth": ["from now on", "going forward", "from this point on"],
    "henceforth": ["from now on", "going forward", "from this point on"],
    "it is necessary to": ["you need to", "you should", "it's important to"],
    "it is necessary to": ["you need to", "you should", "it's important to"],
    "it is important to": ["you need to", "you should", "it's key to"],
    "it is important to": ["you need to", "you should", "it's key to"],
    "it is essential to": ["you have to", "you must", "it's vital to"],
    "it is essential to": ["you have to", "you must", "it's vital to"],
    "the author": ["I", "me", "we"],
    "the author": ["I", "me", "we"],
    "the researcher": ["I", "me", "we"],
    "the researcher": ["I", "me", "we"],
    "the study": ["we", "our research", "our work"],
    "the study": ["we", "our research", "our work"],
    "shall": ["will", "going to", "plan to"],
    "shall": ["will", "going to", "plan to"],
    "must": ["need to", "have to", "should"],
    "must": ["need to", "have to", "should"],
    "ought": ["should", "need to", "might want to"],
    "ought": ["should", "need to", "might want to"],
    },
    },
    "persuasive": {
    "persuasive": {
    # Uncertain to persuasive word replacements
    # Uncertain to persuasive word replacements
    "perhaps": ["definitely", "certainly", "absolutely"],
    "perhaps": ["definitely", "certainly", "absolutely"],
    "maybe": ["definitely", "certainly", "without doubt"],
    "maybe": ["definitely", "certainly", "without doubt"],
    "possibly": ["definitely", "certainly", "absolutely"],
    "possibly": ["definitely", "certainly", "absolutely"],
    "might": ["will", "can", "does"],
    "might": ["will", "can", "does"],
    "could be": ["is", "will be", "definitely is"],
    "could be": ["is", "will be", "definitely is"],
    "somewhat": ["extremely", "highly", "significantly"],
    "somewhat": ["extremely", "highly", "significantly"],
    "relatively": ["extremely", "highly", "significantly"],
    "relatively": ["extremely", "highly", "significantly"],
    "comparatively": ["extremely", "highly", "significantly"],
    "comparatively": ["extremely", "highly", "significantly"],
    "moderately": ["substantially", "considerably", "greatly"],
    "moderately": ["substantially", "considerably", "greatly"],
    "it seems": ["it is clear", "it is evident", "it is certain"],
    "it seems": ["it is clear", "it is evident", "it is certain"],
    "it appears": ["it is clear", "it is evident", "it is certain"],
    "it appears": ["it is clear", "it is evident", "it is certain"],
    "it may be": ["it is", "it will be", "it certainly is"],
    "it may be": ["it is", "it will be", "it certainly is"],
    "it could be": ["it is", "it will be", "it certainly is"],
    "it could be": ["it is", "it will be", "it certainly is"],
    "in my opinion": ["without doubt", "clearly", "obviously"],
    "in my opinion": ["without doubt", "clearly", "obviously"],
    "I think": ["I know", "I am certain", "I guarantee"],
    "I think": ["I know", "I am certain", "I guarantee"],
    "I believe": ["I know", "I am certain", "I guarantee"],
    "I believe": ["I know", "I am certain", "I guarantee"],
    "I feel": ["I know", "I am certain", "I guarantee"],
    "I feel": ["I know", "I am certain", "I guarantee"],
    "unclear": ["proven", "established", "confirmed"],
    "unclear": ["proven", "established", "confirmed"],
    "uncertain": ["proven", "established", "confirmed"],
    "uncertain": ["proven", "established", "confirmed"],
    "unknown": ["well-known", "established", "recognized"],
    "unknown": ["well-known", "established", "recognized"],
    "undetermined": ["verified", "confirmed", "established"],
    "undetermined": ["verified", "confirmed", "established"],
    },
    },
    "informative": {
    "informative": {
    # Casual/subjective to informative word replacements
    # Casual/subjective to informative word replacements
    "I guess": ["research indicates", "evidence suggests", "data shows"],
    "I guess": ["research indicates", "evidence suggests", "data shows"],
    "I suppose": ["research indicates", "evidence suggests", "data shows"],
    "I suppose": ["research indicates", "evidence suggests", "data shows"],
    "I assume": ["research indicates", "evidence suggests", "data shows"],
    "I assume": ["research indicates", "evidence suggests", "data shows"],
    "I reckon": ["research indicates", "evidence suggests", "data shows"],
    "I reckon": ["research indicates", "evidence suggests", "data shows"],
    "kinda": ["approximately", "roughly", "nearly"],
    "kinda": ["approximately", "roughly", "nearly"],
    "sorta": ["approximately", "roughly", "nearly"],
    "sorta": ["approximately", "roughly", "nearly"],
    "pretty much": ["approximately", "roughly", "nearly"],
    "pretty much": ["approximately", "roughly", "nearly"],
    "more or less": ["approximately", "roughly", "nearly"],
    "more or less": ["approximately", "roughly", "nearly"],
    "stuf": ["components", "elements", "factors"],
    "stuf": ["components", "elements", "factors"],
    "things": ["components", "elements", "factors"],
    "things": ["components", "elements", "factors"],
    "whatever": [
    "whatever": [
    "any relevant factors",
    "any relevant factors",
    "all applicable elements",
    "all applicable elements",
    "various components",
    "various components",
    ],
    ],
    "anyway": ["in any case", "regardless", "nevertheless"],
    "anyway": ["in any case", "regardless", "nevertheless"],
    "somehow": ["through some mechanism", "by some process", "via some means"],
    "somehow": ["through some mechanism", "by some process", "via some means"],
    "like": ["for example", "such as", "including"],
    "like": ["for example", "such as", "including"],
    "you know": ["specifically", "in particular", "namely"],
    "you know": ["specifically", "in particular", "namely"],
    "I mean": ["specifically", "in particular", "namely"],
    "I mean": ["specifically", "in particular", "namely"],
    "well": ["in fact", "indeed", "notably"],
    "well": ["in fact", "indeed", "notably"],
    "so": ["therefore", "consequently", "as a result"],
    "so": ["therefore", "consequently", "as a result"],
    "probably": ["likely", "with high probability", "most likely"],
    "probably": ["likely", "with high probability", "most likely"],
    "hopefully": ["potentially", "possibly", "it is expected that"],
    "hopefully": ["potentially", "possibly", "it is expected that"],
    "maybe": ["potentially", "possibly", "it is possible that"],
    "maybe": ["potentially", "possibly", "it is possible that"],
    "perhaps": ["potentially", "possibly", "it is possible that"],
    "perhaps": ["potentially", "possibly", "it is possible that"],
    },
    },
    }
    }


    # Define sentence structure patterns
    # Define sentence structure patterns
    SENTENCE_STRUCTURE_PATTERNS = {
    SENTENCE_STRUCTURE_PATTERNS = {
    "simple": {
    "simple": {
    "description": "Short, direct sentences with a single clause",
    "description": "Short, direct sentences with a single clause",
    "examples": [
    "examples": [
    "We offer the best solution.",
    "We offer the best solution.",
    "Our product saves time.",
    "Our product saves time.",
    "Customers love our service.",
    "Customers love our service.",
    "The results are impressive.",
    "The results are impressive.",
    "This approach works well.",
    "This approach works well.",
    ],
    ],
    "pattern": r"^[^,;:]{10,40}[.!?]$",
    "pattern": r"^[^,;:]{10,40}[.!?]$",
    },
    },
    "compound": {
    "compound": {
    "description": "Two independent clauses joined by a conjunction",
    "description": "Two independent clauses joined by a conjunction",
    "examples": [
    "examples": [
    "We developed this product, and customers love it.",
    "We developed this product, and customers love it.",
    "The software is powerful, but it's easy to use.",
    "The software is powerful, but it's easy to use.",
    "You can start today, or you can wait until tomorrow.",
    "You can start today, or you can wait until tomorrow.",
    "The price is affordable, yet the quality is premium.",
    "The price is affordable, yet the quality is premium.",
    "We provide the tools, and you create the magic.",
    "We provide the tools, and you create the magic.",
    ],
    ],
    "pattern": r"^[^,;:]{10,30},[^,;:]{10,30}[.!?]$",
    "pattern": r"^[^,;:]{10,30},[^,;:]{10,30}[.!?]$",
    },
    },
    "complex": {
    "complex": {
    "description": "An independent clause with one or more dependent clauses",
    "description": "An independent clause with one or more dependent clauses",
    "examples": [
    "examples": [
    "When you use our product, you'll save hours of work.",
    "When you use our product, you'll save hours of work.",
    "Although the process is sophisticated, the interface is intuitive.",
    "Although the process is sophisticated, the interface is intuitive.",
    "If you want to increase productivity, our solution is ideal.",
    "If you want to increase productivity, our solution is ideal.",
    "Because we focus on quality, our customers stay with us.",
    "Because we focus on quality, our customers stay with us.",
    "While other options exist, our approach offers unique benefits.",
    "While other options exist, our approach offers unique benefits.",
    ],
    ],
    "pattern": r"^[^,;:]{10,30},[^,;:]{10,30}[.!?]$",
    "pattern": r"^[^,;:]{10,30},[^,;:]{10,30}[.!?]$",
    },
    },
    "compound-complex": {
    "compound-complex": {
    "description": "Multiple independent clauses with one or more dependent clauses",
    "description": "Multiple independent clauses with one or more dependent clauses",
    "examples": [
    "examples": [
    "When you implement our system, efficiency improves, and costs decrease.",
    "When you implement our system, efficiency improves, and costs decrease.",
    "Although the market is competitive, our product stands out, and customers recognize the difference.",
    "Although the market is competitive, our product stands out, and customers recognize the difference.",
    "If you're looking for results, our solution delivers, and our support team ensures your success.",
    "If you're looking for results, our solution delivers, and our support team ensures your success.",
    "Because we understand your challenges, we've designed this tool, and we continue to enhance it.",
    "Because we understand your challenges, we've designed this tool, and we continue to enhance it.",
    "While traditional methods work, our approach is innovative, and it produces superior outcomes.",
    "While traditional methods work, our approach is innovative, and it produces superior outcomes.",
    ],
    ],
    "pattern": r"^[^,;:]{10,30},[^,;:]{10,30},[^,;:]{10,30}[.!?]$",
    "pattern": r"^[^,;:]{10,30},[^,;:]{10,30},[^,;:]{10,30}[.!?]$",
    },
    },
    }
    }


    def __init__(
    def __init__(
    self,
    self,
    content: Optional[Dict[str, Any]] = None,
    content: Optional[Dict[str, Any]] = None,
    target_style: Optional[str] = None,
    target_style: Optional[str] = None,
    analyzer: Optional[ToneAnalyzer] = None,
    analyzer: Optional[ToneAnalyzer] = None,
    config: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize a style adjuster.
    Initialize a style adjuster.


    Args:
    Args:
    content: Optional content to adjust
    content: Optional content to adjust
    target_style: Optional target style for the content
    target_style: Optional target style for the content
    analyzer: Optional ToneAnalyzer instance
    analyzer: Optional ToneAnalyzer instance
    config: Optional configuration dictionary
    config: Optional configuration dictionary
    """
    """
    self.id = str(uuid.uuid4())
    self.id = str(uuid.uuid4())
    self.content = content
    self.content = content
    self.target_style = target_style or "conversational"
    self.target_style = target_style or "conversational"
    self.analyzer = analyzer
    self.analyzer = analyzer
    self.config = config or self.get_default_config()
    self.config = config or self.get_default_config()
    self.created_at = datetime.datetime.now().isoformat()
    self.created_at = datetime.datetime.now().isoformat()
    self.results = None
    self.results = None


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
    Get the default configuration for the style adjuster.
    Get the default configuration for the style adjuster.


    Returns:
    Returns:
    Default configuration dictionary
    Default configuration dictionary
    """
    """
    return {
    return {
    "max_suggestions": 10,  # Maximum number of suggestions to generate
    "max_suggestions": 10,  # Maximum number of suggestions to generate
    "min_suggestion_confidence": 0.7,  # Minimum confidence score for suggestions
    "min_suggestion_confidence": 0.7,  # Minimum confidence score for suggestions
    "prioritize_by": "impact",  # How to prioritize suggestions: impact, confidence, or position
    "prioritize_by": "impact",  # How to prioritize suggestions: impact, confidence, or position
    "adjust_word_choice": True,  # Whether to adjust word choice
    "adjust_word_choice": True,  # Whether to adjust word choice
    "adjust_sentence_structure": True,  # Whether to adjust sentence structure
    "adjust_sentence_structure": True,  # Whether to adjust sentence structure
    "adjust_paragraph_structure": True,  # Whether to adjust paragraph structure
    "adjust_paragraph_structure": True,  # Whether to adjust paragraph structure
    "adjust_punctuation": True,  # Whether to adjust punctuation
    "adjust_punctuation": True,  # Whether to adjust punctuation
    "adjust_voice": True,  # Whether to adjust voice (active/passive)
    "adjust_voice": True,  # Whether to adjust voice (active/passive)
    "target_style": self.target_style,  # Target style
    "target_style": self.target_style,  # Target style
    "timestamp": datetime.datetime.now().isoformat(),
    "timestamp": datetime.datetime.now().isoformat(),
    }
    }


    def validate_content(self) -> Tuple[bool, List[str]]:
    def validate_content(self) -> Tuple[bool, List[str]]:
    """
    """
    Validate the content for style adjustment.
    Validate the content for style adjustment.


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


    # Check if target style is valid
    # Check if target style is valid
    if self.target_style and self.target_style not in self.STYLE_CATEGORIES:
    if self.target_style and self.target_style not in self.STYLE_CATEGORIES:
    errors.append(
    errors.append(
    f"Invalid target style: {self.target_style}. Must be one of: {', '.join(self.STYLE_CATEGORIES.keys())}"
    f"Invalid target style: {self.target_style}. Must be one of: {', '.join(self.STYLE_CATEGORIES.keys())}"
    )
    )


    return len(errors) == 0, errors
    return len(errors) == 0, errors


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
    errors = []
    errors = []


    # Check required fields
    # Check required fields
    required_fields = [
    required_fields = [
    "max_suggestions",
    "max_suggestions",
    "min_suggestion_confidence",
    "min_suggestion_confidence",
    "prioritize_by",
    "prioritize_by",
    "target_style",
    "target_style",
    ]
    ]


    for field in required_fields:
    for field in required_fields:
    if field not in self.config:
    if field not in self.config:
    errors.append(f"Missing required field: {field}")
    errors.append(f"Missing required field: {field}")


    # Validate field types and values
    # Validate field types and values
    if "max_suggestions" in self.config and not (
    if "max_suggestions" in self.config and not (
    isinstance(self.config["max_suggestions"], int)
    isinstance(self.config["max_suggestions"], int)
    and self.config["max_suggestions"] > 0
    and self.config["max_suggestions"] > 0
    ):
    ):
    errors.append("max_suggestions must be a positive integer")
    errors.append("max_suggestions must be a positive integer")


    if "min_suggestion_confidence" in self.config and not (
    if "min_suggestion_confidence" in self.config and not (
    isinstance(self.config["min_suggestion_confidence"], (int, float))
    isinstance(self.config["min_suggestion_confidence"], (int, float))
    and 0 <= self.config["min_suggestion_confidence"] <= 1
    and 0 <= self.config["min_suggestion_confidence"] <= 1
    ):
    ):
    errors.append("min_suggestion_confidence must be a number between 0 and 1")
    errors.append("min_suggestion_confidence must be a number between 0 and 1")


    if "prioritize_by" in self.config and self.config["prioritize_by"] not in [
    if "prioritize_by" in self.config and self.config["prioritize_by"] not in [
    "impact",
    "impact",
    "confidence",
    "confidence",
    "position",
    "position",
    ]:
    ]:
    errors.append("prioritize_by must be one of: impact, confidence, position")
    errors.append("prioritize_by must be one of: impact, confidence, position")


    if (
    if (
    "target_style" in self.config
    "target_style" in self.config
    and self.config["target_style"] not in self.STYLE_CATEGORIES
    and self.config["target_style"] not in self.STYLE_CATEGORIES
    ):
    ):
    errors.append(
    errors.append(
    f"target_style must be one of: {', '.join(self.STYLE_CATEGORIES.keys())}"
    f"target_style must be one of: {', '.join(self.STYLE_CATEGORIES.keys())}"
    )
    )


    # Check boolean fields
    # Check boolean fields
    boolean_fields = [
    boolean_fields = [
    "adjust_word_choice",
    "adjust_word_choice",
    "adjust_sentence_structure",
    "adjust_sentence_structure",
    "adjust_paragraph_structure",
    "adjust_paragraph_structure",
    "adjust_punctuation",
    "adjust_punctuation",
    "adjust_voice",
    "adjust_voice",
    ]
    ]


    for field in boolean_fields:
    for field in boolean_fields:
    if field in self.config and not isinstance(self.config[field], bool):
    if field in self.config and not isinstance(self.config[field], bool):
    errors.append(f"{field} must be a boolean")
    errors.append(f"{field} must be a boolean")


    return len(errors) == 0, errors
    return len(errors) == 0, errors


    def set_content(self, content: Dict[str, Any]) -> None:
    def set_content(self, content: Dict[str, Any]) -> None:
    """
    """
    Set the content to adjust.
    Set the content to adjust.


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


    def set_target_style(self, target_style: str) -> None:
    def set_target_style(self, target_style: str) -> None:
    """
    """
    Set the target style for the content.
    Set the target style for the content.


    Args:
    Args:
    target_style: Target style
    target_style: Target style
    """
    """
    if target_style not in self.STYLE_CATEGORIES:
    if target_style not in self.STYLE_CATEGORIES:
    raise ValueError(
    raise ValueError(
    f"Invalid target style: {target_style}. Must be one of: {', '.join(self.STYLE_CATEGORIES.keys())}"
    f"Invalid target style: {target_style}. Must be one of: {', '.join(self.STYLE_CATEGORIES.keys())}"
    )
    )


    self.target_style = target_style
    self.target_style = target_style
    self.config["target_style"] = target_style
    self.config["target_style"] = target_style
    self.results = None  # Reset results
    self.results = None  # Reset results


    def set_analyzer(self, analyzer: ToneAnalyzer) -> None:
    def set_analyzer(self, analyzer: ToneAnalyzer) -> None:
    """
    """
    Set the tone analyzer.
    Set the tone analyzer.


    Args:
    Args:
    analyzer: ToneAnalyzer instance
    analyzer: ToneAnalyzer instance
    """
    """
    self.analyzer = analyzer
    self.analyzer = analyzer
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
    if self.content is None:
    if self.content is None:
    return ""
    return ""


    text = ""
    text = ""


    # Add title
    # Add title
    if "title" in self.content:
    if "title" in self.content:
    text += self.content["title"] + "\n\n"
    text += self.content["title"] + "\n\n"


    # Add meta description
    # Add meta description
    if "meta_description" in self.content:
    if "meta_description" in self.content:
    text += self.content["meta_description"] + "\n\n"
    text += self.content["meta_description"] + "\n\n"


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
    text += section["title"] + "\n\n"
    text += section["title"] + "\n\n"


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
    text += feature["name"] + "\n"
    text += feature["name"] + "\n"


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
    text += benefit["name"] + "\n"
    text += benefit["name"] + "\n"


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
    return word_tokenize(text.lower())
    return word_tokenize(text.lower())
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
    return text.split()
    return text.split()


    def _get_paragraphs(self, text: str) -> List[str]:
    def _get_paragraphs(self, text: str) -> List[str]:
    """
    """
    Get paragraphs from text.
    Get paragraphs from text.


    Args:
    Args:
    text: Text to analyze
    text: Text to analyze


    Returns:
    Returns:
    List of paragraphs
    List of paragraphs
    """
    """
    # Split on double newlines
    # Split on double newlines
    paragraphs = text.split("\n\n")
    paragraphs = text.split("\n\n")


    # Filter out empty paragraphs
    # Filter out empty paragraphs
    return [p.strip() for p in paragraphs if p.strip()]
    return [p.strip() for p in paragraphs if p.strip()]


    def _get_stopwords(self) -> List[str]:
    def _get_stopwords(self) -> List[str]:
    """
    """
    Get stopwords.
    Get stopwords.


    Returns:
    Returns:
    List of stopwords
    List of stopwords
    """
    """
    if NLTK_AVAILABLE:
    if NLTK_AVAILABLE:
    # Use NLTK for stopwords
    # Use NLTK for stopwords
    return stopwords.words("english")
    return stopwords.words("english")
    else:
    else:
    # Simple stopwords list
    # Simple stopwords list
    return [
    return [
    "a",
    "a",
    "an",
    "an",
    "the",
    "the",
    "and",
    "and",
    "but",
    "but",
    "or",
    "or",
    "for",
    "for",
    "nor",
    "nor",
    "on",
    "on",
    "at",
    "at",
    "to",
    "to",
    "by",
    "by",
    "in",
    "in",
    "o",
    "o",
    "with",
    "with",
    "about",
    "about",
    "against",
    "against",
    "between",
    "between",
    "into",
    "into",
    "through",
    "through",
    "during",
    "during",
    "before",
    "before",
    "after",
    "after",
    "above",
    "above",
    "below",
    "below",
    "from",
    "from",
    "up",
    "up",
    "down",
    "down",
    "out",
    "out",
    "of",
    "of",
    "over",
    "over",
    "under",
    "under",
    "again",
    "again",
    "further",
    "further",
    "then",
    "then",
    "once",
    "once",
    "here",
    "here",
    "there",
    "there",
    "when",
    "when",
    "where",
    "where",
    "why",
    "why",
    "how",
    "how",
    "all",
    "all",
    "any",
    "any",
    "both",
    "both",
    "each",
    "each",
    "few",
    "few",
    "more",
    "more",
    "most",
    "most",
    "other",
    "other",
    "some",
    "some",
    "such",
    "such",
    "no",
    "no",
    "nor",
    "nor",
    "not",
    "not",
    "only",
    "only",
    "own",
    "own",
    "same",
    "same",
    "so",
    "so",
    "than",
    "than",
    "too",
    "too",
    "very",
    "very",
    "s",
    "s",
    "t",
    "t",
    "can",
    "can",
    "will",
    "will",
    "just",
    "just",
    "don",
    "don",
    "don't",
    "don't",
    "should",
    "should",
    "should've",
    "should've",
    "now",
    "now",
    "d",
    "d",
    "ll",
    "ll",
    "m",
    "m",
    "o",
    "o",
    "re",
    "re",
    "ve",
    "ve",
    "y",
    "y",
    "ain",
    "ain",
    "aren",
    "aren",
    "aren't",
    "aren't",
    "couldn",
    "couldn",
    "couldn't",
    "couldn't",
    "didn",
    "didn",
    "didn't",
    "didn't",
    "doesn",
    "doesn",
    "doesn't",
    "doesn't",
    "hadn",
    "hadn",
    "hadn't",
    "hadn't",
    "hasn",
    "hasn",
    "hasn't",
    "hasn't",
    "haven",
    "haven",
    "haven't",
    "haven't",
    "isn",
    "isn",
    "isn't",
    "isn't",
    "ma",
    "ma",
    "mightn",
    "mightn",
    "mightn't",
    "mightn't",
    "mustn",
    "mustn",
    "mustn't",
    "mustn't",
    "needn",
    "needn",
    "needn't",
    "needn't",
    "shan",
    "shan",
    "shan't",
    "shan't",
    "shouldn",
    "shouldn",
    "shouldn't",
    "shouldn't",
    "wasn",
    "wasn",
    "wasn't",
    "wasn't",
    "weren",
    "weren",
    "weren't",
    "weren't",
    "won",
    "won",
    "won't",
    "won't",
    "wouldn",
    "wouldn",
    "wouldn't",
    "wouldn't",
    "i",
    "i",
    "me",
    "me",
    "my",
    "my",
    "mysel",
    "mysel",
    "we",
    "we",
    "our",
    "our",
    "ours",
    "ours",
    "ourselves",
    "ourselves",
    "you",
    "you",
    "your",
    "your",
    "yours",
    "yours",
    "yoursel",
    "yoursel",
    "yourselves",
    "yourselves",
    "he",
    "he",
    "him",
    "him",
    "his",
    "his",
    "himsel",
    "himsel",
    "she",
    "she",
    "her",
    "her",
    "hers",
    "hers",
    "hersel",
    "hersel",
    "it",
    "it",
    "its",
    "its",
    "itsel",
    "itsel",
    "they",
    "they",
    "them",
    "them",
    "their",
    "their",
    "theirs",
    "theirs",
    "themselves",
    "themselves",
    "what",
    "what",
    "which",
    "which",
    "who",
    "who",
    "whom",
    "whom",
    "this",
    "this",
    "that",
    "that",
    "these",
    "these",
    "those",
    "those",
    "am",
    "am",
    "is",
    "is",
    "are",
    "are",
    "was",
    "was",
    "were",
    "were",
    "be",
    "be",
    "been",
    "been",
    "being",
    "being",
    "have",
    "have",
    "has",
    "has",
    "had",
    "had",
    "having",
    "having",
    "do",
    "do",
    "does",
    "does",
    "did",
    "did",
    "doing",
    "doing",
    "would",
    "would",
    "could",
    "could",
    "should",
    "should",
    "ought",
    "ought",
    "i'm",
    "i'm",
    "you're",
    "you're",
    "he's",
    "he's",
    "she's",
    "she's",
    "it's",
    "it's",
    "we're",
    "we're",
    "they're",
    "they're",
    "i've",
    "i've",
    "you've",
    "you've",
    "we've",
    "we've",
    "they've",
    "they've",
    "i'd",
    "i'd",
    "you'd",
    "you'd",
    "he'd",
    "he'd",
    "she'd",
    "she'd",
    "we'd",
    "we'd",
    "they'd",
    "they'd",
    "i'll",
    "i'll",
    "you'll",
    "you'll",
    "he'll",
    "he'll",
    "she'll",
    "she'll",
    "we'll",
    "we'll",
    "they'll",
    "they'll",
    "isn't",
    "isn't",
    "aren't",
    "aren't",
    "wasn't",
    "wasn't",
    "weren't",
    "weren't",
    "hasn't",
    "hasn't",
    "haven't",
    "haven't",
    "hadn't",
    "hadn't",
    "doesn't",
    "doesn't",
    "don't",
    "don't",
    "didn't",
    "didn't",
    "won't",
    "won't",
    "wouldn't",
    "wouldn't",
    "shan't",
    "shan't",
    "shouldn't",
    "shouldn't",
    "can't",
    "can't",
    "cannot",
    "cannot",
    "couldn't",
    "couldn't",
    "mustn't",
    "mustn't",
    ]
    ]


    def _is_passive_voice(self, sentence: str) -> bool:
    def _is_passive_voice(self, sentence: str) -> bool:
    """
    """
    Check if a sentence is in passive voice.
    Check if a sentence is in passive voice.


    Args:
    Args:
    sentence: Sentence to check
    sentence: Sentence to check


    Returns:
    Returns:
    True if the sentence is in passive voice, False otherwise
    True if the sentence is in passive voice, False otherwise
    """
    """
    # Simple passive voice detection patterns
    # Simple passive voice detection patterns
    passive_patterns = [
    passive_patterns = [
    r"\b(?:am|is|are|was|were|be|being|been)\s+(\w+ed)\b",
    r"\b(?:am|is|are|was|were|be|being|been)\s+(\w+ed)\b",
    r"\b(?:am|is|are|was|were|be|being|been)\s+(\w+en)\b",
    r"\b(?:am|is|are|was|were|be|being|been)\s+(\w+en)\b",
    r"\b(?:am|is|are|was|were|be|being|been)\s+(\w+t)\b",
    r"\b(?:am|is|are|was|were|be|being|been)\s+(\w+t)\b",
    ]
    ]


    # Check if any pattern matches
    # Check if any pattern matches
    for pattern in passive_patterns:
    for pattern in passive_patterns:
    if re.search(pattern, sentence, re.IGNORECASE):
    if re.search(pattern, sentence, re.IGNORECASE):
    return True
    return True


    return False
    return False


    def _convert_to_active_voice(self, sentence: str) -> str:
    def _convert_to_active_voice(self, sentence: str) -> str:
    """
    """
    Convert a passive voice sentence to active voice.
    Convert a passive voice sentence to active voice.


    Args:
    Args:
    sentence: Sentence to convert
    sentence: Sentence to convert


    Returns:
    Returns:
    Sentence in active voice
    Sentence in active voice
    """
    """
    # This is a simplified implementation
    # This is a simplified implementation
    # A full implementation would require more complex NLP
    # A full implementation would require more complex NLP


    # Passive voice patterns and their active voice transformations
    # Passive voice patterns and their active voice transformations
    passive_patterns = [
    passive_patterns = [
    (r"\b(am|is|are)\s+(\w+ed)\s+by\s+(.+)", r"\3 \2s \1"),
    (r"\b(am|is|are)\s+(\w+ed)\s+by\s+(.+)", r"\3 \2s \1"),
    (r"\b(was|were)\s+(\w+ed)\s+by\s+(.+)", r"\3 \2ed \1"),
    (r"\b(was|were)\s+(\w+ed)\s+by\s+(.+)", r"\3 \2ed \1"),
    (r"\b(am|is|are)\s+being\s+(\w+ed)\s+by\s+(.+)", r"\3 is \2ing \1"),
    (r"\b(am|is|are)\s+being\s+(\w+ed)\s+by\s+(.+)", r"\3 is \2ing \1"),
    (r"\b(was|were)\s+being\s+(\w+ed)\s+by\s+(.+)", r"\3 was \2ing \1"),
    (r"\b(was|were)\s+being\s+(\w+ed)\s+by\s+(.+)", r"\3 was \2ing \1"),
    (r"\b(have|has)\s+been\s+(\w+ed)\s+by\s+(.+)", r"\3 has \2ed \1"),
    (r"\b(have|has)\s+been\s+(\w+ed)\s+by\s+(.+)", r"\3 has \2ed \1"),
    (r"\b(had)\s+been\s+(\w+ed)\s+by\s+(.+)", r"\3 had \2ed \1"),
    (r"\b(had)\s+been\s+(\w+ed)\s+by\s+(.+)", r"\3 had \2ed \1"),
    (r"\b(will|shall)\s+be\s+(\w+ed)\s+by\s+(.+)", r"\3 will \2 \1"),
    (r"\b(will|shall)\s+be\s+(\w+ed)\s+by\s+(.+)", r"\3 will \2 \1"),
    (
    (
    r"\b(would|should|could|might)\s+be\s+(\w+ed)\s+by\s+(.+)",
    r"\b(would|should|could|might)\s+be\s+(\w+ed)\s+by\s+(.+)",
    r"\3 would \2 \1",
    r"\3 would \2 \1",
    ),
    ),
    ]
    ]


    # Try each pattern
    # Try each pattern
    for pattern, replacement in passive_patterns:
    for pattern, replacement in passive_patterns:
    if re.search(pattern, sentence, re.IGNORECASE):
    if re.search(pattern, sentence, re.IGNORECASE):
    return re.sub(pattern, replacement, sentence, flags=re.IGNORECASE)
    return re.sub(pattern, replacement, sentence, flags=re.IGNORECASE)


    # If no pattern matches, return the original sentence
    # If no pattern matches, return the original sentence
    return sentence
    return sentence


    def _convert_to_passive_voice(self, sentence: str) -> str:
    def _convert_to_passive_voice(self, sentence: str) -> str:
    """
    """
    Convert an active voice sentence to passive voice.
    Convert an active voice sentence to passive voice.


    Args:
    Args:
    sentence: Sentence to convert
    sentence: Sentence to convert


    Returns:
    Returns:
    Sentence in passive voice
    Sentence in passive voice
    """
    """
    # This is a simplified implementation
    # This is a simplified implementation
    # A full implementation would require more complex NLP
    # A full implementation would require more complex NLP


    # Active voice patterns and their passive voice transformations
    # Active voice patterns and their passive voice transformations
    active_patterns = [
    active_patterns = [
    (r"\b(.+)\s+(\w+s)\s+(.+)", r"\3 is \2ed by \1"),
    (r"\b(.+)\s+(\w+s)\s+(.+)", r"\3 is \2ed by \1"),
    (r"\b(.+)\s+(\w+ed)\s+(.+)", r"\3 was \2ed by \1"),
    (r"\b(.+)\s+(\w+ed)\s+(.+)", r"\3 was \2ed by \1"),
    (r"\b(.+)\s+is\s+(\w+ing)\s+(.+)", r"\3 is being \2ed by \1"),
    (r"\b(.+)\s+is\s+(\w+ing)\s+(.+)", r"\3 is being \2ed by \1"),
    (r"\b(.+)\s+was\s+(\w+ing)\s+(.+)", r"\3 was being \2ed by \1"),
    (r"\b(.+)\s+was\s+(\w+ing)\s+(.+)", r"\3 was being \2ed by \1"),
    (r"\b(.+)\s+has\s+(\w+ed)\s+(.+)", r"\3 has been \2ed by \1"),
    (r"\b(.+)\s+has\s+(\w+ed)\s+(.+)", r"\3 has been \2ed by \1"),
    (r"\b(.+)\s+had\s+(\w+ed)\s+(.+)", r"\3 had been \2ed by \1"),
    (r"\b(.+)\s+had\s+(\w+ed)\s+(.+)", r"\3 had been \2ed by \1"),
    (r"\b(.+)\s+will\s+(\w+)\s+(.+)", r"\3 will be \2ed by \1"),
    (r"\b(.+)\s+will\s+(\w+)\s+(.+)", r"\3 will be \2ed by \1"),
    (r"\b(.+)\s+would\s+(\w+)\s+(.+)", r"\3 would be \2ed by \1"),
    (r"\b(.+)\s+would\s+(\w+)\s+(.+)", r"\3 would be \2ed by \1"),
    ]
    ]


    # Try each pattern
    # Try each pattern
    for pattern, replacement in active_patterns:
    for pattern, replacement in active_patterns:
    if re.search(pattern, sentence, re.IGNORECASE):
    if re.search(pattern, sentence, re.IGNORECASE):
    return re.sub(pattern, replacement, sentence, flags=re.IGNORECASE)
    return re.sub(pattern, replacement, sentence, flags=re.IGNORECASE)


    # If no pattern matches, return the original sentence
    # If no pattern matches, return the original sentence
    return sentence
    return sentence


    def _get_sentence_structure(self, sentence: str) -> str:
    def _get_sentence_structure(self, sentence: str) -> str:
    """
    """
    Determine the structure of a sentence.
    Determine the structure of a sentence.


    Args:
    Args:
    sentence: Sentence to analyze
    sentence: Sentence to analyze


    Returns:
    Returns:
    Sentence structure type
    Sentence structure type
    """
    """
    # Count clauses
    # Count clauses
    independent_clauses = len(re.findall(r"[^,;:]+(?:[,;:]|$)", sentence))
    independent_clauses = len(re.findall(r"[^,;:]+(?:[,;:]|$)", sentence))
    dependent_clauses = len(
    dependent_clauses = len(
    re.findall(
    re.findall(
    r"(?:because|although|while|if|when|after|before|since|unless|until|as|though)[^,;:.]*[,;:]",
    r"(?:because|although|while|if|when|after|before|since|unless|until|as|though)[^,;:.]*[,;:]",
    sentence,
    sentence,
    )
    )
    )
    )


    # Determine sentence structure
    # Determine sentence structure
    if independent_clauses == 1 and dependent_clauses == 0:
    if independent_clauses == 1 and dependent_clauses == 0:
    return "simple"
    return "simple"
    elif independent_clauses > 1 and dependent_clauses == 0:
    elif independent_clauses > 1 and dependent_clauses == 0:
    return "compound"
    return "compound"
    elif independent_clauses == 1 and dependent_clauses >= 1:
    elif independent_clauses == 1 and dependent_clauses >= 1:
    return "complex"
    return "complex"
    elif independent_clauses > 1 and dependent_clauses >= 1:
    elif independent_clauses > 1 and dependent_clauses >= 1:
    return "compound-complex"
    return "compound-complex"
    else:
    else:
    return "unknown"
    return "unknown"


    def _get_sentence_complexity(self, sentence: str) -> float:
    def _get_sentence_complexity(self, sentence: str) -> float:
    """
    """
    Calculate the complexity of a sentence.
    Calculate the complexity of a sentence.


    Args:
    Args:
    sentence: Sentence to analyze
    sentence: Sentence to analyze


    Returns:
    Returns:
    Complexity score
    Complexity score
    """
    """
    # Count words
    # Count words
    words = self._get_words(sentence)
    words = self._get_words(sentence)
    word_count = len(words)
    word_count = len(words)


    # Count clauses
    # Count clauses
    clauses = len(re.findall(r"[^,;:]+(?:[,;:]|$)", sentence))
    clauses = len(re.findall(r"[^,;:]+(?:[,;:]|$)", sentence))


    # Count commas, semicolons, and colons
    # Count commas, semicolons, and colons
    punctuation_count = len(re.findall(r"[,;:]", sentence))
    punctuation_count = len(re.findall(r"[,;:]", sentence))


    # Calculate complexity
    # Calculate complexity
    complexity = (word_count / 10) + clauses + (punctuation_count / 2)
    complexity = (word_count / 10) + clauses + (punctuation_count / 2)


    return complexity
    return complexity


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the style adjuster to a dictionary.
    Convert the style adjuster to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the style adjuster
    Dictionary representation of the style adjuster
    """
    """
    return {
    return {
    "id": self.id,
    "id": self.id,
    "target_style": self.target_style,
    "target_style": self.target_style,
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
    Convert the style adjuster to a JSON string.
    Convert the style adjuster to a JSON string.


    Args:
    Args:
    indent: Number of spaces for indentation
    indent: Number of spaces for indentation


    Returns:
    Returns:
    JSON string representation of the style adjuster
    JSON string representation of the style adjuster
    """
    """
    return json.dumps(self.to_dict(), indent=indent)
    return json.dumps(self.to_dict(), indent=indent)


    def analyze(self) -> Dict[str, Any]:
    def analyze(self) -> Dict[str, Any]:
    """
    """
    Analyze the content for style adjustment.
    Analyze the content for style adjustment.


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


    # Use existing analyzer if available
    # Use existing analyzer if available
    if self.analyzer is not None:
    if self.analyzer is not None:
    # Set content and target tone
    # Set content and target tone
    self.analyzer.content = self.content
    self.analyzer.content = self.content
    self.analyzer.set_target_tone(self.target_style)
    self.analyzer.set_target_tone(self.target_style)


    # Analyze content
    # Analyze content
    analysis_results = self.analyzer.analyze()
    analysis_results = self.analyzer.analyze()
    else:
    else:
    # Create a new analyzer
    # Create a new analyzer
    analyzer = ToneAnalyzer(self.content, self.target_style)
    analyzer = ToneAnalyzer(self.content, self.target_style)


    # Analyze content
    # Analyze content
    analysis_results = analyzer.analyze()
    analysis_results = analyzer.analyze()


    # Store analyzer
    # Store analyzer
    self.analyzer = analyzer
    self.analyzer = analyzer


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
    "target_style": self.target_style,
    "target_style": self.target_style,
    "analysis": analysis_results,
    "analysis": analysis_results,
    "adjustments": {
    "adjustments": {
    "word_choice": [],
    "word_choice": [],
    "sentence_structure": [],
    "sentence_structure": [],
    "paragraph_structure": [],
    "paragraph_structure": [],
    "punctuation": [],
    "punctuation": [],
    "voice": [],
    "voice": [],
    },
    },
    "adjusted_content": None,
    "adjusted_content": None,
    }
    }


    return self.results
    return self.results


    def adjust(self) -> Dict[str, Any]:
    def adjust(self) -> Dict[str, Any]:
    """
    """
    Adjust the content to match the target style.
    Adjust the content to match the target style.


    Returns:
    Returns:
    Dictionary with adjustment results
    Dictionary with adjustment results
    """
    """
    # Analyze content if not already analyzed
    # Analyze content if not already analyzed
    if self.results is None:
    if self.results is None:
    self.analyze()
    self.analyze()


    # Initialize adjusted content
    # Initialize adjusted content
    adjusted_content = self.content.copy()
    adjusted_content = self.content.copy()


    # Apply adjustments
    # Apply adjustments
    if self.config["adjust_word_choice"]:
    if self.config["adjust_word_choice"]:
    adjusted_content = self._adjust_word_choice(adjusted_content)
    adjusted_content = self._adjust_word_choice(adjusted_content)


    if self.config["adjust_sentence_structure"]:
    if self.config["adjust_sentence_structure"]:
    adjusted_content = self._adjust_sentence_structure(adjusted_content)
    adjusted_content = self._adjust_sentence_structure(adjusted_content)


    if self.config["adjust_paragraph_structure"]:
    if self.config["adjust_paragraph_structure"]:
    adjusted_content = self._adjust_paragraph_structure(adjusted_content)
    adjusted_content = self._adjust_paragraph_structure(adjusted_content)


    if self.config["adjust_punctuation"]:
    if self.config["adjust_punctuation"]:
    adjusted_content = self._adjust_punctuation(adjusted_content)
    adjusted_content = self._adjust_punctuation(adjusted_content)


    if self.config["adjust_voice"]:
    if self.config["adjust_voice"]:
    adjusted_content = self._adjust_voice(adjusted_content)
    adjusted_content = self._adjust_voice(adjusted_content)


    # Store adjusted content
    # Store adjusted content
    self.results["adjusted_content"] = adjusted_content
    self.results["adjusted_content"] = adjusted_content


    return self.results
    return self.results


    def _adjust_word_choice(self, content: Dict[str, Any]) -> Dict[str, Any]:
    def _adjust_word_choice(self, content: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Adjust word choice in content.
    Adjust word choice in content.


    Args:
    Args:
    content: Content to adjust
    content: Content to adjust


    Returns:
    Returns:
    Adjusted content
    Adjusted content
    """
    """
    # Get target style word replacements
    # Get target style word replacements
    if self.target_style not in self.WORD_REPLACEMENTS:
    if self.target_style not in self.WORD_REPLACEMENTS:
    return content
    return content


    word_replacements = self.WORD_REPLACEMENTS[self.target_style]
    word_replacements = self.WORD_REPLACEMENTS[self.target_style]


    # Create a copy of the content
    # Create a copy of the content
    adjusted_content = content.copy()
    adjusted_content = content.copy()


    # Extract text from content
    # Extract text from content
    text = self._extract_text_from_content()
    text = self._extract_text_from_content()


    # Get sentences
    # Get sentences
    sentences = self._get_sentences(text)
    sentences = self._get_sentences(text)


    # Initialize adjustments
    # Initialize adjustments
    adjustments = []
    adjustments = []


    # Process each sentence
    # Process each sentence
    for sentence in sentences:
    for sentence in sentences:
    # Check for words to replace
    # Check for words to replace
    for word, replacements in word_replacements.items():
    for word, replacements in word_replacements.items():
    # Create pattern to match whole word
    # Create pattern to match whole word
    pattern = r"\b" + re.escape(word) + r"\b"
    pattern = r"\b" + re.escape(word) + r"\b"


    # Find all matches
    # Find all matches
    matches = list(re.finditer(pattern, sentence, re.IGNORECASE))
    matches = list(re.finditer(pattern, sentence, re.IGNORECASE))


    # Process each match
    # Process each match
    for match in matches:
    for match in matches:
    # Get replacement word
    # Get replacement word
    replacement = random.choice(replacements)
    replacement = random.choice(replacements)


    # Create adjustment
    # Create adjustment
    adjustment = {
    adjustment = {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "word_choice",
    "type": "word_choice",
    "original": match.group(0),
    "original": match.group(0),
    "replacement": replacement,
    "replacement": replacement,
    "sentence": sentence,
    "sentence": sentence,
    "position": match.span(),
    "position": match.span(),
    "confidence": 0.9,
    "confidence": 0.9,
    "impact": "medium",
    "impact": "medium",
    }
    }


    # Add adjustment
    # Add adjustment
    adjustments.append(adjustment)
    adjustments.append(adjustment)


    # Replace in content
    # Replace in content
    for key in adjusted_content:
    for key in adjusted_content:
    if isinstance(adjusted_content[key], str):
    if isinstance(adjusted_content[key], str):
    adjusted_content[key] = re.sub(
    adjusted_content[key] = re.sub(
    pattern,
    pattern,
    replacement,
    replacement,
    adjusted_content[key],
    adjusted_content[key],
    flags=re.IGNORECASE,
    flags=re.IGNORECASE,
    )
    )
    elif isinstance(adjusted_content[key], list):
    elif isinstance(adjusted_content[key], list):
    for i, item in enumerate(adjusted_content[key]):
    for i, item in enumerate(adjusted_content[key]):
    if isinstance(item, str):
    if isinstance(item, str):
    adjusted_content[key][i] = re.sub(
    adjusted_content[key][i] = re.sub(
    pattern, replacement, item, flags=re.IGNORECASE
    pattern, replacement, item, flags=re.IGNORECASE
    )
    )
    elif isinstance(item, dict):
    elif isinstance(item, dict):
    for subkey in item:
    for subkey in item:
    if isinstance(item[subkey], str):
    if isinstance(item[subkey], str):
    item[subkey] = re.sub(
    item[subkey] = re.sub(
    pattern,
    pattern,
    replacement,
    replacement,
    item[subkey],
    item[subkey],
    flags=re.IGNORECASE,
    flags=re.IGNORECASE,
    )
    )


    # Store adjustments
    # Store adjustments
    self.results["adjustments"]["word_choice"] = adjustments
    self.results["adjustments"]["word_choice"] = adjustments


    return adjusted_content
    return adjusted_content


    def _adjust_sentence_structure(self, content: Dict[str, Any]) -> Dict[str, Any]:
    def _adjust_sentence_structure(self, content: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Adjust sentence structure in content.
    Adjust sentence structure in content.


    Args:
    Args:
    content: Content to adjust
    content: Content to adjust


    Returns:
    Returns:
    Adjusted content
    Adjusted content
    """
    """
    # Get target style
    # Get target style
    style_data = self.STYLE_CATEGORIES.get(self.target_style, {})
    style_data = self.STYLE_CATEGORIES.get(self.target_style, {})
    target_sentence_structure = style_data.get("sentence_structure", "")
    target_sentence_structure = style_data.get("sentence_structure", "")


    # If no target sentence structure, return content
    # If no target sentence structure, return content
    if not target_sentence_structure:
    if not target_sentence_structure:
    return content
    return content


    # Create a copy of the content
    # Create a copy of the content
    adjusted_content = content.copy()
    adjusted_content = content.copy()


    # Extract text from content
    # Extract text from content
    text = self._extract_text_from_content()
    text = self._extract_text_from_content()


    # Get sentences
    # Get sentences
    sentences = self._get_sentences(text)
    sentences = self._get_sentences(text)


    # Initialize adjustments
    # Initialize adjustments
    adjustments = []
    adjustments = []


    # Process each sentence
    # Process each sentence
    for sentence in sentences:
    for sentence in sentences:
    # Get sentence structure
    # Get sentence structure
    structure = self._get_sentence_structure(sentence)
    structure = self._get_sentence_structure(sentence)


    # Check if adjustment needed
    # Check if adjustment needed
    if structure != target_sentence_structure:
    if structure != target_sentence_structure:
    # Get sentence complexity
    # Get sentence complexity
    complexity = self._get_sentence_complexity(sentence)
    complexity = self._get_sentence_complexity(sentence)


    # Determine adjustment type
    # Determine adjustment type
    if "simple" in target_sentence_structure and complexity > 2:
    if "simple" in target_sentence_structure and complexity > 2:
    # Split into simpler sentences
    # Split into simpler sentences
    adjusted_sentence = self._simplify_sentence(sentence)
    adjusted_sentence = self._simplify_sentence(sentence)


    # Create adjustment
    # Create adjustment
    adjustment = {
    adjustment = {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "sentence_structure",
    "type": "sentence_structure",
    "original": sentence,
    "original": sentence,
    "replacement": adjusted_sentence,
    "replacement": adjusted_sentence,
    "original_structure": structure,
    "original_structure": structure,
    "target_structure": target_sentence_structure,
    "target_structure": target_sentence_structure,
    "confidence": 0.7,
    "confidence": 0.7,
    "impact": "high",
    "impact": "high",
    }
    }


    # Add adjustment
    # Add adjustment
    adjustments.append(adjustment)
    adjustments.append(adjustment)


    # Replace in content
    # Replace in content
    for key in adjusted_content:
    for key in adjusted_content:
    if isinstance(adjusted_content[key], str):
    if isinstance(adjusted_content[key], str):
    adjusted_content[key] = adjusted_content[key].replace(
    adjusted_content[key] = adjusted_content[key].replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )
    elif isinstance(adjusted_content[key], list):
    elif isinstance(adjusted_content[key], list):
    for i, item in enumerate(adjusted_content[key]):
    for i, item in enumerate(adjusted_content[key]):
    if isinstance(item, str):
    if isinstance(item, str):
    adjusted_content[key][i] = item.replace(
    adjusted_content[key][i] = item.replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )
    elif isinstance(item, dict):
    elif isinstance(item, dict):
    for subkey in item:
    for subkey in item:
    if isinstance(item[subkey], str):
    if isinstance(item[subkey], str):
    item[subkey] = item[subkey].replace(
    item[subkey] = item[subkey].replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )


    elif "complex" in target_sentence_structure and complexity < 3:
    elif "complex" in target_sentence_structure and complexity < 3:
    # Combine with adjacent sentence or add complexity
    # Combine with adjacent sentence or add complexity
    adjusted_sentence = self._complexify_sentence(sentence, sentences)
    adjusted_sentence = self._complexify_sentence(sentence, sentences)


    # Create adjustment
    # Create adjustment
    adjustment = {
    adjustment = {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "sentence_structure",
    "type": "sentence_structure",
    "original": sentence,
    "original": sentence,
    "replacement": adjusted_sentence,
    "replacement": adjusted_sentence,
    "original_structure": structure,
    "original_structure": structure,
    "target_structure": target_sentence_structure,
    "target_structure": target_sentence_structure,
    "confidence": 0.6,
    "confidence": 0.6,
    "impact": "high",
    "impact": "high",
    }
    }


    # Add adjustment
    # Add adjustment
    adjustments.append(adjustment)
    adjustments.append(adjustment)


    # Replace in content
    # Replace in content
    for key in adjusted_content:
    for key in adjusted_content:
    if isinstance(adjusted_content[key], str):
    if isinstance(adjusted_content[key], str):
    adjusted_content[key] = adjusted_content[key].replace(
    adjusted_content[key] = adjusted_content[key].replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )
    elif isinstance(adjusted_content[key], list):
    elif isinstance(adjusted_content[key], list):
    for i, item in enumerate(adjusted_content[key]):
    for i, item in enumerate(adjusted_content[key]):
    if isinstance(item, str):
    if isinstance(item, str):
    adjusted_content[key][i] = item.replace(
    adjusted_content[key][i] = item.replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )
    elif isinstance(item, dict):
    elif isinstance(item, dict):
    for subkey in item:
    for subkey in item:
    if isinstance(item[subkey], str):
    if isinstance(item[subkey], str):
    item[subkey] = item[subkey].replace(
    item[subkey] = item[subkey].replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )


    # Store adjustments
    # Store adjustments
    self.results["adjustments"]["sentence_structure"] = adjustments
    self.results["adjustments"]["sentence_structure"] = adjustments


    return adjusted_content
    return adjusted_content


    def _simplify_sentence(self, sentence: str) -> str:
    def _simplify_sentence(self, sentence: str) -> str:
    """
    """
    Simplify a complex sentence.
    Simplify a complex sentence.


    Args:
    Args:
    sentence: Sentence to simplify
    sentence: Sentence to simplify


    Returns:
    Returns:
    Simplified sentence
    Simplified sentence
    """
    """
    # Split on conjunctions
    # Split on conjunctions
    conjunctions = [", and ", ", but ", ", or ", ", nor ", ", yet ", ", so "]
    conjunctions = [", and ", ", but ", ", or ", ", nor ", ", yet ", ", so "]


    for conjunction in conjunctions:
    for conjunction in conjunctions:
    if conjunction in sentence:
    if conjunction in sentence:
    parts = sentence.split(conjunction, 1)
    parts = sentence.split(conjunction, 1)
    return parts[0] + ". " + parts[1].capitalize()
    return parts[0] + ". " + parts[1].capitalize()


    # Split on dependent clause markers
    # Split on dependent clause markers
    markers = [
    markers = [
    ", which ",
    ", which ",
    ", who ",
    ", who ",
    ", whom ",
    ", whom ",
    ", whose ",
    ", whose ",
    ", where ",
    ", where ",
    ", when ",
    ", when ",
    ", why ",
    ", why ",
    " because ",
    " because ",
    " although ",
    " although ",
    " though ",
    " though ",
    " even though ",
    " even though ",
    " while ",
    " while ",
    " whereas ",
    " whereas ",
    " if ",
    " if ",
    " unless ",
    " unless ",
    " until ",
    " until ",
    " since ",
    " since ",
    " as ",
    " as ",
    " as if ",
    " as if ",
    " as though ",
    " as though ",
    ]
    ]


    for marker in markers:
    for marker in markers:
    if marker in sentence.lower():
    if marker in sentence.lower():
    parts = sentence.lower().split(marker, 1)
    parts = sentence.lower().split(marker, 1)


    # Determine which part is the independent clause
    # Determine which part is the independent clause
    if "." in parts[0] or "!" in parts[0] or "?" in parts[0]:
    if "." in parts[0] or "!" in parts[0] or "?" in parts[0]:
    # First part is a complete sentence
    # First part is a complete sentence
    return parts[0] + ". " + parts[1].capitalize()
    return parts[0] + ". " + parts[1].capitalize()
    else:
    else:
    # Second part might be the independent clause
    # Second part might be the independent clause
    return parts[0] + ". " + parts[1].capitalize()
    return parts[0] + ". " + parts[1].capitalize()


    # If no clear way to split, return original
    # If no clear way to split, return original
    return sentence
    return sentence


    def _complexify_sentence(self, sentence: str, all_sentences: List[str]) -> str:
    def _complexify_sentence(self, sentence: str, all_sentences: List[str]) -> str:
    """
    """
    Make a simple sentence more complex.
    Make a simple sentence more complex.


    Args:
    Args:
    sentence: Sentence to make more complex
    sentence: Sentence to make more complex
    all_sentences: All sentences in the text
    all_sentences: All sentences in the text


    Returns:
    Returns:
    More complex sentence
    More complex sentence
    """
    """
    # Try to combine with adjacent sentence
    # Try to combine with adjacent sentence
    index = all_sentences.index(sentence)
    index = all_sentences.index(sentence)


    if index < len(all_sentences) - 1:
    if index < len(all_sentences) - 1:
    next_sentence = all_sentences[index + 1]
    next_sentence = all_sentences[index + 1]


    # Check if next sentence is short
    # Check if next sentence is short
    if len(self._get_words(next_sentence)) < 10:
    if len(self._get_words(next_sentence)) < 10:
    # Combine with conjunction
    # Combine with conjunction
    conjunctions = [", and ", ", but ", ", or ", ", yet ", ", so "]
    conjunctions = [", and ", ", but ", ", or ", ", yet ", ", so "]
    conjunction = random.choice(conjunctions)
    conjunction = random.choice(conjunctions)


    return (
    return (
    sentence
    sentence
    + conjunction
    + conjunction
    + next_sentence[0].lower()
    + next_sentence[0].lower()
    + next_sentence[1:]
    + next_sentence[1:]
    )
    )


    # Add a dependent clause
    # Add a dependent clause
    dependent_clauses = [
    dependent_clauses = [
    "which is important",
    "which is important",
    "which is significant",
    "which is significant",
    "which is noteworthy",
    "which is noteworthy",
    "which is beneficial",
    "which is beneficial",
    "which is advantageous",
    "which is advantageous",
    "which is valuable",
    "which is valuable",
    "which is essential",
    "which is essential",
    "which is critical",
    "which is critical",
    "which is crucial",
    "which is crucial",
    "which is necessary",
    "which is necessary",
    ]
    ]


    return sentence[:-1] + ", " + random.choice(dependent_clauses) + sentence[-1]
    return sentence[:-1] + ", " + random.choice(dependent_clauses) + sentence[-1]


    def _adjust_paragraph_structure(self, content: Dict[str, Any]) -> Dict[str, Any]:
    def _adjust_paragraph_structure(self, content: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Adjust paragraph structure in content.
    Adjust paragraph structure in content.


    Args:
    Args:
    content: Content to adjust
    content: Content to adjust


    Returns:
    Returns:
    Adjusted content
    Adjusted content
    """
    """
    # Get target style
    # Get target style
    style_data = self.STYLE_CATEGORIES.get(self.target_style, {})
    style_data = self.STYLE_CATEGORIES.get(self.target_style, {})
    target_paragraph_length = style_data.get("paragraph_length", "")
    target_paragraph_length = style_data.get("paragraph_length", "")


    # If no target paragraph length, return content
    # If no target paragraph length, return content
    if not target_paragraph_length:
    if not target_paragraph_length:
    return content
    return content


    # Create a copy of the content
    # Create a copy of the content
    adjusted_content = content.copy()
    adjusted_content = content.copy()


    # Extract text from content
    # Extract text from content
    text = self._extract_text_from_content()
    text = self._extract_text_from_content()


    # Get paragraphs
    # Get paragraphs
    paragraphs = self._get_paragraphs(text)
    paragraphs = self._get_paragraphs(text)


    # Initialize adjustments
    # Initialize adjustments
    adjustments = []
    adjustments = []


    # Process each paragraph
    # Process each paragraph
    for paragraph in paragraphs:
    for paragraph in paragraphs:
    # Get paragraph length
    # Get paragraph length
    word_count = len(self._get_words(paragraph))
    word_count = len(self._get_words(paragraph))


    # Check if adjustment needed
    # Check if adjustment needed
    if "short" in target_paragraph_length and word_count > 75:
    if "short" in target_paragraph_length and word_count > 75:
    # Split into shorter paragraphs
    # Split into shorter paragraphs
    sentences = self._get_sentences(paragraph)
    sentences = self._get_sentences(paragraph)
    mid_point = len(sentences) // 2
    mid_point = len(sentences) // 2


    first_half = " ".join(sentences[:mid_point])
    first_half = " ".join(sentences[:mid_point])
    second_half = " ".join(sentences[mid_point:])
    second_half = " ".join(sentences[mid_point:])


    adjusted_paragraph = first_half + "\n\n" + second_half
    adjusted_paragraph = first_half + "\n\n" + second_half


    # Create adjustment
    # Create adjustment
    adjustment = {
    adjustment = {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "paragraph_structure",
    "type": "paragraph_structure",
    "original": paragraph,
    "original": paragraph,
    "replacement": adjusted_paragraph,
    "replacement": adjusted_paragraph,
    "original_length": word_count,
    "original_length": word_count,
    "target_length": "short",
    "target_length": "short",
    "confidence": 0.8,
    "confidence": 0.8,
    "impact": "medium",
    "impact": "medium",
    }
    }


    # Add adjustment
    # Add adjustment
    adjustments.append(adjustment)
    adjustments.append(adjustment)


    # Replace in content
    # Replace in content
    for key in adjusted_content:
    for key in adjusted_content:
    if isinstance(adjusted_content[key], str):
    if isinstance(adjusted_content[key], str):
    adjusted_content[key] = adjusted_content[key].replace(
    adjusted_content[key] = adjusted_content[key].replace(
    paragraph, adjusted_paragraph
    paragraph, adjusted_paragraph
    )
    )
    elif isinstance(adjusted_content[key], list):
    elif isinstance(adjusted_content[key], list):
    for i, item in enumerate(adjusted_content[key]):
    for i, item in enumerate(adjusted_content[key]):
    if isinstance(item, str):
    if isinstance(item, str):
    adjusted_content[key][i] = item.replace(
    adjusted_content[key][i] = item.replace(
    paragraph, adjusted_paragraph
    paragraph, adjusted_paragraph
    )
    )
    elif isinstance(item, dict):
    elif isinstance(item, dict):
    for subkey in item:
    for subkey in item:
    if isinstance(item[subkey], str):
    if isinstance(item[subkey], str):
    item[subkey] = item[subkey].replace(
    item[subkey] = item[subkey].replace(
    paragraph, adjusted_paragraph
    paragraph, adjusted_paragraph
    )
    )


    elif (
    elif (
    "long" in target_paragraph_length
    "long" in target_paragraph_length
    and word_count < 50
    and word_count < 50
    and len(paragraphs) > 1
    and len(paragraphs) > 1
    ):
    ):
    # Try to combine with adjacent paragraph
    # Try to combine with adjacent paragraph
    index = paragraphs.index(paragraph)
    index = paragraphs.index(paragraph)


    if index < len(paragraphs) - 1:
    if index < len(paragraphs) - 1:
    next_paragraph = paragraphs[index + 1]
    next_paragraph = paragraphs[index + 1]
    combined = paragraph + " " + next_paragraph
    combined = paragraph + " " + next_paragraph


    # Create adjustment
    # Create adjustment
    adjustment = {
    adjustment = {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "paragraph_structure",
    "type": "paragraph_structure",
    "original": paragraph + "\n\n" + next_paragraph,
    "original": paragraph + "\n\n" + next_paragraph,
    "replacement": combined,
    "replacement": combined,
    "original_length": word_count,
    "original_length": word_count,
    "target_length": "long",
    "target_length": "long",
    "confidence": 0.7,
    "confidence": 0.7,
    "impact": "medium",
    "impact": "medium",
    }
    }


    # Add adjustment
    # Add adjustment
    adjustments.append(adjustment)
    adjustments.append(adjustment)


    # Replace in content
    # Replace in content
    for key in adjusted_content:
    for key in adjusted_content:
    if isinstance(adjusted_content[key], str):
    if isinstance(adjusted_content[key], str):
    adjusted_content[key] = adjusted_content[key].replace(
    adjusted_content[key] = adjusted_content[key].replace(
    paragraph + "\n\n" + next_paragraph, combined
    paragraph + "\n\n" + next_paragraph, combined
    )
    )
    elif isinstance(adjusted_content[key], list):
    elif isinstance(adjusted_content[key], list):
    for i, item in enumerate(adjusted_content[key]):
    for i, item in enumerate(adjusted_content[key]):
    if isinstance(item, str):
    if isinstance(item, str):
    adjusted_content[key][i] = item.replace(
    adjusted_content[key][i] = item.replace(
    paragraph + "\n\n" + next_paragraph, combined
    paragraph + "\n\n" + next_paragraph, combined
    )
    )
    elif isinstance(item, dict):
    elif isinstance(item, dict):
    for subkey in item:
    for subkey in item:
    if isinstance(item[subkey], str):
    if isinstance(item[subkey], str):
    item[subkey] = item[subkey].replace(
    item[subkey] = item[subkey].replace(
    paragraph + "\n\n" + next_paragraph,
    paragraph + "\n\n" + next_paragraph,
    combined,
    combined,
    )
    )


    # Store adjustments
    # Store adjustments
    self.results["adjustments"]["paragraph_structure"] = adjustments
    self.results["adjustments"]["paragraph_structure"] = adjustments


    return adjusted_content
    return adjusted_content


    def _adjust_punctuation(self, content: Dict[str, Any]) -> Dict[str, Any]:
    def _adjust_punctuation(self, content: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Adjust punctuation in content.
    Adjust punctuation in content.


    Args:
    Args:
    content: Content to adjust
    content: Content to adjust


    Returns:
    Returns:
    Adjusted content
    Adjusted content
    """
    """
    # Get target style
    # Get target style
    style_data = self.STYLE_CATEGORIES.get(self.target_style, {})
    style_data = self.STYLE_CATEGORIES.get(self.target_style, {})
    target_punctuation = style_data.get("punctuation", "")
    target_punctuation = style_data.get("punctuation", "")


    # If no target punctuation, return content
    # If no target punctuation, return content
    if not target_punctuation:
    if not target_punctuation:
    return content
    return content


    # Create a copy of the content
    # Create a copy of the content
    adjusted_content = content.copy()
    adjusted_content = content.copy()


    # Extract text from content
    # Extract text from content
    text = self._extract_text_from_content()
    text = self._extract_text_from_content()


    # Get sentences
    # Get sentences
    sentences = self._get_sentences(text)
    sentences = self._get_sentences(text)


    # Initialize adjustments
    # Initialize adjustments
    adjustments = []
    adjustments = []


    # Process each sentence
    # Process each sentence
    for sentence in sentences:
    for sentence in sentences:
    # Count punctuation
    # Count punctuation
    exclamation_count = sentence.count("!")
    exclamation_count = sentence.count("!")
    question_count = sentence.count("?")
    question_count = sentence.count("?")
    ellipsis_count = sentence.count("...")
    ellipsis_count = sentence.count("...")
    sentence.count(";")
    sentence.count(";")
    dash_count = sentence.count("-") + sentence.count("—")
    dash_count = sentence.count("-") + sentence.count("—")


    # Check if adjustment needed
    # Check if adjustment needed
    if "emphatic" in target_punctuation:
    if "emphatic" in target_punctuation:
    # Add more emphatic punctuation
    # Add more emphatic punctuation
    if (
    if (
    not any(
    not any(
    [exclamation_count, question_count, ellipsis_count, dash_count]
    [exclamation_count, question_count, ellipsis_count, dash_count]
    )
    )
    and len(sentence) > 20
    and len(sentence) > 20
    ):
    ):
    # Replace period with exclamation point or add emphasis
    # Replace period with exclamation point or add emphasis
    if sentence.endswith("."):
    if sentence.endswith("."):
    adjusted_sentence = sentence[:-1] + "!"
    adjusted_sentence = sentence[:-1] + "!"
    else:
    else:
    adjusted_sentence = sentence + "!"
    adjusted_sentence = sentence + "!"


    # Create adjustment
    # Create adjustment
    adjustment = {
    adjustment = {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "punctuation",
    "type": "punctuation",
    "original": sentence,
    "original": sentence,
    "replacement": adjusted_sentence,
    "replacement": adjusted_sentence,
    "target_punctuation": "emphatic",
    "target_punctuation": "emphatic",
    "confidence": 0.6,
    "confidence": 0.6,
    "impact": "low",
    "impact": "low",
    }
    }


    # Add adjustment
    # Add adjustment
    adjustments.append(adjustment)
    adjustments.append(adjustment)


    # Replace in content
    # Replace in content
    for key in adjusted_content:
    for key in adjusted_content:
    if isinstance(adjusted_content[key], str):
    if isinstance(adjusted_content[key], str):
    adjusted_content[key] = adjusted_content[key].replace(
    adjusted_content[key] = adjusted_content[key].replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )
    elif isinstance(adjusted_content[key], list):
    elif isinstance(adjusted_content[key], list):
    for i, item in enumerate(adjusted_content[key]):
    for i, item in enumerate(adjusted_content[key]):
    if isinstance(item, str):
    if isinstance(item, str):
    adjusted_content[key][i] = item.replace(
    adjusted_content[key][i] = item.replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )
    elif isinstance(item, dict):
    elif isinstance(item, dict):
    for subkey in item:
    for subkey in item:
    if isinstance(item[subkey], str):
    if isinstance(item[subkey], str):
    item[subkey] = item[subkey].replace(
    item[subkey] = item[subkey].replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )


    elif "standard" in target_punctuation:
    elif "standard" in target_punctuation:
    # Normalize punctuation
    # Normalize punctuation
    if exclamation_count > 0 or question_count > 0 or ellipsis_count > 0:
    if exclamation_count > 0 or question_count > 0 or ellipsis_count > 0:
    # Replace excessive punctuation
    # Replace excessive punctuation
    adjusted_sentence = re.sub(r"!+", ".", sentence)
    adjusted_sentence = re.sub(r"!+", ".", sentence)
    adjusted_sentence = re.sub(r"\?+", "?", adjusted_sentence)
    adjusted_sentence = re.sub(r"\?+", "?", adjusted_sentence)
    adjusted_sentence = re.sub(r"\.{3,}", ".", adjusted_sentence)
    adjusted_sentence = re.sub(r"\.{3,}", ".", adjusted_sentence)


    # Create adjustment
    # Create adjustment
    adjustment = {
    adjustment = {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "punctuation",
    "type": "punctuation",
    "original": sentence,
    "original": sentence,
    "replacement": adjusted_sentence,
    "replacement": adjusted_sentence,
    "target_punctuation": "standard",
    "target_punctuation": "standard",
    "confidence": 0.7,
    "confidence": 0.7,
    "impact": "low",
    "impact": "low",
    }
    }


    # Add adjustment
    # Add adjustment
    adjustments.append(adjustment)
    adjustments.append(adjustment)


    # Replace in content
    # Replace in content
    for key in adjusted_content:
    for key in adjusted_content:
    if isinstance(adjusted_content[key], str):
    if isinstance(adjusted_content[key], str):
    adjusted_content[key] = adjusted_content[key].replace(
    adjusted_content[key] = adjusted_content[key].replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )
    elif isinstance(adjusted_content[key], list):
    elif isinstance(adjusted_content[key], list):
    for i, item in enumerate(adjusted_content[key]):
    for i, item in enumerate(adjusted_content[key]):
    if isinstance(item, str):
    if isinstance(item, str):
    adjusted_content[key][i] = item.replace(
    adjusted_content[key][i] = item.replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )
    elif isinstance(item, dict):
    elif isinstance(item, dict):
    for subkey in item:
    for subkey in item:
    if isinstance(item[subkey], str):
    if isinstance(item[subkey], str):
    item[subkey] = item[subkey].replace(
    item[subkey] = item[subkey].replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )


    elif "relaxed" in target_punctuation:
    elif "relaxed" in target_punctuation:
    # Add more casual punctuation
    # Add more casual punctuation
    if (
    if (
    not any([exclamation_count, question_count, ellipsis_count])
    not any([exclamation_count, question_count, ellipsis_count])
    and len(sentence) > 20
    and len(sentence) > 20
    ):
    ):
    # Add ellipsis or exclamation
    # Add ellipsis or exclamation
    if random.random() < 0.5:
    if random.random() < 0.5:
    adjusted_sentence = sentence[:-1] + "..."
    adjusted_sentence = sentence[:-1] + "..."
    else:
    else:
    adjusted_sentence = sentence[:-1] + "!"
    adjusted_sentence = sentence[:-1] + "!"


    # Create adjustment
    # Create adjustment
    adjustment = {
    adjustment = {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "punctuation",
    "type": "punctuation",
    "original": sentence,
    "original": sentence,
    "replacement": adjusted_sentence,
    "replacement": adjusted_sentence,
    "target_punctuation": "relaxed",
    "target_punctuation": "relaxed",
    "confidence": 0.6,
    "confidence": 0.6,
    "impact": "low",
    "impact": "low",
    }
    }


    # Add adjustment
    # Add adjustment
    adjustments.append(adjustment)
    adjustments.append(adjustment)


    # Replace in content
    # Replace in content
    for key in adjusted_content:
    for key in adjusted_content:
    if isinstance(adjusted_content[key], str):
    if isinstance(adjusted_content[key], str):
    adjusted_content[key] = adjusted_content[key].replace(
    adjusted_content[key] = adjusted_content[key].replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )
    elif isinstance(adjusted_content[key], list):
    elif isinstance(adjusted_content[key], list):
    for i, item in enumerate(adjusted_content[key]):
    for i, item in enumerate(adjusted_content[key]):
    if isinstance(item, str):
    if isinstance(item, str):
    adjusted_content[key][i] = item.replace(
    adjusted_content[key][i] = item.replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )
    elif isinstance(item, dict):
    elif isinstance(item, dict):
    for subkey in item:
    for subkey in item:
    if isinstance(item[subkey], str):
    if isinstance(item[subkey], str):
    item[subkey] = item[subkey].replace(
    item[subkey] = item[subkey].replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )


    # Store adjustments
    # Store adjustments
    self.results["adjustments"]["punctuation"] = adjustments
    self.results["adjustments"]["punctuation"] = adjustments


    return adjusted_content
    return adjusted_content


    def _adjust_voice(self, content: Dict[str, Any]) -> Dict[str, Any]:
    def _adjust_voice(self, content: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Adjust voice in content.
    Adjust voice in content.


    Args:
    Args:
    content: Content to adjust
    content: Content to adjust


    Returns:
    Returns:
    Adjusted content
    Adjusted content
    """
    """
    # Get target style
    # Get target style
    style_data = self.STYLE_CATEGORIES.get(self.target_style, {})
    style_data = self.STYLE_CATEGORIES.get(self.target_style, {})
    target_voice = style_data.get("voice", "")
    target_voice = style_data.get("voice", "")


    # If no target voice, return content
    # If no target voice, return content
    if not target_voice:
    if not target_voice:
    return content
    return content


    # Create a copy of the content
    # Create a copy of the content
    adjusted_content = content.copy()
    adjusted_content = content.copy()


    # Extract text from content
    # Extract text from content
    text = self._extract_text_from_content()
    text = self._extract_text_from_content()


    # Get sentences
    # Get sentences
    sentences = self._get_sentences(text)
    sentences = self._get_sentences(text)


    # Initialize adjustments
    # Initialize adjustments
    adjustments = []
    adjustments = []


    # Process each sentence
    # Process each sentence
    for sentence in sentences:
    for sentence in sentences:
    # Check if sentence is in passive voice
    # Check if sentence is in passive voice
    is_passive = self._is_passive_voice(sentence)
    is_passive = self._is_passive_voice(sentence)


    # Check if adjustment needed
    # Check if adjustment needed
    if "active" in target_voice and is_passive:
    if "active" in target_voice and is_passive:
    # Convert to active voice
    # Convert to active voice
    adjusted_sentence = self._convert_to_active_voice(sentence)
    adjusted_sentence = self._convert_to_active_voice(sentence)


    # Only adjust if the sentence actually changed
    # Only adjust if the sentence actually changed
    if adjusted_sentence != sentence:
    if adjusted_sentence != sentence:
    # Create adjustment
    # Create adjustment
    adjustment = {
    adjustment = {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "voice",
    "type": "voice",
    "original": sentence,
    "original": sentence,
    "replacement": adjusted_sentence,
    "replacement": adjusted_sentence,
    "original_voice": "passive",
    "original_voice": "passive",
    "target_voice": "active",
    "target_voice": "active",
    "confidence": 0.7,
    "confidence": 0.7,
    "impact": "medium",
    "impact": "medium",
    }
    }


    # Add adjustment
    # Add adjustment
    adjustments.append(adjustment)
    adjustments.append(adjustment)


    # Replace in content
    # Replace in content
    for key in adjusted_content:
    for key in adjusted_content:
    if isinstance(adjusted_content[key], str):
    if isinstance(adjusted_content[key], str):
    adjusted_content[key] = adjusted_content[key].replace(
    adjusted_content[key] = adjusted_content[key].replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )
    elif isinstance(adjusted_content[key], list):
    elif isinstance(adjusted_content[key], list):
    for i, item in enumerate(adjusted_content[key]):
    for i, item in enumerate(adjusted_content[key]):
    if isinstance(item, str):
    if isinstance(item, str):
    adjusted_content[key][i] = item.replace(
    adjusted_content[key][i] = item.replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )
    elif isinstance(item, dict):
    elif isinstance(item, dict):
    for subkey in item:
    for subkey in item:
    if isinstance(item[subkey], str):
    if isinstance(item[subkey], str):
    item[subkey] = item[subkey].replace(
    item[subkey] = item[subkey].replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )


    elif "passive" in target_voice and not is_passive:
    elif "passive" in target_voice and not is_passive:
    # Convert to passive voice
    # Convert to passive voice
    adjusted_sentence = self._convert_to_passive_voice(sentence)
    adjusted_sentence = self._convert_to_passive_voice(sentence)


    # Only adjust if the sentence actually changed
    # Only adjust if the sentence actually changed
    if adjusted_sentence != sentence:
    if adjusted_sentence != sentence:
    # Create adjustment
    # Create adjustment
    adjustment = {
    adjustment = {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "voice",
    "type": "voice",
    "original": sentence,
    "original": sentence,
    "replacement": adjusted_sentence,
    "replacement": adjusted_sentence,
    "original_voice": "active",
    "original_voice": "active",
    "target_voice": "passive",
    "target_voice": "passive",
    "confidence": 0.6,
    "confidence": 0.6,
    "impact": "medium",
    "impact": "medium",
    }
    }


    # Add adjustment
    # Add adjustment
    adjustments.append(adjustment)
    adjustments.append(adjustment)


    # Replace in content
    # Replace in content
    for key in adjusted_content:
    for key in adjusted_content:
    if isinstance(adjusted_content[key], str):
    if isinstance(adjusted_content[key], str):
    adjusted_content[key] = adjusted_content[key].replace(
    adjusted_content[key] = adjusted_content[key].replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )
    elif isinstance(adjusted_content[key], list):
    elif isinstance(adjusted_content[key], list):
    for i, item in enumerate(adjusted_content[key]):
    for i, item in enumerate(adjusted_content[key]):
    if isinstance(item, str):
    if isinstance(item, str):
    adjusted_content[key][i] = item.replace(
    adjusted_content[key][i] = item.replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )
    elif isinstance(item, dict):
    elif isinstance(item, dict):
    for subkey in item:
    for subkey in item:
    if isinstance(item[subkey], str):
    if isinstance(item[subkey], str):
    item[subkey] = item[subkey].replace(
    item[subkey] = item[subkey].replace(
    sentence, adjusted_sentence
    sentence, adjusted_sentence
    )
    )


    # Store adjustments
    # Store adjustments
    self.results["adjustments"]["voice"] = adjustments
    self.results["adjustments"]["voice"] = adjustments


    return adjusted_content
    return adjusted_content


    def get_suggestions(self) -> List[Dict[str, Any]]:
    def get_suggestions(self) -> List[Dict[str, Any]]:
    """
    """
    Get suggestions for style adjustments.
    Get suggestions for style adjustments.


    Returns:
    Returns:
    List of suggestion dictionaries
    List of suggestion dictionaries
    """
    """
    # Analyze content if not already analyzed
    # Analyze content if not already analyzed
    if self.results is None:
    if self.results is None:
    self.analyze()
    self.analyze()


    # Get all adjustments
    # Get all adjustments
    all_adjustments = []
    all_adjustments = []


    for adjustment_type, adjustments in self.results["adjustments"].items():
    for adjustment_type, adjustments in self.results["adjustments"].items():
    all_adjustments.extend(adjustments)
    all_adjustments.extend(adjustments)


    # Sort adjustments by priority
    # Sort adjustments by priority
    prioritized_adjustments = self._prioritize_adjustments(all_adjustments)
    prioritized_adjustments = self._prioritize_adjustments(all_adjustments)


    # Limit to max suggestions
    # Limit to max suggestions
    max_suggestions = self.config["max_suggestions"]
    max_suggestions = self.config["max_suggestions"]
    limited_adjustments = prioritized_adjustments[:max_suggestions]
    limited_adjustments = prioritized_adjustments[:max_suggestions]


    # Convert adjustments to suggestions
    # Convert adjustments to suggestions
    suggestions = []
    suggestions = []


    for adjustment in limited_adjustments:
    for adjustment in limited_adjustments:
    suggestion = self._adjustment_to_suggestion(adjustment)
    suggestion = self._adjustment_to_suggestion(adjustment)
    suggestions.append(suggestion)
    suggestions.append(suggestion)


    return suggestions
    return suggestions


    def _prioritize_adjustments(
    def _prioritize_adjustments(
    self, adjustments: List[Dict[str, Any]]
    self, adjustments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Prioritize adjustments.
    Prioritize adjustments.


    Args:
    Args:
    adjustments: List of adjustments
    adjustments: List of adjustments


    Returns:
    Returns:
    Prioritized list of adjustments
    Prioritized list of adjustments
    """
    """
    # Get prioritization method
    # Get prioritization method
    prioritize_by = self.config["prioritize_by"]
    prioritize_by = self.config["prioritize_by"]


    if prioritize_by == "impact":
    if prioritize_by == "impact":
    # Sort by impact (high, medium, low)
    # Sort by impact (high, medium, low)
    impact_order = {"high": 0, "medium": 1, "low": 2}
    impact_order = {"high": 0, "medium": 1, "low": 2}
    return sorted(
    return sorted(
    adjustments,
    adjustments,
    key=lambda x: (
    key=lambda x: (
    impact_order.get(x["impact"], 3),
    impact_order.get(x["impact"], 3),
    -x.get("confidence", 0),
    -x.get("confidence", 0),
    ),
    ),
    )
    )


    elif prioritize_by == "confidence":
    elif prioritize_by == "confidence":
    # Sort by confidence (highest first)
    # Sort by confidence (highest first)
    return sorted(adjustments, key=lambda x: -x.get("confidence", 0))
    return sorted(adjustments, key=lambda x: -x.get("confidence", 0))


    elif prioritize_by == "position":
    elif prioritize_by == "position":
    # Sort by position in text (earliest first)
    # Sort by position in text (earliest first)
    # This requires position information, which we don't always have
    # This requires position information, which we don't always have
    # Fall back to impact if position is not available
    # Fall back to impact if position is not available
    if all("position" in adjustment for adjustment in adjustments):
    if all("position" in adjustment for adjustment in adjustments):
    return sorted(
    return sorted(
    adjustments,
    adjustments,
    key=lambda x: x["position"][0] if "position" in x else float("inf"),
    key=lambda x: x["position"][0] if "position" in x else float("inf"),
    )
    )
    else:
    else:
    impact_order = {"high": 0, "medium": 1, "low": 2}
    impact_order = {"high": 0, "medium": 1, "low": 2}
    return sorted(
    return sorted(
    adjustments,
    adjustments,
    key=lambda x: (
    key=lambda x: (
    impact_order.get(x["impact"], 3),
    impact_order.get(x["impact"], 3),
    -x.get("confidence", 0),
    -x.get("confidence", 0),
    ),
    ),
    )
    )


    # Default to impact
    # Default to impact
    impact_order = {"high": 0, "medium": 1, "low": 2}
    impact_order = {"high": 0, "medium": 1, "low": 2}
    return sorted(
    return sorted(
    adjustments,
    adjustments,
    key=lambda x: (impact_order.get(x["impact"], 3), -x.get("confidence", 0)),
    key=lambda x: (impact_order.get(x["impact"], 3), -x.get("confidence", 0)),
    )
    )


    def _adjustment_to_suggestion(self, adjustment: Dict[str, Any]) -> Dict[str, Any]:
    def _adjustment_to_suggestion(self, adjustment: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Convert an adjustment to a suggestion.
    Convert an adjustment to a suggestion.


    Args:
    Args:
    adjustment: Adjustment dictionary
    adjustment: Adjustment dictionary


    Returns:
    Returns:
    Suggestion dictionary
    Suggestion dictionary
    """
    """
    # Create base suggestion
    # Create base suggestion
    suggestion = {
    suggestion = {
    "id": adjustment["id"],
    "id": adjustment["id"],
    "type": adjustment["type"],
    "type": adjustment["type"],
    "original": adjustment["original"],
    "original": adjustment["original"],
    "replacement": adjustment["replacement"],
    "replacement": adjustment["replacement"],
    "confidence": adjustment.get("confidence", 0.0),
    "confidence": adjustment.get("confidence", 0.0),
    "impact": adjustment.get("impact", "low"),
    "impact": adjustment.get("impact", "low"),
    }
    }


    # Add type-specific fields
    # Add type-specific fields
    if adjustment["type"] == "word_choice":
    if adjustment["type"] == "word_choice":
    suggestion["message"] = (
    suggestion["message"] = (
    f"Replace '{adjustment['original']}' with '{adjustment['replacement']}' for a more {self.target_style} style."
    f"Replace '{adjustment['original']}' with '{adjustment['replacement']}' for a more {self.target_style} style."
    )
    )
    suggestion["explanation"] = (
    suggestion["explanation"] = (
    f"The word '{adjustment['original']}' is not typical of {self.target_style} writing. '{adjustment['replacement']}' is a better choice for this style."
    f"The word '{adjustment['original']}' is not typical of {self.target_style} writing. '{adjustment['replacement']}' is a better choice for this style."
    )
    )


    elif adjustment["type"] == "sentence_structure":
    elif adjustment["type"] == "sentence_structure":
    if "simple" in adjustment.get("target_structure", ""):
    if "simple" in adjustment.get("target_structure", ""):
    suggestion["message"] = (
    suggestion["message"] = (
    "Simplify this sentence for a more direct style."
    "Simplify this sentence for a more direct style."
    )
    )
    suggestion["explanation"] = (
    suggestion["explanation"] = (
    "This sentence is too complex for the target style. Breaking it into shorter, simpler sentences will improve readability and match the desired style better."
    "This sentence is too complex for the target style. Breaking it into shorter, simpler sentences will improve readability and match the desired style better."
    )
    )
    else:
    else:
    suggestion["message"] = (
    suggestion["message"] = (
    "Make this sentence more complex for a more sophisticated style."
    "Make this sentence more complex for a more sophisticated style."
    )
    )
    suggestion["explanation"] = (
    suggestion["explanation"] = (
    "This sentence is too simple for the target style. Adding more complexity will make it match the desired style better."
    "This sentence is too simple for the target style. Adding more complexity will make it match the desired style better."
    )
    )


    elif adjustment["type"] == "paragraph_structure":
    elif adjustment["type"] == "paragraph_structure":
    if adjustment.get("target_length", "") == "short":
    if adjustment.get("target_length", "") == "short":
    suggestion["message"] = "Break this paragraph into smaller ones."
    suggestion["message"] = "Break this paragraph into smaller ones."
    suggestion["explanation"] = (
    suggestion["explanation"] = (
    "This paragraph is too long for the target style. Shorter paragraphs improve readability and match the desired style better."
    "This paragraph is too long for the target style. Shorter paragraphs improve readability and match the desired style better."
    )
    )
    else:
    else:
    suggestion["message"] = "Combine this paragraph with the next one."
    suggestion["message"] = "Combine this paragraph with the next one."
    suggestion["explanation"] = (
    suggestion["explanation"] = (
    "This paragraph is too short for the target style. Combining it with another paragraph will make it match the desired style better."
    "This paragraph is too short for the target style. Combining it with another paragraph will make it match the desired style better."
    )
    )


    elif adjustment["type"] == "punctuation":
    elif adjustment["type"] == "punctuation":
    if adjustment.get("target_punctuation", "") == "emphatic":
    if adjustment.get("target_punctuation", "") == "emphatic":
    suggestion["message"] = "Use more emphatic punctuation."
    suggestion["message"] = "Use more emphatic punctuation."
    suggestion["explanation"] = (
    suggestion["explanation"] = (
    "The target style uses more emphatic punctuation to engage readers. Adding exclamation points or other emphatic punctuation will make the content more engaging."
    "The target style uses more emphatic punctuation to engage readers. Adding exclamation points or other emphatic punctuation will make the content more engaging."
    )
    )
    elif adjustment.get("target_punctuation", "") == "standard":
    elif adjustment.get("target_punctuation", "") == "standard":
    suggestion["message"] = "Use more standard punctuation."
    suggestion["message"] = "Use more standard punctuation."
    suggestion["explanation"] = (
    suggestion["explanation"] = (
    "The target style uses more standard punctuation. Normalizing punctuation will make the content more professional and match the desired style better."
    "The target style uses more standard punctuation. Normalizing punctuation will make the content more professional and match the desired style better."
    )
    )
    else:
    else:
    suggestion["message"] = "Use more relaxed punctuation."
    suggestion["message"] = "Use more relaxed punctuation."
    suggestion["explanation"] = (
    suggestion["explanation"] = (
    "The target style uses more relaxed punctuation. Adding ellipses or other casual punctuation will make the content more conversational."
    "The target style uses more relaxed punctuation. Adding ellipses or other casual punctuation will make the content more conversational."
    )
    )


    elif adjustment["type"] == "voice":
    elif adjustment["type"] == "voice":
    if adjustment.get("target_voice", "") == "active":
    if adjustment.get("target_voice", "") == "active":
    suggestion["message"] = "Convert this sentence to active voice."
    suggestion["message"] = "Convert this sentence to active voice."
    suggestion["explanation"] = (
    suggestion["explanation"] = (
    "The target style prefers active voice. Converting passive voice to active voice will make the content more direct and engaging."
    "The target style prefers active voice. Converting passive voice to active voice will make the content more direct and engaging."
    )
    )
    else:
    else:
    suggestion["message"] = "Convert this sentence to passive voice."
    suggestion["message"] = "Convert this sentence to passive voice."
    suggestion["explanation"] = (
    suggestion["explanation"] = (
    "The target style allows or prefers passive voice in some contexts. Converting active voice to passive voice can make the content more formal or objective."
    "The target style allows or prefers passive voice in some contexts. Converting active voice to passive voice can make the content more formal or objective."
    )
    )


    # Add examples
    # Add examples
    suggestion["examples"] = [
    suggestion["examples"] = [
    {
    {
    "original": adjustment["original"],
    "original": adjustment["original"],
    "replacement": adjustment["replacement"],
    "replacement": adjustment["replacement"],
    }
    }
    ]
    ]


    return suggestion
    return suggestion


    def apply_suggestion(self, suggestion_id: str) -> Dict[str, Any]:
    def apply_suggestion(self, suggestion_id: str) -> Dict[str, Any]:
    """
    """
    Apply a specific suggestion to the content.
    Apply a specific suggestion to the content.


    Args:
    Args:
    suggestion_id: ID of the suggestion to apply
    suggestion_id: ID of the suggestion to apply


    Returns:
    Returns:
    Updated content
    Updated content
    """
    """
    # Find the suggestion
    # Find the suggestion
    suggestion = None
    suggestion = None


    for adjustment_type, adjustments in self.results["adjustments"].items():
    for adjustment_type, adjustments in self.results["adjustments"].items():
    for adjustment in adjustments:
    for adjustment in adjustments:
    if adjustment["id"] == suggestion_id:
    if adjustment["id"] == suggestion_id:
    suggestion = adjustment
    suggestion = adjustment
    break
    break


    if suggestion:
    if suggestion:
    break
    break


    if not suggestion:
    if not suggestion:
    raise ValueError(f"Suggestion with ID {suggestion_id} not found")
    raise ValueError(f"Suggestion with ID {suggestion_id} not found")


    # Create a copy of the content
    # Create a copy of the content
    adjusted_content = self.content.copy()
    adjusted_content = self.content.copy()


    # Apply the suggestion
    # Apply the suggestion
    for key in adjusted_content:
    for key in adjusted_content:
    if isinstance(adjusted_content[key], str):
    if isinstance(adjusted_content[key], str):
    adjusted_content[key] = adjusted_content[key].replace(
    adjusted_content[key] = adjusted_content[key].replace(
    suggestion["original"], suggestion["replacement"]
    suggestion["original"], suggestion["replacement"]
    )
    )
    elif isinstance(adjusted_content[key], list):
    elif isinstance(adjusted_content[key], list):
    for i, item in enumerate(adjusted_content[key]):
    for i, item in enumerate(adjusted_content[key]):
    if isinstance(item, str):
    if isinstance(item, str):
    adjusted_content[key][i] = item.replace(
    adjusted_content[key][i] = item.replace(
    suggestion["original"], suggestion["replacement"]
    suggestion["original"], suggestion["replacement"]
    )
    )
    elif isinstance(item, dict):
    elif isinstance(item, dict):
    for subkey in item:
    for subkey in item:
    if isinstance(item[subkey], str):
    if isinstance(item[subkey], str):
    item[subkey] = item[subkey].replace(
    item[subkey] = item[subkey].replace(
    suggestion["original"], suggestion["replacement"]
    suggestion["original"], suggestion["replacement"]
    )
    )


    # Update content
    # Update content
    self.content = adjusted_content
    self.content = adjusted_content


    # Re-analyze
    # Re-analyze
    self.analyze()
    self.analyze()


    return self.content
    return self.content


    def apply_all_suggestions(self) -> Dict[str, Any]:
    def apply_all_suggestions(self) -> Dict[str, Any]:
    """
    """
    Apply all suggestions to the content.
    Apply all suggestions to the content.


    Returns:
    Returns:
    Updated content
    Updated content
    """
    """
    # Get all suggestions
    # Get all suggestions
    suggestions = self.get_suggestions()
    suggestions = self.get_suggestions()


    # Apply each suggestion
    # Apply each suggestion
    for suggestion in suggestions:
    for suggestion in suggestions:
    self.apply_suggestion(suggestion["id"])
    self.apply_suggestion(suggestion["id"])


    return self.content
    return self.content


    def get_style_report(self) -> Dict[str, Any]:
    def get_style_report(self) -> Dict[str, Any]:
    """
    """
    Get a report on the style of the content.
    Get a report on the style of the content.


    Returns:
    Returns:
    Style report dictionary
    Style report dictionary
    """
    """
    # Analyze content if not already analyzed
    # Analyze content if not already analyzed
    if self.results is None:
    if self.results is None:
    self.analyze()
    self.analyze()


    # Get analysis results
    # Get analysis results
    analysis = self.results["analysis"]
    analysis = self.results["analysis"]


    # Create report
    # Create report
    report = {
    report = {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "timestamp": datetime.datetime.now().isoformat(),
    "timestamp": datetime.datetime.now().isoformat(),
    "content_id": self.content.get("id", "unknown"),
    "content_id": self.content.get("id", "unknown"),
    "target_style": self.target_style,
    "target_style": self.target_style,
    "current_style": analysis["tone_analysis"]["dominant_tone"],
    "current_style": analysis["tone_analysis"]["dominant_tone"],
    "style_match": analysis["tone_analysis"]["target_tone"]
    "style_match": analysis["tone_analysis"]["target_tone"]
    == analysis["tone_analysis"]["dominant_tone"],
    == analysis["tone_analysis"]["dominant_tone"],
    "style_consistency": analysis["tone_analysis"]["consistency"],
    "style_consistency": analysis["tone_analysis"]["consistency"],
    "sentiment": analysis["sentiment_analysis"]["dominant_sentiment"],
    "sentiment": analysis["sentiment_analysis"]["dominant_sentiment"],
    "sentiment_consistency": analysis["sentiment_analysis"]["consistency"],
    "sentiment_consistency": analysis["sentiment_analysis"]["consistency"],
    "readability": {
    "readability": {
    "grade_level": analysis.get("readability_scores", {}).get(
    "grade_level": analysis.get("readability_scores", {}).get(
    "grade_level", 0
    "grade_level", 0
    ),
    ),
    "reading_ease": analysis.get("readability_scores", {})
    "reading_ease": analysis.get("readability_scores", {})
    .get("flesch_reading_ease", {})
    .get("flesch_reading_ease", {})
    .get("score", 0),
    .get("score", 0),
    },
    },
    "style_elements": {
    "style_elements": {
    "word_choice": self._get_word_choice_report(),
    "word_choice": self._get_word_choice_report(),
    "sentence_structure": self._get_sentence_structure_report(),
    "sentence_structure": self._get_sentence_structure_report(),
    "paragraph_structure": self._get_paragraph_structure_report(),
    "paragraph_structure": self._get_paragraph_structure_report(),
    "punctuation": self._get_punctuation_report(),
    "punctuation": self._get_punctuation_report(),
    "voice": self._get_voice_report(),
    "voice": self._get_voice_report(),
    },
    },
    "suggestions_count": len(self.get_suggestions()),
    "suggestions_count": len(self.get_suggestions()),
    "improvement_potential": self._get_improvement_potential(),
    "improvement_potential": self._get_improvement_potential(),
    }
    }


    return report
    return report


    def _get_word_choice_report(self) -> Dict[str, Any]:
    def _get_word_choice_report(self) -> Dict[str, Any]:
    """
    """
    Get a report on word choice.
    Get a report on word choice.


    Returns:
    Returns:
    Word choice report dictionary
    Word choice report dictionary
    """
    """
    # Get word choice adjustments
    # Get word choice adjustments
    adjustments = self.results["adjustments"]["word_choice"]
    adjustments = self.results["adjustments"]["word_choice"]


    # Count adjustments
    # Count adjustments
    count = len(adjustments)
    count = len(adjustments)


    # Calculate impact
    # Calculate impact
    impact = sum(1 for adj in adjustments if adj["impact"] == "high") * 3
    impact = sum(1 for adj in adjustments if adj["impact"] == "high") * 3
    impact += sum(1 for adj in adjustments if adj["impact"] == "medium") * 2
    impact += sum(1 for adj in adjustments if adj["impact"] == "medium") * 2
    impact += sum(1 for adj in adjustments if adj["impact"] == "low")
    impact += sum(1 for adj in adjustments if adj["impact"] == "low")


    # Normalize impact
    # Normalize impact
    if count > 0:
    if count > 0:
    impact = impact / (count * 3)
    impact = impact / (count * 3)
    else:
    else:
    impact = 0
    impact = 0


    return {
    return {
    "count": count,
    "count": count,
    "impact": impact,
    "impact": impact,
    "examples": [adj["original"] for adj in adjustments[:3]],
    "examples": [adj["original"] for adj in adjustments[:3]],
    }
    }


    def _get_sentence_structure_report(self) -> Dict[str, Any]:
    def _get_sentence_structure_report(self) -> Dict[str, Any]:
    """
    """
    Get a report on sentence structure.
    Get a report on sentence structure.


    Returns:
    Returns:
    Sentence structure report dictionary
    Sentence structure report dictionary
    """
    """
    # Get sentence structure adjustments
    # Get sentence structure adjustments
    adjustments = self.results["adjustments"]["sentence_structure"]
    adjustments = self.results["adjustments"]["sentence_structure"]


    # Count adjustments
    # Count adjustments
    count = len(adjustments)
    count = len(adjustments)


    # Calculate impact
    # Calculate impact
    impact = sum(1 for adj in adjustments if adj["impact"] == "high") * 3
    impact = sum(1 for adj in adjustments if adj["impact"] == "high") * 3
    impact += sum(1 for adj in adjustments if adj["impact"] == "medium") * 2
    impact += sum(1 for adj in adjustments if adj["impact"] == "medium") * 2
    impact += sum(1 for adj in adjustments if adj["impact"] == "low")
    impact += sum(1 for adj in adjustments if adj["impact"] == "low")


    # Normalize impact
    # Normalize impact
    if count > 0:
    if count > 0:
    impact = impact / (count * 3)
    impact = impact / (count * 3)
    else:
    else:
    impact = 0
    impact = 0


    return {
    return {
    "count": count,
    "count": count,
    "impact": impact,
    "impact": impact,
    "examples": [adj["original"] for adj in adjustments[:3]],
    "examples": [adj["original"] for adj in adjustments[:3]],
    }
    }


    def _get_paragraph_structure_report(self) -> Dict[str, Any]:
    def _get_paragraph_structure_report(self) -> Dict[str, Any]:
    """
    """
    Get a report on paragraph structure.
    Get a report on paragraph structure.


    Returns:
    Returns:
    Paragraph structure report dictionary
    Paragraph structure report dictionary
    """
    """
    # Get paragraph structure adjustments
    # Get paragraph structure adjustments
    adjustments = self.results["adjustments"]["paragraph_structure"]
    adjustments = self.results["adjustments"]["paragraph_structure"]


    # Count adjustments
    # Count adjustments
    count = len(adjustments)
    count = len(adjustments)


    # Calculate impact
    # Calculate impact
    impact = sum(1 for adj in adjustments if adj["impact"] == "high") * 3
    impact = sum(1 for adj in adjustments if adj["impact"] == "high") * 3
    impact += sum(1 for adj in adjustments if adj["impact"] == "medium") * 2
    impact += sum(1 for adj in adjustments if adj["impact"] == "medium") * 2
    impact += sum(1 for adj in adjustments if adj["impact"] == "low")
    impact += sum(1 for adj in adjustments if adj["impact"] == "low")


    # Normalize impact
    # Normalize impact
    if count > 0:
    if count > 0:
    impact = impact / (count * 3)
    impact = impact / (count * 3)
    else:
    else:
    impact = 0
    impact = 0


    return {
    return {
    "count": count,
    "count": count,
    "impact": impact,
    "impact": impact,
    "examples": [adj["original"][:100] + "..." for adj in adjustments[:3]],
    "examples": [adj["original"][:100] + "..." for adj in adjustments[:3]],
    }
    }


    def _get_punctuation_report(self) -> Dict[str, Any]:
    def _get_punctuation_report(self) -> Dict[str, Any]:
    """
    """
    Get a report on punctuation.
    Get a report on punctuation.


    Returns:
    Returns:
    Punctuation report dictionary
    Punctuation report dictionary
    """
    """
    # Get punctuation adjustments
    # Get punctuation adjustments
    adjustments = self.results["adjustments"]["punctuation"]
    adjustments = self.results["adjustments"]["punctuation"]


    # Count adjustments
    # Count adjustments
    count = len(adjustments)
    count = len(adjustments)


    # Calculate impact
    # Calculate impact
    impact = sum(1 for adj in adjustments if adj["impact"] == "high") * 3
    impact = sum(1 for adj in adjustments if adj["impact"] == "high") * 3
    impact += sum(1 for adj in adjustments if adj["impact"] == "medium") * 2
    impact += sum(1 for adj in adjustments if adj["impact"] == "medium") * 2
    impact += sum(1 for adj in adjustments if adj["impact"] == "low")
    impact += sum(1 for adj in adjustments if adj["impact"] == "low")


    # Normalize impact
    # Normalize impact
    if count > 0:
    if count > 0:
    impact = impact / (count * 3)
    impact = impact / (count * 3)
    else:
    else:
    impact = 0
    impact = 0


    return {
    return {
    "count": count,
    "count": count,
    "impact": impact,
    "impact": impact,
    "examples": [adj["original"] for adj in adjustments[:3]],
    "examples": [adj["original"] for adj in adjustments[:3]],
    }
    }


    def _get_voice_report(self) -> Dict[str, Any]:
    def _get_voice_report(self) -> Dict[str, Any]:
    """
    """
    Get a report on voice.
    Get a report on voice.


    Returns:
    Returns:
    Voice report dictionary
    Voice report dictionary
    """
    """
    # Get voice adjustments
    # Get voice adjustments
    adjustments = self.results["adjustments"]["voice"]
    adjustments = self.results["adjustments"]["voice"]


    # Count adjustments
    # Count adjustments
    count = len(adjustments)
    count = len(adjustments)


    # Calculate impact
    # Calculate impact
    impact = sum(1 for adj in adjustments if adj["impact"] == "high") * 3
    impact = sum(1 for adj in adjustments if adj["impact"] == "high") * 3
    impact += sum(1 for adj in adjustments if adj["impact"] == "medium") * 2
    impact += sum(1 for adj in adjustments if adj["impact"] == "medium") * 2
    impact += sum(1 for adj in adjustments if adj["impact"] == "low")
    impact += sum(1 for adj in adjustments if adj["impact"] == "low")


    # Normalize impact
    # Normalize impact
    if count > 0:
    if count > 0:
    impact = impact / (count * 3)
    impact = impact / (count * 3)
    else:
    else:
    impact = 0
    impact = 0


    return {
    return {
    "count": count,
    "count": count,
    "impact": impact,
    "impact": impact,
    "examples": [adj["original"] for adj in adjustments[:3]],
    "examples": [adj["original"] for adj in adjustments[:3]],
    }
    }


    def _get_improvement_potential(self) -> float:
    def _get_improvement_potential(self) -> float:
    """
    """
    Calculate the potential for improvement.
    Calculate the potential for improvement.


    Returns:
    Returns:
    Improvement potential score (0-1)
    Improvement potential score (0-1)
    """
    """
    # Get all adjustments
    # Get all adjustments
    all_adjustments = []
    all_adjustments = []


    for adjustment_type, adjustments in self.results["adjustments"].items():
    for adjustment_type, adjustments in self.results["adjustments"].items():
    all_adjustments.extend(adjustments)
    all_adjustments.extend(adjustments)


    # Count adjustments by impact
    # Count adjustments by impact
    high_impact = sum(1 for adj in all_adjustments if adj["impact"] == "high")
    high_impact = sum(1 for adj in all_adjustments if adj["impact"] == "high")
    medium_impact = sum(1 for adj in all_adjustments if adj["impact"] == "medium")
    medium_impact = sum(1 for adj in all_adjustments if adj["impact"] == "medium")
    low_impact = sum(1 for adj in all_adjustments if adj["impact"] == "low")
    low_impact = sum(1 for adj in all_adjustments if adj["impact"] == "low")


    # Calculate weighted impact
    # Calculate weighted impact
    weighted_impact = (high_impact * 3) + (medium_impact * 2) + low_impact
    weighted_impact = (high_impact * 3) + (medium_impact * 2) + low_impact


    # Get text length
    # Get text length
    text = self._extract_text_from_content()
    text = self._extract_text_from_content()
    word_count = len(self._get_words(text))
    word_count = len(self._get_words(text))


    # Normalize by text length
    # Normalize by text length
    if word_count > 0:
    if word_count > 0:
    normalized_impact = weighted_impact / (word_count / 100)
    normalized_impact = weighted_impact / (word_count / 100)
    else:
    else:
    normalized_impact = 0
    normalized_impact = 0


    # Clamp to 0-1 range
    # Clamp to 0-1 range
    return min(1.0, normalized_impact / 10)
    return min(1.0, normalized_impact / 10)