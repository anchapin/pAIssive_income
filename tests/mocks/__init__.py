"""
"""
Mock implementations for testing.
Mock implementations for testing.


This package provides mock implementations of various external dependencies
This package provides mock implementations of various external dependencies
that can be used for consistent testing without actually connecting to
that can be used for consistent testing without actually connecting to
external services or APIs.
external services or APIs.
"""
"""


from .mock_external_apis import (MockEmailAPI, MockExternalAPIBase,
from .mock_external_apis import (MockEmailAPI, MockExternalAPIBase,
MockHuggingFaceAPI, MockPaymentAPI,
MockHuggingFaceAPI, MockPaymentAPI,
MockStorageAPI, create_mock_api)
MockStorageAPI, create_mock_api)
from .mock_model_providers import (MockBaseModelProvider, MockLMStudioProvider,
from .mock_model_providers import (MockBaseModelProvider, MockLMStudioProvider,
MockOllamaProvider, MockOpenAIProvider,
MockOllamaProvider, MockOpenAIProvider,
create_mock_provider)
create_mock_provider)


__all__ = [
__all__ = [
# Model providers
# Model providers
"MockBaseModelProvider",
"MockBaseModelProvider",
"MockOpenAIProvider",
"MockOpenAIProvider",
"MockOllamaProvider",
"MockOllamaProvider",
"MockLMStudioProvider",
"MockLMStudioProvider",
"create_mock_provider",
"create_mock_provider",
# External APIs
# External APIs
"MockExternalAPIBase",
"MockExternalAPIBase",
"MockHuggingFaceAPI",
"MockHuggingFaceAPI",
"MockPaymentAPI",
"MockPaymentAPI",
"MockEmailAPI",
"MockEmailAPI",
"MockStorageAPI",
"MockStorageAPI",
"create_mock_api",
"create_mock_api",
]
]

