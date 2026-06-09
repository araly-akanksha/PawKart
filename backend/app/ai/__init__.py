# AI Forecasting Module
import os
import logging
from app.ai.registry import registry
from app.ai.models.lstm_model import LstmForecastModel

logger = logging.getLogger(__name__)


def init_models():
    """Instantiate, load, and register all forecasting models."""
    # 1. LSTM Model
    lstm_model = LstmForecastModel()
    
    # Determine model & scaler paths relative to this file
    # app/ai/__init__.py -> app/ -> backend/ -> PawKart/
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    project_dir = os.path.abspath(os.path.join(backend_dir, ".."))
    
    lstm_path = os.path.join(project_dir, "lstm_demand_forecasting_model.keras")
    scaler_path = os.path.join(backend_dir, "demand_scaler.joblib")
    
    try:
        lstm_model.load(lstm_path, scaler_path)
        registry.register("lstm", lstm_model)
        logger.info("LSTM model successfully initialized and registered.")
    except Exception as e:
        logger.error("Failed to load LSTM weights during startup: %s. Model registered as unloaded.", e)
        registry.register("lstm", lstm_model)


__all__ = ["registry", "init_models"]
