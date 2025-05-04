"""Tests for mock external API implementations."""

import pytest

from .mock_external_apis import (
    MockEmailAPI,
    MockHuggingFaceAPI,
    MockPaymentAPI,
    MockStorageAPI,
    create_mock_api,
)

def test_huggingface_api():
    """Test HuggingFace API mock implementation."""
    api = MockHuggingFaceAPI()

    # Test listing models
    models = api.list_models()
    assert len(models) > 0
    assert all(isinstance(m, dict) for m in models)

    # Test filtering models
    filtered = api.list_models({"pipeline_tag": "text - generation"})
    assert all(m["pipeline_tag"] == "text - generation" for m in filtered)

    # Test getting model info
    model_info = api.get_model_info("gpt2")
    assert model_info is not None
    assert model_info["id"] == "gpt2"

    # Test downloading model
    success = api.download_model("gpt2", " / tmp / models")
    assert success is True

    # Test invalid model
    with pytest.raises(ValueError):
        api.download_model("nonexistent - model", " / tmp / models")

def test_payment_api():
    """Test payment API mock implementation."""
    api = MockPaymentAPI()

    # Test customer creation
    customer = api.create_customer(email="test @ example.com", name="Test User")
    assert customer["email"] == "test @ example.com"
    assert customer["name"] == "Test User"
    assert "id" in customer

    # Test subscription creation
    subscription = api.create_subscription(customer_id=customer["id"], 
        plan_id="basic_plan")
    assert subscription["customer_id"] == customer["id"]
    assert subscription["plan_id"] == "basic_plan"
    assert subscription["status"] == "active"

    # Test payment processing
    payment = api.process_payment(amount=1000, currency="usd", payment_method="card")
    assert payment["amount"] == 1000
    assert payment["currency"] == "usd"
    assert payment["status"] == "succeeded"

    # Test retrieving data
    assert api.get_customer(customer["id"]) == customer
    assert api.get_subscription(subscription["id"]) == subscription
    assert api.get_payment(payment["id"]) == payment

def test_email_api():
    """Test email API mock implementation."""
    api = MockEmailAPI()

    # Test sending single email
    result = api.send_email(to="user @ example.com", subject="Test Email", 
        content="Test content")
    assert result["status"] == "sent"
    assert "email_id" in result

    # Test template email
    result = api.send_template(
        template_id="welcome_email",
        to="user @ example.com",
        variables={"service_name": "Test Service", "name": "Test User"},
    )
    assert result["status"] == "sent"

    # Test batch sending
    batch_result = api.send_batch(
        [
            {"to": f"user{i}@example.com", "subject": f"Test {i}", 
                "content": f"Content {i}"}
            for i in range(3)
        ]
    )
    assert batch_result["sent_count"] == 3
    assert batch_result["failed_count"] == 0

    # Test sent emails tracking
    sent_emails = api.get_sent_emails()
    assert len(sent_emails) == 4  # 1 single + 1 template + 3 batch
    assert all("sent_at" in email for email in sent_emails)

def test_storage_api():
    """Test storage API mock implementation."""
    api = MockStorageAPI()

    # Test file upload
    result = api.upload_file(file_path="test.txt", content="Hello, World!")
    assert "id" in result
    assert "url" in result
    file_id = result["id"]

    # Test file download
    download = api.download_file(file_id)
    assert download["content"] == "Hello, World!"
    assert "metadata" in download
    assert download["metadata"]["path"] == "test.txt"

    # Test listing files
    files = api.list_files()
    assert len(files) == 1
    assert files[0]["id"] == file_id
    assert files[0]["path"] == "test.txt"

    # Test file deletion
    delete_result = api.delete_file(file_id)
    assert delete_result["status"] == "deleted"
    assert len(api.list_files()) == 0

    # Test nonexistent file
    with pytest.raises(ValueError):
        api.download_file("nonexistent")
    with pytest.raises(ValueError):
        api.delete_file("nonexistent")

def test_create_mock_api():
    """Test mock API factory function."""
    apis = ["huggingface", "payment", "email", "storage"]

    for api_type in apis:
        api = create_mock_api(api_type)
        assert api is not None

    with pytest.raises(ValueError):
        create_mock_api("nonexistent")
