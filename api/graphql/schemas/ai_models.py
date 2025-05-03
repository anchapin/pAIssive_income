"""
AI Models GraphQL schema.

This module provides GraphQL types and resolvers for the AI models module.
"""


import logging
from typing import Any, Dict, List, Optional


    import strawberry
    from strawberry.types import Info

    STRAWBERRY_AVAILABLE 

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:

= True
except ImportError:
    logger.warning("Strawberry GraphQL is required for GraphQL schema")
    STRAWBERRY_AVAILABLE = False

if STRAWBERRY_AVAILABLE:

    @strawberry.enum
    class ModelType:
        TEXT_GENERATION = "text_generation"
        TEXT_CLASSIFICATION = "text_classification"
        EMBEDDING = "embedding"
        IMAGE = "image"
        AUDIO = "audio"

    @strawberry.type
    class ModelMetrics:
        """Metrics for an AI model"""

        request_count: int
        error_count: int
        token_count: int
        latency_mean_ms: float
        latency_p90_ms: float
        latency_p99_ms: float

    @strawberry.type
    class AIModel:
        """AI model information"""

        id: strawberry.ID
        name: str
        description: str
        model_type: str
        provider: str
        version: str
        capabilities: List[str]
        parameters: Optional[Dict[str, Any]]
        metrics: Optional[ModelMetrics]

    @strawberry.type
    class ModelInferenceResult:
        """Result of model inference"""

        id: strawberry.ID
        model_id: strawberry.ID
        input_text: Optional[str]
        output_text: Optional[str]
        tokens_used: int
        processing_time_ms: float
        created_at: str

    @strawberry.input
    class TextGenerationInput:
        """Input for text generation"""

        prompt: str
        model_id: Optional[strawberry.ID] = None
        max_tokens: Optional[int] = None
        temperature: Optional[float] = None
        top_p: Optional[float] = None
        stop_sequences: Optional[List[str]] = None

    @strawberry.input
    class TextClassificationInput:
        """Input for text classification"""

        text: str
        model_id: Optional[strawberry.ID] = None
        labels: Optional[List[str]] = None

    @strawberry.input
    class EmbeddingInput:
        """Input for embedding generation"""

        text: str
        model_id: Optional[strawberry.ID] = None

    @strawberry.type
    class TextGenerationResult:
        """Result of text generation"""

        id: strawberry.ID
        text: str
        tokens_used: int
        processing_time_ms: float

    @strawberry.type
    class ClassificationLabel:
        """Classification label with confidence score"""

        label: str
        confidence: float

    @strawberry.type
    class TextClassificationResult:
        """Result of text classification"""

        id: strawberry.ID
        labels: List[ClassificationLabel]
        tokens_used: int
        processing_time_ms: float

    @strawberry.type
    class EmbeddingResult:
        """Result of embedding generation"""

        id: strawberry.ID
        embedding: List[float]
        dimensions: int
        tokens_used: int
        processing_time_ms: float

    @strawberry.type
    class AIModelsQuery:
        """AI models query fields"""

        @strawberry.field
        def ai_models(
            self, info: Info, model_type: Optional[ModelType] = None
        ) -> List[AIModel]:
            """
            Get all AI models, optionally filtered by type.

            Args:
                model_type: Optional filter for model type

            Returns:
                List of AI models
            """
            service = info.context["services"].get("ai_models")
            if not service:
                        return []

            # Convert enum to string if provided
            type_filter = model_type.value if model_type else None

            models = service.get_all_models(model_type=type_filter)
                    return [
                AIModel(
                    id=str(model.id),
                    name=model.name,
                    description=model.description,
                    model_type=model.model_type,
                    provider=model.provider,
                    version=model.version,
                    capabilities=model.capabilities,
                    parameters=model.parameters,
                    metrics=(
                        ModelMetrics(
                            request_count=model.metrics.request_count,
                            error_count=model.metrics.error_count,
                            token_count=model.metrics.token_count,
                            latency_mean_ms=model.metrics.latency_mean_ms,
                            latency_p90_ms=model.metrics.latency_p90_ms,
                            latency_p99_ms=model.metrics.latency_p99_ms,
                        )
                        if model.metrics
                        else None
                    ),
                )
                for model in models
            ]

        @strawberry.field
        def ai_model(self, info: Info, id: strawberry.ID) -> Optional[AIModel]:
            """
            Get a specific AI model.

            Args:
                id: ID of the AI model

            Returns:
                AI model if found, None otherwise
            """
            service = info.context["services"].get("ai_models")
            if not service:
                        return None

            model = service.get_model(id)
            if not model:
                        return None

                    return AIModel(
                id=str(model.id),
                name=model.name,
                description=model.description,
                model_type=model.model_type,
                provider=model.provider,
                version=model.version,
                capabilities=model.capabilities,
                parameters=model.parameters,
                metrics=(
                    ModelMetrics(
                        request_count=model.metrics.request_count,
                        error_count=model.metrics.error_count,
                        token_count=model.metrics.token_count,
                        latency_mean_ms=model.metrics.latency_mean_ms,
                        latency_p90_ms=model.metrics.latency_p90_ms,
                        latency_p99_ms=model.metrics.latency_p99_ms,
                    )
                    if model.metrics
                    else None
                ),
            )

        @strawberry.field
        def model_inference_history(
            self, info: Info, limit: int = 10
        ) -> List[ModelInferenceResult]:
            """
            Get model inference history.

            Args:
                limit: Maximum number of results to return

            Returns:
                List of model inference results
            """
            service = info.context["services"].get("ai_models")
            if not service:
                        return []

            history = service.get_inference_history(limit=limit)
                    return [
                ModelInferenceResult(
                    id=str(result.id),
                    model_id=str(result.model_id),
                    input_text=result.input_text,
                    output_text=result.output_text,
                    tokens_used=result.tokens_used,
                    processing_time_ms=result.processing_time_ms,
                    created_at=result.created_at.isoformat(),
                )
                for result in history
            ]

    @strawberry.type
    class AIModelsMutation:
        """AI models mutation fields"""

        @strawberry.mutation
        async def generate_text(
            self, info: Info, input: TextGenerationInput
        ) -> TextGenerationResult:
            """
            Generate text using an AI model.

            Args:
                input: Text generation input

            Returns:
                Text generation result
            """
            service = info.context["services"].get("ai_models")
            if not service:
                raise ValueError("AI models service not available")

            result = await service.generate_text(
                prompt=input.prompt,
                model_id=input.model_id,
                max_tokens=input.max_tokens,
                temperature=input.temperature,
                top_p=input.top_p,
                stop_sequences=input.stop_sequences,
            )

                    return TextGenerationResult(
                id=str(result.id),
                text=result.text,
                tokens_used=result.tokens_used,
                processing_time_ms=result.processing_time_ms,
            )

        @strawberry.mutation
        async def classify_text(
            self, info: Info, input: TextClassificationInput
        ) -> TextClassificationResult:
            """
            Classify text using an AI model.

            Args:
                input: Text classification input

            Returns:
                Text classification result
            """
            service = info.context["services"].get("ai_models")
            if not service:
                raise ValueError("AI models service not available")

            result = await service.classify_text(
                text=input.text, model_id=input.model_id, labels=input.labels
            )

                    return TextClassificationResult(
                id=str(result.id),
                labels=[
                    ClassificationLabel(label=label.label, confidence=label.confidence)
                    for label in result.labels
                ],
                tokens_used=result.tokens_used,
                processing_time_ms=result.processing_time_ms,
            )

        @strawberry.mutation
        async def generate_embedding(
            self, info: Info, input: EmbeddingInput
        ) -> EmbeddingResult:
            """
            Generate embedding for text using an AI model.

            Args:
                input: Embedding input

            Returns:
                Embedding result
            """
            service = info.context["services"].get("ai_models")
            if not service:
                raise ValueError("AI models service not available")

            result = await service.generate_embedding(
                text=input.text, model_id=input.model_id
            )

                    return EmbeddingResult(
                id=str(result.id),
                embedding=result.embedding,
                dimensions=result.dimensions,
                tokens_used=result.tokens_used,
                processing_time_ms=result.processing_time_ms,
            )

else:
    # Fallbacks if Strawberry isn't available
    class AIModelsQuery:
        pass

    class AIModelsMutation:
        pass