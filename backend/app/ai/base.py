"""
Abstract Base Class for all PawKart forecasting models.
=========================================================
Every model (LSTM, GRU, XGBoost, Random Forest) must implement
this interface to be registered, evaluated, and used in ensemble
forecasting.

Design principles:
  - Dataset-agnostic: models accept numpy arrays, not CSV paths
  - Version-aware: each model tracks its version and training metadata
  - Explainability-ready: models expose feature importance when available
  - Future-proof: interface supports both sequence models (RNN) and
    feature-engineered models (tree-based)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import numpy as np


@dataclass
class ModelMetadata:
    """Metadata about a loaded model instance."""
    model_type: str           # "lstm", "gru", "xgboost", "random_forest"
    version: str = "1.0.0"
    trained_at: Optional[str] = None
    dataset_version: Optional[str] = None
    description: str = ""
    input_type: str = "sequence"  # "sequence" (RNN) or "tabular" (tree)
    sequence_length: int = 30
    feature_names: list = field(default_factory=list)


class ForecastModel(ABC):
    """
    Abstract interface for all demand forecasting models.
    
    Lifecycle:
      1. Instantiate with model_type
      2. Call load(path) to load persisted weights/model
      3. Call predict(X) to run inference
      4. Call evaluate(X, y_true) to compute metrics
    """

    def __init__(self, model_type: str):
        self._model_type = model_type
        self._loaded = False
        self._metadata = ModelMetadata(model_type=model_type)

    @property
    def model_type(self) -> str:
        return self._model_type

    @property
    def metadata(self) -> ModelMetadata:
        return self._metadata

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    # ── Abstract Methods ─────────────────────────────────────

    @abstractmethod
    def load(self, model_path: str, scaler_path: Optional[str] = None) -> None:
        """Load model weights/artifacts from disk."""
        ...

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Run inference.
        
        For sequence models (LSTM/GRU):
          X shape: (batch, timesteps, features)
          Returns: (batch, 1) — scaled predictions
        
        For tabular models (XGBoost/RF):
          X shape: (batch, num_features)
          Returns: (batch, 1) — scaled predictions
        """
        ...

    @abstractmethod
    def predict_with_inverse(
        self, X: np.ndarray
    ) -> np.ndarray:
        """
        Predict and inverse-transform to original scale.
        Returns actual sales values, not scaled values.
        """
        ...

    # ── Optional Methods (override where applicable) ─────────

    def get_feature_importance(self) -> Optional[dict]:
        """
        Return feature importance scores if the model supports it.
        Returns: dict mapping feature_name → importance_score, or None.
        
        - XGBoost/RF: built-in feature importance
        - LSTM/GRU: return None (use SHAP externally)
        """
        return None

    def get_model_summary(self) -> dict:
        """Return a human-readable summary of the model."""
        return {
            "model_type": self._model_type,
            "loaded": self._loaded,
            "version": self._metadata.version,
            "input_type": self._metadata.input_type,
            "description": self._metadata.description,
        }
