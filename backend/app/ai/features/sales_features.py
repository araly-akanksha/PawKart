import logging
import pandas as pd
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import Order, OrderItem, Product, Inventory

logger = logging.getLogger(__name__)

def extract_sales_time_series(db: Session) -> pd.DataFrame:
    """
    Extracts daily sales volume for each product to be used in demand forecasting.
    This prepares the static and dynamic features for the forecasting model.
    """
    logger.info("Extracting daily sales time-series for forecasting...")
    
    orders = db.query(Order).all()
    if not orders:
        return pd.DataFrame()
        
    records = []
    products_info = {p.id: p for p in db.query(Product).all()}
    
    for order in orders:
        order_date = order.created_at.date() if order.created_at else datetime.utcnow().date()
        for item in order.items:
            records.append({
                'date': order_date,
                'product_id': item.product_id,
                'quantity_sold': item.quantity
            })
            
    df = pd.DataFrame(records)
    if df.empty:
        return df
        
    # Aggregate daily sales per product
    daily_sales = df.groupby(['date', 'product_id'])['quantity_sold'].sum().reset_index()
    
    # Enrich with static metadata (required for TFT architecture)
    def get_category(pid):
        p = products_info.get(pid)
        return p.category if p else "Unknown"
        
    def get_price(pid):
        p = products_info.get(pid)
        return p.price if p else 0.0
        
    daily_sales['category'] = daily_sales['product_id'].apply(get_category)
    daily_sales['price'] = daily_sales['product_id'].apply(get_price)
    
    # Convert dates to temporal features
    daily_sales['date'] = pd.to_datetime(daily_sales['date'])
    daily_sales['day_of_week'] = daily_sales['date'].dt.dayofweek
    daily_sales['month'] = daily_sales['date'].dt.month
    
    logger.info(f"Extracted {len(daily_sales)} daily sales records.")
    return daily_sales
