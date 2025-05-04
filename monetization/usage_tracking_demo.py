"""
"""
Usage tracking demo for the pAIssive Income project.
Usage tracking demo for the pAIssive Income project.


This script demonstrates how to use the usage tracking system.
This script demonstrates how to use the usage tracking system.
"""
"""


import random
import random
import time
import time
from datetime import datetime, timedelta
from datetime import datetime, timedelta


from .usage_tracker import UsageTracker
from .usage_tracker import UsageTracker


(
(
UsageCategory,
UsageCategory,
UsageLimit,
UsageLimit,
UsageMetric,
UsageMetric,
)
)




def print_separator():
    def print_separator():
    """Print a separator line."""
    print("\n" + "-" * 80 + "\n")


    def generate_random_usage(
    tracker: UsageTracker, customer_id: str, num_records: int = 100, days_back: int = 30
    ) -> None:
    """
    """
    Generate random usage records for a customer.
    Generate random usage records for a customer.


    Args:
    Args:
    tracker: Usage tracker
    tracker: Usage tracker
    customer_id: ID of the customer
    customer_id: ID of the customer
    num_records: Number of records to generate
    num_records: Number of records to generate
    days_back: Number of days back to generate records for
    days_back: Number of days back to generate records for
    """
    """
    # Define metrics and categories
    # Define metrics and categories
    metrics = [
    metrics = [
    UsageMetric.API_CALL,
    UsageMetric.API_CALL,
    UsageMetric.COMPUTE_TIME,
    UsageMetric.COMPUTE_TIME,
    UsageMetric.TOKEN,
    UsageMetric.TOKEN,
    UsageMetric.STORAGE,
    UsageMetric.STORAGE,
    ]
    ]


    categories = [
    categories = [
    UsageCategory.INFERENCE,
    UsageCategory.INFERENCE,
    UsageCategory.TRAINING,
    UsageCategory.TRAINING,
    UsageCategory.EMBEDDING,
    UsageCategory.EMBEDDING,
    UsageCategory.STORAGE,
    UsageCategory.STORAGE,
    ]
    ]


    resource_types = ["model", "database", "storage", "compute"]
    resource_types = ["model", "database", "storage", "compute"]


    resource_ids = [
    resource_ids = [
    "model_gpt4",
    "model_gpt4",
    "model_llama",
    "model_llama",
    "db_postgres",
    "db_postgres",
    "storage_s3",
    "storage_s3",
    "compute_gpu",
    "compute_gpu",
    ]
    ]


    # Generate random usage records
    # Generate random usage records
    now = datetime.now()
    now = datetime.now()


    for i in range(num_records):
    for i in range(num_records):
    # Random timestamp within the last days_back days
    # Random timestamp within the last days_back days
    days_ago = random.uniform(0, days_back)
    days_ago = random.uniform(0, days_back)
    timestamp = now - timedelta(days=days_ago)
    timestamp = now - timedelta(days=days_ago)


    # Random metric and category
    # Random metric and category
    metric = random.choice(metrics)
    metric = random.choice(metrics)
    category = random.choice(categories)
    category = random.choice(categories)


    # Random resource type and ID
    # Random resource type and ID
    resource_type = random.choice(resource_types)
    resource_type = random.choice(resource_types)
    resource_id = random.choice(resource_ids)
    resource_id = random.choice(resource_ids)


    # Random quantity
    # Random quantity
    if metric == UsageMetric.API_CALL:
    if metric == UsageMetric.API_CALL:
    quantity = random.randint(1, 10)
    quantity = random.randint(1, 10)
    elif metric == UsageMetric.COMPUTE_TIME:
    elif metric == UsageMetric.COMPUTE_TIME:
    quantity = random.uniform(0.1, 5.0)
    quantity = random.uniform(0.1, 5.0)
    elif metric == UsageMetric.TOKEN:
    elif metric == UsageMetric.TOKEN:
    quantity = random.randint(10, 1000)
    quantity = random.randint(10, 1000)
    elif metric == UsageMetric.STORAGE:
    elif metric == UsageMetric.STORAGE:
    quantity = random.uniform(0.1, 10.0)
    quantity = random.uniform(0.1, 10.0)
    else:
    else:
    quantity = random.uniform(1, 100)
    quantity = random.uniform(1, 100)


    # Random metadata
    # Random metadata
    metadata = {
    metadata = {
    "endpoint": f"/v1/{random.choice(['completions', 'embeddings', 'chat', 'images'])}",
    "endpoint": f"/v1/{random.choice(['completions', 'embeddings', 'chat', 'images'])}",
    "status_code": random.choice([200, 200, 200, 400, 500]),
    "status_code": random.choice([200, 200, 200, 400, 500]),
    "latency_ms": random.randint(50, 2000),
    "latency_ms": random.randint(50, 2000),
    }
    }


    # Track usage
    # Track usage
    tracker.track_usage(
    tracker.track_usage(
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
    timestamp=timestamp,
    timestamp=timestamp,
    metadata=metadata,
    metadata=metadata,
    check_quota=False,  # Don't check quota for historical data
    check_quota=False,  # Don't check quota for historical data
    )
    )




    def run_demo():
    def run_demo():
    """Run the usage tracking demo."""
    print("Usage Tracking Demo")
    print_separator()

    # Create a usage tracker
    tracker = UsageTracker(storage_dir="usage_data")

    # Create a customer
    customer_id = "cust_demo_123"

    print(f"Setting up usage limits and quotas for customer: {customer_id}")

    # Add usage limits
    limits = [
    UsageLimit(
    customer_id=customer_id,
    metric=UsageMetric.API_CALL,
    max_quantity=1000,
    period=UsageLimit.PERIOD_MONTHLY,
    category=UsageCategory.INFERENCE,
    resource_type="model",
    metadata={"tier": "basic"},
    ),
    UsageLimit(
    customer_id=customer_id,
    metric=UsageMetric.TOKEN,
    max_quantity=100000,
    period=UsageLimit.PERIOD_MONTHLY,
    category=UsageCategory.INFERENCE,
    resource_type="model",
    metadata={"tier": "basic"},
    ),
    UsageLimit(
    customer_id=customer_id,
    metric=UsageMetric.STORAGE,
    max_quantity=10.0,  # GB
    period=UsageLimit.PERIOD_MONTHLY,
    category=UsageCategory.STORAGE,
    resource_type="storage",
    metadata={"tier": "basic"},
    ),
    ]

    for limit in limits:
    tracker.add_limit(limit)
    print(f"Added limit: {limit}")

    print_separator()

    # Get customer limits
    customer_limits = tracker.get_customer_limits(customer_id)

    print(f"Customer limits ({len(customer_limits)}):")
    for limit in customer_limits:
    print(f"- {limit}")

    print_separator()

    # Get customer quotas
    customer_quotas = tracker.get_customer_quotas(customer_id)

    print(f"Customer quotas ({len(customer_quotas)}):")
    for quota in customer_quotas:
    print(f"- {quota}")

    print_separator()

    # Generate random usage data
    print("Generating random usage data...")
    generate_random_usage(tracker, customer_id, num_records=100, days_back=30)
    print("Generated 100 random usage records")

    print_separator()

    # Get usage summary
    summary = tracker.get_usage_summary(customer_id=customer_id)

    print("Usage summary:")
    print(f"Total records: {summary['total_records']}")
    print(f"Total quantity: {summary['total_quantity']}")

    print("\nUsage by metric:")
    for metric, data in summary["metrics"].items():
    print(f"- {metric}: {data['count']} records, {data['quantity']} units")

    print("\nUsage by category:")
    for category, data in summary["categories"].items():
    print(f"- {category}: {data['count']} records, {data['quantity']} units")

    print_separator()

    # Get usage by time
    usage_by_day = tracker.get_usage_by_time(customer_id=customer_id, interval="day")

    print("Usage by day:")
    print(f"Total records: {usage_by_day['total_records']}")
    print(f"Total quantity: {usage_by_day['total_quantity']}")

    print("\nDaily usage:")
    for interval, data in sorted(usage_by_day["intervals"].items()):
    print(f"- {interval}: {data['count']} records, {data['quantity']} units")

    print_separator()

    # Get usage trends
    trends = tracker.get_usage_trends(
    customer_id=customer_id, interval="day", num_intervals=7
    )

    print("Usage trends (last 7 days):")
    print(f"Trend direction: {trends['trend']['direction']}")
    print(f"Percentage change: {trends['trend']['percentage_change']:.2f}%")

    print("\nDaily trends:")
    for interval_data in trends["intervals"]:
    print(
    f"- {interval_data['interval']}: {interval_data['count']} records, {interval_data['quantity']} units"
    )

    print_separator()

    # Track some real-time usage
    print("Tracking real-time usage...")

    for i in range(5):
    # Check if usage is allowed
    allowed, reason, quota = tracker.check_usage_allowed(
    customer_id=customer_id,
    metric=UsageMetric.API_CALL,
    quantity=10,
    category=UsageCategory.INFERENCE,
    resource_type="model",
    )

    if allowed:
    # Track usage
    record, updated_quota, exceeded = tracker.track_usage(
    customer_id=customer_id,
    metric=UsageMetric.API_CALL,
    quantity=10,
    category=UsageCategory.INFERENCE,
    resource_id="model_gpt4",
    resource_type="model",
    metadata={"endpoint": "/v1/completions"},
    )

    print(f"Tracked usage: {record}")

    if updated_quota:
    print(
    f"Updated quota: {updated_quota.used_quantity}/{updated_quota.allocated_quantity} ({updated_quota.get_usage_percentage():.2f}%)"
    )

    if exceeded:
    print("Warning: Quota exceeded!")
    else:
    print(f"Usage not allowed: {reason}")
    break

    print_separator()

    # Get quota status
    status = tracker.get_quota_status(customer_id=customer_id)

    print("Quota status:")
    print(f"Total quotas: {status['total_quotas']}")
    print(f"Exceeded: {status['summary']['exceeded']}")
    print(f"Near limit: {status['summary']['near_limit']}")
    print(f"Healthy: {status['summary']['healthy']}")

    for quota_status in status["quotas"]:
    print(
    f"- {quota_status['metric']}: {quota_status['used_quantity']}/{quota_status['allocated_quantity']} ({quota_status['usage_percentage']:.2f}%)"
    )

    print_separator()

    print("Demo completed successfully!")


    if __name__ == "__main__":
    run_demo()