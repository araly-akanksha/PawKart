import os
import logging
import pandas as pd
from catboost import CatBoostClassifier

from app.schemas import CustomerPurchaseResponse
from app.ai.features.customer_features import extract_customer_rfm_features

logger = logging.getLogger(__name__)

MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, "catboost_customer_model.cbm")

_model = None

def load_model():
    global _model
    if _model is None:
        if os.path.exists(MODEL_PATH):
            _model = CatBoostClassifier()
            _model.load_model(MODEL_PATH)
            logger.info("CatBoost model loaded successfully.")
        else:
            logger.warning(f"CatBoost model file not found at {MODEL_PATH}")
    return _model

def predict_high_probability_customers(db, threshold=0.4, limit=10):
    """
    Returns the top customers most likely to purchase in the next 7 days.
    """
    model = load_model()
    if not model:
        logger.error("Cannot predict without a trained model.")
        return []
        
    df = extract_customer_rfm_features(db)
    if df.empty:
        return []
        
    features = ['recency_days', 'frequency_orders', 'monetary_total', 'avg_order_value', 'favorite_category']
    X = df[features]
    
    # Predict probabilities (assuming class 1 is the 'buy' class)
    probs = model.predict_proba(X)
    
    if probs.shape[1] > 1:
        buy_probs = probs[:, 1]
    else:
        buy_probs = probs[:, 0]
        
    df['purchase_probability'] = buy_probs
    
    # Filter by threshold and sort
    high_prob_df = df[df['purchase_probability'] >= threshold].sort_values(by='purchase_probability', ascending=False).head(limit)
    
    results = []
    for _, row in high_prob_df.iterrows():
        segment = "HIGH"
        if row['purchase_probability'] < 0.6:
            segment = "MEDIUM"
        
        results.append(
            CustomerPurchaseResponse(
                customer_id=row['customer_id'],
                purchase_probability=round(row['purchase_probability'], 2),
                segment=segment
            )
        )
        
    return results
