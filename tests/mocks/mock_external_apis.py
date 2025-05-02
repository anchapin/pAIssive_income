"""
Mock implementations of external APIs for testing.

This module provides mock implementations of various external APIs
that can be used for consistent testing without external dependencies.
"""

import json
import logging
import random
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class MockExternalAPIBase:
    """Base class for mock external APIs."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the mock API.

        Args:
            config: Optional configuration for the mock API
        """
        self.config = config or {}
        self.call_history = []
        self.error_rate = self.config.get("error_rate", 0.05)
        self.latency_range = self.config.get("latency_range", (50, 200))  # ms
        self.error_messages = self.config.get(
            "error_messages",
            {
                "server_error": "Internal server error",
                "not_found": "Resource not found",
                "auth_error": "Authentication failed",
                "rate_limit": "Rate limit exceeded",
            },
        )

    def record_call(self, method_name: str, **kwargs):
        """Record a method call for testing assertions."""
        self.call_history.append(
            {
                "method": method_name,
                "timestamp": datetime.now().isoformat(),
                "args": kwargs,
            }
        )

    def get_call_history(self, method_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get the call history, optionally filtered by method name."""
        if method_name:
            return [call for call in self.call_history if call["method"] == method_name]
        return self.call_history

    def clear_call_history(self):
        """Clear the call history."""
        self.call_history = []


class MockHuggingFaceAPI(MockExternalAPIBase):
    """Mock implementation of the Hugging Face API."""

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

    def list_models(self, filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List available models with optional filtering.

        Args:
            filter_criteria: Optional criteria to filter models

        Returns:
            List of matching models
        """
        self.record_call("list_models", filter_criteria=filter_criteria)

        if not filter_criteria:
            return self.available_models

        filtered_models = []
        for model in self.available_models:
            match = True
            for key, value in filter_criteria.items():
                if key == "pipeline_tag" and value != model.get(key):
                    match = False
                    break
                if key == "tags" and not all(tag in model.get("tags", []) for tag in value):
                    match = False
                    break
            if match:
                filtered_models.append(model)

        return filtered_models

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific model.

        Args:
            model_id: ID of the model to get info for

        Returns:
            Model information or None if not found
        """
        self.record_call("get_model_info", model_id=model_id)

        for model in self.available_models:
            if model["id"] == model_id:
                return model

        return None

    def download_model(self, model_id: str, local_path: str) -> bool:
        """
        Mock downloading a model.

        Args:
            model_id: ID of the model to download
            local_path: Path to save the model

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If the model doesn't exist
        """
        self.record_call("download_model", model_id=model_id, local_path=local_path)

        # Check if model exists
        if not any(m["id"] == model_id for m in self.available_models):
            raise ValueError(f"Model {model_id} not found")

        # Simulate random failures
        if random.random() < self.error_rate:
            raise IOError(self.error_messages["server_error"])

        # Simulate successful download
        return True


class MockPaymentAPI:
    """Mock implementation of payment processing API."""

    def __init__(self):
        """Initialize mock payment API."""
        self._customers = {}
        self._subscriptions = {}
        self._payments = {}

    def create_customer(
        self,
        email: str,
        name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a mock customer.

        Args:
            email: Customer email address
            name: Customer name
            kwargs: Additional customer attributes

        Returns:
            Dict containing customer data
        """
        customer_id = f"cust_{str(uuid.uuid4())}"
        customer = {
            "id": customer_id,
            "email": email,
            "name": name,
            "created_at": datetime.utcnow().isoformat(),
            **kwargs
        }
        self._customers[customer_id] = customer
        return customer

    def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a mock subscription.

        Args:
            customer_id: ID of the customer
            plan_id: ID of the subscription plan
            kwargs: Additional subscription attributes

        Returns:
            Dict containing subscription data
        """
        if customer_id not in self._customers:
            raise ValueError("Customer not found")

        subscription_id = f"sub_{str(uuid.uuid4())}"
        subscription = {
            "id": subscription_id,
            "customer_id": customer_id,
            "plan_id": plan_id,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "current_period_end": None,  # Set based on plan
            **kwargs
        }
        self._subscriptions[subscription_id] = subscription
        return subscription

    def process_payment(
        self,
        amount: int,
        currency: str,
        payment_method: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process a mock payment.

        Args:
            amount: Payment amount in smallest currency unit (e.g., cents)
            currency: Currency code (e.g., 'usd')
            payment_method: Payment method type
            kwargs: Additional payment attributes

        Returns:
            Dict containing payment data
        """
        payment_id = f"pay_{str(uuid.uuid4())}"
        payment = {
            "id": payment_id,
            "amount": amount,
            "currency": currency,
            "payment_method": payment_method,
            "status": "succeeded",
            "created_at": datetime.utcnow().isoformat(),
            **kwargs
        }
        self._payments[payment_id] = payment
        return payment

    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer by ID."""
        return self._customers.get(customer_id)

    def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription by ID."""
        return self._subscriptions.get(subscription_id)

    def get_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Get payment by ID."""
        return self._payments.get(payment_id)


class MockEmailAPI:
    """Mock implementation of email service API."""

    def __init__(self):
        """Initialize mock email API."""
        self._sent_emails = []
        self._templates = {
            "welcome_email": {
                "subject": "Welcome to {service_name}!",
                "content": "Hello {name}, welcome to our service!"
            }
        }

    def send_email(
        self,
        to: str,
        subject: str,
        content: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a mock email.

        Args:
            to: Recipient email address
            subject: Email subject
            content: Email content
            kwargs: Additional email attributes

        Returns:
            Dict containing send status
        """
        email = {
            "id": f"email_{str(uuid.uuid4())}",
            "to": to,
            "subject": subject,
            "content": content,
            "sent_at": datetime.utcnow().isoformat(),
            **kwargs
        }
        self._sent_emails.append(email)
        return {"status": "sent", "email_id": email["id"]}

    def send_template(
        self,
        template_id: str,
        to: str,
        variables: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a mock templated email.

        Args:
            template_id: ID of the email template
            to: Recipient email address
            variables: Template variables
            kwargs: Additional email attributes

        Returns:
            Dict containing send status
        """
        if template_id not in self._templates:
            raise ValueError("Template not found")

        template = self._templates[template_id]
        subject = template["subject"].format(**variables)
        content = template["content"].format(**variables)

        return self.send_email(to=to, subject=subject, content=content, **kwargs)

    def send_batch(
        self,
        emails: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Send multiple mock emails.

        Args:
            emails: List of email data dictionaries

        Returns:
            Dict containing batch send status
        """
        sent_count = 0
        failed_count = 0
        results = []

        for email in emails:
            try:
                result = self.send_email(**email)
                results.append(result)
                sent_count += 1
            except Exception:
                failed_count += 1

        return {
            "status": "completed",
            "sent_count": sent_count,
            "failed_count": failed_count,
            "results": results
        }

    def get_sent_emails(self) -> List[Dict[str, Any]]:
        """Get all sent emails."""
        return self._sent_emails


class MockStorageAPI:
    """Mock implementation of cloud storage API."""

    def __init__(self):
        """Initialize mock storage API."""
        self._files = {}
        self._base_url = "https://mock-storage.example.com"

    def upload_file(
        self,
        file_path: str,
        content: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Upload a mock file.

        Args:
            file_path: Path/name of the file
            content: File content
            kwargs: Additional file attributes

        Returns:
            Dict containing file data
        """
        file_id = f"file_{str(uuid.uuid4())}"
        file_data = {
            "id": file_id,
            "path": file_path,
            "content": content,
            "size": len(content),
            "url": f"{self._base_url}/{file_id}",
            "uploaded_at": datetime.utcnow().isoformat(),
            **kwargs
        }
        self._files[file_id] = file_data
        return {
            "id": file_id,
            "url": file_data["url"]
        }

    def download_file(self, file_id: str) -> Dict[str, Any]:
        """
        Download a mock file.

        Args:
            file_id: ID of the file to download

        Returns:
            Dict containing file data

        Raises:
            ValueError: If file not found
        """
        if file_id not in self._files:
            raise ValueError("File not found")

        file_data = self._files[file_id]
        return {
            "content": file_data["content"],
            "metadata": {
                "path": file_data["path"],
                "size": file_data["size"],
                "uploaded_at": file_data["uploaded_at"]
            }
        }

    def delete_file(self, file_id: str) -> Dict[str, str]:
        """
        Delete a mock file.

        Args:
            file_id: ID of the file to delete

        Returns:
            Dict containing deletion status

        Raises:
            ValueError: If file not found
        """
        if file_id not in self._files:
            raise ValueError("File not found")

        del self._files[file_id]
        return {"status": "deleted"}

    def list_files(self) -> List[Dict[str, Any]]:
        """
        List all mock files.

        Returns:
            List of file metadata
        """
        return [
            {
                "id": file_id,
                "path": data["path"],
                "size": data["size"],
                "url": data["url"],
                "uploaded_at": data["uploaded_at"]
            }
            for file_id, data in self._files.items()
        ]


# Helper function to create a mock API instance
def create_mock_api(api_type: str, config: Optional[Dict[str, Any]] = None):
    """
    Create a mock API of the specified type.

    Args:
        api_type: Type of API ("huggingface", "payment", "email", "storage")
        config: Optional configuration for the mock API

    Returns:
        A mock API instance
    """
    api_classes = {
        "huggingface": MockHuggingFaceAPI,
        "payment": MockPaymentAPI,
        "email": MockEmailAPI,
        "storage": MockStorageAPI,
    }

    api_class = api_classes.get(api_type.lower())
    if not api_class:
        raise ValueError(f"Unknown API type: {api_type}")

    return api_class(config)


def create_mock_api(api_type: str, config: dict = None) -> Any:
    """
    Create a mock API instance with optional configuration.

    Args:
        api_type: Type of API to create ('huggingface', 'payment', 'email', 'storage')
        config: Optional configuration dictionary for the API

    Returns:
        An instance of the requested mock API

    Raises:
        ValueError: If api_type is not recognized
    """
    config = config or {}
    
    if api_type == "huggingface":
        return MockHuggingFaceAPI(**config)
    elif api_type == "payment":
        return MockPaymentAPI(**config)
    elif api_type == "email":
        return MockEmailAPI(**config)
    elif api_type == "storage":
        return MockStorageAPI(**config)
    else:
        raise ValueError(f"Unknown API type: {api_type}")
