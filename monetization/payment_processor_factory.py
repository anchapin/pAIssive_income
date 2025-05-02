"""
Payment processor factory for the pAIssive Income project.

This module provides a factory class for creating and managing payment processor instances.
"""

import importlib
from typing import Any, Dict, List, Optional, Type

from .mock_payment_processor import MockPaymentProcessor
from .payment_processor import PaymentProcessor


class PaymentProcessorFactory:
    """
    Factory class for creating and managing payment processor instances.

    This class provides methods for registering payment processor classes,
    creating payment processor instances, and managing existing instances.
    """

    def __init__(self):
        """Initialize the payment processor factory."""
        self.processor_classes = {}
        self.processor_instances = {}

        # Register built-in payment processors
        self.register_processor("mock", MockPaymentProcessor)

    def register_processor(
        self, processor_type: str, processor_class: Type[PaymentProcessor]
    ) -> None:
        """
        Register a payment processor class.

        Args:
            processor_type: Type identifier for the processor
            processor_class: Payment processor class
        """
        self.processor_classes[processor_type] = processor_class

    def register_processor_from_module(
        self, processor_type: str, module_name: str, class_name: str
    ) -> None:
        """
        Register a payment processor class from a module.

        Args:
            processor_type: Type identifier for the processor
            module_name: Name of the module containing the processor class
            class_name: Name of the processor class
        """
        try:
            module = importlib.import_module(module_name)
            processor_class = getattr(module, class_name)
            self.register_processor(processor_type, processor_class)
        except (ImportError, AttributeError) as e:
            raise ValueError(
                f"Failed to load payment processor class {class_name} from module {module_name}: {e}"
            )

    def create_processor(
        self, processor_type: str, processor_id: str, config: Dict[str, Any]
    ) -> PaymentProcessor:
        """
        Create a payment processor instance.

        Args:
            processor_type: Type of the processor
            processor_id: ID for the processor instance
            config: Configuration for the processor

        Returns:
            Payment processor instance
        """
        # Check if processor type is registered
        if processor_type not in self.processor_classes:
            raise ValueError(f"Unknown payment processor type: {processor_type}")

        # Check if processor ID is already in use
        if processor_id in self.processor_instances:
            raise ValueError(f"Payment processor ID already in use: {processor_id}")

        # Create processor instance
        processor_class = self.processor_classes[processor_type]
        processor = processor_class(config)

        # Store processor instance
        self.processor_instances[processor_id] = processor

        return processor

    def get_processor(self, processor_id: str) -> Optional[PaymentProcessor]:
        """
        Get a payment processor instance by ID.

        Args:
            processor_id: ID of the processor

        Returns:
            Payment processor instance or None if not found
        """
        return self.processor_instances.get(processor_id)

    def list_processors(self) -> List[PaymentProcessor]:
        """
        List all payment processor instances.

        Returns:
            List of payment processor instances
        """
        return list(self.processor_instances.values())

    def remove_processor(self, processor_id: str) -> bool:
        """
        Remove a payment processor instance.

        Args:
            processor_id: ID of the processor

        Returns:
            True if the processor was removed, False otherwise
        """
        if processor_id in self.processor_instances:
            del self.processor_instances[processor_id]
            return True

        return False

    def get_processor_types(self) -> List[str]:
        """
        Get a list of registered processor types.

        Returns:
            List of processor types
        """
        return list(self.processor_classes.keys())


# Create a global factory instance
factory = PaymentProcessorFactory()


# Example usage
if __name__ == "__main__":
    # Create a mock payment processor
    mock_processor = factory.create_processor(
        processor_type="mock",
        processor_id="mock1",
        config={
            "name": "Test Mock Processor",
            "success_rate": 0.95,
            "simulate_network_errors": True,
            "network_error_rate": 0.05,
        },
    )

    print(f"Created processor: {mock_processor}")

    # Get processor by ID
    processor = factory.get_processor("mock1")
    print(f"Retrieved processor: {processor}")

    # List all processors
    processors = factory.list_processors()
    print(f"All processors: {processors}")

    # List processor types
    processor_types = factory.get_processor_types()
    print(f"Available processor types: {processor_types}")

    # Remove processor
    removed = factory.remove_processor("mock1")
    print(f"Processor removed: {removed}")

    # Verify processor is removed
    processor = factory.get_processor("mock1")
    print(f"Processor after removal: {processor}")
