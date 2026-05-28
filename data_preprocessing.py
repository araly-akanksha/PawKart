# ============================================================
# AI-Driven Omnichannel Inventory & Quick-Commerce System
# DATA PREPROCESSING & DATASET INTEGRATION
# ============================================================

# -----------------------------
# IMPORT LIBRARIES
# -----------------------------

import pandas as pd
import numpy as np

# -----------------------------
# LOAD DATASETS
# -----------------------------

customers = pd.read_csv("olist_customers_dataset.csv")
geolocation = pd.read_csv("olist_geolocation_dataset.csv")
order_items = pd.read_csv("olist_order_items_dataset.csv")
payments = pd.read_csv("olist_order_payments_dataset.csv")
reviews = pd.read_csv("olist_order_reviews_dataset.csv")
orders = pd.read_csv("olist_orders_dataset.csv")
products = pd.read_csv("olist_products_dataset.csv")
sellers = pd.read_csv("olist_sellers_dataset.csv")
category_translation = pd.read_csv("product_category_name_translation.csv")

# -----------------------------
# DISPLAY BASIC INFORMATION
# -----------------------------

print("Customers Shape:", customers.shape)
print("Orders Shape:", orders.shape)
print("Products Shape:", products.shape)

# -----------------------------
# REMOVE DUPLICATES
# -----------------------------

customers.drop_duplicates(inplace=True)
orders.drop_duplicates(inplace=True)
order_items.drop_duplicates(inplace=True)
products.drop_duplicates(inplace=True)
sellers.drop_duplicates(inplace=True)

# -----------------------------
# HANDLE MISSING VALUES
# -----------------------------

products.fillna({
    'product_category_name': 'unknown',
    'product_name_lenght': 0,
    'product_description_lenght': 0,
    'product_photos_qty': 0
}, inplace=True)

reviews.fillna({
    'review_comment_message': 'No Review'
}, inplace=True)

# -----------------------------
# CONVERT DATE COLUMNS
# -----------------------------

orders['order_purchase_timestamp'] = pd.to_datetime(
    orders['order_purchase_timestamp']
)

orders['order_delivered_customer_date'] = pd.to_datetime(
    orders['order_delivered_customer_date']
)

# -----------------------------
# MERGE PRODUCT CATEGORY TRANSLATION
# -----------------------------

products = products.merge(
    category_translation,
    how='left',
    on='product_category_name'
)

# -----------------------------
# MERGE ORDERS + CUSTOMERS
# -----------------------------

orders_customers = orders.merge(
    customers,
    how='left',
    on='customer_id'
)

# -----------------------------
# MERGE ORDER ITEMS
# -----------------------------

orders_items = orders_customers.merge(
    order_items,
    how='left',
    on='order_id'
)

# -----------------------------
# MERGE PRODUCTS
# -----------------------------

orders_products = orders_items.merge(
    products,
    how='left',
    on='product_id'
)

# -----------------------------
# MERGE SELLERS
# -----------------------------

full_data = orders_products.merge(
    sellers,
    how='left',
    on='seller_id'
)

# -----------------------------
# MERGE PAYMENTS
# -----------------------------

full_data = full_data.merge(
    payments,
    how='left',
    on='order_id'
)

# -----------------------------
# MERGE REVIEWS
# -----------------------------

full_data = full_data.merge(
    reviews,
    how='left',
    on='order_id'
)

# -----------------------------
# CHECK FINAL DATASET
# -----------------------------

print("\nFinal Dataset Shape:")
print(full_data.shape)

print("\nFinal Dataset Columns:")
print(full_data.columns)

# ============================================================
# FEATURE ENGINEERING
# ============================================================

# -----------------------------
# TOTAL ORDER VALUE
# -----------------------------

full_data['total_order_value'] = (
    full_data['price'] + full_data['freight_value']
)

# -----------------------------
# EXTRACT DATE FEATURES
# -----------------------------

full_data['purchase_year'] = (
    full_data['order_purchase_timestamp'].dt.year
)

full_data['purchase_month'] = (
    full_data['order_purchase_timestamp'].dt.month
)

full_data['purchase_day'] = (
    full_data['order_purchase_timestamp'].dt.day
)

# -----------------------------
# DELIVERY TIME
# -----------------------------

full_data['delivery_days'] = (
    full_data['order_delivered_customer_date']
    - full_data['order_purchase_timestamp']
).dt.days

# -----------------------------
# CUSTOMER PURCHASE COUNT
# -----------------------------

customer_orders = (
    full_data.groupby('customer_unique_id')['order_id']
    .nunique()
    .reset_index()
)

customer_orders.columns = [
    'customer_unique_id',
    'total_customer_orders'
]

full_data = full_data.merge(
    customer_orders,
    on='customer_unique_id',
    how='left'
)

# -----------------------------
# PRODUCT SALES COUNT
# -----------------------------

product_sales = (
    full_data.groupby('product_id')['order_item_id']
    .count()
    .reset_index()
)

product_sales.columns = [
    'product_id',
    'product_sales_count'
]

full_data = full_data.merge(
    product_sales,
    on='product_id',
    how='left'
)

# ============================================================
# DEMAND FORECASTING DATASET
# ============================================================

demand_forecasting = (
    full_data.groupby('order_purchase_timestamp')
    .agg({
        'order_id': 'count',
        'price': 'sum'
    })
    .reset_index()
)

demand_forecasting.columns = [
    'date',
    'total_orders',
    'total_sales'
]

print("\nDemand Forecasting Dataset:")
print(demand_forecasting.head())

# ============================================================
# INVENTORY SIMULATION
# ============================================================

# Simulated Inventory

inventory_data = (
    full_data.groupby('product_id')
    .agg({
        'product_sales_count': 'max'
    })
    .reset_index()
)

# Simulated Stock Level

inventory_data['current_stock'] = np.random.randint(
    20,
    200,
    size=len(inventory_data)
)

# Reorder Threshold

inventory_data['reorder_level'] = 50

# Low Stock Alert

inventory_data['low_stock_alert'] = (
    inventory_data['current_stock']
    < inventory_data['reorder_level']
)

print("\nInventory Dataset:")
print(inventory_data.head())

# ============================================================
# QUICK COMMERCE ANALYTICS
# ============================================================

# Seller Order Count

seller_performance = (
    full_data.groupby('seller_id')
    .agg({
        'order_id': 'count',
        'review_score': 'mean',
        'total_order_value': 'sum'
    })
    .reset_index()
)

seller_performance.columns = [
    'seller_id',
    'total_orders',
    'average_review_score',
    'total_sales'
]

print("\nSeller Performance:")
print(seller_performance.head())

# ============================================================
# SAVE CLEANED DATASETS
# ============================================================

full_data.to_csv(
    "cleaned_full_dataset.csv",
    index=False
)

demand_forecasting.to_csv(
    "demand_forecasting_dataset.csv",
    index=False
)

inventory_data.to_csv(
    "inventory_dataset.csv",
    index=False
)

seller_performance.to_csv(
    "seller_performance_dataset.csv",
    index=False
)

print("\n==============================")
print("DATA PREPROCESSING COMPLETED")
print("==============================")