import copy
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from common_utils import load_from_json_file, save_to_json_file, to_json
from monetization.errors import MonetizationError

from .errors import MonetizationError

error
from .errors import MonetizationError

error
from .errors import MonetizationError

error

"""
"""
Subscription Models for the pAIssive Income project.
Subscription Models for the pAIssive Income project.


This module provides classes for creating and managing different subscription models
This module provides classes for creating and managing different subscription models
for AI-powered software tools. It includes base classes and specific implementations
for AI-powered software tools. It includes base classes and specific implementations
for various subscription models like freemium, tiered, usage-based, and hybrid models.
for various subscription models like freemium, tiered, usage-based, and hybrid models.
"""
"""






(
(
FeatureNotFoundError,
FeatureNotFoundError,
TierNotFoundError,
TierNotFoundError,
ValidationError,
ValidationError,
handle_exception,
handle_exception,
)
)


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class SubscriptionModel:
    class SubscriptionModel:
    """
    """
    Base class for subscription models.
    Base class for subscription models.


    This class provides the foundation for creating and managing subscription models
    This class provides the foundation for creating and managing subscription models
    with different tiers, features, and pricing structures.
    with different tiers, features, and pricing structures.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    name: str,
    name: str,
    description: str = "",
    description: str = "",
    tiers: Optional[List[Dict[str, Any]]] = None,
    tiers: Optional[List[Dict[str, Any]]] = None,
    features: Optional[List[Dict[str, Any]]] = None,
    features: Optional[List[Dict[str, Any]]] = None,
    billing_cycles: Optional[List[str]] = None,
    billing_cycles: Optional[List[str]] = None,
    ):
    ):
    """
    """
    Initialize a subscription model.
    Initialize a subscription model.


    Args:
    Args:
    name: Name of the subscription model
    name: Name of the subscription model
    description: Description of the subscription model
    description: Description of the subscription model
    tiers: List of tier dictionaries (optional)
    tiers: List of tier dictionaries (optional)
    features: List of feature dictionaries (optional)
    features: List of feature dictionaries (optional)
    billing_cycles: List of billing cycle options (optional)
    billing_cycles: List of billing cycle options (optional)
    """
    """
    self.id = str(uuid.uuid4())
    self.id = str(uuid.uuid4())
    self.name = name
    self.name = name
    self.description = description
    self.description = description
    self.tiers = tiers or []
    self.tiers = tiers or []
    self.features = features or []
    self.features = features or []
    self.billing_cycles = billing_cycles or ["monthly", "yearly"]
    self.billing_cycles = billing_cycles or ["monthly", "yearly"]
    self.created_at = datetime.now().isoformat()
    self.created_at = datetime.now().isoformat()
    self.updated_at = self.created_at
    self.updated_at = self.created_at


    def add_tier(
    def add_tier(
    self,
    self,
    name: str,
    name: str,
    description: str = "",
    description: str = "",
    price_monthly: float = 0.0,
    price_monthly: float = 0.0,
    price_yearly: Optional[float] = None,
    price_yearly: Optional[float] = None,
    features: Optional[List[str]] = None,
    features: Optional[List[str]] = None,
    limits: Optional[Dict[str, Any]] = None,
    limits: Optional[Dict[str, Any]] = None,
    target_users: str = "",
    target_users: str = "",
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Add a new tier to the subscription model.
    Add a new tier to the subscription model.


    Args:
    Args:
    name: Name of the tier (e.g., "Basic", "Pro", "Premium")
    name: Name of the tier (e.g., "Basic", "Pro", "Premium")
    description: Description of the tier
    description: Description of the tier
    price_monthly: Monthly price for the tier
    price_monthly: Monthly price for the tier
    price_yearly: Yearly price for the tier (defaults to monthly * 10 if None)
    price_yearly: Yearly price for the tier (defaults to monthly * 10 if None)
    features: List of feature IDs included in this tier
    features: List of feature IDs included in this tier
    limits: Dictionary of usage limits for this tier
    limits: Dictionary of usage limits for this tier
    target_users: Description of target users for this tier
    target_users: Description of target users for this tier


    Returns:
    Returns:
    The newly created tier dictionary
    The newly created tier dictionary
    """
    """
    # Set default yearly price (10 months for the price of 12)
    # Set default yearly price (10 months for the price of 12)
    if price_yearly is None:
    if price_yearly is None:
    price_yearly = price_monthly * 10
    price_yearly = price_monthly * 10


    # Create the tier
    # Create the tier
    tier = {
    tier = {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": name,
    "name": name,
    "description": description,
    "description": description,
    "price_monthly": price_monthly,
    "price_monthly": price_monthly,
    "price_yearly": price_yearly,
    "price_yearly": price_yearly,
    "features": features or [],
    "features": features or [],
    "limits": limits or {},
    "limits": limits or {},
    "target_users": target_users,
    "target_users": target_users,
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    }
    }


    # Add the tier to the model
    # Add the tier to the model
    self.tiers.append(tier)
    self.tiers.append(tier)
    self.updated_at = datetime.now().isoformat()
    self.updated_at = datetime.now().isoformat()


    return tier
    return tier


    def add_feature(
    def add_feature(
    self,
    self,
    name: str,
    name: str,
    description: str = "",
    description: str = "",
    feature_type: str = "functional",
    feature_type: str = "functional",
    value_proposition: str = "",
    value_proposition: str = "",
    development_cost: str = "low",
    development_cost: str = "low",
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Add a new feature to the subscription model.
    Add a new feature to the subscription model.


    Args:
    Args:
    name: Name of the feature
    name: Name of the feature
    description: Description of the feature
    description: Description of the feature
    feature_type: Type of feature (functional, performance, support, etc.)
    feature_type: Type of feature (functional, performance, support, etc.)
    value_proposition: Value proposition of the feature
    value_proposition: Value proposition of the feature
    development_cost: Estimated development cost (low, medium, high)
    development_cost: Estimated development cost (low, medium, high)


    Returns:
    Returns:
    The newly created feature dictionary
    The newly created feature dictionary
    """
    """
    # Create the feature
    # Create the feature
    feature = {
    feature = {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "name": name,
    "name": name,
    "description": description,
    "description": description,
    "feature_type": feature_type,  # Changed from "type" to "feature_type" to match tests
    "feature_type": feature_type,  # Changed from "type" to "feature_type" to match tests
    "type": feature_type,  # Keep "type" for backward compatibility
    "type": feature_type,  # Keep "type" for backward compatibility
    "value_proposition": value_proposition,
    "value_proposition": value_proposition,
    "development_cost": development_cost,
    "development_cost": development_cost,
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    }
    }


    # Add the feature to the model
    # Add the feature to the model
    self.features.append(feature)
    self.features.append(feature)
    self.updated_at = datetime.now().isoformat()
    self.updated_at = datetime.now().isoformat()


    return feature
    return feature


    def assign_feature_to_tier(self, feature_id: str, tier_id: str) -> bool:
    def assign_feature_to_tier(self, feature_id: str, tier_id: str) -> bool:
    """
    """
    Assign a feature to a tier.
    Assign a feature to a tier.


    Args:
    Args:
    feature_id: ID of the feature to assign
    feature_id: ID of the feature to assign
    tier_id: ID of the tier to assign the feature to
    tier_id: ID of the tier to assign the feature to


    Returns:
    Returns:
    True if the feature was assigned, False otherwise
    True if the feature was assigned, False otherwise


    Raises:
    Raises:
    TierNotFoundError: If the tier ID does not exist
    TierNotFoundError: If the tier ID does not exist
    FeatureNotFoundError: If the feature ID does not exist
    FeatureNotFoundError: If the feature ID does not exist
    """
    """
    try:
    try:
    # Find the tier
    # Find the tier
    tier = next((t for t in self.tiers if t["id"] == tier_id), None)
    tier = next((t for t in self.tiers if t["id"] == tier_id), None)
    if not tier:
    if not tier:
    raise TierNotFoundError(
    raise TierNotFoundError(
    message=f"Tier with ID {tier_id} not found",
    message=f"Tier with ID {tier_id} not found",
    tier_id=tier_id,
    tier_id=tier_id,
    model_id=self.id,
    model_id=self.id,
    )
    )


    # Check if the feature exists
    # Check if the feature exists
    feature = next((f for f in self.features if f["id"] == feature_id), None)
    feature = next((f for f in self.features if f["id"] == feature_id), None)
    if not feature:
    if not feature:
    raise FeatureNotFoundError(
    raise FeatureNotFoundError(
    message=f"Feature with ID {feature_id} not found",
    message=f"Feature with ID {feature_id} not found",
    feature_id=feature_id,
    feature_id=feature_id,
    model_id=self.id,
    model_id=self.id,
    )
    )


    # Add the feature to the tier if it's not already there
    # Add the feature to the tier if it's not already there
    if feature_id not in tier["features"]:
    if feature_id not in tier["features"]:
    tier["features"].append(feature_id)
    tier["features"].append(feature_id)
    self.updated_at = datetime.now().isoformat()
    self.updated_at = datetime.now().isoformat()
    logger.info(
    logger.info(
    f"Assigned feature '{feature['name']}' to tier '{tier['name']}'"
    f"Assigned feature '{feature['name']}' to tier '{tier['name']}'"
    )
    )
    return True
    return True


    logger.debug(
    logger.debug(
    f"Feature '{feature['name']}' already assigned to tier '{tier['name']}'"
    f"Feature '{feature['name']}' already assigned to tier '{tier['name']}'"
    )
    )
    return False
    return False


except (TierNotFoundError, FeatureNotFoundError) as e:
except (TierNotFoundError, FeatureNotFoundError) as e:
    # Log the error and return False
    # Log the error and return False
    e.log(level=logging.WARNING)
    e.log(level=logging.WARNING)
    return False
    return False
except Exception as e:
except Exception as e:
    # Handle unexpected errors
    # Handle unexpected errors
    handle_exception(e, error_class=MonetizationError, reraise=False)
    handle_exception(e, error_class=MonetizationError, reraise=False)
    return False
    return False


    def get_tier_features(self, tier_id: str) -> List[Dict[str, Any]]:
    def get_tier_features(self, tier_id: str) -> List[Dict[str, Any]]:
    """
    """
    Get all features for a specific tier.
    Get all features for a specific tier.


    Args:
    Args:
    tier_id: ID of the tier
    tier_id: ID of the tier


    Returns:
    Returns:
    List of feature dictionaries for the tier
    List of feature dictionaries for the tier
    """
    """
    # Find the tier
    # Find the tier
    tier = next((t for t in self.tiers if t["id"] == tier_id), None)
    tier = next((t for t in self.tiers if t["id"] == tier_id), None)
    if not tier:
    if not tier:
    return []
    return []


    # Get the features for the tier
    # Get the features for the tier
    tier_features = []
    tier_features = []
    for feature_id in tier["features"]:
    for feature_id in tier["features"]:
    feature = next((f for f in self.features if f["id"] == feature_id), None)
    feature = next((f for f in self.features if f["id"] == feature_id), None)
    if feature:
    if feature:
    tier_features.append(feature)
    tier_features.append(feature)


    return tier_features
    return tier_features


    def update_tier_price(
    def update_tier_price(
    self,
    self,
    tier_id: str,
    tier_id: str,
    price_monthly: Optional[float] = None,
    price_monthly: Optional[float] = None,
    price_yearly: Optional[float] = None,
    price_yearly: Optional[float] = None,
    ) -> bool:
    ) -> bool:
    """
    """
    Update the price of a tier.
    Update the price of a tier.


    Args:
    Args:
    tier_id: ID of the tier to update
    tier_id: ID of the tier to update
    price_monthly: New monthly price (if None, keeps current price)
    price_monthly: New monthly price (if None, keeps current price)
    price_yearly: New yearly price (if None, keeps current price)
    price_yearly: New yearly price (if None, keeps current price)


    Returns:
    Returns:
    True if the tier was updated, False otherwise
    True if the tier was updated, False otherwise


    Raises:
    Raises:
    TierNotFoundError: If the tier ID does not exist
    TierNotFoundError: If the tier ID does not exist
    ValidationError: If the price values are invalid
    ValidationError: If the price values are invalid
    """
    """
    # Find the tier
    # Find the tier
    tier = next((t for t in self.tiers if t["id"] == tier_id), None)
    tier = next((t for t in self.tiers if t["id"] == tier_id), None)
    if not tier:
    if not tier:
    raise TierNotFoundError(
    raise TierNotFoundError(
    message=f"Tier with ID {tier_id} not found",
    message=f"Tier with ID {tier_id} not found",
    tier_id=tier_id,
    tier_id=tier_id,
    model_id=self.id,
    model_id=self.id,
    )
    )


    try:
    try:
    # Validate price values
    # Validate price values
    if price_monthly is not None and price_monthly < 0:
    if price_monthly is not None and price_monthly < 0:
    raise ValidationError(
    raise ValidationError(
    message="Monthly price cannot be negative",
    message="Monthly price cannot be negative",
    field="price_monthly",
    field="price_monthly",
    validation_errors=[
    validation_errors=[
    {
    {
    "field": "price_monthly",
    "field": "price_monthly",
    "value": price_monthly,
    "value": price_monthly,
    "error": "Price cannot be negative",
    "error": "Price cannot be negative",
    }
    }
    ],
    ],
    )
    )


    if price_yearly is not None and price_yearly < 0:
    if price_yearly is not None and price_yearly < 0:
    raise ValidationError(
    raise ValidationError(
    message="Yearly price cannot be negative",
    message="Yearly price cannot be negative",
    field="price_yearly",
    field="price_yearly",
    validation_errors=[
    validation_errors=[
    {
    {
    "field": "price_yearly",
    "field": "price_yearly",
    "value": price_yearly,
    "value": price_yearly,
    "error": "Price cannot be negative",
    "error": "Price cannot be negative",
    }
    }
    ],
    ],
    )
    )


    # Update the prices
    # Update the prices
    if price_monthly is not None:
    if price_monthly is not None:
    tier["price_monthly"] = price_monthly
    tier["price_monthly"] = price_monthly


    if price_yearly is not None:
    if price_yearly is not None:
    tier["price_yearly"] = price_yearly
    tier["price_yearly"] = price_yearly


    self.updated_at = datetime.now().isoformat()
    self.updated_at = datetime.now().isoformat()
    logger.info(f"Updated prices for tier {tier['name']} (ID: {tier_id})")
    logger.info(f"Updated prices for tier {tier['name']} (ID: {tier_id})")
    return True
    return True


except ValidationError:
except ValidationError:
    # Re-raise validation errors
    # Re-raise validation errors
    raise
    raise
except Exception as e:
except Exception as e:
    # Handle unexpected errors
    # Handle unexpected errors
    handle_exception(e, error_class=ValidationError, reraise=True)
    handle_exception(e, error_class=ValidationError, reraise=True)
    return False  # This line won't be reached due to reraise=True
    return False  # This line won't be reached due to reraise=True


    def get_tier_by_id(self, tier_id: str) -> Optional[Dict[str, Any]]:
    def get_tier_by_id(self, tier_id: str) -> Optional[Dict[str, Any]]:
    """
    """
    Get a tier by its ID.
    Get a tier by its ID.


    Args:
    Args:
    tier_id: ID of the tier to get
    tier_id: ID of the tier to get


    Returns:
    Returns:
    The tier dictionary, or None if not found
    The tier dictionary, or None if not found
    """
    """
    return next((t for t in self.tiers if t["id"] == tier_id), None)
    return next((t for t in self.tiers if t["id"] == tier_id), None)


    def get_feature_by_id(self, feature_id: str) -> Optional[Dict[str, Any]]:
    def get_feature_by_id(self, feature_id: str) -> Optional[Dict[str, Any]]:
    """
    """
    Get a feature by its ID.
    Get a feature by its ID.


    Args:
    Args:
    feature_id: ID of the feature to get
    feature_id: ID of the feature to get


    Returns:
    Returns:
    The feature dictionary, or None if not found
    The feature dictionary, or None if not found
    """
    """
    return next((f for f in self.features if f["id"] == feature_id), None)
    return next((f for f in self.features if f["id"] == feature_id), None)


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the subscription model to a dictionary.
    Convert the subscription model to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the subscription model
    Dictionary representation of the subscription model
    """
    """
    return {
    return {
    "id": self.id,
    "id": self.id,
    "name": self.name,
    "name": self.name,
    "description": self.description,
    "description": self.description,
    "tiers": self.tiers,
    "tiers": self.tiers,
    "features": self.features,
    "features": self.features,
    "billing_cycles": self.billing_cycles,
    "billing_cycles": self.billing_cycles,
    "created_at": self.created_at,
    "created_at": self.created_at,
    "updated_at": self.updated_at,
    "updated_at": self.updated_at,
    }
    }


    def to_json(self, indent: int = 2) -> str:
    def to_json(self, indent: int = 2) -> str:
    """
    """
    Convert the subscription model to a JSON string.
    Convert the subscription model to a JSON string.


    Args:
    Args:
    indent: Number of spaces for indentation
    indent: Number of spaces for indentation


    Returns:
    Returns:
    JSON string representation of the subscription model
    JSON string representation of the subscription model
    """
    """
    return to_json(self.to_dict(), indent=indent)
    return to_json(self.to_dict(), indent=indent)


    def save_to_file(self, file_path: str) -> None:
    def save_to_file(self, file_path: str) -> None:
    """
    """
    Save the subscription model to a JSON file.
    Save the subscription model to a JSON file.


    Args:
    Args:
    file_path: Path to save the file
    file_path: Path to save the file


    Raises:
    Raises:
    MonetizationError: If there's an issue saving the model
    MonetizationError: If there's an issue saving the model
    """
    """
    try:
    try:
    save_to_json_file(self.to_dict(), file_path)
    save_to_json_file(self.to_dict(), file_path)
    logger.info(
    logger.info(
    f"Successfully saved subscription model '{self.name}' to {file_path}"
    f"Successfully saved subscription model '{self.name}' to {file_path}"
    )
    )
except (IOError, OSError) as e:
except (IOError, OSError) as e:
    = MonetizationError(
    = MonetizationError(
    message=f"Failed to save subscription model to {file_path}: {e}",
    message=f"Failed to save subscription model to {file_path}: {e}",
    code="file_write_error",
    code="file_write_error",
    original_exception=e,
    original_exception=e,
    )
    )
    error.log()
    error.log()
    raise error
    raise error
except Exception as e:
except Exception as e:
    # Handle unexpected errors
    # Handle unexpected errors
    = handle_exception(e, error_class=MonetizationError, reraise=True)
    = handle_exception(e, error_class=MonetizationError, reraise=True)


    @classmethod
    @classmethod
    def load_from_file(cls, file_path: str) -> "SubscriptionModel":
    def load_from_file(cls, file_path: str) -> "SubscriptionModel":
    """
    """
    Load a subscription model from a JSON file.
    Load a subscription model from a JSON file.


    This algorithm implements a sophisticated model deserialization process with
    This algorithm implements a sophisticated model deserialization process with
    polymorphic type handling and advanced validation. The implementation follows
    polymorphic type handling and advanced validation. The implementation follows
    these key stages:
    these key stages:


    1. FILE LOADING AND FORMAT VALIDATION:
    1. FILE LOADING AND FORMAT VALIDATION:
    - Attempts to read and parse the JSON file with proper error handling
    - Attempts to read and parse the JSON file with proper error handling
    - Validates the basic JSON structure before proceeding with model construction
    - Validates the basic JSON structure before proceeding with model construction
    - Uses common_utils for consistent file handling across the application
    - Uses common_utils for consistent file handling across the application
    - Converts parsing exceptions into specific ValidationError types for clarity
    - Converts parsing exceptions into specific ValidationError types for clarity


    2. MODEL INTEGRITY VERIFICATION:
    2. MODEL INTEGRITY VERIFICATION:
    - Performs comprehensive validation of required fields
    - Performs comprehensive validation of required fields
    - Builds detailed error report for all missing fields
    - Builds detailed error report for all missing fields
    - Ensures the deserialized data meets all structural requirements
    - Ensures the deserialized data meets all structural requirements
    - Rejects malformed models early to prevent downstream errors
    - Rejects malformed models early to prevent downstream errors


    3. POLYMORPHIC TYPE HANDLING:
    3. POLYMORPHIC TYPE HANDLING:
    - Detects the model type from the deserialized data
    - Detects the model type from the deserialized data
    - Uses runtime type detection to handle specialized model subclasses
    - Uses runtime type detection to handle specialized model subclasses
    - Creates the appropriate concrete class based on model_type
    - Creates the appropriate concrete class based on model_type
    - Supports extensibility through the class hierarchy
    - Supports extensibility through the class hierarchy


    4. SPECIALIZED FREEMIUM MODEL HANDLING:
    4. SPECIALIZED FREEMIUM MODEL HANDLING:
    - Applies special logic for FreemiumModel instances
    - Applies special logic for FreemiumModel instances
    - Validates freemium-specific fields like free_tier_id
    - Validates freemium-specific fields like free_tier_id
    - Handles the special free tier replacement logic
    - Handles the special free tier replacement logic
    - Maintains the integrity of the free tier relationship
    - Maintains the integrity of the free tier relationship


    5. IDENTITY AND METADATA PRESERVATION:
    5. IDENTITY AND METADATA PRESERVATION:
    - Preserves original identifiers across serialization cycles
    - Preserves original identifiers across serialization cycles
    - Maintains creation and modification timestamps
    - Maintains creation and modification timestamps
    - Ensures data consistency in round-trip serialization scenarios
    - Ensures data consistency in round-trip serialization scenarios
    - Supports proper audit trails and version tracking
    - Supports proper audit trails and version tracking


    6. COMPREHENSIVE ERROR HANDLING:
    6. COMPREHENSIVE ERROR HANDLING:
    - Implements specialized error handling for each failure category
    - Implements specialized error handling for each failure category
    - Maps low-level exceptions to domain-specific error types
    - Maps low-level exceptions to domain-specific error types
    - Provides detailed context in error messages
    - Provides detailed context in error messages
    - Maintains error handling consistency through helper functions
    - Maintains error handling consistency through helper functions


    This implementation specifically addresses several critical needs:
    This implementation specifically addresses several critical needs:
    - Safe deserialization of potentially complex data structures
    - Safe deserialization of potentially complex data structures
    - Proper handling of inheritance relationships in serialized form
    - Proper handling of inheritance relationships in serialized form
    - Maintaining object identity across save/load cycles
    - Maintaining object identity across save/load cycles
    - Comprehensive validation to prevent invalid model states
    - Comprehensive validation to prevent invalid model states


    Args:
    Args:
    file_path: Path to the JSON file containing the serialized model
    file_path: Path to the JSON file containing the serialized model


    Returns:
    Returns:
    A fully constructed SubscriptionModel or appropriate subclass instance
    A fully constructed SubscriptionModel or appropriate subclass instance


    Raises:
    Raises:
    ValidationError: If the file contains invalid or incomplete model data
    ValidationError: If the file contains invalid or incomplete model data
    MonetizationError: If there's an issue with file access or processing
    MonetizationError: If there's an issue with file access or processing
    """
    """
    try:
    try:
    # STAGE 1: File loading and initial parsing
    # STAGE 1: File loading and initial parsing
    try:
    try:
    # Attempt to load and parse the file, converting JSON to a Python dictionary
    # Attempt to load and parse the file, converting JSON to a Python dictionary
    data = load_from_json_file(file_path)
    data = load_from_json_file(file_path)
except Exception as e:
except Exception as e:
    # Convert generic parsing errors to specific ValidationError
    # Convert generic parsing errors to specific ValidationError
    # This improves error handling by categorizing the error type
    # This improves error handling by categorizing the error type
    raise ValidationError(
    raise ValidationError(
    message=f"Invalid JSON format in file {file_path}: {e}",
    message=f"Invalid JSON format in file {file_path}: {e}",
    field="file_content",
    field="file_content",
    original_exception=e,
    original_exception=e,
    )
    )


    # STAGE 2: Validate model completeness and integrity
    # STAGE 2: Validate model completeness and integrity
    # Check for all required fields to ensure the model is complete
    # Check for all required fields to ensure the model is complete
    required_fields = [
    required_fields = [
    "name",
    "name",
    "description",
    "description",
    "tiers",
    "tiers",
    "features",
    "features",
    "billing_cycles",
    "billing_cycles",
    "id",
    "id",
    "created_at",
    "created_at",
    "updated_at",
    "updated_at",
    ]
    ]
    missing_fields = [field for field in required_fields if field not in data]
    missing_fields = [field for field in required_fields if field not in data]


    if missing_fields:
    if missing_fields:
    # Generate detailed validation error with specific missing fields
    # Generate detailed validation error with specific missing fields
    raise ValidationError(
    raise ValidationError(
    message=f"Missing required fields in subscription model data: {', '.join(missing_fields)}",
    message=f"Missing required fields in subscription model data: {', '.join(missing_fields)}",
    field="file_content",
    field="file_content",
    validation_errors=[
    validation_errors=[
    {"field": field, "error": "Field is required"}
    {"field": field, "error": "Field is required"}
    for field in missing_fields
    for field in missing_fields
    ],
    ],
    )
    )


    # STAGE 3: Handle polymorphic model types through runtime detection
    # STAGE 3: Handle polymorphic model types through runtime detection
    # Check the model_type to determine the concrete class to instantiate
    # Check the model_type to determine the concrete class to instantiate
    model_type = data.get("model_type", "")
    model_type = data.get("model_type", "")


    # STAGE 3A: Handle the FreemiumModel specialized case
    # STAGE 3A: Handle the FreemiumModel specialized case
    if model_type == "freemium" and cls.__name__ == "FreemiumModel":
    if model_type == "freemium" and cls.__name__ == "FreemiumModel":
    # Additional validation for freemium-specific requirements
    # Additional validation for freemium-specific requirements
    if "free_tier_id" not in data:
    if "free_tier_id" not in data:
    raise ValidationError(
    raise ValidationError(
    message="Missing required field 'free_tier_id' for FreemiumModel",
    message="Missing required field 'free_tier_id' for FreemiumModel",
    field="free_tier_id",
    field="free_tier_id",
    )
    )


    # Create a FreemiumModel instance using the base constructor
    # Create a FreemiumModel instance using the base constructor
    model = cls(
    model = cls(
    name=data["name"],
    name=data["name"],
    description=data["description"],
    description=data["description"],
    features=data["features"],
    features=data["features"],
    billing_cycles=data["billing_cycles"],
    billing_cycles=data["billing_cycles"],
    )
    )


    # STAGE 3B: Handle the special free tier replacement logic
    # STAGE 3B: Handle the special free tier replacement logic
    # The FreemiumModel constructor auto-creates a free tier,
    # The FreemiumModel constructor auto-creates a free tier,
    # but we need to replace it with the one from the saved data
    # but we need to replace it with the one from the saved data
    free_tier_id = data["free_tier_id"]
    free_tier_id = data["free_tier_id"]
    free_tier = next(
    free_tier = next(
    (t for t in data["tiers"] if t["id"] == free_tier_id), None
    (t for t in data["tiers"] if t["id"] == free_tier_id), None
    )
    )


    if free_tier:
    if free_tier:
    # Find and remove the auto-created free tier
    # Find and remove the auto-created free tier
    for i, tier in enumerate(model.tiers):
    for i, tier in enumerate(model.tiers):
    if tier["id"] == model.free_tier["id"]:
    if tier["id"] == model.free_tier["id"]:
    model.tiers.pop(i)
    model.tiers.pop(i)
    break
    break


    # Add the loaded free tier and update the reference
    # Add the loaded free tier and update the reference
    model.tiers.append(free_tier)
    model.tiers.append(free_tier)
    model.free_tier = free_tier
    model.free_tier = free_tier
    else:
    else:
    # Warn if the referenced free tier is missing in the data
    # Warn if the referenced free tier is missing in the data
    logger.warning(
    logger.warning(
    f"Free tier with ID {free_tier_id} not found in loaded data"
    f"Free tier with ID {free_tier_id} not found in loaded data"
    )
    )


    # Add all other tiers from the loaded data
    # Add all other tiers from the loaded data
    for tier in data["tiers"]:
    for tier in data["tiers"]:
    if tier["id"] != free_tier_id:
    if tier["id"] != free_tier_id:
    model.tiers.append(tier)
    model.tiers.append(tier)
    # STAGE 3C: Handle the standard SubscriptionModel case
    # STAGE 3C: Handle the standard SubscriptionModel case
    else:
    else:
    # Create a regular SubscriptionModel instance with all data
    # Create a regular SubscriptionModel instance with all data
    model = cls(
    model = cls(
    name=data["name"],
    name=data["name"],
    description=data["description"],
    description=data["description"],
    tiers=data["tiers"],
    tiers=data["tiers"],
    features=data["features"],
    features=data["features"],
    billing_cycles=data["billing_cycles"],
    billing_cycles=data["billing_cycles"],
    )
    )


    # STAGE 4: Preserve identity and metadata
    # STAGE 4: Preserve identity and metadata
    # Set the original identifiers and timestamps for consistency
    # Set the original identifiers and timestamps for consistency
    model.id = data["id"]
    model.id = data["id"]
    model.created_at = data["created_at"]
    model.created_at = data["created_at"]
    model.updated_at = data["updated_at"]
    model.updated_at = data["updated_at"]


    logger.info(
    logger.info(
    f"Successfully loaded subscription model '{model.name}' from {file_path}"
    f"Successfully loaded subscription model '{model.name}' from {file_path}"
    )
    )
    return model
    return model


    # STAGE 5: Comprehensive error handling for different failure scenarios
    # STAGE 5: Comprehensive error handling for different failure scenarios
except (ValidationError, MonetizationError):
except (ValidationError, MonetizationError):
    # Re-raise domain-specific errors that have already been properly categorized
    # Re-raise domain-specific errors that have already been properly categorized
    raise
    raise
except FileNotFoundError as e:
except FileNotFoundError as e:
    # Convert file not found into a domain-specific error
    # Convert file not found into a domain-specific error
    = MonetizationError(
    = MonetizationError(
    message=f"File not found: {file_path}",
    message=f"File not found: {file_path}",
    code="file_not_found",
    code="file_not_found",
    original_exception=e,
    original_exception=e,
    )
    )
    error.log()
    error.log()
    raise error
    raise error
except Exception as e:
except Exception as e:
    # Handle any other unexpected errors
    # Handle any other unexpected errors
    error = handle_exception(e, error_class=MonetizationError, reraise=True)
    error = handle_exception(e, error_class=MonetizationError, reraise=True)
    return None  # This line won't be reached due to reraise=True
    return None  # This line won't be reached due to reraise=True


    def __str__(self) -> str:
    def __str__(self) -> str:
    """String representation of the subscription model."""
    return f"{self.name} ({len(self.tiers)} tiers, {len(self.features)} features)"

    def __repr__(self) -> str:
    """Detailed string representation of the subscription model."""
    return f"SubscriptionModel(id={self.id}, name={self.name}, tiers={len(self.tiers)}, features={len(self.features)})"


    class FreemiumModel(SubscriptionModel):
    """
    """
    Freemium subscription model with a free tier and paid tiers.
    Freemium subscription model with a free tier and paid tiers.


    This model is designed for products that offer a free tier with limited
    This model is designed for products that offer a free tier with limited
    functionality and paid tiers with additional features.
    functionality and paid tiers with additional features.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    name: str,
    name: str,
    description: str = "",
    description: str = "",
    features: Optional[List[Dict[str, Any]]] = None,
    features: Optional[List[Dict[str, Any]]] = None,
    billing_cycles: Optional[List[str]] = None,
    billing_cycles: Optional[List[str]] = None,
    free_tier_name: str = "Free",
    free_tier_name: str = "Free",
    free_tier_description: str = "Free tier with limited functionality",
    free_tier_description: str = "Free tier with limited functionality",
    free_tier_limits: Optional[Dict[str, Any]] = None,
    free_tier_limits: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize a freemium subscription model.
    Initialize a freemium subscription model.


    Args:
    Args:
    name: Name of the subscription model
    name: Name of the subscription model
    description: Description of the subscription model
    description: Description of the subscription model
    features: List of feature dictionaries (optional)
    features: List of feature dictionaries (optional)
    billing_cycles: List of billing cycle options (optional)
    billing_cycles: List of billing cycle options (optional)
    free_tier_name: Name of the free tier
    free_tier_name: Name of the free tier
    free_tier_description: Description of the free tier
    free_tier_description: Description of the free tier
    free_tier_limits: Dictionary of usage limits for the free tier
    free_tier_limits: Dictionary of usage limits for the free tier
    """
    """
    super().__init__(
    super().__init__(
    name=name,
    name=name,
    description=description,
    description=description,
    features=features,
    features=features,
    billing_cycles=billing_cycles,
    billing_cycles=billing_cycles,
    )
    )


    # Create the free tier
    # Create the free tier
    self.free_tier = self.add_tier(
    self.free_tier = self.add_tier(
    name=free_tier_name,
    name=free_tier_name,
    description=free_tier_description,
    description=free_tier_description,
    price_monthly=0.0,
    price_monthly=0.0,
    price_yearly=0.0,
    price_yearly=0.0,
    limits=free_tier_limits
    limits=free_tier_limits
    or {"usage": "limited", "api_calls": 100, "exports": 5},
    or {"usage": "limited", "api_calls": 100, "exports": 5},
    target_users="Free users and trial users",
    target_users="Free users and trial users",
    )
    )


    def add_paid_tier(
    def add_paid_tier(
    self,
    self,
    name: str,
    name: str,
    description: str = "",
    description: str = "",
    price_monthly: float = 9.99,
    price_monthly: float = 9.99,
    price_yearly: Optional[float] = None,
    price_yearly: Optional[float] = None,
    features: Optional[List[str]] = None,
    features: Optional[List[str]] = None,
    limits: Optional[Dict[str, Any]] = None,
    limits: Optional[Dict[str, Any]] = None,
    target_users: str = "",
    target_users: str = "",
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Add a new paid tier to the freemium model.
    Add a new paid tier to the freemium model.


    Args:
    Args:
    name: Name of the tier (e.g., "Pro", "Premium")
    name: Name of the tier (e.g., "Pro", "Premium")
    description: Description of the tier
    description: Description of the tier
    price_monthly: Monthly price for the tier
    price_monthly: Monthly price for the tier
    price_yearly: Yearly price for the tier (defaults to monthly * 10 if None)
    price_yearly: Yearly price for the tier (defaults to monthly * 10 if None)
    features: List of feature IDs included in this tier
    features: List of feature IDs included in this tier
    limits: Dictionary of usage limits for this tier
    limits: Dictionary of usage limits for this tier
    target_users: Description of target users for this tier
    target_users: Description of target users for this tier


    Returns:
    Returns:
    The newly created tier dictionary
    The newly created tier dictionary
    """
    """
    # Add the tier using the parent class method
    # Add the tier using the parent class method
    tier = super().add_tier(
    tier = super().add_tier(
    name=name,
    name=name,
    description=description,
    description=description,
    price_monthly=price_monthly,
    price_monthly=price_monthly,
    price_yearly=price_yearly,
    price_yearly=price_yearly,
    features=features,
    features=features,
    limits=limits,
    limits=limits,
    target_users=target_users,
    target_users=target_users,
    )
    )


    return tier
    return tier


    def get_free_tier_id(self) -> str:
    def get_free_tier_id(self) -> str:
    """
    """
    Get the ID of the free tier.
    Get the ID of the free tier.


    Returns:
    Returns:
    ID of the free tier
    ID of the free tier
    """
    """
    return self.free_tier["id"]
    return self.free_tier["id"]


    def get_free_tier(self) -> Dict[str, Any]:
    def get_free_tier(self) -> Dict[str, Any]:
    """
    """
    Get the free tier.
    Get the free tier.


    Returns:
    Returns:
    The free tier dictionary
    The free tier dictionary
    """
    """
    return self.free_tier
    return self.free_tier


    def add_feature_to_free_tier(self, feature_id: str) -> bool:
    def add_feature_to_free_tier(self, feature_id: str) -> bool:
    """
    """
    Add a feature to the free tier.
    Add a feature to the free tier.


    Args:
    Args:
    feature_id: ID of the feature to add
    feature_id: ID of the feature to add


    Returns:
    Returns:
    True if the feature was added, False otherwise
    True if the feature was added, False otherwise
    """
    """
    return self.assign_feature_to_tier(feature_id, self.free_tier["id"])
    return self.assign_feature_to_tier(feature_id, self.free_tier["id"])


    def update_tier_limits(self, tier_id: str, limits: Dict[str, Any]) -> bool:
    def update_tier_limits(self, tier_id: str, limits: Dict[str, Any]) -> bool:
    """
    """
    Update the limits of a tier.
    Update the limits of a tier.


    Args:
    Args:
    tier_id: ID of the tier to update
    tier_id: ID of the tier to update
    limits: Dictionary of usage limits for the tier
    limits: Dictionary of usage limits for the tier


    Returns:
    Returns:
    True if the limits were updated, False otherwise
    True if the limits were updated, False otherwise
    """
    """
    # Find the tier
    # Find the tier
    tier = next((t for t in self.tiers if t["id"] == tier_id), None)
    tier = next((t for t in self.tiers if t["id"] == tier_id), None)
    if not tier:
    if not tier:
    return False
    return False


    # Update the limits
    # Update the limits
    tier["limits"] = copy.deepcopy(limits)
    tier["limits"] = copy.deepcopy(limits)
    self.updated_at = datetime.now().isoformat()
    self.updated_at = datetime.now().isoformat()


    return True
    return True


    def update_free_tier_limits(self, limits: Dict[str, Any]) -> bool:
    def update_free_tier_limits(self, limits: Dict[str, Any]) -> bool:
    """
    """
    Update the limits of the free tier.
    Update the limits of the free tier.


    Args:
    Args:
    limits: Dictionary of usage limits for the free tier
    limits: Dictionary of usage limits for the free tier


    Returns:
    Returns:
    True if the limits were updated, False otherwise
    True if the limits were updated, False otherwise
    """
    """
    return self.update_tier_limits(self.free_tier["id"], limits)
    return self.update_tier_limits(self.free_tier["id"], limits)


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the freemium model to a dictionary.
    Convert the freemium model to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the freemium model
    Dictionary representation of the freemium model
    """
    """
    data = super().to_dict()
    data = super().to_dict()
    data["model_type"] = "freemium"
    data["model_type"] = "freemium"
    data["free_tier_id"] = self.free_tier["id"]
    data["free_tier_id"] = self.free_tier["id"]


    return data
    return data




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Create a freemium subscription model
    # Create a freemium subscription model
    model = FreemiumModel(
    model = FreemiumModel(
    name="AI Tool Freemium Subscription",
    name="AI Tool Freemium Subscription",
    description="Freemium subscription model for an AI-powered tool",
    description="Freemium subscription model for an AI-powered tool",
    )
    )


    # Add features
    # Add features
    feature1 = model.add_feature(
    feature1 = model.add_feature(
    name="Basic Text Generation",
    name="Basic Text Generation",
    description="Generate text using AI models",
    description="Generate text using AI models",
    feature_type="functional",
    feature_type="functional",
    value_proposition="Save time on writing",
    value_proposition="Save time on writing",
    development_cost="low",
    development_cost="low",
    )
    )


    feature2 = model.add_feature(
    feature2 = model.add_feature(
    name="Advanced Text Generation",
    name="Advanced Text Generation",
    description="Generate high-quality text with more control",
    description="Generate high-quality text with more control",
    feature_type="functional",
    feature_type="functional",
    value_proposition="Create professional content faster",
    value_proposition="Create professional content faster",
    development_cost="medium",
    development_cost="medium",
    )
    )


    feature3 = model.add_feature(
    feature3 = model.add_feature(
    name="Template Library",
    name="Template Library",
    description="Access to pre-made templates",
    description="Access to pre-made templates",
    feature_type="content",
    feature_type="content",
    value_proposition="Start with proven formats",
    value_proposition="Start with proven formats",
    development_cost="medium",
    development_cost="medium",
    )
    )


    feature4 = model.add_feature(
    feature4 = model.add_feature(
    name="Priority Support",
    name="Priority Support",
    description="Get priority support from our team",
    description="Get priority support from our team",
    feature_type="support",
    feature_type="support",
    value_proposition="Get help when you need it",
    value_proposition="Get help when you need it",
    development_cost="high",
    development_cost="high",
    )
    )


    # Add feature to free tier
    # Add feature to free tier
    model.add_feature_to_free_tier(feature1["id"])
    model.add_feature_to_free_tier(feature1["id"])


    # Add paid tiers
    # Add paid tiers
    pro_tier = model.add_paid_tier(
    pro_tier = model.add_paid_tier(
    name="Pro",
    name="Pro",
    description="Advanced features for professionals",
    description="Advanced features for professionals",
    price_monthly=19.99,
    price_monthly=19.99,
    target_users="Professional content creators and marketing teams",
    target_users="Professional content creators and marketing teams",
    )
    )


    premium_tier = model.add_paid_tier(
    premium_tier = model.add_paid_tier(
    name="Premium",
    name="Premium",
    description="All features for enterprise users",
    description="All features for enterprise users",
    price_monthly=49.99,
    price_monthly=49.99,
    target_users="Enterprise teams and agencies",
    target_users="Enterprise teams and agencies",
    )
    )


    # Assign features to paid tiers
    # Assign features to paid tiers
    model.assign_feature_to_tier(feature1["id"], pro_tier["id"])
    model.assign_feature_to_tier(feature1["id"], pro_tier["id"])
    model.assign_feature_to_tier(feature1["id"], premium_tier["id"])
    model.assign_feature_to_tier(feature1["id"], premium_tier["id"])


    model.assign_feature_to_tier(feature2["id"], pro_tier["id"])
    model.assign_feature_to_tier(feature2["id"], pro_tier["id"])
    model.assign_feature_to_tier(feature2["id"], premium_tier["id"])
    model.assign_feature_to_tier(feature2["id"], premium_tier["id"])


    model.assign_feature_to_tier(feature3["id"], pro_tier["id"])
    model.assign_feature_to_tier(feature3["id"], pro_tier["id"])
    model.assign_feature_to_tier(feature3["id"], premium_tier["id"])
    model.assign_feature_to_tier(feature3["id"], premium_tier["id"])


    model.assign_feature_to_tier(feature4["id"], premium_tier["id"])
    model.assign_feature_to_tier(feature4["id"], premium_tier["id"])


    # Print the model
    # Print the model
    print(model)
    print(model)


    # Get features for each tier
    # Get features for each tier
    free_tier_id = model.get_free_tier_id()
    free_tier_id = model.get_free_tier_id()
    free_features = model.get_tier_features(free_tier_id)
    free_features = model.get_tier_features(free_tier_id)
    print(f"\nFree tier features: {len(free_features)}")
    print(f"\nFree tier features: {len(free_features)}")
    for feature in free_features:
    for feature in free_features:
    print(f"- {feature['name']}: {feature['description']}")
    print(f"- {feature['name']}: {feature['description']}")


    pro_features = model.get_tier_features(pro_tier["id"])
    pro_features = model.get_tier_features(pro_tier["id"])
    print(f"\nPro tier features: {len(pro_features)}")
    print(f"\nPro tier features: {len(pro_features)}")
    for feature in pro_features:
    for feature in pro_features:
    print(f"- {feature['name']}: {feature['description']}")
    print(f"- {feature['name']}: {feature['description']}")


    premium_features = model.get_tier_features(premium_tier["id"])
    premium_features = model.get_tier_features(premium_tier["id"])
    print(f"\nPremium tier features: {len(premium_features)}")
    print(f"\nPremium tier features: {len(premium_features)}")
    for feature in premium_features:
    for feature in premium_features:
    print(f"- {feature['name']}: {feature['description']}")
    print(f"- {feature['name']}: {feature['description']}")


    # Save to file
    # Save to file
    # model.save_to_file("freemium_model.json")
    # model.save_to_file("freemium_model.json")


    # Load from file
    # Load from file
    # loaded_model = SubscriptionModel.load_from_file("freemium_model.json")
    # loaded_model = SubscriptionModel.load_from_file("freemium_model.json")
    # print(f"\nLoaded model: {loaded_model}")
    # print(f"\nLoaded model: {loaded_model}")