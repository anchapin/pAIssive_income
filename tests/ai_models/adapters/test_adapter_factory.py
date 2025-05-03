"""
Tests for the AdapterFactory class.
"""


import pytest

from ai_models.adapters import AdapterFactory, BaseModelAdapter
from errors import ModelError
from interfaces.model_interfaces import IModelAdapter


from ai_models.adapters import adapter_factory, get_adapter_factory

class MockAdapter(BaseModelAdapter):
    """Mock adapter for testing."""

    def __init__(self, **kwargs):
        super().__init__(name="Mock", description="Mock adapter for testing")
        self.kwargs = kwargs

    def connect(self, **kwargs):
        return True

    def disconnect(self):
        return True

    def get_models(self):
        return []


def test_adapter_factory_register():
    """Test registering an adapter with the factory."""
    factory = AdapterFactory()
    factory.register_adapter("mock", MockAdapter)

    assert "mock" in factory.get_available_adapters()


def test_adapter_factory_create():
    """Test creating an adapter from the factory."""
    factory = AdapterFactory()
    factory.register_adapter("mock", MockAdapter)

    adapter = factory.create_adapter("mock", param1="value1", param2="value2")

    assert isinstance(adapter, IModelAdapter)
    assert isinstance(adapter, MockAdapter)
    assert adapter.name == "Mock"
    assert adapter.kwargs["param1"] == "value1"
    assert adapter.kwargs["param2"] == "value2"


def test_adapter_factory_create_unknown():
    """Test creating an unknown adapter type."""
    factory = AdapterFactory()

    with pytest.raises(ModelError):
        factory.create_adapter("unknown")


def test_adapter_factory_get_available_adapters():
    """Test getting available adapter types."""
    factory = AdapterFactory()
    factory.register_adapter("mock1", MockAdapter)
    factory.register_adapter("mock2", MockAdapter)

    adapters = factory.get_available_adapters()

    assert "mock1" in adapters
    assert "mock2" in adapters
    assert len(adapters) == 2


def test_global_adapter_factory():
    """Test the global adapter factory."""
# Get the global factory
    factory = get_adapter_factory()

    # Verify it's the same instance
    assert factory is adapter_factory

    # Register a test adapter
    factory.register_adapter("test_mock", MockAdapter)

    # Create an adapter
    adapter = factory.create_adapter("test_mock")

    # Verify the adapter
    assert isinstance(adapter, MockAdapter)