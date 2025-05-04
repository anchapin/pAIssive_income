"""
AI Models GraphQL resolvers.

This module provides resolvers for AI models queries and mutations.
"""

import logging
from typing import List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO, format=" % (asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    import strawberry
    from strawberry.types import Info

    STRAWBERRY_AVAILABLE = True
except ImportError:
    logger.warning("Strawberry GraphQL is required for GraphQL resolvers")
    STRAWBERRY_AVAILABLE = False

if STRAWBERRY_AVAILABLE:
        InferenceInput,
        InferenceRequestType,
        InferenceResponseType,
        ModelInput,
        ModelMetricsType,
        ModelType,
        ModelTypeEnum,
        ModelVersionType,
    )

    @strawberry.type
    class AIModelsQuery:
        """AI models query resolvers."""

        @strawberry.field
        async def models(
            self,
            info: Info,
            model_type: Optional[ModelTypeEnum] = None,
            limit: Optional[int] = 10,
            offset: Optional[int] = 0,
        ) -> List[ModelType]:
            """
            Get a list of AI models.

            Args:
                info: GraphQL resolver info
                model_type: Filter by model type
                limit: Maximum number of models to return
                offset: Number of models to skip

            Returns:
                List of AI models
            """
            # Get AI models service from context
            service = info.context["services"].get("ai_models")
            if not service:
                logger.warning("AI models service not available")
                return []

            # Get models from service
            try:
                models = await service.get_models(
                    model_type=model_type.value if model_type else None, limit=limit, 
                        offset=offset
                )

                return [
                    ModelType(
                        id=str(model.id),
                        name=model.name,
                        description=model.description,
                        model_type=ModelTypeEnum(model.model_type),
                        provider=model.provider,
                        capabilities=model.capabilities,
                        created_at=model.created_at.isoformat() if model.created_at else None,
                        updated_at=model.updated_at.isoformat() if model.updated_at else None,
                    )
                    for model in models
                ]
            except Exception as e:
                logger.error(f"Error getting models: {str(e)}")
                return []

        @strawberry.field
        async def model(self, info: Info, id: str) -> Optional[ModelType]:
            """
            Get an AI model by ID.

            Args:
                info: GraphQL resolver info
                id: Model ID

            Returns:
                AI model if found, None otherwise
            """
            # Get AI models service from context
            service = info.context["services"].get("ai_models")
            if not service:
                logger.warning("AI models service not available")
                return None

            # Get model from service
            try:
                model = await service.get_model(id)
                if not model:
                    return None

                return ModelType(
                    id=str(model.id),
                    name=model.name,
                    description=model.description,
                    model_type=ModelTypeEnum(model.model_type),
                    provider=model.provider,
                    capabilities=model.capabilities,
                    created_at=model.created_at.isoformat() if model.created_at else None,
                    updated_at=model.updated_at.isoformat() if model.updated_at else None,
                )
            except Exception as e:
                logger.error(f"Error getting model: {str(e)}")
                return None

        @strawberry.field
        async def model_versions(self, info: Info, 
            model_id: str) -> List[ModelVersionType]:
            """
            Get versions of an AI model.

            Args:
                info: GraphQL resolver info
                model_id: Model ID

            Returns:
                List of model versions
            """
            # Get AI models service from context
            service = info.context["services"].get("ai_models")
            if not service:
                logger.warning("AI models service not available")
                return []

            # Get model versions from service
            try:
                versions = await service.get_model_versions(model_id)

                return [
                    ModelVersionType(
                        id=str(version.id),
                        model_id=str(version.model_id),
                        version=version.version,
                        description=version.description,
                        changes=version.changes,
                        created_at=version.created_at.isoformat() if version.created_at else None,
                    )
                    for version in versions
                ]
            except Exception as e:
                logger.error(f"Error getting model versions: {str(e)}")
                return []

        @strawberry.field
        async def model_metrics(self, info: Info, 
            model_id: str) -> Optional[ModelMetricsType]:
            """
            Get metrics for an AI model.

            Args:
                info: GraphQL resolver info
                model_id: Model ID

            Returns:
                Model metrics if found, None otherwise
            """
            # Get AI models service from context
            service = info.context["services"].get("ai_models")
            if not service:
                logger.warning("AI models service not available")
                return None

            # Get model metrics from service
            try:
                metrics = await service.get_model_metrics(model_id)
                if not metrics:
                    return None

                return ModelMetricsType(
                    model_id=str(metrics.model_id),
                    inference_count=metrics.inference_count,
                    average_latency=metrics.average_latency,
                    p95_latency=metrics.p95_latency,
                    p99_latency=metrics.p99_latency,
                    error_rate=metrics.error_rate,
                    token_usage=metrics.token_usage,
                    cost=metrics.cost,
                )
            except Exception as e:
                logger.error(f"Error getting model metrics: {str(e)}")
                return None

    @strawberry.type
    class AIModelsMutation:
        """AI models mutation resolvers."""

        @strawberry.mutation
        async def create_model(self, info: Info, 
            input: ModelInput) -> Optional[ModelType]:
            """
            Create a new AI model.

            Args:
                info: GraphQL resolver info
                input: Model input

            Returns:
                Created model if successful, None otherwise
            """
            # Get AI models service from context
            service = info.context["services"].get("ai_models")
            if not service:
                logger.warning("AI models service not available")
                return None

            # Create model
            try:
                model = await service.create_model(
                    name=input.name,
                    description=input.description,
                    model_type=input.model_type.value,
                    provider=input.provider,
                    capabilities=input.capabilities,
                )

                return ModelType(
                    id=str(model.id),
                    name=model.name,
                    description=model.description,
                    model_type=ModelTypeEnum(model.model_type),
                    provider=model.provider,
                    capabilities=model.capabilities,
                    created_at=model.created_at.isoformat() if model.created_at else None,
                    updated_at=model.updated_at.isoformat() if model.updated_at else None,
                )
            except Exception as e:
                logger.error(f"Error creating model: {str(e)}")
                return None

        @strawberry.mutation
        async def update_model(self, info: Info, id: str, 
            input: ModelInput) -> Optional[ModelType]:
            """
            Update an AI model.

            Args:
                info: GraphQL resolver info
                id: Model ID
                input: Model input

            Returns:
                Updated model if successful, None otherwise
            """
            # Get AI models service from context
            service = info.context["services"].get("ai_models")
            if not service:
                logger.warning("AI models service not available")
                return None

            # Update model
            try:
                model = await service.update_model(
                    id=id,
                    name=input.name,
                    description=input.description,
                    model_type=input.model_type.value,
                    provider=input.provider,
                    capabilities=input.capabilities,
                )

                if not model:
                    return None

                return ModelType(
                    id=str(model.id),
                    name=model.name,
                    description=model.description,
                    model_type=ModelTypeEnum(model.model_type),
                    provider=model.provider,
                    capabilities=model.capabilities,
                    created_at=model.created_at.isoformat() if model.created_at else None,
                    updated_at=model.updated_at.isoformat() if model.updated_at else None,
                )
            except Exception as e:
                logger.error(f"Error updating model: {str(e)}")
                return None

        @strawberry.mutation
        async def delete_model(self, info: Info, id: str) -> bool:
            """
            Delete an AI model.

            Args:
                info: GraphQL resolver info
                id: Model ID

            Returns:
                True if successful, False otherwise
            """
            # Get AI models service from context
            service = info.context["services"].get("ai_models")
            if not service:
                logger.warning("AI models service not available")
                return False

            # Delete model
            try:
                success = await service.delete_model(id)
                return success
            except Exception as e:
                logger.error(f"Error deleting model: {str(e)}")
                return False

        @strawberry.mutation
        async def run_inference(
            self, info: Info, input: InferenceInput
        ) -> Optional[InferenceResponseType]:
            """
            Run inference with an AI model.

            Args:
                info: GraphQL resolver info
                input: Inference input

            Returns:
                Inference response if successful, None otherwise
            """
            # Get AI models service from context
            service = info.context["services"].get("ai_models")
            if not service:
                logger.warning("AI models service not available")
                return None

            # Run inference
            try:
                response = await service.run_inference(
                    model_id=input.model_id,
                    input_data=input.input_data,
                    parameters=input.parameters,
                )

                if not response:
                    return None

                return InferenceResponseType(
                    request_id=str(response.request_id),
                    model_id=str(response.model_id),
                    output=response.output,
                    latency=response.latency,
                    token_usage=response.token_usage,
                    created_at=response.created_at.isoformat() if response.created_at else None,
                )
            except Exception as e:
                logger.error(f"Error running inference: {str(e)}")
                return None
