import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import pandas as pd

from app.models import Order, OrderItem, Product

logger = logging.getLogger(__name__)

def extract_recommendation_features(db: Session) -> pd.DataFrame:
    """
    Extracts features for XGBoost Recommendation engine.
    For point-wise ranking, we extract customer-product interaction history.
    """
    logger.info("Extracting customer-product interactions for XGBoost...")
    
    orders = db.query(Order).all()
    if not orders:
        return pd.DataFrame()
        
    # Map customer interactions
    interactions = []
    
    # We also need product metadata to use as features
    products = {p.id: p for p in db.query(Product).all()}
    
    for order in orders:
        c_name = order.customer_name
        if not c_name:
            continue
            
        c_id = hash(c_name) % 1000000
        
        for item in order.items:
            product = products.get(item.product_id)
            if not product:
                continue
                
            interactions.append({
                'customer_id': c_id,
                'product_id': item.product_id,
                'category_encoded': hash(product.category) % 100, # simple target encoding
                'price': product.price,
                'interaction_count': item.quantity,
                'purchased': 1 # Positive sample
            })
            
    df = pd.DataFrame(interactions)
    
    # Aggregate interactions (if a customer bought the same product multiple times)
    if not df.empty:
        df = df.groupby(['customer_id', 'product_id', 'category_encoded', 'price']).agg({
            'interaction_count': 'sum',
            'purchased': 'max'
        }).reset_index()
        
    logger.info(f"Extracted {len(df)} positive customer-product interactions.")
    return df
