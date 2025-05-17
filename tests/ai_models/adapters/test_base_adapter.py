"""test_base_adapter - Module for tests/ai_models/adapters.test_base_adapter."""

# Standard library imports
import pytest

# Third-party imports

# Local imports
from ai_models.adapters import BaseModelAdapter


class TestBaseModelAdapter:
    """Test the BaseModelAdapter abstract class."""

    def test_base_adapter_is_abstract(self):
        """Test that BaseModelAdapter is an abstract class that cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseModelAdapter()

    def test_required_methods(self):
        """Test that BaseModelAdapter requires specific methods to be implemented."""
        # Create a class that inherits from BaseModelAdapter but doesn't implement all methods
        class IncompleteAdapter(BaseModelAdapter):
            pass

        # Attempting to instantiate the incomplete adapter should raise TypeError
        with pytest.raises(TypeError):
            IncompleteAdapter()

    def test_partial_implementation(self):
        """Test that BaseModelAdapter requires all methods to be implemented."""
        # Create a class that inherits from BaseModelAdapter but only implements some methods
        class PartialAdapter(BaseModelAdapter):
            async def list_models(self):
                return []

            async def generate_text(self, model, prompt, **kwargs):
                return {"text": "test"}

        # Attempting to instantiate the partial adapter should raise TypeError
        with pytest.raises(TypeError):
            PartialAdapter()

    def test_complete_implementation(self):
        """Test that a complete implementation of BaseModelAdapter can be instantiated."""
        # Create a class that implements all required methods
        class CompleteAdapter(BaseModelAdapter):
            async def list_models(self):
                return []

            async def generate_text(self, model, prompt, **kwargs):
                return {"text": "test"}

            async def generate_chat_completions(self, model, messages, **kwargs):
                return {"message": {"role": "assistant", "content": "test"}}

            async def close(self):
                pass

        # Instantiating the complete adapter should not raise any exceptions
        adapter = CompleteAdapter()
        assert isinstance(adapter, BaseModelAdapter)

    @pytest.mark.asyncio
    async def test_concrete_implementation_methods(self):
        """Test that a concrete implementation's methods can be called."""
        # Create a class that implements all required methods
        class TestAdapter(BaseModelAdapter):
            async def list_models(self):
                return [{"id": "model1"}, {"id": "model2"}]

            async def generate_text(self, model, prompt, **kwargs):
                return {"text": f"Response to: {prompt}", "model": model, "kwargs": kwargs}

            async def generate_chat_completions(self, model, messages, **kwargs):
                return {
                    "choices": [{"message": {"content": "Chat response"}}],
                    "model": model,
                    "messages": messages,
                    "kwargs": kwargs
                }

            async def close(self):
                self.closed = True

        # Create an instance and test the methods
        adapter = TestAdapter()

        # Test list_models
        models = await adapter.list_models()
        assert len(models) == 2
        assert models[0]["id"] == "model1"
        assert models[1]["id"] == "model2"

        # Test generate_text
        response = await adapter.generate_text("model1", "Hello", temperature=0.7)
        assert response["text"] == "Response to: Hello"
        assert response["model"] == "model1"
        assert response["kwargs"]["temperature"] == 0.7

        # Test generate_chat_completions
        messages = [{"role": "user", "content": "Hi"}]
        chat_response = await adapter.generate_chat_completions("model1", messages, max_tokens=100)
        assert chat_response["choices"][0]["message"]["content"] == "Chat response"
        assert chat_response["model"] == "model1"
        assert chat_response["messages"] == messages
        assert chat_response["kwargs"]["max_tokens"] == 100

        # Test close
        await adapter.close()
        assert adapter.closed is True
