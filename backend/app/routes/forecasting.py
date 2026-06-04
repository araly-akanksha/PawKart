# ============================================================
# DEMAND FORECASTING ROUTES
# ============================================================
#
# Supports research objective #2:
# ML-based demand forecasting models that predict customer
# purchasing behavior and improve inventory planning accuracy.
#
# Pipeline:
#   1. Load trained LSTM weights via NumPy engine (no TF needed)
#   2. Build a 30-day sales sequence for the product
#   3. Scale → predict → inverse-transform
#   4. Classify demand + generate explainable report
# ============================================================

import os
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.dependencies import get_db
from app.models import Product, OrderItem, Order
from app.schemas import ForecastResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────

# File is at: backend/app/routes/forecasting.py
# Project root is 3 levels up: routes -> app -> backend -> PawKart
_BACKEND = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_PROJECT = os.path.abspath(os.path.join(_BACKEND, ".."))
MODEL_PATH = os.path.join(_PROJECT, "lstm_demand_forecasting_model.keras")
SCALER_PATH = os.path.join(_BACKEND, "demand_scaler.joblib")

# ── Load model and scaler ───────────────────────────────────

_model = None
_scaler = None
_SEQUENCE_LEN = 30

try:
    import numpy as np
    import joblib
    from app.lstm_engine import load_model as load_lstm_model

    if os.path.exists(MODEL_PATH):
        _model = load_lstm_model(MODEL_PATH)
        logger.info("LSTM model loaded (NumPy engine)")
    else:
        logger.warning("LSTM model not found at %s", MODEL_PATH)

    if os.path.exists(SCALER_PATH):
        _scaler = joblib.load(SCALER_PATH)
        logger.info("MinMaxScaler loaded from %s", SCALER_PATH)
    else:
        logger.warning("Scaler not found at %s — run save_scaler.py first", SCALER_PATH)

except Exception as e:
    logger.warning("Could not load ML artifacts: %s. Using statistical fallback.", e)


# ── Helpers ─────────────────────────────────────────────────

def classify_demand(predicted: float) -> str:
    if predicted > 500:
        return "High Demand"
    elif predicted > 200:
        return "Medium Demand"
    else:
        return "Low Demand"


def _build_sales_sequence(product_id: int, db: Session) -> list:
    """30 daily sales totals for a product (oldest → newest)."""
    import numpy as np
    today = datetime.utcnow().date()
    daily = []

    for offset in range(29, -1, -1):
        day = today - timedelta(days=offset)
        nxt = day + timedelta(days=1)

        total = (
            db.query(func.coalesce(func.sum(
                OrderItem.quantity * OrderItem.unit_price
            ), 0))
            .join(Order, OrderItem.order_id == Order.id)
            .filter(OrderItem.product_id == product_id)
            .filter(Order.created_at >= datetime.combine(day, datetime.min.time()))
            .filter(Order.created_at < datetime.combine(nxt, datetime.min.time()))
            .filter(Order.status != "cancelled")
            .scalar()
        ) or 0.0

        daily.append(float(total))

    return daily


def _forecast_statistical(product_id: int, db: Session) -> float:
    """Estimate weekly demand from 30-day order history."""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    total_sold = (
        db.query(func.coalesce(func.sum(OrderItem.quantity), 0))
        .join(Order, OrderItem.order_id == Order.id)
        .filter(OrderItem.product_id == product_id)
        .filter(Order.created_at >= thirty_days_ago)
        .filter(Order.status != "cancelled")
        .scalar()
    ) or 0

    daily_avg = total_sold / 30
    return max(round(daily_avg * 7), 0)


def _forecast_lstm(product_id: int, db: Session) -> dict:
    """LSTM prediction using the NumPy inference engine."""
    import numpy as np

    sales_seq = _build_sales_sequence(product_id, db)
    sales_array = np.array(sales_seq, dtype=np.float32).reshape(-1, 1)

    # Scale using the fitted MinMaxScaler
    scaled = _scaler.transform(sales_array)

    # Reshape for LSTM: (1 sample, 30 timesteps, 1 feature)
    X_input = scaled.reshape(1, _SEQUENCE_LEN, 1).astype(np.float32)

    # Predict using NumPy LSTM engine
    prediction_scaled = _model.predict(X_input)

    # Inverse transform
    prediction_actual = _scaler.inverse_transform(
        prediction_scaled.reshape(-1, 1)
    )[0][0]

    daily = max(float(prediction_actual), 0)
    weekly = max(round(daily * 7), 0)
    recent_avg = sum(sales_seq) / len(sales_seq)
    nonzero_days = sum(1 for s in sales_seq if s > 0)
    trend = "increasing" if sum(sales_seq[-7:]) > sum(sales_seq[:7]) else "stable or decreasing"

    return {
        "daily": round(daily, 2),
        "weekly": weekly,
        "method": "lstm",
        "recent_avg": round(recent_avg, 2),
        "nonzero_days": nonzero_days,
        "trend": trend,
    }


# ── Endpoint ────────────────────────────────────────────────

@router.get("/forecast/{product_id}", response_model=ForecastResponse)
def forecast_demand(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    name = product.product_name

    # Try LSTM first
    if _model is not None and _scaler is not None:
        try:
            r = _forecast_lstm(product_id, db)

            return ForecastResponse(
                product_id=product_id,
                predicted_demand_next_week=r["weekly"],
                demand_category=classify_demand(r["daily"]),
                confidence="high" if r["nonzero_days"] >= 10 else "medium",
                explanation=(
                    f"🧠 LSTM Neural Network Forecast for '{name}':\n\n"
                    f"• Predicted daily sales: ₹{r['daily']:,.0f}\n"
                    f"• Projected weekly demand: ~{r['weekly']} units\n"
                    f"• 30-day avg: ₹{r['recent_avg']:,.0f}/day "
                    f"({r['nonzero_days']}/30 active days)\n"
                    f"• Trend: {r['trend']}\n\n"
                    f"Model: 2-layer LSTM (64 units each), "
                    f"trained on 98,875 sales records with "
                    f"30-day sliding window sequences. "
                    f"Inference via pure-NumPy engine (no TensorFlow required)."
                ),
            )
        except Exception as e:
            logger.error("LSTM prediction failed for product %d: %s", product_id, e)

    # Statistical fallback
    predicted = _forecast_statistical(product_id, db)

    return ForecastResponse(
        product_id=product_id,
        predicted_demand_next_week=predicted,
        demand_category=classify_demand(predicted),
        confidence="medium" if predicted > 0 else "low",
        explanation=(
            f"📊 Statistical Forecast for '{name}':\n\n"
            f"• Estimated weekly demand: ~{predicted} units\n"
            f"• Method: 30-day moving average extrapolation\n\n"
            f"Note: LSTM model scaler not found. "
            f"Run `python save_scaler.py` to enable neural network predictions."
        ),
    )
