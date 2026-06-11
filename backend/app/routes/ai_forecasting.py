import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas import TFTForecastResponse

from app.ai.forecasting.predictor import get_product_forecast

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/forecast/product/{product_id}", response_model=TFTForecastResponse)
def get_tft_product_forecast(
    product_id: int, 
    db: Session = Depends(get_db)
):
    """
    Temporal Fusion Transformer (TFT) Demand Forecasting Proxy.
    Returns predicted demand for 1, 7, and 30 day horizons.
    """
    logger.info(f"Demand forecast requested for product {product_id}")
    return get_product_forecast(product_id, db)

@router.get("/forecast/store/{store_id}", response_model=list[TFTForecastResponse])
def get_tft_store_forecast(
    store_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    [STUB] Store-level aggregated TFT Forecasting.
    """
    return [
        TFTForecastResponse(
            product_id=1,
            forecast_1_day=20,
            forecast_7_days=150,
            forecast_30_days=600,
            confidence=0.85
        )
    ]
