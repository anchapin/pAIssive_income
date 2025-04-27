"""
Mock implementations for testing.

This package provides mock implementations of various external dependencies
that can be used for consistent testing without actually connecting to
external services or APIs.
"""

from .mock_model_providers import (
    MockBaseModelProvider,
    MockOpenAIProvider,
    MockOllamaProvider,
    MockLMStudioProvider,
    create_mock_provider
)

from .mock_external_apis import (
    MockExternalAPIBase,
    MockHuggingFaceAPI,
    MockPaymentAPI,
    MockEmailAPI,
    MockStorageAPI,
    create_mock_api
)

__all__ = [
    # Model providers
    'MockBaseModelProvider',
    'MockOpenAIProvider',
    'MockOllamaProvider',
    'MockLMStudioProvider',
    'create_mock_provider',
    
    # External APIs
    'MockExternalAPIBase',
    'MockHuggingFaceAPI',
    'MockPaymentAPI',
    'MockEmailAPI',
    'MockStorageAPI',
    'create_mock_api',
]