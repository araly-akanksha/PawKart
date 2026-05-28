# =========================================================
# INVENTORY OPTIMIZATION SYSTEM
# =========================================================

# -----------------------------
# IMPORT LIBRARIES
# -----------------------------

import pandas as pd
import numpy as np

# -----------------------------
# LOAD INVENTORY DATASET
# -----------------------------

inventory_df = pd.read_csv("inventory_dataset.csv")

print(inventory_df.head())

# -----------------------------
# STOCK STATUS CLASSIFICATION
# -----------------------------

def classify_stock(stock):

    if stock < 50:
        return "Low Stock"

    elif stock < 150:
        return "Medium Stock"

    else:
        return "Healthy Stock"


inventory_df['Stock_Status'] = inventory_df[
    'current_stock'
].apply(classify_stock)

print("\nStock Status Added\n")

# -----------------------------
# REORDER RECOMMENDATION
# -----------------------------

def reorder_recommendation(stock):

    if stock < 50:
        return 200

    elif stock < 150:
        return 100

    else:
        return 0


inventory_df['Reorder_Quantity'] = inventory_df[
    'current_stock'
].apply(reorder_recommendation)

print("\nReorder Recommendation Added\n")

# -----------------------------
# INVENTORY RISK LEVEL
# -----------------------------

def inventory_risk(stock):

    if stock < 30:
        return "High Risk"

    elif stock < 100:
        return "Moderate Risk"

    else:
        return "Low Risk"


inventory_df['Inventory_Risk'] = inventory_df[
    'current_stock'
].apply(inventory_risk)

print("\nInventory Risk Analysis Added\n")

# -----------------------------
# PRODUCT MOVEMENT ANALYSIS
# -----------------------------

def movement_category(product_sales_count):

    if product_sales_count > 500:
        return "Fast Moving"

    elif product_sales_count > 200:
        return "Medium Moving"

    else:
        return "Slow Moving"


inventory_df['Movement_Category'] = inventory_df[
    'product_sales_count'
].apply(movement_category)

print("\nMovement Analysis Added\n")

# -----------------------------
# INVENTORY HEALTH SCORE
# -----------------------------

inventory_df['Inventory_Health_Score'] = (
    inventory_df['current_stock'] * 0.6
    +
    inventory_df['product_sales_count'] * 0.4
)

print("\nInventory Health Score Added\n")

# -----------------------------
# SAVE FINAL DATASET
# -----------------------------

inventory_df.to_csv(
    "optimized_inventory_dataset.csv",
    index=False
)

print("\nOptimized Inventory Dataset Saved")

# -----------------------------
# DISPLAY RESULTS
# -----------------------------

print("\nFINAL INVENTORY ANALYSIS\n")

print(
    inventory_df[
        [
            'current_stock',
            'product_sales_count',
            'Stock_Status',
            'Reorder_Quantity',
            'Inventory_Risk',
            'Movement_Category',
            'Inventory_Health_Score'
        ]
    ].head(10)
)