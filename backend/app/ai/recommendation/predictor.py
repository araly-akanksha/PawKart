import os
import logging
import pandas as pd
import xgboost as xgb
from sqlalchemy.orm import Session

from app.schemas import RecommendationItem, CustomerRecommendationResponse
from app.models import Product

logger = logging.getLogger(__name__)

MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, "xgboost_recommendation_model.json")

_model = None

def load_model():
    global _model
    if _model is None:
        if os.path.exists(MODEL_PATH):
            _model = xgb.XGBClassifier()
            _model.load_model(MODEL_PATH)
            logger.info("XGBoost model loaded successfully.")
        else:
            logger.warning(f"XGBoost model file not found at {MODEL_PATH}")
    return _model

def get_recommendations(customer_id: int, db: Session, limit: int = 4):
    """
    Predicts top recommended products for a given customer using XGBoost.
    """
    model = load_model()
    if not model:
        return []
        
    # Get all available products
    products = db.query(Product).filter(Product.available == True).all()
    if not products:
        return []
        
    # Construct feature matrix for this customer against all products
    features = []
    pid_map = {}
    
    for p in products:
        features.append({
            'customer_id': customer_id,
            'product_id': p.id,
            'category_encoded': hash(p.category) % 100,
            'price': p.price,
            'interaction_count': 0 # Assuming predicting for unseen items
        })
        pid_map[p.id] = p
        
    df = pd.DataFrame(features)
    X = df[['customer_id', 'product_id', 'category_encoded', 'price', 'interaction_count']]
    
    probs = model.predict_proba(X)
    
    # Probabilities for class 1 (purchase)
    if probs.shape[1] > 1:
        purchase_probs = probs[:, 1]
    else:
        purchase_probs = probs[:, 0]
        
    df['score'] = purchase_probs
    
    # Sort by highest score
    top_items = df.sort_values(by='score', ascending=False).head(limit)
    
    results = []
    for _, row in top_items.iterrows():
        p_id = int(row['product_id'])
        score = float(row['score'])
        p = pid_map[p_id]
        
        # Simple rationale generation
        reason = f"Based on your interest in {p.category}"
        if score > 0.8:
            reason = f"Highly Recommended {p.category}"
            
        results.append(
            RecommendationItem(
                product_id=p_id,
                score=round(score, 2),
                reason=reason
            )
        )
        
    return CustomerRecommendationResponse(
        customer_id=customer_id,
        recommendations=results
    )
