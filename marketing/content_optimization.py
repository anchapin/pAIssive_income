"""
"""
Content optimization module for the pAIssive Income project.
Content optimization module for the pAIssive Income project.


This module provides classes for optimizing marketing content, including
This module provides classes for optimizing marketing content, including
SEO optimization, readability analysis, and tone/style adjustment.
SEO optimization, readability analysis, and tone/style adjustment.
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
import uuid
import uuid
from abc import ABC, abstractmethod
from abc import ABC, abstractmethod
from collections import Counter
from collections import Counter
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


# Standard library imports
# Standard library imports
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




    class SEOAnalyzer(ABC):
    class SEOAnalyzer(ABC):
    """
    """
    Abstract base class for SEO analyzers.
    Abstract base class for SEO analyzers.


    This class provides common functionality for all SEO analyzers,
    This class provides common functionality for all SEO analyzers,
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
    Initialize an SEO analyzer.
    Initialize an SEO analyzer.


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
    Analyze the content for SEO optimization.
    Analyze the content for SEO optimization.


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
    Get the overall SEO score for the content.
    Get the overall SEO score for the content.


    Returns:
    Returns:
    SEO score between 0 and 1
    SEO score between 0 and 1
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
    Get SEO recommendations for the content.
    Get SEO recommendations for the content.


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
    Get the default configuration for the SEO analyzer.
    Get the default configuration for the SEO analyzer.


    Returns:
    Returns:
    Default configuration dictionary
    Default configuration dictionary
    """
    """
    return {
    return {
    "min_keyword_density": 0.01,  # 1%
    "min_keyword_density": 0.01,  # 1%
    "max_keyword_density": 0.03,  # 3%
    "max_keyword_density": 0.03,  # 3%
    "min_word_count": 300,
    "min_word_count": 300,
    "optimal_word_count": 1500,
    "optimal_word_count": 1500,
    "min_title_length": 30,
    "min_title_length": 30,
    "max_title_length": 60,
    "max_title_length": 60,
    "min_meta_description_length": 120,
    "min_meta_description_length": 120,
    "max_meta_description_length": 160,
    "max_meta_description_length": 160,
    "min_heading_count": 3,
    "min_heading_count": 3,
    "min_internal_links": 2,
    "min_internal_links": 2,
    "min_external_links": 1,
    "min_external_links": 1,
    "max_paragraph_length": 300,  # characters
    "max_paragraph_length": 300,  # characters
    "check_image_alt_text": True,
    "check_image_alt_text": True,
    "check_keyword_in_title": True,
    "check_keyword_in_title": True,
    "check_keyword_in_headings": True,
    "check_keyword_in_headings": True,
    "check_keyword_in_first_paragraph": True,
    "check_keyword_in_first_paragraph": True,
    "check_keyword_in_url": True,
    "check_keyword_in_url": True,
    "check_keyword_in_meta_description": True,
    "check_keyword_in_meta_description": True,
    "timestamp": datetime.datetime.now().isoformat(),
    "timestamp": datetime.datetime.now().isoformat(),
    }
    }


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
    "min_keyword_density",
    "min_keyword_density",
    "max_keyword_density",
    "max_keyword_density",
    "min_word_count",
    "min_word_count",
    "optimal_word_count",
    "optimal_word_count",
    "min_title_length",
    "min_title_length",
    "max_title_length",
    "max_title_length",
    "min_meta_description_length",
    "min_meta_description_length",
    "max_meta_description_length",
    "max_meta_description_length",
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
    if "min_keyword_density" in self.config and not (
    if "min_keyword_density" in self.config and not (
    isinstance(self.config["min_keyword_density"], (int, float))
    isinstance(self.config["min_keyword_density"], (int, float))
    and 0 <= self.config["min_keyword_density"] <= 1
    and 0 <= self.config["min_keyword_density"] <= 1
    ):
    ):
    errors.append("min_keyword_density must be a number between 0 and 1")
    errors.append("min_keyword_density must be a number between 0 and 1")


    if "max_keyword_density" in self.config and not (
    if "max_keyword_density" in self.config and not (
    isinstance(self.config["max_keyword_density"], (int, float))
    isinstance(self.config["max_keyword_density"], (int, float))
    and 0 <= self.config["max_keyword_density"] <= 1
    and 0 <= self.config["max_keyword_density"] <= 1
    ):
    ):
    errors.append("max_keyword_density must be a number between 0 and 1")
    errors.append("max_keyword_density must be a number between 0 and 1")


    if "min_word_count" in self.config and not (
    if "min_word_count" in self.config and not (
    isinstance(self.config["min_word_count"], int)
    isinstance(self.config["min_word_count"], int)
    and self.config["min_word_count"] > 0
    and self.config["min_word_count"] > 0
    ):
    ):
    errors.append("min_word_count must be a positive integer")
    errors.append("min_word_count must be a positive integer")


    if "optimal_word_count" in self.config and not (
    if "optimal_word_count" in self.config and not (
    isinstance(self.config["optimal_word_count"], int)
    isinstance(self.config["optimal_word_count"], int)
    and self.config["optimal_word_count"] > 0
    and self.config["optimal_word_count"] > 0
    ):
    ):
    errors.append("optimal_word_count must be a positive integer")
    errors.append("optimal_word_count must be a positive integer")


    if "min_title_length" in self.config and not (
    if "min_title_length" in self.config and not (
    isinstance(self.config["min_title_length"], int)
    isinstance(self.config["min_title_length"], int)
    and self.config["min_title_length"] > 0
    and self.config["min_title_length"] > 0
    ):
    ):
    errors.append("min_title_length must be a positive integer")
    errors.append("min_title_length must be a positive integer")


    if "max_title_length" in self.config and not (
    if "max_title_length" in self.config and not (
    isinstance(self.config["max_title_length"], int)
    isinstance(self.config["max_title_length"], int)
    and self.config["max_title_length"] > 0
    and self.config["max_title_length"] > 0
    ):
    ):
    errors.append("max_title_length must be a positive integer")
    errors.append("max_title_length must be a positive integer")


    if "min_meta_description_length" in self.config and not (
    if "min_meta_description_length" in self.config and not (
    isinstance(self.config["min_meta_description_length"], int)
    isinstance(self.config["min_meta_description_length"], int)
    and self.config["min_meta_description_length"] > 0
    and self.config["min_meta_description_length"] > 0
    ):
    ):
    errors.append("min_meta_description_length must be a positive integer")
    errors.append("min_meta_description_length must be a positive integer")


    if "max_meta_description_length" in self.config and not (
    if "max_meta_description_length" in self.config and not (
    isinstance(self.config["max_meta_description_length"], int)
    isinstance(self.config["max_meta_description_length"], int)
    and self.config["max_meta_description_length"] > 0
    and self.config["max_meta_description_length"] > 0
    ):
    ):
    errors.append("max_meta_description_length must be a positive integer")
    errors.append("max_meta_description_length must be a positive integer")


    # Check min <= max
    # Check min <= max
    if (
    if (
    "min_keyword_density" in self.config
    "min_keyword_density" in self.config
    and "max_keyword_density" in self.config
    and "max_keyword_density" in self.config
    and self.config["min_keyword_density"] > self.config["max_keyword_density"]
    and self.config["min_keyword_density"] > self.config["max_keyword_density"]
    ):
    ):
    errors.append(
    errors.append(
    "min_keyword_density must be less than or equal to max_keyword_density"
    "min_keyword_density must be less than or equal to max_keyword_density"
    )
    )


    if (
    if (
    "min_title_length" in self.config
    "min_title_length" in self.config
    and "max_title_length" in self.config
    and "max_title_length" in self.config
    and self.config["min_title_length"] > self.config["max_title_length"]
    and self.config["min_title_length"] > self.config["max_title_length"]
    ):
    ):
    errors.append(
    errors.append(
    "min_title_length must be less than or equal to max_title_length"
    "min_title_length must be less than or equal to max_title_length"
    )
    )


    if (
    if (
    "min_meta_description_length" in self.config
    "min_meta_description_length" in self.config
    and "max_meta_description_length" in self.config
    and "max_meta_description_length" in self.config
    and self.config["min_meta_description_length"]
    and self.config["min_meta_description_length"]
    > self.config["max_meta_description_length"]
    > self.config["max_meta_description_length"]
    ):
    ):
    errors.append(
    errors.append(
    "min_meta_description_length must be less than or equal to max_meta_description_length"
    "min_meta_description_length must be less than or equal to max_meta_description_length"
    )
    )


    if (
    if (
    "min_word_count" in self.config
    "min_word_count" in self.config
    and "optimal_word_count" in self.config
    and "optimal_word_count" in self.config
    and self.config["min_word_count"] > self.config["optimal_word_count"]
    and self.config["min_word_count"] > self.config["optimal_word_count"]
    ):
    ):
    errors.append(
    errors.append(
    "min_word_count must be less than or equal to optimal_word_count"
    "min_word_count must be less than or equal to optimal_word_count"
    )
    )


    return len(errors) == 0, errors
    return len(errors) == 0, errors


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


    def merge_configs(self, override_config: Dict[str, Any]) -> Dict[str, Any]:
    def merge_configs(self, override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Merge two configuration dictionaries.
    Merge two configuration dictionaries.


    Args:
    Args:
    override_config: Override configuration dictionary
    override_config: Override configuration dictionary


    Returns:
    Returns:
    Merged configuration dictionary
    Merged configuration dictionary
    """
    """
    # Create a copy of the base config
    # Create a copy of the base config
    merged_config = self.config.copy()
    merged_config = self.config.copy()


    # Update with override config
    # Update with override config
    merged_config.update(override_config)
    merged_config.update(override_config)


    # Update timestamp
    # Update timestamp
    merged_config["timestamp"] = datetime.datetime.now().isoformat()
    merged_config["timestamp"] = datetime.datetime.now().isoformat()


    return merged_config
    return merged_config


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the SEO analyzer to a dictionary.
    Convert the SEO analyzer to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the SEO analyzer
    Dictionary representation of the SEO analyzer
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
    Convert the SEO analyzer to a JSON string.
    Convert the SEO analyzer to a JSON string.


    Args:
    Args:
    indent: Number of spaces for indentation
    indent: Number of spaces for indentation


    Returns:
    Returns:
    JSON string representation of the SEO analyzer
    JSON string representation of the SEO analyzer
    """
    """
    return json.dumps(self.to_dict(), indent=indent)
    return json.dumps(self.to_dict(), indent=indent)




    class KeywordAnalyzer(SEOAnalyzer):
    class KeywordAnalyzer(SEOAnalyzer):
    """
    """
    Class for analyzing keyword usage in content.
    Class for analyzing keyword usage in content.


    This class provides methods for analyzing keyword density, placement,
    This class provides methods for analyzing keyword density, placement,
    and optimization in content.
    and optimization in content.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    content: Optional[Dict[str, Any]] = None,
    content: Optional[Dict[str, Any]] = None,
    keywords: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None,
    config: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize a keyword analyzer.
    Initialize a keyword analyzer.


    Args:
    Args:
    content: Optional content to analyze
    content: Optional content to analyze
    keywords: Optional list of keywords to analyze
    keywords: Optional list of keywords to analyze
    config: Optional configuration dictionary
    config: Optional configuration dictionary
    """
    """
    super().__init__(content, config)
    super().__init__(content, config)
    self.keywords = keywords or []
    self.keywords = keywords or []


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


    try:
    try:
    nltk.data.find("corpora/stopwords")
    nltk.data.find("corpora/stopwords")
except LookupError:
except LookupError:
    nltk.download("stopwords")
    nltk.download("stopwords")


    def set_keywords(self, keywords: List[str]) -> None:
    def set_keywords(self, keywords: List[str]) -> None:
    """
    """
    Set the keywords to analyze.
    Set the keywords to analyze.


    Args:
    Args:
    keywords: List of keywords
    keywords: List of keywords
    """
    """
    self.keywords = keywords
    self.keywords = keywords
    self.results = None  # Reset results
    self.results = None  # Reset results


    def validate_content(self) -> Tuple[bool, List[str]]:
    def validate_content(self) -> Tuple[bool, List[str]]:
    """
    """
    Validate the content for keyword analysis.
    Validate the content for keyword analysis.


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


    # Check required fields
    # Check required fields
    required_fields = ["title"]
    required_fields = ["title"]


    for field in required_fields:
    for field in required_fields:
    if field not in self.content:
    if field not in self.content:
    errors.append(f"Missing required field: {field}")
    errors.append(f"Missing required field: {field}")


    # Check if keywords are provided
    # Check if keywords are provided
    if not self.keywords:
    if not self.keywords:
    errors.append("No keywords provided")
    errors.append("No keywords provided")


    return len(errors) == 0, errors
    return len(errors) == 0, errors


    def analyze(self) -> Dict[str, Any]:
    def analyze(self) -> Dict[str, Any]:
    """
    """
    Analyze the content for keyword optimization.
    Analyze the content for keyword optimization.


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
    "keywords": self.keywords,
    "keywords": self.keywords,
    "keyword_density": {},
    "keyword_density": {},
    "keyword_placement": {},
    "keyword_placement": {},
    "overall_score": 0.0,
    "overall_score": 0.0,
    "recommendations": [],
    "recommendations": [],
    }
    }


    # Analyze keyword density
    # Analyze keyword density
    self.results["keyword_density"] = self._analyze_keyword_density()
    self.results["keyword_density"] = self._analyze_keyword_density()


    # Analyze keyword placement
    # Analyze keyword placement
    self.results["keyword_placement"] = self._analyze_keyword_placement()
    self.results["keyword_placement"] = self._analyze_keyword_placement()


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


    def _analyze_keyword_density(self) -> Dict[str, Any]:
    def _analyze_keyword_density(self) -> Dict[str, Any]:
    """
    """
    Analyze keyword density in the content.
    Analyze keyword density in the content.


    This method implements a sophisticated algorithm for calculating optimal keyword density
    This method implements a sophisticated algorithm for calculating optimal keyword density
    for SEO purposes. The process includes:
    for SEO purposes. The process includes:


    1. Extract text from all content sections (title, meta description, body content, etc.)
    1. Extract text from all content sections (title, meta description, body content, etc.)
    2. Tokenize the text and count total words
    2. Tokenize the text and count total words
    3. For each keyword:
    3. For each keyword:
    - Count exact occurrences using word boundary matching to prevent partial matches
    - Count exact occurrences using word boundary matching to prevent partial matches
    - Calculate density ratio (keyword occurrences ÷ total words)
    - Calculate density ratio (keyword occurrences ÷ total words)
    - Evaluate if the density falls within the optimal range (typically 1-3%)
    - Evaluate if the density falls within the optimal range (typically 1-3%)
    4. Return detailed metrics for each keyword with optimization status
    4. Return detailed metrics for each keyword with optimization status


    The optimal keyword density is configured through:
    The optimal keyword density is configured through:
    - min_keyword_density (default: 1%)
    - min_keyword_density (default: 1%)
    - max_keyword_density (default: 3%)
    - max_keyword_density (default: 3%)


    These parameters can be adjusted based on specific SEO requirements and content type.
    These parameters can be adjusted based on specific SEO requirements and content type.


    Returns:
    Returns:
    Dictionary with keyword density analysis including:
    Dictionary with keyword density analysis including:
    - total_words: Total word count in the content
    - total_words: Total word count in the content
    - keywords: Dictionary mapping each keyword to its metrics:
    - keywords: Dictionary mapping each keyword to its metrics:
    - count: Number of occurrences
    - count: Number of occurrences
    - density: Keyword density percentage
    - density: Keyword density percentage
    - is_optimal: Whether density falls within optimal range
    - is_optimal: Whether density falls within optimal range
    - optimal_range: Configuration values for min/max density
    - optimal_range: Configuration values for min/max density
    """
    """
    # Extract text from content
    # Extract text from content
    text = self._extract_text_from_content()
    text = self._extract_text_from_content()


    # Count total words
    # Count total words
    total_words = len(self._tokenize_text(text))
    total_words = len(self._tokenize_text(text))


    # Calculate keyword density for each keyword
    # Calculate keyword density for each keyword
    keyword_density = {}
    keyword_density = {}


    for keyword in self.keywords:
    for keyword in self.keywords:
    # Count keyword occurrences
    # Count keyword occurrences
    keyword_count = self._count_keyword_occurrences(text, keyword)
    keyword_count = self._count_keyword_occurrences(text, keyword)


    # Calculate density
    # Calculate density
    density = keyword_count / total_words if total_words > 0 else 0
    density = keyword_count / total_words if total_words > 0 else 0


    # Determine if density is within optimal range
    # Determine if density is within optimal range
    is_optimal = (
    is_optimal = (
    self.config["min_keyword_density"]
    self.config["min_keyword_density"]
    <= density
    <= density
    <= self.config["max_keyword_density"]
    <= self.config["max_keyword_density"]
    )
    )


    keyword_density[keyword] = {
    keyword_density[keyword] = {
    "count": keyword_count,
    "count": keyword_count,
    "density": density,
    "density": density,
    "is_optimal": is_optimal,
    "is_optimal": is_optimal,
    "optimal_range": {
    "optimal_range": {
    "min": self.config["min_keyword_density"],
    "min": self.config["min_keyword_density"],
    "max": self.config["max_keyword_density"],
    "max": self.config["max_keyword_density"],
    },
    },
    }
    }


    return {"total_words": total_words, "keywords": keyword_density}
    return {"total_words": total_words, "keywords": keyword_density}


    def _analyze_keyword_placement(self) -> Dict[str, Any]:
    def _analyze_keyword_placement(self) -> Dict[str, Any]:
    """
    """
    Analyze keyword placement in strategic content locations.
    Analyze keyword placement in strategic content locations.


    This method evaluates the strategic placement of keywords in high-value content locations
    This method evaluates the strategic placement of keywords in high-value content locations
    that have significant impact on SEO performance. The algorithm:
    that have significant impact on SEO performance. The algorithm:


    1. Identifies key content sections with higher SEO weight:
    1. Identifies key content sections with higher SEO weight:
    - Title (H1) - highest importance
    - Title (H1) - highest importance
    - Meta description - high importance for SERP display
    - Meta description - high importance for SERP display
    - First paragraph - crucial for establishing relevance
    - First paragraph - crucial for establishing relevance
    - Headings (H2, H3) - important for topic structure
    - Headings (H2, H3) - important for topic structure
    - URL slug - significant for search indexing
    - URL slug - significant for search indexing
    - Alt text in images - important for image search and accessibility
    - Alt text in images - important for image search and accessibility


    2. For each keyword:
    2. For each keyword:
    - Checks presence in each strategic location
    - Checks presence in each strategic location
    - Assigns placement score based on configured weights
    - Assigns placement score based on configured weights
    - Calculates overall placement effectiveness score (0-100)
    - Calculates overall placement effectiveness score (0-100)


    3. Provides placement recommendations based on gaps identified
    3. Provides placement recommendations based on gaps identified


    Returns:
    Returns:
    Dictionary with placement analysis for each keyword:
    Dictionary with placement analysis for each keyword:
    - locations: Dict mapping locations to boolean presence indicator
    - locations: Dict mapping locations to boolean presence indicator
    - placement_score: Overall placement effectiveness score (0-100)
    - placement_score: Overall placement effectiveness score (0-100)
    - recommendations: List of recommended placement improvements
    - recommendations: List of recommended placement improvements
    """
    """
    # Extract text from different content sections
    # Extract text from different content sections
    title = self.content.get("title", "")
    title = self.content.get("title", "")
    meta_description = self.content.get("meta_description", "")
    meta_description = self.content.get("meta_description", "")
    first_paragraph = self._extract_first_paragraph()
    first_paragraph = self._extract_first_paragraph()
    headings = self._extract_headings()
    headings = self._extract_headings()
    url = self.content.get("url", "")
    url = self.content.get("url", "")
    alt_texts = self._extract_image_alt_texts()
    alt_texts = self._extract_image_alt_texts()


    # Initialize placement analysis
    # Initialize placement analysis
    placement_analysis = {}
    placement_analysis = {}


    for keyword in self.keywords:
    for keyword in self.keywords:
    # Check keyword presence in each location
    # Check keyword presence in each location
    locations = {
    locations = {
    "title": self._contains_keyword(title, keyword),
    "title": self._contains_keyword(title, keyword),
    "meta_description": self._contains_keyword(meta_description, keyword),
    "meta_description": self._contains_keyword(meta_description, keyword),
    "first_paragraph": self._contains_keyword(first_paragraph, keyword),
    "first_paragraph": self._contains_keyword(first_paragraph, keyword),
    "headings": any(
    "headings": any(
    self._contains_keyword(heading, keyword) for heading in headings
    self._contains_keyword(heading, keyword) for heading in headings
    ),
    ),
    "url": self._contains_keyword(url, keyword),
    "url": self._contains_keyword(url, keyword),
    "alt_texts": any(
    "alt_texts": any(
    self._contains_keyword(alt, keyword) for alt in alt_texts
    self._contains_keyword(alt, keyword) for alt in alt_texts
    ),
    ),
    }
    }


    # Calculate placement score based on location weights
    # Calculate placement score based on location weights
    placement_score = self._calculate_placement_score(locations)
    placement_score = self._calculate_placement_score(locations)


    # Generate placement recommendations
    # Generate placement recommendations
    recommendations = self._generate_placement_recommendations(
    recommendations = self._generate_placement_recommendations(
    locations, keyword
    locations, keyword
    )
    )


    placement_analysis[keyword] = {
    placement_analysis[keyword] = {
    "locations": locations,
    "locations": locations,
    "placement_score": placement_score,
    "placement_score": placement_score,
    "recommendations": recommendations,
    "recommendations": recommendations,
    }
    }


    return placement_analysis
    return placement_analysis


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


    def _extract_first_paragraph(self) -> str:
    def _extract_first_paragraph(self) -> str:
    """
    """
    Extract the first paragraph from the content.
    Extract the first paragraph from the content.


    Returns:
    Returns:
    The first paragraph as a string
    The first paragraph as a string
    """
    """
    # Implementation depends on content structure
    # Implementation depends on content structure
    # Placeholder implementation:
    # Placeholder implementation:
    return self.content.get("introduction", "")
    return self.content.get("introduction", "")


    def _extract_headings(self) -> List[str]:
    def _extract_headings(self) -> List[str]:
    """
    """
    Extract headings from the content.
    Extract headings from the content.


    Returns:
    Returns:
    List of headings as strings
    List of headings as strings
    """
    """
    # Implementation depends on content structure
    # Implementation depends on content structure
    # Placeholder implementation:
    # Placeholder implementation:
    return [
    return [
    section.get("title", "") for section in self.content.get("sections", [])
    section.get("title", "") for section in self.content.get("sections", [])
    ]
    ]


    def _extract_image_alt_texts(self) -> List[str]:
    def _extract_image_alt_texts(self) -> List[str]:
    """
    """
    Extract alt texts from images in the content.
    Extract alt texts from images in the content.


    Returns:
    Returns:
    List of alt texts as strings
    List of alt texts as strings
    """
    """
    # Implementation depends on content structure
    # Implementation depends on content structure
    # Placeholder implementation:
    # Placeholder implementation:
    return [image.get("alt", "") for image in self.content.get("images", [])]
    return [image.get("alt", "") for image in self.content.get("images", [])]


    def _tokenize_text(self, text: str) -> List[str]:
    def _tokenize_text(self, text: str) -> List[str]:
    """
    """
    Tokenize text into words.
    Tokenize text into words.


    Args:
    Args:
    text: The text to tokenize
    text: The text to tokenize


    Returns:
    Returns:
    List of words
    List of words
    """
    """
    # Remove punctuation
    # Remove punctuation
    text = re.sub(r"[^\w\s]", "", text.lower())
    text = re.sub(r"[^\w\s]", "", text.lower())


    # Split on whitespace
    # Split on whitespace
    return text.split()
    return text.split()


    def _count_keyword_occurrences(self, text: str, keyword: str) -> int:
    def _count_keyword_occurrences(self, text: str, keyword: str) -> int:
    """
    """
    Count the number of occurrences of a keyword in text.
    Count the number of occurrences of a keyword in text.


    This method uses word boundary matching to prevent partial matches.
    This method uses word boundary matching to prevent partial matches.
    For example, searching for "car" won't match "carpet" or "scar".
    For example, searching for "car" won't match "carpet" or "scar".


    Args:
    Args:
    text: The text to search in
    text: The text to search in
    keyword: The keyword to count
    keyword: The keyword to count


    Returns:
    Returns:
    Number of occurrences
    Number of occurrences
    """
    """
    # Convert to lowercase for case-insensitive matching
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()
    text_lower = text.lower()
    keyword_lower = keyword.lower()
    keyword_lower = keyword.lower()


    # Use word boundary matching to count occurrences
    # Use word boundary matching to count occurrences
    pattern = r"\b" + re.escape(keyword_lower) + r"\b"
    pattern = r"\b" + re.escape(keyword_lower) + r"\b"
    matches = re.findall(pattern, text_lower)
    matches = re.findall(pattern, text_lower)


    return len(matches)
    return len(matches)


    def _contains_keyword(self, text: str, keyword: str) -> bool:
    def _contains_keyword(self, text: str, keyword: str) -> bool:
    """
    """
    Check if the text contains the keyword.
    Check if the text contains the keyword.


    Args:
    Args:
    text: The text to check
    text: The text to check
    keyword: The keyword to look for
    keyword: The keyword to look for


    Returns:
    Returns:
    True if the text contains the keyword, False otherwise
    True if the text contains the keyword, False otherwise
    """
    """
    return keyword.lower() in text.lower()
    return keyword.lower() in text.lower()


    def _calculate_placement_score(self, locations: Dict[str, bool]) -> float:
    def _calculate_placement_score(self, locations: Dict[str, bool]) -> float:
    """
    """
    Calculate the placement score based on keyword locations.
    Calculate the placement score based on keyword locations.


    Args:
    Args:
    locations: Dictionary mapping locations to boolean presence indicator
    locations: Dictionary mapping locations to boolean presence indicator


    Returns:
    Returns:
    Placement score (0-100)
    Placement score (0-100)
    """
    """
    # Weights for each location
    # Weights for each location
    weights = {
    weights = {
    "title": 3.0,
    "title": 3.0,
    "meta_description": 2.0,
    "meta_description": 2.0,
    "first_paragraph": 2.0,
    "first_paragraph": 2.0,
    "headings": 1.5,
    "headings": 1.5,
    "url": 1.0,
    "url": 1.0,
    "alt_texts": 1.0,
    "alt_texts": 1.0,
    }
    }


    # Calculate score
    # Calculate score
    score = sum(weights[loc] for loc, present in locations.items() if present)
    score = sum(weights[loc] for loc, present in locations.items() if present)


    # Normalize score to 0-100 range
    # Normalize score to 0-100 range
    max_score = sum(weights.values())
    max_score = sum(weights.values())
    placement_score = (score / max_score) * 100 if max_score > 0 else 0
    placement_score = (score / max_score) * 100 if max_score > 0 else 0


    return placement_score
    return placement_score


    def _generate_placement_recommendations(
    def _generate_placement_recommendations(
    self, locations: Dict[str, bool], keyword: str
    self, locations: Dict[str, bool], keyword: str
    ) -> List[str]:
    ) -> List[str]:
    """
    """
    Generate recommendations for improving keyword placement.
    Generate recommendations for improving keyword placement.


    Args:
    Args:
    locations: Dictionary mapping locations to boolean presence indicator
    locations: Dictionary mapping locations to boolean presence indicator
    keyword: The keyword being analyzed
    keyword: The keyword being analyzed


    Returns:
    Returns:
    List of recommendation strings
    List of recommendation strings
    """
    """
    recommendations = []
    recommendations = []


    # Check each location and suggest improvements if keyword is missing
    # Check each location and suggest improvements if keyword is missing
    for loc, present in locations.items():
    for loc, present in locations.items():
    if not present:
    if not present:
    recommendations.append(
    recommendations.append(
    f"Consider including the keyword '{keyword}' in the {loc.replace('_', ' ')}."
    f"Consider including the keyword '{keyword}' in the {loc.replace('_', ' ')}."
    )
    )


    return recommendations
    return recommendations


    def get_score(self) -> float:
    def get_score(self) -> float:
    """
    """
    Get the overall SEO score for the content.
    Get the overall SEO score for the content.


    Returns:
    Returns:
    SEO score between 0 and 1
    SEO score between 0 and 1
    """
    """
    if self.results is None:
    if self.results is None:
    self.analyze()
    self.analyze()


    # Calculate density score
    # Calculate density score
    density_scores = []
    density_scores = []


    for keyword, data in self.results["keyword_density"]["keywords"].items():
    for keyword, data in self.results["keyword_density"]["keywords"].items():
    if data["is_optimal"]:
    if data["is_optimal"]:
    density_scores.append(1.0)
    density_scores.append(1.0)
    else:
    else:
    # Calculate how close the density is to the optimal range
    # Calculate how close the density is to the optimal range
    density = data["density"]
    density = data["density"]
    min_density = data["optimal_range"]["min"]
    min_density = data["optimal_range"]["min"]
    max_density = data["optimal_range"]["max"]
    max_density = data["optimal_range"]["max"]


    if density < min_density:
    if density < min_density:
    # Score based on how close to min_density
    # Score based on how close to min_density
    density_scores.append(density / min_density)
    density_scores.append(density / min_density)
    else:  # density > max_density
    else:  # density > max_density
    # Score based on how close to max_density
    # Score based on how close to max_density
    density_scores.append(max_density / density)
    density_scores.append(max_density / density)


    density_score = (
    density_score = (
    sum(density_scores) / len(density_scores) if density_scores else 0
    sum(density_scores) / len(density_scores) if density_scores else 0
    )
    )


    # Calculate placement score
    # Calculate placement score
    placement_scores = []
    placement_scores = []


    for keyword, data in self.results["keyword_placement"].items():
    for keyword, data in self.results["keyword_placement"].items():
    # Normalize placement score from 0-100 to 0-1
    # Normalize placement score from 0-100 to 0-1
    placement_scores.append(data["placement_score"] / 100.0)
    placement_scores.append(data["placement_score"] / 100.0)


    placement_score = (
    placement_score = (
    sum(placement_scores) / len(placement_scores) if placement_scores else 0
    sum(placement_scores) / len(placement_scores) if placement_scores else 0
    )
    )


    # Calculate overall score (50% density, 50% placement)
    # Calculate overall score (50% density, 50% placement)
    overall_score = (density_score * 0.5) + (placement_score * 0.5)
    overall_score = (density_score * 0.5) + (placement_score * 0.5)


    return overall_score
    return overall_score


    def get_recommendations(self) -> List[Dict[str, Any]]:
    def get_recommendations(self) -> List[Dict[str, Any]]:
    """
    """
    Get SEO recommendations for the content.
    Get SEO recommendations for the content.


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


    # Check keyword density
    # Check keyword density
    for keyword, data in self.results["keyword_density"]["keywords"].items():
    for keyword, data in self.results["keyword_density"]["keywords"].items():
    if not data["is_optimal"]:
    if not data["is_optimal"]:
    density = data["density"]
    density = data["density"]
    min_density = data["optimal_range"]["min"]
    min_density = data["optimal_range"]["min"]
    max_density = data["optimal_range"]["max"]
    max_density = data["optimal_range"]["max"]


    if density < min_density:
    if density < min_density:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "keyword_density",
    "type": "keyword_density",
    "keyword": keyword,
    "keyword": keyword,
    "severity": "medium",
    "severity": "medium",
    "message": f"Keyword '{keyword}' density is too low ({density:.2%}). Aim for at least {min_density:.2%}.",
    "message": f"Keyword '{keyword}' density is too low ({density:.2%}). Aim for at least {min_density:.2%}.",
    "suggestion": f"Add more instances of '{keyword}' throughout the content.",
    "suggestion": f"Add more instances of '{keyword}' throughout the content.",
    }
    }
    )
    )
    else:  # density > max_density
    else:  # density > max_density
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "keyword_density",
    "type": "keyword_density",
    "keyword": keyword,
    "keyword": keyword,
    "severity": "medium",
    "severity": "medium",
    "message": f"Keyword '{keyword}' density is too high ({density:.2%}). Aim for at most {max_density:.2%}.",
    "message": f"Keyword '{keyword}' density is too high ({density:.2%}). Aim for at most {max_density:.2%}.",
    "suggestion": f"Reduce the number of instances of '{keyword}' or add more content to dilute the density.",
    "suggestion": f"Reduce the number of instances of '{keyword}' or add more content to dilute the density.",
    }
    }
    )
    )


    # Check keyword placement
    # Check keyword placement
    for keyword, data in self.results["keyword_placement"].items():
    for keyword, data in self.results["keyword_placement"].items():
    # Get the locations dictionary
    # Get the locations dictionary
    locations = data["locations"]
    locations = data["locations"]


    # Check title
    # Check title
    if not locations["title"] and self.config.get(
    if not locations["title"] and self.config.get(
    "check_keyword_in_title", True
    "check_keyword_in_title", True
    ):
    ):
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "keyword_placement",
    "type": "keyword_placement",
    "keyword": keyword,
    "keyword": keyword,
    "severity": "high",
    "severity": "high",
    "message": f"Keyword '{keyword}' is not in the title.",
    "message": f"Keyword '{keyword}' is not in the title.",
    "suggestion": f"Include '{keyword}' in the title for better SEO.",
    "suggestion": f"Include '{keyword}' in the title for better SEO.",
    }
    }
    )
    )


    # Check headings
    # Check headings
    if not locations["headings"] and self.config.get(
    if not locations["headings"] and self.config.get(
    "check_keyword_in_headings", True
    "check_keyword_in_headings", True
    ):
    ):
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "keyword_placement",
    "type": "keyword_placement",
    "keyword": keyword,
    "keyword": keyword,
    "severity": "medium",
    "severity": "medium",
    "message": f"Keyword '{keyword}' is not in any headings.",
    "message": f"Keyword '{keyword}' is not in any headings.",
    "suggestion": f"Include '{keyword}' in at least one heading for better SEO.",
    "suggestion": f"Include '{keyword}' in at least one heading for better SEO.",
    }
    }
    )
    )


    # Check first paragraph
    # Check first paragraph
    if not locations["first_paragraph"] and self.config.get(
    if not locations["first_paragraph"] and self.config.get(
    "check_keyword_in_first_paragraph", True
    "check_keyword_in_first_paragraph", True
    ):
    ):
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "keyword_placement",
    "type": "keyword_placement",
    "keyword": keyword,
    "keyword": keyword,
    "severity": "medium",
    "severity": "medium",
    "message": f"Keyword '{keyword}' is not in the first paragraph.",
    "message": f"Keyword '{keyword}' is not in the first paragraph.",
    "suggestion": f"Include '{keyword}' in the first paragraph for better SEO.",
    "suggestion": f"Include '{keyword}' in the first paragraph for better SEO.",
    }
    }
    )
    )


    # Check meta description
    # Check meta description
    if not locations["meta_description"] and self.config.get(
    if not locations["meta_description"] and self.config.get(
    "check_keyword_in_meta_description", True
    "check_keyword_in_meta_description", True
    ):
    ):
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "keyword_placement",
    "type": "keyword_placement",
    "keyword": keyword,
    "keyword": keyword,
    "severity": "medium",
    "severity": "medium",
    "message": f"Keyword '{keyword}' is not in the meta description.",
    "message": f"Keyword '{keyword}' is not in the meta description.",
    "suggestion": f"Include '{keyword}' in the meta description for better SEO.",
    "suggestion": f"Include '{keyword}' in the meta description for better SEO.",
    }
    }
    )
    )


    # Check URL
    # Check URL
    if not locations["url"] and self.config.get("check_keyword_in_url", True):
    if not locations["url"] and self.config.get("check_keyword_in_url", True):
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "keyword_placement",
    "type": "keyword_placement",
    "keyword": keyword,
    "keyword": keyword,
    "severity": "medium",
    "severity": "medium",
    "message": f"Keyword '{keyword}' is not in the URL.",
    "message": f"Keyword '{keyword}' is not in the URL.",
    "suggestion": f"Include '{keyword}' in the URL for better SEO.",
    "suggestion": f"Include '{keyword}' in the URL for better SEO.",
    }
    }
    )
    )


    # Check word count
    # Check word count
    total_words = self.results["keyword_density"]["total_words"]
    total_words = self.results["keyword_density"]["total_words"]
    min_word_count = self.config["min_word_count"]
    min_word_count = self.config["min_word_count"]
    optimal_word_count = self.config["optimal_word_count"]
    optimal_word_count = self.config["optimal_word_count"]


    if total_words < min_word_count:
    if total_words < min_word_count:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "content_length",
    "type": "content_length",
    "severity": "high",
    "severity": "high",
    "message": f"Content is too short ({total_words} words). Aim for at least {min_word_count} words.",
    "message": f"Content is too short ({total_words} words). Aim for at least {min_word_count} words.",
    "suggestion": "Add more content to provide more value and improve SEO.",
    "suggestion": "Add more content to provide more value and improve SEO.",
    }
    }
    )
    )
    elif total_words < optimal_word_count:
    elif total_words < optimal_word_count:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "content_length",
    "type": "content_length",
    "severity": "low",
    "severity": "low",
    "message": f"Content is shorter than optimal ({total_words} words). Aim for around {optimal_word_count} words for best results.",
    "message": f"Content is shorter than optimal ({total_words} words). Aim for around {optimal_word_count} words for best results.",
    "suggestion": "Consider adding more content to provide more value and improve SEO.",
    "suggestion": "Consider adding more content to provide more value and improve SEO.",
    }
    }
    )
    )


    return recommendations
    return recommendations




    class ReadabilityAnalyzer(SEOAnalyzer):
    class ReadabilityAnalyzer(SEOAnalyzer):
    """
    """
    Class for analyzing the readability of content.
    Class for analyzing the readability of content.


    This class provides methods for analyzing readability metrics, sentence structure,
    This class provides methods for analyzing readability metrics, sentence structure,
    and text complexity in content.
    and text complexity in content.
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
    Initialize a readability analyzer.
    Initialize a readability analyzer.


    Args:
    Args:
    content: Optional content to analyze
    content: Optional content to analyze
    config: Optional configuration dictionary
    config: Optional configuration dictionary
    """
    """
    super().__init__(content, config)
    super().__init__(content, config)


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
    Get the default configuration for the readability analyzer.
    Get the default configuration for the readability analyzer.


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


    # Add readability-specific config
    # Add readability-specific config
    config.update(
    config.update(
    {
    {
    "target_reading_level": "intermediate",  # beginner, intermediate, advanced
    "target_reading_level": "intermediate",  # beginner, intermediate, advanced
    "max_sentence_length": 25,  # words
    "max_sentence_length": 25,  # words
    "min_sentence_length": 5,  # words
    "min_sentence_length": 5,  # words
    "max_paragraph_length": 150,  # words
    "max_paragraph_length": 150,  # words
    "min_paragraph_length": 30,  # words
    "min_paragraph_length": 30,  # words
    "max_passive_voice_percentage": 0.15,  # 15%
    "max_passive_voice_percentage": 0.15,  # 15%
    "max_complex_word_percentage": 0.1,  # 10%
    "max_complex_word_percentage": 0.1,  # 10%
    "min_flesch_reading_ease": 60.0,  # 60-70 is standard
    "min_flesch_reading_ease": 60.0,  # 60-70 is standard
    "max_flesch_kincaid_grade": 9.0,  # 9th grade level
    "max_flesch_kincaid_grade": 9.0,  # 9th grade level
    "max_smog_index": 9.0,  # 9th grade level
    "max_smog_index": 9.0,  # 9th grade level
    "max_coleman_liau_index": 9.0,  # 9th grade level
    "max_coleman_liau_index": 9.0,  # 9th grade level
    "max_automated_readability_index": 9.0,  # 9th grade level
    "max_automated_readability_index": 9.0,  # 9th grade level
    "max_gunning_fog_index": 12.0,  # 12th grade level
    "max_gunning_fog_index": 12.0,  # 12th grade level
    "check_transition_words": True,
    "check_transition_words": True,
    "check_sentence_beginnings": True,
    "check_sentence_beginnings": True,
    "check_adverb_usage": True,
    "check_adverb_usage": True,
    "check_passive_voice": True,
    "check_passive_voice": True,
    "check_consecutive_sentences": True,
    "check_consecutive_sentences": True,
    }
    }
    )
    )


    return config
    return config


    def validate_content(self) -> Tuple[bool, List[str]]:
    def validate_content(self) -> Tuple[bool, List[str]]:
    """
    """
    Validate the content for readability analysis.
    Validate the content for readability analysis.


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


    return len(errors) == 0, errors
    return len(errors) == 0, errors


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
    text = ""
    text = ""


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


    def analyze(self) -> Dict[str, Any]:
    def analyze(self) -> Dict[str, Any]:
    """
    """
    Analyze the content for readability.
    Analyze the content for readability.


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
    "text_statistics": {},
    "text_statistics": {},
    "readability_scores": {},
    "readability_scores": {},
    "sentence_analysis": {},
    "sentence_analysis": {},
    "paragraph_analysis": {},
    "paragraph_analysis": {},
    "style_analysis": {},
    "style_analysis": {},
    "overall_score": 0.0,
    "overall_score": 0.0,
    "recommendations": [],
    "recommendations": [],
    }
    }


    # Analyze text statistics
    # Analyze text statistics
    self.results["text_statistics"] = self._analyze_text_statistics(text)
    self.results["text_statistics"] = self._analyze_text_statistics(text)


    # Analyze readability scores
    # Analyze readability scores
    self.results["readability_scores"] = self._analyze_readability_scores(text)
    self.results["readability_scores"] = self._analyze_readability_scores(text)


    # Analyze sentence structure
    # Analyze sentence structure
    self.results["sentence_analysis"] = self._analyze_sentence_structure(text)
    self.results["sentence_analysis"] = self._analyze_sentence_structure(text)


    # Analyze paragraph structure
    # Analyze paragraph structure
    self.results["paragraph_analysis"] = self._analyze_paragraph_structure(text)
    self.results["paragraph_analysis"] = self._analyze_paragraph_structure(text)


    # Analyze writing style
    # Analyze writing style
    self.results["style_analysis"] = self._analyze_writing_style(text)
    self.results["style_analysis"] = self._analyze_writing_style(text)


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


    def _count_syllables(self, text: str) -> int:
    def _count_syllables(self, text: str) -> int:
    """
    """
    Count syllables in text.
    Count syllables in text.


    Args:
    Args:
    text: Text to analyze
    text: Text to analyze


    Returns:
    Returns:
    Number of syllables
    Number of syllables
    """
    """
    words = self._get_words(text)
    words = self._get_words(text)


    # Count syllables in each word
    # Count syllables in each word
    return sum(self._count_syllables_in_word(word) for word in words)
    return sum(self._count_syllables_in_word(word) for word in words)


    def _count_syllables_in_word(self, word: str) -> int:
    def _count_syllables_in_word(self, word: str) -> int:
    """
    """
    Count syllables in a word.
    Count syllables in a word.


    Args:
    Args:
    word: Word to analyze
    word: Word to analyze


    Returns:
    Returns:
    Number of syllables
    Number of syllables
    """
    """
    # Remove non-alphabetic characters
    # Remove non-alphabetic characters
    word = re.sub(r"[^a-zA-Z]", "", word.lower())
    word = re.sub(r"[^a-zA-Z]", "", word.lower())


    if not word:
    if not word:
    return 0
    return 0


    # Count vowel groups
    # Count vowel groups
    count = len(re.findall(r"[aeiouy]+", word))
    count = len(re.findall(r"[aeiouy]+", word))


    # Adjust for silent e at end of word
    # Adjust for silent e at end of word
    if word.endswith("e") and len(word) > 2 and word[-2] not in "aeiouy":
    if word.endswith("e") and len(word) > 2 and word[-2] not in "aeiouy":
    count -= 1
    count -= 1


    # Adjust for words ending in 'le'
    # Adjust for words ending in 'le'
    if word.endswith("le") and len(word) > 2 and word[-3] not in "aeiouy":
    if word.endswith("le") and len(word) > 2 and word[-3] not in "aeiouy":
    count += 1
    count += 1


    # Ensure at least one syllable
    # Ensure at least one syllable
    return max(1, count)
    return max(1, count)


    def _analyze_text_statistics(self, text: str) -> Dict[str, Any]:
    def _analyze_text_statistics(self, text: str) -> Dict[str, Any]:
    """
    """
    Analyze text statistics.
    Analyze text statistics.


    Args:
    Args:
    text: Text to analyze
    text: Text to analyze


    Returns:
    Returns:
    Dictionary with text statistics
    Dictionary with text statistics
    """
    """
    # Get sentences
    # Get sentences
    sentences = self._get_sentences(text)
    sentences = self._get_sentences(text)
    num_sentences = len(sentences)
    num_sentences = len(sentences)


    # Get words
    # Get words
    words = self._get_words(text)
    words = self._get_words(text)
    num_words = len(words)
    num_words = len(words)


    # Get paragraphs
    # Get paragraphs
    paragraphs = self._get_paragraphs(text)
    paragraphs = self._get_paragraphs(text)
    num_paragraphs = len(paragraphs)
    num_paragraphs = len(paragraphs)


    # Get syllables
    # Get syllables
    num_syllables = self._count_syllables(text)
    num_syllables = self._count_syllables(text)


    # Get complex words (words with 3+ syllables)
    # Get complex words (words with 3+ syllables)
    complex_words = [
    complex_words = [
    word for word in words if self._count_syllables_in_word(word) >= 3
    word for word in words if self._count_syllables_in_word(word) >= 3
    ]
    ]
    num_complex_words = len(complex_words)
    num_complex_words = len(complex_words)


    # Calculate averages
    # Calculate averages
    avg_words_per_sentence = num_words / num_sentences if num_sentences > 0 else 0
    avg_words_per_sentence = num_words / num_sentences if num_sentences > 0 else 0
    avg_syllables_per_word = num_syllables / num_words if num_words > 0 else 0
    avg_syllables_per_word = num_syllables / num_words if num_words > 0 else 0
    avg_words_per_paragraph = (
    avg_words_per_paragraph = (
    num_words / num_paragraphs if num_paragraphs > 0 else 0
    num_words / num_paragraphs if num_paragraphs > 0 else 0
    )
    )


    # Calculate percentages
    # Calculate percentages
    complex_word_percentage = num_complex_words / num_words if num_words > 0 else 0
    complex_word_percentage = num_complex_words / num_words if num_words > 0 else 0


    return {
    return {
    "num_sentences": num_sentences,
    "num_sentences": num_sentences,
    "num_words": num_words,
    "num_words": num_words,
    "num_paragraphs": num_paragraphs,
    "num_paragraphs": num_paragraphs,
    "num_syllables": num_syllables,
    "num_syllables": num_syllables,
    "num_complex_words": num_complex_words,
    "num_complex_words": num_complex_words,
    "avg_words_per_sentence": avg_words_per_sentence,
    "avg_words_per_sentence": avg_words_per_sentence,
    "avg_syllables_per_word": avg_syllables_per_word,
    "avg_syllables_per_word": avg_syllables_per_word,
    "avg_words_per_paragraph": avg_words_per_paragraph,
    "avg_words_per_paragraph": avg_words_per_paragraph,
    "complex_word_percentage": complex_word_percentage,
    "complex_word_percentage": complex_word_percentage,
    }
    }


    def _analyze_readability_scores(self, text: str) -> Dict[str, Any]:
    def _analyze_readability_scores(self, text: str) -> Dict[str, Any]:
    """
    """
    Analyze text and calculate comprehensive readability scores using multiple algorithms.
    Analyze text and calculate comprehensive readability scores using multiple algorithms.


    This method computes a suite of industry-standard readability metrics including:
    This method computes a suite of industry-standard readability metrics including:
    - Flesch Reading Ease: Scores text from 0-100, with higher scores indicating easier readability
    - Flesch Reading Ease: Scores text from 0-100, with higher scores indicating easier readability
    - Flesch-Kincaid Grade Level: Estimates the US grade level needed to understand the text
    - Flesch-Kincaid Grade Level: Estimates the US grade level needed to understand the text
    - SMOG Index: Measures readability based on polysyllabic words per sentence
    - SMOG Index: Measures readability based on polysyllabic words per sentence
    - Coleman-Liau Index: Bases readability on character count rather than syllables
    - Coleman-Liau Index: Bases readability on character count rather than syllables
    - Automated Readability Index: Calculates readability based on characters per word and words per sentence
    - Automated Readability Index: Calculates readability based on characters per word and words per sentence
    - Gunning Fog Index: Measures readability based on sentence length and complex words
    - Gunning Fog Index: Measures readability based on sentence length and complex words


    The method also determines an overall grade level by averaging multiple algorithms and
    The method also determines an overall grade level by averaging multiple algorithms and
    provides a qualitative reading level assessment (e.g., "Easy", "Medium", "Difficult").
    provides a qualitative reading level assessment (e.g., "Easy", "Medium", "Difficult").


    Args:
    Args:
    text: The content text to analyze
    text: The content text to analyze


    Returns:
    Returns:
    Dictionary containing all readability scores, interpretations, and optimal status flags
    Dictionary containing all readability scores, interpretations, and optimal status flags
    """
    """
    # Get text statistics
    # Get text statistics
    stats = self._analyze_text_statistics(text)
    stats = self._analyze_text_statistics(text)


    # Calculate Flesch Reading Ease
    # Calculate Flesch Reading Ease
    flesch_reading_ease = self._calculate_flesch_reading_ease(
    flesch_reading_ease = self._calculate_flesch_reading_ease(
    stats["avg_words_per_sentence"], stats["avg_syllables_per_word"]
    stats["avg_words_per_sentence"], stats["avg_syllables_per_word"]
    )
    )


    # Calculate Flesch-Kincaid Grade Level
    # Calculate Flesch-Kincaid Grade Level
    flesch_kincaid_grade = self._calculate_flesch_kincaid_grade(
    flesch_kincaid_grade = self._calculate_flesch_kincaid_grade(
    stats["avg_words_per_sentence"], stats["avg_syllables_per_word"]
    stats["avg_words_per_sentence"], stats["avg_syllables_per_word"]
    )
    )


    # Calculate SMOG Index
    # Calculate SMOG Index
    smog_index = self._calculate_smog_index(
    smog_index = self._calculate_smog_index(
    stats["num_complex_words"], stats["num_sentences"]
    stats["num_complex_words"], stats["num_sentences"]
    )
    )


    # Calculate Coleman-Liau Index
    # Calculate Coleman-Liau Index
    coleman_liau_index = self._calculate_coleman_liau_index(
    coleman_liau_index = self._calculate_coleman_liau_index(
    stats["num_words"], stats["num_sentences"], text
    stats["num_words"], stats["num_sentences"], text
    )
    )


    # Calculate Automated Readability Index
    # Calculate Automated Readability Index
    automated_readability_index = self._calculate_automated_readability_index(
    automated_readability_index = self._calculate_automated_readability_index(
    stats["num_words"], stats["num_sentences"], text
    stats["num_words"], stats["num_sentences"], text
    )
    )


    # Calculate Gunning Fog Index
    # Calculate Gunning Fog Index
    gunning_fog_index = self._calculate_gunning_fog(
    gunning_fog_index = self._calculate_gunning_fog(
    stats["avg_words_per_sentence"], stats["complex_word_percentage"]
    stats["avg_words_per_sentence"], stats["complex_word_percentage"]
    )
    )


    # Determine reading level
    # Determine reading level
    reading_level = self._determine_reading_level(flesch_reading_ease)
    reading_level = self._determine_reading_level(flesch_reading_ease)


    # Determine grade level
    # Determine grade level
    grade_level = self._determine_grade_level(
    grade_level = self._determine_grade_level(
    [
    [
    flesch_kincaid_grade,
    flesch_kincaid_grade,
    smog_index,
    smog_index,
    coleman_liau_index,
    coleman_liau_index,
    automated_readability_index,
    automated_readability_index,
    gunning_fog_index,
    gunning_fog_index,
    ]
    ]
    )
    )


    return {
    return {
    "flesch_reading_ease": {
    "flesch_reading_ease": {
    "score": flesch_reading_ease,
    "score": flesch_reading_ease,
    "interpretation": self._interpret_flesch_reading_ease(
    "interpretation": self._interpret_flesch_reading_ease(
    flesch_reading_ease
    flesch_reading_ease
    ),
    ),
    "is_optimal": flesch_reading_ease
    "is_optimal": flesch_reading_ease
    >= self.config["min_flesch_reading_ease"],
    >= self.config["min_flesch_reading_ease"],
    },
    },
    "flesch_kincaid_grade": {
    "flesch_kincaid_grade": {
    "score": flesch_kincaid_grade,
    "score": flesch_kincaid_grade,
    "interpretation": f"{flesch_kincaid_grade:.1f} grade level",
    "interpretation": f"{flesch_kincaid_grade:.1f} grade level",
    "is_optimal": flesch_kincaid_grade
    "is_optimal": flesch_kincaid_grade
    <= self.config["max_flesch_kincaid_grade"],
    <= self.config["max_flesch_kincaid_grade"],
    },
    },
    "smog_index": {
    "smog_index": {
    "score": smog_index,
    "score": smog_index,
    "interpretation": f"{smog_index:.1f} grade level",
    "interpretation": f"{smog_index:.1f} grade level",
    "is_optimal": smog_index <= self.config["max_smog_index"],
    "is_optimal": smog_index <= self.config["max_smog_index"],
    },
    },
    "coleman_liau_index": {
    "coleman_liau_index": {
    "score": coleman_liau_index,
    "score": coleman_liau_index,
    "interpretation": f"{coleman_liau_index:.1f} grade level",
    "interpretation": f"{coleman_liau_index:.1f} grade level",
    "is_optimal": coleman_liau_index
    "is_optimal": coleman_liau_index
    <= self.config["max_coleman_liau_index"],
    <= self.config["max_coleman_liau_index"],
    },
    },
    "automated_readability_index": {
    "automated_readability_index": {
    "score": automated_readability_index,
    "score": automated_readability_index,
    "interpretation": f"{automated_readability_index:.1f} grade level",
    "interpretation": f"{automated_readability_index:.1f} grade level",
    "is_optimal": automated_readability_index
    "is_optimal": automated_readability_index
    <= self.config["max_automated_readability_index"],
    <= self.config["max_automated_readability_index"],
    },
    },
    "gunning_fog_index": {
    "gunning_fog_index": {
    "score": gunning_fog_index,
    "score": gunning_fog_index,
    "interpretation": f"{gunning_fog_index:.1f} grade level",
    "interpretation": f"{gunning_fog_index:.1f} grade level",
    "is_optimal": gunning_fog_index <= self.config["max_gunning_fog_index"],
    "is_optimal": gunning_fog_index <= self.config["max_gunning_fog_index"],
    },
    },
    "reading_level": reading_level,
    "reading_level": reading_level,
    "grade_level": grade_level,
    "grade_level": grade_level,
    }
    }


    def _calculate_flesch_reading_ease(
    def _calculate_flesch_reading_ease(
    self, avg_words_per_sentence: float, avg_syllables_per_word: float
    self, avg_words_per_sentence: float, avg_syllables_per_word: float
    ) -> float:
    ) -> float:
    """
    """
    Calculate the Flesch Reading Ease score for the text.
    Calculate the Flesch Reading Ease score for the text.


    The Flesch Reading Ease algorithm quantifies text readability using sentence length
    The Flesch Reading Ease algorithm quantifies text readability using sentence length
    and syllable count. The algorithm works as follows:
    and syllable count. The algorithm works as follows:


    1. Count the total number of words, sentences, and syllables in the text
    1. Count the total number of words, sentences, and syllables in the text
    2. Calculate average sentence length (ASL) = words / sentences
    2. Calculate average sentence length (ASL) = words / sentences
    3. Calculate average syllables per word (ASW) = syllables / words
    3. Calculate average syllables per word (ASW) = syllables / words
    4. Apply the formula: 206.835 - (1.015 * ASL) - (84.6 * ASW)
    4. Apply the formula: 206.835 - (1.015 * ASL) - (84.6 * ASW)


    The score ranges from 0-100:
    The score ranges from 0-100:
    - 0-30: Very difficult (College graduate level)
    - 0-30: Very difficult (College graduate level)
    - 30-50: Difficult (College level)
    - 30-50: Difficult (College level)
    - 50-60: Fairly difficult (10th-12th grade)
    - 50-60: Fairly difficult (10th-12th grade)
    - 60-70: Standard (8th-9th grade)
    - 60-70: Standard (8th-9th grade)
    - 70-80: Fairly easy (7th grade)
    - 70-80: Fairly easy (7th grade)
    - 80-90: Easy (6th grade)
    - 80-90: Easy (6th grade)
    - 90-100: Very easy (5th grade)
    - 90-100: Very easy (5th grade)


    Args:
    Args:
    avg_words_per_sentence: Average words per sentence
    avg_words_per_sentence: Average words per sentence
    avg_syllables_per_word: Average syllables per word
    avg_syllables_per_word: Average syllables per word


    Returns:
    Returns:
    Flesch Reading Ease score (0-100, higher is easier to read)
    Flesch Reading Ease score (0-100, higher is easier to read)
    """
    """
    # Formula: 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
    # Formula: 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
    score = (
    score = (
    206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
    206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
    )
    )


    # Clamp score to 0-100 range
    # Clamp score to 0-100 range
    return max(0, min(100, score))
    return max(0, min(100, score))


    def _calculate_flesch_kincaid_grade(
    def _calculate_flesch_kincaid_grade(
    self, avg_words_per_sentence: float, avg_syllables_per_word: float
    self, avg_words_per_sentence: float, avg_syllables_per_word: float
    ) -> float:
    ) -> float:
    """
    """
    Calculate Flesch-Kincaid Grade Level.
    Calculate Flesch-Kincaid Grade Level.


    Args:
    Args:
    avg_words_per_sentence: Average words per sentence
    avg_words_per_sentence: Average words per sentence
    avg_syllables_per_word: Average syllables per word
    avg_syllables_per_word: Average syllables per word


    Returns:
    Returns:
    Flesch-Kincaid Grade Level
    Flesch-Kincaid Grade Level
    """
    """
    # Formula: 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
    # Formula: 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
    score = (
    score = (
    (0.39 * avg_words_per_sentence) + (11.8 * avg_syllables_per_word) - 15.59
    (0.39 * avg_words_per_sentence) + (11.8 * avg_syllables_per_word) - 15.59
    )
    )


    # Clamp score to 0-18 range
    # Clamp score to 0-18 range
    return max(0, min(18, score))
    return max(0, min(18, score))


    def _calculate_smog_index(
    def _calculate_smog_index(
    self, num_complex_words: int, num_sentences: int
    self, num_complex_words: int, num_sentences: int
    ) -> float:
    ) -> float:
    """
    """
    Calculate SMOG Index.
    Calculate SMOG Index.


    Args:
    Args:
    num_complex_words: Number of complex words (3+ syllables)
    num_complex_words: Number of complex words (3+ syllables)
    num_sentences: Number of sentences
    num_sentences: Number of sentences


    Returns:
    Returns:
    SMOG Index
    SMOG Index
    """
    """
    # Need at least 30 sentences for accurate SMOG calculation
    # Need at least 30 sentences for accurate SMOG calculation
    if num_sentences < 30:
    if num_sentences < 30:
    # Adjust formula for fewer sentences
    # Adjust formula for fewer sentences
    adjusted_complex_words = (
    adjusted_complex_words = (
    num_complex_words * (30 / num_sentences) if num_sentences > 0 else 0
    num_complex_words * (30 / num_sentences) if num_sentences > 0 else 0
    )
    )
    else:
    else:
    adjusted_complex_words = num_complex_words
    adjusted_complex_words = num_complex_words


    # Formula: 1.043 * sqrt(complex_words * (30 / sentences)) + 3.1291
    # Formula: 1.043 * sqrt(complex_words * (30 / sentences)) + 3.1291
    score = (
    score = (
    1.043 * math.sqrt(adjusted_complex_words * (30 / max(1, num_sentences)))
    1.043 * math.sqrt(adjusted_complex_words * (30 / max(1, num_sentences)))
    + 3.1291
    + 3.1291
    )
    )


    # Clamp score to 0-18 range
    # Clamp score to 0-18 range
    return max(0, min(18, score))
    return max(0, min(18, score))


    def _calculate_coleman_liau_index(
    def _calculate_coleman_liau_index(
    self, num_words: int, num_sentences: int, text: str
    self, num_words: int, num_sentences: int, text: str
    ) -> float:
    ) -> float:
    """
    """
    Calculate Coleman-Liau Index.
    Calculate Coleman-Liau Index.


    Args:
    Args:
    num_words: Number of words
    num_words: Number of words
    num_sentences: Number of sentences
    num_sentences: Number of sentences
    text: Text to analyze
    text: Text to analyze


    Returns:
    Returns:
    Coleman-Liau Index
    Coleman-Liau Index
    """
    """
    # Count characters (excluding spaces)
    # Count characters (excluding spaces)
    num_chars = len(text.replace(" ", ""))
    num_chars = len(text.replace(" ", ""))


    # Calculate L (average number of characters per 100 words)
    # Calculate L (average number of characters per 100 words)
    L = (num_chars / num_words) * 100 if num_words > 0 else 0
    L = (num_chars / num_words) * 100 if num_words > 0 else 0


    # Calculate S (average number of sentences per 100 words)
    # Calculate S (average number of sentences per 100 words)
    S = (num_sentences / num_words) * 100 if num_words > 0 else 0
    S = (num_sentences / num_words) * 100 if num_words > 0 else 0


    # Formula: 0.0588 * L - 0.296 * S - 15.8
    # Formula: 0.0588 * L - 0.296 * S - 15.8
    score = (0.0588 * L) - (0.296 * S) - 15.8
    score = (0.0588 * L) - (0.296 * S) - 15.8


    # Clamp score to 0-18 range
    # Clamp score to 0-18 range
    return max(0, min(18, score))
    return max(0, min(18, score))


    def _calculate_automated_readability_index(
    def _calculate_automated_readability_index(
    self, num_words: int, num_sentences: int, text: str
    self, num_words: int, num_sentences: int, text: str
    ) -> float:
    ) -> float:
    """
    """
    Calculate Automated Readability Index.
    Calculate Automated Readability Index.


    Args:
    Args:
    num_words: Number of words
    num_words: Number of words
    num_sentences: Number of sentences
    num_sentences: Number of sentences
    text: Text to analyze
    text: Text to analyze


    Returns:
    Returns:
    Automated Readability Index
    Automated Readability Index
    """
    """
    # Count characters (excluding spaces)
    # Count characters (excluding spaces)
    num_chars = len(text.replace(" ", ""))
    num_chars = len(text.replace(" ", ""))


    # Calculate average characters per word
    # Calculate average characters per word
    chars_per_word = num_chars / num_words if num_words > 0 else 0
    chars_per_word = num_chars / num_words if num_words > 0 else 0


    # Calculate average words per sentence
    # Calculate average words per sentence
    words_per_sentence = num_words / num_sentences if num_sentences > 0 else 0
    words_per_sentence = num_words / num_sentences if num_sentences > 0 else 0


    # Formula: 4.71 * (chars / words) + 0.5 * (words / sentences) - 21.43
    # Formula: 4.71 * (chars / words) + 0.5 * (words / sentences) - 21.43
    score = (4.71 * chars_per_word) + (0.5 * words_per_sentence) - 21.43
    score = (4.71 * chars_per_word) + (0.5 * words_per_sentence) - 21.43


    # Clamp score to 0-18 range
    # Clamp score to 0-18 range
    return max(0, min(18, score))
    return max(0, min(18, score))


    def _calculate_gunning_fog(
    def _calculate_gunning_fog(
    self, avg_words_per_sentence: float, complex_word_percentage: float
    self, avg_words_per_sentence: float, complex_word_percentage: float
    ) -> float:
    ) -> float:
    """
    """
    Calculate the Gunning Fog Index for the text.
    Calculate the Gunning Fog Index for the text.


    The Gunning Fog Index algorithm measures the readability of English writing by
    The Gunning Fog Index algorithm measures the readability of English writing by
    estimating the years of formal education needed to understand the text on first
    estimating the years of formal education needed to understand the text on first
    reading. The algorithm operates as follows:
    reading. The algorithm operates as follows:


    1. Count the total number of words and sentences in the text
    1. Count the total number of words and sentences in the text
    2. Calculate the percentage of complex words (words with 3+ syllables,
    2. Calculate the percentage of complex words (words with 3+ syllables,
    excluding proper nouns, compound words, and technical jargon)
    excluding proper nouns, compound words, and technical jargon)
    3. Calculate average sentence length (ASL) = words / sentences
    3. Calculate average sentence length (ASL) = words / sentences
    4. Calculate percentage of complex words (PCW) = (complex_words / words) * 100
    4. Calculate percentage of complex words (PCW) = (complex_words / words) * 100
    5. Apply the formula: 0.4 * (ASL + PCW)
    5. Apply the formula: 0.4 * (ASL + PCW)


    Interpretation of the index:
    Interpretation of the index:
    - 6: Sixth grade reading level
    - 6: Sixth grade reading level
    - 8: Eighth grade reading level
    - 8: Eighth grade reading level
    - 10: High school sophomore
    - 10: High school sophomore
    - 12: High school senior
    - 12: High school senior
    - 14: College sophomore
    - 14: College sophomore
    - 16: College senior
    - 16: College senior
    - 18+: Graduate/Professional level
    - 18+: Graduate/Professional level


    For general audiences, a fog index of 12 or below is recommended.
    For general audiences, a fog index of 12 or below is recommended.


    Args:
    Args:
    avg_words_per_sentence: Average words per sentence
    avg_words_per_sentence: Average words per sentence
    complex_word_percentage: Percentage of complex words
    complex_word_percentage: Percentage of complex words


    Returns:
    Returns:
    Gunning Fog Index (representing years of formal education needed)
    Gunning Fog Index (representing years of formal education needed)
    """
    """
    # Formula: 0.4 * ((words / sentences) + 100 * (complex_words / words))
    # Formula: 0.4 * ((words / sentences) + 100 * (complex_words / words))
    score = 0.4 * (avg_words_per_sentence + (100 * complex_word_percentage))
    score = 0.4 * (avg_words_per_sentence + (100 * complex_word_percentage))


    # Clamp score to 0-18 range
    # Clamp score to 0-18 range
    return max(0, min(18, score))
    return max(0, min(18, score))


    def _interpret_flesch_reading_ease(self, score: float) -> str:
    def _interpret_flesch_reading_ease(self, score: float) -> str:
    """
    """
    Interpret Flesch Reading Ease score.
    Interpret Flesch Reading Ease score.


    Args:
    Args:
    score: Flesch Reading Ease score
    score: Flesch Reading Ease score


    Returns:
    Returns:
    Interpretation of the score
    Interpretation of the score
    """
    """
    if score >= 90:
    if score >= 90:
    return "Very Easy - 5th grade level"
    return "Very Easy - 5th grade level"
    elif score >= 80:
    elif score >= 80:
    return "Easy - 6th grade level"
    return "Easy - 6th grade level"
    elif score >= 70:
    elif score >= 70:
    return "Fairly Easy - 7th grade level"
    return "Fairly Easy - 7th grade level"
    elif score >= 60:
    elif score >= 60:
    return "Standard - 8th-9th grade level"
    return "Standard - 8th-9th grade level"
    elif score >= 50:
    elif score >= 50:
    return "Fairly Difficult - 10th-12th grade level"
    return "Fairly Difficult - 10th-12th grade level"
    elif score >= 30:
    elif score >= 30:
    return "Difficult - College level"
    return "Difficult - College level"
    else:
    else:
    return "Very Difficult - College graduate level"
    return "Very Difficult - College graduate level"


    def _determine_reading_level(self, flesch_reading_ease: float) -> str:
    def _determine_reading_level(self, flesch_reading_ease: float) -> str:
    """
    """
    Determine reading level based on Flesch Reading Ease score.
    Determine reading level based on Flesch Reading Ease score.


    Args:
    Args:
    flesch_reading_ease: Flesch Reading Ease score
    flesch_reading_ease: Flesch Reading Ease score


    Returns:
    Returns:
    Reading level (beginner, intermediate, advanced)
    Reading level (beginner, intermediate, advanced)
    """
    """
    if flesch_reading_ease >= 80:
    if flesch_reading_ease >= 80:
    return "beginner"
    return "beginner"
    elif flesch_reading_ease >= 50:
    elif flesch_reading_ease >= 50:
    return "intermediate"
    return "intermediate"
    else:
    else:
    return "advanced"
    return "advanced"


    def _determine_grade_level(self, grade_scores: List[float]) -> float:
    def _determine_grade_level(self, grade_scores: List[float]) -> float:
    """
    """
    Determine average grade level from multiple readability scores.
    Determine average grade level from multiple readability scores.


    Args:
    Args:
    grade_scores: List of grade level scores
    grade_scores: List of grade level scores


    Returns:
    Returns:
    Average grade level
    Average grade level
    """
    """
    # Calculate average grade level
    # Calculate average grade level
    avg_grade = sum(grade_scores) / len(grade_scores) if grade_scores else 0
    avg_grade = sum(grade_scores) / len(grade_scores) if grade_scores else 0


    # Round to nearest 0.5
    # Round to nearest 0.5
    return round(avg_grade * 2) / 2
    return round(avg_grade * 2) / 2


    def _analyze_sentence_structure(self, text: str) -> Dict[str, Any]:
    def _analyze_sentence_structure(self, text: str) -> Dict[str, Any]:
    """
    """
    Analyze sentence structure.
    Analyze sentence structure.


    Args:
    Args:
    text: Text to analyze
    text: Text to analyze


    Returns:
    Returns:
    Dictionary with sentence structure analysis
    Dictionary with sentence structure analysis
    """
    """
    # Get sentences
    # Get sentences
    sentences = self._get_sentences(text)
    sentences = self._get_sentences(text)


    # Calculate sentence lengths
    # Calculate sentence lengths
    sentence_lengths = [len(self._get_words(sentence)) for sentence in sentences]
    sentence_lengths = [len(self._get_words(sentence)) for sentence in sentences]


    # Calculate sentence length statistics
    # Calculate sentence length statistics
    min_length = min(sentence_lengths) if sentence_lengths else 0
    min_length = min(sentence_lengths) if sentence_lengths else 0
    max_length = max(sentence_lengths) if sentence_lengths else 0
    max_length = max(sentence_lengths) if sentence_lengths else 0
    avg_length = (
    avg_length = (
    sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
    sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
    )
    )


    # Count sentences by length
    # Count sentences by length
    short_sentences = sum(
    short_sentences = sum(
    1
    1
    for length in sentence_lengths
    for length in sentence_lengths
    if length < self.config["min_sentence_length"]
    if length < self.config["min_sentence_length"]
    )
    )
    long_sentences = sum(
    long_sentences = sum(
    1
    1
    for length in sentence_lengths
    for length in sentence_lengths
    if length > self.config["max_sentence_length"]
    if length > self.config["max_sentence_length"]
    )
    )
    optimal_sentences = sum(
    optimal_sentences = sum(
    1
    1
    for length in sentence_lengths
    for length in sentence_lengths
    if self.config["min_sentence_length"]
    if self.config["min_sentence_length"]
    <= length
    <= length
    <= self.config["max_sentence_length"]
    <= self.config["max_sentence_length"]
    )
    )


    # Calculate percentages
    # Calculate percentages
    short_sentence_percentage = short_sentences / len(sentences) if sentences else 0
    short_sentence_percentage = short_sentences / len(sentences) if sentences else 0
    long_sentence_percentage = long_sentences / len(sentences) if sentences else 0
    long_sentence_percentage = long_sentences / len(sentences) if sentences else 0
    optimal_sentence_percentage = (
    optimal_sentence_percentage = (
    optimal_sentences / len(sentences) if sentences else 0
    optimal_sentences / len(sentences) if sentences else 0
    )
    )


    # Analyze sentence beginnings
    # Analyze sentence beginnings
    sentence_beginnings = self._analyze_sentence_beginnings(sentences)
    sentence_beginnings = self._analyze_sentence_beginnings(sentences)


    # Analyze sentence variety
    # Analyze sentence variety
    sentence_variety = self._analyze_sentence_variety(sentences)
    sentence_variety = self._analyze_sentence_variety(sentences)


    # Analyze transition words
    # Analyze transition words
    transition_words = self._analyze_transition_words(sentences)
    transition_words = self._analyze_transition_words(sentences)


    return {
    return {
    "sentence_count": len(sentences),
    "sentence_count": len(sentences),
    "sentence_length": {
    "sentence_length": {
    "min": min_length,
    "min": min_length,
    "max": max_length,
    "max": max_length,
    "avg": avg_length,
    "avg": avg_length,
    "short_count": short_sentences,
    "short_count": short_sentences,
    "long_count": long_sentences,
    "long_count": long_sentences,
    "optimal_count": optimal_sentences,
    "optimal_count": optimal_sentences,
    "short_percentage": short_sentence_percentage,
    "short_percentage": short_sentence_percentage,
    "long_percentage": long_sentence_percentage,
    "long_percentage": long_sentence_percentage,
    "optimal_percentage": optimal_sentence_percentage,
    "optimal_percentage": optimal_sentence_percentage,
    "is_optimal": long_sentence_percentage <= 0.2
    "is_optimal": long_sentence_percentage <= 0.2
    and short_sentence_percentage <= 0.1,
    and short_sentence_percentage <= 0.1,
    },
    },
    "sentence_beginnings": sentence_beginnings,
    "sentence_beginnings": sentence_beginnings,
    "sentence_variety": sentence_variety,
    "sentence_variety": sentence_variety,
    "transition_words": transition_words,
    "transition_words": transition_words,
    }
    }


    def _analyze_sentence_beginnings(self, sentences: List[str]) -> Dict[str, Any]:
    def _analyze_sentence_beginnings(self, sentences: List[str]) -> Dict[str, Any]:
    """
    """
    Analyze sentence beginnings.
    Analyze sentence beginnings.


    Args:
    Args:
    sentences: List of sentences
    sentences: List of sentences


    Returns:
    Returns:
    Dictionary with sentence beginnings analysis
    Dictionary with sentence beginnings analysis
    """
    """
    if not sentences:
    if not sentences:
    return {
    return {
    "unique_beginnings_count": 0,
    "unique_beginnings_count": 0,
    "unique_beginnings_percentage": 0,
    "unique_beginnings_percentage": 0,
    "common_beginnings": {},
    "common_beginnings": {},
    "is_optimal": False,
    "is_optimal": False,
    }
    }


    # Get first word of each sentence
    # Get first word of each sentence
    first_words = []
    first_words = []


    for sentence in sentences:
    for sentence in sentences:
    words = self._get_words(sentence)
    words = self._get_words(sentence)
    if words:
    if words:
    first_words.append(words[0].lower())
    first_words.append(words[0].lower())


    # Count occurrences of each first word
    # Count occurrences of each first word
    first_word_counts = Counter(first_words)
    first_word_counts = Counter(first_words)


    # Get most common first words
    # Get most common first words
    most_common = first_word_counts.most_common(5)
    most_common = first_word_counts.most_common(5)


    # Calculate unique beginnings
    # Calculate unique beginnings
    unique_beginnings = len(first_word_counts)
    unique_beginnings = len(first_word_counts)
    unique_beginnings_percentage = (
    unique_beginnings_percentage = (
    unique_beginnings / len(sentences) if sentences else 0
    unique_beginnings / len(sentences) if sentences else 0
    )
    )


    return {
    return {
    "unique_beginnings_count": unique_beginnings,
    "unique_beginnings_count": unique_beginnings,
    "unique_beginnings_percentage": unique_beginnings_percentage,
    "unique_beginnings_percentage": unique_beginnings_percentage,
    "common_beginnings": {word: count for word, count in most_common},
    "common_beginnings": {word: count for word, count in most_common},
    "is_optimal": unique_beginnings_percentage >= 0.7,
    "is_optimal": unique_beginnings_percentage >= 0.7,
    }
    }


    def _analyze_sentence_variety(self, sentences: List[str]) -> Dict[str, Any]:
    def _analyze_sentence_variety(self, sentences: List[str]) -> Dict[str, Any]:
    """
    """
    Analyze sentence variety.
    Analyze sentence variety.


    Args:
    Args:
    sentences: List of sentences
    sentences: List of sentences


    Returns:
    Returns:
    Dictionary with sentence variety analysis
    Dictionary with sentence variety analysis
    """
    """
    if not sentences:
    if not sentences:
    return {"length_variety": 0, "is_optimal": False}
    return {"length_variety": 0, "is_optimal": False}


    # Calculate sentence lengths
    # Calculate sentence lengths
    sentence_lengths = [len(self._get_words(sentence)) for sentence in sentences]
    sentence_lengths = [len(self._get_words(sentence)) for sentence in sentences]


    # Calculate standard deviation of sentence lengths
    # Calculate standard deviation of sentence lengths
    mean_length = sum(sentence_lengths) / len(sentence_lengths)
    mean_length = sum(sentence_lengths) / len(sentence_lengths)
    variance = sum(
    variance = sum(
    (length - mean_length) ** 2 for length in sentence_lengths
    (length - mean_length) ** 2 for length in sentence_lengths
    ) / len(sentence_lengths)
    ) / len(sentence_lengths)
    std_dev = math.sqrt(variance)
    std_dev = math.sqrt(variance)


    # Calculate coefficient of variation (normalized standard deviation)
    # Calculate coefficient of variation (normalized standard deviation)
    cv = std_dev / mean_length if mean_length > 0 else 0
    cv = std_dev / mean_length if mean_length > 0 else 0


    # Determine if variety is optimal
    # Determine if variety is optimal
    is_optimal = cv >= 0.2
    is_optimal = cv >= 0.2


    return {"length_variety": cv, "is_optimal": is_optimal}
    return {"length_variety": cv, "is_optimal": is_optimal}


    def _analyze_transition_words(self, sentences: List[str]) -> Dict[str, Any]:
    def _analyze_transition_words(self, sentences: List[str]) -> Dict[str, Any]:
    """
    """
    Analyze transition words in sentences.
    Analyze transition words in sentences.


    Args:
    Args:
    sentences: List of sentences
    sentences: List of sentences


    Returns:
    Returns:
    Dictionary with transition words analysis
    Dictionary with transition words analysis
    """
    """
    # Common transition words
    # Common transition words
    transition_words = [
    transition_words = [
    "additionally",
    "additionally",
    "also",
    "also",
    "furthermore",
    "furthermore",
    "moreover",
    "moreover",
    "in addition",
    "in addition",
    "similarly",
    "similarly",
    "likewise",
    "likewise",
    "in the same way",
    "in the same way",
    "equally",
    "equally",
    "however",
    "however",
    "but",
    "but",
    "yet",
    "yet",
    "nevertheless",
    "nevertheless",
    "nonetheless",
    "nonetheless",
    "on the other hand",
    "on the other hand",
    "in contrast",
    "in contrast",
    "conversely",
    "conversely",
    "instead",
    "instead",
    "alternatively",
    "alternatively",
    "therefore",
    "therefore",
    "thus",
    "thus",
    "consequently",
    "consequently",
    "as a result",
    "as a result",
    "hence",
    "hence",
    "for example",
    "for example",
    "for instance",
    "for instance",
    "specifically",
    "specifically",
    "namely",
    "namely",
    "to illustrate",
    "to illustrate",
    "in fact",
    "in fact",
    "indeed",
    "indeed",
    "actually",
    "actually",
    "to clarify",
    "to clarify",
    "in other words",
    "in other words",
    "first",
    "first",
    "second",
    "second",
    "third",
    "third",
    "next",
    "next",
    "then",
    "then",
    "finally",
    "finally",
    "lastly",
    "lastly",
    "in conclusion",
    "in conclusion",
    "to summarize",
    "to summarize",
    "in summary",
    "in summary",
    "to conclude",
    "to conclude",
    ]
    ]


    # Count sentences with transition words
    # Count sentences with transition words
    sentences_with_transitions = 0
    sentences_with_transitions = 0
    transition_word_counts = Counter()
    transition_word_counts = Counter()


    for sentence in sentences:
    for sentence in sentences:
    has_transition = False
    has_transition = False


    for word in transition_words:
    for word in transition_words:
    if word in sentence.lower():
    if word in sentence.lower():
    has_transition = True
    has_transition = True
    transition_word_counts[word] += 1
    transition_word_counts[word] += 1


    if has_transition:
    if has_transition:
    sentences_with_transitions += 1
    sentences_with_transitions += 1


    # Calculate percentage of sentences with transition words
    # Calculate percentage of sentences with transition words
    transition_percentage = (
    transition_percentage = (
    sentences_with_transitions / len(sentences) if sentences else 0
    sentences_with_transitions / len(sentences) if sentences else 0
    )
    )


    # Get most common transition words
    # Get most common transition words
    most_common = transition_word_counts.most_common(5)
    most_common = transition_word_counts.most_common(5)


    return {
    return {
    "sentences_with_transitions": sentences_with_transitions,
    "sentences_with_transitions": sentences_with_transitions,
    "transition_percentage": transition_percentage,
    "transition_percentage": transition_percentage,
    "common_transitions": {word: count for word, count in most_common},
    "common_transitions": {word: count for word, count in most_common},
    "is_optimal": transition_percentage >= 0.3,
    "is_optimal": transition_percentage >= 0.3,
    }
    }


    def _analyze_paragraph_structure(self, text: str) -> Dict[str, Any]:
    def _analyze_paragraph_structure(self, text: str) -> Dict[str, Any]:
    """
    """
    Analyze paragraph structure.
    Analyze paragraph structure.


    Args:
    Args:
    text: Text to analyze
    text: Text to analyze


    Returns:
    Returns:
    Dictionary with paragraph structure analysis
    Dictionary with paragraph structure analysis
    """
    """
    # Get paragraphs
    # Get paragraphs
    paragraphs = self._get_paragraphs(text)
    paragraphs = self._get_paragraphs(text)


    # Calculate paragraph lengths
    # Calculate paragraph lengths
    paragraph_lengths = [
    paragraph_lengths = [
    len(self._get_words(paragraph)) for paragraph in paragraphs
    len(self._get_words(paragraph)) for paragraph in paragraphs
    ]
    ]


    # Calculate paragraph length statistics
    # Calculate paragraph length statistics
    min_length = min(paragraph_lengths) if paragraph_lengths else 0
    min_length = min(paragraph_lengths) if paragraph_lengths else 0
    max_length = max(paragraph_lengths) if paragraph_lengths else 0
    max_length = max(paragraph_lengths) if paragraph_lengths else 0
    avg_length = (
    avg_length = (
    sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
    sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
    )
    )


    # Count paragraphs by length
    # Count paragraphs by length
    short_paragraphs = sum(
    short_paragraphs = sum(
    1
    1
    for length in paragraph_lengths
    for length in paragraph_lengths
    if length < self.config["min_paragraph_length"]
    if length < self.config["min_paragraph_length"]
    )
    )
    long_paragraphs = sum(
    long_paragraphs = sum(
    1
    1
    for length in paragraph_lengths
    for length in paragraph_lengths
    if length > self.config["max_paragraph_length"]
    if length > self.config["max_paragraph_length"]
    )
    )
    optimal_paragraphs = sum(
    optimal_paragraphs = sum(
    1
    1
    for length in paragraph_lengths
    for length in paragraph_lengths
    if self.config["min_paragraph_length"]
    if self.config["min_paragraph_length"]
    <= length
    <= length
    <= self.config["max_paragraph_length"]
    <= self.config["max_paragraph_length"]
    )
    )


    # Calculate percentages
    # Calculate percentages
    short_paragraph_percentage = (
    short_paragraph_percentage = (
    short_paragraphs / len(paragraphs) if paragraphs else 0
    short_paragraphs / len(paragraphs) if paragraphs else 0
    )
    )
    long_paragraph_percentage = (
    long_paragraph_percentage = (
    long_paragraphs / len(paragraphs) if paragraphs else 0
    long_paragraphs / len(paragraphs) if paragraphs else 0
    )
    )
    optimal_paragraph_percentage = (
    optimal_paragraph_percentage = (
    optimal_paragraphs / len(paragraphs) if paragraphs else 0
    optimal_paragraphs / len(paragraphs) if paragraphs else 0
    )
    )


    # Analyze paragraph variety
    # Analyze paragraph variety
    paragraph_variety = self._analyze_paragraph_variety(paragraphs)
    paragraph_variety = self._analyze_paragraph_variety(paragraphs)


    return {
    return {
    "paragraph_count": len(paragraphs),
    "paragraph_count": len(paragraphs),
    "paragraph_length": {
    "paragraph_length": {
    "min": min_length,
    "min": min_length,
    "max": max_length,
    "max": max_length,
    "avg": avg_length,
    "avg": avg_length,
    "short_count": short_paragraphs,
    "short_count": short_paragraphs,
    "long_count": long_paragraphs,
    "long_count": long_paragraphs,
    "optimal_count": optimal_paragraphs,
    "optimal_count": optimal_paragraphs,
    "short_percentage": short_paragraph_percentage,
    "short_percentage": short_paragraph_percentage,
    "long_percentage": long_paragraph_percentage,
    "long_percentage": long_paragraph_percentage,
    "optimal_percentage": optimal_paragraph_percentage,
    "optimal_percentage": optimal_paragraph_percentage,
    "is_optimal": long_paragraph_percentage <= 0.2
    "is_optimal": long_paragraph_percentage <= 0.2
    and short_paragraph_percentage <= 0.1,
    and short_paragraph_percentage <= 0.1,
    },
    },
    "paragraph_variety": paragraph_variety,
    "paragraph_variety": paragraph_variety,
    }
    }


    def _analyze_paragraph_variety(self, paragraphs: List[str]) -> Dict[str, Any]:
    def _analyze_paragraph_variety(self, paragraphs: List[str]) -> Dict[str, Any]:
    """
    """
    Analyze paragraph variety.
    Analyze paragraph variety.


    Args:
    Args:
    paragraphs: List of paragraphs
    paragraphs: List of paragraphs


    Returns:
    Returns:
    Dictionary with paragraph variety analysis
    Dictionary with paragraph variety analysis
    """
    """
    if not paragraphs:
    if not paragraphs:
    return {"length_variety": 0, "is_optimal": False}
    return {"length_variety": 0, "is_optimal": False}


    # Calculate paragraph lengths
    # Calculate paragraph lengths
    paragraph_lengths = [
    paragraph_lengths = [
    len(self._get_words(paragraph)) for paragraph in paragraphs
    len(self._get_words(paragraph)) for paragraph in paragraphs
    ]
    ]


    # Calculate standard deviation of paragraph lengths
    # Calculate standard deviation of paragraph lengths
    mean_length = sum(paragraph_lengths) / len(paragraph_lengths)
    mean_length = sum(paragraph_lengths) / len(paragraph_lengths)
    variance = sum(
    variance = sum(
    (length - mean_length) ** 2 for length in paragraph_lengths
    (length - mean_length) ** 2 for length in paragraph_lengths
    ) / len(paragraph_lengths)
    ) / len(paragraph_lengths)
    std_dev = math.sqrt(variance)
    std_dev = math.sqrt(variance)


    # Calculate coefficient of variation (normalized standard deviation)
    # Calculate coefficient of variation (normalized standard deviation)
    cv = std_dev / mean_length if mean_length > 0 else 0
    cv = std_dev / mean_length if mean_length > 0 else 0


    # Determine if variety is optimal
    # Determine if variety is optimal
    is_optimal = cv >= 0.2
    is_optimal = cv >= 0.2


    return {"length_variety": cv, "is_optimal": is_optimal}
    return {"length_variety": cv, "is_optimal": is_optimal}


    def _analyze_writing_style(self, text: str) -> Dict[str, Any]:
    def _analyze_writing_style(self, text: str) -> Dict[str, Any]:
    """
    """
    Analyze writing style.
    Analyze writing style.


    Args:
    Args:
    text: Text to analyze
    text: Text to analyze


    Returns:
    Returns:
    Dictionary with writing style analysis
    Dictionary with writing style analysis
    """
    """
    # Analyze passive voice
    # Analyze passive voice
    passive_voice = self._analyze_passive_voice(text)
    passive_voice = self._analyze_passive_voice(text)


    # Analyze adverb usage
    # Analyze adverb usage
    adverb_usage = self._analyze_adverb_usage(text)
    adverb_usage = self._analyze_adverb_usage(text)


    # Analyze complex words
    # Analyze complex words
    complex_words = self._analyze_complex_words(text)
    complex_words = self._analyze_complex_words(text)


    return {
    return {
    "passive_voice": passive_voice,
    "passive_voice": passive_voice,
    "adverb_usage": adverb_usage,
    "adverb_usage": adverb_usage,
    "complex_words": complex_words,
    "complex_words": complex_words,
    }
    }


    def _analyze_passive_voice(self, text: str) -> Dict[str, Any]:
    def _analyze_passive_voice(self, text: str) -> Dict[str, Any]:
    """
    """
    Analyze passive voice usage.
    Analyze passive voice usage.


    Args:
    Args:
    text: Text to analyze
    text: Text to analyze


    Returns:
    Returns:
    Dictionary with passive voice analysis
    Dictionary with passive voice analysis
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


    # Count passive voice instances
    # Count passive voice instances
    passive_count = 0
    passive_count = 0


    for pattern in passive_patterns:
    for pattern in passive_patterns:
    passive_count += len(re.findall(pattern, text, re.IGNORECASE))
    passive_count += len(re.findall(pattern, text, re.IGNORECASE))


    # Get sentences
    # Get sentences
    sentences = self._get_sentences(text)
    sentences = self._get_sentences(text)


    # Calculate passive voice percentage
    # Calculate passive voice percentage
    passive_percentage = passive_count / len(sentences) if sentences else 0
    passive_percentage = passive_count / len(sentences) if sentences else 0


    # Determine if passive voice usage is optimal
    # Determine if passive voice usage is optimal
    is_optimal = passive_percentage <= self.config["max_passive_voice_percentage"]
    is_optimal = passive_percentage <= self.config["max_passive_voice_percentage"]


    return {
    return {
    "passive_count": passive_count,
    "passive_count": passive_count,
    "passive_percentage": passive_percentage,
    "passive_percentage": passive_percentage,
    "is_optimal": is_optimal,
    "is_optimal": is_optimal,
    }
    }


    def _analyze_adverb_usage(self, text: str) -> Dict[str, Any]:
    def _analyze_adverb_usage(self, text: str) -> Dict[str, Any]:
    """
    """
    Analyze adverb usage.
    Analyze adverb usage.


    Args:
    Args:
    text: Text to analyze
    text: Text to analyze


    Returns:
    Returns:
    Dictionary with adverb usage analysis
    Dictionary with adverb usage analysis
    """
    """
    # Simple adverb detection pattern (words ending in 'ly')
    # Simple adverb detection pattern (words ending in 'ly')
    adverb_pattern = r"\b\w+ly\b"
    adverb_pattern = r"\b\w+ly\b"


    # Find adverbs
    # Find adverbs
    adverbs = re.findall(adverb_pattern, text, re.IGNORECASE)
    adverbs = re.findall(adverb_pattern, text, re.IGNORECASE)


    # Count adverbs
    # Count adverbs
    adverb_count = len(adverbs)
    adverb_count = len(adverbs)


    # Get words
    # Get words
    words = self._get_words(text)
    words = self._get_words(text)


    # Calculate adverb percentage
    # Calculate adverb percentage
    adverb_percentage = adverb_count / len(words) if words else 0
    adverb_percentage = adverb_count / len(words) if words else 0


    # Determine if adverb usage is optimal
    # Determine if adverb usage is optimal
    is_optimal = adverb_percentage <= 0.05
    is_optimal = adverb_percentage <= 0.05


    # Count adverb occurrences
    # Count adverb occurrences
    adverb_counts = Counter(adverb.lower() for adverb in adverbs)
    adverb_counts = Counter(adverb.lower() for adverb in adverbs)


    # Get most common adverbs
    # Get most common adverbs
    most_common = adverb_counts.most_common(5)
    most_common = adverb_counts.most_common(5)


    return {
    return {
    "adverb_count": adverb_count,
    "adverb_count": adverb_count,
    "adverb_percentage": adverb_percentage,
    "adverb_percentage": adverb_percentage,
    "common_adverbs": {word: count for word, count in most_common},
    "common_adverbs": {word: count for word, count in most_common},
    "is_optimal": is_optimal,
    "is_optimal": is_optimal,
    }
    }


    def _analyze_complex_words(self, text: str) -> Dict[str, Any]:
    def _analyze_complex_words(self, text: str) -> Dict[str, Any]:
    """
    """
    Analyze complex word usage.
    Analyze complex word usage.


    Args:
    Args:
    text: Text to analyze
    text: Text to analyze


    Returns:
    Returns:
    Dictionary with complex word analysis
    Dictionary with complex word analysis
    """
    """
    # Get words
    # Get words
    words = self._get_words(text)
    words = self._get_words(text)


    # Find complex words (words with 3+ syllables)
    # Find complex words (words with 3+ syllables)
    complex_words = [
    complex_words = [
    word for word in words if self._count_syllables_in_word(word) >= 3
    word for word in words if self._count_syllables_in_word(word) >= 3
    ]
    ]


    # Count complex words
    # Count complex words
    complex_word_count = len(complex_words)
    complex_word_count = len(complex_words)


    # Calculate complex word percentage
    # Calculate complex word percentage
    complex_word_percentage = complex_word_count / len(words) if words else 0
    complex_word_percentage = complex_word_count / len(words) if words else 0


    # Determine if complex word usage is optimal
    # Determine if complex word usage is optimal
    is_optimal = (
    is_optimal = (
    complex_word_percentage <= self.config["max_complex_word_percentage"]
    complex_word_percentage <= self.config["max_complex_word_percentage"]
    )
    )


    # Count complex word occurrences
    # Count complex word occurrences
    complex_word_counts = Counter(word.lower() for word in complex_words)
    complex_word_counts = Counter(word.lower() for word in complex_words)


    # Get most common complex words
    # Get most common complex words
    most_common = complex_word_counts.most_common(5)
    most_common = complex_word_counts.most_common(5)


    return {
    return {
    "complex_word_count": complex_word_count,
    "complex_word_count": complex_word_count,
    "complex_word_percentage": complex_word_percentage,
    "complex_word_percentage": complex_word_percentage,
    "common_complex_words": {word: count for word, count in most_common},
    "common_complex_words": {word: count for word, count in most_common},
    "is_optimal": is_optimal,
    "is_optimal": is_optimal,
    }
    }


    def get_score(self) -> float:
    def get_score(self) -> float:
    """
    """
    Get the overall readability score for the content.
    Get the overall readability score for the content.


    Returns:
    Returns:
    Readability score between 0 and 1
    Readability score between 0 and 1
    """
    """
    if self.results is None:
    if self.results is None:
    self.analyze()
    self.analyze()


    # Calculate readability score
    # Calculate readability score
    readability_score = 0.0
    readability_score = 0.0


    # Score based on Flesch Reading Ease
    # Score based on Flesch Reading Ease
    if self.results["readability_scores"]["flesch_reading_ease"]["is_optimal"]:
    if self.results["readability_scores"]["flesch_reading_ease"]["is_optimal"]:
    readability_score += 0.2
    readability_score += 0.2
    else:
    else:
    # Calculate partial score based on how close to optimal
    # Calculate partial score based on how close to optimal
    flesch_score = self.results["readability_scores"]["flesch_reading_ease"][
    flesch_score = self.results["readability_scores"]["flesch_reading_ease"][
    "score"
    "score"
    ]
    ]
    min_flesch = self.config["min_flesch_reading_ease"]
    min_flesch = self.config["min_flesch_reading_ease"]
    readability_score += (
    readability_score += (
    0.2 * (flesch_score / min_flesch) if min_flesch > 0 else 0
    0.2 * (flesch_score / min_flesch) if min_flesch > 0 else 0
    )
    )


    # Score based on grade level
    # Score based on grade level
    target_grade = self.config["max_flesch_kincaid_grade"]
    target_grade = self.config["max_flesch_kincaid_grade"]
    actual_grade = self.results["readability_scores"]["grade_level"]
    actual_grade = self.results["readability_scores"]["grade_level"]


    if actual_grade <= target_grade:
    if actual_grade <= target_grade:
    readability_score += 0.2
    readability_score += 0.2
    else:
    else:
    # Calculate partial score based on how close to target
    # Calculate partial score based on how close to target
    readability_score += (
    readability_score += (
    0.2 * (target_grade / actual_grade) if actual_grade > 0 else 0
    0.2 * (target_grade / actual_grade) if actual_grade > 0 else 0
    )
    )


    # Score based on sentence structure
    # Score based on sentence structure
    sentence_score = 0.0
    sentence_score = 0.0


    if self.results["sentence_analysis"]["sentence_length"]["is_optimal"]:
    if self.results["sentence_analysis"]["sentence_length"]["is_optimal"]:
    sentence_score += 0.33
    sentence_score += 0.33


    if self.results["sentence_analysis"]["sentence_beginnings"]["is_optimal"]:
    if self.results["sentence_analysis"]["sentence_beginnings"]["is_optimal"]:
    sentence_score += 0.33
    sentence_score += 0.33


    if self.results["sentence_analysis"]["sentence_variety"]["is_optimal"]:
    if self.results["sentence_analysis"]["sentence_variety"]["is_optimal"]:
    sentence_score += 0.34
    sentence_score += 0.34


    readability_score += 0.2 * sentence_score
    readability_score += 0.2 * sentence_score


    # Score based on paragraph structure
    # Score based on paragraph structure
    paragraph_score = 0.0
    paragraph_score = 0.0


    if self.results["paragraph_analysis"]["paragraph_length"]["is_optimal"]:
    if self.results["paragraph_analysis"]["paragraph_length"]["is_optimal"]:
    paragraph_score += 0.5
    paragraph_score += 0.5


    if self.results["paragraph_analysis"]["paragraph_variety"]["is_optimal"]:
    if self.results["paragraph_analysis"]["paragraph_variety"]["is_optimal"]:
    paragraph_score += 0.5
    paragraph_score += 0.5


    readability_score += 0.2 * paragraph_score
    readability_score += 0.2 * paragraph_score


    # Score based on writing style
    # Score based on writing style
    style_score = 0.0
    style_score = 0.0


    if self.results["style_analysis"]["passive_voice"]["is_optimal"]:
    if self.results["style_analysis"]["passive_voice"]["is_optimal"]:
    style_score += 0.33
    style_score += 0.33


    if self.results["style_analysis"]["adverb_usage"]["is_optimal"]:
    if self.results["style_analysis"]["adverb_usage"]["is_optimal"]:
    style_score += 0.33
    style_score += 0.33


    if self.results["style_analysis"]["complex_words"]["is_optimal"]:
    if self.results["style_analysis"]["complex_words"]["is_optimal"]:
    style_score += 0.34
    style_score += 0.34


    readability_score += 0.2 * style_score
    readability_score += 0.2 * style_score


    return readability_score
    return readability_score


    def get_recommendations(self) -> List[Dict[str, Any]]:
    def get_recommendations(self) -> List[Dict[str, Any]]:
    """
    """
    Get readability recommendations for the content.
    Get readability recommendations for the content.


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


    # Check Flesch Reading Ease
    # Check Flesch Reading Ease
    flesch_score = self.results["readability_scores"]["flesch_reading_ease"][
    flesch_score = self.results["readability_scores"]["flesch_reading_ease"][
    "score"
    "score"
    ]
    ]
    min_flesch = self.config["min_flesch_reading_ease"]
    min_flesch = self.config["min_flesch_reading_ease"]


    if flesch_score < min_flesch:
    if flesch_score < min_flesch:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "readability_score",
    "type": "readability_score",
    "severity": "high",
    "severity": "high",
    "message": f"Flesch Reading Ease score ({flesch_score:.1f}) is below the recommended minimum ({min_flesch:.1f}).",
    "message": f"Flesch Reading Ease score ({flesch_score:.1f}) is below the recommended minimum ({min_flesch:.1f}).",
    "suggestion": "Use shorter sentences and simpler words to improve readability.",
    "suggestion": "Use shorter sentences and simpler words to improve readability.",
    }
    }
    )
    )


    # Check grade level
    # Check grade level
    grade_level = self.results["readability_scores"]["grade_level"]
    grade_level = self.results["readability_scores"]["grade_level"]
    max_grade = self.config["max_flesch_kincaid_grade"]
    max_grade = self.config["max_flesch_kincaid_grade"]


    if grade_level > max_grade:
    if grade_level > max_grade:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "grade_level",
    "type": "grade_level",
    "severity": "medium",
    "severity": "medium",
    "message": f"Content grade level ({grade_level:.1f}) is above the recommended maximum ({max_grade:.1f}).",
    "message": f"Content grade level ({grade_level:.1f}) is above the recommended maximum ({max_grade:.1f}).",
    "suggestion": "Simplify language and sentence structure to lower the grade level.",
    "suggestion": "Simplify language and sentence structure to lower the grade level.",
    }
    }
    )
    )


    # Check sentence length
    # Check sentence length
    avg_sentence_length = self.results["sentence_analysis"]["sentence_length"][
    avg_sentence_length = self.results["sentence_analysis"]["sentence_length"][
    "avg"
    "avg"
    ]
    ]
    max_sentence_length = self.config["max_sentence_length"]
    max_sentence_length = self.config["max_sentence_length"]
    long_sentence_percentage = self.results["sentence_analysis"]["sentence_length"][
    long_sentence_percentage = self.results["sentence_analysis"]["sentence_length"][
    "long_percentage"
    "long_percentage"
    ]
    ]
    is_sentence_length_optimal = self.results["sentence_analysis"][
    is_sentence_length_optimal = self.results["sentence_analysis"][
    "sentence_length"
    "sentence_length"
    ]["is_optimal"]
    ]["is_optimal"]


    if not is_sentence_length_optimal:
    if not is_sentence_length_optimal:
    # Always add a recommendation if sentence length is not optimal
    # Always add a recommendation if sentence length is not optimal
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "sentence_length",
    "type": "sentence_length",
    "severity": "medium",
    "severity": "medium",
    "message": f"Sentence length distribution is not optimal. Average length: {avg_sentence_length:.1f} words, Maximum recommended: {max_sentence_length} words.",
    "message": f"Sentence length distribution is not optimal. Average length: {avg_sentence_length:.1f} words, Maximum recommended: {max_sentence_length} words.",
    "suggestion": "Aim for a better mix of sentence lengths. Break longer sentences into shorter ones to improve readability.",
    "suggestion": "Aim for a better mix of sentence lengths. Break longer sentences into shorter ones to improve readability.",
    }
    }
    )
    )
    elif avg_sentence_length > max_sentence_length * 0.8:
    elif avg_sentence_length > max_sentence_length * 0.8:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "sentence_length",
    "type": "sentence_length",
    "severity": "medium",
    "severity": "medium",
    "message": f"Average sentence length ({avg_sentence_length:.1f} words) is approaching the maximum recommended length ({max_sentence_length} words).",
    "message": f"Average sentence length ({avg_sentence_length:.1f} words) is approaching the maximum recommended length ({max_sentence_length} words).",
    "suggestion": "Break longer sentences into shorter ones to improve readability.",
    "suggestion": "Break longer sentences into shorter ones to improve readability.",
    }
    }
    )
    )


    if long_sentence_percentage > 0.2:
    if long_sentence_percentage > 0.2:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "sentence_length",
    "type": "sentence_length",
    "severity": "medium",
    "severity": "medium",
    "message": f"{long_sentence_percentage:.1%} of sentences are longer than the recommended maximum ({max_sentence_length} words).",
    "message": f"{long_sentence_percentage:.1%} of sentences are longer than the recommended maximum ({max_sentence_length} words).",
    "suggestion": "Identify and break up long sentences to improve readability.",
    "suggestion": "Identify and break up long sentences to improve readability.",
    }
    }
    )
    )


    # Check sentence beginnings
    # Check sentence beginnings
    unique_beginnings_percentage = self.results["sentence_analysis"][
    unique_beginnings_percentage = self.results["sentence_analysis"][
    "sentence_beginnings"
    "sentence_beginnings"
    ]["unique_beginnings_percentage"]
    ]["unique_beginnings_percentage"]


    if unique_beginnings_percentage < 0.7:
    if unique_beginnings_percentage < 0.7:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "sentence_beginnings",
    "type": "sentence_beginnings",
    "severity": "low",
    "severity": "low",
    "message": f"Only {unique_beginnings_percentage:.1%} of sentences have unique beginnings.",
    "message": f"Only {unique_beginnings_percentage:.1%} of sentences have unique beginnings.",
    "suggestion": "Vary sentence beginnings to improve flow and engagement.",
    "suggestion": "Vary sentence beginnings to improve flow and engagement.",
    }
    }
    )
    )


    # Check transition words
    # Check transition words
    transition_percentage = self.results["sentence_analysis"]["transition_words"][
    transition_percentage = self.results["sentence_analysis"]["transition_words"][
    "transition_percentage"
    "transition_percentage"
    ]
    ]


    if transition_percentage < 0.3:
    if transition_percentage < 0.3:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "transition_words",
    "type": "transition_words",
    "severity": "low",
    "severity": "low",
    "message": f"Only {transition_percentage:.1%} of sentences contain transition words.",
    "message": f"Only {transition_percentage:.1%} of sentences contain transition words.",
    "suggestion": "Add more transition words to improve flow and coherence.",
    "suggestion": "Add more transition words to improve flow and coherence.",
    }
    }
    )
    )


    # Check paragraph length
    # Check paragraph length
    avg_paragraph_length = self.results["paragraph_analysis"]["paragraph_length"][
    avg_paragraph_length = self.results["paragraph_analysis"]["paragraph_length"][
    "avg"
    "avg"
    ]
    ]
    max_paragraph_length = self.config["max_paragraph_length"]
    max_paragraph_length = self.config["max_paragraph_length"]
    long_paragraph_percentage = self.results["paragraph_analysis"][
    long_paragraph_percentage = self.results["paragraph_analysis"][
    "paragraph_length"
    "paragraph_length"
    ]["long_percentage"]
    ]["long_percentage"]
    is_paragraph_length_optimal = self.results["paragraph_analysis"][
    is_paragraph_length_optimal = self.results["paragraph_analysis"][
    "paragraph_length"
    "paragraph_length"
    ]["is_optimal"]
    ]["is_optimal"]


    if not is_paragraph_length_optimal:
    if not is_paragraph_length_optimal:
    # Always add a recommendation if paragraph length is not optimal
    # Always add a recommendation if paragraph length is not optimal
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "paragraph_length",
    "type": "paragraph_length",
    "severity": "medium",
    "severity": "medium",
    "message": f"Paragraph length distribution is not optimal. Average length: {avg_paragraph_length:.1f} words, Maximum recommended: {max_paragraph_length} words.",
    "message": f"Paragraph length distribution is not optimal. Average length: {avg_paragraph_length:.1f} words, Maximum recommended: {max_paragraph_length} words.",
    "suggestion": "Aim for a better mix of paragraph lengths. Break longer paragraphs into shorter ones to improve readability.",
    "suggestion": "Aim for a better mix of paragraph lengths. Break longer paragraphs into shorter ones to improve readability.",
    }
    }
    )
    )
    elif avg_paragraph_length > max_paragraph_length * 0.8:
    elif avg_paragraph_length > max_paragraph_length * 0.8:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "paragraph_length",
    "type": "paragraph_length",
    "severity": "medium",
    "severity": "medium",
    "message": f"Average paragraph length ({avg_paragraph_length:.1f} words) is approaching the maximum recommended length ({max_paragraph_length} words).",
    "message": f"Average paragraph length ({avg_paragraph_length:.1f} words) is approaching the maximum recommended length ({max_paragraph_length} words).",
    "suggestion": "Break longer paragraphs into shorter ones to improve readability.",
    "suggestion": "Break longer paragraphs into shorter ones to improve readability.",
    }
    }
    )
    )


    if long_paragraph_percentage > 0.2:
    if long_paragraph_percentage > 0.2:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "paragraph_length",
    "type": "paragraph_length",
    "severity": "medium",
    "severity": "medium",
    "message": f"{long_paragraph_percentage:.1%} of paragraphs are longer than the recommended maximum ({max_paragraph_length} words).",
    "message": f"{long_paragraph_percentage:.1%} of paragraphs are longer than the recommended maximum ({max_paragraph_length} words).",
    "suggestion": "Identify and break up long paragraphs to improve readability.",
    "suggestion": "Identify and break up long paragraphs to improve readability.",
    }
    }
    )
    )


    # Check passive voice
    # Check passive voice
    passive_percentage = self.results["style_analysis"]["passive_voice"][
    passive_percentage = self.results["style_analysis"]["passive_voice"][
    "passive_percentage"
    "passive_percentage"
    ]
    ]
    max_passive = self.config["max_passive_voice_percentage"]
    max_passive = self.config["max_passive_voice_percentage"]


    if passive_percentage > max_passive:
    if passive_percentage > max_passive:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "passive_voice",
    "type": "passive_voice",
    "severity": "medium",
    "severity": "medium",
    "message": f"Passive voice usage ({passive_percentage:.1%}) exceeds the recommended maximum ({max_passive:.1%}).",
    "message": f"Passive voice usage ({passive_percentage:.1%}) exceeds the recommended maximum ({max_passive:.1%}).",
    "suggestion": "Replace passive voice with active voice to improve clarity and engagement.",
    "suggestion": "Replace passive voice with active voice to improve clarity and engagement.",
    }
    }
    )
    )


    # Check adverb usage
    # Check adverb usage
    adverb_percentage = self.results["style_analysis"]["adverb_usage"][
    adverb_percentage = self.results["style_analysis"]["adverb_usage"][
    "adverb_percentage"
    "adverb_percentage"
    ]
    ]


    if adverb_percentage > 0.05:
    if adverb_percentage > 0.05:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "adverb_usage",
    "type": "adverb_usage",
    "severity": "low",
    "severity": "low",
    "message": f"Adverb usage ({adverb_percentage:.1%}) is higher than recommended (5%).",
    "message": f"Adverb usage ({adverb_percentage:.1%}) is higher than recommended (5%).",
    "suggestion": "Replace adverbs with stronger verbs to improve clarity and impact.",
    "suggestion": "Replace adverbs with stronger verbs to improve clarity and impact.",
    }
    }
    )
    )


    # Check complex words
    # Check complex words
    complex_word_percentage = self.results["style_analysis"]["complex_words"][
    complex_word_percentage = self.results["style_analysis"]["complex_words"][
    "complex_word_percentage"
    "complex_word_percentage"
    ]
    ]
    max_complex = self.config["max_complex_word_percentage"]
    max_complex = self.config["max_complex_word_percentage"]


    if complex_word_percentage > max_complex:
    if complex_word_percentage > max_complex:
    recommendations.append(
    recommendations.append(
    {
    {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "type": "complex_words",
    "type": "complex_words",
    "severity": "medium",
    "severity": "medium",
    "message": f"Complex word usage ({complex_word_percentage:.1%}) exceeds the recommended maximum ({max_complex:.1%}).",
    "message": f"Complex word usage ({complex_word_percentage:.1%}) exceeds the recommended maximum ({max_complex:.1%}).",
    "suggestion": "Replace complex words with simpler alternatives to improve readability.",
    "suggestion": "Replace complex words with simpler alternatives to improve readability.",
    }
    }
    )
    )


    return recommendations
    return recommendations