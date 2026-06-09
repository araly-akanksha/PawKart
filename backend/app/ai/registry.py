"""
Model Registry for PawKart forecasting models.
==============================================
Provides a central registry to register, look up, and manage forecasting models.
"""

from typing import Dict, List, Optional
from app.ai.base import ForecastModel


class ModelRegistry:
    """Registry that maps model types to model instances."""

    def __init__(self):
        self._registry: Dict[str, ForecastModel] = {}

    def register(self, model_type: str, model_instance: ForecastModel) -> None:
        """Register a model instance under a specific model_type."""
        self._registry[model_type] = model_instance

    def get_model(self, model_type: str) -> ForecastModel:
        """
        Retrieve a model instance by model_type.
        Raises ValueError if the model_type is not registered.
        """
        if model_type not in self._registry:
            raise ValueError(
                f"Model '{model_type}' is not registered. "
                f"Available models: {list(self._registry.keys())}"
            )
        return self._registry[model_type]

    def has_model(self, model_type: str) -> bool:
        """Check if a model type is registered."""
        return model_type in self._registry

    def list_models(self) -> List[str]:
        """List all registered model types."""
        return list(self._registry.keys())

    def get_all_models(self) -> Dict[str, ForecastModel]:
        """Get the full registry dict."""
        return self._registry


# Global registry instance
registry = ModelRegistry()
