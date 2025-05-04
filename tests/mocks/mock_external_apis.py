"""
"""
Mock implementations of external APIs for testing.
Mock implementations of external APIs for testing.


This module provides mock implementations of various external APIs
This module provides mock implementations of various external APIs
that can be used for consistent testing without external dependencies.
that can be used for consistent testing without external dependencies.
"""
"""


import json
import json
import logging
import logging
import random
import random
import time
import time
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from typing import Any, Dict, List, Optional, Union


import boto3
import boto3


logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class MockExternalAPIBase:
    class MockExternalAPIBase:
    """Base class for mock external APIs."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
    """
    """
    Initialize the mock API.
    Initialize the mock API.


    Args:
    Args:
    config: Optional configuration for the mock API
    config: Optional configuration for the mock API
    """
    """
    self.config = config or {}
    self.config = config or {}
    self.call_history = []
    self.call_history = []
    self.error_rate = self.config.get("error_rate", 0.05)
    self.error_rate = self.config.get("error_rate", 0.05)
    self.latency_range = self.config.get("latency_range", (50, 200))  # ms
    self.latency_range = self.config.get("latency_range", (50, 200))  # ms
    self.error_messages = self.config.get(
    self.error_messages = self.config.get(
    "error_messages",
    "error_messages",
    {
    {
    "server_error": "Internal server error",
    "server_error": "Internal server error",
    "not_found": "Resource not found",
    "not_found": "Resource not found",
    "auth_error": "Authentication failed",
    "auth_error": "Authentication failed",
    "rate_limit": "Rate limit exceeded",
    "rate_limit": "Rate limit exceeded",
    },
    },
    )
    )


    def record_call(self, method_name: str, **kwargs):
    def record_call(self, method_name: str, **kwargs):
    """Record a method call for testing assertions."""
    self.call_history.append(
    {
    "method": method_name,
    "timestamp": datetime.now().isoformat(),
    "args": kwargs,
    }
    )

    def get_call_history(
    self, method_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
    """Get the call history, optionally filtered by method name."""
    if method_name:
    return [call for call in self.call_history if call["method"] == method_name]
    return self.call_history

    def clear_call_history(self):
    """Clear the call history."""
    self.call_history = []


    class MockHuggingFaceAPI(MockExternalAPIBase):

    def __init__(self, config: Optional[Dict[str, Any]] = None):
    """Initialize the mock Hugging Face API."""
    super().__init__(config)
    self.available_models = self.config.get(
    "available_models",
    [
    {
    "id": "gpt2",
    "name": "GPT-2",
    "downloads": 500000,
    "likes": 2500,
    "tags": ["text-generation", "transformer"],
    "pipeline_tag": "text-generation",
    },
    {
    "id": "bert-base-uncased",
    "name": "BERT Base Uncased",
    "downloads": 1000000,
    "likes": 5000,
    "tags": ["text-classification", "transformer"],
    "pipeline_tag": "text-classification",
    },
    {
    "id": "distilbert-base-uncased",
    "name": "DistilBERT Base Uncased",
    "downloads": 750000,
    "likes": 3000,
    "tags": ["text-classification", "transformer"],
    "pipeline_tag": "text-classification",
    },
    {
    "id": "all-MiniLM-L6-v2",
    "name": "All-MiniLM-L6-v2",
    "downloads": 250000,
    "likes": 1000,
    "tags": ["sentence-similarity", "embedding"],
    "pipeline_tag": "feature-extraction",
    },
    ],
    )

    def list_models(
    self, filter_criteria: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
    """
    """
    List available models with optional filtering.
    List available models with optional filtering.


    Args:
    Args:
    filter_criteria: Optional criteria to filter models
    filter_criteria: Optional criteria to filter models


    Returns:
    Returns:
    List of matching models
    List of matching models
    """
    """
    self.record_call("list_models", filter_criteria=filter_criteria)
    self.record_call("list_models", filter_criteria=filter_criteria)


    if not filter_criteria:
    if not filter_criteria:
    return self.available_models
    return self.available_models


    filtered_models = []
    filtered_models = []
    for model in self.available_models:
    for model in self.available_models:
    match = True
    match = True
    for key, value in filter_criteria.items():
    for key, value in filter_criteria.items():
    if key == "pipeline_tag" and value != model.get(key):
    if key == "pipeline_tag" and value != model.get(key):
    match = False
    match = False
    break
    break
    if key == "tags" and not all(
    if key == "tags" and not all(
    tag in model.get("tags", []) for tag in value
    tag in model.get("tags", []) for tag in value
    ):
    ):
    match = False
    match = False
    break
    break
    if match:
    if match:
    filtered_models.append(model)
    filtered_models.append(model)


    return filtered_models
    return filtered_models


    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
    """
    """
    Get information about a specific model.
    Get information about a specific model.


    Args:
    Args:
    model_id: ID of the model to get info for
    model_id: ID of the model to get info for


    Returns:
    Returns:
    Model information or None if not found
    Model information or None if not found
    """
    """
    self.record_call("get_model_info", model_id=model_id)
    self.record_call("get_model_info", model_id=model_id)


    for model in self.available_models:
    for model in self.available_models:
    if model["id"] == model_id:
    if model["id"] == model_id:
    return model
    return model


    return None
    return None


    def download_model(self, model_id: str, local_path: str) -> bool:
    def download_model(self, model_id: str, local_path: str) -> bool:
    """
    """
    Mock downloading a model.
    Mock downloading a model.


    Args:
    Args:
    model_id: ID of the model to download
    model_id: ID of the model to download
    local_path: Path to save the model
    local_path: Path to save the model


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise


    Raises:
    Raises:
    ValueError: If the model doesn't exist
    ValueError: If the model doesn't exist
    """
    """
    self.record_call("download_model", model_id=model_id, local_path=local_path)
    self.record_call("download_model", model_id=model_id, local_path=local_path)


    # Check if model exists
    # Check if model exists
    if not any(m["id"] == model_id for m in self.available_models):
    if not any(m["id"] == model_id for m in self.available_models):
    raise ValueError(f"Model {model_id} not found")
    raise ValueError(f"Model {model_id} not found")


    # Simulate random failures
    # Simulate random failures
    if random.random() < self.error_rate:
    if random.random() < self.error_rate:
    raise IOError(self.error_messages["server_error"])
    raise IOError(self.error_messages["server_error"])


    # Simulate successful download
    # Simulate successful download
    return True
    return True




    class MockPaymentAPI(MockExternalAPIBase):
    class MockPaymentAPI(MockExternalAPIBase):
    """Mock implementation of a payment processing API (like Stripe)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
    """Initialize the mock Payment API."""
    super().__init__(config)
    self.customers = {}
    self.charges = {}
    self.subscriptions = {}
    self.plans = self.config.get(
    "plans",
    [
    {
    "id": "basic-monthly",
    "name": "Basic Monthly",
    "amount": 999,  # cents
    "currency": "usd",
    "interval": "month",
    },
    {
    "id": "basic-annual",
    "name": "Basic Annual",
    "amount": 9990,  # cents
    "currency": "usd",
    "interval": "year",
    },
    {
    "id": "premium-monthly",
    "name": "Premium Monthly",
    "amount": 1999,  # cents
    "currency": "usd",
    "interval": "month",
    },
    {
    "id": "premium-annual",
    "name": "Premium Annual",
    "amount": 19990,  # cents
    "currency": "usd",
    "interval": "year",
    },
    ],
    )

    def create_customer(
    self,
    email: str,
    name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    """
    """
    Create a new customer.
    Create a new customer.


    Args:
    Args:
    email: Customer email
    email: Customer email
    name: Customer name
    name: Customer name
    metadata: Additional metadata
    metadata: Additional metadata


    Returns:
    Returns:
    Customer object
    Customer object
    """
    """
    self.record_call("create_customer", email=email, name=name, metadata=metadata)
    self.record_call("create_customer", email=email, name=name, metadata=metadata)


    customer_id = (
    customer_id = (
    f"cus_{random.randint(10000, 99999)}_{int(datetime.now().timestamp())}"
    f"cus_{random.randint(10000, 99999)}_{int(datetime.now().timestamp())}"
    )
    )
    customer = {
    customer = {
    "id": customer_id,
    "id": customer_id,
    "email": email,
    "email": email,
    "name": name,
    "name": name,
    "created": int(datetime.now().timestamp()),
    "created": int(datetime.now().timestamp()),
    "metadata": metadata or {},
    "metadata": metadata or {},
    "subscriptions": [],
    "subscriptions": [],
    }
    }


    self.customers[customer_id] = customer
    self.customers[customer_id] = customer
    return customer
    return customer


    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
    """
    """
    Get a customer by ID.
    Get a customer by ID.


    Args:
    Args:
    customer_id: The customer ID
    customer_id: The customer ID


    Returns:
    Returns:
    Customer object or None if not found
    Customer object or None if not found
    """
    """
    self.record_call("get_customer", customer_id=customer_id)
    self.record_call("get_customer", customer_id=customer_id)
    return self.customers.get(customer_id)
    return self.customers.get(customer_id)


    def create_subscription(
    def create_subscription(
    self, customer_id: str, plan_id: str, trial_period_days: Optional[int] = None
    self, customer_id: str, plan_id: str, trial_period_days: Optional[int] = None
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create a subscription for a customer.
    Create a subscription for a customer.


    Args:
    Args:
    customer_id: Customer ID
    customer_id: Customer ID
    plan_id: Plan ID
    plan_id: Plan ID
    trial_period_days: Optional trial period in days
    trial_period_days: Optional trial period in days


    Returns:
    Returns:
    Subscription object
    Subscription object


    Raises:
    Raises:
    ValueError: If customer or plan doesn't exist
    ValueError: If customer or plan doesn't exist
    """
    """
    self.record_call(
    self.record_call(
    "create_subscription",
    "create_subscription",
    customer_id=customer_id,
    customer_id=customer_id,
    plan_id=plan_id,
    plan_id=plan_id,
    trial_period_days=trial_period_days,
    trial_period_days=trial_period_days,
    )
    )


    # Check if customer exists
    # Check if customer exists
    if customer_id not in self.customers:
    if customer_id not in self.customers:
    raise ValueError(f"Customer {customer_id} not found")
    raise ValueError(f"Customer {customer_id} not found")


    # Check if plan exists
    # Check if plan exists
    plan = next((p for p in self.plans if p["id"] == plan_id), None)
    plan = next((p for p in self.plans if p["id"] == plan_id), None)
    if not plan:
    if not plan:
    raise ValueError(f"Plan {plan_id} not found")
    raise ValueError(f"Plan {plan_id} not found")


    # Create subscription
    # Create subscription
    now = datetime.now()
    now = datetime.now()
    trial_end = (
    trial_end = (
    now + timedelta(days=trial_period_days) if trial_period_days else None
    now + timedelta(days=trial_period_days) if trial_period_days else None
    )
    )


    if plan["interval"] == "month":
    if plan["interval"] == "month":
    period_end = now + timedelta(days=30)
    period_end = now + timedelta(days=30)
    else:  # year
    else:  # year
    period_end = now + timedelta(days=365)
    period_end = now + timedelta(days=365)


    subscription_id = f"sub_{random.randint(10000, 99999)}_{int(now.timestamp())}"
    subscription_id = f"sub_{random.randint(10000, 99999)}_{int(now.timestamp())}"
    subscription = {
    subscription = {
    "id": subscription_id,
    "id": subscription_id,
    "customer": customer_id,
    "customer": customer_id,
    "plan": plan,
    "plan": plan,
    "status": "trialing" if trial_period_days else "active",
    "status": "trialing" if trial_period_days else "active",
    "current_period_start": int(now.timestamp()),
    "current_period_start": int(now.timestamp()),
    "current_period_end": int(period_end.timestamp()),
    "current_period_end": int(period_end.timestamp()),
    "created": int(now.timestamp()),
    "created": int(now.timestamp()),
    "trial_start": int(now.timestamp()) if trial_period_days else None,
    "trial_start": int(now.timestamp()) if trial_period_days else None,
    "trial_end": int(trial_end.timestamp()) if trial_end else None,
    "trial_end": int(trial_end.timestamp()) if trial_end else None,
    }
    }


    self.subscriptions[subscription_id] = subscription
    self.subscriptions[subscription_id] = subscription
    self.customers[customer_id]["subscriptions"].append(subscription_id)
    self.customers[customer_id]["subscriptions"].append(subscription_id)


    return subscription
    return subscription


    def update_subscription(
    def update_subscription(
    self,
    self,
    subscription_id: str,
    subscription_id: str,
    plan_id: Optional[str] = None,
    plan_id: Optional[str] = None,
    cancel_at_period_end: Optional[bool] = None,
    cancel_at_period_end: Optional[bool] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Update a subscription.
    Update a subscription.


    Args:
    Args:
    subscription_id: Subscription ID
    subscription_id: Subscription ID
    plan_id: New plan ID
    plan_id: New plan ID
    cancel_at_period_end: Whether to cancel at period end
    cancel_at_period_end: Whether to cancel at period end


    Returns:
    Returns:
    Updated subscription object
    Updated subscription object


    Raises:
    Raises:
    ValueError: If subscription doesn't exist
    ValueError: If subscription doesn't exist
    """
    """
    self.record_call(
    self.record_call(
    "update_subscription",
    "update_subscription",
    subscription_id=subscription_id,
    subscription_id=subscription_id,
    plan_id=plan_id,
    plan_id=plan_id,
    cancel_at_period_end=cancel_at_period_end,
    cancel_at_period_end=cancel_at_period_end,
    )
    )


    # Check if subscription exists
    # Check if subscription exists
    if subscription_id not in self.subscriptions:
    if subscription_id not in self.subscriptions:
    raise ValueError(f"Subscription {subscription_id} not found")
    raise ValueError(f"Subscription {subscription_id} not found")


    subscription = self.subscriptions[subscription_id]
    subscription = self.subscriptions[subscription_id]


    # Update plan if provided
    # Update plan if provided
    if plan_id:
    if plan_id:
    # Check if plan exists
    # Check if plan exists
    plan = next((p for p in self.plans if p["id"] == plan_id), None)
    plan = next((p for p in self.plans if p["id"] == plan_id), None)
    if not plan:
    if not plan:
    raise ValueError(f"Plan {plan_id} not found")
    raise ValueError(f"Plan {plan_id} not found")


    subscription["plan"] = plan
    subscription["plan"] = plan


    # Update cancellation settings
    # Update cancellation settings
    if cancel_at_period_end is not None:
    if cancel_at_period_end is not None:
    subscription["cancel_at_period_end"] = cancel_at_period_end
    subscription["cancel_at_period_end"] = cancel_at_period_end


    return subscription
    return subscription


    def cancel_subscription(
    def cancel_subscription(
    self, subscription_id: str, at_period_end: bool = False
    self, subscription_id: str, at_period_end: bool = False
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Cancel a subscription.
    Cancel a subscription.


    Args:
    Args:
    subscription_id: Subscription ID
    subscription_id: Subscription ID
    at_period_end: Whether to cancel at period end
    at_period_end: Whether to cancel at period end


    Returns:
    Returns:
    Updated subscription object
    Updated subscription object


    Raises:
    Raises:
    ValueError: If subscription doesn't exist
    ValueError: If subscription doesn't exist
    """
    """
    self.record_call(
    self.record_call(
    "cancel_subscription",
    "cancel_subscription",
    subscription_id=subscription_id,
    subscription_id=subscription_id,
    at_period_end=at_period_end,
    at_period_end=at_period_end,
    )
    )


    # Check if subscription exists
    # Check if subscription exists
    if subscription_id not in self.subscriptions:
    if subscription_id not in self.subscriptions:
    raise ValueError(f"Subscription {subscription_id} not found")
    raise ValueError(f"Subscription {subscription_id} not found")


    subscription = self.subscriptions[subscription_id]
    subscription = self.subscriptions[subscription_id]


    if at_period_end:
    if at_period_end:
    subscription["cancel_at_period_end"] = True
    subscription["cancel_at_period_end"] = True
    else:
    else:
    subscription["status"] = "canceled"
    subscription["status"] = "canceled"
    subscription["canceled_at"] = int(datetime.now().timestamp())
    subscription["canceled_at"] = int(datetime.now().timestamp())


    return subscription
    return subscription


    def create_charge(
    def create_charge(
    self,
    self,
    customer_id: str,
    customer_id: str,
    amount: int,
    amount: int,
    currency: str = "usd",
    currency: str = "usd",
    description: Optional[str] = None,
    description: Optional[str] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create a one-time charge.
    Create a one-time charge.


    Args:
    Args:
    customer_id: Customer ID
    customer_id: Customer ID
    amount: Amount in cents
    amount: Amount in cents
    currency: Currency code
    currency: Currency code
    description: Charge description
    description: Charge description


    Returns:
    Returns:
    Charge object
    Charge object


    Raises:
    Raises:
    ValueError: If customer doesn't exist
    ValueError: If customer doesn't exist
    """
    """
    self.record_call(
    self.record_call(
    "create_charge",
    "create_charge",
    customer_id=customer_id,
    customer_id=customer_id,
    amount=amount,
    amount=amount,
    currency=currency,
    currency=currency,
    description=description,
    description=description,
    )
    )


    # Check if customer exists
    # Check if customer exists
    if customer_id not in self.customers:
    if customer_id not in self.customers:
    raise ValueError(f"Customer {customer_id} not found")
    raise ValueError(f"Customer {customer_id} not found")


    # Create charge
    # Create charge
    charge_id = (
    charge_id = (
    f"ch_{random.randint(10000, 99999)}_{int(datetime.now().timestamp())}"
    f"ch_{random.randint(10000, 99999)}_{int(datetime.now().timestamp())}"
    )
    )
    charge = {
    charge = {
    "id": charge_id,
    "id": charge_id,
    "customer": customer_id,
    "customer": customer_id,
    "amount": amount,
    "amount": amount,
    "currency": currency,
    "currency": currency,
    "description": description,
    "description": description,
    "status": "succeeded",
    "status": "succeeded",
    "created": int(datetime.now().timestamp()),
    "created": int(datetime.now().timestamp()),
    }
    }


    self.charges[charge_id] = charge
    self.charges[charge_id] = charge
    return charge
    return charge




    class MockEmailAPI(MockExternalAPIBase):
    class MockEmailAPI(MockExternalAPIBase):
    """Mock implementation of an email sending API (like SendGrid)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
    """Initialize the mock Email API."""
    super().__init__(config)
    self.sent_emails = []
    self.templates = self.config.get(
    "templates",
    [
    {
    "id": "welcome",
    "name": "Welcome Email",
    "subject": "Welcome to Our Service",
    },
    {
    "id": "invoice",
    "name": "Invoice",
    "subject": "Your Invoice #{invoice_number}",
    },
    {
    "id": "password_reset",
    "name": "Password Reset",
    "subject": "Reset Your Password",
    },
    {
    "id": "verification",
    "name": "Account Verification",
    "subject": "Verify Your Account",
    },
    ],
    )

    def send_email(
    self,
    to_email: Union[str, List[str]],
    subject: str,
    content: str,
    from_email: Optional[str] = None,
    reply_to: Optional[str] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
    """
    """
    Send an email.
    Send an email.


    Args:
    Args:
    to_email: Recipient email(s)
    to_email: Recipient email(s)
    subject: Email subject
    subject: Email subject
    content: Email content
    content: Email content
    from_email: Sender email
    from_email: Sender email
    reply_to: Reply-to email
    reply_to: Reply-to email
    attachments: List of attachment objects
    attachments: List of attachment objects


    Returns:
    Returns:
    Response object
    Response object
    """
    """
    self.record_call(
    self.record_call(
    "send_email",
    "send_email",
    to_email=to_email,
    to_email=to_email,
    subject=subject,
    subject=subject,
    content=content,
    content=content,
    from_email=from_email,
    from_email=from_email,
    reply_to=reply_to,
    reply_to=reply_to,
    attachments=attachments,
    attachments=attachments,
    )
    )


    # Create email record
    # Create email record
    email = {
    email = {
    "id": f"email_{random.randint(10000, 99999)}_{int(datetime.now().timestamp())}",
    "id": f"email_{random.randint(10000, 99999)}_{int(datetime.now().timestamp())}",
    "to_email": to_email,
    "to_email": to_email,
    "subject": subject,
    "subject": subject,
    "content": content,
    "content": content,
    "from_email": from_email,
    "from_email": from_email,
    "reply_to": reply_to,
    "reply_to": reply_to,
    "attachments": attachments,
    "attachments": attachments,
    "sent_at": datetime.now().isoformat(),
    "sent_at": datetime.now().isoformat(),
    "status": "sent" if random.random() > self.error_rate else "failed",
    "status": "sent" if random.random() > self.error_rate else "failed",
    }
    }


    self.sent_emails.append(email)
    self.sent_emails.append(email)


    return {
    return {
    "id": email["id"],
    "id": email["id"],
    "status": email["status"],
    "status": email["status"],
    "message": (
    "message": (
    "Email sent successfully"
    "Email sent successfully"
    if email["status"] == "sent"
    if email["status"] == "sent"
    else "Failed to send email"
    else "Failed to send email"
    ),
    ),
    }
    }


    def send_template_email(
    def send_template_email(
    self,
    self,
    to_email: Union[str, List[str]],
    to_email: Union[str, List[str]],
    template_id: str,
    template_id: str,
    template_data: Dict[str, Any],
    template_data: Dict[str, Any],
    from_email: Optional[str] = None,
    from_email: Optional[str] = None,
    reply_to: Optional[str] = None,
    reply_to: Optional[str] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Send an email using a template.
    Send an email using a template.


    Args:
    Args:
    to_email: Recipient email(s)
    to_email: Recipient email(s)
    template_id: Template ID
    template_id: Template ID
    template_data: Data to substitute in the template
    template_data: Data to substitute in the template
    from_email: Sender email
    from_email: Sender email
    reply_to: Reply-to email
    reply_to: Reply-to email


    Returns:
    Returns:
    Response object
    Response object


    Raises:
    Raises:
    ValueError: If template doesn't exist
    ValueError: If template doesn't exist
    """
    """
    self.record_call(
    self.record_call(
    "send_template_email",
    "send_template_email",
    to_email=to_email,
    to_email=to_email,
    template_id=template_id,
    template_id=template_id,
    template_data=template_data,
    template_data=template_data,
    from_email=from_email,
    from_email=from_email,
    reply_to=reply_to,
    reply_to=reply_to,
    )
    )


    # Check if template exists
    # Check if template exists
    template = next((t for t in self.templates if t["id"] == template_id), None)
    template = next((t for t in self.templates if t["id"] == template_id), None)
    if not template:
    if not template:
    raise ValueError(f"Template {template_id} not found")
    raise ValueError(f"Template {template_id} not found")


    # Format subject if needed
    # Format subject if needed
    subject = template["subject"]
    subject = template["subject"]
    for key, value in template_data.items():
    for key, value in template_data.items():
    if isinstance(value, (str, int, float)):
    if isinstance(value, (str, int, float)):
    subject = subject.replace(f"{{{key}}}", str(value))
    subject = subject.replace(f"{{{key}}}", str(value))


    # Create mock content
    # Create mock content
    content = f"This is a mock email using the {template['name']} template with data: {json.dumps(template_data)}"
    content = f"This is a mock email using the {template['name']} template with data: {json.dumps(template_data)}"


    # Send the email
    # Send the email
    return self.send_email(
    return self.send_email(
    to_email=to_email,
    to_email=to_email,
    subject=subject,
    subject=subject,
    content=content,
    content=content,
    from_email=from_email,
    from_email=from_email,
    reply_to=reply_to,
    reply_to=reply_to,
    )
    )


    def get_sent_emails(self, to_email: Optional[str] = None) -> List[Dict[str, Any]]:
    def get_sent_emails(self, to_email: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    """
    Get all sent emails, optionally filtered by recipient.
    Get all sent emails, optionally filtered by recipient.


    Args:
    Args:
    to_email: Optional filter by recipient
    to_email: Optional filter by recipient


    Returns:
    Returns:
    List of matching emails
    List of matching emails
    """
    """
    self.record_call("get_sent_emails", to_email=to_email)
    self.record_call("get_sent_emails", to_email=to_email)


    if to_email:
    if to_email:
    return [
    return [
    email
    email
    for email in self.sent_emails
    for email in self.sent_emails
    if (
    if (
    email["to_email"] == to_email
    email["to_email"] == to_email
    or (
    or (
    isinstance(email["to_email"], list)
    isinstance(email["to_email"], list)
    and to_email in email["to_email"]
    and to_email in email["to_email"]
    )
    )
    )
    )
    ]
    ]


    return self.sent_emails
    return self.sent_emails




    class MockStorageAPI(MockExternalAPIBase):
    class MockStorageAPI(MockExternalAPIBase):
    """Mock implementation of a cloud storage API (like AWS S3)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
    """Initialize the mock Storage API."""
    super().__init__(config)
    self.buckets = {}
    self.default_bucket = "default-bucket"
    self.buckets[self.default_bucket] = {}

    def create_bucket(self, bucket_name: str) -> Dict[str, Any]:
    """
    """
    Create a new storage bucket.
    Create a new storage bucket.


    Args:
    Args:
    bucket_name: Name of the bucket
    bucket_name: Name of the bucket


    Returns:
    Returns:
    Bucket information
    Bucket information
    """
    """
    self.record_call("create_bucket", bucket_name=bucket_name)
    self.record_call("create_bucket", bucket_name=bucket_name)


    if (bucket_name in self.buckets):
    if (bucket_name in self.buckets):
    raise ValueError(f"Bucket {bucket_name} already exists")
    raise ValueError(f"Bucket {bucket_name} already exists")


    self.buckets[bucket_name] = {}
    self.buckets[bucket_name] = {}


    return {"name": bucket_name, "created_at": datetime.now().isoformat()}
    return {"name": bucket_name, "created_at": datetime.now().isoformat()}


    def list_buckets(self) -> List[Dict[str, Any]]:
    def list_buckets(self) -> List[Dict[str, Any]]:
    """
    """
    List all buckets.
    List all buckets.


    Returns:
    Returns:
    List of buckets
    List of buckets
    """
    """
    self.record_call("list_buckets")
    self.record_call("list_buckets")


    return [
    return [
    {"name": name, "objects_count": len(objects)}
    {"name": name, "objects_count": len(objects)}
    for name, objects in self.buckets.items()
    for name, objects in self.buckets.items()
    ]
    ]


    def upload_object(
    def upload_object(
    self, data: bytes, key: str, bucket_name: Optional[str] = None
    self, data: bytes, key: str, bucket_name: Optional[str] = None
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Upload an object to storage.
    Upload an object to storage.


    Args:
    Args:
    data: Object data as bytes
    data: Object data as bytes
    key: Object key/path
    key: Object key/path
    bucket_name: Optional bucket name (default: default-bucket)
    bucket_name: Optional bucket name (default: default-bucket)


    Returns:
    Returns:
    Object information
    Object information


    Raises:
    Raises:
    ValueError: If bucket doesn't exist
    ValueError: If bucket doesn't exist
    """
    """
    bucket = bucket_name or self.default_bucket
    bucket = bucket_name or self.default_bucket
    self.record_call("upload_object", key=key, bucket_name=bucket, size=len(data))
    self.record_call("upload_object", key=key, bucket_name=bucket, size=len(data))


    if bucket not in self.buckets:
    if bucket not in self.buckets:
    raise ValueError(f"Bucket {bucket} not found")
    raise ValueError(f"Bucket {bucket} not found")


    # Store object metadata (don't actually store the data to save memory)
    # Store object metadata (don't actually store the data to save memory)
    self.buckets[bucket][key] = {
    self.buckets[bucket][key] = {
    "size": len(data),
    "size": len(data),
    "last_modified": datetime.now().isoformat(),
    "last_modified": datetime.now().isoformat(),
    "etag": f"{random.randint(1000000000, 9999999999):x}",
    "etag": f"{random.randint(1000000000, 9999999999):x}",
    }
    }


    return {
    return {
    "bucket": bucket,
    "bucket": bucket,
    "key": key,
    "key": key,
    "etag": self.buckets[bucket][key]["etag"],
    "etag": self.buckets[bucket][key]["etag"],
    "size": len(data),
    "size": len(data),
    }
    }


    def download_object(
    def download_object(
    self, key: str, bucket_name: Optional[str] = None
    self, key: str, bucket_name: Optional[str] = None
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Download an object from storage.
    Download an object from storage.


    Args:
    Args:
    key: Object key/path
    key: Object key/path
    bucket_name: Optional bucket name (default: default-bucket)
    bucket_name: Optional bucket name (default: default-bucket)


    Returns:
    Returns:
    Object information with mock data
    Object information with mock data


    Raises:
    Raises:
    ValueError: If bucket or object doesn't exist
    ValueError: If bucket or object doesn't exist
    """
    """
    bucket = bucket_name or self.default_bucket
    bucket = bucket_name or self.default_bucket
    self.record_call("download_object", key=key, bucket_name=bucket)
    self.record_call("download_object", key=key, bucket_name=bucket)


    if bucket not in self.buckets:
    if bucket not in self.buckets:
    raise ValueError(f"Bucket {bucket} not found")
    raise ValueError(f"Bucket {bucket} not found")


    if key not in self.buckets[bucket]:
    if key not in self.buckets[bucket]:
    raise ValueError(f"Object {key} not found in bucket {bucket}")
    raise ValueError(f"Object {key} not found in bucket {bucket}")


    # Return mock data
    # Return mock data
    size = self.buckets[bucket][key]["size"]
    size = self.buckets[bucket][key]["size"]
    mock_data = bytes(
    mock_data = bytes(
    random.randint(0, 255) for _ in range(min(size, 1024))
    random.randint(0, 255) for _ in range(min(size, 1024))
    )  # limit to 1KB
    )  # limit to 1KB


    return {
    return {
    "bucket": bucket,
    "bucket": bucket,
    "key": key,
    "key": key,
    "data": mock_data,
    "data": mock_data,
    "size": size,
    "size": size,
    "last_modified": self.buckets[bucket][key]["last_modified"],
    "last_modified": self.buckets[bucket][key]["last_modified"],
    "etag": self.buckets[bucket][key]["etag"],
    "etag": self.buckets[bucket][key]["etag"],
    }
    }


    def list_objects(
    def list_objects(
    self, bucket_name: Optional[str] = None, prefix: Optional[str] = None
    self, bucket_name: Optional[str] = None, prefix: Optional[str] = None
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    List objects in a bucket.
    List objects in a bucket.


    Args:
    Args:
    bucket_name: Optional bucket name (default: default-bucket)
    bucket_name: Optional bucket name (default: default-bucket)
    prefix: Optional prefix to filter objects
    prefix: Optional prefix to filter objects


    Returns:
    Returns:
    List of objects
    List of objects


    Raises:
    Raises:
    ValueError: If bucket doesn't exist
    ValueError: If bucket doesn't exist
    """
    """
    bucket = bucket_name or self.default_bucket
    bucket = bucket_name or self.default_bucket
    self.record_call("list_objects", bucket_name=bucket, prefix=prefix)
    self.record_call("list_objects", bucket_name=bucket, prefix=prefix)


    if bucket not in self.buckets:
    if bucket not in self.buckets:
    raise ValueError(f"Bucket {bucket} not found")
    raise ValueError(f"Bucket {bucket} not found")


    objects = []
    objects = []
    for key, metadata in self.buckets[bucket].items():
    for key, metadata in self.buckets[bucket].items():
    if prefix is None or key.startswith(prefix):
    if prefix is None or key.startswith(prefix):
    obj = {
    obj = {
    "key": key,
    "key": key,
    "size": metadata["size"],
    "size": metadata["size"],
    "last_modified": metadata["last_modified"],
    "last_modified": metadata["last_modified"],
    "etag": metadata["etag"],
    "etag": metadata["etag"],
    }
    }
    objects.append(obj)
    objects.append(obj)


    return objects
    return objects


    def delete_object(self, key: str, bucket_name: Optional[str] = None) -> bool:
    def delete_object(self, key: str, bucket_name: Optional[str] = None) -> bool:
    """
    """
    Delete an object from storage.
    Delete an object from storage.


    Args:
    Args:
    key: Object key/path
    key: Object key/path
    bucket_name: Optional bucket name (default: default-bucket)
    bucket_name: Optional bucket name (default: default-bucket)


    Returns:
    Returns:
    True if deleted, False otherwise
    True if deleted, False otherwise


    Raises:
    Raises:
    ValueError: If bucket doesn't exist
    ValueError: If bucket doesn't exist
    """
    """
    bucket = bucket_name or self.default_bucket
    bucket = bucket_name or self.default_bucket
    self.record_call("delete_object", key=key, bucket_name=bucket)
    self.record_call("delete_object", key=key, bucket_name=bucket)


    if bucket not in self.buckets:
    if bucket not in self.buckets:
    raise ValueError(f"Bucket {bucket} not found")
    raise ValueError(f"Bucket {bucket} not found")


    if key in self.buckets[bucket]:
    if key in self.buckets[bucket]:
    del self.buckets[bucket][key]
    del self.buckets[bucket][key]
    return True
    return True


    return False
    return False




    # Helper function to create a mock API instance
    # Helper function to create a mock API instance
    def create_mock_api(api_type: str, config: Optional[Dict[str, Any]] = None):
    def create_mock_api(api_type: str, config: Optional[Dict[str, Any]] = None):
    """
    """
    Create a mock API of the specified type.
    Create a mock API of the specified type.


    Args:
    Args:
    api_type: Type of API ("huggingface", "payment", "email", "storage")
    api_type: Type of API ("huggingface", "payment", "email", "storage")
    config: Optional configuration for the mock API
    config: Optional configuration for the mock API


    Returns:
    Returns:
    A mock API instance
    A mock API instance
    """
    """
    api_classes = {
    api_classes = {
    "huggingface": MockHuggingFaceAPI,
    "huggingface": MockHuggingFaceAPI,
    "payment": MockPaymentAPI,
    "payment": MockPaymentAPI,
    "email": MockEmailAPI,
    "email": MockEmailAPI,
    "storage": MockStorageAPI,
    "storage": MockStorageAPI,
    }
    }


    api_class = api_classes.get(api_type.lower())
    api_class = api_classes.get(api_type.lower())
    if not api_class:
    if not api_class:
    raise ValueError(f"Unknown API type: {api_type}")
    raise ValueError(f"Unknown API type: {api_type}")


    return api_class(config)
    return api_class(config)