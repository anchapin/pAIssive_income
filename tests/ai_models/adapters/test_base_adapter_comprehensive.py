"""Comprehensive tests for the ai_models.adapters.base_adapter module."""

import abc
from typing import Any, Dict, List

import pytest

from ai_models.adapters.base_adapter import BaseModelAdapter


class TestBaseAdapterComprehensive:
    """Comprehensive test suite for the BaseModelAdapter class."""

    def test_base_adapter_is_abstract(self):
        """Test that BaseModelAdapter is an abstract class."""
        # Verify that BaseModelAdapter is an abstract class
        assert issubclass(BaseModelAdapter, abc.ABC)

        # Verify that BaseModelAdapter cannot be instantiated directly
        with pytest.raises(TypeError) as excinfo:
            BaseModelAdapter()

        assert "Can't instantiate abstract class" in str(excinfo.value)

    def test_base_adapter_abstract_methods(self):
        """Test that BaseModelAdapter has the expected abstract methods."""
        # Get the abstract methods from the class
        abstract_methods = BaseModelAdapter.__abstractmethods__

        # Verify that the expected methods are abstract
        assert "list_models" in abstract_methods
        assert "generate_text" in abstract_methods
        assert "generate_chat_completions" in abstract_methods
        assert "close" in abstract_methods

    def test_incomplete_implementation(self):
        """Test that an incomplete implementation of BaseModelAdapter cannot be instantiated."""
        # Create a class that implements only some of the required methods
        class IncompleteAdapter(BaseModelAdapter):
            async def list_models(self) -> List[Dict[str, Any]]:
                return []

            async def generate_text(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
                return {"text": "test"}

        # Verify that the incomplete implementation cannot be instantiated
        with pytest.raises(TypeError) as excinfo:
            IncompleteAdapter()

        assert "Can't instantiate abstract class" in str(excinfo.value)

    def test_complete_implementation(self):
        """Test that a complete implementation of BaseModelAdapter can be instantiated."""
        # Create a class that implements all required methods
        class CompleteAdapter(BaseModelAdapter):
            async def list_models(self) -> List[Dict[str, Any]]:
                return []

            async def generate_text(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
                return {"text": "test"}

            async def generate_chat_completions(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
                return {"message": {"role": "assistant", "content": "test"}}

            async def close(self):
                pass

        # Verify that the complete implementation can be instantiated
        adapter = CompleteAdapter()
        assert isinstance(adapter, BaseModelAdapter)

    @pytest.mark.asyncio
    async def test_concrete_implementation_methods(self):
        """Test that a concrete implementation's methods can be called."""
        # Create a class that implements all required methods
        class TestAdapter(BaseModelAdapter):
            async def list_models(self) -> List[Dict[str, Any]]:
                return [{"id": "model1"}, {"id": "model2"}]

            async def generate_text(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
                return {"text": f"Generated text for {prompt}"}

            async def generate_chat_completions(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
                return {"message": {"role": "assistant", "content": "Chat response"}}

            async def close(self):
                pass

        # Instantiate the adapter
        adapter = TestAdapter()

        # Test list_models method
        models = await adapter.list_models()
        assert len(models) == 2
        assert models[0]["id"] == "model1"
        assert models[1]["id"] == "model2"

        # Test generate_text method
        text_response = await adapter.generate_text("model1", "Hello")
        assert text_response["text"] == "Generated text for Hello"

        # Test generate_chat_completions method
        chat_response = await adapter.generate_chat_completions(
            "model1",
            [{"role": "user", "content": "Hello"}]
        )
        assert chat_response["message"]["role"] == "assistant"
        assert chat_response["message"]["content"] == "Chat response"

        # Test close method
        await adapter.close()

    @pytest.mark.asyncio
    async def test_implementation_with_additional_methods(self):
        """Test that a concrete implementation can have additional methods."""
        # Create a class that implements all required methods and adds additional ones
        class ExtendedAdapter(BaseModelAdapter):
            async def list_models(self) -> List[Dict[str, Any]]:
                return [{"id": "model1"}]

            async def generate_text(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
                return {"text": "test"}

            async def generate_chat_completions(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
                return {"message": {"role": "assistant", "content": "test"}}

            async def close(self):
                pass

            async def additional_method(self) -> str:
                return "additional"

        # Instantiate the adapter
        adapter = ExtendedAdapter()

        # Test the additional method
        result = await adapter.additional_method()
        assert result == "additional"

    @pytest.mark.asyncio
    async def test_implementation_with_constructor(self):
        """Test that a concrete implementation can have a constructor."""
        # Create a class that implements all required methods and has a constructor
        class AdapterWithConstructor(BaseModelAdapter):
            def __init__(self, base_url: str, api_key: str):
                self.base_url = base_url
                self.api_key = api_key

            async def list_models(self) -> List[Dict[str, Any]]:
                return [{"id": "model1"}]

            async def generate_text(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
                return {"text": f"Using {self.base_url} with key {self.api_key}"}

            async def generate_chat_completions(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
                return {"message": {"role": "assistant", "content": "test"}}

            async def close(self):
                pass

        # Instantiate the adapter with constructor arguments
        adapter = AdapterWithConstructor("https://api.example.com", "sk-123456")

        # Test that the constructor arguments were stored
        assert adapter.base_url == "https://api.example.com"
        assert adapter.api_key == "sk-123456"

        # Test that the methods can use the constructor arguments
        text_response = await adapter.generate_text("model1", "Hello")
        assert text_response["text"] == "Using https://api.example.com with key sk-123456"
