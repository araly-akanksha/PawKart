import os
import logging
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from catboost import CatBoostClassifier, Pool
from sklearn.model_selection import train_test_split

from app.database import SessionLocal
from app.ai.features.customer_features import extract_customer_rfm_features

logger = logging.getLogger(__name__)

# Model path
MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, "catboost_customer_model.cbm")

def train_catboost_model(db: Session = None):
    """
    Trains a CatBoost Classifier to predict if a customer will purchase in the next 7 days.
    """
    logger.info("Starting CatBoost training pipeline...")
    
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
        
    try:
        # 1. Extract Features
        df = extract_customer_rfm_features(db)
        
        if df.empty or len(df) < 5:
            logger.warning("Not enough data to train CatBoost model.")
            return False
            
        # 2. Generate Synthetic Targets for Phase 3 Proof of Concept
        # Since we don't have longitudinal target labels, we simulate a realistic target:
        # Customers who buy frequently and recently are more likely to buy again.
        # Adding some random noise for realistic model fitting.
        
        np.random.seed(42)
        base_prob = 0.1
        # Probability increases if recency is low
        prob = base_prob + np.where(df['recency_days'] < 30, 0.4, 0.0)
        # Probability increases if frequency is high
        prob += np.where(df['frequency_orders'] >= 3, 0.3, 0.0)
        
        # Add some noise
        prob += np.random.uniform(-0.1, 0.1, size=len(df))
        prob = np.clip(prob, 0.0, 1.0)
        
        # Generate binary target
        df['target_buy_next_7_days'] = (np.random.rand(len(df)) < prob).astype(int)
        
        # Guarantee at least one 0 and one 1 for CatBoost training
        if df['target_buy_next_7_days'].nunique() < 2:
            df.loc[0, 'target_buy_next_7_days'] = 0
            df.loc[1, 'target_buy_next_7_days'] = 1
        
        # 3. Prepare Data for CatBoost
        features = ['recency_days', 'frequency_orders', 'monetary_total', 'avg_order_value', 'favorite_category']
        X = df[features]
        y = df['target_buy_next_7_days']
        
        categorical_features_indices = [4] # 'favorite_category' is at index 4
        
        if len(X) < 20:
            X_train, X_test = X, X
            y_train, y_test = y, y
        else:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        train_pool = Pool(X_train, y_train, cat_features=categorical_features_indices)
        test_pool = Pool(X_test, y_test, cat_features=categorical_features_indices)
        
        # 4. Initialize and Train CatBoost
        model = CatBoostClassifier(
            iterations=100,
            learning_rate=0.1,
            depth=6,
            eval_metric='AUC',
            random_seed=42,
            logging_level='Silent',
            allow_writing_files=False
        )
        
        logger.info("Fitting CatBoost model...")
        model.fit(train_pool, eval_set=test_pool)
        
        # 5. Save Model
        model.save_model(MODEL_PATH)
        logger.info(f"CatBoost model trained and saved successfully to {MODEL_PATH}")
        return True
        
    except Exception as e:
        logger.error(f"CatBoost training failed: {e}")
        return False
    finally:
        if close_db:
            db.close()

if __name__ == "__main__":
    # Configure logging for standalone script execution
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    train_catboost_model()
