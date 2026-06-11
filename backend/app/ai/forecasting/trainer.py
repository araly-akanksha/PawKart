import os
import logging
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from catboost import CatBoostRegressor

from app.database import SessionLocal
from app.ai.features.sales_features import extract_sales_time_series

logger = logging.getLogger(__name__)

MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, "tft_proxy_forecast_model.cbm")

def train_forecast_model(db: Session = None):
    """
    Trains a CatBoost Regressor to proxy the TFT Demand Forecasting.
    Uses time-series features (day of week, month, price, category) to predict sales volume.
    """
    logger.info("Starting Demand Forecast training pipeline...")
    
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
        
    try:
        df = extract_sales_time_series(db)
        if df.empty:
            logger.warning("No sales data available for forecasting.")
            return False
            
        # Target: quantity_sold
        # Features: product_id, category, price, day_of_week, month
        # Since we only have a limited mock timeline, we train on all available data
        
        # Simple feature engineering for regression
        X = df[['product_id', 'category', 'price', 'day_of_week', 'month']]
        y = df['quantity_sold']
        
        # Label encode category
        X_encoded = X.copy()
        X_encoded['category'] = X_encoded['category'].astype('category').cat.codes
        
        model = CatBoostRegressor(
            iterations=150,
            learning_rate=0.05,
            depth=5,
            eval_metric='RMSE',
            random_seed=42,
            logging_level='Silent',
            allow_writing_files=False
        )
        
        logger.info("Fitting Forecasting Model (CatBoost Regressor Proxy)...")
        # We pass category indices if needed, but since we label encoded we can just train directly
        model.fit(X_encoded, y)
        
        model.save_model(MODEL_PATH)
        logger.info(f"Forecast model trained and saved to {MODEL_PATH}")
        return True
        
    except Exception as e:
        logger.error(f"Forecast training failed: {e}")
        return False
    finally:
        if close_db:
            db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    train_forecast_model()
