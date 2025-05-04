"""
Example tests demonstrating how to use the mock fixtures.

This module contains example tests that demonstrate how to use
the mock fixtures for external APIs in test scenarios.
"""

import json
import os

# Test using mock_http fixture
def test_openai_api_interaction(mock_http_with_common_responses):
    """
    Test interacting with the OpenAI API using the mock HTTP fixture.
    """
    # Use the pre - configured mock HTTP client
    http = mock_http_with_common_responses

    # Make a request to the OpenAI API
    response = http.post(
        "https://api.openai.com / v1 / chat / completions",
        json={
            "model": "gpt - 3.5 - turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
        },
    )

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["choices"][0]["message"]["content"] == \
        "This is a mock response from the AI."

    # We can also add new mock responses on the fly
    http.add_response(
        "https://api.openai.com / v1 / models",
        {
            "data": [
                {"id": "gpt - 4", "owned_by": "openai"},
                {"id": "gpt - 3.5 - turbo", "owned_by": "openai"},
            ]
        },
    )

    # And then use them
    response = http.get("https://api.openai.com / v1 / models")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2

    # We can also check the request history
    assert len(http.request_history) == 2
    assert http.request_history[0]["method"] == "POST"
    assert http.request_history[1]["method"] == "GET"

# Test using patch_requests fixture
def test_with_patched_requests(patch_requests):
    """
    Test using the patch_requests fixture to mock the requests library.
    """
    # The patch_requests fixture replaces the actual requests library with our mock,
    # which allows us to import and use requests as normal in the code being tested
    import requests

    # Set up a mock response
    patch_requests.add_response(
        "https://api.example.com / data", {"key": "value", "items": [1, 2, 3]}
    )

    # Use the requests library as usual
    response = requests.get("https://api.example.com / data")

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "value"
    assert data["items"] == [1, 2, 3]

# Test using mock_hf_hub fixture
def test_huggingface_hub_interaction(mock_hf_hub_with_models):
    """
    Test interacting with the Hugging Face Hub using the mock fixture.
    """
    # Use the pre - configured mock Hugging Face Hub
    hf_hub = mock_hf_hub_with_models

    # List available models
    models = hf_hub.list_models(search="gpt2")
    assert len(models) == 1
    assert models[0].id == "gpt2"

    # Download a file
    file_path = hf_hub.hf_hub_download(repo_id="gpt2", filename="config.json")

    # Verify the file was downloaded
    assert os.path.exists(file_path)

    # Check the file contents
    with open(file_path, "r") as f:
        config = json.loads(f.read())

    assert config["model_type"] == "gpt2"
    assert config["vocab_size"] == 50257

    # Add a new model
    hf_hub.add_repo({"id": "my - custom - model", "tags": ["text - generation"]})

    hf_hub.add_file(repo_id="my - custom - model", file_path="model.bin", 
        content=b"CUSTOM_MODEL_DATA")

    # Download the new model
    file_path = hf_hub.hf_hub_download(repo_id="my - custom - model", 
        filename="model.bin")

    # Verify the file exists
    assert os.path.exists(file_path)

    # Check the file contents
    with open(file_path, "rb") as f:
        model_data = f.read()

    assert model_data == b"CUSTOM_MODEL_DATA"

# Test using patch_huggingface_hub fixture
def test_with_patched_huggingface_hub(patch_huggingface_hub):
    """
    Test using the patch_huggingface_hub fixture to mock the huggingface_hub library.
    """
    # The patch_huggingface_hub fixture replaces the actual huggingface_hub library
    # with our mock, which allows us to import and use huggingface_hub as normal
    from huggingface_hub import hf_hub_download, list_models

    # Add a model to the mock hub
    patch_huggingface_hub.add_repo({"id": "bert - base - uncased", 
        "pipeline_tag": "fill - mask"})

    patch_huggingface_hub.add_file(
        repo_id="bert - base - uncased",
        file_path="config.json",
        content=json.dumps({"model_type": "bert"}),
    )

    # List models
    models = list_models(search="bert - base - uncased")
    assert len(models) == 1
    assert models[0].id == "bert - base - uncased"

    # Download a file
    file_path = hf_hub_download(repo_id="bert - base - uncased", filename="config.json")

    # Verify the file exists
    assert os.path.exists(file_path)

    # Check the file contents
    with open(file_path, "r") as f:
        config = json.loads(f.read())

    assert config["model_type"] == "bert"

