import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import pandas as pd

from app.models import Order, OrderItem, Product

logger = logging.getLogger(__name__)

def extract_customer_rfm_features(db: Session) -> pd.DataFrame:
    """
    Extracts Recency, Frequency, Monetary (RFM) features for all customers 
    based on historical orders.
    """
    logger.info("Extracting customer RFM features from the database...")
    
    # We will group by customer_name (or phone/email if available) 
    # since mock data uses customer_name heavily.
    orders = db.query(Order).all()
    
    if not orders:
        logger.warning("No orders found for feature extraction.")
        return pd.DataFrame()
        
    data = []
    current_time = datetime.utcnow()
    
    # We need to compute stats per customer
    customer_stats: Dict[str, Dict[str, Any]] = {}
    
    for order in orders:
        c_name = order.customer_name
        if not c_name:
            continue
            
        if c_name not in customer_stats:
            customer_stats[c_name] = {
                'customer_id': hash(c_name) % 1000000, # Mock ID
                'customer_name': c_name,
                'total_orders': 0,
                'total_spent': 0.0,
                'last_order_date': datetime.min,
                'categories': {}
            }
            
        stats = customer_stats[c_name]
        stats['total_orders'] += 1
        stats['total_spent'] += order.total_amount
        
        if order.created_at and order.created_at > stats['last_order_date']:
            stats['last_order_date'] = order.created_at
            
        # Tally categories
        for item in order.items:
            # We can lookup category from product or use item name
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                cat = product.category
                stats['categories'][cat] = stats['categories'].get(cat, 0) + item.quantity

    # Convert to DataFrame
    rows = []
    for c_name, stats in customer_stats.items():
        if stats['total_orders'] == 0:
            continue
            
        days_since_last_order = (current_time - stats['last_order_date']).days if stats['last_order_date'] != datetime.min else 999
        avg_order_value = stats['total_spent'] / stats['total_orders']
        
        # Determine favorite category
        fav_category = "Unknown"
        if stats['categories']:
            fav_category = max(stats['categories'], key=stats['categories'].get)
            
        rows.append({
            'customer_id': stats['customer_id'],
            'customer_name': stats['customer_name'],
            'recency_days': days_since_last_order,
            'frequency_orders': stats['total_orders'],
            'monetary_total': stats['total_spent'],
            'avg_order_value': avg_order_value,
            'favorite_category': fav_category
        })
        
    df = pd.DataFrame(rows)
    logger.info(f"Extracted features for {len(df)} customers.")
    return df
