import os
import logging
import pandas as pd
import numpy as np
import xgboost as xgb
from sqlalchemy.orm import Session
from sklearn.model_selection import train_test_split

from app.database import SessionLocal
from app.ai.features.recommendation_features import extract_recommendation_features

logger = logging.getLogger(__name__)

MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, "xgboost_recommendation_model.json")

def generate_negative_samples(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate negative samples for customer-product interactions.
    If a customer didn't buy a product, we sample some to represent '0' interactions.
    """
    logger.info("Generating negative samples for training...")
    
    unique_customers = df['customer_id'].unique()
    unique_products = df[['product_id', 'category_encoded', 'price']].drop_duplicates()
    
    # We will sample randomly
    negatives = []
    
    for c_id in unique_customers:
        purchased_pids = set(df[df['customer_id'] == c_id]['product_id'])
        # Pick 3 random products they haven't bought
        non_purchased = unique_products[~unique_products['product_id'].isin(purchased_pids)].sample(n=min(3, len(unique_products)))
        
        for _, row in non_purchased.iterrows():
            negatives.append({
                'customer_id': c_id,
                'product_id': row['product_id'],
                'category_encoded': row['category_encoded'],
                'price': row['price'],
                'interaction_count': 0,
                'purchased': 0
            })
            
    neg_df = pd.DataFrame(negatives)
    return pd.concat([df, neg_df], ignore_index=True)

def train_xgboost_model(db: Session = None):
    """
    Trains an XGBoost model to predict product purchase probability for a user.
    """
    logger.info("Starting XGBoost Recommendation training pipeline...")
    
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
        
    try:
        # 1. Extract positive interactions
        df = extract_recommendation_features(db)
        if df.empty:
            logger.warning("No interactions found for XGBoost.")
            return False
            
        # 2. Add negative sampling (otherwise model only sees '1')
        train_df = generate_negative_samples(df)
        
        # 3. Features and Target
        features = ['customer_id', 'product_id', 'category_encoded', 'price', 'interaction_count']
        X = train_df[features]
        y = train_df['purchased']
        
        # 4. Train Model
        model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        
        logger.info("Fitting XGBoost model...")
        model.fit(X, y)
        
        # 5. Save Model
        model.save_model(MODEL_PATH)
        logger.info(f"XGBoost model trained and saved to {MODEL_PATH}")
        return True
        
    except Exception as e:
        logger.error(f"XGBoost training failed: {e}")
        return False
    finally:
        if close_db:
            db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    train_xgboost_model()