# Test using the comprehensive AI model testing setup
def test_ai_model_complete_scenario(mock_ai_model_testing_setup):
    """
    Test a complete AI model scenario using the mock_ai_model_testing_setup fixture.

    This shows how to use the comprehensive fixture that combines
    multiple mock implementations.
    """
    # Extract the components from the setup
    setup = mock_ai_model_testing_setup
    http = setup["http"]
    hf_hub = setup["huggingface_hub"]
    model_providers = setup["model_providers"]
    temp_dir = setup["temp_dir"]

    # Use the HTTP mock
    response = http.post(
        "https://api.openai.com / v1 / chat / completions",
        json={"model": "gpt - 3.5 - turbo", "messages": [{"role": "user", 
            "content": "Hello!"}]},
    )

    assert response.status_code == 200
    assert "This is a mock response" in response.json(
        )["choices"][0]["message"]["content"]

    # Use the Hugging Face Hub mock
    file_path = hf_hub.hf_hub_download(repo_id="gpt2", filename="config.json")

    assert os.path.exists(file_path)

    # Use the model providers
    openai = model_providers["openai"]
    response = openai.generate("Hello!")

    assert isinstance(response, dict) or isinstance(response, str)

    # Use the temporary directory for file operations
    test_file_path = os.path.join(temp_dir, "test.txt")
    with open(test_file_path, "w") as f:
        f.write("Test data")

    assert os.path.exists(test_file_path)

# Additional examples for monetization, marketing, and niche analysis testing

def test_monetization_scenario(mock_monetization_testing_setup):
    """
    Test a monetization scenario using the mock_monetization_testing_setup fixture.
    """
    setup = mock_monetization_testing_setup
    http = setup["http"]
    subscription_data = setup["subscription_data"]

    # Test creating a new customer
    response = http.post(
        "https://api.stripe.com / v1 / customers",
        json={"email": "new @ example.com", "name": "New Customer"},
    )

    assert response.status_code == 200

    # Check the subscription data
    assert subscription_data["customer"]["email"] == "test @ example.com"
    assert subscription_data["subscription"]["status"] == "active"

def test_marketing_scenario(mock_marketing_testing_setup):
    """
    Test a marketing scenario using the mock_marketing_testing_setup fixture.
    """
    setup = mock_marketing_testing_setup
    http = setup["http"]
    campaign_data = setup["campaign_data"]

    # Test sending an email
    response = http.post(
        "https://api.sendgrid.com / v3 / mail / send",
        json={
            "personalizations": [{"to": [{"email": "recipient @ example.com"}]}],
            "from": {"email": "sender @ example.com"},
            "subject": "Test Email",
            "content": [{"type": "text / plain", "value": "Hello!"}],
        },
    )

    assert response.status_code == 202

    # Check the campaign data
    assert campaign_data["campaign_name"] == "Spring Product Launch"
    assert len(campaign_data["channels"]) == 2

def test_niche_analysis_scenario(mock_niche_analysis_testing_setup):
    """
    Test a niche analysis scenario using the mock_niche_analysis_testing_setup fixture.
    """
    setup = mock_niche_analysis_testing_setup
    model_providers = setup["model_providers"]
    niche_data = setup["niche_data"]

    # Use the OpenAI provider to analyze niches
    openai = model_providers["openai"]
    response = openai.generate("identify niches")

    # The response should match what we've configured in the fixture
    assert isinstance(response, str)

    # Check the niche data
    niches = niche_data["niches"]
    assert len(niches) == 3
    assert niches[0]["name"] == "AI Productivity Tools"
    assert niches[0]["opportunity_score"] > 80
