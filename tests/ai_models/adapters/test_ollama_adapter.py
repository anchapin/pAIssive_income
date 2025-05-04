"""
Tests for the OllamaAdapter class.
"""

from unittest.mock import MagicMock, Mock, patch

from ai_models.adapters import OllamaAdapter
from interfaces.model_interfaces import IModelAdapter


def test_ollama_adapter_implements_interface():
    """Test that OllamaAdapter implements the IModelAdapter interface."""
    with patch("requests.Session") as mock_session:
    # Mock the get response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_session.return_value.get.return_value = mock_response

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    assert isinstance(adapter, IModelAdapter)


    @patch("ai_models.adapters.ollama_adapter.requests.Session")
    def test_ollama_adapter_connect(mock_session):
    """Test the connect method."""
    # Mock the session
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance

    # Mock the response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_session_instance.get.return_value = mock_response

    # Create the adapter with _check_ollama_status mocked to avoid the initial call
    with patch.object(OllamaAdapter, "_check_ollama_status"):
    adapter = OllamaAdapter(base_url="http://localhost:11434")

    # Reset the mock to clear the call history
    mock_session_instance.get.reset_mock()

    # Test the connect method
    result = adapter.connect()

    # Verify the result
    assert result is True
    assert adapter._connected is True
    mock_session_instance.get.assert_called_once_with(
    "http://localhost:11434", timeout=5
    )


    @patch("ai_models.adapters.ollama_adapter.requests.Session")
    def test_ollama_adapter_disconnect(mock_session):
    """Test the disconnect method."""
    # Mock the session
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance

    # Create the adapter with _check_ollama_status mocked to avoid the initial call
    with patch.object(OllamaAdapter, "_check_ollama_status"):
    adapter = OllamaAdapter(base_url="http://localhost:11434")

    # Test the disconnect method
    result = adapter.disconnect()

    # Verify the result
    assert result is True
    assert adapter._connected is False
    mock_session_instance.close.assert_called_once()


    @patch("ai_models.adapters.ollama_adapter.requests.Session")
    def test_ollama_adapter_get_models(mock_session):
    """Test the get_models method."""
    # Mock the session
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance

    # Mock the response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
    "models": [
    {
    "name": "llama2:latest",
    "size": 3791730298,
    "modified_at": "2023-10-10T12:34:56Z",
    },
    {
    "name": "mistral:latest",
    "size": 4289147034,
    "modified_at": "2023-10-11T12:34:56Z",
    },
    ]
    }
    mock_session_instance.get.return_value = mock_response

    # Create the adapter with _check_ollama_status mocked to avoid the initial call
    with patch.object(OllamaAdapter, "_check_ollama_status"):
    adapter = OllamaAdapter(base_url="http://localhost:11434")

    # Reset the mock to clear the call history
    mock_session_instance.get.reset_mock()

    # Test the get_models method
    models = adapter.get_models()

    # Verify the result
    assert len(models) == 2
    assert models[0]["id"] == "llama2:latest"
    assert models[0]["name"] == "llama2"
    assert models[0]["type"] == "llm"
    assert models[0]["adapter"] == "ollama"
    assert models[1]["id"] == "mistral:latest"
    assert models[1]["name"] == "mistral"
    assert models[1]["type"] == "llm"
    assert models[1]["adapter"] == "ollama"
    mock_session_instance.get.assert_called_with(
    "http://localhost:11434/api/tags", timeout=60
    )
