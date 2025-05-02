"""
AI Models service for the pAIssive Income API.

This module provides a service for interacting with the AI model endpoints.
"""

from typing import Dict, Any

from .base import BaseService


class AIModelsService(BaseService):
    """
    AI Models service.
    """

    def get_models(self) -> Dict[str, Any]:
        """
        Get all available AI models.

        Returns:
            List of AI models
        """
        return self._get("ai-models/models")

    def get_model(self, model_id: str) -> Dict[str, Any]:
        """
        Get details for a specific AI model.

        Args:
            model_id: Model ID

        Returns:
            Model details
        """
        return self._get(f"ai-models/models/{model_id}")

    def run_inference(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run inference on an AI model.

        Args:
            data: Inference request data
                - model_id: Model ID
                - inputs: Input data for the model
                - parameters: Inference parameters

        Returns:
            Inference results
        """
        return self._post("ai-models/inference", data)

    def download_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Download or register an AI model.

        Args:
            data: Model download data
                - name: Model name
                - source: Model source
                - version: Model version

        Returns:
            Download status
        """
        return self._post("ai-models/models/download", data)

    def get_model_performance(self, model_id: str) -> Dict[str, Any]:
        """
        Get performance metrics for a specific AI model.

        Args:
            model_id: Model ID

        Returns:
            Performance metrics
        """
        return self._get(f"ai-models/models/{model_id}/performance")

    def compare_models(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare multiple AI models.

        Args:
            data: Model comparison data
                - model_ids: List of model IDs to compare
                - metrics: List of metrics to compare
                - test_data: Optional test data for evaluation

        Returns:
            Comparison results
        """
        return self._post("ai-models/models/compare", data)

    def create_model_version(
        self, model_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new version of an AI model.

        Args:
            model_id: Model ID
            data: Version creation data
                - version: Version name
                - changes: Description of changes
                - parameters: Model parameters

        Returns:
            Created model version
        """
        return self._post(f"ai-models/models/{model_id}/versions", data)
