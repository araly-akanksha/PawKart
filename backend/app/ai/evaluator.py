"""
Evaluation Framework for PawKart Forecasting Models
===================================================
Computes precision metrics (RMSE, MAE, MAPE, R² Score) and timing metrics
for model benchmarking, with optional persistence to the database.
"""

import time
import logging
from typing import Dict, Any, Optional
import numpy as np
from sqlalchemy.orm import Session

from app.ai.base import ForecastModel
from app.models import ModelEvaluation

logger = logging.getLogger(__name__)


def calculate_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Compute regression precision metrics: RMSE, MAE, MAPE, and R² Score.
    Handles division-by-zero cases in MAPE cleanly by filtering out zeros.
    """
    y_true = np.asarray(y_true, dtype=np.float64).flatten()
    y_pred = np.asarray(y_pred, dtype=np.float64).flatten()

    if len(y_true) == 0:
        return {"rmse": 0.0, "mae": 0.0, "mape": 0.0, "r2_score": 0.0}

    # 1. MAE (Mean Absolute Error)
    mae = float(np.mean(np.abs(y_true - y_pred)))

    # 2. RMSE (Root Mean Squared Error)
    mse = np.mean((y_true - y_pred) ** 2)
    rmse = float(np.sqrt(mse))

    # 3. MAPE (Mean Absolute Percentage Error)
    # Exclude zero sales from the denominator to avoid division by zero
    zero_mask = y_true > 0.0
    if np.any(zero_mask):
        mape = float(np.mean(np.abs((y_true[zero_mask] - y_pred[zero_mask]) / y_true[zero_mask])) * 100.0)
    else:
        mape = 0.0

    # 4. R² (R-squared Score)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    
    if ss_tot > 0:
        r2_score = float(1.0 - (ss_res / ss_tot))
    else:
        r2_score = 0.0  # Constant true values

    return {
        "rmse": rmse,
        "mae": mae,
        "mape": mape,
        "r2_score": r2_score
    }


def evaluate_model(
    model: ForecastModel,
    X: np.ndarray,
    y_true: np.ndarray,
    db: Optional[Session] = None,
    dataset_version: str = "1.0.0",
    use_inverse_scale: bool = True,
    training_time_seconds: Optional[float] = None
) -> Dict[str, Any]:
    """
    Evaluate a model on a given dataset, measure inference latency, and optionally persist to DB.
    
    Args:
        model: An instance of ForecastModel.
        X: Input features. Shape (batch, sequence, features) for sequence or (batch, features) for tabular.
        y_true: Ground truth target values (actual/original scale if use_inverse_scale=True).
        db: Optional SQLAlchemy Session database connection.
        dataset_version: Identifier of the test dataset.
        use_inverse_scale: If True, evaluates on inverse-scaled predictions (actual sales).
        training_time_seconds: Optional float of how long the model took to train.
    """
    if not model.is_loaded:
        raise ValueError(f"Model '{model.model_type}' is not loaded. Cannot run evaluation.")

    # Time prediction latency
    start_time = time.perf_counter()
    if use_inverse_scale:
        y_pred = model.predict_with_inverse(X)
    else:
        y_pred = model.predict(X)
    end_time = time.perf_counter()
    
    inference_time_total_ms = (end_time - start_time) * 1000.0
    sample_count = len(X)
    inference_time_per_sample_ms = inference_time_total_ms / max(sample_count, 1)

    # Compute regression metrics
    metrics = calculate_regression_metrics(y_true, y_pred)
    
    results = {
        "model_type": model.model_type,
        "dataset_version": dataset_version,
        "rmse": round(metrics["rmse"], 4),
        "mae": round(metrics["mae"], 4),
        "mape": round(metrics["mape"], 2),
        "r2_score": round(metrics["r2_score"], 4),
        "inference_time_ms": round(inference_time_per_sample_ms, 4),
        "sample_count": sample_count,
        "training_time_seconds": training_time_seconds
    }

    # Persist to database if Session provided
    if db is not None:
        try:
            eval_record = ModelEvaluation(
                model_type=results["model_type"],
                dataset_version=results["dataset_version"],
                rmse=results["rmse"],
                mae=results["mae"],
                mape=results["mape"],
                r2_score=results["r2_score"],
                training_time_seconds=results["training_time_seconds"],
                inference_time_ms=results["inference_time_ms"],
                sample_count=results["sample_count"]
            )
            db.add(eval_record)
            db.commit()
            db.refresh(eval_record)
            results["id"] = eval_record.id
            logger.info("Saved evaluation results for '%s' to database.", model.model_type)
        except Exception as e:
            db.rollback()
            logger.error("Failed to save model evaluation to database: %s", e)

    return results
