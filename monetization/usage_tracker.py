"""
"""
Usage tracker for the pAIssive Income project.
Usage tracker for the pAIssive Income project.


This module provides a class for tracking and managing usage records,
This module provides a class for tracking and managing usage records,
including storage, retrieval, and analysis.
including storage, retrieval, and analysis.
"""
"""


import copy
import copy
import json
import json
import os
import os
import time
import time
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from typing import Any, Dict, List, Optional, Tuple


(
(
UsageCategory,
UsageCategory,
UsageLimit,
UsageLimit,
UsageMetric,
UsageMetric,
UsageQuota,
UsageQuota,
UsageRecord,
UsageRecord,
)
)




class UsageTracker:
    class UsageTracker:
    """
    """
    Class for tracking and managing usage.
    Class for tracking and managing usage.


    This class provides methods for recording, retrieving, and analyzing
    This class provides methods for recording, retrieving, and analyzing
    usage of API calls and resources.
    usage of API calls and resources.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    storage_dir: Optional[str] = None,
    storage_dir: Optional[str] = None,
    auto_create_quotas: bool = True,
    auto_create_quotas: bool = True,
    auto_reset_quotas: bool = True,
    auto_reset_quotas: bool = True,
    ):
    ):
    """
    """
    Initialize a usage tracker.
    Initialize a usage tracker.


    Args:
    Args:
    storage_dir: Directory for storing usage data
    storage_dir: Directory for storing usage data
    auto_create_quotas: Whether to automatically create quotas from limits
    auto_create_quotas: Whether to automatically create quotas from limits
    auto_reset_quotas: Whether to automatically reset quotas when due
    auto_reset_quotas: Whether to automatically reset quotas when due
    """
    """
    self.storage_dir = storage_dir
    self.storage_dir = storage_dir
    self.auto_create_quotas = auto_create_quotas
    self.auto_create_quotas = auto_create_quotas
    self.auto_reset_quotas = auto_reset_quotas
    self.auto_reset_quotas = auto_reset_quotas


    if storage_dir and not os.path.exists(storage_dir):
    if storage_dir and not os.path.exists(storage_dir):
    os.makedirs(storage_dir)
    os.makedirs(storage_dir)


    # Create subdirectories for different types of data
    # Create subdirectories for different types of data
    os.makedirs(os.path.join(storage_dir, "records"), exist_ok=True)
    os.makedirs(os.path.join(storage_dir, "records"), exist_ok=True)
    os.makedirs(os.path.join(storage_dir, "limits"), exist_ok=True)
    os.makedirs(os.path.join(storage_dir, "limits"), exist_ok=True)
    os.makedirs(os.path.join(storage_dir, "quotas"), exist_ok=True)
    os.makedirs(os.path.join(storage_dir, "quotas"), exist_ok=True)


    # Initialize storage
    # Initialize storage
    self.records = {}
    self.records = {}
    self.limits = {}
    self.limits = {}
    self.quotas = {}
    self.quotas = {}


    # Initialize indexes
    # Initialize indexes
    self.customer_records = {}
    self.customer_records = {}
    self.metric_records = {}
    self.metric_records = {}
    self.category_records = {}
    self.category_records = {}
    self.resource_records = {}
    self.resource_records = {}


    self.customer_limits = {}
    self.customer_limits = {}
    self.metric_limits = {}
    self.metric_limits = {}


    self.customer_quotas = {}
    self.customer_quotas = {}
    self.metric_quotas = {}
    self.metric_quotas = {}


    # Load data if storage directory is set
    # Load data if storage directory is set
    if storage_dir:
    if storage_dir:
    self.load_data()
    self.load_data()


    def add_limit(self, limit: UsageLimit) -> UsageLimit:
    def add_limit(self, limit: UsageLimit) -> UsageLimit:
    """
    """
    Add a usage limit.
    Add a usage limit.


    Args:
    Args:
    limit: Usage limit to add
    limit: Usage limit to add


    Returns:
    Returns:
    The added usage limit
    The added usage limit
    """
    """
    # Store limit
    # Store limit
    self.limits[limit.id] = limit
    self.limits[limit.id] = limit


    # Add to customer index
    # Add to customer index
    if limit.customer_id not in self.customer_limits:
    if limit.customer_id not in self.customer_limits:
    self.customer_limits[limit.customer_id] = []
    self.customer_limits[limit.customer_id] = []


    self.customer_limits[limit.customer_id].append(limit.id)
    self.customer_limits[limit.customer_id].append(limit.id)


    # Add to metric index
    # Add to metric index
    if limit.metric not in self.metric_limits:
    if limit.metric not in self.metric_limits:
    self.metric_limits[limit.metric] = []
    self.metric_limits[limit.metric] = []


    self.metric_limits[limit.metric].append(limit.id)
    self.metric_limits[limit.metric].append(limit.id)


    # Create quota if auto-create is enabled
    # Create quota if auto-create is enabled
    if self.auto_create_quotas:
    if self.auto_create_quotas:
    # Check if a quota already exists for this limit
    # Check if a quota already exists for this limit
    existing_quota = self.find_matching_quota(limit)
    existing_quota = self.find_matching_quota(limit)


    if not existing_quota:
    if not existing_quota:
    quota = UsageQuota(
    quota = UsageQuota(
    customer_id=limit.customer_id,
    customer_id=limit.customer_id,
    metric=limit.metric,
    metric=limit.metric,
    allocated_quantity=limit.max_quantity,
    allocated_quantity=limit.max_quantity,
    period=limit.period,
    period=limit.period,
    category=limit.category,
    category=limit.category,
    resource_type=limit.resource_type,
    resource_type=limit.resource_type,
    subscription_id=limit.subscription_id,
    subscription_id=limit.subscription_id,
    metadata=copy.deepcopy(limit.metadata),
    metadata=copy.deepcopy(limit.metadata),
    )
    )


    self.add_quota(quota)
    self.add_quota(quota)


    # Save limit if storage directory is set
    # Save limit if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_limit(limit)
    self._save_limit(limit)


    return limit
    return limit


    def get_limit(self, limit_id: str) -> Optional[UsageLimit]:
    def get_limit(self, limit_id: str) -> Optional[UsageLimit]:
    """
    """
    Get a usage limit by ID.
    Get a usage limit by ID.


    Args:
    Args:
    limit_id: ID of the limit
    limit_id: ID of the limit


    Returns:
    Returns:
    The usage limit or None if not found
    The usage limit or None if not found
    """
    """
    return self.limits.get(limit_id)
    return self.limits.get(limit_id)


    def get_customer_limits(
    def get_customer_limits(
    self,
    self,
    customer_id: str,
    customer_id: str,
    metric: Optional[str] = None,
    metric: Optional[str] = None,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    ) -> List[UsageLimit]:
    ) -> List[UsageLimit]:
    """
    """
    Get usage limits for a customer.
    Get usage limits for a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    metric: Type of usage metric to filter by
    metric: Type of usage metric to filter by
    category: Category of usage to filter by
    category: Category of usage to filter by
    resource_type: Type of resource to filter by
    resource_type: Type of resource to filter by


    Returns:
    Returns:
    List of usage limits
    List of usage limits
    """
    """
    if customer_id not in self.customer_limits:
    if customer_id not in self.customer_limits:
    return []
    return []


    limits = []
    limits = []


    for limit_id in self.customer_limits[customer_id]:
    for limit_id in self.customer_limits[customer_id]:
    limit = self.limits.get(limit_id)
    limit = self.limits.get(limit_id)


    if not limit:
    if not limit:
    continue
    continue


    # Filter by metric
    # Filter by metric
    if metric and limit.metric != metric:
    if metric and limit.metric != metric:
    continue
    continue


    # Filter by category
    # Filter by category
    if category and limit.category != category:
    if category and limit.category != category:
    continue
    continue


    # Filter by resource type
    # Filter by resource type
    if resource_type and limit.resource_type != resource_type:
    if resource_type and limit.resource_type != resource_type:
    continue
    continue


    limits.append(limit)
    limits.append(limit)


    return limits
    return limits


    def update_limit(
    def update_limit(
    self,
    self,
    limit_id: str,
    limit_id: str,
    max_quantity: Optional[float] = None,
    max_quantity: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[UsageLimit]:
    ) -> Optional[UsageLimit]:
    """
    """
    Update a usage limit.
    Update a usage limit.


    Args:
    Args:
    limit_id: ID of the limit to update
    limit_id: ID of the limit to update
    max_quantity: New maximum quantity
    max_quantity: New maximum quantity
    metadata: New metadata
    metadata: New metadata


    Returns:
    Returns:
    The updated usage limit or None if not found
    The updated usage limit or None if not found
    """
    """
    # Get limit
    # Get limit
    limit = self.get_limit(limit_id)
    limit = self.get_limit(limit_id)


    if not limit:
    if not limit:
    return None
    return None


    # Update limit
    # Update limit
    if max_quantity is not None:
    if max_quantity is not None:
    limit.max_quantity = max_quantity
    limit.max_quantity = max_quantity


    if metadata is not None:
    if metadata is not None:
    limit.metadata = metadata
    limit.metadata = metadata


    limit.updated_at = datetime.now()
    limit.updated_at = datetime.now()


    # Update matching quota if auto-create is enabled
    # Update matching quota if auto-create is enabled
    if self.auto_create_quotas:
    if self.auto_create_quotas:
    quota = self.find_matching_quota(limit)
    quota = self.find_matching_quota(limit)


    if quota and max_quantity is not None:
    if quota and max_quantity is not None:
    quota.update_allocation(max_quantity)
    quota.update_allocation(max_quantity)


    # Save quota if storage directory is set
    # Save quota if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_quota(quota)
    self._save_quota(quota)


    # Save limit if storage directory is set
    # Save limit if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_limit(limit)
    self._save_limit(limit)


    return limit
    return limit


    def delete_limit(self, limit_id: str) -> bool:
    def delete_limit(self, limit_id: str) -> bool:
    """
    """
    Delete a usage limit.
    Delete a usage limit.


    Args:
    Args:
    limit_id: ID of the limit to delete
    limit_id: ID of the limit to delete


    Returns:
    Returns:
    True if the limit was deleted, False otherwise
    True if the limit was deleted, False otherwise
    """
    """
    # Get limit
    # Get limit
    limit = self.get_limit(limit_id)
    limit = self.get_limit(limit_id)


    if not limit:
    if not limit:
    return False
    return False


    # Remove from customer index
    # Remove from customer index
    if limit.customer_id in self.customer_limits:
    if limit.customer_id in self.customer_limits:
    if limit_id in self.customer_limits[limit.customer_id]:
    if limit_id in self.customer_limits[limit.customer_id]:
    self.customer_limits[limit.customer_id].remove(limit_id)
    self.customer_limits[limit.customer_id].remove(limit_id)


    # Remove from metric index
    # Remove from metric index
    if limit.metric in self.metric_limits:
    if limit.metric in self.metric_limits:
    if limit_id in self.metric_limits[limit.metric]:
    if limit_id in self.metric_limits[limit.metric]:
    self.metric_limits[limit.metric].remove(limit_id)
    self.metric_limits[limit.metric].remove(limit_id)


    # Remove from limits
    # Remove from limits
    del self.limits[limit_id]
    del self.limits[limit_id]


    # Delete file if storage directory is set
    # Delete file if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    file_path = os.path.join(self.storage_dir, "limits", f"{limit_id}.json")
    file_path = os.path.join(self.storage_dir, "limits", f"{limit_id}.json")


    if os.path.exists(file_path):
    if os.path.exists(file_path):
    os.remove(file_path)
    os.remove(file_path)


    return True
    return True


    def add_quota(self, quota: UsageQuota) -> UsageQuota:
    def add_quota(self, quota: UsageQuota) -> UsageQuota:
    """
    """
    Add a usage quota.
    Add a usage quota.


    Args:
    Args:
    quota: Usage quota to add
    quota: Usage quota to add


    Returns:
    Returns:
    The added usage quota
    The added usage quota
    """
    """
    # Store quota
    # Store quota
    self.quotas[quota.id] = quota
    self.quotas[quota.id] = quota


    # Add to customer index
    # Add to customer index
    if quota.customer_id not in self.customer_quotas:
    if quota.customer_id not in self.customer_quotas:
    self.customer_quotas[quota.customer_id] = []
    self.customer_quotas[quota.customer_id] = []


    self.customer_quotas[quota.customer_id].append(quota.id)
    self.customer_quotas[quota.customer_id].append(quota.id)


    # Add to metric index
    # Add to metric index
    if quota.metric not in self.metric_quotas:
    if quota.metric not in self.metric_quotas:
    self.metric_quotas[quota.metric] = []
    self.metric_quotas[quota.metric] = []


    self.metric_quotas[quota.metric].append(quota.id)
    self.metric_quotas[quota.metric].append(quota.id)


    # Save quota if storage directory is set
    # Save quota if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_quota(quota)
    self._save_quota(quota)


    return quota
    return quota


    def get_quota(self, quota_id: str) -> Optional[UsageQuota]:
    def get_quota(self, quota_id: str) -> Optional[UsageQuota]:
    """
    """
    Get a usage quota by ID.
    Get a usage quota by ID.


    Args:
    Args:
    quota_id: ID of the quota
    quota_id: ID of the quota


    Returns:
    Returns:
    The usage quota or None if not found
    The usage quota or None if not found
    """
    """
    return self.quotas.get(quota_id)
    return self.quotas.get(quota_id)


    def get_customer_quotas(
    def get_customer_quotas(
    self,
    self,
    customer_id: str,
    customer_id: str,
    metric: Optional[str] = None,
    metric: Optional[str] = None,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    ) -> List[UsageQuota]:
    ) -> List[UsageQuota]:
    """
    """
    Get usage quotas for a customer.
    Get usage quotas for a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    metric: Type of usage metric to filter by
    metric: Type of usage metric to filter by
    category: Category of usage to filter by
    category: Category of usage to filter by
    resource_type: Type of resource to filter by
    resource_type: Type of resource to filter by


    Returns:
    Returns:
    List of usage quotas
    List of usage quotas
    """
    """
    if customer_id not in self.customer_quotas:
    if customer_id not in self.customer_quotas:
    return []
    return []


    quotas = []
    quotas = []


    for quota_id in self.customer_quotas[customer_id]:
    for quota_id in self.customer_quotas[customer_id]:
    quota = self.quotas.get(quota_id)
    quota = self.quotas.get(quota_id)


    if not quota:
    if not quota:
    continue
    continue


    # Check if reset is due
    # Check if reset is due
    if self.auto_reset_quotas and quota.is_reset_due():
    if self.auto_reset_quotas and quota.is_reset_due():
    quota.reset_usage()
    quota.reset_usage()


    # Save quota if storage directory is set
    # Save quota if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_quota(quota)
    self._save_quota(quota)


    # Filter by metric
    # Filter by metric
    if metric and quota.metric != metric:
    if metric and quota.metric != metric:
    continue
    continue


    # Filter by category
    # Filter by category
    if category and quota.category != category:
    if category and quota.category != category:
    continue
    continue


    # Filter by resource type
    # Filter by resource type
    if resource_type and quota.resource_type != resource_type:
    if resource_type and quota.resource_type != resource_type:
    continue
    continue


    quotas.append(quota)
    quotas.append(quota)


    return quotas
    return quotas


    def update_quota(
    def update_quota(
    self,
    self,
    quota_id: str,
    quota_id: str,
    allocated_quantity: Optional[float] = None,
    allocated_quantity: Optional[float] = None,
    used_quantity: Optional[float] = None,
    used_quantity: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[UsageQuota]:
    ) -> Optional[UsageQuota]:
    """
    """
    Update a usage quota.
    Update a usage quota.


    Args:
    Args:
    quota_id: ID of the quota to update
    quota_id: ID of the quota to update
    allocated_quantity: New allocated quantity
    allocated_quantity: New allocated quantity
    used_quantity: New used quantity
    used_quantity: New used quantity
    metadata: New metadata
    metadata: New metadata


    Returns:
    Returns:
    The updated usage quota or None if not found
    The updated usage quota or None if not found
    """
    """
    # Get quota
    # Get quota
    quota = self.get_quota(quota_id)
    quota = self.get_quota(quota_id)


    if not quota:
    if not quota:
    return None
    return None


    # Check if reset is due
    # Check if reset is due
    if self.auto_reset_quotas and quota.is_reset_due():
    if self.auto_reset_quotas and quota.is_reset_due():
    quota.reset_usage()
    quota.reset_usage()


    # Update quota
    # Update quota
    if allocated_quantity is not None:
    if allocated_quantity is not None:
    quota.update_allocation(allocated_quantity)
    quota.update_allocation(allocated_quantity)


    if used_quantity is not None:
    if used_quantity is not None:
    quota.used_quantity = used_quantity
    quota.used_quantity = used_quantity
    quota.updated_at = datetime.now()
    quota.updated_at = datetime.now()


    if metadata is not None:
    if metadata is not None:
    quota.metadata = metadata
    quota.metadata = metadata
    quota.updated_at = datetime.now()
    quota.updated_at = datetime.now()


    # Save quota if storage directory is set
    # Save quota if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_quota(quota)
    self._save_quota(quota)


    return quota
    return quota


    def delete_quota(self, quota_id: str) -> bool:
    def delete_quota(self, quota_id: str) -> bool:
    """
    """
    Delete a usage quota.
    Delete a usage quota.


    Args:
    Args:
    quota_id: ID of the quota to delete
    quota_id: ID of the quota to delete


    Returns:
    Returns:
    True if the quota was deleted, False otherwise
    True if the quota was deleted, False otherwise
    """
    """
    # Get quota
    # Get quota
    quota = self.get_quota(quota_id)
    quota = self.get_quota(quota_id)


    if not quota:
    if not quota:
    return False
    return False


    # Remove from customer index
    # Remove from customer index
    if quota.customer_id in self.customer_quotas:
    if quota.customer_id in self.customer_quotas:
    if quota_id in self.customer_quotas[quota.customer_id]:
    if quota_id in self.customer_quotas[quota.customer_id]:
    self.customer_quotas[quota.customer_id].remove(quota_id)
    self.customer_quotas[quota.customer_id].remove(quota_id)


    # Remove from metric index
    # Remove from metric index
    if quota.metric in self.metric_quotas:
    if quota.metric in self.metric_quotas:
    if quota_id in self.metric_quotas[quota.metric]:
    if quota_id in self.metric_quotas[quota.metric]:
    self.metric_quotas[quota.metric].remove(quota_id)
    self.metric_quotas[quota.metric].remove(quota_id)


    # Remove from quotas
    # Remove from quotas
    del self.quotas[quota_id]
    del self.quotas[quota_id]


    # Delete file if storage directory is set
    # Delete file if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    file_path = os.path.join(self.storage_dir, "quotas", f"{quota_id}.json")
    file_path = os.path.join(self.storage_dir, "quotas", f"{quota_id}.json")


    if os.path.exists(file_path):
    if os.path.exists(file_path):
    os.remove(file_path)
    os.remove(file_path)


    return True
    return True


    def find_matching_quota(self, limit: UsageLimit) -> Optional[UsageQuota]:
    def find_matching_quota(self, limit: UsageLimit) -> Optional[UsageQuota]:
    """
    """
    Find a quota that matches a limit.
    Find a quota that matches a limit.


    Args:
    Args:
    limit: Usage limit to match
    limit: Usage limit to match


    Returns:
    Returns:
    Matching usage quota or None if not found
    Matching usage quota or None if not found
    """
    """
    # Get quotas for the customer
    # Get quotas for the customer
    quotas = self.get_customer_quotas(
    quotas = self.get_customer_quotas(
    customer_id=limit.customer_id,
    customer_id=limit.customer_id,
    metric=limit.metric,
    metric=limit.metric,
    category=limit.category,
    category=limit.category,
    resource_type=limit.resource_type,
    resource_type=limit.resource_type,
    )
    )


    # Find a quota with the same period
    # Find a quota with the same period
    for quota in quotas:
    for quota in quotas:
    if quota.period == limit.period:
    if quota.period == limit.period:
    return quota
    return quota


    return None
    return None


    def load_data(self) -> None:
    def load_data(self) -> None:
    """Load usage data from storage directory."""
    if not self.storage_dir or not os.path.exists(self.storage_dir):
    return # Load limits
    limits_dir = os.path.join(self.storage_dir, "limits")

    if os.path.exists(limits_dir):
    for filename in os.listdir(limits_dir):
    if filename.endswith(".json"):
    file_path = os.path.join(limits_dir, filename)

    try:
    with open(file_path, "r") as f:
    data = json.load(f)

    limit = UsageLimit.from_dict(data)

    # Store limit
    self.limits[limit.id] = limit

    # Add to customer index
    if limit.customer_id not in self.customer_limits:
    self.customer_limits[limit.customer_id] = []

    self.customer_limits[limit.customer_id].append(limit.id)

    # Add to metric index
    if limit.metric not in self.metric_limits:
    self.metric_limits[limit.metric] = []

    self.metric_limits[limit.metric].append(limit.id)

except Exception as e:
    print(f"Error loading limit from {file_path}: {e}")

    # Load quotas
    quotas_dir = os.path.join(self.storage_dir, "quotas")

    if os.path.exists(quotas_dir):
    for filename in os.listdir(quotas_dir):
    if filename.endswith(".json"):
    file_path = os.path.join(quotas_dir, filename)

    try:
    with open(file_path, "r") as f:
    data = json.load(f)

    quota = UsageQuota.from_dict(data)

    # Store quota
    self.quotas[quota.id] = quota

    # Add to customer index
    if quota.customer_id not in self.customer_quotas:
    self.customer_quotas[quota.customer_id] = []

    self.customer_quotas[quota.customer_id].append(quota.id)

    # Add to metric index
    if quota.metric not in self.metric_quotas:
    self.metric_quotas[quota.metric] = []

    self.metric_quotas[quota.metric].append(quota.id)

except Exception as e:
    print(f"Error loading quota from {file_path}: {e}")

    # Load records
    records_dir = os.path.join(self.storage_dir, "records")

    if os.path.exists(records_dir):
    for filename in os.listdir(records_dir):
    if filename.endswith(".json"):
    file_path = os.path.join(records_dir, filename)

    try:
    with open(file_path, "r") as f:
    data = json.load(f)

    record = UsageRecord.from_dict(data)

    # Store record
    self.records[record.id] = record

    # Add to customer index
    if record.customer_id not in self.customer_records:
    self.customer_records[record.customer_id] = []

    self.customer_records[record.customer_id].append(record.id)

    # Add to metric index
    if record.metric not in self.metric_records:
    self.metric_records[record.metric] = []

    self.metric_records[record.metric].append(record.id)

    # Add to category index
    if record.category not in self.category_records:
    self.category_records[record.category] = []

    self.category_records[record.category].append(record.id)

    # Add to resource index
    if record.resource_type:
    if record.resource_type not in self.resource_records:
    self.resource_records[record.resource_type] = []

    self.resource_records[record.resource_type].append(
    record.id
    )

except Exception as e:
    print(f"Error loading record from {file_path}: {e}")

    def _save_limit(self, limit: UsageLimit) -> None:
    """
    """
    Save a usage limit to the storage directory.
    Save a usage limit to the storage directory.


    Args:
    Args:
    limit: Usage limit to save
    limit: Usage limit to save
    """
    """
    if not self.storage_dir:
    if not self.storage_dir:
    return file_path = os.path.join(self.storage_dir, "limits", f"{limit.id}.json")
    return file_path = os.path.join(self.storage_dir, "limits", f"{limit.id}.json")


    with open(file_path, "w") as f:
    with open(file_path, "w") as f:
    f.write(limit.to_json())
    f.write(limit.to_json())


    def _save_quota(self, quota: UsageQuota) -> None:
    def _save_quota(self, quota: UsageQuota) -> None:
    """
    """
    Save a usage quota to the storage directory.
    Save a usage quota to the storage directory.


    Args:
    Args:
    quota: Usage quota to save
    quota: Usage quota to save
    """
    """
    if not self.storage_dir:
    if not self.storage_dir:
    return file_path = os.path.join(self.storage_dir, "quotas", f"{quota.id}.json")
    return file_path = os.path.join(self.storage_dir, "quotas", f"{quota.id}.json")


    with open(file_path, "w") as f:
    with open(file_path, "w") as f:
    f.write(quota.to_json())
    f.write(quota.to_json())


    def track_usage(
    def track_usage(
    self,
    self,
    customer_id: str,
    customer_id: str,
    metric: str,
    metric: str,
    quantity: float,
    quantity: float,
    category: str = UsageCategory.INFERENCE,
    category: str = UsageCategory.INFERENCE,
    resource_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    subscription_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    check_quota: bool = True,
    check_quota: bool = True,
    ) -> Tuple[UsageRecord, Optional[UsageQuota], bool]:
    ) -> Tuple[UsageRecord, Optional[UsageQuota], bool]:
    """
    """
    Track usage for a customer.
    Track usage for a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    metric: Type of usage metric
    metric: Type of usage metric
    quantity: Quantity of usage
    quantity: Quantity of usage
    category: Category of usage
    category: Category of usage
    resource_id: ID of the resource being used
    resource_id: ID of the resource being used
    resource_type: Type of resource being used
    resource_type: Type of resource being used
    subscription_id: ID of the subscription
    subscription_id: ID of the subscription
    metadata: Additional metadata for the usage record
    metadata: Additional metadata for the usage record
    check_quota: Whether to check and update quotas
    check_quota: Whether to check and update quotas


    Returns:
    Returns:
    Tuple of (usage record, updated quota, quota exceeded)
    Tuple of (usage record, updated quota, quota exceeded)
    """
    """
    # Create usage record
    # Create usage record
    record = UsageRecord(
    record = UsageRecord(
    customer_id=customer_id,
    customer_id=customer_id,
    metric=metric,
    metric=metric,
    quantity=quantity,
    quantity=quantity,
    category=category,
    category=category,
    resource_id=resource_id,
    resource_id=resource_id,
    resource_type=resource_type,
    resource_type=resource_type,
    subscription_id=subscription_id,
    subscription_id=subscription_id,
    metadata=metadata,
    metadata=metadata,
    )
    )


    # Store record
    # Store record
    self.records[record.id] = record
    self.records[record.id] = record


    # Add to customer index
    # Add to customer index
    if customer_id not in self.customer_records:
    if customer_id not in self.customer_records:
    self.customer_records[customer_id] = []
    self.customer_records[customer_id] = []


    self.customer_records[customer_id].append(record.id)
    self.customer_records[customer_id].append(record.id)


    # Add to metric index
    # Add to metric index
    if metric not in self.metric_records:
    if metric not in self.metric_records:
    self.metric_records[metric] = []
    self.metric_records[metric] = []


    self.metric_records[metric].append(record.id)
    self.metric_records[metric].append(record.id)


    # Add to category index
    # Add to category index
    if category not in self.category_records:
    if category not in self.category_records:
    self.category_records[category] = []
    self.category_records[category] = []


    self.category_records[category].append(record.id)
    self.category_records[category].append(record.id)


    # Add to resource index
    # Add to resource index
    if resource_type:
    if resource_type:
    if resource_type not in self.resource_records:
    if resource_type not in self.resource_records:
    self.resource_records[resource_type] = []
    self.resource_records[resource_type] = []


    self.resource_records[resource_type].append(record.id)
    self.resource_records[resource_type].append(record.id)


    # Save record if storage directory is set
    # Save record if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_record(record)
    self._save_record(record)


    # Check and update quota if requested
    # Check and update quota if requested
    updated_quota = None
    updated_quota = None
    quota_exceeded = False
    quota_exceeded = False


    if check_quota:
    if check_quota:
    # Find matching quota
    # Find matching quota
    quotas = self.get_customer_quotas(
    quotas = self.get_customer_quotas(
    customer_id=customer_id,
    customer_id=customer_id,
    metric=metric,
    metric=metric,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    )
    )


    if quotas:
    if quotas:
    # Use the first matching quota
    # Use the first matching quota
    quota = quotas[0]
    quota = quotas[0]


    # Update quota
    # Update quota
    quota.add_usage(quantity)
    quota.add_usage(quantity)


    # Check if quota is exceeded
    # Check if quota is exceeded
    quota_exceeded = quota.is_exceeded()
    quota_exceeded = quota.is_exceeded()


    # Save quota if storage directory is set
    # Save quota if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_quota(quota)
    self._save_quota(quota)


    updated_quota = quota
    updated_quota = quota


    return record, updated_quota, quota_exceeded
    return record, updated_quota, quota_exceeded


    def track_usage_batch(
    def track_usage_batch(
    self, records: List[Dict[str, Any]], check_quota: bool = True
    self, records: List[Dict[str, Any]], check_quota: bool = True
    ) -> List[Tuple[UsageRecord, Optional[UsageQuota], bool]]:
    ) -> List[Tuple[UsageRecord, Optional[UsageQuota], bool]]:
    """
    """
    Track usage in batch for multiple customers or metrics.
    Track usage in batch for multiple customers or metrics.


    Args:
    Args:
    records: List of usage record data
    records: List of usage record data
    check_quota: Whether to check and update quotas
    check_quota: Whether to check and update quotas


    Returns:
    Returns:
    List of tuples of (usage record, updated quota, quota exceeded)
    List of tuples of (usage record, updated quota, quota exceeded)
    """
    """
    results = []
    results = []


    for record_data in records:
    for record_data in records:
    # Track usage for each record
    # Track usage for each record
    result = self.track_usage(
    result = self.track_usage(
    customer_id=record_data["customer_id"],
    customer_id=record_data["customer_id"],
    metric=record_data["metric"],
    metric=record_data["metric"],
    quantity=record_data["quantity"],
    quantity=record_data["quantity"],
    category=record_data.get("category", UsageCategory.INFERENCE),
    category=record_data.get("category", UsageCategory.INFERENCE),
    resource_id=record_data.get("resource_id"),
    resource_id=record_data.get("resource_id"),
    resource_type=record_data.get("resource_type"),
    resource_type=record_data.get("resource_type"),
    subscription_id=record_data.get("subscription_id"),
    subscription_id=record_data.get("subscription_id"),
    metadata=record_data.get("metadata"),
    metadata=record_data.get("metadata"),
    check_quota=check_quota,
    check_quota=check_quota,
    )
    )


    results.append(result)
    results.append(result)


    return results
    return results


    def check_usage_allowed(
    def check_usage_allowed(
    self,
    self,
    customer_id: str,
    customer_id: str,
    metric: str,
    metric: str,
    quantity: float,
    quantity: float,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    ) -> Tuple[bool, Optional[str], Optional[UsageQuota]]:
    ) -> Tuple[bool, Optional[str], Optional[UsageQuota]]:
    """
    """
    Check if usage is allowed based on quotas.
    Check if usage is allowed based on quotas.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    metric: Type of usage metric
    metric: Type of usage metric
    quantity: Quantity of usage
    quantity: Quantity of usage
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource being used
    resource_type: Type of resource being used


    Returns:
    Returns:
    Tuple of (allowed, reason, quota)
    Tuple of (allowed, reason, quota)
    """
    """
    # Find matching quotas
    # Find matching quotas
    quotas = self.get_customer_quotas(
    quotas = self.get_customer_quotas(
    customer_id=customer_id,
    customer_id=customer_id,
    metric=metric,
    metric=metric,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    )
    )


    if not quotas:
    if not quotas:
    # No quotas found, usage is allowed
    # No quotas found, usage is allowed
    return True, None, None
    return True, None, None


    # Check each quota
    # Check each quota
    for quota in quotas:
    for quota in quotas:
    # Check if quota is exceeded
    # Check if quota is exceeded
    if quota.is_exceeded():
    if quota.is_exceeded():
    return False, "Quota exceeded", quota
    return False, "Quota exceeded", quota


    # Check if usage would exceed quota
    # Check if usage would exceed quota
    if quota.used_quantity + quantity > quota.allocated_quantity:
    if quota.used_quantity + quantity > quota.allocated_quantity:
    return False, "Usage would exceed quota", quota
    return False, "Usage would exceed quota", quota


    # All quotas passed, usage is allowed
    # All quotas passed, usage is allowed
    return True, None, quotas[0]
    return True, None, quotas[0]


    def get_record(self, record_id: str) -> Optional[UsageRecord]:
    def get_record(self, record_id: str) -> Optional[UsageRecord]:
    """
    """
    Get a usage record by ID.
    Get a usage record by ID.


    Args:
    Args:
    record_id: ID of the record
    record_id: ID of the record


    Returns:
    Returns:
    The usage record or None if not found
    The usage record or None if not found
    """
    """
    return self.records.get(record_id)
    return self.records.get(record_id)


    def get_customer_records(
    def get_customer_records(
    self,
    self,
    customer_id: str,
    customer_id: str,
    metric: Optional[str] = None,
    metric: Optional[str] = None,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
    limit: int = 100,
    ) -> List[UsageRecord]:
    ) -> List[UsageRecord]:
    """
    """
    Get usage records for a customer.
    Get usage records for a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    metric: Type of usage metric to filter by
    metric: Type of usage metric to filter by
    category: Category of usage to filter by
    category: Category of usage to filter by
    resource_type: Type of resource to filter by
    resource_type: Type of resource to filter by
    start_time: Start time for records
    start_time: Start time for records
    end_time: End time for records
    end_time: End time for records
    limit: Maximum number of records to return
    limit: Maximum number of records to return


    Returns:
    Returns:
    List of usage records
    List of usage records
    """
    """
    if customer_id not in self.customer_records:
    if customer_id not in self.customer_records:
    return []
    return []


    records = []
    records = []


    for record_id in self.customer_records[customer_id]:
    for record_id in self.customer_records[customer_id]:
    record = self.records.get(record_id)
    record = self.records.get(record_id)


    if not record:
    if not record:
    continue
    continue


    # Filter by metric
    # Filter by metric
    if metric and record.metric != metric:
    if metric and record.metric != metric:
    continue
    continue


    # Filter by category
    # Filter by category
    if category and record.category != category:
    if category and record.category != category:
    continue
    continue


    # Filter by resource type
    # Filter by resource type
    if resource_type and record.resource_type != resource_type:
    if resource_type and record.resource_type != resource_type:
    continue
    continue


    # Filter by time range
    # Filter by time range
    if start_time and record.timestamp < start_time:
    if start_time and record.timestamp < start_time:
    continue
    continue


    if end_time and record.timestamp > end_time:
    if end_time and record.timestamp > end_time:
    continue
    continue


    records.append(record)
    records.append(record)


    # Sort by timestamp (newest first)
    # Sort by timestamp (newest first)
    records.sort(key=lambda r: r.timestamp, reverse=True)
    records.sort(key=lambda r: r.timestamp, reverse=True)


    # Apply limit
    # Apply limit
    return records[:limit]
    return records[:limit]


    def delete_record(self, record_id: str) -> bool:
    def delete_record(self, record_id: str) -> bool:
    """
    """
    Delete a usage record.
    Delete a usage record.


    Args:
    Args:
    record_id: ID of the record to delete
    record_id: ID of the record to delete


    Returns:
    Returns:
    True if the record was deleted, False otherwise
    True if the record was deleted, False otherwise
    """
    """
    # Get record
    # Get record
    record = self.get_record(record_id)
    record = self.get_record(record_id)


    if not record:
    if not record:
    return False
    return False


    # Remove from customer index
    # Remove from customer index
    if record.customer_id in self.customer_records:
    if record.customer_id in self.customer_records:
    if record_id in self.customer_records[record.customer_id]:
    if record_id in self.customer_records[record.customer_id]:
    self.customer_records[record.customer_id].remove(record_id)
    self.customer_records[record.customer_id].remove(record_id)


    # Remove from metric index
    # Remove from metric index
    if record.metric in self.metric_records:
    if record.metric in self.metric_records:
    if record_id in self.metric_records[record.metric]:
    if record_id in self.metric_records[record.metric]:
    self.metric_records[record.metric].remove(record_id)
    self.metric_records[record.metric].remove(record_id)


    # Remove from category index
    # Remove from category index
    if record.category in self.category_records:
    if record.category in self.category_records:
    if record_id in self.category_records[record.category]:
    if record_id in self.category_records[record.category]:
    self.category_records[record.category].remove(record_id)
    self.category_records[record.category].remove(record_id)


    # Remove from resource index
    # Remove from resource index
    if record.resource_type and record.resource_type in self.resource_records:
    if record.resource_type and record.resource_type in self.resource_records:
    if record_id in self.resource_records[record.resource_type]:
    if record_id in self.resource_records[record.resource_type]:
    self.resource_records[record.resource_type].remove(record_id)
    self.resource_records[record.resource_type].remove(record_id)


    # Remove from records
    # Remove from records
    del self.records[record_id]
    del self.records[record_id]


    # Delete file if storage directory is set
    # Delete file if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    file_path = os.path.join(self.storage_dir, "records", f"{record_id}.json")
    file_path = os.path.join(self.storage_dir, "records", f"{record_id}.json")


    if os.path.exists(file_path):
    if os.path.exists(file_path):
    os.remove(file_path)
    os.remove(file_path)


    return True
    return True


    def _save_record(self, record: UsageRecord) -> None:
    def _save_record(self, record: UsageRecord) -> None:
    """
    """
    Save a usage record to the storage directory.
    Save a usage record to the storage directory.


    Args:
    Args:
    record: Usage record to save
    record: Usage record to save
    """
    """
    if not self.storage_dir:
    if not self.storage_dir:
    return file_path = os.path.join(self.storage_dir, "records", f"{record.id}.json")
    return file_path = os.path.join(self.storage_dir, "records", f"{record.id}.json")


    with open(file_path, "w") as f:
    with open(file_path, "w") as f:
    f.write(record.to_json())
    f.write(record.to_json())


    def get_usage_summary(
    def get_usage_summary(
    self,
    self,
    customer_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    metric: Optional[str] = None,
    metric: Optional[str] = None,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    group_by: Optional[str] = None,
    group_by: Optional[str] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Get a summary of usage.
    Get a summary of usage.


    Args:
    Args:
    customer_id: ID of the customer to filter by
    customer_id: ID of the customer to filter by
    metric: Type of usage metric to filter by
    metric: Type of usage metric to filter by
    category: Category of usage to filter by
    category: Category of usage to filter by
    resource_type: Type of resource to filter by
    resource_type: Type of resource to filter by
    start_time: Start time for records
    start_time: Start time for records
    end_time: End time for records
    end_time: End time for records
    group_by: Field to group by (customer, metric, category, resource_type)
    group_by: Field to group by (customer, metric, category, resource_type)


    Returns:
    Returns:
    Dictionary with usage summary
    Dictionary with usage summary
    """
    """
    # Get records to summarize
    # Get records to summarize
    records = self.get_filtered_records(
    records = self.get_filtered_records(
    customer_id=customer_id,
    customer_id=customer_id,
    metric=metric,
    metric=metric,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    start_time=start_time,
    start_time=start_time,
    end_time=end_time,
    end_time=end_time,
    )
    )


    # Initialize summary
    # Initialize summary
    summary = {
    summary = {
    "total_records": len(records),
    "total_records": len(records),
    "total_quantity": 0.0,
    "total_quantity": 0.0,
    "metrics": {},
    "metrics": {},
    "categories": {},
    "categories": {},
    "customers": {},
    "customers": {},
    "resource_types": {},
    "resource_types": {},
    }
    }


    # Group records if requested
    # Group records if requested
    if group_by:
    if group_by:
    summary["grouped"] = {}
    summary["grouped"] = {}


    # Calculate summary
    # Calculate summary
    for record in records:
    for record in records:
    # Add to total quantity
    # Add to total quantity
    summary["total_quantity"] += record.quantity
    summary["total_quantity"] += record.quantity


    # Add to metrics
    # Add to metrics
    if record.metric not in summary["metrics"]:
    if record.metric not in summary["metrics"]:
    summary["metrics"][record.metric] = {"count": 0, "quantity": 0.0}
    summary["metrics"][record.metric] = {"count": 0, "quantity": 0.0}


    summary["metrics"][record.metric]["count"] += 1
    summary["metrics"][record.metric]["count"] += 1
    summary["metrics"][record.metric]["quantity"] += record.quantity
    summary["metrics"][record.metric]["quantity"] += record.quantity


    # Add to categories
    # Add to categories
    if record.category not in summary["categories"]:
    if record.category not in summary["categories"]:
    summary["categories"][record.category] = {"count": 0, "quantity": 0.0}
    summary["categories"][record.category] = {"count": 0, "quantity": 0.0}


    summary["categories"][record.category]["count"] += 1
    summary["categories"][record.category]["count"] += 1
    summary["categories"][record.category]["quantity"] += record.quantity
    summary["categories"][record.category]["quantity"] += record.quantity


    # Add to customers
    # Add to customers
    if record.customer_id not in summary["customers"]:
    if record.customer_id not in summary["customers"]:
    summary["customers"][record.customer_id] = {"count": 0, "quantity": 0.0}
    summary["customers"][record.customer_id] = {"count": 0, "quantity": 0.0}


    summary["customers"][record.customer_id]["count"] += 1
    summary["customers"][record.customer_id]["count"] += 1
    summary["customers"][record.customer_id]["quantity"] += record.quantity
    summary["customers"][record.customer_id]["quantity"] += record.quantity


    # Add to resource types
    # Add to resource types
    if record.resource_type:
    if record.resource_type:
    if record.resource_type not in summary["resource_types"]:
    if record.resource_type not in summary["resource_types"]:
    summary["resource_types"][record.resource_type] = {
    summary["resource_types"][record.resource_type] = {
    "count": 0,
    "count": 0,
    "quantity": 0.0,
    "quantity": 0.0,
    }
    }


    summary["resource_types"][record.resource_type]["count"] += 1
    summary["resource_types"][record.resource_type]["count"] += 1
    summary["resource_types"][record.resource_type][
    summary["resource_types"][record.resource_type][
    "quantity"
    "quantity"
    ] += record.quantity
    ] += record.quantity


    # Add to grouped data if requested
    # Add to grouped data if requested
    if group_by:
    if group_by:
    group_value = None
    group_value = None


    if group_by == "customer":
    if group_by == "customer":
    group_value = record.customer_id
    group_value = record.customer_id
    elif group_by == "metric":
    elif group_by == "metric":
    group_value = record.metric
    group_value = record.metric
    elif group_by == "category":
    elif group_by == "category":
    group_value = record.category
    group_value = record.category
    elif group_by == "resource_type":
    elif group_by == "resource_type":
    group_value = record.resource_type
    group_value = record.resource_type


    if group_value:
    if group_value:
    if group_value not in summary["grouped"]:
    if group_value not in summary["grouped"]:
    summary["grouped"][group_value] = {
    summary["grouped"][group_value] = {
    "count": 0,
    "count": 0,
    "quantity": 0.0,
    "quantity": 0.0,
    "records": [],
    "records": [],
    }
    }


    summary["grouped"][group_value]["count"] += 1
    summary["grouped"][group_value]["count"] += 1
    summary["grouped"][group_value]["quantity"] += record.quantity
    summary["grouped"][group_value]["quantity"] += record.quantity
    summary["grouped"][group_value]["records"].append(record.id)
    summary["grouped"][group_value]["records"].append(record.id)


    return summary
    return summary


    def get_usage_by_time(
    def get_usage_by_time(
    self,
    self,
    customer_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    metric: Optional[str] = None,
    metric: Optional[str] = None,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    interval: str = "day",
    interval: str = "day",
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Get usage grouped by time intervals.
    Get usage grouped by time intervals.


    Args:
    Args:
    customer_id: ID of the customer to filter by
    customer_id: ID of the customer to filter by
    metric: Type of usage metric to filter by
    metric: Type of usage metric to filter by
    category: Category of usage to filter by
    category: Category of usage to filter by
    resource_type: Type of resource to filter by
    resource_type: Type of resource to filter by
    start_time: Start time for records
    start_time: Start time for records
    end_time: End time for records
    end_time: End time for records
    interval: Time interval to group by (hour, day, week, month)
    interval: Time interval to group by (hour, day, week, month)


    Returns:
    Returns:
    Dictionary with usage by time
    Dictionary with usage by time
    """
    """
    # Get records to analyze
    # Get records to analyze
    records = self.get_filtered_records(
    records = self.get_filtered_records(
    customer_id=customer_id,
    customer_id=customer_id,
    metric=metric,
    metric=metric,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    start_time=start_time,
    start_time=start_time,
    end_time=end_time,
    end_time=end_time,
    )
    )


    # Initialize result
    # Initialize result
    result = {
    result = {
    "total_records": len(records),
    "total_records": len(records),
    "total_quantity": 0.0,
    "total_quantity": 0.0,
    "interval": interval,
    "interval": interval,
    "intervals": {},
    "intervals": {},
    }
    }


    # Group records by time interval
    # Group records by time interval
    for record in records:
    for record in records:
    # Add to total quantity
    # Add to total quantity
    result["total_quantity"] += record.quantity
    result["total_quantity"] += record.quantity


    # Get interval key
    # Get interval key
    interval_key = self._get_interval_key(record.timestamp, interval)
    interval_key = self._get_interval_key(record.timestamp, interval)


    # Add to intervals
    # Add to intervals
    if interval_key not in result["intervals"]:
    if interval_key not in result["intervals"]:
    result["intervals"][interval_key] = {
    result["intervals"][interval_key] = {
    "count": 0,
    "count": 0,
    "quantity": 0.0,
    "quantity": 0.0,
    "start_time": self._get_interval_start(
    "start_time": self._get_interval_start(
    record.timestamp, interval
    record.timestamp, interval
    ).isoformat(),
    ).isoformat(),
    "end_time": self._get_interval_end(
    "end_time": self._get_interval_end(
    record.timestamp, interval
    record.timestamp, interval
    ).isoformat(),
    ).isoformat(),
    }
    }


    result["intervals"][interval_key]["count"] += 1
    result["intervals"][interval_key]["count"] += 1
    result["intervals"][interval_key]["quantity"] += record.quantity
    result["intervals"][interval_key]["quantity"] += record.quantity


    return result
    return result


    def get_usage_trends(
    def get_usage_trends(
    self,
    self,
    customer_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    metric: Optional[str] = None,
    metric: Optional[str] = None,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    interval: str = "day",
    interval: str = "day",
    num_intervals: int = 30,
    num_intervals: int = 30,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Generate comprehensive usage trend analysis with intelligent pattern detection.
    Generate comprehensive usage trend analysis with intelligent pattern detection.


    This algorithm implements a sophisticated time-series analysis system for
    This algorithm implements a sophisticated time-series analysis system for
    detecting and quantifying usage patterns across multiple dimensions. The
    detecting and quantifying usage patterns across multiple dimensions. The
    implementation follows these key phases:
    implementation follows these key phases:


    1. TIME RANGE DETERMINATION AND NORMALIZATION:
    1. TIME RANGE DETERMINATION AND NORMALIZATION:
    - Establishes proper time boundaries based on requested analysis period
    - Establishes proper time boundaries based on requested analysis period
    - Applies intelligent defaults for missing time parameters
    - Applies intelligent defaults for missing time parameters
    - Normalizes the time range to ensure complete interval coverage
    - Normalizes the time range to ensure complete interval coverage
    - Handles various time granularities (hour, day, week, month) appropriately
    - Handles various time granularities (hour, day, week, month) appropriately
    - Creates proper interval alignment for accurate trend analysis
    - Creates proper interval alignment for accurate trend analysis


    2. TEMPORAL DATA AGGREGATION AND GAP FILLING:
    2. TEMPORAL DATA AGGREGATION AND GAP FILLING:
    - Collects and aggregates usage data into consistent time buckets
    - Collects and aggregates usage data into consistent time buckets
    - Handles sparse data by properly zero-filling missing intervals
    - Handles sparse data by properly zero-filling missing intervals
    - Ensures complete time-series continuity for accurate trend analysis
    - Ensures complete time-series continuity for accurate trend analysis
    - Maintains chronological ordering of data points
    - Maintains chronological ordering of data points
    - Preserves temporal relationships between data points
    - Preserves temporal relationships between data points


    3. STATISTICAL TREND IDENTIFICATION:
    3. STATISTICAL TREND IDENTIFICATION:
    - Divides time-series data into equal analysis segments
    - Divides time-series data into equal analysis segments
    - Calculates summary statistics for each segment
    - Calculates summary statistics for each segment
    - Applies comparative analysis between segments
    - Applies comparative analysis between segments
    - Quantifies the direction and magnitude of usage changes
    - Quantifies the direction and magnitude of usage changes
    - Determines statistically significant trends versus normal variance
    - Determines statistically significant trends versus normal variance


    4. TREND CLASSIFICATION AND INTERPRETATION:
    4. TREND CLASSIFICATION AND INTERPRETATION:
    - Categorizes usage patterns (increasing, decreasing, stable)
    - Categorizes usage patterns (increasing, decreasing, stable)
    - Quantifies percentage changes for objective measurement
    - Quantifies percentage changes for objective measurement
    - Applies thresholds for meaningful trend detection
    - Applies thresholds for meaningful trend detection
    - Provides numerical values for trend strength assessment
    - Provides numerical values for trend strength assessment
    - Delivers actionable insights through pattern classification
    - Delivers actionable insights through pattern classification


    This trend analysis algorithm addresses several critical business requirements:
    This trend analysis algorithm addresses several critical business requirements:
    - Early detection of changing usage patterns
    - Early detection of changing usage patterns
    - Quantitative measurement of growth or decline rates
    - Quantitative measurement of growth or decline rates
    - Support for capacity planning and resource allocation
    - Support for capacity planning and resource allocation
    - Identification of customer behavior changes
    - Identification of customer behavior changes
    - Foundation for predictive analytics and forecasting
    - Foundation for predictive analytics and forecasting


    The implementation specifically supports common business scenarios:
    The implementation specifically supports common business scenarios:
    - Monitoring customer engagement over time
    - Monitoring customer engagement over time
    - Detecting unusual spikes or drops in API usage
    - Detecting unusual spikes or drops in API usage
    - Measuring adoption rates of new features
    - Measuring adoption rates of new features
    - Analyzing resource utilization trends
    - Analyzing resource utilization trends
    - Identifying seasonal patterns in usage behavior
    - Identifying seasonal patterns in usage behavior


    Args:
    Args:
    customer_id: Optional customer identifier to filter usage data
    customer_id: Optional customer identifier to filter usage data
    metric: Optional usage metric type (e.g., API_CALL, STORAGE) to analyze
    metric: Optional usage metric type (e.g., API_CALL, STORAGE) to analyze
    category: Optional usage category (e.g., INFERENCE) to filter by
    category: Optional usage category (e.g., INFERENCE) to filter by
    resource_type: Optional resource type (e.g., model) to filter by
    resource_type: Optional resource type (e.g., model) to filter by
    start_time: Beginning of analysis period (auto-calculated if not provided)
    start_time: Beginning of analysis period (auto-calculated if not provided)
    end_time: End of analysis period (defaults to current time if not provided)
    end_time: End of analysis period (defaults to current time if not provided)
    interval: Time bucket size for aggregation (hour, day, week, month)
    interval: Time bucket size for aggregation (hour, day, week, month)
    num_intervals: Number of intervals to include when auto-calculating time range
    num_intervals: Number of intervals to include when auto-calculating time range


    Returns:
    Returns:
    Comprehensive dictionary containing:
    Comprehensive dictionary containing:
    - Complete time-series data with consistent intervals
    - Complete time-series data with consistent intervals
    - Statistical summary of usage volumes
    - Statistical summary of usage volumes
    - Trend direction classification (increasing, decreasing, stable)
    - Trend direction classification (increasing, decreasing, stable)
    - Quantified percentage change measurement
    - Quantified percentage change measurement
    - Interval-specific usage breakdowns
    - Interval-specific usage breakdowns
    """
    """
    # PHASE 1: Time Range Determination and Normalization
    # PHASE 1: Time Range Determination and Normalization
    # Set default end time to now if not provided
    # Set default end time to now if not provided
    if end_time is None:
    if end_time is None:
    end_time = datetime.now()
    end_time = datetime.now()


    # Calculate appropriate start time based on interval and requested span
    # Calculate appropriate start time based on interval and requested span
    if start_time is None:
    if start_time is None:
    if interval == "hour":
    if interval == "hour":
    start_time = end_time - timedelta(hours=num_intervals)
    start_time = end_time - timedelta(hours=num_intervals)
    elif interval == "day":
    elif interval == "day":
    start_time = end_time - timedelta(days=num_intervals)
    start_time = end_time - timedelta(days=num_intervals)
    elif interval == "week":
    elif interval == "week":
    start_time = end_time - timedelta(weeks=num_intervals)
    start_time = end_time - timedelta(weeks=num_intervals)
    elif interval == "month":
    elif interval == "month":
    # Approximate months as 30 days for consistent calculation
    # Approximate months as 30 days for consistent calculation
    start_time = end_time - timedelta(days=30 * num_intervals)
    start_time = end_time - timedelta(days=30 * num_intervals)
    else:
    else:
    raise ValueError(f"Invalid interval: {interval}")
    raise ValueError(f"Invalid interval: {interval}")


    # PHASE 2: Temporal Data Aggregation and Gap Filling
    # PHASE 2: Temporal Data Aggregation and Gap Filling
    # Get base usage data aggregated by the specified time interval
    # Get base usage data aggregated by the specified time interval
    usage_by_time = self.get_usage_by_time(
    usage_by_time = self.get_usage_by_time(
    customer_id=customer_id,
    customer_id=customer_id,
    metric=metric,
    metric=metric,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    start_time=start_time,
    start_time=start_time,
    end_time=end_time,
    end_time=end_time,
    interval=interval,
    interval=interval,
    )
    )


    # Generate complete sequence of intervals to ensure gap-free analysis
    # Generate complete sequence of intervals to ensure gap-free analysis
    all_intervals = []
    all_intervals = []
    current_time = start_time
    current_time = start_time


    # Iterate through the entire time range to generate all interval keys
    # Iterate through the entire time range to generate all interval keys
    while current_time <= end_time:
    while current_time <= end_time:
    interval_key = self._get_interval_key(current_time, interval)
    interval_key = self._get_interval_key(current_time, interval)
    all_intervals.append(interval_key)
    all_intervals.append(interval_key)


    # Advance to the next interval using appropriate time increment
    # Advance to the next interval using appropriate time increment
    if interval == "hour":
    if interval == "hour":
    current_time += timedelta(hours=1)
    current_time += timedelta(hours=1)
    elif interval == "day":
    elif interval == "day":
    current_time += timedelta(days=1)
    current_time += timedelta(days=1)
    elif interval == "week":
    elif interval == "week":
    current_time += timedelta(weeks=1)
    current_time += timedelta(weeks=1)
    elif interval == "month":
    elif interval == "month":
    # Special handling for month boundaries to maintain proper calendar alignment
    # Special handling for month boundaries to maintain proper calendar alignment
    if current_time.month == 12:
    if current_time.month == 12:
    current_time = datetime(current_time.year + 1, 1, 1)
    current_time = datetime(current_time.year + 1, 1, 1)
    else:
    else:
    current_time = datetime(
    current_time = datetime(
    current_time.year, current_time.month + 1, 1
    current_time.year, current_time.month + 1, 1
    )
    )


    # Initialize the trend analysis result structure
    # Initialize the trend analysis result structure
    trends = {
    trends = {
    "total_records": usage_by_time["total_records"],
    "total_records": usage_by_time["total_records"],
    "total_quantity": usage_by_time["total_quantity"],
    "total_quantity": usage_by_time["total_quantity"],
    "interval": interval,
    "interval": interval,
    "start_time": start_time.isoformat(),
    "start_time": start_time.isoformat(),
    "end_time": end_time.isoformat(),
    "end_time": end_time.isoformat(),
    "intervals": [],
    "intervals": [],
    "trend": {"direction": "stable", "percentage_change": 0.0},
    "trend": {"direction": "stable", "percentage_change": 0.0},
    }
    }


    # PHASE 2 Continued: Fill gaps in the time series data for complete analysis
    # PHASE 2 Continued: Fill gaps in the time series data for complete analysis
    # Process each interval in the time range, inserting zero values where needed
    # Process each interval in the time range, inserting zero values where needed
    for interval_key in all_intervals:
    for interval_key in all_intervals:
    if interval_key in usage_by_time["intervals"]:
    if interval_key in usage_by_time["intervals"]:
    # Use actual usage data when available
    # Use actual usage data when available
    interval_data = usage_by_time["intervals"][interval_key]
    interval_data = usage_by_time["intervals"][interval_key]
    else:
    else:
    # Create zero-filled data for intervals with no recorded usage
    # Create zero-filled data for intervals with no recorded usage
    # This ensures continuity of the time series for accurate trend analysis
    # This ensures continuity of the time series for accurate trend analysis
    interval_data = {
    interval_data = {
    "count": 0,
    "count": 0,
    "quantity": 0.0,
    "quantity": 0.0,
    "start_time": self._get_interval_start(
    "start_time": self._get_interval_start(
    self._parse_interval_key(interval_key, interval), interval
    self._parse_interval_key(interval_key, interval), interval
    ).isoformat(),
    ).isoformat(),
    "end_time": self._get_interval_end(
    "end_time": self._get_interval_end(
    self._parse_interval_key(interval_key, interval), interval
    self._parse_interval_key(interval_key, interval), interval
    ).isoformat(),
    ).isoformat(),
    }
    }


    # Add interval identifier to maintain proper chronological order
    # Add interval identifier to maintain proper chronological order
    interval_data["interval"] = interval_key
    interval_data["interval"] = interval_key


    # Build the complete time series with all intervals represented
    # Build the complete time series with all intervals represented
    trends["intervals"].append(interval_data)
    trends["intervals"].append(interval_data)


    # PHASE 3 & 4: Statistical Trend Identification and Classification
    # PHASE 3 & 4: Statistical Trend Identification and Classification
    # Analyze for trends when sufficient data is available
    # Analyze for trends when sufficient data is available
    if len(trends["intervals"]) >= 2:
    if len(trends["intervals"]) >= 2:
    # Split the time series into two equal segments for comparison
    # Split the time series into two equal segments for comparison
    half_point = len(trends["intervals"]) // 2
    half_point = len(trends["intervals"]) // 2
    first_half = trends["intervals"][:half_point]
    first_half = trends["intervals"][:half_point]
    second_half = trends["intervals"][half_point:]
    second_half = trends["intervals"][half_point:]


    # Calculate the average usage quantity for each half of the time series
    # Calculate the average usage quantity for each half of the time series
    first_half_avg = (
    first_half_avg = (
    sum(i["quantity"] for i in first_half) / len(first_half)
    sum(i["quantity"] for i in first_half) / len(first_half)
    if first_half
    if first_half
    else 0
    else 0
    )
    )
    second_half_avg = (
    second_half_avg = (
    sum(i["quantity"] for i in second_half) / len(second_half)
    sum(i["quantity"] for i in second_half) / len(second_half)
    if second_half
    if second_half
    else 0
    else 0
    )
    )


    # Calculate percentage change between the two periods
    # Calculate percentage change between the two periods
    # Handle division by zero case for when the first period had no usage
    # Handle division by zero case for when the first period had no usage
    if first_half_avg > 0:
    if first_half_avg > 0:
    percentage_change = (
    percentage_change = (
    (second_half_avg - first_half_avg) / first_half_avg
    (second_half_avg - first_half_avg) / first_half_avg
    ) * 100
    ) * 100
    else:
    else:
    # Special handling for cases where usage started from zero
    # Special handling for cases where usage started from zero
    percentage_change = 0 if second_half_avg == 0 else 100
    percentage_change = 0 if second_half_avg == 0 else 100


    # Classify the trend direction using percentage thresholds
    # Classify the trend direction using percentage thresholds
    # This provides a simple but effective categorization of usage patterns
    # This provides a simple but effective categorization of usage patterns
    if percentage_change > 5:
    if percentage_change > 5:
    direction = "increasing"
    direction = "increasing"
    elif percentage_change < -5:
    elif percentage_change < -5:
    direction = "decreasing"
    direction = "decreasing"
    else:
    else:
    direction = "stable"
    direction = "stable"


    # Record the trend analysis results
    # Record the trend analysis results
    trends["trend"] = {
    trends["trend"] = {
    "direction": direction,
    "direction": direction,
    "percentage_change": percentage_change,
    "percentage_change": percentage_change,
    }
    }


    return trends
    return trends


    def get_quota_status(
    def get_quota_status(
    self,
    self,
    customer_id: str,
    customer_id: str,
    metric: Optional[str] = None,
    metric: Optional[str] = None,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Get the status of quotas for a customer.
    Get the status of quotas for a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    metric: Type of usage metric to filter by
    metric: Type of usage metric to filter by
    category: Category of usage to filter by
    category: Category of usage to filter by
    resource_type: Type of resource to filter by
    resource_type: Type of resource to filter by


    Returns:
    Returns:
    Dictionary with quota status
    Dictionary with quota status
    """
    """
    # Get quotas
    # Get quotas
    quotas = self.get_customer_quotas(
    quotas = self.get_customer_quotas(
    customer_id=customer_id,
    customer_id=customer_id,
    metric=metric,
    metric=metric,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    )
    )


    # Initialize result
    # Initialize result
    result = {
    result = {
    "customer_id": customer_id,
    "customer_id": customer_id,
    "total_quotas": len(quotas),
    "total_quotas": len(quotas),
    "quotas": [],
    "quotas": [],
    "summary": {"exceeded": 0, "near_limit": 0, "healthy": 0},
    "summary": {"exceeded": 0, "near_limit": 0, "healthy": 0},
    }
    }


    # Add quota status
    # Add quota status
    for quota in quotas:
    for quota in quotas:
    quota_status = {
    quota_status = {
    "id": quota.id,
    "id": quota.id,
    "metric": quota.metric,
    "metric": quota.metric,
    "category": quota.category,
    "category": quota.category,
    "resource_type": quota.resource_type,
    "resource_type": quota.resource_type,
    "allocated_quantity": quota.allocated_quantity,
    "allocated_quantity": quota.allocated_quantity,
    "used_quantity": quota.used_quantity,
    "used_quantity": quota.used_quantity,
    "remaining_quantity": quota.get_remaining_quantity(),
    "remaining_quantity": quota.get_remaining_quantity(),
    "usage_percentage": quota.get_usage_percentage(),
    "usage_percentage": quota.get_usage_percentage(),
    "is_exceeded": quota.is_exceeded(),
    "is_exceeded": quota.is_exceeded(),
    "is_near_limit": quota.is_near_limit(),
    "is_near_limit": quota.is_near_limit(),
    "reset_at": quota.reset_at.isoformat(),
    "reset_at": quota.reset_at.isoformat(),
    }
    }


    # Add to summary
    # Add to summary
    if quota_status["is_exceeded"]:
    if quota_status["is_exceeded"]:
    result["summary"]["exceeded"] += 1
    result["summary"]["exceeded"] += 1
    elif quota_status["is_near_limit"]:
    elif quota_status["is_near_limit"]:
    result["summary"]["near_limit"] += 1
    result["summary"]["near_limit"] += 1
    else:
    else:
    result["summary"]["healthy"] += 1
    result["summary"]["healthy"] += 1


    # Add to quotas
    # Add to quotas
    result["quotas"].append(quota_status)
    result["quotas"].append(quota_status)


    return result
    return result


    def get_filtered_records(
    def get_filtered_records(
    self,
    self,
    customer_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    metric: Optional[str] = None,
    metric: Optional[str] = None,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    ) -> List[UsageRecord]:
    ) -> List[UsageRecord]:
    """
    """
    Get filtered usage records.
    Get filtered usage records.


    Args:
    Args:
    customer_id: ID of the customer to filter by
    customer_id: ID of the customer to filter by
    metric: Type of usage metric to filter by
    metric: Type of usage metric to filter by
    category: Category of usage to filter by
    category: Category of usage to filter by
    resource_type: Type of resource to filter by
    resource_type: Type of resource to filter by
    start_time: Start time for records
    start_time: Start time for records
    end_time: End time for records
    end_time: End time for records


    Returns:
    Returns:
    List of filtered usage records
    List of filtered usage records
    """
    """
    # Start with all records
    # Start with all records
    if customer_id:
    if customer_id:
    # Get records for the customer
    # Get records for the customer
    records = self.get_customer_records(
    records = self.get_customer_records(
    customer_id=customer_id,
    customer_id=customer_id,
    metric=metric,
    metric=metric,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    start_time=start_time,
    start_time=start_time,
    end_time=end_time,
    end_time=end_time,
    limit=1000000,  # Use a high limit to get all records
    limit=1000000,  # Use a high limit to get all records
    )
    )
    elif metric:
    elif metric:
    # Get records for the metric
    # Get records for the metric
    records = []
    records = []


    if metric in self.metric_records:
    if metric in self.metric_records:
    for record_id in self.metric_records[metric]:
    for record_id in self.metric_records[metric]:
    record = self.records.get(record_id)
    record = self.records.get(record_id)


    if not record:
    if not record:
    continue
    continue


    # Filter by category
    # Filter by category
    if category and record.category != category:
    if category and record.category != category:
    continue
    continue


    # Filter by resource type
    # Filter by resource type
    if resource_type and record.resource_type != resource_type:
    if resource_type and record.resource_type != resource_type:
    continue
    continue


    # Filter by time range
    # Filter by time range
    if start_time and record.timestamp < start_time:
    if start_time and record.timestamp < start_time:
    continue
    continue


    if end_time and record.timestamp > end_time:
    if end_time and record.timestamp > end_time:
    continue
    continue


    records.append(record)
    records.append(record)
    elif category:
    elif category:
    # Get records for the category
    # Get records for the category
    records = []
    records = []


    if category in self.category_records:
    if category in self.category_records:
    for record_id in self.category_records[category]:
    for record_id in self.category_records[category]:
    record = self.records.get(record_id)
    record = self.records.get(record_id)


    if not record:
    if not record:
    continue
    continue


    # Filter by resource type
    # Filter by resource type
    if resource_type and record.resource_type != resource_type:
    if resource_type and record.resource_type != resource_type:
    continue
    continue


    # Filter by time range
    # Filter by time range
    if start_time and record.timestamp < start_time:
    if start_time and record.timestamp < start_time:
    continue
    continue


    if end_time and record.timestamp > end_time:
    if end_time and record.timestamp > end_time:
    continue
    continue


    records.append(record)
    records.append(record)
    elif resource_type:
    elif resource_type:
    # Get records for the resource type
    # Get records for the resource type
    records = []
    records = []


    if resource_type in self.resource_records:
    if resource_type in self.resource_records:
    for record_id in self.resource_records[resource_type]:
    for record_id in self.resource_records[resource_type]:
    record = self.records.get(record_id)
    record = self.records.get(record_id)


    if not record:
    if not record:
    continue
    continue


    # Filter by time range
    # Filter by time range
    if start_time and record.timestamp < start_time:
    if start_time and record.timestamp < start_time:
    continue
    continue


    if end_time and record.timestamp > end_time:
    if end_time and record.timestamp > end_time:
    continue
    continue


    records.append(record)
    records.append(record)
    else:
    else:
    # Get all records
    # Get all records
    records = list(self.records.values())
    records = list(self.records.values())


    # Filter by time range
    # Filter by time range
    if start_time or end_time:
    if start_time or end_time:
    filtered_records = []
    filtered_records = []


    for record in records:
    for record in records:
    if start_time and record.timestamp < start_time:
    if start_time and record.timestamp < start_time:
    continue
    continue


    if end_time and record.timestamp > end_time:
    if end_time and record.timestamp > end_time:
    continue
    continue


    filtered_records.append(record)
    filtered_records.append(record)


    records = filtered_records
    records = filtered_records


    return records
    return records


    def _get_interval_key(self, timestamp: datetime, interval: str) -> str:
    def _get_interval_key(self, timestamp: datetime, interval: str) -> str:
    """
    """
    Get a key for a time interval.
    Get a key for a time interval.


    Args:
    Args:
    timestamp: Timestamp to get the key for
    timestamp: Timestamp to get the key for
    interval: Time interval (hour, day, week, month)
    interval: Time interval (hour, day, week, month)


    Returns:
    Returns:
    Interval key
    Interval key
    """
    """
    if interval == "hour":
    if interval == "hour":
    return timestamp.strftime("%Y-%m-%d-%H")
    return timestamp.strftime("%Y-%m-%d-%H")
    elif interval == "day":
    elif interval == "day":
    return timestamp.strftime("%Y-%m-%d")
    return timestamp.strftime("%Y-%m-%d")
    elif interval == "week":
    elif interval == "week":
    # Get the start of the week (Monday)
    # Get the start of the week (Monday)
    start_of_week = timestamp - timedelta(days=timestamp.weekday())
    start_of_week = timestamp - timedelta(days=timestamp.weekday())
    return start_of_week.strftime("%Y-%m-%d")
    return start_of_week.strftime("%Y-%m-%d")
    elif interval == "month":
    elif interval == "month":
    return timestamp.strftime("%Y-%m")
    return timestamp.strftime("%Y-%m")
    else:
    else:
    raise ValueError(f"Invalid interval: {interval}")
    raise ValueError(f"Invalid interval: {interval}")


    def _parse_interval_key(self, interval_key: str, interval: str) -> datetime:
    def _parse_interval_key(self, interval_key: str, interval: str) -> datetime:
    """
    """
    Parse a time interval key into a datetime.
    Parse a time interval key into a datetime.


    Args:
    Args:
    interval_key: Interval key to parse
    interval_key: Interval key to parse
    interval: Time interval (hour, day, week, month)
    interval: Time interval (hour, day, week, month)


    Returns:
    Returns:
    Datetime for the interval
    Datetime for the interval
    """
    """
    if interval == "hour":
    if interval == "hour":
    return datetime.strptime(interval_key, "%Y-%m-%d-%H")
    return datetime.strptime(interval_key, "%Y-%m-%d-%H")
    elif interval == "day" or interval == "week":
    elif interval == "day" or interval == "week":
    return datetime.strptime(interval_key, "%Y-%m-%d")
    return datetime.strptime(interval_key, "%Y-%m-%d")
    elif interval == "month":
    elif interval == "month":
    return datetime.strptime(interval_key + "-01", "%Y-%m-%d")
    return datetime.strptime(interval_key + "-01", "%Y-%m-%d")
    else:
    else:
    raise ValueError(f"Invalid interval: {interval}")
    raise ValueError(f"Invalid interval: {interval}")


    def _get_interval_start(self, timestamp: datetime, interval: str) -> datetime:
    def _get_interval_start(self, timestamp: datetime, interval: str) -> datetime:
    """
    """
    Get the start of a time interval.
    Get the start of a time interval.


    Args:
    Args:
    timestamp: Timestamp within the interval
    timestamp: Timestamp within the interval
    interval: Time interval (hour, day, week, month)
    interval: Time interval (hour, day, week, month)


    Returns:
    Returns:
    Start of the interval
    Start of the interval
    """
    """
    if interval == "hour":
    if interval == "hour":
    return datetime(
    return datetime(
    timestamp.year, timestamp.month, timestamp.day, timestamp.hour
    timestamp.year, timestamp.month, timestamp.day, timestamp.hour
    )
    )
    elif interval == "day":
    elif interval == "day":
    return datetime(timestamp.year, timestamp.month, timestamp.day)
    return datetime(timestamp.year, timestamp.month, timestamp.day)
    elif interval == "week":
    elif interval == "week":
    # Start of the week (Monday)
    # Start of the week (Monday)
    days_since_monday = timestamp.weekday()
    days_since_monday = timestamp.weekday()
    return datetime(timestamp.year, timestamp.month, timestamp.day) - timedelta(
    return datetime(timestamp.year, timestamp.month, timestamp.day) - timedelta(
    days=days_since_monday
    days=days_since_monday
    )
    )
    elif interval == "month":
    elif interval == "month":
    return datetime(timestamp.year, timestamp.month, 1)
    return datetime(timestamp.year, timestamp.month, 1)
    else:
    else:
    raise ValueError(f"Invalid interval: {interval}")
    raise ValueError(f"Invalid interval: {interval}")


    def _get_interval_end(self, timestamp: datetime, interval: str) -> datetime:
    def _get_interval_end(self, timestamp: datetime, interval: str) -> datetime:
    """
    """
    Get the end of a time interval.
    Get the end of a time interval.


    Args:
    Args:
    timestamp: Timestamp within the interval
    timestamp: Timestamp within the interval
    interval: Time interval (hour, day, week, month)
    interval: Time interval (hour, day, week, month)


    Returns:
    Returns:
    End of the interval
    End of the interval
    """
    """
    start = self._get_interval_start(timestamp, interval)
    start = self._get_interval_start(timestamp, interval)


    if interval == "hour":
    if interval == "hour":
    return start + timedelta(hours=1) - timedelta(microseconds=1)
    return start + timedelta(hours=1) - timedelta(microseconds=1)
    elif interval == "day":
    elif interval == "day":
    return start + timedelta(days=1) - timedelta(microseconds=1)
    return start + timedelta(days=1) - timedelta(microseconds=1)
    elif interval == "week":
    elif interval == "week":
    return start + timedelta(days=7) - timedelta(microseconds=1)
    return start + timedelta(days=7) - timedelta(microseconds=1)
    elif interval == "month":
    elif interval == "month":
    # Last day of the month
    # Last day of the month
    if start.month == 12:
    if start.month == 12:
    next_month = datetime(start.year + 1, 1, 1)
    next_month = datetime(start.year + 1, 1, 1)
    else:
    else:
    next_month = datetime(start.year, start.month + 1, 1)
    next_month = datetime(start.year, start.month + 1, 1)
    return next_month - timedelta(microseconds=1)
    return next_month - timedelta(microseconds=1)
    else:
    else:
    raise ValueError(f"Invalid interval: {interval}")
    raise ValueError(f"Invalid interval: {interval}")




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Create a usage tracker
    # Create a usage tracker
    tracker = UsageTracker(storage_dir="usage_data")
    tracker = UsageTracker(storage_dir="usage_data")


    # Add a usage limit
    # Add a usage limit
    limit = UsageLimit(
    limit = UsageLimit(
    customer_id="cust_123",
    customer_id="cust_123",
    metric=UsageMetric.API_CALL,
    metric=UsageMetric.API_CALL,
    max_quantity=1000,
    max_quantity=1000,
    period=UsageLimit.PERIOD_MONTHLY,
    period=UsageLimit.PERIOD_MONTHLY,
    category=UsageCategory.INFERENCE,
    category=UsageCategory.INFERENCE,
    resource_type="model",
    resource_type="model",
    metadata={"tier": "basic"},
    metadata={"tier": "basic"},
    )
    )


    tracker.add_limit(limit)
    tracker.add_limit(limit)


    print(f"Added limit: {limit}")
    print(f"Added limit: {limit}")


    # Get customer limits
    # Get customer limits
    limits = tracker.get_customer_limits("cust_123")
    limits = tracker.get_customer_limits("cust_123")


    print(f"\nCustomer limits ({len(limits)}):")
    print(f"\nCustomer limits ({len(limits)}):")
    for l in limits:
    for l in limits:
    print(f"- {l}")
    print(f"- {l}")


    # Get customer quotas
    # Get customer quotas
    quotas = tracker.get_customer_quotas("cust_123")
    quotas = tracker.get_customer_quotas("cust_123")


    print(f"\nCustomer quotas ({len(quotas)}):")
    print(f"\nCustomer quotas ({len(quotas)}):")
    for q in quotas:
    for q in quotas:
    print(f"- {q}")
    print(f"- {q}")


    # Track some usage
    # Track some usage
    print("\nTracking usage...")
    print("\nTracking usage...")


    for i in range(5):
    for i in range(5):
    record, quota, exceeded = tracker.track_usage(
    record, quota, exceeded = tracker.track_usage(
    customer_id="cust_123",
    customer_id="cust_123",
    metric=UsageMetric.API_CALL,
    metric=UsageMetric.API_CALL,
    quantity=10,
    quantity=10,
    category=UsageCategory.INFERENCE,
    category=UsageCategory.INFERENCE,
    resource_id="model_gpt4",
    resource_id="model_gpt4",
    resource_type="model",
    resource_type="model",
    metadata={"endpoint": "/v1/completions"},
    metadata={"endpoint": "/v1/completions"},
    )
    )


    print(f"Tracked usage: {record}")
    print(f"Tracked usage: {record}")


    # Get usage summary
    # Get usage summary
    summary = tracker.get_usage_summary(customer_id="cust_123")
    summary = tracker.get_usage_summary(customer_id="cust_123")


    print("\nUsage summary:")
    print("\nUsage summary:")
    print(f"Total records: {summary['total_records']}")
    print(f"Total records: {summary['total_records']}")
    print(f"Total quantity: {summary['total_quantity']}")
    print(f"Total quantity: {summary['total_quantity']}")


    # Get quota status
    # Get quota status
    status = tracker.get_quota_status(customer_id="cust_123")
    status = tracker.get_quota_status(customer_id="cust_123")


    print("\nQuota status:")
    print("\nQuota status:")
    print(f"Total quotas: {status['total_quotas']}")
    print(f"Total quotas: {status['total_quotas']}")
    print(f"Exceeded: {status['summary']['exceeded']}")
    print(f"Exceeded: {status['summary']['exceeded']}")
    print(f"Near limit: {status['summary']['near_limit']}")
    print(f"Near limit: {status['summary']['near_limit']}")
    print(f"Healthy: {status['summary']['healthy']}")
    print(f"Healthy: {status['summary']['healthy']}")


    for quota_status in status["quotas"]:
    for quota_status in status["quotas"]:
    print(
    print(
    f"- {quota_status['metric']}: {quota_status['used_quantity']}/{quota_status['allocated_quantity']} ({quota_status['usage_percentage']:.2f}%)"
    f"- {quota_status['metric']}: {quota_status['used_quantity']}/{quota_status['allocated_quantity']} ({quota_status['usage_percentage']:.2f}%)"
    )
    )