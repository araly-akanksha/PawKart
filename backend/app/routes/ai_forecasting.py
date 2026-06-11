import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas import TFTForecastResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/forecast/product/{product_id}", response_model=TFTForecastResponse)
def get_tft_product_forecast(
    product_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    [STUB] Temporal Fusion Transformer (TFT) Demand Forecasting.
    Returns mocked predictions for Phase 2 integration.
    """
    logger.info(f"TFT Prediction requested for product {product_id}")
    
    # Mocking TFT output
    return TFTForecastResponse(
        product_id=product_id,
        forecast_1_day=145,
        forecast_7_days=960,
        forecast_30_days=4120,
        confidence=0.91
    )

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
